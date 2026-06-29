"""
SEO Experiment & Measurement Workflow — Phase 6.
Tracks before/after metrics for SEO changes.
Records learning summaries and saves to KnowledgeItems.
"""

from datetime import datetime, timedelta

from data.seo_mock_data import get_gsc_queries, get_ga4_landing, SITE_BENCHMARKS
from models.agent_run import AgentRun
from models.seo_models import SEOExperiment, KnowledgeItem
from storage.repository import save_agent_run
from storage.seo_repository import save_experiment, save_knowledge_item, list_experiments
from workflows.base import BaseWorkflow


class SEOExperimentWorkflow(BaseWorkflow):
    """
    Manages SEO experiments:
    - Baseline capture before changes
    - Result comparison after 7/14/28 days
    - Learning summary generation
    - Knowledge item accumulation
    """

    system_prompt = """You are an SEO Experiment Analyst for Korean beauty e-commerce.

Your role is to:
1. Capture accurate baseline metrics before any SEO change
2. Compare before/after metrics objectively after the experiment period
3. Determine if results are statistically meaningful (not random noise)
4. Extract actionable learnings from both successes and failures
5. Document findings in Knowledge Items for future decision-making

Experiment evaluation criteria:
- Success: clicks ▲15%+ OR position ▲2+ positions after 28 days
- Neutral: changes within ±10% — inconclusive
- Regression: clicks ▼15%+ OR position ▼2+ positions — rollback signal

Korean market seasonality to consider:
- Summer (5-8월): skincare focus, SPF-related queries spike
- Holiday periods: Chuseok, Seollal — traffic patterns shift
- Year-end: beauty gift sets, review content peaks"""

    allowed_tools = ["get_seo_overview", "get_seo_query_opportunities"]

    def create_experiment_baselines(self, top_n: int = 5) -> dict:
        """
        Create experiment baselines for top SEO opportunities.
        Captures current metrics before any change is applied.
        """
        run = AgentRun(
            workflow_name="seo_experiment_baseline",
            trigger="manual",
            input_params={"top_n": top_n},
        )
        save_agent_run(run)

        # Get top opportunities to track
        from rules.seo_rules import run_all_seo_rules
        hits = run_all_seo_rules()

        # Focus on actionable, non-technical hits
        trackable = [
            h for h in hits
            if h.opportunity_type in ("ctr_improvement", "ranking_boost", "content_refresh")
        ][:top_n]

        experiments = []
        for hit in trackable:
            url = hit.target_url
            query = hit.target_queries[0] if hit.target_queries else ""

            # Gather baseline metrics
            gsc_rows = [r for r in get_gsc_queries() if r.url == url]
            ga4_rows = get_ga4_landing(url)

            clicks_28d = sum(r.clicks for r in gsc_rows)
            impressions_28d = sum(r.impressions for r in gsc_rows)
            avg_ctr = sum(r.ctr for r in gsc_rows) / len(gsc_rows) if gsc_rows else 0
            avg_position = sum(r.position for r in gsc_rows) / len(gsc_rows) if gsc_rows else 0
            sessions = ga4_rows[0].sessions if ga4_rows else 0
            conversions = ga4_rows[0].conversions if ga4_rows else 0
            revenue = ga4_rows[0].revenue_krw if ga4_rows else 0

            baseline_metrics = {
                "clicks_28d": clicks_28d,
                "impressions_28d": impressions_28d,
                "ctr": round(avg_ctr, 4),
                "position": round(avg_position, 1),
                "sessions": sessions,
                "conversions": conversions,
                "revenue_krw": revenue,
                "primary_query": query,
            }

            change_type = {
                "ctr_improvement": "title_meta",
                "ranking_boost": "content_update",
                "content_refresh": "content_update",
            }.get(hit.opportunity_type, "other")

            today = datetime.now().strftime("%Y-%m-%d")
            exp = SEOExperiment(
                target_url=url,
                change_type=change_type,
                change_description=hit.recommendation,
                baseline_metrics=baseline_metrics,
                baseline_start_date=(datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d"),
                baseline_end_date=today,
                experiment_start_date=today,
                experiment_end_date=(datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d"),
            )

            save_experiment(exp)
            experiments.append(exp)
            run.recommendations_generated.append(exp.experiment_id)
            self._log(f"  [Experiment] Baseline set: {exp.experiment_id} → {url}")

        run.complete(output_summary=f"{len(experiments)}개 실험 베이스라인 설정")
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "baselines_created": len(experiments),
            "experiments": [e.to_dict() for e in experiments],
        }

    def simulate_results_and_learn(self, llm_augment: bool = True) -> dict:
        """
        Simulate experiment results (mock) and generate learning summaries.
        In production, this would pull real GSC data after the experiment period.
        """
        run = AgentRun(
            workflow_name="seo_experiment_results",
            trigger="manual",
            input_params={"mode": "simulation"},
        )
        save_agent_run(run)

        existing = list_experiments(status="baseline_set")
        if not existing:
            # Create some simulated completed experiments for demo
            existing = _create_demo_completed_experiments()

        knowledge_items = []
        completed_experiments = []

        for exp_dict in existing[:5]:
            # Simulate result metrics (in production: pull real GSC data)
            baseline = exp_dict.get("baseline_metrics", {})
            sim_result = _simulate_experiment_result(baseline, exp_dict.get("change_type", ""))

            # Reconstruct experiment object
            exp = SEOExperiment(
                target_url=exp_dict["target_url"],
                change_type=exp_dict["change_type"],
                change_description=exp_dict["change_description"],
                baseline_metrics=baseline,
                baseline_start_date=exp_dict["baseline_start_date"],
                baseline_end_date=exp_dict["baseline_end_date"],
                experiment_start_date=exp_dict.get("experiment_start_date"),
                experiment_end_date=(datetime.now()).strftime("%Y-%m-%d"),
                result_metrics=sim_result["metrics"],
                outcome=sim_result["outcome"],
                learning_summary=sim_result["learning"],
            )
            exp.experiment_id = exp_dict.get("experiment_id", exp.experiment_id)
            exp.status = "completed"
            save_experiment(exp)

            # Create knowledge item from learning
            delta = exp.compute_delta()
            knowledge = KnowledgeItem(
                source_type="experiment",
                source_id=exp.experiment_id,
                title=f"{exp.change_type} 실험: {exp.target_url}",
                summary=sim_result["learning"],
                content=(
                    f"변경 유형: {exp.change_type}\n"
                    f"URL: {exp.target_url}\n"
                    f"결과: {sim_result['outcome']}\n"
                    f"클릭 변화: {delta.get('clicks_delta_pct', 0):+.1f}%\n"
                    f"포지션 변화: {delta.get('position_delta', 0):+.1f}\n"
                    f"학습: {sim_result['learning']}"
                ),
                tags=["experiment", exp.change_type, exp.target_url.split("/")[1] if "/" in exp.target_url else ""],
            )
            save_knowledge_item(knowledge)
            knowledge_items.append(knowledge)
            completed_experiments.append(exp)

            self._log(f"  [Experiment] Completed: {exp.experiment_id} → outcome={sim_result['outcome']}")

        # LLM: Generate strategic learnings
        llm_learning = ""
        if completed_experiments and llm_augment:
            successes = [e for e in completed_experiments if e.outcome == "success"]
            regressions = [e for e in completed_experiments if e.outcome == "regression"]

            prompt = f"""다음 SEO 실험 결과에서 전략적 인사이트를 도출해주세요.

완료된 실험: {len(completed_experiments)}개
성공: {len(successes)}개 | 중립: {len(completed_experiments) - len(successes) - len(regressions)}개 | 퇴보: {len(regressions)}개

실험 상세:
{chr(10).join(f'  - {e.target_url} [{e.change_type}]: {e.outcome} (클릭 {e.compute_delta().get("clicks_delta_pct", 0):+.1f}%)' for e in completed_experiments)}

분석 요청:
1. 성공 패턴 — 어떤 변경이 효과적이었나?
2. 실패 원인 — 무엇이 작동하지 않았나?
3. 다음 실험 사이클을 위한 가설 3개
4. 한국 뷰티 시장에서 특히 효과적인 SEO 전술

한국어로 작성하세요."""

            llm_learning = self.run(prompt, max_iterations=2)

            # Save LLM insight as knowledge item
            if llm_learning:
                ki = KnowledgeItem(
                    source_type="llm_insight",
                    title=f"SEO 실험 전략 학습 ({datetime.now().strftime('%Y-%m-%d')})",
                    summary=llm_learning[:200],
                    content=llm_learning,
                    tags=["experiment_learning", "strategy", "beauty_seo"],
                )
                save_knowledge_item(ki)
                knowledge_items.append(ki)

        run.complete(
            output_summary=f"{len(completed_experiments)}개 실험 완료, {len(knowledge_items)}개 Knowledge Item 저장"
        )
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "experiments_completed": len(completed_experiments),
            "knowledge_items_created": len(knowledge_items),
            "results": [e.to_dict() for e in completed_experiments],
            "knowledge_items": [ki.to_dict() for ki in knowledge_items],
            "llm_learning": llm_learning,
        }


