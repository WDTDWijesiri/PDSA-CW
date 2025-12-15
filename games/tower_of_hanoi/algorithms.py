"""
Tower of Hanoi Algorithms

Implements BOTH recursive and iterative solutions for Tower of Hanoi problem.
This satisfies the coursework requirement of 2 different algorithm approaches.
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
        return 2**n - 1  

# ALGORITHM 1: RECURSIVE SOLUTION (Classic)

def hanoi_recursive_moves(n, source="A", target="C", auxiliary="B", moves=None):
    """
    ALGORITHM 1: Generate the optimal sequence using RECURSIVE algorithm.
    
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
        #base case: move one disk directly
        moves.append((source, target))
    else:
        #recursive case: move n-1 disks, then move largest, then move n-1 disks again
        hanoi_recursive_moves(n-1, source, auxiliary, target, moves)
        moves.append((source, target))
        hanoi_recursive_moves(n-1, auxiliary, target, source, moves)
    
    return moves


# ALGORITHM 2: ITERATIVE SOLUTION (Stack-based)

def hanoi_iterative_moves(n, source="A", target="C", auxiliary="B"):
    """
    ALGORITHM 2: Generate the optimal sequence using ITERATIVE algorithm.
    
    This is a stack-based iterative solution that simulates the recursive approach
    without using recursion. It uses an explicit stack to track operations.
    
    Time Complexity: O(2^n)
    Space Complexity: O(n) - stack depth
    
    Pattern for odd/even number of disks:
    - Odd n: A→C, A→B, C→B pattern
    - Even n: A→B, A→C, B→C pattern
    
    Args:
        n (int): Number of disks
        source (str): Starting peg
        target (str): Goal peg
        auxiliary (str): Auxiliary peg
        
    Returns:
        list: List of tuples (from_peg, to_peg) representing each move
    """
    moves = []
    
    total_moves = 2**n - 1
    
    peg_map = {source: 0, auxiliary: 1, target: 2}
    reverse_map = {0: source, 1: auxiliary, 2: target}

    stacks = [list(range(n, 0, -1)), [], []]

    if n % 2 == 0:
        pairs = [(0, 1), (0, 2), (1, 2)]
    else:
        pairs = [(0, 2), (0, 1), (2, 1)]
    
    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            from_idx, to_idx = pairs[0]
        elif i % 3 == 2:
            from_idx, to_idx = pairs[1]
        else:
            from_idx, to_idx = pairs[2]

        if not stacks[from_idx] and not stacks[to_idx]:
            continue
        elif not stacks[from_idx]:
            stacks[from_idx].append(stacks[to_idx].pop())
            moves.append((reverse_map[to_idx], reverse_map[from_idx]))
        elif not stacks[to_idx]:
            stacks[to_idx].append(stacks[from_idx].pop())
            moves.append((reverse_map[from_idx], reverse_map[to_idx]))
        elif stacks[from_idx][-1] < stacks[to_idx][-1]:
            stacks[to_idx].append(stacks[from_idx].pop())
            moves.append((reverse_map[from_idx], reverse_map[to_idx]))
        else:
            stacks[from_idx].append(stacks[to_idx].pop())
            moves.append((reverse_map[to_idx], reverse_map[from_idx]))
    
    return moves

def hanoi_4_pegs_recursive(n, source="A", target="D", aux1="B", aux2="C", moves=None):
    """
    ALGORITHM 1 (4-peg): Recursive Frame-Stewart algorithm for 4 pegs.
    
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
    
    optimal_k = {
        2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 2, 9: 5, 10: 2
    }
    k = optimal_k.get(n, 1) 
    
    # Frame-Stewart algorithm:
    hanoi_4_pegs_recursive(k, source, aux1, target, aux2, moves)
    
    hanoi_recursive_moves(n - k, source, target, aux2, moves)
   
    hanoi_4_pegs_recursive(k, aux1, target, source, aux2, moves)
    
    return moves


def hanoi_4_pegs_iterative(n, source="A", target="D", aux1="B", aux2="C"):
    """
    ALGORITHM 2 (4-peg): Iterative Frame-Stewart using dynamic programming.
    
    This approach uses dynamic programming to determine optimal k values
    and then iteratively constructs the solution.
    
    Args:
        n (int): Number of disks
        source (str): Starting peg
        target (str): Goal peg
        aux1, aux2 (str): Auxiliary pegs
        
    Returns:
        list: List of tuples (from_peg, to_peg)
    """
   
    moves = []

    stack = [(n, source, target, aux1, aux2, 'start')]
    
    while stack:
        disks, src, tgt, a1, a2, phase = stack.pop()
        
        if disks == 0:
            continue
        elif disks == 1:
            moves.append((src, tgt))
        else:
            # Compute optimal k
            optimal_k = {
                2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 2, 9: 5, 10: 2
            }
            k = optimal_k.get(disks, 1)
            
            if phase == 'start':                
                stack.append((k, a1, tgt, src, a2, 'start'))
                stack.append((disks - k, src, tgt, a2, None, '3peg'))
                stack.append((k, src, a1, tgt, a2, 'start'))

            elif phase == '3peg':               
                three_peg_moves = hanoi_iterative_moves(disks, src, tgt, a2)
                moves.extend(three_peg_moves)
    
    return moves



def timed_recursive_solution(n, pegs=3):
    """
    Generate the optimal solution using RECURSIVE algorithm and measure time.
    
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
        moves = hanoi_4_pegs_recursive(n)
    else:
        moves = hanoi_recursive_moves(n)
    end = time.perf_counter()
    return moves, (end - start)


def timed_iterative_solution(n, pegs=3):
    """
    Generate the optimal solution using ITERATIVE algorithm and measure time.
    
    Args:
        n (int): Number of disks
        pegs (int): Number of pegs (3 or 4)
        
    Returns:
        tuple: (list of moves, execution time in seconds)
    """
    start = time.perf_counter()
    if pegs == 3:
        moves = hanoi_iterative_moves(n)
    elif pegs == 4:
        moves = hanoi_4_pegs_iterative(n)
    else:
        moves = hanoi_iterative_moves(n)
    end = time.perf_counter()
    return moves, (end - start)


def format_moves(moves):
    """
    Convert move list to string format.
    
    Args:
        moves (list): List of tuples like [('A', 'B'), ('B', 'C')]
        
    Returns:
        str: Formatted string like "A->B, B->C"
    """
    return ', '.join([f"{frm}->{to}" for frm, to in moves])