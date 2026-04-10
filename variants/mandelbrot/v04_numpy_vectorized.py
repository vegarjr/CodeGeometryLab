"""V04: Full-grid NumPy vectorization with masked updates."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    cx, cy = np.meshgrid(x, y)

    zx = np.zeros_like(cx)
    zy = np.zeros_like(cy)
    result = np.full((height, width), max_iter, dtype=np.int32)

    for i in range(max_iter):
        mask = (zx * zx + zy * zy) <= 4.0
        if not mask.any():
            break
        new_zx = zx[mask] * zx[mask] - zy[mask] * zy[mask] + cx[mask]
        new_zy = 2.0 * zx[mask] * zy[mask] + cy[mask]
        zx[mask] = new_zx
        zy[mask] = new_zy
        escaped = (zx * zx + zy * zy) > 4.0
        newly_escaped = escaped & (result == max_iter)
        result[newly_escaped] = i + 1

    return result
