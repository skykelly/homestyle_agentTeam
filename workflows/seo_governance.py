"""
SEO Governance & Brand Safety Workflow — Phase 4 extension.
Audits ContentDrafts before they enter the approval queue.

Check categories (from design spec 5.11):
1. 과장 표현 (overstatement)
2. 허위 성능 주장 (false performance claim)
3. 경쟁사 비방 (competitor disparagement)
4. 의료/금융/법률 고위험 표현 (YMYL risk)
5. 개인정보 포함 여부 (PII)
6. 저작권 위험 (copyright)
7. 키워드 스터핑 (keyword stuffing)
8. AI 생성 티 나는 저품질 문장 (AI-sounding text)
9. 브랜드 톤앤매너 위반 (brand tone)
"""

import re
from datetime import datetime

from models.agent_run import AgentRun
from models.seo_models import KnowledgeItem
from storage.repository import save_agent_run
from storage.seo_repository import (
    get_content_draft,
    list_content_drafts,
    save_content_draft,
    save_knowledge_item,
    update_recommendation_status,
)
from workflows.base import BaseWorkflow


# ── Rule-based patterns ───────────────────────────────────────────────────────

# 1. 과장 표현
_OVERSTATEMENT_PATTERNS = [
    (r"세계\s*(최고|최강|1위|넘버원)", "과장 표현: '세계 최고/최강' 사용 금지"),
    (r"100%\s*(효과|보장|확실)", "과장 표현: 100% 효과/보장 금지"),
    (r"완벽한?\s*(피부|효과|결과)", "과장 표현: '완벽한 효과' 등 금지"),
    (r"기적(적)?|마법(적)?", "과장 표현: '기적' '마법' 등 금지"),
    (r"즉시|바로\s*(효과|변화|개선)", "과장 표현: 즉각 효과 주장 금지"),
]

# 2. 허위 성능 주장
_FALSE_CLAIM_PATTERNS = [
    (r"임상\s*(실험|시험|연구)\s*(완료|증명|입증)", "허위 주장: 임상 증명 표현 — 근거 필요"),
    (r"피부과\s*(추천|인증|검증)", "허위 주장: 피부과 인증 표현 — 공식 인증 아닌 경우 금지"),
    (r"FDA\s*(승인|인증)", "허위 주장: FDA 승인 표현 — 공식 인증 여부 확인 필요"),
    (r"주름\s*(제거|없애|사라)", "허위 주장: 주름 제거 주장 — '개선에 도움' 수준으로 완화 필요"),
]

# 3. 경쟁사 비방
_COMPETITOR_PATTERNS = [
    (r"(타사|경쟁사|다른\s*브랜드).{0,20}(나쁜|별로|문제|위험|해롭)", "경쟁사 비방: 부정적 비교 표현 금지"),
    (r"(타사|경쟁사)\s*(제품|브랜드).{0,20}(가짜|조작|사기)", "경쟁사 비방: 허위 사실 주장 법적 위험"),
]

# 4. YMYL 고위험 표현
_YMYL_PATTERNS = [
    (r"(치료|치유|완치|병원\s*불필요)", "YMYL 위험: 의료적 치료 주장 금지"),
    (r"(의약품|처방|약사|의사)\s*(없이|대신|대체)", "YMYL 위험: 의료 대체 표현 금지"),
    (r"(암|당뇨|고혈압).{0,20}(효과|치료|예방)", "YMYL 위험: 질병 예방/치료 주장 금지"),
]

# 7. 키워드 스터핑 (동일 단어 5회+ 반복)
def _check_keyword_stuffing(text: str) -> list[str]:
    if not text:
        return []
    words = re.findall(r'[가-힣]{2,}', text)
    if not words:
        return []
    from collections import Counter
    counter = Counter(words)
    total = len(words) or 1
    flags = []
    for word, count in counter.items():
        density = count / total
        if count >= 5 and density > 0.1:
            flags.append(f"키워드 스터핑: '{word}' {count}회 반복 ({density*100:.0f}%)")
    return flags

# 8. AI 생성 티 나는 패턴
_AI_SOUNDING_PATTERNS = [
    (r"물론입니다|알겠습니다|도움이\s*되었으면", "AI 어투: 챗봇 응답 패턴 제거 필요"),
    (r"다음과\s*같습니다\s*[:：]", "AI 어투: 기계적 문장 구조"),
    (r"위와\s*같이|아래와\s*같이", "AI 어투: 기계적 참조 표현"),
    (r"첫째,\s*둘째,\s*셋째", "AI 어투: 번호 나열 패턴 (자연스럽게 수정 권장)"),
]

