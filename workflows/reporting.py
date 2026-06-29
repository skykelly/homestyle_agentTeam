"""
Workflow: 성과 보고서
Generates comprehensive performance reports with cross-platform
attribution, trend analysis, and forward-looking recommendations.
"""

from workflows.base import BaseWorkflow


SYSTEM_PROMPT = """당신은 한국 퍼포먼스 마케팅 성과 분석 전문가입니다.
광고주와 팀원이 즉시 이해하고 실행할 수 있는 성과 보고서를 작성합니다.

보고서 작성 원칙:
- 핵심 성과 지표를 상단에 요약 (Executive Summary)
- 전기 대비 증감율 명시 (▲▼ 표시)
- 한국 업계 벤치마크 대비 평가
- 성과 원인 분석 (what + why)
- 실행 가능한 개선 액션 (즉시/단기/중기 구분)
- 시각적으로 읽기 쉬운 표 형식 활용

수치는 항상 원화(KRW) 단위로 표시하고,
ROAS는 % 단위, CPC/CPA는 원(₩) 단위로 표시하세요."""


class ReportingWorkflow(BaseWorkflow):
    system_prompt = SYSTEM_PROMPT
    allowed_tools = [
        "generate_performance_report",
        "get_campaign_performance",
        "get_market_events",
        "optimize_budget_allocation",
    ]

    def generate_weekly_report(
        self,
        start_date: str,
        end_date: str,
        category: str = "패션",
        platforms: list[str] | None = None,
    ) -> str:
        platform_str = ", ".join(platforms) if platforms else "전체 플랫폼"
        prompt = f"""
다음 기간의 주간 성과 보고서를 작성해 주세요:

- 보고 기간: {start_date} ~ {end_date}
- 카테고리: {category}
- 분석 플랫폼: {platform_str}

[수행 절차]
1. 주간 성과 보고서 데이터를 생성하세요
2. 전체 플랫폼 성과 데이터를 추가 조회하세요
3. 현재 시장 이벤트를 확인하세요
4. 모든 데이터를 종합하여 다음 형식의 주간 보고서를 작성하세요:

## 📊 주간 성과 보고서 ({start_date} ~ {end_date})

### 1. 핵심 성과 요약 (Executive Summary)
| 지표 | 이번 주 | 전주 대비 | 목표 달성률 |
|------|---------|----------|------------|
(표 형식으로 작성)

### 2. 플랫폼별 성과 비교
(각 플랫폼의 지출, ROAS, CPA, CTR, CVR 포함)

### 3. 주요 인사이트
- 잘 된 점 (Top 3)
- 개선 필요 사항 (Top 3)

### 4. 시장 환경 변화
- 이번 주 주요 이벤트 및 영향
- 경쟁 환경 변화

### 5. 다음 주 액션 플랜
- 즉시 실행 (입찰가, 예산 조정)
- 단기 실행 (소재, 타겟팅 개선)
- 모니터링 항목
"""
        return self.run(prompt)

    def generate_monthly_report(
        self,
        start_date: str,
        end_date: str,
        category: str = "패션",
        total_budget_krw: int = 10_000_000,
    ) -> str:
        prompt = f"""
다음 기간의 월간 성과 보고서 및 다음 달 전략을 작성해 주세요:

- 보고 기간: {start_date} ~ {end_date}
- 카테고리: {category}
- 월 예산: {total_budget_krw:,}원

[수행 절차]
1. 월간 성과 보고서를 생성하세요
2. 전체 플랫폼 상세 성과를 조회하세요
3. 다음 달 시장 이벤트를 확인하세요
4. 다음 달 예산 최적화 플랜을 수립하세요

모든 분석을 완료한 후 종합 월간 보고서를 작성하세요:

## 월간 성과 보고서 ({start_date[:7]})

### 1. 이달의 성과 요약
### 2. 채널별 상세 성과
### 3. 예산 집행 효율 분석
### 4. 이달의 Top 캠페인 & Bottom 캠페인
### 5. 시장 트렌드 및 인사이트
### 6. 다음 달 전략 방향
### 7. 다음 달 예산 배분 권장안
"""
        return self.run(prompt)
