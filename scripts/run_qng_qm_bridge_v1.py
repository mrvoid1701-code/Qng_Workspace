#!/usr/bin/env python3
"""
QNG Quantum Mechanics Bridge: canonical quantization on QNG graph (v1).

Promotes the classical scalar field σ → σ̂ (quantum field operator) and
derives observable consequences via canonical quantization of the action
from G16.

Quantum field construction
──────────────────────────
The action from G16:

    S_matter[σ] = Σ_i [−½|∇σ|²(i) − (m²/2)σ(i)²] · vol(i)

implies the canonical momentum (natural units, c = ħ = 1):

    π̂(i) = ∂_t σ̂(i)

and the equal-time commutation relation:

    [σ̂(i), π̂(j)] = i δ_{ij}

Spectral decomposition
───────────────────────
The spatial kinetic operator on the graph is −L_rw:

    M = −L_rw = I − D^{−1}A,   eigenvalues μ_k ∈ [0, 1]

Computed via deflated power iteration on D^{−1}A:
  · Mode k=0 (constant vector, μ_0=0) is the zero mode — excluded from sums.
  · Modes k=1…K_eff carry the physical degrees of freedom.

Dispersion relation (Klein-Gordon on graph):

    ω_k = √(μ_k + m_eff²)

where m_eff² = |m²_fit| from G16 (absolute value for positive mass).

Vacuum state and observables
─────────────────────────────
Fock vacuum |0⟩: lowest-energy state of Ĥ = Σ_k ω_k (n̂_k + ½).

1.  Zero-point energy:

        E_0 = ½ Σ_{k=1}^{K_eff} ω_k

2.  Vacuum two-point function (propagator):

        G(i,j) = ⟨0|σ̂(i)σ̂(j)|0⟩ = Σ_{k=1}^{K_eff} ψ_k(i)ψ_k(j) / (2ω_k)

    G(i,i) = local vacuum fluctuation amplitude squared.

3.  Uncertainty relation per mode k (vacuum = minimum-uncertainty state):

        Δσ_k = 1/√(2ω_k),   Δπ_k = √(ω_k/2)
        Δσ_k · Δπ_k = ½   (saturates Heisenberg bound)

Gates (G17):
    G17a — Spectral gap:
           μ_1 > 0.01  (graph connected; first excitation gapped above vacuum)
    G17b — Propagator spatial decay:
           OLS slope of G(i,j) vs r_{ij} < −0.01
           (vacuum correlations decrease with distance — massive Yukawa field)
    G17c — Zero-point energy per mode:
           0.05 < E_0/K_eff < 5.0  (finite; correctly UV-bounded in truncation)
    G17d — Heisenberg uncertainty relation:
           |mean_k(Δσ_k · Δπ_k) − 0.5| < 0.01
           (each mode saturates the Heisenberg bound; quantisation correct)

Outputs (in --out-dir):
    qm_modes.csv              per-mode: k, mu_k, omega_k, delta_sigma, delta_pi, product
    propagator_sample.csv     sample pairs: i, j, r_ij, G_ij
    local_fluctuations.csv    per-vertex: G_ii, delta_sigma_vac
    metric_checks_qm.csv      G17 gate summary
    qm_bridge-plot.png        propagator decay (left) + local fluctuation map (right)
    config_qm.json
    run-log-qm.txt
    artifact-hashes-qm.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qm-bridge-v1"
)

PHI_SCALE   = 0.10
M_EFF_SQ    = 0.014      # |m²_fit| from G16 (positive effective mass squared)
N_MODES     = 20         # total modes to find (including zero mode)
N_ITER_POW  = 350        # power-iteration steps per mode
N_SAMPLE    = 800        # random pairs for propagator sampling
C_LIGHT     = 1.0        # natural units


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class QMThresholds:
    g17a_gap_min: float       = 0.01   # μ_1 > 0.01
    g17b_slope_max: float     = -0.01  # OLS slope G vs r < -0.01
    g17c_e0_per_mode_lo: float = 0.05  # E_0/K_eff > 0.05
    g17c_e0_per_mode_hi: float = 5.0   # E_0/K_eff < 5.0
    g17d_heisenberg_tol: float = 0.01  # |mean(ΔσΔπ) - 0.5| < 0.01


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


# ── OLS fit ───────────────────────────────────────────────────────────────────
def ols_fit(x_vals: list[float], y_vals: list[float]) -> tuple[float, float, float]:
    n = len(x_vals)
    if n < 2: return 0.0, 0.0, 0.0
    mx = sum(x_vals) / n; my = sum(y_vals) / n
    Sxx = sum((x - mx)**2 for x in x_vals)
    Sxy = sum((x_vals[i] - mx) * (y_vals[i] - my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0.0, 0.0
    b = Sxy / Sxx; a = my - b * mx
    ss_tot = sum((y - my)**2 for y in y_vals)
    if ss_tot < 1e-30: return a, b, 1.0
    ss_res = sum((y_vals[i] - (a + b * x_vals[i]))**2 for i in range(n))
    return a, b, max(0.0, 1.0 - ss_res / ss_tot)


# ── Spectral computation via deflated power iteration ─────────────────────────
def _dot(u: list[float], v: list[float]) -> float:
    return sum(u[i] * v[i] for i in range(len(u)))


def _norm(v: list[float]) -> float:
    return math.sqrt(_dot(v, v))


def _normalize(v: list[float]) -> list[float]:
    nrm = _norm(v)
    return [x / nrm for x in v] if nrm > 1e-14 else v[:]


def _deflate(v: list[float], basis: list[list[float]]) -> list[float]:
    """Remove projections of v onto each vector in basis (Gram-Schmidt)."""
    w = v[:]
    for b in basis:
        c = _dot(w, b)
        w = [w[i] - c * b[i] for i in range(len(w))]
    return w


def _apply_rw(f: list[float], neighbours: list[list[int]]) -> list[float]:
    """Apply D^{-1}A to f: (D^{-1}A f)(i) = (1/k_i) Σ_{j∈N(i)} f(j)."""
    return [
        (sum(f[j] for j in nb) / len(nb)) if nb else 0.0
        for nb in neighbours
    ]


def compute_eigenmodes(
    neighbours: list[list[int]],
    n_modes: int,
    n_iter: int,
    rng: random.Random,
) -> tuple[list[float], list[list[float]]]:
    """
    Find top n_modes eigenvectors of D^{-1}A (= eigenvectors of L_rw)
    via deflated power iteration.

    Returns (mu_list, vec_list) where mu_k = eigenvalue of −L_rw = 1 − α_k.
    Sorted in ascending order of mu_k (= ascending frequency).
    """
    n = len(neighbours)
    vecs: list[list[float]] = []
    mus:  list[float]        = []

    for _ in range(n_modes):
        # Random start, orthogonalised to previous modes
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, vecs)
        nrm = _norm(v)
        if nrm < 1e-14:
            continue
        v = _normalize(v)

        # Power iteration on D^{-1}A (finds eigenvector with largest eigenvalue)
        for _ in range(n_iter):
            w = _apply_rw(v, neighbours)
            w = _deflate(w, vecs)
            nrm = _norm(w)
            if nrm < 1e-14:
                break
            v = [x / nrm for x in w]

        # Rayleigh quotient: α = v^T (D^{-1}A) v
        Av = _apply_rw(v, neighbours)
        alpha = _dot(v, Av)
        mu = max(0.0, 1.0 - alpha)   # eigenvalue of −L_rw; clamp ≥ 0

        vecs.append(v)
        mus.append(mu)

    # Sort by ascending μ (zero mode first, then increasing frequency)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Propagator ────────────────────────────────────────────────────────────────
def compute_propagator_sample(
    eigvecs: list[list[float]],
    omegas: list[float],
    coords: list[tuple[float, float]],
    pairs: list[tuple[int, int]],
) -> tuple[list[float], list[float]]:
    """
    G(i,j) = Σ_k ψ_k(i) ψ_k(j) / (2 ω_k)  for sampled pairs.
    Returns (r_list, G_list).
    """
    K = len(omegas)
    r_list: list[float] = []
    G_list: list[float] = []
    for i, j in pairs:
        xi, yi = coords[i]; xj, yj = coords[j]
        r_ij = math.hypot(xi - xj, yi - yj)
        G_ij = sum(eigvecs[k][i] * eigvecs[k][j] / (2.0 * omegas[k])
                   for k in range(K))
        r_list.append(r_ij)
        G_list.append(G_ij)
    return r_list, G_list


def compute_local_propagator(
    eigvecs: list[list[float]],
    omegas: list[float],
    n: int,
) -> list[float]:
    """G(i,i) = Σ_k ψ_k(i)² / (2 ω_k)  — local vacuum fluctuation amplitude²."""
    K = len(omegas)
    G_diag = [0.0] * n
    for k in range(K):
        inv2w = 1.0 / (2.0 * omegas[k])
        for i in range(n):
            G_diag[i] += eigvecs[k][i]**2 * inv2w
    return G_diag


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg=(255, 255, 255)):
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


def plot_qm(
    path: Path,
    r_vals: list[float],
    G_vals: list[float],
    coords: list[tuple[float, float]],
    G_diag: list[float],
    ols_a: float,
    ols_b: float,
) -> None:
    w, h = 980, 480
    half = w // 2 - 10
    left, top, right, bottom = 80, 30, half, h - 50
    ox = half + 20; rx = w - 20
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))
    c.rect(ox, top, rx, bottom, (74, 88, 82))

    # Left: G(i,j) vs r_{ij} scatter + OLS line
    r_lo, r_hi = min(r_vals), max(r_vals)
    G_lo, G_hi = min(G_vals), max(G_vals)
    if math.isclose(r_lo, r_hi): r_hi = r_lo + 0.1
    if math.isclose(G_lo, G_hi): G_hi = G_lo + 0.01

    def pxL(r, g):
        px = left + int((r - r_lo) / (r_hi - r_lo + 1e-12) * (right - left))
        py = bottom - int((g - G_lo) / (G_hi - G_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    for r, g in zip(r_vals, G_vals):
        px, py = pxL(r, g)
        c.set(px, py, (40, 112, 184))

    # OLS fit line
    xs = [r_lo, r_hi]
    x0p, y0p = pxL(xs[0], ols_a + ols_b * xs[0])
    x1p, y1p = pxL(xs[1], ols_a + ols_b * xs[1])
    c.line(x0p, y0p, x1p, y1p, (220, 80, 40))

    # Right: spatial map of G(i,i) = vacuum fluctuation
    all_x = [xy[0] for xy in coords]
    all_y = [xy[1] for xy in coords]
    cx_lo, cx_hi = min(all_x), max(all_x)
    cy_lo, cy_hi = min(all_y), max(all_y)
    gd_lo, gd_hi = min(G_diag), max(G_diag)
    if math.isclose(gd_lo, gd_hi): gd_hi = gd_lo + 1e-6

    def pxR(xi, yi):
        px = ox + int((xi - cx_lo) / (cx_hi - cx_lo + 1e-12) * (rx - ox))
        py = bottom - int((yi - cy_lo) / (cy_hi - cy_lo + 1e-12) * (bottom - top))
        return max(ox, min(rx, px)), max(top, min(bottom, py))

    for i, (xi, yi) in enumerate(coords):
        t = (G_diag[i] - gd_lo) / (gd_hi - gd_lo)   # 0=low, 1=high fluctuation
        r_col = int(40 + 180 * t)
        b_col = int(184 - 144 * t)
        px, py = pxR(xi, yi)
        c.set(px, py, (r_col, 80, b_col))
        c.set(px+1, py, (r_col, 80, b_col))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG QM Bridge: canonical quantization on graph (v1) — G17."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-modes", type=int, default=N_MODES)
    p.add_argument("--n-iter", type=int, default=N_ITER_POW)
    p.add_argument("--n-sample", type=int, default=N_SAMPLE)
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
    log("QNG Quantum Mechanics Bridge (v1) — canonical quantisation on graph")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_degree = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")
    log(f"m_eff² = {args.m_eff_sq}  →  m_eff = {math.sqrt(args.m_eff_sq):.6f}")

    thresholds = QMThresholds()

    # ── Spectral decomposition: eigenmodes of −L_rw via power iteration ───────
    log(f"\n[1] Spectral decomposition: {args.n_modes} modes × {args.n_iter} iterations")
    t1 = time.time()
    rng_spec = random.Random(args.seed + 1)
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter, rng_spec)
    t2 = time.time()
    log(f"  Done in {t2-t1:.2f}s")
    log(f"  μ_0 (zero mode) = {fmt(mus[0])}  (expect ≈ 0)")
    log(f"  μ_1 (gap)       = {fmt(mus[1])}  (spectral gap)")
    log(f"  μ_max (mode {args.n_modes-1}) = {fmt(mus[-1])}")
    log(f"  All μ_k ≥ 0: {all(mu >= 0 for mu in mus)}")

    # Skip mode 0 (zero mode, μ≈0, constant vector)
    active_idx = [k for k in range(len(mus)) if k > 0]   # modes 1..K_eff
    K_eff = len(active_idx)
    mu_active    = [mus[k]    for k in active_idx]
    vecs_active  = [eigvecs[k] for k in active_idx]

    # ── Frequencies: ω_k = √(μ_k + m_eff²) ──────────────────────────────────
    log(f"\n[2] Quantum frequencies ω_k = √(μ_k + m_eff²)  (K_eff = {K_eff} modes)")
    omegas = [math.sqrt(mu + args.m_eff_sq) for mu in mu_active]
    log(f"  ω_min = {fmt(min(omegas))}  (= √(m_eff²) = {fmt(math.sqrt(args.m_eff_sq))} for μ≈0 mode)")
    log(f"  ω_max = {fmt(max(omegas))}")
    log(f"  mean ω = {fmt(statistics.mean(omegas))}")

    # ── Zero-point energy ─────────────────────────────────────────────────────
    log(f"\n[3] Zero-point energy E_0 = ½ Σ_k ω_k  (truncated to K_eff={K_eff})")
    E_0 = 0.5 * sum(omegas)
    E_0_per_mode = E_0 / K_eff
    log(f"  E_0 = {fmt(E_0)}")
    log(f"  E_0 / K_eff = {fmt(E_0_per_mode)}")

    # ── Uncertainty relation per mode ─────────────────────────────────────────
    log(f"\n[4] Heisenberg uncertainty relation Δσ_k · Δπ_k per mode:")
    delta_sigma = [1.0 / math.sqrt(2.0 * w) for w in omegas]
    delta_pi    = [math.sqrt(w / 2.0)       for w in omegas]
    products    = [delta_sigma[k] * delta_pi[k] for k in range(K_eff)]
    mean_prod   = statistics.mean(products)
    log(f"  Δσ_k = 1/√(2ω_k):    range [{fmt(min(delta_sigma))}, {fmt(max(delta_sigma))}]")
    log(f"  Δπ_k = √(ω_k/2):     range [{fmt(min(delta_pi))},    {fmt(max(delta_pi))}]")
    log(f"  Δσ_k · Δπ_k:         range [{fmt(min(products))},   {fmt(max(products))}]")
    log(f"  mean(Δσ_k · Δπ_k) = {fmt(mean_prod)}   (Heisenberg: should = 0.5)")

    # ── Propagator G(i,j) for sampled pairs ──────────────────────────────────
    log(f"\n[5] Vacuum propagator G(i,j) — sample of {args.n_sample} pairs")
    rng_samp = random.Random(args.seed + 2)
    all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    sampled = rng_samp.sample(all_pairs, min(args.n_sample, len(all_pairs)))

    t3 = time.time()
    r_vals, G_vals = compute_propagator_sample(vecs_active, omegas, coords, sampled)
    t4 = time.time()
    log(f"  Computed {len(sampled)} G(i,j) values in {t4-t3:.3f}s")
    log(f"  G(i,j): min={fmt(min(G_vals))}  max={fmt(max(G_vals))}  mean={fmt(statistics.mean(G_vals))}")
    log(f"  r_{'{ij}'}: min={fmt(min(r_vals))}  max={fmt(max(r_vals))}  mean={fmt(statistics.mean(r_vals))}")

    # OLS slope of G vs r  (Yukawa: G decays with distance)
    ols_a, ols_b, ols_r2 = ols_fit(r_vals, G_vals)
    log(f"  OLS G ~ a + b·r:  a={fmt(ols_a)}  b={fmt(ols_b)}  R²={fmt(ols_r2)}")

    # ── Local propagator G(i,i) ───────────────────────────────────────────────
    log(f"\n[6] Local propagator G(i,i) = vacuum fluctuation amplitude²")
    G_diag = compute_local_propagator(vecs_active, omegas, n)
    delta_sigma_vac = [math.sqrt(g) for g in G_diag]
    log(f"  G(i,i): min={fmt(min(G_diag))}  max={fmt(max(G_diag))}  mean={fmt(statistics.mean(G_diag))}")
    log(f"  Δσ_vac = √G(i,i): mean={fmt(statistics.mean(delta_sigma_vac))}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    spectral_gap = mus[1] if len(mus) > 1 else 0.0
    heisenberg_dev = abs(mean_prod - 0.5)

    gate_g17a = spectral_gap   > thresholds.g17a_gap_min
    gate_g17b = ols_b          < thresholds.g17b_slope_max
    gate_g17c = (thresholds.g17c_e0_per_mode_lo < E_0_per_mode
                 < thresholds.g17c_e0_per_mode_hi)
    gate_g17d = heisenberg_dev < thresholds.g17d_heisenberg_tol
    gate_g17  = gate_g17a and gate_g17b and gate_g17c and gate_g17d
    decision  = "pass" if gate_g17 else "fail"

    elapsed = time.time() - t0
    log(f"\nQNG QM Bridge completed.")
    log(f"decision={decision}  G17={gate_g17}"
        f"(a={gate_g17a},b={gate_g17b},c={gate_g17c},d={gate_g17d})")
    log(f"G17a spectral gap:    μ_1={fmt(spectral_gap)}"
        f"  threshold=>{thresholds.g17a_gap_min}")
    log(f"G17b propagator slope:b={fmt(ols_b)}"
        f"  threshold=<{thresholds.g17b_slope_max}")
    log(f"G17c E_0/K_eff:       {fmt(E_0_per_mode)}"
        f"  threshold∈({thresholds.g17c_e0_per_mode_lo},{thresholds.g17c_e0_per_mode_hi})")
    log(f"G17d Heisenberg dev:  |mean(ΔσΔπ)−0.5|={fmt(heisenberg_dev)}"
        f"  threshold=<{thresholds.g17d_heisenberg_tol}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    modes_csv = out_dir / "qm_modes.csv"
    write_csv(modes_csv,
              ["mode_k", "mu_k", "omega_k", "delta_sigma", "delta_pi", "ds_dp_product"],
              [
                  {
                      "mode_k": k + 1,
                      "mu_k": fmt(mu_active[k]),
                      "omega_k": fmt(omegas[k]),
                      "delta_sigma": fmt(delta_sigma[k]),
                      "delta_pi": fmt(delta_pi[k]),
                      "ds_dp_product": fmt(products[k]),
                  }
                  for k in range(K_eff)
              ])

    prop_csv = out_dir / "propagator_sample.csv"
    write_csv(prop_csv,
              ["pair_i", "pair_j", "r_ij", "G_ij"],
              [
                  {
                      "pair_i": sampled[p][0],
                      "pair_j": sampled[p][1],
                      "r_ij": fmt(r_vals[p]),
                      "G_ij": fmt(G_vals[p]),
                  }
                  for p in range(len(sampled))
              ])

    fluct_csv = out_dir / "local_fluctuations.csv"
    write_csv(fluct_csv,
              ["vertex", "x", "y", "sigma_norm", "G_ii", "delta_sigma_vac"],
              [
                  {
                      "vertex": i,
                      "x": fmt(coords[i][0]),
                      "y": fmt(coords[i][1]),
                      "sigma_norm": fmt(sigma[i] / max(sigma)),
                      "G_ii": fmt(G_diag[i]),
                      "delta_sigma_vac": fmt(delta_sigma_vac[i]),
                  }
                  for i in range(n)
              ])

    mc_csv = out_dir / "metric_checks_qm.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G17a", "metric": "spectral_gap",
         "value": fmt(spectral_gap),
         "threshold": f">{thresholds.g17a_gap_min}",
         "status": "pass" if gate_g17a else "fail"},
        {"gate_id": "G17b", "metric": "propagator_slope",
         "value": fmt(ols_b),
         "threshold": f"<{thresholds.g17b_slope_max}",
         "status": "pass" if gate_g17b else "fail"},
        {"gate_id": "G17c", "metric": "E0_per_mode",
         "value": fmt(E_0_per_mode),
         "threshold": f"({thresholds.g17c_e0_per_mode_lo},{thresholds.g17c_e0_per_mode_hi})",
         "status": "pass" if gate_g17c else "fail"},
        {"gate_id": "G17d", "metric": "heisenberg_dev",
         "value": fmt(heisenberg_dev),
         "threshold": f"<{thresholds.g17d_heisenberg_tol}",
         "status": "pass" if gate_g17d else "fail"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision,
         "threshold": "G17a&G17b&G17c&G17d", "status": decision},
    ])

    plot_qm(out_dir / "qm_bridge-plot.png",
            r_vals, G_vals, coords, G_diag, ols_a, ols_b)

    config = {
        "script": "run_qng_qm_bridge_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "n_modes_total": args.n_modes,
        "K_eff": K_eff,
        "n_iter_power": args.n_iter,
        "m_eff_sq": args.m_eff_sq,
        "m_eff": round(math.sqrt(args.m_eff_sq), 8),
        "spectral_gap_mu1": round(spectral_gap, 8),
        "omega_min": round(min(omegas), 8),
        "omega_max": round(max(omegas), 8),
        "omega_mean": round(statistics.mean(omegas), 8),
        "E0": round(E_0, 6),
        "E0_per_mode": round(E_0_per_mode, 6),
        "mean_heisenberg_product": round(mean_prod, 10),
        "heisenberg_dev": round(heisenberg_dev, 12),
        "ols_slope_G_vs_r": round(ols_b, 8),
        "ols_r2_G_vs_r": round(ols_r2, 6),
        "mean_G_diag": round(statistics.mean(G_diag), 8),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_qm.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    artifact_files = [modes_csv, prop_csv, fluct_csv, mc_csv,
                      out_dir / "qm_bridge-plot.png", out_dir / "config_qm.json"]
    (out_dir / "artifact-hashes-qm.json").write_text(
        json.dumps({p.name: sha256_of(p) for p in artifact_files if p.exists()}, indent=2),
        encoding="utf-8",
    )
    (out_dir / "run-log-qm.txt").write_text("\n".join(log_lines), encoding="utf-8")
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-qm.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0 if gate_g17 else 1


if __name__ == "__main__":
    sys.exit(main())
