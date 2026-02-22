# Evidence - QNG-T-013

- Priority: P3
- Claim: QNG-C-029
- Claim statement: Universe dynamics follow discrete updates `N_i(t+1)=U(...)`.
- Derivation: `03_math/derivations/qng-c-029.md`
- Core closure note: `01_notes/core-closure-v1.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-013-formal_math.md`
- Current status: pass

## Objective

Verify that the discrete update claim is closed mathematically and executable with non-ambiguous volume dynamics.

## Formula Anchor

```text
N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))
```

## Dataset / Environment

- Symbolic math + dimensional analysis (`DS-007`)
- Cosmo toy simulation closure audit (`DS-002`)

## Method

1. Symbolic closure check (`formal_math`) on derivation text.
2. Executable closure gates (`T-V-01..T-V-04`) comparing `V-A` vs `V-B` rules.
3. Freeze rule selection for v1 only if a single rule passes all closure gates.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Symbolic closure check (legacy P3 gate)
.\.venv\Scripts\python.exe scripts\run_qng_p3_symbolic_validation.py `
  --test-id QNG-T-013 `
  --claim-id QNG-C-029 `
  --mode formal_math `
  --dataset-id DS-007 `
  --derivation "03_math/derivations/qng-c-029.md" `
  --formula-anchor "N_i(t+1) = U(N_i(t), {N_j(t)}_{j in Adj(i)}, eta_i(t))" `
  --seed 3013 `
  --out-dir "05_validation/evidence/artifacts/qng-t-013"

# 2) Core Closure v1 executable gate suite
.\.venv\Scripts\python.exe scripts\run_qng_t_v_volume_rules.py `
  --dataset-id DS-002 `
  --steps 180 `
  --runs 12 `
  --seed 920 `
  --out-dir "05_validation/evidence/artifacts/qng-tv-core-closure-v1"
```

## Inputs

| Input | Version / Date | Notes |
| --- | --- | --- |
| Derivation | `03_math/derivations/qng-c-029.md` (2026-02-21) | Closed update rule with explicit `V_i` dynamics |
| Core closure spec | `01_notes/core-closure-v1.md` (2026-02-21) | Frozen v1 ontology + conservation policy |
| Closure runner | `scripts/run_qng_t_v_volume_rules.py` | Executes `T-V-01..T-V-04` |
| Dataset manifest | `05_validation/dataset-manifest.json` | `DS-002`, `DS-007` references |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Symbolic fit summary | `05_validation/evidence/artifacts/qng-t-013/fit-summary.csv` | Legacy formal check |
| Closure fit summary | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/fit-summary.csv` | Rule-level gate summary |
| Rule comparison | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/rule-comparison.csv` | Pass rates per gate and rule |
| Robustness table | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/robustness-runs.csv` | Per-seed diagnostics |
| Time-series (V-A/V-B) | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/simulation-timeseries-v-a.csv`, `simulation-timeseries-v-b.csv` | Closure trajectories |
| Plot | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/volume-rules-timeseries.png` | Rule behavior overview |
| Run log | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/run-log.txt` | Full configuration snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `V-B` pass rate `T-V-01` (growth gate) | `1.000000` | `>= 0.80` | pass |
| `V-B` pass rate `T-V-02` (spectrum gate) | `1.000000` | `>= 0.80` | pass |
| `V-B` pass rate `T-V-03` (attractor gate) | `1.000000` | `>= 0.80` | pass |
| `V-B` pass rate `T-V-04` (GR kill-switch) | `1.000000` | `>= 0.95` | pass |
| `V-B` selected for closure v1 | `true` | all gates pass | pass |
| `V-A` aggregate recommendation | `fail` | comparator only | expected-fail |

## Pass / Fail Criteria

- Pass: Closed discrete update rule is executable and one frozen v1 volume rule passes all closure gates.
- Fail: No rule passes closure gates, or closure requires post-hoc gate edits to pass.

## Decision

- Decision: pass
- Rationale: `C-029` now has executable closure; `V-B` passes `T-V-01..T-V-04` at `12/12` pass rates and is frozen as the v1 volume rule.
- Last updated: 2026-02-21
- Authenticity: silver
- Leakage risk: low
- Negative control: done

