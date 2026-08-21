"""Tests for analytics totals returned by the API."""

from datetime import date


def add(client, *, amount: str, category: str, payment_method: str, day: int, description: str = "Expense") -> None:
    client.post("/api/expenses", json={"amount": amount, "category": category, "description": description, "date": date.today().replace(day=day).isoformat(), "payment_method": payment_method})


def test_summary_calculations(client) -> None:
    add(client, amount="20.00", category="Food", payment_method="Cash", day=1)
    add(client, amount="40.00", category="Travel", payment_method="Card", day=2)
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    body = response.json()
    assert float(body["total_expenses"]) == 60.0
    assert body["transaction_count"] == 2
    assert float(body["average_daily_expense"]) == 30.0
    assert float(body["highest_expense"]) == 40.0
    assert body["most_expensive_category"] == "Travel"


def test_category_monthly_payment_and_daily_totals(client) -> None:
    add(client, amount="10.00", category="Food", payment_method="Cash", day=1)
    add(client, amount="15.00", category="Food", payment_method="Card", day=1)
    add(client, amount="25.00", category="Bills", payment_method="Card", day=2)

    categories = {item["label"]: float(item["total"]) for item in client.get("/api/analytics/categories").json()}
    payments = {item["label"]: float(item["total"]) for item in client.get("/api/analytics/payment-methods").json()}
    monthly = client.get("/api/analytics/monthly").json()
    daily = client.get("/api/analytics/daily").json()
    top = client.get("/api/analytics/top-expenses").json()
    assert categories == {"Bills": 25.0, "Food": 25.0}
    assert payments == {"Card": 40.0, "Cash": 10.0}
    assert float(monthly[0]["total"]) == 50.0
    assert len(daily) == 2
    assert float(top[0]["amount"]) == 25.0
