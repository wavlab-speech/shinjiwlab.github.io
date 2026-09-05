---
layout: page
permalink: /members/
title: Members
nav: true
order: 1
---

<style>
/* Extra small devices (portrait phones, less than 576px) */
@media (max-width: 575.98px) {
  .w-xs-100 {
    width: 100% !important;
  }

  .w-xs-75 {
    width: 75% !important;
  }

  .w-xs-50 {
    width: 50% !important;
  }

  .w-xs-25 {
    width: 25% !important;
  }
}

/* Small devices (landscape phones, 576px and up) */
@media (min-width: 576px) and (max-width: 767.98px) {
  .w-sm-100 {
    width: 100% !important;
  }

  .w-sm-75 {
    width: 75% !important;
  }

  .w-sm-50 {
    width: 50% !important;
  }

  .w-sm-25 {
    width: 25% !important;
  }
}

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) and (max-width: 991.98px) {

  .w-md-100 {
    width: 100% !important;
  }

  .w-md-75 {
    width: 75% !important;
  }

  .w-md-50 {
    width: 50% !important;
  }

  .w-md-25 {
    width: 25% !important;
  }
}

/* Large devices (desktops, 992px and up) */
@media (min-width: 992px) and (max-width: 1199.98px) {

  .w-lg-100 {
    width: 100% !important;
  }

  .w-lg-75 {
    width: 75% !important;
  }

  .w-lg-50 {
    width: 50% !important;
  }

  .w-lg-25 {
    width: 25% !important;
  }


}

/* Extra large devices (large desktops, 1200px and up) */
@media (min-width: 1200px) {

  .w-xl-100 {
    width: 100% !important;
  }

  .w-xl-75 {
    width: 75% !important;
  }

  .w-xl-50 {
    width: 50% !important;
  }

  .w-xl-25 {
    width: 25% !important;
  }

}



.car-col-2 {
  -webkit-column-count: 2;
  -moz-column-count: 2;
  column-count: 2;
}

.car-col-1 {
  -webkit-column-count: 1;
  -moz-column-count: 1;
  column-count: 1;
}

.car-col-3 {
  -webkit-column-count: 3;
  -moz-column-count: 3;
  column-count: 3;
}

.car-col-4 {
  -webkit-column-count: 4;
  -moz-column-count: 4;
  column-count: 4;
}

.car-col-5 {
  -webkit-column-count: 5;
  -moz-column-count: 5;
  column-count: 5;
}

.car-col-6 {
  -webkit-column-count: 6;
  -moz-column-count: 6;
  column-count: 6;
}

.square{
    position:relative;
    overflow:hidden;
    padding-bottom:100%;
}
.square img{
    position:absolute;
}

.member-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
    /* Without this, grid items stretch to the tallest card in the row, so
       expanding one member's publication list inflates every sibling card
       into a tall empty box. */
    align-items: start;
}

.member-card {
    display: flex;
    flex-direction: column;
    border: 1px solid var(--global-divider-color, rgba(128, 128, 128, 0.25));
    border-radius: 10px;
    padding: 1rem 1.1rem;
    background-color: var(--global-bg-color);
}

.member-card-head {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}

.member-card-photo {
    width: 72px;
    height: 72px;
    flex: 0 0 72px;
    border-radius: 50%;
    object-fit: cover;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.member-card-info {
    min-width: 0;
}

.member-card-name {
    font-weight: 700;
    font-size: 1.05rem;
    line-height: 1.2;
}

.member-card-note {
    display: inline-block;
    font-weight: 400;
    font-size: 0.8rem;
    color: var(--global-text-color-light);
    white-space: nowrap;
}

.member-card-links {
    margin-top: 0.3rem;
    font-size: 0.82rem;
}

.member-card-links a {
    color: var(--global-theme-color);
    margin-right: 0.7rem;
    white-space: nowrap;
    text-decoration: none;
}

.member-card-links a:hover {
    text-decoration: underline;
}

.member-pubs {
    margin-top: 0.85rem;
}

.member-pubs > summary {
    cursor: pointer;
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--global-text-color-light);
    list-style: none;
}

.member-pubs > summary::-webkit-details-marker {
    display: none;
}

.member-pubs > summary::before {
    content: "▸ ";
}

.member-pubs[open] > summary::before {
    content: "▾ ";
}

.member-pubs .pub-count {
    color: var(--global-theme-color);
}

.pub-list {
    list-style: decimal;
    padding-left: 1.25rem;
    margin: 0.6rem 0 0;
    font-size: 0.85rem;
}

.pub-list li {
    margin-bottom: 0.45rem;
    line-height: 1.4;
}

.pub-venue {
    color: var(--global-text-color-light);
    font-style: italic;
}

.pub-more,
.pub-none {
    margin-top: 0.5rem;
    color: var(--global-text-color-light);
}

