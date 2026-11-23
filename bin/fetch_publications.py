#!/usr/bin/env python3
"""
Build each WAVLab member's publication list and save it to
_data/member_pubs/<member_id>.yml.

The list comes from two sources:

  1. _bibliography/papers.bib, the lab's hand-curated list. A member's entries
     are the ones whose author list holds the member's full name (or a
     spelling from the member's `bib_names` in _data/members.yml).
  2. The member's public ORCID record, through the anonymous ORCID public API
     (https://pub.orcid.org/v3.0/<orcid>/works). It needs no credentials.

When a paper is in both, the papers.bib title, venue, year and link win.

Usage:
    python3 bin/fetch_publications.py             # refresh every member
    python3 bin/fetch_publications.py --selftest  # offline checks, no network

Requirements:
    pip install pyyaml
"""

import bisect
import http.client
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.request
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMBERS_FILE = os.path.join(REPO_ROOT, '_data', 'members.yml')
PAPERS_BIB = os.path.join(REPO_ROOT, '_bibliography', 'papers.bib')
# A module global, so the self-test can point it at a temporary directory.
PUBS_DIR = os.path.join(REPO_ROOT, '_data', 'member_pubs')
TESTDATA_DIR = os.path.join(REPO_ROOT, 'bin', 'testdata')

# How many of the most recent publications to store per member. The members
# page only ever displays the 20 newest, so we keep a small buffer beyond that
# rather than hundreds of older papers (which would bloat the repo and make the
# weekly refresh diffs noisy). The true total is stored separately for the count.
KEEP_LATEST = 25

# Refuse to overwrite a member's file when a refresh from the same source
# returns far fewer publications than the file holds. An ORCID record that was
# emptied or made private must not wipe a member's list. Totals from different
# sources cannot be compared, so the rule applies only when the stored `source`
# equals the new one.
MIN_KEEP_RATIO = 0.7

# Google Scholar elides long titles on the author listing page ("Speech
# recognition and understanding for …"). Those cannot be matched against
# papers.bib exactly, so they fall back to a prefix lookup. The prefix must be
# at least this many normalized characters, and must match exactly one bib
# entry, before we accept it -- a short or ambiguous prefix would silently
# attach the wrong paper's metadata.
ELLIPSIS = '…'
MIN_PREFIX_MATCH = 30


