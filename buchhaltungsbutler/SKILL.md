---
name: buchhaltungsbutler
description: Operate BuchhaltungsButler (German cloud accounting) via its REST API and apply German bookkeeping rules for a small UG/GmbH — SKR03/SKR04 accounts, Steuerschlüssel/VAT codes (19 %/7 %, §13b reverse charge, i.g.E.), Vorsteuer/Umsatzsteuer, UStVA, GoBD, BWA, Monatsabschluss, Jahresabschluss prep. Use when the user mentions BuchhaltungsButler, Buchhaltung/bookkeeping, Belege, Rechnungen, invoices or receipts to buchen/verbuchen/kontieren/hochladen, Buchungssatz, Kontierung, Zahlungen zuordnen, Kreditoren/Debitoren, reverse charge, Steuerberater-Export, month-end, or asks how to book a business transaction in Germany. API credentials come from Bitwarden CLI, never from files.
---

# BuchhaltungsButler + Buchhaltung

Two jobs: (1) drive the user's **BuchhaltungsButler** (BB) account through API v1 with `scripts/bb.sh`; (2) decide *how* something is booked under German rules. Default assumption: the client is a **UG (haftungsbeschränkt)** — double-entry books, Bilanz, Körperschaftsteuer, no private accounts, no EÜR. Ask if the user mentions Einzelunternehmen, Freiberufler, EÜR or Privatentnahme, or if `--check` shows a chart other than SKR03/SKR04 (Kasse 1220/Bank 1260 = SKR45, Kasse 0920/Bank 0945 = SKR49).

Read on demand, not up front:

| Need | File |
|------|------|
| Exact endpoint parameters, all 23 `vat` codes, error codes, batch item shapes, call sequences | `references/api.md` |
| How BB models Belege / Zahlungen / Buchungen, Festschreibung, Steuerschlüssel (BU/GU), Kontenrahmen, Deb/Kred mode, month-end, exports | `references/buchhaltungsbutler-konzepte.md` |
| German law and practice (verified 2026-09): USt, §13b, E-Rechnung, Fristen, SKR03↔SKR04 table, 36-case Kontierung cheat sheet, red flags | `references/buchhaltung-de.md` |

## 1. Credentials and setup

Credentials (API Client, API Secret, API Key) live in the user's Bitwarden vault, item **"BuchhaltungsButler API"** (login username = client, password = secret, hidden field `api_key`). `bb.sh` fetches them per call with the Bitwarden CLI; nothing is cached on disk.

- **Never** ask the user to paste credentials into the chat, never write them to any file, never echo them, never pass `api_key` in a body (`bb.sh` injects it and rejects bodies that contain it).
- `bb.sh` needs `BW_SESSION` in the environment. Any exit code 2 (`NOT_UNLOCKED`, `BW_ERROR`, `NO_ITEM`, `AMBIGUOUS_ITEM`, `BAD_ITEM`): stop, relay the message verbatim, and tell the user what to run in *their* terminal — usually
  ```sh
  export BW_SESSION="$(bw unlock --raw)"     # first time: bw config server <url> (self-hosted only); bw login
  ```
  then start Claude Code from that shell and retry. Never run `bw unlock`, `bw login` or `scripts/bb-setup.sh` yourself — they prompt for the master password.
- First-time setup is `scripts/bb-setup.sh`, run **by the user** in their own terminal (it prompts for the three values and stores them in Bitwarden). BB shows the values under *Einstellungen → Schnittstellen und API-Zugang*.
- `bw` missing? The scripts fall back to `nix-shell -p bitwarden-cli` automatically. `jq` and `curl` are required.
- `BB_API_CLIENT/BB_API_SECRET/BB_API_KEY` env vars override Bitwarden (CI only). `BB_BW_ITEM` renames the vault item.

Start every session that touches BB with `scripts/bb.sh --check`: it proves auth and lists the payment accounts (Basiskonten). Bank 1200 / Kasse 1000 means **SKR03**, Bank 1800 / Kasse 1600 means **SKR04** — every account number you use afterwards must match that chart. `settings/get/postingaccounts` is the authoritative account list (BB may have individual Sachkonten).

## 2. Safety rules (non-negotiable)

