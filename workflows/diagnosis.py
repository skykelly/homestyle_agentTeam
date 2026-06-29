"""
Performance Diagnosis Workflow — Phase 2.
Two-stage pipeline:
  Stage 1: Rule engine fires deterministically (no LLM, instant, auditable)
  Stage 2: LLM layer adds context-aware insights on top of rule hits

This follows the design doc principle: "Rule-based baseline 먼저, LLM은 추가 계층"
"""

from datetime import datetime

from models.recommendation import (
    Recommendation, RecommendationType, RiskLevel, ApprovalRequired
)
from models.agent_run import AgentRun
from rules.budget_rules import run_all_budget_rules
from rules.creative_rules import run_all_creative_rules
from rules.landing_rules import run_all_landing_rules
from storage.repository import save_recommendation, save_agent_run
from workflows.approval import ApprovalWorkflow
from workflows.base import BaseWorkflow
from data.korean_market import PLATFORM_BENCHMARKS, CATEGORY_KPIS


class DiagnosisWorkflow(BaseWorkflow):
    """
    Diagnose campaign performance issues using rules first, LLM second.
    Generates structured Recommendations with full approval lifecycle support.
    """

    system_prompt = """당신은 한국 퍼포먼스 마케팅 진단 전문가입니다.
규칙 엔진이 탐지한 성과 이슈를 분석하고, 추가적인 컨텍스트 기반 인사이트를 제공합니다.
데이터에 근거한 구체적인 개선 방안과 우선순위를 제시하세요.
응답은 간결하고 즉시 실행 가능한 형태로 작성하세요."""

    allowed_tools = [
        "get_campaign_performance",
        "get_keyword_analysis",
        "get_market_events",
    ]

    def __init__(self, verbose: bool = True):
        super().__init__(verbose=verbose)
        self.approval_wf = ApprovalWorkflow()

    def diagnose(
        self,
        platform: str,
        campaign: str,
        category: str,
        metrics: dict,
        auto_submit: bool = True,
        llm_augment: bool = True,
    ) -> dict:
        """
        Run full diagnosis pipeline.

        Args:
            platform: Ad platform key (e.g. "naver_search")
            campaign: Campaign name or ID
            category: Product category (e.g. "뷰티")
            metrics: Performance data dict with keys:
                roas (float), cpa_krw (int), ctr_pct (float), cvr_pct (float),
                spend_krw (int), budget_utilization (float 0-1), days_running (int),
                frequency (float, optional), bounce_rate_pct (float, optional),
                page_load_seconds (float, optional), cart_abandon_rate_pct (float, optional),
                sessions (int, optional)
            auto_submit: If True, submit recommendations through approval workflow immediately
            llm_augment: If True, run LLM analysis on top of rule hits
        """
        run = AgentRun(
            workflow_name="diagnosis",
            trigger="manual",
            input_params={
                "platform": platform,
                "campaign": campaign,
                "category": category,
                "metrics_keys": list(metrics.keys()),
            },
        )
        save_agent_run(run)

        bench = PLATFORM_BENCHMARKS.get(platform, {})
        kpis = CATEGORY_KPIS.get(category, CATEGORY_KPIS.get("패션", {}))

        # ── Stage 1: Rule engine (no LLM) ──────────────────────────────────
        rule_hits = []

        rule_hits += run_all_budget_rules(
            platform=platform,
            campaign=campaign,
            current_roas=metrics.get("roas", 0),
            target_roas=kpis.get("target_roas", 300),
            current_cpa_krw=metrics.get("cpa_krw", 0),
            target_cpa_krw=kpis.get("target_cpa_krw", 20000),
            budget_utilization=metrics.get("budget_utilization", 0.95),
            days_running=metrics.get("days_running", 7),
        )

        rule_hits += run_all_creative_rules(
            platform=platform,
            campaign=campaign,
            creative_id=f"{campaign}_creative",
            current_ctr_pct=metrics.get("ctr_pct", 0),
            benchmark_ctr_pct=bench.get("avg_ctr_pct", 1.5),
            current_cvr_pct=metrics.get("cvr_pct", 0),
            benchmark_cvr_pct=bench.get("avg_cvr_pct", 2.0),
            days_running=metrics.get("days_running", 7),
            frequency=metrics.get("frequency", 0),
        )

        if metrics.get("bounce_rate_pct") or metrics.get("page_load_seconds") or metrics.get("cart_abandon_rate_pct"):
            rule_hits += run_all_landing_rules(
                page_url=f"https://example.com/{campaign}",
                campaign=campaign,
                bounce_rate_pct=metrics.get("bounce_rate_pct", 0),
                sessions=metrics.get("sessions", 0),
                avg_load_seconds=metrics.get("page_load_seconds", 0),
                cart_abandon_rate_pct=metrics.get("cart_abandon_rate_pct", 0),
            )

        self._log(f"\n[Diagnosis] Rule engine: {len(rule_hits)} issue(s) detected on {platform}/{campaign}")

        # Convert RuleResults → Recommendation objects
        recommendations = []
        for rr in rule_hits:
            rec = Recommendation(
                recommendation_type=RecommendationType(rr.recommendation_type),
                target_platform=platform,
                target_campaign=campaign,
                current_metric={
                    "roas": metrics.get("roas"),
                    "cpa_krw": metrics.get("cpa_krw"),
                    "ctr_pct": metrics.get("ctr_pct"),
                    "cvr_pct": metrics.get("cvr_pct"),
                    "budget_utilization": metrics.get("budget_utilization"),
                },
                expected_impact={
                    "change_pct": rr.change_pct,
                    "rule_id": rr.rule_id,
                    "description": rr.description,
                },
                confidence_score=rr.confidence,
                risk_level=RiskLevel(rr.risk_level),
                reason=rr.reason,
                evidence=rr.evidence,
                required_approval=ApprovalRequired(rr.required_approval),
                rollback_plan=rr.rollback_plan,
            )
            save_recommendation(rec)
            recommendations.append(rec)
            run.recommendations_generated.append(rec.id)
            self._log(f"  [{rr.rule_id}] {rr.description} → risk={rr.risk_level}, approval={rr.required_approval}")

        # ── Stage 1b: Approval routing ──────────────────────────────────────
        approval_results = []
        if auto_submit:
            for rec in recommendations:
                result = self.approval_wf.submit_for_approval(rec)
                approval_results.append(result)
                self._log(f"  Approval: {rec.id} → {result['status']}")

        # ── Stage 2: LLM augmentation (only when rules found issues) ────────
        llm_insights = ""
        if llm_augment and rule_hits:
            triggered_summary = "\n".join(
                f"  - [{rr.rule_id}] {rr.description}: {rr.reason}"
                for rr in rule_hits
            )
            prompt = f"""다음 규칙 엔진 탐지 결과를 분석하고 추가 인사이트를 제공해주세요.

플랫폼: {platform} | 캠페인: {campaign} | 카테고리: {category}

현재 지표:
{_format_metrics_text(metrics, kpis, bench)}

규칙 엔진 탐지 이슈 ({len(rule_hits)}건):
{triggered_summary}

분석 요청:
1. 근본 원인 (2-3줄, 이슈 간 연관성 포함)
2. 우선순위별 액션 플랜 (최대 5개, 즉시 실행 가능)
3. 한국 시장 특수 고려사항 (시즌, 플랫폼 특성)"""

            run.add_tool_call("llm_diagnosis", prompt[:120], "")
            llm_insights = self.run(prompt, max_iterations=3)

        # ── Finalize run ────────────────────────────────────────────────────
        run.complete(output_summary=f"{len(recommendations)}개 권고사항 생성 (규칙 {len(rule_hits)}건 탐지)")
        save_agent_run(run)

        needs_action = [r for r in approval_results if r.get("status") == "pending_approval"]
        auto_approved = [r for r in approval_results if r.get("status") == "auto_approved"]

        return {
            "run_id": run.run_id,
            "platform": platform,
            "campaign": campaign,
            "category": category,
            "diagnosed_at": datetime.now().isoformat(),
            "summary": {
                "rule_hits": len(rule_hits),
                "recommendations_generated": len(recommendations),
                "auto_approved": len(auto_approved),
                "pending_human_approval": len(needs_action),
            },
            "recommendations": [r.to_dict() for r in recommendations],
            "approval_results": approval_results,
            "pending_approval_ids": [r["recommendation_id"] for r in needs_action],
            "llm_insights": llm_insights,
        }


def _format_metrics_text(metrics: dict, kpis: dict, bench: dict) -> str:
    lines = [
        f"  ROAS: {metrics.get('roas', 'N/A')}% (목표: {kpis.get('target_roas', 'N/A')}%)",
        f"  CPA: {metrics.get('cpa_krw', 0):,}원 (목표: {kpis.get('target_cpa_krw', 0):,}원)",
        f"  CTR: {metrics.get('ctr_pct', 'N/A')}% (벤치마크: {bench.get('avg_ctr_pct', 'N/A')}%)",
        f"  CVR: {metrics.get('cvr_pct', 'N/A')}% (벤치마크: {bench.get('avg_cvr_pct', 'N/A')}%)",
        f"  예산 소진율: {metrics.get('budget_utilization', 'N/A')}",
        f"  운영 일수: {metrics.get('days_running', 'N/A')}일",
    ]
    if metrics.get("bounce_rate_pct"):
        lines.append(f"  이탈률: {metrics['bounce_rate_pct']}%")
    if metrics.get("page_load_seconds"):
        lines.append(f"  페이지 로딩: {metrics['page_load_seconds']}초")
    return "\n".join(lines)
