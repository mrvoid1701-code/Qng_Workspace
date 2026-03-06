#!/usr/bin/env python3
"""
D4 Stage-2 Dual-Kernel Rotation Test (v1).

Goal:
- test a non-circular dual-kernel QNG rotation model on real DS-006 data
- keep anti post-hoc protocol: fixed split, fixed grids, global parameters

Model:
  v_pred^2(r) = bt(r) + k1 * H1_tau(r) + k2 * H2_alpha(r)

  bt(r) = baryon_term(r) = v_baryon(r)^2
  H1_tau: exponential memory kernel over S1-weighted baryonic source
  H2_alpha: long-range power-law kernel over S2-weighted baryonic source

No circular inputs:
- kernels are built from radius + baryon_term only (no v_obs in kernels)
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
from pathlib import Path
import random
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-dual-kernel-v1"

KM_TO_M = 1e3
KPC_TO_M = 3.0857e19
G_UNIT = KM_TO_M * KM_TO_M / KPC_TO_M
A0_SI = 1.2e-10
A0_INTERNAL = A0_SI / G_UNIT


@dataclass
class Point:
    gal: str
    r: float
    v: float
    ve: float
    bt: float


@dataclass
class DualParams:
    tau: float
    alpha: float
    k1: float
    k2: float


def parse_list(raw: str) -> list[float]:
    out: list[float] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(float(t))
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="D4 Stage-2 dual-kernel real-data runner (v1).")
    p.add_argument("--test-id", default="d4-stage2-dual-kernel-v1")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--seed", type=int, default=3401, help="split seed for galaxy train/holdout")
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--s1-lambda", type=float, default=0.28)
    p.add_argument("--s2-const", type=float, default=0.355)
    p.add_argument("--r0-kpc", type=float, default=1.0)
    p.add_argument("--tau-grid", default="0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--alpha-grid", default="0.3,0.5,0.7,1.0,1.3")
    p.add_argument("--outdir", default=str(DEFAULT_OUT))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--no-plots", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_data(path: Path) -> dict[str, list[Point]]:
    if not path.exists():
        raise FileNotFoundError(f"dataset csv not found: {path}")
    out: dict[str, list[Point]] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            try:
                gal = str(r["system_id"]).strip()
                rv = float(r["radius"])
                vv = float(r["v_obs"])
                ve = float(r["v_err"])
                bt = float(r["baryon_term"])
            except Exception:
                continue
            if gal == "" or rv <= 0 or ve <= 0 or bt < 0:
                continue
            out.setdefault(gal, []).append(Point(gal=gal, r=rv, v=vv, ve=ve, bt=bt))
    for pts in out.values():
        pts.sort(key=lambda p: p.r)
    return out


def train_holdout_split(gals: list[str], seed: int, train_frac: float) -> tuple[set[str], set[str]]:
    ordered = sorted(gals)
    rng = random.Random(seed)
    rng.shuffle(ordered)
    n_train = max(1, min(len(ordered) - 1, int(round(train_frac * len(ordered)))))
    train = set(ordered[:n_train])
    holdout = set(ordered[n_train:])
    return train, holdout


def dr_list(pts: list[Point]) -> list[float]:
    n = len(pts)
    if n == 0:
        return []
    if n == 1:
        return [1.0]
    out: list[float] = []
    for i in range(n):
        if i == 0:
            out.append(max((pts[1].r - pts[0].r) / 2.0, 1e-9))
        elif i == n - 1:
            out.append(max((pts[-1].r - pts[-2].r) / 2.0, 1e-9))
        else:
            out.append(max((pts[i + 1].r - pts[i - 1].r) / 2.0, 1e-9))
    return out


def chi_profile(pts: list[Point]) -> list[float]:
    if not pts:
        return []
    m_enc = [p.bt * p.r for p in pts]
    mmax = max(m_enc)
    if mmax <= 0:
        return [0.0 for _ in pts]
    return [x / mmax for x in m_enc]


def s1_profile(pts: list[Point], s1_lambda: float) -> list[float]:
    chi = chi_profile(pts)
    lam = max(s1_lambda, 1e-9)
    return [math.exp(-abs(c - 1.0) / lam) for c in chi]


def kernel_features_for_galaxy(
    pts: list[Point],
    tau: float,
    alpha: float,
    s1_lambda: float,
    s2_const: float,
    r0_kpc: float,
) -> tuple[list[float], list[float]]:
    n = len(pts)
    if n == 0:
        return [], []
    if n == 1:
        src1 = pts[0].bt * math.exp(-abs(0.0 - 1.0) / max(s1_lambda, 1e-9))
        src2 = pts[0].bt * s2_const
        return [src1], [src2]

    drr = dr_list(pts)
    s1 = s1_profile(pts, s1_lambda)
    src1 = [pts[i].bt * s1[i] for i in range(n)]
    src2 = [pts[i].bt * s2_const for i in range(n)]

    tau_eff = max(tau, 1e-9)
    r0_eff = max(r0_kpc, 1e-9)

    h1: list[float] = []
    h2: list[float] = []
    for i in range(n):
        ri = pts[i].r
        num1 = 0.0
        den1 = 0.0
        num2 = 0.0
        den2 = 0.0
        for j in range(n):
            d = abs(ri - pts[j].r)
            w1 = math.exp(-d / tau_eff)
            w2 = 1.0 / (d + r0_eff) ** alpha
            dj = drr[j]
            num1 += w1 * src1[j] * dj
            den1 += w1 * dj
            num2 += w2 * src2[j] * dj
            den2 += w2 * dj
        h1.append(num1 / max(den1, 1e-18))
        h2.append(num2 / max(den2, 1e-18))
    return h1, h2


def mond_v(point: Point, g_dag: float) -> float:
    g_bar = point.bt / point.r
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    if denom <= 1e-15:
        g_obs = math.sqrt(g_bar * g_dag)
    else:
        g_obs = g_bar / denom
    return math.sqrt(max(g_obs * point.r, 0.0))


def golden_search(f, lo: float, hi: float, tol: float = 1e-6, max_iter: int = 200) -> tuple[float, float]:
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    a = lo
    b = hi
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc = f(c)
    fd = f(d)
    for _ in range(max_iter):
        if abs(b - a) < tol:
            break
        if fc < fd:
            b = d
            d = c
            fd = fc
            c = b - phi * (b - a)
            fc = f(c)
        else:
            a = c
            c = d
            fc = fd
            d = a + phi * (b - a)
            fd = f(d)
    x = c if fc < fd else d
    y = fc if fc < fd else fd
    return x, y


def chi2_null(points: list[Point]) -> float:
    return sum(((p.v - math.sqrt(max(p.bt, 0.0))) / p.ve) ** 2 for p in points)


def chi2_mond(points: list[Point], g_dag: float) -> float:
    return sum(((p.v - mond_v(p, g_dag)) / p.ve) ** 2 for p in points)


def fit_mond(points: list[Point]) -> tuple[float, float]:
    lo = 0.001 * A0_INTERNAL
    hi = 100.0 * A0_INTERNAL
    g, c2 = golden_search(lambda gg: chi2_mond(points, gg), lo, hi)
    return g, c2


def feature_rows(
    galaxies: dict[str, list[Point]],
    ids: set[str],
    tau: float,
    alpha: float,
    s1_lambda: float,
    s2_const: float,
    r0_kpc: float,
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for gid in sorted(ids):
        pts = galaxies[gid]
        h1, h2 = kernel_features_for_galaxy(pts, tau, alpha, s1_lambda, s2_const, r0_kpc)
        for i, p in enumerate(pts):
            rows.append(
                {
                    "gal": gid,
                    "r": p.r,
                    "v": p.v,
                    "ve": p.ve,
                    "bt": p.bt,
                    "h1": h1[i],
                    "h2": h2[i],
                }
            )
    return rows


def weighted_sse_v2(rows: list[dict[str, float | str]], k1: float, k2: float) -> float:
    total = 0.0
    for r in rows:
        v = float(r["v"])
        ve = float(r["ve"])
        bt = float(r["bt"])
        h1 = float(r["h1"])
        h2 = float(r["h2"])
        y = v * v
        pred = bt + k1 * h1 + k2 * h2
        sigma = max(2.0 * max(v, 1e-6) * ve, 1e-6)
        w = 1.0 / (sigma * sigma)
        d = y - pred
        total += w * d * d
    return total


def solve_nonneg_k(rows: list[dict[str, float | str]]) -> tuple[float, float, float]:
    a11 = 0.0
    a12 = 0.0
    a22 = 0.0
    b1 = 0.0
    b2 = 0.0
    for r in rows:
        v = float(r["v"])
        ve = float(r["ve"])
        bt = float(r["bt"])
        h1 = float(r["h1"])
        h2 = float(r["h2"])
        sigma = max(2.0 * max(v, 1e-6) * ve, 1e-6)
        w = 1.0 / (sigma * sigma)
        t = v * v - bt
        a11 += w * h1 * h1
        a12 += w * h1 * h2
        a22 += w * h2 * h2
        b1 += w * h1 * t
        b2 += w * h2 * t

    def k2_only() -> float:
        if a22 <= 1e-18:
            return 0.0
        return max(0.0, b2 / a22)

    def k1_only() -> float:
        if a11 <= 1e-18:
            return 0.0
        return max(0.0, b1 / a11)

    det = a11 * a22 - a12 * a12
    candidates: list[tuple[float, float]] = []
    if abs(det) > 1e-18:
        k1 = (b1 * a22 - b2 * a12) / det
        k2 = (a11 * b2 - a12 * b1) / det
        if k1 >= 0.0 and k2 >= 0.0:
            candidates.append((k1, k2))
    candidates.append((0.0, 0.0))
    candidates.append((k1_only(), 0.0))
    candidates.append((0.0, k2_only()))

    best = (0.0, 0.0, float("inf"))
    for k1, k2 in candidates:
        sse = weighted_sse_v2(rows, k1, k2)
        if sse < best[2]:
            best = (k1, k2, sse)
    return best


def chi2_dual(rows: list[dict[str, float | str]], params: DualParams) -> float:
    total = 0.0
    for r in rows:
        v = float(r["v"])
        ve = float(r["ve"])
        bt = float(r["bt"])
        h1 = float(r["h1"])
        h2 = float(r["h2"])
        pred_v2 = bt + params.k1 * h1 + params.k2 * h2
        pred_v = math.sqrt(max(pred_v2, 0.0))
        total += ((v - pred_v) / ve) ** 2
    return total


def safe_rate(numer: float, denom: int) -> float:
    return numer / max(1, denom)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    galaxies = read_data(Path(args.dataset_csv).resolve())
    galaxy_ids = sorted(galaxies.keys())
    train_ids, holdout_ids = train_holdout_split(galaxy_ids, args.seed, args.train_frac)

    train_points = [p for gid in sorted(train_ids) for p in galaxies[gid]]
    holdout_points = [p for gid in sorted(holdout_ids) for p in galaxies[gid]]

    g_dag, train_mond_chi2 = fit_mond(train_points)
    holdout_mond_chi2 = chi2_mond(holdout_points, g_dag)
    train_null_chi2 = chi2_null(train_points)
    holdout_null_chi2 = chi2_null(holdout_points)

    grid_rows: list[dict[str, Any]] = []
    best_params = DualParams(tau=tau_grid[0], alpha=alpha_grid[0], k1=0.0, k2=0.0)
    best_train_chi2 = float("inf")
    best_holdout_chi2 = float("inf")

    for tau in tau_grid:
        for alpha in alpha_grid:
            train_feats = feature_rows(
                galaxies,
                train_ids,
                tau=tau,
                alpha=alpha,
                s1_lambda=args.s1_lambda,
                s2_const=args.s2_const,
                r0_kpc=args.r0_kpc,
            )
            holdout_feats = feature_rows(
                galaxies,
                holdout_ids,
                tau=tau,
                alpha=alpha,
                s1_lambda=args.s1_lambda,
                s2_const=args.s2_const,
                r0_kpc=args.r0_kpc,
            )
            k1, k2, train_sse_v2 = solve_nonneg_k(train_feats)
            dp = DualParams(tau=tau, alpha=alpha, k1=k1, k2=k2)
            c2_train = chi2_dual(train_feats, dp)
            c2_hold = chi2_dual(holdout_feats, dp)

            grid_rows.append(
                {
                    "tau_kpc": f"{tau:.6f}",
                    "alpha": f"{alpha:.6f}",
                    "k1": f"{k1:.9f}",
                    "k2": f"{k2:.9f}",
                    "train_chi2": f"{c2_train:.6f}",
                    "train_chi2_per_n": f"{safe_rate(c2_train, len(train_feats)):.6f}",
                    "holdout_chi2": f"{c2_hold:.6f}",
                    "holdout_chi2_per_n": f"{safe_rate(c2_hold, len(holdout_feats)):.6f}",
                    "train_weighted_sse_v2": f"{train_sse_v2:.6f}",
                }
            )

            if c2_train < best_train_chi2:
                best_train_chi2 = c2_train
                best_holdout_chi2 = c2_hold
                best_params = dp

    best_train_feats = feature_rows(
        galaxies,
        train_ids,
        tau=best_params.tau,
        alpha=best_params.alpha,
        s1_lambda=args.s1_lambda,
        s2_const=args.s2_const,
        r0_kpc=args.r0_kpc,
    )
    best_holdout_feats = feature_rows(
        galaxies,
        holdout_ids,
        tau=best_params.tau,
        alpha=best_params.alpha,
        s1_lambda=args.s1_lambda,
        s2_const=args.s2_const,
        r0_kpc=args.r0_kpc,
    )
    best_train_chi2 = chi2_dual(best_train_feats, best_params)
    best_holdout_chi2 = chi2_dual(best_holdout_feats, best_params)

    train_dual_per_n = safe_rate(best_train_chi2, len(train_points))
    holdout_dual_per_n = safe_rate(best_holdout_chi2, len(holdout_points))
    train_null_per_n = safe_rate(train_null_chi2, len(train_points))
    holdout_null_per_n = safe_rate(holdout_null_chi2, len(holdout_points))
    train_mond_per_n = safe_rate(train_mond_chi2, len(train_points))
    holdout_mond_per_n = safe_rate(holdout_mond_chi2, len(holdout_points))

    train_improve_vs_null_pct = 100.0 * (train_null_chi2 - best_train_chi2) / max(train_null_chi2, 1e-12)
    holdout_improve_vs_null_pct = 100.0 * (holdout_null_chi2 - best_holdout_chi2) / max(holdout_null_chi2, 1e-12)

    aic_train = {
        "null": train_null_chi2 + 2 * 0,
        "mond": train_mond_chi2 + 2 * 1,
        "dual": best_train_chi2 + 2 * 4,
    }
    aic_holdout = {
        "null": holdout_null_chi2 + 2 * 0,
        "mond": holdout_mond_chi2 + 2 * 1,
        "dual": best_holdout_chi2 + 2 * 4,
    }
    bic_train = {
        "null": train_null_chi2 + 0 * math.log(max(1, len(train_points))),
        "mond": train_mond_chi2 + 1 * math.log(max(1, len(train_points))),
        "dual": best_train_chi2 + 4 * math.log(max(1, len(train_points))),
    }
    bic_holdout = {
        "null": holdout_null_chi2 + 0 * math.log(max(1, len(holdout_points))),
        "mond": holdout_mond_chi2 + 1 * math.log(max(1, len(holdout_points))),
        "dual": best_holdout_chi2 + 4 * math.log(max(1, len(holdout_points))),
    }

    summary = {
        "test_id": str(args.test_id),
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "dataset_id": args.dataset_id,
        "dataset_csv": str(Path(args.dataset_csv).resolve()),
        "split_seed": int(args.seed),
        "train_frac": float(args.train_frac),
        "n_galaxies_total": len(galaxy_ids),
        "n_galaxies_train": len(train_ids),
        "n_galaxies_holdout": len(holdout_ids),
        "n_points_train": len(train_points),
        "n_points_holdout": len(holdout_points),
        "fixed_theory_constants": {
            "s1_lambda": float(args.s1_lambda),
            "s2_const": float(args.s2_const),
            "r0_kpc": float(args.r0_kpc),
        },
        "search_space": {
            "tau_grid": tau_grid,
            "alpha_grid": alpha_grid,
        },
        "best_dual_params": {
            "tau_kpc": best_params.tau,
            "alpha": best_params.alpha,
            "k1": best_params.k1,
            "k2": best_params.k2,
        },
        "mond_fit": {
            "g_dag_internal_km2_s2_kpc": g_dag,
            "g_dag_m_s2": g_dag * G_UNIT,
        },
        "metrics": {
            "train": {
                "chi2_null": train_null_chi2,
                "chi2_mond": train_mond_chi2,
                "chi2_dual": best_train_chi2,
                "chi2_per_n_null": train_null_per_n,
                "chi2_per_n_mond": train_mond_per_n,
                "chi2_per_n_dual": train_dual_per_n,
                "improve_vs_null_pct": train_improve_vs_null_pct,
                "delta_chi2_dual_minus_mond": best_train_chi2 - train_mond_chi2,
                "delta_aic_dual_minus_mond": aic_train["dual"] - aic_train["mond"],
                "delta_bic_dual_minus_mond": bic_train["dual"] - bic_train["mond"],
            },
            "holdout": {
                "chi2_null": holdout_null_chi2,
                "chi2_mond": holdout_mond_chi2,
                "chi2_dual": best_holdout_chi2,
                "chi2_per_n_null": holdout_null_per_n,
                "chi2_per_n_mond": holdout_mond_per_n,
                "chi2_per_n_dual": holdout_dual_per_n,
                "improve_vs_null_pct": holdout_improve_vs_null_pct,
                "delta_chi2_dual_minus_mond": best_holdout_chi2 - holdout_mond_chi2,
                "delta_aic_dual_minus_mond": aic_holdout["dual"] - aic_holdout["mond"],
                "delta_bic_dual_minus_mond": bic_holdout["dual"] - bic_holdout["mond"],
            },
        },
        "decision_hint": "Use evaluator script with prereg criteria; no threshold/formula updates allowed.",
    }

    if args.write_artifacts:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "d4_stage2_dual_kernel_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        write_csv(
            out_dir / "grid_search_results.csv",
            grid_rows,
            [
                "tau_kpc",
                "alpha",
                "k1",
                "k2",
                "train_chi2",
                "train_chi2_per_n",
                "holdout_chi2",
                "holdout_chi2_per_n",
                "train_weighted_sse_v2",
            ],
        )
        model_rows = [
            {
                "split": "train",
                "model": "M0_null",
                "chi2": f"{train_null_chi2:.6f}",
                "chi2_per_n": f"{train_null_per_n:.6f}",
                "k_params": "0",
                "aic": f"{aic_train['null']:.6f}",
                "bic": f"{bic_train['null']:.6f}",
            },
            {
                "split": "train",
                "model": "M1_mond",
                "chi2": f"{train_mond_chi2:.6f}",
                "chi2_per_n": f"{train_mond_per_n:.6f}",
                "k_params": "1",
                "aic": f"{aic_train['mond']:.6f}",
                "bic": f"{bic_train['mond']:.6f}",
            },
            {
                "split": "train",
                "model": "M6_dual_kernel",
                "chi2": f"{best_train_chi2:.6f}",
                "chi2_per_n": f"{train_dual_per_n:.6f}",
                "k_params": "4",
                "aic": f"{aic_train['dual']:.6f}",
                "bic": f"{bic_train['dual']:.6f}",
            },
            {
                "split": "holdout",
                "model": "M0_null",
                "chi2": f"{holdout_null_chi2:.6f}",
                "chi2_per_n": f"{holdout_null_per_n:.6f}",
                "k_params": "0",
                "aic": f"{aic_holdout['null']:.6f}",
                "bic": f"{bic_holdout['null']:.6f}",
            },
            {
                "split": "holdout",
                "model": "M1_mond",
                "chi2": f"{holdout_mond_chi2:.6f}",
                "chi2_per_n": f"{holdout_mond_per_n:.6f}",
                "k_params": "1",
                "aic": f"{aic_holdout['mond']:.6f}",
                "bic": f"{bic_holdout['mond']:.6f}",
            },
            {
                "split": "holdout",
                "model": "M6_dual_kernel",
                "chi2": f"{best_holdout_chi2:.6f}",
                "chi2_per_n": f"{holdout_dual_per_n:.6f}",
                "k_params": "4",
                "aic": f"{aic_holdout['dual']:.6f}",
                "bic": f"{bic_holdout['dual']:.6f}",
            },
        ]
        write_csv(
            out_dir / "model_comparison.csv",
            model_rows,
            ["split", "model", "chi2", "chi2_per_n", "k_params", "aic", "bic"],
        )

        report_lines = [
            f"# D4 Stage-2 Dual-Kernel Report ({args.test_id})",
            "",
            f"- generated_utc: `{summary['timestamp_utc']}`",
            f"- dataset_id: `{args.dataset_id}`",
            f"- train/holdout galaxies: `{len(train_ids)}/{len(holdout_ids)}`",
            f"- train/holdout points: `{len(train_points)}/{len(holdout_points)}`",
            "",
            "## Best Dual Parameters",
            "",
            f"- tau_kpc: `{best_params.tau:.6f}`",
            f"- alpha: `{best_params.alpha:.6f}`",
            f"- k1: `{best_params.k1:.9f}`",
            f"- k2: `{best_params.k2:.9f}`",
            "",
            "## Holdout Metrics",
            "",
            f"- null chi2/N: `{holdout_null_per_n:.6f}`",
            f"- mond chi2/N: `{holdout_mond_per_n:.6f}`",
            f"- dual chi2/N: `{holdout_dual_per_n:.6f}`",
            f"- improve_vs_null_pct: `{holdout_improve_vs_null_pct:.6f}`",
            f"- delta_chi2_dual_minus_mond: `{best_holdout_chi2 - holdout_mond_chi2:.6f}`",
            "",
            "## Notes",
            "",
            "- Fixed split and fixed grids (pre-registered anti post-hoc policy).",
            "- Global parameters only (no per-galaxy tuning).",
            "- Kernels use radius + baryon_term only.",
        ]
        (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"summary_json: {out_dir / 'd4_stage2_dual_kernel_summary.json'}")
    print(f"model_comparison_csv: {out_dir / 'model_comparison.csv'}")
    print(f"best_tau_alpha: {best_params.tau:.6f}, {best_params.alpha:.6f}")
    print(f"holdout_chi2_per_n_dual: {holdout_dual_per_n:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
