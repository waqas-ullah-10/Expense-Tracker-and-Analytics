"""Streamlit application for Expense Tracker & Analytics."""

from datetime import date

import pandas as pd
import streamlit as st

from frontend import api_client
from frontend.api_client import ApiClientError
from frontend.components.filters import date_range_filter

CATEGORIES = ["Food", "Transportation", "Shopping", "Bills", "Entertainment", "Healthcare", "Education", "Travel", "Rent", "Other"]
PAYMENT_METHODS = ["Cash", "Card", "Bank Transfer", "Digital Wallet"]

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")


def money(value: object) -> str:
    return f"${float(value or 0):,.2f}"


def show_api_error(error: ApiClientError) -> None:
    st.error(f"Unable to complete that action: {error}")


def add_expense_form(prefix: str = "add") -> None:
    """Draw the validated expense form used on the Add Expense page."""
    with st.form(f"{prefix}_expense_form", clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            amount = st.number_input("Amount", min_value=0.01, step=1.0, format="%.2f")
            category = st.selectbox("Category", CATEGORIES)
            expense_date = st.date_input("Date", value=date.today())
        with right:
            payment_method = st.selectbox("Payment method", PAYMENT_METHODS)
            description = st.text_area("Description", max_chars=500, placeholder="e.g. Weekly grocery shopping")
        submitted = st.form_submit_button("Save expense", type="primary")
    if submitted:
        if not description.strip():
            st.warning("Please enter a short description.")
            return
        try:
            api_client.create_expense({"amount": amount, "category": category, "description": description, "date": expense_date, "payment_method": payment_method})
            st.success("Expense saved successfully.")
        except ApiClientError as error:
            show_api_error(error)


def dashboard() -> None:
    st.title("Dashboard")
    st.caption("A quick view of your spending for the selected period.")
    filters = date_range_filter("dashboard")
    try:
        summary = api_client.get_summary(**filters)
        metrics = st.columns(3)
        metrics[0].metric("Total expenses", money(summary["total_expenses"]))
        metrics[1].metric("Current month", money(summary["current_month_expenses"]))
        metrics[2].metric("Transactions", summary["transaction_count"])
        metrics = st.columns(3)
        metrics[0].metric("Average daily", money(summary["average_daily_expense"]))
        metrics[1].metric("Highest expense", money(summary["highest_expense"]))
        metrics[2].metric("Top category", summary["most_expensive_category"] or "—")

        categories = api_client.get_category_analytics(**filters)
        daily = api_client.get_daily_analytics(**filters)
        left, right = st.columns(2)
        with left:
            st.subheader("Spending by category")
            if categories:
                frame = pd.DataFrame(categories).set_index("label")
                st.bar_chart(frame["total"])
            else:
                st.info("No expense data for this period.")
        with right:
            st.subheader("Daily spending")
            if daily:
                frame = pd.DataFrame(daily).set_index("date")
                st.line_chart(frame["total"])
            else:
                st.info("No expense data for this period.")
    except ApiClientError as error:
        show_api_error(error)


def expenses_page() -> None:
    st.title("Expenses")
    st.caption("Search, filter, edit, or remove transactions.")
    with st.expander("Filters", expanded=True):
        row = st.columns(4)
        search = row[0].text_input("Search descriptions")
        category = row[1].selectbox("Category", ["All"] + CATEGORIES)
        payment = row[2].selectbox("Payment method", ["All"] + PAYMENT_METHODS)
        sort_by = row[3].selectbox("Sort by", ["date", "amount", "category", "created_at"])
        sort_order = st.radio("Order", ["desc", "asc"], horizontal=True)
    try:
        result = api_client.get_expenses(
            search=search or None, category=None if category == "All" else category,
            payment_method=None if payment == "All" else payment, sort_by=sort_by,
            sort_order=sort_order, page_size=100,
        )
        items = result["items"]
        st.caption(f"{result['total']} transaction(s) found")
        if not items:
            st.info("No expenses match these filters.")
            return
        display = pd.DataFrame(items)[["id", "date", "category", "description", "payment_method", "amount"]]
        st.dataframe(display, hide_index=True, use_container_width=True, column_config={"amount": st.column_config.NumberColumn("Amount", format="$%.2f")})
        st.subheader("Edit or delete an expense")
        selected_id = st.selectbox("Choose an expense", [item["id"] for item in items], format_func=lambda expense_id: next(f"#{item['id']} — {item['description']}" for item in items if item["id"] == expense_id))
        selected = next(item for item in items if item["id"] == selected_id)
        with st.form("edit_expense_form"):
            columns = st.columns(2)
            with columns[0]:
                amount = st.number_input("Amount", min_value=0.01, value=float(selected["amount"]), step=1.0, format="%.2f", key="edit_amount")
                edit_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(selected["category"]), key="edit_category")
                expense_date = st.date_input("Date", value=date.fromisoformat(selected["date"]), key="edit_date")
            with columns[1]:
                method = st.selectbox("Payment method", PAYMENT_METHODS, index=PAYMENT_METHODS.index(selected["payment_method"]), key="edit_method")
                description = st.text_area("Description", value=selected["description"], max_chars=500, key="edit_description")
            save = st.form_submit_button("Update expense", type="primary")
        if save:
            try:
                api_client.update_expense(selected_id, {"amount": amount, "category": edit_category, "description": description, "date": expense_date, "payment_method": method})
                st.success("Expense updated. Refresh the page to see the latest table.")
            except ApiClientError as error:
                show_api_error(error)
        if st.button("Delete selected expense", type="secondary"):
            try:
                api_client.delete_expense(selected_id)
                st.success("Expense deleted. Refresh the page to update the table.")
            except ApiClientError as error:
                show_api_error(error)
    except ApiClientError as error:
        show_api_error(error)


