from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Allocation:
    doable_id: str
    user_id: str
    allocated_at: datetime = field(default_factory=datetime.now)
    is_case_allocation: bool = False

    def __post_init__(self):
        if not self.doable_id:
            raise ValueError("Doable ID must be provided.")
        if not self.user_id:
            raise ValueError("User ID must be provided.")
        if not isinstance(self.is_case_allocation, bool):
            raise ValueError("is_case_allocation must be a boolean value.")
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            doable_id=data["doable_id"],
            user_id=data["user_id"],
            allocated_at=datetime.fromisoformat(data["allocated_at"]),
            is_case_allocation=data.get("is_case_allocation", False),
        )

    def to_dict(self) -> dict:
        return {
            "doable_id": self.doable_id,
            "user_id": self.user_id,
            "allocated_at": self.allocated_at.isoformat(),
            "is_case_allocation": self.is_case_allocation,
        }