1. **Reads are free.** Report generation (`reports/create/*`) is a harmless write: run it with `--write` without asking. Everything that creates, links or changes a Beleg, Zahlung, Buchung, comment or master data needs the user's explicit go-ahead for that action, then `--write`; one go-ahead may cover an announced sequence (upload → link), but every posting gets its own table (rule 2). Deleting/cancelling (`receipts/delete/<id>`, `cost-locations/delete`, `postings/cancel`) needs `--destructive` and a second confirmation naming the record.
2. **Show the Buchungssatz before posting**: date, Basiskonto (Zahlung/Debitor/Kreditor) and Sachkonto — or Soll/Haben for a free posting — gross amount per split line, `vat` code, Buchungstext, Kostenstelle, and the Beleg it rests on. One table per posting, then wait for an explicit yes that refers to that table (ja/ok/buchen/yes). A question, a correction or "sieht gut aus" is not a go-ahead — re-show the corrected table and ask again.
3. **Keine Buchung ohne Beleg.** Upload or locate the receipt first; a free posting without a receipt is the exception (RAP, Umbuchung, Eigenbeleg) and must be labelled as such in the Buchungstext. A Kontoauszug is not a Rechnung (no Vorsteuer from it) but is the Beleg for bank fees.
4. **Creates are not idempotent** and there is no duplicate check. Before `receipts/upload`, `receipts/add*`, `transactions/add*`, `invoices/create*`, `settings/add*`: query first (`receipts/get` by `invoicenumber` — no underscore, unlike `invoice_number` on upload — or `counterparty` plus `date_from`/`date_to`; `transactions/get` by date range) and tell the user if a match exists.
5. **Festgeschriebene Buchungen** (fixed) cannot be edited; `postings/cancel` on them books a reversal, not a deletion. To re-book an unfixed posting use `postings/unconfirm/*` first. Nothing in the API fixes postings, files the UStVA, or exports for the Steuerberater — those are UI steps; say so instead of pretending.
6. Never change master data the user did not ask about; `settings/update/*` overwrites the fields you send — read the record first.
7. Rate limits: 100 requests per customer per minute; `receipts/upload` 10 per minute; `receipts/addBatch` and `transactions/addBatch` one call per 5 seconds. Use `--all` for paging (it sleeps between pages); pause between uploads.
8. Tax questions with money at stake (vGA, Betriebsstätte, Rückstellungen, Umwandlung, Verlustvortrag, Option zur Steuerpflicht — the red-flag list in `buchhaltung-de.md` §8): state what the rules say, then tell the user to confirm with the Steuerberater. Never invent thresholds; look them up in the reference or say you are unsure.

## 3. Calling the API

```sh
S=<this skill's directory>/scripts/bb.sh                # default install: ~/.claude/skills/buchhaltungsbutler/scripts/bb.sh
$S --check                                              # auth + payment accounts
$S --list-endpoints                                     # 54 endpoints with read/write/destructive class
$S accounts/get                                         # any read: JSON pretty-printed, exit 0 on success:true
$S receipts/get '{"list_direction":"inbound","payment_status":"unpaid","limit":50}'
$S receipts/get/123                                     # by-id endpoints: id in the path (spec writes .../id_by_customer)
$S --all transactions/get '{"date_from":"2026-01-01","date_to":"2026-01-31"}'   # follows limit/offset
$S --all settings/get/creditors                         # default page is only 25 → always --all
$S --write postings/add/transaction '{"transaction_id_by_customer":123,"postingaccounts":[4964],"postingtexts":["SaaS 01/2026"],"vats":["19_pre"],"amounts":["59.50"]}'
$S --write --upload ./rechnung.pdf 'invoice inbound' '{"counterparty":"ACME GmbH","invoice_number":"R-1001","date":"2026-01-15","amount":119.00,"vat_rate":19}'
$S --destructive receipts/delete/45
echo '{"list_direction":"outbound"}' | $S receipts/get -                        # body from stdin
```

