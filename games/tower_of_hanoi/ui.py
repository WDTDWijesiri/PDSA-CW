import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
import re
from game import GameManager
from algorithms import optimal_moves_count, timed_recursive_solution
import database


def center_dialog_on_parent(parent_window, dialog_window, width=400, height=200):
    """Center a dialog window relative to its parent window."""
    dialog_window.geometry(f"{width}x{height}")
    dialog_window.update_idletasks()
    
    parent_x = parent_window.winfo_x()
    parent_y = parent_window.winfo_y()
    parent_width = parent_window.winfo_width()
    parent_height = parent_window.winfo_height()
    
    x = parent_x + (parent_width - width) // 2
    y = parent_y + (parent_height - height) // 2
    
    dialog_window.geometry(f"{width}x{height}+{x}+{y}")



# ----------------------------
#  CUTE GAME THEME COLORS
# ----------------------------
BG_COLOR = "#0B1B2B"       # dark navy blue
CARD_COLOR = "#1B3A57"     # softer dark card
ACCENT = "#00E5FF"         # soft baby-blue
TEXT = "#f1f5f9"           # almost white
CANCEL_CARD = "#F44336"
PIXEL_FONT = ("Helvetica", 16, "bold")
TITLE_FONT = ("Helvetica", 28, "bold")
SMALL_FONT = ("Helvetica", 12)

