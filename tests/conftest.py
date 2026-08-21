"""Pytest fixtures that isolate API tests in an in-memory SQLite database."""

import os

os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from backend.database import Base, engine
from backend.main import app
from backend.models import Budget, Expense


@pytest.fixture(autouse=True)
def reset_database() -> None:
    """Make every test independent and prevent tests touching local data."""
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(delete(Budget))
        connection.execute(delete(Expense))
    yield


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def expense_payload() -> dict[str, object]:
    return {
        "amount": "45.50",
        "category": "Food",
        "description": "Weekly groceries",
        "date": "2026-08-10",
        "payment_method": "Card",
    }
