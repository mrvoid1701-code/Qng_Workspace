#!/usr/bin/env python3
"""
D3b Candidate Gate v1 — Gate mai bun pentru discriminanță fizică.

Două teste:
1. Anisotropy sweep: la ce valoare anisotropy_keep apare discriminanța?
2. Cross-metric margin: g_qng aliniază grad_qng mai bine decât g_ctrl?

Pre-registration: 05_validation/pre-registrations/d3b-candidate-v1.md
Seed: 9999 | Dataset seed: 3401
"""

from __future__ import annotations

import csv
import heapq
import json
import math
import random
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "d3b-candidate-v1"

ATTACK_SEED = 9999
DATASET_SEED = 3401
N_NODES = 280
K_NEIGHBORS = 8
SPREAD = 2.3
SAMPLES = 72
LOCAL_M = 20
S0 = 1.0

# Anisotropy sweep values (Test 1)
ANISO_VALUES = [0.4, 0.7, 1.0]

# Cross-metric margin threshold (Test 2)
MARGIN_THRESHOLD = 0.05


# ---------------------------------------------------------------------------
# Helpers (identice cu hardening v4)
# ---------------------------------------------------------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    i0 = int(math.floor(pos))
    i1 = int(math.ceil(pos))
    if i0 == i1:
        return xs[i0]
    return (1.0 - (pos - i0)) * xs[i0] + (pos - i0) * xs[i1]


def median_f(v: list[float]) -> float:
    return quantile(v, 0.5)


def p10_f(v: list[float]) -> float:
    return quantile(v, 0.10)


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(a)
    aug = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-16:
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


def fit_ridge(features: list[list[float]], targets: list[float], lam: float = 1e-8) -> list[float]:
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


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    return g22 / det, -g12 / det, g11 / det


def frob2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2 * g12 * g12 + g22 * g22)


def cosine(a: tuple[float, float], b: tuple[float, float]) -> float:
    na = math.hypot(a[0], a[1])
    nb = math.hypot(b[0], b[1])
    if na < 1e-16 or nb < 1e-16:
        return float("nan")
    return (a[0] * b[0] + a[1] * b[1]) / (na * nb)


def dijkstra(adj: list[list[tuple[int, float]]], src: int) -> list[float]:
    n = len(adj)
    d = [float("inf")] * n
    d[src] = 0.0
    pq = [(0.0, src)]
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


def smooth_local(dmat: list[list[float]], vals: list[float], s: float) -> list[float]:
    m = len(dmat)
    out = [0.0] * m
    for i in range(m):
        num = den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * vals[j]
            den += w
        out[i] = num / max(den, 1e-16)
    return out


