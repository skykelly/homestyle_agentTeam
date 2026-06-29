"""
SEO Internal Link Workflow — Phase 4.
Hub-spoke structure analysis and internal link recommendations.
Identifies orphan pages, underlinked high-value pages, and cross-link opportunities.
"""

from datetime import datetime

from data.seo_mock_data import get_crawled_pages, get_ga4_landing, get_gsc_queries, SITE_BENCHMARKS
from models.agent_run import AgentRun
from models.seo_models import InternalLinkRecommendation
from storage.repository import save_agent_run
from storage.seo_repository import save_link_recommendation
from workflows.base import BaseWorkflow


# Hub-spoke topic cluster definition for 뷰티랩
TOPIC_CLUSTERS = {
    "콜라겐 세럼": {
        "hub": "/skincare/collagen-serum-guide",
        "spokes": [
            "/product/collagen-serum-50ml",
            "/skincare/collagen-types",
            "/faq/collagen-age",
            "/faq/collagen-timeline",
            "/skincare/skin-elasticity",
        ],
        "topic": "collagen",
    },
    "스킨케어 루틴": {
        "hub": "/skincare/routine-guide",
        "spokes": [
            "/skincare/30s-routine",
            "/seasonal/summer-skincare",
            "/seasonal/spring-skincare",
            "/faq/hyaluronic-daily",
        ],
        "topic": "routine",
    },
    "성분 가이드": {
        "hub": "/ingredients/niacinamide",
        "spokes": [
            "/skincare/hyaluronic-acid",
            "/skincare/retinol-guide",
            "/faq/retinol-beginners",
            "/faq/serum-vs-ampoule",
        ],
        "topic": "ingredients",
    },
}

# Pages with high traffic that should link to product pages
HIGH_TRAFFIC_CONTENT_PAGES = [
    "/skincare/collagen-serum-guide",
    "/skincare/30s-routine",
    "/reviews/beautylab-serum",
    "/skincare/hyaluronic-acid",
]

PRODUCT_PAGES = [
    "/product/collagen-serum-50ml",
    "/category/serums",
]


