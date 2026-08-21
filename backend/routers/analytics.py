"""Analytics REST endpoints."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend import schemas
from backend.database import get_db
from backend.services import analytics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def validate_dates(date_from: date | None, date_to: date | None) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="date_from cannot be later than date_to")


@router.get("/summary", response_model=schemas.SummaryResponse, summary="Get dashboard metrics")
def get_summary(date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)) -> schemas.SummaryResponse:
    validate_dates(date_from, date_to)
    return analytics.summary(db, date_from, date_to)


@router.get("/categories", response_model=list[schemas.AggregateItem], summary="Get spending totals by category")
def get_categories(date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)) -> list[schemas.AggregateItem]:
    validate_dates(date_from, date_to)
    return analytics.category_totals(db, date_from, date_to)


@router.get("/monthly", response_model=list[schemas.AggregateItem], summary="Get spending totals by month")
def get_monthly(date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)) -> list[schemas.AggregateItem]:
    validate_dates(date_from, date_to)
    return analytics.monthly_totals(db, date_from, date_to)


@router.get("/daily", response_model=list[schemas.DailyAggregateItem], summary="Get spending totals by day")
def get_daily(date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)) -> list[schemas.DailyAggregateItem]:
    validate_dates(date_from, date_to)
    return analytics.daily_totals(db, date_from, date_to)


@router.get("/payment-methods", response_model=list[schemas.AggregateItem], summary="Get spending totals by payment method")
def get_payment_methods(date_from: date | None = None, date_to: date | None = None, db: Session = Depends(get_db)) -> list[schemas.AggregateItem]:
    validate_dates(date_from, date_to)
    return analytics.payment_method_totals(db, date_from, date_to)


@router.get("/top-expenses", response_model=list[schemas.TopExpense], summary="Get the largest expenses")
def get_top_expenses(date_from: date | None = None, date_to: date | None = None, limit: int = Query(5, ge=1, le=50), db: Session = Depends(get_db)) -> list[schemas.TopExpense]:
    validate_dates(date_from, date_to)
    return analytics.top_expenses(db, date_from, date_to, limit)
