"""
Mock SEO data: Google Search Console + GA4 + PageSpeed + Site Crawl
Korean beauty e-commerce site (뷰티랩 BeautyLab) 기준 현실적 수치
"""

from dataclasses import dataclass


@dataclass
class GSCQueryRow:
    query: str
    url: str
    impressions: int
    clicks: int
    ctr: float
    position: float
    device: str = "MOBILE"
    country: str = "kor"


@dataclass
class GA4LandingRow:
    url: str
    sessions: int
    engaged_sessions: int
    conversions: int
    revenue_krw: int
    conversion_rate: float
    source: str = "google"
    medium: str = "organic"


@dataclass
class PageSpeedResult:
    url: str
    strategy: str           # "mobile" | "desktop"
    performance_score: float
    lcp_ms: float           # Largest Contentful Paint
    cls: float              # Cumulative Layout Shift
    inp_ms: float           # Interaction to Next Paint
    seo_score: float
    accessibility_score: float


@dataclass
class CrawledPage:
    url: str
    status_code: int
    title: str
    meta_description: str
    h1: str
    canonical_url: str
    is_indexable: bool
    in_sitemap: bool
    robots_allowed: bool
    has_structured_data: bool
    internal_link_count: int
    redirect_chain_length: int
    page_type: str          # "product", "category", "article", "faq", "home"
    last_updated_days: int = 30


# ── GSC Query Data ──────────────────────────────────────────────────────────

GSC_QUERIES: list[GSCQueryRow] = [
    # High impression / Low CTR → title/meta 개선 기회
    GSCQueryRow("콜라겐 세럼 추천",           "/skincare/collagen-serum-guide",      45000, 520,  0.0116, 5.2),
    GSCQueryRow("히알루론산 세럼 효과",        "/skincare/hyaluronic-acid",           38000, 380,  0.0100, 6.8),
    GSCQueryRow("레티놀 세럼 부작용",          "/skincare/retinol-guide",             29000, 290,  0.0100, 7.1),
    GSCQueryRow("나이아신아마이드 효능",        "/ingredients/niacinamide",            22000, 176,  0.0080, 8.3),
    GSCQueryRow("세럼 바르는 순서",            "/skincare/routine-guide",             18000, 126,  0.0070, 9.1),

    # Page 2 opportunities (position 4-15)
    GSCQueryRow("30대 여성 스킨케어 루틴",     "/skincare/30s-routine",               12000, 480,  0.0400, 4.3),
    GSCQueryRow("콜라겐 먹는거 vs 바르는거",   "/skincare/collagen-types",             9500, 342,  0.0360, 5.7),
    GSCQueryRow("피부 탄력 개선 방법",         "/skincare/skin-elasticity",           11000, 330,  0.0300, 6.1),
    GSCQueryRow("프리미엄 안티에이징 세럼",    "/antiaging/premium-serum",             6200, 155,  0.0250, 8.8),

    # Good performers
    GSCQueryRow("뷰티랩",                     "/",                                   25000, 5000, 0.2000, 1.2),
    GSCQueryRow("뷰티랩 콜라겐 세럼",         "/product/collagen-serum-50ml",         8500, 2125, 0.2500, 1.8),
    GSCQueryRow("뷰티랩 세럼 후기",           "/reviews/beautylab-serum",             7800, 390,  0.0500, 3.2),

    # Cannibalization (same query → 3 URLs competing)
    GSCQueryRow("콜라겐 세럼",               "/product/collagen-serum-50ml",         15000, 750,  0.0500, 3.5),
    GSCQueryRow("콜라겐 세럼",               "/skincare/collagen-serum-guide",        15000, 450,  0.0300, 7.2),
    GSCQueryRow("콜라겐 세럼",               "/category/serums",                      15000, 300,  0.0200, 11.1),

    # Declining content (시즌 지남 + 미업데이트)
    GSCQueryRow("여름 스킨케어 루틴",         "/seasonal/summer-skincare",             8000, 200,  0.0250, 12.1),
    GSCQueryRow("봄 피부 관리",              "/seasonal/spring-skincare",             6500, 130,  0.0200, 14.3),

    # GEO candidates (질문형/비교형 쿼리)
    GSCQueryRow("콜라겐 세럼 몇 살부터 써야 해", "/faq/collagen-age",                  5500,  55,  0.0100, 15.2),
    GSCQueryRow("세럼이랑 앰플 차이",          "/faq/serum-vs-ampoule",               12000, 120,  0.0100, 13.4),
    GSCQueryRow("히알루론산 매일 써도 되나요", "/faq/hyaluronic-daily",                 8800,  88,  0.0100, 16.7),
    GSCQueryRow("레티놀 처음 쓸 때 주의사항", "/faq/retinol-beginners",                6600,  66,  0.0100, 18.2),
    GSCQueryRow("뷰티랩 vs 설화수 세럼 비교", "/comparison/beautylab-vs-sulwhasoo",    3200,  32,  0.0100, 22.1),
    GSCQueryRow("스킨케어 순서 어떻게 해야 하나요", "/skincare/routine-guide",          9000,  90,  0.0100, 11.8),
    GSCQueryRow("콜라겐 세럼 효과 얼마나 걸려", "/faq/collagen-timeline",               7200,  72,  0.0100, 19.5),
]

