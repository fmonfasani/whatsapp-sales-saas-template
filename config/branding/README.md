# config/branding

Product branding lives here so the **code** stays neutral. Anything
client-specific (logo, color palette, copy variants, system prompts that
mention the brand) goes in this directory under your own `.yaml` or `.json`.

This directory is intentionally **gitignored** for everything except
`*.example` files — never commit a real brand config from a client project.

## Convention

```
config/branding/
├── README.md                 # this file (committed)
├── brand.example.yaml        # template, committed
└── brand.yaml                # YOUR brand, gitignored
```

`brand.example.yaml` is the shape the loader expects. Copy it to `brand.yaml`,
fill in real values, point the app at `APP_BRAND_CONFIG=config/branding/brand.yaml`
in your `.env`.
