# CodeGeometryLab Audit Review — v2 Phase 2

## Date
2026-04-10

## Scope of this review
This review updates the earlier MVP-only audit and incorporates the newer **Phase 2** results and files.

It covers:
- repository structure and isolation discipline
- implementation quality of the experimental pipeline
- consistency between written claims and stored result artifacts
- methodological strengths and weaknesses
- what the project currently supports and does not support
- recommended next steps after Phase 2

This is still **not** a line-by-line audit of every file in the repository. It is a focused critical review of the core documents, runner logic, tracer, task definitions, representative variants, and result artifacts.

---

# Executive verdict

## Short verdict
The repository is in a **good early research state**, but the statistical evidence is currently **weaker than the MVP initially suggested**.

That is not failure. It is a sign that the project has become more rigorous.

The strongest current conclusion is:

> CodeGeometryLab has demonstrated that semantically equivalent implementations produce measurably different execution-trace geometries, but it has **not yet** shown that those geometric metrics reliably predict implementation quality after proper multiple-comparison correction.

In other words:
- the **pipeline is real**
- the **question is valid**
- the **current predictive evidence is weak**

That is still a useful research outcome.

---

# What the repo got right

## 1. Creating a separate repository was the right choice
It was correct to isolate this work from Fractal / GeometricAI / SelfSupervisedGeometry rather than bury it inside one of the older research trunks.

This remains the right decision because:
- the idea is speculative
- the implementation style is different
- the new work needs room to fail or pivot without contaminating the older repos

## 2. The non-inheritance policy is strong and necessary
`PROJECT_SCOPE_AND_NON_INHERITANCE.md` remains one of the most important files in the repository.

It protects the side project from being silently governed by older repo-level assumptions, especially prior `CLAUDE.md` instructions and benchmark contracts.

That gives CodeGeometryLab its own methodological identity.

## 3. The project has become more rigorous, not more performative
Phase 2 added the right kinds of improvements:
- more variants
- a second task
- capped-trace flagging
- multiple-testing correction
- visualizations

These changes made the evidence **less flattering**, but **more believable**.

That is exactly what should happen in a serious research repo.

## 4. The experimental structure is sound
The project uses a reasonable structure:
1. correctness gate
2. runtime benchmarking without tracing overhead
3. tracing
4. geometric metric extraction
5. baseline metric extraction
6. correlation analysis
7. multiple-comparison correction
8. serialization and visualization

That is a real scientific workflow, not just an aesthetic experiment.

---

# Files reviewed in this updated audit

## Documents reviewed
- `README.md`
- `PROJECT_SCOPE_AND_NON_INHERITANCE.md`
- `RESEARCH_PLAN_CODE_GEOMETRY.md`
- `RESULTS_CODE_GEOMETRY_MVP.md`
- `RESULTS_CODE_GEOMETRY_PHASE2.md`
- `Review/latestdoc.md`

## Core implementation reviewed
- `experiments/run_mandelbrot_comparison.py`
- `experiments/run_phase2.py`
- `instrumentation/tracer.py`
- `representations/trace_graph.py`
- `representations/state_trajectory.py`
- `representations/fractal_summary.py`
- `metrics/baselines.py`
- `tasks/mandelbrot_task.py`
- `tasks/graph_task.py`

## Sample variant files reviewed
- `variants/mandelbrot/v03_recursive.py`
- `variants/mandelbrot/v04_numpy_vectorized.py`
- `variants/mandelbrot/v05_numpy_rowwise.py`

## Result artifacts reviewed
- `results/mandelbrot_mvp_results.json`
- `results/phase2_results.json`

---

# What was verified

## 1. Phase 2 materially changes the story
The update is not cosmetic.

Phase 2 expands the experiment to:
- **25 Mandelbrot variants**
- **10 graph traversal variants**
- **426 total correlation tests**
- **Benjamini-Hochberg FDR correction**

The central result is now:
- raw significant tests: **11**
- FDR-significant tests: **0**

So the project now explicitly shows that the MVP-style optimistic reading does **not** hold after stronger controls.

## 2. The written Phase 2 summary matches the stored result file
The claims in `RESULTS_CODE_GEOMETRY_PHASE2.md` are consistent with `results/phase2_results.json`.

