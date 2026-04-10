"""V22: Splits computation into separate real and imaginary helper functions."""

import numpy as np


def _next_real(zx, zy, cx):
    return zx * zx - zy * zy + cx


def _next_imag(zx, zy, cy):
    return 2.0 * zx * zy + cy


def _magnitude_sq(zx, zy):
    return zx * zx + zy * zy


def _escape_time(cx, cy, max_iter):
    zx, zy = 0.0, 0.0
    for i in range(max_iter):
        if _magnitude_sq(zx, zy) > 4.0:
            return i
        new_zx = _next_real(zx, zy, cx)
        new_zy = _next_imag(zx, zy, cy)
        zx, zy = new_zx, new_zy
    return max_iter


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    result = np.zeros((height, width), dtype=np.int32)
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            result[row, col] = _escape_time(cx, cy, max_iter)
    return result
