import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import sqlite3
from datetime import datetime
import time
import unittest
from pathlib import Path

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# For charts and analysis
import matplotlib.pyplot as plt
import numpy as np

DB_PATH = Path("snake_ladder_problem.db")
ASSETS_DIR = Path(__file__).parent / "assets"



#  DB LAYER


class ProblemGameDB:
    """SQLite wrapper for the Snake and Ladder Game Problem."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.init_schema()

    def init_schema(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS min_throws_game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                board_size INTEGER NOT NULL,
                correct_answer INTEGER NOT NULL,
                user_answer INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                bfs_time_ms REAL NOT NULL,
                dp_time_ms REAL NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def save_result(
        self,
        player_name: str,
        board_size: int,
        correct_answer: int,
        user_answer: int,
        is_correct: bool,
        bfs_time_ms: float,
        dp_time_ms: float,
    ):
        try:
            self.cursor.execute(
                """
                INSERT INTO min_throws_game
                    (player_name, board_size, correct_answer, user_answer,
                     is_correct, bfs_time_ms, dp_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    player_name,
                    board_size,
                    correct_answer,
                    user_answer,
                    int(is_correct),
                    bfs_time_ms,
                    dp_time_ms,
                ),
            )
            self.conn.commit()
        except Exception as e:
            print(f"DB insert error: {e}")

    def fetch_stats_by_board_size(self):
        self.cursor.execute(
            """
            SELECT
                board_size,
                COUNT(*) as total_games,
                SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
                AVG(bfs_time_ms) as avg_bfs,
                AVG(dp_time_ms) as avg_dp
            FROM min_throws_game
            GROUP BY board_size
            ORDER BY board_size
            """
        )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()



#  MAIN GAME

