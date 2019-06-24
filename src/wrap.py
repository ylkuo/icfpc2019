import multiprocessing

import solvers
import task


def init(i):
    global count
    count = i

frange=[(1, 150), (151, 220), (221, 300)]
def worker():
    while True:
        global count
        with count.get_lock():
            count.value += 1
            task_id = count.value
        if task_id > 300:
            break
        for f, minmax in enumerate(frange):
            if minmax[0] <= task_id <= minmax[1]:
                fn = '../tasks/part{}/prob-{:03d}.desc'.format(f+1, task_id)
        t = task.Task.from_file(fn)
        gs = solvers.best(t, verbose=True)
        gs.to_file('../tasks/solutions/prob-{:03d}.sol'.format(task_id))
        print('Finish task {}'.format(task_id))


if __name__ == '__main__':
    import sys
    n_workers = int(sys.argv[1])
    counter = multiprocessing.Value('i', 0)
    pool = multiprocessing.Pool(initializer=init, initargs=(counter,))
    pool.apply(worker)
    pool.close()
    pool.join()

