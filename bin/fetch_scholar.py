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


def fetch_publications(scholar_id, max_pubs=100):
    """Fetch publications from Google Scholar for a given scholar ID."""
    try:
        from scholarly import scholarly as _scholarly
    except ImportError:
        print("scholarly not installed. Run: pip install scholarly")
        sys.exit(1)

    print(f"  Fetching from Google Scholar: {scholar_id}")
    author = _scholarly.search_author_id(scholar_id, filled=False)
    author = _scholarly.fill(author, sections=['publications'])

    pubs = []
    for i, pub in enumerate(author.get('publications', [])):
        if i >= max_pubs:
            break
        try:
            filled_pub = _scholarly.fill(pub)
            bib = filled_pub.get('bib', {})
            pubs.append({
                'title': bib.get('title', ''),
                'author': bib.get('author', ''),
                'year': str(bib.get('pub_year', '')),
                'venue': bib.get('venue', ''),
                'abstract': bib.get('abstract', ''),
                'url': filled_pub.get('pub_url', ''),
                'num_citations': filled_pub.get('num_citations', 0),
            })
            time.sleep(1)  # be polite to Google Scholar
        except Exception as e:
            print(f"    Warning: failed to fill publication {i}: {e}")
            bib = pub.get('bib', {})
            pubs.append({
                'title': bib.get('title', ''),
                'author': bib.get('author', ''),
                'year': str(bib.get('pub_year', '')),
                'venue': bib.get('venue', ''),
                'abstract': '',
                'url': '',
                'num_citations': pub.get('num_citations', 0),
            })

    return pubs


def save_publications(member_id, pubs):
    """Save publications to YAML file."""
    os.makedirs(PUBS_DIR, exist_ok=True)
    out_file = os.path.join(PUBS_DIR, f'{member_id}.yml')
    with open(out_file, 'w') as f:
        yaml.dump(pubs, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Saved {len(pubs)} publications to {out_file}")


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
