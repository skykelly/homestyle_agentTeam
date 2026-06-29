#!/usr/bin/env python3
"""
Phase 1 & Phase 2 데모 스크립트
- Phase 1: 구조화된 Recommendation 스키마, Rule-based baseline, Agent Run 로깅
- Phase 2: Human Approval Workflow 상태 머신, 고위험 자동 차단, 롤백 플랜
"""

import json
from datetime import datetime
from pathlib import Path

SEPARATOR = "\n" + "=" * 70 + "\n"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def print_section(title: str):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")


def print_json(data: dict, indent: int = 2):
    print(json.dumps(data, ensure_ascii=False, indent=indent))


# ── Phase 1 Demo: Rule-based Engine ────────────────────────────────────────

def demo_phase1_rules():
    print_section("Phase 1-A: Rule-based Budget Rules (LLM 없이 즉시 실행)")

    from rules.budget_rules import run_all_budget_rules

    # Scenario: 네이버 검색광고 — ROAS 저조 + CPA 초과
    results = run_all_budget_rules(
        platform="naver_search",
        campaign="뷰티랩_콜라겐세럼_전환",
        current_roas=180,        # 목표 350%에 한참 못 미침
        target_roas=350,
        current_cpa_krw=45000,   # 목표 18,000원 대비 2.5배
        target_cpa_krw=18000,
        budget_utilization=0.45, # 예산도 소진 안 됨
        days_running=9,
    )

    print(f"\n탐지된 이슈: {len(results)}건")
    for r in results:
        print(f"\n  [{r.rule_id}] {r.description}")
        print(f"  위험도: {r.risk_level} | 신뢰도: {r.confidence*100:.0f}% | 승인필요: {r.required_approval}")
        print(f"  사유: {r.reason}")
        print(f"  롤백: {r.rollback_plan}")

    print_section("Phase 1-B: Rule-based Creative Rules")

    from rules.creative_rules import run_all_creative_rules

    creative_results = run_all_creative_rules(
        platform="meta_instagram",
        campaign="뷰티랩_인스타_브랜딩",
        creative_id="IG_collagen_v1",
        current_ctr_pct=0.18,    # 벤치마크 1.5%의 12%
        benchmark_ctr_pct=1.5,
        current_cvr_pct=0.8,     # 벤치마크 2.0%의 40%
        benchmark_cvr_pct=2.0,
        days_running=25,         # 21일 초과
        frequency=6.2,           # 5회 초과
    )

    print(f"\n탐지된 이슈: {len(creative_results)}건")
    for r in creative_results:
        print(f"\n  [{r.rule_id}] {r.description}")
        print(f"  위험도: {r.risk_level} | 승인필요: {r.required_approval}")
        print(f"  사유: {r.reason}")

    print_section("Phase 1-C: Structured Recommendation 모델 생성")

    from models.recommendation import (
        Recommendation, RecommendationType, RiskLevel, ApprovalRequired
    )
    from storage.repository import save_recommendation, list_recommendations

    rec = Recommendation(
        recommendation_type=RecommendationType.BUDGET_DECREASE,
        target_platform="naver_search",
        target_campaign="뷰티랩_콜라겐세럼_전환",
        current_metric={"roas": 180, "cpa_krw": 45000, "ctr_pct": 1.2, "cvr_pct": 1.8},
        expected_impact={"roas_change_pct": 0, "spend_change_pct": -20, "cpa_reduction_expected": True},
        confidence_score=0.80,
        risk_level=RiskLevel.MEDIUM,
        reason="ROAS 180%로 목표(350%) 대비 30% 이상 미달. 9일 지속.",
        evidence=["현재 ROAS: 180% vs 목표: 350%", "괴리율: -48.6%", "7일 이상 구조적 저성과"],
        required_approval=ApprovalRequired.NONE,
        rollback_plan="예산을 감액 전 수준으로 복원",
    )

    save_recommendation(rec)
    print(f"\n  저장된 Recommendation ID: {rec.id}")
    print(f"  상태: {rec.status}")
    print(f"  유형: {rec.recommendation_type}")
    print(f"  위험도: {rec.risk_level}")

    print_section("Phase 1-D: Agent Run 로깅")

    from models.agent_run import AgentRun
    from storage.repository import save_agent_run, list_agent_runs
    import time

    run = AgentRun(
        workflow_name="budget_rules_demo",
        trigger="manual",
        input_params={"platform": "naver_search", "campaign": "뷰티랩_콜라겐세럼_전환"},
    )
    run.add_tool_call("run_all_budget_rules", "naver_search / ROAS=180", f"{len(results)}건 탐지")
    time.sleep(0.05)
    run.complete(output_summary=f"규칙 {len(results)}건 탐지, 권고사항 1개 생성")
    save_agent_run(run)

    recent_runs = list_agent_runs(limit=3)
    print(f"\n  저장된 Run ID: {run.run_id}")
    print(f"  상태: {run.status}")
    print(f"  소요시간: {run.duration_seconds}초")
    print(f"  전체 로그 건수: {len(recent_runs)}")

    return results, creative_results, rec


