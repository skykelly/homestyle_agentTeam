"""
Phase 3 SEO Agent Demo
뷰티랩(BeautyLab) 한국 뷰티 이커머스 SEO 진단 데모

Demonstrates:
  1. Rule engine — 6 SEO rules running deterministically
  2. Site health overview
  3. Query opportunity analysis (Low CTR, Page 2, Cannibalization, GEO)
  4. Technical SEO audit
  5. PageSpeed Core Web Vitals summary
  6. Content brief generation
  7. Full SEO agent conversational interaction (optional, requires API key)
"""

import json
import os
import sys

from rules.seo_rules import run_all_seo_rules
from tools.handlers import (
    get_seo_overview,
    get_seo_query_opportunities,
    get_technical_audit,
    get_pagespeed_summary,
    generate_content_brief,
    get_seo_recommendations,
)


# ── ANSI colors ──────────────────────────────────────────────────────────────

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def priority_color(p: str) -> str:
    return {
        "critical": RED + BOLD,
        "high": YELLOW,
        "medium": CYAN,
        "low": GREEN,
    }.get(p, "")


def section(title: str) -> None:
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{title}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")


def subsection(title: str) -> None:
    print(f"\n{CYAN}── {title} ──{RESET}")


# ── Demo sections ─────────────────────────────────────────────────────────────

def demo_rule_engine():
    section("Phase 3 — SEO Rule Engine (6 Rules)")
    print("규칙 엔진을 실행합니다 (LLM 없이 결정론적 탐지)...\n")

    hits = run_all_seo_rules(min_impressions=3000)

    priority_counts = {}
    type_counts = {}
    for h in hits:
        priority_counts[h.priority] = priority_counts.get(h.priority, 0) + 1
        type_counts[h.opportunity_type] = type_counts.get(h.opportunity_type, 0) + 1

    print(f"총 탐지 이슈: {len(hits)}건\n")
    print("우선순위 분포:")
    for p in ["critical", "high", "medium", "low"]:
        count = priority_counts.get(p, 0)
        if count:
            print(f"  {priority_color(p)}{p.upper()}: {count}건{RESET}")

    print("\n기회 유형 분포:")
    for t, c in type_counts.items():
        print(f"  {t}: {c}건")

    print(f"\n{BOLD}상위 이슈 (우선순위 순):{RESET}")
    for h in hits[:8]:
        color = priority_color(h.priority)
        print(f"\n  {color}[{h.rule_id}] [{h.priority.upper()}]{RESET} {h.description}")
        print(f"  URL: {h.target_url}")
        if h.target_queries:
            print(f"  쿼리: {h.target_queries[0]}")
        print(f"  예상 임팩트: {h.expected_impact}")
        print(f"  노력도: {h.effort_score}/5 | 임팩트: {h.impact_score}/5 | 신뢰도: {h.confidence_score:.0%}")


def demo_site_overview():
    section("Phase 3 — Site Health Overview (GSC + GA4)")
    overview = get_seo_overview()
    m = overview["metrics"]
    signals = overview["health_signals"]

    print(f"사이트: {overview['site']} ({overview['site_url']})")
    print(f"카테고리: {overview['category']}")
    print(f"분석 기간: {overview['period']}\n")

    def trend_icon(t: str) -> str:
        return "▼" if t == "하락" else "▲"

    def delta_color(pct: float) -> str:
        return RED if pct < 0 else GREEN

    print(f"{'지표':<25} {'현재':>12} {'전기대비':>10} {'트렌드':>6}")
    print("-" * 58)

    click_d = m['total_clicks_delta_pct']
    print(f"{'총 클릭':<25} {m['total_clicks']:>12,} {delta_color(click_d)}{click_d:>+9.1f}%{RESET} {trend_icon(signals['click_trend']):>6}")

    imp_d = m['total_impressions_delta_pct']
    print(f"{'총 노출':<25} {m['total_impressions']:>12,} {delta_color(imp_d)}{imp_d:>+9.1f}%{RESET}")

    ctr_d = m['avg_ctr_delta_pct']
    print(f"{'평균 CTR':<25} {m['avg_ctr']*100:>11.1f}% {delta_color(ctr_d)}{ctr_d:>+9.1f}%{RESET} {trend_icon(signals['ctr_trend']):>6}")

    pos_d = m['avg_position_delta']
    print(f"{'평균 포지션':<25} {m['avg_position']:>12} {delta_color(-pos_d)}{pos_d:>+9.1f}{RESET} {trend_icon(signals['position_trend']):>6}")

    rev_d = m['organic_revenue_delta_pct']
    print(f"{'오가닉 매출':<25} {m['organic_revenue_krw']:>12,}원 {delta_color(rev_d)}{rev_d:>+9.1f}%{RESET}")


