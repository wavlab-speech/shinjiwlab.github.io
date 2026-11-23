# Member Publications from papers.bib and ORCID Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the blocked Google Scholar fetch with a weekly fetch that builds each member's publication list from `_bibliography/papers.bib` and the member's public ORCID record.

**Architecture:** One dependency-free Python script, `bin/fetch_publications.py`, replaces `bin/fetch_scholar.py`. It reuses the old script's BibTeX parser, title index, enrichment, de-duplication and sorting, adds a papers.bib author matcher and an anonymous ORCID client, and writes `_data/member_pubs/<id>.yml`. The member card reads the new directory. Verification follows the repo's existing pattern: a `--selftest` flag with a checked-in fixture, run before any network call.

**Tech Stack:** Python 3.11 standard library + `pyyaml`; Jekyll/Liquid; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-23-orcid-member-publications-design.md`

## Global Constraints

- Work in the worktree `/private/tmp/claude-501/-Users-cyhuang-shinjiwlab-github-io/50942266-8303-40a5-b0b4-373bf6fb977b/scratchpad/wt-orcid`, branch `feat/orcid-publications`. Never commit `_site/`.
- Dependencies: Python standard library and `pyyaml` only. No `requests`, `scholarly` or `bibtexparser`.
- Never send a request to `scholar.google.com`.
- ORCID: anonymous public API, `https://pub.orcid.org/v3.0/<orcid>/works`, header `Accept: application/json`, no credentials.
- `User-Agent: wavlab-site-publications/1.0 (+https://github.com/wavlab-speech/shinjiwlab.github.io)`. Put no email address anywhere in the script, the fixture or the workflow.
- `KEEP_LATEST = 25`. The card shows 20.
- `MIN_KEEP_RATIO = 0.7`, applied only when the stored `source` equals the new `source`.
- Output: `_data/member_pubs/<id>.yml`, keys in this order: `source`, `total`, `pubs`. `source` is exactly `papers.bib+orcid` or `papers.bib`. Each pub has `title`, `year` (string), `venue`, `url`.
- Write YAML with `yaml.safe_dump(..., default_flow_style=False, allow_unicode=True, sort_keys=False)`.
- The script exits non-zero only when it attempted at least one ORCID request and every one failed.
- Commit messages: ASD-STE100 style (short sentences, active voice). End each with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. A member name with a parenthetical nickname, `Ting (Justin) Jiang`, must match `Ting Jiang` in papers.bib and must not raise. Test: Task 1.
2. An `orcid` value written as a URL, in lower case `x`, or with spaces must be normalized; an invalid value must leave the member's file unchanged and print a log line, and must never reach the API. Tests: Task 3 (`normalize_orcid`) and Task 4 (`refresh_member` returns `invalid_orcid`).
3. An ORCID record that returns zero works (made private, or emptied) must not wipe a list: with the same `source`, a drop below 70% is refused. Test: Task 4.
4. An ORCID HTTP 429/503, a timeout or bad JSON must leave that member's file unchanged, and the other members must still refresh. Test: Task 4.
5. The same paper listed twice in ORCID (the arXiv preprint and the published version, in separate groups, same title) must appear once, with the newest year. Test: Task 3 fixture holds such a pair; Task 4 merge test.

---

### Task 1: New script skeleton with the papers.bib author matcher

**Files:**
- Create: `bin/fetch_publications.py`