# ── Phase 2 Demo: Human Approval Workflow ──────────────────────────────────

def demo_phase2_approval():
    print_section("Phase 2-A: 고위험 액션 자동 차단 (campaign_pause)")

    from models.recommendation import (
        Recommendation, RecommendationType, RiskLevel, ApprovalRequired
    )
    from storage.repository import save_recommendation
    from workflows.approval import ApprovalWorkflow

    approval_wf = ApprovalWorkflow()

    # HIGH-RISK: campaign_pause → must go to pending_approval
    high_risk_rec = Recommendation(
        recommendation_type=RecommendationType.CAMPAIGN_PAUSE,   # 고위험 유형
        target_platform="naver_search",
        target_campaign="뷰티랩_콜라겐세럼_전환",
        current_metric={"roas": 75},  # 손익분기점 미달
        expected_impact={"spend_saved_daily_krw": 500000},
        confidence_score=0.90,
        risk_level=RiskLevel.HIGH,
        reason="ROAS 75%로 손익분기점 미달. 7일 연속 손실.",
        evidence=["ROAS: 75% (손익분기점: 100%)", "손실 7일 지속", "즉각 조치 필요"],
        required_approval=ApprovalRequired.NONE,  # 선언은 NONE이지만 시스템이 HUMAN으로 재정의
        rollback_plan="캠페인 재활성화 (입찰 전략 변경 후 재개)",
    )
    save_recommendation(high_risk_rec)

    result = approval_wf.submit_for_approval(high_risk_rec)
    print(f"\n  campaign_pause 제출 결과:")
    print(f"  → 상태: {result['status']}  (NONE 선언이었지만 HIGH RISK로 자동 차단)")
    print(f"  → 권고사항 ID: {result['recommendation_id']}")
    print(f"  → 메시지: {result['message']}")
    print(f"  → 롤백 플랜: {result.get('rollback_plan', '')}")

    print_section("Phase 2-B: 저위험 자동 승인 (bid_adjustment)")

    low_risk_rec = Recommendation(
        recommendation_type=RecommendationType.BID_ADJUSTMENT,
        target_platform="naver_search",
        target_campaign="뷰티랩_콜라겐세럼_전환",
        current_metric={"budget_utilization": 0.42},
        expected_impact={"utilization_target": 0.95},
        confidence_score=0.70,
        risk_level=RiskLevel.LOW,
        reason="예산 소진율 42%로 저조. 3일 지속.",
        evidence=["소진율: 42% (정상: 95%)", "3일 지속", "노출 기회 손실"],
        required_approval=ApprovalRequired.NONE,
        rollback_plan="입찰가를 조정 전 수준으로 복원",
    )
    save_recommendation(low_risk_rec)

    result2 = approval_wf.submit_for_approval(low_risk_rec)
    print(f"\n  bid_adjustment 제출 결과:")
    print(f"  → 상태: {result2['status']}  (저위험 → 자동 승인)")
    print(f"  → 권고사항 ID: {result2['recommendation_id']}")
    print(f"  → 메시지: {result2['message']}")

    print_section("Phase 2-C: Human Approve/Reject 흐름")

    # Approve the high-risk one
    approve_result = approval_wf.approve(
        rec_id=high_risk_rec.id,
        approver="마케팅팀장_김영수",
        notes="데이터 확인 후 승인. 내일 오전 9시 실행 예정.",
    )
    print(f"\n  승인 결과:")
    print(f"  → 상태: {approve_result['status']}")
    print(f"  → 승인자: {approve_result['approved_by']}")
    print(f"  → 롤백 플랜: {approve_result['rollback_plan']}")

    # Create another pending one and reject it
    reject_target = Recommendation(
        recommendation_type=RecommendationType.LANDING_PAGE_CHANGE,
        target_platform="kakao_moment",
        target_campaign="뷰티랩_카카오_전환",
        current_metric={"bounce_rate_pct": 78, "cvr_pct": 0.3},
        expected_impact={"bounce_rate_reduction_pct": 20},
        confidence_score=0.70,
        risk_level=RiskLevel.MEDIUM,
        reason="이탈률 78%로 임계값 초과. 1,200 세션 기준.",
        evidence=["이탈률: 78% (임계값: 70%)", "1,200 세션", "랜딩페이지 UX 개선 필요"],
        required_approval=ApprovalRequired.HUMAN,
        rollback_plan="랜딩페이지를 이전 버전으로 롤백",
    )
    save_recommendation(reject_target)
    approval_wf.submit_for_approval(reject_target)

    reject_result = approval_wf.reject(
        rec_id=reject_target.id,
        approver="퍼포먼스팀_이지은",
        reason="다음 주 리뉴얼 예정이므로 현재 변경 불필요. 리뉴얼 후 재진단 예정.",
    )
    print(f"\n  거절 결과:")
    print(f"  → 상태: {reject_result['status']}")
    print(f"  → 사유: {reject_result['reason']}")

    print_section("Phase 2-D: Executed → Rollback 흐름")

    exec_result = approval_wf.mark_executed(
        rec_id=high_risk_rec.id,
        execution_result={"success": True, "action": "campaign_paused", "paused_at": datetime.now().isoformat()},
    )
    print(f"\n  실행 결과:")
    print(f"  → 상태: {exec_result['status']}")
    print(f"  → 롤백 가능: {exec_result['rollback_available']}")

    rollback_result = approval_wf.rollback(
        rec_id=high_risk_rec.id,
        reason="일시 중지 후 ROAS가 회복되어 재개 결정",
    )
    print(f"\n  롤백 결과:")
    print(f"  → 상태: {rollback_result['status']}")
    print(f"  → 롤백 플랜: {rollback_result['rollback_plan']}")

    print_section("Phase 2-E: 전체 승인 현황 대시보드")

    summary = approval_wf.get_approval_summary()
    print(f"\n  총 권고사항: {summary['total_recommendations']}건")
    print(f"  상태별 분포:")
    for status, count in summary["by_status"].items():
        print(f"    {status}: {count}건")
    print(f"\n  승인 대기: {summary['pending_count']}건")
    if summary["pending_items"]:
        for item in summary["pending_items"]:
            print(f"    [{item['id']}] {item['type']} / {item['platform']} / 위험도: {item['risk_level']}")

    return summary