def load_members():
    with open(MEMBERS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or []


# --------------------------------------------------------------------------
# papers.bib
# --------------------------------------------------------------------------

def clean_latex(text):
    """Render a BibTeX field as the plain text a reader should see.

    papers.bib is written for LaTeX, so titles carry markup that must not reach
    the web page verbatim: brace groups protecting capitalisation ("{POWSM}"),
    en/em dashes written as "--"/"---" ("Kullback--Leibler"), escaped
    ampersands, and accents spelled as {\\'e}. Google Scholar already returns
    proper Unicode, so leaving the markup in would make the curated title look
    *worse* than the one it replaces.
    """
    if not text:
        return ''
    t = text
    # {\'e} / {\"o} / \'{e} -> combining form, then normalize to a single char.
    t = re.sub(r"\{\\([`'\"^~=.])\{?([A-Za-z])\}?\}", r'\2\1', t)
    t = re.sub(r"\\([`'\"^~=.])\{([A-Za-z])\}", r'\2\1', t)
    accents = {"'": '\u0301', '`': '\u0300', '"': '\u0308',
               '^': '\u0302', '~': '\u0303', '=': '\u0304', '.': '\u0307'}
    t = re.sub(r"([A-Za-z])([`'\"^~=.])",
               lambda m: m.group(1) + accents[m.group(2)]
               if m.group(2) in accents else m.group(0), t)
    # Command-form accents: {\u{g}} (breve), \v{s} (caron), \c{c} (cedilla)...
    commands = {'u': '\u0306', 'v': '\u030c', 'c': '\u0327',
                'H': '\u030b', 'k': '\u0328', 'r': '\u030a', 'b': '\u0331'}
    t = re.sub(r'\{?\\([uvcHkrb])\{([A-Za-z])\}\}?',
               lambda m: m.group(2) + commands[m.group(1)], t)
    t = unicodedata.normalize('NFC', t)
    t = t.replace('\\&', '&').replace('\\%', '%').replace('\\$', '$')
    # Any remaining \command{argument} keeps the argument (\textbf, \emph, ...).
    t = re.sub(r'\\[a-zA-Z]+\s*\{([^{}]*)\}', r'\1', t)
    t = t.replace('{', '').replace('}', '')
    t = t.replace('---', '\u2014').replace('--', '\u2013')
    return re.sub(r'\s+', ' ', t).strip()


def normalize_title(title):
    """Collapse a title to a comparison key.

    Google Scholar mangles titles in ways that are purely cosmetic:
    "DeSTA2.5-Audio" comes back as "Desta2. 5-audio", "ESPnet-SDS" as
    "Espnet-sds", "POWSM" as "Powsm". BibTeX, meanwhile, wraps case-sensitive
    fragments in braces ("{POWSM}: A Phonetic...") and spells accents as {\\'e}.
    Folding accents to their base letter, then dropping case and every
    non-alphanumeric character, makes all of those variants collapse onto the
    same key, so an exact dictionary lookup is enough -- no fuzzy matching,
    which would risk merging genuinely different papers.
    """
    t = clean_latex(title).lower().replace('&', ' and ')
    # Decompose accents (é -> e + U+0301) and drop the combining marks, so a
    # Scholar title with real Unicode matches a bib entry written in LaTeX.
    t = ''.join(c for c in unicodedata.normalize('NFKD', t)
                if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '', t)


def _match_brace(text, start):
    """Index just past the '}' closing the '{' at `start`, honouring escapes."""
    depth, cur = 1, start + 1
    while cur < len(text) and depth:
        ch = text[cur]
        if ch == '\\':          # \{ and \} are literal characters, not nesting
            cur += 2
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        cur += 1
    return cur


def _parse_fields(body):
    """Read `name = value` pairs from an entry body, left to right.

    Scanning sequentially -- rather than regexing the whole body for `\\w+\\s*=`
    -- is what keeps an '=' *inside* a value from being mistaken for a new
    field. A url such as {https://x.org/?title=foo} would otherwise register a
    bogus `title` and clobber the real one.
    """
    fields = {}
    pos = 0
    while pos < len(body):
        field = re.compile(r'(\w+)\s*=\s*').match(body, pos) \
            or re.compile(r'[\s,]*(\w+)\s*=\s*').match(body, pos)
        if not field:
            # Skip to just after the next comma at depth 0.
            depth = 0
            while pos < len(body):
                ch = body[pos]
                if ch == '\\':
                    pos += 2
                    continue
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                elif ch == ',' and depth <= 0:
                    pos += 1
                    break
                pos += 1
            else:
                break
            continue

        name = field.group(1).lower()
        start = field.end()
        if start >= len(body):
            break
        if body[start] == '{':
            end = _match_brace(body, start)
            fields[name] = body[start + 1:end - 1]
            pos = end
        elif body[start] == '"':
            end = start + 1
            while end < len(body):
                if body[end] == '\\':
                    end += 2
                    continue
                if body[end] == '"':
                    break
                end += 1
            fields[name] = body[start + 1:end]
            pos = min(end + 1, len(body))
        else:
            end = start
            while end < len(body) and body[end] not in ',\n':
                end += 1
            fields[name] = body[start:end].strip()
            pos = end
    return fields


def parse_bib(path):
    """Parse a BibTeX file into a list of field dicts.

    Deliberately dependency-free (the GitHub Action installs only pyyaml) and
    deliberately minimal: it understands brace-nested and quoted
    values, escaped braces, and skips @string/@comment/@preamble. That is all
    papers.bib uses.
    """
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()

    entries = []
    pos = 0
    while True:
        at = text.find('@', pos)
        if at == -1:
            break
        header = re.match(r'@(\w+)\s*\{\s*([^,\s}]*)\s*,', text[at:])
        if not header:
            pos = at + 1
            continue

        open_brace = text.index('{', at)
        end = _match_brace(text, open_brace)
        body = text[open_brace + 1:end - 1]
        pos = max(end, at + 1)

        entry_type = header.group(1).lower()
        if entry_type in ('string', 'comment', 'preamble'):
            continue

        fields = _parse_fields(body)
        fields['_key'] = header.group(2)
        fields['_type'] = entry_type
        entries.append(fields)
    return entries


def _as_url(value, template):
    """Turn a bib field into an http(s) URL.

    papers.bib is inconsistent: `arxiv` is documented as a bare ID but at least
    one entry holds a full IEEE URL, and `doi` appears both bare and as a
    doi.org URL. Accept either shape; anything else is templated.
    """
    value = (value or '').strip()
    if not value:
        return ''
    if value.startswith('http://') or value.startswith('https://'):
        return value
    return template.format(value)


def bib_link(fields):
    """Best available link for a bib entry, or '' if it has none.

    Order mirrors the convention in CLAUDE.md: the official paper page first,
    then an open-access PDF, then arXiv, then the DOI.
    """
    for name, template in (
        ('html', '{0}'),
        ('pdf', '{0}'),
        ('arxiv', 'https://arxiv.org/abs/{0}'),
        ('doi', 'https://doi.org/{0}'),
    ):
        url = _as_url(fields.get(name), template)
        if url.startswith('http://') or url.startswith('https://'):
            return url
    return ''


class BibIndex:
    """Curated metadata from papers.bib, looked up by title.

    Exact normalized match first. Titles that Google Scholar elided fall back to
    a prefix search, which is accepted only when it is long enough to be
    meaningful and lands on exactly one entry.
    """

    def __init__(self, entries):
        self._exact = entries
        self._keys = sorted(entries)

    def __len__(self):
        return len(self._exact)

    def lookup(self, title):
        key = normalize_title(title)
        if not key:
            return None
        hit = self._exact.get(key)
        if hit:
            return hit
        if ELLIPSIS not in title and not title.rstrip().endswith('...'):
            return None
        if len(key) < MIN_PREFIX_MATCH:
            return None

        start = bisect.bisect_left(self._keys, key)
        matches = []
        while start < len(self._keys) and self._keys[start].startswith(key):
            matches.append(self._keys[start])
            if len(matches) > 1:
                return None  # ambiguous prefix; refuse to guess
            start += 1
        return self._exact[matches[0]] if matches else None


def bib_row(fields):
    """Curated {title, venue, year, url} for one papers.bib entry."""
    venue = (fields.get('abbr_publisher')
             or fields.get('booktitle')
             or fields.get('journal')
             or '').strip()
    return {
        'title': clean_latex((fields.get('title') or '').strip()),
        'venue': clean_latex(venue),
        'year': (fields.get('year') or '').strip(),
        'url': bib_link(fields),
    }


def build_bib_index(entries):
    """Map normalized title -> curated row, for parsed papers.bib entries.

    The first entry with a given title wins.
    """
    index = {}
    for fields in entries:
        title = (fields.get('title') or '').strip()
        if not title:
            continue
        key = normalize_title(title)
        if not key or key in index:
            continue
        index[key] = bib_row(fields)
    return BibIndex(index)


# Google Scholar reports most preprints as "arXiv preprint arXiv:2505.14874".
# When papers.bib supplies a better venue but no link, that identifier is the
# only route back to the paper, so recover it before the venue is overwritten.
ARXIV_IN_VENUE = re.compile(r'arxiv[:\s]\s*(\d{4}\.\d{4,5}(?:v\d+)?)', re.I)


def arxiv_link_from_venue(venue):
    match = ARXIV_IN_VENUE.search(venue or '')
    return f'https://arxiv.org/abs/{match.group(1)}' if match else ''


def enrich(row, bib_index):
    """Replace Scholar metadata with the curated version when papers.bib has it.

    Returns a new row; the Scholar link is kept as a fallback when the bib entry
    carries no link of its own.
    """
    match = bib_index.lookup(row['title'])
    if not match:
        return row
    return {
        'title': match['title'],
        'year': match['year'] or row['year'],
        'venue': match['venue'] or row['venue'],
        # Curated link first, then whatever link the record already had, then
        # the arXiv id we are about to drop from the venue.
        'url': (match['url'] or row['url']
                or arxiv_link_from_venue(row['venue'])),
    }


def dedupe(rows):
    """Collapse records that describe the same work, keeping the newest year.

    Google Scholar profiles routinely list the same work several times
    (preprint + published version, or an elided title alongside its full form),
    which inflates the count. Matching is on the normalized title only. We
    deliberately do NOT fuzzy-match: titles like "Findings of the IWSLT
    2023/2024 ..." are genuinely different annual papers and must never merge.
    """
    deduped = {}
    order = []
    for index, row in enumerate(rows):
        # A title of pure punctuation or non-Latin script normalizes to '';
        # key it by its raw text rather than discarding the record.
        key = normalize_title(row['title']) or f"raw:{row['title'].strip()}"
        prev = deduped.get(key)
        if prev is None:
            order.append(key)
            deduped[key] = row
        elif (row['year'].isdigit()
                and (not prev['year'].isdigit() or row['year'] > prev['year'])):
            deduped[key] = row
    return [deduped[k] for k in order]


def sort_newest_first(rows):
    """Newest first; entries with no usable year sort to the end.

    Python's sort is stable and stays stable under reverse=True, so records
    sharing a year keep the order Google Scholar listed them in. The members
    page renders the stored order as-is, which is what makes the displayed
    "20 most recent" actually the 20 most recent.
    """
    return sorted(rows, key=lambda r: (r['year'].isdigit(), r['year']),
                  reverse=True)


# --------------------------------------------------------------------------
# A member's papers in papers.bib
# --------------------------------------------------------------------------

def split_authors(field):
    """Split a BibTeX author field into names. BibTeX separates names with "and"."""
    text = ' '.join((field or '').split())
    if not text:
        return []
    return [name.strip() for name in re.split(r'\s+and\s+', text) if name.strip()]


def name_key(name):
    """Collapse a person's name to a comparison key.

    papers.bib writes a name both as "Shinji Watanabe" and as "Watanabe,
    Shinji", and members.yml adds nicknames ("Ting (Justin) Jiang"). Drop the
    nickname, put "Last, First" in "First Last" order, fold accents, and keep
    only the letters. The key is the WHOLE name: many authors share a surname
    (papers.bib has 103 with the surname Li), so a surname alone never matches.
    """
    text = re.sub(r'\([^)]*\)', ' ', clean_latex(name or ''))
    if text.count(',') == 1:
        last, first = text.split(',')
        text = f'{first} {last}'
    text = ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))
    return re.sub(r'[^a-z]', '', text.lower())


