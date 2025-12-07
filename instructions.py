"""
Instructions Dialog Module
Provides help and instructions for all games
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

class InstructionsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.show_instructions()
    
    def show_instructions(self):
        instructions_window = tk.Toplevel(self.parent)
        instructions_window.title("🎮 How to Play - Game Collection")
        instructions_window.geometry("800x600")
        instructions_window.transient(self.parent)
        instructions_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(instructions_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎮 Welcome to Computer Science Game Collection!", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Notebook for different games
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add instruction tabs for all games
        games_instructions = {
            "🚦 Traffic Simulation": """
🎯 OBJECTIVE:
Calculate the MAXIMUM FLOW of vehicles from Source (A) to Sink (T) 
through the traffic network without exceeding road capacities!

📊 THE NETWORK:
• Source: A (Start point)
• Sink: T (Destination)  
• Intermediate Nodes: B, C, D, E, F, G, H
• Roads: Directed edges with capacity limits
• Capacities: Randomly generated between 5-15 vehicles/minute

🎮 HOW TO PLAY:
1. Each round presents a NEW random network
2. Study the network visualization and road capacities
3. Calculate the MAXIMUM FLOW from A to T
4. Enter your answer and submit
5. Use 'Show Answer' if you need help

⚡ ALGORITHMS USED:
• Ford-Fulkerson: Finds augmenting paths
• Edmonds-Karp: BFS-based max flow
""",
            "🐍 Snake & Ladder": """
🎯 OBJECTIVE:
Find the MINIMUM NUMBER OF DICE THROWS required to reach the final cell!

📊 GAME BOARD:
• Board size: 6x6 to 12x12 (you choose)
• Snakes: Slide you down when landed on
• Ladders: Climb you up when landed on
• Start: Cell 1
• Goal: Final cell (N×N)

🎮 HOW TO PLAY:
1. Choose board size (6-12)
2. Study the snake and ladder positions
3. Calculate minimum dice throws to reach end
4. Enter your answer and submit
5. Use 'Show Answer' if you need help

⚡ ALGORITHMS USED:
• BFS (Breadth-First Search): Explores all possible moves
• Dijkstra's Algorithm: Finds shortest path considering obstacles
""",
            "🗺️ Traveling Salesman": """
🎯 OBJECTIVE:
Find the SHORTEST ROUTE visiting all selected cities and returning home!

📊 PROBLEM SETUP:
• 10 cities (A-J) with random distances (50-100km)
• Home city randomly selected
• You choose which cities to visit
• Find optimal round trip

🎮 HOW TO PLAY:
1. Select cities to visit using checkboxes
2. Study the distance matrix
3. Calculate shortest route distance
4. Enter your answer and submit
5. Use 'Show Answer' if you need help

⚡ ALGORITHMS USED:
• Brute Force: Checks all permutations
• Nearest Neighbor: Greedy heuristic approach
""",
            "🗼 Tower of Hanoi": """
🎯 OBJECTIVE:
Find the MINIMUM MOVES required to solve the Tower of Hanoi puzzle!

📊 PROBLEM SETUP:
• Disks: 5-10 (you choose)
• Pegs: 3 or 4 (you choose)
• Move all disks from source to destination
• Larger disks cannot be on smaller disks

🎮 HOW TO PLAY:
1. Select number of disks and pegs
2. Calculate minimum moves required
3. Enter your answer and submit
4. Use 'Show Answer' if you need help

⚡ ALGORITHMS USED:
• Recursive: Classic recursive solution
• Iterative: Stack-based implementation
• Frame-Stewart: For 4 pegs
""",
            "♕ Eight Queens": """
🎯 OBJECTIVE:
Place 8 queens on a chessboard so that no two queens attack each other!

📊 PROBLEM SETUP:
• Standard 8x8 chessboard
• Queens cannot share rows, columns, or diagonals
• Find any valid configuration

🎮 HOW TO PLAY:
1. Enter column positions for rows 0-7
2. Format: 8 numbers 0-7 separated by spaces
3. Submit your solution
4. Algorithm verifies if queens are safe

⚡ ALGORITHMS USED:
• Sequential Backtracking: Systematic search
• Threaded Parallel: Multi-threaded solution finding
"""
        }
        
        for game_name, instructions in games_instructions.items():
            frame = ttk.Frame(notebook, padding="10")
            notebook.add(frame, text=game_name)
            
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Arial", 10))
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(1.0, instructions)
            text.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(main_frame, text="Start Playing! 🎮", 
                                 command=instructions_window.destroy)
        close_button.pack(pady=10)