# ── Phase 2 Full Diagnosis Demo ─────────────────────────────────────────────

def demo_diagnosis_workflow():
    print_section("Phase 2-F: DiagnosisWorkflow — 규칙 엔진 + LLM 통합 진단")

    from workflows.diagnosis import DiagnosisWorkflow

    wf = DiagnosisWorkflow(verbose=True)

    # Simulate a poorly performing campaign
    result = wf.diagnose(
        platform="kakao_moment",
        campaign="뷰티랩_카카오_여름프로모션",
        category="뷰티",
        metrics={
            "roas": 165,              # 목표 400% 미달
            "cpa_krw": 38000,         # 목표 16,000원 초과
            "ctr_pct": 0.35,          # 벤치마크 1.8%의 19%
            "cvr_pct": 0.9,           # 벤치마크 2.5%의 36%
            "budget_utilization": 0.55,
            "days_running": 12,
            "frequency": 6.8,
            "bounce_rate_pct": 74,
            "page_load_seconds": 4.2,
            "sessions": 850,
        },
        auto_submit=True,
        llm_augment=True,
    )

    print(f"\n  진단 결과 요약:")
    print(f"  Run ID: {result['run_id']}")
    print(f"  규칙 탐지: {result['summary']['rule_hits']}건")
    print(f"  권고사항: {result['summary']['recommendations_generated']}건")
    print(f"  자동 승인: {result['summary']['auto_approved']}건")
    print(f"  인간 승인 필요: {result['summary']['pending_human_approval']}건")

    if result["pending_approval_ids"]:
        print(f"\n  승인 대기 ID: {', '.join(result['pending_approval_ids'])}")

    print(f"\n  권고사항 목록:")
    for rec in result["recommendations"]:
        print(f"    [{rec['id']}] {rec['recommendation_type']}")
        print(f"           위험도: {rec['risk_level']} | 상태: {rec['status']}")
        print(f"           사유: {rec['reason'][:70]}...")

    if result.get("llm_insights"):
        print(f"\n  LLM 추가 인사이트:")
        print(result["llm_insights"][:600] + "..." if len(result["llm_insights"]) > 600 else result["llm_insights"])

    # Save full result
    out_path = OUTPUT_DIR / f"phase2_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  💾 전체 결과 저장: {out_path}")

    return result


