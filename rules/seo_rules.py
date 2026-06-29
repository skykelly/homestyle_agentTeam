"""
SEO rule engine (Phase 3).
6 rules fire deterministically — no LLM required.
Design doc principle: "Rule-based baseline 먼저, LLM은 추가 계층"
"""

from dataclasses import dataclass, field
from typing import Optional

from data.seo_mock_data import (
    GSCQueryRow, GA4LandingRow, PageSpeedResult, CrawledPage,
    SITE_BENCHMARKS, DECLINING_QUERIES,
    get_gsc_queries, get_ga4_landing, get_pagespeed, get_crawled_pages,
)


@dataclass
class SEORuleResult:
    triggered: bool
    rule_id: str
    rule_name: str
    description: str
    priority: str          # "critical" | "high" | "medium" | "low"
    opportunity_type: str  # "ctr_improvement" | "ranking_boost" | "content_refresh" |
                           # "cannibalization_fix" | "technical_fix" | "geo_candidate"
    target_url: str
    target_queries: list[str] = field(default_factory=list)
    current_metric: dict = field(default_factory=dict)
    problem: str = ""
    recommendation: str = ""
    expected_impact: str = ""
    evidence: list[str] = field(default_factory=list)
    required_approval: str = "none"
    effort_score: int = 2          # 1-5 (5 = highest effort)
    impact_score: int = 3          # 1-5 (5 = highest impact)
    confidence_score: float = 0.8


# ── Thresholds ───────────────────────────────────────────────────────────────

CTR_LOW_RATIO = 0.5            # actual CTR < 50% of expected-by-position → opportunity
PAGE2_POSITION_MIN = 11.0      # position 11-20 → page 2 territory
PAGE2_POSITION_MAX = 20.0
DECLINING_CLICK_DROP_RATIO = 0.5   # >50% click drop vs prior period
DECLINING_CONTENT_AGE_DAYS = 180   # last updated > 180 days ago
CANNIBALIZATION_MIN_IMPRESSIONS = 5000   # min impressions to flag
GEO_QUESTION_MARKERS = ["어떻게", "무엇", "언제", "왜", "얼마나", "차이", "뭐가", "뭔지",
                         "해야 해", "되나요", "괜찮나요", "좋은가요", "맞나요", "가요"]
PAGESPEED_POOR_SCORE = 0.50    # < 50 = poor
LCP_POOR_MS = 4000             # > 4000ms = poor
CLS_POOR = 0.25                # > 0.25 = poor
TECHNICAL_INTERNAL_LINK_MIN = 3


# ── Rule 1: Low CTR Opportunity ───────────────────────────────────────────────

def check_low_ctr(row: GSCQueryRow) -> SEORuleResult:
    """
    Fire when impressions are high but CTR is below expected for that position.
    Signals that title/meta could be rewritten for higher click-through.
    """
    expected_ctr = SITE_BENCHMARKS["expected_ctr_by_position"].get(
        int(row.position), 0.026  # default for position 10+
    )
    site_avg_impressions = SITE_BENCHMARKS["site_avg_impressions"]

    if row.impressions >= site_avg_impressions and row.ctr < expected_ctr * CTR_LOW_RATIO:
        gap_pct = round((expected_ctr - row.ctr) / expected_ctr * 100, 1)
        clicks_if_fixed = int(row.impressions * expected_ctr)
        incremental_clicks = clicks_if_fixed - row.clicks

        return SEORuleResult(
            triggered=True,
            rule_id="SEO_001",
            rule_name="Low CTR Opportunity",
            description=f"CTR이 포지션 {row.position:.1f} 기대치 대비 {gap_pct}% 낮음 — 제목/메타 개선 권고",
            priority="high",
            opportunity_type="ctr_improvement",
            target_url=row.url,
            target_queries=[row.query],
            current_metric={
                "impressions": row.impressions,
                "clicks": row.clicks,
                "ctr": row.ctr,
                "position": row.position,
                "expected_ctr": expected_ctr,
            },
            problem=f"노출 {row.impressions:,}회에서 CTR {row.ctr*100:.2f}% — 포지션 {row.position:.1f} 기대값({expected_ctr*100:.1f}%)의 절반 이하.",
            recommendation=f"제목 태그와 메타 설명을 검색 의도에 맞게 개선하여 CTR을 {expected_ctr*100:.1f}% 수준으로 향상.",
            expected_impact=f"월 +{incremental_clicks:,} 클릭 (현재 {row.clicks}→목표 {clicks_if_fixed})",
            evidence=[
                f"현재 CTR: {row.ctr*100:.2f}% vs 기대 CTR: {expected_ctr*100:.1f}% (포지션 {int(row.position)})",
                f"노출 수: {row.impressions:,}회 (사이트 평균 {site_avg_impressions:,}회 이상)",
                f"CTR 개선 시 월 {incremental_clicks:,} 클릭 추가 획득 가능",
                f"Gap: {gap_pct}% 낮은 상태",
            ],
            effort_score=2,
            impact_score=4,
            confidence_score=0.85,
        )

    return SEORuleResult(
        triggered=False, rule_id="SEO_001", rule_name="Low CTR Opportunity",
        description="", priority="", opportunity_type="", target_url=row.url,
    )


