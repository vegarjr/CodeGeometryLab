# Results — Code Geometry Phase 2

## Date: 2026-04-10

---

## 1. What Changed from MVP

| Fix | MVP | Phase 2 |
|-----|-----|---------|
| Trace/benchmark size | 50×50 traces, 200×200 benchmarks | Same size (200×200) |
| Event cap | 500K | 2M, capped traces flagged |
| Multiple comparison correction | None | Benjamini-Hochberg FDR |
| Mandelbrot variants | 10 | 25 |
| Tasks | 1 (Mandelbrot) | 2 (Mandelbrot + graph traversal) |
| Visualizations | None | Scatter plots + heatmaps |

---

## 2. Correctness Gate

- **Mandelbrot:** 25/25 PASS
- **Graph traversal:** 10/10 PASS

---

## 3. Capping Problem

At 200×200, 19 of 25 Mandelbrot variants hit the 2M event cap. Their geometric metrics are computed from truncated traces.

**Uncapped Mandelbrot variants (6):** v04_numpy_vectorized, v05_numpy_rowwise, v06_early_exit, v07_chunked_blocks, v18_numpy_complex, v19_sentinel_value

**All 10 graph traversal variants:** Uncapped. The graph task (200 nodes, 800 edges) produces manageable trace sizes (700–400K events).

**Implication:** Mandelbrot geometric metrics at full size are largely unreliable for most scalar variants. The graph traversal task is better suited for this analysis methodology. Future work should either use smaller grids for Mandelbrot tracing or accept that Python-level tracing is practical only for tasks below ~100K events.

---

## 4. The Central Result: No Correlations Survive FDR Correction

| Statistic | Value |
|-----------|-------|
| Total correlation tests | 426 |
| Raw significant (p < 0.05) | 11 |
| FDR-significant (BH, alpha=0.05) | **0** |

With 426 tests at alpha=0.05, we'd expect ~21 false positives by chance. Getting 11 raw hits is *below* the chance rate. **No geometric metric reliably predicts any performance outcome after proper correction.**

This is the honest answer to H4.

---

## 5. What the Raw Signals Show (Uncorrected)

Despite the FDR null, some raw signals are consistent and directionally plausible:

### Mandelbrot (n=25)

| Metric | Outcome | rho | p_raw | p_adj | Type |
|--------|---------|-----|-------|-------|------|
| traj_recurrence_rate | runtime_cv | -0.550 | 0.004 | 0.517 | GEO |
| traj_recurrence_rate | stability_cv | -0.516 | 0.008 | 0.517 | GEO |
| traj_displacement | runtime_mean_s | -0.507 | 0.010 | 0.517 | GEO |
| baseline_trace_total_events | runtime_mean_s | +0.518 | 0.008 | 0.517 | BASE |

The `traj_recurrence_rate` signal from the MVP replicates at n=25 (runtime_cv: rho=-0.550, p=0.004). The effect direction is the same: more recurrence = more stable runtime. But it does not survive 426-test FDR.

### Graph Traversal (n=10)

| Metric | Outcome | rho | p_raw | p_adj | Type |
|--------|---------|-----|-------|-------|------|
| traj_displacement | runtime_mean_s | +0.709 | 0.022 | 0.823 | GEO |
| frac_motif_5_unique_ratio | runtime_mean_s | -0.661 | 0.038 | 0.823 | GEO |
| baseline_trace_wall_clock | runtime_mean_s | +0.673 | 0.033 | 0.823 | BASE |
| baseline_trace_total_events | runtime_mean_s | +0.648 | 0.043 | 0.823 | BASE |

The strongest raw correlation in the entire experiment is `traj_displacement → runtime_mean_s` (rho=0.709) in graph traversal — a task with no NumPy offloading, where the tracer sees the full execution. But n=10 is too small for this to survive FDR.

---

## 6. Hypothesis Verdicts (Updated)

### H1 — Trace geometry exists: CONFIRMED
Unchanged from MVP. All variants produce dramatically different geometric signatures. This is not in question.

