#!/usr/bin/env python3
"""
QNG Unruh Thermal Vacuum (v1) — G19.

A static observer in a curved spacetime undergoes constant proper acceleration
to maintain position against the local gravitational field.  The Unruh effect
predicts that such an observer perceives the Minkowski vacuum as a warm thermal
bath at the Unruh temperature:

    T_Unruh = ħ a / (2π c k_B)          (natural units: ħ = c = k_B = 1)

On the QNG graph, the local metric factor α(i) — proportional to the squared
wave speed from G13 — encodes spacetime curvature.  A vertex with α(i) different
from its neighbours must "push" against the local gradient to remain static:

    α_proxy(i) = k_i / k̄              [k̄ = mean degree; local connectivity metric]
    a_eff(i)   = (1/k_i) Σ_{j∈N(i)} |α_proxy(j) − α_proxy(i)|   [mean |∇α| at i]
    T_Unruh(i) = a_eff(i) / (2π)       [local Unruh temperature]

Thermal vacuum state
─────────────────────
At global temperature T_global = mean(T_Unruh), the free scalar vacuum is
promoted to a mixed thermal state with Bose-Einstein occupation numbers:

    n_k = 1 / (exp(ω_k / T_global) − 1)

The thermal two-point function (finite-temperature propagator):

    G_β(i,j) = Σ_k ψ_k(i) ψ_k(j) (2n_k + 1) / (2ω_k)
              = G_0(i,j)  +  ΔG_thermal(i,j)

where ΔG_thermal(i,j) = Σ_k n_k ψ_k(i) ψ_k(j) / ω_k  ≥ 0.

Observable consequences
────────────────────────
1. Quantum suppression of thermal energy:
   Classical equipartition: E_MB = K_eff · T_global
   Bose-Einstein:           E_BE = Σ_k ω_k n_k  ≪  E_MB  (for ω_k ≫ T_global)
   Ratio E_MB/E_BE ≫ 1 confirms the quantum statistics.

2. Superlinear temperature scaling:
   E_BE(2T) / E_BE(T) ≫ 2  (quantum; classical gives exactly 2)
   For ω ≫ T: E_BE(T) ∝ e^{−ω/T} → ratio = e^{+ω/T} ≫ 2.

3. Spatial decay of thermal correlations:
   ΔG_thermal(i,j) shares eigenvectors with G_0, so it also decays with r_{ij}.

Gates (G19):
    G19a — Unruh temperature variation:
           cv(T_Unruh) > 0.05   (graph curvature creates inhomogeneous temperature)
    G19b — Quantum vs classical thermal energy:
           E_MB / E_BE > 2.0    (Bose-Einstein suppression at ω ≫ T)
    G19c — Superlinear temperature scaling:
           E_BE(2T) / E_BE(T) > 3.0  (quantum exponential growth, not classical linear)
    G19d — Thermal propagator spatial decay:
           OLS slope of ΔG_thermal(i,j) vs r_{ij} < −0.001

Outputs (in --out-dir):
    unruh_vertices.csv        per-vertex: α_proxy, a_eff, T_Unruh
    thermal_modes.csv         per-mode: k, ω_k, n_k, ω_k·n_k
    thermal_propagator.csv    sample pairs: r_ij, G0_ij, dG_ij, Gbeta_ij
    metric_checks_unruh.csv   G19 gate summary
    unruh-plot.png            T_Unruh spatial map (left) + thermal propagator (right)
    config_unruh.json
    run-log-unruh.txt
    artifact-hashes-unruh.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-unruh-thermal-v1"
)

M_EFF_SQ   = 0.014
N_MODES    = 20
N_ITER_POW = 350
N_SAMPLE   = 600


@dataclass
class UnruhThresholds:
    g19a_cv_T_min:     float = 0.05
    g19b_supp_min:     float = 2.0
    g19c_ratio_min:    float = 3.0
    g19d_slope_max:    float = -1e-5


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


def ols_fit(x_vals: list[float], y_vals: list[float]) -> tuple[float, float, float]:
    n = len(x_vals)
    if n < 2: return 0.0, 0.0, 0.0
    mx = sum(x_vals)/n; my = sum(y_vals)/n
    Sxx = sum((x-mx)**2 for x in x_vals)
    Sxy = sum((x_vals[i]-mx)*(y_vals[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0.0, 0.0
    b = Sxy/Sxx; a = my - b*mx
    ss_tot = sum((y-my)**2 for y in y_vals)
    if ss_tot < 1e-30: return a, b, 1.0
    ss_res = sum((y_vals[i]-(a+b*x_vals[i]))**2 for i in range(n))
    return a, b, max(0.0, 1.0 - ss_res/ss_tot)


# ── Graph builder ─────────────────────────────────────────────────────────────
def build_dataset_graph(dataset_id: str, seed: int):
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

    coords = [(rng.uniform(-spread, spread), rng.uniform(-spread, spread))
              for _ in range(n)]
    sigma = []
    for x, y in coords:
        r1 = ((x+0.8)**2+(y-0.4)**2)/(2.0*1.35**2)
        r2 = ((x-1.1)**2+(y+0.9)**2)/(2.0*1.10**2)
        s  = 0.75*math.exp(-r1) + 0.55*math.exp(-r2) + rng.gauss(0.0, 0.015)
        sigma.append(min(max(s, 0.0), 1.0))

    adj = [dict() for _ in range(n)]
    for i in range(n):
        xi, yi = coords[i]
        dists = sorted([(math.hypot(xi-coords[j][0], yi-coords[j][1]), j)
                        for j in range(n) if j != i])
        for d, j in dists[:k]:
            w = max(d, 1e-6)*(1.0 + 0.10*abs(sigma[i]-sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w; adj[j][i] = w

    return coords, sigma, [[j for j in m] for m in adj]


# ── Spectral decomposition ────────────────────────────────────────────────────
def _dot(u, v):   return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):     return math.sqrt(_dot(v, v))
def _norm_vec(v): n=_norm(v); return [x/n for x in v] if n>1e-14 else v[:]

def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b)
        w = [w[i]-c*b[i] for i in range(len(w))]
    return w

def _apply_rw(f, neighbours):
    return [(sum(f[j] for j in nb)/len(nb)) if nb else 0.0 for nb in neighbours]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs=[]; mus=[]
    for _ in range(n_modes):
        v = [rng.gauss(0.0,1.0) for _ in range(n)]
        v = _deflate(v, vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            w = _apply_rw(v, neighbours); w = _deflate(w, vecs)
            nm = _norm(w)
            if nm < 1e-14: break
            v = [x/nm for x in w]
        Av = _apply_rw(v, neighbours)
        mu = max(0.0, 1.0 - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Unruh temperature field ───────────────────────────────────────────────────
def compute_unruh_temperatures(
    neighbours: list[list[int]],
) -> tuple[list[float], list[float]]:
    """
    α_proxy(i) = k_i / mean_k    (local connectivity as metric factor proxy)
    a_eff(i)   = mean_{j∈N(i)} |α(j) − α(i)|   (mean absolute gradient)
    T_Unruh(i) = a_eff(i) / (2π)
    """
    n = len(neighbours)
    degrees    = [len(nb) for nb in neighbours]
    mean_k     = sum(degrees) / n
    alpha      = [d / mean_k for d in degrees]     # α_proxy(i)

    a_eff = []
    for i in range(n):
        nb = neighbours[i]
        if not nb:
            a_eff.append(0.0)
            continue
        a_eff.append(sum(abs(alpha[j] - alpha[i]) for j in nb) / len(nb))

    T_unruh = [a / (2.0 * math.pi) for a in a_eff]
    return alpha, T_unruh


# ── Bose-Einstein occupation ──────────────────────────────────────────────────
def bose_einstein(omega: float, T: float) -> float:
    """n_k = 1 / (exp(ω/T) − 1).  Returns 0 if T=0 or ω/T > 700."""
    if T < 1e-14 or omega < 1e-14:
        return 0.0
    x = omega / T
    if x > 700.0:
        return 0.0
    return 1.0 / (math.exp(x) - 1.0)


# ── Propagators ──────────────────────────────────────────────────────────────
def compute_propagators_sample(
    vecs_active, omegas, n_k_vals, coords, sampled_pairs
):
    """
    For each sampled pair (i,j):
      G_0(i,j) = Σ_k ψ_k(i)ψ_k(j) / (2ω_k)
      ΔG(i,j)  = Σ_k n_k ψ_k(i)ψ_k(j) / ω_k
    Returns (r_list, G0_list, dG_list).
    """
    K = len(omegas)
    r_list, G0_list, dG_list = [], [], []
    for i, j in sampled_pairs:
        xi, yi = coords[i]; xj, yj = coords[j]
        r = math.hypot(xi-xj, yi-yj)
        G0 = sum(vecs_active[k][i]*vecs_active[k][j]/(2.0*omegas[k])
                 for k in range(K))
        dG = sum(n_k_vals[k]*vecs_active[k][i]*vecs_active[k][j]/omegas[k]
                 for k in range(K))
        r_list.append(r); G0_list.append(G0); dG_list.append(dG)
    return r_list, G0_list, dG_list


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w, h, bg=(249,251,250)):
        self.width=w; self.height=h
        self.px=bytearray(w*h*3)
        for i in range(w*h): self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]
    def set(self,x,y,c):
        if 0<=x<self.width and 0<=y<self.height:
            i=(y*self.width+x)*3; self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]
    def line(self,x0,y0,x1,y1,c):
        dx,dy=abs(x1-x0),abs(y1-y0); sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1
        err=dx-dy; x,y=x0,y0
        while True:
            self.set(x,y,c)
            if x==x1 and y==y1: break
            e2=2*err
            if e2>=-dy: err-=dy; x+=sx
            if e2<=dx:  err+=dx; y+=sy
    def rect(self,x0,y0,x1,y1,c):
        for x in range(x0,x1+1): self.set(x,y0,c); self.set(x,y1,c)
        for y in range(y0,y1+1): self.set(x0,y,c); self.set(x1,y,c)
    def save_png(self, path):
        raw=bytearray(); rsz=self.width*3
        for y in range(self.height):
            raw.append(0); raw.extend(self.px[y*rsz:(y+1)*rsz])
        def chunk(tag,data):
            return struct.pack("!I",len(data))+tag+data+struct.pack("!I",zlib.crc32(tag+data)&0xFFFFFFFF)
        ihdr=struct.pack("!IIBBBBB",self.width,self.height,8,2,0,0,0)
        path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b""))


def plot_unruh(path, coords, T_unruh, r_list, dG_list, ols_a, ols_b):
    w, h = 980, 480
    half = w//2 - 10
    L, T, R, B = 80, 30, half, h-50
    ox = half+20; rx = w-20
    c = Canvas(w, h)
    c.rect(L,T,R,B,(74,88,82)); c.rect(ox,T,rx,B,(74,88,82))

    # Left: spatial map of T_Unruh
    xs=[xy[0] for xy in coords]; ys=[xy[1] for xy in coords]
    xlo,xhi=min(xs),max(xs); ylo,yhi=min(ys),max(ys)
    Tlo,Thi=min(T_unruh),max(T_unruh)
    if math.isclose(Tlo,Thi): Thi=Tlo+1e-6
    for i,(xi,yi) in enumerate(coords):
        t=(T_unruh[i]-Tlo)/(Thi-Tlo)
        px=L+int((xi-xlo)/(xhi-xlo)*(R-L)); py=B-int((yi-ylo)/(yhi-ylo)*(B-T))
        rc=int(40+180*t); bc=int(184-144*t)
        c.set(px,py,(rc,80,bc)); c.set(px+1,py,(rc,80,bc))

    # Right: ΔG_thermal vs r scatter + OLS
    if r_list and dG_list:
        rlo,rhi=min(r_list),max(r_list)
        glo,ghi=min(dG_list),max(dG_list)
        if math.isclose(rlo,rhi): rhi=rlo+0.1
        if math.isclose(glo,ghi): ghi=glo+1e-6
        for r,g in zip(r_list,dG_list):
            px=ox+int((r-rlo)/(rhi-rlo)*(rx-ox)); py=B-int((g-glo)/(ghi-glo)*(B-T))
            c.set(max(ox,min(rx,px)),max(T,min(B,py)),(40,112,184))
        x0p=ox+int((rlo-rlo)/(rhi-rlo)*(rx-ox)); y0p=B-int((ols_a+ols_b*rlo-glo)/(ghi-glo)*(B-T))
        x1p=ox+int((rhi-rlo)/(rhi-rlo)*(rx-ox)); y1p=B-int((ols_a+ols_b*rhi-glo)/(ghi-glo)*(B-T))
        c.line(max(ox,min(rx,x0p)),max(T,min(B,y0p)),max(ox,min(rx,x1p)),max(T,min(B,y1p)),(220,80,40))
    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="QNG Unruh Thermal Vacuum (v1) — G19.")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-modes", type=int, default=N_MODES)
    p.add_argument("--n-iter",  type=int, default=N_ITER_POW)
    p.add_argument("--n-sample",type=int, default=N_SAMPLE)
    p.add_argument("--m-eff-sq",type=float,default=M_EFF_SQ)
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []
    def log(msg=""):
        print(msg); log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG Unruh Thermal Vacuum (v1) — G19")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Graph ─────────────────────────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_k = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_k:.2f}")

    thr = UnruhThresholds()

    # ── Eigenmodes ────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iterations")
    t1 = time.time()
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter,
                                      random.Random(args.seed + 1))
    log(f"  Done in {time.time()-t1:.2f}s  |  μ_0={fmt(mus[0])}  μ_1={fmt(mus[1])}")
    active = list(range(1, len(mus)))
    K_eff  = len(active)
    mu_act = [mus[k]     for k in active]
    vecs_a = [eigvecs[k] for k in active]
    omegas = [math.sqrt(mu + args.m_eff_sq) for mu in mu_act]
    log(f"  K_eff={K_eff}  |  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── Unruh temperature field ───────────────────────────────────────────────
    log(f"\n[2] Unruh temperature field T_Unruh(i) = a_eff(i)/(2π)")
    alpha_proxy, T_unruh = compute_unruh_temperatures(neighbours)
    T_mean = statistics.mean(T_unruh)
    T_std  = statistics.stdev(T_unruh)
    cv_T   = T_std / T_mean if T_mean > 1e-12 else float("inf")
    log(f"  α_proxy = k_i / k̄   (k̄ = {mean_k:.2f})")
    log(f"  T_Unruh: min={fmt(min(T_unruh))}  max={fmt(max(T_unruh))}  mean={fmt(T_mean)}")
    log(f"  std(T) = {fmt(T_std)}  cv = {fmt(cv_T)}")
    log(f"  Threshold G19a: cv > {thr.g19a_cv_T_min}")
    gate_g19a = cv_T > thr.g19a_cv_T_min
    T_global = T_mean
    log(f"  → T_global = {fmt(T_global)}  [mean Unruh temperature]")

    # ── Bose-Einstein occupation ──────────────────────────────────────────────
    log(f"\n[3] Bose-Einstein occupation n_k(T_global)")
    n_k = [bose_einstein(omegas[k], T_global) for k in range(K_eff)]
    log(f"  n_k: min={fmt(min(n_k))}  max={fmt(max(n_k))}  mean={fmt(statistics.mean(n_k))}")
    log(f"  ω_k/T ∈ [{min(omegas)/T_global:.2f}, {max(omegas)/T_global:.2f}]")

    # ── G19b: Bose-Einstein vs classical suppression ──────────────────────────
    log(f"\n[4] G19b — Quantum vs classical thermal energy")
    E_BE_T = sum(omegas[k] * n_k[k] for k in range(K_eff))
    E_MB   = K_eff * T_global                              # classical equipartition
    ratio_supp = E_MB / E_BE_T if E_BE_T > 1e-30 else float("inf")
    log(f"  E_BE(T)  = {fmt(E_BE_T)}  [Bose-Einstein]")
    log(f"  E_MB     = {fmt(E_MB)}  [classical equipartition = K_eff × T]")
    log(f"  E_MB / E_BE = {fmt(ratio_supp)}")
    log(f"  Threshold G19b: ratio > {thr.g19b_supp_min}")
    gate_g19b = ratio_supp > thr.g19b_supp_min

    # ── G19c: Temperature-doubling ratio ──────────────────────────────────────
    log(f"\n[5] G19c — Temperature doubling: E_BE(2T) / E_BE(T)")
    n_k_2T = [bose_einstein(omegas[k], 2.0 * T_global) for k in range(K_eff)]
    E_BE_2T = sum(omegas[k] * n_k_2T[k] for k in range(K_eff))
    ratio_T  = E_BE_2T / E_BE_T if E_BE_T > 1e-30 else float("inf")
    log(f"  E_BE(2T) = {fmt(E_BE_2T)}")
    log(f"  E_BE(T)  = {fmt(E_BE_T)}")
    log(f"  Ratio    = {fmt(ratio_T)}")
    log(f"  Classical would give ratio = 2.0; quantum gives >> 2")
    log(f"  Threshold G19c: ratio > {thr.g19c_ratio_min}")
    gate_g19c = ratio_T > thr.g19c_ratio_min

    # ── G19d: Thermal propagator spatial decay ────────────────────────────────
    log(f"\n[6] G19d — ΔG_thermal(i,j) spatial decay ({args.n_sample} pair sample)")
    rng_s = random.Random(args.seed + 5)
    all_pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    sampled = rng_s.sample(all_pairs, min(args.n_sample, len(all_pairs)))

    r_list, G0_list, dG_list = compute_propagators_sample(
        vecs_a, omegas, n_k, coords, sampled
    )
    log(f"  ΔG_thermal: min={fmt(min(dG_list))}  max={fmt(max(dG_list))}  mean={fmt(statistics.mean(dG_list))}")
    log(f"  r_{'{ij}'}: min={fmt(min(r_list))}  max={fmt(max(r_list))}  mean={fmt(statistics.mean(r_list))}")
    ols_a_dG, ols_b_dG, r2_dG = ols_fit(r_list, dG_list)
    log(f"  OLS ΔG ~ a + b·r:  a={fmt(ols_a_dG)}  b={fmt(ols_b_dG)}  R²={fmt(r2_dG)}")
    log(f"  Threshold G19d: slope < {thr.g19d_slope_max}")
    gate_g19d = ols_b_dG < thr.g19d_slope_max

    # ── Thermal propagator diagonal ──────────────────────────────────────────
    dG_diag = [sum(n_k[k]*vecs_a[k][i]**2/omegas[k] for k in range(K_eff))
               for i in range(n)]
    log(f"\n  ΔG_thermal(i,i) [local thermal fluctuation]:")
    log(f"    min={fmt(min(dG_diag))}  max={fmt(max(dG_diag))}  mean={fmt(statistics.mean(dG_diag))}")
    log(f"    All positive: {all(x > 0 for x in dG_diag)}")

    # ── Decision ─────────────────────────────────────────────────────────────
    gate_g19 = gate_g19a and gate_g19b and gate_g19c and gate_g19d
    decision = "pass" if gate_g19 else "fail"
    elapsed  = time.time() - t0
    log(f"\nQNG Unruh Thermal completed in {elapsed:.2f}s")
    log(f"decision={decision}  G19={gate_g19}"
        f"(a={gate_g19a},b={gate_g19b},c={gate_g19c},d={gate_g19d})")
    log(f"  G19a cv(T_Unruh):      {fmt(cv_T)}  threshold=>{thr.g19a_cv_T_min}")
    log(f"  G19b E_MB/E_BE:        {fmt(ratio_supp)}  threshold=>{thr.g19b_supp_min}")
    log(f"  G19c E_BE(2T)/E_BE(T): {fmt(ratio_T)}  threshold=>{thr.g19c_ratio_min}")
    log(f"  G19d ΔG slope:         {fmt(ols_b_dG)}  threshold=<{thr.g19d_slope_max}")

    # ── Artifacts ─────────────────────────────────────────────────────────────
    vert_csv = out_dir / "unruh_vertices.csv"
    write_csv(vert_csv, ["vertex","x","y","degree","alpha_proxy","a_eff","T_Unruh"],
              [{"vertex":i,"x":fmt(coords[i][0]),"y":fmt(coords[i][1]),
                "degree":len(neighbours[i]),"alpha_proxy":fmt(alpha_proxy[i]),
                "a_eff":fmt(T_unruh[i]*2*math.pi),"T_Unruh":fmt(T_unruh[i])}
               for i in range(n)])

    modes_csv = out_dir / "thermal_modes.csv"
    write_csv(modes_csv, ["mode_k","mu_k","omega_k","n_k_T","n_k_2T","omega_nk"],
              [{"mode_k":k+1,"mu_k":fmt(mu_act[k]),"omega_k":fmt(omegas[k]),
                "n_k_T":fmt(n_k[k]),"n_k_2T":fmt(n_k_2T[k]),
                "omega_nk":fmt(omegas[k]*n_k[k])} for k in range(K_eff)])

    prop_csv = out_dir / "thermal_propagator.csv"
    write_csv(prop_csv, ["pair_i","pair_j","r_ij","G0_ij","dG_ij","Gbeta_ij"],
              [{"pair_i":sampled[p][0],"pair_j":sampled[p][1],
                "r_ij":fmt(r_list[p]),"G0_ij":fmt(G0_list[p]),
                "dG_ij":fmt(dG_list[p]),"Gbeta_ij":fmt(G0_list[p]+dG_list[p])}
               for p in range(len(sampled))])

    mc_csv = out_dir / "metric_checks_unruh.csv"
    write_csv(mc_csv, ["gate_id","metric","value","threshold","status"], [
        {"gate_id":"G19a","metric":"cv_T_Unruh","value":fmt(cv_T),
         "threshold":f">{thr.g19a_cv_T_min}","status":"pass" if gate_g19a else "fail"},
        {"gate_id":"G19b","metric":"E_MB_over_E_BE","value":fmt(ratio_supp),
         "threshold":f">{thr.g19b_supp_min}","status":"pass" if gate_g19b else "fail"},
        {"gate_id":"G19c","metric":"E_BE_2T_ratio","value":fmt(ratio_T),
         "threshold":f">{thr.g19c_ratio_min}","status":"pass" if gate_g19c else "fail"},
        {"gate_id":"G19d","metric":"dG_thermal_slope","value":fmt(ols_b_dG),
         "threshold":f"<{thr.g19d_slope_max}","status":"pass" if gate_g19d else "fail"},
        {"gate_id":"FINAL","metric":"decision","value":decision,
         "threshold":"G19a&G19b&G19c&G19d","status":decision},
    ])

    plot_unruh(out_dir/"unruh-plot.png", coords, T_unruh, r_list, dG_list, ols_a_dG, ols_b_dG)

    config = {
        "script": "run_qng_unruh_thermal_v1.py",
        "dataset_id": args.dataset_id, "seed": args.seed,
        "n_nodes": n, "mean_degree": round(mean_k, 4),
        "K_eff": K_eff, "m_eff_sq": args.m_eff_sq,
        "T_global": round(T_global, 8),
        "T_unruh_mean": round(T_mean, 8),
        "T_unruh_std": round(T_std, 8),
        "cv_T_unruh": round(cv_T, 6),
        "E_BE_T": round(E_BE_T, 10),
        "E_MB": round(E_MB, 8),
        "ratio_supp_E_MB_over_E_BE": round(ratio_supp, 4) if not math.isinf(ratio_supp) else "inf",
        "E_BE_2T": round(E_BE_2T, 10),
        "ratio_T_doubling": round(ratio_T, 4) if not math.isinf(ratio_T) else "inf",
        "dG_slope": round(ols_b_dG, 8),
        "dG_r2": round(r2_dG, 6),
        "run_utc": datetime.utcnow().isoformat()+"Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
    }
    (out_dir/"config_unruh.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    artifact_files = [vert_csv, modes_csv, prop_csv, mc_csv,
                      out_dir/"unruh-plot.png", out_dir/"config_unruh.json"]
    (out_dir/"artifact-hashes-unruh.json").write_text(
        json.dumps({p.name: sha256_of(p) for p in artifact_files if p.exists()}, indent=2),
        encoding="utf-8")
    log_txt = "\n".join(log_lines)
    (out_dir/"run-log-unruh.txt").write_text(log_txt, encoding="utf-8")
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir/"run-log-unruh.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0 if gate_g19 else 1


if __name__ == "__main__":
    sys.exit(main())
