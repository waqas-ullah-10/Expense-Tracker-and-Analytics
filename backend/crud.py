"""Database operations that are shared by routers and services."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend import models, schemas


def _expense_filters(
    *, search: str | None = None, category: str | None = None,
    payment_method: str | None = None, date_from: date | None = None,
    date_to: date | None = None,
) -> list:
    filters = []
    if search:
        filters.append(models.Expense.description.ilike(f"%{search.strip()}%"))
    if category:
        filters.append(models.Expense.category == category)
    if payment_method:
        filters.append(models.Expense.payment_method == payment_method)
    if date_from:
        filters.append(models.Expense.date >= date_from)
    if date_to:
        filters.append(models.Expense.date <= date_to)
    return filters


def list_expenses(
    db: Session, *, page: int = 1, page_size: int = 50, search: str | None = None,
    category: str | None = None, payment_method: str | None = None,
    date_from: date | None = None, date_to: date | None = None,
    sort_by: str = "date", sort_order: str = "desc",
) -> tuple[list[models.Expense], int]:
    """Return one filtered and sorted page of expenses."""
    filters = _expense_filters(
        search=search, category=category, payment_method=payment_method,
        date_from=date_from, date_to=date_to,
    )
    sortable_fields = {
        "date": models.Expense.date, "amount": models.Expense.amount,
        "category": models.Expense.category, "created_at": models.Expense.created_at,
    }
    column = sortable_fields[sort_by]
    order_clause = column.asc() if sort_order == "asc" else column.desc()
    statement = (
        select(models.Expense).where(*filters).order_by(order_clause, models.Expense.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    total = db.scalar(select(func.count()).select_from(models.Expense).where(*filters)) or 0
    return list(db.scalars(statement).all()), total


def get_expense(db: Session, expense_id: int) -> models.Expense | None:
    return db.get(models.Expense, expense_id)


def create_expense(db: Session, expense: schemas.ExpenseCreate) -> models.Expense:
    db_expense = models.Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def update_expense(
    db: Session, db_expense: models.Expense, expense: schemas.ExpenseUpdate
) -> models.Expense:
    for field, value in expense.model_dump(exclude_unset=True).items():
        setattr(db_expense, field, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, db_expense: models.Expense) -> None:
    db.delete(db_expense)
    db.commit()


def list_budgets(db: Session) -> list[models.Budget]:
    return list(db.scalars(select(models.Budget).order_by(models.Budget.year.desc(), models.Budget.month.desc())).all())


def get_budget(db: Session, budget_id: int) -> models.Budget | None:
    return db.get(models.Budget, budget_id)


def get_budget_for_month(db: Session, month: int, year: int) -> models.Budget | None:
    return db.scalar(select(models.Budget).where(models.Budget.month == month, models.Budget.year == year))


def create_budget(db: Session, budget: schemas.BudgetCreate) -> models.Budget:
    db_budget = models.Budget(**budget.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def update_budget(db: Session, db_budget: models.Budget, budget: schemas.BudgetUpdate) -> models.Budget:
    for field, value in budget.model_dump(exclude_unset=True).items():
        setattr(db_budget, field, value)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, db_budget: models.Budget) -> None:
    db.delete(db_budget)
    db.commit()