**Interfaces:**
- Consumes: from `bin/fetch_scholar.py`, copy these unchanged: `load_members`, `clean_latex`, `normalize_title`, `_match_brace`, `_parse_fields`, `parse_bib`, `_as_url`, `bib_link`, `BibIndex`, `enrich`, `dedupe`, `sort_newest_first`, `ARXIV_IN_VENUE`, `arxiv_link_from_venue`, and the constants `ELLIPSIS`, `MIN_PREFIX_MATCH`.
- Produces:
  - Constants: `REPO_ROOT`, `MEMBERS_FILE`, `PAPERS_BIB`, `PUBS_DIR = os.path.join(REPO_ROOT, '_data', 'member_pubs')` (a module global, so the self-test can point it at a temp dir), `TESTDATA_DIR = os.path.join(REPO_ROOT, 'bin', 'testdata')`, `KEEP_LATEST = 25`, `MIN_KEEP_RATIO = 0.7`.
  - `bib_row(fields: dict) -> dict` → `{'title', 'venue', 'year', 'url'}`, the body of the old `build_bib_index` loop (venue = `abbr_publisher` or `booktitle` or `journal`, all through `clean_latex`; url = `bib_link(fields)`).
  - `build_bib_index(entries: list[dict]) -> BibIndex` — takes parsed entries (not a path), keys by `normalize_title`, first entry wins.
  - `split_authors(field: str) -> list[str]` — split a BibTeX author field on ` and ` (whitespace-insensitive), strip each name.
  - `name_key(name: str) -> str` — `clean_latex`; drop any parenthetical `( ... )`; if the name holds exactly one comma, reorder `Last, First` to `First Last`; fold accents (NFKD, drop combining marks); lower case; drop every non-letter. `"Watanabe, Shinji"` → `"shinjiwatanabe"`.
  - `member_name_keys(member: dict) -> set[str]` — `name_key` of `member['name']` plus each entry of the optional `member['bib_names']`.
  - `bib_rows_for_member(entries: list[dict], keys: set[str]) -> list[dict]` — `bib_row(e)` for every entry with a title where any `name_key(a)` for `a in split_authors(e.get('author', ''))` is in `keys`.
  - `check(label: str, ok: bool) -> None` — record one self-test result and print `PASS`/`FAIL label`.
  - `selftest() -> int` — run every check, print `N/N self-test checks pass`, return 0 if all pass, else 1.
  - `main(argv: list[str]) -> int` — for now only `--selftest`; `if __name__ == '__main__': sys.exit(main(sys.argv[1:]))`.

- [ ] **Step 1: Write the failing checks in `selftest()`**

```python
check('name forms match', name_key('Watanabe, Shinji') == name_key('Shinji Watanabe'))
check('case and hyphen variants match', name_key('Chien-Yu Huang') == name_key('Chien-yu Huang'))
check('nickname in parentheses is ignored', name_key('Ting (Justin) Jiang') == name_key('Ting Jiang'))
check('different person, similar name', name_key('Ching-Feng Liu') != name_key('Chin-Jou Li'))
check('split on and', split_authors('A B and  Watanabe, Shinji\nand C D') == ['A B', 'Watanabe, Shinji', 'C D'])
entries = [
    {'title': 'P1', 'author': 'Chin-Jou Li and Shinji Watanabe', 'year': '2025'},
    {'title': 'P2', 'author': 'Ching-Feng Liu and Xiaoyu Li', 'year': '2025'},
    {'title': 'P3', 'author': 'S. Watanabe', 'year': '2020'},
]
li = member_name_keys({'name': 'Chin-Jou Li'})
check('only the right Li matches', [r['title'] for r in bib_rows_for_member(entries, li)] == ['P1'])
check('bib_names adds a spelling', 'P3' in [r['title'] for r in bib_rows_for_member(
    entries, member_name_keys({'name': 'Shinji Watanabe', 'bib_names': ['S. Watanabe']}))])
real = parse_bib(PAPERS_BIB)
check('Shinji has at least 300 papers.bib entries',
      len(bib_rows_for_member(real, member_name_keys({'name': 'Shinji Watanabe'}))) >= 300)
```

- [ ] **Step 2: Run the self-test and see it fail**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: non-zero exit; `NameError` for `name_key` (or FAIL lines) before the matcher exists.

- [ ] **Step 3: Implement the copied helpers and the Produces list above in `bin/fetch_publications.py`**

Module docstring: what the script does, the two sources, `pip install pyyaml`, and the run commands (`python3 bin/fetch_publications.py`, `--selftest`).

- [ ] **Step 4: Run the self-test and see it pass**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: `8/8 self-test checks pass`, exit 0.

- [ ] **Step 5: Commit**

```bash
git add bin/fetch_publications.py
git commit -m "Add fetch_publications.py with the papers.bib author matcher"
```

