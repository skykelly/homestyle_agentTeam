"""
Claude tool definitions for the Korea Performance Marketing Agent.
Each tool maps to a callable in tool_handlers.py.
"""

TOOLS = [
    {
        "name": "get_campaign_performance",
        "description": (
            "광고 캠페인 성과 데이터를 조회합니다. "
            "네이버, 카카오, 쿠팡, 메타, 유튜브 등 한국 주요 광고 플랫폼의 "
            "ROAS, CPC, CTR, CVR, 전환수, 비용 등 KPI를 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": [
                        "naver_search",
                        "naver_shopping",
                        "kakao_moment",
                        "kakao_display",
                        "coupang_ads",
                        "meta_instagram",
                        "youtube_ads",
                        "all",
                    ],
                    "description": "조회할 광고 플랫폼. 'all'이면 전체 플랫폼 합산.",
                },
                "start_date": {
                    "type": "string",
                    "description": "조회 시작일 (YYYY-MM-DD 형식)",
                },
                "end_date": {
                    "type": "string",
                    "description": "조회 종료일 (YYYY-MM-DD 형식)",
                },
                "campaign_id": {
                    "type": "string",
                    "description": "특정 캠페인 ID (선택사항). 미입력시 전체 캠페인.",
                },
            },
            "required": ["platform", "start_date", "end_date"],
        },
    },
    {
        "name": "get_keyword_analysis",
        "description": (
            "네이버 키워드 분석을 수행합니다. "
            "검색량, 경쟁도, 예상 CPC, 시즌 트렌드를 반환합니다. "
            "한국 시장 특화 키워드 인사이트 제공."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "분석할 키워드 목록 (최대 100개)",
                },
                "category": {
                    "type": "string",
                    "description": "상품/서비스 카테고리 (예: 패션, 뷰티, 식품, 가전)",
                },
                "include_related": {
                    "type": "boolean",
                    "description": "연관 키워드 포함 여부",
                    "default": True,
                },
            },
            "required": ["keywords"],
        },
    },
    {
        "name": "optimize_budget_allocation",
        "description": (
            "한국 시장 데이터 기반으로 광고 예산을 최적 배분합니다. "
            "플랫폼별 ROAS, 카테고리 벤치마크, 시즌 이벤트를 고려하여 "
            "예산 배분 권고안을 생성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "total_budget_krw": {
                    "type": "integer",
                    "description": "총 광고 예산 (원화, KRW)",
                },
                "category": {
                    "type": "string",
                    "description": "주요 상품/서비스 카테고리",
                },
                "objective": {
                    "type": "string",
                    "enum": ["roas_maximize", "cpa_minimize", "awareness", "traffic"],
                    "description": "캠페인 목표",
                },
                "current_month": {
                    "type": "integer",
                    "description": "현재 월 (1-12)",
                },
                "active_platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "현재 운영 중인 플랫폼 목록",
                },
            },
            "required": ["total_budget_krw", "category", "objective", "current_month"],
        },
    },
    {
        "name": "analyze_competitors",
        "description": (
            "한국 시장 경쟁사 광고 분석을 수행합니다. "
            "경쟁사 추정 광고 지출, 주요 키워드, 크리에이티브 전략을 분석합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "분석 대상 브랜드명 (한글/영문)",
                },
                "category": {
                    "type": "string",
                    "description": "경쟁 카테고리",
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "분석할 플랫폼 목록",
                },
            },
            "required": ["brand_name", "category"],
        },
    },
    {
        "name": "generate_ad_copy",
        "description": (
            "한국 시장에 최적화된 광고 문구를 생성합니다. "
            "네이버 검색광고, 카카오 디스플레이, 쿠팡 광고 등 "
            "플랫폼별 규격에 맞는 헤드라인·설명문·CTA를 생성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "상품/서비스명",
                },
                "key_features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "주요 특장점 목록",
                },
                "target_audience": {
                    "type": "string",
                    "description": "타겟 오디언스 설명 (예: 30대 여성, 직장인, 학부모)",
                },
                "platform": {
                    "type": "string",
                    "enum": [
                        "naver_search",
                        "naver_shopping",
                        "kakao_moment",
                        "meta_instagram",
                        "youtube_ads",
                        "coupang_ads",
                    ],
                    "description": "광고 플랫폼",
                },
                "promotion": {
                    "type": "string",
                    "description": "프로모션 내용 (예: 20% 할인, 무료배송, 1+1)",
                },
                "tone": {
                    "type": "string",
                    "enum": ["formal", "casual", "emotional", "informational"],
                    "description": "광고 톤앤매너",
                    "default": "casual",
                },
                "count": {
                    "type": "integer",
                    "description": "생성할 광고 문구 세트 수",
                    "default": 3,
                },
            },
            "required": ["product_name", "key_features", "target_audience", "platform"],
        },
    },
    {
        "name": "get_market_events",
        "description": (
            "한국 시장 주요 이벤트 및 쇼핑 시즌 정보를 반환합니다. "
            "설날, 추석, 어린이날, 블랙프라이데이 등 "
            "광고 집행 시기와 예산 증감 권장사항을 포함합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "integer",
                    "description": "조회 월 (1-12). 미입력시 현재 월 기준.",
                },
                "lookahead_months": {
                    "type": "integer",
                    "description": "몇 개월 앞까지 조회할지 (기본값 2)",
                    "default": 2,
                },
            },
            "required": [],
        },
    },
    {
        "name": "create_campaign_plan",
        "description": (
            "한국 시장 맞춤형 캠페인 플랜을 생성합니다. "
            "목표 KPI, 예산 배분, 플랫폼 전략, 크리에이티브 방향, "
            "주차별 실행 계획을 포함한 종합 캠페인 계획서를 작성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "브랜드명",
                },
                "product_category": {
                    "type": "string",
                    "description": "상품 카테고리",
                },
                "campaign_objective": {
                    "type": "string",
                    "enum": ["brand_awareness", "sales_conversion", "app_install", "lead_generation"],
                    "description": "캠페인 목표",
                },
                "total_budget_krw": {
                    "type": "integer",
                    "description": "총 캠페인 예산 (KRW)",
                },
                "campaign_period_weeks": {
                    "type": "integer",
                    "description": "캠페인 기간 (주 단위)",
                },
                "target_audience": {
                    "type": "string",
                    "description": "타겟 오디언스",
                },
                "key_messages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "핵심 메시지 목록",
                },
            },
            "required": [
                "brand_name",
                "product_category",
                "campaign_objective",
                "total_budget_krw",
                "campaign_period_weeks",
                "target_audience",
            ],
        },
    },
    {
        "name": "generate_performance_report",
        "description": (
            "광고 성과 보고서를 생성합니다. "
            "플랫폼별 성과, KPI 달성률, 인사이트, "
            "다음 기간 최적화 권장사항을 포함한 보고서를 작성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "report_period": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly"],
                    "description": "보고서 기간",
                },
                "start_date": {
                    "type": "string",
                    "description": "보고 시작일 (YYYY-MM-DD)",
                },
                "end_date": {
                    "type": "string",
                    "description": "보고 종료일 (YYYY-MM-DD)",
                },
                "include_recommendations": {
                    "type": "boolean",
                    "description": "최적화 권장사항 포함 여부",
                    "default": True,
                },
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "포함할 플랫폼 목록",
                },
            },
            "required": ["report_period", "start_date", "end_date"],
        },
    },
    {
        "name": "ab_test_analysis",
        "description": (
            "A/B 테스트 결과를 분석하고 통계적 유의성을 검증합니다. "
            "광고 소재, 랜딩페이지, 타겟팅 등 다양한 변수의 "
            "테스트 결과를 분석하여 최적안을 추천합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "test_name": {
                    "type": "string",
                    "description": "테스트명",
                },
                "variant_a": {
                    "type": "object",
                    "description": "변형 A 데이터 {impressions, clicks, conversions, spend_krw}",
                },
                "variant_b": {
                    "type": "object",
                    "description": "변형 B 데이터 {impressions, clicks, conversions, spend_krw}",
                },
                "confidence_level": {
                    "type": "number",
                    "description": "신뢰 수준 (0.90, 0.95, 0.99)",
                    "default": 0.95,
                },
                "primary_metric": {
                    "type": "string",
                    "enum": ["ctr", "cvr", "cpa", "roas"],
                    "description": "주요 평가 지표",
                },
            },
            "required": ["test_name", "variant_a", "variant_b", "primary_metric"],
        },
    },
    # ── Phase 2: Recommendation & Approval tools ────────────────────────────
    {
        "name": "run_diagnosis",
        "description": (
            "캠페인 성과 진단을 실행합니다 (Phase 2). "
            "규칙 엔진(rule-based)으로 성과 이슈를 탐지하고 "
            "구조화된 권고사항(Recommendation)을 자동 생성합니다. "
            "고위험 액션은 자동으로 승인 대기(pending_approval) 상태로 전환됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "진단할 광고 플랫폼 (예: naver_search, kakao_moment)",
                },
                "campaign": {
                    "type": "string",
                    "description": "캠페인명 또는 ID",
                },
                "category": {
                    "type": "string",
                    "description": "상품 카테고리 (예: 뷰티, 패션, 식품)",
                },
                "metrics": {
                    "type": "object",
                    "description": (
                        "현재 성과 지표: roas(float), cpa_krw(int), ctr_pct(float), "
                        "cvr_pct(float), budget_utilization(0-1), days_running(int), "
                        "frequency(float, 선택), bounce_rate_pct(float, 선택), "
                        "page_load_seconds(float, 선택), cart_abandon_rate_pct(float, 선택)"
                    ),
                },
                "auto_submit": {
                    "type": "boolean",
                    "description": "True이면 권고사항을 즉시 승인 워크플로우에 제출",
                    "default": True,
                },
            },
            "required": ["platform", "campaign", "category", "metrics"],
        },
    },
    {
        "name": "list_recommendations",
        "description": (
            "생성된 권고사항 목록을 조회합니다. "
            "상태(draft/pending_approval/approved/rejected/executed/rolled_back)별 필터링 가능."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["draft", "pending_approval", "approved", "rejected", "executed", "failed", "rolled_back"],
                    "description": "필터링할 상태 (미입력 시 전체)",
                },
                "platform": {
                    "type": "string",
                    "description": "필터링할 플랫폼 (선택사항)",
                },
                "limit": {
                    "type": "integer",
                    "description": "최대 조회 건수 (기본값 20)",
                    "default": 20,
                },
            },
            "required": [],
        },
    },
    {
        "name": "approve_recommendation",
        "description": (
            "승인 대기 중인 권고사항을 승인합니다 (Phase 2). "
            "승인 후 status가 approved로 변경되어 실행 가능 상태가 됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "recommendation_id": {
                    "type": "string",
                    "description": "승인할 권고사항 ID",
                },
                "approver": {
                    "type": "string",
                    "description": "승인자 이름 또는 ID",
                },
                "notes": {
                    "type": "string",
                    "description": "승인 메모 (선택사항)",
                },
            },
            "required": ["recommendation_id", "approver"],
        },
    },
    {
        "name": "reject_recommendation",
        "description": (
            "승인 대기 중인 권고사항을 거절합니다 (Phase 2). "
            "거절 사유와 함께 rejected 상태로 전환됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "recommendation_id": {
                    "type": "string",
                    "description": "거절할 권고사항 ID",
                },
                "approver": {
                    "type": "string",
                    "description": "거절 처리자 이름 또는 ID",
                },
                "reason": {
                    "type": "string",
                    "description": "거절 사유 (필수)",
                },
            },
            "required": ["recommendation_id", "approver", "reason"],
        },
    },
    {
        "name": "get_approval_summary",
        "description": (
            "전체 권고사항 승인 현황을 조회합니다 (Phase 2). "
            "상태별 건수, 승인 대기 항목 목록, 롤백 가능 항목을 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    # ── Phase 3: SEO tools ──────────────────────────────────────────────────
    {
        "name": "get_seo_overview",
        "description": (
            "SEO 사이트 개요를 조회합니다 (Phase 3). "
            "Google Search Console 28일 지표(클릭, 노출, CTR, 포지션)와 "
            "오가닉 매출 현황을 전기 대비 비교하여 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "site_url": {
                    "type": "string",
                    "description": "조회할 사이트 URL (예: https://beautylab.co.kr)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "run_seo_diagnosis",
        "description": (
            "SEO 진단을 실행합니다 (Phase 3). "
            "6가지 SEO 규칙(Low CTR, Page2 기회, 콘텐츠 노후화, 카니발라이제이션, "
            "기술적 이슈, GEO 후보)을 자동으로 점검하고 우선순위화된 권고사항을 생성합니다. "
            "LLM 분석을 통한 콘텐츠 브리프도 생성됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "site_url": {
                    "type": "string",
                    "description": "진단할 사이트 URL",
                },
                "min_impressions": {
                    "type": "integer",
                    "description": "분석 대상 최소 노출 수 (기본값 3000)",
                    "default": 3000,
                },
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 전략 분석 포함 여부 (기본값 True)",
                    "default": True,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_seo_query_opportunities",
        "description": (
            "SEO 쿼리 기회를 조회합니다 (Phase 3). "
            "Low CTR, Page 2 진입 기회, 카니발라이제이션, GEO 후보 등 "
            "유형별로 필터링하여 검색 쿼리 개선 기회를 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "opportunity_type": {
                    "type": "string",
                    "enum": ["ctr_improvement", "ranking_boost", "cannibalization_fix",
                             "geo_candidate", "content_refresh", "all"],
                    "description": "조회할 기회 유형. 'all'이면 전체.",
                    "default": "all",
                },
                "min_impressions": {
                    "type": "integer",
                    "description": "최소 노출 수 필터 (기본값 3000)",
                    "default": 3000,
                },
                "limit": {
                    "type": "integer",
                    "description": "최대 반환 건수 (기본값 10)",
                    "default": 10,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_technical_audit",
        "description": (
            "기술적 SEO 감사 결과를 조회합니다 (Phase 3). "
            "사이트 크롤 데이터 기반으로 H1 누락, 메타 설명 누락, "
            "구조화된 데이터 부재, 사이트맵 오류, 리다이렉트 체인 등을 점검합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "page_type": {
                    "type": "string",
                    "enum": ["product", "category", "article", "faq", "home", "all"],
                    "description": "점검할 페이지 유형. 'all'이면 전체.",
                    "default": "all",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_pagespeed_summary",
        "description": (
            "PageSpeed 성과 요약을 조회합니다 (Phase 3). "
            "Core Web Vitals(LCP, CLS, INP) 및 성능 점수를 페이지별로 반환합니다. "
            "모바일/데스크톱 전략별 조회 가능."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "enum": ["mobile", "desktop", "both"],
                    "description": "조회할 전략 (기본값 mobile)",
                    "default": "mobile",
                },
                "url": {
                    "type": "string",
                    "description": "특정 URL 조회 (선택사항). 미입력 시 전체 페이지.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "generate_content_brief",
        "description": (
            "특정 URL의 콘텐츠 브리프를 생성합니다 (Phase 3). "
            "SEO 최적화를 위한 제목 태그 옵션, 메타 설명 옵션, "
            "추천 콘텐츠 섹션, 내부 링크 제안, 구조화 데이터 권장사항을 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "콘텐츠 브리프를 생성할 URL",
                },
                "target_query": {
                    "type": "string",
                    "description": "주요 타겟 검색 쿼리",
                },
                "current_position": {
                    "type": "number",
                    "description": "현재 검색 순위 포지션",
                },
            },
            "required": ["url", "target_query"],
        },
    },
    {
        "name": "run_seo_pipeline",
        "description": (
            "SEO 전체 파이프라인을 병렬로 실행합니다 (Phase 4-6). "
            "진단, 구조화 데이터, 내부 링크, 실험 베이스라인을 동시에 실행하고 "
            "콘텐츠 브리프 생성 후 주간 리포트를 생성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "site_url": {
                    "type": "string",
                    "description": "분석할 사이트 URL (기본값: https://beautylab.co.kr)",
                },
                "skip_llm_in_parallel": {
                    "type": "boolean",
                    "description": "병렬 실행 중 LLM 호출 건너뜀 (속도 최적화, 기본값 True)",
                    "default": True,
                },
            },
            "required": [],
        },
    },
    {
        "name": "run_content_briefs",
        "description": (
            "SEO 기회 기반 콘텐츠 브리프를 생성합니다 (Phase 4). "
            "상위 CTR 기회와 Page 2 기회에 대해 콘텐츠 작성자가 바로 실행 가능한 "
            "구조화된 브리프를 생성합니다. 제목, 메타, H1, FAQ, 내부 링크 포함."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_briefs": {
                    "type": "integer",
                    "description": "생성할 최대 브리프 수 (기본값 5)",
                    "default": 5,
                },
                "opportunity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "대상 기회 유형 (기본값: ['ctr_improvement', 'ranking_boost'])",
                },
            },
            "required": [],
        },
    },
    {
        "name": "run_structured_data_audit",
        "description": (
            "구조화 데이터(Schema.org) 감사 및 JSON-LD 초안을 생성합니다 (Phase 4). "
            "페이지 유형별로 적용 가능한 스키마 타입, 누락 속성, "
            "리치 스니펫 획득 가능성을 평가하고 바로 사용 가능한 JSON-LD 코드를 제공합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "run_internal_link_analysis",
        "description": (
            "내부 링크 구조를 분석하고 개선안을 생성합니다 (Phase 4). "
            "Hub-Spoke 토픽 클러스터 구조, 고립 페이지 구조 탈출, "
            "콘텐츠→제품 전환 경로 강화, FAQ 교차 링크 등을 권고합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "create_experiment_baselines",
        "description": (
            "SEO 실험 베이스라인을 설정합니다 (Phase 6). "
            "변경 전 현재 지표를 캡처하여 실험 추적의 기준점을 설정합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "top_n": {
                    "type": "integer",
                    "description": "실험 설정할 상위 기회 수 (기본값 5)",
                    "default": 5,
                },
            },
            "required": [],
        },
    },
    {
        "name": "analyze_experiment_results",
        "description": (
            "SEO 실험 결과를 분석하고 학습 내용을 저장합니다 (Phase 6). "
            "변경 전후 지표를 비교하고 성공/실패 원인을 분석합니다. "
            "학습 내용은 Knowledge Base에 자동 저장됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "generate_seo_report",
        "description": (
            "SEO 주간 리포트를 생성합니다 (Phase 6). "
            "Organic Search 요약, 기회 매트릭스, 기술 이슈, 콘텐츠 브리프 대기열, "
            "실험 결과, 지식 베이스 현황, 다음 주 우선순위를 포함한 "
            "Markdown 리포트를 생성하고 파일로 저장합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "report_date": {
                    "type": "string",
                    "description": "리포트 날짜 (YYYY-MM-DD). 미입력 시 오늘.",
                },
                "export_markdown": {
                    "type": "boolean",
                    "description": "Markdown 파일 저장 여부 (기본값 True)",
                    "default": True,
                },
            },
            "required": [],
        },
    },
    {
        "name": "list_content_briefs",
        "description": (
            "생성된 콘텐츠 브리프 목록을 조회합니다 (Phase 4-6). "
            "상태(draft/approved/in_progress/published), URL별 필터링 가능."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["draft", "approved", "in_progress", "published"],
                    "description": "필터링할 상태 (미입력 시 전체)",
                },
                "url": {
                    "type": "string",
                    "description": "특정 URL 필터 (선택사항)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_knowledge_items",
        "description": (
            "Knowledge Base 항목을 조회합니다 (Phase 6). "
            "실험 학습, 규칙 탐지, LLM 인사이트 등 축적된 SEO 지식을 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_type": {
                    "type": "string",
                    "enum": ["experiment", "rule_hit", "llm_insight", "manual"],
                    "description": "소스 유형 필터 (선택사항)",
                },
                "tag": {
                    "type": "string",
                    "description": "태그 필터 (선택사항)",
                },
            },
            "required": [],
        },
    },
    # ── Phase 4-6 ext: Editor / Approval / Governance ────────────────────────
    {
        "name": "generate_seo_draft",
        "description": (
            "ContentBrief를 기반으로 SEO 콘텐츠 수정안(ContentDraft)을 생성합니다. "
            "title/meta/h1 before→after diff, 섹션별 개선안, FAQ 추가안을 포함합니다. "
            "생성된 draft는 거버넌스 검수 후 승인 워크플로우로 전달됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "brief_id": {
                    "type": "string",
                    "description": "대상 ContentBrief ID (예: brief_abc12345)",
                },
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 보강 여부 (기본값: true)",
                },
            },
            "required": ["brief_id"],
        },
    },
    {
        "name": "generate_all_drafts",
        "description": (
            "draft 상태의 ContentBrief 전체에 대해 수정안을 일괄 생성합니다. "
            "이미 draft가 있는 brief는 건너뜁니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_briefs": {
                    "type": "integer",
                    "description": "최대 처리 브리프 수 (기본값: 5)",
                },
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 보강 여부 (기본값: false)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "create_seo_recommendations",
        "description": (
            "룰 엔진 결과를 Recommendation 객체로 변환합니다. "
            "상태는 pending_approval로 설정되며, 승인자 검토 대기 상태가 됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_hits": {
                    "type": "integer",
                    "description": "변환할 최대 룰 히트 수 (기본값: 20)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "list_pending_recommendations",
        "description": (
            "승인 대기 중인 SEO 추천 목록을 반환합니다. "
            "우선순위/URL/유형 기준으로 정렬됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "approve_recommendation",
        "description": (
            "SEO 추천을 승인합니다. "
            "승인 시 자동으로 SEO 실험 베이스라인이 생성됩니다. "
            "승인된 추천은 실제 변경 전 ContentDraft 수정이 완료된 후 적용됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rec_id": {
                    "type": "string",
                    "description": "승인할 Recommendation ID (예: rec_abc12345)",
                },
                "approver_notes": {
                    "type": "string",
                    "description": "승인 사유 또는 주석 (선택사항)",
                },
            },
            "required": ["rec_id"],
        },
    },
    {
        "name": "reject_recommendation",
        "description": (
            "SEO 추천을 거부합니다. "
            "거부 이유를 기록하여 향후 규칙 개선에 활용합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "rec_id": {
                    "type": "string",
                    "description": "거부할 Recommendation ID",
                },
                "reason": {
                    "type": "string",
                    "description": "거부 이유",
                },
            },
            "required": ["rec_id"],
        },
    },
    {
        "name": "get_approval_summary",
        "description": (
            "SEO 추천 승인 현황 요약을 반환합니다. "
            "pending/approved/rejected 상태별 건수를 포함합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "audit_seo_draft",
        "description": (
            "ContentDraft에 대해 거버넌스/브랜드 세이프티 검수를 실행합니다. "
            "과장 표현, 허위 주장, YMYL 위험, 키워드 스터핑, 브랜드 톤 위반 등을 점검합니다. "
            "brand_safety_score와 governance_flags를 draft에 기록합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "draft_id": {
                    "type": "string",
                    "description": "검수할 ContentDraft ID (예: draft_abc12345)",
                },
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 심층 검토 여부 (경계 사례에 추가 검토, 기본값: false)",
                },
            },
            "required": ["draft_id"],
        },
    },
    {
        "name": "audit_all_drafts",
        "description": (
            "검수 대기 중인 모든 ContentDraft에 대해 거버넌스 검수를 일괄 실행합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 심층 검토 여부 (기본값: false)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_governance_summary",
        "description": (
            "전체 ContentDraft 거버넌스 검수 현황을 요약합니다. "
            "평균 안전 점수, 상태별 건수를 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_seo_recommendations",
        "description": (
            "SEO 권고사항 목록을 조회합니다 (Phase 3). "
            "기회 유형, 우선순위, URL별로 필터링 가능하며 "
            "임팩트/노력도 점수 기반으로 정렬됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "priority": {
                    "type": "string",
                    "enum": ["critical", "high", "medium", "low", "all"],
                    "description": "우선순위 필터 (기본값 all)",
                    "default": "all",
                },
                "opportunity_type": {
                    "type": "string",
                    "description": "기회 유형 필터 (선택사항)",
                },
                "limit": {
                    "type": "integer",
                    "description": "최대 반환 건수 (기본값 15)",
                    "default": 15,
                },
            },
            "required": [],
        },
    },
    # ── Keyword & Query Agent (Phase 3) ──────────────────────────────────────
    {
        "name": "analyze_keyword_clusters",
        "description": (
            "GSC 쿼리 데이터를 클러스터링하여 키워드 기회를 분석합니다. "
            "검색 의도 분류, CTR 갭 키워드, 우선순위 클러스터를 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "min_impressions": {
                    "type": "integer",
                    "description": "분석 대상 최소 노출수 (기본값 100)",
                    "default": 100,
                },
                "gap_ctr_threshold": {
                    "type": "number",
                    "description": "갭 키워드 판별 CTR 임계값 (기본값 0.02 = 2%)",
                    "default": 0.02,
                },
                "llm_augment": {
                    "type": "boolean",
                    "description": "LLM 인사이트 추가 여부",
                    "default": False,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_keyword_gaps",
        "description": (
            "노출수는 높지만 CTR이 낮은 키워드 갭을 반환합니다. "
            "제목/메타 개선 또는 신규 콘텐츠가 필요한 쿼리를 우선순위별로 정리합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "min_impressions": {
                    "type": "integer",
                    "description": "최소 노출수 (기본값 200)",
                    "default": 200,
                },
                "max_ctr": {
                    "type": "number",
                    "description": "최대 CTR 필터 (기본값 0.02)",
                    "default": 0.02,
                },
                "limit": {
                    "type": "integer",
                    "description": "최대 반환 건수 (기본값 20)",
                    "default": 20,
                },
            },
            "required": [],
        },
    },
    # ── Data Ingestion Agent (Phase 3) ────────────────────────────────────────
    {
        "name": "get_connector_status",
        "description": (
            "모든 데이터 커넥터(GSC, GA4, 네이버, 카카오, 구글 광고)의 "
            "연결 상태와 실API/목 데이터 사용 여부를 확인합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "refresh_data_connectors",
        "description": (
            "모든 광고 커넥터에서 데이터를 수집합니다. "
            "USE_SQLITE=true이면 SQLite daily_metrics 테이블에 저장됩니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "수집할 일수 (기본값 28)",
                    "default": 28,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_data_freshness",
        "description": "각 커넥터의 마지막 데이터 수집 시각과 신선도 상태를 반환합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_daily_metrics_summary",
        "description": (
            "일별 광고 성과 요약을 반환합니다. "
            "USE_SQLITE=true이면 SQLite에서 조회하고, 아니면 목 데이터를 사용합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "플랫폼 필터 (naver_search/kakao/google_ads, 빈값=전체)",
                    "default": "",
                },
                "days": {
                    "type": "integer",
                    "description": "조회 기간 (기본값 7)",
                    "default": 7,
                },
            },
            "required": [],
        },
    },
    # ── Feature Flags & SQLite (Phase 4/5) ───────────────────────────────────
    {
        "name": "get_feature_flags",
        "description": "현재 활성화된 feature flag 목록과 상태를 반환합니다.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]
