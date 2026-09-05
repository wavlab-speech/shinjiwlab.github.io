#!/usr/bin/env python3
"""
Fetch publications from Google Scholar for each WAVLab member and save to YAML data files.

Usage:
    python3 bin/fetch_scholar.py                # fetch from Google Scholar, then enrich
    python3 bin/fetch_scholar.py --enrich-only  # re-apply papers.bib metadata, no network

Requirements:
    pip install scholarly pyyaml     (--enrich-only needs only pyyaml)

This script reads member data from _data/members.yml, fetches publications
from Google Scholar for each member with a scholar_id, and saves the results
to _data/scholar_pubs/<member_id>.yml.

Google Scholar's own metadata is poor: it sentence-cases titles ("Espnet-sds",
"Powsm", "Desta2. 5-audio"), truncates venues with an ellipsis, and reports most
published papers as "arXiv preprint arXiv:...". So every fetched record is
matched against the lab's hand-curated _bibliography/papers.bib and, when a
match is found, the curated title/venue/year/link win. Records with no match
keep their Scholar metadata.

Note: Google Scholar may block automated requests. The script exits non-zero if
it could not refresh a single member, so a blocked run fails loudly instead of
silently leaving stale data behind.
"""

import bisect
import os
import re
import sys
import time
import unicodedata
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMBERS_FILE = os.path.join(REPO_ROOT, '_data', 'members.yml')
PUBS_DIR = os.path.join(REPO_ROOT, '_data', 'scholar_pubs')
PAPERS_BIB = os.path.join(REPO_ROOT, '_bibliography', 'papers.bib')

# How many of the most recent publications to store per member. The members
# page only ever displays the 20 newest, so we keep a small buffer beyond that
# rather than hundreds of older papers (which would bloat the repo and make the
# weekly refresh diffs noisy). The true total is stored separately for the count.
KEEP_LATEST = 25

# Refuse to overwrite a member's file when the new fetch returns dramatically
# fewer publications than we already have. Google Scholar throttles the
# paginated author listing mid-way *without* raising, which yields a truncated
# but non-empty list; saving it would silently wipe most of a member's record
# and drop the count badge on the members page.
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

    Deliberately dependency-free (the GitHub Action installs only scholarly and
    pyyaml) and deliberately minimal: it understands brace-nested and quoted
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


def build_bib_index():
    """Map normalized title -> curated {title, venue, year, url} from papers.bib."""
    if not os.path.exists(PAPERS_BIB):
        print(f"  papers.bib not found at {PAPERS_BIB}; skipping enrichment")
        return BibIndex({})

    index = {}
    for fields in parse_bib(PAPERS_BIB):
        title = (fields.get('title') or '').strip()
        if not title:
            continue
        key = normalize_title(title)
        if not key or key in index:
            continue
        venue = (fields.get('abbr_publisher')
                 or fields.get('booktitle')
                 or fields.get('journal')
                 or '').strip()
        index[key] = {
            'title': clean_latex(title),
            'venue': clean_latex(venue),
            'year': (fields.get('year') or '').strip(),
            'url': bib_link(fields),
        }
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
# Google Scholar
# --------------------------------------------------------------------------

def scholar_citation_url(author_pub_id):
    """Permalink to a single publication on the author's Scholar profile.

    `author_pub_id` is already of the form "<author_id>:<publication_id>", so
    the user parameter can be derived from it rather than passed separately.
    """
    author_pub_id = (author_pub_id or '').strip()
    if ':' not in author_pub_id:
        return ''
    user = author_pub_id.split(':', 1)[0]
    if not user:
        return ''
    return ('https://scholar.google.com/citations'
            f'?view_op=view_citation&hl=en&user={user}'
            f'&citation_for_view={author_pub_id}')


