import streamlit as st
import pandas as pd
from datetime import datetime
import requests

API_URL = "http://localhost:8000"

def view_by_category_tab():
    st.title("🔍 View Expenses by Category")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))
    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 5))
    with col3:
        category = st.selectbox("Category", ["Food", "Rent", "Shopping", "Entertainment", "Other"])

    if st.button("Fetch Expenses"):
        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "category": category
        }

        response = requests.post(f"{API_URL}/category-expenses/", json=payload)

        if response.status_code == 200:
            expenses = response.json()
            if not expenses:
                st.info("No expenses found for the selected category and date range.")
                return

            df = pd.DataFrame(expenses)
            df['expense_date'] = pd.to_datetime(df['expense_date'])
            total = df['amount'].sum()

            st.subheader(f"Total Spent on {category}: ₹{total:.2f}")
            st.dataframe(df[['expense_date', 'amount', 'notes']])

            st.download_button(
                label="Download as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"expenses_{category}_{start_date}_{end_date}.csv",
                mime="text/csv"
            )

            pie_data = df.groupby('notes')['amount'].sum()
            st.subheader("Pie Chart of Notes (Amount Distribution)")
            st.pyplot(pie_data.plot.pie(autopct="%1.1f%%", figsize=(5, 5), title="Notes Breakdown").get_figure())

        else:
            st.error("Failed to fetch data from server.")