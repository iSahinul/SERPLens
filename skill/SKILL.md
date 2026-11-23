---
name: serplens
description: Use when someone wants to find the prompt-like, question-shaped queries their site already appears for in Google Search Console (AEO / AI-search opportunities), run a SERPLens prompt-scan, set up Search Console API access for it, or interpret a SERPLens report — the EDIT CANDIDATE, WATCH and CONTENT GAP verdicts and the proven-demand list.
---

# SERPLens — Search Console through an AEO lens

SERPLens (github.com/iSahinul/SERPLens) is a free CLI toolkit whose first
tool, `prompt-scan`, finds the long, question-shaped queries a site
already appears for in Google Search Console — the same shape as prompts
people type into AI search — and gives each a verdict.

## Running a scan

```bash
git clone https://github.com/iSahinul/SERPLens.git
cd SERPLens
pip install -r requirements.txt

python -m serplens prompt-scan \
  --property https://example.com/ \
  --credentials /path/to/service-account.json
```

- `--property` must match Search Console exactly: `https://example.com/`
  for a URL-prefix property, `sc-domain:example.com` for a domain
  property.
- `--days` defaults to 28. `--out` sets the report path; by default a
  dated markdown report is written to the working directory.
- Output: a terminal summary plus the markdown report with two tables —
  prompt-like queries with verdicts, and the proven-demand list.

## Setup (service account)

The tool reads GSC with the user's own Google service-account key:

1. Google Cloud Console → enable the **Google Search Console API**.
2. Create a service account + JSON key; download the key file.
3. Search Console → property → Settings → Users and permissions → add
   the service account's email as a user.
4. **Key safety:** refer to the key by file path only. Never ask the
   user to paste the key's contents into chat, never copy it into the
   repo, and confirm it is covered by `.gitignore` before any commit.

## Reading the report — the verdicts

- **EDIT CANDIDATE** (position 3.5–20): ranking but not winning. The
  fix: a 40–60 word direct answer near the top of the ranking page,
  and the same question in the page's FAQ if it has one.
- **WATCH** (position ≤ 3.5, 0 clicks): the site likely *is* the
  answer already — featured snippet or AI-overview absorption.
  Editing rarely helps; recommend observing, not changing.
- **CONTENT GAP** (position > 20): not really ranking. This is a
  topic decision (write something new, or don't), never an edit.

Positions are impression-weighted across the query's pages; "Top page"
is the page with the most impressions for that query — that is the page
an EDIT CANDIDATE verdict refers to.

## Proven demand

The second list: queries starting with a question word (how, what,
why…) or running 5+ words, with 3+ impressions, top 25. These are
questions the site's own data proves people ask. Recommend using them
first when researching new content or building an article's FAQ —
they outrank guessed questions.

## Troubleshooting

- **"No rows returned"** — almost always a property-string mismatch or
  the service account was not added to that property. Check both
  before anything else.
- **Credentials file not found** — the path is wrong; ask for the
  correct path to the JSON key (not its contents).
- **Very few prompt-like queries** — normal for young or small sites;
  the proven-demand list is still useful. A wider `--days` window
  (e.g. 90) can help, at the cost of older data.