def fit_grad_hess(chart: list[tuple[float, float]], vals: list[float]):
    feats, targ = [], []
    for (x, y), v in zip(chart[1:], vals[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(v)
    if len(feats) < 10:
        return None
    try:
        beta = fit_ridge(feats, targ)
    except ValueError:
        return None
    return (beta[1], beta[2]), (beta[3], beta[4], beta[5])


def metric_from_hessian(
    h11: float, h12: float, h22: float,
    floor: float = 1e-6,
    anisotropy_keep: float = 0.4,
) -> tuple[float, float, float]:
    """Metrică din Hessian — identic cu v4 dar cu anisotropy_keep variabil."""
    tr = -(h11 + h22)
    det = (-h11) * (-h22) - (-h12) * (-h12)
    disc = max(tr * tr - 4.0 * det, 0.0)
    root = math.sqrt(disc)
    lam1 = 0.5 * (tr - root)
    lam2 = 0.5 * (tr + root)

    a11, a12, a22 = -h11, -h12, -h22
    if abs(a12) > 1e-14:
        v1 = (lam1 - a22, a12)
        v2 = (lam2 - a22, a12)
    else:
        if a11 <= a22:
            v1, v2 = (1.0, 0.0), (0.0, 1.0)
        else:
            v1, v2 = (0.0, 1.0), (1.0, 0.0)

    def norm(v):
        n = math.hypot(v[0], v[1])
        return (v[0] / n, v[1] / n) if n > 1e-18 else (1.0, 0.0)

    q1, q2 = norm(v1), norm(v2)
    mu1 = max(abs(lam1), floor)
    mu2 = max(abs(lam2), floor)
    g11 = mu1 * q1[0] * q1[0] + mu2 * q2[0] * q2[0]
    g12 = mu1 * q1[0] * q1[1] + mu2 * q2[0] * q2[1]
    g22 = mu1 * q1[1] * q1[1] + mu2 * q2[1] * q2[1]

    frob = frob2x2(g11, g12, g22)
    denom = max(frob, 1e-9)
    g11 /= denom
    g12 /= denom
    g22 /= denom

    # Shrinkage: blend spre izotropic
    iso = 1.0 / math.sqrt(2.0)
    keep = clamp(anisotropy_keep, 0.0, 1.0)
    g11 = keep * g11 + (1.0 - keep) * iso
    g22 = keep * g22 + (1.0 - keep) * iso
    g12 = keep * g12
    return g11, g12, g22


def geodesic_chart(dmat: list[list[float]]) -> list[tuple[float, float]] | None:
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
        d02, d12 = dmat[0][j], dmat[l1][j]
        if d02 <= 1e-9:
            continue
        x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
        y2_sq = d02 * d02 - x2 * x2
        if y2_sq > best_y2:
            best_y2, best_l2 = y2_sq, j
    if best_l2 is None or best_y2 <= 1e-12:
        return None
    l2 = best_l2
    d02, d12 = dmat[0][l2], dmat[l1][l2]
    x2 = (d02 * d02 + d01 * d01 - d12 * d12) / (2.0 * d01)
    y2 = math.sqrt(max(d02 * d02 - x2 * x2, 0.0))
    if y2 <= 1e-9:
        return None
    coords = [(0.0, 0.0)] * m
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
        yi = yi_abs if abs(p_plus - d2i) <= abs(p_minus - d2i) else -yi_abs
        coords[i] = (xi, yi)
    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


# ---------------------------------------------------------------------------
# Câmpuri de control (identice cu d3-attack-v1)
# ---------------------------------------------------------------------------

def field_qng_sigma(coords, seed):
    rng = random.Random(seed + 17)
    out = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 ** 2)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 ** 2)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        out.append(clamp(s, 0.0, 1.0))
    return out


def field_random_gaussians(coords, seed):
    rng = random.Random(seed + 1001)
    centers = [(rng.uniform(-2.0, 2.0), rng.uniform(-2.0, 2.0)) for _ in range(4)]
    amplitudes = [rng.uniform(0.3, 0.9) for _ in range(4)]
    widths = [rng.uniform(0.5, 1.5) for _ in range(4)]
    out = []
    for x, y in coords:
        s = sum(a * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * w * w))
                for (cx, cy), a, w in zip(centers, amplitudes, widths))
        out.append(clamp(s + rng.gauss(0.0, 0.01), 0.0, 1.0))
    return out


def field_linear_gradient(coords, seed):
    rng = random.Random(seed + 2002)
    angle = rng.uniform(0, 2 * math.pi)
    dx, dy = math.cos(angle), math.sin(angle)
    vals = [dx * x + dy * y for x, y in coords]
    vmin, vmax = min(vals), max(vals)
    span = max(vmax - vmin, 1e-9)
    return [clamp((v - vmin) / span + rng.gauss(0.0, 0.005), 0.0, 1.0) for v in vals]


def field_sinusoidal(coords, seed):
    rng = random.Random(seed + 3003)
    fx, fy = rng.uniform(0.4, 1.2), rng.uniform(0.4, 1.2)
    ph = rng.uniform(0, 2 * math.pi)
    return [clamp(0.5 * (1 + math.sin(fx * x + fy * y + ph)) + rng.gauss(0.0, 0.01), 0.0, 1.0)
            for x, y in coords]


