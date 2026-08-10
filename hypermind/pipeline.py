"""Routing pipeline — selection only, no side-effect execution."""

from __future__ import annotations

from dataclasses import dataclass, field

from hypermind.agents import AgentRegistry, AgentRole, select_agent
from hypermind.context import ContextBuilder, ContextBundle
from hypermind.intent import IntentResult
from hypermind.intent.router import IntentRouter
from hypermind.models.router import ModelRoute, ModelRouter
from hypermind.policy import PolicyGate
from hypermind.request import HyperMindRequest
from hypermind.tools import ToolDefinition, ToolRegistry
from hypermind.trace import ExecutionTrace, TraceStore


def _wants_vision(text: str) -> bool:
    lowered = text.lower()
    return any(
        k in lowered
        for k in (
            "screenshot",
            "look at this image",
            "look at this photo",
            "vision model",
            "describe this image",
            "analyze this image",
            "llava",
        )
    )


@dataclass
class RouteResult:
    request: HyperMindRequest
    intent: IntentResult
    agent: AgentRole
    agent_reason: str
    model: ModelRoute
    tools_allowed: list[ToolDefinition] = field(default_factory=list)
    tools_blocked: list[str] = field(default_factory=list)
    context: ContextBundle | None = None
    trace: ExecutionTrace | None = None


class IntelligenceRouter:
    """
    User Request → Intent → Agent → Context → Model → Tools/Policy → Trace
    """

    def __init__(
        self,
        *,
        intent_router: IntentRouter | None = None,
        agents: AgentRegistry | None = None,
        models: ModelRouter | None = None,
        tools: ToolRegistry | None = None,
        policy: PolicyGate | None = None,
        context: ContextBuilder | None = None,
        traces: TraceStore | None = None,
        persist_trace: bool = False,
    ) -> None:
        self.intent_router = intent_router or IntentRouter()
        self.agents = agents or AgentRegistry()
        self.models = models or ModelRouter()
        self.tools = tools or ToolRegistry()
        self.policy = policy or PolicyGate(self.tools)
        self.context = context or ContextBuilder()
        self.traces = traces
        self.persist_trace = persist_trace

    def route(
        self,
        request: HyperMindRequest | str,
        *,
        complexity: str = "normal",
        prefer_local: bool = True,
    ) -> RouteResult:
        if isinstance(request, str):
            request = HyperMindRequest(raw_input=request)

        # Project resolve before intent so domain co-resolution can use it
        # without overriding explicit action intents inside IntentRouter.
        resolution = self.context.resolver.index.resolve(
            request.raw_input, explicit_project=request.project
        )
        intent = self.intent_router.classify(
            request,
            project_key=resolution.project.id if resolution.project else None,
            project_id=resolution.project_id.id if resolution.project_id else None,
        )
        agent, agent_reason = select_agent(
            intent, self.agents, risk_level=request.risk_level
        )
        # Pass architecture reason through
        if intent.reason_code == "architecture_request":
            agent, agent_reason = select_agent(
                intent,
                self.agents,
                risk_level=request.risk_level,
                reason_code="architecture_request",
            )

        model = self.models.route(
            request,
            intent,
            agent,
            prefer_local=prefer_local,
            complexity=complexity,
            require_vision=_wants_vision(request.raw_input),
            require_tools="filesystem.write" in agent.allowed_tools
            and complexity == "deep",
        )

        candidate_tools = self.tools.filter_for_agent(agent, available_only=True)
        allowed: list[ToolDefinition] = []
        blocked: list[str] = []
        for tool in candidate_tools:
            decision = self.policy.check(tool.id, agent)
            if decision.allowed:
                allowed.append(tool)
            else:
                blocked.append(tool.id)
        # Also record globally blocked tools the agent might have listed
        for tool_id in agent.allowed_tools:
            if tool_id not in {t.id for t in allowed} and tool_id not in blocked:
                decision = self.policy.check(tool_id, agent)
                if not decision.allowed:
                    blocked.append(tool_id)

        bundle = self.context.build(
            request, agent, intent=intent.intent, model_name=model.model
        )

        util = bundle.context_utilization
        trace = ExecutionTrace(
            request_id=request.id,
            intent=intent.intent,
            agent=agent.id,
            provider=model.provider,
            model=model.model,
            tools_allowed=[t.id for t in allowed],
            route_reason=model.reason_code,
            status="routed",
            intent_reason=intent.reason_code,
            agent_reason=agent_reason,
            policy_blocked=sorted(set(blocked)),
            context_items=len(bundle.items),
            context_chars=bundle.total_chars,
            context_truncated=bundle.truncated,
            context_sources=list(bundle.sources_used),
            generation_count=0,
            duration_ms=None,
            metadata={
                "intent_confidence": intent.confidence,
                "intent_method": intent.method,
                "complexity": complexity,
                "context_items": len(bundle.items),
                "context_chars": bundle.total_chars,
                "context_truncated": bundle.truncated,
                "context_sources": list(bundle.sources_used),
                "context_project": bundle.project,
                "context_project_id": bundle.project_id,
                "candidate_sections": bundle.candidate_sections,
                "selected_sections": bundle.selected_sections,
                "documents_touched": bundle.documents_touched,
                "deduplicated_items": bundle.deduplicated_items,
                "excerpted_items": bundle.excerpted_items,
                "context_profile": bundle.context_profile,
                "context_budget_chars": bundle.context_budget_chars,
                "context_budget_items": bundle.context_budget_items,
                "context_utilization": util,
                "profile_source": bundle.profile_source,
            },
        )

        if self.persist_trace:
            store = self.traces or TraceStore()
            store.write(trace)

        return RouteResult(
            request=request,
            intent=intent,
            agent=agent,
            agent_reason=agent_reason,
            model=model,
            tools_allowed=allowed,
            tools_blocked=sorted(set(blocked)),
            context=bundle,
            trace=trace,
        )
