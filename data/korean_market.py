"""
Korean market knowledge base: holidays, shopping seasons, and benchmarks.
"""

from datetime import date
from typing import NamedTuple


class MarketEvent(NamedTuple):
    name: str
    name_en: str
    month: int
    day: int | None  # None = lunar calendar, computed dynamically
    typical_roas_multiplier: float  # vs. baseline
    recommended_budget_increase_pct: float
    key_categories: list[str]
    notes: str


# Major Korean commerce events (fixed Gregorian calendar dates)
KOREAN_MARKET_EVENTS = [
    MarketEvent(
        name="설날 연휴",
        name_en="Lunar New Year",
        month=1,
        day=None,  # lunar; falls Jan-Feb
        typical_roas_multiplier=1.8,
        recommended_budget_increase_pct=40,
        key_categories=["선물세트", "식품", "패션", "뷰티", "가전"],
        notes="연휴 2주 전부터 집중 광고 필요. 귀성길 모바일 트래픽 급증.",
    ),
    MarketEvent(
        name="발렌타인데이",
        name_en="Valentine's Day",
        month=2,
        day=14,
        typical_roas_multiplier=1.4,
        recommended_budget_increase_pct=20,
        key_categories=["초콜릿", "뷰티", "주얼리", "꽃"],
        notes="화이트데이(3/14)와 세트 기획 권장.",
    ),
    MarketEvent(
        name="화이트데이",
        name_en="White Day",
        month=3,
        day=14,
        typical_roas_multiplier=1.3,
        recommended_budget_increase_pct=15,
        key_categories=["캔디", "뷰티", "선물"],
        notes="한국 특유의 쇼핑 이벤트. 20-30대 타겟 집중.",
    ),
    MarketEvent(
        name="어린이날",
        name_en="Children's Day",
        month=5,
        day=5,
        typical_roas_multiplier=2.0,
        recommended_budget_increase_pct=50,
        key_categories=["완구", "아동복", "도서", "체험", "가전"],
        notes="황금연휴 연계. 가족 단위 소비 극대화 시즌.",
    ),
    MarketEvent(
        name="어버이날",
        name_en="Parents' Day",
        month=5,
        day=8,
        typical_roas_multiplier=1.6,
        recommended_budget_increase_pct=30,
        key_categories=["건강식품", "홍삼", "꽃", "선물세트", "여행"],
        notes="카네이션 관련 상품 검색량 폭증.",
    ),
    MarketEvent(
        name="스승의날",
        name_en="Teachers' Day",
        month=5,
        day=15,
        typical_roas_multiplier=1.2,
        recommended_budget_increase_pct=10,
        key_categories=["선물", "꽃", "도서"],
        notes="소규모이나 선물 카테고리에 영향.",
    ),
    MarketEvent(
        name="618 쇼핑 페스티벌",
        name_en="618 Shopping Festival",
        month=6,
        day=18,
        typical_roas_multiplier=1.5,
        recommended_budget_increase_pct=35,
        key_categories=["가전", "패션", "뷰티", "식품"],
        notes="중국發 행사가 한국으로 전파. 쿠팡·네이버 대규모 프로모션.",
    ),
    MarketEvent(
        name="추석 연휴",
        name_en="Chuseok (Korean Thanksgiving)",
        month=9,
        day=None,  # lunar; falls Sep-Oct
        typical_roas_multiplier=2.1,
        recommended_budget_increase_pct=60,
        key_categories=["선물세트", "식품", "한과", "홍삼", "가전"],
        notes="설날과 함께 연간 최대 쇼핑 시즌. 3주 전부터 광고 집중.",
    ),
    MarketEvent(
        name="빼빼로데이",
        name_en="Pepero Day",
        month=11,
        day=11,
        typical_roas_multiplier=1.4,
        recommended_budget_increase_pct=20,
        key_categories=["과자", "초콜릿", "선물"],
        notes="11/11 이중 의미(빼빼로+광군절). 식품 카테고리 단기 급증.",
    ),
    MarketEvent(
        name="광군제 (블랙프라이데이)",
        name_en="11.11 / Black Friday",
        month=11,
        day=11,
        typical_roas_multiplier=2.5,
        recommended_budget_increase_pct=80,
        key_categories=["가전", "패션", "뷰티", "가구", "식품"],
        notes="한국 최대 할인 행사. 쿠팡·네이버쇼핑·무신사 대규모 딜.",
    ),
    MarketEvent(
        name="크리스마스 시즌",
        name_en="Christmas Season",
        month=12,
        day=25,
        typical_roas_multiplier=1.9,
        recommended_budget_increase_pct=50,
        key_categories=["선물", "패션", "뷰티", "주얼리", "장난감"],
        notes="12월 초부터 연말 분위기 광고 집행 권장.",
    ),
    MarketEvent(
        name="연말 결산 세일",
        name_en="Year-End Sale",
        month=12,
        day=26,
        typical_roas_multiplier=1.7,
        recommended_budget_increase_pct=40,
        key_categories=["가전", "패션", "도서", "소프트웨어"],
        notes="크리스마스 직후~31일. 연말 소진 예산 집행 급증.",
    ),
]

