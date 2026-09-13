# BuchhaltungsButler — concepts reference

How BuchhaltungsButler (BB) models bookkeeping, what its UI terms mean, and how they map to the API v1 (`app.buchhaltungsbutler.de/docs/api/v1/`). Compiled from the BB help center (wissen.buchhaltungsbutler.de) and the API spec. SKR account numbers are given as `SKR03 | SKR04` unless stated otherwise. Statements marked *(inferred)* are not stated verbatim in a source.

---

## 1. Data model and terminology

### 1.1 The three objects: Beleg, Zahlung, Buchung

- **Beleg** (receipt: an invoice, credit note or other voucher document) lives in *Belegverwaltung* / *Belege*, sorted into **Eingangsbelege** (inbound: supplier invoices) and **Ausgangsbelege** (outbound: your own invoices). BB's OCR reads Belegdatum, Gegenpartei, Rechnungsnummer, Betrag, USt-Satz, IBAN and USt-ID of the counterparty; the user corrects and saves. A fresh upload is tagged **ungeprüft** (unchecked).
- **Zahlung** (transaction / payment; the UI also says Transaktion or Umsatz) is a movement on a **Zahlungskonto** (payment account: bank, credit card, PayPal, Kasse, manual account). Zahlungen arrive via bank interface (finAPI/Qwist), payment-provider integrations, CSV import, manual entry, "Beleg erzeugt Zahlung", or the API.
- **Buchung** (posting / Buchungssatz) is the journal entry. BB has three kinds: a posting *at a Zahlung* (the normal EÜR case), a posting *at a Beleg* (only with Debitoren/Kreditoren active: "Beleg kreditorisch/debitorisch erfassen"), and a **freie Buchung** in the *Erweitert* area (no Zahlung, no Beleg: accruals, RAP, payroll journals, Umbuchungen, EB-Werte, AfA).
- A Beleg is assigned to a **Zahlung**, never to an individual Buchung. One Zahlung can carry several Belege and several **Teilbuchungen** (split postings), but the Beleg-to-posting link is only implicit (FIFO, see §4.4). For DATEV exports BB recommends one Beleg per Zahlung because only one Beleglink per posting can be transmitted.
- The workflow order BB expects: upload Beleg → check data → (Bilanzierer) book the Beleg against a Kreditor/Debitor → assign the Zahlung → book the Zahlung (EÜR: expense/revenue; Deb/Kred: clearing of the open item).

Source: Buchhaltung und Zahlungszuordnung am Beleg — https://wissen.buchhaltungsbutler.de/hc/de/articles/16331531911837
Source: Erste Schritte mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11419668183709
Source: GoBD konformes Arbeiten mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432424987037

### 1.2 Basiskonto vs Sachkonto, Soll/Haben logic

- Every Buchungssatz in BB has a **Basiskonto** (main account, the "Ausgangskonto") on one side and a **Sachkonto** (contra account, Buchungskonto/Gegenkonto) on the other. Basiskonten are Zahlungskonten (Bank, Kasse, **Auslagenkonto**, **Verrechnungskonto**) and Debitoren-/Kreditorenkonten; Sachkonten are usually Aufwands-/Erlöskonten or balance-sheet accounts.
- BB derives Soll/Haben from the money flow: money **in** on the Basiskonto → Basiskonto in **Soll**; money **out** → Basiskonto in **Haben**. The words Soll/Haben appear only in *Erweitert*.
- In a **Splitbuchung / Teilbuchung**, a **negative** partial amount flips the Soll/Haben side of that line. This is how Skonto, fees netted against revenue, or a supplier invoice netted against a customer payment are booked (example: customer pays EUR 50 net of a EUR 50 supplier invoice → line 2 "-50" on the expense account, line 1 becomes EUR 100 revenue).
- Direct booking **Basiskonto an Basiskonto** is blocked; transfers go through **Geldtransit** `1360 | 1460` (§7.7).
- Umsatzsteuer-/Vorsteuerkonten cannot be booked directly; they are filled only via the Steuerschlüssel on a posting (§3.5).

Source: Informationen zu Basiskonten und zur Einrichtung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465877273757
Source: Verschiedene Buchungskonten oder Steuersätze bebuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11321777612957

### 1.3 Eingangs-/Ausgangsbelege, Gutschriften, Rechnungskorrekturen

- Upload Ausgangsrechnungen only into the Ausgangsbelege area; an Ausgangsrechnung filed as Eingangsbeleg is wrong.
- **Gutschrift** in BB's sense is a document with opposite sign to an invoice. API receipt `type`: `invoice inbound` (Eingangsrechnung), `invoice outbound` (Ausgangsrechnung), `credit inbound` (Eingangsgutschrift § 14 UStG), `credit outbound` (Ausgangsgutschrift § 14 UStG). A negative `amount` on upload "indicates a reversed payment".
- A **Stornorechnung / Rechnungskorrektur** created in BB's invoicing module is a normal invoice with a negative total; BB labels it "Rechnungskorrektur" automatically. With Debitoren active, assign it to the customer's Debitorenkonto; at payment, assign both the original and the correction to the Zahlung.
- The "Belege zuweisen" dialog defaults to Eingangsbelege for outgoing payments and Ausgangsbelege for incoming payments; for opposite-sign documents (Gutschriften, Rechnungskorrekturen) change the filter. Filter also defaults to *unbezahlt*; a Beleg already assigned once is "bezahlt" and only appears under *alle*.

Source: Ausgangsrechnungen in der Kasse verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11419453337373
Source: Stornorechnungen oder Rechnungskorrekturen erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454359040925
Source: Belege manuell einer Zahlung zuweisen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443312093725

### 1.4 "Beleg erzeugt Zahlung"

- Option on manual Basiskonten (Kasse, Auslagenkonto, Verrechnungskonto, Prepaid-Konto, manual bank account); **on by default** for manually created payment accounts. Assigning an Eingangsbeleg to such an account creates a Zahlung with the Beleg's amount and the **Rechnungsdatum as Zahlungsdatum**, plus a Buchungsvorschlag. Correcting the Beleg data later updates the generated Zahlung.
- Exists only for **Eingangsbelege**; incoming payments for Ausgangsrechnungen on Kasse/EÜR-Verrechnungskonto must be added manually.
- Belege that generated a Zahlung this way **cannot** be booked kreditorisch (no open item ever existed). Workaround for cash-paid invoices that must be kreditorisch: upload with "automatische Kontenzuordnung", book the Kreditor, then add the Kasse-Zahlung manually.
- On a revisionssicheres Kassenkonto the generated Zahlung is written at the moment of confirmation, not in Belegdatum order — disable the option if chronological order cannot be guaranteed.
- API: `accounts/add` parameter `receipt_creates_transaction` (boolean, default false); `receipts/upload`/`receipts/add` parameter `account` assigns the Beleg to a payment account on upload.

Source: Zahlung durch Belegzuweisung erzeugen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11444714286621
Source: Mit Debitoren und Kreditoren buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11452107588893
Source: Revisionssicheres Kassenbuch einrichten und auswerten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11467646903069

### 1.5 Buchungsvormerkung (EÜR)

- For Einnahmen-Überschuss-Rechner (who book only Zahlungen): when checking an unpaid Beleg you can record a **Buchungsvormerkung** (posting reservation) at the Beleg. It is not a posting; it becomes the Buchungsvorschlag on the Zahlung once the Beleg is linked to it.
- Applied only when Zahlungsbetrag and Rechnungsbetrag match **exactly**. Existing Buchungsvormerkungen take precedence over Automatisierungsregel proposals.

Source: Buchungsvormerkungen erfassen (für EÜR) — https://wissen.buchhaltungsbutler.de/hc/de/articles/16331667205917
Source: Mit Automatisierungsregeln arbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421057914781

### 1.6 Belegmatching and Magic Flow

- Matching runs whenever a new Zahlung or Beleg arrives. Pre-selection: up to 1,000 Belege whose Rechnungsdatum is at most **90 days before / 30 days after** the Zahlungsdatum; ranked by (1) amount + Rechnungsnummer alone in the Verwendungszweck, (2) amount + Gegenpartei, (3) amount. A "Rater" scores the candidates.
- No match when: amounts differ (foreign-currency invoices and Skonto payments cannot be matched), Beleg outside the date window, Beleg not in pre-selection, OCR misread, or the Zahlung is already booked. Several Belege to one Zahlung (Sammelzahlung) is never automatic.
- **Payment Reference**: for PayPal/Amazon/Stripe payments BB stores the provider's reference. A Beleg matches 100 % if it carries the same reference. On uploaded documents the reference must follow one of the signal words `Verwendungszweck`, `Purpose`, `Zahlungs-ID`, `Transaction-id`, `Referenz-Nr`, `Reference-ID`, `Referenz`, `Reference`, `Zahlungsreferenz`, separated by at most a punctuation mark and a space ("Referenz: 123abc" ok; "Referenz123abc" not). Via API/CSV pass it in `payment_reference` on both `transactions/add` and `receipts/upload`/`invoices/create` (Amazon order id, PayPal and Stripe transaction id supported).
- **Magic Flow** (top right of the Beleg detail view): offered when OCR has read the Beleg and a Zahlung was auto-assigned; one click confirms both the assignment and the Buchungsvorschlag.
- Wrong Kreditor/Debitor assignment usually means your own IBAN/USt-ID is missing from *Unternehmensdaten* (they act as exclusion criteria) or was entered on a Kreditor's master data.

Source: Belegmatching verstehen und optimieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443781087389
Source: Buchhaltung und Zahlungszuordnung am Beleg — https://wissen.buchhaltungsbutler.de/hc/de/articles/16331531911837
Source: Belegzuordnung zu falschem Debitoren-/Kreditorenkonto — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421829670045

### 1.7 Automatisierungsregeln

- *Einstellungen → Automatisierungsregeln*. "Wenn/Dann" rules, applied **only to newly imported** Belege/Zahlungen, never retroactively. Rules for Eingangsrechnungen need Kreditoren active; for Ausgangsrechnungen, Debitoren.
- Criteria (AND-combined): Zahlung — Gegenpartei, Betrag, Verwendungszweck; Eingangsbeleg/Ausgangsrechnung — Gegenpartei, Rechnungsnummer, Betrag, Volltext. Operators: ist / ist nicht / enthält / enthält nicht (text), ist / ist nicht / größer als / kleiner als (Betrag), enthält / enthält nicht (Volltext).
- Actions: **Beleglos markieren** (Zahlung), **Kontieren auf** (books directly, button already green), **Buchungsvorschlag auf** (overrides the automatic proposal, still needs confirmation), **Teilbuchungsvorschlag auf** (up to 10 lines with account, text, USt, KSt, KSt2; amounts as fixed, percent or Restbetrag; only for Belege, requires Deb/Kred, not for foreign-currency Belege), **Kreditor zuweisen**, **Debitor zuweisen**.
- Practice: put "codes" in your own invoice layout (e.g. per OSS country) and key Volltext rules on them.

Source: Mit Automatisierungsregeln arbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421057914781

### 1.8 Kommentare, Aufgaben, Schnellfilter, Sammelfunktion

- **Kommentar**: free text on a Zahlung or Beleg; exported in the BB Standardformat column "Kommentar" and in `postings/get` field `comment`. Recommended for missing Belege ("describe the Geschäftsvorfall for the Steuerberater"). API: `comments/add` with `comment_text` (2–210 chars) and exactly one of `transaction_id_by_customer` / `receipt_id_by_customer`.
- **Aufgaben** (tasks): created from the context menu of a Zahlung or Beleg; tag users with `@`; open tasks blue, done grey; participants are notified by e-mail and in the Benachrichtigungscenter; filter by status. Visible only to roles that can see the underlying area. No API endpoint.
- **Schnellfilter**: saved filter presets in *Zahlungen*, *Belege*, *Erweitert*; per user, not shared. Key built-in filters: "Fehlender Beleg" and "Ungebucht" (Zahlungen), "Ungebucht" and "Duplikatsverdacht" (Belege), "Gelöschte Belege anzeigen".
- **Sammelfunktion** (bottom of Belege/Zahlungen lists): Bestätigen, Aufheben, Festschreiben, Aktualisieren (refresh proposals), Kontieren, Löschen; Belege additionally Überweisen, Zuweisen (Deb/Kred), Zuordnen (Eingang/Ausgang); Zahlungen additionally Beleglos.

Source: Fehlende Belege identifizieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443881408285
Source: Aufgaben — https://wissen.buchhaltungsbutler.de/hc/de/articles/20658552399261
Source: Schnellfilter - Vorlagen für Filter erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/21062365037981
Source: Hacks und Shortcuts mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11420828181277

### 1.9 UI term ↔ API term

