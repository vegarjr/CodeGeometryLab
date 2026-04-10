"""V18: NumPy vectorized using native complex128 dtype."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    C = x[np.newaxis, :] + 1j * y[:, np.newaxis]

    Z = np.zeros_like(C)
    result = np.full((height, width), max_iter, dtype=np.int32)

    for i in range(max_iter):
        mask = np.abs(Z) <= 2.0
        if not mask.any():
            break
        Z[mask] = Z[mask] ** 2 + C[mask]
        escaped = np.abs(Z) > 2.0
        newly_escaped = escaped & (result == max_iter)
        result[newly_escaped] = i + 1

    return result
