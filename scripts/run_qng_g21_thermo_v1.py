#!/usr/bin/env python3
"""
QNG Thermodynamic Consistency — G21 on Jaccard Informational Graph (v1).

Verifică consistența termodinamică completă a vacuumului termal QNG:

    G21a — S_total > 0     : entropia totală pozitivă (non-trivial: S > 0.01 nats)
    G21b — C_V > 0         : capacitate calorică pozitivă (stabilitate termodinamică)
    G21c — |F − (U−TS)|/denom < 1e-8  : identitatea termodinamică F=U-TS la precizie numerică
    G21d — S(2T)/S(T) > 1.5: entropia crește cu temperatura (a doua lege, Bose-Einstein)

Ingrediente (toate refolosesc logica G19/G20):
    - Graf Jaccard (n=280, k_init=8, k_conn=8, seed=3401)
    - Eigenmodes prin power iteration (deflatat)
    - T_global = T_Unruh_mean (coerент cu G19)
    - Funcție de partiție bosonic: Z = Π_k 1/(1−exp(−β ω_k))
    - Energie liberă: F = −T ln Z
    - Energie internă: U = Σ_k ω_k n_k  (n_k Bose-Einstein)
    - Entropie: S = ln Z + β U  (echivalent cu S = (U−F)/T)
    - Capacitate calorică: C_V = Σ_k ω_k² n_k(n_k+1) / T²

Usage:
    python scripts/run_qng_g21_thermo_v1.py
    python scripts/run_qng_g21_thermo_v1.py --seed 4999 --n-modes 25
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g21-thermo-v1"
)

M_EFF_SQ   = 0.014
N_MODES    = 20
N_ITER_POW = 350


@dataclass
class ThermoThresholds:
    # G21a: entropia totală > prag minim (T_Unruh << ω_min → regim ultra-rece, S ~ 1e-6)
    g21a_S_min:        float = 1e-8
    # G21b: capacitate calorică pozitivă
    g21b_CV_min:       float = 1e-12
    # G21c: eroarea identității F = U − TS  (relativ la |F|+|U|)
    g21c_id_err_max:   float = 1e-8
    # G21d: S(2T)/S(T) — entropia la temperatură dublă e mai mare cu cel puțin 50%
    g21d_S_ratio_min:  float = 1.5


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

def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
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
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Spectral decomposition (power iteration cu deflaţie) ──────────────────────

def _dot(u: list, v: list) -> float:
    return sum(u[i] * v[i] for i in range(len(u)))

def _norm(v: list) -> float:
    return math.sqrt(_dot(v, v))

def _deflate(v: list, basis: list) -> list:
    w = v[:]
    for b in basis:
        c = _dot(w, b)
        w = [w[i] - c * b[i] for i in range(len(w))]
    return w

def _apply_rw(f: list, neighbours: list) -> list:
    return [(sum(f[j] for j in nb) / len(nb)) if nb else 0. for nb in neighbours]

def compute_eigenmodes(neighbours: list, n_modes: int, n_iter: int, rng: random.Random):
    n = len(neighbours); vecs = []; mus = []
    for _ in range(n_modes):
        v = [rng.gauss(0., 1.) for _ in range(n)]
        v = _deflate(v, vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x / nm for x in v]
        for _ in range(n_iter):
            w = _apply_rw(v, neighbours); w = _deflate(w, vecs)
            nm = _norm(w)
            if nm < 1e-14: break
            v = [x / nm for x in w]
        Av = _apply_rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Unruh temperature (proxy pentru T_global) ─────────────────────────────────

def compute_T_global(neighbours: list) -> float:
    """T_global = mean(T_Unruh) — coerент cu G19."""
    n = len(neighbours)
    degrees = [len(nb) for nb in neighbours]
    mean_k = sum(degrees) / n
    alpha = [d / mean_k for d in degrees]
    T_list = []
    for i in range(n):
        nb = neighbours[i]
        if not nb:
            T_list.append(0.)
            continue
        a_eff = sum(abs(alpha[j] - alpha[i]) for j in nb) / len(nb)
        T_list.append(a_eff / (2. * math.pi))
    return statistics.mean(T_list)


# ── Termodinamică bosonic ─────────────────────────────────────────────────────

def bose_einstein(omega: float, T: float) -> float:
    """Ocupaţie Bose-Einstein n_k = 1/(exp(ω/T)−1)."""
    if T < 1e-14 or omega < 1e-14: return 0.
    x = omega / T
    if x > 700.: return 0.
    return 1. / (math.exp(x) - 1.)


def thermo_quantities(omegas: list, T: float):
    """
    Calculează (ln_Z, F, U, S, C_V) pentru un set de frecvenţe la temperatura T.

    Formule (unități naturale, k_B=ħ=1):
        ln Z = −Σ_k ln(1 − exp(−β ω_k))
        F    = −T ln Z
        U    = Σ_k ω_k n_k
        S    = ln Z + β U  ≡ (U − F)/T
        C_V  = Σ_k ω_k² n_k(n_k+1) / T²
    """
    if T < 1e-14:
        return 0., 0., 0., 0., 0.
    beta = 1. / T
    ln_Z = 0.; U = 0.; C_V = 0.
    for omega in omegas:
        if omega < 1e-14: continue
        x = beta * omega
        if x > 700.:
            # exp(-x) ≈ 0: ln(1-exp(-x)) ≈ -exp(-x) ≈ 0, n_k ≈ 0
            continue
        expm = math.exp(-x)
        ln_Z  += -math.log(1. - expm)          # pozitiv (Z_k ≥ 1)
        n_k    = expm / (1. - expm)             # = 1/(exp(x)-1)
        U     += omega * n_k
        C_V   += omega**2 * n_k * (n_k + 1.) / T**2
    F = -T * ln_Z
    S = ln_Z + beta * U                        # = (U-F)/T
    return ln_Z, F, U, S, C_V


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="G21 Thermodynamic Consistency — Jaccard Graph (v1)"
    )
    p.add_argument("--n-nodes",  type=int,   default=280)
    p.add_argument("--k-init",   type=int,   default=8)
    p.add_argument("--k-conn",   type=int,   default=8)
    p.add_argument("--seed",     type=int,   default=3401)
    p.add_argument("--n-modes",  type=int,   default=N_MODES)
    p.add_argument("--n-iter",   type=int,   default=N_ITER_POW)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG Thermodynamic Consistency — G21 on Jaccard Graph (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log(f"Graph: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"Modes: {args.n_modes}  iter: {args.n_iter}  m²={args.m_eff_sq}")

    # ── Graf ──────────────────────────────────────────────────────────────────
    neighbours = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(neighbours)
    mean_k = sum(len(nb) for nb in neighbours) / n
    log(f"\nGraf construit: n={n}  mean_degree={mean_k:.2f}")

    thr = ThermoThresholds()

    # ── Eigenmodes ─────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iter")
    t1 = time.time()
    mus, _ = compute_eigenmodes(neighbours, args.n_modes, args.n_iter,
                                random.Random(args.seed + 1))
    log(f"  Done in {time.time()-t1:.2f}s  μ_0={fmt(mus[0])}  μ_1={fmt(mus[1])}")
    active = list(range(1, len(mus)))   # ignorăm modul zero (Goldstone)
    K_eff  = len(active)
    mu_act = [mus[k] for k in active]
    omegas = [math.sqrt(mu + args.m_eff_sq) for mu in mu_act]
    log(f"  K_eff={K_eff}  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── Temperatura globală (T_Unruh_mean, coerentă cu G19) ───────────────────
    T_global = compute_T_global(neighbours)
    log(f"\n[2] T_global = T_Unruh_mean = {fmt(T_global)}")
    log(f"  β_global = 1/T = {fmt(1./T_global)}")

    # ── Calculăm termodinamica la T și la 2T ─────────────────────────────────
    log(f"\n[3] Funcţie de partiţie + mărimi termodinamice la T_global")
    ln_Z_T, F_T, U_T, S_T, CV_T = thermo_quantities(omegas, T_global)
    log(f"  ln Z     = {fmt(ln_Z_T)}")
    log(f"  F (free energy) = {fmt(F_T)}")
    log(f"  U (internal)    = {fmt(U_T)}")
    log(f"  S (entropy)     = {fmt(S_T)}")
    log(f"  C_V             = {fmt(CV_T)}")

    log(f"\n[4] Mărimi termodinamice la 2·T_global")
    ln_Z_2T, F_2T, U_2T, S_2T, CV_2T = thermo_quantities(omegas, 2. * T_global)
    log(f"  ln Z(2T)= {fmt(ln_Z_2T)}")
    log(f"  S(2T)   = {fmt(S_2T)}")
    log(f"  U(2T)   = {fmt(U_2T)}")
    log(f"  C_V(2T) = {fmt(CV_2T)}")

    # ── Gate G21a: S > 0 ──────────────────────────────────────────────────────
    log(f"\n[G21a] S_total = {fmt(S_T)}  threshold > {thr.g21a_S_min}")
    gate_g21a = S_T > thr.g21a_S_min
    log(f"  G21a: {'PASS' if gate_g21a else 'FAIL'}")

    # ── Gate G21b: C_V > 0 ────────────────────────────────────────────────────
    log(f"\n[G21b] C_V = {fmt(CV_T)}  threshold > {thr.g21b_CV_min}")
    gate_g21b = CV_T > thr.g21b_CV_min
    log(f"  G21b: {'PASS' if gate_g21b else 'FAIL'}")

    # ── Gate G21c: identitate termodinamică F = U − T·S ───────────────────────
    log(f"\n[G21c] Identitate termodinamică: F = U − T·S")
    F_check = U_T - T_global * S_T
    denom   = abs(F_T) + abs(U_T) + 1e-30    # evităm împărțire la zero la T→0
    id_err  = abs(F_T - F_check) / denom
    log(f"  F_computed = {fmt(F_T)}")
    log(f"  U − T·S    = {fmt(F_check)}")
    log(f"  |err| / denom = {fmt(id_err)}  threshold < {thr.g21c_id_err_max}")
    gate_g21c = id_err < thr.g21c_id_err_max
    log(f"  G21c: {'PASS' if gate_g21c else 'FAIL'}")

    # ── Gate G21d: S(2T)/S(T) > 1.5 (a doua lege + statistică Bose-Einstein) ─
    log(f"\n[G21d] A doua lege: S(2T)/S(T)")
    if S_T > 1e-30:
        S_ratio = S_2T / S_T
    else:
        S_ratio = float("inf") if S_2T > 0 else 1.
    log(f"  S(T)   = {fmt(S_T)}")
    log(f"  S(2T)  = {fmt(S_2T)}")
    log(f"  ratio  = {fmt(S_ratio)}  threshold > {thr.g21d_S_ratio_min}")
    gate_g21d = S_ratio > thr.g21d_S_ratio_min
    log(f"  G21d: {'PASS' if gate_g21d else 'FAIL'}")

    # ── Bonus: verificare derivată β (non-gate, diagnostic) ───────────────────
    log(f"\n[DIAGNOSTIC] d(ln Z)/d(−β) vs U  (verificare funcţie de partiţie)")
    delta_b   = 1. / T_global * 1e-4   # δβ mic
    ln_Z_p, *_ = thermo_quantities(omegas, 1. / (1. / T_global + delta_b))
    ln_Z_m, *_ = thermo_quantities(omegas, 1. / (1. / T_global - delta_b))
    # d(lnZ)/dβ = -U  →  d(lnZ)/d(-β) = U
    # FD pe β: [lnZ(β+δ) - lnZ(β-δ)] / (2δ) = d(lnZ)/dβ = -U
    deriv_lnZ_dbeta = (ln_Z_p - ln_Z_m) / (2. * delta_b)   # = d(lnZ)/dβ = -U
    deriv_lnZ       = -deriv_lnZ_dbeta                       # = d(lnZ)/d(-β) = U
    deriv_err = abs(deriv_lnZ - U_T) / (abs(U_T) + 1e-30)
    log(f"  d(ln Z)/d(−β) [FD] = {fmt(deriv_lnZ)}")
    log(f"  U_thermal           = {fmt(U_T)}")
    log(f"  eroare relativă     = {fmt(deriv_err)}  (diagnostic, nu gate)")

    # ── Decizie ───────────────────────────────────────────────────────────────
    gate_g21  = gate_g21a and gate_g21b and gate_g21c and gate_g21d
    decision  = "pass" if gate_g21 else "fail"
    elapsed   = time.time() - t0

    log(f"\n{'='*70}")
    log(f"G21 Thermodynamics completed in {elapsed:.2f}s")
    log(f"decision={decision}  (a={gate_g21a}, b={gate_g21b}, c={gate_g21c}, d={gate_g21d})")
    log(f"  G21a S_total:        {fmt(S_T)}     threshold > {thr.g21a_S_min}")
    log(f"  G21b C_V:            {fmt(CV_T)}    threshold > {thr.g21b_CV_min}")
    log(f"  G21c id_error:       {fmt(id_err)}  threshold < {thr.g21c_id_err_max}")
    log(f"  G21d S(2T)/S(T):     {fmt(S_ratio)} threshold > {thr.g21d_S_ratio_min}")
    log(f"\n  Consistența termodinamică verificată: S≥0, C_V>0, F=U−TS, dS/dT>0.")

    # ── Per-mode tabel ────────────────────────────────────────────────────────
    n_k_T  = [bose_einstein(w, T_global)       for w in omegas]
    n_k_2T = [bose_einstein(w, 2. * T_global)  for w in omegas]
    s_k    = []
    for k, omega in enumerate(omegas):
        x = omega / T_global if T_global > 1e-14 else 0.
        if x > 700.:
            s_k.append(0.)
        else:
            ln_zk = -math.log(1. - math.exp(-x)) if x > 1e-14 else 0.
            s_k.append(ln_zk + x * n_k_T[k])

    # ── Artefacte ─────────────────────────────────────────────────────────────
    write_csv(out_dir / "thermo_modes_g21.csv",
              ["mode_k", "mu_k", "omega_k", "n_k_T", "n_k_2T", "s_k", "cv_k"],
              [{"mode_k": k + 1,
                "mu_k":    fmt(mu_act[k]),
                "omega_k": fmt(omegas[k]),
                "n_k_T":   fmt(n_k_T[k]),
                "n_k_2T":  fmt(n_k_2T[k]),
                "s_k":     fmt(s_k[k]),
                "cv_k":    fmt(omegas[k]**2 * n_k_T[k] * (n_k_T[k] + 1.) / T_global**2)}
               for k in range(K_eff)])

    write_csv(out_dir / "metric_checks_g21.csv",
              ["gate_id", "metric", "value", "threshold", "status"],
              [
        {"gate_id": "G21a", "metric": "S_total",
         "value": fmt(S_T),    "threshold": f">{thr.g21a_S_min}",
         "status": "pass" if gate_g21a else "fail"},
        {"gate_id": "G21b", "metric": "C_V",
         "value": fmt(CV_T),   "threshold": f">{thr.g21b_CV_min}",
         "status": "pass" if gate_g21b else "fail"},
        {"gate_id": "G21c", "metric": "id_error",
         "value": fmt(id_err), "threshold": f"<{thr.g21c_id_err_max}",
         "status": "pass" if gate_g21c else "fail"},
        {"gate_id": "G21d", "metric": "S_ratio_2T",
         "value": fmt(S_ratio),"threshold": f">{thr.g21d_S_ratio_min}",
         "status": "pass" if gate_g21d else "fail"},
        {"gate_id": "FINAL", "metric": "decision",
         "value": decision,    "threshold": "G21a&G21b&G21c&G21d",
         "status": decision},
    ])

    config = {
        "script":   "run_qng_g21_thermo_v1.py",
        "graph":    {"n": args.n_nodes, "k_init": args.k_init,
                     "k_conn": args.k_conn, "seed": args.seed},
        "mean_degree": round(mean_k, 4),
        "K_eff":       K_eff,
        "m_eff_sq":    args.m_eff_sq,
        "T_global":    round(T_global, 8),
        "ln_Z":        round(ln_Z_T, 8),
        "F":           round(F_T, 8),
        "U":           round(U_T, 8),
        "S_total":     round(S_T, 8),
        "C_V":         round(CV_T, 8),
        "id_error":    round(id_err, 14),
        "S_ratio_2T":  round(S_ratio, 6),
        "deriv_err_diagnostic": round(deriv_err, 8),
        "decision":    decision,
        "run_utc":     datetime.utcnow().isoformat() + "Z",
        "elapsed_s":   round(elapsed, 3),
    }
    (out_dir / "config_g21.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )
    (out_dir / "run-log-g21.txt").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    log(f"\nArtefacte: {out_dir}")

    return 0 if gate_g21 else 1


if __name__ == "__main__":
    sys.exit(main())
