import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_logger


logger = setup_logger('db_helper')


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="db_host",
        user="db_user",
        password="db_password",
        database="db_name"
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    cursor.close()
    connection.close()


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expense called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def fetch_expense_summary(start_date, end_date):
    logger.info(f"fetch_expense_summary called with start: {start_date} end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, SUM(amount) as Total 
               FROM expenses WHERE expense_date
               BETWEEN %s and %s  
               GROUP BY category;''',
            (start_date, end_date)
        )
        data = cursor.fetchall()
        return data


def fetch_expenses_by_category_and_date(start_date, end_date, category):
    logger.info(f"fetch_expenses_by_category_and_date called with start: {start_date}, end: {end_date}, category: {category}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM expenses WHERE expense_date BETWEEN %s AND %s AND category = %s''',
            (start_date, end_date, category)
        )
        expenses = cursor.fetchall()
        return expenses


def fetch_expenses_by_date_range(start_date, end_date):
    logger.info(f"fetch_expenses_by_date_range called with start: {start_date}, end: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM expenses WHERE expense_date BETWEEN %s AND %s''',
            (start_date, end_date)
        )
        expenses = cursor.fetchall()
        return expenses


def fetch_all_expenses():
    logger.info("fetch_all_expenses called")
    with get_db_cursor() as cursor:
        cursor.execute('''SELECT * FROM expenses''')
        expenses = cursor.fetchall()
        return expenses


if __name__ == "__main__":
    expenses = fetch_expenses_for_date("2024-09-30")
    print(expenses)
    # delete_expenses_for_date("2024-08-25")
    summary = fetch_expense_summary("2024-08-01", "2024-08-05")
    for record in summary:
        print(record)
