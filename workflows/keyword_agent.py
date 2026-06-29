"""
Keyword & Query Agent — Phase 3.

Analyzes GSC data to:
1. Cluster related queries into topic groups
2. Classify search intent per cluster
3. Find keyword gaps (high impressions, low CTR / low rank)
4. Score content opportunities by potential traffic impact
5. Recommend priority keywords for content briefs
"""

import json
import re
from collections import defaultdict
from datetime import datetime

from models.agent_run import AgentRun
from models.seo_models import KnowledgeItem
from storage.repository import save_agent_run
from storage.seo_repository import save_knowledge_item
from workflows.base import BaseWorkflow


# ── Intent classification rules ─────────────────────────────────────────────

_INFORMATIONAL_SIGNALS = [
    "이란", "이란?", "이란 무엇", "효과", "뜻", "의미", "원인", "방법", "하는법",
    "사용법", "차이", "비교", "추천", "가이드", "완전", "총정리", "정리",
]
_COMMERCIAL_SIGNALS = [
    "추천", "순위", "best", "top", "좋은", "어떤", "비교", "vs",
    "후기", "리뷰", "평점", "별점", "선택",
]
_TRANSACTIONAL_SIGNALS = [
    "구매", "구입", "살", "사다", "주문", "가격", "얼마", "할인", "세일",
    "쿠폰", "최저가", "배송", "무료",
]
_NAVIGATIONAL_SIGNALS = ["뷰티랩", "beautylab", "공식", "홈페이지", "사이트"]


def _classify_intent(query: str) -> str:
    q = query.lower()
    if any(s in q for s in _NAVIGATIONAL_SIGNALS):
        return "navigational"
    if any(s in q for s in _TRANSACTIONAL_SIGNALS):
        return "transactional"
    if any(s in q for s in _COMMERCIAL_SIGNALS):
        return "commercial_investigation"
    if any(s in q for s in _INFORMATIONAL_SIGNALS):
        return "informational"
    return "mixed"


def _extract_root_term(query: str) -> str:
    """Strip intent modifiers to find the core topic."""
    stop = [
        "이란", "이란?", "란", "추천", "순위", "효과", "사용법", "하는법",
        "가이드", "구매", "구입", "가격", "할인", "리뷰", "후기", "비교",
        "좋은", "어떤", "방법", "총정리", "완전", "정리",
    ]
    result = query
    for s in stop:
        result = result.replace(s, "").strip()
    return result if len(result) >= 2 else query


def _cluster_queries(rows: list[dict]) -> dict[str, list[dict]]:
    """Group queries by shared root term (2-gram overlap)."""
    clusters: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        root = _extract_root_term(row["query"])
        clusters[root].append(row)
    # Merge clusters with very similar roots
    final: dict[str, list[dict]] = {}
    used = set()
    keys = sorted(clusters.keys(), key=lambda k: -sum(r["impressions"] for r in clusters[k]))
    for k in keys:
        if k in used:
            continue
        group = list(clusters[k])
        for k2 in keys:
            if k2 == k or k2 in used:
                continue
            if k2 in k or k in k2 or (len(k) >= 2 and len(k2) >= 2 and k[:3] == k2[:3]):
                group.extend(clusters[k2])
                used.add(k2)
        final[k] = group
        used.add(k)
    return final


def _score_cluster(rows: list[dict]) -> float:
    """Score a cluster by total impressions * (1 - avg_ctr) — potential upside."""
    if not rows:
        return 0.0
    total_imp = sum(r["impressions"] for r in rows)
    avg_ctr = sum(r["ctr"] for r in rows) / len(rows)
    avg_pos = sum(r["position"] for r in rows) / len(rows)
    # Higher score = more impressions + lower CTR (room to improve) + lower position (ranking gap)
    score = total_imp * (1 - avg_ctr) * (avg_pos / 10)
    return round(score, 1)