| UI (German) | API v1 | Notes |
|---|---|---|
| Zahlung / Transaktion / Umsatz | `transaction` (`transactions/*`) | `amount` positive = incoming, negative = outgoing; `booking_date` `YYYY-MM-DD HH:II:SS` |
| Zahlungskonto / Basiskonto (Bank, Kasse, Auslagenkonto, Verrechnungskonto) | `account` (number, e.g. `1200`); created with `accounts/add` (`type`: `cash`, `bank/institution`, `other`) | `accounts/get` returns `name` + `postingaccount_number` of payment accounts only |
| Buchungskonto / Sachkonto / Gegenkonto | `postingaccount`, `postingaccount_number`, `postingaccount_debit`/`postingaccount_credit` (free posting) | Debitoren/Kreditoren are also `postingaccounts` (`settings/get/postingaccounts`, `all debtors`, `all creditors`) |
| Kreditor / Debitor | `creditor` / `debtor` (`settings/add/creditor`, `settings/add/debtor`); `creditor_debtor` on receipt upload | Sammelkonten `70000` / `10000` |
| Beleg / Eingangsbeleg / Ausgangsbeleg | `receipt`; `list_direction` `inbound` / `outbound` | `receipts/get` requires `list_direction` |
| Eingangsrechnung / Ausgangsrechnung / Eingangsgutschrift / Ausgangsgutschrift | `type` = `invoice inbound` / `invoice outbound` / `credit inbound` / `credit outbound` | |
| Buchung / Buchungssatz | `posting` (`postings/add/transaction`, `postings/add/receipt`, `postings/add/free`) | receipt postings only with Deb/Kred active |
| Teilbuchung / Splitbuchung | parallel arrays `postingaccounts[]`, `postingtexts[]`, `vats[]`, `amounts[]`, `cost_locations[]` | sum of `amounts` must equal the transaction/receipt amount; format `0000.00` |
| Erweitert / freies Buchen | `postings/add/free` | positive `amount` only; Soll/Haben explicit via debit/credit account |
| Steuersatz / Steuerschlüssel (BU) | `vat` (`19_pre`, `19_vat`, `0_none`, …, see §3.6); `tax_key` in `postings/get` = BU key | |
| Buchungstext | `postingtext` (≤ 128 chars) | UI keyword search in Buchungstext proposes accounts |
| Kostenstelle / KS, Kostenstelle 2 / KS2 | `cost_location`, `cost_location_two` (≤ 10 alphanumeric chars) | `cost-locations/*` endpoints |
| Nr. shown in the UI (Beleg-, Zahlungs-, Buchungsnummer) | `id_by_customer` | per-account counter; the internal `receipts_id`/`postings_id` are not exposed |
| Rechnungsnummer | `invoice_number` (upload, ≤ 60 chars) / `invoicenumber` (get, invoices) | DATEV "Belegfeld 1" |
| Gegenpartei / Rechnungssteller / Zahlungsempfänger | `counterparty` (receipt), `to_from` (transaction) | |
| Verwendungszweck | `purpose` (transaction, ≤ 500 chars on CSV import) | |
| Zahlungsreferenz / Payment Reference | `payment_reference` | matching key for PayPal/Amazon/Stripe |
| Rechnungsdatum / Belegdatum | `date` (receipt) | |
| Abweichendes Leistungsdatum | `date_delivery` (receipt), `date_of_supply` (invoices/create), `date_delivery` + `date_vat_effective` in `postings/get` | must not be after `date` (DATEV) |
| Fälligkeit | `date_payment_due` (receipt), `due_days` (invoice), `due_in_days` (creditor/debtor) | |
| bezahlt / unbezahlt | `payment_status` `paid` / `unpaid` (`receipts/get`) | "bezahlt" = assigned to a Zahlung |
| bestätigt / unbestätigt | no explicit field; `postings/unconfirm/*` removes an unfixed posting | |
| festgeschrieben / nicht festgeschrieben | `posting_status` `fixed` / `unfixed`; field `fixed` `"1"`/`"0"` in `postings/get` | no API call fixes postings |
| Storno / Generalumkehr | `postings/cancel` (deletes unfixed, reverses fixed) | |
| Gelöschte Belege | `receipts/delete/id_by_customer`, `receipts/restore/id_by_customer`, `deleted=true` filter | soft delete only |
| Kommentar | `comments/add` | |
| Offene-Posten-Buchhaltung (OI) | `oi_receipts_ids_by_customer[]` on `postings/add/transaction` (required when OI is active) | |
| BWA / SuSa / Kontenblatt | `reports/create/bwa`, `reports/create/sums`, `reports/get/bwa`, `reports/get/sums`, `reports/get/sums/ledger` | asynchronous, one report of each type at a time |
| Rechnung / Gutschrift / Angebot (Faktura) | `invoices/create` (`type` `invoice` / `credit` / `offer`), `invoices/create/draft`, `invoices/create/e-invoice` | |
| Beleg erzeugt Zahlung | `receipt_creates_transaction` (`accounts/add`) | |
| Revisionssicheres Kassenkonto | `is_revision_safe` (`accounts/add`, cash only) | |
| E-Rechnung (ZUGFeRD / XRechnung) | `e_invoice_type` `0` pdf / `1` ZUGFeRD / `2` XRechnung; `file_type` `pdf` / `xml` | metadata parameters are ignored on e-invoice upload |

Source: Einrichtung der API-Schnittstelle — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468075328797
Source: API spec 1.9.1 (`/receipts/upload`, `/transactions/add`, `/postings/add/*`, `/accounts/add`, `/settings/add/creditor`) — https://app.buchhaltungsbutler.de/docs/api/v1/

---

## 2. Lifecycle and irreversibility

### 2.1 Status chain

1. **Ungebucht / kein Vorschlag** — grey button: no account assigned.
2. **Buchungsvorschlag, unbestätigt** — blue button: BB (or a rule with "Buchungsvorschlag auf") proposed an account; not yet a posting for evaluations.
3. **Gebucht / bestätigt** — green button: confirmed posting. Only confirmed postings enter BWA, EÜR, GuV, SuSa, Bilanz, USt.-VA and the Controlling Dashboard. Automation "Kontieren auf" lands here directly. API `postings/add/*` creates postings that count as confirmed *(inferred: the spec has no proposal state and `unconfirm/*` reverses them)*.
4. **Festgeschrieben** (fixed) — green lock. Done in *Abschluss → Jetzt festschreiben* for a period, or via Sammelfunktion "Festschreiben". The posting gets a `date_fixed` timestamp and a gap-free, year-spanning **Journalnummer**. There is no API call for fixing; it is a UI action.

Beleg status is separate: **ungeprüft** → geprüft; **unbezahlt** → **bezahlt** (assigned to a Zahlung); **ungebucht** → gebucht. A Beleg counts as "gebucht" as soon as the Zahlung it is assigned to is booked — except when that Zahlung was booked *only* against a Debitor/Kreditor, in which case the Beleg stays "ungebucht" until booked itself.

Source: Buchungssätze und Belegbilder in unterschiedlichen Formaten exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445407988637
Source: Schritte, um die Buchhaltung am Monatsende fertigzustellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421107352989
Source: GoBD konformes Arbeiten mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432424987037

### 2.2 What Festschreibung blocks

- **Zahlungen** with a fixed posting cannot be deleted ("aus technischen Gründen").
- **Belege** with a fixed debitorische/kreditorische Buchung can only be deleted after the posting is removed (which generates a Stornobuchung that survives the deletion).
- **Konten** (Basiskonten, Bank, Deb/Kred, individual Sachkonten) with fixed postings cannot be deleted; hide them instead.
- **Kontenrahmenwechsel** is impossible once anything is fixed (§5.5).
- Accounts with *confirmed but unfixed* postings can be deleted only after the postings are set back to unbestätigt.
- Everything else (Besteuerungsart, Belegzuweisung, Standard-Steuersatz) stays editable and re-computes evaluations retroactively — see §4.

Source: Löschen von festgeschriebenen Zahlungen und Belegen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11422252682781
Source: Basiskonten ausblenden oder löschen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454462250909
Source: Kontenrahmen und Sachkontenlänge wählen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465983139101

### 2.3 Correcting mistakes at each stage

| Stage | UI | API |
|---|---|---|
| Wrong proposal, unbestätigt | overwrite account / vat, confirm | `postings/add/*` (creates the confirmed posting) |
| Confirmed, not fixed | "Aufheben" (Buchungsbestätigung aufheben) → re-book; Zahlung/Beleg can still be deleted | `postings/unconfirm/transaction` / `unconfirm/receipt` / `unconfirm/free`, then add again; `postings/cancel` deletes an unfixed posting |
| Fixed | Storno via **Generalumkehr**: save the Zahlung with empty Buchungskonto (BB generates the Stornobuchung and leaves the Zahlung open), or book a second Zahlung with opposite sign and net both on Interimskonto `1590 \| 1370`; at a Beleg: "Buchung bearbeiten" → "Buchung entfernen" → confirm (Stornobuchung is created) | `postings/cancel` on a fixed posting creates a **reversal posting**; then post anew |
| Wrong Beleg uploaded | delete (soft) → filter "Gelöschte Belege anzeigen" → restore possible | `receipts/delete/id_by_customer`, `receipts/restore/id_by_customer` |
| Duplicate Zahlung imported | delete via context menu / Sammelfunktion (only if not fixed) | no API delete for transactions |
| Wrong Kontenrahmen | only via support and only while no posting is fixed (full account reset, §5.5); otherwise export, remap in Excel, import into a new account | — |
| Wrong Sachkontenlänge | not changeable at all ("derzeit leider nicht möglich"); export, remap, import into a new account | — |

- **GU keys**: on a Storno of a fixed posting BB exports the **Generalumkehrschlüssel** (GU, e.g. 29 instead of BU 9) so that third-party systems import it as a negative amount with the same Soll/Haben side; SuSa values are reduced rather than cumulated (§3.1).
- Exports and evaluations warn about ungebuchte Geschäftsvorfälle when a Zahlung was left open after a Storno.
- If the USt.-VA for the period was already filed, corrections require a **berichtigte USt.-VA** (§8.3).

Source: Löschen von festgeschriebenen Zahlungen und Belegen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11422252682781
Source: Logik der Steuerschlüssel, Sachverhalte §13b & Automatikkonten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408521543581
Source: API spec 1.9.1 (`/postings/cancel`, `/postings/unconfirm/*`) — https://app.buchhaltungsbutler.de/docs/api/v1/

### 2.4 GoBD implications

- Uploaded files are stored unchanged (original + OCR-optimised PDF) with `guid`, `receipts_id`, `date_uploaded`, `filename_original` on object storage in German AWS data centres (Frankfurt). Deleting a Beleg is never physical; deleted documents remain visible via filter. Consumed Belegkontingent is not refunded by deleting.
- Postings carry `guid`, `postings_id`, `date_last_action`, `date_fixed`. The journal number is gap-free and continues across years. Ist-Versteuerung re-postings ("nicht fällig" → "fällig") get the journal number with suffix `-1`, `-2`, …
- The Finanzverwaltung expects postings to be fixed **before** the USt.-VA is transmitted (Festschreibedatum older than Übermittlungsdatum). The USt.-VA screen warns about unfixed postings.
- The offene-Posten feature binds a Beleg to its Zahlung independently of fixing: while the Zahlung is booked, the Beleg cannot be unassigned; unbook first (Beleg detail → "Zahlung buchen").
- BB has no Wirtschaftsprüfer-Testat for the archive; keep paper originals as backup.
- Data retention: 10 years after cancellation, the account is only deactivated; reactivation for export/audit is free for 3 days.
- Bank data via scraping interfaces is not guaranteed complete; reconcile against statements.

Source: GoBD konformes Arbeiten mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432424987037
Source: Warn- und Fehlermeldungen bei der Umsatzsteuer-Voranmeldung (USt-VA) — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432104747677
Source: Zusätzliche Belege buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11441898777757
Source: Kündigung der Services & Aufbewahrungsfristen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11441697058205

---

## 3. Steuerschlüssel (tax keys)

### 3.1 BU/GU code list

**BU** = Buchungsschlüssel used on regular postings; **GU** = Generalumkehrschlüssel used when a fixed posting is reversed (exported as negative amount, same Soll/Haben side). Between 01.07.2020 and 31.12.2020 the same codes booked 16 %/5 % instead of 19 %/7 %.

| Steuerschlüssel (UI label) | BU | GU |
|---|---|---|
| 7% UmSt. | 2 | 22 |
| 19% UmSt. | 3 | 23 |
| 7% VSt. | 8 | 28 |
| 19% VSt. | 9 | 29 |
| 7% i.g.E. (USt./VSt.) | 18 | 68 |
| 19% i.g.E. (USt./VSt.) | 19 | 69 |
| §13b 19% UmSt./VSt. | 94 | 34 |
| 7% i.g.E. UmSt. aber keine VSt. | 12 | 62 |
| 19% i.g.E. UmSt. aber keine VSt. | 13 | 63 |
| §13b 19% UmSt. aber keine VSt. | 95 | 35 |
| 7% aufzuteilende VSt. | 98 | 38 |
| 19% aufzuteilende VSt. | 99 | 39 |
| 7% i.g.E. UmSt./aufzuteilende VSt. | 57 | 77 |
| 19% i.g.E. UmSt./aufzuteilende VSt. | 58 | 78 |
| §13b 19% UmSt./aufzuteilende VSt. | 59 | 79 |

Additional keys introduced 01.07.2020 (BU/GU valid from 01.01.2021 for the reduced rates): 5% UmSt. 4/24, 16% UmSt. 5/25, 5% VSt. 6/26, 16% VSt. 7/27, 5% i.g.E. 16/66, 16% i.g.E. 17/67, §13b 16% UmSt./VSt. 50/70, 5% i.g.E. ohne VSt. 14/64, 16% i.g.E. ohne VSt. 15/65, §13b 16% ohne VSt. 51/71, 5% aufzut. VSt. 96/36, 16% aufzut. VSt. 97/37, 5% i.g.E./aufzut. VSt. 53/73, 16% i.g.E./aufzut. VSt. 54/74, §13b 16%/aufzut. VSt. 52/72.

- Keys **57, 58, 59** (and the 50-range keys) are BB-defined, not DATEV-defined; the Steuerberater must create them in the Kanzleisoftware before importing.
- For **Automatikkonten** the export carries **no** BU key; the account itself implies the tax.
- Export column **Sachverhalt L+L**: BB always writes `7` next to key 94 (sonstige Leistung of an EU business). Other §13b Sachverhalte (1 Drittland, 4 Bauleistungen, …) are only representable via Automatikkonten.
- Aufwandskonten accept only Vorsteuer keys, Ertragskonten only Umsatzsteuer keys; BB restricts the dropdown per account. Since the 2020 change the standard keys are labelled "19/16%" / "7/5%" (implicit, date-dependent); explicit "old" keys sit under "alte Steuersätze".

Source: Logik der Steuerschlüssel, Sachverhalte §13b & Automatikkonten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408521543581
Source: Software-Änderungen | Mehrwertsteuersenkung 2020 — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282864819357
Source: Buchungssätze und Belegbilder in unterschiedlichen Formaten exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445407988637

### 3.2 Which key for which situation

