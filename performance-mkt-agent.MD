# Performance Marketing AI Agent 개발 계획서

## 1. 프로젝트 목표

퍼포먼스 마케팅 대행사가 반복적으로 수행하는 광고 운영, 성과 진단, 예산 조정, 소재 테스트, 키워드/검색어 관리, 랜딩 페이지 개선, SEO/GEO 대응, 리포팅 업무를 AI Agent Team으로 대체한다.

목표는 광고 플랫폼 자체의 자동 입찰을 다시 만드는 것이 아니다. Google Ads, Meta Ads, GA4, Search Console, 내부 제품/프로모션/매출 데이터를 연결해 다음의 업무 루프를 자동화하는 것이다.

1. 매일 광고 성과를 수집한다.
2. 이상 징후와 기회 영역을 진단한다.
3. 캠페인/예산/소재/검색어/랜딩 개선안을 만든다.
4. 사람이 승인하면 API 또는 작업 지시서 형태로 실행한다.
5. 실행 결과를 다시 학습 데이터와 운영 지식으로 축적한다.

초기 MVP는 "완전 자동 집행"이 아니라 "진단 → 추천 → 승인 → 실행 → 리포트" 구조로 만든다. 예산 변경, 캠페인 중단, 신규 집행, 소재 교체는 반드시 Human Approval을 거치도록 한다.

---

## 2. 핵심 사용자

**Primary User**

퍼포먼스 마케팅 담당자 또는 브랜드/제품 캠페인 오너.

**Secondary User**

마케팅 리더, 이커머스 운영자, SEO/GEO 담당자, 제품/프로모션 담당자.

**대체하려는 대행사 업무**

- 일별 광고 성과 모니터링
- ROAS, CPA, CVR, CPC, CTR 이상 징후 탐지
- 캠페인/광고그룹/소재별 성과 진단
- 예산 증액/감액 추천
- 저성과 캠페인 원인 분석
- 신규 타겟/키워드/소재 제안
- 랜딩 페이지 개선 제안
- SEO 검색어 기회 발굴
- AI 검색/GEO 대응 콘텐츠 브리프 생성
- 주간/월간 리포트 작성
- 실험 설계와 결과 판정

---

## 3. MVP 범위

**포함**

1. Google Ads 성과 데이터 수집
2. GA4 전환/매출/세션 데이터 수집
3. Search Console 검색어/페이지 성과 수집
4. Meta Ads는 초기에는 mock connector로 구조만 설계
5. 캠페인 성과 대시보드
6. AI 성과 진단 리포트
7. 예산/소재/키워드/랜딩 개선 추천
8. 승인 워크플로우
9. 승인된 액션의 실행 로그 저장
10. 주간 리포트 자동 생성
11. Agent 실행 이력과 추천 근거 저장

**제외**

1. 승인 없는 자동 예산 변경
2. 대규모 캠페인 자동 생성
3. 개인정보 기반 타겟팅 자동 집행
4. 법무/브랜드 검수 없는 소재 자동 배포
5. 실제 광고비 집행 API 호출은 MVP 후반부에서 feature flag로 제한

---

## 4. 제품 컨셉

제품명은 임시로 **Performance Agent One**으로 한다.

이 시스템은 하나의 챗봇이 아니라 여러 전문 Agent가 협업하는 Agent Team 구조다.

중앙의 Marketing Orchestrator Agent가 사용자의 목표와 데이터를 해석하고, 하위 Agent들에게 작업을 분배한다.

### Agent Team 구성

**1. Marketing Orchestrator Agent**

전체 작업을 조율한다.
사용자의 목표, 기간, 예산, 캠페인 상태를 파악하고 필요한 Agent를 호출한다.

**2. Data Ingestion Agent**

Google Ads, GA4, Search Console, Meta Ads, 내부 매출/상품/프로모션 데이터를 수집한다.
API 호출 실패, 누락 데이터, 지연 데이터를 감지한다.

**3. Performance Diagnosis Agent**

ROAS, CPA, CPC, CTR, CVR, 전환수, 매출, 예산 소진율을 분석한다.
성과 하락 원인을 캠페인, 소재, 타겟, 검색어, 랜딩, 외부 이벤트 관점으로 분해한다.

**4. Budget Optimization Agent**

캠페인별 예산 증액/감액 후보를 제안한다.
단순 ROAS 기준이 아니라 전환 규모, 학습 안정성, 예산 소진율, 마진, 재고, 프로모션 우선순위를 함께 고려한다.

**5. Creative Agent**

