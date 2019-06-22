import itertools
import heapq
import numpy as np

import task
import gamestate

from collections import defaultdict

# bfs to find paths from start to the goal
def bfs(gs, start, goal):
    graph = gs.interior
    queue = [(start, [start])]
    visited = defaultdict(set)
    while queue:
        (vertex, path) = queue.pop(0)
        neighbors = [(1,0), (-1,0), (0,1), (0,-1)]
        neighbors = [tuple(map(sum, zip(n, vertex))) for n in neighbors]
        neighbors = set(filter(lambda n: n[0] >= 0 and \
            n[0] < gs.X and n[1] >= 0 and n[1] < gs.Y and \
            graph[n] and n not in visited[vertex], neighbors))
        for next in neighbors - set(path):
            visited[vertex].add(next)
            if next == goal:
                yield path + [next]
            else:
                queue.append((next, path + [next]))

def shortest_path(gs, start, goal):
    path = list(next(bfs(gs, start, goal)))
    assert len(path) > 0
    return path

# nearest neighbor algorithm to solve traveling salesman
# n_cand to set number of nearest neighbors candidates (based on Manhattan distance).
def nn(worker, n_cand=5):
    while True:
        if np.all(np.logical_not(worker.gs.unpainted)):
            return
        # find nearest neighbor and go there
        pos = (worker.x, worker.y)
        unvisited = np.dstack(np.where(worker.gs.unpainted == True))[0]
        approx_nearest = heapq.nsmallest(n_cand, unvisited, key=lambda y: sum(np.abs(y-pos)))
        paths = [shortest_path(worker.gs, pos, tuple(n)) for n in approx_nearest]
        path = min(paths, key=lambda p: len(p))
        assert len(path) > 0
        for n in path[1:]:
            dx = n[0] - worker.x; dy = n[1] - worker.y
            worker.move(dx, dy)

# mincut to get regions and paint each region
def mincut_nn():
    pass

if __name__ == "__main__":
    tasks = task.tasks_in_directory(task.part1)
    gs = gamestate.State(tasks[0])
    gs.start()
    nn(gs.workers[0])
    print(gs.to_string())
