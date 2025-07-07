class Cell:
    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.has_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.neighbor_mine_count = 0
