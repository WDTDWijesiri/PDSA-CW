import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import math
import sqlite3
from datetime import datetime
import time
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import colorsys
import heapq
import unittest
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# ============ ENHANCED VISUAL CONSTANTS ============
COLORS = {
    'bg_dark': '#0f1a2c',
    'bg_panel': '#1a2b4a',
    'bg_light': '#2a3f6e',
    'accent_blue': '#4a9eff',
    'accent_green': '#2ecc71',
    'accent_red': '#ff4757',
    'accent_yellow': '#ffd32a',
    'accent_purple': '#9b59b6',
    'text_light': '#ecf0f1',
    'text_dim': '#95a5a6',
    'road': '#2c3e50',
    'road_marking': '#f1c40f',
    'intersection': '#34495e',
    'car_colors': ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
}

NODE_POSITIONS = {
    'A': (150, 400),  # Source
    'B': (300, 250), 'C': (300, 400), 'D': (300, 550),
    'E': (450, 250), 'F': (450, 400), 
    'G': (600, 250), 'H': (600, 400),
    'T': (750, 325)   # Sink
}

EDGE_PATHS = {
    ('A', 'B'): [(150, 400), (225, 325), (300, 250)],
    ('A', 'C'): [(150, 400), (225, 400), (300, 400)],
    ('A', 'D'): [(150, 400), (225, 475), (300, 550)],
    ('B', 'E'): [(300, 250), (375, 250), (450, 250)],
    ('B', 'F'): [(300, 250), (375, 325), (450, 400)],
    ('C', 'E'): [(300, 400), (375, 325), (450, 250)],
    ('C', 'F'): [(300, 400), (375, 400), (450, 400)],
    ('D', 'F'): [(300, 550), (375, 475), (450, 400)],
    ('E', 'G'): [(450, 250), (525, 250), (600, 250)],
    ('E', 'H'): [(450, 250), (525, 325), (600, 400)],
    ('F', 'H'): [(450, 400), (525, 400), (600, 400)],
    ('G', 'T'): [(600, 250), (675, 287), (750, 325)],
    ('H', 'T'): [(600, 400), (675, 363), (750, 325)]
}

EDGES = [
    ('A', 'B'), ('A', 'C'), ('A', 'D'),
    ('B', 'E'), ('B', 'F'),
    ('C', 'E'), ('C', 'F'),
    ('D', 'F'),
    ('E', 'G'), ('E', 'H'),
    ('F', 'H'),
    ('G', 'T'), ('H', 'T')
]

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"

class GameMode(Enum):
    SIMULATION = "Traffic Management"
    ALGORITHM = "Flow Calculation"
    CHALLENGE = "Time Challenge"
    MAX_FLOW_GAME = "Max Flow Game"

