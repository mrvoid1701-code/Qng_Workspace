#!/usr/bin/env python3
"""
QNG-T-CURL-003-v2: Discrete curl test with spatially-varying metric per chart point.

Pre-registration: 05_validation/pre-registrations/qng-t-curl-003-v2.md

Key change from CURL-002:
  CURL-002 FAIL root cause: a_lag = -tau * g_anchor^{-1} * H_anchor * v  => constant vector
  at all chart points => zero curl by construction (constant-metric approximation).

  This version fixes that by computing g(x_k) AND H(x_k) at each chart node via a
  LOCAL SUB-QUADRATIC FIT centered at that node, using its n_sub nearest chart neighbours.
  Now a_lag(x_k) = -tau * g^{-1}(x_k) * H(x_k) * v varies across the chart => curl != 0.

  Static baseline (C1): still uses constant anchor metric + quadratic-varying grad
  => curl_static ~ 0 (same as CURL-002 C1 PASS).

Gates (must be written in prereg before run — already done):
  C1: median(curl_rel_static)  < 1e-8
  C2: median(curl_rel_lag_iso) > 10 * median(curl_rel_static)
  C3: median(curl_rel_rewired) > 10 * median(curl_rel_static)
  FINAL: C1 AND C2 AND C3

Usage:
  python run_qng_t_curl_003_v2.py --dataset DS-002 --out-dir <path>
  python run_qng_t_curl_003_v2.py --dataset DS-002 --dataset DS-003 --dataset DS-006

Anti-tuning:
  If gates fail, next version must be curl-003-v3 with fresh prereg; thresholds frozen.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import math
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

SCRIPT_VERSION = "curl-003-v2"
ROOT = Path(__file__).resolve().parent.parent

DEFAULT_OUT_BASE = ROOT / "05_validation" / "evidence" / "artifacts"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class Config:
    dataset_id: str = "DS-002"
    seed: int = 20260225
    samples: int = 72
    local_m: int = 20          # chart nodes per anchor
    n_sub: int = 10            # nearest nodes for per-point Hessian fit
    tau_test: float = 1.0
    v_iso: tuple[float, float] = (1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0))
    v_grad: tuple[float, float] = (1.0 / math.sqrt(1.25), 0.5 / math.sqrt(1.25))
    rewire_fraction: float = 0.40
    a_epsilon: float = 1e-12
    # Gate thresholds (locked in prereg)
    c1_static_max: float = 1e-8
    c2_lag_factor_min: float = 10.0
    c3_rewire_factor_min: float = 10.0
    anisotropy_keep: float = 0.4
    frob_floor: float = 1e-9
    ridge_lam: float = 1e-8
    min_chart_nodes: int = 10


# ---------------------------------------------------------------------------
# Pure math utilities (stdlib only, no numpy)
# ---------------------------------------------------------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def frob_norm2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


def inv2x2(g11: float, g12: float, g22: float) -> Optional[tuple[float, float, float]]:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    return g22 / det, -g12 / det, g11 / det  # inv11, inv12, inv22


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    """Gauss-Jordan with partial pivoting."""
    n = len(b)
    aug = [[a[i][j] for j in range(n)] + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-18:
            raise ValueError("Singular.")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        pv = aug[col][col]
        for j in range(col, n + 1):
            aug[col][j] /= pv
        for r in range(n):
            if r == col:
                continue
            fac = aug[r][col]
            if fac == 0.0:
                continue
            for j in range(col, n + 1):
                aug[r][j] -= fac * aug[col][j]
    return [aug[i][n] for i in range(n)]


def fit_ridge(features: list[list[float]], targets: list[float], lam: float = 1e-9) -> list[float]:
    if not features:
        raise ValueError("No features.")
    p = len(features[0])
    a = [[0.0] * p for _ in range(p)]
    b = [0.0] * p
    for x, y in zip(features, targets):
        for i in range(p):
            b[i] += x[i] * y
            for j in range(p):
                a[i][j] += x[i] * x[j]
    for i in range(p):
        a[i][i] += lam
    return solve_linear_system(a, b)


def eig2x2(g11: float, g12: float, g22: float) -> tuple[float, float]:
    tr = g11 + g22
    det = g11 * g22 - g12 * g12
    disc = max(tr * tr - 4.0 * det, 0.0)
    root = math.sqrt(disc)
    l1 = 0.5 * (tr - root)
    l2 = 0.5 * (tr + root)
    return (l1, l2) if l1 <= l2 else (l2, l1)


# ---------------------------------------------------------------------------
# Graph construction (identical to run_qng_metric_hardening_v4.py)
# ---------------------------------------------------------------------------

def build_dataset_graph(
    dataset_id: str, seed: int
) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float]:
    rng = random.Random(seed + 17)
    ds = dataset_id.upper().strip()
    if ds == "DS-002":
        n, k, spread = 280, 8, 2.3
    elif ds == "DS-003":
        n, k, spread = 240, 7, 2.0
    elif ds == "DS-006":
        n, k, spread = 320, 9, 2.7
    else:
        n, k, spread = 260, 8, 2.2

    coords: list[tuple[float, float]] = []
    for _ in range(n):
        coords.append((rng.uniform(-spread, spread), rng.uniform(-spread, spread)))

    sigma: list[float] = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(clamp(s, 0.0, 1.0))

    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.hypot(xi - xj, yi - yj)
            dist[i][j] = d
            dist[j][i] = d

    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    edge_lengths: list[float] = []
    for i in range(n):
        neigh = sorted(range(n), key=lambda j: dist[i][j] if j != i else float("inf"))[:k]
        for j in neigh:
            base = max(dist[i][j], 1e-6)
            w = base * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)

    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    median_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, sigma, adj_list, max(median_edge, 1e-9)


def dijkstra(adj: list[list[tuple[int, float]]], src: int) -> list[float]:
    inf = float("inf")
    d = [inf] * len(adj)
    d[src] = 0.0
    pq: list[tuple[float, int]] = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u]:
            continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v]:
                d[v] = nd
                heapq.heappush(pq, (nd, v))
    return d


def choose_anchors(sigma: list[float], samples: int, seed: int) -> list[int]:
    rng = random.Random(seed + 71)
    n = len(sigma)
    target = max(8, min(samples, n))
    idx_sorted = sorted(range(n), key=lambda i: sigma[i], reverse=True)
    anchors = set(idx_sorted[: target // 2])
    bins: list[list[int]] = [[], [], [], []]
    s_sorted = sorted(sigma)
    q1 = s_sorted[int(0.25 * (n - 1))]
    q2 = s_sorted[int(0.50 * (n - 1))]
    q3 = s_sorted[int(0.75 * (n - 1))]
    for i, s in enumerate(sigma):
        bins[0 if s <= q1 else 1 if s <= q2 else 2 if s <= q3 else 3].append(i)
    while len(anchors) < target:
        b = bins[len(anchors) % 4] or list(range(n))
        anchors.add(b[rng.randrange(len(b))])
    return list(anchors)


def local_nodes_from_anchor(d: list[float], anchor: int, m: int) -> list[int]:
    ranked = sorted(range(len(d)), key=lambda i: d[i])
    out = [anchor]
    for i in ranked:
        if i == anchor:
            continue
        out.append(i)
        if len(out) >= m:
            break
    return out


def local_pairwise_distances(
    adj: list[list[tuple[int, float]]], local_nodes: list[int]
) -> list[list[float]]:
    d_all = [dijkstra(adj, node) for node in local_nodes]
    m = len(local_nodes)
    return [[d_all[i][local_nodes[j]] for j in range(m)] for i in range(m)]


def geodesic_tangent_chart(
    dmat: list[list[float]],
) -> Optional[list[tuple[float, float]]]:
    m = len(dmat)
    if m < 8:
        return None
    candidates = list(range(1, m))
    l1 = max(candidates, key=lambda j: dmat[0][j])
    d01 = dmat[0][l1]
    if d01 <= 1e-9:
        return None
    best_l2, best_y2 = None, -1.0
    for j in candidates:
        if j == l1:
            continue
        d02 = dmat[0][j]
        d12 = dmat[l1][j]
        if d02 <= 1e-9:
            continue
        x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
        y2_sq = d02 * d02 - x2 * x2
        if y2_sq > best_y2:
            best_y2 = y2_sq
            best_l2 = j
    if best_l2 is None or best_y2 <= 1e-12:
        return None
    l2 = best_l2
    d02 = dmat[0][l2]
    d12 = dmat[l1][l2]
    x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
    y2 = math.sqrt(max(d02 * d02 - x2 * x2, 0.0))
    if y2 <= 1e-9:
        return None
    coords: list[tuple[float, float]] = [(0.0, 0.0)] * m
    coords[l1] = (d01, 0.0)
    coords[l2] = (x2, y2)
    for i in range(m):
        if i in (0, l1, l2):
            continue
        d0i, d1i, d2i = dmat[0][i], dmat[l1][i], dmat[l2][i]
        if d0i <= 1e-12:
            coords[i] = (0.0, 0.0)
            continue
        xi = (d0i * d0i + d01 * d01 - d1i * d1i) / (2.0 * d01)
        yi_abs = math.sqrt(max(d0i * d0i - xi * xi, 0.0))
        p_plus = math.hypot(xi - x2, yi_abs - y2)
        p_minus = math.hypot(xi - x2, -yi_abs - y2)
        coords[i] = (xi, yi_abs if abs(p_plus - d2i) <= abs(p_minus - d2i) else -yi_abs)
    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


def smooth_sigma_local(
    dmat: list[list[float]], sigma_local: list[float], s: float
) -> list[float]:
    m = len(dmat)
    out = []
    for i in range(m):
        num = den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * sigma_local[j]
            den += w
        out.append(num / max(den, 1e-16))
    return out


def metric_from_sigma_hessian_v4(
    h11: float,
    h12: float,
    h22: float,
    floor: float = 1e-6,
    anisotropy_keep: float = 0.4,
    frob_floor: float = 1e-9,
) -> tuple[float, float, float]:
    """v4 Frobenius-normalised metric (returns g11, g12, g22)."""
    tr = -(h11 + h22)
    det = (-h11) * (-h22) - (-h12) ** 2
    disc = max(tr * tr - 4.0 * det, 0.0)
    root = math.sqrt(disc)
    lam1 = 0.5 * (tr - root)
    lam2 = 0.5 * (tr + root)
    a11, a12, a22 = -h11, -h12, -h22
    if abs(a12) > 1e-14:
        v1 = (lam1 - a22, a12)
        v2 = (lam2 - a22, a12)
    else:
        v1, v2 = ((1.0, 0.0), (0.0, 1.0)) if a11 <= a22 else ((0.0, 1.0), (1.0, 0.0))

    def norm(v: tuple[float, float]) -> tuple[float, float]:
        n = math.hypot(v[0], v[1])
        return (v[0] / n, v[1] / n) if n > 1e-18 else (1.0, 0.0)

    q1, q2 = norm(v1), norm(v2)
    mu1, mu2 = max(abs(lam1), floor), max(abs(lam2), floor)
    g11 = mu1 * q1[0] ** 2 + mu2 * q2[0] ** 2
    g12 = mu1 * q1[0] * q1[1] + mu2 * q2[0] * q2[1]
    g22 = mu1 * q1[1] ** 2 + mu2 * q2[1] ** 2
    frob = frob_norm2x2(g11, g12, g22)
    denom = max(frob, frob_floor)
    g11 /= denom; g12 /= denom; g22 /= denom
    iso = 1.0 / math.sqrt(2.0)
    keep = clamp(anisotropy_keep, 0.0, 1.0)
    g11 = keep * g11 + (1.0 - keep) * iso
    g22 = keep * g22 + (1.0 - keep) * iso
    g12 = keep * g12
    return g11, g12, g22


# ---------------------------------------------------------------------------
# NEW: per-point Hessian estimation via local sub-quadratic fit
# ---------------------------------------------------------------------------

def estimate_hessian_at_point(
    chart: list[tuple[float, float]],
    sigma_smooth: list[float],
    cx: float,
    cy: float,
    n_sub: int,
    lam: float = 1e-8,
) -> Optional[tuple[float, float, float]]:
    """
    Fit a local quadratic model centered at (cx, cy) using the n_sub chart nodes
    nearest to that point, and return the Hessian coefficients (h11, h12, h22).

    Sigma(x',y') ~ c + b1*x' + b2*y' + 0.5*h11*x'^2 + h12*x'*y' + 0.5*h22*y'^2
    where x' = x - cx, y' = y - cy.

    This gives a spatially-varying Hessian: H(cx, cy) = (h11, h12, h22).
    """
    # Sort chart nodes by distance to (cx, cy)
    indexed = sorted(
        range(len(chart)),
        key=lambda i: math.hypot(chart[i][0] - cx, chart[i][1] - cy),
    )
    nearby = indexed[: min(n_sub, len(indexed))]
    if len(nearby) < 6:
        return None
    feats: list[list[float]] = []
    targ: list[float] = []
    for idx in nearby:
        x = chart[idx][0] - cx
        y = chart[idx][1] - cy
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(sigma_smooth[idx])
    try:
        beta = fit_ridge(feats, targ, lam=lam)
    except ValueError:
        return None
    return beta[3], beta[4], beta[5]  # h11, h12, h22


# ---------------------------------------------------------------------------
# Curl computation: static (constant metric) + lag (per-point metric)
# ---------------------------------------------------------------------------

def compute_curl_spatially_varying(
    chart: list[tuple[float, float]],
    sigma_smooth: list[float],
    g_anchor: tuple[float, float, float],   # constant anchor metric for static baseline
    velocity: tuple[float, float],
    tau: float,
    cfg: Config,
) -> Optional[dict[str, float]]:
    """
    For each chart node (x_k, y_k):
      1. STATIC: a_static(x_k) = -g_anchor^{-1} * grad_Σ(x_k)   [constant metric]
      2. LAG:    a_lag(x_k)    = -tau * g^{-1}(x_k) * H(x_k) * v [per-point metric]

    Fits linear model over all nodes, extracts curl_z = ∂_x a_y - ∂_y a_x.
    Returns curl_rel_static and curl_rel_lag.
    """
    # First pass: global quadratic fit for static grad (same as CURL-002)
    feats_quad: list[list[float]] = []
    targ_quad: list[float] = []
    for i, (x, y) in enumerate(chart):
        feats_quad.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ_quad.append(sigma_smooth[i])
    if len(feats_quad) < 6:
        return None
    try:
        beta = fit_ridge(feats_quad, targ_quad, lam=cfg.ridge_lam)
    except ValueError:
        return None
    _c, b1, b2, h11_g, h12_g, h22_g = beta

    inv_g = inv2x2(*g_anchor)
    if inv_g is None:
        return None
    inv11, inv12, inv22 = inv_g
    vx, vy = velocity

    pts = chart[1:]  # exclude anchor at origin
    sigma_pts = sigma_smooth[1:]
    if len(pts) < cfg.min_chart_nodes:
        return None

    ax_static: list[float] = []
    ay_static: list[float] = []
    ax_lag: list[float] = []
    ay_lag: list[float] = []

    for i, (x, y) in enumerate(pts):
        # Static: spatially-varying gradient, constant metric
        gx = b1 + h11_g * x + h12_g * y
        gy = b2 + h12_g * x + h22_g * y
        ax_si = -(inv11 * gx + inv12 * gy)
        ay_si = -(inv12 * gx + inv22 * gy)
        ax_static.append(ax_si)
        ay_static.append(ay_si)

        # Lag: per-point Hessian and metric
        h_local = estimate_hessian_at_point(
            chart, sigma_smooth, x, y, n_sub=cfg.n_sub, lam=cfg.ridge_lam
        )
        if h_local is None:
            # fallback to global Hessian at this point (still constant metric, safe)
            h11_k, h12_k, h22_k = h11_g, h12_g, h22_g
        else:
            h11_k, h12_k, h22_k = h_local

        g_k = metric_from_sigma_hessian_v4(
            h11_k, h12_k, h22_k,
            anisotropy_keep=cfg.anisotropy_keep,
            frob_floor=cfg.frob_floor,
        )
        inv_k = inv2x2(*g_k)
        if inv_k is None:
            ax_lag.append(ax_si)
            ay_lag.append(ay_si)
            continue
        inv11_k, inv12_k, inv22_k = inv_k
        # a_lag = -tau * g^{-1}(x_k) * H(x_k) * v
        lag_x = inv11_k * (vx * h11_k + vy * h12_k) + inv12_k * (vx * h12_k + vy * h22_k)
        lag_y = inv12_k * (vx * h11_k + vy * h12_k) + inv22_k * (vx * h12_k + vy * h22_k)
        ax_lag.append(ax_si - tau * lag_x)
        ay_lag.append(ay_si - tau * lag_y)

    def fit_curl(ax_vals: list[float], ay_vals: list[float]) -> float:
        fa = [[1.0, x, y] for (x, y) in pts]
        try:
            ba = fit_ridge(fa, ax_vals, lam=1e-9)
            by = fit_ridge(fa, ay_vals, lam=1e-9)
        except ValueError:
            return float("nan")
        return by[1] - ba[2]  # ∂_x a_y - ∂_y a_x

    curl_s = fit_curl(ax_static, ay_static)
    curl_l = fit_curl(ax_lag, ay_lag)

    # Reference magnitude: static acceleration at anchor
    fa = [[1.0, x, y] for (x, y) in pts]
    try:
        ba = fit_ridge(fa, ax_static, lam=1e-9)
        by = fit_ridge(fa, ay_static, lam=1e-9)
        a_mag = math.hypot(ba[0], by[0])
    except ValueError:
        a_mag = max(math.hypot(ax_static[0], ay_static[0]) if ax_static else 0.0, cfg.a_epsilon)

    denom = max(a_mag, cfg.a_epsilon)
    return {
        "curl_static": abs(curl_s),
        "curl_lag": abs(curl_l),
        "a_mag": a_mag,
        "curl_rel_static": abs(curl_s) / denom,
        "curl_rel_lag": abs(curl_l) / denom,
    }


# ---------------------------------------------------------------------------
# Rewire control (same as CURL-002, but used for lag curl)
# ---------------------------------------------------------------------------

def rewire_sigma(sigma_local: list[float], seed: int, noise_frac: float = 0.30) -> list[float]:
    """Shuffle sigma labels + add ±30% multiplicative noise (random sign flip on structure)."""
    rng = random.Random(seed + 9999)
    shuffled = sigma_local[:]
    rng.shuffle(shuffled)
    return [clamp(s * (1.0 + rng.uniform(-noise_frac, noise_frac)), 0.0, 1.0) for s in shuffled]


# ---------------------------------------------------------------------------
# CSV utilities
# ---------------------------------------------------------------------------

def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Main runner for one dataset
# ---------------------------------------------------------------------------

def run_dataset(cfg: Config, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg)
        log_lines.append(msg)

    log(f"=== QNG-T-CURL-003-v2 | dataset={cfg.dataset_id} seed={cfg.seed} ===")
    log(f"samples={cfg.samples} local_m={cfg.local_m} n_sub={cfg.n_sub} tau={cfg.tau_test}")

    coords, sigma, adj_list, median_edge = build_dataset_graph(cfg.dataset_id, cfg.seed)
    s0 = median_edge
    log(f"graph: n={len(coords)} median_edge={median_edge:.4f}")

    anchors = choose_anchors(sigma, cfg.samples, cfg.seed)
    log(f"anchors selected: {len(anchors)}")

    curl_static_vals: list[float] = []
    curl_lag_iso_vals: list[float] = []
    curl_lag_grad_vals: list[float] = []
    curl_rewired_vals: list[float] = []

    per_anchor_rows: list[dict] = []
    n_skip = 0

    for anchor in anchors:
        d_anchor = dijkstra(adj_list, anchor)
        local_nodes = local_nodes_from_anchor(d_anchor, anchor, cfg.local_m)
        if len(local_nodes) < cfg.min_chart_nodes:
            n_skip += 1
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]

        d_local = local_pairwise_distances(adj_list, local_nodes)
        chart = geodesic_tangent_chart(d_local)
        if chart is None:
            n_skip += 1
            continue

        sigma_local = [sigma[n] for n in local_nodes]
        sigma_smooth = smooth_sigma_local(d_local, sigma_local, s0)

        # Anchor metric (for static baseline)
        # Estimate Hessian at anchor using global quadratic
        feats_q = []
        for i, (x, y) in enumerate(chart):
            feats_q.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        if len(feats_q) < 6:
            n_skip += 1
            continue
        try:
            beta_anchor = fit_ridge(feats_q, sigma_smooth, lam=cfg.ridge_lam)
        except ValueError:
            n_skip += 1
            continue

        h11_a, h12_a, h22_a = beta_anchor[3], beta_anchor[4], beta_anchor[5]
        g_anchor = metric_from_sigma_hessian_v4(
            h11_a, h12_a, h22_a,
            anisotropy_keep=cfg.anisotropy_keep,
            frob_floor=cfg.frob_floor,
        )

        # --- REAL graph: iso velocity ---
        r_iso = compute_curl_spatially_varying(
            chart, sigma_smooth, g_anchor, cfg.v_iso, cfg.tau_test, cfg
        )
        if r_iso is None:
            n_skip += 1
            continue

        # --- REAL graph: grad velocity ---
        r_grad = compute_curl_spatially_varying(
            chart, sigma_smooth, g_anchor, cfg.v_grad, cfg.tau_test, cfg
        )

        # --- REWIRED control: shuffled sigma + per-point metric ---
        rng_rew = random.Random(anchor + cfg.seed)
        sigma_rewired = rewire_sigma(sigma_smooth, seed=anchor + cfg.seed)
        r_rew = compute_curl_spatially_varying(
            chart, sigma_rewired, g_anchor, cfg.v_iso, cfg.tau_test, cfg
        )

        curl_static_vals.append(r_iso["curl_rel_static"])
        curl_lag_iso_vals.append(r_iso["curl_rel_lag"])
        if r_grad:
            curl_lag_grad_vals.append(r_grad["curl_rel_lag"])
        if r_rew:
            curl_rewired_vals.append(r_rew["curl_rel_lag"])

        per_anchor_rows.append({
            "anchor_id": anchor,
            "curl_rel_static": f"{r_iso['curl_rel_static']:.6e}",
            "curl_rel_lag_iso": f"{r_iso['curl_rel_lag']:.6e}",
            "curl_rel_lag_grad": f"{r_grad['curl_rel_lag']:.6e}" if r_grad else "nan",
            "curl_rel_rewired": f"{r_rew['curl_rel_lag']:.6e}" if r_rew else "nan",
            "a_mag": f"{r_iso['a_mag']:.6e}",
        })

    log(f"anchors processed: {len(curl_static_vals)}  skipped: {n_skip}")

    if not curl_static_vals:
        log("ERROR: no valid anchors")
        (out_dir / "run-log.txt").write_text("\n".join(log_lines))
        return {"status": "error", "reason": "no_valid_anchors"}

    med_static = statistics.median(curl_static_vals)
    med_lag_iso = statistics.median(curl_lag_iso_vals)
    med_lag_grad = statistics.median(curl_lag_grad_vals) if curl_lag_grad_vals else float("nan")
    med_rewired = statistics.median(curl_rewired_vals) if curl_rewired_vals else float("nan")

    ref = max(med_static, cfg.a_epsilon)
    lag_factor = med_lag_iso / ref
    rew_factor = med_rewired / ref if not math.isnan(med_rewired) else float("nan")

    log(f"median curl_rel_static  = {med_static:.3e}  (C1 threshold < {cfg.c1_static_max:.0e})")
    log(f"median curl_rel_lag_iso = {med_lag_iso:.3e}  factor={lag_factor:.1f}x (C2 threshold > {cfg.c2_lag_factor_min:.0f}x)")
    log(f"median curl_rel_rewired = {med_rewired:.3e}  factor={rew_factor:.1f}x (C3 threshold > {cfg.c3_rewire_factor_min:.0f}x)")

    c1 = med_static < cfg.c1_static_max
    c2 = lag_factor > cfg.c2_lag_factor_min
    c3 = (not math.isnan(rew_factor)) and rew_factor > cfg.c3_rewire_factor_min

    log(f"C1 (static < 1e-8): {'PASS' if c1 else 'FAIL'}")
    log(f"C2 (lag > 10x static): {'PASS' if c2 else 'FAIL'}")
    log(f"C3 (rewired > 10x static): {'PASS' if c3 else 'FAIL'}")

    decision = "pass" if (c1 and c2 and c3) else "fail"
    log(f"DECISION: {decision.upper()}")

    # Write outputs
    write_csv(
        out_dir / "curl_rel_values.csv",
        ["anchor_id", "curl_rel_static", "curl_rel_lag_iso", "curl_rel_lag_grad", "curl_rel_rewired", "a_mag"],
        per_anchor_rows,
    )
    gate_rows = [
        {"gate": "C1", "metric": "median_curl_rel_static", "value": f"{med_static:.6e}", "threshold": f"<{cfg.c1_static_max:.0e}", "status": "pass" if c1 else "fail"},
        {"gate": "C2", "metric": "lag_factor_iso", "value": f"{lag_factor:.3f}", "threshold": f">{cfg.c2_lag_factor_min:.0f}", "status": "pass" if c2 else "fail"},
        {"gate": "C3", "metric": "rewire_factor", "value": f"{rew_factor:.3f}" if not math.isnan(rew_factor) else "nan", "threshold": f">{cfg.c3_rewire_factor_min:.0f}", "status": "pass" if c3 else "fail"},
        {"gate": "FINAL", "metric": "all_pass", "value": decision, "threshold": "pass", "status": decision},
    ]
    write_csv(
        out_dir / "gate_summary.csv",
        ["gate", "metric", "value", "threshold", "status"],
        gate_rows,
    )

    config_dict = {
        "script": SCRIPT_VERSION,
        "dataset_id": cfg.dataset_id,
        "seed": cfg.seed,
        "samples": cfg.samples,
        "local_m": cfg.local_m,
        "n_sub": cfg.n_sub,
        "tau_test": cfg.tau_test,
        "v_iso": list(cfg.v_iso),
        "v_grad": list(cfg.v_grad),
        "rewire_fraction": cfg.rewire_fraction,
        "anchors_used": len(curl_static_vals),
        "anchors_skipped": n_skip,
    }
    (out_dir / "config.json").write_text(json.dumps(config_dict, indent=2))

    log_text = "\n".join(log_lines)
    (out_dir / "run-log.txt").write_text(log_text)

    # Artifact hashes
    hashes = {
        p.name: sha256_of(p)
        for p in sorted(out_dir.iterdir())
        if p.is_file() and p.suffix in (".csv", ".json")
    }
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2))

    return {
        "dataset_id": cfg.dataset_id,
        "decision": decision,
        "med_static": med_static,
        "med_lag_iso": med_lag_iso,
        "med_lag_grad": med_lag_grad,
        "med_rewired": med_rewired,
        "lag_factor": lag_factor,
        "rew_factor": rew_factor,
        "c1": c1, "c2": c2, "c3": c3,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="QNG-T-CURL-003-v2: spatially-varying metric curl test.")
    parser.add_argument("--dataset", action="append", dest="datasets", default=[], metavar="DS",
                        help="Dataset ID (may repeat). Default: DS-002 DS-003 DS-006")
    parser.add_argument("--out-base", type=Path, default=DEFAULT_OUT_BASE, help="Output base directory.")
    parser.add_argument("--seed", type=int, default=20260225)
    parser.add_argument("--samples", type=int, default=72)
    parser.add_argument("--n-sub", type=int, default=10, help="Chart nodes for per-point Hessian fit.")
    parser.add_argument("--tau", type=float, default=1.0)
    args = parser.parse_args()

    datasets = args.datasets or ["DS-002", "DS-003", "DS-006"]
    results = []
    for ds in datasets:
        ds_tag = ds.lower().replace("-", "")
        out_dir = args.out_base / f"qng-t-curl-003-v2-{ds_tag}"
        cfg = Config(
            dataset_id=ds,
            seed=args.seed,
            samples=args.samples,
            n_sub=args.n_sub,
            tau_test=args.tau,
        )
        r = run_dataset(cfg, out_dir)
        results.append(r)
        print()

    print("=== SUMMARY ===")
    all_pass = True
    for r in results:
        status = r.get("decision", "error")
        print(f"  {r.get('dataset_id','?'):8s}  {status.upper():5s}  "
              f"static={r.get('med_static', float('nan')):.2e}  "
              f"lag_iso={r.get('med_lag_iso', float('nan')):.2e}  "
              f"factor={r.get('lag_factor', float('nan')):.1f}x  "
              f"C1={'P' if r.get('c1') else 'F'} "
              f"C2={'P' if r.get('c2') else 'F'} "
              f"C3={'P' if r.get('c3') else 'F'}")
        if status != "pass":
            all_pass = False

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
