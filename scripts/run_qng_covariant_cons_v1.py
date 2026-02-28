#!/usr/bin/env python3
"""
QNG emergent covariant conservation: ∇_μ T^{μν} = 0 from wave dynamics (v1).

Demonstrates that on the QNG graph with a non-trivial ADM background metric,
the FLAT-SPACE energy T^{00} is NOT conserved (metric does work on the field),
but the COVARIANT energy-momentum conservation ∇_μ T^{μν} = 0 is restored
by the metric-weighted Noether charge.

Physical statement
──────────────────
The flat-space stress-energy tensor for a scalar field satisfies

    ∂_μ T^{μν} ≠ 0   in curved space (metric is not constant)

but the COVARIANT divergence satisfies

    ∇_μ T^{μν} = 0   (general covariance of field equations)

On the QNG graph this is tested by running the covariant wave equation

    ∂_t² h(i) = α(i) c² [L_rw h](i),    α(i) = N(i)² / γ(i)

and comparing two energy functionals:

    E_flat(t)  = ½ Σ_i k_i v_i² + PE
                 [flat-space measure — NOT conserved by covariant wave]

    E_cov(t)   = ½ Σ_i (k_i / α_i) v_i² + PE
                 [Noether-conserved for covariant wave — the correct T^{00}]

The key emergent phenomenon:
  • E_flat DRIFTS  (∂_μ T^{μν} ≠ 0: metric does work on the flat field)
  • E_cov CONSERVED (∇_μ T^{μν} = 0: covariant conservation holds)
  • Ratio E_flat_drift / E_cov_drift >> 1 (covariant formulation is much better)

Gates (G14):
    G14a — Flat conservation broken:
            |E_flat(T)/E_flat(0) − 1| > 0.01  (metric breaks ∂_μ T^{μν} = 0)
    G14b — Covariant conservation holds:
            |E_cov(T)/E_cov(0) − 1| < 0.02   (∇_μ T^{μν} = 0 confirmed)
    G14c — Metric correction is substantial:
            drift_ratio = E_flat_drift / E_cov_drift > 3.0
            (covariant formulation restores conservation by factor ≥ 3)
    G14d — Covariant Hamiltonian structure:
            time-reversal error with covariant leapfrog < 1e-4

Outputs (in --out-dir):
    covariant_cons.csv          t, E_cov_ratio, E_flat_ratio, metric_factor
    metric_checks_cov_cons.csv  G14 gate summary
    covariant_cons-plot.png     E_flat(t) and E_cov(t) divergence over time
    config_cov_cons.json
    run-log-cov_cons.txt
    artifact-hashes-cov_cons.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-covariant-cons-v1"
)

PHI_SCALE    = 0.10
C_WAVE       = 0.15
DT           = 0.40
N_STEPS      = 400       # longer run to accumulate E_flat drift
SIGMA_INIT   = 1.0
AMP_INIT     = 0.01
RECORD_EVERY = 8


# ── Gate thresholds ───────────────────────────────────────────────────────────
@dataclass
class CovConsThresholds:
    g14a_flat_drift_min: float  = 0.01   # |E_flat drift| > 1%
    g14b_cov_drift_max: float   = 0.02   # |E_cov drift| < 2%
    g14c_drift_ratio_min: float = 3.0    # E_flat_drift / E_cov_drift > 3
    g14d_time_rev_max: float    = 1e-4   # time-reversal < 1e-4


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

    return coords, sigma, [[j for j in m] for m in adj]


def build_adm_metric(
    sigma: list[float], phi_scale: float
) -> list[float]:
    """Returns alpha(i) = N(i)² / γ(i)."""
    sigma_max = max(sigma)
    alpha = []
    for s in sigma:
        phi = -phi_scale * s / sigma_max
        N   = 1.0 + phi
        gam = 1.0 - 2.0 * phi
        alpha.append(N * N / gam)
    return alpha


# ── Laplacian & leapfrog ──────────────────────────────────────────────────────
def apply_laplacian(u: list[float], neighbours: list[list[int]]) -> list[float]:
    n = len(u)
    Lu = [0.0] * n
    for i in range(n):
        nb = neighbours[i]
        ki = len(nb)
        if ki:
            Lu[i] = sum(u[j] - u[i] for j in nb) / ki
    return Lu


def leapfrog_step(
    h_cur: list[float], h_prev: list[float],
    neighbours: list[list[int]], alpha: list[float],
    c2: float, dt: float,
) -> list[float]:
    n = len(h_cur)
    Lu = apply_laplacian(h_cur, neighbours)
    return [2.0*h_cur[i] - h_prev[i] + alpha[i]*c2*dt*dt*Lu[i] for i in range(n)]


# ── Energy observables ────────────────────────────────────────────────────────
def compute_energies(
    h_cur: list[float], h_prev: list[float],
    neighbours: list[list[int]], alpha: list[float],
    c2: float, dt: float,
) -> tuple[float, float]:
    """Returns (E_cov, E_flat)."""
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
    seen: set[tuple[int,int]] = set()
    for i in range(n):
        for j in neighbours[i]:
            if (i,j) not in seen and (j,i) not in seen:
                d = h_cur[i] - h_cur[j]
                pot += d * d
                seen.add((i,j))
    pot *= 0.5 * c2

    return ke_cov + pot, ke_flat + pot


def time_reversal_error(
    u_init: list[float], u_N: list[float], u_Nm1: list[float],
    neighbours: list[list[int]], alpha: list[float],
    c2: float, dt: float, n_steps: int,
) -> float:
    back_cur, back_prev = u_Nm1[:], u_N[:]
    n = len(u_init)
    for _ in range(n_steps):
        Lu = apply_laplacian(back_cur, neighbours)
        back_next = [
            2.0*back_cur[i] - back_prev[i] + alpha[i]*c2*dt*dt*Lu[i]
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
    def __init__(self, w, h, bg=(255,255,255)):
        self.width, self.height = w, h
        self.px = bytearray(w*h*3)
        for i in range(w*h):
            self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]

    def set(self, x, y, c):
        if 0<=x<self.width and 0<=y<self.height:
            i=(y*self.width+x)*3
            self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]

    def line(self, x0,y0,x1,y1,c):
        dx,dy=abs(x1-x0),abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1
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

    def save_png(self, path):
        raw = bytearray()
        for y in range(self.height):
            raw.append(0); raw.extend(self.px[y*self.width*3:(y+1)*self.width*3])
        def chunk(tag,data):
            return struct.pack("!I",len(data))+tag+data+struct.pack("!I",zlib.crc32(tag+data)&0xFFFFFFFF)
        ihdr=struct.pack("!IIBBBBB",self.width,self.height,8,2,0,0,0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b""))


def plot_conservation_comparison(
    path: Path,
    ts: list[float], E_cov: list[float], E_flat: list[float],
) -> None:
    if not ts:
        return
    all_y = E_cov + E_flat
    w,h = 980,480; left,top,right,bottom = 80,30,w-20,h-50
    c = Canvas(w,h,bg=(249,251,250))
    c.rect(left,top,right,bottom,(74,88,82))
    x_lo,x_hi=min(ts),max(ts); y_lo,y_hi=min(all_y),max(all_y)
    if math.isclose(x_lo,x_hi): x_hi=x_lo+1
    if math.isclose(y_lo,y_hi): y_hi=y_lo+1

    def px(xi,yi):
        ppx=left+int((xi-x_lo)/(x_hi-x_lo)*(right-left))
        ppy=bottom-int((yi-y_lo)/(y_hi-y_lo)*(bottom-top))
        return max(left,min(right,ppx)),max(top,min(bottom,ppy))

    x0p,y0p=px(x_lo,1.0); x1p,y1p=px(x_hi,1.0)
    c.line(x0p,y0p,x1p,y1p,(180,180,180))

    for ys,col in [(E_cov,(40,112,184)),(E_flat,(220,100,40))]:
        for i in range(len(ts)-1):
            x0p,y0p=px(ts[i],ys[i]); x1p,y1p=px(ts[i+1],ys[i+1])
            c.line(x0p,y0p,x1p,y1p,col)

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="QNG emergent covariant conservation ∇_μ T^{μν}=0 (v1) — Gate G14."
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
    def log(msg=""):
        print(msg); log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG emergent covariant conservation ∇_μ T^{μν} = 0 (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Build graph and metric ────────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_degree = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_degree:.2f}")

    alpha = build_adm_metric(sigma, args.phi_scale)
    mean_alpha = statistics.mean(alpha)
    log(f"ADM α: mean={fmt(mean_alpha)}  min={fmt(min(alpha))}  max={fmt(max(alpha))}")
    log(f"  Flat/covariant mass ratio 1/α: mean={fmt(statistics.mean(1.0/a for a in alpha))}")

    thresholds = CovConsThresholds()
    c2 = args.c_wave**2
    dt = args.dt

    # ── Initial conditions ────────────────────────────────────────────────────
    centre_idx = max(range(n), key=lambda i: sigma[i])
    cx, cy = coords[centre_idx]
    h_cur  = [AMP_INIT * math.exp(-((coords[i][0]-cx)**2+(coords[i][1]-cy)**2)/(2.0*SIGMA_INIT**2))
              for i in range(n)]
    h_prev = h_cur[:]
    h_init = h_cur[:]

    E_cov0, E_flat0 = compute_energies(h_cur, h_prev, neighbours, alpha, c2, dt)
    log(f"\nIC: AMP={AMP_INIT}  σ_init={SIGMA_INIT}")
    log(f"E_cov(0)={fmt(E_cov0)}  E_flat(0)={fmt(E_flat0)}")
    log(f"Initial ratio E_cov/E_flat = {fmt(E_cov0/E_flat0 if E_flat0>1e-30 else 0.0)}")

    # ── Forward simulation ────────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} covariant leapfrog steps…")
    ts: list[float]         = [0.0]
    rec_E_cov: list[float]  = [1.0]
    rec_E_flat: list[float] = [1.0]
    E_cov_final = E_cov0
    E_flat_final = E_flat0

    t_sim = time.time()
    for step in range(1, args.n_steps + 1):
        h_next = leapfrog_step(h_cur, h_prev, neighbours, alpha, c2, dt)
        h_prev = h_cur
        h_cur  = h_next

        if step % RECORD_EVERY == 0 or step == args.n_steps:
            E_c, E_f = compute_energies(h_cur, h_prev, neighbours, alpha, c2, dt)
            ts.append(step * dt)
            rec_E_cov.append(E_c / E_cov0 if E_cov0 > 1e-30 else 0.0)
            rec_E_flat.append(E_f / E_flat0 if E_flat0 > 1e-30 else 0.0)
            E_cov_final = E_c
            E_flat_final = E_f

    log(f"  Done in {time.time()-t_sim:.2f}s")

    # ── Time-reversal test ────────────────────────────────────────────────────
    log(f"\nRunning {args.n_steps} backward steps…")
    tr_err = time_reversal_error(
        h_init, h_cur, h_prev, neighbours, alpha, c2, dt, args.n_steps
    )
    log(f"  Time-reversal error: {fmt(tr_err)}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    E_flat_drift = abs(E_flat_final / E_flat0 - 1.0) if E_flat0 > 1e-30 else 999.0
    E_cov_drift  = abs(E_cov_final  / E_cov0  - 1.0) if E_cov0  > 1e-30 else 999.0
    drift_ratio  = E_flat_drift / E_cov_drift if E_cov_drift > 1e-10 else float("inf")

    gate_g14a = E_flat_drift >= thresholds.g14a_flat_drift_min
    gate_g14b = E_cov_drift  <  thresholds.g14b_cov_drift_max
    gate_g14c = drift_ratio  >  thresholds.g14c_drift_ratio_min
    gate_g14d = tr_err       <  thresholds.g14d_time_rev_max
    gate_g14  = gate_g14a and gate_g14b and gate_g14c and gate_g14d
    decision  = "pass" if gate_g14 else "fail"

    elapsed = time.time() - t0
    log(f"\nQNG covariant conservation completed.")
    log(f"decision={decision}  G14={gate_g14}"
        f"(a={gate_g14a},b={gate_g14b},c={gate_g14c},d={gate_g14d})")
    log(f"G14a flat broken:   |ΔE_flat/E|={fmt(E_flat_drift)}  "
        f"threshold=≥{thresholds.g14a_flat_drift_min}")
    log(f"G14b cov conserved: |ΔE_cov/E|={fmt(E_cov_drift)}   "
        f"threshold=<{thresholds.g14b_cov_drift_max}")
    log(f"G14c drift ratio:   E_flat/E_cov={fmt(drift_ratio)}  "
        f"threshold=>{thresholds.g14c_drift_ratio_min}")
    log(f"G14d time-rev.:     err={fmt(tr_err)}  "
        f"threshold=<{thresholds.g14d_time_rev_max}")

    # ── Write artifacts ───────────────────────────────────────────────────────
    cc_csv = out_dir / "covariant_cons.csv"
    write_csv(cc_csv, ["t","E_cov_ratio","E_flat_ratio"], [
        {"t":fmt(ts[i]),"E_cov_ratio":fmt(rec_E_cov[i]),"E_flat_ratio":fmt(rec_E_flat[i])}
        for i in range(len(ts))
    ])

    mc_csv = out_dir / "metric_checks_cov_cons.csv"
    write_csv(mc_csv, ["gate_id","metric","value","threshold","status"], [
        {"gate_id":"G14a","metric":"E_flat_drift",
         "value":fmt(E_flat_drift),"threshold":f"≥{thresholds.g14a_flat_drift_min}",
         "status":"pass" if gate_g14a else "fail"},
        {"gate_id":"G14b","metric":"E_cov_drift",
         "value":fmt(E_cov_drift),"threshold":f"<{thresholds.g14b_cov_drift_max}",
         "status":"pass" if gate_g14b else "fail"},
        {"gate_id":"G14c","metric":"drift_ratio",
         "value":fmt(drift_ratio),"threshold":f">{thresholds.g14c_drift_ratio_min}",
         "status":"pass" if gate_g14c else "fail"},
        {"gate_id":"G14d","metric":"time_reversal",
         "value":fmt(tr_err),"threshold":f"<{thresholds.g14d_time_rev_max}",
         "status":"pass" if gate_g14d else "fail"},
        {"gate_id":"FINAL","metric":"decision","value":decision,
         "threshold":"G14a&G14b&G14c&G14d","status":decision},
    ])

    plot_conservation_comparison(out_dir/"covariant_cons-plot.png", ts, rec_E_cov, rec_E_flat)

    config = {
        "script":"run_qng_covariant_cons_v1.py",
        "dataset_id":args.dataset_id,"seed":args.seed,
        "phi_scale":args.phi_scale,"c_wave":args.c_wave,
        "dt":args.dt,"n_steps":args.n_steps,
        "n_nodes":n,"mean_degree":round(mean_degree,4),
        "mean_alpha":round(mean_alpha,6),
        "E_flat_drift":round(E_flat_drift,8),
        "E_cov_drift":round(E_cov_drift,8),
        "drift_ratio":round(drift_ratio,4),
        "tr_err":float(f"{tr_err:.4e}"),
        "run_utc":datetime.utcnow().isoformat()+"Z",
        "elapsed_s":round(elapsed,3),"decision":decision,
    }
    (out_dir/"config_cov_cons.json").write_text(json.dumps(config,indent=2),encoding="utf-8")

    artifact_files=[cc_csv,mc_csv,out_dir/"covariant_cons-plot.png",out_dir/"config_cov_cons.json"]
    (out_dir/"artifact-hashes-cov_cons.json").write_text(
        json.dumps({p.name:sha256_of(p) for p in artifact_files if p.exists()},indent=2),
        encoding="utf-8"
    )
    (out_dir/"run-log-cov_cons.txt").write_text("\n".join(log_lines),encoding="utf-8")
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir/"run-log-cov_cons.txt").write_text("\n".join(log_lines),encoding="utf-8")
    return 0 if gate_g14 else 1


if __name__ == "__main__":
    sys.exit(main())
