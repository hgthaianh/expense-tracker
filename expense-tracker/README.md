# Personal Expense Tracker CLI

A simple command-line interface for tracking personal expenses. Built with Python, Typer, and Pandas.

## Features

- ✅ Add expenses with amount, category, and description
- ✅ List all expenses with optional filters
- ✅ Delete expenses by ID
- ✅ View spending summary by category
- ✅ Export expenses to CSV
- ✅ Data persisted in JSON file

## Installation

```bash
# Clone or navigate to the project directory
cd expense-tracker

# Install in development mode
pip install -e .
```

## Usage

### Add an Expense

```bash
expense-tracker add 50.00 food "Lunch at restaurant"
expense-tracker add 1500 rent "Monthly rent payment"
expense-tracker add 25.50 transport "Grab ride to work"
```

### List Expenses

```bash
# List all expenses
expense-tracker list

# Filter by category
expense-tracker list --category food

# Filter by date range
expense-tracker list --start-date 2026-01-01 --end-date 2026-01-31

# Limit number of results
expense-tracker list --limit 10
```

### View Summary

```bash
# Summary by category
expense-tracker summary

# Summary for a specific month
expense-tracker summary --month 2026-01
```

### Delete an Expense

```bash
expense-tracker delete <expense-id>
```

### Export to CSV

```bash
expense-tracker export expenses_backup.csv
```

## Data Storage

Expenses are stored in `expenses.json` in the current directory. The file is created automatically when you add your first expense.

## License

MIT License - see [LICENSE](LICENSE) for details.
