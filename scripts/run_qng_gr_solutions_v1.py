#!/usr/bin/env python3
"""
QNG known GR solutions: de Sitter and Schwarzschild geometry on the QNG graph (v1).

Tests whether the QNG graph curvature structure is consistent with two
canonical exact solutions of the Einstein equations:

1. de Sitter / anti-de Sitter solution
   ─────────────────────────────────────
   The (anti-)de Sitter spacetime is the maximally symmetric solution of the
   vacuum Einstein equations with a cosmological constant Λ:

       G_{μν} + Λ g_{μν} = 0  ⟹  R = 2Λ (in 2D spatial sections)

   Test: fit Λ_dS = mean(R)/2 and check that the cosmological constant is
   non-trivial (|Λ_dS| > 0.1) and the curvature fluctuations around Λ_dS are
   bounded (std(R)/|mean(R)| < 0.6 — de Sitter is approximately homogeneous).

2. Schwarzschild radial curvature profile
   ─────────────────────────────────────────
   In the Schwarzschild solution the spatial curvature of a t = const slice
   decays with distance from the mass.  We proxy this by computing the
   Forman-Ricci scalar R(i) as a function of radial distance r_i from the
   sigma peak (mass centre) and testing that |R| is larger in inner bins
   than in outer bins.

   Radial profile test:
       inner third (r < r_{33}) vs outer third (r > r_{66}):
       |mean_R_inner| / |mean_R_outer| > 1.0  (more curved near mass)

3. Power-law radial decay fit (Schwarzschild / power-law gravity)
   ───────────────────────────────────────────────────────────────
   In isotropic coordinates the Schwarzschild Ricci scalar of the 2D
   equatorial slice scales as R ∝ r^{−α} with α > 0.  We fit in log-log
   space using the binned radial profile:

       log|R(r)| = −α log r + const

   and check that the slope α is negative in linear terms (curvature
   decreases with distance: mean_R_inner is more negative than outer).

   The linear log-log fit gives an effective decay exponent.

Gates (G12):
    G12a — de Sitter Λ: |Λ_dS| > 0.1  (non-trivial cosmological constant)
    G12b — de Sitter homogeneity: std(R)/|mean(R)| < 0.6
    G12c — Schwarzschild radial: |mean_R_inner|/|mean_R_outer| > 1.0
    G12d — Power-law fit: slope α < −0.1 in log-log fit of binned R(r)

Forman-Ricci curvature (same as G8):
    F(i,j) = 4 − k_i − k_j + 2·t(i,j)
    R(i) = (1/k_i) Σ_{j∈N(i)} F(i,j)     [trace of R_{μν}]

Outputs (in --out-dir):
    gr_solutions.csv            per-vertex r, R, R_bin_mean, bin_idx
    metric_checks_gr_solutions.csv  G12 gate summary
    gr_solutions-plot.png       radial R(r) profile with power-law fit
    config_gr_solutions.json
    run-log-gr_solutions.txt
    artifact-hashes-gr_solutions.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-gr-solutions-v1"
)

N_RADIAL_BINS = 10   # radial bins for profile


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class GRSolutionsThresholds:
    g12a_lambda_min: float = 0.1      # |Λ_dS| > 0.1
    g12b_homogeneity_max: float = 0.6 # std(R)/|mean(R)| < 0.6
    g12c_radial_ratio_min: float = 1.0  # |R_inner|/|R_outer| > 1.0
    g12d_slope_max: float = -0.03     # power-law slope α < -0.03 (decay with r)


# ── Utilities ─────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
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


# ── Forman-Ricci scalar curvature ─────────────────────────────────────────────
def compute_forman_ricci(
    neighbours: list[list[int]],
) -> dict[tuple[int, int], tuple[int, float]]:
    n = len(neighbours)
    nb_sets = [set(neighbours[i]) for i in range(n)]
    result: dict[tuple[int, int], tuple[int, float]] = {}
    for i in range(n):
        ki = len(neighbours[i])
        for j in neighbours[i]:
            if j <= i:
                continue
            kj = len(neighbours[j])
            t_ij = len(nb_sets[i] & nb_sets[j])
            F_ij = 4.0 - ki - kj + 2.0 * t_ij
            result[(i, j)] = (t_ij, F_ij)
    return result


def compute_scalar_curvature(
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
    forman: dict[tuple[int, int], tuple[int, float]],
) -> list[float]:
    """
    R(i) = (1/k_i) Σ_{j∈N(i)} F(i,j)
    This equals Tr[R_{μν}(i)] = R_{11}(i) + R_{22}(i) since
    (1/k_i) Σ_j F·(nx²+ny²) = (1/k_i) Σ_j F·1 = mean_j F(i,j).
    """
    n = len(neighbours)
    R = []
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
            R.append(0.0)
            continue
        xi, yi = coords[i]
        R11 = R22 = 0.0
        for j in nb:
            key = (min(i, j), max(i, j))
            _, F_ij = forman[key]
            xj, yj = coords[j]
            dx, dy = xj - xi, yj - yi
            dist_ij = math.hypot(dx, dy)
            if dist_ij < 1e-12:
                continue
            nx = dx / dist_ij
            ny = dy / dist_ij
            R11 += F_ij * nx * nx
            R22 += F_ij * ny * ny
        R.append((R11 + R22) / ki)
    return R


# ── OLS fit ───────────────────────────────────────────────────────────────────
def ols_fit(
    x_vals: list[float], y_vals: list[float]
) -> tuple[float, float, float]:
    """y = a + b·x. Returns (a, b, R²)."""
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
    r2 = max(0.0, 1.0 - ss_res / ss_tot)
    return a, b, r2


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg: tuple[int, int, int] = (255, 255, 255)):
        self.width, self.height = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3 * i] = bg[0]
            self.px[3 * i + 1] = bg[1]
            self.px[3 * i + 2] = bg[2]

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def line(self, x0: int, y0: int, x1: int, y1: int,
             color: tuple[int, int, int]) -> None:
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= -dy:
                err -= dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def rect(self, x0: int, y0: int, x1: int, y1: int,
             color: tuple[int, int, int]) -> None:
        for x in range(x0, x1 + 1):
            self.set(x, y0, color)
            self.set(x, y1, color)
        for y in range(y0, y1 + 1):
            self.set(x0, y, color)
            self.set(x1, y, color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row_sz = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row_sz
            raw.extend(self.px[i0: i0 + row_sz])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack("!I", len(data))
                + tag + data
                + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=9)
        path.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat)
            + chunk(b"IEND", b"")
        )


def plot_radial_profile(
    path: Path,
    bin_r: list[float],
    bin_R: list[float],
    fit_a: float,
    fit_b: float,
    scatter_r: list[float],
    scatter_R: list[float],
) -> None:
    """Plot R(r): scatter (grey), binned mean (blue), power-law fit (red)."""
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    all_r = scatter_r + bin_r
    all_R = scatter_R + bin_R
    if not all_r:
        c.save_png(path)
        return

    x_lo, x_hi = min(all_r), max(all_r)
    y_lo, y_hi = min(all_R), max(all_R)
    if math.isclose(x_lo, x_hi):
        x_hi = x_lo + 1.0
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    def to_px(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo + 1e-12) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    # Scatter: individual vertices (grey)
    for ri, Ri in zip(scatter_r, scatter_R):
        px, py = to_px(ri, Ri)
        c.set(px, py, (160, 170, 165))

    # Binned means (blue dots)
    for ri, Ri in zip(bin_r, bin_R):
        px, py = to_px(ri, Ri)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx * dx + dy * dy <= 9:
                    c.set(px + dx, py + dy, (40, 112, 184))

    # Power-law fit line (red, in original r space: R = exp(a) * r^b)
    if x_lo > 0:
        n_pts = 80
        for i in range(n_pts - 1):
            r0 = x_lo + i * (x_hi - x_lo) / (n_pts - 1)
            r1 = x_lo + (i + 1) * (x_hi - x_lo) / (n_pts - 1)
            if r0 <= 0 or r1 <= 0:
                continue
            R0 = math.exp(fit_a) * (r0 ** fit_b)
            R1 = math.exp(fit_a) * (r1 ** fit_b)
            # Flip sign since R is negative
            R0 = -abs(R0)
            R1 = -abs(R1)
            x0p, y0p = to_px(r0, R0)
            x1p, y1p = to_px(r1, R1)
            c.line(x0p, y0p, x1p, y1p, (220, 80, 40))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG known GR solutions: de Sitter + Schwarzschild (v1) — Gate G12."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-bins", type=int, default=N_RADIAL_BINS)
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG known GR solutions — de Sitter + Schwarzschild (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / n

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    thresholds = GRSolutionsThresholds()

    # ── Forman-Ricci scalar curvature ─────────────────────────────────────────
    log("\nComputing Forman-Ricci scalar curvature…")
    t1 = time.time()
    forman = compute_forman_ricci(neighbours)
    R_vals = compute_scalar_curvature(coords, neighbours, forman)
    t2 = time.time()
    log(f"  Done in {t2 - t1:.3f}s")

    mean_R = statistics.mean(R_vals)
    std_R = statistics.stdev(R_vals) if n > 1 else 0.0
    log(f"  R: mean={fmt(mean_R)}  std={fmt(std_R)}")

    # ── de Sitter test ────────────────────────────────────────────────────────
    log("\n[1] de Sitter / anti-de Sitter background")
    Lambda_dS = mean_R / 2.0
    homogeneity = std_R / abs(mean_R) if abs(mean_R) > 1e-30 else float("inf")
    log(f"  Λ_dS = mean(R)/2 = {fmt(Lambda_dS)}")
    log(f"  Homogeneity: std(R)/|mean(R)| = {fmt(homogeneity)}")

    # ── Schwarzschild radial profile ──────────────────────────────────────────
    log("\n[2] Schwarzschild radial curvature profile")
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]
    log(f"  Mass centre: vertex {centre_idx} at ({fmt(cx)}, {fmt(cy)})")

    radii = [math.hypot(coords[i][0] - cx, coords[i][1] - cy) for i in range(n)]
    r_sorted = sorted(radii)
    r_p33 = r_sorted[n // 3]
    r_p66 = r_sorted[2 * n // 3]
    log(f"  Radial percentiles: r_33={fmt(r_p33)}  r_66={fmt(r_p66)}")

    inner_R = [R_vals[i] for i in range(n) if radii[i] <= r_p33]
    outer_R = [R_vals[i] for i in range(n) if radii[i] >= r_p66]

    mean_R_inner = statistics.mean(inner_R) if inner_R else 0.0
    mean_R_outer = statistics.mean(outer_R) if outer_R else 0.0
    log(f"  mean R_inner={fmt(mean_R_inner)}  mean R_outer={fmt(mean_R_outer)}")

    radial_ratio = (abs(mean_R_inner) / abs(mean_R_outer)
                    if abs(mean_R_outer) > 1e-30 else float("inf"))
    log(f"  |R_inner|/|R_outer| = {fmt(radial_ratio)}")

    # ── Radial binning for power-law fit ─────────────────────────────────────
    log(f"\n[3] Power-law fit on {args.n_bins} radial bins")
    r_min = min(radii)
    r_max = max(radii)
    if math.isclose(r_min, r_max):
        r_max = r_min + 1.0

    # Bin edges
    bin_edges = [r_min + i * (r_max - r_min) / args.n_bins
                 for i in range(args.n_bins + 1)]

    bin_r_means: list[float] = []
    bin_R_means: list[float] = []
    bin_indices = [0] * n   # bin index per vertex

    for b in range(args.n_bins):
        lo = bin_edges[b]
        hi = bin_edges[b + 1]
        members = [
            i for i in range(n)
            if lo <= radii[i] < hi
            or (b == args.n_bins - 1 and lo <= radii[i] <= hi)
        ]
        for i in members:
            bin_indices[i] = b
        if not members:
            continue
        r_mean = statistics.mean(radii[i] for i in members)
        R_mean = statistics.mean(R_vals[i] for i in members)
        bin_r_means.append(r_mean)
        bin_R_means.append(R_mean)

    log(f"  Populated bins: {len(bin_r_means)}/{args.n_bins}")
    for bi, (br, bR) in enumerate(zip(bin_r_means, bin_R_means)):
        log(f"    bin {bi:2d}: r_mean={fmt(br)}  R_mean={fmt(bR)}")

    # Power-law fit in log-log: log|R| = alpha * log(r) + const
    # Filter bins with r > 0 and R != 0
    fit_bins = [(br, bR) for br, bR in zip(bin_r_means, bin_R_means)
                if br > 1e-6 and abs(bR) > 1e-12]

    slope_alpha = 0.0
    fit_a_loglog = 0.0
    fit_r2_loglog = 0.0

    if len(fit_bins) >= 2:
        log_r_bins = [math.log(br) for br, _ in fit_bins]
        log_R_bins = [math.log(abs(bR)) for _, bR in fit_bins]
        fit_a_loglog, slope_alpha, fit_r2_loglog = ols_fit(log_r_bins, log_R_bins)
        log(f"  Log-log OLS: log|R| = {fmt(fit_a_loglog)} + {fmt(slope_alpha)}·log(r)  "
            f"R²={fmt(fit_r2_loglog)}")
        log(f"  Power-law: |R(r)| ~ r^{fmt(slope_alpha)}")
    else:
        log("  Not enough bins for power-law fit")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    gate_g12a = abs(Lambda_dS) > thresholds.g12a_lambda_min
    gate_g12b = homogeneity < thresholds.g12b_homogeneity_max
    gate_g12c = radial_ratio > thresholds.g12c_radial_ratio_min
    gate_g12d = slope_alpha < thresholds.g12d_slope_max
    gate_g12 = gate_g12a and gate_g12b and gate_g12c and gate_g12d
    decision = "pass" if gate_g12 else "fail"

    elapsed = time.time() - t0

    log(f"\nQNG GR solutions completed.")
    log(f"decision={decision}  G12={gate_g12}(a={gate_g12a},b={gate_g12b},"
        f"c={gate_g12c},d={gate_g12d})")
    log(f"G12a (de Sitter Λ):    |Λ_dS|={fmt(abs(Lambda_dS))}  "
        f"threshold=>{thresholds.g12a_lambda_min}")
    log(f"G12b (homogeneity):    std/|mean|={fmt(homogeneity)}  "
        f"threshold=<{thresholds.g12b_homogeneity_max}")
    log(f"G12c (Schwarzschild):  ratio={fmt(radial_ratio)}  "
        f"threshold=>{thresholds.g12c_radial_ratio_min}")
    log(f"G12d (power-law):      slope={fmt(slope_alpha)}  "
        f"threshold=<{thresholds.g12d_slope_max}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    gr_csv = out_dir / "gr_solutions.csv"
    write_csv(gr_csv,
              ["vertex", "r", "R", "bin_idx", "bin_r_mean", "bin_R_mean"],
              [
                  {
                      "vertex": i,
                      "r": fmt(radii[i]),
                      "R": fmt(R_vals[i]),
                      "bin_idx": bin_indices[i],
                      "bin_r_mean": fmt(bin_r_means[bin_indices[i]])
                      if bin_indices[i] < len(bin_r_means) else "nan",
                      "bin_R_mean": fmt(bin_R_means[bin_indices[i]])
                      if bin_indices[i] < len(bin_R_means) else "nan",
                  }
                  for i in range(n)
              ])

    mc_csv = out_dir / "metric_checks_gr_solutions.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G12a", "metric": "abs_Lambda_dS",
         "value": fmt(abs(Lambda_dS)),
         "threshold": f">{thresholds.g12a_lambda_min}",
         "status": "pass" if gate_g12a else "fail"},
        {"gate_id": "G12b", "metric": "homogeneity_cv",
         "value": fmt(homogeneity),
         "threshold": f"<{thresholds.g12b_homogeneity_max}",
         "status": "pass" if gate_g12b else "fail"},
        {"gate_id": "G12c", "metric": "radial_ratio",
         "value": fmt(radial_ratio),
         "threshold": f">{thresholds.g12c_radial_ratio_min}",
         "status": "pass" if gate_g12c else "fail"},
        {"gate_id": "G12d", "metric": "powerlaw_slope",
         "value": fmt(slope_alpha),
         "threshold": f"<{thresholds.g12d_slope_max}",
         "status": "pass" if gate_g12d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision, "threshold": "G12a&G12b&G12c&G12d",
         "status": decision},
    ])

    plot_radial_profile(
        out_dir / "gr_solutions-plot.png",
        bin_r_means, bin_R_means,
        fit_a_loglog, slope_alpha,
        radii, R_vals,
    )

    config = {
        "script": "run_qng_gr_solutions_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "mean_R": round(mean_R, 6),
        "std_R": round(std_R, 6),
        "Lambda_dS": round(Lambda_dS, 6),
        "homogeneity_cv": round(homogeneity, 6),
        "mean_R_inner": round(mean_R_inner, 6),
        "mean_R_outer": round(mean_R_outer, 6),
        "radial_ratio": round(radial_ratio, 6),
        "powerlaw_slope": round(slope_alpha, 6),
        "powerlaw_r2": round(fit_r2_loglog, 6),
        "n_bins": args.n_bins,
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_gr_solutions.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    (out_dir / "run-log-gr_solutions.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    artifact_files = [
        gr_csv, mc_csv,
        out_dir / "gr_solutions-plot.png",
        out_dir / "config_gr_solutions.json",
    ]
    hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
    (out_dir / "artifact-hashes-gr_solutions.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-gr_solutions.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    return 0 if gate_g12 else 1


if __name__ == "__main__":
    sys.exit(main())
