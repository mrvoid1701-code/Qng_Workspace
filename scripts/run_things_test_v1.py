#!/usr/bin/env python3
"""
THINGS Test v1 — subset-check THINGS pe sub-eșantionul THINGS din ds006

Galaxii: 13 din cele 19 THINGS (de Blok et al. 2008, AJ 136 2648)
  prezente in ds006/SPARC: DDO154, IC2574, NGC2366, NGC2403, NGC2841,
  NGC2903, NGC2976, NGC3198, NGC3521, NGC5055, NGC6946, NGC7331, NGC7793

Scop: verificare de consistenta pe sub-setul THINGS disponibil in ds006.
  Nu este o validare complet independenta: foloseste acelasi pachet ds006 si lipsesc 6/19 galaxii THINGS.

Modele comparate:
  M0: Null (Newtonian)     — v = sqrt(bt),                        0 params
  M1: MOND RAR (McGaugh)   — g_obs = g_bar/(1-exp(-√χ)),          1 param (g†)
  M1s: MOND Simple         — g_obs = g_bar*(1 + 1/√χ),            1 param (g†)
  M1m: MOND Standard       — g_obs = g_bar*½(1+√(1+4/χ)),         1 param (g†)
  M8c: QNG straton         — g_obs = g_bar + k*√(g_bar·g†)*exp(-g_bar/g†), 2 params

Metodologie: 5-fold CV pe galaxii (seed=42), identic cu D9b.

Date: data/rotation/rotation_ds006_rotmod.csv (sub-set THINGS)
Referinta: de Blok et al. 2008, arXiv:0810.2100
"""

from __future__ import annotations

import csv
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "things-test-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M   # factor conversie [km²/s²/kpc] → [m/s²]
A0_SI    = 1.2e-10                   # MOND a0 [m/s²]
A0_INT   = A0_SI / G_UNIT            # MOND a0 [km²/s²/kpc]

N_FOLDS = 5
SEED    = 42

# Cele 13 galaxii THINGS prezente in ds006
THINGS_GALAXIES = [
    "DDO154", "IC2574", "NGC2366", "NGC2403", "NGC2841",
    "NGC2903", "NGC2976", "NGC3198", "NGC3521", "NGC5055",
    "NGC6946", "NGC7331", "NGC7793",
]
# Lipsesc din ds006 (vor fi adaugate cand datele THINGS complete vor fi incarcate):
THINGS_MISSING = ["NGC925", "NGC3031", "NGC3621", "NGC3627", "NGC4736", "NGC4826"]


# ---------------------------------------------------------------------------
# Date
# ---------------------------------------------------------------------------

def load_things(path: Path) -> dict[str, list[dict]]:
    gals: dict[str, list[dict]] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gal = row["system_id"]
            if gal not in THINGS_GALAXIES:
                continue
            r  = float(row["radius"])
            v  = float(row["v_obs"])
            ve = float(row["v_err"])
            bt = float(row["baryon_term"])
            if r <= 0 or ve <= 0 or bt < 0:
                continue
            g_bar = bt / max(r, 1e-9)
            chi   = g_bar / A0_INT
            gals.setdefault(gal, []).append({
                "r": r, "v": v, "ve": ve, "bt": bt, "g_bar": g_bar, "chi": chi,
            })
    for pts in gals.values():
        pts.sort(key=lambda p: p["r"])
    return gals


def flatten(gals_dict: dict, names: list[str]) -> list[dict]:
    pts = []
    for n in names:
        pts.extend(gals_dict[n])
    return pts


# ---------------------------------------------------------------------------
# Forme MOND
# ---------------------------------------------------------------------------

def nu_rar(chi: float) -> float:
    """RAR McGaugh 2016: 1/(1-exp(-√χ))"""
    x = math.sqrt(max(chi, 1e-30))
    e = math.exp(-x)
    if 1.0 - e < 1e-15:
        return 1.0 / max(x, 1e-15)
    return 1.0 / (1.0 - e)


def nu_simple(chi: float) -> float:
    """Simple (Famaey&Binney): 1 + 1/√χ"""
    return 1.0 + 1.0 / math.sqrt(max(chi, 1e-30))


def nu_standard(chi: float) -> float:
    """Standard Milgrom 83: ½(1+√(1+4/χ))"""
    return 0.5 * (1.0 + math.sqrt(1.0 + 4.0 / max(chi, 1e-30)))


def v_mond_form(pt: dict, g_dag: float, nu_fn) -> float:
    g_bar = pt["g_bar"]
    chi_d = g_bar / max(g_dag, 1e-30)
    g_obs = g_bar * nu_fn(chi_d)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


# ---------------------------------------------------------------------------
# M8c — QNG straton
# ---------------------------------------------------------------------------