---

### Task 2: Fix the three comma-separated author lists in papers.bib

**Files:**
- Modify: `_bibliography/papers.bib` (entries `seki19inter`, `wiesner19inter`, `hayashi19inter`)
- Modify: `bin/fetch_publications.py` (`selftest`)

**Interfaces:**
- Consumes: `parse_bib`, `split_authors`, `PAPERS_BIB` (Task 1).

- [ ] **Step 1: Add the lint check to `selftest()`**

A name with two or more commas is a list separated by commas, unless one comma part is a BibTeX suffix.

```python
SUFFIXES = {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv'}
bad = [e['_key'] for e in real for a in split_authors(e.get('author', ''))
       if a.count(',') >= 2 and not ({p.strip().lower() for p in a.split(',')} & SUFFIXES)]
check('papers.bib separates authors with "and"', bad == [])
```

- [ ] **Step 2: Run the self-test and see it fail**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: `FAIL papers.bib separates authors with "and"`; exit 1.

- [ ] **Step 3: In the three entries, replace each `, ` between two authors with ` and `**

Change only the `author` field. Keep every name's spelling.

- [ ] **Step 4: Run the self-test and the site build**

Run: `python3 bin/fetch_publications.py --selftest && bundle exec jekyll build`
Expected: `9/9 self-test checks pass`; the build ends with `done in`.

- [ ] **Step 5: Commit**

```bash
git add _bibliography/papers.bib bin/fetch_publications.py
git commit -m "Separate authors with and in three papers.bib entries"
```

---

### Task 3: Parse ORCID works from a checked-in fixture

**Files:**
- Create: `bin/testdata/orcid_works_sample.json`
- Modify: `bin/fetch_publications.py`

**Interfaces:**
- Consumes: `TESTDATA_DIR`, `normalize_title` (Task 1).
- Produces:
  - `EXCLUDED_TYPES = {'data-set', 'software', 'patent', 'lecture-speech', 'supervised-student-publication', 'website', 'physical-object', 'research-technique', 'spin-off-company', 'standards-and-policy', 'technical-standard'}`. Keep `other`: on Shinji's record all 353 `other` works are arXiv preprints, and 20 of his 25 displayed papers are among them.
  - `normalize_orcid(value) -> str | None` — accept a bare iD or `https://orcid.org/<iD>` (also `http://`), strip spaces, upper-case `x`; return `NNNN-NNNN-NNNN-NNN[0-9X]` or `None`.
  - `parse_orcid_works(data: dict) -> list[dict]` — for each `data['group']`, take `work-summary[0]`; skip it when the type is in `EXCLUDED_TYPES` or the title is empty. Row: `title` = `title.title.value`; `year` = `publication-date.year.value` or `''`; `venue` = `journal-title.value`, with `arxiv` in any case written `arXiv`; `url` = `https://doi.org/<doi>` from the first external id of type `doi`, else `url.value`, else `''`.

- [ ] **Step 1: Build the fixture**

Download Shinji's public record once and keep a small, fixed sample. Write it as `bin/testdata/orcid_works_sample.json`:

```bash
python3 - <<'PY'
import json, re, urllib.request
UA = "wavlab-site-publications/1.0 (+https://github.com/wavlab-speech/shinjiwlab.github.io)"
req = urllib.request.Request("https://pub.orcid.org/v3.0/0000-0002-5970-8631/works",
                             headers={"Accept": "application/json", "User-Agent": UA})
groups = json.load(urllib.request.urlopen(req, timeout=30))["group"]
keep = ("title", "type", "publication-date", "journal-title", "external-ids", "url", "put-code")
slim = lambda g: {"work-summary": [{k: s.get(k) for k in keep} for s in g["work-summary"][:2]]}
key = lambda g: re.sub(r"[^a-z0-9]", "", g["work-summary"][0]["title"]["title"]["value"].lower())
typ = lambda g: g["work-summary"][0]["type"]
pick = [g for g in groups if typ(g) == "other"][:2] + [g for g in groups if typ(g) == "conference-paper"][:2] \
     + [g for g in groups if typ(g) == "journal-article"][:1]
others = {key(g): g for g in groups if typ(g) == "other"}
pair = next((others[key(g)], g) for g in groups if typ(g) != "other" and key(g) in others)
sample = [slim(g) for g in pick + list(pair)]
synthetic = [
    {"work-summary": [{"title": {"title": {"value": "Selftest data set"}}, "type": "data-set",
                       "publication-date": {"year": {"value": "2024"}}}]},
    {"work-summary": [{"title": None, "type": "conference-paper",
                       "publication-date": {"year": {"value": "2024"}}}]},
    {"work-summary": [{"title": {"title": {"value": "Selftest work with no date"}},
                       "type": "journal-article", "publication-date": None}]},
]
json.dump({"group": sample + synthetic}, open("bin/testdata/orcid_works_sample.json", "w"), indent=1)
print(len(sample), "real groups +", len(synthetic), "synthetic")
PY
```

