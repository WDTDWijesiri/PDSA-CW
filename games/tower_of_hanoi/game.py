"""
Tower of Hanoi Game Manager

Manages the game state, including disk positions, move validation, and game progress tracking.
"""

import time


class GameManager:
    """Manages the Tower of Hanoi game state and mechanics."""
    
    def __init__(self, pegs=3, disks=5):
        """
        Initialize the game manager.
        
        Args:
            pegs (int): Number of pegs (3 or 4)
            disks (int): Number of disks (typically 5-10)
        """
        self.pegs_count = pegs
        self.disks = disks

        self.pegs = [list(range(disks, 0, -1))] + [[] for _ in range(pegs - 1)]

        self.move_history = []
        self.moves_count = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the game timer."""
        self.start_time = time.perf_counter()

    def move(self, frm, to):
        """
        Move a disk from one peg to another.
        
        Args:
            frm (int): Source peg index (0=A, 1=B, 2=C, etc.)
            to (int): Destination peg index
            
        Raises:
            ValueError: If the move is invalid
        """
        if not self.pegs[frm]:
            raise ValueError("❌ Source peg is empty!")

        disk = self.pegs[frm][-1]

        if self.pegs[to] and self.pegs[to][-1] < disk:
            raise ValueError("❌ Cannot place larger disk on smaller disk!")

        self.pegs[frm].pop()
        self.pegs[to].append(disk)

        self.moves_count += 1
        self.move_history.append((frm, to))

    def is_solved(self):
        """
        Check if the puzzle is solved.
        
        Returns:
            bool: True if all disks are stacked on the last peg in correct order
        """
        return len(self.pegs[-1]) == self.disks and self.pegs[-1] == list(range(self.disks, 0, -1))

    def finish(self):
        """
        Finish the game and calculate elapsed time.
        
        Returns:
            float: Elapsed time in seconds, or 0 if game not started
        """
        if self.start_time:
            self.end_time = time.perf_counter()
            return self.end_time - self.start_time
        return 0
    
    def get_move_sequence(self):
        """
        Convert move history to string format.
        
        Returns:
            str: Move sequence like "A->B, B->C, C->D"
        """
        peg_names = ['A', 'B', 'C', 'D', 'E']
        return ', '.join([f"{peg_names[frm]}->{peg_names[to]}" for frm, to in self.move_history])