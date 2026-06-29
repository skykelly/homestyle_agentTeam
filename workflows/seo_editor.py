"""
SEO Editor Workflow — Phase 4 extension.
Generates title/meta/h1 rewrites + section-level content diffs
from a ContentBrief. Produces a ContentDraft for human approval.
"""

import json
import re
from datetime import datetime

from data.seo_mock_data import get_gsc_queries, CrawledPage, SITE_BENCHMARKS
from models.agent_run import AgentRun
from models.seo_models import ContentDraft
from storage.repository import save_agent_run
from storage.seo_repository import (
    get_content_brief,
    list_content_briefs,
    save_content_draft,
    list_content_drafts,
)
from workflows.base import BaseWorkflow


# ── Mock current-page content (simulates CMS/crawler data) ───────────────────

_CURRENT_PAGE_DATA: dict[str, dict] = {
    "/skincare/collagen-serum-guide": {
        "title": "콜라겐 세럼 완벽 가이드",
        "meta": "콜라겐 세럼 관련 정보를 정리했습니다.",
        "h1": "콜라겐 세럼 가이드",
        "body_sections": [
            {"heading": "콜라겐 세럼이란?", "word_count": 120},
            {"heading": "사용 방법", "word_count": 80},
        ],
    },
    "/skincare/hyaluronic-acid": {
        "title": "히알루론산 세럼 정보",
        "meta": "히알루론산 세럼에 대해 알아보세요.",
        "h1": "히알루론산 안내",
        "body_sections": [
            {"heading": "히알루론산이란?", "word_count": 100},
            {"heading": "효과", "word_count": 60},
        ],
    },
    "/skincare/retinol-guide": {
        "title": "레티놀 가이드",
        "meta": "레티놀 세럼 사용법을 알려드립니다.",
        "h1": "레티놀 안내",
        "body_sections": [
            {"heading": "레티놀이란?", "word_count": 90},
            {"heading": "주의사항", "word_count": 70},
        ],
    },
}

_DEFAULT_PAGE = {
    "title": "페이지 제목",
    "meta": "페이지 설명",
    "h1": "페이지 h1",
    "body_sections": [{"heading": "소개", "word_count": 100}],
}


