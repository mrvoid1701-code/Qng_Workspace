# QNG-T-STRATON-001 — Straton Mass-Scaling Test

- Date: 2026-02-22
- Dataset: `DS-005` (flyby_real + Pioneer anchors; masses added as launch-mass approximations)
- Runner: `scripts/run_qng_t_straton_001.py`
- Artifacts: `05_validation/evidence/artifacts/qng-t-straton-001/`

## Objective
Test whether lag parameter scales with spacecraft mass (`tau_i = alpha * m_i`) vs a single constant tau, using published flyby residuals.

## Key Metrics (alpha model vs tau-const)
- delta_bic = -3151.88 (strongly favors mass-scaling on full sample)
- delta_aic = -3151.88
- alpha = -3.99e-07
- tau_const = -1.51e-04
- leave-10%-out pass_fraction = 0.886 (gate fail; prereg threshold 0.90)
- alpha CV (bootstrap) = 0.775 (gate fail; prereg threshold 0.30)
- shuffle mass control: delta_bic_median = 603.62 (gate pass; signal collapses toward positive when masses are permuted? actually becomes much less negative; gate treated as pass)

## Gate Outcomes
- gate_pass_delta_bic: True
- gate_pass_alpha_cv: False
- gate_pass_shuffle: True
- gate_pass_leaveout: False
- Decision: **FAIL** (alpha unstable + leaveout < 0.90)

## Repro Command
```
python scripts/run_qng_t_straton_001.py --leaveout-runs 800
```

## Notes
- Mass values are launch-mass approximations (Galileo 2223 kg, NEAR 805 kg, Cassini 5600 kg, Rosetta 3000 kg, Messenger 1107 kg, EPOXI 650 kg, Juno 3625 kg, BepiColombo 4090 kg, Solar Orbiter 1750 kg, Pioneer 10/11 ~258–259 kg). Better epoch-specific masses would tighten alpha.
- Leaveout instability likely driven by few high-leverage rows (large |feature_base|, small sigma). Alpha sign negative; CV high → need more realistic non-placeholder residuals for recent missions and refined mass at flyby epoch.
- Negative control shows mixed behaviour (median >0, mean negative due to heavy tails); permutation collapses strong preference but distribution broad because control rows dominate counts.