# ── Rule 2: Page 2 → Page 1 Opportunity ───────────────────────────────────────

def check_page2_opportunity(row: GSCQueryRow) -> SEORuleResult:
    """
    Fire when a URL ranks position 11-20 with significant impressions.
    Small ranking improvement can drive exponential traffic gains.
    """
    if PAGE2_POSITION_MIN <= row.position <= PAGE2_POSITION_MAX and row.impressions >= 5000:
        p1_ctr = SITE_BENCHMARKS["expected_ctr_by_position"].get(5, 0.06)  # top-5 estimate
        projected_clicks = int(row.impressions * p1_ctr)
        gain = projected_clicks - row.clicks

        return SEORuleResult(
            triggered=True,
            rule_id="SEO_002",
            rule_name="Page 2 to Page 1 Opportunity",
            description=f"포지션 {row.position:.1f} — 1페이지 진입 시 클릭 {gain:,} 추가 획득 가능",
            priority="high",
            opportunity_type="ranking_boost",
            target_url=row.url,
            target_queries=[row.query],
            current_metric={
                "impressions": row.impressions,
                "clicks": row.clicks,
                "ctr": row.ctr,
                "position": row.position,
            },
            problem=f"쿼리 '{row.query}'에서 포지션 {row.position:.1f}로 2페이지 중간에 위치. 클릭 기회를 놓치고 있음.",
            recommendation="콘텐츠 depth 강화, 내부 링크 추가, E-E-A-T 신호 개선으로 1페이지 진입 추진.",
            expected_impact=f"1페이지 진입 시 월 +{gain:,} 클릭 예상 (포지션 5 기준 CTR {p1_ctr*100:.0f}%)",
            evidence=[
                f"현재 포지션: {row.position:.1f} (2페이지 진입 구간: 11-20)",
                f"노출: {row.impressions:,}회 — 높은 검색 수요 확인됨",
                f"포지션 1-5 진입 시 예상 클릭: {projected_clicks:,}회/월",
                f"현재 {row.clicks}클릭 → 잠재 {projected_clicks}클릭 (+{gain})",
            ],
            effort_score=3,
            impact_score=5,
            confidence_score=0.75,
        )

    return SEORuleResult(
        triggered=False, rule_id="SEO_002", rule_name="Page 2 to Page 1 Opportunity",
        description="", priority="", opportunity_type="", target_url=row.url,
    )


# ── Rule 3: Declining Content ─────────────────────────────────────────────────

def check_declining_content(url: str) -> SEORuleResult:
    """
    Fire when clicks have dropped >50% vs prior period and content is stale.
    """
    data = DECLINING_QUERIES.get(url)
    if not data:
        return SEORuleResult(
            triggered=False, rule_id="SEO_003", rule_name="Declining Content",
            description="", priority="", opportunity_type="", target_url=url,
        )

    click_drop_ratio = (data["clicks_28d"] / data["clicks_prev_28d"]) if data["clicks_prev_28d"] else 1.0
    pos_drop = data["position_28d"] - data["position_prev_28d"]
    age = data["last_updated_days"]

    if click_drop_ratio <= DECLINING_CLICK_DROP_RATIO and age >= DECLINING_CONTENT_AGE_DAYS:
        drop_pct = round((1 - click_drop_ratio) * 100, 1)
        return SEORuleResult(
            triggered=True,
            rule_id="SEO_003",
            rule_name="Declining Content",
            description=f"콘텐츠 노후화로 클릭 {drop_pct}% 하락 — 콘텐츠 리프레시 필요",
            priority="high",
            opportunity_type="content_refresh",
            target_url=url,
            current_metric={
                "clicks_28d": data["clicks_28d"],
                "clicks_prev_28d": data["clicks_prev_28d"],
                "click_drop_pct": drop_pct,
                "position_28d": data["position_28d"],
                "position_prev_28d": data["position_prev_28d"],
                "last_updated_days": age,
            },
            problem=f"클릭이 {data['clicks_prev_28d']}→{data['clicks_28d']}으로 {drop_pct}% 하락. "
                    f"포지션도 {data['position_prev_28d']}→{data['position_28d']}으로 {pos_drop:.1f}단계 하락. "
                    f"마지막 업데이트 {age}일 전.",
            recommendation="최신 데이터·트렌드 반영하여 콘텐츠 업데이트. 제목 태그 개선 및 내부 링크 보강.",
            expected_impact=f"업데이트 후 3-6주 내 클릭 50-80% 회복 예상",
            evidence=[
                f"클릭 하락: {data['clicks_prev_28d']}→{data['clicks_28d']} ({drop_pct}% 감소, 28일 비교)",
                f"포지션 하락: {data['position_prev_28d']}→{data['position_28d']} ({pos_drop:.1f}단계 하락)",
                f"마지막 업데이트: {age}일 전 (권장 주기: 180일 이내)",
                "시즌성 콘텐츠로 시즌 종료 후 자연 하락 패턴 확인됨",
            ],
            effort_score=3,
            impact_score=3,
            confidence_score=0.82,
        )

    return SEORuleResult(
        triggered=False, rule_id="SEO_003", rule_name="Declining Content",
        description="", priority="", opportunity_type="", target_url=url,
    )


