"""
Tool handler implementations for the Korea Performance Marketing Agent.
In production these would call real APIs; here they return realistic simulated data.
"""

import json
import math
import random
from datetime import datetime, date, timedelta

from data.korean_market import (
    PLATFORM_BENCHMARKS,
    CATEGORY_KPIS,
    CONSUMER_INSIGHTS,
    get_upcoming_events,
    get_platform_recommendation,
)


def _days_between(start: str, end: str) -> int:
    fmt = "%Y-%m-%d"
    return max(1, (datetime.strptime(end, fmt) - datetime.strptime(start, fmt)).days + 1)


def _platform_metrics(platform: str, days: int, category: str = "패션") -> dict:
    """Generate realistic-looking platform metrics."""
    bench = PLATFORM_BENCHMARKS.get(platform, {})
    roas = bench.get("avg_roas", 300) * random.uniform(0.85, 1.15)
    ctr = bench.get("avg_ctr_pct", 1.5) * random.uniform(0.9, 1.1)
    cvr = bench.get("avg_cvr_pct", 2.0) * random.uniform(0.85, 1.15)

    daily_spend = random.randint(50_000, 500_000)
    spend = daily_spend * days
    impressions = int(spend / bench.get("avg_cpm_krw", 5000) * 1000) if "avg_cpm_krw" in bench else int(spend / bench.get("avg_cpc_krw", {}).get(category, 300) * ctr / 100)
    clicks = int(impressions * ctr / 100)
    conversions = int(clicks * cvr / 100)
    revenue = int(spend * roas / 100)
    cpa = int(spend / conversions) if conversions else 0

    return {
        "platform": platform,
        "platform_name": bench.get("name", platform),
        "spend_krw": spend,
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": round(ctr, 2),
        "conversions": conversions,
        "cvr_pct": round(cvr, 2),
        "revenue_krw": revenue,
        "roas": round(roas, 1),
        "cpa_krw": cpa,
        "cpc_krw": int(spend / clicks) if clicks else 0,
    }


# ---------------------------------------------------------------------------
# Tool handler functions
# ---------------------------------------------------------------------------

def get_campaign_performance(
    platform: str,
    start_date: str,
    end_date: str,
    campaign_id: str | None = None,
) -> dict:
    days = _days_between(start_date, end_date)
    platforms = (
        list(PLATFORM_BENCHMARKS.keys())
        if platform == "all"
        else [platform]
    )

    results = [_platform_metrics(p, days) for p in platforms]

    total_spend = sum(r["spend_krw"] for r in results)
    total_revenue = sum(r["revenue_krw"] for r in results)
    total_conversions = sum(r["conversions"] for r in results)
    blended_roas = round(total_revenue / total_spend * 100, 1) if total_spend else 0

    return {
        "period": {"start": start_date, "end": end_date, "days": days},
        "campaign_id": campaign_id or "all",
        "summary": {
            "total_spend_krw": total_spend,
            "total_revenue_krw": total_revenue,
            "total_conversions": total_conversions,
            "blended_roas": blended_roas,
            "avg_cpa_krw": int(total_spend / total_conversions) if total_conversions else 0,
        },
        "platform_breakdown": results,
    }


def get_keyword_analysis(
    keywords: list[str],
    category: str = "패션",
    include_related: bool = True,
) -> dict:
    results = []
    for kw in keywords[:20]:  # cap at 20
        monthly_search = random.randint(1_000, 500_000)
        competition = random.choice(["낮음", "보통", "높음", "매우 높음"])
        cpc = random.randint(100, 2000)
        results.append({
            "keyword": kw,
            "monthly_search_volume": monthly_search,
            "competition": competition,
            "estimated_cpc_krw": cpc,
            "trend": random.choice(["상승", "유지", "하락"]),
            "mobile_ratio_pct": random.randint(60, 85),
        })

    related = []
    if include_related:
        suffixes = [" 추천", " 후기", " 가격", " 할인", " 최저가"]
        for kw in keywords[:3]:
            for s in suffixes[:2]:
                related.append({
                    "keyword": kw + s,
                    "monthly_search_volume": random.randint(500, 50_000),
                    "estimated_cpc_krw": random.randint(80, 800),
                })

    return {
        "category": category,
        "analyzed_keywords": results,
        "related_keywords": related,
        "insights": [
            f"'{keywords[0]}' 키워드는 모바일 비중이 높아 모바일 입찰가 가중치 설정 권장",
            "시즌 이벤트(설날/추석) 전후 2주간 검색량 급증 패턴 확인됨",
            "브랜드 키워드 평균 CPC가 일반 키워드 대비 40% 낮음",
        ],
    }


