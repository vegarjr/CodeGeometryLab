# Project Scope and Non-Inheritance Declaration

## Project Identity

**Name:** Code Geometry Lab
**Purpose:** Test whether execution traces of semantically equivalent code can be represented geometrically or fractally, and whether those geometric signatures help predict which implementation is better.
**Status:** New experimental research program (initiated 2026-04-10)

---

## Relationship to Sibling Repositories

This repository is a **sibling** to the following projects, not a child or extension:

| Repository | Location | Relationship |
|---|---|---|
| Fractal (FractalAI) | `/home/vegar/Documents/Fractal` | Reference source |
| GeometricAI | `/home/vegar/Documents/GeometricAI` | Reference source |
| SelfSupervisedGeometry | `/home/vegar/Documents/SelfSupervisedGeometry` | Reference source |

---

## What Is Inherited Conceptually

These ideas from the sibling repos inform this project's design, adopted after explicit review:

1. **Fingerprint-as-geometric-signature pattern** (Fractal)
   - The idea of encoding structured data as a fixed-dimensional normalized vector for similarity computation
   - Adapted here: execution traces encoded as geometric feature vectors

2. **Append-only structured logging** (Fractal: AbstentionLog, SelectionAuditLog)
   - JSONL-based event logging with timestamped entries
   - Adapted here: execution trace events as structured records

3. **Residual-based routing / comparison** (GeometricAI, Fractal)
   - Comparing implementations by prediction residual rather than input fingerprint
   - Adapted here: comparing code variants by execution trace distance

4. **Frozen-probe transfer testing** (SelfSupervisedGeometry)
   - Training a metric on one condition, evaluating on others, to test invariance
   - Adapted here: testing whether geometric metrics generalize across input regimes

5. **Factorized representation** (SelfSupervisedGeometry)
   - Separating invariant structure from dynamic state in learned representations
   - Adapted here: separating code structure metrics from execution state metrics

6. **Benchmark discipline** (all three repos)
   - Repeated runs, variance reporting, OOD evaluation, correctness gates
   - Adopted directly

7. **Result serialization to JSON** (all three repos)
   - Structured result dicts with timestamps and metadata
   - Adopted directly

---

## What Is Only Advisory

These elements from sibling repos are available for consultation but do not govern this project:

1. **Fractal CLAUDE.md** — Contains 116 lessons and locked hyperparameters for the Fractal AI system. These are specific to orthogonal projection multi-task learning. May be consulted for general experimental discipline but do not apply to this project's parameters or architecture.

2. **REGISTRY_CONTRACT_v1_1.md** (Fractal) — Defines kernel vs extension, invariants (S1-S4, B1-B4, I1), and locked constants. These govern the Fractal projection registry, not this project.

3. **FRACTAL_AI_CONTRACT_v0_1.md** (Fractal) — Growth protocol for projection registry. Advisory only.

4. **GEOMETRIC_INFERENCE_BENCHMARK_v0_1.md** (GeometricAI) — Benchmark spec for 3D→2D projection learning. Task structure and gating pattern may inform this project's experiment design, but the specific tasks and baselines do not apply.

5. **PROJECT_SPEC_v0_1.md** (SelfSupervisedGeometry) — Vision for self-supervised 3D structure discovery. Architectural patterns are informative but domain-specific.

6. **LESSONS.md files** (Fractal: L1-L116, GeometricAI: L1-L12) — Accumulated findings. Some general lessons (e.g., "IID overestimates OOD", "structure matching > brute force") are broadly applicable. Domain-specific lessons (e.g., "proj_dim=24", "OVA threshold=3") do not apply.

---

## What Is Intentionally NOT Inherited

1. **Hyperparameter locks** — All locked constants from Fractal (EPOCHS=200, BATCH_SIZE=256, LR=1e-3, PROJ_DIM=24, etc.) are NOT inherited. This project determines its own parameters empirically.

2. **Architectural commitments** — Orthogonal projections, bypass heads, QR re-orthogonalization, OVA decomposition — these are Fractal-specific. Not adopted.

3. **Task definitions** — Weather prediction, air quality, 3D projection learning, self-supervised geometry — these are domain tasks of sibling repos. This project's task is code execution analysis.

4. **Gating thresholds** — FIDELITY_FLOOR=0.960, ISOLATION_COLLISION_THRESHOLD=1e-6, MERGE_COLLISION_THRESHOLD=0.05 — these are calibrated to Fractal's domain. Not adopted.

5. **Evolution stage system** — The 16-stage evolution pipeline (stage0_reflex through stage16_transfer) is Fractal-specific infrastructure. Not adopted.

6. **Model zoo** — MLP, DeepSets, GNN, per_vertex_mlp, scale_law, registry models from GeometricAI — these solve 3D geometry tasks. Not adopted as-is (patterns may inform architecture choices).

7. **Caution level system** — Green/yellow/red caution from Fractal's distribution boundary detection. Not adopted.

8. **Session handoff documents** — SESSION_HANDOFF_MARCH_2026.md files capture state of sibling projects, not this one.

---

## Governing Principle

> Nothing from sibling repositories is binding on this project unless explicitly adopted above with a stated reason.
>
> This project succeeds or fails on its own empirical evidence, not on inherited authority.