Conventions that bite (details: `api.md` §Conventions):
- Every endpoint is POST with a JSON body. Dates `YYYY-MM-DD`; transaction `booking_date` with time `YYYY-MM-DD HH:MM:SS`.
- `receipts/get` requires `list_direction`; `postings/get` requires `date_from`/`date_to` (max 1000 per page). `rows` is the number of items in this page, not the total — page until `data` has fewer than `limit` items.
- Amounts: `receipts/upload`, `receipts/add`, `transactions/add` take numbers (upload amount positive for a normal invoice, negative only for a Gutschrift/Storno; transactions + in / − out). `postings/add/transaction|receipt` take split `amounts` as **gross strings** `"0000.00"` that must sum to the transaction/receipt amount; the `add-batch/*` item schemas declare `amounts` as numbers and list `oi_receipts_ids_by_customer` as required. `postings/add/free` takes one positive **string** `amount`; direction comes from the debit/credit account.
- The sign of split `amounts` on an outgoing (negative) transaction is not documented: start with the sign of the transaction `amount`; if code 27 "total does not match" comes back, flip it.
- Ids: requests send integers, responses return strings. `id_by_customer` is the number shown in the BB UI. The by-id path form (`receipts/get/123`) is what existing clients use but is unverified live; if BB answers code 5 "invalid id_by_customer", retry `receipts/get/id_by_customer '{"id_by_customer":123}'`, which `bb.sh` also accepts.
- Errors: `{"success":false,"error_code":N,"message":"…"}` with HTTP 400 (validation), 401 (auth), 403 (state/throttle), 422 (upload not processable), 500, 504 (code 30 timeout — a write may have happened, re-read before retrying). Codes are per endpoint; read the message. 3/4 = credentials or `api_key` wrong, 11 = customer inactive, 15 with HTTP 403 = throttled (on `receipts/get` 15 means a bad `order` field).
- Modes you cannot read via API: Deb/Kred and Offene-Posten (OI). Heuristic: `--all settings/get/creditors` returns entries ⇒ Kreditoren are active. Try `postings/add/transaction` without `oi_receipts_ids_by_customer`; if BB answers that it is required (code 34) ⇒ OI mode is on — repeat with one receipt id or `null` per split line.

## 4. Core workflows

**A. Eingangsrechnung end-to-end (invoice → receipt → [Kreditor] → payment → posting)**
1. Duplicate check: `receipts/get '{"list_direction":"inbound","invoicenumber":"R-1001"}'` (exact match) or `counterparty` plus a `date_from`/`date_to` window around the invoice date.
2. Upload: `--write --upload <pdf> 'invoice inbound' '{counterparty, invoice_number, date, amount (gross, positive), vat_rate, date_payment_due}'`; note the returned `id_by_customer`/`filename`. E-invoices (XRechnung/ZUGFeRD) are parsed from the XML and ignore the metadata fields. Pre-assign a supplier with `creditor_debtor` when Kreditoren are active.
3. **Kreditoren active** (the normal case for a Bilanzierer; heuristic in §3): book the Beleg now, at invoice date — `--write postings/add/receipt '{"receipt_id_by_customer":R,"creditor":70001,"postingaccounts":[4964],"postingtexts":["SaaS 01/2026"],"vats":["19_pre"],"amounts":["119.00"]}'` (Vorsteuer arises at Rechnungsdatum; the open item sits on the Kreditor). Show the table first (rule 2). **Kreditoren off**: skip this step; the expense is booked with the payment in step 6.
4. Find the payment: `transactions/get` with `date_from/date_to` around the due date and `to_from` = supplier. No payment yet → stop here; BB matches later (exact amount, 90 days before / 30 days after the Zahlung) or the user continues when paid.
5. Link: `--write transactions/assign/receipt '{"transaction_id_by_customer":T,"receipt_id_by_customer":R}'`. Linking books nothing.
6. Post the payment. Kreditoren active: `postingaccounts:[70001]`, `vats:["0_none"]`, amount = payment (clears the open item). Kreditoren off: decide the Kontierung (section 5) and post the expense — `--write postings/add/transaction` with parallel arrays (`postingaccounts`, `postingtexts`, `vats`, `amounts`, optional `cost_locations`, `oi_receipts_ids_by_customer` only in OI mode); split lines share index positions and must sum to the transaction amount. Table + go-ahead first.
7. Confirm success and report the posting in one line. `postings/add/*` returns no id; re-read with `postings/get` if the user needs the Buchungsnummer.

