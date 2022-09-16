import os
import sqlite3


def get_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "tasks.db"))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all_as_dict(query_result) -> list[dict]:
    return [dict(row) for row in query_result.fetchall()]
