# AGENTS.md — SERPLens

A Python CLI that reads Google Search Console data via a service-account
key and scans for prompt-like queries, triaged EDIT / WATCH / GAP.

## Working in this repo
- Run tests: `python3 -m unittest discover -s tests`
- Run a scan: `python3 -m serplens.cli --site <property> --key <path>`
- The user-facing skill for this project lives in `skill/SKILL.md` —
  read it before running scans or explaining verdicts.

## House rules
- **Key safety:** refer to the service-account key by path only. Never
  print, paste or commit its contents.
- Triage thresholds are deliberate (prompt-like = 8+ words, impressions
  >= 5; EDIT 3.5–20, WATCH <= 3.5 with 0 clicks, GAP > 20). Do not loosen
  them without saying why.
- Standard library + the Google API client only; no new dependencies
  without a reason.
