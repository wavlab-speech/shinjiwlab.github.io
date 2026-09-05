# Publication gap detection from Shinji's website

**Status:** the checker and the weekly notifier are implemented. The local
review tool (`--review`) is designed but not built.
**Date:** 2026-09-04

## Problem

`_bibliography/papers.bib` is maintained by hand. Nobody reliably notices when a
lab paper is accepted, so the publications page drifts behind reality. Measured
drift as of 2026-09-04, measured with a `year >= 2025` cutoff: papers on
Shinji's public publication list are absent from `papers.bib`, including
EMNLP'26, COLM'26 and Interspeech'26 acceptances and five journal papers in
press. (With a `>= 2022` cutoff the figure was 43 candidates — 49 raw minus 6
caught as duplicates at J >= 0.85 — but that pulled in pre-2025 backlog, so the
cutoff was tightened to 2025 and the backlog left to a manual backfill.)

The inefficiency is *noticing* new papers, not typing BibTeX. This design
addresses only the noticing.

## Non-goals

These were considered and rejected on measured evidence:

- **Replacing `papers.bib` with a scrape.** Shinji's page has no links at all
  (58 anchors on the page, all navigation), no topic labels, and no `selected`
  flag. A replacement would destroy 57 link fields, all 435 `abbr` badges, and
  the 11 front-page selections.
- **Taking titles from Shinji's page as authoritative.** Of 107 differing title
  pairs, `papers.bib` is better in 71 and the website in 0. The website carries
  13% ALL-CAPS titles (copied from camera-ready PDFs) versus 4% in `papers.bib`,
  plus mechanical title-casing that capitalises function words (`Approach And
  Results`, `Online Register For`, `Full-Duplex-Bench V1.5`). Confirmed that
  jekyll-scholar's `apa` style preserves case verbatim, so these would be
  visible defects.
- **DBLP enrichment.** Measured 4/12 hit rate against genuinely-new papers,
  with repeated 503/HTTPError responses, and no unique contribution over
  OpenAlex. Dropped.
- **The bot editing `papers.bib`.** See "Safety model".

## Verified findings

Everything below was measured against the live page and the current `papers.bib`.

| Question | Result |
|---|---|
| Plain `curl` fetch | HTTP 200, 599 KB, server-rendered — no browser/JS needed |
| `robots.txt` | `/view/` not disallowed (only `/feeds`, `/*/_/`) |
| Class-independent selector | `p[role=presentation][dir=ltr]` + `h1..h4` → all 687 entries |
| Title/author/venue extraction | 683/687 (99.4%) via a double-quote regex |
| Currency of the source | 100% of `papers.bib` 2025 (60/60) and 2026 (22/22) entries present |
| Entries with no year | 231/687, of which 217 say "accepted" |
| Distinct raw venue strings | 109 on the site vs 34 `abbr_publisher` values; 69 appear once |
| Exact-match false-positive rate | 12% (6 of 49), caused by defects in `papers.bib` |
| Fuzzy threshold reliability | Not automatable — Branchformer (`papers.bib:2460`) scores only 0.67 |
| OpenAlex enrichment | 9/12 (75%) — DOI, year, canonical venue, landing page |
| arXiv enrichment | 8/12 (67%) — bare arXiv ID, exactly the field format required |

Enrichment misses are concentrated in just-accepted, not-yet-published papers.
Nothing indexes those; they are expected to need manual completion.

## Safety model

The bot **never writes to `papers.bib`**. It writes two new files. Confirmed that
`_config.yml:154` sets `bibliography: papers.bib` and `_pages/publications.md:25`
renders with `-f papers`, so a second `.bib` in `_bibliography/` is not rendered
by Jekyll. `incoming.bib` therefore sits next to `papers.bib` for easy
copy-paste while being inert on the site.

Consequence: a parse regression cannot damage curated `abbr`, `arxiv`, `code`,
`pdf`, `html` or `selected` data. The worst case is a noisy PR, which a
maintainer closes.

## Data flow