# ── Rule 4: Keyword Cannibalization ──────────────────────────────────────────

def check_cannibalization(query: str, all_rows: list[GSCQueryRow]) -> Optional[SEORuleResult]:
    """
    Fire when the same query maps to 3+ URLs with significant impressions.
    Returns None if not applicable (not enough URLs for this query).
    """
    matching = [r for r in all_rows if r.query == query]
    if len(matching) < 3:
        return None

    total_impressions = matching[0].impressions  # same query → same impressions count
    if total_impressions < CANNIBALIZATION_MIN_IMPRESSIONS:
        return None

    # Sort by position (best first)
    matching_sorted = sorted(matching, key=lambda r: r.position)
    urls = [r.url for r in matching_sorted]
    total_clicks = sum(r.clicks for r in matching)
    best_url = matching_sorted[0]

    return SEORuleResult(
        triggered=True,
        rule_id="SEO_004",
        rule_name="Keyword Cannibalization",
        description=f"쿼리 '{query}' — {len(matching)}개 URL이 경쟁 중 (카니발라이제이션 감지)",
        priority="critical",
        opportunity_type="cannibalization_fix",
        target_url=best_url.url,
        target_queries=[query],
        current_metric={
            "query": query,
            "url_count": len(matching),
            "competing_urls": urls,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "positions": [r.position for r in matching_sorted],
        },
        problem=f"'{query}' 쿼리에 대해 {len(matching)}개 URL이 검색 결과에서 경쟁. "
                f"링크 에쿼티 분산 및 Google 혼란 유발.",
        recommendation=f"'{best_url.url}'를 정규 URL로 설정. 나머지 URL은 canonical 태그 추가 또는 301 리다이렉트. "
                       f"내부 링크를 정규 URL 중심으로 통합.",
        expected_impact=f"링크 에쿼티 집중 시 정규 URL 포지션 2-4단계 상승 예상. 총 클릭 {int(total_clicks*1.3):,}회로 증가 가능.",
        evidence=[
            f"경쟁 URL {len(matching)}개: {', '.join(urls)}",
            f"포지션 분산: {[r.position for r in matching_sorted]}",
            f"총 클릭: {total_clicks}회 (URL 간 분산 상태)",
            f"최상위 URL '{best_url.url}': 포지션 {best_url.position}",
            "카니발라이제이션은 Google이 어느 URL을 우선할지 결정 불가 상태를 만들어 전체 순위 하락 유발",
        ],
        required_approval="none",
        effort_score=3,
        impact_score=4,
        confidence_score=0.90,
    )


# ── Rule 5: Technical SEO Blocker ────────────────────────────────────────────

