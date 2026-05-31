# AI runtime — {{ project_name }}

This project ships with [`aine-platform`](https://github.com/fmonfasani/hookclose)
wired up via [`{{ project_slug }}.ai.bootstrap`](../src/{{ project_slug }}/ai/bootstrap.py).
One call returns a bundle ready to call a routed LLM provider.

## TL;DR

```python
from {{ project_slug }}.ai import bootstrap_runtime

bundle = bootstrap_runtime()
result = await bundle.codegen.generate("write a fibonacci function")
print(result.notes)
for patch in result.patches:
    print(patch.path, "→", len(patch.content), "bytes")
```

Or from the CLI:

```bash
make ai-task GOAL="add a /healthz endpoint that returns JSON"
# equivalent to:  python -m scripts.ai_assist "add a /healthz endpoint…"
```

## Without keys

The runtime degrades to a deterministic local fallback provider when none of
the supported env vars are set (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, …).
This means:

- `pip install -e ".[dev]"` works without secrets.
- `pytest` works without secrets — every unit test runs against the fallback.
- `make ai-task GOAL="..."` works without secrets — you get a stub response.

To wire a real provider, copy `.env.example` to `.env`, fill in the key, and
re-run anything. The runtime reads the env at `bootstrap_runtime()` time.

## Mocking providers in tests

The bootstrap helper accepts a custom `Runtime`, which is the supported
escape hatch for test doubles. Two patterns:

### 1. Use the real fallback runtime (cheapest)

```python
from {{ project_slug }}.ai import bootstrap_runtime

def test_my_feature():
    bundle = bootstrap_runtime()       # uses local fallback
    # exercise code that calls bundle.codegen.generate(...)
```

### 2. Hand-build a `Runtime` with a fake `ProviderManager`

```python
from runtime.composition import Runtime
from providers.manager import ProviderManager   # or a stub of the same shape

def test_my_feature():
    fake_manager = StubProviderManager(answers=["…"])
    custom = build_runtime(...)  # wire fake_manager in
    bundle = bootstrap_runtime(runtime=custom)
```

The `aine-platform` README has the full surface; this template only re-exports
the most common entry point so consumers don't need to learn the whole API.

## Where do prompts live?

Two conventions, pick one and stick to it:

- **Inline** — for one-off goals (CLI, scripts, ad-hoc tools), pass the prompt
  string directly to `codegen.generate(goal)`. Good for prototypes.
- **`src/{{ project_slug }}/prompts/`** — for repeated use (skills, agent loops,
  reusable workflows), put each prompt in its own `.md` file and load it from
  Python. Keeps prompt versioning visible in git diffs, lets reviewers comment
  on them like code.

For prompts that reach production traffic, lean toward option 2. For
exploration, inline is fine.

## Cost & observability

`aine-platform` emits events (provider chosen, tokens used, retry attempts).
Subscribe to its event bus to ship those to your observability stack. The
`Runtime.healing` and `Runtime.chainer` give you retry-on-failure and
multi-step task chaining respectively — see the platform's docs for the
full surface.

When you ship real LLM usage to prod, set a cost ceiling at the provider
config level — the routing engine sorts providers by price, so cheaper
models win ties, but it does not impose a hard spend cap by itself.
