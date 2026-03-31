#!/usr/bin/env python3
"""
D7 — QNG Straton Law (T3: lege cu limite corecte, derivata din teoria straton)

Diagnosticul D6 a aratat problema critica:
  S1(chi) = exp(-|chi-1|/sigma) → 0 la chi << 1 (periferie, 70% din date)
  Deci T1 e UCIS exact unde e nevoie (deep MOND regime).

  RAR bins D6:
    chi=0.012: date=9.75, M7=1.75  → underpredicts 5.6×!
    chi=0.505: date=1.41, M7=1.41  → OK
    chi=3.3:   date=0.77, M7=1.20  → overcorrects

Solutia (derivata din QNG straton theory):
  Termenul T3 = sqrt(g_bar * a0) * exp(-chi)    [QNG straton suppression]

  Proprietati matematice ale T3:
    - chi → 0 (outer, deep MOND): T3 → sqrt(g_bar * a0) * 1 = sqrt(g_bar * a0)
      → v^2_extra = r * T3 = sqrt(g_bar * a0 * r^2) = sqrt(GM * a0) = CONST
      → Curba PLATA emergenta!
    - chi → ∞ (inner, Newtonian): T3 → sqrt(g_bar * a0) * exp(-chi) → 0
      → Newtonian limit restaurat!
    - La chi = 1 (tranzitie): T3 = sqrt(a0^2) * exp(-1) = a0 * 0.368

  Derivare din teoria QNG:
    Distributia chi are forma exp(-chi/sigma_chi) (chi pozitiv, asimetric).
    Factorul de supresie straton: psi(chi) = exp(-chi) vine din probabilitatea de
    a gasi un nod QNG in regim "activ" (energia <= a0).
    La chi > 1: nodul e "saturat" → suprima contributia.
    La chi < 1: nodul e "activ" → lasa toata corectia.
    Amplitudinea: sqrt(g_bar * a0) = media geometrica a celor 2 scale (MOND geometric mean).

  Comparatie cu MOND RAR (McGaugh+2016):
    MOND: g_obs = g_bar / (1 - exp(-sqrt(chi)))
    T3:   g_obs = g_bar + k * sqrt(g_bar * a0) * exp(-chi)

    La chi → 0: MOND → sqrt(g_bar * a0)       T3 → k * sqrt(g_bar * a0)  (k factor)
    La chi → ∞: MOND → g_bar                  T3 → g_bar                 (identical)
    La chi = 1: MOND: extra = 0.58*a0          T3: extra = k * 0.368 * a0

  T3 este DIFERIT de MOND prin:
    1. Supresie mai rapida (exp(-chi) vs 1-exp(-sqrt(chi))): mai Newtonian la chi>1
    2. Amplitudine cu parametru k liber
    3. Forma de tranzitie diferita la chi~1

Modele:
  M0:  Null (0 param)
  M1:  MOND RAR (1 param: g_dag)
  M8a: T3 only — k*sqrt(g_bar*a0)*exp(-chi)     [1 param]
  M8b: T3+T2  — k1*T3 + k2*T2                   [2 param]
       T2 = S2*g_bar/sqrt(1+chi) (structural, din D6)
  M8c: T3 cu g_dag liber — k*sqrt(g_bar*g_dag)*exp(-g_bar/g_dag) [2 param]
       Verifica daca g_dag optim ≈ a0 (MOND) sau altceva (QNG)
  M8d: QNG completat — interpolation function derivata din straton:
       nu_QNG(chi) = 1 + k / (1 + chi) / sqrt(chi + epsilon)  [2 param: k, epsilon]
       La chi→0: → k/sqrt(epsilon)   La chi>>1: → 0

Criterii preregistrate:
  PASS:     chi2/N < chi2/N(Null) cu >40%
  TARGET:   chi2/N < 1.5 * chi2/N(MOND)
  BONUS:    chi2/N < chi2/N(MOND) sau g_dag_fit ≈ a0 (straton derivation confirmed)
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "d7-qng-straton-law-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M
A0_SI    = 1.2e-10
A0_INT   = A0_SI / G_UNIT

S2_CONST = 0.355


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def load_galaxies(path: Path) -> dict[str, list[dict]]:
    gals: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r  = float(row["radius"])
            v  = float(row["v_obs"])
            ve = float(row["v_err"])
            bt = float(row["baryon_term"])
            if r <= 0 or ve <= 0 or bt < 0:
                continue
            g_bar = bt / max(r, 1e-9)
            chi   = g_bar / A0_INT
            gals.setdefault(row["system_id"], []).append({
                "r": r, "v": v, "ve": ve, "bt": bt, "g_bar": g_bar, "chi": chi,
            })
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


# ---------------------------------------------------------------------------
# Termeni
# ---------------------------------------------------------------------------

def T3(pt: dict, g_dag: float = None) -> float:
    """
    T3 = sqrt(g_bar * g_dag) * exp(-g_bar / g_dag)

    Cu g_dag = a0: straton law clasic
    Cu g_dag liber: permite detectia daca g_dag QNG ≠ a0 MOND
    """
    gd    = A0_INT if g_dag is None else g_dag
    chi_d = pt["g_bar"] / max(gd, 1e-30)
    return math.sqrt(max(pt["g_bar"] * gd, 0.0)) * math.exp(-chi_d)


def T2(pt: dict) -> float:
    """T2 (structural, din D6): S2 * g_bar / sqrt(1 + chi)"""
    return S2_CONST * pt["g_bar"] / math.sqrt(1.0 + pt["chi"])


def nu_qng(pt: dict, k: float, eps: float) -> float:
    """
    Functia de interpolatie QNG:
    nu(chi) = 1 + k / ((1 + chi) * sqrt(chi + eps))

    La chi→0:  → 1 + k/sqrt(eps)   (amplitudine controlata de eps)
    La chi→∞:  → 1 + k/chi^(3/2)  → 1 (Newtonian)
    La chi=1:  → 1 + k/(2*sqrt(1+eps))
    """
    chi = pt["chi"]
    return 1.0 + k / ((1.0 + chi) * math.sqrt(chi + max(eps, 1e-9)))


def v_null(pt: dict) -> float:
    return math.sqrt(max(pt["bt"], 0.0))


def v_mond(pt: dict, g_dag: float) -> float:
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    x     = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


def v_m8a(pt: dict, k: float) -> float:
    """M8a: v^2 = bt + r * k * T3(g_dag=a0)"""
    return math.sqrt(max(pt["bt"] + pt["r"] * k * T3(pt), 0.0))


def v_m8b(pt: dict, k1: float, k2: float) -> float:
    """M8b: v^2 = bt + r * (k1*T3 + k2*T2)"""
    return math.sqrt(max(pt["bt"] + pt["r"] * (k1 * T3(pt) + k2 * T2(pt)), 0.0))


def v_m8c(pt: dict, k: float, g_dag: float) -> float:
    """M8c: v^2 = bt + r * k * T3(g_dag liber)"""
    return math.sqrt(max(pt["bt"] + pt["r"] * k * T3(pt, g_dag), 0.0))


def v_m8d(pt: dict, k: float, eps: float) -> float:
    """M8d: v^2 = bt * nu_QNG(chi)^2"""
    nu = nu_qng(pt, k, eps)
    return math.sqrt(max(pt["bt"] * nu * nu, 0.0))


# ---------------------------------------------------------------------------
# Optimizare
# ---------------------------------------------------------------------------

def golden_search(f, lo: float, hi: float, tol: float = 1e-7, max_iter: int = 500):
    phi = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(max_iter):
        if abs(b - a) < tol:
            break
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = f(d)
    best = c if fc < fd else d
    return best, min(fc, fd)


def fit_2param(chi2_fn, lo1, hi1, lo2, hi2, n_outer=50) -> tuple:
    """Grid 1D pe param2, golden pe param1."""
    best = (lo1, lo2, float("inf"))
    for i in range(n_outer):
        p2 = lo2 + (hi2 - lo2) * i / max(n_outer - 1, 1)
        p1_opt, chi2_v = golden_search(lambda p1: chi2_fn(p1, p2), lo1, hi1)
        if chi2_v < best[2]:
            best = (p1_opt, p2, chi2_v)

    # Refinare locale in jurul minimului
    p1_c, p2_c, best_chi2 = best
    p2_step = (hi2 - lo2) / n_outer
    for i in range(30):
        p2 = max(lo2, p2_c - p2_step) + 2 * p2_step * i / 29
        p1_opt, chi2_v = golden_search(
            lambda p1: chi2_fn(p1, p2),
            max(lo1, p1_c * 0.5), p1_c * 2.0 + 0.01, tol=1e-8)
        if chi2_v < best[2]:
            best = (p1_opt, p2, chi2_v)

    return best


def chi2_all(pts_list, f_model):
    return sum(((p["v"] - f_model(p)) / p["ve"])**2 for p in pts_list)


# ---------------------------------------------------------------------------
# RAR bins
# ---------------------------------------------------------------------------

def rar_bins(all_pts, f_model, n_bins=12):
    g_bars = [p["g_bar"] for p in all_pts if p["g_bar"] > 0]
    lmin   = math.log10(min(g_bars))
    lmax   = math.log10(max(g_bars))
    bins   = [[] for _ in range(n_bins)]
    for p in all_pts:
        if p["g_bar"] <= 0:
            continue
        idx = int((math.log10(p["g_bar"]) - lmin) / (lmax - lmin) * n_bins)
        bins[min(idx, n_bins-1)].append(p)
    out = []
    for i, bp in enumerate(bins):
        if not bp:
            continue
        g_bar_m = 10 ** (lmin + (i + 0.5) * (lmax - lmin) / n_bins)
        g_obs_d = [p["v"]**2 / max(p["r"], 1e-9) for p in bp]
        g_obs_m = [f_model(p)**2 / max(p["r"], 1e-9) for p in bp]
        out.append({
            "chi": g_bar_m / A0_INT,
            "g_obs_data": sum(g_obs_d) / len(g_obs_d),
            "g_obs_model": sum(g_obs_m) / len(g_obs_m),
            "g_bar": g_bar_m, "n": len(bp),
        })
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D7 — QNG Straton Law: T3 = sqrt(g_bar*a0)*exp(-chi)")
    print(f"Date: {DATA_CSV.name}")
    print()

    gals    = load_galaxies(DATA_CSV)
    all_pts = [p for pts in gals.values() for p in pts]
    n       = len(all_pts)
    n_gal   = len(gals)
    print(f"  {n} puncte, {n_gal} galaxii")
    print(f"  a0 = {A0_SI:.2e} m/s²  ({A0_INT:.2f} km²/s²/kpc)")
    print()

    # Verifica forma T3 in diferite regimuri
    chi_vals = [0.01, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
    print("Forma T3 = sqrt(g_bar*a0)*exp(-chi):")
    print(f"  {'chi':>8s}  {'T3/a0':>10s}  {'MOND_extra/a0':>14s}  {'ratio':>8s}")
    for chi_t in chi_vals:
        g_bar_t = chi_t * A0_INT
        t3_val  = math.sqrt(g_bar_t * A0_INT) * math.exp(-chi_t) / A0_INT
        # MOND extra = g_bar*(nu-1) unde nu = 1/(1-exp(-sqrt(chi)))
        x = math.sqrt(chi_t)
        denom = 1.0 - math.exp(-x)
        nu = 1.0 / denom if denom > 1e-15 else 1.0 / (x - x**3/6)
        mond_extra = chi_t * (nu - 1.0)  # in unitati de a0
        ratio = t3_val / max(mond_extra, 1e-9)
        print(f"  {chi_t:8.3f}  {t3_val:10.4f}  {mond_extra:14.4f}  {ratio:8.4f}")
    print()

    # ------------------------------------------------------------------
    # Modele de referinta
    # ------------------------------------------------------------------
    chi2_null = chi2_all(all_pts, v_null)
    print(f"M0 Null:     chi2/N = {chi2_null/n:.3f}")

    g_dag_fit, chi2_mond = golden_search(
        lambda g: chi2_all(all_pts, lambda p: v_mond(p, g)),
        0.0001 * A0_INT, 200.0 * A0_INT)
    print(f"M1 MOND RAR: chi2/N = {chi2_mond/n:.3f}  g†={g_dag_fit*G_UNIT:.3e} m/s²  "
          f"(g†/a0={g_dag_fit/A0_INT:.3f})")
    print()

    # ------------------------------------------------------------------
    # M8a: T3 only (g_dag = a0 fix)
    # ------------------------------------------------------------------
    print("M8a: T3 only (g_dag=a0 fix)...", end="", flush=True)
    k_8a, chi2_8a = golden_search(
        lambda k: chi2_all(all_pts, lambda p: v_m8a(p, k)), 0.0, 20.0)
    print(f" chi2/N={chi2_8a/n:.3f}  k={k_8a:.5f}")

    # ------------------------------------------------------------------
    # M8b: T3 + T2 (k1, k2)
    # ------------------------------------------------------------------
    print("M8b: T3+T2 (2 param)...", end="", flush=True)
    k1_8b, k2_8b, chi2_8b = fit_2param(
        lambda k1, k2: chi2_all(all_pts, lambda p: v_m8b(p, k1, k2)),
        0.0, 20.0, 0.0, 10.0, n_outer=50)
    print(f" chi2/N={chi2_8b/n:.3f}  k1={k1_8b:.5f}, k2={k2_8b:.5f}")

    # ------------------------------------------------------------------
    # M8c: T3 cu g_dag liber (k, g_dag)
    # ------------------------------------------------------------------
    print("M8c: T3 cu g_dag liber...", end="", flush=True)
    k_8c, gd_8c, chi2_8c = fit_2param(
        lambda k, gd: chi2_all(all_pts, lambda p: v_m8c(p, k, gd)),
        0.0, 20.0, 0.01 * A0_INT, 20.0 * A0_INT, n_outer=60)
    print(f" chi2/N={chi2_8c/n:.3f}  k={k_8c:.5f}, g_dag={gd_8c*G_UNIT:.3e} m/s²  "
          f"(g_dag/a0={gd_8c/A0_INT:.3f})")

    # ------------------------------------------------------------------
    # M8d: nu_QNG interpolation (k, eps)
    # ------------------------------------------------------------------
    print("M8d: nu_QNG interp...", end="", flush=True)
    k_8d, eps_8d, chi2_8d = fit_2param(
        lambda k, eps: chi2_all(all_pts, lambda p: v_m8d(p, k, eps)),
        0.0, 5.0, 1e-4, 2.0, n_outer=50)
    print(f" chi2/N={chi2_8d/n:.3f}  k={k_8d:.5f}, eps={eps_8d:.5f}")

    # ------------------------------------------------------------------
    # Tabel comparativ
    # ------------------------------------------------------------------
    print()
    print("=" * 72)
    print("COMPARATIE COMPLETA D4→D7")
    print("=" * 72)
    print(f"{'Model':42s}  {'chi2/N':>8s}  {'vs Null':>8s}  {'vs MOND':>8s}")
    print("-" * 72)

    results = [
        ("M0 Null",                          chi2_null, 0),
        ("D4c Kernel exp (tau=73kpc)",        254.72 * n, 1),
        ("D5 Power-law×MOND factor",          210.81 * n, 2),
        ("D6 M7b T2=S2*g_bar/√(1+chi)",      240.05 * n, 1),
        ("M8a T3=√(g*a0)·exp(-chi)  [1p]",   chi2_8a,   1),
        ("M8b T3+T2  [2p]",                   chi2_8b,   2),
        ("M8c T3 g_dag liber  [2p]",          chi2_8c,   2),
        ("M8d nu_QNG interp  [2p]",           chi2_8d,   2),
        ("M1 MOND RAR  [1p]",                 chi2_mond,  1),
    ]
    for name, chi2_v, k_par in results:
        vs_null = (chi2_null - chi2_v) / chi2_null * 100
        vs_mond = chi2_v / chi2_mond
        m = " <--" if name.startswith("M1") else ""
        print(f"  {name:40s}  {chi2_v/n:8.3f}  {vs_null:7.1f}%  {vs_mond:7.3f}×{m}")
    print()

    # ------------------------------------------------------------------
    # RAR bins pentru cel mai bun model
    # ------------------------------------------------------------------
    chi2_list = [
        (chi2_8a, lambda p: v_m8a(p, k_8a), "M8a"),
        (chi2_8b, lambda p: v_m8b(p, k1_8b, k2_8b), "M8b"),
        (chi2_8c, lambda p: v_m8c(p, k_8c, gd_8c), "M8c"),
        (chi2_8d, lambda p: v_m8d(p, k_8d, eps_8d), "M8d"),
    ]
    best_model = min(chi2_list, key=lambda x: x[0])
    best_chi2, best_fn, best_name = best_model
    chi2_mond_fn = lambda p: v_mond(p, g_dag_fit)

    print(f"RAR bins pentru {best_name} (cel mai bun model QNG):")
    print(f"  {'chi=g_bar/a0':>12s}  {'n':>5s}  {'g_obs/g_bar':>12s}  "
          f"{'M8/g_bar':>12s}  {'MOND/g_bar':>12s}  {'diff':>8s}")
    bins_best  = rar_bins(all_pts, best_fn)
    bins_mond  = rar_bins(all_pts, chi2_mond_fn)
    for b, bm in zip(bins_best, bins_mond):
        ratio_d  = b["g_obs_data"]  / max(b["g_bar"], 1e-9)
        ratio_m  = b["g_obs_model"] / max(b["g_bar"], 1e-9)
        ratio_r  = bm["g_obs_model"] / max(bm["g_bar"], 1e-9)
        diff     = ratio_m - ratio_d
        indicator = "→OK" if abs(diff) < 0.3 else ("↑" if diff > 0 else "↓")
        print(f"  {b['chi']:12.3f}  {b['n']:5d}  {ratio_d:12.3f}  "
              f"{ratio_m:12.3f}  {ratio_r:12.3f}  {indicator}")
    print()

    # ------------------------------------------------------------------
    # Diagnostice per galaxie (cel mai bun model)
    # ------------------------------------------------------------------
    gal_stats = []
    for gid, pts in gals.items():
        c_null = sum(((p["v"]-v_null(p))/p["ve"])**2 for p in pts)
        c_best = sum(((p["v"]-best_fn(p))/p["ve"])**2 for p in pts)
        c_mond = sum(((p["v"]-chi2_mond_fn(p))/p["ve"])**2 for p in pts)
        nm = len(pts)
        if nm > 0:
            gal_stats.append({
                "gid": gid, "n": nm,
                "c_null": c_null/nm, "c_best": c_best/nm, "c_mond": c_mond/nm,
            })
    beats_mond = [g for g in gal_stats if g["c_best"] < g["c_mond"]]
    print(f"Galaxii unde {best_name} bate MOND: {len(beats_mond)}/{len(gal_stats)}")
    if beats_mond:
        print(f"  {[g['gid'] for g in sorted(beats_mond, key=lambda x: x['c_mond']-x['c_best'], reverse=True)[:8]]}")
    print()

    # ------------------------------------------------------------------
    # Analiza M8c: g_dag optim vs a0
    # ------------------------------------------------------------------
    print("Analiza M8c — g_dag QNG vs a0 MOND:")
    print(f"  g_dag MOND (M1):  {g_dag_fit*G_UNIT:.4e} m/s²  (g_dag/a0={g_dag_fit/A0_INT:.4f})")
    print(f"  g_dag QNG (M8c):  {gd_8c*G_UNIT:.4e} m/s²  (g_dag/a0={gd_8c/A0_INT:.4f})")
    ratio_gdag = gd_8c / g_dag_fit
    if 0.5 < ratio_gdag < 2.0:
        print(f"  -> g_dag QNG ≈ g_dag MOND (ratio={ratio_gdag:.3f}). Consistent!")
    else:
        print(f"  -> g_dag QNG ≠ g_dag MOND (ratio={ratio_gdag:.3f}). Diferente structurale.")
    print()

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    print("=" * 72)
    print("VERDICT D7")
    print("=" * 72)

    best_chi2_per_n = best_chi2 / n
    imp_null = (chi2_null - best_chi2) / chi2_null * 100
    factor_mond = best_chi2 / chi2_mond
    beats_all = best_chi2 < chi2_mond

    print(f"Best QNG ({best_name}):  chi2/N = {best_chi2_per_n:.3f}")
    print(f"vs Null:   {imp_null:+.1f}%")
    print(f"vs MOND:   {factor_mond:.3f}× ({'+' if factor_mond>1 else ''}{(factor_mond-1)*100:.1f}%)")
    print()

    if beats_all:
        status = f"BONUS: {best_name} bate MOND complet! chi2={best_chi2_per_n:.3f} < {chi2_mond/n:.3f}"
        conclusion = "beats_mond"
    elif factor_mond < 1.3:
        status = f"TARGET HIT: {best_name} la <1.3× de MOND!"
        conclusion = "near_mond"
    elif factor_mond < 1.5:
        status = f"PASS+: {best_name} intre MOND si null, la {factor_mond:.2f}× de MOND."
        conclusion = "pass_plus"
    elif imp_null >= 40.0:
        status = f"PASS: {best_name} > 40% imbunatatire vs Null."
        conclusion = "pass"
    elif imp_null >= 20.0:
        status = f"PARTIAL: {imp_null:.1f}% imbunatatire vs Null, {factor_mond:.2f}× mai rau ca MOND."
        conclusion = "partial"
    else:
        status = "FAIL: sub 20% imbunatatire."
        conclusion = "fail"

    print(status)
    print()

    # Interpretare T3 vs MOND
    print("Interpretare T3 vs MOND:")
    print("  T3 = k*sqrt(g_bar*a0)*exp(-chi)  vs  MOND g_extra ≈ sqrt(g_bar*a0) [la chi→0]")
    if k_8a > 0.5:
        print(f"  k_T3 = {k_8a:.3f}: corectie realista (nu zero)")
    else:
        print(f"  k_T3 = {k_8a:.3f}: corectie mica, T3 contribuie putin")
    print(f"  Supresie exp(-chi) la chi>1: T3 scade mai rapid ca MOND la interior.")
    print(f"  La chi=3: T3/MOND_extra = {math.sqrt(3)*math.exp(-3)/((3/(1-math.exp(-math.sqrt(3))))-3):.4f}")
    print()

    # Straton lag derivare revizuita
    print("Straton lag → a0 (derivare revizuita):")
    print(f"  g_dag M8c = {gd_8c*G_UNIT:.3e} m/s²  vs a0 = {A0_SI:.3e} m/s²")
    delta_e    = 0.00426      # δE0/E0 din raportul straton lag
    cv_val     = 0.414        # cv din T-029
    # Canal cosmologic: a0 = H0 * c * sqrt(Omega_Lambda)
    H0_si  = 70e3 / 3.086e22
    Om_lam = 0.7
    a0_h   = H0_si * 3e8 * math.sqrt(Om_lam)
    print(f"  Canal H0: a0 = H0*c*sqrt(Omega_L) = {a0_h:.3e} m/s²  (vs {A0_SI:.3e})")
    # Canal cv: a0 = (1 - cv) * (c^2 / R_Hubble)
    R_hub  = 3e8 / H0_si
    a0_cv  = (1.0 - cv_val) * (3e8)**2 / R_hub
    print(f"  Canal cv: a0 = (1-cv)*c²/R_H = {a0_cv:.3e} m/s²  (vs {A0_SI:.3e})")
    # Canal delta: a0 = delta * c * H0
    a0_d   = delta_e * 3e8 * H0_si
    print(f"  Canal δ:  a0 = delta*c*H0 = {a0_d:.3e} m/s²  (vs {A0_SI:.3e})")
    best_canal = min(
        [("H0*c*sqrt(OmL)", a0_h), ("(1-cv)*c²/R_H", a0_cv), ("delta*c*H0", a0_d)],
        key=lambda x: abs(math.log10(x[1] / A0_SI)))
    print(f"  Cel mai aproape: {best_canal[0]} = {best_canal[1]:.3e} "
          f"(factor {best_canal[1]/A0_SI:.2e} vs a0)")
    print()

    # ------------------------------------------------------------------
    # Salveaza artifacts
    # ------------------------------------------------------------------
    summary = {
        "test_id": "d7-qng-straton-law-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "T3_formula": "sqrt(g_bar*g_dag)*exp(-g_bar/g_dag)  [straton suppression]",
        "T3_physics": {
            "chi→0": "→ sqrt(g_bar*a0) [deep MOND, curba plata]",
            "chi→∞": "→ 0 [Newtonian limit restaurat]",
        },
        "a0_si": A0_SI,
        "n_points": n, "n_galaxies": n_gal,
        "models": {
            "M0_null":  {"chi2_per_n": chi2_null/n},
            "M8a_T3":   {"chi2_per_n": chi2_8a/n, "k": k_8a},
            "M8b_T3T2": {"chi2_per_n": chi2_8b/n, "k1": k1_8b, "k2": k2_8b},
            "M8c_gdag": {"chi2_per_n": chi2_8c/n, "k": k_8c,
                         "g_dag_si": gd_8c*G_UNIT, "g_dag_over_a0": gd_8c/A0_INT},
            "M8d_nuQNG":{"chi2_per_n": chi2_8d/n, "k": k_8d, "eps": eps_8d},
            "M1_MOND":  {"chi2_per_n": chi2_mond/n, "g_dag_si": g_dag_fit*G_UNIT},
        },
        "best_model": best_name,
        "conclusion": conclusion,
        "improve_vs_null_pct": imp_null,
        "factor_vs_mond": factor_mond,
        "galaxies_beats_mond": len(beats_mond),
        "straton_lag_canale": {
            "H0_c_OmL": a0_h,
            "cv_c2_RH": a0_cv,
            "delta_c_H0": a0_d,
        },
    }
    (OUT_DIR / "d7_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