```
Shinji's site ──fetch──> section filter ──> year filter ──> candidates
                         (Journal +          (>=2022 or
                          Conference)         undated)
                                                  |
papers.bib ──parse──> existing titles             |
                                                  v
                                      three-tier title match
                    ┌─────────────┬───────────────┬──────────────┐
                  exact        J >= 0.85      0.60 <= J < 0.85   J < 0.60
                  skip          skip          flag as suspect     new
                                                  └────────┬───────┘
                                                    enrich (OpenAlex, arXiv)
                                                           |
                                                  render draft stubs
                                                           |
                                    _bibliography/incoming.bib
                                    docs/publication-title-review.md
                                                           |
                                                    PR against `source`
```

## Component design

### Scraper

- `p[role=presentation][dir=ltr]` plus `h1..h4` in document order, tracking the
  current section heading. Deliberately avoids Google's generated class names
  (`zfr3Q`), which are not contractual.
- Text extraction joins spans with **no separator** — Google Sites splits text
  mid-word, and a space separator corrupts tokens (`Interspeech'2 5`, `(202 3 )`).
- Section filter keeps only `Journal (refereed)` and
  `International Conference and Workshop (refereed)`. This drops 223 pre-CMU
  career papers and 65 keynotes/tutorials/books.
- Year filter keeps `year >= 2025` or no year at all (undated means "accepted",
  i.e. current). Years outside 1990–2030 are discarded as noise; the source
  contains `2070` and `2098`. The cutoff is deliberately recent: this automation
  exists to catch *new* papers, and a lower cutoff drags pre-2025 backlog into
  the first run. Older gaps are a separate manual backfill.
- **Hard failure if the scrape yields zero entries** or fewer than 500 blocks.
  A layout change must break loudly, never emit an empty PR.

### Matcher

Title normalisation for comparison only: NFKD, lowercase, strip all
non-alphanumerics. Similarity is Jaccard over token sets with English stopwords
removed.

| Band | Action |
|---|---|
| exact normalised match | skip silently |
| J >= 0.85 | skip silently |
| 0.60 <= J < 0.85 | emit stub, annotated with the suspected duplicate |
| J < 0.60 | emit stub as new |

The middle band exists because the threshold is provably not automatable: the
Branchformer paper is present in `papers.bib` but scores 0.67, while genuinely
distinct papers score as high as 0.5. The band is surfaced for a human, not
resolved by the script.

### Year resolution

The page lists accepted papers without a year, but their venue abbreviations
carry one: `Proc. Interspeech'26 (accepted)`. A regex over the venue string
recovers a year for 226 of the 231 undated entries (98%). The rest are journal
papers marked "accepted" with no year stated anywhere; those render
`year={TODO}`.

This replaced an external-API lookup — see "Enrichment: proposed, built, then
removed" below. The script makes exactly one HTTP request: the page itself.

### Venue mapper

Maps the venue text on the page to the `@string` macros in `papers.bib` and to
`abbr_publisher` labels, via an ordered list of regexes. The page has 109
distinct venue strings against our 34 labels, so this was expected to need an
external source of canonical names — but the long tail turns out to be old
pre-CMU venues that the section and year filters exclude anyway. Measured on the
current candidate set it resolves **36/36** with no `TODO`. Unmapped venues emit
`abbr_publisher={TODO}` plus the raw string as a comment.

### Stub renderer

Follows the conventions verified in `papers.bib`: `booktitle=ICASSP` as a bare
macro for `@inproceedings`, `journal={...}` as a braced literal for `@article`,
`arxiv={2105.01051}` as a bare ID.

```bibtex
% source: Shinji's site, "Journal (refereed)"
% enrichment: OpenAlex (venue, year, doi)
@article{TODO_bando_taslp2026,
  abbr={TODO},
  abbr_publisher={TASLP},
  title={Online Frontend System for Multi-Talker DSR Using Neural Blind Source Separation and Diarization},
  author={Yoshiaki Bando and Tomohiko Nakamura and Satoru Fukayama and Shinji Watanabe},
  journal={IEEE/ACM Transactions on Audio, Speech, and Language Processing},
  year={2026},
  doi={10.1109/taslpro.2026.3711759},
  html={https://doi.org/10.1109/taslpro.2026.3711759},
  % arxiv: not found
}
```

`abbr` is always `TODO`. Topic labels are curation and are never guessed.
Citation keys are always `TODO_`-prefixed so an unedited stub cannot be merged
by accident.

