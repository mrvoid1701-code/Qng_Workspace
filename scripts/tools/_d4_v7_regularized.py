#!/usr/bin/env python3
"""Shared helpers for D4 v7 regularized lanes."""

from __future__ import annotations

import math
from typing import Any

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import (
    A0_INTERNAL,
    chi2_candidate,
    chi2_focus_candidate,
    f6,
    golden_search_1d,
    kernel_features_for_galaxy,
)


def make_rows_with_gid(
    galaxies: dict[str, list[Any]],
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
                    "gid": gid,
                    "r": p.r,
                    "v": p.v,
                    "ve": p.ve,
                    "bt": p.bt,
                    "h1": h1[i],
                    "h2": h2[i],
                }
            )
    return rows


def outer_component(rows: list[dict[str, float]], r_tail_kpc: float, a0_internal: float = A0_INTERNAL) -> list[float]:
    out: list[float] = []
    for r in rows:
        gbar = (r["bt"] / max(r["r"], 1e-12)) / max(a0_internal, 1e-30)
        val = r["h2"] * (r["r"] / max(r["r"] + r_tail_kpc, 1e-12)) / math.sqrt(1.0 + gbar)
        out.append(val)
    return out


def design_columns_v7(rows: list[dict[str, float]], r_tail_kpc: float, a0_internal: float = A0_INTERNAL) -> list[list[float]]:
    return [[r["h1"] for r in rows], outer_component(rows, r_tail_kpc, a0_internal)]


def predict_v2(rows: list[dict[str, float]], coeffs: list[float], cols: list[list[float]]) -> list[float]:
    out: list[float] = []
    for i, r in enumerate(rows):
        v2 = r["bt"]
        for j, c in enumerate(cols):
            v2 += coeffs[j] * c[i]
        out.append(v2)
    return out


def smooth_penalty(rows: list[dict[str, float]], pred_v2: list[float], a0_internal: float = A0_INTERNAL) -> float:
    if len(rows) <= 1:
        return 0.0
    total = 0.0
    count = 0
    prev_gid = str(rows[0]["gid"])
    prev_gextra = (pred_v2[0] - rows[0]["bt"]) / max(rows[0]["r"], 1e-12)
    for i in range(1, len(rows)):
        gid = str(rows[i]["gid"])
        gextra = (pred_v2[i] - rows[i]["bt"]) / max(rows[i]["r"], 1e-12)
        if gid == prev_gid:
            d = (gextra - prev_gextra) / max(a0_internal, 1e-30)
            total += d * d
            count += 1
        prev_gid = gid
        prev_gextra = gextra
    return total / max(1, count)


def train_objective_j(
    rows: list[dict[str, float]],
    coeffs: list[float],
    cols: list[list[float]],
    focus_gamma: float,
    r_tail_kpc: float,
    lambda_s: float,
    lambda_e: float,
    tau_on_edge: bool,
    alpha_on_edge: bool,
    a0_internal: float = A0_INTERNAL,
) -> float:
    chi2_focus = chi2_focus_candidate(rows, coeffs, cols, focus_gamma, r_tail_kpc, a0_internal)
    p2 = predict_v2(rows, coeffs, cols)
    r_smooth = smooth_penalty(rows, p2, a0_internal)
    r_edge = float(tau_on_edge) + float(alpha_on_edge)
    return chi2_focus + max(0.0, lambda_s) * r_smooth + max(0.0, lambda_e) * r_edge


def fit_nonneg_objective_j(
    rows: list[dict[str, float]],
    cols: list[list[float]],
    focus_gamma: float,
    r_tail_kpc: float,
    lambda_s: float,
    lambda_e: float,
    tau_on_edge: bool,
    alpha_on_edge: bool,
    a0_internal: float = A0_INTERNAL,
    max_outer_iter: int = 18,
    tol: float = 1e-7,
) -> list[float]:
    p = len(cols)
    k = [0.0] * p

    def obj(v: list[float]) -> float:
        return train_objective_j(
            rows=rows,
            coeffs=v,
            cols=cols,
            focus_gamma=focus_gamma,
            r_tail_kpc=r_tail_kpc,
            lambda_s=lambda_s,
            lambda_e=lambda_e,
            tau_on_edge=tau_on_edge,
            alpha_on_edge=alpha_on_edge,
            a0_internal=a0_internal,
        )

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


def edge_flags(tau: float, alpha: float, tau_grid: list[float], alpha_grid: list[float]) -> tuple[bool, bool]:
    tau_min = min(tau_grid)
    tau_max = max(tau_grid)
    alpha_min = min(alpha_grid)
    alpha_max = max(alpha_grid)
    tau_edge = abs(tau - tau_min) <= 1e-12 or abs(tau - tau_max) <= 1e-12
    alpha_edge = abs(alpha - alpha_min) <= 1e-12 or abs(alpha - alpha_max) <= 1e-12
    return tau_edge, alpha_edge


def count_active(coeffs: list[float], eps: float = 1e-9) -> int:
    return sum(1 for x in coeffs if float(x) > eps)


def evaluate_candidate_point(
    train_rows: list[dict[str, float]],
    holdout_rows: list[dict[str, float]],
    train_cols: list[list[float]],
    holdout_cols: list[list[float]],
    focus_gamma: float,
    r_tail_kpc: float,
    lambda_s: float,
    lambda_e: float,
    tau_on_edge: bool,
    alpha_on_edge: bool,
    holdout_mond_per_n: float,
    n_train_points: int,
    n_holdout_points: int,
) -> dict[str, Any]:
    coeffs = fit_nonneg_objective_j(
        rows=train_rows,
        cols=train_cols,
        focus_gamma=focus_gamma,
        r_tail_kpc=r_tail_kpc,
        lambda_s=lambda_s,
        lambda_e=lambda_e,
        tau_on_edge=tau_on_edge,
        alpha_on_edge=alpha_on_edge,
    )
    train_obj = train_objective_j(
        rows=train_rows,
        coeffs=coeffs,
        cols=train_cols,
        focus_gamma=focus_gamma,
        r_tail_kpc=r_tail_kpc,
        lambda_s=lambda_s,
        lambda_e=lambda_e,
        tau_on_edge=tau_on_edge,
        alpha_on_edge=alpha_on_edge,
    )
    train_focus = chi2_focus_candidate(train_rows, coeffs, train_cols, focus_gamma, r_tail_kpc, A0_INTERNAL)
    train_chi2 = chi2_candidate(train_rows, coeffs, train_cols)
    holdout_chi2 = chi2_candidate(holdout_rows, coeffs, holdout_cols)
    holdout_dual_per_n = holdout_chi2 / max(1, n_holdout_points)
    holdout_mond_worse = 100.0 * (holdout_dual_per_n - holdout_mond_per_n) / max(holdout_mond_per_n, 1e-12)
    return {
        "coeffs": coeffs,
        "train_objective_j_per_n": train_obj / max(1, n_train_points),
        "train_focus_chi2_per_n_dual": train_focus / max(1, n_train_points),
        "train_chi2_per_n_dual": train_chi2 / max(1, n_train_points),
        "holdout_chi2_per_n_dual": holdout_dual_per_n,
        "holdout_mond_worse_pct": holdout_mond_worse,
    }


__all__ = [
    "A0_INTERNAL",
    "chi2_candidate",
    "chi2_focus_candidate",
    "count_active",
    "design_columns_v7",
    "edge_flags",
    "evaluate_candidate_point",
    "f6",
    "make_rows_with_gid",
]

