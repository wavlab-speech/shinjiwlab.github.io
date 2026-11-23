# Member publication lists from papers.bib and ORCID

**Status:** design approved in conversation on 2026-11-23. Not implemented.
**Date:** 2026-11-23

## Problem

The members page shows, for each member, the newest publications (20 shown, 25
stored) and a total count. `bin/fetch_scholar.py` fetches them every week from
Google Scholar with the `scholarly` library. Then it corrects the title, venue,
year and link from `_bibliography/papers.bib`.

Google Scholar returns HTTP 403 to GitHub-hosted runners. From 2026-10-11 to
2026-11-22, seven runs reached Google Scholar, and six failed. The one success
(2026-10-18) got a runner that was not blocked. The workflow was disabled with
`gh workflow disable update-publications.yml`.

The fetch also does not meet the maintainer's requirement for a safe method:

- Google Scholar has no API. Its help page refuses bulk access.
- Its robots.txt (Wayback copy, 2026-09-23) has `Disallow: /citations?`, and
  allows only `/citations?user=`. `scholarly` 1.7.11 requests
  `/citations?hl=en&user=<id>`, so the request is disallowed. Pagination
  (`cstart=`) is disallowed too.
- The Google Terms of Service forbid automated access that violates robots.txt.

## The requirement: "safe"

The maintainer defined "safe" as:

- The data provider's terms permit the automated access. Nothing circumvents a
  block.
- No third-party proxies.
- No vendor in a legal dispute about scraping.
- The job runs unattended on GitHub-hosted runners at no cost.

## Approaches considered

