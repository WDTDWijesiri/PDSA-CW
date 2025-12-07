# 🎮 Computer Science Game Collection

A comprehensive collection of interactive games demonstrating various computer science algorithms.

## 📁 Project Structure

```
game_collection/
│
├── main.py                     # Main entry point - run this file
├── main_menu.py               # Main menu UI
├── database.py                # Database management
├── instructions.py            # Help and instructions dialog
│
├── traffic_game.py            # 🚦 Traffic Simulation Game
├── snake_ladder_game.py       # 🐍 Snake & Ladder Game
├── tsp_game.py                # 🗺️ Traveling Salesman Problem Game
├── hanoi_game.py              # 🗼 Tower of Hanoi Game
├── queens_game.py             # ♕ Eight Queens Puzzle Game
│
└── game_collection.db         # SQLite database (auto-generated)
```

## 🎯 Games Overview

### 1. 🚦 Traffic Simulation
- **Algorithm**: Max Flow (Ford-Fulkerson, Edmonds-Karp)
- **Objective**: Calculate maximum vehicle flow through a network
- **Features**: Random network generation, visual graph display

### 2. 🐍 Snake & Ladder
- **Algorithm**: BFS, Dijkstra's Algorithm
- **Objective**: Find minimum dice throws to reach the end
- **Features**: Configurable board size (6x6 to 12x12), visual board

### 3. 🗺️ Traveling Salesman Problem
- **Algorithm**: Brute Force, Nearest Neighbor
- **Objective**: Find shortest route visiting all cities
- **Features**: City selection, distance matrix display

### 4. 🗼 Tower of Hanoi
- **Algorithm**: Recursive, Iterative
- **Objective**: Calculate minimum moves to solve puzzle
- **Features**: Configurable disks (5-10) and pegs (3-4)

### 5. ♕ Eight Queens Puzzle
- **Algorithm**: Sequential Backtracking, Threaded Parallel
- **Objective**: Place 8 queens without attacks
- **Features**: Solution visualization, validity checking

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install matplotlib networkx
```

## ▶️ How to Run

1. **Navigate to the project directory:**
   ```bash
   cd game_collection
   ```

2. **Run the main application:**
   ```bash
   python main.py
   ```

3. **The main menu will appear with all game options**

## 📊 Database

The application uses SQLite to store:
- Player information
- Game scores and attempts
- Algorithm performance metrics
- Game history

The database file `game_collection.db` is automatically created on first run.

## 🎮 How to Play

1. **Enter your player name** on the main menu
2. **Select a game** from the available options
3. **Read the instructions** (click "How to Play")
4. **Solve the puzzle** and submit your answer
5. **Check your score** and try again!

## 🔧 Module Details

### `database.py`
- Handles all database operations
- Creates and manages game tables
- Saves player responses and scores

### `main_menu.py`
- Main UI with game selection
- Player management
- Navigation between games

### `traffic_game.py`
- Implements max flow algorithms
- Network visualization using NetworkX
- Random network generation

### `snake_ladder_game.py`
- Board generation with snakes and ladders
- BFS and Dijkstra implementations
- Visual board representation

### `tsp_game.py`
- Distance matrix generation
- Brute force and heuristic solutions
- City selection interface

### `hanoi_game.py`
- Recursive and iterative solutions
- Multi-peg support (3-4 pegs)
- Move calculation

### `queens_game.py`
- Backtracking algorithm
- Multi-threaded solution finding
- Chessboard visualization

### `instructions.py`
- Comprehensive help system
- Game-specific instructions
- Algorithm explanations

## 🎨 Features

- **Interactive UI**: Modern tkinter interface
- **Visual Feedback**: Graphs, boards, and matrices
- **Performance Tracking**: Algorithm execution times
- **Score System**: Track your progress
- **Database Storage**: Persistent game history
- **Multiple Algorithms**: Compare different approaches

## 🛠️ Customization

You can easily modify:
- Board sizes in Snake & Ladder
- Network structure in Traffic Simulation
- Number of cities in TSP
- Number of disks/pegs in Hanoi
- Add new games by creating similar modules

## 📝 Code Organization

Each game module follows the same pattern:
1. **Algorithm Class**: Core logic and algorithms
2. **UI Class**: Tkinter interface
3. **Integration**: Database saving and main menu navigation

## 🤝 Contributing

To add a new game:
1. Create a new file (e.g., `new_game.py`)
2. Implement the algorithm class
3. Implement the UI class
4. Add database table in `database.py`
5. Add game button in `main_menu.py`
6. Add instructions in `instructions.py`

## 📚 Learning Resources

Each game demonstrates important CS concepts:
- **Graph Theory**: Traffic Simulation, Snake & Ladder
- **Optimization**: TSP, Tower of Hanoi
- **Backtracking**: Eight Queens
- **Dynamic Programming**: Various approaches
- **Parallel Computing**: Threaded solutions

## 🐛 Troubleshooting

**Issue**: Missing dependencies
- **Solution**: Run `pip install matplotlib networkx`

**Issue**: Database errors
- **Solution**: Delete `game_collection.db` and restart

**Issue**: UI not displaying
- **Solution**: Check Python version (3.7+) and tkinter installation

## 📄 License

This project is for educational purposes.

## 🙏 Acknowledgments

- Built with Python's tkinter for UI
- Uses matplotlib for graph visualization
- Uses NetworkX for network algorithms
- SQLite for data persistence

---

**Enjoy exploring algorithms through games!** 🎮✨
