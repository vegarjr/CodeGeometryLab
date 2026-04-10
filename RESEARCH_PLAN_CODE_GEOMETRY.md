# Research Plan — Code Geometry Lab

## Date: 2026-04-10

---

## 1. Repo Audit Findings

### Fractal (FractalAI)

**Maturity:** Production-ready. 89 experiments, 116 lessons, 701 tests, real-world deployment.

**Reusable for this project:**
- **Append-only JSONL logging** (AbstentionLog, SelectionAuditLog): Clean event-based tracing pattern with timestamps, aggregation, and batch retrieval. Directly adaptable for execution trace recording.
- **InputFingerprint (12D vector)**: Statistical signature encoding (mean/std/skew/kurtosis/eigenvalue ratio/correlation). Pattern transferable to execution trace fingerprinting.
- **Timing harness** (profile_sparse_routing.py): Warmup + median latency measurement with device sync. Reusable for variant benchmarking.
- **K-retry benchmark pattern** (exp73): Best-of-K with validation metric selection. Reusable for repeated-run aggregation.
- **Result dict structure** (distillation.py): {fidelity, r2_agreement, model, metadata, fingerprint, novelty}. Template for our result serialization.
- **MetaFeatureBuilder** (18-dim meta-features from task records): Pattern for building meta-descriptors from execution metadata.

**Not reusable:**
- 89 archived old versions in phase1_tabular/archive/ — obsolete
- fractal_xgb/ — documented catastrophic failure
- Soft orthogonality regularization — replaced by QR
- Synthetic-only benchmarks — overestimate real performance by +0.40 (L113)
- All locked hyperparameters (EPOCHS=200, PROJ_DIM=24, etc.) — domain-specific
- Evolution stage system (16 stages) — too coupled to Fractal's architecture

### GeometricAI

**Maturity:** Paper-ready. 22 tests pass, 12 locked lessons, clean modular codebase.

**Reusable for this project:**
- **EvolutionLoop pattern** (evolution_loop.py): Architecture ladder with epsilon-based selection (try all, pick simplest within epsilon of best). Transferable as a model selection strategy.
- **ResidualMonitor** (residual_monitor.py): Three-phase calibrate→check→discover pattern. Generic anomaly detection transferable to trace anomaly detection.
- **LawRegistry** (law_registry.py): Residual-based multi-model routing with frozen install. Pattern for comparing implementations by trace distance.
- **NoveltyBuffer** (novelty_buffer.py): FIFO accumulation with ready-signal. Generic pattern.
- **Training harness** (training.py): Early stopping, seed control, validation-based gating. Directly reusable.
- **Evaluation metrics** (metrics.py): Robust R² with zero-variance guard.

**Not reusable:**
- generator/projections.py, generator/objects.py — domain-specific (3D geometry)
- deepsets.py — catastrophic failure on per-element tasks (L5: R²=-5.94)
- Missing Tier 1 experiments (exp02-exp06) — never implemented, project pivoted
- GNN with cube topology — topology doesn't transfer

**Key lesson adopted:** Architecture matching > brute-force flexibility. Structure your representations to match the task, not the data.

### SelfSupervisedGeometry

**Maturity:** Research prototype. 10 experiments, 18 reviews, focused exploration.

**Reusable for this project:**
- **multi_output_installer.py**: Wraps multi-output predictor as per-dimension tasks. Generic and graduated.
- **pytorch_wrapper.py**: PyTorch-to-sklearn API bridge. Fully generic.
- **run_all_authoritative_evals.py**: Checkpoint-based evaluation harness with condition sweeps. Template for our experiment runner.
- **Three-target factorization pattern** (exp04_v5): Separate invariant structure from dynamic state. Applicable to separating code structure from execution dynamics.
- **Frozen probe transfer testing**: Train metric on one condition, test on others. Applicable to testing metric generalization across input sizes.

**Not reusable:**
- exp01 (ill-posed task, R²=-0.01)
- exp02 v1, exp03 v1, exp04 v1-v4 (all superseded with metric bugs)
- datagen/multi_view.py (3D-specific data generation)
- set_temporal_encoder.py (Chamfer loss for permutation invariance — interesting but not needed for v1)