def demo_query_opportunities():
    section("Phase 3 — Query Opportunities")

    subsection("카니발라이제이션 (Keyword Cannibalization)")
    cann = get_seo_query_opportunities(opportunity_type="cannibalization_fix", min_impressions=5000)
    for opp in cann["opportunities"]:
        print(f"\n  {RED}{BOLD}[{opp['rule_id']}] {opp['description']}{RESET}")
        print(f"  타겟 URL: {opp['target_url']}")
        if opp.get("target_queries"):
            print(f"  쿼리: {opp['target_queries']}")
        print(f"  예상 임팩트: {opp['expected_impact']}")

    subsection("Low CTR 기회 (High Impression / Low CTR)")
    ctr_opps = get_seo_query_opportunities(opportunity_type="ctr_improvement", limit=5)
    for opp in ctr_opps["opportunities"]:
        print(f"\n  {YELLOW}[{opp['rule_id']}]{RESET} {opp['description']}")
        print(f"  URL: {opp['target_url']} | 쿼리: {opp['target_queries']}")
        print(f"  예상: {opp['expected_impact']} | I:{opp['impact_score']} E:{opp['effort_score']}")

    subsection("Page 2 → Page 1 기회")
    page2 = get_seo_query_opportunities(opportunity_type="ranking_boost", limit=5)
    for opp in page2["opportunities"]:
        print(f"\n  {CYAN}[{opp['rule_id']}]{RESET} {opp['description']}")
        print(f"  URL: {opp['target_url']}")
        print(f"  예상: {opp['expected_impact']}")

    subsection("GEO / AI Search 후보")
    geo = get_seo_query_opportunities(opportunity_type="geo_candidate", limit=5)
    for opp in geo["opportunities"]:
        print(f"\n  [{opp['rule_id']}] {opp['description']}")
        print(f"  쿼리: {opp['target_queries']}")


def demo_technical_audit():
    section("Phase 3 — Technical SEO Audit")
    audit = get_technical_audit(page_type="all")

    print(f"점검 페이지: {audit['pages_audited']}개 | 탐지 이슈: {audit['total_issues']}건\n")

    print(f"{'URL':<40} {'상태':>5} {'H1':>4} {'Meta':>5} {'Schema':>7} {'Sitemap':>8} {'이슈':>4}")
    print("-" * 80)
    for p in audit["page_summaries"]:
        h1_ok = "✓" if p["has_h1"] else "✗"
        meta_ok = "✓" if p["has_meta_description"] else "✗"
        schema_ok = "✓" if p["has_structured_data"] else "✗"
        sitemap_ok = "✓" if p["in_sitemap"] else "✗"
        issues = p["issue_count"]
        url_short = p["url"][:38]
        status_color = RED if p["status_code"] != 200 else ""
        issue_color = RED if issues > 2 else YELLOW if issues > 0 else GREEN
        print(
            f"  {status_color}{url_short:<38}{RESET} "
            f"{p['status_code']:>5} "
            f"{'✓' if h1_ok=='✓' else RED+'✗'+RESET:>4} "
            f"{'✓' if meta_ok=='✓' else RED+'✗'+RESET:>5} "
            f"{'✓' if schema_ok=='✓' else RED+'✗'+RESET:>7} "
            f"{sitemap_ok:>8} "
            f"{issue_color}{issues:>4}{RESET}"
        )

    if audit["issues"]:
        print(f"\n{BOLD}주요 이슈:{RESET}")
        for issue in audit["issues"][:6]:
            color = RED if issue["priority"] in ("critical", "high") else YELLOW
            print(f"\n  {color}[{issue['rule_id']}] {issue['description']}{RESET}")
            print(f"  권고: {issue['recommendation']}")


def demo_pagespeed():
    section("Phase 3 — PageSpeed / Core Web Vitals")
    ps = get_pagespeed_summary(strategy="mobile")

    summary = ps["summary"]
    print(f"모바일 기준 | 분석 페이지: {ps['pages_analyzed']}개 | 성능 Poor: {ps['pages_with_poor_performance']}개")
    print(f"평균 성능 점수: {summary['avg_performance_score']:.2f} | 평균 LCP: {summary['avg_lcp_ms']:.0f}ms | 평균 CLS: {summary['avg_cls']:.3f}\n")

    print(f"{'URL':<40} {'점수':>6} {'LCP(ms)':>8} {'LCP등급':>9} {'CLS':>6} {'CLS등급':>9}")
    print("-" * 85)

    for r in ps["results"]:
        score_color = RED if r["performance_rating"] == "Poor" else YELLOW if r["performance_rating"] == "Needs Improvement" else GREEN
        lcp_color = RED if r["lcp_rating"] == "Poor" else YELLOW if r["lcp_rating"] == "Needs Improvement" else GREEN
        cls_color = RED if r["cls_rating"] == "Poor" else YELLOW if r["cls_rating"] == "Needs Improvement" else GREEN
        url_short = r["url"][:38]
        print(
            f"  {url_short:<38} "
            f"{score_color}{r['performance_score']:.2f}{RESET:>6} "
            f"{lcp_color}{r['lcp_ms']:>8.0f}{RESET} "
            f"{lcp_color}{r['lcp_rating']:>9}{RESET} "
            f"{cls_color}{r['cls']:>6.2f}{RESET} "
            f"{cls_color}{r['cls_rating']:>9}{RESET}"
        )


