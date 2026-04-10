"""Real outcome metrics: runtime, scaling, stability."""

import time
import numpy as np


def measure_runtime(compute_fn, params, n_runs=30):
    """Measure wall-clock runtime over n_runs (no tracing overhead)."""
    times = []
    for _ in range(n_runs):
        t0 = time.monotonic()
        compute_fn(**params)
        t1 = time.monotonic()
        times.append(t1 - t0)

    times = np.array(times)
    return {
        "runtime_mean_s": float(np.mean(times)),
        "runtime_std_s": float(np.std(times)),
        "runtime_min_s": float(np.min(times)),
        "runtime_median_s": float(np.median(times)),
        "runtime_cv": float(np.std(times) / np.mean(times)) if np.mean(times) > 0 else 0.0,
    }


def measure_scaling(compute_fn, base_params, sizes=(200, 500, 1000), n_runs=5):
    """Measure runtime scaling across input sizes.

    Scales both width and height proportionally.
    Returns scaling metrics including estimated scaling exponent.
    """
    results = {}
    log_sizes = []
    log_times = []

    for size in sizes:
        params = dict(base_params)
        params["width"] = size
        params["height"] = size

        times = []
        for _ in range(n_runs):
            t0 = time.monotonic()
            compute_fn(**params)
            t1 = time.monotonic()
            times.append(t1 - t0)

        median_time = float(np.median(times))
        results[f"scaling_{size}_median_s"] = median_time
        if median_time > 0:
            log_sizes.append(np.log(size))
            log_times.append(np.log(median_time))

    # Fit scaling exponent: time ~ size^alpha
    if len(log_sizes) >= 2:
        coeffs = np.polyfit(log_sizes, log_times, 1)
        results["scaling_exponent"] = float(coeffs[0])
    else:
        results["scaling_exponent"] = float("nan")

    return results


def measure_stability(compute_fn, params, n_runs=30):
    """Measure run-to-run stability (variance in runtime).

    Lower CV = more stable.
    """
    times = []
    for _ in range(n_runs):
        t0 = time.monotonic()
        compute_fn(**params)
        t1 = time.monotonic()
        times.append(t1 - t0)

    times = np.array(times)
    # Remove warmup (first 3 runs)
    if len(times) > 5:
        times = times[3:]

    return {
        "stability_cv": float(np.std(times) / np.mean(times)) if np.mean(times) > 0 else 0.0,
        "stability_iqr_s": float(np.percentile(times, 75) - np.percentile(times, 25)),
    }
