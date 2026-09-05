#!/usr/bin/env python3
"""Detect lab papers that are on Shinji's public publication list but missing
from _bibliography/papers.bib.

Design: docs/superpowers/specs/2026-09-04-publication-sync-design.md

This script does not write to papers.bib. It reports what is missing and
exits 1 when there is work to do, so the weekly workflow can branch on it.

Usage:
    python scripts/check_publications.py                 # report to stdout
    python scripts/check_publications.py --review        # edit and write papers.bib
    python scripts/check_publications.py --report out.md # report to a file
    python scripts/check_publications.py --fixture f.html
    python scripts/check_publications.py --selftest
"""

from __future__ import annotations

import argparse
import difflib
import gzip
import hashlib
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import time
import unicodedata
import webbrowser
import urllib.error
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    sys.exit("error: beautifulsoup4 is required (pip install beautifulsoup4)")

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "_bibliography" / "papers.bib"

SITE_URL = "https://sites.google.com/view/shinjiwatanabe/publications"
CONTACT = "chienyuh@andrew.cmu.edu"
UA = f"wavlab-pubbot/1.0 (+https://www.wavlab.org; {CONTACT})"

# Only these two sections are lab publications. The rest of the page is
# Shinji's pre-CMU career, keynotes, tutorials and books.
KEEP_SECTIONS = {
    "Journal (refereed)",
    "International Conference and Workshop (refereed)",
}
ALL_SECTIONS = KEEP_SECTIONS | {
    "Book",
    "Book chapter",
    "PhD thesis",
    "Keynote talk",
    "Tutorial/Overview/Invited talk",
    "Review and overview paper",
}

MIN_YEAR = 2025           # this automation catches new papers, not backlog
YEAR_SANE = (1990, 2030)  # the source page contains 2070 and 2098

DUP_SKIP = 0.85           # >= this: silently treated as already present
DUP_SUSPECT = 0.60        # >= this: emitted but flagged as a possible duplicate

# A layout change must break loudly rather than emit an empty PR.
MIN_BLOCKS = 600
MIN_TITLES = 600

STOPWORDS = {
    "a", "an", "and", "at", "by", "for", "from", "in", "into", "of", "on",
    "or", "over", "the", "to", "under", "via", "with",
}
# Words a mechanical title-caser wrongly capitalises; used by the title report.
FUNCTION_WORDS = STOPWORDS | {"as", "but", "not", "nor", "so", "than", "that"}

# The `abbr` vocabulary is read from papers.bib at run time, not hard-coded.
# A literal list goes stale: it held 16 values while the file already used 39.
VOCAB_COMMON = 16          # how many of the most-used values a stub lists


def abbr_vocabulary(records: list[dict]) -> list[str]:
    """Every topic value in papers.bib, most-used first.

    Values combine with "&", so split them into their parts. Ordering by use
    lets a stub offer the common ones and keep the long tail out of the way.
    """
    counts: dict[str, int] = {}
    for record in records:
        for part in re.split(r"[&+]", record.get("abbr") or ""):
            part = part.strip()
            if part and part != "TODO":
                counts[part] = counts.get(part, 0) + 1
    return sorted(counts, key=lambda k: (-counts[k], k))

DQUOTE = '["“”]'
ENTRY_RE = re.compile(
    rf'^(?P<authors>.+?)\s*,?\s*{DQUOTE}\s*(?P<title>.+?)\s*[,.]?\s*'
    rf'(?:{DQUOTE}|\'\')\s*(?P<rest>.*)$'
)

