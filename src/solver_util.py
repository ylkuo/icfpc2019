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
