import time

def optimal_moves_count(n):
    return 2**n - 1

def hanoi_recursive_moves(n, source="A", target="C", auxiliary="B", moves=None):
    if moves is None:
        moves = []
    if n == 1:
        moves.append((source, target))
    else:
        hanoi_recursive_moves(n-1, source, auxiliary, target, moves)
        moves.append((source, target))
        hanoi_recursive_moves(n-1, auxiliary, target, source, moves)
    return moves

def timed_recursive_solution(n):
    start = time.perf_counter()
    moves = hanoi_recursive_moves(n)
    end = time.perf_counter()
    return moves, (end - start)
