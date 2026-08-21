"""Expense-management REST endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


@router.get("/categories", response_model=list[str], summary="List supported expense categories")
def get_categories() -> list[str]:
    return schemas.CATEGORIES


@router.get("/payment-methods", response_model=list[schemas.PaymentMethod], summary="List payment methods")
def get_payment_methods() -> list[schemas.PaymentMethod]:
    return list(schemas.PaymentMethod)


@router.get("", response_model=schemas.ExpenseListResponse, summary="List, search, filter, and sort expenses")
def get_expenses(
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100),
    search: str | None = Query(None, max_length=100), category: str | None = Query(None),
    payment_method: schemas.PaymentMethod | None = Query(None), date_from: date | None = None,
    date_to: date | None = None, sort_by: str = Query("date", pattern="^(date|amount|category|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"), db: Session = Depends(get_db),
) -> schemas.ExpenseListResponse:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from cannot be later than date_to")
    items, total = crud.list_expenses(
        db, page=page, page_size=page_size, search=search, category=category,
        payment_method=payment_method.value if payment_method else None, date_from=date_from,
        date_to=date_to, sort_by=sort_by, sort_order=sort_order,
    )
    return schemas.ExpenseListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED, summary="Create an expense")
def post_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)) -> schemas.ExpenseRead:
    return crud.create_expense(db, expense)


@router.get("/{expense_id}", response_model=schemas.ExpenseRead, summary="Get one expense")
def get_expense(expense_id: int, db: Session = Depends(get_db)) -> schemas.ExpenseRead:
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=schemas.ExpenseRead, summary="Update an expense")
def put_expense(expense_id: int, payload: schemas.ExpenseUpdate, db: Session = Depends(get_db)) -> schemas.ExpenseRead:
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return crud.update_expense(db, expense, payload)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an expense")
def remove_expense(expense_id: int, db: Session = Depends(get_db)) -> None:
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    crud.delete_expense(db, expense)
