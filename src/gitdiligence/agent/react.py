"""Boucle ReAct — le coeur de l'agent.

Implémente le cycle : thought → tool call → observation → repeat
jusqu'à ce que l'agent appelle generate_report ou atteigne le max d'itérations.
"""

from pydantic import ValidationError

from gitdiligence.agent.prompts import build_system_prompt
from gitdiligence.agent.state import AgentState, Step
from gitdiligence.llm.client import call_claude
from gitdiligence.report.schema import DiligenceReport
from gitdiligence.tools.base import Tool
from gitdiligence.tools import registry

MAX_ITERATIONS = 25


def _build_generate_report_tool() -> dict:
    """Construit la définition de l'outil generate_report pour Claude.

    Utilise le JSON Schema généré par Pydantic — comme ça Claude sait
    exactement quel format produire.
    """
    return {
        "name": "generate_report",
        "description": "Produit le rapport final de due diligence. Appelle cet outil quand tu as assez d'information.",
        "input_schema": DiligenceReport.model_json_schema(),
    }


def _extract_thought(response) -> str:
    """Extrait le texte de raisonnement de la réponse Claude."""
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)


def _extract_tool_call(response) -> tuple[str, dict, str] | None:
    """Extrait le premier appel d'outil de la réponse Claude.

    Retourne (tool_name, tool_input, tool_use_id) ou None.
    """
    for block in response.content:
        if block.type == "tool_use":
            return block.name, block.input, block.id
    return None


def run_agent(
    owner: str,
    repo: str,
    model: str = "claude-sonnet-4-6",
    max_steps: int = MAX_ITERATIONS,
    verbose: bool = False,
) -> AgentState:
    """Lance l'agent ReAct sur un repo GitHub.

    Retourne l'AgentState avec le rapport et les étapes.
    """
    state = AgentState(owner=owner, repo=repo)
    system = build_system_prompt(owner, repo)

    # Premier message : demande d'analyse
    state.messages.append({
        "role": "user",
        "content": f"Analyse le repo {owner}/{repo}",
    })

    # Les outils disponibles
    tools = registry.all_tools()
    generate_report_tool = _build_generate_report_tool()

    for iteration in range(max_steps):
        if verbose:
            print(f"\n--- Itération {iteration + 1}/{max_steps} ---")

        # Appel à Claude
        response = call_claude(
            messages=state.messages,
            tools=tools,
            system=system,
            model=model,
            extra_tools=[generate_report_tool],
        )

        # Comptabilise les tokens
        state.add_tokens(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

        # Extrait le raisonnement
        thought = _extract_thought(response)
        if verbose and thought:
            print(f"Thought: {thought[:200]}...")

        # Ajoute la réponse de Claude aux messages
        state.messages.append({
            "role": "assistant",
            "content": response.content,
        })

        # Extrait l'appel d'outil
        tool_call = _extract_tool_call(response)

        # Pas d'appel d'outil → Claude a fini sans rapport (ne devrait pas arriver)
        if tool_call is None:
            if verbose:
                print("Claude a terminé sans appeler generate_report.")
            break

        tool_name, tool_input, tool_use_id = tool_call
        if verbose:
            print(f"Tool: {tool_name}({tool_input})")

        # Cas spécial : generate_report → valide et termine
        if tool_name == "generate_report":
            try:
                state.report = DiligenceReport(**tool_input)
                # Confirme à Claude que le rapport est valide
                state.messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": "Rapport validé avec succès.",
                    }],
                })
                state.add_step(Step(
                    tool_name=tool_name,
                    tool_input=tool_input,
                    result="Rapport validé.",
                    thought=thought,
                ))
                if verbose:
                    print(f"Rapport généré ! Verdict: {state.report.verdict}")
                break

            except ValidationError as e:
                # Rapport invalide → renvoie l'erreur à Claude pour qu'il corrige
                error_msg = f"Rapport invalide : {e}"
                state.messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": error_msg,
                        "is_error": True,
                    }],
                })
                if verbose:
                    print(f"Erreur de validation : {e}")
                continue

        # Outil normal → exécute et renvoie le résultat
        try:
            tool = registry.get_tool(tool_name)
            result = tool.execute(**tool_input)
        except Exception as e:
            result = f"Erreur lors de l'exécution de {tool_name}: {e}"

        state.add_step(Step(
            tool_name=tool_name,
            tool_input=tool_input,
            result=result,
            thought=thought,
        ))

        # Renvoie le résultat à Claude
        state.messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result,
            }],
        })

        if verbose:
            print(f"Result: {result[:200]}...")

    return state
