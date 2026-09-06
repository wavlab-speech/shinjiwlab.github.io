---
layout: page
permalink: /speech_lunch
title: Speech Lunch
nav: true
order: 10
---

Welcome to the Speech Lunch (formerly Sphinx Lunch) at Carnegie Mellon University!
This lunch meeting is designed to discuss any speech-related research items regularly.
The meeting consists of presentations by CMU faculty members, CMU students, and guest speakers.
We welcome any reserach topics, including an ordinary presentation, conference presentation rehearsals, preliminary research ideas, research discussions, and so on.
We also welcome any CMU researchers and external researchers to join the meeting.

During the semester, we will regularly have meetings in the following slots:

- Date: Thursday 12:30 pm - 1:30 pm

The time and room may change, especially if we have a guest speaker.
We will announce the talk information through our [mailing list](https://mailman.srv.cs.cmu.edu/mailman/listinfo/sphinxmail). Approval by the admin is required.
So, please subscribe to it if you're interested in the CMU speech!

Please contact Chien-yu Huang <cyhuang1997@gmail.com> and Shinji Watanabe <shinjiw@ieee.org> if you would like to participate in our Speech Lunch.

## Talk schedule

<style>
  .sl-schedule {
    margin-top: 1.2rem;
    --sl-border: rgba(0, 0, 0, 0.12);
    --sl-surface: rgba(0, 0, 0, 0.025);
    /* Set explicitly per theme: in dark mode al-folio maps --global-text-color-light
       to the same value as --global-text-color, which would erase the hierarchy. */
    --sl-muted: #6f6f6f;
  }
  html[data-theme='dark'] .sl-schedule {
    --sl-border: rgba(255, 255, 255, 0.16);
    --sl-surface: rgba(255, 255, 255, 0.05);
    --sl-muted: #b8b8b8;
  }

  .sl-sr {
    position: absolute;
    width: 1px; height: 1px;
    padding: 0; margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  /* Semester picker ------------------------------------------------------- */
  .sl-toolbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-bottom: 0.9rem;
  }
  .sl-toolbar label {
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--sl-muted);
    margin: 0;
  }
  .sl-select {
    font: inherit;
    font-size: 1rem;          /* >=16px, or iOS Safari zooms the page on tap */
    padding: 0.25rem 0.5rem;
    color: var(--global-text-color);
    background-color: var(--global-bg-color);
    border: 1px solid var(--sl-border);
    border-radius: 6px;
  }
  html[data-theme='dark'] .sl-select { color-scheme: dark; }

  /* Next talk ------------------------------------------------------------- */
  .sl-next {
    border: 1px solid var(--sl-border);
    border-left: 4px solid var(--global-theme-color);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    background-color: var(--sl-surface);
  }
  .sl-kicker {
    font-size: 0.72rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--global-theme-color);
  }
  .sl-next-date {
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1.25;
    margin: 0.15rem 0 0.4rem;
  }
  .sl-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem 0.6rem;
    font-size: 0.85rem;
    color: var(--sl-muted);
    margin-bottom: 0.7rem;
  }
  .sl-chip {
    border: 1px solid var(--sl-border);
    border-radius: 999px;
    padding: 0.05rem 0.55rem;
    font-size: 0.75rem;
    white-space: nowrap;
  }
  .sl-speaker { font-weight: 600; font-size: 1.05rem; }
  .sl-title { margin-top: 0.15rem; line-height: 1.45; }
  .sl-abstract {
    margin-top: 0.7rem;
    font-size: 0.9rem;
    line-height: 1.65;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
  }

  /* Section headings ------------------------------------------------------ */
  .sl-h {
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 700;
    color: var(--sl-muted);
    margin: 1.9rem 0 0.2rem;
  }
  .sl-schedule > div > .sl-h:first-child { margin-top: 0; }

  /* Compact rows ---------------------------------------------------------- */
  .sl-row {
    display: grid;
    grid-template-columns: 5.5rem minmax(0, 1fr) auto;
    gap: 0.15rem 0.9rem;
    align-items: baseline;
    padding: 0.6rem 0;
    border-top: 1px solid var(--sl-border);
  }
  .sl-row-date {
    font-variant-numeric: tabular-nums;
    font-size: 0.9rem;
    color: var(--sl-muted);
  }
  .sl-row-main { overflow-wrap: anywhere; }
  .sl-row-speaker { font-weight: 600; }
  .sl-row-title { font-size: 0.88rem; color: var(--sl-muted); line-height: 1.5; }
  .sl-row-note { font-size: 0.8rem; color: var(--sl-muted); font-style: italic; }
  .sl-row-loc { font-size: 0.8rem; color: var(--sl-muted); white-space: nowrap; }
  .sl-row.sl-break .sl-row-main { font-style: italic; color: var(--sl-muted); }

  /* Past talks are separated by their heading, not by opacity: dimming text
     that is already muted pushes it below the readable contrast ratio. */

  .sl-details { margin-top: 0.3rem; }
  .sl-details > summary {
    cursor: pointer;
    font-size: 0.82rem;
    color: var(--global-theme-color);
    list-style: none;
  }
  .sl-details > summary::-webkit-details-marker { display: none; }
  .sl-details > summary::after { content: " \25B8"; }
  .sl-details[open] > summary::after { content: " \25BE"; }
  .sl-details .sl-abstract { margin-top: 0.4rem; }

  .sl-note { font-size: 0.85rem; color: var(--sl-muted); margin-top: 1.5rem; }
  .sl-status { color: var(--sl-muted); font-style: italic; }

  @media (max-width: 576px) {
    .sl-row { grid-template-columns: minmax(0, 1fr); gap: 0.1rem; }
    .sl-row-loc { white-space: normal; }
    .sl-toolbar { justify-content: flex-start; }
  }
