#!/usr/bin/env python3
"""
QNG Test: Discrete Curl with Memory Lag (QNG-T-CURL-002)

Extends CURL-001 with:
- Lag term: a_lag = -tau * (v·nabla)(g^{-1} nabla Sigma)
- v3 vs v4 metric comparison
- C1: static curl ~ 0 (gradient flow baseline)
- C2: lag curl >> static curl (memory signature)
- C3: rewired control separates from real graph

Pre-registration: 05_validation/pre-registrations/qng-t-curl-002.md
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-curl-002"
ISO_V3 = 0.5
ISO_V4 = 1.0 / math.sqrt(2.0)


@dataclass
class GateThresholds:
    c1_static_max: float = 1e-8      # machine precision baseline
    c2_lag_factor_min: float = 10.0  # lag curl must be >10x static
    c3_rewire_factor_min: float = 10.0  # rewired > 10x real static
    tau_test: float = 1.0            # normalized lag amplitude
    a_epsilon: float = 1e-6
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
    disc = max(tr * tr - 4.0 * (g11 * g22 - g12 * g12), 0.0)
    root = math.sqrt(disc)
    l1, l2 = 0.5 * (tr - root), 0.5 * (tr + root)
    return (l1, l2) if l1 <= l2 else (l2, l1)


def frob2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    return g22 / det, -g12 / det, g11 / det


def metric_from_hessian(h11: float, h12: float, h22: float,
                        floor: float = 1e-6, k: float = 0.4,
                        version: str = "v4") -> tuple[float, float, float]:
    """Build SPD metric from Hessian using v3 (trace) or v4 (Frobenius) normalization."""
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

    if version == "v3":
        denom = max(g11 + g22, 1e-12)
        iso = 0.5
    else:  # v4
        denom = max(frob2x2(g11, g12, g22), 1e-9)
        iso = ISO_V4
    g11 /= denom; g12 /= denom; g22 /= denom
    g11 = k * g11 + (1 - k) * iso
    g22 = k * g22 + (1 - k) * iso
    g12 = k * g12
    return g11, g12, g22


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
    coords = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread)) for _ in range(n)]
    sigma = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 ** 2)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 ** 2)
        sigma.append(clamp(0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0, 0.015), 0, 1))
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])
            dist[i][j] = d; dist[j][i] = d
    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    edge_lengths = []
    for i in range(n):
        neigh = sorted(range(n), key=lambda j: dist[i][j] if j != i else float("inf"))[:k]
        for j in neigh:
            w = max(dist[i][j], 1e-6) * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w; adj[j][i] = w; edge_lengths.append(w)
    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    me = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, sigma, adj_list, max(me, 1e-9)


def dijkstra(adj: list[list[tuple[int, float]]], src: int) -> list[float]:
    n = len(adj)
    d = [float("inf")] * n; d[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        du, u = heapq.heappop(pq)
        if du > d[u]: continue
        for v, w in adj[u]:
            nd = du + w
            if nd < d[v]:
                d[v] = nd; heapq.heappush(pq, (nd, v))
    return d


def choose_anchors(sigma: list[float], samples: int, seed: int) -> list[int]:
    rng = random.Random(seed + 71)
    n = len(sigma)
    target = max(8, min(samples, n))
    anchors = set(sorted(range(n), key=lambda i: sigma[i], reverse=True)[:target // 2])
    bins = [[], [], [], []]
    s_sorted = sorted(sigma)
    q1 = s_sorted[int(0.25 * (n - 1))]; q2 = s_sorted[int(0.50 * (n - 1))]; q3 = s_sorted[int(0.75 * (n - 1))]
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
        if i != anchor: out.append(i)
        if len(out) >= m: break
    return out


def local_pairwise_distances(adj: list[list[tuple[int, float]]], nodes: list[int]) -> list[list[float]]:
    d_all = [dijkstra(adj, node) for node in nodes]
    return [[d_all[i][nodes[j]] for j in range(len(nodes))] for i in range(len(nodes))]


def geodesic_tangent_chart(dmat: list[list[float]]) -> list[tuple[float, float]] | None:
    m = len(dmat)
    if m < 8: return None
    candidates = list(range(1, m))
    l1 = max(candidates, key=lambda j: dmat[0][j])
    d01 = dmat[0][l1]
    if d01 <= 1e-9: return None
    best_l2, best_y2 = None, -1.0
    for j in candidates:
        if j == l1: continue
        d02 = dmat[0][j]
        if d02 <= 1e-9: continue
        x2 = (d02 ** 2 + d01 ** 2 - dmat[l1][j] ** 2) / (2.0 * d01)
        y2_sq = d02 ** 2 - x2 ** 2
        if y2_sq > best_y2:
            best_y2 = y2_sq; best_l2 = j
    if best_l2 is None or best_y2 <= 1e-12: return None
    l2 = best_l2
    d02 = dmat[0][l2]
    x2 = (d02 ** 2 + d01 ** 2 - dmat[l1][l2] ** 2) / (2.0 * d01)
    y2 = math.sqrt(max(d02 ** 2 - x2 ** 2, 0.0))
    if y2 <= 1e-9: return None
    coords = [(0.0, 0.0)] * m; coords = list(coords)
    coords[l1] = (d01, 0.0); coords[l2] = (x2, y2)
    for i in range(m):
        if i in (0, l1, l2): continue
        d0i = dmat[0][i]
        if d0i <= 1e-12: continue
        xi = (d0i ** 2 + d01 ** 2 - dmat[l1][i] ** 2) / (2.0 * d01)
        yi_abs = math.sqrt(max(d0i ** 2 - xi ** 2, 0.0))
        p_plus = math.hypot(xi - x2, yi_abs - y2)
        p_minus = math.hypot(xi - x2, -yi_abs - y2)
        coords[i] = (xi, yi_abs if abs(p_plus - dmat[l2][i]) <= abs(p_minus - dmat[l2][i]) else -yi_abs)
    xs = [c[0] for c in coords[1:]]; ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8: return None
    return coords


def smooth_sigma_local(dmat: list[list[float]], sigma_local: list[float], s: float) -> list[float]:
    m = len(dmat); out = []
    for i in range(m):
        num = den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * sigma_local[j]; den += w
        out.append(num / max(den, 1e-16))
    return out


def estimate_sigma_quad(chart: list[tuple[float, float]], sigma_local: list[float]) -> list[float] | None:
    """Fit quadratic Sigma model; return beta = [c, b1, b2, h11, h12, h22]."""
    feats, targ = [], []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
    if len(feats) < 10: return None
    try:
        return fit_ridge(feats, targ, lam=1e-8)
    except ValueError:
        return None


def compute_curl_at_origin(
    beta: list[float],         # quadratic Sigma model coefficients
    g_metric: tuple[float, float, float],  # (g11, g12, g22)
    pts: list[tuple[float, float]],        # chart points (excluding anchor)
    velocity: tuple[float, float],         # velocity direction for lag
    tau: float,                            # lag amplitude
    a_epsilon: float,
) -> dict[str, float]:
    """
    Compute curl of a_static and a_total = a_static + tau * a_lag at origin.

    Returns dict with curl_rel_static, curl_rel_lag, a_static_mag.
    """
    # Unpack quadratic Sigma model: Σ ≈ c + b1*x + b2*y + h11*x^2/2 + h12*x*y + h22*y^2/2
    c, b1, b2, h11, h12, h22 = beta  # pylint: disable=unused-variable

    g11, g12, g22 = g_metric
    inv = inv2x2(g11, g12, g22)
    if inv is None:
        return {}
    inv11, inv12, inv22 = inv

    vx, vy = velocity

    ax_s, ay_s, ax_l, ay_l = [], [], [], []
    for (x, y) in pts:
        # grad Sigma at (x,y)
        gx = b1 + h11 * x + h12 * y
        gy = b2 + h12 * x + h22 * y
        # Static acceleration
        ax_si = -(inv11 * gx + inv12 * gy)
        ay_si = -(inv12 * gx + inv22 * gy)
        ax_s.append(ax_si); ay_s.append(ay_si)
        # Lag correction: -tau * (v · nabla)(g^{-1} nabla Sigma)
        # (v · nabla) g^{-1} nabla Sigma ≈ v_j * partial_j (g^{ij} partial_i Sigma)
        # Since g is constant over the patch: (v · nabla)(g^{-1} nabla Sigma)_x = g^{ij} v_j partial_{ji} Sigma
        # = inv11 * (vx * h11 + vy * h12) + inv12 * (vx * h12 + vy * h22)
        lag_x = inv11 * (vx * h11 + vy * h12) + inv12 * (vx * h12 + vy * h22)
        lag_y = inv12 * (vx * h11 + vy * h12) + inv22 * (vx * h12 + vy * h22)
        ax_l.append(ax_si - tau * lag_x)
        ay_l.append(ay_si - tau * lag_y)

    def fit_curl(ax_vals, ay_vals) -> float:
        fa, fb = [], []
        for (x, y), ax_v, ay_v in zip(pts, ax_vals, ay_vals):
            fa.append([1.0, x, y]); fb.append([1.0, x, y])
        try:
            ba = fit_ridge(fa, ax_vals, lam=1e-9)
            by = fit_ridge(fb, ay_vals, lam=1e-9)
        except ValueError:
            return float("nan")
        # curl = E - C: ba = [A, B, C], by = [D, E, F]
        return by[1] - ba[2]

    curl_s = fit_curl(ax_s, ay_s)
    curl_l = fit_curl(ax_l, ay_l)
    a_mag = math.hypot(ax_s[0] if ax_s else 0.0, ay_s[0] if ay_s else 0.0)  # At first point ≈ origin

    # Better: use model intercept A, D as a_at_origin
    fa = [[1.0, x, y] for (x, y) in pts]
    try:
        ba = fit_ridge(fa, ax_s, lam=1e-9)
        by = fit_ridge(fa, ay_s, lam=1e-9)
        a_mag = math.hypot(ba[0], by[0])
    except ValueError:
        pass

    denom = max(a_mag, a_epsilon)
    return {
        "curl_static": abs(curl_s),
        "curl_lag": abs(curl_l),
        "a_mag": a_mag,
        "curl_rel_static": abs(curl_s) / denom,
        "curl_rel_lag": abs(curl_l) / denom,
    }


def rewire_graph(adj_list: list[list[tuple[int, float]]], seed: int, fraction: float) -> list[list[tuple[int, float]]]:
    rng = random.Random(seed + 7777)
    n = len(adj_list)
    edges, seen = [], set()
    for i, nbrs in enumerate(adj_list):
        for j, w in nbrs:
            if (min(i, j), max(i, j)) not in seen:
                edges.append((i, j, w)); seen.add((min(i, j), max(i, j)))
    n_rewire = int(len(edges) * fraction)
    rewire_set = set(rng.sample(range(len(edges)), min(n_rewire, len(edges))))
    new_adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for k, (i, j, w) in enumerate(edges):
        if k in rewire_set:
            ni = rng.randrange(n); nj = rng.randrange(n)
            while nj == ni: nj = rng.randrange(n)
            new_adj[ni][nj] = w; new_adj[nj][ni] = w
        else:
            new_adj[i][j] = w; new_adj[j][i] = w
    return [[(j, w) for j, w in m.items()] for m in new_adj]


def plot_histogram(path: Path, real_vals: list[float], lag_vals: list[float], ctrl_vals: list[float], bins: int = 28) -> None:
    all_vals = real_vals + lag_vals + ctrl_vals
    if not all_vals: return
    lo = min(all_vals); hi = max(all_vals)
    if math.isclose(lo, hi): hi = lo + 1.0
    w, h = 1100, 640
    left, top, right, bottom = 70, 30, w - 20, h - 60

    class _C:
        def __init__(self):
            self.px = bytearray((249, 251, 250) * (w * h))
        def set(self, x, y, c):
            if 0 <= x < w and 0 <= y < h:
                i = (y * w + x) * 3; self.px[i:i + 3] = bytes(c)
        def line(self, x0, y0, x1, y1, c):
            dx, dy = abs(x1 - x0), -abs(y1 - y0)
            sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
            err = dx + dy
            while True:
                self.set(x0, y0, c)
                if x0 == x1 and y0 == y1: break
                e2 = 2 * err
                if e2 >= dy: err += dy; x0 += sx
                if e2 <= dx: err += dx; y0 += sy
        def rect(self, x0, y0, x1, y1, c):
            for x in range(x0, x1 + 1): self.set(x, y0, c); self.set(x, y1, c)
            for y in range(y0, y1 + 1): self.set(x0, y, c); self.set(x1, y, c)
        def save_png(self, path):
            raw = bytearray()
            for y in range(h):
                raw.append(0); raw.extend(self.px[y * w * 3:(y + 1) * w * 3])
            def chunk(tag, data):
                return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            ihdr = struct.pack("!IIBBBBB", w, h, 8, 2, 0, 0, 0)
            idat = zlib.compress(bytes(raw), level=9)
            path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))

    c = _C(); c.rect(left, top, right, bottom, (74, 88, 82))
    bar_w = max(1, (right - left - 8) // bins // 3)

    def draw_bars(vals, color, offset):
        counts = [0] * bins
        for v in vals:
            t = (v - lo) / max(hi - lo, 1e-12)
            counts[min(bins - 1, max(0, int(t * bins)))] += 1
        cmax = max(counts) if counts else 1
        for i, cnt in enumerate(counts):
            x0 = left + 4 + i * bar_w * 3 + offset * bar_w
            x1 = min(right - 2, x0 + bar_w - 1)
            hp = int((bottom - top - 10) * (cnt / max(cmax, 1)))
            for x in range(x0, x1 + 1):
                c.line(x, bottom, x, bottom - hp, color)

    draw_bars(real_vals, (38, 102, 179), 0)    # blue: static
    draw_bars(lag_vals, (200, 80, 30), 1)       # orange: lag
    draw_bars(ctrl_vals, (80, 160, 80), 2)      # green: control
    c.save_png(path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows: w.writerow(row)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="QNG-T-CURL-002: discrete curl with memory lag.")
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

    coords, sigma, adj, median_edge = build_dataset_graph(args.dataset_id, args.seed)
    adj_norm = [[(j, w / median_edge) for j, w in row] for row in adj]
    adj_rewired = rewire_graph(adj_norm, seed=args.seed, fraction=thresholds.rewire_fraction)
    s0 = 1.0

    anchors = choose_anchors(sigma, args.samples, args.seed)

    compare_rows: list[dict[str, str]] = []
    control_rows: list[dict[str, str]] = []

    curl_static_v4: list[float] = []
    curl_lag_iso_v4: list[float] = []
    curl_lag_grad_v4: list[float] = []
    curl_static_v3: list[float] = []
    curl_lag_iso_v3: list[float] = []
    curl_static_rewired: list[float] = []

    rng = random.Random(args.seed + 12345)

    for anchor in anchors:
        # -- Real graph --
        d_anchor = dijkstra(adj_norm, anchor)
        local_nodes = local_nodes_from_anchor(d_anchor, anchor=anchor, m=20)
        if len(local_nodes) < 12: continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]
        d_local = local_pairwise_distances(adj_norm, local_nodes)
        chart = geodesic_tangent_chart(d_local)
        if chart is None: continue
        sigma_local = [sigma[n] for n in local_nodes]
        sigma_smooth = smooth_sigma_local(d_local, sigma_local, s0)
        beta = estimate_sigma_quad(chart, sigma_smooth)
        if beta is None: continue

        pts = chart[1:]  # exclude anchor at origin

        # v4 metric
        g_v4 = metric_from_hessian(beta[3], beta[4], beta[5], version="v4")
        # v3 metric
        g_v3 = metric_from_hessian(beta[3], beta[4], beta[5], version="v3")

        # Velocity vectors
        v_iso = (1.0 / math.sqrt(2.0), 1.0 / math.sqrt(2.0))  # isotropic fixed
        # Gradient-aligned velocity
        grad_mag = math.hypot(beta[1], beta[2])
        if grad_mag > 1e-10:
            v_grad = (-beta[1] / grad_mag, -beta[2] / grad_mag)
        else:
            v_grad = v_iso

        r_v4_static = compute_curl_at_origin(beta, g_v4, pts, v_iso, tau=0.0, a_epsilon=thresholds.a_epsilon)
        r_v4_lag_iso = compute_curl_at_origin(beta, g_v4, pts, v_iso, tau=thresholds.tau_test, a_epsilon=thresholds.a_epsilon)
        r_v4_lag_grad = compute_curl_at_origin(beta, g_v4, pts, v_grad, tau=thresholds.tau_test, a_epsilon=thresholds.a_epsilon)
        r_v3_static = compute_curl_at_origin(beta, g_v3, pts, v_iso, tau=0.0, a_epsilon=thresholds.a_epsilon)
        r_v3_lag_iso = compute_curl_at_origin(beta, g_v3, pts, v_iso, tau=thresholds.tau_test, a_epsilon=thresholds.a_epsilon)

        if not (r_v4_static and r_v4_lag_iso and r_v4_lag_grad and r_v3_static and r_v3_lag_iso):
            continue

        curl_static_v4.append(r_v4_static["curl_rel_static"])
        curl_lag_iso_v4.append(r_v4_lag_iso["curl_rel_lag"])
        curl_lag_grad_v4.append(r_v4_lag_grad["curl_rel_lag"])
        curl_static_v3.append(r_v3_static["curl_rel_static"])
        curl_lag_iso_v3.append(r_v3_lag_iso["curl_rel_lag"])

        compare_rows.append({
            "anchor_id": str(anchor),
            "curl_rel_static_v4": fmt(r_v4_static["curl_rel_static"]),
            "curl_rel_lag_iso_v4": fmt(r_v4_lag_iso["curl_rel_lag"]),
            "curl_rel_lag_grad_v4": fmt(r_v4_lag_grad["curl_rel_lag"]),
            "curl_rel_static_v3": fmt(r_v3_static["curl_rel_static"]),
            "curl_rel_lag_iso_v3": fmt(r_v3_lag_iso["curl_rel_lag"]),
            "a_mag_v4": fmt(r_v4_static["a_mag"]),
        })

        # -- Rewired graph (negative control) --
        d_rewired = dijkstra(adj_rewired, anchor)
        local_rew = local_nodes_from_anchor(d_rewired, anchor=anchor, m=20)
        if len(local_rew) < 12: continue
        if local_rew[0] != anchor:
            local_rew = [anchor] + [n for n in local_rew if n != anchor]
        d_rew_local = local_pairwise_distances(adj_rewired, local_rew)
        chart_rew = geodesic_tangent_chart(d_rew_local)
        if chart_rew is not None:
            sigma_rew = [sigma[n] for n in local_rew]
            sigma_rew_smooth = smooth_sigma_local(d_rew_local, sigma_rew, s0)
            beta_rew = estimate_sigma_quad(chart_rew, sigma_rew_smooth)
            if beta_rew is not None:
                g_rew = metric_from_hessian(beta_rew[3], beta_rew[4], beta_rew[5], version="v4")
                r_rew = compute_curl_at_origin(beta_rew, g_rew, chart_rew[1:], v_iso, tau=0.0, a_epsilon=thresholds.a_epsilon)
                if r_rew:
                    curl_static_rewired.append(r_rew["curl_rel_static"])
                    control_rows.append({
                        "anchor_id": str(anchor),
                        "label": "rewired",
                        "curl_rel_static": fmt(r_rew["curl_rel_static"]),
                    })

    if not curl_static_v4:
        print("ERROR: No usable anchors.", file=sys.stderr)
        return 2

    med_static_v4 = median(curl_static_v4)
    med_lag_iso_v4 = median(curl_lag_iso_v4) if curl_lag_iso_v4 else float("nan")
    med_lag_grad_v4 = median(curl_lag_grad_v4) if curl_lag_grad_v4 else float("nan")
    med_static_v3 = median(curl_static_v3)
    med_lag_iso_v3 = median(curl_lag_iso_v3) if curl_lag_iso_v3 else float("nan")
    med_rewired = median(curl_static_rewired) if curl_static_rewired else float("nan")

    # Gates
    gate_c1 = math.isfinite(med_static_v4) and (med_static_v4 < thresholds.c1_static_max)

    # C2: lag curl > 10x static
    c2_iso = math.isfinite(med_lag_iso_v4) and med_static_v4 > 1e-20 and (med_lag_iso_v4 > thresholds.c2_lag_factor_min * med_static_v4)
    c2_grad = math.isfinite(med_lag_grad_v4) and med_static_v4 > 1e-20 and (med_lag_grad_v4 > thresholds.c2_lag_factor_min * med_static_v4)
    gate_c2 = c2_iso and c2_grad

    # C3: rewired > 10x real static
    gate_c3 = math.isfinite(med_rewired) and med_static_v4 > 1e-20 and (med_rewired > thresholds.c3_rewire_factor_min * med_static_v4)

    decision = "pass" if (gate_c1 and gate_c2 and gate_c3) else "fail"

    gate_rows = [
        {"gate_id": "C1", "metric": "median_curl_rel_static_v4", "value": fmt(med_static_v4), "threshold": f"<{fmt(thresholds.c1_static_max)}", "status": "pass" if gate_c1 else "fail"},
        {"gate_id": "C2", "metric": f"median_lag_iso_v4/{thresholds.c2_lag_factor_min}x_static", "value": f"{fmt(med_lag_iso_v4)} vs {fmt(thresholds.c2_lag_factor_min * med_static_v4)}", "threshold": f">{thresholds.c2_lag_factor_min}x", "status": "pass" if c2_iso else "fail"},
        {"gate_id": "C2", "metric": f"median_lag_grad_v4/{thresholds.c2_lag_factor_min}x_static", "value": f"{fmt(med_lag_grad_v4)} vs {fmt(thresholds.c2_lag_factor_min * med_static_v4)}", "threshold": f">{thresholds.c2_lag_factor_min}x", "status": "pass" if c2_grad else "fail"},
        {"gate_id": "C3", "metric": f"median_rewired/{thresholds.c3_rewire_factor_min}x_static", "value": f"{fmt(med_rewired)} vs {fmt(thresholds.c3_rewire_factor_min * med_static_v4)}", "threshold": f">{thresholds.c3_rewire_factor_min}x", "status": "pass" if gate_c3 else "fail"},
        {"gate_id": "INFO", "metric": "median_curl_rel_static_v3", "value": fmt(med_static_v3), "threshold": "informational", "status": "info"},
        {"gate_id": "INFO", "metric": "median_curl_rel_lag_iso_v3", "value": fmt(med_lag_iso_v3), "threshold": "informational", "status": "info"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision, "threshold": "C1&C2&C3", "status": decision},
    ]

    write_csv(out_dir / "curl_comparison.csv",
              ["anchor_id", "curl_rel_static_v4", "curl_rel_lag_iso_v4", "curl_rel_lag_grad_v4",
               "curl_rel_static_v3", "curl_rel_lag_iso_v3", "a_mag_v4"],
              compare_rows)
    write_csv(out_dir / "curl_controls.csv", ["anchor_id", "label", "curl_rel_static"], control_rows)
    write_csv(out_dir / "gate_summary.csv", ["gate_id", "metric", "value", "threshold", "status"], gate_rows)

    config = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "samples": args.samples,
        "anchors_used": len(compare_rows),
        "tau_test": thresholds.tau_test,
        "rewire_fraction": thresholds.rewire_fraction,
        "gates": {
            "C1_static_max": thresholds.c1_static_max,
            "C2_lag_factor_min": thresholds.c2_lag_factor_min,
            "C3_rewire_factor_min": thresholds.c3_rewire_factor_min,
        },
        "decision": decision,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    plot_histogram(out_dir / "curl-memory-signature.png", curl_static_v4, curl_lag_iso_v4, curl_static_rewired)

    files_for_hash = [out_dir / f for f in ["curl_comparison.csv", "curl_controls.csv", "gate_summary.csv", "config.json"]]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started
    run_log = [
        "QNG-T-CURL-002 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"dataset_id: {args.dataset_id}  seed: {args.seed}  anchors_used: {len(compare_rows)}",
        f"duration_seconds: {duration:.3f}",
        f"decision: {decision}",
        "",
        f"C1  static_v4_median: {fmt(med_static_v4)}",
        f"C2  lag_iso_v4_median: {fmt(med_lag_iso_v4)}  lag_grad_v4_median: {fmt(med_lag_grad_v4)}",
        f"C3  rewired_median: {fmt(med_rewired)}",
        "",
        f"INFO v3 static: {fmt(med_static_v3)}  v3 lag_iso: {fmt(med_lag_iso_v3)}",
    ]
    (out_dir / "run-log.txt").write_text("\n".join(run_log), encoding="utf-8")

    print(f"QNG-T-CURL-002 completed. dataset={args.dataset_id}  anchors={len(compare_rows)}")
    print(f"decision={decision}  C1={gate_c1}  C2={gate_c2}  C3={gate_c3}")
    print(f"C1 static_v4={fmt(med_static_v4)}")
    print(f"C2 lag_iso_v4={fmt(med_lag_iso_v4)}  ({fmt(med_lag_iso_v4/(med_static_v4+1e-30))}x static)")
    print(f"C2 lag_grad_v4={fmt(med_lag_grad_v4)}  ({fmt(med_lag_grad_v4/(med_static_v4+1e-30))}x static)")
    print(f"C3 rewired={fmt(med_rewired)}  ({fmt(med_rewired/(med_static_v4+1e-30))}x static)")
    print(f"INFO v3 vs v4: static_v3={fmt(med_static_v3)}  static_v4={fmt(med_static_v4)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
