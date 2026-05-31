# services/gateway

The WhatsApp gateway lives **outside this repo as a git submodule**. T3 ships
the adapter (`src/{{ project_slug }}/whatsapp/gateway.py`'s `KapsoGateway`)
but not the gateway service itself — that's the open-source
[Kapso](https://kapso.ai) deployment.

## Add Kapso as a submodule

```bash
git submodule add https://github.com/<kapso-org>/kapso-gateway services/gateway/kapso
git submodule update --init
```

Then point `APP_KAPSO_BASE_URL` in your `.env` at `http://kapso:4000` (or
wherever your compose puts it). The adapter in
`src/{{ project_slug }}/whatsapp/gateway.py` handles the HTTP plumbing.

## Why a submodule, not a copy

- Kapso releases independently — you want to pull upstream fixes without
  squashing the history into your own repo.
- The gateway is a runtime service, not your product code. Treating it as a
  pinned external dependency makes that boundary explicit.

## If you don't want Kapso

The `WhatsAppGatewayPort` in `src/{{ project_slug }}/whatsapp/gateway.py` is
the Protocol — write your own adapter against Meta Cloud API directly (or
any other gateway) and inject it into `Client`. The rest of the agent loop
doesn't care.

For local dev, `InMemoryGateway` (also in `gateway.py`) returns deterministic
fake send receipts — that's what the unit tests use.
