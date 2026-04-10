# Code Geometry Lab — File Index for External Review

**Project:** Code Geometry Lab
**Date:** 2026-04-10
**Repo:** https://github.com/vegarjr/CodeGeometryLab

---

## Root Documents

| Path | Description |
|------|-------------|
| `README.md` | Project overview, structure summary, and dependency list |
| `CLAUDE_CODE_INSTRUCTION_CODE_GEOMETRY.md` | Original research instruction document that defined the project scope and methodology |
| `PROJECT_SCOPE_AND_NON_INHERITANCE.md` | Declares what is/isn't inherited from sibling repos (Fractal, GeometricAI, SelfSupervisedGeometry) |
| `RESEARCH_PLAN_CODE_GEOMETRY.md` | Full audit of sibling repos, reuse decisions, MVP task selection, experiment design, success/failure criteria |
| `RESULTS_CODE_GEOMETRY_MVP.md` | Final results write-up: hypothesis verdicts, correlation tables, ranking, honest assessment, next steps |
| `.gitignore` | Excludes .venv/, __pycache__/, .claude/ from version control |

---

## Variants — 10 Mandelbrot Implementations

All accept `(x_min, x_max, y_min, y_max, width, height, max_iter)` and return a 2D integer array. All produce identical output (verified by correctness gate).

| Path | Description |
|------|-------------|
| `variants/__init__.py` | Package init |
| `variants/mandelbrot/__init__.py` | Package init |
| `variants/mandelbrot/v01_naive_loop.py` | Double nested for-loop with inline complex arithmetic |
| `variants/mandelbrot/v02_complex_class.py` | Python complex type with per-pixel helper function |
| `variants/mandelbrot/v03_recursive.py` | Recursive escape-time function (depth = iteration count) |
| `variants/mandelbrot/v04_numpy_vectorized.py` | Full-grid NumPy vectorization with masked updates |
| `variants/mandelbrot/v05_numpy_rowwise.py` | Row-at-a-time vectorization (hybrid scalar/vector) |
| `variants/mandelbrot/v06_early_exit.py` | Cardioid/bulb pre-check to skip known-interior points |
| `variants/mandelbrot/v07_chunked_blocks.py` | Block-tiled processing with configurable chunk size |
| `variants/mandelbrot/v08_generator_pipeline.py` | Generator-based lazy evaluation pulled by a consumer |
| `variants/mandelbrot/v09_functional_map.py` | Map/reduce style with pure functions, no mutation |
| `variants/mandelbrot/v10_object_oriented.py` | Class-based with state encapsulation and method decomposition |

---

## Tasks

| Path | Description |
|------|-------------|
| `tasks/__init__.py` | Package init |
| `tasks/mandelbrot_task.py` | Task definition: reference params, variant loading, correctness gate that asserts all variants match |

---

## Instrumentation

| Path | Description |
|------|-------------|
| `instrumentation/__init__.py` | Package init |
| `instrumentation/tracer.py` | sys.settrace-based execution tracer; captures call/return/line events, timing, depth, function counts |

---

## Representations

| Path | Description |
|------|-------------|
| `representations/__init__.py` | Package init |
| `representations/trace_graph.py` | Builds call graph, temporal transition graph, and line-flow graph from trace events; computes graph metrics |
| `representations/state_trajectory.py` | Converts trace into a time-series of 6D feature vectors; computes path length, curvature, dispersion, recurrence |
| `representations/fractal_summary.py` | Compression ratio, n-gram motif analysis, branching profile, self-similarity scoring |

---

## Metrics

| Path | Description |
|------|-------------|
| `metrics/__init__.py` | Package init |
| `metrics/geometric_metrics.py` | Unified collector: calls all three representations and returns 67 flat metrics per variant |
| `metrics/outcome_metrics.py` | Measures runtime (30 runs), scaling exponent across grid sizes, run-to-run stability |
| `metrics/baselines.py` | Static code baselines (line count, AST nodes, cyclomatic complexity, nesting depth) + trivial trace stats |

---

## Experiments

| Path | Description |
|------|-------------|
| `experiments/__init__.py` | Package init |
| `experiments/run_mandelbrot_comparison.py` | Main experiment runner: correctness gate, benchmarking, tracing, geometric metrics, correlations, ranking |

---

## Results

| Path | Description |
|------|-------------|
| `results/mandelbrot_mvp_results.json` | Full machine-readable results: per-variant metrics, correlations, config, ranking |
| `results/mandelbrot_mvp_correlation_summary.csv` | Top correlations between geometric/baseline metrics and outcomes with rho and p-values |

---

## Review

| Path | Description |
|------|-------------|
| `Review/latestdoc.md` | This file — complete file index for external review |
