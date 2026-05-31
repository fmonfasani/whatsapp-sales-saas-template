# DEPLOY — WhatsApp SaaS en una VPS (Ubuntu 24.04)

Runbook ejecutable para llevar WhatsApp SaaS de cero a producción en un VPS
single-host. Asume Ubuntu 24.04, dominio apuntando al VPS por A/AAAA, y un
correo válido para Let's Encrypt.

> **TL;DR**
> ```bash
> ssh root@tu-vps
> apt update && apt install -y git
> git clone <repo> /opt/sample && cd /opt/sample
> sudo bash infra/scripts/bootstrap.sh sample.example.com you@example.com
> sudo nano /opt/sample/.env.prod        # rellenar <CHANGE_ME>
> sudo bash infra/scripts/deploy.sh
> sudo bash infra/scripts/healthcheck.sh
> ```

## 1. Prerrequisitos

- **VPS:** 4 GB RAM / 2 vCPU mínimos (Hetzner CX22, DigitalOcean s-2vcpu-4gb).
- **Sistema:** Ubuntu 24.04 LTS limpio, acceso `root` por SSH.
- **DNS:** registro `A` (y `AAAA` si tenés IPv6) para tu dominio apuntando al VPS.
- **Cuentas externas:** OpenRouter (LLM), Meta Business (WhatsApp), Kapso (gateway).

## 2. Bootstrap (una sola vez)

```bash
ssh root@tu-vps
apt update && apt install -y git
git clone https://github.com/fmonfasani/sample.git /opt/sample
cd /opt/sample
sudo bash infra/scripts/bootstrap.sh sample.example.com you@example.com
```

Lo que hace:

1. Instala `docker`, `docker compose plugin`, `certbot`, `ufw`, `fail2ban`,
   `gettext-base`.
2. Cierra el firewall a todo excepto 22/80/443 (SSH/HTTP/HTTPS).
3. Genera `.env.prod` con `POSTGRES_PASSWORD`, `APP_ENCRYPTION_KEY` y
   `META_VERIFY_TOKEN` **aleatorios**. Te quedan tres `<CHANGE_ME>` por
   rellenar (`OPENROUTER_API_KEY`, `META_APP_SECRET`, `KAPSO_GATEWAY_URL`).
4. Pide el certificado TLS a Let's Encrypt en modo `standalone` (bind temporal
   al :80 — por eso corre antes que `deploy.sh`).
5. Renderiza `infra/nginx/nginx.conf` con tu dominio.
6. Instala la unit `systemd` para que el stack arranque solo al reboot.
7. Deja `/usr/local/bin/sample-reload-nginx` listo para el hook de renovación.

## 3. Llenar secretos

```bash
sudo nano /opt/sample/.env.prod
```

Reemplazá los tres `<CHANGE_ME>`:

| Variable | Dónde sale |
|---|---|
| `OPENROUTER_API_KEY` | https://openrouter.ai/keys |
| `META_APP_SECRET` | Meta Developer → App → Settings → Basic |
| `KAPSO_GATEWAY_URL` | URL interna del gateway Kapso (o donde corra tu adaptador) |

> El `META_VERIFY_TOKEN` generado por bootstrap se carga acá. **Es el mismo**
> que tenés que pegar en Meta → Webhooks → Verify Token.

## 4. Deploy inicial

```bash
sudo bash infra/scripts/deploy.sh
```

Build de la imagen `app-api` (≈3 min la primera vez), levanta el stack
ordenado por dependencias (postgres → redis → api → nginx) y espera a que
todos los healthchecks queden `healthy`.

## 5. Verificación

```bash
sudo bash infra/scripts/healthcheck.sh
```

Chequea:

- ✓ los 4 contenedores en `healthy`
- ✓ `GET https://sample.example.com/health` → 200
- ✓ días de vida del certificado TLS
- ✓ disco usado < 85%

Si todo OK, configurá el webhook en Meta:

- **Callback URL:** `https://sample.example.com/webhook`
- **Verify Token:** el que tenés en `.env.prod` como `META_VERIFY_TOKEN`

## 6. Operación día a día

| Acción | Comando |
|---|---|
| Pull + rebuild + rolling restart | `sudo bash infra/scripts/update.sh` |
| Volver al sha previo (post update.sh fallido) | `sudo bash infra/scripts/rollback.sh` |
| Dump de Postgres + retención 14 días | `sudo bash infra/scripts/backup.sh` |
| Smoke test E2E | `sudo bash infra/scripts/healthcheck.sh` |
| Ver logs de la API | `docker logs -f app-api` |
| Acceso a Postgres | `docker exec -it app-postgres psql -U sample sample` |

### Cron sugerido

```cron
# Backup diario 04:00 UTC
0 4 * * * /opt/sample/infra/scripts/backup.sh >> /var/log/sample-backup.log 2>&1

# Healthcheck cada minuto (alertable vía monitor externo si exit != 0)
* * * * * /opt/sample/infra/scripts/healthcheck.sh >/dev/null 2>&1 || echo "sample unhealthy at $(date)" | mail -s "[sample] degraded" ops@example.com
```

## 7. Seguridad — qué está aplicado y qué no

**Aplicado:**

- TLS 1.2/1.3 por nginx + HSTS preload + OCSP stapling + headers (`X-Frame`,
  `CSP`, `Referrer-Policy`, `Permissions-Policy`).
- Tokens sensibles cifrados con AES-256-GCM (`sample.security.TokenCipher`).
  La clave vive solo en `.env.prod` (chmod 600, gitignored).
- Logs filtran secretos en *todos* los handlers (`SecretRedactingFilter` en
  el root logger). Patrones: `OPENROUTER_API_KEY`, `META_APP_SECRET`, cualquier
  `*_TOKEN`/`*_SECRET`/`*_PASSWORD`, `Authorization: Bearer …`, claves `sk-…`.
- Rate limiting doble: nginx (20 r/s burst 40 en `/webhook`) + SlowAPI dentro
  de la app (con backend Redis en prod).
- Webhook firmado con HMAC-SHA256 (verificado contra `META_APP_SECRET`).
- Postgres / Redis solo en la red docker interna (no `ports:` a host).
- API expuesta a `127.0.0.1:8000` — nginx es el único camino desde internet.
- Container `api` corre como UID 10001 no-root.
- `ufw` cerrado: solo 22/80/443.
- `fail2ban` instalado para SSH brute-force.

**Pendiente** (fuera del scope de v1):

- Rotación automática de `APP_ENCRYPTION_KEY` (hoy es manual: rotar +
  re-encriptar la columna afectada).
- Multi-VPS / HA / failover.
- SIEM / shipping de logs a un colector externo.

## 8. Troubleshooting

| Síntoma | Diagnóstico |
|---|---|
| `healthcheck.sh` dice `api: unhealthy` | `docker logs app-api` — buscar stack trace |
| TLS expirado | `certbot renew` manualmente; chequear `journalctl -u certbot.timer` |
| Webhook devuelve 401 | `META_APP_SECRET` distinto entre Meta y `.env.prod` |
| Webhook devuelve 429 | rate limit alcanzado; ajustar `APP_RATE_LIMIT_WEBHOOK` |
| OOM en api | bajá `--workers` en el `CMD` del Dockerfile, o subí el límite de memoria en compose |
| Backup falla con "container not running" | el stack está caído; chequear `systemctl status sample` |
