"""V03: Recursive function for iteration (depth = escape count)."""

import sys
import numpy as np

_ORIGINAL_LIMIT = sys.getrecursionlimit()


def _recurse(zx, zy, cx, cy, iteration, max_iter):
    if zx * zx + zy * zy > 4.0 or iteration >= max_iter:
        return iteration
    new_zx = zx * zx - zy * zy + cx
    new_zy = 2.0 * zx * zy + cy
    return _recurse(new_zx, new_zy, cx, cy, iteration + 1, max_iter)


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    sys.setrecursionlimit(max(max_iter + 50, _ORIGINAL_LIMIT))
    try:
        result = np.zeros((height, width), dtype=np.int32)
        for row in range(height):
            cy = y_min + (y_max - y_min) * row / (height - 1)
            for col in range(width):
                cx = x_min + (x_max - x_min) * col / (width - 1)
                result[row, col] = _recurse(0.0, 0.0, cx, cy, 0, max_iter)
        return result
    finally:
        sys.setrecursionlimit(_ORIGINAL_LIMIT)
