#!/usr/bin/env python3
"""
QNG Einstein tensor: discrete Forman-Ricci curvature and G_{ij} (v1).

Computes the discrete curvature structure of the QNG graph via Forman-Ricci
curvature, then constructs the discrete Ricci tensor R_{μν}(i) and Einstein
tensor G_{μν}(i) = R_{μν}(i) − ½δ_{μν}R(i) at every vertex.

Algorithm
─────────
1. Forman-Ricci curvature per edge (Sreejith et al. 2016):

       F(i,j) = 4 − k_i − k_j + 2·t(i,j)

   where k_i = deg(i) and t(i,j) = |N(i) ∩ N(j)| is the number of
   triangles (2-simplices) containing edge (i,j).

2. Discrete Ricci tensor at vertex i (geometric projection):

       R_{μν}(i) = (1/k_i) Σ_{j∈N(i)} F(i,j) · n̂^μ_{ij} · n̂^ν_{ij}

   where n̂_{ij} = (r_j − r_i)/|r_j − r_i| is the edge unit vector.

3. Scalar curvature:   R(i) = R_{11}(i) + R_{22}(i)

4. Einstein tensor:    G_{μν}(i) = R_{μν}(i) − ½ δ_{μν} R(i)

   Identity: Tr[G(i)] = G_{11}(i)+G_{22}(i) = R(i)−R(i) = 0  (exact in 2D).

Physical interpretation
───────────────────────
The Forman-Ricci curvature on a graph is a discretisation of the
sectional/Ricci curvature of an underlying Riemannian manifold.  For a
random k-NN geometric graph (k ≈ 9–10), the bulk curvature is expected to
be negative (hyperbolic-like) because each node is surrounded by more
neighbours than the Euclidean "ball" predicts—exactly the regime where QNG
predicts a non-trivial geometric back-reaction.

The off-diagonal component G_{12}(i) measures the local anisotropy of the
curvature distribution.  For a statistically isotropic point process it
vanishes on average but fluctuates around zero.

Gates (G8):
    G8a — Negative curvature:     mean_F < −1.0
    G8b — Curvature inhomogeneity: std(R) / |mean(R)| > 0.05
    G8c — Off-diagonal symmetry:   |mean(G_12)| / std(G_12) < 0.30
    G8d — Approximate isotropy:    mean(|G_11−G_22|) / |mean(R)| < 0.50

Outputs (in --out-dir):
    forman_ricci.csv            node_i, node_j, k_i, k_j, triangles, F
    einstein_tensor.csv         per-vertex R_11,R_12,R_22,R,G_11,G_12,G_22
    metric_checks_einstein.csv  G8 gate summary
    ricci_distribution-plot.png sorted R(i) curvature landscape
    config_einstein.json
    run-log-einstein.txt
    artifact-hashes-einstein.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-einstein-v1"
)


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class EinsteinThresholds:
    g8a_mean_F_max: float = -1.0    # mean_F < -1 (negatively curved)
    g8b_cv_R_min: float = 0.05     # std(R)/|mean(R)| > 0.05 (inhomogeneous)
    g8c_sym_ratio_max: float = 0.30 # |mean(G12)|/std(G12) < 0.30
    g8d_aniso_ratio_max: float = 0.50 # mean|G11-G22|/|mean(R)| < 0.50


# ── Utilities ─────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3):
        return f"{v:.8e}"
    return f"{v:.8f}"


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

    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        for j in range(i + 1, n):
            xj, yj = coords[j]
            d = math.hypot(xi - xj, yi - yj)
            dist[i][j] = d
            dist[j][i] = d

    adj: list[dict[int, float]] = [dict() for _ in range(n)]
    for i in range(n):
        neigh = sorted(range(n), key=lambda j: dist[i][j] if j != i else 1e18)[:k]
        for j in neigh:
            base = max(dist[i][j], 1e-6)
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
    """
    Returns dict mapping edge (i,j) with i<j to (t_ij, F_ij) where
      t_ij = |N(i) ∩ N(j)|  (triangle count)
      F_ij = 4 − k_i − k_j + 2·t_ij  (Forman-Ricci curvature)
    """
    n = len(neighbours)
    nb_sets = [set(neighbours[i]) for i in range(n)]
    result: dict[tuple[int, int], tuple[int, float]] = {}
    for i in range(n):
        ki = len(neighbours[i])
        for j in neighbours[i]:
            if j <= i:
                continue
            kj = len(neighbours[j])
            # common neighbours (triangles through edge i-j)
            t_ij = len(nb_sets[i] & nb_sets[j])
            F_ij = 4.0 - ki - kj + 2.0 * t_ij
            result[(i, j)] = (t_ij, F_ij)
    return result


# ── Discrete Ricci tensor and Einstein tensor ─────────────────────────────────
def compute_tensors(
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
    forman: dict[tuple[int, int], tuple[int, float]],
) -> list[tuple[float, float, float, float, float, float, float]]:
    """
    Returns per-vertex list of (R11, R12, R22, R, G11, G12, G22).

    R_{μν}(i) = (1/k_i) Σ_{j∈N(i)} F(i,j)·n̂^μ_{ij}·n̂^ν_{ij}
    R(i)      = R_11 + R_22
    G_{μν}(i) = R_{μν}(i) − ½δ_{μν} R(i)
    """
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


def plot_sorted_series(
    path: Path,
    values: list[float],
    color: tuple[int, int, int],
    hline: float | None = None,
) -> None:
    """Plot sorted values as a "curvature spectrum" (rank vs value)."""
    if not values:
        return
    sv = sorted(values)
    xs = list(range(len(sv)))
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    x_lo, x_hi = 0.0, float(len(sv) - 1)
    y_lo = min(sv)
    y_hi = max(sv)
    if hline is not None:
        y_lo = min(y_lo, hline)
        y_hi = max(y_hi, hline)
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    def to_px(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo + 1e-12) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return (
            max(left, min(right, int(px))),
            max(top, min(bottom, int(py))),
        )

    if hline is not None:
        hx0, hy0 = to_px(x_lo, hline)
        hx1, hy1 = to_px(x_hi, hline)
        c.line(hx0, hy0, hx1, hy1, (200, 50, 50))

    for i in range(len(sv) - 1):
        x0p, y0p = to_px(xs[i], sv[i])
        x1p, y1p = to_px(xs[i + 1], sv[i + 1])
        c.line(x0p, y0p, x1p, y1p, color)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG Einstein tensor (Forman-Ricci) v1 — Gate G8."
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
    log("QNG Einstein tensor — Forman-Ricci curvature and G_{ij} (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    degrees = [len(nb) for nb in neighbours]
    mean_degree = sum(degrees) / n
    n_edges = sum(degrees) // 2

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.4f}  edges={n_edges}")

    thresholds = EinsteinThresholds()

    # ── Forman-Ricci curvature ────────────────────────────────────────────────
    log("\nComputing Forman-Ricci curvature…")
    t1 = time.time()
    forman = compute_forman_ricci(neighbours)
    t2 = time.time()
    log(f"  {len(forman)} edges processed in {t2 - t1:.3f}s")

    all_F = [F for _, F in forman.values()]
    mean_F = statistics.mean(all_F)
    std_F = statistics.stdev(all_F) if len(all_F) > 1 else 0.0
    min_F = min(all_F)
    max_F = max(all_F)
    all_t = [t for t, _ in forman.values()]
    mean_t = statistics.mean(all_t)

    log(f"  Forman curvature: mean={fmt(mean_F)}  std={fmt(std_F)}  "
        f"min={fmt(min_F)}  max={fmt(max_F)}")
    log(f"  Mean triangles per edge: {mean_t:.3f}")

    # ── Ricci and Einstein tensors ────────────────────────────────────────────
    log("\nComputing discrete Ricci and Einstein tensors…")
    t3 = time.time()
    tensors = compute_tensors(coords, neighbours, forman)
    t4 = time.time()
    log(f"  Done in {t4 - t3:.3f}s")

    R11_vals = [v[0] for v in tensors]
    R12_vals = [v[1] for v in tensors]
    R22_vals = [v[2] for v in tensors]
    R_vals   = [v[3] for v in tensors]
    G11_vals = [v[4] for v in tensors]
    G12_vals = [v[5] for v in tensors]
    G22_vals = [v[6] for v in tensors]

    mean_R   = statistics.mean(R_vals)
    std_R    = statistics.stdev(R_vals) if n > 1 else 0.0
    mean_G12 = statistics.mean(G12_vals)
    std_G12  = statistics.stdev(G12_vals) if n > 1 else 1.0
    mean_aniso = statistics.mean(abs(G11_vals[i] - G22_vals[i]) for i in range(n))

    log(f"  R: mean={fmt(mean_R)}  std={fmt(std_R)}")
    log(f"  G_12: mean={fmt(mean_G12)}  std={fmt(std_G12)}")
    log(f"  mean|G_11-G_22| = {fmt(mean_aniso)}")

    # Verify Tr[G] = 0 exactly
    max_tr_G = max(abs(G11_vals[i] + G22_vals[i]) for i in range(n))
    log(f"  max|Tr G| = {fmt(max_tr_G)}  (must be ≈ 0 by construction)")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    cv_R = std_R / abs(mean_R) if abs(mean_R) > 1e-30 else 0.0
    sym_ratio = abs(mean_G12) / std_G12 if std_G12 > 1e-30 else 0.0
    aniso_ratio = mean_aniso / abs(mean_R) if abs(mean_R) > 1e-30 else 0.0

    gate_g8a = mean_F < thresholds.g8a_mean_F_max
    gate_g8b = cv_R > thresholds.g8b_cv_R_min
    gate_g8c = sym_ratio < thresholds.g8c_sym_ratio_max
    gate_g8d = aniso_ratio < thresholds.g8d_aniso_ratio_max
    gate_g8 = gate_g8a and gate_g8b and gate_g8c and gate_g8d
    decision = "pass" if gate_g8 else "fail"

    log(f"\nQNG Einstein tensor completed.")
    log(f"decision={decision}  G8={gate_g8}(a={gate_g8a},b={gate_g8b},"
        f"c={gate_g8c},d={gate_g8d})")
    log(f"G8a (neg curvature):  mean_F={fmt(mean_F)}  threshold=<{thresholds.g8a_mean_F_max}")
    log(f"G8b (inhomogeneous):  std(R)/|mean(R)|={fmt(cv_R)}  threshold=>{thresholds.g8b_cv_R_min}")
    log(f"G8c (off-diag sym):   |mean(G12)|/std(G12)={fmt(sym_ratio)}  threshold=<{thresholds.g8c_sym_ratio_max}")
    log(f"G8d (isotropy):       mean|G11-G22|/|mean(R)|={fmt(aniso_ratio)}  threshold=<{thresholds.g8d_aniso_ratio_max}")

    elapsed = time.time() - t0

    # ── Write artifacts ───────────────────────────────────────────────────────
    # forman_ricci.csv
    fr_csv = out_dir / "forman_ricci.csv"
    fr_rows = []
    for (i, j), (t_ij, F_ij) in sorted(forman.items()):
        fr_rows.append({
            "node_i": i, "node_j": j,
            "k_i": degrees[i], "k_j": degrees[j],
            "triangles": t_ij, "F": fmt(F_ij),
        })
    write_csv(fr_csv, ["node_i", "node_j", "k_i", "k_j", "triangles", "F"], fr_rows)

    # einstein_tensor.csv
    et_csv = out_dir / "einstein_tensor.csv"
    et_rows = [
        {
            "vertex": i,
            "R_11": fmt(R11_vals[i]), "R_12": fmt(R12_vals[i]),
            "R_22": fmt(R22_vals[i]), "R": fmt(R_vals[i]),
            "G_11": fmt(G11_vals[i]), "G_12": fmt(G12_vals[i]),
            "G_22": fmt(G22_vals[i]),
        }
        for i in range(n)
    ]
    write_csv(et_csv,
              ["vertex", "R_11", "R_12", "R_22", "R", "G_11", "G_12", "G_22"],
              et_rows)

    # metric_checks_einstein.csv
    mc_csv = out_dir / "metric_checks_einstein.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G8a", "metric": "mean_F",
         "value": fmt(mean_F),
         "threshold": f"<{thresholds.g8a_mean_F_max}",
         "status": "pass" if gate_g8a else "fail"},
        {"gate_id": "G8b", "metric": "cv_R",
         "value": fmt(cv_R),
         "threshold": f">{thresholds.g8b_cv_R_min}",
         "status": "pass" if gate_g8b else "fail"},
        {"gate_id": "G8c", "metric": "offdiag_sym",
         "value": fmt(sym_ratio),
         "threshold": f"<{thresholds.g8c_sym_ratio_max}",
         "status": "pass" if gate_g8c else "fail"},
        {"gate_id": "G8d", "metric": "aniso_ratio",
         "value": fmt(aniso_ratio),
         "threshold": f"<{thresholds.g8d_aniso_ratio_max}",
         "status": "pass" if gate_g8d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision,
         "threshold": "G8a&G8b&G8c&G8d", "status": decision},
    ])

    # Plot: sorted R(i) — curvature landscape
    plot_sorted_series(
        out_dir / "ricci_distribution-plot.png",
        R_vals,
        color=(40, 112, 184),
        hline=0.0,
    )

    # config
    config = {
        "script": "run_qng_einstein_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "n_nodes": n,
        "n_edges": n_edges,
        "mean_degree": round(mean_degree, 4),
        "mean_F": round(mean_F, 6),
        "mean_R": round(mean_R, 6),
        "std_R": round(std_R, 6),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_einstein.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    (out_dir / "run-log-einstein.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    artifact_files = [fr_csv, et_csv, mc_csv,
                      out_dir / "ricci_distribution-plot.png",
                      out_dir / "config_einstein.json"]
    hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
    (out_dir / "artifact-hashes-einstein.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-einstein.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    return 0 if gate_g8 else 1


if __name__ == "__main__":
    sys.exit(main())
