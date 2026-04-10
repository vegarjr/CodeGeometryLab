# Claude Code Instruction — Code Geometry / Fractal Trace Research Lab

## Summary
Build this as a **new repository / new folder**, not inside the existing Fractal AI repo.

The new repo should have access to the earlier repos as **reference sources**, but it must **not** inherit their assumptions blindly.

The purpose of this side project is to test a new research hypothesis:

> **Can execution traces of semantically equivalent code be represented geometrically or fractally, and do those geometric signatures help predict which implementation is better?**

"Better" must be defined empirically, not aesthetically.

---

# 1. Repository strategy

## Decision
Create a **new repository** for this project.

### Why
The earlier repos already have their own goals:
- **Fractal AI**: recursive dynamical architectures, kernel contracts, routing, growth, compute efficiency
- **GeometricAI**: mature structured research trunk
- **SelfSupervisedGeometry**: frontier branch for latent structure and geometry

This new idea is still exploratory and could easily contaminate those repos with speculative machinery.

## Important constraint
The new repository must still be able to **inspect and reuse** useful pieces from the old repositories.

### Recommended workspace layout
This is a guide, not a rigid requirement:

```text
/workspace/
  FractalAI/
  GeometricAI/
  SelfSupervisedGeometry/
  CodeGeometryLab/
```

Or equivalent local paths.

The new repo should live as a **sibling** of the old repos, not nested inside one of them.

---

# 2. Important warning about existing CLAUDE.md and contracts

The Fractal folder already contains a `CLAUDE.md` and earlier contract files.
Those may be useful as reference, but they can also silently bias or misdirect this side project if treated as governing instructions.

## Rule
For this project:
- earlier `CLAUDE.md` files are **reference documents**, not controlling law
- earlier contracts are **reference contracts**, not automatically binding on this repo
- you may reuse ideas from them only if they fit the new project after explicit review

## Required safeguard
Create a local project note early that says, in effect:

- this repo is a new experimental program
- external repos are read as references
- nothing is inherited without explicit adoption

Suggested file:
- `PROJECT_SCOPE_AND_NON_INHERITANCE.md`

Content should include:
- what is inherited conceptually
- what is only advisory
- what is intentionally *not* inherited

---

# 3. Core mission of the new repo

The repo should test whether code can be analyzed as:

1. a **dynamical system**
2. a **graph process**
3. a **recursive / fractal growth pattern**
4. a **geometric trajectory in latent space**

The system should compare multiple semantically equivalent Python implementations and determine whether geometric trace properties correlate with:
- runtime speed
- memory use
- stability
- scaling behavior
- structural elegance / regularity
- or other measurable performance characteristics

The project is successful only if it produces an empirical answer.

---

# 4. First principle: audit old repos before implementation

Before building anything serious, inspect the existing repositories thoroughly.
Do not assume earlier chat summaries are complete.

## Repositories to audit
At minimum:
- FractalAI
- GeometricAI
- SelfSupervisedGeometry

## What to look for
Search for reusable ideas related to:
- execution logging
- timing / profiling
- recursive or fractal representations
- sparse routing
- compute tracking
- graph-style or hierarchical state transitions
- benchmark harness patterns
- result serialization patterns
- geometric encodings
- latent trajectory analysis

## Also identify
- obsolete paths
- superseded files
- broken or invalid benchmark lines
- assumptions that belong only to older contracts

## Deliverable
Before major coding, create:

`RESEARCH_PLAN_CODE_GEOMETRY.md`

This file must contain:
1. which old files/repos are reusable
2. which are not worth reusing
3. what the cleanest MVP is
4. what the first experiment will be
5. what counts as success or failure

Do not skip this step.

---

# 5. Research hypothesis to formalize

The working hypothesis is:

> Different implementations of the same algorithm induce different execution geometries, and some of those geometric properties may correlate with quality.

This must be broken into testable sub-questions:

## H1 — Trace geometry exists
Execution traces can be converted into structured geometric or fractal representations.

## H2 — Geometric metrics differ across implementations
Semantically equivalent implementations produce measurably different geometric signatures.

