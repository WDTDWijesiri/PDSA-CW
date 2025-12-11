import time

class GameManager:
    def __init__(self, pegs=3, disks=5):
        self.pegs_count = pegs
        self.disks = disks

        # Peg A = index 0
        self.pegs = [list(range(disks, 0, -1))] + [[] for _ in range(pegs - 1)]

        self.move_history = []
        self.moves_count = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def move(self, frm, to):
        if not self.pegs[frm]:
            raise ValueError("Source peg is empty")

        disk = self.pegs[frm][-1]

        if self.pegs[to] and self.pegs[to][-1] < disk:
            raise ValueError("Cannot place larger disk on smaller disk")

        self.pegs[frm].pop()
        self.pegs[to].append(disk)

        self.moves_count += 1
        self.move_history.append((frm, to))

    def is_solved(self):
        return len(self.pegs[-1]) == self.disks and self.pegs[-1] == list(range(self.disks, 0, -1))

    def finish(self):
        if self.start_time:
            self.end_time = time.perf_counter()
            return self.end_time - self.start_time
        return 0
