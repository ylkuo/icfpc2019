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
        self.x, self.y = position
        self.time = time
        self.cmds = []

        self.parent = parent
        if parent is None:
            self.worker_id = [time]
        else:
            self.worker_id = [time] + parent.worker_id
        self.gs.add_worker(self)

        self.speed_expires = -1
        self.drill_expires = -1

        self.pf = Pathfinder(self.gs)

        self.direction = 1
        self.arms = [
                    [(0, 0), (-1, 1), (0, 1), (1, 1)],
                    [(0, 0), (1, 1), (1, 0), (1, -1)],
                    [(0, 0), (1, -1), (0, -1), (-1, -1)],
                    [(0, 0), (-1, -1), (-1, 0), (-1, 1)]
                ]

        self.paint()

        self.cmd2fun = {
                    'B' : None,
                    'F' : self.speed,
                    'L' : self.drill,
                    'R' : None,
                    'T' : None,
                    'C' : self.clone,
                    'W' : self.move_up,
                    'D' : self.move_right,
                    'S' : self.move_down,
                    'A' : self.move_left,
                    'Z' : self.wait,
                    'Q' : self.rotate_Q,
                    'E' : self.rotate_E
                }

    # Given a string, call the appropriate function to execute that command
    def act(self, cmd):
        self.cmd2fun[cmd]()

    def do(self, cmd):
        self.cmds.append(cmd)
        self.time += 1

    def paint(self):
        if self.gs.has_boosters[self.x, self.y]:
            self.gs.collect_boosters(self.x, self.y, self.time + 1)

        for dx, dy in self.arms[self.direction]:
            x_ = self.x + dx
            y_ = self.y + dy
            if x_ >= 0 and x_ < self.gs.X and y_ >= 0 and y_ < self.gs.Y:
                self.gs.unpainted[x_, y_] = False

    def is_booster_available(self, bt):
        return self.gs.is_booster_available(bt, self.time)

    def use_booster(self, bt):
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

    def wait(self):
        self.move(0, 0)

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

    def compute_distance(self):
        self.pf.compute_distance(self.x, self.y)

    def nearest_in_array(self, goal):
        return self.pf.nearest_in_array(self.x, self.y, goal)

    def nearest_in_set(self, goal):
        return self.pf.nearest_in_set(self.x, self.y, goal)

    def compute_path(self, x, y):
        return self.pf.compute_path(self.x, self.y, x, y)

    def walk_path_to(self, x, y):
        path = self.pf.compute_path(self.x, self.y, x, y)
        for x_, y_ in path[1:]:
            self.move(x_ - self.x, y_ - self.y)

    def walk_path_to_max(self, x, y, maxsteps):
        path = self.pf.compute_path(self.x, self.y, x, y)
        for x_, y_ in path[1:maxsteps + 1]:
            self.move(x_ - self.x, y_ - self.y)
        return (self.x == x) and (self.y == y)

class State:
    def __init__(self, t):
        self.task = t
        self.X = t.xmax
        self.Y = t.ymax

        self.spawn_list = list(t.bt2pos[X])

        self.interior = compute_interior.interior_with_obstacles(t.map, t.obstacles, self.X, self.Y)
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

        self.boosters[C] = [-1] * self.task.extra_clones

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

    def add_worker(self, w):
        self.workers.append(w)
        self.workers.sort(key = lambda w : w.worker_id)

    # Return the worker that is currently at the oldest time
    def oldest_worker(self):
        time = min([w.time for w in self.workers])
        for w in self.workers:
            if w.time == time:
                return w

    def time(self):
        return max([w.time for w in self.workers])

    def to_string(self):
        self.workers.sort(key = lambda w : w.worker_id)
        return '#'.join((''.join(w.cmds)) for w in self.workers)

    def to_file(self, filename):
        s = self.to_string()
        with open(filename, 'w') as f:
            f.write(s)

    # Restarts the simulation from the beginning with proper interleaving of the workers in sync
    # Truncates simulation as soon as everything has been painted
    # Validates that everything is painted at the end
    def replay_and_validate(self):
        self.workers.sort(key = lambda w : w.worker_id)

        idx = [0] * len(self.workers)

        gs = State(self.task)
        gs.start()

        while True:
            flag = False
            ws = gs.workers
            for i, w in enumerate(ws):
                if idx[i] < len(self.workers[i].cmds):
                    flag = True
                    w.act(self.workers[i].cmds[idx[i]])
                    idx[i] += 1

            if not np.any(gs.unpainted):
                return gs

            assert flag

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

    def all_nearest_in_array(self, x0, y0, goal):
        x0 += 1
        y0 += 1
        self.dist[x0, y0] = 0
        self.visited.fill(False)
        self.visited[x0, y0] = True

        active = [(x0, y0)]
        result = []
        while len(active) > 0 and len(result) == 0:
            next_active = []
            for x, y in active:
                if goal[x - 1, y - 1]:
                    result.append((x - 1, y - 1))
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

        return result

    # Going to a square with a lower value of "noncentrality" is a step cost of
    # cost_inward, otherwise 1.
    def nearest_in_array_with_bias(self, x0, y0, goal, noncentrality, cost_inward = 3):
        inf = 2 * (np.size(self.dist) + 10)
        x0 += 1
        y0 += 1
        self.dist.fill(inf)
        self.dist[x0, y0] = 0
        self.visited.fill(False)

        cur_dist = 0

        active = [(x0, y0)]
        result = []
        while len(active) > 0:
            next_active = []
            for x, y in active:
                if self.dist[x, y] > cur_dist:
                    next_active.append((x, y))
                    continue
                assert self.dist[x, y] == cur_dist

                if goal[x - 1, y - 1]:
                    return (x - 1, y - 1)
                for dx, dy in dxys:
                    x_ = x + dx
                    y_ = y + dy
                    if self.interior[x_, y_]:
                        if noncentrality[x_ - 1, y_ - 1] < noncentrality[x - 1, y - 1]:
                            dist_ = cur_dist + cost_inward
                        else:
                            dist_ = cur_dist + 1

                        if self.dist[x_, y_] == inf:
                            next_active.append((x_, y_))

                        if self.dist[x_, y_] > dist_:
                            self.dist[x_, y_] = dist_
                            self.dx[x_, y_] = -dx
                            self.dy[x_, y_] = -dy

            active = next_active
            cur_dist += 1

        return result

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

class RegionManager:
    def __init__(self, gs):
        self.gs = gs
        self.X = gs.X; self.Y = gs.Y

        self.regions = np.zeros((self.X, self.Y), dtype=int)
    
    def compute_regions(self):
        new_rid = 1
        for x in range(self.X):
            for y in range(self.Y):
                if not self.gs.interior[x,y]:
                    continue
                rid = new_rid
                for dx, dy in [(-1, 0), (0, -1)]:
                    x_ = x + dx
                    y_ = y + dy
                    if x_ >= 0 and x_ < self.X and y_ >= 0 and y_ < self.Y and \
                        self.gs.interior[x_, y_]:
                        rid = self.regions[x_, y_]
                        break
                if rid == new_rid:
                    new_rid += 1
                self.regions[x, y] = rid

    def get_region(self, rid):
        return np.logical_and(self.regions == rid, self.gs.unpainted)

    def to_string(self):
        rows = []
        for y in range(self.Y):
            row = []
            for x in range(self.X):
                if self.regions[x,y] == 0:
                    row.append('##')
                else:
                    row.append(str(self.regions[x,y]).zfill(2))
            rows.append(''.join(row))
        return '\n'.join(rows)