# Korean ad platform benchmarks by category (KRW, 2024 기준)
PLATFORM_BENCHMARKS = {
    "naver_search": {
        "name": "네이버 검색광고",
        "avg_cpc_krw": {
            "패션": 350,
            "뷰티": 420,
            "식품": 280,
            "가전": 890,
            "여행": 750,
            "건강": 510,
            "교육": 620,
            "금융": 1200,
        },
        "avg_ctr_pct": 3.2,
        "avg_cvr_pct": 2.8,
        "avg_roas": 450,
        "strength": "구매 의도 높은 검색 트래픽. 브랜드 및 카테고리 키워드.",
    },
    "naver_shopping": {
        "name": "네이버 쇼핑광고",
        "avg_cpc_krw": {
            "패션": 180,
            "뷰티": 210,
            "식품": 150,
            "가전": 450,
            "여행": 0,
            "건강": 260,
            "교육": 0,
            "금융": 0,
        },
        "avg_ctr_pct": 2.1,
        "avg_cvr_pct": 3.5,
        "avg_roas": 600,
        "strength": "제품 이미지 노출. 쇼핑 의도 명확한 사용자.",
    },
    "kakao_display": {
        "name": "카카오 디스플레이광고",
        "avg_cpm_krw": 4500,
        "avg_ctr_pct": 0.8,
        "avg_cvr_pct": 1.2,
        "avg_roas": 280,
        "strength": "카카오톡 메시지형, DA. 20-40대 광범위 도달.",
    },
    "kakao_moment": {
        "name": "카카오모먼트",
        "avg_cpm_krw": 3800,
        "avg_ctr_pct": 1.1,
        "avg_cvr_pct": 1.5,
        "avg_roas": 320,
        "strength": "카카오톡·다음 네트워크. 리타겟팅 효율 우수.",
    },
    "coupang_ads": {
        "name": "쿠팡 광고",
        "avg_cpc_krw": {
            "패션": 140,
            "뷰티": 170,
            "식품": 120,
            "가전": 380,
            "여행": 0,
            "건강": 220,
            "교육": 0,
            "금융": 0,
        },
        "avg_ctr_pct": 2.8,
        "avg_cvr_pct": 5.2,
        "avg_roas": 750,
        "strength": "로켓배송 신뢰도. 구매 전환율 최상위. 이커머스 집중.",
    },
    "meta_instagram": {
        "name": "인스타그램 광고",
        "avg_cpm_krw": 8200,
        "avg_ctr_pct": 1.5,
        "avg_cvr_pct": 1.8,
        "avg_roas": 350,
        "strength": "비주얼 중심 브랜드 인지도. MZ세대(18-35) 집중.",
    },
    "youtube_ads": {
        "name": "유튜브 광고",
        "avg_cpv_krw": 12,
        "avg_view_rate_pct": 32,
        "avg_cvr_pct": 0.9,
        "avg_roas": 240,
        "strength": "동영상 스토리텔링. 전 연령대 브랜드 인지도.",
    },
}

