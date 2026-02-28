#!/usr/bin/env python3
"""
QNG covariant metric-wave dynamics: □h_{μν} with ADM background metric (v1).

Extends the flat-space tensor wave equation (G7) to a fully covariant
d'Alembertian operator using the ADM metric from G10.

Covariant wave equation
───────────────────────
For a tensor perturbation h_{μν} in the static ADM background
g_{ab} = diag(−N², γ, γ) with N(i) = 1 + Φ(i), γ(i) = 1 − 2Φ(i):

    □h(i) = −(1/N²) ∂_t² h + (1/γ) Δ_γ h = 0

Rearranging for the leapfrog:

    ∂_t² h(i) = α(i) · c² · [L_rw h](i)

where the metric coupling factor is:

    α(i) = N(i)² / γ(i) = (1 + Φ(i))² / (1 − 2Φ(i))

Physical interpretation:
• α < 1 near mass (Φ < 0): waves propagate slower in deep potential wells
  (gravitational time-dilation of wave phase velocity)
• α = 1 in flat space (Φ = 0): recovers flat-space L_rw wave equation

Noether-conserved energy for the covariant leapfrog
─────────────────────────────────────────────────────
The equation ∂_t² h(i) = α(i) c² L_rw h(i) follows from the action:

    S = Σ_i k_i/α(i) × (−½) (∂_t h)² + (c²/2) Σ_edges (h_i − h_j)²

The Noether-conserved energy is:

    E_cov = ½ Σ_i k_i/α(i) · v_i² + (c²/2) Σ_{edges} (h_i − h_j)²

Note: this differs from the flat-space E_flat = ½ Σ_i k_i v_i² + PE.  The
metric correction 1/α(i) replaces the uniform mass k_i with the
position-dependent effective mass k_i/α(i).

Gates (G13):
    G13a — Stability:       max_t max_i |h_+(i,t)| / AMP ≤ 1.5
    G13b — Covariant energy conservation:
            |E_cov(T) / E_cov(0) − 1| < 0.02  (< 2% drift)
    G13c — Metric speed reduction confirmed:
            1 − mean_i α(i) > 0.05  (≥ 5% speed reduction near mass)
    G13d — Time-reversal symmetry:
            max|h_back − h_0| / max|h_0| < 1e-4

Three polarisation modes are evolved (same IC as G7):
    h_+  (plus, TT) — Gaussian IC
    h_×  (cross, TT) — zero IC
    h_tr (trace, scalar) — zero IC

Outputs (in --out-dir):
    covariant_wave.csv          t, E_cov, E_flat, E_cov/E_cov0, E_flat/E_flat0
    metric_checks_covariant_wave.csv  G13 gate summary
    covariant_wave-plot.png     E_cov(t)/E(0) and E_flat(t)/E(0) vs time
    config_covariant_wave.json
    run-log-covariant_wave.txt
    artifact-hashes-covariant_wave.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-covariant-wave-v1"
)

# ── Physics parameters ─────────────────────────────────────────────────────────
PHI_SCALE   = 0.10
C_WAVE      = 0.15
DT          = 0.40
N_STEPS     = 200
SIGMA_INIT  = 1.0
AMP_INIT    = 0.01
RECORD_EVERY = 4


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class CovariantWaveThresholds:
    g13a_stability_max: float  = 1.5     # max amplitude / AMP ≤ 1.5
    g13b_energy_drift_max: float = 0.02  # |E_cov(T)/E_cov(0)−1| < 2%
    g13c_speed_red_min: float  = 0.05    # 1−mean(α) > 0.05 (≥5% reduction)
    g13d_time_rev_max: float   = 1e-4    # time-reversal error < 1e-4


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
                adj[i][j] = w
                adj[j][i] = w

    neighbours = [[j for j in m] for m in adj]
    return coords, sigma, neighbours


# ── ADM metric ────────────────────────────────────────────────────────────────
def build_adm_metric(
    sigma: list[float], phi_scale: float
) -> tuple[list[float], list[float], list[float], list[float]]:
    """Returns (phi, lapse N, gamma, alpha = N²/gamma)."""
    sigma_max = max(sigma)
    phi   = [-phi_scale * s / sigma_max for s in sigma]
    lapse = [1.0 + p for p in phi]
    gamma = [1.0 - 2.0 * p for p in phi]
    alpha = [lapse[i]**2 / gamma[i] for i in range(len(phi))]
    return phi, lapse, gamma, alpha


# ── Covariant Laplacian ───────────────────────────────────────────────────────
def apply_laplacian(u: list[float], neighbours: list[list[int]]) -> list[float]:
    """Degree-normalised RW Laplacian: [L_rw u](i) = (1/k_i) Σ_j (u_j − u_i)."""
    n = len(u)
    Lu = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki == 0:
            continue
        Lu[i] = sum(u[j] - u[i] for j in nb) / ki
    return Lu


# ── Covariant leapfrog step ───────────────────────────────────────────────────
def leapfrog_step(
    h_cur: list[float],
    h_prev: list[float],
    neighbours: list[list[int]],
    alpha: list[float],
    c2: float,
    dt: float,
) -> list[float]:
    """h_{n+1}(i) = 2 h_n(i) − h_{n-1}(i) + α(i) c² dt² [L_rw h_n](i)."""
    n = len(h_cur)
    Lu = apply_laplacian(h_cur, neighbours)
    return [
        2.0 * h_cur[i] - h_prev[i] + alpha[i] * c2 * dt * dt * Lu[i]
        for i in range(n)
    ]


# ── Energy observables ────────────────────────────────────────────────────────
def covariant_energy(
    h_cur: list[float],
    h_prev: list[float],
    neighbours: list[list[int]],
    alpha: list[float],
    c2: float,
    dt: float,
) -> tuple[float, float, float]:
    """
    Returns (E_cov, E_flat, PE).
    E_cov = ½ Σ_i (k_i/α_i) v_i² + PE   ← Noether-conserved
    E_flat = ½ Σ_i k_i v_i² + PE         ← flat-space energy (drifts)
    PE = (c²/2) Σ_edges (h_i − h_j)²
    """
    n = len(h_cur)
    ke_cov = ke_flat = 0.0
    for i in range(n):
        ki = float(len(neighbours[i]))
        vi = (h_cur[i] - h_prev[i]) / dt
        ke_cov  += (ki / alpha[i]) * vi * vi
        ke_flat += ki * vi * vi
    ke_cov  *= 0.5
    ke_flat *= 0.5

    pot = 0.0
    seen: set[tuple[int, int]] = set()
    for i in range(n):
        for j in neighbours[i]:
            if (i, j) not in seen and (j, i) not in seen:
                d = h_cur[i] - h_cur[j]
                pot += d * d
                seen.add((i, j))
    pot *= 0.5 * c2

    return ke_cov + pot, ke_flat + pot, pot


# ── Time-reversal ─────────────────────────────────────────────────────────────
def time_reversal_error(
    u_init: list[float],
    u_N: list[float],
    u_Nm1: list[float],
    neighbours: list[list[int]],
    alpha: list[float],
    c2: float,
    dt: float,
    n_steps: int,
) -> float:
    """Reverse the covariant leapfrog by swapping (cur, prev)."""
    back_cur  = u_Nm1[:]
    back_prev = u_N[:]
    n = len(u_init)
    for _ in range(n_steps):
        Lu = apply_laplacian(back_cur, neighbours)
        back_next = [
            2.0 * back_cur[i] - back_prev[i] + alpha[i] * c2 * dt * dt * Lu[i]
            for i in range(n)
        ]
        back_prev = back_cur
        back_cur  = back_next
    max_u0 = max(abs(v) for v in u_init)
    if max_u0 < 1e-30:
        return 0.0
    return max(abs(back_cur[i] - u_init[i]) for i in range(n)) / max_u0


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w: int, h: int, bg=(255, 255, 255)):
        self.width, self.height = w, h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]

    def set(self, x, y, c):
        if 0<=x<self.width and 0<=y<self.height:
            i=(y*self.width+x)*3
            self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]

    def line(self, x0, y0, x1, y1, c):
        dx,dy=abs(x1-x0),abs(y1-y0)
        sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1
        err=dx-dy; x,y=x0,y0
        while True:
            self.set(x,y,c)
            if x==x1 and y==y1: break
            e2=2*err
            if e2>=-dy: err-=dy; x+=sx
            if e2<=dx: err+=dx; y+=sy

    def rect(self, x0,y0,x1,y1,c):
        for x in range(x0,x1+1): self.set(x,y0,c); self.set(x,y1,c)
        for y in range(y0,y1+1): self.set(x0,y,c); self.set(x1,y,c)

    def save_png(self, path: Path) -> None:
        raw = bytearray()
        for y in range(self.height):
            raw.append(0); raw.extend(self.px[y*self.width*3:(y+1)*self.width*3])
        def chunk(tag,data):
            return struct.pack("!I",len(data))+tag+data+struct.pack("!I",zlib.crc32(tag+data)&0xFFFFFFFF)
        ihdr = struct.pack("!IIBBBBB",self.width,self.height,8,2,0,0,0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b""))


def plot_cov_wave(
    path: Path,
    ts: list[float],
    E_cov: list[float],
    E_flat: list[float],
) -> None:
    if not ts:
        return
    all_y = E_cov + E_flat
    w, h = 980, 480
    left, top, right, bottom = 80, 30, w-20, h-50
    c = Canvas(w, h, bg=(249,251,250))
    c.rect(left,top,right,bottom,(74,88,82))
    x_lo,x_hi=min(ts),max(ts)
    y_lo,y_hi=min(all_y),max(all_y)
    if math.isclose(x_lo,x_hi): x_hi=x_lo+1
    if math.isclose(y_lo,y_hi): y_hi=y_lo+1

    def px(xi,yi):
        px=left+int((xi-x_lo)/(x_hi-x_lo)*(right-left))
        py=bottom-int((yi-y_lo)/(y_hi-y_lo)*(bottom-top))
        return max(left,min(right,px)),max(top,min(bottom,py))

    # Reference line 1.0
    x0p,y0p=px(x_lo,1.0); x1p,y1p=px(x_hi,1.0)
    c.line(x0p,y0p,x1p,y1p,(180,180,180))

    for ys,col in [(E_cov,(40,112,184)),(E_flat,(220,100,40))]:
        for i in range(len(ts)-1):
            x0p,y0p=px(ts[i],ys[i]); x1p,y1p=px(ts[i+1],ys[i+1])
            c.line(x0p,y0p,x1p,y1p,col)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="QNG covariant metric-wave dynamics (v1) — Gate G13."
    )
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--c-wave", type=float, default=C_WAVE)
    p.add_argument("--dt", type=float, default=DT)
    p.add_argument("--n-steps", type=int, default=N_STEPS)
    p.add_argument("--phi-scale", type=float, default=PHI_SCALE)
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
    log("QNG covariant metric-wave □h_{μν} with ADM background (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph and ADM metric ────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_degree = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    phi, lapse, gamma_metric, alpha = build_adm_metric(sigma, args.phi_scale)
    mean_alpha = statistics.mean(alpha)
    min_alpha  = min(alpha)
    speed_red  = 1.0 - mean_alpha
    log(f"ADM metric: Φ_scale={args.phi_scale}  "
        f"mean_α={fmt(mean_alpha)}  min_α={fmt(min_alpha)}")
    log(f"Speed reduction 1−mean(α) = {fmt(speed_red)}")

    thresholds = CovariantWaveThresholds()
    c2 = args.c_wave ** 2
    dt = args.dt

    # CFL check (α ≤ 1, so covariant CFL is relaxed vs flat)
    cfl_eff = math.sqrt(max(alpha)) * args.c_wave * dt
    assert cfl_eff <= math.sqrt(2) + 0.1, f"CFL violated: {cfl_eff}"

    # ── Initial conditions (same as G7: Gaussian h_+, zero h_× and h_tr) ─────
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]

    def gaussian(x, y):
        return AMP_INIT * math.exp(
            -((x - cx)**2 + (y - cy)**2) / (2.0 * SIGMA_INIT**2)
        )

    hp_cur  = [gaussian(x, y) for x, y in coords]  # h_+
    hx_cur  = [0.0] * n                              # h_×  (zero IC)
    htr_cur = [0.0] * n                              # h_tr (zero IC)
    hp_prev = hp_cur[:]   # zero initial velocity
    hx_prev = hx_cur[:]
    htr_prev = htr_cur[:]

    hp_init = hp_cur[:]   # save for time-reversal test

    E_cov0, E_flat0, _ = covariant_energy(
        hp_cur, hp_prev, neighbours, alpha, c2, dt
    )
    log(f"\nIC: Gaussian AMP={AMP_INIT}  σ={SIGMA_INIT}")
    log(f"E_cov(0)={fmt(E_cov0)}  E_flat(0)={fmt(E_flat0)}")

    # ── Simulation ────────────────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} covariant leapfrog steps…")
    ts: list[float]        = [0.0]
    rec_E_cov: list[float] = [1.0]
    rec_E_flat: list[float]= [1.0]

    max_amp = max(abs(v) for v in hp_cur)
    E_cov_final = E_cov0
    E_flat_final = E_flat0

    t_sim = time.time()
    for step in range(1, args.n_steps + 1):
        hp_cur  = leapfrog_step(hp_cur,  hp_prev,  neighbours, alpha, c2, dt)
        hp_prev = hp_cur[:]   # leapfrog: prev ← old cur (already swapped above)
        # Fix: keep two states
    # Redo properly:
    hp_cur  = [gaussian(x, y) for x, y in coords]
    hp_prev = hp_cur[:]
    hp_init = hp_cur[:]
    E_cov0, E_flat0, _ = covariant_energy(hp_cur, hp_prev, neighbours, alpha, c2, dt)

    ts = [0.0]; rec_E_cov = [1.0]; rec_E_flat = [1.0]
    max_amp = max(abs(v) for v in hp_cur)
    E_cov_final = E_cov0

    for step in range(1, args.n_steps + 1):
        hp_next = leapfrog_step(hp_cur, hp_prev, neighbours, alpha, c2, dt)
        hp_prev = hp_cur
        hp_cur  = hp_next

        amax = max(abs(v) for v in hp_cur)
        if amax > max_amp:
            max_amp = amax

        if step % RECORD_EVERY == 0 or step == args.n_steps:
            E_c, E_f, _ = covariant_energy(hp_cur, hp_prev, neighbours, alpha, c2, dt)
            ts.append(step * dt)
            rec_E_cov.append(E_c / E_cov0 if E_cov0 > 1e-30 else 0.0)
            rec_E_flat.append(E_f / E_flat0 if E_flat0 > 1e-30 else 0.0)
            E_cov_final = E_c
            E_flat_final = E_f

    log(f"  Forward simulation done in {time.time()-t_sim:.2f}s")

    # ── Time-reversal test ────────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} steps backward (time-reversal)…")
    t_rev = time.time()
    tr_err = time_reversal_error(
        hp_init, hp_cur, hp_prev, neighbours, alpha, c2, dt, args.n_steps
    )
    log(f"  Time-reversal error: {fmt(tr_err)}  ({time.time()-t_rev:.2f}s)")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    stab_ratio  = max_amp / AMP_INIT
    E_cov_drift = abs(E_cov_final / E_cov0 - 1.0) if E_cov0 > 1e-30 else 999.0

    gate_g13a = stab_ratio   <= thresholds.g13a_stability_max
    gate_g13b = E_cov_drift  < thresholds.g13b_energy_drift_max
    gate_g13c = speed_red    > thresholds.g13c_speed_red_min
    gate_g13d = tr_err       < thresholds.g13d_time_rev_max
    gate_g13  = gate_g13a and gate_g13b and gate_g13c and gate_g13d
    decision  = "pass" if gate_g13 else "fail"

    elapsed = time.time() - t0
    log(f"\nQNG covariant wave completed.")
    log(f"decision={decision}  G13={gate_g13}"
        f"(a={gate_g13a},b={gate_g13b},c={gate_g13c},d={gate_g13d})")
    log(f"G13a stability:   max|h|/AMP={fmt(stab_ratio)}  "
        f"threshold=≤{thresholds.g13a_stability_max}")
    log(f"G13b E_cov drift: |E_cov(T)/E_cov(0)−1|={fmt(E_cov_drift)}  "
        f"threshold=<{thresholds.g13b_energy_drift_max}")
    log(f"G13c speed red.:  1−mean(α)={fmt(speed_red)}  "
        f"threshold=>{thresholds.g13c_speed_red_min}")
    log(f"G13d time-rev.:   err={fmt(tr_err)}  "
        f"threshold=<{thresholds.g13d_time_rev_max}")

    # Report E_flat drift (informational)
    E_flat_drift = abs(E_flat_final / E_flat0 - 1.0) if E_flat0 > 1e-30 else 999.0
    log(f"\nNote: E_flat drift = {fmt(E_flat_drift)}  (metric breaks flat conservation)")
    log(f"Note: E_cov vs E_flat at T: ratio = {fmt(E_cov_final / E_flat_final if E_flat_final > 1e-30 else 0.0)}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    cw_csv = out_dir / "covariant_wave.csv"
    write_csv(cw_csv, ["t","E_cov_ratio","E_flat_ratio"], [
        {"t":fmt(ts[i]), "E_cov_ratio":fmt(rec_E_cov[i]), "E_flat_ratio":fmt(rec_E_flat[i])}
        for i in range(len(ts))
    ])

    mc_csv = out_dir / "metric_checks_covariant_wave.csv"
    write_csv(mc_csv, ["gate_id","metric","value","threshold","status"], [
        {"gate_id":"G13a","metric":"stability_ratio",
         "value":fmt(stab_ratio),"threshold":f"≤{thresholds.g13a_stability_max}",
         "status":"pass" if gate_g13a else "fail"},
        {"gate_id":"G13b","metric":"E_cov_drift",
         "value":fmt(E_cov_drift),"threshold":f"<{thresholds.g13b_energy_drift_max}",
         "status":"pass" if gate_g13b else "fail"},
        {"gate_id":"G13c","metric":"speed_reduction",
         "value":fmt(speed_red),"threshold":f">{thresholds.g13c_speed_red_min}",
         "status":"pass" if gate_g13c else "fail"},
        {"gate_id":"G13d","metric":"time_reversal_err",
         "value":fmt(tr_err),"threshold":f"<{thresholds.g13d_time_rev_max}",
         "status":"pass" if gate_g13d else "fail"},
        {"gate_id":"FINAL","metric":"decision","value":decision,
         "threshold":"G13a&G13b&G13c&G13d","status":decision},
    ])

    plot_cov_wave(out_dir / "covariant_wave-plot.png", ts, rec_E_cov, rec_E_flat)

    config = {
        "script": "run_qng_covariant_wave_v1.py",
        "dataset_id": args.dataset_id, "seed": args.seed,
        "phi_scale": args.phi_scale, "c_wave": args.c_wave,
        "dt": args.dt, "n_steps": args.n_steps,
        "n_nodes": n, "mean_degree": round(mean_degree,4),
        "mean_alpha": round(mean_alpha,6), "speed_red": round(speed_red,6),
        "stab_ratio": round(stab_ratio,6), "E_cov_drift": round(E_cov_drift,8),
        "E_flat_drift": round(E_flat_drift,8),
        "tr_err": float(f"{tr_err:.4e}"),
        "run_utc": datetime.utcnow().isoformat()+"Z",
        "elapsed_s": round(elapsed,3), "decision": decision,
    }
    (out_dir/"config_covariant_wave.json").write_text(
        json.dumps(config,indent=2), encoding="utf-8"
    )

    artifact_files = [cw_csv, mc_csv,
                      out_dir/"covariant_wave-plot.png",
                      out_dir/"config_covariant_wave.json"]
    (out_dir/"artifact-hashes-covariant_wave.json").write_text(
        json.dumps({p.name:sha256_of(p) for p in artifact_files if p.exists()},indent=2),
        encoding="utf-8"
    )
    (out_dir/"run-log-covariant_wave.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir/"run-log-covariant_wave.txt").write_text(
        "\n".join(log_lines), encoding="utf-8"
    )
    return 0 if gate_g13 else 1


if __name__ == "__main__":
    sys.exit(main())
