#!/usr/bin/env python3
"""
D3 Attack Test v1 — Circularitate Gate.

Întrebarea: Este D3 discriminant față de câmpul Sigma QNG, sau trece pentru orice
câmp scalar neted arbitrar?

Metodă:
- Folosim ACELAȘI graf și ACEEAȘI structură locală ca în hardening v4 (DS-002).
- Înlocuim câmpul Sigma cu 5 câmpuri de control diferite:
    C1: Random Gaussian mixture (centre random, nu centrele QNG)
    C2: Linear gradient (câmp liniar simplu)
    C3: Sinusoidal (câmp periodic)
    C4: Quadratic bowl (paraboloid)
    C5: Pure noise (zgomot Gaussian brut, nesmoothed)
- Rulăm pipeline-ul D3 complet pe fiecare câmp de control.
- Raportăm: median cos_sim, p10 cos_sim, pass/fail D3, median cos_sim shuffled.

Predicție (hypothesis): C1-C4 vor trece D3. Dacă e adevărat, D3 nu testează
că Sigma QNG e fizic special — testează că pipeline-ul e intern consistent
pentru orice câmp neted.

Pre-registration: 05_validation/pre-registrations/d3-attack-v1.md (scris anterior rulării)
Seed: 9999 (fix, declarat)
"""

from __future__ import annotations

import csv
import heapq
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "d3-attack-v1"
PRE_REG_DIR = ROOT / "05_validation" / "pre-registrations"

ATTACK_SEED = 9999
DATASET_SEED = 3401  # identic cu hardening v4 — ACELAȘI graf
N_NODES = 280
K_NEIGHBORS = 8
SPREAD = 2.3
SAMPLES = 72
LOCAL_M = 20


# ---------------------------------------------------------------------------
# Helpers (identice cu hardening v4 — nicio modificare)
# ---------------------------------------------------------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


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


def median_f(values: list[float]) -> float:
    return quantile(values, 0.5)


def p10_f(values: list[float]) -> float:
    return quantile(values, 0.10)


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


def fit_ridge(features: list[list[float]], targets: list[float], lam: float = 1e-8) -> list[float]:
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


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    return g22 / det, -g12 / det, g11 / det


def frob2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


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


def smooth_sigma_local(dmat: list[list[float]], sigma_local: list[float], s: float) -> list[float]:
    m = len(dmat)
    out = [0.0] * m
    for i in range(m):
        num = den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * sigma_local[j]
            den += w
        out[i] = num / max(den, 1e-16)
    return out


def estimate_sigma_grad_hessian(
    chart: list[tuple[float, float]], sigma_local: list[float]
) -> tuple[tuple[float, float], tuple[float, float, float]] | None:
    feats: list[list[float]] = []
    targ: list[float] = []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
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
    """Identic cu metric_from_sigma_hessian_v4 din hardening v4."""
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

    def norm(v: tuple[float, float]) -> tuple[float, float]:
        n = math.hypot(v[0], v[1])
        if n <= 1e-18:
            return (1.0, 0.0)
        return v[0] / n, v[1] / n

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

    iso = 1.0 / math.sqrt(2.0)
    keep = clamp(anisotropy_keep, 0.0, 1.0)
    g11 = keep * g11 + (1.0 - keep) * iso
    g22 = keep * g22 + (1.0 - keep) * iso
    g12 = keep * g12
    return g11, g12, g22


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
        yi = yi_abs if abs(p_plus - d2i) <= abs(p_minus - d2i) else -yi_abs
        coords[i] = (xi, yi)
    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


# ---------------------------------------------------------------------------
# Graf (identic cu DS-002 din hardening v4, FĂRĂ coupling Sigma în muchii)
# NOTĂ: hardening v4 folosește edge weights cu Sigma gradient coupling.
# Testul de atac rulează DOUĂ variante:
#   variant="coupled"   — graf cu coupling (ca hardening v4, cu câmpul de control)
#   variant="uncoupled" — graf pur geometric (fără coupling)
# ---------------------------------------------------------------------------

def build_base_graph(seed: int) -> tuple[list[tuple[float, float]], list[list[tuple[int, float]]], float]:
    """Graf pur geometric (k-NN pe distanțe euclidiene, fără coupling)."""
    rng = random.Random(seed + 17)
    coords: list[tuple[float, float]] = []
    for _ in range(N_NODES):
        coords.append((rng.uniform(-SPREAD, SPREAD), rng.uniform(-SPREAD, SPREAD)))

    adj: list[dict[int, float]] = [dict() for _ in range(N_NODES)]
    edge_lengths: list[float] = []
    for i in range(N_NODES):
        xi, yi = coords[i]
        dists = []
        for j in range(N_NODES):
            if j == i:
                continue
            xj, yj = coords[j]
            dists.append((math.hypot(xi - xj, yi - yj), j))
        dists.sort()
        for d, j in dists[:K_NEIGHBORS]:
            w = max(d, 1e-6)
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)

    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    med_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, adj_list, max(med_edge, 1e-9)


