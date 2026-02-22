# Pre-Registration - QNG Metric Hardening v1

- Date: 2026-02-21
- Test ID: `QNG-T-METRIC-001`
- Scope: emergent continuous metric hardening from coarse-grained graph distances
- Lock dependencies:
  - `01_notes/metric/metric-lock-v1.md`
  - `03_math/derivations/qng-core-emergent-metric-v1.md`

## Fixed Command (v1)

```powershell
.\.venv\Scripts\python.exe scripts\run_qng_metric_hardening_v1.py `
  --dataset-id DS-002 `
  --scales "s0,1.25s0,1.5s0" `
  --samples 72 `
  --seed 1401 `
  --out-dir "05_validation/evidence/artifacts/qng-metric-hardening-v1"
```

## Inputs (Locked)

- dataset id: `DS-002` (or alternate DS only as new prereg run record, same gates)
- scales: `s0,1.25s0,1.5s0`
- anchor sampling policy: top-`Sigma` + stratified random
- chart method: two-landmark geodesic tangent chart
- distance normalization: divide by median edge length

## Gates (Locked)

### Gate D1 - SPD / Signature

- Compute eigenvalues of local metric `g(p)`.
- Pass condition (space metric):
  - `min_eig >= eps`
- Locked value:
  - `eps = 1e-8`

### Gate D2 - Coarse-Grain Stability

For `s in {1.25s0,1.5s0}`:

```text
Delta_g(s) = ||g(s)-g(s0)||_F / ||g(s0)||_F
```

Pass:
- `median(Delta_g) <= 0.10`
- `p90(Delta_g) <= 0.25`

### Gate D3 - Compatibility with Sigma Field

Compare directions:

```text
a^i ~= -g^{ij} partial_j Sigma
```

using cosine similarity vs raw `-nabla Sigma`.

Pass:
- `median(cos_sim) >= 0.90`
- `p10(cos_sim) >= 0.70`

### Gate D4 - Negative Control (Must Collapse)

Permutation control:
- shuffle `Sigma` labels across nodes.

Pass if collapse occurs:
- `median(cos_sim_shuffled) < 0.55`

## Stop Conditions (Anti-Tuning)

- If D1 fails:
  - no gate edits; only new lock version (`metric-lock-v2.md`) with new prereg.
- If D2 fails:
  - change coarse-grain method only in a new version; no hidden edits.
- If D4 does not collapse:
  - test is invalid for claimed mechanism.

## Output Requirement

Runner must output at minimum:
- `metric_checks.csv`
- `eigs.csv`
- `drift.csv`
- `align_sigma.csv`
- `run-log.txt`
- `config.json`

