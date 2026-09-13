# BuchhaltungsButler API v1 — Reference

Covers the official Swagger 2.0 spec, `info.version` 1.9.1, all 54 endpoints. BuchhaltungsButler (BB) is a German cloud accounting SaaS. Its API is a flat RPC-over-POST surface, not REST: one path per operation, everything in a JSON body.

## Conventions

### Base URL and documentation

- Base URL: `https://webapp.buchhaltungsbutler.de/api/v1` (the spec's `basePath` is already the full URL — do not concatenate `host` + `basePath`; scheme `https` only; see quirk 22).
- Full URL = base URL + path, e.g. `https://webapp.buchhaltungsbutler.de/api/v1/receipts/get`.
- Human-readable docs: https://app.buchhaltungsbutler.de/docs/api/v1/ — machine spec (German descriptions, HTML inside): https://app.buchhaltungsbutler.de/docs/api/v1.de.json

### Authentication — two layers, both required on every call

| Layer | Where it goes | Value | Where to get it |
|---|---|---|---|
| HTTP Basic Auth (RFC 2617) | `Authorization: Basic base64("<API_CLIENT>:<API_SECRET>")` | API Client and API Secret of the API user | BB web app → **Einstellungen** (settings) → **Schnittstellen und API-Zugang** (interfaces and API access) |
| Customer selector | JSON body field `api_key` (string, required on all 54 endpoints) | the api_key of the **Mandant** (client / customer account) whose books you act on | same settings area, shown per customer |

- Wrong or missing Basic credentials → HTTP 401, code 3. Valid credentials but unknown `api_key`, or an `api_key` this API client is not allowed to manage → HTTP 401, code 4.
- One API client can manage several customers; `api_key` decides whose books you write into. Treat it like a secret and never log it.

### Request format

- Every endpoint is `POST`. All declared parameters are `in: body`, top-level keys of one JSON object; there are no query parameters. The only path variable is the record id of the four `/…/id_by_customer` endpoints (see Identifiers below): the spec writes the placeholder `id_by_customer` where the real URL carries the number, e.g. `POST /receipts/get/123`.
- Send `Content-Type: application/json` (the help-center setup article requires this header with a raw JSON body). The spec declares `produces: application/json` and no `consumes`.
- `/receipts/upload` is the exception: `file` may be a real file upload (multipart form) or a base64 string inside the JSON body. For base64, `file_name` becomes mandatory (error 33 "file name is not specified"); for a real upload `file_name` is ignored.
- Booleans: the spec mostly writes defaults as the string `"false"` (a JSON `false` only on `/accounts/add` and `/settings/get/postingaccounts`); send JSON `true`/`false`.
- Code 23 "no post and files content received or declined" (HTTP 400) means the body was empty or could not be decoded — check `Content-Type` and encoding before anything else.
- Spec descriptions contain HTML (`<br/>`, `<i>`) and German curly quotes; strip them when displaying.

### Response envelopes

Success (list endpoint shown; `rows`/`data` appear only where documented per endpoint):

```json
{"success": true, "message": "", "rows": 12, "data": [ { "...": "..." } ]}
```

- `success` boolean, `message` string (usually `""` on success). Create endpoints return identifying fields at top level instead of `data` (`id_by_customer`, `postingaccount_number`, `filename`, `invoicenumber`, `file_name`, `code`).
- Batch endpoints return `{"success": bool, "<collection>": [per-item results], "errors": [per-item failures]}`; see each batch endpoint. The response shape (per-item results plus `errors[]`) implies partial success; the spec does not state whether successful items are committed when others fail — verify before relying on it.

Error:

```json
{"success": false, "error_code": 7, "message": "invalid date_from specified"}
```

- HTTP status carries the class: 400 validation or business rule, 401 authentication, 403 account state or throttling, 422 unprocessable file (upload only), 500 internal, 504 timeout.
- `error_code` numbers are **per endpoint, not global**. Code 7 is "invalid date_from" on `/receipts/get`, "account does not exist" on `/transactions/add`, "posting not found" on `/postings/cancel`. Always interpret the code together with the path, and prefer `message` for humans.
- Codes that carry the same meaning on every endpoint:

| HTTP | code | message (verbatim) | Meaning |
|---|---|---|---|
| 401 | 3 | API credentials unknown or invalid | Basic Auth failed |
| 401 | 4 | customer not found or insufficient privileges (generic definition: "customer not found or invalid api client for customer or insufficient privileges") | `api_key` unknown or not managed by this API client |
| 403 | 11 | customer has no active status | customer account is not active (subscription state) |
| 500 | 0 | error while processing the request | internal error; retry later |
| 504 | 30 | a timeout occurred while processing the request | server-side timeout; a write may or may not have happened — re-read before retrying |
| 400 | 23 | no post and files content received or declined | empty or undecodable body (declared on 21 endpoints; code 23 means "no receipts assigned to transaction" on `/transactions/unassign/receipt` and can also mean "invalid booking text specified" on `/transactions/add`) |
| 403 | 15 | adding temporarily restricted / upload temporarily restricted | throttled (batch endpoints, `/transactions/add`, `/receipts/upload`) |

Defined in the spec but referenced by no path: code 1 "Api method calls require HTTP requests", code 2 "Api method calls require POST requests".

### Rate limits

| Scope | Limit | Source |
|---|---|---|
| all endpoints | 100 requests per customer (`api_key`) per minute | docs page |
| `/receipts/upload` | max 10 requests per minute | spec |
| `/receipts/addBatch`, `/transactions/addBatch` | one request every 5 seconds | spec |
| batch endpoints, `/transactions/add`, `/receipts/upload` | HTTP 403 code 15 when throttled | spec |
| `/receipts/upload` | HTTP 403 code 12 "customer has reached the upload limit" (plan quota) | spec |
| `/invoices/create`, `/invoices/create/e-invoice` | HTTP 403 code 33 "customer has reached the upload limit" | spec |

No `Retry-After` header is documented. Back off (≥ 5 s for batch throttles, ≥ 60 s for the per-minute limits) and retry; never retry a write blindly after 504/code 30.

### Pagination

Paging is `limit`/`offset` in the body. Defaults and caps differ per endpoint:

| Endpoint | `limit` default | `limit` max | `offset` default |
|---|---|---|---|
| `/receipts/get` | 500 | 500 | 0 |
| `/transactions/get` | 500 | 500 | 0 |
| `/postings/get` | not stated (request capped at 1000 postings) | 1000 | not stated |
| `/cost-locations/get` | not stated (request capped at 1000) | 1000 | not stated |
| `/settings/get/creditors` | 25 | not stated | 0 |
| `/settings/get/debtors` | 25 | not stated | 0 |
| `/settings/get/postingaccounts` | 1000 | not stated | 0 |
| `/accounts/get`, `/receipts/assigned-transactions/get`, `/transactions/assigned-receipts/get` | no paging | — | — |

Meaning of `rows`: the spec documents `rows` on every list response as **"Number of returned rows"**, i.e. the number of items in this page's `data`, not the total number of matching records. Nothing in the spec supports reading it as a total, so it cannot be used to compute the page count. Page by requesting `offset += limit` until `data` has fewer than `limit` items (compare `data.length`, which works under either reading). Sort orders are only stable where an `order` parameter exists; `/transactions/get` switches to `id_by_customer ASC` when `id_by_customer_from`/`_to` is used, which is the most robust cursor available.

### Formats

| Kind | Format | Notes |
|---|---|---|
| Date | `YYYY-MM-DD` (e.g. `2017-04-26`) | receipts, postings, reports, `date_delivery`, `date_payment_due`, `due_date`. Empty string is never a valid date. |
| Date-time | `YYYY-MM-DD HH:MM:SS` (e.g. `2017-04-26 13:45:00`) | `booking_date`/`value_date` on transactions (spec writes the PHP-style `HH:II:SS`, same thing), `date_since_last_modified` (if only a date is given, time defaults to `23:59:59`). Responses return `booking_date`, `value_date` and posting `date` with a `00:00:00` time part. |
| Amount, decimal point | `123.45`, never a comma, two decimals | responses always return amounts as strings (`"123.99"`) |
| Amount as JSON number (float) | `/receipts/add`, `/receipts/upload`, `/transactions/add`, batch items `Receipt`, `Transaction`, `PostingsFree` | `0.00` is invalid on receipts and transactions |
| Amount as JSON string | `/postings/add/free` `amount` (type string) | |
| Amount arrays | `/postings/add/receipt`, `/postings/add/transaction` `amounts` (item type unspecified; "Amount must be in format 0000.00"); batch items `ReceiptPostings`/`TransactionPostings` `amounts` are `array[number]` | splits must sum to the receipt / transaction amount (errors 37 / 27) |
| Invoice item arrays | strings in the spec's usage examples: `"item_amount": ["10","20"]`, `"item_single_price": ["20","19.99"]`, `"item_vat": ["7","19"]`; `discount_value`, `due_days` are strings | |
| Sign rules | receipts: negative allowed ("reversed payment", e.g. `-12.30`). Transactions: positive = incoming, negative = outgoing. Free postings: **no negative amounts** (error 22), direction is expressed by `postingaccount_debit`/`postingaccount_credit`. | |
| Currency | `EUR` is the only value that is safe everywhere: `/receipts/upload` requires `'EUR' if specified`; batch item enums are `["EUR"]`. `/receipts/add` says "At the moment we accept USD, GBP and CHF", `/transactions/add` lists ~50 ISO codes. Foreign-currency receipts must be re-read via `/receipts/get/id_by_customer` (`amount` is the EUR value, `amount_original` + `currency_original` + `exchangerate` the original) before posting; postings in foreign currency are only allowed on one specific account (errors 34/25/39). | |
| VAT rate on receipts | `vat_rate` number, e.g. `19.00` or `0`; "may also be an empty string" for unknown/mixed rates | |
| Country | German country name (`Dänemark`) or ISO 3166-1 alpha-2 (`DK`) | invoices, creditors, debtors |
| Posting text | max 128 characters | |
| Cost location code | alphanumeric, max 10 characters, or a number > 0 | |
| Comment text | 2–210 characters | |
| Invoice number on receipts | max 60 characters, may be empty string | |

### Identifiers: `id_by_customer`

- Every receipt, transaction, posting and report has an `id_by_customer`: a per-customer counter that matches the number shown in the BB web UI. It is not a global database id and is only meaningful together with the `api_key`.
- Requests take ids as **integers** (`receipt_id_by_customer: 123`); responses return them as **strings** (`"id_by_customer": "123"`). Cast before comparing.
- Master data is addressed differently: creditors, debtors, posting accounts and payment accounts by `postingaccount_number` (integer in most requests, but a **string** on `/settings/add/creditor`, `/settings/add/debtor` and their batch items; always a string in responses); cost locations by `code`.
- `/transactions/get` supports exclusive id bounds `id_by_customer_from` / `id_by_customer_to` (the boundary ids themselves are NOT returned).
- The four `/…/id_by_customer` endpoints (`/receipts/get/id_by_customer`, `/receipts/delete/id_by_customer`, `/receipts/restore/id_by_customer`, `/transactions/get/id_by_customer`) do not declare the id parameter in the spec at all, yet each defines error 5 "invalid id_by_customer specified". Two independent client implementations and the vendor's integration-partner documentation put the id **in the URL path**, replacing the literal `id_by_customer` segment: `POST /receipts/get/123`, `POST /receipts/delete/123`, `POST /receipts/restore/123`, `POST /transactions/get/123` (body: `{"api_key": "<API_KEY>"}` plus `get_file` where applicable). If the server answers with error 5 to that form, retry with the literal path and a body field `id_by_customer` (integer). Neither form is verified against the live API in this reference; `scripts/bb.sh` supports both.

### Domain vocabulary (German UI terms you will meet in messages and the UI)

| API term | German UI term | Meaning |
|---|---|---|
| receipt | **Beleg** | any supporting document: inbound/outbound invoice or credit note |
| `list_direction: inbound` / `outbound` | **Eingangsbelege** / **Ausgangsbelege** | purchase-side / sales-side receipts |
| receipt `type` `invoice inbound` / `invoice outbound` | **Eingangsrechnung** / **Ausgangsrechnung** | supplier invoice / own invoice |
| receipt `type` `credit inbound` / `credit outbound` | **Eingangsgutschrift § 14 UStG** / **Ausgangsgutschrift § 14 UStG** | credit notes in the § 14 UStG sense (self-billing) |
| transaction | **Transaktion**, **Umsatz** | bank / cash / card movement on a payment account |
| account (payment account, "basic account") | **Konto** (Bank, Kasse) | bank, cash or other money account; has a `postingaccount_number` such as 1200 |
| postingaccount | **Buchungskonto**, **Sachkonto** | chart-of-accounts entry (SKR03/SKR04 style numbers) |
| creditor / debtor | **Kreditor** / **Debitor** | supplier / customer sub-ledger account (e.g. 70001 / 10001) |
| posting | **Buchung** | journal entry; "free posting" (**freie Buchung**) = manual debit/credit entry without receipt or transaction |
| confirmed | **bestätigt** | booked; can still be unconfirmed via API |
| fixed | **festgeschrieben** (**Festschreibung**, GoBD) | locked; can only be reversed by a **Stornobuchung** (reversal posting) |
| cost location | **Kostenstelle** | cost centre; `cost_location_two` is the second cost-centre dimension |
| open item posting (OI) | **Offene-Posten-Buchhaltung** | receivables/payables tracked per receipt; drives `oi_receipts_ids_by_customer` |
| BWA | **Betriebswirtschaftliche Auswertung** | management P&L report |
| sums report | **Summen- und Saldenliste** | trial balance |
| ledger | **Kontenblatt** | single-account ledger |
| `date` vs `date_delivery` | **Buchungsdatum** / **Leistungsdatum** | document date vs supply date; `date_delivery` may not be after `date` (DATEV compatibility) |
| `credit_type` `H` (`S`) | **Haben** / **Soll** | credit / debit side |
| `tax_key` | **Steuerschlüssel** | DATEV tax key |
| USt. / VSt. | **Umsatzsteuer** / **Vorsteuer** | output VAT / input VAT |
| §13b | reverse charge (§ 13b UStG) | |
| i.g.E. | **innergemeinschaftlicher Erwerb** | intra-community acquisition |

### VAT codes (`vat` on `/postings/add/free`, `vats[]` on `/postings/add/receipt` and `/postings/add/transaction`, identical list in all three)

| Code | German label (verbatim from the spec) | English gloss |
|---|---|---|
| `0_none` | keine Ust. | no VAT |
| `19_vat` | 19% Ust. | 19 % output VAT (sales) |
| `7_vat` | 7% Ust. | 7 % output VAT |
| `19_pre` | 19% Vst. | 19 % input VAT (purchases) |
| `7_pre` | 7% Vst. | 7 % input VAT |
| `19_both_1` | §13b 19% USt./VSt. | reverse charge, output and input VAT |
| `19_both_506` | §13b 19% USt./VSt. (EU §13b Abs. 1) | reverse charge, EU supplier |
| `19_both_6506` | §13b 19% USt. (EU §13b Abs. 1, ohne VSt.) | reverse charge, EU supplier, no input VAT deduction |
| `19_both_511` | §13b 19% USt./VSt. (Drittland §13b Abs. 2 Nr. 1) | reverse charge, third-country supplier |
| `19_both_6511` | §13b 19% USt. (Drittland §13b Abs. 2 Nr. 1, ohne VSt.) | reverse charge, third country, no input VAT deduction |
| `19_both_6501` | §13b 19/16% USt. (ohne VSt.) | reverse charge, no input VAT deduction |
| `19_both_2` | I.g.E. 19% USt./VSt. | intra-community acquisition 19 % |
| `7_both` | I.g.E. 7% USt./VSt. | intra-community acquisition 7 % |
| `19_both_1_no_pre` | §13b 19/16% USt. | reverse charge, output VAT only |
| `19_both_2_no_pre` | i.g.E. 19/16% USt. | intra-community acquisition, output VAT only |
| `7_both_no_pre` | i.g.E. 7/5% USt. | intra-community acquisition 7 %, output VAT only |
| `19_pre_app` | 19/16% Aufz. VSt. | input VAT, "Aufz." variant (abbreviation not expanded in the spec) |
| `7_pre_app` | 7/5% Aufz. VSt. | input VAT 7 %, "Aufz." variant |
| `19_both_app_1` | §13b 19/16% USt./Aufz. VSt. | reverse charge, "Aufz." variant |
| `19_both_app_506` | §13b 19/16% USt./Aufz. VSt. (EU §13b Abs. 1) | reverse charge EU, "Aufz." variant |
| `19_both_app_511` | §13b 19/16% USt./Aufz. VSt. (Drittland §13b Abs. 2 Nr. 1) | reverse charge third country, "Aufz." variant |
| `19_both_app_2` | i.g.E. 19/16% USt./Aufz. VSt. | intra-community acquisition, "Aufz." variant |
| `7_both_app` | i.g.E. 7/5% USt./Aufz. VSt. | intra-community acquisition 7 %, "Aufz." variant |

Notes: labels with `19/16%` and `7/5%` cover the temporary German rate cut of July–December 2020; the rate actually applied depends on the posting date, and a code that does not exist for that date fails with "the vat option is not available for this date" (`/postings/add/receipt` code 42). Which codes an account accepts depends on the account's settings ("must be posted with vat option …", "vat option unavailable due to current settings", "vat option unavailable with 'not liable to sales tax' setting" for **Kleinunternehmer**). Rule of thumb: expense accounts take `*_pre`, revenue accounts take `*_vat`, neutral accounts take `0_none`.

### Posting lifecycle and the write verbs

```
(none) --add--> confirmed (bestätigt) --UI/export--> fixed (festgeschrieben)
   ^                 |                                   |
   |          unconfirm/* (API)                     cancel (API)
   +-----------------+                        creates Stornobuchung
        cancel (API) deletes outright         (both entries stay visible)
```

- `/postings/add/*` create confirmed postings. Fixing (**Festschreibung**) is not available via API.
- `/postings/unconfirm/{receipt,transaction,free}` removes the postings of one receipt / transaction / one free posting by un-confirming them; works only while not fixed. The receipt or transaction itself stays.
- `/postings/cancel` on an unfixed posting deletes it; on a fixed posting it books a reversal posting (**Stornobuchung**). Either way the original cannot be "un-cancelled" via API.
- Receipt delete is soft (`deleted: "1"`, restorable via `/receipts/restore/id_by_customer`); cost-location delete is hard; there is no delete at all for transactions, creditors, debtors, posting accounts, payment accounts, comments and invoices.

### Safety table — every endpoint by effect

Categories: read (no change) · create (new records, not idempotent — a repeat creates duplicates) · update (in place, idempotent for the same payload) · link (create/remove an assignment, reversible) · revert (undo a state change, reversible) · delete (destructive; confirm with the user first).

| Endpoint | Category | Reversible? | Idempotent? | Note |
|---|---|---|---|---|
| `/accounts/get` | read | — | yes | |
| `/cost-locations/get` | read | — | yes | |
| `/postings/get` | read | — | yes | date range required |
| `/receipts/get` | read | — | yes | `list_direction` required |
| `/receipts/get/id_by_customer` | read | — | yes | can return the file (base64) |
| `/receipts/assigned-transactions/get` | read | — | yes | |
| `/transactions/get` | read | — | yes | |
| `/transactions/get/id_by_customer` | read | — | yes | |
| `/transactions/assigned-receipts/get` | read | — | yes | |
| `/settings/get/creditors` | read | — | yes | default limit 25 |
| `/settings/get/debtors` | read | — | yes | default limit 25 |
| `/settings/get/postingaccounts` | read | — | yes | |
| `/reports/get/bwa` | read | — | yes | fails with code 8 until generation finished |
| `/reports/get/sums` | read | — | yes | fails with code 8 until generation finished |
| `/reports/get/sums/ledger` | read | — | yes | computed on the fly, may be slow |
| `/accounts/add` | create | no (no delete/update for accounts) | no | duplicate names rejected (code 9) |
| `/comments/add` | create | no (no delete for comments) | no | |
| `/cost-locations/add` | create | via `/cost-locations/delete` | no | |
| `/invoices/create` | create | no (no cancel via API) | no | issues a numbered invoice and a receipt |
| `/invoices/create/draft` | create | no via API (drafts live in the UI) | no | not booked, no number |
| `/invoices/create/e-invoice` | create | no | no | XRechnung / ZUGFeRD |
| `/postings/add/free` | create | `/postings/unconfirm/free` while unfixed, else `/postings/cancel` | no | returns no id |
| `/postings/add/receipt` | create | `/postings/unconfirm/receipt` while unfixed | no | returns no id |
| `/postings/add/transaction` | create | `/postings/unconfirm/transaction` while unfixed | no | returns no id |
| `/postings/add-batch/free` | create | per posting as above | no | partial success possible |
| `/postings/add-batch/receipts` | create | per receipt as above | no | partial success possible |
| `/postings/add-batch/transactions` | create | per transaction as above | no | partial success possible |
| `/receipts/add` | create | soft-delete via `/receipts/delete/id_by_customer` | no | receipt without file |
| `/receipts/addBatch` | create | soft-delete per receipt | no | max 50, one call per 5 s |
| `/receipts/upload` | create | soft-delete | no | max 10/min, OCR runs |
| `/settings/add/creditor` | create | no (no delete for creditors) | no | |
| `/settings/add/debtor` | create | no (no delete for debtors) | no | |
| `/settings/add/postingaccount` | create | no (no delete for posting accounts) | no | |
| `/settings/add-batch/creditors` | create | no | no | partial success possible |
| `/settings/add-batch/debtors` | create | no | no | partial success possible |
| `/transactions/add` | create | no (no delete/update for transactions) | no | no duplicate detection |
| `/transactions/addBatch` | create | no | no | max 50, one call per 5 s |
| `/reports/create/bwa` | create | n/a (report replaces the previous BWA) | no | async; code 12 while one is running |
| `/reports/create/sums` | create | n/a (replaces previous sums report) | no | async; code 12 while one is running |
| `/cost-locations/update` | update | re-update | yes | name only |
| `/settings/update/creditor` | update | re-update | yes | overwrites the fields sent |
| `/settings/update/debtor` | update | re-update | yes | overwrites the fields sent |
| `/settings/update/postingaccount` | update | re-update | yes | name only |
| `/postings/assign/receipt-to-free-posting` | link | no unassign endpoint for free postings | repeat likely fails (code 10) | |
| `/transactions/assign/receipt` | link | `/transactions/unassign/receipt` | repeat behaviour unspecified | does not post anything |
| `/transactions/assign-batch/receipt` | link | `/transactions/unassign/receipt` per pair | as above | max 50 pairs |
| `/transactions/unassign/receipt` | link | re-assign | second call → code 23 "no receipts assigned" | blocked by a confirmed posting (code 10) |
| `/postings/unconfirm/free` | revert | re-add the posting | second call → code 6/7 | unfixed only |
| `/postings/unconfirm/receipt` | revert | re-add | second call → code 7 | unfixed only |
| `/postings/unconfirm/transaction` | revert | re-add | second call → code 7 | unfixed only |
| `/receipts/restore/id_by_customer` | revert | `/receipts/delete/id_by_customer` | second call → code 7 | |
| `/cost-locations/delete` | delete | **no** | second call → code 6 | permanent |
| `/receipts/delete/id_by_customer` | delete | yes, `/receipts/restore/id_by_customer` | second call → code 7 | soft delete; refused if fixed/confirmed postings exist (8/9) |
| `/postings/cancel` | delete | **no** | second call → code 8/9 | unfixed → deleted, fixed → reversal posting |

## Receipts

Receipts (**Belege**) are the documents. Two ways in: `/receipts/upload` (with file, OCR runs) and `/receipts/add` / `/receipts/addBatch` (metadata only, no file). Receipts get linked to bank transactions (`/transactions/assign/receipt`) or posted directly against a creditor/debtor (`/postings/add/receipt`).

### POST /receipts/get

Purpose: list receipts of one direction with filters; response contains `rows` and an array of receipts. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | customer selector |
| `list_direction` | yes | string | `inbound` (**Eingangsbelege**), `outbound` (**Ausgangsbelege**) | |
| `payment_status` | no | string | `paid` (**bezahlt**), `unpaid` (**unbezahlt**) | validated if given |
| `counterparty` | no | string | free text | invoicing party (inbound) or recipient (outbound) |
| `date_from` | no | string | `YYYY-MM-DD` | issuing date ≥ value; empty string invalid |
| `date_to` | no | string | `YYYY-MM-DD` | issuing date ≤ value |
| `limit` | no | integer | default 500, max 500 | |
| `offset` | no | integer | default 0 | |
| `order` | no | object | keys: `date`, `amount`, `invoicenumber`, `invoicingparty`; values `ASC` or `DESC` | e.g. `{"date": "ASC", "amount": "DESC"}`. The spec's schema literally declares one property named `field`; the examples show the real shape. |
| `include_offers` | no | boolean | default false | include offers (**Angebote**; presumably those created via `/invoices/create` type `offer`) |
| `deleted` | no | boolean | default false | if true, **only** soft-deleted receipts are returned |
| `invoicenumber` | no | string | | exact invoice number filter |
| `due_date` | no | string | `YYYY-MM-DD` | receipts with exactly this due date |
| `date_since_last_modified` | no | string | `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD` (→ 23:59:59) | `date_updated` later than value; use for incremental sync |

Response `data[]` (all strings): `filename`, `id_by_customer`, `type` (e.g. `invoice inbound`), `date`, `date_delivery`, `date_uploaded`, `counterparty`, `invoicenumber`, `amount`, `payment_date`, `due_date`, `account`, `link_to_receipt_id_by_customer`, `deleted` (`"0"`/`"1"`). Plus `rows`.

Errors worth knowing: 5 invalid list_direction · 6 invalid payment_status · 7/8 invalid date_from/date_to · 9 invalid counterparty · 10 invalid limit · 12 invalid offset · 13 invalid include_offers · 14 invalid deleted · 15 invalid sort field · 16 invalid sort value · 17 invalid invoicenumber · 18 invalid due_date · 19 invalid date_since_last_modified.

Cross-refs: single receipt with file → `/receipts/get/id_by_customer`; payments linked to a receipt → `/receipts/assigned-transactions/get`.

### POST /receipts/get/id_by_customer

Purpose: fetch one receipt by `id_by_customer`, optionally with the file as base64. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `id_by_customer` | yes | integer | **URL path segment**: `POST /receipts/get/123` (fallback: body field `id_by_customer`) | **not declared in the spec's parameter list**; implied by the path placeholder, the description ("by id_by_customer") and error 5 "invalid id_by_customer specified"; see Conventions → Identifiers |
| `get_file` | no | boolean | default false | include `file_content` (base64). `e_invoice_type` 0 → standard PDF, 1 → ZUGFeRD PDF, 2 → XRechnung XML |

Response `data` (object, strings): `filename`, `id_by_customer`, `date`, `counterparty`, `invoicenumber`, `amount` (EUR value), `amount_original`, `currency` (`EUR`), `currency_original`, `exchangerate`, `vat`, `payment_date`, `account`, `type`, `e_invoice_type` (`"0"`/`"1"`/`"2"`), `list_direction`, `payment_reference`, `file_content` (base64, only with `get_file`), `file_type` (`pdf`/`xml`), `date_delivery`, `date_payment_due`, `link_to_receipt_id_by_customer`, `deleted`.

Errors: 5 invalid id_by_customer · 6 invalid get_file. (No explicit "not found" code is listed; expect 5.)

Cross-refs: required before `/postings/add/receipt` on a foreign-currency receipt (use the calculated `amount`).

### POST /receipts/add

Purpose: create a receipt **without a file** (metadata only). Safety: create, not idempotent.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `type` | yes | string | `invoice inbound`, `invoice outbound`, `credit inbound`, `credit outbound` | see vocabulary table |
| `counterparty` | yes | string | non-empty | |
| `invoice_number` | yes | string | max 60 chars, may be `""` | |
| `date` | yes | string | `YYYY-MM-DD` | issuing date |
| `amount` | yes | number (float) | ≠ 0.00; negative = reversed payment | |
| `currency` | yes | string | spec text: "At the moment we accept USD, GBP and CHF"; `EUR` is what every other endpoint expects | non-empty |
| `vat_rate` | no | number (float) | e.g. `19.00`, `0`; empty string for unknown/multiple rates | |
| `account` | no | integer | posting account number of a payment account, e.g. `1200`; `0` invalid | must exist as payment account |
| `creditor_debtor` | no | integer | creditor number for `invoice inbound`, debtor number for `invoice outbound`, e.g. `70001`; `0` invalid | creditors/debtors must be activated and compatible with `type` |
| `payment_reference` | no | string | | auto-match with a transaction carrying the same reference |
| `date_delivery` | no | string | `YYYY-MM-DD`, not after `date` | DATEV rule |
| `date_payment_due` | no | string | `YYYY-MM-DD` | |
| `link_to_receipt_id_by_customer` | no | integer | valid id of another receipt | both receipts get assigned together when one is assigned manually |

Response: `id_by_customer` (string).

Errors: 8 invalid receipt type · 9 invalid account · 10 account does not exist · 17 invalid counterparty · 18 invalid invoice number · 19 invalid date · 20 invalid amount · 21 invalid currency · 22 invalid vat rate · 24 invalid creditor/debtor · 25 creditor/debtor does not exist · 26 receipt type cannot be assigned to a creditor account · 27 creditors not activated · 28 type cannot be assigned to a debtor account · 29 debtors not activated · 34 invalid payment reference · 35 invalid date delivery · 36 invalid date_payment_due · 37 invalid link_to_receipt_id_by_customer.

Cross-refs: with a file use `/receipts/upload`; many at once `/receipts/addBatch`.

### POST /receipts/addBatch

Purpose: create up to 50 receipts (no files) in one call; one request every 5 seconds. Safety: create, not idempotent, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipts` | yes | array of `Receipt` | max 50 items | same fields and error messages as `/receipts/add` |

`Receipt` item (definition `Receipt`; required: `type`, `counterparty`, `invoice_number`, `date`, `amount`, `currency`):

| Field | Required | Type | Notes |
|---|---|---|---|
| `type` | yes | string | `invoice inbound` / `invoice outbound` / `credit inbound` / `credit outbound` |
| `counterparty` | yes | string | |
| `invoice_number` | yes | string | max 60, may be `""` |
| `date` | yes | string | `YYYY-MM-DD` |
| `amount` | yes | number (float) | negative allowed |
| `currency` | yes | string | schema enum `["EUR"]`; the description lists ~50 ISO codes — send `EUR` |
| `vat_rate` | no | number (float) | |
| `account` | no | integer | payment account number |
| `creditor_debtor` | no | integer | creditor / debtor number |
| `payment_reference` | no | string | |
| `date_delivery` | no | string | `YYYY-MM-DD`, not after `date` |
| `date_payment_due` | no | string | `YYYY-MM-DD` |
| `link_to_receipt_id_by_customer` | no | integer | |

Response: `success`, `receipts[]` of `{success: true, message, id_by_customer}`, `errors[]` of `{success: false, error_code, message, request_data}`. Item error codes follow `/receipts/add`.

Batch-level errors: 5 Number of receipts exceeded (limit 50) · 6 No receipts found · 403/15 adding temporarily restricted.

### POST /receipts/upload

Purpose: upload a receipt file; BB runs document recognition (OCR) and returns the stored filename and the new id. Max 10 requests per minute. Safety: create, not idempotent (same file twice → two receipts).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `file` | yes | string / file | real file upload or base64 string. MIME: `application/pdf`, `text/xml`, `application/xml`, `image/jpeg`, `image/png`, `image/bmp`, `image/tiff` | size and page limits apply (errors 7, 14; values not stated) |
| `type` | yes | string | `invoice inbound`, `invoice outbound`, `credit inbound`, `credit outbound` | |
| `file_name` | no (required for base64) | string | | ignored for real uploads |
| `account` | no | integer | payment account number; `0` invalid | |
| `creditor_debtor` | no | integer | creditor (inbound) / debtor (outbound) number | |
| `counterparty` | no | string | non-empty | ignored for e-invoices (XML/ZUGFeRD carry their own data) |
| `invoice_number` | no | string | max 60 | ignored for e-invoices |
| `date` | no | string | `YYYY-MM-DD` | ignored for e-invoices |
| `amount` | no | number (float) | ≠ 0.00, negative allowed | ignored for e-invoices |
| `currency` | no | string | must be `EUR` if given | ignored for e-invoices |
| `vat_rate` | no | number (float) | | ignored for e-invoices |
| `payment_reference` | no | string | Amazon order id, PayPal transaction id, Stripe transaction id | ignored for e-invoices |
| `date_delivery` | no | string | `YYYY-MM-DD`, not after `date` | ignored for e-invoices |
| `date_payment_due` | no | string | `YYYY-MM-DD` | ignored for e-invoices |
| `link_to_receipt_id_by_customer` | no | integer | | |

Optional metadata you pass pre-fills the receipt; OCR fills the rest. Fields you omit may be recognised wrongly — read the receipt back with `/receipts/get/id_by_customer` before posting.

Response: `id_by_customer` (string), `filename` (internal filename without extension).

Errors: 5 no file provided · 6 file type not accepted · 7 maximum file size exceeded · 14 maximum pages exceeded · 33 file name is not specified (base64 without `file_name`) · 422/31 receipt not processable · 422/32 receipt ocr processing failed · 403/12 upload limit reached · 403/15 upload temporarily restricted · plus the `/receipts/add` validation codes 8–10, 17–22, 24–29, 34–37.

Cross-refs: link to the paying transaction with `/transactions/assign/receipt`; post directly with `/postings/add/receipt`.

### POST /receipts/delete/id_by_customer

Purpose: mark a receipt as deleted (soft delete). Safety: delete, reversible via restore.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `id_by_customer` | yes | integer | **URL path segment**: `POST /receipts/delete/123` (fallback: body field) | not declared in the spec; implied by error 5 "invalid id_by_customer specified"; see Conventions → Identifiers |

Response: `id_by_customer`.

Errors: 5 invalid id_by_customer · 6 no receipt found · 7 receipt is already deleted · 8 receipt can't be marked as deleted – fixed postings exist · 9 receipt is directly assigned to confirmed postings (unconfirm first with `/postings/unconfirm/receipt`).

Deleted receipts are listed with `/receipts/get` `deleted: true`.

### POST /receipts/restore/id_by_customer

Purpose: undo a soft delete. Safety: revert.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `id_by_customer` | yes | integer | **URL path segment**: `POST /receipts/restore/123` (fallback: body field) | not declared in the spec; implied by error 5; see Conventions → Identifiers |

Response: `id_by_customer`.

Errors: 5 invalid id_by_customer · 6 no receipt found · 7 receipt is not marked as deleted · 8 restoration of receipt failed.

### POST /receipts/assigned-transactions/get

Purpose: list the transactions linked to one receipt (was the invoice paid?). Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipt_id_by_customer` | yes | integer | | |
| `confirmed_only` | no | boolean | default false | only assignments that are part of confirmed postings |

Response: `rows`, `data[]` of `{id_by_customer, to_from, amount, booking_date, value_date, purpose}` (strings).

Errors: 5 invalid receipt_id_by_customer · 6 no receipt found · 7 invalid confirmed_only.

Cross-refs: opposite direction `/transactions/assigned-receipts/get`.

## Transactions

Transactions are movements on payment accounts (**Konten**: bank, cash, card). Bank-connected accounts fill automatically; `/transactions/add` and `/transactions/addBatch` import the rest (cash book, CSV). Transactions are posted with `/postings/add/transaction`.

### POST /transactions/get

Purpose: list transactions by account, date, counterparty or id range. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `id_by_customer_from` | no | integer | exclusive lower bound | switches sort to `id_by_customer ASC`, even with date params |
| `id_by_customer_to` | no | integer | exclusive upper bound | same sort effect |
| `date_from` | no | string | `YYYY-MM-DD` | booking date ≥ |
| `date_to` | no | string | `YYYY-MM-DD` | booking date ≤ |
| `date_since_last_modified` | no | string | `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD` (→ 23:59:59) | `date_updated` later than value |
| `account` | no | integer | payment account number, e.g. `1200` | |
| `to_from` | no | string | payer/payee | |
| `limit` | no | integer | default 500, max 500 | |
| `offset` | no | integer | default 0 | |

Response: `rows`, `data[]` of `{id_by_customer, to_from, amount, booking_date ("YYYY-MM-DD 00:00:00"), value_date, purpose}` (strings). Note the list omits `account`, `currency`, bank fields and `type`; fetch them per id.

Errors: 5/6 invalid date_from/date_to · 7 invalid account · 8 invalid to_from · 9 invalid limit · 10 invalid offset · 12/13 invalid id_by_customer_from/_to · 14 invalid date_since_last_modified.

### POST /transactions/get/id_by_customer

Purpose: one transaction with full detail. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `id_by_customer` | yes | integer | **URL path segment**: `POST /transactions/get/123` (fallback: body field) | not declared in the spec; implied by the description and error 5; see Conventions → Identifiers |

Response `data` (object): `id_by_customer`, `account` (declared integer, example `"1200"`), `to_from`, `booking_date`, `value_date`, `amount`, `currency`, `account_number` (IBAN), `bank_code` (BIC), `bank_name`, `purpose`, `type`, `booking_text`.

Errors: 5 invalid id_by_customer · 6 transaction not found.

### POST /transactions/add

Purpose: add one transaction to a payment account. Safety: create, not idempotent, no duplicate detection; no update/delete afterwards.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `account` | yes | integer | posting account number of an existing payment account, e.g. `1200` | |
| `to_from` | yes | string | payer / payee | |
| `amount` | yes | number (float) | positive incoming, negative outgoing, ≠ 0.00 | in the account's currency |
| `booking_date` | yes | string | `YYYY-MM-DD HH:MM:SS` (spec: `HH:II:SS`), e.g. `2017-04-26 00:00:00` | |
| `value_date` | no | string | same format | defaults to `booking_date`; empty string invalid |
| `account_number` | no | string | IBAN or account number of counterparty | non-empty if given |
| `bank_code` | no | string | BIC or bank code | non-empty if given |
| `bank_name` | no | string | | non-empty if given |
| `purpose` | no | string | may be `""` | |
| `type` | no | string | e.g. `Direct debit` | non-empty if given |
| `booking_text` | no | string | may be `""` | |
| `payment_reference` | no | string | | auto-match with a receipt carrying the same reference |
| `currency` | no | string | AED, AUD, BGN, BRL, CAD, CHF, CNY, COP, CYP, CZK, DKK, EUR, GBP, HKD, HRK, HUF, IDR, ILS, INR, ISK, JPY, KRW, LTL, LVL, MTL, MXN, MYR, NOK, NZD, PEN, PHP, PLN, QAR, ROL, RON, RUB, SEK, SGD, SIT, SKK, THB, TRL, TRY, UAH, USD, VND, ZAR | non-empty if given |

Response: `id_by_customer`.

Errors: 5 no account · 6 invalid account · 7 account does not exist · 8 no to_from · 9 invalid to_from · 10 no amount · 13 invalid amount · 14 no booking date · 16 invalid booking date · 17 invalid value date · 18 invalid account number · 19 invalid bank code · 20 invalid bank name · 21 invalid purpose · 22 invalid type · 23 (spec response key 24) invalid booking text specified — the body carries `error_code` 23, colliding with the generic empty-body code; disambiguate via `message` (see quirk 13) · 25 invalid payment reference · 26 invalid currency · 403/15 adding temporarily restricted.

Cross-refs: check `/transactions/get` for the date range first to avoid re-importing a statement; payment accounts come from `/accounts/get` / `/accounts/add`.

### POST /transactions/addBatch

Purpose: add up to 50 transactions; one request every 5 seconds. Safety: create, not idempotent, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transactions` | yes | array of `Transaction` | max 50 | same fields/errors as `/transactions/add` |

`Transaction` item (definition `Transaction`; required: `account`, `to_from`, `amount`, `booking_date`):

| Field | Required | Type | Notes |
|---|---|---|---|
| `account` | yes | integer | payment account number |
| `to_from` | yes | string | |
| `amount` | yes | number (float) | sign = direction |
| `booking_date` | yes | string | `YYYY-MM-DD HH:MM:SS` |
| `value_date` | no | string | defaults to booking_date |
| `account_number` | no | string | IBAN |
| `bank_code` | no | string | BIC |
| `bank_name` | no | string | |
| `purpose` | no | string | |
| `type` | no | string | |
| `booking_text` | no | string | |
| `payment_reference` | no | string | |
| `currency` | no | string | schema enum `["EUR"]` (description lists ~50 codes) |

Response: `success`, `transactions[]` of `{success, message, id_by_customer}`, `errors[]` of `{success: false, error_code, message, request_data}`.

Batch-level errors: 5 Number of transactions exceeded (limit 50) · 403/15 adding temporarily restricted.

### POST /transactions/assign/receipt

Purpose: link one receipt to one transaction (**Beleg zuordnen**). Creates the link only; nothing is booked. Safety: link, reversible with `/transactions/unassign/receipt`.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transaction_id_by_customer` | yes | integer | | |
| `receipt_id_by_customer` | yes | integer | | |

Response: `success`, `message`.

Errors: 5 invalid assignment type · 6 no transaction_id_by_customer · 7 no receipt_id_by_customer (the spec wires this response to the free-posting definition, so the returned message may read "posting not found" — see quirk 23) · 8 transaction not found · 9 receipt not found.

Cross-refs: a receipt with `link_to_receipt_id_by_customer` drags its partner along; post the transaction afterwards with `/postings/add/transaction`; for a receipt ↔ free posting link use `/postings/assign/receipt-to-free-posting`.

### POST /transactions/assign-batch/receipt

Purpose: link up to 50 receipt/transaction pairs. Safety: link, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transactions_to_receipts` | yes | array of `TransactionToReceipt` | max 50 | |

`TransactionToReceipt` item (required: both): `receipt_id_by_customer` (integer), `transaction_id_by_customer` (integer).

Response: `success`, `transactions_to_receipts[]` of `{success, message, transaction_id_by_customer, receipt_id_by_customer}`, `errors[]` of `{success: false, error_code, message, request_data}`.

Batch-level errors: 10 Number of transactions to receipts exceeded · 12 No transactions to receipts found · 403/15 adding temporarily restricted.

### POST /transactions/unassign/receipt

Purpose: remove the link between one receipt and one transaction; neither record is deleted. Safety: link (undo).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transaction_id_by_customer` | yes | integer | | |
| `receipt_id_by_customer` | yes | integer | receipt to unassign | |

Response: `success`, `message`.

Errors: 6 no or invalid transaction_id_by_customer · 7 no or invalid receipt_id_by_customer · 8 transaction not found · 9 receipt not found · 10 receipt could not be removed because of a confirmed posting (run `/postings/unconfirm/transaction` first) · 23 no receipts assigned to transaction (here code 23 is **not** the generic empty-body error).

### POST /transactions/assigned-receipts/get

Purpose: list receipts linked to one transaction. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transaction_id_by_customer` | yes | integer | | |
| `confirmed_only` | no | boolean | default false | |

Response: `rows`, `data[]` of `{id_by_customer, filename}`.

Errors: 5 invalid transaction_id_by_customer · 6 no transaction found · 7 invalid confirmed_only.

## Invoices

Outgoing documents BB renders itself (**Rechnung**, **Gutschrift**, **Angebot**). `/invoices/create` books a final invoice and creates the matching outbound receipt; `/invoices/create/draft` leaves an editable draft in the UI; `/invoices/create/e-invoice` produces XRechnung / ZUGFeRD. There is no endpoint to list, read, edit, send, cancel or release invoices; the resulting receipt is visible through `/receipts/get` with `list_direction: outbound` (offers only with `include_offers: true`).

Item fields are **positional parallel arrays**: index i of `item_name`, `item_amount`, `item_unit`, `item_vat` (or `item_tax_type`/`item_tax_amount`), `item_single_price`, `item_description` describes line i; all must have the same length.

### POST /invoices/create

Purpose: create and book a final invoice, credit note or offer; returns number and file name. Safety: create, not idempotent (a second call issues a second numbered document).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `type` | yes | string | `invoice` (**Rechnung**), `credit` (**Gutschrift**), `offer` (**Angebot**) | |
| `show_prices_type` | yes | string | `net` (**Netto**), `gross` (**Brutto**) | are `item_single_price` values net or gross |
| `company_name` | yes | string | recipient company | |
| `date` | yes | string | format not stated in the spec; use `YYYY-MM-DD` | invoice date |
| `item_name` | yes | array | e.g. `["Item 1", "Item 2"]` | |
| `item_amount` | yes | array | quantities, e.g. `["10", "20"]` | |
| `item_unit` | yes | array | e.g. `["Std.", "Stk."]` | |
| `item_vat` | yes | array | rates 0–100, e.g. `["7", "19"]` | |
| `item_single_price` | yes | array | e.g. `["20", "19.99"]` | |
| `contact_person_name` | no | string | | |
| `street` | no | string | | |
| `additional_addressline` | no | string | | note spelling: no underscore between address and line (creditors/debtors use `additional_address_line`) |
| `zip` | no | string | | |
| `city` | no | string | | |
| `country` | no | string | German name (`Dänemark`) or ISO-2 (`DK`) | |
| `email` | no | string | recipient email for sending | |
| `recurring_interval` | no | string | `weekly`, `monthly`, `quarterly`, `yearly` | |
| `recurring_date_next` | no | string | required if `recurring_interval` set; format not stated | |
| `date_of_supply` | no | string | date or period text | printed on the PDF; if both `date` and `date_of_supply` are `YYYY-MM-DD`, it becomes the receipt's `date_delivery`; a value after the invoice date is silently ignored (DATEV) |
| `invoicenumber` | no | string | | default: next BB number |
| `correspondence` | no | string | cover text | |
| `discount_type` | no | string | `percent`, `EUR` | |
| `discount_value` | no | string | | |
| `payment_conditions` | no | string | | |
| `due_days` | no | string | days between invoice date and due date | |
| `final_provisions` | no | string | closing remark | |
| `show_bankdata` | no | boolean | default false | |
| `show_contactdata` | no | boolean | default false | |
| `item_description` | no | array | per-item descriptions | |
| `customer_number` | no | string | | |
| `payment_reference` | no | string | Amazon order id, PayPal or Stripe transaction id | matches the resulting receipt with the transaction |
| `language` | no | string | `de_DE` (default), `en_US` | labels on the PDF |

Response: `id_by_customer` (undescribed in the spec; presumably the resulting outbound receipt), `invoicenumber`, `file_name`.

Errors: 5 invalid type · 6 no items · 7 invalid show_prices_type · 8/9 invalid recurring_interval/recurring_date_next · 10/12 invalid show_bankdata/show_contactdata · 13 invalid company_name · 14 contact_person_name · 16 street · 17 additional_addressline · 18 zip · 19 city · 20 country · 21 invalid date · 22 invalid invoicenumber · 24 date_of_supply · 25 email · 26 correspondence · 27 discount_value · 28 discount_type · 29 payment_conditions · 31 final_provisions · 32 item_name · 34 item_amount · 35 item_unit · 38 customer_number · 39 item_vat · 43 due_days · 44 language · 403/33 upload limit reached.

Cross-refs: debtor master data → `/settings/add/debtor`; the created receipt can be linked to a payment with `/transactions/assign/receipt`.

### POST /invoices/create/draft

Purpose: create an invoice draft (**Entwurf**) for review and release in the web app; not booked, no invoice number. Safety: create; drafts cannot be listed, edited or released via API.

Parameters are those of `/invoices/create` **without** `invoicenumber`, `due_days` and `payment_reference`:

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `type` | yes | string | `invoice`, `credit`, `offer` | |
| `show_prices_type` | yes | string | `net`, `gross` | |
| `company_name` | yes | string | | |
| `date` | yes | string | | |
| `item_name` | yes | array | | |
| `item_amount` | yes | array | | |
| `item_unit` | yes | array | | |
| `item_vat` | yes | array | 0–100 | |
| `item_single_price` | yes | array | | |
| `contact_person_name`, `street`, `additional_addressline`, `zip`, `city`, `country`, `email` | no | string | as in `/invoices/create` | |
| `recurring_interval`, `recurring_date_next` | no | string | as above | |
| `date_of_supply` | no | string | as above | |
| `correspondence`, `discount_type`, `discount_value`, `payment_conditions`, `final_provisions` | no | string | as above | |
| `show_bankdata`, `show_contactdata` | no | boolean | default false | |
| `item_description` | no | array | | |
| `customer_number` | no | string | | |
| `language` | no | string | `de_DE`, `en_US` | |

Response: `success`, `message` only (no id, no number).

Errors: same numbering as `/invoices/create` minus 22, 32, 34, 35, 39, 43, 33.

### POST /invoices/create/e-invoice

Purpose: create and book a structured electronic invoice (XRechnung / ZUGFeRD) for recipients that require one (e.g. German public-sector buyers). Safety: create, not idempotent.

Differences to `/invoices/create`: address fields and `email` are **required**, `item_vat` is replaced by `item_tax_type` + `item_tax_amount`, `e_invoice_id` is required.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `type` | yes | string | `invoice`, `credit`, `offer` | |
| `show_prices_type` | yes | string | `net`, `gross` | |
| `company_name` | yes | string | | |
| `date` | yes | string | | |
| `item_name` | yes | array | | |
| `item_amount` | yes | array | | |
| `item_unit` | yes | array | | |
| `item_tax_type` | yes | array | `S` VAT standard rate · `Z` 0 % VAT · `AE` reverse charge (§13b) · `K` EU intra-community supply · `G` third-country export · `E` VAT-exempt supply | one per item |
| `item_tax_amount` | yes | array | rates 0–100 | only meaningful where `item_tax_type` is `S`; still send an array of the same length |
| `item_single_price` | yes | array | | |
| `e_invoice_id` | yes | string | buyer reference (**Leitweg-ID** for German authorities); `"0"` if none | |
| `contact_person_name` | no | string | | |
| `street` | yes | string | | |
| `additional_addressline` | no | string | | |
| `zip` | yes | string | | |
| `city` | yes | string | | |
| `country` | yes | string | German name or ISO-2 | |
| `email` | yes | string | | |
| `recurring_interval`, `recurring_date_next` | no | string | as in `/invoices/create` | |
| `date_of_supply` | no | string | as above | |
| `invoicenumber` | no | string | | |
| `correspondence`, `discount_type`, `discount_value`, `payment_conditions` | no | string | | |
| `due_days` | no | string | default `"0"` (due = invoice date) | |
| `final_provisions` | no | string | | |
| `show_bankdata`, `show_contactdata` | no | boolean | default false | |
| `item_description` | no | array | | |
| `customer_number` | no | string | | |
| `payment_reference` | no | string | | |
| `language` | no | string | `de_DE`, `en_US` | |

Response: `id_by_customer`, `invoicenumber`, `file_name`.

Errors: as `/invoices/create`, but 39 invalid item_tax_type (replaces item_vat) · 40 invalid item_tax_amount · 42 invalid e_invoice_id (spec response key 41, but the body `error_code` is 42) or invalid e_invoice_type (no such parameter exists — see quirk 11) — disambiguate via `message` · 403/33 upload limit.

## Postings

Postings (**Buchungen**) are journal entries. Three flavours: receipt postings (receipt → expense/revenue account, requires creditor/debtor posting to be activated in the customer's settings), transaction postings (bank movement → accounts, optionally per open item), free postings (manual debit/credit pair). Split lines are **positional parallel arrays**: index i of `postingaccounts`, `postingtexts`, `vats`, `amounts`, `cost_locations`, `cost_locations_two`, `oi_receipts_ids_by_customer` describes split line i, all arrays must have the same length, and `amounts` must sum to the receipt / transaction amount. None of the add endpoints returns the created posting id; re-read with `/postings/get`.

### POST /postings/get

Purpose: read the journal for a date range (required), filtered by account, posting account, status, cost location. Each request is limited to 1000 postings. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `date_from` | yes | string | `YYYY-MM-DD` | posting date ≥ |
| `date_to` | yes | string | `YYYY-MM-DD` | posting date ≤ |
| `date_last_action_from` | no | string | `YYYY-MM-DD` | created or status-changed (confirmed, fixed) on/after |
| `date_last_action_to` | no | string | `YYYY-MM-DD` | created or status-changed on/before |
| `account` | no | string | comma-separated: `all` (default), `all financial accounts`, `free booking`, or account numbers | e.g. `"1200,1000"` or `"free booking"` |
| `postingaccount` | no | string | comma-separated: `all` (default), `all postingaccounts`, `all debtors`, `all creditors`, or numbers | |
| `posting_status` | no | string | `all` (default), `fixed`, `unfixed` | |
| `cost_location` | no | string | one cost location code | |
| `order` | no | string | `default`, `date ASC`, `date DESC`, `date_last_action ASC`, `date_last_action DESC`, `id_by_customer ASC`, `id_by_customer DESC` | case-sensitive; default = date ASC, then date_last_action |
| `limit` | no | integer | max 1000 | |
| `offset` | no | integer | | |

Response: `rows`, `data[]` (strings): `id_by_customer`, `date` (`YYYY-MM-DD 00:00:00`), `date_delivery`, `date_vat_effective`, `postingtext`, `amount`, `currency`, `vat` (rate, e.g. `19.00`), `credit_type` (`H`), `debit_postingaccount_number`, `credit_postingaccount_number`, `tax_key`, `booking_number`, `cost_location`, `cost_location_two`, `circumstances_ll` (undocumented), `transaction_amount`, `transaction_purpose`, `receipts_assigned_ids_by_customer`, `receipts_assigned_types`, `receipts_assigned_invoice_numbers`, `receipts_assigned_counterparties`, `receipts_assigned_vat_rates`, `receipts_assigned_amounts`, `receipts_assigned_dates`, `receipts_assigned_links`, `fixed` (`"0"`/`"1"`), `comment`, `receipt_id_by_customer`, `transaction_id_by_customer`. Each row is one posting record (one debit/credit pair with its own amount); the plural `receipts_assigned_*` fields are typed as strings, so several values are presumably joined into one string — the separator is not specified.

Errors: 5/6 invalid date_from/date_to · 7 invalid account · 8 invalid postingaccount · 9 invalid posting_status · 10 invalid limit · 12 invalid offset · 13 invalid cost_location · 14/16 invalid date_last_action_from/to · 17 invalid order.

Cross-refs: use `account: "free booking"` + `order: "id_by_customer DESC"` to find the id of a free posting you just created.

### POST /postings/add/receipt

Purpose: post one receipt against one or more posting accounts (creditor/debtor posting must be activated). For a foreign-currency receipt first fetch `/receipts/get/id_by_customer` and use the calculated `amount`. Safety: create, not idempotent; undo with `/postings/unconfirm/receipt` while unfixed.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipt_id_by_customer` | yes | integer | | |
| `postingaccounts` | yes | array | posting account numbers, one per split | |
| `postingtexts` | yes | array | max 128 chars each | |
| `vats` | yes | array | VAT codes from the table above | |
| `cost_locations` | no | array | codes, max 10 chars | |
| `cost_locations_two` | no | array | codes, max 10 chars | |
| `amounts` | yes | array | format `0000.00`; must sum to the receipt amount | |
| `creditor` | yes (spec flag) — only when posting an incoming invoice with creditor posting active | integer | creditor number | |
| `debtor` | yes (spec flag) — only when posting an outgoing invoice with debtor posting active | integer | debtor number | |

Response: `success`, `message` (no posting id).

Errors: 5 invalid posting type · 6 receipt not found · 7 receipt is deleted · 8 expected account type by receipt does not match creditor/debtor type · 9 receipt type does not allow postings · 10 creditor posting not activated · 12 debtor posting not activated · 13 receipt not valid, complete the data · 14 receipt has already created a transaction · 16 a transaction linked to the receipt has already been posted · 17 no postingaccount · 18 postingaccount not valid · 19 not available · 20 cannot be booked manually · 21 no vat option · 22 invalid vat option for account · 24 account must be posted with vat option X · 25 vat option invalid for account · 26 account must be posted with/without VAT · 27 invalid tax key · 28 vat option unavailable due to settings · 29 unavailable with 'not liable to sales tax' · 31 posting text > 128 · 32 cost location > 10 · 33 cost location format · 34 foreign currencies only on account X · 35 invalid amount · 37 total does not match receipt amount · 38 total invalid · 39 foreign-currency postings not allowed · 40 no postings on receipts without currency · 41 date delivery invalid · 42 vat option not available for this date · 43 creditor/debtor invalid · 44/45 cost location two length/format · 46 invalid or not existing parameters.

Cross-refs: if the receipt is paid via a bank transaction, post the transaction instead (`/postings/add/transaction`) after linking (`/transactions/assign/receipt`) — error 16 guards against double booking.

### POST /postings/add-batch/receipts

Purpose: post several receipts in one call. Safety: create, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipts` | yes | array of `ReceiptPostings` | | each item validated like `/postings/add/receipt` |

`ReceiptPostings` item (spec `required`: `receipt_id_by_customer`, `postingaccounts`, `vats`, `amounts`, `creditor`, `debtor`):

| Field | Required (spec) | Type | Notes |
|---|---|---|---|
| `receipt_id_by_customer` | yes | integer | example 142 |
| `postingaccounts` | yes | array[integer] | |
| `postingstexts` | no | array[string] | **spelled `postingstexts` in the batch definition** (single endpoint: `postingtexts`, required there). Send the batch spelling; if rejected, try `postingtexts`. |
| `vats` | yes | array[string] | VAT codes |
| `cost_locations` | no | array[string] | |
| `cost_locations_two` | no | array[string] | |
| `amounts` | yes | array[number] | sum = receipt amount |
| `creditor` | yes (spec) | integer | example 70000; single endpoint says conditional |
| `debtor` | yes (spec) | integer | example 10000; single endpoint says conditional |

Positional rule: arrays inside one item must have the same length; index i describes split i.

Response: `success`, `receipts[]` of `{success, message}`, `errors[]` of `{success: false, error_code, message, request_data}` (item codes as `/postings/add/receipt`). Batch-level: 403/15 adding temporarily restricted. Response description reads "add receipt postings successfully".

### POST /postings/add/transaction

Purpose: post one transaction across one or more posting accounts, optionally assigning open-item receipts per split. Safety: create, not idempotent; undo with `/postings/unconfirm/transaction` while unfixed.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transaction_id_by_customer` | yes | integer | | |
| `postingaccounts` | yes | array | posting account numbers | |
| `postingtexts` | yes | array | max 128 chars each | |
| `vats` | yes | array | VAT codes | |
| `cost_locations` | no | array | | |
| `cost_locations_two` | no | array | | |
| `amounts` | yes | array | format `0000.00`; must sum to the transaction amount | |
| `oi_receipts_ids_by_customer` | yes (spec flag) — only if open-item (OI) postings are activated | array | one receipt id or `null` per split, e.g. `[123, null]` | `null` = explicitly no receipt for that split |

Response: `success`, `message` (no posting id).

Errors: 5 invalid posting type · 6 transaction not found · 7 a receipt linked to the transaction has already been posted · 8 no postingaccount · 9 not valid · 10 not available · 12 cannot be booked manually · 13 no vat option · 14 invalid vat option · 16 account must be posted with vat option X · 17 account must be posted with/without vat class · 18 invalid tax key · 19 vat unavailable due to settings · 20 unavailable with 'not liable to sales tax' · 21 posting text > 128 · 22 cost location > 10 · 24 cost location format · 25 foreign currencies only on account X · 26 invalid amount · 27 total does not match transaction amount · 29 total invalid · 31/32 cost location two · 34 for each partial posting one or no receipt must be given via oi_receipts_ids_by_customer · 46 invalid or not existing parameters.

### POST /postings/add-batch/transactions

Purpose: post several transactions in one call. Safety: create, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transactions` | yes | array of `TransactionPostings` | | validated like `/postings/add/transaction` |

`TransactionPostings` item (required: `transaction_id_by_customer`, `postingaccounts`, `postingtexts`, `vats`, `amounts`, `oi_receipts_ids_by_customer`):

| Field | Required | Type | Notes |
|---|---|---|---|
| `transaction_id_by_customer` | yes | integer | example 142 |
| `postingaccounts` | yes | array[integer] | |
| `postingtexts` | yes | array[string] | correct spelling here |
| `vats` | yes | array[string] | |
| `cost_locations` | no | array[string] | |
| `cost_locations_two` | no | array[string] | |
| `amounts` | yes | array[number] | sum = transaction amount |
| `oi_receipts_ids_by_customer` | yes (spec) | array[integer] | `null` entries allowed per the single endpoint; only needed with OI activated |

Response: `success`, `transactions[]` of `{success, message}`, `errors[]` of `{success: false, error_code, message, request_data}`. Batch-level: 403/15.

### POST /postings/add/free

Purpose: one manual journal entry (**freie Buchung**) debit → credit, not tied to a receipt or transaction (accruals, corrections, opening balances). Safety: create, not idempotent; undo with `/postings/unconfirm/free` while unfixed, `/postings/cancel` otherwise.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `date` | yes | string | `YYYY-MM-DD` | |
| `postingtext` | yes | string | max 128 chars | |
| `amount` | yes | **string** | e.g. `"250.00"`; **no negative amounts** (error 22) | |
| `postingaccount_debit` | yes | integer | **Soll** account | must be manually bookable; ≠ credit |
| `postingaccount_credit` | yes | integer | **Haben** account | |
| `vat` | yes | string | one code from the VAT table | must be allowed for the account combination |
| `cost_location` | no | string | max 10 chars | |
| `cost_location_two` | no | string | max 10 chars | |

Response: `success`, `message` (no posting id — find it via `/postings/get` with `account: "free booking"`).

Errors: 5 invalid posting type · 6 no date · 7 invalid date · 8 no postingtext · 9 text > 128 · 10 no postingaccount_debit · 12 debit invalid/not available · 13 no postingaccount_credit · 14 credit invalid/not available · 16 cost location > 10 · 17 cost location format · 18 no vat · 19 invalid vat · 20 no amount · 21 invalid amount · 22 no negative amounts allowed · 24 debit cannot be posted manually · 25 credit cannot be posted manually · 26 credit identical to debit · 27 account must be posted with vat option X · 28 vat option invalid for account · 29 account must be posted with/without vat class · 31 no vat possible for combination · 32 tax key invalid for combination · 33 vat unavailable due to settings · 34 unavailable with 'not liable to sales tax' · 36/37 cost location two length/format.

Cross-refs: attach a document afterwards with `/postings/assign/receipt-to-free-posting`.

### POST /postings/add-batch/free

Purpose: several free postings in one call. Safety: create, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `free_postings` | yes | array of `PostingsFree` items | | validated like `/postings/add/free` |

`PostingsFree` item (spec `required`: `date`, `postingtext`, `vat`, **`amounts`**, `postingaccount_debit`, `postingaccount_credit` — `amounts` is a phantom, the field is `amount`):

| Field | Required | Type | Example | Notes |
|---|---|---|---|---|
| `date` | yes | string | `2024-04-07` | |
| `postingtext` | yes | string | `postingtext` | |
| `amount` | effectively yes | **number** | `12.87` | single endpoint takes a string; the batch item is a number; positive only |
| `postingaccount_debit` | yes | integer | `1590` | |
| `postingaccount_credit` | yes | integer | `320` | |
| `vat` | yes | string | `19_vat` | |
| `cost_location` | no | string | | |
| `cost_location_two` | no | string | | |

Response: `success`, `free_postings[]` of `{success, message}`, `errors[]` of `{success: false, error_code, message, request_data}`. Batch-level: 403/15. Response description reads "add receipt postings successfully" (copy-paste in the spec).

### POST /postings/assign/receipt-to-free-posting

Purpose: attach a receipt to an existing free posting so the entry has its document. Safety: link; no unassign endpoint exists for this link.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipt_id_by_customer` | yes | integer | | |
| `posting_id_by_customer` | yes | integer | id of the free posting (from `/postings/get`) | |

Response: `success`, `message`.

Errors: 5 invalid assignment type · 6 receipt not found · 7 posting not found · 8 receipt is deleted · 9 posting is no free posting · 10 assignment failed.

Cross-refs: receipt ↔ transaction links use `/transactions/assign/receipt`.

### POST /postings/unconfirm/receipt

Purpose: remove the postings of one receipt by un-confirming them; only while not fixed. Safety: revert.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `receipt_id_by_customer` | yes | integer | | |

Response: `success`, `message`.

Errors: 5 invalid unconfirm type · 6 receipt not found · 7 receipt has no postings to unconfirm · 8 receipt has fixed postings that cannot be unconfirmed · 9 parameter must be an integer · 10 parameter is required.

### POST /postings/unconfirm/transaction

Purpose: remove the postings of one transaction by un-confirming them; only while not fixed. Safety: revert.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `transaction_id_by_customer` | yes | integer | | |

Response: `success`, `message`.

Errors: 5 invalid unconfirm type · 6 transaction not found · 7 transaction has no postings to unconfirm · 8 transaction has fixed postings · 9 must be an integer · 10 is required.

Cross-refs: required before `/transactions/unassign/receipt` if the assignment is part of a confirmed posting.

### POST /postings/unconfirm/free

Purpose: remove one free posting by un-confirming it; only while not fixed. Safety: revert.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `posting_id_by_customer` | yes | integer | id of the free posting | |

Response: `success`, `message`.

Errors: 5 invalid unconfirm type · 6 posting not found · 7 posting is not a free posting · 8 posting is fixed and cannot be unconfirmed · 9 must be an integer · 10 is required.

### POST /postings/cancel

Purpose: take a posting out of the books. Not fixed → deleted outright; fixed → a reversal posting (**Stornobuchung**) is created and both stay visible. Safety: delete, irreversible via API; confirm with the user.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `posting_id_by_customer` | yes | integer | any posting type | |

Response: `success`, `message`.

Errors: 5 parameter is required · 6 must be an integer · 7 posting not found · 8 posting cannot be cancelled · 9 posting could not be cancelled.

Cross-refs: prefer `/postings/unconfirm/*` when the goal is to correct and re-book an unfixed posting.

## Settings — debtors, creditors, posting accounts

Master data lives under `/settings`. Creditors (**Kreditoren**) and debtors (**Debitoren**) are sub-ledger accounts addressed by `postingaccount_number`; posting accounts (**Buchungskonten**) form the chart of accounts. None of the three can be deleted via API.

### POST /settings/get/debtors

Purpose: list debtors (**Debitoren**, customers you invoice). Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `limit` | no | integer | default 25 | |
| `offset` | no | integer | default 0 | |

Response: `rows`, `data[]`: `type` (`debitor`), `name`, `contact_person_name`, `street`, `additional_addressline`, `zip`, `city`, `country`, `sales_tax_id_eu`, `email`, `uid_ch` (Swiss UID), `iban`, `bic`, `postingaccount_number`, `import_pending` (integer). Note `customer_number` is accepted on add/update but not returned here.

Errors: 5 invalid settings type.

### POST /settings/add/debtor

Purpose: create a debtor account. Safety: create, not idempotent, no delete afterwards.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `name` | yes | string | | |
| `postingaccount_number` | no | string | | omitted → next free number is assigned |
| `contact_person_name` | no | string | | |
| `street` | no | string | | |
| `additional_address_line` | no | string | | note underscore spelling |
| `customer_number` | no | string | | |
| `zip` | no | string | | |
| `city` | no | string | | |
| `country` | no | string | German name or ISO-2 | |
| `sales_tax_id` | no | string | VAT id (**USt-IdNr.**) | |
| `email` | no | string | | |
| `iban` | no | string | | |
| `bic` | no | string | | |

Response: `postingaccount_number` (string).

Errors: 5 invalid settings type · 6 invalid type · 7 invalid postingaccount_number · 8 invalid name · 9 contact_person_name · 10 street · 12 additional_addressline · 13 zip · 14 (spec message literally "invalid street specified", a copy-paste duplicate of 10 — presumably city) · 16 country · 17 sales_tax_id · 18 iban · 19 bic · 20 email · 21 customer_number.

### POST /settings/add-batch/debtors

Purpose: create several debtors. Safety: create, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `debtors` | yes | array of `SettingsDebtor` | | validated like `/settings/add/debtor` |

`SettingsDebtor` item (required: `name`): `name` (string), `postingaccount_number` (string), `contact_person_name`, `street`, `additional_address_line`, `customer_number`, `zip`, `city`, `country`, `sales_tax_id`, `iban`, `bic` (all strings). **No `email` field** in the batch item.

Response: `success`, `debtors[]` of `{success, postingaccount_number, message}`, `errors[]` of `{success: false, error_code, message, request_data}`. Batch-level: 403/15.

### POST /settings/update/debtor

Purpose: update a debtor; only the fields you send change, but each sent field is overwritten. Safety: update.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `postingaccount_number` | yes | integer | existing debtor number | |
| `name` | no | string | | |
| `contact_person_name` | no | string | | |
| `street` | no | string | | |
| `additional_address_line` | no | string | | |
| `customer_number` | no | string | | |
| `zip` | no | string | | |
| `city` | no | string | | |
| `country` | no | string | German name or ISO-2 | |
| `sales_tax_id` | no | string | | |
| `email` | no | string | | |
| `iban` | no | string | | |
| `bic` | no | string | | |

Response: `data` (the updated debtor: `type`, `name`, `contact_person_name`, `street`, `additional_addressline`, `zip`, `city`, `country`, `sales_tax_id_eu`, `email`, `uid_ch`, `iban`, `bic`, `postingaccount_number`).

Errors: 1 wrong debtor account postingaccount_number · 5 invalid settings type · 8–21 field validation as on add (14 again reads "invalid street specified") · 24 no debtor found for specified postingaccount_number.

### POST /settings/get/creditors

Purpose: list creditors (**Kreditoren**, suppliers). Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `limit` | no | integer | default 25 | |
| `offset` | no | integer | default 0 | |

Response: `rows`, `data[]`: `type` (`creditor`), `name`, `contact_person_name`, `street`, `additional_addressline`, `zip`, `city`, `country`, `sales_tax_id_eu`, `email`, `uid_ch`, `iban`, `bic`, `postingaccount_number`, `import_pending`. `due_in_days` is not returned.

Errors: 5 invalid settings type.

### POST /settings/add/creditor

Purpose: create a creditor account. Safety: create, not idempotent, no delete afterwards.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `name` | yes | string | | |
| `postingaccount_number` | no | string | | omitted → next free number |
| `contact_person_name` | no | string | | |
| `street` | no | string | | |
| `additional_address_line` | no | string | | |
| `zip` | no | string | | |
| `city` | no | string | | |
| `country` | no | string | German name or ISO-2 | |
| `sales_tax_id` | no | string | | |
| `email` | no | string | | |
| `iban` | no | string | | |
| `bic` | no | string | | |
| `due_in_days` | no | integer | payment term in days | |

Response: `postingaccount_number` (string).

Errors: 5 invalid settings type · 6 invalid type · 7 invalid postingaccount_number · 8 invalid name · 9 contact_person_name · 10 street · 12 additional_addressline · 13 zip · 14 (spec message literally "invalid street specified", a copy-paste duplicate of 10 — presumably city) · 16 country · 17 sales_tax_id · 18 iban · 19 bic · 20 email · 21 invalid due in days.

Cross-refs: use the returned number as `creditor_debtor` on `/receipts/upload` / `/receipts/add` and as `creditor` on `/postings/add/receipt`.

### POST /settings/add-batch/creditors

Purpose: create several creditors. Safety: create, partial success.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `creditors` | yes | array of `SettingsCreditor` | | validated like `/settings/add/creditor` |

`SettingsCreditor` item (required: `name`): `name`, `postingaccount_number` (string), `contact_person_name`, `street`, `additional_address_line`, `zip`, `city`, `country`, `sales_tax_id`, `iban`, `bic` (strings), `due_in_days` (integer). **No `email` field** in the batch item.

Response: `success`, `creditors[]` of `{success, postingaccount_number, message}`, `errors[]` of `{success: false, error_code, message, request_data}`. Batch-level: 403/15.

### POST /settings/update/creditor

Purpose: update a creditor. Safety: update.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `postingaccount_number` | yes | integer | existing creditor number | |
| `name` | no | string | | |
| `contact_person_name` | no | string | | |
| `street` | no | string | | |
| `additional_address_line` | no | string | | |
| `zip` | no | string | | |
| `city` | no | string | | |
| `country` | no | string | | |
| `sales_tax_id` | no | string | | |
| `email` | no | string | | |
| `iban` | no | string | | |
| `bic` | no | string | | |
| `due_in_days` | no | integer | | |

Response: `data` (updated creditor, same shape as the debtor object with `type: creditor`; the spec labels it "the updated Debitor").

Errors: 1 wrong creditor account postingaccount_number · 5 invalid settings type · 8–20 field validation as on add (14 again reads "invalid street specified") · 21 invalid due in days · 24 no creditor found for specified postingaccount_number.

### POST /settings/get/postingaccounts

Purpose: list the chart of accounts including payment accounts, creditors and debtors, with exclusion flags. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `limit` | no | integer | default 1000 | |
| `offset` | no | integer | default 0 | |
| `order` | no | string | `postingaccount_number ASC` / `DESC`, `name ASC` / `DESC`, `type ASC` / `DESC` | default null |
| `exclude_postingaccounts` | no | boolean | default false | drop ordinary posting accounts |
| `exclude_accounts` | no | boolean | default false | drop payment ("base") accounts such as bank |
| `exclude_creditors` | no | boolean | default false | |
| `exclude_debtors` | no | boolean | default false | |

Response: `rows`, `data[]`: `postingaccount_number`, `name`, `type` (e.g. `postingaccount`), `subtype` (e.g. `default chart`), `parent_postingaccount_number`, `parent_name`.

Errors: 5 invalid settings type · 6 invalid limit · 7 invalid offset · 8 invalid order · 9 invalid exclude_accounts · 10 invalid exclude_postingaccounts · 12 invalid exclude_creditors · 13 invalid exclude_debtors.

Cross-refs: to resolve "office supplies" to a number before posting; payment accounts only → `/accounts/get`.

### POST /settings/add/postingaccount

Purpose: add a custom posting account that inherits its properties (VAT behaviour, report position) from a parent account of the standard chart. Safety: create, no delete afterwards.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `name` | yes | string | length limits reported as %min%–%max% | must be unique |
| `postingaccount_number` | yes | integer | digit-count and range limits reported in messages | must be unused |
| `parent_postingaccount_number` | yes | integer | standard-chart account to inherit from; may not itself be a manually added account | |

Response: `postingaccount_number`, `parent_postingaccount_number` (strings).

Errors: 5 no postingaccount_number · 6 must have %min% to %max% digits · 7 out of allowed range · 8 already exists or not available due to settings · 9 invalid postingaccount_number · 10 no name · 12 name length · 13 name already exists · 14 invalid name · 16 no parent_postingaccount_number · 17 number must be at least %min% digits · 18 parent not valid / not available / was added manually · 19 invalid parent_postingaccount_number.

### POST /settings/update/postingaccount

Purpose: rename a posting account (name is the only editable property). Safety: update.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `name` | yes | string | | |
| `postingaccount_number` | yes | integer | | |

Response: `data` `{name, postingaccount_number}`.

Errors: 5 invalid settings type · 6 no name · 7 name length · 8 invalid name · 9 wrong postingaccount_number · 10 no postingaccount found.

## Accounts

Payment accounts ("basic accounts", **Konten**: bank, cash, other). Transactions belong to exactly one of them. No update or delete via API.

### POST /accounts/get

Purpose: list payment accounts with their posting account numbers. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |

Response: `rows`, `data[]` of `{name (e.g. "Bank (…)"), postingaccount_number (e.g. "1200")}`.

Errors: universal only.

Cross-refs: the number is the `account` value for `/transactions/get`, `/transactions/add`, `/receipts/add`, `/receipts/upload` and the `account` filter on `/postings/get`.

### POST /accounts/add

Purpose: register a new payment account. Safety: create, not idempotent; cannot be changed or removed afterwards.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `type` | yes | string | `cash`, `bank/institution`, `other` | |
| `name` | yes | string | unique; length %min%–%max% | |
| `postingaccount_number` | yes | integer | unused; digit/range limits apply | e.g. `1210` |
| `receipt_creates_transaction` | no | boolean | default false | receipts assigned to this account automatically create a transaction (typical for cash) |
| `is_revision_safe` | no | boolean | default false | cash accounts only: saved transactions can then only be removed via a cancellation transaction (**revisionssicheres Kassenbuch**) |

Response: `postingaccount_number` (string).

Errors: 5 no type · 6 invalid type · 7 no name · 8 name length · 9 name already exists · 10 invalid name · 12 no postingaccount_number · 13 digits · 14 out of range · 16 already exists · 17 invalid postingaccount_number · 18 invalid receipt_creates_transaction · 19 invalid is_revision_safe.

## Comments

### POST /comments/add

Purpose: attach a free-text note to exactly one receipt or one transaction. Safety: create; comments cannot be read, edited or deleted via API (they show in the web app and in `/postings/get` `comment` where applicable).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `comment_text` | yes | string | 2–210 characters | |
| `transaction_id_by_customer` | one of the two | integer | | |
| `receipt_id_by_customer` | one of the two | integer | | |

Response: `success`, `message`.

Errors: 5 invalid transaction_id_by_customer · 6 invalid receipt_id_by_customer · 7 only one of the two may be specified · 8 one of the two must be specified · 9 transaction not found · 10 receipt not found · 12 invalid comment_text · 13 no comment text.

## Cost locations

Cost centres (**Kostenstellen**), referenced by `code` from the posting endpoints (`cost_location`, `cost_locations[]`, `cost_location_two`, `cost_locations_two[]`).

### POST /cost-locations/get

Purpose: list cost locations or fetch one by code; each request limited to 1000. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `code` | no | string | | exact match, returns at most one |
| `limit` | no | integer | max 1000 | |
| `offset` | no | integer | | |

Response: `rows`, `data[]` of `{code, name}`.

Errors: 5 invalid limit · 6 invalid offset · 7 invalid code.

### POST /cost-locations/add

Purpose: create a cost location. Safety: create, not idempotent (check the list first).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `code` | yes | string | alphanumeric, max 10 chars | identifier used in postings |
| `name` | yes | string | | |

Response: `code`.

Errors: 5 invalid code · 6 invalid name.

### POST /cost-locations/update

Purpose: rename a cost location (the code itself cannot be changed). Safety: update.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `code` | yes | string | existing code | |
| `name` | yes | string | new name | |

Response: `success`, `message`.

Errors: 5 no cost location code · 6 cost location was not found · 7 invalid name.

### POST /cost-locations/delete

Purpose: delete a cost location. Safety: delete, **permanent** (no restore endpoint); confirm with the user.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `code` | yes | string | | |

Response: `success`, `message`.

Errors: 5 no cost location code · 6 not found · 7 cost location may not be deleted (in use).

## Reports

BWA and sums reports are **asynchronous two-step** calls: `create` returns a report `id_by_customer` immediately and starts generation; `get` fails with code 8 "report generation has not been finished yet" until it is done. Only one report per type can be generating at a time (create → code 12 "report generation already in progress"), and a new report of the same type **replaces** the previous one — do not request a second one while polling. The ledger is different: it is computed on the fly and needs no prior report.

### POST /reports/create/bwa

Purpose: trigger generation of a **BWA** (**Betriebswirtschaftliche Auswertung**) for a period. Safety: create (replaces the previous BWA).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `date_from` | yes | string | `YYYY-MM-DD` | first day of period |
| `date_to` | yes | string | `YYYY-MM-DD` | last day of period |

Response: `id_by_customer` (report id, string).

Errors: 6 invalid date_from · 7 invalid date_to · 12 report generation already in progress.

### POST /reports/get/bwa

Purpose: fetch a finished BWA, optionally with its files. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `report_id_by_customer` | yes | integer | id from create | |
| `get_files` | no | boolean | default false | include base64 files |

Response: `report` object with keys `integrityError`, `standardChart`, `usedCostLocations`, `usedPostingaccountsNumbers`, `postingsRecordsCount`, `uncompletedPostingsCount`, `groups` (→ classes → postingaccounts, each with unformatted `amountsSum`), `totals`. `files` (only with `get_files`): `{csv, pdf}` base64 or `null` when not requested / still generating / expired.

Errors: 6 invalid report_id_by_customer · 7 report was not found (also after it has been replaced) · 8 report generation has not been finished yet (poll again) · 9 invalid get_files.

### POST /reports/create/sums

Purpose: trigger a sums report (**Summen- und Saldenliste**) over all posting accounts for a period, optionally with PDF/CSV/ZIP export. Safety: create (replaces the previous sums report).

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `date_from` | yes | string | `YYYY-MM-DD` | |
| `date_to` | yes | string | `YYYY-MM-DD` | |
| `base` | no | string | `date` (**Buchungsdatum**, default), `date_delivery_else_date` (**Buchungs- und Leistungsdatum**) | which date decides period membership |
| `file_pdf` | no | boolean | default false | also render a PDF |
| `file_csv` | no | boolean | default false | also render a CSV |
| `archive_export` | no | boolean | default false | ZIP with CSV plus all ledgers (**Kontenblätter**) |

Response: `id_by_customer` (report id).

Errors: 6/7 invalid date_from/date_to · 8 invalid base · 9 invalid file_pdf · 10 invalid file_csv · 12 report generation already in progress · 13 invalid archive_export.

### POST /reports/get/sums

Purpose: fetch a finished sums report. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `report_id_by_customer` | yes | integer | | |
| `get_files` | no | boolean | default false | |

Response: `report` object with `integrityError`, `countPostingsWithDateVatEffectiveNotConsideredInReport`, `sums` keyed by posting account number, each entry with `postingaccount` plus unformatted `balanceBeforeDebit`, `balanceBeforeCredit`, `balanceBeforeAbsolute`, `balanceBeforeSide`, `sumPeriodDebit`, `sumPeriodCredit`, `balanceAfterDebit`, `balanceAfterCredit`, `balanceAfterAbsolute`, `balanceAfterSide`. `files` (with `get_files`): `{csv, pdf, csv_archive}` base64 or `null`.

Errors: 6 invalid report_id_by_customer · 7 report was not found · 8 generation not finished · 9 invalid get_files.

### POST /reports/get/sums/ledger

Purpose: ledger (**Kontenblatt**) of one posting account for a period — every posting with running balance. Computed on the fly; no prior `create` needed; can be slow for busy accounts. Safety: read.

| Parameter | Required | Type | Allowed values / format | Notes |
|---|---|---|---|---|
| `api_key` | yes | string | | |
| `postingaccount_number` | yes | integer | | numbers available appear as keys of `sums` in `/reports/get/sums` |
| `date_from` | yes | string | `YYYY-MM-DD` | |
| `date_to` | yes | string | `YYYY-MM-DD` | |
| `base` | no | string | `date` (default), `date_delivery_else_date` | |

Response: `report_sums_postingaccount_ledger` with `integrityError`, `postingaccount_number`, `postingaccountLedger` (array; each entry: date, posting text, counter posting account, amount, vat, `balanceAfterAbsolute`, `balanceAfterSide`; empty if no postings).

Errors: 10 invalid postingaccount_number · 12/13 invalid date_from/date_to · 14 invalid base · 16 postingaccount was not found.

## What v1 cannot do

Verified against the 54 paths in the spec.

| Resource | Available | Missing |
|---|---|---|
| Receipts | list, get, add, addBatch, upload, soft delete, restore, list linked transactions | **no update** of metadata after creation (re-create instead), no hard delete, no file download other than base64 via get |
| Transactions | list, get, add, addBatch, assign/unassign receipt, list linked receipts | **no update, no delete**, no duplicate detection on import |
| Invoices | create, create draft, create e-invoice | **no list/read, no update, no cancel or delete, no send/re-send**; drafts cannot be listed or released via API (release happens in the web app) |
| Postings | list, add (receipt / transaction / free, single and batch), assign receipt to free posting, unconfirm, cancel | no get-by-id, **no in-place edit** (unconfirm + re-add), no fixing (**Festschreibung**), no unassign of a receipt from a free posting, add endpoints return no id |
| Creditors / debtors | list, add, addBatch, update | **no delete**, no get-by-number (page the list) |
| Posting accounts | list, add, update (name only) | **no delete**, no change of number or parent |
| Payment accounts | list, add | **no update, no delete** |
| Comments | add | **no read, update or delete** |
| Cost locations | list, add, update (name), delete | no restore after delete, no code change |
| Reports | BWA, sums, ledger | no other reports (no EÜR, GuV, Bilanz, UStVA, DATEV export), no list of generated reports, previous report of a type is replaced |
| Tenant / meta | — | no endpoint to list customers (`api_key` values) or to read customer settings (chart type, OI activation, creditor/debtor posting activation); those states surface only as error codes |
| Eventing | — | no webhooks or change feeds; poll with `date_since_last_modified` (receipts, transactions) and `date_last_action_from` (postings) |

## Typical call sequences

All bodies are JSON sent with `Content-Type: application/json` and the Basic Auth header; `<API_KEY>` selects the customer. Account numbers are SKR03-style examples (1200 bank, 4930 office supplies, 1600 trade payables, 70001 creditor, 10001 debtor) — resolve the real ones via `/settings/get/postingaccounts` and `/accounts/get` first.

### (a) Upload a receipt → find the bank transaction → link → post

1. Upload (base64 → `file_name` required):

```json
POST /receipts/upload
{"api_key": "<API_KEY>", "type": "invoice inbound", "file": "<BASE64_PDF>", "file_name": "supplier-invoice-2026-08-0042.pdf", "counterparty": "<SUPPLIER_NAME>", "invoice_number": "2026-08-0042", "date": "2026-08-14", "amount": 119.00, "currency": "EUR", "vat_rate": 19.00}
→ {"success": true, "message": "", "id_by_customer": "123", "filename": "receipt567"}
```

2. List August transactions on the bank account:

```json
POST /transactions/get
{"api_key": "<API_KEY>", "account": 1200, "date_from": "2026-08-01", "date_to": "2026-08-31", "limit": 500, "offset": 0}
→ {"success": true, "rows": 2, "data": [{"id_by_customer": "654", "to_from": "<SUPPLIER_NAME>", "amount": "-119.00", "booking_date": "2026-08-20 00:00:00", "value_date": "2026-08-20 00:00:00", "purpose": "Invoice 2026-08-0042"}, {"...": "..."}]}
```

3. Link receipt 123 to transaction 654 (creates the assignment only):

```json
POST /transactions/assign/receipt
{"api_key": "<API_KEY>", "transaction_id_by_customer": 654, "receipt_id_by_customer": 123}
→ {"success": true, "message": ""}
```

4. Post the transaction with account and VAT code (one split line):

```json
POST /postings/add/transaction
{"api_key": "<API_KEY>", "transaction_id_by_customer": 654, "postingaccounts": [4930], "postingtexts": ["Office supplies, invoice 2026-08-0042"], "vats": ["19_pre"], "amounts": ["119.00"], "oi_receipts_ids_by_customer": [123]}
→ {"success": true, "message": ""}
```

Notes: the spec only says the amounts must sum to the transaction amount in format `0000.00`; whether an outgoing (negative) transaction expects `"119.00"` or `"-119.00"` is not stated — if code 27 "total amount … does not match" comes back, flip the sign. Send `oi_receipts_ids_by_customer` only if open-item posting is activated for the customer (otherwise omit it). Verify with `/postings/get` (`date_from`/`date_to` around 2026-08-20, `account: "1200"`).

### (b) Create a free posting and attach a receipt

1. Book the entry (amount is a string, positive; direction via debit/credit):

```json
POST /postings/add/free
{"api_key": "<API_KEY>", "date": "2026-08-31", "postingtext": "Accrual office supplies August", "amount": "250.00", "postingaccount_debit": 4930, "postingaccount_credit": 1600, "vat": "19_pre"}
→ {"success": true, "message": ""}
```

2. The response carries no id; find it:

```json
POST /postings/get
{"api_key": "<API_KEY>", "date_from": "2026-08-31", "date_to": "2026-08-31", "account": "free booking", "order": "id_by_customer DESC", "limit": 10}
→ {"success": true, "rows": 1, "data": [{"id_by_customer": "9876", "postingtext": "Accrual office supplies August", "amount": "250.00", "debit_postingaccount_number": "4930", "credit_postingaccount_number": "1600", "fixed": "0", "...": "..."}]}
```

3. Attach the document (receipt 123 created via upload or `/receipts/add`):

```json
POST /postings/assign/receipt-to-free-posting
{"api_key": "<API_KEY>", "receipt_id_by_customer": 123, "posting_id_by_customer": 9876}
→ {"success": true, "message": ""}
```

Undo while unfixed: `POST /postings/unconfirm/free {"api_key": "<API_KEY>", "posting_id_by_customer": 9876}`.

### (c) BWA or sums report: create → poll get until ready

```json
POST /reports/create/bwa
{"api_key": "<API_KEY>", "date_from": "2026-01-01", "date_to": "2026-03-31"}
→ {"success": true, "message": "", "id_by_customer": "17"}

POST /reports/get/bwa            (repeat every few seconds)
{"api_key": "<API_KEY>", "report_id_by_customer": 17, "get_files": false}
→ 400 {"success": false, "error_code": 8, "message": "report generation has not been finished yet"}
→ … later: {"success": true, "message": "", "report": {"integrityError": false, "groups": [ "..." ], "totals": { "...": "..." }, "...": "..."}}
```

Sums report with files, then the ledger of one account:

```json
POST /reports/create/sums
{"api_key": "<API_KEY>", "date_from": "2026-01-01", "date_to": "2026-03-31", "base": "date", "file_pdf": true, "file_csv": true}
→ {"success": true, "message": "", "id_by_customer": "18"}

POST /reports/get/sums
{"api_key": "<API_KEY>", "report_id_by_customer": 18, "get_files": true}
→ {"success": true, "report": {"sums": {"4930": {"balanceAfterAbsolute": "…", "balanceAfterSide": "…", "...": "..."}}, "...": "..."}, "files": {"csv": "<BASE64>", "pdf": "<BASE64>", "csv_archive": null}}

POST /reports/get/sums/ledger    (no create needed)
{"api_key": "<API_KEY>", "postingaccount_number": 4930, "date_from": "2026-01-01", "date_to": "2026-03-31"}
```

Polling rules: stop on `success: true`; keep polling on code 8; code 7 after a successful create means the report was replaced by a newer one; code 12 on create means the previous generation is still running — poll its id instead of creating again. Budget the polls against the 100 requests/minute limit.

### (d) Page through postings for a date range

```json
POST /postings/get
{"api_key": "<API_KEY>", "date_from": "2026-01-01", "date_to": "2026-12-31", "order": "id_by_customer ASC", "limit": 1000, "offset": 0}
→ {"success": true, "rows": 1000, "data": [ … 1000 rows … ]}

POST /postings/get
{"api_key": "<API_KEY>", "date_from": "2026-01-01", "date_to": "2026-12-31", "order": "id_by_customer ASC", "limit": 1000, "offset": 1000}
→ {"success": true, "rows": 1000, "data": [ … ]}

POST /postings/get
{"api_key": "<API_KEY>", "date_from": "2026-01-01", "date_to": "2026-12-31", "order": "id_by_customer ASC", "limit": 1000, "offset": 2000}
→ {"success": true, "rows": 137, "data": [ … 137 rows … ]}   ← fewer than limit: done
```

Stop when `data.length < limit` (or `data` is empty). Fix the `order` so pages do not shift; if postings may be added while you page, narrow the range or use `date_last_action_from` for incremental runs. For receipts and transactions the same loop uses `limit: 500`.

### (e) Create a creditor, then upload an inbound invoice pre-assigned to it

```json
POST /settings/add/creditor
{"api_key": "<API_KEY>", "name": "<SUPPLIER_NAME>", "street": "<STREET>", "zip": "<ZIP>", "city": "<CITY>", "country": "DE", "sales_tax_id": "<VAT_ID>", "iban": "<IBAN>", "due_in_days": 14}
→ {"success": true, "postingaccount_number": "70001", "message": ""}

POST /receipts/upload
{"api_key": "<API_KEY>", "type": "invoice inbound", "file": "<BASE64_PDF>", "file_name": "supplier-invoice-2026-09-0007.pdf", "creditor_debtor": 70001, "date": "2026-09-02", "amount": 238.00, "currency": "EUR", "vat_rate": 19.00, "invoice_number": "2026-09-0007", "counterparty": "<SUPPLIER_NAME>"}
→ {"success": true, "message": "", "id_by_customer": "124", "filename": "receipt568"}
```

If creditor posting is activated, book the receipt straight to the creditor:

```json
POST /postings/add/receipt
{"api_key": "<API_KEY>", "receipt_id_by_customer": 124, "postingaccounts": [4930], "postingtexts": ["Office supplies, invoice 2026-09-0007"], "vats": ["19_pre"], "amounts": ["238.00"], "creditor": 70001}
→ {"success": true, "message": ""}
```

Before adding, check `/settings/get/creditors` (page with `limit`/`offset`, default 25) for an existing supplier with the same name — creation is not idempotent and creditors cannot be deleted.

## Spec quirks

Inconsistencies found in `v1.de.json` 1.9.1, each cross-checked with `jq` against the raw file.

1. **Missing id parameter.** `/receipts/get/id_by_customer`, `/receipts/delete/id_by_customer`, `/receipts/restore/id_by_customer` and `/transactions/get/id_by_customer` declare only `api_key` (plus `get_file`), yet each defines error 5 "invalid id_by_customer specified". The literal `id_by_customer` in the path is a placeholder: existing clients call `POST /receipts/get/123` etc. with the id as the last path segment. A body field `id_by_customer` is the untested fallback. Not verified live.
2. **Phantom required field.** `definitions.PostingsFree.items.required` lists `amounts` while the property is `amount`. No payload can satisfy the schema literally; send `amount`.
3. **`postingstexts` typo.** `definitions.ReceiptPostings` spells the field `postingstexts` and does not list it as required, whereas `/postings/add/receipt` uses `postingtexts` and requires it. `TransactionPostings` spells it `postingtexts`. Which spelling the server accepts on the batch endpoint is not verifiable from the spec.
4. **Conditional fields flagged required.** `/postings/add/receipt` marks both `creditor` and `debtor` required and describes each as required only for the matching receipt type; `ReceiptPostings` requires both. `/postings/add/transaction` marks `oi_receipts_ids_by_customer` required but says it is only required with OI posting activated.
5. **Batch items lack `email`.** `SettingsCreditor` and `SettingsDebtor` have no `email` property although the single add/update endpoints accept it.
6. **Currency statements contradict each other.** `/receipts/add`: "At the moment we accept USD, GBP and CHF"; `/receipts/upload`: "Has to be 'EUR' if specified"; `Receipt`/`Transaction` batch items: schema enum `["EUR"]` but a description listing ~50 ISO codes (`RSD` appears only in the batch lists); `/transactions/add` lists the codes without an enum. Only `EUR` is consistent.
7. **`rows` semantics.** Documented everywhere as "Number of returned rows"; some third-party tooling treats it as the total match count. Do not rely on it for page math.
8. **Response enums are examples.** Every response property carries a one-element `enum` holding a sample value (`"receipt123"`, `1`); only `e_invoice_type` (`0`/`1`/`2`) and `file_type` (`pdf`/`xml`) on `/receipts/get/id_by_customer` look like real enumerations. Never validate responses against these enums.
9. **Integer in, string out.** Ids, account numbers and amounts are integers/numbers in requests and strings in responses (`rows` is even an integer on some endpoints and a string sample on others). `/transactions/get/id_by_customer` declares `account` as integer with a string example.
10. **`/receipts/get` `order` schema.** Declared as an object with one required property literally named `field` (enum ASC/DESC); the examples show the real shape `{"date": "ASC", "amount": "DESC"}` with keys `date`, `amount`, `invoicenumber`, `invoicingparty`.
11. **E-invoice leftovers.** `/invoices/create/e-invoice` error 42 "invalid e_invoice_type specified" refers to a parameter that does not exist; the response keyed `400 (41)` (`InvoicesCreateEInvoice_ErrorCode41`, "invalid e_invoice_id specified") also carries `error_code` 42 in its body, so no response ever carries code 41; the usage examples for `item_tax_type` and `item_tax_amount` are labelled `"item_vat"`.
12. **Copy-paste descriptions.** `/settings/update/creditor` response data is "the updated Debitor"; `/postings/add-batch/transactions` and `/postings/add-batch/free` report "add receipt postings successfully"; creditor `due_in_days` is described as belonging to a "debtor account"; the batch debtor `contact_person_name` says "creditor account"; `/settings/get/debtors` summary is "get debitors"; `/cost-locations/get` `limit`/`offset` talk about "postings".
13. **Same code, different meaning.** Code 15 is HTTP 403 "adding temporarily restricted" on batch endpoints but HTTP 400 "invalid sort field specified" on `/receipts/get`; code 23 is the generic empty-body error on 21 endpoints but "no receipts assigned to transaction" on `/transactions/unassign/receipt`. On `/transactions/add` the response keyed `400 (24)` (`TransactionsAdd_ErrorCode24`, "invalid booking text specified") carries `error_code` 23 in its body, colliding with that endpoint's own generic code 23 — a caller matching on 24 never sees it; disambiguate via `message`. Codes are strictly per endpoint.
14. **Add endpoints return no posting id.** `/postings/add/free`, `/postings/add/receipt`, `/postings/add/transaction` (and their batches) answer with `success`/`message` only; `/invoices/create/draft` returns neither id nor number.
15. **Paging caps differ.** `/postings/get` and `/cost-locations/get` cap at 1000; `/receipts/get` and `/transactions/get` at 500; creditors/debtors default to 25 with no stated cap; `/settings/get/postingaccounts` defaults to 1000.
16. **Format notation.** Transaction dates are written `YYYY-MM-DD HH:II:SS` (PHP `date()` notation for minutes). Booleans mostly default to the string `"false"` (a JSON `false` on `/accounts/add` and `/settings/get/postingaccounts`). `/receipts/add` `vat_rate` is a number that "may also be an empty string". `/invoices/create` `date` and `recurring_date_next` have no stated format.
17. **Generic error definitions.** The 35 endpoints with their own code-4 definition say "customer not found or insufficient privileges"; the other 19 (all batch endpoints, `/cost-locations/*`, `/reports/*`, `/transactions/unassign/receipt`, `/transactions/assigned-receipts/get`) reference the generic `Request_ErrorCode4` and return the longer "customer not found or invalid api client for customer or insufficient privileges". `Request_ErrorCode1`/`2` (HTTP/POST required) are defined but referenced by no path.
18. **Orphan definitions.** `PostingsReservationsAdd_*`, `PostingsReservationsGet_*`, `PostingsReservationsDelete_*` (success and ~30 error definitions) exist without any `/postings/reservations…` path — an undocumented or planned endpoint family.
19. **No `consumes`, no `securityDefinitions`.** The spec declares neither the multipart upload nor Basic Auth formally; both come from the prose and the docs page.
20. **Version field.** Third-party consumers report that `info.version` is not bumped reliably when the spec content changes; compare the path list and parameters rather than the version string (not independently verified here).
21. **Spelling drift.** `additional_addressline` (invoices, and in creditor/debtor responses) vs `additional_address_line` (creditor/debtor requests); `invoice_number` (receipts) vs `invoicenumber` (invoices and receipt responses); `/receipts/addBatch` and `/transactions/addBatch` are camelCase while every other batch path is `add-batch`.
22. **`basePath` is a full URL.** `host` is `webapp.buchhaltungsbutler.de` but `basePath` is `https://webapp.buchhaltungsbutler.de/api/v1`, which already contains scheme and host (invalid Swagger 2.0). Tooling that builds URLs as scheme + host + basePath produces a broken URL; use `basePath` alone.
23. **Mis-wired error response.** `/transactions/assign/receipt` maps its `400 (7)` response to `PostingsAssignReceiptToFreePosting_ErrorCode7` ("posting not found"); the matching `TransactionsAssignReceipt_ErrorCode7` ("no receipt_id_by_customer specified") exists but is referenced by no path, so the message a caller sees for a missing `receipt_id_by_customer` may read "posting not found".

## Sources

- Official Swagger 2.0 spec (German descriptions), v1.9.1: https://app.buchhaltungsbutler.de/docs/api/v1.de.json (download the JSON to inspect with `jq`; this reference was generated from version 1.9.1 of that file)
- Official API documentation page (base URL, Basic Auth, `api_key`, 100 requests/customer/minute; on credentials it says only that the api key "can be found in customers company data settings"): https://app.buchhaltungsbutler.de/docs/api/v1/
- Help-center article "Einrichtung der API-Schnittstelle" (source for the menu path **Einstellungen** → **Schnittstellen und API-Zugang**, where API Client, API Secret and API Key are shown; the `Content-Type: application/json` header with a raw JSON body; and the vendor Postman collection with 6 example requests): https://wissen.buchhaltungsbutler.de/hc/de/articles/11468075328797-Einrichtung-der-API-Schnittstelle
- Base URL: https://webapp.buchhaltungsbutler.de/api/v1
- Operational categorisation (read/create/update/link/revert/delete), idempotency notes and the cancel/unconfirm semantics were cross-checked against the spec text; claims that the spec contradicted (e.g. that the sums ledger requires a finished sums report) were dropped.