### Title review report

`docs/publication-title-review.md` lists pairs that matched but whose titles
differ, annotated with which side looks defective. Heuristics, both validated
above: proportion of uppercase letters, and capitalised function words. The
report is read-only and changes nothing.

Its first run should surface the five known `papers.bib` defects
(`papers.bib:1774` `lA Comparative Study`; `yenju_interspeech2022` doubled
`and`; and the comma-to-`and` corruption in `motoi_icassp2023`,
`yifan_slt2022`, `yoshiki_slt2022`) plus 17 ALL-CAPS titles. Fixing those is a
separate manual cleanup, not part of this automation.

## Phasing

**Phase 1 — local only.** `scripts/check_publications.py`, run by hand. Output
reviewed for quality before any automation exists. No workflow file.

**Phase 2 — automation.** `.github/workflows/check-publications.yml`, mirroring
`update-conferences.yml`: weekly cron (Monday 07:00 UTC, an hour after the
conferences bot) plus `workflow_dispatch`, opens a PR against `source`, never
touches a deploy branch, creates no PR when there is nothing to add. Adds a
`concurrency` group so runs cannot overlap, and a 30-minute `timeout-minutes`.

Two things the workflow does that the conferences bot does not:

- **Runs `--selftest` against the checked-in fixture before any network call**,
  so scraper and matcher regressions fail offline rather than after six minutes
  of API traffic.
- **Reports its own run statistics in the PR body** via `--stats-file`, so a
  reviewer can see how many candidates were found, how many were flagged as
  possible duplicates, and how many resolved a `year`, without opening the diff.

### Enrichment: proposed, built, then removed

Enrichment was in the approved design and was fully implemented against
OpenAlex and arXiv. It was then **deleted**, because the field it populated is
one this repository does not use:

| Field | Entries in `papers.bib` (of 436) |
|---|---|
| `arxiv` | 21 (4.8%) |
| `html` | 16 (3.7%) |
| `code` | 12 (2.8%) |
| `pdf` | 8 (1.8%) |
| any link at all | 33 (7.6%) |
| any link, 2025-26 entries | **0 of 82** |

So 106 lines of API code, a circuit breaker, a wall-clock budget and
degraded-run reporting existed to fill a field that had not been used once in
two years. That is the whole justification for removing it.

Getting the retry policy right had already taken three attempts, which is
itself evidence the leg was not worth its weight: too impatient (gave up after
~7 s, silently produced stubs with a third of their metadata), then too patient
(a ~63 s ladder turned a 6-minute job into an **18-minute** one that still
resolved 0/36), then patience split by stakes (critical page fetch retries hard,
best-effort lookups fail fast).

**What replaced the one part that mattered.** OpenAlex also supplied `year`,
which jekyll-scholar needs for grouping. Venue abbreviations on the page carry
it already — `Proc. Interspeech'26 (accepted)` — so a one-line regex recovers a
year for **226 of the 231** undated entries (98%). The five it cannot are
journal papers marked "accepted" with no year stated anywhere, which honestly
have no year yet.

Measured outcome of the removal:

| | With enrichment | Without |
|---|---|---|
| runtime | 6-18 min | **2.5 s** |
| external APIs | 2 | **0** |
| stubs with a `year` | 24/36 (best run), 3/36 (rate-limited) | **31/36** |
| failure modes | scrape failure, rate limiting, degraded output | scrape failure |
| script length | 817 lines | 664 lines |

The simpler version is also strictly better at the field that mattered, because
a regex over the source page cannot be rate-limited.

## Testing

No test suite exists in this repo, so verification is explicit:

- Scraper: against a checked-in HTML fixture, assert >= 600 blocks and >= 600
  extracted titles *before* the section and year filters are applied (the
  current page yields 687 and 683), so a Google Sites layout change is caught
  offline.
- Matcher: assert the six known false positives are suppressed and that
  Branchformer lands in the suspect band.
- Enricher: assert exact-title-match guard rejects a near-miss result.
- End to end: run against the live page, then `bundle exec jekyll build` to
  confirm `incoming.bib` does not alter the rendered site.

## Phase 1 verification results (2026-09-04)

