#!/usr/bin/env python3
"""
QNG Quantum Information & Emergent Geometry (v1) — G18.

Builds on the canonical quantisation from G17 to probe the quantum information
structure of the vacuum state: how quantum information is shared across space,
whether eigenmodes are delocalized (valid QFT), whether the vacuum is spatially
homogeneous, and what spatial dimension the graph manifests.

Physical observables
────────────────────
1. Binary entanglement entropy S_A (mode-sharing proxy):

       q_k(A) = Σ_{i∈A} ψ_k(i)²        [weight of mode k in region A]
       S_A = Σ_{k=1}^{K_eff} h(q_k)     h(p) = −p ln p − (1−p) ln(1−p)

   S_A measures how much quantum information from each mode is shared between
   A and its complement B = V∖A.  For delocalized modes q_k ≈ ½ → h ≈ ln 2,
   giving S_A ≈ K_eff · ln 2 ≈ 13.2 for K_eff=19.

2. Inverse participation ratio (IPR):

       IPR_k = Σ_{i=1}^{n} ψ_k(i)⁴

   IPR_k ≈ 1/n for a fully delocalized (extended) mode.
   IPR_k ≈ 1   for a fully localized mode (Anderson-localized).
   Gate: n · mean(IPR) < 5  ↔  modes extended over ≥ n/5 vertices.

3. Vacuum fluctuation homogeneity:

       G(i,i) = Σ_{k} ψ_k(i)² / (2 ω_k)   [local vacuum fluctuation squared]
       cv = std(G_ii) / mean(G_ii)

   Small cv ↔ vacuum fluctuations are spatially uniform (no preferred centre).

4. Spectral dimension d_s from random-walk return probability:

       P(t) = P(walker returns to start after t steps)
             ∝ t^{−d_s/2}  for large t  (diffusion scaling)
       d_s = −2 · d log P(t) / d log t   [from OLS fit]

   For a 2-dimensional manifold: d_s = 2.  Gate: d_s ∈ (1.0, 3.5).

Gates (G18):
    G18a — S_A  > 0.5 · K_eff · ln 2  (substantial quantum mode sharing)
    G18b — n · mean(IPR) < 5.0          (extended, non-localized modes)
    G18c — cv(G_ii) < 0.50              (homogeneous vacuum)
    G18d — d_s ∈ (1.0, 3.5)            (emergent ~2D geometry; lower bound = minimum for connected graph)

Outputs (in --out-dir):
    qm_info_modes.csv          per-mode: k, mu_k, omega_k, IPR_k, n_IPR, q_k, h_q
    qm_info_walk.csv           per-step: t, P_t, log_t, log_P_t
    qm_info_local.csv          per-vertex: G_ii, delta_sigma_vac
    metric_checks_qm_info.csv  G18 gate summary
    qm_info-plot.png           log-P(t) decay (left) + q_k histogram (right)
    config_qm_info.json
    run-log-qm-info.txt
    artifact-hashes-qm-info.json

Dependency policy: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import random
import statistics
import struct
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qm-info-v1"
)

# ── Hyper-parameters ──────────────────────────────────────────────────────────
M_EFF_SQ    = 0.014    # from G16 Rayleigh quotient
N_MODES     = 20       # total modes (including zero mode)
N_ITER_POW  = 350      # power-iteration steps per mode
N_WALKS     = 80       # random-walk realisations per vertex
N_STEPS     = 12       # random-walk maximum step count
T_LO        = 4        # earliest t used for d_s OLS fit
T_HI        = 10       # latest  t used for d_s OLS fit


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class InfoThresholds:
    g18a_entropy_min: float  = 0.0    # S_A > 0.5·K·ln2; set dynamically
    g18b_ipr_max:     float  = 5.0    # n·mean(IPR) < 5
    g18c_cv_max:      float  = 0.50   # cv(G_ii) < 0.50
    g18d_ds_lo:       float  = 1.0    # d_s > 1.0 (any connected graph has d_s ≥ 1)
    g18d_ds_hi:       float  = 3.5    # d_s < 3.5


# ── Utilities ─────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v):   return "nan"
    if math.isinf(v):   return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def ols_fit(x_vals: list[float], y_vals: list[float]) -> tuple[float, float, float]:
    n = len(x_vals)
    if n < 2:
        return 0.0, 0.0, 0.0
    mx = sum(x_vals) / n; my = sum(y_vals) / n
    Sxx = sum((x - mx)**2 for x in x_vals)
    Sxy = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(n))
    if abs(Sxx) < 1e-30:
        return my, 0.0, 0.0
    b = Sxy / Sxx; a = my - b * mx
    ss_tot = sum((y - my)**2 for y in y_vals)
    if ss_tot < 1e-30:
        return a, b, 1.0
    ss_res = sum((y_vals[i] - (a + b * x_vals[i]))**2 for i in range(n))
    return a, b, max(0.0, 1.0 - ss_res / ss_tot)


# ── Graph builder ─────────────────────────────────────────────────────────────
def build_dataset_graph(
    dataset_id: str, seed: int
) -> tuple[list[tuple[float, float]], list[float], list[list[int]]]:
    rng = random.Random(seed)
    ds = dataset_id.upper().strip()
    if ds == "DS-002":
        n, k, spread = 280, 8, 2.3
    elif ds == "DS-003":
        n, k, spread = 240, 7, 2.0
    elif ds == "DS-006":
        n, k, spread = 320, 9, 2.7
    else:
        n, k, spread = 260, 8, 2.2

    coords: list[tuple[float, float]] = [
        (rng.uniform(-spread, spread), rng.uniform(-spread, spread))
        for _ in range(n)
    ]
    sigma: list[float] = []
    for x, y in coords:
        r1 = ((x + 0.8)**2 + (y - 0.4)**2) / (2.0 * 1.35**2)
        r2 = ((x - 1.1)**2 + (y + 0.9)**2) / (2.0 * 1.10**2)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(min(max(s, 0.0), 1.0))

    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        dists = sorted(
            [(math.hypot(xi - coords[j][0], yi - coords[j][1]), j)
             for j in range(n) if j != i]
        )
        for d, j in dists[:k]:
            w = max(d, 1e-6) * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w; adj[j][i] = w

    return coords, sigma, [[j for j in m] for m in adj]


# ── Spectral decomposition (deflated power iteration on D⁻¹A) ─────────────────
def _dot(u: list[float], v: list[float]) -> float:
    return sum(u[i] * v[i] for i in range(len(u)))

def _normalize(v: list[float]) -> list[float]:
    nrm = math.sqrt(_dot(v, v))
    return [x / nrm for x in v] if nrm > 1e-14 else v[:]

def _deflate(v: list[float], basis: list[list[float]]) -> list[float]:
    w = v[:]
    for b in basis:
        c = _dot(w, b)
        w = [w[i] - c * b[i] for i in range(len(w))]
    return w

def _apply_rw(f: list[float], neighbours: list[list[int]]) -> list[float]:
    return [
        (sum(f[j] for j in nb) / len(nb)) if nb else 0.0
        for nb in neighbours
    ]

def compute_eigenmodes(
    neighbours: list[list[int]], n_modes: int, n_iter: int, rng: random.Random
) -> tuple[list[float], list[list[float]]]:
    """Top n_modes eigenvectors of D⁻¹A via deflated power iteration.
    Returns (mu_list, vec_list), sorted ascending by μ_k = 1 − α_k."""
    n = len(neighbours)
    vecs: list[list[float]] = []
    mus:  list[float]        = []

    for _ in range(n_modes):
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, vecs)
        nrm = math.sqrt(_dot(v, v))
        if nrm < 1e-14:
            continue
        v = _normalize(v)

        for _ in range(n_iter):
            w = _apply_rw(v, neighbours)
            w = _deflate(w, vecs)
            nrm = math.sqrt(_dot(w, w))
            if nrm < 1e-14:
                break
            v = [x / nrm for x in w]

        Av = _apply_rw(v, neighbours)
        alpha = _dot(v, Av)
        mu = max(0.0, 1.0 - alpha)

        vecs.append(v)
        mus.append(mu)

    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── G18a: binary entanglement entropy ────────────────────────────────────────
def _h_bin(p: float) -> float:
    """Binary entropy h(p) = −p ln p − (1−p) ln(1−p).  h(0)=h(1)=0."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log(p) - (1.0 - p) * math.log(1.0 - p)


