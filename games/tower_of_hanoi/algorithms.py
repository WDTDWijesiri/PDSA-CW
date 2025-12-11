"""
Tower of Hanoi Algorithms

Implements the classic recursive solution and performance analysis for the Tower of Hanoi problem.
"""

import time


def optimal_moves_count(n):
    """
    Calculate the optimal number of moves required to solve the Tower of Hanoi.
    
    The formula is 2^n - 1, where n is the number of disks.
    
    Args:
        n (int): Number of disks
        
    Returns:
        int: Minimum number of moves required
    """
    return 2**n - 1


def hanoi_recursive_moves(n, source="A", target="C", auxiliary="B", moves=None):
    """
    Generate the optimal sequence of moves using the recursive algorithm.
    
    Time Complexity: O(2^n)
    Space Complexity: O(n) - recursion depth
    
    The algorithm works as follows:
    1. Move n-1 disks from source to auxiliary (using target as temporary)
    2. Move the largest disk from source to target
    3. Move n-1 disks from auxiliary to target (using source as temporary)
    
    Args:
        n (int): Number of disks
        source (str): Starting peg (default 'A')
        target (str): Goal peg (default 'C')
        auxiliary (str): Auxiliary peg (default 'B')
        moves (list): Accumulator for the list of moves
        
    Returns:
        list: List of tuples (from_peg, to_peg) representing each move
    """
    if moves is None:
        moves = []
    
    if n == 1:
        # Base case: move one disk directly
        moves.append((source, target))
    else:
        # Recursive case: move n-1 disks, then move largest, then move n-1 disks again
        hanoi_recursive_moves(n-1, source, auxiliary, target, moves)
        moves.append((source, target))
        hanoi_recursive_moves(n-1, auxiliary, target, source, moves)
    
    return moves


def timed_recursive_solution(n):
    """
    Generate the optimal solution and measure execution time.
    
    Args:
        n (int): Number of disks
        
    Returns:
        tuple: (list of moves, execution time in seconds)
    """
    start = time.perf_counter()
    moves = hanoi_recursive_moves(n)
    end = time.perf_counter()
    return moves, (end - start)