def build_coupled_graph(
    seed: int, field: list[float]
) -> tuple[list[tuple[float, float]], list[list[tuple[int, float]]], float]:
    """Graf cu coupling pe câmpul de control (identic cu hardening v4 dar cu field în loc de sigma)."""
    rng = random.Random(seed + 17)
    coords: list[tuple[float, float]] = []
    for _ in range(N_NODES):
        coords.append((rng.uniform(-SPREAD, SPREAD), rng.uniform(-SPREAD, SPREAD)))

    adj: list[dict[int, float]] = [dict() for _ in range(N_NODES)]
    edge_lengths: list[float] = []
    for i in range(N_NODES):
        xi, yi = coords[i]
        dists = []
        for j in range(N_NODES):
            if j == i:
                continue
            xj, yj = coords[j]
            dists.append((math.hypot(xi - xj, yi - yj), j))
        dists.sort()
        for d, j in dists[:K_NEIGHBORS]:
            base = max(d, 1e-6)
            w = base * (1.0 + 0.10 * abs(field[i] - field[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)

    adj_list = [[(j, w) for j, w in m.items()] for m in adj]
    med_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, adj_list, max(med_edge, 1e-9)


# ---------------------------------------------------------------------------
# Câmpuri de control
# ---------------------------------------------------------------------------

def field_qng_sigma(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """Câmpul Sigma original QNG (baseline de referință)."""
    rng = random.Random(seed + 17)
    out = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        out.append(clamp(s, 0.0, 1.0))
    return out


def field_random_gaussians(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """C1: Sumă de Gaussiene cu centre complet random (nu centrele QNG)."""
    rng = random.Random(seed + 1001)
    n_centers = 4
    centers = [(rng.uniform(-2.0, 2.0), rng.uniform(-2.0, 2.0)) for _ in range(n_centers)]
    amplitudes = [rng.uniform(0.3, 0.9) for _ in range(n_centers)]
    widths = [rng.uniform(0.5, 1.5) for _ in range(n_centers)]
    out = []
    for x, y in coords:
        s = sum(
            a * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2.0 * w * w))
            for (cx, cy), a, w in zip(centers, amplitudes, widths)
        )
        s += rng.gauss(0.0, 0.01)
        out.append(clamp(s, 0.0, 1.0))
    return out


def field_linear_gradient(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """C2: Gradient liniar simplu — cel mai simplu câmp posibil."""
    rng = random.Random(seed + 2002)
    angle = rng.uniform(0, 2 * math.pi)
    dx, dy = math.cos(angle), math.sin(angle)
    vals = [dx * x + dy * y for x, y in coords]
    vmin, vmax = min(vals), max(vals)
    span = max(vmax - vmin, 1e-9)
    return [clamp((v - vmin) / span + rng.gauss(0.0, 0.005), 0.0, 1.0) for v in vals]


def field_sinusoidal(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """C3: Câmp sinusoidal periodic — complet diferit de Gaussiene."""
    rng = random.Random(seed + 3003)
    freq_x = rng.uniform(0.4, 1.2)
    freq_y = rng.uniform(0.4, 1.2)
    phase = rng.uniform(0, 2 * math.pi)
    out = []
    for x, y in coords:
        s = 0.5 * (1.0 + math.sin(freq_x * x + freq_y * y + phase))
        s += rng.gauss(0.0, 0.01)
        out.append(clamp(s, 0.0, 1.0))
    return out


def field_quadratic_bowl(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """C4: Paraboloid quadratic — structură concavă uniformă."""
    rng = random.Random(seed + 4004)
    cx, cy = rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5)
    vals = [-(( x - cx) ** 2 + (y - cy) ** 2) for x, y in coords]
    vmin, vmax = min(vals), max(vals)
    span = max(vmax - vmin, 1e-9)
    return [clamp((v - vmin) / span + rng.gauss(0.0, 0.005), 0.0, 1.0) for v in vals]


def field_pure_noise(coords: list[tuple[float, float]], seed: int) -> list[float]:
    """C5: Zgomot Gaussian pur — fără structură spațială. Trebuie să PICE D3."""
    rng = random.Random(seed + 5005)
    return [clamp(rng.gauss(0.5, 0.2), 0.0, 1.0) for _ in coords]


# ---------------------------------------------------------------------------
# Pipeline D3 (extras din hardening v4, fără modificări)
# ---------------------------------------------------------------------------

def choose_anchors_by_field(field: list[float], samples: int, seed: int) -> list[int]:
    rng = random.Random(seed + 71)
    n = len(field)
    target = max(8, min(samples, n))
    idx_sorted = sorted(range(n), key=lambda i: field[i], reverse=True)
    top_n = target // 2
    anchors = set(idx_sorted[:top_n])

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


def run_d3_on_field(
    coords: list[tuple[float, float]],
    adj_list: list[list[tuple[int, float]]],
    median_edge: float,
    field: list[float],
    seed: int,
) -> dict:
    """
    Rulează pipeline-ul D3 complet pe un câmp arbitrar.
    Returnează: median_cos_sim, p10_cos_sim, median_cos_shuf, d3_pass, d4_pass, anchors_used
    """
    adj_norm = [[(j, w / median_edge) for j, w in row] for row in adj_list]
    s0 = 1.0
    rng = random.Random(seed + 991)

    anchors = choose_anchors_by_field(field, SAMPLES, seed)

    cos_raw_vals: list[float] = []
    cos_shuf_vals: list[float] = []
    anchors_used = 0

    for anchor in anchors:
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
            continue

        # Pairwise distances locale
        d_all = [dijkstra(adj_norm, node) for node in local_nodes]
        m = len(local_nodes)
        d_local = [[d_all[i][local_nodes[j]] for j in range(m)] for i in range(m)]

        chart = geodesic_tangent_chart(d_local)
        if chart is None:
            continue

        field_local = [field[n] for n in local_nodes]
        field_s0 = smooth_sigma_local(d_local, field_local, s0)

        gh0 = estimate_sigma_grad_hessian(chart, field_s0)
        if gh0 is None:
            continue

        grad0_vec, hess0 = gh0
        a_raw = (-grad0_vec[0], -grad0_vec[1])

        g11, g12, g22 = metric_from_hessian(hess0[0], hess0[1], hess0[2])
        inv = inv2x2(g11, g12, g22)
        if inv is None:
            continue
        inv11, inv12, inv22 = inv

        a_metric = (
            -(inv11 * grad0_vec[0] + inv12 * grad0_vec[1]),
            -(inv12 * grad0_vec[0] + inv22 * grad0_vec[1]),
        )
        cos_raw = cosine(a_metric, a_raw)
        if math.isfinite(cos_raw):
            cos_raw_vals.append(cos_raw)

        # Negative control D4
        field_shuf = field_local[:]
        rng.shuffle(field_shuf)
        field_shuf_s0 = smooth_sigma_local(d_local, field_shuf, s0)
        gh_shuf = estimate_sigma_grad_hessian(chart, field_shuf_s0)
        if gh_shuf is not None:
            grad_shuf, hess_shuf = gh_shuf
            g11s, g12s, g22s = metric_from_hessian(hess_shuf[0], hess_shuf[1], hess_shuf[2])
            inv_shuf = inv2x2(g11s, g12s, g22s)
            if inv_shuf is not None:
                si11, si12, si22 = inv_shuf
                a_ms = (
                    -(si11 * grad_shuf[0] + si12 * grad_shuf[1]),
                    -(si12 * grad_shuf[0] + si22 * grad_shuf[1]),
                )
                cos_shuf = cosine(a_ms, a_raw)
                if math.isfinite(cos_shuf):
                    cos_shuf_vals.append(cos_shuf)

        anchors_used += 1

    med_cos = median_f(cos_raw_vals) if cos_raw_vals else float("nan")
    p10_cos = p10_f(cos_raw_vals) if cos_raw_vals else float("nan")
    med_shuf = median_f(cos_shuf_vals) if cos_shuf_vals else float("nan")

    d3_pass = (
        math.isfinite(med_cos) and math.isfinite(p10_cos)
        and med_cos >= 0.90
        and p10_cos >= 0.70
    )
    d4_pass = math.isfinite(med_shuf) and med_shuf < 0.55

    return {
        "anchors_used": anchors_used,
        "n_cos_raw": len(cos_raw_vals),
        "median_cos_sim": med_cos,
        "p10_cos_sim": p10_cos,
        "median_cos_sim_shuffled": med_shuf,
        "d3_pass": d3_pass,
        "d4_pass": d4_pass,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("D3 Attack Test v1")
    print(f"Seed: {ATTACK_SEED} | Dataset seed: {DATASET_SEED} | N={N_NODES} | Samples={SAMPLES}")
    print()

    # Construim coordonatele (necesare pentru câmpurile care depind de poziție)
    rng_coords = random.Random(DATASET_SEED + 17)
    coords = [
        (rng_coords.uniform(-SPREAD, SPREAD), rng_coords.uniform(-SPREAD, SPREAD))
        for _ in range(N_NODES)
    ]

    # Definim câmpurile de control
    control_fields = [
        ("BASELINE_QNG", "Sigma QNG original (referință)", field_qng_sigma),
        ("C1_RAND_GAUSS", "Random Gaussian mixture (centre random)", field_random_gaussians),
        ("C2_LINEAR", "Linear gradient (câmp liniar simplu)", field_linear_gradient),
        ("C3_SINUS", "Sinusoidal periodic", field_sinusoidal),
        ("C4_QUADRATIC", "Quadratic bowl (paraboloid)", field_quadratic_bowl),
        ("C5_PURE_NOISE", "Pure Gaussian noise (fără structură)", field_pure_noise),
    ]

    rows: list[dict] = []

    for field_id, field_desc, field_fn in control_fields:
        field = field_fn(coords, ATTACK_SEED)

        # Varianta uncoupled: graf pur geometric
        _, adj_uncoupled, med_uncoupled = build_base_graph(DATASET_SEED)
        res_uncoupled = run_d3_on_field(coords, adj_uncoupled, med_uncoupled, field, ATTACK_SEED)

        # Varianta coupled: graf cu coupling pe câmpul de control
        _, adj_coupled, med_coupled = build_coupled_graph(DATASET_SEED, field)
        res_coupled = run_d3_on_field(coords, adj_coupled, med_coupled, field, ATTACK_SEED)

        def fmt(v) -> str:
            if isinstance(v, bool):
                return str(v)
            if isinstance(v, float):
                if math.isnan(v):
                    return "nan"
                return f"{v:.4f}"
            return str(v)

        for variant, res in [("uncoupled", res_uncoupled), ("coupled", res_coupled)]:
            row = {
                "field_id": field_id,
                "variant": variant,
                "description": field_desc,
                "anchors_used": res["anchors_used"],
                "median_cos_sim": fmt(res["median_cos_sim"]),
                "p10_cos_sim": fmt(res["p10_cos_sim"]),
                "median_cos_sim_shuffled": fmt(res["median_cos_sim_shuffled"]),
                "d3_pass": fmt(res["d3_pass"]),
                "d4_pass": fmt(res["d4_pass"]),
            }
            rows.append(row)
            verdict_d3 = "PASS" if res["d3_pass"] else "FAIL"
            verdict_d4 = "PASS" if res["d4_pass"] else "FAIL"
            print(
                f"[{field_id}][{variant}] "
                f"med_cos={fmt(res['median_cos_sim'])} p10={fmt(res['p10_cos_sim'])} "
                f"shuf={fmt(res['median_cos_sim_shuffled'])} "
                f"D3={verdict_d3} D4={verdict_d4} "
                f"anchors={res['anchors_used']}"
            )

        print()

    # Scrie CSV
    csv_path = OUT_DIR / "d3_attack_results.csv"
    fieldnames = [
        "field_id", "variant", "description", "anchors_used",
        "median_cos_sim", "p10_cos_sim", "median_cos_sim_shuffled",
        "d3_pass", "d4_pass",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    # Scrie JSON summary
    summary = {
        "test_id": "d3-attack-v1",
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "attack_seed": ATTACK_SEED,
        "dataset_seed": DATASET_SEED,
        "n_nodes": N_NODES,
        "samples": SAMPLES,
        "hypothesis": (
            "D3 este o tautologie: trece pentru orice câmp scalar neted, "
            "nu doar pentru Sigma QNG. Dacă C1-C4 trec D3, gate-ul nu e discriminant fizic."
        ),
        "results": rows,
    }
    json_path = OUT_DIR / "d3_attack_summary.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Rezultate: {OUT_DIR}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")

    # Verdict final
    control_d3_passes = [
        r["d3_pass"] == "True"
        for r in rows
        if r["field_id"] not in ("BASELINE_QNG", "C5_PURE_NOISE")
    ]
    n_pass = sum(control_d3_passes)
    n_total = len(control_d3_passes)
    print()
    print(f"VERDICT: {n_pass}/{n_total} câmpuri de control (C1-C4) trec D3.")
    if n_pass >= 3:
        print("=> CONFIRMAT: D3 este non-discriminant. Trece pentru câmpuri scalare arbitrare netede.")
    elif n_pass == 0:
        print("=> INFIRMAT: D3 este discriminant. Câmpurile de control pică.")
    else:
        print("=> PARȚIAL: Rezultat mixt. Necesită analiză suplimentară.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