def field_quadratic_bowl(coords, seed):
    rng = random.Random(seed + 4004)
    cx, cy = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)
    vals = [-((x - cx) ** 2 + (y - cy) ** 2) for x, y in coords]
    vmin, vmax = min(vals), max(vals)
    span = max(vmax - vmin, 1e-9)
    return [clamp((v - vmin) / span + rng.gauss(0.0, 0.005), 0.0, 1.0) for v in vals]


def field_pure_noise(coords, seed):
    rng = random.Random(seed + 5005)
    return [clamp(rng.gauss(0.5, 0.2), 0.0, 1.0) for _ in coords]


# ---------------------------------------------------------------------------
# Construire graf (uncoupled — pur geometric)
# ---------------------------------------------------------------------------

def build_graph(seed: int):
    rng = random.Random(seed + 17)
    coords = [(rng.uniform(-SPREAD, SPREAD), rng.uniform(-SPREAD, SPREAD))
               for _ in range(N_NODES)]
    adj: list[dict[int, float]] = [dict() for _ in range(N_NODES)]
    edge_lengths = []
    for i in range(N_NODES):
        xi, yi = coords[i]
        dists = sorted(
            [(math.hypot(xi - coords[j][0], yi - coords[j][1]), j)
             for j in range(N_NODES) if j != i]
        )
        for d, j in dists[:K_NEIGHBORS]:
            w = max(d, 1e-6)
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)
    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    med_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, adj_list, max(med_edge, 1e-9)


