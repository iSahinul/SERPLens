"""SERPLens command line: python -m serplens prompt-scan ..."""
from __future__ import annotations

import argparse
import datetime
import os
import re
import sys

from . import __version__
from .gsc import fetch_query_page_rows
from .prompt_scan import (aggregate, print_summary, prompt_like,
                          proven_demand, render_markdown)


def _slug(property_url: str) -> str:
    s = re.sub(r"^https?://", "", property_url)
    s = re.sub(r"^sc-domain:", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "property"


def cmd_prompt_scan(args) -> int:
    if not os.path.exists(args.credentials):
        print(f"Credentials file not found: {args.credentials}",
              file=sys.stderr)
        print("Create a Google Cloud service account, download its JSON "
              "key, and add the account's email as a user on your Search "
              "Console property. See README → Setup.", file=sys.stderr)
        return 2
    rows = fetch_query_page_rows(args.credentials, args.property,
                                 days=args.days)
    if not rows:
        print("No Search Console rows returned for that property/window. "
              "Check the property URL matches GSC exactly (including "
              "sc-domain: form) and the service account has access.")
        return 1
    queries = aggregate(rows)
    prompt_items = prompt_like(queries)
    proven_items = proven_demand(queries)
    out = args.out or (f"serplens-prompt-scan-{_slug(args.property)}-"
                       f"{datetime.date.today().isoformat()}.md")
    md = render_markdown(args.property, args.days, prompt_items,
                         proven_items)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print_summary(prompt_items, proven_items)
    print(f"\nReport written: {out}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="serplens",
        description="SERPLens — read your Search Console data through "
                    "an AEO lens.")
    p.add_argument("--version", action="version",
                   version=f"SERPLens {__version__}")
    sub = p.add_subparsers(dest="command", required=True)
    ps = sub.add_parser(
        "prompt-scan",
        help="Find prompt-like (8+ word) queries you already appear "
             "for, with an EDIT / WATCH / GAP verdict for each.")
    ps.add_argument("--property", required=True,
                    help="GSC property exactly as in Search Console, "
                         "e.g. https://example.com/ or "
                         "sc-domain:example.com")
    ps.add_argument("--credentials", required=True,
                    help="Path to your Google service-account JSON key")
    ps.add_argument("--days", type=int, default=28,
                    help="Lookback window in days (default 28)")
    ps.add_argument("--out", default=None,
                    help="Report file path (default: "
                         "serplens-prompt-scan-<property>-<date>.md)")
    ps.set_defaults(func=cmd_prompt_scan)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
