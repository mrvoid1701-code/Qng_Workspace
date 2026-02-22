# Evidence - QNG-T-050

- Priority: P2
- Claim: QNG-C-103
- Claim statement: Cosmic expansion corresponds to proliferation of stable nodes and relational complexity.
- Derivation: `03_math/derivations/qng-c-103.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-050-cosmo_sim.md`
- Current status: pass

## Objective

Cosmic expansion corresponds to proliferation of stable nodes and relational complexity.

## Formula Anchor

```text
a(t) proportional to |N(t)|^(1/3)
```

## Dataset / Environment

- Cosmological toy simulation / synthetic catalogs
- Operational dataset id: `DS-002` (local simulation suite)

## Method

- Simulate node-growth + memory dynamics and test scaling/signature predictions.
- Evaluate robustness across multiple seeds with fixed parameterization.
- Test direct coupling between expansion proxy and node proliferation.
- Test whether relational complexity co-grows with stable node count.

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
| Fit summary | `05_validation/evidence/artifacts/qng-t-050/fit-summary.csv` | Main pass metrics |
| Robustness per run | `05_validation/evidence/artifacts/qng-t-050/robustness-runs.csv` | Seed-by-seed diagnostics |
| Stability report | `05_validation/evidence/artifacts/qng-t-050/parameter-stability.md` | CV summary |
| Expansion/complexity plot | `05_validation/evidence/artifacts/qng-t-050/expansion-complexity.png` | a_obs vs N_norm vs C_norm |
| Time-series table | `05_validation/evidence/artifacts/qng-t-050/simulation-timeseries.csv` | Reference run |
| Run log | `05_validation/evidence/artifacts/qng-t-050/run-log.txt` | Full configuration snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `corr(a_obs, (N/N0)^(1/3))` mean | `0.999429` | `>= 0.96` | pass |
| `corr(complexity, N)` mean | `0.999997` | `>= 0.86` | pass |
| `slope(complexity vs N)` mean | `0.312673` | `> 0` | pass |
| `corr(expansion, complexity)` mean | `0.967648` | informational | pass |
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
- Rationale: DS-002 cosmo suite reproduces expansion-proliferation-complexity coupling across 18 runs.
- Last updated: 2026-02-16
- Authenticity: bronze
- Leakage risk: med
- Negative control: planned
