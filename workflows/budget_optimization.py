"""
Workflow: 예산 최적화
Analyzes current spend efficiency and recommends budget reallocation
based on Korean market benchmarks, seasonal events, and ROAS targets.
"""

from workflows.base import BaseWorkflow


SYSTEM_PROMPT = """당신은 한국 퍼포먼스 마케팅 예산 최적화 전문가입니다.
데이터 기반으로 광고 예산을 플랫폼·채널·시기별로 최적 배분하여
ROAS와 CPA를 극대화합니다.

예산 최적화 원칙:
- 성과 상위 플랫폼에 예산 집중 (80/20 법칙 적용)
- 한국 쇼핑 시즌(설날, 추석, 블랙프라이데이) 선제적 예산 확보
- 모바일 트래픽 비중(78%) 고려한 입찰 전략
- 카테고리별 평균 CPA 벤치마크 기준 효율 평가

모든 수치는 원화(KRW)로, 권장사항은 구체적 수치와 함께 제시하세요."""


class BudgetOptimizationWorkflow(BaseWorkflow):
    system_prompt = SYSTEM_PROMPT
    allowed_tools = [
        "get_campaign_performance",
        "optimize_budget_allocation",
        "get_market_events",
        "generate_performance_report",
    ]

    def optimize(
        self,
        total_budget_krw: int,
        category: str,
        objective: str,
        current_month: int,
        active_platforms: list[str] | None = None,
    ) -> str:
        platforms_str = ", ".join(active_platforms) if active_platforms else "미지정"
        prompt = f"""
다음 조건에 맞는 광고 예산 최적화 플랜을 수립해 주세요:

- 총 예산: {total_budget_krw:,}원 (KRW)
- 상품 카테고리: {category}
- 캠페인 목표: {objective}
- 현재 월: {current_month}월
- 운영 중인 플랫폼: {platforms_str}

[분석 절차]
1. 현재 캠페인 성과 데이터를 조회하세요 (가용 데이터 기준)
2. {category} 카테고리 최적 예산 배분안을 계산하세요
3. {current_month}월 이후 한국 시장 주요 이벤트를 확인하세요
4. 월간 성과 보고서를 생성하세요

모든 데이터를 바탕으로 다음을 포함한 예산 최적화 보고서를 작성하세요:
- 현재 대비 최적 예산 배분 비교 (플랫폼별 %, 금액)
- 예상 ROAS 및 예상 매출
- 시즌 이벤트 대응 예산 시나리오 (이벤트 전/중/후)
- 주차별 예산 집행 가이드
- 즉시 실행 가능한 입찰가 조정 액션 플랜
"""
        return self.run(prompt)
