# Nexudus public API reference (reverse-engineered)

Source: the white-label SPA bundle at `https://<site>.nexudus.site/assets/index-*.js`
(object `Ot` holds the full endpoint map; grep it again if the API changes).

## Hosts

| Purpose | URL |
|---|---|
| Tenant lookup | `GET https://spaces.nexudus.com/api/sys/businesses/getByHost?host=<slug>` |
| Tenant API base | `https://<slug>.spaces.nexudus.com` |
| Portal SPA | `https://<slug>.nexudus.site/<slug>/...` (client-side routes only, not an API) |
| Site summary for LLMs | `https://<slug>.nexudus.site/llms.txt` |

Example: slug `myspace` -> `{"Id": <businessId>, "WebAddress": "myspace.spaces.nexudus.com"}`,
so the API base is `https://myspace.spaces.nexudus.com`.

## Auth

```
POST {base}/api/token
Content-Type: application/x-www-form-urlencoded
grant_type=password&username=<email>&password=<pw>[&totp=<code>]
-> 200 {"access_token": "...", "expires_in": ...}
-> 400 {"error":"invalid_grant","error_description":"The email or password is incorrect."}
-> 400 {"error":"two_factor_auth_check"}         # send totp
-> 400 {"error":"must_reset_password"}           # error_description is a reset token
```

Then `Authorization: Bearer <access_token>`; also send `X-Use-Timezone: true` (the SPA does).
Refresh: `GET {base}/api/sys/users/token/refresh`.
Impersonation (team admins): `GET /api/public/coworkers/{id}/impersonate` -> token,
then `GET /api/sys/users/exchange?token=...&validForInMinutes=1440`.

## Deliveries (page `/user/activity/deliveries`)

| Call | Path |
|---|---|
| List mine | `GET /api/public/deliveries/my?showPending=true|false` |
| Details | `GET /api/public/deliveries/{id}` |
| Mark collected | `PUT /api/public/deliveries/{id}/markAsCollected` (POST returns 405) |
| Create | `POST /api/public/deliveries` |

## Other member endpoints seen in the bundle

- Bookings/visitors/events/courses/files: `/api/public/{bookings,visitors,events,courses/v2,files}/my`
- Billing: `/api/public/billing/invoices/my?paid=&creditNotes=`, `/api/public/billing/invoices/{id}/pdf?t=<jwt>`
- Contracts: `/api/public/billing/coworkerContracts/{id}`, `.../v2/{id}/pause`
- Plans/products: `/api/public/plans/my`, `/api/public/products/my`, `/api/public/store/products`
- Profile: `PATCH /api/public/coworker/profile`, `GET /api/public/coworkers/profiles`
- Directory: `/api/public/coworkers/published`, `/api/public/teams/published`
- Virtual office / mail: `/api/public/vo/{meta,addresses,recipients,preferences}`
- Public/anon (verified 200 without a token): `/api/public/businesses/current`,
  `/api/public/configuration`, `/api/public/countries`,
  `/api/public/events?onlyHomePage=true`, `/api/public/blogPosts`,
  `/api/public/plans/published`, `/api/public/resources/published/summary`,
  `/api/public/resources/published/details`, `/api/public/store/products`
- The paths advertised in `llms.txt` (`/api/public/resources`, `/api/public/tariffs`,
  `/api/public/bootstrap`) are **wrong** -> 404. Use the ones above.
- Query modifiers the API understands: `?page=`, `?size=`, `?_shape=Field1,Field2`

## Notes / gotchas

- `https://<slug>.nexudus.site/api/public/...` returns the SPA HTML — always call the
  `*.spaces.nexudus.com` base instead.
- 401 with no body = missing/expired bearer token (the skill retries once with a fresh token).
- Feature flags gate pages: `PublicWebSite.Deliveries`, `PublicWebsite.MyActivity.Deliveries.Hide`
  in `GET /api/public/configuration`.