# Ordered: first match wins. (pattern, entry_type, venue field value, abbr_publisher)
# Keys match OpenAlex canonical venue names and the site's raw venue text.
# `None` as the venue value means "emit a TODO and the raw string".
VENUE_MAP: list[tuple[str, str, str | None, str]] = [
    (r"\bfindings\b.*\bEMNLP\b|\bEMNLP\b.*\bfindings\b", "inproceedings", "{Proceedings of Findings of EMNLP}", "EMNLP"),
    (r"\bfindings\b.*\bACL\b|\bACL\b.*\bfindings\b", "inproceedings", "ACLFindings", "ACLFindings"),
    (r"\bfindings\b.*\bEACL\b", "inproceedings", "EACLFindings", "EACLFindings"),
    (r"\bEMNLP\b|Empirical Methods in Natural Language", "inproceedings", "{Proceedings of EMNLP}", "EMNLP"),
    (r"\bInterspeech\b", "inproceedings", "interspeech", "Interspeech"),
    (r"\bICASSP\b|Acoustics,? Speech and Signal Processing", "inproceedings", "ICASSP", "ICASSP"),
    (r"\bASRU\b|Automatic Speech Recognition and Understanding", "inproceedings", "ASRU", "ASRU"),
    (r"\bSLT\b|Spoken Language Technology", "inproceedings", "SLT", "SLT"),
    (r"\bNAACL\b|North American Chapter", "inproceedings", "NAACL", "NAACL"),
    (r"\bEACL\b|European Chapter", "inproceedings", "EACL", "EACL"),
    (r"\bACL\b|Association for Computational Linguistics", "inproceedings", "ACL", "ACL"),
    (r"\bICML\b|International Conference on Machine Learning", "inproceedings", "ICML", "ICML"),
    (r"\bICLR\b|Learning Representations", "inproceedings", "ICLR", "ICLR"),
    (r"\bNeurIPS\b|\bNIPS\b|Neural Information Processing", "inproceedings", "NeurIPS", "NeurIPS"),
    (r"\bAAAI\b", "inproceedings", "AAAI", "AAAI"),
    (r"\bIJCAI\b", "inproceedings", "{Proceedings of IJCAI}", "IJCAI"),
    (r"\bWASPAA\b", "inproceedings", "WASPAA", "WASPAA"),
    (r"\bAPSIPA\b", "inproceedings", "APSIPA", "APSIPA"),
    (r"\bIWSLT\b|Spoken Language Translation", "inproceedings", "IWSLT", "IWSLT"),
    (r"\bCOLM\b|Conference on Language Modeling", "inproceedings", "{Proceedings of COLM}", "COLM"),
    (r"\bCHiME\b", "inproceedings", "{CHiME Workshop}", "CHiME"),
    (r"\bDCASE\b", "inproceedings", "{DCASE Workshop}", "DCASE"),
    (r"\bISMIR\b", "inproceedings", "{Proceedings of ISMIR}", "ISMIR"),
    (r"\bEUSIPCO\b", "inproceedings", "{Proceedings of EUSIPCO}", "EUSIPCO"),
    # journals
    (r"Transactions on Audio,? Speech,? and Language|\bTASLP\b|IEEE ACM Trans. Audio",
     "article", "TASLP", "TASLP"),
    (r"Computer Speech (&|and) Language|Comput. Speech Lang.", "article",
     "{Computer Speech \\& Language}", "CSL"),
    (r"Signal Processing Letters", "article", "{IEEE Signal Processing Letters}", "SPL"),
    (r"Selected Topics in Signal Processing", "article",
     "{IEEE Journal of Selected Topics in Signal Processing}", "JSTSP"),
    (r"Open Journal of Signal Processing", "article",
     "{IEEE Open Journal of Signal Processing}", "OJSP"),
    (r"Transactions on Multimedia", "article", "{IEEE Transactions on Multimedia}", "TMM"),
    (r"Speech Communication", "article", "{Speech Communication}", "SpeechCom"),
    (r"Signal Processing Magazine", "article", "{IEEE Signal Processing Magazine}", "SPM"),
]


# The review page offers venues by label. One choice sets the entry type, the
# field name and whether the value is a bare @string macro or a braced literal.
# Those three move together, which is what makes `booktitle=IWSLTT` (an
# undefined macro, rendered "In iwsltt 2022" for months) and `@article` with a
# `booktitle` (which renders no venue at all) impossible to express here.
#   label -> (entry type, field, value, braced, abbr_publisher)
VENUE_BY_LABEL: dict[str, tuple[str, str, str, bool, str]] = {}
for _pattern, _kind, _value, _abbr in VENUE_MAP:
    if _value is None:
        continue
    _label = "EMNLP Findings" if _value == "{Proceedings of Findings of EMNLP}" else _abbr
    if _label in VENUE_BY_LABEL:
        continue
    _braced = _value.startswith("{")
    VENUE_BY_LABEL[_label] = (
        _kind,
        "journal" if _kind == "article" else "booktitle",
        _value.strip("{}") if _braced else _value,
        _braced,
        _abbr,
    )


# ---------------------------------------------------------------- normalising

def hard_key(text: str) -> str:
    """Aggressive identity key: ignores case, punctuation and spacing."""
    text = unicodedata.normalize("NFKD", text).lower()
    return re.sub(r"[^a-z0-9]", "", text)


def tokens(text: str) -> set[str]:
    text = unicodedata.normalize("NFKD", text).lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return {w for w in text.split() if w and w not in STOPWORDS}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


# ------------------------------------------------------------------- scraping

def read_html(path: Path) -> str:
    """Read a fixture, transparently handling gzip (the checked-in one is .gz
    because the raw page is 585 KB)."""
    if path.suffix == ".gz":
        return gzip.decompress(path.read_bytes()).decode("utf-8", "replace")
    return path.read_text(encoding="utf-8")


def fetch(url: str, tries: int = 6, timeout: int = 30) -> bytes:
    """GET with a self-identifying User-Agent and exponential backoff.

    The User-Agent is not optional: without one, sites.google.com and dblp
    both return 503.

    This is the only network call the script makes, and it is critical: without
    the page there is no run at all. So it retries generously and honours
    `Retry-After` when sent.
    """
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last = exc
            code = getattr(exc, "code", None)
            if code is not None and code not in (429, 500, 502, 503, 504):
                raise
            if attempt == tries - 1:
                break
            delay = 2 ** attempt
            retry_after = getattr(exc, "headers", None)
            if retry_after is not None:
                try:
                    delay = max(delay, min(60, int(retry_after.get("Retry-After", 0))))
                except (TypeError, ValueError):
                    pass
            time.sleep(delay)
    raise RuntimeError(f"giving up on {url}: {last}")