# ------------------------------------------------
# MAIN MENU CLASS (Start Game, Stats, etc.)
# ------------------------------------------------
class MainMenu:
    def __init__(self):
        database.init_db()
        self.root = tk.Tk()
        self.root.title("Tower of Hanoi - Recursive Logic Solver")
        self.root.geometry("1000x650")
        self.root.configure(bg=BG_COLOR)
        
        # Center window on screen
        self._center_window(self.root)

        self.build_ui()
    
    def _start_with_sound(self, callback):
        """Execute callback for main menu."""
        callback()
    
    def _center_window(self, window):
        """Center a window on the screen."""
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Parse geometry to get width and height
        geom = window.geometry().split('+')[0].split('x')
        window_width = int(geom[0])
        window_height = int(geom[1])
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def run(self):
        self.root.mainloop()

    # -------------------------------
    #  BUILD MAIN MENU UI
    # -------------------------------
    def build_ui(self):
        title = tk.Label(
            self.root,
            text="🏰  TOWER OF HANOI",
            bg=BG_COLOR,
            fg=ACCENT,
            font=TITLE_FONT
        )
        title.pack(pady=(40, 10))

        subtitle = tk.Label(
            self.root,
            text="═══════════════════════════════════════════════════════════\nAlgorithmic Puzzle Simulator",
            bg=BG_COLOR,
            fg=TEXT,
            font=PIXEL_FONT
        )
        subtitle.pack(pady=(0, 30))

        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack()

        buttons = [
            ("▶️  START GAME", lambda: self._start_with_sound(self.start_game_flow), "#2196F3"),
            ("📊  STATISTICS", lambda: self._start_with_sound(self.show_statistics), "#FF9800"),
            ("🏆  LEADERBOARD", lambda: self._start_with_sound(self.show_leaderboard), "#9C27B0"),
            ("🧠  ALGORITHM INFO", lambda: self._start_with_sound(self.show_algorithm_info), "#00BCD4"),
            ("🚪  QUIT GAME", self.root.destroy, "#F44336"),
        ]

        for text, cmd, btn_color in buttons:
            btn = tk.Button(
                frame,
                text=text,
                width=25,
                height=2,
                command=cmd,
                bg=btn_color,
                fg="white",
                font=PIXEL_FONT,
                activebackground=ACCENT
            )
            btn.pack(pady=8)

    # -------------------------------
    #  START GAME WORKFLOW
    # -------------------------------
    def start_game_flow(self):
        # Get player name with validation
        name = self._get_player_name()
        if not name:
            return

        # Get number of pegs
        pegs = self._get_pegs_choice()

        # Randomly select disks and show info
        disks = random.randint(5, 10)
        optimal_moves = optimal_moves_count(disks, pegs)
        
        # Show disks and optimal moves (styled dialog)
        messagebox.showinfo("Disks Selected",
                       f"🎲 Disks selected: {disks}\n\n"
                       f"Good luck!",
                       parent=self.root)

        # Show game rules
        rules = (
            "🏰 TOWER OF HANOI RULES\n"
            "═════════════════════════════════════════════════════════════\n"
            "• Move 1 disk at a time\n"
            "• Never place larger disk on smaller\n"
            f"• Solve with {pegs} pegs\n"
            f"• Optimal moves: {optimal_moves}\n"
            "• Try to beat the optimal!"
        )
        messagebox.showinfo("Rules", rules, parent=self.root)
        
        # Ask for prediction
        self._get_prediction(optimal_moves, disks)

        # Launch game
        for w in self.root.winfo_children():
            w.destroy()

        GameWindow(self.root, name, pegs, disks, menu=self)
    
    def _get_prediction(self, optimal_moves, disks):
        """Ask player to predict move count and sequence."""
        pred_win = tk.Toplevel(self.root)
        pred_win.title("Make Your Prediction")
        pred_win.geometry("700x550")
        pred_win.configure(bg=BG_COLOR)
        
        # Center window
        pred_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 700) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 550) // 2
        pred_win.geometry(f"700x550+{x}+{y}")
        
        title = tk.Label(
            pred_win, 
            text=f"🎯 Prediction for {disks} Disks",
            bg=CARD_COLOR, 
            fg=ACCENT, 
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)
        
        separator = tk.Label(pred_win, text="═" * 50, bg=BG_COLOR, fg=ACCENT)
        separator.pack(pady=(0, 20))
        
        # Move count prediction
        frame1 = tk.Frame(pred_win, bg=BG_COLOR)
        frame1.pack(pady=15, padx=30, fill="x")
        
        tk.Label(
            frame1, 
            text="📊 Predict move count:", 
            bg=BG_COLOR, 
            fg=TEXT, 
            font=("Helvetica", 15, "bold")
        ).pack(anchor="w")
        
        move_count_var = tk.StringVar()
        move_entry = tk.Entry(
            frame1, 
            textvariable=move_count_var,
            font=("Helvetica", 14),
            width=25
        )
        move_entry.pack(anchor="w", pady=8)
        
        # Move sequence prediction
        frame2 = tk.Frame(pred_win, bg=BG_COLOR)
        frame2.pack(pady=15, padx=30, fill="both", expand=True)
        
        tk.Label(
            frame2, 
            text="🔄 Predict move sequence (e.g., A→B, B→C, ...):",
            bg=BG_COLOR, 
            fg=TEXT, 
            font=("Helvetica", 15, "bold")
        ).pack(anchor="w")
        
        sequence_text = tk.Text(
            frame2,
            height=7,
            width=50,
            font=("Helvetica", 13),
            bg=CARD_COLOR,
            fg=TEXT
        )
        sequence_text.pack(anchor="w", pady=8, fill="both", expand=True)
        
        # Close button
        def close_and_save():
            pred_win.destroy()
        
        btn = tk.Button(
            pred_win,
            text="🎮 Start Game",
            command=close_and_save,
            bg=ACCENT,
            fg="black",
            font=("Helvetica", 15, "bold"),
            width=25,
            height=2,
            relief="raised",
            bd=3
        )
        btn.pack(pady=20)
        
        pred_win.transient(self.root)
        pred_win.grab_set()
        self.root.wait_window(pred_win)
    
    def _get_player_name(self):
        """Get and validate player name from user."""
        while True:
            name = simpledialog.askstring(
                "🎮 Player Name", 
                "Enter your name:",
                parent=self.root
            )
            if name is None:  # User cancelled
                return None
            name = name.strip()
            
            # Check length
            if len(name) < 2:
                messagebox.showwarning("Invalid Name", "Name must be at least 2 characters!", parent=self.root)
                continue
            
            # Check if too long
            if len(name) > 20:
                messagebox.showwarning("Invalid Name", "Name must be 20 characters or less!", parent=self.root)
                continue
            
            # Check for special characters (only alphanumeric and spaces)
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9 ]*$', name):
                messagebox.showwarning("Invalid Name", "Name cannot start with a number.", parent=self.root)
                continue
            
            return name
    
    def _get_pegs_choice(self):
        """Get number of pegs from user."""
        while True:
            val = simpledialog.askstring(
                "Number of Pegs",
                "Select number of pegs:\n( 3 or 4 )",
                parent=self.root
            )
            if val is None:  # User cancelled
                return 3
            val = val.strip()
            if not val:
                messagebox.showwarning("Invalid Input", "Field cannot be empty.", parent=self.root)
                continue
            if not val.isdigit():
                messagebox.showwarning("Invalid Input", "Not a number.", parent=self.root)
                continue
            pegs = int(val)
            if pegs in (3, 4):
                return pegs
            messagebox.showwarning("Invalid Choice", "Only 3 or 4 pegs allowed.", parent=self.root)

    # -------------------------------
    #  STATISTICS WINDOW
    # -------------------------------
    def show_statistics(self):
        """Display all game statistics in a new window."""
        rows = database.fetch_all()

        win = tk.Toplevel(self.root)
        win.title("Game Statistics")
        win.configure(bg=BG_COLOR)
        center_dialog_on_parent(self.root, win, 1100, 500)

        title = tk.Label(win, text="📊 Game Records", bg=BG_COLOR, fg=ACCENT, font=("Helvetica", 16, "bold"))
        title.pack(pady=12)
        separator = tk.Label(win, text="═" * 115, bg=BG_COLOR, fg=ACCENT, font=("Helvetica", 10))
        separator.pack(pady=(0, 12))

        cols = ["Player", "Pegs", "Disks", "Moves", "Optimal", "Time (s)", "Algo Time (s)", "Solved", "Efficiency (%)", "Date"]
        
        # Frame for treeview with scrollbars
        tree_frame = tk.Frame(win, bg=BG_COLOR)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")

        for r in rows:
            # rows: player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, solved, efficiency, date
            player, pegs, disks, moves, optimal, t_algo, algo_time, solved, efficiency, date = r
            solved_text = "Yes" if solved else "No"
            eff_pct = f"{(efficiency*100):.1f}" if efficiency is not None else "0.0"
            tree.insert("", "end", values=(player, pegs, disks, moves, optimal, t_algo, algo_time, solved_text, eff_pct, date))

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        tk.Button(win, text="Close", command=win.destroy, bg=CANCEL_CARD, fg=TEXT).pack(pady=10)

    # -------------------------------
    #  LEADERBOARD
    # -------------------------------
    def show_leaderboard(self):
        """Display the leaderboard with top players."""
        rows = database.fetch_leaderboard()

        win = tk.Toplevel(self.root)
        win.title("Leaderboard")
        win.configure(bg=BG_COLOR)
        center_dialog_on_parent(self.root, win, 900, 450)

        tk.Label(win, text="🏆 Leaderboard (Completed Games)", bg=BG_COLOR, fg=ACCENT, font=("Helvetica", 16, "bold")).pack(pady=12)
        separator = tk.Label(win, text="═" * 100, bg=BG_COLOR, fg=ACCENT, font=("Helvetica", 10))
        separator.pack(pady=(0, 12))

        cols = ["Rank", "Player", "Pegs", "Disks", "Moves", "Optimal", "Efficiency (%)", "Time (s)", "Solved", "Date"]
        
        # Frame for treeview with scrollbars
        tree_frame = tk.Frame(win, bg=BG_COLOR)
        tree_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)

        for c in cols:
            tree.heading(c, text=c)
            # make rank narrow, name wider
            if c == "Player":
                tree.column(c, width=180, anchor="w")
            elif c == "Rank":
                tree.column(c, width=50, anchor="center")
            else:
                tree.column(c, width=100, anchor="center")

        for i, r in enumerate(rows, start=1):
            # rows: player, pegs, disks, moves, optimal_moves, time_taken, efficiency, date, diff, solved
            player, pegs, disks, moves, optimal, t, efficiency, date, diff, solved = r
            eff_pct = f"{(efficiency*100):.1f}" if efficiency is not None else "0.0"
            solved_text = "Yes" if solved else "No"
            tree.insert("", "end", values=(i, player, pegs, disks, moves, optimal, eff_pct, f"{t:.2f}", solved_text, date))

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tk.Button(win, text="Close", command=win.destroy, bg=CANCEL_CARD, fg=TEXT).pack(pady=8)

    # -------------------------------
    #  ALGORITHM INFO
    # -------------------------------
    def show_algorithm_info(self):
        """Display information about the Tower of Hanoi algorithm."""
        win = tk.Toplevel(self.root)
        win.title("Algorithm Information")
        win.configure(bg=CARD_COLOR)
        center_dialog_on_parent(self.root, win, 650, 550)

        txt = (
            "🧠 TOWER OF HANOI ALGORITHM\n"
            "═════════════════════════════════════════════════\n\n"
            "⚙️  Approach: Recursive Method\n"
            "⏱️  Time Complexity: O(2ⁿ)\n"
            "📈 Optimal Moves: 2ⁿ - 1\n\n"
            "🔄 How it works:\n"
            "   1. Move n-1 disks from source to auxiliary\n"
            "   2. Move the largest disk to destination\n"
            "   3. Move n-1 disks from auxiliary to destination\n\n"
            "🏔️  Variations:\n"
            "   • 3 pegs: Classic Hanoi (exponential)\n"
            "   • 4 pegs: Frame-Stewart (sub-exponential)\n"
        )

        label = tk.Label(
            win, 
            text=txt, 
            bg=CARD_COLOR, 
            fg=TEXT, 
            font=("Courier", 13), 
            justify="left"
        )
        label.pack(padx=25, pady=20)

        frame = tk.Frame(win, bg=BG_COLOR)
        frame.pack(pady=15)

        tk.Button(
            frame, 
            text="Show Example (3 disks)", 
            bg=ACCENT, 
            fg="black",
            font=("Helvetica", 11, "bold"),
            command=lambda: self.show_example(3)
        ).pack(side="left", padx=8)

        tk.Button(
            frame, 
            text="Show Example (5 disks)", 
            bg=ACCENT, 
            fg="black",
            font=("Helvetica", 11, "bold"),
            command=lambda: self.show_example(5)
        ).pack(side="left", padx=8)

        tk.Button(
            frame, 
            text="Close", 
            command=win.destroy, 
            bg=CANCEL_CARD, 
            fg=TEXT,
            font=("Helvetica", 11, "bold")
        ).pack(side="left", padx=8)

    def show_example(self, n):
        """Show example moves for n disks."""
        moves, t = timed_recursive_solution(n)
        s = "\n".join([f"{i+1}. {a} → {b}" for i, (a, b) in enumerate(moves)])
        
        example_win = tk.Toplevel(self.root)
        example_win.title(f"Solution Example ({n} disks)")
        example_win.configure(bg=BG_COLOR)
        center_dialog_on_parent(self.root, example_win, 400, 400)

        header = tk.Label(
            example_win,
            text=f"Solution for {n} disks\n({len(moves)} moves in {t*1000:.3f}ms)",
            bg=BG_COLOR,
            fg=ACCENT,
            font=PIXEL_FONT
        )
        header.pack(pady=10)

        # Scrollable text
        text_frame = tk.Frame(example_win, bg=BG_COLOR)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(text_frame, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=BG_COLOR)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(scrollable, text=s, bg=BG_COLOR, fg=TEXT, font=("Helvetica", 12), justify="left").pack(anchor="w", padx=10, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y", expand=False)

        tk.Button(example_win, text="Close", command=example_win.destroy, bg=CANCEL_CARD, fg=TEXT).pack(pady=10)


# ------------------------------------------------
# GAME WINDOW
# ------------------------------------------------
class GameWindow:
    """Main game window for playing Tower of Hanoi."""
    
    def __init__(self, parent, player, pegs, disks, menu=None):
        self.player = player
        self.pegs = pegs
        self.disks = disks
        self.menu = menu
        self.win = parent
        self.win.title(f"Tower of Hanoi - {player}")
        self.win.geometry("900x800")
        self.win.configure(bg=BG_COLOR)
        self._center_game_window()

        self.manager = GameManager(pegs=pegs, disks=disks)
        self.manager.start()
        
        # Drag-drop tracking
        self.dragging = False
        self.dragged_disk = None
        self.dragged_disk_size = None
        self.from_peg = None
        self.peg_positions = {}
        self.drag_ghost_id = None
        self.target_peg = None
        self.highlight_id = None
        self.paused = False
        
        # Build UI in correct order: title → info → pegs → controls
        self.build_title()
        self.build_info_panel()
        
        # Canvas for pegs
        self.canvas = tk.Canvas(self.win, bg="#0b1220", width=780, height=340, highlightthickness=0)
        self.canvas.pack(pady=15)
        
        # Bind canvas events for drag-drop
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.build_controls()
        self.draw_pegs()

        self.update_timer()
    
    def _center_game_window(self):
        """Center the game window on the screen."""
        self.win.update_idletasks()
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        
        window_width = 900
        window_height = 800
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # -------------------------------
    #  GAME TITLE
    # -------------------------------
    def build_title(self):
        """Build game title display."""
        title_frame = tk.Frame(self.win, bg=BG_COLOR)
        title_frame.pack(pady=(20, 10))
        
        title = tk.Label(
            title_frame,
            text="🏰 TOWER OF HANOI GAME",
            bg=BG_COLOR,
            fg=ACCENT,
            font=("Helvetica", 22, "bold")
        )
        title.pack()
        
        separator = tk.Label(title_frame, text="═" * 50, bg=BG_COLOR, fg=ACCENT)
        separator.pack()

    # -------------------------------
    #  PLAYER INFO AND TIMER
    # -------------------------------
    def build_info_panel(self):
        """Build player information and timer display."""
        info_frame = tk.Frame(self.win, bg=BG_COLOR)
        info_frame.pack(pady=15)
        
        self.player_label = tk.Label(
            info_frame,
            text=f"👤 Player: {self.player}",
            bg=BG_COLOR,
            fg=TEXT,
            font=("Helvetica", 14, "bold")
        )
        self.player_label.pack(side="left", padx=25)
        
        self.time_label = tk.Label(
            info_frame,
            text="⏱️  Time: 0.00s",
            bg=BG_COLOR,
            fg=TEXT,
            font=("Helvetica", 14, "bold")
        )
        self.time_label.pack(side="left", padx=25)
        
        self.pause_btn = tk.Button(
            info_frame,
            text="⏸️  Pause",
            bg="#FFA500",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=12,
            height=1,
            command=self.toggle_pause,
            relief="raised",
            bd=2
        )
        self.pause_btn.pack(side="left", padx=15)

        self.reset_btn = tk.Button(
            info_frame,
            text="🔄 Reset",
            bg="#FF5722",
            fg="white",
            font=("Helvetica", 12, "bold"),
            width=10,
            height=1,
            command=self.reset_game,
            relief="raised",
            bd=2
        )
        self.reset_btn.pack(side="left", padx=15)

    # -------------------------------
    #  MOVE CONTROLS
    # -------------------------------
    def build_controls(self):
        """Build game control buttons and move selection."""
        frame = tk.Frame(self.win, bg=BG_COLOR)
        frame.pack(pady=15)

        options = [chr(ord("A") + i) for i in range(self.pegs)]

        self.from_var = tk.StringVar(value="A")
        self.to_var = tk.StringVar(value="B")

        tk.Label(frame, text="From:", bg=BG_COLOR, fg=TEXT, font=("Helvetica", 11, "bold")).pack(side="left", padx=8)
        ttk.Combobox(frame, textvariable=self.from_var, values=options, width=4, state="readonly", font=("Helvetica", 11)).pack(side="left", padx=5)

        tk.Label(frame, text="To:", bg=BG_COLOR, fg=TEXT, font=("Helvetica", 11, "bold")).pack(side="left", padx=8)
        ttk.Combobox(frame, textvariable=self.to_var, values=options, width=4, state="readonly", font=("Helvetica", 11)).pack(side="left", padx=5)

        tk.Button(frame, text="▶️  Make Move", bg=ACCENT, fg="black", font=("Helvetica", 11, "bold"),
                  command=self.do_move, relief="raised", bd=2, width=12, height=1).pack(side="left", padx=10)

        tk.Button(frame, text="⚡ Auto Solve", bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold"),
                  command=self.auto_solve, relief="raised", bd=2, width=12, height=1).pack(side="left", padx=8)

        tk.Button(frame, text="💾 Save & Quit", bg=CARD_COLOR, fg=TEXT, font=("Helvetica", 11, "bold"),
              command=self.save_and_exit, relief="raised", bd=2, width=12, height=1).pack(side="left", padx=8)

        tk.Button(frame, text="🎲 New Game", bg="#9C27B0", fg="white", font=("Helvetica", 11, "bold"),
              command=self.new_game, relief="raised", bd=2, width=12, height=1).pack(side="left", padx=8)

        tk.Button(frame, text="🔙 Back to Menu", bg="#B91C1C", fg="white", font=("Helvetica", 11, "bold"),
              command=self.back_to_menu, relief="raised", bd=2, width=12, height=1).pack(side="left", padx=8)
        
        # Stats below controls
        stats_frame = tk.Frame(self.win, bg=BG_COLOR)
        stats_frame.pack(pady=10)

        self.moves_label = tk.Label(stats_frame, text="🎮 Moves: 0", fg=TEXT, bg=BG_COLOR, font=("Helvetica", 13, "bold"))
        self.moves_label.pack(side="left", padx=20)

        opt = optimal_moves_count(self.disks, self.pegs)
        self.opt_label = tk.Label(stats_frame, text=f"✨ Optimal: {opt}", fg=ACCENT, bg=BG_COLOR, font=("Helvetica", 13, "bold"))
        self.opt_label.pack(side="left", padx=20)
    
    def toggle_pause(self):
        """Toggle pause state and freeze timer."""
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶️  Resume", bg="#2196F3")
        else:
            self.pause_btn.config(text="⏸️  Pause", bg="#FFA500")
    
    def reset_game(self):
        """Reset the game state: timer, disks, and move count."""
        self.manager = GameManager(pegs=self.pegs, disks=self.disks)
        self.manager.start()
        self.moves_label.config(text="🎮 Moves: 0")
        self.time_label.config(text="⏱️  Time: 0.00s")
        self.draw_pegs()
        self.paused = False
        self.pause_btn.config(text="⏸️  Pause", bg="#FFA500")
    
    def new_game(self):
        """Start a new game with random disk count and reset timer."""
        import random
        self.disks = random.randint(5, 10)
        self.manager = GameManager(pegs=self.pegs, disks=self.disks)
        self.manager.start()
        self.moves_label.config(text="🎮 Moves: 0")
        self.time_label.config(text="⏱️  Time: 0.00s")
        opt = optimal_moves_count(self.disks, self.pegs)
        self.opt_label.config(text=f"✨ Optimal: {opt}")
        self.draw_pegs()
        self.paused = False
        self.pause_btn.config(text="⏸️  Pause", bg="#FFA500")

    # -------------------------------
    #  DRAW DISKS + PEGS
    # -------------------------------
    def draw_pegs(self):
        """Draw the pegs and disks on the canvas."""
        self.canvas.delete("all")
        self.peg_positions = {}

        width = 780
        gap = width // (self.pegs + 1)
        peg_xs = []

        for i in range(self.pegs):
            x = gap * (i + 1)
            peg_xs.append(x)
            self.peg_positions[i] = {'x': x, 'disks': []}

            # Draw peg stand
            self.canvas.create_rectangle(x-5, 290, x+5, 60, fill="#1e293b", outline="")

            # Draw peg base
            self.canvas.create_rectangle(x-120, 310, x+120, 330, fill="#142030", outline="")
            
            # Draw peg label
            self.canvas.create_text(x, 345, text=chr(ord("A") + i), fill=ACCENT, font=("Helvetica", 12, "bold"))

        max_w = 180
        min_w = 40

        # Semi-saturated color palette for disks (outstanding but balanced)
        DISK_COLORS = [
            "#E57373", "#64B5F6", "#81C784", "#FFD54F", "#BA68C8",
            "#4DD0E1", "#FF8A65", "#F06292", "#9CCC65", "#4FC3F7",
            "#A1887F", "#7986CB"
        ]

        for p_idx, peg in enumerate(self.manager.pegs):
            x = peg_xs[p_idx]
            for level, disk in enumerate(peg):
                size_ratio = disk / self.disks
                w = min_w + int(size_ratio * (max_w - min_w))
                y = 310 - (level+1)*25
                color = DISK_COLORS[(disk-1) % len(DISK_COLORS)]
                
                # Create disk rectangle with tag for drag-drop
                rect_id = self.canvas.create_rectangle(
                    x-w//2, y-18, x+w//2, y, 
                    fill=color, outline="#333333", width=2
                )
                
                # Add disk number in center
                self.canvas.create_text(
                    x, y-9, 
                    text=str(disk), 
                    fill="white", 
                    font=("Helvetica", 12, "bold")
                )
                
                # Tag disk with position info
                self.canvas.tag_bind(rect_id, "<Button-1>", lambda e, d=disk, p=p_idx: self.on_disk_click(e, d, p))
                self.canvas.itemconfig(rect_id, tags=(f"disk_{disk}", f"peg_{p_idx}"))
                
                self.peg_positions[p_idx]['disks'].append((disk, rect_id))

    # Drag-drop handlers
    def on_disk_click(self, event, disk_num, peg_idx):
        """Handle disk click for dragging."""
        peg = self.manager.pegs[peg_idx]
        if peg and peg[-1] == disk_num:  # Only allow dragging if top disk
            self.dragging = True
            self.dragged_disk = disk_num
            self.dragged_disk_size = disk_num
            self.from_peg = peg_idx
            self.canvas.config(cursor="hand2")
    
    def on_canvas_click(self, event):
        """Handle canvas click."""
        pass  # Handled by disk-specific binding
    
    def on_canvas_drag(self, event):
        """Handle canvas drag motion with visual feedback."""
        if not self.dragging or self.dragged_disk is None:
            return
        
        # Remove old ghost if exists
        if self.drag_ghost_id:
            self.canvas.delete(self.drag_ghost_id)
            self.drag_ghost_id = None
        
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None
        
        # Draw semi-transparent ghost disk at cursor
        width = 780
        gap = width // (self.pegs + 1)
        max_w = 180
        min_w = 40
        
        size_ratio = self.dragged_disk_size / self.disks
        disk_w = min_w + int(size_ratio * (max_w - min_w))
        
        DISK_COLORS = [
            "#E57373", "#64B5F6", "#81C784", "#FFD54F", "#BA68C8",
            "#4DD0E1", "#FF8A65", "#F06292", "#9CCC65", "#4FC3F7",
            "#A1887F", "#7986CB"
        ]
        color = DISK_COLORS[(self.dragged_disk_size-1) % len(DISK_COLORS)]
        
        # Draw ghost disk following cursor
        ghost_y = event.y
        self.drag_ghost_id = self.canvas.create_rectangle(
            event.x - disk_w//2, ghost_y - 18,
            event.x + disk_w//2, ghost_y,
            fill=color, outline="#00FF00", width=3
        )
        
        # Find and highlight target peg
        for i in range(self.pegs):
            peg_x = gap * (i + 1)
            if peg_x - 100 <= event.x <= peg_x + 100:
                self.target_peg = i
                # Highlight the target peg base
                self.highlight_id = self.canvas.create_rectangle(
                    peg_x - 120, 310, peg_x + 120, 330,
                    fill="#00FF00", outline="#00FF00", width=2
                )
                self.canvas.tag_lower(self.highlight_id)
                break
        else:
            self.target_peg = None
        
        self.canvas.config(cursor="hand2")
    
    def on_canvas_release(self, event):
        """Handle canvas release to drop disk."""
        # Clean up ghost visuals
        if self.drag_ghost_id:
            self.canvas.delete(self.drag_ghost_id)
            self.drag_ghost_id = None
        
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            self.highlight_id = None
        
        if not self.dragging or self.dragged_disk is None:
            self.dragging = False
            self.canvas.config(cursor="arrow")
            return
        
        # Find which peg the mouse is over
        width = 780
        gap = width // (self.pegs + 1)
        to_peg = None
        
        for i in range(self.pegs):
            x = gap * (i + 1)
            # Check if mouse is within peg x-range (with margin)
            if x - 100 <= event.x <= x + 100:
                to_peg = i
                break
        
        self.dragging = False
        self.canvas.config(cursor="arrow")
        
        if to_peg is not None and to_peg != self.from_peg:
            try:
                self.manager.move(self.from_peg, to_peg)
                self.moves_label.config(text=f"🎮 Moves: {self.manager.moves_count}")
                self.draw_pegs()
                
                if self.manager.is_solved():
                    self.handle_win()
            except ValueError as e:
                messagebox.showwarning("Invalid Move", str(e), parent=self.win)
                self.draw_pegs()
        else:
            self.draw_pegs()

    # -------------------------------
    #  USER MOVE
    # -------------------------------
    def do_move(self):
        """Execute a user move with validation."""
        try:
            frm = ord(self.from_var.get()) - ord("A")
            to = ord(self.to_var.get()) - ord("A")

            if frm == to:
                messagebox.showwarning("Invalid Move", "Source and destination must be different!", parent=self.win)
                return

            self.manager.move(frm, to)
            self.moves_label.config(text=f"🎮 Moves: {self.manager.moves_count}")
            self.draw_pegs()
            
            if self.manager.is_solved():
                self.handle_win()
        except ValueError as e:
            messagebox.showwarning("Invalid Move", str(e), parent=self.win)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.win)

    # -------------------------------
    #  AUTO SOLVE
    # -------------------------------
    def auto_solve(self):
        """Automatically solve the puzzle using the optimal algorithm."""
        confirm_text = f"Solve the puzzle in {optimal_moves_count(self.disks, self.pegs)} optimal moves?\n(This will overwrite your current progress)"
        if not messagebox.askyesno("Auto Solve", confirm_text, parent=self.win):
            return

        moves, _ = timed_recursive_solution(self.disks, self.pegs)

        # Animate moves
        for a, b in moves:
            # Check if paused and wait
            while self.paused:
                self.win.update()
                time.sleep(0.1)
            
            try:
                frm = ord(a) - ord("A")
                to = ord(b) - ord("A")
                self.manager.move(frm, to)
            except:
                pass

            self.moves_label.config(text=f"🎮 Moves: {self.manager.moves_count}")
            self.draw_pegs()
            self.win.update()
            time.sleep(0.25)

        if self.manager.is_solved():
            self.handle_win()

    # -------------------------------
    #  WIN HANDLING
    # -------------------------------
    def handle_win(self):
        """Handle winning the game."""
        elapsed = self.manager.finish()
        _, algo_time = timed_recursive_solution(self.disks, self.pegs)
        optimal = optimal_moves_count(self.disks, self.pegs)

        try:
            solved = int(self.manager.is_solved())
            moves = self.manager.moves_count or 0
            efficiency = (optimal / moves) if solved and moves > 0 else 0.0
            database.insert_result(
                self.player, self.pegs, self.disks,
                moves, optimal,
                elapsed, algo_time,
                solved=solved,
                efficiency=efficiency
            )
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save result: {e}", parent=self.win)

        # Calculate performance
        efficiency = (optimal / self.manager.moves_count) * 100
        message = (
            f"🎉 SOLVED! 🎉\n"
            f"{'═' * 40}\n"
            f"👤 Player: {self.player}\n"
            f"🎮 Moves: {self.manager.moves_count} / {optimal} (optimal)\n"
            f"⭐ Efficiency: {efficiency:.1f}%\n"
            f"⏱️  Time: {elapsed:.2f} seconds"
        )

        messagebox.showinfo("Puzzle Solved", message, parent=self.win)

        # Return to main menu
        for w in self.win.winfo_children():
            w.destroy()
        self.win.title("Tower of Hanoi")
        self.win.geometry("1000x650")
        if self.menu:
            self.menu.build_ui()

    def back_to_menu(self):
        """Return to main menu without saving current progress (confirm)."""
        if not messagebox.askyesno("Confirm", "Return to main menu? Unsaved progress will be lost.", parent=self.win):
            return

        # Clear game UI and return
        for w in self.win.winfo_children():
            w.destroy()
        self.win.title("Tower of Hanoi")
        self.win.geometry("1000x650")
        if self.menu:
            self.menu.build_ui()

    # -------------------------------
    #  SAVE & EXIT
    # -------------------------------
    def save_and_exit(self):
        """Save progress and return to main menu."""
        if messagebox.askyesno("Save & Quit", "Save your progress and return to the main menu?", parent=self.win):
            elapsed = self.manager.finish() or 0.0
            _, algo_time = timed_recursive_solution(self.disks, self.pegs)
            optimal = optimal_moves_count(self.disks, self.pegs)

            try:
                solved = int(self.manager.is_solved())
                moves = self.manager.moves_count or 0
                efficiency = (optimal / moves) if solved and moves > 0 else 0.0
                database.insert_result(
                    self.player, self.pegs, self.disks,
                    moves, optimal,
                    elapsed, algo_time,
                    solved=solved,
                    efficiency=efficiency
                )
            except Exception as e:
                messagebox.showerror("Database Error", f"Could not save result: {e}", parent=self.win)

            # Return to main menu
            for w in self.win.winfo_children():
                w.destroy()
            self.win.title("Tower of Hanoi")
            self.win.geometry("1000x650")
            if self.menu:
                self.menu.build_ui()

    # -------------------------------
    #  TIMER
    # -------------------------------
    def update_timer(self):
        """Update the game timer every 200ms."""
        if self.manager.start_time and not self.manager.end_time and not self.paused:
            t = time.perf_counter() - self.manager.start_time
            self.time_label.config(text=f"⏱️  Time: {t:.2f}s")

        self.win.after(200, self.update_timer)