- **German VAT shown** on the invoice → `7%/19% VSt.` (purchases) or `7%/19% USt.` (sales).
- **No tax, or foreign tax you cannot reclaim in Germany** → **"keine USt."**. The help center's explicit example: an invoice from a large Irish ad platform showing 19 % Irish VAT is booked with "keine Steuer" — the gross amount is the expense. (Ask the vendor to re-issue B2B with reverse charge if you have a USt-ID.)
- **i.g.E.** (innergemeinschaftlicher Erwerb, `I.g.E. 19%/7% USt./VSt.`): **goods** bought from an EU supplier under reverse charge — not for services. BB books USt and VSt simultaneously (Kz. 89/93 and 61); the result nets to zero except for rounding (USt on the rounded-down Umsatz, VSt to the cent). Example from the source: fish delivered by a Paris wholesaler to a Berlin restaurant → `i.g.E. 7% USt./VSt.`. Typical accounts: `3425 | 5425` "Innergemeinschaftlicher Erwerb 19% VSt. und 19% USt." (Automatikkonto) or a plain Wareneingang `3200 | 5200` with the i.g.E. key; tax accounts `1574 | 1404` and `1774 | 3804`.
- **§13b** (`§13b 19% USt./VSt.`): **sonstige Leistungen** (services) received from a business in another EU state where you owe the VAT — e.g. search-engine marketing bought from an Irish company. Reported in Kz. 46/47 (USt) and 67 (VSt). Preferred account: Automatikkonto `3123 | 5923` *(SKR04 number inferred)* "Leistungen eines im anderen EG-Land ansässigen Unternehmens 19% VSt/19% USt"; alternatively an ordinary expense account (e.g. 4600 Werbekosten) with the §13b key. Tax accounts `1577 | 1407` and `1787 | 3837`.
- **Other §13b cases** (Drittland services, Bauleistungen, Gebäudereinigung, Gas/Strom, Mobilfunk, Schrott, …) cannot be expressed via the key; book them on the DATEV **Automatikkonto** defined for that Sachverhalt, e.g. `3125 | 5925` "Leistungen eines im Drittland ansässigen Unternehmers 19% VSt. und 19% USt." (a US SaaS vendor invoicing without VAT), `3145 | 5945` (same, ohne Vorsteuer), `3120 | 5920` "Bauleistungen eines im Inland ansässigen Unternehmers". These map to Kz. 84/85 with VSt in Kz. 67. Find them via the Stichwortverzeichnis. The API additionally exposes explicit codes `19_both_511` / `19_both_6511` for the Drittland case (§3.6).
- **Kleinunternehmer mit USt-ID**: key 95 (§13b USt, no VSt) is only available with that setting; CSV imports containing key 95 fail otherwise.
- Account `3165 | 5965` "Leistungen nach §13b UStG ohne Vorsteuerabzug" cannot be evaluated correctly in the USt.-VA; BB warns and recommends filing that period via ELSTER manually.

Source: Logik der Steuerschlüssel, Sachverhalte §13b & Automatikkonten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408521543581
Source: Reverse-Charge-Verfahren: So buchen Sie sonstige Leistungen aus der EU (wiki) — https://www.buchhaltungsbutler.de/wiki/reverse-charge-eu-buchen/
Source: Reverse Charge Drittland (wiki) — https://www.buchhaltungsbutler.de/wiki/reverse-charge-drittland-buchen/
Source: Innergemeinschaftlicher Erwerb (wiki) — https://www.buchhaltungsbutler.de/wiki/buchungssatz-lieferungen-eu/
Source: Importfehler bei CSV-Dateien — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431949907741
Source: Warn- und Fehlermeldungen bei der Umsatzsteuer-Voranmeldung (USt-VA) — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432104747677

### 3.3 Automatikkonten

- A DATEV **Automatikkonto** carries its Steuersatz in the name ("… 19/16% Vorsteuer", "Umsätze/Erlöse 19/16% USt.") and can only be booked with that implicit key; the dropdown offers nothing else. In DATEV's Kontenrahmen they are marked AV (automatische Vorsteuer) / AM (automatische Umsatzsteuer).
- Consequences: to book **without** tax (Eigenbeleg, foreign VAT) use the non-automatic sibling (`3200 | 5200` Wareneingang instead of `3400 | 5400`; `8200 | 4200` instead of `8400 | 4400`). Explicit old rates (19 % after 01.07.2020) also need the non-automatic account.
- When creating an individual Sachkonto, choosing an Automatikkonto as **Vorlagekonto** copies the tax automatic; keep the rate in the new name. For Dreiecksgeschäft and EU-Neufahrzeug the DATEV Automatikkonten `3553 | 5553` and `3440 | 5440` are deactivated in BB because they would key the tax wrongly (§7.16, §7.17).
- CSV import: postings on Automatikkonten must carry **no** BU key (or 0); otherwise "Der angegebene Steuerschlüssel wird nicht unterstützt".
- API error codes 27/16/24 ("the account … must be posted with vat option …") are the Automatikkonto check.

Source: Individuelle Sachkonten anlegen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454526317085
Source: Eigenbelege — https://wissen.buchhaltungsbutler.de/hc/de/articles/20426914295453
Source: Importfehler bei CSV-Dateien — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431949907741
Source: Software-Änderungen | Mehrwertsteuersenkung 2020 — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282864819357

### 3.4 Kennziffern of the USt.-VA

- Postings with a **USt key** are classified by the key regardless of account; the Umsatz is back-computed from the booked tax and rounded down. 19% USt → **Kz. 81**; 7% USt → **Kz. 86**; i.g.E. 19% → Kz. 89 (USt) + 61 (VSt); i.g.E. 7% → Kz. 93 + 61.
- Postings with a **VSt key**: 19%/7% VSt → **Kz. 66**; §13b 19% USt./VSt. → **Kz. 46** (USt) + **Kz. 67** (VSt), unless the account forces another mapping.
- **Account-driven** mappings (excerpt; full table in the source): `8336 | 4336` sonstige Leistungen EU §13b → Kz. 21; `8125 | 4125` steuerfreie i.g. Lieferungen → Kz. 41; `8120 | 4120` Ausfuhrlieferungen Drittland and `8150 | 4150` sonstige steuerfreie Umsätze → Kz. 43; `8320 | 4320` Lieferungen an Privat im anderen EU-Land, `8338 | 4338` Dienstleistungen Drittland steuerbar, `8339 | 4339` Dienstleistungen EU nicht steuerbar → Kz. 45; `8100/8105/8110 | 4100/4105/4110` steuerfrei ohne VSt → Kz. 48; `8337 | 4337` Dienstleistungen DE §13b → Kz. 60; `1588 | 1433` Einfuhrumsatzsteuer → Kz. 62; `3120 | 5920`, `3125 | 5925`, `3145 | 5945` → Kz. 84; `3550 | 5550` steuerfreier i.g.E. → Kz. 90; `1781 | 3830` 1/11 Sondervorauszahlung → Kz. 39 (other USt payments on `1780 | 3820` are not in the VA).
- The mapping of a Konto to a Kennziffer **cannot be changed** by the user. Individual accounts inherit the mapping of their Vorlagekonto.
- **ZM** consistency: L (i.g. Lieferung) = Kz. 41, S (sonstige Leistung) = Kz. 21; values must agree.

Source: Buchungskonten den Kennziffern der USt.-VA zuordnen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11472964130461
Source: Zusammenfassende Meldung (ZM) erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473312092445

### 3.5 Aufzuteilende Vorsteuer and the tax accounts

- With **aufzuteilende Vorsteuer** keys the input tax is parked on dedicated Forderungskonten; at year end the deductible share is re-booked in one sum to "Abziehbare Vorsteuer". Use cases: partly tax-free business, mixed private use (Fahrtenbuch).
- The automatic USt/VSt accounts that BB fills via the Steuerschlüssel are **gesperrt** (among them SKR03 USt `1771–1779, 1785–1787` and VSt `1572, 1574, 1577–1579, 1589` | SKR04 USt `3801–3809, 3813, 3815, 3835–3838` and VSt `1402, 1404, 1407–1409`; full list in §5.4): never book them directly, never import postings on them, no Saldovortrag onto them. The payment/clearing accounts `1780 | 3820`, `1781 | 3830`, `1789 | 3840`, `1790 | 3841` and the plain Vorsteuer account `1570 | 1400` are bookable (§3.4, §7.13, §7.19). All USt/VSt accounts are zeroed at the start of each Wirtschaftsjahr; carry the balance manually via `1790 | 3841` (§7.13).

Source: Logik der Steuerschlüssel, Sachverhalte §13b & Automatikkonten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408521543581
Source: Individuelle Sachkonten anlegen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454526317085
Source: Buchungssätze im (DATEV) CSV-Format importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11446480380189

### 3.6 API `vat` codes ↔ UI label ↔ situation

Codes and labels verbatim from the API spec (`postings/add/free`, `postings/add/transaction`, `postings/add/receipt`). BU keys are taken from §3.1 where the label matches; otherwise *(inferred)*. For `postings/add/transaction` and `postings/add/receipt` the split `amounts` must sum to the (gross) transaction/receipt amount (errors 27/37), so they are gross and BB derives net and tax from the code. Whether `postings/add/free` `amount` is gross or net is not stated in the spec *(inferred: gross, by analogy with the UI)* — verify with a test posting before relying on it.

| `vat` | UI label (spec) | Tax situation | Likely BU | Typical cases |
|---|---|---|---|---|
| `0_none` | keine Ust. | no German tax booked | none / 0 | foreign VAT that cannot be reclaimed (Irish 23 %, US sales tax) → gross is the expense; steuerfreie/nicht steuerbare items (insurance, bank fees, Beiträge, Eigenbeleg); Deb/Kred clearing; own sales to EU business customers on `8336 \| 4336` (reverse charge) or Drittland customers on `8338 \| 4338`; Kleinunternehmer sales |
| `19_vat` | 19% Ust. | Umsatzsteuer 19 % | 3 | own domestic sales at 19 % (`8400 \| 4400`) |
| `7_vat` | 7% Ust. | Umsatzsteuer 7 % | 2 | own reduced-rate sales (`8300 \| 4300`) |
| `19_pre` | 19% Vst. | Vorsteuer 19 % | 9 | domestic supplier invoice with 19 % German VAT |
| `7_pre` | 7% Vst. | Vorsteuer 7 % | 8 | domestic invoice at 7 % (Bahn, Bücher, Hotelübernachtung) |
| `19_both_1` | §13b 19% USt./VSt. | reverse charge, USt + VSt (generic §13b key, Sachverhalt 7) | 94 | EU B2B service (SaaS from an Irish or Luxembourg vendor, no VAT, your USt-ID on the invoice) when no Automatikkonto is used |
| `19_both_506` | §13b 19% USt./VSt. (EU §13b Abs. 1) | reverse charge on sonstige Leistung of an EU business | 94 *(inferred)* | same as above; preferred explicit code for EU B2B SaaS/ads |
| `19_both_6506` | §13b 19% USt. (EU §13b Abs. 1, ohne VSt.) | §13b USt owed, no VSt deduction | 95 *(inferred)* | EU B2B service received by a business without Vorsteuerabzug (Kleinunternehmer mit USt-ID, steuerfreie Umsätze) |
| `19_both_511` | §13b 19% USt./VSt. (Drittland §13b Abs. 2 Nr. 1) | reverse charge on service of a non-EU business | 94 with L+L Sachverhalt 1 *(inferred)*; account `3125 \| 5925` gives Kz. 84 | US SaaS/API vendor invoicing without VAT |
| `19_both_6511` | §13b 19% USt. (Drittland §13b Abs. 2 Nr. 1, ohne VSt.) | as above, no VSt | 95 *(inferred)*; account `3145 \| 5945` | non-EU service, recipient not entitled to Vorsteuer |
| `19_both_6501` | §13b 19/16% USt. (ohne VSt.) | §13b USt only, implicit rate | 95 *(inferred)* | legacy/implicit-rate variant of `19_both_6506`/`6511` |
| `19_both_2` | I.g.E. 19% USt./VSt. | innergemeinschaftlicher Erwerb 19 % | 19 | goods bought from an EU supplier (hardware from an EU shop, B2B with USt-ID) |
| `7_both` | I.g.E. 7% USt./VSt. | innergemeinschaftlicher Erwerb 7 % | 18 | EU goods at reduced rate (books, food) |
| `19_both_1_no_pre` | §13b 19/16% USt. | §13b USt, no VSt, implicit rate | 95 *(inferred)* | as `19_both_6501` |
| `19_both_2_no_pre` | i.g.E. 19/16% USt. | i.g.E. USt, no VSt | 13 *(inferred)* | EU goods purchase without Vorsteuerabzug |
| `7_both_no_pre` | i.g.E. 7/5% USt. | i.g.E. 7 % USt, no VSt | 12 *(inferred)* | as above, reduced rate |
| `19_pre_app` | 19/16% Aufz. VSt. | aufzuteilende Vorsteuer 19 % | 99 *(inferred)* | mixed-use costs (Fahrtenbuch fuel) |
| `7_pre_app` | 7/5% Aufz. VSt. | aufzuteilende Vorsteuer 7 % | 98 *(inferred)* | mixed-use costs at 7 % |
| `19_both_app_1` | §13b 19/16% USt./Aufz. VSt. | §13b with aufzuteilender VSt | 59 *(inferred)* | EU service for mixed use |
| `19_both_app_506` | §13b 19/16% USt./Aufz. VSt. (EU §13b Abs. 1) | as above, EU explicit | 59 *(inferred)* | |
| `19_both_app_511` | §13b 19/16% USt./Aufz. VSt. (Drittland §13b Abs. 2 Nr. 1) | as above, Drittland | 59 *(inferred)* | |
| `19_both_app_2` | i.g.E. 19/16% USt./Aufz. VSt. | i.g.E. with aufzuteilender VSt | 58 *(inferred)* | |
| `7_both_app` | i.g.E. 7/5% USt./Aufz. VSt. | i.g.E. 7 % with aufzuteilender VSt | 57 *(inferred)* | |

Implicit-rate rows (spec labels "19/16%" / "7/5%") carry a BU marked *(inferred)*: no §3.1 label matches them verbatim, the mapping holds only by rate. For Leistungs-/Buchungsdatum 01.07.–31.12.2020 these codes booked 16 %/5 % under the same upper-block BU, while the lower-block keys (51, 15, 14, 97, 96, 52, 54, 53) then marked the old higher rates; only from 01.01.2021 do the lower-block keys belong to the explicit 16 %/5 % codes (§3.1).

Behavioural notes from the spec:
- Error 27/16/24 "the account must be posted with vat option X" → Automatikkonto; pass the code it demands (or none is not allowed — `vat` is required).
- Error 33/19/28 "vat option unavailable due to current settings" → e.g. `19_both_6506` without Kleinunternehmer setting, or `_app` codes when aufzuteilende Vorsteuer is not enabled *(inferred)*.
- Error 34/20/29 "vat option unavailable with 'not liable to sales tax' setting" → account is set to Kleinunternehmer/not USt-pflichtig; only `0_none` works.
- Error 42 (receipt postings) "the vat option is not available for this date" → rate/date mismatch (2020 rates).
- Aufwandskonto + `19_vat` or Ertragskonto + `19_pre` → error 29/17/26 "must be posted with/without …".

Source: API spec 1.9.1 (`/postings/add/free`) — https://app.buchhaltungsbutler.de/docs/api/v1/
Source: Logik der Steuerschlüssel, Sachverhalte §13b & Automatikkonten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408521543581
Source: Buchungskonten den Kennziffern der USt.-VA zuordnen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11472964130461

---

## 4. Soll- vs Ist-Versteuerung

### 4.1 Definitions and setting