# 9. 브랜드 톤앤매너 위반
_BRAND_TONE_PATTERNS = [
    (r"존나|ㅋㅋ|ㅎㅎ|ㄷㄷ|ㅠㅠ", "브랜드 톤: 비격식 표현 금지"),
    (r"엄청\s*(좋음|짱|대박)", "브랜드 톤: 구어체 과장 표현 지양"),
    (r"욕설|비속어", "브랜드 톤: 비속어 절대 금지"),
]


def _run_pattern_checks(text: str, patterns: list[tuple]) -> list[str]:
    flags = []
    for pattern, message in patterns:
        if re.search(pattern, text):
            flags.append(message)
    return flags


def audit_text(text: str) -> dict:
    """
    Run all rule-based governance checks on a text string.
    Returns flags list and a safety score (1.0 = clean, 0.0 = many violations).
    """
    flags = []
    flags += _run_pattern_checks(text, _OVERSTATEMENT_PATTERNS)
    flags += _run_pattern_checks(text, _FALSE_CLAIM_PATTERNS)
    flags += _run_pattern_checks(text, _COMPETITOR_PATTERNS)
    flags += _run_pattern_checks(text, _YMYL_PATTERNS)
    flags += _check_keyword_stuffing(text)
    flags += _run_pattern_checks(text, _AI_SOUNDING_PATTERNS)
    flags += _run_pattern_checks(text, _BRAND_TONE_PATTERNS)

    # Safety score: starts at 1.0, deduct per flag
    critical_flags = [f for f in flags if any(kw in f for kw in ["허위", "YMYL", "경쟁사 비방", "키워드 스터핑"])]
    warning_flags = [f for f in flags if f not in critical_flags]

    score = 1.0 - (len(critical_flags) * 0.2) - (len(warning_flags) * 0.05)
    score = round(max(0.0, min(1.0, score)), 2)

    return {
        "flags": flags,
        "critical_count": len(critical_flags),
        "warning_count": len(warning_flags),
        "safety_score": score,
        "passed": score >= 0.7 and len(critical_flags) == 0,
    }


