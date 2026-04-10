"""V09: Map/reduce style with pure functions, no mutation."""

import numpy as np


def _make_grid(x_min, x_max, y_min, y_max, width, height):
    xs = [x_min + (x_max - x_min) * c / (width - 1) for c in range(width)]
    ys = [y_min + (y_max - y_min) * r / (height - 1) for r in range(height)]
    return [(r, c, xs[c], ys[r]) for r in range(height) for c in range(width)]


def _iterate_once(state):
    zx, zy, cx, cy, iteration, escaped = state
    if escaped:
        return state
    new_zx = zx * zx - zy * zy + cx
    new_zy = 2.0 * zx * zy + cy
    new_escaped = (new_zx * new_zx + new_zy * new_zy) > 4.0
    return (new_zx, new_zy, cx, cy, iteration + 1, new_escaped)


def _compute_pixel(args):
    _, _, cx, cy, max_iter = args
    state = (0.0, 0.0, cx, cy, 0, False)
    for _ in range(max_iter):
        state = _iterate_once(state)
        if state[5]:  # escaped
            break
    return state[4]  # iteration count


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    grid = _make_grid(x_min, x_max, y_min, y_max, width, height)
    tasks = [(r, c, cx, cy, max_iter) for r, c, cx, cy in grid]
    counts = list(map(_compute_pixel, tasks))
    result = np.array(counts, dtype=np.int32).reshape(height, width)
    return result
