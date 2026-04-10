"""V05: Row-at-a-time vectorization (hybrid loop/vector)."""

import numpy as np


def _compute_row(cx_row, cy_val, max_iter):
    width = len(cx_row)
    zx = np.zeros(width)
    zy = np.zeros(width)
    result = np.full(width, max_iter, dtype=np.int32)

    for i in range(max_iter):
        mask = (zx * zx + zy * zy) <= 4.0
        if not mask.any():
            break
        new_zx = zx[mask] * zx[mask] - zy[mask] * zy[mask] + cx_row[mask]
        new_zy = 2.0 * zx[mask] * zy[mask] + cy_val
        zx[mask] = new_zx
        zy[mask] = new_zy
        escaped = (zx * zx + zy * zy) > 4.0
        newly_escaped = escaped & (result == max_iter)
        result[newly_escaped] = i + 1

    return result


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    cx_row = np.linspace(x_min, x_max, width)
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy_val = y_min + (y_max - y_min) * row / (height - 1)
        result[row] = _compute_row(cx_row, cy_val, max_iter)
    return result
