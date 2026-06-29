"""Unit tests for tool handlers (no API calls required)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pytest
from tools.handlers import (
    get_campaign_performance,
    get_keyword_analysis,
    optimize_budget_allocation,
    analyze_competitors,
    generate_ad_copy,
    get_market_events,
    create_campaign_plan,
    generate_performance_report,
    ab_test_analysis,
    dispatch,
)


class TestGetCampaignPerformance:
    def test_single_platform(self):
        result = get_campaign_performance("naver_search", "2024-11-01", "2024-11-30")
        assert "summary" in result
        assert "platform_breakdown" in result
        assert result["summary"]["total_spend_krw"] > 0

    def test_all_platforms(self):
        result = get_campaign_performance("all", "2024-11-01", "2024-11-07")
        assert len(result["platform_breakdown"]) > 1

    def test_date_period(self):
        result = get_campaign_performance("kakao_moment", "2024-01-01", "2024-01-07")
        assert result["period"]["days"] == 7


class TestGetKeywordAnalysis:
    def test_basic(self):
        result = get_keyword_analysis(["스킨케어", "세럼"], category="뷰티")
        assert "analyzed_keywords" in result
        assert len(result["analyzed_keywords"]) == 2

    def test_with_related(self):
        result = get_keyword_analysis(["화장품"], include_related=True)
        assert len(result["related_keywords"]) > 0

    def test_cap_at_20(self):
        keywords = [f"키워드{i}" for i in range(30)]
        result = get_keyword_analysis(keywords)
        assert len(result["analyzed_keywords"]) == 20


class TestOptimizeBudgetAllocation:
    def test_small_budget(self):
        result = optimize_budget_allocation(
            total_budget_krw=500_000,
            category="패션",
            objective="roas_maximize",
            current_month=11,
        )
        assert "recommended_allocation" in result
        assert result["total_budget_krw"] == 500_000

    def test_large_budget(self):
        result = optimize_budget_allocation(
            total_budget_krw=100_000_000,
            category="가전",
            objective="roas_maximize",
            current_month=12,
        )
        allocations = result["recommended_allocation"]
        total_pct = sum(a["budget_pct"] for a in allocations.values())
        assert total_pct == 100

    def test_upcoming_events_included(self):
        result = optimize_budget_allocation(
            total_budget_krw=10_000_000,
            category="뷰티",
            objective="cpa_minimize",
            current_month=1,
        )
        assert "upcoming_events_to_consider" in result


class TestAnalyzeCompetitors:
    def test_basic(self):
        result = analyze_competitors("테스트브랜드", "뷰티")
        assert "market_landscape" in result
        assert "competitive_insights" in result

    def test_with_platforms(self):
        result = analyze_competitors("테스트브랜드", "패션", ["naver_search", "coupang_ads"])
        assert result["category"] == "패션"


class TestGenerateAdCopy:
    def test_naver_search(self):
        result = generate_ad_copy(
            product_name="콜라겐 세럼",
            key_features=["탄력 개선", "보습 강화"],
            target_audience="30대 여성",
            platform="naver_search",
            count=3,
        )
        assert len(result["ad_copies"]) == 3
        for copy in result["ad_copies"]:
            assert len(copy["headline"]) <= 15

    def test_instagram(self):
        result = generate_ad_copy(
            product_name="트렌디 백팩",
            key_features=["방수", "가벼운 무게"],
            target_audience="20대 직장인",
            platform="meta_instagram",
        )
        assert result["platform"] == "meta_instagram"

    def test_with_promotion(self):
        result = generate_ad_copy(
            product_name="테스트 상품",
            key_features=["기능1"],
            target_audience="전 연령",
            platform="coupang_ads",
            promotion="블랙프라이데이 40% 할인",
        )
        assert result["ad_copies"]


class TestGetMarketEvents:
    def test_no_args(self):
        result = get_market_events()
        assert "upcoming_events" in result
        assert "consumer_behavior_insights" in result

    def test_with_month(self):
        result = get_market_events(month=9, lookahead_months=2)
        assert result["current_month"] == 9

    def test_events_have_required_fields(self):
        result = get_market_events(month=11)
        for event in result["upcoming_events"]:
            assert "name" in event
            assert "typical_roas_multiplier" in event
            assert "key_categories" in event


class TestCreateCampaignPlan:
    def test_basic(self):
        result = create_campaign_plan(
            brand_name="테스트브랜드",
            product_category="뷰티",
            campaign_objective="sales_conversion",
            total_budget_krw=30_000_000,
            campaign_period_weeks=4,
            target_audience="30대 여성",
        )
        assert "weekly_execution_plan" in result
        assert len(result["weekly_execution_plan"]) == 4

    def test_weekly_budget_matches(self):
        total = 40_000_000
        weeks = 4
        result = create_campaign_plan(
            brand_name="브랜드A",
            product_category="패션",
            campaign_objective="brand_awareness",
            total_budget_krw=total,
            campaign_period_weeks=weeks,
            target_audience="20-30대",
        )
        weekly_total = sum(w["budget_krw"] for w in result["weekly_execution_plan"])
        assert weekly_total == total


class TestGeneratePerformanceReport:
    def test_weekly(self):
        result = generate_performance_report("weekly", "2024-11-01", "2024-11-07")
        assert "executive_summary" in result
        assert "platform_performance" in result

    def test_with_recommendations(self):
        result = generate_performance_report(
            "monthly", "2024-11-01", "2024-11-30", include_recommendations=True
        )
        assert "recommendations" in result

    def test_without_recommendations(self):
        result = generate_performance_report(
            "weekly", "2024-11-01", "2024-11-07", include_recommendations=False
        )
        assert "recommendations" not in result


class TestAbTestAnalysis:
    def test_roas_winner(self):
        variant_a = {"impressions": 10000, "clicks": 300, "conversions": 15, "spend_krw": 500000, "revenue_krw": 2000000}
        variant_b = {"impressions": 10000, "clicks": 280, "conversions": 18, "spend_krw": 500000, "revenue_krw": 2500000}
        result = ab_test_analysis("테스트1", variant_a, variant_b, "roas")
        assert result["winner"] in ("A", "B")
        assert "is_statistically_significant" in result

    def test_cpa_winner_lower_is_better(self):
        variant_a = {"impressions": 5000, "clicks": 150, "conversions": 10, "spend_krw": 200000}
        variant_b = {"impressions": 5000, "clicks": 160, "conversions": 20, "spend_krw": 200000}
        result = ab_test_analysis("CPA테스트", variant_a, variant_b, "cpa")
        # B has lower CPA (200000/20=10000 vs 200000/10=20000)
        assert result["winner"] == "B"


class TestDispatch:
    def test_valid_tool(self):
        result_str = dispatch("get_market_events", {"month": 11})
        result = json.loads(result_str)
        assert "upcoming_events" in result

    def test_unknown_tool(self):
        result_str = dispatch("nonexistent_tool", {})
        result = json.loads(result_str)
        assert "error" in result

    def test_bad_args(self):
        result_str = dispatch("get_campaign_performance", {"platform": "naver_search"})
        result = json.loads(result_str)
        assert "error" in result
