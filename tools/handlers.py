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
from storage.repository import list_recommendations


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


# ---------------------------------------------------------------------------
# Phase 2: Recommendation & Approval tool handlers
# ---------------------------------------------------------------------------

def run_diagnosis(
    platform: str,
    campaign: str,
    category: str,
    metrics: dict,
    auto_submit: bool = True,
) -> dict:
    from workflows.diagnosis import DiagnosisWorkflow
    wf = DiagnosisWorkflow(verbose=False)
    return wf.diagnose(
        platform=platform,
        campaign=campaign,
        category=category,
        metrics=metrics,
        auto_submit=auto_submit,
        llm_augment=False,   # Tools called from within LLM — skip nested LLM call
    )


def list_recommendations_handler(
    status: str | None = None,
    platform: str | None = None,
    limit: int = 20,
) -> dict:
    recs = list_recommendations(status=status, platform=platform, limit=limit)
    return {
        "total": len(recs),
        "filter": {"status": status, "platform": platform},
        "recommendations": recs,
    }


def approve_recommendation(
    recommendation_id: str,
    approver: str,
    notes: str = "",
) -> dict:
    from workflows.approval import ApprovalWorkflow
    wf = ApprovalWorkflow()
    return wf.approve(recommendation_id, approver, notes)


def reject_recommendation(
    recommendation_id: str,
    approver: str,
    reason: str,
) -> dict:
    from workflows.approval import ApprovalWorkflow
    wf = ApprovalWorkflow()
    return wf.reject(recommendation_id, approver, reason)


def get_approval_summary() -> dict:
    from workflows.approval import ApprovalWorkflow
    wf = ApprovalWorkflow()
    return wf.get_approval_summary()


# ---------------------------------------------------------------------------
# Phase 3: SEO tool handlers
# ---------------------------------------------------------------------------

def get_seo_overview(site_url: str = "https://beautylab.co.kr") -> dict:
    from data.seo_mock_data import SITE_BENCHMARKS
    b = SITE_BENCHMARKS
    p = b["period_28d"]
    prev = b["period_prev_28d"]

    def delta_pct(cur, old):
        return round((cur - old) / old * 100, 1) if old else 0

    return {
        "site": b["site_name"],
        "site_url": b["site_url"],
        "category": b["category"],
        "period": "최근 28일",
        "metrics": {
            "total_clicks": p["total_clicks"],
            "total_clicks_delta_pct": delta_pct(p["total_clicks"], prev["total_clicks"]),
            "total_impressions": p["total_impressions"],
            "total_impressions_delta_pct": delta_pct(p["total_impressions"], prev["total_impressions"]),
            "avg_ctr": p["avg_ctr"],
            "avg_ctr_delta_pct": delta_pct(p["avg_ctr"], prev["avg_ctr"]),
            "avg_position": p["avg_position"],
            "avg_position_delta": round(p["avg_position"] - prev["avg_position"], 1),
            "organic_revenue_krw": p["organic_revenue_krw"],
            "organic_revenue_delta_pct": delta_pct(p["organic_revenue_krw"], prev["organic_revenue_krw"]),
        },
        "health_signals": {
            "click_trend": "하락" if p["total_clicks"] < prev["total_clicks"] else "상승",
            "position_trend": "하락" if p["avg_position"] > prev["avg_position"] else "상승",
            "ctr_trend": "하락" if p["avg_ctr"] < prev["avg_ctr"] else "상승",
        },
    }


def run_seo_diagnosis(
    site_url: str = "https://beautylab.co.kr",
    min_impressions: int = 3000,
    llm_augment: bool = False,  # Default False when called from within LLM
) -> dict:
    from workflows.seo_diagnosis import SEODiagnosisWorkflow
    wf = SEODiagnosisWorkflow(verbose=False)
    return wf.diagnose(
        site_url=site_url,
        min_impressions=min_impressions,
        llm_augment=llm_augment,
        max_results=15,
    )


def get_seo_query_opportunities(
    opportunity_type: str = "all",
    min_impressions: int = 3000,
    limit: int = 10,
) -> dict:
    from rules.seo_rules import run_all_seo_rules
    all_hits = run_all_seo_rules(min_impressions=min_impressions)

    if opportunity_type != "all":
        hits = [h for h in all_hits if h.opportunity_type == opportunity_type]
    else:
        hits = all_hits

    hits = hits[:limit]

    return {
        "opportunity_type": opportunity_type,
        "total_found": len(all_hits) if opportunity_type == "all" else len([h for h in all_hits if h.opportunity_type == opportunity_type]),
        "returned": len(hits),
        "opportunities": [
            {
                "rule_id": h.rule_id,
                "priority": h.priority,
                "opportunity_type": h.opportunity_type,
                "target_url": h.target_url,
                "target_queries": h.target_queries,
                "description": h.description,
                "expected_impact": h.expected_impact,
                "effort_score": h.effort_score,
                "impact_score": h.impact_score,
                "confidence_score": h.confidence_score,
            }
            for h in hits
        ],
    }


