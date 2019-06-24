import sys
import os.path

import task
import gamestate
import solvers
import solve_mod3

def go():
    max_bias = 20
    names = ['NN', 'mod3', 'mod3 tie']
    for i in range(1, max_bias + 1):
        names.append('mod3 bias ' + str(i))

    for i in range(len(names)):
        while len(names[i]) < 20:
            names[i] = names[i] + ' '

    tasks = task.all_tasks()
    for t in tasks[::15]:
        print(os.path.basename(t.filename))

        gs = []

        gs.append(solvers.nn_solver(t))
        gs.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = False, make_clones = True))
        gs.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = True, make_clones = True))
        for i in range(1, max_bias + 1):
            gs.append(solve_mod3.solve_mod3(t, outward_bias = i, tie_break = False, make_clones = True))

        best = min([gs_.time() for gs_ in gs])

        for i in range(len(names)):
            print('    ', end = '')
            if gs[i].time() == best:
                print('**  ', end = '')
            else:
                print('    ', end = '')
            print(names[i], end = '')
            print(' ', end = '')
            print(gs[i].time())

        sys.stdout.flush()

if __name__ == "__main__":
    go()