def scrape(html: str) -> list[dict]:
    """Extract publication entries, tagged with their section heading.

    Uses role/dir attributes rather than Google's generated class names
    (zfr3Q), which are not contractual. Spans are joined with NO separator:
    Google Sites splits text mid-word, so a space separator corrupts tokens
    into things like "Interspeech'2 5" and "(202 3 )".
    """
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.select("p[role=presentation][dir=ltr], h1, h2, h3, h4")
    if len(blocks) < MIN_BLOCKS:
        raise RuntimeError(
            f"scrape found only {len(blocks)} blocks (expected >= {MIN_BLOCKS}). "
            "The page layout has probably changed; refusing to continue rather "
            "than report a false 'nothing new'."
        )

    section: str | None = None
    entries: list[dict] = []
    for block in blocks:
        text = collapse(block.get_text(""))
        if not text:
            continue
        if text in ALL_SECTIONS:
            section = text
            continue
        if section is None or len(text) < 40:
            continue
        match = ENTRY_RE.match(text)
        if not match or len(match.group("title")) < 10:
            continue
        # Read the year from the venue text only, never from the whole citation.
        # Three titles carry a year of their own -- "2025 URGENT Speech
        # Enhancement Challenge ... Proc. ICASSP'26" -- and reading the whole
        # string picks the title's year over the venue's.
        rest = collapse(match.group("rest"))
        years = [
            int(y) for y in re.findall(r"\b(?:19|20)\d\d\b", rest)
            if YEAR_SANE[0] <= int(y) <= YEAR_SANE[1]
        ]
        entries.append({
            "section": section,
            "authors": match.group("authors").strip(),
            "title": collapse(match.group("title")).rstrip("."),
            "rest": rest,
            "year": max(years) if years else None,
            "raw": text,
        })

    if len(entries) < MIN_TITLES:
        raise RuntimeError(
            f"scrape extracted only {len(entries)} titles (expected >= {MIN_TITLES}). "
            "The citation format has probably changed; refusing to continue."
        )
    return entries


# -------------------------------------------------------------------- reading

