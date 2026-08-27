"""Authenticated Python client for the Nexudus coworking "public" API.

Discovered from the Nexudus white-label SPA (nexudus.site) bundle:

  * Tenant resolution: GET https://spaces.nexudus.com/api/sys/businesses/getByHost?host=<site>
    -> {"Id": ..., "WebAddress": "<site>.spaces.nexudus.com"}  (this is the API base)
  * Auth:  POST {base}/api/token   (form: grant_type=password&username=&password=&totp=)
           -> {"access_token": "<jwt>", "expires_in": ...}
  * Member data: GET/POST {base}/api/public/...  with `Authorization: Bearer <jwt>`

Credentials (first match wins):
  1. NEXUDUS_EMAIL / NEXUDUS_PASSWORD (+ optional NEXUDUS_TOTP, NEXUDUS_SITE)
  2. ~/.config/nexudus/credentials.json
     {"site": "<tenant-slug>", "email": "...", "password": "...", "totp": null}

Tokens are cached in ~/.cache/nexudus/token-<site>.json until ~expiry.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any

import httpx

SYS_BASE = "https://spaces.nexudus.com"
DEFAULT_SITE = os.environ.get("NEXUDUS_SITE", "")  # tenant slug, e.g. "acmecoworking"
CRED_FILE = Path(os.path.expanduser("~/.config/nexudus/credentials.json"))
CACHE_DIR = Path(os.path.expanduser("~/.cache/nexudus"))

# Convenience aliases -> (method, path). {id} is filled from `target`.
ENDPOINTS: dict[str, tuple[str, str]] = {
    "deliveries": ("GET", "/api/public/deliveries/my?showPending={pending}"),
    "delivery": ("GET", "/api/public/deliveries/{id}"),
    "collect": ("PUT", "/api/public/deliveries/{id}/markAsCollected"),
    "profile": ("GET", "/api/public/coworkers/profiles"),
    "business": ("GET", "/api/public/businesses/current"),
    "configuration": ("GET", "/api/public/configuration"),
    "bookings": ("GET", "/api/public/bookings/my?showUpcoming={pending}"),
    "invoices": ("GET", "/api/public/billing/invoices/my?paid=false&creditNotes=false"),
    "events": ("GET", "/api/public/events/my?showUpcoming={pending}"),
    "visitors": ("GET", "/api/public/visitors/my?showUpcoming={pending}"),
    "plans": ("GET", "/api/public/plans/my"),
    "files": ("GET", "/api/public/files/my"),
    "teams": ("GET", "/api/public/teams/my?isTeamAdmin=false&teamId="),
    "products": ("GET", "/api/public/products/my"),
    "onboarding": ("GET", "/api/public/onboarding"),
    "resources": ("GET", "/api/public/resources/published/summary"),
    "published-plans": ("GET", "/api/public/plans/published"),
    "public-events": ("GET", "/api/public/events?onlyHomePage=true"),
    "countries": ("GET", "/api/public/countries"),
    # --- visitors (write) ---
    "visitor-create": ("POST", "/api/public/visitors"),
    "visitor-delete": ("DELETE", "/api/public/visitors/{id}"),
    # --- bookings (read + write) ---
    "booking": ("GET", "/api/public/bookings/{id}"),
    "booking-cancel": ("DELETE", "/api/public/bookings/{id}"),
    "booking-fee": ("GET", "/api/public/bookings/{id}/cancellationFee"),
    "booking-policies": ("GET", "/api/public/bookings/cancellation-policies/{id}"),
    "booking-available": ("POST", "/api/public/bookings/available"),
    "booking-price": ("POST", "/api/public/bookings/price"),
    "booking-preview": ("POST", "/api/public/bookings/{id}/preview"),
    "booking-suggestions": ("GET", "/api/public/bookings/suggestions"),
    "bookings-cancelled": ("GET", "/api/public/bookings/cancelled"),
    "basket-preview": ("POST", "/api/public/checkout/basket/preview"),
    "basket-invoice": ("POST", "/api/public/checkout/basket/invoice"),
    # --- other member surfaces ---
    "helpdesk": ("GET", "/api/public/helpdesk/messages?showClosed=false"),
    "helpdesk-create": ("POST", "/api/public/helpdesk/messages"),
    "board": ("GET", "/api/public/community/board/threads?groupId=&inbox=&query=&tag="),
    "delivery-save": ("PUT", "/api/public/deliveries"),
    "floorplans": ("GET", "/api/public/floorPlans"),
    "sensors": ("GET", "/api/public/sensors"),
    "announcements": ("GET", "/api/public/announcements/active"),
}

PUBLIC_ACTIONS = {"business", "configuration", "resources", "published-plans",
                  "public-events", "countries"}


class NexudusError(RuntimeError):
    pass


def _load_credentials(site: str | None = None) -> dict[str, Any]:
    cfg: dict[str, Any] = {}
    if CRED_FILE.exists():
        try:
            cfg = json.loads(CRED_FILE.read_text())
        except Exception as exc:  # pragma: no cover
            raise NexudusError(f"{CRED_FILE} is not valid JSON: {exc}") from exc
    email = os.environ.get("NEXUDUS_EMAIL") or cfg.get("email")
    password = os.environ.get("NEXUDUS_PASSWORD") or cfg.get("password")
    totp = os.environ.get("NEXUDUS_TOTP") or cfg.get("totp")
    resolved = site or os.environ.get("NEXUDUS_SITE") or cfg.get("site") or DEFAULT_SITE
    return {"site": resolved, "email": email, "password": password, "totp": totp}


async def resolve_base(site: str) -> str:
    """Return the API base URL (https://<web>.spaces.nexudus.com) for a tenant slug/host."""
    if not site:
        raise NexudusError(
            "No Nexudus site configured. Set NEXUDUS_SITE=<tenant-slug>, pass site=..., or add "
            f'"site" to {CRED_FILE}.'
        )
    host = site.split("//")[-1].split("/")[0]
    if host.endswith(".spaces.nexudus.com"):
        return f"https://{host}"
    slug = host.split(".")[0]
    cache = CACHE_DIR / f"base-{slug}.json"
    if cache.exists():
        try:
            return json.loads(cache.read_text())["base"]
        except Exception:
            pass
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(f"{SYS_BASE}/api/sys/businesses/getByHost", params={"host": slug})
    if r.status_code != 200:
        raise NexudusError(f"tenant lookup failed for {slug!r}: HTTP {r.status_code} {r.text[:200]}")
    body = r.json()
    web = body.get("WebAddress")
    if not web:
        raise NexudusError(f"no Nexudus business found for host {slug!r}: {body}")
    base = web if web.startswith("http") else f"https://{web}"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"base": base, "businessId": body.get("Id")}))
    return base


