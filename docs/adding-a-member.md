# Add yourself to the Members page

The [Members page](https://www.wavlab.org/members/) comes from one data file.
To add yourself, edit that file and add a photo. You do not write any HTML.

The site makes your publication list from two sources: the lab's list of
papers (`_bibliography/papers.bib`) and your public ORCID record. You do not
write the list on the Members page.

---

## Before you start

You need these items:

- **A photo.** Use a square photo. The card cuts the photo to a circle of 72
  pixels.
- **Your ORCID iD.** This item is optional. Open your record on
  <https://orcid.org/>. Copy the iD at the end of the address:

  ```
  https://orcid.org/0000-0002-5970-8631
                    ^^^^^^^^^^^^^^^^^^^
                    this is your orcid
  ```

  The site uses only the works that you made public in your ORCID record.
- **Your Google Scholar ID.** This item is optional. The card uses it only for
  a "Google Scholar" link. The site gets no data from Google Scholar. Open your
  Google Scholar profile. Copy the `user=` part of the address:

  ```
  https://scholar.google.com/citations?user=U5xRA6QAAAAJ&hl=en
                                            ^^^^^^^^^^^^
                                            this is your scholar_id
  ```

If you do not have an ORCID iD, do not add the `orcid` field. Your card is
still correct. Your list then shows only your papers in
`_bibliography/papers.bib`. If you do not have a Google Scholar profile, do not
add the `scholar_id` field. The card then shows no Google Scholar link.

---

## Procedure

### 1. Make a branch from `source`

The default branch is `source`. The default branch is not `main`.

> **CAUTION: Do not edit the `master` branch. The deploy workflow writes that
> branch. Your changes to `master` will be lost.**

```bash
git clone https://github.com/wavlab-speech/shinjiwlab.github.io.git
cd shinjiwlab.github.io
git checkout source
git pull
git checkout -b add-member-yourname
```

### 2. Add your photo

Put your photo in the `assets/img/` directory.

```bash
cp ~/Downloads/my-photo.jpg assets/img/yourname.jpg
```

### 3. Add yourself to `_data/members.yml`

Add your entry at the end of the group for your role. The sequence in each
group is the sequence on the page.

```yaml
- id: your_name
  name: Your Name
  role: phd
  scholar_id: XXXXXXXXXXXX
  orcid: 0000-0000-0000-0000
  website: https://yourname.github.io/
  image: yourname.jpg
```

### 4. Look at the page on your computer

```bash
bundle install
bundle exec jekyll serve
```

Open <http://localhost:4000/members/>. Then do these three checks:

1. Make sure that your card is in the correct group.
2. Make sure that the shape of your photo is correct.
3. Make sure that your links open the correct pages.

### 5. Open a pull request

```bash
git add _data/members.yml assets/img/yourname.jpg
git commit -m "Add Your Name to members"
git push origin add-member-yourname
gh pr create --base source --title "Add Your Name to members"
```

> **CAUTION: Add only these two files. Do not add the `_site/` directory. The
> build makes that directory.**

---

## The fields

| Field | Necessary | Description |
|---|---|---|
| `id` | yes | A unique name in lower case. Use the form `firstname_lastname`. The data file `_data/member_pubs/<id>.yml` uses this name also. |
| `name` | yes | The card shows this name. The card shows the name as you write it. The script also finds your papers in `_bibliography/papers.bib` by this full name. |
| `role` | yes | This field selects your group on the page. See the list below. |
| `orcid` | no | Your ORCID iD, for example `0000-0002-5970-8631`. The site adds the public works of your ORCID record to your list. |
| `bib_names` | no | Other spellings of your name in `_bibliography/papers.bib`, as a list. Example: `["S. Watanabe"]`. Use this field only if the script does not find your papers by your full name. |
| `scholar_id` | no | The 12 characters from your Google Scholar address. The card uses it only for the "Google Scholar" link. |
| `website` | no | The address must start with `http://` or `https://`. The card removes all other addresses. |
| `image` | no | The name of your photo file in `assets/img/`. |
| `note` | no | The card shows this text in parentheses after your name. Example: `co-supervising`. |

### The permitted roles

```
faculty | postdoc | phd | master | visitor | industrial
```

> **CAUTION: Write the `role` value correctly. An incorrect value removes you
> from the page. The build does not fail, and you get no error message. If
> your card is not on the page, examine this field first.**

---

## How you get your publication list

You do not do anything. The site adds your publications in three steps:

| Time | Result |
|---|---|
| A person merges your pull request | Your card comes on the page. The card shows "No publications listed yet". |
| The next Sunday | A scheduled workflow starts `bin/fetch_publications.py`. The script makes the file `_data/member_pubs/<id>.yml`. The script gets your papers from `_bibliography/papers.bib` and from your public ORCID record. The workflow then opens a pull request. |
| A person merges that pull request | Your publication list and your publication count come on the card. |

To get your publications immediately, start the script yourself. Then add the
result to your own pull request.

```bash
pip install pyyaml
python3 bin/fetch_publications.py
```

The script needs no account and no key. It sends one request to the public
ORCID API for each member who has an `orcid` field.

If an ORCID request fails, the script does not change that member's file. You
can start the script again safely. The script also does not replace a list
with a list that is much shorter from the same source.

### Keep your ORCID record current

The site shows only the works that are public in your ORCID record. ORCID does
not always add your papers by itself. For example, the 2025 DOI records of
Interspeech and ACL papers carry no ORCID iD, so ORCID's automatic update from
Crossref cannot add these papers to your record. Add each missing paper to
your ORCID record yourself, and make it public. For instructions, see the
ORCID help center at <https://support.orcid.org/hc>.

### Incorrect titles

When a paper is in `_bibliography/papers.bib` and in your ORCID record, the
script uses the curated title, venue, year, and link from
`_bibliography/papers.bib`. The script compares the titles to find the same
paper.

To correct your entry, add your paper to `_bibliography/papers.bib`. This
correction improves the Publications page and your member card. After you edit
that file, start the script again:

```bash
python3 bin/fetch_publications.py
```

The script keeps the ORCID data for all other papers. A note at the top of the
Members page tells the readers about this limit. The note sends the readers to
your personal page.

### Links

Each title on the card links to the paper when the script finds a link. The
script uses the link from `_bibliography/papers.bib` first, and then the link
from your ORCID record. If neither source has a link, the script uses the link
that the site stored from Google Scholar until 2026-10-18
(`bin/scholar_links.yml`). Some of these links open the paper page on Google
Scholar. Nothing updates that file.

To add or correct a link, add an `html`, `pdf`, `arxiv`, or `doi` field to your
paper in `_bibliography/papers.bib`.

---

## Change or remove your entry

To change your photo, your address, or your name, edit your entry in
`_data/members.yml`. Then open a pull request. No other file refers to you.

To change your role, edit the `role` field. You move to the new group
automatically. Your publications move with you.

When you leave the lab, do these three steps:

1. Delete your entry from `_data/members.yml`.
2. Delete the file `_data/member_pubs/<id>.yml`.
3. Add your name to the Alumni list at the bottom of `_pages/members.md`. Give
   your dates and your new organization. This list is still HTML.

---

## Problems and solutions

**My card is not on the page.**
Examine the `role` field. The value must be one of the six permitted values.

**The card does not show my website.**
The address must start with `http://` or `https://`. The card removes an
address such as `yourname.github.io`. This rule prevents unsafe links.

**My photo has an incorrect shape.**
The card cuts each photo to a circle. Cut your photo to a square first.

**My publication count is incorrect.**
The count shows the number of different papers in `_bibliography/papers.bib`
and in the public part of your ORCID record together. The script removes the
duplicate papers first. Thus this count can differ from the count in ORCID. If
the count is too low, make sure that your works are public in ORCID. If the
count is too high, examine your ORCID record for papers from a different
person. Correct your record. The site then corrects the count at the next run.

**My list is missing a paper.**
Add the paper to your ORCID record and make it public. If it is a lab paper,
make sure that it is in `_bibliography/papers.bib` with your full name in the
author list.

**The card shows only 20 papers.**
This quantity is correct. The card shows your 20 most recent papers. The card
also gives a link to your full ORCID record, or to your Google Scholar profile
if you have no ORCID iD.

ORCID gives a year but no month for most works. Thus, in each year, your
ORCID works that are not in `_bibliography/papers.bib` come first, the most
recently added work first. Then your papers in `_bibliography/papers.bib`
come, in the sequence of that file.
