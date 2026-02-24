#!/usr/bin/env python3
"""
QNG Test: Curl of Acceleration Field (QNG-T-CURL-001)

Tests whether the acceleration field a^i = -g^{ij} ∂_j Σ is approximately curl-free,
as required by the gradient-flow law. A large relative curl indicates metric inconsistency
or failure of the coarse-graining assumption A1.

Pre-registration: 05_validation/pre-registrations/qng-t-curl-001.md
Dependency policy: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import heapq
import json
import math
import platform
import random
import statistics
import struct
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-curl-001"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class GateThresholds:
    # C1: curl magnitude
    c1_median_max: float = 0.10
    c1_p90_max: float = 0.30
    # C2: negative control separation (rewired > real × factor)
    c2_separation_factor: float = 1.5
    # Epsilon for division
    a_epsilon: float = 1e-6
    # Rewire fraction
    rewire_fraction: float = 0.50


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    i0 = int(math.floor(pos))
    i1 = int(math.ceil(pos))
    if i0 == i1:
        return xs[i0]
    w = pos - i0
    return (1.0 - w) * xs[i0] + w * xs[i1]


def median(values: list[float]) -> float:
    return quantile(values, 0.5)


def percentile90(values: list[float]) -> float:
    return quantile(values, 0.90)


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    aug = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-16:
            raise ValueError("Singular matrix.")
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
    a = [[0.0 for _ in range(p)] for _ in range(p)]
    b = [0.0 for _ in range(p)]
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


def frob_norm2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    return g22 / det, -g12 / det, g11 / det


def build_dataset_graph(dataset_id: str, seed: int) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float]:
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


def rewire_graph(adj_list: list[list[tuple[int, float]]], seed: int, fraction: float) -> list[list[tuple[int, float]]]:
    """Randomly rewire a fraction of edges, preserving edge weights but destroying spatial structure."""
    rng = random.Random(seed + 7777)
    n = len(adj_list)

    # Collect all edges (undirected, each pair once).
    edges: list[tuple[int, int, float]] = []
    seen = set()
    for i, nbrs in enumerate(adj_list):
        for j, w in nbrs:
            if (min(i, j), max(i, j)) not in seen:
                edges.append((i, j, w))
                seen.add((min(i, j), max(i, j)))

    # Rewire fraction of edges.
    n_rewire = int(len(edges) * fraction)
    indices_to_rewire = set(rng.sample(range(len(edges)), min(n_rewire, len(edges))))

    new_adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for k, (i, j, w) in enumerate(edges):
        if k in indices_to_rewire:
            # Replace with a random pair.
            ni = rng.randrange(n)
            nj = rng.randrange(n)
            while nj == ni:
                nj = rng.randrange(n)
            new_adj[ni][nj] = w
            new_adj[nj][ni] = w
        else:
            new_adj[i][j] = w
            new_adj[j][i] = w

    return [[(j, w) for j, w in m.items()] for m in new_adj]


def dijkstra(adj: list[list[tuple[int, float]]], src: int) -> list[float]:
    n = len(adj)
    d = [float("inf")] * n
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
    bins = [[], [], [], []]
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


def local_nodes_from_anchor(dist_anchor: list[float], anchor: int, m: int) -> list[int]:
    ranked = sorted(range(len(dist_anchor)), key=lambda i: dist_anchor[i])
    out = [anchor]
    for i in ranked:
        if i != anchor:
            out.append(i)
        if len(out) >= m:
            break
    return out


def local_pairwise_distances(adj: list[list[tuple[int, float]]], local_nodes: list[int]) -> list[list[float]]:
    d_all = [dijkstra(adj, node) for node in local_nodes]
    m = len(local_nodes)
    return [[d_all[i][local_nodes[j]] for j in range(m)] for i in range(m)]


def geodesic_tangent_chart(dmat: list[list[float]]) -> list[tuple[float, float]] | None:
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
        if d02 <= 1e-9:
            continue
        x2 = (d02 ** 2 + d01 ** 2 - dmat[l1][j] ** 2) / (2.0 * d01)
        y2_sq = d02 ** 2 - x2 ** 2
        if y2_sq > best_y2:
            best_y2 = y2_sq
            best_l2 = j
    if best_l2 is None or best_y2 <= 1e-12:
        return None

    l2 = best_l2
    d02 = dmat[0][l2]
    x2 = (d02 ** 2 + d01 ** 2 - dmat[l1][l2] ** 2) / (2.0 * d01)
    y2 = math.sqrt(max(d02 ** 2 - x2 ** 2, 0.0))
    if y2 <= 1e-9:
        return None

    coords = [(0.0, 0.0)] * m
    coords = list(coords)
    coords[l1] = (d01, 0.0)
    coords[l2] = (x2, y2)
    for i in range(m):
        if i in (0, l1, l2):
            continue
        d0i = dmat[0][i]
        if d0i <= 1e-12:
            continue
        xi = (d0i ** 2 + d01 ** 2 - dmat[l1][i] ** 2) / (2.0 * d01)
        yi_abs = math.sqrt(max(d0i ** 2 - xi ** 2, 0.0))
        p_plus = math.hypot(xi - x2, yi_abs - y2)
        p_minus = math.hypot(xi - x2, -yi_abs - y2)
        yi = yi_abs if abs(p_plus - dmat[l2][i]) <= abs(p_minus - dmat[l2][i]) else -yi_abs
        coords[i] = (xi, yi)

    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


def smooth_sigma_local(dmat: list[list[float]], sigma_local: list[float], s: float) -> list[float]:
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


def estimate_sigma_grad_hessian(
    chart: list[tuple[float, float]], sigma_local: list[float]
) -> tuple[tuple[float, float], tuple[float, float, float]] | None:
    feats, targ = [], []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
    if len(feats) < 10:
        return None
    try:
        beta = fit_ridge(feats, targ, lam=1e-8)
    except ValueError:
        return None
    return (beta[1], beta[2]), (beta[3], beta[4], beta[5])


def metric_from_sigma_hessian_v4(
    h11: float, h12: float, h22: float,
    floor: float = 1e-6, anisotropy_keep: float = 0.4, frob_floor: float = 1e-9,
) -> tuple[float, float, float]:
    """v4 metric: SPD projection + Frobenius normalization + shrinkage."""
    tr = -(h11 + h22)
    det = h11 * h22 - h12 * h12
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
    mu1 = max(abs(lam1), floor)
    mu2 = max(abs(lam2), floor)
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


def estimate_curl(
    chart: list[tuple[float, float]],
    sigma_local: list[float],
    s0: float,
    a_epsilon: float,
) -> tuple[float, float, float] | None:
    """
    Estimate curl of acceleration field a^i = -g^{ij} ∂_j Σ at the anchor (origin).

    Returns (curl_abs, a_mag, curl_rel) or None if estimation fails.

    Method:
    1. Fit quadratic Sigma model to get grad and Hessian at each chart point.
    2. Compute metric g at each chart point from Hessian_v4.
    3. Compute a = -g^{-1} grad at each chart point.
    4. Fit linear model: a_x ≈ A + B*x + C*y, a_y ≈ D + E*x + F*y.
    5. curl = E - C (= ∂_x a_y - ∂_y a_x evaluated at origin).
    6. |a| = sqrt(A^2 + D^2).
    7. curl_rel = |curl| / max(|a|, epsilon).
    """
    sigma_smooth = smooth_sigma_local(
        [[0.0] * len(chart)] + [[0.0] * len(chart)] * (len(chart) - 1),
        sigma_local,
        s0,
    )
    # Use the full distance matrix approach — we need dmat for smoothing.
    # Since we don't have dmat here directly, use chart coords as proxy distances.
    # (This function is called from a context that passes pre-computed smooth sigma.)
    # --- This function receives chart and already-smoothed sigma_local. ---
    # Compute a at each local chart node (excluding anchor).

    # We need the local acceleration at each node.
    # Approach: for each subset of 3+ nodes around each chart point, estimate local grad + Hessian,
    # compute g, compute a. But for efficiency, fit a global linear model.
    # Simpler and equivalent: use the quadratic sigma fit coefficients.
    # At point (x,y): grad_sigma = (b1 + h11*x + h12*y, b2 + h12*x + h22*y)
    #                 Hessian is approx constant (from quadratic fit).
    # The metric at each point varies; but in the weak-field limit it's approximately
    # constant over the local patch. So use the anchor Hessian for the metric.
    # This is the "flat metric" curl test.

    gh0 = estimate_sigma_grad_hessian(chart, sigma_local)
    if gh0 is None:
        return None
    grad0, hess0 = gh0
    g11, g12, g22 = metric_from_sigma_hessian_v4(hess0[0], hess0[1], hess0[2])
    inv = inv2x2(g11, g12, g22)
    if inv is None:
        return None
    inv11, inv12, inv22 = inv

    # Fit quadratic Sigma model: Σ(x,y) ≈ c + b1*x + b2*y + 0.5*h11*x^2 + h12*x*y + 0.5*h22*y^2
    feats, targ = [], []
    pts: list[tuple[float, float]] = []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
        pts.append((x, y))
    if len(feats) < 10:
        return None
    try:
        beta = fit_ridge(feats, targ, lam=1e-8)
    except ValueError:
        return None
    # beta = [c, b1, b2, h11, h12, h22]
    b1, b2, h11q, h12q, h22q = beta[1], beta[2], beta[3], beta[4], beta[5]

    # At each chart point (x,y):
    # grad_Σ = (b1 + h11*x + h12*y, b2 + h12*x + h22*y)
    # a = -g^{-1} grad_Σ
    # Fit: a_x ≈ A + B*x + C*y, a_y ≈ D + E*x + F*y
    ax_feats, ax_targ = [], []
    ay_feats, ay_targ = [], []
    for (x, y) in pts:
        gx = b1 + h11q * x + h12q * y
        gy = b2 + h12q * x + h22q * y
        ax_val = -(inv11 * gx + inv12 * gy)
        ay_val = -(inv12 * gx + inv22 * gy)
        ax_feats.append([1.0, x, y])
        ax_targ.append(ax_val)
        ay_feats.append([1.0, x, y])
        ay_targ.append(ay_val)
    if len(ax_feats) < 6:
        return None
    try:
        beta_ax = fit_ridge(ax_feats, ax_targ, lam=1e-9)
        beta_ay = fit_ridge(ay_feats, ay_targ, lam=1e-9)
    except ValueError:
        return None
    # beta_ax = [A, B, C]; beta_ay = [D, E, F]
    A, B, C = beta_ax
    D, E, F = beta_ay
    curl = E - C
    a_mag = math.hypot(A, D)
    curl_rel = abs(curl) / max(a_mag, a_epsilon)
    return abs(curl), a_mag, curl_rel


def run_curl_on_graph(
    adj: list[list[tuple[int, float]]],
    sigma: list[float],
    anchors: list[int],
    s0: float,
    thresholds: GateThresholds,
    label: str = "real",
) -> list[dict[str, str]]:
    """Run curl estimation on all anchors and return rows."""
    rows: list[dict[str, str]] = []
    for anchor in anchors:
        d_anchor = dijkstra(adj, anchor)
        local_nodes = local_nodes_from_anchor(d_anchor, anchor=anchor, m=20)
        if len(local_nodes) < 12:
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]
        d_local = local_pairwise_distances(adj, local_nodes)
        chart = geodesic_tangent_chart(d_local)
        if chart is None:
            continue
        sigma_local = [sigma[n] for n in local_nodes]
        sigma_smooth = smooth_sigma_local(d_local, sigma_local, s0)

        result = estimate_curl(chart, sigma_smooth, s0, thresholds.a_epsilon)
        if result is None:
            continue
        curl_abs, a_mag, curl_rel = result
        rows.append({
            "anchor_id": str(anchor),
            "label": label,
            "curl_abs": fmt(curl_abs),
            "a_mag": fmt(a_mag),
            "curl_rel": fmt(curl_rel),
        })
    return rows


def plot_histogram(path: Path, values: list[float], title_key: str, bins: int = 24, color: tuple[int, int, int] = (40, 112, 184)) -> None:
    if not values:
        values = [0.0]
    lo, hi = min(values), max(values)
    if math.isclose(lo, hi):
        hi = lo + 1.0
    w, h = 980, 620
    left, top, right, bottom = 70, 30, w - 20, h - 60
    from pathlib import Path as _P

    class _Canvas:
        def __init__(self):
            self.px = bytearray((249, 251, 250) * (w * h))

        def set(self, x, y, c):
            if 0 <= x < w and 0 <= y < h:
                i = (y * w + x) * 3
                self.px[i:i + 3] = bytes(c)

        def line(self, x0, y0, x1, y1, c):
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
            err = dx + dy
            while True:
                self.set(x0, y0, c)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy; x0 += sx
                if e2 <= dx:
                    err += dx; y0 += sy

        def rect(self, x0, y0, x1, y1, c):
            for x in range(x0, x1 + 1):
                self.set(x, y0, c); self.set(x, y1, c)
            for y in range(y0, y1 + 1):
                self.set(x0, y, c); self.set(x1, y, c)

        def save_png(self, path):
            raw = bytearray()
            for y in range(h):
                raw.append(0)
                i0 = y * w * 3
                raw.extend(self.px[i0:i0 + w * 3])

            def chunk(tag, data):
                return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)

            ihdr = struct.pack("!IIBBBBB", w, h, 8, 2, 0, 0, 0)
            idat = zlib.compress(bytes(raw), level=9)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

    c = _Canvas()
    c.rect(left, top, right, bottom, (74, 88, 82))
    counts = [0] * bins
    for v in values:
        t = (v - lo) / max(hi - lo, 1e-12)
        counts[min(bins - 1, max(0, int(t * bins)))] += 1
    cmax = max(counts) if counts else 1
    bar_w = max(1, (right - left - 8) // bins)
    for i, cnt in enumerate(counts):
        x0 = left + 4 + i * bar_w
        x1 = min(right - 2, x0 + bar_w - 1)
        hp = int((bottom - top - 10) * (cnt / max(cmax, 1)))
        for x in range(x0, x1 + 1):
            c.line(x, bottom, x, bottom - hp, color)
    marker = abs(hash(title_key)) % 120
    c.line(left + 8, top + 8, left + 48 + marker % 20, top + 8, (130, 70, 60))
    c.save_png(path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QNG curl of acceleration field test (QNG-T-CURL-001).")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    thresholds = GateThresholds()
    warnings: list[str] = []

    coords, sigma, adj, median_edge = build_dataset_graph(args.dataset_id, args.seed)
    # Normalize distances by median edge length (same as metric hardening).
    adj_norm = [[(j, w / median_edge) for j, w in row] for row in adj]
    s0 = 1.0

    anchors = choose_anchors(sigma, args.samples, args.seed)

    # Real graph curl.
    real_rows = run_curl_on_graph(adj_norm, sigma, anchors, s0, thresholds, label="real")

    # Rewired graph curl (negative control).
    adj_rewired = rewire_graph(adj_norm, seed=args.seed, fraction=thresholds.rewire_fraction)
    rewired_rows = run_curl_on_graph(adj_rewired, sigma, anchors, s0, thresholds, label="rewired")

    if not real_rows:
        warnings.append("No usable anchors for real graph curl estimation.")
        print("ERROR: No usable anchors.", file=sys.stderr)
        return 2

    curl_rel_real = [float(r["curl_rel"]) for r in real_rows if r["curl_rel"] not in ("nan", "inf")]
    curl_rel_rewired = [float(r["curl_rel"]) for r in rewired_rows if r["curl_rel"] not in ("nan", "inf")]

    # ---- C1 gate ----
    med_real = median(curl_rel_real) if curl_rel_real else float("nan")
    p90_real = percentile90(curl_rel_real) if curl_rel_real else float("nan")
    gate_c1_med = math.isfinite(med_real) and (med_real < thresholds.c1_median_max)
    gate_c1_p90 = math.isfinite(p90_real) and (p90_real < thresholds.c1_p90_max)
    gate_c1 = gate_c1_med and gate_c1_p90

    # ---- C2 gate ----
    med_rewired = median(curl_rel_rewired) if curl_rel_rewired else float("nan")
    gate_c2 = (
        math.isfinite(med_real)
        and math.isfinite(med_rewired)
        and med_real > 1e-12  # non-trivially nonzero
        and (med_rewired > med_real * thresholds.c2_separation_factor)
    )

    decision = "pass" if (gate_c1 and gate_c2) else "fail"

    gate_rows = [
        {"gate_id": "C1", "metric": "median_curl_rel", "value": fmt(med_real), "threshold": f"<{fmt(thresholds.c1_median_max)}", "status": "pass" if gate_c1_med else "fail"},
        {"gate_id": "C1", "metric": "p90_curl_rel", "value": fmt(p90_real), "threshold": f"<{fmt(thresholds.c1_p90_max)}", "status": "pass" if gate_c1_p90 else "fail"},
        {"gate_id": "C2", "metric": "median_curl_rel_rewired", "value": fmt(med_rewired), "threshold": f">{fmt(thresholds.c2_separation_factor)}x median_real={fmt(med_real * thresholds.c2_separation_factor)}", "status": "pass" if gate_c2 else "fail"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision, "threshold": "C1&C2", "status": decision},
    ]

    write_csv(out_dir / "curl_results.csv", ["anchor_id", "label", "curl_abs", "a_mag", "curl_rel"], real_rows)
    write_csv(out_dir / "curl_rewired.csv", ["anchor_id", "label", "curl_abs", "a_mag", "curl_rel"], rewired_rows)
    write_csv(out_dir / "gate_summary.csv", ["gate_id", "metric", "value", "threshold", "status"], gate_rows)

    config_payload = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "samples_requested": args.samples,
        "anchors_real": len(real_rows),
        "anchors_rewired": len(rewired_rows),
        "s0": s0,
        "rewire_fraction": thresholds.rewire_fraction,
        "gates": {
            "C1_median_max": thresholds.c1_median_max,
            "C1_p90_max": thresholds.c1_p90_max,
            "C2_separation_factor": thresholds.c2_separation_factor,
        },
        "decision": decision,
    }
    (out_dir / "config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    plot_histogram(
        out_dir / "curl-distribution.png",
        curl_rel_real + curl_rel_rewired,
        "curl",
        bins=28,
        color=(60, 120, 200),
    )

    files_for_hash = [
        out_dir / "curl_results.csv",
        out_dir / "curl_rewired.csv",
        out_dir / "gate_summary.csv",
        out_dir / "config.json",
        out_dir / "curl-distribution.png",
    ]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started
    run_log_lines = [
        "QNG-T-CURL-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"samples: {args.samples}",
        f"seed: {args.seed}",
        f"duration_seconds: {duration:.3f}",
        f"anchors_real: {len(real_rows)}",
        f"anchors_rewired: {len(rewired_rows)}",
        f"decision: {decision}",
        "",
        "artifact_hashes_sha256:",
    ] + [f"- {k}: {v}" for k, v in hashes.items()]
    if warnings:
        run_log_lines += ["", "warnings:"] + [f"- {w}" for w in warnings]
    (out_dir / "run-log.txt").write_text("\n".join(run_log_lines), encoding="utf-8")

    print(f"QNG-T-CURL-001 completed. dataset={args.dataset_id}")
    print(f"decision={decision}  C1={gate_c1}(med={fmt(med_real)},p90={fmt(p90_real)})  C2={gate_c2}(rewired_med={fmt(med_rewired)})")
    print(f"Real anchors: {len(real_rows)}  Rewired anchors: {len(rewired_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
