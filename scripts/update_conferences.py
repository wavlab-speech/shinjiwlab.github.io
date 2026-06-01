#!/usr/bin/env python3
"""Refresh _data/conferences.yml deadline/date fields from ccfddl/ccf-deadlines.

Only entries that carry a ``ccfddl:`` key (e.g. ``ccfddl: CG/icassp``) are
touched. Identity / curation fields (name, acronym, ccfddl) are
preserved; the script overwrites only the volatile fields:
year, abstract_deadline, deadline, utc_offset, start, end, place, url, note.

Entries without ``ccfddl:`` (e.g. ARR) are left untouched for manual
maintenance.

For each tracked conference the script picks the *next upcoming* edition (the
soonest deadline still in the future); if every deadline has passed it falls
back to the latest available year.

Run from anywhere; paths are resolved relative to this file. Intended for the
scheduled GitHub Action, which opens a PR with the diff for human review.

Dependencies: ruamel.yaml  (pip install ruamel.yaml)
"""
from __future__ import annotations

import datetime as dt
import re
import sys
import urllib.request
from pathlib import Path

from ruamel.yaml import YAML

RAW_BASE = "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/"
DATA_FILE = Path(__file__).resolve().parent.parent / "_data" / "conferences.yml"

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}
# also accept 3-letter abbreviations (jan, feb, ...) and "sept"
_MONTHS.update({name[:3]: num for name, num in list(_MONTHS.items())})
_MONTHS["sept"] = 9

# Canonical key order and quoting for deterministic emission (clean PR diffs).
_KEY_ORDER = [
    "name", "acronym", "year", "ccfddl",
    "abstract_deadline", "deadline", "utc_offset",
    "start", "end", "place", "url", "note",
]
_QUOTED_KEYS = {"place", "note"}

yaml = YAML(typ="safe")


def fetch(path: str):
    """Load a ccfddl conference YAML file (e.g. 'CG/icassp')."""
    url = f"{RAW_BASE}{path}.yml"
    req = urllib.request.Request(url, headers={"User-Agent": "wavlab-conf-bot"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return yaml.load(resp.read().decode("utf-8"))


def parse_deadline(value: str | None) -> dt.datetime | None:
    if not value or value == "TBD":
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2})", str(value))
    if not m:
        return None
    y, mo, d, h, mi = (int(x) for x in m.groups())
    try:
        return dt.datetime(y, mo, d, h, mi)
    except ValueError:
        return None


def fmt_deadline(value: str | None) -> str | None:
    """'YYYY-MM-DD HH:MM:SS' -> 'YYYY-MM-DD HH:MM' (drop seconds); None if TBD."""
    if not value or value == "TBD":
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})", str(value))
    return f"{m.group(1)} {m.group(2)}" if m else None


def parse_date_range(value: str | None):
    """Parse ccfddl 'date' strings into (start_iso, end_iso).

    Handles e.g. 'May 16-21, 2027', 'September 27 - October 1, 2026',
    'May 01-05, 2026', 'December 6, 2026'. Returns (None, None) on failure.
    """
    if not value:
        return None, None
    m = re.match(
        r"^\s*([A-Za-z]+)\s+(\d{1,2})"          # start month + day
        r"(?:\s*-\s*(?:([A-Za-z]+)\s+)?(\d{1,2}))?"  # optional end (month?) day
        r"\s*,\s*(\d{4})\s*$",                  # year
        str(value),
    )
    if not m:
        return None, None
    mon1, day1, mon2, day2, year = m.groups()
    start_mo = _MONTHS.get(mon1.lower())
    if not start_mo:
        return None, None
    year = int(year)
    start_day = int(day1)
    if day2 is None:                       # single-day conference
        end_mo, end_day = start_mo, start_day
    else:
        end_mo = _MONTHS.get(mon2.lower(), start_mo) if mon2 else start_mo
        end_day = int(day2)
    start_year = end_year = year
    if end_mo < start_mo:                  # crosses the new year (e.g. Dec-Jan)
        end_year = year + 1
    try:
        start = dt.date(start_year, start_mo, start_day)
        end = dt.date(end_year, end_mo, end_day)
    except ValueError:
        return None, None
    return start.isoformat(), end.isoformat()


def tz_to_offset(tz: str | None):
    """'AoE'->-12, 'UTC'->0, 'UTC-7'->-7, 'UTC+8'->8; None if unrecognized."""
    if not tz or tz == "AoE":
        return -12
    m = re.match(r"^UTC([+-]\d+)?$", tz)
    if not m:
        return None
    return int(m.group(1)) if m.group(1) else 0