def analytics_page() -> None:
    st.title("Analytics")
    st.caption("Explore how and where you spend money.")
    filters = date_range_filter("analytics")
    try:
        categories = api_client.get_category_analytics(**filters)
        monthly = api_client.get_monthly_analytics(**filters)
        daily = api_client.get_daily_analytics(**filters)
        payments = api_client.get_payment_method_analytics(**filters)
        top = api_client.get_top_expenses(**filters, limit=10)
        left, right = st.columns(2)
        with left:
            st.subheader("Category analysis")
            if categories:
                st.bar_chart(pd.DataFrame(categories).set_index("label")["total"])
            else:
                st.info("No category data.")
        with right:
            st.subheader("Payment methods")
            if payments:
                st.bar_chart(pd.DataFrame(payments).set_index("label")["total"])
            else:
                st.info("No payment-method data.")
        left, right = st.columns(2)
        with left:
            st.subheader("Monthly analysis")
            if monthly:
                st.line_chart(pd.DataFrame(monthly).set_index("label")["total"])
            else:
                st.info("No monthly data.")
        with right:
            st.subheader("Daily spending")
            if daily:
                st.line_chart(pd.DataFrame(daily).set_index("date")["total"])
            else:
                st.info("No daily data.")
        st.subheader("Top expenses")
        if top:
            table = pd.DataFrame(top)[["date", "category", "description", "payment_method", "amount"]]
            st.dataframe(table, hide_index=True, use_container_width=True, column_config={"amount": st.column_config.NumberColumn("Amount", format="$%.2f")})
        else:
            st.info("No expenses for this period.")
    except ApiClientError as error:
        show_api_error(error)


def budget_page() -> None:
    st.title("Budget")
    st.caption("Set a monthly limit and monitor your progress.")
    today = date.today()
    selection = st.columns(2)
    month = selection[0].number_input("Month", min_value=1, max_value=12, value=today.month, step=1)
    year = selection[1].number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1)
    try:
        overview = api_client.get_budget_overview(int(month), int(year))
        budget = overview["budget"]
        if budget:
            row = st.columns(4)
            row[0].metric("Monthly budget", money(budget["amount"]))
            row[1].metric("Total spent", money(overview["total_spent"]))
            row[2].metric("Remaining", money(overview["remaining_budget"]))
            row[3].metric("Used", f"{float(overview['percentage_used']):.1f}%")
            st.progress(min(float(overview["percentage_used"]) / 100, 1.0))
            if overview["status"] == "over":
                st.error("You have exceeded this monthly budget.")
            elif overview["status"] == "warning":
                st.warning("You have used at least 80% of this monthly budget.")
            else:
                st.success("Your spending is currently within budget.")
            with st.form("update_budget"):
                amount = st.number_input("New budget amount", min_value=0.01, value=float(budget["amount"]), step=10.0, format="%.2f")
                update = st.form_submit_button("Update budget")
            if update:
                api_client.update_budget(budget["id"], {"amount": amount})
                st.success("Budget updated. Refresh to update the figures.")
            if st.button("Delete this monthly budget"):
                api_client.delete_budget(budget["id"])
                st.success("Budget deleted. Refresh to update the page.")
        else:
            st.info(f"No budget has been set for {int(month):02d}/{int(year)}. Spending so far: {money(overview['total_spent'])}.")
            with st.form("create_budget"):
                amount = st.number_input("Monthly budget amount", min_value=0.01, value=1000.0, step=10.0, format="%.2f")
                create = st.form_submit_button("Create budget", type="primary")
            if create:
                api_client.create_budget({"amount": amount, "month": int(month), "year": int(year)})
                st.success("Budget created. Refresh to see its progress.")
    except ApiClientError as error:
        show_api_error(error)


def main() -> None:
    with st.sidebar:
        st.title("💸 Expense Tracker")
        page = st.radio("Navigation", ["Dashboard", "Expenses", "Add Expense", "Analytics", "Budget"])
        st.divider()
        st.caption("The Streamlit app communicates only with FastAPI over HTTP.")
    if page == "Dashboard":
        dashboard()
    elif page == "Expenses":
        expenses_page()
    elif page == "Add Expense":
        st.title("Add Expense")
        st.caption("Record a new transaction.")
        add_expense_form()
    elif page == "Analytics":
        analytics_page()
    else:
        budget_page()


if __name__ == "__main__":
    main()
