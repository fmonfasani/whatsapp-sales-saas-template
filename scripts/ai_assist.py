"""CLI: ask the AI runtime to generate files toward a goal.

    python -m scripts.ai_assist "add a /healthz endpoint"

Without ``OPENROUTER_API_KEY`` set, the local fallback provider returns a
deterministic stub (useful for smoke-testing the wiring). With a real key,
the request goes through the routed provider configured in the runtime.

This script is intentionally tiny: it's a thin driver over
``{{ project_slug }}.ai.bootstrap``. Treat it as an example, not a contract —
copy + adapt for your own ai-task workflows.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from sample.ai import bootstrap_runtime, has_real_provider


async def _run(goal: str, context: str) -> int:
    bundle = bootstrap_runtime()
    where = "real provider" if has_real_provider(bundle) else "local fallback (no key)"
    print(f"[ai-assist] using {where} -- {len(bundle.runtime.provider_names)} provider(s)")
    result = await bundle.codegen.generate(goal, context=context)
    print(f"[ai-assist] provider: {result.provider}  tokens: {result.total_tokens}")
    print(f"[ai-assist] notes: {result.notes}")
    if result.degraded:
        print("[ai-assist] WARNING: result degraded (parse/JSON failure)")
    for patch in result.patches:
        print(f"  - {patch.path} ({len(patch.content)} bytes)")
    return 0 if not result.degraded else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask the AI runtime to generate file patches.")
    parser.add_argument("goal", help="What you want built (one sentence is fine).")
    parser.add_argument(
        "--context",
        default="",
        help="Extra constraints / file references the model should consider.",
    )
    args = parser.parse_args(argv)
    return asyncio.run(_run(args.goal, args.context))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
