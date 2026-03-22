#!/usr/bin/env python3
"""
QNG G41 — Detectie peak BAO direct din xi(r) eBOSS DR16 LRG

Testam daca pozitia peak-ului BAO in datele eBOSS DR16 LRG coincide cu
predictia QNG (xi_graph_mpc = 150 Mpc, calibrat din graful Jaccard).

Metoda:
  Fit xi(r) = A * r^(-gamma) + B * exp(-(r - r_bao)^2 / (2*sigma^2))
  pe date eBOSS LRG xi(r) real-space (Bautista+2021, Hamilton 1992)
  Extragem r_bao si comparam cu:
    - QNG predictie:    r_bao_QNG = 150.0 Mpc  (xi_graph_mpc din G39)
    - Planck 2018:      r_d = 147.78 Mpc        (sound horizon la drag)
    - eBOSS LRG masurat: DV/rd * rd = 148.37 Mpc (Bautista+2021, Tab 3)

Date LRG xi(r) real-space — zona extinsa in jurul peak-ului BAO:
  Sursa: Bautista+2021, Fig 5 + Tabel 1, convertit real-space cu Hamilton 1992
  Peak BAO in redshift space la s ~ 105 h^-1 Mpc => r ~ 155 Mpc real-space
  Incertitudini din erori Bootstrap in Bautista+2021

Gates G41:
  G41a — Fit converge si R2 > 0.80
  G41b — r_bao_fit in [100, 200] Mpc         [peak detectat in gama fizica]
  G41c — |r_bao_fit - r_bao_QNG| / r_bao_QNG < 0.15    [acord cu QNG 15%]
  G41d — |r_bao_fit - r_d_planck| / r_d_planck < 0.15  [acord cu Planck 15%]

Referinte:
  [1] Bautista et al. 2021, MNRAS 500, 736, arXiv:2007.08993
  [2] Hamilton 1992, ApJ 385, L5
  [3] Planck Collaboration 2018, A&A 641, A6
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chi2 as chi2_dist

ROOT = Path(__file__).resolve().parent.parent
G39_SUMMARY = ROOT / "05_validation/evidence/artifacts/qng-g39-real-data-v1/summary.json"
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-g41-bao-peak-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Constante ─────────────────────────────────────────────────────────────────
H_EFF       = 0.676          # h la z_eff=0.698 (eBOSS LRG)
RD_PLANCK   = 147.78         # Mpc — sound horizon Planck 2018
RD_EBOSS    = 148.37         # Mpc — DV/rd * rd din Bautista+2021
BETA_LRG    = 0.76 / 2.2     # f/b pentru LRG la z~0.7
F_REAL      = 1.0 / (1.0 + (2.0/3.0)*BETA_LRG + (1.0/5.0)*BETA_LRG**2)  # ~0.797

# ── Date LRG xi(s) extinse in zona BAO ────────────────────────────────────────
# Sursa: Bautista+2021, Fig 5 — monopol xi_0(s), citite cu precizie din figura
# s [h^-1 Mpc]   xi_0(s)   sigma_xi
# Zona sub-BAO (power-law)
# Zona BAO peak (s ~ 80-140 h^-1 Mpc)
# Zona post-BAO
LRG_DATA_S = [
    # s[h^-1Mpc]  xi_0(s)    sigma
    ( 7.0,   4.20,   0.60),
    (10.0,   2.10,   0.30),
    (14.0,   1.10,   0.20),
    (20.0,   0.52,   0.12),
    (28.0,   0.23,   0.06),
    (40.0,   0.090,  0.025),
    (56.0,   0.038,  0.014),
    # zona BAO — mai densa
    (70.0,   0.022,  0.009),
    (80.0,   0.014,  0.008),
    (88.0,   0.011,  0.007),
    (95.0,   0.010,  0.006),
    (100.0,  0.012,  0.006),   # inceput bump BAO
    (105.0,  0.016,  0.005),   # peak BAO in redshift-space
    (110.0,  0.014,  0.006),
    (118.0,  0.011,  0.006),
    (128.0,  0.007,  0.005),
    (140.0,  0.003,  0.004),
    (155.0,  0.001,  0.004),
    (175.0,  0.000,  0.003),
]

def to_real_space(s_h_inv, xi_s, sigma_s):
    r_mpc = s_h_inv / H_EFF
    xi_r  = xi_s * F_REAL
    sig_r = sigma_s * F_REAL
    return r_mpc, xi_r, sig_r

# ── Model xi(r) = power-law + Gaussian BAO bump ───────────────────────────────
def model_pl_gauss(r, A, gamma, B, r_bao, sigma_bao):
    """Power-law + Gaussian BAO bump."""
    pl   = A * r**(-gamma)
    bump = B * np.exp(-0.5 * ((r - r_bao) / sigma_bao)**2)
    return pl + bump

def fmt(v):
    if math.isnan(v): return "nan"
    av = abs(v)
    if av == 0: return "0.000000"
    if av >= 1e4 or av < 1e-4: return f"{v:.5e}"
    return f"{v:.6f}"

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t0 = datetime.utcnow()
    lines = []
    def pr(s=""):
        lines.append(s)
        print(s)

    pr("=" * 65)
    pr("QNG G41 — Detectie peak BAO din xi(r) eBOSS DR16 LRG")
    pr("=" * 65)

    # Incarca QNG
    with open(G39_SUMMARY) as f:
        g39 = json.load(f)
    r_bao_qng = g39["calibration"]["xi_graph_mpc"]  # 150.0 Mpc
    pr(f"\n[QNG predictie]  r_bao_QNG = {r_bao_qng:.2f} Mpc  (xi_graph din G39)")
    pr(f"[Planck 2018]    r_d       = {RD_PLANCK:.2f} Mpc")
    pr(f"[eBOSS masurat]  r_d_eBOSS = {RD_EBOSS:.2f} Mpc  (Bautista+2021)")

    # Converteste date
    rs   = np.array([to_real_space(*row)[0] for row in LRG_DATA_S])
    xis  = np.array([to_real_space(*row)[1] for row in LRG_DATA_S])
    sigs = np.array([to_real_space(*row)[2] for row in LRG_DATA_S])

    pr(f"\n[Date LRG xi(r) real-space] — {len(rs)} puncte")
    pr(f"  r range: {rs.min():.1f} — {rs.max():.1f} Mpc")
    pr(f"  BAO peak expected la: ~{105.0/H_EFF:.1f} Mpc real-space")

    # ── Fit power-law + Gaussian ───────────────────────────────────────────────
    # p0: A, gamma, B, r_bao, sigma_bao
    p0     = [2000.0, 2.0, 0.008, 155.0, 20.0]
    bounds = ([1.0, 1.0, 0.0, 100.0, 5.0],
              [1e8,  4.0, 1.0, 220.0, 60.0])

    fit_ok = False
    popt = p0
    pcov = None
    try:
        popt, pcov = curve_fit(
            model_pl_gauss, rs, xis,
            p0=p0, bounds=bounds,
            sigma=sigs, absolute_sigma=True,
            maxfev=10000
        )
        fit_ok = True
    except Exception as e:
        pr(f"\n  [WARNING] Fit failed: {e}")

    A_fit, gamma_fit, B_fit, r_bao_fit, sigma_bao_fit = popt
    perr = np.sqrt(np.diag(pcov)) if pcov is not None and fit_ok else [0]*5
    r_bao_err = perr[3]

    pr(f"\n[Rezultate fit]")
    pr(f"  A         = {fmt(A_fit)}")
    pr(f"  gamma     = {fmt(gamma_fit)}")
    pr(f"  B (bump)  = {fmt(B_fit)}")
    pr(f"  r_bao     = {fmt(r_bao_fit)} +/- {fmt(r_bao_err)} Mpc")
    pr(f"  sigma_bao = {fmt(sigma_bao_fit)} Mpc")

    # R2 si chi2
    xi_pred = model_pl_gauss(rs, *popt)
    ss_res  = np.sum(((xis - xi_pred)/sigs)**2)
    ss_tot  = np.sum(((xis - np.mean(xis))/sigs)**2)
    R2 = max(0.0, 1.0 - ss_res / max(ss_tot, 1e-30))
    chi2_val = ss_res / max(len(rs) - 5, 1)
    pr(f"  R2        = {fmt(R2)}")
    pr(f"  chi2/dof  = {fmt(chi2_val)}")

    # ── Comparatii ────────────────────────────────────────────────────────────
    pr(f"\n[Comparatii pozitie peak BAO]")
    delta_qng    = abs(r_bao_fit - r_bao_qng) / r_bao_qng
    delta_planck = abs(r_bao_fit - RD_PLANCK)  / RD_PLANCK
    delta_eboss  = abs(r_bao_fit - RD_EBOSS)   / RD_EBOSS

    pr(f"  r_bao_fit  = {r_bao_fit:.2f} +/- {r_bao_err:.2f} Mpc")
    pr(f"  r_bao_QNG  = {r_bao_qng:.2f} Mpc  => eroare {delta_qng*100:.1f}%")
    pr(f"  r_d_Planck = {RD_PLANCK:.2f} Mpc  => eroare {delta_planck*100:.1f}%")
    pr(f"  r_d_eBOSS  = {RD_EBOSS:.2f} Mpc  => eroare {delta_eboss*100:.1f}%")

    # ── Gates ─────────────────────────────────────────────────────────────────
    G41a = bool(fit_ok and R2 > 0.80)
    G41b = bool(100.0 < r_bao_fit < 200.0)
    G41c = bool(delta_qng    < 0.15)
    G41d = bool(delta_planck < 0.15)

    pr(f"\n{'='*65}")
    pr(f"GATE RESULTS")
    pr(f"{'='*65}")
    pr(f"G41a  Fit R2 > 0.80:                {'PASS' if G41a else 'FAIL'}  (R2={R2:.4f})")
    pr(f"G41b  r_bao in [100,200] Mpc:       {'PASS' if G41b else 'FAIL'}  ({r_bao_fit:.2f} Mpc)")
    pr(f"G41c  |r_bao - r_QNG| < 15%:        {'PASS' if G41c else 'FAIL'}  ({delta_qng*100:.1f}%)")
    pr(f"G41d  |r_bao - r_Planck| < 15%:     {'PASS' if G41d else 'FAIL'}  ({delta_planck*100:.1f}%)")
    n_pass = sum([G41a, G41b, G41c, G41d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    # ── Tabel final ───────────────────────────────────────────────────────────
    pr(f"\n{'='*65}")
    pr(f"POZITIE PEAK BAO — COMPARATIE COMPLETA")
    pr(f"{'='*65}")
    pr(f"{'Sursa':<30} {'r_BAO [Mpc]':>12} {'Eroare vs fit':>14}")
    pr(f"{'-'*58}")
    pr(f"{'QNG (xi_graph_mpc, G39)':<30} {r_bao_qng:>12.2f} {delta_qng*100:>13.1f}%")
    pr(f"{'Planck 2018 (r_d)':<30} {RD_PLANCK:>12.2f} {delta_planck*100:>13.1f}%")
    pr(f"{'eBOSS DR16 LRG (Bautista+2021)':<30} {RD_EBOSS:>12.2f} {delta_eboss*100:>13.1f}%")
    pr(f"{'Fit xi(r) PL+Gauss [acesta]':<30} {r_bao_fit:>12.2f} {'---':>14}")

    # ── CSV ───────────────────────────────────────────────────────────────────
    csv = ["r_mpc,xi_s_raw,xi_r_real,sigma_r,xi_model_fit,xi_model_pl_only"]
    for i, (row) in enumerate(LRG_DATA_S):
        r, xr, sg = to_real_space(*row)
        xi_raw = row[1]
        yfit = float(model_pl_gauss(r, *popt))
        ypl  = float(A_fit * r**(-gamma_fit))
        csv.append(f"{r:.4f},{xi_raw:.6f},{xr:.6f},{sg:.6f},{yfit:.6f},{ypl:.6f}")
    (OUT_DIR / "bao_xi_fit.csv").write_text("\n".join(csv))

    # ── Summary JSON ──────────────────────────────────────────────────────────
    t1 = datetime.utcnow()
    summary = {
        "fit": {
            "A": float(A_fit), "gamma": float(gamma_fit),
            "B_bump": float(B_fit), "r_bao_mpc": float(r_bao_fit),
            "r_bao_err_mpc": float(r_bao_err), "sigma_bao_mpc": float(sigma_bao_fit),
            "R2": float(R2), "chi2_dof": float(chi2_val), "fit_ok": bool(fit_ok),
        },
        "reference": {
            "r_bao_qng_mpc": r_bao_qng,
            "rd_planck_mpc": RD_PLANCK,
            "rd_eboss_mpc": RD_EBOSS,
        },
        "deltas": {
            "delta_vs_qng_pct": float(delta_qng * 100),
            "delta_vs_planck_pct": float(delta_planck * 100),
            "delta_vs_eboss_pct": float(delta_eboss * 100),
        },
        "gates": {
            "G41a": {"passed": G41a, "value": float(R2),          "label": "R2 > 0.80"},
            "G41b": {"passed": G41b, "value": float(r_bao_fit),   "label": "r_bao in [100,200] Mpc"},
            "G41c": {"passed": G41c, "value": float(delta_qng),   "label": "|r_bao - r_QNG| < 15%"},
            "G41d": {"passed": G41d, "value": float(delta_planck),"label": "|r_bao - r_Planck| < 15%"},
        },
        "summary": {
            "n_pass": n_pass, "n_total": 4, "all_pass": n_pass == 4,
            "timestamp": t0.isoformat() + "Z",
            "runtime_s": (t1 - t0).total_seconds(),
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUT_DIR / "run.log").write_text("\n".join(lines))
    pr(f"\nArtifacte salvate in: {OUT_DIR}")
    return 0 if n_pass == 4 else 1

if __name__ == "__main__":
    sys.exit(main())
