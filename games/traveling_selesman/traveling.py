import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import math
import sqlite3
from datetime import datetime
import time
import unittest
from pathlib import Path
import winsound
from enum import Enum
import json
import itertools
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for tkinter compatibility
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class City:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
    
    def distance_to(self, other_city):
        """Calculate Euclidean distance between two cities"""
        return math.sqrt((self.x - other_city.x)**2 + (self.y - other_city.y)**2)

class TSPAlgorithm:
    @staticmethod
    def brute_force(cities, start_city, distance_matrix):
        """Brute force solution - try all permutations"""
        if len(cities) <= 1:
            return [], 0
        
        # Remove start city and find all permutations
        other_cities = [c for c in cities if c.name != start_city.name]
        min_distance = float('inf')
        best_path = []
        
        for perm in itertools.permutations(other_cities):
            distance = 0
            current = start_city
            path = [start_city.name]
            
            # Calculate distance through permutation
            for city in perm:
                distance += distance_matrix.get((current.name, city.name), 0)
                current = city
                path.append(city.name)
            
            # Return to start
            distance += distance_matrix.get((current.name, start_city.name), 0)
            path.append(start_city.name)
            
            if distance < min_distance:
                min_distance = distance
                best_path = path
        
        return best_path, min_distance
    
    @staticmethod
    def nearest_neighbor(cities, start_city, distance_matrix):
        """Nearest neighbor heuristic algorithm"""
        if len(cities) <= 1:
            return [], 0
        
        unvisited = [c for c in cities if c.name != start_city.name]
        path = [start_city.name]
        current = start_city
        total_distance = 0
        
        while unvisited:
            # Find nearest unvisited city
            nearest = None
            min_dist = float('inf')
            for city in unvisited:
                dist = distance_matrix.get((current.name, city.name), float('inf'))
                if dist < min_dist:
                    min_dist = dist
                    nearest = city
            
            if nearest:
                total_distance += min_dist
                path.append(nearest.name)
                current = nearest
                unvisited.remove(nearest)
        
        # Return to start
        total_distance += distance_matrix.get((current.name, start_city.name), 0)
        path.append(start_city.name)
        
        return path, total_distance
    
    @staticmethod
    def genetic_algorithm(cities, start_city, distance_matrix, population_size=100, generations=500):
        """Genetic algorithm solution"""
        if len(cities) <= 1:
            return [], 0
        
        # Remove start city from population generation
        other_cities = [c for c in cities if c.name != start_city.name]
        
        def calculate_fitness(individual):
            """Calculate fitness of an individual route"""
            distance = 0
            current = start_city
            for city in individual:
                distance += distance_matrix.get((current.name, city.name), 0)
                current = city
            distance += distance_matrix.get((current.name, start_city.name), 0)
            return 1.0 / (distance + 0.01)  # Add small constant to avoid division by zero
        
        # Initialize population
        population = []
        for _ in range(population_size):
            individual = other_cities.copy()
            random.shuffle(individual)
            population.append(individual)
        
        best_distance = float('inf')
        best_path = []
        
        # Evolution
        for generation in range(generations):
            # Evaluate fitness
            fitness = []
            for individual in population:
                fitness.append(calculate_fitness(individual))
            
            # Check for best solution
            for individual in population:
                distance = 0
                current = start_city
                path = [start_city.name]
                
                for city in individual:
                    distance += distance_matrix.get((current.name, city.name), 0)
                    current = city
                    path.append(city.name)
                
                distance += distance_matrix.get((current.name, start_city.name), 0)
                path.append(start_city.name)
                
                if distance < best_distance:
                    best_distance = distance
                    best_path = path
            
            # Selection (tournament selection)
            new_population = []
            for _ in range(population_size):
                # Tournament of size 3
                tournament = random.sample(list(zip(population, fitness)), 3)
                tournament.sort(key=lambda x: x[1], reverse=True)
                new_population.append(tournament[0][0])
            
            # Crossover and mutation
            population = []
            for i in range(0, len(new_population), 2):
                if i + 1 < len(new_population):
                    parent1 = new_population[i]
                    parent2 = new_population[i + 1]
                    
                    # Crossover (order crossover)
                    child1, child2 = TSPAlgorithm._crossover(parent1, parent2)
                    
                    # Mutation
                    if random.random() < 0.1:
                        child1 = TSPAlgorithm._mutate(child1)
                    if random.random() < 0.1:
                        child2 = TSPAlgorithm._mutate(child2)
                    
                    population.extend([child1, child2])
                else:
                    population.append(new_population[i])
        
        return best_path, best_distance
    
    @staticmethod
    def _crossover(parent1, parent2):
        """Order crossover for TSP"""
        size = len(parent1)
        a, b = sorted(random.sample(range(size), 2))
        
        child1 = [None] * size
        child2 = [None] * size
        
        # Copy segment
        child1[a:b] = parent1[a:b]
        child2[a:b] = parent2[a:b]
        
        # Fill remaining positions
        idx1 = idx2 = b
        for i in range(b, size + b):
            pos = i % size
            if parent2[pos] not in child1:
                child1[idx1 % size] = parent2[pos]
                idx1 += 1
            if parent1[pos] not in child2:
                child2[idx2 % size] = parent1[pos]
                idx2 += 1
        
        return child1, child2
    
    @staticmethod
    def _mutate(individual):
        """Swap mutation"""
        if len(individual) >= 2:
            a, b = random.sample(range(len(individual)), 2)
            individual[a], individual[b] = individual[b], individual[a]
        return individual

class TravelingSalesmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Traveling Salesman Problem Game")
        
        # Get screen dimensions and set to large size
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # Use 95% of screen for better visibility
        self.window_width = int(self.screen_width * 0.95)
        self.window_height = int(self.screen_height * 0.90)
        
        # Center the window
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # Set minimum window size
        self.root.minsize(1200, 700)
        
        self.root.configure(bg='#1e3d59')
        
        # Sound effects flag
        self.sound_enabled = True
        
        # Game difficulty
        self.difficulty = Difficulty.MEDIUM
        
        # Animation control
        self.title_animation_id = None
        
        # Play Phase variables
        self.play_phase_active = False
        self.play_animation_id = None
        self.play_speed = 100  # ms between steps
        self.current_algorithm_index = 0
        self.algorithm_visualization_active = False
        self.path_visualization_lines = []
        
        # Canvas dimensions for city placement
        self.canvas_width = 1400  # Increased canvas width
        self.canvas_height = 1200  # Increased canvas height
        
        # Algorithms for Play Phase
        self.play_algorithms = {
            'recursive_backtracking': {
                'name': 'Recursive Backtracking',
                'description': 'Checks all possible paths',
                'color': '#E74C3C',
                'path': [],
                'distance': 0,
                'time': 0
            },
            'iterative_validation': {
                'name': 'Iterative Validation',
                'description': 'Step-by-step path validation',
                'color': '#3498DB',
                'path': [],
                'distance': 0,
                'time': 0
            },
            'nearest_neighbor': {
                'name': 'Nearest Neighbor',
                'description': 'Greedy shortest-path approximation',
                'color': '#27AE60',
                'path': [],
                'distance': 0,
                'time': 0
            }
        }
        
        # Create database and tables
        self.init_database()
        
        # Game state
        self.cities = []
        self.distance_matrix = {}
        self.home_city = None
        self.selected_cities = []
        self.user_selected_cities = []  # Cities selected by user
        self.current_route = []
        self.best_route = []
        self.best_distance = float('inf')
        self.player_name = ""
        self.game_over = False
        self.game_id = None
        self.num_cities = 10
        self.city_names = [chr(65 + i) for i in range(self.num_cities)]  # A-J
        self.city_selection_mode = False  # Flag for city selection phase
        
        # Algorithm results - THREE algorithms as per requirement
        self.algorithm_results = {
            'brute_force': {'time': 0, 'distance': 0, 'path': []},
            'nearest_neighbor': {'time': 0, 'distance': 0, 'path': []},
            'genetic_algorithm': {'time': 0, 'distance': 0, 'path': []}
        }
        
        # City colors
        self.city_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        
        self.setup_main_menu()
    
    def init_database(self):
        #Initialize SQLite database with all required tables
        try:
            self.db_path = Path("tsp_game.db")
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create players table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    games_played INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    best_score REAL DEFAULT 0,
                    total_distance_saved REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create game_history table - ONLY store correct answers
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    player_id INTEGER,
                    player_name TEXT,
                    home_city TEXT,
                    selected_cities TEXT,
                    player_route TEXT,
                    player_distance REAL,
                    optimal_route TEXT,
                    optimal_distance REAL,
                    game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            ''')
            
            # Create algorithm_performance table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS algorithm_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    algorithm_name TEXT,
                    execution_time_ms REAL,
                    distance REAL,
                    complexity_analysis TEXT,
                    game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create game_settings table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            raise
    
    def clear_window(self):
        """Clear all widgets from window"""
        # Stop any running animations
        if self.title_animation_id:
            self.root.after_cancel(self.title_animation_id)
            self.title_animation_id = None
        
        # Stop Play Phase animations
        if self.play_animation_id:
            self.root.after_cancel(self.play_animation_id)
            self.play_animation_id = None
        
        self.play_phase_active = False
        
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def generate_cities(self):
        #Generate random cities with distances between 50-100 km
        try:
            self.cities = []
            
            # Generate random positions with better spacing
            margin = 100
            effective_width = self.canvas_width - 2 * margin
            effective_height = self.canvas_height - 2 * margin
            
            # Calculate minimum distance between cities for better spacing
            min_distance = min(effective_width, effective_height) // (self.num_cities // 2)
            
            city_positions = []
            attempts_per_city = 0
            max_attempts = 100
            
            for i in range(self.num_cities):
                placed = False
                attempts = 0
                
                while not placed and attempts < max_attempts:
                    x = random.randint(margin, self.canvas_width - margin)
                    y = random.randint(margin, self.canvas_height - margin)
                    
                    # Check distance from existing cities
                    too_close = False
                    for pos in city_positions:
                        px, py = pos
                        dist = math.sqrt((x - px)**2 + (y - py)**2)
                        if dist < min_distance:
                            too_close = True
                            break
                    
                    if not too_close:
                        city_positions.append((x, y))
                        name = self.city_names[i]
                        self.cities.append(City(name, x, y))
                        placed = True
                    
                    attempts += 1
                    attempts_per_city = max(attempts_per_city, attempts)
                
                if not placed:
                    # Force placement if couldn't find good spot
                    x = random.randint(margin, self.canvas_width - margin)
                    y = random.randint(margin, self.canvas_height - margin)
                    name = self.city_names[i]
                    self.cities.append(City(name, x, y))
            
            # Generate random distances between 50 and 100 km
            self.distance_matrix = {}
            for i in range(self.num_cities):
                for j in range(self.num_cities):
                    if i != j:
                        distance = random.randint(50, 100)
                        self.distance_matrix[(self.city_names[i], self.city_names[j])] = distance
                    else:
                        self.distance_matrix[(self.city_names[i], self.city_names[j])] = 0
            
            # Select random home city
            self.home_city = random.choice(self.cities)
            
            # Reset game state
            self.current_route = [self.home_city.name]
            self.best_route = []
            self.best_distance = float('inf')
            self.game_over = False
            self.city_selection_mode = True  # Enter city selection mode
            self.user_selected_cities = []  # Clear previous selections
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate cities: {e}")
    
    def calculate_distance(self, route):
        #Calculate total distance for a given route using distance matrix
        try:
            total = 0
            for i in range(len(route) - 1):
                city1 = route[i]
                city2 = route[i + 1]
                total += self.distance_matrix.get((city1, city2), 0)
            return total
        except Exception as e:
            messagebox.showerror("Error", f"Failed to calculate distance: {e}")
            return float('inf')
    
    def run_algorithms(self):
        """Run THREE TSP algorithms and record their performance"""
        try:
            if not self.user_selected_cities:
                raise ValueError("No cities selected by user")
            
            all_cities = [self.home_city] + self.user_selected_cities
            
            # Brute Force (only for small number of cities)
            if len(all_cities) <= 8:
                start_time = time.time()
                path, distance = TSPAlgorithm.brute_force(all_cities, self.home_city, self.distance_matrix)
                self.algorithm_results['brute_force'] = {
                    'time': (time.time() - start_time) * 1000,
                    'distance': distance,
                    'path': path
                }
            else:
                self.algorithm_results['brute_force'] = {
                    'time': -1,
                    'distance': float('inf'),
                    'path': []
                }
            
            # Nearest Neighbor
            start_time = time.time()
            path, distance = TSPAlgorithm.nearest_neighbor(all_cities, self.home_city, self.distance_matrix)
            self.algorithm_results['nearest_neighbor'] = {
                'time': (time.time() - start_time) * 1000,
                'distance': distance,
                'path': path
            }
            
            # Genetic Algorithm
            start_time = time.time()
            path, distance = TSPAlgorithm.genetic_algorithm(all_cities, self.home_city, self.distance_matrix)
            self.algorithm_results['genetic_algorithm'] = {
                'time': (time.time() - start_time) * 1000,
                'distance': distance,
                'path': path
            }
            
            # Find optimal solution from the THREE algorithms
            optimal_distance = float('inf')
            optimal_algorithm = None
            
            for algo, result in self.algorithm_results.items():
                if result['distance'] < optimal_distance:
                    optimal_distance = result['distance']
                    optimal_algorithm = algo
            
            self.best_distance = optimal_distance
            self.best_route = self.algorithm_results[optimal_algorithm]['path']
            
        except Exception as e:
            messagebox.showerror("Algorithm Error", f"Failed to run algorithms: {e}")
    
    def play_sound(self, sound_type):
        #Play sound effects with error handling
        if not self.sound_enabled:
            return
            
        try:
            if sound_type == "click":
                frequency = random.randint(300, 500)
                duration = random.randint(30, 80)
                winsound.Beep(frequency, duration)
            elif sound_type == "correct":
                for freq in [262, 330, 392, 523]:
                    winsound.Beep(freq, 100)
            elif sound_type == "incorrect":
                for freq in [392, 330, 262, 196]:
                    winsound.Beep(freq, 150)
            elif sound_type == "win":
                for freq in [523, 659, 784, 1047, 784, 659, 523]:
                    winsound.Beep(freq, 150)
        except Exception:
            pass  # Sound not available on this system
    
    def setup_main_menu(self):
        """Create main menu with options"""
        self.clear_window()
        
        # Create a main frame with padding
        main_frame = tk.Frame(self.root, bg='#1e3d59', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas for scrolling if content is too large
        canvas = tk.Canvas(main_frame, bg='#1e3d59', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e3d59')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title with animation
        title_frame = tk.Frame(scrollable_frame, bg='#1e3d59')
        title_frame.pack(pady=(20, 20))
        
        self.title_label = tk.Label(
            title_frame, text="✈️ Traveling Salesman 🧳",
            font=("Impact", 48, "bold"), bg='#1e3d59', fg='#4ECDC4'
        )
        self.title_label.pack()
        
        # Animate title color
        self.title_color_index = 0
        self.animate_title()
        
        tk.Label(
            title_frame, text="Find the Shortest Route",
            font=("Arial", 24, "italic"), bg='#1e3d59', fg='#f5f5f5'
        ).pack(pady=(0, 40))
        
        # Menu buttons with responsive sizing
        button_frame = tk.Frame(scrollable_frame, bg='#1e3d59')
        button_frame.pack(pady=20, padx=100, fill=tk.BOTH, expand=True)
        
        menu_buttons = [
            ("🎮 New Game", self.setup_player_selection),
            ("📊 Algorithm Comparison", self.show_algorithm_comparison),
            ("📈 Algorithm Performance Chart", self.show_algorithm_performance_chart),
            ("❓ How to Play", self.show_instructions),
            ("🏆 Player Stats", self.show_player_stats),
            ("📈 Leaderboard", self.show_leaderboard),
            ("⚙️ Game Settings", self.show_game_settings),
            ("🔬 Complexity Analysis", self.show_complexity_analysis),
            ("❌ Exit", self.root.quit)
        ]
        
        for text, command in menu_buttons:
            btn = tk.Button(
                button_frame, text=text, command=command,
                font=("Arial", 14, "bold"), bg='#2c3e50', fg='white',
                activebackground='#34495e', padx=20, pady=12,
                cursor="hand2", relief=tk.RAISED, bd=3,
                width=25
            )
            btn.pack(pady=8)
        
        # Game statistics
        stats_frame = tk.Frame(scrollable_frame, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        stats_frame.pack(pady=30, padx=50, fill=tk.X)
        
        # Get statistics
        try:
            self.cursor.execute("SELECT COUNT(*) FROM game_history")
            total_games = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT COUNT(DISTINCT player_id) FROM game_history")
            unique_players = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT COUNT(*) FROM algorithm_performance")
            algorithm_runs = self.cursor.fetchone()[0] or 0
            
            stats_text = f"🎮 Total Games: {total_games} | 👥 Players: {unique_players} | 🧮 Algorithm Runs: {algorithm_runs}"
            tk.Label(
                stats_frame, text=stats_text,
                font=("Arial", 12), bg='#2c3e50', fg='#ecf0f1'
            ).pack(pady=10)
        except sqlite3.Error:
            stats_text = "🎮 Database Statistics Unavailable"
            tk.Label(
                stats_frame, text=stats_text,
                font=("Arial", 12), bg='#2c3e50', fg='#ecf0f1'
            ).pack(pady=10)
        
        # Version info
        tk.Label(
            scrollable_frame, text="Version 2.0 | Three Algorithms Edition | Performance Chart Added",
            font=("Arial", 10), bg='#1e3d59', fg='#7f8c8d'
        ).pack(side=tk.BOTTOM, pady=20)
    
    def animate_title(self):
        #Animate title color#
        try:
            colors = ['#4ECDC4', '#45B7D1', '#FF6B6B', '#96CEB4', '#FFEAA7']
            self.title_label.config(fg=colors[self.title_color_index])
            self.title_color_index = (self.title_color_index + 1) % len(colors)
            
            # Schedule next animation
            self.title_animation_id = self.root.after(1000, self.animate_title)
        except (tk.TclError, AttributeError):
            # Widget has been destroyed, stop animation
            self.title_animation_id = None
    
    def show_instructions(self):
        #Show game instructions
        instructions = tk.Toplevel(self.root)
        instructions.title("How to Play")
        instructions.geometry("700x700")
        instructions.configure(bg='#1e3d59')
        
        # Center the window
        instructions.update_idletasks()
        width = instructions.winfo_width()
        height = instructions.winfo_height()
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        instructions.geometry(f"{width}x{height}+{x}+{y}")
        
        tk.Label(
            instructions, text="📖 How to Play TSP Game",
            font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
        ).pack(pady=20)
        
        text_frame = tk.Frame(instructions, bg='#2c3e50')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        instruction_text = """
        🎯 Game Objective:
        
        Find the shortest route that starts from the HOME city,
        visits all USER-SELECTED cities exactly once, and returns to
        the HOME city.
        
        📝 Game Rules:
        
        1. HOME city is randomly selected (shown in gold)
        2. FIRST: Click to select cities you want to visit
        3. THEN: Click "Start Game" to begin route building
        4. Click on cities to build your route
        5. Route must start and end at HOME city
        6. Route must visit all selected cities
        7. Each city can be visited only once
        
        🎮 PLAY PHASE (NEW!):
        
        • After building your route, click "Play" button
        • Watch THREE algorithms evaluate your path:
          1. Recursive Backtracking (checks all paths)
          2. Iterative Validation (step-by-step check)
          3. Nearest Neighbor (greedy approximation)
        • See how your route compares to each algorithm
        
        🧮 THREE Main Algorithms Used:
        
        • Brute Force - Checks all permutations (optimal)
        • Nearest Neighbor - Greedy heuristic
        • Genetic Algorithm - Evolutionary approach
        
        🏆 Scoring:
        
        • Score is saved ONLY when you find optimal route
        • Distance between cities: 50-100 km
        • You must select cities to visit first
        
        ⚠️ IMPORTANT:
        
        • Only selected cities can be visited
        • Unselected cities are disabled after Start Game
        • Click "Play" to evaluate your completed route
        
        💡 Tips:
        
        • Select cities that are close together
        • Try different starting paths
        • Use algorithm hints
        • Use the Play feature to test your route
        """
        
        text_widget = tk.Text(
            text_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
            font=("Arial", 12), padx=10, pady=10, relief=tk.FLAT
        )
        text_widget.insert(tk.END, instruction_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            instructions, text="Close",
            command=instructions.destroy, font=("Arial", 14),
            bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
        ).pack(pady=20)
    
    def show_algorithm_comparison(self):
        #Show algorithm comparison from database
        try:
            # Fetch algorithm performance data
            self.cursor.execute('''
                SELECT algorithm_name, 
                       AVG(execution_time_ms) as avg_time,
                       AVG(distance) as avg_distance,
                       COUNT(*) as runs
                FROM algorithm_performance
                GROUP BY algorithm_name
                ORDER BY avg_distance
            ''')
            
            results = self.cursor.fetchall()
            
            # Create window
            comp_window = tk.Toplevel(self.root)
            comp_window.title("Algorithm Comparison")
            comp_window.geometry("800x600")
            comp_window.configure(bg='#1e3d59')
            
            # Center the window
            comp_window.update_idletasks()
            width = comp_window.winfo_width()
            height = comp_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            comp_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                comp_window, text="📊 Algorithm Comparison (Historical Data)",
                font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=20)
            
            if results:
                # Create frame for treeview
                tree_frame = tk.Frame(comp_window, bg='#2c3e50')
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                # Treeview
                tree = ttk.Treeview(
                    tree_frame,
                    columns=("Algorithm", "Avg Time (ms)", "Avg Distance (km)", "Runs"),
                    show="headings",
                    height=10
                )
                
                # Define columns
                tree.heading("Algorithm", text="Algorithm")
                tree.heading("Avg Time (ms)", text="Avg Time (ms)")
                tree.heading("Avg Distance (km)", text="Avg Distance (km)")
                tree.heading("Runs", text="Runs")
                
                tree.column("Algorithm", width=150)
                tree.column("Avg Time (ms)", width=150, anchor=tk.CENTER)
                tree.column("Avg Distance (km)", width=150, anchor=tk.CENTER)
                tree.column("Runs", width=100, anchor=tk.CENTER)
                
                # Add data
                for row in results:
                    tree.insert("", tk.END, values=(
                        row[0].replace('_', ' ').title(),
                        f"{row[1]:.2f}",
                        f"{row[2]:.2f}",
                        row[3]
                    ))
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    comp_window, text="No algorithm data available yet.",
                    font=("Arial", 16), bg='#1e3d59', fg='#ecf0f1'
                ).pack(pady=100)
            
            # Close button
            tk.Button(
                comp_window, text="Close",
                command=comp_window.destroy, font=("Arial", 14),
                bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to fetch algorithm data: {e}")
    
    def show_algorithm_performance_chart(self):
        """Show chart of algorithm performance over 15 game rounds"""
        try:
            # Fetch algorithm performance data for last 15 games
            self.cursor.execute('''
                SELECT 
                    gh.game_date,
                    ap.algorithm_name,
                    ap.execution_time_ms,
                    ap.distance
                FROM algorithm_performance ap
                JOIN game_history gh ON ap.game_id = gh.game_id
                WHERE ap.algorithm_name IN ('brute_force', 'nearest_neighbor', 'genetic_algorithm')
                ORDER BY gh.game_date DESC
                LIMIT 45  -- 15 games * 3 algorithms
            ''')
            
            results = self.cursor.fetchall()
            
            if not results:
                messagebox.showinfo("No Data", "No algorithm performance data available yet.")
                return
            
            # Process data
            data = {}
            dates = []
            
            for game_date, algorithm, time_ms, distance in results:
                date_str = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S').strftime('%m-%d %H:%M')
                
                if date_str not in dates:
                    dates.append(date_str)
                
                if algorithm not in data:
                    data[algorithm] = {'times': [], 'distances': []}
                
                data[algorithm]['times'].append(time_ms)
                data[algorithm]['distances'].append(distance)
            
            # Keep only last 15 entries (most recent games)
            dates = dates[-15:]
            for algo in data:
                data[algo]['times'] = data[algo]['times'][-15:]
                data[algo]['distances'] = data[algo]['distances'][-15:]
            
            # Create chart window
            chart_window = tk.Toplevel(self.root)
            chart_window.title("Algorithm Performance Chart (15 Rounds)")
            chart_window.geometry("1200x800")
            chart_window.configure(bg='#1e3d59')
            
            # Center the window
            chart_window.update_idletasks()
            width = chart_window.winfo_width()
            height = chart_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            chart_window.geometry(f"{width}x{height}+{x}+{y}")
            
            # Title
            tk.Label(
                chart_window, text="📊 Algorithm Performance Chart",
                font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=20)
            
            # Create notebook for multiple charts
            notebook = ttk.Notebook(chart_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab 1: Execution Time Chart
            time_frame = tk.Frame(notebook, bg='white')
            notebook.add(time_frame, text="⏱️ Execution Time")
            
            # Create figure for execution time
            fig_time, ax_time = plt.subplots(figsize=(10, 5))
            fig_time.patch.set_facecolor('#2c3e50')
            ax_time.set_facecolor('#ecf0f1')
            
            # Plot data for each algorithm
            colors = {
                'brute_force': '#E74C3C',
                'nearest_neighbor': '#3498DB',
                'genetic_algorithm': '#27AE60'
            }
            
            algorithm_names = {
                'brute_force': 'Brute Force',
                'nearest_neighbor': 'Nearest Neighbor',
                'genetic_algorithm': 'Genetic Algorithm'
            }
            
            x = np.arange(len(dates))
            width = 0.25
            
            for i, (algo, values) in enumerate(data.items()):
                if values['times']:
                    ax_time.plot(x, values['times'], 
                               label=algorithm_names[algo], 
                               color=colors[algo], 
                               linewidth=3,
                               marker='o',
                               markersize=8)
            
            ax_time.set_xlabel('Game Round', fontsize=12, fontweight='bold')
            ax_time.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
            ax_time.set_title('Algorithm Execution Time Over 15 Rounds', fontsize=14, fontweight='bold', pad=20)
            ax_time.set_xticks(x)
            ax_time.set_xticklabels(dates, rotation=45, ha='right')
            ax_time.legend()
            ax_time.grid(True, alpha=0.3)
            
            # Embed chart in tkinter
            canvas_time = FigureCanvasTkAgg(fig_time, master=time_frame)
            canvas_time.draw()
            canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab 2: Distance Comparison Chart
            distance_frame = tk.Frame(notebook, bg='white')
            notebook.add(distance_frame, text="📏 Distance Comparison")
            
            # Create figure for distances
            fig_dist, ax_dist = plt.subplots(figsize=(10, 5))
            fig_dist.patch.set_facecolor('#2c3e50')
            ax_dist.set_facecolor('#ecf0f1')
            
            # Bar chart for average distances
            algorithms = list(data.keys())
            avg_distances = []
            std_distances = []
            
            for algo in algorithms:
                if data[algo]['distances']:
                    distances = data[algo]['distances']
                    avg_distances.append(np.mean(distances))
                    std_distances.append(np.std(distances))
            
            # Create bar chart
            x_pos = np.arange(len(algorithms))
            bars = ax_dist.bar(x_pos, avg_distances, 
                             yerr=std_distances,
                             capsize=10,
                             color=[colors[algo] for algo in algorithms],
                             alpha=0.8)
            
            # Add value labels on bars
            for i, (bar, avg) in enumerate(zip(bars, avg_distances)):
                height = bar.get_height()
                ax_dist.text(bar.get_x() + bar.get_width()/2., height + 5,
                           f'{avg:.1f} km', ha='center', va='bottom',
                           fontweight='bold')
            
            ax_dist.set_xlabel('Algorithm', fontsize=12, fontweight='bold')
            ax_dist.set_ylabel('Average Distance (km)', fontsize=12, fontweight='bold')
            ax_dist.set_title('Average Route Distance by Algorithm', fontsize=14, fontweight='bold', pad=20)
            ax_dist.set_xticks(x_pos)
            ax_dist.set_xticklabels([algorithm_names[algo] for algo in algorithms])
            ax_dist.grid(True, alpha=0.3, axis='y')
            
            # Embed chart in tkinter
            canvas_dist = FigureCanvasTkAgg(fig_dist, master=distance_frame)
            canvas_dist.draw()
            canvas_dist.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab 3: Performance Summary Table
            table_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(table_frame, text="📋 Performance Summary")
            
            # Create performance summary
            summary_text = "📊 PERFORMANCE SUMMARY (Last 15 Rounds)\n\n"
            summary_text += "=" * 60 + "\n\n"
            
            for algo in algorithms:
                if data[algo]['times'] and data[algo]['distances']:
                    times = data[algo]['times']
                    distances = data[algo]['distances']
                    
                    summary_text += f"🔹 {algorithm_names[algo].upper()}:\n"
                    summary_text += f"   • Avg Time: {np.mean(times):.2f} ms\n"
                    summary_text += f"   • Avg Distance: {np.mean(distances):.2f} km\n"
                    summary_text += f"   • Best Distance: {min(distances):.2f} km\n"
                    summary_text += f"   • Worst Distance: {max(distances):.2f} km\n"
                    summary_text += f"   • Success Rate: {100 if all(t > 0 for t in times) else 0}%\n\n"
            
            # Add comparison analysis
            summary_text += "=" * 60 + "\n"
            summary_text += "📈 COMPARATIVE ANALYSIS:\n\n"
            
            # Find best algorithm for time and distance
            if data:
                # Find fastest algorithm
                avg_times = {algo: np.mean(data[algo]['times']) for algo in algorithms if data[algo]['times']}
                fastest_algo = min(avg_times, key=avg_times.get) if avg_times else None
                
                # Find most efficient algorithm (shortest distance)
                avg_dists = {algo: np.mean(data[algo]['distances']) for algo in algorithms if data[algo]['distances']}
                efficient_algo = min(avg_dists, key=avg_dists.get) if avg_dists else None
                
                if fastest_algo:
                    summary_text += f"• ⚡ Fastest Algorithm: {algorithm_names[fastest_algo]}\n"
                
                if efficient_algo:
                    summary_text += f"• 🎯 Most Efficient: {algorithm_names[efficient_algo]}\n"
                
                # Calculate time savings
                if fastest_algo and efficient_algo and fastest_algo != efficient_algo:
                    fastest_time = avg_times[fastest_algo]
                    efficient_time = avg_times[efficient_algo]
                    time_diff = efficient_time - fastest_time
                    summary_text += f"• ⏱️  Time Trade-off: {algorithm_names[efficient_algo]} is {time_diff:.1f}ms slower but more accurate\n"
            
            # Add recommendations
            summary_text += "\n" + "=" * 60 + "\n"
            summary_text += "💡 RECOMMENDATIONS:\n\n"
            summary_text += "• For small cities (≤8): Use Brute Force for optimal solution\n"
            summary_text += "• For speed: Use Nearest Neighbor (fastest)\n"
            summary_text += "• For balance: Use Genetic Algorithm (good speed & accuracy)\n"
            summary_text += "• For learning: Compare all three in Play Phase\n"
            
            # Create text widget for summary
            text_widget = tk.Text(
                table_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
                font=("Courier New", 11), padx=15, pady=15, relief=tk.FLAT
            )
            text_widget.insert(tk.END, summary_text)
            text_widget.config(state=tk.DISABLED)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(table_frame, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Tab 4: Database Statistics
            stats_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(stats_frame, text="🗄️ Database Output")
            
            # Fetch database statistics
            self.cursor.execute('''
                SELECT 
                    COUNT(DISTINCT game_id) as total_games,
                    COUNT(*) as total_runs,
                    AVG(execution_time_ms) as avg_time,
                    AVG(distance) as avg_distance
                FROM algorithm_performance
            ''')
            
            db_stats = self.cursor.fetchone()
            
            # Fetch per-algorithm statistics
            self.cursor.execute('''
                SELECT 
                    algorithm_name,
                    COUNT(*) as runs,
                    AVG(execution_time_ms) as avg_time,
                    AVG(distance) as avg_distance,
                    MIN(distance) as best_distance,
                    MAX(distance) as worst_distance
                FROM algorithm_performance
                GROUP BY algorithm_name
                ORDER BY avg_distance
            ''')
            
            algo_stats = self.cursor.fetchall()
            
            # Create database output display
            db_text = "🗄️ DATABASE OUTPUT SCREENSHOT\n\n"
            db_text += "=" * 60 + "\n\n"
            
            if db_stats:
                total_games, total_runs, avg_time, avg_distance = db_stats
                db_text += f"📈 OVERALL STATISTICS:\n"
                db_text += f"   • Total Games: {total_games}\n"
                db_text += f"   • Algorithm Runs: {total_runs}\n"
                db_text += f"   • Avg Time: {avg_time:.2f} ms\n"
                db_text += f"   • Avg Distance: {avg_distance:.2f} km\n\n"
            
            db_text += "=" * 60 + "\n\n"
            db_text += "🔍 ALGORITHM-SPECIFIC STATISTICS:\n\n"
            
            # Create table-like display
            header = f"{'ALGORITHM':<25} {'RUNS':<8} {'AVG TIME':<12} {'AVG DIST':<12} {'BEST':<10} {'WORST':<10}\n"
            separator = "-" * 80 + "\n"
            db_text += header
            db_text += separator
            
            for row in algo_stats:
                algo_name, runs, avg_time, avg_dist, best_dist, worst_dist = row
                # Format algorithm name
                display_name = algo_name.replace('_', ' ').title()
                if len(display_name) > 24:
                    display_name = display_name[:21] + "..."
                
                db_text += f"{display_name:<25} {runs:<8} {avg_time:<12.1f} {avg_dist:<12.1f} {best_dist:<10.1f} {worst_dist:<10.1f}\n"
            
            db_text += "\n" + "=" * 60 + "\n\n"
            db_text += "📅 LAST 15 ROUNDS DETAIL:\n\n"
            
            # Show detailed recent data
            self.cursor.execute('''
                SELECT 
                    gh.game_date,
                    ap.algorithm_name,
                    ap.execution_time_ms,
                    ap.distance
                FROM algorithm_performance ap
                JOIN game_history gh ON ap.game_id = gh.game_id
                ORDER BY gh.game_date DESC
                LIMIT 15
            ''')
            
            recent_runs = self.cursor.fetchall()
            
            for game_date, algorithm, time_ms, distance in recent_runs:
                date_str = datetime.strptime(game_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                algo_display = algorithm.replace('_', ' ').title()[:15]
                db_text += f"[{date_str}] {algo_display:<20} {time_ms:>8.1f}ms {distance:>8.1f}km\n"
            
            # Create text widget for database output
            db_text_widget = tk.Text(
                stats_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
                font=("Courier New", 10), padx=15, pady=15, relief=tk.FLAT
            )
            db_text_widget.insert(tk.END, db_text)
            db_text_widget.config(state=tk.DISABLED)
            
            # Add scrollbar
            db_scrollbar = tk.Scrollbar(stats_frame, command=db_text_widget.yview)
            db_text_widget.configure(yscrollcommand=db_scrollbar.set)
            
            db_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            db_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Tab 5: Export Options
            export_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(export_frame, text="💾 Export Data")
            
            tk.Label(
                export_frame, text="Export Performance Data",
                font=("Arial", 16, "bold"), bg='#2c3e50', fg='#4ECDC4'
            ).pack(pady=20)
            
            # Export buttons
            export_buttons_frame = tk.Frame(export_frame, bg='#2c3e50')
            export_buttons_frame.pack(pady=20)
            
            def export_to_csv():
                """Export data to CSV file"""
                try:
                    # Fetch all performance data
                    self.cursor.execute('''
                        SELECT 
                            gh.game_date,
                            ap.algorithm_name,
                            ap.execution_time_ms,
                            ap.distance,
                            ap.complexity_analysis
                        FROM algorithm_performance ap
                        JOIN game_history gh ON ap.game_id = gh.game_id
                        ORDER BY gh.game_date
                    ''')
                    
                    all_data = self.cursor.fetchall()
                    
                    if all_data:
                        # Create DataFrame
                        df = pd.DataFrame(all_data, columns=[
                            'game_date', 'algorithm_name', 'execution_time_ms', 
                            'distance', 'complexity_analysis'
                        ])
                        
                        # Generate filename with timestamp
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"tsp_performance_{timestamp}.csv"
                        
                        # Export to CSV
                        df.to_csv(filename, index=False)
                        messagebox.showinfo("Export Successful", 
                                          f"Data exported to:\n{filename}\n\n"
                                          f"Total records: {len(df)}")
                    else:
                        messagebox.showinfo("No Data", "No performance data to export.")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export data: {e}")
            
            def export_summary_report():
                """Export summary report as text file"""
                try:
                    # Create comprehensive report
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    report = f"TSP ALGORITHM PERFORMANCE REPORT\n"
                    report += f"Generated: {timestamp}\n"
                    report += "=" * 60 + "\n\n"
                    
                    # Add overall statistics
                    self.cursor.execute('''
                        SELECT 
                            COUNT(DISTINCT game_id) as total_games,
                            COUNT(*) as total_runs,
                            AVG(execution_time_ms) as avg_time,
                            AVG(distance) as avg_distance
                        FROM algorithm_performance
                    ''')
                    
                    stats = self.cursor.fetchone()
                    if stats:
                        total_games, total_runs, avg_time, avg_distance = stats
                        report += "OVERALL STATISTICS:\n"
                        report += f"  Total Games: {total_games}\n"
                        report += f"  Total Algorithm Runs: {total_runs}\n"
                        report += f"  Average Time: {avg_time:.2f} ms\n"
                        report += f"  Average Distance: {avg_distance:.2f} km\n\n"
                    
                    # Add algorithm comparison
                    report += "ALGORITHM COMPARISON:\n"
                    self.cursor.execute('''
                        SELECT 
                            algorithm_name,
                            COUNT(*) as runs,
                            AVG(execution_time_ms) as avg_time,
                            AVG(distance) as avg_distance,
                            MIN(execution_time_ms) as best_time,
                            MIN(distance) as best_distance
                        FROM algorithm_performance
                        GROUP BY algorithm_name
                        ORDER BY avg_distance
                    ''')
                    
                    algo_comparison = self.cursor.fetchall()
                    for algo_name, runs, avg_time, avg_dist, best_time, best_dist in algo_comparison:
                        display_name = algo_name.replace('_', ' ').title()
                        report += f"\n{display_name}:\n"
                        report += f"  Runs: {runs}\n"
                        report += f"  Avg Time: {avg_time:.2f} ms\n"
                        report += f"  Avg Distance: {avg_dist:.2f} km\n"
                        report += f"  Best Time: {best_time:.2f} ms\n"
                        report += f"  Best Distance: {best_dist:.2f} km\n"
                    
                    # Add recommendations
                    report += "\n" + "=" * 60 + "\n"
                    report += "RECOMMENDATIONS:\n\n"
                    report += "1. For optimal solutions (≤8 cities): Use Brute Force\n"
                    report += "2. For fastest results: Use Nearest Neighbor\n"
                    report += "3. For balance: Use Genetic Algorithm\n"
                    report += "4. For learning: Use Play Phase to compare all algorithms\n"
                    
                    # Save report
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"tsp_report_{timestamp}.txt"
                    
                    with open(filename, 'w') as f:
                        f.write(report)
                    
                    messagebox.showinfo("Report Exported", 
                                      f"Report saved to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"Failed to export report: {e}")
            
            def generate_performance_chart_image():
                """Generate and save chart as image"""
                try:
                    # Create a comprehensive chart
                    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
                    fig.suptitle('TSP Algorithm Performance Analysis', fontsize=16, fontweight='bold')
                    
                    # Chart 1: Execution Time Trend
                    ax1 = axes[0, 0]
                    for algo, values in data.items():
                        if values['times']:
                            ax1.plot(values['times'], 
                                   label=algorithm_names[algo],
                                   color=colors[algo],
                                   linewidth=2)
                    ax1.set_title('Execution Time Trend')
                    ax1.set_xlabel('Game Round')
                    ax1.set_ylabel('Time (ms)')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    # Chart 2: Distance Comparison
                    ax2 = axes[0, 1]
                    algo_labels = [algorithm_names[algo] for algo in algorithms]
                    avg_dists = [np.mean(data[algo]['distances']) for algo in algorithms if data[algo]['distances']]
                    bar_colors = [colors[algo] for algo in algorithms if data[algo]['distances']]
                    ax2.bar(range(len(avg_dists)), avg_dists, color=bar_colors, alpha=0.7)
                    ax2.set_title('Average Distance Comparison')
                    ax2.set_ylabel('Distance (km)')
                    ax2.set_xticks(range(len(algo_labels)))
                    ax2.set_xticklabels(algo_labels, rotation=45)
                    
                    # Chart 3: Success Rate
                    ax3 = axes[1, 0]
                    success_rates = []
                    for algo in algorithms:
                        if data[algo]['times']:
                            success_rate = 100 if all(t > 0 for t in data[algo]['times']) else 0
                            success_rates.append(success_rate)
                    ax3.pie(success_rates, labels=algo_labels, 
                           colors=bar_colors, autopct='%1.1f%%')
                    ax3.set_title('Algorithm Success Rate')
                    
                    # Chart 4: Time vs Distance Scatter
                    ax4 = axes[1, 1]
                    for algo in algorithms:
                        if data[algo]['times'] and data[algo]['distances']:
                            ax4.scatter(data[algo]['times'], data[algo]['distances'],
                                      color=colors[algo],
                                      label=algorithm_names[algo],
                                      alpha=0.6)
                    ax4.set_title('Time vs Distance')
                    ax4.set_xlabel('Time (ms)')
                    ax4.set_ylabel('Distance (km)')
                    ax4.legend()
                    ax4.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    
                    # Save image
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"tsp_chart_{timestamp}.png"
                    plt.savefig(filename, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    messagebox.showinfo("Chart Saved", 
                                      f"Performance chart saved to:\n{filename}")
                except Exception as e:
                    messagebox.showerror("Chart Error", f"Failed to save chart: {e}")
            
            # Create export buttons
            export_functions = [
                ("📊 Export to CSV", export_to_csv),
                ("📄 Export Report", export_summary_report),
                ("🖼️ Save Chart as Image", generate_performance_chart_image),
            ]
            
            for text, func in export_functions:
                btn = tk.Button(
                    export_buttons_frame, text=text, command=func,
                    font=("Arial", 12), bg='#3498db', fg='white',
                    padx=20, pady=10, cursor="hand2", width=25
                )
                btn.pack(pady=10)
            
            # Information text
            info_text = "\n📝 Export Information:\n\n"
            info_text += "• CSV Export: Full performance data in spreadsheet format\n"
            info_text += "• Report Export: Summary report in text format\n"
            info_text += "• Chart Export: Performance charts as PNG image\n"
            info_text += "• Files are saved in the current directory\n"
            
            info_label = tk.Label(
                export_frame, text=info_text,
                font=("Arial", 11), bg='#2c3e50', fg='#bdc3c7',
                justify=tk.LEFT
            )
            info_label.pack(pady=20)
            
            # Control buttons at bottom
            button_frame = tk.Frame(chart_window, bg='#1e3d59')
            button_frame.pack(pady=10)
            
            tk.Button(
                button_frame, text="🔄 Refresh Data",
                command=lambda: [chart_window.destroy(), self.show_algorithm_performance_chart()],
                font=("Arial", 12), bg='#3498db', fg='white',
                padx=20, pady=10, cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame, text="📋 Copy Summary",
                command=lambda: self.copy_to_clipboard(summary_text),
                font=("Arial", 12), bg='#9b59b6', fg='white',
                padx=20, pady=10, cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_frame, text="❌ Close",
                command=chart_window.destroy,
                font=("Arial", 12), bg='#e74c3c', fg='white',
                padx=20, pady=10, cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Chart Error", f"Failed to display chart: {e}\n\nPlease install required packages:\npip install matplotlib numpy pandas")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy to clipboard: {e}")
    
    def setup_player_selection(self):
        """Show player selection screen"""
        self.clear_window()
        
        selection_frame = tk.Frame(self.root, bg='#1e3d59')
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            selection_frame, text="Player Setup",
            font=("Impact", 36, "bold"), bg='#1e3d59', fg='#4ECDC4'
        ).pack(pady=(50, 30))
        
        # Player name entry
        name_frame = tk.Frame(selection_frame, bg='#2c3e50', relief=tk.RAISED, bd=3)
        name_frame.pack(pady=20, padx=100, ipadx=20, ipady=20)
        
        tk.Label(
            name_frame, text="Enter Your Name:",
            font=("Arial", 18, "bold"), bg='#2c3e50', fg='#f7dc6f'
        ).pack(pady=10)
        
        self.name_entry = tk.Entry(name_frame, font=("Arial", 16), width=30)
        self.name_entry.pack(pady=20, padx=20)
        self.name_entry.focus_set()
        
        # Start button
        tk.Button(
            selection_frame, text="🎮 Start Game",
            command=self.start_new_game, font=("Arial", 18, "bold"),
            bg='#27ae60', fg='white', padx=40, pady=20, cursor="hand2"
        ).pack(pady=30)
        
        # Back button
        tk.Button(
            selection_frame, text="← Back to Menu",
            command=self.setup_main_menu, font=("Arial", 14),
            bg='#e67e22', fg='white', padx=20, pady=10, cursor="hand2"
        ).pack(pady=20)
    
    def start_new_game(self):
        """Start a new game with player name"""
        try:
            player_name = self.name_entry.get().strip()
            if not player_name:
                player_name = "Player"
            
            if len(player_name) > 50:
                messagebox.showwarning("Name Too Long", "Player name must be less than 50 characters.")
                return
            
            self.player_name = player_name
            self.player_id = self.get_or_create_player(player_name)
            self.game_id = f"TSP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate new game
            self.generate_cities()
            self.setup_game_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {e}")
    
    def get_or_create_player(self, name):
        """Get existing player or create new one"""
        try:
            self.cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
            result = self.cursor.fetchone()
            
            if result:
                return result[0]
            else:
                self.cursor.execute(
                    "INSERT INTO players (name) VALUES (?)",
                    (name,)
                )
                self.conn.commit()
                return self.cursor.lastrowid
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to get/create player: {e}")
            return None
    
    def setup_game_ui(self):
        """Setup the main game interface with better layout"""
        self.clear_window()
        
        # Main container using PanedWindow for resizable split
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#1e3d59', sashwidth=8, sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # ========== LEFT PANEL - Scrollable (40% of width) ==========
        left_container = tk.Frame(main_paned, bg='#1e3d59')
        main_paned.add(left_container, minsize=400, width=int(self.window_width * 0.4))
        
        # Create canvas and scrollbar for left panel
        left_canvas = tk.Canvas(left_container, bg='#2c3e50', highlightthickness=0)
        left_scrollbar = tk.Scrollbar(left_container, orient=tk.VERTICAL, command=left_canvas.yview)
        scrollable_left_frame = tk.Frame(left_canvas, bg='#2c3e50')
        
        scrollable_left_frame.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        left_canvas.create_window((0, 0), window=scrollable_left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Pack canvas and scrollbar
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        
        # Make mouse wheel scroll work on the left panel
        def on_mouse_wheel_left(event):
            left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        left_canvas.bind_all("<MouseWheel>", on_mouse_wheel_left)
        
        # ========== RIGHT PANEL - Game board (60% of width) ==========
        right_panel = tk.Frame(main_paned, bg='#d5dbdb')
        main_paned.add(right_panel, minsize=600)
        
        # ========== LEFT PANEL CONTENT ==========
        
        # Player info at top
        player_info_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        player_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            player_info_frame, text=f"Player: {self.player_name}",
            font=("Arial", 14, "bold"), bg='#34495e', fg='#4ECDC4'
        ).pack(pady=5)
        
        # Game title
        tk.Label(
            scrollable_left_frame, text="TSP Challenge",
            font=("Impact", 20, "bold"), bg='#2c3e50', fg='#f7dc6f'
        ).pack(pady=(10, 5))
        
        # Home city display
        home_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        home_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            home_frame, text="🏠 HOME CITY",
            font=("Arial", 14, "bold"), bg='#34495e', fg='#FFD700'
        ).pack(pady=5)
        
        tk.Label(
            home_frame, text=self.home_city.name,
            font=("Arial", 24, "bold"), bg='#34495e', fg='#FFD700'
        ).pack(pady=10)
        
        # City selection status
        selection_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        selection_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            selection_frame, text="📍 SELECT CITIES TO VISIT",
            font=("Arial", 12, "bold"), bg='#34495e', fg='#4ECDC4'
        ).pack(pady=5)
        
        self.selection_status_label = tk.Label(
            selection_frame, 
            text="Click cities on the map to select them" if self.city_selection_mode else f"Selected {len(self.selected_cities)} cities",
            font=("Arial", 11), bg='#34495e', fg='white',
            wraplength=350, justify=tk.LEFT
        )
        self.selection_status_label.pack(pady=5, padx=10)
        
        # Selected cities display
        selected_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        selected_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            selected_frame, text="✅ YOUR SELECTED CITIES",
            font=("Arial", 12, "bold"), bg='#34495e', fg='#96CEB4'
        ).pack(pady=5)
        
        self.selected_cities_label = tk.Label(
            selected_frame, 
            text="None selected" if not self.user_selected_cities else ", ".join([c.name for c in self.user_selected_cities]),
            font=("Arial", 11), bg='#34495e', fg='white',
            wraplength=350, justify=tk.LEFT
        )
        self.selected_cities_label.pack(pady=5, padx=10)
        
        # Control buttons
        control_frame = tk.Frame(scrollable_left_frame, bg='#2c3e50')
        control_frame.pack(pady=10, padx=15, fill=tk.X)
        
        self.start_game_btn = tk.Button(
            control_frame, text="🚀 Start Game", command=self.start_game_phase,
            font=("Arial", 12, "bold"), bg='#27ae60', fg='white',
            padx=15, pady=8, cursor="hand2", state=tk.DISABLED, width=15
        )
        self.start_game_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.clear_selection_btn = tk.Button(
            control_frame, text="🔄 Clear", command=self.clear_selection,
            font=("Arial", 12), bg='#e67e22', fg='white',
            padx=15, pady=8, cursor="hand2", width=10
        )
        self.clear_selection_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Current route display
        route_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        route_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            route_frame, text="🛣️ CURRENT ROUTE",
            font=("Arial", 12, "bold"), bg='#34495e', fg='#FF6B6B'
        ).pack(pady=5)
        
        self.route_label = tk.Label(
            route_frame, 
            text="Start by selecting cities, then click 'Start Game'" if self.city_selection_mode else "→ ".join(self.current_route) if self.current_route else "Build your route",
            font=("Arial", 11), bg='#34495e', fg='white',
            wraplength=350, justify=tk.LEFT
        )
        self.route_label.pack(pady=5, padx=10)
        
        # Distance display
        distance_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        distance_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            distance_frame, text="📏 TOTAL DISTANCE",
            font=("Arial", 12, "bold"), bg='#34495e', fg='#96CEB4'
        ).pack(pady=5)
        
        self.distance_label = tk.Label(
            distance_frame, text="0 km",
            font=("Arial", 18, "bold"), bg='#34495e', fg='#96CEB4'
        )
        self.distance_label.pack(pady=10)
        
        # PLAY PHASE section
        play_phase_frame = tk.Frame(scrollable_left_frame, bg='#2c3e50')
        play_phase_frame.pack(pady=15, padx=15, fill=tk.X)
        
        tk.Label(
            play_phase_frame, text="🎮 PLAY PHASE",
            font=("Arial", 14, "bold"), bg='#2c3e50', fg='#9B59B6'
        ).pack(pady=5)
        
        # PLAY button
        self.play_btn = tk.Button(
            play_phase_frame, text="▶ Play", command=self.start_play_phase,
            font=("Arial", 14, "bold"), bg='#9B59B6', fg='white',
            padx=20, pady=10, cursor="hand2", state=tk.DISABLED, width=15
        )
        self.play_btn.pack(pady=5)
        
        # Delay slider
        delay_frame = tk.Frame(play_phase_frame, bg='#2c3e50')
        delay_frame.pack(pady=5, fill=tk.X)
        
        tk.Label(
            delay_frame, text="DELAY:", 
            font=("Arial", 11), bg='#2c3e50', fg='white'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.delay_slider = tk.Scale(
            delay_frame, from_=0, to=1000, orient=tk.HORIZONTAL,
            length=200, bg='#2c3e50', fg='white',
            troughcolor='#34495e', highlightbackground='#2c3e50',
            sliderlength=20, showvalue=False
        )
        self.delay_slider.set(100)
        self.delay_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            delay_frame, text="Speed",
            font=("Arial", 9), bg='#2c3e50', fg='#7f8c8d'
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Play Phase status
        play_status_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        play_status_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(
            play_status_frame, text="⚡ PLAY PHASE STATUS",
            font=("Arial", 11, "bold"), bg='#34495e', fg='#9B59B6'
        ).pack(pady=5)
        
        self.play_status_label = tk.Label(
            play_status_frame, 
            text="Build your route first" if not self.city_selection_mode and len(self.current_route) < 3 else "Ready to play!",
            font=("Arial", 10), bg='#34495e', fg='white',
            wraplength=350, justify=tk.LEFT
        )
        self.play_status_label.pack(pady=5, padx=10)
        
        # Route building buttons
        route_control_frame = tk.Frame(scrollable_left_frame, bg='#2c3e50')
        route_control_frame.pack(pady=10, padx=15, fill=tk.X)
        
        self.clear_route_btn = tk.Button(
            route_control_frame, text="🔄 Clear Route", command=self.clear_route,
            font=("Arial", 12), bg='#e67e22', fg='white',
            padx=10, pady=8, cursor="hand2", state=tk.DISABLED, width=12
        )
        self.clear_route_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.submit_btn = tk.Button(
            route_control_frame, text="✅ Submit", command=self.submit_solution,
            font=("Arial", 12, "bold"), bg='#27ae60', fg='white',
            padx=10, pady=8, cursor="hand2", state=tk.DISABLED, width=12
        )
        self.submit_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # Algorithm hints button
        self.hints_btn = tk.Button(
            scrollable_left_frame, text="🤖 Algorithm Hints", command=self.show_algorithm_hints,
            font=("Arial", 12), bg='#3498db', fg='white',
            padx=10, pady=8, cursor="hand2", state=tk.DISABLED, width=20
        )
        self.hints_btn.pack(pady=5, padx=15, fill=tk.X)
        
        # Best distance found
        best_frame = tk.Frame(scrollable_left_frame, bg='#34495e', relief=tk.SUNKEN, bd=2)
        best_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            best_frame, text="🥇 BEST FOUND",
            font=("Arial", 12, "bold"), bg='#34495e', fg='#FFD700'
        ).pack(pady=5)
        
        self.best_distance_label = tk.Label(
            best_frame, text="Not available yet",
            font=("Arial", 16, "bold"), bg='#34495e', fg='#FFD700'
        )
        self.best_distance_label.pack(pady=10)
        
        # Navigation buttons at bottom
        nav_frame = tk.Frame(scrollable_left_frame, bg='#2c3e50')
        nav_frame.pack(side=tk.BOTTOM, pady=10, padx=15, fill=tk.X)
        
        tk.Button(
            nav_frame, text="🔄 New Game", command=self.start_new_game,
            font=("Arial", 12), bg='#9b59b6', fg='white',
            padx=10, pady=8, cursor="hand2", width=12
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        tk.Button(
            nav_frame, text="🏠 Menu", command=self.setup_main_menu,
            font=("Arial", 12), bg='#e74c3c', fg='white',
            padx=10, pady=8, cursor="hand2", width=12
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # ========== RIGHT PANEL ==========
        
        # Board title
        board_title = tk.Frame(right_panel, bg='#154360', height=50)
        board_title.pack(fill=tk.X)
        board_title.pack_propagate(False)
        
        self.board_title_label = tk.Label(
            board_title, 
            text="SELECT CITIES TO VISIT - Click cities to select them" if self.city_selection_mode else "BUILD YOUR ROUTE - Click SELECTED cities to build route",
            font=("Impact", 16, "bold"), bg='#154360', fg='#f7dc6f'
        )
        self.board_title_label.pack(pady=15)
        
        # Legend
        legend_frame = tk.Frame(right_panel, bg='#154360')
        legend_frame.pack(fill=tk.X, pady=(5, 0))
        
        legend_text = "🏠 Home   🔵 Available   ✅ Selected   🟢 In Route   🔴 Current Path   ✖️ Disabled"
        tk.Label(
            legend_frame, text=legend_text,
            font=("Arial", 10), bg='#154360', fg='white'
        ).pack()
        
        # Play Phase legend
        play_legend_frame = tk.Frame(right_panel, bg='#154360')
        play_legend_frame.pack(fill=tk.X, pady=(0, 5))
        
        play_legend_text = "Play Phase: 🔴 Recursive Backtracking   🔵 Iterative Validation   🟢 Nearest Neighbor"
        tk.Label(
            play_legend_frame, text=play_legend_text,
            font=("Arial", 9), bg='#154360', fg='white'
        ).pack()
        
        # Create canvas container with scrollbars
        canvas_container = tk.Frame(right_panel, bg='#d5dbdb')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.game_canvas = tk.Canvas(
            canvas_container, 
            bg='#fef9e7', 
            highlightthickness=0,
            scrollregion=(0, 0, self.canvas_width, self.canvas_height)
        )
        
        # Add scrollbars
        h_scrollbar = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self.game_canvas.xview)
        v_scrollbar = tk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self.game_canvas.yview)
        
        self.game_canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Grid layout for scrollable canvas
        self.game_canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
        
        # Draw initial cities
        self.draw_cities()
        
        # Bind click events to game canvas
        self.game_canvas.bind("<Button-1>", self.city_click)
        
        # Make canvas focusable for scrolling
        self.game_canvas.bind("<Enter>", lambda e: self.game_canvas.focus_set())
        
        # Mouse wheel scrolling for right panel
        def on_mouse_wheel_right(event):
            self.game_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.game_canvas.bind_all("<MouseWheel>", on_mouse_wheel_right)
        
        # Force update of Play button state
        self.update_play_button_state()
    
    def draw_cities(self):
        """Draw all cities on the canvas with improved visuals"""
        try:
            self.game_canvas.delete("all")
            
            # Draw connections for current route (if in route building phase)
            if not self.city_selection_mode and len(self.current_route) > 1:
                for i in range(len(self.current_route) - 1):
                    city1_name = self.current_route[i]
                    city2_name = self.current_route[i + 1]
                    
                    city1 = next(c for c in self.cities if c.name == city1_name)
                    city2 = next(c for c in self.cities if c.name == city2_name)
                    
                    # Draw line with arrow
                    self.game_canvas.create_line(
                        city1.x, city1.y, city2.x, city2.y,
                        fill='#FF6B6B', width=3, 
                        arrow=tk.LAST, arrowshape=(16, 20, 6),
                        tags="route_line"
                    )
                    
                    # Add distance label midway
                    mid_x = (city1.x + city2.x) / 2
                    mid_y = (city1.y + city2.y) / 2
                    distance = self.distance_matrix.get((city1_name, city2_name), 0)
                    
                    # Draw a background for the text
                    self.game_canvas.create_rectangle(
                        mid_x - 25, mid_y - 12,
                        mid_x + 25, mid_y + 12,
                        fill='white', outline='#FF6B6B', width=1,
                        tags="distance_bg"
                    )
                    
                    self.game_canvas.create_text(
                        mid_x, mid_y,
                        text=f"{distance} km",
                        font=("Arial", 9, "bold"),
                        fill='#2c3e50',
                        tags="distance_text"
                    )
            
            # Draw all cities with better visual hierarchy
            for i, city in enumerate(self.cities):
                # Determine city properties
                is_home = (city.name == self.home_city.name)
                is_selected = city in self.user_selected_cities
                is_in_route = city.name in self.current_route
                is_enabled = self.city_selection_mode or city in self.selected_cities or city == self.home_city
                
                # City appearance based on state
                if is_home:
                    color = '#FFD700'  # Gold for home
                    radius = 28
                    border_color = '#B7950B'
                    border_width = 4
                    shadow_offset = 4
                elif is_selected and self.city_selection_mode:
                    color = '#27ae60'  # Green for selected
                    radius = 24
                    border_color = '#1e8449'
                    border_width = 3
                    shadow_offset = 3
                elif is_in_route and not self.city_selection_mode:
                    color = '#3498db'  # Blue for in route
                    radius = 22
                    border_color = '#2980b9'
                    border_width = 3
                    shadow_offset = 3
                elif not is_enabled and not self.city_selection_mode:
                    # Disabled city (not selected)
                    color = '#95A5A6'  # Light gray
                    radius = 20
                    border_color = '#7F8C8D'
                    border_width = 2
                    shadow_offset = 2
                else:
                    color = '#BDC3C7'  # Gray for available
                    radius = 20
                    border_color = '#7F8C8D'
                    border_width = 2
                    shadow_offset = 2
                
                # Draw city shadow for depth
                self.game_canvas.create_oval(
                    city.x - radius + shadow_offset, city.y - radius + shadow_offset,
                    city.x + radius + shadow_offset, city.y + radius + shadow_offset,
                    fill='#2c3e50', outline='', tags="city_shadow"
                )
                
                # Draw city circle
                self.game_canvas.create_oval(
                    city.x - radius, city.y - radius,
                    city.x + radius, city.y + radius,
                    fill=color, outline=border_color, width=border_width,
                    tags="city_circle"
                )
                
                # Draw city name
                self.game_canvas.create_text(
                    city.x, city.y,
                    text=city.name,
                    font=("Arial", 14, "bold"),
                    fill='#2c3e50',
                    tags="city_name"
                )
                
                # Add selection indicator
                if is_selected and self.city_selection_mode:
                    # Draw checkmark
                    self.game_canvas.create_text(
                        city.x, city.y + radius + 15,
                        text="✓ SELECTED",
                        font=("Arial", 10, "bold"),
                        fill='#27ae60',
                        tags="selection_indicator"
                    )
                
                # Show disabled status with X
                if not is_enabled and not self.city_selection_mode:
                    self.game_canvas.create_text(
                        city.x, city.y,
                        text="✖",
                        font=("Arial", 24, "bold"),
                        fill='#E74C3C',
                        tags="disabled_mark"
                    )
            
            # Update canvas scroll region to include all elements
            self.game_canvas.configure(scrollregion=self.game_canvas.bbox("all"))
            
        except Exception as e:
            print(f"Error drawing cities: {e}")
    
    def city_click(self, event):
        """Handle city click events"""
        if self.game_over:
            return
        
        # Adjust for canvas scrolling
        canvas_x = self.game_canvas.canvasx(event.x)
        canvas_y = self.game_canvas.canvasy(event.y)
        
        # Find clicked city
        clicked_city = None
        min_distance = float('inf')
        
        for city in self.cities:
            distance = math.sqrt((canvas_x - city.x)**2 + (canvas_y - city.y)**2)
            if distance < 30 and distance < min_distance:  # Within click radius
                clicked_city = city
                min_distance = distance
        
        if clicked_city:
            self.play_sound("click")
            
            if self.city_selection_mode:
                # City selection phase
                if clicked_city.name == self.home_city.name:
                    messagebox.showinfo("Cannot Select Home", "Home city is automatically included. Select other cities to visit.")
                    return
                
                if clicked_city in self.user_selected_cities:
                    # Deselect city
                    self.user_selected_cities.remove(clicked_city)
                else:
                    # Select city
                    if len(self.user_selected_cities) >= 8:
                        messagebox.showinfo("Maximum Reached", "You can select up to 8 cities to visit.")
                        return
                    self.user_selected_cities.append(clicked_city)
                
                # Update display
                selected_names = [city.name for city in self.user_selected_cities]
                if selected_names:
                    self.selected_cities_label.config(text=", ".join(selected_names))
                else:
                    self.selected_cities_label.config(text="None selected")
                
                # Enable/disable start game button
                if len(self.user_selected_cities) >= 1:
                    self.start_game_btn.config(state=tk.NORMAL, bg='#27ae60')
                else:
                    self.start_game_btn.config(state=tk.DISABLED, bg='#7D3C98')
                
                self.draw_cities()
            else:
                # Route building phase - ONLY allow selected cities
                if clicked_city not in self.selected_cities and clicked_city != self.home_city:
                    messagebox.showinfo("City Not Selected", 
                                      f"City {clicked_city.name} was not selected.\n"
                                      f"You can only visit: {', '.join([c.name for c in self.selected_cities])}")
                    return
                
                self.add_city_to_route(clicked_city)
    
    def start_game_phase(self):
        """Start the route building phase after city selection"""
        if not self.user_selected_cities:
            messagebox.showinfo("No Cities Selected", "Please select at least one city to visit.")
            return
        
        # Set selected cities
        self.selected_cities = self.user_selected_cities.copy()
        
        # Run algorithms to find optimal solution
        self.run_algorithms()
        
        # Update UI for route building phase
        self.city_selection_mode = False
        self.board_title_label.config(text="BUILD YOUR ROUTE - Click SELECTED cities to build route")
        
        # Update selection status
        selected_names = [c.name for c in self.selected_cities]
        self.selection_status_label.config(text=f"Selected {len(self.selected_cities)} cities: {', '.join(selected_names)}")
        
        # Enable route building buttons
        self.clear_route_btn.config(state=tk.NORMAL, bg='#e67e22')
        self.submit_btn.config(state=tk.NORMAL, bg='#27ae60')
        self.hints_btn.config(state=tk.NORMAL, bg='#3498db')
        
        # Disable selection buttons
        self.start_game_btn.config(state=tk.DISABLED, bg='#7D3C98')
        self.clear_selection_btn.config(state=tk.DISABLED, bg='#7D3C98')
        
        # Clear any existing route and start with home city
        self.current_route = [self.home_city.name]
        self.update_route_display()
        self.draw_cities()
        
        # Force update of Play button state
        self.update_play_button_state()
        
        messagebox.showinfo("Game Started", 
                          f"Game Started!\n\n"
                          f"Home: {self.home_city.name}\n"
                          f"Cities to visit: {', '.join([c.name for c in self.selected_cities])}\n\n"
                          f"Only selected cities can be visited.\n"
                          f"Build your route starting from {self.home_city.name}!")
    
    def clear_selection(self):
        """Clear selected cities"""
        self.user_selected_cities = []
        self.selected_cities_label.config(text="None selected")
        self.start_game_btn.config(state=tk.DISABLED, bg='#7D3C98')
        self.draw_cities()
    
    def add_city_to_route(self, city):
        """Add a city to the current route"""
        city_name = city.name
        
        # If route is empty, must start with home city
        if len(self.current_route) == 0:
            if city_name != self.home_city.name:
                messagebox.showinfo("Start at Home", "Route must start at the HOME city!")
                return
            self.current_route.append(city_name)
        
        # Check if trying to return to home
        elif city_name == self.home_city.name and len(self.current_route) > 1:
            # Check if all selected cities are visited
            selected_names = {city.name for city in self.selected_cities}
            visited_names = set(self.current_route)
            
            if selected_names.issubset(visited_names):
                # Complete the route by returning to home
                self.current_route.append(city_name)
                self.update_route_display()
                self.draw_cities()
                
                # Play sound and show message
                self.play_sound("correct")
                distance = self.calculate_distance(self.current_route)
                messagebox.showinfo("Route Complete!", 
                                  f"🎉 Route completed successfully!\n"
                                  f"📏 Total distance: {distance:.2f} km\n"
                                  f"✅ Click 'Play' to evaluate your route.")
                return
            else:
                # Find missing cities
                missing = selected_names - visited_names
                messagebox.showinfo("Not All Cities Visited", 
                                  f"You must visit all selected cities before returning home!\n"
                                  f"Missing: {', '.join(missing)}")
                return
        
        # Check if city is already in route
        elif city_name in self.current_route:
            messagebox.showinfo("City Already Visited", "Each city can only be visited once!")
            return
        
        # Add city to route (only if it's selected or home)
        elif city in self.selected_cities or city == self.home_city:
            self.current_route.append(city_name)
        else:
            messagebox.showinfo("City Not Selected", f"City {city_name} was not selected!")
            return
        
        # Update display
        self.update_route_display()
        self.draw_cities()
    
    def update_route_display(self):
        """Update route display and distance"""
        try:
            # Update route label
            if self.current_route:
                route_text = " → ".join(self.current_route)
                self.route_label.config(text=route_text)
            else:
                self.route_label.config(text="No route built yet")
            
            # Calculate and update distance
            if len(self.current_route) > 1:
                distance = self.calculate_distance(self.current_route)
                self.distance_label.config(text=f"{distance:.2f} km")
                
                # Update best distance if this is better
                if distance < self.best_distance and self.is_valid_route():
                    self.best_distance = distance
                    self.best_distance_label.config(text=f"{distance:.2f} km")
            
            # Always update Play button state
            self.update_play_button_state()
            
        except Exception as e:
            print(f"Error updating route display: {e}")
    
    def update_play_button_state(self):
        """Enable/disable Play button based on route completion"""
        try:
            is_complete = self.check_complete_route()
            is_in_game_phase = not self.city_selection_mode
            
            if is_complete and is_in_game_phase:
                self.play_btn.config(state=tk.NORMAL, bg='#9B59B6')
                self.play_status_label.config(
                    text=f"✅ Route complete! Click 'Play' to evaluate.\n"
                         f"📏 Distance: {self.calculate_distance(self.current_route):.2f} km"
                )
            else:
                self.play_btn.config(state=tk.DISABLED, bg='#7D3C98')
                
                if not is_in_game_phase:
                    self.play_status_label.config(text="📝 Complete city selection first")
                elif not is_complete:
                    if len(self.current_route) == 1:  # Only home city
                        self.play_status_label.config(text="🛣️ Build your route starting from home")
                    elif self.current_route[-1] != self.home_city.name:
                        selected_names = {city.name for city in self.selected_cities}
                        visited_names = set(self.current_route)
                        missing = selected_names - visited_names
                        
                        if missing:
                            self.play_status_label.config(
                                text=f"📍 Return to {self.home_city.name} after visiting all cities\n"
                                     f"❌ Missing: {', '.join(missing)}"
                            )
                        else:
                            self.play_status_label.config(
                                text=f"🏁 Click {self.home_city.name} to complete the route"
                            )
        except Exception as e:
            print(f"Error updating play button state: {e}")
    
    def clear_route(self):
        """Clear the current route"""
        self.current_route = [self.home_city.name]  # Start with home city
        self.update_route_display()
        self.draw_cities()
    
    def is_valid_route(self):
        """Check if current route is valid"""
        if len(self.current_route) < 2:
            return False
        
        # Must start at home
        if self.current_route[0] != self.home_city.name:
            return False
        
        # Must contain all selected cities
        route_set = set(self.current_route)
        selected_names = {city.name for city in self.selected_cities}
        if not selected_names.issubset(route_set):
            return False
        
        # No duplicate cities (except home at start and end)
        middle_route = self.current_route[1:-1] if self.current_route[-1] == self.home_city.name else self.current_route[1:]
        if len(middle_route) != len(set(middle_route)):
            return False
        
        return True
    
    def check_complete_route(self):
        """Check if route is complete and valid"""
        # Must have at least 3 cities (home + at least one other + home)
        if len(self.current_route) < 3:
            return False
        
        # Must start and end at home
        if self.current_route[0] != self.home_city.name or self.current_route[-1] != self.home_city.name:
            return False
        
        # Must contain all selected cities
        selected_names = {city.name for city in self.selected_cities}
        route_set = set(self.current_route)
        if not selected_names.issubset(route_set):
            return False
        
        # No duplicate cities in the middle (excluding start and end home)
        middle_route = self.current_route[1:-1]
        if len(middle_route) != len(set(middle_route)):
            return False
        
        return True
    
    def start_play_phase(self):
        """Start the Play Phase to evaluate the player's path"""
        if not self.check_complete_route():
            messagebox.showinfo("Incomplete Route", 
                              "Please complete your route first:\n"
                              "1. Start and end at home city\n"
                              "2. Visit all selected cities\n"
                              "3. Each city visited only once")
            return
        
        if self.play_phase_active:
            self.stop_play_phase()
            return
        
        self.play_phase_active = True
        self.play_btn.config(text="⏸ Stop", bg='#E74C3C')
        self.play_status_label.config(text="⚡ Running algorithm evaluation...")
        
        # Reset algorithm results
        for algo in self.play_algorithms.values():
            algo['path'] = []
            algo['distance'] = 0
            algo['time'] = 0
        
        # Run the three algorithms
        self.run_play_algorithms()
        
        # Start visualization
        self.current_algorithm_index = 0
        self.visualize_next_algorithm()
    
    def run_play_algorithms(self):
        """Run the three algorithms for Play Phase and record performance"""
        # 1. Recursive Backtracking (checks all possible paths)
        start_time = time.time()
        recursive_path = self.recursive_backtracking()
        recursive_time = (time.time() - start_time) * 1000  # Convert to ms
        recursive_distance = self.calculate_distance(recursive_path)
        
        self.play_algorithms['recursive_backtracking']['path'] = recursive_path
        self.play_algorithms['recursive_backtracking']['distance'] = recursive_distance
        self.play_algorithms['recursive_backtracking']['time'] = recursive_time
        
        # 2. Iterative Validation (step-by-step validation)
        start_time = time.time()
        iterative_path = self.iterative_validation()
        iterative_time = (time.time() - start_time) * 1000
        iterative_distance = self.calculate_distance(iterative_path)
        
        self.play_algorithms['iterative_validation']['path'] = iterative_path
        self.play_algorithms['iterative_validation']['distance'] = iterative_distance
        self.play_algorithms['iterative_validation']['time'] = iterative_time
        
        # 3. Nearest Neighbor (greedy heuristic)
        start_time = time.time()
        nn_path = self.nearest_neighbor_heuristic()
        nn_time = (time.time() - start_time) * 1000
        nn_distance = self.calculate_distance(nn_path)
        
        self.play_algorithms['nearest_neighbor']['path'] = nn_path
        self.play_algorithms['nearest_neighbor']['distance'] = nn_distance
        self.play_algorithms['nearest_neighbor']['time'] = nn_time
    
    def recursive_backtracking(self):
        """Recursive backtracking algorithm to check all possible paths"""
        if not self.selected_cities or len(self.selected_cities) > 8:
            return self.current_route
        
        # Get all cities to visit (excluding home from permutations)
        cities_to_visit = [c for c in self.selected_cities if c.name != self.home_city.name]
        
        best_path = None
        best_distance = float('inf')
        
        # Generate all permutations (use islice for large numbers if needed)
        for perm in itertools.permutations(cities_to_visit):
            # Build path: home + permutation + home
            test_path = [self.home_city.name] + [city.name for city in perm] + [self.home_city.name]
            distance = self.calculate_distance(test_path)
            
            if distance < best_distance:
                best_distance = distance
                best_path = test_path
        
        return best_path if best_path else self.current_route
    
    def iterative_validation(self):
        """Iterative step-by-step path validation with improvements"""
        if len(self.current_route) < 3:
            return self.current_route
        
        validated_path = [self.home_city.name]
        visited = {self.home_city.name}
        
        # First pass: validate existing route
        for i in range(1, len(self.current_route) - 1):
            current_city = self.current_route[i]
            
            # Skip if already visited or not in selected cities
            if current_city in visited:
                continue
            
            if any(c.name == current_city for c in self.selected_cities):
                validated_path.append(current_city)
                visited.add(current_city)
        
        # Second pass: add missing cities in optimal order
        missing_cities = [c for c in self.selected_cities 
                         if c.name not in visited and c.name != self.home_city.name]
        
        # Sort missing cities by distance from last city in path
        if missing_cities and validated_path:
            last_city_name = validated_path[-1]
            last_city = next((c for c in self.cities if c.name == last_city_name), None)
            
            if last_city:
                missing_cities.sort(
                    key=lambda city: self.distance_matrix.get(
                        (last_city.name, city.name), float('inf')
                    )
                )
        
        # Add missing cities
        for city in missing_cities:
            validated_path.append(city.name)
        
        # Return to home
        if validated_path[-1] != self.home_city.name:
            validated_path.append(self.home_city.name)
        
        return validated_path
    
    def nearest_neighbor_heuristic(self):
        """Nearest neighbor greedy heuristic with improved logic"""
        if not self.selected_cities:
            return [self.home_city.name]
        
        # Start from home city
        path = [self.home_city.name]
        current_city = self.home_city
        unvisited = [c for c in self.selected_cities if c.name != self.home_city.name]
        
        while unvisited:
            # Find nearest unvisited city
            nearest = None
            min_dist = float('inf')
            
            for city in unvisited:
                dist = self.distance_matrix.get((current_city.name, city.name), float('inf'))
                if dist < min_dist:
                    min_dist = dist
                    nearest = city
            
            if nearest:
                path.append(nearest.name)
                current_city = nearest
                unvisited.remove(nearest)
            else:
                break
        
        # Return to home
        if path[-1] != self.home_city.name:
            path.append(self.home_city.name)
        
        return path
    
    def visualize_next_algorithm(self):
        """Visualize the next algorithm in sequence"""
        if not self.play_phase_active or self.current_algorithm_index >= len(self.play_algorithms):
            self.stop_play_phase()
            return
        
        algorithm_keys = list(self.play_algorithms.keys())
        current_key = algorithm_keys[self.current_algorithm_index]
        algorithm = self.play_algorithms[current_key]
        
        # Update status
        self.play_status_label.config(
            text=f"⚡ Running: {algorithm['name']}\n📏 Distance: {algorithm['distance']:.2f} km\n⏱️ Time: {algorithm['time']:.2f} ms"
        )
        
        # Visualize algorithm path
        self.visualize_algorithm_path(current_key, algorithm)
        
        # Move to next algorithm after delay
        delay = self.delay_slider.get()
        self.play_animation_id = self.root.after(delay + 1000, self.move_to_next_algorithm)
    
    def move_to_next_algorithm(self):
        """Move to the next algorithm in the visualization sequence"""
        self.current_algorithm_index += 1
        
        # Clear previous visualization
        self.clear_visualization_lines()
        
        if self.current_algorithm_index < len(self.play_algorithms):
            self.visualize_next_algorithm()
        else:
            # All algorithms visualized
            self.stop_play_phase()
    
    def visualize_algorithm_path(self, algorithm_key, algorithm):
        """Visualize the algorithm's path on the canvas"""
        self.clear_visualization_lines()
        
        if not algorithm['path'] or len(algorithm['path']) < 2:
            return
        
        color = algorithm['color']
        
        # Draw the algorithm's path
        for i in range(len(algorithm['path']) - 1):
            city1_name = algorithm['path'][i]
            city2_name = algorithm['path'][i + 1]
            
            city1 = next((c for c in self.cities if c.name == city1_name), None)
            city2 = next((c for c in self.cities if c.name == city2_name), None)
            
            if city1 and city2:
                # Draw line with algorithm's color
                line = self.game_canvas.create_line(
                    city1.x, city1.y, city2.x, city2.y,
                    fill=color, width=4,
                    arrow=tk.LAST, arrowshape=(12, 15, 5),
                    dash=(4, 4)
                )
                self.path_visualization_lines.append(line)
    
    def clear_visualization_lines(self):
        """Clear all visualization lines from canvas"""
        for line in self.path_visualization_lines:
            self.game_canvas.delete(line)
        self.path_visualization_lines = []
    
    def show_final_algorithm_comparison(self):
        """Show detailed comparison of all three algorithms with performance metrics"""
        player_distance = self.calculate_distance(self.current_route)
        
        # Create a new window for results
        results_window = tk.Toplevel(self.root)
        results_window.title("Play Phase Results")
        results_window.geometry("800x600")
        results_window.configure(bg='#1e3d59')
        
        # Center the window
        results_window.update_idletasks()
        width = results_window.winfo_width()
        height = results_window.winfo_height()
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2
        results_window.geometry(f"{width}x{height}+{x}+{y}")
        
        tk.Label(
            results_window, text="🎮 PLAY PHASE RESULTS",
            font=("Impact", 28, "bold"), bg='#1e3d59', fg='#9B59B6'
        ).pack(pady=20)
        
        # Create a notebook for tabs
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Tab 1: Performance Comparison
        perf_frame = tk.Frame(notebook, bg='#2c3e50')
        notebook.add(perf_frame, text="📊 Performance Comparison")
        
        # Create performance table
        tree_frame = tk.Frame(perf_frame, bg='#2c3e50')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(
            tree_frame,
            columns=("Algorithm", "Distance (km)", "Time (ms)", "Status"),
            show="headings",
            height=10
        )
        
        # Define columns
        tree.heading("Algorithm", text="Algorithm")
        tree.heading("Distance (km)", text="Distance (km)")
        tree.heading("Time (ms)", text="Time (ms)")
        tree.heading("Status", text="Status")
        
        tree.column("Algorithm", width=200)
        tree.column("Distance (km)", width=150, anchor=tk.CENTER)
        tree.column("Time (ms)", width=150, anchor=tk.CENTER)
        tree.column("Status", width=150, anchor=tk.CENTER)
        
        # Add algorithm data
        best_distance = float('inf')
        best_algorithm = None
        
        for algo_key, algo_data in self.play_algorithms.items():
            algo_distance = algo_data['distance']
            algo_time = algo_data.get('time', 0)
            
            # Determine if this is the best algorithm
            if algo_distance < best_distance:
                best_distance = algo_distance
                best_algorithm = algo_data['name']
            
            # Determine status
            if algo_distance == best_distance:
                status = "🏆 BEST"
            else:
                diff = algo_distance - best_distance
                status = f"+{diff:.1f} km"
            
            tree.insert("", tk.END, values=(
                algo_data['name'],
                f"{algo_distance:.2f}",
                f"{algo_time:.2f}",
                status
            ))
        
        # Add player's route
        tree.insert("", tk.END, values=(
            "🎮 YOUR ROUTE",
            f"{player_distance:.2f}",
            "-",
            "YOUR SCORE"
        ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tab 2: Detailed Analysis
        analysis_frame = tk.Frame(notebook, bg='#2c3e50')
        notebook.add(analysis_frame, text="🔍 Detailed Analysis")
        
        analysis_text = f"""
        🎯 PLAYER'S ROUTE ANALYSIS:
        
        • Your distance: {player_distance:.2f} km
        • Best algorithm distance: {best_distance:.2f} km
        • Difference: {player_distance - best_distance:+.2f} km
        
        📊 ALGORITHM PERFORMANCE:
        
        1. Recursive Backtracking:
           • Distance: {self.play_algorithms['recursive_backtracking']['distance']:.2f} km
           • Time: {self.play_algorithms['recursive_backtracking'].get('time', 0):.2f} ms
           • Strategy: Checks all possible permutations
        
        2. Iterative Validation:
           • Distance: {self.play_algorithms['iterative_validation']['distance']:.2f} km
           • Time: {self.play_algorithms['iterative_validation'].get('time', 0):.2f} ms
           • Strategy: Validates step-by-step
        
        3. Nearest Neighbor:
           • Distance: {self.play_algorithms['nearest_neighbor']['distance']:.2f} km
           • Time: {self.play_algorithms['nearest_neighbor'].get('time', 0):.2f} ms
           • Strategy: Greedy heuristic
        
        🏆 WINNER: {best_algorithm}
        
        💡 RECOMMENDATIONS:
        """
        
        # Add recommendations based on comparison
        if player_distance <= best_distance + 0.01:  # Within 1% tolerance
            analysis_text += "\n✅ EXCELLENT! Your route is optimal or very close!"
            analysis_text += "\n🎉 You've found one of the best possible paths!"
            self.play_sound("win")
        elif player_distance <= best_distance * 1.1:  # Within 10% of best
            analysis_text += "\n👍 GOOD! Your route is within 10% of optimal."
            analysis_text += f"\n💡 You could save {player_distance - best_distance:.2f} km"
            self.play_sound("correct")
        else:
            analysis_text += "\n📝 ROOM FOR IMPROVEMENT"
            analysis_text += f"\n💡 You could save {player_distance - best_distance:.2f} km ({((player_distance - best_distance)/best_distance*100):.1f}%)"
            analysis_text += f"\n🔧 Try using the {best_algorithm} strategy"
            self.play_sound("incorrect")
        
        text_widget = tk.Text(
            analysis_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
            font=("Arial", 12), padx=15, pady=15, relief=tk.FLAT
        )
        text_widget.insert(tk.END, analysis_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 3: Algorithm Paths
        paths_frame = tk.Frame(notebook, bg='#2c3e50')
        notebook.add(paths_frame, text="🛣️ Algorithm Paths")
        
        paths_text = "📋 ALGORITHM PATHS:\n\n"
        
        # Player's route
        paths_text += f"🎮 YOUR ROUTE:\n"
        paths_text += f"   → {' → '.join(self.current_route)}\n"
        paths_text += f"   📏 Distance: {player_distance:.2f} km\n\n"
        
        # Algorithm routes
        for algo_key, algo_data in self.play_algorithms.items():
            paths_text += f"🔹 {algo_data['name']}:\n"
            if algo_data['path']:
                paths_text += f"   → {' → '.join(algo_data['path'])}\n"
            paths_text += f"   📏 Distance: {algo_data['distance']:.2f} km\n"
            paths_text += f"   ⏱️  Time: {algo_data.get('time', 0):.2f} ms\n\n"
        
        paths_widget = tk.Text(
            paths_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
            font=("Courier New", 11), padx=15, pady=15, relief=tk.FLAT
        )
        paths_widget.insert(tk.END, paths_text)
        paths_widget.config(state=tk.DISABLED)
        paths_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Close button
        tk.Button(
            results_window, text="Close",
            command=results_window.destroy, font=("Arial", 14),
            bg='#3498db', fg='white', padx=30, pady=10, cursor="hand2"
        ).pack(pady=20)
        
        # Also update status label
        self.play_status_label.config(text="✅ Evaluation complete - Check results!")
    
    def stop_play_phase(self):
        """Stop the Play Phase and show results"""
        self.play_phase_active = False
        self.algorithm_visualization_active = False
        
        if self.play_animation_id:
            self.root.after_cancel(self.play_animation_id)
            self.play_animation_id = None
        
        # Clear visualization lines
        self.clear_visualization_lines()
        
        self.play_btn.config(text="▶ Play", bg='#9B59B6')
        self.play_status_label.config(text="📊 Calculating results...")
        
        # Calculate final results and show comparison
        self.show_final_algorithm_comparison()
    
    def submit_solution(self):
        """Submit current route as solution"""
        try:
            if not self.check_complete_route():
                messagebox.showinfo("Invalid Route", 
                                  "Route must:\n"
                                  "1. Start and end at HOME city\n"
                                  "2. Visit all selected cities\n"
                                  "3. Visit each city only once")
                return
            
            player_distance = self.calculate_distance(self.current_route)
            
            # Find optimal distance from algorithms
            optimal_distance = float('inf')
            for result in self.algorithm_results.values():
                if result['distance'] < optimal_distance:
                    optimal_distance = result['distance']
            
            # Check if player found optimal solution (within 1% tolerance)
            is_optimal = abs(player_distance - optimal_distance) / optimal_distance < 0.01
            
            # Show result
            if is_optimal:
                self.play_sound("win")
                
                # Save game results (only for correct answers)
                self.save_game_results(player_distance)
                
                messagebox.showinfo(
                    "🎉 OPTIMAL SOLUTION! 🎉",
                    f"Congratulations {self.player_name}!\n\n"
                    f"You found the optimal route!\n"
                    f"Your distance: {player_distance:.2f} km\n"
                    f"Optimal distance: {optimal_distance:.2f} km\n\n"
                    f"Score saved to database!"
                )
                
                # Show optimal route
                self.show_optimal_solution()
                self.game_over = True
                
            else:
                self.play_sound("incorrect")
                messagebox.showinfo(
                    "❌ Not Optimal",
                    f"Your route can be improved {self.player_name}!\n\n"
                    f"Your distance: {player_distance:.2f} km\n"
                    f"Optimal distance: {optimal_distance:.2f} km\n"
                    f"Difference: {player_distance - optimal_distance:.2f} km\n\n"
                    f"Try again!\n\n"
                    f"Note: Score is only saved when you find the optimal route."
                )
        except Exception as e:
            messagebox.showerror("Submission Error", f"Failed to submit solution: {e}")
    
    def show_optimal_solution(self):
        """Show the optimal solution found by algorithms"""
        try:
            # Find best algorithm result
            best_algo = None
            best_distance = float('inf')
            
            for algo, result in self.algorithm_results.items():
                if result['distance'] < best_distance:
                    best_distance = result['distance']
                    best_algo = algo
            
            if best_algo:
                optimal_route = self.algorithm_results[best_algo]['path']
                
                # Draw optimal route
                for i in range(len(optimal_route) - 1):
                    city1_name = optimal_route[i]
                    city2_name = optimal_route[i + 1]
                    
                    city1 = next(c for c in self.cities if c.name == city1_name)
                    city2 = next(c for c in self.cities if c.name == city2_name)
                    
                    # Draw optimal route line (green)
                    self.game_canvas.create_line(
                        city1.x, city1.y, city2.x, city2.y,
                        fill='#27ae60', width=2, arrow=tk.LAST,
                        arrowshape=(12, 16, 4), dash=(2, 2)
                    )
        except Exception as e:
            print(f"Error showing optimal solution: {e}")
    
    def save_game_results(self, player_distance):
        """Save game results to database ONLY when answer is correct"""
        try:
            # Find optimal solution
            optimal_distance = float('inf')
            optimal_route = []
            for algo, result in self.algorithm_results.items():
                if result['distance'] < optimal_distance:
                    optimal_distance = result['distance']
                    optimal_route = result['path']
            
            # Update player stats - increment correct answers
            self.cursor.execute('''
                UPDATE players 
                SET games_played = games_played + 1,
                    correct_answers = correct_answers + 1,
                    total_distance_saved = total_distance_saved + ?,
                    best_score = CASE WHEN ? > best_score THEN ? ELSE best_score END
                WHERE id = ?
            ''', (player_distance, player_distance, player_distance, self.player_id))
            
            # Add to game history - ONLY for correct answers
            self.cursor.execute('''
                INSERT INTO game_history 
                (game_id, player_id, player_name, home_city, selected_cities, 
                 player_route, player_distance, optimal_route, optimal_distance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.game_id, self.player_id, self.player_name, self.home_city.name,
                json.dumps([c.name for c in self.selected_cities]),
                json.dumps(self.current_route), player_distance,
                json.dumps(optimal_route), optimal_distance
            ))
            
            # Save algorithm performance
            for algo, result in self.algorithm_results.items():
                if result['time'] >= 0:  # Skip algorithms that weren't run
                    complexity = self.get_complexity_analysis(algo, len(self.selected_cities) + 1)
                    
                    self.cursor.execute('''
                        INSERT INTO algorithm_performance 
                        (game_id, algorithm_name, execution_time_ms, distance, complexity_analysis)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        self.game_id, algo, result['time'], result['distance'], complexity
                    ))
            
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save game results: {e}")
    
    def get_complexity_analysis(self, algorithm, n):
        """Get complexity analysis for an algorithm"""
        try:
            complexities = {
                'brute_force': f'O(n!) = O({n}!) = O({math.factorial(n) if n <= 10 else "very large"})',
                'nearest_neighbor': f'O(n²) = O({n}²) = O({n**2})',
                'genetic_algorithm': f'O(p * g * n) = O(100 * 500 * {n}) = O({50000 * n})'
            }
            return complexities.get(algorithm, "Unknown")
        except Exception:
            return "Complexity analysis failed"
    
    def show_algorithm_hints(self):
        """Show algorithm comparison and hints"""
        try:
            hints_window = tk.Toplevel(self.root)
            hints_window.title("Algorithm Hints")
            hints_window.geometry("800x600")
            hints_window.configure(bg='#1e3d59')
            
            # Center the window
            hints_window.update_idletasks()
            width = hints_window.winfo_width()
            height = hints_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            hints_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                hints_window, text="🤖 THREE Algorithm Performance",
                font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=20)
            
            # Create notebook for tabs
            notebook = ttk.Notebook(hints_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Performance tab
            perf_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(perf_frame, text="📊 Performance")
            
            # Create performance table
            columns = ("Algorithm", "Distance (km)", "Time (ms)", "Complexity")
            tree = ttk.Treeview(perf_frame, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Add algorithm data
            for algo, result in self.algorithm_results.items():
                if result['time'] >= 0:
                    algo_name = algo.replace('_', ' ').title()
                    complexity = self.get_complexity_analysis(algo, len(self.selected_cities) + 1)
                    tree.insert("", tk.END, values=(
                        algo_name,
                        f"{result['distance']:.2f}",
                        f"{result['time']:.2f}",
                        complexity.split(' = ')[0]
                    ))
            
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Hints tab
            hints_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(hints_frame, text="💡 Hints")
            
            hints_text = f"""
            💡 Strategy Hints:
            
            1. Look for clusters of cities - visit them together
            2. Try to minimize backtracking
            3. Consider the triangle inequality
            4. Start with cities farthest from home
            
            🔍 THREE Algorithm Insights:
            
            • Brute Force: Guaranteed optimal but slow for >8 cities
            • Nearest Neighbor: Fast but may miss optimal
            • Genetic Algorithm: Good heuristic for large instances
            
            🎯 Current Game Info:
            
            • Home city: {self.home_city.name}
            • Selected cities: {', '.join([c.name for c in self.selected_cities])}
            • Current best: {self.best_distance:.2f} km
            • Distance range: 50-100 km between cities
            
            🎮 PLAY PHASE:
            
            • Click "Play" when your route is complete
            • Watch three algorithms evaluate your path
            • Learn from the comparisons
            """
            
            text_widget = tk.Text(
                hints_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
                font=("Arial", 12), padx=10, pady=10, relief=tk.FLAT
            )
            text_widget.insert(tk.END, hints_text)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Close button
            tk.Button(
                hints_window, text="Close",
                command=hints_window.destroy, font=("Arial", 14),
                bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show algorithm hints: {e}")
    
    def show_player_stats(self):
        """Show player statistics"""
        try:
            stats_window = tk.Toplevel(self.root)
            stats_window.title("Player Statistics")
            stats_window.geometry("800x600")
            stats_window.configure(bg='#1e3d59')
            
            # Center the window
            stats_window.update_idletasks()
            width = stats_window.winfo_width()
            height = stats_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            stats_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                stats_window, text="📊 Player Statistics",
                font=("Impact", 28, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=(30, 20))
            
            # Fetch player stats
            self.cursor.execute('''
                SELECT name, games_played, correct_answers, 
                       ROUND(total_distance_saved, 2) as total_saved,
                       ROUND(best_score, 2) as best,
                       ROUND(CASE WHEN games_played > 0 
                            THEN correct_answers * 100.0 / games_played 
                            ELSE 0 END, 1) as accuracy
                FROM players
                ORDER BY accuracy DESC, games_played DESC
            ''')
            
            players = self.cursor.fetchall()
            
            if players:
                # Create Treeview for stats
                tree_frame = tk.Frame(stats_window, bg='#1e3d59')
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
                
                # Treeview
                tree = ttk.Treeview(
                    tree_frame,
                    columns=("Name", "Games", "Correct", "Accuracy", "Best Score", "Total Saved"),
                    show="headings",
                    height=15
                )
                
                # Define columns
                tree.heading("Name", text="Player Name")
                tree.heading("Games", text="Games Played")
                tree.heading("Correct", text="Correct Answers")
                tree.heading("Accuracy", text="Accuracy %")
                tree.heading("Best Score", text="Best Distance")
                tree.heading("Total Saved", text="Total Distance Saved")
                
                tree.column("Name", width=150)
                tree.column("Games", width=100, anchor=tk.CENTER)
                tree.column("Correct", width=100, anchor=tk.CENTER)
                tree.column("Accuracy", width=100, anchor=tk.CENTER)
                tree.column("Best Score", width=120, anchor=tk.CENTER)
                tree.column("Total Saved", width=120, anchor=tk.CENTER)
                
                # Add data
                for player in players:
                    tree.insert("", tk.END, values=player)
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                tk.Label(
                    stats_window, text="No player statistics available",
                    font=("Arial", 16), bg='#1e3d59', fg='#ecf0f1'
                ).pack(pady=50)
            
            # Close button
            tk.Button(
                stats_window, text="Close",
                command=stats_window.destroy, font=("Arial", 14),
                bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show player stats: {e}")
    
    def show_leaderboard(self):
        """Show game leaderboard"""
        try:
            leader_window = tk.Toplevel(self.root)
            leader_window.title("Leaderboard")
            leader_window.geometry("800x600")
            leader_window.configure(bg='#1e3d59')
            
            # Center the window
            leader_window.update_idletasks()
            width = leader_window.winfo_width()
            height = leader_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            leader_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                leader_window, text="🏆 TSP LEADERBOARD 🏆",
                font=("Impact", 32, "bold"), bg='#1e3d59', fg='#f7dc6f'
            ).pack(pady=(30, 20))
            
            # Fetch top games
            self.cursor.execute('''
                SELECT gh.game_date, p.name, gh.player_distance, gh.optimal_distance,
                       ROUND((gh.optimal_distance / gh.player_distance) * 100, 1) as efficiency
                FROM game_history gh
                JOIN players p ON gh.player_id = p.id
                ORDER BY efficiency DESC, gh.player_distance
                LIMIT 10
            ''')
            
            games = self.cursor.fetchall()
            
            # Display leaderboard
            leader_frame = tk.Frame(leader_window, bg='#2c3e50', relief=tk.RAISED, bd=3)
            leader_frame.pack(pady=20, padx=50, fill=tk.BOTH, expand=True)
            
            if games:
                for i, game in enumerate(games):
                    game_date = datetime.strptime(game[0], '%Y-%m-%d %H:%M:%S').strftime('%b %d')
                    
                    # Gold, Silver, Bronze for top 3
                    if i == 0:
                        color = '#FFD700'
                        emoji = "🥇"
                    elif i == 1:
                        color = '#C0C0C0'
                        emoji = "🥈"
                    elif i == 2:
                        color = '#CD7F32'
                        emoji = "🥉"
                    else:
                        color = '#ecf0f1'
                        emoji = "🏅"
                    
                    frame = tk.Frame(leader_frame, bg='#34495e')
                    frame.pack(fill=tk.X, pady=5, padx=20)
                    
                    # Rank and name
                    rank_frame = tk.Frame(frame, bg='#34495e')
                    rank_frame.pack(side=tk.LEFT, padx=10)
                    
                    tk.Label(
                        rank_frame, text=emoji, font=("Arial", 20), bg='#34495e', fg=color
                    ).pack()
                    
                    tk.Label(
                        rank_frame, text=f"{i+1}. {game[1]}", 
                        font=("Arial", 14, "bold"), bg='#34495e', fg=color
                    ).pack()
                    
                    # Stats
                    stats_frame = tk.Frame(frame, bg='#34495e')
                    stats_frame.pack(side=tk.RIGHT, padx=10)
                    
                    stats_text = f"Score: {game[4]}% | {game[2]:.1f}km ({game_date})"
                    tk.Label(
                        stats_frame, text=stats_text, font=("Arial", 12), 
                        bg='#34495e', fg=color
                    ).pack()
            else:
                tk.Label(
                    leader_frame, text="No games played yet!",
                    font=("Arial", 16), bg='#2c3e50', fg='#ecf0f1'
                ).pack(pady=50)
            
            # Close button
            tk.Button(
                leader_window, text="Close",
                command=leader_window.destroy, font=("Arial", 14),
                bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show leaderboard: {e}")
    
    def show_complexity_analysis(self):
        """Show detailed complexity analysis for THREE algorithms"""
        try:
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Complexity Analysis")
            analysis_window.geometry("900x700")
            analysis_window.configure(bg='#1e3d59')
            
            # Center the window
            analysis_window.update_idletasks()
            width = analysis_window.winfo_width()
            height = analysis_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            analysis_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                analysis_window, text="🔬 THREE Algorithm Complexity Analysis",
                font=("Impact", 28, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=(30, 20))
            
            # Create notebook for tabs
            notebook = ttk.Notebook(analysis_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Time Complexity tab
            time_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(time_frame, text="⏱️ Time Complexity")
            
            time_text = """
            Time Complexity Analysis for THREE Algorithms:
            
            1. Brute Force (Exhaustive Search):
               • Complexity: O(n!)
               • Description: Generates all permutations of cities
               • Practical Limit: n ≤ 8-10
               • Example: 10! = 3,628,800 permutations
            
            2. Nearest Neighbor (Greedy):
               • Complexity: O(n²)
               • Description: Always visits nearest unvisited city
               • Approximation Ratio: O(log n) in worst case
               • Very fast but not always optimal
            
            3. Genetic Algorithm (Evolutionary):
               • Complexity: O(p * g * n)
               • p = Population size (typically 100)
               • g = Generations (typically 500)
               • n = Number of cities
               • Good heuristic for large instances
            
            🎮 PLAY PHASE ALGORITHMS:
            
            4. Recursive Backtracking:
               • Complexity: O(n!)
               • Checks all possible paths like brute force
               • Stops early if finds better solution
            
            5. Iterative Validation:
               • Complexity: O(n²)
               • Validates player's path step by step
               • Suggests improvements at each step
            
            6. Nearest Neighbor (Play Phase):
               • Complexity: O(n²)
               • Greedy approximation for comparison
            """
            
            time_widget = tk.Text(
                time_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
                font=("Courier New", 11), padx=15, pady=15, relief=tk.FLAT
            )
            time_widget.insert(tk.END, time_text)
            time_widget.config(state=tk.DISABLED)
            time_widget.pack(fill=tk.BOTH, expand=True)
            
            # Space Complexity tab
            space_frame = tk.Frame(notebook, bg='#2c3e50')
            notebook.add(space_frame, text="💾 Space Complexity")
            
            space_text = """
            Space Complexity Analysis for THREE Algorithms:
            
            1. Brute Force:
               • Space: O(n)
               • Only needs to store current permutation
               • Very memory efficient
            
            2. Nearest Neighbor:
               • Space: O(n)
               • Stores visited/unvisited status
               • Very memory efficient
            
            3. Genetic Algorithm:
               • Space: O(p * n)
               • Stores population of p individuals
               • Each individual is a permutation of n cities
            
            🎮 PLAY PHASE ALGORITHMS:
            
            4. Recursive Backtracking:
               • Space: O(n) for recursion stack
               • Uses backtracking to explore paths
            
            5. Iterative Validation:
               • Space: O(n)
               • Stores current path and remaining cities
            
            6. Nearest Neighbor (Play Phase):
               • Space: O(n)
               • Same as regular nearest neighbor
            """
            
            space_widget = tk.Text(
                space_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
                font=("Courier New", 11), padx=15, pady=15, relief=tk.FLAT
            )
            space_widget.insert(tk.END, space_text)
            space_widget.config(state=tk.DISABLED)
            space_widget.pack(fill=tk.BOTH, expand=True)
            
            # Close button
            tk.Button(
                analysis_window, text="Close",
                command=analysis_window.destroy, font=("Arial", 14),
                bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show complexity analysis: {e}")
    
    def show_game_settings(self):
        """Show game settings"""
        try:
            settings_window = tk.Toplevel(self.root)
            settings_window.title("Game Settings")
            settings_window.geometry("400x400")
            settings_window.configure(bg='#1e3d59')
            
            # Center the window
            settings_window.update_idletasks()
            width = settings_window.winfo_width()
            height = settings_window.winfo_height()
            x = (self.screen_width - width) // 2
            y = (self.screen_height - height) // 2
            settings_window.geometry(f"{width}x{height}+{x}+{y}")
            
            tk.Label(
                settings_window, text="⚙️ Game Settings",
                font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
            ).pack(pady=20)
            
            # Settings options
            settings_frame = tk.Frame(settings_window, bg='#2c3e50', relief=tk.RAISED, bd=3)
            settings_frame.pack(pady=20, padx=50, ipadx=20, ipady=20)
            
            # Sound toggle
            sound_var = tk.BooleanVar(value=self.sound_enabled)
            
            def toggle_sound():
                self.sound_enabled = sound_var.get()
            
            tk.Checkbutton(
                settings_frame, text="Enable Sound Effects", variable=sound_var,
                command=toggle_sound, font=("Arial", 12), bg='#2c3e50', fg='white',
                selectcolor='#34495e'
            ).pack(pady=10, anchor=tk.W)
            
            # Number of cities
            city_frame = tk.Frame(settings_frame, bg='#2c3e50')
            city_frame.pack(pady=10, fill=tk.X)
            
            tk.Label(
                city_frame, text="Number of Cities:", 
                font=("Arial", 12), bg='#2c3e50', fg='white'
            ).pack(side=tk.LEFT)
            
            city_var = tk.StringVar(value=str(self.num_cities))
            city_spinbox = tk.Spinbox(
                city_frame, from_=5, to=15, textvariable=city_var,
                font=("Arial", 12), width=5
            )
            city_spinbox.pack(side=tk.RIGHT, padx=10)
            
            def update_cities():
                try:
                    self.num_cities = int(city_var.get())
                    self.city_names = [chr(65 + i) for i in range(self.num_cities)]
                    messagebox.showinfo("Settings Updated", "Number of cities updated. Changes will take effect in new games.")
                except:
                    messagebox.showerror("Error", "Invalid number of cities")
            
            # Reset database button
            def reset_database():
                if messagebox.askyesno("Reset Database", "Delete all game records?"):
                    try:
                        self.cursor.execute("DELETE FROM game_history")
                        self.cursor.execute("DELETE FROM players")
                        self.cursor.execute("DELETE FROM algorithm_performance")
                        self.cursor.execute("DELETE FROM game_settings")
                        self.conn.commit()
                        messagebox.showinfo("Reset Complete", "All records have been deleted.")
                        settings_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to reset database: {e}")
            
            tk.Button(
                settings_frame, text="🗑️ Reset Database", command=reset_database,
                font=("Arial", 12), bg='#e74c3c', fg='white',
                padx=20, pady=8, cursor="hand2"
            ).pack(pady=15)
            
            # Apply button
            tk.Button(
                settings_frame, text="Apply Settings", command=update_cities,
                font=("Arial", 12), bg='#3498db', fg='white',
                padx=20, pady=8, cursor="hand2"
            ).pack(pady=10)
            
            # Close button
            tk.Button(
                settings_window, text="Close",
                command=settings_window.destroy, font=("Arial", 14),
                bg='#3498db', fg='white', padx=30, pady=10, cursor="hand2"
            ).pack(pady=20)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show game settings: {e}")

class TestTSPAlgorithms(unittest.TestCase):
    """Unit tests for TSP algorithms"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create test cities
        self.cities = [
            City("A", 0, 0),
            City("B", 10, 0),
            City("C", 10, 10),
            City("D", 0, 10)
        ]
        self.start_city = self.cities[0]
        
        # Create test distance matrix (50-100 km range)
        self.distance_matrix = {
            ("A", "B"): 50, ("B", "A"): 50,
            ("A", "C"): 75, ("C", "A"): 75,
            ("A", "D"): 100, ("D", "A"): 100,
            ("B", "C"): 60, ("C", "B"): 60,
            ("B", "D"): 90, ("D", "B"): 90,
            ("C", "D"): 55, ("D", "C"): 55
        }
    
    def test_brute_force_small(self):
        """Test brute force with small number of cities"""
        path, distance = TSPAlgorithm.brute_force(self.cities, self.start_city, self.distance_matrix)
        self.assertEqual(len(path), 5)  # A -> ... -> A
        self.assertGreater(distance, 0)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "A")
    
    def test_nearest_neighbor(self):
        """Test nearest neighbor algorithm"""
        path, distance = TSPAlgorithm.nearest_neighbor(self.cities, self.start_city, self.distance_matrix)
        self.assertEqual(len(path), 5)
        self.assertGreater(distance, 0)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "A")
    
    def test_genetic_algorithm(self):
        """Test genetic algorithm"""
        path, distance = TSPAlgorithm.genetic_algorithm(self.cities, self.start_city, self.distance_matrix, 
                                                        population_size=20, generations=50)
        self.assertEqual(len(path), 5)
        self.assertGreater(distance, 0)
        self.assertEqual(path[0], "A")
        self.assertEqual(path[-1], "A")
    
    def test_algorithms_consistency(self):
        """Test that all algorithms produce valid routes"""
        algorithms = [
            lambda: TSPAlgorithm.brute_force(self.cities, self.start_city, self.distance_matrix),
            lambda: TSPAlgorithm.nearest_neighbor(self.cities, self.start_city, self.distance_matrix),
            lambda: TSPAlgorithm.genetic_algorithm(self.cities, self.start_city, self.distance_matrix, 
                                                   population_size=20, generations=50)
        ]
        
        for algo in algorithms:
            path, distance = algo()
            self.assertEqual(path[0], "A")
            self.assertEqual(path[-1], "A")
            self.assertGreater(distance, 0)
            self.assertTrue(all(city in path for city in ["A", "B", "C", "D"]))
    
    def test_distance_calculation(self):
        """Test distance calculation between cities"""
        city1 = City("X", 0, 0)
        city2 = City("Y", 3, 4)
        distance = city1.distance_to(city2)
        self.assertEqual(distance, 5.0)  # 3-4-5 triangle
    
    def test_distance_matrix_range(self):
        """Test that distances are in 50-100 km range"""
        for (city1, city2), distance in self.distance_matrix.items():
            self.assertGreaterEqual(distance, 50)
            self.assertLessEqual(distance, 100)
    
    def test_route_validation(self):
        """Test route validation logic"""
        game = TravelingSalesmanGame.__new__(TravelingSalesmanGame)
        game.home_city = City("A", 0, 0)
        game.selected_cities = [City("B", 1, 1), City("C", 2, 2)]
        
        # Test valid route
        game.current_route = ["A", "B", "C", "A"]
        self.assertTrue(game.is_valid_route())
        
        # Test invalid - doesn't start at home
        game.current_route = ["B", "C", "A"]
        self.assertFalse(game.is_valid_route())
        
        # Test invalid - doesn't visit all cities
        game.current_route = ["A", "B", "A"]
        self.assertFalse(game.is_valid_route())
        
        # Test invalid - duplicate city
        game.current_route = ["A", "B", "C", "B", "A"]
        self.assertFalse(game.is_valid_route())
    
    def test_calculate_distance(self):
        """Test distance calculation function"""
        game = TravelingSalesmanGame.__new__(TravelingSalesmanGame)
        game.distance_matrix = {
            ("A", "B"): 50, ("B", "A"): 50,
            ("B", "C"): 75, ("C", "B"): 75,
            ("C", "A"): 100, ("A", "C"): 100
        }
        
        route = ["A", "B", "C", "A"]
        distance = game.calculate_distance(route)
        self.assertEqual(distance, 225)  # 50 + 75 + 100
    
    def test_exception_handling(self):
        """Test exception handling in game functions"""
        game = TravelingSalesmanGame.__new__(TravelingSalesmanGame)
        
        # Test with invalid route
        game.distance_matrix = {}
        route = ["A", "B", "C"]
        distance = game.calculate_distance(route)
        self.assertEqual(distance, float('inf'))  # Should return infinity for invalid route

def run_unit_tests():
    """Run unit tests and display results"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTSPAlgorithms)
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Capture test output
    import io
    from contextlib import redirect_stdout
    
    f = io.StringIO()
    with redirect_stdout(f):
        result = runner.run(suite)
    
    # Create results window
    root = tk.Tk()
    root.title("Unit Test Results")
    root.geometry("800x600")
    root.configure(bg='#1e3d59')
    
    # Center the window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    tk.Label(
        root, text="🧪 Unit Test Results",
        font=("Impact", 24, "bold"), bg='#1e3d59', fg='#4ECDC4'
    ).pack(pady=20)
    
    text_frame = tk.Frame(root, bg='#2c3e50')
    text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    text_widget = tk.Text(
        text_frame, wrap=tk.WORD, bg='#2c3e50', fg='white',
        font=("Courier New", 10), padx=10, pady=10, relief=tk.FLAT
    )
    
    text_widget.insert(tk.END, f.getvalue())
    
    if result.wasSuccessful():
        text_widget.insert(tk.END, "\n\n✅ ALL TESTS PASSED!\n")
        text_widget.tag_add("success", "end-3l", "end")
        text_widget.tag_config("success", foreground="#27ae60", 
                              font=("Arial", 12, "bold"))
    else:
        text_widget.insert(tk.END, f"\n\n❌ {len(result.failures) + len(result.errors)} TESTS FAILED!\n")
        text_widget.tag_add("failure", "end-3l", "end")
        text_widget.tag_config("failure", foreground="#e74c3c", 
                              font=("Arial", 12, "bold"))
    
    text_widget.config(state=tk.DISABLED)
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    tk.Button(
        root, text="Close",
        command=root.destroy, font=("Arial", 14),
        bg='#e67e22', fg='white', padx=30, pady=10, cursor="hand2"
    ).pack(pady=20)
    
    root.mainloop()

def check_dependencies():
    """Check and install required dependencies"""
    required_packages = ['matplotlib', 'numpy', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        response = messagebox.askyesno(
            "Missing Dependencies",
            f"The following packages are required for charts:\n{', '.join(missing_packages)}\n\n"
            f"Install now? (Requires internet connection)"
        )
        
        if response:
            try:
                import subprocess
                import sys
                for package in missing_packages:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                messagebox.showinfo("Success", "Dependencies installed successfully!")
            except Exception as e:
                messagebox.showerror("Installation Failed", 
                                   f"Failed to install packages: {e}\n\n"
                                   f"Please run manually:\n"
                                   f"pip install {' '.join(missing_packages)}")
                return False
    return True

def main():
    """Main function to run the game with improved window handling"""
    try:
        # Check dependencies
        if not check_dependencies():
            messagebox.showwarning("Limited Features", 
                                 "Chart features will be unavailable.\n"
                                 "Basic game functions will still work.")
        
        root = tk.Tk()
        
        # Create the game instance
        game = TravelingSalesmanGame(root)
        
        # Make window resizable
        root.resizable(True, True)
        
        # Bind window resize event to update layout if needed
        def on_resize(event):
            # You can add responsive behavior here
            pass
        
        root.bind('<Configure>', on_resize)
        
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Failed to start game: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()