"""
Eight Queens Puzzle Game Module
Uses sequential and threaded backtracking algorithms
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import threading

class EightQueens:
    def __init__(self):
        self.solutions = []
        self.found_solutions = set()
    
    def is_safe(self, board, row, col):
        for i in range(row):
            if board[i] == col or abs(board[i] - col) == abs(i - row):
                return False
        return True
    
    def solve_sequential(self):
        start_time = time.time()
        solutions = []
        
        def solve(board, row):
            if row == 8:
                solutions.append(tuple(board))
                return
            for col in range(8):
                if self.is_safe(board, row, col):
                    board[row] = col
                    solve(board, row + 1)
                    board[row] = -1
        
        solve([-1] * 8, 0)
        execution_time = time.time() - start_time
        return len(solutions), execution_time
    
    def solve_threaded(self):
        start_time = time.time()
        results = []
        threads = []
        
        def solve_for_first_row(start_col, result_list):
            local_solutions = []
            board = [-1] * 8
            board[0] = start_col
            
            def solve_local(board, row):
                if row == 8:
                    local_solutions.append(tuple(board))
                    return
                for col in range(8):
                    if self.is_safe(board, row, col):
                        board[row] = col
                        solve_local(board, row + 1)
                        board[row] = -1
            
            solve_local(board, 1)
            result_list.extend(local_solutions)
        
        for col in range(8):
            thread = threading.Thread(target=solve_for_first_row, args=(col, results))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        execution_time = time.time() - start_time
        return len(set(results)), execution_time

class QueensGameUI:
    def __init__(self, root, db, player_name):
        self.root = root
        self.db = db
        self.player_name = player_name
        self.game = EightQueens()
        self.player_score = 0
        self.total_attempts = 0
        
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
        
        title_label = ttk.Label(header_frame, text="♕ Eight Queens Puzzle", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.score_label = ttk.Label(header_frame, text="Score: 0/0", 
                                   font=("Arial", 12, "bold"))
        self.score_label.pack(side=tk.RIGHT, padx=10)
        
        # Back button
        back_button = ttk.Button(header_frame, text="← Main Menu", 
                                command=self.back_to_main)
        back_button.pack(side=tk.RIGHT, padx=10)
        
        # Chessboard
        board_frame = ttk.LabelFrame(main_frame, text="♟️ Chessboard", padding="10")
        board_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.board_canvas = tk.Canvas(board_frame, bg='white', height=400, width=400)
        self.board_canvas.pack()
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="📊 Algorithm Performance", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=6, width=100, font=("Arial", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="🎯 Your Turn", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Enter solution (8 numbers 0-7, space separated):").pack(side=tk.LEFT, padx=5)
        self.answer_entry = ttk.Entry(input_frame, width=20, font=("Arial", 12))
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="🎯 Submit Solution", 
                  command=self.submit_solution).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="🔄 New Problem", 
                  command=self.new_problem).pack(side=tk.LEFT, padx=5)
    
    def draw_chessboard(self):
        self.board_canvas.delete("all")
        cell_size = 50
        
        # Draw chessboard
        for i in range(8):
            for j in range(8):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                if (i + j) % 2 == 0:
                    color = "white"
                else:
                    color = "lightgray"
                
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
    
    def new_problem(self):
        self.draw_chessboard()
        
        # Calculate solutions
        sequential_count, sequential_time = self.game.solve_sequential()
        threaded_count, threaded_time = self.game.solve_threaded()
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"♕ Eight Queens Puzzle\n\n")
        self.results_text.insert(tk.END, f"⚡ Algorithm Performance:\n")
        self.results_text.insert(tk.END, f"  Sequential: {sequential_count} solutions ({sequential_time:.6f}s)\n")
        self.results_text.insert(tk.END, f"  Threaded: {threaded_count} solutions ({threaded_time:.6f}s)\n")
        self.results_text.insert(tk.END, f"\n🎯 Find a valid solution where no queens attack each other!\n")
        self.results_text.insert(tk.END, f"Enter column positions for rows 0-7 (e.g., '0 4 7 5 2 6 1 3')\n")
    
    def submit_solution(self):
        try:
            solution_input = self.answer_entry.get().strip()
            solution = [int(x) for x in solution_input.split()]
            
            if len(solution) != 8:
                messagebox.showerror("Error", "Please enter exactly 8 numbers!")
                return
            
            if any(x < 0 or x > 7 for x in solution):
                messagebox.showerror("Error", "All numbers must be between 0 and 7!")
                return
            
            # Check if solution is valid
            is_valid = True
            board = [-1] * 8
            for i in range(8):
                board[i] = solution[i]
                if not self.game.is_safe(board, i, solution[i]):
                    is_valid = False
                    break
            
            self.total_attempts += 1
            
            if is_valid:
                self.player_score += 1
                # Save to database
                self.db.save_player_response('queens', {
                    'player_name': self.player_name,
                    'solution': ' '.join(map(str, solution)),
                    'is_unique': True,
                    'sequential_time': 0.001,
                    'threaded_time': 0.001
                })
                
                self.display_result(True)
                self.draw_solution(solution)
            else:
                self.display_result(False)
            
            self.update_score_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers separated by spaces!")
    
    def draw_solution(self, solution):
        self.draw_chessboard()
        cell_size = 50
        
        for row, col in enumerate(solution):
            x = col * cell_size + cell_size // 2
            y = row * cell_size + cell_size // 2
            self.board_canvas.create_text(x, y, text="♕", font=("Arial", 20), fill="red")
    
    def display_result(self, is_valid):
        self.results_text.insert(tk.END, f"\n🎮 Result:\n")
        
        if is_valid:
            self.results_text.insert(tk.END, "  🎉 VALID SOLUTION! Well done! 🎉\n")
            messagebox.showinfo("Result", "VALID SOLUTION! 🎉\nAll queens are safe!")
        else:
            self.results_text.insert(tk.END, "  ❌ INVALID SOLUTION. Queens are attacking! ❌\n")
            messagebox.showinfo("Result", "INVALID SOLUTION!\nQueens are attacking each other.")
    
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.player_score}/{self.total_attempts}")
    
    def back_to_main(self):
        from main_menu import GameCollectionUI
        GameCollectionUI(self.root)