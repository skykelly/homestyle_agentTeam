"""
Workflow: 캠페인 기획
Full-funnel campaign planning for the Korean market.
Produces a complete campaign blueprint with platform mix,
weekly execution plan, KPI targets, and creative brief.
"""

from workflows.base import BaseWorkflow


SYSTEM_PROMPT = """당신은 한국 디지털 마케팅 캠페인 기획 전문가입니다.
브랜드 전략부터 퍼포먼스 실행까지 전 단계를 아우르는 통합 캠페인 플랜을 수립합니다.

캠페인 기획 원칙:
1. 풀 퍼널 접근 (인지 → 고려 → 전환 → 재구매)
2. 한국 시장 특화 채널 믹스 (네이버, 카카오, 쿠팡 중심)
3. 데이터 기반 KPI 목표 설정 (한국 카테고리 벤치마크 기준)
4. 한국 쇼핑 캘린더 연동 시즌 전략
5. 크리에이티브 효율화 (A/B 테스트 설계 포함)
6. 법적 준수 (한국 개인정보보호법, 표시광고법)

보고서는 실무 담당자가 바로 실행할 수 있도록 구체적이고 명확하게 작성하세요."""


class CampaignPlanningWorkflow(BaseWorkflow):
    system_prompt = SYSTEM_PROMPT
    allowed_tools = [
        "create_campaign_plan",
        "optimize_budget_allocation",
        "get_market_events",
        "analyze_competitors",
        "generate_ad_copy",
        "get_keyword_analysis",
    ]

    def plan(
        self,
        brand_name: str,
        product_category: str,
        campaign_objective: str,
        total_budget_krw: int,
        campaign_period_weeks: int,
        target_audience: str,
        key_messages: list[str] | None = None,
        include_competitor_analysis: bool = True,
    ) -> str:
        messages_str = "\n".join(f"- {m}" for m in key_messages) if key_messages else "- (미지정)"

        prompt = f"""
다음 조건으로 한국 시장 맞춤형 캠페인 플랜을 수립해 주세요:

브랜드명: {brand_name}
상품 카테고리: {product_category}
캠페인 목표: {campaign_objective}
총 예산: {total_budget_krw:,}원 (KRW)
캠페인 기간: {campaign_period_weeks}주
타겟 오디언스: {target_audience}
핵심 메시지:
{messages_str}

[수행 절차 - 순서대로 실행하세요]

1. 한국 시장 이벤트를 조회하여 캠페인 기간과 겹치는 이벤트를 파악하세요
2. 전체 캠페인 플랜을 생성하세요 (KPI, 플랫폼 전략, 주차별 계획)
3. 예산 최적화 배분안을 산출하세요
4. {'경쟁사 분석을 수행하세요' if include_competitor_analysis else '경쟁사 분석은 생략합니다'}
5. 네이버 검색광고 기반 핵심 키워드를 분석하세요
6. 주요 플랫폼(네이버, 카카오)의 초기 광고 소재를 생성하세요

모든 조사를 완료한 후, 다음을 포함한 종합 캠페인 기획서를 작성하세요:

## 1. 캠페인 개요
- 목표 KPI (ROAS, CPA, 전환수)
- 타겟 오디언스 정의
- 핵심 메시지 및 USP

## 2. 채널 전략
- 플랫폼별 역할 정의 (인지/고려/전환)
- 예산 배분 (플랫폼별 %, 금액)
- 예상 성과 (ROAS, 예상 매출)

## 3. 시즌 캘린더
- 주요 이벤트 연계 프로모션
- 예산 시나리오 (일반 vs. 이벤트)

## 4. 크리에이티브 전략
- 플랫폼별 광고 소재 방향
- 초기 A/B 테스트 설계

## 5. 실행 플랜
- 주차별 실행 항목
- 성과 체크포인트 (KPI 모니터링 기준)

## 6. 리스크 관리
- 주요 리스크 및 대응 방안
"""
        return self.run(prompt)
