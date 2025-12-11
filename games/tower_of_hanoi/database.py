import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hanoi_game.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player TEXT NOT NULL,
    pegs INTEGER NOT NULL,
    disks INTEGER NOT NULL,
    moves INTEGER NOT NULL,
    optimal_moves INTEGER NOT NULL,
    time_taken REAL NOT NULL,
    algorithm_time REAL NOT NULL,
    date TEXT NOT NULL
);
"""

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()

def insert_result(player, pegs, disks, moves, optimal, time_taken, algo_time):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO results (player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (player, pegs, disks, moves, optimal, time_taken, algo_time, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, date FROM results ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_leaderboard(limit=10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT player, pegs, disks, moves, optimal_moves, time_taken, date,
               (moves - optimal_moves) AS diff
        FROM results
        ORDER BY diff ASC, time_taken ASC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()

