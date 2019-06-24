import shutil
import os.path

import task


def read_times(i):
    pass


def run():
    os.path.makedirs('../submission/', exist_ok = True)

    tasks = task.all_tasks()

    for t in tasks:
        name = os.path.basename(t.filename)
        assert name.endswith('.desc')
        root = name[:-5]

        t.use_clone = False

        t.sol_clone_0 = '../tasks/solutions0/' + root + '.sol'
        t.sol_clone_1 = '../tasks/solutions1/' + root + '.sol'
        t.buy_file = '../submission/' + root + '.buy'
        t.dest_file = '../submission/' + root + '.sol'

        with open('../tasks/time0/' + root + '.t', 'r') as f:
            t.time_clone_0 = int(f.read().strip())

        with open('../tasks/time1/' + root + '.t', 'r') as f:
            t.time_clone_1 = int(f.read().strip())

    tasks.sort(key = lambda t : t.time_clone_0 / t.time_clone_1, reverse = True)

    num_clones = 199

    for i in range(num_clones):
        t = tasks[i]
        print("Buying a clone for ", os.path.basename(t.filename)[:-5], " times are ", t.time_clone_0, " vs ", t.time_clone_1, " ratio ", t.time_clone_0 / t.time_clone_1)
        t.use_clone = True

    for t in tasks:
        if t.use_clone:
            source_file = t.sol_clone_1

            with open(t.buy_file, 'w') as f:
                f.write('C')
        else:
            source_file = t.sol_clone_0

        shutil.copyfile(source_file, t.dest_file)

if __name__ == "__main__":
    run()
