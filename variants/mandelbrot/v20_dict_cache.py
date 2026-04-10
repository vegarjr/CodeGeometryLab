"""V20: Caches results in a dict keyed by (row, col) — dictionary-driven storage."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    cache = {}
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            zx, zy = 0.0, 0.0
            iteration = 0
            while zx * zx + zy * zy <= 4.0 and iteration < max_iter:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                iteration += 1
            cache[(row, col)] = iteration

    result = np.zeros((height, width), dtype=np.int32)
    for (row, col), val in cache.items():
        result[row, col] = val
    return result
