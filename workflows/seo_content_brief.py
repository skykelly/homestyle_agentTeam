"""
SEO Content Brief Workflow — Phase 4.
LLM-powered content brief generation for top CTR + Page 2 opportunities.
Produces structured ContentBrief objects ready for content writers.
"""

from datetime import datetime

from data.seo_mock_data import get_gsc_queries, get_ga4_landing, get_crawled_pages
from models.agent_run import AgentRun
from models.seo_models import ContentBrief
from rules.seo_rules import run_all_seo_rules, SEORuleResult
from storage.repository import save_agent_run
from storage.seo_repository import save_content_brief
from workflows.base import BaseWorkflow


class SEOContentBriefWorkflow(BaseWorkflow):
    """
    Generates comprehensive, writer-ready content briefs for top SEO opportunities.
    Combines rule engine data with LLM to produce structured briefs.
    """

    system_prompt = """You are an SEO Content Brief Specialist for Korean beauty e-commerce.

You create detailed, actionable content briefs that content writers can immediately execute.

For each brief, provide:
1. Clear content objective tied to search intent and conversion goal
2. Primary + secondary query cluster mapping
3. Specific content gaps (what's missing vs. competitors/intent)
4. Concrete recommended sections with headings
5. 3 title tag options (under 60 chars, include primary keyword near front)
6. 2 meta description options (150-160 chars, include CTA)
7. 3 H1 options
8. 5-7 FAQ items that match question-type long-tail queries
9. Internal link suggestions with anchor text
10. Structured data schema suggestions

Korean beauty market context:
- Primary personas: 20-40대 여성, skincare-conscious consumers
- Key intent signals: 추천, 효과, 성분, 순서, 비교, 부작용, 사용법
- Seasonal relevance: summer (5-8월) = SPF/light textures, winter = moisture/barrier
- Products: serums, essences, ampoules — consumers are sophisticated and ingredient-aware

All outputs in Korean. Be specific, not generic."""

    allowed_tools = [
        "get_seo_overview",
        "get_seo_query_opportunities",
        "get_technical_audit",
    ]

    def generate_briefs(
        self,
        max_briefs: int = 5,
        opportunity_types: list[str] | None = None,
        llm_augment: bool = True,
    ) -> dict:
        """
        Generate content briefs for top SEO opportunities.

        Args:
            max_briefs: Maximum number of briefs to generate
            opportunity_types: Types to include (default: ctr_improvement + ranking_boost)
            llm_augment: Whether to use LLM for enriched brief generation
        """
        if opportunity_types is None:
            opportunity_types = ["ctr_improvement", "ranking_boost"]

        run = AgentRun(
            workflow_name="seo_content_brief",
            trigger="manual",
            input_params={"max_briefs": max_briefs, "opportunity_types": opportunity_types},
        )
        save_agent_run(run)

        # Get top opportunities from rule engine
        all_hits = run_all_seo_rules()
        target_hits = [h for h in all_hits if h.opportunity_type in opportunity_types][:max_briefs]

        self._log(f"\n[ContentBrief] Generating {len(target_hits)} briefs for {opportunity_types}")

        briefs = []
        llm_enhanced_count = 0

        for hit in target_hits:
            brief = self._build_brief_from_rule(hit)

            if llm_augment:
                brief = self._enrich_brief_with_llm(brief, hit)
                llm_enhanced_count += 1

            save_content_brief(brief)
            briefs.append(brief)
            run.recommendations_generated.append(brief.brief_id)
            self._log(f"  ✓ Brief: {brief.brief_id} → {brief.target_url} [{brief.primary_query_cluster}]")

        run.complete(
            output_summary=f"{len(briefs)}개 콘텐츠 브리프 생성 ({llm_enhanced_count}개 LLM 보강)"
        )
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "generated_at": datetime.now().isoformat(),
            "briefs_generated": len(briefs),
            "llm_enhanced": llm_enhanced_count,
            "briefs": [b.to_dict() for b in briefs],
        }

    def _build_brief_from_rule(self, hit: SEORuleResult) -> ContentBrief:
        """Build a baseline ContentBrief from rule engine data (no LLM)."""
        url = hit.target_url
        query = hit.target_queries[0] if hit.target_queries else url.split("/")[-1]

        # Find crawl data for this URL
        pages = get_crawled_pages()
        page = next((p for p in pages if p.url == url), None)

        # Find GA4 data
        ga4_rows = get_ga4_landing(url)
        ga4 = ga4_rows[0] if ga4_rows else None

        # Determine search intent
        question_words = ["어떻게", "무엇", "왜", "얼마나", "차이", "되나요", "해야"]
        commercial_words = ["추천", "최고", "베스트", "후기", "리뷰"]
        is_question = any(w in query for w in question_words)
        is_commercial = any(w in query for w in commercial_words)

        if is_question:
            intent = "informational"
            objective = f"'{query}' 질문에 대한 완전하고 신뢰할 수 있는 답변을 제공하여 AI 검색 인용 및 Featured Snippet 획득"
        elif is_commercial:
            intent = "commercial_investigation"
            objective = f"'{query}' 검색자의 구매 결정을 지원하는 비교·추천 콘텐츠로 전환율 개선"
        else:
            intent = "mixed"
            objective = f"'{query}' 검색 의도에 맞는 정보 제공으로 CTR 및 체류 시간 개선"

        # Secondary queries derived from topic
        secondary = _derive_secondary_queries(query)

        # Current gaps
        gaps = _identify_content_gaps(page, hit)

        # Section recommendations
        sections = _recommend_sections(query, intent, page)

        # Title options
        titles = [
            f"{query} 완벽 가이드 2026 | 뷰티랩",
            f"[전문가 분석] {query} — 성분·효과·사용법 정리",
            f"{query}: 뷰티랩이 직접 테스트한 실사용 리뷰",
        ]

        # Meta descriptions
        metas = [
            f"{query}에 대한 모든 것. 성분 분석, 사용 순서, 피부 타입별 추천까지. 뷰티랩 전문가가 직접 검증한 정보.",
            f"'{query}' 고민 완전 해결! 효과·부작용·사용법·추천 제품을 한눈에 정리. 지금 확인하세요.",
        ]

        # H1 options
        h1s = [
            f"{query} 완벽 가이드",
            f"{query}: 전문가가 알려주는 모든 것",
            f"{query} — 뷰티랩 실사용 분석",
        ]

        # FAQ items
        faqs = _generate_faqs(query)

        # Internal links
        internal_links = [
            {"url": "/product/collagen-serum-50ml", "anchor_text": "뷰티랩 프리미엄 콜라겐 세럼"},
            {"url": "/skincare/routine-guide", "anchor_text": "스킨케어 순서 완벽 가이드"},
            {"url": "/category/serums", "anchor_text": "뷰티랩 세럼 전체 라인업"},
            {"url": "/ingredients/niacinamide", "anchor_text": "나이아신아마이드 효능 정리"},
        ]

        # Schema suggestions
        schema_suggestions = ["Article", "BreadcrumbList"]
        if is_question:
            schema_suggestions.append("FAQPage")
        if page and page.page_type == "product":
            schema_suggestions = ["Product", "Offer", "AggregateRating", "BreadcrumbList"]

        return ContentBrief(
            target_url=url,
            primary_query_cluster=query,
            search_intent=intent,
            secondary_queries=secondary,
            current_gap=gaps,
            recommended_sections=sections,
            title_options=titles,
            meta_description_options=metas,
            h1_options=h1s,
            faq_items=faqs,
            internal_link_suggestions=internal_links,
            structured_data_suggestions=schema_suggestions,
            content_objective=objective,
            target_audience="20-40대 뷰티/스킨케어 관심 여성",
            confidence_score=hit.confidence_score,
            risk_level="low",
            expected_impact=hit.expected_impact,
            agent_run_id=None,
        )

    def _enrich_brief_with_llm(self, brief: ContentBrief, hit: SEORuleResult) -> ContentBrief:
        """
        Use LLM to enrich the content brief with more specific insights.
        Enhances FAQ, content gaps, and section recommendations.
        """
        query = brief.primary_query_cluster

        # Get GSC row data for context
        gsc_rows = [r for r in get_gsc_queries() if r.url == brief.target_url]
        gsc_str = "\n".join(
            f"  - 쿼리: '{r.query}' | 노출: {r.impressions:,} | CTR: {r.ctr*100:.2f}% | 포지션: {r.position}"
            for r in gsc_rows[:5]
        )

        prompt = f"""다음 SEO 기회에 대한 콘텐츠 브리프를 개선해주세요.

URL: {brief.target_url}
주요 쿼리: {query}
검색 의도: {brief.search_intent}
콘텐츠 목표: {brief.content_objective}

GSC 데이터:
{gsc_str if gsc_str else "  (데이터 없음)"}

현재 탐지된 문제:
  {hit.problem}

현재 콘텐츠 갭:
  {chr(10).join(f"  - {g}" for g in brief.current_gap)}

다음을 개선해주세요:
1. 현재 콘텐츠 갭을 더 구체적으로 분석 (경쟁 페이지 대비 누락 정보 3-5개)
2. 추천 섹션 구조를 더 세밀하게 (소제목 포함, H2/H3 구분)
3. FAQ 5개 (실제 사용자가 검색할 질문형으로, 각 답변 2-3문장)
4. 내부 링크 anchor text를 자연스러운 한국어 문장으로

JSON 형식으로 응답:
{{
  "refined_gaps": ["갭1", "갭2", ...],
  "refined_sections": ["섹션1", "섹션2", ...],
  "faq_items": [{{"question": "질문", "answer": "답변"}}, ...],
  "anchor_texts": [{{"url": "/path", "anchor_text": "텍스트"}}, ...]
}}"""

        try:
            response = self.run(prompt, max_iterations=2)
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                import json
                data = json.loads(json_match.group())
                if data.get("refined_gaps"):
                    brief.current_gap = data["refined_gaps"]
                if data.get("refined_sections"):
                    brief.recommended_sections = data["refined_sections"]
                if data.get("faq_items"):
                    brief.faq_items = data["faq_items"]
                if data.get("anchor_texts"):
                    brief.internal_link_suggestions = data["anchor_texts"]
        except Exception:
            pass  # Fall back to rule-based brief if LLM fails

        return brief


