# Code Geometry Lab

**Research question:** Can execution traces of semantically equivalent code be represented geometrically or fractally, and do those geometric signatures help predict which implementation is better?

## Status

MVP in progress. Testing with 10 Mandelbrot set implementations.

## Structure

```
variants/mandelbrot/    — 10 semantically equivalent implementations
tasks/                  — Task definitions and correctness checks
instrumentation/        — Execution trace capture
representations/        — Geometric representations (graph, trajectory, fractal)
metrics/                — Geometric metrics, outcome metrics, baselines
experiments/            — Experiment runners
results/                — Machine-readable results (JSON/CSV)
notebooks/              — Analysis notebooks
references/             — Reference material from sibling repos
```

## Dependencies

- Python 3.10+
- NumPy
- SciPy
- NetworkX

## Sibling Repositories (reference only)

- Fractal (FractalAI)
- GeometricAI
- SelfSupervisedGeometry

See `PROJECT_SCOPE_AND_NON_INHERITANCE.md` for reuse policy.
