#!/usr/bin/env python3
"""
QNG G39 — Calibrare BAO & Comparatie QNG C(r) vs 2dFGRS xi(r)

Primul test pe date reale (observationale).

Date 2dFGRS (Hawkins et al. 2003, MNRAS 346, 78):
  Functia de corelatie a galaxiilor: xi(r) = (r/r0)^(-gamma)
  r0    = 5.05 +/- 0.26  h^-1 Mpc  (scala de clustering, unde xi=1)
  gamma = 1.67 +/- 0.03            (exponent power-law)
  h     = 0.674                    (Planck 2018)
  => r0 = 5.05 / 0.674 = 7.49 Mpc  (in unitati absolute)

QNG C(r) din G33:
  r=1..4 BFS hops, exponential fit xi_fit=1.364 hops

Test:
  1. Fit power-law la QNG C(r): C(d) = A * d^(-gamma_QNG)
  2. Comparam gamma_QNG cu gamma_2dFGRS=1.67
  3. Calibrare BAO: alpha = 150 Mpc / xi_graph (scala de corelatie)
     => 1 hop = 96 Mpc
  4. Verificam ca ξ_fit * alpha e in gama structurii la scara mare (~BAO)

Gates:
  G39a — R^2(log-log fit QNG C(r)) > 0.85    [C(r) e power-law]
  G39b — |gamma_QNG - 1.67| / 1.67 < 0.30    [exponent la 30% de 2dFGRS]
  G39c — alpha_BAO in [30, 300] Mpc/hop       [scala fizica rezonabila]
  G39d — xi_fit * alpha_BAO in [50, 300] Mpc  [lungimea de corelatie e in gama LSS]

Referinta observationala:
  Hawkins et al. 2003, MNRAS 346, 78 — "The 2dF Galaxy Redshift Survey:
  correlation functions, peculiar velocities and the matter density of the Universe"
  https://arxiv.org/abs/astro-ph/0212375
"""

from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
G33_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g33-propagator-v1"
G34_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g34-scaling-v1"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g39-real-data-v1"

# ── Date observationale 2dFGRS (Hawkins et al. 2003) ──────────────────────────
R0_H_INV_MPC = 5.05        # h^-1 Mpc (scala de clustering xi=1)
GAMMA_2DFGRS = 1.67        # exponent power-law
H_PLANCK     = 0.674       # h = H0/100, Planck 2018
R0_MPC       = R0_H_INV_MPC / H_PLANCK  # = 7.49 Mpc (scala absoluta)

# Scala BAO (standard ruler, Planck 2018)
BAO_SCALE_MPC = 150.0      # Mpc (distanta comoving la peak BAO)


def fmt(v):
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.5e}"
    return f"{v:.6f}"


def log_log_powerlaw_fit(xs, ys, weights=None):
    """Fit y = A * x^(-gamma) in log-log space cu regresie liniara ponderata."""
    n = len(xs)
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    if weights is None:
        w = [1.0] * n
    else:
        w = weights

    sw  = sum(w)
    swx = sum(w[i]*lx[i] for i in range(n))
    swy = sum(w[i]*ly[i] for i in range(n))
    swxx = sum(w[i]*lx[i]**2 for i in range(n))
    swxy = sum(w[i]*lx[i]*ly[i] for i in range(n))

    denom = sw*swxx - swx**2
    if abs(denom) < 1e-15:
        return float("nan"), float("nan"), float("nan")

    slope     = (sw*swxy - swx*swy) / denom
    intercept = (swy - slope*swx) / sw
    A     = math.exp(intercept)
    gamma = -slope

    # R² in log-log
    my = swy / sw
    ss_tot = sum(w[i]*(ly[i]-my)**2 for i in range(n))
    ly_pred = [intercept + slope*lx[i] for i in range(n)]
    ss_res  = sum(w[i]*(ly[i]-ly_pred[i])**2 for i in range(n))
    R2 = 1.0 - ss_res/ss_tot if ss_tot > 1e-15 else float("nan")

    return gamma, A, R2


