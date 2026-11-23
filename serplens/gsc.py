"""Google Search Console API access (service-account auth).

Setup: create a Google Cloud service account with a JSON key, then add
the service account's email as a user on your Search Console property.
That is the standard pattern for server-side GSC tools — your key file
never leaves your machine.
"""
from __future__ import annotations

import datetime

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
ROW_LIMIT = 25000


def _service(credentials_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def fetch_query_page_rows(credentials_path: str, property_url: str,
                          days: int = 28) -> list[dict]:
    """Return Search Analytics rows for the last `days` days (ending
    3 days ago, to let GSC data settle), one row per (query, page):
    {query, page, clicks, impressions, position}."""
    end = datetime.date.today() - datetime.timedelta(days=3)
    start = end - datetime.timedelta(days=days - 1)
    service = _service(credentials_path)
    rows: list[dict] = []
    start_row = 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query", "page"],
            "rowLimit": ROW_LIMIT,
            "startRow": start_row,
            "dataState": "final",
        }
        resp = service.searchanalytics().query(
            siteUrl=property_url, body=body
        ).execute()
        batch = resp.get("rows", [])
        for r in batch:
            rows.append({
                "query": r["keys"][0],
                "page": r["keys"][1],
                "clicks": r.get("clicks", 0),
                "impressions": r.get("impressions", 0),
                "position": r.get("position", 0.0),
            })
        if len(batch) < ROW_LIMIT:
            break
        start_row += ROW_LIMIT
    return rows
