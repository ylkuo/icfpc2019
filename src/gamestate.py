import numpy as np

import compute_interior

class State:
    def __init__(self, task):
        self.task = task
        self.X = task.xmax
        self.Y = task.ymax

        self.interior = compute_interior.interior_with_obstacles(task.map, task.obstacles, self.X, self.Y)
