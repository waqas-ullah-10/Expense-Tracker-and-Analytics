"""Small HTTP client used by Streamlit; it never accesses the database directly."""

import os
from datetime import date
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 10


class ApiClientError(Exception):
    """A safe, user-friendly error surfaced by the Streamlit interface."""


def _serialise(value: Any) -> Any:
    if isinstance(value, date):
        return value.isoformat()
    return value


def _request(method: str, path: str, *, params: dict | None = None, payload: dict | None = None) -> Any:
    """Call the API and translate network/API failures into friendly exceptions."""
    try:
        response = requests.request(
            method, f"{API_BASE_URL}{path}", params={key: _serialise(value) for key, value in (params or {}).items() if value is not None},
            json={key: _serialise(value) for key, value in (payload or {}).items()} if payload is not None else None,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise ApiClientError("The API is unavailable. Start the FastAPI backend and try again.") from exc

    if response.status_code == 204:
        return None
    if not response.ok:
        try:
            detail = response.json().get("detail", "Request failed")
        except ValueError:
            detail = "Request failed"
        if isinstance(detail, list):
            detail = "; ".join(item.get("msg", "Invalid input") for item in detail)
        raise ApiClientError(str(detail))
    return response.json()


def get_expenses(**filters: Any) -> dict[str, Any]:
    return _request("GET", "/api/expenses", params=filters)


def get_expense(expense_id: int) -> dict[str, Any]:
    return _request("GET", f"/api/expenses/{expense_id}")


def create_expense(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/api/expenses", payload=payload)


def update_expense(expense_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return _request("PUT", f"/api/expenses/{expense_id}", payload=payload)


def delete_expense(expense_id: int) -> None:
    _request("DELETE", f"/api/expenses/{expense_id}")


def get_summary(**filters: Any) -> dict[str, Any]:
    return _request("GET", "/api/analytics/summary", params=filters)


def get_category_analytics(**filters: Any) -> list[dict[str, Any]]:
    return _request("GET", "/api/analytics/categories", params=filters)


def get_monthly_analytics(**filters: Any) -> list[dict[str, Any]]:
    return _request("GET", "/api/analytics/monthly", params=filters)


def get_daily_analytics(**filters: Any) -> list[dict[str, Any]]:
    return _request("GET", "/api/analytics/daily", params=filters)


def get_payment_method_analytics(**filters: Any) -> list[dict[str, Any]]:
    return _request("GET", "/api/analytics/payment-methods", params=filters)


def get_top_expenses(**filters: Any) -> list[dict[str, Any]]:
    return _request("GET", "/api/analytics/top-expenses", params=filters)


def get_budgets() -> list[dict[str, Any]]:
    return _request("GET", "/api/budgets")


def create_budget(payload: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/api/budgets", payload=payload)


def update_budget(budget_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return _request("PUT", f"/api/budgets/{budget_id}", payload=payload)


def delete_budget(budget_id: int) -> None:
    _request("DELETE", f"/api/budgets/{budget_id}")


def get_budget_overview(month: int, year: int) -> dict[str, Any]:
    return _request("GET", "/api/budgets/overview", params={"month": month, "year": year})
