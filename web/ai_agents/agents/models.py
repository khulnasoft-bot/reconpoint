"""Data models for crew orchestration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional


class CrewState(Enum):
    """State of the crew orchestrator."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class AgentStatus(Enum):
    """Status of a worker agent."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    WARNING = "warning"  # Completed but hit max iterations
    ERROR = "error"
    FAILED = "failed"  # Task determined infeasible
    CANCELLED = "cancelled"


@dataclass
class AgentWorker:
    """A worker agent managed by the crew."""

    id: str
    task: str
    status: AgentStatus = AgentStatus.PENDING
    priority: int = 1
    depends_on: List[str] = field(default_factory=list)
    result: Optional[str] = None
    error: Optional[str] = None
    tools_used: List[str] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "task": self.task,
            "status": self.status.value,
            "priority": self.priority,
            "depends_on": self.depends_on,
            "result": self.result,
            "error": self.error,
            "tools_used": self.tools_used,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentWorker":
        """Create from dictionary."""
        worker = cls(
            id=data["id"],
            task=data["task"],
            priority=data.get("priority", 1),
            depends_on=data.get("depends_on", []),
        )
        worker.status = AgentStatus(data.get("status", "pending"))
        worker.result = data.get("result")
        worker.error = data.get("error")
        worker.tools_used = data.get("tools_used", [])
        worker.started_at = data.get("started_at")
        worker.completed_at = data.get("completed_at")
        return worker


@dataclass
class Finding:
    """A security finding from an agent."""

    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    description: str
    agent_id: str
    evidence: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "agent_id": self.agent_id,
            "evidence": self.evidence,
        }


# Type alias for worker event callback
WorkerCallback = Callable[[str, str, Dict[str, Any]], None]
