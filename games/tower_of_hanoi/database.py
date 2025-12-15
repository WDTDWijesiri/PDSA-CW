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
    recursive_time REAL NOT NULL,
    iterative_time REAL NOT NULL,
    date TEXT NOT NULL,
    solved INTEGER DEFAULT 0,
    efficiency REAL DEFAULT 0.0,
    user_moves TEXT,
    actual_moves TEXT,
    is_correct INTEGER DEFAULT 0,
    efficiency_note TEXT
);
"""

CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
"""

CREATE_ALGORITHM_PERFORMANCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS algorithm_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_name TEXT NOT NULL,
    pegs INTEGER NOT NULL,
    disks INTEGER NOT NULL,
    moves_count INTEGER NOT NULL,
    execution_time REAL NOT NULL,
    move_sequence TEXT,
    is_optimal INTEGER DEFAULT 1,
    complexity_class TEXT,
    date TEXT NOT NULL
);
"""

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(CREATE_TABLE_SQL)
    cur.executescript(CREATE_USERS_TABLE_SQL)
    cur.executescript(CREATE_ALGORITHM_PERFORMANCE_TABLE_SQL)

    try:
        cur.execute("PRAGMA table_info(results)")
        existing_columns = [col[1] for col in cur.fetchall()]

        if 'recursive_time' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN recursive_time REAL DEFAULT 0.0")
        if 'iterative_time' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN iterative_time REAL DEFAULT 0.0")

        if 'algorithm_time' in existing_columns:
            pass
        
        if 'solved' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN solved INTEGER DEFAULT 0")
        if 'efficiency' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN efficiency REAL DEFAULT 0.0")
        if 'user_moves' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN user_moves TEXT")
        if 'actual_moves' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN actual_moves TEXT")
        if 'is_correct' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN is_correct INTEGER DEFAULT 0")
        if 'efficiency_note' not in existing_columns:
            cur.execute("ALTER TABLE results ADD COLUMN efficiency_note TEXT")
        
        conn.commit()
    except Exception as e:
        print(f"Migration warning: {e}")
    
    conn.close()

def insert_result(player, pegs, disks, moves, optimal, time_taken, 
                  recursive_time, iterative_time,
                  solved=0, efficiency=None, user_moves=None, actual_moves=None, 
                  is_correct=0, efficiency_note=None):
    """
    Insert a game result into the database.
    
    Args:
        player (str): Player name
        pegs (int): Number of pegs used
        disks (int): Number of disks
        moves (int): Actual moves made
        optimal (int): Optimal number of moves
        time_taken (float): Time taken to solve (seconds)
        recursive_time (float): Recursive algorithm execution time
        iterative_time (float): Iterative algorithm execution time
        solved (int): Whether puzzle was solved (0 or 1)
        efficiency (float): Efficiency ratio (optional, auto-calculated if None)
        user_moves (str): User's move sequence (e.g., "A->B, B->C")
        actual_moves (str): Optimal move sequence
        is_correct (int): Whether solution was correct (0 or 1)
        efficiency_note (str): Additional notes about efficiency
    """

    if efficiency is None and moves > 0:
        efficiency = optimal / moves
    elif efficiency is None:
        efficiency = 0.0
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO results 
        (player, pegs, disks, moves, optimal_moves, time_taken, recursive_time, iterative_time, date,
         solved, efficiency, user_moves, actual_moves, is_correct, efficiency_note) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (player, pegs, disks, moves, optimal, time_taken, recursive_time, iterative_time,
         datetime.utcnow().isoformat(), solved, efficiency, user_moves, 
         actual_moves, is_correct, efficiency_note)
    )
    conn.commit()
    conn.close()

def fetch_all():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("PRAGMA table_info(results)")
    columns = [col[1] for col in cur.fetchall()]
    
    base_cols = "player, pegs, disks, moves, optimal_moves, time_taken"

    if 'recursive_time' in columns and 'iterative_time' in columns:
        base_cols += ", recursive_time, iterative_time"
    elif 'algorithm_time' in columns:
        base_cols += ", algorithm_time"
    
    extra_cols = []
    if 'solved' in columns:
        extra_cols.append('solved')
    if 'efficiency' in columns:
        extra_cols.append('efficiency')
    if 'date' in columns:
        extra_cols.append('date')
    
    all_cols = base_cols
    if extra_cols:
        all_cols += ", " + ", ".join(extra_cols)
    
    cur.execute(f"SELECT {all_cols} FROM results ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_leaderboard(limit=10):
    conn = get_conn()
    cur = conn.cursor()
    
    # Check if solved and efficiency columns exist
    cur.execute("PRAGMA table_info(results)")
    columns = [col[1] for col in cur.fetchall()]
    
    has_solved = 'solved' in columns
    has_efficiency = 'efficiency' in columns
    
    if has_solved and has_efficiency:
        cur.execute("""
            SELECT player, pegs, disks, moves, optimal_moves, time_taken, efficiency, date,
                   (moves - optimal_moves) AS diff, solved
            FROM results
            ORDER BY solved DESC, diff ASC, time_taken ASC
            LIMIT ?
        """, (limit,))
    else:
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

def insert_user(name):
    """Insert a new user into the users table"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            (name, datetime.utcnow().isoformat())
        )
        conn.commit()
        user_id = cur.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        # User already exists
        conn.close()
        return None

