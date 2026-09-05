---
layout: page
permalink: /publications/
title: Publications
nav: true
order: 2
---

- [2026 Papers]({% post_url 2026-01-30-paper-list %})
- [2025 Papers]({% post_url 2025-01-30-paper-list %})
- [2024 Papers]({% post_url 2024-01-30-paper-list %})
- [2023 Papers]({% post_url 2023-03-14-paper-list %})
- [2022 Papers]({% post_url 2022-12-31-paper-list %})
- [2021 Papers]({% post_url 2021-12-31-paper-list %})
- [2020 Papers]({% post_url 2020-12-31-paper-list %})
- [2019 Papers]({% post_url 2019-12-31-paper-list %})
- [2018 Papers]({% post_url 2018-12-31-paper-list %})


<div class="publications">

{%- comment -%}
  The year range is derived rather than hand-listed. A hard-coded list silently
  drops any paper whose year is not on it: a 2027 entry rendered nowhere while
  `jekyll build` still exited 0 and printed no warning. "+1" leaves headroom for
  next year's already-accepted papers.

  A year with no papers emits `<ol class="bibliography"></ol>` rather than an
  empty string, so the guard looks for an actual list item instead of testing
  for emptiness. Without it, 2017 printed a bare heading with nothing under it.
{%- endcomment -%}
{% assign maxyear = site.time | date: "%Y" | plus: 1 %}
{% for y in (2017..maxyear) reversed %}
  {% capture bibyear %}{% bibliography -f papers -q @*[year={{y}}]* %}{% endcapture %}
  {% if bibyear contains "<li" %}
  <h2>{{ y }}</h2>
  {{ bibyear }}
  {% endif %}
{% endfor %}

</div>