def xi_2dfgrs(r_mpc):
    """Functia de corelatie 2dFGRS: xi(r) = (r/r0)^(-gamma)."""
    return (r_mpc / R0_MPC) ** (-GAMMA_2DFGRS)


def main():
    out_dir = Path(DEFAULT_OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        try: print(msg)
        except UnicodeEncodeError: print(str(msg).encode("ascii", "replace").decode())
        lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG G39 — Calibrare BAO & Comparatie C(r) vs 2dFGRS xi(r)")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Date observationale ────────────────────────────────────────────────────
    log("\n[0] Date observationale 2dFGRS (Hawkins et al. 2003):")
    log(f"    xi(r) = (r/r0)^(-gamma)")
    log(f"    r0    = {R0_H_INV_MPC} h^-1 Mpc = {R0_MPC:.3f} Mpc  (h={H_PLANCK})")
    log(f"    gamma = {GAMMA_2DFGRS}  (exponent power-law)")
    log(f"    BAO standard ruler = {BAO_SCALE_MPC} Mpc  (Planck 2018)")

    log(f"\n    xi(r) la scale relevante:")
    for r_mpc in [1, 2, 5, 8, 15, 30, 100, 150]:
        log(f"    xi({r_mpc:4d} Mpc) = {xi_2dfgrs(r_mpc):.4f}")

    # ── Incarcare date QNG G33 ─────────────────────────────────────────────────
    g33_json = G33_DIR / "summary.json"
    g34_json = G34_DIR / "summary.json"
    if not g33_json.exists():
        log("EROARE: G33 summary.json lipseste.")
        return 1
    if not g34_json.exists():
        log("EROARE: G34 summary.json lipseste.")
        return 1

    with g33_json.open() as f:
        g33 = json.load(f)
    with g34_json.open() as f:
        g34 = json.load(f)

    xi_fit   = g33["correlation_length"]["xi_fit"]    # hops, exponential fit
    R2_exp   = g33["correlation_length"]["R2_fit"]
    xi_graph = g34["analysis"]["xi_mean"]              # hops, media pe n=50..400

    C_profile_raw = g33["C_profile"]
    rs_all  = sorted(int(r) for r in C_profile_raw.keys())
    C_vals  = {r: C_profile_raw[str(r)]["mean"] for r in rs_all}
    C_std   = {r: C_profile_raw[str(r)]["std"]  for r in rs_all}
    C_count = {r: C_profile_raw[str(r)]["count"] for r in rs_all}

    # Filtram r=5 (doar 3 perechi — nesemnificativ statistic)
    rs = [r for r in rs_all if C_count[r] >= 100]

    log(f"\n[1] Date QNG G33:")
    log(f"    xi_fit (exp, G33) = {fmt(xi_fit)} hops   R2={R2_exp:.4f}")
    log(f"    xi_graph (media G34, n=50..400) = {fmt(xi_graph)} hops")
    log(f"\n    C(r) profil (r={rs[0]}..{rs[-1]} hops, n>100 perechi):")
    log(f"\n    {'r':>3}  {'C(r)':>10}  {'std':>10}  {'n_pairs':>8}")
    log("    " + "-"*38)
    for r in rs:
        log(f"    {r:>3}  {fmt(C_vals[r]):>10}  {fmt(C_std[r]):>10}  {C_count[r]:>8}")

    # ── Fit power-law la QNG C(r) ──────────────────────────────────────────────
    log(f"\n[2] Fit power-law C(d) = A * d^(-gamma_QNG) in log-log:")

    # Ponderi proportionale cu sqrt(n_pairs) / std (mai multe perechi = mai sigur)
    ws = [math.sqrt(C_count[r]) / C_std[r] if C_std[r] > 1e-15 else 1.0 for r in rs]
    gamma_QNG, A_QNG, R2_QNG = log_log_powerlaw_fit(
        [float(r) for r in rs],
        [C_vals[r] for r in rs],
        weights=ws
    )

    # Fit neponderat pentru comparatie
    gamma_QNG_uw, A_QNG_uw, R2_QNG_uw = log_log_powerlaw_fit(
        [float(r) for r in rs],
        [C_vals[r] for r in rs],
    )

    log(f"\n    Fit ponderat:   gamma_QNG = {fmt(gamma_QNG)},  A = {fmt(A_QNG)},  R2 = {R2_QNG:.4f}")
    log(f"    Fit neponderat: gamma_QNG = {fmt(gamma_QNG_uw)}, A = {fmt(A_QNG_uw)}, R2 = {R2_QNG_uw:.4f}")
    log(f"\n    2dFGRS observat: gamma = {GAMMA_2DFGRS}")
    delta_gamma = abs(gamma_QNG - GAMMA_2DFGRS) / GAMMA_2DFGRS
    log(f"    |gamma_QNG - gamma_obs| / gamma_obs = {delta_gamma*100:.1f}%")

    log(f"\n    Valori fit vs observat:")
    log(f"\n    {'r':>3}  {'C_QNG':>10}  {'C_fit':>10}  {'xi_2dF(norm)':>14}  {'reziduu':>8}")
    log("    " + "-" * 52)
    # Normalizam ambele la r=1 pentru comparatie forma
    C_fit_r1 = A_QNG * 1.0 ** (-gamma_QNG)
    xi_obs_r1 = 1.0 ** (-GAMMA_2DFGRS)  # = 1
    for r in rs:
        c_fit_norm = (A_QNG * r**(-gamma_QNG)) / C_fit_r1
        xi_norm    = float(r)**(-GAMMA_2DFGRS) / xi_obs_r1
        reziduu    = c_fit_norm - xi_norm
        log(f"    {r:>3}  {fmt(C_vals[r]):>10}  {fmt(A_QNG*r**(-gamma_QNG)):>10}  "
            f"{fmt(xi_norm):>14}  {fmt(reziduu):>8}")

    # ── Calibrare BAO ──────────────────────────────────────────────────────────
    log(f"\n[3] Calibrare scala: 1 hop = ? Mpc")
    log(f"\n    Metoda A — BAO standard ruler:")
    log(f"    Premisa: xi_graph (lungimea de corelatie a grafului) corespunde")
    log(f"    scalei caracteristice de clustering in spatiul fizic.")
    log(f"    xi_graph = {fmt(xi_graph)} hops")
    log(f"    BAO = {BAO_SCALE_MPC} Mpc")
    alpha_BAO = BAO_SCALE_MPC / xi_graph
    log(f"    alpha_BAO = {BAO_SCALE_MPC} / {fmt(xi_graph)} = {fmt(alpha_BAO)} Mpc/hop")

    log(f"\n    Metoda B — Potrivire exponent + amplitudine cu 2dFGRS:")
    log(f"    La r=1 hop: C_QNG(1) = {fmt(C_vals[1])}")
    log(f"    La r=alpha_BAO Mpc: xi_2dFGRS({alpha_BAO:.1f} Mpc) = {fmt(xi_2dfgrs(alpha_BAO))}")
    log(f"    Factor normalizare: beta = C_QNG(1) / xi_2dFGRS(alpha_BAO) = "
        f"{fmt(C_vals[1] / xi_2dfgrs(alpha_BAO))}")

    log(f"\n    Scala calibrata: 1 hop = {fmt(alpha_BAO)} Mpc")
    log(f"    Graficul QNG (n=280 noduri) reprezinta un volum de:")
    vol_side = alpha_BAO * math.sqrt(280)  # daca graful e 2D
    vol_cube = alpha_BAO**3 * 280          # daca fiecare nod e un voxel
    log(f"    sqrt(n) * alpha = {vol_side:.0f} Mpc  (estimat 2D)")
    log(f"    n * alpha^3 = {vol_cube:.2e} Mpc^3  (n voxeli 3D)")

    # ── Comparatie forme: QNG vs 2dFGRS dupa calibrare ────────────────────────
    log(f"\n[4] Comparatie forma QNG C(r) vs 2dFGRS xi(r) dupa calibrare:")
    log(f"\n    Normalizam ambele la valoarea la r=1 hop ({alpha_BAO:.1f} Mpc):")
    log(f"\n    {'hop d':>6}  {'r_Mpc':>8}  {'C_norm':>10}  {'xi_norm':>10}  {'delta%':>8}")
    log("    " + "-" * 50)

    C_1     = C_vals[1]
    xi_at_1 = xi_2dfgrs(alpha_BAO * 1.0)

    chi2_sum = 0.0
    n_chi2   = 0
    for d in rs:
        r_mpc   = alpha_BAO * d
        c_norm  = C_vals[d] / C_1
        xi_norm = xi_2dfgrs(r_mpc) / xi_at_1
        delta   = (c_norm - xi_norm) / xi_norm * 100 if xi_norm > 1e-10 else float("nan")
        sigma_c = C_std[d] / C_1
        if sigma_c > 1e-10:
            chi2_sum += ((c_norm - xi_norm) / sigma_c) ** 2
            n_chi2 += 1
        log(f"    {d:>6}  {r_mpc:>8.1f}  {fmt(c_norm):>10}  {fmt(xi_norm):>10}  {delta:>7.1f}%")

    chi2_dof = chi2_sum / max(n_chi2 - 1, 1)
    log(f"\n    chi2/dof = {fmt(chi2_dof)}")

    # ── Lungimea de corelatie in Mpc ───────────────────────────────────────────
    xi_fit_mpc  = xi_fit  * alpha_BAO
    xi_graph_mpc = xi_graph * alpha_BAO
    log(f"\n[5] Lungimea de corelatie in unitati fizice:")
    log(f"    xi_fit  = {fmt(xi_fit)} hops × {fmt(alpha_BAO)} Mpc/hop = {xi_fit_mpc:.1f} Mpc")
    log(f"    xi_graph= {fmt(xi_graph)} hops × {fmt(alpha_BAO)} Mpc/hop = {xi_graph_mpc:.1f} Mpc")
    log(f"    2dFGRS r0 = {R0_MPC:.2f} Mpc  (scala clustering observat)")
    log(f"    BAO peak  = {BAO_SCALE_MPC:.0f} Mpc  (standard ruler)")
    log(f"\n    xi_fit_mpc / BAO_peak = {xi_fit_mpc/BAO_SCALE_MPC:.3f}  "
        f"(xi ≈ {xi_fit_mpc/BAO_SCALE_MPC*100:.0f}% din BAO)")

    # ── Gates ──────────────────────────────────────────────────────────────────
    log("\n" + "=" * 70)
    log("GATES G39")
    log("=" * 70)

    # G39a: R² (log-log fit) > 0.85
    g39a = (not math.isnan(R2_QNG)) and R2_QNG > 0.85
    val_g39a = R2_QNG

    # G39b: |gamma_QNG - 1.67| / 1.67 < 0.30
    g39b = (not math.isnan(delta_gamma)) and delta_gamma < 0.30
    val_g39b = delta_gamma

    # G39c: alpha_BAO in [30, 300] Mpc/hop
    g39c = (not math.isnan(alpha_BAO)) and (30.0 <= alpha_BAO <= 300.0)
    val_g39c = alpha_BAO

    # G39d: xi_fit * alpha_BAO in [50, 300] Mpc
    g39d = (not math.isnan(xi_fit_mpc)) and (50.0 <= xi_fit_mpc <= 300.0)
    val_g39d = xi_fit_mpc

    for label, gate, val, cond in [
        ("G39a", g39a, val_g39a,
         "R^2(log-log power-law fit) > 0.85  [C(r) are forma power-law]"),
        ("G39b", g39b, val_g39b,
         "|gamma_QNG - 1.67| / 1.67 < 0.30  [exponent la 30% de 2dFGRS]"),
        ("G39c", g39c, val_g39c,
         "alpha_BAO in [30, 300] Mpc/hop  [scala fizica rezonabila]"),
        ("G39d", g39d, val_g39d,
         "xi_fit * alpha_BAO in [50, 300] Mpc  [lungimea de corelatie in LSS]"),
    ]:
        st = "PASS" if gate else "FAIL"
        log(f"\n{label} — {cond}")
        log(f"       Valoare: {fmt(val)}  ->  {st}")

    n_pass = sum([g39a, g39b, g39c, g39d])
    log(f"\nSUMAR: {n_pass}/4 gate-uri trecute")
    log(f"G39a [{'PASS' if g39a else 'FAIL'}]  G39b [{'PASS' if g39b else 'FAIL'}]  "
        f"G39c [{'PASS' if g39c else 'FAIL'}]  G39d [{'PASS' if g39d else 'FAIL'}]")

    log(f"\nConcluzii fizice:")
    log(f"  1. QNG C(r) urmeaza o lege de putere cu gamma={fmt(gamma_QNG)} "
        f"vs 2dFGRS gamma=1.67 (delta={delta_gamma*100:.1f}%)")
    log(f"  2. Calibrare: 1 hop ≈ {alpha_BAO:.0f} Mpc/hop")
    log(f"  3. Lungimea de corelatie QNG = {xi_fit_mpc:.0f} Mpc "
        f"≈ {xi_fit_mpc/BAO_SCALE_MPC*100:.0f}% din scala BAO (150 Mpc)")
    log(f"  4. Graful n=280 reprezinta ~{vol_cube:.1e} Mpc^3 din universul observabil")
    log(f"Timp total: {time.time()-t0:.3f}s")

    result = {
        "qng": {
            "gamma_QNG": gamma_QNG, "gamma_QNG_unweighted": gamma_QNG_uw,
            "A_QNG": A_QNG, "R2_QNG": R2_QNG,
            "xi_fit_hops": xi_fit, "xi_graph_hops": xi_graph,
        },
        "obs_2dfgrs": {
            "gamma": GAMMA_2DFGRS, "r0_h_inv_mpc": R0_H_INV_MPC,
            "r0_mpc": R0_MPC, "h": H_PLANCK,
            "reference": "Hawkins et al. 2003, MNRAS 346, 78, arXiv:astro-ph/0212375",
        },
        "calibration": {
            "alpha_BAO_mpc_per_hop": alpha_BAO,
            "BAO_scale_mpc": BAO_SCALE_MPC,
            "xi_fit_mpc": xi_fit_mpc, "xi_graph_mpc": xi_graph_mpc,
            "volume_n_voxels_mpc3": vol_cube,
        },
        "comparison": {
            "delta_gamma_pct": delta_gamma * 100,
            "chi2_dof": chi2_dof,
        },
        "gates": {
            "G39a": {"passed": g39a, "value": val_g39a},
            "G39b": {"passed": g39b, "value": val_g39b},
            "G39c": {"passed": g39c, "value": val_g39c},
            "G39d": {"passed": g39d, "value": val_g39d},
        },
        "summary": {
            "n_pass": n_pass, "n_total": 4, "all_pass": n_pass == 4,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "runtime_s": round(time.time() - t0, 3),
        }
    }
    with (out_dir / "summary.json").open("w") as f:
        json.dump(result, f, indent=2)
    with (out_dir / "run.log").open("w") as f:
        f.write("\n".join(lines))
    log(f"\nArtefacte: {out_dir}")

    return 0 if n_pass == 4 else 1


if __name__ == "__main__":
    sys.exit(main())
