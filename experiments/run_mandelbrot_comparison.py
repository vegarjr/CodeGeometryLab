"""Main experiment: compare Mandelbrot variants across all metric types.

Phase 2 pipeline:
1. Correctness gate
2. Runtime benchmarking (no tracing overhead)
3. Scaling analysis
4. Instrumented tracing (at benchmark size — no size confound)
5. Geometric metrics
6. Baseline metrics
7. Correlation analysis with BH-FDR correction
8. Metric redundancy analysis
9. Save all results
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


def benjamini_hochberg(p_values, alpha=0.05):
    """Apply Benjamini-Hochberg FDR correction.

    Args:
        p_values: list of (key, p_value) tuples
        alpha: FDR level

    Returns list of (key, p_value, adjusted_p, significant) tuples,
    sorted by original p_value.
    """
    sorted_pv = sorted(p_values, key=lambda x: x[1])
    m = len(sorted_pv)
    results = []
    for rank, (key, p) in enumerate(sorted_pv, 1):
        adjusted = min(p * m / rank, 1.0)
        results.append((key, p, adjusted, adjusted < alpha))

    # Enforce monotonicity: adjusted p must be non-decreasing from bottom
    for i in range(len(results) - 2, -1, -1):
        key, p, adj, sig = results[i]
        _, _, adj_next, _ = results[i + 1]
        if adj > adj_next:
            results[i] = (key, p, adj_next, adj_next < alpha)

    return results


def run_experiment(
    n_benchmark_runs=30,
    n_scaling_runs=5,
    scaling_sizes=(200, 500, 1000),
    trajectory_points=100,
):
    """Run the full experiment pipeline.

    Phase 2 changes vs MVP:
    - Tracing at same grid size as benchmarking (no size confound)
    - Event cap raised to 2M, capped traces flagged
    - BH-FDR correction on all correlation tests
    """
    start_time = time.monotonic()
    print("=" * 70)
    print("CODE GEOMETRY LAB — Mandelbrot Variant Comparison (Phase 2)")
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

    # ---- Phase 4: Instrumented Tracing (at benchmark size) ----
    print("\n[Phase 4] Instrumented Tracing (at benchmark size — no size confound)")
    trace_params = dict(REFERENCE_PARAMS)  # Same size as benchmarks

    trace_records = {}
    capped_variants = []
    for name, compute_fn in variants:
        if name not in valid_variants:
            continue
        target_file = name
        print(f"  Tracing {name}...", end=" ", flush=True)
        _, record = trace_variant(name, compute_fn, trace_params, target_file=target_file)
        trace_records[name] = record
        d = record.to_dict()
        cap_tag = " [CAPPED]" if d["was_capped"] else ""
        if d["was_capped"]:
            capped_variants.append(name)
        print(f"events={d['total_events']}, calls={d['total_calls']}, "
              f"max_depth={d['max_call_depth']}{cap_tag}")

    if capped_variants:
        print(f"\n  WARNING: {len(capped_variants)} variants hit event cap: {capped_variants}")
        print("  Their geometric metrics are computed from truncated traces.")

    # ---- Phase 5: Geometric Metrics ----
    print("\n[Phase 5] Geometric Metrics")
    geometric_results = {}
    for name, record in trace_records.items():
        print(f"  Computing geometry for {name}...", end=" ", flush=True)
        gm = compute_all_geometric_metrics(record, trajectory_points=trajectory_points)
        gm["_was_capped"] = record.was_capped
        geometric_results[name] = gm
        print(f"{len(gm)} metrics computed")

    # ---- Phase 6: Baseline Metrics ----
    print("\n[Phase 6] Baseline Metrics")
    baseline_results = {}
    for name, module_path in zip(VARIANT_NAMES, VARIANT_MODULES):
        if name not in valid_variants:
            continue
        bl = compute_all_baselines(module_path)
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

    # ---- Phase 8: Correlation Analysis with BH-FDR ----
    print("\n[Phase 8] Correlation Analysis (with BH-FDR correction)")

    outcome_keys = [
        "runtime_mean_s",
        "runtime_cv",
        "scaling_exponent",
        "stability_cv",
    ]

    all_metric_keys = set()
    for name in valid_variants:
        all_metric_keys.update(combined[name].keys())
    predictor_keys = sorted([
        k for k in all_metric_keys
        if k not in outcome_keys
        and k not in ("all_times_s", "variant_name", "_was_capped")
        and not k.startswith("runtime_")
        and not k.startswith("stability_")
        and not k.startswith("scaling_")
    ])

    # Collect ALL correlation tests
    all_tests = []  # (outcome, predictor, rho, p_value, n)
    correlations = {}

    for outcome in outcome_keys:
        outcome_vals = []
        for name in valid_variants:
            val = combined[name].get(outcome)
            if val is not None and not (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                outcome_vals.append((name, val))

        if len(outcome_vals) < 4:
            continue

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

            x = np.array(x_vals, dtype=float)
            y_sub = np.array(y_vals, dtype=float)

            if np.std(x) < 1e-12 or np.std(y_sub) < 1e-12:
                continue

            rho, p_value = stats.spearmanr(x, y_sub)
            if not np.isnan(rho):
                test_key = f"{pred_key}__vs__{outcome}"
                all_tests.append((test_key, outcome, pred_key, float(rho), float(p_value), len(x_vals)))

    # Apply BH-FDR correction across ALL tests
    if all_tests:
        p_for_bh = [(t[0], t[4]) for t in all_tests]
        bh_results = benjamini_hochberg(p_for_bh, alpha=0.05)
        bh_lookup = {key: (adj_p, sig) for key, _, adj_p, sig in bh_results}
    else:
        bh_lookup = {}

    total_tests = len(all_tests)
    print(f"  Total correlation tests: {total_tests}")

    # Build structured correlations with adjusted p-values
    for test_key, outcome, pred_key, rho, p_raw, n in all_tests:
        adj_p, sig = bh_lookup.get(test_key, (p_raw, False))
        correlations.setdefault(outcome, []).append({
            "predictor": pred_key,
            "spearman_rho": rho,
            "p_value_raw": p_raw,
            "p_value_adjusted": adj_p,
            "significant_after_fdr": sig,
            "n": n,
        })

    for outcome in correlations:
        correlations[outcome].sort(key=lambda c: abs(c["spearman_rho"]), reverse=True)

    # Print results
    n_raw_sig = sum(1 for t in all_tests if t[4] < 0.05)
    n_fdr_sig = sum(1 for _, (adj, sig) in bh_lookup.items() if sig)
    print(f"  Significant at raw p<0.05: {n_raw_sig}")
    print(f"  Significant after BH-FDR: {n_fdr_sig}")

    print(f"\nTop correlations (|rho| > 0.5, showing raw and adjusted p):")
    print("-" * 95)
    for outcome in outcome_keys:
        if outcome not in correlations:
            continue
        for corr in correlations[outcome]:
            if abs(corr["spearman_rho"]) > 0.5:
                geo_tag = "[GEO]" if not corr["predictor"].startswith("baseline_") else "[BASE]"
                fdr_tag = " FDR*" if corr["significant_after_fdr"] else ""
                raw_tag = "*" if corr["p_value_raw"] < 0.05 else ""
                print(f"  {geo_tag} {corr['predictor']:45s} vs {outcome:20s} "
                      f"rho={corr['spearman_rho']:+.3f} "
                      f"p_raw={corr['p_value_raw']:.4f}{raw_tag} "
                      f"p_adj={corr['p_value_adjusted']:.4f}{fdr_tag}")

    # ---- Phase 9: Ranking Table ----
    print(f"\n[Phase 9] Variant Ranking by Runtime ({len(valid_variants)} variants)")
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
        "experiment": "mandelbrot_variant_comparison_phase2",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "n_benchmark_runs": n_benchmark_runs,
            "n_scaling_runs": n_scaling_runs,
            "scaling_sizes": list(scaling_sizes),
            "trace_grid_size": "same_as_benchmark",
            "trajectory_points": trajectory_points,
            "reference_params": REFERENCE_PARAMS,
            "event_cap": 2_000_000,
            "fdr_correction": "benjamini_hochberg",
        },
        "correctness": {name: {"passed": r["passed"]} for name, r in gate_report.items()},
        "capped_variants": capped_variants,
        "runtime": runtime_results,
        "scaling": scaling_results,
        "geometric": geometric_results,
        "baselines": baseline_results,
        "correlation_stats": {
            "total_tests": total_tests,
            "raw_significant": n_raw_sig,
            "fdr_significant": n_fdr_sig,
        },
        "correlations": correlations,
        "ranking_by_runtime": ranked,
        "elapsed_s": elapsed,
    }

    for name in results["runtime"]:
        if "all_times_s" in results["runtime"][name]:
            del results["runtime"][name]["all_times_s"]

    os.makedirs("results", exist_ok=True)
    result_path = "results/mandelbrot_phase2_results.json"
    with open(result_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {result_path}")

    return results


if __name__ == "__main__":
    results = run_experiment()
