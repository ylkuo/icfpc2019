import gamestate
import plan
import solve_mod3

# A solver is a function from Task to State

def nn_solver(task):
    gs = gamestate.State(task)
    plan.nn(gs.start())
    return gs

solvers = [nn_solver, solve_mod3.solve_mod3]

name2solver = {
            'nn' : nn_solver,
            'mod3' : solve_mod3.solve_mod3
        }
