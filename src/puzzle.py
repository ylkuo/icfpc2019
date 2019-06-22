import numpy as np

import task
from task import B, F, L, R, C, X

class Puzzle:
    def __init__(self, s):
        a, b, c = s.strip().split('#')
        self.points_in = task.parse_point_list(b)
        self.points_out = task.parse_point_list(b)
        xs = [int(x) for x in a.split(',')]
        self.block, self.epoch, self.size, self.vmin, self.vmax = xs[:5]

        self.boosters = {}

        for bt, i in [(B, 5), (F, 6), (L, 7), (R, 8), (C, 9), (X, 10)]:
            self.boosters[bt] = xs[i]

# Given an array of bool that is True for the interior of a rectilinear region,
# return the appropriate list of points describing its boundary.
# Assume interior_extra has been given a border of False on all four sides.
def read_map(self, interior_extra):
    i = interior_extra
    X, Y = np.shape(i)

    x0 = None
    y0 = None

    for y in range(Y):
        for x in range(X):
            if i[x, y]:
                x0, y0 = x, y
                break

        if x0 is not None:
            break

    # d = direction
    d = 1

    dxys = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]], dtype = int)

    xy = np.array([x0, y0], dtype = int)
    path = [list(xy - 1)]

    while True:
        xy = xy + dxys[d]
        x, y = list(xy)

        if x == x0 and y == y0:
            break

        count = np.sum(i[x - 1 : x + 1, y - 1 : y + 1])
        assert count in [1, 2, 3]
        if count != 2:
            path.append(list(xy - 1))
            d = (d + 2 + count) % 4

    return path

def solve_puzzle(puzzle):
    M = puzzle.size
    M2 = M + 2
    i = np.zeros((M2, M2), dtype = bool)
    i[1 : -1, 1 : -1] = True

    todo = []
    for x, y in puzzle.points_out:
        todo.append((x + 1, y + 1))

    forbidden = np.zeros((M2, M2), dtype = bool)
    for x, y in puzzle.points_in:
        forbidden[x + 1, y + 1] = True

    dxys = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    visited = np.zeros((M2, M2), dtype = bool)
    dx = np.zeros((M2, M2), dtype = int)
    dy = np.zeros((M2, M2), dtype = int)
    while len(todo) > 0:
        visited.fill(False)
        dx.fill(0)
        dy.fill(0)
        active = list(todo)
        done = []

        for x, y in active:
            visited[x, y] = True

        while len(done) == 0:
            next_active = []
            for x, y in active:
                if not i[x, y]:
                    done.append((x, y))
                    continue
                if forbidden[x, y]:
                    continue

                for dx_, dy_ in dxys:
                    x_ = x + dx_
                    y_ = y + dy_
                    if not visited[x_, y_]:
                        next_active.append((x_, y_))
                        visited[x_, y_] = True
                        dx[x_, y_] = -dx_
                        dy[x_, y_] = -dy_
            active = next_active

        for xy in done:
            x, y = xy
            while dx[x, y] != 0 or dy[x, y] != 0:
                dx_ = dx[x, y]
                dy_ = dy[x, y]
                x += dx_
                y += dy_
                i[x, y] = False
            todo.remove(x, y)

    # Add any necessary complexity

    path = None
    while True:
        path = read_map(i)
        assert len(path) <= puzzle.vmax

        if len(path) >= puzzle.vmin:
            break

        progress = False
        for x, y in path:
            count = np.sum(i[x : x + 2, y : y + 2])
            if count == 1:
                if np.sum(forbidden[x : x + 2, y : y + 2]) == 0:
                    i[x : x + 2, y : y + 2] = False
                    progress = True

        assert progress