def optimize_budget_allocation(
    total_budget_krw: int,
    category: str,
    objective: str,
    current_month: int,
    active_platforms: list[str] | None = None,
) -> dict:
    rec = get_platform_recommendation(category, total_budget_krw)
    upcoming = get_upcoming_events(current_month, lookahead_months=2)
    kpis = CATEGORY_KPIS.get(category, CATEGORY_KPIS["패션"])

    allocation_detail = {}
    for platform, pct in rec["allocation"].items():
        budget = int(total_budget_krw * pct / 100)
        bench = PLATFORM_BENCHMARKS.get(platform, {})
        est_roas = bench.get("avg_roas", 300)
        allocation_detail[platform] = {
            "platform_name": bench.get("name", platform),
            "budget_krw": budget,
            "budget_pct": pct,
            "estimated_roas": est_roas,
            "estimated_revenue_krw": int(budget * est_roas / 100),
        }

    event_boosts = []
    for event in upcoming[:3]:
        event_boosts.append({
            "event": event.name,
            "event_en": event.name_en,
            "month": event.month,
            "recommended_budget_increase_pct": event.recommended_budget_increase_pct,
            "key_categories": event.key_categories,
            "roas_multiplier": event.typical_roas_multiplier,
        })

    total_est_revenue = sum(a["estimated_revenue_krw"] for a in allocation_detail.values())

    return {
        "total_budget_krw": total_budget_krw,
        "category": category,
        "objective": objective,
        "target_roas": kpis["target_roas"],
        "target_cpa_krw": kpis["target_cpa_krw"],
        "recommended_allocation": allocation_detail,
        "estimated_blended_roas": round(total_est_revenue / total_budget_krw * 100, 1),
        "estimated_total_revenue_krw": total_est_revenue,
        "upcoming_events_to_consider": event_boosts,
        "optimization_tips": [
            "주요 이벤트 2주 전부터 예산을 점진적으로 증가시키세요",
            "모바일 입찰가 가중치를 1.2-1.4배로 설정하세요 (모바일 비중 78%)",
            "ROAS 목표 미달 캠페인은 7일 후 입찰 전략 조정을 권장합니다",
            f"{category} 카테고리 평균 CPA는 {kpis['target_cpa_krw']:,}원입니다",
        ],
    }


def analyze_competitors(
    brand_name: str,
    category: str,
    platforms: list[str] | None = None,
) -> dict:
    if not platforms:
        platforms = ["naver_search", "naver_shopping", "kakao_moment"]

    competitors = []
    for i in range(3):
        share = random.randint(8, 35)
        competitors.append({
            "brand": f"경쟁사 {chr(65+i)} (익명처리)",
            "estimated_monthly_spend_krw": random.randint(5_000_000, 80_000_000),
            "market_share_pct": share,
            "top_keywords": [f"{category} {kw}" for kw in ["브랜드", "추천", "가격비교"]],
            "primary_platform": random.choice(platforms),
            "creative_style": random.choice(["할인 강조형", "브랜드 감성형", "리뷰/UGC 활용형"]),
        })

    return {
        "target_brand": brand_name,
        "category": category,
        "analysis_platforms": platforms,
        "market_landscape": {
            "total_estimated_ad_spend_krw": random.randint(200_000_000, 800_000_000),
            "top_3_competitors": competitors,
        },
        "competitive_insights": [
            f"{brand_name}의 네이버 검색 노출 순위는 카테고리 상위 20% 수준",
            "경쟁사 대비 모바일 광고 비중이 낮아 개선 기회 존재",
            "리뷰 기반 광고 소재 활용 시 CTR 25-30% 향상 예상",
            f"{category} 카테고리에서 쿠팡광고 점유율이 전년 대비 15% 성장",
        ],
        "recommended_actions": [
            "경쟁사 상위 키워드에 브랜드 방어 입찰 설정",
            "경쟁사 대비 차별화된 USP를 광고 소재에 명시",
            "리타겟팅 광고로 경쟁사 검색 사용자 재유입 유도",
        ],
    }


