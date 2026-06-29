"""
SEO Recommendation Approval Workflow.
Converts rule-engine hits into structured Recommendations,
then manages the pending_approval → approved | rejected lifecycle.
"""

from datetime import datetime

from models.agent_run import AgentRun
from models.seo_models import Recommendation, KnowledgeItem
from storage.repository import save_agent_run
from storage.seo_repository import (
    save_recommendation,
    list_recommendations,
    get_recommendation,
    update_recommendation_status,
    save_knowledge_item,
)
from workflows.base import BaseWorkflow


# ── Mapping helpers ───────────────────────────────────────────────────────────

_OWNER_MAP = {
    "ctr_improvement":  "content",
    "ranking_boost":    "content",
    "content_refresh":  "content",
    "technical":        "dev",
    "cannibalization":  "seo",
    "geo_candidate":    "content",
}

_ROLLBACK_MAP = {
    "ctr_improvement":  "버전 히스토리에서 기존 title/meta 복구",
    "ranking_boost":    "콘텐츠 업데이트 이전 버전으로 롤백",
    "content_refresh":  "CMS 버전 히스토리에서 이전 버전 복구",
    "technical":        "변경 전 설정 백업 후 복구, 개발팀 확인",
    "cannibalization":  "canonical/redirect 설정 이전 상태로 복구",
    "geo_candidate":    "추가 콘텐츠 섹션 제거",
}


def _hit_to_recommendation(hit) -> Recommendation:
    """Convert a SEORuleResult to a Recommendation model."""
    gsc_rows = []
    try:
        from data.seo_mock_data import get_gsc_queries
        gsc_rows = [r for r in get_gsc_queries() if r.url == hit.target_url]
    except Exception:
        pass

    current_metrics = {}
    if gsc_rows:
        current_metrics = {
            "clicks": sum(r.clicks for r in gsc_rows),
            "impressions": sum(r.impressions for r in gsc_rows),
            "ctr": round(sum(r.ctr for r in gsc_rows) / len(gsc_rows), 4),
            "position": round(sum(r.position for r in gsc_rows) / len(gsc_rows), 1),
        }

    priority_map = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low"}

    return Recommendation(
        target_url=hit.target_url,
        opportunity_type=hit.opportunity_type,
        priority=priority_map.get(hit.priority, "medium"),
        problem=f"[{hit.rule_id}] {hit.opportunity_type} 감지",
        recommendation=hit.recommendation,
        evidence=hit.target_queries[:3] if hit.target_queries else [],
        expected_impact=f"impact_score={hit.impact_score}/5",
        confidence_score=round(min(hit.impact_score / 5.0, 1.0), 2),
        risk_level="low" if hit.impact_score <= 2 else "medium" if hit.impact_score <= 4 else "high",
        effort_score=2,
        impact_score=hit.impact_score,
        owner=_OWNER_MAP.get(hit.opportunity_type, "seo"),
        rollback_plan=_ROLLBACK_MAP.get(hit.opportunity_type, "변경 전 상태로 수동 복구"),
        target_query_cluster=hit.target_queries[0] if hit.target_queries else None,
        current_metrics=current_metrics,
        rule_id=hit.rule_id,
    )