# Korean consumer behavior insights
CONSUMER_INSIGHTS = {
    "mobile_usage": "모바일 트래픽 비중 78%. 모바일 최적화 필수.",
    "kakao_dominance": "메시징 앱 카카오톡 월 4,800만 MAU. 알림톡·친구톡 마케팅 병행 권장.",
    "naver_dominance": "국내 검색 시장 점유율 60%+. 네이버 SEO·광고 필수.",
    "review_culture": "네이버 리뷰·카카오 리뷰 중요도 매우 높음. UGC 활용 광고 효율 30% 향상.",
    "live_commerce": "네이버 쇼핑라이브·카카오쇼핑라이브 성장 중. 인플루언서 협업 ROAS 평균 500%+.",
    "mz_generation": "MZ세대(1980-2010년생) 소비 주도. 가치 소비·ESG 브랜드 선호.",
    "quick_delivery": "로켓배송 등 당일·익일배송 기대치 높음. 배송 광고 소재 효율적.",
    "discount_sensitivity": "할인율 표시 광고 CTR 35% 증가. '최저가' 키워드 선호.",
    "peak_hours": "평일 점심(12-13시)·퇴근 후(20-22시) 트래픽 최고. 예산 시간 배분 최적화 필요.",
    "payment_preference": "카카오페이·네이버페이·토스 간편결제 선호. 결제 편의성 강조 필요.",
}

# Category-specific KPI benchmarks (Korea, 2024)
CATEGORY_KPIS = {
    "패션": {"target_roas": 400, "target_cpa_krw": 25000, "avg_order_value_krw": 85000},
    "뷰티": {"target_roas": 500, "target_cpa_krw": 18000, "avg_order_value_krw": 65000},
    "식품": {"target_roas": 350, "target_cpa_krw": 15000, "avg_order_value_krw": 45000},
    "가전": {"target_roas": 600, "target_cpa_krw": 85000, "avg_order_value_krw": 320000},
    "건강": {"target_roas": 450, "target_cpa_krw": 35000, "avg_order_value_krw": 95000},
    "여행": {"target_roas": 300, "target_cpa_krw": 45000, "avg_order_value_krw": 280000},
    "교육": {"target_roas": 280, "target_cpa_krw": 55000, "avg_order_value_krw": 180000},
    "금융": {"target_roas": 250, "target_cpa_krw": 120000, "avg_order_value_krw": 0},
}


def get_upcoming_events(current_month: int, lookahead_months: int = 2) -> list[MarketEvent]:
    """Return market events within the lookahead window."""
    months = [(current_month + i - 1) % 12 + 1 for i in range(lookahead_months + 1)]
    return [e for e in KOREAN_MARKET_EVENTS if e.month in months]


def get_platform_recommendation(category: str, budget_krw: int) -> dict:
    """Recommend platform mix based on category and budget."""
    if budget_krw < 1_000_000:
        # 소규모 예산: 네이버 검색 집중
        return {
            "primary": "naver_search",
            "allocation": {"naver_search": 70, "naver_shopping": 30},
            "rationale": "소규모 예산은 구매 의도 높은 검색광고 집중 권장",
        }
    elif budget_krw < 10_000_000:
        # 중규모: 네이버 + 카카오
        return {
            "primary": "naver_search",
            "allocation": {
                "naver_search": 40,
                "naver_shopping": 25,
                "kakao_moment": 20,
                "coupang_ads": 15,
            },
            "rationale": "검색 + 디스플레이 혼합으로 인지도와 전환 균형",
        }
    else:
        # 대규모: 풀 채널
        return {
            "primary": "naver_search",
            "allocation": {
                "naver_search": 25,
                "naver_shopping": 20,
                "kakao_moment": 15,
                "coupang_ads": 20,
                "meta_instagram": 10,
                "youtube_ads": 10,
            },
            "rationale": "풀 퍼널 전략으로 인지~전환 전체 커버",
        }