def generate_ad_copy(
    product_name: str,
    key_features: list[str],
    target_audience: str,
    platform: str,
    promotion: str | None = None,
    tone: str = "casual",
    count: int = 3,
) -> dict:
    platform_specs = {
        "naver_search": {"headline_chars": 15, "desc_chars": 45, "has_url": True},
        "naver_shopping": {"headline_chars": 30, "desc_chars": 0, "has_url": False},
        "kakao_moment": {"headline_chars": 25, "desc_chars": 50, "has_url": True},
        "meta_instagram": {"headline_chars": 40, "desc_chars": 125, "has_url": True},
        "youtube_ads": {"headline_chars": 30, "desc_chars": 90, "has_url": True},
        "coupang_ads": {"headline_chars": 25, "desc_chars": 0, "has_url": False},
    }

    spec = platform_specs.get(platform, platform_specs["naver_search"])
    promo_text = f" | {promotion}" if promotion else ""
    feature1 = key_features[0] if key_features else "최고 품질"
    feature2 = key_features[1] if len(key_features) > 1 else "특가 한정"

    copies = []
    templates = [
        {
            "headline": f"{product_name}{promo_text}",
            "description": f"{target_audience}을 위한 {feature1}. 지금 바로 확인하세요!",
            "cta": "지금 구매하기",
            "strategy": "직접 소구형",
        },
        {
            "headline": f"[한정특가] {product_name}",
            "description": f"{feature1}·{feature2} | {target_audience} 만족도 1위",
            "cta": "특가 확인하기",
            "strategy": "희소성 강조형",
        },
        {
            "headline": f"{feature1} {product_name}",
            "description": f"후기 ★4.8 | {target_audience} 검증 완료{promo_text}",
            "cta": "리뷰 보고 구매",
            "strategy": "사회적 증거형",
        },
    ]

    for i, tmpl in enumerate(templates[:count]):
        hl = tmpl["headline"][: spec["headline_chars"]]
        desc = tmpl["description"][: spec["desc_chars"]] if spec["desc_chars"] else ""
        copies.append({
            "variant": chr(65 + i),
            "headline": hl,
            "description": desc,
            "cta": tmpl["cta"],
            "strategy": tmpl["strategy"],
            "char_count": {
                "headline": len(hl),
                "description": len(desc),
            },
        })

    return {
        "product_name": product_name,
        "platform": platform,
        "platform_spec": spec,
        "tone": tone,
        "ad_copies": copies,
        "korean_copywriting_tips": [
            "숫자와 퍼센트를 적극 활용하세요 ('30% 할인', '5만 개 판매')",
            "네이버/카카오 사용자는 '후기', '리뷰', '랭킹' 키워드에 높은 반응",
            "한국어 감탄사('역대급', '완판임박', '강추')는 CTR을 높입니다",
            "가격 비교 심리를 활용한 '최저가 보장' 문구가 효과적",
        ],
    }


def get_market_events(
    month: int | None = None,
    lookahead_months: int = 2,
) -> dict:
    current_month = month or datetime.now().month
    events = get_upcoming_events(current_month, lookahead_months)

    return {
        "current_month": current_month,
        "lookahead_months": lookahead_months,
        "upcoming_events": [
            {
                "name": e.name,
                "name_en": e.name_en,
                "month": e.month,
                "typical_roas_multiplier": e.typical_roas_multiplier,
                "recommended_budget_increase_pct": e.recommended_budget_increase_pct,
                "key_categories": e.key_categories,
                "notes": e.notes,
            }
            for e in events
        ],
        "consumer_behavior_insights": CONSUMER_INSIGHTS,
    }


