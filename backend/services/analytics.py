"""Database-independent aggregation logic for analytics and budget progress."""

from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend import models, schemas

ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _filtered_expenses(db: Session, date_from: date | None, date_to: date | None) -> list[models.Expense]:
    query = select(models.Expense)
    if date_from:
        query = query.where(models.Expense.date >= date_from)
    if date_to:
        query = query.where(models.Expense.date <= date_to)
    return list(db.scalars(query.order_by(models.Expense.date)).all())


def summary(db: Session, date_from: date | None = None, date_to: date | None = None) -> schemas.SummaryResponse:
    """Calculate dashboard metrics for the selected date range."""
    expenses = _filtered_expenses(db, date_from, date_to)
    total = sum((expense.amount for expense in expenses), ZERO)
    daily_totals: dict[date, Decimal] = defaultdict(lambda: ZERO)
    category_totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for expense in expenses:
        daily_totals[expense.date] += expense.amount
        category_totals[expense.category] += expense.amount

    today = date.today()
    current_month_total = sum(
        (expense.amount for expense in expenses if expense.date.year == today.year and expense.date.month == today.month),
        ZERO,
    )
    return schemas.SummaryResponse(
        total_expenses=_round(total),
        current_month_expenses=_round(current_month_total),
        average_daily_expense=_round(total / len(daily_totals)) if daily_totals else ZERO,
        transaction_count=len(expenses),
        highest_expense=_round(max((expense.amount for expense in expenses), default=ZERO)),
        most_expensive_category=max(category_totals, key=category_totals.get) if category_totals else None,
    )


def _aggregate(expenses: list[models.Expense], key_name: str) -> list[schemas.AggregateItem]:
    totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for expense in expenses:
        totals[getattr(expense, key_name)] += expense.amount
    return [schemas.AggregateItem(label=label, total=_round(total)) for label, total in sorted(totals.items())]


def category_totals(db: Session, date_from: date | None, date_to: date | None) -> list[schemas.AggregateItem]:
    return _aggregate(_filtered_expenses(db, date_from, date_to), "category")


def payment_method_totals(db: Session, date_from: date | None, date_to: date | None) -> list[schemas.AggregateItem]:
    return _aggregate(_filtered_expenses(db, date_from, date_to), "payment_method")


def monthly_totals(db: Session, date_from: date | None, date_to: date | None) -> list[schemas.AggregateItem]:
    expenses = _filtered_expenses(db, date_from, date_to)
    totals: dict[str, Decimal] = defaultdict(lambda: ZERO)
    for expense in expenses:
        totals[expense.date.strftime("%Y-%m")] += expense.amount
    return [schemas.AggregateItem(label=label, total=_round(total)) for label, total in sorted(totals.items())]


def daily_totals(db: Session, date_from: date | None, date_to: date | None) -> list[schemas.DailyAggregateItem]:
    expenses = _filtered_expenses(db, date_from, date_to)
    totals: dict[date, Decimal] = defaultdict(lambda: ZERO)
    for expense in expenses:
        totals[expense.date] += expense.amount
    return [schemas.DailyAggregateItem(label=item_date.isoformat(), date=item_date, total=_round(total)) for item_date, total in sorted(totals.items())]


def top_expenses(db: Session, date_from: date | None, date_to: date | None, limit: int) -> list[models.Expense]:
    return sorted(_filtered_expenses(db, date_from, date_to), key=lambda expense: expense.amount, reverse=True)[:limit]


def budget_overview(db: Session, month: int, year: int) -> schemas.BudgetOverview:
    """Compare the stored monthly budget with expenses in that same calendar month."""
    budget = db.scalar(select(models.Budget).where(models.Budget.month == month, models.Budget.year == year))
    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
    spent = sum((expense.amount for expense in _filtered_expenses(db, start, end)), ZERO)
    if not budget:
        return schemas.BudgetOverview(budget=None, total_spent=_round(spent), remaining_budget=None, percentage_used=None, status="not_set")
    remaining = budget.amount - spent
    percentage = (spent / budget.amount) * Decimal("100")
    status = "over" if percentage > 100 else "warning" if percentage >= 80 else "on_track"
    return schemas.BudgetOverview(
        budget=schemas.BudgetRead.model_validate(budget), total_spent=_round(spent),
        remaining_budget=_round(remaining), percentage_used=_round(percentage), status=status,
    )
