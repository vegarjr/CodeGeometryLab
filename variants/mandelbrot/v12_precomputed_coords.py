"""V12: Pre-compute all coordinates into arrays, then iterate separately."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    # Pre-compute coordinate arrays
    cx_arr = np.empty((height, width))
    cy_arr = np.empty((height, width))
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx_arr[row, col] = x_min + (x_max - x_min) * col / (width - 1)
            cy_arr[row, col] = cy

    # Iterate using pre-computed coords
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        for col in range(width):
            cx = cx_arr[row, col]
            cy = cy_arr[row, col]
            zx, zy = 0.0, 0.0
            for i in range(max_iter):
                if zx * zx + zy * zy > 4.0:
                    result[row, col] = i
                    break
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
            else:
                result[row, col] = max_iter
    return result