- Official docs for the admin/back-office API (different auth, `/api/spaces/...`):
  https://developers.nexudus.com — useful if you need write access beyond member scope.

## Visitors (page `/user/activity/visitors`)

| Call | Path |
|---|---|
| List mine | `GET /api/public/visitors/my?showUpcoming=true[&hostApprovalStatus=]` |
| **Invite** | `POST /api/public/visitors` body `{FullName, Email, PhoneNumber, Notes, ExpectedArrival}` (local time) |
| Delete | `DELETE /api/public/visitors/{id}` |
| Details | `GET /api/public/visitors/details/{coworkerId}/{visitorId}` |
| Host approve | `POST /api/public/visitors/details/{cid}/{vid}/approve?cid=&vid=&status=` |

Record fields: `FullName, Email, PhoneNumber, HostApprovalStatus, Notes, ExpectedArrival,
UtcExpectedArrival, Arrived, ArrivalDate, Id, UniqueId`.

## Bookings

| Call | Path |
|---|---|
| List mine | `GET /api/public/bookings/my` (also `/team`, `/cancelled`, `/team/cancelled`) |
| One | `GET /api/public/bookings/{id}` |
| Availability | `POST /api/public/bookings/available` body `{ResourceId, FromTime, ToTime, CoworkerId}` |
| Price quote | `POST /api/public/bookings/price?_shape=Price,DynamicPriceAdjustment,...` |
| Update preview | `POST /api/public/bookings/{id}/preview` |
| **Cancel** | `DELETE /api/public/bookings/{id}` body `{id, cancellationReason, cancellationReasonDetails}` |
| Cancellation fee | `GET /api/public/bookings/{id}/cancellationFee` |
| Cancellation policy | `GET /api/public/bookings/cancellation-policies/{resourceId}` |
| Suggestions | `GET /api/public/bookings/suggestions` |
| Floor plans | `GET /api/public/floorPlans`, `/api/public/floorPlans/assets`, `/api/public/floorPlans/layout?id=&guid=` |
| Resource products | `GET /api/public/resources/published/{id}/products` |

**Creating a booking is a basket/checkout flow, not a single POST**: the SPA builds a booking
object `{ResourceId, FromTime, ToTime, ChargeNow, BookingVisitors, BookingProducts, CustomFields,
Id, UniqueId, CoworkerFullName}`, prices it via `bookings/price`, then commits with
`POST /api/public/checkout/basket/preview` followed by `POST /api/public/checkout/basket/invoice`,
both with body `{"Basket":[{"Type":"booking","Booking":{...}}],"agreedTermsAndConditions":true,
"createZeroValueInvoice":true}`. Verified working: preview returns `preview.TotalFormated`
and priced lines; invoice returns an **empty body (`None`)** on success — confirm by re-listing
`bookings`. Booking credits show as an offsetting negative line, giving a £0.00 invoice.
`POST /api/public/bookings/available` without `CoworkerId` fails the
"Must have Plan or Coworking to Book" rule and returns `Available=false`.

## Other member write surfaces in the bundle

- Helpdesk: `GET/POST /api/public/helpdesk/messages`, `POST .../{id}/close`, comments CRUD
- Community board: `/api/public/community/board/...` (returns `400 DISABLED` on this tenant)
- Profile: `PATCH /api/public/coworker/profile`, `POST /api/public/coworkers/profiles`
- Plans: `POST /api/public/plans/cancel`; contracts pause/resume `.../v2/{id}/pause|resume`
- Perks `POST /api/public/perks/{id}/claim`, events `POST /api/public/events/my/{id}/sendTicket`,
  `DELETE /api/public/events/my/{id}` (cancel ticket), courses `POST /api/public/courses/{id}/signup`
- Forms/surveys: `POST /api/public/forms/{id}`, `POST /api/public/survey/submit`
- Settings: `POST /api/public/settings/value/{key}`
