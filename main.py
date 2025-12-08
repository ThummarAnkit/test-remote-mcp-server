import random
from fastmcp import FastMCP
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

# Create a FastMCP server instance
server = FastMCP("Expense-Tracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)

init_db()

@server.tool
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = "") -> dict:
    """Add a new expense to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO expenses (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
        """, (date, amount, category, subcategory, note))
        
        return {"status": "ok", "id": cur.lastrowid}
    
@server.tool
def list_expenses(start_date, end_date) -> list:
    """List recent expenses."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        """, (start_date,end_date))
        
        expenses = cur.fetchall()
        return [{"id": row[0], "date": row[1], "amount": row[2], "category": row[3], "subcategory": row[4], "note": row[5]} for row in expenses]

@server.tool
def edit_expense(expense_id: int, date: str = None, amount: float = None, category: str = None, subcategory: str = None, note: str = None) -> dict:
    """Edit an existing expense."""
    fields = []
    values = []
    
    if date is not None:
        fields.append("date = ?")
        values.append(date)
    if amount is not None:
        fields.append("amount = ?")
        values.append(amount)
    if category is not None:
        fields.append("category = ?")
        values.append(category)
    if subcategory is not None:
        fields.append("subcategory = ?")
        values.append(subcategory)
    if note is not None:
        fields.append("note = ?")
        values.append(note)
    
    values.append(expense_id)
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f"""
            UPDATE expenses
            SET {', '.join(fields)}
            WHERE id = ?
        """, values)
        
        return {"status": "ok"}
    
@server.tool
def summarize_expenses(start_date: str, end_date: str, category: str = None) -> dict:
    """Summarize expenses by category."""
    query = """
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE date BETWEEN ? AND ?
    """
    params = [start_date, end_date]

    if category:
        query += " AND category = ?"
        params.append(category)
        
    query += " GROUP BY category ORDER BY category ASC"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(query, params)
        summary = cur.fetchall()
        return {row[0]: row[1] for row in summary}

@server.resource("expense://categories", mime_type="application/json")
def categories():
    """Serve the categories JSON file."""
    with open(CATEGORIES_PATH, "r", encoding='utf-8') as f:
        return f.read()

# Start the server
if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)