"""
Agent Run logging model (Phase 1).
Records every workflow execution for audit and debugging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class RunStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentRun:
    workflow_name: str
    trigger: str        # "manual", "scheduled", "event"
    input_params: dict

    # Auto-generated
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    status: RunStatus = field(default=RunStatus.RUNNING)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    tool_calls: list = field(default_factory=list)                    # list[dict]
    recommendations_generated: list = field(default_factory=list)    # list[str] rec IDs
    error_message: Optional[str] = None
    output_summary: Optional[str] = None

    def complete(self, output_summary: str = None, error: str = None) -> None:
        self.completed_at = datetime.now().isoformat()
        started = datetime.fromisoformat(self.started_at)
        completed = datetime.fromisoformat(self.completed_at)
        self.duration_seconds = round((completed - started).total_seconds(), 2)
        if error:
            self.status = RunStatus.FAILED
            self.error_message = error
        else:
            self.status = RunStatus.COMPLETED
            self.output_summary = output_summary

    def add_tool_call(self, tool_name: str, input_summary: str, result_preview: str) -> None:
        self.tool_calls.append({
            "tool": tool_name,
            "input": input_summary,
            "result_preview": result_preview,
            "timestamp": datetime.now().isoformat(),
        })

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "workflow_name": self.workflow_name,
            "trigger": self.trigger,
            "input_params": self.input_params,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "tool_calls": self.tool_calls,
            "recommendations_generated": self.recommendations_generated,
            "error_message": self.error_message,
            "output_summary": self.output_summary,
        }
