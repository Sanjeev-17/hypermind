"""HyperMind CLI — route, run (bounded generate), models."""

from __future__ import annotations

import argparse
import json
import sys

from hypermind.agents import AgentRegistry, select_agent
from hypermind.context import ContextBuilder
from hypermind.executor import HyperMindExecutor
from hypermind.intent.router import IntentRouter
from hypermind.memory import MemoryCandidateEngine, MemoryProposeRequest
from hypermind.models.adapters import default_providers
from hypermind.pipeline import IntelligenceRouter
from hypermind.request import HyperMindRequest


def format_route(result) -> str:
    tools = "\n".join(f"  {t.id}" for t in result.tools_allowed) or "  (none)"
    lines = [
        f"Intent: {result.intent.intent}",
        f"Agent: {result.agent.id}",
        f"Provider: {result.model.provider}",
        f"Model: {result.model.model}",
        "Tools:",
        tools,
        "",
        f"Reason: {result.model.reason_code}",
    ]
    return "\n".join(lines)


def format_run(result, *, verbose: bool = False) -> str:
    route = result.route
    lines = [
        f"Intent: {route.intent.intent}",
        f"Agent: {route.agent.id}",
        f"Provider: {route.model.provider}",
        f"Model: {route.model.model}",
    ]
    if verbose:
        ctx = result.trace.context_items
        lines.extend(
            [
                f"Context items: {ctx}",
                f"Context chars: {result.trace.context_chars}",
                f"Context sources: {', '.join(result.trace.context_sources) or '(none)'}",
                f"Duration: {result.trace.duration_ms} ms",
                f"Status: {result.trace.status}",
                f"Route reason: {route.model.reason_code}",
            ]
        )
    lines.append("")
    if result.ok and result.response is not None:
        lines.append("Response:")
        lines.append(result.response.text)
    else:
        lines.append(result.error or "Execution failed.")
    return "\n".join(lines)


def format_models(providers) -> str:
    rows: list[tuple[str, ...]] = [
        ("PROVIDER", "MODEL", "CLASS", "TIER", "TEXT", "VISION", "LAT_MS", "AVAILABLE")
    ]
    for provider in providers:
        for cap in provider.list_models():
            rows.append(
                (
                    cap.provider,
                    cap.model,
                    cap.model_class,
                    cap.latency_tier,
                    "yes" if cap.text_eligible else "no",
                    "yes" if cap.supports_vision else "no",
                    str(cap.estimated_latency_ms)
                    if cap.estimated_latency_ms is not None
                    else "-",
                    "yes" if cap.available else "no",
                )
            )
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = []
    for row in rows:
        lines.append(
            "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))
        )
    return "\n".join(lines)


def cmd_route(args: argparse.Namespace) -> int:
    router = IntelligenceRouter(persist_trace=args.trace)
    request = HyperMindRequest(
        raw_input=args.text,
        project=args.project,
        risk_level=args.risk,
    )
    result = router.route(
        request,
        complexity=args.complexity,
        prefer_local=not args.prefer_cloud,
    )
    if args.json:
        assert result.trace is not None
        print(result.trace.to_json())
    else:
        print(format_route(result))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    on_token = None
    if args.stream and not args.json:

        def on_token(piece: str) -> None:
            sys.stdout.write(piece)
            sys.stdout.flush()

    executor = HyperMindExecutor(
        persist_trace=args.persist_trace,
        allow_stub=args.allow_stub,
        timeout_seconds=args.timeout,
        stream=True if args.stream else None,
        on_token=on_token,
        max_output_tokens=args.max_tokens,
    )
    request = HyperMindRequest(
        raw_input=args.text,
        project=args.project,
        risk_level=args.risk,
    )
    result = executor.execute(
        request,
        complexity=args.complexity,
        prefer_local=not args.prefer_cloud,
    )
    if args.stream and not args.json and result.ok:
        sys.stdout.write("\n")
        if args.trace:
            print(
                f"\n[{result.trace.provider}/{result.trace.model} "
                f"{result.trace.duration_ms}ms status={result.trace.status}]"
            )
        return 0 if result.ok else 1
    if args.json:
        payload = result.trace.to_dict()
        if result.response is not None:
            payload["response_preview"] = result.response.text[:500]
        if result.error:
            payload["error"] = result.error
        print(json.dumps(payload, indent=2))
    else:
        print(format_run(result, verbose=args.trace))
    return 0 if result.ok else 1


