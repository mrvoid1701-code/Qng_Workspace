# QNG Stability V1 Strict

Date: 2026-03-03  
Policy ID: `qng-stability-v1-strict`  
Status: frozen candidate lane (theory hardening)

## Scope

This lock defines the stability-focused contract for QNG core variables:

- `Sigma_i` (stability field, bounded in `[0,1]`)
- `chi_i` (straton/memory load)
- `phi_i` (phase state)

The lock is separate from GR/QM official gate governance and does not modify GR/QM thresholds.

## Freeze Rules

1. Equations and parameter symbols are frozen by:
   - `03_math/derivations/qng-stability-action-v1.md`
   - `03_math/derivations/qng-stability-update-v1.md`
2. Stress thresholds are frozen by:
   - `05_validation/pre-registrations/qng-stability-v1-strict.md`
3. Any model change requires:
   - new prereg version (`...-v2.md`),
   - new run ID,
   - explicit degraded/non-degraded comparison.

## Locked Deliverables

- one sweep runner:
  - `scripts/tools/run_stability_stress_v1.py`
- one evidence package root:
  - `05_validation/evidence/artifacts/stability-v1/`
- required outputs:
  - `summary.csv`
  - `gate_summary.csv`
  - `report.md`
  - `manifest.json`

Taxonomy package:

- `05_validation/evidence/artifacts/stability-v1-failure-taxonomy-v1/`
  - `fail_cases.csv`
  - `pass_cases.csv`
  - `pattern_summary.csv`
  - `feature_correlations.csv`
  - `report.md`
  - `run-log.txt`

## Stability Invariants (Hard Gates)

The strict lane checks:

1. boundedness: `0 <= Sigma <= 1`
2. metric positivity: diagonal metric proxy strictly positive
3. metric conditioning bound: `cond(g)` upper bounded
4. runaway guard: `max |chi|` bounded
5. perturbative backreaction:
   - `|delta_E / E|` bounded
   - variational residual bounded
   - `max |delta alpha / alpha|` bounded on active nodes (`|chi| >= chi_active_min`)
6. locality/no-signalling proxy:
   - one-step non-local response below tolerance

## Governance

Every improvement must include:

1. mathematical statement (equation-level),
2. prereg test protocol,
3. explicit FAIL criterion.

Candidate-v2 prereg anchor:

- `05_validation/pre-registrations/qng-stability-energy-covariant-v2.md`
- run record: `05_validation/pre-registrations/qng-stability-energy-covariant-v2-run-record-2026-03-03.md`

Candidate-v2 tooling/evidence:

- `scripts/tools/run_stability_energy_candidate_eval_v2.py`
- `scripts/tools/evaluate_stability_energy_promotion_v1.py`
- `scripts/tools/summarize_stability_energy_promotion_v1.py`
- `05_validation/evidence/artifacts/stability-energy-covariant-v2/`
- `05_validation/evidence/artifacts/stability-energy-promotion-eval-v1/`

Official switch record:

- `docs/STABILITY_ENERGY_V2_OFFICIAL_SWITCH.md`
- `docs/STABILITY_V2_FREEZE.md`

Noether/action alignment note:

- `03_math/derivations/qng-stability-noether-alignment-sketch-v1.md`

Convergence contract:

- `05_validation/pre-registrations/qng-stability-convergence-v1.md`
- `05_validation/pre-registrations/qng-stability-convergence-v1-run-record-2026-03-03.md`
- `05_validation/pre-registrations/qng-stability-convergence-v2.md`
- `05_validation/pre-registrations/qng-stability-convergence-v2-run-record-2026-03-03.md`
