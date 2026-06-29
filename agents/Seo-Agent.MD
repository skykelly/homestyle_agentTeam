SEO Marketing AI Agent 개발 계획서

1. 프로젝트 목표

SEO Marketing AI Agent의 목표는 기존 SEO 대행사 또는 내부 SEO 담당자가 반복적으로 수행하는 검색 성과 분석, 키워드 기회 발굴, 콘텐츠 개선, 기술 SEO 진단, 구조화 데이터 점검, 내부 링크 최적화, GEO/AI 검색 대응, 리포팅 업무를 AI Agent Team으로 대체하는 것이다.

이 Agent는 단순한 SEO 콘텐츠 생성기가 아니다.
검색 데이터, 사이트 데이터, 콘텐츠 데이터, 제품/카테고리 지식, GA4 전환 데이터, PageSpeed/기술 진단 데이터를 연결하여 다음의 운영 루프를 자동화한다.

검색 성과 수집 → 기회 탐지 → 원인 진단 → 개선안 생성 → 승인 → CMS/개발 요청 → 성과 측정 → 지식 축적

초기 MVP는 “자동 발행”이 아니라 “진단·추천·브리프·수정안 생성·승인 워크플로우”를 중심으로 구현한다. 콘텐츠 발행, title/meta 변경, canonical 변경, robots/sitemap 수정, 구조화 데이터 삽입 등 검색 노출에 직접 영향을 줄 수 있는 액션은 반드시 Human Approval을 거친다.

⸻

2. 제품 컨셉

제품명은 임시로 SEO Agent One으로 한다.

SEO Agent One은 Organic Search와 AI Search 시대를 동시에 대응하는 Agent Team이다. 기존 SEO의 핵심인 Google 검색 성과 개선뿐 아니라, ChatGPT, Perplexity, Gemini, AI Overview, Copilot 등 답변형 검색 환경에서 브랜드와 제품이 정확히 언급되고 인용될 수 있도록 콘텐츠와 지식 구조를 개선한다.

핵심 방향은 다음과 같다.

1. SEO 운영의 반복 분석 업무를 자동화한다.
2. 검색어 단위가 아니라 Query Intent Cluster 단위로 기회를 관리한다.
3. 콘텐츠 생성이 아니라 “검색 의도-제품 지식-브랜드 메시지-전환 목적”을 연결한 브리프를 생성한다.
4. 기술 SEO 이슈를 단순 나열하지 않고 비즈니스 영향도 기준으로 우선순위화한다.
5. AI 검색 대응을 위해 명확한 Q&A, 비교 정보, 제품 속성, 근거 기반 콘텐츠, 구조화 데이터, 내부 링크를 강화한다.
6. 모든 추천과 실행 결과를 Knowledge Base에 축적하여 다음 판단에 활용한다.

⸻

3. 핵심 사용자

Primary User는 SEO 담당자, 콘텐츠 마케터, 이커머스 카테고리 담당자, 브랜드/제품 마케터다.

Secondary User는 마케팅 리더, D2C몰 운영자, 개발/퍼블리싱 담당자, 상품기획 담당자, 고객경험 담당자다.

대체하고자 하는 업무는 다음과 같다.

* Google Search Console 데이터 확인
* Organic Search 트래픽 하락 원인 분석
* 검색어별 CTR/Position 개선 기회 탐색
* 콘텐츠 리라이트 브리프 작성
* Title/Meta Description 개선안 작성
* 제품/카테고리 페이지 SEO 개선안 작성
* 내부 링크 후보 발굴
* 중복/카니발라이제이션 콘텐츠 탐지
* 색인/크롤링 이슈 점검
* Core Web Vitals 및 PageSpeed 개선 우선순위 도출
* 구조화 데이터 적용 후보 발굴
* FAQ, 구매가이드, 비교 콘텐츠, How-to 콘텐츠 브리프 생성
* AI 검색/GEO 대응용 Brand Answer 콘텐츠 설계
* 주간/월간 SEO 리포트 작성

⸻

4. MVP 범위

4.1 포함 범위

MVP에서는 다음 기능을 구현한다.

1. Google Search Console mock connector 및 connector interface
2. GA4 organic landing page mock connector 및 connector interface
3. PageSpeed Insights mock connector 및 connector interface
4. Sitemap/robots/meta/canonical 간단 진단 crawler
5. SEO Dashboard
6. Query Opportunity 분석
7. Content Brief 생성
8. Title/Meta 개선안 생성
9. Technical SEO Audit
10. Structured Data 추천
11. Internal Link 추천
12. GEO/AI Search Brief 생성
13. Recommendation 생성 및 승인 워크플로우
14. Weekly SEO Report Markdown export
15. Agent 실행 로그 저장
16. 추천 근거 및 결과를 Knowledge Items로 축적

