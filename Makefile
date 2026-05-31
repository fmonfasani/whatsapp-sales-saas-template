# {{ project_name }} — common dev tasks. `make help` for the menu.
#
# All targets use `python -m <tool>` so they work in any venv and don't depend
# on console-script shims being on PATH.

PYTHON ?= python
VENV   ?= .venv
PIP    := $(VENV)/Scripts/pip
PY     := $(VENV)/Scripts/python

# Cross-platform: on POSIX the bin dir is `bin`, on Windows `Scripts`. Fall back
# if .venv/Scripts doesn't exist (Linux/Mac).
ifeq (,$(wildcard $(VENV)/Scripts))
PIP := $(VENV)/bin/pip
PY  := $(VENV)/bin/python
endif

.DEFAULT_GOAL := help

.PHONY: help
help: ## List the available targets.
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

.PHONY: init
init: ## Run the one-time placeholder substitution (after `degit`/clone).
	$(PYTHON) scripts/init.py

.PHONY: venv
venv: ## Create the local virtualenv at .venv (skip if exists).
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)

.PHONY: dev
dev: venv ## Create the venv + install with the dev extras editable.
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

.PHONY: fmt
fmt: ## Apply ruff format + ruff --fix.
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

.PHONY: lint
lint: ## Ruff check (no autofix).
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

.PHONY: type
type: ## mypy --strict.
	$(PY) -m mypy src tests

.PHONY: test
test: ## pytest.
	$(PY) -m pytest

.PHONY: cov
cov: ## pytest with coverage report.
	$(PY) -m pytest --cov --cov-report=term-missing --cov-report=xml

.PHONY: check
check: lint type test ## Full local gate — run before every push.

.PHONY: ai-task
ai-task: ## Run the AI assistant against a goal: make ai-task GOAL="..."
	@test -n "$(GOAL)" || (echo "usage: make ai-task GOAL=\"<your goal>\"" && exit 1)
	$(PY) -m scripts.ai_assist "$(GOAL)"

.PHONY: up
up: ## Bring up postgres + redis for local dev (docker compose).
	docker compose -f infra/docker/docker-compose.base.yml up -d

.PHONY: down
down: ## Stop the local stack.
	docker compose -f infra/docker/docker-compose.base.yml down

.PHONY: api
api: ## Run the API with auto-reload (assumes `make up` first).
	$(PY) -m uvicorn services.api.main:app --reload --port 8000

.PHONY: clean
clean: ## Remove caches + build artifacts (NOT the venv).
	@rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml htmlcov build dist *.egg-info
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

.PHONY: distclean
distclean: clean ## clean + drop the venv.
	@rm -rf $(VENV)