- **Soll-Versteuerung** (accrual VAT, "nach vereinbarten Entgelten"): USt is due at the Leistungsdatum. **Ist-Versteuerung** ("nach vereinnahmten Entgelten"): USt is due when payment is received. **Vorsteuer** is identical under both: always at the Rechnungsdatum.
- Set under *Einstellungen → Steuerliche Einstellungen → Besteuerungsart*. Soll-Versteuerer should activate **Debitoren** so that revenue and USt are booked at the Beleg (Rechnungs-/Leistungsdatum); otherwise USt is reported in the payment period and possibly too late.
- The Besteuerungsart only matters for **debitorisch** booked Ausgangsrechnungen. Without Debitoren, USt always follows the Zahlungsdatum.

Source: Erklärungen zu Soll- und Ist-Versteuerung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445000762781
Source: Grundlagen zur Arbeit mit Debitoren und Kreditoren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11451892160797

### 4.2 Switching and its effects

- BB computes due USt **fictitiously at evaluation time** from the current setting; nothing is hard-booked. A switch is therefore possible any time and **retroactively changes** USt.-VA, SuSa/Kontenblätter and GDPdU output for past periods. Always evaluate a period with the Besteuerungsart that applied then; same for GDPdU exports.
- Switching Ist → Soll: activate Debitoren/Kreditoren. Open items across a year-end: ask the Steuerberater.
- Changing the **Standard-Steuersatz** (Einstellungen → Buchhalterische Einstellungen → Standardkonto für Einnahmen) likewise recomputes past Ist-Versteuerung postings.

Source: Auswirkungen eines Wechsels von Ist- zu Soll-Versteuerung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408276094237
Source: GDPdU-Export für Betriebsprüfungen erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445774450973

### 4.3 Abweichendes Leistungsdatum

- Entered at the Beleg next to the Rechnungsdatum; **may not be later than the Rechnungsdatum** (DATEV compatibility; use the Leistungsdatum as Rechnungsdatum in that case). OCR does not read it; enter manually or pass `date_delivery` via API. `invoices/create` `date_of_supply` in `YYYY-MM-DD` becomes the Beleg's date_delivery.
- Considered **only for debitorisch/kreditorisch booked Belege**. Effects: BWA by Leistungsdatum (Rechnungsdatum shown); USt.-VA: USt of Ausgangsrechnungen at Leistungsdatum (if ≤ Rechnungsdatum), VSt always at Rechnungsdatum; ZM always Rechnungsdatum (for services change the Rechnungsdatum manually to the ZM-relevant date); SuSa/Kontenblätter always Rechnungsdatum, so they can differ from the USt.-VA — the USt.-VA is the correct one. `reports/create/sums` accepts `base: date_delivery_else_date` to evaluate by Leistungsdatum.
- For a Zahlung merely linked to a Beleg (EÜR) the **Zahlungsdatum** decides the rate; the Leistungsdatum is ignored.

Source: Auswirkungen eines abweichenden Leistungsdatums — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408182136861
Source: Software-Änderungen | Mehrwertsteuersenkung 2020 — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282864819357
Source: Belege hochladen und verarbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443147763101

### 4.4 Debitoren-Buchhaltung as Ist-Versteuerer

- Booking a Beleg debitorisch as Ist-Versteuerer posts USt to **"Umsatzsteuer nicht fällig"** (e.g. `1766` 19 %). When the Zahlung is booked against the Debitor with the Beleg assigned, BB re-posts in the background from "nicht fällig" to "fällig" (`1776 | 3806`), journal suffix `-1`.
- Payment against a Debitor **without** Beleg → USt at the **Standard-Steuersatz** of the Standarderlöskonto; with Beleg → the Beleg's rates. Unterzahlungen are split pro rata across the Beleg's rates; **Überzahlungen** at the Standard-Steuersatz. A payment against a Debitor cannot be given a different rate manually.
- Belege are matched to split lines **FIFO**: first assigned Beleg feeds the first Teilbuchung, then the remainder. Two Belege with different rates on one Zahlung therefore compute wrongly — split the Zahlung (delete and re-create manually) so each Beleg has its own Zahlung; BB recommends one Beleg per Zahlung anyway. Several Belege on one Zahlung only if same rate.
- Debitorisch booked Ausgangsrechnungen **cannot be cleared in Erweitert** (no USt re-posting). Workaround: sonstiges Basiskonto → manual Zahlung at the desired date → assign Beleg → clear the Debitor → second manual Zahlung to zero the Basiskonto → book that against the originally intended account (e.g. erhaltene Anzahlungen).
- **Forderungsverlust**: upload the invoice again labelled "Forderungsausfall", dated at the write-off date, **negative** amount, same Debitor, account Forderungsverluste with 19 % USt → Debitor cleared, "USt nicht fällig" released.
- The Gutschrift workaround for Ist-Versteuerer (§7.6): create the clearing Zahlung at the **Gutschriftsdatum**, not the Rechnungsdatum, so USt becomes due with the credit note.

Source: Besonderheiten bei der Debitoren-Buchhaltung als Ist-Versteuerer — https://wissen.buchhaltungsbutler.de/hc/de/articles/11279492940061
Source: Mit Debitoren und Kreditoren buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11452107588893
Source: Eine Rechnung mit einer Gutschrift verrechnen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281267173277

---

## 5. Kontenrahmen

### 5.1 Options and detection

- Available: **SKR 03**, **SKR 03 Gastro**, **SKR 03 Ärzte**, **SKR 04**, **SKR 42** (Vereine/gemeinnützige, with Kostenstellen 1 Ideeller Bereich, 2 Vermögensverwaltung, 3 Zweckbetrieb, 4 Wirtschaftlicher Geschäftsbetrieb, 9 Sammelposten pre-set), **SKR 45** (soziale Einrichtungen), **SKR 49** (Vereine). SKR03 is process-oriented (Handel), SKR04 follows the Bilanz/GuV structure; SKR03 is the most common for start-ups and Freiberufler.
- Detect from a Steuerberater SuSa/BWA or from `accounts/get`: SKR03 → Kasse **1000**, Bank **1200**, Erlöse 19 % 8400; SKR04 → Kasse **1600**, Bank **1800**, Erlöse 4400; SKR45 → Kasse 1220, Bank 1260; SKR49 → Kasse 0920, Bank 0945.
- GuV, amtliche EÜR and the Kennziffern mapping are documented for SKR03/SKR04 only.

Source: Kontenrahmen und Sachkontenlänge wählen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465983139101
Source: Projektverwaltung und Kostenstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445076569885
Source: Gewinn- und Verlustrechnung (GuV) — https://wissen.buchhaltungsbutler.de/hc/de/articles/38323605286429

### 5.2 Sachkontenlänge

- Chosen at account creation: **4 to 8 digits**. Debitoren-/Kreditorenkonten always have **one digit more** (5 to 9). Cannot be changed later. Kontenrahmen and Sachkontenlänge are the only two settings that cannot be changed afterwards (Gewinnermittlungsart, Besteuerungsart, Deb/Kred mode, Funktionsumfang can).
- `accounts/add` error 13 "the postingaccount_number must have %min% to %max% digits" and 14 "out of allowed range" enforce length and the allowed Basiskonten ranges.

Source: Kontenrahmen und Sachkontenlänge wählen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465983139101
Source: Erste Schritte mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11419668183709

### 5.3 Allowed Basiskonten (excerpt for SKR03 | SKR04)

| Basiskontentyp (`accounts/add` `type`) | Konto | SKR03 | SKR04 |
|---|---|---|---|
| Bank/Geldinstitut (`bank/institution`) | Bank | 1200 | 1800 |
| | Bank 1 … Bank 4 | 1210, 1220, 1230, 1240 | 1810, 1820, 1830, 1840 |
| | Bank 5 (range) | 1250–1288 | 1850–1888 |
| | Postbank, Postbank 1–3 | 1100, 1100, 1120, 1130 | 1700, 1710, 1720, 1730 |
| | LZB-Guthaben / Bundesbankguthaben | 1190 / 1195 | 1780 / 1790 |
| Kasse (`cash`) | Kasse | 1000 | 1600 |
| | Nebenkasse 1 / 2 | 1010 / 1020 | 1610 / 1620 |
| Sonstiges Basiskonto (`other`) | Verbindlichkeiten ggü. Kreditinstituten (+ Restlaufzeit variants) | 630, 631, 640, 650 | 3150, 3151, 3160, 3170 |
| | Verbindlichkeiten ggü. Kreditinstituten aus Teilzahlungsverträgen | 660, 661, 670, 680 | 3180, 3181, 3190, 3200 |
| | Verbindlichkeiten ggü. verbundenen Unternehmen | 700, 701, 705, 710 | 3400, 3401, 3405, 3410 |
| | Verbindlichkeiten ggü. Beteiligungsunternehmen | 715, 716, 720, 725 | 3450, 3451, 3455, 3460 |
| | **Verbindlichkeiten gegenüber Gesellschaftern** (+ Restlaufzeit) | 730, 731, 740, 750 | 3510, 3511, 3514, 3517 |
| | Verbindlichkeiten ggü. Gesellschaftern für offene Ausschüttungen | 755 | 3519 |
| | **EÜR-Verrechnungskonto** (Verrechnungskonto § 4 Abs. 3 EStG) | 1371 | 1486 |
| | Sonstige Verbindlichkeiten (+ Restlaufzeit, § 11 Abs. 2 EStG) | 1700, 1701, 1702, 1703, 1704 | 3500, 3501, 3504, 3507, 3509 |
| | Darlehen (+ Restlaufzeit) | 1705, 1706, 1707, 1708 | 3560, 3561, 3564, 3567 |
| | Kreditkartenabrechnung | 1730 | 3610 |
| | **Sonstige Verrechnungskonten (Interimskonten)** | 1792 | 3630 |
| | **Privateinlagen** (range) | 1890–1899 | 2180–2189 |

SKR45/SKR49 columns exist in the source (e.g. Bank 1260/945, Kasse 1220/920). The allowed ranges are shown in the tooltip of "Buchungskontonummer" in the UI.

Source: Informationen zu Basiskonten und zur Einrichtung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465877273757

### 5.4 Creating, hiding, deleting accounts

- **Individual Sachkonto**: *Einstellungen → Kontenverwaltung → + Neues Konto*. Pick a number close to the Vorlagekonto (same Nummernkreis), a **Vorlagekonto** (template: the new account behaves like it in all evaluations, Bilanz position, Kennziffer, tax automatic) and a unique name. Search the Standardkontenrahmen for the closest template. API: `settings/add/postingaccount`. Reasons: second company car, revenue by product, OSS revenue per country, Differenzbesteuerung, Dreiecksgeschäft.
- **Gesperrte Kontonummern** cannot be used for individual accounts, e.g. SKR03 `1400, 1512, 1517, 1572, 1574, 1577–1579, 1589, 1600, 1712, 1717, 1763, 1765, 1771–1779, 1785–1787, 3089, 3151, 3152, 3154, 3155, 3440, 3553, 3732, 3735, 3737, 3739, 3740, 3742, 3747, 3749, 3792, 3793, 8333, 8340, 8732, 8735, 8747, 8749, 9303, 9313, 9314, 9333, 9334, 9336`; SKR04 `1200, 1182, 1184, 1402, 1404, 1407–1409, 3261, 3270, 3300, 3801–3809, 3813, 3815, 3835–3838, 4333, 4340, 4732, 4735, 4747, 4749, 5189, 5440, 5553, 5732, 5735, 5737, 5739, 5740, 5742, 5747, 5749, 5792, 5793, 5951, 5952, 5954, 5955, 9303, 9304, 9313, 9314, 9333, 9334, 9336` (tax accounts, Forderungen/Verbindlichkeiten aus L+L collectors, deactivated Automatikkonten). Full lists in the source.
- **Manual Basiskonto**: type Bank/Geldinstitut for a bank without interface (CSV import), Kasse (optionally revisionssicher), Sonstiges Basiskonto for Auslagen-, Verrechnungs-, Prepaid- or Interimskonten. Accounts cannot be deleted via API.
- **Hide**: *Kontenverwaltung → Stift → "In der Dropdownliste der Basiskonten ausblenden"*; also removes it from *Liquide Mittel* on the start page (re-add there via "Konten ändern"). Recommended for used accounts.
- **Delete** (Papierkorb): only for unused/test accounts; blocked if postings are confirmed (unconfirm first) and impossible if any posting is fixed. All account types can be removed under these rules.

Source: Individuelle Sachkonten anlegen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454526317085
Source: Basiskonten ausblenden oder löschen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11454462250909
Source: Informationen zu Basiskonten und zur Einrichtung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465877273757

### 5.5 Kontenrahmenwechsel

- Only via support and only while **no posting is fixed**. It performs a full reset: deletes Konten, Zahlungen, Buchungen, individual Buchungskonten, Kreditoren/Debitoren and saved Buchungsvorschläge (Stichwörter). The request must name the account e-mail, Firmenname, target Kontenrahmen and explicitly consent to the deletion.
- After Festschreibung: close the period, export, remap account numbers (Excel replace), import into a **new** BB account; support can move the paid plan.
- A test account cannot be reset either; register a new one for production.

Source: Kontenrahmen und Sachkontenlänge wählen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465983139101
Source: Erste Schritte mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11419668183709

---

## 6. Debitoren/Kreditoren mode

### 6.1 Activation and modes

- *Einstellungen → Buchhalterische Einstellungen → Debitoren / Kreditoren*: **Aus**, **Selektiv** or **Sammelkonto**. Activation adds the *Belege* menu (booking at the Beleg) next to *Belegverwaltung*. Both can be changed any time, but a switch should normally happen at year-end.
- **Selektiv**: a Beleg is booked kreditorisch/debitorisch only if a matching Kreditor/Debitor exists or is assigned manually; otherwise it is simply booked at the Zahlung. **Sammelkonto**: unmatched Belege get the Sammelkreditor **70000** / Sammeldebitor **10000** proposed, so every invoice becomes an open item.
- Master data helps matching: IBAN and USt-ID on the Kreditor make automatic assignment and Überweisungen reliable. Create Deb/Kred in Kontenverwaltung, at the Beleg ("Neuen Kreditor anlegen") or by CSV/API (`settings/add/creditor` — `name` required, `postingaccount_number` optional (next free number otherwise), `country` as German name or ISO-2, plus `sales_tax_id`, `iban`, `bic`, `due_in_days`).
- **EÜR evaluation and the amtliche EÜR exist only with Deb/Kred = Aus.** Bilanzierer normally activate them; Soll-Versteuerer should.

Source: Debitoren und Kreditoren aktivieren und einrichten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11451725464477
Source: Eine Einnahmenüberschussrechnung (EÜR) erstellen und exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11474039285405
Source: API spec 1.9.1 (`/settings/add/creditor`) — https://app.buchhaltungsbutler.de/docs/api/v1/