def get_technical_audit(page_type: str = "all") -> dict:
    from data.seo_mock_data import get_crawled_pages
    from rules.seo_rules import check_technical_blocker

    pages = get_crawled_pages() if page_type == "all" else get_crawled_pages(page_type)
    all_issues = []
    page_summaries = []

    for page in pages:
        issues = check_technical_blocker(page)
        triggered = [i for i in issues if i.triggered]
        page_summaries.append({
            "url": page.url,
            "status_code": page.status_code,
            "page_type": page.page_type,
            "is_indexable": page.is_indexable,
            "in_sitemap": page.in_sitemap,
            "has_h1": bool(page.h1.strip()),
            "has_meta_description": bool(page.meta_description.strip()),
            "has_structured_data": page.has_structured_data,
            "redirect_chain_length": page.redirect_chain_length,
            "internal_link_count": page.internal_link_count,
            "last_updated_days": page.last_updated_days,
            "issue_count": len(triggered),
        })
        all_issues.extend(triggered)

    return {
        "page_type_filter": page_type,
        "pages_audited": len(pages),
        "total_issues": len(all_issues),
        "page_summaries": page_summaries,
        "issues": [
            {
                "rule_id": i.rule_id,
                "priority": i.priority,
                "target_url": i.target_url,
                "description": i.description,
                "problem": i.problem,
                "recommendation": i.recommendation,
                "expected_impact": i.expected_impact,
            }
            for i in all_issues
        ],
    }


def get_pagespeed_summary(strategy: str = "mobile", url: str = "") -> dict:
    from data.seo_mock_data import get_pagespeed, PAGESPEED_DATA

    if strategy == "both":
        rows = PAGESPEED_DATA
    else:
        rows = get_pagespeed(url=url, strategy=strategy)

    def classify_lcp(lcp_ms):
        if lcp_ms <= 2500:
            return "Good"
        if lcp_ms <= 4000:
            return "Needs Improvement"
        return "Poor"

    def classify_cls(cls):
        if cls <= 0.1:
            return "Good"
        if cls <= 0.25:
            return "Needs Improvement"
        return "Poor"

    def classify_score(score):
        if score >= 0.9:
            return "Good"
        if score >= 0.5:
            return "Needs Improvement"
        return "Poor"

    results = []
    for r in rows:
        results.append({
            "url": r.url,
            "strategy": r.strategy,
            "performance_score": r.performance_score,
            "performance_rating": classify_score(r.performance_score),
            "lcp_ms": r.lcp_ms,
            "lcp_rating": classify_lcp(r.lcp_ms),
            "cls": r.cls,
            "cls_rating": classify_cls(r.cls),
            "inp_ms": r.inp_ms,
            "seo_score": r.seo_score,
            "accessibility_score": r.accessibility_score,
        })

    poor_count = sum(1 for r in results if r["performance_rating"] == "Poor")
    return {
        "strategy": strategy,
        "url_filter": url or "all",
        "pages_analyzed": len(results),
        "pages_with_poor_performance": poor_count,
        "results": results,
        "summary": {
            "avg_performance_score": round(sum(r["performance_score"] for r in results) / len(results), 2) if results else 0,
            "avg_lcp_ms": round(sum(r["lcp_ms"] for r in results) / len(results)) if results else 0,
            "avg_cls": round(sum(r["cls"] for r in results) / len(results), 3) if results else 0,
        },
    }


