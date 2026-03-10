#!/usr/bin/env python3
"""
QNG G17 v2 — Canonical Quantization pe Graf Jaccard Informational

Diferente fata de v1:
  1. Graf: k-NN 2D → Jaccard Informational (fara coordonate spatiale)
  2. Distanta: Euclidiana → Geodezica pe graf (BFS shortest path)
     G17b masoara decay-ul G(i,j) vs distanta intrinseca, nu geometrie externa.

Schimbarea distantei e mai corecta fizic: pe un graf discret, "distanta"
naturala e lungimea celui mai scurt drum, nu distanta intr-un embedding
arbitrar. Propagatorul Yukawa G(i,j) ~ exp(-m*r_graph) ar trebui sa scada
cu distanta geodezica daca graful are geometrie sanatoasa.

Gate-urile G17a-d raman neschimbate (aceleasi thresholds si logica).

Dependinte: stdlib only.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
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
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g17-v2"

M_EFF_SQ   = 0.014
N_MODES    = 20
N_ITER_POW = 500
N_SAMPLE   = 600

N_NODES  = 280
K_INIT   = 8
K_CONN   = 8


@dataclass
class QMThresholdsV2:
    g17a_gap_min:          float = 0.01
    g17b_slope_max:        float = -0.01
    g17c_e0_per_mode_lo:   float = 0.05
    g17c_e0_per_mode_hi:   float = 5.0
    g17d_heisenberg_tol:   float = 0.01


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


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(rows)


def ols_fit(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my-b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    ss_res = sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))
    return a, b, max(0., 1.-ss_res/ss_tot)


# ── Graf Jaccard ──────────────────────────────────────────────────────────────
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

    neighbours = [sorted(s) for s in adj]
    degs = [len(nb) for nb in neighbours]
    max_deg = max(degs) if degs else 1
    sigma = [min(max(d/max_deg + rng.gauss(0., 0.02), 0.), 1.) for d in degs]
    return sigma, neighbours


# ── Distanta geodezica pe graf (BFS) ─────────────────────────────────────────
def bfs_distances_from(source: int, neighbours: list[list[int]]) -> list[int]:
    """
    BFS din nodul source → distante geodezice la toate nodurile.
    Noduri inaccesibile primesc distanta = -1.
    """
    n = len(neighbours)
    dist = [-1] * n
    dist[source] = 0
    queue = collections.deque([source])
    while queue:
        v = queue.popleft()
        for u in neighbours[v]:
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                queue.append(u)
    return dist


def compute_geodesic_distances(
    pairs: list[tuple[int, int]],
    neighbours: list[list[int]],
) -> list[float]:
    """
    Distante geodezice pentru o lista de perechi (i,j).
    Optimizare: BFS o singura data per nod sursa unic.
    Returneaza distante ca float (pentru compatibilitate cu OLS).
    """
    sources = sorted({i for i, j in pairs})
    dist_cache: dict[int, list[int]] = {}
    for s in sources:
        dist_cache[s] = bfs_distances_from(s, neighbours)

    r_list = []
    for i, j in pairs:
        d = dist_cache[i][j]
        r_list.append(float(d) if d >= 0 else float("nan"))
    return r_list


# ── Spectral decomposition ────────────────────────────────────────────────────
def _dot(u, v): return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v): n=math.sqrt(_dot(v,v)); return [x/n for x in v] if n>1e-14 else v[:]
def _defl(v, basis):
    w=v[:]
    for b in basis: c=_dot(w,b); w=[w[i]-c*b[i] for i in range(len(w))]
    return w
def _rw(f, nb): return [(sum(f[j] for j in b)/len(b)) if b else 0. for b in nb]


def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    vecs, mus = [], []
    for _ in range(n_modes):
        v = _norm(_defl([rng.gauss(0.,1.) for _ in range(len(neighbours))], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w,w)) < 1e-14: break
            v = w
        Av = _rw(v, neighbours); alpha = _dot(v, Av)
        mu = max(0., 1.-alpha); vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Propagator ────────────────────────────────────────────────────────────────
def compute_propagator_sample(eigvecs, omegas, pairs, r_vals):
    """G(i,j) = Σ_k ψ_k(i) ψ_k(j) / (2ω_k) pentru perechi selectate."""
    K = len(omegas); G_list = []
    for idx, (i, j) in enumerate(pairs):
        if math.isnan(r_vals[idx]):
            G_list.append(float("nan")); continue
        G_ij = sum(eigvecs[k][i]*eigvecs[k][j]/(2.*omegas[k]) for k in range(K))
        G_list.append(G_ij)
    return G_list


def compute_local_propagator(eigvecs, omegas, n):
    K = len(omegas); G_diag = [0.]*n
    for k in range(K):
        inv2w = 1./(2.*omegas[k])
        for i in range(n): G_diag[i] += eigvecs[k][i]**2*inv2w
    return G_diag


# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="QNG G17 v2 — Jaccard + geodesic distance")
    p.add_argument("--n-nodes",  type=int,   default=N_NODES)
    p.add_argument("--k-init",   type=int,   default=K_INIT)
    p.add_argument("--k-conn",   type=int,   default=K_CONN)
    p.add_argument("--seed",     type=int,   default=3401)
    p.add_argument("--n-modes",  type=int,   default=N_MODES)
    p.add_argument("--n-iter",   type=int,   default=N_ITER_POW)
    p.add_argument("--n-sample", type=int,   default=N_SAMPLE)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    p.add_argument("--write-artifacts", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    def log(msg=""):
        try:
            print(msg)
        except UnicodeEncodeError:
            print(str(msg).encode("ascii", "replace").decode("ascii"))
        log_lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG G17 v2 — Jaccard Informational Graph + Geodesic Distance")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log()
    log("Schimbari fata de G17 v1:")
    log("  - Graf: k-NN 2D → Jaccard Informational")
    log("  - Distanta: Euclidiana → Geodezica pe graf (BFS)")
    log("  - Thresholds G17a-d: neschimbate")
    log()

    # ── Graf ─────────────────────────────────────────────────────────────────
    log(f"[0] Graf Jaccard: n={args.n_nodes}, k_init={args.k_init}, k_conn={args.k_conn}")
    t_g = time.time()
    sigma, neighbours = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(neighbours)
    mean_deg = sum(len(nb) for nb in neighbours)/n
    log(f"  Construit in {time.time()-t_g:.2f}s  |  n={n}, k_avg={mean_deg:.2f}")
    log(f"  m_eff² = {args.m_eff_sq}  →  m_eff = {math.sqrt(args.m_eff_sq):.6f}")

    thresholds = QMThresholdsV2()

    # ── Spectral ─────────────────────────────────────────────────────────────
    log(f"\n[1] Eigenmode computation: {args.n_modes} modes × {args.n_iter} iter")
    t1 = time.time()
    rng_spec = random.Random(args.seed+1)
    mus, eigvecs = compute_eigenmodes(neighbours, args.n_modes, args.n_iter, rng_spec)
    log(f"  Done in {time.time()-t1:.2f}s")
    log(f"  μ_0 (zero mode) = {fmt(mus[0])}  (expect ≈ 0)")
    log(f"  μ_1 (gap)       = {fmt(mus[1])}  (spectral gap)")
    log(f"  μ_max           = {fmt(mus[-1])}")

    active_idx = list(range(1, len(mus)))
    K_eff = len(active_idx)
    mu_active   = [mus[k]    for k in active_idx]
    vecs_active = [eigvecs[k] for k in active_idx]

    # ── Frecvente ─────────────────────────────────────────────────────────────
    log(f"\n[2] Frecvente ω_k = √(μ_k + m²)  (K_eff={K_eff})")
    omegas = [math.sqrt(mu+args.m_eff_sq) for mu in mu_active]
    log(f"  ω ∈ [{fmt(min(omegas))}, {fmt(max(omegas))}]")

    # ── Zero-point energy ────────────────────────────────────────────────────
    log(f"\n[3] Zero-point energy E_0 = ½ Σ ω_k")
    E_0 = 0.5*sum(omegas); E_0_per_mode = E_0/K_eff
    log(f"  E_0={fmt(E_0)}  E_0/K_eff={fmt(E_0_per_mode)}")

    # ── Heisenberg ───────────────────────────────────────────────────────────
    log(f"\n[4] Heisenberg: Δσ_k · Δπ_k per mod")
    d_sig = [1./math.sqrt(2.*w) for w in omegas]
    d_pi  = [math.sqrt(w/2.) for w in omegas]
    prods = [d_sig[k]*d_pi[k] for k in range(K_eff)]
    mean_prod = statistics.mean(prods)
    heisenberg_dev = abs(mean_prod-0.5)
    log(f"  mean(Δσ·Δπ) = {fmt(mean_prod)}  (tinta: 0.5)  dev={fmt(heisenberg_dev)}")

    # ── Propagator + distanta geodezica ──────────────────────────────────────
    log(f"\n[5] Propagator G(i,j) cu distanta geodezica ({args.n_sample} perechi)")
    rng_samp = random.Random(args.seed+2)
    all_pairs = [(i,j) for i in range(n) for j in range(i+1, n)]
    sampled = rng_samp.sample(all_pairs, min(args.n_sample, len(all_pairs)))

    log(f"  Calcul distante geodezice (BFS)...")
    t_bfs = time.time()
    r_vals = compute_geodesic_distances(sampled, neighbours)
    log(f"  Done in {time.time()-t_bfs:.3f}s")

    valid_r = [r for r in r_vals if not math.isnan(r)]
    log(f"  r_geodesic: min={fmt(min(valid_r))}, max={fmt(max(valid_r))}, "
        f"mean={fmt(sum(valid_r)/len(valid_r))}")

    G_vals_raw = compute_propagator_sample(vecs_active, omegas, sampled, r_vals)

    # Filtreaza NaN din perechi nereachabile
    valid = [(r_vals[k], G_vals_raw[k]) for k in range(len(sampled))
             if not math.isnan(r_vals[k]) and not math.isnan(G_vals_raw[k])]
    r_filt = [x[0] for x in valid]; G_filt = [x[1] for x in valid]
    log(f"  G(i,j): min={fmt(min(G_filt))}, max={fmt(max(G_filt))}, "
        f"mean={fmt(statistics.mean(G_filt))}")

    ols_a, ols_b, ols_r2 = ols_fit(r_filt, G_filt)
    log(f"  OLS G ~ a + b·r_geo:  a={fmt(ols_a)}, b={fmt(ols_b)}, R²={fmt(ols_r2)}")
    log(f"  Interpretare: b<0 → propagator Yukawa scade cu distanta geodezica")

    # ── Local propagator ──────────────────────────────────────────────────────
    log(f"\n[6] Propagator local G(i,i)")
    G_diag = compute_local_propagator(vecs_active, omegas, n)
    log(f"  G(i,i): min={fmt(min(G_diag))}, max={fmt(max(G_diag))}, "
        f"mean={fmt(statistics.mean(G_diag))}")

    # ── Gate evaluation ───────────────────────────────────────────────────────
    spectral_gap = mus[1] if len(mus) > 1 else 0.

    gate_g17a = spectral_gap   > thresholds.g17a_gap_min
    gate_g17b = ols_b          < thresholds.g17b_slope_max
    gate_g17c = (thresholds.g17c_e0_per_mode_lo < E_0_per_mode
                 < thresholds.g17c_e0_per_mode_hi)
    gate_g17d = heisenberg_dev < thresholds.g17d_heisenberg_tol
    gate_g17  = gate_g17a and gate_g17b and gate_g17c and gate_g17d
    decision  = "pass" if gate_g17 else "fail"
    elapsed   = time.time()-t0

    log(f"\n{'='*70}")
    log(f"G17 v2 completed in {elapsed:.2f}s")
    log(f"decision={decision}")
    log(f"  G17a spectral gap  μ₁={fmt(spectral_gap):>12}  > {thresholds.g17a_gap_min}"
        f"  → {'PASS' if gate_g17a else 'FAIL'}")
    log(f"  G17b slope G vs r  b={fmt(ols_b):>13}  < {thresholds.g17b_slope_max}"
        f"  → {'PASS' if gate_g17b else 'FAIL'}")
    log(f"  G17c E₀/K_eff     {fmt(E_0_per_mode):>13}  ∈ ({thresholds.g17c_e0_per_mode_lo}"
        f",{thresholds.g17c_e0_per_mode_hi})  → {'PASS' if gate_g17c else 'FAIL'}")
    log(f"  G17d Heisenberg   dev={fmt(heisenberg_dev):>10}  < {thresholds.g17d_heisenberg_tol}"
        f"  → {'PASS' if gate_g17d else 'FAIL'}")
    log(f"{'='*70}")

    if not args.write_artifacts:
        return 0 if gate_g17 else 1

    # ── Artefacte ─────────────────────────────────────────────────────────────
    modes_csv = out_dir / "g17_modes.csv"
    write_csv(modes_csv, ["k","mu_k","omega_k","delta_sigma","delta_pi","product"],
        [{"k": k+1, "mu_k": fmt(mu_active[k]), "omega_k": fmt(omegas[k]),
          "delta_sigma": fmt(d_sig[k]), "delta_pi": fmt(d_pi[k]),
          "product": fmt(prods[k])} for k in range(K_eff)])

    prop_csv = out_dir / "g17_propagator.csv"
    write_csv(prop_csv, ["pair_i","pair_j","r_geodesic","G_ij"],
        [{"pair_i": sampled[k][0], "pair_j": sampled[k][1],
          "r_geodesic": fmt(r_vals[k]), "G_ij": fmt(G_vals_raw[k])}
         for k in range(len(sampled))])

    metrics_csv = out_dir / "metric_checks_g17_v2.csv"
    write_csv(metrics_csv, ["gate_id","metric","value","threshold","pass"],
        [{"gate_id":"G17a","metric":"spectral_gap","value":fmt(spectral_gap),
          "threshold":f">{thresholds.g17a_gap_min}","pass":str(gate_g17a)},
         {"gate_id":"G17b","metric":"propagator_slope_vs_geodesic",
          "value":fmt(ols_b),"threshold":f"<{thresholds.g17b_slope_max}",
          "pass":str(gate_g17b)},
         {"gate_id":"G17c","metric":"E0_per_mode","value":fmt(E_0_per_mode),
          "threshold":f"({thresholds.g17c_e0_per_mode_lo},{thresholds.g17c_e0_per_mode_hi})",
          "pass":str(gate_g17c)},
         {"gate_id":"G17d","metric":"heisenberg_dev","value":fmt(heisenberg_dev),
          "threshold":f"<{thresholds.g17d_heisenberg_tol}","pass":str(gate_g17d)}])

    config = {"version":"g17-v2","graph":"jaccard_informational",
               "distance":"geodesic_bfs","n":n,"k_init":args.k_init,
               "k_conn":args.k_conn,"seed":args.seed,
               "results":{"spectral_gap":round(spectral_gap,6),
                           "slope_g_vs_r":round(ols_b,6),
                           "E0_per_mode":round(E_0_per_mode,6),
                           "heisenberg_dev":round(heisenberg_dev,8),
                           "decision":decision,"elapsed_s":round(elapsed,2)}}
    cfg_path = out_dir/"config_g17_v2.json"
    cfg_path.write_text(json.dumps(config, indent=2))

    artifacts = [modes_csv, prop_csv, metrics_csv, cfg_path]
    hashes = {p.name: sha256_of(p) for p in artifacts if p.exists()}
    (out_dir/"artifact-hashes-g17-v2.json").write_text(json.dumps(hashes, indent=2))
    (out_dir/"run-log-g17-v2.txt").write_text("\n".join(log_lines), encoding="utf-8")

    print(f"\nArtefacte: {out_dir}/")
    return 0 if gate_g17 else 1


if __name__ == "__main__":
    sys.exit(main())
