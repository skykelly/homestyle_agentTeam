"""
Naver Ads (검색광고) connector.

Real API: requires NAVER_ADS_API_KEY, NAVER_ADS_SECRET_KEY, NAVER_ADS_CUSTOMER_ID.
Docs: https://naver.github.io/naver-ads-api/

Auth header:
  X-API-KEY: {api_key}
  X-SECRET-KEY: {secret_key (base64 HMAC-SHA256)}
  X-CUSTOMER: {customer_id}
"""

import hashlib
import hmac
import base64
import os
import time
from datetime import datetime, timedelta
from connectors.base import BaseConnector


class NaverAdsConnector(BaseConnector):
    connector_id = "NAVER_ADS"
    display_name = "Naver Ads (검색광고)"
    BASE_URL = "https://api.naver.com"

    def is_available(self) -> bool:
        return bool(
            os.getenv("NAVER_ADS_API_KEY")
            and os.getenv("NAVER_ADS_SECRET_KEY")
            and os.getenv("NAVER_ADS_CUSTOMER_ID")
        )

    def _auth_headers(self, method: str, path: str) -> dict:
        """Generate HMAC-SHA256 signed headers for Naver Ads API."""
        api_key = os.getenv("NAVER_ADS_API_KEY", "")
        secret_key = os.getenv("NAVER_ADS_SECRET_KEY", "")
        customer_id = os.getenv("NAVER_ADS_CUSTOMER_ID", "")
        timestamp = str(int(time.time() * 1000))

        message = f"{timestamp}.{method}.{path}"
        signature = base64.b64encode(
            hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()

        return {
            "X-API-KEY": api_key,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "X-CUSTOMER": customer_id,
            "Content-Type": "application/json; charset=UTF-8",
        }

    def fetch(self, days: int = 28, **kwargs) -> list[dict]:
        """
        Real implementation — uses httpx (already in requirements).

        import httpx
        headers = self._auth_headers("GET", "/ncc/campaigns")
        resp = httpx.get(f"{self.BASE_URL}/ncc/campaigns", headers=headers)
        resp.raise_for_status()
        campaigns = resp.json()

        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        rows = []
        for c in campaigns:
            stat_headers = self._auth_headers("GET", "/stats/campaign")
            stat_resp = httpx.get(
                f"{self.BASE_URL}/stats/campaign",
                headers=stat_headers,
                params={
                    "ids": c["nccCampaignId"],
                    "fields": "clkCnt,impCnt,salesAmt,crCnt,avgRnk",
                    "timeRange": {"since": start, "until": end},
                    "timeUnit": "DAY",
                }
            )
            stat_resp.raise_for_status()
            for stat in stat_resp.json().get("data", []):
                rows.append({
                    "campaign_id": c["nccCampaignId"],
                    "campaign_name": c.get("name", ""),
                    "date": stat["dt"],
                    "impressions": stat["impCnt"],
                    "clicks": stat["clkCnt"],
                    "spend_krw": stat["salesAmt"],
                    "conversions": stat["crCnt"],
                    "avg_position": stat["avgRnk"],
                    "ctr": stat["clkCnt"] / max(stat["impCnt"], 1),
                    "platform": "naver_search",
                })
        return rows
        """
        raise NotImplementedError("Set NAVER_ADS_API_KEY/SECRET_KEY/CUSTOMER_ID to use real API")

    def mock_data(self, days: int = 28, **kwargs) -> list[dict]:
        from data.korean_market import PLATFORM_BENCHMARKS
        import random
        bench = PLATFORM_BENCHMARKS.get("naver_search", {})
        rows = []
        base_date = datetime.now()
        campaigns = [
            {"id": "naver_camp_001", "name": "콜라겐세럼_브랜드검색"},
            {"id": "naver_camp_002", "name": "히알루론산_일반검색"},
            {"id": "naver_camp_003", "name": "레티놀_경쟁키워드"},
        ]
        for i in range(min(days, 28)):
            date_str = (base_date - timedelta(days=i)).strftime("%Y-%m-%d")
            for camp in campaigns:
                impressions = random.randint(3000, 15000)
                ctr = bench.get("avg_ctr_pct", 3.5) / 100 * random.uniform(0.8, 1.2)
                clicks = int(impressions * ctr)
                spend_krw = clicks * random.randint(400, 900)
                conversions = int(clicks * 0.04 * random.uniform(0.8, 1.2))
                rows.append({
                    "campaign_id": camp["id"],
                    "campaign_name": camp["name"],
                    "date": date_str,
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend_krw": spend_krw,
                    "conversions": conversions,
                    "revenue_krw": spend_krw * bench.get("avg_roas", 450) / 100,
                    "avg_position": round(random.uniform(1.2, 4.5), 1),
                    "ctr": round(ctr, 4),
                    "platform": "naver_search",
                })
        return rows
