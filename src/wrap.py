import solvers
import task


frange=[(1, 150), (151, 220), (221, 300)]
def worker(task_id, extra):
    for f, minmax in enumerate(frange):
        if minmax[0] <= task_id <= minmax[1]:
            fn = '../tasks/part{}/prob-{:03d}.desc'.format(f+1, task_id)
    t = task.Task.from_file(fn)
    t.set_extra_clones(extra)
    gs = solvers.best(t, verbose=True)
    gs.to_file('../tasks/solutions1/prob-{:03d}.sol'.format(task_id))
    with open('../tasks/time1/prob-{:03d}.t'.format(task_id), 'w') as f:
        f.write(str(gs.time()))
    print('Finish task {}'.format(task_id))


if __name__ == '__main__':
    import sys
    min_task = int(sys.argv[1])
    max_task = int(sys.argv[2])
    extra = int(sys.argv[3])
    for task_id in range(min_task, max_task):
        worker(task_id, extra)

