"""Multi-provider LLM client (Claude + Gemini).

Dispatcher that detects the provider from the model name and
returns a normalized LLMResponse. react.py never knows which
provider is being used.
"""

import os
import time
import uuid

from gitdiligence.llm.models import LLMResponse, ToolCall, Usage
from gitdiligence.tools.base import Tool


# --- Provider detection ---


def detect_provider(model: str) -> str:
    """Detect the provider from the model name."""
    if model.startswith("gemini-"):
        return "gemini"
    return "claude"


# --- Tool format conversion ---


def tools_to_claude_format(tools: list[Tool]) -> list[dict]:
    """Convert our tools to Claude format (input_schema)."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }
        for tool in tools
    ]


def tools_to_gemini_format(tools: list[Tool]) -> list[dict]:
    """Convert our tools to Gemini format (parameters)."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
        }
        for tool in tools
    ]


def _resolve_refs(schema: dict) -> dict:
    """Resolve $ref in a JSON Schema by inlining definitions.

    Gemini does not support $ref/$defs. We replace each $ref
    with the corresponding definition.
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
    """Convert extra_tools (Claude format) to Gemini format."""
    result = []
    for tool in extra_tools:
        schema = tool.get("input_schema", tool.get("parameters", {}))
        result.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": _resolve_refs(dict(schema)),
        })
    return result


# --- Message formatting ---


def format_assistant_message(response: LLMResponse) -> dict:
    """Build the assistant message to append to the history."""
    if response.provider == "gemini":
        return {"role": "model", "parts": response.raw_content}
    # Claude
    return {"role": "assistant", "content": response.raw_content}


def format_tool_results(results: list[dict], provider: str) -> dict:
    """Build the user message containing tool results.

    results: list of {"name": ..., "id": ..., "content": ..., "is_error": ...}
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


# --- LLM calls ---


def _call_claude(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str,
    max_tokens: int,
    extra_tools: list[dict],
) -> LLMResponse:
    """Call the Claude API and return an LLMResponse."""
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
            print(f"Rate limit reached. Waiting {wait}s...")
            time.sleep(wait)

    # Normalize the response
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
    """Call the Gemini API and return an LLMResponse."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise ImportError(
            "google-genai is required for Gemini models. "
            "Install it with: pip install gitdiligence[gemini]"
        )

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Convert tools to Gemini format
    all_declarations = tools_to_gemini_format(tools) + _extra_tools_to_gemini(extra_tools)
    gemini_tools = [types.Tool(function_declarations=all_declarations)]

    # Convert messages to Gemini format
    # Messages are either in native Gemini format (via format_assistant_message
    # / format_tool_results), or the first user message as a string.
    gemini_contents = []
    for msg in messages:
        if "parts" in msg:
            # Already in Gemini format (previous messages)
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
                print(f"Rate limit reached. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

    # Normalize the response
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


# --- Public dispatcher ---


def call_llm(
    messages: list[dict],
    tools: list[Tool],
    system: str,
    model: str = "gemini-2.5-flash",
    max_tokens: int = 16000,
    extra_tools: list[dict] | None = None,
) -> LLMResponse:
    """Call the appropriate LLM based on the requested model.

    Returns a normalized LLMResponse, regardless of the provider.
    """
    provider = detect_provider(model)
    extra = extra_tools or []

    if provider == "gemini":
        return _call_gemini(messages, tools, system, model, max_tokens, extra)
    return _call_claude(messages, tools, system, model, max_tokens, extra)
