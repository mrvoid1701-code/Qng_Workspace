# Evidence - QNG-T-051

- Priority: P2
- Claim: QNG-C-104
- Claim statement: Emergent scale factor follows cube-root scaling with node count.
- Derivation: `03_math/derivations/qng-c-104.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-051-cosmo_sim.md`
- Current status: pass

## Objective

Emergent scale factor follows cube-root scaling with node count.

## Formula Anchor

```text
a(t) = (|N(t)|/|N(t0)|)^(1/3)
```

## Dataset / Environment

- Cosmological toy simulation / synthetic catalogs
- Operational dataset id: `DS-002` (local simulation suite)

## Method

- Simulate node-growth + memory dynamics and test scaling/signature predictions.
- Build `a_model(t) = (N(t)/N(t0))^(1/3)` from simulated node count.
- Compare observed expansion proxy `a_obs(t)` vs `a_model(t)` across multiple seeds.
- Require high fit quality and low parameter-free error.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Run DS-002 P2 cosmo suite (covers QNG-T-050/051/053)
.\.venv\Scripts\python.exe scripts\run_qng_p2_cosmo_suite.py `
  --dataset-id DS-002 `
  --steps 180 `
  --runs 18 `
  --seed 410 `
  --sigma-min 0.34 `
  --base-growth 0.0105 `
  --memory-weight 0.22 `
  --noise-scale 1.0 `
  --artifact-root "05_validation/evidence/artifacts"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| DS-002 dataset definition | `05_validation/dataset-manifest.json` (2026-02-16) | Cosmo simulation family |
| Suite runner | `scripts/run_qng_p2_cosmo_suite.py` | Generates artifacts for 050/051/053 |
| Configuration | steps=`180`, runs=`18`, seed base=`410` | Fixed for reproducibility |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Fit summary | `05_validation/evidence/artifacts/qng-t-051/fit-summary.csv` | Main scale-factor metrics |
| Robustness per run | `05_validation/evidence/artifacts/qng-t-051/robustness-runs.csv` | Seed-by-seed diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-051/parameter-stability.md` | CV summary |
| Scale-factor plot | `05_validation/evidence/artifacts/qng-t-051/scale-factor-fit.png` | `a_obs` vs `a_model` |
| Time-series table | `05_validation/evidence/artifacts/qng-t-051/simulation-timeseries.csv` | Reference run |
| Run log | `05_validation/evidence/artifacts/qng-t-051/run-log.txt` | Full configuration snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `R^2(a_obs vs a_model)` mean | `0.998836` | `>= 0.97` | pass |
| `CV(R^2)` | `1.362912e-04` | `<= 0.03` | pass |
| `MAPE(a_obs, a_model)` mean | `0.008347` | `<= 0.03` | pass |
| Rule summary | `True, True, True` | all true | pass |

## Core Closure Supplement (2026-02-21)

Additional closure audit run:

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_t_v_volume_rules.py `
  --dataset-id DS-002 `
  --steps 180 `
  --runs 12 `
  --seed 920 `
  --out-dir "05_validation/evidence/artifacts/qng-tv-core-closure-v1"
```

Key supplementary outputs:
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/fit-summary.csv`
- `05_validation/evidence/artifacts/qng-tv-core-closure-v1/rule-comparison.csv`

Supplementary result:
- `selected_rule_v1 = V-B`
- `V-B` closure-gate pass rates (`T-V-01..04`) = `1.0, 1.0, 1.0, 1.0`

## Pass / Fail Criteria

- Pass: Predicted scaling/signatures appear across reasonable parameter bands without ad-hoc tuning.
- Fail: Signatures absent or only appear under nonphysical/extreme parameter tuning.

## Decision

- Decision: pass
- Rationale: Cube-root scale-factor relation validated with high fit quality and low drift across robustness runs.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