# ── Helper functions ──────────────────────────────────────────────────────────

def _derive_secondary_queries(query: str) -> list[str]:
    suffixes = [" 추천", " 효과", " 부작용", " 사용법", " 성분", " 순서", " 비교"]
    secondary = [query + s for s in suffixes if s not in query][:4]
    # Add question variants
    if "세럼" in query:
        secondary.append("세럼 바르는 순서")
    if "콜라겐" in query:
        secondary.append("콜라겐 흡수 방법")
    return secondary[:5]


def _identify_content_gaps(page, hit: SEORuleResult) -> list[str]:
    gaps = []
    if page:
        if not page.meta_description:
            gaps.append("메타 설명 없음 — 검색 스니펫이 자동 생성되어 CTR 저하")
        if not page.h1:
            gaps.append("H1 태그 없음 — 주제 신호 부재")
        if not page.has_structured_data:
            gaps.append("구조화 데이터 없음 — 리치 스니펫 기회 상실")
        if page.internal_link_count < 5:
            gaps.append(f"내부 링크 {page.internal_link_count}개 — 링크 에쿼티 유입 부족 (권장: 5개 이상)")
        if page.last_updated_days > 90:
            gaps.append(f"마지막 업데이트 {page.last_updated_days}일 전 — 최신 정보 부족")

    # From rule hit
    gaps.append(f"현재 포지션 {hit.current_metric.get('position', '?')} — 콘텐츠 depth 강화 필요")
    gaps.append("사용자 질문형 FAQ 섹션 없음 — 롱테일 쿼리 커버리지 부족")
    gaps.append("제품 링크와 콘텐츠 연결 미흡 — 정보→구매 전환 경로 약함")

    return gaps[:6]


