"""V25: Explicit state machine — each pixel transitions through states."""

import numpy as np

STATE_ITERATING = 0
STATE_ESCAPED = 1
STATE_MAXED = 2


def _step_pixel(zx, zy, cx, cy, iteration, max_iter):
    """Returns (new_zx, new_zy, new_iteration, state)."""
    if zx * zx + zy * zy > 4.0:
        return zx, zy, iteration, STATE_ESCAPED
    if iteration >= max_iter:
        return zx, zy, iteration, STATE_MAXED
    new_zx = zx * zx - zy * zy + cx
    new_zy = 2.0 * zx * zy + cy
    return new_zx, new_zy, iteration + 1, STATE_ITERATING


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            zx, zy, iteration, state = 0.0, 0.0, 0, STATE_ITERATING
            while state == STATE_ITERATING:
                zx, zy, iteration, state = _step_pixel(zx, zy, cx, cy, iteration, max_iter)
            result[row, col] = iteration
    return result