광고 카피, 이미지 콘셉트, 소재 테스트 가설을 생성한다.
제품 USP, 고객 pain point, 시즌성, 프로모션 메시지를 반영한다.

**6. Keyword & Query Agent**

Search Ads 검색어, SEO 검색어, Search Console query 데이터를 분석한다.
신규 키워드, 제외 키워드, 랜딩 페이지 개선 기회를 제안한다.

**7. SEO/GEO Agent**

검색 노출 페이지와 AI 검색 대응 콘텐츠를 진단한다.
FAQ, 비교 콘텐츠, 구매가이드, 제품 지식 구조화, schema markup 후보를 제안한다.

**8. Experiment Agent**

A/B 테스트, 예산 테스트, 소재 테스트, 랜딩 테스트를 설계한다.
실험 종료 후 통계적으로 유의한 결과인지 판단하고 다음 액션을 제안한다.

**9. Compliance & Brand Safety Agent**

광고 문구, 가격 표현, 프로모션 조건, 브랜드 톤, 금지 표현을 검토한다.
위험도가 높은 추천은 자동 실행하지 않고 승인 필요 상태로 남긴다.

**10. Reporting Agent**

일간/주간/월간 리포트를 자동 생성한다.
단순 숫자 나열이 아니라 "무엇이 변했고, 왜 변했고, 다음에 무엇을 해야 하는가" 중심으로 작성한다.

---

## 5. 핵심 기능

### 5.1 Dashboard

- 전체 광고비
- 매출
- 전환수
- ROAS
- CPA
- CPC
- CTR
- CVR
- 캠페인별 성과
- 전일/전주/전월 대비 변화
- 위험 캠페인
- 성장 후보 캠페인
- 승인 대기 액션

### 5.2 Daily Performance Brief

매일 아침 다음 내용을 생성한다.

- 어제 성과 요약
- 전일 대비 가장 큰 변화
- 예산 과소/과다 집행 캠페인
- ROAS 하락 캠페인
- CPA 급등 캠페인
- 신규 기회 캠페인
- 오늘 승인해야 할 액션

### 5.3 Recommendation Engine

추천 액션 유형은 다음과 같다.

- 예산 증액
- 예산 감액
- 캠페인 일시 중지
- 입찰 전략 점검
- 소재 교체
- 신규 소재 테스트
- 검색어 제외
- 키워드 확장
- 랜딩 페이지 개선
- SEO 콘텐츠 생성
- GEO 대응 콘텐츠 생성
- 트래킹 오류 점검
- 프로모션 메시지 교체

각 추천에는 반드시 다음 필드를 포함한다.

- `recommendation_type`
- `target_platform`
- `target_campaign`
- `current_metric`
- `expected_impact`
- `confidence_score`
- `risk_level`
- `reason`
- `evidence`
- `required_approval`
- `rollback_plan`

### 5.4 Human Approval Workflow

추천 액션은 바로 실행하지 않는다.

상태값은 다음과 같다.

- `draft`
- `pending_approval`
- `approved`
- `rejected`
- `executed`
- `failed`
- `rolled_back`

사용자는 추천을 승인, 거절, 수정 승인할 수 있어야 한다.

### 5.5 Execution Layer

초기에는 실제 API 실행 대신 execution plan을 생성한다.
이후 Google Ads API, Meta Marketing API 연결이 완료되면 승인된 액션만 실행한다.

실행 전에는 dry-run을 지원한다.

### 5.6 SEO/GEO Brief Generator

Search Console 데이터와 제품 지식을 기반으로 다음 문서를 생성한다.

- 검색어 기회 리포트
- 콘텐츠 개선 브리프
- 제품 비교 콘텐츠 브리프
- FAQ 후보
- AI 검색 답변 최적화용 Q&A
- schema markup 제안
- 내부 링크 제안

---

## 6. 기술 구조

### 권장 스택

| 영역 | 기술 |
|------|------|
| Frontend | Next.js App Router, TypeScript |
| UI | Tailwind CSS, shadcn/ui |
| Backend | Next.js API Route 또는 FastAPI |
| DB MVP | SQLite |
| DB Production | PostgreSQL |
| ORM | Prisma 또는 Drizzle |
| Job Queue | BullMQ 또는 cron 기반 worker |
| LLM Adapter | OpenAI-compatible interface |
| Agent Runtime | custom lightweight orchestrator |
| Auth MVP | simple local auth |
| Logging | structured JSON logs |
| Tests | Vitest 또는 Pytest |

