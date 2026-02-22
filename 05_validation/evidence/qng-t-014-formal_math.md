# Evidence - QNG-T-014

- Priority: P3
- Claim: QNG-C-032
- Claim statement: Node stability is `Sigma_i in [0,1]` with multiplicative components.
- Derivation: `03_math/derivations/qng-c-032.md`
- Core closure note: `01_notes/core-closure-v1.md`
- Test plan source: `05_validation/test-plan.md`
- Evidence file: `05_validation/evidence/qng-t-014-formal_math.md`
- Current status: pass

## Objective

Verify bounded stability closure and confirm that `Sigma`-gated persistence supports a stable executable update regime.

## Formula Anchor

```text
Sigma_i = Sigma_chi * Sigma_struct * Sigma_temp * Sigma_phi
0 <= Sigma_i <= 1
```

## Dataset / Environment

- Symbolic math + dimensional analysis (`DS-007`)
- Core closure simulation gate suite (`DS-002`)

## Method

1. Symbolic boundedness/consistency check on derivation.
2. Closure execution under `V-A` and `V-B` to test:
   - spectrum behavior (`T-V-02`)
   - attractor/identity robustness (`T-V-03`)
   - GR-limit safety (`T-V-04`).
3. Accept stability closure only if frozen v1 rule remains robust.

## Reproducible Run

```powershell
# 0) Workspace integrity
.\.venv\Scripts\python.exe scripts\lint_workspace.py

# 1) Symbolic closure check (legacy P3 gate)
.\.venv\Scripts\python.exe scripts\run_qng_p3_symbolic_validation.py `
  --test-id QNG-T-014 `
  --claim-id QNG-C-032 `
  --mode formal_math `
  --dataset-id DS-007 `
  --derivation "03_math/derivations/qng-c-032.md" `
  --formula-anchor "Sigma_i = Sigma_chi * Sigma_struct * Sigma_temp * Sigma_phi" `
  --seed 3014 `
  --out-dir "05_validation/evidence/artifacts/qng-t-014"

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
| Derivation | `03_math/derivations/qng-c-032.md` (2026-02-21) | Bounded component maps and `tau=alpha_tau*chi` coupling |
| Core closure spec | `01_notes/core-closure-v1.md` (2026-02-21) | Frozen v1 update + conservation policy |
| Closure runner | `scripts/run_qng_t_v_volume_rules.py` | Executes gate suite |
| Dataset manifest | `05_validation/dataset-manifest.json` | `DS-002`, `DS-007` references |

## Outputs

| Artifact | Path | Notes |
| --- | --- | --- |
| Symbolic fit summary | `05_validation/evidence/artifacts/qng-t-014/fit-summary.csv` | Legacy formal check |
| Closure fit summary | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/fit-summary.csv` | Rule-level gate summary |
| Rule comparison | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/rule-comparison.csv` | Pass rates per gate and rule |
| Stability report | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/parameter-stability.md` | CV and dispersion metrics |
| Windows JSD table | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/stationarity-windows.csv` | Spectrum-drift diagnostics |
| Run log | `05_validation/evidence/artifacts/qng-tv-core-closure-v1/run-log.txt` | Full configuration snapshot |

## Metrics

| Metric | Value | Threshold | Status |
| --- | --- | --- | --- |
| `V-B` pass rate `T-V-02` (stability-spectrum gate) | `1.000000` | `>= 0.80` | pass |
| `V-B` pass rate `T-V-03` (identity/attractor gate) | `1.000000` | `>= 0.80` | pass |
| `V-B` pass rate `T-V-04` (GR kill-switch gate) | `1.000000` | `>= 0.95` | pass |
| `V-B` `jsd_mean` aggregate | `0.003827` | controlled drift | pass |
| `V-B` selected for closure v1 | `true` | all gates pass | pass |

## Pass / Fail Criteria

- Pass: Stability closure remains bounded and robust under the frozen executable rule.
- Fail: Stability breaks under perturbation/spectrum gates or GR-limit sanity gate.

## Decision

- Decision: pass
- Rationale: `Sigma`-gated closure is mathematically bounded and operationally robust for frozen v1 rule `V-B` across all registered closure gates.
- Last updated: 2026-02-21
- Authenticity: silver
- Leakage risk: low
- Negative control: done

