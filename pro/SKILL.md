---
name: pro
description: Explicit-invocation only — consult this skill when the user types /pro or names it directly, and not otherwise. Applies the house internal register — high-density continuous prose, stacked hyphen-compounds, ad-hoc acronym coinage, parenthetical status tags, explicit decision-rights handoffs, at a user-selected depth (P1/P2/P3). Output is prose only, shorter than its source: no tables, no glossary block, no introduction, no commentary about the pass. The depth level is the user's call and changes which readers the output loses, so this skill should never be started on Claude's own initiative — a rewrite request on its own is handled normally, without it. Counterpart to /bro, which does the inverse.
disable-model-invocation: true
argument-hint: "[1|2|3]"
---

# /pro — house register

Maximum signal per line, for readers who already share the context. Density is the point and also the failure mode — most of what follows is which compressions pay and which quietly cost content, credibility, or the one reader you needed to convince.

## Invocation

Only when called. `/pro` → **P2**; `/pro 1` and `/pro 3` select depth. The depths differ in *which readers they lose*, not just in density, so the level is the author's call and never a default. Unclear audience plus any sign the document leaves the team: ask before writing.

## Output shape

Continuous prose. Bold run-in heads, then sentences. No tables, no glossary block, no trailing notes on the rewrite — at any depth. Nothing in the document describes its own construction.

**No introduction.** Open on the first real claim. No framing sentence, no statement of what follows, no naming of the register or its depth. The rules are implied by the context; announcing them spends the lines they were meant to save.

**Terse, succinct, pithy, compendious.** Materially shorter than the source *and* complete. Density that doesn't shrink the page is the same document in harder words. The lever is words-per-claim, never claims-per-document — step 1 is what stops "shorter" becoming "less". Cut throat-clearing, cut any sentence restating its neighbour at higher compaction, cut every phrase announcing what the next passage does. A block earns its place by carrying a claim no other block carries. Calibration: P1 near source length, P2 well under, P3 under that. Longer than what it replaced is a failed pass, however well it reads.

Three scaffolds are gone — the grid that exposed missing cells, the term block that caught a cold reader, the trailer that itemized additions. Their jobs remain. Steps 1, 3 and 5 absorb them.

## The pass

Order matters: compressing before inventorying is how content disappears.

**1. Inventory.** List every load-bearing claim before writing a word. Compression feels like editing and behaves like deletion; an item never logged is one you won't notice missing. Check the finished draft against the list. Comparative content — options against criteria, tiers against properties — gets gridded on scratch first so you notice the empty cell, then written as prose. The grid is a drafting instrument and never ships.

**2. Split spine from body.** Spine does the argumentative work — why this matters, why the alternative fails, what the reader must decide — and keeps full sentences, because a telegraphed argument is unverifiable and an unverifiable argument persuades nobody. Body is enumerable — taxonomies, task lists, tiers, options, criteria — and telegraphs freely into fragments, arrows, middot-runs, slash-pairs. Most drafts arrive body-overwritten and spine-underwritten: shorten the body, sharpen the spine.

**3. Coin.** A coinage earns its place by recurrence (3+ uses), downstream-label use (it becomes a field name, ticket label, dashboard axis), or disambiguation — naming two things separately to make a conflation visible, which *is* the argument rather than shorthand for it. Clearing none of the three, it's a tax with no return; cut it.

No term block downstream, so each coinage survives alone. Decode on sight — `installer-swap`, `change-freeze`, `time-to-mitigate` — or gloss inline as content: "time-to-mitigate (TTM) is the number that moves." Never leave a bare acronym to be reconstructed. Relabelling an identifier the source already used strands anyone holding the old reference and no mapping line catches them, so keep the original or pick one whose relation to it is obvious on sight; when neither works, don't relabel. Never collide two coinages on the same letters. Existing team shorthand stays, in quotes on first use.