def pick_edition(confs):
    """Pick the soonest future deadline; else the latest year."""
    now = dt.datetime.utcnow()
    parsed = []
    for conf in confs:
        timeline = (conf.get("timeline") or [{}])[0]
        deadline = parse_deadline(timeline.get("deadline"))
        parsed.append((deadline, int(conf.get("year", 0)), conf))
    future = [p for p in parsed if p[0] and p[0] >= now]
    if future:
        return min(future, key=lambda p: p[0])[2]
    return max(parsed, key=lambda p: p[1])[2]


def update_entry(entry) -> str:
    doc = fetch(entry["ccfddl"])
    meta = doc[0]
    conf = pick_edition(meta["confs"])
    timeline = (conf.get("timeline") or [{}])[0]

    entry["year"] = int(conf["year"])

    deadline = fmt_deadline(timeline.get("deadline"))
    note_bits = []
    if deadline:
        entry["deadline"] = deadline
    else:
        note_bits.append("Next deadline TBD on ccfddl — verify on the official site.")

    abstract = fmt_deadline(timeline.get("abstract_deadline"))
    if abstract:
        entry["abstract_deadline"] = abstract
    elif "abstract_deadline" in entry:
        del entry["abstract_deadline"]

    offset = tz_to_offset(conf.get("timezone"))
    if offset is None or offset == -12:   # -12 / AoE is our default -> omit key
        if "utc_offset" in entry:
            del entry["utc_offset"]
    else:
        entry["utc_offset"] = offset

    start, end = parse_date_range(conf.get("date"))
    if start:
        entry["start"] = start
        entry["end"] = end

    if conf.get("link"):
        entry["url"] = conf["link"]
    if conf.get("place"):
        entry["place"] = conf["place"]

    comment = timeline.get("comment")
    if comment:
        note_bits.insert(0, str(comment))
    if note_bits:
        entry["note"] = " ".join(note_bits)
    elif "note" in entry:
        del entry["note"]

    return f"{entry.get('acronym')} -> {entry['year']}"


def _quote(value) -> str:
    s = str(value)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _format_value(key, value) -> str:
    if key == "tags":
        return "[" + ", ".join(str(t) for t in value) + "]"
    if key in ("year", "utc_offset"):
        return str(value)
    if key in ("start", "end"):
        if isinstance(value, (dt.date, dt.datetime)):
            return value.strftime("%Y-%m-%d")
        return str(value)
    if key in ("deadline", "abstract_deadline"):
        if isinstance(value, dt.datetime):
            return value.strftime("%Y-%m-%d %H:%M")
        return str(value)
    if key in _QUOTED_KEYS:
        return _quote(value)
    return str(value)  # acronym, ccfddl, url — single tokens, safe unquoted


def dump_entry(entry: dict) -> str:
    lines = []
    seen = set()
    for key in _KEY_ORDER:
        if key in entry and entry[key] is not None:
            seen.add(key)
            prefix = "- " if not lines else "  "
            lines.append(f"{prefix}{key}: {_format_value(key, entry[key])}")
    # Emit any unexpected extra keys last, so nothing is silently dropped.
    for key in entry:
        if key not in seen and entry[key] is not None:
            lines.append(f"  {key}: {_format_value(key, entry[key])}")
    return "\n".join(lines)


def main() -> int:
    text = DATA_FILE.read_text(encoding="utf-8")

    # Preserve the leading comment/header block verbatim (everything before the
    # first list item), so documentation isn't lost on round-trip.
    body_lines = text.splitlines()
    first_item = next((i for i, ln in enumerate(body_lines)
                       if ln.startswith("- ")), len(body_lines))
    header = "\n".join(body_lines[:first_item]).rstrip("\n")

    data = yaml.load(text)
    updated, failed = [], []
    for entry in data:
        if not isinstance(entry, dict) or "ccfddl" not in entry:
            continue
        try:
            updated.append(update_entry(entry))
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed.append(f"{entry.get('acronym')}: {exc}")

    blocks = [dump_entry(e) for e in data if isinstance(e, dict)]
    output = header + "\n\n" + "\n\n".join(blocks) + "\n"
    DATA_FILE.write_text(output, encoding="utf-8")

    print("Updated:", ", ".join(updated) if updated else "(none)")
    if failed:
        print("Failed:", "; ".join(failed), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