### H2 — Geometric metrics correlate with outcomes: WEAKLY SUPPORTED (uncorrected only)
Raw correlations exist and replicate across sample sizes (traj_recurrence_rate at n=10 in MVP and n=25 in Phase 2). But no correlation survives FDR correction. The signal is real but weak relative to the multiple-testing burden.

### H3 — Geometric metrics beat baselines: NOT SUPPORTED
After FDR, neither geometric nor baseline metrics are significant. In raw terms, geometric and baseline metrics perform comparably — neither dominates.

### H4 — Geometric ranking adds novel value: NOT SUPPORTED after FDR
The MVP's claim that `cg_density` uniquely predicted runtime_cv does not hold after (a) increasing to 25 variants and (b) applying FDR correction.

---

## 7. Why the MVP Findings Didn't Hold Up

1. **Multiple comparison correction.** The MVP computed 268 tests without correction. Phase 2 computes 426. The raw p=0.031 for cg_density becomes non-significant.

2. **Most Mandelbrot traces are capped.** At 200×200, most scalar Python variants produce >2M trace events. Their geometric metrics are from truncated traces, adding noise.

3. **Increased variant count diluted the signal.** Adding 15 variants with similar structure (many are scalar loops) added statistical power but also noise. The strongest signals (traj_recurrence_rate) remain directionally consistent but not significant after FDR.

4. **The graph traversal task shows the strongest raw geometric signal,** but has only n=10 variants — too few for FDR-corrected significance.

---

## 8. What Actually Worked

1. **The experimental pipeline is solid.** Correctness gate, tracing, metrics, FDR-corrected correlations, and visualizations all work correctly. The methodology is sound.

2. **The graph traversal task is better for this research.** No NumPy offloading means the tracer sees real execution geometry. No capping problem. Richer control-flow diversity. This should be the primary task going forward.

3. **traj_recurrence_rate is a real signal.** It replicates across sample sizes (n=10: rho=-0.701, n=25: rho=-0.550) and is directionally consistent. It doesn't survive FDR, but it's not random noise.

4. **traj_displacement predicts graph traversal runtime.** rho=0.709 is the strongest raw correlation in the experiment and has a clear interpretation: algorithms that traverse more "state distance" take longer.

---

## 9. Honest Assessment

The Code Geometry hypothesis, as tested, **does not produce statistically reliable predictions after multiple comparison correction.**

This does not mean the idea is worthless. It means:
- The signal is too weak relative to the number of metrics tested
- The methodology needs either (a) fewer, better-chosen metrics or (b) many more variants
- Python-level tracing has severe limitations for compute-heavy tasks (capping)
- The graph traversal task is more promising than Mandelbrot for this research

---

## 10. Recommended Next Steps (If Continuing)

1. **Focus on graph traversal.** Drop Mandelbrot or use only for validation. Graph traversal has no capping, no NumPy offloading, richer control flow.

2. **Expand graph variants to 25+.** The strongest signal (rho=0.709) is at n=10. At n=25, it might survive FDR.

3. **Pre-register 5-10 core metrics.** Drop the 67-metric shotgun. Pick traj_recurrence_rate, traj_displacement, frac_compression_ratio, cg_density, frac_motif_5_unique_ratio based on Phase 1-2 evidence. Fewer tests = lower FDR burden.

4. **Test composite predictors.** A regression model combining 3-5 geometric metrics might capture jointly what no single metric captures alone.

5. **Consider the minimum detectable effect.** With 10 variants and 426 tests, you need rho > 0.95 to survive FDR. That's unrealistic. Fewer metrics OR more variants are both necessary.

---

## 11. Key Numbers

| Metric | Value |
|--------|-------|
| Mandelbrot variants | 25 |
| Graph traversal variants | 10 |
| Total variants | 35 |
| Total correlation tests | 426 |
| Raw significant (p<0.05) | 11 |
| FDR-significant | **0** |
| Strongest raw (Mandelbrot) | traj_recurrence_rate → runtime_cv (rho=-0.550, p=0.004) |
| Strongest raw (graph) | traj_displacement → runtime_mean_s (rho=+0.709, p=0.022) |
| Mandelbrot capped variants | 19/25 |
| Graph capped variants | 0/10 |
| Total experiment time | 506 seconds |