def parse_bib(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    records = []
    offset = 0
    for chunk in re.split(r"\n(?=@)", raw):
        line_no = raw.count("\n", 0, offset) + 1
        offset += len(chunk) + 1
        stripped = chunk.lstrip()
        if not stripped.startswith("@") or stripped.lower().startswith("@string"):
            continue
        cite = re.match(r"@(\w+)\{([^,]+),", stripped)
        # Most entries use title={...}, but an ACL Anthology export uses
        # title = "..." instead. Missing one means that paper is never matched
        # and would be re-reported as missing forever.
        title = (re.search(r"title\s*=\s*\{(.*?)\},?\s*\n", chunk, re.S)
                 or re.search(r'title\s*=\s*"(.*?)",?\s*\n', chunk, re.S))
        if not cite or not title:
            continue
        clean = collapse(title.group(1)).strip("{}").replace("{", "").replace("}", "")
        year = re.search(r"year\s*=\s*\{?(\d{4})", chunk)
        abbr = re.search(r"abbr\s*=\s*\{([^}]*)\}", chunk)
        records.append({
            "citekey": cite.group(2).strip(),
            "abbr": abbr.group(1) if abbr else "",
            "title": clean,
            "year": year.group(1) if year else None,
            "line": line_no,
            "key": hard_key(clean),
            "tokens": tokens(clean),
        })
    return records



# ------------------------------------------------------------------ rendering

# Venue abbreviations carry the year: "Proc. Interspeech'26 (accepted)".
# Measured: this recovers a year for 226 of the 231 undated entries (98%),
# which is why the script needs no external API to fill `year`. The remaining
# few are journal papers marked "accepted" with no year anywhere -- those
# honestly have no year yet.
_APOSTROPHE_YEAR = re.compile(r"[\'\u2018\u2019](\d\d)\b")


def year_from_venue(rest: str) -> int | None:
    match = _APOSTROPHE_YEAR.search(rest)
    if not match:
        return None
    year = 2000 + int(match.group(1))
    return year if YEAR_SANE[0] <= year <= YEAR_SANE[1] else None


def map_venue(section: str, *candidates: str | None) -> tuple[str, str | None, str]:
    """Resolve (entry_type, venue field value, abbr_publisher)."""
    for text in candidates:
        if not text:
            continue
        for pattern, kind, value, abbr in VENUE_MAP:
            if re.search(pattern, text, re.I):
                return kind, value, abbr
    kind = "article" if section.startswith("Journal") else "inproceedings"
    return kind, None, "TODO"


def format_authors(raw: str) -> str:
    """Convert "A, B, and C" into BibTeX's "A and B and C"."""
    text = re.sub(r"\bMember\b\s*,?", "", raw)          # stray title in one entry
    text = re.sub(r",?\s+and\s+", ", ", text)
    parts = [p.strip(" .") for p in text.split(",")]
    return " and ".join(p for p in parts if p)


def make_citekey(authors: str, year: int | str | None, title: str) -> str:
    first = authors.split(" and ")[0] if authors else "unknown"
    surname = re.sub(r"[^a-z]", "", first.split()[-1].lower()) or "unknown"
    word = next(
        (w for w in re.sub(r"[^a-z0-9 ]", " ", title.lower()).split()
         if w not in STOPWORDS and len(w) > 3),
        "paper",
    )
    return f"TODO_{surname}{year or 'XXXX'}{word}"


def render_stub(entry: dict, suspect: tuple[float, dict] | None,
                vocab: list[str]) -> str:
    kind, venue, abbr = map_venue(entry["section"], entry["rest"])
    year = entry["year"] or year_from_venue(entry["rest"])
    authors = format_authors(entry["authors"])
    lines: list[str] = []

    if suspect:
        score, other = suspect
        lines += [
            f"% !! POSSIBLE DUPLICATE (Jaccard {score:.2f}) -- check before adding:",
            f"%    papers.bib:{other['line']}  {other['citekey']}",
            f"%    \"{other['title'][:88]}\"",
        ]
    lines.append(f"% source: Shinji's site, \"{entry['section']}\"")
    if not entry["year"]:
        note = f"year {year} inferred from the venue" if year else "year unknown"
        lines.append(f"% the site lists this without a year (\"accepted\"); {note}")
    if uppercase_ratio(entry["title"]) > 0.85:
        lines.append("% !! the site's title is ALL-CAPS (copied from a camera-ready);")
        lines.append("%    restore normal capitalisation before adding this.")
    if venue is None:
        lines.append(f"% venue unmapped, raw text: {entry['rest'][:70]}")

    lines.append("% abbr options: " + " ".join(vocab[:VOCAB_COMMON]))
    lines.append("%   combine with & for multi-topic work, e.g. abbr={SE&ASR}")
    lines.append(f"@{kind}{{{make_citekey(authors, year, entry['title'])},")
    lines.append("  abbr={TODO},")
    lines.append(f"  abbr_publisher={{{abbr}}},")
    lines.append(f"  title={{{entry['title']}}},")
    lines.append(f"  author={{{authors}}},")

    field = "journal" if kind == "article" else "booktitle"
    # `{...}` is a braced literal; anything else is a bare @string macro.
    lines.append(f"  {field}={'{TODO}' if venue is None else venue},")

    lines.append(f"  year={{{year or 'TODO'}}},")
    lines.append("}")
    return "\n".join(lines)


# ------------------------------------------------------------------ flagging

def uppercase_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


# ------------------------------------------------------------------- writing

class WriteRefused(Exception):
    """A check failed. The tool did not change papers.bib."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_entry(card: dict, vocab: list[str]) -> str:
    """Turn one completed card into the BibTeX text that goes into papers.bib.

    Raises WriteRefused with a message meant for the person, not the log.
    """
    title = collapse(card.get("title", ""))
    if len(title) < 10:
        raise WriteRefused("The title is too short.")

    abbr = [a for a in card.get("abbr", []) if a in vocab]
    if not abbr:
        raise WriteRefused(f"{title[:40]}: choose at least one topic.")
    # Fixed order, so ASR&SSL and SSL&ASR can never both exist.
    abbr.sort(key=vocab.index)

    venue = card.get("venue")
    if venue not in VENUE_BY_LABEL:
        raise WriteRefused(f"{title[:40]}: unknown venue {venue!r}.")
    kind, field, value, braced, publisher = VENUE_BY_LABEL[venue]

    try:
        year = int(card.get("year"))
    except (TypeError, ValueError):
        raise WriteRefused(f"{title[:40]}: the year is missing.")
    if not YEAR_SANE[0] <= year <= YEAR_SANE[1]:
        raise WriteRefused(f"{title[:40]}: {year} is not a plausible year.")

    authors = collapse(card.get("authors", ""))
    if " and " not in authors and len(authors) < 4:
        raise WriteRefused(f"{title[:40]}: the author list is empty.")

    lines = [f"@{kind}{{{card['citekey']},",
             f"  abbr={{{'&'.join(abbr)}}},",
             f"  abbr_publisher={{{publisher}}},",
             f"  title={{{title}}},",
             f"  author={{{authors}}},",
             f"  {field}={'{' + value + '}' if braced else value},",
             f"  year={{{year}}},"]
    for name in ("arxiv", "code", "html", "pdf"):
        raw = collapse(card.get("links", {}).get(name, ""))
        if not raw:
            continue
        if name == "arxiv":
            # A URL here builds http://arxiv.org/abs/<url>, a dead link. It
            # shipped three times before #289 caught it.
            bare = re.sub(r"^.*?arxiv\.org/(?:abs|pdf)/", "", raw)
            bare = bare[:-4] if bare.endswith(".pdf") else bare
            if not re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", bare):
                raise WriteRefused(f"{title[:40]}: the arxiv field needs a bare id, for example 2105.01051.")
            raw = bare
        elif not raw.startswith(("http://", "https://")):
            # Without a scheme the template prepends /assets/pdf/ and 404s.
            raise WriteRefused(f"{title[:40]}: the {name} link needs http:// or https://.")
        lines.append(f"  {name}={{{raw}}},")
    if card.get("selected"):
        lines.append("  selected={true},")
    lines.append("}")

    entry = "\n".join(lines)
    if entry.count("{") != entry.count("}"):
        raise WriteRefused(f"{title[:40]}: a field has an unbalanced brace.")
    return entry


def unique_citekey(base: str, taken: set[str], title: str) -> str:
    """A key nobody else uses.

    A collision is not an error in BibTeX: jekyll-scholar increments the last
    character of the second key, and that key is the entry's HTML anchor. Six
    such pairs were fixed in #290, so this refuses to make more.
    """
    if base not in taken:
        return base
    words = [w for w in re.sub(r"[^a-z0-9 ]", " ", title.lower()).split()
             if w not in STOPWORDS and len(w) > 2 and w not in base]
    for word in words:
        if base + word not in taken:
            return base + word
    for n in range(2, 50):
        if f"{base}{n}" not in taken:
            return f"{base}{n}"
    raise WriteRefused(f"Cannot find a free citation key near {base!r}.")


def splice(original: str, entries: list[tuple[int, str]]) -> str:
    """Insert each entry at the head of its year block.

    Insert only. Never parse the file and write it back out: a round trip
    through the parser would drop the 11 `selected` flags, every `abbr` badge
    and every link field, and turn a three-line change into a 4,500-line diff.
    """
    text = original
    for year, entry in sorted(entries, key=lambda e: e[0]):
        at = None
        for match in re.finditer(r"(?m)^@(?!string)\w+\{", text):
            chunk = text[match.start():match.start() + 900]
            found = re.search(r"year\s*=\s*\{?(\d{4})", chunk)
            if found and int(found.group(1)) < year:
                at = match.start()
                break
        if at is None:                       # older than everything in the file
            at = len(text.rstrip("\n")) + 1
            text = text.rstrip("\n") + "\n\n" + entry + "\n"
            continue
        text = text[:at] + entry + "\n\n" + text[at:]
    return text


def write_papers_bib(entries: list[tuple[int, str]], expect_digest: str) -> dict:
    """Write papers.bib, or raise and leave it exactly as it was."""
    if digest(BIB) != expect_digest:
        raise WriteRefused(
            "Another program changed papers.bib after this page opened. "
            "The tool wrote nothing. Reload the page to start again.")

    before = BIB.read_text(encoding="utf-8")
    n_before = len(parse_bib(BIB))
    after = splice(before, entries)

    backup = BIB.with_suffix(".bib.bak")
    backup.write_text(before, encoding="utf-8")

    # Same directory, so os.replace is atomic. A crash mid-write leaves the
    # original file untouched rather than a truncated one.
    tmp = BIB.with_suffix(".bib.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(after)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, BIB)

    try:
        records = parse_bib(BIB)
        keys = [r["citekey"] for r in records]
        if len(records) != n_before + len(entries):
            raise WriteRefused(
                f"papers.bib now holds {len(records)} entries. "
                f"The tool expected {n_before + len(entries)}.")
        if len(set(keys)) != len(keys):
            duplicated = {k for k in keys if keys.count(k) > 1}
            raise WriteRefused(
                f"These citation keys now occur more than once: {duplicated}.")
    except Exception:
        os.replace(backup, BIB)
        raise
    try:
        shown = str(backup.relative_to(ROOT))
    except ValueError:                       # a test copy outside the repo
        shown = str(backup)
    return {"written": len(entries), "entries": n_before + len(entries),
            "backup": shown}


# ------------------------------------------------------------------- serving

PAGE = ROOT / "scripts" / "review_page.html"


def git(*args: str) -> str:
    try:
        done = subprocess.run(("git",) + args, cwd=str(ROOT),
                              capture_output=True, text=True, timeout=10)
        return done.stdout.strip() if done.returncode == 0 else ""
    except Exception:
        return ""


def build_payload(missing: list[tuple[dict, tuple[float, dict] | None]],
                  records: list[dict], vocab: list[str]) -> dict:
    """Everything the page needs, decided here rather than in the browser."""
    taken = {r["citekey"] for r in records}
    papers = []
    for index, (entry, suspect) in enumerate(missing):
        kind, venue, publisher = map_venue(entry["section"], entry["rest"])
        year = entry["year"] or year_from_venue(entry["rest"])
        authors = format_authors(entry["authors"])
        key = unique_citekey(
            make_citekey(authors, year, entry["title"]).replace("TODO_", ""),
            taken, entry["title"])
        taken.add(key)
        papers.append({
            "id": f"p{index}",
            "citekey": key,
            "title": entry["title"],
            "authors": authors,
            "rest": entry["rest"],
            "venue": publisher if publisher in VENUE_BY_LABEL else "",
            "year": year,
            "duplicate": ({"citekey": suspect[1]["citekey"],
                           "line": suspect[1]["line"],
                           "score": round(suspect[0], 2)} if suspect else None),
        })
    return {
        "papers": papers,
        "vocab": vocab,
        "common": VOCAB_COMMON,
        "venues": {k: list(v) for k, v in VENUE_BY_LABEL.items()},
        "entries": len(records),
        "digest": digest(BIB),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD") or "unknown",
        "dirty": bool(git("status", "--porcelain", "--", str(BIB))),
    }


def serve_review(payload: dict, vocab: list[str]) -> int:
    """Serve the review page on the loopback address until one write happens."""
    if not PAGE.exists():
        print(f"error: page template not found: {PAGE}", file=sys.stderr)
        return 2
    template = PAGE.read_text(encoding="utf-8")
    outcome = {"code": 1}

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_args):        # keep the terminal readable
            pass

        def _send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            page = template.replace("__DATA__", json.dumps(payload))
            self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")

        def do_POST(self):
            if self.path != "/commit":
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
                cards = body.get("cards") or []
                if not cards:
                    raise WriteRefused("No paper is ready.")
                entries = []
                for card in cards:
                    entries.append((int(card["year"]), build_entry(card, vocab)))
                result = write_papers_bib(entries, body.get("digest", ""))
            except WriteRefused as refusal:
                self._send(409, json.dumps({"error": str(refusal)}).encode(),
                           "application/json; charset=utf-8")
                return
            except Exception as exc:          # a bug here must not damage the file
                self._send(500, json.dumps({"error": f"{type(exc).__name__}: {exc}"}).encode(),
                           "application/json; charset=utf-8")
                return
            self._send(200, json.dumps(result).encode(),
                       "application/json; charset=utf-8")
            print(f"\nwrote {result['written']} entries to "
                  f"_bibliography/papers.bib ({result['entries']} total)")
            print(f"backup: {result['backup']}")
            print("\nread the change before you push:")
            print("  git diff _bibliography/papers.bib")
            print("\nthe tool checked the structure. please check the facts:")
            print("  the title, the venue, the year and the topic")
            print("\nto undo:")
            print("  git checkout -- _bibliography/papers.bib")
            outcome["code"] = 0
            threading.Thread(target=server.shutdown, daemon=True).start()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"review page: {url}")
    if payload["dirty"]:
        print("note: papers.bib already has uncommitted changes", file=sys.stderr)
    if payload["branch"] in ("master", "main"):
        print(f"note: you are on branch {payload['branch']}", file=sys.stderr)
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nthe tool stopped. it wrote nothing.")
    finally:
        server.server_close()
    return outcome["code"]


# ----------------------------------------------------------------- self-test

def selftest(fixture: Path) -> int:
    """Assertions from the spec's testing section."""
    entries = scrape(read_html(fixture))
    assert len(entries) >= MIN_TITLES, len(entries)
    print(f"  ok  scraper extracted {len(entries)} titles from the fixture")

    records = parse_bib(BIB)
    raw_count = len([c for c in re.split(r"\n(?=@)", BIB.read_text(encoding="utf-8"))
                     if c.lstrip().startswith("@")
                     and not c.lstrip().lower().startswith("@string")])
    assert len(records) == raw_count, (
        f"parsed {len(records)} of {raw_count} entries -- an unparsed entry can "
        "never be matched, so it would be re-reported as missing forever")
    print(f"  ok  parsed all {len(records)} entries from papers.bib")

    by_key = {r["key"]: r for r in records}
    # These papers ARE in papers.bib, so they must never be reported as new --
    # whether they match exactly or only fuzzily. Asserting the outcome rather
    # than the mechanism keeps the test valid after papers.bib title fixes.
    known_present = [
        "Align, Write, Re-order: Explainable End-to-End Speech Translation via Operation Sequence Generation",
        "ESPnet-SE++: Speech Enhancement for Robust Speech Recognition, Translation, and Understanding",
        "A Study on the Integration of Pre-Trained SSL, ASR, LM and SLU Models for Spoken Language Understanding",
    ]
    for title in known_present:
        exact = hard_key(title) in by_key
        best = max(jaccard(tokens(title), r["tokens"]) for r in records)
        assert exact or best >= DUP_SKIP, f"{title!r} would be reported as new (J={best:.2f})"
    print(f"  ok  {len(known_present)} papers already in papers.bib are not reported as new")

    # Branchformer is present in papers.bib under a longer title, so it must land
    # in the suspect band -- evidence that the threshold is not trustworthy alone.
    # This assertion depends on papers.bib content, so a legitimate edit to that
    # entry must not fail CI and block the bot: skip with a note if it is gone.
    branch = "Branchformer: Parallel MLP-Attention Architectures for Speech Recognition and Understanding"
    if any("branchformer" in r["tokens"] and "mlp" in r["tokens"] for r in records):
        best = max(jaccard(tokens(branch), r["tokens"]) for r in records)
        assert DUP_SUSPECT <= best < DUP_SKIP, f"Branchformer scored {best:.2f}"
        print(f"  ok  Branchformer lands in the suspect band ({best:.2f})")
    else:
        print("  --  Branchformer entry not found in papers.bib; suspect-band "
              "check skipped (data changed, not a logic failure)")

    assert year_from_venue("Proc. Interspeech'26 (accepted)") == 2026
    assert year_from_venue("Proc. Findings of EMNLP'26") == 2026
    assert year_from_venue("IEEE Open Journal of Signal Processing (accepted)") is None
    assert year_from_venue("Proc. ICASSP'12, pp. 4753--4756") == 2012
    recovered = sum(1 for e in entries
                    if e["year"] is None and year_from_venue(e["rest"]))
    undated = sum(1 for e in entries if e["year"] is None)
    assert recovered / max(undated, 1) > 0.9, f"only {recovered}/{undated} recovered"
    print(f"  ok  year recovered from the venue string for "
          f"{recovered}/{undated} undated entries")

    # A title can carry a year of its own ("2025 URGENT Speech Enhancement
    # Challenge ... Proc. ICASSP'26"). Reading the whole citation picked the
    # title's year over the venue's, and the stub then stated the wrong year.
    conflicts = [e for e in entries
                 if e["year"] and year_from_venue(e["rest"])
                 and e["year"] != year_from_venue(e["rest"])]
    assert not conflicts, (
        f"{len(conflicts)} entries take their year from the title rather than "
        f"the venue, e.g. {conflicts[0]['title'][:50]!r}")
    print("  ok  years come from the venue, not from a year inside the title")

    vocab = abbr_vocabulary(records)
    assert len(vocab) > 30, f"only {len(vocab)} abbr values learned from papers.bib"
    assert vocab[0] == "ASR", vocab[:3]
    print(f"  ok  learned {len(vocab)} abbr values from papers.bib at run time")

    kind, venue, abbr = map_venue("Journal (refereed)",
                                  "IEEE Transactions on Audio Speech and Language Processing")
    assert (kind, venue, abbr) == ("article", "TASLP", "TASLP"), (kind, venue, abbr)
    kind, venue, abbr = map_venue("International Conference and Workshop (refereed)",
                                  None, "Proc. Interspeech'26 (accepted)")
    assert (kind, venue, abbr) == ("inproceedings", "interspeech", "Interspeech")
    # venue strings must match the spelling papers.bib already uses, or the
    # page shows two names for one venue
    _, venue, _ = map_venue("International Conference and Workshop (refereed)",
                            None, "Proc. Findings of EMNLP'26")
    assert venue == "{Proceedings of Findings of EMNLP}", venue
    _, venue, _ = map_venue("Journal (refereed)", "Computer Speech & Language")
    assert venue == "{Computer Speech \\& Language}", venue
    print("  ok  venue mapper resolves journal and conference cases")

    assert format_authors("A B, C D, and E F") == "A B and C D and E F"
    assert "Member" not in format_authors("A B, Member, and C D")
    print("  ok  author formatter normalises separators")

    # --- the write path -------------------------------------------------
    vocab_all = abbr_vocabulary(records)
    card = {"citekey": "probe2026test", "title": "A Probe Entry For The Write Path",
            "authors": "Test Author and Shinji Watanabe", "abbr": ["SSL", "ASR"],
            "venue": "Interspeech", "year": 2026, "links": {}, "selected": False}
    entry = build_entry(card, vocab_all)
    assert "abbr={ASR&SSL}" in entry, entry      # fixed order, never SSL&ASR
    assert "booktitle=interspeech," in entry     # bare macro, not braced
    assert "{interspeech}" not in entry
    assert "journal" not in entry                # a conference is @inproceedings
    print("  ok  a completed card renders with fixed topic order and a bare macro")

    refusals = [
        ({**card, "abbr": []}, "no topic"),
        ({**card, "year": None}, "no year"),
        ({**card, "year": 2099}, "implausible year"),
        ({**card, "venue": "NoSuchVenue"}, "unknown venue"),
        ({**card, "abbr": ["NotAReal Topic"]}, "topic outside the vocabulary"),
        ({**card, "title": "unbalanced { brace in the title here"}, "unbalanced brace"),
        ({**card, "links": {"pdf": "example.com/a.pdf"}}, "link without a scheme"),
        ({**card, "links": {"arxiv": "not-an-id"}}, "arxiv that is not an id"),
    ]
    for bad, why in refusals:
        try:
            build_entry(bad, vocab_all)
        except WriteRefused:
            continue
        raise AssertionError(f"build_entry accepted a card with {why}")
    print(f"  ok  {len(refusals)} malformed cards refused before any write")

    # A URL in `arxiv` built http://arxiv.org/abs/<url> and shipped three dead
    # links before #289. It is stripped to a bare id now.
    stripped = build_entry({**card, "links": {"arxiv": "https://arxiv.org/abs/2105.01051v2"}},
                           vocab_all)
    assert "arxiv={2105.01051v2}," in stripped, stripped
    print("  ok  an arxiv URL is reduced to a bare id")

    # Splice inserts and never rewrites: every existing entry must come back
    # byte-identical, or a three-line change becomes a 4,500-line diff.
    original = BIB.read_text(encoding="utf-8")

    def entry_chunks(text: str) -> list[str]:
        return [c for c in re.split(r"\n(?=@)", text)
                if c.lstrip().startswith("@")
                and not c.lstrip().lower().startswith("@string")]

    before_chunks = entry_chunks(original)
    spliced = splice(original, [(2026, entry), (2019, entry.replace("probe2026test", "probe2019test"))])
    after_chunks = entry_chunks(spliced)
    after_set = set(after_chunks)
    assert len(after_chunks) == len(before_chunks) + 2, len(after_chunks)
    changed = [c for c in before_chunks if c not in after_set]
    assert not changed, f"{len(changed)} existing entries were modified by splice"
    years = [int(m.group(1)) if (m := re.search(r"year\s*=\s*\{?(\d{4})", c)) else 0
             for c in after_chunks]
    at = next(i for i, c in enumerate(after_chunks) if "probe2026test" in c)
    assert years[at - 1] >= 2026 >= years[at + 1], (years[at - 1], years[at + 1])
    print("  ok  splice inserts in the right year block and leaves every entry unchanged")

    assert unique_citekey("taken", {"taken"}, "A Distinctive Title Here") != "taken"
    print("  ok  a colliding citation key is given a new name")
    print("\nself-test passed")
    return 0


# ---------------------------------------------------------------------- main

def find_missing(site: list[dict], records: list[dict],
                 min_year: int) -> list[tuple[dict, tuple[float, dict] | None]]:
    """Papers on the site that papers.bib does not have.

    Each result carries an optional (score, record) pair naming the closest
    existing entry, for the band where a human has to decide.
    """
    by_key = {r["key"]: r for r in records}

    # The year filter consults the venue abbreviation too, not just a 4-digit
    # year. Without that, "Proc. ICASSP'24 (accepted)" counts as undated and
    # slips past a `year >= 2025` cutoff -- four 2023-24 papers did exactly that.
    def effective_year(entry: dict) -> int | None:
        return entry["year"] or year_from_venue(entry["rest"])

    candidates = [
        e for e in site
        if e["section"] in KEEP_SECTIONS
        and ((effective_year(e) or min_year) >= min_year)
        and hard_key(e["title"]) not in by_key
    ]

    missing = []
    for entry in candidates:
        toks = tokens(entry["title"])
        score, best = 0.0, None
        for record in records:
            value = jaccard(toks, record["tokens"])
            if value > score:
                score, best = value, record
        if score >= DUP_SKIP:
            continue
        missing.append((entry, (score, best) if score >= DUP_SUSPECT and best else None))
    return missing


def report(missing: list[tuple[dict, tuple[float, dict] | None]],
           vocab: list[str]) -> str:
    """A Markdown report of what is missing, for the weekly issue.

    The draft entry is included on purpose. Dropping the bot PR removed the
    one place a second person saw an entry before it went live; putting the
    BibTeX in the issue gives that reader back, on a phone if need be.
    """
    if not missing:
        return "Nothing is missing. `papers.bib` matches the publication list.\n"

    out = [
        f"{len(missing)} paper{'s' if len(missing) != 1 else ''} on "
        f"[Shinji's publication list]({SITE_URL}) "
        f"{'are' if len(missing) != 1 else 'is'} not in `_bibliography/papers.bib`.",
        "",
        "To add them, run:",
        "",
        "```bash",
        "python3 scripts/check_publications.py --review",
        "```",
        "",
        "The drafts below are what that tool starts from. `abbr` is left blank:"
        " it is a curation choice, so no tool guesses it.",
        "",
    ]
    for index, (entry, suspect) in enumerate(missing, 1):
        year = entry["year"] or year_from_venue(entry["rest"])
        out.append(f"### {index}. {entry['title']}")
        out.append("")
        out.append(f"- venue on the site: `{entry['rest']}`")
        out.append(f"- year: {year if year else '**not stated anywhere**'}")
        if uppercase_ratio(entry["title"]) > 0.85:
            out.append("- :warning: the title is ALL-CAPS on the site and needs"
                       " normal capitalisation")
        if suspect:
            score, other = suspect
            out.append(f"- :warning: scores {score:.2f} against `{other['citekey']}`"
                       f" (papers.bib:{other['line']}) -- check it is not the same paper")
        out.append("")
        out.append("```bibtex")
        out.append(render_stub(entry, None, vocab))
        out.append("```")
        out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fixture", type=Path, help="parse this HTML file instead of fetching")
    ap.add_argument("--save-fixture", type=Path, help="write the fetched HTML here")
    ap.add_argument("--min-year", type=int, default=MIN_YEAR)
    ap.add_argument("--report", type=Path,
                    help="write the Markdown report here instead of to stdout")
    ap.add_argument("--review", action="store_true",
                    help="open the review page and write completed entries into papers.bib")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        fixture = args.fixture or (ROOT / "scripts" / "testdata" / "publications.html.gz")
        if not fixture.exists():
            print(f"error: fixture not found: {fixture}", file=sys.stderr)
            return 1
        return selftest(fixture)

    if args.fixture:
        html = read_html(args.fixture)
    else:
        print(f"fetching {SITE_URL}", file=sys.stderr)
        html = fetch(SITE_URL).decode("utf-8", "replace")
        if args.save_fixture:
            args.save_fixture.parent.mkdir(parents=True, exist_ok=True)
            args.save_fixture.write_text(html, encoding="utf-8")

    site = scrape(html)
    records = parse_bib(BIB)
    print(f"site: {len(site)} entries | papers.bib: {len(records)} entries",
          file=sys.stderr)

    missing = find_missing(site, records, args.min_year)
    suspects = sum(1 for _, s in missing if s)
    print(f"=> {len(missing)} missing ({suspects} need a duplicate check)",
          file=sys.stderr)

    vocab = abbr_vocabulary(records)

    if args.review:
        return serve_review(build_payload(missing, records, vocab), vocab)

    text = report(missing, vocab)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
        print(f"wrote {args.report}", file=sys.stderr)
    else:
        print(text)

    # Exit 1 means "there is work to do", so the workflow can branch on it.
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
