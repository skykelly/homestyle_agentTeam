"""
Google Ads connector.

Real API: requires GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CUSTOMER_ID,
          GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN.
Docs: https://developers.google.com/google-ads/api/docs/start

Install: pip install google-ads
"""

import os
from datetime import datetime, timedelta
from connectors.base import BaseConnector


class GoogleAdsConnector(BaseConnector):
    connector_id = "GOOGLE_ADS"
    display_name = "Google Ads"

    def is_available(self) -> bool:
        return bool(
            os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
            and os.getenv("GOOGLE_ADS_CUSTOMER_ID")
            and os.getenv("GOOGLE_ADS_CLIENT_ID")
            and os.getenv("GOOGLE_ADS_CLIENT_SECRET")
            and os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
        )

    def fetch(self, days: int = 28, **kwargs) -> list[dict]:
        """
        Real implementation — requires google-ads SDK.

        from google.ads.googleads.client import GoogleAdsClient

        config = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "use_proto_plus": True,
        }
        client = GoogleAdsClient.load_from_dict(config)
        ga_service = client.get_service("GoogleAdsService")

        from datetime import date, timedelta
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=days)).isoformat()
        customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")

        query = f\"\"\"
            SELECT
              campaign.id,
              campaign.name,
              segments.date,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions,
              metrics.conversions_value
            FROM campaign
            WHERE segments.date BETWEEN '{start}' AND '{end}'
            ORDER BY segments.date DESC
        \"\"\"
        stream = ga_service.search_stream(customer_id=customer_id, query=query)

        rows = []
        for batch in stream:
            for row in batch.results:
                rows.append({
                    "campaign_id": str(row.campaign.id),
                    "campaign_name": row.campaign.name,
                    "date": row.segments.date,
                    "impressions": row.metrics.impressions,
                    "clicks": row.metrics.clicks,
                    "spend_krw": row.metrics.cost_micros / 1_000_000,
                    "conversions": row.metrics.conversions,
                    "revenue_krw": row.metrics.conversions_value,
                    "ctr": row.metrics.clicks / max(row.metrics.impressions, 1),
                    "platform": "google_ads",
                })
        return rows
        """
        raise NotImplementedError(
            "Install google-ads and set GOOGLE_ADS_DEVELOPER_TOKEN/CUSTOMER_ID/CLIENT_ID/"
            "CLIENT_SECRET/REFRESH_TOKEN"
        )

    def mock_data(self, days: int = 28, **kwargs) -> list[dict]:
        from data.korean_market import PLATFORM_BENCHMARKS
        import random
        bench = PLATFORM_BENCHMARKS.get("google", {})
        rows = []
        base_date = datetime.now()
        campaigns = [
            {"id": "gads_camp_001", "name": "BeautyLab_Brand_KW"},
            {"id": "gads_camp_002", "name": "Collagen_Serum_Generic"},
            {"id": "gads_camp_003", "name": "Skincare_Shopping"},
        ]
        for i in range(min(days, 28)):
            date_str = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
            for camp in campaigns:
                impressions = random.randint(5000, 25000)
                ctr = bench.get("avg_ctr_pct", 2.1) / 100 * random.uniform(0.8, 1.2)
                clicks = int(impressions * ctr)
                cpc_krw = bench.get("avg_cpc_krw", {}).get("뷰티", 350)
                spend_krw = clicks * cpc_krw * random.uniform(0.9, 1.1)
                conversions = int(clicks * 0.035 * random.uniform(0.8, 1.2))
                rows.append({
                    "campaign_id": camp["id"],
                    "campaign_name": camp["name"],
                    "date": date_str,
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend_krw": int(spend_krw),
                    "conversions": conversions,
                    "revenue_krw": int(spend_krw * bench.get("avg_roas", 320) / 100),
                    "ctr": round(ctr, 4),
                    "platform": "google_ads",
                })
        return rows
