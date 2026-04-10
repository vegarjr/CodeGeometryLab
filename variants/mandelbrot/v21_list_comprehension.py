"""V21: List comprehension with nested helper — expression-oriented style."""

import numpy as np


def _escape(cx, cy, max_iter):
    zx, zy = 0.0, 0.0
    for i in range(max_iter):
        if zx * zx + zy * zy > 4.0:
            return i
        tmp = zx * zx - zy * zy + cx
        zy = 2.0 * zx * zy + cy
        zx = tmp
    return max_iter


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    rows = [
        [
            _escape(
                x_min + (x_max - x_min) * col / (width - 1),
                y_min + (y_max - y_min) * row / (height - 1),
                max_iter,
            )
            for col in range(width)
        ]
        for row in range(height)
    ]
    return np.array(rows, dtype=np.int32)
