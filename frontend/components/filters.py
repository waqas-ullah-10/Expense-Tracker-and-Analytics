"""Reusable date-range selector for dashboard and analytics pages."""

from datetime import date, timedelta

import streamlit as st


def date_range_filter(key_prefix: str) -> dict[str, date | None]:
    """Render standard date presets and return API-ready date filters."""
    today = date.today()
    presets = ["Today", "This week", "This month", "Last month", "Custom range"]
    choice = st.selectbox("Date range", presets, key=f"{key_prefix}_range")
    if choice == "Today":
        start = end = today
    elif choice == "This week":
        start, end = today - timedelta(days=today.weekday()), today
    elif choice == "This month":
        start, end = today.replace(day=1), today
    elif choice == "Last month":
        current_month_start = today.replace(day=1)
        end = current_month_start - timedelta(days=1)
        start = end.replace(day=1)
    else:
        selected = st.date_input("Choose dates", value=(today.replace(day=1), today), key=f"{key_prefix}_custom")
        if isinstance(selected, tuple) and len(selected) == 2:
            start, end = selected
        else:
            st.info("Choose both a start and end date to apply a custom range.")
            return {"date_from": None, "date_to": None}
    return {"date_from": start, "date_to": end}
