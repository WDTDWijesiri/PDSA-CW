"""
Database Module for Tower of Hanoi Game

Handles persistence of game results using SQLite.
Best practices implemented:
- Connection context managers to ensure proper resource cleanup
- Parameterized queries to prevent SQL injection
- Single responsibility principle
"""

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
    solved INTEGER NOT NULL DEFAULT 0,
    efficiency REAL NOT NULL DEFAULT 0.0,
    date TEXT NOT NULL
);
"""

# Create index for better query performance
CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_results_player ON results(player);
"""


def get_conn():
    """
    Get a database connection.
    
    Returns:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    return conn


def init_db():
    """Initialize the database with required tables and indexes."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.executescript(CREATE_TABLE_SQL + CREATE_INDEX_SQL)
            conn.commit()
            # Ensure migration: add columns if older schema exists
            cur.execute("PRAGMA table_info(results)")
            cols = {r['name'] for r in cur.fetchall()}
            if 'solved' not in cols:
                try:
                    cur.execute("ALTER TABLE results ADD COLUMN solved INTEGER NOT NULL DEFAULT 0")
                except sqlite3.OperationalError:
                    pass
            if 'efficiency' not in cols:
                try:
                    cur.execute("ALTER TABLE results ADD COLUMN efficiency REAL NOT NULL DEFAULT 0.0")
                except sqlite3.OperationalError:
                    pass
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")


def insert_result(player, pegs, disks, moves, optimal, time_taken, algo_time, solved=0, efficiency=None):
    """
    Insert a game result into the database.
    
    Args:
        player (str): Player name
        pegs (int): Number of pegs used
        disks (int): Number of disks in the puzzle
        moves (int): Actual moves made
        optimal (int): Optimal number of moves
        time_taken (float): Time taken to solve (seconds)
        algo_time (float): Algorithm execution time (seconds)
        
    Raises:
        sqlite3.Error: If database operation fails
    """
    # Compute efficiency if not provided and if moves > 0
    try:
        if efficiency is None:
            try:
                efficiency = (optimal / moves) if moves and moves > 0 else 0.0
            except Exception:
                efficiency = 0.0

        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO results 
                   (player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, solved, efficiency, date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (player, pegs, disks, moves, optimal, time_taken, algo_time, int(bool(solved)), float(efficiency), datetime.utcnow().isoformat())
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database insert error: {e}")
        raise


def fetch_all():
    """
    Fetch all game results ordered by date (newest first).
    
    Returns:
        list: List of tuples containing game records
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, solved, efficiency, date
                   FROM results
                   ORDER BY date DESC"""
            )
            rows = cur.fetchall()
            return rows
    except sqlite3.Error as e:
        print(f"Database fetch error: {e}")
        return []


def fetch_leaderboard(limit=10):
    """
    Fetch the leaderboard: best players sorted by move efficiency then time.
    
    Args:
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of tuples with player data sorted by performance
    """
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            # Include all players but rank solved games first.
            # For solved games order by (moves - optimal) asc then time asc; unsolved get pushed below.
            cur.execute(
                """SELECT player, pegs, disks, moves, optimal_moves, time_taken, efficiency, date,
                          (moves - optimal_moves) AS diff, solved
                   FROM results
                   ORDER BY solved DESC,
                            CASE WHEN solved=1 THEN (moves - optimal_moves) ELSE 999999 END ASC,
                            time_taken ASC,
                            efficiency DESC
                   LIMIT ?""",
                (limit,)
            )
            rows = cur.fetchall()
            return rows
    except sqlite3.Error as e:
        print(f"Database fetch error: {e}")
        return []


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at: {DB_PATH}")