class SnakeAndLadderProblemGame:
    """
    Snake and Ladder Game Problem, cozy style with responsive layout.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake and Ladder Game Problem")

        # Fullscreen / maximized
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.attributes("-zoomed", True)
        self.root.configure(bg="#88cfff")
        self.root.resizable(True, True)

        # Track current size for responsive layout
        self.window_width = self.root.winfo_screenwidth()
        self.window_height = self.root.winfo_screenheight()
        self.root.bind("<Configure>", self.on_resize)

        # Theme colors
        self.color_sky = "#88cfff"
        self.color_grass = "#7bc96f"
        self.color_dirt = "#b87a42"
        self.color_wood_light = "#f0d3aa"
        self.color_wood_dark = "#a86c3f"
        self.color_panel = "#fdf7ee"
        self.color_panel_alt = "#f5ebdd"
        self.color_accent = "#f6a623"
        self.color_accent2 = "#f46e6e"
        self.color_accent3 = "#58a6ff"
        self.color_text = "#3c3c3c"

        # Game state
        self.board_size: int = 8
        self.snakes = {}
        self.ladders = {}
        self.min_throws_answer: int | None = None
        self.algorithm_times = {"bfs": 0.0, "dp": 0.0}
        self.correct_option_index: int | None = None
        self.current_options: list[int] = []

        # DB
        self.db = ProblemGameDB()

        # Anim helpers
        self._title_phase = 0
        self._snake_wiggle_phase = 0
        self._board_cells_to_reveal = []

        # Image cache
        self.images = {}
        self._tk_img_cache = {}
        self.load_images()

        self.build_main_menu()

    
    #  Responsive helpers
    
    def on_resize(self, event: tk.Event):
        if event.width <= 1 or event.height <= 1:
            return
        self.window_width = event.width
        self.window_height = event.height

    def get_board_canvas_size(self) -> tuple[int, int]:
        """
        For the play screen we want the board as large as possible.

        Increase it even more: almost all remaining space.
        """
        cw = int(self.window_width * 0.68)   # 68% of width
        ch = int(self.window_height * 0.8)   # 80% of height
        cw = max(min(cw, 1400), 750)
        ch = max(min(ch, 1000), 750)
        return cw, ch

    
    #  Images
    
    def load_images(self):
        if not PIL_AVAILABLE:
            print("PIL not available; running without image assets.")
            return

        def load(name: str):
            path = ASSETS_DIR / name
            if path.exists():
                try:
                    img = Image.open(path).convert("RGBA")
                    self.images[name] = img
                except Exception as e:
                    print(f"Failed to load {name}: {e}")
            else:
                print(f"Asset not found (fallback to colors): {name}")

        load("background_sky.png")
        load("background_grass.png")
        load("panel_wood.png")
        load("button_wood.png")
        load("tile_normal.png")
        load("tile_snake.png")
        load("tile_ladder.png")
        load("snake_head.png")
        load("ladder.png")
        load("logo.png")

    def get_tk_image(self, name: str, size=None):
        if name not in self.images or not PIL_AVAILABLE:
            return None
        base = self.images[name]
        if size is None:
            size = base.size
        key = (name, size)
        if key not in self._tk_img_cache:
            img = base.resize(size, Image.NEAREST)
            self._tk_img_cache[key] = ImageTk.PhotoImage(img)
        return self._tk_img_cache[key]

    
    #  Common helpers
    
    def clear_window(self):
        for w in self.root.winfo_children():
            w.destroy()

    def start_title_animation(self, label: tk.Label):
        colors = ["#ffffff", "#ffe6a1", "#ffffff", "#ffd5bf"]
        max_pad = 12

        def step():
            try:
                self._title_phase += 1
                c = colors[self._title_phase % len(colors)]
                label.config(fg=c)
                offset = (self._title_phase % (2 * max_pad)) - max_pad
                pad = 10 + abs(offset)
                label.pack_configure(padx=pad)
                self.root.after(300, step)
            except tk.TclError:
                return

        step()

    
    #  UI: Main menu
    
    def build_main_menu(self):
        self.clear_window()

        sky = tk.Frame(self.root, bg=self.color_sky)
        sky.pack(fill=tk.BOTH, expand=True)

        # Background sky image if available
        if "background_sky.png" in self.images and PIL_AVAILABLE:
            bg_img = self.get_tk_image(
                "background_sky.png",
                (self.window_width, self.window_height),
            )
            bg_label = tk.Label(sky, image=bg_img, bg=self.color_sky)
            bg_label.image = bg_img
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        grass_strip_height = max(int(self.window_height * 0.08), 60)
        grass_strip = tk.Frame(sky, bg=self.color_grass, height=grass_strip_height)
        grass_strip.pack(side=tk.BOTTOM, fill=tk.X)

        if "background_grass.png" in self.images and PIL_AVAILABLE:
            grass_img = self.get_tk_image(
                "background_grass.png",
                (self.window_width, grass_strip_height),
            )
            g_label = tk.Label(grass_strip, image=grass_img, bg=self.color_grass)
            g_label.image = grass_img
            g_label.place(x=0, y=0, relwidth=1, relheight=1)

        main_frame = tk.Frame(sky, bg="", highlightthickness=0)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(20, 10))

        # Title area centered
        sign_outer = tk.Frame(
            main_frame, bg=self.color_wood_dark, bd=3, relief=tk.RIDGE
        )
        sign_outer.pack(pady=(0, 15))

        sign_inner = tk.Frame(sign_outer, bg=self.color_wood_light, padx=25, pady=12)
        sign_inner.pack()

        if "logo.png" in self.images and PIL_AVAILABLE:
            logo_w = min(int(self.window_width * 0.28), 420)
            logo_h = min(int(self.window_height * 0.16), 180)
            logo_w = max(260, logo_w)
            logo_h = max(110, logo_h)
            logo_img = self.get_tk_image("logo.png", (logo_w, logo_h))
            logo_label = tk.Label(sign_inner, image=logo_img, bg=self.color_wood_light)
            logo_label.image = logo_img
            logo_label.pack()
        else:
            title_label = tk.Label(
                sign_inner,
                text="Snake & Ladder\nGame Problem",
                font=("Segoe UI", 30, "bold"),
                bg=self.color_wood_light,
                fg="white",
            )
            title_label.pack()
            self.start_title_animation(title_label)

        subtitle = tk.Label(
            main_frame,
            text="A cozy puzzle where algorithms meet board games.",
            font=("Segoe UI", 13),
            bg=self.color_sky,
            fg="#ffffff",
        )
        subtitle.pack(pady=(0, 15))

        # Main content
        content = tk.Frame(main_frame, bg="")
        content.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(content, bg="", padx=0)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(content, bg="", padx=10, width=260)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        # LEFT: card panel centered
        left_outer = tk.Frame(
            left,
            bg=self.color_wood_dark,
            bd=2,
            relief=tk.RIDGE,
        )
        left_outer.pack(
            pady=10,
            padx=int(self.window_width * 0.08),
            fill=tk.X,
            expand=False,
        )

        left_inner = tk.Frame(left_outer, bg=self.color_panel, padx=28, pady=18)
        left_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            left_inner,
            text="Board Size",
            font=("Segoe UI", 18, "bold"),
            bg=self.color_panel,
            fg=self.color_text,
        ).pack(pady=(0, 6))

        tk.Label(
            left_inner,
            text="Choose N for an N×N board (6–12).\nSnakes = Ladders = N − 2.",
            font=("Segoe UI", 11),
            bg=self.color_panel,
            fg=self.color_text,
            justify=tk.CENTER,
        ).pack(pady=(0, 10))

        self.size_var = tk.IntVar(value=8)
        slider_frame = tk.Frame(left_inner, bg=self.color_panel)
        slider_frame.pack(pady=12)

        tk.Label(
            slider_frame,
            text="N =",
            font=("Segoe UI", 12, "bold"),
            bg=self.color_panel,
            fg=self.color_text,
        ).pack(side=tk.LEFT, padx=(0, 4))

        size_slider = tk.Scale(
            slider_frame,
            from_=6,
            to=12,
            orient=tk.HORIZONTAL,
            variable=self.size_var,
            length=220,
            bg=self.color_panel,
            fg=self.color_text,
            troughcolor="#e3d2bc",
            highlightbackground=self.color_panel,
        )
        size_slider.pack(side=tk.LEFT, padx=8)

        size_label = tk.Label(
            slider_frame,
            text=f"({self.size_var.get()}×{self.size_var.get()})",
            font=("Segoe UI", 11, "bold"),
            bg=self.color_panel,
            fg=self.color_accent2,
        )
        size_label.pack(side=tk.LEFT, padx=6)

        def update_label(*_):
            size_label.config(
                text=f"({self.size_var.get()}×{self.size_var.get()})"
            )

        self.size_var.trace("w", update_label)

        btn_bg = self.color_accent
        start_btn = tk.Button(
            left_inner,
            text="Start New Problem Round",
            command=self.start_new_round,
            font=("Segoe UI", 12, "bold"),
            bg=btn_bg,
            fg="white",
            activebackground="#f8c15a",
            activeforeground="white",
            padx=26,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT,
        )
        start_btn.pack(pady=(14, 8))
        start_btn.configure(
            highlightthickness=1,
            highlightbackground="#b07b27",
        )

        # RIGHT: slim info panel
        right_outer = tk.Frame(
            right,
            bg=self.color_wood_dark,
            bd=2,
            relief=tk.RIDGE,
        )
        right_outer.pack(pady=10, fill=tk.Y, expand=False)

        right_inner = tk.Frame(right_outer, bg=self.color_panel_alt, padx=18, pady=14)
        right_inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            right_inner,
            text="About This Game",
            font=("Segoe UI", 15, "bold"),
            bg=self.color_panel_alt,
            fg=self.color_text,
        ).pack(pady=(0, 8))

        tk.Label(
            right_inner,
            text=(
                "• Classic snake & ladder board.\n"
                "• Random cozy boards each round.\n"
                "• Compute minimum dice throws.\n"
                "• Compare BFS and DP algorithms.\n"
                "• Three multiple‑choice answers.\n"
                "• Stores player results & timings."
            ),
            font=("Segoe UI", 10),
            bg=self.color_panel_alt,
            fg=self.color_text,
            justify=tk.LEFT,
        ).pack(pady=(0, 12), anchor=tk.W)

        stats_btn = tk.Button(
            right_inner,
            text="View Algorithm Stats",
            command=self.show_algorithm_stats,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_accent3,
            fg="white",
            activebackground="#7fb8ff",
            activeforeground="white",
            padx=16,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
        )
        stats_btn.pack(pady=(4, 4))
        stats_btn.configure(
            highlightthickness=1,
            highlightbackground="#24529b",
        )

        # NEW: Chart & Analysis buttons (integrated without changing existing ones)
        chart_btn = tk.Button(
            right_inner,
            text="Show Time Chart",
            command=self.show_algorithm_chart,
            font=("Segoe UI", 10, "bold"),
            bg="#4caf50",
            fg="white",
            activebackground="#66bb6a",
            activeforeground="white",
            padx=16,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
        )
        chart_btn.pack(pady=(4, 4), fill=tk.X)
        chart_btn.configure(
            highlightthickness=1,
            highlightbackground="#2e7d32",
        )

        analysis_btn = tk.Button(
            right_inner,
            text="Save Complexity Report",
            command=self.save_complexity_analysis_report,
            font=("Segoe UI", 10, "bold"),
            bg="#9c27b0",
            fg="white",
            activebackground="#ba68c8",
            activeforeground="white",
            padx=16,
            pady=6,
            cursor="hand2",
            relief=tk.FLAT,
        )
        analysis_btn.pack(pady=(2, 4), fill=tk.X)
        analysis_btn.configure(
            highlightthickness=1,
            highlightbackground="#6a1b9a",
        )

        # Bottom: exit
        exit_btn = tk.Button(
            grass_strip,
            text="Exit Game",
            command=self.root.quit,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_dirt,
            fg="white",
            activebackground="#c88c52",
            activeforeground="white",
            padx=16,
            pady=5,
            cursor="hand2",
            relief=tk.FLAT,
        )
        exit_btn.pack(side=tk.RIGHT, padx=20, pady=14)
        exit_btn.configure(
            highlightthickness=1,
            highlightbackground="#8b5a2b",
        )

        tk.Label(
            grass_strip,
            text="Snake & Ladder Problem • Cozy Edition",
            font=("Segoe UI", 9, "italic"),
            bg=self.color_grass,
            fg="#2f4f2f",
        ).pack(side=tk.LEFT, padx=20)

    
    #  Board generation & algorithms
    
    def start_new_round(self):
        try:
            N = int(self.size_var.get())
        except Exception:
            messagebox.showerror(
                "Invalid Input", "Board size N must be an integer."
            )
            return

        if not (6 <= N <= 12):
            messagebox.showerror(
                "Invalid Board Size", "N must be between 6 and 12."
            )
            return

        self.board_size = N
        self.generate_random_board(N)
        self.compute_min_throws()
        self.build_round_ui()

    def generate_random_board(self, N: int):
        total_cells = N * N
        desired_count = max(1, N - 2)

        self.snakes.clear()
        self.ladders.clear()

        used_cells = {1, total_cells}

        # Ladders
        attempts = 0
        while len(self.ladders) < desired_count and attempts < 1000:
            attempts += 1
            start = random.randint(2, total_cells - 2)
            end = random.randint(start + 1, min(total_cells - 1, start + N * 2))

            if (
                start < end
                and start not in used_cells
                and end not in used_cells
                and start not in self.snakes
                and end not in self.snakes.values()
                and start not in self.ladders
                and end not in self.ladders.values()
            ):
                self.ladders[start] = end
                used_cells.add(start)
                used_cells.add(end)

        # Snakes
        attempts = 0
        while len(self.snakes) < desired_count and attempts < 1000:
            attempts += 1
            start = random.randint(3, total_cells - 1)
            end = random.randint(2, start - 1)

            if (
                start > end
                and start not in used_cells
                and end not in used_cells
                and start not in self.ladders
                and end not in self.ladders.values()
                and start not in self.snakes
                and end not in self.snakes.values()
            ):
                self.snakes[start] = end
                used_cells.add(start)
                used_cells.add(end)

        if len(self.ladders) < desired_count or len(self.snakes) < desired_count:
            print(
                f"Warning: could not generate full N-2 snakes/ladders for N={N}. "
                f"Got {len(self.ladders)} ladders, {len(self.snakes)} snakes."
            )

    def _build_moves_array(self, total_cells: int) -> list[int]:
        moves = [-1] * (total_cells + 1)
        for s, e in self.ladders.items():
            if 1 <= s <= total_cells and 1 <= e <= total_cells:
                moves[s] = e
        for s, e in self.snakes.items():
            if 1 <= s <= total_cells and 1 <= e <= total_cells:
                moves[s] = e
        return moves

    def bfs_min_throws(self, total_cells: int) -> int:
        """
        Breadth-First Search to find minimum throws.
        Time Complexity: O(V + E) = O(V) where V = total_cells = N², E ≤ 6V
        Space Complexity: O(V) for visited array and queue
        """
        if total_cells < 1:
            raise ValueError("total_cells must be >= 1")

        moves = self._build_moves_array(total_cells)
        visited = [False] * (total_cells + 1)
        queue: list[tuple[int, int]] = []

        queue.append((1, 0))
        visited[1] = True

        while queue:
            pos, dist = queue.pop(0)
            if pos == total_cells:
                return dist

            for dice in range(1, 7):
                nxt = pos + dice
                if nxt <= total_cells:
                    if moves[nxt] != -1:
                        nxt = moves[nxt]
                    if not visited[nxt]:
                        visited[nxt] = True
                        queue.append((nxt, dist + 1))

        return -1

    def dp_min_throws(self, total_cells: int) -> int:
        """
        Dynamic Programming to compute minimum throws.
        Time Complexity: O(6V) = O(V) where V = total_cells = N²
        Space Complexity: O(V) for dp array
        """
        if total_cells < 1:
            raise ValueError("total_cells must be >= 1")

        moves = self._build_moves_array(total_cells)
        INF = float("inf")
        dp = [INF] * (total_cells + 1)
        dp[1] = 0

        for i in range(1, total_cells + 1):
            if dp[i] == INF:
                continue
            for dice in range(1, 7):
                nxt = i + dice
                if nxt <= total_cells:
                    dest = moves[nxt] if moves[nxt] != -1 else nxt
                    dp[dest] = min(dp[dest], dp[i] + 1)

        return dp[total_cells] if dp[total_cells] != float("inf") else -1

    def compute_min_throws(self):
        total_cells = self.board_size * self.board_size

        start = time.time()
        bfs_ans = self.bfs_min_throws(total_cells)
        bfs_time = (time.time() - start) * 1000

        start = time.time()
        dp_ans = self.dp_min_throws(total_cells)
        dp_time = (time.time() - start) * 1000

        if bfs_ans != dp_ans:
            print(
                f"WARNING: BFS ({bfs_ans}) != DP ({dp_ans}). "
                f"Using BFS result as ground truth."
            )

        self.min_throws_answer = bfs_ans
        self.algorithm_times = {"bfs": bfs_time, "dp": dp_time}

    
    #  UI for one problem round
    
    def build_round_ui(self):
        self.clear_window()
        self._snake_wiggle_phase = 0

        bg = tk.Frame(self.root, bg=self.color_sky)
        bg.pack(fill=tk.BOTH, expand=True)

        grass_height = max(int(self.window_height * 0.08), 60)
        grass = tk.Frame(bg, bg=self.color_grass, height=grass_height)
        grass.pack(side=tk.BOTTOM, fill=tk.X)

        top_frame = tk.Frame(bg, bg=self.color_sky)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=18, pady=12)

        # Layout: LEFT narrow panel with all controls, RIGHT huge board
        main = tk.Frame(top_frame, bg=self.color_sky)
        main.pack(fill=tk.BOTH, expand=True)

        # LEFT PANEL

        left_outer = tk.Frame(
            main,
            bg=self.color_wood_dark,
            bd=2,
            relief=tk.RIDGE,
            width=int(self.window_width * 0.22),
        )
        left_outer.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=4)

        left = tk.Frame(left_outer, bg=self.color_panel_alt, padx=12, pady=10)
        left.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(
            left,
            text=f"Board {self.board_size}×{self.board_size}",
            font=("Segoe UI", 14, "bold"),
            bg=self.color_panel_alt,
            fg=self.color_text,
        )
        title.pack(pady=(2, 2))

        sub = tk.Label(
            left,
            text=f"Cells 1 – {self.board_size**2}",
            font=("Segoe UI", 10),
            bg=self.color_panel_alt,
            fg=self.color_text,
        )
        sub.pack(pady=(0, 6))

        tk.Label(
            left,
            text="Minimum Throws?",
            font=("Segoe UI", 13, "bold"),
            bg=self.color_panel_alt,
            fg=self.color_text,
        ).pack(pady=(4, 4))

        qt = tk.Label(
            left,
            text=(
                f"From cell 1 to cell {self.board_size**2},\n"
                f"what is the smallest number of dice throws\n"
                f"(1–6) needed to reach the final cell?"
            ),
            font=("Segoe UI", 10),
            bg=self.color_panel_alt,
            fg=self.color_text,
            justify=tk.LEFT,
        )
        qt.pack(pady=(0, 8), anchor=tk.W)

        self.current_options = self.generate_multiple_choice(
            self.min_throws_answer
        )
        random.shuffle(self.current_options)
        self.correct_option_index = self.current_options.index(
            self.min_throws_answer
        )

        self.option_var = tk.IntVar(value=-1)

        for idx, opt in enumerate(self.current_options):
            rb = tk.Radiobutton(
                left,
                text=str(opt),
                variable=self.option_var,
                value=idx,
                font=("Segoe UI", 11),
                bg=self.color_panel_alt,
                fg=self.color_text,
                selectcolor="#f2ddc6",
                activebackground=self.color_panel_alt,
                activeforeground=self.color_accent2,
                anchor=tk.W,
                padx=6,
            )
            rb.pack(pady=1, fill=tk.X)

        name_frm = tk.Frame(left, bg=self.color_panel_alt)
        name_frm.pack(pady=(10, 4), anchor=tk.W, fill=tk.X)

        tk.Label(
            name_frm,
            text="Your Name:",
            font=("Segoe UI", 10, "bold"),
            bg=self.color_panel_alt,
            fg=self.color_text,
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.player_name_entry = tk.Entry(
            name_frm,
            font=("Segoe UI", 10),
            width=14,
            bg="#fffaf3",
            fg=self.color_text,
            insertbackground=self.color_text,
        )
        self.player_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        submit_btn = tk.Button(
            left,
            text="Submit Answer",
            command=self.check_answer,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_accent,
            fg="white",
            activebackground="#f8c15a",
            activeforeground="white",
            padx=10,
            pady=5,
            cursor="hand2",
            relief=tk.FLAT,
        )
        submit_btn.pack(pady=(10, 4), fill=tk.X)
        submit_btn.configure(
            highlightthickness=1,
            highlightbackground="#b07b27",
        )

        back_btn = tk.Button(
            left,
            text="Back to Main Menu",
            command=self.build_main_menu,
            font=("Segoe UI", 9, "bold"),
            bg=self.color_dirt,
            fg="white",
            activebackground="#c88c52",
            activeforeground="white",
            padx=10,
            pady=4,
            cursor="hand2",
            relief=tk.FLAT,
        )
        back_btn.pack(pady=(2, 8), fill=tk.X)
        back_btn.configure(
            highlightthickness=1,
            highlightbackground="#8b5a2b",
        )

        info_box = tk.Frame(left, bg="#f3e4d4", bd=1, relief=tk.SUNKEN)
        info_box.pack(pady=(4, 4), fill=tk.X)

        tk.Label(
            info_box,
            text=(
                f"Snakes: {len(self.snakes)}   "
                f"Ladders: {len(self.ladders)}"
            ),
            font=("Segoe UI", 9),
            bg="#f3e4d4",
            fg=self.color_text,
        ).pack(pady=(2, 0))

        tk.Label(
            info_box,
            text="Algorithm Performance",
            font=("Segoe UI", 9, "bold"),
            bg="#f3e4d4",
            fg=self.color_text,
        ).pack(pady=(2, 0))

        tk.Label(
            info_box,
            text=f"BFS: {self.algorithm_times['bfs']:.2f} ms",
            font=("Segoe UI", 8),
            bg="#f3e4d4",
            fg="#3a9c4f",
        ).pack()

        tk.Label(
            info_box,
            text=f"DP : {self.algorithm_times['dp']:.2f} ms",
            font=("Segoe UI", 8),
            bg="#f3e4d4",
            fg="#3b7bbf",
        ).pack(pady=(0, 2))

        # RIGHT: HUGE BOARD 

        board_outer = tk.Frame(
            main,
            bg=self.color_wood_dark,
            bd=2,
            relief=tk.RIDGE,
        )
        board_outer.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True,
            padx=(10, 0),
            pady=4,
        )

        board_frame = tk.Frame(board_outer, bg=self.color_panel, padx=6, pady=6)
        board_frame.pack(fill=tk.BOTH, expand=True)

        canvas_w, canvas_h = self.get_board_canvas_size()
        canvas = tk.Canvas(
            board_frame,
            width=canvas_w,
            height=canvas_h,
            bg="#c4f0ff",
            highlightthickness=0,
        )
        canvas.pack(padx=4, pady=4)

        cell_size = min(canvas_w, canvas_h) / (self.board_size + 0.2)
        offset_x = (canvas_w - self.board_size * cell_size) / 2
        offset_y = (canvas_h - self.board_size * cell_size) / 2

        canvas.create_rectangle(
            offset_x - 10,
            offset_y - 10,
            offset_x + self.board_size * cell_size + 10,
            offset_y + self.board_size * cell_size + 10,
            fill="#f9fdfd",
            outline=self.color_wood_dark,
            width=2,
        )

        def cell_number(row: int, col: int) -> int:
            if row % 2 == 0:
                return (self.board_size - row - 1) * self.board_size + col + 1
            else:
                return (
                    (self.board_size - row - 1) * self.board_size
                    + (self.board_size - col)
                )

        tile_normal = tile_snake = tile_ladder = None
        if PIL_AVAILABLE:
            size = (int(cell_size), int(cell_size))
            tile_normal = self.get_tk_image("tile_normal.png", size)
            tile_snake = self.get_tk_image("tile_snake.png", size)
            tile_ladder = self.get_tk_image("tile_ladder.png", size)

        self._board_cells_to_reveal = []

        for row in range(self.board_size):
            row_ids = []
            for col in range(self.board_size):
                num = cell_number(row, col)
                x1 = offset_x + col * cell_size
                y1 = offset_y + row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                if num in self.snakes:
                    base_fill = "#fbd5d0"
                    img = tile_snake
                elif num in self.ladders:
                    base_fill = "#d7f5c7"
                    img = tile_ladder
                else:
                    base_fill = "#fdf5e7" if (row + col) % 2 == 0 else "#f3e3ce"
                    img = tile_normal

                if img is not None:
                    tile = canvas.create_image(
                        x1, y1, anchor=tk.NW, image=img, state="hidden"
                    )
                    rect_id = None
                else:
                    rect_id = canvas.create_rectangle(
                        x1, y1, x2, y2, fill=self.color_panel, outline="#e0c9a9", width=1
                    )
                    tile = None

                text_color = (
                    self.color_accent2
                    if num in self.snakes
                    else "#3a9c4f"
                    if num in self.ladders
                    else "#7b5b3e"
                )
                text_id = canvas.create_text(
                    x1 + cell_size / 2,
                    y1 + cell_size / 2,
                    text=str(num),
                    font=("Segoe UI", max(int(cell_size * 0.24), 11), "bold"),
                    fill=text_color,
                    state="hidden",
                )
                row_ids.append((rect_id, tile, text_id, base_fill))
            self._board_cells_to_reveal.append(row_ids)

        def reveal_row(row_idx=0):
            if row_idx >= len(self._board_cells_to_reveal):
                self._animate_snakes(canvas, cell_size, offset_x, offset_y)
                return
            for rect_id, tile, text_id, fill in self._board_cells_to_reveal[row_idx]:
                if tile is not None:
                    canvas.itemconfig(tile, state="normal")
                else:
                    canvas.itemconfig(rect_id, fill=fill)
                canvas.itemconfig(text_id, state="normal")
            self.root.after(60, lambda: reveal_row(row_idx + 1))

        reveal_row(0)

        def center_for_cell(num: int) -> tuple[float, float]:
            row = self.board_size - ((num - 1) // self.board_size) - 1
            col = (num - 1) % self.board_size
            if row % 2 != 0:
                col = self.board_size - 1 - col
            cx = offset_x + col * cell_size + cell_size / 2
            cy = offset_y + row * cell_size + cell_size / 2
            return cx, cy

        self._snake_lines = []

        ladder_img = None
        if PIL_AVAILABLE:
            ladder_img = self.get_tk_image(
                "ladder.png",
                (int(cell_size * 0.4), int(cell_size * 0.8)),
            )

        for s, e in self.ladders.items():
            sx, sy = center_for_cell(s)
            ex, ey = center_for_cell(e)
            canvas.create_line(
                sx,
                sy,
                ex,
                ey,
                fill=self.color_dirt,
                width=max(cell_size * 0.05, 3),
            )
            if ladder_img:
                canvas.create_image(
                    sx, sy - cell_size * 0.4, image=ladder_img
                )
                canvas.image = ladder_img
            else:
                canvas.create_text(
                    sx,
                    sy - cell_size / 3,
                    text="🪜",
                    font=("Segoe UI", max(int(cell_size * 0.22), 10)),
                )

        snake_head_img = None
        if PIL_AVAILABLE:
            snake_head_img = self.get_tk_image(
                "snake_head.png",
                (int(cell_size * 0.6), int(cell_size * 0.6)),
            )

        for s, e in self.snakes.items():
            sx, sy = center_for_cell(s)
            ex, ey = center_for_cell(e)
            mx = (sx + ex) / 2
            my = (sy + ey) / 2 - cell_size * 0.7
            snake_id = canvas.create_line(
                sx,
                sy,
                mx,
                my,
                ex,
                ey,
                fill="#62c665",
                width=max(cell_size * 0.08, 4),
                smooth=True,
            )
            self._snake_lines.append((snake_id, sx, sy, mx, my, ex, ey))

            if snake_head_img:
                canvas.create_image(
                    sx - cell_size * 0.3,
                    sy - cell_size * 0.3,
                    image=snake_head_img,
                    anchor=tk.NW,
                )
                canvas.image = snake_head_img
            else:
                canvas.create_oval(
                    sx - 9,
                    sy - 9,
                    sx + 9,
                    sy + 9,
                    fill="#f46e6e",
                    outline="#c85252",
                    width=2,
                )
                canvas.create_text(
                    sx,
                    sy - cell_size / 3,
                    text="🐍",
                    font=("Segoe UI Emoji", max(int(cell_size * 0.2), 10)),
                )

    def _animate_snakes(self, canvas: tk.Canvas, cell_size, ox, oy):
        """Gentle wiggle animation for snakes."""

        def step():
            try:
                self._snake_wiggle_phase += 1
                phase = self._snake_wiggle_phase
                for (line_id, sx, sy, mx, my, ex, ey) in self._snake_lines:
                    offset = math.sin(phase / 10.0) * (cell_size * 0.15)
                    canvas.coords(
                        line_id,
                        sx,
                        sy,
                        mx + offset,
                        my,
                        ex,
                        ey,
                    )
                self.root.after(100, step)
            except tk.TclError:
                return

        step()

    
    #  Answer / result
    
    def generate_multiple_choice(self, correct_answer: int) -> list[int]:
        if correct_answer is None or correct_answer <= 0:
            return [3, 4, 5]

        options = {correct_answer}
        theoretical_min = (self.board_size * self.board_size - 1 + 5) // 6

        options.add(correct_answer + random.randint(1, 3))
        lower = max(theoretical_min, correct_answer - random.randint(1, 3))
        options.add(lower)

        options = sorted(options)
        if len(options) > 3:
            options = options[:3]
        while len(options) < 3:
            options.append(options[-1] + 1)
        return options

    def check_answer(self):
        name = self.player_name_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Name Required", "Please enter your name."
            )
            return

        idx = self.option_var.get()
        if idx == -1:
            messagebox.showwarning(
                "Answer Required", "Please select one of the options."
            )
            return

        try:
            user_answer = self.current_options[idx]
        except Exception:
            messagebox.showerror(
                "Internal Error", "Could not read your selected option."
            )
            return

        correct_index = self.correct_option_index
        is_correct = idx == correct_index

        self.db.save_result(
            player_name=name,
            board_size=self.board_size,
            correct_answer=self.min_throws_answer,
            user_answer=user_answer,
            is_correct=is_correct,
            bfs_time_ms=self.algorithm_times["bfs"],
            dp_time_ms=self.algorithm_times["dp"],
        )

        self.show_result_window(name, user_answer, is_correct)

    def show_result_window(
        self, player_name: str, user_answer: int, is_correct: bool
    ):
        win = tk.Toplevel(self.root)
        win.title("Game Result")

        w = max(int(self.window_width * 0.28), 360)
        h = max(int(self.window_height * 0.26), 250)
        win.geometry(f"{w}x{h}")
        win.configure(bg=self.color_sky)
        win.resizable(False, False)

        outer = tk.Frame(win, bg=self.color_wood_dark, bd=2, relief=tk.RIDGE)
        outer.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        panel = tk.Frame(outer, bg=self.color_panel, padx=14, pady=12)
        panel.pack(expand=True, fill=tk.BOTH)

        title_text = "Great Job!" if is_correct else "Nice Try!"
        title_color = self.color_accent if is_correct else self.color_accent2

        title = tk.Label(
            panel,
            text=title_text,
            font=("Segoe UI", 16, "bold"),
            bg=self.color_panel,
            fg=title_color,
        )
        title.pack(pady=(4, 6))

        msg = (
            f"Player: {player_name}\n\n"
            f"Your answer: {user_answer}\n"
            f"Correct answer: {self.min_throws_answer}"
        )
        if not is_correct:
            msg += "\n\nYou can always try another cozy board!"

        tk.Label(
            panel,
            text=msg,
            font=("Segoe UI", 10),
            bg=self.color_panel,
            fg=self.color_text,
            justify=tk.LEFT,
        ).pack(pady=4, padx=4, anchor=tk.W)

        tk.Label(
            panel,
            text=(
                f"BFS time: {self.algorithm_times['bfs']:.2f} ms\n"
                f"DP time : {self.algorithm_times['dp']:.2f} ms"
            ),
            font=("Segoe UI", 9),
            bg=self.color_panel,
            fg="#3b7bbf",
            justify=tk.LEFT,
        ).pack(pady=(3, 8))

        btn_frame = tk.Frame(panel, bg=self.color_panel)
        btn_frame.pack(pady=(2, 4))

        def new_round_and_close():
            win.destroy()
            self.start_new_round()

        new_btn = tk.Button(
            btn_frame,
            text="New Round",
            command=new_round_and_close,
            font=("Segoe UI", 9, "bold"),
            bg=self.color_accent,
            fg="white",
            activebackground="#f8c15a",
            activeforeground="white",
            padx=12,
            pady=4,
            cursor="hand2",
            relief=tk.FLAT,
        )
        new_btn.pack(side=tk.LEFT, padx=4)
        new_btn.configure(
            highlightthickness=1,
            highlightbackground="#b07b27",
        )

        def back_menu_and_close():
            win.destroy()
            self.build_main_menu()

        back_btn = tk.Button(
            btn_frame,
            text="Main Menu",
            command=back_menu_and_close,
            font=("Segoe UI", 9, "bold"),
            bg=self.color_dirt,
            fg="white",
            activebackground="#c88c52",
            activeforeground="white",
            padx=12,
            pady=4,
            cursor="hand2",
            relief=tk.FLAT,
        )
        back_btn.pack(side=tk.LEFT, padx=4)
        back_btn.configure(
            highlightthickness=1,
            highlightbackground="#8b5a2b",
        )

    
    #  Stats screen
    
    def show_algorithm_stats(self):
        stats = self.db.fetch_stats_by_board_size()
        win = tk.Toplevel(self.root)
        win.title("Algorithm Performance")

        w = max(int(self.window_width * 0.55), 640)
        h = max(int(self.window_height * 0.5), 420)
        win.geometry(f"{w}x{h}")
        win.configure(bg=self.color_sky)

        outer = tk.Frame(win, bg=self.color_wood_dark, bd=3, relief=tk.RIDGE)
        outer.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        panel = tk.Frame(outer, bg=self.color_panel, padx=10, pady=10)
        panel.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            panel,
            text="Algorithm Performance",
            font=("Segoe UI", 18, "bold"),
            bg=self.color_panel,
            fg=self.color_text,
        ).pack(pady=(6, 6))

        if not stats:
            tk.Label(
                panel,
                text="No data yet.\nPlay a few rounds to see stats!",
                font=("Segoe UI", 12),
                bg=self.color_panel,
                fg=self.color_text,
            ).pack(pady=40)
        else:
            frame = tk.Frame(panel, bg=self.color_panel)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)

            tree_scroll_y = tk.Scrollbar(frame)
            tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

            tree = ttk.Treeview(
                frame,
                yscrollcommand=tree_scroll_y.set,
                selectmode="browse",
                height=10,
            )
            tree_scroll_y.config(command=tree.yview)

            tree["columns"] = (
                "Board",
                "Games",
                "Correct",
                "Avg BFS (ms)",
                "Avg DP (ms)",
            )
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("Board", anchor=tk.CENTER, width=90)
            tree.column("Games", anchor=tk.CENTER, width=80)
            tree.column("Correct", anchor=tk.CENTER, width=130)
            tree.column("Avg BFS (ms)", anchor=tk.CENTER, width=130)
            tree.column("Avg DP (ms)", anchor=tk.CENTER, width=130)

            tree.heading("#0", text="", anchor=tk.W)
            tree.heading("Board", text="Board", anchor=tk.CENTER)
            tree.heading("Games", text="Games", anchor=tk.CENTER)
            tree.heading("Correct", text="Correct", anchor=tk.CENTER)
            tree.heading("Avg BFS (ms)", text="Avg BFS (ms)", anchor=tk.CENTER)
            tree.heading("Avg DP (ms)", text="Avg DP (ms)", anchor=tk.CENTER)

            for i, row in enumerate(stats):
                board_size, total_games, correct, avg_bfs, avg_dp = row
                accuracy = (
                    (correct / total_games) * 100 if total_games else 0
                )
                tree.insert(
                    "",
                    "end",
                    iid=i,
                    values=(
                        f"{board_size}×{board_size}",
                        total_games,
                        f"{correct} ({accuracy:.1f}%)",
                        f"{avg_bfs:.2f}",
                        f"{avg_dp:.2f}",
                    ),
                )

            tree.pack(fill=tk.BOTH, expand=True)

            style = ttk.Style()
            style.theme_use("clam")
            style.configure(
                "Treeview",
                background="#f7f1e8",
                foreground=self.color_text,
                fieldbackground="#f7f1e8",
                borderwidth=0,
            )
            style.map("Treeview", background=[("selected", "#e0d2c0")])

        close_btn = tk.Button(
            panel,
            text="Close",
            command=win.destroy,
            font=("Segoe UI", 10, "bold"),
            bg=self.color_dirt,
            fg="white",
            activebackground="#c88c52",
            activeforeground="white",
            padx=18,
            pady=4,
            cursor="hand2",
            relief=tk.FLAT,
        )
        close_btn.pack(pady=(6, 4))
        close_btn.configure(
            highlightthickness=1,
            highlightbackground="#8b5a2b",
        )

    
    #  NEW: Chart using DB data (Part I integration)
    
    def show_algorithm_chart(self):
        """
        Use matplotlib to create:
        1) Line chart of BFS/DP times per game round.
        2) Bar chart of average BFS/DP time.
        Also print summary statistics to console.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    id, 
                    bfs_time_ms, 
                    dp_time_ms, 
                    board_size 
                FROM min_throws_game 
                ORDER BY id
                """
            )
            data = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load data from database:\n{e}",
            )
            return

        if not data:
            messagebox.showinfo(
                "No Data",
                "No game rounds found in the database.\n"
                "Play some rounds first to generate data.",
            )
            return

        # Extract data
        game_rounds = [row[0] for row in data]
        bfs_times = [row[1] for row in data]
        dp_times = [row[2] for row in data]
        board_sizes = [row[3] for row in data]

        # Create the chart
        plt.figure(figsize=(12, 6))

        # Plot BFS and DP times
        plt.subplot(2, 1, 1)
        plt.plot(
            game_rounds,
            bfs_times,
            "o-",
            label="BFS Time (ms)",
            color="blue",
            markersize=6,
        )
        plt.plot(
            game_rounds,
            dp_times,
            "s-",
            label="DP Time (ms)",
            color="green",
            markersize=6,
        )

        plt.title(
            f"Algorithm Execution Time Comparison ({len(data)} Game Rounds)"
        )
        plt.xlabel("Game Round (Row ID)")
        plt.ylabel("Time (milliseconds)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Add board size information
        for round_num, bfs_t, dp_t, size in zip(
            game_rounds, bfs_times, dp_times, board_sizes
        ):
            plt.annotate(
                f"{size}×{size}",
                (round_num, max(bfs_t, dp_t)),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
                fontsize=8,
                alpha=0.7,
            )

        # Bar chart of average times
        plt.subplot(2, 1, 2)
        algorithms = ["BFS", "DP"]
        average_times = [np.mean(bfs_times), np.mean(dp_times)]

        bars = plt.bar(
            algorithms,
            average_times,
            color=["blue", "green"],
            alpha=0.6,
            width=0.5,
        )

        plt.title("Average Execution Time Comparison")
        plt.ylabel("Time (milliseconds)")

        # Add values on top of bars
        for bar, value in zip(bars, average_times):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.3f} ms",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.show()

        # Print summary statistics in console
        print("\n" + "=" * 50)
        print("SUMMARY STATISTICS")
        print("=" * 50)
        print(f"Total Game Rounds: {len(data)}")
        print(
            "Board Sizes Range: "
            f"{min(board_sizes)}×{min(board_sizes)} to "
            f"{max(board_sizes)}×{max(board_sizes)}"
        )
        print("\nBFS Algorithm:")
        print(f"  Average Time: {np.mean(bfs_times):.4f} ms")
        print(f"  Min Time: {min(bfs_times):.4f} ms")
        print(f"  Max Time: {max(bfs_times):.4f} ms")
        print(f"  Standard Deviation: {np.std(bfs_times):.4f} ms")

        print("\nDP Algorithm:")
        print(f"  Average Time: {np.mean(dp_times):.4f} ms")
        print(f"  Min Time: {min(dp_times):.4f} ms")
        print(f"  Max Time: {max(dp_times):.4f} ms")
        print(f"  Standard Deviation: {np.std(dp_times):.4f} ms")

        print("\n" + "=" * 50)
        print("OBSERVATIONS FROM DATA:")
        print("=" * 50)
        print("1. Both algorithms are extremely fast (< 0.15 ms)")
        print("2. BFS is consistently faster than DP in most rounds")
        print("3. Execution time tends to increase with board size")
        print("4. DP often shows more variability in execution time")

    
    #  NEW: Complexity analysis report (Part II integration)
    
    def save_complexity_analysis_report(self):
        """
        Generate a detailed complexity and empirical analysis report
        and save it to 'algorithm_complexity_analysis.txt'.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    id, 
                    bfs_time_ms, 
                    dp_time_ms, 
                    board_size 
                FROM min_throws_game 
                ORDER BY id
                """
            )
            data = cursor.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not load data from database:\n{e}",
            )
            return

        if not data:
            messagebox.showinfo(
                "No Data",
                "No game rounds found in the database.\n"
                "Play some rounds first to generate data.",
            )
            return

        game_rounds = [row[0] for row in data]
        bfs_times = [row[1] for row in data]
        dp_times = [row[2] for row in data]
        board_sizes = [row[3] for row in data]

        avg_bfs = np.mean(bfs_times)
        avg_dp = np.mean(dp_times)

        # Save analysis to file (based closely on your template)
        try:
            with open("algorithm_complexity_analysis.txt", "w") as f:
                f.write("ALGORITHM COMPLEXITY ANALYSIS REPORT\n")
                f.write("=" * 50 + "\n\n")

                f.write("DATABASE SAMPLE (First 5 rows):\n")
                for i in range(min(5, len(data))):
                    f.write(
                        f"Round {data[i][0]}: Board {data[i][3]}×{data[i][3]}, "
                        f"BFS={data[i][1]:.4f}ms, DP={data[i][2]:.4f}ms\n"
                    )

                f.write("\n" + "=" * 50 + "\n")
                f.write("TIME COMPLEXITY ANALYSIS\n")
                f.write("=" * 50 + "\n")

                f.write("\n1. BFS ALGORITHM:\n")
                f.write("   - Code Analysis: Visits each cell once in worst case\n")
                f.write("   - Each cell explores up to 6 edges (dice rolls)\n")
                f.write("   - Complexity: O(6V) = O(V) = O(N²)\n")
                f.write("   - Actual: V = N² cells\n")

                f.write("\n2. DP ALGORITHM:\n")
                f.write(
                    "   - Code Analysis: DP table of size V, each cell updates 6 times\n"
                )
                f.write("   - Complexity: O(6V) = O(V) = O(N²)\n")
                f.write("   - Processes ALL cells regardless of solution\n")

                f.write("\n" + "=" * 50 + "\n")
                f.write("EMPIRICAL FINDINGS FROM DATA\n")
                f.write("=" * 50 + "\n")

                f.write(f"\nTotal Game Rounds: {len(data)}\n")
                f.write(
                    f"Board Sizes Range: {min(board_sizes)}×{min(board_sizes)} "
                    f"to {max(board_sizes)}×{max(board_sizes)}\n"
                )

                f.write(f"\nAverage BFS Time: {avg_bfs:.4f} ms\n")
                f.write(f"Average DP Time:  {avg_dp:.4f} ms\n")
                if avg_dp != 0:
                    f.write(
                        f"BFS/DP Ratio:     {avg_bfs / avg_dp:.2f}\n"
                    )
                else:
                    f.write("BFS/DP Ratio:     N/A (DP avg time is 0)\n")

                f.write("\nTrend with Board Size:\n")
                sizes = sorted(set(board_sizes))
                for size in sizes:
                    bfs_avg = np.mean(
                        [
                            bfs
                            for bfs, s in zip(bfs_times, board_sizes)
                            if s == size
                        ]
                    )
                    dp_avg = np.mean(
                        [
                            dp
                            for dp, s in zip(dp_times, board_sizes)
                            if s == size
                        ]
                    )
                    f.write(
                        f"  {size}×{size}: BFS={bfs_avg:.4f}ms, "
                        f"DP={dp_avg:.4f}ms\n"
                    )

                f.write("\n" + "=" * 50 + "\n")
                f.write("OBSERVATIONS:\n")
                f.write("=" * 50 + "\n")
                f.write(
                    "1. Both algorithms are extremely fast for board sizes 6–12.\n"
                )
                f.write(
                    "2. BFS often appears slightly faster in practice, "
                    "since it can terminate once the target is reached.\n"
                )
                f.write(
                    "3. DP processes all cells regardless of when the "
                    "shortest path is found, which can make it a bit slower.\n"
                )
                f.write(
                    "4. Measured execution times tend to grow as board size "
                    "increases, which is consistent with O(N²) complexity.\n"
                )
                f.write(
                    "5. For interactive game-sized boards, both algorithms "
                    "are effectively instantaneous.\n"
                )

            messagebox.showinfo(
                "Report Saved",
                "Complexity analysis saved to:\n"
                "algorithm_complexity_analysis.txt",
            )
            print("Analysis saved to 'algorithm_complexity_analysis.txt'")
        except Exception as e:
            messagebox.showerror(
                "File Error",
                f"Could not save analysis report:\n{e}",
            )



#  UNIT TESTS

class TestSnakeAndLadderProblemAlgorithms(unittest.TestCase):
    def setUp(self):
        self.obj = SnakeAndLadderProblemGame.__new__(
            SnakeAndLadderProblemGame
        )
        self.obj.board_size = 10
        self.obj.snakes = {}
        self.obj.ladders = {}

    def test_bfs_basic_no_snakes_ladders(self):
        total_cells = 100
        self.obj.snakes = {}
        self.obj.ladders = {}
        res = self.obj.bfs_min_throws(total_cells)
        self.assertEqual(res, 17)

    def test_dp_basic_no_snakes_ladders(self):
        total_cells = 100
        self.obj.snakes = {}
        self.obj.ladders = {}
        bfs = self.obj.bfs_min_throws(total_cells)
        dp = self.obj.dp_min_throws(total_cells)
        self.assertEqual(dp, bfs)

    def test_bfs_with_ladders_improves(self):
        total_cells = 100
        self.obj.snakes = {}
        self.obj.ladders = {}
        base = self.obj.bfs_min_throws(total_cells)

        self.obj.ladders = {1: 50}
        res = self.obj.bfs_min_throws(total_cells)
        self.assertLessEqual(res, base)

    def test_snakes_ladders_generation_counts(self):
        self.obj.generate_random_board = SnakeAndLadderProblemGame.generate_random_board.__get__(
            self.obj
        )
        for N in range(6, 13):
            self.obj.generate_random_board(N)
            self.assertGreaterEqual(len(self.obj.ladders), 1)
            self.assertGreaterEqual(len(self.obj.snakes), 1)

    def test_bfs_dp_consistency_random_board(self):
        self.obj.generate_random_board = SnakeAndLadderProblemGame.generate_random_board.__get__(
            self.obj
        )
        self.obj.generate_random_board(8)
        total_cells = 64
        bfs = self.obj.bfs_min_throws(total_cells)
        dp = self.obj.dp_min_throws(total_cells)
        self.assertEqual(bfs, dp)


def run_unit_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestSnakeAndLadderProblemAlgorithms
    )
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


def main():
    root = tk.Tk()
    game = SnakeAndLadderProblemGame(root)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="Run Unit Tests (Console)", command=run_unit_tests)

    root.mainloop()


if __name__ == "__main__":
    main()