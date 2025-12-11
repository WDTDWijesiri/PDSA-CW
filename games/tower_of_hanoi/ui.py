import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import time
from game import GameManager
from algorithms import optimal_moves_count, timed_recursive_solution
import database

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

        self.build_ui()

    def run(self):
        self.root.mainloop()

    # -------------------------------
    #  BUILD MAIN MENU UI
    # -------------------------------
    def build_ui(self):
        title = tk.Label(
            self.root,
            text="TOWER OF HANOI",
            bg=BG_COLOR,
            fg=ACCENT,
            font=TITLE_FONT
        )
        title.pack(pady=(40, 10))

        subtitle = tk.Label(
            self.root,
            text="Algorithmic Puzzle Simulator",
            bg=BG_COLOR,
            fg=TEXT,
            font=PIXEL_FONT
        )
        subtitle.pack(pady=(0, 30))

        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack()

        buttons = [
            ("Start Game", self.start_game_flow),
            ("Statistics", self.show_statistics),
            ("Leaderboard", self.show_leaderboard),
            ("Algorithms Info", self.show_algorithm_info),
            ("Quit Game", self.root.destroy),
        ]

        for text, cmd in buttons:
            btn = tk.Button(
                frame,
                text=text,
                width=20,
                height=2,
                command=cmd,
                bg=CARD_COLOR,
                fg=TEXT,
                font=PIXEL_FONT,
                activebackground=ACCENT
            )
            btn.pack(pady=10)

    # -------------------------------
    #  START GAME WORKFLOW
    # -------------------------------
    def start_game_flow(self):
        # Temporary loading window
        temp_window = tk.Toplevel(self.root)
        temp_window.title("Loading Game...")
        temp_window.geometry("400x200")
        temp_window.configure(bg=BG_COLOR)

        tk.Label(
            temp_window,
            text="Preparing your Tower of Hanoi Game...",
            bg=BG_COLOR,
            fg=ACCENT,
            font=PIXEL_FONT
        ).pack(pady=40)

        temp_window.update()

        # Ask inputs
        name = simpledialog.askstring("Player Name", "Enter your name:", parent=self.root)
        if not name:
            temp_window.destroy()
            return

        pegs = simpledialog.askinteger("Pegs", "Select number of pegs (3 or 4):", minvalue=3, maxvalue=4)
        if pegs not in (3, 4):
            pegs = 3

        disks = random.randint(5, 10)
        messagebox.showinfo("Disks", f"Disks selected: {disks}")

        rules = (
            "• Move 1 disk at a time\n"
            "• No large disk on a smaller one\n"
            "• Solve using 3 or 4 pegs\n"
            "• Try to beat the optimal moves!"
        )
        messagebox.showinfo("Rules", rules)

        temp_window.destroy()

        # launch game inside the same window (replace menu)
        for w in self.root.winfo_children():
            w.destroy()

        GameWindow(self.root, name, pegs, disks, menu=self)

    # -------------------------------
    #  STATISTICS WINDOW
    # -------------------------------
    def show_statistics(self):
        rows = database.fetch_all()

        win = tk.Toplevel(self.root)
        win.title("Statistics")
        win.configure(bg=BG_COLOR)

        title = tk.Label(win, text="Game Records", bg=BG_COLOR, fg=ACCENT, font=PIXEL_FONT)
        title.pack(pady=10)

        cols = ["Player", "Pegs", "Disks", "Moves", "Optimal", "Time", "Algo Time", "Date"]
        tree = ttk.Treeview(win, columns=cols, show="headings", height=15)

        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110, anchor="center")

        for r in rows:
            tree.insert("", "end", values=r)

        tree.pack(padx=20, pady=10)

        tk.Button(win, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=10)

    # -------------------------------
    #  LEADERBOARD
    # -------------------------------
    def show_leaderboard(self):
        rows = database.fetch_leaderboard()

        win = tk.Toplevel(self.root)
        win.title("Leaderboard")
        win.configure(bg=BG_COLOR)

        tk.Label(win, text="Leaderboard", bg=BG_COLOR, fg=ACCENT, font=PIXEL_FONT).pack(pady=10)

        for i, r in enumerate(rows, start=1):
            player, pegs, disks, moves, optimal, t, date, diff = r
            line = f"{i}. {player} — {disks} disks — {moves} moves (opt {optimal}) — {t:.2f}s"
            tk.Label(win, text=line, bg=BG_COLOR, fg=TEXT, font=SMALL_FONT).pack(anchor="w", padx=20)

        tk.Button(win, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=10)

    # -------------------------------
    #  ALGORITHM INFO
    # -------------------------------
    def show_algorithm_info(self):
        win = tk.Toplevel(self.root)
        win.title("Algorithm Info")
        win.configure(bg=BG_COLOR)

        txt = (
            "Tower of Hanoi Algorithm\n"
            "• Recursive method\n"
            "• Time Complexity: O(2^n)\n"
            "• Optimal = 2^n - 1\n\n"
            "We use recursion to simulate optimal moves."
        )

        tk.Label(win, text=txt, bg=BG_COLOR, fg=TEXT, font=SMALL_FONT, justify="left").pack(padx=20, pady=20)

        tk.Button(win, text="Show Example (3 disks)", bg=CARD_COLOR, fg=TEXT,
                  command=lambda: self.show_example(3)).pack(pady=8)

        tk.Button(win, text="Close", command=win.destroy, bg=CARD_COLOR, fg=TEXT).pack(pady=8)

    def show_example(self, n):
        moves, t = timed_recursive_solution(n)
        s = "\n".join([f"{i+1}. {a}->{b}" for i, (a, b) in enumerate(moves)])
        messagebox.showinfo("Example", f"{len(moves)} moves in {t:.6f}s\n\n{s}")