class SEOGovernanceWorkflow(BaseWorkflow):
    """
    Audits ContentDrafts for brand safety before approval.
    - Rule-based checks run always
    - LLM deep-review optional (for borderline cases)
    Updates draft.brand_safety_score and draft.governance_flags in storage.
    """

    system_prompt = """당신은 뷰티랩 브랜드 세이프티 검수 에이전트입니다.

검수 원칙:
1. 과장/허위 주장이 있으면 반드시 플래그 처리한다
2. 의료/법률/금융 고위험 표현은 엄격히 차단한다
3. 브랜드 톤앤매너(전문적, 친근함, 사실 기반)를 기준으로 판단한다
4. 단순히 "좋지 않다"가 아니라 구체적인 수정 방향을 제시한다
5. 통과/실패 판정에 명확한 근거를 제공한다

허용 기준:
- "피부 장벽 강화에 도움을 줍니다" → 허용
- "주름 개선에 효과적입니다" → 근거 있으면 허용
- "피부를 완벽하게 재생합니다" → 불허 (과장)
- "세계 최고의 세럼" → 불허 (근거 없는 최상급)"""

    allowed_tools = []

    def audit_draft(self, draft_id: str, llm_augment: bool = False) -> dict:
        """
        Audit a single ContentDraft. Updates its brand_safety_score and governance_flags.
        Returns audit result including pass/fail and all flags.
        """
        run = AgentRun(
            workflow_name="seo_governance",
            trigger="manual",
            input_params={"draft_id": draft_id},
        )
        save_agent_run(run)

        draft = get_content_draft(draft_id)
        if not draft:
            run.fail(f"Draft {draft_id} not found")
            save_agent_run(run)
            return {"error": f"draft_id '{draft_id}' not found"}

        # Collect all text to check
        all_text_parts = [
            draft.get("title_after", ""),
            draft.get("meta_after", ""),
            draft.get("h1_after", ""),
        ]
        for s in draft.get("section_rewrites", []):
            all_text_parts.append(s.get("after", ""))
        for faq in draft.get("faq_additions", []):
            all_text_parts.append(faq.get("question", "") + " " + faq.get("answer", ""))

        combined_text = " ".join(all_text_parts)

        # Rule-based audit
        result = audit_text(combined_text)
        flags = result["flags"]
        safety_score = result["safety_score"]
        passed = result["passed"]

        # LLM deep review for borderline cases
        llm_feedback = ""
        if llm_augment and (0.5 <= safety_score <= 0.85 or result["warning_count"] > 2):
            llm_feedback = self._llm_review(draft, flags)
            if llm_feedback:
                flags.append(f"[LLM 검토] {llm_feedback[:200]}")

        # Update draft in storage
        from storage.seo_repository import _load, _save, DRAFTS_FILE, _LOCK
        with _LOCK:
            items = _load(DRAFTS_FILE)
            for item in items:
                if item.get("draft_id") == draft_id:
                    item["brand_safety_score"] = safety_score
                    item["governance_flags"] = flags
                    item["status"] = "governance_checked"
                    break
            _save(DRAFTS_FILE, items)

        # Save to knowledge base if there are notable flags
        if flags:
            ki = KnowledgeItem(
                source_type="governance",
                source_id=draft_id,
                title=f"거버넌스 검수: {draft['target_url']}",
                summary=f"안전점수 {safety_score:.2f} | 플래그 {len(flags)}건 | {'통과' if passed else '수정 필요'}",
                content="\n".join(flags),
                tags=["governance", "brand_safety", draft["target_url"].split("/")[1] if "/" in draft["target_url"] else ""],
            )
            save_knowledge_item(ki)

        run.complete(output_summary=f"검수 완료: score={safety_score:.2f}, {'PASS' if passed else 'FAIL'}")
        save_agent_run(run)

        self._log(f"  [Governance] {draft_id}: score={safety_score:.2f} | {'✓ PASS' if passed else '✗ FAIL'} | flags={len(flags)}")

        return {
            "run_id": run.run_id,
            "draft_id": draft_id,
            "target_url": draft["target_url"],
            "safety_score": safety_score,
            "passed": passed,
            "critical_count": result["critical_count"],
            "warning_count": result["warning_count"],
            "flags": flags,
            "llm_feedback": llm_feedback,
            "recommendation": "승인 가능" if passed else "수정 후 재검토 필요",
        }

    def audit_all_pending_drafts(self, llm_augment: bool = False) -> dict:
        """Audit all drafts in 'draft' or 'governance_checked' status."""
        drafts = list_content_drafts(status="draft") + list_content_drafts(status="governance_checked")
        results = []
        passed_count = 0

        for draft in drafts:
            result = self.audit_draft(draft["draft_id"], llm_augment=llm_augment)
            results.append(result)
            if result.get("passed"):
                passed_count += 1

        return {
            "audited": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "results": results,
        }

    def get_governance_summary(self) -> dict:
        """Summary of governance state across all drafts."""
        all_drafts = list_content_drafts()
        status_counts: dict[str, int] = {}
        scores = []

        for d in all_drafts:
            s = d.get("status", "unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
            score = d.get("brand_safety_score", 0)
            if score:
                scores.append(score)

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "total_drafts": len(all_drafts),
            "by_status": status_counts,
            "avg_safety_score": avg_score,
            "pending_governance": status_counts.get("draft", 0),
        }

    def _llm_review(self, draft: dict, existing_flags: list[str]) -> str:
        """LLM deep-dive for borderline governance cases."""
        title = draft.get("title_after", "")
        meta = draft.get("meta_after", "")
        sections_text = "\n".join(
            f"- {s.get('after', '')}"
            for s in draft.get("section_rewrites", [])[:3]
        )

        flags_text = "\n".join(f"- {f}" for f in existing_flags[:5]) if existing_flags else "없음"

        prompt = f"""다음 SEO 콘텐츠를 브랜드 세이프티 관점에서 검토하세요.

URL: {draft['target_url']}
Title: {title}
Meta: {meta}
주요 섹션:
{sections_text}

이미 발견된 플래그:
{flags_text}

다음을 확인해주세요:
1. 추가로 발견되는 과장/허위 주장이 있나요?
2. 브랜드 톤앤매너(전문적, 친근, 사실 기반)에 맞나요?
3. 수정이 필요하다면 구체적인 대안을 제시하세요.

50자 이내로 핵심 피드백만 작성하세요."""

        return self.run(prompt, max_iterations=1)
