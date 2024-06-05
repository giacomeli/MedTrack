import sqlite3
from datetime import datetime

def create_connection():
    conn = sqlite3.connect('stock_control.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def insert_item(item_name, quantity, created_at, updated_at):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO stock (item_name, quantity, created_at, updated_at)
    VALUES (?, ?, ?, ?)
    ''', (item_name, quantity, created_at, updated_at))
    conn.commit()
    conn.close()

def update_item(item_name, quantity, updated_at):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE stock
    SET quantity = ?, updated_at = ?
    WHERE item_name = ?
    ''', (quantity, updated_at, item_name))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM stock WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, item_name, quantity, created_at, updated_at FROM stock')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_item_names():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT item_name FROM stock')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def search_items(search_text):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, item_name, quantity, created_at, updated_at FROM stock WHERE item_name LIKE ?', ('%' + search_text + '%',))
    rows = cursor.fetchall()
    conn.close()
    return rows

create_table()
