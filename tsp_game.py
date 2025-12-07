"""
Traveling Salesman Problem Game Module
Uses brute force and nearest neighbor algorithms
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import itertools
import time

class TSPGame:
    def __init__(self):
        self.cities = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        self.distances = {}
        self.initialize_distances()
    
    def initialize_distances(self):
        for i in range(len(self.cities)):
            for j in range(i + 1, len(self.cities)):
                dist = random.randint(50, 100)
                self.distances[(self.cities[i], self.cities[j])] = dist
                self.distances[(self.cities[j], self.cities[i])] = dist
    
    def get_distance(self, city1, city2):
        return self.distances.get((city1, city2), 100)
    
    def brute_force(self, cities_to_visit, home_city):
        start_time = time.time()
        if not cities_to_visit:
            return 0, time.time() - start_time
            
        min_distance = float('inf')
        
        for perm in itertools.permutations(cities_to_visit):
            current_distance = self.get_distance(home_city, perm[0])
            for i in range(len(perm) - 1):
                current_distance += self.get_distance(perm[i], perm[i + 1])
            current_distance += self.get_distance(perm[-1], home_city)
            min_distance = min(min_distance, current_distance)
        
        return min_distance, time.time() - start_time
    
    def nearest_neighbor(self, cities_to_visit, home_city):
        start_time = time.time()
        if not cities_to_visit:
            return 0, time.time() - start_time
            
        unvisited = set(cities_to_visit)
        current = home_city
        total_distance = 0
        
        while unvisited:
            nearest = min(unvisited, key=lambda city: self.get_distance(current, city))
            total_distance += self.get_distance(current, nearest)
            current = nearest
            unvisited.remove(nearest)
        
        total_distance += self.get_distance(current, home_city)
        return total_distance, time.time() - start_time

class TSPGameUI:
    def __init__(self, root, db, player_name):
        self.root = root
        self.db = db
        self.player_name = player_name
        self.game = TSPGame()
        self.player_score = 0
        self.total_attempts = 0
        self.answer_revealed = False
        
        self.setup_ui()
        self.new_problem()
    
    def setup_ui(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)
        
        title_label = ttk.Label(header_frame, text="🗺️ Traveling Salesman Problem", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.score_label = ttk.Label(header_frame, text="Score: 0/0", 
                                   font=("Arial", 12, "bold"))
        self.score_label.pack(side=tk.RIGHT, padx=10)
        
        # Back button
        back_button = ttk.Button(header_frame, text="← Main Menu", 
                                command=self.back_to_main)
        back_button.pack(side=tk.RIGHT, padx=10)
        
        # City selection
        selection_frame = ttk.LabelFrame(main_frame, text="🏙️ City Selection", padding="10")
        selection_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(selection_frame, text="Select cities to visit:").pack(anchor=tk.W)
        
        self.city_vars = {}
        cities_frame = ttk.Frame(selection_frame)
        cities_frame.pack(fill=tk.X, pady=5)
        
        for i, city in enumerate(self.game.cities):
            var = tk.BooleanVar()
            self.city_vars[city] = var
            cb = ttk.Checkbutton(cities_frame, text=city, variable=var)
            cb.grid(row=i//5, column=i%5, sticky=tk.W, padx=5)
        
        ttk.Button(selection_frame, text="Generate Problem", 
                  command=self.new_problem).pack(pady=5)
        
        # Distance matrix
        matrix_frame = ttk.LabelFrame(main_frame, text="📏 Distance Matrix (km)", padding="10")
        matrix_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.matrix_text = scrolledtext.ScrolledText(matrix_frame, height=8, width=100, font=("Courier", 9))
        self.matrix_text.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="🎯 Your Turn", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Shortest route distance (km):").pack(side=tk.LEFT, padx=5)
        self.answer_entry = ttk.Entry(input_frame, width=10, font=("Arial", 12))
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="🎯 Submit Answer", 
                  command=self.submit_answer).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="🔍 Show Answer", 
                  command=self.show_answer).pack(side=tk.LEFT, padx=5)
    
    def new_problem(self):
        self.answer_revealed = False
        self.home_city = random.choice(self.game.cities)
        self.selected_cities = [city for city, var in self.city_vars.items() if var.get()]
        
        if not self.selected_cities:
            self.selected_cities = random.sample([c for c in self.game.cities if c != self.home_city], 3)
            # Auto-select these cities in the UI
            for city in self.selected_cities:
                self.city_vars[city].set(True)
        
        self.game.initialize_distances()
        
        # Calculate shortest distance
        brute_dist, brute_time = self.game.brute_force(self.selected_cities, self.home_city)
        nn_dist, nn_time = self.game.nearest_neighbor(self.selected_cities, self.home_city)
        
        self.correct_answer = min(brute_dist, nn_dist)
        
        # Display distance matrix
        self.matrix_text.delete(1.0, tk.END)
        self.matrix_text.insert(tk.END, f"Home City: {self.home_city}\n")
        self.matrix_text.insert(tk.END, f"Cities to visit: {', '.join(self.selected_cities)}\n\n")
        
        self.matrix_text.insert(tk.END, "Distance Matrix:\n")
        self.matrix_text.insert(tk.END, "    " + " ".join(f"{city:>4}" for city in [''] + self.game.cities) + "\n")
        for city1 in self.game.cities:
            row = f"{city1:>3}"
            for city2 in self.game.cities:
                dist = self.game.get_distance(city1, city2)
                row += f"{dist:>4}"
            self.matrix_text.insert(tk.END, row + "\n")
        
        self.matrix_text.insert(tk.END, f"\n⚡ Algorithm Results:\n")
        self.matrix_text.insert(tk.END, f"  Brute Force: {brute_dist} km ({brute_time:.6f}s)\n")
        self.matrix_text.insert(tk.END, f"  Nearest Neighbor: {nn_dist} km ({nn_time:.6f}s)\n")
        self.matrix_text.insert(tk.END, f"\n🎯 Find the shortest route distance!\n")
    
    def submit_answer(self):
        try:
            player_answer = float(self.answer_entry.get().strip())
            
            if player_answer < 0:
                messagebox.showerror("Error", "Distance cannot be negative!")
                return
            
            self.total_attempts += 1
            is_correct = abs(player_answer - self.correct_answer) < 0.1
            
            if is_correct:
                self.player_score += 1
            
            # Save to database
            self.db.save_player_response('tsp', {
                'player_name': self.player_name,
                'home_city': self.home_city,
                'selected_cities': ','.join(self.selected_cities),
                'shortest_distance': self.correct_answer,
                'player_answer': player_answer,
                'is_correct': is_correct,
                'brute_force_time': 0.001,
                'nearest_neighbor_time': 0.001,
                'dynamic_programming_time': 0.001
            })
            
            self.display_result(player_answer, is_correct)
            self.update_score_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def display_result(self, player_answer, is_correct):
        self.matrix_text.insert(tk.END, f"\n🎮 Result:\n")
        self.matrix_text.insert(tk.END, f"  Your answer: {player_answer} km\n")
        
        if is_correct:
            self.matrix_text.insert(tk.END, "  🎉 CORRECT! Excellent route! 🎉\n")
            messagebox.showinfo("Result", "CORRECT! 🎉\nYou found the optimal route!")
        else:
            self.matrix_text.insert(tk.END, "  ❌ Incorrect. Try again or click 'Show Answer'! ❌\n")
    
    def show_answer(self):
        if not self.answer_revealed:
            self.matrix_text.insert(tk.END, f"\n🔍 Correct Answer: {self.correct_answer} km\n")
            self.answer_revealed = True
            messagebox.showinfo("Answer", f"The shortest route distance is: {self.correct_answer} km")
    
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.player_score}/{self.total_attempts}")
    
    def back_to_main(self):
        from main_menu import GameCollectionUI
        GameCollectionUI(self.root)