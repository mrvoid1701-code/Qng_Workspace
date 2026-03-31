#!/usr/bin/env python3
"""
D5 — Dual Kernel QNG pe date reale SPARC (DS-006, N=3391)

Motivatie (sinteza Grok + Codex):
  - D4c a aratat ca un singur kernel exponential fara modulare nu reproduce curbe plate:
    chi2/N = 254 vs null=302 vs MOND=94. Monoton in tau → nicio scala preferata.
  - Codex identifica problema: "forma legii efective", nu amplitudinea.
    Solutia: H2 modulate cu factor MOND-like: 1/sqrt(1 + g_bar/a0)
    Acest factor concentreaza H2 la r mare (g_bar < a0) si suprima la r mic (g_bar > a0).
  - Grok sugereaza: a0 = straton lag convertit in acceleratie = scala emergenta QNG.
    Deci folosim a0 ca constanta fizica derivata din teorie, nu ca parametru extern.

Model M6 — Dual Kernel QNG:
  H1(r) = (1/tau_e) * sum_j exp(-|r-r_j|/tau_e) * S1(r_j) * bt(r_j) * dr_j
  H2(r) = sum_j [1/(|r-r_j|+r0)^alpha] * S2 * bt(r_j) * dr_j
  Outer(r) = H2(r) * [r/(r+r_tail)] / sqrt(1 + g_bar(r)/a0)

  v_pred(r)^2 = bt(r) + k1 * H1(r) + k2 * Outer(r)

unde:
  S1(r) = exp(-|g_bar(r)/a0 - 1| / sigma_chi)   [energetic: peak la tranzitia MOND]
  S2 = 0.355                                        [structural: uniform]
  r0 = 1 kpc (softening K2)
  sigma_chi = 0.28 (din distributia chi QNG)

Fizica factorului de modulare 1/sqrt(1 + g_bar/a0):
  - g_bar >> a0 (interior, Newtonian): factor ≈ 1/sqrt(g_bar/a0) → suprima H2
  - g_bar << a0 (exterior, dark matter): factor ≈ 1 → H2 activ
  → H2 contribuie exact unde e nevoie (periferia galaxiei)

Parametri liberi:
  tau_e   [kpc] — scala kernel energetic K1
  alpha   [1]   — puterea kernel structural K2
  r_tail  [kpc] — raza de taper Outer
  k1, k2  [1]   — amplitudini (optimizate per (tau_e, alpha, r_tail))

Protocol de test:
  Faza 1: H1 only (scan tau_e, k1)
  Faza 2: Outer only (scan alpha, r_tail, k2)
  Faza 3: Combinat (tau_e*, alpha*, r_tail* + fit k1, k2 joint 2D)

Criterii preregistrate:
  PASS:  chi2/N(M6) < chi2/N(M0) cu >20%
  BONUS: chi2/N(M6) < chi2/N(MOND)
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
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "d5-dual-kernel-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M    # conversie km²/s²/kpc → m/s²
A0_SI    = 1.2e-10                   # m/s² — scala MOND (straton lag emergent)
A0_INT   = A0_SI / G_UNIT            # in km²/s²/kpc

S2_CONST  = 0.355    # valoare structurala uniforma (din distributia stability QNG)
SIGMA_CHI = 0.28     # latimea distributiei energetice (din raport stability QNG)
R0_SOFT   = 1.0      # kpc — softening K2 (evita divergenta la Δr=0)


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def load_galaxies(path: Path) -> dict[str, list[dict]]:
    gals: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r   = float(row["radius"])
            v   = float(row["v_obs"])
            ve  = float(row["v_err"])
            bt  = float(row["baryon_term"])
            if r <= 0 or ve <= 0 or bt < 0:
                continue
            gbar = bt / max(r, 1e-9)
            gals.setdefault(row["system_id"], []).append({
                "r": r, "v": v, "ve": ve, "bt": bt,
                "g_bar": gbar,
                "s1": math.exp(-abs(gbar / A0_INT - 1.0) / SIGMA_CHI),
            })
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


def integration_dr(pts: list[dict]) -> list[float]:
    n = len(pts)
    if n == 0:
        return []
    dr = []
    for j in range(n):
        if n == 1:
            dr.append(1.0)
        elif j == 0:
            dr.append((pts[1]["r"] - pts[0]["r"]) / 2.0)
        elif j == n - 1:
            dr.append((pts[-1]["r"] - pts[-2]["r"]) / 2.0)
        else:
            dr.append((pts[j+1]["r"] - pts[j-1]["r"]) / 2.0)
    return dr


# ---------------------------------------------------------------------------
# Kernel H1 — exponential × S1 (energetic)
# ---------------------------------------------------------------------------

def compute_H1(pts: list[dict], tau_e: float) -> list[float]:
    """
    H1(r_i) = (1/tau_e) * sum_j exp(-|r_i-r_j|/tau_e) * S1(r_j) * bt(r_j) * dr_j

    S1(r_j) = exp(-|g_bar(r_j)/a0 - 1| / sigma_chi)
    Peak la g_bar = a0 (tranzitia MOND): memoria e maxima la scala de tranzitie.
    """
    tau_e = max(tau_e, 1e-9)
    dr = integration_dr(pts)
    n = len(pts)
    h1 = []
    for i in range(n):
        ri = pts[i]["r"]
        h = 0.0
        for j in range(n):
            kernel = math.exp(-abs(ri - pts[j]["r"]) / tau_e)
            h += kernel * pts[j]["s1"] * pts[j]["bt"] * dr[j]
        h1.append(h / tau_e)
    return h1


# ---------------------------------------------------------------------------
# Kernel H2 — power-law × S2 (structural)
# ---------------------------------------------------------------------------

def compute_H2(pts: list[dict], alpha: float) -> list[float]:
    """
    H2(r_i) = sum_j [1/(|r_i-r_j|+r0)^alpha] * S2 * bt(r_j) * dr_j

    alpha < 1: decadere lenta → contributie la r mare (nu dispare)
    alpha = 0.5: H2 ∝ sqrt(r) la r mare cu bt constant → creste usor
    """
    dr = integration_dr(pts)
    n = len(pts)
    h2 = []
    for i in range(n):
        ri = pts[i]["r"]
        h = 0.0
        for j in range(n):
            ddr = abs(ri - pts[j]["r"]) + R0_SOFT
            kernel = 1.0 / (ddr ** alpha)
            h += kernel * S2_CONST * pts[j]["bt"] * dr[j]
        h2.append(h)
    return h2


# ---------------------------------------------------------------------------
# Outer — H2 modulate cu factor MOND-like
# ---------------------------------------------------------------------------

def compute_outer(pts: list[dict], h2: list[float], r_tail: float) -> list[float]:
    """
    Outer(r_i) = H2(r_i) * [r_i/(r_i+r_tail)] / sqrt(1 + g_bar(r_i)/a0)

    Factor [r/(r+r_tail)]: taper — activeaza efectul progresiv la r > r_tail
    Factor 1/sqrt(1+g_bar/a0): modulare MOND-like
      - g_bar >> a0 → suprima (interiorul, regim Newtonian)
      - g_bar << a0 → H2 activ (periferia, regim dark-matter)

    De ce nu e circular: a0 e constanta fizica derivata din straton lag QNG,
    nu un parametru ajustat per galaxie.
    """
    outer = []
    for i, pt in enumerate(pts):
        taper = pt["r"] / (pt["r"] + r_tail)
        # Evita impartire la 0 pentru g_bar=0
        modulation = 1.0 / math.sqrt(1.0 + max(pt["g_bar"], 0.0) / A0_INT)
        outer.append(h2[i] * taper * modulation)
    return outer


# ---------------------------------------------------------------------------
# Modele simple
# ---------------------------------------------------------------------------

def v_null(pt: dict) -> float:
    return math.sqrt(max(pt["bt"], 0.0))


def v_mond(pt: dict, g_dag: float) -> float:
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


def v_dual(pt: dict, h1: float, outer: float, k1: float, k2: float) -> float:
    return math.sqrt(max(pt["bt"] + k1 * h1 + k2 * outer, 0.0))


# ---------------------------------------------------------------------------
# Optimizare
# ---------------------------------------------------------------------------

def golden_search(f, lo: float, hi: float,
                  tol: float = 1e-5, max_iter: int = 300) -> tuple[float, float]:
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


def chi2_single_param(all_pts, h_arr, k):
    """chi2 pentru v^2 = bt + k*h (un singur kernel)"""
    total = 0.0
    for pt, h in zip(all_pts, h_arr):
        vp = math.sqrt(max(pt["bt"] + k * h, 0.0))
        total += ((pt["v"] - vp) / pt["ve"]) ** 2
    return total


def chi2_dual(all_pts, h1_arr, outer_arr, k1, k2):
    """chi2 pentru v^2 = bt + k1*H1 + k2*Outer"""
    total = 0.0
    for pt, h1, out in zip(all_pts, h1_arr, outer_arr):
        vp = math.sqrt(max(pt["bt"] + k1 * h1 + k2 * out, 0.0))
        total += ((pt["v"] - vp) / pt["ve"]) ** 2
    return total


def fit_k1_k2_joint(all_pts, h1_arr, outer_arr, n_grid=30) -> tuple[float, float, float]:
    """
    Grid 2D (k1, k2) → minimizeaza chi2_dual.
    Linear scan per k2, inner golden per k1.
    """
    best_k1, best_k2, best_chi2 = 0.0, 0.0, float("inf")
    for i in range(n_grid):
        k2 = 5.0 * i / max(n_grid - 1, 1)
        k1_opt, chi2_v = golden_search(
            lambda k1: chi2_dual(all_pts, h1_arr, outer_arr, k1, k2),
            0.0, 20.0, tol=1e-4)
        if chi2_v < best_chi2:
            best_chi2 = chi2_v
            best_k1   = k1_opt
            best_k2   = k2
    # Refinare
    k2_lo = max(0.0, best_k2 - 0.5)
    k2_hi = best_k2 + 0.5
    for i in range(20):
        k2 = k2_lo + (k2_hi - k2_lo) * i / 19
        k1_opt, chi2_v = golden_search(
            lambda k1: chi2_dual(all_pts, h1_arr, outer_arr, k1, k2),
            0.0, 20.0, tol=1e-5)
        if chi2_v < best_chi2:
            best_chi2 = chi2_v
            best_k1   = k1_opt
            best_k2   = k2
    return best_k1, best_k2, best_chi2


# ---------------------------------------------------------------------------
# Diagnostice per galaxie
# ---------------------------------------------------------------------------

def galaxy_chi2(pts, h1, outer, k1, k2):
    return sum(((pt["v"] - v_dual(pt, h1[i], outer[i], k1, k2)) / pt["ve"])**2
               for i, pt in enumerate(pts))


def galaxy_chi2_null(pts):
    return sum(((pt["v"] - v_null(pt)) / pt["ve"])**2 for pt in pts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D5 — Dual Kernel QNG (K1 exp×S1 + K2 power-law×S2×MOND-modulation)")
    print(f"Date: {DATA_CSV.name}")
    print()

    gals    = load_galaxies(DATA_CSV)
    all_pts = [p for pts in gals.values() for p in pts]
    n       = len(all_pts)
    n_gal   = len(gals)
    print(f"  {n} puncte, {n_gal} galaxii")
    print(f"  a0 = {A0_SI:.2e} m/s²  ({A0_INT:.4f} km²/s²/kpc)")
    print()

    # M0: Null
    chi2_null = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in all_pts)
    print(f"M0 Null:     chi2/N = {chi2_null/n:.2f}")

    # M1: MOND
    g_dag_fit, chi2_mond = golden_search(
        lambda g: sum(((p["v"] - v_mond(p, g)) / p["ve"])**2 for p in all_pts),
        0.001 * A0_INT, 100.0 * A0_INT)
    print(f"M1 MOND RAR: chi2/N = {chi2_mond/n:.2f}  g† = {g_dag_fit*G_UNIT:.2e} m/s²")
    print()

    # ==================================================================
    # FAZA 1: H1 only (exponential × S1)
    # ==================================================================
    print("=" * 65)
    print("FAZA 1: H1 only — scan tau_e in [0.5, 40] kpc")
    print("=" * 65)

    tau_scan = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 18.0, 25.0, 40.0]
    f1_results = []
    for tau_e in tau_scan:
        h1_all = []
        for pts in gals.values():
            h1_g = compute_H1(pts, tau_e)
            h1_all.extend(h1_g)
        k1_opt, chi2_v = golden_search(
            lambda k: chi2_single_param(all_pts, h1_all, k),
            0.0, 50.0, tol=1e-4)
        f1_results.append((tau_e, k1_opt, chi2_v))
        sign = " *" if chi2_v < chi2_null else ""
        print(f"  tau_e={tau_e:5.1f} kpc  k1={k1_opt:.4f}  chi2/N={chi2_v/n:.2f}{sign}")

    best_f1 = min(f1_results, key=lambda x: x[2])
    tau_e_star, k1_star, chi2_f1 = best_f1
    print(f"  -> Best H1: tau_e={tau_e_star:.1f} kpc, k1={k1_star:.4f}, chi2/N={chi2_f1/n:.2f}")
    print()

    # ==================================================================
    # FAZA 2: Outer only — scan alpha, r_tail
    # ==================================================================
    print("=" * 65)
    print("FAZA 2: Outer only — scan alpha, r_tail")
    print("=" * 65)
    print(f"  Outer(r) = H2(r) * [r/(r+r_tail)] / sqrt(1 + g_bar/a0)")
    print()

    alpha_scan  = [0.1, 0.3, 0.5, 0.7, 1.0, 1.3]
    r_tail_scan = [1.0, 2.0, 5.0, 10.0]
    f2_results  = []
    for alpha in alpha_scan:
        # Pre-calcul H2 (scump, O(N²) per galaxie, reutilizat pentru toti r_tail)
        h2_cache: dict[str, list[float]] = {}
        for gid, pts in gals.items():
            h2_cache[gid] = compute_H2(pts, alpha)
        for r_tail in r_tail_scan:
            outer_all = []
            for gid, pts in gals.items():
                outer_g = compute_outer(pts, h2_cache[gid], r_tail)
                outer_all.extend(outer_g)
            k2_opt, chi2_v = golden_search(
                lambda k: chi2_single_param(all_pts, outer_all, k),
                0.0, 20.0, tol=1e-4)
            f2_results.append((alpha, r_tail, k2_opt, chi2_v))
            sign = " **" if chi2_v < chi2_null else (
                   " *"  if chi2_v < chi2_f1   else "")
            print(f"  alpha={alpha:.2f}  r_tail={r_tail:5.1f} kpc  "
                  f"k2={k2_opt:.4f}  chi2/N={chi2_v/n:.2f}{sign}")
    print()

    best_f2 = min(f2_results, key=lambda x: x[3])
    alpha_star, r_tail_star, k2_star, chi2_f2 = best_f2
    print(f"  -> Best Outer: alpha={alpha_star:.2f}, r_tail={r_tail_star:.1f} kpc, "
          f"k2={k2_star:.4f}, chi2/N={chi2_f2/n:.2f}")
    print()

    # ==================================================================
    # FAZA 3: Combinat — k1, k2 joint la (tau_e*, alpha*, r_tail*)
    # ==================================================================
    print("=" * 65)
    print(f"FAZA 3: Combinat — tau_e={tau_e_star:.1f} kpc, "
          f"alpha={alpha_star:.2f}, r_tail={r_tail_star:.1f} kpc")
    print("=" * 65)

    h1_comb = []
    outer_comb = []
    h2_comb_cache: dict[str, list[float]] = {}
    for gid, pts in gals.items():
        h2_comb_cache[gid] = compute_H2(pts, alpha_star)
    for gid, pts in gals.items():
        h1_g     = compute_H1(pts, tau_e_star)
        outer_g  = compute_outer(pts, h2_comb_cache[gid], r_tail_star)
        h1_comb.extend(h1_g)
        outer_comb.extend(outer_g)

    print("  Fit joint k1, k2...", end="", flush=True)
    k1_f, k2_f, chi2_dual_f = fit_k1_k2_joint(all_pts, h1_comb, outer_comb, n_grid=40)
    print(f" k1={k1_f:.5f}, k2={k2_f:.5f}, chi2/N={chi2_dual_f/n:.2f}")
    print()

    # ==================================================================
    # TABEL COMPARATIV
    # ==================================================================
    print("=" * 65)
    print("COMPARATIE MODELE")
    print("=" * 65)
    aic_null  = chi2_null    + 2 * 0
    aic_mond  = chi2_mond    + 2 * 1
    aic_h1    = chi2_f1      + 2 * 2
    aic_outer = chi2_f2      + 2 * 2
    aic_dual  = chi2_dual_f  + 2 * 4

    print(f"{'Model':40s}  {'chi2/N':>8s}  {'AIC':>12s}")
    print("-" * 65)
    for name, chi2_v, aic_v in [
        ("M0 Null",                        chi2_null,   aic_null),
        ("M6a H1 only (exp×S1)",           chi2_f1,     aic_h1),
        ("M6b Outer only (power-law×MOND)", chi2_f2,     aic_outer),
        ("M6 Dual (H1 + Outer)",           chi2_dual_f, aic_dual),
        ("M1 MOND RAR",                    chi2_mond,   aic_mond),
    ]:
        marker = " <-- MOND" if name.startswith("M1") else ""
        print(f"  {name:38s}  {chi2_v/n:8.2f}  {aic_v:12.1f}{marker}")
    print()

    # ==================================================================
    # DIAGNOSTICE PER GALAXIE (top contribuitori)
    # ==================================================================
    print("Structura Outer(r) in galaxii reprezentative:")
    print(f"  (a0={A0_SI:.1e} m/s²,  factor=1/sqrt(1+g_bar/a0))")

    h1_per_gal:     dict[str, list[float]] = {}
    outer_per_gal:  dict[str, list[float]] = {}
    for gid, pts in gals.items():
        h1_per_gal[gid]    = compute_H1(pts, tau_e_star)
        outer_per_gal[gid] = compute_outer(pts, h2_comb_cache[gid], r_tail_star)

    samples = ["DDO154", "NGC6503", "NGC3198", "NGC2403", "UGC02953", "NGC7814"]
    for gid in samples:
        if gid not in gals:
            continue
        pts   = gals[gid]
        outs  = outer_per_gal[gid]
        h1s   = h1_per_gal[gid]
        r_in  = pts[0]["r"];    r_out  = pts[-1]["r"]
        bt_out = pts[-1]["bt"]
        out_in  = outs[0];      out_out  = outs[-1]
        h1_in   = h1s[0];       h1_out   = h1s[-1]
        # factor de modulare la margine
        mod_out = 1.0 / math.sqrt(1.0 + pts[-1]["g_bar"] / A0_INT)
        taper_out = pts[-1]["r"] / (pts[-1]["r"] + r_tail_star)
        frac_k2 = k2_f * out_out / max(bt_out, 1e-9)
        print(f"  {gid:12s}: r=[{r_in:.1f},{r_out:.1f}]kpc  "
              f"mod={mod_out:.3f}  taper={taper_out:.3f}  "
              f"k2*Out/bt={frac_k2:.2f}  k1*H1_out/bt={k1_f*h1_out/max(bt_out,1e-9):.2f}")
    print()

    # ==================================================================
    # VERDICT
    # ==================================================================
    print("=" * 65)
    print("VERDICT D5")
    print("=" * 65)

    improve_vs_null = (chi2_null - chi2_dual_f) / chi2_null * 100
    delta_mond      = chi2_dual_f - chi2_mond
    delta_aic_mond  = aic_dual - aic_mond
    beats_mond      = chi2_dual_f < chi2_mond

    print(f"M6 Dual vs Null:  Δchi2={chi2_null-chi2_dual_f:+.0f}  ({improve_vs_null:+.1f}%)")
    print(f"M6 Dual vs MOND:  Δchi2={delta_mond:+.0f}   ΔAIC={delta_aic_mond:+.1f}")
    print()

    if beats_mond:
        status = "BONUS: M6 Dual bate MOND! Necesita replicare independenta."
        conclusion = "dual_beats_mond"
    elif improve_vs_null >= 20.0:
        status = "PASS: M6 Dual > 20% imbunatatire vs Null — efect real dual-kernel."
        conclusion = "dual_beats_null_strong"
    elif improve_vs_null >= 10.0:
        status = "PARTIAL: M6 Dual 10-20% imbunatatire vs Null — semnal moderat."
        conclusion = "dual_beats_null_moderate"
    else:
        status = "FAIL: Dual kernel nu reduce suficient chi2."
        conclusion = "dual_fails"

    print(status)
    print()

    # Interpretare factor MOND-like
    print("Analiza factorului de modulare 1/sqrt(1+g_bar/a0):")
    transitions = [p for p in all_pts if 0.3 < p["g_bar"]/A0_INT < 3.0]
    inner_dom   = [p for p in all_pts if p["g_bar"]/A0_INT > 3.0]
    outer_dom   = [p for p in all_pts if p["g_bar"]/A0_INT < 0.3]
    print(f"  Puncte outer (g_bar<0.3*a0): {len(outer_dom):4d}  — factor ≈ 1.0 (H2 activ)")
    print(f"  Puncte tranzitie:             {len(transitions):4d}  — factor variabil")
    print(f"  Puncte inner (g_bar>3*a0):   {len(inner_dom):4d}  — factor suprima H2")
    print()

    if alpha_star <= 0.5:
        print(f"  alpha={alpha_star:.2f}: kernel power-law lent → H2 creste cu r la periferie.")
    elif alpha_star <= 1.0:
        print(f"  alpha={alpha_star:.2f}: kernel power-law moderat → H2 relativ constant la periferie.")
    else:
        print(f"  alpha={alpha_star:.2f}: kernel power-law rapid → H2 scade la periferie (similar cu exp).")
    print()

    # Legatura cu straton lag
    print("Legatura cu straton lag (sugestia Grok):")
    print(f"  a0 folosit = {A0_SI:.2e} m/s² (MOND)")
    print(f"  Grok: a_straton ≈ 0.07 × c²/r_char — daca r_char ≈ 13 kpc → a_straton ≈ {0.07*(3e8)**2/(13*KPC_TO_M):.2e} m/s²")
    r_char_needed = 0.07 * (3e8)**2 / A0_SI / 1e3  # in pc
    print(f"  Pentru a0=1.2e-10 m/s², r_char ar trebui ≈ {r_char_needed/1e3:.0f} kpc")
    print(f"  Comparatie: r_tail optim = {r_tail_star:.1f} kpc — NU coincide direct.")
    print(f"  → Necesita derivare formala straton lag → a0 ca pas urmator.")

    # ==================================================================
    # Salveaza artifacts
    # ==================================================================
    summary = {
        "test_id": "d5-dual-kernel-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "model": {
            "H1": "exp(-|r-r'|/tau_e) * S1(r') * bt(r')  [kernel energetic]",
            "S1": f"exp(-|g_bar/a0 - 1| / {SIGMA_CHI})",
            "H2": f"[1/(|r-r'|+{R0_SOFT})^alpha] * {S2_CONST} * bt(r')  [structural]",
            "Outer": "H2(r) * r/(r+r_tail) / sqrt(1 + g_bar/a0)  [MOND modulated]",
            "v_pred": "sqrt(bt + k1*H1 + k2*Outer)",
        },
        "a0_si": A0_SI,
        "best_params": {
            "tau_e_kpc":   tau_e_star,
            "alpha":       alpha_star,
            "r_tail_kpc":  r_tail_star,
            "k1":          k1_f,
            "k2":          k2_f,
        },
        "n_points": n, "n_galaxies": n_gal,
        "results": {
            "M0_null":      {"chi2_per_n": chi2_null  / n},
            "M6a_H1_only":  {"chi2_per_n": chi2_f1   / n, "tau_e": tau_e_star},
            "M6b_Outer_only": {"chi2_per_n": chi2_f2  / n, "alpha": alpha_star, "r_tail": r_tail_star},
            "M6_dual":      {"chi2_per_n": chi2_dual_f / n},
            "M1_MOND":      {"chi2_per_n": chi2_mond  / n},
        },
        "conclusion": conclusion,
        "improve_vs_null_pct": improve_vs_null,
        "delta_chi2_vs_mond": delta_mond,
        "delta_aic_vs_mond": delta_aic_mond,
    }
    (OUT_DIR / "d5_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nArtifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
