#!/usr/bin/env python3
"""
QNG Semiclassical Back-reaction — G20 on Jaccard Informational Graph (v1).

Port al G20 (run_qng_semiclassical_v1.py) pe graful Jaccard coordinate-free.

Diferente față de v1 (k-NN 2D):
  • Graful: Jaccard Informational Graph (n=280, k_init=8, k_conn=8, seed=3401)
  • Fără coordonate 2D (fără ploturi de embedding)
  • Fizica înglobată (eigenmodes, ε_vac, back-reaction) e identică

Gate thresholds: identice cu G20 v1.

Gates (G20):
    G20a — |Σε_vac − E_0|/E_0 < 0.01
    G20b — cv(ε_vac) > 0.05
    G20c — 1e-5 < |δE_0/E_0| < 0.30
    G20d — max(residual) < 0.20

Usage:
    python scripts/run_qng_g20_jaccard_v1.py
    python scripts/run_qng_g20_jaccard_v1.py --seed 4999
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g20-jaccard-v1"
)

M_EFF_SQ    = 0.014
N_MODES     = 20
N_ITER_POW  = 350
LAMBDA_BACK = 0.05


@dataclass
class SemiThresholds:
    g20a_energy_tol:   float = 0.01
    g20b_cv_min:       float = 0.05
    g20c_dE_lo:        float = 1e-5
    g20c_dE_hi:        float = 0.30
    g20d_residual_max: float = 0.20


# ── Utilities ──────────────────────────────────────────────────────────────────

def fmt(v: float) -> str:
    if math.isnan(v):  return "nan"
    if math.isinf(v):  return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def write_csv(path: Path, fieldnames: list, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# ── Jaccard Graph ──────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter/union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Spectral decomposition ────────────────────────────────────────────────────

def _dot(u, v):   return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):     return math.sqrt(_dot(v, v))

def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w

def _apply_rw(f, neighbours):
    return [(sum(f[j] for j in nb)/len(nb)) if nb else 0. for nb in neighbours]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs=[]; mus=[]
    for _ in range(n_modes):
        v = [rng.gauss(0., 1.) for _ in range(n)]
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
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Vacuum energy density ─────────────────────────────────────────────────────

def compute_epsilon_vac(vecs_active, omegas, n):
    K = len(omegas)
    eps = [0.] * n
    for k in range(K):
        hw = 0.5 * omegas[k]
        for i in range(n):
            eps[i] += hw * vecs_active[k][i]**2
    return eps


# ── First-order back-reaction ─────────────────────────────────────────────────

def first_order_correction(vecs_active, omegas, f_field, lambda_back):
    K = len(omegas); n = len(f_field)
    d_omega = []; omega1 = []
    for k in range(K):
        f_avg_k = sum(f_field[i] * vecs_active[k][i]**2 for i in range(n))
        dw = (lambda_back / 2.) * omegas[k] * f_avg_k
        d_omega.append(dw); omega1.append(omegas[k] + dw)
    delta_E0 = 0.5 * sum(d_omega)
    return d_omega, omega1, delta_E0


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="G20 Semiclassical — Jaccard Graph (v1)")
    p.add_argument("--n-nodes",    type=int,   default=280)
    p.add_argument("--k-init",     type=int,   default=8)
    p.add_argument("--k-conn",     type=int,   default=8)
    p.add_argument("--seed",       type=int,   default=3401)
    p.add_argument("--n-modes",    type=int,   default=N_MODES)
    p.add_argument("--n-iter",     type=int,   default=N_ITER_POW)
    p.add_argument("--lambda-back",type=float, default=LAMBDA_BACK)
    p.add_argument("--m-eff-sq",   type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",    default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    def log(msg=""):
        try:
            print(msg)
        except UnicodeEncodeError:
            print(str(msg).encode("ascii", "replace").decode("ascii"))
        lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG Semiclassical Back-reaction — G20 on Jaccard Graph (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log(f"Graph: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"λ_back={args.lambda_back}  m²={args.m_eff_sq}  modes={args.n_modes}")

    # ── Graf ──────────────────────────────────────────────────────────────────
    neighbours = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(neighbours)
    mean_k = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraf construit: n={n}  mean_degree={mean_k:.2f}")

    thr = SemiThresholds()

    # ── Eigenmodes ─────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iter")
    t1 = time.time()
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter,
                                      random.Random(args.seed + 1))
    log(f"  Done in {time.time()-t1:.2f}s  μ_0={fmt(mus[0])}  μ_1={fmt(mus[1])}")
    active = list(range(1, len(mus)))
    K_eff  = len(active)
    mu_act = [mus[k]     for k in active]
    vecs_a = [eigvecs[k] for k in active]
    omegas = [math.sqrt(mu + args.m_eff_sq) for mu in mu_act]
    E0 = 0.5 * sum(omegas)
    log(f"  K_eff={K_eff}  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]  E_0={fmt(E0)}")

    # ── Metric α^(0) ─────────────────────────────────────────────────────────
    degrees = [len(nb) for nb in neighbours]
    alpha0 = [d / mean_k for d in degrees]
    log(f"\n[2] α^(0) = k_i/k̄: min={fmt(min(alpha0))}  max={fmt(max(alpha0))}")

    # ── Vacuum energy ε_vac^(0) ───────────────────────────────────────────────
    log(f"\n[3] ε_vac^(0)(i) = ½ Σ_k ω_k ψ_k(i)²")
    eps_vac0 = compute_epsilon_vac(vecs_a, omegas, n)
    mean_eps = statistics.mean(eps_vac0)
    std_eps  = statistics.stdev(eps_vac0)
    cv_eps   = std_eps / mean_eps if mean_eps > 1e-14 else float("inf")
    E0_check = sum(eps_vac0)
    energy_err = abs(E0_check - E0) / E0
    log(f"  ε_vac: min={fmt(min(eps_vac0))}  max={fmt(max(eps_vac0))}  mean={fmt(mean_eps)}")
    log(f"  cv={fmt(cv_eps)}  Σε_vac={fmt(E0_check)}  E_0={fmt(E0)}")

    # G20a
    log(f"\n[G20a] |Σε_vac − E_0|/E_0 = {fmt(energy_err)}  threshold=<{thr.g20a_energy_tol}")
    gate_g20a = energy_err < thr.g20a_energy_tol
    log(f"  G20a: {'PASS' if gate_g20a else 'FAIL'}")

    # G20b
    log(f"\n[G20b] cv(ε_vac) = {fmt(cv_eps)}  threshold=>{thr.g20b_cv_min}")
    gate_g20b = cv_eps > thr.g20b_cv_min
    log(f"  G20b: {'PASS' if gate_g20b else 'FAIL'}")

    # ── Back-reaction field f(i) ──────────────────────────────────────────────
    f_field = [(eps_vac0[i] - mean_eps) / mean_eps for i in range(n)]
    log(f"\n[4] f(i) = (ε_vac(i)−ē)/ē: min={fmt(min(f_field))}  max={fmt(max(f_field))}")

    # G20c
    log(f"\n[5] First-order correction (λ={args.lambda_back})")
    d_omega, omega1, delta_E0 = first_order_correction(
        vecs_a, omegas, f_field, args.lambda_back
    )
    E0_1 = E0 + delta_E0
    dE_rel = abs(delta_E0) / E0
    log(f"  δE_0={fmt(delta_E0)}  E_0^(1)={fmt(E0_1)}  |δE_0|/E_0={fmt(dE_rel)}")
    log(f"  Analitic: λ/2×cv²={fmt(args.lambda_back/2*cv_eps**2)}")
    log(f"  Threshold G20c: ({thr.g20c_dE_lo}, {thr.g20c_dE_hi})")
    gate_g20c = thr.g20c_dE_lo < dE_rel < thr.g20c_dE_hi
    log(f"  G20c: {'PASS' if gate_g20c else 'FAIL'}")

    # Metric corectat α^(1)
    alpha1 = [alpha0[i] * (1. + args.lambda_back * f_field[i]) for i in range(n)]
    rel_change = [abs(alpha1[i]-alpha0[i])/alpha0[i] for i in range(n)]
    log(f"\n[6] α^(1): max δα/α={fmt(max(rel_change))}  all>0: {all(a>0 for a in alpha1)}")

    # G20d
    log(f"\n[G20d] Self-consistency residual")
    eps_vac1 = compute_epsilon_vac(vecs_a, omega1, n)
    residuals = [abs(eps_vac1[i] - eps_vac0[i]) / mean_eps for i in range(n)]
    max_res  = max(residuals)
    mean_res = statistics.mean(residuals)
    log(f"  |Δε_vac|/ē: mean={fmt(mean_res)}  max={fmt(max_res)}")
    log(f"  Threshold G20d: < {thr.g20d_residual_max}")
    gate_g20d = max_res < thr.g20d_residual_max
    log(f"  G20d: {'PASS' if gate_g20d else 'FAIL'}")

    # ── Decizie ───────────────────────────────────────────────────────────────
    gate_g20 = gate_g20a and gate_g20b and gate_g20c and gate_g20d
    decision = "pass" if gate_g20 else "fail"
    elapsed  = time.time() - t0

    log(f"\n{'='*70}")
    log(f"G20 Jaccard completed in {elapsed:.2f}s")
    log(f"decision={decision}  (a={gate_g20a}, b={gate_g20b}, c={gate_g20c}, d={gate_g20d})")
    log(f"  G20a energy conservation: {fmt(energy_err)}  <{thr.g20a_energy_tol}")
    log(f"  G20b cv(ε_vac):           {fmt(cv_eps)}  >{thr.g20b_cv_min}")
    log(f"  G20c |δE_0|/E_0:          {fmt(dE_rel)}  ∈({thr.g20c_dE_lo},{thr.g20c_dE_hi})")
    log(f"  G20d max(residual):        {fmt(max_res)}  <{thr.g20d_residual_max}")
    log(f"\n  Bucla GR↔QM se închide la ordinul întâi (λ={args.lambda_back}) pe graful Jaccard.")

    # ── Artefacte ─────────────────────────────────────────────────────────────
    write_csv(out_dir / "backreaction_vertices_jaccard.csv",
              ["vertex","degree","alpha0","eps_vac0","f_field","alpha1","eps_vac1","residual"],
              [{"vertex": i, "degree": degrees[i],
                "alpha0": fmt(alpha0[i]), "eps_vac0": fmt(eps_vac0[i]),
                "f_field": fmt(f_field[i]), "alpha1": fmt(alpha1[i]),
                "eps_vac1": fmt(eps_vac1[i]), "residual": fmt(residuals[i])}
               for i in range(n)])

    write_csv(out_dir / "backreaction_modes_jaccard.csv",
              ["mode_k","mu_k","omega_k0","delta_omega_k","omega_k1"],
              [{"mode_k": k+1, "mu_k": fmt(mu_act[k]),
                "omega_k0": fmt(omegas[k]), "delta_omega_k": fmt(d_omega[k]),
                "omega_k1": fmt(omega1[k])} for k in range(K_eff)])

    write_csv(out_dir / "metric_checks_g20_jaccard.csv",
              ["gate_id","metric","value","threshold","status"], [
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

    config = {
        "script": "run_qng_g20_jaccard_v1.py",
        "graph": {"n": args.n_nodes, "k_init": args.k_init,
                  "k_conn": args.k_conn, "seed": args.seed},
        "mean_degree": round(mean_k, 4), "K_eff": K_eff,
        "m_eff_sq": args.m_eff_sq, "lambda_back": args.lambda_back,
        "E0": round(E0, 8), "E0_corrected": round(E0_1, 8),
        "delta_E0": round(delta_E0, 12), "dE0_rel": round(dE_rel, 10),
        "energy_err": round(energy_err, 12),
        "cv_eps_vac": round(cv_eps, 6), "max_residual": round(max_res, 10),
        "decision": decision,
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "elapsed_s": round(elapsed, 3),
    }
    (out_dir / "config_g20_jaccard.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    (out_dir / "run-log-g20-jaccard.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    log(f"\nArtefacte: {out_dir}")

    return 0 if gate_g20 else 1


if __name__ == "__main__":
    sys.exit(main())
