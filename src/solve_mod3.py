import numpy as np

import task
import gamestate

def solve_mod3(task, verbose = False):
    gs = gamestate.State(task)

    target = np.zeros((gs.X, gs.Y, 2), dtype = int)
    for x in range(gs.X):
        for y in range(gs.Y):
            if x == 0:
                target[x, y, 0] = x
                target[x, y, 1] = y
            else:
                target[x, y, 0] = x - 1
                target[x, y, 1] = min(gs.Y - 1, 1 + 3 * (y // 3))
            if not gs.interior[target[x, y, 0], target[x, y, 1]]:
                target[x, y, 0] = x
                target[x, y, 1] = y

    goal = np.zeros((gs.X, gs.Y), dtype = bool)

    pf = gamestate.Pathfinder(gs)

    i = 0

    gs.start()
    while True:
        i += 1
        if verbose and (i % 1000 == 0):
            print(np.sum(gs.unpainted))

        if np.sum(gs.unpainted) == 0:
            return gs

        for w in gs.workers:
            goal.fill(False)
            t = target[gs.unpainted]
            goal[t[:, 0], t[:, 1]] = True
            x, y = pf.nearest_in_array(w.x, w.y, goal)
            path = pf.compute_path(w.x, w.y, x, y)
            assert len(path) > 0
            for x_, y_ in path[1:]:
                w.move(x_ - w.x, y_ - w.y)

if __name__ == "__main__":
    import sys
    fn = sys.argv[1]
    task = task.Task.from_file(fn)
    gs = solve_mod3(task, verbose = True)
    gs.to_file('temp_mod3.sol')
