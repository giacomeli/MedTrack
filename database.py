import sqlite3
from datetime import datetime

def connect():
    return sqlite3.connect('stock.db')

def create_tables():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                observation TEXT,
                date_time TEXT NOT NULL
            )
        ''')
        conn.commit()

def insert_item(name, quantity, created_at, updated_at):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (name, quantity, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (name, quantity, created_at, updated_at))
        conn.commit()

def fetch_all():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory')
        return cursor.fetchall()

def fetch_item_names():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM inventory')
        return [row[0] for row in cursor.fetchall()]

def search_items(search_text):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM inventory WHERE LOWER(name) LIKE ?', (f'%{search_text}%',))
        return cursor.fetchall()

def item_exists(name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM inventory WHERE name = ?', (name,))
        return cursor.fetchone() is not None

def delete_item(item_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        conn.commit()

def withdraw_item(name, quantity):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventory
            SET quantity = quantity - ?, updated_at = ?
            WHERE name = ? AND quantity >= ?
        ''', (quantity, datetime.now().strftime('%d/%m/%Y %H:%M:%S'), name, quantity))
        conn.commit()

def log_withdrawal(name, quantity, observation, date_time):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO withdrawals (name, quantity, observation, date_time)
            VALUES (?, ?, ?, ?)
        ''', (name, quantity, observation, date_time))
        conn.commit()