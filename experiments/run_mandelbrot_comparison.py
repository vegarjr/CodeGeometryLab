"""Main experiment: compare 10 Mandelbrot variants across all metric types.

Runs the full pipeline:
1. Correctness gate
2. Runtime benchmarking (no tracing overhead)
3. Instrumented tracing
4. Geometric metrics
5. Baseline metrics
6. Scaling analysis
7. Correlation analysis
8. Save all results
"""

import json
import os
import sys
import time
from datetime import datetime

import numpy as np
from scipy import stats

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks.mandelbrot_task import (
    REFERENCE_PARAMS,
    VARIANT_NAMES,
    VARIANT_MODULES,
    correctness_gate,
    load_variants,
)
from instrumentation.tracer import trace_variant
from metrics.geometric_metrics import compute_all_geometric_metrics
from metrics.outcome_metrics import measure_runtime, measure_scaling, measure_stability
from metrics.baselines import compute_all_baselines, compute_trace_baselines


def run_experiment(
    n_benchmark_runs=30,
    n_scaling_runs=5,
    scaling_sizes=(200, 500, 1000),
    trace_grid_size=50,
    trajectory_points=100,
):
    """Run the full experiment pipeline."""
    start_time = time.monotonic()
    print("=" * 70)
    print("CODE GEOMETRY LAB — Mandelbrot Variant Comparison")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # ---- Phase 1: Correctness Gate ----
    print("\n[Phase 1] Correctness Gate")
    gate_report = correctness_gate(verbose=True)
    valid_variants = [name for name, r in gate_report.items() if r["passed"]]
    print(f"\n{len(valid_variants)} variants passed. Proceeding with those.\n")

    # ---- Phase 2: Runtime Benchmarking (clean, no tracing) ----
    print("[Phase 2] Runtime Benchmarking (no tracing overhead)")
    variants = load_variants()
    runtime_results = {}
    for name, compute_fn in variants:
        if name not in valid_variants:
            continue
        print(f"  Benchmarking {name}...", end=" ", flush=True)
        rt = measure_runtime(compute_fn, REFERENCE_PARAMS, n_runs=n_benchmark_runs)
        stability = measure_stability(compute_fn, REFERENCE_PARAMS, n_runs=n_benchmark_runs)
        rt.update(stability)
        runtime_results[name] = rt
        print(f"mean={rt['runtime_mean_s']:.4f}s, cv={rt['runtime_cv']:.3f}")

    # ---- Phase 3: Scaling Analysis ----
    print("\n[Phase 3] Scaling Analysis")
    scaling_results = {}
    base_params = dict(REFERENCE_PARAMS)
    for name, compute_fn in variants:
        if name not in valid_variants:
            continue
        print(f"  Scaling {name}...", end=" ", flush=True)
        sc = measure_scaling(compute_fn, base_params, sizes=scaling_sizes, n_runs=n_scaling_runs)
        scaling_results[name] = sc
        print(f"exponent={sc['scaling_exponent']:.2f}")

    # ---- Phase 4: Instrumented Tracing ----
    print("\n[Phase 4] Instrumented Tracing")
    # Use smaller grid for tracing to keep event counts manageable
    trace_params = dict(REFERENCE_PARAMS)
    trace_params["width"] = trace_grid_size
    trace_params["height"] = trace_grid_size

    trace_records = {}
    for name, compute_fn in variants:
        if name not in valid_variants:
            continue
        # Find the source file for this variant
        module_parts = name  # e.g., "v01_naive_loop"
        target_file = module_parts
        print(f"  Tracing {name}...", end=" ", flush=True)
        _, record = trace_variant(name, compute_fn, trace_params, target_file=target_file)
        trace_records[name] = record
        d = record.to_dict()
        print(f"events={d['total_events']}, calls={d['total_calls']}, max_depth={d['max_call_depth']}")

    # ---- Phase 5: Geometric Metrics ----
    print("\n[Phase 5] Geometric Metrics")
    geometric_results = {}
    for name, record in trace_records.items():
        print(f"  Computing geometry for {name}...", end=" ", flush=True)
        gm = compute_all_geometric_metrics(record, trajectory_points=trajectory_points)
        geometric_results[name] = gm
        print(f"{len(gm)} metrics computed")

    # ---- Phase 6: Baseline Metrics ----
    print("\n[Phase 6] Baseline Metrics")
    baseline_results = {}
    for name, module_path in zip(VARIANT_NAMES, VARIANT_MODULES):
        if name not in valid_variants:
            continue
        bl = compute_all_baselines(module_path)
        # Add trace baselines
        if name in trace_records:
            bl.update(compute_trace_baselines(trace_records[name]))
        baseline_results[name] = bl
        print(f"  {name}: lines={bl['baseline_line_count']}, "
              f"cc={bl['baseline_cyclomatic_complexity']}, "
              f"ast={bl['baseline_ast_node_count']}")

    # ---- Phase 7: Build Combined Table ----
    print("\n[Phase 7] Building Combined Metrics Table")
    combined = {}
    for name in valid_variants:
        combined[name] = {}
        if name in runtime_results:
            combined[name].update(runtime_results[name])
        if name in scaling_results:
            combined[name].update(scaling_results[name])
        if name in geometric_results:
            combined[name].update(geometric_results[name])
        if name in baseline_results:
            combined[name].update(baseline_results[name])

    # ---- Phase 8: Correlation Analysis ----
    print("\n[Phase 8] Correlation Analysis")

    # Target outcomes to correlate against
    outcome_keys = [
        "runtime_mean_s",
        "runtime_cv",
        "scaling_exponent",
        "stability_cv",
    ]

    # Get all metric keys (geometric + baseline)
    all_metric_keys = set()
    for name in valid_variants:
        all_metric_keys.update(combined[name].keys())
    # Remove outcome keys and non-numeric
    predictor_keys = sorted([
        k for k in all_metric_keys
        if k not in outcome_keys
        and k not in ("all_times_s", "variant_name")
        and not k.startswith("runtime_")
        and not k.startswith("stability_")
        and not k.startswith("scaling_")
    ])

    correlations = {}
    for outcome in outcome_keys:
        outcome_vals = []
        for name in valid_variants:
            val = combined[name].get(outcome)
            if val is not None and not (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                outcome_vals.append((name, val))

        if len(outcome_vals) < 4:
            continue

        names_ordered = [v[0] for v in outcome_vals]
        y = np.array([v[1] for v in outcome_vals])

        for pred_key in predictor_keys:
            x_vals = []
            y_vals = []
            for name, yv in outcome_vals:
                xv = combined[name].get(pred_key)
                if xv is not None and not (isinstance(xv, float) and (np.isnan(xv) or np.isinf(xv))):
                    x_vals.append(xv)
                    y_vals.append(yv)

            if len(x_vals) < 4:
                continue

            x = np.array(x_vals)
            y_sub = np.array(y_vals)

            # Skip if no variance
            if np.std(x) < 1e-12 or np.std(y_sub) < 1e-12:
                continue

            rho, p_value = stats.spearmanr(x, y_sub)
            if not np.isnan(rho):
                correlations.setdefault(outcome, []).append({
                    "predictor": pred_key,
                    "spearman_rho": float(rho),
                    "p_value": float(p_value),
                    "n": len(x_vals),
                })

    # Sort correlations by absolute rho
    for outcome in correlations:
        correlations[outcome].sort(key=lambda c: abs(c["spearman_rho"]), reverse=True)

    # ---- Print Top Correlations ----
    print("\nTop correlations (|rho| > 0.5):")
    print("-" * 80)
    significant_found = False
    for outcome in outcome_keys:
        if outcome not in correlations:
            continue
        for corr in correlations[outcome]:
            if abs(corr["spearman_rho"]) > 0.5:
                significant_found = True
                sig = "*" if corr["p_value"] < 0.05 else ""
                geo_tag = "[GEO]" if not corr["predictor"].startswith("baseline_") else "[BASE]"
                print(f"  {geo_tag} {corr['predictor']:45s} vs {outcome:20s} "
                      f"rho={corr['spearman_rho']:+.3f} p={corr['p_value']:.4f}{sig}")

    if not significant_found:
        print("  No correlations with |rho| > 0.5 found.")

    # ---- Phase 9: Ranking Table ----
    print("\n[Phase 9] Variant Ranking by Runtime")
    print("-" * 70)
    ranked = sorted(valid_variants, key=lambda n: runtime_results[n]["runtime_mean_s"])
    print(f"{'Rank':<5} {'Variant':<25} {'Mean(s)':<10} {'CV':<8} {'Scale Exp':<10}")
    for rank, name in enumerate(ranked, 1):
        rt = runtime_results[name]
        sc = scaling_results[name]
        print(f"{rank:<5} {name:<25} {rt['runtime_mean_s']:<10.4f} "
              f"{rt['runtime_cv']:<8.3f} {sc['scaling_exponent']:<10.2f}")

    # ---- Save Results ----
    elapsed = time.monotonic() - start_time
    print(f"\nTotal experiment time: {elapsed:.1f}s")

    results = {
        "experiment": "mandelbrot_variant_comparison_mvp",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_benchmark_runs": n_benchmark_runs,
            "n_scaling_runs": n_scaling_runs,
            "scaling_sizes": list(scaling_sizes),
            "trace_grid_size": trace_grid_size,
            "trajectory_points": trajectory_points,
            "reference_params": REFERENCE_PARAMS,
        },
        "correctness": {name: {"passed": r["passed"]} for name, r in gate_report.items()},
        "runtime": runtime_results,
        "scaling": scaling_results,
        "geometric": {k: {mk: mv for mk, mv in v.items()} for k, v in geometric_results.items()},
        "baselines": baseline_results,
        "correlations": correlations,
        "ranking_by_runtime": ranked,
        "elapsed_s": elapsed,
    }

    # Remove non-serializable fields
    for name in results["runtime"]:
        if "all_times_s" in results["runtime"][name]:
            del results["runtime"][name]["all_times_s"]

    os.makedirs("results", exist_ok=True)
    result_path = "results/mandelbrot_mvp_results.json"
    with open(result_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {result_path}")

    return results


if __name__ == "__main__":
    results = run_experiment()
