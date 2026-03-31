#!/usr/bin/env python3
"""
QNG spectral analysis v1: full eigenvalue spectrum vs continuum (Weyl) limit.

Computes ALL eigenvalues of the symmetric normalised graph Laplacian
    L_sym = D^{-1/2} L_c D^{-1/2}  (eigenvalues in [0, 2])
for the QNG graph (DS-002, same construction as the wave-dynamics script) and
compares them with the continuum Weyl prediction:
    μ_m^{Weyl}  =  (π h² / A) × m

where h² = mean-squared edge length and A = graph domain area.

Method:
    1. Lanczos tridiagonalisation with full MGS re-orthogonalisation → T.
    2. Sturm-sequence + bisection to recover all n eigenvalues of T.
    3. Sort: 0 = μ_0 ≤ μ_1 ≤ … ≤ μ_{n−1} ≤ 2.
    4. Weyl slope α_Weyl = π h² / A; fit OLS slope α_meas on low-m eigenvalues.
    5. Gate G6a–G6d.

Gates:
    G6a — Zero eigenvalue: μ_0 < 1e-6      (connected graph → trivial kernel)
    G6b — Fiedler gap:     μ_1 > 1e-3      (non-trivial spectral gap)
    G6c — Weyl slope:      |α_meas/α_Weyl − 1| < 0.25  (within 25 %)
    G6d — Continuum R²:    R² > 0.95 for m ∈ [1, m_cross/2]

Outputs (in --out-dir):
    spectrum.csv                m, mu_m, mu_weyl
    metric_checks_spectrum.csv  G6 gate summary
    spectrum-plot.png           μ_m vs m: measured (blue) + Weyl (red)
    config_spectrum.json
    run-log-spectrum.txt
    artifact-hashes-spectrum.json

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
import platform
import random
import statistics
import struct
import sys
import time
import zlib


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-spectrum-v1"
)

LANCZOS_SEED_OFFSET = 77   # added to --seed for Lanczos starting vector


# ── Gate thresholds ────────────────────────────────────────────────────────────
@dataclass
class SpectrumThresholds:
    g6a_zero_eig_max: float = 1e-6   # μ_0 < 1e-6
    g6b_fiedler_min:  float = 1e-3   # μ_1 > 1e-3
    g6c_slope_rel_tol: float = 0.25  # |α_meas/α_Weyl − 1| < 0.25
    g6d_r2_min:       float = 0.95   # R² > 0.95 in low-freq regime


# ── Utilities ──────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v):   return "nan"
    if math.isinf(v):   return "inf"
    av = abs(v)
    if av == 0.0 or (1e-3 <= av < 1e4):
        return f"{v:.8f}"
    return f"{v:.6e}"


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


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
        for row in rows:
            w.writerow(row)


# ── Graph builder (same construction as wave-dynamics script) ──────────────────
def build_dataset_graph(
    dataset_id: str, seed: int
) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float, float]:
    """Returns (coords, sigma, adj_list, median_edge, spread)."""
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

    coords: list[tuple[float, float]] = [
        (rng.uniform(-spread, spread), rng.uniform(-spread, spread))
        for _ in range(n)
    ]

    def _clamp01(x: float) -> float:
        return min(max(x, 0.0), 1.0)

    sigma: list[float] = []
    for x, y in coords:
        r1 = ((x + 0.8) ** 2 + (y - 0.4) ** 2) / (2.0 * 1.35 * 1.35)
        r2 = ((x - 1.1) ** 2 + (y + 0.9) ** 2) / (2.0 * 1.10 * 1.10)
        s = 0.75 * math.exp(-r1) + 0.55 * math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(_clamp01(s))

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
        neigh = sorted(range(n), key=lambda j: dist[i][j] if j != i else 1e18)[:k]
        for j in neigh:
            base = max(dist[i][j], 1e-6)
            w = base * (1.0 + 0.10 * abs(sigma[i] - sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w
                adj[j][i] = w
                edge_lengths.append(w)

    adj_list = [[(j, ww) for j, ww in m.items()] for m in adj]
    median_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, sigma, adj_list, max(median_edge, 1e-9), spread


def build_adjacency(
    n: int, adj_list: list[list[tuple[int, float]]]
) -> list[list[int]]:
    return [[j for j, _ in row] for row in adj_list]


# ── Symmetric normalised Laplacian L_sym ────────────────────────────────────
def apply_lsym(
    v: list[float],
    neighbours: list[list[int]],
    inv_sqrt_d: list[float],
) -> list[float]:
    """
    L_sym = I − D^{−1/2} A D^{−1/2}
    [L_sym v]_i = v_i − inv_sqrt_d[i] · Σ_{j∈N(i)} inv_sqrt_d[j] · v_j
    Eigenvalues in [0, 2].  Symmetric in the standard inner product.
    """
    n = len(v)
    result = list(v)
    for i in range(n):
        s = sum(inv_sqrt_d[j] * v[j] for j in neighbours[i])
        result[i] -= inv_sqrt_d[i] * s
    return result


# ── Lanczos tridiagonalisation with full MGS re-orthogonalisation ─────────────
def lanczos_full_reorth(
    neighbours: list[list[int]],
    inv_sqrt_d: list[float],
    seed: int,
    max_steps: int | None = None,
) -> tuple[list[float], list[float]]:
    """
    Run Lanczos on L_sym with full Modified Gram-Schmidt re-orthogonalisation.
    Returns (alpha, beta) for the symmetric tridiagonal T:
        alpha[j]   = diagonal    (length m)
        beta[j]    = off-diagonal (length m-1)
    """
    n = len(neighbours)
    m = min(n, max_steps) if max_steps else n

    rng = random.Random(seed)
    q = [rng.gauss(0.0, 1.0) for _ in range(n)]
    norm = math.sqrt(sum(x * x for x in q))
    q = [x / norm for x in q]

    Q: list[list[float]] = [q]
    alpha: list[float] = []
    beta_out: list[float] = []

    for j in range(m):
        Lq = apply_lsym(Q[j], neighbours, inv_sqrt_d)

        # α_j = ⟨Q[j], L_sym Q[j]⟩
        a = sum(Q[j][i] * Lq[i] for i in range(n))
        alpha.append(a)

        # Residual r = L_sym Q[j] − α_j Q[j] − β_{j−1} Q[j−1]
        if j == 0:
            r = [Lq[i] - a * Q[j][i] for i in range(n)]
        else:
            bprev = beta_out[-1]
            r = [Lq[i] - a * Q[j][i] - bprev * Q[j - 1][i] for i in range(n)]

        # Full MGS re-orthogonalisation against all previous vectors
        for k in range(j + 1):
            dot = sum(r[i] * Q[k][i] for i in range(n))
            r = [r[i] - dot * Q[k][i] for i in range(n)]

        b = math.sqrt(sum(x * x for x in r))
        beta_out.append(b)

        if b < 1e-12 or j == m - 1:
            break

        Q.append([x / b for x in r])

    return alpha, beta_out[:-1]   # off-diagonal has one fewer entry


# ── Sturm-sequence eigenvalue count (LDL^T form, numerically stable) ──────────
def sturm_count(alpha: list[float], beta: list[float], lam: float) -> int:
    """
    Count eigenvalues of symmetric tridiagonal T strictly less than lam.
    Uses the LDL^T recurrence: d_k = (α_k − λ) − β_{k−1}² / d_{k−1}.
    Count = number of negative d_k.
    """
    d = alpha[0] - lam
    count = 1 if d < 0 else 0
    for i in range(1, len(alpha)):
        if d == 0.0:
            d = 1e-300
        d = (alpha[i] - lam) - beta[i - 1] ** 2 / d
        if d < 0:
            count += 1
    return count


# ── Bisection to find all eigenvalues ─────────────────────────────────────────
def find_all_eigenvalues(
    alpha: list[float],
    beta: list[float],
    lo: float = -0.01,
    hi: float = 2.01,
    tol: float = 1e-9,
) -> list[float]:
    """
    Find all eigenvalues of symmetric tridiagonal T in [lo, hi]
    using Sturm-sequence bisection (iterative, stack-based).
    """
    eigenvalues: list[float] = []
    cnt_lo = sturm_count(alpha, beta, lo)
    cnt_hi = sturm_count(alpha, beta, hi)
    stack = [(lo, hi, cnt_lo, cnt_hi)]

    while stack:
        a, b, ca, cb = stack.pop()
        n_in = cb - ca
        if n_in == 0:
            continue
        if b - a < tol:
            # n_in (possibly degenerate) eigenvalues in this tiny interval
            for _ in range(n_in):
                eigenvalues.append((a + b) / 2)
            continue
        mid = (a + b) / 2
        cm = sturm_count(alpha, beta, mid)
        if cm > ca:
            stack.append((a, mid, ca, cm))
        if cb > cm:
            stack.append((mid, b, cm, cb))

    eigenvalues.sort()
    return eigenvalues


# ── Simple OLS ────────────────────────────────────────────────────────────────
def ols(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Returns (slope, intercept, R²) for y = slope*x + intercept."""
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    xm = sum(xs) / n
    ym = sum(ys) / n
    cov = sum((xs[i] - xm) * (ys[i] - ym) for i in range(n))
    var = sum((x - xm) ** 2 for x in xs)
    if var < 1e-30:
        return float("nan"), float("nan"), float("nan")
    slope = cov / var
    intercept = ym - slope * xm
    ss_res = sum((ys[i] - (slope * xs[i] + intercept)) ** 2 for i in range(n))
    ss_tot = sum((y - ym) ** 2 for y in ys)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-30 else 1.0
    return slope, intercept, r2