**4. Compact.** Apply the register inventory below. Content that would have been a table takes one of three shapes: a flat list becomes a middot-run behind a run-in head; two-to-four contrasted items become bullets with the distinguishing property stated per bullet; several things across several dimensions stay prose, organized on whichever axis carries the argument, with non-discriminating dimensions dropped rather than dutifully covered. Prose beats a grid on exactly one count — a cell demands filling, which invites padding and fabrication, while prose says only what discriminates.

**5. Carry the honesty inline.** No trailer, so both obligations move into the body.

*Additions: don't make them.* Everything written reads as the source author's assertion, permanently, with nothing below to disown it. Everything in the output traces to the source — no invented specifics, no status tag without a real value behind it, no resolving an ambiguity the source left open. Where an addition is genuinely load-bearing it must stand as content in the author's voice and be true; if it can't, it doesn't go in.

*Caveats: weave them.* Hedges, limits, unknowns and open calls ride inside the sentence carrying the claim they qualify, unlabelled — no "caveat", no "note that", no "as in the original". State the limit as fact: "my knowledge runs to May 2026, so anything past 1.3 may have moved." In flow, a hedge reads as the author's own care, which is what it always was.

Close by returning decision rights. That handoff is content, not commentary — it stays.

## Register inventory

| Move | Form | Plain → register |
|---|---|---|
| Run-in head | `**Short label.** Sentence…` | carries the structure a heading would, without breaking the prose run |
| Middot-run | `A · B · C` | flat enumeration inline — replaces a one-column list or a bulleted set of bare items |
| Hyphen-compound premodifier | `X-Yed`, `X-Ying` | "a flag enabled by default" → "enabled-by-default flag" |
| Suffix families | `-shaped`, `-bearing`, `-guarded`, `-native`, `-blind`, `-dominant` | "roughly fits the spec" → "spec-shaped"; "treats every locale the same" → "locale-blind" |
| Slash-pair | `A/B`, `A-yes/B-no` | "passes staging but fails prod" → "staging-yes/prod-no" |
| Arrow for consequence | `→` | "which means we can roll back per tenant" → "→ per-tenant rollback" |
| Parenthetical status tag | `(clean)`, `(no-op)`, `(pending)` | appends verification state to a claim |
| Noun-stack | compound abstract nouns | "the gap between what we monitor and what we alert on" → "monitoring-alerting gap" |
| Clipped copula | drop articles and auxiliaries | "The quote is an estimate, not a guarantee." → "Quote is estimate, not guarantee." |
| First-person verification | "I smoke-verified X (clean)" | own your own checks explicitly |
| Em-dash decision handoff | "— that call is yours" | close by returning decision rights |

The handoff is a feature, not a flourish: the register's signature move is separating what the writer has settled from what the reader must decide. Preserve it even when compressing hard.

## What not to compress

- **Anything you'd have to invent to fill.** Status tags are the trap — `(clean)`, `(scoped)`, `(unauthored)` suit the register beautifully and invite fabrication. Tag only what you hold real values for; where the values exist somewhere you can't see, leave the slot and flag it.
- **Empty sections.** Don't silently fill, don't silently drop. Frame the emptiness deliberately or ask what belongs there.
- **Hedges carrying legal, safety or attribution weight.** "Plausibly", "we don't yet know", "not mine to settle" are load-bearing. Compressing a hedge into a claim is the most expensive mistake available here, precisely because the output sounds confident.
- **Technical abstraction level.** Never add specifics the source lacked. Density is a prose operation, not a research one — source names categories, output names categories.

## Failure modes

