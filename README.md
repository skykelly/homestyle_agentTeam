# 🇰🇷 한국 시장 퍼포먼스 마케팅 AI 에이전트

네이버, 카카오, 쿠팡, 메타, 유튜브 등 한국 주요 광고 플랫폼을 통합 운영하는  
Claude 기반 멀티 워크플로우 퍼포먼스 마케팅 에이전트입니다.

---

## 아키텍처

```
homestyle_agentTeam/
├── main.py                          # CLI 진입점 (typer)
├── config/
│   └── settings.py                  # 환경 변수 & 플랫폼 설정
├── data/
│   └── korean_market.py             # 한국 시장 지식베이스
│                                    #   ├── 쇼핑 이벤트 캘린더 (설날/추석/블프 등)
│                                    #   ├── 플랫폼별 벤치마크 (ROAS/CPC/CTR)
│                                    #   └── 카테고리별 KPI 기준
├── tools/
│   ├── definitions.py               # Claude tool schemas (9개 도구)
│   └── handlers.py                  # Tool 핸들러 구현체
├── workflows/                       # 전문화된 워크플로우 (agentic loop)
│   ├── base.py                      # BaseWorkflow (tool-use 루프)
│   ├── campaign_analysis.py         # 캠페인 성과 분석
│   ├── budget_optimization.py       # 예산 최적화
│   ├── creative_strategy.py         # 광고 소재 전략
│   ├── campaign_planning.py         # 캠페인 기획
│   └── reporting.py                 # 성과 보고서
├── agents/
│   └── performance_marketing_agent.py  # 통합 대화형 에이전트
└── tests/
    ├── test_tools.py                # Tool handler 단위 테스트
    └── test_korean_market.py        # 한국 시장 데이터 테스트
```

### 워크플로우 구조

```
사용자 요청
    │
    ▼
KoreaPerformanceMarketingAgent
    │
    ├─► CampaignAnalysisWorkflow    (성과 분석: 플랫폼별 ROAS/CPA 비교)
    ├─► BudgetOptimizationWorkflow  (예산 최적화: 시즌·카테고리 기반)
    ├─► CreativeStrategyWorkflow    (소재 전략: 플랫폼별 카피 + A/B 테스트)
    ├─► CampaignPlanningWorkflow    (캠페인 기획: 풀 퍼널 플랜)
    └─► ReportingWorkflow           (성과 보고: 주간/월간 리포트)
                │
                ▼
          BaseWorkflow (agentic loop)
                │
                ▼
         Claude Tool Use API
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
    네이버    카카오   쿠팡 / 메타 / 유튜브
```

---

## 지원 기능

| # | 기능 | 사용 도구 |
|---|------|----------|
| 1 | 캠페인 성과 조회 | `get_campaign_performance` |
| 2 | 네이버 키워드 분석 | `get_keyword_analysis` |
| 3 | 예산 최적화 배분 | `optimize_budget_allocation` |
| 4 | 경쟁사 분석 | `analyze_competitors` |
| 5 | 광고 소재(카피) 생성 | `generate_ad_copy` |
| 6 | 한국 시장 이벤트 캘린더 | `get_market_events` |
| 7 | 캠페인 플랜 수립 | `create_campaign_plan` |
| 8 | 성과 보고서 생성 | `generate_performance_report` |
| 9 | A/B 테스트 분석 | `ab_test_analysis` |

### 지원 광고 플랫폼

- **네이버**: 검색광고, 쇼핑광고, 파워콘텐츠
- **카카오**: 카카오모먼트, 카카오 디스플레이광고
- **쿠팡**: 쿠팡 로켓광고
- **메타**: 인스타그램, 페이스북
- **구글/유튜브**: 유튜브 인스트림, 구글 디스플레이

---

## 설치 & 실행

### 1. 환경 설정

```bash
git clone <repo>
cd homestyle_agentTeam
pip install -r requirements.txt

cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 등 API 키 입력
```

### 2. 실행 방법

```bash
# 대화형 모드 (기본값)
python main.py

# 데모 실행
python main.py demo

# 캠페인 성과 분석
python main.py analyze --start 2024-11-01 --end 2024-11-30 --category 뷰티

# 예산 최적화
python main.py budget --budget 50000000 --category 뷰티 --objective roas_maximize

# 캠페인 기획
python main.py plan --brand "MyBrand" --category 패션 --budget 30000000 --weeks 4

# 성과 보고서 (주간/월간)
python main.py report --start 2024-11-01 --end 2024-11-07 --type weekly
python main.py report --start 2024-11-01 --end 2024-11-30 --type monthly

# 광고 소재 전략
python main.py creative --product "콜라겐 세럼" --audience "30대 여성" \
  --features "탄력개선,보습,무방부제" --promo "블랙프라이데이 30% 할인"
```

### 3. Python API 사용

```python
# 대화형 에이전트
from agents.performance_marketing_agent import KoreaPerformanceMarketingAgent

agent = KoreaPerformanceMarketingAgent()
response = agent.chat("11월 뷰티 캠페인 성과를 분석해줘")
print(response)

# 특화 워크플로우
from workflows.campaign_planning import CampaignPlanningWorkflow

workflow = CampaignPlanningWorkflow()
plan = workflow.plan(
    brand_name="MyBrand",
    product_category="뷰티",
    campaign_objective="sales_conversion",
    total_budget_krw=30_000_000,
    campaign_period_weeks=4,
    target_audience="30-45세 여성",
    key_messages=["피부 탄력 개선", "천연 성분", "피부과 테스트 완료"],
)
```

---

## 한국 시장 특화 지식

### 쇼핑 이벤트 캘린더 (자동 반영)
| 이벤트 | 월 | ROAS 배수 | 예산 증가 권장 |
|--------|-----|----------|--------------|
| 설날 연휴 | 1-2월 | 1.8x | +40% |
| 어린이날 | 5월 | 2.0x | +50% |
| 어버이날 | 5월 | 1.6x | +30% |
| 추석 연휴 | 9-10월 | 2.1x | +60% |
| 광군제/블프 | 11월 | 2.5x | +80% |
| 크리스마스 | 12월 | 1.9x | +50% |

### 플랫폼별 벤치마크 (2024 기준)
| 플랫폼 | 평균 ROAS | 평균 CVR |
|--------|---------|---------|
| 쿠팡광고 | 750% | 5.2% |
| 네이버쇼핑 | 600% | 3.5% |
| 네이버검색 | 450% | 2.8% |
| 카카오모먼트 | 320% | 1.5% |
| 인스타그램 | 350% | 1.8% |

---

## 테스트

```bash
python -m pytest tests/ -v
# 45개 테스트 모두 통과
```