class SEOInternalLinkWorkflow(BaseWorkflow):
    """
    Analyzes internal link structure and recommends improvements.
    Focuses on hub-spoke topology, orphan rescue, and conversion path strengthening.
    """

    system_prompt = """You are an Internal Link Strategy Specialist for Korean beauty e-commerce.

Your role is to design internal linking structures that:
1. Distribute PageRank from high-authority pages to high-value pages
2. Create clear topic clusters (hub-spoke) for semantic SEO
3. Strengthen the content→product conversion path
4. Rescue orphan pages by connecting them to relevant hubs
5. Improve navigation for both search engines and users

Korean beauty e-commerce context:
- Product pages (/product/*) need more internal links for conversion
- Category pages (/category/*) should connect to all relevant product pages
- Article/Guide pages should link to product pages with commercial anchor text
- FAQ pages should link to detailed guides and product pages

Anchor text principles:
- Use natural Korean language anchors (avoid generic "여기를 클릭")
- Include target keywords in anchors where natural
- Vary anchor text to avoid over-optimization"""

    allowed_tools = ["get_seo_overview", "get_technical_audit"]

    def analyze_and_recommend(self, llm_augment: bool = True) -> dict:
        """
        Analyze internal link structure and generate recommendations.
        """
        run = AgentRun(
            workflow_name="seo_internal_link",
            trigger="manual",
            input_params={"llm_augment": llm_augment},
        )
        save_agent_run(run)

        pages = get_crawled_pages()
        ga4_data = {r.url: r for r in get_ga4_landing()}
        gsc_data = {}
        for r in get_gsc_queries():
            if r.url not in gsc_data:
                gsc_data[r.url] = r

        recommendations: list[InternalLinkRecommendation] = []

        # ── 1. Orphan page rescue ─────────────────────────────────────────
        for page in pages:
            if page.status_code != 200:
                continue
            if page.internal_link_count < 2 and page.is_indexable:
                # Find best hub for this page
                best_hub = _find_best_hub(page.url)
                if best_hub:
                    ga4 = ga4_data.get(best_hub)
                    rec = InternalLinkRecommendation(
                        source_url=best_hub,
                        target_url=page.url,
                        anchor_text=_suggest_anchor(page.url, gsc_data),
                        placement_hint="본문 관련 섹션 내 자연스러운 문장에 삽입",
                        topic_relevance="동일 토픽 클러스터 내 연결",
                        link_type="orphan_rescue",
                        priority="high" if (ga4 and ga4.sessions > 1000) else "medium",
                        rationale=f"{page.url}의 내부 링크 {page.internal_link_count}개 — 고립 페이지 위험. {best_hub}에서 연결하여 크롤 및 링크 에쿼티 확보.",
                    )
                    save_link_recommendation(rec)
                    recommendations.append(rec)
                    self._log(f"  [Link] Orphan rescue: {best_hub} → {page.url}")

        # ── 2. Hub → Spoke connections ────────────────────────────────────
        for cluster_name, cluster in TOPIC_CLUSTERS.items():
            hub = cluster["hub"]
            for spoke in cluster["spokes"]:
                # Check if link already implied by high internal_link_count on hub
                hub_page = next((p for p in pages if p.url == hub), None)
                if hub_page and hub_page.internal_link_count > 8:
                    continue  # Hub already well-connected

                ga4_spoke = ga4_data.get(spoke)
                gsc_spoke = gsc_data.get(spoke)

                rec = InternalLinkRecommendation(
                    source_url=hub,
                    target_url=spoke,
                    anchor_text=_suggest_anchor(spoke, gsc_data),
                    placement_hint=f"'{cluster_name}' 섹션 내 첫 번째 관련 언급 시",
                    topic_relevance=f"클러스터: {cluster_name} — {cluster['topic']} 주제 연결",
                    link_type="hub_to_spoke",
                    priority="high" if gsc_spoke and gsc_spoke.impressions > 5000 else "medium",
                    rationale=f"토픽 클러스터 '{cluster_name}' — hub {hub}에서 spoke {spoke}로 연결하여 주제 권위도 집중화",
                )
                save_link_recommendation(rec)
                recommendations.append(rec)

        # ── 3. High-traffic content → Product pages ───────────────────────
        for content_url in HIGH_TRAFFIC_CONTENT_PAGES:
            ga4 = ga4_data.get(content_url)
            if not ga4 or ga4.sessions < 500:
                continue

            for product_url in PRODUCT_PAGES:
                rec = InternalLinkRecommendation(
                    source_url=content_url,
                    target_url=product_url,
                    anchor_text=_suggest_product_anchor(product_url),
                    placement_hint="콘텐츠 중반부 또는 '추천 제품' 섹션",
                    topic_relevance="콘텐츠-제품 전환 경로 강화",
                    link_type="spoke_to_hub",
                    priority="high",
                    rationale=(
                        f"{content_url}의 월 세션 {ga4.sessions:,}회 → "
                        f"{product_url} 전환 경로 강화로 오가닉 매출 개선 가능. "
                        f"현재 전환율 {ga4.conversion_rate*100:.1f}% 개선 목표."
                    ),
                )
                save_link_recommendation(rec)
                recommendations.append(rec)
                self._log(f"  [Link] Content→Product: {content_url} → {product_url}")

        # ── 4. Cross-links between related FAQ pages ──────────────────────
        faq_pages = [p for p in pages if p.page_type == "faq" and p.status_code == 200]
        for i, faq_a in enumerate(faq_pages):
            for faq_b in faq_pages[i+1:]:
                rec = InternalLinkRecommendation(
                    source_url=faq_a.url,
                    target_url=faq_b.url,
                    anchor_text=_suggest_anchor(faq_b.url, gsc_data),
                    placement_hint="FAQ 답변 마지막 문장 또는 '관련 질문' 섹션",
                    topic_relevance="FAQ 페이지 간 상호 연결 — 검색자 탐색 경로 개선",
                    link_type="cross_link",
                    priority="medium",
                    rationale="FAQ 페이지 간 교차 링크로 체류 시간 증가 및 관련 쿼리 커버리지 확대",
                )
                save_link_recommendation(rec)
                recommendations.append(rec)

        # ── LLM: Strategic internal link analysis ─────────────────────────
        llm_analysis = ""
        if llm_augment and recommendations:
            high_pri = [r for r in recommendations if r.priority == "high"][:5]
            summary = "\n".join(
                f"  - [{r.link_type}] {r.source_url} → {r.target_url} | {r.rationale[:80]}"
                for r in high_pri
            )

            prompt = f"""뷰티랩 사이트의 내부 링크 구조 개선 전략을 분석해주세요.

상위 우선순위 링크 권고 ({len(high_pri)}건):
{summary}

토픽 클러스터 현황:
  - 콜라겐 세럼 클러스터: hub={TOPIC_CLUSTERS['콜라겐 세럼']['hub']}, {len(TOPIC_CLUSTERS['콜라겐 세럼']['spokes'])}개 spoke
  - 스킨케어 루틴 클러스터: hub={TOPIC_CLUSTERS['스킨케어 루틴']['hub']}, {len(TOPIC_CLUSTERS['스킨케어 루틴']['spokes'])}개 spoke
  - 성분 가이드 클러스터: hub={TOPIC_CLUSTERS['성분 가이드']['hub']}, {len(TOPIC_CLUSTERS['성분 가이드']['spokes'])}개 spoke

분석 요청:
1. 현재 내부 링크 구조의 핵심 문제점 (2-3가지)
2. 콘텐츠→제품 전환 경로 강화 방안
3. 고립 페이지 구조 해결 우선순위
4. anchor text 자연스러운 예시 3개 (한국어)
5. 6개월 내 예상 트래픽 개선 효과"""

            llm_analysis = self.run(prompt, max_iterations=2)

        run.complete(output_summary=f"{len(recommendations)}개 내부 링크 권고사항 생성")
        save_agent_run(run)

        # Group by type
        by_type = {}
        for r in recommendations:
            by_type.setdefault(r.link_type, []).append(r.to_dict())

        return {
            "run_id": run.run_id,
            "analyzed_at": datetime.now().isoformat(),
            "total_recommendations": len(recommendations),
            "by_link_type": {k: len(v) for k, v in by_type.items()},
            "high_priority_count": sum(1 for r in recommendations if r.priority == "high"),
            "topic_clusters_analyzed": len(TOPIC_CLUSTERS),
            "recommendations": sorted(
                [r.to_dict() for r in recommendations],
                key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 9),
            ),
            "by_type": by_type,
            "llm_analysis": llm_analysis,
        }


