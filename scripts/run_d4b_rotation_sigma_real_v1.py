#!/usr/bin/env python3
"""
D4b Rotation — Sigma_chi REAL pe curbe de rotatie

Foloseste formula exacta a modulului energetic (S1) din teoria QNG:
  Sigma_chi(r) = exp(-|chi(r) - 1| / lambda_chi)
  lambda_chi = 0.28  (din core-closure-v1 si cod vol-rules)
  chi_ref = 1.0 (normalizat)

chi(r) ∝ densitate(r) ∝ dM(r)/dr — calculat numeric din baryon_term

Forta QNG din gradient:
  a_QNG(r) = tau * |d Sigma_chi / dr|

Concluzii pre-declarate din analiza duala (stability-dual-attributes-v1):
  - S2 (structural) e aproximativ constant (100% pass) → ∇S2 ≈ 0
  - S1 (energetic) variaza → toata actiunea e in ∇Sigma_chi
  - Sigma_chi are maxim la chi = 1 (inel de stabilitate la raza unde chi ≈ chi_ref)

Modele testate:
  M0: Null — v = sqrt(baryon_term)
  M1: MOND (RAR)   — g_obs = g_bar/(1-exp(-sqrt(g_bar/g†)))   [1 param]
  M4: QNG S1 real  — a_extra = tau * |d Sigma_chi / dr|        [2 params: tau, chi_norm]

chi_norm = parametru de scalare chi(r) = M_enc(r) / (M_gal * chi_norm)
M_enc(r) = integral al densitatii (calculat din baryon_term)

Tinta: daca QNG S1 real bate MOND → remarcabil.
       Daca nu → gradient S1 nu e mecanismul dark matter in QNG.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "d4b-rotation-sigma-real-v1"

LAMBDA_CHI = 0.28   # din core-closure-v1: exp(-|chi-1|/0.28)
CHI_REF = 1.0       # normalizat

KM_TO_M = 1e3
KPC_TO_M = 3.0857e19
G_UNIT = KM_TO_M**2 / KPC_TO_M   # conversie km²/s²/kpc → m/s²
A0_SI = 1.2e-10     # m/s², MOND
A0_INT = A0_SI / G_UNIT  # km²/s²/kpc


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
                {"gal": row["system_id"], "r": r, "v": v, "ve": ve,
                 "bt": bt, "g_bar": bt / r})
    # Sorteaza per raza in fiecare galaxie
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


# ---------------------------------------------------------------------------
# Calcul chi(r) din masa barionica inchisa
# ---------------------------------------------------------------------------

def compute_chi_profile(pts: list[dict], chi_norm: float) -> list[float]:
    """
    chi(r) = M_enc(r) / (M_total * chi_norm)
    M_enc(r) ≈ ∑_{j<i} baryon_term_j (aproximare simplificata)

    In realitate M_enc(r) = G * M(<r) / r², dar nu avem G*M individual —
    avem v_baryon² = baryon_term = G*M(<r)/r, deci:
      G*M(<r) = baryon_term * r   [km²/s²/kpc * kpc = km²/s²]

    Deci M_enc(r) ∝ baryon_term(r) * r   (masa inchisa)
    chi(r) = (baryon_term(r) * r) / (baryon_term_max * r_max * chi_norm)
    """
    if not pts:
        return []
    # M_enc(r) ∝ baryon_term * r (masa inchisa estimata)
    m_enc = [p["bt"] * p["r"] for p in pts]
    m_max = max(m_enc) if m_enc else 1.0
    if m_max <= 0:
        m_max = 1.0
    # chi(r) normalizat: 1.0 la raza cu masa maxima inchisa
    return [me / (m_max * chi_norm) for me in m_enc]


def sigma_chi_fn(chi: float) -> float:
    """Sigma_chi = exp(-|chi - 1| / 0.28)"""
    return math.exp(-abs(chi - CHI_REF) / LAMBDA_CHI)


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


def compute_qng_s1_galaxy(pts: list[dict], tau: float, chi_norm: float
                           ) -> list[float]:
    """
    Calculeaza v_QNG per galaxie cu formula Sigma_chi reala.
    a_extra = tau * |d Sigma_chi / dr|
    """
    chi_vals = compute_chi_profile(pts, chi_norm)
    sigma_vals = [sigma_chi_fn(c) for c in chi_vals]

    v_preds = []
    for i, pt in enumerate(pts):
        # Deriva numerica a Sigma_chi
        if len(pts) == 1:
            dS_dr = 0.0
        elif i == 0:
            dS_dr = abs((sigma_vals[1] - sigma_vals[0]) /
                        max(pts[1]["r"] - pts[0]["r"], 1e-9))
        elif i == len(pts) - 1:
            dS_dr = abs((sigma_vals[-1] - sigma_vals[-2]) /
                        max(pts[-1]["r"] - pts[-2]["r"], 1e-9))
        else:
            dS_dr = abs((sigma_vals[i+1] - sigma_vals[i-1]) /
                        max(pts[i+1]["r"] - pts[i-1]["r"], 1e-9))

        g_obs = pt["g_bar"] + tau * dS_dr
        v_preds.append(math.sqrt(max(g_obs * pt["r"], 0.0)))

    return v_preds


# ---------------------------------------------------------------------------
# Fit utilities
# ---------------------------------------------------------------------------

def golden_search(f, lo: float, hi: float,
                  tol: float = 1e-5, max_iter: int = 200) -> tuple[float, float]:
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


def grid_search_2d(f, lo1, hi1, lo2, hi2, n=20) -> tuple[float, float, float]:
    """Grid search grossier pentru 2 parametri."""
    best_p1, best_p2, best_f = lo1, lo2, float("inf")
    for i in range(n):
        p1 = lo1 + (hi1 - lo1) * i / (n - 1)
        for j in range(n):
            p2 = lo2 + (hi2 - lo2) * j / (n - 1)
            val = f(p1, p2)
            if val < best_f:
                best_f, best_p1, best_p2 = val, p1, p2
    return best_p1, best_p2, best_f


def refine_2d(f, p1, p2, scale1=0.5, scale2=0.5, n=15) -> tuple[float, float, float]:
    """Refinare locala 2D."""
    return grid_search_2d(f,
        max(0, p1 - scale1), p1 + scale1,
        max(1e-4, p2 - scale2), p2 + scale2,
        n)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def chi2_mond_fn(g_dag: float, all_pts: list[dict]) -> float:
    return sum(((p["v"] - v_mond(p, g_dag)) / p["ve"])**2 for p in all_pts)


def chi2_qng_s1_fn(tau: float, chi_norm: float,
                   gals: dict[str, list[dict]]) -> float:
    total = 0.0
    for pts in gals.values():
        vpreds = compute_qng_s1_galaxy(pts, tau, chi_norm)
        for pt, vp in zip(pts, vpreds):
            total += ((pt["v"] - vp) / pt["ve"])**2
    return total


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D4b Rotation — Sigma_chi REAL (Stability S1 Energetic Channel)")
    print(f"lambda_chi = {LAMBDA_CHI}, chi_ref = {CHI_REF}")
    print(f"MOND a0 = {A0_INT:.1f} km²/s²/kpc")
    print()

    gals = load_galaxies(DATA_CSV)
    all_pts = [p for pts in gals.values() for p in pts]
    n = len(all_pts)
    n_gal = len(gals)
    print(f"Date: {n} puncte din {n_gal} galaxii")
    print()

    # ------------------------------------------------------------------
    # M0: Null
    # ------------------------------------------------------------------
    chi2_null = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in all_pts)
    print(f"M0 Null:          chi2/N = {chi2_null/n:.2f}  chi2 = {chi2_null:.0f}")

    # ------------------------------------------------------------------
    # M1: MOND
    # ------------------------------------------------------------------
    g_dag_fit, chi2_mond = golden_search(
        lambda g: chi2_mond_fn(g, all_pts),
        0.001 * A0_INT, 100.0 * A0_INT)
    g_dag_si = g_dag_fit * G_UNIT
    print(f"M1 MOND (RAR):    chi2/N = {chi2_mond/n:.2f}  chi2 = {chi2_mond:.0f}  g† = {g_dag_si:.2e} m/s²")

    # ------------------------------------------------------------------
    # M4: QNG S1 real — fit tau si chi_norm
    # ------------------------------------------------------------------
    print()
    print("M4 QNG S1 real: grid search (tau, chi_norm)... ", end="", flush=True)

    # tau: amplitudinea fortei [km²/s²/kpc / (1/kpc)] = [km²/s²]
    # Estimare: a_extra ≈ tau * dSigma/dr ~ tau * 1/LAMBDA_CHI / r_typ
    # Dorim a_extra ~ g_bar ~ 1000 km²/s²/kpc, r_typ ~ 5 kpc, dSigma/dr ~ 1/(0.28*5)
    # tau ~ 1000 * 0.28 * 5 = 1400 km²/s²
    # Cauta tau in [0, 50000]

    # chi_norm: scala de normalizare a lui chi
    # chi(r) = M_enc(r) / (M_max * chi_norm)
    # La chi_norm = 1: chi_max = 1 (maximul e exact la chi_ref = 1)
    # La chi_norm > 1: toate valorile chi < 1 → Sigma_chi ≈ exp(-(1-chi)/0.28)
    # La chi_norm < 1: unele valori chi > 1 → inelul de stabilitate e in interior
    # Cauta chi_norm in [0.1, 5.0]

    p1_best, p2_best, chi2_qng_coarse = grid_search_2d(
        lambda tau, cn: chi2_qng_s1_fn(tau, cn, gals),
        0.0, 50000.0, 0.1, 5.0, n=20)

    print(f"coarse: tau={p1_best:.0f}, chi_norm={p2_best:.3f}, chi2/N={chi2_qng_coarse/n:.2f}")
    print("  refinare... ", end="", flush=True)

    p1_ref, p2_ref, chi2_qng_refined = refine_2d(
        lambda tau, cn: chi2_qng_s1_fn(tau, cn, gals),
        p1_best, p2_best,
        scale1=min(p1_best * 0.8, 10000), scale2=min(p2_best * 0.8, 2.0),
        n=20)

    # O runda in plus de rafinare
    p1_f, p2_f, chi2_qng_fit = refine_2d(
        lambda tau, cn: chi2_qng_s1_fn(tau, cn, gals),
        p1_ref, p2_ref,
        scale1=min(p1_ref * 0.3, 3000), scale2=min(p2_ref * 0.3, 0.5),
        n=25)

    print("done")
    print(f"M4 QNG S1 real:   chi2/N = {chi2_qng_fit/n:.2f}  chi2 = {chi2_qng_fit:.0f}  tau = {p1_f:.1f} km²/s²  chi_norm = {p2_f:.4f}")

    # ------------------------------------------------------------------
    # Tabel comparativ
    # ------------------------------------------------------------------
    print()
    print("=" * 65)
    print("COMPARATIE MODELE")
    print("=" * 65)
    print(f"{'Model':30s}  {'chi2/N':>8s}  {'chi2':>12s}  {'k':>3s}")
    print("-" * 65)
    for name, chi2_v, k in [
        ("M0 Null (Newtonian)",      chi2_null,       0),
        ("M1 MOND (RAR)",            chi2_mond,       1),
        ("M4 QNG S1 Sigma_chi real", chi2_qng_fit,    2),
    ]:
        print(f"  {name:28s}  {chi2_v/n:8.2f}  {chi2_v:12.1f}  {k:3d}")

    print()

    # ------------------------------------------------------------------
    # Analiza structurii Sigma_chi per galaxie reprezentativa
    # ------------------------------------------------------------------
    print("Structura Sigma_chi(r) in galaxii reprezentative:")
    sample_gals = ["DDO154", "NGC6503", "NGC3198", "NGC2403", "UGC02953"]
    for gid in sample_gals:
        if gid not in gals:
            continue
        pts = gals[gid]
        chi_vals = compute_chi_profile(pts, p2_f)
        sigma_vals = [sigma_chi_fn(c) for c in chi_vals]
        idx_max = sigma_vals.index(max(sigma_vals))
        r_max_sigma = pts[idx_max]["r"]
        r_outer = pts[-1]["r"]
        sigma_outer = sigma_vals[-1]
        sigma_max = max(sigma_vals)
        print(f"  {gid:12s}: r_max_Sigma = {r_max_sigma:.1f} kpc  sigma_max = {sigma_max:.3f}  sigma_outer = {sigma_outer:.3f}")

    print()

    # ------------------------------------------------------------------
    # Verdict
    # ------------------------------------------------------------------
    print("=" * 65)
    print("VERDICT")
    print("=" * 65)

    mond_wins = chi2_mond < chi2_qng_fit
    delta = chi2_qng_fit - chi2_mond
    aic_mond = chi2_mond + 2
    aic_qng  = chi2_qng_fit + 4  # 2 params

    print(f"MOND: chi2/N = {chi2_mond/n:.2f}")
    print(f"QNG S1 real: chi2/N = {chi2_qng_fit/n:.2f}")
    print(f"Δchi2 (QNG - MOND) = {delta:+.0f}")
    print(f"ΔAIC  (QNG - MOND) = {(aic_qng - aic_mond):+.0f}  (penalizeaza QNG pentru 1 param extra)")
    print()

    if mond_wins:
        print("CONCLUZIE: MOND bate QNG S1 gradient.")
        print()
        print("De ce? Sigma_chi(r) = exp(-|chi(r)-1|/0.28)")
        print("  → La r mare: chi(r) → 0 → Sigma_chi → exp(-1/0.28) ≈ 0.027 (CONSTANTA)")
        print("  → La r mic: chi(r) → 1 → Sigma_chi → 1 (maxim, CONSTANTA la centru)")
        print("  → Gradientul Sigma_chi ≠ 0 doar intr-o zona intermediara ingusta")
        print("  → Nu poate produce forta plata pe intreaga curba de rotatie")
        print()
        print("IMPLICATIE PENTRU TEORIA QNG:")
        print("  Mecanismul dark matter in QNG NU este gradientul canalului S1.")
        print("  Canalul S1 produce un inel de stabilitate, nu o forta distribuita.")
        print("  Mecanismul dark matter trebuie sa fie:")
        print("  (a) Memoria acumulata (history_term) — necesita kernel explicit")
        print("  (b) Un camp cu o alta dependenta de r (ex. chi^2 sau log-chi)")
        print("  (c) Efectul colectiv S1 × S2 intr-un mod non-gradient")
    else:
        print("CONCLUZIE: QNG S1 real BATE MOND.")
        print("Aceasta ar fi o descoperire remarcabila — necesita verificare.")

    # ------------------------------------------------------------------
    # Salveaza artifacts
    # ------------------------------------------------------------------
    summary = {
        "test_id": "d4b-rotation-sigma-real-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "theory_params": {"lambda_chi": LAMBDA_CHI, "chi_ref": CHI_REF},
        "n_points": n, "n_galaxies": n_gal,
        "models": {
            "M0_null":     {"chi2": chi2_null,    "chi2_per_n": chi2_null/n,    "k": 0},
            "M1_MOND":     {"chi2": chi2_mond,    "chi2_per_n": chi2_mond/n,    "k": 1,
                            "g_dag_m_s2": g_dag_si},
            "M4_QNG_S1":   {"chi2": chi2_qng_fit, "chi2_per_n": chi2_qng_fit/n, "k": 2,
                            "tau_km2_s2": p1_f, "chi_norm": p2_f},
        },
        "mond_wins": mond_wins,
        "delta_chi2_qng_minus_mond": delta,
    }
    (OUT_DIR / "d4b_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print()
    print(f"Artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
