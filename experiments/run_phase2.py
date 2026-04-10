"""Phase 2 experiment: 25 Mandelbrot + 10 graph traversal variants.

Fixes from audit review:
- Tracing at benchmark size (no size confound)
- Event cap raised to 2M with capped-trace flagging
- BH-FDR correction on all correlation tests
- Two tasks (Mandelbrot + graph traversal)
- Scatter plot visualizations for top correlations
"""

import json
import os
import sys
import time
from datetime import datetime

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instrumentation.tracer import trace_variant
from metrics.geometric_metrics import compute_all_geometric_metrics
from metrics.outcome_metrics import measure_runtime, measure_stability
from metrics.baselines import compute_all_baselines, compute_trace_baselines


def benjamini_hochberg(p_values, alpha=0.05):
    sorted_pv = sorted(p_values, key=lambda x: x[1])
    m = len(sorted_pv)
    results = []
    for rank, (key, p) in enumerate(sorted_pv, 1):
        adjusted = min(p * m / rank, 1.0)
        results.append((key, p, adjusted, adjusted < alpha))
    for i in range(len(results) - 2, -1, -1):
        key, p, adj, sig = results[i]
        _, _, adj_next, _ = results[i + 1]
        if adj > adj_next:
            results[i] = (key, p, adj_next, adj_next < alpha)
    return results


def run_single_task(task_name, variant_names, variant_modules, load_fn, gate_fn,
                    ref_params, benchmark_fn_maker, trace_params, n_runs=30):
    """Run one task through the full pipeline. Returns combined metrics dict."""
    print(f"\n{'='*70}")
    print(f"TASK: {task_name}")
    print(f"{'='*70}")

    # Correctness gate
    print(f"\n[1] Correctness Gate")
    gate_report = gate_fn(verbose=True)
    valid = [n for n, r in gate_report.items() if r["passed"]]
    print(f"\n{len(valid)}/{len(gate_report)} passed.\n")

    variants = load_fn()

    # Runtime benchmarking
    print(f"[2] Runtime Benchmarking ({n_runs} runs)")
    runtime_results = {}
    for name, fn in variants:
        if name not in valid:
            continue
        print(f"  {name}...", end=" ", flush=True)
        times = []
        for _ in range(n_runs):
            t0 = time.monotonic()
            fn(**ref_params)
            t1 = time.monotonic()
            times.append(t1 - t0)
        times = np.array(times)
        rt = {
            "runtime_mean_s": float(np.mean(times)),
            "runtime_std_s": float(np.std(times)),
            "runtime_median_s": float(np.median(times)),
            "runtime_cv": float(np.std(times) / np.mean(times)) if np.mean(times) > 0 else 0.0,
        }
        # Stability: discard warmup
        if len(times) > 5:
            stable = times[3:]
            rt["stability_cv"] = float(np.std(stable) / np.mean(stable)) if np.mean(stable) > 0 else 0.0
        else:
            rt["stability_cv"] = rt["runtime_cv"]
        runtime_results[name] = rt
        print(f"mean={rt['runtime_mean_s']:.4f}s, cv={rt['runtime_cv']:.3f}")

    # Tracing
    print(f"\n[3] Instrumented Tracing")
    trace_records = {}
    capped = []
    for name, fn in variants:
        if name not in valid:
            continue
        print(f"  {name}...", end=" ", flush=True)
        _, record = trace_variant(name, fn, trace_params, target_file=name)
        trace_records[name] = record
        d = record.to_dict()
        tag = " [CAPPED]" if d["was_capped"] else ""
        if d["was_capped"]:
            capped.append(name)
        print(f"events={d['total_events']}, calls={d['total_calls']}, depth={d['max_call_depth']}{tag}")

    if capped:
        print(f"  WARNING: capped traces: {capped}")

    # Geometric metrics
    print(f"\n[4] Geometric Metrics")
    geo_results = {}
    for name, record in trace_records.items():
        gm = compute_all_geometric_metrics(record)
        gm["_was_capped"] = record.was_capped
        geo_results[name] = gm

    # Baselines
    print(f"[5] Baseline Metrics")
    base_results = {}
    for name, mod_path in zip(variant_names, variant_modules):
        if name not in valid:
            continue
        bl = compute_all_baselines(mod_path)
        if name in trace_records:
            bl.update(compute_trace_baselines(trace_records[name]))
        base_results[name] = bl

    # Combine
    combined = {}
    for name in valid:
        combined[name] = {}
        if name in runtime_results:
            combined[name].update(runtime_results[name])
        if name in geo_results:
            combined[name].update(geo_results[name])
        if name in base_results:
            combined[name].update(base_results[name])

    return combined, valid, runtime_results, capped


