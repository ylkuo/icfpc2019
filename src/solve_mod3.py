import math
import numpy as np

import task
import gamestate
import solver_util

def solve_mod3(task, tie_break = False, make_clones = False, verbose = False):
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
    dist2 = np.zeros((gs.X + 2, gs.Y + 2), dtype = int)
    dist = None # np.zeros((gs.X, gs.Y), dtype = int)
    inf = 2 * (gs.X * gs.Y + 10)

    count = 0

    gs.start()

    if tie_break:
        noncentrality = solver_util.compute_centrality(gs)

    if make_clones:
        solver_util.make_clones(gs)

    for w in gs.workers:
        w.too_close = False

    while True:
        count += 1
        if verbose and (count % 1000 == 0):
            print(np.sum(gs.unpainted))

        if np.sum(gs.unpainted) == 0:
            if make_clones:
                gs2 = gs.replay_and_validate()
                if verbose:
                    print("Time:", gs.time(), "truncated to", gs2.time())
                return gs2
            else:
                return gs

        w = gs.oldest_worker()

        # Are we too close to other workers?
        if not w.too_close:
            for w_ in gs.workers:
                if not (w is w_) and abs(w.x - w_.x) + abs(w.y - w_.y) < 5:
                    w.too_close = True
                    break

        if w.too_close:
            # Compute farthest unpainted point from any other worker
            dist2.fill(inf)
            for w_ in gs.workers:
                w_.compute_distance()
                if not (w is w_):
                    dist2 = np.minimum(dist2, w_.pf.dist)
            dist = dist2[1 : -1, 1 : -1]
            dist[~gs.unpainted] = 0

            x, y = np.unravel_index(np.argmax(dist, axis = None), dist.shape)
            w.walk_path_to(x, y)
            w.too_close = False

        else:
            goal.fill(False)
            t = target[gs.unpainted]
            goal[t[:, 0], t[:, 1]] = True

            if tie_break:
                xs = w.pf.all_nearest_in_array(w.x, w.y, goal)
                assert len(xs) > 0
                x, y = xs[0]
                least_central = noncentrality[x, y]
                for x_, y_ in xs[1:]:
                    if noncentrality[x_, y_] > least_central:
                        x = x_
                        y = y_
                        least_central = noncentrality[x_, y_]
            else:
                x, y = w.nearest_in_array(goal)
            w.walk_path_to_max(x, y, 30)

if __name__ == "__main__":
    import sys
    fn = sys.argv[1]
    task = task.Task.from_file(fn)
    gs = solve_mod3(task, tie_break = True, make_clones = True, verbose = True)
    gs.to_file('temp_mod3.sol')
