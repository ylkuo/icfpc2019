import itertools
import heapq
import numpy as np

import task
import gamestate

from collections import defaultdict


# nearest neighbor algorithm to solve traveling salesman
def nn(worker):
    finder = gamestate.Pathfinder(worker.gs)
    while True:
        if np.all(np.logical_not(worker.gs.unpainted)):
            return
        # find nearest neighbor and go there
        pos = (worker.x, worker.y)
        x, y = finder.nearest_in_array(worker.x, worker.y, worker.gs.unpainted)
        path = finder.compute_path(worker.x, worker.y, x, y)
        assert len(path) > 0
        for n in path[1:]:
            dx = n[0] - worker.x; dy = n[1] - worker.y
            worker.move(dx, dy)

# mincut to get regions and paint each region
def mincut_nn():
    pass

if __name__ == "__main__":
    tasks = task.tasks_in_directory(task.part1)
    gs = gamestate.State(tasks[140])
    gs.start()
    nn(gs.workers[0])
    print(gs.to_string())
