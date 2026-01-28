"""Expense data model."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Expense:
    """Represents a single expense entry."""
    
    amount: float
    category: str
    description: str
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        # Ensure amount is positive
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Normalize category to lowercase
        self.category = self.category.lower().strip()
        
        # Ensure description is not empty
        if not self.description.strip():
            raise ValueError("Description cannot be empty")
        self.description = self.description.strip()
    
    def to_dict(self) -> dict:
        """Convert expense to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Create an Expense instance from a dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            amount=float(data["amount"]),
            category=data["category"],
            description=data["description"],
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            created_at=data.get("created_at", datetime.now().isoformat()),
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"[{self.id}] {self.date} | {self.category:12} | ${self.amount:>10.2f} | {self.description}"
