import sqlite3
from datetime import datetime

DB_NAME = "bharatbiz.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            customer_name TEXT,
            amount INTEGER,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_invoice(invoice_id, customer_name, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO invoices (invoice_id, customer_name, amount, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        invoice_id,
        customer_name,
        amount,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(amount) FROM invoices")
    count, total = cursor.fetchone()

    conn.close()

    return count or 0, total or 0


def get_last_invoice():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT invoice_id, customer_name, amount, created_at
        FROM invoices
        ORDER BY id DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()
    return result
