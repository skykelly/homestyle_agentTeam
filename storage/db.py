"""
SQLite persistence layer — Design Spec §7.

Activate with: USE_SQLITE=true (env var).
DB file: data/store/seo.db

Tables:
  daily_metrics       — ad platform + organic daily KPIs
  recommendations     — all recommendation types (SEO + perf marketing)
  agent_runs          — execution history per workflow
  knowledge_items     — agent memory / learning store
  content_briefs      — SEO content briefs
  content_drafts      — editor output drafts
  seo_experiments     — A/B experiment baselines + results
  structured_data     — Schema.org markup recommendations
  internal_links      — internal link recommendations
"""

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path("data/store/seo.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_LOCK = threading.Lock()

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS daily_metrics (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,
    platform    TEXT    NOT NULL,
    campaign_id TEXT,
    campaign_name TEXT,
    impressions INTEGER DEFAULT 0,
    clicks      INTEGER DEFAULT 0,
    spend_krw   REAL    DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue_krw REAL    DEFAULT 0,
    ctr         REAL    DEFAULT 0,
    cpc_krw     REAL    DEFAULT 0,
    roas        REAL    DEFAULT 0,
    extra       TEXT,
    created_at  TEXT    DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_dm_date     ON daily_metrics(date);
CREATE INDEX IF NOT EXISTS idx_dm_platform ON daily_metrics(platform);

CREATE TABLE IF NOT EXISTS recommendations (
    id              TEXT PRIMARY KEY,
    workflow_name   TEXT,
    target_url      TEXT,
    opportunity_type TEXT,
    priority        TEXT DEFAULT 'medium',
    status          TEXT DEFAULT 'pending_approval',
    risk_level      TEXT DEFAULT 'medium',
    effort_score    INTEGER DEFAULT 3,
    impact_score    INTEGER DEFAULT 3,
    problem         TEXT,
    recommendation  TEXT,
    expected_impact TEXT,
    confidence_score REAL DEFAULT 0.5,
    owner           TEXT,
    rollback_plan   TEXT,
    rule_id         TEXT,
    evidence        TEXT,
    current_metrics TEXT,
    approver_notes  TEXT,
    rejection_reason TEXT,
    experiment_id   TEXT,
    approved_at     TEXT,
    rejected_at     TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_rec_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_rec_url    ON recommendations(target_url);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id              TEXT PRIMARY KEY,
    workflow_name       TEXT NOT NULL,
    trigger             TEXT DEFAULT 'manual',
    status              TEXT DEFAULT 'running',
    input_params        TEXT,
    tool_calls          TEXT,
    recommendations_generated TEXT,
    error_message       TEXT,
    output_summary      TEXT,
    started_at          TEXT,
    completed_at        TEXT,
    duration_seconds    REAL
);
CREATE INDEX IF NOT EXISTS idx_run_workflow ON agent_runs(workflow_name);
CREATE INDEX IF NOT EXISTS idx_run_status   ON agent_runs(status);

CREATE TABLE IF NOT EXISTS knowledge_items (
    item_id         TEXT PRIMARY KEY,
    source_type     TEXT,
    source_id       TEXT,
    title           TEXT,
    summary         TEXT,
    content         TEXT,
    tags            TEXT,
    relevance_score REAL DEFAULT 1.0,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT
);

CREATE TABLE IF NOT EXISTS content_briefs (
    brief_id        TEXT PRIMARY KEY,
    target_url      TEXT,
    primary_query_cluster TEXT,
    search_intent   TEXT,
    secondary_queries TEXT,
    recommended_sections TEXT,
    faq_items       TEXT,
    current_gap     TEXT,
    status          TEXT DEFAULT 'draft',
    priority        TEXT DEFAULT 'medium',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS content_drafts (
    draft_id        TEXT PRIMARY KEY,
    brief_id        TEXT,
    target_url      TEXT,
    version         INTEGER DEFAULT 1,
    title_before    TEXT,
    title_after     TEXT,
    meta_before     TEXT,
    meta_after      TEXT,
    h1_before       TEXT,
    h1_after        TEXT,
    section_rewrites TEXT,
    faq_additions   TEXT,
    quality_score   REAL DEFAULT 0,
    brand_safety_score REAL DEFAULT 0,
    governance_flags TEXT,
    diff_summary    TEXT,
    status          TEXT DEFAULT 'draft',
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS seo_experiments (
    experiment_id   TEXT PRIMARY KEY,
    target_url      TEXT,
    change_type     TEXT,
    change_description TEXT,
    baseline_metrics TEXT,
    post_metrics    TEXT,
    baseline_start_date TEXT,
    baseline_end_date TEXT,
    experiment_start_date TEXT,
    experiment_end_date TEXT,
    status          TEXT DEFAULT 'running',
    result_summary  TEXT,
    recommendation_id TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS structured_data (
    rec_id          TEXT PRIMARY KEY,
    target_url      TEXT,
    page_type       TEXT,
    schema_type     TEXT,
    priority        TEXT,
    current_status  TEXT,
    recommendation  TEXT,
    implementation_snippet TEXT,
    rich_result_eligible INTEGER DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS internal_links (
    rec_id          TEXT PRIMARY KEY,
    source_url      TEXT,
    target_url      TEXT,
    anchor_text     TEXT,
    context_snippet TEXT,
    priority        TEXT,
    opportunity_type TEXT,
    estimated_impact TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _LOCK:
        conn = get_conn()
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    # Deserialise JSON columns
    json_cols = {
        "evidence", "current_metrics", "input_params", "tool_calls",
        "recommendations_generated", "tags", "secondary_queries",
        "recommended_sections", "faq_items", "current_gap",
        "section_rewrites", "faq_additions", "governance_flags",
        "baseline_metrics", "post_metrics",
    }
    for col in json_cols:
        if col in d and isinstance(d[col], str):
            try:
                d[col] = json.loads(d[col])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def _json(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val, ensure_ascii=False)
    return str(val)


# ── Generic upsert / query helpers ──────────────────────────────────────────

def upsert(table: str, pk_col: str, pk_val: str, data: dict) -> None:
    """Insert or replace a row by primary key."""
    cols = list(data.keys())
    placeholders = ", ".join("?" * len(cols))
    col_list = ", ".join(cols)
    values = [data[c] for c in cols]
    with _LOCK:
        conn = get_conn()
        conn.execute(
            f"INSERT OR REPLACE INTO {table} ({col_list}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
        conn.close()


def query(
    table: str,
    where: Optional[str] = None,
    params: tuple = (),
    order_by: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    sql = f"SELECT * FROM {table}"
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    if limit:
        sql += f" LIMIT {limit}"
    conn = get_conn()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def update_fields(table: str, pk_col: str, pk_val: str, fields: dict) -> Optional[dict]:
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [pk_val]
    with _LOCK:
        conn = get_conn()
        conn.execute(f"UPDATE {table} SET {set_clause} WHERE {pk_col} = ?", values)
        conn.commit()
        rows = conn.execute(f"SELECT * FROM {table} WHERE {pk_col} = ?", (pk_val,)).fetchall()
        conn.close()
    return _row_to_dict(rows[0]) if rows else None


# ── daily_metrics ────────────────────────────────────────────────────────────

def insert_daily_metrics(rows: list[dict]) -> int:
    """Bulk-insert daily metric rows. Returns inserted count."""
    if not rows:
        return 0
    cols = [
        "date", "platform", "campaign_id", "campaign_name",
        "impressions", "clicks", "spend_krw", "conversions",
        "revenue_krw", "ctr", "cpc_krw", "roas", "extra",
    ]
    with _LOCK:
        conn = get_conn()
        inserted = 0
        for row in rows:
            vals = [row.get(c) for c in cols]
            if row.get("clicks") and row.get("spend_krw"):
                row.setdefault("cpc_krw", row["spend_krw"] / max(row["clicks"], 1))
            if row.get("spend_krw") and row.get("revenue_krw"):
                row.setdefault("roas", row["revenue_krw"] / max(row["spend_krw"], 1) * 100)
            vals = [row.get(c) for c in cols]
            placeholders = ", ".join("?" * len(cols))
            conn.execute(
                f"INSERT OR IGNORE INTO daily_metrics ({', '.join(cols)}) VALUES ({placeholders})",
                vals,
            )
            inserted += conn.execute("SELECT changes()").fetchone()[0]
        conn.commit()
        conn.close()
    return inserted


def get_daily_metrics(
    platform: Optional[str] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> list[dict]:
    conditions = []
    params = []
    if platform:
        conditions.append("platform = ?")
        params.append(platform)
    if since:
        conditions.append("date >= ?")
        params.append(since)
    if until:
        conditions.append("date <= ?")
        params.append(until)
    where = " AND ".join(conditions) if conditions else None
    return query("daily_metrics", where=where, params=tuple(params), order_by="date DESC")


# ── agent_runs ───────────────────────────────────────────────────────────────

def upsert_agent_run(run: dict) -> None:
    row = {
        "run_id": run["run_id"],
        "workflow_name": run["workflow_name"],
        "trigger": run.get("trigger", "manual"),
        "status": run.get("status", "running"),
        "input_params": _json(run.get("input_params")),
        "tool_calls": _json(run.get("tool_calls")),
        "recommendations_generated": _json(run.get("recommendations_generated")),
        "error_message": run.get("error_message"),
        "output_summary": run.get("output_summary"),
        "started_at": run.get("started_at"),
        "completed_at": run.get("completed_at"),
        "duration_seconds": run.get("duration_seconds"),
    }
    upsert("agent_runs", "run_id", run["run_id"], row)


def get_agent_runs(workflow_name: Optional[str] = None, limit: int = 50) -> list[dict]:
    where = "workflow_name = ?" if workflow_name else None
    params = (workflow_name,) if workflow_name else ()
    return query("agent_runs", where=where, params=params, order_by="started_at DESC", limit=limit)


# ── knowledge_items ──────────────────────────────────────────────────────────

def upsert_knowledge_item(item: dict) -> None:
    row = {
        "item_id": item["item_id"],
        "source_type": item.get("source_type"),
        "source_id": item.get("source_id"),
        "title": item.get("title"),
        "summary": item.get("summary"),
        "content": item.get("content"),
        "tags": _json(item.get("tags")),
        "relevance_score": item.get("relevance_score", 1.0),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }
    upsert("knowledge_items", "item_id", item["item_id"], row)


def get_knowledge_items(source_type: Optional[str] = None, tag: Optional[str] = None) -> list[dict]:
    rows = query("knowledge_items", order_by="created_at DESC")
    if source_type:
        rows = [r for r in rows if r.get("source_type") == source_type]
    if tag:
        rows = [r for r in rows if tag in (r.get("tags") or [])]
    return rows


# Initialise schema on import
init_db()
