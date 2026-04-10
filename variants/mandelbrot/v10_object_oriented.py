"""V10: MandelbrotComputer class with state encapsulation."""

import numpy as np


class MandelbrotComputer:
    def __init__(self, x_min, x_max, y_min, y_max, width, height, max_iter):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.width = width
        self.height = height
        self.max_iter = max_iter
        self._result = None

    def _pixel_to_complex(self, row, col):
        cx = self.x_min + (self.x_max - self.x_min) * col / (self.width - 1)
        cy = self.y_min + (self.y_max - self.y_min) * row / (self.height - 1)
        return cx, cy

    def _compute_escape(self, cx, cy):
        zx = 0.0
        zy = 0.0
        for iteration in range(self.max_iter):
            if zx * zx + zy * zy > 4.0:
                return iteration
            tmp = zx * zx - zy * zy + cx
            zy = 2.0 * zx * zy + cy
            zx = tmp
        return self.max_iter

    def _compute_row(self, row):
        row_result = np.zeros(self.width, dtype=np.int32)
        for col in range(self.width):
            cx, cy = self._pixel_to_complex(row, col)
            row_result[col] = self._compute_escape(cx, cy)
        return row_result

    def run(self):
        self._result = np.zeros((self.height, self.width), dtype=np.int32)
        for row in range(self.height):
            self._result[row] = self._compute_row(row)
        return self._result

    @property
    def result(self):
        return self._result


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    computer = MandelbrotComputer(x_min, x_max, y_min, y_max, width, height, max_iter)
    return computer.run()
