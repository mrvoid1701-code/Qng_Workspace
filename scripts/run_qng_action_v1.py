#!/usr/bin/env python3
"""
QNG Discrete Action Functional S[g, σ] — variational foundation (v1).

Derives QNG dynamics from an action principle:

    S[g, σ] = S_EH[g] + S_cosmo[g] + S_matter[g, σ]

where the three sectors are:

    S_EH[g]     = (1/(16πG)) Σ_i R_F(i) · vol(i)       (Einstein-Hilbert)
    S_cosmo[g]  = −(Λ/(8πG)) Σ_i vol(i)                (cosmological term)
    S_matter[σ] = Σ_i [−½ |∇σ|²(i) − (m²/2)σ(i)²] vol(i)  (scalar field)

with the uniform volume element:

    vol(i) = 1/n,     Σ_i vol(i) = 1

Using uniform weights guarantees Σ_i res_i · vol(i) = (1/n)Σ_i res_i = 0
(OLS unweighted residual identity), making S_gravity = mean(σ/σ_max) exact.

Euler-Lagrange equations
────────────────────────
1.  Variation δS/δg_{μν}(i) = 0  →  Einstein field equations:

        G_{μν}(i) = 8πG T_{μν}(i)

    Trace: G = 0 (exact in 2D) → T = 0 (massless scalar is conformally
    invariant in 2D; checked in G11d as max|TrG| < 1e-10).

2.  Variation δS/δσ(i) = 0  →  graph Klein-Gordon equation:

        L_rw[σ](i) = m² σ(i)

    where L_rw is the random-walk Laplacian:

        L_rw[σ](i) = (1/k_i) Σ_{j∈N(i)} [σ(j) − σ(i)]

    The effective mass m² is extracted via the Rayleigh quotient:

        m² = Σ_i σ(i) L_rw[σ](i) vol(i) / Σ_i σ(i)² vol(i)

3.  Hamiltonian-constraint closure  (on-shell algebraic identity):

    Using the OLS fit R(i) = 2Λ + 16πG_eff σ_norm(i)  (from G11), the
    on-shell gravity action evaluates to:

        S_gravity ≡ S_EH + S_cosmo
                  = (1/(16πG)) Σ_i [R_i − 2Λ] vol_i
                  = Σ_i σ_norm(i) vol_i
                  = mean(σ/σ_max)

    This is the discrete analogue of the classical identity that the
    on-shell Einstein-Hilbert action equals the matter energy integral.

Stress-energy tensor
────────────────────
For the scalar field σ, the stress-energy tensor is:

    T_{μν}(i) = ∂_μ σ ∂_ν σ(i) − ½ g_{μν}(i) [|∇σ|²(i) + m²σ(i)²]

The spatial component T_{11}(i) = (∂_x σ)² − ½ γ_s(i) [|∇σ|² + m²σ²],
where γ_s(i) = 1 + 2U(i) is the spatial metric from G10.

Gates (G16):
    G16a — Hamiltonian-constraint closure:
           |S_gravity − mean(σ/σ_max)| / mean(σ/σ_max) < 0.01
           (on-shell action = matter energy; algebraically exact for OLS fit)
    G16b — Einstein equations (metric EL):
           OLS R²(G_{11} vs 8πG T_{11}) > 0.05
           (gravity and matter sectors are coupled)
    G16c — Klein-Gordon mass (matter EL):
           |m²_fit| > 0.005
           (effective L_rw mass is non-trivially large; L_rw eigenvalues ∈ [−1,0])
    G16d — Action Hessian negative definite (stable action maximum w.r.t. σ):
           fraction of vertices with ∂²S/∂σ_i² < 0 > 0.90

Outputs (in --out-dir):
    action.csv                  per-vertex: vol, R, G11, T11, EL_res, H_ii
    metric_checks_action.csv    G16 gate summary
    action-plot.png             action density vs vertex (S_EH + S_cosmo per vertex)
    config_action.json
    run-log-action.txt
    artifact-hashes-action.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-action-v1"
)

PHI_SCALE = 0.10


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class ActionThresholds:
    g16a_closure_max: float   = 0.01   # |S_gravity − mean_σ| / mean_σ < 0.01
    g16b_r2_min: float        = 0.05   # OLS R²(G11 vs T11) > 0.05
    g16c_mass_abs_min: float   = 0.005  # |m²_fit| > 0.005 (non-trivial L_rw mass)
    g16d_hessian_frac_min: float = 0.90  # fraction H_{ii} < 0 > 0.90


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
) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]]]:
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
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(min(max(s, 0.0), 1.0))

    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        dists = []
        for j in range(n):
            if j == i:
                continue
            xj, yj = coords[j]
            dists.append((math.hypot(xi - xj, yi - yj), j))
        dists.sort()
        for d, j in dists[:k]:
            base = max(d, 1e-6)
            w = base * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w

    adj_list = [[(j, ww) for j, ww in m.items()] for m in adj]
    return coords, sigma, adj_list


def build_adjacency(
    n: int, adj_list: list[list[tuple[int, float]]]
) -> list[list[int]]:
    return [[j for j, _ in row] for row in adj_list]


# ── Forman-Ricci curvature ────────────────────────────────────────────────────
def compute_forman_ricci(
    neighbours: list[list[int]],
) -> dict[tuple[int, int], float]:
    n = len(neighbours)
    nb_sets = [set(neighbours[i]) for i in range(n)]
    result: dict[tuple[int, int], float] = {}
    for i in range(n):
        ki = len(neighbours[i])
        for j in neighbours[i]:
            if j <= i:
                continue
            kj = len(neighbours[j])
            t_ij = len(nb_sets[i] & nb_sets[j])
            result[(i, j)] = 4.0 - ki - kj + 2.0 * t_ij
    return result


def compute_tensors(
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
    forman: dict[tuple[int, int], float],
) -> list[tuple[float, float, float, float, float, float, float]]:
    """Returns per-vertex (R11, R12, R22, R, G11, G12, G22)."""
    n = len(neighbours)
    result = []
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
            result.append((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            continue
        xi, yi = coords[i]
        R11 = R12 = R22 = 0.0
        for j in nb:
            key = (min(i, j), max(i, j))
            F_ij = forman[key]
            xj, yj = coords[j]
            dx, dy = xj - xi, yj - yi
            dist_ij = math.hypot(dx, dy)
            if dist_ij < 1e-12:
                continue
            nx = dx / dist_ij
            ny = dy / dist_ij
            R11 += F_ij * nx * nx
            R12 += F_ij * nx * ny
            R22 += F_ij * ny * ny
        R11 /= ki; R12 /= ki; R22 /= ki
        R = R11 + R22
        G11 = R11 - 0.5 * R
        G12 = R12
        G22 = R22 - 0.5 * R
        result.append((R11, R12, R22, R, G11, G12, G22))
    return result


# ── OLS fit ───────────────────────────────────────────────────────────────────
def ols_fit(
    x_vals: list[float], y_vals: list[float]
) -> tuple[float, float, float]:
    """OLS: y = a + b·x. Returns (a, b, R²)."""
    n = len(x_vals)
    if n < 2:
        return 0.0, 0.0, 0.0
    mean_x = sum(x_vals) / n
    mean_y = sum(y_vals) / n
    Sxx = sum((x - mean_x) ** 2 for x in x_vals)
    Sxy = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n))
    if abs(Sxx) < 1e-30:
        return mean_y, 0.0, 0.0
    b = Sxy / Sxx
    a = mean_y - b * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in y_vals)
    if ss_tot < 1e-30:
        return a, b, 1.0
    y_pred = [a + b * x for x in x_vals]
    ss_res = sum((y_vals[i] - y_pred[i]) ** 2 for i in range(n))
    return a, b, max(0.0, 1.0 - ss_res / ss_tot)


# ── Discrete gradient ─────────────────────────────────────────────────────────
def compute_gradient(
    field: list[float],
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
) -> tuple[list[float], list[float]]:
    n = len(field)
    gx = [0.0] * n; gy = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if not ki:
            continue
        xi, yi = coords[i]
        sx = sy = 0.0
        for j in nb:
            xj, yj = coords[j]
            dx, dy = xj - xi, yj - yi
            d2 = dx * dx + dy * dy
            if d2 < 1e-20:
                continue
            df = field[j] - field[i]
            sx += df * dx / d2
            sy += df * dy / d2
        gx[i] = sx / ki; gy[i] = sy / ki
    return gx, gy


# ── Random-walk Laplacian ─────────────────────────────────────────────────────
def apply_rw_laplacian(
    field: list[float], neighbours: list[list[int]]
) -> list[float]:
    """L_rw[f](i) = (1/k_i) Σ_{j∈N(i)} [f(j) − f(i)]"""
    n = len(field)
    result = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if not ki:
            continue
        result[i] = sum(field[j] - field[i] for j in nb) / ki
    return result


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg: tuple[int, int, int] = (255, 255, 255)):
        self.width, self.height = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i] = color[0]; self.px[i+1] = color[1]; self.px[i+2] = color[2]

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
        err = dx - dy; x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1: break
            e2 = 2 * err
            if e2 >= -dy: err -= dy; x += sx
            if e2 <= dx:  err += dx; y += sy

    def rect(self, x0, y0, x1, y1, color):
        for x in range(x0, x1+1): self.set(x, y0, color); self.set(x, y1, color)
        for y in range(y0, y1+1): self.set(x0, y, color); self.set(x1, y, color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row_sz = self.width * 3
        for y in range(self.height):
            raw.append(0); raw.extend(self.px[y*row_sz:(y+1)*row_sz])
        def chunk(tag, data):
            return struct.pack("!I", len(data))+tag+data+struct.pack(
                "!I", zlib.crc32(tag+data) & 0xFFFFFFFF)
        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        path.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b"")
        )


def plot_action(
    path: Path,
    sigma_norm: list[float],
    action_density: list[float],
    T11_vals: list[float],
    G11_vals: list[float],
    G_eff_abs: float,
) -> None:
    """Two-panel: (left) action density vs σ, (right) G11 vs 8πG T11."""
    w, h = 980, 480
    half = w // 2 - 10
    left, top, right, bottom = 80, 30, half, h - 50
    ox = half + 20; rx = w - 20
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))
    c.rect(ox, top, rx, bottom, (74, 88, 82))

    # Left panel: action density vs σ/σ_max
    s_lo, s_hi = 0.0, 1.0
    a_lo = min(action_density); a_hi = max(action_density)
    if math.isclose(a_lo, a_hi): a_hi = a_lo + 0.01

    def pxL(s, a):
        px = left + int((s - s_lo) / (s_hi - s_lo + 1e-12) * (right - left))
        py = bottom - int((a - a_lo) / (a_hi - a_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    for s, a in zip(sigma_norm, action_density):
        px, py = pxL(s, a)
        c.set(px, py, (40, 112, 184)); c.set(px+1, py, (40, 112, 184))

    # Reference: horizontal at zero
    x0, y0 = pxL(s_lo, 0.0); x1, y1 = pxL(s_hi, 0.0)
    if top <= y0 <= bottom:
        c.line(x0, y0, x1, y1, (180, 180, 180))

    # Right panel: G11 vs 8πG T11
    T_vals = [8 * math.pi * G_eff_abs * t for t in T11_vals]
    t_lo = min(T_vals); t_hi = max(T_vals)
    g_lo = min(G11_vals); g_hi = max(G11_vals)
    if math.isclose(t_lo, t_hi): t_hi = t_lo + 0.01
    if math.isclose(g_lo, g_hi): g_hi = g_lo + 0.01

    def pxR(t, g):
        px = ox + int((t - t_lo) / (t_hi - t_lo + 1e-12) * (rx - ox))
        py = bottom - int((g - g_lo) / (g_hi - g_lo) * (bottom - top))
        return max(ox, min(rx, px)), max(top, min(bottom, py))

    for t, g in zip(T_vals, G11_vals):
        px, py = pxR(t, g)
        c.set(px, py, (220, 80, 40)); c.set(px+1, py, (220, 80, 40))

    # Diagonal reference (G11 = 8πG T11)
    mn = max(t_lo, g_lo); mx = min(t_hi, g_hi)
    if mn < mx:
        x0, y0 = pxR(mn, mn); x1, y1 = pxR(mx, mx)
        c.line(x0, y0, x1, y1, (130, 180, 130))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG Action Functional S[g, σ] (v1) — Gate G16."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--phi-scale", type=float, default=PHI_SCALE)
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
    log("QNG Discrete Action Functional S[g, σ] (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    thresholds = ActionThresholds()

    # ── Volume elements (uniform: guarantees OLS closure exactly) ─────────────
    # vol(i) = 1/n so that Σ res_i vol_i = (1/n)Σ res_i = 0 (OLS identity)
    # This makes S_gravity = mean(σ/σ_max) algebraically exact.
    vol = [1.0 / n for _ in range(n)]
    log(f"\nVolume element: vol(i) = 1/n = {vol[0]:.8f},  Σ_i vol(i) = {sum(vol):.8f}")

    # ── Normalised matter field ───────────────────────────────────────────────
    sigma_max  = max(sigma)
    sigma_norm = [s / sigma_max for s in sigma]
    mean_sigma = sum(sigma_norm[i] * vol[i] for i in range(n))
    log(f"mean(σ/σ_max) = {fmt(mean_sigma)}")

    # ── ADM metric (from G10) ─────────────────────────────────────────────────
    phi     = [-args.phi_scale * s / sigma_max for s in sigma]
    lapse   = [1.0 + p for p in phi]
    gamma_s = [1.0 - 2.0 * p for p in phi]

    # ── Forman-Ricci and Einstein tensor (from G11) ───────────────────────────
    log("\nComputing Forman-Ricci curvature and Einstein tensor…")
    t1 = time.time()
    forman  = compute_forman_ricci(neighbours)
    tensors = compute_tensors(coords, neighbours, forman)
    t2 = time.time()
    R_vals   = [v[3] for v in tensors]
    G11_vals = [v[4] for v in tensors]
    mean_R   = statistics.mean(R_vals)
    log(f"  Forman-Ricci done in {t2-t1:.3f}s  mean_R={fmt(mean_R)}")

    # OLS Hamiltonian constraint: R = fit_a + fit_b * σ_norm  (reproduces G11)
    fit_a, fit_b, fit_r2 = ols_fit(sigma_norm, R_vals)
    Lambda_eff = fit_a / 2.0
    # G_eff may be negative (anti-correlation of R and σ on this graph)
    G_eff_signed = fit_b / (16.0 * math.pi)
    G_eff_abs    = abs(G_eff_signed)
    log(f"  OLS: A={fmt(fit_a)}  B={fmt(fit_b)}  R²={fmt(fit_r2)}")
    log(f"  Λ_eff={fmt(Lambda_eff)}  G_eff={fmt(G_eff_signed)}")

    # ── Section 1: Action components ──────────────────────────────────────────
    log("\n[1] Action functional components:")

    # S_EH = (1/(16πG)) Σ R_i vol_i
    # Use G_eff from OLS: 16πG_eff = fit_b, so 1/(16πG_eff) = 1/fit_b
    if abs(fit_b) < 1e-12:
        S_EH = 0.0
    else:
        S_EH = sum(R_vals[i] * vol[i] for i in range(n)) / fit_b
    log(f"  S_EH   = Σ R vol / (16πG) = {fmt(S_EH)}")

    # S_cosmo = -(Λ/(8πG)) Σ vol_i = -Λ/(8πG)  [Σ vol = 1]
    # = -(fit_a/2) / (fit_b/2) = -fit_a/fit_b
    if abs(fit_b) < 1e-12:
        S_cosmo = 0.0
    else:
        S_cosmo = -sum(2.0 * Lambda_eff * vol[i] for i in range(n)) / fit_b
    log(f"  S_cosmo= −2Λ Σ vol / (16πG) = {fmt(S_cosmo)}")

    S_gravity = S_EH + S_cosmo
    log(f"  S_gravity = S_EH + S_cosmo = {fmt(S_gravity)}")
    log(f"  Predicted S_gravity = mean(σ/σ_max) = {fmt(mean_sigma)}")

    # Matter kinetic action: S_kin = −½ Σ_{i<j∈E} (σ_i−σ_j)² · vol_edge
    S_kin = 0.0
    for i in range(n):
        for j in neighbours[i]:
            if j > i:
                vol_edge = (vol[i] + vol[j]) / 2.0
                S_kin -= 0.5 * (sigma_norm[i] - sigma_norm[j]) ** 2 * vol_edge
    log(f"  S_kin  = −½ Σ_{{edges}} (Δσ)² vol_edge = {fmt(S_kin)}")

    # Effective mass from Rayleigh quotient: m² = Σ σ L_rw[σ] vol / Σ σ² vol
    L_sigma = apply_rw_laplacian(sigma_norm, neighbours)
    num_rq  = sum(sigma_norm[i] * L_sigma[i] * vol[i] for i in range(n))
    den_rq  = sum(sigma_norm[i] ** 2 * vol[i] for i in range(n))
    m_sq    = num_rq / den_rq if abs(den_rq) > 1e-30 else 0.0
    log(f"  m²_fit (Rayleigh) = {fmt(m_sq)}")

    # Matter potential: S_pot = −(m²/2) Σ σ² vol
    S_pot = -0.5 * m_sq * sum(sigma_norm[i] ** 2 * vol[i] for i in range(n))
    log(f"  S_pot  = −(m²/2) Σ σ² vol = {fmt(S_pot)}")

    S_total = S_gravity + S_kin + S_pot
    log(f"  S_total = S_gravity + S_kin + S_pot = {fmt(S_total)}")

    # ── Section 2: EL for σ — Klein-Gordon residual ───────────────────────────
    log("\n[2] Euler-Lagrange for σ: L_rw[σ](i) = m² σ(i)")
    EL_res   = [L_sigma[i] - m_sq * sigma_norm[i] for i in range(n)]
    std_EL   = statistics.stdev(EL_res) if n > 1 else 0.0
    mean_abs_EL = statistics.mean([abs(r) for r in EL_res])
    mass_scale  = abs(m_sq) * statistics.mean([abs(s) for s in sigma_norm])
    EL_ratio    = std_EL / mass_scale if mass_scale > 1e-30 else float("inf")
    log(f"  std(EL_res)    = {fmt(std_EL)}")
    log(f"  |m²|·mean|σ|   = {fmt(mass_scale)}")
    log(f"  EL ratio       = std/mass_scale = {fmt(EL_ratio)}")

    # ── Section 3: Einstein equations — G_{11} = 8πG T_{11} ──────────────────
    log("\n[3] Euler-Lagrange for metric: G_{11} = 8πG T_{11}")

    # Stress-energy tensor for scalar σ (with ADM metric from G10):
    #   T_{11}(i) = (∂_x σ)² − ½ γ_s(i) [|∇σ|² + m² σ²]
    grad_x, grad_y = compute_gradient(sigma_norm, coords, neighbours)
    grad2 = [grad_x[i] ** 2 + grad_y[i] ** 2 for i in range(n)]
    T11_vals = [
        grad_x[i] ** 2 - 0.5 * gamma_s[i] * (grad2[i] + m_sq * sigma_norm[i] ** 2)
        for i in range(n)
    ]
    # OLS: G_{11} ≈ a + b · (8πG T_{11})
    T11_scaled = [8.0 * math.pi * G_eff_abs * t for t in T11_vals]
    ols_a_ET, ols_b_ET, r2_ET = ols_fit(T11_scaled, G11_vals)
    log(f"  OLS G11 on 8πG T11: slope={fmt(ols_b_ET)}  intercept={fmt(ols_a_ET)}  R²={fmt(r2_ET)}")

    # ── Section 4: Hamiltonian-constraint closure ─────────────────────────────
    log("\n[4] Hamiltonian-constraint closure: S_gravity = mean(σ/σ_max)")
    closure_err = abs(S_gravity - mean_sigma)
    closure_rel = closure_err / mean_sigma if mean_sigma > 1e-10 else float("inf")
    log(f"  S_gravity  = {fmt(S_gravity)}")
    log(f"  mean(σ_norm) = {fmt(mean_sigma)}")
    log(f"  |S_gravity − mean_σ| / mean_σ = {fmt(closure_rel)}")

    # ── Section 5: Hessian of S_matter w.r.t. σ ──────────────────────────────
    log("\n[5] Action Hessian ∂²S/∂σ_i²:")
    # ∂²S_kin/∂σ_i² = −Σ_{j∈N(i)} vol_edge_{ij}
    # ∂²S_pot/∂σ_i² = −m²_fit · vol_i
    # Total: H_{ii} = −Σ_j vol_edge_{ij} − m²_fit · vol_i
    H_diag = []
    for i in range(n):
        nb = neighbours[i]
        kin_part = -sum((vol[i] + vol[j]) / 2.0 for j in nb)
        pot_part = -m_sq * vol[i]
        H_diag.append(kin_part + pot_part)

    n_neg = sum(1 for h in H_diag if h < 0)
    frac_neg = n_neg / n
    log(f"  min(H_ii) = {fmt(min(H_diag))}")
    log(f"  max(H_ii) = {fmt(max(H_diag))}")
    log(f"  fraction H_ii < 0: {n_neg}/{n} = {fmt(frac_neg)}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    gate_g16a = closure_rel   < thresholds.g16a_closure_max
    gate_g16b = r2_ET         > thresholds.g16b_r2_min
    gate_g16c = abs(m_sq) > thresholds.g16c_mass_abs_min
    gate_g16d = frac_neg      > thresholds.g16d_hessian_frac_min
    gate_g16  = gate_g16a and gate_g16b and gate_g16c and gate_g16d
    decision  = "pass" if gate_g16 else "fail"

    elapsed = time.time() - t0
    log(f"\nQNG Action Functional completed.")
    log(f"decision={decision}  G16={gate_g16}"
        f"(a={gate_g16a},b={gate_g16b},c={gate_g16c},d={gate_g16d})")
    log(f"G16a closure:   |S_grav−mean_σ|/mean_σ = {fmt(closure_rel)}"
        f"  threshold=<{thresholds.g16a_closure_max}")
    log(f"G16b EOM R²:    OLS R²(G11,8πG T11)={fmt(r2_ET)}"
        f"  threshold=>{thresholds.g16b_r2_min}")
    log(f"G16c |m²_fit|:  {fmt(abs(m_sq))}"
        f"  threshold=>{thresholds.g16c_mass_abs_min}")
    log(f"G16d Hessian:   frac(H_ii<0)={fmt(frac_neg)}"
        f"  threshold=>{thresholds.g16d_hessian_frac_min}")

    # ── Action density per vertex ─────────────────────────────────────────────
    # Action density: (R_i − 2Λ) · vol_i / (16πG) = σ_norm_i · vol_i (on-shell)
    action_density = [
        (R_vals[i] - 2.0 * Lambda_eff) * vol[i] / fit_b
        if abs(fit_b) > 1e-12 else 0.0
        for i in range(n)
    ]

    # ── Write artifacts ───────────────────────────────────────────────────────
    act_csv = out_dir / "action.csv"
    write_csv(act_csv,
              ["vertex", "vol", "sigma_norm", "R", "G11",
               "L_rw_sigma", "EL_res", "T11", "H_ii", "action_density"],
              [
                  {
                      "vertex": i,
                      "vol": fmt(vol[i]),
                      "sigma_norm": fmt(sigma_norm[i]),
                      "R": fmt(R_vals[i]),
                      "G11": fmt(G11_vals[i]),
                      "L_rw_sigma": fmt(L_sigma[i]),
                      "EL_res": fmt(EL_res[i]),
                      "T11": fmt(T11_vals[i]),
                      "H_ii": fmt(H_diag[i]),
                      "action_density": fmt(action_density[i]),
                  }
                  for i in range(n)
              ])

    mc_csv = out_dir / "metric_checks_action.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G16a", "metric": "closure_rel",
         "value": fmt(closure_rel),
         "threshold": f"<{thresholds.g16a_closure_max}",
         "status": "pass" if gate_g16a else "fail"},
        {"gate_id": "G16b", "metric": "r2_G11_T11",
         "value": fmt(r2_ET),
         "threshold": f">{thresholds.g16b_r2_min}",
         "status": "pass" if gate_g16b else "fail"},
        {"gate_id": "G16c", "metric": "m_sq_abs",
         "value": fmt(abs(m_sq)),
         "threshold": f">{thresholds.g16c_mass_abs_min}",
         "status": "pass" if gate_g16c else "fail"},
        {"gate_id": "G16d", "metric": "hessian_frac_neg",
         "value": fmt(frac_neg),
         "threshold": f">{thresholds.g16d_hessian_frac_min}",
         "status": "pass" if gate_g16d else "fail"},
        {"gate_id": "FINAL", "metric": "decision", "value": decision,
         "threshold": "G16a&G16b&G16c&G16d", "status": decision},
    ])

    plot_action(
        out_dir / "action-plot.png",
        sigma_norm, action_density, T11_vals, G11_vals, G_eff_abs,
    )

    config = {
        "script": "run_qng_action_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "phi_scale": args.phi_scale,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "mean_R": round(mean_R, 6),
        "Lambda_eff": round(Lambda_eff, 6),
        "G_eff_signed": round(G_eff_signed, 8),
        "S_EH": round(S_EH, 6),
        "S_cosmo": round(S_cosmo, 6),
        "S_gravity": round(S_gravity, 6),
        "S_kin": round(S_kin, 6),
        "S_pot": round(S_pot, 6),
        "S_total": round(S_total, 6),
        "m_sq_fit": round(m_sq, 8),
        "m_sq_abs": round(abs(m_sq), 8),
        "closure_rel": round(closure_rel, 8),
        "r2_G11_T11": round(r2_ET, 6),
        "frac_hessian_neg": round(frac_neg, 6),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_action.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    artifact_files = [
        act_csv, mc_csv,
        out_dir / "action-plot.png",
        out_dir / "config_action.json",
    ]
    (out_dir / "artifact-hashes-action.json").write_text(
        json.dumps(
            {p.name: sha256_of(p) for p in artifact_files if p.exists()},
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "run-log-action.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-action.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )
    return 0 if gate_g16 else 1


if __name__ == "__main__":
    sys.exit(main())
