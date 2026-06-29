"""
SEO-specific repository (Phase 4-6).
Stores ContentBrief, StructuredDataRecommendation, InternalLinkRecommendation,
SEOExperiment, KnowledgeItem to JSON files.
"""

import json
import os
import threading
from pathlib import Path
from typing import Optional

STORE_DIR = Path(__file__).parent.parent / "data" / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)

BRIEFS_FILE = STORE_DIR / "seo_content_briefs.json"
SCHEMA_RECS_FILE = STORE_DIR / "seo_structured_data.json"
LINK_RECS_FILE = STORE_DIR / "seo_internal_links.json"
EXPERIMENTS_FILE = STORE_DIR / "seo_experiments.json"
KNOWLEDGE_FILE = STORE_DIR / "seo_knowledge_items.json"
RECOMMENDATIONS_FILE = STORE_DIR / "seo_recommendations.json"
DRAFTS_FILE = STORE_DIR / "seo_content_drafts.json"

_LOCK = threading.Lock()


def _load(path: Path) -> list:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save(path: Path, data: list) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── ContentBrief ─────────────────────────────────────────────────────────────

def save_content_brief(brief) -> None:
    with _LOCK:
        items = _load(BRIEFS_FILE)
        items = [i for i in items if i.get("brief_id") != brief.brief_id]
        items.append(brief.to_dict())
        _save(BRIEFS_FILE, items)


def list_content_briefs(status: str = "", url: str = "") -> list[dict]:
    items = _load(BRIEFS_FILE)
    if status:
        items = [i for i in items if i.get("status") == status]
    if url:
        items = [i for i in items if i.get("target_url") == url]
    return items


def get_content_brief(brief_id: str) -> Optional[dict]:
    return next((i for i in _load(BRIEFS_FILE) if i.get("brief_id") == brief_id), None)


# ── StructuredDataRecommendation ─────────────────────────────────────────────

def save_schema_recommendation(rec) -> None:
    with _LOCK:
        items = _load(SCHEMA_RECS_FILE)
        items = [i for i in items if i.get("rec_id") != rec.rec_id]
        items.append(rec.to_dict())
        _save(SCHEMA_RECS_FILE, items)


def list_schema_recommendations(page_type: str = "") -> list[dict]:
    items = _load(SCHEMA_RECS_FILE)
    if page_type:
        items = [i for i in items if i.get("page_type") == page_type]
    return items


# ── InternalLinkRecommendation ───────────────────────────────────────────────

def save_link_recommendation(rec) -> None:
    with _LOCK:
        items = _load(LINK_RECS_FILE)
        items = [i for i in items if i.get("rec_id") != rec.rec_id]
        items.append(rec.to_dict())
        _save(LINK_RECS_FILE, items)


def list_link_recommendations(priority: str = "") -> list[dict]:
    items = _load(LINK_RECS_FILE)
    if priority:
        items = [i for i in items if i.get("priority") == priority]
    return items


# ── SEOExperiment ─────────────────────────────────────────────────────────────

def save_experiment(exp) -> None:
    with _LOCK:
        items = _load(EXPERIMENTS_FILE)
        items = [i for i in items if i.get("experiment_id") != exp.experiment_id]
        items.append(exp.to_dict())
        _save(EXPERIMENTS_FILE, items)


def list_experiments(status: str = "") -> list[dict]:
    items = _load(EXPERIMENTS_FILE)
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


def get_experiment(experiment_id: str) -> Optional[dict]:
    return next((i for i in _load(EXPERIMENTS_FILE) if i.get("experiment_id") == experiment_id), None)


# ── KnowledgeItem ─────────────────────────────────────────────────────────────

def save_knowledge_item(item) -> None:
    with _LOCK:
        items = _load(KNOWLEDGE_FILE)
        items = [i for i in items if i.get("item_id") != item.item_id]
        items.append(item.to_dict())
        _save(KNOWLEDGE_FILE, items)


def list_knowledge_items(source_type: str = "", tag: str = "") -> list[dict]:
    items = _load(KNOWLEDGE_FILE)
    if source_type:
        items = [i for i in items if i.get("source_type") == source_type]
    if tag:
        items = [i for i in items if tag in (i.get("tags") or [])]
    return items


# ── Recommendation ───────────────────────────────────────────────────────────

def save_recommendation(rec) -> None:
    with _LOCK:
        items = _load(RECOMMENDATIONS_FILE)
        items = [i for i in items if i.get("rec_id") != rec.rec_id]
        items.append(rec.to_dict())
        _save(RECOMMENDATIONS_FILE, items)


def list_recommendations(status: str = "", priority: str = "") -> list[dict]:
    items = _load(RECOMMENDATIONS_FILE)
    if status:
        items = [i for i in items if i.get("status") == status]
    if priority:
        items = [i for i in items if i.get("priority") == priority]
    return sorted(items, key=lambda x: x.get("impact_score", 0), reverse=True)


def get_recommendation(rec_id: str) -> Optional[dict]:
    return next((i for i in _load(RECOMMENDATIONS_FILE) if i.get("rec_id") == rec_id), None)


def update_recommendation_status(rec_id: str, status: str, **kwargs) -> Optional[dict]:
    """Update status and optional fields (approver_notes, rejection_reason, etc.)."""
    from datetime import datetime
    with _LOCK:
        items = _load(RECOMMENDATIONS_FILE)
        for item in items:
            if item.get("rec_id") == rec_id:
                item["status"] = status
                item["updated_at"] = datetime.now().isoformat()
                for k, v in kwargs.items():
                    item[k] = v
                _save(RECOMMENDATIONS_FILE, items)
                return item
    return None


# ── ContentDraft ──────────────────────────────────────────────────────────────

def save_content_draft(draft) -> None:
    with _LOCK:
        items = _load(DRAFTS_FILE)
        items = [i for i in items if i.get("draft_id") != draft.draft_id]
        items.append(draft.to_dict())
        _save(DRAFTS_FILE, items)


def list_content_drafts(brief_id: str = "", status: str = "") -> list[dict]:
    items = _load(DRAFTS_FILE)
    if brief_id:
        items = [i for i in items if i.get("brief_id") == brief_id]
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


def get_content_draft(draft_id: str) -> Optional[dict]:
    return next((i for i in _load(DRAFTS_FILE) if i.get("draft_id") == draft_id), None)


def get_seo_store_summary() -> dict:
    recs = _load(RECOMMENDATIONS_FILE)
    return {
        "content_briefs": len(_load(BRIEFS_FILE)),
        "schema_recommendations": len(_load(SCHEMA_RECS_FILE)),
        "internal_link_recommendations": len(_load(LINK_RECS_FILE)),
        "experiments": len(_load(EXPERIMENTS_FILE)),
        "knowledge_items": len(_load(KNOWLEDGE_FILE)),
        "recommendations": len(recs),
        "pending_approvals": len([r for r in recs if r.get("status") == "pending_approval"]),
        "content_drafts": len(_load(DRAFTS_FILE)),
    }
