---
name: nexudus
description: Query a Nexudus-powered coworking site's member API (deliveries/parcels, bookings, invoices, visitors, events, plans, profile) over HTTP, e.g. myspace.nexudus.site. Use when the user asks about packages or mail waiting for them at the coworking space, wants to mark a delivery collected, list their room bookings or invoices, or wants to automate/integrate anything on a nexudus.site or spaces.nexudus.com portal.
---

# Nexudus member API

Python skill, callable directly in the kernel:

```python
await nexudus("deliveries")                 # my uncollected parcels
await nexudus("deliveries", pending=False)  # full history
await nexudus("delivery", target="<id>")
await nexudus("collect", target="<id>")     # mark collected
await nexudus("visitors")                   # upcoming guests
await nexudus.invite_visitor("Ada Lovelace", "ada@example.com", "2026-09-01T10:00:00")
await nexudus.create_booking(<resource_id>, "2026-09-01T09:00:00.000Z", "2026-09-01T09:30:00.000Z",
                             coworker_full_name="Your Name", preview_only=True)   # price it
await nexudus.cancel_booking(<booking_id>, reason="Other", details="plans changed")
await nexudus.booking_available(<resource_id>, "2026-09-01T09:00:00Z", "2026-09-01T09:30:00Z",
                                coworker_id=<your_coworker_id>)   # from "profile"
await nexudus("endpoints")                  # list all 39 aliases
await nexudus("path", target="/api/public/bookings/my?showUpcoming=true", raw=True)
await nexudus("path", target="/api/public/countries", anon=True)   # no login needed
```

Shell form: `nexudus deliveries --pending False --raw True`

`<tenant-slug>` is the first label of the portal host: `https://<slug>.nexudus.site/...`.

## Setup (once)

Credentials are the member's normal portal login:

```bash
mkdir -p ~/.config/nexudus && chmod 700 ~/.config/nexudus
cat > ~/.config/nexudus/credentials.json <<'JSON'
{"site": "<tenant-slug>", "email": "you@example.com", "password": "..."}
JSON
chmod 600 ~/.config/nexudus/credentials.json
nexudus login          # verifies and caches a bearer token
```

Or export `NEXUDUS_SITE`, `NEXUDUS_EMAIL`, `NEXUDUS_PASSWORD` (plus `NEXUDUS_TOTP`
if 2FA is on — a login attempt reports `two_factor_auth_check` when it is needed).
Tokens are cached in `~/.cache/nexudus/token-<site>.json`.

## How it works

1. `GET https://spaces.nexudus.com/api/sys/businesses/getByHost?host=<slug>` -> tenant API base
   (`https://<slug>.spaces.nexudus.com`).
2. `POST {base}/api/token` with `grant_type=password` -> `access_token` (JWT).
3. `GET/POST {base}/api/public/...` with `Authorization: Bearer <jwt>`.

Unauthenticated, no credentials needed: `business`, `configuration`, `resources`,
`published-plans`, `public-events`, `countries`, plus `https://<site>.nexudus.site/llms.txt` for a human-readable site summary.

See [references/api.md](references/api.md) for the endpoint map and troubleshooting.
