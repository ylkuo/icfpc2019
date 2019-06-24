import os.path

import task
import gamestate
import plan
import solve_mod3

# A solver is a function from Task to State

def nn_solver(t):
    gs = gamestate.State(t)
    plan.nn(gs.start())
    return gs

def best_(t, verbose = False):
    states = []

    if verbose: print('NN')
    states.append(nn_solver(t))
    if verbose: print('     ', states[-1].time())
    if verbose: print('mod3')
    states.append(solve_mod3.solve_mod3(t))
    if verbose: print('     ', states[-1].time())
    if verbose: print('mod3 with clones')
    states.append(solve_mod3.solve_mod3(t, make_clones = True))
    if verbose: print('     ', states[-1].time())

    states.sort(key = lambda s : s.time())
    return states[0]

def prob1(t):
    assert os.path.basename(t.filename) == "prob-001.desc"
    gs = gamestate.State(t)
    w = gs.start()
    w.move_up()
    w.move_up()
    w.move_down()
    w.move_right()
    w.move_right()
    w.move_right()
    w.move_right()
    w.move_right()
    w.move_right()
    return gs

def best(t, verbose = False):
    names = []
    states = []

    has_clones = (t.extra_clones > 0) or (len(t.bt2pos[task.C]) > 0)
    has_teles = (len(t.bt2pos[task.R]) > 0)

    if os.path.basename(t.filename) == "prob-001.desc":
        names.append("by hand")
        states.append(prob1(t))

    if has_clones:
        # names.append("mod3")
        # states.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = False, make_clones = True))

        # names.append("mod3 tie")
        # states.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = True, make_clones = True))

        for bias in [5, 8]:
            names.append("mod3 clones bias " + str(bias))
            states.append(solve_mod3.solve_mod3(t, outward_bias = bias, tie_break = False, make_clones = True))
    else:
        # names.append("mod3")
        # states.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = False, make_clones = False))

        # names.append("mod3 tie")
        # states.append(solve_mod3.solve_mod3(t, outward_bias = 0, tie_break = True, make_clones = False))

        for bias in [5, 8]:
            names.append("mod3 bias " + str(bias))
            states.append(solve_mod3.solve_mod3(t, outward_bias = bias, tie_break = False, make_clones = False))

    best_time = min([gs.time() for gs in states])

    if verbose:
        for i in range(len(names)):
            if states[i].time() == best_time:
                print("{: >10}  **  {}".format(names[i], states[i].time()))
            else:
                print("{: >10}      {}".format(names[i], states[i].time()))

    for gs in states:
        if gs.time() == best_time:
            return gs

solvers = [nn_solver, solve_mod3.solve_mod3]

name2solver = {
            'nn' : nn_solver,
            'mod3' : solve_mod3.solve_mod3,
            'mod3_clone' : (lambda t : solve_mod3.solve_mod3(t, make_clones = True)),
            'best' : best
        }

if __name__ == "__main__":
    import sys
    fn = sys.argv[1]
    t = task.Task.from_file(fn)
    gs = best(t, verbose = True)
    gs.to_file('temp_best.sol')