Expected: `7 real groups + 3 synthetic`.

- [ ] **Step 2: Add the failing checks to `selftest()`**

```python
sample = json.load(open(os.path.join(TESTDATA_DIR, 'orcid_works_sample.json')))
rows = parse_orcid_works(sample)
titles = [r['title'] for r in rows]
check('excluded type is dropped', 'Selftest data set' not in titles)
check('work with no title is dropped', len(rows) == len(sample['group']) - 2)
check('work with no date keeps an empty year',
      [r['year'] for r in rows if r['title'] == 'Selftest work with no date'] == [''])
check('arXiv venue is normalized', any(r['venue'] == 'arXiv' for r in rows))
check('DOI becomes a doi.org link', any(r['url'].startswith('https://doi.org/10.') for r in rows))
check('orcid: bare iD', normalize_orcid('0000-0002-5970-8631') == '0000-0002-5970-8631')
check('orcid: URL form, spaces, lower-case x',
      normalize_orcid(' https://orcid.org/0000-0002-1825-009x ') == '0000-0002-1825-009X')
check('orcid: invalid', normalize_orcid('0000-0002-5970') is None and normalize_orcid('') is None)
```

- [ ] **Step 3: Run the self-test and see it fail**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: non-zero exit; `NameError` for `parse_orcid_works`.

- [ ] **Step 4: Implement `EXCLUDED_TYPES`, `normalize_orcid` and `parse_orcid_works`**

Read every nested key with `(x or {}).get(...)`: ORCID uses `null` for missing parts.

- [ ] **Step 5: Run the self-test and see it pass**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: `17/17 self-test checks pass`.

- [ ] **Step 6: Commit**

```bash
git add bin/fetch_publications.py bin/testdata/orcid_works_sample.json
git commit -m "Parse ORCID works, with a checked-in sample record"
```

---

### Task 4: Fetch, merge, guard, save, and the main loop

**Files:**
- Modify: `bin/fetch_publications.py`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces:
  - `USER_AGENT` (the exact string in Global Constraints); `ORCID_WORKS_URL = 'https://pub.orcid.org/v3.0/{orcid}/works'`.
  - `class OrcidError(Exception)`.
  - `fetch_orcid_works(orcid: str, opener=urllib.request.urlopen, timeout: float = 30.0) -> dict` — raises `OrcidError` on `HTTPError`, `URLError`, `TimeoutError`, or JSON that does not decode to a dict.
  - `merge_rows(orcid_rows: list[dict], bib_rows: list[dict], bib_index: BibIndex) -> list[dict]` — `enrich` each ORCID row, append the bib rows, then `sort_newest_first(dedupe(...))`. Because `dedupe` keys on the normalized title, a bib row that ORCID also has collapses into the enriched ORCID row.
  - `member_rows(member: dict, entries: list[dict], bib_index: BibIndex, fetch=fetch_orcid_works) -> tuple[str, list[dict]]` — returns `('papers.bib', bib rows sorted)` when the member has no `orcid` key; else `('papers.bib+orcid', merge_rows(...))`. Raises `OrcidError` from `fetch`, and `ValueError` when `orcid` is present but `normalize_orcid` returns `None`.
  - `read_existing(member_id: str) -> dict | None` (copied).
  - `write_file(member_id: str, source: str, total: int, pubs: list[dict]) -> str`.
  - `save_publications(member_id: str, source: str, pubs: list[dict]) -> bool` — refuse when `existing.get('source') == source` and `total < previous * MIN_KEEP_RATIO`; else write the total and `pubs[:KEEP_LATEST]`.
  - `ensure_member_files(members: list[dict]) -> list[str]` — as before, with `write_file(id, 'papers.bib', 0, [])`.
  - `refresh_member(member: dict, entries: list[dict], bib_index: BibIndex, fetch=fetch_orcid_works) -> str` — one of `'saved'`, `'refused'`, `'orcid_failed'`, `'invalid_orcid'`. It changes no file for the last two and prints the reason.
  - `exit_status(orcid_attempts: int, orcid_failures: int) -> int` — `1` if `orcid_attempts > 0 and orcid_failures == orcid_attempts`, else `0`.
  - `main(argv)` without `--selftest`: parse papers.bib once, `ensure_member_files`, loop the members with `time.sleep(1)` after each ORCID request, print one line per member and `Refreshed X of Y members (Z ORCID failures).`, return `exit_status(...)`.

