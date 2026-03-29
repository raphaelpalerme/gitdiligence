"""Client LLM multi-provider (Claude + Gemini).

Dispatcher qui détecte le provider via le nom du modèle et
retourne une LLMResponse normalisée. react.py ne connaît jamais
le provider utilisé.
"""

import os
import time
import uuid

from gitdiligence.llm.models import LLMResponse, ToolCall, Usage
from gitdiligence.tools.base import Tool


# --- Détection du provider ---


def detect_provider(model: str) -> str:
    """Détecte le provider à partir du nom du modèle."""
    if model.startswith("gemini-"):
        return "gemini"
    return "claude"


# --- Conversion des outils ---


def tools_to_claude_format(tools: list[Tool]) -> list[dict]:
    """Convertit nos outils au format Claude (input_schema)."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }
        for tool in tools
    ]


def tools_to_gemini_format(tools: list[Tool]) -> list[dict]:
    """Convertit nos outils au format Gemini (parameters)."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in tools
    ]


def _resolve_refs(schema: dict) -> dict:
    """Résout les $ref dans un JSON Schema en inlinant les définitions.

    Gemini ne supporte pas $ref/$defs. On remplace chaque $ref
    par la définition correspondante.
    """
    defs = schema.pop("$defs", {})
    if not defs:
        return schema

    def resolve(obj):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_name = obj["$ref"].split("/")[-1]
                return resolve(defs[ref_name])
            return {k: resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [resolve(item) for item in obj]
        return obj

    return resolve(schema)


def _extra_tools_to_gemini(extra_tools: list[dict]) -> list[dict]:
    """Convertit les extra_tools (format Claude) au format Gemini."""
    result = []
    for tool in extra_tools:
        schema = tool.get("input_schema", tool.get("parameters", {}))
        result.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": _resolve_refs(dict(schema)),
        })
    return result


# --- Format des messages ---


def format_assistant_message(response: LLMResponse) -> dict:
    """Construit le message assistant à ajouter à l'historique."""
    if response.provider == "gemini":
        return {"role": "model", "parts": response.raw_content}
    # Claude
    return {"role": "assistant", "content": response.raw_content}


def format_tool_results(results: list[dict], provider: str) -> dict:
    """Construit le message user contenant les résultats des outils.

    results: liste de {"name": ..., "id": ..., "content": ..., "is_error": ...}
    """
    if provider == "gemini":
        from google.genai import types

        parts = []
        for r in results:
            parts.append(types.Part.from_function_response(
                name=r["name"],
                response={"result": r["content"]},
            ))
        return {"role": "user", "parts": parts}

    # Claude
    tool_results = []
    for r in results:
        tr = {
            "type": "tool_result",
            "tool_use_id": r["id"],
            "content": r["content"],
        }
        if r.get("is_error"):
            tr["is_error"] = True
        tool_results.append(tr)
    return {"role": "user", "content": tool_results}


# --- Appels LLM ---


def _call_claude(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str,
    max_tokens: int,
    extra_tools: list[dict],
) -> LLMResponse:
    """Appelle l'API Claude et retourne une LLMResponse."""
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    all_tools = tools_to_claude_format(tools) + extra_tools

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                tools=all_tools,
            )
            break
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait = 60 * (attempt + 1)
            print(f"Rate limit atteint. Attente de {wait}s...")
            time.sleep(wait)

    # Normalise la réponse
    text_parts = []
    tool_calls = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "tool_use":
            tool_calls.append(ToolCall(name=block.name, input=block.input, id=block.id))

    return LLMResponse(
        text="\n".join(text_parts),
        tool_calls=tool_calls,
        usage=Usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        ),
        raw_content=response.content,
        provider="claude",
    )


def _call_gemini(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str,
    max_tokens: int,
    extra_tools: list[dict],
) -> LLMResponse:
    """Appelle l'API Gemini et retourne une LLMResponse."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError(
            "google-genai est requis pour les modèles Gemini. "
            "Installe-le avec : pip install gitdiligence[gemini]"
        )

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Convertit les outils au format Gemini
    all_declarations = tools_to_gemini_format(tools) + _extra_tools_to_gemini(extra_tools)
    gemini_tools = [types.Tool(function_declarations=all_declarations)]

    # Convertit les messages au format Gemini
    # Les messages sont soit au format natif Gemini (via format_assistant_message
    # / format_tool_results), soit le premier message user en string.
    gemini_contents = []
    for msg in messages:
        if "parts" in msg:
            # Déjà au format Gemini (messages précédents)
            gemini_contents.append(msg)
        elif msg["role"] == "user" and isinstance(msg["content"], str):
            gemini_contents.append({
                "role": "user",
                "parts": [types.Part.from_text(text=msg["content"])],
            })

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=gemini_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    tools=gemini_tools,
                    max_output_tokens=max_tokens,
                ),
            )
            break
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt == max_retries - 1:
                    raise
                wait = 60 * (attempt + 1)
                print(f"Rate limit atteint. Attente de {wait}s...")
                time.sleep(wait)
            else:
                raise

    # Normalise la réponse
    text_parts = []
    tool_calls = []
    parts = response.candidates[0].content.parts

    for part in parts:
        if part.text:
            text_parts.append(part.text)
        elif part.function_call:
            tool_calls.append(ToolCall(
                name=part.function_call.name,
                input=dict(part.function_call.args) if part.function_call.args else {},
                id=f"gemini-{uuid.uuid4().hex[:8]}",
            ))

    # Token usage
    usage_meta = response.usage_metadata
    input_tokens = usage_meta.prompt_token_count if usage_meta else 0
    output_tokens = usage_meta.candidates_token_count if usage_meta else 0

    return LLMResponse(
        text="\n".join(text_parts),
        tool_calls=tool_calls,
        usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
        raw_content=parts,
        provider="gemini",
    )


# --- Dispatcher public ---


def call_llm(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str = "gemini-2.5-flash",
    max_tokens: int = 16000,
    extra_tools: list[dict] | None = None,
) -> LLMResponse:
    """Appelle le LLM approprié selon le modèle demandé.

    Retourne une LLMResponse normalisée, quel que soit le provider.
    """
    provider = detect_provider(model)
    extra = extra_tools or []

    if provider == "gemini":
        return _call_gemini(messages, tools, system, model, max_tokens, extra)
    return _call_claude(messages, tools, system, model, max_tokens, extra)
