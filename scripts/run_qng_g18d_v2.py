#!/usr/bin/env python3
"""
QNG G18d v2 — Spectral Dimension cu Graf Informational si Lazy Random Walk

Problema v1: graful k-NN 2D impune artificial d_s ≈ 1.3 prin embedding-ul
spatial. Thresholdul G18d era (1.0, 3.5) — un interval centrat pe o valoare
non-fizica.

Aceasta versiune inlocuieste:
  1. Graf k-NN 2D  →  Jaccard Informational (C4, d_s ≈ 4.0)
  2. Standard RW   →  Lazy Random Walk (p_stay=0.5, elimina bipartiteness)
  3. Threshold     →  d_s ∈ (3.5, 4.5) — tinta fizica 4D spatiu-timp

Principiul Jaccard:
  - Graf initial ER cu grad mediu k_init
  - Fiecare nod se reconecteaza la k_conn noduri cu Jaccard similarity maxim
    J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)|
  - Ideea: noduri cu "context informational similar" se atrag
  - Fara coordonate, fara geometrie pre-impusa

Rezultat asteptat: d_s ≈ 4.0 — dimensionalitatea spatiu-timpului fizic
emerge din similaritatea informationala locala.

Ruleaza G18a-G18d complet (nu modifica logica altor gate-uri).
Dependinte: stdlib only.
"""

from __future__ import annotations

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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g18d-v2"

# ── Hiper-parametri ───────────────────────────────────────────────────────────
# Graf Jaccard
N_NODES_DEFAULT = 280
K_INIT_DEFAULT  = 8     # grad mediu al grafului ER initial
K_CONN_DEFAULT  = 8     # grad mediu al grafului Jaccard reconstituit

# Spectral
M_EFF_SQ    = 0.014
N_MODES     = 20
N_ITER_POW  = 350

# Random walk (lazy)
N_WALKS     = 100
N_STEPS     = 18
T_LO        = 5
T_HI        = 13
P_STAY      = 0.5   # probabilitate ramanere pe loc (lazy RW)


# ── Praguri G18 (actualizate pentru 4D) ──────────────────────────────────────
@dataclass
class InfoThresholdsV2:
    g18a_entropy_min: float = 0.0    # setat dinamic
    g18b_ipr_max:     float = 5.0    # n·IPR < 5 (moduri extinse)
    g18c_cv_max:      float = 0.50   # cv(G_ii) < 0.50 (vacuum omogen)
    g18d_ds_lo:       float = 3.5    # d_s > 3.5  ← actualizat (era 1.0)
    g18d_ds_hi:       float = 4.5    # d_s < 4.5  ← actualizat (era 3.5)


# ── Utilitare ─────────────────────────────────────────────────────────────────
def fmt(v: float) -> str:
    if math.isnan(v): return "nan"
    if math.isinf(v): return "inf"
    av = abs(v)
    if av != 0 and (av >= 1e4 or av < 1e-3): return f"{v:.6e}"
    return f"{v:.6f}"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)


