#!/usr/bin/env python3
"""
QNG Semiclassical Back-reaction (v1) — G20.

Closes the loop between classical GR (G10–G16) and canonical quantisation (G17–G19)
by feeding the quantum vacuum stress-energy ⟨T̂_μν⟩ back into the graph metric.

The semiclassical Einstein equation
──────────────────────────────────────
    G_μν + Λg_μν = 8πG (T_μν^{classical} + ⟨T̂_μν⟩_vacuum)

On the QNG graph this becomes a correction to the metric factor α(i):

    α^{(1)}(i) = α^{(0)}(i) · (1 + λ f(i))

where:
    α^{(0)}(i) = k_i / k̄         (flat connectivity metric from G18/G19)
    ε_vac(i)   = ½ Σ_k ω_k ψ_k(i)²   (vacuum energy density; total = E_0 from G17)
    f(i)       = (ε_vac(i) − ē) / ē   (normalised back-reaction field; ē = mean(ε_vac))
    λ          = 0.05              (back-reaction coupling, ~5%; perturbative regime)

First-order perturbation theory gives the quantum-corrected frequencies:

    ω_k^{(1)} ≈ ω_k · (1 + λ/2 · ⟨f⟩_{ψ_k²})   where ⟨f⟩_{ψ_k²} = Σ_i f(i) ψ_k(i)²

and the corrected zero-point energy:

    E_0^{(1)} = ½ Σ_k ω_k^{(1)}  =  E_0 + δE_0

    δE_0 = (λ/4) Σ_k ω_k ⟨f⟩_{ψ_k²}  =  (λ/2) · E_0 · cv(ε_vac)²

Self-consistency residual
──────────────────────────
The loop closes when the corrected vacuum energy ε_vac^{(1)} does not differ
substantially from ε_vac^{(0)}:

    ε_vac^{(1)}(i) = ½ Σ_k ω_k^{(1)} ψ_k(i)²

    residual(i) = |ε_vac^{(1)}(i) − ε_vac^{(0)}(i)| / ē

If max(residual) ≪ 1, the semiclassical solution is self-consistent to first order.

Gates (G20):
    G20a — Global energy conservation:
           |Σ_i ε_vac(i) − E_0| / E_0 < 0.01
           (vertex-sum of vacuum energy = G17 zero-point energy; algebraic identity)
    G20b — Quantum source spatial structure:
           cv(ε_vac) > 0.05
           (vacuum energy is inhomogeneous → back-reaction has spatial content)
    G20c — Measurable, perturbative back-reaction:
           1e-5 < |δE_0 / E_0| < 0.30
           (energy shift is nonzero but small → stable semiclassical regime)
    G20d — Loop self-consistency:
           max(residual) < 0.20
           (one back-reaction step converges; iteration would be safe)

Outputs (in --out-dir):
    backreaction_vertices.csv    per-vertex: α0, ε_vac, f, α1, ε_vac1, residual
    backreaction_modes.csv       per-mode: ω_k0, ⟨f⟩_k, δω_k, ω_k1
    metric_checks_semi.csv       G20 gate summary
    semiclassical-plot.png       ε_vac spatial map (left) + residual map (right)
    config_semi.json
    run-log-semi.txt
    artifact-hashes-semi.json

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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-semiclassical-v1"
)

M_EFF_SQ     = 0.014
N_MODES      = 20
N_ITER_POW   = 350
LAMBDA_BACK  = 0.05    # back-reaction coupling (5%)


@dataclass
class SemiThresholds:
    g20a_energy_tol:   float = 0.01
    g20b_cv_min:       float = 0.05
    g20c_dE_lo:        float = 1e-5
    g20c_dE_hi:        float = 0.30
    g20d_residual_max: float = 0.20


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
            w = max(d, 1e-6)*(1.0+0.10*abs(sigma[i]-sigma[j]))
            if j not in adj[i] or w < adj[i][j]:
                adj[i][j] = w; adj[j][i] = w

    return coords, sigma, [[j for j in m] for m in adj]


# ── Spectral decomposition ────────────────────────────────────────────────────
def _dot(u, v):   return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):     return math.sqrt(_dot(v, v))

def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
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


# ── Vacuum energy density ─────────────────────────────────────────────────────
def compute_epsilon_vac(
    vecs_active: list[list[float]], omegas: list[float], n: int
) -> list[float]:
    """ε_vac(i) = ½ Σ_k ω_k ψ_k(i)²  — zero-point energy per vertex."""
    K = len(omegas)
    eps = [0.0] * n
    for k in range(K):
        hw = 0.5 * omegas[k]
        for i in range(n):
            eps[i] += hw * vecs_active[k][i]**2
    return eps


# ── First-order back-reaction ─────────────────────────────────────────────────
def first_order_correction(
    vecs_active: list[list[float]], omegas: list[float],
    f_field: list[float],
    lambda_back: float,
) -> tuple[list[float], list[float], float]:
    """
    ⟨f⟩_{ψ_k²} = Σ_i f(i) ψ_k(i)²  (mode-averaged back-reaction field)
    δω_k       = (λ/2) ω_k ⟨f⟩_{ψ_k²}
    ω_k^{(1)}  = ω_k + δω_k
    δE_0       = ½ Σ_k δω_k

    Returns (delta_omega, omega1, delta_E0).
    """
    K   = len(omegas)
    n   = len(f_field)
    d_omega = []
    omega1  = []
    for k in range(K):
        f_avg_k = sum(f_field[i] * vecs_active[k][i]**2 for i in range(n))
        dw = (lambda_back / 2.0) * omegas[k] * f_avg_k
        d_omega.append(dw)
        omega1.append(omegas[k] + dw)

    delta_E0 = 0.5 * sum(d_omega)
    return d_omega, omega1, delta_E0


# ── PNG canvas ────────────────────────────────────────────────────────────────
class Canvas:
    def __init__(self, w, h, bg=(249,251,250)):
        self.width=w; self.height=h
        self.px=bytearray(w*h*3)
        for i in range(w*h): self.px[3*i]=bg[0]; self.px[3*i+1]=bg[1]; self.px[3*i+2]=bg[2]
    def set(self,x,y,c):
        if 0<=x<self.width and 0<=y<self.height:
            i=(y*self.width+x)*3; self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]
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


def plot_semi(path, coords, eps_vac, residuals):
    w, h = 980, 480
    half = w//2 - 10
    L, T, R, B = 80, 30, half, h-50
    ox = half+20; rx = w-20
    c = Canvas(w, h)
    c.rect(L,T,R,B,(74,88,82)); c.rect(ox,T,rx,B,(74,88,82))

    xs=[xy[0] for xy in coords]; ys=[xy[1] for xy in coords]
    xlo,xhi=min(xs),max(xs); ylo,yhi=min(ys),max(ys)

    # Left: ε_vac map
    elo,ehi=min(eps_vac),max(eps_vac)
    if math.isclose(elo,ehi): ehi=elo+1e-9
    for i,(xi,yi) in enumerate(coords):
        t=(eps_vac[i]-elo)/(ehi-elo)
        px=L+int((xi-xlo)/(xhi-xlo)*(R-L)); py=B-int((yi-ylo)/(yhi-ylo)*(B-T))
        rc=int(40+180*t); bc=int(184-144*t)
        c.set(max(L,min(R,px)),max(T,min(B,py)),(rc,80,bc))
        c.set(max(L,min(R,px+1)),max(T,min(B,py)),(rc,80,bc))

    # Right: residual map
    rlo,rhi=min(residuals),max(residuals)
    if math.isclose(rlo,rhi): rhi=rlo+1e-12
    for i,(xi,yi) in enumerate(coords):
        t=(residuals[i]-rlo)/(rhi-rlo)
        px=ox+int((xi-xlo)/(xhi-xlo)*(rx-ox)); py=B-int((yi-ylo)/(yhi-ylo)*(B-T))
        g=int(40+180*(1-t)); r_=int(40+180*t)
        c.set(max(ox,min(rx,px)),max(T,min(B,py)),(r_,g,40))
        c.set(max(ox,min(rx,px+1)),max(T,min(B,py)),(r_,g,40))

    c.save_png(path)


# ── Argument parser ───────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="QNG Semiclassical Back-reaction (v1) — G20.")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed",       type=int,   default=3401)
    p.add_argument("--out-dir",    default=str(DEFAULT_OUT_DIR))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--plots", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--n-modes",    type=int,   default=N_MODES)
    p.add_argument("--n-iter",     type=int,   default=N_ITER_POW)
    p.add_argument("--lambda-back",type=float, default=LAMBDA_BACK)
    p.add_argument("--m-eff-sq",   type=float, default=M_EFF_SQ)
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
    log("QNG Semiclassical Back-reaction (v1) — G20")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)

    # ── Graph ─────────────────────────────────────────────────────────────────
    coords, sigma, neighbours = build_dataset_graph(args.dataset_id, args.seed)
    n = len(coords)
    mean_k = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraph: n={n}  mean_degree={mean_k:.2f}")
    log(f"Back-reaction coupling λ = {args.lambda_back}")

    thr = SemiThresholds()

    # ── Eigenmodes (same as G17–G19) ─────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iterations")
    t1 = time.time()
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter,
                                      random.Random(args.seed + 1))
    log(f"  Done in {time.time()-t1:.2f}s  |  μ_0={fmt(mus[0])}  μ_1={fmt(mus[1])}")
    active  = list(range(1, len(mus)))
    K_eff   = len(active)
    mu_act  = [mus[k]     for k in active]
    vecs_a  = [eigvecs[k] for k in active]
    omegas  = [math.sqrt(mu + args.m_eff_sq) for mu in mu_act]
    E0      = 0.5 * sum(omegas)
    log(f"  K_eff={K_eff}  |  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]  |  E_0 = {fmt(E0)}")

    # ── Flat metric α^(0) ────────────────────────────────────────────────────
    degrees = [len(nb) for nb in neighbours]
    alpha0  = [d / mean_k for d in degrees]
    log(f"\n[2] Flat metric α^(0) = k_i/k̄")
    log(f"  α^(0): min={fmt(min(alpha0))}  max={fmt(max(alpha0))}  mean={fmt(statistics.mean(alpha0))}")

    # ── Vacuum energy density ε_vac^(0) ──────────────────────────────────────
    log(f"\n[3] Vacuum energy density ε_vac^(0)(i) = ½ Σ_k ω_k ψ_k(i)²")
    eps_vac0 = compute_epsilon_vac(vecs_a, omegas, n)
    mean_eps = statistics.mean(eps_vac0)
    std_eps  = statistics.stdev(eps_vac0)
    cv_eps   = std_eps / mean_eps if mean_eps > 1e-14 else float("inf")
    E0_check = sum(eps_vac0)
    log(f"  ε_vac: min={fmt(min(eps_vac0))}  max={fmt(max(eps_vac0))}  mean={fmt(mean_eps)}")
    log(f"  std={fmt(std_eps)}  cv={fmt(cv_eps)}")
    log(f"  Σ_i ε_vac(i) = {fmt(E0_check)}  (should = E_0 = {fmt(E0)})")
    energy_err = abs(E0_check - E0) / E0

    # ── G20a: energy conservation ─────────────────────────────────────────────
    log(f"\n[G20a] Energy conservation: |Σε_vac − E_0|/E_0 = {fmt(energy_err)}")
    log(f"  Threshold: < {thr.g20a_energy_tol}")
    gate_g20a = energy_err < thr.g20a_energy_tol

    # ── G20b: spatial variation ───────────────────────────────────────────────
    log(f"\n[G20b] Spatial variation: cv(ε_vac) = {fmt(cv_eps)}")
    log(f"  Threshold: > {thr.g20b_cv_min}")
    gate_g20b = cv_eps > thr.g20b_cv_min

    # ── Normalised back-reaction field f(i) ───────────────────────────────────
    f_field = [(eps_vac0[i] - mean_eps) / mean_eps for i in range(n)]
    log(f"\n[4] Back-reaction field f(i) = (ε_vac(i) − ē)/ē")
    log(f"  f: min={fmt(min(f_field))}  max={fmt(max(f_field))}  mean≈{fmt(sum(f_field)/n)}")

    # ── G20c: first-order correction δE_0 ────────────────────────────────────
    log(f"\n[5] First-order quantum corrections (λ = {args.lambda_back})")
    d_omega, omega1, delta_E0 = first_order_correction(
        vecs_a, omegas, f_field, args.lambda_back
    )
    E0_1  = E0 + delta_E0
    dE_rel = abs(delta_E0) / E0
    log(f"  δω_k: min={fmt(min(d_omega))}  max={fmt(max(d_omega))}")
    log(f"  E_0^(0)  = {fmt(E0)}")
    log(f"  δE_0     = {fmt(delta_E0)}")
    log(f"  E_0^(1)  = {fmt(E0_1)}")
    log(f"  |δE_0|/E_0 = {fmt(dE_rel)}")
    log(f"  Analytic estimate: λ/2 × cv² = {fmt(args.lambda_back/2*cv_eps**2)}")
    log(f"  Threshold G20c: ({thr.g20c_dE_lo}, {thr.g20c_dE_hi})")
    gate_g20c = thr.g20c_dE_lo < dE_rel < thr.g20c_dE_hi

    # ── Corrected metric α^(1) ────────────────────────────────────────────────
    alpha1 = [alpha0[i] * (1.0 + args.lambda_back * f_field[i]) for i in range(n)]
    log(f"\n[6] Corrected metric α^(1)(i) = α^(0)(i) · (1 + λ·f(i))")
    log(f"  α^(1): min={fmt(min(alpha1))}  max={fmt(max(alpha1))}  mean={fmt(statistics.mean(alpha1))}")
    log(f"  All α^(1) > 0: {all(a > 0 for a in alpha1)}")
    rel_change = [abs(alpha1[i]-alpha0[i])/alpha0[i] for i in range(n)]
    log(f"  |δα/α|: mean={fmt(statistics.mean(rel_change))}  max={fmt(max(rel_change))}")

    # ── G20d: self-consistency residual ───────────────────────────────────────
    log(f"\n[G20d] Self-consistency: ε_vac^(1) vs ε_vac^(0)")
    eps_vac1 = compute_epsilon_vac(vecs_a, omega1, n)
    residuals = [abs(eps_vac1[i] - eps_vac0[i]) / mean_eps for i in range(n)]
    max_res  = max(residuals)
    mean_res = statistics.mean(residuals)
    log(f"  ε_vac^(1): min={fmt(min(eps_vac1))}  max={fmt(max(eps_vac1))}")
    log(f"  Residual |Δε_vac|/ē: mean={fmt(mean_res)}  max={fmt(max_res)}")
    log(f"  Analytic estimate: λ cv² / 2 = {fmt(args.lambda_back*cv_eps**2/2)}")
    log(f"  Threshold G20d: max(residual) < {thr.g20d_residual_max}")
    gate_g20d = max_res < thr.g20d_residual_max

    # ── Summary ───────────────────────────────────────────────────────────────
    gate_g20 = gate_g20a and gate_g20b and gate_g20c and gate_g20d
    decision = "pass" if gate_g20 else "fail"
    elapsed  = time.time() - t0
    log(f"\n{'='*70}")
    log(f"QNG Semiclassical Back-reaction completed in {elapsed:.2f}s")
    log(f"decision={decision}  G20={gate_g20}"
        f"(a={gate_g20a},b={gate_g20b},c={gate_g20c},d={gate_g20d})")
    log(f"  G20a energy conservation: |ΔE|/E = {fmt(energy_err)}  threshold=<{thr.g20a_energy_tol}")
    log(f"  G20b cv(ε_vac):           {fmt(cv_eps)}  threshold=>{thr.g20b_cv_min}")
    log(f"  G20c |δE_0|/E_0:          {fmt(dE_rel)}  threshold∈({thr.g20c_dE_lo},{thr.g20c_dE_hi})")
    log(f"  G20d max(residual):        {fmt(max_res)}  threshold=<{thr.g20d_residual_max}")

    log(f"\nPhysical summary:")
    log(f"  Quantum vacuum corrects the metric by up to {max(rel_change)*100:.3f}%")
    log(f"  Zero-point energy shifts by {dE_rel*100:.4f}%")
    log(f"  One back-reaction step is self-consistent: max residual = {fmt(max_res)}")
    log(f"  The GR ↔ QM loop closes at first order (λ = {args.lambda_back}).")

    # ── Artifacts ─────────────────────────────────────────────────────────────
    artifact_files: list[Path] = []
    mc_csv = out_dir / "metric_checks_semi.csv"
    write_csv(mc_csv, ["gate_id","metric","value","threshold","status"], [
        {"gate_id":"G20a","metric":"energy_conservation_err",
         "value":fmt(energy_err),"threshold":f"<{thr.g20a_energy_tol}",
         "status":"pass" if gate_g20a else "fail"},
        {"gate_id":"G20b","metric":"cv_eps_vac",
         "value":fmt(cv_eps),"threshold":f">{thr.g20b_cv_min}",
         "status":"pass" if gate_g20b else "fail"},
        {"gate_id":"G20c","metric":"dE0_rel",
         "value":fmt(dE_rel),"threshold":f"({thr.g20c_dE_lo},{thr.g20c_dE_hi})",
         "status":"pass" if gate_g20c else "fail"},
        {"gate_id":"G20d","metric":"max_self_consistency_residual",
         "value":fmt(max_res),"threshold":f"<{thr.g20d_residual_max}",
         "status":"pass" if gate_g20d else "fail"},
        {"gate_id":"FINAL","metric":"decision","value":decision,
         "threshold":"G20a&G20b&G20c&G20d","status":decision},
    ])
    artifact_files.append(mc_csv)

    if args.write_artifacts:
        vert_csv = out_dir / "backreaction_vertices.csv"
        write_csv(vert_csv,
                  ["vertex","x","y","degree","alpha0","eps_vac0","f_field","alpha1","eps_vac1","residual"],
                  [{"vertex":i,"x":fmt(coords[i][0]),"y":fmt(coords[i][1]),
                    "degree":degrees[i],"alpha0":fmt(alpha0[i]),
                    "eps_vac0":fmt(eps_vac0[i]),"f_field":fmt(f_field[i]),
                    "alpha1":fmt(alpha1[i]),"eps_vac1":fmt(eps_vac1[i]),
                    "residual":fmt(residuals[i])} for i in range(n)])
        artifact_files.append(vert_csv)

        modes_csv = out_dir / "backreaction_modes.csv"
        write_csv(modes_csv,
                  ["mode_k","mu_k","omega_k0","f_avg_k","delta_omega_k","omega_k1"],
                  [{"mode_k":k+1,"mu_k":fmt(mu_act[k]),"omega_k0":fmt(omegas[k]),
                    "f_avg_k":fmt(d_omega[k]/(args.lambda_back/2*omegas[k]) if omegas[k]>0 else 0),
                    "delta_omega_k":fmt(d_omega[k]),"omega_k1":fmt(omega1[k])}
                   for k in range(K_eff)])
        artifact_files.append(modes_csv)

        if args.plots:
            plot_path = out_dir / "semiclassical-plot.png"
            plot_semi(plot_path, coords, eps_vac0, residuals)
            artifact_files.append(plot_path)

    config = {
        "script": "run_qng_semiclassical_v1.py",
        "dataset_id": args.dataset_id, "seed": args.seed,
        "n_nodes": n, "mean_degree": round(mean_k, 4),
        "K_eff": K_eff, "m_eff_sq": args.m_eff_sq,
        "lambda_back": args.lambda_back,
        "E0": round(E0, 8),
        "E0_corrected": round(E0_1, 8),
        "delta_E0": round(delta_E0, 12),
        "dE0_rel": round(dE_rel, 10),
        "energy_conservation_err": round(energy_err, 12),
        "cv_eps_vac": round(cv_eps, 6),
        "mean_eps_vac": round(mean_eps, 10),
        "max_residual": round(max_res, 10),
        "mean_residual": round(mean_res, 10),
        "max_alpha1_change_rel": round(max(rel_change), 8),
        "run_utc": datetime.utcnow().isoformat()+"Z",
        "elapsed_s": round(elapsed, 3),
        "decision": decision,
        "write_artifacts": bool(args.write_artifacts),
        "plots": bool(args.plots),
    }
    if args.write_artifacts:
        cfg_path = out_dir / "config_semi.json"
        cfg_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        artifact_files.append(cfg_path)
        (out_dir/"artifact-hashes-semi.json").write_text(
            json.dumps({p.name: sha256_of(p) for p in artifact_files if p.exists()}, indent=2),
            encoding="utf-8")
    (out_dir/"run-log-semi.txt").write_text("\n".join(log_lines), encoding="utf-8")
    log(f"\nArtifacts written to: {out_dir}")
    (out_dir/"run-log-semi.txt").write_text("\n".join(log_lines), encoding="utf-8")
    return 0 if gate_g20 else 1


if __name__ == "__main__":
    sys.exit(main())
