import streamlit as st
from datetime import datetime
import requests
import pandas as pd
from datetime import date


API_URL = "http://localhost:8000"


def analytics_tab():
    # Dashboard summary for current month
    today = date.today()
    start_of_month = today.replace(day=1)
    payload = {
        "start_date": start_of_month.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d")
    }
    response = requests.post(f"{API_URL}/all-expenses/", json=payload)
    if response.status_code == 200:
        expenses = response.json()
        if expenses:
            df = pd.DataFrame(expenses)
            total_spent = df['amount'].sum()
            top_categories = df.groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
            largest_expense = df.loc[df['amount'].idxmax()]
            num_expenses = len(df)
            avg_expense = df['amount'].mean()
            st.header("📊 Dashboard Overview (This Month)")
            st.metric("Total Spent", f"₹{total_spent:.2f}")
            st.metric("Number of Expenses", num_expenses)
            st.metric("Average Expense", f"₹{avg_expense:.2f}")
            st.write("**Top 3 Categories:**")
            for cat, amt in top_categories.items():
                st.write(f"- {cat}: ₹{amt:.2f}")
            st.write(f"**Largest Expense:** {largest_expense['category']} - ₹{largest_expense['amount']:.2f} ({largest_expense['notes']}) on {largest_expense['expense_date']}")
        else:
            st.info("No expenses found for this month.")
    else:
        st.error("Failed to fetch dashboard data.")

    # Monthly/Yearly Summary
    st.header("📅 Monthly and Yearly Summary")
    response = requests.get(f"{API_URL}/all-expenses/")
    if response.status_code == 200:
        expenses = response.json()
        if expenses:
            df = pd.DataFrame(expenses)
            df['expense_date'] = pd.to_datetime(df['expense_date'])
            df['year'] = df['expense_date'].dt.year
            df['month'] = df['expense_date'].dt.to_period('M')
            # Monthly summary
            monthly_summary = df.groupby('month')['amount'].sum()
            st.subheader("Monthly Expenses")
            st.bar_chart(monthly_summary)
            # Yearly summary
            yearly_summary = df.groupby('year')['amount'].sum()
            st.subheader("Yearly Expenses")
            st.bar_chart(yearly_summary)
        else:
            st.info("No expenses found for monthly/yearly summary.")
    else:
        st.error("Failed to fetch all expenses for summary.")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))

    with col2:
        end_date = st.date_input("End Date", datetime( 2024,    8, 5))

    if st.button("Get Analytics"):
        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        response = requests.post(f"{API_URL}/analytics/", json=payload)
        if response.status_code == 200:
            response_json = response.json()
            if response_json:
                data = {
                    "Category": list(response_json.keys()),
                    "Total": [response_json[category]["total"] for category in response_json],
                    "Percentage": [response_json[category]["percentage"] for category in response_json]
                }
                df = pd.DataFrame(data)
                df_sorted = df.sort_values(by="Percentage", ascending=False)
                st.title("Expense Breakdown By Category")
                st.bar_chart(data=df_sorted.set_index("Category")['Percentage'], width=0, height=0, use_container_width=True)
                df_sorted["Total"] = df_sorted["Total"].map("{:.2f}".format)
                df_sorted["Percentage"] = df_sorted["Percentage"].map("{:.2f}".format)
                st.table(df_sorted)
            else:
                st.info("No analytics data found for the selected range.")
        else:
            st.error("Failed to fetch analytics data from server.")

