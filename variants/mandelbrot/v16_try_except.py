"""V16: Uses exception for escape detection — exception-driven control flow."""

import numpy as np


class Escaped(Exception):
    def __init__(self, iteration):
        self.iteration = iteration


def _iterate(cx, cy, max_iter):
    zx, zy = 0.0, 0.0
    for i in range(max_iter):
        if zx * zx + zy * zy > 4.0:
            raise Escaped(i)
        tmp = zx * zx - zy * zy + cx
        zy = 2.0 * zx * zy + cy
        zx = tmp
    return max_iter


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            try:
                result[row, col] = _iterate(cx, cy, max_iter)
            except Escaped as e:
                result[row, col] = e.iteration
    return result
