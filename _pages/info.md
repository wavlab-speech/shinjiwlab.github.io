---
layout: page
permalink: /info/
title: Info
description: Information and guidelines for members of WAVLab.
nav: true
order: 8

# Each card either points at a lab post (give its `slug`) or at an arbitrary URL
# (give `url` for an internal page or `external` for an off-site one). A `title`
# or `blurb` here overrides the post's own; the cards read better with one, and
# keeping the text here leaves the posts untouched, so the "Updated" date stays
# a record of when the guide itself last changed. To add a guide, add one entry.
# The tracker is the only page here that changes on its own, so it leads as a
# full-width card rather than competing with the static guides in a grid.
feature:
  title: "Conference deadline tracker"
  url: /conferences/
  blurb: "Live countdowns for the conferences the lab follows."
  icon: "fas fa-calendar-alt"

sections:
  - name: "Clusters and compute"
    icon: "fas fa-server"
    items:
      - slug: babel-usage
        title: "Babel"
        blurb: "LTI's cluster: access, GPU limits, storage layout, and ESPnet on Slurm."
      - slug: tir-usage
        title: "TIR"
        tag: "for ESPnet users"
        blurb: "CMU's TIR cluster: Slurm jobs, modules, and ESPnet and Kaldi installation."
      - slug: psc-usage
        title: "PSC"
        blurb: "ACCESS account setup, SSH login, GPU and CPU partitions, and ESPnet installation."
      - slug: delta-usage
        title: "Delta"
        blurb: "NCSA account setup, login, partitions, and ESPnet and Kaldi installation."
      - slug: aws-usage
        title: "AWS"
        blurb: "Launching a GPU instance, sharing access, and installing ESPnet."
  - name: "Tools and templates"
    icon: "fas fa-tools"
    items:
      - slug: espnet2-recipe
        title: "ESPnet2 recipes"
        blurb: "How to make an ESPnet2 recipe from scratch."
      - slug: dependency-jobs
        title: "SLURM dependency jobs"
        blurb: "Chain sequential Slurm jobs so each starts after the previous one finishes."
      - title: "Lab logos and slides template"
        external: https://github.com/wavlab-speech/lab_logo
        blurb: "Need to request access."

gallery_icon: "fas fa-images"
galleries:
  - slug: 2023-record
    year: 2023
    thumb: assets/img/gallery/thumbs/2023.jpg
  - slug: 2022-record
    year: 2022
    thumb: assets/img/gallery/thumbs/2022.jpg
  - slug: 2021-record
    year: 2021
    thumb: assets/img/gallery/thumbs/2021.jpg
---