- [ ] **Step 1: Add the failing checks to `selftest()`**

Point `PUBS_DIR` at `tempfile.mkdtemp()` for these checks and restore it afterwards.

```python
def fake_fetch(works):
    return lambda orcid, **kw: works
def failing_fetch(orcid, **kw):
    raise OrcidError('HTTP 503')
def opener_429(req, timeout):
    raise urllib.error.HTTPError(req.full_url, 429, 'Too Many Requests', {}, None)
index = build_bib_index([{'title': 'Shared Paper', 'abbr_publisher': 'ICASSP', 'year': '2025', 'author': 'Shinji Watanabe'}])
merged = merge_rows([{'title': 'shared paper', 'venue': 'arXiv', 'year': '2025', 'url': ''},
                     {'title': 'Dup Title', 'venue': 'arXiv', 'year': '2024', 'url': ''},
                     {'title': 'Dup Title', 'venue': 'Interspeech', 'year': '2025', 'url': ''}],
                    [{'title': 'Shared Paper', 'venue': 'ICASSP', 'year': '2025', 'url': ''},
                     {'title': 'Bib Only', 'venue': 'SLT', 'year': '2023', 'url': ''}], index)
check('merge: bib metadata wins', ('Shared Paper', 'ICASSP') in [(r['title'], r['venue']) for r in merged])
check('merge: preprint and published collapse to the newest', [r['year'] for r in merged if r['title'] == 'Dup Title'] == ['2025'])
check('merge: bib-only paper is added', 'Bib Only' in [r['title'] for r in merged])
try:
    fetch_orcid_works('0000-0002-5970-8631', opener=opener_429); got = False
except OrcidError:
    got = True
check('HTTP 429 raises OrcidError', got)
m = {'id': 'm1', 'name': 'Shinji Watanabe', 'orcid': '0000-0002-5970-8631'}
write_file('m1', 'papers.bib+orcid', 100, [])
check('same source, big drop is refused', refresh_member(m, [], index, fetch=fake_fetch({'group': []})) == 'refused'
      and read_existing('m1')['total'] == 100)
write_file('m1', 'papers.bib+orcid', 100, [])
check('ORCID failure keeps the file', refresh_member(m, [], index, fetch=failing_fetch) == 'orcid_failed'
      and read_existing('m1')['total'] == 100)
check('invalid orcid keeps the file', refresh_member(dict(m, orcid='0000-12'), [], index, fetch=failing_fetch) == 'invalid_orcid'
      and read_existing('m1')['total'] == 100)
yaml.safe_dump({'total': 855, 'pubs': []}, open(os.path.join(PUBS_DIR, 'm2.yml'), 'w'))
check('file without source is replaced', save_publications('m2', 'papers.bib+orcid', [{'title': 'T', 'venue': '', 'year': '2025', 'url': ''}])
      and read_existing('m2')['source'] == 'papers.bib+orcid')
write_file('m3', 'papers.bib', 10, [])
check('a different source is replaced', save_publications('m3', 'papers.bib+orcid', [{'title': 'T', 'venue': '', 'year': '2025', 'url': ''}]))
check('exit status', (exit_status(3, 3), exit_status(3, 2), exit_status(0, 0)) == (1, 0, 0))
```

