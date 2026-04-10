# Code Geometry Lab — File Index for External Review

**Project:** Code Geometry Lab
**Date:** 2026-04-10 (Phase 2)
**Repo:** https://github.com/vegarjr/CodeGeometryLab

---

## Root Documents

| Path | Description |
|------|-------------|
| `README.md` | Project overview, structure summary, and dependency list |
| `CLAUDE_CODE_INSTRUCTION_CODE_GEOMETRY.md` | Original research instruction document that defined the project scope and methodology |
| `PROJECT_SCOPE_AND_NON_INHERITANCE.md` | Declares what is/isn't inherited from sibling repos (Fractal, GeometricAI, SelfSupervisedGeometry) |
| `RESEARCH_PLAN_CODE_GEOMETRY.md` | Full audit of sibling repos, reuse decisions, MVP task selection, experiment design, success/failure criteria |
| `RESULTS_CODE_GEOMETRY_MVP.md` | MVP results (10 variants, no FDR correction). Superseded by Phase 2 but kept for history. |
| `RESULTS_CODE_GEOMETRY_PHASE2.md` | **Phase 2 results: 35 variants, BH-FDR correction, two tasks. Central finding: 0 FDR-significant correlations.** |
| `.gitignore` | Excludes .venv/, __pycache__/, .claude/ from version control |

---

## Variants — 25 Mandelbrot Implementations

All accept `(x_min, x_max, y_min, y_max, width, height, max_iter)` and return a 2D integer array. All produce identical output (verified by correctness gate).

| Path | Description |
|------|-------------|
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
| `variants/mandelbrot/v11_while_true_break.py` | while-True with explicit break instead of while-condition |
| `variants/mandelbrot/v12_precomputed_coords.py` | Pre-computes all coordinates into arrays before iteration |
| `variants/mandelbrot/v13_column_major.py` | Column-major traversal (cache-unfriendly) |
| `variants/mandelbrot/v14_flat_array.py` | Flat 1D array with divmod indexing |
| `variants/mandelbrot/v15_enumerate_style.py` | Pythonic enumerate + linspace iteration |
| `variants/mandelbrot/v16_try_except.py` | Exception-driven escape detection |
| `variants/mandelbrot/v17_deque_worklist.py` | Worklist pattern with deque queue |
| `variants/mandelbrot/v18_numpy_complex.py` | NumPy vectorized with native complex128 dtype |
| `variants/mandelbrot/v19_sentinel_value.py` | Sentinel value (-1) to mark completed pixels in flat array |
| `variants/mandelbrot/v20_dict_cache.py` | Dictionary-keyed result storage |
| `variants/mandelbrot/v21_list_comprehension.py` | Nested list comprehension with helper function |
| `variants/mandelbrot/v22_split_real_imag.py` | Separate helper functions for real, imaginary, and magnitude |
| `variants/mandelbrot/v23_itertools_product.py` | itertools.product for grid traversal (single flat loop) |
| `variants/mandelbrot/v24_half_grid_symmetry.py` | Vertical symmetry exploitation (computes top half, mirrors) |
| `variants/mandelbrot/v25_state_machine.py` | Explicit state machine with state constants and transition function |

---

## Variants — 10 Graph Traversal Implementations

All accept `(adj, source)` where adj is a weighted directed adjacency list, and return a dict of shortest distances.

| Path | Description |
|------|-------------|
| `variants/graph_traversal/g01_dijkstra_heap.py` | Classic Dijkstra with heapq (textbook) |
| `variants/graph_traversal/g02_dijkstra_no_skip.py` | Dijkstra without stale-entry skip |
| `variants/graph_traversal/g03_bellman_ford.py` | Bellman-Ford: relaxes all edges V-1 times |
| `variants/graph_traversal/g04_bfs_weighted.py` | SPFA-like BFS with re-queuing on improvement |
| `variants/graph_traversal/g05_recursive_relax.py` | Recursive DFS-style relaxation |
| `variants/graph_traversal/g06_dict_priority.py` | Manual priority queue (scan for minimum each step) |
| `variants/graph_traversal/g07_sorted_list_queue.py` | Sorted list as priority queue (re-sort after insert) |
| `variants/graph_traversal/g08_class_based.py` | OOP ShortestPathFinder class with method decomposition |
| `variants/graph_traversal/g09_iterative_improve.py` | Repeated full-edge scan until convergence |
| `variants/graph_traversal/g10_bidirectional.py` | Forward Dijkstra + backward refinement pass |

---

## Tasks

| Path | Description |
|------|-------------|
| `tasks/mandelbrot_task.py` | Mandelbrot task: reference params, variant loading, correctness gate (25 variants) |
| `tasks/graph_task.py` | Graph traversal task: reference graph generator, variant loading, correctness gate (10 variants) |

---

## Instrumentation

| Path | Description |
|------|-------------|
| `instrumentation/tracer.py` | sys.settrace-based tracer; 2M event cap with capped-trace flagging |

---

## Representations

| Path | Description |
|------|-------------|
| `representations/trace_graph.py` | Call graph, temporal transition graph, line-flow graph + metrics |
| `representations/state_trajectory.py` | 6D feature vector time-series + path/curvature/recurrence metrics |
| `representations/fractal_summary.py` | Compression ratio, n-gram motifs, branching profile, self-similarity |

---

## Metrics

| Path | Description |
|------|-------------|
| `metrics/geometric_metrics.py` | Unified collector: 67 flat metrics per variant from all representations |
| `metrics/outcome_metrics.py` | Runtime, scaling exponent, stability measurement |
| `metrics/baselines.py` | Static code baselines (line count, AST, cyclomatic complexity) + trace baselines |

---

## Experiments

| Path | Description |
|------|-------------|
| `experiments/run_mandelbrot_comparison.py` | MVP experiment runner (Phase 1, single task) |
| `experiments/run_phase2.py` | **Phase 2 runner: both tasks, FDR correction, visualizations** |

---

## Results

| Path | Description |
|------|-------------|
| `results/mandelbrot_mvp_results.json` | MVP results (10 variants, no FDR) |
| `results/mandelbrot_mvp_correlation_summary.csv` | MVP top correlations |
| `results/phase2_results.json` | **Phase 2 full results: 35 variants, 426 tests, FDR-corrected** |
| `results/top_correlations.png` | Scatter plots for top 10 correlations across both tasks |
| `results/heatmap_mandelbrot.png` | Correlation heatmap for Mandelbrot metrics |
| `results/heatmap_graph_traversal.png` | Correlation heatmap for graph traversal metrics |

---

## Review

| Path | Description |
|------|-------------|
| `Review/latestdoc.md` | This file — complete file index for external review |
| `Review/CODE_GEOMETRY_LAB_AUDIT_REVIEW.md` | External audit review of MVP (pre-Phase 2) |