4.2 제외 범위

초기 MVP에서는 다음을 제외한다.

1. 승인 없는 CMS 자동 발행
2. 대량 AI 콘텐츠 자동 생성 및 자동 게시
3. 자동 백링크 생성
4. 댓글/포럼/커뮤니티 자동 스팸 배포
5. Google 색인 강제 요청 자동화
6. 검색 순위 조작 목적의 Black-hat SEO
7. 실제 CMS 변경 API 호출
8. Search Console API 실계정 연동
9. 외부 유료 SEO 툴의 실제 API 연동
10. 실시간 SERP 크롤링 대량 실행

⸻

5. Agent Team 구조

SEO Agent One은 중앙 Orchestrator와 전문 Sub-Agent로 구성한다.

5.1 SEO Orchestrator Agent

전체 SEO 작업을 조율하는 중앙 Agent다.

역할:

* 사용자의 요청을 해석한다.
* 필요한 하위 Agent를 호출한다.
* 데이터 수집, 분석, 추천, 승인 요청, 리포트 생성을 연결한다.
* 추천 간 충돌을 조정한다.
* 비즈니스 영향도 기준으로 우선순위를 산정한다.
* 최종 결과를 사람이 이해할 수 있는 형태로 정리한다.

5.2 SEO Data Ingestion Agent

Search Console, GA4, PageSpeed, Sitemap, CMS, Product Feed 데이터를 수집하고 정규화한다.

역할:

* GSC query/page/date/device/country 데이터 수집
* GA4 landing page/session/conversion/revenue 데이터 수집
* PageSpeed/Lighthouse score 수집
* Sitemap URL 목록 수집
* URL별 title, meta description, h1, canonical, status code 추출
* 제품/카테고리 메타데이터 수집
* 모든 데이터를 공통 schema로 저장

5.3 Query Opportunity Agent

검색어와 페이지 데이터를 분석해 성장 기회를 찾는다.

대표 기회 유형:

* 노출은 높지만 CTR이 낮은 query
* 평균 position 4~15위로 page 1 진입 가능성이 높은 query
* 클릭은 많지만 전환율이 낮은 landing page
* position은 유지되나 클릭이 감소한 query
* 브랜드 검색어에서 경쟁사/리뷰/커뮤니티 페이지에 밀리는 query
* 제품 비교/추천/구매가이드 의도가 강한 query
* AI 검색 답변화 가능성이 높은 question query
* query intent와 landing page content가 맞지 않는 경우
* 여러 페이지가 같은 query를 두고 경쟁하는 cannibalization

5.4 Content Brief Agent

Query Opportunity를 바탕으로 콘텐츠 개선 브리프를 생성한다.

역할:

* 검색 의도 분류
* 타깃 query cluster 정의
* 현재 페이지의 부족한 정보 진단
* 추가해야 할 섹션 제안
* FAQ 제안
* 제품/카테고리 USP 반영
* 브랜드 메시지 반영
* 내부 링크 후보 제안
* title/meta/h1 개선안 작성
* 콘텐츠 작성자 또는 CMS 담당자가 바로 작업할 수 있는 brief 생성

5.5 SEO Editor Agent

기존 콘텐츠를 SEO 관점에서 개선하는 Agent다.

역할:

* title 개선안 생성
* meta description 개선안 생성
* h1/h2 구조 개선
* 본문 섹션 리라이트
* FAQ 생성
* 비교표/체크리스트/구매가이드 초안 생성
* 중복 표현 제거
* 브랜드 톤앤매너 반영
* 과도한 키워드 반복 방지
* Helpful content 관점의 품질 체크

초기 MVP에서는 실제 CMS에 반영하지 않고, 수정안 diff와 Markdown 초안을 생성한다.

5.6 Technical SEO Agent

기술 SEO 이슈를 진단하고 우선순위를 정한다.

점검 항목:

* HTTP status code
* redirect chain
* canonical 누락/충돌
* noindex/nofollow
* robots.txt 차단 여부
* sitemap 포함 여부
* title/meta 누락
* h1 누락 또는 중복
* duplicate title/meta
* 이미지 alt 누락
* internal link depth
* broken links
* mobile friendliness
* PageSpeed/Core Web Vitals
* JS rendering risk
* pagination risk
* URL parameter risk

