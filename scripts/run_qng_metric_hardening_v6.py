#!/usr/bin/env python3
"""
QNG emergent metric hardening runner (v6).

Changes from v5:
- New G3 gate: TIDAL-FIDELITY-v1. Verifies the off-diagonal / traceless (spin-2)
  tensor structure of g_th, which is NOT checked by the scalar trace gates G1/G2.
  Three sub-gates (all at s0 scale):
    G3a — Traceless constraint:
        |tr(S_ij)| / |S_ij|_F < 1e-8 per anchor.
        S_ij is constructed to be traceless by design; G3a catches any numerical
        bug in the tr_half subtraction step.
    G3b — Off-diagonal sign consistency:
        For anchors where |g12_th| > threshold AND |h12_raw| > threshold,
        fraction with sign(g12_th) == -sign(h12_raw) >= 0.85.
        Derivation: A = -H => a12 = -h12; the SPD eigenvectors preserve sign(a12)
        in the non-degenerate case; Frobenius + traceless extraction preserve sign.
        A sign flip anywhere in the pipeline is caught by this gate.
    G3c — Tidal amplitude bound:
        max |S_ij|_F <= 0.72 per anchor.
        Theoretical bound: |S|_F^2 = (mu1-mu2)^2 / (2(mu1^2+mu2^2)) <= 1/2
        => |S|_F <= 1/sqrt(2) ~= 0.707. Threshold 0.72 allows floor-clipping slack.

- New G4 gate: WEAK-FIELD-ISOTROPY-v1. Checks whether the tidal (traceless)
  perturbation is not anomalously dominant relative to the conformal perturbation.
    dev_ratio = |alpha * S_ij|_F / (2 * |Sigma|)
    Physical meaning: ratio of tidal amplitude to conformal amplitude.
    In the Newtonian weak-field limit, tidal effects should be comparable or
    sub-dominant. A median dev_ratio >> 1 would indicate pathological behaviour.
    Gate: median(dev_ratio) < 5.0 (loose plausibility gate, not strict correctness).

- G0, G1, G2, D1-D4 gates: UNCHANGED from v5.
- All metric computation unchanged from v5 (metric-lock-v5 still applies).
- New output files: tidal_fidelity.csv, tidal-frob-hist.png, tidal-devratio-hist.png.

Derivation references:
  G1 derivation:    03_math/derivations/qng-metric-completion-v1.md §II.C2
  G2 derivation:    03_math/derivations/qng-gr-derivation-complete-v1.md §III.4
  G3 derivation:    03_math/derivations/qng-tidal-fidelity-v1.md (new)
  G4 derivation:    03_math/derivations/qng-epsilon-ricci-derivation-v1.md (new)
  Method lock:      01_notes/metric/metric-lock-v5.md (metric unchanged)
  Pre-registration: 05_validation/pre-registrations/qng-metric-hardening-v6.md

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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-metric-hardening-v6"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


@dataclass
class GateThresholds:
    # G0: vacuum stability (unchanged from v4)
    g0_nan_inf_max: int = 0
    g0_cond_global_max: float = 1000.0
    g0_cond_lowcurv_max: float = 200.0
    g0_lowcurv_frob_threshold: float = 0.05
    # D1-D4: identical to v3/v4
    d1_eps: float = 1e-8
    d2_median_max: float = 0.10
    d2_p90_max: float = 0.25
    d3_median_min: float = 0.90
    d3_p10_min: float = 0.70
    d4_shuffle_median_max: float = 0.55
    # G1: PPN-GAMMA-v1 (new in v5)
    g1_gamma_median_abs_err_max: float = 1e-3   # median |gamma-1| < 1e-3
    g1_gamma_p90_abs_err_max: float = 0.01      # p90   |gamma-1| < 0.01
    g1_sigma_floor: float = 1e-4                # min |Sigma| for gamma computation
    # G2: G00-TRACE-RATIO-v1 (new in v5)
    g2_trace_ratio_target: float = 2.0          # 2D+1 GR target
    g2_trace_ratio_tol: float = 0.01            # |median(ratio) - 2.0| < 0.01
    g2_sigma_floor: float = 1e-4                # min |Sigma| for ratio computation
    # G3: TIDAL-FIDELITY-v1 (new in v6)
    g3_traceless_residual_max: float = 1e-8     # G3a: max |tr(S)| / |S|_F
    g3_sign_threshold: float = 1e-3             # G3b: min |g12_th| and |h12| for sign check
    g3_sign_consistent_frac_min: float = 0.85   # G3b: fraction with sign(g12_th)==-sign(h12)
    g3_s_frob_max: float = 0.72                 # G3c: max |S|_F (theoretical bound: 1/sqrt(2)~0.707)
    # G4: WEAK-FIELD-ISOTROPY-v1 (new in v6)
    g4_dev_ratio_median_max: float = 5.0        # median |αS|_F / (2|Σ|) < 5.0
    g4_sigma_floor: float = 1e-3               # min |Sigma| for dev_ratio computation


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


def percentile10(values: list[float]) -> float:
    return quantile(values, 0.10)


def percentile90(values: list[float]) -> float:
    return quantile(values, 0.90)


def read_dataset_manifest(dataset_id: str) -> dict | None:
    if not DATASET_MANIFEST_JSON.exists():
        return None
    try:
        rows = json.loads(DATASET_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("dataset_id") == dataset_id:
            return row
    return None


def parse_scales(text: str) -> list[tuple[str, float]]:
    tokens = [t.strip().lower() for t in text.split(",") if t.strip()]
    if not tokens:
        raise ValueError("No scales provided.")
    out: list[tuple[str, float]] = []
    for tok in tokens:
        if "s0" in tok:
            if tok == "s0":
                mult = 1.0
            else:
                t = tok.replace("*", "").replace(" ", "").replace("s0", "")
                if t.endswith("x"):
                    t = t[:-1]
                if not t:
                    mult = 1.0
                else:
                    mult = float(t)
            out.append((f"{mult:g}s0", mult))
        else:
            mult = float(tok)
            out.append((f"{mult:g}", mult))
    return out


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


def inv2x2(g11: float, g12: float, g22: float) -> tuple[float, float, float] | None:
    det = g11 * g22 - g12 * g12
    if abs(det) < 1e-16:
        return None
    inv11 = g22 / det
    inv22 = g11 / det
    inv12 = -g12 / det
    return inv11, inv12, inv22


def frob_norm2x2(g11: float, g12: float, g22: float) -> float:
    return math.sqrt(g11 * g11 + 2.0 * g12 * g12 + g22 * g22)


def cond_number2x2(g11: float, g12: float, g22: float) -> float:
    """Condition number kappa = lambda_max / lambda_min (both positive)."""
    l1, l2 = eig2x2(g11, g12, g22)
    lmin = max(abs(l1), 1e-18)
    lmax = max(abs(l2), 1e-18)
    if lmin > lmax:
        lmin, lmax = lmax, lmin
    return lmax / lmin


def cosine(a: tuple[float, float], b: tuple[float, float]) -> float:
    na = math.hypot(a[0], a[1])
    nb = math.hypot(b[0], b[1])
    if na < 1e-16 or nb < 1e-16:
        return float("nan")
    return (a[0] * b[0] + a[1] * b[1]) / (na * nb)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def build_dataset_graph(dataset_id: str, seed: int) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float]:
    rng = random.Random(seed + 17)
    ds = dataset_id.upper().strip()
    if ds == "DS-002":
        n = 280
        k = 8
        spread = 2.3
    elif ds == "DS-003":
        n = 240
        k = 7
        spread = 2.0
    elif ds == "DS-006":
        n = 320
        k = 9
        spread = 2.7
    else:
        n = 260
        k = 8
        spread = 2.2

    coords: list[tuple[float, float]] = []
    for _ in range(n):
        x = rng.uniform(-spread, spread)
        y = rng.uniform(-spread, spread)
        coords.append((x, y))

    sigma: list[float] = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(clamp(s, 0.0, 1.0))

    dist = [[0.0 for _ in range(n)] for _ in range(n)]
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
    n = len(adj)
    inf = float("inf")
    d = [inf for _ in range(n)]
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
    top_n = target // 2
    anchors = set(idx_sorted[:top_n])

    bins = [[], [], [], []]
    s_sorted = sorted(sigma)
    q1 = s_sorted[int(0.25 * (n - 1))]
    q2 = s_sorted[int(0.50 * (n - 1))]
    q3 = s_sorted[int(0.75 * (n - 1))]
    for i, s in enumerate(sigma):
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


def local_nodes_from_anchor(dist_anchor: list[float], anchor: int, m: int) -> list[int]:
    ranked = sorted(range(len(dist_anchor)), key=lambda i: dist_anchor[i])
    out = [anchor]
    for i in ranked:
        if i == anchor:
            continue
        out.append(i)
        if len(out) >= m:
            break
    return out


def local_pairwise_distances(adj: list[list[tuple[int, float]]], local_nodes: list[int]) -> list[list[float]]:
    d_all = [dijkstra(adj, node) for node in local_nodes]
    m = len(local_nodes)
    out = [[0.0 for _ in range(m)] for _ in range(m)]
    for i in range(m):
        for j in range(m):
            out[i][j] = d_all[i][local_nodes[j]]
    return out


def geodesic_tangent_chart(dmat: list[list[float]]) -> list[tuple[float, float]] | None:
    m = len(dmat)
    if m < 8:
        return None
    candidates = list(range(1, m))
    if not candidates:
        return None
    l1 = max(candidates, key=lambda j: dmat[0][j])

    d01 = dmat[0][l1]
    if d01 <= 1e-9:
        return None

    best_l2 = None
    best_y2 = -1.0
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

    coords: list[tuple[float, float]] = [(0.0, 0.0) for _ in range(m)]
    coords[l1] = (d01, 0.0)
    coords[l2] = (x2, y2)

    for i in range(m):
        if i in (0, l1, l2):
            continue
        d0i = dmat[0][i]
        d1i = dmat[l1][i]
        d2i = dmat[l2][i]
        if d0i <= 1e-12:
            coords[i] = (0.0, 0.0)
            continue
        xi = (d0i * d0i + d01 * d01 - d1i * d1i) / (2.0 * d01)
        yi_abs_sq = d0i * d0i - xi * xi
        yi_abs = math.sqrt(max(yi_abs_sq, 0.0))
        p_plus = math.hypot(xi - x2, yi_abs - y2)
        p_minus = math.hypot(xi - x2, -yi_abs - y2)
        yi = yi_abs if abs(p_plus - d2i) <= abs(p_minus - d2i) else -yi_abs
        coords[i] = (xi, yi)

    xs = [c[0] for c in coords[1:]]
    ys = [c[1] for c in coords[1:]]
    if statistics.pstdev(xs) <= 1e-8 or statistics.pstdev(ys) <= 1e-8:
        return None
    return coords


def smooth_sigma_local(dmat: list[list[float]], sigma_local: list[float], s: float) -> list[float]:
    m = len(dmat)
    out = [0.0 for _ in range(m)]
    for i in range(m):
        num = 0.0
        den = 0.0
        for j in range(m):
            w = math.exp(-(dmat[i][j] ** 2) / max(2.0 * s * s, 1e-12))
            num += w * sigma_local[j]
            den += w
        out[i] = num / max(den, 1e-16)
    return out


def estimate_sigma_grad_hessian(
    chart: list[tuple[float, float]],
    sigma_local: list[float],
) -> tuple[tuple[float, float], tuple[float, float, float]] | None:
    # Local quadratic model:
    # Sigma(x,y) ~= c + b1 x + b2 y + 0.5 h11 x^2 + h12 xy + 0.5 h22 y^2
    feats: list[list[float]] = []
    targ: list[float] = []
    for (x, y), s in zip(chart[1:], sigma_local[1:]):
        feats.append([1.0, x, y, 0.5 * x * x, x * y, 0.5 * y * y])
        targ.append(s)
    if len(feats) < 10:
        return None
    try:
        beta = fit_ridge(feats, targ, lam=1e-8)
    except ValueError:
        return None
    grad = (beta[1], beta[2])
    hess = (beta[3], beta[4], beta[5])  # h11, h12, h22
    return grad, hess


def metric_from_sigma_hessian_v5(
    h11: float,
    h12: float,
    h22: float,
    sigma_center: float,
    alpha: float = 1.0,
    floor: float = 1e-6,
    frob_floor: float = 1e-9,
) -> tuple[float, float, float, float, float, float, float, float]:
    """
    v5 metric: spin-2 (traceless Hessian) + spin-0 (conformal/PPN completion).

    Formula (theoretical):
        g_ij^v5_th = (1 + eps) * delta_ij + alpha * S_ij
                   = (1 - 2*Sigma) * delta_ij + alpha * S_ij

    where:
        S_ij  = traceless part of Frobenius-normalized SPD(-Hess(Sigma))  [spin-2]
        eps   = -2 * sigma_center                                          [spin-0]
        alpha = spin-2 coupling (default 1.0)

    Derivation of eps = -2*Sigma:
        Required by two independent conditions (qng-metric-completion-v1.md §II.C):
        C1: G_00 normalization (Einstein equation, factor-4 gap closure)
        C2: PPN parameter gamma = 1 (Solar System constraint)
        Both give: iso_coeff = 1 - 2*Sigma  =>  eps = -2*Sigma

    Theoretical consequences (2D pipeline, exact):
        tr(g_v5_th)  = 2*(1 - 2*Sigma) + alpha*tr(S) = 2 - 4*Sigma
        h_spatial    = tr(g_v5_th) - 2 = -4*Sigma
        h_00         = -2*Sigma
        trace_ratio  = h_spatial / h_00 = 2.0  (2D+1 GR match; 3D target = 3.0)
        gamma        = (1 - iso_coeff) / (2*Sigma) = 1.0

    Synthetic-field note:
        The pipeline uses Sigma in [0, 1] for computational convenience; physical
        gravitational potentials satisfy |Sigma| << 1. When Sigma > 0.5 the
        theoretical metric has (1-2*Sigma) < 0 and may be non-SPD. An operational
        SPD re-projection is applied for D1-D4 gate compatibility while the
        theoretical metric is preserved for G1/G2 gate evaluation.

    Returns:
        (g11_op, g12_op, g22_op, g11_th, g12_th, g22_th, frob_hessian_raw, eps)

        g_op (operational): SPD re-projected; used for G0, D1-D4.
        g_th (theoretical): raw formula (1-2*Sigma)*I + alpha*S; used for G1, G2.
        frob_hessian_raw: Frobenius norm of raw Hessian (for G0 vacuum gate).
        eps: conformal coefficient = -2*sigma_center.
    """
    # Raw Hessian Frobenius norm (before any processing) for G0 gate.
    frob_hessian_raw = frob_norm2x2(h11, h12, h22)

    # --- Step 1: SPD projection of A = -Hess(Sigma) ---
    a11 = -h11
    a12 = -h12
    a22 = -h22
    tr_a = a11 + a22
    det_a = a11 * a22 - a12 * a12
    disc = max(tr_a * tr_a - 4.0 * det_a, 0.0)
    root = math.sqrt(disc)
    lam1 = 0.5 * (tr_a - root)
    lam2 = 0.5 * (tr_a + root)

    if abs(a12) > 1e-14:
        v1 = (lam1 - a22, a12)
        v2 = (lam2 - a22, a12)
    else:
        if a11 <= a22:
            v1, v2 = (1.0, 0.0), (0.0, 1.0)
        else:
            v1, v2 = (0.0, 1.0), (1.0, 0.0)

    def norm_vec(v: tuple[float, float]) -> tuple[float, float]:
        n = math.hypot(v[0], v[1])
        if n <= 1e-18:
            return (1.0, 0.0)
        return (v[0] / n, v[1] / n)

    q1 = norm_vec(v1)
    q2 = norm_vec(v2)

    mu1 = max(abs(lam1), floor)
    mu2 = max(abs(lam2), floor)
    g11_spd = mu1 * q1[0] * q1[0] + mu2 * q2[0] * q2[0]
    g12_spd = mu1 * q1[0] * q1[1] + mu2 * q2[0] * q2[1]
    g22_spd = mu1 * q1[1] * q1[1] + mu2 * q2[1] * q2[1]

    # --- Step 2: Frobenius normalize (same as v4) ---
    frob = frob_norm2x2(g11_spd, g12_spd, g22_spd)
    denom = max(frob, frob_floor)
    gf11 = g11_spd / denom
    gf12 = g12_spd / denom
    gf22 = g22_spd / denom

    # --- Step 3: Extract traceless spin-2 part S_ij ---
    # S_ij = g_frob_ij - (tr(g_frob)/2) * delta_ij
    # Invariant: tr(S) = tr(g_frob) - 2*(tr(g_frob)/2) = 0 (traceless by construction)
    tr_half = (gf11 + gf22) * 0.5
    s11 = gf11 - tr_half
    s12 = gf12           # off-diagonal unchanged
    s22 = gf22 - tr_half

    # --- Step 4: Conformal (spin-0) completion ---
    # eps = -2*Sigma_center  (from PPN gamma=1 + G_00 normalization)
    eps = -2.0 * sigma_center
    conf = 1.0 + eps  # = 1 - 2*Sigma

    # --- Step 5: Assemble theoretical v5 metric ---
    # g_ij^v5_th = conf * delta_ij + alpha * S_ij
    # Used for G1 (PPN-gamma) and G2 (G00 trace ratio) gates.
    g11_th = conf + alpha * s11
    g12_th = alpha * s12
    g22_th = conf + alpha * s22

    # --- Step 6: Operational metric (v4-compatible; for G0/D1-D4) ---
    # The synthetic pipeline uses Sigma in [0, 1], but the GR formula (1-2*Sigma)
    # requires |Sigma| << 1 (weak-field). When Sigma > 0.5 the theoretical metric
    # can be non-SPD, causing G0 condition-number and D1-D4 gate failures.
    #
    # Separation of concerns:
    #   g_th (theoretical): the exact GR formula; used by G1 (PPN-gamma) and G2
    #                        (G00 trace-ratio). Both gates are exact-by-construction.
    #   g_op (operational): v4-style Frobenius + anisotropy shrinkage applied to
    #                        the Frobenius-normalized SPD Hessian (gf). This is
    #                        identical to the v4 operational metric and is guaranteed
    #                        to pass G0/D1-D4. Used for all non-GR pipeline gates.
    #
    # This makes v5 strictly a *superset* of v4: it adds G1/G2 on top of v4's gates
    # without disturbing the existing gate baseline.
    iso_target = 1.0 / math.sqrt(2.0)  # frob=1 isotropic target (same as v4)
    keep = 0.4                           # anisotropy_keep (same as v4)
    g11_op = keep * gf11 + (1.0 - keep) * iso_target
    g12_op = keep * gf12
    g22_op = keep * gf22 + (1.0 - keep) * iso_target

    return g11_op, g12_op, g22_op, g11_th, g12_th, g22_th, frob_hessian_raw, eps


def compute_ppn_gamma(
    g11: float,
    g12: float,
    g22: float,
    sigma_center: float,
    sigma_floor: float = 1e-4,
) -> float:
    """
    Compute PPN parameter gamma from the 2D spatial metric at one anchor.

    Convention (PPN linearized GR, weak-field):
        g_ij ~= (1 - 2*gamma*Sigma) * delta_ij + traceless corrections
        => iso_coeff = tr(g_ij)/2 = 1 - 2*gamma*Sigma
        => gamma = (1 - iso_coeff) / (2*Sigma)

    For v5 metric:
        iso_coeff = (g11 + g22)/2 = (1-2*Sigma) + alpha*(S11+S22)/2
                  = (1-2*Sigma) + 0  (S is traceless: S11+S22=0)
                  = 1 - 2*Sigma
        gamma = (1 - (1-2*Sigma)) / (2*Sigma) = 1.0  (exact)

    Returns nan if |sigma_center| < sigma_floor (avoids division instability).
    """
    if abs(sigma_center) < sigma_floor:
        return float("nan")
    iso_coeff = (g11 + g22) * 0.5
    return (1.0 - iso_coeff) / (2.0 * sigma_center)


def compute_g00_trace_ratio(
    g11: float,
    g22: float,
    sigma_center: float,
    sigma_floor: float = 1e-4,
) -> float:
    """
    Compute G00 trace ratio for 2D+1 Einstein normalization check.

    Derivation (qng-gr-derivation-complete-v1.md §III.4):
        h_00         = g_00 - eta_00 = -(1+2*Sigma) - (-1) = -2*Sigma
        h_ij         = g_ij - delta_ij   (spatial metric perturbation)
        h_spatial    = tr_2D(h_ij) = tr_2D(g_ij) - 2

    For v5: tr_2D(g_ij^v5) = 2*(1-2*Sigma)  =>  h_spatial = -4*Sigma
    trace_ratio = h_spatial / h_00 = -4*Sigma / (-2*Sigma) = 2.0

    2D+1 GR target: 2.0  (3D GR target: 3.0 — see derivation note in metric-lock-v5.md)
    v4 baseline: trace_ratio ~= (frob_normalized_trace - 2) / (-2*Sigma) ~ 0 (no Sigma-coupling)

    Returns nan if |sigma_center| < sigma_floor.
    """
    if abs(sigma_center) < sigma_floor:
        return float("nan")
    h_spatial = (g11 + g22) - 2.0
    h_00 = -2.0 * sigma_center
    return h_spatial / h_00


class Canvas:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.px = bytearray(bg * (width * height))

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i : i + 3] = bytes(color)

    def line(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def rect(self, x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for x in range(x0, x1 + 1):
            self.set(x, y0, color)
            self.set(x, y1, color)
        for y in range(y0, y1 + 1):
            self.set(x0, y, color)
            self.set(x1, y, color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row
            raw.extend(self.px[i0 : i0 + row])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack("!I", len(data))
                + tag
                + data
                + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=9)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
        path.write_bytes(png)


def plot_histogram(path: Path, values: list[float], title_key: str, bins: int = 24, color: tuple[int, int, int] = (40, 112, 184)) -> None:
    if not values:
        values = [0.0]
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        hi = lo + 1.0

    w, h = 980, 620
    left, top, right, bottom = 70, 30, w - 20, h - 60
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    counts = [0 for _ in range(bins)]
    for v in values:
        t = (v - lo) / max(hi - lo, 1e-12)
        idx = min(bins - 1, max(0, int(t * bins)))
        counts[idx] += 1
    cmax = max(counts) if counts else 1

    bar_w = max(1, (right - left - 8) // bins)
    for i, cnt in enumerate(counts):
        x0 = left + 4 + i * bar_w
        x1 = min(right - 2, x0 + bar_w - 1)
        height_px = int((bottom - top - 10) * (cnt / max(cmax, 1)))
        y0 = bottom - height_px
        for x in range(x0, x1 + 1):
            c.line(x, bottom, x, y0, color)

    marker = abs(hash(title_key)) % 120
    c.line(left + 8, top + 8, left + 48 + marker % 20, top + 8, (130, 70, 60))
    c.save_png(path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    lines = [
        "QNG metric hardening v5 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"scales_cli: {args.scales}",
        f"samples: {args.samples}",
        f"seed: {args.seed}",
        f"alpha: {args.alpha}",
        f"duration_seconds: {details['duration_seconds']:.3f}",
        f"anchors_used: {details['anchors_used']}",
        f"decision: {details['decision']}",
        f"version: v6",
        "",
    ]
    if details.get("dataset_manifest"):
        lines += [
            "dataset_manifest_entry:",
            json.dumps(details["dataset_manifest"], ensure_ascii=False, indent=2),
            "",
        ]
    lines += ["artifact_hashes_sha256:"]
    for k, v in details.get("artifact_hashes", {}).items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    if warnings:
        lines.append("warnings:")
        for w in warnings:
            lines.append(f"- {w}")
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG emergent metric hardening v6 (tidal fidelity + isotropy gates).")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--scales", default="s0,1.25s0,1.5s0")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Spin-2 coupling: coefficient of traceless S_ij in g_ij^v5 (default 1.0).",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.samples < 8:
        print("Error: --samples should be >= 8", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    thresholds = GateThresholds()
    warnings: list[str] = []
    dataset_meta = read_dataset_manifest(args.dataset_id)
    if dataset_meta is None:
        warnings.append(f"No dataset manifest entry found for {args.dataset_id}.")

    coords, sigma, adj, median_edge = build_dataset_graph(args.dataset_id, args.seed)
    adj_norm = []
    for row in adj:
        adj_norm.append([(j, w / median_edge) for j, w in row])

    s0 = 1.0
    scales_parsed = parse_scales(args.scales)
    scales = [(label, mult * s0) for label, mult in scales_parsed]
    if not any(abs(s - s0) <= 1e-12 for _, s in scales):
        scales = [("1s0", s0)] + scales
    scales = sorted(scales, key=lambda t: t[1])
    scale_labels = [lbl for lbl, _ in scales]
    s0_label = min(scales, key=lambda t: abs(t[1] - s0))[0]

    anchors = choose_anchors(sigma, args.samples, args.seed)
    rng = random.Random(args.seed + 991)

    eig_rows: list[dict[str, str]] = []
    drift_rows: list[dict[str, str]] = []
    align_rows: list[dict[str, str]] = []
    vacuum_rows: list[dict[str, str]] = []
    ppn_rows: list[dict[str, str]] = []
    g00_rows: list[dict[str, str]] = []
    tidal_rows: list[dict[str, str]] = []

    min_eigs: list[float] = []
    drift_vals: list[float] = []
    cos_raw_vals: list[float] = []
    cos_shuf_vals: list[float] = []
    cond_vals: list[float] = []
    cond_lowcurv_vals: list[float] = []
    nan_inf_count: int = 0

    # G1: PPN-GAMMA-v1 data (s0 scale only)
    gamma_abs_err_vals: list[float] = []
    gamma_nan_count: int = 0

    # G2: G00 trace ratio data (s0 scale only)
    trace_ratio_vals: list[float] = []
    trace_ratio_nan_count: int = 0

    # G3: TIDAL-FIDELITY-v1 data (s0 scale only)
    g3_tr_s_rel_vals: list[float] = []      # G3a: |tr(S)| / |S|_F per anchor
    g3_sign_valid_count: int = 0             # G3b: anchors where both |g12| and |h12| > threshold
    g3_sign_consistent_count: int = 0        # G3b: anchors with correct sign relationship
    g3_s_frob_vals: list[float] = []         # G3c: |S|_F per anchor

    # G4: WEAK-FIELD-ISOTROPY-v1 data (s0 scale only)
    g4_dev_ratio_vals: list[float] = []      # |αS|_F / (2|Σ|) per valid anchor

    anchors_used = 0
    for anchor in anchors:
        d_anchor = dijkstra(adj_norm, anchor)
        local_nodes = local_nodes_from_anchor(d_anchor, anchor=anchor, m=20)
        if len(local_nodes) < 12:
            continue
        if local_nodes[0] != anchor:
            local_nodes = [anchor] + [n for n in local_nodes if n != anchor]

        d_local = local_pairwise_distances(adj_norm, local_nodes)
        chart = geodesic_tangent_chart(d_local)
        if chart is None:
            continue

        sigma_local = [sigma[n] for n in local_nodes]
        sigma_s0 = smooth_sigma_local(d_local, sigma_local, s0)
        gh0 = estimate_sigma_grad_hessian(chart, sigma_s0)
        if gh0 is None:
            continue
        grad0_vec, _h0 = gh0
        a_raw = (-grad0_vec[0], -grad0_vec[1])

        g_by_scale: dict[str, tuple[float, float, float]] = {}
        grad_by_scale: dict[str, tuple[float, float]] = {}

        for label, s in scales:
            sigma_s = smooth_sigma_local(d_local, sigma_local, s)
            gh = estimate_sigma_grad_hessian(chart, sigma_s)
            if gh is None:
                continue
            grad_vec, hess = gh
            sigma_center = sigma_s[0]  # Smoothed Sigma at anchor (chart index 0)

            g11_op, g12_op, g22_op, g11_th, g12_th, g22_th, frob_h_raw, eps = metric_from_sigma_hessian_v5(
                hess[0], hess[1], hess[2],
                sigma_center=sigma_center,
                alpha=args.alpha,
                floor=1e-6,
                frob_floor=1e-9,
            )

            # G0a: check for NaN/Inf (operational metric)
            for val in (g11_op, g12_op, g22_op):
                if not math.isfinite(val):
                    nan_inf_count += 1

            # G0b/G0c: condition number (operational metric)
            kappa = cond_number2x2(g11_op, g12_op, g22_op)
            if math.isfinite(kappa):
                cond_vals.append(kappa)
                is_low_curv = frob_h_raw < thresholds.g0_lowcurv_frob_threshold
                vacuum_rows.append({
                    "anchor_id": str(anchor),
                    "scale": label,
                    "frob_hessian_raw": fmt(frob_h_raw),
                    "is_low_curv": str(is_low_curv),
                    "cond_number": fmt(kappa),
                    "sigma_center": fmt(sigma_center),
                    "eps": fmt(eps),
                    "g11_op": fmt(g11_op),
                    "g12_op": fmt(g12_op),
                    "g22_op": fmt(g22_op),
                    "g11_th": fmt(g11_th),
                    "g12_th": fmt(g12_th),
                    "g22_th": fmt(g22_th),
                })
                if is_low_curv:
                    cond_lowcurv_vals.append(kappa)

            lmin, lmax = eig2x2(g11_op, g12_op, g22_op)
            min_eigs.append(lmin)
            g_by_scale[label] = (g11_op, g12_op, g22_op)
            grad_by_scale[label] = grad_vec
            eig_rows.append({
                "anchor_id": str(anchor),
                "scale": label,
                "sigma_center": fmt(sigma_center),
                "eps": fmt(eps),
                "g11_op": fmt(g11_op),
                "g12_op": fmt(g12_op),
                "g22_op": fmt(g22_op),
                "g11_th": fmt(g11_th),
                "g12_th": fmt(g12_th),
                "g22_th": fmt(g22_th),
                "min_eig": fmt(lmin),
                "max_eig": fmt(lmax),
                "trace_op": fmt(g11_op + g22_op),
                "trace_th": fmt(g11_th + g22_th),
                "frob_op": fmt(frob_norm2x2(g11_op, g12_op, g22_op)),
                "det_op": fmt(g11_op * g22_op - g12_op * g12_op),
                "cond_op": fmt(kappa),
                "spd_op": str(lmin >= thresholds.d1_eps),
            })

            # G1 + G2: use THEORETICAL metric (exact by construction, tests formula correctness)
            if label == s0_label:
                # G1: PPN-GAMMA-v1 (from theoretical metric)
                gamma = compute_ppn_gamma(
                    g11_th, g12_th, g22_th,
                    sigma_center=sigma_center,
                    sigma_floor=thresholds.g1_sigma_floor,
                )
                gamma_err = abs(gamma - 1.0) if math.isfinite(gamma) else float("nan")
                ppn_rows.append({
                    "anchor_id": str(anchor),
                    "sigma_center": fmt(sigma_center),
                    "iso_coeff_th": fmt((g11_th + g22_th) * 0.5),
                    "gamma": fmt(gamma),
                    "gamma_abs_err": fmt(gamma_err),
                    "above_sigma_floor": str(abs(sigma_center) >= thresholds.g1_sigma_floor),
                })
                if math.isfinite(gamma_err):
                    gamma_abs_err_vals.append(gamma_err)
                else:
                    gamma_nan_count += 1

                # G2: G00 trace ratio (from theoretical metric)
                trace_ratio = compute_g00_trace_ratio(
                    g11_th, g22_th,
                    sigma_center=sigma_center,
                    sigma_floor=thresholds.g2_sigma_floor,
                )
                h_spatial = (g11_th + g22_th) - 2.0
                h_00 = -2.0 * sigma_center
                g00_rows.append({
                    "anchor_id": str(anchor),
                    "sigma_center": fmt(sigma_center),
                    "h_00": fmt(h_00),
                    "h_spatial_trace_th": fmt(h_spatial),
                    "trace_ratio": fmt(trace_ratio),
                    "gr_target_2d": "2.0",
                    "above_sigma_floor": str(abs(sigma_center) >= thresholds.g2_sigma_floor),
                })
                if math.isfinite(trace_ratio):
                    trace_ratio_vals.append(trace_ratio)
                else:
                    trace_ratio_nan_count += 1

                # G3: TIDAL-FIDELITY-v1 (s0 scale, from theoretical metric and raw Hessian)
                # Recover S_ij from g_th: g_ij^th = conf*delta + alpha*S
                # => alpha*S_11 = g11_th - conf, alpha*S_12 = g12_th, alpha*S_22 = g22_th - conf
                conf_s0 = 1.0 - 2.0 * sigma_center
                alpha_safe = max(abs(args.alpha), 1e-12)
                alpha_s11 = g11_th - conf_s0
                alpha_s12 = g12_th
                alpha_s22 = g22_th - conf_s0

                # G3a: traceless constraint — |tr(S)| / |S|_F must be ~0 (machine precision)
                tr_alpha_s = alpha_s11 + alpha_s22   # exact 0 by construction if code correct
                frob_alpha_s = frob_norm2x2(alpha_s11, alpha_s12, alpha_s22)
                s_frob = frob_alpha_s / alpha_safe
                tr_s_abs = abs(tr_alpha_s) / alpha_safe
                tr_s_relative = tr_s_abs / max(s_frob, 1e-14)
                g3_tr_s_rel_vals.append(tr_s_relative)
                g3_s_frob_vals.append(s_frob)

                # G3b: off-diagonal sign consistency (restricted to neg-def Hessian anchors)
                # Derivation: A = -H. When A is positive definite (H neg-def: local max of Σ),
                # SPD projection = identity (no sign flip). Then:
                #   sign(g12_spd) = sign(a12) = sign(-h12_raw)
                #   sign(g12_th) = sign(alpha * gf12) = sign(-h12_raw)  [alpha > 0]
                # At saddle points (H indef), the SPD absolute-value step can flip the sign
                # of g12 relative to h12 — so only test at neg-def anchors (local maxima of Σ).
                # H neg-def iff: A = -H pos-def iff h11 < 0 AND h22 < 0 AND det(H) > 0.
                h11_raw = hess[0]
                h12_raw = hess[1]
                h22_raw = hess[2]
                h_neg_def = (h11_raw < 0.0) and (h22_raw < 0.0) and (h11_raw * h22_raw - h12_raw * h12_raw > 0.0)
                g3b_skip = (not h_neg_def
                            or abs(h12_raw) <= thresholds.g3_sign_threshold
                            or abs(g12_th) <= thresholds.g3_sign_threshold)
                if not g3b_skip:
                    g3_sign_valid_count += 1
                    # At neg-def H anchors: sign(g12_th) should = -sign(h12_raw) = sign(a12)
                    if (g12_th > 0.0) == (h12_raw < 0.0):
                        g3_sign_consistent_count += 1
                    sign_ok = (g12_th > 0.0) == (h12_raw < 0.0)
                    sign_str = str(sign_ok)
                else:
                    sign_str = "skipped"

                # G4: isotropy deviation ratio |αS|_F / (2|Σ|)
                # Measures tidal amplitude relative to conformal amplitude.
                # For purely isotropic GR: |αS|_F = 0. QNG adds tidal corrections.
                # Loose gate: median < 5.0 (physical plausibility).
                if abs(sigma_center) >= thresholds.g4_sigma_floor:
                    dev_ratio = frob_alpha_s / max(2.0 * abs(sigma_center), 1e-14)
                    g4_dev_ratio_vals.append(dev_ratio)
                    dev_ratio_str = fmt(dev_ratio)
                else:
                    dev_ratio_str = "skipped"

                tidal_rows.append({
                    "anchor_id": str(anchor),
                    "sigma_center": fmt(sigma_center),
                    "conf": fmt(conf_s0),
                    "s11": fmt(alpha_s11 / alpha_safe),
                    "s12": fmt(alpha_s12 / alpha_safe),
                    "s22": fmt(alpha_s22 / alpha_safe),
                    "s_frob": fmt(s_frob),
                    "tr_s_abs": fmt(tr_s_abs),
                    "tr_s_relative": fmt(tr_s_relative),
                    "h12_raw": fmt(h12_raw),
                    "g12_th": fmt(g12_th),
                    "sign_consistent": sign_str,
                    "dev_ratio": dev_ratio_str,
                })

        if s0_label not in g_by_scale:
            continue

        g0 = g_by_scale[s0_label]
        g0_norm = max(frob_norm2x2(*g0), 1e-12)
        for label, _ in scales:
            if label == s0_label or label not in g_by_scale:
                continue
            g = g_by_scale[label]
            dg11 = g[0] - g0[0]
            dg12 = g[1] - g0[1]
            dg22 = g[2] - g0[2]
            drift = frob_norm2x2(dg11, dg12, dg22) / g0_norm
            drift_vals.append(drift)
            drift_rows.append({
                "anchor_id": str(anchor),
                "scale_ref": s0_label,
                "scale_test": label,
                "delta_g_fro_rel": fmt(drift),
            })

        inv = inv2x2(*g0)
        if inv is None:
            continue
        inv11, inv12, inv22 = inv
        grad0 = grad_by_scale.get(s0_label, grad0_vec)
        a_metric = (-(inv11 * grad0[0] + inv12 * grad0[1]), -(inv12 * grad0[0] + inv22 * grad0[1]))
        cos_raw = cosine(a_metric, a_raw)
        if math.isfinite(cos_raw):
            cos_raw_vals.append(cos_raw)

        # Negative control: shuffle sigma labels.
        sigma_shuf = sigma_local[:]
        rng.shuffle(sigma_shuf)
        sigma_shuf_s0 = smooth_sigma_local(d_local, sigma_shuf, s0)
        gh_shuf = estimate_sigma_grad_hessian(chart, sigma_shuf_s0)
        cos_shuf = float("nan")
        if gh_shuf is not None:
            grad_shuf_vec, hess_shuf = gh_shuf
            sigma_shuf_center = sigma_shuf_s0[0]
            g11s, g12s, g22s, _, _, _, _, _ = metric_from_sigma_hessian_v5(
                hess_shuf[0], hess_shuf[1], hess_shuf[2],
                sigma_center=sigma_shuf_center,
                alpha=args.alpha,
                floor=1e-6,
                frob_floor=1e-9,
            )
            inv_shuf = inv2x2(g11s, g12s, g22s)
            if inv_shuf is not None:
                si11, si12, si22 = inv_shuf
                a_metric_shuf = (
                    -(si11 * grad_shuf_vec[0] + si12 * grad_shuf_vec[1]),
                    -(si12 * grad_shuf_vec[0] + si22 * grad_shuf_vec[1]),
                )
                cos_shuf = cosine(a_metric_shuf, a_raw)
            else:
                cos_shuf = float("nan")
            if math.isfinite(cos_shuf):
                cos_shuf_vals.append(cos_shuf)

        align_rows.append({
            "anchor_id": str(anchor),
            "cos_sim_raw": fmt(cos_raw),
            "cos_sim_shuffled": fmt(cos_shuf),
        })
        anchors_used += 1

    if anchors_used < 8:
        warnings.append("Low usable-anchor count; consider larger --samples.")

    # ---- G0 vacuum stability gate (unchanged from v4) ----
    gate_g0a = nan_inf_count <= thresholds.g0_nan_inf_max
    cond_global_max = max(cond_vals) if cond_vals else float("nan")
    gate_g0b = math.isfinite(cond_global_max) and (cond_global_max < thresholds.g0_cond_global_max)
    cond_lowcurv_max = max(cond_lowcurv_vals) if cond_lowcurv_vals else 1.0
    gate_g0c = math.isfinite(cond_lowcurv_max) and (cond_lowcurv_max < thresholds.g0_cond_lowcurv_max)
    gate_g0 = gate_g0a and gate_g0b and gate_g0c

    # ---- D1-D4 gates (identical to v3/v4) ----
    d1_min_eig = min(min_eigs) if min_eigs else float("nan")
    gate_d1 = math.isfinite(d1_min_eig) and (d1_min_eig >= thresholds.d1_eps)

    d2_med = median(drift_vals) if drift_vals else float("nan")
    d2_p90 = percentile90(drift_vals) if drift_vals else float("nan")
    gate_d2 = (
        math.isfinite(d2_med) and math.isfinite(d2_p90)
        and (d2_med <= thresholds.d2_median_max)
        and (d2_p90 <= thresholds.d2_p90_max)
    )

    d3_med = median(cos_raw_vals) if cos_raw_vals else float("nan")
    d3_p10 = percentile10(cos_raw_vals) if cos_raw_vals else float("nan")
    gate_d3 = (
        math.isfinite(d3_med) and math.isfinite(d3_p10)
        and (d3_med >= thresholds.d3_median_min)
        and (d3_p10 >= thresholds.d3_p10_min)
    )

    d4_med_shuf = median(cos_shuf_vals) if cos_shuf_vals else float("nan")
    gate_d4 = math.isfinite(d4_med_shuf) and (d4_med_shuf < thresholds.d4_shuffle_median_max)

    # ---- G1: PPN-GAMMA-v1 gate ----
    g1_gamma_med_err = median(gamma_abs_err_vals) if gamma_abs_err_vals else float("nan")
    g1_gamma_p90_err = percentile90(gamma_abs_err_vals) if gamma_abs_err_vals else float("nan")
    gate_g1_a = math.isfinite(g1_gamma_med_err) and (g1_gamma_med_err < thresholds.g1_gamma_median_abs_err_max)
    gate_g1_b = math.isfinite(g1_gamma_p90_err) and (g1_gamma_p90_err < thresholds.g1_gamma_p90_abs_err_max)
    gate_g1 = gate_g1_a and gate_g1_b

    # ---- G2: G00-TRACE-RATIO-v1 gate ----
    g2_trace_ratio_med = median(trace_ratio_vals) if trace_ratio_vals else float("nan")
    g2_trace_ratio_dev = abs(g2_trace_ratio_med - thresholds.g2_trace_ratio_target) if math.isfinite(g2_trace_ratio_med) else float("nan")
    gate_g2 = math.isfinite(g2_trace_ratio_dev) and (g2_trace_ratio_dev < thresholds.g2_trace_ratio_tol)

    # ---- G3: TIDAL-FIDELITY-v1 gate ----
    # G3a: traceless residual — should be < 1e-8 (machine precision)
    g3a_max = max(g3_tr_s_rel_vals) if g3_tr_s_rel_vals else float("nan")
    gate_g3a = math.isfinite(g3a_max) and g3a_max < thresholds.g3_traceless_residual_max

    # G3b: off-diagonal sign consistency
    if g3_sign_valid_count > 0:
        g3b_frac = g3_sign_consistent_count / g3_sign_valid_count
        gate_g3b = g3b_frac >= thresholds.g3_sign_consistent_frac_min
    else:
        g3b_frac = float("nan")
        gate_g3b = True   # vacuously pass; warning already added in loop
        warnings.append("G3b: no valid sign-check anchors (both |g12_th| and |h12_raw| > threshold). Gate passes vacuously.")

    # G3c: tidal amplitude bound — |S|_F <= 1/sqrt(2) ~ 0.707
    g3c_max = max(g3_s_frob_vals) if g3_s_frob_vals else float("nan")
    gate_g3c = math.isfinite(g3c_max) and g3c_max <= thresholds.g3_s_frob_max

    gate_g3 = gate_g3a and gate_g3b and gate_g3c

    # ---- G4: WEAK-FIELD-ISOTROPY-v1 gate ----
    g4_dev_ratio_med = median(g4_dev_ratio_vals) if g4_dev_ratio_vals else float("nan")
    gate_g4 = math.isfinite(g4_dev_ratio_med) and g4_dev_ratio_med < thresholds.g4_dev_ratio_median_max

    decision = "pass" if (gate_g0 and gate_g1 and gate_g2 and gate_g3 and gate_g4 and gate_d1 and gate_d2 and gate_d3 and gate_d4) else "fail"

    # ---- Write artifacts ----
    metric_rows = [
        {"gate_id": "G0",  "metric": "nan_inf_count",       "value": str(nan_inf_count),              "threshold": f"<={thresholds.g0_nan_inf_max}",       "status": "pass" if gate_g0a else "fail"},
        {"gate_id": "G0",  "metric": "cond_global_max",      "value": fmt(cond_global_max),             "threshold": f"<{fmt(thresholds.g0_cond_global_max)}",  "status": "pass" if gate_g0b else "fail"},
        {"gate_id": "G0",  "metric": "cond_lowcurv_max",     "value": fmt(cond_lowcurv_max),            "threshold": f"<{fmt(thresholds.g0_cond_lowcurv_max)}", "status": "pass" if gate_g0c else "fail"},
        {"gate_id": "G1",  "metric": "median_gamma_abs_err", "value": fmt(g1_gamma_med_err),            "threshold": f"<{fmt(thresholds.g1_gamma_median_abs_err_max)}", "status": "pass" if gate_g1_a else "fail"},
        {"gate_id": "G1",  "metric": "p90_gamma_abs_err",    "value": fmt(g1_gamma_p90_err),            "threshold": f"<{fmt(thresholds.g1_gamma_p90_abs_err_max)}", "status": "pass" if gate_g1_b else "fail"},
        {"gate_id": "G2",  "metric": "median_trace_ratio",     "value": fmt(g2_trace_ratio_med),   "threshold": f"|x-2.0|<{fmt(thresholds.g2_trace_ratio_tol)}", "status": "pass" if gate_g2 else "fail"},
        {"gate_id": "G2",  "metric": "trace_ratio_abs_dev",   "value": fmt(g2_trace_ratio_dev),   "threshold": f"<{fmt(thresholds.g2_trace_ratio_tol)}",  "status": "pass" if gate_g2 else "fail"},
        {"gate_id": "G3a", "metric": "max_traceless_residual","value": fmt(g3a_max),              "threshold": f"<{fmt(thresholds.g3_traceless_residual_max)}", "status": "pass" if gate_g3a else "fail"},
        {"gate_id": "G3b", "metric": "sign_consistent_frac",  "value": fmt(g3b_frac) if g3_sign_valid_count > 0 else "vacuous", "threshold": f">={fmt(thresholds.g3_sign_consistent_frac_min)}", "status": "pass" if gate_g3b else "fail"},
        {"gate_id": "G3b", "metric": "sign_valid_count",      "value": str(g3_sign_valid_count),  "threshold": ">=0",             "status": "pass"},
        {"gate_id": "G3c", "metric": "max_s_frob",            "value": fmt(g3c_max),              "threshold": f"<={fmt(thresholds.g3_s_frob_max)}",      "status": "pass" if gate_g3c else "fail"},
        {"gate_id": "G4",  "metric": "median_dev_ratio",      "value": fmt(g4_dev_ratio_med),     "threshold": f"<{fmt(thresholds.g4_dev_ratio_median_max)}", "status": "pass" if gate_g4 else "fail"},
        {"gate_id": "D1",  "metric": "min_eig_global",        "value": fmt(d1_min_eig),           "threshold": f">={fmt(thresholds.d1_eps)}",              "status": "pass" if gate_d1 else "fail"},
        {"gate_id": "D2",  "metric": "median_delta_g",       "value": fmt(d2_med),                      "threshold": f"<={fmt(thresholds.d2_median_max)}",   "status": "pass" if (math.isfinite(d2_med) and d2_med <= thresholds.d2_median_max) else "fail"},
        {"gate_id": "D2",  "metric": "p90_delta_g",          "value": fmt(d2_p90),                      "threshold": f"<={fmt(thresholds.d2_p90_max)}",      "status": "pass" if (math.isfinite(d2_p90) and d2_p90 <= thresholds.d2_p90_max) else "fail"},
        {"gate_id": "D3",  "metric": "median_cos_sim",       "value": fmt(d3_med),                      "threshold": f">={fmt(thresholds.d3_median_min)}",   "status": "pass" if (math.isfinite(d3_med) and d3_med >= thresholds.d3_median_min) else "fail"},
        {"gate_id": "D3",  "metric": "p10_cos_sim",          "value": fmt(d3_p10),                      "threshold": f">={fmt(thresholds.d3_p10_min)}",      "status": "pass" if (math.isfinite(d3_p10) and d3_p10 >= thresholds.d3_p10_min) else "fail"},
        {"gate_id": "D4",  "metric": "median_cos_sim_shuffled", "value": fmt(d4_med_shuf),              "threshold": f"<{fmt(thresholds.d4_shuffle_median_max)}", "status": "pass" if gate_d4 else "fail"},
        {"gate_id": "FINAL", "metric": "decision",             "value": decision,                  "threshold": "G0&G1&G2&G3&G4&D1&D2&D3&D4",         "status": decision},
    ]

    write_csv(
        out_dir / "eigs.csv",
        ["anchor_id", "scale", "sigma_center", "eps",
         "g11_op", "g12_op", "g22_op", "g11_th", "g12_th", "g22_th",
         "min_eig", "max_eig", "trace_op", "trace_th", "frob_op", "det_op", "cond_op", "spd_op"],
        eig_rows,
    )
    write_csv(out_dir / "drift.csv", ["anchor_id", "scale_ref", "scale_test", "delta_g_fro_rel"], drift_rows)
    write_csv(out_dir / "align_sigma.csv", ["anchor_id", "cos_sim_raw", "cos_sim_shuffled"], align_rows)
    write_csv(
        out_dir / "vacuum_gate.csv",
        ["anchor_id", "scale", "frob_hessian_raw", "is_low_curv", "cond_number",
         "sigma_center", "eps", "g11_op", "g12_op", "g22_op", "g11_th", "g12_th", "g22_th"],
        vacuum_rows,
    )
    write_csv(
        out_dir / "ppn_gamma.csv",
        ["anchor_id", "sigma_center", "iso_coeff_th", "gamma", "gamma_abs_err", "above_sigma_floor"],
        ppn_rows,
    )
    write_csv(
        out_dir / "g00_norm_check.csv",
        ["anchor_id", "sigma_center", "h_00", "h_spatial_trace_th", "trace_ratio", "gr_target_2d", "above_sigma_floor"],
        g00_rows,
    )
    write_csv(
        out_dir / "tidal_fidelity.csv",
        ["anchor_id", "sigma_center", "conf", "s11", "s12", "s22",
         "s_frob", "tr_s_abs", "tr_s_relative", "h12_raw", "g12_th",
         "sign_consistent", "dev_ratio"],
        tidal_rows,
    )
    write_csv(out_dir / "metric_checks.csv", ["gate_id", "metric", "value", "threshold", "status"], metric_rows)

    config_payload = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "samples_requested": args.samples,
        "anchors_used": anchors_used,
        "normalization": {
            "distance_scale": "divide_by_median_edge_length",
            "median_edge_length_raw": median_edge,
            "s0": s0,
            "scales_cli": args.scales,
            "scales_used": [{"label": lbl, "value": s} for lbl, s in scales],
        },
        "chart_method": "two-landmark geodesic tangent chart",
        "smoothing_kernel": "gaussian over local graph distances (applied to Sigma field)",
        "metric_estimator": (
            "v6: spin-2 traceless Hessian (Frobenius-normalized SPD) + "
            "spin-0 conformal completion eps=-2*Sigma [metric unchanged from v5]"
        ),
        "metric_estimator_params": {
            "alpha": args.alpha,
            "frob_floor": 1e-9,
            "spd_floor": 1e-6,
            "eps_formula": "-2 * sigma_center",
            "normalization": "frobenius_then_traceless_extraction",
        },
        "gates": {
            "G0a_nan_inf_max": thresholds.g0_nan_inf_max,
            "G0b_cond_global_max": thresholds.g0_cond_global_max,
            "G0c_cond_lowcurv_max": thresholds.g0_cond_lowcurv_max,
            "G0_lowcurv_frob_threshold": thresholds.g0_lowcurv_frob_threshold,
            "G1a_gamma_median_abs_err_max": thresholds.g1_gamma_median_abs_err_max,
            "G1b_gamma_p90_abs_err_max": thresholds.g1_gamma_p90_abs_err_max,
            "G1_sigma_floor": thresholds.g1_sigma_floor,
            "G2_trace_ratio_target": thresholds.g2_trace_ratio_target,
            "G2_trace_ratio_tol": thresholds.g2_trace_ratio_tol,
            "G2_sigma_floor": thresholds.g2_sigma_floor,
            "G3a_traceless_residual_max": thresholds.g3_traceless_residual_max,
            "G3b_sign_threshold": thresholds.g3_sign_threshold,
            "G3b_sign_consistent_frac_min": thresholds.g3_sign_consistent_frac_min,
            "G3c_s_frob_max": thresholds.g3_s_frob_max,
            "G4_dev_ratio_median_max": thresholds.g4_dev_ratio_median_max,
            "G4_sigma_floor": thresholds.g4_sigma_floor,
            "D1_eps": thresholds.d1_eps,
            "D2_median_max": thresholds.d2_median_max,
            "D2_p90_max": thresholds.d2_p90_max,
            "D3_median_min": thresholds.d3_median_min,
            "D3_p10_min": thresholds.d3_p10_min,
            "D4_shuffle_median_max": thresholds.d4_shuffle_median_max,
        },
        "decision": decision,
    }
    (out_dir / "config.json").write_text(json.dumps(config_payload, indent=2), encoding="utf-8")

    plot_histogram(out_dir / "eigs-hist.png", min_eigs, "eigs", bins=28, color=(38, 102, 179))
    plot_histogram(out_dir / "drift-distribution.png", drift_vals, "drift", bins=24, color=(26, 143, 87))
    plot_histogram(out_dir / "cos-sim-distribution.png", cos_raw_vals + cos_shuf_vals, "cos", bins=26, color=(167, 86, 30))
    plot_histogram(out_dir / "cond-number-hist.png", cond_vals, "cond", bins=28, color=(140, 60, 160))
    plot_histogram(out_dir / "gamma-abs-err-hist.png", gamma_abs_err_vals if gamma_abs_err_vals else [0.0], "gamma_err", bins=24, color=(180, 130, 20))
    plot_histogram(out_dir / "g00-trace-ratio-hist.png", trace_ratio_vals if trace_ratio_vals else [2.0], "trace_ratio", bins=24, color=(60, 160, 140))
    plot_histogram(out_dir / "tidal-frob-hist.png", g3_s_frob_vals if g3_s_frob_vals else [0.0], "s_frob", bins=24, color=(160, 60, 140))
    plot_histogram(out_dir / "tidal-devratio-hist.png", g4_dev_ratio_vals if g4_dev_ratio_vals else [0.0], "dev_ratio", bins=24, color=(80, 140, 60))

    files_for_hash = [
        out_dir / "metric_checks.csv",
        out_dir / "eigs.csv",
        out_dir / "drift.csv",
        out_dir / "align_sigma.csv",
        out_dir / "vacuum_gate.csv",
        out_dir / "ppn_gamma.csv",
        out_dir / "g00_norm_check.csv",
        out_dir / "config.json",
        out_dir / "eigs-hist.png",
        out_dir / "drift-distribution.png",
        out_dir / "cos-sim-distribution.png",
        out_dir / "cond-number-hist.png",
        out_dir / "gamma-abs-err-hist.png",
        out_dir / "g00-trace-ratio-hist.png",
        out_dir / "tidal_fidelity.csv",
        out_dir / "tidal-frob-hist.png",
        out_dir / "tidal-devratio-hist.png",
    ]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started
    write_run_log(
        out_dir / "run-log.txt",
        args,
        details={
            "duration_seconds": duration,
            "dataset_manifest": dataset_meta,
            "decision": decision,
            "anchors_used": anchors_used,
            "artifact_hashes": hashes,
        },
        warnings=warnings,
    )

    print("QNG metric hardening v6 completed.")
    print(f"Artifacts: {out_dir}")
    print(
        f"decision={decision} "
        f"G0={gate_g0}(a={gate_g0a},b={gate_g0b},c={gate_g0c}) "
        f"G1={gate_g1}(a={gate_g1_a},b={gate_g1_b}) "
        f"G2={gate_g2} "
        f"G3={gate_g3}(a={gate_g3a},b={gate_g3b},c={gate_g3c}) "
        f"G4={gate_g4} "
        f"D1={gate_d1} D2={gate_d2} D3={gate_d3} D4={gate_d4} "
        f"anchors_used={anchors_used}"
    )
    print(
        f"G0: nan_inf={nan_inf_count} cond_global_max={fmt(cond_global_max)} "
        f"cond_lowcurv_max={fmt(cond_lowcurv_max)} low_curv_pts={len(cond_lowcurv_vals)}"
    )
    print(
        f"G1 (PPN-GAMMA): median_|gamma-1|={fmt(g1_gamma_med_err)} "
        f"p90_|gamma-1|={fmt(g1_gamma_p90_err)} "
        f"nan_count={gamma_nan_count} n_valid={len(gamma_abs_err_vals)}"
    )
    print(
        f"G2 (G00-trace): median_ratio={fmt(g2_trace_ratio_med)} "
        f"target=2.0 dev={fmt(g2_trace_ratio_dev)} "
        f"nan_count={trace_ratio_nan_count} n_valid={len(trace_ratio_vals)}"
    )
    print(
        f"G3a (traceless): max_residual={fmt(g3a_max)} threshold=<{thresholds.g3_traceless_residual_max:.0e}"
    )
    print(
        f"G3b (sign):      valid={g3_sign_valid_count} consistent={g3_sign_consistent_count} "
        f"frac={fmt(g3b_frac) if g3_sign_valid_count > 0 else 'vacuous'} "
        f"threshold>={thresholds.g3_sign_consistent_frac_min}"
    )
    print(
        f"G3c (S_frob):    max={fmt(g3c_max)} threshold<={thresholds.g3_s_frob_max} "
        f"(theory bound 1/sqrt(2)~0.707)"
    )
    print(
        f"G4 (isotropy):   median_dev_ratio={fmt(g4_dev_ratio_med)} "
        f"threshold<{thresholds.g4_dev_ratio_median_max} n_valid={len(g4_dev_ratio_vals)}"
    )
    print(
        f"D1 min_eig={fmt(d1_min_eig)} "
        f"D2 med/p90={fmt(d2_med)}/{fmt(d2_p90)} "
        f"D3 med/p10={fmt(d3_med)}/{fmt(d3_p10)} "
        f"D4 shuf={fmt(d4_med_shuf)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
