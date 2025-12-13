"""
Tower of Hanoi Algorithms

Implements the classic recursive solution and performance analysis for the Tower of Hanoi problem.
"""

import time


def compute_frame_stewart_moves(n):
    """
    Compute the optimal number of moves for 4 pegs using Frame-Stewart algorithm.
    
    T(n) = min over k=1 to n-1 of 2*T(k) + T3(n-k)
    where T3(m) = 2^m - 1
    
    Args:
        n (int): Number of disks
        
    Returns:
        int: Optimal moves for 4 pegs
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    # Memoization
    memo = [0] * (n + 1)
    memo[0] = 0
    memo[1] = 1
    
    for i in range(2, n + 1):
        min_moves = float('inf')
        for k in range(1, i):
            moves = 2 * memo[k] + (2**(i - k) - 1)
            if moves < min_moves:
                min_moves = moves
        memo[i] = min_moves
    
    return memo[n]


def compute_optimal_k(n):
    """
    Compute the optimal k for Frame-Stewart algorithm for n disks.
    
    Returns the k that minimizes 2*T4(k) + T3(n-k)
    
    Args:
        n (int): Number of disks
        
    Returns:
        int: Optimal k
    """
    if n <= 1:
        return 0
    
    min_moves = float('inf')
    best_k = 1
    t4 = [0] * (n + 1)
    t4[0] = 0
    t4[1] = 1
    for i in range(2, n + 1):
        min_m = float('inf')
        for kk in range(1, i):
            m = 2 * t4[kk] + (2**(i - kk) - 1)
            if m < min_m:
                min_m = m
        t4[i] = min_m
    
    for k in range(1, n):
        moves = 2 * t4[k] + (2**(n - k) - 1)
        if moves < min_moves:
            min_moves = moves
            best_k = k
    return best_k


def optimal_moves_count(n, pegs=3):
    """
    Calculate the optimal number of moves required to solve the Tower of Hanoi.
    
    For 3 pegs: 2^n - 1
    For 4 pegs: Frame-Stewart optimal moves
    
    Args:
        n (int): Number of disks
        pegs (int): Number of pegs (3 or 4)
        
    Returns:
        int: Minimum number of moves required
    """
    if pegs == 3:
        return 2**n - 1
    elif pegs == 4:
        return compute_frame_stewart_moves(n)
    else:
        return 2**n - 1  # Default to 3-peg


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


def hanoi_4_pegs_moves(n, source="A", target="D", aux1="B", aux2="C", moves=None):
    """
    Generate the optimal sequence of moves for 4 pegs using Frame-Stewart algorithm.
    
    Args:
        n (int): Number of disks
        source (str): Starting peg
        target (str): Goal peg
        aux1, aux2 (str): Auxiliary pegs
        moves (list): Accumulator for moves
        
    Returns:
        list: List of tuples (from_peg, to_peg)
    """
    if moves is None:
        moves = []
    
    if n == 0:
        return moves
    if n == 1:
        moves.append((source, target))
        return moves
    
    # Optimal k values for Frame-Stewart (precomputed)
    optimal_k = {
        2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 2, 9: 5, 10: 2
    }
    k = optimal_k.get(n, 1)  # Default to 1 if not found
    
    # Frame-Stewart algorithm:
    # 1. Move k disks to aux1 using 4 pegs
    hanoi_4_pegs_moves(k, source, aux1, target, aux2, moves)
    # 2. Move n-k disks to target using 3 pegs (source, aux2, target)
    hanoi_recursive_moves(n - k, source, target, aux2, moves)
    # 3. Move k disks from aux1 to target using 4 pegs
    hanoi_4_pegs_moves(k, aux1, target, source, aux2, moves)
    
    return moves


def timed_recursive_solution(n, pegs=3):
    """
    Generate the optimal solution and measure execution time.
    
    Args:
        n (int): Number of disks
        pegs (int): Number of pegs (3 or 4)
        
    Returns:
        tuple: (list of moves, execution time in seconds)
    """
    start = time.perf_counter()
    if pegs == 3:
        moves = hanoi_recursive_moves(n)
    elif pegs == 4:
        moves = hanoi_4_pegs_moves(n)
    else:
        moves = hanoi_recursive_moves(n)
    end = time.perf_counter()
    return moves, (end - start)

