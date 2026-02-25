# QNG-T-CURL-005 — Residual Curl, no synthetic base, hard controls (v1 prereg)

## Definitions
- a_newton = -g^{-1} ∇Σ (per anchor, emergent metric v4, proxy ∇Σ from metric diagonals/off-diagonals).
- a_lag = τ * v·x (direction v_iso=[1,1] or v_grad=[1,0.5]).
- a_total = a_newton + a_lag (no synthetic g·x term).
- proj_grad(v) = projection of v on ∇Σ.
- a_res = a_total − proj_grad(a_total).
- curl_abs = |curl(a_res)| from local linear fit on chart; curl_rel = curl_abs / (||a_res|| + ε), ε=1e-12.

## Controls
- rewire_strong: off-diagonal random sign flip with 3× scaling.
- block_shuffle: shuffle ∇Σ proxy within |∇Σ| quantile bins (25/50/75%).

## Gates
- C1’: median curl_rel(static_res) ≤ 1e-4.
- C2’: lag_factor = max(median(lag_iso), median(lag_grad)) / median(static) ≥ 1.5.
- C3’: rewire_factor = median(rewire) / median(static) ≥ 2.0. (block factor recorded, not gated v1)
- C4’: τ sweep (0, τ0, 2τ0, 4τ0, τ0=1): medians non-decreasing AND median(4τ0) ≥ 1.5× median(0).
- FINAL: all gates pass.

## Run settings
- Datasets: DS-002 / DS-003 / DS-006 (v4 artifacts).
- Anchors: 72 @ scale 1s0, seed 20260224.
- Outputs: gate_summary.csv (with info rows), curl_rel_values.csv, curl_abs_values.csv, run-log.txt.

## Anti-tuning
No gate edits after seeing results; changes require curl-006 prereg.***