def create_campaign_plan(
    brand_name: str,
    product_category: str,
    campaign_objective: str,
    total_budget_krw: int,
    campaign_period_weeks: int,
    target_audience: str,
    key_messages: list[str] | None = None,
) -> dict:
    rec = get_platform_recommendation(product_category, total_budget_krw)
    kpis = CATEGORY_KPIS.get(product_category, CATEGORY_KPIS["패션"])
    weekly_budget = total_budget_krw // campaign_period_weeks

    weekly_plan = []
    for w in range(1, campaign_period_weeks + 1):
        if w <= 1:
            phase, focus = "런칭", "인지도 확보, 브랜드 검색량 증대"
        elif w <= campaign_period_weeks - 1:
            phase, focus = "성장", "전환 최적화, ROAS 개선"
        else:
            phase, focus = "마무리", "리타겟팅, 잔여 예산 효율 집행"

        weekly_plan.append({
            "week": w,
            "phase": phase,
            "budget_krw": weekly_budget,
            "focus": focus,
            "key_actions": [
                f"{'A/B 테스트 소재 2종 런칭' if w == 1 else '성과 하위 20% 소재 OFF'}",
                f"{'입찰가 학습기간 설정' if w == 1 else 'ROAS 기준 예산 재배분'}",
            ],
        })

    objective_kpis = {
        "brand_awareness": {"primary_kpi": "CPM", "target": "5,000원 이하"},
        "sales_conversion": {"primary_kpi": "ROAS", "target": f"{kpis['target_roas']}% 이상"},
        "app_install": {"primary_kpi": "CPI", "target": "3,000-8,000원"},
        "lead_generation": {"primary_kpi": "CPL", "target": "10,000-30,000원"},
    }

    return {
        "brand_name": brand_name,
        "product_category": product_category,
        "campaign_objective": campaign_objective,
        "total_budget_krw": total_budget_krw,
        "campaign_period_weeks": campaign_period_weeks,
        "target_audience": target_audience,
        "kpi_targets": objective_kpis.get(campaign_objective, {}),
        "secondary_kpis": {
            "target_roas": kpis["target_roas"],
            "target_cpa_krw": kpis["target_cpa_krw"],
            "avg_order_value_krw": kpis["avg_order_value_krw"],
        },
        "platform_strategy": rec,
        "weekly_execution_plan": weekly_plan,
        "creative_direction": {
            "key_messages": key_messages or ["품질 강조", "가격 경쟁력", "빠른 배송"],
            "recommended_formats": ["이미지 배너", "동영상 6초/15초", "카탈로그 광고"],
            "korean_specific": [
                "네이버 브랜드검색 + 파워콘텐츠 병행",
                "카카오톡 선물하기 연동 광고 검토",
                "쿠팡 브랜드 스토어 + 검색광고 연계",
            ],
        },
        "risk_factors": [
            "경쟁사 입찰가 경쟁으로 CPC 상승 가능",
            "한국 개인정보보호법(PIPA) 준수 쿠키 전략 필요",
            "쿠팡·네이버 알고리즘 업데이트 모니터링 필요",
        ],
    }


def generate_performance_report(
    report_period: str,
    start_date: str,
    end_date: str,
    include_recommendations: bool = True,
    platforms: list[str] | None = None,
) -> dict:
    if not platforms:
        platforms = ["naver_search", "naver_shopping", "kakao_moment", "coupang_ads"]

    days = _days_between(start_date, end_date)
    perf_data = [_platform_metrics(p, days) for p in platforms]

    total_spend = sum(p["spend_krw"] for p in perf_data)
    total_revenue = sum(p["revenue_krw"] for p in perf_data)
    total_conversions = sum(p["conversions"] for p in perf_data)
    blended_roas = round(total_revenue / total_spend * 100, 1) if total_spend else 0

    # Simulated vs. prior period
    prev_roas = blended_roas * random.uniform(0.88, 1.12)
    roas_change = round((blended_roas - prev_roas) / prev_roas * 100, 1)

    best_platform = max(perf_data, key=lambda x: x["roas"])
    worst_platform = min(perf_data, key=lambda x: x["roas"])

    report = {
        "report_period": report_period,
        "period": {"start": start_date, "end": end_date, "days": days},
        "executive_summary": {
            "total_spend_krw": total_spend,
            "total_revenue_krw": total_revenue,
            "total_conversions": total_conversions,
            "blended_roas": blended_roas,
            "avg_cpa_krw": int(total_spend / total_conversions) if total_conversions else 0,
            "roas_vs_prior_period_pct": roas_change,
        },
        "platform_performance": perf_data,
        "highlights": {
            "best_performing_platform": best_platform["platform_name"],
            "best_roas": best_platform["roas"],
            "worst_performing_platform": worst_platform["platform_name"],
            "worst_roas": worst_platform["roas"],
        },
    }

    if include_recommendations:
        report["recommendations"] = [
            f"{best_platform['platform_name']} 예산을 15-20% 증액하여 성과 극대화",
            f"{worst_platform['platform_name']} 입찰 전략을 타겟 CPA 기반으로 전환 검토",
            "전환율 상위 20% 키워드에 입찰가 가중치 1.3배 적용",
            "리타겟팅 오디언스 기간을 30일 → 14일로 단축하여 구매 의도 집중",
            "모바일 입찰가 조정: 현재 설정 대비 10-15% 상향 권장",
        ]

    return report


