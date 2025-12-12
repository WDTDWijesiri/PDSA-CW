import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
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
CARD_COLOR = "#1e293b"     # softer dark card
ACCENT = "#00E5FF"         # soft baby-blue
TEXT = "#f1f5f9"           # almost white
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
        self.root.title("Tower of Hanoi")
        self.root.geometry("1000x650")
        self.root.configure(bg=BG_COLOR)
        
        # Center window on screen
        self._center_window(self.root)

        self.build_ui()
    
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
            ("▶️  START GAME", self.start_game_flow),
            ("📊  STATISTICS", self.show_statistics),
            ("🏆  LEADERBOARD", self.show_leaderboard),
            ("🧠  ALGORITHM INFO", self.show_algorithm_info),
            ("🚪  QUIT GAME", self.root.destroy),
        ]

        for text, cmd in buttons:
            btn = tk.Button(
                frame,
                text=text,
                width=25,
                height=2,
                command=cmd,
                bg=CARD_COLOR,
                fg=TEXT,
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
        messagebox.showinfo("Disks", f"Disks selected: {disks}\n\nGood luck!")

        # Show game rules
        rules = (
            "TOWER OF HANOI RULES\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• Move 1 disk at a time\n"
            "• Never place larger disk on smaller\n"
            "• Solve with {0} pegs\n"
            "• Try to beat the optimal: {1} moves".format(pegs, 2**disks - 1)
        )
        messagebox.showinfo("Rules", rules)

        # Launch game
        for w in self.root.winfo_children():
            w.destroy()

        GameWindow(self.root, name, pegs, disks, menu=self)
    
    def _get_player_name(self):
        """Get and validate player name from user."""
        while True:
            name = simpledialog.askstring(
                "Player Name", 
                "Enter your name:",
                parent=self.root
            )
            if name is None:  # User cancelled
                return None
            if len(name.strip()) < 2:
                messagebox.showwarning(
                    "Invalid Name",
                    "Name must be at least 2 characters!",
                    parent=self.root
                )
                continue
            if len(name) > 20:
                messagebox.showwarning(
                    "Invalid Name",
                    "Name must be 20 characters or less!",
                    parent=self.root
                )
                continue
            return name.strip()
    
    def _get_pegs_choice(self):
        """Get number of pegs from user."""
        while True:
            pegs = simpledialog.askinteger(
                "Number of Pegs",
                "Select number of pegs:\n3 = Classic Tower of Hanoi\n4 = Frame-Stewart Algorithm",
                minvalue=3,
                maxvalue=4,
                parent=self.root
            )
            if pegs is None:  # User cancelled
                return 3
            if pegs in (3, 4):
                return pegs
            messagebox.showwarning(
                "Invalid Choice",
                "Please select 3 or 4 pegs!",
                parent=self.root
            )

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

        title = tk.Label(win, text="📊 Game Records", bg=BG_COLOR, fg=ACCENT, font=PIXEL_FONT)
        title.pack(pady=10)
        separator = tk.Label(win, text="═" * 115, bg=BG_COLOR, fg=ACCENT)
        separator.pack(pady=(0, 10))

        cols = ["Player", "Pegs", "Disks", "Moves", "Optimal", "Time (s)", "Algo Time (s)", "Solved", "Efficiency (%)", "Date"]
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")

        for r in rows:
            # rows: player, pegs, disks, moves, optimal_moves, time_taken, algorithm_time, solved, efficiency, date
            player, pegs, disks, moves, optimal, t_algo, algo_time, solved, efficiency, date = r
            solved_text = "Yes" if solved else "No"
            eff_pct = f"{(efficiency*100):.1f}" if efficiency is not None else "0.0"
            tree.insert("", "end", values=(player, pegs, disks, moves, optimal, t_algo, algo_time, solved_text, eff_pct, date))

        tree.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Button(win, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=10)

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

        tk.Label(win, text="🏆 Leaderboard (Completed Games)", bg=BG_COLOR, fg=ACCENT, font=PIXEL_FONT).pack(pady=10)
        separator = tk.Label(win, text="═" * 100, bg=BG_COLOR, fg=ACCENT)
        separator.pack(pady=(0, 10))

        cols = ["Rank", "Player", "Pegs", "Disks", "Moves", "Optimal", "Efficiency (%)", "Time (s)", "Solved", "Date"]
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)

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

        tree.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Button(win, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=8)

    # -------------------------------
    #  ALGORITHM INFO
    # -------------------------------
    def show_algorithm_info(self):
        """Display information about the Tower of Hanoi algorithm."""
        win = tk.Toplevel(self.root)
        win.title("Algorithm Information")
        win.configure(bg=BG_COLOR)
        center_dialog_on_parent(self.root, win, 500, 400)

        txt = (
            "🧠 TOWER OF HANOI ALGORITHM\n"
            "═" * 52 + "\n\n"
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

        label = tk.Label(win, text=txt, bg=BG_COLOR, fg=TEXT, font=("Courier", 11), justify="left")
        label.pack(padx=20, pady=20)

        frame = tk.Frame(win, bg=BG_COLOR)
        frame.pack(pady=10)

        tk.Button(frame, text="Show Example (3 disks)", bg=ACCENT, fg="black",
                  command=lambda: self.show_example(3)).pack(side="left", padx=5)

        tk.Button(frame, text="Show Example (5 disks)", bg=ACCENT, fg="black",
                  command=lambda: self.show_example(5)).pack(side="left", padx=5)

        tk.Button(frame, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(side="left", padx=5)

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

        tk.Label(scrollable, text=s, bg=BG_COLOR, fg=TEXT, font=SMALL_FONT, justify="left").pack(anchor="w", padx=10, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(example_win, text="Close", command=example_win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=10)


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
        self.win.geometry("900x700")
        self.win.configure(bg=BG_COLOR)
        self._center_game_window()

        self.manager = GameManager(pegs=pegs, disks=disks)
        self.manager.start()

        self.canvas = tk.Canvas(self.win, bg="#0b1220", width=780, height=360, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.build_info_panel()
        self.build_controls()
        self.draw_pegs()

        self.update_timer()
    
    def _center_game_window(self):
        """Center the game window on the screen."""
        self.win.update_idletasks()
        screen_width = self.win.winfo_screenwidth()
        screen_height = self.win.winfo_screenheight()
        
        window_width = 900
        window_height = 700
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # -------------------------------
    #  INFO PANEL
    # -------------------------------
    def build_info_panel(self):
        """Build information display panel."""
        frame = tk.Frame(self.win, bg=BG_COLOR)
        frame.pack(pady=10)

        self.moves_label = tk.Label(frame, text="🎮 Moves: 0", fg=TEXT, bg=BG_COLOR, font=SMALL_FONT)
        self.moves_label.pack(side="left", padx=15)

        opt = optimal_moves_count(self.disks)
        self.opt_label = tk.Label(frame, text=f"✨ Optimal: {opt}", fg=ACCENT, bg=BG_COLOR, font=SMALL_FONT)
        self.opt_label.pack(side="left", padx=15)

        self.time_label = tk.Label(frame, text="⏱️  Time: 0.00s", fg=TEXT, bg=BG_COLOR, font=SMALL_FONT)
        self.time_label.pack(side="left", padx=15)

    # -------------------------------
    #  MOVE CONTROLS
    # -------------------------------
    def build_controls(self):
        """Build game control buttons and move selection."""
        frame = tk.Frame(self.win, bg=BG_COLOR)
        frame.pack(pady=12)

        options = [chr(ord("A") + i) for i in range(self.pegs)]

        self.from_var = tk.StringVar(value="A")
        self.to_var = tk.StringVar(value="B")

        tk.Label(frame, text="From:", bg=BG_COLOR, fg=TEXT, font=SMALL_FONT).pack(side="left", padx=8)
        ttk.Combobox(frame, textvariable=self.from_var, values=options, width=4, state="readonly").pack(side="left", padx=5)

        tk.Label(frame, text="To:", bg=BG_COLOR, fg=TEXT, font=SMALL_FONT).pack(side="left", padx=8)
        ttk.Combobox(frame, textvariable=self.to_var, values=options, width=4, state="readonly").pack(side="left", padx=5)

        tk.Button(frame, text="▶️  Make Move", bg=ACCENT, fg="black", font=("Helvetica", 10, "bold"),
                  command=self.do_move).pack(side="left", padx=10)

        tk.Button(frame, text="⚡ Auto Solve", bg="#4CAF50", fg="white",
                  command=self.auto_solve).pack(side="left", padx=8)

        tk.Button(frame, text="💾 Save & Quit", bg=CARD_COLOR, fg=TEXT,
              command=self.save_and_exit).pack(side="left", padx=8)

        tk.Button(frame, text="🔙 Back to Menu", bg="#B91C1C", fg="white",
              command=self.back_to_menu).pack(side="left", padx=8)

    # -------------------------------
    #  DRAW DISKS + PEGS
    # -------------------------------
    def draw_pegs(self):
        """Draw the pegs and disks on the canvas."""
        self.canvas.delete("all")

        width = 780
        gap = width // (self.pegs + 1)
        peg_xs = []

        for i in range(self.pegs):
            x = gap * (i + 1)
            peg_xs.append(x)

            # Draw peg stand
            self.canvas.create_rectangle(x-5, 310, x+5, 80, fill="#1e293b", outline="")

            # Draw peg base
            self.canvas.create_rectangle(x-120, 310, x+120, 330, fill="#142030", outline="")
            
            # Draw peg label
            self.canvas.create_text(x, 345, text=chr(ord("A") + i), fill=ACCENT, font=("Helvetica", 12, "bold"))

        max_w = 180
        min_w = 40

        # Rainbow color palette for disks
        RAINBOW = [
            "#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00",
            "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF",
            "#FF00FF", "#FF007F"
        ]

        for p_idx, peg in enumerate(self.manager.pegs):
            x = peg_xs[p_idx]
            for level, disk in enumerate(peg):
                size_ratio = disk / self.disks
                w = min_w + int(size_ratio * (max_w - min_w))
                y = 310 - (level+1)*25
                color = RAINBOW[(disk-1) % len(RAINBOW)]
                self.canvas.create_rectangle(x-w//2, y-18, x+w//2, y, fill=color, outline="black", width=2)

    # -------------------------------
    #  USER MOVE
    # -------------------------------
    def do_move(self):
        """Execute a user move with validation."""
        try:
            frm = ord(self.from_var.get()) - ord("A")
            to = ord(self.to_var.get()) - ord("A")

            if frm == to:
                messagebox.showwarning(
                    "Invalid Move",
                    "Source and destination must be different!",
                    parent=self.win
                )
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
        if not messagebox.askyesno(
            "Auto Solve",
            f"Solve the puzzle in {optimal_moves_count(self.disks)} optimal moves?\n(This will overwrite your current progress)",
            parent=self.win
        ):
            return

        moves, _ = timed_recursive_solution(self.disks)

        # Animate moves
        for a, b in moves:
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
        _, algo_time = timed_recursive_solution(self.disks)
        optimal = optimal_moves_count(self.disks)

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
        if messagebox.askyesno(
            "Save & Quit",
            "Save your progress and return to the main menu?",
            parent=self.win
        ):
            elapsed = self.manager.finish() or 0.0
            _, algo_time = timed_recursive_solution(self.disks)
            optimal = optimal_moves_count(self.disks)

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
        if self.manager.start_time and not self.manager.end_time:
            t = time.perf_counter() - self.manager.start_time
            self.time_label.config(text=f"Time: {t:.2f}s")

        self.win.after(200, self.update_timer)