출력은 단순 오류 리스트가 아니라 impact_score, effort_score, priority, owner, recommended_action을 포함해야 한다.

5.7 Structured Data Agent

페이지 유형별 구조화 데이터 적용 후보를 판단한다.

페이지 유형:

* Product page
* Category page
* Article page
* FAQ page
* Review page
* How-to guide
* Organization/Brand page
* Local business page
* Breadcrumb

역할:

* 현재 structured data 존재 여부 확인
* 적용 가능한 schema type 추천
* 필수/권장 property 누락 확인
* Product, Offer, Review, AggregateRating, Breadcrumb 등 후보 생성
* JSON-LD 초안 생성
* Rich Results Test 대상 URL 목록 생성
* 구조화 데이터 변경은 승인 후 개발 요청으로 넘김

5.8 Internal Linking Agent

사이트 내 연결 구조를 개선하는 Agent다.

역할:

* 중요 페이지의 internal link depth 확인
* traffic은 많지만 전환 페이지로 연결되지 않는 콘텐츠 탐지
* 제품/카테고리/구매가이드/FAQ 간 연결 후보 생성
* anchor text 추천
* orphan page 탐지
* topic cluster 단위 hub-spoke 구조 추천
* Knowledge Atlas 또는 제품 지식과 연결 가능한 페이지 제안

5.9 GEO / Answer Engine Agent

AI 검색과 답변형 검색에 대응하는 Agent다.

역할:

* 브랜드/제품 관련 질문형 query cluster 생성
* AI가 답변하기 쉬운 명확한 문장 구조 제안
* 제품 비교, 구매 기준, 장단점, FAQ, 근거 기반 설명 생성
* Brand Answer 콘텐츠 브리프 생성
* AI 답변에 인용되기 쉬운 source-friendly page 구조 제안
* llms.txt, sitemap, structured data, canonical, author/source 신뢰도 점검 항목 생성
* ChatGPT/Perplexity/Gemini 등 외부 답변 결과를 수동 또는 mock snapshot으로 저장
* AI Answer Share of Voice를 추적할 수 있는 데이터 구조 설계

5.10 Experiment & Measurement Agent

SEO 개선안의 성과를 측정하는 Agent다.

역할:

* 개선 전 baseline 저장
* title/meta 변경 전후 CTR 비교
* 콘텐츠 개선 전후 impressions/clicks/position 변화 분석
* GA4 conversion/revenue 영향 분석
* 변경 후 7일/14일/28일 단위 성과 추적
* 성공/실패 원인 기록
* 추천 rule 개선을 위한 learning log 생성

5.11 Governance & Brand Safety Agent

SEO 추천이 브랜드, 법무, 품질 기준을 위반하지 않는지 점검한다.

점검 항목:

* 과장 표현
* 허위 성능 주장
* 경쟁사 비방
* 의료/금융/법률성 고위험 표현
* 개인정보 포함 여부
* 저작권 위험
* 키워드 스터핑
* AI 생성 티가 나는 저품질 문장
* 브랜드 톤앤매너 위반
* 승인 없이 발행될 수 없는 액션 여부

⸻

6. 핵심 기능

6.1 SEO Dashboard

대시보드는 다음 항목을 보여준다.

* Organic clicks
* Organic impressions
* Organic CTR
* Average position
* Non-brand clicks
* Brand clicks
* Top 3 query count
* Top 10 query count
* Page 2 opportunity count
* Low CTR opportunity count
* Declining page count
* Technical issue count
* Index issue count
* PageSpeed risk page count
* Content brief count
* Approval pending count
* SEO revenue 또는 organic conversion

화면 구성:

1. Executive Summary
2. Opportunity Matrix
3. Query Cluster View
4. Landing Page Performance
5. Technical SEO Risk
6. Content Brief Queue
7. GEO/AI Search Readiness
8. Weekly Recommendations

⸻

6.2 Opportunity Matrix

기회는 다음 4개 축으로 분류한다.

유형	조건	추천 액션
High Impression / Low CTR	노출 많음, CTR 낮음	title/meta 개선
Page 2 to Page 1	평균 position 4~15	콘텐츠 보강, 내부 링크 강화
High Traffic / Low Conversion	클릭 많음, 전환 낮음	landing page 개선
Declining Content	최근 클릭/노출 하락	콘텐츠 업데이트, intent 재정렬
Cannibalization	동일 query에 여러 URL 경쟁	canonical/merge/internal link 조정
Technical Blocker	색인/속도/robots/canonical 문제	개발 요청
GEO Candidate	질문형/비교형/추천형 query	Q&A, 비교표, Brand Answer 콘텐츠