async def get_token(site: str | None = None, force: bool = False) -> str:
    """Return a cached or freshly minted bearer token for the member account."""
    cred = _load_credentials(site)
    slug = cred["site"].split("//")[-1].split(".")[0]
    tok_file = CACHE_DIR / f"token-{slug}.json"
    if not force and tok_file.exists():
        try:
            cached = json.loads(tok_file.read_text())
            if cached.get("expires_at", 0) > time.time() + 60:
                return cached["access_token"]
        except Exception:
            pass
    if not cred["email"] or not cred["password"]:
        raise NexudusError(
            "No Nexudus credentials. Set NEXUDUS_EMAIL/NEXUDUS_PASSWORD (+NEXUDUS_SITE), or write "
            f'{CRED_FILE} with {{"site": "<tenant-slug>", "email": "...", "password": "..."}}.'
        )
    base = await resolve_base(cred["site"])
    form = {"grant_type": "password", "username": cred["email"], "password": cred["password"]}
    if cred.get("totp"):
        form["totp"] = str(cred["totp"])
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"{base}/api/token",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
        )
    if r.status_code != 200:
        try:
            err = r.json()
            detail = f"{err.get('error')}: {err.get('error_description')}"
        except Exception:
            detail = r.text[:300]
        if "two_factor" in detail:
            detail += " (set NEXUDUS_TOTP to a current 2FA code and retry)"
        raise NexudusError(f"login failed (HTTP {r.status_code}) {detail}")
    body = r.json()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tok_file.write_text(
        json.dumps({"access_token": body["access_token"], "expires_at": time.time() + float(body.get("expires_in", 3600))})
    )
    os.chmod(tok_file, 0o600)
    return body["access_token"]


async def request(
    path: str,
    method: str = "GET",
    data: Any = None,
    site: str | None = None,
    authenticated: bool = True,
) -> Any:
    """Call any Nexudus endpoint. `path` may be a full URL or a /api/... path."""
    cred = _load_credentials(site)
    base = await resolve_base(cred["site"])
    url = path if path.startswith("http") else base + ("" if path.startswith("/") else "/") + path
    headers = {"Accept": "application/json", "Content-Type": "application/json", "X-Use-Timezone": "true"}
    if authenticated:
        headers["Authorization"] = f"Bearer {await get_token(cred['site'])}"
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.request(method.upper(), url, headers=headers, json=data)
        if r.status_code == 401 and authenticated:  # stale token -> retry once
            headers["Authorization"] = f"Bearer {await get_token(cred['site'], force=True)}"
            r = await c.request(method.upper(), url, headers=headers, json=data)
    if r.status_code >= 400:
        raise NexudusError(f"{method.upper()} {url} -> HTTP {r.status_code} {r.text[:400]}")
    if not r.content:
        return {"status": r.status_code, "body": None}
    try:
        return r.json()
    except Exception:
        return r.text


