#!/usr/bin/env python3
"""
D9b — MOND Multi-Form Benchmark: care forma MOND e cea mai buna?

Scopul: gasim cel mai puternic MOND posibil ca baseline, apoi comparam M8c contra el.
Daca M8c bate chiar si MOND_best → rezultat de neclintit.

Forme MOND testate (toate cu 1 param liber: g†):
  RAR   (McGaugh 2016):   g_obs = g_bar / (1 - exp(-√χ))         ← curent in D7/D9
  Simple (Famaey&Binney): g_obs = g_bar * ν,  ν = 1 + 1/√χ
  Standard (Milgrom 83):  g_obs = g_bar * ν,  ν = ½(1+√(1+4/χ))
  Gamma  (exp linear):    g_obs = g_bar / (1 - exp(-χ))

M8c (2 param: k, g†):  g_obs = g_bar + k * √(g_bar·g†) * exp(-g_bar/g†)

Metodologie: 5-fold cross-validation identic cu D9 (seed=42).
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
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "d9b-mond-forms-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M
A0_SI    = 1.2e-10
A0_INT   = A0_SI / G_UNIT

N_FOLDS  = 5
SEED     = 42


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


def flatten(gals_dict: dict, names: list[str]) -> list[dict]:
    pts = []
    for n in names:
        pts.extend(gals_dict[n])
    return pts


# ---------------------------------------------------------------------------
# Forme MOND
# ---------------------------------------------------------------------------

def nu_rar(chi: float) -> float:
    """McGaugh 2016 RAR: 1/(1-exp(-√χ))"""
    x = math.sqrt(max(chi, 1e-30))
    d = 1.0 - math.exp(-x)
    return 1.0 / d if abs(d) > 1e-15 else 1.0 / 1e-15

def nu_simple(chi: float) -> float:
    """Famaey & Binney 2005: 1 + 1/√χ"""
    return 1.0 + 1.0 / math.sqrt(max(chi, 1e-30))

def nu_standard(chi: float) -> float:
    """Milgrom 1983 standard: ½(1 + √(1 + 4/χ))"""
    return 0.5 * (1.0 + math.sqrt(1.0 + 4.0 / max(chi, 1e-30)))

def nu_gamma(chi: float) -> float:
    """Exponential liniar: 1/(1-exp(-χ))"""
    d = 1.0 - math.exp(-max(chi, 1e-30))
    return 1.0 / d if abs(d) > 1e-15 else 1.0 / 1e-15

MOND_FORMS = {
    "RAR":      nu_rar,
    "Simple":   nu_simple,
    "Standard": nu_standard,
    "Gamma":    nu_gamma,
}

def v_mond_form(pt: dict, g_dag: float, nu_fn) -> float:
    """v_obs pentru orice forma MOND: g_obs = g_bar * ν(g_bar/g†)"""
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    chi_d = g_bar / max(g_dag, 1e-30)
    g_obs = g_bar * nu_fn(chi_d)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


# ---------------------------------------------------------------------------
# M8c
# ---------------------------------------------------------------------------

def T3(pt: dict, g_dag: float) -> float:
    chi_d = pt["g_bar"] / max(g_dag, 1e-30)
    return math.sqrt(max(pt["g_bar"] * g_dag, 0.0)) * math.exp(-chi_d)

def v_m8c(pt: dict, k: float, g_dag: float) -> float:
    return math.sqrt(max(pt["bt"] + pt["r"] * k * T3(pt, g_dag), 0.0))


# ---------------------------------------------------------------------------
# Optimizare
# ---------------------------------------------------------------------------

def chi2_pts(pts: list[dict], f_model) -> float:
    return sum(((p["v"] - f_model(p)) / p["ve"])**2 for p in pts)

def golden_search(f, lo: float, hi: float, tol: float = 1e-7, max_iter: int = 600):
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
    return (c if fc < fd else d), min(fc, fd)

def fit_mond_form(pts: list[dict], nu_fn) -> tuple[float, float]:
    """Fit g† pentru o forma MOND. Returns (g_dag, chi2/N)."""
    N = len(pts)
    if N == 0:
        return A0_INT, float("inf")
    gd_opt, c2 = golden_search(
        lambda gd: chi2_pts(pts, lambda p: v_mond_form(p, gd, nu_fn)),
        0.01 * A0_INT, 10.0 * A0_INT)
    return gd_opt, c2 / N

def fit_m8c(pts: list[dict]) -> tuple[float, float, float]:
    """Fit M8c (k, g†). Returns (k, g_dag, chi2/N)."""
    N = len(pts)
    if N == 0:
        return 0.0, A0_INT, float("inf")

    def chi2_fn(k: float, g_dag: float) -> float:
        return chi2_pts(pts, lambda p: v_m8c(p, k, g_dag))

    n_outer = 60
    best = (1.0, A0_INT, float("inf"))
    for i in range(n_outer):
        gd = 0.1 * A0_INT + (5.0 * A0_INT - 0.1 * A0_INT) * i / (n_outer - 1)
        k_opt, c2 = golden_search(lambda k: chi2_fn(k, gd), 0.05, 8.0)
        if c2 < best[2]:
            best = (k_opt, gd, c2)

    k_c, gd_c, _ = best
    gd_step = 0.4 * A0_INT
    for i in range(40):
        gd = max(0.05 * A0_INT, gd_c - gd_step) + 2 * gd_step * i / 39
        k_opt, c2 = golden_search(
            lambda k: chi2_fn(k, gd),
            max(0.05, k_c * 0.5), k_c * 2.0 + 0.5, tol=1e-8)
        if c2 < best[2]:
            best = (k_opt, gd, c2)

    k_f, gd_f, c2_f = best
    return k_f, gd_f, c2_f / N


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------

def run_crossval(gals: dict) -> dict:
    names = sorted(gals.keys())
    rng   = random.Random(SEED)
    rng.shuffle(names)

    folds = [[] for _ in range(N_FOLDS)]
    for i, name in enumerate(names):
        folds[i % N_FOLDS].append(name)

    # Acumuleaza chi2 test per forma
    test_sums  = {form: 0.0 for form in MOND_FORMS}
    test_sums["M8c"] = 0.0
    test_n_total = 0

    fold_results = []

    for fold_idx in range(N_FOLDS):
        test_names  = folds[fold_idx]
        train_names = [n for i, f in enumerate(folds) for n in f if i != fold_idx]

        train_pts = flatten(gals, train_names)
        test_pts  = flatten(gals, test_names)
        n_test    = len(test_pts)
        test_n_total += n_test

        print(f"\n=== Fold {fold_idx+1}/{N_FOLDS} "
              f"(train {len(train_names)} gal / test {len(test_names)} gal) ===")

        # Fit M8c pe TRAIN
        k_train, gd_train, c2_train_m8c = fit_m8c(train_pts)
        c2_test_m8c = chi2_pts(test_pts, lambda p: v_m8c(p, k_train, gd_train)) / n_test
        test_sums["M8c"] += c2_test_m8c * n_test
        print(f"  M8c  TRAIN chi2/N={c2_train_m8c:.3f}  "
              f"k={k_train:.4f} g†/a0={gd_train/A0_INT:.4f}  "
              f"TEST chi2/N={c2_test_m8c:.3f}")

        fold_mond = {}
        for form_name, nu_fn in MOND_FORMS.items():
            gd_opt, c2_train = fit_mond_form(train_pts, nu_fn)
            c2_test = chi2_pts(test_pts,
                               lambda p, gd=gd_opt, nf=nu_fn: v_mond_form(p, gd, nf)) / n_test
            test_sums[form_name] += c2_test * n_test
            ratio = c2_test_m8c / max(c2_test, 1e-15)
            beats = ratio < 1.0
            fold_mond[form_name] = {
                "gdag_over_a0": gd_opt / A0_INT,
                "train_chi2_per_n": c2_train,
                "test_chi2_per_n":  c2_test,
                "ratio_m8c_over_mond": ratio,
                "m8c_beats": beats,
            }
            print(f"  {form_name:<9} TRAIN chi2/N={c2_train:.3f}  "
                  f"g†/a0={gd_opt/A0_INT:.4f}  "
                  f"TEST chi2/N={c2_test:.3f}  "
                  f"ratio={ratio:.4f} {'✓' if beats else '✗'}")

        fold_results.append({
            "fold": fold_idx + 1,
            "n_train_gal": len(train_names),
            "n_test_gal":  len(test_names),
            "n_test_pts":  n_test,
            "m8c": {"k": k_train, "gdag_over_a0": gd_train/A0_INT,
                    "test_chi2_per_n": c2_test_m8c},
            "mond_forms": fold_mond,
        })

    # Medii globale ponderate pe n_test_pts
    mean_m8c = test_sums["M8c"] / test_n_total
    print("\n" + "="*65)
    print("SUMAR GLOBAL (medii ponderate pe puncte test)")
    print("="*65)
    print(f"  M8c    mean TEST chi2/N = {mean_m8c:.4f}")

    mond_means = {}
    best_form  = None
    best_chi2  = float("inf")
    for form_name in MOND_FORMS:
        mn = test_sums[form_name] / test_n_total
        mond_means[form_name] = mn
        ratio = mean_m8c / max(mn, 1e-15)
        beats = ratio < 1.0
        print(f"  {form_name:<9} mean TEST chi2/N = {mn:.4f}  "
              f"M8c/MOND={ratio:.4f} {'✓ M8c wins' if beats else '✗ M8c loses'}")
        if mn < best_chi2:
            best_chi2 = mn
            best_form = form_name

    ratio_vs_best = mean_m8c / max(best_chi2, 1e-15)
    improve_vs_best = (1.0 - ratio_vs_best) * 100.0
    print(f"\n  Cea mai buna forma MOND: {best_form} (chi2/N={best_chi2:.4f})")
    print(f"  M8c vs MOND_best: ratio={ratio_vs_best:.4f}, "
          f"imbunatatire={improve_vs_best:.2f}%")

    # Unweighted fold means (for direct comparability with D9 legacy metric).
    mean_m8c_unweighted = sum(f["m8c"]["test_chi2_per_n"] for f in fold_results) / N_FOLDS
    mond_means_unweighted = {}
    best_form_unweighted = None
    best_chi2_unweighted = float("inf")
    for form_name in MOND_FORMS:
        mn_u = sum(f["mond_forms"][form_name]["test_chi2_per_n"] for f in fold_results) / N_FOLDS
        mond_means_unweighted[form_name] = mn_u
        if mn_u < best_chi2_unweighted:
            best_chi2_unweighted = mn_u
            best_form_unweighted = form_name
    ratio_vs_best_unweighted = mean_m8c_unweighted / max(best_chi2_unweighted, 1e-15)
    improve_vs_best_unweighted = (1.0 - ratio_vs_best_unweighted) * 100.0

    print(f"  (Unweighted folds) best MOND: {best_form_unweighted} "
          f"ratio={ratio_vs_best_unweighted:.4f}, improve={improve_vs_best_unweighted:.2f}%")

    beats_best = ratio_vs_best < 1.0
    if beats_best and improve_vs_best > 5.0:
        verdict = "STRONG_PASS"
    elif beats_best:
        verdict = "PASS"
    else:
        verdict = "FAIL"
    print(f"  VERDICT: {verdict}")

    return {
        "fold_results": fold_results,
        "summary": {
            "n_folds":        N_FOLDS,
            "n_galaxies":     len(gals),
            "mean_m8c_test":  mean_m8c,
            "mond_means":     mond_means,
            "mean_m8c_test_unweighted": mean_m8c_unweighted,
            "mond_means_unweighted": mond_means_unweighted,
            "best_mond_form": best_form,
            "best_mond_chi2": best_chi2,
            "ratio_m8c_over_best_mond": ratio_vs_best,
            "improve_pct_vs_best_mond": improve_vs_best,
            "best_mond_form_unweighted": best_form_unweighted,
            "best_mond_chi2_unweighted": best_chi2_unweighted,
            "ratio_m8c_over_best_mond_unweighted": ratio_vs_best_unweighted,
            "improve_pct_vs_best_mond_unweighted": improve_vs_best_unweighted,
            "m8c_beats_best_mond": beats_best,
            "verdict":        verdict,
            "seed":           SEED,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not DATA_CSV.exists():
        print(f"EROARE: {DATA_CSV}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Incarc date din {DATA_CSV} ...")
    gals = load_galaxies(DATA_CSV)
    print(f"  {len(gals)} galaxii, {sum(len(v) for v in gals.values())} puncte\n")

    results = run_crossval(gals)

    out = {
        "test_id":       "d9b-mond-forms-v1",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset":       "SPARC rotmod DS006",
        "method":        f"{N_FOLDS}-fold CV, frozen params pe test (summary weighted by n_test_pts; unweighted also reported)",
        "mond_forms":    list(MOND_FORMS.keys()),
        "a0_si":         A0_SI,
        "results":       results,
    }
    out_path = OUT_DIR / "d9b_summary.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSalvat: {out_path}")

    s = results["summary"]
    sys.exit(0 if s["verdict"] in ("STRONG_PASS", "PASS") else 2)


if __name__ == "__main__":
    main()