</style>

<div class="sl-schedule" id="sl-schedule">
  <div class="sl-toolbar">
    <label for="sl-semester">Semester</label>
    <select id="sl-semester" class="sl-select">
      <option value="">Current semester</option>
    </select>
  </div>
  <p class="sl-sr" id="sl-announce" role="status" aria-live="polite"></p>
  <div id="sl-body"><p class="sl-status">Loading the schedule…</p></div>
  <noscript>
    <p class="sl-status">
      The talk schedule is loaded with JavaScript, which appears to be disabled.
      Talks are announced on our mailing list, linked above.
    </p>
  </noscript>
</div>

{% raw %}
<script>
(function () {
  var CSV_BASE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQJKbd_caVWoWstQ4W93XP9jikGDp6ablHQQJoV4iIxV7kVuDfj7F9zz8VBvDG6Crbh8jLjadBd6GN/pub?output=csv";

  // ---------------------------------------------------------------------------
  // MAINTENANCE NOTE
  //
  // The CURRENT semester needs no edit here: the export with no `gid` returns the
  // spreadsheet's LEFTMOST tab, so as long as each new semester is added as the
  // leftmost tab, this page follows it automatically.
  //
  // This list drives the ARCHIVE picker, and it deliberately includes the
  // in-progress semester as well -- whichever entry matches the current tab's
  // computed label is hidden at runtime, so there is never a duplicate, and the
  // entry starts showing in the archive by itself once the semester rolls over.
  // Add one line per new semester when convenient; the live view never needs it.
  //
  // The `name` is a hand-typed string, NOT read from Google. It matters: when a
  // tab stores dates as "M/D" with no year, the year is taken from this name, so
  // it must read "Fall YYYY" or "Spring YYYY". Tabs that store a full "M/D/YYYY"
  // date ignore the name and use the year in the cell.
  // A tab's id is the `gid=` value in the sheet's URL when that tab is open.
  // ---------------------------------------------------------------------------
  var SEMESTERS = [
    { name: "Fall 2026",   gid: "2056576296" },
    { name: "Spring 2026", gid: "986981840" },
    { name: "Fall 2025",   gid: "908298604" },
    { name: "Spring 2025", gid: "1405763946" },
    { name: "Fall 2024",   gid: "1931292116" },
    { name: "Spring 2024", gid: "511445022" },
    { name: "Fall 2023",   gid: "989792674" },
    { name: "Spring 2023", gid: "2011781738" },
    { name: "Fall 2022",   gid: "0" }
  ];

  var root = document.getElementById("sl-schedule");
  var body = document.getElementById("sl-body");
  var picker = document.getElementById("sl-semester");
  var announce = document.getElementById("sl-announce");
  if (!root || !body || !picker) return;

  // -- Quote-aware CSV parser. Abstracts contain commas, quotes and newlines,
  //    so splitting on "," would corrupt them.
  function parseCSV(text) {
    var rows = [], row = [], field = "", inQuotes = false;
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);   // strip BOM
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (inQuotes) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i++; }
          else { inQuotes = false; }
        } else if (c !== "\r") { field += c; }
      } else if (c === '"') {
        inQuotes = true;
      } else if (c === ",") {
        row.push(field); field = "";
      } else if (c === "\n") {
        row.push(field); rows.push(row); row = []; field = "";
      } else if (c !== "\r") {
        field += c;
      }
    }
    if (field !== "" || row.length) { row.push(field); rows.push(row); }
    return rows;
  }

  // -- Map by header name. Columns differ between semesters (the older tabs have
  //    no Location or Presentation column), and this also keeps the sheet's
  //    unnamed internal-notes column off the page.
  var WANTED = ["date", "speaker", "presentation", "location", "title", "abstract"];

  function toRecords(rows) {
    if (!rows.length) return [];
    var header = rows[0].map(function (h) { return h.trim().toLowerCase(); });
    var idx = {};
    WANTED.forEach(function (key) { idx[key] = header.indexOf(key); });
    return rows.slice(1).map(function (r) {
      var rec = {};
      WANTED.forEach(function (key) {
        rec[key] = idx[key] >= 0 && r[idx[key]] ? r[idx[key]].trim() : "";
      });
      return rec;
    });
  }

  // -- Date cells come in several shapes across the tabs:
  //      "8/27"                                   (no year -- needs an anchor)
  //      "09/01"                                  (zero padded, no year)
  //      "9/12/2024" / "11/02/2023"               (explicit year)
  //      "10/19/2023 (Fall Break)"                (explicit year + a note)
  //    Free-text rows ("Webpage: ...", "next semester") must not match.
  var DATE_RE = /^\s*(\d{1,2})\s*[\/\-]\s*(\d{1,2})(?:\s*[\/\-]\s*(\d{2,4}))?\s*(?:\(([^)]*)\))?\s*$/;

  function parseDateCell(str) {
    var m = DATE_RE.exec(str || "");
    if (!m) return null;
    var mo = +m[1], d = +m[2];
    if (mo < 1 || mo > 12 || d < 1 || d > 31) return null;
    var y = null;
    if (m[3]) { y = +m[3]; if (y < 100) y += 2000; }
    return { mo: mo, day: d, year: y, note: (m[4] || "").trim() };
  }

  // -- "Fall 2025" + month 9 -> 2025. Handles a January date on a Fall tab and a
  //    September date on a Spring tab.
  function yearFromSemester(name, month) {
    var m = /^(fall|spring|summer)\s+(\d{4})$/i.exec(name || "");
    if (!m) return null;
    var term = m[1].toLowerCase(), y = +m[2];
    if (term === "fall") return month <= 5 ? y + 1 : y;
    if (term === "spring") return month >= 9 ? y - 1 : y;
    return y;
  }

  // When the lab meets, as stated in the page copy above (0 = Sunday). A talk
  // carries the END of its meeting as its timestamp, so it leaves the "Next
  // talk" card when the meeting finishes instead of at midnight.
  var MEETING_DAY = 4;
  var MEETING_END_HOUR = 13, MEETING_END_MINUTE = 30;

  function makeDate(y, mo, d) {
    var cand = new Date(y, mo - 1, d, MEETING_END_HOUR, MEETING_END_MINUTE, 0);
    return (cand.getMonth() === mo - 1 && cand.getDate() === d) ? cand : null;
  }

  // -- Name the tab as a whole. Every row then derives its year from this ONE
  //    anchor, so a tab can never split across two calendar years -- which is
  //    what a per-row "closest year" guess used to do once the leftmost tab went
  //    a few months stale, promoting an already-held talk into "Next talk".
  function anchorFor(parsed, today) {
    if (!parsed.length) return null;

    // The sheet's own year always wins when a cell carries one.
    for (var i = 0; i < parsed.length; i++) {
      if (parsed[i].year !== null) {
        return (parsed[i].mo >= 6 ? "Fall " : "Spring ") + parsed[i].year;
      }
    }

    var fall = 0;
    parsed.forEach(function (p) { if (p.mo >= 6) fall++; });
    var term = fall * 2 >= parsed.length ? "Fall" : "Spring";

    // Rank the candidate years. The distance test alone flips a whole semester
    // forward once the leftmost tab goes badly stale, which would advertise an
    // already-held talk as the next one. Shifting a year moves every date off
    // MEETING_DAY (365 days = 52 weeks + 1), so the weekday is the stronger
    // signal and is tried first; if the lab ever moves off Thursdays no
    // candidate scores, and this falls back to the distance test on its own.
    // The window reaches back several years so that the weekday test still has a
    // correct candidate to find if the sheet is left stale for more than a year.
    var y0 = today.getFullYear(), cands = [], best = null, bestDay = -1, bestDist = Infinity;
    for (var yy = y0 - 6; yy <= y0 + 1; yy++) cands.push(yy);
    cands.forEach(function (y) {
      var name = term + " " + y, stamps = [], onDay = 0;
      parsed.forEach(function (p) {
        var dt = makeDate(yearFromSemester(name, p.mo), p.mo, p.day);
        if (!dt) return;
        stamps.push(dt.getTime());
        if (dt.getDay() === MEETING_DAY) onDay++;
      });
      if (!stamps.length) return;
      stamps.sort(function (a, b) { return a - b; });
      var dist = Math.abs(stamps[Math.floor(stamps.length / 2)] - today.getTime());
      if (onDay > bestDay || (onDay === bestDay && dist < bestDist)) {
        bestDay = onDay; bestDist = dist; best = name;
      }
    });
    return best;
  }

  function fmtLong(d) {
    return d.toLocaleDateString(undefined, {
      weekday: "long", month: "long", day: "numeric", year: "numeric"
    });
  }
  function fmtShort(d) {
    return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  }

  // -- Every value below comes from the spreadsheet: build nodes, never innerHTML.
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function renderNext(item) {
    var card = el("div", "sl-next");
    card.appendChild(el("div", "sl-kicker", "Next talk"));
    card.appendChild(el("div", "sl-next-date", fmtLong(item.date)));

    var meta = el("div", "sl-meta");
    if (item.location) meta.appendChild(el("span", null, "📍 " + item.location));
    if (item.presentation) meta.appendChild(el("span", "sl-chip", item.presentation));
    if (item.note) meta.appendChild(el("span", "sl-chip", item.note));
    if (meta.childNodes.length) card.appendChild(meta);

    card.appendChild(el("div", "sl-speaker", item.speaker || "Speaker TBA"));
    card.appendChild(el("div", "sl-title", item.title || "Title TBA"));
    if (item.abstract) card.appendChild(el("div", "sl-abstract", item.abstract));
    return card;
  }

  function renderRow(item, collapsible) {
    var row = el("div", "sl-row" + (item.isBreak ? " sl-break" : ""));
    var dateCell = el("div", "sl-row-date", fmtShort(item.date));
    dateCell.title = fmtLong(item.date);   // the year is implied by the heading
    row.appendChild(dateCell);

    var main = el("div", "sl-row-main");
    if (item.isBreak) {
      main.appendChild(el("div", null, item.speaker || item.note));
    } else {
      main.appendChild(el("div", "sl-row-speaker", item.speaker || "Speaker TBA"));
      if (item.title) main.appendChild(el("div", "sl-row-title", item.title));
      if (item.note) main.appendChild(el("div", "sl-row-note", item.note));
      if (collapsible && item.abstract) {
        var det = el("details", "sl-details");
        var sum = el("summary", null, "Abstract");
        // Distinguish the N identical "Abstract" toggles for screen readers.
        sum.setAttribute("aria-label", "Abstract — " + (item.speaker || "this talk"));
        det.appendChild(sum);
        det.appendChild(el("div", "sl-abstract", item.abstract));
        main.appendChild(det);
      }
    }
    row.appendChild(main);
    row.appendChild(el("div", "sl-row-loc", item.location || ""));
    return row;
  }

  function renderSection(title, items, collapsible) {
    var frag = document.createDocumentFragment();
    // A heading element, not a styled div: screen readers navigate by heading.
    // The page title above is an <h2>, so these sections are <h3>.
    frag.appendChild(el("h3", "sl-h", title));
    var box = el("div", null);
    items.forEach(function (it) { box.appendChild(renderRow(it, collapsible)); });
    frag.appendChild(box);
    return frag;
  }

  function setStatus(message) {
    body.textContent = "";
    body.appendChild(el("p", "sl-status", message));
  }

  function say(message) {
    if (announce) announce.textContent = message;
  }

  function footerNote() {
    return el("p", "sl-note",
      "Talks are on Thursdays, 12:30–1:30 pm, unless announced otherwise.");
  }

  function toItems(records, semesterName) {
    // "This row has no room" only means "this is not a talk" on a tab where
    // rooms are actually recorded. Test the VALUES, not the header: a new
    // semester tab carries the Location header before anyone fills in a room,
    // and on such a tab every speaker still waiting for a room would otherwise
    // be dimmed as a break week and skipped for the "Next talk" card.
    // On the legacy tabs, which have no Location column, the date note names
    // the break instead.
    var tabRecordsRooms = records.some(function (r) { return !!r.location; });
    var parsed = [];
    records.forEach(function (r) {
      var dp = parseDateCell(r.date);
      if (dp) parsed.push({ rec: r, dp: dp });
    });
    if (!parsed.length) return { items: [], label: null };

    var anchor = semesterName || anchorFor(parsed.map(function (p) { return p.dp; }), new Date());

    var items = [];
    parsed.forEach(function (p) {
      var y = p.dp.year !== null ? p.dp.year : yearFromSemester(anchor, p.dp.mo);
      if (y === null) return;
      var date = makeDate(y, p.dp.mo, p.dp.day);
      if (!date) return;
      var r = p.rec;
      items.push({
        date: date,
        speaker: r.speaker,
        presentation: r.presentation,
        location: r.location,
        title: r.title,
        abstract: r.abstract,
        note: p.dp.note,
        // A break week ("Interspeech", "Fall break", "Thanksgiving") is named
        // either in the speaker cell or, on the legacy tabs, in the date note.
        // Requiring a location column for the first form is what stops a real
        // speaker with an unfilled title being dimmed as a break week.
        isBreak: !r.title && !r.abstract && !r.location &&
                 ((tabRecordsRooms && !!r.speaker) || (!r.speaker && !!p.dp.note))
      });
    });
    items.sort(function (a, b) { return a.date - b.date; });
    return { items: items, label: anchor };
  }

  // -- Current semester: next-talk card, then upcoming, then past.
  function renderCurrent(items) {
    var now = Date.now();
    var upcoming = items.filter(function (i) { return i.date.getTime() >= now; });
    var past = items.filter(function (i) { return i.date.getTime() < now; }).reverse();

    var next = null;
    for (var i = 0; i < upcoming.length; i++) {
      if (!upcoming[i].isBreak) { next = upcoming[i]; break; }
    }
    var rest = upcoming.filter(function (i) { return i !== next; });

    body.textContent = "";
    if (next) body.appendChild(renderNext(next));
    if (rest.length) body.appendChild(renderSection("Upcoming", rest, false));
    if (past.length) body.appendChild(renderSection("Past talks", past, true));
    body.appendChild(footerNote());
  }

  // -- An archived semester is entirely in the past: one chronological list.
  function renderArchive(name, items) {
    body.textContent = "";
    body.appendChild(renderSection(name, items, true));
    body.appendChild(footerNote());
  }

  var cache = {};
  var reqSeq = 0;

  function load(gid) {
    var key = gid || "current";
    if (cache[key]) return Promise.resolve(cache[key]);
    return fetch(gid ? CSV_BASE + "&gid=" + encodeURIComponent(gid) : CSV_BASE, { cache: "no-cache" })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.text();
      })
      .then(function (text) {
        cache[key] = toRecords(parseCSV(text));
        return cache[key];
      });
  }

  function show(gid, userAsked) {
    // A cached semester resolves in a microtask while an earlier, uncached one is
    // still on the network. Without this token the slower response wins and the
    // rendered schedule disagrees with the <select>.
    var myReq = ++reqSeq;
    setStatus("Loading the schedule…");
    // Announce a semester the reader chose. Staying quiet on the first load
    // avoids interrupting a screen reader that is still reading the page.
    if (userAsked) say("Loading the schedule…");

    var entry = null;
    for (var i = 0; i < SEMESTERS.length; i++) {
      if (SEMESTERS[i].gid === gid) { entry = SEMESTERS[i]; break; }
    }

    load(gid)
      .then(function (records) {
        if (myReq !== reqSeq) return;
        var out = toItems(records, entry ? entry.name : null);
        if (!out.items.length) {
          var empty = records.length
            ? "No dated talks could be read for this semester."
            : "No talks are listed for this semester yet.";
          setStatus(empty);
          say(empty);
          return;
        }
        if (entry) {
          renderArchive(entry.name, out.items);
          say("Showing the " + entry.name + " schedule.");
        } else {
          renderCurrent(out.items);
          syncPicker(out.label);
          say("Showing the current schedule.");
        }
      })
      .catch(function () {
        if (myReq !== reqSeq) return;
        var failed = "The schedule could not be loaded right now. Please try again later — talks are also announced on our mailing list.";
        setStatus(failed);
        say(failed);
      });
  }

  // -- Label the "current" option from its own data, and drop the archive entry
  //    that duplicates it.
  function syncPicker(label) {
    if (!label) return;
    picker.options[0].textContent = label + " (current)";
    for (var i = picker.options.length - 1; i > 0; i--) {
      if (picker.options[i].textContent === label) picker.remove(i);
    }
  }

  SEMESTERS.forEach(function (s) {
    var opt = document.createElement("option");
    opt.value = s.gid;
    opt.textContent = s.name;
    picker.appendChild(opt);
  });

  // Browsers restore a <select> by index across reloads, which would land on an
  // arbitrary semester once the duplicate option is removed. Always start here.
  picker.selectedIndex = 0;
  picker.addEventListener("change", function () { show(picker.value, true); });
  show("");
})();
</script>
{% endraw %}
