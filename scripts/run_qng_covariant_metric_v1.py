#!/usr/bin/env python3
"""
QNG covariant metric: ADM decomposition of the QNG graph geometry (v1).

Constructs the full 2+1 covariant metric tensor via ADM decomposition,
using the sigma field σ(i) to define a gravitational potential Φ(i).

ADM decomposition
─────────────────
Gravitational potential (negative near mass → attractive):

    Φ(i) = −Φ_scale · σ(i) / σ_max

Lapse function (time runs slower near mass, equivalence principle):

    N(i) = 1 + Φ(i) = 1 − Φ_scale · σ(i)/σ_max  ∈ [1−Φ_scale, 1]

Isotropic spatial metric (space stretches near mass):

    γ_{ij}(i) = (1 − 2Φ(i)) δ_{ij}   ≡ γ(i) δ_{ij}

With Φ_scale = 0.08:  γ(i) = 1 + 0.16·σ(i)/σ_max ∈ [1.0, 1.16]  (always > 0)

Full 2+1 spacetime metric (zero shift N^i = 0):

    g_{ab}(i) = diag(−N(i)², γ(i), γ(i))

Geodesic acceleration (test particle at rest, via weak-field geodesic equation):

    a^i(p) = −∂^i Φ(p) = +Φ_scale · (∇σ)(p) / σ_max

Since σ peaks at the mass centre, ∇σ points inward and a^i points toward
the mass centre (gravitational attraction).

Discrete gradient of f at vertex i (least-squares on edge differences):

    (∂_x f)_i = (1/k_i) Σ_{j∈N(i)} [f(j)−f(i)] (x_j−x_i) / |r_j−r_i|²
    (∂_y f)_i = (1/k_i) Σ_{j∈N(i)} [f(j)−f(i)] (y_j−y_i) / |r_j−r_i|²

Gates (G10):
    G10a — No horizon:      min_i N(i) > 0        (lapse positive everywhere)
    G10b — Weak field:      max_i |Φ(i)| < 0.5    (linearised gravity valid)
    G10c — Positive metric: min_i γ(i) > 0         (spatial metric pos. def.)
    G10d — Inward gravity:  mean_i a_radial(i) > 0
                            a_radial(i) = a(i) · r̂_{i→centre}

Outputs (in --out-dir):
    covariant_metric.csv        per-vertex x,y,sigma,Phi,N,gamma,ax,ay,a_radial
    metric_checks_covariant.csv G10 gate summary
    covariant_metric-plot.png   spatial map of N(i) and a_radial
    config_covariant.json
    run-log-covariant.txt
    artifact-hashes-covariant.json

Dependency policy: stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import argparse
import hashlib
import json
import math
import statistics
import struct
import sys
import time
import zlib

from _common import (
    add_standard_cli_args,
    configure_stdio_utf8,
    ensure_outdir,
    rng as make_rng,
    write_csv as write_csv_common,
    write_run_manifest,
)


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-covariant-metric-v1"
)

# ── Physics parameters ─────────────────────────────────────────────────────────
PHI_SCALE = 0.08   # weak-field parameter; |Φ| ≤ PHI_SCALE << 1


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class CovariantMetricThresholds:
    g10a_lapse_min: float = 0.0      # N(i) > 0 everywhere (no horizon)
    g10b_weakfield_max: float = 0.5  # |Φ(i)| < 0.5 (linearised regime)
    g10c_gamma_min: float = 0.0      # γ(i) > 0 (positive definite)
    g10d_accel_min: float = 0.0      # mean a_radial > 0 (inward)


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
    write_csv_common(path, fieldnames, rows)


# ── Graph builder ─────────────────────────────────────────────────────────────
def build_dataset_graph(
    dataset_id: str, seed: int
) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]]]:
    rng = make_rng(seed)
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


# ── Discrete gradient ─────────────────────────────────────────────────────────
def compute_gradient(
    field: list[float],
    coords: list[tuple[float, float]],
    neighbours: list[list[int]],
) -> tuple[list[float], list[float]]:
    """
    Least-squares gradient at each vertex:
        (∂_x f)_i = (1/k_i) Σ_{j∈N(i)} [f_j−f_i](x_j−x_i) / |r_{ij}|²
        (∂_y f)_i = (1/k_i) Σ_{j∈N(i)} [f_j−f_i](y_j−y_i) / |r_{ij}|²
    """
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


def lerp_color(
    v: float, lo: float, hi: float,
    c0: tuple[int, int, int], c1: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Linearly interpolate a colour between c0 (at lo) and c1 (at hi)."""
    if hi <= lo:
        return c0
    t = max(0.0, min(1.0, (v - lo) / (hi - lo)))
    return (
        int(c0[0] + t * (c1[0] - c0[0])),
        int(c0[1] + t * (c1[1] - c0[1])),
        int(c0[2] + t * (c1[2] - c0[2])),
    )