async def deliveries(pending: bool = True, site: str | None = None) -> Any:
    """List the logged-in member's deliveries (pending=True -> uncollected only)."""
    return await request(f"/api/public/deliveries/my?showPending={str(pending).lower()}", site=site)


async def mark_collected(delivery_id: str, site: str | None = None) -> Any:
    """Mark one delivery as collected."""
    return await request(f"/api/public/deliveries/{delivery_id}/markAsCollected", method="PUT", site=site)


async def invite_visitor(
    full_name: str,
    email: str,
    expected_arrival: str,
    phone: str = "",
    notes: str = "",
    site: str | None = None,
) -> Any:
    """Register a visitor. `expected_arrival` is local time, e.g. "2026-09-01T10:00:00"."""
    payload = {
        "FullName": full_name,
        "Email": email,
        "PhoneNumber": phone,
        "Notes": notes,
        "ExpectedArrival": expected_arrival,
    }
    return await request("/api/public/visitors", method="POST", data=payload, site=site)


async def create_booking(
    resource_id: int,
    from_time: str,
    to_time: str,
    coworker_full_name: str = "",
    charge_now: bool = False,
    preview_only: bool = True,
    site: str | None = None,
) -> Any:
    """Create a booking through the basket/checkout flow (the SPA's only way to book).

    Times are UTC ISO with milliseconds, e.g. "2026-09-01T09:00:00.000Z".
    `preview_only=True` prices it without committing (POST /checkout/basket/preview);
    set preview_only=False to actually book (POST /checkout/basket/invoice).
    A £0 invoice is created when membership credits cover the slot.
    """
    import uuid as _uuid

    booking = {
        "ResourceId": resource_id,
        "FromTime": from_time,
        "ToTime": to_time,
        "ChargeNow": charge_now,
        "BookingVisitors": [],
        "BookingProducts": [],
        "CustomFields": None,
        "Id": 0,
        "UniqueId": str(_uuid.uuid4()),
        "CoworkerFullName": coworker_full_name,
    }
    body = {
        "Basket": [{"Type": "booking", "Booking": booking}],
        "agreedTermsAndConditions": True,
        "createZeroValueInvoice": True,
    }
    path = "/api/public/checkout/basket/preview" if preview_only else "/api/public/checkout/basket/invoice"
    return await request(path, method="POST", data=body, site=site)


async def cancel_booking(booking_id: int | str, reason: str = "Other", details: str = "",
                         site: str | None = None) -> Any:
    """Cancel one booking (DELETE with a cancellation-reason body)."""
    payload = {"id": int(booking_id), "cancellationReason": reason,
               "cancellationReasonDetails": details}
    return await request(f"/api/public/bookings/{booking_id}", method="DELETE",
                         data=payload, site=site)


async def booking_available(resource_id: int, from_time: str, to_time: str,
                            coworker_id: int | None = None, site: str | None = None) -> Any:
    """Check whether a resource is free. Times are ISO-8601 UTC, e.g. "2026-09-01T09:00:00Z".

    `coworker_id` is required by the plan-eligibility rule; omit it and the API returns
    Available=false with ErrorCode=CUSTOM_MESSAGE. Get it from `profile` / any booking record.
    """
    payload: dict[str, Any] = {"ResourceId": resource_id, "FromTime": from_time, "ToTime": to_time}
    if coworker_id is not None:
        payload["CoworkerId"] = coworker_id
    return await request("/api/public/bookings/available", method="POST", data=payload, site=site)