# ------------------------------------------------
# GAME WINDOW
# ------------------------------------------------
class GameWindow:
    def __init__(self, parent, player, pegs, disks, menu=None):
        self.player = player
        self.pegs = pegs
        self.disks = disks

        self.menu = menu
        self.win = parent
        self.win.title(f"Tower - {player}")
        self.win.geometry("900x600")
        self.win.configure(bg=BG_COLOR)

        self.manager = GameManager(pegs=pegs, disks=disks)
        self.manager.start()

        self.canvas = tk.Canvas(self.win, bg="#0b1220", width=780, height=360, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.build_info_panel()
        self.build_controls()
        self.draw_pegs()

        self.update_timer()

    # -------------------------------
    #  INFO PANEL
    # -------------------------------
    def build_info_panel(self):
        frame = tk.Frame(self.win, bg=BG_COLOR)
        frame.pack()

        self.moves_label = tk.Label(frame, text="Moves: 0", fg=TEXT, bg=BG_COLOR, font=SMALL_FONT)
        self.moves_label.pack(side="left", padx=10)

        opt = optimal_moves_count(self.disks)
        self.opt_label = tk.Label(frame, text=f"Optimal: {opt}", fg=TEXT, bg=BG_COLOR, font=SMALL_FONT)
        self.opt_label.pack(side="left", padx=10)

        self.time_label = tk.Label(frame, text="Time: 0.00s", fg=TEXT, bg=BG_COLOR, font=SMALL_FONT)
        self.time_label.pack(side="left", padx=10)

    # -------------------------------
    #  MOVE CONTROLS
    # -------------------------------
    def build_controls(self):
        frame = tk.Frame(self.win, bg=BG_COLOR)
        frame.pack(pady=10)

        options = [chr(ord("A") + i) for i in range(self.pegs)]

        self.from_var = tk.StringVar(value="A")
        self.to_var = tk.StringVar(value="B")

        tk.Label(frame, text="From:", bg=BG_COLOR, fg=TEXT).pack(side="left")
        ttk.Combobox(frame, textvariable=self.from_var, values=options, width=4, state="readonly").pack(side="left")

        tk.Label(frame, text="To:", bg=BG_COLOR, fg=TEXT).pack(side="left", padx=10)
        ttk.Combobox(frame, textvariable=self.to_var, values=options, width=4, state="readonly").pack(side="left")

        tk.Button(frame, text="Move", bg=ACCENT, fg="black", command=self.do_move).pack(side="left", padx=10)

        tk.Button(frame, text="Auto Solve", bg=CARD_COLOR, fg=TEXT, command=self.auto_solve).pack(side="left", padx=10)

        tk.Button(frame, text="Save & Exit", bg=CARD_COLOR, fg=TEXT, command=self.save_and_exit).pack(side="left", padx=10)

    # -------------------------------
    #  DRAW DISKS + PEGS
    # -------------------------------
    def draw_pegs(self):
        self.canvas.delete("all")

        width = 780
        gap = width // (self.pegs + 1)
        peg_xs = []

        for i in range(self.pegs):
            x = gap * (i + 1)
            peg_xs.append(x)

            self.canvas.create_rectangle(x-5, 310, x+5, 80, fill="#1e293b", outline="")

            self.canvas.create_rectangle(x-120, 310, x+120, 330, fill="#142030", outline="")

        max_w = 180
        min_w = 40

        # colorful rainbow palette (repeats if more disks than colors)
        RAINBOW = [
            "#FF0000", "#FF7F00", "#FFFF00", "#7FFF00", "#00FF00",
            "#00FF7F", "#00FFFF", "#007FFF", "#0000FF", "#7F00FF",
            "#FF00FF", "#FF007F"
        ]

        for p_idx, peg in enumerate(self.manager.pegs):
            x = peg_xs[p_idx]
            # peg list stores disks bottom->top (index 0 bottom)
            for level, disk in enumerate(peg):
                size_ratio = disk / self.disks
                w = min_w + int(size_ratio * (max_w - min_w))
                y = 310 - (level+1)*25
                color = RAINBOW[(disk-1) % len(RAINBOW)]
                self.canvas.create_rectangle(x-w//2, y-18, x+w//2, y, fill=color, outline="black")

    # -------------------------------
    #  USER MOVE
    # -------------------------------
    def do_move(self):
        frm = ord(self.from_var.get()) - ord("A")
        to = ord(self.to_var.get()) - ord("A")

        try:
            self.manager.move(frm, to)
            self.moves_label.config(text=f"Moves: {self.manager.moves_count}")
            self.draw_pegs()
            if self.manager.is_solved():
                self.handle_win()
        except Exception as e:
            messagebox.showwarning("Invalid Move", str(e))

    # -------------------------------
    #  AUTO SOLVE
    # -------------------------------
    def auto_solve(self):
        moves, _ = timed_recursive_solution(self.disks)

        # Animate moves
        for a, b in moves:
            frm = ord(a) - ord("A")
            to = ord(b) - ord("A")

            try:
                self.manager.move(frm, to)
            except:
                pass

            self.moves_label.config(text=f"Moves: {self.manager.moves_count}")
            self.draw_pegs()
            self.win.update()
            time.sleep(0.25)

        if self.manager.is_solved():
            self.handle_win()

    # -------------------------------
    #  WIN HANDLING
    # -------------------------------
    def handle_win(self):
        elapsed = self.manager.finish()
        _, algo_time = timed_recursive_solution(self.disks)
        optimal = optimal_moves_count(self.disks)

        database.insert_result(
            self.player, self.pegs, self.disks,
            self.manager.moves_count, optimal,
            elapsed, algo_time
        )

        messagebox.showinfo(
            "Solved!",
            f"You did it!\nMoves: {self.manager.moves_count}\nOptimal: {optimal}\nTime: {elapsed:.2f}s"
        )

        # return to main menu in same window
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
        elapsed = self.manager.finish() or 0.0
        _, algo_time = timed_recursive_solution(self.disks)
        optimal = optimal_moves_count(self.disks)

        database.insert_result(
            self.player, self.pegs, self.disks,
            self.manager.moves_count, optimal,
            elapsed, algo_time
        )
        # return to main menu in same window
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
        if self.manager.start_time and not self.manager.end_time:
            t = time.perf_counter() - self.manager.start_time
            self.time_label.config(text=f"Time: {t:.2f}s")

        self.win.after(200, self.update_timer)
