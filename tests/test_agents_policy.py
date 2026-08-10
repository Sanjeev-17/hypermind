"""Agent selection and tool filtering tests."""

from hypermind.agents import AgentRegistry, select_agent
from hypermind.intent import IntentResult
from hypermind.policy import PolicyGate
from hypermind.tools import ToolRegistry


def test_coding_selects_coder():
    intent = IntentResult("coding", 0.9, "deterministic", "repo_operation")
    role, reason = select_agent(intent)
    assert role.id == "coder"
    assert "coder" in reason


def test_architecture_selects_architect():
    intent = IntentResult("planning", 0.9, "deterministic", "architecture_request")
    role, reason = select_agent(intent, reason_code="architecture_request")
    assert role.id == "architect"


def test_memory_selects_knowledge_curator():
    intent = IntentResult("memory", 0.9, "deterministic", "memory_command")
    role, _ = select_agent(intent)
    assert role.id == "knowledge_curator"


def test_tool_filter_respects_agent_allowlist():
    reg = ToolRegistry()
    agent = AgentRegistry().get("design_critic")
    tools = reg.filter_for_agent(agent)
    ids = {t.id for t in tools}
    assert "filesystem.read" in ids
    assert "filesystem.write" not in ids


def test_policy_blocks_delete_by_default():
    gate = PolicyGate()
    coder = AgentRegistry().get("coder")
    # coder does not list delete; even if we check directly:
    decision = gate.check("filesystem.delete", coder)
    assert decision.allowed is False
    assert decision.reason_code == "blocked_by_default"


def test_policy_blocks_email_and_publish():
    gate = PolicyGate()
    agent = AgentRegistry().get("chief_of_staff")
    assert gate.check("email.send", agent).allowed is False
    assert gate.check("publish", agent).allowed is False


def test_coder_write_allowed_when_listed():
    gate = PolicyGate()
    coder = AgentRegistry().get("coder")
    assert gate.check("filesystem.write", coder).allowed is True
    assert gate.check("git.status", coder).allowed is True
