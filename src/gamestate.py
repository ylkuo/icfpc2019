import numpy as np

import compute_interior
import task

from task import B, F, L, R, C, X

# Lifecycle
#   gs = State(task)
#   worker = gs.start()
#   # do stuff with the worker object, which can produce other worker objects
#   # can do queries against gs to examine game state
#   gs.to_string()
#
# OR
#
#   gs = State(task)
#   gs.start()
#   while True:
#       ws = gs.workers
#       for w in ws:
#           # do a single action with w
#   gs.to_string()
#

#
# What happens if the various workers fall out of sync?
#   'Time' means number of steps elapsed since beginning of simulation
#   gs.time is the least time of any worker
#   So, to keep in sync, only execute commands on workers for which worker.time == gs.time
#   Using a booster on a worker causes that to be consumed immediately from the supply
#   Acting on a worker causes any painting to be updated immediately
#   Collecting a booster is only added when gamestate reaches that time step
#

# directions 0, 1, 2, 3 are N, E, S, W

dxdy2str = {
            (0, 0) : 'Z',
            (0, 1) : 'W',
            (1, 0) : 'D',
            (0, -1) : 'S',
            (-1, 0) : 'A'
        }

class Worker:
    def __init__(self, gs, position, time, parent):
        self.gs = gs
        self.gs.workers.append(self)
        self.x, self.y = position
        self.time = time
        self.cmds = []

        self.parent = parent
        if parent is None:
            self.worker_id = [time]
        else:
            self.worker_id = [time] + parent.worker_id

        self.speed_expires = -1
        self.drill_expires = -1

        self.direction = 1
        self.arms = [
                    [(0, 0), (-1, 1), (0, 1), (1, 1)],
                    [(0, 0), (1, 1), (1, 0), (1, -1)],
                    [(0, 0), (1, -1), (0, -1), (-1, -1)],
                    [(0, 0), (-1, -1), (-1, 0), (-1, 1)]
                ]

        self.paint()

    def do(self, cmd):
        if self.gs.has_boosters[self.x, self.y]:
            self.gs.collect_boosters(self.x, self.y, self.time)

        self.cmds.append(cmd)
        self.time += 1

    def paint(self):
        for dx, dy in self.arms[self.direction]:
            x_ = self.x + dx
            y_ = self.y + dy
            if x_ >= 0 and x_ < self.gs.X and y_ >= 0 and y_ < self.gs.Y:
                self.gs.unpainted[x_, y_] = False

    def is_booster_available(self, bt):
        return self.gs.is_booster_available(bt, self.time)

    def use_booster(eslf, bt):
        self.gs.use_booster(bt, self.time)

    def attach(self, dx, dy):
        assert False
        self.use_booster(B)
        self.do('B({}, {})'.format(dx, dy))

    def speed(self):
        self.use_booster(F)
        self.speed_expires = self.time + 50
        self.do('F')

    def drill(self):
        self.use_booster(L)
        self.drill_expires = self.time + 30
        self.do('L')

    def place_teleport(self):
        assert False
        self.use_booster(R)
        self.do('R')

    def clone(self):
        self.use_booster(C)
        w = Worker(self.gs, (self.x, self.y), self.time + 1, self)
        self.do('C')
        return w

    def move(self, dx, dy):
        x = self.x + dx
        y = self.y + dy
        assert x >= 0 and x < self.gs.X and y >= 0 and y < self.gs.Y
        if self.time >= self.drill_expires:
            assert self.gs.interior[x, y]
        self.x = x
        self.y = y

        self.paint()

        if self.time < self.speed_expires:
            x = self.x + dx
            y = self.y + dy
            assert x >= 0 and x < self.gs.X and y >= 0 and y < self.gs.Y
            if self.time < self.drill_expires or self.interior[x, y]:
                self.x = x
                self.y = y
                self.paint()

        self.do(dxdy2str[(dx, dy)])

    def move_left(self):
        self.move(-1, 0)

    def move_right(self):
        self.move(1, 0)

    def move_up(self):
        self.move(0, 1)

    def move_down(self):
        self.move(0, -1)

    # clockwise (to the right)
    def rotate_E(self):
        self.direction = (self.direction + 1) % 4
        self.paint()
        self.do('E')

    # anti-clockwise (to the left)
    def rotate_Q(self):
        self.direction = (self.direction + 3) % 4
        self.paint()
        self.do('Q')