def binary_entropy_partition(
    vecs_active: list[list[float]], n: int, rng: random.Random
) -> tuple[float, list[float], list[float]]:
    """
    Random balanced partition A (|A| = n//2).
    Returns (S_A, q_k list, h_q_k list).
    """
    A_mask = [False] * n
    A_size = n // 2
    indices = list(range(n))
    rng.shuffle(indices)
    for i in indices[:A_size]:
        A_mask[i] = True

    K = len(vecs_active)
    q_list  = [sum(vecs_active[k][i]**2 for i in range(n) if A_mask[i]) for k in range(K)]
    hq_list = [_h_bin(q) for q in q_list]
    S_A = sum(hq_list)
    return S_A, q_list, hq_list


# ── G18b: inverse participation ratio ────────────────────────────────────────
def compute_ipr(vecs_active: list[list[float]], n: int) -> list[float]:
    """IPR_k = Σ_i ψ_k(i)⁴  for each active mode k."""
    return [sum(v[i]**4 for i in range(n)) for v in vecs_active]


# ── G18c: local propagator G(i,i) ─────────────────────────────────────────────
def compute_local_propagator(
    vecs_active: list[list[float]], omegas: list[float], n: int
) -> list[float]:
    """G(i,i) = Σ_k ψ_k(i)² / (2 ω_k)."""
    K = len(omegas)
    G_diag = [0.0] * n
    for k in range(K):
        inv2w = 1.0 / (2.0 * omegas[k])
        for i in range(n):
            G_diag[i] += vecs_active[k][i]**2 * inv2w
    return G_diag