⸻

6.3 Content Brief Generator

Content Brief는 다음 구조로 생성한다.

{
  "brief_id": "brief_001",
  "target_url": "/refrigerators/best-refrigerator-guide",
  "primary_query_cluster": "냉장고 추천",
  "secondary_queries": ["4도어 냉장고 추천", "오브제 냉장고 장점", "가족용 냉장고 용량"],
  "search_intent": "commercial_investigation",
  "current_gap": [
    "용량 선택 기준이 부족함",
    "가족 구성원별 추천이 없음",
    "에너지 효율 비교 정보가 부족함"
  ],
  "recommended_sections": [
    "가족 구성원별 냉장고 용량 선택법",
    "4도어/양문형/상냉장 하냉동 비교",
    "2026년 냉장고 구매 체크리스트",
    "자주 묻는 질문"
  ],
  "title_options": [
    "2026 냉장고 추천: 가족 구성원별 용량과 타입 선택 가이드",
    "냉장고 구매 전 꼭 확인할 7가지 기준"
  ],
  "meta_description_options": [
    "가족 수, 용량, 설치 공간, 에너지 효율, 기능을 기준으로 냉장고 선택 방법을 정리했습니다."
  ],
  "internal_link_suggestions": [
    {
      "anchor_text": "오브제컬렉션 냉장고",
      "target_url": "/refrigerators/objet"
    }
  ],
  "structured_data_suggestions": ["FAQPage", "BreadcrumbList", "Product"],
  "expected_impact": "CTR improvement and long-tail query expansion",
  "confidence_score": 0.74,
  "risk_level": "low"
}

⸻

6.4 Recommendation Engine

모든 추천은 다음 schema를 따른다.

{
  "recommendation_id": "rec_001",
  "type": "content_update",
  "priority": "high",
  "target_url": "/example-page",
  "target_query_cluster": "냉장고 추천",
  "current_metric": {
    "impressions": 120000,
    "clicks": 1800,
    "ctr": 0.015,
    "position": 6.4
  },
  "problem": "노출은 높지만 CTR이 낮고 title이 검색 의도와 맞지 않음",
  "recommendation": "title과 meta description을 구매가이드형으로 개선",
  "expected_impact": "CTR uplift",
  "evidence": [
    "최근 28일 impressions 증가",
    "CTR이 site average보다 낮음",
    "position 4~8 구간"
  ],
  "required_approval": true,
  "owner": "content",
  "effort_score": 2,
  "impact_score": 4,
  "confidence_score": 0.78,
  "rollback_plan": "기존 title/meta를 version history에서 복구",
  "status": "pending_approval"
}

⸻

6.5 SEO Report Generator

주간 리포트는 Markdown으로 export한다.

구성:

1. 이번 주 Organic Search 요약
2. 주요 상승/하락 query
3. 주요 상승/하락 landing page
4. 신규 발견 기회
5. 기술 SEO 주요 이슈
6. Content Brief 생성 목록
7. 승인 대기 액션
8. 지난 개선안 성과
9. 다음 주 우선순위
10. 리더용 한 줄 요약

⸻

7. 기술 구조

초기 구현은 Performance Marketing Agent와 동일한 구조를 따른다.

* Frontend: Next.js App Router
* Language: TypeScript
* UI: Tailwind CSS + shadcn/ui
* Backend: Next.js API Routes
* DB: SQLite for MVP
* Production DB: PostgreSQL
* ORM: Prisma 또는 Drizzle
* Agent Runtime: custom lightweight orchestrator
* LLM Adapter: OpenAI-compatible interface
* Job Scheduler: cron-based worker
* Crawler: Playwright 또는 lightweight fetch parser
* Chart: Recharts
* Export: Markdown, CSV
* Test: Vitest

초기에는 실제 API 연결보다 mock data와 rule-based analysis를 우선한다. 실제 GSC/GA4/PageSpeed 연동은 connector interface가 안정된 뒤 feature flag로 연결한다.

⸻

8. 데이터 모델

8.1 sites

* id
* name
* domain
* search_console_property
* ga4_property_id
* sitemap_url
* robots_url
* created_at
* updated_at

8.2 urls

* id
* site_id
* url
* path
* page_type
* title
* meta_description
* h1
* canonical_url
* status_code
* is_indexable
* in_sitemap
* robots_allowed
* last_crawled_at

8.3 gsc_daily_metrics

* id
* site_id
* url_id
* query
* date
* device
* country
* clicks
* impressions
* ctr
* position

8.4 ga4_landing_metrics

