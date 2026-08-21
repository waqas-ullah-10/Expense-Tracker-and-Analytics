"""Tests for expense CRUD, filtering, and input validation."""


def test_create_and_get_expense(client, expense_payload) -> None:
    created = client.post("/api/expenses", json=expense_payload)
    assert created.status_code == 201
    expense_id = created.json()["id"]

    fetched = client.get(f"/api/expenses/{expense_id}")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Weekly groceries"
    assert float(fetched.json()["amount"]) == 45.50


def test_list_search_filter_and_sort_expenses(client, expense_payload) -> None:
    client.post("/api/expenses", json=expense_payload)
    client.post("/api/expenses", json={**expense_payload, "amount": "80.00", "category": "Travel", "description": "Train ticket", "date": "2026-08-11", "payment_method": "Cash"})

    response = client.get("/api/expenses", params={"search": "train", "category": "Travel", "sort_by": "amount", "sort_order": "asc"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["description"] == "Train ticket"


def test_update_and_delete_expense(client, expense_payload) -> None:
    expense_id = client.post("/api/expenses", json=expense_payload).json()["id"]
    updated = client.put(f"/api/expenses/{expense_id}", json={"amount": "60.00", "description": "Updated groceries"})
    assert updated.status_code == 200
    assert float(updated.json()["amount"]) == 60.00
    assert updated.json()["description"] == "Updated groceries"

    deleted = client.delete(f"/api/expenses/{expense_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/expenses/{expense_id}").status_code == 404


def test_invalid_and_missing_expenses(client, expense_payload) -> None:
    invalid = client.post("/api/expenses", json={**expense_payload, "amount": "0", "category": "Unknown"})
    assert invalid.status_code == 422
    assert client.get("/api/expenses/9999").status_code == 404
    assert client.put("/api/expenses/9999", json={"amount": "20.00"}).status_code == 404
    assert client.delete("/api/expenses/9999").status_code == 404


def test_invalid_date_range_is_rejected(client) -> None:
    response = client.get("/api/expenses", params={"date_from": "2026-09-01", "date_to": "2026-08-01"})
    assert response.status_code == 422