# ── G18d: random-walk return probability & spectral dimension ──────────────────
def random_walk_simulation(
    neighbours: list[list[int]], n_walks: int, n_steps: int, rng: random.Random
) -> list[float]:
    """
    P(t) = fraction of (walk, step t) pairs where the walker returns to start.
    Returns P_t[1..n_steps] (index 0 unused).
    """
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total  = n * n_walks

    for start in range(n):
        nb_start = neighbours[start]
        if not nb_start:
            continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                nb = neighbours[v]
                v = rng.choice(nb) if nb else v
                if v == start:
                    counts[t] += 1

    P_t = [counts[t] / total for t in range(n_steps + 1)]
    return P_t   # index 0 unused (P[0] = 0 by definition)


def spectral_dimension(
    P_t: list[float], t_lo: int, t_hi: int
) -> tuple[float, float, float]:
    """
    OLS of log P(t) vs log t for t in [t_lo, t_hi].
    d_s = −2 × slope.  Returns (d_s, slope, r²).
    """
    log_t = []; log_P = []
    for t in range(t_lo, t_hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            log_t.append(math.log(t))
            log_P.append(math.log(P_t[t]))
    if len(log_t) < 2:
        return float("nan"), float("nan"), 0.0
    a, b, r2 = ols_fit(log_t, log_P)
    return -2.0 * b, b, r2


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg=(249, 251, 250)):
        self.width, self.height = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx = 1 if x0<x1 else -1; sy = 1 if y0<y1 else -1; err=dx-dy; x,y=x0,y0
        while True:
            self.set(x, y, c)
            if x==x1 and y==y1: break
            e2=2*err
            if e2>=-dy: err-=dy; x+=sx
            if e2<=dx:  err+=dx; y+=sy

    def rect(self, x0, y0, x1, y1, c):
        for x in range(x0,x1+1): self.set(x,y0,c); self.set(x,y1,c)
        for y in range(y0,y1+1): self.set(x0,y,c); self.set(x1,y,c)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        rsz = self.width * 3
        for y in range(self.height):
            raw.append(0); raw.extend(self.px[y*rsz:(y+1)*rsz])
        def chunk(tag, data):
            return struct.pack("!I", len(data)) + tag + data + struct.pack(
                "!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        path.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b"")
        )