def choose_anchors(field: list[float], seed: int) -> list[int]:
    rng = random.Random(seed + 71)
    n = len(field)
    target = max(8, min(SAMPLES, n))
    idx_sorted = sorted(range(n), key=lambda i: field[i], reverse=True)
    anchors = set(idx_sorted[:target // 2])
    s_sorted = sorted(field)
    q1 = s_sorted[int(0.25 * (n - 1))]
    q2 = s_sorted[int(0.50 * (n - 1))]
    q3 = s_sorted[int(0.75 * (n - 1))]
    bins = [[], [], [], []]
    for i, s in enumerate(field):
        if s <= q1:
            bins[0].append(i)
        elif s <= q2:
            bins[1].append(i)
        elif s <= q3:
            bins[2].append(i)
        else:
            bins[3].append(i)
    while len(anchors) < target:
        b = bins[len(anchors) % 4]
        if not b:
            b = list(range(n))
        anchors.add(b[rng.randrange(len(b))])
    return list(anchors)


def get_local_context(
    anchor: int,
    adj_norm: list[list[tuple[int, float]]],
    field: list[float],
):
    """Returnează (chart, d_local, field_local) sau None."""
    d_anchor = dijkstra(adj_norm, anchor)
    ranked = sorted(range(N_NODES), key=lambda i: d_anchor[i])
    local_nodes = [anchor]
    for i in ranked:
        if i == anchor:
            continue
        local_nodes.append(i)
        if len(local_nodes) >= LOCAL_M:
            break
    if len(local_nodes) < 12:
        return None

    d_all = [dijkstra(adj_norm, node) for node in local_nodes]
    m = len(local_nodes)
    d_local = [[d_all[i][local_nodes[j]] for j in range(m)] for i in range(m)]

    chart = geodesic_chart(d_local)
    if chart is None:
        return None

    field_local = [field[n] for n in local_nodes]
    return chart, d_local, field_local


# ---------------------------------------------------------------------------
# Test 1: Anisotropy Sweep
# ---------------------------------------------------------------------------

def run_anisotropy_sweep(
    adj_norm: list[list[tuple[int, float]]],
    field: list[float],
    aniso: float,
    seed: int,
) -> dict:
    anchors = choose_anchors(field, seed)
    cos_vals: list[float] = []

    for anchor in anchors:
        ctx = get_local_context(anchor, adj_norm, field)
        if ctx is None:
            continue
        chart, d_local, field_local = ctx
        field_s0 = smooth_local(d_local, field_local, S0)
        gh = fit_grad_hess(chart, field_s0)
        if gh is None:
            continue
        grad_vec, hess = gh
        a_raw = (-grad_vec[0], -grad_vec[1])

        g11, g12, g22 = metric_from_hessian(hess[0], hess[1], hess[2], anisotropy_keep=aniso)
        inv = inv2x2(g11, g12, g22)
        if inv is None:
            continue
        inv11, inv12, inv22 = inv
        a_metric = (
            -(inv11 * grad_vec[0] + inv12 * grad_vec[1]),
            -(inv12 * grad_vec[0] + inv22 * grad_vec[1]),
        )
        c = cosine(a_metric, a_raw)
        if math.isfinite(c):
            cos_vals.append(c)

    return {
        "aniso": aniso,
        "median_cos": median_f(cos_vals),
        "p10_cos": p10_f(cos_vals),
        "n": len(cos_vals),
    }


# ---------------------------------------------------------------------------
# Test 2: Cross-Metric Margin
# ---------------------------------------------------------------------------

def run_cross_metric(
    adj_norm: list[list[tuple[int, float]]],
    field_qng: list[float],
    field_ctrl: list[float],
    aniso: float,
    seed: int,
) -> dict:
    """
    Pentru fiecare anchor:
    - alpha_self = cos_sim(-g_qng^{-1}·grad_qng, -grad_qng)
    - alpha_cross = cos_sim(-g_ctrl^{-1}·grad_qng, -grad_qng)
    - margin = alpha_self - alpha_cross

    Gate D3b_cross trece dacă median(margin) > MARGIN_THRESHOLD.
    """
    anchors = choose_anchors(field_qng, seed)
    margins: list[float] = []
    alpha_selfs: list[float] = []
    alpha_crosses: list[float] = []

    for anchor in anchors:
        # Context pentru câmpul QNG
        ctx_qng = get_local_context(anchor, adj_norm, field_qng)
        if ctx_qng is None:
            continue
        chart, d_local, field_qng_local = ctx_qng

        # Câmpul ctrl pe aceleași noduri locale
        d_anchor = dijkstra(adj_norm, anchor)
        ranked = sorted(range(N_NODES), key=lambda i: d_anchor[i])
        local_nodes = [anchor]
        for i in ranked:
            if i == anchor:
                continue
            local_nodes.append(i)
            if len(local_nodes) >= LOCAL_M:
                break
        field_ctrl_local = [field_ctrl[n] for n in local_nodes]

        # Gradient QNG (referință pentru ambele cosine)
        field_qng_s0 = smooth_local(d_local, field_qng_local, S0)
        gh_qng = fit_grad_hess(chart, field_qng_s0)
        if gh_qng is None:
            continue
        grad_qng, hess_qng = gh_qng
        a_raw = (-grad_qng[0], -grad_qng[1])

        # Metrica self (din QNG)
        g11s, g12s, g22s = metric_from_hessian(
            hess_qng[0], hess_qng[1], hess_qng[2], anisotropy_keep=aniso)
        inv_s = inv2x2(g11s, g12s, g22s)
        if inv_s is None:
            continue
        a_self = (
            -(inv_s[0] * grad_qng[0] + inv_s[1] * grad_qng[1]),
            -(inv_s[1] * grad_qng[0] + inv_s[2] * grad_qng[1]),
        )
        alpha_self = cosine(a_self, a_raw)

        # Metrica ctrl (din câmpul de control)
        field_ctrl_s0 = smooth_local(d_local, field_ctrl_local, S0)
        gh_ctrl = fit_grad_hess(chart, field_ctrl_s0)
        if gh_ctrl is None:
            continue
        grad_ctrl, hess_ctrl = gh_ctrl
        g11c, g12c, g22c = metric_from_hessian(
            hess_ctrl[0], hess_ctrl[1], hess_ctrl[2], anisotropy_keep=aniso)
        inv_c = inv2x2(g11c, g12c, g22c)
        if inv_c is None:
            continue
        # Aplică metrica ctrl pe gradientul QNG (cross-test)
        a_cross = (
            -(inv_c[0] * grad_qng[0] + inv_c[1] * grad_qng[1]),
            -(inv_c[1] * grad_qng[0] + inv_c[2] * grad_qng[1]),
        )
        alpha_cross = cosine(a_cross, a_raw)

        if math.isfinite(alpha_self) and math.isfinite(alpha_cross):
            margins.append(alpha_self - alpha_cross)
            alpha_selfs.append(alpha_self)
            alpha_crosses.append(alpha_cross)

    med_margin = median_f(margins)
    p10_margin = p10_f(margins)
    d3b_pass = math.isfinite(med_margin) and med_margin > MARGIN_THRESHOLD

    return {
        "median_alpha_self": median_f(alpha_selfs),
        "median_alpha_cross": median_f(alpha_crosses),
        "median_margin": med_margin,
        "p10_margin": p10_margin,
        "d3b_cross_pass": d3b_pass,
        "n": len(margins),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fmt(v) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        if math.isnan(v):
            return "nan"
        return f"{v:.4f}"
    return str(v)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D3b Candidate Gate v1")
    print(f"Seed: {ATTACK_SEED} | Dataset seed: {DATASET_SEED} | Margin threshold: {MARGIN_THRESHOLD}")
    print()

    rng_coords = random.Random(DATASET_SEED + 17)
    coords = [
        (rng_coords.uniform(-SPREAD, SPREAD), rng_coords.uniform(-SPREAD, SPREAD))
        for _ in range(N_NODES)
    ]

    _, adj_list, med_edge = build_graph(DATASET_SEED)
    adj_norm = [[(j, w / med_edge) for j, w in row] for row in adj_list]

    FIELDS = [
        ("BASELINE_QNG", field_qng_sigma),
        ("C1_RAND_GAUSS", field_random_gaussians),
        ("C2_LINEAR", field_linear_gradient),
        ("C3_SINUS", field_sinusoidal),
        ("C4_QUADRATIC", field_quadratic_bowl),
        ("C5_PURE_NOISE", field_pure_noise),
    ]

    computed_fields = {fid: fn(coords, ATTACK_SEED) for fid, fn in FIELDS}

    # -----------------------------------------------------------------------
    # TEST 1: Anisotropy Sweep
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("TEST 1: Anisotropy Sweep — la ce keep apare discriminanța?")
    print("=" * 70)

    sweep_rows = []
    for fid, _ in FIELDS:
        field = computed_fields[fid]
        row_data = {"field_id": fid}
        for aniso in ANISO_VALUES:
            res = run_anisotropy_sweep(adj_norm, field, aniso, ATTACK_SEED)
            row_data[f"med_cos_aniso{aniso}"] = res["median_cos"]
            row_data[f"p10_cos_aniso{aniso}"] = res["p10_cos"]

        print(f"\n[{fid}]")
        for aniso in ANISO_VALUES:
            mc = row_data[f"med_cos_aniso{aniso}"]
            p10 = row_data[f"p10_cos_aniso{aniso}"]
            d3_pass = math.isfinite(mc) and mc >= 0.90
            print(f"  aniso={aniso:.1f}: med_cos={fmt(mc)}  p10={fmt(p10)}  D3_would_pass={d3_pass}")
        sweep_rows.append(row_data)

    # Verificare discriminanță la aniso=1.0
    qng_cos_10 = next(r["med_cos_aniso1.0"] for r in sweep_rows if r["field_id"] == "BASELINE_QNG")
    noise_cos_10 = next(r["med_cos_aniso1.0"] for r in sweep_rows if r["field_id"] == "C5_PURE_NOISE")
    gap_10 = qng_cos_10 - noise_cos_10 if (math.isfinite(qng_cos_10) and math.isfinite(noise_cos_10)) else float("nan")

    print(f"\nDISCRIMINANȚĂ la aniso=1.0: QNG={fmt(qng_cos_10)} vs Noise={fmt(noise_cos_10)} gap={fmt(gap_10)}")
    if math.isfinite(gap_10) and gap_10 > 0.05:
        print("=> Discriminanță confirmată la aniso=1.0 (gap > 0.05)")
    else:
        print("=> Discriminanță INSUFICIENTĂ chiar și la aniso=1.0 — problema e mai profundă")

    # -----------------------------------------------------------------------
    # TEST 2: Cross-Metric Margin (la toate valorile aniso)
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST 2: Cross-Metric Margin — g_qng vs g_ctrl pe grad_qng")
    print(f"Gate D3b_cross trece dacă median(margin) > {MARGIN_THRESHOLD}")
    print("=" * 70)

    field_qng = computed_fields["BASELINE_QNG"]
    cross_rows = []

    for aniso in ANISO_VALUES:
        print(f"\n[aniso={aniso:.1f}]")
        for ctrl_id, _ in FIELDS[1:]:  # exclude BASELINE_QNG ca ctrl
            field_ctrl = computed_fields[ctrl_id]
            res = run_cross_metric(adj_norm, field_qng, field_ctrl, aniso, ATTACK_SEED)
            verdict = "PASS" if res["d3b_cross_pass"] else "FAIL"
            print(
                f"  ctrl={ctrl_id:15s}  "
                f"self={fmt(res['median_alpha_self'])}  "
                f"cross={fmt(res['median_alpha_cross'])}  "
                f"margin={fmt(res['median_margin'])}  "
                f"D3b={verdict}"
            )
            cross_rows.append({
                "aniso": str(aniso),
                "ctrl_field": ctrl_id,
                "median_alpha_self": fmt(res["median_alpha_self"]),
                "median_alpha_cross": fmt(res["median_alpha_cross"]),
                "median_margin": fmt(res["median_margin"]),
                "p10_margin": fmt(res["p10_margin"]),
                "d3b_cross_pass": str(res["d3b_cross_pass"]),
            })

    # -----------------------------------------------------------------------
    # Scrie artifacts
    # -----------------------------------------------------------------------
    # Sweep CSV
    sweep_fieldnames = ["field_id"]
    for aniso in ANISO_VALUES:
        sweep_fieldnames += [f"med_cos_aniso{aniso}", f"p10_cos_aniso{aniso}"]
    sweep_csv = OUT_DIR / "anisotropy_sweep.csv"
    with sweep_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sweep_fieldnames)
        w.writeheader()
        for row in sweep_rows:
            w.writerow({k: fmt(v) if isinstance(v, float) else v for k, v in row.items()})

    # Cross CSV
    cross_csv = OUT_DIR / "cross_metric_margin.csv"
    cross_fieldnames = ["aniso", "ctrl_field", "median_alpha_self", "median_alpha_cross",
                        "median_margin", "p10_margin", "d3b_cross_pass"]
    with cross_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cross_fieldnames)
        w.writeheader()
        for row in cross_rows:
            w.writerow(row)

    # Summary JSON
    summary = {
        "test_id": "d3b-candidate-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "attack_seed": ATTACK_SEED,
        "dataset_seed": DATASET_SEED,
        "margin_threshold": MARGIN_THRESHOLD,
        "gap_qng_vs_noise_at_aniso1": gap_10,
        "sweep_rows": sweep_rows,
        "cross_rows": cross_rows,
    }
    (OUT_DIR / "d3b_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )

    # -----------------------------------------------------------------------
    # Verdict final
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("VERDICT FINAL")
    print("=" * 70)

    # Câte cross-tests trec la aniso=1.0?
    cross_pass_10 = [r for r in cross_rows if r["aniso"] == "1.0" and r["d3b_cross_pass"] == "True"]
    cross_total_10 = [r for r in cross_rows if r["aniso"] == "1.0"]
    print(f"Cross-metric pass la aniso=1.0: {len(cross_pass_10)}/{len(cross_total_10)}")

    if math.isfinite(gap_10):
        print(f"Aniso sweep gap QNG vs Noise: {fmt(gap_10)}")
        if gap_10 > 0.05:
            print("Concluzii: Discriminanță apare la aniso=1.0. D3 curent e spart prin shrinkage.")
            print("Recomandare: reduce anisotropy_keep la 1.0 SAU adoptă D3b_cross ca gate.")
        else:
            print("Concluzie: Problema e mai profundă decât shrinkage-ul.")
            print("D3 e spart structural — nu prin parametri, ci prin design.")
            print("Niciun ajustaj al anisotropy_keep nu poate repara gate-ul.")

    print(f"\nArtifacts: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