# Declining content — prior period comparison
DECLINING_QUERIES = {
    "/seasonal/summer-skincare": {"clicks_28d": 200, "clicks_prev_28d": 980, "position_28d": 12.1, "position_prev_28d": 5.8, "last_updated_days": 310},
    "/seasonal/spring-skincare": {"clicks_28d": 130, "clicks_prev_28d": 720, "position_28d": 14.3, "position_prev_28d": 6.2, "last_updated_days": 290},
}


# ── GA4 Landing Page Data ────────────────────────────────────────────────────

GA4_LANDING_PAGES: list[GA4LandingRow] = [
    GA4LandingRow("/product/collagen-serum-50ml",    8200, 6150,  492, 73800000, 0.060),
    GA4LandingRow("/skincare/collagen-serum-guide",  3100, 1550,   62,  9300000, 0.020),
    GA4LandingRow("/skincare/hyaluronic-acid",       2400,  960,   24,  3600000, 0.010),
    GA4LandingRow("/skincare/30s-routine",           1800, 1080,   54,  8100000, 0.030),
    GA4LandingRow("/category/serums",                4500, 2700,  225, 33750000, 0.050),
    GA4LandingRow("/reviews/beautylab-serum",        2900, 2320,  232, 34800000, 0.080),
    GA4LandingRow("/",                              12000, 7200,  360, 54000000, 0.030),
    GA4LandingRow("/faq/serum-vs-ampoule",            850,  170,    9,  1350000, 0.010),
    GA4LandingRow("/faq/collagen-age",                420,   84,    4,   600000, 0.010),
    GA4LandingRow("/seasonal/summer-skincare",        820,  164,    8,  1200000, 0.010),
]


# ── PageSpeed Data ───────────────────────────────────────────────────────────

PAGESPEED_DATA: list[PageSpeedResult] = [
    PageSpeedResult("/product/collagen-serum-50ml",    "mobile", 0.52, 4800, 0.18, 320, 0.91, 0.88),
    PageSpeedResult("/skincare/collagen-serum-guide",  "mobile", 0.61, 3900, 0.12, 280, 0.89, 0.92),
    PageSpeedResult("/category/serums",                "mobile", 0.44, 5600, 0.24, 410, 0.85, 0.84),
    PageSpeedResult("/",                               "mobile", 0.58, 4200, 0.15, 310, 0.90, 0.90),
    PageSpeedResult("/faq/serum-vs-ampoule",           "mobile", 0.78, 2800, 0.08, 220, 0.93, 0.95),
    PageSpeedResult("/product/collagen-serum-50ml",   "desktop", 0.71, 2100, 0.10, 180, 0.94, 0.92),
    PageSpeedResult("/category/serums",               "desktop", 0.63, 2800, 0.12, 220, 0.88, 0.87),
]


# ── Crawled Pages ────────────────────────────────────────────────────────────

