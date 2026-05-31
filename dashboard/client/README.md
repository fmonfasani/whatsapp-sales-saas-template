# dashboard/client

Customer-facing dashboard placeholder. T3 ships **only the admin dashboard**
(`dashboard/admin/`) — the client-facing one is deferred until a stable
`Conversation` entity exists, which is a P11 deliverable in the Waseller
reference project.

When you're ready to build it, the cleanest path is:

1. `npx create-next-app@latest dashboard/client --typescript --tailwind --app --no-src-dir --import-alias "@/*"`
2. Mirror the structure of `dashboard/admin/src/{lib,app}` so the two
   dashboards share conventions.
3. Reuse `dashboard/admin/src/lib/api.ts` shape; new endpoints (conversations,
   leads, analytics) get added to `services/api/main.py` first.
4. Add a `dashboard-client` job to `.github/workflows/ci.yml` matching the
   existing `dashboard-admin` job.

Until then, this directory is intentionally empty.
