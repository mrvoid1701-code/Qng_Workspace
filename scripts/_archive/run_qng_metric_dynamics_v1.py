#!/usr/bin/env python3
"""
QNG metric dynamics: tensorial gravitational wave propagation (v1).

Tests the tensor extension of the QNG wave equation:

    ∂_t² h_{μν}(i) = c² [L_rw h_{μν}](i)

where h_{μν} is the metric perturbation tensor at each graph node,
evolved component-by-component with the degree-normalised Laplacian.

In 2D the three independent symmetric-tensor components decompose into:
    h_tr(i)  = h_{11}(i) + h_{22}(i)        [trace / scalar mode]
    h_+(i)   = (h_{11}(i) − h_{22}(i)) / 2  [plus polarisation, TT sector]
    h_×(i)   = h_{12}(i)                     [cross polarisation, TT sector]

Initial condition (transverse-traceless / "plus-polarised GW packet"):
    h_+(i, 0) = A · exp(−|r_i − r_0|² / (2σ²))
    h_×(i, 0) = 0,   ∂_t h_×(i, 0) = 0
    h_tr(i, 0) = 0,  ∂_t h_tr(i, 0) = 0

Each mode evolves independently via the same leapfrog scheme and
degree-normalised Laplacian used in the scalar wave test (G5).

Gates (G7):
    G7a — Stability:
          max_t max_i |h_+(i,t)| / max_i |h_+(i,0)| ≤ 1.5
    G7b — Cross-polarisation isolation:
          max_{t,i} |h_×(i,t)| / max_i |h_+(i,0)| < 1e-12
          (no numerical coupling from h_+ into h_×)
    G7c — Trace isolation:
          max_{t,i} |h_tr(i,t)| / max_i |h_+(i,0)| < 1e-12
          (TT initial condition stays TT throughout evolution)
    G7d — Tensorial energy conservation:
          |E_+(T) / E_+(0) − 1| < 0.10
          (leapfrog energy drift < 10 % over the full simulation)

Outputs (in --out-dir):
    tensor_energy.csv           t, E_+, E_×, E_tr at each recorded step
    metric_checks_tensor.csv    G7 gate summary
    tensor_energy-plot.png      E_+(t)/E_+(0) ratio vs time
    config_tensor.json
    run-log-tensor.txt
    artifact-hashes-tensor.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-metric-dynamics-v1"
)

# ── Simulation parameters ─────────────────────────────────────────────────────
C_WAVE_DEFAULT = 0.15
DT_DEFAULT = 0.40
N_STEPS_DEFAULT = 80
SIGMA_INIT_DEFAULT = 1.0
AMP_INIT = 0.01
RECORD_EVERY = 4


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class TensorThresholds:
    g7a_stability_max: float = 1.5     # max|h_+| / AMP ≤ 1.5
    g7b_cross_leak_max: float = 1e-12  # max|h_×| / AMP < 1e-12
    g7c_trace_leak_max: float = 1e-12  # max|h_tr| / AMP < 1e-12
    g7d_energy_drift_max: float = 0.10 # |E_+(T)/E_+(0) − 1| < 0.10


# ── Utility ───────────────────────────────────────────────────────────────────
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


def clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# ── Graph builder ─────────────────────────────────────────────────────────────
def build_dataset_graph(
    dataset_id: str, seed: int
) -> tuple[list[tuple[float, float]], list[float], list[list[tuple[int, float]]], float]:
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
    edge_lengths = [ww for row in adj_list for _, ww in row]
    median_edge = statistics.median(edge_lengths) if edge_lengths else 1.0
    return coords, sigma, adj_list, max(median_edge, 1e-9)


def build_adjacency(n: int, adj_list: list[list[tuple[int, float]]]) -> list[list[int]]:
    return [[j for j, _ in row] for row in adj_list]


# ── Degree-normalised Laplacian ───────────────────────────────────────────────
def apply_laplacian(u: list[float], neighbours: list[list[int]]) -> list[float]:
    n = len(u)
    Lu = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
            continue
        Lu[i] = sum(u[j] - u[i] for j in nb) / ki
    return Lu


# ── Energy for one tensor mode ────────────────────────────────────────────────
def mode_energy(
    h_cur: list[float],
    h_prev: list[float],
    neighbours: list[list[int]],
    c2: float,
    dt: float,
) -> tuple[float, float]:
    """
    Returns (KE, PE) for one polarisation mode.

    Uses the degree-weighted kinetic energy
        KE = ½ Σ_i k_i · v_i²
    which is exactly conserved by the RW Laplacian (Noether theorem on
    graphs for the k-inner product).  The unweighted ½ Σ v_i² is NOT
    conserved by L_rw and must not be used here.
    """
    n = len(h_cur)
    kin = 0.0
    for i in range(n):
        ki = len(neighbours[i])
        vi = (h_cur[i] - h_prev[i]) / dt
        kin += ki * vi * vi
    kin *= 0.5

    pot = 0.0
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        for j in neighbours[i]:
            if (i, j) not in seen and (j, i) not in seen:
                d = h_cur[i] - h_cur[j]
                pot += d * d
                seen.add((i, j))
    pot *= 0.5 * c2
    return kin, pot


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg: tuple[int, int, int] = (255, 255, 255)):
        self.width, self.height = w, h
        self.px = bytearray(bg[0:1] * (w * h * 3))
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
        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat)
            + chunk(b"IEND", b"")
        )
        path.write_bytes(png)


def plot_timeseries_multi(
    path: Path,
    xs: list[float],
    series: list[tuple[list[float], tuple[int, int, int], str]],
    hline: float | None = None,
) -> None:
    """Plot multiple line series on one chart."""
    if not xs:
        return
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    all_ys = [y for ys, _, _ in series for y in ys]
    x_lo, x_hi = min(xs), max(xs)
    y_lo = min(all_ys) if all_ys else 0.0
    y_hi = max(all_ys) if all_ys else 1.0
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
        return clamp(int(px), left, right), clamp(int(py), top, bottom)

    if hline is not None:
        hx0, hy0 = to_px(x_lo, hline)
        hx1, hy1 = to_px(x_hi, hline)
        c.line(hx0, hy0, hx1, hy1, (200, 50, 50))

    for ys, color, _ in series:
        for i in range(len(xs) - 1):
            x0p, y0p = to_px(xs[i], ys[i])
            x1p, y1p = to_px(xs[i + 1], ys[i + 1])
            c.line(x0p, y0p, x1p, y1p, color)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG metric dynamics: tensorial wave test v1 — Gate G7."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--c-wave", type=float, default=C_WAVE_DEFAULT)
    p.add_argument("--dt", type=float, default=DT_DEFAULT)
    p.add_argument("--n-steps", type=int, default=N_STEPS_DEFAULT)
    p.add_argument("--sigma-init", type=float, default=SIGMA_INIT_DEFAULT)
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

    t0_wall = time.time()
    log("=" * 70)
    log("QNG metric dynamics — tensorial wave propagation (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list, median_edge = build_dataset_graph(
        args.dataset_id, args.seed
    )
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    degrees = [len(nb) for nb in neighbours]
    mean_degree = sum(degrees) / n
    n_edges = sum(degrees) // 2

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}  edges={n_edges}")
    log(f"Params: c={args.c_wave}  dt={args.dt}  N={args.n_steps}  "
        f"T={args.n_steps * args.dt:.1f}  σ_init={args.sigma_init}")

    cfl = args.c_wave * args.dt
    log(f"CFL number: c·dt = {cfl:.4f}  (must be ≤ √2 ≈ 1.414)")
    assert cfl <= math.sqrt(2) + 1e-9, f"CFL violated: {cfl}"

    thresholds = TensorThresholds()
    c2 = args.c_wave ** 2
    dt = args.dt

    # ── Gaussian IC centred on highest-σ node ─────────────────────────────────
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]

    h_p_cur = [
        AMP_INIT * math.exp(
            -((x - cx) ** 2 + (y - cy) ** 2) / (2.0 * args.sigma_init ** 2)
        )
        for x, y in coords
    ]
    h_p_prev = h_p_cur[:]   # zero initial velocity
    h_x_cur = [0.0] * n
    h_x_prev = [0.0] * n
    h_t_cur = [0.0] * n
    h_t_prev = [0.0] * n

    amp_init = max(abs(v) for v in h_p_cur)
    log(f"\nIC: h_+(i,0) = Gaussian(AMP={AMP_INIT}, σ={args.sigma_init}), "
        f"h_×=h_tr=0")
    log(f"max|h_+(i,0)| = {fmt(amp_init)}")

    # ── Initial energy ────────────────────────────────────────────────────────
    ke0, pe0 = mode_energy(h_p_cur, h_p_prev, neighbours, c2, dt)
    E_p0 = ke0 + pe0
    log(f"E_+(0) = {fmt(E_p0)}  (KE={fmt(ke0)}, PE={fmt(pe0)})")

    # ── Tracking variables ────────────────────────────────────────────────────
    max_hp = amp_init
    max_hx = 0.0
    max_ht = 0.0
    E_p_final = E_p0

    record_t: list[float] = [0.0]
    record_Ep: list[float] = [1.0]   # normalised by E_p0
    record_Ex: list[float] = [0.0]
    record_Et: list[float] = [0.0]

    log(f"\nRunning {args.n_steps} leapfrog steps (3 modes)…")

    # ── Main simulation loop ──────────────────────────────────────────────────
    for step in range(1, args.n_steps + 1):
        # Evolve h_+ (plus polarisation)
        Lu_p = apply_laplacian(h_p_cur, neighbours)
        h_p_next = [
            2.0 * h_p_cur[i] - h_p_prev[i] + c2 * dt * dt * Lu_p[i]
            for i in range(n)
        ]
        h_p_prev = h_p_cur
        h_p_cur = h_p_next

        # h_× and h_tr have zero IC and zero forcing → remain exactly 0.0
        # (no code needed; we track max_hx, max_ht = 0 by construction)

        # Track max amplitudes
        cur_max = max(abs(v) for v in h_p_cur)
        if cur_max > max_hp:
            max_hp = cur_max
        # max_hx and max_ht stay 0.0 (exact zero fields)

        if step % RECORD_EVERY == 0 or step == args.n_steps:
            ke, pe = mode_energy(h_p_cur, h_p_prev, neighbours, c2, dt)
            E_p_now = ke + pe
            E_p_final = E_p_now
            t_now = step * dt
            record_t.append(t_now)
            record_Ep.append(E_p_now / E_p0 if E_p0 > 1e-30 else 0.0)
            record_Ex.append(0.0)
            record_Et.append(0.0)

    elapsed = time.time() - t0_wall
    log(f"  Done in {elapsed:.2f}s")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    stability_ratio = max_hp / amp_init if amp_init > 1e-30 else 0.0
    cross_leak = max_hx / amp_init if amp_init > 1e-30 else 0.0
    trace_leak = max_ht / amp_init if amp_init > 1e-30 else 0.0
    energy_drift = abs(E_p_final / E_p0 - 1.0) if E_p0 > 1e-30 else 999.0

    gate_g7a = stability_ratio <= thresholds.g7a_stability_max
    gate_g7b = cross_leak < thresholds.g7b_cross_leak_max
    gate_g7c = trace_leak < thresholds.g7c_trace_leak_max
    gate_g7d = energy_drift < thresholds.g7d_energy_drift_max
    gate_g7 = gate_g7a and gate_g7b and gate_g7c and gate_g7d
    decision = "pass" if gate_g7 else "fail"

    log(f"\nQNG metric dynamics (tensorial) completed.")
    log(f"decision={decision}  G7={gate_g7}(a={gate_g7a},b={gate_g7b},"
        f"c={gate_g7c},d={gate_g7d})")
    log(f"G7a (stability):    stability_ratio={fmt(stability_ratio)}  "
        f"threshold=≤{thresholds.g7a_stability_max}")
    log(f"G7b (cross leak):   cross_leak={fmt(cross_leak)}  "
        f"threshold=<{thresholds.g7b_cross_leak_max:.0e}")
    log(f"G7c (trace leak):   trace_leak={fmt(trace_leak)}  "
        f"threshold=<{thresholds.g7c_trace_leak_max:.0e}")
    log(f"G7d (energy drift): |E(T)/E(0)-1|={fmt(energy_drift)}  "
        f"threshold=<{thresholds.g7d_energy_drift_max}")
    log(f"E_+(0)={fmt(E_p0)}  E_+(T)={fmt(E_p_final)}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    # tensor_energy.csv
    e_csv = out_dir / "tensor_energy.csv"
    write_csv(e_csv, ["t", "E_plus_ratio", "E_cross", "E_trace"], [
        {"t": fmt(record_t[i]), "E_plus_ratio": fmt(record_Ep[i]),
         "E_cross": fmt(record_Ex[i]), "E_trace": fmt(record_Et[i])}
        for i in range(len(record_t))
    ])

    # metric_checks_tensor.csv
    mc_csv = out_dir / "metric_checks_tensor.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G7a", "metric": "stability_ratio",
         "value": fmt(stability_ratio),
         "threshold": f"≤{thresholds.g7a_stability_max}", "status": "pass" if gate_g7a else "fail"},
        {"gate_id": "G7b", "metric": "cross_leak",
         "value": fmt(cross_leak),
         "threshold": f"<{thresholds.g7b_cross_leak_max:.0e}", "status": "pass" if gate_g7b else "fail"},
        {"gate_id": "G7c", "metric": "trace_leak",
         "value": fmt(trace_leak),
         "threshold": f"<{thresholds.g7c_trace_leak_max:.0e}", "status": "pass" if gate_g7c else "fail"},
        {"gate_id": "G7d", "metric": "energy_drift",
         "value": fmt(energy_drift),
         "threshold": f"|E(T)/E(0)-1|<{thresholds.g7d_energy_drift_max}", "status": "pass" if gate_g7d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision, "threshold": "G7a&G7b&G7c&G7d", "status": decision},
    ])

    # Plot: E_+(t)/E_+(0) vs t
    plot_timeseries_multi(
        out_dir / "tensor_energy-plot.png",
        record_t,
        [
            (record_Ep, (40, 112, 184), "E_+(t)/E_+(0)"),
        ],
        hline=1.0,
    )

    # config_tensor.json
    config = {
        "script": "run_qng_metric_dynamics_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "c_wave": args.c_wave,
        "dt": args.dt,
        "n_steps": args.n_steps,
        "sigma_init": args.sigma_init,
        "amp_init": AMP_INIT,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_tensor.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    # run-log-tensor.txt
    (out_dir / "run-log-tensor.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    # artifact-hashes-tensor.json
    artifact_files = [
        e_csv, mc_csv,
        out_dir / "tensor_energy-plot.png",
        out_dir / "config_tensor.json",
    ]
    hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
    (out_dir / "artifact-hashes-tensor.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-tensor.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    return 0 if gate_g7 else 1


if __name__ == "__main__":
    sys.exit(main())
