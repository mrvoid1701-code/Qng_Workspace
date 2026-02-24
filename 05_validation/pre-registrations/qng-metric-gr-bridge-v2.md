# Pre-registration: QNG-T-METRIC-006 (GR Bridge v2, Frobenius iso 1/sqrt(2))

- Scope: GR bridge gates for v4 metric (Frobenius normalization).
- Iso reference: 1/sqrt(2) ≈ 0.707107 (replaces v1 iso=0.5).
- Artifact dirs: `qng-metric-hardening-v4-ds002, qng-metric-hardening-v4-ds003, qng-metric-hardening-v4-ds006`.
- Scale_ref: `1s0`.

## Gates
- B1: weak-field perturbation — median(h) ≤ 0.20 and p90(h) ≤ 0.32.
- B2: metric sanity — min_eig ≥ 0.25 and cond_p90 ≤ 2.50.
- B3: Newton direction — cos_raw median ≥ 0.95 and p10 ≥ 0.90.
- B4: continuum stability — drift median ≤ 0.07 and p90 ≤ 0.20.
- B5: control separation — raw_minus_shuffled_median ≥ 0.90.
- FINAL: pass if all B1–B5 pass.

## Fixed
- Inputs: eigs.csv, align_sigma.csv, drift.csv, metric_checks.csv per dataset.
- Iso_ref default 1/sqrt(2); scale_ref fixed 1s0.
- No thresholds retuning after run.

## Free (allowed)
- Artifact dirs can be extended with new datasets (same gate thresholds).
- Out dir path.
