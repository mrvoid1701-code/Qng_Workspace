# QNG-T-CURL-003-v2 — Curl with spatially varying metric (prereg)

**Status:** Locked before implementation  
**Datasets:** DS-002 / DS-003 / DS-006 (metric v4 artifacts)  
**Anchors:** 72 @ scale 1s0, seed 20260225  
**Tau:** τ0 = 1.0; directions v_iso = [1,1], v_grad = [1,0.5]

## Motivation
CURL-002 fails C2/C3 because constant-metric approximation makes a_lag curl-free. This version computes g(x,y) and H(x,y) across the local chart to recover non-zero curl.

## Method (per anchor)
1. Build local chart grid (≥5×5 points) in chart coords using neighboring nodes.  
2. Bilinear-interpolate Σ on the grid; compute Hessian H(x,y) by finite differences.  
3. Compute metric per point: g(x,y) = metric_from_sigma_hessian_v4(H(x,y)); invert to g⁻¹(x,y).  
4. Compute a_lag(x,y) = −τ · g⁻¹(x,y) · H(x,y) · v for v ∈ {v_iso, v_grad}.  
5. Fit linear model (x,y) → a_lag(x), a_lag(y); curl_z = ∂x a_y − ∂y a_x.  
6. curl_rel = |curl| / (||a|| + ε), ε = 1e-12.
7. Controls: rewired metric (random sign flip on off-diagonal, +30% noise) recompute steps 3–6.

## Gates
- C1: median(curl_rel_static) < 1e-8  
- C2: median(curl_rel_lag_iso) > 10 × median(curl_rel_static)  
- C3: median(curl_rel_rewired) > 10 × median(curl_rel_static)  
- FINAL: all above pass

## Outputs
- gate_summary.csv (C1–C3)  
- curl_rel_values.csv per anchor (static / lag_iso / lag_grad / rewired)  
- run-log.txt (params, seeds)  
- Optional: diagnostic plots of curl distribution

## Anti-tuning
If gates fail, next version must be curl-003-v3 with a fresh prereg; do not edit thresholds after seeing results.