- [ ] **Step 2: Run the self-test and see it fail**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: non-zero exit; `NameError` for `merge_rows`.

- [ ] **Step 3: Implement the Produces list above**

`fetch_orcid_works` builds `urllib.request.Request(ORCID_WORKS_URL.format(orcid=orcid), headers={'Accept': 'application/json', 'User-Agent': USER_AGENT})` and calls `opener(req, timeout=timeout)`.

- [ ] **Step 4: Run the self-test and see it pass**

Run: `python3 bin/fetch_publications.py --selftest`
Expected: `27/27 self-test checks pass`.

- [ ] **Step 5: Run once against the live API for Shinji, without writing files**

```bash
python3 - <<'PY'
import importlib.util, re, subprocess, yaml
spec = importlib.util.spec_from_file_location("fp", "bin/fetch_publications.py"); fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
entries = fp.parse_bib(fp.PAPERS_BIB); index = fp.build_bib_index(entries)
source, rows = fp.member_rows({'name': 'Shinji Watanabe', 'orcid': '0000-0002-5970-8631'}, entries, index)
old = yaml.safe_load(subprocess.check_output(['git', 'show', 'origin/source:_data/scholar_pubs/shinji_watanabe.yml']))['pubs']
new = {fp.normalize_title(r['title']) for r in rows}
print(source, len(rows), 'rows;', sum(fp.normalize_title(p['title']) in new for p in old), 'of', len(old), 'old displayed titles found')
PY
```

Expected: `papers.bib+orcid`, more than 700 rows, and at least `23 of 25` old titles found.

- [ ] **Step 6: Commit**

```bash
git add bin/fetch_publications.py
git commit -m "Fetch ORCID works, merge them with papers.bib, and guard the save"
```

---

### Task 5: Move the data, remove the old script, and update the card and the Members page

**Files:**
- Move: `_data/scholar_pubs/` → `_data/member_pubs/` (`git mv`)
- Delete: `bin/fetch_scholar.py` (`git rm`)
- Modify: `_includes/member_card.html`
- Modify: `_pages/members.md:298-306` (the `pub-disclaimer` paragraph)

**Interfaces:**
- Consumes: the output format in Global Constraints.

- [ ] **Step 1: Move the data and remove the old script**

Run: `git mv _data/scholar_pubs _data/member_pubs && git rm -q bin/fetch_scholar.py`

- [ ] **Step 2: Update `_includes/member_card.html`**

- Read `site.data.member_pubs[m.id]` instead of `site.data.scholar_pubs[m.id]`.
- `{%- assign orcid = m.orcid | default: "" | remove: "https://orcid.org/" | remove: "http://orcid.org/" | strip -%}` and `orcid_url = "https://orcid.org/" | append: orcid | escape`.
- In `member-card-links`, after the Google Scholar link: `{%- if orcid != "" %}<a href="{{ orcid_url }}" target="_blank" rel="noopener noreferrer">ORCID ↗</a>{% endif -%}`.
- "View all" and "View on" links: ORCID when `orcid != ""`, else Google Scholar when `scholar != ""`, else none. Copy: `View all on ORCID ↗` / `View on ORCID ↗`.
- Update the header comment: data from papers.bib and ORCID via `bin/fetch_publications.py`; the file path; the escaping note now covers ORCID-sourced fields.

- [ ] **Step 3: Replace the `pub-disclaimer` paragraph in `_pages/members.md`**

```html
<p class="pub-disclaimer">
The publication list under each member comes from two sources: the lab's
curated list of papers, and the member's public
<a href="https://orcid.org/" target="_blank" rel="noopener noreferrer">ORCID</a>
record. It shows only the most recent papers, so it can be incomplete or out
of date. For a complete list, please see each member's own website or ORCID
record, linked on their card. The lab's curated list of papers is on the
<a href="{{ site.baseurl }}/publications/">Publications</a> page.
</p>
```

