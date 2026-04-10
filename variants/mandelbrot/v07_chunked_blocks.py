"""V07: Block-tiled processing with configurable chunk size."""

import numpy as np

CHUNK_SIZE = 32


def _compute_block(cx_block, cy_block, max_iter):
    shape = cx_block.shape
    zx = np.zeros(shape)
    zy = np.zeros(shape)
    result = np.full(shape, max_iter, dtype=np.int32)

    for i in range(max_iter):
        mask = (zx * zx + zy * zy) <= 4.0
        if not mask.any():
            break
        new_zx = zx[mask] * zx[mask] - zy[mask] * zy[mask] + cx_block[mask]
        new_zy = 2.0 * zx[mask] * zy[mask] + cy_block[mask]
        zx[mask] = new_zx
        zy[mask] = new_zy
        escaped = (zx * zx + zy * zy) > 4.0
        newly_escaped = escaped & (result == max_iter)
        result[newly_escaped] = i + 1

    return result


def compute(x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    cx_full, cy_full = np.meshgrid(x, y)
    result = np.zeros((height, width), dtype=np.int32)

    for r0 in range(0, height, CHUNK_SIZE):
        r1 = min(r0 + CHUNK_SIZE, height)
        for c0 in range(0, width, CHUNK_SIZE):
            c1 = min(c0 + CHUNK_SIZE, width)
            result[r0:r1, c0:c1] = _compute_block(
                cx_full[r0:r1, c0:c1],
                cy_full[r0:r1, c0:c1],
                max_iter,
            )

    return result