**Key lesson adopted:** R² is dangerous for constant targets. Use task-appropriate metrics. Define metrics before training.

---

## 2. Reuse Decision Table

| Source Repo | Module/Pattern | Decision | Reason |
|---|---|---|---|
| Fractal | JSONL append-only logging pattern | **ADOPT** (pattern only) | Clean, proven event tracing. Rewrite for our schema. |
| Fractal | 12D fingerprint vector pattern | **ADOPT** (concept) | Fixed-dim statistical signature. Adapt to execution trace features. |
| Fractal | Timing harness (warmup+median) | **ADOPT** (pattern) | Standard profiling practice. Implement our own version. |
| Fractal | K-retry benchmark pattern | **ADOPT** (pattern) | Robust aggregation. Implement for repeated variant runs. |
| Fractal | Result dict serialization | **ADOPT** (pattern) | Structured JSON output. Adapt fields for our domain. |
| Fractal | Evolution stages / pipeline | **SKIP** | Too coupled to Fractal architecture. |
| Fractal | Locked hyperparameters | **SKIP** | Domain-specific. We set our own. |
| GeometricAI | Epsilon-based model selection | **STUDY** | Good principle. May apply to metric selection. |
| GeometricAI | Residual-based routing | **STUDY** | Interesting for variant comparison. Not needed for MVP. |
| GeometricAI | Three-phase monitoring | **STUDY** | Useful for future streaming analysis. Not needed for MVP. |
| GeometricAI | Training harness pattern | **ADOPT** (pattern) | Early stopping, seed control. |
| SelfSupGeo | multi_output_installer.py | **STUDY** | May be useful for multi-metric decomposition later. |
| SelfSupGeo | Frozen probe transfer test | **ADOPT** (concept) | Test metric generalization across input regimes. |
| SelfSupGeo | Factorized representation idea | **STUDY** | Separate structure vs dynamics. Not needed for MVP. |
| All three | JSON result serialization | **ADOPT** | Standard practice across all repos. |
| All three | Repeated runs + variance | **ADOPT** | Experimental discipline. |

---

## 3. Selected MVP Task: Mandelbrot Set Computation

### Why Mandelbrot

- **Deterministic**: Given (c, max_iter), the escape iteration count is deterministic
- **Correctness-checkable**: All variants must produce identical iteration counts for identical inputs
- **Rich implementation space**: Admits recursion, iteration, vectorization, complex-number abstractions, early-exit strategies, row-wise vs pixel-wise processing, chunked vs full-grid computation
- **Cheap to run**: A 200×200 grid with max_iter=100 runs in milliseconds to seconds depending on implementation
- **Scalable**: Can test 200×200 up to 2000×2000 to measure scaling behavior
- **Numerical simplicity**: Integer iteration counts avoid floating-point tolerance issues for correctness checking

### The 10 Variants

Each variant computes the Mandelbrot escape iteration count for a grid of complex points. They differ meaningfully in structure:

| # | Name | Key Structural Difference |
|---|---|---|
| V01 | `naive_loop` | Double nested for-loop, inline complex arithmetic |
| V02 | `complex_class` | Python complex number type, per-pixel function call |
| V03 | `recursive` | Recursive function for iteration (depth = escape count) |
| V04 | `numpy_vectorized` | Full-grid NumPy vectorization, masked updates |
| V05 | `numpy_rowwise` | Row-at-a-time vectorization (hybrid loop/vector) |
| V06 | `early_exit_optimized` | Cardioid/bulb pre-check + symmetry exploitation |
| V07 | `chunked_blocks` | Block-tiled processing with configurable chunk size |
| V08 | `generator_pipeline` | Generator-based lazy evaluation, pulled by consumer |
| V09 | `functional_map` | map/reduce style with pure functions, no mutation |
| V10 | `object_oriented` | MandelbrotComputer class with state encapsulation |

All variants accept the same inputs: `(x_min, x_max, y_min, y_max, width, height, max_iter)` and return a 2D integer array of escape iteration counts.

