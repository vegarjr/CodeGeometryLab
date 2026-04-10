"""V15: Uses enumerate and zip with linspace for Pythonic iteration."""

import numpy as np


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    xs = np.linspace(x_min, x_max, width)
    ys = np.linspace(y_min, y_max, height)
    result = np.zeros((height, width), dtype=np.int32)

    for r, cy in enumerate(ys):
        for c, cx in enumerate(xs):
            zx, zy = 0.0, 0.0
            iteration = 0
            while zx * zx + zy * zy <= 4.0 and iteration < max_iter:
                tmp = zx * zx - zy * zy + cx
                zy = 2.0 * zx * zy + cy
                zx = tmp
                iteration += 1
            result[r, c] = iteration
    return result
