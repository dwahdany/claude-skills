---
name: pro
description: Explicit-invocation only — consult this skill when the user types /pro or names it directly, and not otherwise. Applies the house internal register — high-density prose, stacked hyphen-compounds, ad-hoc acronym coinage, parenthetical status tags, explicit decision-rights handoffs, at a user-selected depth (P1/P2/P3). The depth level is the user's call and changes which readers the output loses, so this skill should never be started on Claude's own initiative — a rewrite request on its own is handled normally, without it. Counterpart to /bro, which does the inverse.
disable-model-invocation: true
argument-hint: "[1|2|3]"
---

# /pro — house register

A repeatable pass converting plainly-written internal prose into the house register: maximum signal per line for readers who already share the context.

The register exists because internal readers are context-rich and time-poor. Density is the point — but density is also the failure mode, so most of this skill is about which compressions pay and which ones quietly cost content, credibility, or the one reader you most needed to convince.

## Invocation

Run only when called. `/pro` on its own applies **P2**. `/pro 1` and `/pro 3` select depth explicitly.

The gate matters because the three depths differ in *which readers they lose*, not just in how dense they are — and that's the author's call, not a default. Auto-applying this register to a doc heading for sign-off or external circulation makes it worse, confidently. If the target audience is unclear from context and there's any sign the document leaves the team, ask for a depth before writing rather than assuming P2.

## The pass

Work in this order. Ordering matters: compressing before inventorying is how content disappears.

### 1. Inventory before compressing

List every load-bearing claim in the source before writing a word of output. Compression feels like editing but behaves like deletion — an item never logged is an item you won't notice missing. Check the finished draft against the list.

### 2. Split spine from body

Two content types, compressed differently:

- **Spine** — passages doing argumentative work: why this matters, why the alternative fails, what the reader must decide. Spine keeps full sentences. Telegraphing an argument makes it unverifiable, and an unverifiable argument persuades nobody.
- **Body** — enumerable content: taxonomies, task lists, tiers, options, criteria. Telegraph freely — fragments, arrows, tables, slash-pairs.

Most drafts arrive with the body over-written and the spine under-written. The pass usually *shortens* the body and *sharpens* rather than shortens the spine.

### 3. Coin the term set

Ad-hoc acronyms and compounds are the register's main compression lever and its main route to unreadability. A coinage earns its place by clearing at least one of:

- **Recurrence** — appears 3+ times. Below that, defining it costs more than abbreviating saves.
- **Tabularity** — it will become a column header, row label, or axis in some downstream artifact (results table, dashboard, ticket field). A short name for a four-tier severity scale pays for itself the first time someone builds the table.
- **Disambiguation** — naming two things separately makes a conflation visible. If the document's argument is that readers conflate X with Y, giving X and Y distinct short names *is* the argument, not shorthand for it.

Coinages clearing none of these are a tax with no return. Cut them.

Prefer coinages that partially decode on sight (`TTM` for time-to-mitigate) over opaque ones. Never coin two terms colliding on the same letters. Keep existing team shorthand in quotes on first use rather than replacing it.

### 4. Build the term block

Put every coinage in one dense block near the top, defined once, middot-separated. This is the mechanism letting the body run at full compaction without stranding a cold reader — load-bearing, not front-matter. When the user cuts for space, cut elsewhere and say why.

```
**Terms.** TTM time-to-mitigate · RB/FF rollback / fix-forward · CF change-freeze ·
SEV1…SEV4 severity tiers · PIR post-incident review
```

If you relabel identifiers the source already used, record the old→new mapping here so the change survives contact with people holding old references.

### 5. Compact

Apply the constructions in **Register inventory** below. Convert prose lists to tables where the content has consistent columns — a table is denser than any prose equivalent and it forces you to notice missing cells.

### 6. Separate what you added from what was theirs

The register sounds settled and authoritative, so anything you add reads as if the source author asserted it. Itemize your additions *outside* the document, so the author can disown them without hunting. Same for structural changes: if you relabelled a taxonomy or reordered sections, say so and confirm it's revertible.

### 7. Report the tradeoff, once

State the density/accessibility cost briefly, with the mitigation already built in. Don't hedge repeatedly or ask permission for the register the user requested.

## Register inventory

| Move | Form | Plain → register |
|---|---|---|
| Hyphen-compound premodifier | `X-Yed`, `X-Ying` | "a flag enabled by default" → "enabled-by-default flag" |
| Suffix families | `-shaped`, `-bearing`, `-guarded`, `-native`, `-blind`, `-dominant` | "roughly fits the spec" → "spec-shaped"; "treats every locale the same" → "locale-blind" |
| Slash-pair | `A/B`, `A-yes/B-no` | "passes staging but fails prod" → "staging-yes/prod-no" |
| Arrow for consequence | `→` | "which means we can roll back per tenant" → "→ per-tenant rollback" |
| Parenthetical status tag | `(clean)`, `(no-op)`, `(pending)` | appends verification state to a claim |
| Noun-stack | compound abstract nouns | "the gap between what we monitor and what we alert on" → "monitoring-alerting gap" |
| Clipped copula | drop articles and auxiliaries | "The quote is an estimate, not a guarantee." → "Quote is estimate, not guarantee." |
| First-person verification | "I smoke-verified X (clean)" | own your own checks explicitly |
| Em-dash decision handoff | "— that call is yours" | close by returning decision rights |