## H3 — Some geometric metrics correlate with real outcomes
At least some geometric metrics correlate with runtime, memory use, stability, or scaling.

## H4 — Geometric ranking adds value over trivial baselines
The geometric view tells us something beyond:
- code length
- cyclomatic complexity
- runtime-only ranking
- memory-only ranking

If H4 fails, say so clearly.

---

# 6. MVP scope

The first version must be **small, falsifiable, and cheap**.
Do not build a giant meta-framework first.

## Required MVP structure
Choose **one algorithmic task** first.
It should be:
- deterministic
- correctness-checkable
- rich enough to admit multiple implementations
- cheap enough to run many times

### Good candidates
Pick one based on repo fit and implementation convenience:
- Mandelbrot iteration
- recursive vs iterative transform
- small numerical solver
- graph traversal
- parser/token transform
- vectorized vs looped numeric routine

## Then generate 10 variants
Create **10 semantically equivalent Python implementations** of the same task.

They should differ meaningfully in:
- recursion vs iteration
- vectorization vs explicit loops
- helper function decomposition
- control-flow structure
- intermediate-state organization
- branching pattern
- memory reuse style

Do not count trivial renamings or formatting changes as real variants.

---

# 7. Correctness gate

Before any geometry analysis, verify correctness.

## Rule
A code variant that is wrong must never be ranked as best.

## Required checks
For all variants:
- identical output, or
- acceptable numerical tolerance on the chosen test suite

Variants that fail correctness should be excluded or marked invalid.

---

# 8. Execution instrumentation

Build a lightweight instrumentation layer.

## Must capture at least
- wall-clock runtime
- repeated-run variance
- function call counts
- recursion depth / loop depth
- branch counts
- trace length
- event sequence
- selected summaries of intermediate state

## If feasible also capture
- peak memory
- allocation counts
- per-block timing
- exception/failure modes

## Trace record design
Use structured events rather than raw logs.

Each event should include a useful subset of:
- step id
- event type
- function/block id
- parent or predecessor id
- branch id
- depth
- timestamp or delta time
- input/output shape summary
- numerical summary (mean/std/norm, if relevant)

Keep v1 lightweight.
Do not build a profiler that makes the experiment unusably slow.

---

# 9. Geometric representations to build

For each execution trace, create one or more representations.

## Representation A — Execution graph
Nodes may represent:
- functions
- blocks
- events
- state checkpoints

Edges may represent:
- temporal order
- calls
- returns
- branch transitions

## Representation B — State trajectory
Turn the execution into a sequence of feature vectors over time.

These vectors may be built from:
- engineered trace features
- lightweight statistical summaries
- later, learned embeddings

## Representation C — Recursive / fractal summary
Build a summary of:
- branching structure
- motif repetition
- self-similarity across trace scales
- compression / repeatability

Do not overcomplicate v1 with heavy learned embeddings unless necessary.

---

# 10. Geometric metrics

Start with interpretable metrics first.

## Candidate metric families
Choose a strong subset, not necessarily all.

### Trace / graph metrics
- node count
- edge count
- max depth
- mean branching factor
- graph diameter
- recurrence count
- motif reuse count
- graph entropy
- spectral radius or simple spectral summaries

### Trajectory metrics
- total path length
- average step norm
- curvature proxy
- dispersion
- recurrence / return frequency
- instability proxy
- trace compressibility

### Fractal / self-similarity proxies
- repeated motif score
- hierarchical reuse score
- branching growth profile
- approximate self-similarity score
- compression ratio as a reuse proxy

## Strong recommendation
Prefer metrics that are:
- reproducible
- computationally cheap
- interpretable
- robust across repeated runs

---

# 11. Real outcome metrics

Geometry is only useful if it predicts something real.

## Required measured outcomes
For each variant, record:
- correctness
- runtime
- memory if available
- stability across repeated runs
- scaling behavior as input size changes
- implementation complexity stats if useful

## Then test correlations
Ask whether geometric metrics correlate with:
- faster execution
- lower memory
- better scaling
- lower variance
- fewer unstable or noisy transitions

This is the real question.
Not “which trace looks nicest?”

---

# 12. Required baselines

You must compare the geometry-based approach against simpler baselines.