def _recommend_sections(query: str, intent: str, page) -> list[str]:
    sections = [
        f"## {query}란? — 핵심 개념 정리",
        "## 주요 성분 분석 및 효능",
    ]

    if intent == "informational":
        sections += [
            "## 올바른 사용법 및 순서",
            "## 피부 타입별 적용 가이드",
            "## 주의사항 및 부작용",
            "## 자주 묻는 질문 (FAQPage 스키마)",
        ]
    elif intent == "commercial_investigation":
        sections += [
            "## 선택 기준 및 비교 포인트",
            "### 비교표: 주요 제품 핵심 차이",
            "## 뷰티랩 추천 제품 라인업",
            "## 실사용 후기 요약",
            "## 구매 가이드 — 내 피부에 맞는 선택법",
        ]
    else:
        sections += [
            "## 효과와 기대치",
            "## 사용 순서 가이드",
            "## 뷰티랩 추천 제품",
            "## 자주 묻는 질문",
        ]

    sections.append("## 내부 링크 — 관련 콘텐츠 더 보기")
    return sections


def _generate_faqs(query: str) -> list[dict]:
    base_faqs = [
        {"question": f"{query}는 언제부터 효과가 나타나나요?",
         "answer": f"{query}의 효과는 보통 2-4주 꾸준한 사용 후 나타납니다. 피부 타입과 현재 피부 상태에 따라 개인차가 있으며, 처음 2주는 피부 적응 기간으로 보는 것이 좋습니다."},
        {"question": f"{query}는 매일 사용해도 되나요?",
         "answer": "처음에는 주 3회로 시작하여 피부 반응을 확인한 후 매일 사용으로 늘리는 것을 권장합니다. 피부 자극이 없다면 아침, 저녁 모두 사용 가능합니다."},
        {"question": f"{query} 사용 순서는 어떻게 되나요?",
         "answer": "기본 스킨케어 순서는 클렌징 → 토너 → 세럼/앰플 → 에센스 → 수분 크림 순입니다. 여러 세럼을 사용할 경우 질감이 가벼운 제품부터 먼저 바릅니다."},
        {"question": f"{query}와 앰플의 차이는 무엇인가요?",
         "answer": "세럼은 활성 성분을 고농도로 함유하고 가벼운 질감으로 피부 깊이 침투합니다. 앰플은 세럼보다 농도가 더 높은 집중 케어 제품으로, 특정 피부 고민 해결에 집중 사용합니다."},
        {"question": f"{query} 선택 시 주의할 성분은 무엇인가요?",
         "answer": "레티놀과 AHA/BHA는 함께 사용 시 자극이 생길 수 있습니다. 민감성 피부라면 향료, 알코올, 인공색소가 없는 제품을 선택하고, 새 제품은 귀 뒤나 팔 안쪽에서 패치 테스트를 진행하세요."},
    ]
    return base_faqs[:5]