def format_context(
    pack,
    *,
    max_items: int,
    max_chars: int,
    intent: str | None = None,
    debug: bool = False,
    profile=None,
) -> str:
    project = pack.project or "(none)"
    if pack.project_id:
        project = f"{project} / {pack.project_id}"
    profile_id = pack.context_profile or (profile.id if profile else "(none)")
    lines = [
        f"Intent: {intent or pack.intent or '(unknown)'}",
        f"Project: {project}",
        f"Context profile: {profile_id}",
        "",
        "Budget:",
        f"{pack.context_budget_items or max_items} items / {pack.context_budget_chars or max_chars:,} chars",
        "",
        "Selected:",
        f"{len(pack.items)} items / {pack.total_chars:,} chars",
        f"Utilization: {pack.context_utilization:.1%}"
        if pack.context_budget_chars
        else f"Candidates: {pack.candidate_sections} sections",
        f"Candidates: {pack.candidate_sections} sections",
        f"Documents touched: {pack.documents_touched}",
        f"Truncated: {'yes' if pack.truncated else 'no'}",
        f"Deduped: {pack.deduplicated_items}  Excerpted: {pack.excerpted_items}",
        "",
    ]
    if debug and profile is not None:
        lines[3:3] = [
            "Profile rules:",
            f"  Profile source: {profile.source}",
            f"  Include profile: {'yes' if profile.include_profile else 'no'}",
            f"  Decision cap: {profile.decisions_max}",
            f"  Section cap: {profile.section_max_chars} chars",
            f"  Preferred sources: {', '.join(profile.preferred_source_types) or '(none)'}",
            (
                f"  Model cap: {profile.model_cap_chars}"
                if profile.model_cap_chars
                else "  Model cap: (none)"
            ),
            "",
        ]
    for i, item in enumerate(pack.items, start=1):
        score = item.metadata.get("score")
        section = item.metadata.get("heading_path") or item.metadata.get("heading")
        lines.append(f"{i}. {item.kind.value}")
        lines.append(f"   {item.source_ref}")
        if section:
            lines.append(f"   Section: {_ascii_safe(str(section))}")
        else:
            lines.append(f"   {_ascii_safe(item.title)}")
        if score is not None:
            try:
                lines.append(f"   Score: {float(score):.2f}")
            except (TypeError, ValueError):
                lines.append(f"   Score: {score}")
        if debug:
            comps = item.metadata.get("score_components") or {}
            for name, val in sorted(comps.items(), key=lambda kv: -kv[1]):
                lines.append(f"      {name:26} +{val:g}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _ascii_safe(text: str) -> str:
    return text.encode("ascii", errors="replace").decode("ascii")


def _print(text: str) -> None:
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode(encoding, errors="replace").decode(encoding, errors="replace"))


