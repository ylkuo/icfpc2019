import task
import gamestate
import plan
import solve_mod3

# A solver is a function from Task to State

def nn_solver(task):
    gs = gamestate.State(task)
    plan.nn(gs.start())
    return gs

def best(task, verbose = False):
    states = []

    if verbose: print('NN')
    states.append(nn_solver(task))
    if verbose: print('     ', states[-1].time())
    if verbose: print('mod3')
    states.append(solve_mod3.solve_mod3(task))
    if verbose: print('     ', states[-1].time())
    if verbose: print('mod3 with clones')
    states.append(solve_mod3.solve_mod3(task, make_clones = True))
    if verbose: print('     ', states[-1].time())

    states.sort(key = lambda s : s.time())
    return states[0]

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
    task = task.Task.from_file(fn)
    gs = best(task, verbose = True)
    gs.to_file('temp_best.sol')

