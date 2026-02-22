# Pre-registration: QNG-T-STRATON-001

- Claim: `QNG-C-014` (tau depends on chi; straton relevance)
- Hypothesis: tau scales with spacecraft mass (tau_i = alpha * m_i) rather than a single global tau.
- Dataset: `DS-005` flyby_real + Pioneer anchors; requires column `spacecraft_mass_kg`.
- Model A (null): tau = tau0 (constant).
- Model B (straton): tau_i = alpha * m_i.

## Gates
1) delta_bic = bic_B - bic_A <= -10 (strong support for mass-scaling).
2) alpha stability: CV_bootstrap(alpha) < 0.30.
3) Negative control (shuffle masses): delta_bic should collapse toward 0 or positive; gate if median delta_bic_shuffle > -2.
4) leave-10%-out: pass_fraction >= 0.90.

## Controls
- Mass shuffle (permute spacecraft_mass_kg across rows).
- Include control passes (declared `control` rows) in fits to test collapse behaviour.

## Fixed
- Feature: `feature_base_m_s3` from derived flyby file.
- Observed acceleration: `a_obs_whole_m_s2`.
- Weights: 1/sigma_whole^2 (fallback to sigma_perigee if zero, then 1e-18).
- Single-parameter fits (k=1) for both models.
- Random seeds: bootstrap 20260222, leaveout 20260223, shuffle 20260224.

## Free
- Number of resamples: bootstrap=400, leaveout=800, shuffle=400 (can increase, not decrease).
- Placeholder residuals for recent missions allowed but must be flagged; replacing them with published OD residuals is encouraged and does not change gates.

## Outputs
- fit-summary.csv
- bootstrap-alpha.csv
- straton-report.md
- run-log.txt

## Pass/Fail
- Pass only if all gates 1–4 are true.
- Fail otherwise; do not retune thresholds post-run.