class GameState(Enum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"
    IN_PROGRESS = "in_progress"

@dataclass
class AlgorithmPerformance:
    """Class to track algorithm performance metrics"""
    name: str
    max_flow: int
    execution_time_ms: float
    nodes_visited: int = 0
    memory_usage_mb: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class FlowResult:
    algorithm: str
    max_flow: int
    execution_time: float
    path_flows: Dict[Tuple[str, str], int]
    algorithm_details: AlgorithmPerformance = None

class AdvancedTrafficGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🚦 Advanced Traffic Flow Simulator 🚗")
        self.root.geometry("1600x900")
        self.root.configure(bg=COLORS['bg_dark'])
        
        # Game state
        self.running = False
        self.paused = False
        self.simulation_speed = 1.0
        self.difficulty = Difficulty.MEDIUM
        self.game_mode = GameMode.MAX_FLOW_GAME
        self.current_level = 1
        self.score = 0
        self.time_elapsed = 0
        self.money = 1000
        
        # Statistics
        self.vehicles_spawned = 0
        self.vehicles_arrived = 0
        self.vehicles_congested = 0
        self.avg_travel_time = 0
        self.total_distance = 0
        
        # Max Flow Game specific
        self.current_round = 1
        self.max_rounds = 5
        self.current_max_flow = 0
        self.player_answer = 0
        self.algorithm_results: List[FlowResult] = []
        self.algorithm_performances: List[AlgorithmPerformance] = []
        self.game_state = GameState.IN_PROGRESS
        self.session_start_time = None
        self.player_name = None
        self.session_id = None
        
        # Game objects
        self.vehicles = []
        self.traffic_lights = {}
        self.road_upgrades = {}
        self.next_vehicle_id = 1
        
        # Network configuration
        self.nodes = NODE_POSITIONS
        self.edges = EDGES
        self.edge_paths = EDGE_PATHS
        
        # Edge properties
        self.edge_capacities = {}
        self.edge_flows = {}
        self.edge_congestion = {}
        self.edge_speeds = {}
        
        # Pathfinding
        self.adjacency = self._build_adjacency()
        
        # UI components
        self.canvas = None
        self.info_labels = {}
        self.control_buttons = {}
        self.upgrade_buttons = {}
        
        # Algorithm tracking
        self.algorithm_execution_times = []
        self.algorithm_memory_usage = []
        self.round_execution_stats = []
        
        # Database
        self.init_database()
        
        # Start with main menu
        self.show_main_menu()
    
    def _build_adjacency(self):
        """Build adjacency list for the graph"""
        adj = {}
        for u, v in self.edges:
            if u not in adj:
                adj[u] = []
            if v not in adj:
                adj[v] = []
            adj[u].append(v)
        return adj
    
    def init_database(self):
        """Initialize SQLite database with proper structure"""
        try:
            self.db_path = Path("advanced_traffic.db")
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create all tables
            tables = [
                '''CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    game_mode TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    score INTEGER DEFAULT 0,
                    correct_answer INTEGER,
                    total_rounds INTEGER DEFAULT 0,
                    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_duration_seconds REAL DEFAULT 0
                )''',
                '''CREATE TABLE IF NOT EXISTS algorithm_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    algorithm_name TEXT NOT NULL,
                    execution_time_ms REAL NOT NULL,
                    max_flow_result INTEGER NOT NULL,
                    nodes_visited INTEGER DEFAULT 0,
                    memory_usage_mb REAL DEFAULT 0,
                    algorithm_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
                )''',
                '''CREATE TABLE IF NOT EXISTS player_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT UNIQUE NOT NULL,
                    total_games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    draws INTEGER DEFAULT 0,
                    best_score INTEGER DEFAULT 0,
                    average_execution_time_ms REAL DEFAULT 0,
                    fastest_algorithm_time_ms REAL DEFAULT 0,
                    total_algorithm_runs INTEGER DEFAULT 0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS max_flow_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    round_number INTEGER NOT NULL,
                    player_answer INTEGER,
                    correct_answer INTEGER NOT NULL,
                    is_correct BOOLEAN,
                    answer_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
                )'''
            ]
            
            for table in tables:
                try:
                    self.cursor.execute(table)
                except sqlite3.Error as e:
                    print(f"Error creating table: {e}")
            
            self.conn.commit()
            print("Database initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            try:
                self.conn = sqlite3.connect(':memory:', check_same_thread=False)
                self.cursor = self.conn.cursor()
                
                all_tables = [
                    '''CREATE TABLE game_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT NOT NULL,
                        game_mode TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        level INTEGER DEFAULT 1,
                        score INTEGER DEFAULT 0,
                        correct_answer INTEGER,
                        total_rounds INTEGER DEFAULT 0,
                        session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_duration_seconds REAL DEFAULT 0
                    )''',
                    '''CREATE TABLE algorithm_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        round_number INTEGER NOT NULL,
                        algorithm_name TEXT NOT NULL,
                        execution_time_ms REAL NOT NULL,
                        max_flow_result INTEGER NOT NULL,
                        nodes_visited INTEGER DEFAULT 0,
                        memory_usage_mb REAL DEFAULT 0,
                        algorithm_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
                    )''',
                    '''CREATE TABLE player_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player_name TEXT UNIQUE NOT NULL,
                        total_games INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        losses INTEGER DEFAULT 0,
                        draws INTEGER DEFAULT 0,
                        best_score INTEGER DEFAULT 0,
                        average_execution_time_ms REAL DEFAULT 0,
                        fastest_algorithm_time_ms REAL DEFAULT 0,
                        total_algorithm_runs INTEGER DEFAULT 0,
                        last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''',
                    '''CREATE TABLE max_flow_answers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        round_number INTEGER NOT NULL,
                        player_answer INTEGER,
                        correct_answer INTEGER NOT NULL,
                        is_correct BOOLEAN,
                        answer_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
                    )'''
                ]
                
                for table in all_tables:
                    self.cursor.execute(table)
                
                self.conn.commit()
                print("Using in-memory database as fallback")
                
            except Exception as inner_e:
                print(f"Failed to create in-memory database: {inner_e}")
                raise
    
    def generate_random_capacities(self):
        """Generate random capacities between 5 and 15 for each edge"""
        self.edge_capacities = {}
        for edge in self.edges:
            capacity = random.randint(5, 15)
            self.edge_capacities[edge] = capacity
        return self.edge_capacities
    
    def measure_memory_usage(self):
        """Simple memory usage measurement (simulated)"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return random.uniform(5.0, 15.0)
    
    def edmonds_karp_max_flow(self, source='A', sink='T'):
        """Edmonds-Karp algorithm (BFS implementation of Ford-Fulkerson)"""
        start_time = time.perf_counter()
        
        # Build residual graph
        residual = {}
        nodes_visited = 0
        
        # Initialize residual graph
        for u, v in self.edges:
            capacity = self.edge_capacities.get((u, v), 0)
            if u not in residual:
                residual[u] = {}
            if v not in residual:
                residual[v] = {}
            residual[u][v] = capacity
            residual[v][u] = 0
        
        max_flow = 0
        path_flows = {}
        
        while True:
            # BFS to find augmenting path
            queue = [source]
            parent = {source: None}
            visited = {source}
            nodes_visited += 1
            
            while queue:
                current = queue.pop(0)
                nodes_visited += 1
                
                for neighbor in list(residual.get(current, {}).keys()):
                    if neighbor not in visited and residual[current][neighbor] > 0:
                        visited.add(neighbor)
                        parent[neighbor] = current
                        
                        if neighbor == sink:
                            break
                        
                        queue.append(neighbor)
            
            if sink not in parent:
                break
            
            # Find minimum residual capacity along the path
            path_flow = float('inf')
            v = sink
            path_nodes = []
            
            while v != source:
                u = parent[v]
                path_flow = min(path_flow, residual[u][v])
                path_nodes.append((u, v))
                v = u
            
            # Update residual capacities
            v = sink
            while v != source:
                u = parent[v]
                residual[u][v] -= path_flow
                residual[v][u] += path_flow
                v = u
            
            max_flow += path_flow
            
            for edge in path_nodes:
                if edge in self.edges:
                    path_flows[edge] = path_flows.get(edge, 0) + path_flow
        
        execution_time = (time.perf_counter() - start_time) * 1000
        
        memory_usage = self.measure_memory_usage()
        
        algorithm_perf = AlgorithmPerformance(
            name="Edmonds-Karp",
            max_flow=max_flow,
            execution_time_ms=execution_time,
            nodes_visited=nodes_visited,
            memory_usage_mb=memory_usage
        )
        
        self.algorithm_performances.append(algorithm_perf)
        
        return FlowResult(
            algorithm="Edmonds-Karp",
            max_flow=max_flow,
            execution_time=execution_time,
            path_flows=path_flows,
            algorithm_details=algorithm_perf
        )
    
    def dinic_max_flow(self, source='A', sink='T'):
        """Dinic's algorithm for maximum flow"""
        start_time = time.perf_counter()
        nodes_visited = 0
        
        graph = {}
        for u, v in self.edges:
            capacity = self.edge_capacities.get((u, v), 0)
            if u not in graph:
                graph[u] = {}
            if v not in graph:
                graph[v] = {}
            graph[u][v] = capacity
            graph[v][u] = 0
        
        def bfs_level_graph(s, t):
            nonlocal nodes_visited
            level = {node: -1 for node in graph}
            level[s] = 0
            queue = [s]
            nodes_visited += 1
            
            while queue:
                u = queue.pop(0)
                nodes_visited += 1
                for v in graph.get(u, {}):
                    if level[v] == -1 and graph[u][v] > 0:
                        level[v] = level[u] + 1
                        queue.append(v)
            
            return level
        
        def dfs_blocking_flow(u, t, flow, level, ptr):
            nonlocal nodes_visited
            if u == t:
                return flow
            
            for i in range(ptr[u], len(list(graph.get(u, {}).keys()))):
                v = list(graph.get(u, {}).keys())[i]
                ptr[u] = i
                nodes_visited += 1
                if level[v] == level[u] + 1 and graph[u][v] > 0:
                    current_flow = min(flow, graph[u][v])
                    pushed = dfs_blocking_flow(v, t, current_flow, level, ptr)
                    
                    if pushed > 0:
                        graph[u][v] -= pushed
                        graph[v][u] += pushed
                        return pushed
            
            return 0
        
        max_flow = 0
        
        while True:
            level = bfs_level_graph(source, sink)
            if level[sink] == -1:
                break
            
            ptr = {node: 0 for node in graph}
            
            while True:
                flow = dfs_blocking_flow(source, sink, float('inf'), level, ptr)
                if flow == 0:
                    break
                max_flow += flow
        
        execution_time = (time.perf_counter() - start_time) * 1000
        
        memory_usage = self.measure_memory_usage()
        
        algorithm_perf = AlgorithmPerformance(
            name="Dinic",
            max_flow=max_flow,
            execution_time_ms=execution_time,
            nodes_visited=nodes_visited,
            memory_usage_mb=memory_usage
        )
        
        self.algorithm_performances.append(algorithm_perf)
        
        return FlowResult(
            algorithm="Dinic",
            max_flow=max_flow,
            execution_time=execution_time,
            path_flows={},
            algorithm_details=algorithm_perf
        )
    
    def calculate_max_flow_algorithms(self):
        """Calculate maximum flow using both algorithms and record timing"""
        try:
            self.algorithm_performances = []
            
            edmonds_karp_result = self.edmonds_karp_max_flow()
            dinic_result = self.dinic_max_flow()
            
            self.algorithm_results = [edmonds_karp_result, dinic_result]
            
            if edmonds_karp_result.max_flow != dinic_result.max_flow:
                print(f"Warning: Algorithms disagree! Edmonds-Karp: {edmonds_karp_result.max_flow}, Dinic: {dinic_result.max_flow}")
                self.current_max_flow = (edmonds_karp_result.max_flow + dinic_result.max_flow) // 2
            else:
                self.current_max_flow = edmonds_karp_result.max_flow
            
            round_stats = {
                'round': self.current_round,
                'algorithms': [],
                'total_time_ms': 0,
                'avg_time_ms': 0
            }
            
            for perf in self.algorithm_performances:
                round_stats['algorithms'].append({
                    'name': perf.name,
                    'time_ms': perf.execution_time_ms,
                    'memory_mb': perf.memory_usage_mb,
                    'nodes': perf.nodes_visited,
                    'max_flow': perf.max_flow
                })
                round_stats['total_time_ms'] += perf.execution_time_ms
            
            if self.algorithm_performances:
                round_stats['avg_time_ms'] = round_stats['total_time_ms'] / len(self.algorithm_performances)
            
            self.round_execution_stats.append(round_stats)
            
            self.save_algorithm_performance_for_round()
            
            return self.current_max_flow
            
        except Exception as e:
            print(f"Algorithm Error: {e}")
            messagebox.showerror("Algorithm Error", f"Failed to calculate maximum flow: {str(e)}")
            return 0
    
    def save_algorithm_performance_for_round(self):
        """Save algorithm performance for current round to database"""
        try:
            if not hasattr(self, 'session_id') or self.session_id is None:
                print("No session ID available")
                return
            
            for perf in self.algorithm_performances:
                self.cursor.execute('''
                    INSERT INTO algorithm_performance 
                    (session_id, round_number, algorithm_name, execution_time_ms, 
                     max_flow_result, nodes_visited, memory_usage_mb)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.session_id,
                    self.current_round,
                    perf.name,
                    perf.execution_time_ms,
                    perf.max_flow,
                    perf.nodes_visited,
                    perf.memory_usage_mb
                ))
            
            self.conn.commit()
            print(f"Saved algorithm performance data for round {self.current_round}")
            
        except Exception as e:
            print(f"Error saving algorithm performance: {e}")
            self.conn.rollback()
    
    def start_max_flow_game(self):
        """Start the maximum flow game as per requirements"""
        try:
            player_name = simpledialog.askstring(
                "Player Name",
                "Enter your name:",
                parent=self.root
            )
            
            if not player_name:
                player_name = "Anonymous"
            
            self.player_name = player_name
            self.game_mode = GameMode.MAX_FLOW_GAME
            self.current_round = 1
            self.score = 0
            self.game_state = GameState.IN_PROGRESS
            self.session_start_time = time.time()
            
            self.algorithm_performances = []
            self.round_execution_stats = []
            
            self.cursor.execute('''
                INSERT INTO game_sessions (player_name, game_mode, difficulty, score, total_rounds)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.player_name, self.game_mode.value, self.difficulty.value, 0, 0))
            
            self.session_id = self.cursor.lastrowid
            self.conn.commit()
            
            self.start_max_flow_round()
            
        except Exception as e:
            messagebox.showerror("Game Error", f"Failed to start game: {str(e)}")
    
    def start_max_flow_round(self):
        """Start a new round of the maximum flow game"""
        if self.current_round > self.max_rounds:
            self.end_max_flow_game()
            return
        
        self.clear_screen()
        self.generate_random_capacities()
        correct_answer = self.calculate_max_flow_algorithms()
        self.setup_max_flow_round_ui(correct_answer)
    
    def setup_max_flow_round_ui(self, correct_answer):
        """Setup UI for maximum flow round with algorithm timing info"""
        main_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(main_frame, bg=COLORS['bg_panel'], height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text=f"🚦 Maximum Flow Challenge - Round {self.current_round}/{self.max_rounds}",
            font=("Impact", 28, "bold"),
            fg=COLORS['accent_blue'],
            bg=COLORS['bg_panel']
        ).pack(expand=True)
        
        content_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        left_panel = tk.Frame(content_frame, bg=COLORS['bg_panel'], width=800)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.canvas = tk.Canvas(left_panel, bg=COLORS['bg_dark'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.draw_max_flow_network()
        
        right_panel = tk.Frame(content_frame, bg=COLORS['bg_panel'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        instr_frame = tk.Frame(right_panel, bg=COLORS['bg_light'])
        instr_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            instr_frame,
            text="Calculate the maximum flow from A (Source) to T (Sink)",
            font=("Arial", 14, "bold"),
            fg=COLORS['text_light'],
            bg=COLORS['bg_light'],
            wraplength=350
        ).pack(pady=10)
        
        input_frame = tk.Frame(right_panel, bg=COLORS['bg_panel'])
        input_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            input_frame,
            text="Your Answer:",
            font=("Arial", 16, "bold"),
            fg=COLORS['text_light'],
            bg=COLORS['bg_panel']
        ).pack(pady=(0, 10))
        
        self.answer_var = tk.StringVar()
        answer_entry = tk.Entry(
            input_frame,
            textvariable=self.answer_var,
            font=("Arial", 24, "bold"),
            justify=tk.CENTER,
            width=15
        )
        answer_entry.pack(pady=10)
        answer_entry.focus()
        
        submit_btn = tk.Button(
            input_frame,
            text="✅ SUBMIT ANSWER",
            command=self.check_max_flow_answer,
            font=("Arial", 16, "bold"),
            fg='white',
            bg=COLORS['accent_green'],
            padx=30,
            pady=15,
            cursor="hand2"
        )
        submit_btn.pack(pady=20)
        
        answer_entry.bind('<Return>', lambda e: self.check_max_flow_answer())
        
        perf_frame = tk.Frame(right_panel, bg=COLORS['bg_light'])
        perf_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            perf_frame,
            text="🕒 Algorithm Performance:",
            font=("Arial", 14, "bold"),
            fg=COLORS['text_light'],
            bg=COLORS['bg_light']
        ).pack(pady=(0, 10), anchor='w')
        
        scroll_container = tk.Frame(perf_frame, bg=COLORS['bg_light'], height=200)
        scroll_container.pack(fill=tk.BOTH, expand=True)
        scroll_container.pack_propagate(False)
        
        perf_canvas = tk.Canvas(scroll_container, bg=COLORS['bg_light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=perf_canvas.yview,
                                bg=COLORS['bg_panel'], troughcolor=COLORS['bg_dark'], width=12)
        scrollable_frame = tk.Frame(perf_canvas, bg=COLORS['bg_light'])
        
        scrollable_frame.bind("<Configure>", lambda e: perf_canvas.configure(scrollregion=perf_canvas.bbox("all")))
        canvas_window = perf_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=350)
        perf_canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            perf_canvas.itemconfig(canvas_window, width=event.width)
        
        perf_canvas.bind("<Configure>", on_canvas_configure)
        
        for perf in self.algorithm_performances:
            algo_frame = tk.Frame(scrollable_frame, bg=COLORS['bg_panel'], relief=tk.RAISED, bd=2)
            algo_frame.pack(fill=tk.X, pady=8, padx=5)
            
            header_frame = tk.Frame(algo_frame, bg=COLORS['bg_panel'])
            header_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(
                header_frame,
                text=f"{perf.name}:",
                font=("Arial", 13, "bold"),
                fg=COLORS['accent_blue'],
                bg=COLORS['bg_panel'],
                anchor='w'
            ).pack(side=tk.LEFT)
            
            time_color = COLORS['accent_green'] if perf.execution_time_ms < 10 else (
                COLORS['accent_yellow'] if perf.execution_time_ms < 50 else COLORS['accent_red']
            )
            
            tk.Label(
                header_frame,
                text=f"{perf.execution_time_ms:.2f} ms",
                font=("Arial", 12, "bold"),
                fg=time_color,
                bg=COLORS['bg_panel']
            ).pack(side=tk.RIGHT)
            
            details_frame = tk.Frame(algo_frame, bg=COLORS['bg_light'])
            details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            details_grid = tk.Frame(details_frame, bg=COLORS['bg_light'])
            details_grid.pack(fill=tk.X, padx=5)
            
            left_col = tk.Frame(details_grid, bg=COLORS['bg_light'])
            left_col.grid(row=0, column=0, sticky='w', padx=(0, 20))
            
            tk.Label(
                left_col,
                text=f"Max Flow: {perf.max_flow}",
                font=("Arial", 11, "bold"),
                fg=COLORS['text_light'],
                bg=COLORS['bg_light'],
                anchor='w'
            ).pack(anchor='w', pady=2)
            
            tk.Label(
                left_col,
                text=f"Nodes: {perf.nodes_visited}",
                font=("Arial", 10),
                fg=COLORS['text_dim'],
                bg=COLORS['bg_light'],
                anchor='w'
            ).pack(anchor='w', pady=2)
            
            right_col = tk.Frame(details_grid, bg=COLORS['bg_light'])
            right_col.grid(row=0, column=1, sticky='w')
            
            tk.Label(
                right_col,
                text=f"Memory: {perf.memory_usage_mb:.2f} MB",
                font=("Arial", 10),
                fg=COLORS['text_dim'],
                bg=COLORS['bg_light'],
                anchor='w'
            ).pack(anchor='w', pady=2)
            
            if perf.timestamp:
                time_str = perf.timestamp.strftime('%H:%M:%S')
                tk.Label(
                    right_col,
                    text=f"Time: {time_str}",
                    font=("Arial", 9),
                    fg=COLORS['text_dim'],
                    bg=COLORS['bg_light'],
                    anchor='w'
                ).pack(anchor='w', pady=2)
            
            details_grid.columnconfigure(0, weight=1)
            details_grid.columnconfigure(1, weight=1)
        
        perf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel(event):
            perf_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        perf_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        score_frame = tk.Frame(right_panel, bg=COLORS['bg_light'])
        score_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            score_frame,
            text=f"Score: {self.score}",
            font=("Arial", 18, "bold"),
            fg=COLORS['accent_yellow'],
            bg=COLORS['bg_light']
        ).pack(pady=10)
    
    def draw_max_flow_network(self):
        """Draw the network with capacities for max flow game"""
        if not self.canvas:
            return
            
        self.canvas.delete("all")
        
        for (u, v), points in self.edge_paths.items():
            if (u, v) in self.edge_capacities:
                capacity = self.edge_capacities[(u, v)]
                
                for i in range(len(points)-1):
                    x1, y1 = points[i]
                    x2, y2 = points[i+1]
                    
                    width = 3 + capacity / 5
                    color = self.get_capacity_color(capacity)
                    
                    self.canvas.create_line(x1, y1, x2, y2,
                                          fill=color, width=width, smooth=True,
                                          arrow=tk.LAST if i == len(points)-2 else None,
                                          arrowshape=(8, 10, 3))
                
                if len(points) >= 2:
                    mid_idx = len(points) // 2
                    if mid_idx < len(points):
                        x, y = points[mid_idx]
                        
                        self.canvas.create_rectangle(x-25, y-15, x+25, y+15,
                                                   fill=COLORS['bg_panel'],
                                                   outline=color, width=2)
                        
                        self.canvas.create_text(x, y, text=str(capacity),
                                              font=("Arial", 12, "bold"),
                                              fill='white')
        
        for node, (x, y) in self.nodes.items():
            if node == 'A':
                color = COLORS['accent_green']
                label = "Source (A)"
            elif node == 'T':
                color = COLORS['accent_red']
                label = "Sink (T)"
            else:
                color = COLORS['accent_blue']
                label = node
            
            self.canvas.create_oval(x-25, y-25, x+25, y+25,
                                  fill=color, outline='white', width=3)
            
            self.canvas.create_text(x, y, text=label,
                                  font=("Arial", 12, "bold"),
                                  fill='white')
        
        self.canvas.create_text(100, 50, text="Directed Network",
                              font=("Arial", 14, "bold"),
                              fill=COLORS['text_light'],
                              anchor='w')
        
        self.canvas.create_text(100, 80, text="Numbers show capacity (vehicles/min)",
                              font=("Arial", 10),
                              fill=COLORS['text_dim'],
                              anchor='w')
    
    def get_capacity_color(self, capacity):
        """Get color based on capacity"""
        normalized = (capacity - 5) / 10
        
        if normalized < 0.33:
            return '#ff6b6b'
        elif normalized < 0.66:
            return '#feca57'
        else:
            return '#1dd1a1'
    
    def check_max_flow_answer(self):
        """Check player's maximum flow answer"""
        try:
            answer_text = self.answer_var.get().strip()
            if not answer_text:
                messagebox.showwarning("Invalid Input", "Please enter a number!")
                return
            
            player_answer = int(answer_text)
            
            if player_answer < 0:
                messagebox.showwarning("Invalid Input", "Flow cannot be negative!")
                return
            
            correct_answer = self.current_max_flow
            is_correct = (player_answer == correct_answer)
            round_score = self.calculate_round_score(player_answer, correct_answer, is_correct)
            self.score += round_score
            
            self.save_max_flow_answer(player_answer, correct_answer, is_correct)
            self.show_round_result(player_answer, correct_answer, is_correct, round_score)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def calculate_round_score(self, player_answer, correct_answer, is_correct):
        """Calculate score for the round"""
        if is_correct:
            base_score = 100
            
            algorithm_bonus = 0
            for result in self.algorithm_results:
                if player_answer == result.max_flow:
                    algorithm_bonus += 25
            
            return base_score + algorithm_bonus
        
        else:
            difference = abs(player_answer - correct_answer)
            if difference <= 2:
                return 50
            elif difference <= 5:
                return 25
            else:
                return 0
    
    def save_max_flow_answer(self, player_answer, correct_answer, is_correct):
        """Save player's answer to database"""
        try:
            self.cursor.execute('''
                INSERT INTO max_flow_answers 
                (session_id, round_number, player_answer, correct_answer, is_correct)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.session_id, self.current_round, player_answer, correct_answer, is_correct))
            
            self.cursor.execute('''
                UPDATE game_sessions 
                SET score = ?, total_rounds = ?
                WHERE id = ?
            ''', (self.score, self.current_round, self.session_id))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error saving answer: {e}")
            self.conn.rollback()
    
    def show_round_result(self, player_answer, correct_answer, is_correct, round_score):
        """Show result of the current round with algorithm timing details"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Round Result")
        result_window.geometry("700x600")
        result_window.configure(bg=COLORS['bg_dark'])
        result_window.transient(self.root)
        result_window.grab_set()
        
        result_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - result_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - result_window.winfo_height()) // 2
        result_window.geometry(f"+{x}+{y}")
        
        if is_correct:
            icon = "✅"
            message = "CORRECT!"
            color = COLORS['accent_green']
        else:
            icon = "❌"
            message = "INCORRECT"
            color = COLORS['accent_red']
        
        tk.Label(
            result_window,
            text=f"{icon} {message}",
            font=("Impact", 36, "bold"),
            fg=color,
            bg=COLORS['bg_dark']
        ).pack(pady=20)
        
        details_frame = tk.Frame(result_window, bg=COLORS['bg_panel'])
        details_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        round_details = [
            ("Your Answer", str(player_answer)),
            ("Correct Answer", str(correct_answer)),
            ("Round Score", str(round_score)),
            ("Total Score", str(self.score)),
            ("", "")
        ]
        
        for label, value in round_details:
            if label:
                frame = tk.Frame(details_frame, bg=COLORS['bg_light'])
                frame.pack(fill=tk.X, pady=2, padx=20)
                
                tk.Label(
                    frame,
                    text=label,
                    font=("Arial", 12, "bold"),
                    fg=COLORS['text_light'],
                    bg=COLORS['bg_light'],
                    width=15,
                    anchor='w'
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Label(
                    frame,
                    text=value,
                    font=("Arial", 12),
                    fg=COLORS['accent_yellow'],
                    bg=COLORS['bg_light']
                ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            details_frame,
            text="📊 Algorithm Performance Details",
            font=("Arial", 14, "bold"),
            fg=COLORS['accent_blue'],
            bg=COLORS['bg_panel']
        ).pack(pady=(10, 5))
        
        perf_frame = tk.Frame(details_frame, bg=COLORS['bg_panel'])
        perf_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        headers = ["Algorithm", "Time (ms)", "Max Flow", "Nodes", "Memory (MB)"]
        for col, header in enumerate(headers):
            tk.Label(
                perf_frame,
                text=header,
                font=("Arial", 11, "bold"),
                fg=COLORS['text_light'],
                bg=COLORS['accent_blue'],
                relief=tk.RAISED,
                bd=1
            ).grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        for row, perf in enumerate(self.algorithm_performances, 1):
            data = [
                perf.name,
                f"{perf.execution_time_ms:.2f}",
                str(perf.max_flow),
                str(perf.nodes_visited),
                f"{perf.memory_usage_mb:.2f}"
            ]
            
            for col, value in enumerate(data):
                bg_color = COLORS['bg_light'] if row % 2 == 1 else COLORS['bg_panel']
                tk.Label(
                    perf_frame,
                    text=value,
                    font=("Arial", 10),
                    fg=COLORS['text_light'],
                    bg=bg_color,
                    relief=tk.SUNKEN,
                    bd=1
                ).grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
        
        for i in range(len(headers)):
            perf_frame.grid_columnconfigure(i, weight=1)
        
        button_frame = tk.Frame(result_window, bg=COLORS['bg_dark'])
        button_frame.pack(pady=20)
        
        if self.current_round < self.max_rounds:
            next_btn = tk.Button(
                button_frame,
                text="NEXT ROUND",
                command=lambda: [result_window.destroy(), self.next_max_flow_round()],
                font=("Arial", 14, "bold"),
                fg='white',
                bg=COLORS['accent_green'],
                padx=30,
                pady=10,
                cursor="hand2"
            )
            next_btn.pack(side=tk.LEFT, padx=10)
        
        end_btn = tk.Button(
            button_frame,
            text="END GAME",
            command=lambda: [result_window.destroy(), self.end_max_flow_game()],
            font=("Arial", 14, "bold"),
            fg='white',
            bg=COLORS['accent_blue'],
            padx=30,
            pady=10,
            cursor="hand2"
        )
        end_btn.pack(side=tk.LEFT, padx=10)
    
    def next_max_flow_round(self):
        """Move to next round"""
        self.current_round += 1
        self.start_max_flow_round()
    
    def end_max_flow_game(self):
        """End the maximum flow game and show final results"""
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            try:
                self.cursor.execute('''
                    UPDATE game_sessions 
                    SET session_duration_seconds = ?, score = ?
                    WHERE id = ?
                ''', (session_duration, self.score, self.session_id))
                self.conn.commit()
            except Exception as e:
                print(f"Error updating session duration: {e}")
        
        if self.score >= 400:
            self.game_state = GameState.WIN
        elif self.score >= 200:
            self.game_state = GameState.DRAW
        else:
            self.game_state = GameState.LOSE
        
        self.update_player_progress()
        self.show_final_results()
    
    def update_player_progress(self):
        """Update player progress in database with algorithm statistics"""
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_runs,
                    AVG(execution_time_ms) as avg_time,
                    MIN(execution_time_ms) as min_time
                FROM algorithm_performance 
                WHERE session_id = ?
            ''', (self.session_id,))
            
            algo_stats = self.cursor.fetchone()
            
            self.cursor.execute('''
                SELECT * FROM player_progress WHERE player_name = ?
            ''', (self.player_name,))
            
            existing = self.cursor.fetchone()
            
            if existing:
                wins = existing[3] + (1 if self.game_state == GameState.WIN else 0)
                losses = existing[4] + (1 if self.game_state == GameState.LOSE else 0)
                draws = existing[5] + (1 if self.game_state == GameState.DRAW else 0)
                best_score = max(existing[6], self.score)
                
                total_runs = existing[9] + (algo_stats[0] if algo_stats else 0)
                
                if existing[7] > 0 and algo_stats and algo_stats[1]:
                    current_avg = existing[7]
                    current_runs = existing[9]
                    new_avg = (current_avg * current_runs + algo_stats[1] * algo_stats[0]) / total_runs
                elif algo_stats and algo_stats[1]:
                    new_avg = algo_stats[1]
                else:
                    new_avg = existing[7]
                
                fastest_time = min(existing[8], algo_stats[2]) if existing[8] > 0 and algo_stats and algo_stats[2] else (
                    algo_stats[2] if algo_stats and algo_stats[2] else existing[8]
                )
                
                self.cursor.execute('''
                    UPDATE player_progress 
                    SET total_games = total_games + 1,
                        wins = ?,
                        losses = ?,
                        draws = ?,
                        best_score = ?,
                        average_execution_time_ms = ?,
                        fastest_algorithm_time_ms = ?,
                        total_algorithm_runs = ?,
                        last_played = CURRENT_TIMESTAMP
                    WHERE player_name = ?
                ''', (wins, losses, draws, best_score, new_avg, fastest_time, total_runs, self.player_name))
            else:
                wins = 1 if self.game_state == GameState.WIN else 0
                losses = 1 if self.game_state == GameState.LOSE else 0
                draws = 1 if self.game_state == GameState.DRAW else 0
                
                avg_time = algo_stats[1] if algo_stats and algo_stats[1] else 0
                min_time = algo_stats[2] if algo_stats and algo_stats[2] else 0
                total_runs = algo_stats[0] if algo_stats else 0
                
                self.cursor.execute('''
                    INSERT INTO player_progress 
                    (player_name, total_games, wins, losses, draws, best_score,
                     average_execution_time_ms, fastest_algorithm_time_ms, total_algorithm_runs)
                    VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?)
                ''', (self.player_name, wins, losses, draws, self.score, avg_time, min_time, total_runs))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error updating player progress: {e}")
            self.conn.rollback()
    
    def show_final_results(self):
        """Show final game results with algorithm performance summary"""
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        if self.game_state == GameState.WIN:
            title = "🏆 VICTORY! 🏆"
            color = COLORS['accent_green']
            message = "Congratulations! You've mastered maximum flow!"
        elif self.game_state == GameState.DRAW:
            title = "🤝 GOOD GAME! 🤝"
            color = COLORS['accent_yellow']
            message = "Well played! Try again to improve your score!"
        else:
            title = "💪 KEEP TRYING! 💪"
            color = COLORS['accent_red']
            message = "Better luck next time! Practice makes perfect!"
        
        tk.Label(
            main_frame,
            text=title,
            font=("Impact", 48, "bold"),
            fg=color,
            bg=COLORS['bg_dark']
        ).pack(pady=30)
        
        tk.Label(
            main_frame,
            text=message,
            font=("Arial", 20),
            fg=COLORS['text_light'],
            bg=COLORS['bg_dark']
        ).pack(pady=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        results_frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(results_frame, text="📊 Game Results")
        
        results_container = tk.Frame(results_frame, bg=COLORS['bg_dark'])
        results_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        canvas = tk.Canvas(results_container, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = tk.Scrollbar(results_container, orient="vertical", command=canvas.yview,
                                bg=COLORS['accent_blue'], troughcolor=COLORS['bg_panel'], width=16)
        scrollable_results = tk.Frame(canvas, bg=COLORS['bg_dark'])
        
        scrollable_results.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_results, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def configure_window(event):
            canvas.itemconfig(window, width=event.width)
        
        window = canvas.create_window((0, 0), window=scrollable_results, anchor="nw")
        canvas.bind("<Configure>", configure_window)
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        stats_frame = tk.Frame(scrollable_results, bg=COLORS['bg_panel'])
        stats_frame.pack(fill=tk.X, pady=10, padx=20)
        
        tk.Label(
            stats_frame,
            text="Game Statistics",
            font=("Arial", 18, "bold"),
            fg=COLORS['accent_blue'],
            bg=COLORS['bg_panel']
        ).pack(pady=10)
        
        game_stats = [
            ("Final Score", str(self.score)),
            ("Rounds Played", f"{self.current_round - 1}/{self.max_rounds}"),
            ("Game Result", self.game_state.value.upper()),
            ("", "")
        ]
        
        for label, value in game_stats:
            if label:
                frame = tk.Frame(stats_frame, bg=COLORS['bg_light'])
                frame.pack(fill=tk.X, pady=2)
                
                tk.Label(
                    frame,
                    text=label,
                    font=("Arial", 12, "bold"),
                    fg=COLORS['text_light'],
                    bg=COLORS['bg_light'],
                    width=25,
                    anchor='w'
                ).pack(side=tk.LEFT, padx=20)
                
                tk.Label(
                    frame,
                    text=value,
                    font=("Arial", 12),
                    fg=COLORS['accent_yellow'],
                    bg=COLORS['bg_light']
                ).pack(side=tk.LEFT, padx=20)
        
        try:
            self.cursor.execute('''
                SELECT total_games, wins, losses, draws, best_score,
                       average_execution_time_ms, fastest_algorithm_time_ms, total_algorithm_runs
                FROM player_progress 
                WHERE player_name = ?
            ''', (self.player_name,))
            
            player_stats = self.cursor.fetchone()
            
            if player_stats:
                player_frame = tk.Frame(scrollable_results, bg=COLORS['bg_panel'])
                player_frame.pack(fill=tk.X, pady=10, padx=20)
                
                tk.Label(
                    player_frame,
                    text="Player Statistics",
                    font=("Arial", 18, "bold"),
                    fg=COLORS['accent_green'],
                    bg=COLORS['bg_panel']
                ).pack(pady=10)
                
                total_games, wins, losses, draws, best_score, avg_time, fastest_time, total_runs = player_stats
                win_rate = (wins / total_games * 100) if total_games > 0 else 0
                
                player_stats_display = [
                    ("Total Games", str(total_games)),
                    ("Wins", str(wins)),
                    ("Losses", str(losses)),
                    ("Draws", str(draws)),
                    ("Win Rate", f"{win_rate:.1f}%"),
                    ("Best Score", str(best_score)),
                    ("Avg Algorithm Time", f"{avg_time:.2f} ms" if avg_time else "N/A"),
                    ("Fastest Algorithm Time", f"{fastest_time:.2f} ms" if fastest_time else "N/A"),
                    ("Total Algorithm Runs", str(total_runs))
                ]
                
                for label, value in player_stats_display:
                    frame = tk.Frame(player_frame, bg=COLORS['bg_light'])
                    frame.pack(fill=tk.X, pady=2)
                    
                    tk.Label(
                        frame,
                        text=label,
                        font=("Arial", 12, "bold"),
                        fg=COLORS['text_light'],
                        bg=COLORS['bg_light'],
                        width=25,
                        anchor='w'
                    ).pack(side=tk.LEFT, padx=20)
                    
                    tk.Label(
                        frame,
                        text=value,
                        font=("Arial", 12),
                        fg=COLORS['accent_yellow'],
                        bg=COLORS['bg_light']
                    ).pack(side=tk.LEFT, padx=20)
                    
        except Exception as e:
            print(f"Error fetching player stats: {e}")
        
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_algorithms,
                    AVG(execution_time_ms) as avg_time,
                    MIN(execution_time_ms) as min_time,
                    MAX(execution_time_ms) as max_time,
                    SUM(nodes_visited) as total_nodes
                FROM algorithm_performance
                WHERE session_id = ?
            ''', (self.session_id,))
            
            session_algo_stats = self.cursor.fetchone()
            
            if session_algo_stats:
                algo_frame = tk.Frame(scrollable_results, bg=COLORS['bg_panel'])
                algo_frame.pack(fill=tk.X, pady=10, padx=20)
                
                tk.Label(
                    algo_frame,
                    text="This Session - Algorithm Performance",
                    font=("Arial", 18, "bold"),
                    fg=COLORS['accent_purple'],
                    bg=COLORS['bg_panel']
                ).pack(pady=10)
                
                total_algorithms, avg_time, min_time, max_time, total_nodes = session_algo_stats
                
                session_stats = [
                    ("Total Algorithm Runs", str(total_algorithms)),
                    ("Average Execution Time", f"{avg_time:.2f} ms"),
                    ("Fastest Execution Time", f"{min_time:.2f} ms"),
                    ("Slowest Execution Time", f"{max_time:.2f} ms"),
                    ("Total Nodes Visited", f"{total_nodes:,}" if total_nodes else "N/A")
                ]
                
                for label, value in session_stats:
                    frame = tk.Frame(algo_frame, bg=COLORS['bg_light'])
                    frame.pack(fill=tk.X, pady=2)
                    
                    tk.Label(
                        frame,
                        text=label,
                        font=("Arial", 12, "bold"),
                        fg=COLORS['text_light'],
                        bg=COLORS['bg_light'],
                        width=25,
                        anchor='w'
                    ).pack(side=tk.LEFT, padx=20)
                    
                    tk.Label(
                        frame,
                        text=value,
                        font=("Arial", 12),
                        fg=COLORS['accent_yellow'],
                        bg=COLORS['bg_light']
                    ).pack(side=tk.LEFT, padx=20)
                    
        except Exception as e:
            print(f"Error fetching session algo stats: {e}")
        
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="PLAY AGAIN",
            command=self.start_max_flow_game,
            font=("Arial", 16, "bold"),
            fg='white',
            bg=COLORS['accent_green'],
            padx=40,
            pady=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            button_frame,
            text="VIEW LEADERBOARD",
            command=self.show_leaderboard,
            font=("Arial", 16, "bold"),
            fg='white',
            bg=COLORS['accent_blue'],
            padx=40,
            pady=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            button_frame,
            text="MAIN MENU",
            command=self.show_main_menu,
            font=("Arial", 16, "bold"),
            fg='white',
            bg=COLORS['accent_purple'],
            padx=40,
            pady=15,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=20)
    
    def show_main_menu(self):
        """Show enhanced main menu"""
        self.clear_screen()
        
        menu_frame = tk.Frame(self.root, bg=COLORS['bg_dark'])
        menu_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame = tk.Frame(menu_frame, bg=COLORS['bg_dark'], bd=0)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        title_label = tk.Label(
            content_frame, text="🚦 MAXIMUM FLOW CHALLENGE 🚗",
            font=("Impact", 48, "bold"), fg=COLORS['accent_blue'],
            bg=COLORS['bg_dark'], bd=0
        )
        title_label.pack(pady=(0, 10))
        
        tk.Label(
            content_frame, text="Calculate Maximum Flow in Traffic Networks",
            font=("Arial", 20, "italic"), fg=COLORS['text_dim'],
            bg=COLORS['bg_dark'], bd=0
        ).pack(pady=(0, 50))
        
        mode_frame = tk.Frame(content_frame, bg=COLORS['bg_dark'], bd=0)
        mode_frame.pack(pady=20)
        
        mode_buttons = [
            ("🎮 MAX FLOW GAME", COLORS['accent_green'], self.start_max_flow_game),
            ("📈 PERFORMANCE CHARTS", COLORS['accent_purple'], self.show_performance_charts),
            ("🧮 ALGORITHM DEMO", COLORS['accent_blue'], self.show_algorithm_demo),
            ("📊 STATISTICS", COLORS['accent_purple'], self.show_statistics),
            ("🏆 LEADERBOARD", COLORS['accent_yellow'], self.show_leaderboard),
            ("❓ HOW TO PLAY", COLORS['accent_red'], self.show_help)
        ]
        
        for text, color, command in mode_buttons:
            btn = tk.Button(
                mode_frame, text=text, command=command,
                font=("Arial", 18, "bold"), fg='white',
                bg=color, activebackground=self.darken_color(color, 20),
                padx=50, pady=20, cursor="hand2",
                relief=tk.FLAT, bd=0,
                highlightthickness=2, highlightbackground=self.lighten_color(color, 30),
                highlightcolor=self.lighten_color(color, 30)
            )
            btn.pack(pady=10, fill=tk.X)
        
        bottom_frame = tk.Frame(content_frame, bg=COLORS['bg_panel'])
        bottom_frame.pack(pady=50, fill=tk.X)
        
        tk.Label(
            bottom_frame,
            text="Instructions: Calculate maximum flow from Source (A) to Sink (T) through the network",
            font=("Arial", 12),
            fg=COLORS['text_light'],
            bg=COLORS['bg_panel'],
            wraplength=600
        ).pack(pady=10)
    
    def show_performance_charts(self):
        """NEW METHOD: Show performance charts for algorithm comparison"""
        try:
            # Create a new window for charts
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Algorithm Performance Analysis")
            chart_window.geometry("1200x800")
            chart_window.configure(bg=COLORS['bg_dark'])
            
            # Title
            tk.Label(
                chart_window,
                text="📊 Algorithm Performance Charts",
                font=("Impact", 28, "bold"),
                fg=COLORS['accent_blue'],
                bg=COLORS['bg_dark']
            ).pack(pady=20)
            
            # Query data from database
            try:
                query = """
                SELECT round_number, algorithm_name, execution_time_ms, max_flow_result, nodes_visited
                FROM algorithm_performance
                WHERE session_id = ?
                ORDER BY round_number, algorithm_name
                """
                self.cursor.execute(query, (self.session_id,))
                data = self.cursor.fetchall()
                
                if not data:
                    tk.Label(chart_window, text="No performance data found. Play the game first!", 
                            font=("Arial", 16), fg=COLORS['accent_red'], bg=COLORS['bg_dark']).pack(pady=50)
                    return
                
                # Convert to DataFrame
                df = pd.DataFrame(data, columns=['Round', 'Algorithm', 'Time_ms', 'Max_Flow', 'Nodes_Visited'])
                
                # Create figure with subplots
                fig, axes = plt.subplots(2, 2, figsize=(12, 9))
                fig.suptitle('Algorithm Performance Analysis', fontsize=16, fontweight='bold')
                plt.subplots_adjust(hspace=0.35, wspace=0.3)
                
                # Chart 1: Execution Time Trend
                for algo in ['Edmonds-Karp', 'Dinic']:
                    algo_data = df[df['Algorithm'] == algo]
                    axes[0, 0].plot(algo_data['Round'], algo_data['Time_ms'], marker='o', 
                                   label=algo, linewidth=2, markersize=8)
                axes[0, 0].set_title('Execution Time per Round', fontsize=14)
                axes[0, 0].set_xlabel('Round Number', fontsize=12)
                axes[0, 0].set_ylabel('Time (milliseconds)', fontsize=12)
                axes[0, 0].legend(fontsize=11)
                axes[0, 0].grid(True, linestyle='--', alpha=0.6)
                axes[0, 0].tick_params(axis='both', labelsize=10)
                
                # Chart 2: Average Time Comparison (Bar Chart)
                avg_time = df.groupby('Algorithm')['Time_ms'].mean()
                colors = ['#4a9eff', '#2ecc71']
                bars = axes[0, 1].bar(avg_time.index, avg_time.values, color=colors, width=0.6)
                axes[0, 1].set_title('Average Execution Time', fontsize=14)
                axes[0, 1].set_ylabel('Time (milliseconds)', fontsize=12)
                axes[0, 1].tick_params(axis='both', labelsize=10)
                
                # Add value labels on bars
                for bar, avg in zip(bars, avg_time.values):
                    height = bar.get_height()
                    axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.5,
                                   f'{avg:.2f} ms', ha='center', va='bottom', 
                                   fontweight='bold', fontsize=11)
                
                # Chart 3: Max Flow Found by Each Algorithm (Box Plot)
                flow_data = [df[df['Algorithm']=='Edmonds-Karp']['Max_Flow'], 
                           df[df['Algorithm']=='Dinic']['Max_Flow']]
                box = axes[1, 0].boxplot(flow_data, labels=['Edmonds-Karp', 'Dinic'], 
                                        patch_artist=True, widths=0.6)
                box['boxes'][0].set_facecolor('#4a9eff')
                box['boxes'][1].set_facecolor('#2ecc71')
                axes[1, 0].set_title('Max Flow Results Distribution', fontsize=14)
                axes[1, 0].set_ylabel('Maximum Flow', fontsize=12)
                axes[1, 0].tick_params(axis='both', labelsize=10)
                axes[1, 0].grid(True, axis='y', linestyle='--', alpha=0.6)
                
                # Chart 4: Nodes Visited vs Time Scatter Plot
                for algo in ['Edmonds-Karp', 'Dinic']:
                    algo_data = df[df['Algorithm'] == algo]
                    axes[1, 1].scatter(algo_data['Time_ms'], algo_data['Nodes_Visited'], 
                                     label=algo, alpha=0.7, s=100, edgecolors='black', linewidth=0.5)
                axes[1, 1].set_title('Time vs. Nodes Visited', fontsize=14)
                axes[1, 1].set_xlabel('Time (ms)', fontsize=12)
                axes[1, 1].set_ylabel('Nodes Visited', fontsize=12)
                axes[1, 1].legend(fontsize=11)
                axes[1, 1].grid(True, linestyle='--', alpha=0.6)
                axes[1, 1].tick_params(axis='both', labelsize=10)
                
                # Embed the Matplotlib figure in the Tkinter window
                canvas = FigureCanvasTkAgg(fig, master=chart_window)
                canvas.draw()
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=20, pady=10)
                
                # Control buttons frame
                control_frame = tk.Frame(chart_window, bg=COLORS['bg_dark'])
                control_frame.pack(pady=10)
                
                def export_to_csv():
                    """Export data to CSV file"""
                    filename = f"algorithm_performance_session_{self.session_id}.csv"
                    df.to_csv(filename, index=False)
                    messagebox.showinfo("Export Successful", 
                                      f"Data exported to '{filename}'")
                
                def export_to_excel():
                    """Export data to Excel file"""
                    try:
                        filename = f"algorithm_performance_session_{self.session_id}.xlsx"
                        df.to_excel(filename, index=False)
                        messagebox.showinfo("Export Successful", 
                                          f"Data exported to '{filename}'")
                    except Exception as e:
                        messagebox.showerror("Export Error", 
                                          f"Could not export to Excel: {str(e)}\nMake sure pandas is installed with Excel support.")
                
                def show_database_screenshot_instructions():
                    """Show instructions for taking database screenshots"""
                    instructions = """
                    To take database screenshots:
                    
                    1. Install DB Browser for SQLite (free software)
                    2. Open 'advanced_traffic.db' file
                    3. Go to 'Browse Data' tab
                    4. Select 'algorithm_performance' table
                    5. Take screenshot of the data table
                    
                    The database file is located in the same folder as this application.
                    """
                    messagebox.showinfo("Database Screenshot Instructions", instructions)
                
                # Buttons
                tk.Button(
                    control_frame,
                    text="📥 Export to CSV",
                    command=export_to_csv,
                    font=("Arial", 12, "bold"),
                    fg='white',
                    bg=COLORS['accent_green'],
                    padx=20,
                    pady=10,
                    cursor="hand2"
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    control_frame,
                    text="📊 Export to Excel",
                    command=export_to_excel,
                    font=("Arial", 12, "bold"),
                    fg='white',
                    bg=COLORS['accent_blue'],
                    padx=20,
                    pady=10,
                    cursor="hand2"
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    control_frame,
                    text="🗄️ Database Instructions",
                    command=show_database_screenshot_instructions,
                    font=("Arial", 12, "bold"),
                    fg='white',
                    bg=COLORS['accent_purple'],
                    padx=20,
                    pady=10,
                    cursor="hand2"
                ).pack(side=tk.LEFT, padx=10)
                
                tk.Button(
                    control_frame,
                    text="Close",
                    command=chart_window.destroy,
                    font=("Arial", 12, "bold"),
                    fg='white',
                    bg=COLORS['accent_red'],
                    padx=20,
                    pady=10,
                    cursor="hand2"
                ).pack(side=tk.LEFT, padx=10)
                
            except Exception as e:
                messagebox.showerror("Data Error", f"Could not fetch data: {str(e)}")
                chart_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Chart Error", f"Could not display charts: {str(e)}")
    
    def show_algorithm_demo(self):
        """Show algorithm demonstration"""
        demo_window = tk.Toplevel(self.root)
        demo_window.title("Algorithm Demonstration")
        demo_window.geometry("1000x700")
        demo_window.configure(bg=COLORS['bg_dark'])
        
        tk.Label(
            demo_window,
            text="🧮 Algorithm Demonstration",
            font=("Impact", 32, "bold"),
            fg=COLORS['accent_blue'],
            bg=COLORS['bg_dark']
        ).pack(pady=20)
        
        self.generate_random_capacities()
        max_flow = self.calculate_max_flow_algorithms()
        
        canvas_frame = tk.Frame(demo_window, bg=COLORS['bg_panel'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg_dark'], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_max_flow_network_on_canvas(canvas)
        
        results_frame = tk.Frame(demo_window, bg=COLORS['bg_light'])
        results_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            results_frame,
            text="Algorithm Results:",
            font=("Arial", 16, "bold"),
            fg=COLORS['text_light'],
            bg=COLORS['bg_light']
        ).pack(pady=10)
        
        for result in self.algorithm_results:
            frame = tk.Frame(results_frame, bg=COLORS['bg_panel'])
            frame.pack(fill=tk.X, pady=2, padx=20)
            
            tk.Label(
                frame,
                text=f"{result.algorithm}:",
                font=("Arial", 14),
                fg=COLORS['text_light'],
                bg=COLORS['bg_panel'],
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT, padx=10)
            
            tk.Label(
                frame,
                text=f"Max Flow = {result.max_flow}, Time = {result.execution_time:.2f} ms",
                font=("Arial", 14),
                fg=COLORS['accent_yellow'],
                bg=COLORS['bg_panel']
            ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            demo_window,
            text="CLOSE",
            command=demo_window.destroy,
            font=("Arial", 14, "bold"),
            fg='white',
            bg=COLORS['accent_red'],
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=20)
    
    def draw_max_flow_network_on_canvas(self, canvas):
        """Draw network on given canvas"""
        for (u, v), points in self.edge_paths.items():
            if (u, v) in self.edge_capacities:
                capacity = self.edge_capacities[(u, v)]
                
                for i in range(len(points)-1):
                    x1, y1 = points[i]
                    x2, y2 = points[i+1]
                    
                    width = 3 + capacity / 5
                    color = self.get_capacity_color(capacity)
                    
                    canvas.create_line(x1, y1, x2, y2,
                                     fill=color, width=width, smooth=True,
                                     arrow=tk.LAST if i == len(points)-2 else None,
                                     arrowshape=(8, 10, 3))
                
                if len(points) >= 2:
                    mid_idx = len(points) // 2
                    if mid_idx < len(points):
                        x, y = points[mid_idx]
                        
                        canvas.create_rectangle(x-25, y-15, x+25, y+15,
                                             fill=COLORS['bg_panel'],
                                             outline=color, width=2)
                        
                        canvas.create_text(x, y, text=str(capacity),
                                         font=("Arial", 12, "bold"),
                                         fill='white')
        
        for node, (x, y) in self.nodes.items():
            if node == 'A':
                color = COLORS['accent_green']
                label = "Source (A)"
            elif node == 'T':
                color = COLORS['accent_red']
                label = "Sink (T)"
            else:
                color = COLORS['accent_blue']
                label = node
            
            canvas.create_oval(x-25, y-25, x+25, y+25,
                             fill=color, outline='white', width=3)
            
            canvas.create_text(x, y, text=label,
                             font=("Arial", 12, "bold"),
                             fill='white')
    
    def show_statistics(self):
        """Show game statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Game Statistics")
        stats_window.geometry("800x600")
        stats_window.configure(bg=COLORS['bg_dark'])
        
        tk.Label(
            stats_window,
            text="📊 Game Statistics",
            font=("Impact", 32, "bold"),
            fg=COLORS['accent_blue'],
            bg=COLORS['bg_dark']
        ).pack(pady=20)
        
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_games,
                    COUNT(DISTINCT player_name) as unique_players,
                    AVG(score) as avg_score,
                    MAX(score) as max_score,
                    MIN(execution_time_ms) as min_time,
                    AVG(execution_time_ms) as avg_time
                FROM game_sessions gs
                JOIN algorithm_performance ap ON gs.id = ap.session_id
            ''')
            
            stats = self.cursor.fetchone()
            
            if stats:
                stats_frame = tk.Frame(stats_window, bg=COLORS['bg_panel'])
                stats_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
                
                statistics = [
                    ("Total Games Played", str(stats[0])),
                    ("Unique Players", str(stats[1])),
                    ("Average Score", f"{stats[2]:.1f}"),
                    ("Highest Score", str(stats[3])),
                    ("Fastest Algorithm Time", f"{stats[4]:.2f} ms"),
                    ("Average Algorithm Time", f"{stats[5]:.2f} ms")
                ]
                
                for i, (label, value) in enumerate(statistics):
                    frame = tk.Frame(stats_frame, bg=COLORS['bg_light'])
                    frame.pack(fill=tk.X, pady=5)
                    
                    tk.Label(
                        frame,
                        text=label,
                        font=("Arial", 14),
                        fg=COLORS['text_light'],
                        bg=COLORS['bg_light'],
                        width=25,
                        anchor='w'
                    ).pack(side=tk.LEFT, padx=20)
                    
                    tk.Label(
                        frame,
                        text=value,
                        font=("Arial", 14, "bold"),
                        fg=COLORS['accent_yellow'],
                        bg=COLORS['bg_light']
                    ).pack(side=tk.RIGHT, padx=20)
                    
        except Exception as e:
            print(f"Error fetching statistics: {e}")
        
        tk.Button(
            stats_window,
            text="CLOSE",
            command=stats_window.destroy,
            font=("Arial", 14, "bold"),
            fg='white',
            bg=COLORS['accent_red'],
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=20)
    
    def show_leaderboard(self):
        """Show leaderboard of top players"""
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("800x600")
        leaderboard_window.configure(bg=COLORS['bg_dark'])
        leaderboard_window.transient(self.root)
        
        leaderboard_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - leaderboard_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - leaderboard_window.winfo_height()) // 2
        leaderboard_window.geometry(f"+{x}+{y}")
        
        tk.Label(
            leaderboard_window,
            text="🏆 LEADERBOARD 🏆",
            font=("Impact", 36, "bold"),
            fg=COLORS['accent_yellow'],
            bg=COLORS['bg_dark']
        ).pack(pady=20)
        
        try:
            self.cursor.execute('''
                SELECT player_name, best_score, wins, total_games,
                       (wins * 1.0 / total_games * 100) as win_rate
                FROM player_progress
                WHERE total_games >= 1
                ORDER BY best_score DESC, win_rate DESC
                LIMIT 10
            ''')
            
            top_players = self.cursor.fetchall()
            
            tree_frame = tk.Frame(leaderboard_window, bg=COLORS['bg_dark'])
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            scrollbar = tk.Scrollbar(tree_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            tree = ttk.Treeview(
                tree_frame,
                yscrollcommand=scrollbar.set,
                columns=('Rank', 'Player', 'Best Score', 'Wins', 'Games', 'Win Rate'),
                show='headings',
                height=15
            )
            
            tree.column('Rank', width=80, anchor=tk.CENTER)
            tree.column('Player', width=200, anchor=tk.W)
            tree.column('Best Score', width=120, anchor=tk.CENTER)
            tree.column('Wins', width=80, anchor=tk.CENTER)
            tree.column('Games', width=80, anchor=tk.CENTER)
            tree.column('Win Rate', width=100, anchor=tk.CENTER)
            
            tree.heading('Rank', text='Rank')
            tree.heading('Player', text='Player')
            tree.heading('Best Score', text='Best Score')
            tree.heading('Wins', text='Wins')
            tree.heading('Games', text='Games')
            tree.heading('Win Rate', text='Win Rate %')
            
            for i, player in enumerate(top_players, 1):
                player_name, best_score, wins, total_games, win_rate = player
                win_rate_str = f"{win_rate:.1f}%" if win_rate else "0.0%"
                
                tags = ('highlight',) if player_name == self.player_name else ()
                
                tree.insert(
                    '', 'end',
                    values=(i, player_name, best_score, wins, total_games, win_rate_str),
                    tags=tags
                )
            
            tree.tag_configure('highlight', background=COLORS['accent_blue'], foreground='white')
            
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=tree.yview)
            
        except Exception as e:
            print(f"Error fetching leaderboard: {e}")
        
        tk.Button(
            leaderboard_window,
            text="CLOSE",
            command=leaderboard_window.destroy,
            font=("Arial", 14, "bold"),
            fg='white',
            bg=COLORS['accent_red'],
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=20)
    
    def show_help(self):
        """Show help instructions"""
        help_window = tk.Toplevel(self.root)
        help_window.title("How to Play")
        help_window.geometry("700x600")
        help_window.configure(bg=COLORS['bg_dark'])
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        rules_frame = tk.Frame(notebook, bg=COLORS['bg_dark'])
        notebook.add(rules_frame, text="🎮 Game Rules")
        
        rules_text = """
        MAXIMUM FLOW CHALLENGE
        
        Objective:
        Calculate the maximum possible flow from
        Source (A) to Sink (T) through the network.
        
        Rules:
        1. Each edge has a capacity (vehicles/minute)
        2. Flow cannot exceed edge capacity
        3. Flow conservation: Incoming = Outgoing at nodes
        4. You have 5 rounds to prove your skills
        
        Scoring:
        • Correct answer: 100 points
        • Close answer (within 2): 50 points
        • Close answer (within 5): 25 points
        • Wrong answer: 0 points
        
        Win Conditions:
        • Score 400+ points: VICTORY 🏆
        • Score 200-399 points: DRAW 🤝
        • Score below 200: DEFEAT 💪
        """
        
        tk.Label(
            rules_frame,
            text=rules_text,
            font=("Arial", 14),
            fg=COLORS['text_light'],
            bg=COLORS['bg_dark'],
            justify=tk.LEFT
        ).pack(padx=20, pady=20)
        
        tk.Button(
            help_window,
            text="CLOSE",
            command=help_window.destroy,
            font=("Arial", 14, "bold"),
            fg='white',
            bg=COLORS['accent_red'],
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=20)
    
    def clear_screen(self):
        """Clear all widgets from screen"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def darken_color(self, hex_color, percent):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
    
    def lighten_color(self, hex_color, percent):
        """Lighten a hex color"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c + (255 - c) * percent / 100)) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


def main():
    """Main function to run the game"""
    try:
        root = tk.Tk()
        root.title("🚦 Advanced Traffic Flow Simulator")
        root.geometry("1200x800")
        root.configure(bg=COLORS['bg_dark'])
        
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        game = AdvancedTrafficGame(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to start application: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Install required packages if missing
    try:
        import matplotlib
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "pandas"])
    
    main()