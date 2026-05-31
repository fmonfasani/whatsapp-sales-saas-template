# config/tenants

Per-tenant config seed data. Real tenant configs are **never** committed —
this directory exists so the loader has a place to look, with a `.example`
showing the expected shape.

```
config/tenants/
├── README.md                    # this file
├── tenant.example.yaml          # template, committed
└── *.yaml                       # real tenants, gitignored
```

For a multi-tenant SaaS, prefer storing tenant config in the database
(`Tenant` model). Use this directory only for bootstrap / seed data.
