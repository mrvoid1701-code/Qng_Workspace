#!/usr/bin/env python3
"""
D6 — QNG Effective Law (lege efectiva locala, per-punct)

Motivatie din analiza D4c/D5:
  - D4c: kernel exp fara modulare → chi2/N=254, monoton in tau, fara minim fizic
  - D5: kernel power-law + factor MOND → chi2/N=210, salt de 17% din factor
  - Problema comuna: kernelele integreaza global → contributie prea uniforma

Solutia (Codex): schimba "forma legii efective", nu amplitudinea.
  g_extra trebuie sa fie PER-PUNCT si sa urmeze forma corecta:
    - g_bar >> a0 (interior, Newtonian): g_extra → 0
    - g_bar << a0 (periferie, dark matter): g_extra → sqrt(g_bar * a0)
  Aceasta ultima forma produce curbe plate in mod NATURAL (ca MOND).

Derivare QNG:
  In QNG, campul de memorie are 2 componente din dualitate S1/S2:
  - S1 (energetic/chi): S1(r) = exp(-|g_bar/a0 - 1| / sigma_chi)
    Peak la tranzitia Newtonian→MOND (g_bar = a0)
  - S2 (structural/uniform): S2 = 0.355 (constant din distributia stability)

  Legea efectiva QNG:
    g_QNG(r) = k1 * S1(r) * sqrt(g_bar(r) * a0)     [termen energetic]
             + k2 * S2 * g_bar(r) / sqrt(1 + g_bar(r)/a0)  [termen structural]

  Model final:
    v_pred(r)^2 = bt(r) + r * g_QNG(r)
               = g_bar*r * [1 + k1*S1*sqrt(a0/g_bar) + k2*S2/sqrt(1+g_bar/a0)]

Demonstratie curba plata din termen 1:
  La r mare, masa barionica concentrata: g_bar = GM/r^2
  v^2 ≈ r * k1 * S1 * sqrt(g_bar * a0)
       = k1 * S1 * sqrt(g_bar * a0 * r^2)
       = k1 * S1 * sqrt(GM * a0)    ← CONSTANTA! Curba plata emergenta.

  Identic cu MOND deep regime: v^4 = G * M_bar * a0

De ce nu e circular:
  - g_bar = bt/r = GM_baryon/r^2 din masa stele+gaz (independent de v_obs)
  - a0 = 1.2e-10 m/s² constanta fizica (straton lag emergent)
  - S1, S2 din distributia chi QNG (constant sigma_chi=0.28, S2=0.355)
  - k1, k2 sunt singurii parametri liberi (2 total)

Comparatii:
  M0: Null (0 parametri)
  M7a: k1 only — termen energetic S1*sqrt(g_bar*a0)
  M7b: k2 only — termen structural S2*g_bar/sqrt(1+g_bar/a0)
  M7: Dual (k1+k2, 2 parametri)
  M1: MOND RAR (1 parametru: g†)
  M7+: MOND-QNG hibrid cu k, g_dag (2 parametri, benchmark)

Criterii preregistrate:
  PASS:  chi2/N(M7) < chi2/N(M0) cu >30%
  TARGET: chi2/N(M7) aproape de chi2/N(MOND) (Δ < 50%)
  BONUS:  chi2/N(M7) < chi2/N(MOND)
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
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "d6-qng-effective-law-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M    # km²/s²/kpc → m/s²
A0_SI    = 1.2e-10                   # MOND / straton lag emergent [m/s²]
A0_INT   = A0_SI / G_UNIT            # [km²/s²/kpc]

S2_CONST  = 0.355
SIGMA_CHI = 0.28


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
            s1    = math.exp(-abs(chi - 1.0) / SIGMA_CHI)
            gals.setdefault(row["system_id"], []).append({
                "r":     r,
                "v":     v,
                "ve":    ve,
                "bt":    bt,
                "g_bar": g_bar,
                "chi":   chi,
                "s1":    s1,
            })
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


# ---------------------------------------------------------------------------
# Lege efectiva QNG — per punct, fara integrale
# ---------------------------------------------------------------------------

def g_qng_term1(pt: dict) -> float:
    """
    Termen 1 (energetic): k1 * S1(r) * sqrt(g_bar(r) * a0)

    Proprietati:
    - Peak la g_bar = a0 (tranzitia MOND), S1 ≈ 1
    - La g_bar << a0: sqrt(g_bar*a0) → 0 dar S1 → exp(-1/0.28) ≈ 0.03 (scade)
    - La g_bar >> a0: sqrt(g_bar*a0) creste dar S1 → 0 exponential (suprima)
    - Maximum real: in jurul g_bar ~ a0

    v^2_extra = r * k1 * g_qng_term1 → k1 * S1 * sqrt(g_bar * a0 * r^2)
    La r mare cu masa concentrata (g_bar ~ GM/r^2):
      → k1 * S1 * sqrt(GM * a0) = const → CURBA PLATA
    """
    return pt["s1"] * math.sqrt(max(pt["g_bar"] * A0_INT, 0.0))


def g_qng_term2(pt: dict) -> float:
    """
    Termen 2 (structural): k2 * S2 * g_bar / sqrt(1 + g_bar/a0)

    Proprietati:
    - La g_bar << a0: → k2 * S2 * g_bar (proportional cu baryon)
    - La g_bar >> a0: → k2 * S2 * sqrt(g_bar * a0) (converge la forma MOND)
    - Continuu si fara divergenta
    """
    return S2_CONST * pt["g_bar"] / math.sqrt(1.0 + pt["g_bar"] / A0_INT)


def v_model_m7(pt: dict, k1: float, k2: float) -> float:
    """
    v_pred^2 = bt(r) + r * [k1 * T1(r) + k2 * T2(r)]
    unde T1 = g_qng_term1, T2 = g_qng_term2
    """
    extra = pt["r"] * (k1 * g_qng_term1(pt) + k2 * g_qng_term2(pt))
    return math.sqrt(max(pt["bt"] + extra, 0.0))


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


def v_mond_qng(pt: dict, k: float, g_dag: float) -> float:
    """
    Hibrid MOND-QNG: v = sqrt(bt + r * k * S1 * sqrt(g_bar * g_dag))
    Verifica daca g_dag din QNG ≈ a0 sau altceva.
    """
    g_extra = k * pt["s1"] * math.sqrt(max(pt["g_bar"] * max(g_dag, 0.0), 0.0))
    return math.sqrt(max(pt["bt"] + pt["r"] * g_extra, 0.0))


# ---------------------------------------------------------------------------
# Optimizare
# ---------------------------------------------------------------------------

def golden_search(f, lo: float, hi: float,
                  tol: float = 1e-6, max_iter: int = 400) -> tuple[float, float]:
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


def fit_k1_k2(all_pts, n_grid=60) -> tuple[float, float, float]:
    """Grid 2D pe (k1, k2) + refinare."""
    best = (0.0, 0.0, float("inf"))
    for i in range(n_grid):
        k2 = 5.0 * i / max(n_grid - 1, 1)
        k1_opt, chi2_v = golden_search(
            lambda k1: sum(((p["v"] - v_model_m7(p, k1, k2)) / p["ve"])**2
                          for p in all_pts),
            0.0, 20.0)
        if chi2_v < best[2]:
            best = (k1_opt, k2, chi2_v)

    # Refinare 2D fine
    k1_c, k2_c, _ = best
    for i in range(40):
        k2 = max(0.0, k2_c - 0.5) + 1.0 * i / 39
        k1_opt, chi2_v = golden_search(
            lambda k1: sum(((p["v"] - v_model_m7(p, k1, k2)) / p["ve"])**2
                          for p in all_pts),
            max(0.0, k1_c - 2.0), k1_c + 2.0, tol=1e-7)
        if chi2_v < best[2]:
            best = (k1_opt, k2, chi2_v)

    return best


# ---------------------------------------------------------------------------
# Analiza RAR — relatia acceleratie observata vs barionica
# ---------------------------------------------------------------------------

def compute_rar_bins(all_pts, k1, k2, n_bins=12) -> list[dict]:
    """
    Imparte g_bar in n_bins logaritmice si compara:
      g_obs_data vs g_obs_model vs g_mond vs g_bar (null)
    """
    g_bars = [p["g_bar"] for p in all_pts if p["g_bar"] > 0]
    log_min = math.log10(min(g_bars))
    log_max = math.log10(max(g_bars))
    bins: list[list[dict]] = [[] for _ in range(n_bins)]
    for p in all_pts:
        if p["g_bar"] <= 0:
            continue
        idx = int((math.log10(p["g_bar"]) - log_min) / (log_max - log_min) * n_bins)
        idx = min(idx, n_bins - 1)
        bins[idx].append(p)

    results = []
    for i, bp in enumerate(bins):
        if not bp:
            continue
        g_bar_m = 10 ** (log_min + (i + 0.5) * (log_max - log_min) / n_bins)
        g_obs_d = [p["v"]**2 / max(p["r"], 1e-9) for p in bp]
        g_obs_m = [(v_model_m7(p, k1, k2)**2) / max(p["r"], 1e-9) for p in bp]
        g_mond  = [v_mond(p, A0_INT)**2 / max(p["r"], 1e-9) for p in bp]
        results.append({
            "g_bar":     g_bar_m,
            "g_obs_data": sum(g_obs_d) / len(g_obs_d),
            "g_obs_m7":  sum(g_obs_m) / len(g_obs_m),
            "g_mond":    sum(g_mond)  / len(g_mond),
            "n":         len(bp),
        })
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D6 — QNG Effective Law (lege locala per-punct, fara integrale)")
    print(f"Date: {DATA_CSV.name}")
    print()

    gals    = load_galaxies(DATA_CSV)
    all_pts = [p for pts in gals.values() for p in pts]
    n       = len(all_pts)
    n_gal   = len(gals)
    print(f"  {n} puncte, {n_gal} galaxii")
    print(f"  a0 = {A0_SI:.2e} m/s²  ({A0_INT:.2f} km²/s²/kpc)")
    print()

    # Distributia chi (g_bar/a0) in date
    chi_vals  = [p["chi"] for p in all_pts]
    chi_below = sum(1 for c in chi_vals if c < 1.0)
    chi_above = sum(1 for c in chi_vals if c >= 1.0)
    chi_near  = sum(1 for c in chi_vals if 0.3 < c < 3.0)
    print(f"  Distributia chi=g_bar/a0:")
    print(f"    chi < 1  (deep MOND): {chi_below:4d} puncte ({100*chi_below/n:.0f}%)")
    print(f"    chi 0.3-3 (tranzitie): {chi_near:4d} puncte ({100*chi_near/n:.0f}%)")
    print(f"    chi > 1  (Newtonian):  {chi_above:4d} puncte ({100*chi_above/n:.0f}%)")
    print()

    # Analizez S1: la ce g_bar e maxima S1?
    s1_vals = [p["s1"] for p in all_pts]
    s1_mean = sum(s1_vals) / len(s1_vals)
    s1_max  = max(s1_vals)
    print(f"  S1 stats: mean={s1_mean:.3f}, max={s1_max:.3f}")
    print(f"  T1 (S1*sqrt(g_bar*a0)) stats per punct:")
    t1_vals = [g_qng_term1(p) for p in all_pts]
    t2_vals = [g_qng_term2(p) for p in all_pts]
    print(f"    T1: mean={sum(t1_vals)/len(t1_vals):.3f}, max={max(t1_vals):.3f}")
    print(f"    T2: mean={sum(t2_vals)/len(t2_vals):.3f}, max={max(t2_vals):.3f}")
    print()

    # ------------------------------------------------------------------
    # M0: Null
    # ------------------------------------------------------------------
    chi2_null = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in all_pts)
    print(f"M0 Null:          chi2/N = {chi2_null/n:.3f}")

    # ------------------------------------------------------------------
    # M1: MOND
    # ------------------------------------------------------------------
    g_dag_fit, chi2_mond = golden_search(
        lambda g: sum(((p["v"] - v_mond(p, g)) / p["ve"])**2 for p in all_pts),
        0.0001 * A0_INT, 200.0 * A0_INT, tol=1e-8)
    print(f"M1 MOND RAR:      chi2/N = {chi2_mond/n:.3f}  g†={g_dag_fit*G_UNIT:.3e} m/s²")

    # ------------------------------------------------------------------
    # M7a: k1 only (termen energetic S1*sqrt(g_bar*a0))
    # ------------------------------------------------------------------
    k1_a, chi2_m7a = golden_search(
        lambda k: sum(((p["v"] - v_model_m7(p, k, 0.0)) / p["ve"])**2 for p in all_pts),
        0.0, 20.0)
    print(f"M7a T1 only:      chi2/N = {chi2_m7a/n:.3f}  k1={k1_a:.5f}")

    # ------------------------------------------------------------------
    # M7b: k2 only (termen structural S2*g_bar/sqrt(1+g_bar/a0))
    # ------------------------------------------------------------------
    k2_b, chi2_m7b = golden_search(
        lambda k: sum(((p["v"] - v_model_m7(p, 0.0, k)) / p["ve"])**2 for p in all_pts),
        0.0, 20.0)
    print(f"M7b T2 only:      chi2/N = {chi2_m7b/n:.3f}  k2={k2_b:.5f}")

    # ------------------------------------------------------------------
    # M7: Dual (k1 + k2)
    # ------------------------------------------------------------------
    print(f"M7 Dual fit...", end="", flush=True)
    k1_f, k2_f, chi2_m7 = fit_k1_k2(all_pts, n_grid=60)
    print(f"  chi2/N = {chi2_m7/n:.3f}  k1={k1_f:.5f}, k2={k2_f:.5f}")

    # ------------------------------------------------------------------
    # M7+: MOND-QNG hibrid (k, g_dag liberi) — benchmark 2 parametri
    # M7+: v = sqrt(bt + r * k * S1 * sqrt(g_bar * g_dag))
    # ------------------------------------------------------------------
    print(f"M7+ MOND-QNG fit...", end="", flush=True)

    def chi2_mqng(k: float, g_dag: float) -> float:
        return sum(((p["v"] - v_mond_qng(p, k, g_dag)) / p["ve"])**2 for p in all_pts)

    best_mqng = (1.0, A0_INT, float("inf"))
    for i in range(30):
        gd = 0.01 * A0_INT + (10.0 * A0_INT - 0.01 * A0_INT) * i / 29
        k_opt, chi2_v = golden_search(lambda k: chi2_mqng(k, gd), 0.0, 20.0)
        if chi2_v < best_mqng[2]:
            best_mqng = (k_opt, gd, chi2_v)
    # Refinare g_dag
    gd_c = best_mqng[1]
    for i in range(20):
        gd = max(0.001*A0_INT, gd_c - 2*A0_INT) + 4*A0_INT * i / 19
        k_opt, chi2_v = golden_search(lambda k: chi2_mqng(k, gd), 0.0, 20.0, tol=1e-7)
        if chi2_v < best_mqng[2]:
            best_mqng = (k_opt, gd, chi2_v)
    k_mq, gd_mq, chi2_mq = best_mqng
    print(f" chi2/N = {chi2_mq/n:.3f}  k={k_mq:.4f}, g_dag={gd_mq*G_UNIT:.3e} m/s²")

    # ------------------------------------------------------------------
    # Tabel comparativ
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("COMPARATIE MODELE")
    print("=" * 70)
    print(f"{'Model':40s}  {'chi2/N':>8s}  {'AIC':>12s}  {'k_par':>5s}")
    print("-" * 70)
    for name, chi2_v, k_par in [
        ("M0 Null",                         chi2_null, 0),
        ("M7a T1=S1*sqrt(g_bar*a0)",        chi2_m7a,  1),
        ("M7b T2=S2*g_bar/sqrt(1+g/a0)",    chi2_m7b,  1),
        ("M7 Dual (T1+T2)",                 chi2_m7,   2),
        ("M7+ MOND-QNG (k*S1*sqrt(g*g†))", chi2_mq,   2),
        ("M1 MOND RAR",                     chi2_mond,  1),
    ]:
        aic = chi2_v + 2 * k_par
        marker = " <-- MOND" if name.startswith("M1") else ""
        print(f"  {name:38s}  {chi2_v/n:8.3f}  {aic:12.1f}  {k_par:5d}{marker}")
    print()

    # ------------------------------------------------------------------
    # Analiza RAR per bin de g_bar
    # ------------------------------------------------------------------
    print("Relatia de Acceleratie Radiala (RAR) — model vs date vs MOND:")
    print(f"  {'g_bar/a0':>10s}  {'n':>5s}  {'g_obs/g_bar':>12s}  {'M7/g_bar':>12s}  {'MOND/g_bar':>12s}")
    rar = compute_rar_bins(all_pts, k1_f, k2_f, n_bins=10)
    for row in rar:
        chi_r   = row["g_bar"] / A0_INT
        ratio_d = row["g_obs_data"] / max(row["g_bar"], 1e-9)
        ratio_m = row["g_obs_m7"]   / max(row["g_bar"], 1e-9)
        ratio_r = row["g_mond"]     / max(row["g_bar"], 1e-9)
        print(f"  {chi_r:10.3f}  {row['n']:5d}  {ratio_d:12.3f}  {ratio_m:12.3f}  {ratio_r:12.3f}")
    print()

    # ------------------------------------------------------------------
    # Diagnostice per galaxie
    # ------------------------------------------------------------------
    print("Top 10 galaxii cu cel mai mare beneficiu M7 vs Null:")
    gal_stats = []
    for gid, pts in gals.items():
        chi2_n = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in pts)
        chi2_m = sum(((p["v"] - v_model_m7(p, k1_f, k2_f)) / p["ve"])**2 for p in pts)
        chi2_o = sum(((p["v"] - v_mond(p, g_dag_fit)) / p["ve"])**2 for p in pts)
        nm     = len(pts)
        if nm > 0:
            gal_stats.append({
                "gid": gid, "n": nm,
                "chi2_null": chi2_n / nm,
                "chi2_m7":   chi2_m / nm,
                "chi2_mond": chi2_o / nm,
                "delta": chi2_n - chi2_m,
            })
    gal_stats.sort(key=lambda x: -x["delta"])
    print(f"  {'Galaxy':12s}  {'n':>4s}  {'Null':>7s}  {'M7':>7s}  {'MOND':>7s}  {'Δ':>8s}")
    for gs in gal_stats[:10]:
        better = ">" if gs["chi2_m7"] < gs["chi2_mond"] else " "
        print(f"  {gs['gid']:12s}  {gs['n']:4d}  {gs['chi2_null']:7.2f}  "
              f"{gs['chi2_m7']:7.2f}  {gs['chi2_mond']:7.2f}{better}  {gs['delta']:8.1f}")
    print()

    # Galaxii unde M7 bate MOND
    m7_beats_mond = [gs for gs in gal_stats if gs["chi2_m7"] < gs["chi2_mond"]]
    print(f"  Galaxii unde M7 bate MOND: {len(m7_beats_mond)}/{len(gal_stats)}")
    if m7_beats_mond:
        print(f"  Ex: {[g['gid'] for g in m7_beats_mond[:5]]}")
    print()

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    print("=" * 70)
    print("VERDICT D6")
    print("=" * 70)

    imp_null = (chi2_null - chi2_m7) / chi2_null * 100
    imp_mond = (chi2_mond - chi2_m7) / chi2_mond * 100  # negativ = mai rau
    delta_mond = chi2_m7 - chi2_mond
    beats_mond = chi2_m7 < chi2_mond

    print(f"M7 vs Null:  Δchi2={chi2_null-chi2_m7:+.0f}  ({imp_null:+.1f}%)")
    print(f"M7 vs MOND:  Δchi2={delta_mond:+.0f}  (factor={chi2_m7/chi2_mond:.2f}×)")
    print(f"M7+ vs MOND: Δchi2={chi2_mq-chi2_mond:+.0f}  (factor={chi2_mq/chi2_mond:.2f}×)")
    print()

    if beats_mond:
        status     = "BONUS: M7 bate MOND complet!"
        conclusion = "m7_beats_mond"
    elif imp_null >= 30.0 and chi2_m7 / chi2_mond < 1.5:
        status     = f"PASS+: M7 > 30% vs Null si la {chi2_m7/chi2_mond:.1f}× de MOND."
        conclusion = "pass_plus"
    elif imp_null >= 30.0:
        status     = f"PASS: M7 > 30% vs Null. ({chi2_m7/chi2_mond:.1f}× mai rau ca MOND)"
        conclusion = "pass"
    elif imp_null >= 20.0:
        status     = f"PARTIAL: M7 > 20% vs Null. ({chi2_m7/chi2_mond:.1f}× mai rau ca MOND)"
        conclusion = "partial"
    else:
        status     = "FAIL: sub 20% imbunatatire."
        conclusion = "fail"

    print(status)
    print()

    # Interpretare T1 vs T2
    print("Contributii individuale:")
    print(f"  T1 (energetic S1*sqrt(g*a0)): chi2/N={chi2_m7a/n:.3f}  k1={k1_a:.5f}")
    print(f"  T2 (structural g/sqrt(1+g/a0)): chi2/N={chi2_m7b/n:.3f}  k2={k2_b:.5f}")
    print(f"  Dual:                           chi2/N={chi2_m7/n:.3f}  k1={k1_f:.5f}, k2={k2_f:.5f}")
    if k1_f < 1e-4:
        print("  -> T1 nu contribuie (k1≈0) — S1 nu e localizata suficient")
    if k2_f < 1e-4:
        print("  -> T2 nu contribuie (k2≈0)")
    if k1_f > 1e-4 and k2_f > 1e-4:
        print("  -> Ambii termeni contribuie — dualitate confirmata")
    print()

    # Straton lag derivare
    print("Straton lag → a0 (sugestia Grok):")
    print(f"  a0 utilizat = {A0_SI:.3e} m/s²")
    print(f"  δE0/E0 = 0.426% (din raportul straton lag)")
    delta_e = 0.00426
    # Daca a0 = delta_e * c^2 / r_galaxy cu r_galaxy ~ 10 kpc:
    r_gal_kpc = 10.0
    r_gal_m   = r_gal_kpc * KPC_TO_M
    a_straton = delta_e * (3e8)**2 / r_gal_m
    print(f"  Daca r_galaxy=10kpc: a_straton=δE0/E0*c²/r = {a_straton:.3e} m/s²")
    r_needed  = delta_e * (3e8)**2 / A0_SI
    print(f"  r_char pt a_straton=a0: {r_needed/KPC_TO_M:.1f} kpc")
    print(f"  → r_char ≈ {r_needed/KPC_TO_M:.0f} kpc ≈ scala Hubble? Nu e o scala galacticii.")
    print(f"  → Alt canal dimensional-consistent: a0 = δ × H0 × c, cu δ=0.07, H0=70 km/s/Mpc")
    H0 = 70.0 * 1e3 / (3.086e22)  # s^-1
    a0_cosmo = 0.07 * H0 * 3e8
    print(f"    a0_cosmo = 0.07 * H0 * c = {a0_cosmo:.3e} m/s² (vs MOND {A0_SI:.3e})")
    print()

    # ------------------------------------------------------------------
    # Salveaza artifacts
    # ------------------------------------------------------------------
    rar_data = [
        {"g_bar_over_a0": r["g_bar"]/A0_INT,
         "g_obs_data": r["g_obs_data"],
         "g_obs_m7": r["g_obs_m7"],
         "g_mond": r["g_mond"],
         "n": r["n"]} for r in rar]

    summary = {
        "test_id": "d6-qng-effective-law-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "model": {
            "T1": "k1 * S1(r) * sqrt(g_bar(r) * a0)  [energetic, S1=exp(-|chi-1|/0.28)]",
            "T2": "k2 * S2 * g_bar(r) / sqrt(1+g_bar/a0)  [structural, S2=0.355]",
            "v_pred": "sqrt(bt + r*(k1*T1 + k2*T2))",
        },
        "a0_si": A0_SI, "S2": S2_CONST, "sigma_chi": SIGMA_CHI,
        "n_points": n, "n_galaxies": n_gal,
        "best_params": {"k1": k1_f, "k2": k2_f},
        "results": {
            "M0_null":  {"chi2_per_n": chi2_null/n},
            "M7a_T1":   {"chi2_per_n": chi2_m7a/n, "k1": k1_a},
            "M7b_T2":   {"chi2_per_n": chi2_m7b/n, "k2": k2_b},
            "M7_dual":  {"chi2_per_n": chi2_m7/n,  "k1": k1_f, "k2": k2_f},
            "M7plus":   {"chi2_per_n": chi2_mq/n,  "k": k_mq,
                         "g_dag_si": gd_mq*G_UNIT},
            "M1_MOND":  {"chi2_per_n": chi2_mond/n, "g_dag_si": g_dag_fit*G_UNIT},
        },
        "conclusion": conclusion,
        "improve_vs_null_pct": imp_null,
        "factor_vs_mond": chi2_m7 / chi2_mond,
        "galaxies_m7_beats_mond": len(m7_beats_mond),
        "total_galaxies": len(gal_stats),
        "rar_bins": rar_data,
        "straton_lag": {
            "delta_e0_e0": delta_e,
            "a0_cosmo_formula": "delta * H0 * c",
            "a0_cosmo_si": a0_cosmo,
            "a0_mond_si": A0_SI,
            "ratio": a0_cosmo / A0_SI,
        }
    }
    (OUT_DIR / "d6_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