def get_user(name):
    """Get user by name"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM users WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return row

def fetch_all_users():
    """Fetch all users"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM users ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def insert_algorithm_performance(algorithm_name, pegs, disks, moves_count, 
                                 execution_time, move_sequence=None, 
                                 is_optimal=1, complexity_class=None):
    """Insert algorithm performance data"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO algorithm_performance 
        (algorithm_name, pegs, disks, moves_count, execution_time, move_sequence, 
         is_optimal, complexity_class, date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (algorithm_name, pegs, disks, moves_count, execution_time, move_sequence, 
         is_optimal, complexity_class, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def fetch_algorithm_performance(limit=15):
    """Fetch algorithm performance records"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, algorithm_name, pegs, disks, moves_count, execution_time, 
               move_sequence, is_optimal, complexity_class, date 
        FROM algorithm_performance 
        ORDER BY date DESC 
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_algorithm_comparison(pegs, disks):
    """Fetch algorithm performance comparison for specific peg and disk count"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT algorithm_name, AVG(execution_time) as avg_time, 
               MIN(execution_time) as min_time, MAX(execution_time) as max_time,
               COUNT(*) as run_count
        FROM algorithm_performance 
        WHERE pegs = ? AND disks = ?
        GROUP BY algorithm_name
        ORDER BY avg_time ASC
    """, (pegs, disks))
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_performance_data():
    """Fetch performance data for comparison charts (last 15 records)"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(results)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'recursive_time' in columns and 'iterative_time' in columns:
        cur.execute("""
            SELECT disks, pegs, moves, optimal_moves, time_taken, recursive_time, iterative_time
            FROM results 
            ORDER BY id DESC 
            LIMIT 15
        """)
    else:
        cur.execute("""
            SELECT disks, pegs, moves, optimal_moves, time_taken, algorithm_time 
            FROM results 
            ORDER BY id DESC 
            LIMIT 15
        """)
    
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_algorithm_times():
    """Fetch algorithm times for report generation (last 15 records)"""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(results)")
    columns = [col[1] for col in cur.fetchall()]
    
    if 'recursive_time' in columns and 'iterative_time' in columns:
        cur.execute("""
            SELECT disks, recursive_time, iterative_time, pegs, efficiency_note 
            FROM results 
            ORDER BY id DESC 
            LIMIT 15
        """)
    elif 'algorithm_time' in columns:
        cur.execute("""
            SELECT disks, algorithm_time, pegs, efficiency_note 
            FROM results 
            ORDER BY id DESC 
            LIMIT 15
        """)
    else:
        cur.execute("""
            SELECT disks, pegs 
            FROM results 
            ORDER BY id DESC 
            LIMIT 15
        """)
    
    rows = cur.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    