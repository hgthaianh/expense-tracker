"""Expense manager with pandas for data analysis."""

from datetime import datetime
from typing import List, Optional
import pandas as pd

from .models import Expense
from .storage import JSONStorage


class ExpenseManager:
    """Manage expenses with pandas for data analysis and reporting."""
    
    def __init__(self, storage: Optional[JSONStorage] = None):
        """Initialize manager with storage backend.
        
        Args:
            storage: JSONStorage instance. Creates default if None.
        """
        self.storage = storage or JSONStorage()
    
    def add_expense(
        self,
        amount: float,
        category: str,
        description: str,
        date: Optional[str] = None
    ) -> Expense:
        """Add a new expense.
        
        Args:
            amount: Expense amount (positive number).
            category: Expense category (e.g., food, transport).
            description: Description of the expense.
            date: Optional date string (YYYY-MM-DD). Defaults to today.
            
        Returns:
            The created Expense object.
        """
        expense = Expense(
            amount=amount,
            category=category,
            description=description,
            date=date or datetime.now().strftime("%Y-%m-%d")
        )
        self.storage.add_expense(expense)
        return expense
    
    def list_expenses(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Expense]:
        """List expenses with optional filters.
        
        Args:
            category: Filter by category name.
            start_date: Filter expenses on or after this date (YYYY-MM-DD).
            end_date: Filter expenses on or before this date (YYYY-MM-DD).
            limit: Maximum number of expenses to return.
            
        Returns:
            List of filtered Expense objects.
        """
        expenses = self.storage.load_expenses()
        
        # Apply category filter
        if category:
            category = category.lower().strip()
            expenses = [e for e in expenses if e.category == category]
        
        # Apply date filters
        if start_date:
            expenses = [e for e in expenses if e.date >= start_date]
        if end_date:
            expenses = [e for e in expenses if e.date <= end_date]
        
        # Sort by date (newest first)
        expenses.sort(key=lambda e: e.date, reverse=True)
        
        # Apply limit
        if limit and limit > 0:
            expenses = expenses[:limit]
        
        return expenses
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID.
        
        Args:
            expense_id: ID of the expense to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        return self.storage.delete_expense(expense_id)
    
    def get_summary(self, month: Optional[str] = None) -> pd.DataFrame:
        """Get spending summary by category.
        
        Args:
            month: Optional month filter (YYYY-MM format).
            
        Returns:
            DataFrame with category summaries.
        """
        expenses = self.storage.load_expenses()
        
        if not expenses:
            return pd.DataFrame(columns=["category", "total", "count", "average"])
        
        # Convert to DataFrame
        df = pd.DataFrame([e.to_dict() for e in expenses])
        
        # Filter by month if specified
        if month:
            df = df[df["date"].str.startswith(month)]
        
        if df.empty:
            return pd.DataFrame(columns=["category", "total", "count", "average"])
        
        # Group by category and calculate statistics
        summary = df.groupby("category").agg(
            total=("amount", "sum"),
            count=("amount", "count"),
            average=("amount", "mean")
        ).reset_index()
        
        # Sort by total spending (descending)
        summary = summary.sort_values("total", ascending=False)
        
        # Round numeric columns
        summary["total"] = summary["total"].round(2)
        summary["average"] = summary["average"].round(2)
        
        return summary
    
    def get_total_spending(self, month: Optional[str] = None) -> float:
        """Get total spending amount.
        
        Args:
            month: Optional month filter (YYYY-MM format).
            
        Returns:
            Total spending amount.
        """
        expenses = self.storage.load_expenses()
        
        if month:
            expenses = [e for e in expenses if e.date.startswith(month)]
        
        return sum(e.amount for e in expenses)
    
    def export_to_csv(self, filepath: str, **filters) -> int:
        """Export expenses to CSV file.
        
        Args:
            filepath: Path to the output CSV file.
            **filters: Optional filters (category, start_date, end_date).
            
        Returns:
            Number of expenses exported.
        """
        expenses = self.list_expenses(**filters)
        
        if not expenses:
            # Create empty CSV with headers
            df = pd.DataFrame(columns=["id", "date", "category", "amount", "description"])
        else:
            df = pd.DataFrame([e.to_dict() for e in expenses])
            # Reorder columns for better readability
            columns = ["id", "date", "category", "amount", "description", "created_at"]
            df = df[[c for c in columns if c in df.columns]]
        
        df.to_csv(filepath, index=False, encoding="utf-8")
        return len(expenses)
    
    def get_categories(self) -> List[str]:
        """Get list of all unique categories.
        
        Returns:
            Sorted list of category names.
        """
        expenses = self.storage.load_expenses()
        categories = set(e.category for e in expenses)
        return sorted(categories)
