# QNG-T-CURL-004 — Residual Curl with Strong Controls (v1 prereg)

## Definitions
- a_newton = -g^{-1} ∇Σ (per anchor, using emergent metric g and local ∇Σ proxy).
- a_total = a_grad_linear + a_newton + a_lag, with a_lag along chosen direction.
- Projection: proj_grad(v) = projection of vector v on ∇Σ.
- Residual field: a_res = a_total − proj_grad(a_total).
- curl_abs = |curl(a_res)| from local linear fit; curl_rel = curl_abs / (||a_res|| + ε), ε = 1e-12.

## Controls
- rewire_strong: rewire metric off-diagonal with 30% perturbation / sign flip.
- block_shuffle: shuffle ∇Σ proxy across anchors within blocks (quantile-like) to break alignment.

## Gates (v1)
- C1’: median curl_rel(static_res) ≤ 1e-4.
- C2’: lag_factor_res = max(median(lag_iso), median(lag_grad)) / median(static) ≥ 1.5.
- C3’: rewire_factor_res = median(rewire) / median(static) ≥ 2.0. (block shuffle recorded, no gate)
- C4’: tau sweep monotone: medians for τ ∈ {0, τ0, 2τ0, 4τ0} non-decreasing AND median(4τ0) ≥ 1.5× median(0).
- FINAL: pass iff C1’–C4’ all pass.

## Run settings
- Datasets: DS-002 / DS-003 / DS-006 (v4 metric artifacts).
- Anchors: 72 @ scale 1s0, seed 20260224.
- τ0 = 1.0. Directions: v_iso = [1,1], v_grad = [1,0.5].

## Outputs
- gate_summary.csv (includes info rows + gates).
- curl_rel_values.csv, curl_abs_values.csv per anchor.
- run-log.txt with parameters.

## Anti-tuning
No threshold edits after results; any change requires curl-005 prereg.***
