import math
import os.path
import numpy as np

import task
import gamestate

def print_tasks_in_directory(path):
    tasks = task.tasks_in_directory(path)
    for t in tasks:
        gs = gamestate.State(t)
        i = gs.interior

        print(t.summary())
        if os.path.basename(t.filename) < 'prob-280':
            continue

        rows = []
        for y in range(gs.Y):
            row = []
            for x in range(gs.X):
                if i[x, gs.Y - y - 1]:
                    row.append(' ')
                else:
                    row.append('#')
            rows.append(''.join(row))

        print('\n'.join(rows))
        if len(input(t.summary()).strip()) > 0:
            break

def print_all_tasks():
    tasks = task.all_tasks()
    f = "{: >10}" * 7
    i = 0
    total_score = 0
    for t in tasks:
        if i % 20 == 0:
            print()
            print(f.format("area", "x", "y", "max_score", "clones", "spawns", "teleports"))
        i += 1

        gs = gamestate.State(t)
        gs.start()

        area = np.sum(gs.interior)
        x = gs.X
        y = gs.Y
        num_clones = len(gs.clone_on_ground)
        num_spawns = len(gs.spawn_list)
        num_teles = len(gs.tele_on_ground)
        max_score = 1 + int(1000 * math.log(x * y) / math.log(2))
        total_score += max_score
        print(f.format(area, x, y, max_score, num_clones, num_spawns, num_teles) + "   " + os.path.basename(t.filename))

    print()
    print("Total available score: ", total_score)

if __name__ == "__main__":
    print_all_tasks()
    # print_tasks_in_directory(task.part1)
    # print_tasks_in_directory(task.part2)
    # print_tasks_in_directory(task.part3)
    # tasks = tasks_in_directory(part1)
