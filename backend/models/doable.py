from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Doable:
    id: str
    title: str
    case_id: Optional[str] = None
    type: str = "task"
    priority: str = "medium"
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

    valid_priorities = {"low", "medium", "high"}
    valid_statuses = {"pending", "allocated", "completed"}

    def __post_init__(self):
        """
        Perform validation and processing.
        """
        if self.type not in ["task", "email"]:
            raise ValueError("Invalid type. Must be 'task' or 'email'.")
        if self.priority not in self.valid_priorities:
            raise ValueError(f"Invalid priority '{self.priority}'. Must be one of {self.valid_priorities}.")
        if self.status not in self.valid_statuses:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of {self.valid_statuses}.")
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Doable instance from a dictionary.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            case_id=data.get("case_id"),
            type=data.get("type", "task"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "pending"),
            created_at=data["created_at"],
        )

    def to_dict(self) -> dict:
        """
        Convert the Doable instance to a dictionary.
        """
        return {
            "id": self.id,
            "title": self.title,
            "case_id": self.case_id,
            "type": self.type,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
