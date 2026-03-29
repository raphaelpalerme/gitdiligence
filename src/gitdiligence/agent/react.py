"""Boucle ReAct — le coeur de l'agent.

Implémente le cycle : thought → tool call → observation → repeat
jusqu'à ce que l'agent appelle generate_report ou atteigne le max d'itérations.
Fonctionne avec Claude et Gemini grâce à la couche d'abstraction dans llm/client.py.
"""

from pydantic import ValidationError

from gitdiligence.agent.prompts import build_system_prompt
from gitdiligence.agent.state import AgentState, Step
from gitdiligence.llm.client import call_llm, format_assistant_message, format_tool_results
from gitdiligence.report.schema import DiligenceReport
from gitdiligence.tools import registry

MAX_ITERATIONS = 25


def _build_generate_report_tool() -> dict:
    """Construit la définition de l'outil generate_report.

    Utilise le JSON Schema généré par Pydantic — comme ça le LLM sait
    exactement quel format produire.
    """
    return {
        "name": "generate_report",
        "description": "Produit le rapport final de due diligence. Appelle cet outil quand tu as assez d'information.",
        "input_schema": DiligenceReport.model_json_schema(),
    }


def run_agent(
    owner: str,
    repo: str,
    model: str = "gemini-2.5-flash",
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

        # Appel au LLM (Claude ou Gemini selon le modèle)
        response = call_llm(
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

        # Raisonnement
        if verbose and response.text:
            print(f"Thought: {response.text[:200]}...")

        # Ajoute la réponse du LLM aux messages
        state.messages.append(format_assistant_message(response))

        # Pas d'appel d'outil → le LLM a fini sans rapport
        if not response.tool_calls:
            if verbose:
                print("Le LLM a terminé sans appeler generate_report.")
            break

        # Exécute chaque outil et collecte les résultats
        results = []
        done = False

        for tc in response.tool_calls:
            if verbose:
                print(f"Tool: {tc.name}({tc.input})")

            # Cas spécial : generate_report → valide et termine
            if tc.name == "generate_report":
                try:
                    state.report = DiligenceReport(**tc.input)
                    results.append({
                        "name": tc.name,
                        "id": tc.id,
                        "content": "Rapport validé avec succès.",
                    })
                    state.add_step(Step(
                        tool_name=tc.name,
                        tool_input=tc.input,
                        result="Rapport validé.",
                        thought=response.text,
                    ))
                    if verbose:
                        print(f"Rapport généré ! Verdict: {state.report.verdict}")
                    done = True

                except ValidationError as e:
                    error_msg = f"Rapport invalide : {e}"
                    results.append({
                        "name": tc.name,
                        "id": tc.id,
                        "content": error_msg,
                        "is_error": True,
                    })
                    if verbose:
                        print(f"Erreur de validation : {e}")
                continue

            # Outil normal → exécute
            try:
                tool = registry.get_tool(tc.name)
                result = tool.execute(**tc.input)
            except Exception as e:
                result = f"Erreur lors de l'exécution de {tc.name}: {e}"

            state.add_step(Step(
                tool_name=tc.name,
                tool_input=tc.input,
                result=result,
                thought=response.text,
            ))

            results.append({
                "name": tc.name,
                "id": tc.id,
                "content": result,
            })

            if verbose:
                print(f"Result: {result[:200]}...")

        # Renvoie tous les résultats au LLM en un seul message
        state.messages.append(format_tool_results(results, response.provider))

        if done:
            break

    return state