- **Density without shrinkage.** Every sentence tightened, but heads, blocks and explanatory asides added, netting out longer. Count against the source before delivering; if it grew, cut structure and elaboration, never claims.
- **Preamble.** A framing sentence before the first claim, or a line naming what the document is about to do. Both are pure cost — delete and start at the claim.
- **Pass-commentary.** Notes about what you did to the text are not part of the text: no change summary, no tradeoff paragraph, no additions log, no revert offer. If something about the rewrite truly needs saying it goes in the chat around the document, and usually it doesn't.
- **Opacity mistaken for density.** Test: could a smart, adjacent, non-team reader follow this start to finish with nothing but the document? There's no glossary to fall back on, so every coinage must have paid for itself where it first appeared. If the reader stops to reconstruct, you compressed the spine.
- **Register drift into parody.** Every compound should replace words. A compound replacing nothing is costume.
- **Silent authorship.** The trailer used to absorb this; now the only defence is adding nothing you can't stand behind in the author's voice.
- **Losing the persuasion target.** Ask which passages exist to convince someone who doesn't already agree — skeptical reviewers, external readers, sign-off authorities. They have the least tolerance for shared-context assumptions and are the first thing coinage-density loses.

## Depth control

Offer a level rather than guessing.

- **P1** — house voice, structure intact, no coinage. Survives cold reading. For sign-off, external circulation, anything that must persuade a reader who doesn't already agree.
- **P2** — coinage glossed in flow, telegraphed body, run-in heads and middot-runs. Standard house output.
- **P3** — connective compression on the spine. Narrow; see below.

No depth produces a table. The prohibition is register-wide and the reason isn't formatting: a table is *set-shaped* where an argument is *sequence-shaped*, so tabularizing a chain of reasoning destroys the order that made it checkable — a category error dressed as compression. A grid is terminal too, admitting no further compression, which makes it a dead end exactly where the spine still has give.

### What P3 actually is

By P3 the body is already telegraphed to fragments and middot-runs, leaving only the spine — which is sequential and causal. P3 is therefore **connective compression**: delete the words carrying a logical relation while preserving the relation.

| Move | Replaces | P2 → P3 |
|---|---|---|
| Semicolon-chained clauses | "and also", "meanwhile", "it then" | "The job builds the cache. It then swaps the pointer." → "Job builds cache; swaps pointer." |
| Em-dash apposition | "which is", "that are" | "the fallback path, which is load-bearing" → "the fallback path — load-bearing" |
| Colon-as-expansion | "the reason is that" | "The reason is that X" → "Reason: X" |
| Collapsed conditional | if/then | "If it passes on staging but fails in prod, config drift is the cause" → "Staging pass, prod fail: config drift." |
| Negation-pair | definition + warning in four words | "an estimate rather than a guarantee" → "estimate, not guarantee" |
| Agent deletion | inferable subject | "We can't ship a fix we can't distinguish from a regression" → "No shipping a regression-indistinguishable fix" |
| Meta-sentence deletion | scaffolding | cut any sentence announcing what the next sentence will do |

### The P3 constraint

P3's failure mode differs in kind from P2's and is worse. P2 fails by opacity: the reader doesn't know a coinage, asks, gets told — recoverable. P3 fails by **relational ambiguity**. A semicolon or em-dash marks that a relation exists without specifying which; "X; Y" reads as *therefore*, *whereas* or *namely* depending on the reader. Someone reconstructing "therefore" where you meant "whereas" has misread the argument with no signal they did, and nothing in the document repairs it. A confused reader asks; a confidently-misreading reader signs off on the wrong thing.

So P3 is selectively denser, not uniformly. **Compress a connective only where the relation is recoverable from content alone.** Ranked by safety: arrows (`→`) specify direction, safest; colons specify expansion; em-dashes specify apposition loosely; semicolons specify nothing, riskiest. Where two readings are both plausible, spend the word.

Two carve-outs bind hardest here, where pressure to cut is highest and cost worst. Hedges stay — "plausibly", "we don't yet know", "not mine to settle" look like scaffolding at this density and aren't. Attribution stays — who verified what, who owns the open call.

**Who P3 is for:** readers who wrote adjacent parts of the document, or a second read. Not sign-off, not external, not persuasion. Narrower than P2 rather than better — offer it as a different tool, not an upgrade.

Default to P2. If an output still isn't dense enough, the remaining fat is in the spine — say so rather than compressing it silently, because spine shouldn't shrink without a decision.