def member_name_keys(member):
    """Name keys for a member: the name, plus each spelling in `bib_names`."""
    names = [member.get('name', '')] + list(member.get('bib_names') or [])
    return {key for key in (name_key(n) for n in names) if key}


def bib_rows_for_member(entries, keys):
    """Curated rows for every papers.bib entry that lists the member as an author."""
    rows = []
    for fields in entries:
        if not (fields.get('title') or '').strip():
            continue
        if any(name_key(a) in keys for a in split_authors(fields.get('author', ''))):
            rows.append(bib_row(fields))
    return rows



# --------------------------------------------------------------------------
# ORCID
# --------------------------------------------------------------------------

# ORCID work types that are not publications. Everything else is kept,
# including "other": on Shinji's record every "other" work is an arXiv preprint
# imported from Scopus, and 20 of his 25 newest papers are among them.
EXCLUDED_TYPES = {
    'data-set', 'software', 'patent', 'lecture-speech',
    'supervised-student-publication', 'website', 'physical-object',
    'research-technique', 'spin-off-company', 'standards-and-policy',
    'technical-standard',
}

ORCID_ID = re.compile(r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$')


def normalize_orcid(value):
    """The bare ORCID iD in `value`, or None when `value` is not a valid iD.

    Accepts "0000-0002-5970-8631" and "https://orcid.org/0000-0002-5970-8631"
    (http:// too), with spaces around it and a lower-case check digit "x".
    """
    text = str(value or '').strip()
    text = re.sub(r'^https?://orcid\.org/', '', text, flags=re.I).strip().upper()
    return text if ORCID_ID.match(text) else None


def _value(node, *path):
    """Follow `path` through nested dicts. ORCID writes null for missing parts."""
    for key in path:
        node = (node or {}).get(key)
    return node


def _orcid_link(work):
    """A DOI link if the work has a DOI, else the work's own URL, else ''."""
    for ext in _value(work, 'external-ids', 'external-id') or []:
        if (ext or {}).get('external-id-type') != 'doi':
            continue
        # The value is usually a bare DOI, but may already carry a resolver
        # prefix; strip it so the link is not doubled.
        doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:)', '',
                     (ext.get('external-id-value') or '').strip(), flags=re.I)
        if doi:
            return 'https://doi.org/' + doi
    url = (_value(work, 'url', 'value') or '').strip()
    return url if url.startswith(('http://', 'https://')) else ''