def cmd_context(args: argparse.Namespace) -> int:
    """Inspect context selection without calling a model."""
    from hypermind.context.profiles import ContextProfileError
    from hypermind.config import load_models_config
    import os

    request = HyperMindRequest(
        raw_input=args.text,
        project=args.project,
        risk_level=args.risk,
    )
    builder = ContextBuilder()
    resolution = builder.resolver.index.resolve(
        request.raw_input, explicit_project=request.project
    )
    intent = IntentRouter().classify(
        request,
        project_key=resolution.project.id if resolution.project else None,
        project_id=resolution.project_id.id if resolution.project_id else None,
    )
    agent, _ = select_agent(intent, AgentRegistry(), risk_level=request.risk_level)

    model_name = (
        os.getenv("HYPERMIND_OLLAMA_MODEL")
        or load_models_config().ollama.model
        or None
    )
    try:
        profile = builder.resolver.profile_resolver.resolve(
            intent.intent,
            request,
            project=resolution.project.id if resolution.project else None,
            override_profile=args.context_profile,
            override_max_chars=args.max_context_chars,
            override_max_items=args.max_items,
            model_name=model_name,
        )
    except ContextProfileError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    pack = builder.build(
        request,
        agent,
        intent=intent.intent,
        context_profile=args.context_profile,
        max_items=args.max_items,
        max_chars=args.max_context_chars,
        model_name=model_name,
    )
    if args.json:
        payload = {
            "intent": intent.intent,
            "intent_reason": intent.reason_code,
            "project": pack.project,
            "project_id": pack.project_id,
            "context_profile": pack.context_profile,
            "profile_source": pack.profile_source,
            "context_budget_chars": pack.context_budget_chars,
            "context_budget_items": pack.context_budget_items,
            "context_utilization": pack.context_utilization,
            "context_items": len(pack.items),
            "context_chars": pack.total_chars,
            "context_truncated": pack.truncated,
            "context_sources": pack.sources_used,
            "candidate_sections": pack.candidate_sections,
            "selected_sections": pack.selected_sections,
            "documents_touched": pack.documents_touched,
            "deduplicated_items": pack.deduplicated_items,
            "excerpted_items": pack.excerpted_items,
            "items": [
                {
                    "kind": i.kind.value,
                    "source_type": i.source_type,
                    "source_ref": i.source_ref,
                    "title": i.title,
                    "chars": i.chars,
                    "priority": i.priority,
                    "relevance": i.relevance,
                    "score": i.metadata.get("score"),
                    "heading_path": i.metadata.get("heading_path"),
                    "score_components": i.metadata.get("score_components")
                    if args.debug
                    else None,
                }
                for i in pack.items
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        _print(
            format_context(
                pack,
                max_items=profile.max_items,
                max_chars=profile.max_chars,
                intent=intent.intent,
                debug=bool(args.debug),
                profile=profile,
            )
        )
    return 0


def cmd_models(args: argparse.Namespace) -> int:
    if args.benchmark:
        from hypermind.models.benchmark import run_local_benchmark

        result = run_local_benchmark(
            include_vision=bool(args.include_vision),
            timeout_seconds=float(args.benchmark_timeout),
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Wrote latency cache: {result['path']}")
            for name, row in result["models"].items():
                if row.get("skipped_reason"):
                    print(f"  {name}: skipped ({row['skipped_reason']})")
                elif row.get("ok"):
                    print(
                        f"  {name}: ok wall={row.get('wall_ms')}ms "
                        f"class={row.get('model_class')} tier={row.get('latency_tier')}"
                    )
                else:
                    print(
                        f"  {name}: FAIL {row.get('error_code')} "
                        f"wall={row.get('wall_ms')}ms"
                    )
            print("\nRefreshed model listing:")
            print(format_models(default_providers()))
        return 0

    providers = default_providers()
    if args.json:
        data = []
        for provider in providers:
            for cap in provider.list_models():
                data.append(
                    {
                        "provider": cap.provider,
                        "model": cap.model,
                        "local": cap.local,
                        "available": cap.available,
                        "reason": cap.availability_reason,
                        "model_class": cap.model_class,
                        "latency_tier": cap.latency_tier,
                        "text_eligible": cap.text_eligible,
                        "supports_vision": cap.supports_vision,
                        "estimated_latency_ms": cap.estimated_latency_ms,
                    }
                )
        print(json.dumps(data, indent=2))
    else:
        print(format_models(providers))
    return 0


def cmd_memory_propose(args: argparse.Namespace) -> int:
    """Machine contract: stdin JSON → stdout JSON only. No memory writes."""
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as exc:
        err = {
            "ok": False,
            "error": {"code": "INVALID_INPUT", "message": f"Invalid JSON: {exc}"},
        }
        print(json.dumps(err), file=sys.stdout)
        print("invalid stdin JSON", file=sys.stderr)
        return 2

    if not isinstance(payload, dict):
        err = {
            "ok": False,
            "error": {"code": "INVALID_INPUT", "message": "Root must be a JSON object"},
        }
        print(json.dumps(err))
        return 2

    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        err = {
            "ok": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": "Field 'text' is required and must be a non-empty string",
            },
        }
        print(json.dumps(err))
        return 2

    source_refs = payload.get("source_refs") or ["input:user"]
    if not isinstance(source_refs, list) or not all(
        isinstance(x, str) and x.strip() for x in source_refs
    ):
        err = {
            "ok": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": "source_refs must be a list of non-empty strings",
            },
        }
        print(json.dumps(err))
        return 2

    try:
        req = MemoryProposeRequest(
            text=text,
            project=payload.get("project"),
            source_refs=[str(x).strip() for x in source_refs],
            max_candidates=int(payload.get("max_candidates", 5)),
        )
    except (TypeError, ValueError) as exc:
        err = {
            "ok": False,
            "error": {"code": "INVALID_INPUT", "message": str(exc)[:300]},
        }
        print(json.dumps(err))
        return 2

    engine = MemoryCandidateEngine(allow_stub=bool(getattr(args, "allow_stub", False)))
    result = engine.propose(req)
    print(json.dumps(result.to_envelope()))
    if not result.ok:
        print(result.error.get("message", "propose failed") if result.error else "failed", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hypermind",
        description="HyperMind intelligence routing and bounded local execution",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    route = sub.add_parser("route", help="Classify and route a request (no generation)")
    route.add_argument("text", help="User request text")
    route.add_argument("--project", default=None)
    route.add_argument("--risk", default=None, choices=["low", "medium", "high", "critical"])
    route.add_argument(
        "--complexity",
        default="normal",
        choices=["simple", "normal", "deep"],
    )
    route.add_argument("--prefer-cloud", action="store_true")
    route.add_argument("--json", action="store_true", help="Emit execution trace JSON")
    route.add_argument("--trace", action="store_true", help="Persist trace under .hypermind/traces")
    route.set_defaults(func=cmd_route)

    run = sub.add_parser(
        "run",
        help="Route then perform one bounded generation (Ollama when available)",
    )
    run.add_argument("text", help="User request text")
    run.add_argument("--project", default=None)
    run.add_argument("--risk", default=None, choices=["low", "medium", "high", "critical"])
    run.add_argument(
        "--complexity",
        default="normal",
        choices=["simple", "normal", "deep"],
    )
    run.add_argument("--prefer-cloud", action="store_true")
    run.add_argument(
        "--trace",
        action="store_true",
        help="Show operational verbose fields (no hidden reasoning)",
    )
    run.add_argument(
        "--persist-trace",
        action="store_true",
        help="Persist trace under .hypermind/traces",
    )
    run.add_argument("--json", action="store_true", help="Emit execution trace JSON")
    run.add_argument(
        "--allow-stub",
        action="store_true",
        help="Allow stub provider generation (tests / offline demos)",
    )
    run.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Ollama generate timeout seconds (default from models.yaml)",
    )
    run.add_argument(
        "--stream",
        action="store_true",
        help="Stream Ollama tokens to stdout (NDJSON chat API)",
    )
    run.add_argument(
        "--max-tokens",
        type=int,
        default=1024,
        help="Max generation tokens (Ollama num_predict)",
    )
    run.set_defaults(func=cmd_run)

    models = sub.add_parser("models", help="List provider models and availability")
    models.add_argument("--json", action="store_true")
    models.add_argument(
        "--benchmark",
        action="store_true",
        help="One-shot latency probe of installed Ollama models (no download)",
    )
    models.add_argument(
        "--include-vision",
        action="store_true",
        help="Include vision-reserved tags in --benchmark",
    )
    models.add_argument(
        "--benchmark-timeout",
        type=float,
        default=60.0,
        help="Per-model timeout for --benchmark (default 60s)",
    )
    models.set_defaults(func=cmd_models)

    context = sub.add_parser(
        "context",
        help="Inspect bounded context selection (no model call)",
    )
    context.add_argument("text", help="User request text")
    context.add_argument("--project", default=None)
    context.add_argument(
        "--risk", default=None, choices=["low", "medium", "high", "critical"]
    )
    context.add_argument(
        "--context-profile",
        default=None,
        help="Override context profile (design, coding, writing, …)",
    )
    context.add_argument("--max-items", type=int, default=None)
    context.add_argument(
        "--max-context-chars",
        type=int,
        default=None,
        help="Override max context characters (validated)",
    )
    context.add_argument("--json", action="store_true")
    context.add_argument(
        "--debug",
        action="store_true",
        help="Show deterministic score components and profile rules",
    )
    context.set_defaults(func=cmd_context)

    memory = sub.add_parser("memory", help="Controlled memory candidate operations")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)
    propose = memory_sub.add_parser(
        "propose",
        help="Propose memory candidates from stdin JSON (no persistence)",
    )
    propose.add_argument(
        "--json",
        action="store_true",
        default=True,
        help="Emit JSON envelope on stdout (machine default)",
    )
    propose.add_argument(
        "--allow-stub",
        action="store_true",
        help="Allow stub provider (tests / offline demos only)",
    )
    propose.set_defaults(func=cmd_memory_propose)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
