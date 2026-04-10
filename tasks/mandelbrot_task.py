"""Mandelbrot task definition: reference parameters, correctness gate, variant loading."""

import importlib
import numpy as np

# Reference parameters
REFERENCE_PARAMS = dict(
    x_min=-2.0, x_max=1.0,
    y_min=-1.5, y_max=1.5,
    width=200, height=200,
    max_iter=100,
)

VARIANT_MODULES = [
    "variants.mandelbrot.v01_naive_loop",
    "variants.mandelbrot.v02_complex_class",
    "variants.mandelbrot.v03_recursive",
    "variants.mandelbrot.v04_numpy_vectorized",
    "variants.mandelbrot.v05_numpy_rowwise",
    "variants.mandelbrot.v06_early_exit",
    "variants.mandelbrot.v07_chunked_blocks",
    "variants.mandelbrot.v08_generator_pipeline",
    "variants.mandelbrot.v09_functional_map",
    "variants.mandelbrot.v10_object_oriented",
]

VARIANT_NAMES = [
    "v01_naive_loop",
    "v02_complex_class",
    "v03_recursive",
    "v04_numpy_vectorized",
    "v05_numpy_rowwise",
    "v06_early_exit",
    "v07_chunked_blocks",
    "v08_generator_pipeline",
    "v09_functional_map",
    "v10_object_oriented",
]


def load_variants():
    """Load all variant modules and return list of (name, compute_fn) pairs."""
    variants = []
    for name, module_path in zip(VARIANT_NAMES, VARIANT_MODULES):
        mod = importlib.import_module(module_path)
        variants.append((name, mod.compute))
    return variants


def compute_reference():
    """Compute reference output using v01 (simplest, most readable)."""
    mod = importlib.import_module(VARIANT_MODULES[0])
    return mod.compute(**REFERENCE_PARAMS)


def correctness_gate(verbose=True):
    """Run all variants and verify they produce identical output.

    Returns dict mapping variant name to (passed: bool, result: ndarray or None).
    """
    reference = compute_reference()
    variants = load_variants()
    report = {}

    for name, compute_fn in variants:
        try:
            result = compute_fn(**REFERENCE_PARAMS)
            match = np.array_equal(reference, result)
            report[name] = {"passed": match, "result": result}
            if verbose:
                status = "PASS" if match else "FAIL"
                if not match:
                    diff_count = np.sum(reference != result)
                    max_diff = int(np.max(np.abs(reference.astype(int) - result.astype(int))))
                    print(f"  {name}: {status} ({diff_count} pixels differ, max diff={max_diff})")
                else:
                    print(f"  {name}: {status}")
        except Exception as e:
            report[name] = {"passed": False, "result": None, "error": str(e)}
            if verbose:
                print(f"  {name}: ERROR — {e}")

    passed = [n for n, r in report.items() if r["passed"]]
    failed = [n for n, r in report.items() if not r["passed"]]

    if verbose:
        print(f"\n{len(passed)}/{len(report)} variants passed correctness gate.")
        if failed:
            print(f"Failed: {failed}")

    return report


if __name__ == "__main__":
    print("Running correctness gate...")
    correctness_gate()