class KeywordQueryAgent(BaseWorkflow):
    """
    Keyword & Query analysis agent.
    Reads GSC data (real or mock), clusters queries, classifies intent,
    and surfaces actionable keyword opportunities.
    """

    system_prompt = """당신은 한국 뷰티 이커머스 키워드 분석 전문가입니다.

역할:
1. GSC 데이터에서 의미 있는 키워드 클러스터를 도출한다.
2. 각 클러스터의 검색 의도를 정확히 분류한다.
3. CTR 개선 여지가 큰 키워드 갭을 발견한다.
4. 우선순위 높은 키워드를 콘텐츠 브리프 작성에 연결한다.

분석 기준:
- 노출수 100 이상인 쿼리를 대상으로 한다.
- CTR 2% 미만이면서 노출수 500 이상 → 기회 키워드
- 평균 순위 4~15 → 페이지1 진입 가능 구간
- 같은 의도의 쿼리가 여러 URL에 분산 → 카니발라이제이션 위험"""

    allowed_tools = ["get_seo_overview", "get_seo_query_opportunities"]

    def analyze(
        self,
        min_impressions: int = 100,
        gap_ctr_threshold: float = 0.02,
        llm_augment: bool = True,
    ) -> dict:
        """
        Full keyword analysis pipeline.
        Returns clusters, intent breakdown, gap keywords, and opportunity list.
        """
        run = AgentRun(
            workflow_name="keyword_agent",
            trigger="manual",
            input_params={"min_impressions": min_impressions, "llm_augment": llm_augment},
        )
        save_agent_run(run)

        # ── Fetch GSC data ────────────────────────────────────────────────
        from connectors.gsc_connector import GSCConnector
        raw = GSCConnector().get_data()
        gsc_rows = [r for r in raw["data"] if r["impressions"] >= min_impressions]
        data_source = raw["source"]

        # ── Cluster + classify ────────────────────────────────────────────
        clusters = _cluster_queries(gsc_rows)
        cluster_analysis = []
        for root_term, rows in clusters.items():
            intent = _classify_intent(root_term)
            votes = [_classify_intent(r["query"]) for r in rows]
            # Majority vote
            from collections import Counter
            intent = Counter(votes).most_common(1)[0][0]

            total_imp = sum(r["impressions"] for r in rows)
            total_clicks = sum(r["clicks"] for r in rows)
            avg_ctr = total_clicks / max(total_imp, 1)
            avg_pos = sum(r["position"] for r in rows) / len(rows)
            opp_score = _score_cluster(rows)
            urls = list({r["url"] for r in rows})

            cluster_analysis.append({
                "cluster": root_term,
                "query_count": len(rows),
                "queries": [r["query"] for r in rows[:5]],
                "intent": intent,
                "total_impressions": total_imp,
                "total_clicks": total_clicks,
                "avg_ctr": round(avg_ctr, 4),
                "avg_position": round(avg_pos, 1),
                "opportunity_score": opp_score,
                "urls": urls,
                "cannibalization_risk": len(urls) > 2,
            })

        cluster_analysis.sort(key=lambda x: -x["opportunity_score"])

        # ── Keyword gaps ──────────────────────────────────────────────────
        gaps = [
            {
                "query": r["query"],
                "url": r["url"],
                "impressions": r["impressions"],
                "clicks": r["clicks"],
                "ctr": round(r["ctr"], 4),
                "position": round(r["position"], 1),
                "gap_type": (
                    "position_gap" if r["position"] > 10
                    else "ctr_gap" if r["ctr"] < gap_ctr_threshold
                    else "mixed_gap"
                ),
                "estimated_click_gain": int(
                    r["impressions"] * (0.10 - r["ctr"])
                ) if r["ctr"] < 0.10 else 0,
            }
            for r in gsc_rows
            if r["ctr"] < gap_ctr_threshold and r["impressions"] >= 200
        ]
        gaps.sort(key=lambda x: -x["estimated_click_gain"])

        # ── Intent breakdown ──────────────────────────────────────────────
        intent_counts: dict[str, int] = {}
        for c in cluster_analysis:
            intent_counts[c["intent"]] = intent_counts.get(c["intent"], 0) + 1

        # ── Top opportunities ─────────────────────────────────────────────
        top_opportunities = [
            {
                "cluster": c["cluster"],
                "intent": c["intent"],
                "opportunity_score": c["opportunity_score"],
                "avg_position": c["avg_position"],
                "total_impressions": c["total_impressions"],
                "action": (
                    "신규 콘텐츠 작성"
                    if c["avg_ctr"] < 0.01
                    else "제목/메타 최적화" if c["avg_position"] <= 10
                    else "순위 개선 필요"
                ),
            }
            for c in cluster_analysis[:10]
        ]

        # ── LLM enrichment ────────────────────────────────────────────────
        llm_insights = ""
        if llm_augment and top_opportunities:
            try:
                llm_insights = self._llm_insights(top_opportunities, gaps[:5])
            except Exception:
                pass

        # ── Save to knowledge base ────────────────────────────────────────
        ki = KnowledgeItem(
            source_type="keyword_analysis",
            source_id=run.run_id,
            title=f"키워드 분석 — {datetime.now().strftime('%Y-%m-%d')}",
            summary=(
                f"클러스터 {len(cluster_analysis)}개 | "
                f"갭 키워드 {len(gaps)}개 | "
                f"상위 기회: {top_opportunities[0]['cluster'] if top_opportunities else '-'}"
            ),
            content=json.dumps(top_opportunities[:5], ensure_ascii=False),
            tags=["keyword_analysis", "gsc", data_source],
        )
        save_knowledge_item(ki)

        run.complete(
            output_summary=(
                f"클러스터 {len(cluster_analysis)}개 분석 | "
                f"갭 {len(gaps)}개 | 데이터 소스: {data_source}"
            )
        )
        save_agent_run(run)

        self._log(
            f"  [Keyword] {len(cluster_analysis)} clusters | "
            f"{len(gaps)} gaps | source={data_source}"
        )

        return {
            "run_id": run.run_id,
            "data_source": data_source,
            "total_queries_analyzed": len(gsc_rows),
            "clusters": cluster_analysis,
            "keyword_gaps": gaps[:20],
            "intent_breakdown": intent_counts,
            "top_opportunities": top_opportunities,
            "llm_insights": llm_insights,
            "summary": {
                "total_clusters": len(cluster_analysis),
                "total_gaps": len(gaps),
                "high_opportunity_clusters": sum(
                    1 for c in cluster_analysis if c["opportunity_score"] > 5000
                ),
                "cannibalization_risks": sum(
                    1 for c in cluster_analysis if c["cannibalization_risk"]
                ),
            },
        }

    def get_cluster_for_brief(self, min_opportunity_score: float = 1000.0) -> list[dict]:
        """
        Return top clusters suitable for ContentBrief generation.
        Filters for commercial/informational intent with high opportunity score.
        """
        result = self.analyze(llm_augment=False)
        return [
            c for c in result["clusters"]
            if c["opportunity_score"] >= min_opportunity_score
            and c["intent"] in ("informational", "commercial_investigation", "mixed")
        ][:10]

    def _llm_insights(self, top_opps: list[dict], gaps: list[dict]) -> str:
        prompt = f"""다음 SEO 키워드 분석 결과를 검토하고 핵심 인사이트를 제공하세요.

상위 기회 클러스터:
{chr(10).join(f"- {o['cluster']} (의도:{o['intent']}, 노출:{o['total_impressions']}, 순위:{o['avg_position']})" for o in top_opps[:5])}

CTR 갭 키워드 (노출 많고 CTR 낮음):
{chr(10).join(f"- {g['query']} (노출:{g['impressions']}, CTR:{g['ctr']:.1%}, 순위:{g['position']})" for g in gaps[:5])}

다음에 집중하세요:
1. 가장 빠른 CTR 개선이 가능한 1~2개 키워드
2. 새 콘텐츠가 필요한 키워드 갭
3. 카니발라이제이션 위험 여부

50자 이내로 핵심만 요약하세요."""
        return self.run(prompt, max_iterations=1)
