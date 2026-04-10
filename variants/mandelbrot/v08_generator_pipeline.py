"""V08: Generator-based lazy evaluation, pulled by consumer."""

import numpy as np


def _pixel_coords(x_min, x_max, y_min, y_max, width, height):
    for row in range(height):
        cy = y_min + (y_max - y_min) * row / (height - 1)
        for col in range(width):
            cx = x_min + (x_max - x_min) * col / (width - 1)
            yield row, col, cx, cy


def _escape_iterations(pixel_stream, max_iter):
    for row, col, cx, cy in pixel_stream:
        zx = 0.0
        zy = 0.0
        iteration = 0
        while zx * zx + zy * zy <= 4.0 and iteration < max_iter:
            tmp = zx * zx - zy * zy + cx
            zy = 2.0 * zx * zy + cy
            zx = tmp
            iteration += 1
        yield row, col, iteration


def _collect(iteration_stream, height, width):
    result = np.zeros((height, width), dtype=np.int32)
    for row, col, iteration in iteration_stream:
        result[row, col] = iteration
    return result


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    pixels = _pixel_coords(x_min, x_max, y_min, y_max, width, height)
    iterations = _escape_iterations(pixels, max_iter)
    return _collect(iterations, height, width)
