"""
Kakao Moment (카카오 모먼트) connector.

Real API: requires KAKAO_ADS_ACCESS_TOKEN + KAKAO_ADS_ACCOUNT_ID.
Docs: https://developers.kakao.com/docs/latest/ko/moment/common

Auth: Authorization: Bearer {access_token}
      adAccountId: {account_id}
"""

import os
from datetime import datetime, timedelta
from connectors.base import BaseConnector


class KakaoMomentConnector(BaseConnector):
    connector_id = "KAKAO"
    display_name = "Kakao Moment (카카오모먼트)"
    BASE_URL = "https://apis.kakao.com/adManage/v1"

    def is_available(self) -> bool:
        return bool(
            os.getenv("KAKAO_ADS_ACCESS_TOKEN")
            and os.getenv("KAKAO_ADS_ACCOUNT_ID")
        )

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {os.getenv('KAKAO_ADS_ACCESS_TOKEN', '')}",
            "adAccountId": os.getenv("KAKAO_ADS_ACCOUNT_ID", ""),
            "Content-Type": "application/json",
        }

    def fetch(self, days: int = 28, **kwargs) -> list[dict]:
        """
        Real implementation:

        import httpx
        headers = self._headers()

        # 1) List campaigns
        resp = httpx.get(f"{self.BASE_URL}/campaigns", headers=headers)
        resp.raise_for_status()
        campaigns = resp.json().get("content", [])

        from datetime import date, timedelta
        end = date.today().isoformat().replace("-", "")
        start = (date.today() - timedelta(days=days)).isoformat().replace("-", "")

        rows = []
        for c in campaigns:
            # 2) Fetch report per campaign
            report_resp = httpx.get(
                f"{self.BASE_URL}/campaigns/{c['id']}/stats",
                headers=headers,
                params={"startDate": start, "endDate": end, "timeUnit": "DAY"},
            )
            report_resp.raise_for_status()
            for stat in report_resp.json().get("data", []):
                rows.append({
                    "campaign_id": c["id"],
                    "campaign_name": c.get("name", ""),
                    "date": stat["date"],
                    "impressions": stat.get("impression", 0),
                    "clicks": stat.get("click", 0),
                    "spend_krw": stat.get("cost", 0),
                    "conversions": stat.get("conversion", 0),
                    "revenue_krw": stat.get("revenue", 0),
                    "ctr": stat.get("ctr", 0),
                    "platform": "kakao",
                })
        return rows
        """
        raise NotImplementedError("Set KAKAO_ADS_ACCESS_TOKEN and KAKAO_ADS_ACCOUNT_ID")

    def mock_data(self, days: int = 28, **kwargs) -> list[dict]:
        from data.korean_market import PLATFORM_BENCHMARKS
        import random
        bench = PLATFORM_BENCHMARKS.get("kakao", {})
        rows = []
        base_date = datetime.now()
        campaigns = [
            {"id": "kakao_camp_001", "name": "뷰티랩_브랜드_카카오"},
            {"id": "kakao_camp_002", "name": "세럼_DA_리타겟팅"},
        ]
        for i in range(min(days, 28)):
            date_str = (base_date - timedelta(days=i)).strftime("%Y%m%d")
            for camp in campaigns:
                impressions = random.randint(20000, 80000)
                ctr = bench.get("avg_ctr_pct", 0.8) / 100 * random.uniform(0.7, 1.3)
                clicks = int(impressions * ctr)
                spend_krw = int(impressions * bench.get("avg_cpm_krw", 3500) / 1000)
                conversions = int(clicks * 0.025 * random.uniform(0.8, 1.2))
                rows.append({
                    "campaign_id": camp["id"],
                    "campaign_name": camp["name"],
                    "date": date_str,
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend_krw": spend_krw,
                    "conversions": conversions,
                    "revenue_krw": spend_krw * bench.get("avg_roas", 280) / 100,
                    "ctr": round(ctr, 4),
                    "platform": "kakao",
                })
        return rows
