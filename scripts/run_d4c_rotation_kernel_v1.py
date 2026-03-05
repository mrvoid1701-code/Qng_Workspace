#!/usr/bin/env python3
"""
D4c Rotation — Kernel exponential spatial pe date reale SPARC (DS-006)

Implementeaza recomandarea kernel cumulativ (Grok):
  history_term(r_i) = sum_j exp(-|r_i - r_j| / tau) * baryon_term(r_j) * dr_j

Model:
  v_pred(r)^2 = baryon_term(r) + k * history_term(r)

Avantaje vs D4a/D4b:
  - Nu foloseste history_term din CSV (care e circular cu v_obs)
  - Kernelul exponential e analitic, non-circular: tau si k sunt liberi
  - baryon_term(r) = v_baryon^2 = GM_baryon/r (independent de v_obs)
  - Fizica: memoria gravitationala acumulata la raza r din toate razele interioare
    ponderate exponential cu distanta |r-r'|

Modele comparate:
  M0: Null   — v = sqrt(baryon_term)
  M1: MOND   — g_obs = g_bar / (1 - exp(-sqrt(g_bar/g†)))    [1 param]
  M5: QNG-K  — v^2 = baryon_term + k * H_tau(r)              [2 params: tau, k]
               H_tau(r) = sum_j exp(-|r-r_j|/tau) * baryon_term(r_j) * dr_j

Test pre-declarat:
  PASS daca chi2/N (QNG-K) < chi2/N (M0) cu delta > 10%
  BONUS daca chi2/N (QNG-K) < chi2/N (MOND)
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV  = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
OUT_DIR   = ROOT / "05_validation" / "evidence" / "artifacts" / "d4c-rotation-kernel-v1"

KM_TO_M   = 1e3
KPC_TO_M  = 3.0857e19
G_UNIT    = KM_TO_M**2 / KPC_TO_M   # km²/s²/kpc → m/s²
A0_SI     = 1.2e-10                  # m/s²
A0_INT    = A0_SI / G_UNIT           # km²/s²/kpc


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def load_galaxies(path: Path) -> dict[str, list[dict]]:
    gals: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bt = float(row["baryon_term"])
            r  = float(row["radius"])
            v  = float(row["v_obs"])
            ve = float(row["v_err"])
            if r <= 0 or ve <= 0 or bt < 0:
                continue
            gals.setdefault(row["system_id"], []).append(
                {"r": r, "v": v, "ve": ve, "bt": bt, "g_bar": bt / r})
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


# ---------------------------------------------------------------------------
# Kernel history term
# ---------------------------------------------------------------------------

def compute_history_term(pts: list[dict], tau: float) -> list[float]:
    """
    H_tau(r_i) = (1/tau) * sum_j exp(-|r_i - r_j| / tau) * baryon_term(r_j) * dr_j

    Normalizare (1/tau): face H_tau sa aiba unitati [km^2/s^2] identice cu bt.
    Limita tau→0: H_tau(r_i) → bt(r_i)  (kernel delta → scaling unitar)
    Limita tau→∞: H_tau(r_i) → mean(bt) * L / tau → 0
    Limita fizica interesanta: tau ~ scala galacticii (1-30 kpc)

    De ce e non-circular:
      - baryon_term(r_j) = v_baryon^2 = GM_baryon/r derivat din masa stele+gaz
      - tau e parametru liber, nu ajustat per galaxie
      - suma e o predictie, nu v_obs
    """
    n = len(pts)
    if n == 0:
        return []

    # Calcul dr_j (largimea intervalului de integrare per punct)
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

    tau_eff = max(tau, 1e-9)
    hist = []
    for i in range(n):
        ri = pts[i]["r"]
        h = 0.0
        for j in range(n):
            rj = pts[j]["r"]
            w = math.exp(-abs(ri - rj) / tau_eff)
            h += w * pts[j]["bt"] * dr[j]
        hist.append(h / tau_eff)   # normalizare 1/tau
    return hist


# ---------------------------------------------------------------------------
# Modele
# ---------------------------------------------------------------------------

def v_null(pt: dict) -> float:
    return math.sqrt(max(pt["bt"], 0.0))


def v_mond(pt: dict, g_dag: float) -> float:
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = (g_bar / denom) if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


def v_qng_kernel(pt: dict, h: float, k: float) -> float:
    """v^2 = baryon_term + k * H_tau(r)"""
    return math.sqrt(max(pt["bt"] + k * h, 0.0))


# ---------------------------------------------------------------------------
# Fit utilities
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


def grid_2d(f, lo1, hi1, lo2, hi2, n=25) -> tuple[float, float, float]:
    bp1, bp2, bf = lo1, lo2, float("inf")
    step1 = (hi1 - lo1) / max(n - 1, 1)
    step2 = (hi2 - lo2) / max(n - 1, 1)
    for i in range(n):
        p1 = lo1 + i * step1
        for j in range(n):
            p2 = lo2 + j * step2
            val = f(p1, p2)
            if val < bf:
                bf, bp1, bp2 = val, p1, p2
    return bp1, bp2, bf


def refine_2d(f, p1, p2, s1, s2, n=20) -> tuple[float, float, float]:
    return grid_2d(f,
        max(0.0, p1 - s1), p1 + s1,
        max(0.0, p2 - s2), p2 + s2, n)


# ---------------------------------------------------------------------------
# Chi2 functions
# ---------------------------------------------------------------------------

def chi2_mond_global(g_dag: float, all_pts: list[dict]) -> float:
    return sum(((p["v"] - v_mond(p, g_dag)) / p["ve"])**2 for p in all_pts)


def chi2_kernel_global(tau: float, k: float,
                       gals: dict[str, list[dict]]) -> float:
    total = 0.0
    for pts in gals.values():
        hist = compute_history_term(pts, tau)
        for pt, h in zip(pts, hist):
            total += ((pt["v"] - v_qng_kernel(pt, h, k)) / pt["ve"])**2
    return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D4c Rotation — Kernel exponential spatial (H_tau)")
    print(f"Date: {DATA_CSV.name}")
    print()

    gals     = load_galaxies(DATA_CSV)
    all_pts  = [p for pts in gals.values() for p in pts]
    n        = len(all_pts)
    n_gal    = len(gals)
    print(f"  {n} puncte, {n_gal} galaxii")
    print()

    # ------------------------------------------------------------------
    # M0: Null
    # ------------------------------------------------------------------
    chi2_null = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in all_pts)
    print(f"M0 Null:     chi2/N = {chi2_null/n:.2f}")

    # ------------------------------------------------------------------
    # M1: MOND (referinta principala)
    # ------------------------------------------------------------------
    g_dag_fit, chi2_mond = golden_search(
        lambda g: chi2_mond_global(g, all_pts),
        0.001 * A0_INT, 100.0 * A0_INT)
    print(f"M1 MOND RAR: chi2/N = {chi2_mond/n:.2f}  g† = {g_dag_fit * G_UNIT:.2e} m/s²")

    # ------------------------------------------------------------------
    # M5: QNG Kernel — grid search 2D (tau, k)
    # ------------------------------------------------------------------
    # tau: scala spatiala in kpc
    #   - prea mic (tau<<1 kpc): kernelul e local → ≈ baryon_term * factor → ~M0
    #   - prea mare (tau>>100 kpc): kernelul integreaza tot → constanta × k → decalaj uniform
    #   - optim asteptat: tau ~ r_half ~ 2-20 kpc
    #
    # k: amplitudinea memoriei
    #   - H_tau are unitati [km^2/s^2] similar cu baryon_term
    #   - k ~ 0.1-10 (fara unitati)

    print()
    # Scan tau la valori fizice (1-50 kpc) — per fiecare tau, fit k cu golden search
    print("M5 QNG Kernel: scan tau in [0.5, 60] kpc (fit k per tau)...")
    tau_scan = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 30.0, 50.0, 60.0]
    scan_results = []
    for tau_s in tau_scan:
        # Pre-calculeaza H_tau per galaxie (costisitor per tau)
        hcache: dict[str, list[float]] = {}
        for gid, pts in gals.items():
            hcache[gid] = compute_history_term(pts, tau_s)

        def chi2_k_only(k: float) -> float:
            total = 0.0
            for gid, pts in gals.items():
                for pt, h in zip(pts, hcache[gid]):
                    total += ((pt["v"] - v_qng_kernel(pt, h, k)) / pt["ve"])**2
            return total

        k_opt, chi2_s = golden_search(chi2_k_only, 0.0, 20.0, tol=1e-4)
        scan_results.append((tau_s, k_opt, chi2_s))
        print(f"  tau={tau_s:5.1f} kpc  k={k_opt:.4f}  chi2/N={chi2_s/n:.2f}")

    best_scan = min(scan_results, key=lambda x: x[2])
    tau_best_scan, k_best_scan, chi2_best_scan = best_scan
    print(f"  -> Minim scan: tau={tau_best_scan:.1f} kpc, k={k_best_scan:.4f}, chi2/N={chi2_best_scan/n:.2f}")
    print()

    # Refinare 2D in jurul minimului scan
    print("  refinare 2D... ", end="", flush=True)
    tau_r1, k_r1, chi2_r1 = refine_2d(
        lambda tau, k: chi2_kernel_global(tau, k, gals),
        tau_best_scan, k_best_scan,
        min(tau_best_scan * 0.6, 10.0), min(k_best_scan * 0.6 + 0.3, 3.0), n=20)
    print(f"tau={tau_r1:.2f} kpc, k={k_r1:.4f}, chi2/N={chi2_r1/n:.2f}")

    print("  refinare finala... ", end="", flush=True)
    tau_f, k_f, chi2_kf = refine_2d(
        lambda tau, k: chi2_kernel_global(tau, k, gals),
        tau_r1, k_r1,
        min(tau_r1 * 0.3, 3.0), min(k_r1 * 0.3 + 0.1, 1.0), n=25)
    print(f"tau={tau_f:.3f} kpc, k={k_f:.5f}, chi2/N={chi2_kf/n:.2f}")
    print()

    # ------------------------------------------------------------------
    # Tabel comparativ
    # ------------------------------------------------------------------
    aic_null  = chi2_null + 2 * 0
    aic_mond  = chi2_mond + 2 * 1
    aic_kf    = chi2_kf   + 2 * 2

    print("=" * 70)
    print("COMPARATIE MODELE")
    print("=" * 70)
    print(f"{'Model':35s}  {'chi2/N':>8s}  {'AIC':>12s}  {'k':>3s}")
    print("-" * 70)
    for name, chi2_v, aic_v, k_par in [
        ("M0 Null (Newtonian baryonic)",  chi2_null, aic_null, 0),
        ("M1 MOND (RAR)",                 chi2_mond, aic_mond, 1),
        ("M5 QNG Kernel exp spatial",     chi2_kf,   aic_kf,   2),
    ]:
        print(f"  {name:33s}  {chi2_v/n:8.2f}  {aic_v:12.1f}  {k_par:3d}")
    print()

    # ------------------------------------------------------------------
    # Structura H_tau per galaxie reprezentativa
    # ------------------------------------------------------------------
    print("Structura H_tau(r) in galaxii reprezentative (tau_fit = {:.2f} kpc):".format(tau_f))
    samples = ["DDO154", "NGC6503", "NGC3198", "NGC2403", "UGC02953", "NGC7814"]
    for gid in samples:
        if gid not in gals:
            continue
        pts  = gals[gid]
        hist = compute_history_term(pts, tau_f)
        r_in  = pts[0]["r"]
        r_out = pts[-1]["r"]
        h_in  = hist[0]
        h_out = hist[-1]
        # Gradientul: creste sau scade spre exterior?
        gradient = "↑ creste" if h_out > h_in else "↓ scade"
        # Comparatie magnitudine H vs bt la ultima raza
        bt_out = pts[-1]["bt"]
        ratio  = k_f * h_out / max(bt_out, 1e-9)
        print(f"  {gid:12s}: r=[{r_in:.1f},{r_out:.1f}] kpc  "
              f"H_in={h_in:.1f}  H_out={h_out:.1f}  {gradient}  "
              f"k*H/bt_outer={ratio:.2f}")
    print()

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)

    improve_vs_null = (chi2_null - chi2_kf) / chi2_null * 100
    beats_mond      = chi2_kf < chi2_mond
    delta_mond      = chi2_kf - chi2_mond
    delta_aic       = aic_kf  - aic_mond

    print(f"QNG Kernel vs Null:  Δchi2 = {chi2_null-chi2_kf:+.0f}  ({improve_vs_null:+.1f}%)")
    print(f"QNG Kernel vs MOND:  Δchi2 = {delta_mond:+.0f}   ΔAIC = {delta_aic:+.1f}")
    print()

    if beats_mond:
        print("*** BONUS: QNG Kernel bate MOND! Necesita verificare independenta. ***")
        conclusion = "qng_kernel_beats_mond"
    elif improve_vs_null >= 10.0 and chi2_kf / n < chi2_null / n:
        print("PASS: QNG Kernel bate Null cu >10% — kernel spatial are efect real.")
        conclusion = "qng_kernel_beats_null"
    else:
        print("FAIL: QNG Kernel nu reduce chi2/N suficient fata de Null.")
        conclusion = "qng_kernel_fails"

    print()
    print(f"Tau optim:  {tau_f:.3f} kpc")
    print(f"k optim:    {k_f:.5f}")
    print()

    # Interpretare fizica
    if tau_f < 2.0:
        print(f"Tau = {tau_f:.2f} kpc — scala sub-kpc: memoria e locala, similara cu un factor de scalare.")
    elif tau_f < 10.0:
        print(f"Tau = {tau_f:.2f} kpc — scala kpc: compatibil cu raza scalei disc galactic (raza de semi-masa tipica).")
    elif tau_f < 30.0:
        print(f"Tau = {tau_f:.2f} kpc — scala 10-30 kpc: memoria integreaza interiorul galaxiei.")
    else:
        print(f"Tau = {tau_f:.2f} kpc — scala mare: kernelul integreaza toata galaxia → aproape constant → ~M0.")

    print()
    print("Structura matematica:")
    print("  H_tau(r) = sum_j exp(-|r-r_j|/tau) * bt(r_j) * dr_j")
    print("  La r mare (exterior): H_tau plateau → gradientul H ≈ 0 la r>>tau")
    print("  La r mic (interior):  H_tau mic (putine puncte in interior)")
    print("  Maxim H_tau: la raza de semi-masa (unde se concentreaza bt(r_j))")
    print()
    if conclude_kernel_flat(gals, tau_f, k_f):
        print("  Verificare curba plata: H_tau(r) produce contrib. relativ constanta la r>tau")
        print("  => k*H_tau/r ≈ constant (centrifugal) la periferie — compatible cu curba plata.")
    else:
        print("  H_tau scade la periferie => nu produce curba plata naturala.")

    # ------------------------------------------------------------------
    # Salveaza artifacts
    # ------------------------------------------------------------------
    summary = {
        "test_id": "d4c-rotation-kernel-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "kernel": "exponential_spatial",
        "kernel_formula": "H_tau(r_i) = sum_j exp(-|r_i-r_j|/tau) * bt(r_j) * dr_j",
        "n_points": n, "n_galaxies": n_gal,
        "models": {
            "M0_null":  {"chi2": chi2_null, "chi2_per_n": chi2_null/n, "k": 0},
            "M1_MOND":  {"chi2": chi2_mond, "chi2_per_n": chi2_mond/n, "k": 1,
                         "g_dag_m_s2": g_dag_fit * G_UNIT},
            "M5_QNG_K": {"chi2": chi2_kf,   "chi2_per_n": chi2_kf/n,  "k": 2,
                         "tau_kpc": tau_f, "k_coupling": k_f},
        },
        "conclusion": conclusion,
        "improve_vs_null_pct": improve_vs_null,
        "delta_chi2_vs_mond": delta_mond,
        "delta_aic_vs_mond": delta_aic,
    }
    (OUT_DIR / "d4c_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Artifacts: {OUT_DIR}")
    return 0


def conclude_kernel_flat(gals: dict[str, list[dict]], tau: float, k: float) -> bool:
    """Verifica daca k*H_tau(r)/r e aproximativ constant la periferie in >50% galaxii."""
    flat_count = 0
    total = 0
    for pts in gals.values():
        if len(pts) < 5:
            continue
        hist = compute_history_term(pts, tau)
        outer = pts[len(pts)//2:]
        outer_h = hist[len(pts)//2:]
        contribs = [k * h / max(p["r"], 1e-9) for p, h in zip(outer, outer_h)]
        if len(contribs) < 2:
            continue
        cv = (max(contribs) - min(contribs)) / max(sum(contribs)/len(contribs), 1e-9)
        if cv < 0.5:
            flat_count += 1
        total += 1
    return flat_count / max(total, 1) > 0.5


if __name__ == "__main__":
    sys.exit(main())
