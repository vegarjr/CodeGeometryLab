"""V19: Uses sentinel value (-1) to mark completed pixels in a flat iteration."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    n_pixels = height * width
    cx = np.empty(n_pixels)
    cy = np.empty(n_pixels)
    for row in range(height):
        y_val = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            idx = row * width + col
            cx[idx] = x_min + (x_max - x_min) * col / (width - 1)
            cy[idx] = y_val

    zx = np.zeros(n_pixels)
    zy = np.zeros(n_pixels)
    result = np.full(n_pixels, -1, dtype=np.int32)  # sentinel: -1 = not done

    for i in range(max_iter):
        active = result == -1
        if not active.any():
            break
        # Update active pixels
        new_zx = zx[active] * zx[active] - zy[active] * zy[active] + cx[active]
        new_zy = 2.0 * zx[active] * zy[active] + cy[active]
        zx[active] = new_zx
        zy[active] = new_zy
        # Check escape
        escaped = (zx * zx + zy * zy) > 4.0
        newly_done = escaped & (result == -1)
        result[newly_done] = i + 1

    # Remaining pixels reached max_iter
    result[result == -1] = max_iter
    return result.reshape(height, width)
