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

.member-pubs-section details {
    border: 1px solid var(--global-divider-color);
    border-radius: 4px;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
}

.member-pubs-section details summary {
    cursor: pointer;
    font-weight: 500;
}

.member-pubs-section .pub-list {
    list-style: decimal;
    padding-left: 1.2rem;
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

.member-pubs-section .pub-list li {
    margin-bottom: 0.4rem;
}

.member-pubs-section .pub-venue {
    color: var(--global-text-color-light);
    font-style: italic;
}

</style>


#### Faculty
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-1" style="display:table-cell; vertical-align:middle; text-align:center">
    	<a href="https://sites.google.com/view/shinjiwatanabe" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/shinji_20210605.jpg">
        </a>
        <div class="caption">
            Shinji Watanabe
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>

<div class="member-pubs-section mt-2">
{% assign pubs = site.data.scholar_pubs.shinji_watanabe %}
<details>
<summary><strong>Shinji Watanabe</strong> — Publications
{% if pubs.size > 0 %}<small class="text-muted">({{ pubs.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=qesMX_wAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
{% if pubs.size > 20 %}<p><small><em>Showing 20 of {{ pubs.size }} publications. <a href="https://scholar.google.com/citations?user=qesMX_wAAAAJ" target="_blank" rel="noopener noreferrer">View all on Google Scholar ↗</a></em></small></p>{% endif %}
</details>
</div>
<hr />

#### Post-Doc
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-1">
    <div class="square">
    <a href="https://github.com/popcornell" target="_blank" rel="noopener noreferrer">
        <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/samuele.jpg">
    </a></div>
        <div class="caption">
            Samuele Cornell
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-1">
    </div>
    <div class="col-sm mt-3 mt-md-1">
    </div>
    <div class="col-sm mt-3 mt-md-1">
    </div>
</div>
<!-- <div class="row mt-3">
    <div class="col-sm mt-3 mt-md-1">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div> -->

<div class="member-pubs-section mt-2">
{% assign pubs = site.data.scholar_pubs.samuele_cornell %}
<details>
<summary><strong>Samuele Cornell</strong> — Publications
{% if pubs.size > 0 %}<small class="text-muted">({{ pubs.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=A3lfL0QAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
{% if pubs.size > 20 %}<p><small><em>Showing 20 of {{ pubs.size }} publications. <a href="https://scholar.google.com/citations?user=A3lfL0QAAAAJ" target="_blank" rel="noopener noreferrer">View all on Google Scholar ↗</a></em></small></p>{% endif %}
</details>
</div>
<hr />


#### PhD Students
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://jctian98.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/jinchuan.jpg">
        </a></div>
        <div class="caption">
            Jinchuan Tian
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://wanchichen.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/william_chen.png">
        </a></div>
        <div class="caption">
            William Chen
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://shikhar-s.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/shikhar.png">
        </a></div>
        <div class="caption">
            Shikhar Bharadwaj
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://cyhuang-tw.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/chienyu.png">
        </a></div>
        <div class="caption">
            Chien-yu Huang
        </div>
    </div>
</div>
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://jaeyeonkim99.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/jaeyeon.jpg">
        </a></div>
        <div class="caption">
            Jaeyeon Kim (co-supervising)
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>

<div class="member-pubs-section mt-2">
{% assign pubs_jinchuan = site.data.scholar_pubs.jinchuan_tian %}
<details>
<summary><strong>Jinchuan Tian</strong> — Publications
{% if pubs_jinchuan.size > 0 %}<small class="text-muted">({{ pubs_jinchuan.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://jctian98.github.io/" target="_blank" rel="noopener noreferrer"><small>Personal Website ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_jinchuan limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
</details>

{% assign pubs_william = site.data.scholar_pubs.william_chen %}
<details>
<summary><strong>William Chen</strong> — Publications
{% if pubs_william.size > 0 %}<small class="text-muted">({{ pubs_william.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=e89NRb0AAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_william limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
{% if pubs_william.size > 20 %}<p><small><em>Showing 20 of {{ pubs_william.size }} publications. <a href="https://scholar.google.com/citations?user=e89NRb0AAAAJ" target="_blank" rel="noopener noreferrer">View all on Google Scholar ↗</a></em></small></p>{% endif %}
</details>

{% assign pubs_shikhar = site.data.scholar_pubs.shikhar_bharadwaj %}
<details>
<summary><strong>Shikhar Bharadwaj</strong> — Publications
{% if pubs_shikhar.size > 0 %}<small class="text-muted">({{ pubs_shikhar.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=pbU47_MAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_shikhar limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
</details>

{% assign pubs_chienyu = site.data.scholar_pubs.chienyu_huang %}
<details>
<summary><strong>Chien-yu Huang</strong> — Publications
{% if pubs_chienyu.size > 0 %}<small class="text-muted">({{ pubs_chienyu.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=1Xfc3ikAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_chienyu limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
</details>

{% assign pubs_jaeyeon = site.data.scholar_pubs.jaeyeon_kim %}
<details>
<summary><strong>Jaeyeon Kim</strong> — Publications
{% if pubs_jaeyeon.size > 0 %}<small class="text-muted">({{ pubs_jaeyeon.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=2Yi8qMIAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
{% if pubs_jaeyeon.size == 0 %}
<p><em>No publications yet in lab bibliography. <a href="https://scholar.google.com/citations?user=2Yi8qMIAAAAJ" target="_blank" rel="noopener noreferrer">View on Google Scholar ↗</a></em></p>
{% else %}
<ol class="pub-list">
{% for pub in pubs_jaeyeon limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
{% endif %}
</details>
</div>
<hr />

#### Master Students
<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
      <div class="square">
        <a href="https://masao-someki.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/msomeki.png">
        </a></div>
        <div class="caption">
            Masao Someki
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>

<div class="member-pubs-section mt-2">
{% assign pubs_masao = site.data.scholar_pubs.masao_someki %}
<details>
<summary><strong>Masao Someki</strong> — Publications
{% if pubs_masao.size > 0 %}<small class="text-muted">({{ pubs_masao.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://masao-someki.github.io/" target="_blank" rel="noopener noreferrer"><small>Personal Website ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_masao limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
</details>
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


<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
	  <div class="square">
          <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/photo-dahee.jpg">
        </div>
        <div class="caption">
            Dahee Yang
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
      <div class="square">
        <a href="https://chinjouli.github.io/mysite" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/chinjou.jpg">
        </a></div>
        <div class="caption">
            Chin-Jou Li
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
      <div class="square">
        <a href="https://www.linkedin.com/in/thanapat-trachu-602551227/" target="_blank" rel="noopener noreferrer">
          <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/thanapat.jpg">
        </a></div>
        <div class="caption">
            Thanapat Trachu
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>
<hr />

#### Industrial Collaborators

<div class="row mt-3">
    <div class="col-sm mt-3 mt-md-0">
        <div class="square">
        <a href="https://jungjee.github.io/" target="_blank" rel="noopener noreferrer">
            <img class="img-fluid rounded z-depth-1" src="{{ site.baseurl }}/assets/img/jeeweon.png">
        </a></div>
        <div class="caption">
            Jee-weon Jung
        </div>
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
    <div class="col-sm mt-3 mt-md-0">
    </div>
</div>

<div class="member-pubs-section mt-2">
{% assign pubs_jeeweon = site.data.scholar_pubs.jeeweon_jung %}
<details>
<summary><strong>Jee-weon Jung</strong> — Publications
{% if pubs_jeeweon.size > 0 %}<small class="text-muted">({{ pubs_jeeweon.size }} in lab bibliography)</small>{% endif %}
&nbsp;<a href="https://scholar.google.com/citations?user=A5OcLdAAAAAJ" target="_blank" rel="noopener noreferrer"><small>Full Google Scholar ↗</small></a>
</summary>
<ol class="pub-list">
{% for pub in pubs_jeeweon limit:20 %}
<li>{% assign pub_url = pub.url | strip %}{% assign sch8 = pub_url | slice: 0, 8 | downcase %}{% assign sch7 = pub_url | slice: 0, 7 | downcase %}{% if sch8 == 'https://' or sch7 == 'http://' %}<a href="{{ pub_url | escape }}" target="_blank" rel="noopener noreferrer">{{ pub.title | escape }}</a>{% else %}{{ pub.title | escape }}{% endif %}
<span class="pub-venue">{% if pub.venue %}{{ pub.venue | escape }}, {% endif %}{{ pub.year | escape }}</span></li>
{% endfor %}
</ol>
{% if pubs_jeeweon.size > 20 %}<p><small><em>Showing 20 of {{ pubs_jeeweon.size }} publications. <a href="https://scholar.google.com/citations?user=A5OcLdAAAAAJ" target="_blank" rel="noopener noreferrer">View all on Google Scholar ↗</a></em></small></p>{% endif %}
</details>
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



