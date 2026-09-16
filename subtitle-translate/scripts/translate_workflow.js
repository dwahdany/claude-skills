export const meta = {
  name: 'translate-subtitles',
  description: 'Translate a subtitle SRT in batches with subagents: style guide, per-batch translation, per-batch editorial review',
  phases: [
    { title: 'Style guide', detail: 'one agent reads the whole file and fixes names, terms, forms of address' },
    { title: 'Translate', detail: 'one agent per batch' },
    { title: 'Review', detail: 'one editor per batch, writes the final batch file' },
  ],
}

// args: { dir, srcSrt, batches, src, dst, notes?, maxChars? }
//   dir      absolute work dir; batch files live in dir/batches/NN.json (from make_batches.py)
//   srcSrt   absolute path of the source SRT (read once for the style guide)
//   batches  number of batch files
//   src/dst  language names, e.g. 'English' / 'Russian'
//   notes    free text about the show (original language of names, genre, anything translators must know)
//   maxChars soft per-cue length limit for the target language (default 70)
for (const k of ['dir', 'srcSrt', 'batches', 'src', 'dst']) if (!args || args[k] === undefined) throw new Error(`args.${k} required`)
const { dir: DIR, srcSrt, batches: N_BATCHES, src: SRC, dst: DST } = args
const NOTES = args.notes || ''
const MAX = args.maxChars || 70
const pad = n => String(n).padStart(2, '0')

const GLOSSARY = {
  type: 'object',
  properties: {
    names: { type: 'array', items: { type: 'object', properties: { source: { type: 'string' }, target: { type: 'string' } }, required: ['source', 'target'] } },
    terms: { type: 'array', items: { type: 'object', properties: { source: { type: 'string' }, target: { type: 'string' } }, required: ['source', 'target'] } },
    address: { type: 'array', items: { type: 'object', properties: { who: { type: 'string' }, whom: { type: 'string' }, form: { type: 'string' }, why: { type: 'string' } }, required: ['who', 'whom', 'form'] } },
    tone: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['names', 'terms', 'address', 'tone', 'notes'],
}
const TRANSLATIONS = {
  type: 'object',
  properties: { translations: { type: 'array', items: { type: 'object', properties: { i: { type: 'integer' }, text: { type: 'string' } }, required: ['i', 'text'] } } },
  required: ['translations'],
}
const REVIEW = {
  type: 'object',
  properties: { count: { type: 'integer' }, changed: { type: 'integer' }, issues: { type: 'array', items: { type: 'string' } } },
  required: ['count', 'changed', 'issues'],
}

phase('Style guide')
const glossary = await agent(`Read ${srcSrt} — the ${SRC} subtitles of one episode/film. Build a style guide for translating it into ${DST} subtitles, so that ${N_BATCHES} translators working on separate parts stay consistent.
${NOTES ? `\nAbout this title: ${NOTES}\n` : ''}
Produce:
- names: every person, place, organisation and product name that appears, each with ONE fixed ${DST} rendering (standard transliteration rules for the names' original language; nicknames and titles consistent).
- terms: recurring terms, titles, ranks, jargon and catchphrases, each with one fixed ${DST} rendering.
- address: who addresses whom formally vs informally (if ${DST} distinguishes, e.g. ты/вы, du/Sie, tu/vous), derived from relationships and register.
- tone: overall tone and register (genre, formality, humour, profanity level, how to render it in ${DST}).
- notes: anything else translators must know (running jokes, wordplay, on-screen text, song lyrics handling, recurring formulas).

Be complete but compact — the guide is pasted into every translator's prompt.`, { label: 'style-guide', phase: 'Style guide', schema: GLOSSARY })
if (!glossary) throw new Error('style guide agent failed')
const guide = JSON.stringify(glossary)
log(`style guide: ${glossary.names.length} names, ${glossary.terms.length} terms, ${glossary.address.length} address rules`)

const RULES = `Rules:
- Natural, idiomatic ${DST} as a native subtitler would write it; keep the register (slang, formality, rudeness) of the source.
- Be concise: subtitles are read fast. Prefer the shortest natural phrasing that keeps meaning and tone; drop filler. A cue should rarely exceed ${MAX} characters.
- Keep speaker-change dashes ("- ") exactly where the source has them; keep ♪ markers; keep bracketed sound cues like [music] but translate the word inside.
- Translate every item completely into ${DST}; never leave ${SRC} words except names the style guide says to keep untransliterated.
- Follow the style guide exactly for names, terms and forms of address.
- No notes, no commentary, no extra entries.`

const results = await pipeline(
  Array.from({ length: N_BATCHES }, (_, n) => n),
  n => agent(`You are a professional ${SRC}→${DST} subtitle translator working on one episode.

Read the JSON file ${DIR}/batches/${pad(n)}.json. It has "items" (each with "i" = cue index and "en" = ${SRC} cue text; internal line breaks were flattened to spaces, and a leading "- " marks a speaker change inside the cue) and "context" (the last ${SRC} lines of the previous batch — for continuity only, do not translate them).

Style guide for this title:
${guide}

${RULES}

Output:
1. Write ${DIR}/batches/${pad(n)}.draft.json containing {"translations": [{"i": <index>, "text": "<${DST} text>"}, ...]} — exactly one entry per item, same order, same "i" values.
2. Return the same data via the structured output tool.`, { label: `translate:${pad(n)}`, phase: 'Translate', schema: TRANSLATIONS }),

  (draft, n) => agent(`You are a senior ${DST} subtitle editor reviewing one batch of a translated episode.

${SRC} source: read ${DIR}/batches/${pad(n)}.json (fields "items" with "i" and "en"; "context" is the tail of the previous batch, for continuity only).

${DST} draft:
${draft ? JSON.stringify(draft) : 'NO DRAFT AVAILABLE — translate every item yourself, following the rules below.'}

Style guide for this title:
${guide}

${RULES}

Check every cue against the ${SRC} and fix what is wrong: mistranslations, lost or added meaning, wrong tone or register, unnatural ${DST}, inconsistency with the style guide, missing or misplaced speaker-change dashes, lost ♪ or bracketed cues, ${SRC} left untranslated, and wordy cues that can be shortened without losing meaning (aim for ≤ ${MAX} characters where the source allows). Exactly one translation per item, same "i" values, same order.

Write the corrected batch to ${DIR}/batches/${pad(n)}.reviewed.json as {"translations": [{"i": <index>, "text": "<${DST} text>"}, ...]}. Then return via the structured output tool: count (translations written), changed (how many you modified), issues (short notes on anything unresolved, e.g. ambiguous speaker; may be empty).`, { label: `review:${pad(n)}`, phase: 'Review', schema: REVIEW })
    .then(r => ({ batch: n, drafted: draft ? draft.translations.length : 0, reviewed: r ? r.count : 0, changed: r ? r.changed : null, issues: r ? r.issues : ['review agent failed'] }))
)

const summary = results.filter(Boolean)
log(`${summary.length}/${N_BATCHES} batches finished`)
return { glossary: { names: glossary.names.length, terms: glossary.terms.length, address: glossary.address.length }, batches: summary }
