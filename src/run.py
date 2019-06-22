import numpy as np

import task
import gamestate

def print_tasks_in_directory(path):
    tasks = task.tasks_in_directory(path)
    for t in tasks:
        gs = gamestate.State(t)
        i = gs.interior

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

if __name__ == "__main__":
    print_tasks_in_directory(task.part1)
    # tasks = tasks_in_directory(part1)