* id
* site_id
* url_id
* date
* sessions
* engaged_sessions
* conversions
* revenue
* conversion_rate
* source
* medium

8.5 query_clusters

* id
* site_id
* name
* intent
* funnel_stage
* primary_query
* secondary_queries_json
* business_category
* priority_score

8.6 technical_audits

* id
* site_id
* url_id
* audit_type
* severity
* issue
* evidence
* recommended_action
* owner
* impact_score
* effort_score
* status
* created_at

8.7 pagespeed_audits

* id
* site_id
* url_id
* strategy
* performance_score
* accessibility_score
* best_practices_score
* seo_score
* lcp
* cls
* inp
* opportunities_json
* created_at

8.8 content_briefs

* id
* site_id
* target_url_id
* query_cluster_id
* title
* search_intent
* current_gap_json
* recommended_sections_json
* title_options_json
* meta_options_json
* internal_links_json
* structured_data_json
* status
* created_by_agent_run_id
* created_at

8.9 content_drafts

* id
* brief_id
* version
* draft_markdown
* diff_summary
* quality_score
* brand_safety_score
* status
* created_at

8.10 recommendations

* id
* site_id
* type
* priority
* target_url_id
* query_cluster_id
* problem
* recommendation
* evidence_json
* expected_impact
* confidence_score
* risk_level
* owner
* effort_score
* impact_score
* required_approval
* status
* rollback_plan
* created_at
* updated_at

8.11 experiments

* id
* recommendation_id
* target_url_id
* change_type
* baseline_start_date
* baseline_end_date
* experiment_start_date
* experiment_end_date
* baseline_metrics_json
* result_metrics_json
* outcome
* learning_summary

8.12 agent_runs

* id
* agent_name
* input_json
* output_json
* status
* error_message
* started_at
* completed_at

8.13 geo_answer_snapshots

* id
* site_id
* query
* platform
* answer_text
* mentioned_brand
* cited_urls_json
* competitors_json
* sentiment
* captured_at

8.14 knowledge_items

* id
* source_type
* source_id
* title
* summary
* content
* tags_json
* created_at

⸻

9. 핵심 Rule 설계

9.1 Low CTR Opportunity Rule

조건:

* impressions > site median
* position <= 10
* ctr < expected_ctr_by_position
* query intent가 브랜드/제품/구매 관련
* 최근 28일 데이터 존재

추천:

* title 개선
* meta description 개선
* structured data 적용 검토
* snippet 친화적 문장 추가
* FAQ 추가

⸻

9.2 Page 2 Opportunity Rule

조건:

* position >= 4 and position <= 15
* impressions 증가 추세
* target URL indexable
* technical blocker 없음
* 해당 query cluster의 business value 높음

추천:

* 콘텐츠 섹션 보강
* 내부 링크 추가
* anchor text 개선
* 관련 FAQ 추가
* 비교표/체크리스트 추가
* title과 h1 검색 의도 정렬

⸻

9.3 Declining Content Rule

조건:

* 최근 28일 clicks가 이전 28일 대비 20% 이상 감소
* position 하락 또는 CTR 하락
* 해당 page의 update age가 90일 이상
* 계절성 또는 프로모션 종료 여부 확인

추천:

* 콘텐츠 최신화
* outdated section 수정
* title/meta 재작성
* query intent 변화 반영
* 경쟁 페이지 분석 요청
* 내부 링크 재배치

⸻

9.4 Cannibalization Rule

조건:

* 동일 query가 2개 이상 URL에 노출
* URL별 position이 교차 변동
* primary URL이 명확하지 않음
* 유사 title/h1 존재

추천:

* canonical 검토
* 콘텐츠 통합
* 내부 링크 anchor 재정렬
* 한 URL을 primary landing page로 지정
* 중복 페이지의 목적 재정의

⸻

9.5 Technical Blocker Rule

조건:

* indexable false
* noindex 존재
* canonical이 다른 URL을 가리킴
* sitemap 누락
* robots 차단
* 4xx/5xx 발생
* redirect chain 2회 이상
* PageSpeed SEO score 낮음

추천:

* 개발 요청 ticket 생성
* owner 지정
* 영향 URL 수 계산
* business impact 기준 우선순위 지정

⸻

9.6 GEO Candidate Rule

조건:

* query가 질문형, 비교형, 추천형, 구매 기준형
* 제품/브랜드 관련성이 높음
* GSC에서 long-tail impressions 증가
* 검색 결과에서 zero-click 가능성이 높음
* 내부 콘텐츠에 명확한 답변 구조가 부족함