.pub-disclaimer {
    /* The theme zeroes h4 margin-top, so the bottom margin here is the only
       thing separating this block from the "Faculty" heading. Every other
       section heading gets its clearance from the <hr /> above it. */
    margin: 1.5rem 0 2.25rem;
    padding: 0.7rem 0.9rem;
    border-left: 3px solid var(--global-theme-color);
    border-radius: 0 6px 6px 0;
    background-color: var(--global-code-bg-color, rgba(128, 128, 128, 0.07));
    font-size: 0.85rem;
    line-height: 1.5;
    color: var(--global-text-color-light);
}

.pub-disclaimer a {
    color: var(--global-theme-color);
}

</style>

<p class="pub-disclaimer">
The publication list under each member is fetched automatically from
<a href="https://scholar.google.com/" target="_blank" rel="noopener noreferrer">Google Scholar</a>
and shows only that member's most recent papers, so it may be incomplete or
out of date, and titles and venues are not always correct. For an accurate and
complete list, please see each member's own website or Google Scholar profile,
linked on their card. The lab's curated list of papers is on the
<a href="{{ site.baseurl }}/publications/">Publications</a> page.
</p>

#### Faculty

<div class="member-grid">
{%- assign faculty = site.data.members | where: "role", "faculty" -%}
{% for m in faculty %}{% include member_card.html member=m %}{% endfor %}
</div>
<hr />

#### Post-Doc

<div class="member-grid">
{%- assign postdocs = site.data.members | where: "role", "postdoc" -%}
{% for m in postdocs %}{% include member_card.html member=m %}{% endfor %}
</div>
<hr />


#### PhD Students

<div class="member-grid">
{%- assign phds = site.data.members | where: "role", "phd" -%}
{% for m in phds %}{% include member_card.html member=m %}{% endfor %}
</div>
<hr />

#### Master Students

<div class="member-grid">
{%- assign masters = site.data.members | where: "role", "master" -%}
{% for m in masters %}{% include member_card.html member=m %}{% endfor %}
</div>

<hr />

<!-- #### Undergraduate Students
<div class="row mt-3">
    <div class="col-sm mt-1 mt-md-1">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>
<hr /> -->

#### Visitors

<div class="member-grid">
{%- assign visitors = site.data.members | where: "role", "visitor" -%}
{% for m in visitors %}{% include member_card.html member=m %}{% endfor %}
</div>
<hr />

#### Industrial Collaborators

<div class="member-grid">
{%- assign industrial = site.data.members | where: "role", "industrial" -%}
{% for m in industrial %}{% include member_card.html member=m %}{% endfor %}
</div>
<hr />

#### Alumni

##### Visting Faculty
<ul>
<li>2023. 09 -- 2024. 06: Karen Livescu (TTIC) </li>
</ul>

##### Post-Docs
<ul>
<li>2024. 02 - 2025. 05: Hye-jin Shim (CMU) </li>
<li>2023. 03 - 2024. 09: Jeeweon Jung (CMU)</li>
<li>2022. 03 - 2024. 08: Soumi Maiti (CMU) </li>
<li>2021. 09 - 2024. 07: Zhong-Qiu Wang (CMU) </li>
</ul>

##### PhD
<ul>
<li>2021. 09 - 2026. 04: Brian Yan (CMU) </li>
<li>2022. 05 - 2026. 03: Li-Wei Chen (CMU, co-supervising) </li>
<li>2020. 08 - 2026. 03: Siddhant Arora (CMU) </li>
<li>2019. 09 - 2025. 12: Jiatong Shi (CMU) </li>
<li>2020. 09 - 2025. 04: Yifan Peng (CMU) </li>
<li>2019. 09 - 2024. 05: Xuankai Chang (CMU) </li>
<li>2021. 09 - 2024. 05: Muqiao Yang (CMU, co-supervisor) </li>
<li>2021. 01 - 2023. 06: Xinjian Li (CMU, co-supervisor) </li>
<li>2020. 09 - 2023. 06: Jessica Huynh (CMU, co-supervisor) </li>
<li>2020. 09 - 2022. 08: Siddharth Dalmia (CMU, co-supervisor)</li>
<li>2017. 09 - 2021. 08: Aswin Shanmugam Subramanian (JHU)</li>
<li>2017. 10 - 2021. 08: Matthew Maciejewski (JHU, co-supervisor)</li>
<li>2017. 12 - 2020. 12: Matthew Wiesner (JHU, co-supervising)</li>
</ul>

