# QNG-T-028 Sensitivity Scan (metric v4) — prereg

Scope: Robustness of T-028 (real flyby) to kernel hyperparameters.

Parameters scanned:
- anisotropy_keep ∈ {0.2, 0.3, 0.4, 0.5, 0.6}
- tau_universal ∈ {0.25, 0.40, 0.55}

Runs: 5×3 = 15 combinations, seed fixed = 20260225, dataset DS-005, script `scripts/run_qng_t_028_trajectory_real.py`.

Metric: Δchi² = chi2_total(memory) − chi2_total(baseline) (from model-comparison.md per run).

Gate:
- G1: Δchi² < 0 on ≥12 of 15 combos (memory better than baseline).
- FINAL: pass if G1 holds.

Outputs:
- artifacts per combo under `05_validation/evidence/artifacts/qng-t-028-sens-v4/comb_<ani>_<tau>/`
- summary CSV `sens_summary.csv` with columns (anisotropy_keep, tau_universal, delta_chi2, status)
- gate_summary.csv with G1 and FINAL
- run-log.txt (parameters, counts, seed)

Notes:
- Hyperparameters are passed through to the runner as env/context only; no post-hoc threshold edits allowed. If underlying script ignores them, record that limitation in the evidence narrative.***
