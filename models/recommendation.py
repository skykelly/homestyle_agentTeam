"""
Structured Recommendation schema (Phase 1).
Matches design doc section 5.3 — all recommendations flow through this model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class RecommendationType(str, Enum):
    BUDGET_INCREASE = "budget_increase"
    BUDGET_DECREASE = "budget_decrease"
    BID_ADJUSTMENT = "bid_adjustment"
    CREATIVE_REFRESH = "creative_refresh"
    AUDIENCE_EXPANSION = "audience_expansion"
    CAMPAIGN_PAUSE = "campaign_pause"
    KEYWORD_ADD = "keyword_add"
    KEYWORD_REMOVE = "keyword_remove"
    LANDING_PAGE_CHANGE = "landing_page_change"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class ApprovalRequired(str, Enum):
    NONE = "none"
    HUMAN = "human"
    MANAGER = "manager"


@dataclass
class Recommendation:
    recommendation_type: RecommendationType
    target_platform: str
    target_campaign: str
    current_metric: dict        # {"roas": 280, "cpa_krw": 15000, ...}
    expected_impact: dict       # {"roas_change_pct": 15, "spend_change_pct": 20, ...}
    confidence_score: float     # 0.0 - 1.0
    risk_level: RiskLevel
    reason: str
    evidence: list              # list[str]
    required_approval: ApprovalRequired
    rollback_plan: str

    # Auto-generated
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    status: RecommendationStatus = field(default=RecommendationStatus.DRAFT)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    executed_at: Optional[str] = None
    execution_result: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recommendation_type": self.recommendation_type,
            "target_platform": self.target_platform,
            "target_campaign": self.target_campaign,
            "current_metric": self.current_metric,
            "expected_impact": self.expected_impact,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "reason": self.reason,
            "evidence": self.evidence,
            "required_approval": self.required_approval,
            "rollback_plan": self.rollback_plan,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "rejection_reason": self.rejection_reason,
            "executed_at": self.executed_at,
            "execution_result": self.execution_result,
        }
