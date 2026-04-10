"""V11: while-True with explicit break — different control flow from while-condition."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            zx, zy = 0.0, 0.0
            iteration = 0
            while True:
                if iteration >= max_iter:
                    break
                if zx * zx + zy * zy > 4.0:
                    break
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                iteration += 1
            result[row, col] = iteration
    return result
