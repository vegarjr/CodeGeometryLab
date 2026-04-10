"""V02: Python complex number type with per-pixel function call."""

import numpy as np


def _escape_time(c, max_iter):
    z = 0 + 0j
    for i in range(max_iter):
        if abs(z) > 2.0:
            return i
        z = z * z + c
    return max_iter


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            c = complex(cx, cy)
            result[row, col] = _escape_time(c, max_iter)
    return result
