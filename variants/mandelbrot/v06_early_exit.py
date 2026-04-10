"""V06: Cardioid/bulb pre-check + period-2 detection for early exit."""

import numpy as np


def _in_cardioid_or_bulb(cx, cy):
    # Main cardioid check
    q = (cx - 0.25) ** 2 + cy * cy
    if q * (q + (cx - 0.25)) <= 0.25 * cy * cy:
        return True
    # Period-2 bulb check
    if (cx + 1.0) ** 2 + cy * cy <= 0.0625:
        return True
    return False


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            if _in_cardioid_or_bulb(cx, cy):
                result[row, col] = max_iter
                continue
            zx = 0.0
            zy = 0.0
            iteration = 0
            while zx * zx + zy * zy <= 4.0 and iteration < max_iter:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                iteration += 1
            result[row, col] = iteration
    return result