def main():
    print(SEPARATOR)
    print("🚀 Phase 1 & Phase 2 구현 데모")
    print(f"   실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEPARATOR)

    print("\n══ PHASE 1: 구조화된 권고사항 + 규칙 엔진 + 로깅 ══")
    rule_results, creative_results, rec = demo_phase1_rules()

    print("\n══ PHASE 2: Human Approval Workflow ══")
    summary = demo_phase2_approval()

    print("\n══ PHASE 2: 통합 진단 워크플로우 ══")
    diag_result = demo_diagnosis_workflow()

    print(SEPARATOR)
    print("✅ Phase 1 & Phase 2 데모 완료")
    print(f"\n구현된 기능:")
    print(f"  Phase 1:")
    print(f"    • Structured Recommendation 스키마 (9가지 유형, 4가지 위험도)")
    print(f"    • Rule-based Budget Rules (BUDGET_001~005) — LLM 없이 즉시 실행")
    print(f"    • Rule-based Creative Rules (CREATIVE_001~003)")
    print(f"    • Rule-based Landing Rules (LANDING_001~003)")
    print(f"    • Agent Run 로깅 (JSON 파일 persistence)")
    print(f"  Phase 2:")
    print(f"    • Human Approval Workflow 상태 머신")
    print(f"      draft → pending_approval → approved/rejected → executed/failed → rolled_back")
    print(f"    • 고위험 액션 자동 차단 (campaign_pause, budget_decrease, landing_page_change)")
    print(f"    • 저위험 액션 자동 승인 (bid_adjustment, keyword_add, audience_expansion)")
    print(f"    • 롤백 플랜 자동 생성 (모든 권고사항에 포함)")
    print(f"    • DiagnosisWorkflow: 규칙 엔진 1차 → LLM 인사이트 2차")
    print(f"    • 5개 신규 Claude 도구: run_diagnosis, list_recommendations,")
    print(f"      approve_recommendation, reject_recommendation, get_approval_summary")
    print(SEPARATOR)


if __name__ == "__main__":
    main()
