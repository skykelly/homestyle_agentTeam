"""
Export SEO agent data to docs/data/*.json for GitHub Pages dashboard.
Run by GitHub Actions after the pipeline executes.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def dump(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✓ {name}")


def main():
    print("Exporting dashboard data → docs/data/")

    # ── 1. Run rule engine for issues ────────────────────────────────────
    from rules.seo_rules import run_all_seo_rules
    hits = run_all_seo_rules()

    priority_breakdown = {}
    for h in hits:
        p = h.priority.lower()
        priority_breakdown[p] = priority_breakdown.get(p, 0) + 1

    issues_data = [
        {
            "rule_id": h.rule_id,
            "opportunity_type": h.opportunity_type,
            "priority": h.priority,
            "target_url": h.target_url,
            "target_queries": h.target_queries,
            "recommendation": h.recommendation,
            "impact_score": h.impact_score,
        }
        for h in hits
    ]
    dump("seo_issues.json", issues_data)

    # ── 2. Organic search summary ────────────────────────────────────────
    from data.seo_mock_data import get_gsc_queries, get_ga4_landing, SITE_BENCHMARKS

    gsc = get_gsc_queries()
    ga4 = get_ga4_landing()

    total_clicks = sum(r.clicks for r in gsc)
    total_impressions = sum(r.impressions for r in gsc)
    avg_ctr = total_clicks / total_impressions if total_impressions else 0
    avg_pos = sum(r.position for r in gsc) / len(gsc) if gsc else 0
    revenue = sum(r.revenue_krw for r in ga4)

    prev_clicks = SITE_BENCHMARKS.get("prev_clicks_28d", 22100)
    prev_revenue = SITE_BENCHMARKS.get("prev_revenue_krw", 265_000_000)
    prev_pos = SITE_BENCHMARKS.get("prev_avg_position", 7.1)
    prev_ctr = SITE_BENCHMARKS.get("prev_avg_ctr", 0.057)

    # Top opportunities for bar chart
    top_opps = sorted(hits, key=lambda h: h.impact_score, reverse=True)[:5]

    # Schema by type breakdown
    from storage.seo_repository import list_schema_recommendations
    schema_recs = list_schema_recommendations()
    schema_by_type: dict = {}
    for r in schema_recs:
        t = r.get("schema_type", "Other")
        schema_by_type[t] = schema_by_type.get(t, 0) + 1

    from storage.seo_repository import get_seo_store_summary, list_experiments
    store = get_seo_store_summary()
    active_exps = len([e for e in list_experiments() if e.get("status") == "baseline_set"])

    summary = {
        "generated_at": datetime.now().isoformat(),
        "site_url": SITE_BENCHMARKS.get("site_url", "https://beautylab.co.kr"),
        "total_clicks": total_clicks,
        "total_impressions": total_impressions,
        "avg_ctr": round(avg_ctr, 4),
        "avg_position": round(avg_pos, 2),
        "revenue_krw": revenue,
        "clicks_delta_pct": round((total_clicks - prev_clicks) / prev_clicks * 100, 1) if prev_clicks else 0,
        "revenue_delta_pct": round((revenue - prev_revenue) / prev_revenue * 100, 1) if prev_revenue else 0,
        "ctr_delta_pct": round((avg_ctr - prev_ctr) / prev_ctr * 100, 1) if prev_ctr else 0,
        "position_delta": round(avg_pos - prev_pos, 2),
        "total_issues": len(hits),
        "priority_breakdown": priority_breakdown,
        "content_briefs": store.get("content_briefs", 0),
        "schema_recommendations": store.get("schema_recommendations", 0),
        "internal_link_recommendations": store.get("internal_link_recommendations", 0),
        "experiments_active": active_exps,
        "knowledge_items": store.get("knowledge_items", 0),
        "schema_by_type": schema_by_type,
        "top_opportunities": [
            {"target_url": h.target_url, "opportunity_type": h.opportunity_type, "impact_score": h.impact_score}
            for h in top_opps
        ],
    }
    dump("seo_summary.json", summary)

    # ── 3. Content briefs ─────────────────────────────────────────────────
    from storage.seo_repository import list_content_briefs
    dump("seo_briefs.json", list_content_briefs())

    # ── 4. Schema recommendations ─────────────────────────────────────────
    dump("seo_schema.json", schema_recs)

    # ── 5. Internal link recommendations ─────────────────────────────────
    from storage.seo_repository import list_link_recommendations
    dump("seo_links.json", list_link_recommendations())

    # ── 6. Experiments ────────────────────────────────────────────────────
    dump("seo_experiments.json", list_experiments())

    # ── 7. Knowledge items ────────────────────────────────────────────────
    from storage.seo_repository import list_knowledge_items
    dump("seo_knowledge.json", list_knowledge_items())

    print(f"\nDone — {len(list(OUT.glob('*.json')))} files written to docs/data/")


if __name__ == "__main__":
    main()
