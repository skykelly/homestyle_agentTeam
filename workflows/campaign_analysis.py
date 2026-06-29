"""
Workflow: 캠페인 성과 분석
Multi-step agentic workflow that pulls cross-platform data,
identifies winners/losers, and surfaces actionable insights.
"""

from workflows.base import BaseWorkflow


SYSTEM_PROMPT = """당신은 한국 디지털 퍼포먼스 마케팅 전문가입니다.
네이버, 카카오, 쿠팡, 메타, 유튜브 등 한국 주요 광고 플랫폼 전문가로,
데이터 기반 인사이트를 한국어로 명확하게 제공합니다.

분석 시 반드시 다음을 포함하세요:
1. 플랫폼별 성과 비교 (ROAS, CPA, CTR, CVR)
2. 한국 시장 벤치마크 대비 평가
3. 상위/하위 성과 캠페인 식별
4. 구체적인 액션 아이템 (수치 포함)
5. 다음 기간 예산 조정 권장사항

응답은 한국어로 작성하되, 영어 마케팅 용어(ROAS, CPA 등)는 그대로 사용하세요."""


class CampaignAnalysisWorkflow(BaseWorkflow):
    system_prompt = SYSTEM_PROMPT
    allowed_tools = [
        "get_campaign_performance",
        "get_market_events",
        "optimize_budget_allocation",
        "ab_test_analysis",
    ]

    def analyze(
        self,
        start_date: str,
        end_date: str,
        platforms: list[str] | None = None,
        category: str = "패션",
    ) -> str:
        platform_str = ", ".join(platforms) if platforms else "전체 플랫폼"
        prompt = f"""
다음 기간의 광고 캠페인 성과를 종합 분석해 주세요:

- 분석 기간: {start_date} ~ {end_date}
- 분석 플랫폼: {platform_str}
- 상품 카테고리: {category}

[분석 절차]
1. 전체 플랫폼('all') 성과 데이터를 조회하세요
2. 현재 월의 한국 시장 이벤트를 확인하세요
3. {category} 카테고리 기준 예산 최적화 권장사항을 확인하세요
4. 모든 데이터를 종합하여 다음 항목을 포함한 분석 보고서를 작성하세요:
   - 전체 성과 요약 (총 지출, 총 수익, 전환수, 통합 ROAS)
   - 플랫폼별 성과 비교표
   - 성과 우수/부진 플랫폼 원인 분석
   - 한국 시장 이벤트를 고려한 향후 2개월 기회
   - 즉시 실행 가능한 최적화 액션 플랜 (우선순위 순)
"""
        return self.run(prompt)