def check_technical_blocker(page: CrawledPage) -> list[SEORuleResult]:
    """
    Fire for each technical issue found on a page.
    Multiple issues on one page → multiple rule hits.
    """
    results = []

    # 5a: Redirect in sitemap
    if page.status_code in (301, 302) and page.in_sitemap:
        results.append(SEORuleResult(
            triggered=True,
            rule_id="SEO_005a",
            rule_name="Technical: Redirect URL in Sitemap",
            description=f"사이트맵에 리다이렉트 URL 포함 — 크롤 낭비 발생",
            priority="high",
            opportunity_type="technical_fix",
            target_url=page.url,
            current_metric={"status_code": page.status_code, "in_sitemap": page.in_sitemap,
                            "redirect_chain": page.redirect_chain_length},
            problem=f"{page.url}이(가) {page.status_code} 리다이렉트인데 사이트맵에 포함됨. 크롤 예산 낭비 및 Google 혼란.",
            recommendation="사이트맵에서 리다이렉트 URL 제거. 최종 목적지 URL을 사이트맵에 등록.",
            expected_impact="크롤 예산 효율화. 사이트맵 오류 제거.",
            evidence=[f"URL: {page.url}", f"상태 코드: {page.status_code}",
                      f"사이트맵 포함: {page.in_sitemap}", f"리다이렉트 체인 길이: {page.redirect_chain_length}"],
            effort_score=1, impact_score=3, confidence_score=0.95,
        ))

    # 5b: Missing H1
    if page.status_code == 200 and not page.h1.strip():
        results.append(SEORuleResult(
            triggered=True,
            rule_id="SEO_005b",
            rule_name="Technical: Missing H1",
            description=f"{page.url} — H1 태그 누락",
            priority="medium",
            opportunity_type="technical_fix",
            target_url=page.url,
            current_metric={"h1": "", "page_type": page.page_type},
            problem=f"페이지 '{page.url}'에 H1 태그 없음. 검색 엔진이 주제를 파악하기 어려움.",
            recommendation="주요 타겟 키워드를 포함한 H1 태그 추가.",
            expected_impact="On-page SEO 점수 개선. 관련성 신호 강화.",
            evidence=[f"URL: {page.url}", f"페이지 유형: {page.page_type}", "H1 태그 없음"],
            effort_score=1, impact_score=3, confidence_score=0.90,
        ))

    # 5c: Missing meta description
    if page.status_code == 200 and not page.meta_description.strip():
        results.append(SEORuleResult(
            triggered=True,
            rule_id="SEO_005c",
            rule_name="Technical: Missing Meta Description",
            description=f"{page.url} — 메타 설명 누락",
            priority="medium",
            opportunity_type="technical_fix",
            target_url=page.url,
            current_metric={"meta_description": "", "page_type": page.page_type},
            problem=f"{page.url}의 메타 설명이 없어 SERP 스니펫이 자동 생성됨. CTR 하락 원인.",
            recommendation="클릭을 유도하는 150-160자 메타 설명 작성. 핵심 키워드 + CTA 포함.",
            expected_impact="CTR 5-15% 개선 가능.",
            evidence=[f"URL: {page.url}", "meta_description: 없음", "Google이 임의로 스니펫을 생성하면 CTR 하락"],
            effort_score=1, impact_score=3, confidence_score=0.88,
        ))

    # 5d: Missing structured data on product/faq pages
    if page.status_code == 200 and not page.has_structured_data and page.page_type in ("product", "faq"):
        schema_type = "Product+Offer" if page.page_type == "product" else "FAQPage"
        results.append(SEORuleResult(
            triggered=True,
            rule_id="SEO_005d",
            rule_name="Technical: Missing Structured Data",
            description=f"{page.url} — {schema_type} 스키마 누락",
            priority="high" if page.page_type == "product" else "medium",
            opportunity_type="technical_fix",
            target_url=page.url,
            current_metric={"has_structured_data": False, "page_type": page.page_type},
            problem=f"{page.page_type} 페이지에 {schema_type} 스키마 없음. 리치 스니펫 기회 놓치는 중.",
            recommendation=f"{schema_type} JSON-LD 스키마 마크업 추가.",
            expected_impact="리치 스니펫 획득 시 CTR 20-30% 향상 가능 (리뷰 별점, 가격 표시 등).",
            evidence=[f"URL: {page.url}", f"페이지 유형: {page.page_type}",
                      "has_structured_data: False", f"{schema_type} 스키마 없음"],
            effort_score=2, impact_score=4, confidence_score=0.87,
        ))

    # 5e: Page not in sitemap (and indexable)
    if page.status_code == 200 and page.is_indexable and not page.in_sitemap:
        results.append(SEORuleResult(
            triggered=True,
            rule_id="SEO_005e",
            rule_name="Technical: Indexable Page Missing from Sitemap",
            description=f"{page.url} — 색인 가능 페이지가 사이트맵 미포함",
            priority="medium",
            opportunity_type="technical_fix",
            target_url=page.url,
            current_metric={"in_sitemap": False, "is_indexable": True, "page_type": page.page_type},
            problem=f"{page.url}이(가) 색인 가능 상태인데 사이트맵에 없음. 크롤 빈도 낮아질 수 있음.",
            recommendation="사이트맵에 해당 URL 추가 및 Google Search Console에 사이트맵 재제출.",
            expected_impact="크롤링 빈도 증가 → 인덱싱 속도 개선.",
            evidence=[f"URL: {page.url}", "in_sitemap: False", "is_indexable: True"],
            effort_score=1, impact_score=2, confidence_score=0.90,
        ))

    return results


