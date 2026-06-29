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
]
