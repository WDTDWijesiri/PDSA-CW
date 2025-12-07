"""
Main Menu Module
Provides the main interface for game selection
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import GameDatabase
from instructions import InstructionsDialog

class GameCollectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Computer Science Game Collection")
        self.root.geometry("1200x800")
        
        self.db = GameDatabase()
        self.current_player = "Player1"
        self.current_game = None
        
        self.setup_main_menu()
    
    def setup_main_menu(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main menu frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎮 COMPUTER SCIENCE GAME COLLECTION", 
                               font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(main_frame, text="Explore Algorithms Through Interactive Games!", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=10)
        
        # Player info
        player_frame = ttk.Frame(main_frame)
        player_frame.pack(pady=10)
        
        ttk.Label(player_frame, text="Player Name:").pack(side=tk.LEFT, padx=5)
        self.player_entry = ttk.Entry(player_frame, width=20)
        self.player_entry.pack(side=tk.LEFT, padx=5)
        self.player_entry.insert(0, self.current_player)
        
        ttk.Button(player_frame, text="Update", command=self.update_player).pack(side=tk.LEFT, padx=5)
        
        # Games grid
        games_frame = ttk.LabelFrame(main_frame, text="🎯 Select a Game", padding="20")
        games_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Create game buttons
        games = [
            ("🐍 Snake & Ladder", self.start_snake_ladder),
            ("🚦 Traffic Simulation", self.start_traffic_simulation),
            ("🗺️ Traveling Salesman", self.start_tsp),
            ("🗼 Tower of Hanoi", self.start_hanoi),
            ("♕ Eight Queens", self.start_queens),
            ("📊 Statistics", self.show_statistics),
            ("❓ How to Play", self.show_instructions),
            ("❌ Exit", self.exit_game)
        ]
        
        for i, (game_name, command) in enumerate(games):
            btn = ttk.Button(games_frame, text=game_name, command=command, width=20)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights
        games_frame.columnconfigure(0, weight=1)
        games_frame.columnconfigure(1, weight=1)
    
    def update_player(self):
        name = self.player_entry.get().strip()
        if name:
            self.current_player = name
            messagebox.showinfo("Success", f"Player name updated to: {name}")
    
    def start_traffic_simulation(self):
        from traffic_game import TrafficSimulationGame
        self.current_game = TrafficSimulationGame(self.root, self.db, self.current_player)
    
    def start_snake_ladder(self):
        from snake_ladder_game import SnakeLadderGameUI
        self.current_game = SnakeLadderGameUI(self.root, self.db, self.current_player)
    
    def start_tsp(self):
        from tsp_game import TSPGameUI
        self.current_game = TSPGameUI(self.root, self.db, self.current_player)
    
    def start_hanoi(self):
        from hanoi_game import HanoiGameUI
        self.current_game = HanoiGameUI(self.root, self.db, self.current_player)
    
    def start_queens(self):
        from queens_game import QueensGameUI
        self.current_game = QueensGameUI(self.root, self.db, self.current_player)
    
    def show_statistics(self):
        messagebox.showinfo("Statistics", "Game statistics feature coming soon!")
    
    def show_instructions(self):
        InstructionsDialog(self.root)
    
    def exit_game(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.db.close()
            self.root.quit()