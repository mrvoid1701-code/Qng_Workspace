#!/usr/bin/env python3
"""
D4 Rotation Real v1 — test discriminant pe curbe de rotatie reale

Foloseste DOAR baryon_term + radius ca input (NU history_term, care e circular).
Compara 4 modele:
  M0: Null/Newtonian  — v_pred = sqrt(baryon_term),                   0 params
  M1: MOND (RAR)      — g_obs = g_bar/(1-exp(-sqrt(g_bar/g†))),       1 param (g†)
  M2: Power-law RAR   — g_obs = g_bar * (g_ref/g_bar)^alpha,          2 params
  M3: QNG gradient    — a_extra = tau * d(g_bar)/dr,                   1 param (tau)

MOND este benchmark: deja validat empiric pe sute de galaxii (McGaugh 2016).
Daca QNG bate MOND → remarcabil. Daca MOND bate QNG → QNG are nevoie de
un mecanism suplimentar pentru curbe de rotatie.

Date: data/rotation/rotation_ds006_rotmod.csv
  - 175 galaxii, 3391 puncte
  - baryon_term [km²/s²] = v_baryon²
  - radius [kpc]
  - v_obs [km/s], v_err [km/s]

Unitati interne: km²/s²/kpc pentru acceleratii (g = v²/r)
  - 1 km²/s²/kpc = 3.241e-14 m/s²
  - MOND a0 ~ 1.2e-10 m/s² = 3703 km²/s²/kpc

Pre-registration: fisier de fata + commit timestamp.
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
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-rotation-real-v1"

# MOND a0 in km²/s²/kpc (literatura: 1.2e-10 m/s²)
A0_MOND_SI = 1.2e-10        # m/s²
KPC_TO_M = 3.0857e19        # m/kpc
KM_TO_M = 1e3               # m/km
# g [km²/s²/kpc] → [m/s²]: multiply by KM_TO_M² / KPC_TO_M
G_UNIT_FACTOR = KM_TO_M**2 / KPC_TO_M   # = 3.241e-14 m·kpc/(s²·km²)
A0_MOND_INTERNAL = A0_MOND_SI / G_UNIT_FACTOR   # km²/s²/kpc


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def load_data(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bt = float(row["baryon_term"])
            r = float(row["radius"])
            v = float(row["v_obs"])
            ve = float(row["v_err"])
            if r <= 0 or ve <= 0 or bt < 0:
                continue
            rows.append({
                "gal": row["system_id"],
                "r": r,          # kpc
                "v": v,          # km/s
                "ve": ve,        # km/s
                "bt": bt,        # km²/s²  (= v_baryon²)
                "g_bar": bt / r, # km²/s²/kpc
            })
    return rows


# ---------------------------------------------------------------------------
# Modele
# ---------------------------------------------------------------------------

def v_null(pt: dict) -> float:
    """M0: Newtonian — v = sqrt(baryon_term)"""
    return math.sqrt(max(pt["bt"], 0.0))


def v_mond(pt: dict, g_dag: float) -> float:
    """
    M1: MOND McGaugh 2016 RAR
    g_obs = g_bar / (1 - exp(-sqrt(g_bar/g†)))
    v_obs = sqrt(g_obs * r)
    """
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-12))
    denom = 1.0 - math.exp(-x)
    if denom < 1e-15:
        # Taylor: denom ≈ x, g_obs ≈ g_bar/x = sqrt(g_bar * g_dag)
        g_obs = math.sqrt(g_bar * g_dag)
    else:
        g_obs = g_bar / denom
    return math.sqrt(max(g_obs * pt["r"], 0.0))


def v_qng_gradient(pt: dict, tau: float, pts_in_gal: list[dict]) -> float:
    """
    M3: QNG gradient — a_extra = tau * |d(g_bar)/dr|
    g_obs = g_bar + tau * |dg_bar/dr|
    v_obs = sqrt(g_obs * r)
    Deriva numerica din punctele vecine in aceeasi galaxie.
    """
    g_bar = pt["g_bar"]
    r0 = pt["r"]

    # Deriv numerica: gaseste vecini in galaxie
    neighbors = sorted(pts_in_gal, key=lambda p: abs(p["r"] - r0))
    if len(neighbors) < 2:
        dg_dr = 0.0
    else:
        # Cel mai apropiat vecin diferit de punctul curent
        others = [p for p in neighbors if abs(p["r"] - r0) > 1e-9]
        if not others:
            dg_dr = 0.0
        else:
            nb = others[0]
            dg_dr = abs((nb["g_bar"] - g_bar) / (nb["r"] - r0))

    g_obs = g_bar + tau * dg_dr
    return math.sqrt(max(g_obs * pt["r"], 0.0))


# ---------------------------------------------------------------------------
# Chi2
# ---------------------------------------------------------------------------

def chi2_model(pts: list[dict], v_pred_fn) -> float:
    return sum(((pt["v"] - v_pred_fn(pt)) / pt["ve"])**2 for pt in pts)


# ---------------------------------------------------------------------------
# Fit 1-param cu sectiune aurie (golden section search)
# ---------------------------------------------------------------------------

def golden_search(f, lo, hi, tol=1e-6, max_iter=200) -> tuple[float, float]:
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def aic(chi2: float, k: int) -> float:
    return chi2 + 2.0 * k


def bic(chi2: float, k: int, n: int) -> float:
    return chi2 + k * math.log(max(n, 1))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D4 Rotation Real v1")
    print(f"Data: {DATA_CSV}")
    print(f"MOND a0 (internal) = {A0_MOND_INTERNAL:.1f} km²/s²/kpc")
    print()

    pts = load_data(DATA_CSV)
    n = len(pts)
    gals = {}
    for pt in pts:
        gals.setdefault(pt["gal"], []).append(pt)
    n_gal = len(gals)
    print(f"Loaded: {n} puncte din {n_gal} galaxii")
    print()

    # ------------------------------------------------------------------
    # M0: Null / Newtonian
    # ------------------------------------------------------------------
    chi2_null = chi2_model(pts, v_null)
    print(f"M0 Null (Newtonian):  chi2 = {chi2_null:.1f}  chi2/N = {chi2_null/n:.2f}")

    # ------------------------------------------------------------------
    # M1: MOND — fit g_dag global pe toate galaxiile
    # ------------------------------------------------------------------
    def chi2_mond(g_dag):
        return chi2_model(pts, lambda p: v_mond(p, g_dag))

    # Cauta in [0.01, 100] * A0_MOND_INTERNAL
    lo_m, hi_m = 0.01 * A0_MOND_INTERNAL, 100.0 * A0_MOND_INTERNAL
    g_dag_fit, chi2_mond_fit = golden_search(chi2_mond, lo_m, hi_m)
    g_dag_si = g_dag_fit * G_UNIT_FACTOR
    print(f"M1 MOND (RAR):        chi2 = {chi2_mond_fit:.1f}  chi2/N = {chi2_mond_fit/n:.2f}  g† = {g_dag_fit:.1f} km²/s²/kpc = {g_dag_si:.2e} m/s²  (literatura: 1.2e-10)")

    # ------------------------------------------------------------------
    # M3: QNG gradient — fit tau global
    # ------------------------------------------------------------------
    # Precalculeaza derivatele per galaxie
    gal_pts = {gal: sorted(pts_g, key=lambda p: p["r"]) for gal, pts_g in gals.items()}
    pts_with_gal = [(pt, gal_pts[pt["gal"]]) for pt in pts]

    def chi2_qng(tau):
        return sum(((pt["v"] - v_qng_gradient(pt, tau, gal_lst)) / pt["ve"])**2
                   for pt, gal_lst in pts_with_gal)

    # Tau pozitiv: cauta in [0, 10]
    # Tau e in unitati [kpc] deoarece a_extra = tau * dg/dr [km²/s²/kpc / kpc] = tau * km²/s²/kpc²
    # Dar g_obs = g_bar + a_extra [km²/s²/kpc], deci tau [kpc²]
    lo_q, hi_q = 0.0, 50.0
    tau_fit, chi2_qng_fit = golden_search(chi2_qng, lo_q, hi_q)
    print(f"M3 QNG gradient:      chi2 = {chi2_qng_fit:.1f}  chi2/N = {chi2_qng_fit/n:.2f}  tau = {tau_fit:.4f} kpc²")

    # ------------------------------------------------------------------
    # Rezultate comparative
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("COMPARATIE MODELE")
    print("=" * 70)
    print(f"{'Model':25s}  {'chi2':>10s}  {'chi2/N':>8s}  {'AIC':>10s}  {'BIC':>10s}  {'params':>6s}")
    print("-" * 70)
    models = [
        ("M0 Null (Newtonian)", chi2_null, 0),
        ("M1 MOND (RAR)",       chi2_mond_fit, 1),
        ("M3 QNG gradient",     chi2_qng_fit, 1),
    ]
    for name, chi2_v, k in models:
        print(f"  {name:23s}  {chi2_v:10.1f}  {chi2_v/n:8.2f}  {aic(chi2_v,k):10.1f}  {bic(chi2_v,k,n):10.1f}  {k:6d}")

    print()
    print("Interpretare chi2/N:")
    print("  chi2/N >> 1 → model slab, reziduuri mari")
    print("  chi2/N ≈ 1  → model bun, reziduuri de ordinul erorii de masurare")
    print()

    # Verdict
    best_chi2 = min(chi2_mond_fit, chi2_qng_fit)
    mond_wins = chi2_mond_fit <= chi2_qng_fit
    delta_mond_qng = chi2_qng_fit - chi2_mond_fit

    print("VERDICT:")
    if chi2_null / n > 5.0:
        print(f"  ✓ Null (Newtonian) ESUAZA sever: chi2/N = {chi2_null/n:.1f} >> 1")
        print(f"    → Exista semnal real de dark matter in date (asteptat)")
    if chi2_mond_fit / n < 3.0:
        print(f"  ✓ MOND fiteza rezonabil: chi2/N = {chi2_mond_fit/n:.2f}")
        print(f"    g† fit = {g_dag_si:.2e} m/s² (literatura: 1.20e-10)")
    if mond_wins:
        print(f"  ✗ QNG gradient PIERDE fata de MOND: Δchi2 = +{delta_mond_qng:.0f}")
        print(f"    → QNG gradient (prima derivata) nu reproduce fenomenologia dark matter")
    else:
        print(f"  ✓ QNG gradient BATE MOND: Δchi2 = {-delta_mond_qng:.0f}")

    print()
    print("CE IMPLICA ASTA PENTRU QNG:")
    print("  MOND este deja validat empiric cu acelasi numar de parametri.")
    if mond_wins:
        print("  QNG necesita o formula de cuplaj DIFERITA de prima derivata a acceleratiei")
        print("  barionice pentru a reproduce curbele de rotatie.")
        print("  Optiuni: (1) QNG → aceeasi RAR ca MOND (derivabil din teoria QNG?)")
        print("           (2) QNG → formula noua testabila diferita de MOND")

    # ------------------------------------------------------------------
    # Per-galaxie: reziduuri MOND vs QNG
    # ------------------------------------------------------------------
    per_gal = []
    for gal, gpts in gal_pts.items():
        c0 = sum(((p["v"] - v_null(p)) / p["ve"])**2 for p in gpts)
        c1 = sum(((p["v"] - v_mond(p, g_dag_fit)) / p["ve"])**2 for p in gpts)
        c3 = sum(((p["v"] - v_qng_gradient(p, tau_fit, gpts)) / p["ve"])**2 for p in gpts)
        per_gal.append({"gal": gal, "N": len(gpts),
                         "chi2_null": c0, "chi2_mond": c1, "chi2_qng": c3,
                         "mond_per_n": c1 / len(gpts), "qng_per_n": c3 / len(gpts)})

    per_gal.sort(key=lambda r: r["mond_per_n"])

    # Scrie CSV
    csv_path = OUT_DIR / "per_galaxy_chi2.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["gal","N","chi2_null","chi2_mond","chi2_qng",
                                           "mond_per_n","qng_per_n"])
        w.writeheader()
        for r in per_gal:
            w.writerow({k: (f"{v:.3f}" if isinstance(v,float) else v) for k,v in r.items()})

    # Summary JSON
    summary = {
        "test_id": "d4-rotation-real-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "n_points": n,
        "n_galaxies": n_gal,
        "models": {
            "M0_null":         {"chi2": chi2_null,      "chi2_per_n": chi2_null/n,      "k": 0},
            "M1_MOND":         {"chi2": chi2_mond_fit,  "chi2_per_n": chi2_mond_fit/n,  "k": 1,
                                "g_dag_km2_s2_kpc": g_dag_fit, "g_dag_m_s2": g_dag_si},
            "M3_QNG_gradient": {"chi2": chi2_qng_fit,  "chi2_per_n": chi2_qng_fit/n,   "k": 1,
                                "tau_kpc2": tau_fit},
        },
        "mond_wins_vs_qng": mond_wins,
        "delta_chi2_qng_minus_mond": delta_mond_qng,
        "verdict": "MOND bate QNG gradient" if mond_wins else "QNG gradient bate MOND",
    }
    (OUT_DIR / "d4_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print()
    print(f"Artifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
