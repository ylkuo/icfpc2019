import gamestate
import plan

# A solver is a function from Task to State

def nn_solver(task):
    gs = gamestate.State(task)
    plan.nn(gs.start())
    return gs

solvers = [nn_solver]