추천:

* Brand Answer 콘텐츠 생성
* FAQ 섹션 추가
* 비교표 추가
* 제품 속성 데이터 명확화
* 출처/근거/작성자/업데이트일 표시
* structured data 적용
* Knowledge Atlas 연결

⸻

10. 화면 설계

10.1 /seo

SEO Executive Dashboard

구성:

* KPI cards
* Organic trend chart
* Opportunity Matrix
* Top Recommendations
* Technical Risk Summary
* GEO Readiness Summary

10.2 /seo/queries

Query Opportunity 화면

구성:

* Query table
* Cluster filter
* Intent filter
* Impression/CTR/Position scatter
* Opportunity score
* Generate Brief button

10.3 /seo/pages

Landing Page 화면

구성:

* URL list
* SEO metrics
* GA4 metrics
* Technical status
* Content gap
* Recommendations

10.4 /seo/briefs

Content Brief Queue

구성:

* Brief status
* Target query
* Target URL
* Recommended sections
* Title/meta options
* Approval status

10.5 /seo/technical

Technical SEO Audit

구성:

* Issue summary
* Severity filter
* URL detail
* Owner
* Status
* Create dev ticket mock action

10.6 /seo/geo

GEO / AI Search Readiness

구성:

* Question query clusters
* Brand Answer candidates
* AI answer snapshots
* Mention/citation tracking
* GEO content brief generator

10.7 /seo/reports

SEO Report Export

구성:

* Weekly report
* Monthly report
* Executive summary
* Markdown export
* CSV export

⸻

11. API Connector 설계

공통 interface를 먼저 만든다.

export interface SEOConnector {
  getSiteProperties(): Promise<SiteProperty[]>;
  getSearchAnalytics(input: SearchAnalyticsInput): Promise<SearchAnalyticsRow[]>;
  inspectUrl(input: UrlInspectionInput): Promise<UrlInspectionResult>;
  getSitemaps(siteUrl: string): Promise<SitemapResult[]>;
}

GA4 connector:

export interface AnalyticsConnector {
  getLandingPageMetrics(input: LandingPageMetricInput): Promise<LandingPageMetricRow[]>;
  getOrganicConversions(input: OrganicConversionInput): Promise<OrganicConversionRow[]>;
}

PageSpeed connector:

export interface PageSpeedConnector {
  runAudit(input: PageSpeedAuditInput): Promise<PageSpeedAuditResult>;
}

Crawler connector:

export interface SiteCrawler {
  crawlUrl(url: string): Promise<CrawledPage>;
  crawlSitemap(sitemapUrl: string): Promise<SitemapUrl[]>;
  checkRobots(domain: string, path: string): Promise<RobotsResult>;
}

CMS connector는 초기에는 mock으로 둔다.

export interface CMSConnector {
  createDraft(input: ContentDraftInput): Promise<CMSDraftResult>;
  updateMetadataDraft(input: MetadataDraftInput): Promise<CMSDraftResult>;
}

실제 CMS 반영은 MVP 이후로 미룬다.

⸻

12. LLM Prompt 구조

12.1 System Prompt

You are an SEO Marketing AI Agent.
You analyze organic search performance, search intent, content gaps, technical SEO issues, and GEO readiness.
Always distinguish facts from assumptions.
Never recommend manipulative or spammy SEO tactics.
Do not publish, modify, or request indexing without human approval.
Every recommendation must include evidence, expected impact, confidence score, risk level, and rollback plan.
Prioritize business impact, search intent fit, and user helpfulness.

12.2 Query Opportunity Prompt

입력:

* query
* url
* impressions
* clicks
* ctr
* position
* device
* landing page title/meta/h1
* GA4 conversion data
* site average CTR
* previous period metrics

출력:

* opportunity type
* problem
* likely cause
* recommended action
* evidence
* expected impact
* confidence score
* risk level

12.3 Content Brief Prompt

입력:

* target query cluster
* search intent
* current page content summary
* product knowledge
* competitor/benchmark notes
* brand tone
* target user
* conversion goal

출력:

* content objective
* target audience
* primary/secondary queries
* recommended outline
* title options
* meta description options
* FAQ
* internal link suggestions
* structured data suggestions
* quality checklist

12.4 GEO Brief Prompt

입력:

* question query
* brand/product knowledge
* current page content
* desired answer
* source evidence
* competing answer patterns

출력:

* answer-first content section
* concise factual answer
* supporting explanation
* comparison table
* FAQ
* source-friendly statements
* structured data suggestions
* Knowledge Atlas entities to connect

