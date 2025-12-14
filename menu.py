import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# Function to run python files
def run_game(file_name):
    try:
        subprocess.Popen([sys.executable, file_name])
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open {file_name}\n{e}")

# Main window
root = tk.Tk()
root.title("🎮 Game Hub")
root.geometry("500x600")
root.resizable(False, False)
root.configure(bg="#1e1e2f")

# Title
title = tk.Label(
    root,
    text="🎮 PYTHON GAME HUB",
    font=("Arial", 22, "bold"),
    fg="#ffffff",
    bg="#1e1e2f"
)
title.pack(pady=30)

# Button style
def create_button(text, file):
    return tk.Button(
        root,
        text=text,
        font=("Arial", 14, "bold"),
        width=30,
        height=2,
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        bd=0,
        cursor="hand2",
        command=lambda: run_game(file)
    )

# Buttons
btn1 = create_button("🐍 Snake and Ladder", "snake.py")
btn2 = create_button("🚦 Traffic Simulation", "traffic.py")
btn3 = create_button("🧭 Traveling Salesman Problem", "tsp.py")
btn4 = create_button("🗼 Tower of Hanoi", "th.py")
btn5 = create_button("♟ Eight Queens Puzzle", "queen.py")

btn1.pack(pady=10)
btn2.pack(pady=10)
btn3.pack(pady=10)
btn4.pack(pady=10)
btn5.pack(pady=10)

# Exit button
exit_btn = tk.Button(
    root,
    text="❌ Exit",
    font=("Arial", 12, "bold"),
    width=15,
    bg="#e74c3c",
    fg="white",
    bd=0,
    cursor="hand2",
    command=root.destroy
)
exit_btn.pack(pady=30)

# Footer
footer = tk.Label(
    root,
    text="Developed using Python 🐍",
    font=("Arial", 10),
    fg="#aaaaaa",
    bg="#1e1e2f"
)
footer.pack(side="bottom", pady=10)

root.mainloop()
