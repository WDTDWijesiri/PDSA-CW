from algorithms import optimal_moves_count, hanoi_recursive_moves

def test_optimal():
    assert optimal_moves_count(3) == 7

def test_moves():
    moves = hanoi_recursive_moves(3)
    assert len(moves) == 7
