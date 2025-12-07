"""
Snake and Ladder Game Module
Shortest path problem using BFS and Dijkstra's algorithm
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
from collections import deque
import heapq
import time

class SnakeLadderGame:
    def __init__(self, board_size):
        self.board_size = board_size
        self.total_cells = board_size * board_size
        self.snakes = {}
        self.ladders = {}
        self.initialize_board()
    
    def initialize_board(self):
        num_obstacles = self.board_size - 2
        
        # Create snakes
        for _ in range(num_obstacles):
            while True:
                start = random.randint(self.board_size + 1, self.total_cells - 1)
                end = random.randint(1, start - self.board_size)
                if start not in self.snakes and start not in self.ladders:
                    self.snakes[start] = end
                    break
        
        # Create ladders
        for _ in range(num_obstacles):
            while True:
                start = random.randint(1, self.total_cells - self.board_size)
                end = random.randint(start + self.board_size, self.total_cells)
                if start not in self.ladders and start not in self.snakes:
                    self.ladders[start] = end
                    break
    
    def bfs_min_throws(self):
        start_time = time.time()
        visited = [False] * (self.total_cells + 1)
        queue = deque([(1, 0)])
        visited[1] = True
        
        while queue:
            pos, throws = queue.popleft()
            for dice in range(1, 7):
                next_pos = self.get_next_position(pos, dice)
                if next_pos == self.total_cells:
                    return throws + 1, time.time() - start_time
                if not visited[next_pos]:
                    visited[next_pos] = True
                    queue.append((next_pos, throws + 1))
        return -1, time.time() - start_time
    
    def dijkstra_min_throws(self):
        start_time = time.time()
        dist = [float('inf')] * (self.total_cells + 1)
        dist[1] = 0
        heap = [(0, 1)]
        
        while heap:
            throws, pos = heapq.heappop(heap)
            if throws > dist[pos]:
                continue
            if pos == self.total_cells:
                return throws, time.time() - start_time
            for dice in range(1, 7):
                next_pos = self.get_next_position(pos, dice)
                if next_pos <= self.total_cells and throws + 1 < dist[next_pos]:
                    dist[next_pos] = throws + 1
                    heapq.heappush(heap, (throws + 1, next_pos))
        return -1, time.time() - start_time
    
    def get_next_position(self, current_pos, dice_roll):
        new_pos = current_pos + dice_roll
        if new_pos > self.total_cells:
            return current_pos
        return self.snakes.get(new_pos, self.ladders.get(new_pos, new_pos))

class SnakeLadderGameUI:
    def __init__(self, root, db, player_name):
        self.root = root
        self.db = db
        self.player_name = player_name
        self.board_size = 6
        self.game = None
        self.player_score = 0
        self.total_attempts = 0
        self.answer_revealed = False
        
        self.setup_ui()
        self.new_game()
    
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
        
        title_label = ttk.Label(header_frame, text="🐍 Snake and Ladder Game", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.score_label = ttk.Label(header_frame, text="Score: 0/0", 
                                   font=("Arial", 12, "bold"))
        self.score_label.pack(side=tk.RIGHT, padx=10)
        
        # Back button
        back_button = ttk.Button(header_frame, text="← Main Menu", 
                                command=self.back_to_main)
        back_button.pack(side=tk.RIGHT, padx=10)
        
        # Board size selection
        size_frame = ttk.LabelFrame(main_frame, text="🎲 Board Setup", padding="10")
        size_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(size_frame, text="Board Size (6-12):").pack(side=tk.LEFT, padx=5)
        self.size_var = tk.StringVar(value="6")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, 
                                 values=[str(i) for i in range(6, 13)], width=5)
        size_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(size_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)
        
        # Visual board display
        board_frame = ttk.LabelFrame(main_frame, text="🎯 Game Board Visualization", padding="10")
        board_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.board_canvas = tk.Canvas(board_frame, bg='white', height=400)
        self.board_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="📊 Game Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=8, width=100, font=("Arial", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="🎲 Your Turn", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Minimum dice throws to reach the end:").pack(side=tk.LEFT, padx=5)
        self.answer_entry = ttk.Entry(input_frame, width=10, font=("Arial", 12))
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="🎯 Submit Answer", 
                  command=self.submit_answer).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="🔍 Show Answer", 
                  command=self.show_answer).pack(side=tk.LEFT, padx=5)
    
    def draw_board(self):
        self.board_canvas.delete("all")
        cell_size = 30
        margin = 50
        
        # Draw board grid
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1 = margin + j * cell_size
                y1 = margin + i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                cell_num = i * self.board_size + j + 1
                if (i + j) % 2 == 0:
                    color = "lightblue"
                else:
                    color = "white"
                
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
                self.board_canvas.create_text(x1 + cell_size//2, y1 + cell_size//2, text=str(cell_num))
        
        # Draw snakes (red lines)
        for start, end in self.game.snakes.items():
            start_row = (start - 1) // self.board_size
            start_col = (start - 1) % self.board_size
            end_row = (end - 1) // self.board_size
            end_col = (end - 1) % self.board_size
            
            x1 = margin + start_col * cell_size + cell_size//2
            y1 = margin + start_row * cell_size + cell_size//2
            x2 = margin + end_col * cell_size + cell_size//2
            y2 = margin + end_row * cell_size + cell_size//2
            
            self.board_canvas.create_line(x1, y1, x2, y2, fill="red", width=3, arrow=tk.LAST)
        
        # Draw ladders (green lines)
        for start, end in self.game.ladders.items():
            start_row = (start - 1) // self.board_size
            start_col = (start - 1) % self.board_size
            end_row = (end - 1) // self.board_size
            end_col = (end - 1) % self.board_size
            
            x1 = margin + start_col * cell_size + cell_size//2
            y1 = margin + start_row * cell_size + cell_size//2
            x2 = margin + end_col * cell_size + cell_size//2
            y2 = margin + end_row * cell_size + cell_size//2
            
            self.board_canvas.create_line(x1, y1, x2, y2, fill="green", width=3, arrow=tk.LAST)
    
    def new_game(self):
        try:
            self.board_size = int(self.size_var.get())
            if not 6 <= self.board_size <= 12:
                raise ValueError("Board size must be between 6 and 12")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid board size (6-12)")
            return
        
        self.answer_revealed = False
        self.game = SnakeLadderGame(self.board_size)
        self.draw_board()
        
        # Calculate minimum throws
        bfs_throws, bfs_time = self.game.bfs_min_throws()
        dijkstra_throws, dijkstra_time = self.game.dijkstra_min_throws()
        
        self.correct_answer = min(bfs_throws, dijkstra_throws)
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🎲 Snake and Ladder Board ({self.board_size}x{self.board_size})\n")
        self.results_text.insert(tk.END, f"Total cells: {self.game.total_cells}\n\n")
        
        self.results_text.insert(tk.END, "🐍 Snakes:\n")
        for start, end in self.game.snakes.items():
            self.results_text.insert(tk.END, f"  {start} → {end}\n")
        
        self.results_text.insert(tk.END, "\n🪜 Ladders:\n")
        for start, end in self.game.ladders.items():
            self.results_text.insert(tk.END, f"  {start} → {end}\n")
        
        self.results_text.insert(tk.END, f"\n⚡ Algorithm Results:\n")
        self.results_text.insert(tk.END, f"  BFS: {bfs_throws} throws ({bfs_time:.6f}s)\n")
        self.results_text.insert(tk.END, f"  Dijkstra: {dijkstra_throws} throws ({dijkstra_time:.6f}s)\n")
        self.results_text.insert(tk.END, f"\n🎯 Find the minimum dice throws needed!\n")
    
    def submit_answer(self):
        try:
            player_answer = int(self.answer_entry.get().strip())
            
            if player_answer < 1:
                messagebox.showerror("Error", "Number of throws must be at least 1!")
                return
            
            self.total_attempts += 1
            is_correct = (player_answer == self.correct_answer)
            
            if is_correct:
                self.player_score += 1
            
            # Save to database
            self.db.save_player_response('snake_ladder', {
                'player_name': self.player_name,
                'board_size': self.board_size,
                'correct_answer': self.correct_answer,
                'player_answer': player_answer,
                'is_correct': is_correct,
                'bfs_time': 0.001,
                'dijkstra_time': 0.001
            })
            
            self.display_result(player_answer, is_correct)
            self.update_score_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def display_result(self, player_answer, is_correct):
        self.results_text.insert(tk.END, f"\n🎮 Result:\n")
        self.results_text.insert(tk.END, f"  Your answer: {player_answer}\n")
        
        if is_correct:
            self.results_text.insert(tk.END, "  🎉 CORRECT! Excellent! 🎉\n")
            messagebox.showinfo("Result", "CORRECT! 🎉\nYou found the optimal path!")
        else:
            self.results_text.insert(tk.END, "  ❌ Incorrect. Try again or click 'Show Answer'! ❌\n")
    
    def show_answer(self):
        if not self.answer_revealed:
            self.results_text.insert(tk.END, f"\n🔍 Correct Answer: {self.correct_answer} throws\n")
            self.answer_revealed = True
            messagebox.showinfo("Answer", f"The minimum throws required is: {self.correct_answer}")
    
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.player_score}/{self.total_attempts}")
    
    def back_to_main(self):
        from main_menu import GameCollectionUI
        GameCollectionUI(self.root)