class SEOEditorWorkflow(BaseWorkflow):
    """
    Generates concrete content edits from a ContentBrief:
    - title / meta description / h1 rewrites (before → after diff)
    - section-by-section content improvement suggestions
    - FAQ additions
    Saves output as a ContentDraft ready for governance check + approval.
    """

    system_prompt = """당신은 한국 뷰티 이커머스 SEO 에디터입니다.

역할:
1. ContentBrief를 바탕으로 구체적인 title/meta/h1 개선안을 작성한다.
2. 기존 섹션의 SEO 개선 포인트를 명확히 제시한다.
3. 검색 의도(search intent)와 정확히 일치하는 문장을 만든다.
4. 브랜드 톤앤매너(친근하되 전문적, 과장 없음, 근거 기반)를 유지한다.
5. 제목/메타는 55자/160자 이내 권장.

작성 원칙:
- 사실에 근거한 표현만 사용한다 (예: "세계 최고" 금지, "피부 장벽 강화에 도움" 허용)
- 주요 키워드는 자연스럽게 앞쪽에 배치한다
- 클릭을 유도하되 과장하지 않는다
- FAQ는 실제 사용자 질문 패턴을 반영한다"""

    allowed_tools = ["get_seo_overview", "get_seo_query_opportunities"]

    def generate_draft(
        self,
        brief_id: str,
        llm_augment: bool = True,
    ) -> dict:
        """
        Generate a ContentDraft from an existing ContentBrief.
        Rule-based rewrite first; LLM enrichment if llm_augment=True.
        """
        run = AgentRun(
            workflow_name="seo_editor",
            trigger="manual",
            input_params={"brief_id": brief_id, "llm_augment": llm_augment},
        )
        save_agent_run(run)

        brief = get_content_brief(brief_id)
        if not brief:
            run.fail(f"Brief {brief_id} not found")
            save_agent_run(run)
            return {"error": f"brief_id '{brief_id}' not found"}

        url = brief["target_url"]
        current = _CURRENT_PAGE_DATA.get(url, _DEFAULT_PAGE)

        # ── Rule-based rewrites ───────────────────────────────────────────
        title_after = _rewrite_title(brief, current)
        meta_after = _rewrite_meta(brief, current)
        h1_after = _rewrite_h1(brief, current)
        section_rewrites = _build_section_rewrites(brief, current)
        faq_additions = brief.get("faq_items", [])[:3]

        # ── LLM enrichment ────────────────────────────────────────────────
        if llm_augment:
            try:
                llm_result = self._llm_enrich(brief, current, title_after, meta_after, section_rewrites)
                if llm_result:
                    title_after = llm_result.get("title_after", title_after)
                    meta_after = llm_result.get("meta_after", meta_after)
                    h1_after = llm_result.get("h1_after", h1_after)
                    if llm_result.get("section_rewrites"):
                        section_rewrites = llm_result["section_rewrites"]
                    if llm_result.get("faq_additions"):
                        faq_additions = llm_result["faq_additions"]
            except Exception:
                pass  # fall back to rule-based

        # ── Quality scoring ───────────────────────────────────────────────
        quality_score = _compute_quality_score(brief, title_after, meta_after, section_rewrites)

        # ── Existing draft version count ──────────────────────────────────
        existing = list_content_drafts(brief_id=brief_id)
        version = len(existing) + 1

        diff_summary = (
            f"Title: '{current['title']}' → '{title_after}'\n"
            f"Meta: '{current['meta'][:60]}...' → '{meta_after[:60]}...'\n"
            f"H1: '{current['h1']}' → '{h1_after}'\n"
            f"섹션 개선: {len(section_rewrites)}개 | FAQ 추가: {len(faq_additions)}개"
        )

        draft = ContentDraft(
            brief_id=brief_id,
            target_url=url,
            version=version,
            title_before=current["title"],
            title_after=title_after,
            meta_before=current["meta"],
            meta_after=meta_after,
            h1_before=current["h1"],
            h1_after=h1_after,
            section_rewrites=section_rewrites,
            faq_additions=faq_additions,
            quality_score=quality_score,
            brand_safety_score=0.0,   # filled by governance agent
            governance_flags=[],
            diff_summary=diff_summary,
        )

        save_content_draft(draft)
        run.recommendations_generated.append(draft.draft_id)
        run.complete(output_summary=f"Draft v{version} 생성: {url}")
        save_agent_run(run)

        self._log(f"  [Editor] Draft created: {draft.draft_id} (quality={quality_score:.2f})")

        return {
            "run_id": run.run_id,
            "draft_id": draft.draft_id,
            "target_url": url,
            "version": version,
            "quality_score": quality_score,
            "diff_summary": diff_summary,
            "draft": draft.to_dict(),
        }

    def generate_drafts_for_pending_briefs(
        self,
        max_briefs: int = 5,
        llm_augment: bool = True,
    ) -> dict:
        """Generate drafts for all briefs that don't yet have a draft."""
        briefs = list_content_briefs(status="draft")[:max_briefs]
        results = []
        for brief in briefs:
            bid = brief["brief_id"]
            existing = list_content_drafts(brief_id=bid)
            if existing:
                continue
            result = self.generate_draft(bid, llm_augment=llm_augment)
            results.append(result)

        return {
            "drafts_generated": len(results),
            "results": results,
        }

    def _llm_enrich(
        self,
        brief: dict,
        current: dict,
        title_draft: str,
        meta_draft: str,
        sections: list[dict],
    ) -> dict:
        """Ask LLM to refine the rule-based drafts. Returns dict or empty."""
        prompt = f"""다음 SEO 브리프와 현재 페이지 정보를 바탕으로 개선안을 작성하세요.

URL: {brief['target_url']}
주요 키워드 클러스터: {brief['primary_query_cluster']}
검색 의도: {brief['search_intent']}
보조 키워드: {', '.join(brief.get('secondary_queries', [])[:3])}

현재 페이지:
- Title: {current['title']}
- Meta: {current['meta']}
- H1: {current['h1']}

초안 (규칙 기반):
- Title 초안: {title_draft}
- Meta 초안: {meta_draft}

콘텐츠 갭:
{chr(10).join(f'- {g}' for g in brief.get('current_gap', [])[:3])}

다음 JSON 형식으로 응답하세요:
{{
  "title_after": "55자 이내 제목",
  "meta_after": "155자 이내 메타 설명",
  "h1_after": "H1 태그 텍스트",
  "section_rewrites": [
    {{
      "section": "섹션명",
      "before": "기존 내용 요약",
      "after": "개선된 내용 초안 (2~3문장)",
      "reason": "개선 이유"
    }}
  ],
  "faq_additions": [
    {{"question": "질문", "answer": "답변 (2~3문장)"}}
  ]
}}

중요: JSON만 응답하세요."""

        raw = self.run(prompt, max_iterations=2)
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            return json.loads(match.group())
        return {}


