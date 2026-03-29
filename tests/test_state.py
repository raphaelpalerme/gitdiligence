"""Tests for the state management (agent/state.py)."""

from gitdiligence.agent.state import AgentState, Step


def test_initial_state():
    """The initial state is empty and not finished."""
    state = AgentState(owner="pallets", repo="flask")

    assert state.owner == "pallets"
    assert state.steps == []
    assert state.total_tokens == 0
    assert state.is_done is False


def test_add_step():
    """We can add a step."""
    state = AgentState(owner="pallets", repo="flask")
    step = Step(
        tool_name="get_repo_info",
        tool_input={"owner": "pallets", "repo": "flask"},
        result='{"name": "flask"}',
        thought="Je vais récupérer les infos du repo.",
    )
    state.add_step(step)

    assert len(state.steps) == 1
    assert state.steps[0].tool_name == "get_repo_info"
    assert state.steps[0].thought == "Je vais récupérer les infos du repo."


def test_add_tokens():
    """The token counter accumulates."""
    state = AgentState(owner="pallets", repo="flask")
    state.add_tokens(input_tokens=100, output_tokens=50)
    state.add_tokens(input_tokens=200, output_tokens=80)

    assert state.input_tokens == 300
    assert state.output_tokens == 130
    assert state.total_tokens == 430


def test_is_done_when_report_set():
    """The agent is finished when the report is set."""
    state = AgentState(owner="pallets", repo="flask")
    assert state.is_done is False

    # Simulate a report (None means not finished, object means finished)
    state.report = "fake_report"  # type: ignore
    assert state.is_done is True