def plot_qm_info(
    path: Path,
    P_t: list[float],
    t_lo: int,
    t_hi: int,
    ols_a_walk: float,
    ols_b_walk: float,
    q_list: list[float],
    K_eff: int,
) -> None:
    w, h = 980, 480
    half = w // 2 - 10
    left, top, right, bottom = 80, 30, half, h - 50
    ox = half + 20; rx = w - 20
    c = Canvas(w, h)
    c.rect(left, top, right, bottom, (74, 88, 82))
    c.rect(ox, top, rx, bottom, (74, 88, 82))

    # Left: log P(t) vs log t
    ts = [t for t in range(1, len(P_t)) if P_t[t] > 1e-10]
    if not ts: return
    log_ts = [math.log(t) for t in ts]
    log_Ps = [math.log(P_t[t]) for t in ts]
    lt_lo, lt_hi = min(log_ts), max(log_ts)
    lP_lo, lP_hi = min(log_Ps), max(log_Ps)
    if math.isclose(lt_lo, lt_hi): lt_hi = lt_lo + 0.1
    if math.isclose(lP_lo, lP_hi): lP_hi = lP_lo + 0.1

    def pxL(lt, lP):
        px = left + int((lt - lt_lo) / (lt_hi - lt_lo) * (right - left))
        py = bottom - int((lP - lP_lo) / (lP_hi - lP_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    for lt, lP in zip(log_ts, log_Ps):
        px, py = pxL(lt, lP)
        c.set(px, py, (40, 112, 184))
        c.set(px+1, py, (40, 112, 184))

    # OLS line on left
    x0p, y0p = pxL(lt_lo, ols_a_walk + ols_b_walk * lt_lo)
    x1p, y1p = pxL(lt_hi, ols_a_walk + ols_b_walk * lt_hi)
    c.line(x0p, y0p, x1p, y1p, (220, 80, 40))

    # Right: q_k histogram
    bins = 20
    bin_counts = [0] * bins
    for q in q_list:
        b = min(int(q * bins), bins - 1)
        bin_counts[b] += 1
    max_count = max(bin_counts) if bin_counts else 1
    bw = (rx - ox) // bins
    for bi, cnt in enumerate(bin_counts):
        bar_h = int(cnt / max_count * (bottom - top - 4))
        bx0 = ox + bi * bw + 1
        bx1 = bx0 + bw - 2
        by0 = bottom - bar_h
        for x in range(bx0, bx1 + 1):
            for y in range(by0, bottom + 1):
                c.set(x, y, (40, 150, 112))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG QM Information & Emergent Geometry (v1) — G18."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-modes", type=int, default=N_MODES)
    p.add_argument("--n-iter", type=int, default=N_ITER_POW)
    p.add_argument("--n-walks", type=int, default=N_WALKS)
    p.add_argument("--n-steps", type=int, default=N_STEPS)
    p.add_argument("--t-lo", type=int, default=T_LO)
    p.add_argument("--t-hi", type=int, default=T_HI)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    def log(msg: str = "") -> None:
        print(msg); log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG Quantum Information & Emergent Geometry (v1) — G18")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Graph ─────────────────────────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_degree = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    thresholds = InfoThresholds()

    # ── Spectral decomposition ────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iterations")
    t1 = time.time()
    rng_spec = random.Random(args.seed + 1)
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter, rng_spec)
    t2 = time.time()
    log(f"  Done in {t2-t1:.2f}s")
    log(f"  μ_0 (zero mode) = {fmt(mus[0])}  (expect ≈ 0)")
    log(f"  μ_1 (gap)       = {fmt(mus[1])}")
    log(f"  μ_max           = {fmt(mus[-1])}")

    # Active modes (skip zero mode)
    active_idx  = list(range(1, len(mus)))
    K_eff       = len(active_idx)
    mu_active   = [mus[k]     for k in active_idx]
    vecs_active = [eigvecs[k] for k in active_idx]
    omegas      = [math.sqrt(mu + args.m_eff_sq) for mu in mu_active]
    log(f"  K_eff = {K_eff}  |  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── G18a: binary entanglement entropy ─────────────────────────────────────
    log(f"\n[2] G18a — Binary entanglement entropy S_A (|A| = n//2 = {n//2})")
    rng_part = random.Random(args.seed + 3)
    S_A, q_list, hq_list = binary_entropy_partition(vecs_active, n, rng_part)
    entropy_threshold = 0.5 * K_eff * math.log(2)
    log(f"  q_k:  min={fmt(min(q_list))}  max={fmt(max(q_list))}  mean={fmt(statistics.mean(q_list))}")
    log(f"  h(q_k): min={fmt(min(hq_list))}  max={fmt(max(hq_list))}")
    log(f"  S_A = {fmt(S_A)}")
    log(f"  Threshold: S_A > 0.5·K·ln2 = {fmt(entropy_threshold)}")
    gate_g18a = S_A > entropy_threshold

    # ── G18b: inverse participation ratio ─────────────────────────────────────
    log(f"\n[3] G18b — Mode delocalization (IPR)")
    ipr_vals = compute_ipr(vecs_active, n)
    mean_ipr = statistics.mean(ipr_vals)
    n_ipr    = n * mean_ipr
    log(f"  IPR per mode (×n):  min={fmt(n*min(ipr_vals))}  max={fmt(n*max(ipr_vals))}  mean={fmt(n_ipr)}")
    log(f"  Uniform mode would give n·IPR = 1.0")
    log(f"  Threshold: n·mean(IPR) < {thresholds.g18b_ipr_max}")
    gate_g18b = n_ipr < thresholds.g18b_ipr_max

    # ── G18c: vacuum fluctuation homogeneity ───────────────────────────────────
    log(f"\n[4] G18c — Vacuum fluctuation homogeneity cv(G_ii)")
    G_diag = compute_local_propagator(vecs_active, omegas, n)
    mean_G = statistics.mean(G_diag)
    std_G  = statistics.stdev(G_diag)
    cv_G   = std_G / mean_G if mean_G > 1e-12 else float("inf")
    log(f"  G(i,i): min={fmt(min(G_diag))}  max={fmt(max(G_diag))}  mean={fmt(mean_G)}")
    log(f"  std={fmt(std_G)}  cv={fmt(cv_G)}")
    log(f"  Threshold: cv < {thresholds.g18c_cv_max}")
    gate_g18c = cv_G < thresholds.g18c_cv_max

    # ── G18d: spectral dimension from random walk ──────────────────────────────
    log(f"\n[5] G18d — Spectral dimension d_s (random walk: {args.n_walks} walks × {n} vertices × {args.n_steps} steps)")
    rng_walk = random.Random(args.seed + 4)
    t3 = time.time()
    P_t = random_walk_simulation(neighbours, args.n_walks, args.n_steps, rng_walk)
    t4 = time.time()
    log(f"  Done in {t4-t3:.3f}s")
    for t in range(1, args.n_steps + 1):
        log(f"  P(t={t:2d}) = {fmt(P_t[t])}")

    d_s, slope_rw, r2_rw = spectral_dimension(P_t, args.t_lo, min(args.t_hi, args.n_steps))
    log(f"  OLS log P(t) vs log t  [t={args.t_lo}..{args.t_hi}]:")
    log(f"    slope = {fmt(slope_rw)}  d_s = {fmt(d_s)}  R² = {fmt(r2_rw)}")
    log(f"  Threshold: d_s ∈ ({thresholds.g18d_ds_lo}, {thresholds.g18d_ds_hi})")
    gate_g18d = thresholds.g18d_ds_lo < d_s < thresholds.g18d_ds_hi

    # ── Final decision ────────────────────────────────────────────────────────
    gate_g18 = gate_g18a and gate_g18b and gate_g18c and gate_g18d
    decision = "pass" if gate_g18 else "fail"
    elapsed  = time.time() - t0
    log(f"\nQNG QM Information completed in {elapsed:.2f}s")
    log(f"decision={decision}  G18={gate_g18}"
        f"(a={gate_g18a},b={gate_g18b},c={gate_g18c},d={gate_g18d})")
    log(f"  G18a S_A:        {fmt(S_A)}  threshold=>{fmt(entropy_threshold)}")
    log(f"  G18b n·IPR:      {fmt(n_ipr)}  threshold=<{thresholds.g18b_ipr_max}")
    log(f"  G18c cv(G_ii):   {fmt(cv_G)}  threshold=<{thresholds.g18c_cv_max}")
    log(f"  G18d d_s:        {fmt(d_s)}  threshold∈({thresholds.g18d_ds_lo},{thresholds.g18d_ds_hi})")

    # ── Artifacts ──────────────────────────────────────────────────────────────
    modes_csv = out_dir / "qm_info_modes.csv"
    write_csv(modes_csv,
              ["mode_k", "mu_k", "omega_k", "IPR_k", "n_IPR_k", "q_k", "h_q_k"],
              [
                  {
                      "mode_k": k + 1,
                      "mu_k":    fmt(mu_active[k]),
                      "omega_k": fmt(omegas[k]),
                      "IPR_k":   fmt(ipr_vals[k]),
                      "n_IPR_k": fmt(n * ipr_vals[k]),
                      "q_k":     fmt(q_list[k]),
                      "h_q_k":   fmt(hq_list[k]),
                  }
                  for k in range(K_eff)
              ])

    walk_csv = out_dir / "qm_info_walk.csv"
    write_csv(walk_csv, ["t", "P_t", "log_t", "log_P_t"],
              [
                  {
                      "t":      t,
                      "P_t":    fmt(P_t[t]),
                      "log_t":  fmt(math.log(t)) if t > 0 else "nan",
                      "log_P_t": fmt(math.log(P_t[t])) if P_t[t] > 1e-10 else "nan",
                  }
                  for t in range(1, args.n_steps + 1)
              ])

    local_csv = out_dir / "qm_info_local.csv"
    write_csv(local_csv, ["vertex", "x", "y", "G_ii", "delta_sigma_vac"],
              [
                  {
                      "vertex": i,
                      "x": fmt(coords[i][0]),
                      "y": fmt(coords[i][1]),
                      "G_ii": fmt(G_diag[i]),
                      "delta_sigma_vac": fmt(math.sqrt(G_diag[i])),
                  }
                  for i in range(n)
              ])

    mc_csv = out_dir / "metric_checks_qm_info.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G18a", "metric": "binary_entropy_SA",
         "value": fmt(S_A),
         "threshold": f">{fmt(entropy_threshold)}",
         "status": "pass" if gate_g18a else "fail"},
        {"gate_id": "G18b", "metric": "n_times_mean_IPR",
         "value": fmt(n_ipr),
         "threshold": f"<{thresholds.g18b_ipr_max}",
         "status": "pass" if gate_g18b else "fail"},
        {"gate_id": "G18c", "metric": "cv_G_diag",
         "value": fmt(cv_G),
         "threshold": f"<{thresholds.g18c_cv_max}",
         "status": "pass" if gate_g18c else "fail"},
        {"gate_id": "G18d", "metric": "spectral_dimension_ds",
         "value": fmt(d_s),
         "threshold": f"({thresholds.g18d_ds_lo},{thresholds.g18d_ds_hi})",
         "status": "pass" if gate_g18d else "fail"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision,
         "threshold": "G18a&G18b&G18c&G18d", "status": decision},
    ])

    # OLS coefficients for the walk plot line
    _lt = [math.log(t) for t in range(args.t_lo, args.t_hi + 1)
           if t < len(P_t) and P_t[t] > 1e-9]
    _lP = [math.log(P_t[t]) for t in range(args.t_lo, args.t_hi + 1)
           if t < len(P_t) and P_t[t] > 1e-9]
    ols_a_w, ols_b_w, _ = ols_fit(_lt, _lP) if len(_lt) >= 2 else (0, 0, 0)

    plot_qm_info(out_dir / "qm_info-plot.png",
                 P_t, args.t_lo, args.t_hi, ols_a_w, ols_b_w, q_list, K_eff)

    config = {
        "script": "run_qng_qm_info_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "K_eff": K_eff,
        "m_eff_sq": args.m_eff_sq,
        "spectral_gap_mu1": round(mus[1] if len(mus)>1 else 0, 8),
        "binary_entropy_SA": round(S_A, 6),
        "entropy_threshold": round(entropy_threshold, 6),
        "mean_IPR": round(mean_ipr, 8),
        "n_times_mean_IPR": round(n_ipr, 6),
        "mean_G_diag": round(mean_G, 8),
        "cv_G_diag": round(cv_G, 6),
        "spectral_dim_ds": round(d_s, 6) if not math.isnan(d_s) else None,
        "rw_slope": round(slope_rw, 8) if not math.isnan(slope_rw) else None,
        "rw_r2": round(r2_rw, 6),
        "n_walks": args.n_walks,
        "n_steps": args.n_steps,
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_qm_info.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    artifact_files = [
        modes_csv, walk_csv, local_csv, mc_csv,
        out_dir / "qm_info-plot.png",
        out_dir / "config_qm_info.json",
    ]
    (out_dir / "artifact-hashes-qm-info.json").write_text(
        json.dumps({p.name: sha256_of(p) for p in artifact_files if p.exists()}, indent=2),
        encoding="utf-8",
    )
    (out_dir / "run-log-qm-info.txt").write_text("\n".join(log_lines), encoding="utf-8")
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-qm-info.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0 if gate_g18 else 1


if __name__ == "__main__":
    sys.exit(main())