`scripts/check_publications.py` implemented and run against the live page.

| Check | Result |
|---|---|
| `--selftest` against the checked-in fixture | 7/7 assertions pass |
| Scrape | 683 titles from 687 blocks |
| Candidates after section + `year >= 2025` filter | 38, of which 2 suppressed at J >= 0.85 |
| Stubs emitted | 36, one flagged as a possible duplicate |
| Venue resolved to a real `abbr_publisher` | 36/36 (no `TODO` venues) |
| `year` resolved (site year, else inferred from venue) | 31/36 |
| `year={TODO}` (no year stated anywhere) | 5/36, all journal "accepted" |
| Runtime, live | 2.5 s |
| Title report precision | flags exactly the 5 known `papers.bib` defects, 0 false alarms out of 112 pairs |
| `incoming.bib` rendered by Jekyll? | No — 0 occurrences of its titles in `_site/publications/index.html` |
| Completed stub pasted into `papers.bib` | builds clean; `abbr` and `abbr_publisher` badges render; `journal=TASLP` macro expands |

Two defects were found and fixed during verification:

- The title report originally paired only on the aggressive key, which by
  construction cannot see the comma-to-`and` corruption (`and` is a word, not
  punctuation, so it survives normalisation). The report now also pairs on the
  fuzzy band.
- Stubs originally carried `%` comments *inside* the entry braces. BibTeX has no
  comment character — `%` is LaTeX — so a pasted stub could break the build. All
  generated comments now sit outside the entry.

Unrelated pre-existing issue noticed: `bundle exec jekyll build` fails with
`invalid byte sequence in US-ASCII` unless `LANG`/`LC_ALL` are set to a UTF-8
locale. Not caused by this work, but worth knowing.

## Shape change: the intermediate file is gone (2026-09-05)

The first design wrote draft stubs to `_bibliography/incoming.bib`, opened a PR
with that file, and left a maintainer to move each entry into `papers.bib` by
hand. That file is now gone, and so is the PR.

The local tool runs the scrape itself -- the scraping code is in the same
script -- so the intermediate file bought nothing and could disagree with a
local run. The weekly job's only job is now to say that there is work to do.

Two consequences, one good and one not:

- **Good.** There is one fewer file to keep in step, and no bot branch to go
  stale.
- **Not good.** The bot PR was the one place a second person saw an entry
  before it went live. To keep that reader, the weekly issue carries the draft
  BibTeX for each missing paper, so it can be read on a phone. That is a
  partial replacement, not an equal one: the real review is now the `git diff`
  the person who ran the tool reads before they push.

### What the weekly job does now

It runs `scripts/check_publications.py --report`, which exits 1 when papers are
missing and 0 when none are. On 1 it creates or updates ONE issue titled
"Publications missing from papers.bib". On 0 it closes that issue.

One long-lived issue, rewritten in place, gives the reject list for free: a week
whose candidate set has not changed produces an identical body and therefore no
notification. A genuinely new paper changes the body and notifies. A committed
list of rejected papers would cost code and a file convention to do the same.

### Two defects found and fixed before this shipped

- **`scrape()` read the year from the whole citation, including the title.**
  Three entries carry a year in the title -- "2025 URGENT Speech Enhancement
  Challenge ... Proc. ICASSP'26" -- so the stub stated 2025 for a 2026 paper.
  The year now comes from the venue text only. A self-test assertion holds it.
  The 37 papers merged in #286 were checked: none took a wrong year, because
  all three affected papers were already in `papers.bib`.
- **The `abbr` vocabulary was a hard-coded list of 16 values.** `papers.bib`
  already used 39. The list is now read from `papers.bib` at run time, ordered
  by use, and a self-test assertion holds that too.

## Known limitations, to be restated in every PR body

- Scraping depends on Google Sites' HTML structure. Mitigated by the
  class-independent selector and the loud-failure guard, not eliminated.
- Link fields (`arxiv`, `doi`, `html`) are never filled in — by design, see
  "Enrichment" above. A maintainer who wants them adds them by hand, as has
  always been the case here.
- The suspect band requires human judgement by construction.
- The source page contains its own data noise (impossible years, ALL-CAPS
  titles, a stray `Member,` inside one author list).
