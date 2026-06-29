"""
Phase 4-6 SEO Demo — BeautyLab Korea
Demonstrates: Content Briefs, Structured Data, Internal Links,
              Experiments, Reporting, and Parallel Pipeline
"""

import argparse
import json
import sys
import time

# ── ANSI colors ───────────────────────────────────────────────────────────────
BOLD  = "\033[1m"
CYAN  = "\033[96m"
GREEN = "\033[92m"
YELL  = "\033[93m"
RED   = "\033[91m"
DIM   = "\033[2m"
RESET = "\033[0m"

def h1(text): print(f"\n{BOLD}{CYAN}{'═'*60}{RESET}\n{BOLD}{CYAN}  {text}{RESET}\n{BOLD}{CYAN}{'═'*60}{RESET}")
def h2(text): print(f"\n{BOLD}{YELL}── {text} {'─'*(54-len(text))}{RESET}")
def ok(text):  print(f"  {GREEN}✓{RESET} {text}")
def info(text): print(f"  {DIM}{text}{RESET}")
def err(text): print(f"  {RED}✗ {text}{RESET}")


def demo_content_briefs(llm: bool):
    h2("Phase 4 — Content Briefs")
    from workflows.seo_content_brief import SEOContentBriefWorkflow
    wf = SEOContentBriefWorkflow(verbose=False)
    result = wf.generate_briefs(
        max_briefs=3,
        opportunity_types=["ctr_improvement", "ranking_boost"],
        llm_augment=llm,
    )
    ok(f"Generated {result['briefs_generated']} content briefs")
    for b in result.get("briefs", [])[:3]:
        info(f"  [{b.get('search_intent','?')}] {b.get('target_url','?')}")
        info(f"    Primary cluster : {b.get('primary_query_cluster','?')}")
        info(f"    Sections        : {len(b.get('recommended_sections', []))}")
        info(f"    FAQ items       : {len(b.get('faq_items', []))}")
    if result.get("llm_enriched"):
        ok(f"LLM enriched {result['llm_enriched']} briefs")
    return result


def demo_structured_data(llm: bool):
    h2("Phase 5a — Structured Data Audit")
    from workflows.seo_structured_data import SEOStructuredDataWorkflow
    wf = SEOStructuredDataWorkflow(verbose=False)
    result = wf.audit_and_recommend(llm_augment=llm)
    ok(f"Recommendations generated : {result['recommendations_generated']}")
    rich_count = sum(1 for r in result.get("recommendations", []) if r.get("rich_result_eligible"))
    ok(f"Rich-result eligible      : {rich_count}")
    for r in result.get("recommendations", [])[:3]:
        info(f"  [{r.get('schema_type','?')}] {r.get('target_url','?')}")
        info(f"    Impact={r.get('impact_score',0)} Effort={r.get('effort_score',0)}")
    return result


def demo_internal_links(llm: bool):
    h2("Phase 5b — Internal Link Analysis")
    from workflows.seo_internal_link import SEOInternalLinkWorkflow
    wf = SEOInternalLinkWorkflow(verbose=False)
    result = wf.analyze_and_recommend(llm_augment=llm)
    ok(f"Total recommendations : {result['total_recommendations']}")
    for link_type, items in result.get("by_type", {}).items():
        count = len(items) if isinstance(items, list) else items
        info(f"  {link_type:<20} {count}")
    for r in result.get("recommendations", [])[:3]:
        info(f"  [{r.get('link_type','?')}] {r.get('source_url','?')} → {r.get('target_url','?')}")
        info(f"    anchor: \"{r.get('anchor_text','?')}\"")
    return result


def demo_experiments():
    h2("Phase 6a — Experiment Baselines")
    from workflows.seo_experiment import SEOExperimentWorkflow
    wf = SEOExperimentWorkflow(verbose=False)
    result = wf.create_experiment_baselines(top_n=3)
    ok(f"Baselines created : {result['baselines_created']}")
    for exp in result.get("experiments", [])[:3]:
        bm = exp.get("baseline_metrics", {})
        info(f"  [{exp.get('change_type','?')}] {exp.get('target_url','?')}")
        info(f"    clicks={bm.get('clicks_28d',0)}  pos={bm.get('position',0)}")
    return result


def demo_experiment_results(llm: bool):
    h2("Phase 6b — Experiment Results + Knowledge Items")
    from workflows.seo_experiment import SEOExperimentWorkflow
    wf = SEOExperimentWorkflow(verbose=False)
    result = wf.simulate_results_and_learn(llm_augment=llm)
    ok(f"Experiments completed    : {result['experiments_completed']}")
    ok(f"Knowledge items created  : {result['knowledge_items_created']}")
    for r in result.get("results", [])[:3]:
        delta = r.get("delta", {})
        info(f"  {r.get('outcome','?'):10} {r.get('target_url','?')}")
    if result.get("llm_learning"):
        info(f"\n  LLM Strategic Insights (preview):")
        info(f"  {result['llm_learning'][:300].strip()}...")
    return result


