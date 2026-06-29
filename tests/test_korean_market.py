"""Unit tests for Korean market data module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from data.korean_market import (
    KOREAN_MARKET_EVENTS,
    PLATFORM_BENCHMARKS,
    CATEGORY_KPIS,
    CONSUMER_INSIGHTS,
    get_upcoming_events,
    get_platform_recommendation,
)


class TestKoreanMarketEvents:
    def test_events_populated(self):
        assert len(KOREAN_MARKET_EVENTS) > 0

    def test_event_fields(self):
        for event in KOREAN_MARKET_EVENTS:
            assert event.name
            assert event.name_en
            assert 1 <= event.month <= 12
            assert event.typical_roas_multiplier > 1.0
            assert event.recommended_budget_increase_pct > 0
            assert len(event.key_categories) > 0

    def test_chuseok_in_events(self):
        names = [e.name for e in KOREAN_MARKET_EVENTS]
        assert "추석 연휴" in names

    def test_black_friday_high_roas(self):
        bf = next(e for e in KOREAN_MARKET_EVENTS if "광군제" in e.name)
        assert bf.typical_roas_multiplier >= 2.0

    def test_get_upcoming_events_returns_events(self):
        events = get_upcoming_events(current_month=11, lookahead_months=2)
        assert len(events) > 0

    def test_get_upcoming_events_year_wrap(self):
        # December wrapping into January
        events = get_upcoming_events(current_month=12, lookahead_months=2)
        months = {e.month for e in events}
        assert 12 in months or 1 in months


class TestPlatformBenchmarks:
    def test_all_major_platforms_present(self):
        expected = [
            "naver_search", "naver_shopping", "kakao_display",
            "kakao_moment", "coupang_ads", "meta_instagram", "youtube_ads",
        ]
        for platform in expected:
            assert platform in PLATFORM_BENCHMARKS

    def test_benchmark_has_roas(self):
        for platform, data in PLATFORM_BENCHMARKS.items():
            assert "avg_roas" in data, f"{platform} missing avg_roas"
            assert data["avg_roas"] > 0

    def test_coupang_highest_cvr(self):
        coupang_cvr = PLATFORM_BENCHMARKS["coupang_ads"]["avg_cvr_pct"]
        naver_cvr = PLATFORM_BENCHMARKS["naver_search"]["avg_cvr_pct"]
        # Coupang typically has higher conversion rate than pure search
        assert coupang_cvr >= naver_cvr


class TestCategoryKPIs:
    def test_all_categories_have_kpis(self):
        required = ["패션", "뷰티", "식품", "가전", "건강", "여행", "교육", "금융"]
        for cat in required:
            assert cat in CATEGORY_KPIS

    def test_kpi_fields(self):
        for cat, kpis in CATEGORY_KPIS.items():
            assert "target_roas" in kpis
            assert "target_cpa_krw" in kpis
            assert "avg_order_value_krw" in kpis
            assert kpis["target_roas"] > 0
            assert kpis["target_cpa_krw"] > 0

    def test_electronics_higher_cpa(self):
        # Electronics typically has higher CPA than fashion
        assert CATEGORY_KPIS["가전"]["target_cpa_krw"] > CATEGORY_KPIS["패션"]["target_cpa_krw"]


class TestGetPlatformRecommendation:
    def test_small_budget_naver_focused(self):
        rec = get_platform_recommendation("패션", 500_000)
        assert rec["primary"] == "naver_search"
        total_pct = sum(rec["allocation"].values())
        assert total_pct == 100

    def test_large_budget_multichannel(self):
        rec = get_platform_recommendation("뷰티", 50_000_000)
        assert len(rec["allocation"]) >= 4

    def test_allocation_sums_to_100(self):
        for budget in [500_000, 5_000_000, 50_000_000]:
            rec = get_platform_recommendation("식품", budget)
            total = sum(rec["allocation"].values())
            assert total == 100, f"Budget {budget}: allocation sums to {total}, not 100"


class TestConsumerInsights:
    def test_mobile_usage_mentioned(self):
        assert "mobile_usage" in CONSUMER_INSIGHTS

    def test_naver_dominance_mentioned(self):
        assert "naver_dominance" in CONSUMER_INSIGHTS

    def test_peak_hours_mentioned(self):
        assert "peak_hours" in CONSUMER_INSIGHTS
