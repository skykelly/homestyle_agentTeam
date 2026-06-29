"""
Google Analytics 4 connector.

Real API: requires GA4_SERVICE_ACCOUNT_JSON + GA4_PROPERTY_ID env vars.
Docs: https://developers.google.com/analytics/devguides/reporting/data/v1
"""

import os
from connectors.base import BaseConnector


class GA4Connector(BaseConnector):
    connector_id = "GA4"
    display_name = "Google Analytics 4"

    def is_available(self) -> bool:
        return bool(
            os.getenv("GA4_SERVICE_ACCOUNT_JSON") and os.getenv("GA4_PROPERTY_ID")
        )

    def fetch(self, days: int = 28, **kwargs) -> list[dict]:
        """
        Real implementation — requires google-analytics-data.
        Install: pip install google-analytics-data

        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Dimension, Metric
        )
        from google.oauth2 import service_account
        import json

        sa_json = json.loads(os.getenv("GA4_SERVICE_ACCOUNT_JSON"))
        creds = service_account.Credentials.from_service_account_info(
            sa_json,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
        client = BetaAnalyticsDataClient(credentials=creds)

        from datetime import date, timedelta
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=days)).isoformat()

        request = RunReportRequest(
            property=f"properties/{os.getenv('GA4_PROPERTY_ID')}",
            dimensions=[Dimension(name="landingPage"), Dimension(name="sessionSource")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="engagedSessions"),
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        resp = client.run_report(request)

        rows = []
        for row in resp.rows:
            rows.append({
                "url": row.dimension_values[0].value,
                "source": row.dimension_values[1].value,
                "sessions": int(row.metric_values[0].value),
                "engaged_sessions": int(row.metric_values[1].value),
                "conversions": int(row.metric_values[2].value),
                "revenue_krw": float(row.metric_values[3].value),
                "conversion_rate": (
                    int(row.metric_values[2].value) /
                    max(int(row.metric_values[0].value), 1)
                ),
            })
        return rows
        """
        raise NotImplementedError("Install google-analytics-data and set GA4_SERVICE_ACCOUNT_JSON")

    def mock_data(self, **kwargs) -> list[dict]:
        from data.seo_mock_data import get_ga4_landing
        all_urls = [
            "/skincare/collagen-serum-guide", "/skincare/hyaluronic-acid",
            "/skincare/retinol-guide", "/makeup/cushion-foundation",
            "/haircare/scalp-treatment",
        ]
        rows = []
        for url in all_urls:
            ga4 = get_ga4_landing(url)
            if ga4:
                r = ga4[0]
                rows.append({
                    "url": r.url,
                    "source": r.source,
                    "sessions": r.sessions,
                    "engaged_sessions": r.engaged_sessions,
                    "conversions": r.conversions,
                    "revenue_krw": r.revenue_krw,
                    "conversion_rate": r.conversion_rate,
                })
        return rows