def generate_content_brief(
    url: str,
    target_query: str,
    current_position: float = 0,
) -> dict:
    from data.seo_mock_data import get_gsc_queries, get_ga4_landing
    from rules.seo_rules import check_low_ctr, check_geo_candidate

    # Find existing data for this URL
    gsc_rows = [r for r in get_gsc_queries() if r.url == url]
    ga4_rows = get_ga4_landing(url)

    # Find matching query row
    matching_row = next((r for r in gsc_rows if r.query == target_query), None)

    position = current_position or (matching_row.position if matching_row else 0)
    impressions = matching_row.impressions if matching_row else 0
    current_ctr = matching_row.ctr if matching_row else 0

    # Determine search intent
    question_markers = ["어떻게", "무엇", "언제", "왜", "얼마나", "차이", "되나요", "해야 해"]
    is_question = any(m in target_query for m in question_markers)
    search_intent = "informational" if is_question else "commercial" if "추천" in target_query or "최고" in target_query else "mixed"

    # GA4 data
    ga4 = ga4_rows[0] if ga4_rows else None

    return {
        "brief_id": f"BRIEF_{url.replace('/', '_').strip('_').upper()[:20]}_{datetime.now().strftime('%Y%m%d')}",
        "target_url": url,
        "primary_query": target_query,
        "search_intent": search_intent,
        "current_metrics": {
            "position": position,
            "impressions": impressions,
            "current_ctr": current_ctr,
            "sessions": ga4.sessions if ga4 else None,
            "conversion_rate": ga4.conversion_rate if ga4 else None,
        },
        "title_options": [
            f"{target_query} 완벽 가이드 2024 | 뷰티랩",
            f"[전문가 추천] {target_query} — 효과·성분·사용법",
            f"{target_query}: 뷰티랩이 검증한 최고의 선택",
        ],
        "meta_description_options": [
            f"{target_query}에 대한 모든 것. 성분 분석, 사용 순서, 피부 타입별 추천. 뷰티랩 전문가의 리얼 테스트 결과.",
            f"'{target_query}' 고민 해결! 효과·부작용·사용법을 한눈에 정리. 뷰티랩 추천 제품도 확인하세요.",
        ],
        "recommended_sections": _get_recommended_sections(target_query, search_intent),
        "internal_link_suggestions": [
            {"url": "/product/collagen-serum-50ml", "anchor_text": "뷰티랩 콜라겐 세럼"},
            {"url": "/skincare/routine-guide", "anchor_text": "스킨케어 순서 가이드"},
            {"url": "/category/serums", "anchor_text": "전체 세럼 라인업"},
        ],
        "structured_data_recommendations": [
            "Article (published_date, author, image)",
            "FAQPage (자주 묻는 질문 섹션)" if is_question else "BreadcrumbList",
            "BreadcrumbList",
        ],
        "content_gaps": [
            f"'{target_query}' 쿼리 주변의 LSI 키워드 추가 필요",
            "경쟁 페이지 대비 콘텐츠 depth 부족 (목표 1,500자 이상)",
            "이미지 alt 태그에 타겟 키워드 미포함",
        ],
        "seo_checklist": {
            "title_includes_keyword": True,
            "meta_description_present": bool(ga4),  # proxy
            "h1_matches_title": True,
            "faq_schema": is_question,
            "internal_links_min_3": (len(gsc_rows) > 0),
            "image_alt_tags": False,
        },
    }


def get_seo_recommendations(
    priority: str = "all",
    opportunity_type: str = "",
    limit: int = 15,
) -> dict:
    from rules.seo_rules import run_all_seo_rules
    all_hits = run_all_seo_rules()

    filtered = all_hits
    if priority != "all":
        filtered = [h for h in filtered if h.priority == priority]
    if opportunity_type:
        filtered = [h for h in filtered if h.opportunity_type == opportunity_type]

    # Sort by priority score (impact/effort * confidence)
    filtered.sort(
        key=lambda h: h.impact_score / max(h.effort_score, 1) * h.confidence_score,
        reverse=True,
    )
    filtered = filtered[:limit]

    priority_counts = {}
    for h in all_hits:
        priority_counts[h.priority] = priority_counts.get(h.priority, 0) + 1

    return {
        "filters": {"priority": priority, "opportunity_type": opportunity_type},
        "total_recommendations": len(all_hits),
        "returned": len(filtered),
        "priority_breakdown": priority_counts,
        "recommendations": [
            {
                "rule_id": h.rule_id,
                "rule_name": h.rule_name,
                "priority": h.priority,
                "opportunity_type": h.opportunity_type,
                "target_url": h.target_url,
                "target_queries": h.target_queries,
                "description": h.description,
                "problem": h.problem,
                "recommendation": h.recommendation,
                "expected_impact": h.expected_impact,
                "evidence": h.evidence,
                "effort_score": h.effort_score,
                "impact_score": h.impact_score,
                "confidence_score": h.confidence_score,
                "priority_score": round(h.impact_score / max(h.effort_score, 1) * h.confidence_score, 2),
                "required_approval": h.required_approval,
            }
            for h in filtered
        ],
    }


