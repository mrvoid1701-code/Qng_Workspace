# QNG-T-CURL-003 — Discrete Curl Relative (v1 prereg)

## Scope
Detect non-conservative component induced by lag term using normalized curl on emergent metric charts (v4 artifacts). Runs on DS-002 / DS-003 / DS-006 with fixed seeds and sampling identical to CURL-002.

## Definitions
- curl\_abs: |curl(a)| from local linear fit of acceleration field.
- curl\_rel: curl\_abs / (||a|| + ε), with ε = 1e-12.
- Configs: scale = `1s0`, samples = 72, seed = 20260224, tau sweep τ ∈ {0, τ0, 2τ0, 4τ0} with τ0 = 1.0.
- Variants: static (τ=0), lag\_iso (τ0, v_iso=[1,1]), lag\_grad (τ0, v_grad=[1,0.5]), rewired control (off-diagonal sign flipped, τ=0).

## Gates
- C1 (smallness): median(curl\_rel_static) < 1e-8.
- C2 (lag boost): max(median(lag\_iso), median(lag\_grad)) / median(static) ≥ 1.15.
- C3 (rewire control): median(rewired) / median(static) ≥ 2.5.
- C4 (monotonic τ): medians across τ sweep are non-decreasing and median(τ=4τ0) ≥ 1.5 × median(τ=0).
- FINAL: pass iff C1–C4 all pass.

## Outputs
- `gate_summary.csv` with rel metrics, ratios, decisions.
- `curl_rel_values.csv` and `curl_abs_values.csv` per anchor.
- `run-log.txt` JSON with parameters used.

## No post-hoc tuning
If gates fail, next version must be `curl-004` with a new prereg; do not change thresholds after seeing results.