# ── Rule-based rewrite helpers ────────────────────────────────────────────────

def _rewrite_title(brief: dict, current: dict) -> str:
    cluster = brief.get("primary_query_cluster", "")
    intent = brief.get("search_intent", "")
    year = datetime.now().year

    intent_prefix = {
        "commercial_investigation": f"{year} {cluster}",
        "commercial": f"{cluster} 추천",
        "informational": f"{cluster} 완전 가이드",
        "transactional": f"{cluster} 구매 가이드",
        "mixed": f"{cluster} 효과와 사용법",
    }.get(intent, cluster)

    secondary = brief.get("secondary_queries", [])
    suffix = f" — {secondary[0]}" if secondary else ""
    title = f"{intent_prefix}{suffix}"
    return title[:55]


def _rewrite_meta(brief: dict, current: dict) -> str:
    cluster = brief.get("primary_query_cluster", "")
    secondary = brief.get("secondary_queries", [])
    sections = brief.get("recommended_sections", [])

    secondary_text = f" {secondary[0]}부터 " if secondary else " "
    section_text = f"{sections[0]} 포함." if sections else ""
    meta = f"{cluster}에 대한 전문 가이드.{secondary_text}{section_text} 뷰티랩이 정리했습니다."
    return meta[:155]


def _rewrite_h1(brief: dict, current: dict) -> str:
    cluster = brief.get("primary_query_cluster", "")
    intent = brief.get("search_intent", "")

    if "informational" in intent:
        return f"{cluster}: 전문가가 알려주는 완벽 가이드"
    elif "commercial" in intent:
        return f"{cluster} 추천 및 선택 가이드"
    else:
        return f"{cluster} — 효과, 사용법, 주의사항"


def _build_section_rewrites(brief: dict, current: dict) -> list[dict]:
    rewrites = []
    recommended = brief.get("recommended_sections", [])
    existing = [s["heading"] for s in current.get("body_sections", [])]

    for section in recommended[:4]:
        is_existing = any(section[:8] in e for e in existing)
        if is_existing:
            rewrites.append({
                "section": section,
                "before": f"기존 '{section}' 섹션 — 정보 부족 또는 최신화 필요",
                "after": f"'{section}'에 대한 구체적 설명, 수치 데이터, FAQ 보강 필요",
                "reason": "검색 의도 정렬 및 E-E-A-T 강화",
            })
        else:
            rewrites.append({
                "section": section,
                "before": "(섹션 없음)",
                "after": f"신규 섹션 '{section}' 추가 — 사용자 검색 의도 충족을 위해 필요",
                "reason": "콘텐츠 갭 해소",
            })
    return rewrites


def _compute_quality_score(brief: dict, title: str, meta: str, sections: list[dict]) -> float:
    score = 0.0
    # Title length
    if 20 <= len(title) <= 55:
        score += 0.2
    # Meta length
    if 80 <= len(meta) <= 155:
        score += 0.2
    # Primary keyword in title
    cluster = brief.get("primary_query_cluster", "").split()[0]
    if cluster and cluster in title:
        score += 0.2
    # Has sections
    if len(sections) >= 2:
        score += 0.2
    # Has FAQs in brief
    if brief.get("faq_items"):
        score += 0.2
    return round(min(score, 1.0), 2)
