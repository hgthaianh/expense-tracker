"""CLI interface for the expense tracker using Typer."""

from typing import Optional
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .manager import ExpenseManager
from .storage import JSONStorage

# Initialize Typer app
app = typer.Typer(
    name="expense-tracker",
    help="📊 Personal Expense Tracker CLI - Track your expenses easily!",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()

# Default storage file
DEFAULT_STORAGE = "expenses.json"


def get_manager(storage_file: str = DEFAULT_STORAGE) -> ExpenseManager:
    """Get ExpenseManager instance with specified storage file."""
    storage = JSONStorage(storage_file)
    return ExpenseManager(storage)


@app.command()
def add(
    amount: float = typer.Argument(..., help="Expense amount (positive number)"),
    category: str = typer.Argument(..., help="Expense category (e.g., food, transport, rent)"),
    description: str = typer.Argument(..., help="Description of the expense"),
    date: Optional[str] = typer.Option(
        None,
        "--date", "-d",
        help="Expense date (YYYY-MM-DD). Defaults to today."
    ),
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """💰 Add a new expense."""
    try:
        manager = get_manager(storage_file)
        expense = manager.add_expense(
            amount=amount,
            category=category,
            description=description,
            date=date
        )
        
        console.print(Panel(
            f"[bold green]✓ Expense added successfully![/bold green]\n\n"
            f"[cyan]ID:[/cyan] {expense.id}\n"
            f"[cyan]Amount:[/cyan] ${expense.amount:.2f}\n"
            f"[cyan]Category:[/cyan] {expense.category}\n"
            f"[cyan]Description:[/cyan] {expense.description}\n"
            f"[cyan]Date:[/cyan] {expense.date}",
            title="New Expense",
            border_style="green"
        ))
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_expenses(
    category: Optional[str] = typer.Option(
        None,
        "--category", "-c",
        help="Filter by category"
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "--start-date",
        help="Filter from date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="Filter to date (YYYY-MM-DD)"
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit", "-n",
        help="Maximum number of expenses to show"
    ),
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """📋 List all expenses with optional filters."""
    manager = get_manager(storage_file)
    expenses = manager.list_expenses(
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    if not expenses:
        console.print("[yellow]No expenses found.[/yellow]")
        return
    
    # Create a beautiful table
    table = Table(
        title="💳 Your Expenses",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True
    )
    
    table.add_column("ID", style="dim", width=10)
    table.add_column("Date", style="blue", width=12)
    table.add_column("Category", style="magenta", width=15)
    table.add_column("Amount", style="green", justify="right", width=12)
    table.add_column("Description", style="white", width=30)
    
    for expense in expenses:
        table.add_row(
            expense.id,
            expense.date,
            expense.category,
            f"${expense.amount:.2f}",
            expense.description
        )
    
    console.print(table)
    
    # Show total
    total = sum(e.amount for e in expenses)
    console.print(f"\n[bold]Total:[/bold] [green]${total:.2f}[/green] ({len(expenses)} expenses)")


@app.command()
def delete(
    expense_id: str = typer.Argument(..., help="ID of the expense to delete"),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompt"
    ),
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """🗑️  Delete an expense by ID."""
    manager = get_manager(storage_file)
    
    # Check if expense exists
    expense = manager.storage.get_expense_by_id(expense_id)
    if not expense:
        console.print(f"[bold red]Error:[/bold red] Expense with ID '{expense_id}' not found.")
        raise typer.Exit(1)
    
    # Show expense details and confirm
    if not force:
        console.print(Panel(
            f"[cyan]ID:[/cyan] {expense.id}\n"
            f"[cyan]Amount:[/cyan] ${expense.amount:.2f}\n"
            f"[cyan]Category:[/cyan] {expense.category}\n"
            f"[cyan]Description:[/cyan] {expense.description}\n"
            f"[cyan]Date:[/cyan] {expense.date}",
            title="Expense to Delete",
            border_style="yellow"
        ))
        
        confirm = typer.confirm("Are you sure you want to delete this expense?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Delete the expense
    if manager.delete_expense(expense_id):
        console.print(f"[bold green]✓ Expense '{expense_id}' deleted successfully![/bold green]")
    else:
        console.print(f"[bold red]Error:[/bold red] Failed to delete expense.")
        raise typer.Exit(1)


@app.command()
def summary(
    month: Optional[str] = typer.Option(
        None,
        "--month", "-m",
        help="Filter by month (YYYY-MM format)"
    ),
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """📊 Show spending summary by category."""
    manager = get_manager(storage_file)
    
    summary_df = manager.get_summary(month=month)
    total = manager.get_total_spending(month=month)
    
    if summary_df.empty:
        console.print("[yellow]No expenses found for the specified period.[/yellow]")
        return
    
    # Create summary table
    title = "📊 Spending Summary"
    if month:
        title += f" ({month})"
    
    table = Table(
        title=title,
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    
    table.add_column("Category", style="magenta", width=15)
    table.add_column("Total", style="green", justify="right", width=12)
    table.add_column("Count", style="blue", justify="center", width=8)
    table.add_column("Average", style="yellow", justify="right", width=12)
    
    for _, row in summary_df.iterrows():
        table.add_row(
            row["category"],
            f"${row['total']:.2f}",
            str(int(row["count"])),
            f"${row['average']:.2f}"
        )
    
    console.print(table)
    console.print(f"\n[bold]Grand Total:[/bold] [green]${total:.2f}[/green]")


@app.command()
def export(
    output_file: str = typer.Argument(
        "expenses.csv",
        help="Output CSV file path"
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category", "-c",
        help="Filter by category"
    ),
    start_date: Optional[str] = typer.Option(
        None,
        "--start-date",
        help="Filter from date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None,
        "--end-date",
        help="Filter to date (YYYY-MM-DD)"
    ),
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """📤 Export expenses to CSV file."""
    manager = get_manager(storage_file)
    
    count = manager.export_to_csv(
        filepath=output_file,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    
    console.print(f"[bold green]✓ Exported {count} expenses to '{output_file}'[/bold green]")


@app.command()
def categories(
    storage_file: str = typer.Option(
        DEFAULT_STORAGE,
        "--storage", "-s",
        help="Path to storage file"
    ),
):
    """🏷️  List all expense categories."""
    manager = get_manager(storage_file)
    cats = manager.get_categories()
    
    if not cats:
        console.print("[yellow]No categories found. Add some expenses first![/yellow]")
        return
    
    console.print("[bold cyan]Available Categories:[/bold cyan]")
    for cat in cats:
        console.print(f"  • {cat}")


@app.callback()
def main():
    """
    📊 Personal Expense Tracker CLI
    
    Track your daily expenses with ease. Data is stored locally in a JSON file.
    """
    pass


if __name__ == "__main__":
    app()
