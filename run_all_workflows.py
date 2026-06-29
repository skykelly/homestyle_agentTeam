#!/usr/bin/env python3
"""
전체 워크플로우 자동 실행 스크립트
5개 워크플로우를 순서대로 실행하고 결과를 outputs/ 폴더에 저장합니다.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# 출력 디렉토리 생성
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SEPARATOR = "\n" + "=" * 70 + "\n"

def save_output(name: str, content: str) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"{ts}_{name}.md"
    path.write_text(content, encoding="utf-8")
    print(f"  💾 저장: {path}")
    return path


def print_header(step: int, total: int, title: str):
    bar = "█" * step + "░" * (total - step)
    print(f"\n{'='*70}")
    print(f"[{step}/{total}] {bar}  {title}")
    print(f"{'='*70}")


def run_workflow_1():
    """워크플로우 1: 캠페인 성과 분석"""
    print_header(1, 5, "캠페인 성과 분석 워크플로우")
    from workflows.campaign_analysis import CampaignAnalysisWorkflow

    wf = CampaignAnalysisWorkflow(verbose=True)
    result = wf.analyze(
        start_date="2024-11-01",
        end_date="2024-11-30",
        category="뷰티",
    )
    save_output("01_campaign_analysis", result)
    return result


def run_workflow_2():
    """워크플로우 2: 예산 최적화"""
    print_header(2, 5, "예산 최적화 워크플로우")
    from workflows.budget_optimization import BudgetOptimizationWorkflow

    wf = BudgetOptimizationWorkflow(verbose=True)
    result = wf.optimize(
        total_budget_krw=50_000_000,
        category="뷰티",
        objective="roas_maximize",
        current_month=11,
        active_platforms=["naver_search", "naver_shopping", "kakao_moment", "coupang_ads"],
    )
    save_output("02_budget_optimization", result)
    return result


def run_workflow_3():
    """워크플로우 3: 크리에이티브 전략"""
    print_header(3, 5, "크리에이티브 전략 워크플로우")
    from workflows.creative_strategy import CreativeStrategyWorkflow

    wf = CreativeStrategyWorkflow(verbose=True)
    result = wf.develop_creative(
        product_name="프리미엄 콜라겐 세럼",
        key_features=[
            "피부 탄력 30% 개선 (임상 테스트 완료)",
            "히알루론산·레티놀 고농도 함유",
            "무향·무방부제·피부과 테스트 완료",
            "30일 사용 시 눈에 띄는 변화",
        ],
        target_audience="30-45세 직장 여성",
        platforms=["naver_search", "meta_instagram", "kakao_moment", "coupang_ads"],
        promotion="블랙프라이데이 특가 30% 할인 + 무료 미니 세럼 증정",
    )
    save_output("03_creative_strategy", result)
    return result


def run_workflow_4():
    """워크플로우 4: 캠페인 기획"""
    print_header(4, 5, "캠페인 기획 워크플로우")
    from workflows.campaign_planning import CampaignPlanningWorkflow

    wf = CampaignPlanningWorkflow(verbose=True)
    result = wf.plan(
        brand_name="뷰티랩 (BeautyLab)",
        product_category="뷰티",
        campaign_objective="sales_conversion",
        total_budget_krw=100_000_000,
        campaign_period_weeks=6,
        target_audience="30-45세 스킨케어에 관심 높은 직장 여성",
        key_messages=[
            "임상 테스트로 검증된 피부 탄력 개선",
            "천연 성분 · 무방부제 · 피부과 테스트",
            "30일 환불 보장",
        ],
        include_competitor_analysis=True,
    )
    save_output("04_campaign_plan", result)
    return result


def run_workflow_5():
    """워크플로우 5: 성과 보고서 (주간 + 월간)"""
    print_header(5, 5, "성과 보고서 워크플로우")
    from workflows.reporting import ReportingWorkflow

    wf = ReportingWorkflow(verbose=True)

    print("\n[5-A] 주간 보고서 생성...")
    weekly = wf.generate_weekly_report(
        start_date="2024-11-18",
        end_date="2024-11-24",
        category="뷰티",
        platforms=["naver_search", "naver_shopping", "kakao_moment", "coupang_ads"],
    )
    save_output("05a_weekly_report", weekly)

    print("\n[5-B] 월간 보고서 생성...")
    monthly = wf.generate_monthly_report(
        start_date="2024-11-01",
        end_date="2024-11-30",
        category="뷰티",
        total_budget_krw=100_000_000,
    )
    save_output("05b_monthly_report", monthly)

    return weekly + "\n\n---\n\n" + monthly


def main():
    print("\n🚀 한국 퍼포먼스 마케팅 에이전트 — 전체 워크플로우 자동 실행")
    print(f"   실행 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   출력 폴더: {OUTPUT_DIR.absolute()}")

    results = {}
    errors = {}
    start_time = time.time()

    workflows = [
        ("campaign_analysis", run_workflow_1),
        ("budget_optimization", run_workflow_2),
        ("creative_strategy", run_workflow_3),
        ("campaign_planning", run_workflow_4),
        ("reporting", run_workflow_5),
    ]

    for name, fn in workflows:
        t0 = time.time()
        try:
            result = fn()
            results[name] = result
            elapsed = time.time() - t0
            print(f"\n  ✅ 완료 ({elapsed:.1f}초) — {len(result):,}자 생성")
        except Exception as e:
            errors[name] = str(e)
            print(f"\n  ❌ 오류: {e}")

    total_elapsed = time.time() - start_time
    print(SEPARATOR)
    print(f"🏁 전체 실행 완료")
    print(f"   총 소요 시간: {total_elapsed:.1f}초")
    print(f"   성공: {len(results)}/5  |  실패: {len(errors)}/5")
    if errors:
        for name, err in errors.items():
            print(f"   ❌ {name}: {err}")
    print(f"   결과 파일: {OUTPUT_DIR.absolute()}/")
    print(SEPARATOR)

    # Summary index
    index_lines = [
        f"# 한국 퍼포먼스 마케팅 에이전트 실행 결과",
        f"",
        f"실행 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"총 소요 시간: {total_elapsed:.1f}초",
        f"",
        f"## 워크플로우 실행 결과",
        f"",
    ]
    for name in [w[0] for w in workflows]:
        status = "✅ 성공" if name in results else f"❌ 실패: {errors.get(name,'')}"
        index_lines.append(f"- **{name}**: {status}")

    (OUTPUT_DIR / "00_index.md").write_text("\n".join(index_lines), encoding="utf-8")
    print(f"  📋 인덱스: {OUTPUT_DIR}/00_index.md")


if __name__ == "__main__":
    main()