- [ ] **Step 4: Build and check the members page**

Run: `bundle exec jekyll build && grep -o '">Google Scholar ↗</a>' _site/members/index.html | wc -l && grep -o 'ORCID ↗' _site/members/index.html | wc -l; grep -c 'scholar.google.com/"' _site/members/index.html`
Expected: build ends with `done in`; `16` card-header Google Scholar links (the pattern starts at `">`, so it skips the "View all on Google Scholar ↗" links); `0` ORCID links (no `orcid` fields yet); `0` for the old Google Scholar link in the disclaimer.

- [ ] **Step 5: Check the ORCID link with a temporary value, then revert it**

Run: add `orcid: https://orcid.org/0000-0002-5970-8631` to Shinji's entry, then `bundle exec jekyll build && grep -o 'href="https://orcid.org/0000-0002-5970-8631"' _site/members/index.html | sort -u; git checkout _data/members.yml`
Expected: exactly one line, `href="https://orcid.org/0000-0002-5970-8631"` (the URL form was stripped once, not doubled).

- [ ] **Step 6: Commit**

```bash
git add -A _data/member_pubs _data/scholar_pubs bin/fetch_scholar.py _includes/member_card.html _pages/members.md
git commit -m "Read member publications from _data/member_pubs and link to ORCID"
```

---

### Task 6: The workflow, the member docs and the members.yml header

**Files:**
- Modify: `.github/workflows/update-publications.yml`
- Modify: `docs/adding-a-member.md`
- Modify: `_data/members.yml` (header comment only, lines 1–35)

- [ ] **Step 1: Update the workflow**

