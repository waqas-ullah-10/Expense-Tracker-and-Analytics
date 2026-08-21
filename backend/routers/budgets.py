"""Monthly-budget REST endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.services import analytics

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


@router.get("", response_model=list[schemas.BudgetRead], summary="List monthly budgets")
def get_budgets(db: Session = Depends(get_db)) -> list[schemas.BudgetRead]:
    return crud.list_budgets(db)


@router.get("/overview", response_model=schemas.BudgetOverview, summary="Get budget spending progress")
def get_budget_overview(month: int | None = None, year: int | None = None, db: Session = Depends(get_db)) -> schemas.BudgetOverview:
    today = date.today()
    target_month, target_year = month or today.month, year or today.year
    if not 1 <= target_month <= 12 or not 2000 <= target_year <= 2100:
        raise HTTPException(status_code=422, detail="month or year is invalid")
    return analytics.budget_overview(db, target_month, target_year)


@router.post("", response_model=schemas.BudgetRead, status_code=status.HTTP_201_CREATED, summary="Create a monthly budget")
def post_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)) -> schemas.BudgetRead:
    if crud.get_budget_for_month(db, budget.month, budget.year):
        raise HTTPException(status_code=409, detail="A budget already exists for this month")
    return crud.create_budget(db, budget)


@router.put("/{budget_id}", response_model=schemas.BudgetRead, summary="Update a monthly budget")
def put_budget(budget_id: int, payload: schemas.BudgetUpdate, db: Session = Depends(get_db)) -> schemas.BudgetRead:
    budget = crud.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    merged_month = payload.month if payload.month is not None else budget.month
    merged_year = payload.year if payload.year is not None else budget.year
    matching_budget = crud.get_budget_for_month(db, merged_month, merged_year)
    if matching_budget and matching_budget.id != budget_id:
        raise HTTPException(status_code=409, detail="A budget already exists for this month")
    return crud.update_budget(db, budget, payload)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a monthly budget")
def remove_budget(budget_id: int, db: Session = Depends(get_db)) -> None:
    budget = crud.get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    crud.delete_budget(db, budget)