CRAWLED_PAGES: list[CrawledPage] = [
    CrawledPage(
        url="/product/collagen-serum-50ml",
        status_code=200,
        title="뷰티랩 프리미엄 콜라겐 세럼 50ml",
        meta_description="히알루론산·레티놀 함유 고농도 콜라겐 세럼. 피부 탄력 30% 개선 임상 완료.",
        h1="뷰티랩 프리미엄 콜라겐 세럼",
        canonical_url="/product/collagen-serum-50ml",
        is_indexable=True, in_sitemap=True, robots_allowed=True,
        has_structured_data=False,  # Product/Offer schema 누락
        internal_link_count=8, redirect_chain_length=0,
        page_type="product", last_updated_days=45,
    ),
    CrawledPage(
        url="/skincare/collagen-serum-guide",
        status_code=200,
        title="콜라겐 세럼 추천 가이드",
        meta_description="",  # meta description 누락
        h1="콜라겐 세럼 선택 방법",
        canonical_url="/skincare/collagen-serum-guide",
        is_indexable=True, in_sitemap=True, robots_allowed=True,
        has_structured_data=False,
        internal_link_count=3, redirect_chain_length=0,
        page_type="article", last_updated_days=95,
    ),
    CrawledPage(
        url="/faq/serum-vs-ampoule",
        status_code=200,
        title="세럼이랑 앰플 차이 완벽 정리",
        meta_description="세럼과 앰플의 차이점, 사용 순서, 선택 방법을 정리했습니다.",
        h1="세럼 vs 앰플: 무엇이 다를까?",
        canonical_url="/faq/serum-vs-ampoule",
        is_indexable=True, in_sitemap=False,  # sitemap 미포함
        robots_allowed=True,
        has_structured_data=False,  # FAQPage schema 없음
        internal_link_count=2, redirect_chain_length=0,
        page_type="faq", last_updated_days=120,
    ),
    CrawledPage(
        url="/old-collagen-guide",
        status_code=301,
        title="",
        meta_description="",
        h1="",
        canonical_url="/skincare/collagen-serum-guide",
        is_indexable=False, in_sitemap=True,  # Sitemap에 redirect URL 포함 (bad)
        robots_allowed=True,
        has_structured_data=False,
        internal_link_count=0, redirect_chain_length=2,  # 리다이렉트 체인
        page_type="article", last_updated_days=400,
    ),
    CrawledPage(
        url="/category/serums",
        status_code=200,
        title="세럼 종류 | 뷰티랩",
        meta_description="뷰티랩 세럼 전체 라인업.",
        h1="",  # H1 누락
        canonical_url="/category/serums",
        is_indexable=True, in_sitemap=True, robots_allowed=True,
        has_structured_data=False,
        internal_link_count=24, redirect_chain_length=0,
        page_type="category", last_updated_days=20,
    ),
    CrawledPage(
        url="/skincare/30s-routine",
        status_code=200,
        title="30대 스킨케어 루틴",
        meta_description="30대 여성을 위한 스킨케어 루틴 가이드.",
        h1="30대 여성 스킨케어 루틴 완벽 가이드",
        canonical_url="/skincare/30s-routine",
        is_indexable=True, in_sitemap=True, robots_allowed=True,
        has_structured_data=False,
        internal_link_count=5, redirect_chain_length=0,
        page_type="article", last_updated_days=60,
    ),
]


# ── Site Benchmarks ──────────────────────────────────────────────────────────

SITE_BENCHMARKS = {
    "site_url": "https://beautylab.co.kr",
    "site_name": "뷰티랩 (BeautyLab)",
    "category": "뷰티/스킨케어",
    "period_28d": {
        "total_clicks": 18500,
        "total_impressions": 420000,
        "avg_ctr": 0.044,
        "avg_position": 8.2,
        "organic_revenue_krw": 220000000,
    },
    "period_prev_28d": {
        "total_clicks": 22100,
        "total_impressions": 390000,
        "avg_ctr": 0.057,
        "avg_position": 7.1,
        "organic_revenue_krw": 265000000,
    },
    "expected_ctr_by_position": {
        1: 0.28, 2: 0.15, 3: 0.11, 4: 0.08, 5: 0.06,
        6: 0.05, 7: 0.04, 8: 0.034, 9: 0.030, 10: 0.026,
    },
    "site_avg_impressions": 5000,
}


# ── Helper Functions ─────────────────────────────────────────────────────────

def get_gsc_queries(min_impressions: int = 0, max_position: float = 100, url_filter: str = "") -> list[GSCQueryRow]:
    rows = [r for r in GSC_QUERIES if r.impressions >= min_impressions and r.position <= max_position]
    if url_filter:
        rows = [r for r in rows if url_filter in r.url]
    return rows


def get_ga4_landing(url: str = "") -> list[GA4LandingRow]:
    if url:
        return [r for r in GA4_LANDING_PAGES if r.url == url]
    return GA4_LANDING_PAGES


def get_pagespeed(url: str = "", strategy: str = "mobile") -> list[PageSpeedResult]:
    rows = [r for r in PAGESPEED_DATA if r.strategy == strategy]
    if url:
        rows = [r for r in rows if r.url == url]
    return rows


def get_crawled_pages(page_type: str = "") -> list[CrawledPage]:
    if page_type:
        return [r for r in CRAWLED_PAGES if r.page_type == page_type]
    return CRAWLED_PAGES