def plot_covariant_metric(
    path: Path,
    coords: list[tuple[float, float]],
    lapse: list[float],
    a_radial: list[float],
) -> None:
    """Scatter plot: lapse N(i) as colour, a_radial as dot size proxy."""
    n = len(coords)
    w, h = 980, 480
    left, top, right, bottom = 40, 30, w // 2 - 10, h - 50
    # Left panel: N(i) map; Right panel: a_radial map
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))
    c.rect(w // 2 + 10, top, w - 20, bottom, (74, 88, 82))

    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    x_lo, x_hi = min(xs), max(xs)
    y_lo, y_hi = min(ys), max(ys)
    if math.isclose(x_lo, x_hi):
        x_hi = x_lo + 1.0
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    N_lo, N_hi = min(lapse), max(lapse)
    ar_lo, ar_hi = min(a_radial), max(a_radial)

    def to_px_left(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return max(left, min(right, px)), max(top, min(bottom, py))

    def to_px_right(xi: float, yi: float) -> tuple[int, int]:
        offset = w // 2 + 10
        r_right = w - 20
        px = offset + int((xi - x_lo) / (x_hi - x_lo) * (r_right - offset))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return max(offset, min(r_right, px)), max(top, min(bottom, py))

    for i in range(n):
        xi, yi = coords[i]
        # Left: N(i) — blue=slow (low N), red=fast (high N)
        px, py = to_px_left(xi, yi)
        col_n = lerp_color(lapse[i], N_lo, N_hi, (40, 80, 200), (220, 60, 40))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    c.set(px + dx, py + dy, col_n)
        # Right: a_radial — blue=inward, red=outward
        px2, py2 = to_px_right(xi, yi)
        col_a = lerp_color(a_radial[i], ar_lo, ar_hi, (220, 60, 40), (40, 160, 80))
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx * dx + dy * dy <= 4:
                    c.set(px2 + dx, py2 + dy, col_a)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG covariant metric: ADM decomposition (v1) — Gate G10."
    )
    add_standard_cli_args(
        p,
        default_dataset_id="DS-002",
        default_seed=3401,
        default_out_dir=str(DEFAULT_OUT_DIR),
        include_plots=True,
    )
    p.add_argument("--phi-scale", type=float, default=PHI_SCALE)
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    configure_stdio_utf8()
    args = parse_args()
    out_dir = ensure_outdir(args.out_dir)

    log_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG covariant metric — ADM decomposition (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / n

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")
    log(f"Phi_scale = {args.phi_scale}")

    thresholds = CovariantMetricThresholds()

    # ── ADM metric components ─────────────────────────────────────────────────
    sigma_max = max(sigma)
    sigma_min = min(sigma)
    log(f"\nσ field: min={fmt(sigma_min)}  max={fmt(sigma_max)}")

    # Gravitational potential: negative near mass (sigma peak = mass centre)
    phi = [-args.phi_scale * s / sigma_max for s in sigma]

    # Lapse: N = 1 + Φ = 1 − Φ_scale·σ/σ_max
    lapse = [1.0 + p for p in phi]

    # Isotropic spatial metric factor: γ = 1 − 2Φ = 1 + 2·Φ_scale·σ/σ_max
    gamma = [1.0 - 2.0 * p for p in phi]

    # Full metric determinant: g = −N² · γ²  (2D spatial × time)
    log("\nADM metric components:")
    log(f"  Φ: min={fmt(min(phi))}  max={fmt(max(phi))}")
    log(f"  N: min={fmt(min(lapse))}  max={fmt(max(lapse))}")
    log(f"  γ: min={fmt(min(gamma))}  max={fmt(max(gamma))}")

    # ── Geodesic acceleration ─────────────────────────────────────────────────
    # a^i = −∂^i Φ = +Φ_scale · (∇σ)^i / σ_max
    # Discrete gradient of Φ (same as computing -accel directly)
    dphi_dx, dphi_dy = compute_gradient(phi, coords, neighbours)

    # Acceleration: a^i = −grad Φ
    a_x = [-g for g in dphi_dx]
    a_y = [-g for g in dphi_dy]

    # Radial component toward mass centre (max sigma vertex)
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]
    log(f"\nMass centre: vertex {centre_idx}  at ({fmt(cx)}, {fmt(cy)})  σ={fmt(sigma[centre_idx])}")

    a_radial = []
    for i in range(n):
        xi, yi = coords[i]
        dx, dy = cx - xi, cy - yi
        d = math.hypot(dx, dy)
        if d < 1e-12:
            a_radial.append(0.0)
        else:
            a_radial.append((a_x[i] * dx + a_y[i] * dy) / d)

    mean_a_radial = statistics.mean(a_radial)
    mean_a_mag = statistics.mean(math.hypot(a_x[i], a_y[i]) for i in range(n))
    log(f"\nGeodesic acceleration:")
    log(f"  mean |a| = {fmt(mean_a_mag)}")
    log(f"  mean a_radial = {fmt(mean_a_radial)}  (positive = inward)")
    log(f"  fraction inward = {sum(1 for ar in a_radial if ar > 0) / n:.3f}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    gate_g10a = min(lapse) > thresholds.g10a_lapse_min
    gate_g10b = max(abs(p) for p in phi) < thresholds.g10b_weakfield_max
    gate_g10c = min(gamma) > thresholds.g10c_gamma_min
    gate_g10d = mean_a_radial > thresholds.g10d_accel_min
    gate_g10 = gate_g10a and gate_g10b and gate_g10c and gate_g10d
    decision = "pass" if gate_g10 else "fail"

    elapsed = time.time() - t0

    log(f"\nQNG covariant metric completed.")
    log(f"decision={decision}  G10={gate_g10}(a={gate_g10a},b={gate_g10b},"
        f"c={gate_g10c},d={gate_g10d})")
    log(f"G10a (no horizon):      min N={fmt(min(lapse))}  "
        f"threshold=>{thresholds.g10a_lapse_min}")
    log(f"G10b (weak field):      max|Φ|={fmt(max(abs(p) for p in phi))}  "
        f"threshold=<{thresholds.g10b_weakfield_max}")
    log(f"G10c (positive metric): min γ={fmt(min(gamma))}  "
        f"threshold=>{thresholds.g10c_gamma_min}")
    log(f"G10d (inward gravity):  mean a_radial={fmt(mean_a_radial)}  "
        f"threshold=>{thresholds.g10d_accel_min}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    if args.write_artifacts:
        cm_csv = out_dir / "covariant_metric.csv"
        write_csv(
            cm_csv,
            ["vertex", "x", "y", "sigma", "Phi", "N", "gamma", "a_x", "a_y", "a_radial"],
            [
                {
                    "vertex": i,
                    "x": fmt(coords[i][0]),
                    "y": fmt(coords[i][1]),
                    "sigma": fmt(sigma[i]),
                    "Phi": fmt(phi[i]),
                    "N": fmt(lapse[i]),
                    "gamma": fmt(gamma[i]),
                    "a_x": fmt(a_x[i]),
                    "a_y": fmt(a_y[i]),
                    "a_radial": fmt(a_radial[i]),
                }
                for i in range(n)
            ],
        )

        mc_csv = out_dir / "metric_checks_covariant.csv"
        write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
            {"gate_id": "G10a", "metric": "min_N",
             "value": fmt(min(lapse)),
             "threshold": f">{thresholds.g10a_lapse_min}",
             "status": "pass" if gate_g10a else "fail"},
            {"gate_id": "G10b", "metric": "max_abs_Phi",
             "value": fmt(max(abs(p) for p in phi)),
             "threshold": f"<{thresholds.g10b_weakfield_max}",
             "status": "pass" if gate_g10b else "fail"},
            {"gate_id": "G10c", "metric": "min_gamma",
             "value": fmt(min(gamma)),
             "threshold": f">{thresholds.g10c_gamma_min}",
             "status": "pass" if gate_g10c else "fail"},
            {"gate_id": "G10d", "metric": "mean_a_radial",
             "value": fmt(mean_a_radial),
             "threshold": f">{thresholds.g10d_accel_min}",
             "status": "pass" if gate_g10d else "fail"},
            {"gate_id": "FINAL", "metric": "decision",
             "value": decision, "threshold": "G10a&G10b&G10c&G10d",
             "status": decision},
        ])

        plot_path = out_dir / "covariant_metric-plot.png"
        if args.plots:
            plot_covariant_metric(plot_path, coords, lapse, a_radial)

        config_path = out_dir / "config_covariant.json"
        config = {
            "script": "run_qng_covariant_metric_v1.py",
            "dataset_id": args.dataset_id,
            "seed": args.seed,
            "phi_scale": args.phi_scale,
            "n_nodes": n,
            "mean_degree": round(mean_degree, 4),
            "sigma_max": round(sigma_max, 6),
            "min_N": round(min(lapse), 6),
            "max_N": round(max(lapse), 6),
            "min_gamma": round(min(gamma), 6),
            "max_gamma": round(max(gamma), 6),
            "mean_a_radial": round(mean_a_radial, 8),
            "run_utc": datetime.utcnow().isoformat() + "Z",
            "elapsed_s": round(elapsed, 3),
            "decision": decision,
        }
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        manifest_path = write_run_manifest(
            out_dir=out_dir,
            script_name="run_qng_covariant_metric_v1.py",
            args_dict={
                "dataset_id": args.dataset_id,
                "seed": args.seed,
                "phi_scale": args.phi_scale,
                "out_dir": str(out_dir),
                "write_artifacts": bool(args.write_artifacts),
                "plots": bool(args.plots),
            },
            gate_id="G10",
            decision=decision,
            elapsed_s=elapsed,
            extras={
                "min_N": round(min(lapse), 6),
                "max_abs_phi": round(max(abs(p) for p in phi), 6),
                "min_gamma": round(min(gamma), 6),
                "mean_a_radial": round(mean_a_radial, 8),
            },
        )

        run_log_path = out_dir / "run-log-covariant.txt"
        run_log_path.write_text("\n".join(log_lines), encoding="utf-8")

        artifact_files = [cm_csv, mc_csv, config_path, manifest_path, run_log_path]
        if args.plots:
            artifact_files.append(plot_path)
        hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
        (out_dir / "artifact-hashes-covariant.json").write_text(
            json.dumps(hashes, indent=2), encoding="utf-8"
        )
        log(f"\nArtifacts written to: {out_dir}")
        run_log_path.write_text("\n".join(log_lines), encoding="utf-8")
    else:
        log("\nArtifacts skipped (--no-write-artifacts).")

    return 0 if gate_g10 else 1


if __name__ == "__main__":
    sys.exit(main())