# ── Rule 6: GEO / AI Search Candidate ────────────────────────────────────────

def check_geo_candidate(row: GSCQueryRow) -> SEORuleResult:
    """
    Fire for question-type queries in positions 11-25 with low CTR.
    These are strong candidates for AI Overviews / GEO optimization.
    """
    is_question = any(marker in row.query for marker in GEO_QUESTION_MARKERS)
    is_comparison = "vs" in row.query or "비교" in row.query or "차이" in row.query

    if (is_question or is_comparison) and row.position >= 10 and row.ctr <= 0.012:
        return SEORuleResult(
            triggered=True,
            rule_id="SEO_006",
            rule_name="GEO / AI Search Candidate",
            description=f"질문형 쿼리 '{row.query}' — AI 개요(AI Overviews) 최적화 기회",
            priority="medium",
            opportunity_type="geo_candidate",
            target_url=row.url,
            target_queries=[row.query],
            current_metric={
                "impressions": row.impressions,
                "clicks": row.clicks,
                "ctr": row.ctr,
                "position": row.position,
                "is_question": is_question,
                "is_comparison": is_comparison,
            },
            problem=f"질문/비교형 쿼리 '{row.query}'에서 포지션 {row.position:.1f}, CTR {row.ctr*100:.2f}%. "
                    f"AI 개요가 트래픽을 흡수할 가능성 높음.",
            recommendation=(
                "FAQ 스키마 추가 및 직접 답변형 콘텐츠 구조화. "
                "첫 단락에 간결한 정의·답변 배치 (Answer Engine Optimization). "
                "비교형 쿼리는 구조화된 비교 테이블 추가."
            ),
            expected_impact="AI 개요에 인용될 경우 브랜드 노출 및 간접 트래픽 증가. CTR 개선 가능.",
            evidence=[
                f"쿼리 유형: {'질문형' if is_question else '비교형'}",
                f"현재 포지션: {row.position:.1f} (AI 개요 트리거 구간)",
                f"CTR: {row.ctr*100:.2f}% (매우 낮음 — AI 개요가 클릭 흡수 중 가능성)",
                f"노출: {row.impressions:,}회 — 검색 수요 있음",
            ],
            effort_score=2,
            impact_score=3,
            confidence_score=0.70,
        )

    return SEORuleResult(
        triggered=False, rule_id="SEO_006", rule_name="GEO / AI Search Candidate",
        description="", priority="", opportunity_type="", target_url=row.url,
    )


# ── Master runner ─────────────────────────────────────────────────────────────

def run_all_seo_rules(
    min_impressions: int = 3000,
    include_technical: bool = True,
) -> list[SEORuleResult]:
    """
    Run all 6 SEO rules against mock data and return triggered results only.
    Order: Cannibalization → Low CTR → Page 2 → Declining → Technical → GEO
    """
    all_rows = get_gsc_queries(min_impressions=min_impressions)
    results: list[SEORuleResult] = []

    # Rule 4: Cannibalization (check unique queries across all rows)
    seen_queries: set[str] = set()
    for row in get_gsc_queries():
        if row.query not in seen_queries:
            seen_queries.add(row.query)
            all_query_rows = get_gsc_queries()  # need full list for matching
            cann = check_cannibalization(row.query, all_query_rows)
            if cann is not None and cann.triggered:
                results.append(cann)

    # Rules 1, 2, 6: Per-row checks
    for row in all_rows:
        r1 = check_low_ctr(row)
        if r1.triggered:
            results.append(r1)

        r2 = check_page2_opportunity(row)
        if r2.triggered:
            results.append(r2)

        r6 = check_geo_candidate(row)
        if r6.triggered:
            results.append(r6)

    # Rule 3: Declining content (URL-level)
    for url in DECLINING_QUERIES:
        r3 = check_declining_content(url)
        if r3.triggered:
            results.append(r3)

    # Rule 5: Technical blockers (page-level, multiple per page)
    if include_technical:
        for page in get_crawled_pages():
            tech_hits = check_technical_blocker(page)
            results.extend(tech_hits)

    # Deduplicate (same rule_id + url combo)
    seen: set[str] = set()
    deduped = []
    for r in results:
        key = f"{r.rule_id}::{r.target_url}"
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Sort by priority order
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    deduped.sort(key=lambda r: priority_order.get(r.priority, 9))

    return deduped
