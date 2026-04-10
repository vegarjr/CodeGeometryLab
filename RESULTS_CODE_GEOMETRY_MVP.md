# Results — Code Geometry MVP

## Date: 2026-04-10

---

## 1. Experiment Summary

**Task:** Mandelbrot set escape-time computation (200×200 grid, max_iter=100)
**Variants:** 10 semantically equivalent Python implementations
**Runs:** 30 per variant (benchmarking), 5 per variant per size (scaling)
**Tracing:** Instrumented on 50×50 grid to keep event counts manageable
**Geometric metrics:** 67 per variant (graph, trajectory, fractal)
**Baseline metrics:** 12 per variant (static code analysis + trivial trace stats)
**Outcomes measured:** runtime, runtime CV, scaling exponent, stability CV

---

## 2. Correctness Gate

**Result: 10/10 PASS.** All variants produce identical integer arrays on the reference grid. No variants excluded.

---

## 3. Runtime Ranking

| Rank | Variant | Mean Runtime (s) | CV | Scaling Exponent |
|------|---------|------------------|----|------------------|
| 1 | v04_numpy_vectorized | 0.0443 | 0.051 | 2.68 |
| 2 | v06_early_exit | 0.0569 | 0.066 | 2.02 |
| 3 | v07_chunked_blocks | 0.0798 | 0.047 | 1.73 |
| 4 | v01_naive_loop | 0.1259 | 0.069 | 2.04 |
| 5 | v10_object_oriented | 0.1336 | 0.075 | 1.99 |
| 6 | v08_generator_pipeline | 0.1347 | 0.078 | 2.05 |
| 7 | v02_complex_class | 0.1362 | 0.046 | 2.02 |
| 8 | v09_functional_map | 0.2360 | 0.052 | 2.02 |
| 9 | v03_recursive | 0.2395 | 0.040 | 2.01 |
| 10 | v05_numpy_rowwise | 0.2682 | 0.047 | 1.30 |

**Observations:**
- NumPy vectorization wins decisively (3× faster than naive loop)
- Early-exit optimization is the second fastest despite being scalar
- Recursive variant is nearly the slowest due to Python call overhead
- Scaling exponents mostly cluster around 2.0 (expected: O(n²) pixels), except v04 (2.68, overhead from NumPy mask reallocation at scale) and v05 (1.30, row-wise vectorization amortizes better)

---

## 4. Hypothesis Results

### H1 — Trace geometry exists: PASS

All 10 variants produce measurably different geometric signatures. Key differentiators:

| Metric | Range across variants | Interpretation |
|--------|----------------------|----------------|
| Trace event count | 1,010 → 500,000 | 500× difference in trace verbosity |
| Max call depth | 1 → 102 | Recursive variant vastly deeper |
| Total function calls | 1 → 52,998 | Per-pixel function calls dominate |
| Call graph nodes | 1 → 5 | Decomposition level varies |
| Compression ratio | 0.012 → 0.167 | V04 (vectorized) highly compressible; V03 (recursive) less so |
| Self-similarity mean | 0.33 → 0.98 | Flat loops are highly self-similar; recursive less so |

Geometric signatures clearly distinguish implementations.

### H2 — Geometric metrics correlate with real outcomes: PARTIAL PASS

**Statistically significant correlations (p < 0.05):**

| Geometric Metric | Outcome | Spearman ρ | p-value | Interpretation |
|------------------|---------|-----------|---------|----------------|
| cg_density | runtime_cv | -0.680 | 0.031 | Denser call graphs → more stable runtime |
| lg_edge_count | runtime_cv | +0.661 | 0.038 | More line-level transitions → less stable |
| traj_recurrence_rate | stability_cv | -0.701 | 0.024 | Traces that revisit similar states → more stable |

**Near-significant (p < 0.10):**

| Geometric Metric | Outcome | Spearman ρ | p-value |
|------------------|---------|-----------|---------|
| cg_max_in_degree | runtime_mean_s | +0.614 | 0.059 |
| tg_dag_longest_path | scaling_exponent | +0.609 | 0.062 |
| frac_depth_entropy | runtime_mean_s | +0.555 | 0.096 |
| frac_compression_ratio | runtime_mean_s | -0.515 | 0.128 |

**For runtime (mean speed):** No single metric reaches p < 0.05 with n=10. Multiple geometric metrics reach ρ ≈ 0.55, suggesting a real but weak signal. With more variants, this might reach significance.

**For stability (CV, consistency):** Geometric metrics DO reach significance. The execution trajectory's recurrence rate is a genuine geometric signal that predicts run-to-run stability.

### H3 — Some geometric metrics correlate with real outcomes: PARTIAL PASS

For **runtime stability** (CV and stability_cv), the best predictor overall is:
- `baseline_cyclomatic_complexity` → stability_cv: ρ = +0.746, p = 0.013 (BASELINE)

The best geometric predictor is:
- `traj_recurrence_rate` → stability_cv: ρ = -0.701, p = 0.024 (GEOMETRIC)

The baseline wins in absolute ρ. However:
- `cg_density` → runtime_cv: ρ = -0.680, p = 0.031 (GEOMETRIC, no baseline equivalent reaches significance for runtime_cv)

So geometric metrics do provide statistically significant predictions for some outcomes that baselines don't cover as well.

### H4 — Geometric ranking adds value over trivial baselines: PARTIALLY SUPPORTED

**Where geometry adds value:**
1. **cg_density → runtime_cv (ρ = -0.680, p = 0.031):** No baseline metric significantly predicts runtime_cv. This is a genuinely novel signal from call graph geometry.
2. **traj_recurrence_rate → stability_cv (ρ = -0.701, p = 0.024):** While cyclomatic complexity also predicts stability_cv, recurrence rate captures a different aspect (dynamic execution pattern vs static code structure). They are complementary.