def T3(pt: dict, g_dag: float) -> float:
    chi_d = pt["g_bar"] / max(g_dag, 1e-30)
    return math.sqrt(max(pt["g_bar"] * g_dag, 0.0)) * math.exp(-chi_d)


def v_m8c(pt: dict, k: float, g_dag: float) -> float:
    return math.sqrt(max(pt["bt"] + pt["r"] * k * T3(pt, g_dag), 0.0))


# ---------------------------------------------------------------------------
# M0 Null
# ---------------------------------------------------------------------------

def v_null(pt: dict) -> float:
    return math.sqrt(max(pt["bt"], 0.0))


# ---------------------------------------------------------------------------
# Chi2
# ---------------------------------------------------------------------------

def chi2_pts(pts: list[dict], vfn) -> float:
    return sum(((p["v"] - vfn(p)) / p["ve"])**2 for p in pts)


# ---------------------------------------------------------------------------
# Optimizare
# ---------------------------------------------------------------------------

def golden_search(f, lo: float, hi: float, tol: float = 1e-7, nmax: int = 300):
    phi = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc, fd = f(c), f(d)
    for _ in range(nmax):
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
    best = c if fc <= fd else d
    return best, min(fc, fd)


def fit_mond(pts: list[dict], nu_fn) -> tuple[float, float]:
    """Fit g† pentru o forma MOND. Returns (g_dag, chi2_total)."""
    def f(g_dag):
        return chi2_pts(pts, lambda p: v_mond_form(p, g_dag, nu_fn))
    return golden_search(f, 0.01 * A0_INT, 200.0 * A0_INT)


def fit_m8c(pts: list[dict]) -> tuple[float, float, float]:
    """Fit M8c (k, g†). Returns (k, g_dag, chi2_total)."""
    best = (0.0, A0_INT, 1e30)
    # Grid grossier pe k, then golden pe g_dag
    for k_try in [0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 7.0, 10.0]:
        def f_gd(gd, k=k_try):
            return chi2_pts(pts, lambda p: v_m8c(p, k, gd))
        gd_opt, c2 = golden_search(f_gd, 0.01 * A0_INT, 200.0 * A0_INT)
        if c2 < best[2]:
            best = (k_try, gd_opt, c2)
    # Rafinare k in jurul optimului
    k_center = best[0]
    def f_k(k):
        def f_gd(gd):
            return chi2_pts(pts, lambda p: v_m8c(p, k, gd))
        _, c2 = golden_search(f_gd, 0.01 * A0_INT, 200.0 * A0_INT)
        return c2
    k_lo = max(0.01, k_center * 0.3)
    k_hi = k_center * 3.0
    k_opt, _ = golden_search(f_k, k_lo, k_hi)
    def f_gd_final(gd):
        return chi2_pts(pts, lambda p: v_m8c(p, k_opt, gd))
    gd_opt_f, c2_f = golden_search(f_gd_final, 0.01 * A0_INT, 200.0 * A0_INT)
    return k_opt, gd_opt_f, c2_f


def aic(chi2: float, k: int) -> float:
    return chi2 + 2.0 * k