| Approach | Result |
|---|---|
| Google Scholar through `FreeProxies` | Rejected. It sends requests through unknown machines to go around a deliberate block. One site that uses it failed for 8 days in a row (rzhangbq, 2026-11-10 to 11-17). |
| Google Scholar through SerpApi | Rejected. Reliable on runners (ooibc88: 49 of 49 runs), but Google sued SerpApi in 2025-12, and it still scrapes Google Scholar. |
| Google Scholar through ScraperAPI | Rejected. Paid ($49 per month), and it is a proxy. |
| Google Scholar, more frequent runs | Rejected. Does not avoid the block, and still violates robots.txt. |
| DBLP | Rejected. Its robots.txt disallows the search API and `/pid/*.xml` and `/pid/*.bib`. dblp.org returned an Anubis bot challenge (HTTP 202) to every scripted client on 2026-11-23. |
| OpenAlex | Rejected. A free key gives $1 of use per day. But its documentation says the data is CC0, while its Terms of Service (2026-10-02) prohibit "unauthorized ... republication of the Data" without written consent. The two conflict. Author profiles also split: Shinji's 25 newest papers are spread over about 10 author IDs (best single ID: 7 of 25). |
| Semantic Scholar | Rejected. It needs an API key, the site must display "Semantic Scholar", AI2 may end access at any time, and profiles split (Shinji's newest paper is on a 9-paper fragment). |
| `papers.bib` only | Considered. Completely safe, but it covers only 51% of the papers shown today. New members and visitors get almost nothing. |
| **`papers.bib` + ORCID public API** | **Chosen.** |

Why ORCID: the ORCID Public APIs Terms of Service grant "a limited royalty-free
license to make non-commercial use of the Public APIs to ... search public data
in the ORCID Registry". Each person keeps one iD, so there is no algorithmic
author disambiguation. Shinji's record (`0000-0002-5970-8631`) holds 716 works
and covers 23 of his 25 displayed papers (measured 2026-11-23).

The accepted trade-off: a member's list is only as complete as that member's
ORCID record. Interspeech (ISCA, DOI prefix 10.21437) and ACL (10.18653) DOIs
carry no ORCID in Crossref (2025: 0 of 1,388 and 0 of 11,121 records). So these
papers do not reach ORCID automatically. Members must add them by hand.

## Goals

- Keep the page the same: up to 20 newest publications per member, and a total.
- Get the data from `papers.bib` (lab papers) and ORCID (the whole career).
- Run unattended every week, and open a pull request for human review.
- Need no secrets.

## Non-goals

- Citation counts.
- Any data from Google Scholar. `scholar_id` stays only as a profile link.
- Automatic ORCID iD discovery in the weekly job.
- Writing ORCID data back into `papers.bib`. `papers.bib` stays hand-curated.

## Anti-goals

- A member's list shrinks silently because ORCID was unreachable.
- A member's list shows another person's paper (many members share a common
  surname: 103 authors in `papers.bib` have the surname Li, 63 have Chen).
- The site shows data that the provider's terms do not allow.

## Design

### Data model

- `_data/members.yml` gets two new optional fields:
  - `orcid`: the 19-character iD, for example `0000-0002-5970-8631`.
  - `bib_names`: a list of other spellings of the member's name in `papers.bib`.
- `scholar_id` stays. The card uses it only for the "Google Scholar" link.
- The output moves from `_data/scholar_pubs/<id>.yml` to
  `_data/member_pubs/<id>.yml`, because the data no longer comes from Google
  Scholar. The file gets a new key, `source`:

  ```yaml
  source: papers.bib+orcid   # or "papers.bib" for a member without an orcid
  total: 716
  pubs:
  - title: ...
    year: '2026'
    venue: ICASSP
    url: https://...
  ```

### Script: `bin/fetch_publications.py`

It replaces `bin/fetch_scholar.py`. It keeps these parts of the old script:
`parse_bib`, `BibIndex`, `normalize_title`, `enrich`, `dedupe`,
`sort_newest_first`, `write_file`, `KEEP_LATEST = 25`.

For each member:

1. Find the member's entries in `papers.bib`. Compare the normalized full name
   with each author, in both BibTeX forms ("First Last" and "Last, First"), and
   with each spelling in `bib_names`. Never match on the surname alone.
2. If the member has an `orcid`, get
   `https://pub.orcid.org/v3.0/<orcid>/works` with
   `Accept: application/json` and no credentials (the anonymous API). From
   each work group, use the first work summary: title, publication year,
   `journal-title` as the venue, and a link from the DOI, the arXiv ID or the
   work URL.
3. Merge. Correct each ORCID row from `papers.bib` with `enrich` (the
   `papers.bib` data wins). Add the `papers.bib` entries that ORCID does not
   have. Remove duplicates with `dedupe`. Sort with `sort_newest_first`.
4. Save the total and the newest `KEEP_LATEST` entries.

The anonymous ORCID API allows 12 requests per second and 25,000 reads per day
for each IP address. The job sends about 16 requests each week.

### The truncation guard

Today `MIN_KEEP_RATIO = 0.7` refuses a new total below 70% of the stored total.
The stored totals come from Google Scholar, so the first run would be refused
for most members.

New rule: compare the totals only when the stored `source` is the same as the
new `source`. A file without `source` (from the Google Scholar period) is
replaced once.

### When ORCID fails

- If the ORCID request fails for a member, do not change that member's file.
  Report the member in the job log.
- Exit non-zero only when every ORCID request failed. Then the run turns red,
  which points to a real problem (for example an ORCID outage or an API
  change), not to one bad record.

### Fix three entries in `papers.bib`

`seki19inter`, `wiesner19inter` and `hayashi19inter` separate authors with
commas instead of `and`. BibTeX reads each list as one author. This breaks the
name match, and it shows the wrong authors on the Publications page. Change the
commas to `and`.

### Card, page and workflow

- `_includes/member_card.html`: read `site.data.member_pubs`. Show an
  "ORCID ↗" link when `orcid` is set. Keep the "Google Scholar ↗" link when
  `scholar_id` is set. The "View all" link goes to ORCID when `orcid` is set,
  and to Google Scholar if not.
- `_pages/members.md`: change the note that says the lists come from Google
  Scholar.
- `.github/workflows/update-publications.yml`: install only `pyyaml`, run
  `python3 -u bin/fetch_publications.py`, and keep the site build check and the
  pull request step (fixed branch `bot/update-scholar-pubs`; rename it). After
  the merge, enable the workflow again with
  `gh workflow enable update-publications.yml`.
- `docs/adding-a-member.md` and the header comment of `_data/members.yml`:
  describe `orcid` and `bib_names`, and the new data source.

### Collect the ORCID iDs (one time)

Search the ORCID public registry by name
(`https://pub.orcid.org/v3.0/expanded-search/`). The results show the
affiliations. List the likely iD for each member. The maintainer confirms each
iD with the member before it goes into `members.yml`. Members without an iD
keep a `papers.bib`-only list.

## Verification

- The name matcher: both BibTeX forms match; `bib_names` match; a different
  person with the same surname does not match ("Ching-Feng Liu" must not match
  "Chin-Jou Li").
- The author parser reads the three fixed entries correctly.
- The guard: the same source compares totals; a file without `source` is
  replaced.
- ORCID failure: the member's file does not change.
- A saved ORCID JSON response tests the parsing without the network.
- A live run for Shinji: at least 23 of his 25 currently displayed papers
  appear in the new list.
- `bundle exec jekyll build`, then the members page shows the lists, the counts
  and the correct links.

## Left to the builder

- Which ORCID work types to include. ORCID records can also hold data sets,
  software, patents and other types.
- What to show as the venue when `journal-title` is empty (common for
  conference papers).
- Whether to keep an offline mode (like `--enrich-only`) for local runs.
- How to test. The repo has no test suite.
- How to test the workflow on a branch: it checks out `ref: source`, so a run
  on a branch uses the old script unless the checkout follows the branch.

## Sources

- ORCID Public APIs Terms of Service: https://info.orcid.org/public-client-terms-of-service/
- ORCID API limits: https://info.orcid.org/faq/what-are-the-api-limits/
- Google Scholar robots.txt (Wayback, 2026-09-23): https://web.archive.org/web/20260923084854/https://scholar.google.com/robots.txt
- Google Scholar help (Wayback, 2026-11-15): https://web.archive.org/web/20261115040931/https://scholar.google.com/intl/en/scholar/help.html
- OpenAlex Terms of Service (2026-10-02): https://openalex.org/OpenAlex_termsofservice.pdf
- DBLP robots.txt: https://dblp.org/robots.txt
- al-folio closed the same Google Scholar problem as `wontfix`: https://github.com/alshedivat/al-folio/issues/3619
