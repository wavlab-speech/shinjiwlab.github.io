# Add yourself to the Members page

The [Members page](https://www.wavlab.org/members/) comes from one data file.
To add yourself, edit that file and add a photo. You do not write any HTML.

The site gets your publication list from Google Scholar. You do not write the
list, and you do not edit it.

---

## Before you start

You need these two items:

- **A photo.** Use a square photo. The card cuts the photo to a circle of 72
  pixels.
- **Your Google Scholar ID.** This item is optional. Open your Google Scholar
  profile. Copy the `user=` part of the address:

  ```
  https://scholar.google.com/citations?user=U5xRA6QAAAAJ&hl=en
                                            ^^^^^^^^^^^^
                                            this is your scholar_id
  ```

If you do not have a Google Scholar profile, do not add the `scholar_id` field.
Your card is still correct. The card shows "No publications listed yet". The
card does not show a Google Scholar link.

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
| `id` | yes | A unique name in lower case. Use the form `firstname_lastname`. The data file `_data/scholar_pubs/<id>.yml` uses this name also. |
| `name` | yes | The card shows this name. The card shows the name as you write it. |
| `role` | yes | This field selects your group on the page. See the list below. |
| `scholar_id` | no | The 12 characters from your Google Scholar address. Without this field, the site gets no publications for you. |
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
| The next Sunday | A scheduled workflow starts `bin/fetch_scholar.py`. The script makes the file `_data/scholar_pubs/<id>.yml`. The script gets your publications. The workflow then opens a pull request. |
| A person merges that pull request | Your publication list and your publication count come on the card. |

To get your publications immediately, start the script yourself. Then add the
result to your own pull request.

```bash
pip install scholarly pyyaml
python3 bin/fetch_scholar.py
```

Google Scholar limits the number of requests. Thus the script can fail. You
can start the script again safely. The script does not replace good data with
empty data or with too little data.

To make only the empty data files, use this command. This command does not use
the network.

```bash
python3 bin/fetch_scholar.py --enrich-only
```

### Incorrect titles

Google Scholar changes the letters in a title. Example: Google Scholar changes
`POWSM` to `Powsm`. Google Scholar also shows many published papers as arXiv
preprints.

The script corrects these errors. The script compares each title with the
titles in `_bibliography/papers.bib`. If the script finds the paper in that
file, the script uses the curated title, venue, year, and link.

To correct your entry, add your paper to `_bibliography/papers.bib`. This
correction improves the Publications page and your member card. After you edit
that file, use this command:

```bash
python3 bin/fetch_scholar.py --enrich-only
```

The script keeps the Google Scholar data for all other papers. A note at the
top of the Members page tells the readers about this limit. The note sends the
readers to your personal page.

---

## Change or remove your entry

To change your photo, your address, or your name, edit your entry in
`_data/members.yml`. Then open a pull request. No other file refers to you.

To change your role, edit the `role` field. You move to the new group
automatically. Your publications move with you.

When you leave the lab, do these three steps:

1. Delete your entry from `_data/members.yml`.
2. Delete the file `_data/scholar_pubs/<id>.yml`.
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
The count shows the number of different papers in your Google Scholar profile.
The script removes the duplicate papers first. Thus this count can differ from
the count in Google Scholar. If the count is very different, examine your
Google Scholar profile. The profile can contain papers from a different person
with your name. Correct your profile. The site then corrects the count at the
next run.

**The card shows only 20 papers.**
This quantity is correct. The card shows your 20 most recent papers. The card
also gives a link to your full Google Scholar profile.