### 6.2 What changes in booking

- Aufwand/Erlös and USt/VSt are booked **at the Beleg** at Rechnungs-/Leistungsdatum ("Beleg kreditorisch/debitorisch erfassen": choose Kreditor/Debitor, Buchungskonto, Steuersatz, Kostenstelle). This creates an **offener Posten** on the Personenkonto, mirrored in `1400 | 1200` Forderungen aus L+L / `1600 | 3300` Verbindlichkeiten aus L+L (both gesperrt for direct booking).
- The **Zahlung** is booked against the Debitor/Kreditor **without tax**; it only clears the open item. BB proposes this automatically when the Beleg is assigned. Ist-Versteuerer: USt moves from "nicht fällig" to "fällig" in the background (§4.4).
- **No double booking**: a Zahlung with a kreditorisch booked Beleg can only be booked against the Kreditor; a Beleg whose Zahlung is already booked on Aufwand/Erlös cannot be booked kreditorisch until that posting is lifted. API: error 7 "a receipt linked to the transaction has already been posted" / error 16 "a transaction linked to the receipt has already been posted".
- **Selective use** is legitimate: book the month directly at the bank and only invoices unpaid at period end kreditorisch/debitorisch. Cost: two postings per Geschäftsvorfall.
- Filter "Ungebucht" in *Belege* hides Belege already booked at the Beleg or assigned to a Zahlung booked on Aufwand/Erlös — including Belege on a booked **partial** payment; therefore book the Beleg before the Zahlung.
- Vorsteuer must be claimed at the Rechnungsdatum; invoices paid in a later period should be booked kreditorisch or the deduction may be lost (5-year rule anecdote in the source). The USt.-VA screen warns "Nicht verbuchte Belege".
- API: `postings/add/receipt` requires `creditor` (inbound) or `debtor` (outbound) and only works with the mode active (errors 10/12). With **offene-Posten-Buchhaltung** active, `postings/add/transaction` requires `oi_receipts_ids_by_customer` (one receipt id or `null` per split line, error 34).

Source: Mit Debitoren und Kreditoren buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11452107588893
Source: Grundlagen zur Arbeit mit Debitoren und Kreditoren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11451892160797
Source: Warn- und Fehlermeldungen bei der Umsatzsteuer-Voranmeldung (USt-VA) — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432104747677
Source: API spec 1.9.1 (`/postings/add/receipt`, `/postings/add/transaction`) — https://app.buchhaltungsbutler.de/docs/api/v1/

### 6.3 Offene Posten, Sammelzahlungen, wrong assignment, CSV import

- Open items are visible as balances on the Personenkonten in the SuSa (Schnellauswahl "Debitoren"/"Kreditoren") and via `receipts/get` `payment_status: unpaid`. Unpaid Eingangsrechnungen at period end should be booked kreditorisch for a correct Periodenabschluss.
- **Sammelzahlung** for several kreditorisch/debitorisch booked Belege: DATEV cannot "ausziffern" several Belege on one Zahlung; BB recommends a **Verrechnungskonto** (sonstiges Basiskonto with Beleg erzeugt Zahlung): one manual Zahlung per Beleg there (clears each Personenkonto), then the bank payment against Geldtransit/Verrechnungskonto.
- **Wrong Debitor/Kreditor assigned**: fix by completing own IBAN/USt-ID in *Unternehmensdaten* and checking the Personenkonto's master data (own IBAN/USt-ID entered by mistake) via *Kontenverwaltung → Volltextsuche → Stift*. A Beleg already booked on the wrong Personenkonto must be unbooked before it can be re-assigned *(inferred from the no-double-booking rule)*.
- **CSV import** (*Einstellungen → Datenimport → Debitoren/Kreditoren*): separate files for Debitoren and Kreditoren; required `Buchungskontonummer` and unique `Firmenname/Bezeichnung` (merge Vor-/Nachname into one column for private persons); optional Ansprechpartner, Straße, Adresszusatz, PLZ, Ort, Land, E-Mail, USt-ID, Kundennummer, IBAN, BIC. Duplicate handling "Aktualisieren/Überschreiben" or "Überspringen" — re-import with the same Kontonummer is the bulk-edit path. Distinct from **Kontakte** import (address book for invoicing only, no Personenkonto). Buchungssatz imports referencing unknown Personenkonten fail with "Das als … angegebene Konto ist nicht verfügbar" — import the Deb/Kred first.

Source: Belege manuell einer Zahlung zuweisen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443312093725
Source: Belegzuordnung zu falschem Debitoren-/Kreditorenkonto — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421829670045
Source: Debitoren-/Kreditorenkonten im CSV-Format importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11448069905821
Source: Kontakte als CSV Datei importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/32108156230045
Source: Importfehler bei CSV-Dateien — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431949907741

---

## 7. Sonderfälle — how BB expects them booked

Accounts as `SKR03 | SKR04`. "Erweitert" = free posting (`postings/add/free`); "an der Zahlung" = `postings/add/transaction`; "am Beleg" = `postings/add/receipt`.

### 7.1 Abschreibungen, GWG vs Sammelposten, Anlagenverwaltung
Purchase: book the full net amount on the Anlagekonto (e.g. Büroeinrichtung `420 | 650`) with 19 % VSt at the Zahlung/Beleg. Depreciation: at 31.12. in *Erweitert*, AfA-Aufwandskonto im Soll an Bestandskonto im Haben, linear over the AfA-Tabelle life, pro rata months in the first and last year (desk EUR 2,000 / 13 years = 153.84 p.a.; bought in September → 4/12 in year 1). Assets > EUR 1,000 must follow the amtliche AfA-Tabelle. GWG method is a setting (*Buchhalterische Einstellungen → Abschreibungen*: "Geringwertige Wirtschaftsgüter (GWG)" `480 | 670` Sofortabschreibung, or "Sammelposten" pooled over 5 years); only the chosen method's accounts are bookable, and CSV imports touching the other method's account fail ("Einzelne Konten sind … nicht verfügbar" → import in two passes, switching the setting). The **Anlagenverwaltung** starts when a posting on an Anlagenkonto is confirmed (dialog "Erfassen": Inventarnummer, Nutzungsdauer or "nicht abschreiben"), books **monthly** AfA automatically (retroactively if the purchase month is past), handles GWG without asking a life, disposes assets from a sale posting on an Erlöskonto ("Ausbuchen", Buchgewinn/-verlust computed), and can take over existing assets with Übernahmebetrag and remaining months. "Anlage löschen" stops future AfA only.
Source: Abschreibungen berechnen und verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11259650218013
Source: Abschreibungsart zwischen GWG und Sammelposten ändern — https://wissen.buchhaltungsbutler.de/hc/de/articles/11444878256413
Source: Anlagenverwaltung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473445146397

### 7.2 Aktive / passive Rechnungsabgrenzungsposten
aRAP: payment in the old year, expense belongs to the new year (January rent paid in December; a 12-month software subscription paid in October → 3/12 expense now, 9/12 aRAP). Book the Zahlung at the bank against the expense account with the applicable VSt (VSt is claimed at Rechnungsdatum), then in *Erweitert* at 31.12. move the deferred net share from the expense account to ARAP `980 | 1900`, and back on 01.01. pRAP mirrors this for income received in advance (interest example, § 4 Nr. 8a UStG tax-free) via PRAP `990 | 3900` *(SKR number inferred from DATEV standard)*. **ARAP/PRAP must be booked without tax**; CSV imports with a Steuerschlüssel or an Automatikkonto against RAP fail — remove those lines and book them manually in *Erweitert*.
Source: Aktive & passive Rechnungsabgrenzungsposten verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11278472921117
Source: Importfehler bei CSV-Dateien — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431949907741

### 7.3 Auslagen, Spesen, Privateinlagen — the Auslagenkonto
Create one **Auslagenkonto** per owner/Gesellschafter/employee as *Sonstiges Basiskonto* (`accounts/add` type `other`), template **Privateinlagen `1890 | 2180`** for Einzelunternehmen or **Verbindlichkeiten ggü. Gesellschaftern `730 | 3510`** for companies (a UG/GmbH has no Privatkonten; what the owner pays is a liability to the Gesellschafter). With "Beleg erzeugt Zahlung" active, assigning a Beleg to the Auslagenkonto creates the Zahlung and the proposal; the balance shows what the company owes the person. Reimbursement: bank outflow against **Geldtransit `1360 | 1460`**, plus a manual incoming Zahlung on the Auslagenkonto against Geldtransit (no Auslagenrechnung needed). Rare cases without a Basiskonto: *Erweitert*, expense an Privateinlagen `1890 | 2190` (Einzelunternehmen) or an Verbindlichkeiten ggü. Gesellschaftern `730 | 3510` (GmbH). Where "Kasse" is written the Finanzamt expects a proper Kassenbuch; prefer an Auslagenkonto if no physical cash register exists.
Source: Auslagen, Spesen oder Privateinlagen buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11278919655965
Source: Informationen zu Basiskonten und zur Einrichtung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11465877273757

### 7.4 Skonto
Never reduce the Beleg; book the invoice at full amount. At the Zahlung add a **Teilbuchung** with a **negative** amount on Erhaltene Skonti (search "Erhaltene"/"Skonti"; 19 % variant `3736 | 5736`) or Gewährte Skonti (`8736 | 4736`), **with the invoice's tax rate** so USt/VSt is corrected. With Deb/Kred the first line is the Personenkonto instead of Aufwand/Erlös. The difference is shown at Belegzuweisung. Accounts with an explicit rate in the name accept only that rate; for 16 %/5 % use the generic "Erhaltene/Gewährte Skonti" account with the implicit "16/19%" key. Skonto payments are not auto-matched to Belege.
Source: Erhaltenen und gewährten Skonto verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281526395037
Source: Mit Debitoren und Kreditoren buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11452107588893

### 7.5 Rechnung mit Gutschrift verrechnen
Partial Gutschrift with a payment: assign both invoice and Gutschrift to the Zahlung; book the Zahlung on Aufwand/Ertrag or against the Personenkonto. Full Gutschrift, **no payment, no Deb/Kred**: create a EUR 0.01 Zahlung on a sonstiges Basiskonto dated before the bookkeeping start (e.g. 01.01. of the prior year), book it against Interimskonto `1590 | 1370`, and assign invoice + Gutschrift (and any further such pairs) to it → both leave the open list. **With Deb/Kred**: create an Interimskonto Basiskonto `1891 | 3631` with Beleg erzeugt Zahlung; Soll-Versteuerer add the Zahlung at the Rechnungsdatum, Ist-Versteuerer at the **Gutschriftsdatum** in the amount of the Ausgangsrechnung; assign the Gutschrift to the Basiskonto (Zahlung auto-created); book both Zahlungen against the Debitor/Kreditor. Rechnungskorrekturen/Stornorechnungen are handled the same way.
Source: Eine Rechnung mit einer Gutschrift verrechnen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281267173277

### 7.6 Stornos, Rücklastschriften, Teilgutschriften
Original already booked: book the refund/return against the **same** Aufwands-/Erlöskonto with the **same** tax rate; the negative sign flips Soll/Haben and reduces expense/revenue and the tax account. Original not yet booked: book both original and reversal **without tax** on Interimskonto `1590` (erfolgsneutral). Rücklastschriftgebühren: split them off to Nebenkosten des Geldverkehrs `4970 | 6855` so Last- and Gutschrift net to zero. Teilgutschrift: original on Erlös/Aufwand, Teilgutschrift against the same account, same rate. The USt.-VA warning "Buchungen entgegen der normalen Logik" (Zahlungsausgang als Ertrag / Eingang als Aufwand > EUR 100 per posting or EUR 400 total) is expected here and can be ignored after checking the SuSa; for durchlaufende Posten use `1590 | 1370` for both legs.
Source: Stornos oder Rücklastschriften erfassen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11320416257693
Source: Warn- und Fehlermeldungen bei der Umsatzsteuer-Voranmeldung (USt-VA) — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432104747677

### 7.7 Geldüberträge zwischen Zahlungskonten
Bank ↔ Kasse, Bank → Kreditkarte, Bank → PayPal, Amazon/Stripe Payouts, Auslagenerstattung: every Basiskonto is booked from its own statement, so both legs go against **Geldtransit `1360 | 1460`** (outflow on account A against Geldtransit; manual or imported inflow on account B against Geldtransit). Direct Basiskonto-an-Basiskonto postings are blocked (UI, API, CSV import: "Unzulässige Buchungskombination"). Geldtransit must be **zero** at period end (Monatsabschluss check). Consider individual Geldtransit sub-accounts per payment provider (template 1360) for easier reconciliation.
Source: Geldüberträge zwischen Zahlungskonten verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281936719005
Source: Buchhaltung mit Amazon — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281029665309

