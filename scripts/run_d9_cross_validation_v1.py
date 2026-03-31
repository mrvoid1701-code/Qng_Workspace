#!/usr/bin/env python3
"""
D9 — Cross-Validation M8c vs MOND pe SPARC (anti-cherry-pick)

Metodologie:
  5-fold cross-validation pe cei 175 SPARC (galactics).
  Pentru fiecare fold:
    1. FIT M8c pe TRAIN (140 gal) → k_train, g_dag_train
    2. FIT MOND pe TRAIN (140 gal) → g_dag_mond_train
    3. Evalueaza parametri INGHETATI pe TEST (35 gal)
    4. Raporteaza chi2/N pe TEST

Daca M8c/MOND < 1 consistent pe toate fold-urile:
  → modelul generalizeaza, NU e overfit pe training set.
  → argument anti-cherry-pick definitiv.

Criteriu preregistrat:
  PASS:   M8c/MOND < 1.0 pe cel putin 4/5 fold-uri
  STRONG: M8c/MOND_mean < 0.95 (media pe toate fold-urile)
  FAIL:   M8c/MOND >= 1.0 pe >= 3 fold-uri (modelul nu generalizeaza)
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
OUT_DIR  = ROOT / "05_validation" / "evidence" / "artifacts" / "d9-cross-validation-v1"

KM_TO_M  = 1e3
KPC_TO_M = 3.0857e19
G_UNIT   = KM_TO_M**2 / KPC_TO_M
A0_SI    = 1.2e-10
A0_INT   = A0_SI / G_UNIT

N_FOLDS  = 5
SEED     = 42  # fix seed → reproductibil


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
# Modele
# ---------------------------------------------------------------------------

def T3(pt: dict, g_dag: float) -> float:
    chi_d = pt["g_bar"] / max(g_dag, 1e-30)
    return math.sqrt(max(pt["g_bar"] * g_dag, 0.0)) * math.exp(-chi_d)


def v_m8c(pt: dict, k: float, g_dag: float) -> float:
    return math.sqrt(max(pt["bt"] + pt["r"] * k * T3(pt, g_dag), 0.0))


def v_mond(pt: dict, g_dag: float) -> float:
    g_bar = pt["g_bar"]
    if g_bar <= 0:
        return 0.0
    x     = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * pt["r"], 0.0))


def chi2_pts(pts: list[dict], f_model) -> float:
    return sum(((p["v"] - f_model(p)) / p["ve"])**2 for p in pts)


# ---------------------------------------------------------------------------
# Optimizare (fara dependente externe)
# ---------------------------------------------------------------------------

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


def fit_m8c(pts: list[dict]) -> tuple[float, float, float]:
    """
    Fit M8c pe pts: minimizeaza chi2 peste (k, g_dag).
    Returns (k, g_dag, chi2/N).
    """
    N = len(pts)
    if N == 0:
        return 0.0, A0_INT, float("inf")

    def chi2_fn(k: float, g_dag: float) -> float:
        return chi2_pts(pts, lambda p: v_m8c(p, k, g_dag))

    # Grid 2D: g_dag in [0.1*A0, 5*A0], k in [0.1, 5.0]
    n_outer = 60
    best = (1.0, A0_INT, float("inf"))
    for i in range(n_outer):
        gd = 0.1 * A0_INT + (5.0 * A0_INT - 0.1 * A0_INT) * i / (n_outer - 1)
        k_opt, c2 = golden_search(lambda k: chi2_fn(k, gd), 0.05, 8.0)
        if c2 < best[2]:
            best = (k_opt, gd, c2)

    # Refinare locala
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


def fit_mond(pts: list[dict]) -> tuple[float, float]:
    """Fit MOND (1 param: g_dag). Returns (g_dag, chi2/N)."""
    N = len(pts)
    if N == 0:
        return A0_INT, float("inf")
    gd_opt, c2 = golden_search(
        lambda gd: chi2_pts(pts, lambda p: v_mond(p, gd)),
        0.01 * A0_INT, 10.0 * A0_INT)
    return gd_opt, c2 / N


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------

def run_crossval(gals: dict) -> dict:
    names = sorted(gals.keys())
    rng   = random.Random(SEED)
    rng.shuffle(names)

    n_gal  = len(names)
    folds  = [[] for _ in range(N_FOLDS)]
    for i, name in enumerate(names):
        folds[i % N_FOLDS].append(name)

    fold_results = []

    for fold_idx in range(N_FOLDS):
        test_names  = folds[fold_idx]
        train_names = [n for i, f in enumerate(folds) for n in f if i != fold_idx]

        train_pts = flatten(gals, train_names)
        test_pts  = flatten(gals, test_names)

        n_train = len(train_pts)
        n_test  = len(test_pts)

        print(f"\n--- Fold {fold_idx+1}/{N_FOLDS} ---")
        print(f"  TRAIN: {len(train_names)} gal, {n_train} pts")
        print(f"  TEST:  {len(test_names)} gal, {n_test} pts")

        # Fit pe TRAIN
        print("  Fitting M8c pe TRAIN...")
        k_train, gd_train, c2_train_m8c = fit_m8c(train_pts)
        print(f"  M8c TRAIN: k={k_train:.4f}, g_dag/a0={gd_train/A0_INT:.4f}, chi2/N={c2_train_m8c:.4f}")

        print("  Fitting MOND pe TRAIN...")
        gd_mond_train, c2_train_mond = fit_mond(train_pts)
        print(f"  MOND TRAIN: g_dag/a0={gd_mond_train/A0_INT:.4f}, chi2/N={c2_train_mond:.4f}")

        # Evalueaza pe TEST (parametri INGHETATI din TRAIN)
        c2_test_m8c  = chi2_pts(test_pts, lambda p: v_m8c(p, k_train, gd_train)) / n_test
        c2_test_mond = chi2_pts(test_pts, lambda p: v_mond(p, gd_mond_train)) / n_test

        ratio = c2_test_m8c / max(c2_test_mond, 1e-15)
        beats = ratio < 1.0

        print(f"  TEST  M8c  chi2/N = {c2_test_m8c:.4f}")
        print(f"  TEST  MOND chi2/N = {c2_test_mond:.4f}")
        print(f"  Ratio M8c/MOND    = {ratio:.4f}  {'✓ BEATS MOND' if beats else '✗ LOSES TO MOND'}")

        fold_results.append({
            "fold": fold_idx + 1,
            "n_train_gal": len(train_names),
            "n_test_gal":  len(test_names),
            "n_train_pts": n_train,
            "n_test_pts":  n_test,
            "train_k":     k_train,
            "train_gdag_over_a0": gd_train / A0_INT,
            "train_gdag_mond_over_a0": gd_mond_train / A0_INT,
            "train_chi2_per_n_m8c":  c2_train_m8c,
            "train_chi2_per_n_mond": c2_train_mond,
            "test_chi2_per_n_m8c":   c2_test_m8c,
            "test_chi2_per_n_mond":  c2_test_mond,
            "test_ratio_m8c_over_mond": ratio,
            "test_beats_mond": beats,
        })

    # Statistici globale
    ratios        = [f["test_ratio_m8c_over_mond"] for f in fold_results]
    beats_count   = sum(1 for f in fold_results if f["test_beats_mond"])
    mean_ratio    = sum(ratios) / N_FOLDS
    # Coeficient de variatie al ratio-ului
    var_ratio     = sum((r - mean_ratio)**2 for r in ratios) / N_FOLDS
    std_ratio     = math.sqrt(var_ratio)

    # Median
    sorted_ratios = sorted(ratios)
    median_ratio  = sorted_ratios[N_FOLDS // 2]

    # Mean test chi2/N (legacy: unweighted over folds)
    mean_m8c  = sum(f["test_chi2_per_n_m8c"]  for f in fold_results) / N_FOLDS
    mean_mond = sum(f["test_chi2_per_n_mond"]  for f in fold_results) / N_FOLDS

    improve_pct = (1.0 - mean_ratio) * 100.0

    # Point-weighted aggregates for comparability with D9b.
    total_test_pts = sum(f["n_test_pts"] for f in fold_results)
    weighted_m8c = sum(f["test_chi2_per_n_m8c"] * f["n_test_pts"] for f in fold_results) / max(total_test_pts, 1)
    weighted_mond = sum(f["test_chi2_per_n_mond"] * f["n_test_pts"] for f in fold_results) / max(total_test_pts, 1)
    weighted_ratio = weighted_m8c / max(weighted_mond, 1e-15)
    weighted_improve_pct = (1.0 - weighted_ratio) * 100.0

    # Criteriu
    if beats_count >= 4 and mean_ratio < 0.95:
        verdict = "STRONG_PASS"
    elif beats_count >= 4:
        verdict = "PASS"
    elif beats_count == 3:
        verdict = "MARGINAL"
    else:
        verdict = "FAIL"

    return {
        "fold_results": fold_results,
        "summary": {
            "n_folds":       N_FOLDS,
            "n_galaxies":    n_gal,
            "beats_count":   beats_count,
            "mean_ratio_m8c_over_mond": mean_ratio,
            "median_ratio":  median_ratio,
            "std_ratio":     std_ratio,
            "improve_pct_vs_mond": improve_pct,
            "mean_test_chi2_m8c":  mean_m8c,
            "mean_test_chi2_mond": mean_mond,
            "mean_test_chi2_m8c_weighted": weighted_m8c,
            "mean_test_chi2_mond_weighted": weighted_mond,
            "mean_ratio_m8c_over_mond_weighted": weighted_ratio,
            "improve_pct_vs_mond_weighted": weighted_improve_pct,
            "verdict": verdict,
            "seed": SEED,
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not DATA_CSV.exists():
        print(f"EROARE: date lipsa la {DATA_CSV}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Incarc date din {DATA_CSV} ...")
    gals = load_galaxies(DATA_CSV)
    n_gal = len(gals)
    n_pts = sum(len(v) for v in gals.values())
    print(f"  {n_gal} galaxii, {n_pts} puncte totale")

    print(f"\nRulez {N_FOLDS}-fold cross-validation (seed={SEED})...")
    results = run_crossval(gals)

    s = results["summary"]
    print("\n" + "="*60)
    print("SUMAR FINAL D9")
    print("="*60)
    print(f"  Galaxii: {s['n_galaxies']}")
    print(f"  Fold-uri M8c bate MOND: {s['beats_count']}/{N_FOLDS}")
    print(f"  Mean ratio M8c/MOND:    {s['mean_ratio_m8c_over_mond']:.4f}")
    print(f"  Median ratio:           {s['median_ratio']:.4f}")
    print(f"  Std ratio:              {s['std_ratio']:.4f}")
    print(f"  Imbunatatire medie:     {s['improve_pct_vs_mond']:.2f}%")
    print(f"  Mean TEST chi2/N M8c:   {s['mean_test_chi2_m8c']:.4f}")
    print(f"  Mean TEST chi2/N MOND:  {s['mean_test_chi2_mond']:.4f}")
    print(f"  Weighted ratio M8c/MOND:{s['mean_ratio_m8c_over_mond_weighted']:.4f}")
    print(f"  Weighted improve:       {s['improve_pct_vs_mond_weighted']:.2f}%")
    print(f"  VERDICT: {s['verdict']}")

    # Salveaza JSON
    out = {
        "test_id":    "d9-cross-validation-v1",
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dataset":    "SPARC rotmod (DS006)",
        "method":     f"{N_FOLDS}-fold cross-validation (shuffle+modulo split, non-stratified), frozen parameters",
        "a0_si":      A0_SI,
        "results":    results,
    }
    out_path = OUT_DIR / "d9_summary.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\nSalvat: {out_path}")

    # Exit code pe baza verdictului
    if s["verdict"] in ("STRONG_PASS", "PASS"):
        sys.exit(0)
    elif s["verdict"] == "MARGINAL":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
