"""V13: Column-major traversal — iterates columns then rows (cache-unfriendly)."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for col in range(width):
        cx = x_min + (x_max - x_min) * col / (width - 1)
        for row in range(height):
            cy = y_min + (y_max - y_min) * row / (height - 1)
            zx, zy = 0.0, 0.0
            iteration = 0
            while zx * zx + zy * zy <= 4.0 and iteration < max_iter:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                iteration += 1
            result[row, col] = iteration
    return result