초기 구현은 단순성과 Codex 작업 효율을 위해 Next.js + TypeScript + SQLite 구조로 시작한다. Python 기반 분석 모듈이 필요하면 `/workers` 하위에 별도로 둔다.

---

## 7. 데이터 모델

### accounts
- `id`
- `name`
- `business_unit`
- `currency`
- `timezone`
- `created_at`

### platforms
- `id`
- `name`
- `type`
- `auth_status`
- `created_at`

### campaigns
- `id`
- `platform`
- `external_campaign_id`
- `name`
- `objective`
- `status`
- `budget`
- `bidding_strategy`
- `start_date`
- `end_date`

### ad_groups
- `id`
- `campaign_id`
- `external_ad_group_id`
- `name`
- `status`

### ads
- `id`
- `campaign_id`
- `ad_group_id`
- `external_ad_id`
- `name`
- `creative_id`
- `status`

### daily_metrics
- `id`
- `date`
- `platform`
- `campaign_id`
- `ad_group_id`
- `ad_id`
- `impressions`
- `clicks`
- `cost`
- `conversions`
- `revenue`
- `ctr`
- `cpc`
- `cpa`
- `cvr`
- `roas`

### search_queries
- `id`
- `date`
- `source`
- `query`
- `page`
- `impressions`
- `clicks`
- `ctr`
- `position`
- `conversions`
- `revenue`

### landing_pages
- `id`
- `url`
- `title`
- `product_category`
- `status`
- `seo_score`
- `conversion_rate`

### recommendations
- `id`
- `created_at`
- `agent_name`
- `recommendation_type`
- `target_platform`
- `target_entity_type`
- `target_entity_id`
- `title`
- `summary`
- `evidence_json`
- `expected_impact`
- `confidence_score`
- `risk_level`
- `status`
- `approval_required`
- `approved_by`
- `approved_at`

### agent_runs
- `id`
- `agent_name`
- `input_json`
- `output_json`
- `status`
- `started_at`
- `completed_at`
- `error_message`

### experiments
- `id`
- `name`
- `hypothesis`
- `target_entity_type`
- `target_entity_id`
- `start_date`
- `end_date`
- `primary_metric`
- `status`
- `result_summary`

### knowledge_items
- `id`
- `type`
- `title`
- `content`
- `source`
- `tags`
- `created_at`
- `updated_at`

---

## 8. 주요 화면

### 8.1 Home Dashboard
- 오늘의 성과 요약
- 위험 신호
- 기회 신호
- 승인 대기 추천
- 주간 성과 변화

### 8.2 Campaign Detail
- 캠페인 KPI
- 추세 차트
- 광고그룹/소재별 성과
- 관련 추천
- 실행 이력

### 8.3 Recommendations
- 추천 목록
- 필터: `risk_level`, `platform`, `status`, `recommendation_type`
- 상세 근거 보기
- 승인/거절/수정 승인

### 8.4 Agent Runs
- Agent 실행 기록
- 입력 데이터
- 출력 결과
- 오류 로그
- 재실행 버튼

### 8.5 SEO/GEO
- 검색어 기회
- 페이지별 노출/클릭/순위
- 콘텐츠 개선 브리프
- AI 검색 대응 Q&A 초안

### 8.6 Reports
- Daily Brief
- Weekly Report
- Monthly Report
- Export Markdown
- Export HTML

---

## 9. Agent 의사결정 규칙

### Budget Optimization Rule

**예산 증액 후보:**
- ROAS가 목표 이상
- CPA가 목표 이하
- 예산 소진율이 85% 이상
- 최근 3일 이상 성과 안정
- 재고 또는 프로모션 이슈 없음

**예산 감액 후보:**
- ROAS가 목표 미만
- CPA가 목표 초과
- 최근 3일 이상 하락
- 클릭은 있으나 전환이 낮음
- 랜딩 페이지 CVR 저하

### Creative Test Rule

**신규 소재 테스트 후보:**
- CTR 하락
- frequency 상승
- CVR 유지 또는 하락
- 동일 메시지 장기 운영
- 프로모션/시즌 변화 발생

### Landing Page Rule

**랜딩 개선 후보:**
- 광고 CTR은 높지만 CVR 낮음
- Search Console 노출은 많지만 CTR 낮음
- 제품 USP와 광고 메시지 불일치
- 가격/혜택/CTA 가시성 부족

### SEO/GEO Rule

**콘텐츠 생성 후보:**
- 노출은 높지만 클릭 낮은 query
- AI 검색에서 답변형으로 노출될 가능성이 높은 question query
- 제품 비교/구매가이드 의도가 강한 query
- 브랜드가 답변 주도권을 가져야 하는 query