def ab_test_analysis(
    test_name: str,
    variant_a: dict,
    variant_b: dict,
    primary_metric: str,
    confidence_level: float = 0.95,
) -> dict:
    def calc_metrics(v: dict) -> dict:
        imp = v.get("impressions", 0)
        clicks = v.get("clicks", 0)
        conv = v.get("conversions", 0)
        spend = v.get("spend_krw", 0)
        return {
            "ctr": round(clicks / imp * 100, 2) if imp else 0,
            "cvr": round(conv / clicks * 100, 2) if clicks else 0,
            "cpa": int(spend / conv) if conv else 0,
            "roas": round(v.get("revenue_krw", spend * 3) / spend * 100, 1) if spend else 0,
        }

    metrics_a = calc_metrics(variant_a)
    metrics_b = calc_metrics(variant_b)

    metric_a_val = metrics_a[primary_metric]
    metric_b_val = metrics_b[primary_metric]

    if primary_metric in ("cpa",):
        # Lower is better
        winner = "A" if metric_a_val < metric_b_val else "B"
        improvement = round(abs(metric_b_val - metric_a_val) / metric_a_val * 100, 1)
    else:
        winner = "A" if metric_a_val > metric_b_val else "B"
        improvement = round(abs(metric_b_val - metric_a_val) / metric_a_val * 100, 1)

    # Simplified significance check (in production: chi-squared / z-test)
    total_a = variant_a.get("impressions", 0) + variant_a.get("clicks", 0)
    total_b = variant_b.get("impressions", 0) + variant_b.get("clicks", 0)
    is_significant = total_a > 1000 and total_b > 1000 and improvement > 5

    return {
        "test_name": test_name,
        "primary_metric": primary_metric,
        "confidence_level": confidence_level,
        "variant_a_metrics": metrics_a,
        "variant_b_metrics": metrics_b,
        "winner": winner,
        "improvement_pct": improvement,
        "is_statistically_significant": is_significant,
        "recommendation": (
            f"변형 {winner}를 채택하세요. {primary_metric.upper()} 기준 {improvement}% 개선."
            if is_significant
            else "데이터가 충분하지 않습니다. 최소 7일 더 테스트를 진행하세요."
        ),
        "next_steps": [
            f"변형 {winner} 전체 예산 100% 적용" if is_significant else "테스트 기간 연장",
            "2차 테스트: 랜딩페이지 CTA 문구 최적화 진행",
            "승리 소재의 변형(색상, 이미지) 추가 테스트 권장",
        ],
    }


# Dispatch table: tool name -> handler function
TOOL_HANDLERS = {
    "get_campaign_performance": get_campaign_performance,
    "get_keyword_analysis": get_keyword_analysis,
    "optimize_budget_allocation": optimize_budget_allocation,
    "analyze_competitors": analyze_competitors,
    "generate_ad_copy": generate_ad_copy,
    "get_market_events": get_market_events,
    "create_campaign_plan": create_campaign_plan,
    "generate_performance_report": generate_performance_report,
    "ab_test_analysis": ab_test_analysis,
}


def dispatch(tool_name: str, tool_input: dict) -> str:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {tool_name}"}, ensure_ascii=False)
    try:
        result = handler(**tool_input)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