---

## 4. Proposed Experiment

### Phase 1: Correctness Gate
- Run all 10 variants on a reference grid (x ∈ [-2, 1], y ∈ [-1.5, 1.5], 200×200, max_iter=100)
- Assert all produce identical integer arrays
- Exclude any variant that fails

### Phase 2: Instrumented Execution
- Instrument each variant to capture structured trace events:
  - Function calls (entry/exit with depth)
  - Loop iterations (count per nesting level)
  - Branch decisions (taken/not-taken counts)
  - Intermediate state snapshots (every N steps: grid statistics)
  - Wall-clock timing per block
- Run each variant 30 times on the reference grid
- Record: runtime (mean, std, min, max), trace event counts, trace structure

### Phase 3: Geometric Representation
For each variant's execution trace, build:

**A. Execution Graph**
- Nodes: functions/blocks/events
- Edges: temporal order, call relationships
- Metrics: node count, edge count, max depth, branching factor, graph diameter, spectral radius

**B. State Trajectory**
- Sequence of feature vectors over execution time
- Features: elapsed fraction, active pixel count, mean iteration count, branch entropy
- Metrics: path length, step norm variance, curvature proxy, dispersion, recurrence frequency

**C. Fractal/Self-Similarity Summary**
- Motif repetition detection
- Branching growth profile
- Compression ratio as reuse proxy
- Hierarchical structure score

### Phase 4: Correlation Analysis
For each variant, compute:
- Geometric metrics (from Phase 3)
- Real outcome metrics: runtime, peak memory (if available), scaling exponent (200→500→1000→2000 grid), run-to-run variance

Test rank correlations (Spearman) between geometric metrics and real outcomes.

### Phase 5: Baseline Comparison
Compare geometry-based ranking against:
- Runtime-only ranking
- Memory-only ranking (if available)
- Line count / AST node count
- Cyclomatic complexity
- Trace length only (trivial trace statistic)

---

## 5. Success and Failure Criteria

### Success (H1-H4 all supported)
- **H1 PASS**: All 10 variants produce measurably different geometric signatures (at least 8 of 10 pairwise distinguishable)
- **H2 PASS**: Geometric metrics show statistically significant rank correlation (|ρ| > 0.6, p < 0.05) with at least one real outcome metric
- **H3 PASS**: The best geometric predictor of runtime outperforms line count and cyclomatic complexity as a predictor
- **H4 PASS**: At least one geometric metric captures information not available from any single baseline metric

### Partial Success
- H1 and H2 pass but H3/H4 fail: Geometry exists and differs, but doesn't beat simple baselines. Interesting but not practically useful. Document and consider whether richer tasks would change the result.

### Failure
- H1 fails: Traces are not meaningfully distinguishable geometrically. The framing is wrong for this task.
- H2 fails: Geometric differences exist but don't correlate with anything real. Beautiful but useless.
- All geometric metrics are redundant with trace length: The "geometry" is just counting steps with extra steps.

### Anti-Self-Deception Commitments
1. Correctness gate before any ranking
2. 30 runs per variant per input size
3. At least one held-out input regime (different grid region or resolution)
4. No aesthetic scoring
5. No claiming causality from weak correlation
6. If we search over many metrics post-hoc, report the full search, not just the winner
7. Baselines computed before geometric metrics, not after

---

## 6. Cleanest MVP Path

1. Write 10 variants in `variants/mandelbrot/`
2. Write correctness test in `tasks/mandelbrot_task.py`
3. Write instrumentation in `instrumentation/tracer.py`
4. Write representations in `representations/{trace_graph.py, state_trajectory.py, fractal_summary.py}`
5. Write metrics in `metrics/{geometric_metrics.py, outcome_metrics.py, baselines.py}`
6. Write experiment runner in `experiments/run_mandelbrot_comparison.py`
7. Run, collect results, analyze correlations
8. Write `RESULTS_CODE_GEOMETRY_MVP.md`

Total estimated modules: ~12 Python files + 2 markdown deliverables.
No external dependencies beyond NumPy, NetworkX (for graph metrics), and SciPy (for correlations).
