#!/usr/bin/env python3
"""
Fetch publications from Google Scholar for each WAVLab member and save to YAML data files.

Usage:
    python3 bin/fetch_scholar.py

Requirements:
    pip install scholarly pyyaml

This script reads member data from _data/members.yml, fetches publications
from Google Scholar for each member with a scholar_id, and saves the results
to _data/scholar_pubs/<member_id>.yml.

Note: Google Scholar may block automated requests. The script includes retry
logic and delays to handle rate limiting. If blocked, try again later or use
a proxy.
"""

import os
import sys
import time
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMBERS_FILE = os.path.join(REPO_ROOT, '_data', 'members.yml')
PUBS_DIR = os.path.join(REPO_ROOT, '_data', 'scholar_pubs')


def load_members():
    with open(MEMBERS_FILE, 'r') as f:
        return yaml.safe_load(f)


# How many of the most recent publications to store per member. The members
# page only ever displays the 20 newest, so we keep a small buffer beyond that
# rather than hundreds of older papers (which would bloat the repo and make the
# weekly refresh diffs noisy). The true total is stored separately for the count.
KEEP_LATEST = 25


def fetch_publications(scholar_id):
    """Fetch a member's full publication list from Google Scholar (newest first).

    We read only the author's publication list (a single, paginated request)
    and use the metadata it already provides. We deliberately do NOT call
    scholarly.fill() on each publication: filling every paper issues one extra
    request per paper, which quickly triggers Google Scholar rate limiting and
    silently blocks the whole run. The list view gives us title, year and the
    'citation' string (which we use as the venue) -- enough for the members
    page. Exact duplicates (same normalized title) are collapsed before the
    list is returned, sorted newest-first (no cap); the caller decides how many
    to keep.
    """
    import re

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
        title = bib.get('title') or ''
        if not title:
            continue
        # 'citation' is the grey line under the title, e.g.
        # "ICASSP 2021 IEEE International Conference ..., 2021"; drop the
        # trailing year so the template's ", {{ year }}" isn't duplicated.
        citation = bib.get('citation') or ''
        venue = re.sub(r',?\s*\d{4}\s*$', '', citation).strip()
        rows.append({
            'title': title,
            'year': str(bib.get('pub_year') or ''),
            'venue': venue,
            'url': '',
        })

    # Google Scholar profiles routinely list the same work several times
    # (preprint + published version, or minor title variants), which inflates
    # the count. Collapse exact duplicates after case/punctuation-insensitive
    # normalization, keeping the newest-year copy of each. We deliberately do
    # NOT fuzzy-match: titles like "Findings of the IWSLT 2023/2024 ..." are
    # genuinely different annual papers and must never be merged.
    deduped = {}
    for r in rows:
        key = re.sub(r'[^a-z0-9]+', ' ', r['title'].lower()).strip()
        if not key:
            continue
        prev = deduped.get(key)
        if (prev is None
                or (r['year'].isdigit()
                    and (not prev['year'].isdigit() or r['year'] > prev['year']))):
            deduped[key] = r
    rows = list(deduped.values())

    # Newest first; entries with no usable year sort to the end.
    rows.sort(key=lambda r: (r['year'].isdigit(), r['year']), reverse=True)
    return rows


def save_publications(member_id, pubs):
    """Save the member's true total plus their most recent publications.

    `pubs` is the member's full, newest-first publication list. We persist the
    real total (for the count badge) but only keep the latest KEEP_LATEST
    entries to keep the data files lean.
    """
    os.makedirs(PUBS_DIR, exist_ok=True)
    out_file = os.path.join(PUBS_DIR, f'{member_id}.yml')
    data = {'total': len(pubs), 'pubs': pubs[:KEEP_LATEST]}
    with open(out_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Saved {len(data['pubs'])} of {data['total']} publications to {out_file}")


def main():
    members = load_members()
    os.makedirs(PUBS_DIR, exist_ok=True)

    for member in members:
        member_id = member['id']
        name = member['name']
        scholar_id = member.get('scholar_id', '')

        if not scholar_id:
            print(f"Skipping {name} (no scholar_id)")
            continue

        print(f"Processing {name} (scholar_id: {scholar_id})")
        try:
            pubs = fetch_publications(scholar_id)
            if pubs:
                save_publications(member_id, pubs)
            else:
                # Google Scholar often soft-blocks scrapers and returns an empty
                # publication list *without* raising. Never overwrite good data
                # with nothing — leave the existing YAML file in place.
                print(f"  No publications returned for {name}; "
                      "keeping existing data.")
        except Exception as e:
            print(f"  Error fetching publications for {name}: {e}")

        time.sleep(5)  # delay between authors

    print("\nDone!")


if __name__ == '__main__':
    main()
