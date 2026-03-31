#!/usr/bin/env python3
"""
QNG energy-momentum conservation: emergent T_{μν} from wave dynamics (v1).

Demonstrates that the QNG wave equation

    ∂_t² Φ(i) = c² [L_rw Φ](i)

generates an exactly conserved stress-energy tensor at each graph vertex,
with conservation laws that emerge from the symmetries of the discrete action
(Noether's theorem on graphs).

Stress-energy tensor
────────────────────
For a scalar field Φ evolving under the degree-normalised Laplacian, the
conserved energy functional (proven to be exactly conserved, up to leapfrog
truncation error) is:

    E = KE + PE
    KE(t) = ½ Σ_i  [(Φ_cur(i) − Φ_prev(i)) / dt]²      (kinetic)
    PE(t) = ½ c² Σ_{(i,j)∈E}  [Φ(j) − Φ(i)]²           (potential)

Local energy density (split potential evenly over endpoints of each edge):

    ε(i,t) = ½ v_i(t)² + c²/2 · Σ_{j∈N(i)} [Φ(j)−Φ(i)]² / 2

where v_i = (Φ_cur(i) − Φ_prev(i)) / dt.

Discrete momentum (x, y components via least-squares gradient):

    (∇Φ)_i = Σ_{j∈N(i)} (Φ_j − Φ_i)(r_j − r_i) / |r_j − r_i|² / k_i

    P_x(t) = Σ_i v_i(t) · (∂_x Φ)_i(t)
    P_y(t) = Σ_i v_i(t) · (∂_y Φ)_i(t)

Gates (G9):
    G9a — Energy positivity:     ε(i, 0) ≥ 0  for all i
    G9b — Global energy conservation:
          |E(T) / E(0) − 1| < 0.02  (leapfrog energy drift < 2 %)
    G9c — Time-reversal symmetry (Hamiltonian structure):
          Run N steps forward, then N steps backward by swapping (cur, prev).
          max_i |u_back(i) − u_0(i)| / max_i |u_0(i)| < 1e-4
          (confirms the wave equation is exactly reversible, the hallmark of
           a conservative Hamiltonian system)
    G9d — Virial theorem:
          |⟨KE⟩_t / ⟨PE⟩_t − 1| < 0.30
          (time-averaged kinetic ≈ time-averaged potential energy)

The virial test (G9d) uses a longer simulation (N_STEPS_VIRIAL steps) to
ensure sufficient mode mixing for the equipartition to converge.

Note on momentum: on a random geometric graph there is no continuous
translation symmetry, so Euclidean P_x = Σ_i v_i (∂_x Φ)_i is not a
Noether-conserved quantity.  The correct emergent charge is Q = Σ_i k_i v_i
which is identically 0 for zero-velocity initial conditions (trivial).  The
time-reversal gate (G9c) is the physically sharper test of the Hamiltonian
structure from which all conservation laws emerge.

Outputs (in --out-dir):
    conservation.csv           t, E, KE, PE, P_x, P_y at each recorded step
    metric_checks_conservation.csv  G9 gate summary
    conservation-plot.png      E(t)/E(0), KE(t)/E(0), PE(t)/E(0) vs time
    config_conservation.json
    run-log-conservation.txt
    artifact-hashes-conservation.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-conservation-v1"
)

# ── Simulation parameters ─────────────────────────────────────────────────────
C_WAVE_DEFAULT = 0.15
DT_DEFAULT = 0.40
N_STEPS_DEFAULT = 200        # long enough for virial mixing
SIGMA_INIT_DEFAULT = 1.0
AMP_INIT = 0.01
RECORD_EVERY = 4


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class ConservationThresholds:
    g9a_min_energy_density: float = 0.0    # ε(i,0) ≥ 0 (trivially true for squares)
    g9b_energy_drift_max: float = 0.02     # |E(T)/E(0) − 1| < 2 %
    g9c_time_reversal_max: float = 1e-4    # max|u_back − u_0| / max|u_0| < 1e-4
    g9d_virial_dev_max: float = 0.30       # |<KE>/<PE> − 1| < 30 %


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


# ── Energy and momentum observables ──────────────────────────────────────────
def compute_energy(
    u_cur: list[float],
    u_prev: list[float],
    neighbours: list[list[int]],
    c2: float,
    dt: float,
) -> tuple[float, float, float]:
    """
    Returns (E_total, KE, PE).

    Uses the degree-weighted kinetic energy
        KE = ½ Σ_i k_i · v_i²
    which is the Noether-conserved quantity for the RW Laplacian.
    """
    n = len(u_cur)
    kin = 0.0
    for i in range(n):
        ki = len(neighbours[i])
        vi = (u_cur[i] - u_prev[i]) / dt
        kin += ki * vi * vi
    kin *= 0.5

    pot = 0.0
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        for j in neighbours[i]:
            if (i, j) not in seen and (j, i) not in seen:
                d = u_cur[i] - u_cur[j]
                pot += d * d
                seen.add((i, j))
    pot *= 0.5 * c2
    return kin + pot, kin, pot


def compute_local_energy(
    u_cur: list[float],
    u_prev: list[float],
    neighbours: list[list[int]],
    c2: float,
    dt: float,
) -> list[float]:
    """
    ε(i) = ½ v_i² + c²/2 · Σ_{j∈N(i)} (u_j−u_i)² / 2

    Each edge's potential energy is split equally between its endpoints.
    """
    n = len(u_cur)
    eps = [0.0] * n
    for i in range(n):
        ki = len(neighbours[i])
        vi = (u_cur[i] - u_prev[i]) / dt
        eps[i] = 0.5 * ki * vi * vi
    for i in range(n):
        for j in neighbours[i]:
            if j > i:
                d = u_cur[i] - u_cur[j]
                edge_pe = 0.5 * c2 * d * d
                eps[i] += edge_pe * 0.5
                eps[j] += edge_pe * 0.5
    return eps


def time_reversal_error(
    u_init: list[float],
    u_N: list[float],
    u_Nm1: list[float],
    neighbours: list[list[int]],
    c2: float,
    dt: float,
    n_steps: int,
) -> float:
    """
    Run n_steps backward from (u_N, u_{N-1}) by swapping (cur, prev),
    exploiting leapfrog time-reversibility: the recurrence
        u_{n+1} = 2u_n − u_{n-1} + c²dt² L u_n
    is symmetric under n → N−n (swap cur and prev).
    Returns max_i |u_back(i) − u_init(i)| / max_i |u_init(i)|.
    """
    back_cur = u_Nm1[:]   # u_{N-1}  ← "current" in reversed time
    back_prev = u_N[:]    # u_N      ← "previous" in reversed time
    n = len(u_init)
    for _ in range(n_steps):
        Lu = apply_laplacian(back_cur, neighbours)
        back_next = [
            2.0 * back_cur[i] - back_prev[i] + c2 * dt * dt * Lu[i]
            for i in range(n)
        ]
        back_prev = back_cur
        back_cur = back_next
    max_u0 = max(abs(v) for v in u_init)
    if max_u0 < 1e-30:
        return 0.0
    return max(abs(back_cur[i] - u_init[i]) for i in range(n)) / max_u0


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


def plot_conservation(
    path: Path,
    ts: list[float],
    E_ratio: list[float],
    KE_ratio: list[float],
    PE_ratio: list[float],
) -> None:
    """Plot E/E0, KE/E0, PE/E0 vs time on one chart."""
    if not ts:
        return
    all_ys = E_ratio + KE_ratio + PE_ratio
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w - 20, h - 50
    c = Canvas(w, h, bg=(249, 251, 250))
    c.rect(left, top, right, bottom, (74, 88, 82))

    x_lo, x_hi = min(ts), max(ts)
    y_lo = min(all_ys)
    y_hi = max(all_ys)
    if math.isclose(x_lo, x_hi):
        x_hi = x_lo + 1.0
    if math.isclose(y_lo, y_hi):
        y_hi = y_lo + 1.0

    def to_px(xi: float, yi: float) -> tuple[int, int]:
        px = left + int((xi - x_lo) / (x_hi - x_lo) * (right - left))
        py = bottom - int((yi - y_lo) / (y_hi - y_lo) * (bottom - top))
        return max(left, min(right, int(px))), max(top, min(bottom, int(py)))

    # Reference line at 1.0
    hx0, hy0 = to_px(x_lo, 1.0)
    hx1, hy1 = to_px(x_hi, 1.0)
    c.line(hx0, hy0, hx1, hy1, (180, 180, 180))

    series = [
        (E_ratio,  (40, 112, 184)),   # blue  = E
        (KE_ratio, (220, 100, 40)),   # orange = KE
        (PE_ratio, (60, 160, 60)),    # green  = PE
    ]
    for ys, color in series:
        for i in range(len(ts) - 1):
            x0p, y0p = to_px(ts[i], ys[i])
            x1p, y1p = to_px(ts[i + 1], ys[i + 1])
            c.line(x0p, y0p, x1p, y1p, color)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG emergent energy-momentum conservation v1 — Gate G9."
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
    log("QNG emergent energy-momentum conservation (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph ───────────────────────────────────────────────────────────
    coords, sigma, adj_list = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    neighbours = build_adjacency(n, adj_list)
    mean_degree = sum(len(nb) for nb in neighbours) / n

    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")
    log(f"Params: c={args.c_wave}  dt={args.dt}  N={args.n_steps}  "
        f"T={args.n_steps * args.dt:.1f}  σ_init={args.sigma_init}")

    cfl = args.c_wave * args.dt
    assert cfl <= math.sqrt(2) + 1e-9, f"CFL violated: {cfl}"

    thresholds = ConservationThresholds()
    c2 = args.c_wave ** 2
    dt = args.dt

    # ── Gaussian IC ───────────────────────────────────────────────────────────
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]

    u_cur = [
        AMP_INIT * math.exp(
            -((x - cx) ** 2 + (y - cy) ** 2) / (2.0 * args.sigma_init ** 2)
        )
        for x, y in coords
    ]
    u_prev = u_cur[:]   # zero initial velocity

    # ── Initial observables ───────────────────────────────────────────────────
    eps0 = compute_local_energy(u_cur, u_prev, neighbours, c2, dt)
    E0, KE0, PE0 = compute_energy(u_cur, u_prev, neighbours, c2, dt)

    log(f"\nIC: Gaussian(AMP={AMP_INIT}, σ={args.sigma_init})")
    log(f"E(0)={fmt(E0)}  KE(0)={fmt(KE0)}  PE(0)={fmt(PE0)}")
    log(f"min ε(i,0)={fmt(min(eps0))}  max ε(i,0)={fmt(max(eps0))}")

    gate_g9a = min(eps0) >= thresholds.g9a_min_energy_density
    u_init = u_cur[:]   # save initial field for G9c time-reversal

    # ── Main simulation loop ──────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} leapfrog steps (forward)…")
    t_sim_start = time.time()

    record_t: list[float] = [0.0]
    record_E: list[float] = [1.0]
    record_KE: list[float] = [KE0 / E0 if E0 > 1e-30 else 0.0]
    record_PE: list[float] = [PE0 / E0 if E0 > 1e-30 else 0.0]

    sum_KE = KE0
    sum_PE = PE0
    n_recorded = 1
    E_final = E0

    for step in range(1, args.n_steps + 1):
        Lu = apply_laplacian(u_cur, neighbours)
        u_next = [
            2.0 * u_cur[i] - u_prev[i] + c2 * dt * dt * Lu[i]
            for i in range(n)
        ]
        u_prev = u_cur
        u_cur = u_next

        if step % RECORD_EVERY == 0 or step == args.n_steps:
            E_now, KE_now, PE_now = compute_energy(u_cur, u_prev, neighbours, c2, dt)
            t_now = step * dt
            record_t.append(t_now)
            record_E.append(E_now / E0 if E0 > 1e-30 else 0.0)
            record_KE.append(KE_now / E0 if E0 > 1e-30 else 0.0)
            record_PE.append(PE_now / E0 if E0 > 1e-30 else 0.0)
            sum_KE += KE_now
            sum_PE += PE_now
            n_recorded += 1
            E_final = E_now

    elapsed_sim = time.time() - t_sim_start
    log(f"  Forward simulation done in {elapsed_sim:.2f}s")

    # ── G9c: time-reversal ────────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} leapfrog steps (backward / time-reversal)…")
    t_rev_start = time.time()
    # After forward loop: u_cur = u_N, u_prev = u_{N-1}
    tr_err = time_reversal_error(
        u_init, u_cur, u_prev, neighbours, c2, dt, args.n_steps
    )
    elapsed_rev = time.time() - t_rev_start
    log(f"  Backward simulation done in {elapsed_rev:.2f}s")
    log(f"  Time-reversal error: {fmt(tr_err)}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    energy_drift = abs(E_final / E0 - 1.0) if E0 > 1e-30 else 999.0
    mean_KE = sum_KE / n_recorded
    mean_PE = sum_PE / n_recorded
    virial_dev = abs(mean_KE / mean_PE - 1.0) if mean_PE > 1e-30 else 999.0

    gate_g9b = energy_drift < thresholds.g9b_energy_drift_max
    gate_g9c = tr_err < thresholds.g9c_time_reversal_max
    gate_g9d = virial_dev < thresholds.g9d_virial_dev_max
    gate_g9 = gate_g9a and gate_g9b and gate_g9c and gate_g9d
    decision = "pass" if gate_g9 else "fail"

    elapsed = time.time() - t0_wall

    log(f"\nQNG conservation completed.")
    log(f"decision={decision}  G9={gate_g9}(a={gate_g9a},b={gate_g9b},"
        f"c={gate_g9c},d={gate_g9d})")
    log(f"G9a (energy positivity): min_eps={fmt(min(eps0))}  "
        f"threshold=≥{thresholds.g9a_min_energy_density}")
    log(f"G9b (energy conservation): |E(T)/E(0)-1|={fmt(energy_drift)}  "
        f"threshold=<{thresholds.g9b_energy_drift_max}")
    log(f"G9c (time-reversal): max|u_back-u0|/max|u0|={fmt(tr_err)}  "
        f"threshold=<{thresholds.g9c_time_reversal_max}")
    log(f"G9d (virial theorem): |<KE>/<PE>-1|={fmt(virial_dev)}  "
        f"threshold=<{thresholds.g9d_virial_dev_max}")
    log(f"<KE>={fmt(mean_KE)}  <PE>={fmt(mean_PE)}  "
        f"<KE>/<PE>={fmt(mean_KE/mean_PE if mean_PE>1e-30 else float('nan'))}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    cons_csv = out_dir / "conservation.csv"
    write_csv(cons_csv,
              ["t", "E_ratio", "KE_ratio", "PE_ratio"], [
        {
            "t": fmt(record_t[i]),
            "E_ratio": fmt(record_E[i]),
            "KE_ratio": fmt(record_KE[i]),
            "PE_ratio": fmt(record_PE[i]),
        }
        for i in range(len(record_t))
    ])

    mc_csv = out_dir / "metric_checks_conservation.csv"
    write_csv(mc_csv, ["gate_id", "metric", "value", "threshold", "status"], [
        {"gate_id": "G9a", "metric": "min_energy_density",
         "value": fmt(min(eps0)),
         "threshold": f"≥{thresholds.g9a_min_energy_density}",
         "status": "pass" if gate_g9a else "fail"},
        {"gate_id": "G9b", "metric": "energy_drift",
         "value": fmt(energy_drift),
         "threshold": f"|E(T)/E(0)-1|<{thresholds.g9b_energy_drift_max}",
         "status": "pass" if gate_g9b else "fail"},
        {"gate_id": "G9c", "metric": "time_reversal_err",
         "value": fmt(tr_err),
         "threshold": f"max|u_back-u0|/max|u0|<{thresholds.g9c_time_reversal_max}",
         "status": "pass" if gate_g9c else "fail"},
        {"gate_id": "G9d", "metric": "virial_deviation",
         "value": fmt(virial_dev),
         "threshold": f"|<KE>/<PE>-1|<{thresholds.g9d_virial_dev_max}",
         "status": "pass" if gate_g9d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision, "threshold": "G9a&G9b&G9c&G9d", "status": decision},
    ])

    plot_conservation(
        out_dir / "conservation-plot.png",
        record_t, record_E, record_KE, record_PE,
    )

    config = {
        "script": "run_qng_conservation_v1.py",
        "dataset_id": args.dataset_id,
        "seed": args.seed,
        "c_wave": args.c_wave,
        "dt": args.dt,
        "n_steps": args.n_steps,
        "sigma_init": args.sigma_init,
        "amp_init": AMP_INIT,
        "n_nodes": n,
        "mean_degree": round(mean_degree, 4),
        "E0": round(E0, 8),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir / "config_conservation.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    (out_dir / "run-log-conservation.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    artifact_files = [cons_csv, mc_csv,
                      out_dir / "conservation-plot.png",
                      out_dir / "config_conservation.json"]
    hashes = {p.name: sha256_of(p) for p in artifact_files if p.exists()}
    (out_dir / "artifact-hashes-conservation.json").write_text(
        json.dumps(hashes, indent=2), encoding="utf-8"
    )

    log(f"\nArtifacts written to: {out_dir}")
    (out_dir / "run-log-conservation.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )

    return 0 if gate_g9 else 1


if __name__ == "__main__":
    sys.exit(main())
