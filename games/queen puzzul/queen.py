import tkinter as tk
from tkinter import ttk, messagebox
import time
import sqlite3
from datetime import datetime
import random
from pathlib import Path

class EightQueensGame:
    def __init__(self, root):
        self.root = root
        self.root.title("♛ Eight Queens Challenge ♛")
        self.root.geometry("1400x900")
        
        # Gaming theme colors
        self.colors = {
            'bg': '#0f0f23',
            'bg_dark': '#0a0a18',
            'bg_light': '#1a1a3a',
            'board_dark': '#2d2d5a',
            'board_light': '#3d3d7a',
            'queen': '#ff6b8b',
            'queen_glow': '#ff2e63',
            'queen_highlight': '#ff9eb5',
            'conflict': '#ff4757',
            'safe': '#2ed573',
            'text': '#f1f2f6',
            'text_light': '#dfe4ea',
            'button': '#3742fa',
            'button_hover': '#5352ed',
            'button_alt': '#ffa502',
            'success': '#7bed9f',
            'warning': '#ff9f43',
            'error': '#ff6b81',
            'gold': '#ffd700',
            'silver': '#c0c0c0',
            'bronze': '#cd7f32'
        }
        
        # Game state
        self.board_size = 8
        self.queens = []
        self.identified_solutions = set()
        self.player_name = ""
        self.player_score = 0
        self.player_level = 1
        self.game_time = 0
        self.game_start_time = 0
        self.hints_used = 0
        self.max_hints = 3
        self.timer_running = False
        self.timer_id = None
        
        # Database
        self.db_path = Path("queen_challenge.db")
        self.init_database()
        
        # Preload solutions
        self.preload_solutions()
        
        # Start with welcome screen
        self.show_welcome_screen()
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                score INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                games_played INTEGER DEFAULT 0,
                solutions_found INTEGER DEFAULT 0,
                best_time REAL DEFAULT 0,
                total_time REAL DEFAULT 0,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution TEXT UNIQUE,
                discovered_by TEXT,
                discovery_time REAL,
                discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                score_gained INTEGER,
                level_reached INTEGER,
                time_spent REAL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def preload_solutions(self):
        """Preload or generate solutions"""
        try:
            self.cursor.execute("SELECT solution FROM solutions")
            results = self.cursor.fetchall()
            self.identified_solutions = {r[0] for r in results}
            
            if len(self.identified_solutions) < 92:
                # Generate solutions in main thread
                self.generate_solutions()
        except:
            self.identified_solutions = set()
    
    def generate_solutions(self):
        """Generate all 92 solutions using backtracking"""
        all_solutions = self.solve_backtracking()
        
        # Save to database
        for solution in all_solutions:
            try:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO solutions (solution) VALUES (?)",
                    (solution,)
                )
            except:
                pass
        
        self.conn.commit()
        self.identified_solutions = set(all_solutions)
    
    def solve_backtracking(self):
        """Backtracking algorithm to find all solutions"""
        solutions = []
        
        def is_safe(board, row, col):
            for i in range(row):
                if board[i] == col or abs(board[i] - col) == abs(i - row):
                    return False
            return True
        
        def backtrack(board, row):
            if row == 8:
                solution = ''.join(str(col + 1) for col in board)
                solutions.append(solution)
                return
            for col in range(8):
                if is_safe(board, row, col):
                    board[row] = col
                    backtrack(board, row + 1)
                    board[row] = -1
        
        board = [-1] * 8
        backtrack(board, 0)
        
        return solutions
    
    def clear_window(self):
        """Clear all widgets and stop timer"""
        # Stop timer if running
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            self.timer_running = False
        
        # Clear widgets
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_welcome_screen(self):
        """Show welcome screen"""
        self.clear_window()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title frame
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(pady=50)
        
        self.title_label = tk.Label(
            title_frame, 
            text="♛ EIGHT QUEENS CHALLENGE ♛",
            font=("Impact", 64, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['queen']
        )
        self.title_label.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            title_frame,
            text="The Ultimate Chess Puzzle Challenge",
            font=("Arial", 24, "italic"),
            bg=self.colors['bg'],
            fg=self.colors['text_light']
        )
        subtitle.pack(pady=10)
        
        # Start button
        start_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        start_frame.pack(pady=50)
        
        self.start_button = tk.Button(
            start_frame,
            text="🎮 START GAME",
            command=self.show_player_setup,
            font=("Impact", 32, "bold"),
            bg=self.colors['button'],
            fg='white',
            activebackground=self.colors['button_hover'],
            activeforeground='white',
            padx=50,
            pady=20,
            cursor="hand2",
            relief=tk.RAISED,
            bd=5
        )
        self.start_button.pack()
        self.add_button_glow(self.start_button)
        
        # Stats summary
        stats_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        stats_frame.pack(pady=30)
        
        # Get global stats
        try:
            self.cursor.execute("SELECT COUNT(*) FROM players")
            total_players = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT COUNT(*) FROM solutions WHERE discovered_by IS NOT NULL")
            found_solutions = self.cursor.fetchone()[0] or 0
            
            stats_text = f"👑 {total_players} Players | 🏆 {found_solutions}/92 Solutions Found"
            tk.Label(
                stats_frame,
                text=stats_text,
                font=("Arial", 16),
                bg=self.colors['bg'],
                fg=self.colors['text_light']
            ).pack()
        except:
            pass
    
    def add_button_glow(self, button):
        """Add glowing effect to button"""
        def on_enter(e):
            button.config(bg=self.colors['button_hover'])
        
        def on_leave(e):
            button.config(bg=self.colors['button'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def show_player_setup(self):
        """Show player name entry screen"""
        self.clear_window()
        
        # Background
        bg_frame = tk.Frame(self.root, bg=self.colors['bg'])
        bg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Main content
        content_frame = tk.Frame(bg_frame, bg=self.colors['bg'])
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(
            content_frame,
            text="ENTER THE ARENA",
            font=("Impact", 48, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['queen']
        ).pack(pady=(0, 10))
        
        tk.Label(
            content_frame,
            text="Claim Your Throne",
            font=("Arial", 24, "italic"),
            bg=self.colors['bg'],
            fg=self.colors['text_light']
        ).pack(pady=(0, 40))
        
        # Name entry
        entry_frame = tk.Frame(content_frame, bg=self.colors['bg_light'], 
                             relief=tk.RAISED, bd=5)
        entry_frame.pack(pady=20)
        
        tk.Label(
            entry_frame,
            text="YOUR ROYAL NAME:",
            font=("Arial", 18, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['queen_highlight']
        ).pack(pady=20, padx=40)
        
        self.name_entry = tk.Entry(
            entry_frame,
            font=("Arial", 24, "bold"),
            bg=self.colors['board_dark'],
            fg='white',
            insertbackground='white',
            width=20,
            justify='center'
        )
        self.name_entry.pack(pady=20, padx=40)
        self.name_entry.focus()
        
        # Auto-generate button
        def generate_name():
            names = ["QueenSlayer", "ChessMaster", "RoyalGuard", "PawnPromoter",
                    "CheckmateKing", "BishopHunter", "KnightRider", "RookDestroyer"]
            titles = ["The Wise", "The Bold", "The Quick", "The Strategic",
                     "The Unbeaten", "The Legend", "The Conqueror"]
            name = f"{random.choice(names)} {random.choice(titles)}"
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
        
        tk.Button(
            entry_frame,
            text="🎲 Generate Royal Name",
            command=generate_name,
            font=("Arial", 12),
            bg=self.colors['button_alt'],
            fg='white',
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack(pady=(0, 20))
        
        # Start game button
        def start_with_name():
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showwarning("Royal Decree", "A monarch must have a name!")
                return
            
            self.player_name = name
            self.register_player()
            self.show_tutorial()
        
        start_button = tk.Button(
            content_frame,
            text="⚔️ BEGIN CHALLENGE ⚔️",
            command=start_with_name,
            font=("Impact", 28, "bold"),
            bg=self.colors['success'],
            fg='white',
            padx=40,
            pady=20,
            cursor="hand2"
        )
        start_button.pack(pady=30)
        self.add_button_glow(start_button)
        
        # Back button
        tk.Button(
            content_frame,
            text="← Return to Throne Room",
            command=self.show_welcome_screen,
            font=("Arial", 14),
            bg=self.colors['bg_light'],
            fg=self.colors['text'],
            padx=20,
            pady=10,
            cursor="hand2"
        ).pack()
    
    def register_player(self):
        """Register or update player in database"""
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO players (name) VALUES (?)
            ''', (self.player_name,))
            
            # Get current stats
            self.cursor.execute('''
                SELECT score, level FROM players WHERE name = ?
            ''', (self.player_name,))
            result = self.cursor.fetchone()
            
            if result:
                self.player_score, self.player_level = result
            else:
                self.player_score = 0
                self.player_level = 1
            
            self.conn.commit()
        except Exception as e:
            print(f"Error registering player: {e}")
            self.player_score = 0
            self.player_level = 1
    
    def show_tutorial(self):
        """Show interactive tutorial"""
        self.clear_window()
        
        # Create tutorial slides
        tutorial_slides = [
            {
                "title": "👑 THE ROYAL CHALLENGE",
                "content": """Welcome to the Eight Queens Challenge!

Your mission is to place 8 queens on a chessboard so that none can attack each other.

Queens can move:
• Any number of squares vertically
• Any number of squares horizontally
• Any number of squares diagonally

No two queens can share the same row, column, or diagonal!""",
                "image": "♛"
            },
            {
                "title": "🎮 GAME CONTROLS",
                "content": """• CLICK any square to place a queen
• CLICK a queen to remove it
• You must place exactly 8 queens
• No conflicts allowed!

Use the tools on the right:
• CHECK SOLUTION - Verify your placement
• HINT - Get help when stuck
• GIVE UP - Reveal a solution (penalty applies)
• NEW BOARD - Start fresh""",
                "image": "🎯"
            },
            {
                "title": "🏆 SCORING SYSTEM",
                "content": """• Find a NEW solution: +1000 points
• Find a KNOWN solution: +500 points
• Use a HINT: -100 points
• GIVE UP: -200 points
• Time bonus: Faster solutions earn more!

Level up by finding solutions:
• Level 1: 0 solutions
• Level 2: 1 solution
• Level 5: 10 solutions
• Level 10: All 92 solutions!""",
                "image": "⭐"
            },
            {
                "title": "💡 PRO TIPS",
                "content": """1. Start with queens in different rows
2. Avoid placing queens in same columns
3. Watch for diagonal attacks
4. Use symmetry to your advantage
5. Try the 4-queen test first
6. Remember: There are 92 unique solutions!

Ready to claim your throne?""",
                "image": "💎"
            }
        ]
        
        # Background
        bg_frame = tk.Frame(self.root, bg=self.colors['bg'])
        bg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tutorial content
        content_frame = tk.Frame(bg_frame, bg=self.colors['bg_light'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        tutorial_title = tk.Label(
            content_frame,
            text=tutorial_slides[0]["title"],
            font=("Impact", 36, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['queen']
        )
        tutorial_title.pack(pady=30)
        
        # Content with image
        mid_frame = tk.Frame(content_frame, bg=self.colors['bg_light'])
        mid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left - Image
        image_frame = tk.Frame(mid_frame, bg=self.colors['bg_light'])
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        
        tutorial_image = tk.Label(
            image_frame,
            text=tutorial_slides[0]["image"],
            font=("Arial", 120, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['queen_highlight']
        )
        tutorial_image.pack(expand=True)
        
        # Right - Text
        text_frame = tk.Frame(mid_frame, bg=self.colors['bg_light'])
        text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20)
        
        tutorial_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 18),
            bg=self.colors['board_dark'],
            fg=self.colors['text'],
            padx=30,
            pady=30,
            relief=tk.FLAT,
            height=10
        )
        tutorial_text.pack(fill=tk.BOTH, expand=True)
        tutorial_text.insert(1.0, tutorial_slides[0]["content"])
        tutorial_text.config(state=tk.DISABLED)
        
        # Navigation
        nav_frame = tk.Frame(content_frame, bg=self.colors['bg_light'])
        nav_frame.pack(pady=30)
        
        # Skip tutorial button
        tk.Button(
            nav_frame,
            text="Skip Tutorial → Start Game",
            command=self.start_game,
            font=("Arial", 14, "bold"),
            bg=self.colors['warning'],
            fg='black',
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=10)
        
        # Start game button
        tk.Button(
            nav_frame,
            text="🎮 START GAME",
            command=self.start_game,
            font=("Arial", 14, "bold"),
            bg=self.colors['success'],
            fg='white',
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=10)
    
    def start_game(self):
        """Start the main game"""
        self.clear_window()
        self.game_start_time = time.time()
        self.hints_used = 0
        self.queens = []
        self.timer_running = True
        
        # Main game frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Game board (70%)
        left_panel = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Board title
        board_title = tk.Frame(left_panel, bg=self.colors['bg_dark'], height=80)
        board_title.pack(fill=tk.X)
        board_title.pack_propagate(False)
        
        tk.Label(
            board_title,
            text="ROYAL CHESSBOARD",
            font=("Impact", 28, "bold"),
            bg=self.colors['bg_dark'],
            fg=self.colors['queen']
        ).pack(pady=20)
        
        # Board container
        board_container = tk.Frame(left_panel, bg=self.colors['bg_dark'])
        board_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.create_game_board(board_container)
        
        # Right panel - Game controls (30%)
        right_panel = tk.Frame(main_frame, bg=self.colors['bg_light'], width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        # Player info
        player_frame = tk.Frame(right_panel, bg=self.colors['board_dark'], 
                              relief=tk.RAISED, bd=3)
        player_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            player_frame,
            text=f"👑 {self.player_name}",
            font=("Arial", 20, "bold"),
            bg=self.colors['board_dark'],
            fg=self.colors['queen_highlight']
        ).pack(pady=10)
        
        # Level and score
        info_frame = tk.Frame(player_frame, bg=self.colors['board_dark'])
        info_frame.pack(pady=10)
        
        self.level_label = tk.Label(
            info_frame,
            text=f"Level: {self.player_level}",
            font=("Arial", 16, "bold"),
            bg=self.colors['board_dark'],
            fg=self.colors['success']
        )
        self.level_label.pack(side=tk.LEFT, padx=20)
        
        self.score_label = tk.Label(
            info_frame,
            text=f"Score: {self.player_score}",
            font=("Arial", 16, "bold"),
            bg=self.colors['board_dark'],
            fg=self.colors['gold']
        )
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        # Game stats
        stats_frame = tk.Frame(right_panel, bg=self.colors['board_dark'],
                             relief=tk.SUNKEN, bd=2)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.queen_count_label = tk.Label(
            stats_frame,
            text="Queens: 0/8",
            font=("Arial", 18, "bold"),
            bg=self.colors['board_dark'],
            fg=self.colors['text']
        )
        self.queen_count_label.pack(pady=10)
        
        self.conflict_label = tk.Label(
            stats_frame,
            text="Status: No Conflicts",
            font=("Arial", 14),
            bg=self.colors['board_dark'],
            fg=self.colors['safe']
        )
        self.conflict_label.pack(pady=5)
        
        self.time_label = tk.Label(
            stats_frame,
            text="Time: 0:00",
            font=("Arial", 12),
            bg=self.colors['board_dark'],
            fg=self.colors['text_light']
        )
        self.time_label.pack(pady=5)
        
        # Game controls
        controls_frame = tk.Frame(right_panel, bg=self.colors['bg_light'])
        controls_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Control buttons
        control_buttons = [
            ("✅ CHECK SOLUTION", self.check_solution, self.colors['success']),
            ("💡 HINT", self.show_hint, self.colors['warning']),
            ("🔄 NEW BOARD", self.new_board, self.colors['button']),
            ("🏳️ GIVE UP", self.give_up, self.colors['error']),
            ("📊 STATS", self.show_stats, self.colors['button_alt']),
            ("🏆 LEADERBOARD", self.show_leaderboard, self.colors['gold']),
            ("🏠 MAIN MENU", self.show_welcome_screen, self.colors['bg_dark'])
        ]
        
        for text, command, color in control_buttons:
            btn = tk.Button(
                controls_frame,
                text=text,
                command=command,
                font=("Arial", 12, "bold"),
                bg=color,
                fg='white',
                padx=20,
                pady=12,
                cursor="hand2",
                width=20
            )
            btn.pack(pady=8)
            self.add_button_glow(btn)
        
        # Hints remaining
        hint_frame = tk.Frame(right_panel, bg=self.colors['board_dark'])
        hint_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.hint_label = tk.Label(
            hint_frame,
            text=f"💡 Hints: {self.max_hints - self.hints_used}/{self.max_hints}",
            font=("Arial", 12),
            bg=self.colors['board_dark'],
            fg=self.colors['text_light']
        )
        self.hint_label.pack(pady=10)
        
        # Progress bar
        progress_frame = tk.Frame(right_panel, bg=self.colors['bg_light'])
        progress_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            progress_frame,
            text="Royal Progress",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg_light'],
            fg=self.colors['text']
        ).pack()
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=350,
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)
        
        # Update progress
        self.update_progress_bar()
        
        # Start timer
        self.start_timer()
        
        # Update board display
        self.update_board_display()
    
    def create_game_board(self, parent):
        """Create interactive game board"""
        self.board_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        self.board_frame.pack(expand=True)
        
        self.board_buttons = []
        cell_size = 70
        
        # Create 8x8 grid with labels
        for row in range(8):
            button_row = []
            
            # Row label
            tk.Label(
                self.board_frame,
                text=str(8 - row),
                font=("Arial", 14, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['queen'],
                width=3
            ).grid(row=row, column=0)
            
            for col in range(8):
                # Determine square color
                if (row + col) % 2 == 0:
                    base_color = self.colors['board_light']
                else:
                    base_color = self.colors['board_dark']
                
                # Create square
                square_frame = tk.Frame(
                    self.board_frame,
                    width=cell_size,
                    height=cell_size,
                    bg=base_color,
                    bd=1,
                    relief=tk.RAISED
                )
                square_frame.grid(row=row, column=col + 1, padx=1, pady=1)
                square_frame.grid_propagate(False)
                
                # Queen button
                btn = tk.Button(
                    square_frame,
                    text="",
                    font=("Arial", 32, "bold"),
                    bg=base_color,
                    fg=self.colors['queen'],
                    activebackground=base_color,
                    bd=0,
                    command=lambda r=row, c=col: self.toggle_queen(r, c)
                )
                btn.place(relx=0.5, rely=0.5, anchor='center', 
                         width=cell_size-10, height=cell_size-10)
                
                # Add hover effect
                self.add_cell_hover_effect(btn, base_color)
                
                button_row.append(btn)
            
            self.board_buttons.append(button_row)
        
        # Column labels
        for col in range(8):
            tk.Label(
                self.board_frame,
                text=chr(65 + col),
                font=("Arial", 14, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['queen'],
                height=2
            ).grid(row=8, column=col + 1)
    
    def add_cell_hover_effect(self, button, base_color):
        """Add hover effect to board cells"""
        def on_enter(e):
            if button['text'] == "":
                # Lighten color on hover
                button.config(
                    bg=self.lighten_color(base_color, 20),
                    fg=self.colors['queen_highlight']
                )
                # Show preview queen
                button.config(text="♛", font=("Arial", 28, "bold"))
        
        def on_leave(e):
            # Check if queen actually exists at this position
            row = button.master.grid_info()['row']
            col = button.master.grid_info()['column'] - 1  # Adjust for label column
            
            has_queen = any(q[0] == row and q[1] == col for q in self.queens)
            if not has_queen:
                button.config(text="", bg=base_color, fg=self.colors['queen'])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def lighten_color(self, color, amount):
        """Lighten a color by given amount"""
        if color.startswith('#'):
            r = min(255, int(color[1:3], 16) + amount)
            g = min(255, int(color[3:5], 16) + amount)
            b = min(255, int(color[5:7], 16) + amount)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def toggle_queen(self, row, col):
        """Place or remove queen"""
        # Check if queen exists
        queen_pos = None
        for i, (r, c) in enumerate(self.queens):
            if r == row and c == col:
                queen_pos = i
                break
        
        if queen_pos is not None:
            # Remove queen
            self.queens.pop(queen_pos)
            self.board_buttons[row][col].config(text="")
        else:
            # Check limit
            if len(self.queens) >= 8:
                self.show_message("Royal Decree", "Only 8 queens can rule the board!", "warning")
                return
            
            # Place queen
            self.queens.append((row, col))
            self.board_buttons[row][col].config(text="♛")
        
        self.update_board_display()
    
    def update_board_display(self):
        """Update game display"""
        # Update queen count
        count = len(self.queens)
        self.queen_count_label.config(text=f"Queens: {count}/8")
        
        # Check conflicts
        conflicts = self.check_conflicts()
        
        if conflicts:
            self.conflict_label.config(
                text=f"⚠ {len(conflicts)} Conflicts!",
                fg=self.colors['conflict']
            )
        else:
            status = "Perfect! ✓" if count == 8 else "No Conflicts ✓"
            self.conflict_label.config(
                text=f"Status: {status}",
                fg=self.colors['safe']
            )
    
    def check_conflicts(self):
        """Check for queen conflicts"""
        conflicts = []
        for i in range(len(self.queens)):
            for j in range(i + 1, len(self.queens)):
                r1, c1 = self.queens[i]
                r2, c2 = self.queens[j]
                
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
                    conflicts.append((r1, c1, r2, c2))
        
        return conflicts
    
    def start_timer(self):
        """Start game timer"""
        if self.timer_running:
            elapsed = time.time() - self.game_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.time_label.config(text=f"Time: {minutes}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.start_timer)
    
    def update_progress_bar(self):
        """Update progress bar"""
        if hasattr(self, 'progress_bar'):
            # Calculate progress based on solutions found
            try:
                self.cursor.execute(
                    "SELECT solutions_found FROM players WHERE name = ?",
                    (self.player_name,)
                )
                result = self.cursor.fetchone()
                solutions_found = result[0] if result else 0
                
                progress = (solutions_found / 92) * 100
                self.progress_bar['value'] = progress
            except:
                pass
    
    def check_solution(self):
        """Check current solution"""
        if len(self.queens) != 8:
            self.show_message("Incomplete Board", "Place exactly 8 queens!", "warning")
            return
        
        conflicts = self.check_conflicts()
        if conflicts:
            self.show_message("Conflict Detected", 
                            f"{len(conflicts)} queens are attacking each other!", "error")
            return
        
        # Convert to solution string
        solution = self.get_solution_string()
        
        # Check if solution is known
        try:
            self.cursor.execute(
                "SELECT discovered_by FROM solutions WHERE solution = ?",
                (solution,)
            )
            result = self.cursor.fetchone()
        except:
            result = None
        
        elapsed = time.time() - self.game_start_time
        time_bonus = max(0, 500 - int(elapsed))  # Bonus for speed
        
        if result and result[0]:
            # Known solution
            score_gain = 500 + time_bonus
            message = f"✅ Solution Found!\n\nThis solution was first discovered by:\n{result[0]}\n\nTime Bonus: +{time_bonus}"
        else:
            # New solution!
            score_gain = 1000 + time_bonus
            message = f"🎉 ROYAL DISCOVERY! 🎉\n\nYou found a NEW solution!\n\nTime Bonus: +{time_bonus}"
            
            # Save to database
            try:
                self.cursor.execute(
                    "UPDATE solutions SET discovered_by = ?, discovery_time = ? WHERE solution = ?",
                    (self.player_name, elapsed, solution)
                )
                self.conn.commit()
            except:
                pass
        
        # Update player stats
        self.player_score += score_gain
        try:
            self.cursor.execute('''
                UPDATE players 
                SET score = score + ?, 
                    solutions_found = solutions_found + 1,
                    total_time = total_time + ?,
                    best_time = CASE WHEN ? < best_time OR best_time = 0 THEN ? ELSE best_time END
                WHERE name = ?
            ''', (score_gain, elapsed, elapsed, elapsed, self.player_name))
            
            # Check level up
            self.cursor.execute(
                "SELECT solutions_found FROM players WHERE name = ?",
                (self.player_name,)
            )
            solutions_found = self.cursor.fetchone()[0]
            new_level = min(10, 1 + solutions_found // 10)
            
            if new_level > self.player_level:
                self.player_level = new_level
                self.cursor.execute(
                    "UPDATE players SET level = ? WHERE name = ?",
                    (new_level, self.player_name)
                )
                message += f"\n\n🏆 LEVEL UP! You reached Level {new_level}!"
            
            self.conn.commit()
        except:
            pass
        
        # Update display
        self.level_label.config(text=f"Level: {self.player_level}")
        self.score_label.config(text=f"Score: {self.player_score}")
        self.update_progress_bar()
        
        # Show celebration
        self.celebrate_solution(message, score_gain)
        
        # Start new game
        self.root.after(3000, self.new_board)
    
    def get_solution_string(self):
        """Convert board to solution string"""
        sorted_queens = sorted(self.queens, key=lambda x: x[0])
        return ''.join(str(col + 1) for row, col in sorted_queens)
    
    def celebrate_solution(self, message, score_gain):
        """Celebrate finding a solution"""
        # Create celebration window
        celeb_window = tk.Toplevel(self.root)
        celeb_window.title("🎉 Royal Achievement!")
        celeb_window.geometry("600x400")
        celeb_window.configure(bg=self.colors['bg'])
        celeb_window.transient(self.root)
        
        # Center window
        celeb_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
        celeb_window.geometry(f"600x400+{x}+{y}")
        
        # Celebration content
        tk.Label(
            celeb_window,
            text="✨ ROYAL ACHIEVEMENT ✨",
            font=("Impact", 28, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['gold']
        ).pack(pady=20)
        
        tk.Label(
            celeb_window,
            text=message,
            font=("Arial", 14),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            justify=tk.CENTER
        ).pack(pady=20, padx=30)
        
        tk.Label(
            celeb_window,
            text=f"Score: +{score_gain}",
            font=("Arial", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['success']
        ).pack(pady=20)
        
        tk.Label(
            celeb_window,
            text=f"Total Score: {self.player_score}",
            font=("Arial", 18),
            bg=self.colors['bg'],
            fg=self.colors['text_light']
        ).pack(pady=10)
        
        # Continue button
        tk.Button(
            celeb_window,
            text="Continue Challenge →",
            command=celeb_window.destroy,
            font=("Arial", 14, "bold"),
            bg=self.colors['success'],
            fg='white',
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(pady=30)
    
    def show_hint(self):
        """Show hint to player"""
        if self.hints_used >= self.max_hints:
            self.show_message("No Hints Left", "You've used all your hints!", "warning")
            return
        
        self.hints_used += 1
        self.player_score = max(0, self.player_score - 100)  # Penalty for hint
        self.hint_label.config(text=f"💡 Hints: {self.max_hints - self.hints_used}/{self.max_hints}")
        self.score_label.config(text=f"Score: {self.player_score}")
        
        # Find safe position for next queen
        for row in range(8):
            if any(q[0] == row for q in self.queens):
                continue
            
            for col in range(8):
                safe = True
                for qr, qc in self.queens:
                    if col == qc or abs(row - qr) == abs(col - qc):
                        safe = False
                        break
                
                if safe:
                    # Highlight the suggested position
                    self.highlight_position(row, col)
                    self.show_message(
                        "Royal Hint",
                        f"Try placing a queen at:\nRow {8-row}, Column {chr(65+col)}\n\n(-100 points)",
                        "info"
                    )
                    return
        
        self.show_message("Hint", "No safe positions found. Try rearranging your queens.", "info")
    
    def highlight_position(self, row, col):
        """Highlight a board position"""
        button = self.board_buttons[row][col]
        original_bg = button['bg']
        
        # Pulsing highlight
        def pulse(count=0):
            if count < 6:  # 3 pulses
                color = self.colors['success'] if count % 2 == 0 else original_bg
                button.config(bg=color)
                if count < 5:  # Schedule next pulse
                    self.root.after(300, lambda: pulse(count + 1))
                else:
                    button.config(bg=original_bg)
        
        pulse()
    
    def give_up(self):
        """Player gives up - show a solution"""
        response = messagebox.askyesno(
            "Surrender?",
            "Are you sure you want to give up?\n\nYou will lose 200 points and see a solution."
        )
        
        if not response:
            return
        
        # Penalty
        self.player_score = max(0, self.player_score - 200)
        self.score_label.config(text=f"Score: {self.player_score}")
        
        # Get a random solution
        solution = self.get_random_solution()
        self.show_solution(solution)
        
        # Update database
        try:
            self.cursor.execute(
                "UPDATE players SET score = ? WHERE name = ?",
                (self.player_score, self.player_name)
            )
            self.conn.commit()
        except:
            pass
        
        # Start new game after delay
        self.root.after(5000, self.new_board)
    
    def get_random_solution(self):
        """Get a random solution from database or generate one"""
        try:
            self.cursor.execute("SELECT solution FROM solutions ORDER BY RANDOM() LIMIT 1")
            result = self.cursor.fetchone()
            if result:
                return result[0]
        except:
            pass
        
        # Generate a solution
        return self.generate_solution()
    
    def generate_solution(self):
        """Generate a valid solution"""
        def solve():
            board = [-1] * 8
            
            def is_safe(row, col):
                for i in range(row):
                    if board[i] == col or abs(board[i] - col) == abs(i - row):
                        return False
                return True
            
            def backtrack(row):
                if row == 8:
                    return True
                
                cols = list(range(8))
                random.shuffle(cols)
                
                for col in cols:
                    if is_safe(row, col):
                        board[row] = col
                        if backtrack(row + 1):
                            return True
                        board[row] = -1
                return False
            
            backtrack(0)
            return ''.join(str(col + 1) for col in board)
        
        return solve()
    
    def show_solution(self, solution):
        """Display a solution on the board"""
        # Clear current board
        self.clear_board(animate=False)
        
        # Place solution queens
        for row, col_char in enumerate(solution):
            col = int(col_char) - 1
            self.queens.append((row, col))
            self.board_buttons[row][col].config(text="♛")
        
        # Show solution window
        sol_window = tk.Toplevel(self.root)
        sol_window.title("Solution Revealed")
        sol_window.geometry("500x300")
        sol_window.configure(bg=self.colors['bg'])
        sol_window.transient(self.root)
        
        # Center window
        sol_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 300) // 2
        sol_window.geometry(f"500x300+{x}+{y}")
        
        tk.Label(
            sol_window,
            text="🏳️ Solution Revealed",
            font=("Impact", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['warning']
        ).pack(pady=20)
        
        tk.Label(
            sol_window,
            text="Study this solution and try again!",
            font=("Arial", 14),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(pady=10)
        
        tk.Label(
            sol_window,
            text=f"Solution: {solution}",
            font=("Courier", 18, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['queen']
        ).pack(pady=20)
    
    def new_board(self):
        """Start a new game board"""
        self.clear_board()
        self.game_start_time = time.time()
        self.hints_used = 0
        self.hint_label.config(text=f"💡 Hints: {self.max_hints}/{self.max_hints}")
        self.update_board_display()
    
    def clear_board(self, animate=True):
        """Clear the game board"""
        if animate and self.queens:
            # Remove queens one by one
            for i, (row, col) in enumerate(self.queens):
                self.root.after(i * 100, lambda r=row, c=col: self.animate_queen_removal(r, c))
            self.root.after(len(self.queens) * 100, lambda: setattr(self, 'queens', []))
        else:
            # Clear immediately
            for row, col in self.queens:
                self.board_buttons[row][col].config(text="")
            self.queens = []
    
    def animate_queen_removal(self, row, col):
        """Animate queen removal during clear"""
        if hasattr(self, 'board_buttons') and len(self.board_buttons) > row and len(self.board_buttons[row]) > col:
            self.board_buttons[row][col].config(text="")
    
    def show_stats(self):
        """Show player statistics"""
        # Get detailed stats
        try:
            self.cursor.execute('''
                SELECT score, level, games_played, solutions_found, 
                       best_time, total_time, join_date
                FROM players WHERE name = ?
            ''', (self.player_name,))
            
            result = self.cursor.fetchone()
        except:
            result = None
        
        if not result:
            self.show_message("No Stats", "Play some games first!", "info")
            return
        
        score, level, games, solutions, best_time, total_time, join_date = result
        
        # Calculate averages
        avg_time = total_time / games if games > 0 else 0
        success_rate = (solutions / games * 100) if games > 0 else 0
        
        # Create stats window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Royal Statistics")
        stats_window.geometry("600x500")
        stats_window.configure(bg=self.colors['bg'])
        stats_window.transient(self.root)
        
        # Center window
        stats_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 500) // 2
        stats_window.geometry(f"600x500+{x}+{y}")
        
        tk.Label(
            stats_window,
            text=f"👑 {self.player_name}'s Royal Record",
            font=("Impact", 24, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['queen']
        ).pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(stats_window, bg=self.colors['board_dark'])
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        stats_text = f"""
        🏆 Level: {level}
        ⭐ Score: {score:,}
        
        🎮 Games Played: {games}
        ✅ Solutions Found: {solutions}/92
        📊 Success Rate: {success_rate:.1f}%
        
        ⏱️ Best Time: {best_time:.1f}s
        ⏱️ Average Time: {avg_time:.1f}s
        ⏱️ Total Play Time: {total_time/60:.1f} min
        
        📅 Joined: {join_date.split()[0] if join_date else 'Today'}
        """
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=("Arial", 14),
            bg=self.colors['board_dark'],
            fg=self.colors['text'],
            justify=tk.LEFT
        ).pack(pady=30, padx=30)
        
        # Progress to next level
        next_level_solutions = level * 10
        progress = min(100, (solutions / next_level_solutions) * 100) if next_level_solutions > 0 else 0
        
        tk.Label(
            stats_frame,
            text=f"Progress to Level {level + 1}: {solutions}/{next_level_solutions} solutions",
            font=("Arial", 12),
            bg=self.colors['board_dark'],
            fg=self.colors['text_light']
        ).pack(pady=10)
        
        progress_bar = ttk.Progressbar(
            stats_frame,
            length=400,
            mode='determinate'
        )
        progress_bar.pack(pady=10)
        progress_bar['value'] = progress
        
        tk.Button(
            stats_window,
            text="Close",
            command=stats_window.destroy,
            font=("Arial", 12),
            bg=self.colors['button'],
            fg='white',
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def show_leaderboard(self):
        """Show global leaderboard"""
        try:
            self.cursor.execute('''
                SELECT name, score, level, solutions_found, best_time
                FROM players
                ORDER BY score DESC
                LIMIT 10
            ''')
            
            leaders = self.cursor.fetchall()
        except:
            leaders = []
        
        # Create leaderboard window
        leader_window = tk.Toplevel(self.root)
        leader_window.title("Royal Leaderboard")
        leader_window.geometry("800x600")
        leader_window.configure(bg=self.colors['bg'])
        
        tk.Label(
            leader_window,
            text="🏆 ROYAL LEADERBOARD 🏆",
            font=("Impact", 32, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['gold']
        ).pack(pady=20)
        
        # Create leaderboard table
        table_frame = tk.Frame(leader_window, bg=self.colors['board_dark'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        # Table headers
        headers = ["Rank", "Player", "Score", "Level", "Solutions", "Best Time"]
        for col, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Arial", 12, "bold"),
                bg=self.colors['board_dark'],
                fg=self.colors['queen'],
                bd=1,
                relief=tk.SUNKEN
            ).grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        # Table data
        for row, (name, score, level, solutions, best_time) in enumerate(leaders, 1):
            # Rank with medals
            if row == 1:
                rank = "🥇"
                color = self.colors['gold']
            elif row == 2:
                rank = "🥈"
                color = self.colors['silver']
            elif row == 3:
                rank = "🥉"
                color = self.colors['bronze']
            else:
                rank = str(row)
                color = self.colors['text']
            
            # Highlight current player
            bg_color = self.colors['board_light'] if name == self.player_name else self.colors['board_dark']
            
            tk.Label(
                table_frame,
                text=rank,
                font=("Arial", 14, "bold"),
                bg=bg_color,
                fg=color
            ).grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=name,
                font=("Arial", 12, "bold" if name == self.player_name else "normal"),
                bg=bg_color,
                fg=self.colors['text']
            ).grid(row=row, column=1, sticky='nsew', padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=f"{score:,}",
                font=("Arial", 11),
                bg=bg_color,
                fg=self.colors['text']
            ).grid(row=row, column=2, sticky='nsew', padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=str(level),
                font=("Arial", 11),
                bg=bg_color,
                fg=self.colors['text']
            ).grid(row=row, column=3, sticky='nsew', padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=str(solutions),
                font=("Arial", 11),
                bg=bg_color,
                fg=self.colors['text']
            ).grid(row=row, column=4, sticky='nsew', padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=f"{best_time:.1f}s" if best_time else "N/A",
                font=("Arial", 11),
                bg=bg_color,
                fg=self.colors['text']
            ).grid(row=row, column=5, sticky='nsew', padx=1, pady=1)
        
        # Configure grid weights
        for i in range(6):
            table_frame.grid_columnconfigure(i, weight=1)
        
        tk.Button(
            leader_window,
            text="Close",
            command=leader_window.destroy,
            font=("Arial", 12),
            bg=self.colors['button'],
            fg='white',
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def show_message(self, title, message, type="info"):
        """Show a styled message box"""
        color_map = {
            "info": self.colors['button'],
            "warning": self.colors['warning'],
            "error": self.colors['error'],
            "success": self.colors['success']
        }
        
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.geometry("400x200")
        msg_window.configure(bg=self.colors['bg'])
        msg_window.transient(self.root)
        
        # Center window
        msg_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 200) // 2
        msg_window.geometry(f"400x200+{x}+{y}")
        
        tk.Label(
            msg_window,
            text=title,
            font=("Impact", 20, "bold"),
            bg=self.colors['bg'],
            fg=color_map[type]
        ).pack(pady=20)
        
        tk.Label(
            msg_window,
            text=message,
            font=("Arial", 12),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            justify=tk.CENTER
        ).pack(pady=10, padx=20)
        
        tk.Button(
            msg_window,
            text="OK",
            command=msg_window.destroy,
            font=("Arial", 12),
            bg=color_map[type],
            fg='white',
            padx=30,
            pady=10
        ).pack(pady=20)


def main():
    """Main function"""
    root = tk.Tk()
    
    # Center window
    root.update_idletasks()
    width = 1400
    height = 900
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Set title
    root.title("♛ Eight Queens Challenge ♛")
    
    # Create game
    game = EightQueensGame(root)
    
    # Run main loop
    root.mainloop()


if __name__ == "__main__":
    main()