class SEOApprovalWorkflow(BaseWorkflow):
    """
    Manages the full recommendation lifecycle:
    1. create_recommendations() — converts rule hits → Recommendations (pending_approval)
    2. list_pending()           — shows what's waiting for human review
    3. approve(rec_id)          — marks approved, optionally links to experiment
    4. reject(rec_id, reason)   — marks rejected, records reason
    5. bulk_approve_low_risk()  — auto-approves low-risk recs below threshold
    """

    system_prompt = """당신은 SEO 추천 검토 에이전트입니다.
각 추천의 근거, 예상 임팩트, 리스크를 검토하고
승인/거부 판단을 지원합니다. 승인 없이는 어떠한 사이트 변경도 실행하지 않습니다."""

    allowed_tools = ["get_seo_overview", "get_seo_recommendations"]

    def create_recommendations(self, max_hits: int = 20) -> dict:
        """
        Run rule engine and convert top hits to Recommendation objects.
        Deduplicates against already-stored recs by rule_id + target_url.
        """
        run = AgentRun(
            workflow_name="seo_approval_create",
            trigger="manual",
            input_params={"max_hits": max_hits},
        )
        save_agent_run(run)

        from rules.seo_rules import run_all_seo_rules
        hits = run_all_seo_rules()

        # Sort by impact descending, take top N
        hits_sorted = sorted(hits, key=lambda h: h.impact_score, reverse=True)[:max_hits]

        existing = list_recommendations()
        existing_keys = {(r.get("rule_id"), r.get("target_url")) for r in existing}

        created = []
        for hit in hits_sorted:
            key = (hit.rule_id, hit.target_url)
            if key in existing_keys:
                continue
            rec = _hit_to_recommendation(hit)
            save_recommendation(rec)
            created.append(rec)
            run.recommendations_generated.append(rec.rec_id)

        run.complete(output_summary=f"{len(created)}개 신규 추천 생성 (pending_approval)")
        save_agent_run(run)

        self._log(f"  [Approval] {len(created)} new recommendations created")
        return {
            "run_id": run.run_id,
            "recommendations_created": len(created),
            "recommendations": [r.to_dict() for r in created],
        }

    def list_pending(self) -> dict:
        """Return all recommendations awaiting approval."""
        pending = list_recommendations(status="pending_approval")
        by_priority = {}
        for r in pending:
            p = r.get("priority", "medium")
            by_priority.setdefault(p, []).append(r)

        return {
            "total_pending": len(pending),
            "by_priority": {k: len(v) for k, v in by_priority.items()},
            "recommendations": pending,
        }

    def approve(
        self,
        rec_id: str,
        approver_notes: str = "",
        create_experiment: bool = True,
    ) -> dict:
        """
        Approve a recommendation.
        Optionally creates an SEOExperiment baseline to track the change.
        """
        rec = get_recommendation(rec_id)
        if not rec:
            return {"error": f"rec_id '{rec_id}' not found"}
        if rec.get("status") not in ("pending_approval", "rejected"):
            return {"error": f"Cannot approve — current status: {rec['status']}"}

        updated = update_recommendation_status(
            rec_id,
            status="approved",
            approver_notes=approver_notes,
            approved_at=datetime.now().isoformat(),
        )

        exp_id = None
        if create_experiment and rec.get("opportunity_type") in ("ctr_improvement", "ranking_boost", "content_refresh"):
            exp_id = self._create_experiment_for_rec(updated)

        self._log(f"  [Approval] ✓ Approved: {rec_id} ({rec['target_url']})")
        return {
            "status": "approved",
            "rec_id": rec_id,
            "target_url": rec["target_url"],
            "approver_notes": approver_notes,
            "experiment_id": exp_id,
        }

    def reject(self, rec_id: str, reason: str = "") -> dict:
        """Reject a recommendation with an optional reason."""
        rec = get_recommendation(rec_id)
        if not rec:
            return {"error": f"rec_id '{rec_id}' not found"}
        if rec.get("status") == "approved":
            return {"error": "Cannot reject an already-approved recommendation"}

        update_recommendation_status(
            rec_id,
            status="rejected",
            rejection_reason=reason or "사유 미기재",
            rejected_at=datetime.now().isoformat(),
        )

        self._log(f"  [Approval] ✗ Rejected: {rec_id} — {reason}")
        return {
            "status": "rejected",
            "rec_id": rec_id,
            "target_url": rec["target_url"],
            "rejection_reason": reason,
        }

    def bulk_approve_low_risk(
        self,
        max_risk_level: str = "low",
        max_effort_score: int = 2,
        approver_notes: str = "자동 승인: 저위험 추천",
    ) -> dict:
        """
        Auto-approve pending recommendations below risk/effort thresholds.
        Useful for quick wins that don't need manual review.
        """
        risk_order = {"low": 0, "medium": 1, "high": 2}
        threshold = risk_order.get(max_risk_level, 0)

        pending = list_recommendations(status="pending_approval")
        approved_ids = []
        skipped = []

        for rec in pending:
            r_level = risk_order.get(rec.get("risk_level", "high"), 2)
            effort = rec.get("effort_score", 5)
            if r_level <= threshold and effort <= max_effort_score:
                self.approve(rec["rec_id"], approver_notes=approver_notes, create_experiment=False)
                approved_ids.append(rec["rec_id"])
            else:
                skipped.append(rec["rec_id"])

        self._log(f"  [Approval] Bulk approved {len(approved_ids)}, skipped {len(skipped)}")
        return {
            "bulk_approved": len(approved_ids),
            "skipped": len(skipped),
            "approved_ids": approved_ids,
        }

    def get_approval_summary(self) -> dict:
        """Dashboard summary of recommendation states."""
        all_recs = list_recommendations()
        status_counts: dict[str, int] = {}
        for r in all_recs:
            s = r.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        return {
            "total": len(all_recs),
            "by_status": status_counts,
            "pending": status_counts.get("pending_approval", 0),
            "approved": status_counts.get("approved", 0),
            "rejected": status_counts.get("rejected", 0),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _create_experiment_for_rec(self, rec: dict) -> str | None:
        """Create an SEOExperiment baseline for the approved recommendation."""
        try:
            from models.seo_models import SEOExperiment
            from storage.seo_repository import save_experiment
            from data.seo_mock_data import get_gsc_queries, get_ga4_landing
            from datetime import timedelta

            url = rec["target_url"]
            gsc = [r for r in get_gsc_queries() if r.url == url]
            ga4 = get_ga4_landing(url)

            baseline = {
                "clicks_28d": sum(r.clicks for r in gsc),
                "impressions_28d": sum(r.impressions for r in gsc),
                "ctr": round(sum(r.ctr for r in gsc) / len(gsc), 4) if gsc else 0,
                "position": round(sum(r.position for r in gsc) / len(gsc), 1) if gsc else 0,
                "sessions": ga4[0].sessions if ga4 else 0,
                "conversions": ga4[0].conversions if ga4 else 0,
                "revenue_krw": ga4[0].revenue_krw if ga4 else 0,
            }

            today = datetime.now()
            exp = SEOExperiment(
                target_url=url,
                change_type={"ctr_improvement": "title_meta", "ranking_boost": "content_update", "content_refresh": "content_update"}.get(rec["opportunity_type"], "other"),
                change_description=rec["recommendation"],
                baseline_metrics=baseline,
                baseline_start_date=(today - __import__("datetime").timedelta(days=28)).strftime("%Y-%m-%d"),
                baseline_end_date=today.strftime("%Y-%m-%d"),
                experiment_start_date=today.strftime("%Y-%m-%d"),
                experiment_end_date=(today + __import__("datetime").timedelta(days=28)).strftime("%Y-%m-%d"),
                recommendation_id=rec["rec_id"],
            )
            save_experiment(exp)

            # Link experiment back to recommendation
            update_recommendation_status(rec["rec_id"], status="approved", experiment_id=exp.experiment_id)
            return exp.experiment_id

        except Exception as e:
            self._log(f"  [Approval] Warning: experiment creation failed — {e}")
            return None