def _rows(payload: Any) -> list[dict]:
    """Best-effort extraction of the record list from a Nexudus response."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("Records", "Results", "Items", "Value", "Data"):
            inner = payload.get(key)
            if isinstance(inner, list):
                return inner
            if isinstance(inner, dict) and isinstance(inner.get("Records"), list):
                return inner["Records"]
        # single-purpose wrappers like {"Plans": [...]} / {"Resources": [...]}
        lists = [v for v in payload.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
        if len(lists) >= 1:
            return lists[0]
        return [payload]
    return []


def _clip(value: Any, width: int = 90) -> str:
    text = json.dumps(value, default=str) if isinstance(value, (dict, list)) else str(value)
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 3] + "..."


def _summarise(payload: Any, limit: int = 20) -> str:
    rows = _rows(payload)
    if not rows or not all(isinstance(r, dict) for r in rows):
        return _clip(payload, 6000)
    preferred = [
        "Id", "Name", "Title", "Notes", "Description", "Status", "Carrier", "TrackingNumber",
        "ArrivedOn", "CollectedOn", "Collected", "CoworkerName", "CoworkerFullName",
        "ResourceName", "FromTime", "ToTime", "InvoiceNumber", "Total", "TotalPrice",
        "PriceFormatted", "BusinessName",
    ]
    out = [f"{len(rows)} record(s)"]
    for row in rows[:limit]:
        keys = [k for k in preferred if k in row] or [
            k for k, v in list(row.items())[:10] if not isinstance(v, (dict, list))
        ][:8]
        out.append(" | ".join(f"{k}={_clip(row.get(k))}" for k in keys))
    if len(rows) > limit:
        out.append(f"... {len(rows) - limit} more (use raw=True for full JSON)")
    return "\n".join(out)


async def _run(
    action: str = "deliveries",
    target: str = "",
    site: str = "",
    pending: bool = True,
    method: str = "GET",
    data: str = "",
    raw: bool = False,
    limit: int = 20,
    anon: bool = False,
) -> str:
    """Query a Nexudus coworking site's member API (deliveries, bookings, invoices, ...).

    action: one of the aliases in nexudus.ENDPOINTS, plus `endpoints` (list aliases),
            `login` (check credentials), or `path` (raw call, put the /api/... path in `target`).
    target: delivery/record id, or the raw API path when action="path".
    site:   tenant slug or host (default: $NEXUDUS_SITE or "site" in the credentials file).
    pending: showPending/showUpcoming flag for list endpoints.
    method: HTTP method for action="path".
    data:   JSON body string for POST/PUT calls.
    raw:    return full JSON instead of a summarised table.
    """
    site_arg = site or None
    if action == "endpoints":
        return "\n".join(f"{k:14s} {m} {p}" for k, (m, p) in sorted(ENDPOINTS.items())) + \
            "\nplus: path (raw call), login (credential check), endpoints (this list)"
    if action == "login":
        cred = _load_credentials(site_arg)
        base = await resolve_base(cred["site"])
        await get_token(cred["site"], force=True)
        return f"OK: authenticated as {cred['email']} on {base}"

    body = json.loads(data) if data else None
    if action == "path":
        if not target:
            return "action='path' needs target='/api/public/...'"
        payload = await request(target, method=method, data=body, site=site_arg,
                                authenticated=not anon)
    else:
        if action not in ENDPOINTS:
            return f"Unknown action {action!r}. Try action='endpoints'."
        meth, path = ENDPOINTS[action]
        if "{id}" in path:
            if not target:
                return f"action={action!r} needs target=<id>"
            path = path.replace("{id}", str(target))
        path = path.replace("{pending}", str(pending).lower())
        payload = await request(path, method=method if method != "GET" else meth, data=body,
                                site=site_arg, authenticated=action not in PUBLIC_ACTIONS)
    return json.dumps(payload, indent=2, default=str) if raw else _summarise(payload, limit)


async def run(
    action: str = "deliveries",
    target: str = "",
    site: str = "",
    pending: bool = True,
    method: str = "GET",
    data: str = "",
    raw: bool = False,
    limit: int = 20,
    anon: bool = False,
) -> str:
    """Query a Nexudus coworking site's member API (deliveries, bookings, invoices, ...).

    action: one of the aliases in nexudus.ENDPOINTS, plus `endpoints` (list aliases),
            `login` (check credentials), or `path` (raw call, path goes in `target`).
    target: record id, or the raw API path when action="path".
    site:   tenant slug or host (default: $NEXUDUS_SITE or "site" in the credentials file).
    pending: showPending/showUpcoming flag for list endpoints.
    method: HTTP method for action="path".
    data:   JSON body string for POST/PUT calls.
    raw:    return full JSON instead of a summarised table.
    limit:  max rows in the summary.
    anon:   skip authentication (for public endpoints) when action="path".
    """
    try:
        return await _run(action, target, site, pending, method, data, raw, limit, anon)
    except NexudusError as exc:
        return f"ERROR: {exc}"


if __name__ == "__main__":  # pragma: no cover
    import sys

    print(asyncio.run(run(*sys.argv[1:])))