---

## 10. API Connector 설계

### 공통 인터페이스

각 플랫폼 connector는 동일 인터페이스를 따른다.

```typescript
interface MarketingConnector {
  getAccounts(): Promise<Account[]>
  getCampaigns(accountId: string): Promise<Campaign[]>
  getMetrics(params: MetricQuery): Promise<DailyMetric[]>
  createExecutionPlan(action: Recommendation): Promise<ExecutionPlan>
  executeApprovedAction(action: Recommendation): Promise<ExecutionResult>
}
```

### Google Ads Connector

**초기 구현:**
- campaign 목록 조회
- daily metrics 조회
- keyword/search term 데이터 조회
- recommendation 조회
- dry-run execution plan 생성

**후속 구현:**
- campaign budget 변경
- campaign status 변경
- asset 추가
- experiment 생성

### GA4 Connector

**초기 구현:**
- date별 sessions, users, conversions, revenue 조회
- source/medium/campaign 기준 전환 성과 조회
- landing page 기준 성과 조회

### Search Console Connector

**초기 구현:**
- query별 impressions, clicks, ctr, position 조회
- page별 impressions, clicks, ctr, position 조회
- query + page 조합 조회

### Meta Ads Connector

**초기 구현:**
- mock connector
- sample JSON 기반 dashboard 표시
- connector interface만 먼저 완성

**후속 구현:**
- campaign/adset/ad insights 조회
- creative 성과 조회
- 승인된 액션 실행

---

## 11. LLM Prompt 구조

### System Prompt

```
너는 퍼포먼스 마케팅 운영 전문가이자 광고 성과 분석 Agent다.
반드시 수치 근거를 기반으로 판단한다.
추정과 사실을 구분한다.
예산 변경, 캠페인 중단, 소재 교체는 자동 실행하지 않고 승인 요청으로 남긴다.
불확실한 경우 confidence_score를 낮게 설정한다.
```

### Diagnosis Prompt

```
입력된 캠페인 성과 데이터를 분석해 다음을 출력하라.

- 핵심 변화
- 원인 가설
- 위험 캠페인
- 성장 후보 캠페인
- 추천 액션
- 근거 데이터
- confidence_score
- risk_level
```

### Recommendation Prompt

```
추천 액션을 JSON으로 출력하라.
각 추천은 실행 가능해야 하며, target entity와 rollback plan을 포함해야 한다.
```

---

## 12. 개발 단계

### Phase 0. Repository 준비
- Next.js 프로젝트 생성
- TypeScript 설정
- Tailwind/shadcn 설정
- SQLite/ORM 설정
- 기본 layout 구성
- sample data seed 구성

### Phase 1. Data Model & Seed
- DB schema 작성
- sample campaigns, metrics, search queries 생성
- seed script 작성
- dashboard에서 sample data 표시

### Phase 2. Dashboard
- Home Dashboard
- Campaign Detail
- KPI cards
- trend chart
- campaign table
- risk/opportunity cards

### Phase 3. Agent Runtime
- agent registry 구현
- orchestrator 구현
- agent_runs 저장
- mock LLM adapter 구현
- 실제 LLM adapter는 환경변수 기반으로 연결

### Phase 4. Diagnosis Agent
- daily_metrics 기반 성과 진단
- rule-based baseline 먼저 구현
- 이후 LLM summary 추가
- recommendations 테이블에 저장

### Phase 5. Recommendation & Approval
- 추천 목록 화면
- 추천 상세 화면
- approve/reject/update 상태 변경
- 승인 이력 저장

### Phase 6. SEO/GEO Agent
- Search Console mock data 기반 query 분석
- 콘텐츠 브리프 생성
- FAQ/Q&A 초안 생성
- landing page 개선 제안

### Phase 7. Report Agent
- Daily Brief 생성
- Weekly Report 생성
- Markdown export
- HTML export

### Phase 8. Real Connectors
- Google Ads connector skeleton
- GA4 connector skeleton
- Search Console connector skeleton
- OAuth credential placeholder
- 실제 API 호출은 feature flag로 보호

### Phase 9. Guardrail & Monitoring
- high-risk action 차단
- 예산 변경 한도 설정
- action audit log
- error handling
- retry policy
- test coverage 보강

---

## 13. Codex 작업 지시

우선 실제 광고 API 연결보다 제품 골격과 Agent 운영 루프를 먼저 구현한다.