This includes:
- total tests = 426
- raw significant = 11
- FDR significant = 0
- strongest raw graph signal = `traj_displacement -> runtime_mean_s`, rho ≈ 0.709
- strongest raw Mandelbrot signal = `traj_recurrence_rate -> runtime_cv`, rho ≈ -0.550
- neither survives FDR

That consistency matters and increases trust in the repo.

## 3. The tracer has improved, but the Mandelbrot tracing problem remains severe
The tracer was improved by:
- increasing max events from 500K to 2M
- explicitly marking `was_capped`

That is good.

But the core problem remains:
- **19 of 25 Mandelbrot variants** still hit the cap at the chosen size
- geometric metrics for those variants are therefore computed from truncated traces

This means the Mandelbrot portion of the experiment is now openly acknowledged as noisy and partially compromised for full-size trace geometry analysis.

## 4. Graph traversal is the better task for this methodology
The graph traversal task is a major improvement.

Why it is better:
- no NumPy offloading
- no trace capping at current size
- richer control-flow diversity
- cleaner alignment between Python-level execution and traced execution

This is the most important positive development in Phase 2.

---

# Strengths of the project as it stands now

## 1. The core concept is now properly testable
The project has successfully transformed a vague metaphor into a real question:

> Do engineered geometric summaries of execution traces predict anything meaningful about implementations?

That is a valid and useful scientific problem.

## 2. The repo is willing to invalidate its own early optimism
This is one of the strongest signs of quality.

The project did not cling to the MVP interpretation once Phase 2 weakened it.
Instead, it updated the conclusion in the stricter direction.

That increases credibility.

## 3. The graph-traversal branch gives the project a real future path
The Mandelbrot task now appears to be a mixed blessing:
- useful historically
- poor for this tracing methodology at full size

The graph task gives the project a more promising and more honest research base going forward.

## 4. The pipeline is reusable
Even though the current predictive result is weak, the project has already built reusable infrastructure for:
- correctness-gated multi-variant evaluation
- Python execution tracing
- graph / trajectory / fractal-summary extraction
- baseline comparisons
- FDR-aware correlation analysis

That is valuable in itself.

---

# Weaknesses and risks

## 1. The current statistical evidence is weak
This is the central scientific limitation.

After proper correction, there are **zero significant correlations**.

That means the repo currently does **not** support claims that code-geometry metrics robustly predict quality.

The strongest defensible statement is:
- there are **raw directional signals**
- but they are not yet statistically reliable under the present testing setup

## 2. The metric shotgun is too wide for the current sample sizes
The project is testing too many predictors relative to the number of variants.

This creates an ugly triangle:
- many metrics
- small `n`
- harsh FDR burden

That is why even plausible raw correlations get washed out.

The repo now says this explicitly, and that is correct.

## 3. Mandelbrot is partially the wrong task for full-size Python-level tracing
This is now one of the clearest lessons.

The problem is not Mandelbrot in itself.
The problem is that at the chosen scale:
- most scalar variants produce traces too large to capture fully
- vectorized variants offload important compute into NumPy internals that the tracer does not follow

So Mandelbrot is a poor fit for drawing strong conclusions about full execution geometry using the current instrumentation.

## 4. The current geometry is still proxy geometry
This remains true after Phase 2.

The repo is not yet learning deep geometric code embeddings.
It is using engineered summaries such as:
- graph density
- motif ratios
- compression ratio
- trajectory displacement
- recurrence proxies

That is fine for an MVP/Phase 2.
But it means the project should keep describing itself accurately.

## 5. Mechanism claims must remain weak
The current results support:
- descriptive differences
- correlation scouting
- task/method diagnosis

They do **not** yet support strong causal explanations for why specific geometric metrics should determine runtime behavior.

---

# Updated scientific assessment

## What is currently supported
The repo currently supports these claims reasonably well:

1. Semantically equivalent implementations can produce substantially different execution-trace geometries.
2. Some geometric metrics show raw directional correlations with runtime or stability.
3. The graph traversal task is a better fit than Mandelbrot for Python-level execution-geometry research.
4. The experimental infrastructure is solid enough to continue iterating.

## What is not currently supported
The repo does **not** currently support these stronger claims:

1. geometric metrics reliably identify the best implementation
2. geometric metrics outperform baselines in a robust statistically corrected sense
3. fractal/code-geometry analysis is already practically predictive
4. the current metric suite generalizes across tasks with reliable significance

---

# What Phase 2 taught us

## 1. The MVP result was too optimistic
This does not mean the MVP was useless.
It means it was underpowered and insufficiently corrected.

Phase 2 correctly showed that the stronger MVP-style interpretation should not stand as the main conclusion.

## 2. `traj_recurrence_rate` is interesting but not proven
This metric still looks worth keeping an eye on.
It shows a directionally plausible and replicated raw signal in Mandelbrot.

But it is not yet strong enough to anchor a major claim.

## 3. `traj_displacement` on graph traversal is the best current lead
This is the most interesting raw signal now.
It has a strong intuitive interpretation and occurs in the task where the tracer is most faithful.

But with only 10 graph variants, it is still not enough.

## 4. Methodological honesty improved more than empirical performance
This is the correct reading of the update.
The repo became **more scientifically trustworthy**, even though the headline effect weakened.

That is progress.

---

# Recommended next steps

## Priority 1 — Focus the project around graph traversal or similarly trace-friendly tasks
This is now the clearest recommendation.

Why:
- graph traversal avoids the Mandelbrot capping problem
- the tracer sees the real control flow
- the strongest raw signal currently lives there

Recommendation:
- make graph traversal the main development task
- treat Mandelbrot as secondary or validation-only

## Priority 2 — Expand graph variants aggressively
The graph task currently has only **10 variants**.
That is too small.

Recommendation:
- expand to **25–30 graph variants**
- preserve semantic equivalence and correctness
- add structurally diverse implementations, not cosmetic rewrites

This is probably the single highest-value next step.

## Priority 3 — Pre-register a small core metric set
The current 67-metric panel is too broad for the sample size.

Recommendation:
- reduce to a small set of pre-registered metrics
- likely candidates: `traj_displacement`, `traj_recurrence_rate`, `frac_compression_ratio`, one graph metric, and one motif metric
- clearly distinguish **exploratory** metrics from **core confirmatory** metrics

This will reduce the multiple-testing burden and make the results easier to interpret.

## Priority 4 — Consider composite predictors instead of single-metric fishing
It is plausible that no single metric is strong enough on its own, but a small combination is.

Recommendation:
- test simple multivariate models
- keep them interpretable
- do not jump immediately to large black-box models

This should happen only after the metric panel has been narrowed.

## Priority 5 — Explicitly separate three layers in the writeup
The repo should now clearly distinguish:

1. **trace geometry exists**
2. **raw directional predictive signal exists**
3. **statistically robust prediction has not yet been achieved**

That separation will keep the project honest and prevent rhetorical drift.

## Priority 6 — Do not rush into more exotic geometry yet
Do **not** immediately jump to:
- topological data analysis
- deep learned latent manifolds
- highly elaborate fractal metrics

The project first needs stronger evidence that the simpler signals survive with:
- more variants
- fewer tests
- better task selection

---

# Recommended immediate action list

## Best immediate sequence
1. Freeze Phase 2 as the current authoritative result
2. Update the review language everywhere to match the FDR-corrected reality
3. Expand graph traversal variants to 25+
4. Pre-register a small core metric set
5. Re-run the experiment on graph traversal first
6. Reassess whether any signal survives under that narrower design

## What not to do next
Do **not** immediately:
- celebrate the current code-geometry hypothesis as empirically validated
- add another giant family of metrics
- rely on capped Mandelbrot traces as the main evidence base
- oversell fractal before the predictive core works

---

# Final verdict

CodeGeometryLab is still a worthwhile research project.

But the project’s value has shifted.
It is currently valuable **less as a proof that code geometry works**, and **more as a disciplined exploration that has now exposed where the original claim weakens under stronger testing**.

That is not a collapse. It is refinement.

The current state should be described like this:

> The project has built a credible experimental framework, found some raw promising signals, and shown that those signals do not yet survive robust correction. The next stage is not to add more theory, but to reduce noise, narrow the metric panel, and test a better task family at larger sample size.

That is the honest place to stand.
