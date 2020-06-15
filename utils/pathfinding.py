import math


def dist(v1, v2):
    a = abs(v1[0] - v2[0]) ** 2
    b = abs(v1[1] - v2[1]) ** 2
    return math.sqrt(a + b)


class AStarPathFinder:

    def __init__(self, size):
        self.start = None
        self.end = None
        self.size = size
        self.blocks = {}
        self.scores = {}
        
        self.clear_scores()

    def clear_scores(self):
        for x in range(-self.size, self.size + 1):
            for y in range(-self.size, self.size + 1):
                self.scores[x, y] = None
    
    def clear_blocks(self):
        self.blocks = {}

    def block(self, pos, block=True):
        self.blocks[pos] = block
    
    def unblock(self, po):
        self.blocks[pos] = True
    
    def set_start(self, pos):
        self.start = pos
    
    def set_end(self, pos):
        self.end = pos
    
    def add_next_coords(self, pos, next_coords):
        for d in ((0,1), (0,-1), (1,0), (-1,0)):
            p = (pos[0]+d[0], pos[1]+d[1])
            if p in self.scores and self.scores[p] is None:
                next_coords.add(p)
    
    def score_cells(self):
        self.clear_scores()
        self.scores[self.end] = 0.0

        next_coords = set()
        next_score = 0.0
        self.add_next_coords(self.end, next_coords)
        cycles = 0
        while True:
            if self.scores[self.start] is not None:
                break
            if cycles >= self.size*2**3:
                break
            next_score += 1
            for c in next_coords.copy():
                if c in self.blocks:
                    self.scores[c] == float('inf')
                else:
                    self.scores[c] = next_score
                    self.add_next_coords(c, next_coords)
                next_coords.remove(c)
            
            cycles += 1
    
    def follow_path(self):
        cp = self.start
        cs = self.scores[cp]
        cycles = 0
        yield cp
        while cp != self.end and cycles < self.size**2:
            candidates = []
            for d in ((0,1), (0,-1), (1,0), (-1,0)):
                np = (cp[0]+d[0], cp[1]+d[1])
                ns = self.scores.get(np)
                if ns is not None and ns < cs:
                    nd = dist(np, self.end)
                    candidates.append((nd, ns, np))
            
            if candidates:
                candidates.sort()
                candidates = [c for c in candidates if c[0] == candidates[0][0]]
                _, cs, cp = candidates[0]
                yield cp
            cycles += 1
