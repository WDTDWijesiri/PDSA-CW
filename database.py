"""
Database Management Module
Handles all database operations for the game collection
"""

import sqlite3

class GameDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('game_collection.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Snake and Ladder results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snake_ladder_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                board_size INTEGER,
                correct_answer INTEGER,
                player_answer INTEGER,
                is_correct BOOLEAN,
                bfs_time REAL,
                dijkstra_time REAL,
                game_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Traffic simulation results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                max_flow INTEGER,
                player_answer INTEGER,
                is_correct BOOLEAN,
                ford_fulkerson_time REAL,
                edmonds_karp_time REAL,
                game_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # TSP results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tsp_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                home_city TEXT,
                selected_cities TEXT,
                shortest_distance REAL,
                player_answer REAL,
                is_correct BOOLEAN,
                brute_force_time REAL,
                nearest_neighbor_time REAL,
                dynamic_programming_time REAL,
                game_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Tower of Hanoi results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hanoi_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                num_disks INTEGER,
                num_pegs INTEGER,
                min_moves INTEGER,
                player_moves INTEGER,
                is_correct BOOLEAN,
                recursive_time REAL,
                iterative_time REAL,
                game_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        # Eight Queens results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queens_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                solution TEXT,
                is_unique BOOLEAN,
                sequential_time REAL,
                threaded_time REAL,
                game_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (id)
            )
        ''')
        
        self.conn.commit()
    
    def save_player_response(self, game_type, data):
        cursor = self.conn.cursor()
        
        # Insert or get player
        player_name = data.get('player_name', 'Anonymous')
        cursor.execute('INSERT OR IGNORE INTO players (name) VALUES (?)', (player_name,))
        cursor.execute('SELECT id FROM players WHERE name = ?', (player_name,))
        player_id = cursor.fetchone()[0]
        
        if game_type == 'traffic':
            cursor.execute('''
                INSERT INTO traffic_results 
                (player_id, max_flow, player_answer, is_correct, ford_fulkerson_time, edmonds_karp_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (player_id, data['max_flow'], data['player_answer'], data['is_correct'],
                  data['ford_fulkerson_time'], data['edmonds_karp_time']))
        
        elif game_type == 'snake_ladder':
            cursor.execute('''
                INSERT INTO snake_ladder_results 
                (player_id, board_size, correct_answer, player_answer, is_correct, bfs_time, dijkstra_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, data['board_size'], data['correct_answer'], data['player_answer'],
                  data['is_correct'], data['bfs_time'], data['dijkstra_time']))
        
        elif game_type == 'tsp':
            cursor.execute('''
                INSERT INTO tsp_results 
                (player_id, home_city, selected_cities, shortest_distance, player_answer, is_correct,
                 brute_force_time, nearest_neighbor_time, dynamic_programming_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, data['home_city'], data['selected_cities'], data['shortest_distance'],
                  data['player_answer'], data['is_correct'], data['brute_force_time'],
                  data['nearest_neighbor_time'], data['dynamic_programming_time']))
        
        elif game_type == 'hanoi':
            cursor.execute('''
                INSERT INTO hanoi_results 
                (player_id, num_disks, num_pegs, min_moves, player_moves, is_correct,
                 recursive_time, iterative_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, data['num_disks'], data['num_pegs'], data['min_moves'],
                  data['player_moves'], data['is_correct'], data['recursive_time'],
                  data['iterative_time']))
        
        elif game_type == 'queens':
            cursor.execute('''
                INSERT INTO queens_results 
                (player_id, solution, is_unique, sequential_time, threaded_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (player_id, data['solution'], data['is_unique'],
                  data['sequential_time'], data['threaded_time']))
        
        self.conn.commit()
    
    def close(self):
        self.conn.close()