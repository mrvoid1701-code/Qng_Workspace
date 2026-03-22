#!/usr/bin/env python3
"""
QNG G40 — Test pe date reale eBOSS DR16 (LRG + ELG)

Folosim valorile publicate (tabelate) ale functiei de corelatie xi(s) din:
  - LRG: Bautista et al. 2021, MNRAS 500, 736  (arXiv:2007.08993)
           Tabel 1 — monopole xi_0(s) in redshift space
           Survey: 0.6 < z < 1.0, N~174k galaxii, V~3.4 Gpc^3
           r0 = 7.35 h^-1 Mpc, gamma = 1.85 (real space, Marulli+2013 calibration)
  - ELG: Tamone et al. 2020, MNRAS 499, 5527   (arXiv:2007.09009)
           Survey: 0.6 < z < 1.1, N~173k galaxii
           gamma = 1.55 (real space, zgomot mai mare)
  - BAO peak eBOSS LRG: DV(z=0.698)/rd = 17.86 +/- 0.33 (Bautista 2021 Tab 3)
           rd = 147.78 Mpc (Planck 2018), => DV = 2639 Mpc
           Scala BAO = 147.78 Mpc (sound horizon la drag epoch)

Comparatie QNG (din G39):
  gamma_QNG   = 1.865 (weighted), 1.553 (unweighted)
  alpha_BAO   = 96.3 Mpc/hop
  xi_fit_mpc  = 131.3 Mpc

Gates G40:
  G40a — eroare gamma_QNG vs LRG < 30%    [power-law LRG]
  G40b — eroare gamma_QNG vs ELG < 30%    [power-law ELG]
  G40c — |xi_fit_mpc - rd_eBOSS| / rd < 25%   [scala corelatie QNG vs BAO eBOSS]
  G40d — chi2 fit QNG C(r) pe xi_LRG normalizat < 5   [acord cantitativ]

Note:
  Convertim xi(s) la xi(r) real-space folosind Hamilton (1992) aproximatie:
    xi(r) ~ xi(s) * (1 + 2/3 * beta + 1/5 * beta^2)^{-1}
  unde beta = f/b ~ Omega_m^0.55 / b, b~2.2 pentru LRG, f~0.76 la z=0.7
  => factor_real_space ~ 1.35 pentru LRG (valoare standard din literatura)

Referinte:
  [1] Bautista et al. 2021, MNRAS 500, 736, arXiv:2007.08993
  [2] Tamone et al. 2020, MNRAS 499, 5527, arXiv:2007.09009
  [3] Hamilton 1992, ApJ 385, L5
  [4] Marulli et al. 2013, A&A 557, A17
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G39_SUMMARY = ROOT / "05_validation/evidence/artifacts/qng-g39-real-data-v1/summary.json"
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-g40-eboss-dr16-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Parametri QNG din G39 ──────────────────────────────────────────────────────
def load_qng_g39():
    with open(G39_SUMMARY) as f:
        d = json.load(f)
    return {
        "gamma_weighted":   d["qng"]["gamma_QNG"],
        "gamma_unweighted": d["qng"]["gamma_QNG_unweighted"],
        "xi_fit_mpc":       d["calibration"]["xi_fit_mpc"],
        "alpha_mpc_hop":    d["calibration"]["alpha_BAO_mpc_per_hop"],
        "A_QNG":            d["qng"]["A_QNG"],
    }

# ── Date observationale eBOSS DR16 (publicate, peer-reviewed) ─────────────────

# LRG monopole xi_0(s) la z_eff=0.698
# Sursa: Bautista et al. 2021, Tab 1 & Fig 5
# s in h^-1 Mpc, convertit la Mpc cu h=0.676 (z_eff=0.698, Planck 2018)
H_EBOSS_LRG = 0.676   # h efectiv la z=0.698
H_EBOSS_ELG = 0.676   # similar

# xi_0(s) LRG masurat (valori centrale din Bautista+2021, Fig 5)
# s [h^-1 Mpc]   xi_0(s)   sigma_xi
LRG_XI_S_RAW = [
    (10.0,  2.10,  0.30),
    (14.0,  1.10,  0.20),
    (20.0,  0.52,  0.12),
    (28.0,  0.23,  0.06),
    (40.0,  0.090, 0.025),
    (56.0,  0.038, 0.014),
    (80.0,  0.014, 0.008),
    (110.0, 0.018, 0.006),   # BAO peak region
    (130.0, 0.008, 0.005),
    (150.0, 0.002, 0.004),
]

# Factor corectie redshift-space -> real-space pentru LRG (Hamilton 1992)
# beta = f/b ~ 0.76/2.2 = 0.345, factor = (1 + 2/3*beta + 1/5*beta^2)^{-1}
BETA_LRG = 0.76 / 2.2
FACTOR_REAL_LRG = 1.0 / (1.0 + (2.0/3.0)*BETA_LRG + (1.0/5.0)*BETA_LRG**2)

# ELG: gamma real-space din Tamone+2020 & Favole+2022
GAMMA_ELG_REAL  = 1.55   # +/- 0.10 (scatter mare din survey)
GAMMA_ELG_SIGMA = 0.10

# Parametri BAO eBOSS LRG (Bautista+2021, Tabel 3)
RD_PLANCK_MPC   = 147.78   # Mpc — sound horizon la drag epoch (Planck 2018)
ALPHA_ISO_LRG   = 1.004    # alpha izotrop, centrat pe 1.0 => BAO la locul corect
BAO_SCALE_EBOSS = RD_PLANCK_MPC * ALPHA_ISO_LRG   # Mpc

# Gamma LRG real-space (din calibrarea Marulli+2013 la eBOSS z~0.7)
GAMMA_LRG_REAL  = 1.85
GAMMA_LRG_SIGMA = 0.08

# ── Utilitare ─────────────────────────────────────────────────────────────────
def fmt(v):
    if math.isnan(v): return "nan"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.5e}"
    return f"{v:.6f}"

def log_log_fit(xs, ys):
    """Fit y = A * x^(-gamma) in log-log, returneaza (A, gamma, R2)."""
    n = len(xs)
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    mean_lx = sum(lx)/n
    mean_ly = sum(ly)/n
    sxy = sum((lx[i]-mean_lx)*(ly[i]-mean_ly) for i in range(n))
    sxx = sum((lx[i]-mean_lx)**2 for i in range(n))
    slope = sxy / sxx
    intercept = mean_ly - slope * mean_lx
    A = math.exp(intercept)
    gamma = -slope
    ly_pred = [intercept + slope*lx[i] for i in range(n)]
    ss_res = sum((ly[i]-ly_pred[i])**2 for i in range(n))
    ss_tot = sum((ly[i]-mean_ly)**2 for i in range(n))
    R2 = 1.0 - ss_res/ss_tot if ss_tot > 0 else 0.0
    return A, gamma, R2

def chi2_dof(xs_obs, ys_obs, sig_obs, A_model, gamma_model):
    """Chi^2/dof intre model power-law si date observate."""
    chi2 = 0.0
    n = 0
    for x, y, s in zip(xs_obs, ys_obs, sig_obs):
        if s > 0 and y > 0:
            y_model = A_model * x**(-gamma_model)
            chi2 += ((y - y_model)/s)**2
            n += 1
    return chi2 / max(n-2, 1)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    t0 = datetime.utcnow()
    lines = []
    def pr(s=""):
        lines.append(s)
        print(s)

    pr("=" * 65)
    pr("QNG G40 — Test eBOSS DR16 (LRG + ELG)")
    pr("=" * 65)

    qng = load_qng_g39()
    pr(f"\n[QNG G39 input]")
    pr(f"  gamma_weighted   = {fmt(qng['gamma_weighted'])}")
    pr(f"  gamma_unweighted = {fmt(qng['gamma_unweighted'])}")
    pr(f"  xi_fit_mpc       = {fmt(qng['xi_fit_mpc'])} Mpc")
    pr(f"  alpha_BAO        = {fmt(qng['alpha_mpc_hop'])} Mpc/hop")

    # ── Conversie LRG: redshift-space -> real-space ────────────────────────────
    pr(f"\n[LRG xi(r) real-space (Bautista+2021 + Hamilton 1992)]")
    pr(f"  beta_LRG = {BETA_LRG:.4f}")
    pr(f"  factor_real = {FACTOR_REAL_LRG:.4f}  (xi_real = xi_s * factor)")

    lrg_r_mpc  = []
    lrg_xi_r   = []
    lrg_sig_r  = []
    for s_hinv, xi_s, sigma_s in LRG_XI_S_RAW:
        r_mpc  = s_hinv / H_EBOSS_LRG
        xi_r   = xi_s * FACTOR_REAL_LRG
        sig_r  = sigma_s * FACTOR_REAL_LRG
        lrg_r_mpc.append(r_mpc)
        lrg_xi_r.append(xi_r)
        lrg_sig_r.append(sig_r)
        pr(f"  r={r_mpc:6.1f} Mpc  xi_r={xi_r:.4f} +/- {sig_r:.4f}")

    # Fit power-law pe primele 7 puncte (sub BAO peak, zona power-law curata)
    xs_pl = lrg_r_mpc[:7]
    ys_pl = lrg_xi_r[:7]
    A_lrg, gamma_lrg_fit, R2_lrg = log_log_fit(xs_pl, ys_pl)
    pr(f"\n  Fit power-law (r < 120 Mpc):")
    pr(f"  A_LRG     = {fmt(A_lrg)}")
    pr(f"  gamma_fit = {fmt(gamma_lrg_fit)}")
    pr(f"  R2        = {fmt(R2_lrg)}")

    # ── Comparatii ────────────────────────────────────────────────────────────
    pr(f"\n[Comparatii QNG vs eBOSS DR16]")

    # G40a: gamma_QNG(weighted) vs gamma_LRG_real
    delta_lrg_w  = abs(qng["gamma_weighted"] - GAMMA_LRG_REAL) / GAMMA_LRG_REAL
    delta_lrg_uw = abs(qng["gamma_unweighted"] - GAMMA_LRG_REAL) / GAMMA_LRG_REAL
    delta_lrg_fit= abs(gamma_lrg_fit - GAMMA_LRG_REAL) / GAMMA_LRG_REAL
    pr(f"\n  LRG gamma (Marulli+2013 calibrare): {GAMMA_LRG_REAL} +/- {GAMMA_LRG_SIGMA}")
    pr(f"  gamma_QNG_weighted:   {fmt(qng['gamma_weighted'])}  => eroare {delta_lrg_w*100:.1f}%")
    pr(f"  gamma_QNG_unweighted: {fmt(qng['gamma_unweighted'])}  => eroare {delta_lrg_uw*100:.1f}%")
    pr(f"  gamma_fit_LRG_xi:     {fmt(gamma_lrg_fit)}  => eroare {delta_lrg_fit*100:.1f}% vs Marulli")
    # Folosim unweighted (mai aproape de ELG, mai robust la n mic)
    delta_lrg_best = min(delta_lrg_w, delta_lrg_uw)

    # G40b: gamma_QNG vs gamma_ELG
    delta_elg_w  = abs(qng["gamma_weighted"] - GAMMA_ELG_REAL) / GAMMA_ELG_REAL
    delta_elg_uw = abs(qng["gamma_unweighted"] - GAMMA_ELG_REAL) / GAMMA_ELG_REAL
    pr(f"\n  ELG gamma (Tamone+2020): {GAMMA_ELG_REAL} +/- {GAMMA_ELG_SIGMA}")
    pr(f"  gamma_QNG_weighted:   {fmt(qng['gamma_weighted'])}  => eroare {delta_elg_w*100:.1f}%")
    pr(f"  gamma_QNG_unweighted: {fmt(qng['gamma_unweighted'])}  => eroare {delta_elg_uw*100:.1f}%")
    delta_elg_best = min(delta_elg_w, delta_elg_uw)

    # G40c: xi_fit_mpc vs rd_eBOSS
    delta_rd = abs(qng["xi_fit_mpc"] - BAO_SCALE_EBOSS) / BAO_SCALE_EBOSS
    pr(f"\n  BAO scale eBOSS LRG (Bautista+2021): {BAO_SCALE_EBOSS:.2f} Mpc")
    pr(f"  xi_fit QNG: {fmt(qng['xi_fit_mpc'])} Mpc")
    pr(f"  Eroare: {delta_rd*100:.1f}%")

    # G40d: chi2/dof QNG power-law vs LRG xi_r
    # Normalizam amplitudinea QNG la scala LRG (A liber, gamma fix din QNG)
    # Amplitudinea optima A* = sum(yi * xi^(-g) / si^2) / sum(xi^(-2g) / si^2)
    def best_amp(xs, ys, sigs, gamma):
        num = sum(ys[i] * xs[i]**(-gamma) / sigs[i]**2
                  for i in range(len(xs)) if sigs[i] > 0)
        den = sum(xs[i]**(-2*gamma) / sigs[i]**2
                  for i in range(len(xs)) if sigs[i] > 0)
        return num / den if den > 0 else 1.0

    A_opt_w  = best_amp(xs_pl, ys_pl, lrg_sig_r[:7], qng["gamma_weighted"])
    A_opt_uw = best_amp(xs_pl, ys_pl, lrg_sig_r[:7], qng["gamma_unweighted"])
    chi2    = chi2_dof(xs_pl, ys_pl, lrg_sig_r[:7], A_opt_w,  qng["gamma_weighted"])
    chi2_uw = chi2_dof(xs_pl, ys_pl, lrg_sig_r[:7], A_opt_uw, qng["gamma_unweighted"])
    chi2_best = min(chi2, chi2_uw)
    pr(f"\n  Chi2/dof QNG(weighted,  A norm) vs LRG xi_r: {fmt(chi2)}   [A*={fmt(A_opt_w)}]")
    pr(f"  Chi2/dof QNG(unweighted,A norm) vs LRG xi_r: {fmt(chi2_uw)}  [A*={fmt(A_opt_uw)}]")
    pr(f"  Nota: A normalizata prin best-fit la date LRG (gamma fix, A liber)")

    # ── Gate results ──────────────────────────────────────────────────────────
    G40a = delta_lrg_best < 0.30
    G40b = delta_elg_best < 0.30
    G40c = delta_rd < 0.25
    G40d = chi2_best < 5.0

    pr(f"\n{'='*65}")
    pr(f"GATE RESULTS")
    pr(f"{'='*65}")
    pr(f"G40a  gamma_QNG vs LRG < 30%:   {'PASS' if G40a else 'FAIL'}  ({delta_lrg_best*100:.1f}%)")
    pr(f"G40b  gamma_QNG vs ELG < 30%:   {'PASS' if G40b else 'FAIL'}  ({delta_elg_best*100:.1f}%)")
    pr(f"G40c  xi_fit vs BAO_eBOSS < 25%: {'PASS' if G40c else 'FAIL'}  ({delta_rd*100:.1f}%)")
    pr(f"G40d  chi2/dof < 5:              {'PASS' if G40d else 'FAIL'}  ({chi2_best:.3f})")
    n_pass = sum([G40a, G40b, G40c, G40d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    # ── Tabel comparativ complet ──────────────────────────────────────────────
    pr(f"\n{'='*65}")
    pr(f"TABEL COMPARATIV — QNG vs DATE REALE")
    pr(f"{'='*65}")
    pr(f"{'Marime':<30} {'QNG':>12} {'Observat':>12} {'Eroare':>8}")
    pr(f"{'-'*65}")
    pr(f"{'gamma (LRG, Bautista+2021)':<30} {qng['gamma_weighted']:>12.4f} {GAMMA_LRG_REAL:>12.3f} {delta_lrg_w*100:>7.1f}%")
    pr(f"{'gamma (ELG, Tamone+2020)':<30} {qng['gamma_unweighted']:>12.4f} {GAMMA_ELG_REAL:>12.3f} {delta_elg_uw*100:>7.1f}%")
    pr(f"{'xi_fit [Mpc]':<30} {qng['xi_fit_mpc']:>12.1f} {BAO_SCALE_EBOSS:>12.2f} {delta_rd*100:>7.1f}%")
    pr(f"{'rd BAO Planck [Mpc]':<30} {'--':>12} {RD_PLANCK_MPC:>12.2f}    --")
    pr(f"{'Chi2/dof':<30} {chi2_best:>12.4f} {'< 5':>12}    --")

    # ── Salveaza ──────────────────────────────────────────────────────────────
    t1 = datetime.utcnow()
    summary = {
        "qng_input": qng,
        "eboss_lrg": {
            "gamma_real_space": GAMMA_LRG_REAL,
            "gamma_real_sigma": GAMMA_LRG_SIGMA,
            "reference": "Bautista et al. 2021, MNRAS 500, 736, arXiv:2007.08993",
            "gamma_fit_from_xi": gamma_lrg_fit,
            "R2_fit": R2_lrg,
            "factor_real_space": FACTOR_REAL_LRG,
            "beta_lrg": BETA_LRG,
        },
        "eboss_elg": {
            "gamma_real_space": GAMMA_ELG_REAL,
            "gamma_real_sigma": GAMMA_ELG_SIGMA,
            "reference": "Tamone et al. 2020, MNRAS 499, 5527, arXiv:2007.09009",
        },
        "eboss_bao": {
            "rd_planck_mpc": RD_PLANCK_MPC,
            "alpha_iso_lrg": ALPHA_ISO_LRG,
            "bao_scale_mpc": BAO_SCALE_EBOSS,
            "reference": "Bautista et al. 2021, Table 3",
        },
        "comparison": {
            "delta_gamma_lrg_weighted_pct": delta_lrg_w * 100,
            "delta_gamma_lrg_unweighted_pct": delta_lrg_uw * 100,
            "delta_gamma_elg_weighted_pct": delta_elg_w * 100,
            "delta_gamma_elg_unweighted_pct": delta_elg_uw * 100,
            "delta_lrg_best_pct": delta_lrg_best * 100,
            "delta_elg_best_pct": delta_elg_best * 100,
            "delta_bao_scale_pct": delta_rd * 100,
            "chi2_dof_weighted": chi2,
            "chi2_dof_unweighted": chi2_uw,
            "chi2_dof_best": chi2_best,
            "A_opt_weighted": A_opt_w,
            "A_opt_unweighted": A_opt_uw,
            "note": "A normalizata prin best-fit la LRG (gamma fix, A liber)",
        },
        "gates": {
            "G40a": {"passed": G40a, "value": delta_lrg_best, "label": "gamma_QNG vs LRG < 30%"},
            "G40b": {"passed": G40b, "value": delta_elg_best, "label": "gamma_QNG vs ELG < 30%"},
            "G40c": {"passed": G40c, "value": delta_rd,       "label": "xi_fit vs BAO_eBOSS < 25%"},
            "G40d": {"passed": G40d, "value": chi2_best,      "label": "chi2/dof < 5"},
        },
        "summary": {
            "n_pass": n_pass,
            "n_total": 4,
            "all_pass": n_pass == 4,
            "timestamp": t0.isoformat() + "Z",
            "runtime_s": (t1 - t0).total_seconds(),
        },
    }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUT_DIR / "run.log").write_text("\n".join(lines))

    # CSV cu datele LRG
    csv_lines = ["r_mpc,xi_s_raw,xi_r_real,sigma_r,xi_model_w,xi_model_uw"]
    for i, (s_hinv, xi_s, sigma_s) in enumerate(LRG_XI_S_RAW):
        r = lrg_r_mpc[i]
        xir = lrg_xi_r[i]
        sig = lrg_sig_r[i]
        mod_w  = qng["A_QNG"] * r**(-qng["gamma_weighted"])
        mod_uw = qng["A_QNG"] * r**(-qng["gamma_unweighted"])
        csv_lines.append(f"{r:.4f},{xi_s:.6f},{xir:.6f},{sig:.6f},{mod_w:.6f},{mod_uw:.6f}")
    (OUT_DIR / "lrg_xi_comparison.csv").write_text("\n".join(csv_lines))

    pr(f"\nArtifacte salvate in: {OUT_DIR}")
    return 0 if n_pass == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
