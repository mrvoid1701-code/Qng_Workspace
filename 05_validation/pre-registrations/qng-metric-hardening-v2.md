# Pre-Registration - QNG Metric Hardening v2

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-002`
- Scope: emergent continuous metric hardening from **dynamic Sigma Hessian** estimator
- Lock dependencies:
  - `01_notes/metric/metric-lock-v2.md`
  - `03_math/derivations/qng-core-emergent-metric-v1.md`

## Fixed Command (v2)

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v2.py `
  --dataset-id DS-002 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 2401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v2"
```

## Inputs (Locked)

- dataset id: `DS-002` (other datasets allowed only as new prereg run record)
- scales: `s0,1.25s0,1.5s0`
- anchor sampling: top-`Sigma` + stratified random
- chart method: two-landmark geodesic tangent chart
- Sigma smoothing kernel: Gaussian in local graph distances
- metric estimator: SPD projection of `-Hessian(Sigma_s)`

## Gates (Locked)

### Gate D1 - SPD / Signature

- Pass: `min_eig >= eps`
- Locked: `eps = 1e-8`

### Gate D2 - Coarse-Grain Stability

For `s in {1.25s0,1.5s0}`:

```text
Delta_g(s) = ||g(s)-g(s0)||_F / ||g(s0)||_F
```

Pass:
- `median(Delta_g) <= 0.10`
- `p90(Delta_g) <= 0.25`

### Gate D3 - Compatibility with Sigma Field

```text
a^i ~= -g^{ij} partial_j Sigma
```

Pass:
- `median(cos_sim) >= 0.90`
- `p10(cos_sim) >= 0.70`

### Gate D4 - Negative Control (Must Collapse)

- Shuffle `Sigma` labels across nodes.
- Recompute `g_shuf` and `grad_shuf`.
- Compare shuffled metric-driven direction against original raw `-nabla Sigma` direction.

Pass if collapse:
- `median(cos_sim_shuffled) < 0.55`

## Stop Conditions (Anti-Tuning)

- If any gate fails: keep gates unchanged.
- Method changes require `metric-lock-v3.md` + new prereg.

## Output Requirement

Required artifacts:
- `metric_checks.csv`
- `eigs.csv`
- `drift.csv`
- `align_sigma.csv`
- `run-log.txt`
- `config.json`

