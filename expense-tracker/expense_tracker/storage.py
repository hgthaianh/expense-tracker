"""JSON file storage handler for expenses."""

import json
from pathlib import Path
from typing import List
import threading

from .models import Expense


class JSONStorage:
    """Handle read/write operations to JSON storage file."""
    
    _lock = threading.Lock()
    
    def __init__(self, filepath: str = "expenses.json"):
        """Initialize storage with file path.
        
        Args:
            filepath: Path to the JSON storage file.
        """
        self.filepath = Path(filepath)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create the storage file if it doesn't exist."""
        if not self.filepath.exists():
            self._write_data([])
    
    def _read_data(self) -> List[dict]:
        """Read raw data from JSON file.
        
        Returns:
            List of expense dictionaries.
        """
        with self._lock:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except (json.JSONDecodeError, FileNotFoundError):
                return []
    
    def _write_data(self, data: List[dict]) -> None:
        """Write data to JSON file.
        
        Args:
            data: List of expense dictionaries to write.
        """
        with self._lock:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_expenses(self) -> List[Expense]:
        """Load all expenses from storage.
        
        Returns:
            List of Expense objects.
        """
        data = self._read_data()
        expenses = []
        for item in data:
            try:
                expenses.append(Expense.from_dict(item))
            except (ValueError, KeyError) as e:
                # Skip invalid entries but log them
                print(f"Warning: Skipping invalid expense entry: {e}")
        return expenses
    
    def save_expenses(self, expenses: List[Expense]) -> None:
        """Save all expenses to storage.
        
        Args:
            expenses: List of Expense objects to save.
        """
        data = [expense.to_dict() for expense in expenses]
        self._write_data(data)
    
    def add_expense(self, expense: Expense) -> None:
        """Add a single expense to storage.
        
        Args:
            expense: Expense object to add.
        """
        expenses = self.load_expenses()
        expenses.append(expense)
        self.save_expenses(expenses)
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID.
        
        Args:
            expense_id: ID of the expense to delete.
            
        Returns:
            True if expense was deleted, False if not found.
        """
        expenses = self.load_expenses()
        original_count = len(expenses)
        expenses = [e for e in expenses if e.id != expense_id]
        
        if len(expenses) < original_count:
            self.save_expenses(expenses)
            return True
        return False
    
    def get_expense_by_id(self, expense_id: str) -> Expense | None:
        """Get an expense by its ID.
        
        Args:
            expense_id: ID of the expense to find.
            
        Returns:
            Expense object if found, None otherwise.
        """
        expenses = self.load_expenses()
        for expense in expenses:
            if expense.id == expense_id:
                return expense
        return None