- Header comment and `name:` (`Update Member Publications`): sources are papers.bib and ORCID.
- Checkout: delete `ref: source`, so a manual run on a branch tests that branch. The default branch is `source`, so the schedule still uses `source`.
- Delete the `Set up Python` comment about scholarly; `pip install pyyaml`.
- New step before the fetch: `python3 bin/fetch_publications.py --selftest`.
- Fetch step: `python3 -u bin/fetch_publications.py`, `timeout-minutes: 10`. Rewrite its comments for ORCID.
- Pull request step: add `if: github.ref == 'refs/heads/source'` (a run on another branch would put that branch's code into the bot PR); `branch: bot/update-member-pubs`; `add-paths: _data/member_pubs/`; commit message `chore: refresh member publications from papers.bib and ORCID`; title `Update member publications from papers.bib and ORCID`; body: three short sentences: what changed, that papers.bib data wins over ORCID data, and that a member whose ORCID request failed kept the old file.

- [ ] **Step 2: Update `docs/adding-a-member.md`**

Keep the document's STE style. Change these parts:
- Line 6 and the "How you get your publication list" section: the sources are papers.bib and ORCID.
- Add an optional item "Your ORCID iD" beside the Google Scholar ID item: where to find it (`https://orcid.org/` → your record), the format `0000-0002-5970-8631`, and that the site shows only public works.
- State this fact: Interspeech and ACL papers do not reach ORCID automatically. Add them to your ORCID record by hand (ORCID: Add works → Add DOI).
- The example YAML (line 66) and the field table (lines 102–105): add `orcid` and `bib_names`; the data file path is `_data/member_pubs/<id>.yml`; `scholar_id` now gives only the card link.
- Manual run: `pip install pyyaml` and `python3 bin/fetch_publications.py`. Delete the `--enrich-only` instructions and the `bibtexparser` note. After you edit papers.bib, run the script again.
- "Incorrect titles": papers.bib data replaces ORCID data for the same paper; add your paper to papers.bib to correct it.
- Removal step (line 188) and the count explanation (lines 207–216): new path; the count is the number of different papers in papers.bib and your ORCID record.

- [ ] **Step 3: Update the `_data/members.yml` header comment**

Describe `orcid` and `bib_names` in the field list; replace `_data/scholar_pubs/` with `_data/member_pubs/` and `bin/fetch_scholar.py` with `bin/fetch_publications.py`.

- [ ] **Step 4: Verify**

Run: `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/update-publications.yml')); yaml.safe_load(open('_data/members.yml')); print('yaml ok')" && git grep -nE 'scholar_pubs|fetch_scholar|scholarly|bibtexparser' -- . ':(exclude)docs/superpowers' ':(exclude)_site'`
Expected: `yaml ok`, then no grep output (exit 1).

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/update-publications.yml docs/adding-a-member.md _data/members.yml
git commit -m "Describe ORCID in the workflow, the member docs and members.yml"
```

---

### Task 7: Collect the ORCID iDs, refresh the data, and prepare the pull request

**Files:**
- Modify: `_data/members.yml` (add confirmed `orcid` values)
- Modify: `_data/member_pubs/*.yml` (generated)
- Modify: `docs/superpowers/specs/2026-11-23-orcid-member-publications-design.md` (`Status:` line)

- [x] **Step 1–2: Collect and confirm the iDs (done 2026-11-23)**

The maintainer gave these iDs. Each checksum is valid, and each ORCID record carries the member's name. A member not listed has no ORCID iD and gets no `orcid` field: `ting_jiang`, `haoran_wang`, `kuangda_wang`.

| `id` | `orcid` |
|---|---|
| `samuele_cornell` | `0000-0002-5358-1844` |
| `chienyu_huang` | `0000-0003-4927-1293` |
| `shinji_watanabe` | `0000-0002-5970-8631` |
| `william_chen` | `0000-0002-3251-3084` |
| `shikhar_bharadwaj` | `0009-0000-4927-4561` |
| `jinchuan_tian` | `0009-0002-5461-4342` |
| `jaeyeon_kim` | `0009-0007-4412-9999` |
| `sichen_jin` | `0009-0000-6932-0342` |
| `haeri_kim` | `0009-0004-1267-0092` |
| `masao_someki` | `0009-0006-5864-7634` |
| `chinjou_li` | `0009-0007-8221-4553` |
| `kazuki_yano` | `0009-0004-2180-9359` |
| `jeeweon_jung` | `0000-0003-0505-2988` |

On 2026-11-23, seven of these records had no public works: `jinchuan_tian`, `shikhar_bharadwaj`, `masao_someki`, `chinjou_li`, `jaeyeon_kim`, `sichen_jin`, `kazuki_yano`. Their lists come from `papers.bib` until they add public works. `kazuki_yano` has no data file on `origin/source`; `ensure_member_files` creates it.

- [ ] **Step 3: Add the thirteen `orcid` values above to `_data/members.yml`**

Put each `orcid:` line directly after the member's `scholar_id:` line, as the bare iD.

- [ ] **Step 4: Run the self-test and the live refresh**

Run: `python3 bin/fetch_publications.py --selftest && python3 -u bin/fetch_publications.py`
Expected: the self-test passes; then one line per member and `Refreshed N of 16 members (0 ORCID failures).`; exit 0. Every file in `_data/member_pubs/` has a `source` key.

- [ ] **Step 5: Build and look at the Members page**

Run: `bundle exec jekyll build`, then open `/members/` in the local preview.
Expected: every card shows its list and count; members with an iD show `ORCID ↗`; light and dark mode render; no console errors.

- [ ] **Step 6: Mark the spec as implemented, and commit**

Set the spec's `**Status:**` line to `implemented on 2026-11-<day>; ORCID iDs for <N> of 16 members.`

```bash
git add _data/members.yml _data/member_pubs docs/superpowers/specs/2026-11-23-orcid-member-publications-design.md
git commit -m "Add the confirmed ORCID iDs and refresh the member publications"
```

- [ ] **Step 7: Draft the pull request text and wait for approval**

Write a short title and body (the change, and how to check it). Show them to the maintainer. Push and open the PR against `source` only after the maintainer approves the text.

- [ ] **Step 8: After the merge**

Run: `gh workflow enable update-publications.yml && gh workflow run update-publications.yml --ref source`
Expected: the run passes the self-test and the fetch, builds the site, and opens no PR or a PR with no unexpected change.
