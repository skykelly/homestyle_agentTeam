"""
JSON file-based persistence for recommendations and agent runs (Phase 1).
Thin wrapper — swap for SQLite or DynamoDB later without touching callers.
"""

import json
import threading
from pathlib import Path
from typing import Optional

from models.recommendation import Recommendation
from models.agent_run import AgentRun


DATA_DIR = Path("data/store")
DATA_DIR.mkdir(parents=True, exist_ok=True)

RECOMMENDATIONS_FILE = DATA_DIR / "recommendations.json"
AGENT_RUNS_FILE = DATA_DIR / "agent_runs.json"

_LOCK = threading.Lock()


def _load(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(path: Path, data: list) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Recommendation repository
# ---------------------------------------------------------------------------

def save_recommendation(rec: Recommendation) -> None:
    with _LOCK:
        recs = _load(RECOMMENDATIONS_FILE)
        for i, r in enumerate(recs):
            if r["id"] == rec.id:
                recs[i] = rec.to_dict()
                _save(RECOMMENDATIONS_FILE, recs)
                return
        recs.append(rec.to_dict())
        _save(RECOMMENDATIONS_FILE, recs)


def update_recommendation_dict(data: dict) -> None:
    """Update a recommendation stored as a raw dict (used by approval state machine)."""
    with _LOCK:
        recs = _load(RECOMMENDATIONS_FILE)
        for i, r in enumerate(recs):
            if r["id"] == data["id"]:
                recs[i] = data
                _save(RECOMMENDATIONS_FILE, recs)
                return
        recs.append(data)
        _save(RECOMMENDATIONS_FILE, recs)


def get_recommendation(rec_id: str) -> Optional[dict]:
    for r in _load(RECOMMENDATIONS_FILE):
        if r["id"] == rec_id:
            return r
    return None


def list_recommendations(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
) -> list:
    recs = _load(RECOMMENDATIONS_FILE)
    if status:
        recs = [r for r in recs if r["status"] == status]
    if platform:
        recs = [r for r in recs if r["target_platform"] == platform]
    return recs[-limit:]


# ---------------------------------------------------------------------------
# Agent Run repository
# ---------------------------------------------------------------------------

def save_agent_run(run: AgentRun) -> None:
    from config.feature_flags import is_enabled
    if is_enabled("USE_SQLITE"):
        from storage.db import upsert_agent_run
        upsert_agent_run(run.to_dict())
        return
    with _LOCK:
        runs = _load(AGENT_RUNS_FILE)
        for i, r in enumerate(runs):
            if r["run_id"] == run.run_id:
                runs[i] = run.to_dict()
                _save(AGENT_RUNS_FILE, runs)
                return
        runs.append(run.to_dict())
        _save(AGENT_RUNS_FILE, runs)


def get_agent_run(run_id: str) -> Optional[dict]:
    from config.feature_flags import is_enabled
    if is_enabled("USE_SQLITE"):
        rows = __import__("storage.db", fromlist=["get_agent_runs"]).get_agent_runs()
        return next((r for r in rows if r["run_id"] == run_id), None)
    for r in _load(AGENT_RUNS_FILE):
        if r["run_id"] == run_id:
            return r
    return None


def list_agent_runs(workflow_name: Optional[str] = None, limit: int = 20) -> list:
    from config.feature_flags import is_enabled
    if is_enabled("USE_SQLITE"):
        from storage.db import get_agent_runs
        return get_agent_runs(workflow_name=workflow_name, limit=limit)
    runs = _load(AGENT_RUNS_FILE)
    if workflow_name:
        runs = [r for r in runs if r["workflow_name"] == workflow_name]
    return runs[-limit:]