**B. Book bank transactions that already have receipts** — `--all transactions/get` for the period and `--all postings/get` for the same `date_from`/`date_to` with `account` = the bank account number; unbooked = transactions whose `id_by_customer` appears in no posting's `transaction_id_by_customer`. For each: `transactions/assigned-receipts/get` → Kontierung → one confirmation table for the whole batch → post each with `postings/add/transaction` (string amounts), or `postings/add-batch/transactions` (item `amounts` as numbers). A transaction whose receipt was booked against a Kreditor/Debitor can only be posted against that Personenkonto.

**C. Free posting (no bank movement)** — RAP, Umbuchungen, Gesellschafterdarlehen-Zinsen, corrections: `postings/add/free` with `postingaccount_debit`, `postingaccount_credit`, `amount` (positive string `"250.00"`), `vat`, `date`, `postingtext` (≤ 128 chars). The response carries no id — fetch it with `postings/get '{"date_from":"<date>","date_to":"<date>","account":"free booking","order":"id_by_customer DESC","limit":5}'`, match on `postingtext`/`amount`, take `id_by_customer`, then `--write postings/assign/receipt-to-free-posting '{"receipt_id_by_customer":R,"posting_id_by_customer":P}'`.

**D. Month-end review** — (1) unbooked transactions as in B; (2) `receipts/get` `payment_status:"unpaid"` inbound and outbound = Belege without an assigned Zahlung → open items, overdue via `due_date` (drill into one with `receipts/assigned-transactions/get` only when needed); (3) `--write reports/create/sums` → poll `reports/get/sums` → sanity-check Vorsteuer/Umsatzsteuer accounts and the bank balance against the real statement; (4) list what still blocks the UStVA (due the 10th of the following month, +1 month with Dauerfristverlängerung; filed from the BB UI). Full checklist: `buchhaltungsbutler-konzepte.md` §8.1, `buchhaltung-de.md` §5.1.

**E. Reports** — BWA and SuSa are two-step and asynchronous: `--write reports/create/bwa` (or `/sums`) with `date_from`/`date_to` → returns `id_by_customer` → `reports/get/bwa '{"report_id_by_customer":N}'` until it stops answering "not ready" (code 8); only one report per type in flight, a new create replaces the previous one. `reports/get/sums/ledger` (Kontenblatt) is computed on the fly for one `postingaccount_number` and period.

**F. Master data** — `--all settings/get/creditors|debtors|postingaccounts`; create suppliers before pre-assigning uploads; `settings/add/postingaccount` for individual Sachkonten; `accounts/add` for a manual Basiskonto (Verrechnungskonto, Auslagenkonto; number ranges are validated per Kontenrahmen). None of these can be deleted via API.

**G. Ausgangsrechnung** — `invoices/create` issues a numbered invoice and its receipt immediately and cannot be listed, edited or cancelled through the API; prefer `invoices/create/draft` (the user releases it in the UI) unless the user explicitly wants a final invoice. `invoices/create/e-invoice` for XRechnung/ZUGFeRD recipients. Reverse-charge invoices to EU business customers need both USt-IdNr, the note "Steuerschuldnerschaft des Leistungsempfängers", 0 % lines, and a ZM entry.

## 5. Kontierung quick reference

Decide in this order: (1) direction and document type (Rechnung? Kontoauszug, Mahnung, Angebot, Lieferschein are not Rechnungen — no Vorsteuer from them); (2) where the supplier sits — DE / EU business with your USt-IdNr on the invoice / Drittland; (3) is German VAT shown; (4) what was bought; (5) deductibility overlay (Bewirtung 70/30, Geschenke ≤ 50 €, private items of the Gesellschafter → Verrechnungskonto). Then pick the `vat` code and the account pair. Full decision trees: `buchhaltung-de.md` §2.11–2.12; all 23 codes with BU keys: `buchhaltungsbutler-konzepte.md` §3.6.

**Incoming invoice → `vat` code**