def bic(chi2: float, k: int, n: int) -> float:
    return chi2 + k * math.log(max(n, 1))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("THINGS Test v1 — de Blok et al. 2008 sub-set")
    print("=" * 70)
    print(f"Date: {DATA_CSV}")
    print(f"MOND a0 (intern) = {A0_INT:.1f} km²/s²/kpc  ({A0_SI:.1e} m/s²)")
    print()

    gals = load_things(DATA_CSV)
    gal_names = sorted(gals.keys())
    n_gal = len(gal_names)
    all_pts = flatten(gals, gal_names)
    n_total = len(all_pts)

    print(f"THINGS galaxii incarcate: {n_gal}/{len(THINGS_GALAXIES) + len(THINGS_MISSING)}")
    print(f"Galaxii: {', '.join(gal_names)}")
    print(f"Total puncte: {n_total}")
    print()
    for g in gal_names:
        print(f"  {g:12s}: {len(gals[g]):3d} puncte  "
              f"r=[{gals[g][0]['r']:.2f},{gals[g][-1]['r']:.2f}] kpc  "
              f"g_bar/a0=[{gals[g][0]['g_bar']/A0_INT:.2f},{gals[g][-1]['g_bar']/A0_INT:.2f}]")
    print()

    if n_gal < len(THINGS_GALAXIES):
        missing_found = [g for g in THINGS_GALAXIES if g not in gals]
        if missing_found:
            print(f"ATENTIE: {len(missing_found)} galaxii THINGS nu au fost gasite in ds006:")
            print(f"  {missing_found}")
            print()

    # ------------------------------------------------------------------
    # Fit GLOBAL (toate punctele)
    # ------------------------------------------------------------------
    print("─" * 70)
    print("FIT GLOBAL pe toate punctele THINGS")
    print("─" * 70)

    chi2_null_g = chi2_pts(all_pts, v_null)
    print(f"M0  Null:          chi2={chi2_null_g:8.1f}  chi2/N={chi2_null_g/n_total:.3f}  k=0")

    nu_forms = [
        ("M1  MOND RAR",    nu_rar),
        ("M1s MOND Simple", nu_simple),
        ("M1m MOND Std",    nu_standard),
    ]
    mond_results = {}
    for name, nu_fn in nu_forms:
        g_dag, c2 = fit_mond(all_pts, nu_fn)
        g_dag_si = g_dag * G_UNIT
        mond_results[name] = {"g_dag": g_dag, "g_dag_si": g_dag_si, "chi2": c2}
        print(f"{name}: chi2={c2:8.1f}  chi2/N={c2/n_total:.3f}  k=1  "
              f"g†={g_dag_si:.2e} m/s²")

    k_m8c, gd_m8c, c2_m8c = fit_m8c(all_pts)
    gd_m8c_si = gd_m8c * G_UNIT
    print(f"M8c QNG straton:   chi2={c2_m8c:8.1f}  chi2/N={c2_m8c/n_total:.3f}  k=2  "
          f"k={k_m8c:.3f}  g†={gd_m8c_si:.2e} m/s²")
    print()

    # ------------------------------------------------------------------
    # 5-Fold Cross-Validation pe galaxii
    # ------------------------------------------------------------------
    print("─" * 70)
    print(f"5-FOLD CROSS-VALIDATION (seed={SEED}, split pe galaxii)")
    print("─" * 70)

    rng = random.Random(SEED)
    shuffled = gal_names[:]
    rng.shuffle(shuffled)
    folds = [shuffled[i::N_FOLDS] for i in range(N_FOLDS)]

    model_keys = ["M1_RAR", "M1s_Simple", "M1m_Standard", "M8c"]
    cv_chi2 = {k: 0.0 for k in model_keys}
    cv_n    = 0

    for fold_i, test_gals in enumerate(folds):
        train_gals = [g for g in gal_names if g not in test_gals]
        train_pts  = flatten(gals, train_gals)
        test_pts   = flatten(gals, test_gals)
        n_tr, n_te = len(train_pts), len(test_pts)

        # Fit pe TRAIN
        gd_rar,  c2_tr_rar  = fit_mond(train_pts, nu_rar)
        gd_sim,  c2_tr_sim  = fit_mond(train_pts, nu_simple)
        gd_std,  c2_tr_std  = fit_mond(train_pts, nu_standard)
        k_cv, gd_cv, c2_tr_m8c = fit_m8c(train_pts)

        # Eval pe TEST
        c2_te_rar = chi2_pts(test_pts, lambda p: v_mond_form(p, gd_rar, nu_rar))
        c2_te_sim = chi2_pts(test_pts, lambda p: v_mond_form(p, gd_sim, nu_simple))
        c2_te_std = chi2_pts(test_pts, lambda p: v_mond_form(p, gd_std, nu_standard))
        c2_te_m8c = chi2_pts(test_pts, lambda p: v_m8c(p, k_cv, gd_cv))

        cv_chi2["M1_RAR"]      += c2_te_rar
        cv_chi2["M1s_Simple"]  += c2_te_sim
        cv_chi2["M1m_Standard"]+= c2_te_std
        cv_chi2["M8c"]         += c2_te_m8c
        cv_n += n_te

        print(f"  Fold {fold_i+1}: train={n_tr}pt({len(train_gals)}gal)  "
              f"test={n_te}pt({len(test_gals)}gal: {','.join(test_gals)})")
        print(f"    TEST chi2/N — RAR:{c2_te_rar/n_te:.3f}  "
              f"Sim:{c2_te_sim/n_te:.3f}  Std:{c2_te_std/n_te:.3f}  "
              f"M8c:{c2_te_m8c/n_te:.3f}")

    print()
    print("REZULTATE CV (mean TEST chi2/N):")
    for k in model_keys:
        print(f"  {k:14s}: {cv_chi2[k]/cv_n:.4f}")

    best_mond_key = min(["M1_RAR","M1s_Simple","M1m_Standard"], key=lambda k: cv_chi2[k])
    best_mond_cv  = cv_chi2[best_mond_key] / cv_n
    m8c_cv        = cv_chi2["M8c"] / cv_n
    ratio         = m8c_cv / best_mond_cv
    m8c_wins      = m8c_cv < best_mond_cv

    print()
    print("─" * 70)
    print("VERDICT FINAL — THINGS")
    print("─" * 70)
    chi2_rar_g = mond_results["M1  MOND RAR"]["chi2"]
    print(f"  MOND best CV: {best_mond_key} = {best_mond_cv:.4f}")
    print(f"  M8c (QNG)  CV: {m8c_cv:.4f}")
    print(f"  Ratio M8c/MOND_best: {ratio:.4f}  "
          f"({'✓ M8c BATE MOND pe THINGS' if m8c_wins else '✗ M8c pierde fata de MOND pe THINGS'})")
    print()

    # Per-galaxie breakdown
    print("─" * 70)
    print("PER GALAXIE (fit global, chi2/N):")
    print(f"  {'Galaxy':12s}  {'N':>4s}  {'Null':>6s}  {'MOND_RAR':>9s}  {'M8c':>7s}  {'Winner':>10s}")
    print("  " + "-" * 55)

    gd_rar_g, _ = fit_mond(all_pts, nu_rar)
    per_gal_rows = []
    for g in gal_names:
        pts_g = gals[g]
        n_g   = len(pts_g)
        c0    = chi2_pts(pts_g, v_null) / n_g
        c1    = chi2_pts(pts_g, lambda p: v_mond_form(p, gd_rar_g, nu_rar)) / n_g
        c3    = chi2_pts(pts_g, lambda p: v_m8c(p, k_m8c, gd_m8c)) / n_g
        winner = "M8c" if c3 < c1 else "MOND"
        print(f"  {g:12s}  {n_g:4d}  {c0:6.2f}  {c1:9.3f}  {c3:7.3f}  {winner:>10s}")
        per_gal_rows.append({"galaxy": g, "N": n_g,
                              "chi2_n_null": round(c0, 4),
                              "chi2_n_mond_rar": round(c1, 4),
                              "chi2_n_m8c": round(c3, 4),
                              "winner": winner})
    print()

    # ------------------------------------------------------------------
    # Scriere artefacte
    # ------------------------------------------------------------------
    # CSV per galaxie
    csv_path = OUT_DIR / "per_galaxy.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["galaxy","N","chi2_n_null","chi2_n_mond_rar","chi2_n_m8c","winner"])
        w.writeheader()
        w.writerows(per_gal_rows)

    # Summary JSON
    summary = {
        "test_id": "things-test-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reference": "de Blok et al. 2008, AJ 136 2648 (arXiv:0810.2100)",
        "data_source": "ds006_rotmod.csv (SPARC subset coincident cu THINGS)",
        "n_things_total": len(THINGS_GALAXIES) + len(THINGS_MISSING),
        "n_things_in_ds006": n_gal,
        "n_things_missing": len(THINGS_MISSING),
        "things_missing_galaxies": THINGS_MISSING,
        "galaxies": gal_names,
        "n_points": n_total,
        "cv_folds": N_FOLDS,
        "cv_seed": SEED,
        "global_fit": {
            "M0_null":     {"chi2": round(chi2_null_g, 2), "chi2_per_n": round(chi2_null_g/n_total, 4), "k": 0},
            "M1_MOND_RAR": {"chi2": round(mond_results["M1  MOND RAR"]["chi2"], 2),
                            "chi2_per_n": round(mond_results["M1  MOND RAR"]["chi2"]/n_total, 4),
                            "k": 1,
                            "g_dag_m_s2": mond_results["M1  MOND RAR"]["g_dag_si"]},
            "M8c_QNG":     {"chi2": round(c2_m8c, 2), "chi2_per_n": round(c2_m8c/n_total, 4),
                            "k": 2, "k_param": round(k_m8c, 4),
                            "g_dag_m_s2": gd_m8c_si},
        },
        "cv_results": {k: {"mean_test_chi2_per_n": round(cv_chi2[k]/cv_n, 4)} for k in model_keys},
        "verdict": {
            "best_mond": best_mond_key,
            "best_mond_cv_chi2_per_n": round(best_mond_cv, 4),
            "m8c_cv_chi2_per_n": round(m8c_cv, 4),
            "ratio_m8c_over_mond": round(ratio, 4),
            "m8c_wins": m8c_wins,
            "conclusion": (
                "M8c (QNG straton) BATE MOND pe sub-setul THINGS disponibil in ds006 (subset check, nu validare independenta completa)"
                if m8c_wins else
                "M8c (QNG straton) pierde fata de MOND pe sub-setul THINGS disponibil in ds006 (subset check)"
            ),
        },
    }

    (OUT_DIR / "things_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Artefacte scrise in: {OUT_DIR}")
    print(f"  - per_galaxy.csv")
    print(f"  - things_summary.json")
    print()

    if THINGS_MISSING:
        print(f"NOTE: Lipsesc {len(THINGS_MISSING)} galaxii THINGS din ds006:")
        print(f"  {THINGS_MISSING}")
        print(f"  → Adaugati fisierele THINGS originale mâine si re-rulati pentru rezultat complet.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
