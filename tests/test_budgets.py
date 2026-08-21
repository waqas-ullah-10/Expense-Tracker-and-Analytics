"""Tests for monthly budget CRUD and spending-progress calculations."""

from datetime import date


def test_create_retrieve_update_and_delete_budget(client) -> None:
    payload = {"amount": "1000.00", "month": 8, "year": 2026}
    created = client.post("/api/budgets", json=payload)
    assert created.status_code == 201
    budget_id = created.json()["id"]
    assert len(client.get("/api/budgets").json()) == 1

    updated = client.put(f"/api/budgets/{budget_id}", json={"amount": "1200.00"})
    assert updated.status_code == 200
    assert float(updated.json()["amount"]) == 1200.0
    assert client.delete(f"/api/budgets/{budget_id}").status_code == 204
    assert client.put("/api/budgets/9999", json={"amount": "30.00"}).status_code == 404


def test_budget_calculations_and_duplicate_protection(client) -> None:
    today = date.today()
    client.post("/api/budgets", json={"amount": "100.00", "month": today.month, "year": today.year})
    duplicate = client.post("/api/budgets", json={"amount": "200.00", "month": today.month, "year": today.year})
    assert duplicate.status_code == 409
    client.post("/api/expenses", json={"amount": "85.00", "category": "Food", "description": "Groceries", "date": today.isoformat(), "payment_method": "Card"})
    overview = client.get("/api/budgets/overview", params={"month": today.month, "year": today.year})
    assert overview.status_code == 200
    body = overview.json()
    assert float(body["total_spent"]) == 85.0
    assert float(body["remaining_budget"]) == 15.0
    assert float(body["percentage_used"]) == 85.0
    assert body["status"] == "warning"
