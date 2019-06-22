import os
import os.path

def parse_point(s):
    a, b = s.strip('()').split(',')
    return (int(a), int(b))

def parse_point_list(s):
    if len(s) == 0:
        return []

    points = []
    xs = s.split(',')
    for i in range(0, len(xs), 2):
        x = int(xs[i].strip('()'))
        y = int(xs[i + 1].strip('()'))
        points.append((x, y))

    return points

########

def parse_map(s):
    return parse_point_list(s)

def parse_starting_point(s):
    return parse_point(s)

def parse_obstacles(s):
    obstacles = []
    if len(s) > 0:
        for x in s.split(';'):
            obstacles.append(parse_point_list(x))
    return obstacles

def parse_boosters(s):
    boosters = []
    if len(s) > 0:
        for x in s.split(';'):
            boosters.append((x[0], parse_point(x[1:])))
    return boosters

task_parsers = [parse_map, parse_starting_point, parse_obstacles, parse_boosters]

#########

class Task:
    def __init__(self, map, start, obstacles, boosters):
        self.map = map
        self.start = start
        self.obstacles = obstacles
        self.boosters = boosters

        self.map_xs = [x for (x, y) in self.map]
        self.map_ys = [y for (x, y) in self.map]
        self.xmax = max(self.map_xs)
        self.xmin = min(self.map_xs)
        self.ymax = max(self.map_ys)
        self.ymin = min(self.map_ys)

        self.task_string = None
        self.filename = None

    # static
    def from_string(s):
        parts = []
        for i, part in enumerate(s.strip().split('#')):
            assert i < len(task_parsers)
            parts.append(task_parsers[i](part))
        assert len(parts) == len(task_parsers)

        self = Task(*parts)
        self.task_string = s
        return self

    # static
    def from_file(filename):
        with open(filename, 'r') as f:
            self = Task.from_string(f.read())
            self.filename = filename
            return self

    def summary(self):
        if self.filename is None:
            filename = '(no file)'
        else:
            filename = os.path.basename(self.filename)

        out = 'Task {}: X ({}, {}), Y ({}, {}), {} obstacles, {} boosters'
        return out.format(filename, self.xmin, self.xmax, self.ymin, self.ymax, len(self.obstacles), len(self.boosters))

def tasks_in_directory(path):
    assert os.path.isdir(path)
    tasks = []
    for filename in os.listdir(path):
        # if filename.startswith('prob-') and filename.endswith('.desc'):
        if filename.endswith('.desc'):
            tasks.append(Task.from_file(os.path.join(path, filename)))

    tasks.sort(key = lambda t : t.filename)
    return tasks

examples = '../tasks/example/'
part1 = '../tasks/part1/'

if __name__ == "__main__":
    import compute_interior
    c = compute_interior.interior

    tasks = tasks_in_directory(examples)
    for t in tasks:
        print(t.summary())
        print(c(t.map, t.xmax, t.ymax))
        print(c(t.obstacles[0], t.xmax, t.ymax))
        print(c(t.obstacles[1], t.xmax, t.ymax))

    # tasks = tasks_in_directory(part1)
    # for t in tasks:
        # print(t.summary())
