import subprocess
import json
import ast
import os
import time

import task
import puzzle
import solvers

team_id = 177

python_exec_name = "python3.7"

def call_client(args):
    cmd = [python_exec_name, 'lambda-cli.py'] + args

    result = subprocess.run(cmd,
            cwd = '../lambda-client/',
            universal_newlines = True,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE)

    if result.returncode != 0:
        print("Error in ", ' '.join(cmd))
        print("**stdout")
        print(result.stdout)
        print("**stderr")
        print(result.stderr)
        result.check_returncode()

    return result.stdout

# Returns a dictionary
#
#   block       integer of which block we are on
#   excluded    list of excluded team ids
#   puzzle      puzzle description string
#   task        task description string
#
def getblockinfo():
    # return json.loads(call_client(['getblockinfo']))
    return ast.literal_eval(call_client(['getblockinfo']))

# task_solver : function from Task to State
# puzzle_solver : function from Puzzle to Task
def work_on_current_block(task_solver = solvers.nn_solver, puzzle_solver = puzzle.solve_puzzle):
    # Get current block chain
    blockinfo = getblockinfo()
    block_idx = blockinfo['block']
    task_string = blockinfo['task']
    puzzle_string = blockinfo['puzzle']
    excluded = blockinfo['excluded']
    balances = blockinfo['balances']

    subdir = os.path.join('..', 'chain_submissions', str(block_idx))
    os.makedirs(subdir, exist_ok = True)

    task_solution_path = os.path.join(subdir, 'task.sol')
    puzzle_solution_path = os.path.join(subdir, 'puzzle.desc')
    submitted_path = os.path.join(subdir, 'submitted')

    print("Working on block", block_idx)

    if str(team_id) in excluded:
        print("Note that we are excluded from working on this block!")

    print("  Balance:", balances[str(team_id)])

    if os.path.exists(submitted_path):
        print("  Already submitted to this block")
        return

    # Parse puzzles

    t = task.Task.from_string(task_string)
    p = puzzle.Puzzle(puzzle_string)

    # Solve puzzles

    print("  solving...")
    task_solution = task_solver(t)
    print("  ...done with task")
    puzzle_solution = puzzle_solver(p)
    print("  ...done with puzzle")

    # Print puzzles


    task_solution.to_file(task_solution_path)
    with open(puzzle_solution_path, 'w') as f:
        f.write(puzzle_solution.to_string())

    # Submit puzzles

    print("  submitting...")
    call_client(['submit', str(block_idx), str(task_solution_path), str(puzzle_solution_path)])
    print("  ...submitted!")

    with open(submitted_path, 'w') as f:
        f.write('Submitted\n')

def work_periodically(period = 5 * 60):
    while True:
        work_on_current_block()
        time.sleep(period)

if __name__ == "__main__":
    work_periodically()