def demo_content_brief():
    section("Phase 3 — Content Brief Generation")
    url = "/skincare/collagen-serum-guide"
    query = "콜라겐 세럼 추천"

    print(f"URL: {url}")
    print(f"타겟 쿼리: {query}\n")

    brief = generate_content_brief(url=url, target_query=query, current_position=5.2)

    print(f"브리프 ID: {brief['brief_id']}")
    print(f"검색 의도: {brief['search_intent']}")
    print(f"\n현재 지표:")
    m = brief["current_metrics"]
    print(f"  포지션: {m['position']} | 노출: {m['impressions']:,} | CTR: {m['current_ctr']*100:.2f}%")

    print(f"\n{BOLD}제목 태그 옵션:{RESET}")
    for i, t in enumerate(brief["title_options"], 1):
        print(f"  {i}. {t}")

    print(f"\n{BOLD}메타 설명 옵션:{RESET}")
    for i, m in enumerate(brief["meta_description_options"], 1):
        print(f"  {i}. {m}")

    print(f"\n{BOLD}추천 콘텐츠 섹션:{RESET}")
    for s in brief["recommended_sections"]:
        print(f"  • {s}")

    print(f"\n{BOLD}내부 링크 제안:{RESET}")
    for link in brief["internal_link_suggestions"]:
        print(f"  → {link['url']} ({link['anchor_text']})")

    print(f"\n{BOLD}구조화 데이터:{RESET}")
    for sd in brief["structured_data_recommendations"]:
        print(f"  • {sd}")


def demo_top_recommendations():
    section("Phase 3 — Prioritized SEO Recommendations (Impact/Effort Ranked)")
    recs = get_seo_recommendations(priority="all", limit=10)

    print(f"전체 권고사항: {recs['total_recommendations']}건 | 상위 {len(recs['recommendations'])}건 표시\n")
    print(f"{'#':<3} {'RuleID':<10} {'Priority':<10} {'Type':<22} {'I':>2} {'E':>2} {'P-Score':>8}  URL")
    print("-" * 90)

    for i, r in enumerate(recs["recommendations"], 1):
        color = priority_color(r["priority"])
        print(
            f"  {i:<2} {r['rule_id']:<10} {color}{r['priority']:<10}{RESET} "
            f"{r['opportunity_type']:<22} {r['impact_score']:>2} {r['effort_score']:>2} "
            f"{r['priority_score']:>8.2f}  {r['target_url']}"
        )


def demo_seo_agent(run_llm: bool = False):
    """Optional: run the full SEO agent with LLM (requires API key)."""
    if not run_llm:
        section("Phase 3 — SEO Agent (LLM Demo — skipped)")
        print("LLM 데모를 실행하려면 --llm 플래그를 사용하세요.")
        print("예: python run_seo_demo.py --llm")
        return

    section("Phase 3 — SEO Agent (Full LLM Interaction)")
    print("SEO 에이전트 초기화 중...\n")

    from agents.seo_agent import SEOAgent
    agent = SEOAgent(verbose=True)

    print(f"\n{BOLD}[쿼리 기회 보고서]{RESET}")
    result = agent.query_opportunity_report()
    print("\n" + result[:2000] + ("..." if len(result) > 2000 else ""))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    run_llm = "--llm" in sys.argv

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Phase 3 SEO Agent Demo — 뷰티랩 BeautyLab{RESET}")
    print(f"{BOLD}  한국 뷰티 이커머스 SEO 진단{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    demo_rule_engine()
    demo_site_overview()
    demo_query_opportunities()
    demo_technical_audit()
    demo_pagespeed()
    demo_content_brief()
    demo_top_recommendations()
    demo_seo_agent(run_llm=run_llm)

    section("Demo Complete")
    print("Phase 3 SEO Agent 구현 완료:")
    print("  ✓ rules/seo_rules.py          — 6개 SEO 규칙 엔진")
    print("  ✓ workflows/seo_diagnosis.py   — SEO 진단 워크플로우 (규칙 + LLM)")
    print("  ✓ agents/seo_agent.py          — SEO 오케스트레이터 에이전트")
    print("  ✓ tools/definitions.py         — 7개 SEO 도구 정의 추가")
    print("  ✓ tools/handlers.py            — SEO 도구 핸들러 구현")
    print("  ✓ data/seo_mock_data.py        — GSC/GA4/PageSpeed/크롤 모의 데이터")
    print("  ✓ run_seo_demo.py              — 전체 데모 스크립트")
    print(f"\n  총 SEO 탐지 이슈: {len(run_all_seo_rules())}건")
    print("\n  실행: python run_seo_demo.py")
    print("  LLM 포함: python run_seo_demo.py --llm")


if __name__ == "__main__":
    main()
