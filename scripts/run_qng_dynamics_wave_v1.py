#!/usr/bin/env python3
"""
QNG dynamics: wave propagation test (v1).

Tests the prediction from qng-wave-equation-v1.md:

    ∂_t²δΣ = c² ∇²_graph δΣ     (wave equation on the QNG graph)

Starting from a localized Gaussian perturbation δΣ(x,0) at the highest-Σ
node (the gravitational "source" centre), we evolve forward in time using the
leapfrog scheme:

    u_{t+1}(i) = 2u_t(i) - u_{t-1}(i) + c²dt² [L·u_t](i)

where L is the degree-normalised (random-walk) graph Laplacian:

    [L·u](i) = (1/k_i) Σ_{j∈N(i)} (u(j) - u(i))   k_i = degree of i

This operator has eigenvalues in [-2, 0]; the CFL stability condition is
c·dt ≤ √2.  We use c = C_WAVE, dt = DT (see parameters below).

Gates:
    G5a — Stability: max |u_i(t)| over all i,t  ≤ 1.5 · max |u_i(0)|
           (no numerical blow-up; leapfrog is stable well within CFL limit)
    G5b — Spread: σ(T)/σ(0) > 1.2
           (RMS spread grows → wave propagates away from source)
    G5c — Dynamism: max_t σ(t) / min_t σ(t) > 1.2
           (spread is NOT constant → perturbation is evolving, not frozen)
    G5d — Dispersion: excite the highest-frequency eigenmode of the graph
           Laplacian (most-negative eigenvalue λ_d, found via power iteration);
           measure the oscillation frequency ω_meas from zero-crossings of a
           single node's time-series in a separate 300-step sub-simulation;
           verify ω_meas ≈ c·√|λ_d| (within 25%).  This directly confirms the
           linear dispersion relation ω = c|k| for the discrete wave equation.

Outputs (in --out-dir):
    wave_energy.csv          E(t) and σ(t) at each recorded timestep
    wave_eigenmode.csv       G5d eigenmode sub-simulation: u[node](t) vs time
    metric_checks_wave.csv   G5 gate summary (G5a–G5d)
    wave_energy-plot.png     E(t)/E(0) vs time (raster)
    wave_spread-plot.png     σ(t)/σ(0) vs time (raster)
    wave_eigenmode-plot.png  eigenmode trajectory u(t) with ±AMP reference lines
    run-log-wave.txt

Derivation reference: 03_math/derivations/qng-wave-equation-v1.md
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-dynamics-wave-v1"
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"

# ── Wave simulation parameters ────────────────────────────────────────────────
C_WAVE_DEFAULT = 0.15    # effective wave speed in normalised graph units
DT_DEFAULT = 0.40        # time step  (CFL: c·dt ≤ √2 ≈ 1.41; 0.15×0.40=0.06 ✓)
N_STEPS_DEFAULT = 80     # total simulation steps  → T = 80×0.40 = 32 time units
SIGMA_INIT_DEFAULT = 1.0 # Gaussian initial width (Euclidean graph coordinate units)
AMP_INIT = 0.01          # perturbation amplitude (small → linear regime)
RECORD_EVERY = 4         # record E(t) and σ(t) every this many steps
N_STEPS_G5D = 300        # G5d eigenmode sub-simulation steps (T = 300×0.4 = 120 time units)


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class WaveThresholds:
    g5a_stability_max: float = 1.5      # max|u(t)| / max|u(0)| ≤ 1.5 (no blow-up)
    g5b_spread_ratio_min: float = 1.2   # σ(T)/σ(0) > 1.2
    g5c_dynamism_min: float = 1.2       # max_t σ(t) / min_t σ(t) > 1.2
    g5d_freq_rel_tol: float = 0.25      # |ω_meas/ω_pred − 1| < 0.25
    g5d_min_crossings: int = 2          # need at least this many zero-crossings


# ── Utility ───────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


# ── Graph builder (identical to v5/v6) ───────────────────────────────────────
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


# ── Graph Laplacian (degree-normalised / random-walk) ────────────────────────
def build_adjacency(n: int, adj_list: list[list[tuple[int, float]]]) -> list[list[int]]:
    """Return simple neighbour lists (unweighted)."""
    return [[j for j, _ in row] for row in adj_list]


def apply_laplacian(
    u: list[float],
    neighbours: list[list[int]],
) -> list[float]:
    """
    Degree-normalised graph Laplacian:
        [L·u](i) = (1/k_i) Σ_{j∈N(i)} (u(j) - u(i))
    Eigenvalues ∈ [-2, 0].  CFL stable for c·dt ≤ √2.
    """
    n = len(u)
    Lu = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
            continue
        s = sum(u[j] - u[i] for j in nb)
        Lu[i] = s / ki
    return Lu


# ── Energy and spread diagnostics ────────────────────────────────────────────
def discrete_energy(
    u_cur: list[float],
    u_prev: list[float],
    neighbours: list[list[int]],
    c2: float,
    dt: float,
) -> float:
    """
    Discrete conserved energy (leapfrog, unweighted Laplacian):
        E = ½ Σ_i [(u_cur_i - u_prev_i)/dt]²       (kinetic, centred)
          + ½ c² Σ_{(i,j)∈E} (u_cur_i - u_cur_j)²  (potential)

    The kinetic term uses the staggered velocity (u_cur - u_prev)/dt.
    For true leapfrog energy, half-step velocities should be used; here we
    use the simpler centred approximation which is O(dt²) accurate.
    """
    n = len(u_cur)
    # Kinetic
    kin = 0.0
    for i in range(n):
        vi = (u_cur[i] - u_prev[i]) / dt
        kin += vi * vi
    kin *= 0.5
    # Potential: sum over directed edges, divide by 2 at end
    pot = 0.0
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        for j in neighbours[i]:
            if (i, j) not in seen and (j, i) not in seen:
                diff = u_cur[i] - u_cur[j]
                pot += diff * diff
                seen.add((i, j))
    pot *= 0.5 * c2
    return kin + pot


def rms_spread(
    u: list[float],
    coords: list[tuple[float, float]],
    centre: tuple[float, float],
) -> float:
    """
    Euclidean RMS spread of perturbation u around centre:
        σ = sqrt( Σ_i |x_i - centre|² |u_i|² / Σ_i |u_i|² )
    """
    num = 0.0
    den = 0.0
    cx, cy = centre
    for i, (x, y) in enumerate(coords):
        ui2 = u[i] * u[i]
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        num += d2 * ui2
        den += ui2
    if den < 1e-30:
        return 0.0
    return math.sqrt(num / den)


# ── G5d: power iteration for most-negative Laplacian eigenvalue ──────────────
def power_iteration_min_eigenvalue(
    neighbours: list[list[int]],
    n_iters: int = 500,
    seed: int = 42,
) -> tuple[float, list[float]]:
    """
    Find the most-negative eigenvalue λ_d (and its eigenvector v_d) of the
    degree-normalised Laplacian L_rw via power iteration on −L_rw.

    −L_rw has eigenvalues in [0, 2]; its largest eigenvalue corresponds to
    the MOST NEGATIVE eigenvalue of L_rw (the highest-frequency wave mode).

    Returns (lambda_d, v_d) where:
        lambda_d ≤ 0  (most negative eigenvalue of L_rw)
        v_d           normalised so max_i |v_d[i]| = 1.0
    """
    rng = random.Random(seed)
    n = len(neighbours)
    v = [rng.gauss(0.0, 1.0) for _ in range(n)]
    norm = math.sqrt(sum(x * x for x in v))
    v = [x / norm for x in v]

    lam = 0.0
    for _ in range(n_iters):
        # Apply L_rw to v
        Lv = [0.0] * n
        for i in range(n):
            nb = neighbours[i]
            ki = len(nb)
            if ki > 0:
                Lv[i] = sum(v[j] - v[i] for j in nb) / ki
        # Rayleigh quotient of L_rw (will converge to λ_d)
        num = sum(v[i] * Lv[i] for i in range(n))
        den = sum(v[i] * v[i] for i in range(n))
        lam = num / den if den > 1e-30 else 0.0
        # Power iteration step: apply −L_rw = negate Lv
        neg_Lv = [-x for x in Lv]
        norm = math.sqrt(sum(x * x for x in neg_Lv))
        if norm < 1e-12:
            break
        v = [x / norm for x in neg_Lv]

    # Normalise so max |v_i| = 1
    v_max = max(abs(x) for x in v)
    if v_max > 1e-12:
        v = [x / v_max for x in v]
    return lam, v


# ── Canvas / PNG writer (minimal, identical to v5/v6) ────────────────────────
class Canvas:
    def __init__(self, width: int, height: int, bg: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.px = bytearray(bg * (width * height))

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i: i + 3] = bytes(color)

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
            raw.extend(self.px[i0: i0 + row])

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


def plot_timeseries(
    path: Path,
    xs: list[float],
    ys: list[float],
    color: tuple[int, int, int] = (40, 112, 184),
    hline: float | None = None,
    hline_color: tuple[int, int, int] = (200, 50, 50),
) -> None:
    """Plot a simple line chart of ys vs xs."""
    if not xs or not ys:
        return
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    if hline is not None:
        y_lo = min(y_lo, hline)
        y_hi = max(y_hi, hline)
    if math.isclose(x_lo, x_hi):
        x_hi = x_lo + 1.0
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    def to_px(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return clamp(px, left, right), clamp(py, top, bottom)

    if hline is not None:
        hx0, hy0 = to_px(x_lo, hline)
        hx1, hy1 = to_px(x_hi, hline)
        c.line(hx0, hy0, hx1, hy1, hline_color)

    for i in range(len(xs) - 1):
        x0p, y0p = to_px(xs[i], ys[i])
        x1p, y1p = to_px(xs[i + 1], ys[i + 1])
        c.line(x0p, y0p, x1p, y1p, color)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG dynamics wave propagation test v1 — Gate G5."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--c-wave", type=float, default=C_WAVE_DEFAULT,
                   help="Effective wave speed (graph normalised units). Default=0.15.")
    p.add_argument("--dt", type=float, default=DT_DEFAULT,
                   help="Time step. CFL: c*dt <= sqrt(2). Default=0.40.")
    p.add_argument("--n-steps", type=int, default=N_STEPS_DEFAULT,
                   help="Number of leapfrog steps. Default=80.")
    p.add_argument("--sigma-init", type=float, default=SIGMA_INIT_DEFAULT,
                   help="Initial Gaussian spread (Euclidean units). Default=1.0.")
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()

    # CFL check
    cfl = args.c_wave * args.dt
    if cfl > math.sqrt(2) * 0.99:
        print(f"ERROR: CFL violated: c*dt = {cfl:.4f} > sqrt(2) = {math.sqrt(2):.4f}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    thresholds = WaveThresholds()
    warnings: list[str] = []

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list, median_edge = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)

    # ── Find source centre (highest-Sigma node) ───────────────────────────────
    centre_idx = max(range(n), key=lambda i: sigma[i])
    centre_xy = coords[centre_idx]

    # ── Initial perturbation: Gaussian centred at source node ─────────────────
    #   δΣ_i(0) = AMP * exp(-|x_i - centre|² / (2 σ_init²))
    #   ∂_t δΣ(0) = 0  →  u_{-1} = u_0  (start from rest)
    u_cur: list[float] = []
    cx, cy = centre_xy
    for x, y in coords:
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        val = AMP_INIT * math.exp(-d2 / (2.0 * args.sigma_init ** 2))
        u_cur.append(val)
    u_prev = u_cur[:]  # zero initial velocity

    max_u0 = max(abs(v) for v in u_cur)
    sigma0 = rms_spread(u_cur, coords, centre_xy)

    if sigma0 < 1e-12:
        print("ERROR: initial perturbation is effectively zero.", file=sys.stderr)
        return 2

    c2 = args.c_wave ** 2
    dt = args.dt

    # ── Initial energy ────────────────────────────────────────────────────────
    # At t=0, kinetic = 0 (start from rest), energy = potential only
    e0 = discrete_energy(u_cur, u_prev, neighbours, c2, dt)
    if e0 < 1e-30:
        print("ERROR: initial energy is zero — check parameters.", file=sys.stderr)
        return 2

    # ── Leapfrog evolution ────────────────────────────────────────────────────
    energy_rows: list[dict[str, str]] = []
    energy_vals: list[float] = []       # E(t)/E(0)
    spread_vals: list[float] = []       # σ(t)/σ(0)
    spread_abs_vals: list[float] = []   # σ(t) absolute, for dynamism
    time_vals: list[float] = []
    max_u_all_time: float = max_u0      # track amplitude stability (G5a)

    for step in range(args.n_steps):
        # Graph Laplacian applied to current u
        Lu = apply_laplacian(u_cur, neighbours)

        # Leapfrog step
        u_next = [
            2.0 * u_cur[i] - u_prev[i] + c2 * dt * dt * Lu[i]
            for i in range(n)
        ]

        # Track max amplitude for G5a stability gate
        step_max_u = max(abs(v) for v in u_next)
        if step_max_u > max_u_all_time:
            max_u_all_time = step_max_u

        # Record diagnostics every RECORD_EVERY steps
        if step % RECORD_EVERY == 0 or step == args.n_steps - 1:
            t_now = step * dt
            e_now = discrete_energy(u_cur, u_prev, neighbours, c2, dt)
            e_rel = e_now / e0
            sig_now = rms_spread(u_cur, coords, centre_xy)
            sig_rel = sig_now / sigma0 if sigma0 > 1e-12 else float("nan")

            energy_rows.append({
                "step": str(step),
                "time": fmt(t_now),
                "energy": fmt(e_now),
                "energy_rel": fmt(e_rel),
                "sigma": fmt(sig_now),
                "sigma_rel": fmt(sig_rel),
                "u_centre": fmt(u_cur[centre_idx]),
            })
            energy_vals.append(e_rel)
            spread_vals.append(sig_rel)
            spread_abs_vals.append(sig_now)
            time_vals.append(t_now)

        # Advance
        u_prev = u_cur
        u_cur = u_next

    # Final diagnostics
    t_final = args.n_steps * dt
    e_final = discrete_energy(u_cur, u_prev, neighbours, c2, dt)
    e_final_rel = e_final / e0
    sigma_final = rms_spread(u_cur, coords, centre_xy)
    sigma_final_rel = sigma_final / sigma0 if sigma0 > 1e-12 else float("nan")
    u_centre_final = u_cur[centre_idx]
    u_centre_rel = abs(u_centre_final) / max(max_u0, 1e-30)

    # ── Gate evaluation ───────────────────────────────────────────────────────
    # G5a: stability (no amplitude blow-up)
    stability_ratio = max_u_all_time / max(max_u0, 1e-30)
    gate_g5a = math.isfinite(stability_ratio) and stability_ratio <= thresholds.g5a_stability_max

    # G5b: spread increase
    gate_g5b = math.isfinite(sigma_final_rel) and sigma_final_rel > thresholds.g5b_spread_ratio_min

    # G5c: dynamism (spread is evolving, not frozen)
    sigma_max_t = max(spread_abs_vals) if spread_abs_vals else sigma_final
    sigma_min_t = min(spread_abs_vals) if spread_abs_vals else sigma0
    dynamism_ratio = sigma_max_t / sigma_min_t if sigma_min_t > 1e-12 else float("nan")
    gate_g5c = math.isfinite(dynamism_ratio) and dynamism_ratio > thresholds.g5c_dynamism_min

    # G5d: dispersion — eigenmode frequency test
    #   1. Find λ_d (most-negative eigenvalue) and eigenvector v_d via power iteration.
    #   2. Excite a sub-simulation starting from v_d (scaled to AMP_INIT amplitude).
    #   3. Count zero-crossings of u[node_d](t) to measure ω_meas.
    #   4. Predicted: ω_pred = c · √|λ_d|.  Gate: |ω_meas/ω_pred − 1| < 0.25.
    lambda_d, v_d = power_iteration_min_eigenvalue(neighbours, seed=args.seed)
    # node with largest |v_d| → strongest signal, easiest to count crossings
    node_d = max(range(n), key=lambda i: abs(v_d[i]))
    omega_pred = args.c_wave * math.sqrt(abs(lambda_d)) if lambda_d < 0 else 0.0

    # Sub-simulation IC: u_i = AMP_INIT * v_d[i]  (max already normalised to 1)
    ud_cur = [AMP_INIT * v_d[i] for i in range(n)]
    ud_prev = ud_cur[:]   # zero initial velocity

    eigenmode_rows: list[dict[str, str]] = []
    eigenmode_traj: list[float] = []   # u[node_d](t)
    eigenmode_times: list[float] = []

    for step_d in range(N_STEPS_G5D):
        Lu_d = apply_laplacian(ud_cur, neighbours)
        ud_next = [
            2.0 * ud_cur[i] - ud_prev[i] + c2 * dt * dt * Lu_d[i]
            for i in range(n)
        ]
        if step_d % RECORD_EVERY == 0 or step_d == N_STEPS_G5D - 1:
            t_d = step_d * dt
            eigenmode_rows.append({
                "step": str(step_d),
                "time": fmt(t_d),
                "u_node": fmt(ud_cur[node_d]),
            })
            eigenmode_traj.append(ud_cur[node_d])
            eigenmode_times.append(t_d)
        ud_prev = ud_cur
        ud_cur = ud_next

    # Count zero-crossings in the recorded trajectory
    n_crossings = sum(
        1 for k in range(1, len(eigenmode_traj))
        if eigenmode_traj[k - 1] * eigenmode_traj[k] < 0.0
    )
    # Also count crossings in the un-subsampled loop would be more accurate, but
    # with RECORD_EVERY=4 we sample every 4 steps (dt_rec=1.6 time units).
    # Period ≈ 2π/ω_pred ≈ 31 time units → ~19 samples/period → no aliasing.
    t_g5d = N_STEPS_G5D * dt
    omega_meas = math.pi * n_crossings / t_g5d if t_g5d > 0 else 0.0
    freq_rel = omega_meas / omega_pred if omega_pred > 1e-12 else float("nan")
    gate_g5d = (
        math.isfinite(freq_rel)
        and abs(freq_rel - 1.0) < thresholds.g5d_freq_rel_tol
        and n_crossings >= thresholds.g5d_min_crossings
    )

    gate_g5 = gate_g5a and gate_g5b and gate_g5c and gate_g5d
    decision = "pass" if gate_g5 else "fail"

    # ── Write outputs ─────────────────────────────────────────────────────────
    write_csv(
        out_dir / "wave_energy.csv",
        ["step", "time", "energy", "energy_rel", "sigma", "sigma_rel", "u_centre"],
        energy_rows,
    )

    metric_rows = [
        {"gate_id": "G5a", "metric": "stability_ratio",
         "value": fmt(stability_ratio),
         "threshold": f"<={thresholds.g5a_stability_max}",
         "status": "pass" if gate_g5a else "fail"},
        {"gate_id": "G5b", "metric": "sigma_ratio_final",
         "value": fmt(sigma_final_rel),
         "threshold": f">{thresholds.g5b_spread_ratio_min}",
         "status": "pass" if gate_g5b else "fail"},
        {"gate_id": "G5c", "metric": "sigma_dynamism_ratio",
         "value": fmt(dynamism_ratio),
         "threshold": f">{thresholds.g5c_dynamism_min}",
         "status": "pass" if gate_g5c else "fail"},
        {"gate_id": "G5d", "metric": "freq_ratio",
         "value": fmt(freq_rel),
         "threshold": f"|omega_meas/omega_pred-1|<{thresholds.g5d_freq_rel_tol} & crossings>={thresholds.g5d_min_crossings}",
         "status": "pass" if gate_g5d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision,
         "threshold": "G5a&G5b&G5c&G5d",
         "status": decision},
    ]
    write_csv(out_dir / "metric_checks_wave.csv",
              ["gate_id", "metric", "value", "threshold", "status"], metric_rows)

    # G5d: eigenmode time-series CSV
    write_csv(out_dir / "wave_eigenmode.csv",
              ["step", "time", "u_node"], eigenmode_rows)

    # Time-series plots
    plot_timeseries(out_dir / "wave_energy-plot.png", time_vals, energy_vals,
                    color=(40, 112, 184), hline=1.0, hline_color=(200, 60, 60))
    plot_timeseries(out_dir / "wave_spread-plot.png", time_vals, spread_vals,
                    color=(30, 150, 90), hline=thresholds.g5b_spread_ratio_min,
                    hline_color=(200, 60, 60))

    # G5d: eigenmode oscillation plot (u vs t, with ±AMP reference lines)
    plot_timeseries(out_dir / "wave_eigenmode-plot.png", eigenmode_times, eigenmode_traj,
                    color=(140, 40, 180), hline=0.0, hline_color=(120, 120, 120))

    # Config and hashes
    config = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "centre_idx": centre_idx,
        "centre_xy": list(centre_xy),
        "c_wave": args.c_wave,
        "dt": args.dt,
        "cfl": cfl,
        "n_steps": args.n_steps,
        "t_final": t_final,
        "sigma_init": args.sigma_init,
        "amp_init": AMP_INIT,
        "laplacian": "degree-normalised random-walk",
        "scheme": "leapfrog",
        "thresholds": {
            "g5a_stability_max": thresholds.g5a_stability_max,
            "g5b_spread_ratio_min": thresholds.g5b_spread_ratio_min,
            "g5c_dynamism_min": thresholds.g5c_dynamism_min,
            "g5d_freq_rel_tol": thresholds.g5d_freq_rel_tol,
            "g5d_min_crossings": thresholds.g5d_min_crossings,
            "n_steps_g5d": N_STEPS_G5D,
        },
        "results": {
            "E0": e0,
            "E_final": e_final,
            "E_final_rel": e_final_rel,
            "stability_ratio": stability_ratio,
            "sigma0": sigma0,
            "sigma_final": sigma_final,
            "sigma_final_rel": sigma_final_rel,
            "dynamism_ratio": dynamism_ratio,
            "u_centre_rel": u_centre_rel,
            "lambda_d": lambda_d,
            "omega_pred": omega_pred,
            "omega_meas": omega_meas,
            "freq_rel": freq_rel if math.isfinite(freq_rel) else None,
            "n_crossings": n_crossings,
            "decision": decision,
        },
    }
    (out_dir / "config_wave.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    files_for_hash = [
        out_dir / "wave_energy.csv",
        out_dir / "wave_eigenmode.csv",
        out_dir / "metric_checks_wave.csv",
        out_dir / "config_wave.json",
    ]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes-wave.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")

    duration = time.perf_counter() - started

    log_lines = [
        "QNG dynamics wave v1 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}",
        f"n_nodes: {n}",
        f"centre_idx: {centre_idx}  sigma_centre={sigma[centre_idx]:.4f}",
        f"c_wave: {args.c_wave}  dt: {args.dt}  n_steps: {args.n_steps}",
        f"cfl: {cfl:.4f}  (limit: sqrt(2)={math.sqrt(2):.4f})",
        f"sigma_init: {args.sigma_init}  amp_init: {AMP_INIT}",
        f"duration_seconds: {duration:.3f}",
        f"decision: {decision}",
        "",
        f"E0={e0:.4e}  E_final={e_final:.4e}  E_final_rel={e_final_rel:.6f}",
        f"stability_ratio={stability_ratio:.6f}  (G5a threshold <={thresholds.g5a_stability_max})",
        f"sigma0={sigma0:.4f}  sigma_final={sigma_final:.4f}  ratio={sigma_final_rel:.4f}",
        f"  (G5b threshold >{thresholds.g5b_spread_ratio_min})",
        f"dynamism_ratio={dynamism_ratio:.6f}  (G5c threshold >{thresholds.g5c_dynamism_min})",
        f"u_centre_rel={u_centre_rel:.4f}  (informational)",
        f"lambda_d={lambda_d:.6f}  omega_pred={omega_pred:.6f}  omega_meas={omega_meas:.6f}",
        f"  freq_rel={fmt(freq_rel)}  n_crossings={n_crossings}"
        f"  (G5d threshold |freq_rel-1|<{thresholds.g5d_freq_rel_tol} & crossings>={thresholds.g5d_min_crossings})",
        "",
    ]
    if warnings:
        log_lines.append("warnings:")
        log_lines.extend(f"- {w}" for w in warnings)
    (out_dir / "run-log-wave.txt").write_text("\n".join(log_lines), encoding="utf-8")

    # ── Print summary ─────────────────────────────────────────────────────────
    print("QNG dynamics wave v1 completed.")
    print(f"Artifacts: {out_dir}")
    print(
        f"decision={decision}  G5={gate_g5}(a={gate_g5a},b={gate_g5b},c={gate_g5c},d={gate_g5d})"
    )
    print(
        f"G5a (stability): max_u/max_u0={fmt(stability_ratio)} threshold=<={thresholds.g5a_stability_max}"
    )
    print(
        f"G5b (spread):  σ_final/σ_0={fmt(sigma_final_rel)} threshold=>{thresholds.g5b_spread_ratio_min}"
    )
    print(
        f"G5c (dynamism): max_σ/min_σ={fmt(dynamism_ratio)} threshold=>{thresholds.g5c_dynamism_min}"
    )
    print(
        f"G5d (dispersion): λ_d={lambda_d:.4f}  ω_pred={omega_pred:.4f}"
        f"  ω_meas={omega_meas:.4f}  freq_rel={fmt(freq_rel)}"
        f"  crossings={n_crossings}  threshold=|·-1|<{thresholds.g5d_freq_rel_tol}"
    )
    print(
        f"E0={fmt(e0)}  E_final={fmt(e_final)}  (T={t_final:.1f}  c={args.c_wave}  dt={args.dt}  steps={args.n_steps})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
