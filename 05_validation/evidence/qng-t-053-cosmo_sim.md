# Evidence - QNG-T-053

- Priority: P2
- Claim: QNG-C-111
- Claim statement: Time arrow is irreversible update ordering and entropy scales with count of stable reconfigurations.
- Derivation: `03_math/derivations/qng-c-111.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-053-cosmo_sim.md`
- Current status: pass

## Objective

Time arrow is irreversible update ordering and entropy scales with count of stable reconfigurations.

## Formula Anchor

```text
S(t) = k_S * log(Omega(t))
```

## Dataset / Environment

- Cosmological toy simulation / synthetic catalogs
- Operational dataset id: `DS-002` (local simulation suite)

## Method

- Simulate node-growth + memory dynamics and test scaling/signature predictions.
- Track cumulative stable reconfigurations `Omega(t)` during updates.
- Fit `S_obs(t) = k * log(Omega(t))` and evaluate goodness-of-fit.
- Verify irreversible ordering via monotonic `Omega(t)` and near-monotonic entropy progression.

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
| Fit summary | `05_validation/evidence/artifacts/qng-t-053/fit-summary.csv` | Main entropy/time-arrow metrics |
| Robustness per run | `05_validation/evidence/artifacts/qng-t-053/robustness-runs.csv` | Seed-by-seed diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-053/parameter-stability.md` | CV summary |
| Entropy plot | `05_validation/evidence/artifacts/qng-t-053/entropy-time-arrow.png` | `S_obs` vs fitted `k*log(Omega)` |
| Time-series table | `05_validation/evidence/artifacts/qng-t-053/simulation-timeseries.csv` | Reference run |
| Run log | `05_validation/evidence/artifacts/qng-t-053/run-log.txt` | Full configuration snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `k_fit` mean | `1.000101` | `> 0` | pass |
| `R^2(S_obs vs k*log(Omega))` mean | `0.999634` | `>= 0.94` | pass |
| `Omega` monotonic ratio mean | `1.000000` | `>= 0.99` | pass |
| Entropy monotonic ratio mean | `0.954321` | `>= 0.90` | pass |
| Rule summary | `True, True, True, True` | all true | pass |

## Pass / Fail Criteria

- Pass: Predicted scaling/signatures appear across reasonable parameter bands without ad-hoc tuning.
- Fail: Signatures absent or only appear under nonphysical/extreme parameter tuning.

## Decision

- Decision: pass
- Rationale: Entropy-log(Omega) scaling and irreversible update ordering validated across DS-002 suite runs.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
