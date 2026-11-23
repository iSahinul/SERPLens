"""Prompt-like query scan — the AEO lens on Search Console data.

Technique: in Search Console, long queries (8+ words) are usually real
questions people typed or spoke — the same shape as AI prompts. If your
site already appears for them but earns few clicks, a short direct-answer
block on the ranking page is often the cheapest win in SEO.

Every qualifying query gets a triage verdict:

- EDIT CANDIDATE: position 3.5-20 — ranking but not winning. Add a
  40-60 word direct answer near the top of the ranking page, and repeat
  the question in the page's FAQ if it has one.
- WATCH: position <= 3.5 with 0 clicks — you likely ARE the answer
  (featured snippet / AI overview absorption). Editing rarely helps;
  observe only.
- CONTENT GAP: position > 20 — not really ranking. A topic decision,
  not an edit.

The scan also lists "proven demand": queries that start with a question
word or run 5+ words (impressions >= 3, top 25). These are questions
your own data proves people ask — use them first when researching new
content.
"""
from __future__ import annotations

import datetime

QUESTION_WORDS = {
    "who", "what", "when", "where", "why", "how", "does", "do", "did",
    "can", "could", "should", "is", "are", "was", "were", "which",
    "will", "would", "may",
}

PROMPT_MIN_WORDS = 8
PROMPT_MIN_IMPRESSIONS = 5
PROVEN_MIN_IMPRESSIONS = 3
PROVEN_LIMIT = 25


def verdict(position: float, clicks: int) -> str:
    if position > 20:
        return "CONTENT GAP"
    if position <= 3.5 and clicks == 0:
        return "WATCH"
    return "EDIT CANDIDATE"


def aggregate(rows: list[dict]) -> dict[str, dict]:
    """Collapse (query, page) rows into per-query totals with an
    impression-weighted position and the top page by impressions."""
    out: dict[str, dict] = {}
    for r in rows:
        q = out.setdefault(r["query"], {
            "query": r["query"], "clicks": 0, "impressions": 0,
            "_pos_weighted": 0.0, "top_page": None, "_top_imp": -1,
        })
        q["clicks"] += r["clicks"]
        q["impressions"] += r["impressions"]
        q["_pos_weighted"] += r["impressions"] * r["position"]
        if r["impressions"] > q["_top_imp"]:
            q["_top_imp"] = r["impressions"]
            q["top_page"] = r["page"]
    for q in out.values():
        q["position"] = (q["_pos_weighted"] / q["impressions"]
                         if q["impressions"] else 0.0)
        del q["_pos_weighted"], q["_top_imp"]
    return out


def prompt_like(queries: dict[str, dict]) -> list[dict]:
    items = [q for q in queries.values()
             if len(q["query"].split()) >= PROMPT_MIN_WORDS
             and q["impressions"] >= PROMPT_MIN_IMPRESSIONS]
    for q in items:
        q["verdict"] = verdict(q["position"], q["clicks"])
    return sorted(items, key=lambda q: -q["impressions"])


def proven_demand(queries: dict[str, dict]) -> list[dict]:
    items = []
    for q in sorted(queries.values(), key=lambda q: -q["impressions"]):
        words = q["query"].lower().split()
        if not words or q["impressions"] < PROVEN_MIN_IMPRESSIONS:
            continue
        if words[0] not in QUESTION_WORDS and len(words) < 5:
            continue
        items.append(q)
        if len(items) >= PROVEN_LIMIT:
            break
    return items


def render_markdown(property_url: str, days: int,
                    prompt_items: list[dict], proven_items: list[dict],
                    today: datetime.date | None = None) -> str:
    today = today or datetime.date.today()
    lines = [
        f"# SERPLens prompt-query scan — {property_url}",
        "",
        f"Generated: {today.isoformat()} · window: last {days} days of "
        "Search Console data",
        "",
        "## Prompt-like queries (8+ words, impressions >= 5)",
        "",
    ]
    if not prompt_items:
        lines += ["(none qualified)", ""]
    else:
        lines += ["| Verdict | Query | Imp | Clicks | Pos | Top page |",
                  "|---|---|---|---|---|---|"]
        for q in prompt_items:
            query = q["query"].replace("|", "\\|")
            lines.append(f"| {q['verdict']} | {query} | {q['impressions']} "
                         f"| {q['clicks']} | {q['position']:.1f} "
                         f"| {q['top_page'] or 'NO PAGE'} |")
        lines.append("")
    lines += [
        "**What to do:** EDIT CANDIDATE — add a 40-60 word direct answer "
        "near the top of the ranking page. WATCH — you are likely the "
        "snippet/AI answer already; leave it. CONTENT GAP — a topic "
        "decision, not an edit.",
        "",
        "## Proven demand (question queries your own data verifies)",
        "",
    ]
    if not proven_items:
        lines += ["(none qualified)", ""]
    else:
        lines += ["| Query | Imp | Clicks | Pos | Top page |",
                  "|---|---|---|---|---|"]
        for q in proven_items:
            query = q["query"].replace("|", "\\|")
            lines.append(f"| {query} | {q['impressions']} | {q['clicks']} "
                         f"| {q['position']:.1f} "
                         f"| {q['top_page'] or 'NO PAGE'} |")
        lines.append("")
    return "\n".join(lines)


def print_summary(prompt_items: list[dict], proven_items: list[dict]) -> None:
    counts = {"EDIT CANDIDATE": 0, "WATCH": 0, "CONTENT GAP": 0}
    for q in prompt_items:
        counts[q["verdict"]] = counts.get(q["verdict"], 0) + 1
    print(f"\nPrompt-like queries: {len(prompt_items)} "
          f"(EDIT {counts['EDIT CANDIDATE']} · WATCH {counts['WATCH']} · "
          f"GAP {counts['CONTENT GAP']})")
    for q in prompt_items:
        print(f"  [{q['verdict']}] {q['impressions']} imp / {q['clicks']} "
              f"clicks / pos {q['position']:.1f} — {q['query']!r} "
              f"-> {q['top_page'] or 'NO PAGE'}")
    print(f"\nProven-demand queries: {len(proven_items)}")
    for q in proven_items:
        print(f"  {q['impressions']} imp / {q['clicks']} clicks / "
              f"pos {q['position']:.1f} — {q['query']!r}")