def _get_recommended_sections(query: str, intent: str) -> list[str]:
    base = [
        f"{query}란? (정의 및 핵심 특징)",
        "주요 성분 분석",
        "피부 타입별 사용 가이드",
        "올바른 사용 순서",
        "기대 효과 및 주의사항",
    ]
    if intent == "informational":
        base.append("자주 묻는 질문 (FAQ)")
    if "비교" in query or "vs" in query:
        base.insert(2, "비교 분석 테이블")
    base.append("뷰티랩 추천 제품")
    return base


# ---------------------------------------------------------------------------
# Phase 4-6: SEO Advanced tool handlers
# ---------------------------------------------------------------------------

def run_seo_pipeline_handler(
    site_url: str = "https://beautylab.co.kr",
    skip_llm_in_parallel: bool = True,
) -> dict:
    from workflows.seo_parallel_runner import SEOParallelRunner
    runner = SEOParallelRunner(max_workers=4, llm_augment=False, verbose=False)
    result = runner.run_full_seo_pipeline(site_url=site_url, skip_llm_in_parallel=skip_llm_in_parallel)
    # Return a summary to avoid huge tool output
    return {
        "status": "completed",
        "elapsed_seconds": result.get("total_elapsed_seconds"),
        "summary": result.get("summary", {}),
        "report_file": result.get("stages", {}).get("stage3", {}).get("report", {}).get("report_file", ""),
    }


def run_content_briefs_handler(
    max_briefs: int = 5,
    opportunity_types: list[str] | None = None,
) -> dict:
    from workflows.seo_content_brief import SEOContentBriefWorkflow
    wf = SEOContentBriefWorkflow(verbose=False)
    result = wf.generate_briefs(
        max_briefs=max_briefs,
        opportunity_types=opportunity_types,
        llm_augment=False,
    )
    return {
        "briefs_generated": result["briefs_generated"],
        "run_id": result["run_id"],
        "briefs": result["briefs"][:3],  # Truncate for tool output
    }


def run_structured_data_audit_handler() -> dict:
    from workflows.seo_structured_data import SEOStructuredDataWorkflow
    wf = SEOStructuredDataWorkflow(verbose=False)
    return wf.audit_and_recommend(llm_augment=False)


def run_internal_link_analysis_handler() -> dict:
    from workflows.seo_internal_link import SEOInternalLinkWorkflow
    wf = SEOInternalLinkWorkflow(verbose=False)
    return wf.analyze_and_recommend(llm_augment=False)


def create_experiment_baselines_handler(top_n: int = 5) -> dict:
    from workflows.seo_experiment import SEOExperimentWorkflow
    wf = SEOExperimentWorkflow(verbose=False)
    return wf.create_experiment_baselines(top_n=top_n)


def analyze_experiment_results_handler() -> dict:
    from workflows.seo_experiment import SEOExperimentWorkflow
    wf = SEOExperimentWorkflow(verbose=False)
    result = wf.simulate_results_and_learn(llm_augment=True)
    return {
        "experiments_completed": result["experiments_completed"],
        "knowledge_items_created": result["knowledge_items_created"],
        "results_summary": [
            {
                "experiment_id": e["experiment_id"],
                "target_url": e["target_url"],
                "change_type": e["change_type"],
                "outcome": e["outcome"],
                "delta": e.get("delta"),
            }
            for e in result["results"]
        ],
    }


def generate_seo_report_handler(
    report_date: str | None = None,
    export_markdown: bool = True,
) -> dict:
    from workflows.seo_reporting import SEOReportingWorkflow
    wf = SEOReportingWorkflow(verbose=False)
    result = wf.generate_weekly_report(
        report_date=report_date,
        export_markdown=export_markdown,
        llm_augment=False,
    )
    return {
        "report_date": result["report_date"],
        "report_file": result["report_file"],
        "stats": result["stats"],
        "markdown_preview": result["markdown"][:1500] + "..." if len(result["markdown"]) > 1500 else result["markdown"],
    }


def list_content_briefs_handler(status: str = "", url: str = "") -> dict:
    from storage.seo_repository import list_content_briefs
    briefs = list_content_briefs(status=status, url=url)
    return {
        "total": len(briefs),
        "filters": {"status": status, "url": url},
        "briefs": briefs,
    }


def get_knowledge_items_handler(source_type: str = "", tag: str = "") -> dict:
    from storage.seo_repository import list_knowledge_items
    items = list_knowledge_items(source_type=source_type, tag=tag)
    return {
        "total": len(items),
        "filters": {"source_type": source_type, "tag": tag},
        "items": items,
    }


# ── Phase 4-6 ext: Editor / Approval / Governance handlers ───────────────────