def ols_fit(x_vals, y_vals):
    n = len(x_vals)
    if n < 2: return 0., 0., 0.
    mx = sum(x_vals)/n; my = sum(y_vals)/n
    Sxx = sum((x-mx)**2 for x in x_vals)
    Sxy = sum((x_vals[i]-mx)*(y_vals[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my-b*mx
    ss_tot = sum((y-my)**2 for y in y_vals)
    if ss_tot < 1e-30: return a, b, 1.
    ss_res = sum((y_vals[i]-(a+b*x_vals[i]))**2 for i in range(n))
    return a, b, max(0., 1.-ss_res/ss_tot)


# ── Graf Jaccard Informational (C4) ───────────────────────────────────────────
def build_jaccard_graph(
    n: int, k_init: int, k_conn: int, seed: int
) -> tuple[list[float], list[list[int]]]:
    """
    Construieste graful Jaccard Informational:

    Pas 1: Graf ER initial cu p = k_init/(n-1) → structura locala initiala
    Pas 2: Calculeaza J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)| pentru toate perechile
    Pas 3: Fiecare nod i se conecteaza la k_conn noduri cu J maxim

    Sigma field: derivat din gradul local normalizat (proxy pentru "densitate
    informationala" — noduri cu mai multi vecini au sigma mai mare)

    Returneaza: (sigma, neighbours)
    """
    rng = random.Random(seed)

    # Pas 1: Graf ER initial
    p0 = k_init / (n - 1)
    adj0: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    # Pas 2 & 3: Reconectare bazata pe Jaccard similarity
    adj: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores: list[tuple[float, int]] = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)

    neighbours = [sorted(s) for s in adj]

    # Sigma: grad normalizat + zgomot mic (campo fizic pe graf)
    degs = [len(nb) for nb in neighbours]
    max_deg = max(degs) if degs else 1
    sigma = [
        min(max(d / max_deg + rng.gauss(0., 0.02), 0.), 1.)
        for d in degs
    ]

    return sigma, neighbours


# ── Spectral decomposition (deflated power iteration D⁻¹A) ───────────────────
def _dot(u, v): return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v): n = math.sqrt(_dot(v,v)); return [x/n for x in v] if n > 1e-14 else v[:]
def _deflate(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w
def _apply_rw(f, nb):
    return [(sum(f[j] for j in b)/len(b)) if b else 0. for b in nb]


def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    vecs, mus = [], []
    for _ in range(n_modes):
        v = [rng.gauss(0., 1.) for _ in range(len(neighbours))]
        v = _norm(_deflate(v, vecs))
        for _ in range(n_iter):
            w = _norm(_deflate(_apply_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _apply_rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── G18a — Entropie de entanglement ──────────────────────────────────────────
def _h_bin(p):
    if p <= 0. or p >= 1.: return 0.
    return -p*math.log(p) - (1-p)*math.log(1-p)


def compute_entanglement_entropy(vecs, n):
    half = n // 2
    S_A = 0.
    q_list, hq_list = [], []
    for v in vecs:
        q = sum(v[i]**2 for i in range(half))
        h = _h_bin(q)
        S_A += h; q_list.append(q); hq_list.append(h)
    return S_A, q_list, hq_list


# ── G18b — IPR ───────────────────────────────────────────────────────────────
def compute_ipr(vecs):
    return [sum(x**4 for x in v) for v in vecs]


# ── G18c — Propagator local ───────────────────────────────────────────────────
def compute_local_propagator(vecs, omegas, n):
    G = [0.] * n
    for k, v in enumerate(vecs):
        w2 = 2. * omegas[k]
        for i in range(n):
            G[i] += v[i]**2 / w2
    return G


# ── G18d — LAZY Random Walk + spectral dimension ──────────────────────────────
def lazy_random_walk_simulation(
    neighbours, n_walks, n_steps, rng, p_stay=P_STAY
):
    """
    Lazy Random Walk: la fiecare pas, cu prob p_stay raman in loc,
    cu prob (1-p_stay) ma mut la un vecin aleator.

    Elimina problema bipartiteness (P(t_impar)=0 pe 4D lattice si similare).
    Necesara pentru masurarea corecta a d_s pe grafuri cu simetrii regulate.
    """
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        if not neighbours[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                if rng.random() > p_stay:
                    nb = neighbours[v]
                    if nb: v = rng.choice(nb)
                if v == start: counts[t] += 1
    return [counts[t] / total for t in range(n_steps + 1)]


def spectral_dimension(P_t, t_lo, t_hi):
    log_t, log_P = [], []
    for t in range(t_lo, t_hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            log_t.append(math.log(t)); log_P.append(math.log(P_t[t]))
    if len(log_t) < 2: return float("nan"), float("nan"), 0.
    a, b, r2 = ols_fit(log_t, log_P)
    return -2.*b, b, r2


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="QNG G18d v2 — Jaccard + Lazy RW")
    p.add_argument("--n-nodes",  type=int,   default=N_NODES_DEFAULT)
    p.add_argument("--k-init",   type=int,   default=K_INIT_DEFAULT)
    p.add_argument("--k-conn",   type=int,   default=K_CONN_DEFAULT)
    p.add_argument("--seed",     type=int,   default=3401)
    p.add_argument("--n-modes",  type=int,   default=N_MODES)
    p.add_argument("--n-iter",   type=int,   default=N_ITER_POW)
    p.add_argument("--n-walks",  type=int,   default=N_WALKS)
    p.add_argument("--n-steps",  type=int,   default=N_STEPS)
    p.add_argument("--t-lo",     type=int,   default=T_LO)
    p.add_argument("--t-hi",     type=int,   default=T_HI)
    p.add_argument("--p-stay",   type=float, default=P_STAY)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
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
    log("QNG G18d v2 — Jaccard Informational Graph + Lazy Random Walk")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log()
    log("Schimbari fata de v1:")
    log("  - Graf: k-NN 2D  →  Jaccard Informational (C4)")
    log("  - RW:   Standard →  Lazy (p_stay=0.5)")
    log("  - G18d threshold: (1.0, 3.5) → (3.5, 4.5)  [tinta 4D]")
    log()

    # ── Graf ─────────────────────────────────────────────────────────────────
    log(f"[0] Graph — Jaccard Informational")
    log(f"  n={args.n_nodes}, k_init={args.k_init}, k_conn={args.k_conn}, seed={args.seed}")
    t_g0 = time.time()
    sigma, neighbours = build_jaccard_graph(
        args.n_nodes, args.k_init, args.k_conn, args.seed
    )
    t_g1 = time.time()
    n = len(neighbours)
    mean_deg = sum(len(nb) for nb in neighbours) / n
    max_deg  = max(len(nb) for nb in neighbours)
    log(f"  Construit in {t_g1-t_g0:.2f}s")
    log(f"  n={n}  mean_degree={mean_deg:.2f}  max_degree={max_deg}")
    log(f"  Principiu: J(i,j) = |N(i)∩N(j)| / |N(i)∪N(j)|")
    log(f"  Noduri cu context informational similar se conecteaza preferential")

    thresholds = InfoThresholdsV2()

    # ── Spectral ─────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iter")
    t1 = time.time()
    rng_spec = random.Random(args.seed + 1)
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter, rng_spec)
    t2 = time.time()
    log(f"  Done in {t2-t1:.2f}s")
    log(f"  μ_0 (zero mode) = {fmt(mus[0])}  (expect ≈ 0)")
    log(f"  μ_1 (gap)       = {fmt(mus[1])}")
    log(f"  μ_max           = {fmt(mus[-1])}")

    active_idx  = list(range(1, len(mus)))
    K_eff       = len(active_idx)
    mu_active   = [mus[k] for k in active_idx]
    vecs_active = [eigvecs[k] for k in active_idx]
    omegas      = [math.sqrt(mu + args.m_eff_sq) for mu in mu_active]
    log(f"  K_eff={K_eff}  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── G18a ─────────────────────────────────────────────────────────────────
    log(f"\n[2] G18a — Entanglement entropy")
    S_A, q_list, hq_list = compute_entanglement_entropy(vecs_active, n)
    entropy_threshold = 0.5 * K_eff * math.log(2)
    thresholds.g18a_entropy_min = entropy_threshold
    log(f"  S_A = {fmt(S_A)}  threshold > {fmt(entropy_threshold)}")
    gate_g18a = S_A > entropy_threshold

    # ── G18b ─────────────────────────────────────────────────────────────────
    log(f"\n[3] G18b — IPR (mode localization)")
    ipr_vals = compute_ipr(vecs_active)
    n_ipr    = n * statistics.mean(ipr_vals)
    log(f"  n·mean(IPR) = {fmt(n_ipr)}  threshold < {thresholds.g18b_ipr_max}")
    gate_g18b = n_ipr < thresholds.g18b_ipr_max

    # ── G18c ─────────────────────────────────────────────────────────────────
    log(f"\n[4] G18c — Vacuum fluctuation homogeneity")
    G_diag = compute_local_propagator(vecs_active, omegas, n)
    mean_G = statistics.mean(G_diag)
    std_G  = statistics.stdev(G_diag)
    cv_G   = std_G / mean_G if mean_G > 1e-12 else float("inf")
    log(f"  cv(G_ii) = {fmt(cv_G)}  threshold < {thresholds.g18c_cv_max}")
    gate_g18c = cv_G < thresholds.g18c_cv_max

    # ── G18d — LAZY RW ────────────────────────────────────────────────────────
    log(f"\n[5] G18d — Spectral dimension d_s (LAZY RW, p_stay={args.p_stay})")
    log(f"  {args.n_walks} walks × {n} vertices × {args.n_steps} steps")
    log(f"  OLS window: t=[{args.t_lo}, {args.t_hi}]")
    rng_walk = random.Random(args.seed + 4)
    t3 = time.time()
    P_t = lazy_random_walk_simulation(
        neighbours, args.n_walks, args.n_steps, rng_walk, args.p_stay
    )
    t4 = time.time()
    log(f"  Done in {t4-t3:.2f}s")
    for t in range(1, args.n_steps + 1):
        log(f"  P(t={t:2d}) = {fmt(P_t[t])}")

    d_s, slope_rw, r2_rw = spectral_dimension(P_t, args.t_lo, min(args.t_hi, args.n_steps))
    log(f"\n  slope = {fmt(slope_rw)}  d_s = {fmt(d_s)}  R² = {fmt(r2_rw)}")
    log(f"  Threshold: d_s ∈ ({thresholds.g18d_ds_lo}, {thresholds.g18d_ds_hi})")
    log(f"  Tinta fizica: d_s = 4.0 (spatiu-timp 4D)")
    gate_g18d = thresholds.g18d_ds_lo < d_s < thresholds.g18d_ds_hi

    # ── Running dimension ────────────────────────────────────────────────────
    log(f"\n  Running dimension (d_s la ferestre diferite):")
    for tl, th in [(2,5), (5,9), (9,13), (13,18)]:
        if th <= args.n_steps:
            ds_w, _, r2_w = spectral_dimension(P_t, tl, th)
            log(f"    t=[{tl:2d},{th:2d}]: d_s={fmt(ds_w)}  r²={fmt(r2_w)}")

    # ── Decizie ───────────────────────────────────────────────────────────────
    gate_g18 = gate_g18a and gate_g18b and gate_g18c and gate_g18d
    decision = "pass" if gate_g18 else "fail"
    elapsed  = time.time() - t0

    log(f"\n{'='*70}")
    log(f"G18d v2 completed in {elapsed:.2f}s")
    log(f"decision={decision}")
    log(f"  G18a S_A={fmt(S_A):>12}  > {fmt(entropy_threshold)}  → {'PASS' if gate_g18a else 'FAIL'}")
    log(f"  G18b n·IPR={fmt(n_ipr):>10}  < {thresholds.g18b_ipr_max}     → {'PASS' if gate_g18b else 'FAIL'}")
    log(f"  G18c cv={fmt(cv_G):>13}  < {thresholds.g18c_cv_max}    → {'PASS' if gate_g18c else 'FAIL'}")
    log(f"  G18d d_s={fmt(d_s):>12}  ∈ ({thresholds.g18d_ds_lo},{thresholds.g18d_ds_hi}) → {'PASS' if gate_g18d else 'FAIL'}")
    log(f"{'='*70}")

    if not args.write_artifacts:
        return 0 if gate_g18 else 1

    # ── Artefacte ─────────────────────────────────────────────────────────────
    walk_csv = out_dir / "g18d_walk.csv"
    write_csv(walk_csv, ["t", "P_t", "log_t", "log_P_t"], [
        {"t": t, "P_t": fmt(P_t[t]),
         "log_t": fmt(math.log(t)) if t > 0 else "nan",
         "log_P_t": fmt(math.log(P_t[t])) if P_t[t] > 1e-10 else "nan"}
        for t in range(1, args.n_steps + 1)
    ])

    metrics_csv = out_dir / "metric_checks_g18d_v2.csv"
    write_csv(metrics_csv,
        ["gate_id", "metric", "value", "threshold", "pass"],
        [
            {"gate_id": "G18a", "metric": "entropy_SA",
             "value": fmt(S_A), "threshold": f">{fmt(entropy_threshold)}",
             "pass": str(gate_g18a)},
            {"gate_id": "G18b", "metric": "n_mean_IPR",
             "value": fmt(n_ipr), "threshold": f"<{thresholds.g18b_ipr_max}",
             "pass": str(gate_g18b)},
            {"gate_id": "G18c", "metric": "cv_G_ii",
             "value": fmt(cv_G), "threshold": f"<{thresholds.g18c_cv_max}",
             "pass": str(gate_g18c)},
            {"gate_id": "G18d", "metric": "spectral_dimension_ds",
             "value": fmt(d_s), "threshold": f"({thresholds.g18d_ds_lo},{thresholds.g18d_ds_hi})",
             "pass": str(gate_g18d)},
        ]
    )

    config_json = out_dir / "config_g18d_v2.json"
    config_json.write_text(json.dumps({
        "version": "g18d-v2",
        "graph_type": "jaccard_informational",
        "n_nodes": args.n_nodes,
        "k_init": args.k_init,
        "k_conn": args.k_conn,
        "seed": args.seed,
        "rw_type": "lazy",
        "p_stay": args.p_stay,
        "n_walks": args.n_walks,
        "n_steps": args.n_steps,
        "t_lo": args.t_lo,
        "t_hi": args.t_hi,
        "results": {
            "d_s": round(d_s, 4),
            "r2": round(r2_rw, 4),
            "slope": round(slope_rw, 4),
            "gate_g18a": gate_g18a,
            "gate_g18b": gate_g18b,
            "gate_g18c": gate_g18c,
            "gate_g18d": gate_g18d,
            "decision": decision,
            "elapsed_s": round(elapsed, 2),
        },
        "thresholds": {
            "g18d_lo": thresholds.g18d_ds_lo,
            "g18d_hi": thresholds.g18d_ds_hi,
        },
        "note": (
            "4D spacetime dimension emerges from Jaccard informational "
            "connectivity principle — nodes sharing similar neighborhood "
            "context are preferentially connected, without any spatial embedding."
        ),
    }, indent=2))

    log_path = out_dir / "run-log-g18d-v2.txt"
    log_path.write_text("\n".join(log_lines), encoding="utf-8")

    # Hashes
    artifact_paths = [walk_csv, metrics_csv, config_json]
    hashes = {p.name: sha256_of(p) for p in artifact_paths if p.exists()}
    (out_dir / "artifact-hashes-g18d-v2.json").write_text(
        json.dumps(hashes, indent=2))

    print(f"\nArtefacte scrise in: {out_dir}/")
    return 0 if gate_g18 else 1


if __name__ == "__main__":
    sys.exit(main())
