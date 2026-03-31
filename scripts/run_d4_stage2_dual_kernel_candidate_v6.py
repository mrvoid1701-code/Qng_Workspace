#!/usr/bin/env python3
"""
D4 Stage-2 dual-kernel candidate v6 (multi-split prereg run).

Purpose:
- evaluate one reduced-DOF candidate (single amplitude + fixed mix grid)
- keep anti post-hoc governance: fixed split seeds + fixed grids + fixed constants
- fit on chi2 in velocity-space (v) with low-accel/outer emphasis
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-dual-kernel-v6-candidate"

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


def parse_list(raw: str) -> list[float]:
    out: list[float] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(float(t))
    return out


def parse_int_list(raw: str) -> list[int]:
    out: list[int] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(int(t))
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run D4 Stage-2 candidate formula v6 on multi-split prereg.")
    p.add_argument("--test-id", default="d4-stage2-dual-kernel-v6-candidate")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--split-seeds", default="3401,3402,3403,3404,3405")
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--s1-lambda", type=float, default=0.28)
    p.add_argument("--s2-const", type=float, default=0.355)
    p.add_argument("--r0-kpc", type=float, default=1.0)
    p.add_argument("--r-tail-kpc", type=float, default=4.0)
    p.add_argument("--tau-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--alpha-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3")
    p.add_argument("--mix-grid", default="0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0")
    p.add_argument("--candidates", default="outer_single_mix_v6")
    p.add_argument("--focus-gamma", type=float, default=2.0)
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


def make_rows_for_ids(
    galaxies: dict[str, list[Point]],
    ids: set[str],
    tau: float,
    alpha: float,
    s1_lambda: float,
    s2_const: float,
    r0_kpc: float,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for gid in sorted(ids):
        pts = galaxies[gid]
        h1, h2 = kernel_features_for_galaxy(pts, tau, alpha, s1_lambda, s2_const, r0_kpc)
        for i, p in enumerate(pts):
            rows.append(
                {
                    "r": p.r,
                    "v": p.v,
                    "ve": p.ve,
                    "bt": p.bt,
                    "h1": h1[i],
                    "h2": h2[i],
                }
            )
    return rows


def mix_column(rows: list[dict[str, float]], mix: float, r_tail_kpc: float, a0_internal: float) -> list[float]:
    m = max(0.0, min(1.0, float(mix)))
    outer = [
        r["h2"]
        * (r["r"] / max(r["r"] + r_tail_kpc, 1e-12))
        / math.sqrt(1.0 + (r["bt"] / max(r["r"], 1e-12)) / max(a0_internal, 1e-30))
        for r in rows
    ]
    return [(1.0 - m) * r["h1"] + m * outer[i] for i, r in enumerate(rows)]


def nnls_coordinate_descent(
    cols: list[list[float]],
    y: list[float],
    w: list[float],
    max_iter: int = 200,
    tol: float = 1e-10,
) -> list[float]:
    p = len(cols)
    n = len(y)
    k = [0.0] * p
    # precompute denominators
    den = []
    for j in range(p):
        d = 0.0
        cj = cols[j]
        for i in range(n):
            d += w[i] * cj[i] * cj[i]
        den.append(max(d, 1e-18))

    for _ in range(max_iter):
        max_delta = 0.0
        for j in range(p):
            num = 0.0
            cj = cols[j]
            for i in range(n):
                pred_except_j = 0.0
                for l in range(p):
                    if l == j:
                        continue
                    pred_except_j += cols[l][i] * k[l]
                resid_j = y[i] - pred_except_j
                num += w[i] * cj[i] * resid_j
            new_kj = max(0.0, num / den[j])
            max_delta = max(max_delta, abs(new_kj - k[j]))
            k[j] = new_kj
        if max_delta < tol:
            break
    return k


def weighted_sse_v2(rows: list[dict[str, float]], coeffs: list[float], cols: list[list[float]]) -> float:
    total = 0.0
    for i, r in enumerate(rows):
        y = r["v"] * r["v"] - r["bt"]
        pred = 0.0
        for j, c in enumerate(cols):
            pred += coeffs[j] * c[i]
        sigma = max(2.0 * max(r["v"], 1e-6) * r["ve"], 1e-6)
        ww = 1.0 / (sigma * sigma)
        d = y - pred
        total += ww * d * d
    return total


def chi2_candidate(rows: list[dict[str, float]], coeffs: list[float], cols: list[list[float]]) -> float:
    total = 0.0
    for i, r in enumerate(rows):
        pred_v2 = r["bt"]
        for j, c in enumerate(cols):
            pred_v2 += coeffs[j] * c[i]
        pred_v = math.sqrt(max(pred_v2, 0.0))
        total += ((r["v"] - pred_v) / r["ve"]) ** 2
    return total


def golden_search_1d(f, lo: float, hi: float, tol: float = 1e-6, max_iter: int = 80) -> tuple[float, float]:
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


def fit_nonneg_chi2_v(
    rows: list[dict[str, float]],
    cols: list[list[float]],
    focus_gamma: float,
    r_tail_kpc: float,
    a0_internal: float,
    max_outer_iter: int = 18,
    tol: float = 1e-7,
) -> list[float]:
    p = len(cols)
    k = [0.0] * p

    def obj(v: list[float]) -> float:
        return chi2_focus_candidate(rows, v, cols, focus_gamma, r_tail_kpc, a0_internal)

    prev = obj(k)
    for _ in range(max_outer_iter):
        max_delta = 0.0
        for j in range(p):
            base = list(k)

            def f1(x: float) -> float:
                vv = list(base)
                vv[j] = max(0.0, x)
                return obj(vv)

            f0 = f1(base[j])
            hi = max(1.0, base[j] * 2.0 + 1e-6)
            fhi = f1(hi)
            # Expand bracket if objective still decreases at boundary.
            while fhi < f0 and hi < 1e6:
                hi *= 2.0
                fhi = f1(hi)
            x_best, _ = golden_search_1d(f1, 0.0, hi, tol=1e-6, max_iter=80)
            x_best = max(0.0, x_best)
            max_delta = max(max_delta, abs(x_best - k[j]))
            k[j] = x_best
        cur = obj(k)
        if abs(prev - cur) < tol and max_delta < tol:
            break
        prev = cur
    return k


def safe_rate(numer: float, denom: int) -> float:
    return numer / max(1, denom)


def f6(x: float) -> str:
    return f"{x:.6f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def focus_weight(row: dict[str, float], focus_gamma: float, r_tail_kpc: float, a0_internal: float) -> float:
    outer = row["r"] / max(row["r"] + r_tail_kpc, 1e-12)
    lowacc = 1.0 / math.sqrt(1.0 + (row["bt"] / max(row["r"], 1e-12)) / max(a0_internal, 1e-30))
    return 1.0 + max(focus_gamma, 0.0) * outer * lowacc


def chi2_focus_candidate(
    rows: list[dict[str, float]],
    coeffs: list[float],
    cols: list[list[float]],
    focus_gamma: float,
    r_tail_kpc: float,
    a0_internal: float,
) -> float:
    total = 0.0
    for i, r in enumerate(rows):
        pred_v2 = r["bt"]
        for j, c in enumerate(cols):
            pred_v2 += coeffs[j] * c[i]
        pred_v = math.sqrt(max(pred_v2, 0.0))
        d = (r["v"] - pred_v) / r["ve"]
        total += focus_weight(r, focus_gamma, r_tail_kpc, a0_internal) * d * d
    return total


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset_csv).resolve()
    out_dir = Path(args.outdir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        dataset_csv_rel = dataset_path.relative_to(ROOT).as_posix()
    except ValueError:
        dataset_csv_rel = dataset_path.name
    dataset_sha256 = sha256_file(dataset_path)

    split_seeds = parse_int_list(args.split_seeds)
    tau_grid = parse_list(args.tau_grid)
    alpha_grid = parse_list(args.alpha_grid)
    mix_grid = parse_list(args.mix_grid)
    if not mix_grid:
        raise ValueError("mix-grid must not be empty")
    candidates = [x.strip() for x in str(args.candidates).split(",") if x.strip()]
    for c in candidates:
        if c not in {"outer_single_mix_v6"}:
            raise ValueError(f"unsupported candidate: {c}")

    galaxies = read_data(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    per_seed_rows: list[dict[str, Any]] = []
    for split_seed in split_seeds:
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, split_seed, args.train_frac)
        train_points = [p for gid in sorted(train_ids) for p in galaxies[gid]]
        holdout_points = [p for gid in sorted(holdout_ids) for p in galaxies[gid]]

        g_dag, train_mond_chi2 = fit_mond(train_points)
        holdout_mond_chi2 = chi2_mond(holdout_points, g_dag)
        train_null_chi2 = chi2_null(train_points)
        holdout_null_chi2 = chi2_null(holdout_points)

        for candidate in candidates:
            best_train_focus_chi2 = float("inf")
            best_train_chi2 = float("inf")
            best_holdout_chi2 = float("inf")
            best_tau = tau_grid[0]
            best_alpha = alpha_grid[0]
            best_mix = mix_grid[0]
            best_coeffs: list[float] = []

            for tau in tau_grid:
                for alpha in alpha_grid:
                    train_rows = make_rows_for_ids(
                        galaxies=galaxies,
                        ids=train_ids,
                        tau=tau,
                        alpha=alpha,
                        s1_lambda=args.s1_lambda,
                        s2_const=args.s2_const,
                        r0_kpc=args.r0_kpc,
                    )
                    holdout_rows = make_rows_for_ids(
                        galaxies=galaxies,
                        ids=holdout_ids,
                        tau=tau,
                        alpha=alpha,
                        s1_lambda=args.s1_lambda,
                        s2_const=args.s2_const,
                        r0_kpc=args.r0_kpc,
                    )
                    for mix in mix_grid:
                        train_cols = [mix_column(train_rows, mix, args.r_tail_kpc, A0_INTERNAL)]
                        holdout_cols = [mix_column(holdout_rows, mix, args.r_tail_kpc, A0_INTERNAL)]
                        coeffs = fit_nonneg_chi2_v(
                            train_rows,
                            train_cols,
                            focus_gamma=float(args.focus_gamma),
                            r_tail_kpc=float(args.r_tail_kpc),
                            a0_internal=A0_INTERNAL,
                        )

                        train_focus_chi2 = chi2_focus_candidate(
                            train_rows,
                            coeffs,
                            train_cols,
                            focus_gamma=float(args.focus_gamma),
                            r_tail_kpc=float(args.r_tail_kpc),
                            a0_internal=A0_INTERNAL,
                        )
                        train_chi2 = chi2_candidate(train_rows, coeffs, train_cols)
                        holdout_chi2 = chi2_candidate(holdout_rows, coeffs, holdout_cols)

                        # Selection is locked to focused train objective from prereg.
                        if train_focus_chi2 < best_train_focus_chi2:
                            best_train_focus_chi2 = train_focus_chi2
                            best_train_chi2 = train_chi2
                            best_holdout_chi2 = holdout_chi2
                            best_tau = tau
                            best_alpha = alpha
                            best_mix = mix
                            best_coeffs = coeffs

            train_focus_dual_per_n = safe_rate(best_train_focus_chi2, len(train_points))
            train_dual_per_n = safe_rate(best_train_chi2, len(train_points))
            holdout_dual_per_n = safe_rate(best_holdout_chi2, len(holdout_points))
            train_null_per_n = safe_rate(train_null_chi2, len(train_points))
            holdout_null_per_n = safe_rate(holdout_null_chi2, len(holdout_points))
            train_mond_per_n = safe_rate(train_mond_chi2, len(train_points))
            holdout_mond_per_n = safe_rate(holdout_mond_chi2, len(holdout_points))

            train_improve_vs_null_pct = 100.0 * (train_null_chi2 - best_train_chi2) / max(train_null_chi2, 1e-12)
            holdout_improve_vs_null_pct = 100.0 * (holdout_null_chi2 - best_holdout_chi2) / max(
                holdout_null_chi2, 1e-12
            )
            holdout_mond_worse_pct = 100.0 * (holdout_dual_per_n - holdout_mond_per_n) / max(
                holdout_mond_per_n, 1e-12
            )
            train_mond_worse_pct = 100.0 * (train_dual_per_n - train_mond_per_n) / max(train_mond_per_n, 1e-12)
            generalization_gap = abs(train_improve_vs_null_pct - holdout_improve_vs_null_pct)

            k_coef = len(best_coeffs)
            # v6 searches (tau, alpha, mix) and then fits nonnegative coefficients.
            k_params = 3 + k_coef
            holdout_delta_aic = (best_holdout_chi2 + 2 * k_params) - (holdout_mond_chi2 + 2 * 1)
            holdout_delta_bic = (best_holdout_chi2 + k_params * math.log(max(1, len(holdout_points)))) - (
                holdout_mond_chi2 + 1 * math.log(max(1, len(holdout_points)))
            )

            row = {
                "test_id": str(args.test_id),
                "dataset_id": str(args.dataset_id),
                "dataset_csv_rel": dataset_csv_rel,
                "dataset_sha256": dataset_sha256,
                "split_seed": str(split_seed),
                "candidate": candidate,
                "n_points_train": str(len(train_points)),
                "n_points_holdout": str(len(holdout_points)),
                "best_tau_kpc": f6(best_tau),
                "best_alpha": f6(best_alpha),
                "best_mix": f6(best_mix),
                "best_k1": f6(best_coeffs[0] if len(best_coeffs) > 0 else 0.0),
                "best_k2": f6(best_coeffs[1] if len(best_coeffs) > 1 else 0.0),
                "best_k3": f6(best_coeffs[2] if len(best_coeffs) > 2 else 0.0),
                "train_focus_chi2_per_n_dual": f6(train_focus_dual_per_n),
                "train_chi2_per_n_dual": f6(train_dual_per_n),
                "train_chi2_per_n_mond": f6(train_mond_per_n),
                "train_chi2_per_n_null": f6(train_null_per_n),
                "holdout_chi2_per_n_dual": f6(holdout_dual_per_n),
                "holdout_chi2_per_n_mond": f6(holdout_mond_per_n),
                "holdout_chi2_per_n_null": f6(holdout_null_per_n),
                "holdout_improve_vs_null_pct": f6(holdout_improve_vs_null_pct),
                "holdout_mond_worse_pct": f6(holdout_mond_worse_pct),
                "train_mond_worse_pct": f6(train_mond_worse_pct),
                "generalization_gap_pp": f6(generalization_gap),
                "holdout_delta_aic_dual_minus_mond": f6(holdout_delta_aic),
                "holdout_delta_bic_dual_minus_mond": f6(holdout_delta_bic),
            }
            per_seed_rows.append(row)

    per_seed_fields = [
        "test_id",
        "dataset_id",
        "dataset_csv_rel",
        "dataset_sha256",
        "split_seed",
        "candidate",
        "n_points_train",
        "n_points_holdout",
        "best_tau_kpc",
        "best_alpha",
        "best_mix",
        "best_k1",
        "best_k2",
        "best_k3",
        "train_focus_chi2_per_n_dual",
        "train_chi2_per_n_dual",
        "train_chi2_per_n_mond",
        "train_chi2_per_n_null",
        "holdout_chi2_per_n_dual",
        "holdout_chi2_per_n_mond",
        "holdout_chi2_per_n_null",
        "holdout_improve_vs_null_pct",
        "holdout_mond_worse_pct",
        "train_mond_worse_pct",
        "generalization_gap_pp",
        "holdout_delta_aic_dual_minus_mond",
        "holdout_delta_bic_dual_minus_mond",
    ]
    write_csv(out_dir / "per_seed_candidate_summary.csv", per_seed_rows, per_seed_fields)

    # Aggregate by candidate.
    agg_rows: list[dict[str, Any]] = []
    for candidate in sorted(set(r["candidate"] for r in per_seed_rows)):
        rows = [r for r in per_seed_rows if r["candidate"] == candidate]
        n = len(rows)

        def avg(field: str) -> float:
            return sum(float(r[field]) for r in rows) / max(n, 1)

        agg_rows.append(
            {
                "candidate": candidate,
                "n_splits": str(n),
                "avg_best_mix": f6(avg("best_mix")),
                "avg_train_focus_chi2_per_n_dual": f6(avg("train_focus_chi2_per_n_dual")),
                "avg_holdout_chi2_per_n_dual": f6(avg("holdout_chi2_per_n_dual")),
                "avg_holdout_chi2_per_n_mond": f6(avg("holdout_chi2_per_n_mond")),
                "avg_holdout_improve_vs_null_pct": f6(avg("holdout_improve_vs_null_pct")),
                "avg_holdout_mond_worse_pct": f6(avg("holdout_mond_worse_pct")),
                "avg_holdout_delta_aic_dual_minus_mond": f6(avg("holdout_delta_aic_dual_minus_mond")),
                "avg_holdout_delta_bic_dual_minus_mond": f6(avg("holdout_delta_bic_dual_minus_mond")),
                "avg_generalization_gap_pp": f6(avg("generalization_gap_pp")),
            }
        )
    agg_fields = [
        "candidate",
        "n_splits",
        "avg_best_mix",
        "avg_train_focus_chi2_per_n_dual",
        "avg_holdout_chi2_per_n_dual",
        "avg_holdout_chi2_per_n_mond",
        "avg_holdout_improve_vs_null_pct",
        "avg_holdout_mond_worse_pct",
        "avg_holdout_delta_aic_dual_minus_mond",
        "avg_holdout_delta_bic_dual_minus_mond",
        "avg_generalization_gap_pp",
    ]
    write_csv(out_dir / "aggregate_summary.csv", agg_rows, agg_fields)

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "test_id": str(args.test_id),
        "dataset_id": str(args.dataset_id),
        "dataset_csv_rel": dataset_csv_rel,
        "dataset_sha256": dataset_sha256,
        "split_seeds": split_seeds,
        "train_frac": float(args.train_frac),
        "fixed_theory_constants": {
            "s1_lambda": float(args.s1_lambda),
            "s2_const": float(args.s2_const),
            "r0_kpc": float(args.r0_kpc),
            "r_tail_kpc": float(args.r_tail_kpc),
        },
        "search_space": {
            "tau_grid": tau_grid,
            "alpha_grid": alpha_grid,
            "mix_grid": mix_grid,
        },
        "fit_objective": {
            "space": "velocity chi2",
            "focus_gamma": float(args.focus_gamma),
            "focus_formula": "1 + gamma * (r/(r+r_tail)) * 1/sqrt(1+gbar/a0)",
            "grid_selection_objective": "train_focus_chi2",
        },
        "candidates": candidates,
        "artifacts": {
            "per_seed_candidate_summary_csv": "per_seed_candidate_summary.csv",
            "aggregate_summary_csv": "aggregate_summary.csv",
            "report_md": "report.md",
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    lines = [
        "# D4 Stage-2 Candidate Formula v6 Report",
        "",
        f"- generated_utc: `{manifest['generated_utc']}`",
        f"- dataset_id: `{args.dataset_id}`",
        f"- split_seeds: `{','.join(str(s) for s in split_seeds)}`",
        f"- candidates: `{','.join(candidates)}`",
        "",
        "## Aggregate Summary",
        "",
    ]
    for row in agg_rows:
        lines.append(
            f"- `{row['candidate']}`: holdout dual={row['avg_holdout_chi2_per_n_dual']}, "
            f"holdout mond={row['avg_holdout_chi2_per_n_mond']}, "
            f"holdout_mond_worse_pct={row['avg_holdout_mond_worse_pct']}, "
            f"deltaAIC={row['avg_holdout_delta_aic_dual_minus_mond']}, "
            f"deltaBIC={row['avg_holdout_delta_bic_dual_minus_mond']}"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"per_seed_csv: {(out_dir / 'per_seed_candidate_summary.csv').as_posix()}")
    print(f"aggregate_csv: {(out_dir / 'aggregate_summary.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