# ── Canvas / PNG writer ────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, width: int, height: int,
                 bg: tuple[int, int, int] = (255, 255, 255)) -> None:
        self.width = width
        self.height = height
        self.px = bytearray(bg * (width * height))

    def set(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.px[i: i + 3] = bytes(color)

    def line(self, x0: int, y0: int, x1: int, y1: int,
             color: tuple[int, int, int]) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
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
                err += dy; x += sx
            if e2 <= dx:
                err += dx; y += sy

    def rect(self, x0: int, y0: int, x1: int, y1: int,
             color: tuple[int, int, int]) -> None:
        for x in range(x0, x1 + 1):
            self.set(x, y0, color); self.set(x, y1, color)
        for y in range(y0, y1 + 1):
            self.set(x0, y, color); self.set(x1, y, color)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        row = self.width * 3
        for y in range(self.height):
            raw.append(0)
            i0 = y * row
            raw.extend(self.px[i0: i0 + row])

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (struct.pack("!I", len(data)) + tag + data
                    + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF))

        ihdr = struct.pack("!IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        idat = zlib.compress(bytes(raw), level=9)
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", ihdr)
               + chunk(b"IDAT", idat)
               + chunk(b"IEND", b""))
        path.write_bytes(png)


def plot_dual(
    path: Path,
    xs: list[float],
    ys1: list[float],
    ys2: list[float],
    color1: tuple[int, int, int] = (40, 112, 184),
    color2: tuple[int, int, int] = (200, 60, 60),
    vline: float | None = None,
    vline_color: tuple[int, int, int] = (100, 180, 80),
) -> None:
    """Line plot with two y-series sharing one x-axis."""
    if not xs:
        return
    w, h = 1100, 520
    left, top, right, bottom = 90, 30, w - 20, h - 50
    can = Canvas(w, h, bg=(249, 251, 250))
    can.rect(left, top, right, bottom, (74, 88, 82))

    x_lo, x_hi = min(xs), max(xs)
    all_ys = ys1 + ys2
    y_lo, y_hi = min(all_ys), max(all_ys)
    if math.isclose(x_lo, x_hi): x_hi = x_lo + 1.0
    if math.isclose(y_lo, y_hi): y_hi = y_lo + 1.0

    def px(xi: float, yi: float) -> tuple[int, int]:
        px_ = left + int((xi - x_lo) / (x_hi - x_lo) * (right - left))
        py_ = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return (clamp(int(px_), left, right), clamp(int(py_), top, bottom))

    # Vertical line at crossover m*
    if vline is not None:
        vx, _ = px(vline, y_lo)
        can.line(vx, top, vx, bottom, vline_color)

    # Series 2 first (background)
    for i in range(len(xs) - 1):
        can.line(*px(xs[i], ys2[i]), *px(xs[i + 1], ys2[i + 1]), color2)
    # Series 1 on top
    for i in range(len(xs) - 1):
        can.line(*px(xs[i], ys1[i]), *px(xs[i + 1], ys1[i + 1]), color1)

    can.save_png(path)