The closing handoff is a feature, not a flourish: the register's signature move is separating what the writer has settled from what the reader must decide. Preserve it even when compressing hard.

## What not to compress

- **Anything you'd have to invent to fill.** Status tags are the trap — `(clean)`, `(scoped)`, `(unauthored)` suit the register beautifully and invite fabrication. Only tag what you hold real values for. If the values exist somewhere you can't see, leave the slot and flag it.
- **Empty sections.** A heading with nothing under it: don't silently fill it, don't silently drop it. Either frame the emptiness deliberately or ask what belongs there.
- **Hedges carrying legal, safety, or attribution weight.** "Plausibly", "we don't yet know", "not mine to settle" are load-bearing. Compressing a hedge into a claim is the most expensive available mistake here, precisely because the output sounds confident.
- **Technical abstraction level.** Never add specifics the source lacked. Density is a prose operation, not a research one — if the source named categories, the output names categories.

## Failure modes

- **Opacity mistaken for density.** Test: could a smart, adjacent, non-team reader follow this with only the term block? If not, you compressed the spine.
- **Register drift into parody.** Every compound should replace words. A compound replacing nothing is costume.
- **Authorial laundering.** See step 6. Non-optional.
- **Losing the persuasion target.** Ask which sections exist to convince someone who doesn't already agree — skeptical reviewers, external readers, sign-off authorities. Those sections have the least tolerance for shared-context assumptions, and they're the ones acronym-density loses first.

## Depth control

Offer a level rather than guessing:

- **P1** — house voice, structure intact, no coinage. Survives cold reading. Use for sign-off, external circulation, anything that must persuade a reader who doesn't already agree.
- **P2** — coinage + term block + telegraphed body + tables where columns are consistent. Standard house output.
- **P3** — connective compression on the spine. Narrow applicability; see below.

**Tables belong at P2, not P3.** A table is *terminal* — once content sits in a grid there's no further compression available, so it can't be a last step. It's also set-shaped rather than sequence-shaped: tabularizing an argument destroys the chain that made the argument checkable, which is a category error dressed as compression. Tables do earn their P2 place, for a reason worth keeping in mind — they force you to notice missing cells. Prose hides gaps; an empty cell is visibly empty.

### What P3 actually is

By P3 the body is already telegraphed and tabularized, so the only compressible material left is the spine — and spine is sequential and causal. P3 is therefore **connective compression**: delete the words carrying a logical relation while preserving the relation itself.

| Move | Replaces | P2 → P3 |
|---|---|---|
| Semicolon-chained clauses | "and also", "meanwhile", "it then" | "The job builds the cache. It then swaps the pointer." → "Job builds cache; swaps pointer." |
| Em-dash apposition | "which is", "that are" | "the fallback path, which is load-bearing" → "the fallback path — load-bearing" |
| Colon-as-expansion | "the reason is that" | "The reason is that X" → "Reason: X" |
| Collapsed conditional | if/then | "If it passes on staging but fails in prod, config drift is the cause" → "Staging pass, prod fail: config drift." |
| Negation-pair | definition + warning in four words | "an estimate rather than a guarantee" → "estimate, not guarantee" |
| Agent deletion | inferable subject | "We can't ship a fix we can't distinguish from a regression" → "No shipping a regression-indistinguishable fix" |
| Meta-sentence deletion | scaffolding | cut any sentence announcing what the next sentence will do — usually the single largest win |

### The P3 constraint

P3's failure mode differs in kind from P2's, and it's worse. P2 fails by opacity: the reader doesn't know a coinage, asks, gets told — recoverable. P3 fails by **relational ambiguity**. A semicolon or em-dash marks that a relation exists without specifying which; "X; Y" reads as *therefore*, *whereas*, or *namely* depending on the reader. Someone who reconstructs "therefore" where you meant "whereas" has misread the argument and has no signal they did. No term block fixes that. A confused reader asks; a confidently-misreading reader signs off on the wrong thing.

So P3 is not uniformly denser — selectively denser. **Compress a connective only where the relation is recoverable from content alone.** Ranked by safety: arrows (`→`) specify direction, safest; colons specify expansion; em-dashes specify apposition loosely; semicolons specify nothing, riskiest. Where two readings are both plausible, spend the word.

Two carve-outs bind hardest at P3, since this is where the pressure to cut is highest and the cost worst:

- **Hedges stay.** "Plausibly", "we don't yet know", "not mine to settle" look like scaffolding at this density. They aren't.
- **Attribution stays.** Who verified what; who owns the open call.

**Who P3 is for:** readers who wrote adjacent parts of the document, or a second read. Not sign-off, not external, not persuasion. P3 is narrower than P2 rather than better than it — offer it as a different tool, not an upgrade.

Default to P2. If the user says an output still isn't dense enough, the remaining fat is in the spine — say so explicitly rather than compressing it silently, because spine shouldn't shrink without a decision.