<style>
  /* al-folio maps --global-text-color-light to the body colour in dark mode, so
     a blurb using it would match its own card title and lose the hierarchy.
     Define the three tones locally instead, the way the Positions page does.
     The whole card is the link, so its border is the control's boundary: these
     alphas put it at 3.18:1 (light) and 3.13:1 (dark) against the page. */
  :root {
    --info-border: rgba(0, 0, 0, 0.42);
    --info-surface: rgba(0, 0, 0, 0.022);
    --info-muted: rgba(0, 0, 0, 0.58);
  }
  html[data-theme='dark'] {
    --info-border: rgba(255, 255, 255, 0.38);
    --info-surface: rgba(255, 255, 255, 0.05);
    --info-muted: rgba(255, 255, 255, 0.74);
  }

  /* The one page here that changes on its own leads the page, so the eye has a
     place to land before the reference shelf below. Border-left accent matches
     the .pos-status idiom on the Positions page. */
  .info-feature {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1.6rem 0 0.4rem;
    padding: 1.1rem 1.25rem;
    border: 1px solid var(--info-border);
    border-left: 3px solid var(--global-theme-color);
    border-radius: 0 8px 8px 0;
    background-color: var(--info-surface);
    color: var(--global-text-color);
    text-decoration: none;
    transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  }
  .info-feature:hover,
  .info-feature:focus-visible {
    border-color: var(--global-theme-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    text-decoration: none;
  }
  .info-feature:focus-visible {
    outline: 2px solid var(--global-theme-color);
    outline-offset: 2px;
  }
  .info-feature:hover .info-feature-title { color: var(--global-theme-color); }
  .info-feature-icon {
    flex: none;
    font-size: 1.6rem;
    color: var(--global-theme-color);
    line-height: 1;
  }
  .info-feature-body { display: flex; flex-direction: column; gap: 0.2rem; }
  .info-feature-title { font-weight: 600; font-size: 1.15rem; line-height: 1.3; }
  .info-feature-blurb { font-size: 0.9rem; line-height: 1.5; color: var(--info-muted); }

  .info-heading {
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--info-muted);
    margin: 2.4rem 0 0.9rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--info-border);
  }

  /* auto-fill + minmax drops to a single column on a phone without a query. */
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
    gap: 0.9rem;
  }

  /* The whole card is the anchor, so it is one tab stop rather than a box
     wrapped around a separate link. */
  .info-card {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.85rem 1rem;
    border: 1px solid var(--info-border);
    border-radius: 8px;
    background-color: var(--info-surface);
    color: var(--global-text-color);
    text-decoration: none;
    transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  }
  .info-card:hover,
  .info-card:focus-visible {
    border-color: var(--global-theme-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    text-decoration: none;
  }
  .info-card:focus-visible {
    outline: 2px solid var(--global-theme-color);
    outline-offset: 2px;
  }
  .info-card:hover .info-card-title { color: var(--global-theme-color); }

  .info-card-title {
    font-weight: 600;
    font-size: 1rem;
    line-height: 1.35;
  }
  .info-card-blurb {
    font-size: 0.85rem;
    line-height: 1.5;
    color: var(--info-muted);
  }
  /* Read from git history, not front matter: several guides carry a 2022 date
     but have been revised since, and one has not been touched since 2022. */
  .info-meta {
    margin-top: 0.15rem;
    font-size: 0.75rem;
    letter-spacing: 0.02em;
    color: var(--info-muted);
  }
  .info-heading i { margin-right: 0.5rem; opacity: 0.8; }
  .info-tag {
    display: inline-block;
    margin-left: 0.4rem;
    padding: 0.05rem 0.45rem;
    border: 1px solid var(--info-border);
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    color: var(--info-muted);
    vertical-align: 0.1em;
  }
  .info-ext {
    font-size: 0.8em;
    color: var(--info-muted);
  }
  .info-missing { color: #c0392b; font-weight: 600; }

  .info-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
    gap: 0.9rem;
  }
  .info-tile {
    display: block;
    overflow: hidden;
    border: 1px solid var(--info-border);
    border-radius: 8px;
    background-color: var(--info-surface);
    color: var(--global-text-color);
    text-decoration: none;
    transition: border-color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
  }
  .info-tile:hover,
  .info-tile:focus-visible {
    border-color: var(--global-theme-color);
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    text-decoration: none;
  }
  .info-tile:focus-visible {
    outline: 2px solid var(--global-theme-color);
    outline-offset: 2px;
  }
  .info-tile img {
    display: block;
    width: 100%;
    /* The width/height attributes reserve space while the image loads, but they
       also set height in px, and aspect-ratio only applies when height is auto. */
    height: auto;
    aspect-ratio: 3 / 2;
    object-fit: cover;
  }
  .info-tile-label {
    padding: 0.6rem 0.85rem;
    font-weight: 600;
  }
  .info-tile:hover .info-tile-label { color: var(--global-theme-color); }

  @media (prefers-reduced-motion: reduce) {
    .info-card,
    .info-tile { transition: none; }
    .info-card:hover,
    .info-card:focus-visible,
    .info-tile:hover,
    .info-tile:focus-visible { transform: none; }
  }
</style>

<a class="info-feature" href="{{ page.feature.url | relative_url }}">
  <span class="info-feature-icon"><i class="{{ page.feature.icon }}" aria-hidden="true"></i></span>
  <span class="info-feature-body">
    <span class="info-feature-title">{{ page.feature.title | escape }}</span>
    <span class="info-feature-blurb">{{ page.feature.blurb | escape }}</span>
  </span>
</a>

{% for section in page.sections %}
<h2 class="info-heading">{% if section.icon %}<i class="{{ section.icon }}" aria-hidden="true"></i>{% endif %}{{ section.name | escape }}</h2>
<div class="info-grid">
  {%- for item in section.items -%}
    {%- comment -%}
      A bad `slug` cannot fail the build the way `post_url` does, so render it
      loudly instead of emitting a silently empty card.
    {%- endcomment -%}
    {%- assign post = site.posts | where: "slug", item.slug | first -%}
    {%- assign missing = false -%}
    {%- assign external = false -%}
    {%- if item.slug -%}
      {%- if post -%}
        {%- assign href = post.url | relative_url -%}
        {%- assign card_title = item.title | default: post.title -%}
        {%- assign blurb = item.blurb | default: post.description -%}
        {%- assign updated = post.last_modified_at -%}
      {%- else -%}
        {%- assign missing = true -%}
        {%- assign href = "#" -%}
        {%- assign card_title = item.title | default: item.slug -%}
        {%- assign blurb = "Missing post for slug: " | append: item.slug -%}
        {%- assign updated = nil -%}
      {%- endif -%}
    {%- elsif item.external -%}
      {%- assign external = true -%}
      {%- assign href = item.external -%}
      {%- assign card_title = item.title -%}
      {%- assign blurb = item.blurb -%}
      {%- assign updated = nil -%}
    {%- else -%}
      {%- assign href = item.url | relative_url -%}
      {%- assign card_title = item.title -%}
      {%- assign blurb = item.blurb -%}
      {%- assign updated = nil -%}
    {%- endif -%}
  <a class="info-card" href="{{ href | escape }}"{% if external %} target="_blank" rel="noopener"{% endif %}>
    <span class="info-card-title{% if missing %} info-missing{% endif %}">{{ card_title | escape }}{% if item.tag %}<span class="info-tag">{{ item.tag | escape }}</span>{% endif %}{% if external %} <span class="info-ext" aria-hidden="true">&#8599;</span><span class="sr-only">(opens in a new tab)</span>{% endif %}</span>
    {%- if blurb %}<span class="info-card-blurb">{{ blurb | escape }}</span>{% endif -%}
    {%- if updated %}<span class="info-meta">Updated {{ updated | date: "%b %Y" }}</span>{% endif -%}
  </a>
  {%- endfor -%}
</div>
{% endfor %}

<h2 class="info-heading">{% if page.gallery_icon %}<i class="{{ page.gallery_icon }}" aria-hidden="true"></i>{% endif %}Galleries</h2>
<div class="info-gallery">
  {%- for g in page.galleries -%}
    {%- assign post = site.posts | where: "slug", g.slug | first -%}
    {%- if post -%}
  <a class="info-tile" href="{{ post.url | relative_url }}">
    <img src="{{ g.thumb | relative_url }}" width="600" height="400" loading="lazy"
         alt="Photo from the {{ g.year }} lab activities gallery">
    <span class="info-tile-label">{{ g.year }} Gallery</span>
  </a>
    {%- else -%}
  <a class="info-tile" href="#"><span class="info-tile-label info-missing">Missing post for slug: {{ g.slug | escape }}</span></a>
    {%- endif -%}
  {%- endfor -%}
</div>