def parse_orcid_works(data):
    """Rows {title, year, venue, url} from an ORCID /works response.

    ORCID groups the copies of one work that different sources added; the first
    summary of each group stands for the work.
    """
    rows = []
    for group in (data or {}).get('group') or []:
        summaries = (group or {}).get('work-summary') or []
        if not summaries:
            continue
        work = summaries[0] or {}
        if work.get('type') in EXCLUDED_TYPES:
            continue
        title = (_value(work, 'title', 'title', 'value') or '').strip()
        if not title:
            continue
        venue = re.sub(r'arxiv', 'arXiv',
                       (_value(work, 'journal-title', 'value') or '').strip(), flags=re.I)
        rows.append({
            'title': title,
            'year': str(_value(work, 'publication-date', 'year', 'value') or '').strip(),
            'venue': venue,
            'url': _orcid_link(work),
        })
    return rows


# --------------------------------------------------------------------------
# Fetch, merge and save
# --------------------------------------------------------------------------

# A generic client name. It identifies the site, and carries no person's
# contact details.
USER_AGENT = 'wavlab-site-publications/1.0 (+https://github.com/wavlab-speech/shinjiwlab.github.io)'
ORCID_WORKS_URL = 'https://pub.orcid.org/v3.0/{orcid}/works'


class OrcidError(Exception):
    """An ORCID request failed: an HTTP error, no connection, a timeout, or bad JSON."""