class State:
    def __init__(self, task):
        self.task = task
        self.X = task.xmax
        self.Y = task.ymax

        self.spawn_list = task.bt2pos[X]

        self.interior = compute_interior.interior_with_obstacles(task.map, task.obstacles, self.X, self.Y)
        self.unpainted = np.copy(self.interior)

        # for a booster type bt, boosters[bt] is a list of the times that available boosters of that type were collected
        self.boosters = None
        self.workers = None

        self.speed_on_ground = None
        self.drill_on_ground = None
        self.clone_on_ground = None
        self.has_boosters = None
        self.started = False

    # You can repeatedly call start() to reset the state to the beginning, but do not use any old workers
    # after restarting or you will corrupt the state
    def start(self):
        self.boosters = {}
        for bt in task.bts:
            self.boosters[bt] = []

        self.workers = []
        self.speed_on_ground = list(self.task.bt2pos[F])
        self.drill_on_ground = list(self.task.bt2pos[L])
        self.clone_on_ground = list(self.task.bt2pos[C])
        self.has_boosters = np.zeros((self.X, self.Y), dtype = bool)
        for bt, pos in self.task.all_boosters:
            if bt != X:
                self.has_boosters[pos[0], pos[1]] = True

        self.started = True

        return Worker(self, self.task.start, 0, None)

    def is_booster_available(self, bt, time):
        for t in self.boosters[bt]:
            if t < time:
                return True
        return False

    def use_booster(self, bt, time):
        tmax = None
        for t in self.boosters[bt]:
            if t < time and ((tmax is None) or (tmax < t)):
                tmax = t
        assert tmax is not None
        self.boosters[bt].remove(tmax)

    def collect_boosters(self, x, y, time):
        pos = (x, y)
        for (bt, xs) in [(F, self.speed_on_ground), (L, self.drill_on_ground), (C, self.clone_on_ground)]:
            while pos in xs:
                xs.remove(pos)
                self.boosters[bt].append(time)
        self.has_boosters[x, y] = False

    def amount_unpainted(self):
        return np.sum(self.unpainted)

    def time(self):
        return max([w.time for w in self.workers])

    def to_string(self):
        self.workers.sort(key = lambda w : w.worker_id)
        return '#'.join((''.join(w.cmds)) for w in self.workers)

    def to_file(self, filename):
        s = self.to_string()
        with open(filename, 'w') as f:
            f.write(s)

#
# The internal arrays used by Pathfinder have a margin of 1 on all four sides.
# In particular, internal indices are off by 1.
#
#dxys_array = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]], dtype = int)
dxys = [(1, 0), (-1, 0), (0, 1), (0, -1)]
class Pathfinder:
    def __init__(self, gs):
        self.gs = gs

        X = gs.X + 2
        Y = gs.Y + 2

        self.interior = np.zeros((X, Y), dtype = bool)
        self.interior[1 : -1, 1 : -1] = gs.interior

        self.visited = np.zeros((X, Y), dtype = bool)
        self.dx = np.zeros((X, Y), dtype = int)
        self.dy = np.zeros((X, Y), dtype = int)
        self.dist = np.zeros((X, Y), dtype = int)

    # When completed, locations reachable from (x, y) will have
    #   visited = True
    #   dist = distance from (x, y)
    #   dx, dy = the step to take to go on the shortest path to (x, y) from a given point
    # All inaccessible locations will have
    #   visited = False
    def compute_distance(self, x0, y0):
        x0 += 1
        y0 += 1
        self.dist[x0, y0] = 0
        self.visited.fill(False)
        self.visited[x0, y0] = True

        active = [(x0, y0)]
        while len(active) > 0:
            next_active = []
            for x, y in active:
                for dx, dy in dxys:
                    x_ = x + dx
                    y_ = y + dy
                    if (not self.visited[x_, y_]) and self.interior[x_, y_]:
                        next_active.append((x_, y_))
                        self.visited[x_, y_] = True
                        self.dist[x_, y_] = self.dist[x, y] + 1
                        self.dx[x_, y_] = -dx
                        self.dy[x_, y_] = -dy
            active = next_active

    # Given a bool array, return (x, y) where goal[x, y] = True and (x, y) is the
    # closest such
    # dist, dx, and dy will be valid along the shortest path from (x0, y0) to (x, y)
    # Return None if no accessible True element of goal
    def nearest_in_array(self, x0, y0, goal):
        x0 += 1
        y0 += 1
        self.dist[x0, y0] = 0
        self.visited.fill(False)
        self.visited[x0, y0] = True

        active = [(x0, y0)]
        while len(active) > 0:
            next_active = []
            for x, y in active:
                if goal[x - 1, y - 1]:
                    return (x - 1, y - 1)
                for dx, dy in dxys:
                    x_ = x + dx
                    y_ = y + dy
                    if (not self.visited[x_, y_]) and self.interior[x_, y_]:
                        next_active.append((x_, y_))
                        self.visited[x_, y_] = True
                        self.dist[x_, y_] = self.dist[x, y] + 1
                        self.dx[x_, y_] = -dx
                        self.dy[x_, y_] = -dy
            active = next_active

    # Same as nearest_in_array, but the goal points are given as a set or list
    def nearest_in_set(self, x0, y0, goal):
        x0 += 1
        y0 += 1
        self.dist[x0, y0] = 0
        self.visited.fill(False)
        self.visited[x0, y0] = True

        active = [(x0, y0)]
        while len(active) > 0:
            next_active = []
            for x, y in active:
                if (x - 1, y - 1) in goal:
                    return (x - 1, y - 1)
                for dx, dy in dxys:
                    x_ = x + dx
                    y_ = y + dy
                    if (not self.visited[x_, y_]) and self.interior[x_, y_]:
                        next_active.append((x_, y_))
                        self.visited[x_, y_] = True
                        self.dist[x_, y_] = self.dist[x, y] + 1
                        self.dx[x_, y_] = -dx
                        self.dy[x_, y_] = -dy
            active = next_active

    # After already performing a search starting from (x0, y0) that found the
    # point (x1, y1), this makes a shortest path from one to the other
    def compute_path(self, x0, y0, x1, y1):
        x = x1
        y = y1
        path = [(x, y)]

        while not ((x == x0) and (y == y0)):
            x_ = x + self.dx[x + 1, y + 1]
            y_ = y + self.dy[x + 1, y + 1]
            x = x_
            y = y_
            path.append((x, y))

        return list(reversed(path))
