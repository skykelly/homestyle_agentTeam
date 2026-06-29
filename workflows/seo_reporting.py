"""
SEO Weekly Report Workflow — Phase 6.
Generates structured Markdown weekly SEO reports.
Covers: organic summary, opportunity matrix, technical issues, content brief queue,
        approval queue, experiment results, knowledge items, next week priorities.
"""

from datetime import datetime, timedelta
from pathlib import Path

from data.seo_mock_data import SITE_BENCHMARKS, DECLINING_QUERIES
from models.agent_run import AgentRun
from rules.seo_rules import run_all_seo_rules
from storage.repository import save_agent_run, list_recommendations
from storage.seo_repository import (
    list_content_briefs, list_schema_recommendations,
    list_link_recommendations, list_experiments, list_knowledge_items,
    get_seo_store_summary,
)
from workflows.base import BaseWorkflow

REPORTS_DIR = Path(__file__).parent.parent / "data" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class SEOReportingWorkflow(BaseWorkflow):
    """
    Generates weekly SEO reports in Markdown format.
    Aggregates all Phase 3-6 outputs into an executive-ready report.
    """

    system_prompt = """You are an SEO Reporting Specialist for Korean beauty e-commerce.

Generate clear, executive-ready weekly SEO reports that:
- Lead with business impact (clicks, revenue, conversions) not vanity metrics
- Distinguish wins from losses clearly
- Prioritize actionable items for next week
- Include a one-line executive summary at the top
- Use ▲/▼ symbols to show trends clearly
- Quantify everything possible ("월 +2,180 클릭 기회" not "클릭 기회 있음")

Report audience: SEO 담당자, 마케팅 리더, 이커머스 운영팀
Language: 한국어 (Korean)"""

    allowed_tools = [
        "get_seo_overview",
        "get_seo_recommendations",
        "get_technical_audit",
    ]

    def generate_weekly_report(
        self,
        report_date: str | None = None,
        export_markdown: bool = True,
        llm_augment: bool = True,
    ) -> dict:
        """
        Generate a complete weekly SEO report.

        Args:
            report_date: Report date (YYYY-MM-DD). Defaults to today.
            export_markdown: Whether to save .md file to data/reports/
            llm_augment: Whether to use LLM for executive summary and insights
        """
        if report_date is None:
            report_date = datetime.now().strftime("%Y-%m-%d")

        run = AgentRun(
            workflow_name="seo_reporting",
            trigger="manual",
            input_params={"report_date": report_date, "export_markdown": export_markdown},
        )
        save_agent_run(run)

        # ── Collect all data ──────────────────────────────────────────────
        benchmarks = SITE_BENCHMARKS
        p = benchmarks["period_28d"]
        prev = benchmarks["period_prev_28d"]

        def delta(cur, old): return round((cur - old) / old * 100, 1) if old else 0
        def trend(pct): return "▲" if pct > 0 else "▼"

        all_hits = run_all_seo_rules()
        priority_counts = {}
        for h in all_hits:
            priority_counts[h.priority] = priority_counts.get(h.priority, 0) + 1

        by_type = {}
        for h in all_hits:
            by_type.setdefault(h.opportunity_type, []).append(h)

        store = get_seo_store_summary()
        experiments = list_experiments()
        knowledge_items = list_knowledge_items()
        content_briefs = list_content_briefs()
        schema_recs = list_schema_recommendations()
        link_recs = list_link_recommendations()

        # ── Build Markdown report ─────────────────────────────────────────
        click_delta = delta(p["total_clicks"], prev["total_clicks"])
        rev_delta = delta(p["organic_revenue_krw"], prev["organic_revenue_krw"])
        pos_delta = round(p["avg_position"] - prev["avg_position"], 1)

        md = []
        md.append(f"# 뷰티랩 SEO 주간 리포트")
        md.append(f"**리포트 날짜:** {report_date}  |  **분석 기간:** 최근 28일  |  **생성:** SEO Agent One\n")
        md.append("---\n")

        # Executive summary placeholder — will be filled by LLM
        md.append("## 📌 Executive Summary\n")
        md.append("> *(아래 LLM 섹션에서 생성)*\n")

        # 1. Organic Search Summary
        md.append("## 1. Organic Search 요약\n")
        md.append("| 지표 | 현재 (28일) | 전기 (28일) | 변화 |")
        md.append("|------|------------|------------|------|")
        md.append(f"| 총 클릭 | {p['total_clicks']:,} | {prev['total_clicks']:,} | {trend(click_delta)} {abs(click_delta):.1f}% |")
        md.append(f"| 총 노출 | {p['total_impressions']:,} | {prev['total_impressions']:,} | {trend(delta(p['total_impressions'], prev['total_impressions']))} {abs(delta(p['total_impressions'], prev['total_impressions'])):.1f}% |")
        md.append(f"| 평균 CTR | {p['avg_ctr']*100:.1f}% | {prev['avg_ctr']*100:.1f}% | {trend(-abs(delta(p['avg_ctr'], prev['avg_ctr'])))} |")
        md.append(f"| 평균 포지션 | {p['avg_position']} | {prev['avg_position']} | {'▼' if pos_delta > 0 else '▲'} {abs(pos_delta):.1f} |")
        md.append(f"| 오가닉 매출 | {p['organic_revenue_krw']:,}원 | {prev['organic_revenue_krw']:,}원 | {trend(rev_delta)} {abs(rev_delta):.1f}% |")
        md.append("")

        health = "⚠️ 주의" if click_delta < -10 else "✅ 안정" if click_delta > 0 else "📊 모니터링"
        md.append(f"**사이트 헬스:** {health} — 클릭 {click_delta:+.1f}%, 매출 {rev_delta:+.1f}%\n")

        # 2. Key Rising/Declining Queries
        md.append("## 2. 주요 하락 쿼리 (콘텐츠 노후화)\n")
        md.append("| URL | 클릭 (현재) | 클릭 (전기) | 하락률 | 마지막 업데이트 |")
        md.append("|-----|------------|------------|--------|----------------|")
        for url, d in DECLINING_QUERIES.items():
            drop = round((1 - d["clicks_28d"] / d["clicks_prev_28d"]) * 100, 1)
            md.append(f"| `{url}` | {d['clicks_28d']:,} | {d['clicks_prev_28d']:,} | ▼{drop}% | {d['last_updated_days']}일 전 |")
        md.append("")

        # 3. Opportunity Matrix
        md.append("## 3. 신규 발견 기회\n")
        md.append(f"**총 탐지 이슈:** {len(all_hits)}건\n")
        md.append("| 유형 | 건수 | 대표 예시 |")
        md.append("|------|------|-----------|")
        type_labels = {
            "cannibalization_fix": "카니발라이제이션",
            "ctr_improvement": "Low CTR 개선",
            "ranking_boost": "Page 2→1 기회",
            "content_refresh": "콘텐츠 리프레시",
            "technical_fix": "기술적 이슈",
            "geo_candidate": "GEO/AI 검색 후보",
        }
        for opp_type, hits in by_type.items():
            label = type_labels.get(opp_type, opp_type)
            example = hits[0].target_url if hits else "-"
            md.append(f"| {label} | {len(hits)} | `{example}` |")
        md.append("")

        # 4. Priority Breakdown
        md.append("### 우선순위 분포\n")
        md.append("| 우선순위 | 건수 |")
        md.append("|----------|------|")
        for p_key in ["critical", "high", "medium", "low"]:
            count = priority_counts.get(p_key, 0)
            emoji = {"critical": "🔴", "high": "🟡", "medium": "🔵", "low": "🟢"}.get(p_key, "")
            md.append(f"| {emoji} {p_key.upper()} | {count} |")
        md.append("")

        # 5. Technical SEO Issues
        md.append("## 4. 기술 SEO 주요 이슈\n")
        tech_hits = [h for h in all_hits if h.opportunity_type == "technical_fix"]
        if tech_hits:
            md.append("| Rule ID | 우선순위 | URL | 이슈 |")
            md.append("|---------|----------|-----|------|")
            for h in tech_hits[:8]:
                md.append(f"| {h.rule_id} | {h.priority.upper()} | `{h.target_url}` | {h.description[:60]} |")
        else:
            md.append("_기술적 이슈 없음_")
        md.append("")

        # 6. Content Brief Queue
        md.append("## 5. Content Brief 현황\n")
        md.append(f"**생성된 브리프:** {store['content_briefs']}개  |  **승인 대기:** {sum(1 for b in content_briefs if b.get('status') == 'draft')}개\n")
        if content_briefs:
            md.append("| Brief ID | URL | 쿼리 클러스터 | 상태 |")
            md.append("|----------|-----|--------------|------|")
            for b in content_briefs[:5]:
                md.append(f"| `{b['brief_id']}` | `{b['target_url']}` | {b['primary_query_cluster']} | {b['status']} |")
        md.append("")

        # 7. Structured Data Queue
        md.append("## 6. 구조화 데이터 권고\n")
        md.append(f"**생성된 권고:** {store['schema_recommendations']}개\n")
        if schema_recs:
            md.append("| URL | 스키마 타입 | 임팩트 | Rich Result |")
            md.append("|-----|------------|--------|-------------|")
            for r in schema_recs[:5]:
                md.append(f"| `{r['target_url']}` | {r['schema_type']} | {r['impact_score']}/5 | {'✅' if r['rich_result_eligible'] else '—'} |")
        md.append("")

        # 8. Internal Link Recommendations
        md.append("## 7. 내부 링크 권고\n")
        md.append(f"**생성된 권고:** {store['internal_link_recommendations']}개\n")
        high_links = [r for r in link_recs if r.get("priority") == "high"][:5]
        if high_links:
            md.append("| 유형 | Source | Target | Anchor Text |")
            md.append("|------|--------|--------|-------------|")
            for r in high_links:
                md.append(f"| {r['link_type']} | `{r['source_url']}` | `{r['target_url']}` | {r['anchor_text']} |")
        md.append("")

        # 9. Experiments
        md.append("## 8. 실험 현황\n")
        md.append(f"**진행 중인 실험:** {len(experiments)}개\n")
        completed = [e for e in experiments if e.get("status") == "completed"]
        if completed:
            md.append("| 실험 ID | URL | 변경 유형 | 결과 |")
            md.append("|---------|-----|----------|------|")
            for e in completed[:5]:
                outcome_emoji = {"success": "✅", "neutral": "⚖️", "regression": "❌"}.get(e.get("outcome", ""), "—")
                md.append(f"| `{e['experiment_id']}` | `{e['target_url']}` | {e['change_type']} | {outcome_emoji} {e.get('outcome', '-')} |")
        else:
            md.append("_진행 중인 실험 없음. 승인된 권고사항을 실험으로 등록하세요._")
        md.append("")

        # 10. Knowledge Items
        md.append("## 9. 지식 베이스 현황\n")
        md.append(f"**축적된 Knowledge Items:** {store['knowledge_items']}개\n")
        if knowledge_items:
            for item in knowledge_items[:3]:
                md.append(f"- **{item['title']}**: {item['summary']}")
        md.append("")

        # 11. Next Week Priorities
        md.append("## 10. 다음 주 우선순위\n")
        priorities = []

        # Critical issues first
        crit_hits = [h for h in all_hits if h.priority == "critical"][:2]
        for h in crit_hits:
            priorities.append(f"🔴 **[즉시]** {h.description} → {h.recommendation}")

        # High-impact low-effort
        quick_wins = sorted(
            [h for h in all_hits if h.priority == "high"],
            key=lambda h: h.impact_score / max(h.effort_score, 1),
            reverse=True,
        )[:3]
        for h in quick_wins:
            priorities.append(f"🟡 **[이번 주]** {h.description} (임팩트: {h.expected_impact})")

        # Content briefs pending
        if content_briefs:
            priorities.append(f"📝 **[콘텐츠팀]** 콘텐츠 브리프 {len(content_briefs)}개 검토 및 집필 착수")

        # Schema implementations
        if schema_recs:
            top_schema = max(schema_recs, key=lambda r: r["impact_score"])
            priorities.append(f"⚙️ **[개발팀]** {top_schema['target_url']} — {top_schema['schema_type']} 스키마 구현 (임팩트 {top_schema['impact_score']}/5)")

        for i, p_item in enumerate(priorities, 1):
            md.append(f"{i}. {p_item}")
        md.append("")

        # Footer
        md.append("---")
        md.append(f"*리포트 생성: SEO Agent One | {datetime.now().strftime('%Y-%m-%d %H:%M')} | 뷰티랩 BeautyLab*")

        markdown_content = "\n".join(md)

        # ── LLM: Executive Summary ────────────────────────────────────────
        exec_summary = ""
        if llm_augment:
            prompt = f"""다음 SEO 주간 리포트 데이터를 분석하여 경영진 요약을 작성해주세요.

핵심 수치:
  - 클릭: {p['total_clicks']:,}회 ({click_delta:+.1f}% vs 전기)
  - 오가닉 매출: {p['organic_revenue_krw']:,}원 ({rev_delta:+.1f}%)
  - 탐지된 SEO 이슈: {len(all_hits)}건 (CRITICAL {priority_counts.get('critical', 0)}건, HIGH {priority_counts.get('high', 0)}건)
  - 생성된 콘텐츠 브리프: {store['content_briefs']}개
  - 구조화 데이터 권고: {store['schema_recommendations']}개
  - 내부 링크 권고: {store['internal_link_recommendations']}개

경영진 요약 형식:
- 3-4문장으로 이번 주 핵심 SEO 현황 요약
- 가장 중요한 액션 1가지 강조
- 예상 비즈니스 임팩트 수치 포함
- 한 줄 요약 (TL;DR) 맨 앞에 배치

한국어로 작성하세요."""
            exec_summary = self.run(prompt, max_iterations=2)

            # Insert exec summary into report
            markdown_content = markdown_content.replace(
                "> *(아래 LLM 섹션에서 생성)*",
                exec_summary,
            )

        # Save Markdown file
        report_filename = ""
        if export_markdown:
            report_filename = f"seo_report_{report_date}.md"
            report_path = REPORTS_DIR / report_filename
            report_path.write_text(markdown_content, encoding="utf-8")
            self._log(f"\n[Report] Saved to: {report_path}")

        run.complete(output_summary=f"SEO 주간 리포트 생성 완료 ({report_date})")
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "report_date": report_date,
            "report_file": report_filename,
            "markdown": markdown_content,
            "executive_summary": exec_summary,
            "stats": {
                "total_issues": len(all_hits),
                "priority_breakdown": priority_counts,
                "content_briefs": store["content_briefs"],
                "schema_recommendations": store["schema_recommendations"],
                "internal_link_recommendations": store["internal_link_recommendations"],
                "experiments": store["experiments"],
                "knowledge_items": store["knowledge_items"],
            },
        }
