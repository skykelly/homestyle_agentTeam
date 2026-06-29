"""
Rule-based budget optimization rules (Phase 1).
These fire deterministically — no LLM required.
Design doc principle: "Rule-based baseline 먼저, LLM은 추가 계층"
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RuleResult:
    triggered: bool
    rule_id: str
    description: str
    recommendation_type: str
    risk_level: str
    confidence: float
    change_pct: Optional[float] = None
    reason: str = ""
    evidence: list = field(default_factory=list)
    required_approval: str = "none"
    rollback_plan: str = ""


# Thresholds
ROAS_BREAK_EVEN = 100           # % — below this is losing money
ROAS_UNDERPERFORM_RATIO = 0.7   # below 70% of target → underperforming
ROAS_OVERPERFORM = 600          # % — excellent ROAS worth scaling
BUDGET_UTILIZATION_LOW = 0.70   # under-spending threshold
BUDGET_UTILIZATION_CAP = 0.95   # near budget cap
CPA_OVERRUN_RATIO = 1.5         # 50% over target CPA


def check_low_roas(
    platform: str,
    campaign: str,
    current_roas: float,
    target_roas: float,
    days_running: int = 7,
) -> RuleResult:
    """Fire if ROAS is critically below break-even or severely below target for 7+ days."""
    if current_roas < ROAS_BREAK_EVEN and days_running >= 7:
        return RuleResult(
            triggered=True,
            rule_id="BUDGET_001",
            description="ROAS 손익분기점 미달 — 캠페인 일시 중지 권고",
            recommendation_type="campaign_pause",
            risk_level="high",
            confidence=0.9,
            reason=f"ROAS {current_roas:.0f}%로 손익분기점({ROAS_BREAK_EVEN}%) 미달. {days_running}일 연속 지속.",
            evidence=[
                f"현재 ROAS: {current_roas:.0f}% (손익분기점: {ROAS_BREAK_EVEN}%)",
                f"손실 지속 기간: {days_running}일",
                f"즉각적인 예산 보호 조치 필요",
            ],
            required_approval="human",
            rollback_plan=f"'{campaign}' 캠페인 재활성화 (입찰 전략 변경 후 재개)",
        )

    if current_roas < target_roas * ROAS_UNDERPERFORM_RATIO and days_running >= 7:
        return RuleResult(
            triggered=True,
            rule_id="BUDGET_002",
            description="ROAS 목표 대비 30% 이상 미달 — 예산 20% 감액 권고",
            recommendation_type="budget_decrease",
            risk_level="medium",
            confidence=0.8,
            change_pct=-20.0,
            reason=f"ROAS {current_roas:.0f}%로 목표({target_roas:.0f}%) 대비 30% 이상 미달. {days_running}일 지속.",
            evidence=[
                f"현재 ROAS: {current_roas:.0f}% vs 목표: {target_roas:.0f}%",
                f"괴리율: {(current_roas/target_roas - 1)*100:.1f}%",
                f"7일 이상 지속 → 구조적 문제 가능성",
            ],
            required_approval="none",
            rollback_plan="예산을 감액 전 수준으로 복원",
        )

    return RuleResult(triggered=False, rule_id="BUDGET_002", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_high_roas(
    platform: str,
    campaign: str,
    current_roas: float,
    target_roas: float,
    budget_utilization: float,
) -> RuleResult:
    """Fire if ROAS is excellent and budget is near cap — scale up opportunity."""
    if current_roas >= ROAS_OVERPERFORM and budget_utilization >= BUDGET_UTILIZATION_CAP:
        return RuleResult(
            triggered=True,
            rule_id="BUDGET_003",
            description="고성과 캠페인 + 예산 소진 — 예산 30% 증액 권고",
            recommendation_type="budget_increase",
            risk_level="low",
            confidence=0.85,
            change_pct=30.0,
            reason=f"ROAS {current_roas:.0f}%로 우수 성과. 예산 소진율 {budget_utilization*100:.0f}%로 확장 여력 없음.",
            evidence=[
                f"ROAS: {current_roas:.0f}% (목표 대비 {(current_roas/target_roas - 1)*100:.0f}% 초과)",
                f"예산 소진율: {budget_utilization*100:.0f}% (스케일업 적기)",
                f"성과 안정 구간 7일 이상 유지 확인 필요",
            ],
            required_approval="none",
            rollback_plan="예산을 증액 전 수준으로 복원 (현재 예산 × 0.77)",
        )

    return RuleResult(triggered=False, rule_id="BUDGET_003", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_cpa_overrun(
    platform: str,
    campaign: str,
    current_cpa_krw: int,
    target_cpa_krw: int,
) -> RuleResult:
    """Fire if CPA is 50%+ over target."""
    if target_cpa_krw > 0 and current_cpa_krw > target_cpa_krw * CPA_OVERRUN_RATIO:
        overrun_pct = (current_cpa_krw / target_cpa_krw - 1) * 100
        return RuleResult(
            triggered=True,
            rule_id="BUDGET_004",
            description="CPA 목표 50% 초과 — 타겟 CPA 자동입찰 전환 권고",
            recommendation_type="bid_adjustment",
            risk_level="medium",
            confidence=0.75,
            reason=f"CPA {current_cpa_krw:,}원으로 목표({target_cpa_krw:,}원) 대비 {overrun_pct:.0f}% 초과.",
            evidence=[
                f"현재 CPA: {current_cpa_krw:,}원 (목표: {target_cpa_krw:,}원)",
                f"초과율: {overrun_pct:.0f}%",
                f"타겟 CPA 자동입찰로 전환 시 10-20% 개선 가능",
            ],
            required_approval="none",
            rollback_plan="수동 입찰 복원 (기존 입찰가로 재설정)",
        )

    return RuleResult(triggered=False, rule_id="BUDGET_004", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_budget_underspend(
    platform: str,
    campaign: str,
    budget_utilization: float,
    days_running: int,
) -> RuleResult:
    """Fire if budget utilization < 70% after 3+ days running."""
    if budget_utilization < BUDGET_UTILIZATION_LOW and days_running >= 3:
        return RuleResult(
            triggered=True,
            rule_id="BUDGET_005",
            description="예산 소진율 저조 — 입찰가 상향 또는 오디언스 확대 권고",
            recommendation_type="bid_adjustment",
            risk_level="low",
            confidence=0.7,
            reason=f"예산 소진율 {budget_utilization*100:.0f}%로 저조. {days_running}일째 지속.",
            evidence=[
                f"예산 소진율: {budget_utilization*100:.0f}% (정상: 95% 이상)",
                f"지속 기간: {days_running}일",
                f"노출 기회 손실 발생 중",
            ],
            required_approval="none",
            rollback_plan="입찰가를 조정 전 수준으로 복원",
        )

    return RuleResult(triggered=False, rule_id="BUDGET_005", description="", recommendation_type="", risk_level="", confidence=0.0)


def run_all_budget_rules(
    platform: str,
    campaign: str,
    current_roas: float,
    target_roas: float,
    current_cpa_krw: int,
    target_cpa_krw: int,
    budget_utilization: float,
    days_running: int = 7,
) -> list:
    """Run all budget rules and return only triggered RuleResults."""
    candidates = [
        check_low_roas(platform, campaign, current_roas, target_roas, days_running),
        check_high_roas(platform, campaign, current_roas, target_roas, budget_utilization),
        check_cpa_overrun(platform, campaign, current_cpa_krw, target_cpa_krw),
        check_budget_underspend(platform, campaign, budget_utilization, days_running),
    ]
    return [r for r in candidates if r.triggered]
