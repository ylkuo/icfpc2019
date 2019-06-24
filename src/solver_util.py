import numpy as np

import task
import gamestate

def nearest_in_list(pf, locations):
    dist = None
    nearest = None
    for x, y in locations:
        if nearest is None or pf.dist[x + 1, y + 1] < dist:
            dist = pf.dist[x + 1, y + 1]
            nearest = (x, y)
    return nearest

def make_clones(gs, spawn_detour_pct=0.004, teleport_detour_pct=0.003):
    pf = gamestate.Pathfinder(gs)

    w = gs.oldest_worker()
    while len(gs.clone_on_ground) > 0:
        goal = set(gs.clone_on_ground)

        w.compute_distance()

        cx, cy = nearest_in_list(w.pf, gs.clone_on_ground)
        d_direct = w.pf.dist[cx + 1, cy + 1]

        best_spawn = None
        best_spawn_divert = None
        if w.is_booster_available(task.C):
            sx, sy = nearest_in_list(w.pf, gs.spawn_list)
            x, y = pf.nearest_in_set(sx, sy, goal)
            d_divert = w.pf.dist[sx + 1, sy + 1] + pf.dist[x + 1, y + 1]

            if best_spawn is None or d_divert < best_spawn_divert:
                best_spawn = (sx, sy)
                best_spawn_divert = d_divert

        best_tele = None
        best_tele_divert = None
        if len(gs.tele_on_ground) > 0:
            sx, sy = nearest_in_list(w.pf, gs.tele_on_ground)
            x, y = pf.nearest_in_set(sx, sy, goal)
            d_divert = w.pf.dist[sx + 1, sy + 1] + pf.dist[x + 1, y + 1]

            if best_tele is None or d_divert < best_tele_divert:
                best_tele = (sx, sy)
                best_tele_divert = d_divert

        if best_spawn is not None:
            if best_spawn_divert - d_direct >= spawn_detour_pct * gs.amount_unpainted():
                best_spawn = None

        if best_tele is not None:
            if best_tele_divert - d_direct >= teleport_detour_pct * gs.amount_unpainted():
                best_tele = None

        # print(w.x, w.y, d_direct, best_spawn_divert, best_tele_divert, spawn_detour_pct * gs.amount_unpainted(), teleport_detour_pct * gs.amount_unpainted())

        if best_spawn is not None:
            x, y = best_spawn
            w.walk_path_to(x, y)
            while w.is_booster_available(task.C):
                w.clone()
        elif best_tele is not None:
            x, y = best_tele
            w.walk_path_to(x, y)
            w.wait()
            w.place_teleport()
        else:
            w.walk_path_to(cx, cy)
            w.wait()

        # if w.is_booster_available(task.C):
            # sx, sy = w.nearest_in_set(set(gs.spawn_list))
            # d_spawn = len(w.compute_path(sx, sy))
            # x, y = w.pf.nearest_in_set(sx, sy, goal)
            # d_clone = len(w.pf.compute_path(sx, sy, x, y))
            # x, y = w.nearest_in_set(goal)
            # d = len(w.compute_path(x, y))
            # if (d_spawn + d_clone) - d < detour_pct*gs.amount_unpainted():
                # w.walk_path_to(sx, sy)
                # while len(gs.boosters[task.C]) > 0:
                    # if w.is_booster_available(task.C):
                        # w.clone()
                    # else:
                        # w.wait()
        # x, y = w.nearest_in_set(goal)
        # w.walk_path_to(x, y)

    w.wait()
    if w.is_booster_available(task.C):
        x, y = w.nearest_in_set(set(gs.spawn_list))
        w.walk_path_to(x, y)

        while w.is_booster_available(task.C):
            w.clone()

    # if len(gs.boosters[task.C]) > 0:
        # goal = set(gs.spawn_list)
        # w = gs.oldest_worker()
        # x, y = w.nearest_in_set(goal)
        # w.walk_path_to(x, y)
# 
        # while len(gs.boosters[task.C]) > 0:
            # if w.is_booster_available(task.C):
                # w.clone()
            # else:
                # w.wait()

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