⸻

13. Codex 작업 지시

13.1 첫 번째 PR: SEO MVP Foundation

Codex는 다음을 구현한다.

1. Next.js + TypeScript 기반 /seo 라우트 생성
2. SQLite + Prisma schema 생성
3. SEO 관련 seed data 생성
4. SEO Dashboard UI 구현
5. Query Opportunity 화면 구현
6. Landing Page 화면 구현
7. Recommendations 화면 구현
8. Agent Runs 화면 구현
9. mock GSC/GA4/PageSpeed data loader 구현
10. rule-based Query Opportunity Agent 구현

실제 외부 API 호출은 하지 않는다. 모든 connector는 interface와 mock implementation만 만든다.

Acceptance Criteria:

* /seo 접속 시 KPI 카드와 trend chart가 보인다.
* seed data 기반으로 query/page 성과가 표시된다.
* Query Opportunity Agent 실행 시 recommendations가 생성된다.
* recommendations에는 type, target_url, evidence, confidence_score, risk_level, approval status가 포함된다.
* agent_runs에 실행 로그가 저장된다.

⸻

13.2 두 번째 PR: Content Brief & Technical SEO

Codex는 다음을 구현한다.

1. /seo/briefs 화면 구현
2. Content Brief 생성 기능 구현
3. Title/Meta 개선안 생성 기능 구현
4. /seo/technical 화면 구현
5. crawler mock 구현
6. technical_audits 테이블 저장
7. structured data recommendation 생성
8. internal link recommendation 생성

Acceptance Criteria:

* query opportunity에서 “Generate Brief” 클릭 시 content brief가 생성된다.
* brief에는 target query, search intent, recommended sections, title options, meta options가 포함된다.
* technical audit 화면에서 severity별 이슈를 볼 수 있다.
* technical issue는 impact_score와 effort_score 기준으로 정렬된다.
* structured data 추천이 URL page_type에 따라 생성된다.

⸻

13.3 세 번째 PR: GEO / AI Search Agent

Codex는 다음을 구현한다.

1. /seo/geo 화면 구현
2. question query cluster 생성
3. Brand Answer brief 생성
4. AI answer snapshot mock table 구현
5. brand mention/citation tracking UI 구현
6. llms.txt readiness checklist 구현
7. Knowledge item 저장 기능 구현

Acceptance Criteria:

* 질문형 query cluster가 자동 분류된다.
* Brand Answer brief가 생성된다.
* AI answer snapshot을 수동으로 등록할 수 있다.
* 브랜드 mention 여부와 cited URL을 저장할 수 있다.
* GEO readiness score가 표시된다.

⸻

13.4 네 번째 PR: Report & Measurement

Codex는 다음을 구현한다.

1. /seo/reports 화면 구현
2. Weekly SEO Report Markdown export
3. Recommendation approval workflow
4. Experiment baseline 저장
5. 변경 전후 성과 비교 mock
6. learning_summary 저장

Acceptance Criteria:

* 주간 SEO 리포트를 Markdown으로 export할 수 있다.
* recommendation을 approve/reject 할 수 있다.
* 승인된 recommendation은 executed가 아니라 approved 상태까지만 변경된다.
* experiment에는 baseline metrics와 result metrics가 저장된다.
* learning summary가 knowledge_items에 저장된다.

⸻

13.5 다섯 번째 PR: Real Connector Skeleton

Codex는 다음을 구현한다.

1. Google Search Console connector skeleton
2. GA4 Data API connector skeleton
3. PageSpeed Insights connector skeleton
4. OAuth/env credential 구조
5. feature flag 기반 real API on/off
6. dry-run mode
7. API error handling
8. rate limit handling
9. connector test mock

Acceptance Criteria:

* .env.example에 필요한 환경변수가 정의된다.
* real connector는 기본 비활성화 상태다.
* ENABLE_REAL_CONNECTORS=true일 때만 실제 호출 준비가 된다.
* 실제 CMS 수정/발행 기능은 구현하지 않는다.
* API 실패 시 agent_runs에 error가 기록된다.

⸻

14. 파일 구조 제안

