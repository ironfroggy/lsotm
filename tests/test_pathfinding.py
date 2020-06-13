from utils.pathfinding import *


def is_one_step(a, b):
    ax, ay = a
    bx, by = b
    assert ax == bx or ay == by
    assert abs(ax - bx) <= 1 and abs(ay - by) <= 1


# ---
# S-E
# ---
def test_straight():
    f = AStarPathFinder(1)
    f.start = (-1, 0)
    f.end = (1, 0)
    f.score_cells()
    
    assert f.scores[1, 0] == 0
    assert f.scores[0, 0] == 1
    assert f.scores[-1, 0] == 2

    path = list(f.follow_path())
    assert path == [(-1, 0), (0, 0), (1, 0)]

# --S
# ---
# E--
def test_diagonal():
    f = AStarPathFinder(1)
    f.start = (1, 1)
    f.end = (-1, -1)
    f.score_cells()
    
    assert f.scores[-1, -1] == 0
    assert f.scores[-1, 0] == 1
    assert f.scores[0, -1] == 1
    assert f.scores[0, 0] == 2
    assert f.scores[1, 0] == 3
    assert f.scores[0, 1] == 3
    assert f.scores[1, 1] == 4

    path = list(f.follow_path())
    assert path[0] == f.start
    for i in range(4):
        is_one_step(path[i], path[i + 1])
    assert path[4] == f.end

# SXE
# -X-
# ---
def test_around_blocks():
    f = AStarPathFinder(1)
    f.start = (-1, 1)
    f.end = (1, 1)
    f.block((0, 1))
    f.block((0, 0))
    f.score_cells()

    # for y in range(-f.size, f.size + 1):
    #     for x in range(-f.size, f.size + 1):
    #         print(' X ' if f.blocks.get((x, y)) else ' - ', end='')
    #     print()

    # for y in range(-f.size, f.size + 1):
    #     for x in range(-f.size, f.size + 1):
    #         s = f.scores[x, y]
    #         if (x, y) == f.start:
    #             print(' S ', end=' ')
    #         elif (x, y) == f.end:
    #             print(' E ', end=' ')
    #         else:
    #             print(s if s is not None else ' - ', end=' ')
    #     print()

    assert f.scores[0, -1] == 3
