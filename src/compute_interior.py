import numpy as np

# points is a list of (x, y) points with
# 0 <= x <= X
# 0 <= y <= Y
# returns a boolean array of size (X, Y)
# where the points on the interior are marked True
# (interior is left)
def interior(points, X, Y):
    delta = np.zeros((X + 1, Y), dtype = int)
    N = len(points)
    assert N >= 4
    points.append(points[0])
    for i in range(N):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        assert (x1 == x2) != (y1 == y2)

        # We only need to look at vertical walls
        if x1 == x2:
            if y2 > y1:
                for y in range(y1, y2):
                    assert int(delta[x1, y]) == 0
                    delta[x1, y] = -1
            else:
                for y in range(y2, y1):
                    assert int(delta[x1, y]) == 0
                    delta[x1, y] = 1

    result = np.cumsum(delta, axis = 0)
    assert np.all(np.isin(result, (0, 1)))
    assert np.all(result[X, :] == 0)
    return result[:X, :] == 1

def interior_with_obstacles(map, obstacles, X, Y):
    i = interior(map, X, Y)
    for o in obstacles:
        i = i & (~interior(o, X, Y))
    return i