### 7.8 Trinkgeld
Deductible within 5–15 % if evidenced (waiter's signature, separate line on the card statement, or an Eigenbeleg). At the Zahlung: Teilbuchung, Buchungstext "Trinkgeld" (proposes Bewirtungskosten), tax **"keine USt."**, amount of the tip; the remaining line stays Bewirtungskosten with VSt.
Source: Trinkgeld verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11320758964381

### 7.9 Fremdwährung
BB converts with daily rates (ECB-based) at Rechnungs-/Zahlungsdatum; supported: AUD, BGN, BRL, CAD, CHF, CNY, CYP, CZK, DKK, GBP, HKD, HRK, HUF, IDR, ILS, INR, ISK, JPY, KRW, LTL, LVL, MTL, MXN, MYR, NOK, NZD, PHP, PLN, ROL, RON, RUB, SEK, SGD, SIT, SKK, THB, TRL, TRY, USD, ZAR (the `transactions/add` `currency` list is slightly longer). Rates can be overridden at Zahlung and Beleg. PayPal-style conversions produce three Zahlungen: book the EUR leg as expense and both FX legs on an Interimskonto (own Basiskonto), re-booking differences monthly to Aufwand/Ertrag aus Währungsumrechnung. Foreign-currency bank account without conversion legs: book the converted EUR amount; recognise FX gains/losses at Stichtage by manual Zahlung; the account balance display and "Kontostand berechnen" ignore currency and will be off. Belege: choose the currency at the Beleg, or convert manually to EUR if unsupported; Deb/Kred differences are split off at the clearing Zahlung to FX gain/loss. Without Deb/Kred no conversion is needed — just assign the Beleg. Foreign-currency Belege are not auto-matched, get no Teilbuchungsvorschlag, and `postings/add/receipt` needs the `amount` computed by BB (`receipts/get/id_by_customer` → `amount`/`amount_original`/`exchangerate`; errors 34/39/40). API upload `currency` must be `EUR`; `receipts/add` (no file) accepts USD, GBP, CHF.
Source: Wie erfasse ich Belege und Zahlungen in einer Fremdwährung? — https://wissen.buchhaltungsbutler.de/hc/de/articles/11407902754333
Source: Zahlungskonten über "Kontostand berechnen" plausibilisieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11474253173021
Source: API spec 1.9.1 (`/receipts/upload`, `/receipts/add`, `/postings/add/receipt`) — https://app.buchhaltungsbutler.de/docs/api/v1/

### 7.10 Lohnbuchhaltung
Without a payroll journal: book net salary and Lohnsteuer payments on Gehälter `4120 | 6020`, Sozialversicherung on Gesetzliche soziale Aufwendungen `4130 | 6110` (accrue the January-10 Lohnsteuer payment). With a payroll journal (CSV import via *Datenimport → Buchungssätze*, or the TAXMARO interface which posts into *Erweitert* for confirmation): expenses are booked in *Erweitert* against Verbindlichkeiten aus Lohn und Gehalt `1740 | 3720`, Lohn-/Kirchensteuer `1741 | 3730`, soziale Sicherheit `1742 | 3740`; bank payments then only clear these liabilities (never expense twice). Expert pattern: Lohnverrechnungskonto `1755 | 3790` between expense and liabilities, must net to zero. If salaries are missing in the BWA, BB points to the Lohnbuchhaltung article — a typical cause *(inferred)* is that bank payments were booked on the Verbindlichkeitskonten without the expense side from a payroll journal.
Source: Lohnbuchhaltung in BuchhaltungsButler erfassen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282286368541
Source: Lohnbuchhaltung aus TAXMARO nahtlos importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468074015901

### 7.11 Prepaid-Guthaben (ads accounts, postage)
Model the prepaid balance as a *Sonstiges Basiskonto* with Beleg erzeugt Zahlung. Top-up: bank outflow and manual inflow on the prepaid account, both against Geldtransit. Usage invoices: assign to the prepaid account (Zahlung auto-created, balance decreases), then book as expense with VSt — VSt only when service and invoice exist. Not for Einzweck-Gutscheine (§ 3 Abs. 13 ff. UStG, e.g. a car-wash card), where VSt arises at top-up.
Source: Lieferanten mit Prepaid-Guthaben buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282126009373

### 7.12 Anfangsbestände / EB-Werte
Erlös-/Aufwandskonten are zeroed each Wirtschaftsjahr; Anlagevermögen, Verbindlichkeiten, Kapital, Forderungen, Rückstellungen, ARAP/PRAP, Finanzkonten, Umlaufvermögen, Anzahlungen, Vorräte, Interimskonten, all Basiskonten and all Deb/Kred carry forward automatically. First year: **Zahlungskonten** — manual Zahlung (Gegenpartei "Anfangsbestand", correct sign) dated the last day of the prior year, booked against **Saldenvortrag 9000**; **Sachkonten** (Bilanzierer) — *Erweitert*, each SuSa balance against 9000 (unterjährig: Summenvortrag 9090), dated 31.12. of the prior year so the SuSa shows "Saldo zum 01.01."; **Deb/Kred** — preferably re-enter the unpaid prior-year invoices kreditorisch/debitorisch (auto-clearing on payment) or book in *Erweitert* (then clear manually; no Ist-USt re-posting). EB-Buchungsstapel from the Steuerberater can be CSV-imported. Corrections after the Jahresabschluss: book only the difference at the old year-end against 9000. Gewinn-/Verlustvortrag: 01.01., 9000 an Gewinnvortrag vor Verwendung `860 | 2970`, or Verlustvortrag `868 | 2978` an 9000. Bilanz integrity requires the balance of 9000 to be zero (or an explained residual).
Source: Wie buche ich Anfangsbestände bzw. EB-Werte ein? — https://wissen.buchhaltungsbutler.de/hc/de/articles/11409068699421
Source: Bilanz: Integritätsprobleme beheben — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431862574109
Source: Wechsel zu BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421251511965

### 7.13 USt-/VSt-Salden vortragen
All USt and VSt accounts are zeroed on 01.01. Year-end (usually by the Steuerberater): accrue the November (Dauerfristverlängerung) and December Vorauszahlungen at 31.12. from `1780 | 3820` to Umsatzsteuer laufendes Jahr `1789 | 3840`; on 01.01. move that balance to Umsatzsteuer Vorjahr `1790 | 3841`; sum all USt accounts (`1767–1788 | 3800–3851`) and VSt accounts (`1528–1588 | 1376–1484`) from the SuSa and book the net to `1790 | 3841` on 01.01. in *Erweitert* (Soll if a refund is expected, Haben if a payment); book the later payment/refund against `1790 | 3841`. Never book the tax accounts themselves.
Source: Salden der Umsatzsteuer- und Vorsteuerkonten vortragen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11408798861597

### 7.14 Eigenbelege
Created at a Zahlung (context menu "Eigenbeleg erstellen"): Gegenpartei, date and amount pre-filled; reason (mandatory explanation for "Sonstiges"); address recommended above EUR 250; PDF gets user name, company data, sequential Eigenbeleg number (*Rechnungseinstellungen*) and a GUID signature; stored revisionssicher, not editable, deletable (number kept), appears among Eingangsbelege (search "Eigenbeleg"). Book **without tax** ("ohne USt./VSt.", API `0_none`) on a non-automatic account (e.g. `3200 | 5200` instead of `3400 | 5400`) — no Vorsteuerabzug. Replace with the original later: delete the Eigenbeleg (assignment released), upload the original, re-book with VSt. Roles Admin, Steuerberater, Standardnutzer; requires access to the Zahlungskonto.
Source: Eigenbelege — https://wissen.buchhaltungsbutler.de/hc/de/articles/20426914295453

### 7.15 Differenzbesteuerung (§ 25a UStG)
Create separate individual accounts: Wareneingang Einzeldifferenz / Gesamtdifferenz (template Wareneingang `3200 | 5200`) and Erlöse Einzel-/Gesamtdifferenz mit/ohne USt (template Umsätze/Erlöse `8200 | 4200`). Purchase from a private person booked without tax; the sale is a Teilbuchung: the purchase-price share without USt on "Erlöse … ohne USt", the margin on "Erlöse … mit USt" at 19 %. Gesamtdifferenz (items ≤ EUR 500 purchase price) is booked the same way once per Besteuerungszeitraum.
Source: Besonderheiten bei der Differenzbesteuerung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11279998187293

### 7.16 OSS and foreign VAT
Only German USt can be keyed. Revenue subject to another EU state's VAT is booked **gross without Steuerschlüssel** on individual Erlöskonten per country/regime (templates: Lieferungen an Privat im anderen EU-Land steuerpflichtig `8320 | 4320` → e.g. "Erlöse PL/OSS" `8322 | 4322`, "Erlöse FR/OSS" `8321 | 4321`, "Erlöse PL/PL" `8332 | 4332`; B2B to EU businesses steuerfreie i.g. Lieferung `8125 | 4125` (ZM, Kz. 41); B2B from a foreign warehouse e.g. `8222 | 4222`). At quarter end compute VAT = brutto / (100 + rate) × rate from the BWA/SuSa and re-book in *Erweitert* Erlöskonto (S) an Umsatzsteuer aus im anderen EU-Land steuerpflichtigen Lieferungen `1767 | 3817` (H) dated the last day of the quarter; the Kontenblatt then shows net revenue and VAT per country for the BZSt portal (no interface). Automate with invoice-layout codes + Automatisierungsregeln, or import Ausgangsrechnungen as debitorische Buchungssätze. Same workaround for any foreign VAT registration (Polish 23 % example: `8201` template `8200`).
Source: Vorbereitung der OSS-Meldung in der Buchhaltung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11322803594269
Source: Was muss ich beachten, wenn ich in einem anderen Land umsatzsteuerpflichtig bin? — https://wissen.buchhaltungsbutler.de/hc/de/articles/11407622675485

### 7.17 Dreiecksgeschäft and EU-Neufahrzeug
Both DATEV Automatikkonten are deactivated in BB (`3553 | 5553` Erwerb als letzter Abnehmer im Dreiecksgeschäft; `3440 | 5440` i.g. Erwerb Neufahrzeug von Lieferant ohne USt-ID). Create an individual account from a **non-automatic** template (`3260 | 5260` resp. `3250 | 5250` from Wareneingang `3200 | 5200`), book the price there (bank or kreditorisch), then in *Erweitert* book 19 % USt and 19 % VSt of the price against Interimskonto `1590 | 1370` — USt account `1794 | 3819` + VSt `1573 | 1436` (Dreiecksgeschäft → Kz. 66/69) resp. `1784 | 3834` + `1584 | 1432` (Neufahrzeug → Kz. 61/94/96). *(Tax account numbers taken from the Kennziffern table; the articles only name the Interimskonto.)*
Source: Erwerb von Waren im Dreiecksgeschäft — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281694063005
Source: EU Neufahrzeug-Erwerb v. Lieferanten o. USt. ID — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281833740189
Source: Buchungskonten den Kennziffern der USt.-VA zuordnen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11472964130461

### 7.18 Investitionsabzugsbetrag (§ 7g EStG)
Off-balance (außerbilanziell) on accounts **9970 / 9971** "Investitionsabzugsbetrag § 7g Abs. 1 EStG"; up to 50 % of planned net cost, max EUR 200,000, profit ≤ EUR 200,000, movable Anlagegut ≥ 90 % business use, bought within 3 years. Year 1: book the IAB in *Erweitert* (9970/9971 pair); year of purchase: reverse it and optionally reduce the AfA base by the same amount plus 20 % Sonderabschreibung. Affects Steuerbilanz only.
Source: Investitionsabzugsbetrag — https://wissen.buchhaltungsbutler.de/hc/de/articles/20068054846237

### 7.19 10.7 % and 5.5 % (agriculture)
Not selectable. Eingangsrechnungen only: Teilbuchung — line 2 on Abziehbare Vorsteuer `1570 | 1400` with the pure tax amount (e.g. 5.5 % of net), line 1 the net on the expense account without tax. Ausgangsrechnungen with these rates cannot be booked in BB.
Source: Buchungen mit 10,7% und 5,5% Umsatzsteuer (USt.)/Vorsteuer (VSt.) erfassen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281149705885

### 7.20 Kassenbuch
Create a Kasse with option **Revisionssicher** (`accounts/add` type `cash`, `is_revision_safe: true`): Zahlungen can no longer be deleted, only stornoed ("Zahlung löschen" creates the Storno). Report *Abschluss → Kassenbuch* (CSV/PDF) sorted by **Erfassungsdatum**, not Zahlungsdatum, and includes out-of-period entries recorded between in-period ones — record cash movements promptly and chronologically. Feed via manual Zahlung, CSV "Kontoauszug importieren" or Beleg erzeugt Zahlung (see caveat §1.4). Not every business needs a Kassenbuch; without one, book cash via Auslagenkonto. Ausgangsrechnungen paid in cash: upload to Ausgangsbelege, add the Kasse Zahlung manually.
Source: Revisionssicheres Kassenbuch einrichten und auswerten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11467646903069
Source: Ausgangsrechnungen in der Kasse verbuchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11419453337373

### 7.21 Marketplace / payment-provider accounts (Amazon pattern)
Each marketplace gets its own Zahlungskonto whose balance must return to **EUR 0** per settlement (sales − fees − payout). Fees are split off automatically as Teilbuchung; set the fee account (e.g. Nebenkosten des Geldverkehrs `4970 | 6855`) and the tax treatment (historically reverse charge) in Automatisierungsregeln, or book the fee invoice kreditorisch and assign it to the payout. Payout on the marketplace account and inflow at the bank both against Geldtransit. Reserve amounts on Durchlaufende Posten `1590 | 1370`. Do not delete "Backup" accounts. Prefer debitorisch imported Ausgangsrechnungen (CSV/API with payment_reference) so payments are just Debitor clearings confirmable in bulk.
Source: Buchhaltung mit Amazon — https://wissen.buchhaltungsbutler.de/hc/de/articles/11281029665309

---

## 8. Periodic work

### 8.1 Monatsabschluss steps and the Monatsabschluss-Checkliste

Order documented by BB — six steps, also mirrored in the in-app **Monatsabschluss-Checkliste (Beta)** under *Abschluss-Cockpit* (roles Admin/Steuerberater/Standardnutzer, progress saved per company and month) — plus the **Fehlende Belege** check from a companion article, inserted here as step 4:
1. **Duplikatsprüfung**: *Belege → Eingangsbelege* filter "Duplikatsverdacht"; sort by Gegenpartei/Datum; check before deleting. Repeat for Ausgangsrechnungen. BB never warns on duplicate uploads by itself.
2. **Ungebuchte Zahlungen**: *Zahlungen*, filter "ungebucht", **Alle Konten**, period limited. API: `transactions/get` for the period, then check which have no posting (`postings/get` filtered by `account`).
3. **Ungebuchte Belege** (Bilanzierer): *Belege* filter "ungebucht"; book unpaid Eingangsrechnungen kreditorisch as offene Verbindlichkeit. Remember the "gebucht via Zahlung" exception (§2.1).
4. **Fehlende Belege**: *Zahlungen* filter "Fehlender Beleg"; assign, upload at the Zahlung, mark **beleglos** (fees, rent without invoice), or leave a Kommentar for the Steuerberater. Check "Beleg hinzufügen" first — the Beleg may exist but not have matched (amount mismatch, several Belege).
5. **Banksalden prüfen**: *Abschluss → Kontostand berechnen* per Zahlungskonto and Stichtag versus the real statement; or SuSa. Requires the Anfangsbestand to be booked; ignores currencies. Connected bank accounts show the bank's balance in *Zahlungen*, manual/PayPal/Amazon/eBay/Stripe accounts a computed one.
6. **Konten plausibilisieren** in *Abschluss → SuSa-Liste/Kontenblätter*: Soll/Haben consistent, count of recurring postings equals periods, consistent Kontierung, suspicious tax/no-tax postings, **Geldtransit `1360 | 1460` and Interimskonto `1590 | 1370` at zero**.
7. **Festschreiben** the period under *Abschluss* (set the period first). Then USt.-VA.
API: `reports/create/sums` + `reports/get/sums`/`reports/get/sums/ledger`; `receipts/get` `payment_status: unpaid`; there is no API for Festschreibung or for the Checkliste.

Source: Schritte, um die Buchhaltung am Monatsende fertigzustellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421107352989
Source: Monatsabschluss-Checkliste (Beta) — https://wissen.buchhaltungsbutler.de/hc/de/articles/38676182512029
Source: Fehlende Belege identifizieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443881408285
Source: Zahlungskonten über "Kontostand berechnen" plausibilisieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11474253173021

### 8.2 USt.-VA erstellen, übermitteln, berichtigen, Protokolle

- *Abschluss → Umsatzsteuer-Voranmeldung*: choose the period; BB shows values per Kennziffer and a yellow box with warnings: postings on accounts BB cannot evaluate (e.g. `3165 | 5965` → file via ELSTER manually), postings "entgegen der normalen Logik" (> EUR 100 each / EUR 400 total; usually refunds, check the SuSa), **unbestätigte Buchungen** in the period (links to Zahlungen/Eingangsbelege/Ausgangsbelege/Erweitert), **nicht festgeschriebene Buchungen** (fix before transmitting), **nicht verbuchte Belege** with Rechnungsdatum in the period that are neither paid-and-booked nor kreditorisch booked (book them kreditorisch to claim VSt in the right period).
- Transmission directly from BB uses **BB's own ELSTER certificate** (§ 87d AO: identification at registration, 5-year record keeping, data shown before/after). Alternatively use ElsterOnline/ElsterFormular with your own certificate.
- **Übermittlungsprotokoll**: save it locally immediately — BB does not store it. Recommended: upload it as Beleg and assign it to the Finanzamt payment. Re-issue via support costs EUR 10 net for the first, EUR 3 per further protocol.
- **Berichtigte USt.-VA**: generate the period again, tick "Es handelt sich hierbei um eine berichtigte Anmeldung" before the Prüfprotokoll, send.
- ELSTER-returned errors name the offending field at the end of the path (e.g. `Telefon` > 20 chars, Sonderzeichen in Firmenname, invalid Steuernummer) → fix in *Unternehmensdaten* (Systemdaten/Ansprechpartner, Allgemeine Firmendaten, Steuerliche Informationen).
- **Konsolidierte USt.-VA** for several companies under one Steuernummer: generate each account's VA, sum the Kennziffern, file via ELSTER-Online with your own certificate.

Source: Umsatzsteuer-Voranmeldung (USt.-VA) erstellen und übermitteln — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473240647965
Source: Warn- und Fehlermeldungen bei der Umsatzsteuer-Voranmeldung (USt-VA) — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432104747677
Source: Berichtigte Umsatzsteuer-Voranmeldung erstellen und übermitteln — https://wissen.buchhaltungsbutler.de/hc/de/articles/11469981205277
Source: Übermittlungsprotokolle der Umsatzsteuer-Voranmeldung (USt.-VA) erneut anfordern — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473124225949
Source: Konsolidierte Umsatzsteuer-Voranmeldung (USt.-VA) erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473051798941

### 8.3 Zusammenfassende Meldung (ZM)

- *Abschluss → Zusammenfassende Meldung*, "Generieren" (e-mail when slow). Included: postings on `8336 | 4336` (sonstige Leistungen EU, "S") and `8125 | 4125` (i.g. Lieferungen, "L") and on individual accounts derived from them. Missing revenue → re-book onto these accounts. L/S is pre-set from the account but editable. Debitoren need the customer's USt-ID in master data to be output. Rechnungsdatum is always used (§4.3). Transmitted with BB's certificate; **corrections are not possible from BB** — use ELSTER Online and report only the changed positions. ZM values must equal USt.-VA Kz. 41 (L) and Kz. 21 (S).

Source: Zusammenfassende Meldung (ZM) erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473312092445

### 8.4 Auswertungen

All evaluations in *Abschluss* are generated asynchronously (refresh or wait for e-mail), include **only confirmed** postings, warn about unconfirmed ones, allow drill-down per account with Beleg preview, and can differ from the SuSa if postings were added after generation — regenerate. Large periods may fail on size; try shorter periods.
- **BWA**: classic structure, not customisable; basis of the Bilanz's Jahresüberschuss; option "Nach Kostenstellen aufschlüsseln" (CSV only); excludes USt/VSt even for EÜR users. Uses Leistungsdatum for debitorisch/kreditorisch Belege. API `reports/create/bwa`.
- **EÜR**: only with Gewinnermittlungsart EÜR and Deb/Kred = Aus; includes vereinnahmte USt and verauslagte VSt (hence differs from BWA); Kostenstellen option. **Amtliche Anlage EÜR** (add-on EUR 5.90/month, years 2023–2025, Anlagen EÜR/AVEÜR/SZ; SE/LuF unsupported): wizard maps accounts to form lines (mapping remembered next year), manual values, ELSTER plausibility check, direct transmission with Übertragungsprotokoll; AVEÜR is not auto-filled.
- **GuV**: SKR03/SKR04 only; formats § 275 Abs. 2, § 276 (klein/mittelgroß), § 275 Abs. 5 (Kleinst) HGB; options Vorjahresvergleich, Prozentangabe, Kontennachweis; PDF/CSV/Excel; access tied to the Bilanz right.
- **SuSa-Liste / Kontenblätter**: choose period and accounts (search, Schnellauswahl Zahlungskonten/Sachkonten/Debitoren/Kreditoren); CSV export = ZIP with overview + one CSV per Kontenblatt; Excel = one workbook, sheet per account. Kontenblätter by Rechnungsdatum. Requires Anfangssalden for meaning. API `reports/create/sums` (`file_pdf`, `file_csv`, `archive_export` with Kontenblätter; `base` date vs date_delivery_else_date) → `reports/get/sums`, `reports/get/sums/ledger`.
- **Bilanz**: only with Gewinnermittlungsart Bilanz; Aktiva must equal Passiva or **Integritätsprobleme** are reported. Causes: incomplete EB-Werte in year 1 (9000 must net to zero), missing Gewinn-/Verlustvortrag (`860 | 2970`, `868 | 2978`) and missing USt/VSt Saldovortrag (`1790 | 3841`) in following years. Individual accounts appear at their Vorlagekonto's position. Transmission of the E-Bilanz only via third parties (eBilanz+ based on the SuSa).
- **Anlagenverwaltung**: see §7.1. **Controlling Dashboard** (Beta): month/quarter/year plus comparison period, KPIs from BWA/SuSa (EBITDA, margins, ROE/ROI, cost structure, "Rule of BHB"), graphs always 6 months, access via Rechteverwaltung (needs "alle Konten sehen").
- **Kontostand berechnen**: §8.1 step 5. **Kassenbuch**: §7.20.
- Empty or wrong evaluations: unconfirmed postings in Zahlungen/Belege/Erweitert, or abweichendes Leistungsdatum effects.

Source: Eine Betriebswirtschaftliche Auswertung (BWA) erstellen und exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473653935005
Source: Eine Einnahmenüberschussrechnung (EÜR) erstellen und exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11474039285405
Source: Das amtliche Formular Anlage EÜR erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/29104969813277
Source: Gewinn- und Verlustrechnung (GuV) — https://wissen.buchhaltungsbutler.de/hc/de/articles/38323605286429
Source: Summen- und Saldenliste (SuSa-Liste) erstellen und exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11474193643293
Source: Bilanz - Erklärung und Übermittlung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11473492321053
Source: Bilanz: Integritätsprobleme beheben — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431862574109
Source: Controlling Dashboard — https://wissen.buchhaltungsbutler.de/hc/de/articles/20250876187933
Source: Leere oder fehlerhafte Auswertungen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431990158365

### 8.5 Steuerberater-Zugang and Mandantenkonten

- A Steuerberater gets a free full account by registering a test account and writing to the BB Steuerberater address; access to a client is granted by the client via *Nutzerverwaltung → Nutzer hinzufügen* with the adviser's e-mail (role Steuerberater: all bookkeeping functions, Auswertungen & Exporte, write access to Stammdaten). One login switches between Mandanten (company name top left).
- **Mandantenkonten** created by the adviser: register with an e-mail the adviser controls, set Kontenrahmen/Sachkontenlänge, enter the client's USt-ID, IBAN and exact Firmenname (Belegerkennung), replace the system e-mail with the client's, add the adviser's main account as **Master/Admin**, then downgrade the client to "Klient/Mandant" or "Klient/Mandant (Nicht-Bucher)" if desired. Linking an existing account needs a temporary extra Admin access from support (5 days).
- Roles: Admin, Steuerberater:in, Standardnutzer:in, Assistent:in (upload/check/sort, pay released invoices, create Ausgangsrechnungen), Belegprüfer:in (Eingangsbelege only), Leserecht; individual roles configurable. Sections "Zahlung zuweisen/buchen" at the Beleg require the privilege "Alle Konten". The Rechnungsfreigabe process lets Master users release Eingangsbelege for payment above a threshold; non-Master users can only pay released ones.

Source: Steuerberater-Zugang einrichten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11446168108957
Source: Mandantenkonten einrichten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445921479709
Source: Mehrmandantenfähigkeit verstehen und nutzen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11453965304349
Source: Nutzerverwaltung und Rechtevergabe nutzen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11453993512733
Source: Rechnungsfreigabe-Prozess — https://wissen.buchhaltungsbutler.de/hc/de/articles/11514173225117

### 8.6 Exports for the Steuerberater

- *Abschluss → Buchungssätze und Belege exportieren*: period, format **DATEV** or **BB Standardformat**, "Belege anhängen", Buchungsstatus (Alle / Festgeschrieben / Nicht festgeschrieben), optional account selection. Result is a ZIP (e-mail when slow; also `https://app.buchhaltungsbutler.de/download/datenexport.zip` while logged into that account). Practice: fix the exported period afterwards, then later export only "Nicht festgeschrieben" to hand over additions/changes.
- Unconfirmed postings at export time: choose (a) output proposals and a placeholder account for ungebuchte, (b) placeholder account for all unconfirmed and ungebuchte, or (c) omit them.
- **DATEV format** (EXTF Buchungsstapel CSV): Umsatz, S/H, WKZ, Konto, Gegenkonto, BU-Schlüssel (none for Automatikkonten), Belegdatum `DDMM`, Belegfeld-1 = Rechnungsnummer or `BB-Int-<n>`, Buchungstext = Gegenpartei + text, Beleglink (GUID matched via the bundled XML in DATEV Belegtransfer/Unternehmen online), Beleginfo 1–7, Zusatzinformation 1–2, Sachverhalt L+L, Kostenstelle/KOST2 *(inferred; not in the export article's column list)*. Belegbilder named by Buchungsnummer (or original name); several Belege per posting → `_1`, `_2`.
- **BB Standardformat** columns: Datum, Buchungstext, Betrag, Währung, Sollkonto, Habenkonto, Steuerschlüssel (BU), Buchungsnummer (BB id, not the journal number), Rechnungsnummern, Gegenpartei, Umsatzsteuer, Zugewiesene Beträge, Beleglinks, Festschreibung (0/1), Kommentar — for controlling tools and non-DATEV software.
- Partner guides: **DATEV** Kanzlei Rechnungswesen (Stapelverarbeitung + Belegtransfer "Ohne Belegtyp", type "DATEV XML-Schnittstelle online/DMS"), **Addison** (DatevPro driver, "Dokumente archivieren", create free fields Kommentar/Verwendungszweck), **Agenda** FIBU (Transfer → DATEV Import → Assistent; may need re-zipping), **Simba** (add `.pdf` to Beleglink column T via Excel, zip CSV + unzipped Belege folder named like the Buchungsstapel), **STOTAX** (DATEV EXTF, Kontenbeziehungstabelle HKR01 for SKR03, Belege folder next to the CSV), **rodat-FIBU/MICRODAT** (import postings first, then "Buchungsbelege importieren" keyed on Beleginfo 1 = file name; only the first of several Belege auto-assigns).
- CSV import of Buchungssätze (the reverse direction) accepts DATEV or individual formats: modes DATEV / Konto+Gegenkonto (S/H flag) / Sollkonto+Habenkonto (positive amounts); fields Betrag, Konto, Gegenkonto, Datum, Buchungstext, Gegenpartei, Rechnungsnummer, Leistungsdatum, S/H, BU, Festschreibung (0/1, date set to import day), Sachverhalt L+L (only 7), Kostenstelle, Zahlungsreferenz. One file per year, comma-separated, 2–500 chars per field, no tax-account postings, no Basiskonto-an-Basiskonto, no BU on Automatikkonten, ARAP/PRAP without tax. **Konfiguration 4** (Beleglink = column 20) is required for DATEV imports with Belegverknüpfung (after a Beleg-Archiv ZIP import) and for merging multi-rate invoice lines into one split Beleg (assign an empty column as Beleglink if none exists). Failed rows come back as a CSV plus Fehlerprotokoll in *Import-Verlauf*.

Source: Buchungssätze und Belegbilder in unterschiedlichen Formaten exportieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445407988637
Source: DATEV: Buchungssätze und Belege importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445618180125
Source: Addison / Agenda / Simba / STOTAX / rodat-FIBU: Buchungssätze und Belege importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445156423581 , https://wissen.buchhaltungsbutler.de/hc/de/articles/11445247028253 , https://wissen.buchhaltungsbutler.de/hc/de/articles/11446128205213 , https://wissen.buchhaltungsbutler.de/hc/de/articles/11446254401821 , https://wissen.buchhaltungsbutler.de/hc/de/articles/11446003729437
Source: Buchungssätze im (DATEV) CSV-Format importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11446480380189
Source: Buchungssätze im DATEV Format mit Belegverknüpfung importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/32108261829661
Source: Ausgangsrechnungen als CSV-Datei importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11446405613981
Source: Importfehler bei CSV-Dateien — https://wissen.buchhaltungsbutler.de/hc/de/articles/11431949907741

### 8.7 GDPdU export, Beleg-Archiv ZIP, Aufbewahrung

- **GDPdU/Prüfungsexport** (Audicon Beschreibungsstandard): Firmenstammblatt.csv, Journal.csv (all **fixed** postings in gap-free Journalnummer order, may include other periods' postings fixed in between; columns Journalnummer, Buchungsdatum, Journaldatum = Festschreibedatum, Belegdatum, Buchungsnummer, Buchungstext, Betrag, Soll/Haben accounts and amounts, USt accounts/amounts, Kostenstelle, Leistungsdatum, "Datum Zuordnung Steuerperiode"), Kontenblaetter.csv (by Rechnungsdatum, not periodengerecht), Kontenplan.csv (Kategorie, BWA-Unterart, USt-Position, EÜR-Zuordnung), Umsatzsteuer.csv (Kennziffern with BMG and Steuer, Leistungsdatum-aware), index.xml, gdpdu-01-08-2002.dtd. Usually the Steuerberater's export suffices for a Z3 request; use BB's only when access to the BB system itself is demanded. Run it with the Besteuerungsart that applied in the audited year. Ist-Versteuerung re-postings carry journal suffixes. BB can also provide a Z3 dataset within 14 working days (CSV + DATEV-XML Belegbild export; only Belege that are booked or assigned to a posting are exported).
- **Beleg-Archiv (ZIP) import** (*Datenimport*): types "DATEV-Export Belegbilder" (unchanged ZIP with document.xml, for migrations from DATEV/sevDesk/lexoffice), "ZIP mit Eingangsbelegen", "ZIP mit Ausgangsbelegen"; files on the top level only, ≤ 50 MB, formats PDF/JPG/PNG/BMP/TIFF/XML; duplicates can be skipped; import cannot be cancelled and imported Belege are revisionssicher (not deletable); consumes Belegkontingent. Then import the Buchungsstapel with Konfiguration 4 to link.
- **Aufbewahrung**: data kept 10 years GoBD-konform after cancellation (account deactivated, not deleted); reactivation for export/Betriebsprüfung free for 3 days (read-only); reactivation for use by booking a plan. Migration formats: DATEV CSV, ZIP with DATEV-XML, Prüfungsexport.

Source: GDPdU-Export für Betriebsprüfungen erstellen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11445774450973
Source: GoBD konformes Arbeiten mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432424987037
Source: Beleg-Archiv (ZIP) — https://wissen.buchhaltungsbutler.de/hc/de/articles/32109224904221
Source: Kündigung der Services & Aufbewahrungsfristen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11441697058205
Source: Reaktivierung des Accounts nach Kündigung — https://wissen.buchhaltungsbutler.de/hc/de/articles/11441808761117

---

## 9. Belegupload channels and E-Rechnungen

### 9.1 Channels

| Channel | How | Limits / notes |
|---|---|---|
| **E-Mail** | forward to the account-specific addresses (one for Eingangsbelege, one for Ausgangsbelege, domain `belege.buchhaltungsbutler.de`) from *Einstellungen → Belegübertragung*; sender must be an **autorisierte Absenderadresse** (also the original invoice sender when forwarding rules keep the original From); put the Ausgangsbelege address in Bcc of your invoicing tool | attachments ≤ 10 MB; Apple Mail inline attachments (`Content-Disposition: inline`) are not read — send as plain text / "als Anhang versenden"; providers requiring a confirmation code for forwarding (Gmail) need an interim mailbox or Zapier; confirmation e-mail lists successful and failed files |
| **Dropbox** | authorise in *Belegübertragung mit Dropbox*; BB creates `Apps/BuchhaltungsButler/Eingangsrechnungen/<one folder per Basiskonto>` + `Automatische Kontenzuordnung`, and `Ausgangsrechnungen`; files are fetched and **deleted** from Dropbox | drop files only into the lowest-level folders; ≤ 50 files per batch; wait for the confirmation mail before the next batch; never rename/move folders (re-link if broken or if folders for new accounts are missing); uploads stop at the plan's upload limit and resume only after the next new file; Dropbox data-protection caveat (US servers) |
| **Google Drive / OneDrive** | via a Zapier copy-zap into the synced Dropbox folders | choose "copy" not "move" |
| **Manual Drag & Drop** | *Belegverwaltung → Hochladen*, choose Eingang/Ausgang and optionally the Basiskonto (Beleg erzeugt Zahlung) | ≤ 20 files per step; check the count at the bottom of the list as checksum |
| **Scan App** (iOS/Android) | enable in *Belegübertragung*, pair via QR code; several accounts supported; choose Eingang/Ausgang per scan | deleting in the app does not delete in BB; files cannot be moved between accounts afterwards |
| **Scanners / scan apps** | network scanners via scan-to-e-mail (authorise the scanner's address) or scan-to-Dropbox; third-party scan apps via Dropbox | |
| **GetMyInvoices** | *Belegübertragung mit GetMyInvoices*: link, enter BB's API key shown in the popup on the GMI side, set a start date to avoid duplicates | daily sync from ~10,000 portals |
| **invoicefetcher** | *Schnittstellen und API-Zugang → Datenübertragung mit Partnerdiensten*: activate, show API key, enter it at invoicefetcher, set start date | transmits Rechnungsnummer, Datum, Währung, Brutto, computed rate |
| **billbee** | partner link with billbee user + API password; tags `bb_import_started` / `bb_import_done` on invoices; one billbee account ↔ one BB account | payment reference via billbee placeholders |
| **Dropscan** | paper mail scanned and pushed via API | multi-page invoices with paper clips, not staples |
| **API** | `receipts/upload` (file as multipart or base64 + `file_name`), `receipts/add` (no file), `invoices/create*` (creates the Ausgangsbeleg) | 10 uploads/minute; `account` or `creditor_debtor` pre-assignment; `payment_reference` for matching |
| **CSV as debitorische Buchungssätze** | Ausgangsrechnungen without Belegbild (E-Commerce) | originals must be archived revisionssicher elsewhere |
| **Beleg-Archiv ZIP** | bulk migration, §8.7 | |

Source: Belege hochladen und verarbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443147763101
Source: Belegupload per E-Mail funktioniert nicht — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421494594077
Source: E-Mail Weiterleitung benötigt Bestätigungscode — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421952068125
Source: Dropbox-Verknüpfung mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11467978769181
Source: Belegupload via Dropbox funktioniert nicht — https://wissen.buchhaltungsbutler.de/hc/de/articles/11421652514845
Source: Cloud-Dienste ohne direkte Schnittstelle anbinden — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443821190941
Source: Die BuchhaltungsButler Scan App: Belege mobil erfassen und hochladen — https://wissen.buchhaltungsbutler.de/hc/de/articles/31347490191005
Source: Scanlösungen für die Arbeit mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11444507584413
Source: Rechnungen über GetMyInvoices abholen lassen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468222457373
Source: Rechnungen über invoicefetcher abholen lassen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468289726237
Source: billbee Rechnungen automatisch importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11467844244765
Source: Papierrechnungen durch Dropscan importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468196366237

### 9.2 File formats, OCR, upload errors

- Accepted: PDF, JPEG, PNG, TIFF (help center also lists BMP, GIF), **ZUGFeRD** (PDF with embedded XML) and **XRechnung** (XML). API MIME types: `application/pdf`, `text/xml`, `application/xml`, `image/jpeg`, `image/png`, `image/bmp`, `image/tiff`. Max **50 pages** and **20 MB** per file (10 MB via e-mail; API errors 7 "maximum file size is <max>MB", 14 "maximum number of pages").
- OCR (ABBYY) reads **up to page 3**; from 4 pages no automatic recognition — enter data manually. OCR text of documents up to 4 pages is stored for full-text search. Abweichendes Leistungsdatum is never read. A wrongly read tax rate is harmless — the rate chosen at the posting counts. BB learns the Gegenpartei after one correction; complete *Unternehmensdaten* and Kreditor IBAN/USt-ID improve recognition. Distorted preview images are an ABBYY artefact of the optimised copy; the original is untouched — re-scan or re-print to PDF.
- Errors: "Dateityp wird nicht unterstützt" → convert; "Datei kann nicht verarbeitet werden" → write-protected/secured PDF, re-save via online converter or print-to-PDF (API 422/31 "receipt not processable", 422/32 "receipt ocr processing failed"); API 403/12 "customer has reached the upload limit" → buy Belegkontingent (*Tarifinformationen*; one-off packs valid 30 days; deleting Belege does not free quota); 403/15 "upload temporarily restricted".
- Rather than OCR, prefer E-Rechnungen from suppliers: data comes from the XML, no correction needed.

Source: Belege hochladen und verarbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443147763101
Source: Fehlermeldung beim Belegupload — https://wissen.buchhaltungsbutler.de/hc/de/articles/11422121017757
Source: GoBD konformes Arbeiten mit BuchhaltungsButler — https://wissen.buchhaltungsbutler.de/hc/de/articles/11432424987037
Source: Zusätzliche Belege buchen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11441898777757
Source: API spec 1.9.1 (`/receipts/upload`) — https://app.buchhaltungsbutler.de/docs/api/v1/

### 9.3 E-Rechnungen (XRechnung / ZUGFeRD)

- Upload like any other Beleg (manual, e-mail, Dropbox, API). Metadata is taken from the XML; on API upload of an e-invoice the parameters `counterparty`, `invoice_number`, `date`, `amount`, `currency`, `vat_rate`, `payment_reference`, `date_delivery`, `date_payment_due` are **ignored**.
- `receipts/get/id_by_customer` reports `e_invoice_type` (`0` PDF, `1` ZUGFeRD PDF, `2` XRechnung XML) and, with `get_file`, returns the base64 file (`file_type` pdf/xml).
- Creating E-Rechnungen: the invoicing module can produce them (API `invoices/create/e-invoice`); general invoicing rules (Stammdaten, Nummernkreis) apply as for normal invoices.

Source: E-Rechnungen (XRechnung und Zugferd) — https://wissen.buchhaltungsbutler.de/hc/de/articles/20227969805853
Source: API spec 1.9.1 (`/receipts/upload`, `/receipts/get/id_by_customer`) — https://app.buchhaltungsbutler.de/docs/api/v1/

---

## 10. API-relevant limits, gotchas and behaviours from the help center

- **Activation and credentials**: *Einstellungen → Schnittstellen und API-Zugang* → activate → shows API Client, API Secret, API Key. Auth = HTTP Basic with `<API_CLIENT>` / `<API_SECRET>`; `api_key` = `<API_KEY>` in every JSON body; header `Content-Type: application/json`. Test with the BB Postman collection (6 example requests). Support does not debug individual requests.
- **Partner API keys**: for listed partner services (GetMyInvoices, invoicefetcher, billbee, TAXMARO, Dropscan, Gastronovi, Shopify …) you do not use your own credentials; activate the partner in *Schnittstellen und API-Zugang* (GetMyInvoices under *Belegübertragung*) and copy the partner-specific API key displayed there into the partner's settings. Partners let you set an "Importiere ab" date to avoid duplicate Belege.
- **Endpoint groups** named in the help center: Receipts, Transactions (incl. assign/unassign receipt), Invoices (incl. drafts), Postings, Settings (Debitoren/Kreditoren), Accounts (Basiskonten query), Comments. The spec additionally has cost-locations and reports.
- **Rate limits**: all endpoints 100 requests per customer (`api_key`) per minute (docs page; see api.md → Rate limits). Additionally `receipts/upload` max 10 requests/minute. `receipts/get` and `transactions/get` page with `limit` ≤ 500 (`offset`); `postings/get` ≤ 1000 per request and requires `date_from`/`date_to`. Report creation is asynchronous and only one report per type may be in flight.
- **Ids**: `id_by_customer` is the number shown in the UI and is what all posting/assign endpoints need; obtain it via `receipts/get` / `transactions/get` (upload returns `id_by_customer` and `filename`). `date_since_last_modified` / `date_last_action_from` support incremental syncs.
- **Amounts and dates**: transactions signed (+ in / − out), receipts gross with negative = reversal, posting `amounts` as strings `0000.00` summing to the transaction/receipt amount, free posting `amount` positive only; `booking_date` with time, other dates `YYYY-MM-DD`; `date_delivery` ≤ `date`.
- **Postings**: `postings/add/*` creates postings directly — there is no "proposal" state via API *(inferred)*. A transaction with a kreditorisch/debitorisch booked receipt can only be posted against that Personenkonto (error 7); a receipt whose transaction is booked cannot be posted (error 16); a receipt that generated a transaction cannot be posted at the receipt (error 14). Receipt postings need Deb/Kred active. Foreign currency: transaction postings error 25 "foreign currencies can only be posted to account X" — get the converted amount first. `postings/cancel` deletes unfixed, reverses fixed; `unconfirm/*` only unfixed. No API for Festschreibung, Belegzuweisung aufheben at fixed level, transaction deletion, USt.-VA, ZM, exports.
- **Belegmatching via API/import**: always send `payment_reference` on both sides; matching window 90 days before / 30 days after the Zahlung; exact amount required; several Belege per Zahlung only manually (`transactions/assign/receipt` repeatedly or `assign-batch`); `link_to_receipt_id_by_customer` couples two Belege (e.g. invoice + Gutschrift) so both are assigned when one is.
- **Accounts**: `accounts/add` validates number ranges per Kontenrahmen (§5.3) and digit count (Sachkontenlänge); `receipt_creates_transaction`, `is_revision_safe` (cash only). `accounts/get` lists payment accounts only — use it to detect SKR03 (1200/1000) vs SKR04 (1800/1600). `settings/add/creditor|debtor` auto-number if `postingaccount_number` is omitted; `country` German name or ISO-2; duplicate names are rejected on CSV import.
- **Comments**: `comments/add` 2–210 chars, exactly one of transaction/receipt id; comments appear in exports.
- **Invoices**: `invoices/create` posts a final Ausgangsbeleg (negative total = Rechnungskorrektur); `date_of_supply` becomes date_delivery only in `YYYY-MM-DD` and if ≤ date; BB assigns its default sequential invoice number unless `invoicenumber` is given (Nummernkreis configured under *Einstellungen → Rechnungseinstellungen*); `payment_reference` supports Amazon/PayPal/Stripe ids.
- **Bank data gotchas that affect API consumers**: duplicates arise from re-linking a bank without "Importiere ab" or CSV import next to a live link; PayPal via finAPI lacks fees (use the direct integration); interfaces may miss transactions — reconcile with "Kontostand berechnen". Deleted duplicate transactions must be removed in the UI.
- **Mehrwertsteuersenkung leftovers**: vat codes labelled "19/16%"/"7/5%" are date-dependent implicit rates; explicit codes (`19_vat`, `19_pre`, `19_both_1`, `19_both_2`, `7_both`) always mean the old (regular) rate; error 42 on receipt postings flags a rate not valid for the date.

Source: Einrichtung der API-Schnittstelle — https://wissen.buchhaltungsbutler.de/hc/de/articles/11468075328797
Source: Belege hochladen und verarbeiten — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443147763101
Source: Belegmatching verstehen und optimieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11443781087389
Source: Import von doppelten Zahlungen — https://wissen.buchhaltungsbutler.de/hc/de/articles/11423965528605
Source: PayPal Konto verbinden und Umsätze importieren — https://wissen.buchhaltungsbutler.de/hc/de/articles/11477160952349
Source: Software-Änderungen | Mehrwertsteuersenkung 2020 — https://wissen.buchhaltungsbutler.de/hc/de/articles/11282864819357
Source: API spec 1.9.1 — https://app.buchhaltungsbutler.de/docs/api/v1/
