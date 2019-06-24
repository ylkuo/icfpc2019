import numpy as np

import task
import gamestate

def make_clones(gs):
    while len(gs.clone_on_ground) > 0:
        goal = set(gs.clone_on_ground)
        w = gs.oldest_worker()
        x, y = w.nearest_in_set(goal)
        w.walk_path_to(x, y)

    if len(gs.boosters[task.C]) > 0:
        goal = set(gs.spawn_list)
        w = gs.oldest_worker()
        x, y = w.nearest_in_set(goal)
        w.walk_path_to(x, y)

        while len(gs.boosters[task.C]) > 0:
            if w.is_booster_available(task.C):
                w.clone()
            else:
                w.wait()

# Returns an array that, for each point x, returns
# the maximum of d(x, y) over all other points y.
# Only considers unpainted points.
def compute_centrality(gs):
    pf1 = gamestate.Pathfinder(gs)
    pf2 = gamestate.Pathfinder(gs)

    x0, y0 = gs.task.start

    pf1.compute_distance(x0, y0)
    dist1 = pf1.dist[1 : -1, 1 : -1]
    dist1[~gs.unpainted] = -1
    x1, y1 = np.unravel_index(np.argmax(dist1, axis = None), dist1.shape)

    pf1.compute_distance(x1, y1)
    dist1 = pf1.dist[1 : -1, 1 : -1]
    dist1[~gs.unpainted] = -1
    x2, y2 = np.unravel_index(np.argmax(dist1, axis = None), dist1.shape)

    pf2.compute_distance(x2, y2)
    dist2 = pf2.dist[1 : -1, 1 : -1]

    return np.maximum(dist1, dist2)

