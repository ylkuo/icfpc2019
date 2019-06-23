import numpy as np

import sys
np.set_printoptions(threshold=sys.maxsize)

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
        x, y = finder.nearest_in_array(worker.x, worker.y, worker.gs.unpainted)
        path = finder.compute_path(worker.x, worker.y, x, y)
        assert len(path) > 0
        for n in path[1:]:
            dx = n[0] - worker.x; dy = n[1] - worker.y
            worker.move(dx, dy)

# get regions and paint each region
def region_nn(worker):
    rm = gamestate.RegionManager(worker.gs)
    rm.compute_regions()
    next_rid = rm.regions[worker.x, worker.y]
    finder = gamestate.Pathfinder(worker.gs)
    while True:
        unpainted = rm.get_region(next_rid)
        if np.all(np.logical_not(unpainted)):
            if np.all(np.logical_not(worker.gs.unpainted)):
                return
            else:
                x, y = finder.nearest_in_array(worker.x, worker.y, worker.gs.unpainted)
                next_rid = rm.regions[x, y]
                continue
        x, y = finder.nearest_in_array(worker.x, worker.y, unpainted)
        path = finder.compute_path(worker.x, worker.y, x, y)
        assert len(path) > 0
        for n in path[1:]:
            dx = n[0] - worker.x; dy = n[1] - worker.y
            worker.move(dx, dy)


if __name__ == "__main__":
    tasks = task.tasks_in_directory(task.part1)
    gs = gamestate.State(tasks[1])
    gs.start()
    nn(gs.workers[0])
    print(gs.to_string())