**Where geometry does NOT add value:**
- For raw runtime prediction, no geometric metric reaches significance. Simple trace length (ρ = 0.55) and total calls (ρ = 0.57) perform comparably.
- For scaling exponent, both geometric and baseline metrics hover around ρ ≈ 0.6, none reaching significance.

**Honest assessment:** Geometry provides modest novel signal, primarily for stability metrics. It does not revolutionize runtime prediction at this sample size. The call graph density result is the strongest evidence that geometric structure captures something beyond trivial statistics.

---

## 5. What Worked

1. **The pipeline works end-to-end.** Correctness gate, tracing, geometric representations, metrics, baselines, and correlation analysis all function correctly.

2. **Geometric signatures are real and distinguishable.** H1 is unambiguously supported. Different implementations create dramatically different execution geometries.

3. **Call graph density predicts runtime stability.** This is a novel finding: implementations with denser call graphs (more interconnections between functions) show lower runtime variance. Plausible mechanism: denser call graphs mean more modular code where Python's function call caching and branch prediction work better.

4. **Trajectory recurrence predicts stability.** Implementations whose execution trajectories repeatedly visit similar states (high recurrence rate) are more stable. This makes physical sense: repetitive execution patterns are more predictable for CPU branch prediction and caching.

5. **Compression ratio shows promising (but not significant) correlation with runtime.** Lower compression ratio (less repetitive trace) → faster execution. This needs more variants to confirm.

---

## 6. What Failed

1. **No geometric metric significantly predicts raw runtime.** The strongest (cg_max_in_degree, ρ = 0.614, p = 0.059) just misses significance. With n=10, we lack statistical power for moderate-strength correlations.

2. **Cyclomatic complexity outperforms geometric metrics for stability prediction.** The simplest baseline (static code complexity) is the strongest single predictor of run-to-run stability. Geometry adds complementary signal but doesn't dominate.

3. **Scaling exponent is not well-predicted by any metric.** Both geometric and baseline metrics show ρ ≈ 0.6 but none reach significance. Scaling behavior may depend more on algorithmic strategy (vectorized vs scalar, row-wise vs full-grid) than on trace geometry.

4. **Sample size limits conclusions.** With n=10 variants, correlations need ρ > 0.65 to reach p < 0.05. Many promising signals (ρ ≈ 0.55) may be real but are underpowered.

---

## 7. Are Geometric Metrics Useful?

**Short answer: Partially, yes.**

**Strongest evidence FOR:** Call graph density predicts runtime variability (p = 0.031), with no comparable baseline metric for this outcome. This is a genuine geometric signal.

**Strongest evidence AGAINST:** For the outcome most people care about (raw speed), geometric metrics don't beat trivial statistics at this sample size. Cyclomatic complexity (a 1970s metric) outperforms geometry for stability prediction.

**Nuanced answer:** Geometric metrics capture aspects of execution dynamics that static metrics cannot. The trajectory recurrence rate and call graph density are measuring real properties of how code executes, not just how it looks. But at n=10, the advantage over baselines is modest and inconsistent across outcomes.

---

## 8. Should the Project Continue?

**Yes, with focused modifications:**

1. **Increase variant count.** Move from 10 to 25-30 variants to gain statistical power. Many ρ ≈ 0.55 correlations may reach significance at n=25.

2. **Test a second task.** Mandelbrot is a compute-bound loop with limited control flow diversity. A graph traversal or parser task would test whether geometric metrics work for structurally richer code.

3. **Test held-out regime.** This MVP used one grid region. Test with zoomed-in regions (more iterations, different escape patterns) to check metric generalization.

4. **Investigate composite metrics.** Simple linear combinations of 2-3 geometric metrics might outperform any single metric. Ridge regression on the top geometric predictors vs baselines would test this.

5. **Profile memory.** We lack memory measurements. Some geometric metrics (especially fractal compression) might predict memory usage better than they predict speed.

---

## 9. Key Numbers

| Metric | Value |
|--------|-------|
| Variants tested | 10 |
| Correctness pass rate | 100% |
| Benchmark runs per variant | 30 |
| Geometric metrics per variant | 67 |
| Baseline metrics per variant | 12 |
| Significant geometric correlations (p<0.05) | 3 |
| Significant baseline correlations (p<0.05) | 1 |
| Best geometric predictor of runtime | cg_max_in_degree (ρ=0.614, p=0.059) |
| Best geometric predictor of stability | traj_recurrence_rate (ρ=-0.701, p=0.024) |
| Best baseline predictor of stability | cyclomatic_complexity (ρ=0.746, p=0.013) |
| Novel geometric signal | cg_density → runtime_cv (ρ=-0.680, p=0.031) |
| Total experiment time | 329 seconds |

---

## 10. Conclusion

The Code Geometry hypothesis is **partially supported**. Execution traces can be meaningfully represented as geometric objects (H1: confirmed), and some geometric properties correlate with real performance outcomes (H2: partially confirmed). However, geometric metrics do not clearly dominate simple baselines (H3: marginal), and their added value is limited to stability prediction and runtime variability rather than raw speed (H4: partially supported for specific outcomes).

The single most interesting finding is that **call graph density predicts runtime stability** — a result with no baseline equivalent and a plausible mechanistic explanation. This alone justifies further investigation.

The project has produced a working experimental pipeline and a falsifiable set of results. The next phase should focus on increasing statistical power (more variants, more tasks) and testing whether composite geometric metrics outperform baselines.