def demo_reporting(llm: bool):
    h2("Phase 6c — Weekly SEO Report")
    from workflows.seo_reporting import SEOReportingWorkflow
    wf = SEOReportingWorkflow(verbose=False)
    result = wf.generate_weekly_report(llm_augment=llm, export_markdown=True)
    ok(f"Report generated : {result.get('report_file','?')}")
    stats = result.get("stats", {})
    info(f"  Issues found        : {stats.get('total_issues',0)}")
    info(f"  Content briefs      : {stats.get('content_briefs',0)}")
    info(f"  Schema recs         : {stats.get('schema_recommendations',0)}")
    info(f"  Internal link recs  : {stats.get('internal_link_recommendations',0)}")
    info(f"  Experiments tracked : {stats.get('experiments',0)}")
    info(f"  Knowledge items     : {stats.get('knowledge_items',0)}")
    return result


def demo_parallel_pipeline(llm: bool, site_url: str):
    h2("Full Parallel Pipeline (Stage 1 → 2 → 3)")
    from workflows.seo_parallel_runner import SEOParallelRunner
    runner = SEOParallelRunner(max_workers=4, llm_augment=llm, verbose=True)

    t0 = time.time()
    result = runner.run_full_seo_pipeline(
        site_url=site_url,
        skip_llm_in_parallel=True,
    )
    elapsed = time.time() - t0

    s = result.get("summary", {})
    ok(f"Pipeline complete in {elapsed:.1f}s")
    ok(f"Total SEO issues          : {s.get('total_seo_issues',0)}")
    ok(f"Schema recommendations    : {s.get('schema_recommendations',0)}")
    ok(f"Internal link recs        : {s.get('internal_link_recommendations',0)}")
    ok(f"Experiment baselines      : {s.get('experiment_baselines',0)}")
    ok(f"Content briefs generated  : {s.get('content_briefs_generated',0)}")
    if s.get("report_file"):
        ok(f"Report saved to           : data/reports/{s['report_file']}")
    return result


def demo_quick_diagnosis(site_url: str):
    h2("Quick Diagnosis (parallel Stage 1 only)")
    from workflows.seo_parallel_runner import SEOParallelRunner
    runner = SEOParallelRunner(max_workers=3, llm_augment=False, verbose=True)
    result = runner.run_quick_diagnosis(site_url=site_url)
    qs = result.get("summary", {})
    ok(f"Quick diagnosis done in {result['elapsed_seconds']}s")
    info(f"  SEO issues   : {qs.get('total_seo_issues',0)}")
    info(f"  Schema recs  : {qs.get('schema_recommendations',0)}")
    info(f"  Link recs    : {qs.get('internal_link_recommendations',0)}")
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SEO Phase 4-6 Demo")
    parser.add_argument("--llm", action="store_true", help="Enable LLM augmentation")
    parser.add_argument("--pipeline", action="store_true", help="Run full parallel pipeline")
    parser.add_argument("--quick", action="store_true", help="Run quick diagnosis only")
    parser.add_argument("--site", default="https://beautylab.co.kr", help="Target site URL")
    args = parser.parse_args()

    h1("BeautyLab SEO Phase 4-6 Demo")
    print(f"  LLM augmentation : {'ON' if args.llm else 'OFF (use --llm to enable)'}")
    print(f"  Target site      : {args.site}")

    if args.quick:
        demo_quick_diagnosis(args.site)
        return

    if args.pipeline:
        demo_parallel_pipeline(args.llm, args.site)
        return

    # Individual workflow demos
    try:
        demo_content_briefs(args.llm)
    except Exception as e:
        err(f"Content briefs failed: {e}")

    try:
        demo_structured_data(args.llm)
    except Exception as e:
        err(f"Structured data failed: {e}")

    try:
        demo_internal_links(args.llm)
    except Exception as e:
        err(f"Internal links failed: {e}")

    try:
        demo_experiments()
    except Exception as e:
        err(f"Experiment baselines failed: {e}")

    try:
        demo_experiment_results(args.llm)
    except Exception as e:
        err(f"Experiment results failed: {e}")

    try:
        demo_reporting(args.llm)
    except Exception as e:
        err(f"Reporting failed: {e}")

    h1("Demo Complete")
    print(f"  Run with --pipeline for full parallel execution")
    print(f"  Run with --llm       for LLM-augmented insights")
    print(f"  Run with --quick     for fast Stage-1 diagnosis only")
    print()


if __name__ == "__main__":
    main()
