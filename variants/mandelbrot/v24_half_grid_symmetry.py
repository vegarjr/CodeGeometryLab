"""V24: Exploits vertical symmetry — computes only top half, mirrors to bottom."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    half = (height + 1) // 2  # compute top half + middle row

    for row in range(half):
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
            result[row, col] = iteration
            # Mirror to bottom half
            mirror_row = height - 1 - row
            if mirror_row != row:
                result[mirror_row, col] = iteration

    return result