# ── Simulation helpers ────────────────────────────────────────────────────────

def _simulate_experiment_result(baseline: dict, change_type: str) -> dict:
    """Simulate realistic experiment results for demo purposes."""
    import random

    if change_type == "title_meta":
        # Title/meta changes typically improve CTR
        click_multiplier = random.uniform(1.15, 1.45)
        pos_improvement = random.uniform(-1.5, -0.5)
        outcome = "success"
        learning = f"제목/메타 설명 개선으로 CTR이 {round((click_multiplier - 1) * 100):.0f}% 향상됨. 검색 의도 정렬이 핵심 성공 요인."
    elif change_type == "content_update":
        # Content updates take longer, mixed results
        click_multiplier = random.uniform(0.95, 1.35)
        pos_improvement = random.uniform(-2.5, 0.5)
        outcome = "success" if click_multiplier > 1.15 else ("regression" if click_multiplier < 0.95 else "neutral")
        learning = f"콘텐츠 업데이트 후 {'긍정적' if outcome == 'success' else '제한적'} 결과. {'E-E-A-T 강화와 FAQ 추가가 효과적.' if outcome == 'success' else '주제 범위 확대보다 깊이 개선이 더 효과적일 수 있음.'}"
    else:
        click_multiplier = random.uniform(0.98, 1.20)
        pos_improvement = random.uniform(-1.0, 0.3)
        outcome = "success" if click_multiplier > 1.1 else "neutral"
        learning = f"기술적 개선은 크롤 효율을 높이지만 직접적인 트래픽 효과는 중장기적으로 나타남."

    result_clicks = int(baseline.get("clicks_28d", 500) * click_multiplier)
    result_impressions = int(baseline.get("impressions_28d", 10000) * random.uniform(0.95, 1.15))
    result_position = max(1.0, baseline.get("position", 10) + pos_improvement)
    result_ctr = result_clicks / result_impressions if result_impressions else 0

    return {
        "outcome": outcome,
        "metrics": {
            "clicks_28d": result_clicks,
            "impressions_28d": result_impressions,
            "ctr": round(result_ctr, 4),
            "position": round(result_position, 1),
        },
        "learning": learning,
    }


