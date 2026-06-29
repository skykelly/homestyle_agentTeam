"""
Human Approval Workflow — Phase 2.
State machine: draft → pending_approval → approved/rejected → executed/failed → rolled_back

High-risk actions (budget_decrease, campaign_pause, landing_page_change) always require
human approval regardless of confidence score.
"""

from datetime import datetime
from typing import Optional

from models.recommendation import (
    Recommendation, RecommendationStatus, ApprovalRequired, RiskLevel
)
from storage.repository import (
    get_recommendation, list_recommendations, update_recommendation_dict
)


# Actions that always block for human approval — no auto-approve allowed
HIGH_RISK_ACTION_TYPES = {"campaign_pause", "budget_decrease", "landing_page_change"}


class ApprovalWorkflow:
    """
    Manages the full recommendation lifecycle.
    Use submit_for_approval() after creating a Recommendation — it routes
    low-risk recs to auto-approve and high-risk to pending_approval.
    """

    def submit_for_approval(self, rec: Recommendation) -> dict:
        """
        Transition: draft → pending_approval (needs human) OR approved (auto).
        Enforces: HIGH_RISK_ACTION_TYPES and HIGH/CRITICAL risk always go to human.
        """
        if rec.status != RecommendationStatus.DRAFT:
            return {"ok": False, "error": f"상태 오류: {rec.status} (draft 상태만 제출 가능)"}

        # Override approval requirement for high-risk types and risk levels
        if rec.recommendation_type in HIGH_RISK_ACTION_TYPES:
            rec.required_approval = ApprovalRequired.HUMAN
        if rec.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            rec.required_approval = ApprovalRequired.HUMAN

        if rec.required_approval == ApprovalRequired.NONE:
            rec.status = RecommendationStatus.APPROVED
            rec.approved_by = "system_auto"
            rec.approved_at = datetime.now().isoformat()
            rec.updated_at = datetime.now().isoformat()
            update_recommendation_dict(rec.to_dict())
            return {
                "ok": True,
                "status": "auto_approved",
                "recommendation_id": rec.id,
                "recommendation_type": rec.recommendation_type,
                "risk_level": rec.risk_level,
                "confidence_score": rec.confidence_score,
                "message": "신뢰도·위험도 기준 충족 → 자동 승인됨",
            }

        rec.status = RecommendationStatus.PENDING_APPROVAL
        rec.updated_at = datetime.now().isoformat()
        update_recommendation_dict(rec.to_dict())
        return {
            "ok": True,
            "status": "pending_approval",
            "recommendation_id": rec.id,
            "recommendation_type": rec.recommendation_type,
            "risk_level": rec.risk_level,
            "confidence_score": rec.confidence_score,
            "reason": rec.reason,
            "rollback_plan": rec.rollback_plan,
            "message": f"승인 대기 중. 위험도: {rec.risk_level}, 유형: {rec.recommendation_type}",
            "required_approval": rec.required_approval,
        }

    def approve(self, rec_id: str, approver: str, notes: str = "") -> dict:
        """Transition: pending_approval → approved."""
        data = get_recommendation(rec_id)
        if not data:
            return {"ok": False, "error": f"추천 ID '{rec_id}'를 찾을 수 없습니다"}
        if data["status"] != RecommendationStatus.PENDING_APPROVAL:
            return {"ok": False, "error": f"승인 불가 상태: {data['status']} (pending_approval 상태만 승인 가능)"}

        data["status"] = RecommendationStatus.APPROVED
        data["approved_by"] = approver
        data["approved_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        if notes:
            data["approval_notes"] = notes
        update_recommendation_dict(data)

        return {
            "ok": True,
            "recommendation_id": rec_id,
            "status": "approved",
            "approved_by": approver,
            "rollback_plan": data.get("rollback_plan", ""),
            "message": "승인 완료. 실행 준비 상태입니다.",
        }

    def reject(self, rec_id: str, approver: str, reason: str) -> dict:
        """Transition: pending_approval → rejected."""
        data = get_recommendation(rec_id)
        if not data:
            return {"ok": False, "error": f"추천 ID '{rec_id}'를 찾을 수 없습니다"}
        if data["status"] != RecommendationStatus.PENDING_APPROVAL:
            return {"ok": False, "error": f"거절 불가 상태: {data['status']}"}

        data["status"] = RecommendationStatus.REJECTED
        data["rejection_reason"] = reason
        data["approved_by"] = approver
        data["updated_at"] = datetime.now().isoformat()
        update_recommendation_dict(data)

        return {
            "ok": True,
            "recommendation_id": rec_id,
            "status": "rejected",
            "reason": reason,
            "message": "거절 처리 완료. 개선 후 재제출 가능합니다.",
        }

    def mark_executed(self, rec_id: str, execution_result: dict) -> dict:
        """Transition: approved → executed or failed."""
        data = get_recommendation(rec_id)
        if not data:
            return {"ok": False, "error": f"추천 ID '{rec_id}'를 찾을 수 없습니다"}
        if data["status"] != RecommendationStatus.APPROVED:
            return {"ok": False, "error": f"실행 불가 상태: {data['status']} (approved 상태만 실행 가능)"}

        success = execution_result.get("success", True)
        data["status"] = RecommendationStatus.EXECUTED if success else RecommendationStatus.FAILED
        data["executed_at"] = datetime.now().isoformat()
        data["execution_result"] = execution_result
        data["updated_at"] = datetime.now().isoformat()
        update_recommendation_dict(data)

        return {
            "ok": True,
            "recommendation_id": rec_id,
            "status": data["status"],
            "result": execution_result,
            "rollback_available": True,
            "rollback_plan": data.get("rollback_plan", ""),
        }

    def rollback(self, rec_id: str, reason: str = "") -> dict:
        """Transition: executed/failed → rolled_back."""
        data = get_recommendation(rec_id)
        if not data:
            return {"ok": False, "error": f"추천 ID '{rec_id}'를 찾을 수 없습니다"}
        if data["status"] not in (RecommendationStatus.EXECUTED, RecommendationStatus.FAILED):
            return {"ok": False, "error": f"롤백 불가 상태: {data['status']}"}

        data["status"] = RecommendationStatus.ROLLED_BACK
        data["updated_at"] = datetime.now().isoformat()
        if reason:
            data["rollback_reason"] = reason
        update_recommendation_dict(data)

        return {
            "ok": True,
            "recommendation_id": rec_id,
            "status": "rolled_back",
            "rollback_plan": data.get("rollback_plan", ""),
            "message": "롤백 완료.",
        }

    def get_pending_approvals(self) -> list:
        """Return all recommendations currently awaiting human approval."""
        return list_recommendations(status=RecommendationStatus.PENDING_APPROVAL)

    def get_approval_summary(self) -> dict:
        """Dashboard summary across all statuses."""
        all_recs = list_recommendations(limit=200)
        by_status: dict = {}
        for r in all_recs:
            s = r["status"]
            by_status[s] = by_status.get(s, 0) + 1

        pending = [r for r in all_recs if r["status"] == RecommendationStatus.PENDING_APPROVAL]

        return {
            "total_recommendations": len(all_recs),
            "by_status": by_status,
            "pending_count": len(pending),
            "pending_items": [
                {
                    "id": r["id"],
                    "type": r["recommendation_type"],
                    "platform": r["target_platform"],
                    "risk_level": r["risk_level"],
                    "reason": r["reason"][:80] + "..." if len(r.get("reason", "")) > 80 else r.get("reason", ""),
                }
                for r in pending
            ],
        }
