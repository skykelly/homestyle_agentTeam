"""
SEO Diagnosis Workflow — Phase 3.
Two-stage pipeline:
  Stage 1: SEO rule engine (6 rules, no LLM)
  Stage 2: LLM layer for content briefs and strategic insights

Design doc principle: "Rule-based baseline 먼저, LLM은 추가 계층"
"""

from datetime import datetime

from data.seo_mock_data import SITE_BENCHMARKS
from models.agent_run import AgentRun
from rules.seo_rules import SEORuleResult, run_all_seo_rules
from storage.repository import save_agent_run
from workflows.base import BaseWorkflow


class SEODiagnosisWorkflow(BaseWorkflow):
    """
    Diagnose SEO health using rule engine first, then LLM insights.
    Produces a structured report with prioritized opportunities.
    """

    system_prompt = """You are an SEO Marketing AI Agent specialized in Korean beauty e-commerce.

Your job is to analyze SEO data from Google Search Console, GA4, PageSpeed Insights, and site crawls,
then provide specific, actionable recommendations ranked by impact/effort ratio.

When analyzing:
- Always ground insights in the data provided (impressions, clicks, CTR, positions)
- Prioritize: Cannibalization > Low CTR (high impressions) > Page 2 opportunities > Technical fixes
- For Korean beauty market, note seasonal patterns and Naver/Google dual-search behavior
- Provide concrete next steps (specific title tags, meta descriptions, schema types)
- Quantify expected impact in clicks or revenue where possible

Respond in Korean. Be concise and actionable — no generic SEO advice."""

    allowed_tools = [
        "get_seo_overview",
        "get_seo_query_opportunities",
        "get_technical_audit",
        "get_pagespeed_summary",
    ]

    def diagnose(
        self,
        site_url: str = "https://beautylab.co.kr",
        min_impressions: int = 3000,
        llm_augment: bool = True,
        max_results: int = 20,
    ) -> dict:
        """
        Run full SEO diagnosis.

        Args:
            site_url: Target site URL
            min_impressions: Minimum impressions threshold for query analysis
            llm_augment: Whether to run LLM strategic analysis on top of rule hits
            max_results: Maximum number of rule results to return
        """
        run = AgentRun(
            workflow_name="seo_diagnosis",
            trigger="manual",
            input_params={
                "site_url": site_url,
                "min_impressions": min_impressions,
                "llm_augment": llm_augment,
            },
        )
        save_agent_run(run)

        benchmarks = SITE_BENCHMARKS
        period = benchmarks["period_28d"]
        prev_period = benchmarks["period_prev_28d"]

        # ── Stage 1: Rule engine ─────────────────────────────────────────────
        all_hits = run_all_seo_rules(min_impressions=min_impressions)
        top_hits = all_hits[:max_results]

        self._log(f"\n[SEO Diagnosis] Rule engine: {len(all_hits)} issue(s) found for {site_url}")

        # Group by opportunity type
        by_type: dict[str, list[SEORuleResult]] = {}
        for hit in top_hits:
            by_type.setdefault(hit.opportunity_type, []).append(hit)

        # Priority summary
        priority_counts = {}
        for hit in all_hits:
            priority_counts[hit.priority] = priority_counts.get(hit.priority, 0) + 1

        for hit in top_hits:
            self._log(f"  [{hit.rule_id}] {hit.description[:80]} | priority={hit.priority}")

        # ── Stage 1b: Site performance delta ────────────────────────────────
        click_delta = period["total_clicks"] - prev_period["total_clicks"]
        click_delta_pct = round(click_delta / prev_period["total_clicks"] * 100, 1)
        revenue_delta = period["organic_revenue_krw"] - prev_period["organic_revenue_krw"]
        revenue_delta_pct = round(revenue_delta / prev_period["organic_revenue_krw"] * 100, 1)

        site_health = {
            "site_url": site_url,
            "period": "최근 28일",
            "total_clicks": period["total_clicks"],
            "total_clicks_prev": prev_period["total_clicks"],
            "click_delta": click_delta,
            "click_delta_pct": click_delta_pct,
            "avg_position": period["avg_position"],
            "avg_position_prev": prev_period["avg_position"],
            "avg_ctr": period["avg_ctr"],
            "organic_revenue_krw": period["organic_revenue_krw"],
            "revenue_delta_pct": revenue_delta_pct,
            "health_status": _assess_health(click_delta_pct, revenue_delta_pct),
        }

        # ── Stage 2: LLM strategic insights ─────────────────────────────────
        llm_insights = ""
        content_briefs = []

        if llm_augment and top_hits:
            # Build a concise summary for LLM
            hits_summary = "\n".join(
                f"  [{h.rule_id}] [{h.priority.upper()}] {h.description}\n"
                f"    URL: {h.target_url} | 예상 임팩트: {h.expected_impact}"
                for h in top_hits[:10]
            )

            prompt = f"""다음 SEO 진단 결과를 분석하고 전략적 인사이트를 제공해주세요.

사이트: {site_url} ({benchmarks['site_name']})
카테고리: {benchmarks['category']}

사이트 현황 (28일):
  - 총 클릭: {period['total_clicks']:,}회 (전기 대비 {click_delta_pct:+.1f}%)
  - 평균 포지션: {period['avg_position']} → {period['avg_position']} (전기: {prev_period['avg_position']})
  - 평균 CTR: {period['avg_ctr']*100:.1f}%
  - 오가닉 매출: {period['organic_revenue_krw']:,}원 ({revenue_delta_pct:+.1f}%)

탐지된 SEO 이슈 ({len(all_hits)}건, 상위 {len(top_hits[:10])}건 표시):
{hits_summary}

이슈 우선순위 분포:
{chr(10).join(f"  - {p}: {c}건" for p, c in sorted(priority_counts.items()))}

요청사항:
1. 가장 높은 ROI 액션 3가지 (즉시 실행 가능, 구체적 지시사항 포함)
2. 카니발라이제이션 해결 전략 (해당하는 경우)
3. CTR 개선을 위한 제목/메타 설명 예시 (최소 2개 URL)
4. 한국 뷰티 카테고리 특화 SEO 전략 포인트"""

            run.add_tool_call("llm_seo_diagnosis", prompt[:120], "")
            llm_insights = self.run(prompt, max_iterations=3)

            # Generate content briefs for top CTR opportunity pages
            ctr_hits = by_type.get("ctr_improvement", [])[:2]
            for hit in ctr_hits:
                brief = _generate_content_brief(hit)
                content_briefs.append(brief)

        # ── Finalize ─────────────────────────────────────────────────────────
        run.complete(output_summary=f"SEO 진단 완료: {len(all_hits)}건 이슈 탐지, {len(content_briefs)}개 콘텐츠 브리프 생성")
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "diagnosed_at": datetime.now().isoformat(),
            "site_health": site_health,
            "summary": {
                "total_issues": len(all_hits),
                "priority_breakdown": priority_counts,
                "by_opportunity_type": {k: len(v) for k, v in by_type.items()},
                "issues_analyzed": len(top_hits),
            },
            "top_opportunities": [_rule_result_to_dict(h) for h in top_hits],
            "by_type": {k: [_rule_result_to_dict(h) for h in v] for k, v in by_type.items()},
            "content_briefs": content_briefs,
            "llm_insights": llm_insights,
        }