class InvalidOrcid(ValueError):
    """A member's `orcid` value is not a valid ORCID iD."""


def fetch_orcid_works(orcid, opener=urllib.request.urlopen, timeout=30.0):
    """The public /works response for one ORCID iD, as a dict.

    Anonymous public API: no credentials. Raises OrcidError on any failure.
    """
    req = urllib.request.Request(
        ORCID_WORKS_URL.format(orcid=orcid),
        headers={'Accept': 'application/json', 'User-Agent': USER_AGENT})
    try:
        with opener(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:          # before URLError: a subclass
        raise OrcidError(f'HTTP {exc.code}') from exc
    except (OSError, socket.timeout, http.client.HTTPException) as exc:
        # URLError, TimeoutError and dropped connections are all OSError.
        raise OrcidError(f'{type(exc).__name__}: {exc}') from exc
    except ValueError as exc:                       # JSONDecodeError, UnicodeDecodeError
        raise OrcidError(f'bad JSON: {exc}') from exc
    if not isinstance(data, dict):
        raise OrcidError('bad JSON: the response is not an object')
    return data


def merge_rows(orcid_rows, bib_rows, bib_index):
    """ORCID rows corrected from papers.bib, plus the papers.bib rows ORCID lacks.

    The ORCID rows go first, so when dedupe meets a paper twice with the same
    year it keeps the enriched ORCID row, which already carries the papers.bib
    title, venue and link.
    """
    enriched = [enrich(dict(row), bib_index) for row in orcid_rows]
    return sort_newest_first(dedupe(enriched + list(bib_rows)))


def member_rows(member, entries, bib_index, fetch=fetch_orcid_works):
    """(source, full newest-first list) for one member.

    Raises InvalidOrcid when `orcid` is present but not a valid iD, and
    OrcidError when the ORCID request fails.
    """
    bib_rows = bib_rows_for_member(entries, member_name_keys(member))
    if 'orcid' not in member:
        return 'papers.bib', sort_newest_first(dedupe(bib_rows))
    orcid = normalize_orcid(member.get('orcid'))
    if orcid is None:
        raise InvalidOrcid(f"orcid {member.get('orcid')!r} is not a valid ORCID iD")
    works = parse_orcid_works(fetch(orcid))
    return 'papers.bib+orcid', merge_rows(works, bib_rows, bib_index)


def read_existing(member_id):
    out_file = os.path.join(PUBS_DIR, f'{member_id}.yml')
    if not os.path.exists(out_file):
        return None
    try:
        with open(out_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or None
    except (OSError, yaml.YAMLError) as exc:
        print(f"  Could not read {out_file}: {exc}")
        return None


def write_file(member_id, source, total, pubs):
    os.makedirs(PUBS_DIR, exist_ok=True)
    out_file = os.path.join(PUBS_DIR, f'{member_id}.yml')
    data = {'source': source, 'total': total, 'pubs': pubs}
    with open(out_file, 'w', encoding='utf-8') as f:
        # safe_dump, to match the safe_load these files are read back with.
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True,
                       sort_keys=False)
    return out_file


def save_publications(member_id, source, pubs):
    """Save the member's total and newest KEEP_LATEST publications.

    Returns False, and writes nothing, when the stored file has the same source
    and the new total is below MIN_KEEP_RATIO of the stored total. A file from
    another source (or from the Google Scholar period, which has no `source`)
    is replaced.
    """
    total = len(pubs)
    existing = read_existing(member_id) or {}
    previous = existing.get('total') or 0
    if (existing.get('source') == source and isinstance(previous, int) and previous
            and total < previous * MIN_KEEP_RATIO):
        print(f"  REFUSING to save {member_id}: {previous} -> {total} publications "
              f"(below {int(MIN_KEEP_RATIO * 100)}% of the stored total from {source}). "
              "Keeping the existing data.")
        return False
    out_file = write_file(member_id, source, total, pubs[:KEEP_LATEST])
    print(f"  Saved {min(total, KEEP_LATEST)} of {total} publications to {out_file}")
    return True


def ensure_member_files(members):
    """Create an empty data file for any member that does not have one yet.

    Adding somebody to the lab should mean editing _data/members.yml and
    nothing else. The members page already tolerates a missing file; this keeps
    _data/members.yml and _data/member_pubs/ in step, and means the weekly PR
    carries the new member's file along with everyone else's refresh.
    """
    os.makedirs(PUBS_DIR, exist_ok=True)
    created = []
    for member in members:
        member_id = member.get('id')
        if not member_id:
            print(f"  Skipping entry with no id: {member!r}")
            continue
        if os.path.exists(os.path.join(PUBS_DIR, f'{member_id}.yml')):
            continue
        write_file(member_id, 'papers.bib', 0, [])
        created.append(member.get('name', member_id))
    if created:
        print("Created empty publication files for: " + ", ".join(created))
    return created


def refresh_member(member, entries, bib_index, fetch=fetch_orcid_works):
    """Refresh one member's file.

    Returns 'saved', 'refused', 'orcid_failed' or 'invalid_orcid'. The last two
    change no file.
    """
    try:
        source, rows = member_rows(member, entries, bib_index, fetch=fetch)
    except InvalidOrcid as exc:
        print(f"  Not changed: {exc}. Write the bare iD, for example 0000-0002-5970-8631.")
        return 'invalid_orcid'
    except OrcidError as exc:
        print(f"  Not changed: the ORCID request failed ({exc}).")
        return 'orcid_failed'
    return 'saved' if save_publications(member['id'], source, rows) else 'refused'


def exit_status(orcid_attempts, orcid_failures):
    """1 only when the run sent ORCID requests and every one of them failed."""
    return 1 if orcid_attempts > 0 and orcid_failures == orcid_attempts else 0

# --------------------------------------------------------------------------
# Self-test and entry point
# --------------------------------------------------------------------------

_RESULTS = []


def check(label, ok):
    """Record one self-test result and print it."""
    _RESULTS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'} {label}")


def selftest():
    """Run every self-test check. No network."""
    del _RESULTS[:]

    # papers.bib author matching
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
    # A name with two or more commas is a list that uses commas instead of
    # "and", unless one comma part is a BibTeX suffix ("von Last, Jr, First").
    SUFFIXES = {'jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv'}
    bad = [e['_key'] for e in real for a in split_authors(e.get('author', ''))
           if a.count(',') >= 2 and not ({p.strip().lower() for p in a.split(',')} & SUFFIXES)]
    check('papers.bib separates authors with "and"', bad == [])
    if bad:
        print('    fix the author field of: ' + ', '.join(sorted(set(bad))))

    # ORCID works, from the checked-in sample record
    sample = json.load(open(os.path.join(TESTDATA_DIR, 'orcid_works_sample.json'), encoding='utf-8'))
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

    # Fetch, merge, guard and save. Writes go to a temporary directory.
    def fake_fetch(works):
        return lambda orcid, **kw: works

    def failing_fetch(orcid, **kw):
        raise OrcidError('HTTP 503')

    def opener_429(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 429, 'Too Many Requests', {}, None)

    global PUBS_DIR
    saved_pubs_dir, PUBS_DIR = PUBS_DIR, tempfile.mkdtemp()
    try:
        index = build_bib_index([{'title': 'Shared Paper', 'abbr_publisher': 'ICASSP',
                                  'year': '2025', 'author': 'Shinji Watanabe'}])
        merged = merge_rows([{'title': 'shared paper', 'venue': 'arXiv', 'year': '2025', 'url': ''},
                             {'title': 'Dup Title', 'venue': 'arXiv', 'year': '2024', 'url': ''},
                             {'title': 'Dup Title', 'venue': 'Interspeech', 'year': '2025', 'url': ''}],
                            [{'title': 'Shared Paper', 'venue': 'ICASSP', 'year': '2025', 'url': ''},
                             {'title': 'Bib Only', 'venue': 'SLT', 'year': '2023', 'url': ''}], index)
        check('merge: bib metadata wins', ('Shared Paper', 'ICASSP') in [(r['title'], r['venue']) for r in merged])
        check('merge: preprint and published collapse to the newest',
              [r['year'] for r in merged if r['title'] == 'Dup Title'] == ['2025'])
        check('merge: bib-only paper is added', 'Bib Only' in [r['title'] for r in merged])
        try:
            fetch_orcid_works('0000-0002-5970-8631', opener=opener_429)
            got = False
        except OrcidError:
            got = True
        check('HTTP 429 raises OrcidError', got)
        m = {'id': 'm1', 'name': 'Shinji Watanabe', 'orcid': '0000-0002-5970-8631'}
        write_file('m1', 'papers.bib+orcid', 100, [])
        check('same source, big drop is refused',
              refresh_member(m, [], index, fetch=fake_fetch({'group': []})) == 'refused'
              and read_existing('m1')['total'] == 100)
        write_file('m1', 'papers.bib+orcid', 100, [])
        check('ORCID failure keeps the file',
              refresh_member(m, [], index, fetch=failing_fetch) == 'orcid_failed'
              and read_existing('m1')['total'] == 100)
        check('invalid orcid keeps the file',
              refresh_member(dict(m, orcid='0000-12'), [], index, fetch=failing_fetch) == 'invalid_orcid'
              and read_existing('m1')['total'] == 100)
        with open(os.path.join(PUBS_DIR, 'm2.yml'), 'w', encoding='utf-8') as f:
            yaml.safe_dump({'total': 855, 'pubs': []}, f)       # a file from the Google Scholar period
        check('file without source is replaced',
              save_publications('m2', 'papers.bib+orcid', [{'title': 'T', 'venue': '', 'year': '2025', 'url': ''}])
              and read_existing('m2')['source'] == 'papers.bib+orcid')
        write_file('m3', 'papers.bib', 10, [])
        check('a different source is replaced',
              save_publications('m3', 'papers.bib+orcid', [{'title': 'T', 'venue': '', 'year': '2025', 'url': ''}]))
        check('exit status', (exit_status(3, 3), exit_status(3, 2), exit_status(0, 0)) == (1, 0, 0))
    finally:
        shutil.rmtree(PUBS_DIR, ignore_errors=True)
        PUBS_DIR = saved_pubs_dir

    passed = sum(_RESULTS)
    print(f"\n{passed}/{len(_RESULTS)} self-test checks pass")
    return 0 if passed == len(_RESULTS) else 1


def main(argv):
    if '--selftest' in argv:
        return selftest()

    members = load_members()
    entries = parse_bib(PAPERS_BIB)
    bib_index = build_bib_index(entries)
    print(f"Loaded {len(entries)} entries from papers.bib")
    ensure_member_files(members)
    print()

    considered = refreshed = attempts = failures = 0
    for member in members:
        member_id = member.get('id')
        if not member_id:
            continue
        considered += 1
        has_orcid = 'orcid' in member
        print(f"{member.get('name', member_id)} "
              f"({'orcid ' + str(member.get('orcid')) if has_orcid else 'papers.bib only'})")
        status = refresh_member(member, entries, bib_index)
        refreshed += status == 'saved'
        if has_orcid and status != 'invalid_orcid':
            attempts += 1
            failures += status == 'orcid_failed'
            time.sleep(1)        # stay far below the public API's rate limit

    print(f"\nRefreshed {refreshed} of {considered} members ({failures} ORCID failures).")
    status = exit_status(attempts, failures)
    if status:
        print("Every ORCID request failed. ORCID may be down, or its API changed. "
              "No file was changed for those members.", file=sys.stderr)
    return status


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
