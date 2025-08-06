from fastapi import FastAPI, HTTPException
from datetime import date
import db_helper
from typing import List, Any
from pydantic import BaseModel

app = FastAPI()

class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date

class CategoryRequest(BaseModel):
    start_date: date
    end_date: date
    category: str

@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses from the database.")
    return expenses

@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: List[Expense]):
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)
    return {"message": "Expenses updated successfully"}

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

@app.post("/category-expenses/")
def get_expenses_by_category_and_date(request: CategoryRequest):
    expenses = db_helper.fetch_expenses_by_category_and_date(
        request.start_date, request.end_date, request.category
    )
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses for category and date range.")
    return expenses

@app.get("/all-expenses/")
def get_all_expenses():
    expenses = db_helper.fetch_all_expenses()
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve all expenses.")
    return expenses

@app.post("/all-expenses/")
def get_all_expenses(date_range: DateRange) -> Any:
    expenses = db_helper.fetch_expenses_by_date_range(date_range.start_date, date_range.end_date)
    if expenses is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve expenses for date range.")
    return expenses