def _assess_health(click_delta_pct: float, revenue_delta_pct: float) -> str:
    if click_delta_pct < -20 or revenue_delta_pct < -20:
        return "critical"
    if click_delta_pct < -10 or revenue_delta_pct < -10:
        return "warning"
    if click_delta_pct >= 5 and revenue_delta_pct >= 5:
        return "healthy"
    return "stable"


def _rule_result_to_dict(r: SEORuleResult) -> dict:
    return {
        "rule_id": r.rule_id,
        "rule_name": r.rule_name,
        "priority": r.priority,
        "opportunity_type": r.opportunity_type,
        "target_url": r.target_url,
        "target_queries": r.target_queries,
        "description": r.description,
        "problem": r.problem,
        "recommendation": r.recommendation,
        "expected_impact": r.expected_impact,
        "evidence": r.evidence,
        "current_metric": r.current_metric,
        "scores": {
            "effort": r.effort_score,
            "impact": r.impact_score,
            "confidence": r.confidence_score,
            "priority_score": round(r.impact_score / max(r.effort_score, 1) * r.confidence_score, 2),
        },
        "required_approval": r.required_approval,
    }


def _generate_content_brief(hit: SEORuleResult) -> dict:
    """Generate a structured content brief for a CTR improvement opportunity."""
    query = hit.target_queries[0] if hit.target_queries else ""
    url = hit.target_url
    position = hit.current_metric.get("position", 0)
    impressions = hit.current_metric.get("impressions", 0)
    current_ctr = hit.current_metric.get("ctr", 0)
    expected_ctr = hit.current_metric.get("expected_ctr", 0)

    return {
        "brief_id": f"BRIEF_{url.replace('/', '_').strip('_').upper()[:20]}",
        "target_url": url,
        "primary_query": query,
        "current_position": position,
        "current_ctr": current_ctr,
        "target_ctr": expected_ctr,
        "title_options": [
            f"{query} — 전문가 추천 가이드 2024",
            f"[뷰티랩] {query}: 효과·성분·사용법 완벽 정리",
            f"{query} 베스트 선택법 | 뷰티랩 전문가 분석",
        ],
        "meta_description_options": [
            f"{query}에 대한 모든 것. 성분 분석, 사용 순서, 피부 타입별 추천까지. 뷰티랩 전문가가 직접 테스트한 리얼 리뷰.",
            f"포지션 {position:.0f}에서 본 {query} 총정리. 효과·부작용·성분 비교를 한 번에 확인하세요.",
        ],
        "search_intent": "informational",
        "recommended_sections": [
            f"{query} 이란? (정의 및 핵심 특징)",
            "성분 분석 및 작용 메커니즘",
            "피부 타입별 사용 권장사항",
            "자주 묻는 질문 (FAQ — FAQPage 스키마 적용)",
            "뷰티랩 추천 제품 라인업 (제품 링크 포함)",
        ],
        "internal_link_suggestions": [
            "/product/collagen-serum-50ml",
            "/skincare/routine-guide",
            "/ingredients/niacinamide",
        ],
        "structured_data": "Article + FAQPage JSON-LD",
        "priority": hit.priority,
        "estimated_monthly_click_gain": hit.expected_impact,
    }