##### MS & Undergraduate
<ul>
<li>2024. 08 - 2026. 05: Chyi-Jiunn Lin (CMU) </li>
<li>2023. 05 - 2025. 05: Kwanghee Choi (CMU) </li>
<li>2022. 09 - 2024. 05: Shih-Lun Wu (CMU) </li>
<li>2021. 09 - 2023. 05: Dan Berrebbi (CMU) </li>
<li>2021. 09 - 2022. 12: Dorsa Zeinali (CMU) </li>
<li>2021. 09 - 2022. 12: Karthik Ganesan (MIIS directed study, CMU) </li>
<li>2021. 01 - 2022. 08: Chaitanya Narisetty (CMU)</li>
<li>2021. 01 - 2022. 08: Peter Wu (CMU, co-supervisor)</li>
<li>2021. 09 - 2022. 08: Sujay Suresh Kumar (MIIS directed study, CMU)</li>
<li>2021. 09 - 2022. 08: Debayan Ghosh (CMU)</li>
<li>2020. 08 - 2021. 08: Tianzi Wang (JHU) </li>
<li>2018. 07 - 2019. 06: Zhiqi Wang (JHU)</li>
<li>2017. 09 - 2018. 12: Szu-Jui Chen (JHU)</li>
</ul>


##### Visitors & Collaborators
<ul>
<li>2026. 02 - 2026. 07: Dahee Yang (Hanyang University) </li>
<li>2026. 01 - 2026. 05: Alexander Polok (Brno University of Technology) </li>
<li>2025. 12 - 2026. 03: Xun Gong (Shanghai Jiao Tong University) </li>
<li>2025. 08 - 2025. 12: Haoran Wang (Shanghai Jiao Tong University) </li>
<li>2025. 04 - 2025. 12: Bo-Hao Su (National Tsing Hua University) </li>
<li>2025. 05 - 2025. 11: Ji-Hoon Kim (Korea Advanced Institute of Science and Technology) </li>
<li>2025. 02 - 2025. 07: Jialu Li (University of Illinois Urbana-Champaign) </li>
<li>2025. 01 - 2025. 04: Pu Wang (KU Leuven) </li>
<li>2024. 08 - 2025. 02: Kalvin Chang (UC Berkeley) </li>
<li>2024. 09 - 2025. 02: Holger Severin Bovbjerg (Aalborg University) </li>
<li>2024. 11 - 2024. 12: Junyi Peng (Brno University of Technology) </li>
<li>2024. 08 - 2024. 12: Carlos Carvalho (Instituto Superior Técnico ) </li>
<li>2024. 04 - 2024. 12: Shuichiro Shimizu (Kyoto University) </li>
<li>2024. 08 - 2024. 11: Shih-Heng Wang (National Taiwan University) </li>
<li>2024. 08 - 2024. 11: Yoshiaki Bando (National Institute of Advanced Industrial Science and Technology) </li>
<li>2023. 09 - 2024. 08: Yihan Wu (Renmin University) </li>
<li>2023. 11 - 2024. 04: Chenda Li (Shanghai Jiaotong University) </li>
<li>2023. 08 - 2024. 03: Roshan Sharma (Carnegie Mellon University)</li>
<li>2023. 03 - 2024. 03: Wangyou Zhang (Shanghai Jiaotong University)</li>
<li>2023. 08 - 2023. 10: Minsu Kim (Korea Advanced Institute of Science and Technology)</li>
<li>2023. 05 - 2023. 08: Kohei Saijo (Waseda University)</li>
<li>2022. 10 - 2023. 01: Takaaki Saeki (University of Tokyo)</li>
<li>2021. 12 - 2022. 12: Yosuke Kashiwagi (Sony)</li>
<li>2022. 04 - 2022. 09: Samuele Cornell (Universita Politecnica delle Marche)</li>
<li>2022. 03 - 2022. 06: Yoshiki Masuyama (Tokyo Metropolitan University)</li>
<li>2021. 07 - 2022. 07: Yushi Ueda (Japan Patent Office)</li>
<li>2021. 08 - 2021. 12: Yen-Ju Lu (Research Center for Information Technology Innovation, Academia Sinica)</li>
<li>2020. 01 - 2021. 01: Pengcheng Guo (Northwestern Polytechnical University)</li>
<li>2019. 12 - 2020. 03 & 2022. 03 - 2022. 06: Yosuke Higuchi (Waseda University)</li>
<li>2019. 12 - 2020. 12: Jing Shi (Chinese Academy of Science)</li>
<li>2019. 07 - 2019. 10: Katsuki Inoue (Okayama University)</li>
<li>2018. 11 - 2019. 05: Murali Karthick Baskar (Brno University of Technology)</li>
<li>2018. 09 - 2018. 12: Xuankai Chang (Shanghai Jiao Tong University)</li>
<li>2018. 08 - 2018. 09: Hirofumi Inaguma (Kyoto University)</li>
<li>2018. 07 - 2020. 03: Yusuke Fujita (Hitachi Ltd.)</li>
<li>2018. 04 - 2018. 09: Nelson Enrique Yalta Soplin (Waseda University)</li>
</ul>



