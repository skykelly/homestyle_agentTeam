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
]
