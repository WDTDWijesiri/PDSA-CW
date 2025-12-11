# Tower of Hanoi Game

A professional, interactive implementation of the classic Tower of Hanoi puzzle with a modern GUI, statistics tracking, and algorithm visualization.

## Features

- **Interactive Gameplay**
  - Play with 3 or 4 pegs
  - Manual move controls with validation
  - Auto-solve functionality with animation
  
- **Algorithm Analysis**
  - Recursive solution implementation
  - Optimal move calculation: 2^n - 1
  - Execution time measurement
  - Move efficiency tracking

- **Statistics & Leaderboard**
  - Persistent game result storage
  - Player statistics display
  - Performance leaderboard (ranked by efficiency and time)
  - Historical game records

- **User Experience**
  - Centered window and dialogs for better visibility
  - Color-coded disk visualization
  - Real-time move counter and timer
  - Input validation for player names
  - Comprehensive error handling

## Installation

### Requirements
- Python 3.6+
- tkinter (usually included with Python)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## How to Play

1. **Start Game**: Enter your player name and select number of pegs (3 or 4)
2. **Understand Disks**: Random number of disks (5-10) selected for each game
3. **Make Moves**: 
   - Select source and destination peg from dropdowns
   - Click "Make Move" button
   - Rules enforced: larger disks cannot go on smaller disks
4. **Solve**: Move all disks from peg A to the last peg (C for 3-peg, D for 4-peg)
5. **Auto Solve**: Click "Auto Solve" to see the optimal solution animated
6. **Save & Quit**: Save your progress and return to main menu

## Algorithm

The game uses the **recursive Tower of Hanoi algorithm**:

```
To move n disks from source to target using auxiliary:
1. Move n-1 disks from source to auxiliary (using target as temp)
2. Move the largest disk from source to target
3. Move n-1 disks from auxiliary to target (using source as temp)
```

### Complexity Analysis
- **Time Complexity**: O(2^n)
- **Space Complexity**: O(n) - recursion depth
- **Optimal Moves**: 2^n - 1

## Project Structure

```
tower_of_hanoi/
├── main.py                 # Entry point
├── ui.py                   # GUI implementation (tkinter)
├── game.py                 # Game state management
├── algorithms.py           # Hanoi algorithm implementation
├── database.py             # SQLite persistence layer
├── test_algorithms.py      # Algorithm tests
├── test_database.py        # Database tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Code Quality & Best Practices

✅ **Implemented Best Practices:**
- Comprehensive docstrings for all functions and classes
- Type hints in function signatures
- Proper error handling with try-except blocks
- Input validation for all user inputs
- Database connection context managers to prevent resource leaks
- Parameterized SQL queries to prevent injection attacks
- Single responsibility principle in modules
- DRY (Don't Repeat Yourself) principles
- Clear separation of concerns (UI, Game Logic, Data)
- Centered windows and dialogs for better UX
- Meaningful error messages with user-friendly emoji indicators

## Game Files Description

### main.py
- Simple entry point that initializes and runs the application

### ui.py
- **MainMenu**: Main menu with game options (Start, Statistics, Leaderboard, Info)
- **GameWindow**: Active game interface with controls and visualization
- Implements proper window centering for all dialogs
- Features scrollable windows for large data displays

### game.py
- **GameManager**: Manages game state, disk positions, and move validation
- Tracks move history and game timing
- Validates all moves against Tower of Hanoi rules

### algorithms.py
- **optimal_moves_count()**: Calculates 2^n - 1
- **hanoi_recursive_moves()**: Generates optimal move sequence
- **timed_recursive_solution()**: Measures algorithm performance

### database.py
- Handles SQLite persistence
- Functions: insert_result, fetch_all, fetch_leaderboard
- Implements error handling and proper connection management
- Creates indexed tables for better query performance

## Performance Metrics

The game tracks:
- **Moves Made**: Actual number of moves performed
- **Optimal Moves**: Theoretical minimum (2^n - 1)
- **Efficiency**: (Optimal / Actual) × 100%
- **Time Taken**: Player's solution time
- **Algorithm Time**: Time to compute optimal solution

## Testing

Run the test suites:

```bash
# Test algorithms
python test_algorithms.py

# Test database
python test_database.py
```

## Future Enhancements

- Difficulty levels with different disk counts
- Multiplayer/competitive mode
- Undo/redo functionality
- Hint system
- Speed-run mode with time limits
- Sound effects and animations
- Mobile version

## License

This project is part of a coursework assignment.

## Author Notes

- **Group Project**: Developed as part of an algorithmic game development coursework
- **Language**: Python
- **Framework**: tkinter for GUI
- **Database**: SQLite for persistent storage