# ── Argument parser ────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG spectral analysis v1 — Gate G6."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--lanczos-tol", type=float, default=1e-9,
                   help="Bisection tolerance for eigenvalue finding. Default=1e-9.")
    return p.parse_args()


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    thresholds = SpectrumThresholds()
    warnings: list[str] = []

    # ── Build graph ────────────────────────────────────────────────────────────
    coords, sigma, adj_list, median_edge, spread = build_dataset_graph(
        args.dataset_id, args.seed
    )
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)

    # ── Graph geometry: degrees, L_sym weights ─────────────────────────────────
    degrees = [len(nb) for nb in neighbours]
    inv_sqrt_d = [
        1.0 / math.sqrt(d) if d > 0 else 0.0 for d in degrees
    ]
    mean_degree = sum(degrees) / n

    # Mean-squared edge length h²_ms (directed; each undirected edge counted ×2)
    total_sq = sum(
        (coords[i][0] - coords[j][0]) ** 2 + (coords[i][1] - coords[j][1]) ** 2
        for i in range(n)
        for j in neighbours[i]
    )
    n_directed = sum(degrees)
    h2_ms = total_sq / n_directed if n_directed > 0 else median_edge ** 2

    # Domain area for Weyl's law (rectangular box [-spread, spread]²)
    area_A = (2.0 * spread) ** 2

    # Weyl slope: α_Weyl = π h²_ms / A
    alpha_weyl = math.pi * h2_ms / area_A

    # Crossover eigenvalue index where Weyl prediction hits the band limit (μ=2)
    # 2 = α_Weyl × m_cross  →  m_cross = 2 / α_Weyl
    m_cross = int(2.0 / alpha_weyl) if alpha_weyl > 0 else n

    print(f"Graph: n={n}  mean_degree={mean_degree:.2f}  h²_ms={h2_ms:.5f}"
          f"  A={area_A:.3f}")
    print(f"Weyl: α_Weyl={alpha_weyl:.6f}  m_cross≈{m_cross}  "
          f"(out of n={n})")

    # ── Lanczos tridiagonalisation ─────────────────────────────────────────────
    print("Running Lanczos (full MGS re-orthogonalisation)…", flush=True)
    t0 = time.perf_counter()
    alpha_T, beta_T = lanczos_full_reorth(
        neighbours, inv_sqrt_d,
        seed=args.seed + LANCZOS_SEED_OFFSET,
        max_steps=n,
    )
    m_lanczos = len(alpha_T)
    dt_lanczos = time.perf_counter() - t0
    print(f"  Lanczos: {m_lanczos} steps in {dt_lanczos:.2f}s", flush=True)

    if m_lanczos < n:
        warnings.append(
            f"Lanczos terminated early at step {m_lanczos} < n={n} "
            f"(starting vector in invariant subspace of dim {m_lanczos})"
        )

    # ── Find all eigenvalues via Sturm bisection ───────────────────────────────
    print("Finding all eigenvalues via Sturm-sequence bisection…", flush=True)
    t0 = time.perf_counter()
    eigenvalues = find_all_eigenvalues(
        alpha_T, beta_T, lo=-0.01, hi=2.01, tol=args.lanczos_tol
    )
    dt_bisect = time.perf_counter() - t0
    n_eig = len(eigenvalues)
    print(f"  Found {n_eig} eigenvalues in {dt_bisect:.2f}s", flush=True)

    if n_eig < 2:
        print("ERROR: fewer than 2 eigenvalues found.", file=sys.stderr)
        return 2

    mu0 = eigenvalues[0]       # should be ≈ 0
    mu1 = eigenvalues[1]       # Fiedler value
    mu_max = eigenvalues[-1]   # should be ≤ 2

    # ── Weyl predictions for each index ───────────────────────────────────────
    weyl = [alpha_weyl * m for m in range(n_eig)]

    # ── Gate G6a and G6b ──────────────────────────────────────────────────────
    gate_g6a = mu0 < thresholds.g6a_zero_eig_max
    gate_g6b = mu1 > thresholds.g6b_fiedler_min

    # ── Gate G6c and G6d: OLS fit in low-frequency regime ────────────────────
    # Use m ∈ [1, m_fit] where m_fit = min(m_cross//2, n_eig-1)
    m_fit = max(2, min(m_cross // 2, n_eig - 1))
    xs_fit = list(range(1, m_fit + 1))        # eigenvalue index m
    ys_fit = eigenvalues[1: m_fit + 1]        # measured μ_m for m=1..m_fit

    slope_meas, intercept_meas, r2_meas = ols(
        [float(x) for x in xs_fit], ys_fit
    )
    slope_rel = slope_meas / alpha_weyl if alpha_weyl > 0 else float("nan")
    gate_g6c = (math.isfinite(slope_rel)
                and abs(slope_rel - 1.0) < thresholds.g6c_slope_rel_tol)
    gate_g6d = math.isfinite(r2_meas) and r2_meas >= thresholds.g6d_r2_min

    gate_g6 = gate_g6a and gate_g6b and gate_g6c and gate_g6d
    decision = "pass" if gate_g6 else "fail"

    # ── Write spectrum CSV ─────────────────────────────────────────────────────
    spectrum_rows = [
        {
            "m":         str(m),
            "mu_m":      fmt(eigenvalues[m]),
            "mu_weyl":   fmt(weyl[m]),
            "ratio":     fmt(eigenvalues[m] / weyl[m])
                         if weyl[m] > 1e-12 else "inf",
        }
        for m in range(n_eig)
    ]
    write_csv(out_dir / "spectrum.csv",
              ["m", "mu_m", "mu_weyl", "ratio"], spectrum_rows)

    # ── Write metric CSV ───────────────────────────────────────────────────────
    metric_rows = [
        {"gate_id": "G6a", "metric": "mu_0",
         "value": fmt(mu0),
         "threshold": f"<{thresholds.g6a_zero_eig_max}",
         "status": "pass" if gate_g6a else "fail"},
        {"gate_id": "G6b", "metric": "mu_1_fiedler",
         "value": fmt(mu1),
         "threshold": f">{thresholds.g6b_fiedler_min}",
         "status": "pass" if gate_g6b else "fail"},
        {"gate_id": "G6c", "metric": "slope_rel",
         "value": fmt(slope_rel),
         "threshold": f"|slope_meas/alpha_Weyl-1|<{thresholds.g6c_slope_rel_tol}",
         "status": "pass" if gate_g6c else "fail"},
        {"gate_id": "G6d", "metric": "continuum_r2",
         "value": fmt(r2_meas),
         "threshold": f">{thresholds.g6d_r2_min}",
         "status": "pass" if gate_g6d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision,
         "threshold": "G6a&G6b&G6c&G6d",
         "status": decision},
    ]
    write_csv(out_dir / "metric_checks_spectrum.csv",
              ["gate_id", "metric", "value", "threshold", "status"],
              metric_rows)

    # ── Spectrum plot: measured (blue) vs Weyl (red) ──────────────────────────
    idx = list(range(n_eig))
    # Cap Weyl at 2.0 for plotting clarity
    weyl_capped = [min(w, 2.0) for w in weyl]
    plot_dual(
        out_dir / "spectrum-plot.png",
        [float(i) for i in idx],
        eigenvalues,         # blue: measured
        weyl_capped,         # red: Weyl
        vline=float(m_cross),
    )

    # ── Config and hashes ─────────────────────────────────────────────────────
    duration = time.perf_counter() - started
    config = {
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "mean_degree": mean_degree,
        "h2_ms": h2_ms,
        "median_edge": median_edge,
        "area_A": area_A,
        "alpha_weyl": alpha_weyl,
        "m_cross": m_cross,
        "m_fit": m_fit,
        "n_lanczos_steps": m_lanczos,
        "n_eigenvalues": n_eig,
        "thresholds": {
            "g6a_zero_eig_max": thresholds.g6a_zero_eig_max,
            "g6b_fiedler_min":  thresholds.g6b_fiedler_min,
            "g6c_slope_rel_tol": thresholds.g6c_slope_rel_tol,
            "g6d_r2_min":       thresholds.g6d_r2_min,
        },
        "results": {
            "mu_0":         mu0,
            "mu_1_fiedler": mu1,
            "mu_max":       mu_max,
            "slope_meas":   slope_meas,
            "slope_weyl":   alpha_weyl,
            "slope_rel":    slope_rel if math.isfinite(slope_rel) else None,
            "r2_continuum": r2_meas  if math.isfinite(r2_meas)  else None,
            "decision":     decision,
        },
    }
    (out_dir / "config_spectrum.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    files_for_hash = [
        out_dir / "spectrum.csv",
        out_dir / "metric_checks_spectrum.csv",
        out_dir / "config_spectrum.json",
    ]
    hashes = {f.name: sha256_of(f) for f in files_for_hash if f.exists()}
    (out_dir / "artifact-hashes-spectrum.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log_lines = [
        "QNG spectrum v1 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"dataset_id: {args.dataset_id}  seed: {args.seed}",
        f"n_nodes: {n}  mean_degree: {mean_degree:.2f}",
        f"h2_ms: {h2_ms:.6f}  median_edge: {median_edge:.6f}  area_A: {area_A:.4f}",
        f"alpha_Weyl: {alpha_weyl:.6f}  m_cross: {m_cross}  m_fit: {m_fit}",
        f"n_lanczos_steps: {m_lanczos}  n_eigenvalues: {n_eig}",
        f"duration_seconds: {duration:.3f}",
        f"decision: {decision}",
        "",
        f"mu_0={fmt(mu0)}  (G6a threshold <{thresholds.g6a_zero_eig_max})",
        f"mu_1_Fiedler={fmt(mu1)}  (G6b threshold >{thresholds.g6b_fiedler_min})",
        f"slope_meas={fmt(slope_meas)}  slope_Weyl={fmt(alpha_weyl)}"
        f"  slope_rel={fmt(slope_rel)}  (G6c threshold |·-1|<{thresholds.g6c_slope_rel_tol})",
        f"R2_continuum={fmt(r2_meas)}  (G6d threshold >{thresholds.g6d_r2_min})",
        f"mu_max={fmt(mu_max)}",
        "",
    ]
    if warnings:
        log_lines.append("warnings:")
        log_lines.extend(f"- {w}" for w in warnings)
    (out_dir / "run-log-spectrum.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    # ── Print summary ──────────────────────────────────────────────────────────
    print("QNG spectrum v1 completed.")
    print(f"Artifacts: {out_dir}")
    print(f"decision={decision}  G6={gate_g6}(a={gate_g6a},b={gate_g6b},"
          f"c={gate_g6c},d={gate_g6d})")
    print(f"G6a (zero eig):  μ_0={fmt(mu0)}"
          f"  threshold=<{thresholds.g6a_zero_eig_max}")
    print(f"G6b (Fiedler):   μ_1={fmt(mu1)}"
          f"  threshold=>{thresholds.g6b_fiedler_min}")
    print(f"G6c (Weyl slope): slope_rel={fmt(slope_rel)}"
          f"  α_meas={fmt(slope_meas)}  α_Weyl={fmt(alpha_weyl)}"
          f"  threshold=|·-1|<{thresholds.g6c_slope_rel_tol}")
    print(f"G6d (continuum R²): R²={fmt(r2_meas)}"
          f"  fit over m=[1,{m_fit}]  threshold=>{thresholds.g6d_r2_min}")
    print(f"Spectrum: μ_max={fmt(mu_max)}  n_eig={n_eig}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
