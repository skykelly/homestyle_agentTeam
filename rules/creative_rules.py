"""
Rule-based creative performance rules (Phase 1).
Fires deterministically — no LLM required.
"""

from rules.budget_rules import RuleResult


CTR_UNDERPERFORM_RATIO = 0.33   # below 33% of benchmark → critical
CREATIVE_FATIGUE_DAYS = 21      # days before forced refresh
CREATIVE_FATIGUE_FREQ = 5.0     # impressions per user before fatigue
CVR_UNDERPERFORM_RATIO = 0.5    # below 50% of benchmark → landing issue


def check_low_ctr(
    platform: str,
    creative_id: str,
    current_ctr_pct: float,
    benchmark_ctr_pct: float,
    days_running: int,
) -> RuleResult:
    """Fire if CTR is below 33% of benchmark for 5+ days."""
    if benchmark_ctr_pct > 0 and current_ctr_pct < benchmark_ctr_pct * CTR_UNDERPERFORM_RATIO and days_running >= 5:
        return RuleResult(
            triggered=True,
            rule_id="CREATIVE_001",
            description="CTR 심각 저조 — 소재 즉시 교체 권고",
            recommendation_type="creative_refresh",
            risk_level="medium",
            confidence=0.85,
            reason=f"CTR {current_ctr_pct:.2f}%로 벤치마크({benchmark_ctr_pct:.2f}%) 대비 67% 이상 미달. {days_running}일 지속.",
            evidence=[
                f"현재 CTR: {current_ctr_pct:.2f}% (벤치마크: {benchmark_ctr_pct:.2f}%)",
                f"미달율: {(1 - current_ctr_pct/benchmark_ctr_pct)*100:.0f}%",
                f"{days_running}일 연속 저성과 → 소재 자체 문제",
            ],
            required_approval="none",
            rollback_plan=f"'{creative_id}' 이전 소재 복원 (비활성화 취소)",
        )

    return RuleResult(triggered=False, rule_id="CREATIVE_001", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_creative_fatigue(
    platform: str,
    creative_id: str,
    days_running: int,
    frequency: float,
) -> RuleResult:
    """Fire if creative runs 21+ days or frequency > 5 per user."""
    if days_running >= CREATIVE_FATIGUE_DAYS or frequency > CREATIVE_FATIGUE_FREQ:
        parts = []
        if days_running >= CREATIVE_FATIGUE_DAYS:
            parts.append(f"{days_running}일 운영 (권장 수명: {CREATIVE_FATIGUE_DAYS}일)")
        if frequency > CREATIVE_FATIGUE_FREQ:
            parts.append(f"평균 노출 빈도 {frequency:.1f}회 (임계값: {CREATIVE_FATIGUE_FREQ}회)")

        return RuleResult(
            triggered=True,
            rule_id="CREATIVE_002",
            description="소재 피로도 감지 — 소재 교체 권고",
            recommendation_type="creative_refresh",
            risk_level="low",
            confidence=0.75,
            reason=". ".join(parts) + " → 성과 저하 예상.",
            evidence=[
                f"소재 운영 기간: {days_running}일",
                f"평균 노출 빈도: {frequency:.1f}회",
                f"소재 수명 초과 (신규 소재로 교체 권장)",
            ],
            required_approval="none",
            rollback_plan="신규 소재 성과 미달 시 기존 소재 재활성화",
        )

    return RuleResult(triggered=False, rule_id="CREATIVE_002", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_low_cvr(
    platform: str,
    campaign: str,
    current_cvr_pct: float,
    benchmark_cvr_pct: float,
    days_running: int,
) -> RuleResult:
    """Fire if CVR < 50% of benchmark — likely landing page issue not creative."""
    if benchmark_cvr_pct > 0 and current_cvr_pct < benchmark_cvr_pct * CVR_UNDERPERFORM_RATIO and days_running >= 5:
        return RuleResult(
            triggered=True,
            rule_id="CREATIVE_003",
            description="CVR 저조 — 랜딩페이지 점검 및 개선 권고",
            recommendation_type="landing_page_change",
            risk_level="medium",
            confidence=0.70,
            reason=f"CVR {current_cvr_pct:.2f}%로 벤치마크({benchmark_cvr_pct:.2f}%) 대비 50% 미달. 랜딩페이지 이슈 가능성.",
            evidence=[
                f"현재 CVR: {current_cvr_pct:.2f}% (벤치마크: {benchmark_cvr_pct:.2f}%)",
                f"CTR 대비 전환 손실 큼 → 광고가 아닌 랜딩 문제",
                f"{days_running}일 지속",
            ],
            required_approval="human",
            rollback_plan="랜딩페이지를 원래 URL로 복원",
        )

    return RuleResult(triggered=False, rule_id="CREATIVE_003", description="", recommendation_type="", risk_level="", confidence=0.0)


def run_all_creative_rules(
    platform: str,
    campaign: str,
    creative_id: str,
    current_ctr_pct: float,
    benchmark_ctr_pct: float,
    current_cvr_pct: float,
    benchmark_cvr_pct: float,
    days_running: int,
    frequency: float = 0.0,
) -> list:
    """Run all creative rules and return only triggered RuleResults."""
    candidates = [
        check_low_ctr(platform, creative_id, current_ctr_pct, benchmark_ctr_pct, days_running),
        check_creative_fatigue(platform, creative_id, days_running, frequency),
        check_low_cvr(platform, campaign, current_cvr_pct, benchmark_cvr_pct, days_running),
    ]
    return [r for r in candidates if r.triggered]