def fetch_publications(scholar_id, bib_index):
    """Fetch a member's full publication list from Google Scholar (newest first).

    We read only the author's publication list (a single, paginated request)
    and use the metadata it already provides. We deliberately do NOT call
    scholarly.fill() on each publication: filling every paper issues one extra
    request per paper, which quickly triggers Google Scholar rate limiting and
    silently blocks the whole run. The list view gives us title, year, the
    'citation' string (which we use as the venue) and 'author_pub_id' (which we
    turn into a per-paper link) -- enough for the members page.

    Records are enriched from papers.bib before deduplication, so the surviving
    copy of each work carries curated metadata. Enrichment is also what lets a
    title Google elided ("Speech recognition for …") collapse together with its
    full-text twin, since both end up carrying the same curated title. Exact
    duplicates (same normalized title) are then collapsed, and the list is
    returned sorted newest-first with no cap; the caller decides how many to
    keep.
    """
    try:
        from scholarly import scholarly as _scholarly
    except ImportError:
        print("scholarly not installed. Run: pip install scholarly")
        sys.exit(1)

    print(f"  Fetching from Google Scholar: {scholar_id}")
    author = _scholarly.search_author_id(scholar_id, filled=False)
    author = _scholarly.fill(author, sections=['publications'])

    rows = []
    for pub in author.get('publications', []):
        bib = pub.get('bib', {})
        title = (bib.get('title') or '').strip()
        if not title:
            continue

        year = str(bib.get('pub_year') or '').strip()

        # 'citation' is the grey line under the title, e.g.
        # "ICASSP 2021 IEEE International Conference ..., 2021". Strip the
        # trailing year so the template's ", {{ year }}" isn't duplicated --
        # but only when those digits really are this record's own year. A blind
        # \d{4}$ also eats the tail of "arXiv preprint arXiv:2603.07534" and of
        # page ranges like "..., 1234-1245" whenever Scholar omits the year.
        venue = (bib.get('citation') or '').strip()
        if year:
            # (?<!\d) keeps "Vol 12025" intact when the record's year is 2025:
            # only a standalone trailing year is the duplicate we want gone.
            venue = re.sub(r',?\s*(?<!\d)' + re.escape(year) + r'\s*$',
                           '', venue).strip()

        rows.append(enrich({
            'title': title,
            'year': year,
            'venue': venue,
            # Prefer a direct arXiv link over Scholar's own citation page: the
            # id is right there in the venue for preprints, and it takes the
            # reader to the paper instead of to another index page. The
            # Scholar permalink is the catch-all when there is no id.
            'url': (arxiv_link_from_venue(venue)
                    or scholar_citation_url(pub.get('author_pub_id'))),
        }, bib_index))

    return sort_newest_first(dedupe(rows))


# --------------------------------------------------------------------------
# Persistence
# --------------------------------------------------------------------------

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


def write_file(member_id, total, pubs):
    os.makedirs(PUBS_DIR, exist_ok=True)
    out_file = os.path.join(PUBS_DIR, f'{member_id}.yml')
    data = {'total': total, 'pubs': pubs}
    with open(out_file, 'w', encoding='utf-8') as f:
        # safe_dump, to match the safe_load these files are read back with.
        # scholarly parses with BeautifulSoup, whose NavigableString subclasses
        # str; plain yaml.dump would serialise such a value as a
        # !!python/object node that safe_load then refuses to read, corrupting
        # the file silently. safe_dump raises at write time instead.
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True,
                       sort_keys=False)
    return out_file


