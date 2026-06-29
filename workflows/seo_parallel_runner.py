"""
SEO Parallel Workflow Runner — Phase 4-6.
Executes multiple SEO sub-workflows concurrently using ThreadPoolExecutor.

Design principle: Independent sub-workflows run in parallel, results merge at the end.
This cuts total execution time from ~sum(T_i) to ~max(T_i).

Workflow DAG:
  ┌─────────────────────────────────────────────────────────┐
  │  PARALLEL STAGE 1 (all independent, run concurrently)  │
  │                                                         │
  │  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
  │  │ SEODiagnosis │  │  Structured │  │  InternalLink│  │
  │  │  (Rule Eng.) │  │    Data     │  │   Analysis   │  │
  │  └──────────────┘  └─────────────┘  └──────────────┘  │
  │                                                         │
  │  ┌────────────────────────────────────────────────────┐ │
  │  │          SEOExperiment (baseline capture)          │ │
  │  └────────────────────────────────────────────────────┘ │
  └─────────────────────────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  STAGE 2 (depends on Stage 1 results)                  │
  │                                                         │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │  SEOContentBrief (uses diagnosis results)        │  │
  │  └──────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────┘
                             │
                             ▼
  ┌─────────────────────────────────────────────────────────┐
  │  STAGE 3 (report aggregates everything)                │
  │                                                         │
  │  ┌──────────────────────────────────────────────────┐  │
  │  │  SEOReporting (weekly Markdown report)           │  │
  │  └──────────────────────────────────────────────────┘  │
  └─────────────────────────────────────────────────────────┘
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from datetime import datetime
from typing import Any, Callable


class SEOParallelRunner:
    """
    Orchestrates parallel execution of SEO sub-workflows.
    Each workflow runs in its own thread with its own Anthropic client instance.
    Results are collected and merged into a unified output.
    """

    def __init__(
        self,
        max_workers: int = 4,
        llm_augment: bool = True,
        verbose: bool = True,
    ):
        self.max_workers = max_workers
        self.llm_augment = llm_augment
        self.verbose = verbose

    def _log(self, msg: str) -> None:
        if self.verbose:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"[{ts}] {msg}")

    def run_full_seo_pipeline(
        self,
        site_url: str = "https://beautylab.co.kr",
        skip_llm_in_parallel: bool = True,
    ) -> dict:
        """
        Run the complete SEO pipeline with parallel Stage 1 workflows.

        Args:
            site_url: Target site URL
            skip_llm_in_parallel: If True, sub-workflows skip LLM calls (faster).
                                   LLM only runs in Stage 3 reporting.
        """
        start_time = time.time()
        self._log(f"🚀 Starting SEO Parallel Pipeline for {site_url}")
        self._log(f"   max_workers={self.max_workers} | llm_augment={self.llm_augment}")

        results: dict[str, Any] = {
            "pipeline_started_at": datetime.now().isoformat(),
            "site_url": site_url,
            "stages": {},
        }

        # ── STAGE 1: Parallel execution ───────────────────────────────────
        self._log("\n📊 Stage 1: Running parallel sub-workflows...")
        stage1_start = time.time()

        stage1_tasks: dict[str, Callable] = {
            "diagnosis": lambda: self._run_diagnosis(site_url, llm_augment=False),
            "structured_data": lambda: self._run_structured_data(llm_augment=False),
            "internal_links": lambda: self._run_internal_links(llm_augment=False),
            "experiments": lambda: self._run_experiments(),
        }

        stage1_results = self._run_parallel(stage1_tasks, stage_name="Stage 1")
        stage1_elapsed = time.time() - stage1_start
        results["stages"]["stage1"] = {
            "elapsed_seconds": round(stage1_elapsed, 2),
            "results": stage1_results,
        }

        self._log(f"✅ Stage 1 complete in {stage1_elapsed:.1f}s")

        # ── STAGE 2: Content briefs (depends on Stage 1 diagnosis) ───────
        self._log("\n📝 Stage 2: Generating content briefs...")
        stage2_start = time.time()

        # Content briefs use diagnosis results to pick top URLs
        diagnosis_result = stage1_results.get("diagnosis", {})
        top_opportunity_types = ["ctr_improvement", "ranking_boost"]

        stage2_tasks: dict[str, Callable] = {
            "content_briefs": lambda: self._run_content_briefs(
                max_briefs=5,
                opportunity_types=top_opportunity_types,
                llm_augment=self.llm_augment and not skip_llm_in_parallel,
            ),
        }

        stage2_results = self._run_parallel(stage2_tasks, stage_name="Stage 2")
        stage2_elapsed = time.time() - stage2_start
        results["stages"]["stage2"] = {
            "elapsed_seconds": round(stage2_elapsed, 2),
            "results": stage2_results,
        }

        self._log(f"✅ Stage 2 complete in {stage2_elapsed:.1f}s")

        # ── STAGE 3: Report (aggregates all) ─────────────────────────────
        self._log("\n📋 Stage 3: Generating weekly SEO report...")
        stage3_start = time.time()
        report_result = self._run_reporting(llm_augment=self.llm_augment)
        stage3_elapsed = time.time() - stage3_start

        results["stages"]["stage3"] = {
            "elapsed_seconds": round(stage3_elapsed, 2),
            "report": report_result,
        }

        self._log(f"✅ Stage 3 complete in {stage3_elapsed:.1f}s")

        # ── Final summary ──────────────────────────────────────────────────
        total_elapsed = time.time() - start_time
        results["pipeline_completed_at"] = datetime.now().isoformat()
        results["total_elapsed_seconds"] = round(total_elapsed, 2)
        results["summary"] = self._build_pipeline_summary(stage1_results, stage2_results, report_result)

        self._log(f"\n🎉 Pipeline complete in {total_elapsed:.1f}s")
        self._print_summary(results["summary"])

        return results

    def run_quick_diagnosis(self, site_url: str = "https://beautylab.co.kr") -> dict:
        """
        Run only Stage 1 diagnosis + structured data + internal links in parallel.
        Faster path for daily check-ins (skips content briefs and reporting).
        """
        start_time = time.time()
        self._log(f"⚡ Quick SEO Diagnosis for {site_url}")

        tasks: dict[str, Callable] = {
            "diagnosis": lambda: self._run_diagnosis(site_url, llm_augment=False),
            "structured_data": lambda: self._run_structured_data(llm_augment=False),
            "internal_links": lambda: self._run_internal_links(llm_augment=False),
        }

        parallel_results = self._run_parallel(tasks, stage_name="Quick Diagnosis")
        elapsed = time.time() - start_time

        self._log(f"✅ Quick diagnosis complete in {elapsed:.1f}s")

        return {
            "mode": "quick_diagnosis",
            "elapsed_seconds": round(elapsed, 2),
            "results": parallel_results,
            "summary": self._build_quick_summary(parallel_results),
        }

    def _run_parallel(
        self,
        tasks: dict[str, Callable],
        stage_name: str = "",
    ) -> dict[str, Any]:
        """Execute tasks concurrently and collect results."""
        results: dict[str, Any] = {}
        errors: dict[str, str] = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name: dict[Future, str] = {}
            for name, task_fn in tasks.items():
                self._log(f"  → Launching: {name}")
                future = executor.submit(task_fn)
                future_to_name[future] = name

            for future in as_completed(future_to_name):
                name = future_to_name[future]
                try:
                    result = future.result()
                    results[name] = result
                    self._log(f"  ← Done: {name}")
                except Exception as e:
                    errors[name] = str(e)
                    results[name] = {"error": str(e)}
                    self._log(f"  ✗ Error: {name} — {e}")

        if errors:
            results["_errors"] = errors

        return results

    # ── Sub-workflow launchers ────────────────────────────────────────────────

    def _run_diagnosis(self, site_url: str, llm_augment: bool = False) -> dict:
        from workflows.seo_diagnosis import SEODiagnosisWorkflow
        wf = SEODiagnosisWorkflow(verbose=False)
        return wf.diagnose(site_url=site_url, llm_augment=llm_augment, max_results=20)

    def _run_structured_data(self, llm_augment: bool = False) -> dict:
        from workflows.seo_structured_data import SEOStructuredDataWorkflow
        wf = SEOStructuredDataWorkflow(verbose=False)
        return wf.audit_and_recommend(llm_augment=llm_augment)

    def _run_internal_links(self, llm_augment: bool = False) -> dict:
        from workflows.seo_internal_link import SEOInternalLinkWorkflow
        wf = SEOInternalLinkWorkflow(verbose=False)
        return wf.analyze_and_recommend(llm_augment=llm_augment)

    def _run_experiments(self) -> dict:
        from workflows.seo_experiment import SEOExperimentWorkflow
        wf = SEOExperimentWorkflow(verbose=False)
        return wf.create_experiment_baselines(top_n=5)

    def _run_content_briefs(
        self,
        max_briefs: int = 5,
        opportunity_types: list[str] | None = None,
        llm_augment: bool = False,
    ) -> dict:
        from workflows.seo_content_brief import SEOContentBriefWorkflow
        wf = SEOContentBriefWorkflow(verbose=False)
        return wf.generate_briefs(
            max_briefs=max_briefs,
            opportunity_types=opportunity_types,
            llm_augment=llm_augment,
        )

    def _run_reporting(self, llm_augment: bool = False) -> dict:
        from workflows.seo_reporting import SEOReportingWorkflow
        wf = SEOReportingWorkflow(verbose=False)
        return wf.generate_weekly_report(llm_augment=llm_augment, export_markdown=True)

    # ── Summary builders ──────────────────────────────────────────────────────

    def _build_pipeline_summary(
        self,
        stage1: dict,
        stage2: dict,
        report: dict,
    ) -> dict:
        diagnosis = stage1.get("diagnosis", {})
        structured = stage1.get("structured_data", {})
        links = stage1.get("internal_links", {})
        experiments = stage1.get("experiments", {})
        briefs = stage2.get("content_briefs", {})

        total_issues = diagnosis.get("summary", {}).get("total_issues", 0)
        schema_count = structured.get("recommendations_generated", 0)
        link_count = links.get("total_recommendations", 0)
        exp_count = experiments.get("baselines_created", 0)
        brief_count = briefs.get("briefs_generated", 0)
        report_file = report.get("report_file", "")

        return {
            "total_seo_issues": total_issues,
            "schema_recommendations": schema_count,
            "internal_link_recommendations": link_count,
            "experiment_baselines": exp_count,
            "content_briefs_generated": brief_count,
            "report_file": report_file,
            "pipeline_health": "healthy" if total_issues > 0 else "no_data",
        }

    def _build_quick_summary(self, results: dict) -> dict:
        diagnosis = results.get("diagnosis", {})
        structured = results.get("structured_data", {})
        links = results.get("internal_links", {})

        return {
            "total_seo_issues": diagnosis.get("summary", {}).get("total_issues", 0),
            "priority_breakdown": diagnosis.get("summary", {}).get("priority_breakdown", {}),
            "schema_recommendations": structured.get("recommendations_generated", 0),
            "internal_link_recommendations": links.get("total_recommendations", 0),
        }

    def _print_summary(self, summary: dict) -> None:
        self._log("\n" + "─" * 50)
        self._log("SEO Pipeline Summary:")
        self._log(f"  Total SEO Issues:          {summary.get('total_seo_issues', 0)}")
        self._log(f"  Schema Recommendations:    {summary.get('schema_recommendations', 0)}")
        self._log(f"  Internal Link Recs:        {summary.get('internal_link_recommendations', 0)}")
        self._log(f"  Experiment Baselines:      {summary.get('experiment_baselines', 0)}")
        self._log(f"  Content Briefs Generated:  {summary.get('content_briefs_generated', 0)}")
        if summary.get("report_file"):
            self._log(f"  Report: data/reports/{summary['report_file']}")
        self._log("─" * 50)
