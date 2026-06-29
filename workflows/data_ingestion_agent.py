"""
Data Ingestion Agent — Phase 3.

Coordinates all data-source connectors, refreshes data into storage
(SQLite when USE_SQLITE=true, otherwise mock data is kept in memory),
and reports connector health + data freshness.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from models.agent_run import AgentRun
from storage.repository import save_agent_run
from workflows.base import BaseWorkflow

_FRESHNESS_FILE = Path("data/store/data_freshness.json")


def _load_freshness() -> dict:
    if _FRESHNESS_FILE.exists():
        try:
            return json.loads(_FRESHNESS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_freshness(data: dict) -> None:
    _FRESHNESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _FRESHNESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class DataIngestionAgent(BaseWorkflow):
    """
    Orchestrates data refresh from all registered connectors.

    With USE_SQLITE=true: fetched rows are persisted to daily_metrics table.
    Without SQLite: reports freshness and connector status only.
    """

    system_prompt = """당신은 데이터 수집 에이전트입니다.
각 커넥터의 상태를 점검하고, 데이터 신선도를 관리하며,
실제 API 연결 전환 준비 상태를 보고합니다."""

    allowed_tools = []

    CONNECTORS = {
        "gsc": ("connectors.gsc_connector", "GSCConnector"),
        "ga4": ("connectors.ga4_connector", "GA4Connector"),
        "naver_ads": ("connectors.naver_ads", "NaverAdsConnector"),
        "kakao": ("connectors.kakao_moment", "KakaoMomentConnector"),
        "google_ads": ("connectors.google_ads", "GoogleAdsConnector"),
    }

    def _get_connector(self, name: str):
        module_path, class_name = self.CONNECTORS[name]
        module = __import__(module_path, fromlist=[class_name])
        return getattr(module, class_name)()

    def get_connector_status(self) -> dict:
        """Check all connectors — availability and current mode."""
        statuses = {}
        for name in self.CONNECTORS:
            try:
                conn = self._get_connector(name)
                statuses[name] = conn.status()
            except Exception as e:
                statuses[name] = {"connector": name, "error": str(e)}
        return {
            "connectors": statuses,
            "real_count": sum(1 for s in statuses.values() if s.get("mode") == "real"),
            "mock_count": sum(1 for s in statuses.values() if s.get("mode") == "mock"),
            "checked_at": datetime.now().isoformat(),
        }

    def refresh_all(self, days: int = 28) -> dict:
        """
        Fetch data from all connectors and persist ad-platform rows to SQLite.
        GSC and GA4 are stored separately (seo pipeline handles those).
        """
        run = AgentRun(
            workflow_name="data_ingestion",
            trigger="manual",
            input_params={"days": days},
        )
        save_agent_run(run)

        from config.feature_flags import is_enabled
        use_sqlite = is_enabled("USE_SQLITE")

        results = {}
        freshness = _load_freshness()
        ad_connectors = ["naver_ads", "kakao", "google_ads"]

        total_rows = 0
        for name in ad_connectors:
            try:
                conn = self._get_connector(name)
                fetched = conn.get_data(days=days)
                row_count = fetched["row_count"]

                if use_sqlite and fetched["data"]:
                    from storage.db import insert_daily_metrics
                    inserted = insert_daily_metrics(fetched["data"])
                    results[name] = {
                        "status": "ok",
                        "source": fetched["source"],
                        "rows_fetched": row_count,
                        "rows_inserted": inserted,
                    }
                else:
                    results[name] = {
                        "status": "ok",
                        "source": fetched["source"],
                        "rows_fetched": row_count,
                        "rows_inserted": 0 if not use_sqlite else row_count,
                        "note": "SQLite disabled — data not persisted" if not use_sqlite else "",
                    }

                freshness[name] = {
                    "last_refresh": datetime.now().isoformat(),
                    "source": fetched["source"],
                    "row_count": row_count,
                }
                total_rows += row_count
                self._log(f"  [Ingestion] {name}: {row_count} rows ({fetched['source']})")

            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}
                self._log(f"  [Ingestion] {name}: ERROR — {e}")

        # GSC + GA4 status (read-only, SEO pipeline handles storage)
        for name in ["gsc", "ga4"]:
            try:
                conn = self._get_connector(name)
                status = conn.status()
                freshness[name] = {
                    "last_refresh": datetime.now().isoformat(),
                    "mode": status["mode"],
                }
                results[name] = {"status": "ok", "mode": status["mode"], "note": "managed by seo_pipeline"}
            except Exception as e:
                results[name] = {"status": "error", "error": str(e)}

        _save_freshness(freshness)

        run.complete(
            output_summary=f"{total_rows}개 광고 행 수집 | SQLite={'ON' if use_sqlite else 'OFF'}"
        )
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "connectors": results,
            "total_ad_rows": total_rows,
            "sqlite_enabled": use_sqlite,
            "freshness_file": str(_FRESHNESS_FILE),
        }

    def get_freshness_report(self) -> dict:
        """Return data freshness status for all connectors."""
        freshness = _load_freshness()
        now = datetime.now()
        report = {}
        for name, info in freshness.items():
            last = info.get("last_refresh")
            if last:
                age_hours = (now - datetime.fromisoformat(last)).total_seconds() / 3600
                is_stale = age_hours > 25
            else:
                age_hours = None
                is_stale = True
            report[name] = {
                **info,
                "age_hours": round(age_hours, 1) if age_hours is not None else None,
                "is_stale": is_stale,
            }

        never_refreshed = [
            name for name in self.CONNECTORS if name not in freshness
        ]
        return {
            "connectors": report,
            "never_refreshed": never_refreshed,
            "stale_count": sum(1 for r in report.values() if r["is_stale"]),
            "checked_at": now.isoformat(),
        }

    def get_daily_metrics_summary(
        self,
        platform: str = "",
        days: int = 7,
    ) -> dict:
        """
        Query daily_metrics from SQLite (if enabled) or return mock summary.
        """
        from config.feature_flags import is_enabled
        if not is_enabled("USE_SQLITE"):
            return {
                "note": "SQLite disabled — enable with USE_SQLITE=true",
                "mock_summary": self._mock_metrics_summary(days),
            }

        from storage.db import get_daily_metrics
        from datetime import date, timedelta
        since = (date.today() - timedelta(days=days)).isoformat()
        rows = get_daily_metrics(platform=platform or None, since=since)

        if not rows:
            return {"note": "No data in SQLite — run refresh_all() first", "rows": 0}

        total_spend = sum(r.get("spend_krw", 0) for r in rows)
        total_revenue = sum(r.get("revenue_krw", 0) for r in rows)
        total_clicks = sum(r.get("clicks", 0) for r in rows)
        total_impressions = sum(r.get("impressions", 0) for r in rows)
        total_conversions = sum(r.get("conversions", 0) for r in rows)

        platforms = list({r["platform"] for r in rows})
        return {
            "period_days": days,
            "platforms": platforms,
            "total_spend_krw": int(total_spend),
            "total_revenue_krw": int(total_revenue),
            "total_clicks": total_clicks,
            "total_impressions": total_impressions,
            "total_conversions": total_conversions,
            "blended_roas": round(total_revenue / max(total_spend, 1) * 100, 1),
            "blended_ctr": round(total_clicks / max(total_impressions, 1), 4),
            "row_count": len(rows),
        }

    def _mock_metrics_summary(self, days: int) -> dict:
        """Return mock summary using connector mock data."""
        conn = self._get_connector("naver_ads")
        rows = conn.mock_data(days=days)
        spend = sum(r.get("spend_krw", 0) for r in rows)
        revenue = sum(r.get("revenue_krw", 0) for r in rows)
        return {
            "period_days": days,
            "total_spend_krw": int(spend),
            "total_revenue_krw": int(revenue),
            "blended_roas": round(revenue / max(spend, 1) * 100, 1),
            "source": "mock",
        }