def generate_seo_draft_handler(brief_id: str, llm_augment: bool = True) -> dict:
    from workflows.seo_editor import SEOEditorWorkflow
    wf = SEOEditorWorkflow(verbose=False)
    return wf.generate_draft(brief_id=brief_id, llm_augment=llm_augment)


def generate_all_drafts_handler(max_briefs: int = 5, llm_augment: bool = False) -> dict:
    from workflows.seo_editor import SEOEditorWorkflow
    wf = SEOEditorWorkflow(verbose=False)
    return wf.generate_drafts_for_pending_briefs(max_briefs=max_briefs, llm_augment=llm_augment)


def create_seo_recommendations_handler(max_hits: int = 20) -> dict:
    from workflows.seo_approval import SEOApprovalWorkflow
    wf = SEOApprovalWorkflow(verbose=False)
    return wf.create_recommendations(max_hits=max_hits)


def list_pending_recommendations_handler() -> dict:
    from workflows.seo_approval import SEOApprovalWorkflow
    wf = SEOApprovalWorkflow(verbose=False)
    return wf.list_pending()


def approve_seo_recommendation_handler(rec_id: str, approver_notes: str = "") -> dict:
    from workflows.seo_approval import SEOApprovalWorkflow
    wf = SEOApprovalWorkflow(verbose=False)
    return wf.approve(rec_id=rec_id, approver_notes=approver_notes)


def reject_seo_recommendation_handler(rec_id: str, reason: str = "") -> dict:
    from workflows.seo_approval import SEOApprovalWorkflow
    wf = SEOApprovalWorkflow(verbose=False)
    return wf.reject(rec_id=rec_id, reason=reason)


def get_seo_approval_summary_handler() -> dict:
    from workflows.seo_approval import SEOApprovalWorkflow
    wf = SEOApprovalWorkflow(verbose=False)
    return wf.get_approval_summary()


def audit_seo_draft_handler(draft_id: str, llm_augment: bool = False) -> dict:
    from workflows.seo_governance import SEOGovernanceWorkflow
    wf = SEOGovernanceWorkflow(verbose=False)
    return wf.audit_draft(draft_id=draft_id, llm_augment=llm_augment)


def audit_all_drafts_handler(llm_augment: bool = False) -> dict:
    from workflows.seo_governance import SEOGovernanceWorkflow
    wf = SEOGovernanceWorkflow(verbose=False)
    return wf.audit_all_pending_drafts(llm_augment=llm_augment)


def get_governance_summary_handler() -> dict:
    from workflows.seo_governance import SEOGovernanceWorkflow
    wf = SEOGovernanceWorkflow(verbose=False)
    return wf.get_governance_summary()


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
    # Phase 2 (performance marketing)
    "run_diagnosis": run_diagnosis,
    "list_recommendations": list_recommendations_handler,
    "approve_perf_recommendation": approve_recommendation,
    "reject_perf_recommendation": reject_recommendation,
    "get_perf_approval_summary": get_approval_summary,
    # Phase 4-6 ext: Editor / Approval / Governance
    "generate_seo_draft": generate_seo_draft_handler,
    "generate_all_drafts": generate_all_drafts_handler,
    "create_seo_recommendations": create_seo_recommendations_handler,
    "list_pending_recommendations": list_pending_recommendations_handler,
    "approve_recommendation": approve_seo_recommendation_handler,
    "reject_recommendation": reject_seo_recommendation_handler,
    "get_approval_summary": get_seo_approval_summary_handler,
    "audit_seo_draft": audit_seo_draft_handler,
    "audit_all_drafts": audit_all_drafts_handler,
    "get_governance_summary": get_governance_summary_handler,
    # Phase 4-6: SEO Advanced
    "run_seo_pipeline": run_seo_pipeline_handler,
    "run_content_briefs": run_content_briefs_handler,
    "run_structured_data_audit": run_structured_data_audit_handler,
    "run_internal_link_analysis": run_internal_link_analysis_handler,
    "create_experiment_baselines": create_experiment_baselines_handler,
    "analyze_experiment_results": analyze_experiment_results_handler,
    "generate_seo_report": generate_seo_report_handler,
    "list_content_briefs": list_content_briefs_handler,
    "get_knowledge_items": get_knowledge_items_handler,
    # Phase 3: SEO
    "get_seo_overview": get_seo_overview,
    "run_seo_diagnosis": run_seo_diagnosis,
    "get_seo_query_opportunities": get_seo_query_opportunities,
    "get_technical_audit": get_technical_audit,
    "get_pagespeed_summary": get_pagespeed_summary,
    "generate_content_brief": generate_content_brief,
    "get_seo_recommendations": get_seo_recommendations,
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