def _create_demo_completed_experiments() -> list[dict]:
    """Create demo experiment data when no existing experiments are found."""
    demo_urls = [
        ("/skincare/collagen-serum-guide", "title_meta", "제목 태그 및 메타 설명 개선"),
        ("/skincare/hyaluronic-acid", "content_update", "히알루론산 콘텐츠 업데이트 및 FAQ 추가"),
        ("/faq/serum-vs-ampoule", "title_meta", "FAQPage 스키마 추가 및 메타 개선"),
    ]
    today = datetime.now().strftime("%Y-%m-%d")
    past_28 = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    items = []
    for url, change_type, desc in demo_urls:
        gsc = [r for r in get_gsc_queries() if r.url == url]
        baseline = {
            "clicks_28d": sum(r.clicks for r in gsc),
            "impressions_28d": sum(r.impressions for r in gsc),
            "ctr": gsc[0].ctr if gsc else 0.01,
            "position": gsc[0].position if gsc else 10.0,
        }
        items.append({
            "experiment_id": f"demo_exp_{url.split('/')[-1][:8]}",
            "target_url": url,
            "change_type": change_type,
            "change_description": desc,
            "baseline_metrics": baseline,
            "baseline_start_date": past_28,
            "baseline_end_date": today,
            "experiment_start_date": today,
            "status": "baseline_set",
        })
    return items
