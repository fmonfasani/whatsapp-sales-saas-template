# whatsapp-sales-saas-template

A complete **WhatsApp Sales SaaS in a box**. Clone, set your keys, point Meta
at your VPS, and you have an autonomous WhatsApp sales agent running under
your own brand.

Built on T2 ([`project-template-aine`](https://github.com/fmonfasani/project-template-aine))
so you inherit a green lint+type+test gate, the `aine-platform` AI runtime,
and all the boring-but-critical infrastructure. T3 adds the WhatsApp vertical:

| Layer | What it ships |
|---|---|
| **SDK** (`src/sample/`) | Tenants · agent loop (recall→SOUL+RAG→LLM→reply) · skills (lead-qualifier, sales-closer, catalog-lookup) · WhatsApp gateway port + Kapso adapter · RAG via Hindsight (in-memory + Postgres tsvector) · buyer memory port + in-memory + Honcho adapter · onboarding (Meta Embedded Signup) · security (AES-256-GCM + log redaction) · event bus |
| **API** (`services/api/`) | FastAPI: `/health`, `/webhook` (Meta HMAC-verified), `/tenants` CRUD, `/tenants/connect-whatsapp` (onboarding), `/skills`, `/goal`, SlowAPI rate limiting, CORS for the dashboard |
| **Workers** (`services/preprocessor/`) | Async queue + drain pattern for ingestion jobs |
| **Gateway** (`services/gateway/`) | README pointing to the Kapso submodule (open-source WhatsApp gateway) |
| **Admin dashboard** (`dashboard/admin/`) | Next.js 14 + TS + Tailwind: tenants list/create/detail/onboard, skills, health |
| **Infra** (`infra/`) | docker-compose.prod.yml (postgres + redis internal, nginx + TLS, restart:always), nginx.conf (HSTS, OCSP stapling, rate cap), Dockerfile.api (multi-stage, non-root), systemd unit, runbook scripts (bootstrap/deploy/update/rollback/backup/healthcheck) |
| **Docs** | `docs/DEPLOY.md` (full VPS runbook) · `docs/QUICKSTART.md` (5-minute local) · `docs/AI.md` (inherited from T2) |
| **Config** (`config/branding/`, `config/tenants/`) | Empty + `.example` files only -- your brand and tenant data live here, gitignored |

What's **deliberately not** included:

- "Waseller" or any other product brand. Your brand lives in `config/branding/`.
- Real tenant data / API keys / `.env`. The `.example` files are templates.
- A second-party customer dashboard. See `dashboard/client/README.md`.

## TL;DR

```bash
npx degit fmonfasani/whatsapp-sales-saas-template my-saas
cd my-saas
python scripts/init.py        # rename src/sample/ to your slug, fill placeholders
make dev                      # venv + pip install -e ".[dev]"
make check                    # full local gate
cp .env.example .env          # then fill in OPENROUTER_API_KEY, META_APP_SECRET, ...
make up                       # docker compose -f infra/docker/docker-compose.base.yml up -d
uvicorn services.api.main:app --reload
```

Then in a Meta-test phone number:

1. POST `/tenants/connect-whatsapp` with a phone_number_id + business_name
2. Send a WhatsApp message to that number
3. The agent replies (echoing via the default EchoLLM, or via OpenRouter if you set the key)

Full step-by-step: [`docs/QUICKSTART.md`](docs/QUICKSTART.md).
Production VPS deploy: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Day-to-day (inherited from T2)

```bash
make fmt        # ruff format + ruff --fix
make lint       # ruff check + ruff format --check
make type       # mypy --strict (src + services + tests)
make test       # pytest (excluding integration marker)
make cov        # coverage report
make check      # lint + type + test (what CI runs)
make ai-task    # AI assistant CLI (from T2)
make clean      # nuke caches
```

## Architecture in one paragraph

A Meta webhook lands at `services/api/main.py:webhook_receive` -> HMAC verified
-> `TenantRouter.try_resolve(phone_number_id)` -> buyer message remembered
-> `AgentLoop.respond(tenant, buyer_id, text)` (recall last N turns ->
tenant-scoped RAG search -> compose SOUL system prompt + history + new message
-> LLM call) -> reply sent via `WhatsAppGatewayPort` (Kapso adapter in prod,
in-memory in tests) -> reply also remembered. Every external system (LLM,
gateway, RAG store, buyer memory) is behind a Protocol, so production wiring
and test wiring use the exact same client code.

## License

MIT (the template). The license of your project is whatever you put in
`scripts/init.py` -- defaults to MIT.
