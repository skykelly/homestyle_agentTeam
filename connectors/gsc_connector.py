"""
Google Search Console connector.

Real API: requires a service-account JSON at GSC_SERVICE_ACCOUNT_JSON (env)
and GSC_SITE_URL (e.g. "sc-domain:beautylab.co.kr").

Docs: https://developers.google.com/webmaster-tools/v1/api_reference_index
"""

import os
from connectors.base import BaseConnector


class GSCConnector(BaseConnector):
    connector_id = "GSC"
    display_name = "Google Search Console"

    def is_available(self) -> bool:
        return bool(
            os.getenv("GSC_SERVICE_ACCOUNT_JSON") and os.getenv("GSC_SITE_URL")
        )

    def fetch(self, days: int = 28, **kwargs) -> list[dict]:
        """
        Real implementation — requires google-auth + googleapiclient.
        Install: pip install google-auth google-api-python-client

        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import json

        sa_json = json.loads(os.getenv("GSC_SERVICE_ACCOUNT_JSON"))
        creds = service_account.Credentials.from_service_account_info(
            sa_json, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=creds)

        from datetime import date, timedelta
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=days)).isoformat()

        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": ["query", "page", "device", "country"],
            "rowLimit": 5000,
        }
        resp = service.searchanalytics().query(
            siteUrl=os.getenv("GSC_SITE_URL"), body=body
        ).execute()

        rows = []
        for r in resp.get("rows", []):
            keys = r["keys"]
            rows.append({
                "query": keys[0],
                "url": keys[1],
                "device": keys[2],
                "country": keys[3],
                "clicks": r["clicks"],
                "impressions": r["impressions"],
                "ctr": r["ctr"],
                "position": r["position"],
            })
        return rows
        """
        raise NotImplementedError("Install google-auth and set GSC_SERVICE_ACCOUNT_JSON")

    def mock_data(self, **kwargs) -> list[dict]:
        from data.seo_mock_data import get_gsc_queries
        return [
            {
                "query": r.query,
                "url": r.url,
                "device": r.device,
                "country": r.country,
                "clicks": r.clicks,
                "impressions": r.impressions,
                "ctr": r.ctr,
                "position": r.position,
            }
            for r in get_gsc_queries()
        ]
