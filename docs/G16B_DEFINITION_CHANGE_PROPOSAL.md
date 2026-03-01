# G16b Definition Change Proposal (Candidate-Only)

Date: 2026-03-01

## Status

- Official gate remains unchanged: `G16b-v1`.
- `G16b-v2` is candidate-only and evaluated in parallel.
- No math formulas or thresholds in `run_qng_action_v1.py` were modified.

## Why v1 is fragile

- `G16b-v1` uses one global fit metric: `R2(G11, 8pi G T11) > 0.05`.
- A single global `R2` can understate coupling in low-signal profiles where `T11` is sign-mixed or near-zero dominated.
- In recent diagnostics, all `G16` failures are `G16b`-driven.

## Candidate v2 definition (diagnostic)

For each profile:

- compute `std(T11)/abs(mean(T11))`.
- if ratio `> 10`: evaluate on high-signal subset `top 20% abs(T11)`.
- else: evaluate on full profile.
- require all three:
  - `abs(pearson) > 0.2`
  - `abs(spearman) > 0.2`
  - `R2 > 0.05`

This is a candidate estimator for robustness diagnostics, not the official decision gate.

## Pre-registered protocol

- Datasets: `DS-002, DS-003, DS-006`
- Seeds: `3401..3600` (200 each, total 600)
- Fixed phi scale: `0.08`
- Fixed candidate thresholds:
  - `low_signal_ratio = 10.0`
  - `high_signal_quantile = 0.80`
  - `corr_min = 0.2`
  - `r2_min = 0.05`
- Promotion rule: v2 becomes official only if pass is `600/600` under this frozen protocol.

## Results (frozen run)

Evidence path:

- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/report.md`
- `05_validation/evidence/artifacts/g16b-v2-candidate-prereg-v1/prereg_manifest.json`

Observed:

- `G16b-v1` fails: `127/600`
- `G16b-v2` fails: `113/600`
- improved (`v1 fail -> v2 pass`): `43`
- degraded (`v1 pass -> v2 fail`): `29`
- v2 pass total: `487/600` (target `600/600` not met)

By dataset:

- DS-002: v1 fail `42`, v2 fail `40`
- DS-003: v1 fail `41`, v2 fail `41`
- DS-006: v1 fail `44`, v2 fail `32`

By signal regime:

- low-signal profiles (`n=210`): v1 fail `60`, v2 fail `17` (strong improvement)
- full-signal profiles (`n=390`): v1 fail `67`, v2 fail `96` (degradation)

## Decision

- `G16b-v2` is **not eligible for promotion** under current pre-registered criterion.
- Keep `G16b-v1` official.
- Keep `G16b-v2` as candidate diagnostic while refining definition before any new prereg run.

## Next hardening direction (no immediate gate switch)

- Preserve v1 behavior in full-signal regime and apply robust diagnostics only in low-signal regime.
- Keep reporting both v1 and v2 side-by-side for at least one release cycle.

## Split-Protocol Follow-up (v1, prereg)

Date: 2026-03-01

Implemented diagnostic split candidate:

- signal index: `p90(|T11|)`
- regime split:
  - `low` if `p90(|T11|) <= 0.024`
  - `high` otherwise
- low gate (robust): `abs(Pearson_hs)>0.2`, `abs(Spearman_hs)>0.2`, `R2_hs>0.05`
- high gate (physics-leaning): `abs(Pearson_full)>0.2`, `abs(cosine_full)>0.2`, `R2_origin_full>0.05`

Evidence:

- `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-protocol-prereg-v1/report.md`

Observed on DS-002/003/006 x seeds 3401..3600:

- v1 fail: `127/600`
- split fail: `100/600` (overall better)
- low-signal fail: `62 -> 20` (improves)
- high-signal fail: `65 -> 80` (degrades)

Decision:

- split-v1 is **not acceptable yet** for promotion because it violates the prereg non-degradation condition in high-signal regime.
- keep `G16b-v1` official and keep split policy as diagnostic-only candidate.

## Hybrid Split Follow-up (v1, prereg)

Date: 2026-03-01

To avoid post-hoc tuning in high-signal regime:

- low-signal rule and thresholds remain exactly the pre-registered `G16b-v2` definition.
- high-signal regime uses unchanged legacy `G16b-v1`.

Hybrid policy:

- if `is_low_signal=true` (from v2 prereg; `std(T11)/|mean(T11)| > 10`) -> decision = `g16b_v2`
- else -> decision = `g16b_v1`

Evidence:

- `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/summary.csv`
- `05_validation/evidence/artifacts/g16b-split-hybrid-prereg-v1/report.md`

Observed on DS-002/003/006 x seeds 3401..3600:

- `g16b_v1` fail: `127/600`
- `g16b_hybrid` fail: `84/600`
- improved vs v1: `43`
- degraded vs v1: `0`
- low-signal fail: `60 -> 17`
- high-signal fail: `67 -> 67` (non-degradation preserved)

Decision:

- hybrid-v1 is acceptable as **next promotion candidate** under prereg checks.
- official gate remains `G16b-v1` until promotion rule is explicitly frozen and completed.
