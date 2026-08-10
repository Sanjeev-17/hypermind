"""Pipeline, context bounds, and trace tests."""

from hypermind.context import ContextBuilder
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest
from hypermind.trace import ExecutionTrace, TraceStore


def test_route_authentication_module():
    result = IntelligenceRouter().route("Review the authentication module")
    assert result.intent.intent == "coding"
    assert result.agent.id == "coder"
    assert result.model.provider
    assert result.trace is not None
    assert result.trace.status == "routed"
    assert "filesystem.read" in result.trace.tools_allowed


def test_context_respects_bounds():
    req = HyperMindRequest(
        raw_input="hello",
        project="hypermind",
        context_refs=[f"file_{i}" for i in range(50)],
    )
    from hypermind.agents import AgentRegistry

    agent = AgentRegistry().get("coder")
    bundle = ContextBuilder().build(req, agent, max_items=5, max_tokens=100)
    assert len(bundle.items) <= 5
    assert bundle.approx_tokens <= 100


def test_trace_json_has_operational_fields_only():
    result = IntelligenceRouter().route("Research competitors for portfolio")
    data = result.trace.to_dict()
    assert data["intent"] == "research"
    assert data["agent"] == "researcher"
    assert "chain_of_thought" not in data
    assert "hidden_reasoning" not in data
    assert data["status"] == "routed"


def test_trace_store_writes(tmp_path):
    store = TraceStore(root=tmp_path)
    trace = ExecutionTrace(
        request_id="abc",
        intent="coding",
        agent="coder",
        provider="stub",
        model="stub-local",
        tools_allowed=["filesystem.read"],
        route_reason="coder_default",
    )
    path = store.write(trace)
    assert path.exists()
    assert (tmp_path / "events.jsonl").exists()


def test_request_rejects_empty():
    try:
        HyperMindRequest(raw_input="  ")
        assert False, "expected ValueError"
    except ValueError:
        pass
