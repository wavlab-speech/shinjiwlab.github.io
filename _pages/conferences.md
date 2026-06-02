---
layout: page
permalink: /conferences/
title: Conferences
description: Submission deadlines and dates for conferences the lab follows. Countdowns use your local timezone; deadlines without a timezone are Anywhere-on-Earth (UTC-12).
nav: false
---

<style>
  .conf-tracker { margin-top: 1rem; }
  .conf-card {
    border: 1px solid var(--global-divider-color);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    background-color: var(--global-bg-color);
    transition: opacity 0.2s ease;
  }
  .conf-card.past { opacity: 0.5; }
  .conf-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  .conf-acronym { font-size: 1.4rem; font-weight: 700; color: var(--global-theme-color); }
  .conf-year { font-weight: 400; color: var(--global-text-color-light); font-size: 1.1rem; }
  .conf-name { color: var(--global-text-color-light); font-size: 0.9rem; margin-bottom: 0.5rem; }
  .conf-countdown {
    font-variant-numeric: tabular-nums;
    font-size: 1.15rem;
    font-weight: 600;
    margin: 0.5rem 0;
  }
  .conf-countdown .num { color: var(--global-theme-color); }
  .conf-card.past .conf-countdown { color: var(--global-text-color-light); }
  .conf-meta { font-size: 0.9rem; line-height: 1.6; }
  .conf-meta .label { color: var(--global-text-color-light); display: inline-block; min-width: 5.5rem; }
  .conf-note { font-size: 0.8rem; color: var(--global-text-color-light); margin-top: 0.4rem; font-style: italic; }
  .conf-empty { color: var(--global-text-color-light); }
</style>

<p class="conf-empty">
  This list is maintained manually, so deadlines and dates may be out of date or
  contain errors — always check each conference's official site for the latest,
  authoritative information. Countdowns below update live in your local timezone.
</p>

<div class="conf-tracker" id="conf-tracker">
  {% for c in site.data.conferences %}
  <div class="conf-card"
       data-deadline="{{ c.deadline | date: '%Y-%m-%d %H:%M' }}"
       data-abstract="{{ c.abstract_deadline | date: '%Y-%m-%d %H:%M' }}"
       data-offset="{{ c.utc_offset | default: -12 }}">
    <div class="conf-head">
      <span class="conf-acronym">{{ c.acronym }} <span class="conf-year">{{ c.year }}</span></span>
    </div>
    <div class="conf-name">{{ c.name }}</div>
    <div class="conf-countdown">…</div>
    <div class="conf-meta">
      {% if c.abstract_deadline %}
      <div><span class="label">Abstract:</span> <span class="conf-abstract-local"></span></div>
      {% endif %}
      <div><span class="label">Paper:</span> <span class="conf-deadline-local"></span></div>
      <div><span class="label">📅 Dates:</span>
        {% if c.start == 'TBA' or c.start == 'TBD' or c.start == nil or c.start == '' %}TBD{% else %}{{ c.start | date: '%b %-d' }}{% if c.end and c.end != c.start %} – {{ c.end | date: '%b %-d, %Y' }}{% else %}, {{ c.start | date: '%Y' }}{% endif %}{% endif %}
      </div>
      <div><span class="label">📍 Place:</span> {{ c.place | default: 'TBD' }}</div>
      {% if c.url %}<div><span class="label">🔗 Site:</span> <a href="{{ c.url }}" target="_blank" rel="noopener">{{ c.url | remove: 'https://' | remove: 'http://' | remove_first: 'www.' | split: '/' | first }}</a></div>{% endif %}
    </div>
    {% if c.note %}<div class="conf-note">{{ c.note }}</div>{% endif %}
  </div>
  {% endfor %}
</div>

<script>
(function () {
  // Parse a "YYYY-MM-DD HH:MM" wall-clock string in a given UTC offset (hours)
  // into an absolute epoch (ms). AoE default offset (-12) is applied by Liquid.
  function toEpoch(str, offsetHours) {
    if (!str) return null;
    var m = str.match(/(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
    if (!m) return null;
    var utcAsWall = Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
    return utcAsWall - offsetHours * 3600 * 1000; // UTC = wall - offset
  }

  function fmtLocal(epoch) {
    if (epoch == null) return "—";
    try {
      var d = new Date(epoch);
      return d.toLocaleString(undefined, {
        year: "numeric", month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit", timeZoneName: "short"
      });
    } catch (e) { return new Date(epoch).toString(); }
  }

  function fmtCountdown(ms) {
    if (ms <= 0) return '<span style="font-weight:600">Deadline passed</span>';
    var s = Math.floor(ms / 1000);
    var d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600);  s -= h * 3600;
    var m = Math.floor(s / 60);    s -= m * 60;
    return '<span class="num">' + d + '</span>d ' +
           '<span class="num">' + h + '</span>h ' +
           '<span class="num">' + m + '</span>m ' +
           '<span class="num">' + s + '</span>s';
  }

  var tracker = document.getElementById("conf-tracker");
  if (!tracker) return;
  var cards = Array.prototype.slice.call(tracker.querySelectorAll(".conf-card"));

  cards.forEach(function (card) {
    var off = parseFloat(card.getAttribute("data-offset"));
    if (isNaN(off)) off = -12;
    card.deadlineEpoch = toEpoch(card.getAttribute("data-deadline"), off);
    card.abstractEpoch = toEpoch(card.getAttribute("data-abstract"), off);
    var dl = card.querySelector(".conf-deadline-local");
    if (dl) dl.textContent = fmtLocal(card.deadlineEpoch);
    var ab = card.querySelector(".conf-abstract-local");
    if (ab) ab.textContent = fmtLocal(card.abstractEpoch);
  });

  // Sort: upcoming deadlines first (soonest at top); passed deadlines after,
  // most-recently-passed first. Entries without a deadline sink to the bottom.
  function sortCards() {
    var now = Date.now();
    cards.sort(function (a, b) {
      var ea = a.deadlineEpoch, eb = b.deadlineEpoch;
      if (ea == null) return 1;
      if (eb == null) return -1;
      var ap = ea < now, bp = eb < now;
      if (ap !== bp) return ap ? 1 : -1;     // future before past
      if (!ap) return ea - eb;               // both future: soonest first
      return eb - ea;                        // both past: most recent first
    });
    cards.forEach(function (card) {
      card.classList.toggle("past", card.deadlineEpoch != null && card.deadlineEpoch < now);
      tracker.appendChild(card);
    });
  }

  function tick() {
    var now = Date.now();
    cards.forEach(function (card) {
      var cd = card.querySelector(".conf-countdown");
      if (!cd) return;
      if (card.deadlineEpoch == null) { cd.textContent = "No deadline set"; return; }
      cd.innerHTML = fmtCountdown(card.deadlineEpoch - now);
    });
  }

  sortCards();
  tick();
  // Re-sort once a minute (so a card flips to "past" without a reload); tick each second.
  setInterval(tick, 1000);
  setInterval(sortCards, 60000);
})();
</script>