### 첫 번째 PR 목표

1. Next.js + TypeScript 프로젝트 기본 구조
2. SQLite DB schema
3. sample seed data
4. Home Dashboard
5. Campaign Detail
6. Recommendations 화면
7. Agent Runs 화면
8. rule-based Diagnosis Agent
9. recommendations 생성
10. approval status 변경

실제 Google Ads/GA4/Search Console API는 아직 호출하지 말고 connector interface와 mock connector만 만든다.

### 두 번째 PR 목표

1. SEO/GEO 화면
2. Search Console mock data
3. Query Opportunity 분석
4. Content Brief 생성
5. Daily Brief 생성
6. Weekly Report Markdown export

### 세 번째 PR 목표

1. Google Ads connector skeleton
2. GA4 connector skeleton
3. Search Console connector skeleton
4. 환경변수 기반 credentials 구조
5. API dry-run mode
6. feature flag 기반 실제 실행 차단

---

## 14. 파일 구조 제안

```
/src
  /app
    /dashboard
    /campaigns/[id]
    /recommendations
    /agent-runs
    /seo-geo
    /reports
    /api
      /agents/run-diagnosis
      /recommendations/[id]/approve
      /recommendations/[id]/reject
  /components
    /dashboard
    /campaigns
    /recommendations
    /reports
    /ui
  /lib
    /db
    /agents
      orchestrator.ts
      diagnosis-agent.ts
      budget-agent.ts
      creative-agent.ts
      seo-geo-agent.ts
      reporting-agent.ts
      compliance-agent.ts
    /connectors
      marketing-connector.ts
      google-ads-connector.ts
      ga4-connector.ts
      search-console-connector.ts
      meta-ads-connector.ts
      mock-connector.ts
    /rules
      performance-rules.ts
      budget-rules.ts
      seo-rules.ts
    /llm
      llm-adapter.ts
      mock-llm.ts
    /reports
      markdown-export.ts
/prisma
  schema.prisma
  seed.ts
/docs
  product-plan.md
  agent-architecture.md
  api-connector-plan.md
  guardrails.md
```

---

## 15. Acceptance Criteria

MVP 완료 기준은 다음과 같다.

1. sample data만으로 대시보드가 정상 동작한다.
2. 캠페인별 KPI와 추세를 볼 수 있다.
3. Diagnosis Agent를 실행하면 recommendations가 생성된다.
4. 각 recommendation은 근거, 기대효과, 위험도, confidence_score를 포함한다.
5. 사용자는 recommendation을 승인/거절할 수 있다.
6. 승인된 액션은 executed가 아니라 approved 상태까지만 변경된다.
7. Agent 실행 이력이 agent_runs에 저장된다.
8. SEO/GEO 화면에서 검색어 기회와 콘텐츠 브리프를 볼 수 있다.
9. Daily/Weekly Report를 Markdown으로 export할 수 있다.
10. 실제 광고 API 실행은 feature flag 없이는 불가능하다.

---

## 16. 중요한 설계 원칙

1. **AI는 광고 플랫폼의 자동입찰을 대체하지 않는다.**
   AI는 운영 판단, 진단, 추천, 실험 설계, 리포팅을 대체한다.

2. **모든 추천은 근거 데이터와 함께 저장한다.**
   "왜 이 추천을 했는가"가 추적 가능해야 한다.

3. **자동 실행보다 승인 워크플로우를 우선한다.**
   광고비와 브랜드 리스크가 있으므로 Human-in-the-loop가 기본이다.

4. **Agent의 결과는 지식으로 축적한다.**
   성공한 추천, 실패한 추천, 거절된 추천, 실행 결과를 모두 knowledge_items 또는 agent memory로 남긴다.

5. **Rule-based baseline을 먼저 만들고 LLM을 붙인다.**
   LLM이 없어도 기본 진단과 추천이 동작해야 한다.

6. **마케팅 언어가 아니라 실행 가능한 액션으로 출력한다.**
   "성과 개선 필요"가 아니라 "캠페인 A 예산 15% 감액 검토, 이유는 CPA 32% 상승과 CVR 18% 하락"처럼 출력한다.

---

## 17. 향후 확장

- 실제 Google Ads API execution
- Meta Marketing API execution
- Creative image generation workflow
- Promotion calendar 연동
- Product feed 연동
- 재고/마진 데이터 연동
- MMM 또는 incrementality module
- Slack/Teams daily alert
- Brand Answer Engine 연동
- Knowledge Atlas 연동
- AgentOne 내부 업무 Agent로 확장
