import sqlite3

DB_PATH = "db.sqlite"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # IMPORTANT (bonus question 7)
    return conn