def correlate_with_fdr(combined, valid, task_name):
    """Run correlation analysis with BH-FDR correction."""
    outcome_keys = ["runtime_mean_s", "runtime_cv", "stability_cv"]

    all_metric_keys = set()
    for name in valid:
        all_metric_keys.update(combined[name].keys())
    predictor_keys = sorted([
        k for k in all_metric_keys
        if k not in outcome_keys
        and k not in ("_was_capped",)
        and not k.startswith("runtime_")
        and not k.startswith("stability_")
    ])

    all_tests = []
    for outcome in outcome_keys:
        for pred_key in predictor_keys:
            x_vals, y_vals = [], []
            for name in valid:
                xv = combined[name].get(pred_key)
                yv = combined[name].get(outcome)
                if (xv is not None and yv is not None
                    and not (isinstance(xv, float) and (np.isnan(xv) or np.isinf(xv)))
                    and not (isinstance(yv, float) and (np.isnan(yv) or np.isinf(yv)))):
                    x_vals.append(float(xv))
                    y_vals.append(float(yv))
            if len(x_vals) < 5:
                continue
            x, y = np.array(x_vals), np.array(y_vals)
            if np.std(x) < 1e-12 or np.std(y) < 1e-12:
                continue
            rho, p = stats.spearmanr(x, y)
            if not np.isnan(rho):
                all_tests.append({
                    "task": task_name,
                    "outcome": outcome,
                    "predictor": pred_key,
                    "rho": float(rho),
                    "p_raw": float(p),
                    "n": len(x_vals),
                })

    # BH-FDR
    if all_tests:
        p_list = [(f"{t['predictor']}__{t['outcome']}", t["p_raw"]) for t in all_tests]
        bh = benjamini_hochberg(p_list)
        bh_lookup = {k: (adj, sig) for k, _, adj, sig in bh}
        for t in all_tests:
            key = f"{t['predictor']}__{t['outcome']}"
            adj_p, sig = bh_lookup.get(key, (t["p_raw"], False))
            t["p_adjusted"] = adj_p
            t["significant_fdr"] = sig

    return all_tests


def make_plots(all_tests, combined_by_task, output_dir):
    """Generate scatter plots for top correlations."""
    os.makedirs(output_dir, exist_ok=True)

    # Get top 10 by |rho| across all tasks
    sorted_tests = sorted(all_tests, key=lambda t: abs(t["rho"]), reverse=True)
    top = sorted_tests[:10]

    fig, axes = plt.subplots(2, 5, figsize=(25, 10))
    axes = axes.flatten()

    for i, t in enumerate(top):
        ax = axes[i]
        task = t["task"]
        combined = combined_by_task[task]
        pred, outcome = t["predictor"], t["outcome"]

        xs, ys, labels = [], [], []
        for name, metrics in combined.items():
            xv = metrics.get(pred)
            yv = metrics.get(outcome)
            if xv is not None and yv is not None:
                xs.append(float(xv))
                ys.append(float(yv))
                labels.append(name)

        ax.scatter(xs, ys, alpha=0.7, s=40)
        for j, label in enumerate(labels):
            ax.annotate(label, (xs[j], ys[j]), fontsize=5, alpha=0.7)

        fdr_tag = " FDR*" if t.get("significant_fdr") else ""
        ax.set_title(f"{pred}\nvs {outcome}\nrho={t['rho']:.3f} p_adj={t.get('p_adjusted', t['p_raw']):.4f}{fdr_tag}",
                     fontsize=7)
        ax.set_xlabel(pred, fontsize=6)
        ax.set_ylabel(outcome, fontsize=6)
        ax.tick_params(labelsize=6)

    plt.suptitle("Top 10 Correlations (All Tasks)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "top_correlations.png"), dpi=150)
    plt.close()
    print(f"  Saved top_correlations.png")

    # Per-task correlation heatmaps
    for task, combined in combined_by_task.items():
        outcome_keys = ["runtime_mean_s", "runtime_cv", "stability_cv"]
        task_tests = [t for t in all_tests if t["task"] == task]
        if not task_tests:
            continue

        # Get unique predictors that have |rho| > 0.4 for any outcome
        strong = set()
        for t in task_tests:
            if abs(t["rho"]) > 0.4:
                strong.add(t["predictor"])
        strong = sorted(strong)[:20]  # limit to 20

        if not strong:
            continue

        matrix = np.zeros((len(strong), len(outcome_keys)))
        for t in task_tests:
            if t["predictor"] in strong:
                r = strong.index(t["predictor"])
                c = outcome_keys.index(t["outcome"]) if t["outcome"] in outcome_keys else -1
                if c >= 0:
                    matrix[r, c] = t["rho"]

        fig, ax = plt.subplots(figsize=(8, max(6, len(strong) * 0.35)))
        im = ax.imshow(matrix, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(outcome_keys)))
        ax.set_xticklabels(outcome_keys, fontsize=8, rotation=30)
        ax.set_yticks(range(len(strong)))
        ax.set_yticklabels(strong, fontsize=7)
        plt.colorbar(im, ax=ax, label="Spearman rho")
        ax.set_title(f"{task}: Top Metric Correlations", fontsize=10)
        plt.tight_layout()
        fname = f"heatmap_{task}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150)
        plt.close()
        print(f"  Saved {fname}")


