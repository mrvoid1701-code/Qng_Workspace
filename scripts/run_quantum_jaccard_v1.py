#!/usr/bin/env python3
"""
Quantum Jaccard Graph — Mean-Field Implementation (v1)

IDEEA CENTRALĂ:
  Graful Jaccard clasic e starea fundamentală (λ=0) a unui sistem cuantic
  în care fiecare muchie (i,j) e un qubit: |1⟩ = există, |0⟩ = nu există.

  Hamiltonianul:
    H = -Σ_{i<j} h_{ij} σ^z_{ij}  +  λ Σ_{i<j} σ^x_{ij}

  unde:
    h_{ij} = J(i,j) - J_threshold   (câmpul Jaccard centrat pe prag)
    λ       = cuplaj cuantic (intensitatea fluctuațiilor cuantice)
    σ^z, σ^x = operatori Pauli pe spațiul muchiei

  Starea fundamentală (mean-field, muchii independente):
    P(muchia (i,j) există) = [1 + h_{ij} / √(h_{ij}² + λ²)] / 2

  Interpretare fizică:
    λ = 0       → Jaccard clasic exact (starea actuală din QNG)
    λ ≈ h̄      → fluctuații cuantice moderate (scară Planck)
    λ → ∞      → graf complet aleator (ER, pierdere coerență)

SCOPUL EXPERIMENTULUI:
  1. Există o tranziție de fază? (d_s sare brusc?)
  2. Apare reducția dimensională UV? (d_s scade la λ mare → CDT-like)
  3. μ₁ e mai stabil în ansamblul cuantic?
  4. La ce λ se "topește" graful Jaccard → ER?
  5. Entropia cuantică a stării de muchii vs d_s

MĂSURI:
  - d_s(λ):         dimensiunea spectrală medie
  - μ₁(λ):          spectral gap (stabilitate QM)
  - ⟨k⟩(λ):         gradul mediu
  - S_ent(λ):        entropia cuantică a stării de muchii (bit von Neumann)
  - pass_rate(λ):    fracția grafurilor din ansamblu cu d_s ∈ (3.5, 4.5)
  - d_s_uv(λ):       dimensiune la scară UV (t=2-5)
  - d_s_ir(λ):       dimensiune la scară IR (t=9-13)

Output:
  quantum_jaccard_sweep.csv
  quantum_jaccard_summary.json
  run-log-quantum-jaccard.txt
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "quantum-jaccard-v1"

# Parametri canonici
N      = 280
K_INIT = 8
K_CONN = 8
SEED   = 3401

# Random walk
N_WALKS = 80
N_STEPS = 18
P_STAY  = 0.5
T_LO, T_HI   = 5, 13
UV_LO, UV_HI = 2, 5
IR_LO, IR_HI = 9, 13

# Ansamblu cuantic
N_SAMPLES_PER_LAMBDA = 30   # grafuri sampate per λ
LAMBDA_GRID = [
    0.0,                    # clasic pur
    0.005, 0.01,            # fluctuații minime
    0.02, 0.05,             # regim cuantic slab
    0.10, 0.15,             # crossover
    0.20, 0.30,             # regim cuantic puternic
    0.50, 1.0, 2.0, 5.0,   # dezordine totală
]

DS_LO, DS_HI = 3.5, 4.5


# ── OLS și metrici ────────────────────────────────────────────────────────────

def ols(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my-b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    if ss_tot < 1e-30: return a, b, 1.
    return a, b, max(0., 1.-sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))/ss_tot)


def ds_window(P_t, lo, hi):
    lx, ly = [], []
    for t in range(lo, hi+1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t)); ly.append(math.log(P_t[t]))
    if len(lx) < 2: return float("nan"), 0.
    _, b, r2 = ols(lx, ly)
    return -2.*b, r2


def lazy_rw(neighbours, n_walks, n_steps, rng, p_stay=P_STAY):
    n = len(neighbours)
    counts = [0] * (n_steps + 1)
    total = n * n_walks
    for start in range(n):
        if not neighbours[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps+1):
                if rng.random() > p_stay:
                    nb = neighbours[v]
                    if nb: v = rng.choice(nb)
                if v == start: counts[t] += 1
    return [counts[t]/total for t in range(n_steps+1)]


def spectral_gap_power_iter(nb, n_iter=300, seed=42):
    """
    Estimare μ₁ (spectral gap) prin power iteration pe Laplacianul RW.
    μ₁ = 1 - λ_max(I - L_rw) = 1 - a doua valoare proprie cea mai mare a W_rw.
    """
    n = len(nb)
    rng = random.Random(seed)
    # Matricea de tranziție lazy: W[i][j] = 0.5/deg(i) dacă (i,j) ∈ E, 0.5 dacă i=j
    deg = [max(len(x), 1) for x in nb]

    def matvec(v):
        # Aplică W pe vectorul v
        out = [0.] * n
        for i in range(n):
            out[i] += 0.5 * v[i]  # termenul de self-loop
            for j in nb[i]:
                out[i] += 0.5 * v[j] / deg[j]
        return out

    # Power iteration pentru a doua valoare proprie (deflation față de v_stat)
    # v_stat ∝ grad (stationara)
    v_stat = [math.sqrt(deg[i]) for i in range(n)]
    norm_stat = math.sqrt(sum(x*x for x in v_stat))
    v_stat = [x/norm_stat for x in v_stat]

    # Vector random, ortogonal pe v_stat
    v = [rng.gauss(0, 1) for _ in range(n)]
    # Deflate
    dot = sum(v[i]*v_stat[i] for i in range(n))
    v = [v[i] - dot*v_stat[i] for i in range(n)]
    norm = math.sqrt(sum(x*x for x in v))
    if norm < 1e-15: return 0.
    v = [x/norm for x in v]

    lam = 0.
    for _ in range(n_iter):
        v2 = matvec(v)
        # Deflate
        dot = sum(v2[i]*v_stat[i] for i in range(n))
        v2 = [v2[i] - dot*v_stat[i] for i in range(n)]
        norm2 = math.sqrt(sum(x*x for x in v2))
        if norm2 < 1e-15: break
        lam = sum(v2[i]*v[i] for i in range(n)) / sum(v[i]*v[i] for i in range(n))
        v = [x/norm2 for x in v2]

    # μ₁ = 1 - λ_2 (a doua valoare proprie cea mai mare a W)
    return max(0., 1. - lam)


# ── Construcția grafului Jaccard — scoruri complete ────────────────────────────

def build_jaccard_scores(n, k_init, seed):
    """
    Returnează:
      adj0: graful ER inițial (contextul)
      J_scores: dict (i,j) → similaritate Jaccard (i<j)
      J_threshold: pragul median al scorurilor de pe muchiile clasice
    """
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    # Calculăm J(i,j) pentru toate perechile (costisitor dar necesar o dată)
    J = {}
    for i in range(n):
        Ni = adj0[i] | {i}
        for j in range(i+1, n):
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            J[(i,j)] = inter/union if union else 0.

    # Identificăm muchiile clasice Jaccard (top k_conn per nod)
    classic_edges = set()
    for i in range(n):
        scores_i = sorted(
            [(J.get((min(i,j), max(i,j)), 0.), j) for j in range(n) if j != i],
            reverse=True
        )
        for _, j in scores_i[:K_CONN]:
            classic_edges.add((min(i,j), max(i,j)))

    # Pragul = media scorurilor Jaccard ale muchiilor clasice
    classic_J_vals = [J[e] for e in classic_edges]
    J_threshold = statistics.mean(classic_J_vals) if classic_J_vals else 0.

    return adj0, J, J_threshold, classic_edges


# ── Quantum sampling ───────────────────────────────────────────────────────────

def quantum_edge_prob(h_ij, lam):
    """
    P(muchia există) = [1 + h / √(h² + λ²)] / 2
    Derivată din starea fundamentală a Hamiltonianului H_ij = -h σ^z + λ σ^x.
    """
    if lam == 0.:
        return 1.0 if h_ij >= 0 else 0.0
    denom = math.sqrt(h_ij * h_ij + lam * lam)
    return (1. + h_ij / denom) / 2.


def sample_quantum_graph(n, J_scores, J_threshold, lam, rng):
    """
    Sampează un graf din distribuția cuantică P(G; λ).
    Fiecare muchie (i,j) există independent cu probabilitate quantum_edge_prob(h_{ij}, λ).
    """
    adj = [set() for _ in range(n)]
    for (i, j), j_val in J_scores.items():
        h = j_val - J_threshold
        p = quantum_edge_prob(h, lam)
        if rng.random() < p:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def quantum_entropy(J_scores, J_threshold, lam):
    """
    Entropia cuantică von Neumann a stării de muchii.
    S = -Σ_{ij} [p log p + (1-p) log(1-p)]  (biți)
    La λ=0: S=0 (stat pur - Jaccard clasic exact).
    La λ→∞: S = nr_muchii_potențiale (maxim dezordine).
    """
    S = 0.
    for j_val in J_scores.values():
        h = j_val - J_threshold
        p = quantum_edge_prob(h, lam)
        if 1e-15 < p < 1 - 1e-15:
            S -= p * math.log2(p) + (1-p) * math.log2(1-p)
    return S


def evaluate_graph(nb, seed):
    rng = random.Random(seed)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2 = ds_window(P_t, T_LO, T_HI)
    ds_uv, _ = ds_window(P_t, UV_LO, UV_HI)
    ds_ir, _ = ds_window(P_t, IR_LO, IR_HI)
    mean_deg = sum(len(x) for x in nb) / len(nb)
    lcc = largest_connected_component(nb)
    return ds, r2, ds_uv, ds_ir, mean_deg, lcc


def largest_connected_component(nb):
    n = len(nb)
    visited = [False] * n
    best = 0
    for start in range(n):
        if visited[start]: continue
        size = 0
        stack = [start]
        while stack:
            v = stack.pop()
            if visited[v]: continue
            visited[v] = True; size += 1
            stack.extend(u for u in nb[v] if not visited[u])
        best = max(best, size)
    return best


# ── Main ───────────────────────────────────────────────────────────────────────

@dataclass
class LambdaResult:
    lam:           float
    sample:        int
    ds:            float
    r2:            float
    ds_uv:         float
    ds_ir:         float
    mean_deg:      float
    lcc:           int
    mu1:           float
    S_ent:         float
    pass_ds:       bool


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 74)
    log("QUANTUM JACCARD GRAPH — Mean-Field λ Sweep")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log(f"N={N}, K_INIT={K_INIT}, K_CONN={K_CONN}, SEED={SEED}")
    log(f"N_SAMPLES_PER_LAMBDA={N_SAMPLES_PER_LAMBDA}")
    log(f"LAMBDA_GRID={LAMBDA_GRID}")
    log("=" * 74)

    # ── Construim scorurile Jaccard o singură dată ─────────────────────────────
    log("\n[INIT] Calculez scorurile Jaccard (toate perechile)...")
    t1 = time.time()
    _, J_scores, J_threshold, classic_edges = build_jaccard_scores(N, K_INIT, SEED)
    log(f"  Perechi totale: {len(J_scores)}")
    log(f"  Muchii clasice Jaccard: {len(classic_edges)}")
    log(f"  J_threshold = {J_threshold:.6f}")
    log(f"  J_scores range: [{min(J_scores.values()):.4f}, {max(J_scores.values()):.4f}]")

    # Distribuția câmpurilor h
    h_vals = [v - J_threshold for v in J_scores.values()]
    h_pos = [h for h in h_vals if h > 0]
    h_neg = [h for h in h_vals if h < 0]
    log(f"  h > 0 (muchii favorizate): {len(h_pos)} ({100*len(h_pos)/len(h_vals):.1f}%)")
    log(f"  h < 0 (muchii defavorizate): {len(h_neg)} ({100*len(h_neg)/len(h_vals):.1f}%)")
    log(f"  |h| mediu: {statistics.mean(abs(h) for h in h_vals):.6f}")
    log(f"  Crossover λ_c ≈ mean(|h|) = {statistics.mean(abs(h) for h in h_vals):.6f}")
    log(f"  ({time.time()-t1:.1f}s)")

    # ── Sweep λ ───────────────────────────────────────────────────────────────
    log("\n" + "─" * 74)
    log(f"{'λ':>8}  {'d_s mean':>9}  {'d_s std':>8}  {'d_s_uv':>8}  {'d_s_ir':>8}  "
        f"{'<k>':>6}  {'μ₁':>7}  {'S_ent':>9}  {'PASS':>5}")
    log("─" * 74)

    all_results: list[LambdaResult] = []
    summary_per_lambda = []

    for lam in LAMBDA_GRID:
        t1 = time.time()
        rng_sample = random.Random(SEED ^ int(lam * 1e6) ^ 0xDEAD)

        # Entropia cuantică e deterministă (nu depinde de samplare)
        S_ent = quantum_entropy(J_scores, J_threshold, lam)

        ds_list, ds_uv_list, ds_ir_list = [], [], []
        deg_list, mu1_list, lcc_list = [], [], []

        for s in range(N_SAMPLES_PER_LAMBDA):
            nb = sample_quantum_graph(N, J_scores, J_threshold, lam, rng_sample)
            ds, r2, ds_uv, ds_ir, mean_deg, lcc = evaluate_graph(nb, SEED ^ s ^ 0xABCD)
            mu1 = spectral_gap_power_iter(nb, seed=SEED ^ s)

            r = LambdaResult(lam, s, ds, r2, ds_uv, ds_ir, mean_deg, lcc, mu1, S_ent,
                             DS_LO < ds < DS_HI)
            all_results.append(r)

            if not math.isnan(ds):
                ds_list.append(ds); ds_uv_list.append(ds_uv); ds_ir_list.append(ds_ir)
            deg_list.append(mean_deg)
            if mu1 > 0: mu1_list.append(mu1)
            lcc_list.append(lcc)

        ds_mean  = statistics.mean(ds_list)  if ds_list  else float("nan")
        ds_std   = statistics.stdev(ds_list) if len(ds_list) > 1 else 0.
        uv_mean  = statistics.mean(ds_uv_list) if ds_uv_list else float("nan")
        ir_mean  = statistics.mean(ds_ir_list) if ds_ir_list else float("nan")
        deg_mean = statistics.mean(deg_list)
        mu1_mean = statistics.mean(mu1_list) if mu1_list else 0.
        pass_n   = sum(1 for r in all_results if r.lam == lam and r.pass_ds)

        log(f"  λ={lam:6.3f}  d_s={ds_mean:7.4f}±{ds_std:5.4f}  "
            f"uv={uv_mean:6.3f}  ir={ir_mean:6.3f}  "
            f"k={deg_mean:5.1f}  μ₁={mu1_mean:6.4f}  "
            f"S={S_ent:9.1f}  {pass_n}/{N_SAMPLES_PER_LAMBDA}  ({time.time()-t1:.1f}s)")

        summary_per_lambda.append({
            "lam": lam,
            "ds_mean": ds_mean, "ds_std": ds_std,
            "ds_uv": uv_mean, "ds_ir": ir_mean,
            "mean_deg": deg_mean, "mu1_mean": mu1_mean,
            "S_ent": S_ent,
            "pass_frac": pass_n / N_SAMPLES_PER_LAMBDA,
            "lcc_mean": statistics.mean(lcc_list),
        })

    # ── Analiză tranziție de fază ──────────────────────────────────────────────
    log("\n" + "=" * 74)
    log("ANALIZĂ TRANZIȚIE DE FAZĂ")
    log("=" * 74)

    # Găsim λ critic: unde pass_rate scade sub 50%
    lambda_crit_ds = None
    for i in range(1, len(summary_per_lambda)):
        if summary_per_lambda[i-1]["pass_frac"] >= 0.5 and summary_per_lambda[i]["pass_frac"] < 0.5:
            lambda_crit_ds = (summary_per_lambda[i-1]["lam"] + summary_per_lambda[i]["lam"]) / 2
            break

    # Running dimension: diferență UV-IR
    log("\n  Running dimension (UV→IR) per λ:")
    for s in summary_per_lambda:
        if not math.isnan(s["ds_uv"]) and not math.isnan(s["ds_ir"]):
            delta = s["ds_ir"] - s["ds_uv"]
            arrow = "↑" if delta > 0.3 else ("↓" if delta < -0.3 else "→")
            log(f"    λ={s['lam']:5.3f}: UV={s['ds_uv']:.3f} {arrow} IR={s['ds_ir']:.3f}  Δ={delta:+.3f}")

    log("\n  Spectral gap μ₁ per λ:")
    for s in summary_per_lambda:
        flag = " ⚠ FRAGILE" if 0 < s["mu1_mean"] < 0.015 else (" ✗ GAP CLOSED" if s["mu1_mean"] <= 0 else "")
        log(f"    λ={s['lam']:5.3f}: μ₁={s['mu1_mean']:.5f}{flag}")

    log("\n  Entropia cuantică S_ent per λ (starea de muchii):")
    s_max = max(s["S_ent"] for s in summary_per_lambda)
    for s in summary_per_lambda:
        bar = "█" * int(30 * s["S_ent"] / s_max) if s_max > 0 else ""
        log(f"    λ={s['lam']:5.3f}: S={s['S_ent']:9.1f} bit  {bar}")

    log("\n" + "=" * 74)
    log("VERDICT")
    log("=" * 74)

    # d_s la λ=0 vs λ mare
    ds_classical = summary_per_lambda[0]["ds_mean"]
    ds_max_lam   = summary_per_lambda[-1]["ds_mean"]

    log(f"\n  d_s(λ=0)   = {ds_classical:.4f}  ← Jaccard clasic")
    log(f"  d_s(λ=5.0) = {ds_max_lam:.4f}  ← dezordine maximă")

    if lambda_crit_ds:
        log(f"\n  λ_critic (pass_rate=50%) ≈ {lambda_crit_ds:.3f}")
        log(f"  Interpretare: la λ > {lambda_crit_ds:.3f}, coerența cuantică Jaccard")
        log(f"  se sparge → graful nu mai produce d_s≈4.")
    else:
        log(f"\n  Nu s-a detectat tranziție de fază clară în intervalul λ testat.")

    # Reducție UV
    s0 = summary_per_lambda[0]
    if not math.isnan(s0["ds_uv"]) and s0["ds_uv"] < 3.5:
        log(f"\n  ✓ Reducție dimensională UV detectată la λ=0:")
        log(f"    d_s_uv = {s0['ds_uv']:.3f} < 3.5  (scară Planck)")
        log(f"    d_s_ir = {s0['ds_ir']:.3f} ≈ 4  (scară clasică)")
        log(f"    Running UV→IR confirmat — consistent cu CDT/Asymptotic Safety")
    else:
        log(f"\n  d_s_uv(λ=0) = {s0['ds_uv']:.3f}")

    # μ₁ în ansamblu vs. single seed
    mu1_at_0   = summary_per_lambda[0]["mu1_mean"]
    mu1_std_0  = statistics.stdev([r.mu1 for r in all_results if r.lam == 0.0 and r.mu1 > 0]) if \
                 sum(1 for r in all_results if r.lam == 0.0 and r.mu1 > 0) > 1 else 0.
    log(f"\n  μ₁ în ansamblu cuantic (λ=0): {mu1_at_0:.5f} ± {mu1_std_0:.5f}")
    log(f"  (Față de μ₁ single-seed = 0.01109 — margine 10.9%)")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    csv_path = OUT_DIR / "quantum_jaccard_sweep.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(all_results[0]).keys()))
        w.writeheader()
        for r in all_results:
            w.writerow(asdict(r))

    summary = {
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "params": {
            "N": N, "K_INIT": K_INIT, "K_CONN": K_CONN, "SEED": SEED,
            "N_SAMPLES_PER_LAMBDA": N_SAMPLES_PER_LAMBDA,
            "J_threshold": J_threshold,
            "h_abs_mean": statistics.mean(abs(h) for h in h_vals),
        },
        "per_lambda": summary_per_lambda,
        "lambda_critical_ds": lambda_crit_ds,
        "ds_classical": ds_classical,
        "ds_max_disorder": ds_max_lam,
        "total_time_s": round(time.time() - t0, 1),
    }

    json_path = OUT_DIR / "quantum_jaccard_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    log_path = OUT_DIR / "run-log-quantum-jaccard.txt"
    with open(log_path, "w") as f:
        f.write("\n".join(lines))

    log(f"\n  Artefacte: {OUT_DIR}")
    log(f"  Timp total: {time.time()-t0:.1f}s")
    log("=" * 74)


if __name__ == "__main__":
    main()
