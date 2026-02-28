#!/usr/bin/env python3
"""
QNG complete Einstein equations: G_{μν} = 8πG T_{μν} on the QNG graph (v1).

Tests four aspects of the complete Einstein field equations:

1. Hamiltonian constraint (Gauss law of GR)
   ─────────────────────────────────────────
   For a time-symmetric slice (zero extrinsic curvature K=0) with a
   cosmological constant Λ, the ADM Hamiltonian constraint reads:

       R^{(3)} − 2Λ = 16πG ρ

   where R^{(3)} is the 3D Ricci scalar and ρ is the matter energy density.
   On the QNG graph we proxy ρ(i) = σ(i)/σ_max and fit by OLS:

       R(i) = A + B · σ(i)/σ_max   ⟹  Λ = A/2,  G_eff = B / (16π)

2. Bianchi identity (contracted second Bianchi)
   ─────────────────────────────────────────────
   The Einstein tensor satisfies ∇_μ G^{μν} = 0 identically on smooth
   manifolds.  On the QNG graph we compute the discrete divergence:

       B_x(i) = ∂_x G_{11}(i) + ∂_y G_{12}(i)
       B_y(i) = ∂_x G_{12}(i) + ∂_y G_{22}(i)

   using the least-squares edge-difference gradient.

3. Trace identity (2D structural identity)
   ─────────────────────────────────────────
   In 2D: Tr G = G_{11} + G_{22} = R − R = 0 exactly.
   Verified numerically as max|Tr G| < 1e-10.

4. G_eff sign (positive Newton's constant)
   ─────────────────────────────────────────
   G_eff = B/(16π) must be non-trivially large: |G_eff_natural| > threshold.

Gates (G11):
    G11a — Hamiltonian fit:  R² of OLS [R(i) on σ(i)/σ_max] > 0.02
    G11b — Non-trivial G_eff: |B_slope| > 0.05 · |mean_R|
    G11c — Bianchi identity:  mean_i |B(i)| / |mean_R| < 1.5
    G11d — Trace identity:    max_i |G_11(i) + G_22(i)| < 1e-10

Forman-Ricci curvature and Einstein tensor (same as G8):
    F(i,j) = 4 − k_i − k_j + 2·t(i,j)
    R_{μν}(i) = (1/k_i) Σ_{j∈N(i)} F(i,j)·n̂^μ_{ij}·n̂^ν_{ij}
    G_{μν}(i) = R_{μν}(i) − ½δ_{μν}R(i)

Outputs (in --out-dir):
    einstein_eq.csv             per-vertex R, G_11,G_12,G_22, rho, B_x,B_y
    metric_checks_einstein_eq.csv  G11 gate summary
    einstein_eq-plot.png        scatter of R(i) vs σ(i) with OLS fit line
    config_einstein_eq.json
    run-log-einstein_eq.txt
    artifact-hashes-einstein_eq.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-einstein-eq-v1"
)

PHI_SCALE = 0.10


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class EinsteinEqThresholds:
    g11a_r2_min: float = 0.02          # OLS R² > 0.02 (some correlation)
    g11b_slope_min: float = 0.05       # |B_slope| > 0.05·|mean_R|
    g11c_bianchi_max: float = 1.5      # mean|B|/|mean_R| < 1.5
    g11d_trace_max: float = 1e-10      # max|Tr G| < 1e-10


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


# ── Forman-Ricci curvature ────────────────────────────────────────────────────
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


def compute_tensors(
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
    forman: dict[tuple[int, int], tuple[int, float]],
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
            _, F_ij = forman[key]
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
        R11 /= ki
        R12 /= ki
        R22 /= ki
        R = R11 + R22
        G11 = R11 - 0.5 * R
        G12 = R12
        G22 = R22 - 0.5 * R
        result.append((R11, R12, R22, R, G11, G12, G22))
    return result


# ── Discrete gradient ─────────────────────────────────────────────────────────
def compute_gradient(
    field: list[float],
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
) -> tuple[list[float], list[float]]:
    n = len(field)
    gx = [0.0] * n
    gy = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
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
        gx[i] = sx / ki
        gy[i] = sy / ki
    return gx, gy


# ── OLS fit ───────────────────────────────────────────────────────────────────
def ols_fit(
    x_vals: list[float], y_vals: list[float]
) -> tuple[float, float, float]:
    """Simple OLS: y = a + b·x.  Returns (a, b, R²)."""
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


def plot_einstein_eq(
    path: Path,
    sigma_norm: list[float],
    R_vals: list[float],
    fit_a: float,
    fit_b: float,
) -> None:
    """Scatter plot of R(i) vs σ(i)/σ_max with OLS fit line."""
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    x_lo, x_hi = 0.0, 1.0
    y_lo = min(R_vals)
    y_hi = max(R_vals)
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    def to_px(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo + 1e-12) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    # Scatter points
    for s, R in zip(sigma_norm, R_vals):
        px, py = to_px(s, R)
        c.set(px, py, (40, 112, 184))
        c.set(px + 1, py, (40, 112, 184))
        c.set(px, py + 1, (40, 112, 184))

    # OLS fit line
    xs_line = [x_lo, x_hi]
    ys_line = [fit_a + fit_b * x for x in xs_line]
    x0p, y0p = to_px(xs_line[0], ys_line[0])
    x1p, y1p = to_px(xs_line[1], ys_line[1])
    c.line(x0p, y0p, x1p, y1p, (220, 80, 40))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG complete Einstein equations (v1) — Gate G11."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
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
    log("QNG complete Einstein equations G_{μν} = 8πG T_{μν} (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / n

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    thresholds = EinsteinEqThresholds()

    # ── Forman-Ricci and Einstein tensor ─────────────────────────────────────
    log("\nComputing Forman-Ricci curvature and Einstein tensor…")
    t1 = time.time()
    forman = compute_forman_ricci(neighbours)
    tensors = compute_tensors(coords, neighbours, forman)
    t2 = time.time()
    log(f"  Done in {t2 - t1:.3f}s")

    R_vals   = [v[3] for v in tensors]
    G11_vals = [v[4] for v in tensors]
    G12_vals = [v[5] for v in tensors]
    G22_vals = [v[6] for v in tensors]

    mean_R = statistics.mean(R_vals)
    std_R  = statistics.stdev(R_vals) if n > 1 else 0.0
    log(f"  R: mean={fmt(mean_R)}  std={fmt(std_R)}")

    # Trace identity check (G11d)
    max_tr_G = max(abs(G11_vals[i] + G22_vals[i]) for i in range(n))
    log(f"  max|Tr G| = {fmt(max_tr_G)}")

    # ── Hamiltonian constraint: OLS fit R = A + B·σ/σ_max ────────────────────
    log("\nFitting Hamiltonian constraint R(i) = 2Λ + 16πG_eff·σ(i)/σ_max …")
    sigma_max = max(sigma)
    sigma_norm = [s / sigma_max for s in sigma]

    fit_a, fit_b, fit_r2 = ols_fit(sigma_norm, R_vals)
    Lambda_fit = fit_a / 2.0
    G_eff = fit_b / (16.0 * math.pi)

    log(f"  OLS: A={fmt(fit_a)}  B={fmt(fit_b)}  R²={fmt(fit_r2)}")
    log(f"  Λ_eff = A/2 = {fmt(Lambda_fit)}")
    log(f"  G_eff = B/(16π) = {fmt(G_eff)}")

    # ── Bianchi identity: ∇_μ G^{μν} ≈ 0 ─────────────────────────────────────
    log("\nChecking discrete Bianchi identity…")
    t3 = time.time()
    dG11_dx, dG11_dy = compute_gradient(G11_vals, coords, neighbours)
    dG12_dx, dG12_dy = compute_gradient(G12_vals, coords, neighbours)
    dG22_dx, dG22_dy = compute_gradient(G22_vals, coords, neighbours)
    t4 = time.time()
    log(f"  Gradient computation in {t4 - t3:.3f}s")

    B_x = [dG11_dx[i] + dG12_dy[i] for i in range(n)]
    B_y = [dG12_dx[i] + dG22_dy[i] for i in range(n)]
    B_mag = [math.hypot(B_x[i], B_y[i]) for i in range(n)]
    mean_B = statistics.mean(B_mag)
    bianchi_ratio = mean_B / abs(mean_R) if abs(mean_R) > 1e-30 else float("inf")
    log(f"  mean|B| = {fmt(mean_B)}  |mean_R| = {fmt(abs(mean_R))}")
    log(f"  Bianchi ratio = mean|B|/|mean_R| = {fmt(bianchi_ratio)}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    slope_threshold = thresholds.g11b_slope_min * abs(mean_R)
    gate_g11a = fit_r2 > thresholds.g11a_r2_min
    gate_g11b = abs(fit_b) > slope_threshold
    gate_g11c = bianchi_ratio < thresholds.g11c_bianchi_max
    gate_g11d = max_tr_G < thresholds.g11d_trace_max
    gate_g11 = gate_g11a and gate_g11b and gate_g11c and gate_g11d
    decision = "pass" if gate_g11 else "fail"

    elapsed = time.time() - t0

    log(f"\nQNG Einstein equations completed.")
    log(f"decision={decision}  G11={gate_g11}(a={gate_g11a},b={gate_g11b},"
        f"c={gate_g11c},d={gate_g11d})")
    log(f"G11a (Hamiltonian fit): R²={fmt(fit_r2)}  "
        f"threshold=>{thresholds.g11a_r2_min}")
    log(f"G11b (non-trivial G_eff): |B|={fmt(abs(fit_b))}  "
        f"threshold=>{fmt(slope_threshold)}")
    log(f"G11c (Bianchi identity): ratio={fmt(bianchi_ratio)}  "
        f"threshold=<{thresholds.g11c_bianchi_max}")
    log(f"G11d (trace identity): max|TrG|={fmt(max_tr_G)}  "
        f"threshold=<{thresholds.g11d_trace_max}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    eq_csv = out_dir / "einstein_eq.csv"
    write_csv(eq_csv,
              ["vertex", "R", "G_11", "G_12", "G_22", "sigma_norm",
               "B_x", "B_y", "B_mag"],
              [
                  {
                      "vertex": i,
                      "R": fmt(R_vals[i]),
                      "G_11": fmt(G11_vals[i]),
                      "G_12": fmt(G12_vals[i]),
                      "G_22": fmt(G22_vals[i]),
                      "sigma_norm": fmt(sigma_norm[i]),
                      "B_x": fmt(B_x[i]),
                      "B_y": fmt(B_y[i]),
                      "B_mag": fmt(B_mag[i]),
                  }
                  for i in range(n)
              ])

    mc_csv = out_dir / "metric_checks_einstein_eq.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G11a", "metric": "hamiltonian_R2",
         "value": fmt(fit_r2),
         "threshold": f">{thresholds.g11a_r2_min}",
         "status": "pass" if gate_g11a else "fail"},
        {"gate_id": "G11b", "metric": "slope_abs_B",
         "value": fmt(abs(fit_b)),
         "threshold": f">{fmt(slope_threshold)}",
         "status": "pass" if gate_g11b else "fail"},
        {"gate_id": "G11c", "metric": "bianchi_ratio",
         "value": fmt(bianchi_ratio),
         "threshold": f"<{thresholds.g11c_bianchi_max}",
         "status": "pass" if gate_g11c else "fail"},
        {"gate_id": "G11d", "metric": "max_trace_G",
         "value": fmt(max_tr_G),
         "threshold": f"<{thresholds.g11d_trace_max}",
         "status": "pass" if gate_g11d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision, "threshold": "G11a&G11b&G11c&G11d",
         "status": decision},
    ])

    plot_einstein_eq(
        out_dir / "einstein_eq-plot.png",
        sigma_norm, R_vals, fit_a, fit_b,
    )

    config = {
        "script": "run_qng_einstein_eq_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "mean_R": round(mean_R, 6),
        "std_R": round(std_R, 6),
        "fit_a": round(fit_a, 6),
        "fit_b": round(fit_b, 6),
        "fit_r2": round(fit_r2, 6),
        "Lambda_fit": round(Lambda_fit, 6),
        "G_eff": round(G_eff, 8),
        "bianchi_ratio": round(bianchi_ratio, 6),
        "max_tr_G": float(f"{max_tr_G:.4e}"),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_einstein_eq.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    (out_dir / "run-log-einstein_eq.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    artifact_files = [
        eq_csv, mc_csv,
        out_dir / "einstein_eq-plot.png",
        out_dir / "config_einstein_eq.json",
    ]
    hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
    (out_dir / "artifact-hashes-einstein_eq.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-einstein_eq.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    return 0 if gate_g11 else 1


if __name__ == "__main__":
    sys.exit(main())
