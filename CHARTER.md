# CHARTER — {{ project_name }}

The five disciplines this project keeps. Inherited from `project-template`;
edit freely once your project diverges.

## 1. Layers stay sealed

Public API lives in `src/{{ project_slug }}/__init__.py` and nowhere else.
Importing internals from another module within the package is fine; reaching
*into* the package from outside is not. If a consumer needs something, it
gets re-exported from `__init__.py` — that's the negotiation.

## 2. No client / environment data hardcoded

Constants that vary across deploys live in env vars (loaded once at a
boundary) or a config object. The product code is symbolic, not factual.
A magic string in the middle of a function is almost always a bug waiting
to be discovered by the next deploy.

## 3. Ports and adapters for external systems

Anything network-bound (HTTP API, database, queue, blob store, LLM) is
accessed through a Protocol or ABC defined inside this repo. The real
adapter lives next to the port; a fake adapter lives in tests. The product
code never imports the vendor SDK directly.

## 4. One place per cross-cutting concern

Logging config, secret loading, env parsing, retry policy: each one lives
in exactly one module. If you find yourself copying the same `try/except`
or env-var parse twice, that's the signal to extract.

## 5. Green gate before every commit

`make check` (lint + type + test) must pass locally before you push. CI runs
the same gate on every push and pull request. A red main is a fire drill,
not a normal Tuesday.

---

A failure to keep one of these is not a moral problem — it's an instruction
to refactor the offending code into compliance, today, before adding more on top.