/src
  /app
    /seo
      page.tsx
      /queries
        page.tsx
      /pages
        page.tsx
      /briefs
        page.tsx
      /technical
        page.tsx
      /geo
        page.tsx
      /reports
        page.tsx
    /api
      /seo
        /run-diagnosis
        /generate-brief
        /run-technical-audit
        /generate-geo-brief
        /approve-recommendation
        /export-report
  /components
    /seo
      SeoKpiCards.tsx
      OrganicTrendChart.tsx
      OpportunityMatrix.tsx
      QueryTable.tsx
      LandingPageTable.tsx
      RecommendationCard.tsx
      ContentBriefCard.tsx
      TechnicalIssueTable.tsx
      GeoReadinessPanel.tsx
      SeoReportPreview.tsx
  /lib
    /agents
      seo-orchestrator.ts
      query-opportunity-agent.ts
      content-brief-agent.ts
      seo-editor-agent.ts
      technical-seo-agent.ts
      structured-data-agent.ts
      internal-link-agent.ts
      geo-answer-agent.ts
      seo-reporting-agent.ts
      governance-agent.ts
    /connectors
      search-console-connector.ts
      ga4-connector.ts
      pagespeed-connector.ts
      crawler-connector.ts
      cms-connector.ts
      mock-search-console.ts
      mock-ga4.ts
      mock-pagespeed.ts
    /rules
      low-ctr-rule.ts
      page-two-rule.ts
      declining-content-rule.ts
      cannibalization-rule.ts
      technical-blocker-rule.ts
      geo-candidate-rule.ts
    /llm
      llm-client.ts
      prompts.ts
      schemas.ts
    /reports
      weekly-seo-report.ts
      markdown-export.ts
/prisma
  schema.prisma
  seed.ts
/docs
  seo-agent-plan.md
  seo-agent-architecture.md
  seo-agent-prd.md
  seo-agent-prompts.md

⸻

15. 성공 기준

MVP 성공 기준은 다음과 같다.

1. SEO 담당자가 매일 Search Console을 수동으로 보지 않아도 주요 이슈를 알 수 있다.
2. Query Opportunity가 자동으로 분류된다.
3. 우선순위 높은 콘텐츠 개선 후보가 자동 생성된다.
4. Content Brief가 실무자가 바로 작업 가능한 수준으로 생성된다.
5. 기술 SEO 이슈가 비즈니스 영향도 기준으로 정렬된다.
6. SEO 추천은 항상 근거와 confidence score를 포함한다.
7. 승인 없는 발행 또는 사이트 변경이 발생하지 않는다.
8. 주간 리포트가 자동 생성된다.
9. 개선 결과가 experiment와 knowledge item으로 축적된다.
10. GEO/AI Search 대응 후보가 별도 관리된다.

⸻

16. 설계 원칙

1. SEO Agent는 콘텐츠를 대량 생산하는 도구가 아니라 검색 성장 루프를 자동화하는 도구다.
2. 모든 추천은 데이터 근거를 가져야 한다.
3. 자동 실행보다 Human Approval을 우선한다.
4. Black-hat SEO, 자동 백링크, 스팸성 콘텐츠 생성을 금지한다.
5. Query가 아니라 Intent Cluster 단위로 판단한다.
6. SEO 성과는 clicks만이 아니라 conversion/revenue와 연결한다.
7. 기술 SEO 이슈는 심각도보다 비즈니스 영향도 기준으로 우선순위화한다.
8. GEO 대응은 별도 기능이 아니라 콘텐츠와 지식 구조 개선의 확장으로 본다.
9. Agent 실행 결과는 모두 추적 가능해야 한다.
10. 실행 결과와 학습 내용은 Knowledge Base에 축적한다.

⸻

17. 향후 확장

MVP 이후 확장 방향은 다음과 같다.

1. 실제 Google Search Console API 연동
2. 실제 GA4 Data API 연동
3. 실제 PageSpeed Insights API 연동
4. CMS draft 생성 연동
5. Jira/Asana/Linear 개발 요청 ticket 생성
6. Slack/Teams SEO alert
7. 경쟁사 SERP snapshot 수집
8. 외부 SEO tool API 연동
9. Product Feed 연동
10. Knowledge Atlas 연동
11. Brand Answer Engine 연동
12. AI Answer Share of Voice 추적
13. 다국가/다국어 SEO 관리
14. 제품 카탈로그 기반 자동 SEO brief
15. 내부 링크 자동 추천 및 CMS 반영
16. SEO experiment 자동 판정
17. AgentOne 내부 업무 Agent와 통합

⸻

18. Codex에게 전달할 핵심 한 줄

SEO Agent One은 “AI 콘텐츠 생성기”가 아니라, Search Console·GA4·PageSpeed·사이트 크롤링·제품 지식을 연결해 SEO/GEO 성장 기회를 찾고, 사람이 승인 가능한 개선안과 콘텐츠 브리프를 생성하며, 실행 결과를 지식으로 축적하는 Agent Team이다.