def _find_best_hub(url: str) -> str | None:
    """Find the best hub page to link from for a given URL."""
    for cluster in TOPIC_CLUSTERS.values():
        if url in cluster["spokes"]:
            return cluster["hub"]
        if url == cluster["hub"]:
            return None
    # Default hub for unknown pages
    if "skincare" in url or "ingredient" in url:
        return "/skincare/collagen-serum-guide"
    if "faq" in url:
        return "/skincare/routine-guide"
    return "/skincare/collagen-serum-guide"


def _suggest_anchor(url: str, gsc_data: dict) -> str:
    """Suggest natural Korean anchor text for a URL."""
    gsc = gsc_data.get(url)
    if gsc:
        query = gsc.query
        # Clean up query for anchor text use
        return f"{query} 자세히 알아보기"

    anchor_map = {
        "/product/collagen-serum-50ml": "뷰티랩 프리미엄 콜라겐 세럼",
        "/skincare/collagen-serum-guide": "콜라겐 세럼 완벽 가이드",
        "/skincare/hyaluronic-acid": "히알루론산 세럼 효과 알아보기",
        "/skincare/retinol-guide": "레티놀 세럼 사용법과 주의사항",
        "/skincare/routine-guide": "올바른 스킨케어 순서 가이드",
        "/skincare/30s-routine": "30대 스킨케어 루틴",
        "/faq/serum-vs-ampoule": "세럼과 앰플의 차이",
        "/faq/collagen-age": "콜라겐 세럼 나이별 사용 가이드",
        "/faq/hyaluronic-daily": "히알루론산 매일 사용 가이드",
        "/category/serums": "뷰티랩 전체 세럼 라인업",
        "/reviews/beautylab-serum": "뷰티랩 세럼 실사용 후기",
        "/ingredients/niacinamide": "나이아신아마이드 효능 완벽 정리",
    }
    return anchor_map.get(url, url.split("/")[-1].replace("-", " ").title())


def _suggest_product_anchor(product_url: str) -> str:
    anchors = {
        "/product/collagen-serum-50ml": "뷰티랩 콜라겐 세럼 구매하기",
        "/category/serums": "뷰티랩 세럼 전체 보기",
    }
    return anchors.get(product_url, "제품 상세 보기")