| Situation | `vat` | Note |
|-----------|-------|------|
| German supplier, 19 % shown | `19_pre` | Full Vorsteuer; §14 Abs. 4 UStG content, or Kleinbetragsrechnung ≤ 250 € brutto |
| German supplier, 7 % shown (Bahn, Taxi ≤ 50 km, books, hotel room, restaurant **food** since 2026) | `7_pre` | Hotel/restaurant bills carry two rates → one split line per rate |
| EU business, service, 0 % with your USt-IdNr (SaaS, ads, cloud, consulting from IE/LU/NL …) | `19_both_506` | §13b Abs. 1 UStG reverse charge; USt and VSt net to zero; still shown in the UStVA |
| Non-EU business, service, no VAT (US API/SaaS vendor, UK/CH contractor) | `19_both_511` | §13b Abs. 2 Nr. 1 UStG; zero-sum, but must be declared |
| EU business, **goods**, 0 % with your USt-IdNr | `19_both_2` / `7_both` | innergemeinschaftlicher Erwerb |
| Foreign VAT shown (Irish 23 %, US sales tax) | `0_none` | Never deductible; gross is the expense; fix your USt-IdNr in the vendor account and request a net invoice |
| German 19 % charged by a foreign vendor treating you as a consumer | `0_none` | §14c: not deductible; get a B2B invoice |
| Exempt / not taxable (bank and card fees, insurance, IHK, rent without option, Kleinunternehmer invoice) | `0_none` | No Vorsteuer even if the supplier is German |
| Reverse charge without Vorsteuerabzug (rare for a normal UG) | `19_both_6506` / `19_both_6511` | |

**Outgoing invoice** — domestic B2B/B2C 19 %: `19_vat` on 8400 | 4400; EU B2B service with the customer's valid USt-IdNr: `0_none` on 8336 | 4336 (reverse charge note + ZM); non-EU business customer: `0_none` on 8338 | 4338; reduced-rate goods: `7_vat` on 8300 | 4300. Payment-processor payouts are not revenue: book the gross sale, the fee on 4970 | 6855 (`0_none`, exempt payment service), and the transit via 1360 | 1460.

**Account pairs (SKR03 | SKR04) for the everyday cases** — labels verified against the DATEV 2026 charts in `buchhaltung-de.md` §6; BB may use its own individual Sachkonten, so confirm with `settings/get/postingaccounts`. Basiskonto = Bank 1200 | 1800 unless stated.

