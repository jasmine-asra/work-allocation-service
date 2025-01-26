from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass
class User:
    user_name: str
    first_name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    last_name: Optional[str] = None
    preferred_doable_type: Optional[str] = None

    def __post_init__(self):
        """
        Perform validation and processing.
        """
        if self.preferred_doable_type and self.preferred_doable_type not in ["task", "email"]:
            raise ValueError("Invalid preferred doable type. Must be 'task', 'email' or None.")
        
    @classmethod
    def from_dict(cls, user_dict: dict):
        """
        Create a User instance from a dictionary.
        """
        return cls(
            user_name=user_dict["user_name"],
            first_name=user_dict["first_name"],
            last_name=user_dict.get("last_name"),
            preferred_doable_type=user_dict.get("preferred_doable_type"),
            id=user_dict.get("id", str(uuid.uuid4()))
        )

    def to_dict(self) -> dict:
        """
        Convert the User instance to a dictionary.
        """
        return {
            "id": self.id,
            "user_name": self.user_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "preferred_doable_type": self.preferred_doable_type,
        }