def save_publications(member_id, pubs):
    """Save the member's true total plus their most recent publications.

    `pubs` is the member's full, newest-first publication list. We persist the
    real total (for the count badge) but only keep the latest KEEP_LATEST
    entries to keep the data files lean.

    Returns True if the file was written, False if the write was refused
    because the fetch looked truncated.
    """
    total = len(pubs)
    existing = read_existing(member_id)
    previous = (existing or {}).get('total') or 0
    if isinstance(previous, int) and previous and total < previous * MIN_KEEP_RATIO:
        print(f"  REFUSING to save {member_id}: {previous} -> {total} publications "
              f"(below {int(MIN_KEEP_RATIO * 100)}% of the previous total). "
              "Google Scholar most likely truncated the listing; keeping existing data.")
        return False

    out_file = write_file(member_id, total, pubs[:KEEP_LATEST])
    print(f"  Saved {min(total, KEEP_LATEST)} of {total} publications to {out_file}")
    return True


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def ensure_member_files(members):
    """Create an empty data file for any member that does not have one yet.

    Adding somebody to the lab should mean editing _data/members.yml and
    nothing else. The members page already tolerates a missing file, so this is
    housekeeping rather than a fix: it keeps _data/members.yml and
    _data/scholar_pubs/ in step, gives members with no Scholar profile a real
    file instead of a permanent gap, and means the weekly PR carries the new
    member's file along with everyone else's refresh.
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
        write_file(member_id, 0, [])
        created.append(member.get('name', member_id))
    if created:
        print("Created empty publication files for: " + ", ".join(created))
    return created


def enrich_only():
    """Re-apply papers.bib metadata to the committed YAML files. No network.

    Useful after papers.bib gains entries or fixes: it upgrades titles, venues
    and links for records already on disk without going near Google Scholar.
    `total` is left untouched, since the stored list is only the newest slice.
    """
    bib_index = build_bib_index()
    if not bib_index:
        print("No bib entries loaded; nothing to enrich.")
        return 1

    print(f"Loaded {len(bib_index)} entries from papers.bib\n")
    members = load_members()
    ensure_member_files(members)
    changed_files = 0
    changed_rows = 0
    for member in members:
        member_id = member.get('id')
        if not member_id:
            continue
        existing = read_existing(member_id)
        if not existing or not existing.get('pubs'):
            continue

        rows = existing['pubs']
        enriched = [enrich(dict(row), bib_index) for row in rows]
        delta = sum(1 for old, new in zip(rows, enriched) if old != new)
        # Enrichment can rewrite both the title and the year, so records that
        # looked distinct may now be the same work, and the file may no longer
        # be newest-first. The members page renders the stored order verbatim
        # and does not re-sort, so both have to be re-established here.
        updated = sort_newest_first(dedupe(enriched))
        merged = len(enriched) - len(updated)
        if not delta and updated == rows:
            continue

        total = existing.get('total', len(updated))
        if isinstance(total, int) and merged:
            total = max(total - merged, len(updated))
        write_file(member_id, total, updated)
        changed_files += 1
        changed_rows += delta
        note = f", merged {merged} duplicate(s)" if merged else ''
        print(f"  {member.get('name', member_id)}: "
              f"enriched {delta} of {len(rows)} records{note}")

    print(f"\nDone! Enriched {changed_rows} records across {changed_files} files.")
    return 0


def main():
    if '--enrich-only' in sys.argv[1:]:
        return enrich_only()

    members = load_members()
    bib_index = build_bib_index()
    print(f"Loaded {len(bib_index)} entries from papers.bib")
    ensure_member_files(members)
    print()

    considered = 0
    refreshed = 0
    for member in members:
        member_id = member.get('id')
        name = member.get('name', member_id)
        scholar_id = member.get('scholar_id', '')

        if not member_id:
            print(f"Skipping entry with no id: {member!r}")
            continue
        if not scholar_id:
            print(f"Skipping {name} (no scholar_id)")
            continue

        considered += 1
        print(f"Processing {name} (scholar_id: {scholar_id})")
        try:
            pubs = fetch_publications(scholar_id, bib_index)
            if pubs:
                if save_publications(member_id, pubs):
                    refreshed += 1
            else:
                # Google Scholar often soft-blocks scrapers and returns an empty
                # publication list *without* raising. Never overwrite good data
                # with nothing -- leave the existing YAML file in place.
                print(f"  No publications returned for {name}; "
                      "keeping existing data.")
        except Exception as e:
            print(f"  Error fetching publications for {name}: {e}")

        time.sleep(5)  # delay between authors

    print(f"\nRefreshed {refreshed} of {considered} members.")
    if considered and not refreshed:
        # Every single member failed. That is not a quiet no-op: it means
        # Google Scholar is blocking us (or the profile IDs are wrong) and the
        # published data is going stale. Fail the run so the scheduled workflow
        # goes red instead of reporting success with nothing to show for it.
        print("Refreshed nothing -- Google Scholar is most likely blocking this "
              "runner. Failing so the run is visible.", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
