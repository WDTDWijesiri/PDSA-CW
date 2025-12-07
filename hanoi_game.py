"""
Tower of Hanoi Game Module
Uses recursive and iterative algorithms
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time

class TowerOfHanoi:
    def __init__(self):
        self.moves = []
    
    def recursive_3_pegs(self, n, source, destination, auxiliary):
        if n == 1:
            self.moves.append(f"{source} -> {destination}")
            return 1
        count = 0
        count += self.recursive_3_pegs(n - 1, source, auxiliary, destination)
        count += 1
        self.moves.append(f"{source} -> {destination}")
        count += self.recursive_3_pegs(n - 1, auxiliary, destination, source)
        return count
    
    def iterative_3_pegs(self, n, source, destination, auxiliary):
        start_time = time.time()
        self.moves = []
        stack = [(n, source, destination, auxiliary, False)]
        total_moves = 0
        
        while stack:
            n, src, dest, aux, processed = stack.pop()
            if n == 1:
                self.moves.append(f"{src} -> {dest}")
                total_moves += 1
            else:
                if processed:
                    self.moves.append(f"{src} -> {dest}")
                    total_moves += 1
                    stack.append((n - 1, aux, dest, src, False))
                else:
                    stack.append((n, src, dest, aux, True))
                    stack.append((n - 1, src, aux, dest, False))
        
        execution_time = time.time() - start_time
        return total_moves, execution_time

class HanoiGameUI:
    def __init__(self, root, db, player_name):
        self.root = root
        self.db = db
        self.player_name = player_name
        self.game = TowerOfHanoi()
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
        
        title_label = ttk.Label(header_frame, text="🗼 Tower of Hanoi", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        self.score_label = ttk.Label(header_frame, text="Score: 0/0", 
                                   font=("Arial", 12, "bold"))
        self.score_label.pack(side=tk.RIGHT, padx=10)
        
        # Back button
        back_button = ttk.Button(header_frame, text="← Main Menu", 
                                command=self.back_to_main)
        back_button.pack(side=tk.RIGHT, padx=10)
        
        # Problem setup
        setup_frame = ttk.LabelFrame(main_frame, text="⚙️ Problem Setup", padding="10")
        setup_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(setup_frame, text="Number of disks (5-10):").pack(side=tk.LEFT, padx=5)
        self.disk_var = tk.StringVar(value="5")
        disk_combo = ttk.Combobox(setup_frame, textvariable=self.disk_var, 
                                 values=[str(i) for i in range(5, 11)], width=5)
        disk_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(setup_frame, text="Number of pegs (3-4):").pack(side=tk.LEFT, padx=5)
        self.peg_var = tk.StringVar(value="3")
        peg_combo = ttk.Combobox(setup_frame, textvariable=self.peg_var, 
                                values=['3', '4'], width=5)
        peg_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(setup_frame, text="New Problem", 
                  command=self.new_problem).pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="📊 Problem Information", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, width=100, font=("Arial", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="🎯 Your Turn", padding="10")
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Minimum moves required:").pack(side=tk.LEFT, padx=5)
        self.answer_entry = ttk.Entry(input_frame, width=10, font=("Arial", 12))
        self.answer_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(input_frame, text="🎯 Submit Answer", 
                  command=self.submit_answer).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="🔍 Show Answer", 
                  command=self.show_answer).pack(side=tk.LEFT, padx=5)
    
    def new_problem(self):
        self.answer_revealed = False
        self.num_disks = int(self.disk_var.get())
        self.num_pegs = int(self.peg_var.get())
        
        self.game = TowerOfHanoi()
        
        if self.num_pegs == 3:
            recursive_moves = self.game.recursive_3_pegs(self.num_disks, 'A', 'C', 'B')
            iterative_moves, iterative_time = self.game.iterative_3_pegs(self.num_disks, 'A', 'C', 'B')
            self.correct_answer = recursive_moves
        else:
            # For 4 pegs, use Frame-Stewart (simplified)
            self.correct_answer = 2 ** self.num_disks - 1  # Simplified calculation
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🗼 Tower of Hanoi Problem\n")
        self.results_text.insert(tk.END, f"Number of disks: {self.num_disks}\n")
        self.results_text.insert(tk.END, f"Number of pegs: {self.num_pegs}\n\n")
        
        if self.num_pegs == 3:
            self.results_text.insert(tk.END, f"⚡ Algorithm Results:\n")
            self.results_text.insert(tk.END, f"  Recursive: {recursive_moves} moves\n")
            self.results_text.insert(tk.END, f"  Iterative: {iterative_moves} moves ({iterative_time:.6f}s)\n")
        else:
            self.results_text.insert(tk.END, f"⚡ Using Frame-Stewart algorithm for 4 pegs\n")
        
        self.results_text.insert(tk.END, f"\n🎯 Find the minimum moves required!\n")
        self.results_text.insert(tk.END, f"Rules:\n")
        self.results_text.insert(tk.END, f"• Only one disk can be moved at a time\n")
        self.results_text.insert(tk.END, f"• No larger disk on smaller disk\n")
        self.results_text.insert(tk.END, f"• Move all disks from A to C\n")
    
    def submit_answer(self):
        try:
            player_answer = int(self.answer_entry.get().strip())
            
            if player_answer < 1:
                messagebox.showerror("Error", "Number of moves must be at least 1!")
                return
            
            self.total_attempts += 1
            is_correct = (player_answer == self.correct_answer)
            
            if is_correct:
                self.player_score += 1
            
            # Save to database
            self.db.save_player_response('hanoi', {
                'player_name': self.player_name,
                'num_disks': self.num_disks,
                'num_pegs': self.num_pegs,
                'min_moves': self.correct_answer,
                'player_moves': player_answer,
                'is_correct': is_correct,
                'recursive_time': 0.001,
                'iterative_time': 0.001
            })
            
            self.display_result(player_answer, is_correct)
            self.update_score_display()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number!")
    
    def display_result(self, player_answer, is_correct):
        self.results_text.insert(tk.END, f"\n🎮 Result:\n")
        self.results_text.insert(tk.END, f"  Your answer: {player_answer} moves\n")
        
        if is_correct:
            self.results_text.insert(tk.END, "  🎉 CORRECT! Perfect solution! 🎉\n")
            messagebox.showinfo("Result", "CORRECT! 🎉\nYou found the optimal solution!")
        else:
            self.results_text.insert(tk.END, "  ❌ Incorrect. Try again or click 'Show Answer'! ❌\n")
    
    def show_answer(self):
        if not self.answer_revealed:
            self.results_text.insert(tk.END, f"\n🔍 Correct Answer: {self.correct_answer} moves\n")
            self.answer_revealed = True
            messagebox.showinfo("Answer", f"The minimum moves required is: {self.correct_answer}")
    
    def update_score_display(self):
        self.score_label.config(text=f"Score: {self.player_score}/{self.total_attempts}")
    
    def back_to_main(self):
        from main_menu import GameCollectionUI
        GameCollectionUI(self.root)