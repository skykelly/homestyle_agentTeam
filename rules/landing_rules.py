"""
Rule-based landing page and conversion funnel rules (Phase 1).
Fires deterministically — no LLM required.
"""

from rules.budget_rules import RuleResult


BOUNCE_RATE_HIGH = 70.0         # % threshold
PAGE_LOAD_SLOW_SECS = 3.0       # seconds — slow on mobile
PAGE_LOAD_CRITICAL_SECS = 5.0   # seconds — critical
CART_ABANDON_HIGH = 80.0        # % threshold
MIN_SESSIONS = 500              # minimum traffic for significance
MIN_CART_SESSIONS = 200


def check_high_bounce_rate(
    page_url: str,
    bounce_rate_pct: float,
    sessions: int,
) -> RuleResult:
    """Fire if bounce rate > 70% with 500+ sessions."""
    if bounce_rate_pct > BOUNCE_RATE_HIGH and sessions >= MIN_SESSIONS:
        return RuleResult(
            triggered=True,
            rule_id="LANDING_001",
            description="높은 이탈률 — 랜딩페이지 UX 개선 필요",
            recommendation_type="landing_page_change",
            risk_level="medium",
            confidence=0.80,
            reason=f"이탈률 {bounce_rate_pct:.0f}%로 임계값({BOUNCE_RATE_HIGH:.0f}%) 초과. {sessions:,} 세션 기준.",
            evidence=[
                f"이탈률: {bounce_rate_pct:.0f}% (정상 범위: 40-60%)",
                f"분석 세션: {sessions:,}건 (통계적으로 유의미)",
                f"광고 메시지와 랜딩 일관성 점검 필요",
            ],
            required_approval="human",
            rollback_plan="랜딩페이지를 이전 버전으로 롤백",
        )

    return RuleResult(triggered=False, rule_id="LANDING_001", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_slow_page_load(
    page_url: str,
    avg_load_seconds: float,
) -> RuleResult:
    """Fire if page load time exceeds 3 seconds."""
    if avg_load_seconds > PAGE_LOAD_SLOW_SECS:
        risk = "critical" if avg_load_seconds > PAGE_LOAD_CRITICAL_SECS else "medium"
        return RuleResult(
            triggered=True,
            rule_id="LANDING_002",
            description="페이지 로딩 속도 저하 — 기술 최적화 필요",
            recommendation_type="landing_page_change",
            risk_level=risk,
            confidence=0.90,
            reason=f"페이지 로딩 평균 {avg_load_seconds:.1f}초. 모바일 전환율에 직접 영향.",
            evidence=[
                f"평균 로딩: {avg_load_seconds:.1f}초 (목표: 2초 이하)",
                "1초 지연 시 전환율 7% 감소 (Google 데이터)",
                "모바일 비중 78% 환경에서 치명적 영향",
            ],
            required_approval="human",
            rollback_plan="이미지 압축/CDN 설정 변경 전 원복",
        )

    return RuleResult(triggered=False, rule_id="LANDING_002", description="", recommendation_type="", risk_level="", confidence=0.0)


def check_cart_abandonment(
    campaign: str,
    cart_abandon_rate_pct: float,
    sessions: int,
) -> RuleResult:
    """Fire if cart abandonment rate > 80% with 200+ cart sessions."""
    if cart_abandon_rate_pct > CART_ABANDON_HIGH and sessions >= MIN_CART_SESSIONS:
        return RuleResult(
            triggered=True,
            rule_id="LANDING_003",
            description="장바구니 이탈률 과다 — 리마케팅 오디언스 강화 권고",
            recommendation_type="audience_expansion",
            risk_level="medium",
            confidence=0.75,
            reason=f"장바구니 이탈률 {cart_abandon_rate_pct:.0f}%. {sessions:,} 세션 중 고의도 이탈 발생.",
            evidence=[
                f"장바구니 이탈률: {cart_abandon_rate_pct:.0f}% (업계 평균: 70%)",
                f"분석 세션: {sessions:,}건",
                "이탈 사용자 리타겟팅으로 20-30% 재유입 가능",
            ],
            required_approval="none",
            rollback_plan="리마케팅 오디언스 설정 제거",
        )

    return RuleResult(triggered=False, rule_id="LANDING_003", description="", recommendation_type="", risk_level="", confidence=0.0)


def run_all_landing_rules(
    page_url: str,
    campaign: str,
    bounce_rate_pct: float = 0.0,
    sessions: int = 0,
    avg_load_seconds: float = 0.0,
    cart_abandon_rate_pct: float = 0.0,
) -> list:
    """Run all landing page rules and return only triggered RuleResults."""
    candidates = [
        check_high_bounce_rate(page_url, bounce_rate_pct, sessions),
        check_slow_page_load(page_url, avg_load_seconds),
        check_cart_abandonment(campaign, cart_abandon_rate_pct, sessions),
    ]
    return [r for r in candidates if r.triggered]
