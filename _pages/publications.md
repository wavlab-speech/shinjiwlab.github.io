---
layout: page
permalink: /publications/
title: Publications
years: [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017]
nav: true
order: 2
---

- [2024 Papers]({% post_url 2024-01-30-paper-list %})
- [2023 Papers]({% post_url 2023-03-14-paper-list %})
- [2022 Papers]({% post_url 2022-12-31-paper-list %})
- [2021 Papers]({% post_url 2021-12-31-paper-list %})
- [2020 Papers]({% post_url 2020-12-31-paper-list %})
- [2019 Papers]({% post_url 2019-12-31-paper-list %})
- [2018 Papers]({% post_url 2018-12-31-paper-list %})


<div class="publications">

{% for y in page.years %}
  <h2>{{ y }}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>