def main():
    start = time.monotonic()
    print("=" * 70)
    print("CODE GEOMETRY LAB — Phase 2 Experiment")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    # ---- Task 1: Mandelbrot (25 variants) ----
    from tasks.mandelbrot_task import (
        REFERENCE_PARAMS as M_PARAMS,
        VARIANT_NAMES as M_NAMES,
        VARIANT_MODULES as M_MODULES,
        load_variants as m_load,
        correctness_gate as m_gate,
    )
    m_combined, m_valid, m_runtime, m_capped = run_single_task(
        "mandelbrot", M_NAMES, M_MODULES, m_load, m_gate,
        M_PARAMS, None, M_PARAMS, n_runs=30,
    )

    # ---- Task 2: Graph Traversal (10 variants) ----
    from tasks.graph_task import (
        REFERENCE_PARAMS as G_PARAMS,
        VARIANT_NAMES as G_NAMES,
        VARIANT_MODULES as G_MODULES,
        load_variants as g_load,
        correctness_gate as g_gate,
    )
    g_combined, g_valid, g_runtime, g_capped = run_single_task(
        "graph_traversal", G_NAMES, G_MODULES, g_load, g_gate,
        G_PARAMS, None, G_PARAMS, n_runs=30,
    )

    # ---- Correlation Analysis ----
    print(f"\n{'='*70}")
    print("CORRELATION ANALYSIS (BH-FDR corrected)")
    print(f"{'='*70}")

    m_tests = correlate_with_fdr(m_combined, m_valid, "mandelbrot")
    g_tests = correlate_with_fdr(g_combined, g_valid, "graph_traversal")
    all_tests = m_tests + g_tests

    total = len(all_tests)
    raw_sig = sum(1 for t in all_tests if t["p_raw"] < 0.05)
    fdr_sig = sum(1 for t in all_tests if t.get("significant_fdr", False))
    print(f"\nTotal tests: {total}")
    print(f"Raw p<0.05: {raw_sig}")
    print(f"FDR-significant: {fdr_sig}")

    # Print top results
    print(f"\nTop correlations (|rho| > 0.5):")
    print("-" * 100)
    for t in sorted(all_tests, key=lambda x: abs(x["rho"]), reverse=True):
        if abs(t["rho"]) <= 0.5:
            break
        geo_tag = "[GEO]" if not t["predictor"].startswith("baseline_") else "[BASE]"
        fdr = " FDR*" if t.get("significant_fdr") else ""
        raw = "*" if t["p_raw"] < 0.05 else ""
        print(f"  {t['task']:15s} {geo_tag} {t['predictor']:40s} vs {t['outcome']:18s} "
              f"rho={t['rho']:+.3f} p_raw={t['p_raw']:.4f}{raw} p_adj={t.get('p_adjusted', 0):.4f}{fdr}")

    # ---- Visualizations ----
    print(f"\n[Visualizations]")
    combined_by_task = {"mandelbrot": m_combined, "graph_traversal": g_combined}
    make_plots(all_tests, combined_by_task, "results")

    # ---- Save ----
    elapsed = time.monotonic() - start
    results = {
        "experiment": "phase2_multi_task",
        "timestamp": datetime.now().isoformat(),
        "tasks": {
            "mandelbrot": {
                "n_variants": len(m_valid),
                "capped": m_capped,
                "runtime": m_runtime,
            },
            "graph_traversal": {
                "n_variants": len(g_valid),
                "capped": g_capped,
                "runtime": g_runtime,
            },
        },
        "correlation_stats": {
            "total_tests": total,
            "raw_significant": raw_sig,
            "fdr_significant": fdr_sig,
        },
        "top_correlations": sorted(all_tests, key=lambda x: abs(x["rho"]), reverse=True)[:30],
        "all_correlations": all_tests,
        "elapsed_s": elapsed,
    }

    os.makedirs("results", exist_ok=True)
    with open("results/phase2_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to results/phase2_results.json")
    print(f"Total time: {elapsed:.1f}s")

    return results


if __name__ == "__main__":
    main()