| Case | Sachkonto SKR03 | Sachkonto SKR04 | `vat` |
|------|-----------------|-----------------|-------|
| Software subscription / SaaS, German vendor | 4964 Lizenzen | 6837 | `19_pre` |
| SaaS / ads / cloud from an EU vendor (reverse charge) | 3123 (Automatikkonto) or 4964 with code | 5923 or 6837 | `19_both_506` |
| API / cloud from a US vendor | 3125 (Automatikkonto) | 5925 | `19_both_511` |
| Hosting, domains, IT maintenance (DE) | 4806 Wartung Hard-/Software or 4925 Internet | 6495 or 6810 | `19_pre` |
| Telefon / Internet | 4920 / 4925 | 6805 / 6810 | `19_pre` |
| Freelancer / Fremdleistungen (DE) | 3100 | 5900 | `19_pre` (Kleinunternehmer: `0_none`) |
| Bürobedarf | 4930 | 6815 | `19_pre` |
| Hardware ≤ 800 € netto (GWG) | 4855 Sofortabschreibung GWG (asset: 0480) | 6260 (0670) | `19_pre` |
| Laptop / hardware > 800 € netto | 0410 Geschäftsausstattung (AfA: 4830) | 0635 (6220) | `19_pre` |
| Fachliteratur / Fortbildung | 4940 / 4945 | 6820 / 6821 | `7_pre` / `19_pre` |
| Travel (employee incl. GGF): Fahrt / Übernachtung / Verpflegung / km | 4663 / 4666 / 4664 / 4668 | 6663 / 6660 / 6664 / 6668 | as shown; Pauschalen `0_none` |
| Bewirtung Geschäftspartner (70/30, VSt 100 %) | 4650 (70 %) + 4654 (30 %) | 6640 + 6644 | food `7_pre`, drinks `19_pre`, each split 70/30 |
| Team lunch / Betriebsveranstaltung | 4140 | 6130 | `7_pre` / `19_pre` |
| Geschenke Geschäftspartner ≤ 50 € / > 50 € | 4630 / 4635 | 6610 / 6620 | `19_pre` / `0_none` |
| Miete, Coworking | 4210 | 6310 | `19_pre` if VAT shown, else `0_none` |
| Werbekosten | 4600 | 6600 | `19_pre` (EU ad platform: `19_both_506`) |
| Bank, card, payment-processor fees | 4970 | 6855 | `0_none` |
| Versicherungen / IHK, Verbände | 4360 / 4380 | 6400 / 6420 | `0_none` |
| Rechts-/Steuerberatung / Buchführung / Jahresabschluss | 4950 / 4955 / 4957 | 6825 / 6830 / 6827 | `19_pre` |
| Umsatzerlöse 19 % (DE) / EU B2B services / Drittland | 8400 / 8336 / 8338 | 4400 / 4336 / 4338 | `19_vat` / `0_none` / `0_none` |
| Körperschaftsteuer + SolZ Vorauszahlung | 2200 + 2208 | 7600 + 7608 | `0_none` |
| Gewerbesteuer | 4320 | 7610 | `0_none` |
| USt-Zahllast an das Finanzamt / Sondervorauszahlung | 1780 / 1781 | 3820 / 3830 | `0_none` |
| Geschäftsführergehalt (Gesellschafter-GF) / Netto / Lohnsteuer / SV | 4124 / 1740 / 1741 / 1742 | 6024 / 3720 / 3730 / 3740 | `0_none` |
| Stammkapital-Einzahlung | 0800 Gezeichnetes Kapital | 2900 | `0_none` (free posting or Bank posting) |
| Gesellschafterdarlehen erhalten / Zinsen | 0730 Verbindlichkeiten ggü. Gesellschaftern / 2120 | 3510 (alt. 3640) / 7310 | `0_none` |
| Private purchase with the company card (GGF) | 1381 Forderungen gegen Gesellschafter | 1307 | `0_none` — no expense, no Vorsteuer |
| Gewinnausschüttung / KapESt | 0755 offene Ausschüttungen / 1746 | 3519 / 3760 | `0_none` (Steuerberater territory) |

Amounts for BB posting endpoints are gross per split line; BB derives net and tax from the `vat` code. For §13b codes the gross equals the net invoice amount. A Privateinlage/-entnahme does not exist for a UG — anything private goes through 1381 | 1307 or 0730 | 3510, otherwise it is vGA territory.

## 6. Glossary — BB UI ↔ API (full table: `buchhaltungsbutler-konzepte.md` §1.9)

| UI (German) | API | Meaning |
|-------------|-----|---------|
| Beleg / Eingangsbeleg / Ausgangsbeleg | receipt, `list_direction` inbound/outbound, `type` `invoice inbound` … | invoice or credit-note document |
| Zahlung / Umsatz / Transaktion | transaction (`amount` + in, − out) | bank, card, PayPal, Kasse movement |
| Buchung / Buchungssatz / Splitbuchung | posting; parallel arrays per split line | journal entry: free / receipt / transaction posting |
| Basiskonto / Zahlungskonto | account (`postingaccount_number`) | bank, Kasse, Auslagen-/Verrechnungskonto |
| Sachkonto / Buchungskonto / Gegenkonto | postingaccount | contra account (Aufwand/Ertrag/Bilanz) |
| Steuersatz / Steuerschlüssel (BU) | `vat` (`19_pre`, …); `tax_key` in `postings/get` | tax treatment incl. DATEV key on export |
| Kreditor / Debitor | creditor / debtor; `creditor_debtor` on upload | supplier / customer sub-ledger (70000… / 10000…) |
| Kostenstelle | `cost_location`, `cost_location_two` | cost centre (≤ 10 chars) |
| Buchungstext | `postingtext` (≤ 128 chars) | |
| Rechnungsnummer | `invoice_number` (upload) / `invoicenumber` (get, invoices) | spelling differs per endpoint |
| bestätigt / festgeschrieben | (implicit) / `posting_status` fixed, field `fixed` | booked / GoBD-locked |
| Nr. in der UI | `id_by_customer` | per-customer counter; integer in, string out |
| Offene Posten | `oi_receipts_ids_by_customer`, `payment_status` | open-item mode when Deb/Kred is active |
