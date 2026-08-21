"""Pydantic request and response schemas plus shared validation rules."""

from datetime import date as Date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

CATEGORIES = [
    "Food", "Transportation", "Shopping", "Bills", "Entertainment",
    "Healthcare", "Education", "Travel", "Rent", "Other",
]


class PaymentMethod(str, Enum):
    CASH = "Cash"
    CARD = "Card"
    BANK_TRANSFER = "Bank Transfer"
    DIGITAL_WALLET = "Digital Wallet"


def validate_category(value: str) -> str:
    """Keep validation in one place so category rules are easy to extend later."""
    value = value.strip().title()
    if value not in CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
    return value


class ExpenseBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=1, max_length=500)
    date: Date
    payment_method: PaymentMethod

    @field_validator("category")
    @classmethod
    def category_is_supported(cls, value: str) -> str:
        return validate_category(value)

    @field_validator("description")
    @classmethod
    def description_is_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Description cannot be empty")
        return value


class ExpenseCreate(ExpenseBase):
    """Payload used to create an expense."""


class ExpenseUpdate(BaseModel):
    """Partial payload used to update an expense."""

    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    date: Date | None = None
    payment_method: PaymentMethod | None = None

    @field_validator("category")
    @classmethod
    def category_is_supported(cls, value: str | None) -> str | None:
        return validate_category(value) if value is not None else value

    @field_validator("description")
    @classmethod
    def description_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Description cannot be empty")
        return value


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ExpenseListResponse(BaseModel):
    items: list[ExpenseRead]
    total: int
    page: int
    page_size: int


class BudgetBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetCreate(BudgetBase):
    """Payload used to create a monthly budget."""


class BudgetUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    month: int | None = Field(default=None, ge=1, le=12)
    year: int | None = Field(default=None, ge=2000, le=2100)


class BudgetRead(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BudgetOverview(BaseModel):
    budget: BudgetRead | None
    total_spent: Decimal
    remaining_budget: Decimal | None
    percentage_used: Decimal | None
    status: str


class SummaryResponse(BaseModel):
    total_expenses: Decimal
    current_month_expenses: Decimal
    average_daily_expense: Decimal
    transaction_count: int
    highest_expense: Decimal
    most_expensive_category: str | None


class AggregateItem(BaseModel):
    label: str
    total: Decimal


class DailyAggregateItem(AggregateItem):
    date: Date


class TopExpense(ExpenseRead):
    """Expense response reused by the analytics endpoint."""
