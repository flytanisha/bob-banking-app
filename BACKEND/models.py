"""
models.py — all database interactions.

No SQL is written outside this module.

Tables
------
customers : id INTEGER PK, username TEXT UNIQUE, password_hash TEXT
accounts  : id INTEGER PK, customer_id INTEGER FK, balance REAL
"""
import sqlite3
from werkzeug.security import generate_password_hash
import config


def get_db_connection():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


_CREATE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS customers (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL
    );

    CREATE TABLE IF NOT EXISTS accounts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        balance     REAL    NOT NULL DEFAULT 0.0
    );
"""


def init_db(conn=None):
    _own = conn is None
    if _own:
        conn = get_db_connection()
    try:
        conn.executescript(_CREATE_SCHEMA)
        conn.commit()
    finally:
        if _own:
            conn.close()


_SEED_CUSTOMERS = [
    ("alice", "password123", 1000.00),
    ("bob",   "password456",  500.00),
]


def seed_db(conn=None):
    _own = conn is None
    if _own:
        conn = get_db_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM customers").fetchone()
        if row["cnt"] > 0:
            return
        for username, password, starting_balance in _SEED_CUSTOMERS:
            pw_hash = generate_password_hash(password)
            cursor = conn.execute(
                "INSERT INTO customers (username, password_hash) VALUES (?, ?)",
                (username, pw_hash),
            )
            customer_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO accounts (customer_id, balance) VALUES (?, ?)",
                (customer_id, starting_balance),
            )
        conn.commit()
    finally:
        if _own:
            conn.close()


def get_customer_by_username(username, conn=None):
    _own = conn is None
    if _own:
        conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM customers WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        if _own:
            conn.close()


def get_account_by_customer_id(customer_id, conn=None):
    _own = conn is None
    if _own:
        conn = get_db_connection()
    try:
        return conn.execute(
            "SELECT * FROM accounts WHERE customer_id = ?",
            (customer_id,),
        ).fetchone()
    finally:
        if _own:
            conn.close()


def update_balance(account_id, new_balance, conn=None):
    _own = conn is None
    if _own:
        conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, account_id),
        )
        conn.commit()
    finally:
        if _own:
            conn.close()