## Minimum baselines
- runtime-only ranking
- memory-only ranking
- line count / AST size
- static complexity proxies
- trivial trace statistics

## Required conclusion style
If geometry does not beat or add to trivial baselines, state that clearly.
Do not force a positive story.

---

# 13. Validation rules

## Anti-self-deception rules
1. correctness gate first
2. repeated runs per variant
3. at least one held-out input regime
4. no aesthetic-only scoring
5. no claiming causality from weak correlation
6. do not cherry-pick one metric after seeing the result without documenting it

## Preferred evaluation pattern
For each variant:
- run multiple times
- aggregate mean and variance
- compute geometry metrics once or repeatedly as needed
- correlate geometry metrics with measured outcomes

---

# 14. Suggested repo structure

These are suggestions only.
If a better structure emerges after repo audit, use that.

```text
CodeGeometryLab/
  README.md
  PROJECT_SCOPE_AND_NON_INHERITANCE.md
  RESEARCH_PLAN_CODE_GEOMETRY.md
  RESULTS_CODE_GEOMETRY_MVP.md
  references/
  tasks/
  variants/
  instrumentation/
  representations/
  metrics/
  experiments/
  results/
  notebooks/
```

## Suggested module ideas
- `instrumentation/trace_instrumentation.py`
- `representations/trace_graph.py`
- `representations/state_trajectory.py`
- `metrics/geometric_metrics.py`
- `tasks/<task_name>.py`
- `experiments/run_variant_comparison.py`
- `experiments/generate_or_store_variants.py`

Again: these are **guides**, not fixed names.

---

# 15. Reuse policy for old repos

## Reuse if genuinely helpful
- logging patterns
- timing utilities
- compute trackers
- recursive/fractal abstractions
- result serialization formats
- benchmark discipline

## Do not reuse blindly
If older modules are:
- obsolete
- benchmark-invalid
- tightly coupled to unrelated tasks
- based on assumptions disproven later

then document that and do not import them just because they exist.

## Best practice
Create a short reuse table in `RESEARCH_PLAN_CODE_GEOMETRY.md`:
- source repo
- file/module
- reuse decision
- reason

---

# 16. Deliverables

## Deliverable 1 — Audit/plan
`RESEARCH_PLAN_CODE_GEOMETRY.md`

Must include:
- repo audit findings
- reuse decisions
- selected MVP task
- proposed experiment
- explicit success/failure criteria

## Deliverable 2 — Working MVP
A runnable experiment that:
- compares 10 semantically equivalent implementations
- instruments execution
- computes geometric metrics
- compares them to real runtime/cost metrics
- ranks or summarizes variants

## Deliverable 3 — Results note
`RESULTS_CODE_GEOMETRY_MVP.md`

Must clearly state:
- what worked
- what failed
- whether geometric metrics were useful
- whether the project should continue
- what to do next

## Deliverable 4 — Machine-readable results
Save at least:
- per-variant metrics JSON or CSV
- ranking table
- correlation table
- run metadata

---

# 17. Hard constraints

- Do not assume prior chat summaries are complete
- Do not assume old repo `CLAUDE.md` files govern this project
- Do not assume old contracts are binding unless explicitly adopted
- Do not make suggested filenames final before audit
- Do not overbuild v1
- Do not claim success without evidence
- Do not confuse beautiful geometry with useful geometry

---

# 18. Preferred mindset

Be scientifically ambitious and skeptical.

We are not trying to decorate code with fractal metaphors.
We are trying to test whether **execution geometry** is a useful analytic signal.

Possible valid outcomes:
- **Yes**: some geometric metrics predict useful outcomes
- **Partially**: only certain trace representations or tasks show signal
- **No**: the geometric framing is interesting but not practically predictive

All three are acceptable if honestly demonstrated.

---

# 19. First action

Your first action is:

1. set up the new repo as a sibling to the old repos
2. ensure you can inspect the old repos as references
3. create `PROJECT_SCOPE_AND_NON_INHERITANCE.md`
4. audit the old repos
5. write `RESEARCH_PLAN_CODE_GEOMETRY.md`
6. only then start implementing the MVP

Do not skip the audit.
