# German bookkeeping and tax compliance for a small UG (haftungsbeschränkt)

Reference for keeping the books of a small software/consulting **UG (haftungsbeschränkt)** (entrepreneurial company with limited liability, a GmbH variant with < 25.000 € share capital) in BuchhaltungsButler (BB) on the DATEV SKR03 or SKR04 chart. Status: 2026-09-13. Every figure carries its source; anything not confirmed against a primary or reputable source is marked **(unverified)**. Where a value changed between 2024 and 2026 the old value, new value and effective date are given. German legal/UI terms are **bold** on first use with an English gloss, then used as-is.

Conventions: `SKR03 | SKR04` account pairs; DATEV **BU-Schlüssel** (Buchungsschlüssel = tax key) as `BU 9`; BB `vat` codes in backticks (`19_pre`) as listed in `references/api.md` §VAT codes; UStVA **Kennzahl** (form field code) as `Kz 81`. Laws: UStG (VAT act), UStDV (VAT ordinance), EStG (income tax act), KStG (corporation tax act), GewStG (trade tax act), AO (fiscal code), HGB (commercial code), GmbHG.

---

## 1. Basics

### 1.1 Belegprinzip and GoBD

- **Belegprinzip** ("keine Buchung ohne Beleg", no entry without a voucher): every posting must be traceable to a **Beleg** (voucher: invoice, receipt, contract, bank statement line, or a self-made **Eigenbeleg**). Belegfunktion is part of the **GoBD** (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff), BMF letter of 28.11.2019, amended by BMF letter of 11.03.2024 (IV D 2 - S 0316/21/10001 :002), in force since 01.04.2024 (→ https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2024-03-11-aenderung-gobd.pdf?__blob=publicationFile&v=4 ; summary → https://www.ihk.de/osnabrueck/recht-und-fair-play/steuerrecht/aktuell/bmf-veroeffentlicht-neufassung-der-gobd-6486906). The 2024 revision is mostly editorial (e.g. "Datenträgerüberlassung" → "Datenüberlassung", mobile scanning/cloud clarified).
- GoBD essentials: **Nachvollziehbarkeit/Nachprüfbarkeit** (a third party must be able to follow every entry from Beleg to Bilanz and back), **Vollständigkeit** (every transaction, Einzelaufzeichnungspflicht), **Richtigkeit**, **zeitgerecht** (timely), **Ordnung**, **Unveränderbarkeit** (§ 146 Abs. 4 AO; changes only via traceable Storno/reversal).
- Timeliness: **Kasseneinnahmen und Kassenausgaben sind täglich festzuhalten** (§ 146 Abs. 1 Satz 2 AO → https://www.gesetze-im-internet.de/ao_1977/__146.html). Non-cash transactions: recording within 10 days is "unbedenklich"; with periodic bookkeeping they must be recorded and **festgeschrieben** (locked) by the end of the following month (GoBD Rz. 47–50 as summarised → https://www.haufe.de/id/beitrag/gobd-von-a-wie-aufzeichnungen-bis-z-wie-zwangsgeld-126-festschreibung-der-buchfuehrung-HI9892666.html). In BB: **Festschreibung** = "Buchungen festschreiben" for the month; locked postings can only be reversed (GU key export), not edited.
- **Verfahrensdokumentation** (process documentation): describes how Belege are received, digitised, booked, archived and who may change what. Required for electronic bookkeeping; its absence alone is not a formal defect if traceability is otherwise given, but auditors ask for it (GoBD Rz. 151 ff., unverified paragraph number). Keep it as a short living document: tools (BB, bank feeds, mail import), naming, retention, access rights.
- **Datenzugriff** in a Betriebsprüfung (tax audit): § 147 Abs. 6 AO gives the auditor three modes: **Z1** unmittelbarer Zugriff (read-only access to the live system), **Z2** mittelbarer Zugriff (you run evaluations for the auditor), **Z3** Datenüberlassung (export on a data carrier; the "GDPdU-/DATEV-Export", today the GoBD export) (→ https://www.gesetze-im-internet.de/ao_1977/__147.html). BB provides the DATEV/GoBD export; keep the Verfahrensdokumentation next to it.

### 1.2 Doppelte Buchführung, Soll/Haben, account types

- A UG is a **Formkaufmann** (merchant by legal form, § 13 Abs. 3 GmbHG, § 6 HGB) → **Buchführungspflicht** under §§ 238 ff. HGB and § 140 AO, **doppelte Buchführung** (double-entry) with **Inventur**, **Bilanz** and **GuV**; the Einnahmen-Überschuss-Rechnung (§ 4 Abs. 3 EStG) is not available to a UG regardless of size.
- **Buchungssatz** is written "Soll an Haben" (debit to credit). Rules by account type:

| Account type | Increase | Decrease | Opening balance side | Examples |
|---|---|---|---|---|
| **Aktivkonto** (asset) | Soll | Haben | Soll | Bank, Kasse, Forderungen, Anlagen, Vorsteuer |
| **Passivkonto** (liability/equity) | Haben | Soll | Haben | Verbindlichkeiten, Stammkapital, Rücklagen, Umsatzsteuer |
| **Aufwandskonto** (expense) | Soll | Haben (corrections) | — closes to GuV | Miete, Gehälter, Fremdleistungen |
| **Ertragskonto** (revenue) | Haben | Soll (corrections) | — closes to GuV | Umsatzerlöse, Zinserträge |

- Expense paid by bank: `Aufwand (Soll) + Vorsteuer (Soll) an Bank (Haben)`. Sales invoice: `Forderungen (Soll) an Erlöse (Haben) + Umsatzsteuer (Haben)`. In BB you choose the **Sachkonto** (contra account) and the `vat` code; BB books the Vorsteuer/Umsatzsteuer accounts itself (they cannot be posted directly).

Worked Buchungssätze (SKR03 | SKR04; BB derives the tax lines from the `vat` code, you only name the Sachkonto):
- Supplier invoice 1.190 € incl. 19 %: `4930 | 6815 Bürobedarf 1.000 + 1576 | 1406 Vorsteuer 190 an 1600 | 3300 Verbindlichkeiten 1.190`; payment `1600 | 3300 an 1200 | 1800 Bank 1.190`.
- Own invoice 5.950 € incl. 19 %: `1400 | 1200 Forderungen 5.950 an 8400 | 4400 Erlöse 5.000 + 1776 | 3806 Umsatzsteuer 950`; receipt `Bank an Forderungen`.
- EU SaaS 100 € reverse charge: `3123 | 5923 Aufwand 100 + 1577 | 1407 Vorsteuer § 13b 19 an 1600 | 3300 100 + 1787 | 3837 Umsatzsteuer § 13b 19` — tax lines net to zero, both appear in the UStVA.
- Salary of the GGF: `4124 | 6024 Gehalt 4.000 an 1740 | 3720 Nettolohn 3.300 + 1741 | 3730 Lohnsteuer 700`.
- Year-end AfA: `4830 | 6220 Abschreibungen an 0410 | 0635 Geschäftsausstattung`.
- Correction: never delete a festgeschriebene Buchung; reverse it (BB `postings/cancel`, exported with the GU key) and post anew with a reference to the original.

### 1.3 SKR03 vs SKR04 Kontenklassen

SKR03 follows the **Prozessgliederungsprinzip** (process order), SKR04 the **Abschlussgliederungsprinzip** (financial-statement order, mirrors §§ 266/275 HGB) (→ https://www.datev.de/web/de/berufsgruppenuebergreifend/ratgeber/rechnungswesen/datev-standard-kontenrahmen ; → https://ebilanzplus.de/blog/die-unterschiede-zwischen-den-datev-kontenrahmen-skr-03-und-skr-04). Both are DATEV standards, updated yearly (2026 PDFs: DATEV Dok. 0907817 → https://www.datev.de/hilfe/0907817).

| Klasse | SKR03 | SKR04 |
|---|---|---|
| 0 | Anlage- und Kapitalkonten (assets and equity/long-term liabilities) | Anlagevermögen |
| 1 | Finanz- und Privatkonten (bank, receivables, VAT, short-term payables) | Umlaufvermögen (receivables, bank, Vorsteuer) |
| 2 | Abgrenzungskonten (neutral expense/income, taxes on income) | Eigenkapital |
| 3 | Wareneingang, Fremdleistungen, Bestände | Fremdkapital (payables, Umsatzsteuer) |
| 4 | Betriebliche Aufwendungen (all operating expenses) | Betriebliche Erträge (revenues) |
| 5–6 | free (5) / free (6) | 5 Materialaufwand, Fremdleistungen; 6 Betriebliche Aufwendungen |
| 7 | Bestände an Erzeugnissen | Weitere Erträge/Aufwendungen (Zinsen, Steuern) |
| 8 | Erlöskonten | free |
| 9 | Vortrags-, Kapital-, statistische Konten | Vortrags- und statistische Konten |

BB tells you the chart in use: Bank 1200/Kasse 1000 = SKR03; Bank 1800/Kasse 1600 = SKR04.

### 1.4 Bilanz, GuV, BWA, SuSa

- **Bilanz** (balance sheet): assets vs equity+liabilities at the **Abschlussstichtag**; structure § 266 HGB, small companies may use the verkürzte Bilanz (§ 266 Abs. 1 Satz 3 HGB).
- **GuV** (Gewinn- und Verlustrechnung, income statement): § 275 HGB, Gesamtkostenverfahren usual; Kleinstkapitalgesellschaften may use the condensed form (§ 275 Abs. 5 HGB).
- **BWA** (Betriebswirtschaftliche Auswertung): management report derived from the GuV accounts for a period, not a legal document; DATEV "Standard-BWA" layout; useful for monthly review (BB: `reports/create/bwa`).
- **SuSa** (Summen- und Saldenliste): per-account debit/credit totals and balances for a period — the audit trail between Buchungen and Bilanz; check it before the Steuerberater export (BB: `reports/create/sums`).
- **Jahresabschluss** = Bilanz + GuV (+ Anhang unless Kleinst-relief) + for the Steuererklärung the **E-Bilanz** (§ 5b EStG, see §5).

### 1.5 Aufbewahrungsfristen (retention periods)

Changed by the **Viertes Bürokratieentlastungsgesetz** (BEG IV) with effect from 01.01.2025: **Buchungsbelege** 10 → 8 years (§ 147 Abs. 3 AO, § 257 Abs. 4 HGB, § 14b Abs. 1 UStG); applies to all documents whose 10-year period had not expired on 31.12.2024 (→ https://www.gesetze-im-internet.de/ao_1977/__147.html ; → https://www.gesetze-im-internet.de/hgb/__257.html ; → https://www.haufe.de/finance/buchfuehrung-kontierung/aufbewahrungsfristen-welche-unterlagen-vernichtet-werden-koennen_186_432446.html ; → https://www.ihk-muenchen.de/ratgeber/steuern/finanzverwaltung/aufbewahrungsfristen/).

| Document class (§ 147 Abs. 1 AO) | Period | Note |
|---|---|---|
| Bücher, Aufzeichnungen, Inventare, Jahresabschlüsse, Lageberichte, Eröffnungsbilanz, Arbeitsanweisungen/Organisationsunterlagen (incl. Verfahrensdokumentation) (Nr. 1, 4a) | **10 years** | unchanged |
| **Buchungsbelege** (Nr. 4): invoices in/out, receipts, bank statements, Reisekostenabrechnungen, Bewirtungsbelege, Lohnunterlagen as far as Belege | **8 years** (was 10 until 31.12.2024) | § 14b UStG for Rechnungen likewise 8 years; banks/insurers keep 10 years (§ 257 Abs. 4 Satz 2 HGB) |
| Handels-/Geschäftsbriefe received and sent, sonstige steuerrelevante Unterlagen (Nr. 2, 3, 5) | **6 years** | e-mails with contractual content are Geschäftsbriefe |

Period starts at the end of the calendar year of the last entry / document creation (§ 147 Abs. 4 AO); it does not end while the documents matter for an open tax assessment (§ 147 Abs. 3 Satz 5 AO). Electronic originals (E-Rechnung XML, PDFs, bank exports) must stay in their original machine-readable form (GoBD); paper scanned according to the Verfahrensdokumentation may be destroyed (except documents whose original matters, e.g. notarial deeds, Zollbelege).

### 1.6 Kassenbuch (cash book)

- Duty exists only if the company handles cash. **Kasseneinnahmen und Kassenausgaben sind täglich festzuhalten** (§ 146 Abs. 1 Satz 2 AO); the cash book must be **kassensturzfähig** (book balance = counted cash at any time) (→ https://www.gesetze-im-internet.de/ao_1977/__146.html). A pure bank/card UG with no cash needs no Kassenbuch; then keep Kasse 1000 | 1600 at zero and pay small cash outlays privately, reimbursed via Reisekostenabrechnung/Auslagen (Gesellschafter-Verrechnungskonto, §6).
- Electronic cash registers need a certified **TSE** (§ 146a AO, KassenSichV) and must be reported to the Finanzamt via ELSTER (Meldepflicht since 01.01.2025: systems bought before 01.07.2025 by 31.07.2025, later ones within one month) (→ https://finanzamt.hessen.de/service/finanzaemter-in-hessen/mitteilungspflicht-fuer-kassensysteme-und-taxameter). Not relevant for a software UG without a till.

### 1.7 Eigenbeleg (self-made voucher)

Accepted only if no third-party voucher exists (tip, coin parking meter, market stall, vending machine) or the original is demonstrably lost; content: payee name/address (if known), date, nature of expense, amount, reason for the Eigenbeleg, date and signature of the person creating it (→ https://onlinebilanz.de/eigenbeleg-erstellen-pflichtinhalte-zulaessige-faelle/ ; → https://www.mobilexpense.com/de/blog/eigenbeleg-fehlende-belege). **No Vorsteuerabzug** from an Eigenbeleg (§ 15 Abs. 1 Nr. 1 UStG requires a Rechnung). Keep them rare; frequent Eigenbelege are an audit flag. The Bewirtungsbeleg's "Angaben zum Anlass und zu den Teilnehmern" is itself an Eigenbeleg attached to the restaurant bill (BMF 19.11.2025 Rz. 1–2, see §4.7).

### 1.8 Rechnung: Pflichtangaben § 14 Abs. 4 UStG, Kleinbetragsrechnung § 33 UStDV, Fahrausweise § 34 UStDV

Full invoice (§ 14 Abs. 4 Satz 1 UStG → https://www.gesetze-im-internet.de/ustg_1980/__14.html):
1. full name and address of supplier **and** recipient;
2. supplier's **Steuernummer** or **USt-IdNr**;
3. **Ausstellungsdatum** (issue date);
4. unique, sequential **Rechnungsnummer**;
5. quantity and customary description of goods / scope and nature of the service;
6. **Zeitpunkt der Leistung** (delivery/service date; for advance payments the date of receipt if it differs from the issue date) — the month suffices (§ 31 Abs. 4 UStDV); if identical to the issue date the phrase "Leistungsdatum entspricht Rechnungsdatum" is enough (BFH 17.12.2008 XI R 62/07 as cited → https://www.haufe.de/steuern/finanzverwaltung/vorsteuerabzug-rechnungsangabe-leistungszeitpunkt_164_551000.html);
7. **Entgelt** (net) broken down by tax rate and exemption, plus any pre-agreed reduction (Skonto terms, Rabatt);
8. **Steuersatz** and **Steuerbetrag**, or a reference to the exemption;
9. reference to the recipient's Aufbewahrungspflicht in the case of § 14b Abs. 1 Satz 5 (works on buildings for non-businesses);
10. the word **"Gutschrift"** when the recipient issues the invoice (self-billing).
Additional duties § 14a UStG: for i.g. Lieferungen and EU B2B services both parties' USt-IdNr; for reverse charge the words **"Steuerschuldnerschaft des Leistungsempfängers"** (§ 14a Abs. 5, Abs. 1 UStG → https://www.gesetze-im-internet.de/ustg_1980/__14a.html); for Kleinunternehmer a reference to § 19 (§ 34a UStDV); for Reiseleistungen/Differenzbesteuerung the respective phrase.

**Kleinbetragsrechnung** (§ 33 UStDV → https://www.gesetze-im-internet.de/ustdv_1980/__33.html): gross total **≤ 250 €** (since 2017; before 150 €). Minimum content: supplier name and address, issue date, quantity/description, gross amount with the **tax rate** (or exemption note). Recipient name, invoice number and separate tax amount are not required; Vorsteuer is calculated by splitting the gross (§ 35 Abs. 1 UStDV: 19/119 or 7/107 → https://www.gesetze-im-internet.de/ustdv_1980/__35.html). Not allowed for i.g. Lieferungen, reverse-charge supplies (§ 13b) or § 3c distance sales (§ 33 Satz 3 UStDV).

**Fahrausweise** (tickets, § 34 UStDV → https://www.gesetze-im-internet.de/ustdv_1980/__34.html): count as invoices if they show the carrier's name/address, issue date, gross amount and the tax rate when it is not 7 % (rail: no rate needed since Schienenbahn is 7 % at all distances). Vorsteuer via § 35 Abs. 2 UStDV split; only for journeys inside Germany for the business (commuting tickets of employees are not "für das Unternehmen").

### 1.9 Vorsteuerabzug § 15 UStG — checklist

Deduct German VAT only if all hold (§ 15 Abs. 1 Satz 1 Nr. 1 UStG → https://www.gesetze-im-internet.de/ustg_1980/__15.html):
1. supplier is an Unternehmer and the tax is legally owed for this supply (VAT shown wrongly, § 14c UStG, is never deductible);
2. the supply is for the company (≥ 10 % business use; 100 % for a UG normally — private use of the Gesellschafter is a **vGA** issue, not an "Entnahme");
3. you hold a **proper invoice** (§§ 14, 14a; e-invoice rules §3) — for Kleinbeträge/Fahrausweise the reduced content; for § 13b reverse charge the deduction (§ 15 Abs. 1 Nr. 4) does not depend on a formally complete invoice (UStAE 15.10 Abs. 1, not re-verified);
4. the supply has been performed (or, for a prepayment invoice, paid) — deduction in the Voranmeldungszeitraum in which both conditions are met, not earlier and not later at will;
5. no exclusion: § 15 Abs. 1a UStG (costs non-deductible under § 4 Abs. 5 Nr. 1–4, 7 EStG: gifts > 50 €, Gästehäuser, Jagd/Yacht, unangemessene Repräsentation — but **Bewirtung**: Vorsteuer 100 % deductible although 30 % of the cost is not; § 15 Abs. 1a Satz 2), § 15 Abs. 2 (inputs for exempt outputs without VSt-Abzug), § 15 Abs. 1b (mixed-use real estate).
Foreign VAT (Irish, Austrian, US sales tax …) is **never** Vorsteuer in the UStVA (§2.10). Vorsteuer from Ist-Versteuerer invoices: the JStG 2024 ties the deduction to payment and adds the invoice note "Versteuerung nach vereinnahmten Entgelten" (§ 14 Abs. 4 Nr. 6a, § 15 Abs. 1 Nr. 1 UStG n.F.) — effective for invoices issued after 31.12.2027 (§ 27 Abs. 41 UStG; the Regierungsentwurf's 2026 date was moved in the enacted JStG 2024) (→ https://www.zdh.de/ueber-uns/fachbereich-steuern-und-finanzen/editorial/jahressteuergesetz-2024-die-umsatzsteuer-wird-ab-dem-jahr-2026-wieder-ein-stueck-komplizierter/).

### 1.10 Leistungsdatum and Steuerentstehung

- Under **Sollversteuerung** (§ 13 Abs. 1 Nr. 1a UStG → https://www.gesetze-im-internet.de/ustg_1980/__13.html) VAT arises at the end of the Voranmeldungszeitraum in which the supply is performed — not when invoiced or paid. Prepayments: when received. Under **Istversteuerung** (Nr. 1b): when the payment is received.
- Book revenue and expense in the period of the **Leistungsdatum**; the Rechnungsdatum only dates the Beleg. Year-end: invoices dated January for December work belong to December (Forderung/Verbindlichkeit or Rückstellung), and vice versa (RAP §§ 250 HGB).
- **Dauerleistungen** (subscriptions, retainer, hosting): each billing period is a **Teilleistung**; the invoice must show the **Leistungszeitraum** (e.g. "01.03.–31.03.2026"); annual prepaid SaaS is expensed via **aktive Rechnungsabgrenzung** (0980 | 1900 Aktive Rechnungsabgrenzung; passive side 0990 | 3900; DATEV 2026) across the months if material.

---

## 2. Umsatzsteuer (VAT)

### 2.1 Rates and categories

| Category | Rule | Typical items for a tech UG |
|---|---|---|
| **19 %** Regelsteuersatz | § 12 Abs. 1 UStG | software, consulting, hardware, ads, coworking, flights inland, beverages |
| **7 %** ermäßigt | § 12 Abs. 2 UStG (→ https://www.gesetze-im-internet.de/ustg_1980/__12.html) | Nr. 1/Anlage 2: books, newspapers, food; Nr. 10: **Personenbeförderung** — Schienenbahn at any distance (since 01.01.2020), bus/taxi/ship only within one Gemeinde or ≤ 50 km; Nr. 11: **Beherbergung** (hotel room; not "Leistungen, die nicht unmittelbar der Vermietung dienen", i.e. breakfast, parking, WLAN are separate — the Aufteilungsgebot was upheld by the ECJ on 05.03.2026, C-409/24 to C-411/24 as reported → https://hannes-kollegen.mynewsdesk.com/news/umsatzsteuer-aufteilungsgebot-fuer-hotel-nebenleistungen-7-oder-19-prozent-507919); Nr. 15: **Restaurant- und Verpflegungsdienstleistungen** except beverages — permanent 7 % since 01.01.2026 (Steueränderungsgesetz 2025; 2024–2025 it was 19 %) (→ https://www.ihk.de/darmstadt/produktmarken/recht-und-fair-play/steuerinfo/mehrwertsteuersenkung-fuer-die-gastronomie-ab-2026-6927450) |
| **0 %** | § 12 Abs. 3 UStG (photovoltaic) | irrelevant here; do not confuse with "steuerfrei" |
| **steuerfrei mit Vorsteuerabzug** | § 4 Nr. 1a (Ausfuhr), Nr. 1b (i.g. Lieferung), Nr. 2–7 | goods exported / shipped B2B into the EU |
| **steuerfrei ohne Vorsteuerabzug** | § 4 Nr. 8 (finance, payment services), Nr. 9a (land), Nr. 11 (insurance brokerage), Nr. 12 (letting), Nr. 14 (health), Nr. 21 (education) | bank/card/payment-processor fees, insurance, rent without option |
| **nicht steuerbar** | place of supply outside Germany (§ 3a Abs. 2 B2B services) | services to EU/non-EU business customers |

Restaurant bills since 2026 carry two rates (food 7 %, drinks 19 %); a combined price may be split with 30 % of the price attributed to drinks without objection (IHK Darmstadt → same URL as above). Hotel: room 7 %, breakfast food 7 % since 2026, breakfast drinks/parking/WLAN 19 %; for "Business Packages" the 19 % share may be set at 15 % of the package price (Servicepauschale, UStAE 12.16 as reported → https://www.ihk.de/schleswig-holstein/recht/steuern/aktuelles/mehrwertsteuer-in-gastronomie-6932586).

### 2.2 Soll- vs Ist-Versteuerung

- Default **Sollversteuerung** (accrual, § 16 Abs. 1 UStG). **Istversteuerung** (§ 20 UStG → https://www.gesetze-im-internet.de/ustg_1980/__20.html) on application if the previous year's Gesamtumsatz did not exceed **800.000 €** (raised from 600.000 € by the Wachstumschancengesetz, effective VZ 2024 → https://www.lexware.de/wissen/buchhaltung-finanzen/umsatzsteuerliche-ist-versteuerung-alle-infos/), or if exempt from bookkeeping (§ 148 AO), or for Freiberufler income (a UG has Gewerbe income, so only the turnover route applies).
- Effect: VAT due when paid → liquidity; Vorsteuer deduction stays invoice-based (until the 2028 change in §1.9). Apply once at the Finanzamt (Fragebogen zur steuerlichen Erfassung or later letter). Tell BB/Steuerberater which regime applies — BB's UStVA figures depend on it.

### 2.3 Kleinunternehmer § 19 UStG (2025 reform)

- Since 01.01.2025 (Jahressteuergesetz 2024): supplies are **steuerfrei** if the previous year's Gesamtumsatz ≤ **25.000 €** and the current year's ≤ **100.000 €** (before 2025: 22.000 € / 50.000 € forecast, and the tax was merely "nicht erhoben") (§ 19 Abs. 1 UStG → https://www.gesetze-im-internet.de/ustg_1980/__19.html ; → https://www.ihk.de/stuttgart/fuer-unternehmen/recht-und-steuern/steuerrecht/umsatzsteuer-national/kleinunternehmerregelung-in-der-umsatzsteuer-1843632). Crossing 100.000 € switches to Regelbesteuerung from that very Umsatz (no year-end grace). No Vorsteuerabzug (unechte Befreiung). **Verzicht** (opt-out) binds for at least five calendar years (§ 19 Abs. 3).
- Kleinunternehmer file no UStVA and, since VZ 2024, no annual USt-Erklärung unless asked or unless they owe VAT under § 13b / i.g. Erwerb (§ 18 Abs. 4a UStG → https://www.haufe.de/finance/buchfuehrung-kontierung/kleinunternehmer-wann-ist-eine-ust-erklaerung-abzugeben_186_396414.html). Simplified invoices (§ 34a UStDV); must receive E-Rechnungen but need not issue them. New **EU-Kleinunternehmerregelung** § 19a for other member states (EU-wide 100.000 €).
- For a B2B software UG the regime is rarely useful (customers deduct VAT anyway; the UG loses Vorsteuer on hardware/SaaS); usually opt out in the Fragebogen.

### 2.4 UStVA (Umsatzsteuer-Voranmeldung) rhythm, due dates, Dauerfrist

- **Voranmeldungszeitraum** (§ 18 Abs. 2, 2a UStG → https://www.gesetze-im-internet.de/ustg_1980/__18.html): quarter by default; **monthly** if the previous year's VAT (Zahllast) exceeded **9.000 €** (2025+; **7.500 €** until 2024, BEG IV); **no UStVA** (annual return only) if the previous year's VAT ≤ **2.000 €** (2025+; 1.000 € until 2024) and the Finanzamt exempts you; monthly by choice if the previous year showed a **refund** > 9.000 €. New businesses must file monthly in the founding year and the next — but this rule is **suspended for 2021–2026** (§ 18 Abs. 2 Satz 6), so a UG founded in 2026 starts quarterly unless the projected tax exceeds 9.000 € (→ https://www.haufe.de/id/beitrag/umsatzsteuer-voranmeldung-2026-15-voranmeldung-bei-beginn-der-unternehmerischen-taetigkeit-HI16943563.html). From 2027 the monthly-for-founders rule returns unless extended **(watch for a change)**.
- Due: **10th day** after the period (§ 18 Abs. 1), shifting to the next Werktag if it falls on a weekend/holiday (§ 108 Abs. 3 AO); ELSTER/ERiC transmission with certificate; payment by the same day (3-day **Schonfrist** § 240 Abs. 3 AO applies to bank transfers, not to filing).
- **Dauerfristverlängerung** (§§ 46–48 UStDV → https://www.gesetze-im-internet.de/ustdv_1980/__47.html): +1 month for filing and paying. Monthly filers must pay a **Sondervorauszahlung** of **1/11** of the previous year's Vorauszahlungen, declared and paid with the first UStVA of the year (by 10.02.), credited in the December UStVA (**Kz 39**). Quarterly filers apply by 10.04. and pay no Sondervorauszahlung (→ https://www.steuerschroeder.de/Steuerrechner/Dauerfristverlaengerung.html). Accounts: 1781 | 3830 "Umsatzsteuer-Vorauszahlungen 1/11".
- **Verspätungszuschlag** (§ 152 AO → https://www.gesetze-im-internet.de/ao_1977/__152.html): annual returns: 0,25 % of the (reduced) tax per month, min. 25 €/month (§ 152 Abs. 5 Satz 2); for monthly/quarterly Voranmeldungen and the Sondervorauszahlung Abs. 5 does not apply (§ 152 Abs. 8) — the Finanzamt sets the Zuschlag at its discretion by duration, frequency and tax amount; no statutory minimum. Automatic when the annual return is more than 14 months late.
- **USt-Jahreserklärung** (§ 18 Abs. 3): deadlines of § 149 AO (see §5). Differences to the sum of the UStVAs are settled within one month of filing.

UStVA 2026 form fields that matter for a tech UG (BMF Vordruckmuster 2026 → https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Umsatzsteuer/2025-12-29-vordruckmuster-USt-voranmeldung-2026.pdf?__blob=publicationFile&v=7):

| Kz | Content | Typical source |
|---|---|---|
| 81 / 86 | taxable turnover 19 % / 7 % (net) | 8400 \| 4400, 8300 \| 4300 |
| 41 | i.g. Lieferungen § 4 Nr. 1b | 8125 \| 4125 (+ ZM) |
| 43 | other exempt with VSt (exports § 4 Nr. 1a) | 8120 \| 4120 |
| 48 | exempt without VSt (§ 4 Nr. 8–29, § 19) | rare |
| 89 / 93 | i.g. Erwerb 19 % / 7 % (base + tax) | BU 19 / 18 |
| 46 / 47 | § 13b Abs. 1 services from EU businesses (base / tax) | 3123 \| 5923, BU 94 |
| 84 / 85 | other § 13b Abs. 2 cases incl. Nr. 1 non-EU services (base / tax) | 3125 \| 5925 |
| 60 | your own supplies where the customer owes German VAT (§ 13b Abs. 5, e.g. Bauleistungen) | 8337 \| 4337, BU 46 |
| 21 | non-taxable EU B2B services § 18b Satz 1 Nr. 2 (must match the ZM) | 8336 \| 4336, BU 47 |
| 45 | other non-taxable turnover (place of supply abroad: non-EU services, OSS) | 8338 \| 4338, 8339 \| 4339 |
| 66 | Vorsteuer from invoices | 1571/1576 \| 1401/1406 |
| 61 | Vorsteuer from i.g. Erwerb | 1574 \| 1404 |
| 67 | Vorsteuer from § 13b | 1577 \| 1407 |
| 39 | Sondervorauszahlung credited (December) | 1781 \| 3830 |
| 83 | remaining payment (negative = refund) | |

### 2.5 Zusammenfassende Meldung (ZM, § 18a UStG)

- Report to the BZSt (ELSTER/BOP) the USt-IdNr and net amount of every EU B2B customer for **i.g. Lieferungen** and **§ 3a Abs. 2 services** (and Dreiecksgeschäfte). Deadline **25th day** after the reporting period; goods **monthly**, or quarterly if i.g. Lieferungen did not exceed **50.000 €** in the current and the four previous quarters; services always quarterly (in a monthly ZM they go into the last month of the quarter) (§ 18a Abs. 1, 2 UStG → https://www.gesetze-im-internet.de/ustg_1980/__18a.html ; → https://www.bzst.de/DE/Unternehmen/Umsatzsteuer/ZusammenfassendeMeldung/Fristen/fristen.html). No Dauerfristverlängerung for the ZM. Nil periods: no ZM.
- A missing or wrong ZM removes the exemption of the i.g. Lieferung (§ 4 Nr. 1b Satz 2 UStG → https://www.gesetze-im-internet.de/ustg_1980/__4.html). Kz 41 and Kz 21 of the UStVAs must reconcile to the ZM.
- **USt-IdNr check**: BZSt **Bestätigungsverfahren** (§ 18e UStG → https://www.gesetze-im-internet.de/ustg_1980/__18e.html): einfache Abfrage (valid?) or **qualifizierte Abfrage** (name/address match) via the BZSt portal or its XML-RPC interface; keep the confirmation (print/PDF or the returned record) with the customer master data; re-check periodically and before large invoices.

### 2.6 Reverse charge § 13b UStG (Steuerschuldnerschaft des Leistungsempfängers)

(§ 13b UStG → https://www.gesetze-im-internet.de/ustg_1980/__13b.html)

| Case | Norm | Tax arises | UStVA | DATEV accounts / BU |
|---|---|---|---|---|
| Services from a business in another EU state, place of supply Germany under § 3a Abs. 2 (SaaS, ads, cloud, consulting, licences) | § 13b **Abs. 1** | end of the Voranmeldungszeitraum in which the service is performed | Kz 46/47 + VSt Kz 67 | 3123 \| 5923 (Automatikkonto) or any expense account with **BU 94**; BB `19_both_506` |
| Werklieferungen and other services of a business established **abroad** (non-EU vendor; also EU vendor for services not under § 3a Abs. 2, e.g. real-estate related) | § 13b **Abs. 2 Nr. 1** | on invoice issue, at latest end of the month following performance | Kz 84/85 + Kz 67 | 3125 \| 5925 (Automatikkonto); BB `19_both_511` |
| Bauleistungen | Abs. 2 Nr. 4 | as Nr. 1 | 84/85 | only if the recipient itself performs Bauleistungen (§ 13b Abs. 5 Satz 2) — not a software UG; 3120 \| 5920 |
| Gas/electricity, Gebäudereinigung, Schrott/Altmetall, Gold, Telekommunikation (Wiederverkäufer) | Abs. 2 Nr. 5, 7, 8, 9, 12 | | 84/85 | recipient must be Wiederverkäufer/cleaner — usually not applicable |
| Mobile phones, tablets, game consoles, integrated circuits, bought **domestically** with ≥ **5.000 €** per economic transaction | Abs. 2 Nr. 10 | | 84/85 | applies even to a German supplier — the invoice then shows no VAT |
| Emission certificates, Edelmetalle etc. | Abs. 2 Nr. 6, 11 | | | rare |

Rules: the recipient owes the VAT if it is an Unternehmer or juristische Person (Abs. 5); it deducts the same amount as Vorsteuer in the same period (§ 15 Abs. 1 Nr. 4) → cash-neutral, but the amounts must appear in the UStVA. Supplier's invoice: no VAT, note "Steuerschuldnerschaft des Leistungsempfängers"/"Reverse charge", both USt-IdNr. If the foreign supplier charged its home VAT anyway (your USt-IdNr not on file), you still owe German § 13b VAT on the Entgelt and cannot deduct the foreign VAT — request a corrected invoice (→ https://www.datev-community.de/t5/Betriebliches-Rechnungswesen/Reverse-Charge-amp-falsche-Umsatzsteuer-auf-Rechnungen-aus-dem/td-p/481755). If a foreign supplier charged **German** VAT to a business customer (OSS-registered consumer invoicing), that VAT is § 14c "unrichtig ausgewiesen" and not deductible either.

### 2.7 Innergemeinschaftlicher Erwerb (i.g.E., goods from the EU)

- Buying goods from an EU business that ships them to Germany, quoting your USt-IdNr: the supplier invoices tax-free (its i.g. Lieferung); you book **Erwerbsteuer** 19 %/7 % (Kz 89/93) and the matching Vorsteuer (Kz 61) (§ 1a, § 3d UStG). BU 19 (19 %) / BU 18 (7 %); BB `19_both_2` / `7_both`; DATEV Automatikkonten 3425 | 5425 "Innergemeinschaftlicher Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer" (7 %: 3420 | 5420; DATEV 2026); accounts 1774 | 3804 (USt i.g.E.) and 1574 | 1404 (VSt i.g.E.).
- The **Erwerbsschwelle** of 12.500 € (§ 1a Abs. 3 UStG → https://www.gesetze-im-internet.de/ustg_1980/__1a.html) only matters for Kleinunternehmer and other non-deducting buyers; a regelbesteuerte UG always has an i.g. Erwerb. Report goods purchases from EU webshops as i.g.E. even when the shop shows the German price — check whether the invoice shows German 19 % (then normal `19_pre`, the shop is OSS/registered in Germany) or 0 % with your USt-IdNr (then i.g.E.).

### 2.8 Own invoices into the EU: i.g. Lieferung and § 3a Abs. 2 services

- **i.g. Lieferung** (goods): exempt under § 4 Nr. 1b/§ 6a if the customer is a business with a valid USt-IdNr of another member state, the goods physically leave Germany (Gelangensnachweis/Gelangensbestätigung, §§ 17a–17c UStDV), the ZM is filed correctly, and the invoice shows both USt-IdNr and "steuerfreie innergemeinschaftliche Lieferung". Revenue 8125 | 4125, Kz 41, BU 11, BB `0_none` on that account.
- **B2B services** (§ 3a Abs. 2 UStG → https://www.gesetze-im-internet.de/ustg_1980/__3a.html): place of supply is the customer's seat → **not taxable in Germany**; the customer self-assesses (Art. 196 VAT Directive). Invoice without VAT, both USt-IdNr, note "Steuerschuldnerschaft des Leistungsempfängers" (§ 14a Abs. 1). Revenue 8336 | 4336, Kz 21, BU 47, **ZM quarterly**. Verify the USt-IdNr (qualifiziert) before invoicing; without a valid number treat the customer as a consumer (German 19 % or OSS).
- **B2C** in the EU: digital services (software downloads, SaaS to consumers, e-books) and distance sales are taxed in the customer's state once the EU-wide B2C threshold of **10.000 €** per year is exceeded (§ 3a Abs. 5 Satz 3, § 3c Abs. 4 UStG → https://www.gesetze-im-internet.de/ustg_1980/__3c.html); below it German VAT applies (or opt in). Other B2C services: German VAT (§ 3a Abs. 1).

### 2.9 OSS (One-Stop-Shop, § 18j UStG)

Registration at the BZSt (BOP); one quarterly declaration for all EU B2C destination-country VAT, due and payable by the **last day of the month following the quarter** (30.04., 31.07., 31.10., 31.01.) (§ 18j Abs. 4 UStG → https://www.gesetze-im-internet.de/ustg_1980/__18j.html ; → https://www.datev.de/web/de/berufsgruppenuebergreifend/gesetzliche-themen/one-stop-shop-verfahren). DATEV: BU 44 with country/rate, Kz 45 in the UStVA; revenue account 8339 | 4339 ("im anderen EU-Land steuerbare Leistungen"). Destination VAT is a **Verbindlichkeit**, not German Umsatzsteuer; BB has no OSS vat code — book gross on the revenue account with `0_none` and a separate liability line, and let the Steuerberater file OSS (red flag §8).

### 2.10 Drittland (non-EU) and foreign VAT

- **Goods exported**: exempt § 4 Nr. 1a/§ 6 with Ausfuhrnachweis (ATLAS Ausgangsvermerk, or carrier documents); 8120 | 4120, Kz 43, BU 1.
- **B2B services to non-EU businesses**: § 3a Abs. 2 → not taxable in Germany; no ZM; 8338 | 4338, Kz 45; invoice without VAT, statement such as "Nicht im Inland steuerbare Leistung — Leistungsort beim Empfänger (§ 3a Abs. 2 UStG)"; ask the customer for a business registration/VAT number as evidence of Unternehmereigenschaft. Destination-country rules may apply (e.g. Swiss VAT registration of foreign suppliers above a worldwide turnover threshold — red flag §8).
- **B2C to non-EU consumers**: Katalogleistungen of § 3a Abs. 4 (consulting, data processing, software/electronic services, licences) are taxed at the consumer's residence → not taxable in Germany; other B2C services follow § 3a Abs. 1 → German VAT.
- **Foreign VAT on purchases is never Vorsteuer** in the UStVA (§ 15 covers German tax only). Options: reclaim via the **Vorsteuervergütungsverfahren** (§ 18 Abs. 9 UStG, §§ 59–61a UStDV): EU countries — electronic application via the BZSt portal within **nine months** after year end (30.09.), minimum **400 €** per quarter or **50 €** per year (§ 61 UStDV → https://www.gesetze-im-internet.de/ustdv_1980/__61.html); non-EU countries — within **six months** (30.06.), minimum **1.000 €** / **500 €**, only with reciprocity (§ 61a UStDV → https://www.gesetze-im-internet.de/ustdv_1980/__61a.html ; → https://www.handelskammer-hamburg.de/recht-steuern/steuerrecht/umsatzsteuer-mehrwertsteuer/umsatzsteuer-mehrwertsteuer-international/vorsteuerverguetung-eu-drittstaaten-6682998). Otherwise the foreign VAT is simply part of the expense (`0_none`, gross). Better: give every foreign B2B vendor your USt-IdNr so they invoice net (reverse charge).

### 2.11 Decision tree — incoming invoice → Steuerschlüssel

```
Incoming invoice (Eingangsrechnung)
├─ Is it a Rechnung at all? (Kontoauszug, Mahnung, Angebot, Lieferschein = no) → no VAT key, no posting from it
├─ Supplier seated in Germany (German address, DE-Steuernummer/USt-IdNr)
│  ├─ German VAT 19 % shown ................................ BU 9  | BB 19_pre  | Kz 66   (needs §14 Abs. 4 content or §33 Kleinbetrag)
│  ├─ German VAT 7 % shown (rail, taxi ≤50 km, books, hotel room, food) BU 8 | BB 7_pre | Kz 66
│  ├─ mixed rates on one bill (hotel, restaurant) ............ split lines per rate (19_pre / 7_pre)
│  ├─ no VAT because exempt § 4 Nr. 8/11/12 (bank fees, insurance, rent w/o option) → no key | BB 0_none
│  ├─ no VAT, supplier is Kleinunternehmer § 19 (note on invoice) ......... no key | BB 0_none (no Vorsteuer!)
│  ├─ no VAT, domestic § 13b case (mobiles/tablets ≥ 5.000 €, Bauleistung) ... BU 94 on 3125|5925-type account | Kz 84/85 + 67
│  └─ VAT shown but invoice defective (no Leistungsdatum, no recipient, wrong entity) → request correction; until then book without Vorsteuer or park it
├─ Supplier seated in another EU state
│  ├─ Service (SaaS, ads, cloud, consulting, licence), no VAT, your USt-IdNr on it → § 13b Abs. 1: BU 94 (3123|5923) | BB 19_both_506 | Kz 46/47 + 67
│  ├─ Service, but foreign VAT charged (your USt-IdNr missing) → expense gross, BB 0_none; still declare § 13b on the net (ask Steuerberater); request corrected invoice; never deduct the foreign VAT
│  ├─ Service, German 19 % VAT charged (vendor treats you as consumer) → § 14c: not deductible; get a B2B invoice; meanwhile 0_none gross
│  ├─ Goods shipped to you, 0 % with your USt-IdNr → i.g.E.: BU 19 (7 %: BU 18) | BB 19_both_2 / 7_both | Kz 89(93) + 61
│  ├─ Goods with German 19 % shown (vendor registered/OSS in DE) → BU 9 | BB 19_pre
│  └─ Payment/finance service (card acquirer, PSP fees) → exempt § 4 Nr. 8: no key | BB 0_none (no § 13b tax arises on exempt services)
└─ Supplier seated outside the EU (US, UK, CH …)
   ├─ Service (API, SaaS, cloud, contractor), no VAT ........ § 13b Abs. 2 Nr. 1: Automatikkonto 3125|5925 (BU 94 logic) | BB 19_both_511 | Kz 84/85 + 67
   ├─ Service with US sales tax / UK VAT shown ................ still § 13b on the net; foreign tax = cost, BB 0_none for that part; ask for net invoice
   ├─ Service with German 19 % shown (vendor OSS-registered, consumer treatment) → § 14c, not deductible; get B2B invoice
   └─ Goods imported → Einfuhrumsatzsteuer (customs receipt) is Vorsteuer Kz 62 (BU per software; BB: book EUSt on 1588|1433 "Entstandene Einfuhrumsatzsteuer" (DATEV 2026) with 0_none; the goods invoice itself 0_none)
Deductibility overlay (independent of the key): Bewirtung 70/30 (VSt 100 %), Geschenke > 50 € (no VSt, no expense), private items of the Gesellschafter → Verrechnungskonto (no VSt).
```

### 2.12 Decision tree — outgoing invoice → Steuersatz / Schlüssel / Rechnungshinweis

```
Outgoing invoice (Ausgangsrechnung)
├─ Customer in Germany
│  ├─ B2B or B2C, standard service/goods ....... 19 %: BU 3 | BB 19_vat | 8400|4400 | Kz 81; Pflichtangaben § 14 Abs. 4; E-Rechnung rules (§3)
│  ├─ reduced-rate item (books, press) ......... 7 %:  BU 2 | BB 7_vat  | 8300|4300 | Kz 86
│  ├─ you deliver a § 13b Abs. 2 item (Bauleistung to a builder, mobiles ≥ 5.000 € B2B) → no VAT, note "Steuerschuldnerschaft des Leistungsempfängers", 8337|4337, BU 46, Kz 60
│  └─ gross ≤ 250 € → Kleinbetragsrechnung allowed (§ 33 UStDV), still E-Rechnung-exempt
├─ Customer in another EU state
│  ├─ Business with valid USt-IdNr (qualifizierte BZSt-Abfrage documented)
│  │  ├─ Service (§ 3a Abs. 2) .... no VAT; both USt-IdNr; "Steuerschuldnerschaft des Leistungsempfängers"; 8336|4336, BU 47, Kz 21, ZM quarterly; BB 0_none
│  │  └─ Goods shipped to that state .... exempt § 4 Nr. 1b; both USt-IdNr; "steuerfreie innergemeinschaftliche Lieferung"; Gelangensnachweis; 8125|4125, BU 11, Kz 41, ZM (monthly if > 50.000 €/quarter); BB 0_none
│  ├─ No (valid) USt-IdNr → treat as consumer
│  │  ├─ digital service / distance sale and EU-wide B2C turnover > 10.000 € → destination VAT via OSS; 8339|4339, BU 44, Kz 45; note destination rate; BB 0_none + liability
│  │  ├─ digital service / distance sale ≤ 10.000 € (and no opt-in) → German 19 %: BU 3 | 19_vat
│  │  └─ other B2C service (§ 3a Abs. 1) → German 19 %: BU 3 | 19_vat
│  └─ EU public body / non-profit with USt-IdNr → as business (§ 13b Abs. 5 "juristische Person")
└─ Customer outside the EU
   ├─ Business: service → not taxable in DE; no VAT; note "Nicht im Inland steuerbar, § 3a Abs. 2 UStG"; 8338|4338, Kz 45; no ZM; BB 0_none; keep evidence of business status
   ├─ Business: goods exported → exempt § 4 Nr. 1a; Ausfuhrnachweis; "steuerfreie Ausfuhrlieferung"; 8120|4120, BU 1, Kz 43
   ├─ Consumer: Katalogleistung § 3a Abs. 4 (software, consulting, data processing) → not taxable in DE; 8338|4338, Kz 45
   └─ Consumer: other service → German 19 %: BU 3 | 19_vat
Always: Leistungsdatum/-zeitraum, sequential number, your Steuernummer or USt-IdNr, correct legal name "… UG (haftungsbeschränkt)", Handelsregister number and Geschäftsführer (§ 35a GmbHG on Geschäftsbriefe).
```

### 2.13 What changed 2024 → 2026 (thresholds and rules used in this file)

| Item | Old | New | Effective | Source |
|---|---|---|---|---|
| Ist-Versteuerung threshold (§ 20 UStG) | 600.000 € | **800.000 €** | VZ 2024 | https://www.gesetze-im-internet.de/ustg_1980/__20.html |
| UStVA monthly threshold (§ 18 Abs. 2 UStG) | 7.500 € | **9.000 €** | 01.01.2025 | https://www.gesetze-im-internet.de/ustg_1980/__18.html |
| UStVA exemption threshold | 1.000 € | **2.000 €** | 01.01.2025 | same |
| Founders' monthly UStVA rule | suspended 2021–2026 | returns 2027 unless extended | 01.01.2027 | same |
| Kleinunternehmer (§ 19 UStG) | 22.000 € / 50.000 € forecast, "nicht erhoben" | **25.000 € / 100.000 €**, steuerfrei, EU regime § 19a | 01.01.2025 | https://www.gesetze-im-internet.de/ustg_1980/__19.html |
| Kleinunternehmer annual USt return | required | not required (unless § 18 Abs. 4a / request) | VZ 2024 | https://www.haufe.de/finance/buchfuehrung-kontierung/kleinunternehmer-wann-ist-eine-ust-erklaerung-abzugeben_186_396414.html |
| Retention Buchungsbelege / Rechnungen | 10 years | **8 years** | 01.01.2025 (periods not yet expired) | https://www.gesetze-im-internet.de/ao_1977/__147.html |
| E-Rechnung reception | — | mandatory | 01.01.2025 | https://www.gesetze-im-internet.de/ustg_1980/__27.html |
| E-Rechnung issuing | PDF/paper | > 800.000 € Vorjahresumsatz: 2027; all: **2028** | 01.01.2027 / 01.01.2028 | same |
| Restaurant food VAT | 19 % (2024–2025) | **7 %** permanent (drinks 19 %) | 01.01.2026 | https://www.gesetze-im-internet.de/ustg_1980/__12.html |
| Hotel breakfast | 19 % | food 7 %, drinks 19 % (Aufteilungsgebot upheld by ECJ 05.03.2026) | 01.01.2026 | https://www.ihk.de/schleswig-holstein/recht/steuern/aktuelles/mehrwertsteuer-in-gastronomie-6932586 |
| Geschenke limit (§ 4 Abs. 5 Nr. 1 EStG) | 35 € | **50 €** | 01.01.2024 | https://www.gesetze-im-internet.de/estg/__4.html |
| Degressive AfA (§ 7 Abs. 2 EStG) | 2× / max 20 % (01.04.–31.12.2024); none 01.01.–30.06.2025 | **3× / max 30 %** | 01.07.2025–31.12.2027 | https://www.gesetze-im-internet.de/estg/__7.html |
| Körperschaftsteuer (§ 23 KStG) | 15 % | 14 % (2028) … **10 % (2032)** | VZ 2028 ff. | https://www.gesetze-im-internet.de/kstg_1977/__23.html |
| GewSt Mindesthebesatz (§ 16 Abs. 4 GewStG) | 200 % | **280 %** | Erhebungszeitraum 2027 | https://www.gesetze-im-internet.de/gewstg/__16.html |
| Mindestbesteuerung (§ 10d Abs. 2 EStG) | 60 % above 1 Mio € | **70 %** | VZ 2024–2027 | https://www.gesetze-im-internet.de/estg/__10d.html |
| HGB size classes (§§ 267, 267a) | 350.000/700.000 €; 6/12 Mio € | **450.000/900.000 €; 7,5/15 Mio €** | FY from 01.01.2024 (option 2023) | https://www.gesetze-im-internet.de/hgb/__267a.html |
| Entfernungspauschale (GGF privately) | 0,30 € km 1–20, 0,38 € from km 21 | **0,38 € from km 1** | 01.01.2026 | https://www.gesetze-im-internet.de/estg/__9.html |
| Künstlersozialabgabe | 5,0 % (2025); Bagatellgrenze 450 € | **4,9 %**; **1.000 €** | 01.01.2026 | https://www.kuenstlersozialkasse.de/nachrichten/detail/kuenstlersozialabgabe-sinkt-im-jahr-2026-auf-49-prozent |
| Insolvenzgeldumlage | 0,06 % (2023–2024) | **0,15 %** (2025, 2026) | 01.01.2025 | https://www.haufe.de/personal/entgelt/insolvenzgeldumlage-senkung-geplant_78_365594.html |
| GoBD | 28.11.2019 version | amended 11.03.2024 | 01.04.2024 | https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/AO-Anwendungserlass/2024-03-11-aenderung-gobd.pdf?__blob=publicationFile&v=4 |
| Bewirtungsbeleg rules | BMF 30.06.2021 | BMF **19.11.2025** (TSE bills, digital Eigenbeleg, E-Rechnung) | Bewirtungen from 01.01.2025 | https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Einkommensteuer/2025-11-19-bewirtungskosten-als-betriebsausgaben.pdf?__blob=publicationFile&v=2 |
| Kassensysteme Meldepflicht (§ 146a Abs. 4 AO) | — | report via ELSTER (existing by 31.07.2025) | 01.01.2025 | https://finanzamt.hessen.de/service/finanzaemter-in-hessen/mitteilungspflicht-fuer-kassensysteme-und-taxameter |
| Transparenzregister fee | 20,80 € (2022–2023; 4,80 € in 2020, 11,47 € in 2021) | **19,80 €**/year (TrGebV) | Gebührenjahr 2024 | https://www.haufe.de/id/beitrag/unternehmenspflichten-beim-transparenzregister-106-gebuehren-HI11575406.html |
| Unchanged despite drafts | Verpflegungspauschalen 14/28 € (draft 16/32 € dropped); GWG 800 €/Sammelposten 1.000 € (draft 1.000/5.000 € dropped); Lohnsteuer-Anmeldung 1.080/5.000 €; Kilometerpauschale 0,30 €; Sachbezug 50 €; Betriebsveranstaltung 110 € | | | https://www.gesetze-im-internet.de/estg/__9.html ; https://www.gesetze-im-internet.de/estg/__6.html ; https://www.gesetze-im-internet.de/estg/__41a.html |

---

## 3. E-Rechnung (§ 14 UStG as amended by the Wachstumschancengesetz)

- Definition: an **E-Rechnung** is issued, transmitted and received in a **structured electronic format** that allows electronic processing and complies with the European norm for electronic invoicing (EN 16931, Directive 2014/55/EU) or an agreed interoperable format (§ 14 Abs. 1 Satz 3, 6 UStG → https://www.gesetze-im-internet.de/ustg_1980/__14.html). A plain **PDF, paper, JPG or e-mail text is a "sonstige Rechnung"**, not an E-Rechnung. Compliant formats: **XRechnung** (pure XML, UBL or CII) and **ZUGFeRD** ≥ 2.0.1 (hybrid PDF/A-3 with embedded XML; profiles EN 16931/COMFORT, EXTENDED, XRECHNUNG; MINIMUM and BASIC-WL are not compliant) — in a hybrid file the **XML is the legally leading part** (BMF FAQ → https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html).
- **Reception duty since 01.01.2025** for every domestic business (including Kleinunternehmer, Vermieter): an e-mail inbox suffices; you must be able to store the XML unchanged and make it readable. BB ingests XRechnung/ZUGFeRD as Belege — archive the original XML, not only a rendered PDF.
- **Issuing duty** (domestic B2B, § 14 Abs. 2 Satz 2 Nr. 1 UStG) with transition rules in **§ 27 Abs. 38 UStG** (→ https://www.gesetze-im-internet.de/ustg_1980/__27.html):
  - until 31.12.2026: paper or, with the recipient's consent, any electronic format (PDF) allowed;
  - 2027: PDF/paper still allowed if the issuer's **Gesamtumsatz 2026 ≤ 800.000 €**; above that E-Rechnung mandatory from 01.01.2027;
  - EDI formats allowed until 31.12.2027 with consent;
  - from **01.01.2028: E-Rechnung mandatory for all** domestic B2B supplies (→ https://www.grantthornton.de/themen/2026/e-rechnungspflicht-2027-die-wichtigsten-fragen-und-antworten-zur-e-rechnung/).
- **Exempt from the issuing duty**: **Kleinbetragsrechnungen ≤ 250 €** (§ 33 UStDV), **Fahrausweise** (§ 34 UStDV), invoices to consumers (B2C), exempt supplies under **§ 4 Nr. 8–29**, and invoices of **Kleinunternehmer** (§ 34a UStDV, since 2025) — they may still be issued as E-Rechnung (→ https://sevdesk.de/ratgeber/buchhaltung-finanzen/rechnungen/e-rechnung/e-rechnung-ausnahmen/). Non-domestic recipients (EU/non-EU) are outside the German duty.
- Second BMF letter of **15.10.2025** (III C 2 - S 7287-a/00019/007/243 → https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Umsatzsteuer/Umsatzsteuer-Anwendungserlass/2025-10-15-einfuehrung-obligatorische-e-rechnung.pdf?__blob=publicationFile&v=5): all §§ 14/14a mandatory data must be inside the structured XML (not only in an attachment); distinguishes **Formatfehler**, **Geschäftsregelfehler** and **Inhaltsfehler**; validation against EN 16931 is expected of the recipient; a non-compliant file counts as sonstige Rechnung (Vorsteuer at risk after the transition) (→ https://www.haufe.de/finance/steuern-finanzen/bmf-schreiben-v-15102025-zur-e-rechnung_190_669628.html).
- Archiving: the XML is the Buchungsbeleg → **8 years**, unaltered, machine-readable, indexed (GoBD); a visualisation may be stored in addition. Corrections of an E-Rechnung must themselves be E-Rechnungen (Rechnungskorrektur with reference to the original number).
- Practical: from 2027/2028 issue XRechnung/ZUGFeRD from BB (`invoices/create` produces the format configured in BB, check in the UI) and ask suppliers for ZUGFeRD; for Bewirtungsbelege see BMF 19.11.2025 (§4.7).

---

## 4. Ertragsteuern and UG-specific rules

### 4.1 Körperschaftsteuer (KSt) and Solidaritätszuschlag

- **Körperschaftsteuer 15 %** of the zu versteuerndes Einkommen (§ 23 Abs. 1 KStG) plus **Solidaritätszuschlag 5,5 %** of the KSt (§ 4 SolzG → https://www.gesetze-im-internet.de/solzg_1995/__4.html) = **15,825 %**.
- **Reduction schedule** enacted by the Gesetz für ein steuerliches Investitionssofortprogramm ("Investitionsbooster", BGBl. 2025 I of 18.07.2025), § 23 Abs. 1 KStG n.F. (→ https://www.gesetze-im-internet.de/kstg_1977/__23.html ; → https://www.bundesfinanzministerium.de/Monatsberichte/Ausgabe/2025/08/Inhalte/Kapitel-2-Fokus/investitionssofortprogramm-deutschland.html):

| VZ | KSt | KSt incl. SolZ |
|---|---|---|
| up to 2027 | 15 % | 15,825 % |
| 2028 | 14 % | 14,77 % |
| 2029 | 13 % | 13,715 % |
| 2030 | 12 % | 12,66 % |
| 2031 | 11 % | 11,605 % |
| from 2032 | 10 % | 10,55 % |

- KSt-Vorauszahlungen quarterly on **10.03., 10.06., 10.09., 10.12.** (§ 31 Abs. 1 KStG with § 37 Abs. 1 EStG → https://www.gesetze-im-internet.de/estg/__37.html), set by Bescheid; new UGs get them after the first assessment or from the Fragebogen forecast. Booking: 2200 | 7600 Körperschaftsteuer, 2208 | 7608 Solidaritätszuschlag; prior-year settlements 2203 | 7603 "Körperschaftsteuer für Vorjahre" and 2209 | 7609 "Solidaritätszuschlag für Vorjahre" (SKR03 2209 label truncated in extraction), refunds 2204 | 7604. KSt and SolZ are **not deductible** (§ 10 Nr. 2 KStG) — they reduce the Jahresüberschuss but are added back for tax.
- Latent taxes (§ 274 HGB) may be skipped by small companies (§ 274a HGB → https://www.gesetze-im-internet.de/hgb/__274a.html).

### 4.2 Gewerbesteuer (GewSt)

- **Steuermesszahl 3,5 %** (§ 11 Abs. 2 GewStG → https://www.gesetze-im-internet.de/gewstg/__11.html) × Gewerbeertrag = Messbetrag; × municipal **Hebesatz** (Mindesthebesatz **200 %** through Erhebungszeitraum 2026, **280 %** from 2027 — § 16 Abs. 4 Satz 2 GewStG n.F. with § 36 Abs. 5b GewStG, Neuntes Gesetz zur Änderung des Steuerberatungsgesetzes, Bundestag 24.04.2026 → https://www.gesetze-im-internet.de/gewstg/__16.html ; → https://www.haufe.de/id/beitrag/neuntes-gesetz-zur-aenderung-des-steuerberatungsgesetzes-8-anhebung-des-gewerbesteuer-mindesthebesatzes-HI17166582.html ; big cities 400–490 %) = GewSt. Example: Hebesatz 400 % → 14 % of the Gewerbeertrag; total burden 2026 with KSt/SolZ ≈ 29,8 %.
- **No Freibetrag** for Kapitalgesellschaften: the 24.500 € allowance of § 11 Abs. 1 Satz 3 Nr. 1 GewStG applies only to natural persons and Personengesellschaften.
- **Not deductible** as Betriebsausgabe since 2008 (§ 4 Abs. 5b EStG → https://www.gesetze-im-internet.de/estg/__4.html); book on 4320 | 7610 and add back. Prior-year adjustments: 2281 | 7641 "Gewerbesteuernachzahlungen und -erstattungen für Vorjahre nach § 4 Abs. 5b EStG".
- **Hinzurechnungen** § 8 Nr. 1 GewStG: 25 % of the sum of (100 % of interest + 20 % of rents for movables + 50 % of rents for immovables + 25 % of licence fees) in excess of the **Freibetrag of 200.000 €** — effective add-backs 25 % / 5 % / 12,5 % / 6,25 % (→ https://www.gesetze-im-internet.de/gewstg/__8.html) — irrelevant for most small UGs.
- Vorauszahlungen on **15.02., 15.05., 15.08., 15.11.** (§ 19 Abs. 1 GewStG → https://www.gesetze-im-internet.de/gewstg/__19.html), paid to the **Gemeinde**, not the Finanzamt. Gewerbesteuererklärung with the KSt return; the Finanzamt issues the Messbescheid, the Gemeinde the GewSt-Bescheid.

### 4.3 Kapitalertragsteuer on Ausschüttungen (distributions)

- The UG withholds **25 % Kapitalertragsteuer + 5,5 % SolZ** thereon = **26,375 %** (plus Kirchensteuer if applicable) from every Gewinnausschüttung to a natural-person shareholder (§ 43 Abs. 1 Nr. 1, § 43a Abs. 1 Nr. 1 EStG → https://www.gesetze-im-internet.de/estg/__43a.html). The tax arises at the **Zufluss**; for KapESt purposes (§ 44 Abs. 2 EStG, all shareholders) the Zufluss is the payment date fixed in the Beschluss, otherwise the **day after** the Beschlussfassung, and withheld KapESt/SolZ must be paid **at that moment** — the old "10th of the following month" practice no longer applies (§ 44 Abs. 1 Satz 2, 5, Abs. 2 EStG → https://www.gesetze-im-internet.de/estg/__44.html ; → https://www.haufe.de/id/beitrag/kapitalertragsteuer-6-entstehung-anmeldung-und-abfuehrung-HI6445991.html). The beherrschender-Gesellschafter "Zufluss at Fälligkeit" doctrine concerns the shareholder's own § 11 EStG timing, not the UG's withholding. File the **Kapitalertragsteuer-Anmeldung** via ELSTER (form KapEStA → https://www.elster.de/eportal/helpGlobal?themaGlobal=help_kapesta_2026) and issue the shareholder a **Steuerbescheinigung** (§ 45a Abs. 2 EStG; BMF 16.05.2025 → https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Abgeltungsteuer/2025-05-16-kapitalertragSt-steuerbescheinigung.pdf?__blob=publicationFile&v=4).
- Shareholder side: Abgeltungsteuer, or on application the **Teileinkünfteverfahren** (60 % taxable at the personal rate) for holdings ≥ 25 %, or ≥ 1 % with professional activity for the company (§ 32d Abs. 2 Nr. 3 EStG → https://www.juhn.com/fachwissen/gmbh-steuerrecht/gewinnausschuettung-gmbh-teileinkuenfteverfahren/).
- Accounts (DATEV 2026): resolution `0860 | 2970 Gewinnvortrag vor Verwendung an 0755 | 3519 Verbindlichkeiten gegenüber Gesellschaftern für offene Ausschüttungen`; withholding `0755 | 3519 an 1746 | 3760 Verbindlichkeiten aus Einbehaltungen (KapESt und SolZ, KiSt auf KapESt) für offene Ausschüttungen`; payments from Bank. Do **not** use 2213 | 7630 "Kapitalertragsteuer 25 %" — that account is for KapESt withheld **from** the UG on its own capital income (anrechenbar).
- A UG may only distribute after the **gesetzliche Rücklage** has been fed (§4.4) and never the Stammkapital (§ 30 GmbHG).

### 4.4 Stammkapital, gesetzliche Rücklage, Umwandlung in eine GmbH

- **Stammkapital** of a UG: any amount from 1 € (§ 5a Abs. 1 GmbHG), must be fully paid in cash before registration; Sacheinlagen are excluded (§ 5a Abs. 2) (→ https://www.gesetze-im-internet.de/gmbhg/__5a.html). Accounts: 0800 | 2900 Gezeichnetes Kapital; unpaid parts 0820 | 2910 Ausstehende Einlagen (nicht eingefordert, offen abgesetzt).
- **Gesetzliche Rücklage § 5a Abs. 3 GmbHG**: each year **one quarter of the Jahresüberschuss, reduced by a Verlustvortrag from the previous year**, goes to the legal reserve; it may be used only for a Kapitalerhöhung aus Gesellschaftsmitteln (§ 57c), to cover a Jahresfehlbetrag not covered by a Gewinnvortrag, or a Verlustvortrag not covered by a Jahresüberschuss. Booking at Ergebnisverwendung: `Jahresüberschuss (Ergebnisverwendung) an 0846 | 2930 Gesetzliche Rücklage`. The duty ends once the Stammkapital is raised to ≥ 25.000 € (§ 5a Abs. 5); no obligation to ever convert. The remaining 75 % may be carried forward (0860 | 2970) or distributed after KapESt.
- **Umwandlung UG → GmbH** = Kapitalerhöhung to ≥ 25.000 € by shareholder resolution (¾ majority, notarised Satzungsänderung), Handelsregister entry, Firma may change to "GmbH"; a Sachkapitalerhöhung is allowed for this step (BGH, § 5a Abs. 2 Satz 2 not applicable) (→ https://www.haufe.de/id/beitrag/10-recht-der-kapitalgesellschaften-g-umwandlung-in-eine-gmbhkapitalmassnahmen-bei-der-ug-haftungsbeschraenkt-HI16419447.html). Costs: Notar, Registergericht, Steuerberater; tax-neutral.
- § 5a Abs. 4: the Gesellschafterversammlung must be convened immediately when **Zahlungsunfähigkeit droht**.

### 4.5 Gesellschafterdarlehen and Gesellschafter-Verrechnungskonto

- A UG has **no Privateinlagen/-entnahmen** accounts (those, SKR03 1800/1890 | SKR04 2100/2180, are for Einzelunternehmer/Personengesellschaften). Every money flow between company and shareholder is a **loan, a salary, a distribution, a capital contribution or an expense reimbursement** and must be documented as such. Use:
  - shareholder owes the UG (private purchase with the company card, advance): **Forderungen gegen GmbH-Gesellschafter** 1381 | 1307 (Restlaufzeit ≤ 1 year 1382 | 1308);
  - UG owes the shareholder (shareholder paid a business bill privately, loan received): **Verbindlichkeiten gegenüber Gesellschaftern** 0730 | 3510 (≤ 1 year 0731 | 3511; SKR04 also 3640 "Verbindlichkeiten gegenüber GmbH-Gesellschaftern", ≤ 1 year 3641); long-term loans 0740/0750 | 3514/3517 by remaining term (SKR04 3564/3567 are third-party Darlehen by term; all labels from the DATEV 2026 SKR PDFs → https://www.datev.de/hilfe/0907817).
  In practice one "Verrechnungskonto Gesellschafter" is used and reclassified at year end by balance sign; a **debit balance is a loan to the shareholder** and must bear interest at arm's length, otherwise the interest advantage is a **vGA** (§4.6) (→ https://www.lexware.de/wissen/buchhaltung-finanzen/gesellschafter-verrechnungskonto-diese-steuerregeln-sollten-sie-kennen/). § 30 GmbHG forbids payments that eat into the Stammkapital unless a full-value repayment claim exists.
- **Gesellschafterdarlehen to the UG**: written contract in advance (amount, interest, term, repayment), interest at market rate (or 0 % — interest-free loans from shareholders are allowed; interest that is too high is a vGA); interest paid is a deductible Zinsaufwand 2120 | 7310; the shareholder taxes it as Kapitalertrag at the personal rate when holding ≥ 10 % (§ 32d Abs. 2 Nr. 1b EStG) — the UG does **not** withhold KapESt on plain loan interest. In insolvency such loans are **nachrangig** (§ 39 Abs. 1 Nr. 5 InsO) and repayments within **one year** before the insolvency application are **anfechtbar** (§ 135 Abs. 1 Nr. 2 InsO → https://www.gesetze-im-internet.de/inso/__135.html). A **Rangrücktritt** removes the loan from the Überschuldungsstatus (§ 19 Abs. 2 Satz 2 InsO).

### 4.6 Geschäftsführergehalt, Lohnsteuer, Sozialversicherung, vGA

- The **Gesellschafter-Geschäftsführer** (GGF) needs a written **Anstellungsvertrag**, approved by the Gesellschafterversammlung, in force **before** payments start; for a beherrschender GGF every payment must rest on a clear, prior, civil-law-valid agreement (**Rückwirkungsverbot**), and it must be actually carried out (Durchführungsgebot) and **angemessen** (Fremdvergleich: company size, profit, sector; Tantieme usually ≤ 25 % of total pay) (→ https://www.lexware.de/wissen/unternehmensfuehrung/verdeckte-gewinnausschuettung/ ; → https://www.smartsteuer.de/online/lexikon/v/verdeckte-gewinnausschuettung/).
- **Lohnsteuer**: the GGF is an Arbeitnehmer for wage-tax purposes; ELStAM retrieval, monthly payroll, **Lohnsteuer-Anmeldung** by the **10th** after the period (§ 41a Abs. 1 EStG); period monthly if last year's Lohnsteuer > **5.000 €**, quarterly if > **1.080 €** and ≤ 5.000 €, annual if ≤ 1.080 € (§ 41a Abs. 2 EStG, unchanged → https://www.gesetze-im-internet.de/estg/__41a.html; some blogs cite 2.000/9.000 € — not in the law text). Accounts: 4124 | 6024 Geschäftsführergehälter (GmbH-Gesellschafter), 1741 | 3730 Lohn-/Kirchensteuer, 1742 | 3740 Sozialversicherung, 1740 | 3720 net salary payable.
- **Sozialversicherung**: a GGF holding ≥ 50 % or a comprehensive **Sperrminorität** is not abhängig beschäftigt → no statutory SV (own private/voluntary health and pension cover); minority GGF without Sperrminorität → SV-pflichtig. The Einzugsstelle must trigger the **Statusfeststellungsverfahren** with the DRV Bund Clearingstelle for every GGF (§ 7a Abs. 1 Satz 2 SGB IV → https://www.gesetze-im-internet.de/sgb_4/__7a.html ; → https://www.ihk.de/duesseldorf/recht-und-steuern/recht/merkblaetter-von-a-bis-z/sozialversicherungspflicht-des-gmbh-geschaeftsfuehrers-5463064). Employer SV and Umlagen for SV-pflichtige staff: 4130 | 6110; Beitragsnachweis by the **fifth-last** Bankarbeitstag (§ 28f Abs. 3 SGB IV: zwei Arbeitstage vor Fälligkeit → https://www.gesetze-im-internet.de/sgb_4/__28f.html), payment by the **third-last** Bankarbeitstag of the month (§ 23 Abs. 1 SGB IV → https://www.gesetze-im-internet.de/sgb_4/__23.html); Insolvenzgeldumlage 2026 **0,15 %** (→ https://www.haufe.de/personal/entgelt/insolvenzgeldumlage-senkung-geplant_78_365594.html). Unfallversicherung: the UG is a member of its Berufsgenossenschaft (administrative/IT: VBG); a GGF may insure voluntarily; digital **Lohnnachweis** for the previous year by **16.02.** (→ https://www.dguv.de/de/versicherung/uv-meldeverfahren/faq/fristen/index.jsp).
- Tax-free extras for the GGF as employee: **Sachbezug 50 €/month** (§ 8 Abs. 2 Satz 11 EStG), Aufmerksamkeiten 60 € per personal occasion (R 19.6 LStR), Betriebsveranstaltung Freibetrag **110 €** per event and person, two per year (§ 19 Abs. 1 Nr. 1a EStG → https://www.gesetze-im-internet.de/estg/__19.html), Reisekosten (§ 3 Nr. 16), Homeoffice equipment.
- **verdeckte Gewinnausschüttung (vGA, § 8 Abs. 3 Satz 2 KStG → https://www.gesetze-im-internet.de/kstg_1977/__8.html)**: any Vermögensminderung/verhinderte Vermögensmehrung caused by the shareholder relationship that a prudent manager would not have granted to a third party. Typical triggers in a one-person UG: salary or bonus without prior written agreement or paid irregularly; unangemessen high salary; private expenses booked as Betriebsausgabe (holiday, private phone, family meals); interest-free debit balance on the Verrechnungskonto; private use of the company car without agreement; Sonntags-/Nachtzuschläge to the GGF; rent paid to the shareholder above market. Consequence: the amount is added back to the UG's income (KSt/GewSt) **and** taxed as Kapitalertrag at the shareholder; where goods or services are consumed privately, Umsatzsteuer on the unentgeltliche Wertabgabe (§ 3 Abs. 1b, Abs. 9a UStG) comes on top. Always route doubtful items through the Verrechnungskonto and ask the Steuerberater.

### 4.7 Bewirtung (§ 4 Abs. 5 Satz 1 Nr. 2 EStG), Geschenke, Betriebsveranstaltung

- **Geschäftliche Bewirtung** (clients, prospects, partners; also the own staff present): **70 % deductible, 30 % not** (§ 4 Abs. 5 Satz 1 Nr. 2 EStG → https://www.gesetze-im-internet.de/estg/__4.html); **Vorsteuer 100 %** deductible (§ 15 Abs. 1a Satz 2 UStG). Required record: Ort, Tag, Teilnehmer, Anlass (concrete: "Projektbesprechung Angebot X", not "Geschäftsessen"), Höhe; for restaurant bills the bill must be attached and the Bewirtungsbeleg (Eigenbeleg) signed. New **BMF letter of 19.11.2025** (replaces BMF 30.06.2021 for Bewirtungen from 01.01.2025; the 2021 letter continues for earlier dates → https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Einkommensteuer/2025-11-19-bewirtungskosten-als-betriebsausgaben.pdf?__blob=publicationFile&v=2): only **machine-generated, electronically recorded and TSE-secured** restaurant bills are accepted (handwritten bills are not); bills **> 250 €** must contain the § 14 Abs. 4 data including the **name of the Bewirtende** printed by the restaurant (handwritten later additions do not count); ≤ 250 € the § 33 UStDV content suffices; tips may be shown on the bill or evidenced separately; the Eigenbeleg part may be digital and must be linked to the bill; a Kassenbeleg > 250 € may later be replaced by an E-Rechnung. Record separately from other expenses (§ 4 Abs. 7 EStG): 4650 | 6640 (70 %) and 4654 | 6644 (30 %).
- **Betriebliche Bewirtung of own employees** (team lunch during a workshop, Betriebsfeier): fully deductible (Nr. 2 does not apply), Vorsteuer 100 %; but check Arbeitslohn: **Betriebsveranstaltung** Freibetrag 110 € gross per person, max. two per year, open to all (§ 19 Abs. 1 Nr. 1a EStG; excess may be pauschal-taxed at 25 %, § 40 Abs. 2 Nr. 2); **Arbeitsessen** during an außergewöhnlicher Arbeitseinsatz ≤ 60 € per person is a tax-free Aufmerksamkeit (R 19.6 Abs. 2 LStR); regular team lunches are taxable Arbeitslohn (Sachbezugswert) (→ https://www.haufe.de/personal/entgelt/betriebsveranstaltungen/betriebsveranstaltung-freibetrag_78_429214.html). Accounts: 4140 | 6130 Freiwillige soziale Aufwendungen, lohnsteuerfrei (or 6640 sub-account "Bewirtung intern"); Aufmerksamkeiten 4653 | 6643.
- A one-person UG whose sole employee is the GGF: a lunch alone is never Bewirtung (private living cost, § 12 Nr. 1 EStG) — only the Verpflegungspauschale on business trips.
- **Geschenke** to non-employees: deductible only if the total per recipient per year ≤ **50 €** (net if Vorsteuer deductible; raised from 35 € on 01.01.2024 by the Wachstumschancengesetz) (§ 4 Abs. 5 Satz 1 Nr. 1 EStG); above → nothing deductible and **no Vorsteuer** (§ 15 Abs. 1a UStG); record separately (§ 4 Abs. 7) on 4630 | 6610 (≤ 50 €) / 4635 | 6620 (> 50 €); optional flat tax 30 % for the recipient (§ 37b EStG → https://www.gesetze-im-internet.de/estg/__37b.html). Gifts to employees: Sachbezug/Aufmerksamkeit rules (§4.6).

### 4.8 GWG, Sammelposten, AfA

(§ 6 Abs. 2, 2a EStG → https://www.gesetze-im-internet.de/estg/__6.html ; § 7 EStG → https://www.gesetze-im-internet.de/estg/__7.html)

| Net cost (without deductible VAT) | Treatment | Accounts |
|---|---|---|
| ≤ 250 € | expense immediately, no Verzeichnis | Bürobedarf 4930 \| 6815 or GWG 4855 \| 6260 |
| > 250 € and ≤ **800 €** | **GWG** Sofortabschreibung (§ 6 Abs. 2), listed in an Anlageverzeichnis (BB: Anlagen or the Steuerberater's) — or the Sammelposten | 0480 \| 0670 then 4855 \| 6260, or straight to 4855 \| 6260 |
| > 250 € and ≤ **1.000 €** | alternative **Sammelposten** (§ 6 Abs. 2a): pool per year, written off 1/5 per year over five years regardless of disposal; choice binds all such assets of the year | 0485 \| 0675, AfA 4862 \| 6264 |
| > 800 € (or > 1.000 € with Sammelposten) | capitalise and depreciate over the **betriebsgewöhnliche Nutzungsdauer** (AfA-Tabelle) | 0027 \| 0135 software, 0420 \| 0650 Büroeinrichtung, 0410 \| 0635 Geschäftsausstattung (EDV-Hardware), 0400 \| 0630 Betriebsausstattung; AfA 4830 \| 6220 (Sachanlagen), 4822 \| 6200 (immaterial) |

The 800 €/1.000 € limits are unchanged since 2018; the Wachstumschancengesetz draft's 1.000 €/5.000 € was dropped and no 2026 change is enacted (→ https://www.haufe.de/finance/jahresabschluss-bilanzierung/grenze-fuer-geringwertige-wirtschaftsgueter-auf-800-eur-erhoeht_188_411044.html). The GWG rule applies to **bewegliche, abnutzbare, selbständig nutzbare** assets — a monitor or docking station is not selbständig nutzbar (part of the PC), software licences count via R 5.5 EStR as Trivialprogramme ≤ 800 € (unverified reference).

- **Lineare AfA** (§ 7 Abs. 1): cost / useful life, pro rata temporis by month in the year of purchase. AfA-Tabelle (allgemein verwendbare Anlagegüter, BMF 15.12.2000): office furniture 13 years, phones 5 years, cars 6 years, servers 7 years (unverified individual values — check the table).
- **Computer hardware and software**: useful life may be set at **one year** (BMF 22.02.2022, IV C 3 - S 2190/21/10002 :025, replacing BMF 26.02.2021; applies to PCs, notebooks, tablets, docking stations, peripherals, Betriebs- und Anwendersoftware) — full write-off in the year of purchase even above 800 €, but not a Sofortabschreibung: still capitalise, list, and depreciate (pro rata not required per BMF, full year allowed) (→ https://www.haufe.de/finance/buchfuehrung-kontierung/bmf-verkuerzung-nutzungsdauer-software-und-hardware_186_632212.html). Handelsrechtlich many Steuerberater keep 3 years (Maßgeblichkeit deviates) — decide once with the Steuerberater. Smartphones are not covered (5 years or GWG).
- **Degressive AfA** re-introduced: for movable assets bought **after 30.06.2025 and before 01.01.2028** up to **3× the linear rate, max. 30 %** per year of the remaining book value (§ 7 Abs. 2 EStG n.F., Investitionssofortprogramm); switch to linear allowed. (2024 window: 01.04.–31.12.2024 with 2× / max. 20 %.) Electric vehicles bought 01.07.2025–31.12.2027: arithmetisch-degressiv 75/10/5/5/3/2 % (§ 7 Abs. 2a) (→ https://www.ihk-muenchen.de/ratgeber/steuern/investitionsprogramm/).
- **Investitionsabzugsbetrag § 7g EStG**: up to 50 % of planned investments deductible in advance if the profit ≤ 200.000 €; Sonderabschreibung 40 % (since 2024) — a planning tool for the Steuerberater, not for day-to-day Kontierung (→ https://www.gesetze-im-internet.de/estg/__7g.html).

### 4.9 Reisekosten (travel), Homeoffice, Arbeitszimmer

- The GGF travels as an **Arbeitnehmer** of the UG → use "Reisekosten Arbeitnehmer" accounts 4660–4668 | 6650–6668 (not "Unternehmer" 4670 | 6670); reimbursements are tax-free within § 3 Nr. 16 EStG; a Reisekostenabrechnung per trip (date, route, purpose, receipts) is the Beleg.
- **Verpflegungspauschalen** 2026 unchanged since 2020: **14 €** for absence > 8 h and for arrival/departure days of multi-day trips, **28 €** for 24 h (§ 9 Abs. 4a Satz 3 EStG → https://www.gesetze-im-internet.de/estg/__9.html); cut by **20 %** (5,60 €) for a provided breakfast and **40 %** (11,20 €) for lunch/dinner (Satz 8); three-month limit at the same place (Satz 6). Foreign rates: BMF 05.12.2025 for 2026 (→ https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Lohnsteuer/2025-12-05-steuerliche-behandlung-reisekosten-2026.pdf?__blob=publicationFile&v=5). Account 4664 | 6664, no VAT (`0_none`).
- **Fahrtkosten**: own car on a Dienstreise **0,30 €/km** (pauschaler Kilometersatz per § 9 Abs. 1 Satz 3 Nr. 4a Satz 2 EStG referring to § 5 Abs. 2 BRKG: 30 Cent → https://www.gesetze-im-internet.de/brkg_2005/__5.html), 0,20 € for other motor vehicles; account 4668 | 6668, `0_none`. Public transport/taxi/flight at cost with Vorsteuer as shown (rail 7 %, taxi 7 % ≤ 50 km/within town else 19 %, domestic flight 19 %, international flight exempt/not taxable): 4663 | 6663. The **Entfernungspauschale** (home–office commute) is the GGF's private Werbungskosten item — **0,38 €** from the first km from 2026 (Steueränderungsgesetz 2025; 2022–2025: 0,30 € for km 1–20 and 0,38 € from km 21) — not a company expense unless a taxable Fahrtkostenzuschuss is paid.
- **Übernachtung**: actual hotel cost with the UG as invoice recipient (room 7 %, breakfast food 7 % since 2026, drinks/parking 19 %), account 4666 | 6660; if breakfast is included the Verpflegungspauschale is cut by 20 %. Without receipt the employer may reimburse **20 €** per night tax-free in Germany (R 9.7 Abs. 3 LStR → https://www.haufe.de/id/beitrag/reisekostenerstattung-durch-den-arbeitgeber-523-uebernachtungspauschalen-HI17056358.html) — the company then books 20 € with an Eigenbeleg, no VAT.
- **Homeoffice-Pauschale** 6 €/day, max. **1.260 €**/year, and **Arbeitszimmer** Jahrespauschale **1.260 €** or actual costs when the room is the Mittelpunkt (§ 4 Abs. 5 Satz 1 Nr. 6b, 6c EStG) are deductions in the GGF's **personal** income-tax return, not UG expenses. If the UG rents a room from the GGF, the Mietvertrag must serve a vorrangiges betriebliches Interesse of the UG (otherwise the rent is Arbeitslohn) and the rent must be arm's length (vGA); rent 4210 | 6310 without VAT unless the GGF opts for VAT.

---

## 5. Compliance calendar for a UG

Dates falling on a weekend or public holiday move to the next Werktag (§ 108 Abs. 3 AO). "with StB" = a Steuerberater is mandated (§ 149 Abs. 3 AO).

| When | What | Basis / source |
|---|---|---|
| 10th of every month (or quarter month) | **UStVA** for the previous period; +1 month with Dauerfristverlängerung; monthly **Lohnsteuer-Anmeldung** if payroll > 5.000 €/yr | § 18 Abs. 1 UStG; § 41a EStG |
| 10.02. | Antrag Dauerfristverlängerung + **Sondervorauszahlung 1/11** (monthly filers); quarterly filers by 10.04. | §§ 46–48 UStDV |
| 25th after month/quarter | **ZM** (goods monthly or quarterly ≤ 50.000 €; services quarterly) | § 18a UStG |
| last day of month after quarter | **OSS** return and payment (if registered) | § 18j UStG |
| 10.03., 10.06., 10.09., 10.12. | **KSt-Vorauszahlung** + SolZ | § 31 KStG, § 37 EStG |
| 15.02., 15.05., 15.08., 15.11. | **GewSt-Vorauszahlung** to the Gemeinde | § 19 GewStG |
| 5th-last / 3rd-last Bankarbeitstag | SV **Beitragsnachweis** / **Beitragszahlung** (if SV-pflichtige employees) | § 28f Abs. 3 / § 23 Abs. 1 SGB IV |
| 16.02. | digital **Lohnnachweis** to the Berufsgenossenschaft; **DEÜV Jahresmeldung** by 15.02. | DGUV; § 10 DEÜV |
| 28.02. | Lohnsteuerbescheinigungen for employees transmitted; the Steuerbescheinigung § 45a Abs. 2 for distributions has **no** statutory deadline — issue on request, in practice together with the payout so the shareholder has it for the ESt return | § 41b EStG; § 45a Abs. 2 EStG |
| 31.03. | **Künstlersozialabgabe** Meldung of previous year's fees (if abgabepflichtig; 2026 rate **4,9 %**, 2025: 5,0 %; Bagatellgrenze 1.000 €/year since 2026 for Eigenwerber/Generalklausel) | § 27 KSVG; → https://www.kuenstlersozialkasse.de/nachrichten/detail/kuenstlersozialabgabe-sinkt-im-jahr-2026-auf-49-prozent |
| within 3 months / **6 months** after year end | **Jahresabschluss aufstellen** (Bilanz, GuV, Anhang unless Kleinst) — 6 months for kleine Kapitalgesellschaften "wenn dies einem ordnungsgemäßen Geschäftsgang entspricht" | § 264 Abs. 1 Satz 3–4 HGB → https://www.gesetze-im-internet.de/hgb/__264.html |
| within 8 / **11 months** | **Feststellung** des Jahresabschlusses and Ergebnisverwendungsbeschluss by the Gesellschafterversammlung (11 months for kleine Gesellschaften) | § 42a Abs. 2 GmbHG → https://www.gesetze-im-internet.de/gmbhg/__42a.html |
| **31.07.2026** (VZ 2025, without StB) / **01.03.2027** (VZ 2025, with StB; 28.02.2027 is a Sunday) | **KSt-Erklärung, GewSt-Erklärung, USt-Jahreserklärung, E-Bilanz** for 2025; VZ 2026: 02.08.2027 (31.07.2027 is a Saturday) / 29.02.2028 | § 149 Abs. 2, 3 AO (7 months / end of February of the second following year; first VZ without pandemic extensions) → https://www.gesetze-im-internet.de/ao_1977/__149.html ; → https://www.steuertipps.de/finanzamt-formalitaeten/abgabefrist-fuer-die-steuererklaerung |
| with the KSt return | **E-Bilanz** (§ 5b EStG): Bilanz + GuV **incl. unverdichtete Kontennachweise** (mandatory for FY starting after 31.12.2024), Anlagenspiegel; Taxonomie 6.9 (BMF 10.06.2025) for FY 2026, usable for FY 2025 | → https://www.gesetze-im-internet.de/estg/__5b.html ; → https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Einkommensteuer/2025-06-10-ebilanz-taxonomien-6-9.html |
| **within 12 months** after the Abschlussstichtag (31.12. for calendar-year companies) | **Offenlegung** at the **Unternehmensregister** (publikations-plattform.de; since FY 2022 no longer Bundesanzeiger): Kleinstkapitalgesellschaft → **Hinterlegung** of the Bilanz only (§ 326 Abs. 2 HGB); kleine → Bilanz + Anhang, no GuV (§ 326 Abs. 1). Ordnungsgeld by the Bundesamt für Justiz after a 6-week Nachfrist: min. 2.500 €, reduced to **500 €** (Kleinst) / **1.000 €** (klein) if filed late within the Nachfrist | § 325 Abs. 1a HGB → https://www.gesetze-im-internet.de/hgb/__325.html ; § 335 Abs. 4 HGB → https://www.gesetze-im-internet.de/hgb/__335.html ; → https://www.publikations-plattform.de/order/de/faq/uebermittlung |
| ongoing | **Transparenzregister**: wirtschaftlich Berechtigte registered and kept current (every change "unverzüglich"); annual fee 19,80 € since 2024 | § 20 GwG → https://www.gesetze-im-internet.de/gwg_2017/__20.html ; → https://www.haufe.de/id/beitrag/unternehmenspflichten-beim-transparenzregister-106-gebuehren-HI11575406.html |
| ongoing | **Handelsregister**: changes of Geschäftsführer, Sitz, Geschäftsanschrift, Satzung via Notar; new **Gesellschafterliste** after every share change (§ 40 GmbHG → https://www.gesetze-im-internet.de/gmbhg/__40.html); Geschäftsbriefe/invoices show Firma, Sitz, Registergericht, HRB, Geschäftsführer (§ 35a GmbHG) | |
| yearly (Bescheid) | **IHK-Beitrag**: Grundbeitrag + Umlage on the Gewerbeertrag; a UG is in the Handelsregister → **no** Existenzgründer exemption and no Umlage-Freibetrag (those are for natural persons) | § 3 Abs. 3 IHKG → https://www.gesetze-im-internet.de/ihkg/__3.html ; → https://www.ihk-muenchen.de/ueber-uns/beitrag/ |
| yearly | Betriebsprüfung readiness: GoBD export (Z3) for the closed year, Verfahrensdokumentation updated, Belege festgeschrieben monthly, Verrechnungskonto reconciled and interest booked, Gesellschafterbeschlüsse filed | § 147 Abs. 6 AO |

Size classes (raised for FY beginning after 31.12.2023, in force 17.04.2024): **Kleinstkapitalgesellschaft** § 267a HGB — not exceeding two of: Bilanzsumme **450.000 €** (was 350.000), Umsatzerlöse **900.000 €** (was 700.000), **10** employees; **kleine Kapitalgesellschaft** § 267 Abs. 1 — **7,5 Mio €** (was 6), **15 Mio €** (was 12), **50** employees; effect after two consecutive Abschlussstichtage (§ 267 Abs. 4) (→ https://www.gesetze-im-internet.de/hgb/__267a.html ; → https://www.gesetze-im-internet.de/hgb/__267.html ; → https://www.ihk-muenchen.de/ratgeber/recht/gesellschaftsrecht/anhebung-schwellenwerte-hgb/). Kleinst relief: no Anhang if certain data is shown under the Bilanz (§ 264 Abs. 1 Satz 5), condensed GuV, Hinterlegung instead of publication.

### 5.1 Month-end routine (BB)

1. Import/complete all bank and card transactions for the month; every transaction has a posting or a documented reason (Geldtransit, Verrechnungskonto).
2. Every posting has a Beleg: `receipts/get` for unpaid/unlinked receipts; Eingangsrechnungen without payment stay as Verbindlichkeiten (Kreditor); Ausgangsrechnungen as Forderungen (Debitor).
3. Reverse-charge check: each foreign vendor invoice carries `19_both_506`/`19_both_511` (or sits on 3123 | 5923 / 3125 | 5925); no foreign VAT booked as Vorsteuer.
4. Rates check: 7 % lines only for rail/taxi ≤ 50 km/books/hotel room/food; Bewirtung split 70/30 with Bewirtungsbeleg attached; Geschenke on 4630 | 6610 with recipient list.
5. Verrechnungskonto Gesellschafter: balance explained, repaid or interest agreement in place.
6. USt-Verprobung: Kz 81 × 19 % ≈ Kz 81 tax; Kz 46 × 19 % = Kz 47 = Kz 67 share; Kz 21 equals the ZM total for the period; Vorsteuer 66 plausible against 19 % expense accounts.
7. Transmit UStVA (and ZM by the 25th, Lohnsteuer-Anmeldung by the 10th); pay; book the payment on 1780 | 3820.
8. **Festschreiben** the month in BB after the UStVA is filed (GoBD: by end of the following month); store the ELSTER protocol as Beleg.
9. Update the Anlagenverzeichnis for new assets > 250 € (GWG list) and > 800 € (AfA).

### 5.2 Year-end hand-over to the Steuerberater (Kleinst-UG)

- SuSa and Journal export (DATEV format) for the full year, Kontennachweise; open-item lists Debitoren/Kreditoren at 31.12. with due dates.
- Bank statements at 31.12. for every account (incl. payment-processor balances = Forderung/Geldtransit), cash count if a Kasse exists.
- Anlagenverzeichnis: purchases with invoices, disposals; decision on Nutzungsdauer for IT (1 year vs 3 years) and degressive vs linear AfA.
- Contracts: Geschäftsführer-Anstellungsvertrag and any amendments (dated before payments), Gesellschafterdarlehen contracts and interest computation, Mietvertrag (Homeoffice), Gesellschafterbeschlüsse (Ergebnisverwendung, Ausschüttung), Rangrücktritte.
- Accruals: unpaid December invoices received in January (Verbindlichkeiten), work done but not yet invoiced (Forderungen/unfertige Leistungen), prepaid subscriptions (aktive RAP 0980 | 1900), Rückstellungen for Abschluss-/Steuerberatungskosten, Aufbewahrung, Urlaub, expected KSt/GewSt (Steuerrückstellungen).
- Tax accounts: Vorauszahlungen booked on 2200/2208/4320 | 7600/7608/7610; Bescheide for the year; UStVA sums vs. book Umsatzsteuer/Vorsteuer accounts (differences → 1790 | 3841).
- Payroll year-end: Lohnkonten, Lohnsteuerbescheinigungen, SV-Jahresmeldungen (if SV-pflichtig), Berufsgenossenschaft Lohnnachweis (16.02.).
- Special records: Bewirtungsbelege, Geschenkeliste (per recipient), Reisekostenabrechnungen, USt-IdNr confirmations for EU customers, ZM copies, OSS returns.
- Output you will receive back: Jahresabschluss (Bilanz, GuV, Anhang unless Kleinst-relief), E-Bilanz transmission protocol, KSt/GewSt/USt returns, Ergebnisverwendungsvorschlag incl. gesetzliche Rücklage (25 %), and the file for the Unternehmensregister (Hinterlegung within 12 months).

---

## 6. SKR03 ↔ SKR04 account table (small software/consulting UG)

Labels verified against the DATEV Kontenrahmen 2026 PDFs (Bau/Handwerk edition of the standard SKR, DATEV Dok. 0907817; standard core numbering, → https://www.datev.de/hilfe/0907817); labels marked (v) verified there, (u) not found in the extraction/unverified. BB may add individual Sachkonten — check `settings/get/postingaccounts`.

| Purpose | SKR03 | SKR04 | Note |
|---|---|---|---|
| Bank | 1200 Bank (v) | 1800 Bank (v) | further banks 1210…/1810… |
| Kasse | 1000 Kasse (v) | 1600 Kasse (v) | only if cash exists |
| Geldtransit (card settlements, transfers in transit) | 1360 (v) | 1460 (v) | payout of a payment processor: 1360 \| 1460 |
| Durchlaufende Posten | 1590 (v) | 1370 (v) | |
| Forderungen aus L+L | 1400 (v) | 1200 (v) | Debitoren 10000–69999 |
| Sonstige Vermögensgegenstände | 1500 (v) | 1300 (v) | Kautionen 1525 \| 1350 (v) |
| Forderungen gegen GmbH-Gesellschafter (Verrechnungskonto, debit side) | 1381 (v); ≤1 J 1382 | 1307 (v); ≤1 J 1308 | interest-bearing; vGA risk |
| Verbindlichkeiten gegenüber Gesellschaftern (Verrechnungskonto, credit side; Gesellschafterdarlehen) | 0730 (v); ≤1 J 0731; 1–5 J 0740; >5 J 0750 | 3510 (v); ≤1 J 3511; 1–5 J 3514; >5 J 3517; SKR04 alt. 3640 "gegenüber GmbH-Gesellschaftern" (v), ≤1 J 3641 | loan contract |
| Verbindlichkeiten gegenüber Gesellschaftern für offene Ausschüttungen | 0755 (v) | 3519 (v) | after Ausschüttungsbeschluss |
| Verbindlichkeiten aus Einbehaltungen (KapESt/SolZ) für offene Ausschüttungen | 1746 (v) | 3760 (v) | pay with KapEStA |
| Verbindlichkeiten aus L+L | 1600 (v) | 3300 (v) | Kreditoren 70000–99999 |
| Sonstige Verbindlichkeiten | 1700 (v) | 3500 (v) | |
| Verbindlichkeiten aus Steuern und Abgaben (KSt/GewSt payable) | 1736 (v) | 3700 (v) | or book taxes directly against Bank |
| Verbindlichkeiten aus Lohn und Gehalt / Lohn- und Kirchensteuer / soziale Sicherheit | 1740 / 1741 / 1742 (v) | 3720 / 3730 / 3740 (v; 3740 standard label "im Rahmen der sozialen Sicherheit") | payroll |
| Abziehbare Vorsteuer 7 % / 19 % | 1571 / 1576 (v) | 1401 / 1406 (v) | filled by vat code |
| Abziehbare Vorsteuer § 13b 19 % | 1577 (v) | 1407 (v) | Kz 67 |
| Abziehbare Vorsteuer i.g. Erwerb 19 % | 1574 (v) | 1404 (v) | Kz 61 |
| Umsatzsteuer 7 % / 19 % | 1771 / 1776 (v) | 3801 / 3806 (v) | |
| Umsatzsteuer § 13b 19 % | 1787 (v) | 3837 (v) | Kz 47/85 |
| Umsatzsteuer i.g. Erwerb 19 % | 1774 (v) | 3804 (v) | Kz 89 |
| USt-Vorauszahlungen / 1/11 Sondervorauszahlung | 1780 / 1781 (v) | 3820 / 3830 (v) | payments to Finanzamt |
| USt-Verbindlichkeiten Vorjahr / frühere Jahre | 1790 / 1791 (v) | 3841 / 3845 (v) | Jahreserklärung differences |
| Gezeichnetes Kapital (Stammkapital) | 0800 (v) | 2900 (v) | |
| Ausstehende Einlagen, nicht eingefordert | 0820 (v) | 2910 (v) | rarely for a UG (cash fully paid) |
| Kapitalrücklage | 0840 (v) | 2920 (v) | Agio, freiwillige Zuzahlungen § 272 Abs. 2 Nr. 4 HGB |
| Gesetzliche Rücklage (§ 5a Abs. 3 GmbHG) | 0846 (v) | 2930 (v) | 25 % of Jahresüberschuss |
| Gewinnvortrag / Verlustvortrag vor Verwendung | 0860 / 0868 (v) | 2970 / 2978 (v) | |
| Jahresüberschuss/-fehlbetrag | result of the GuV closing; DATEV 9000-range Saldovorträge | same | not a posting account in daily work |
| Darlehen (bank loans) | 0630 Verbindlichkeiten gegenüber Kreditinstituten (v) | 3150 (v) | |
| Umsatzerlöse 19 % | 8400 Erlöse 19 % USt (v; Automatikkonto) | 4400 (v) | Kz 81 |
| Umsatzerlöse 7 % | 8300 (v) | 4300 (v) | Kz 86 |
| Steuerfreie i.g. Lieferungen § 4 Nr. 1b | 8125 (v) | 4125 (v) | Kz 41, ZM |
| Steuerfreie Umsätze § 4 Nr. 1a (Ausfuhr) | 8120 (v) | 4120 (v) | Kz 43 |
| Erlöse EU B2B sonstige Leistungen (Steuerschuldnerschaft des Leistungsempfängers) | 8336 (v) | 4336 (v) | Kz 21, ZM |
| Erlöse Leistungen § 13b (customer owes German VAT) | 8337 (v) | 4337 (v) | Kz 60 |
| Erlöse Drittland (nicht steuerbar) | 8338 (v) | 4338 (v) | Kz 45 |
| Erlöse im anderen EU-Land steuerbar (OSS/B2C) | 8339 (v) | 4339 (v) | Kz 45 |
| Erlösschmälerungen / gewährte Skonti 19 % | 8700 / 8736 (v) | 4700 / 4736 (v) | |
| Sonstige betriebliche Erträge | 2700 (v; "andere betriebs-/periodenfremde sonstige Erträge"); Währungsgewinne 2660 (v) | 4830 (v); Währungsgewinne 4840 (v) | refunds, Versicherungsentschädigung |
| Fremdleistungen | 3100 (v) | 5900 (v) | freelancers, subcontractors |
| Sonstige Leistungen eines im anderen EU-Land ansässigen Unternehmers 19 % VSt/USt (§ 13b Abs. 1) | 3123 (v) | 5923 (v) | Automatikkonto, Kz 46/47 |
| Leistungen eines im Ausland ansässigen Unternehmers 19 % VSt/USt (§ 13b Abs. 2 Nr. 1) | 3125 (v) | 5925 (v) | Automatikkonto, Kz 84/85 |
| Innergemeinschaftlicher Erwerb 19 % VSt/USt (7 %) | 3425 (3420) (v) | 5425 (5420) (v) | goods from EU, Automatikkonto |
| Erhaltene Skonti 19 % VSt | 3736 (v) | 5736 (v) | |
| Löhne und Gehälter / Gehälter | 4100 / 4120 (v) | 6000 / 6020 (v) | |
| Geschäftsführergehälter (GmbH-Gesellschafter) | 4124 (v) | 6024 (v) | |
| Gesetzliche soziale Aufwendungen (employer SV) | 4130 (v) | 6110 (v) | |
| Freiwillige soziale Aufwendungen, lohnsteuerfrei | 4140 (v) | 6130 (v) | team events within Freibetrag |
| Miete (unbewegliche WG), Coworking | 4210 (v) | 6310 (v) | |
| Gas, Strom, Wasser | 4240 (v) | 6325 (v) | |
| Telefon / Internet | 4920 / 4925 (v) | 6805 / 6810 (v) | |
| Bürobedarf | 4930 (v) | 6815 (v) | |
| Porto | 4910 (v) | 6800 (v) | |
| Software licences/subscriptions (zeitlich befristete Überlassung von Rechten) | 4964 (v) | 6837 (v) | SaaS from DE with 19 % |
| EDV-Kosten: Wartung Hard-/Software, hosting, cloud | 4806 (v) | 6495 (v) | hosting commonly here or 4925 \| 6810 |
| Fachliteratur (Zeitschriften, Bücher, digitale Medien) | 4940 (v) | 6820 (v) | 7 % for print/e-books |
| Fortbildung | 4945 (v) | 6821 (v) | |
| Reisekosten Arbeitnehmer: Fahrtkosten / Übernachtung / Verpflegungsmehraufwand / Kilometergeld | 4663 / 4666 / 4664 / 4668 (v) | 6663 / 6660 / 6664 / 6668 (v) | 4660 \| 6650 general |
| Bewirtung abziehbar / nicht abziehbar | 4650 / 4654 (v) | 6640 / 6644 (v) | 70/30 |
| Aufmerksamkeiten | 4653 (v) | 6643 (v) | |
| Geschenke abziehbar (≤ 50 €) / nicht abziehbar / ausschließlich betrieblich nutzbar | 4630 / 4635 / 4638 (v) | 6610 / 6620 / 6625 (v) | |
| Werbekosten | 4600 (v) | 6600 (v) | ads, website |
| Rechts- und Beratungskosten | 4950 (v) | 6825 (v) | lawyer, Steuerberater advice |
| Buchführungskosten | 4955 (v) | 6830 (v) | BB subscription, Buchhaltungsservice |
| Abschluss- und Prüfungskosten | 4957 (v) | 6827 (v) | Jahresabschluss fee |
| Nebenkosten des Geldverkehrs (bank, card, PSP fees) | 4970 (v; 2026 sub-label "Kontoführungsgebühren") | 6855 (v) | no VAT |
| Versicherungen | 4360 (v) | 6400 (v) | no VAT (Versicherungsteuer is not VAT) |
| Beiträge (IHK, Verbände) | 4380 (v) | 6420 (v) | no VAT |
| Sonstige Abgaben / Verspätungszuschläge abzugsfähig / nicht abzugsfähig | 4390 / 4396 / 4397 (v) | 6430 / 6436 / 6437 (v) | Säumniszuschläge on Betriebssteuern are deductible; on KSt/GewSt not |
| Kfz-Kosten / Kfz-Steuer / laufende Betriebskosten | 4500 / 4510 / 4530 (v) | 6500 / 7685 / 6530 (v) | private use → vGA check |
| GWG Sofortabschreibung / Sammelposten AfA | 4855 / 4862 (v) | 6260 / 6264 (v) | |
| GWG asset / Sammelposten asset | 0480 / 0485 (v) | 0670 / 0675 (v) | |
| Abschreibungen Sachanlagen / immaterielle VG | 4830 / 4822 (v) | 6220 / 6200 (v) | |
| Betriebsausstattung / Geschäftsausstattung (EDV-Hardware) / Büroeinrichtung | 0400 / 0410 / 0420 (v) | 0630 / 0635 / 0650 (v) | SKR04 0640 is Ladeneinrichtung |
| EDV-Software (purchased licences, capitalised) | 0027 (v) | 0135 (v) | |
| Sonstige betriebliche Aufwendungen | 4900 (v) | 6300 (v) | last resort; Sonstiger Betriebsbedarf 4980 \| 6850 |
| Zinsaufwand (general / kurzfristige Verbindlichkeiten) | 2100 / 2120 (v) | 7300 / 7310 (v) | Gesellschafterdarlehen interest |
| Körperschaftsteuer / KSt für Vorjahre / KSt-Erstattungen Vorjahre | 2200 / 2203 / 2204 (v) | 7600 / 7603 / 7604 (v) | not deductible |
| Solidaritätszuschlag | 2208 (v) | 7608 (v) | |
| Gewerbesteuer / GewSt-Nachzahlungen und -Erstattungen Vorjahre | 4320 / 2281 (v) | 7610 / 7641 (v) | not deductible (§ 4 Abs. 5b) |
| Steuernachzahlungen / -erstattungen Vorjahre für sonstige Steuern | 2285 / 2287 (v) | 7690 / 7692 (v) | |
| Nicht abziehbare Betriebsausgaben (other) | 4654 Bewirtung, 4635 Geschenke, 4397 Verspätungszuschläge, 2380 Spenden nicht abziehbar (v) | 6644, 6620, 6437 (v); SKR04 Spenden account not extracted | add-backs in the KSt return |
| Privateinlagen / Privatentnahmen | — do not exist for a UG — | — | use 1381 \| 1307 or 0730 \| 3510 (Gesellschafter-Verrechnung); anything else is vGA/verdeckte Einlage territory |

---

## 7. Kontierung cheat sheet — typical Geschäftsvorfälle of a small tech UG

Format: Soll / Haben (SKR03 | SKR04), DATEV key and legal case, BB `vat`, Beleg, pitfalls. Amounts in BB posting endpoints are gross per line; BB derives net and tax from the `vat` code. "Bank" = 1200 | 1800.

| # | Case | Soll / Haben (SKR03 \| SKR04) | Key / legal case | Beleg requirements | Pitfalls |
|---|---|---|---|---|---|
| 1 | SaaS subscription from an Irish/Luxembourg vendor, no VAT, your USt-IdNr on the invoice | 3123 \| 5923 (or 4964 \| 6837 with key) / Bank or Kreditor | § 13b Abs. 1 UStG, BU 94; BB `19_both_506`; Kz 46/47 + 67 | invoice with both USt-IdNr, reverse-charge note, Leistungszeitraum | vendor charged Irish VAT → your USt-IdNr not in the vendor account: fix account, request corrected invoice; foreign VAT never deductible |
| 2 | US API/cloud vendor, no VAT | 3125 \| 5925 / Bank | § 13b Abs. 2 Nr. 1 UStG (im Ausland ansässiger Unternehmer), Automatikkonto (BU 94 logic); BB `19_both_511`; Kz 84/85 + 67 | vendor invoice (their receipt is fine if it names your company), Leistungszeitraum | card statements alone are not Belege; monthly receipts must be downloaded; tax arises at invoice date, latest month after service |
| 3 | Domestic freelancer invoice 19 % | 3100 \| 5900 / 1600 \| 3300 (Kreditor), then Kreditor / Bank | BU 9; BB `19_pre`; Kz 66 | § 14 Abs. 4 complete incl. Leistungszeitraum, Steuernummer | freelancer is Kleinunternehmer → no VAT, `0_none`; Scheinselbständigkeit is an SV risk (Statusfeststellung) |
| 4 | Hardware ≤ 800 € net (monitor set, keyboard, router) | 4855 \| 6260 (or 0480 \| 0670 then AfA) / Bank | GWG § 6 Abs. 2 EStG; BU 9; BB `19_pre` | invoice to the UG | > 250 €: record in Anlageverzeichnis; monitor alone is not selbständig nutzbar — with the PC it is one asset |
| 5 | Laptop 1.800 € net | 0410 \| 0635 Geschäftsausstattung (or 0420 \| 0650) / Bank; AfA at year end 4830 \| 6220 / 0410 \| 0635 | § 7 EStG; 1-year Nutzungsdauer (BMF 22.02.2022) or degressive 30 %; BU 9; BB `19_pre` | invoice to the UG, serial number in the Anlagenverzeichnis | private use by the GGF must be agreed (Sachbezug) or is vGA; handels- vs steuerrechtliche Nutzungsdauer decision |
| 6 | Domain/hosting from a German provider 19 % | 4806 \| 6495 (or 4925 \| 6810) / Bank | BU 9; BB `19_pre` | invoice with Leistungszeitraum | annual prepayment → aktive RAP if material |
| 7 | Long-distance rail ticket (Fernverkehr) | 4663 \| 6663 / Bank or Verrechnungskonto | 7 % Schienenbahn (§ 12 Abs. 2 Nr. 10 UStG); BU 8; BB `7_pre` | online ticket = Fahrausweis § 34 UStDV (name, date, amount) | international legs are exempt/not taxable → `0_none`; BahnCard: 19 % if pure business |
| 8 | Taxi | 4663 \| 6663 / Bank | 7 % within town or ≤ 50 km, else 19 %; BU 8 / 9; BB `7_pre` / `19_pre` | Quittung ≤ 250 € with rate | app receipts from foreign platforms may be § 13b (platform fee) — check who is the supplier |
| 9 | Hotel with breakfast | 4666 \| 6660 room (7 %) / 4666 breakfast food (7 % since 2026) / 4666 drinks-parking (19 %) / Bank | BU 8 + 9; BB `7_pre` + `19_pre` split lines | invoice addressed to the UG (not to the traveller privately) | breakfast included → cut Verpflegungspauschale 20 %; Business-Package split 15 % at 19 % |
| 10 | Restaurant with a client (Bewirtung) — bill 100 € food + 30 € drinks net | 4650 \| 6640 70 % + 4654 \| 6644 30 % of each rate line / Bank | § 4 Abs. 5 Nr. 2 EStG; Vorsteuer 100 % (§ 15 Abs. 1a S. 2); BU 8 (food 7 %) + BU 9 (drinks 19 %); BB `7_pre` + `19_pre`, each split 70/30 → four lines | TSE bill, Bewirtungsbeleg (Ort, Tag, Teilnehmer, Anlass, Höhe, signature); > 250 € printed name of host | tip: on bill or Eigenbeleg, 70/30 too; handwritten bill = no deduction (BMF 19.11.2025) |
| 11 | Team lunch / workshop catering for employees | 4140 \| 6130 (or 6640 "Bewirtung intern") / Bank | fully deductible; Vorsteuer 100 %; BU 8/9; BB `7_pre`/`19_pre` | bill with participants | Arbeitslohn unless Betriebsveranstaltung ≤ 110 € or Arbeitsessen ≤ 60 € at an außergewöhnlicher Einsatz; a solo GGF lunch is private |
| 12 | Coworking rent 19 % | 4210 \| 6310 / Bank | BU 9; BB `19_pre` | contract + monthly invoice (Dauerrechnung with Leistungszeitraum) | landlord without VAT option → `0_none`; Kaution → 1525 \| 1350 |
| 13 | Bank fees, card fees | 4970 \| 6855 / Bank | exempt § 4 Nr. 8 UStG; no key; BB `0_none` | bank statement/fee notice is the Beleg | never `19_pre` |
| 14 | Payout of a payment processor (Irish entity), net of fees; sales of 1.000 € gross, fee 29 € | Bank 971 + 4970 \| 6855 29 / 1360 \| 1460 Geldtransit 1.000 (or directly / Forderungen) ; the sales themselves: Forderungen \| Debitor / 8400 \| 4400 1.000 (`19_vat`) per invoice or daily summary | fees exempt § 4 Nr. 8 (payment services) → `0_none`; no § 13b tax arises on an exempt service | processor's monthly fee invoice + payout report | book revenue gross, never the net payout as revenue; reconcile the Geldtransit to zero monthly; if the processor also charges taxable services (dashboard, fraud tools) those are § 13b Abs. 1 `19_both_506` |
| 15 | Stammkapital paid in (e.g. 1.000 €) | Bank / 0800 \| 2900 | no VAT; BB `0_none` (free posting) | Gesellschaftsvertrag, bank receipt (Nachweis for the notary) | pay from the shareholder's account with reference "Stammeinlage"; the UG must not pay founding costs beyond what the Satzung allows |
| 16 | Gesellschafterdarlehen received 10.000 € | Bank / 0730 \| 3510 (or 3640; long-term 0740/0750 \| 3514/3517) | `0_none` | written loan contract dated before the transfer | interest booked yearly 2120 \| 7310 / 0730 \| 3510; Rangrücktritt in crisis; § 135 InsO on repayments |
| 17 | Gesellschafterdarlehen repaid + interest | 0730 \| 3510 / Bank; 2120 \| 7310 / Bank | `0_none` | contract, interest calculation | no KapESt withholding on loan interest; shareholder taxes it personally |
| 18 | Geschäftsführergehalt 4.000 € gross, beherrschender GGF (no SV): Lohnsteuer 700 € | 4124 \| 6024 4.000 / 1740 \| 3720 3.300 (net) + 1741 \| 3730 700; payment 1740 \| 3720 / Bank; LSt 1741 \| 3730 / Bank | `0_none` | Anstellungsvertrag, monthly Lohnabrechnung, LSt-Anmeldung | irregular or unpaid salary of a beherrschender GGF → vGA; with SV: employer share 4130 \| 6110 / 1742 \| 3740 |
| 19 | KSt-Vorauszahlung + SolZ | 2200 \| 7600 and 2208 \| 7608 / Bank | `0_none` | Vorauszahlungsbescheid | not deductible — add back in the tax computation; GewSt Vorauszahlung 4320 \| 7610 / Bank |
| 20 | USt-Zahllast paid to the Finanzamt | 1780 \| 3820 / Bank (Sondervorauszahlung 1781 \| 3830) | `0_none` | UStVA transmission protocol | refund: Bank / 1780 \| 3820; year-end reclass to 1790 \| 3841 by the Steuerberater |
| 21 | Own invoice to a German B2B customer 5.000 € + 19 % | Forderungen 1400 \| 1200 (Debitor) 5.950 / 8400 \| 4400 5.000 + 1776 \| 3806 950 | BU 3; BB `19_vat`; Kz 81 | § 14 Abs. 4 complete; E-Rechnung from 2027/2028 | Leistungszeitraum decides the period; Skonto granted later → 8736 \| 4736 |
| 22 | Own invoice to an EU B2B customer (valid USt-IdNr) 5.000 € | Forderungen / 8336 \| 4336 5.000 | § 3a Abs. 2 → not taxable; BU 47; BB `0_none`; Kz 21; **ZM** (quarterly) | both USt-IdNr, "Steuerschuldnerschaft des Leistungsempfängers", qualifizierte Bestätigung archived | no valid USt-IdNr → German 19 % or OSS; ZM omission = penalty and Kz 21 mismatch |
| 23 | Own invoice to a non-EU business customer | Forderungen / 8338 \| 4338 | § 3a Abs. 2 → not taxable; no key; BB `0_none`; Kz 45 | note "nicht im Inland steuerbar"; evidence of business status | consumer in Drittland: Katalogleistung → same; other services → 19 % |
| 24 | Kleinbetragsrechnung issued/received ≤ 250 € | as the underlying case | § 33 UStDV; Vorsteuer by 19/119 or 7/107 (§ 35) | name/address of supplier, date, description, gross, rate | no recipient needed, but not for § 13b/i.g. cases; E-Rechnung-exempt |
| 25 | Eigenbeleg (lost taxi receipt 18 €, tip) | 4663 \| 6663 / Verrechnungskonto or Kasse | no Vorsteuer; BB `0_none` | date, amount, purpose, payee, reason, signature | keep rare; auditors sample them |
| 26 | Skonto taken on a supplier invoice (2 % of 1.190 €) | Kreditor 1.190 / Bank 1.166,20 + 3736 \| 5736 20 (net) + Vorsteuer correction 3,80 | BU 9 on the Skonto line (BB `19_pre` on 3736 \| 5736) | supplier invoice with Skonto term | Vorsteuer must be corrected (§ 17 UStG); BB handles it when the Skonto line carries the same vat code |
| 27 | Rücklastschrift (returned direct debit) + bank fee | reverse the original payment (Kreditor / Bank storno); fee 4970 \| 6855 / Bank | fee exempt § 4 Nr. 8; `0_none` | bank notice | do not book the fee as Skonto or Erlösschmälerung |
| 28 | Private purchase with the company card (GGF) | 1381 \| 1307 / Bank | no expense, no Vorsteuer; `0_none` | card statement; repayment by the GGF | repay promptly or charge arm's-length interest; recurring items → vGA |
| 29 | Ad-platform invoice (Irish entity) with Irish VAT wrongly charged | 4600 \| 6600 gross incl. Irish VAT / Bank (`0_none`); additionally declare § 13b Abs. 1 on the net (line on 3123 \| 5923 `19_both_506` for the net, ask Steuerberater for the practical handling) | § 13b Abs. 1; § 15 covers German tax only | invoice; screenshot of the account's tax settings | enter your USt-IdNr in the vendor account so future invoices are net; request re-issue; do not deduct foreign VAT |
| 30 | App-store / OS vendor subscriptions (Irish entities) | business account with USt-IdNr: 4964 \| 6837 via 3123 \| 5923 logic, `19_both_506` (§ 13b Abs. 1); consumer-style receipt with German 19 % VAT: `0_none` gross (VAT is § 14c, not deductible) | | monthly invoice from the developer/business portal | switch the account to business/USt-IdNr; receipts addressed to a private person are not the UG's Belege |
| 31 | Gewinnausschüttung 10.000 € with KapESt | 0860 \| 2970 / 0755 \| 3519 10.000; 0755 \| 3519 / 1746 \| 3760 2.637,50; 0755 \| 3519 / Bank 7.362,50; 1746 \| 3760 / Bank 2.637,50 | § 43 Abs. 1 Nr. 1, § 43a EStG 25 % + SolZ 5,5 % = 26,375 %; KapEStA at Zufluss | Gesellschafterbeschluss (Ergebnisverwendung), Steuerbescheinigung § 45a | gesetzliche Rücklage first (§ 5a Abs. 3 GmbHG); § 30 GmbHG; Zufluss = payment date in the Beschluss, else day after the Beschluss (§ 44 Abs. 2 EStG) |
| 32 | Gesetzliche Rücklage at year end (Jahresüberschuss 8.000 €, no Verlustvortrag) | Ergebnisverwendung / 0846 \| 2930 2.000 | § 5a Abs. 3 GmbHG (25 %) | Beschluss / Jahresabschluss | usually booked by the Steuerberater in the Abschluss |
| 33 | Verpflegungsmehraufwand paid to the GGF (2 days, 14+28+14 €) | 4664 \| 6664 56 / 1381 \| 1307 or Bank | § 9 Abs. 4a EStG; `0_none` | Reisekostenabrechnung with times and purpose | cut for provided meals; three-month rule; no Vorsteuer on Pauschalen |
| 34 | Kilometergeld 0,30 €/km for the GGF's private car | 4668 \| 6668 / 1381 \| 1307 or Bank | § 3 Nr. 16 EStG, BRKG § 5 Abs. 2; `0_none` | Fahrtenaufzeichnung per trip (date, route, km, purpose) | commuting is not a Dienstreise |
| 35 | Hardware bought from an EU webshop, 0 % with your USt-IdNr | 0410 \| 0635 or 4855 \| 6260 / Bank via 3425 \| 5425 logic | i.g. Erwerb § 1a; BU 19; BB `19_both_2`; Kz 89 + 61 | invoice with both USt-IdNr, "innergemeinschaftliche Lieferung" | shop charged German 19 % → normal `19_pre` instead |
| 36 | IHK-Beitrag, insurance premium | 4380 \| 6420 / Bank; 4360 \| 6400 / Bank | no VAT; `0_none` | Beitragsbescheid, Police | Versicherungsteuer is not Vorsteuer |

---

## 8. Red flags — ask the Steuerberater before booking or deciding

- **vGA suspicion**: any payment or benefit to the GGF/shareholder without a prior written agreement, above-market salary/rent/interest, private costs in the books, debit balance on the Verrechnungskonto without interest, company car use (→ https://www.reiss-steuerkanzlei.de/post/verdeckte-gewinnausschuettung-gmbh).
- **Betriebsstätte abroad / GGF living abroad or working long from another country**: permanent establishment and Ort der Geschäftsleitung (§ 10 AO) risks under the DBA; foreign payroll/social-security registration; Wegzugsbesteuerung § 6 AStG for the shareholder.
- **OSS / B2C sales into the EU**, marketplaces, digital goods to consumers, and any **Drittland VAT registration** (e.g. Swiss VAT, UK VAT on digital services).
- **Umsatzsteuer-Option** (§ 9 UStG) for renting out property or subletting the office; **Vorsteueraufteilung** § 15 Abs. 4 when exempt turnover appears (e.g. selling a used car is taxable, but Zinserträge/bank interest are exempt but irrelevant).
- **Investitionsabzugsbetrag / Sonderabschreibung § 7g**, degressive vs linear AfA choice, GWG vs Sammelposten policy — planning items with multi-year effect.
- **Rückstellungen** (§ 249 HGB): Abschluss- und Prüfungskosten, Aufbewahrung, Urlaub, drohende Verluste, Prozessrisiken; **latente Steuern** (§ 274 HGB, waivable for small companies § 274a); RAP for prepaid subscriptions.
- **Umwandlung UG → GmbH**, Anteilsübertragungen, new shareholders, Holding structures, Verkauf of shares: notarial and tax steps, § 8c KStG.
- **§ 8c KStG Verlustuntergang**: transfer of more than 50 % of the shares within five years destroys the Verlustvortrag (fortführungsgebundener Verlustvortrag § 8d as escape) (→ https://www.gesetze-im-internet.de/kstg_1977/__8c.html); **Mindestbesteuerung** § 10d Abs. 2 EStG: 1 Mio € unlimited, above that 70 % (2024–2027; 60 % before/after) (→ https://www.gesetze-im-internet.de/estg/__10d.html).
- **Insolvenzreife / Überschuldung**: Zahlungsunfähigkeit → application within **3 weeks**, Überschuldung within **6 weeks** (§ 15a InsO → https://www.gesetze-im-internet.de/inso/__15a.html); Überschuldung is excluded if a positive **Fortführungsprognose for the next 12 months** exists (§ 19 Abs. 2 InsO → https://www.gesetze-im-internet.de/inso/__19.html); a UG with 1 € Stammkapital and start-up losses is quickly bilanziell überschuldet — Rangrücktritt on Gesellschafterdarlehen and a documented prognosis are essential; § 5a Abs. 4 GmbHG duty to convene the shareholders when Zahlungsunfähigkeit droht; Zahlungsverbot § 15b InsO.
- **Payroll beyond the GGF**: first employee (Betriebsnummer, Umlagen U1/U2, Minijob rules), Scheinselbständigkeit of long-term freelancers, Künstlersozialabgabe when paying designers/copywriters/photographers above 1.000 €/year.
- **E-Rechnung readiness 2027/2028**, format validation failures, and archiving of XML in BB.
- **Kryptowährungen, Fremdwährungskonten, Auslandskonten**: valuation (§ 256a HGB), Kursdifferenzen: Erträge/Aufwendungen aus der Währungsumrechnung 2660/2150 | 4840/6880 (DATEV 2026), Meldepflichten.
- Anything where the UStVA result looks wrong (Kz 21 vs ZM, Kz 46/47 ≠ Kz 67, negative Vorsteuer), a Finanzamt letter arrives (Nachfrage, Verspätungszuschlag, Prüfungsanordnung), or a Beleg cannot be produced for a booked amount.

---

## 9. Glossary (German term → meaning used here)

| Term | Meaning |
|---|---|
| **Abschlussstichtag** | balance-sheet date (31.12. for calendar-year companies) |
| **AfA** (Absetzung für Abnutzung) | tax depreciation |
| **Anlagenverzeichnis / Anlagespiegel** | fixed-asset register / fixed-asset schedule (part of the E-Bilanz) |
| **Aufteilungsgebot** | duty to split one price into components with different VAT rates (hotel room vs breakfast) |
| **Automatikkonto** | DATEV account that carries its tax treatment in its name; posted without BU key |
| **Beherrschender Gesellschafter-Geschäftsführer** | controlling shareholder-director (≥ 50 % or blocking minority) |
| **Beleg / Eigenbeleg / Fremdbeleg** | voucher / self-made voucher / third-party voucher |
| **Betriebsprüfung** | tax audit (Außenprüfung) |
| **BU / GU** | Buchungsschlüssel (tax key) / Generalumkehrschlüssel (reversal key, BU + 20) |
| **Dauerfristverlängerung** | permanent one-month extension for UStVA filing/payment |
| **Debitor / Kreditor** | customer / supplier sub-ledger account |
| **Erwerbsteuer** | German VAT self-assessed on an innergemeinschaftlicher Erwerb |
| **Festschreibung** | GoBD locking of postings; afterwards only reversals |
| **Fremdvergleich** | arm's-length test (vGA) |
| **Gelangensnachweis / Gelangensbestätigung** | proof that goods arrived in another EU state (i.g. Lieferung) |
| **Gesamtumsatz** | total turnover as defined in § 19 Abs. 2 UStG (basis for Kleinunternehmer, Ist-Versteuerung, E-Rechnung transition) |
| **GGF** | Gesellschafter-Geschäftsführer (shareholder-director) |
| **GWG** | geringwertiges Wirtschaftsgut (low-value asset ≤ 800 € net) |
| **Hebesatz** | municipal trade-tax multiplier |
| **Hinterlegung** | deposit of the Bilanz at the Unternehmensregister without publication (Kleinst) |
| **i.g.E. / i.g. Lieferung** | innergemeinschaftlicher Erwerb (EU purchase of goods) / intra-EU supply of goods |
| **Kennzahl (Kz)** | field code in the UStVA form |
| **Kleinbetragsrechnung** | small-amount invoice ≤ 250 € gross with reduced content |
| **Leistungsdatum / Leistungszeitraum** | date / period of supply — decides the booking period and VAT month |
| **Offenlegung** | disclosure of the Jahresabschluss at the Unternehmensregister |
| **RAP** (Rechnungsabgrenzungsposten) | prepaid expenses / deferred income (aktive / passive) |
| **Rangrücktritt** | subordination agreement for a shareholder loan |
| **Reverse charge / Steuerschuldnerschaft des Leistungsempfängers** | VAT owed by the customer (§ 13b) |
| **Sammelposten** | pooled asset item 250–1.000 € written off over five years |
| **Soll / Haben** | debit / credit |
| **Sondervorauszahlung** | 1/11 special prepayment for the Dauerfristverlängerung |
| **SuSa** | Summen- und Saldenliste (trial balance) |
| **USt / VSt / USt-IdNr** | Umsatzsteuer (output VAT) / Vorsteuer (input VAT) / VAT identification number |
| **UStVA** | Umsatzsteuer-Voranmeldung (advance VAT return) |
| **Verrechnungskonto** | clearing account (here: shareholder clearing account) |
| **vGA** | verdeckte Gewinnausschüttung (hidden profit distribution) |
| **Voranmeldungszeitraum** | UStVA period (month or quarter) |
| **Zahllast** | VAT payable (Umsatzsteuer minus Vorsteuer) |
| **ZM** | Zusammenfassende Meldung (EC sales list) |

## 10. Verification notes

Verified 2026-09-13 against gesetze-im-internet.de (UStG §§ 1a, 3a, 3c, 4, 12, 13, 13b, 14, 14a, 14b, 14c, 15, 18, 18a, 18e, 18j, 19, 20, 27; UStDV §§ 33–35, 46–48, 61, 61a; AO §§ 146, 147, 149, 152; EStG §§ 4, 6, 7, 7g, 8, 9, 10d, 19, 37, 37b, 41a, 43a, 44, 5b; KStG §§ 8, 8c, 23, 31; GewStG §§ 8, 11, 16, 19; SolzG § 4; GmbHG §§ 5a, 40, 42a; HGB §§ 257, 264, 267, 267a, 274a, 325, 326, 335; InsO §§ 15a, 19, 135; SGB IV §§ 7a, 23; IHKG § 3; GwG § 20; BRKG § 5), the BMF UStVA 2026 form, BMF letters (GoBD 11.03.2024, E-Rechnung 15.10.2025, Bewirtung 19.11.2025, E-Bilanz 10.06.2025, Reisekosten Ausland 05.12.2025), the DATEV Kontenrahmen 2026 PDFs (SKR03/SKR04) and the DATEV Steuerschlüssel-Tabelle (Dok. 0907049, 2023 edition; BU keys unchanged since). Secondary sources (Haufe, IHK, lexware, sevdesk, Steuerberater blogs) are cited where no primary text was fetched. Items marked (u)/(unverified) are listed in the skill's open questions.
