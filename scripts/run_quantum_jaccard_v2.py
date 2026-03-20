#!/usr/bin/env python3
"""
Quantum Jaccard Graph v2 — Softmax Local Selection

PROBLEMA v1:
  Formularea cu prag global (h_{ij} = J(i,j) - J_mean) nu reproduce
  graful Jaccard clasic la λ=0. Cauza: selecția Jaccard clasică e
  LOCALĂ (top-k per nod), nu globală (threshold global pe J).

SOLUȚIA v2 — Gumbel-max trick:
  Fiecare nod i selectează k_conn vecini din distribuția:
    P(j | i, λ) ∝ exp(J(i,j) / λ)

  Implementat prin Gumbel-max:
    key_{ij} = J(i,j)/λ + Gumbel(0,1)
    Nodul i se conectează la top-k_{conn} j după key_{ij}

  Proprietăți:
    λ → 0 : top-k exact → Jaccard clasic (λ=0 e exact QNG curent)
    λ → ∞ : chei ≈ Gumbel(0,1) → selectie uniformă → ER

  Interpretare cuantică:
    λ = "temperatura cuantică" a grafului
    Graful clasic Jaccard e starea T=0 (zero quantum fluctuations)
    Fluctuațiile cuantice = imprecizii în selecția vecinilor

EXPERIMENTE:
  1. λ sweep [0, 0.001, 0.005, ..., 1.0] — faza structurală
  2. Fiecare λ: 30 sample-uri → statistici d_s, μ₁, running
  3. Detectare λ_c: unde pass_rate scade sub 50%
  4. Entropia Gumbel: H(P_i) per nod vs λ
  5. Comparație directă cu Jaccard clasic single-seed

FIZICA AȘTEPTATĂ:
  λ=0:       d_s ≈ 4.08 (reproduce clasicul, confirmare)
  λ mic:     d_s ≈ 4 (robust — e o fază, nu un punct?)
  λ_c:       tranziție de fază topologică
  λ mare:    d_s ≈ ER (> 4.5, pică G18d)
  UV/IR:     running d_s_UV < d_s_IR la λ mic? (predicție CDT)

Output:
  quantum_jaccard_v2_sweep.csv
  quantum_jaccard_v2_summary.json
  run-log-quantum-jaccard-v2.txt
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
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "quantum-jaccard-v2"

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

N_SAMPLES = 30   # sample-uri per λ

# Grid λ — dens la λ mic (zona de interes), rar la λ mare
LAMBDA_GRID = [
    0.000,                               # clasic pur (Jaccard exact)
    0.001, 0.002, 0.005,                 # fluctuații minime
    0.010, 0.020, 0.030, 0.050,          # regim cuantic slab
    0.075, 0.100, 0.150, 0.200,          # crossover
    0.300, 0.500, 1.000,                 # dezordine mare
]

DS_LO, DS_HI = 3.5, 4.5


# ── OLS și metrici de bază ────────────────────────────────────────────────────

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
    total  = n * n_walks
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


def spectral_gap(nb, n_iter=300, seed=42):
    """μ₁ = 1 - λ₂(W_lazy) prin power iteration."""
    n = len(nb)
    rng = random.Random(seed)
    deg = [max(len(x), 1) for x in nb]

    def matvec(v):
        out = [0.] * n
        for i in range(n):
            out[i] += 0.5 * v[i]
            for j in nb[i]:
                out[i] += 0.5 * v[j] / deg[j]
        return out

    v_stat = [math.sqrt(deg[i]) for i in range(n)]
    ns = math.sqrt(sum(x*x for x in v_stat))
    v_stat = [x/ns for x in v_stat]

    v = [rng.gauss(0, 1) for _ in range(n)]
    dot = sum(v[i]*v_stat[i] for i in range(n))
    v = [v[i] - dot*v_stat[i] for i in range(n)]
    nm = math.sqrt(sum(x*x for x in v))
    if nm < 1e-15: return 0.
    v = [x/nm for x in v]

    lam = 0.
    for _ in range(n_iter):
        v2 = matvec(v)
        dot = sum(v2[i]*v_stat[i] for i in range(n))
        v2 = [v2[i] - dot*v_stat[i] for i in range(n)]
        nm2 = math.sqrt(sum(x*x for x in v2))
        if nm2 < 1e-15: break
        lam = sum(v2[i]*v[i] for i in range(n)) / sum(v[i]*v[i] for i in range(n))
        v = [x/nm2 for x in v2]

    return max(0., 1. - lam)


def mean_clustering(nb):
    nb_sets = [set(x) for x in nb]
    total = 0.; cnt = 0
    for i in range(len(nb)):
        k = len(nb[i])
        if k < 2: continue
        tri = sum(1 for u in nb[i] for v in nb[i] if v > u and v in nb_sets[u])
        total += 2*tri / (k*(k-1)); cnt += 1
    return total/cnt if cnt else 0.


def lcc_size(nb):
    n = len(nb); vis = [False]*n; best = 0
    for s in range(n):
        if vis[s]: continue
        sz = 0; stack = [s]
        while stack:
            v = stack.pop()
            if vis[v]: continue
            vis[v] = True; sz += 1
            stack.extend(u for u in nb[v] if not vis[u])
        best = max(best, sz)
    return best


# ── Construcție Jaccard scores per nod ────────────────────────────────────────

def build_jaccard_per_node(n, k_init, seed):
    """
    Returnează: pentru fiecare nod i, lista sortată descendent
    [(J(i,j), j) for j != i], calculată pe graful ER contextual.
    """
    rng = random.Random(seed)
    p0  = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    scores_per_node = []
    for i in range(n):
        Ni = adj0[i] | {i}
        row = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            row.append((inter/union if union else 0., j))
        row.sort(reverse=True)
        scores_per_node.append(row)

    return scores_per_node


# ── Gumbel-max sampling ───────────────────────────────────────────────────────

def gumbel(rng):
    """Sampează din distribuția Gumbel(0,1): -log(-log(U))."""
    u = rng.random()
    while u < 1e-300: u = rng.random()
    return -math.log(-math.log(u))


def sample_quantum_graph_v2(n, scores_per_node, k_conn, lam, rng):
    """
    Gumbel-max trick pentru top-k sampling din softmax:
      key_{ij} = J(i,j)/λ + Gumbel(0,1)   (λ > 0)
      key_{ij} = J(i,j)                    (λ = 0, top-k exact)
    Nodul i se conectează la top k_conn j după key.
    Graf neorientat: muchia (i,j) există dacă i→j SAU j→i.
    """
    adj = [set() for _ in range(n)]

    for i in range(n):
        row = scores_per_node[i]
        if lam == 0.:
            # Top-k exact: primii k_conn din lista sortată
            for _, j in row[:k_conn]:
                adj[i].add(j); adj[j].add(i)
        else:
            # Gumbel-max: adaugă zgomot Gumbel scalat la fiecare scor
            keyed = [(J_ij / lam + gumbel(rng), j) for J_ij, j in row]
            keyed.sort(reverse=True)
            for _, j in keyed[:k_conn]:
                adj[i].add(j); adj[j].add(i)

    return [sorted(s) for s in adj]


# ── Entropia selecției per nod ────────────────────────────────────────────────

def softmax_entropy_per_node(scores_per_node, lam):
    """
    Entropia Shannon a distribuției softmax pentru fiecare nod.
    H_i = -Σ_j p_{ij} log p_{ij}   unde p_{ij} = softmax(J(i,j)/λ)_j
    La λ=0: H=0 (certitudine absolută — top-k determinist).
    La λ→∞: H=log(n-1) (uniformă).
    Returnăm media și std peste noduri.
    """
    if lam == 0.:
        return 0., 0.
    entropies = []
    for row in scores_per_node:
        logits = [J/lam for J, _ in row]
        max_l  = max(logits)
        ws     = [math.exp(l - max_l) for l in logits]
        Z      = sum(ws)
        ps     = [w/Z for w in ws]
        H = -sum(p * math.log(p) for p in ps if p > 1e-300)
        entropies.append(H)
    return statistics.mean(entropies), statistics.stdev(entropies)


def evaluate(nb, seed):
    rng = random.Random(seed)
    P_t  = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds,   r2  = ds_window(P_t, T_LO, T_HI)
    ds_uv, _  = ds_window(P_t, UV_LO, UV_HI)
    ds_ir, _  = ds_window(P_t, IR_LO, IR_HI)
    md   = sum(len(x) for x in nb) / len(nb)
    return ds, r2, ds_uv, ds_ir, md


# ── Main ───────────────────────────────────────────────────────────────────────

@dataclass
class SampleResult:
    lam:      float
    sample:   int
    ds:       float
    r2:       float
    ds_uv:    float
    ds_ir:    float
    mean_deg: float
    mu1:      float
    clust:    float
    lcc:      int
    H_mean:   float   # entropia medie softmax per nod
    H_std:    float
    pass_ds:  bool


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    def log(msg=""):
        print(msg); lines.append(msg)

    t0 = time.time()
    log("=" * 76)
    log("QUANTUM JACCARD v2 — Gumbel-max Local Selection")
    log(f"Run: {datetime.utcnow().isoformat()}Z")
    log(f"N={N}, K_INIT={K_INIT}, K_CONN={K_CONN}, SEED={SEED}")
    log(f"N_SAMPLES={N_SAMPLES}, λ values: {len(LAMBDA_GRID)}")
    log("=" * 76)
    log("")
    log("Formulare: key(i→j; λ) = J(i,j)/λ + Gumbel(0,1)")
    log("           nod i → top-K_CONN j după key")
    log("           λ=0: Jaccard clasic exact | λ→∞: ER uniform")
    log("")

    # ── Build scores (o singură dată) ─────────────────────────────────────────
    log("[INIT] Calculez scoruri Jaccard per nod...")
    t1 = time.time()
    scores_per_node = build_jaccard_per_node(N, K_INIT, SEED)
    log(f"  Done ({time.time()-t1:.1f}s)")

    # Verifică că la λ=0 reproduce graful clasic (sanity check)
    rng_check = random.Random(SEED ^ 0xFACE)
    nb_check  = sample_quantum_graph_v2(N, scores_per_node, K_CONN, 0.0, rng_check)
    md_check  = sum(len(x) for x in nb_check) / N
    log(f"  Sanity check λ=0: mean_deg = {md_check:.2f}  (expected ≈ 9.4)")

    # ── Header tabel ──────────────────────────────────────────────────────────
    log("")
    log("─" * 76)
    log(f"{'λ':>7}  {'d_s':>8}  {'±':>6}  {'d_uv':>6}  {'d_ir':>6}  "
        f"{'<k>':>5}  {'μ₁':>7}  {'C':>6}  {'H_nod':>7}  {'PASS':>7}")
    log("─" * 76)

    all_results: list[SampleResult] = []
    summary_per_lam = []

    for lam in LAMBDA_GRID:
        t1 = time.time()
        rng_s = random.Random(SEED ^ int(lam * 1e7) ^ 0xC0FFEE)

        # Entropia softmax (deterministă în λ)
        H_mean, H_std = softmax_entropy_per_node(scores_per_node, lam)

        ds_l, ds_uv_l, ds_ir_l = [], [], []
        md_l, mu1_l, cl_l      = [], [], []
        lcc_l                  = []

        for s in range(N_SAMPLES):
            nb  = sample_quantum_graph_v2(N, scores_per_node, K_CONN, lam, rng_s)
            ds, r2, ds_uv, ds_ir, md = evaluate(nb, SEED ^ s ^ 0xABCD)
            mu  = spectral_gap(nb, seed=SEED ^ s)
            cl  = mean_clustering(nb)
            lcc = lcc_size(nb)

            r = SampleResult(lam, s, ds, r2, ds_uv, ds_ir, md,
                             mu, cl, lcc, H_mean, H_std,
                             DS_LO < ds < DS_HI)
            all_results.append(r)

            if not math.isnan(ds):
                ds_l.append(ds); ds_uv_l.append(ds_uv); ds_ir_l.append(ds_ir)
            md_l.append(md)
            if mu > 0: mu1_l.append(mu)
            cl_l.append(cl); lcc_l.append(lcc)

        ds_mean  = statistics.mean(ds_l)  if ds_l  else float("nan")
        ds_std   = statistics.stdev(ds_l) if len(ds_l) > 1 else 0.
        uv_mean  = statistics.mean(ds_uv_l) if ds_uv_l else float("nan")
        ir_mean  = statistics.mean(ds_ir_l) if ds_ir_l else float("nan")
        md_mean  = statistics.mean(md_l)
        mu1_mean = statistics.mean(mu1_l) if mu1_l else 0.
        cl_mean  = statistics.mean(cl_l)
        pass_n   = sum(1 for r in all_results if r.lam == lam and r.pass_ds)

        log(f"  λ={lam:5.3f}  {ds_mean:7.4f}  ±{ds_std:5.4f}  "
            f"{uv_mean:6.3f}  {ir_mean:6.3f}  "
            f"{md_mean:5.1f}  {mu1_mean:6.4f}  {cl_mean:6.4f}  "
            f"{H_mean:7.4f}  {pass_n:2d}/{N_SAMPLES}  ({time.time()-t1:.1f}s)")

        summary_per_lam.append({
            "lam": lam,
            "ds_mean": ds_mean, "ds_std": ds_std,
            "ds_uv": uv_mean,   "ds_ir": ir_mean,
            "mean_deg": md_mean, "mu1_mean": mu1_mean,
            "clustering": cl_mean,
            "lcc_mean": statistics.mean(lcc_l),
            "H_mean": H_mean, "H_std": H_std,
            "pass_frac": pass_n / N_SAMPLES,
        })

    # ── Analiză ───────────────────────────────────────────────────────────────
    log("")
    log("=" * 76)
    log("ANALIZĂ")
    log("=" * 76)

    # λ_c: primul λ unde pass_rate < 50%
    lam_c = None
    for i in range(1, len(summary_per_lam)):
        if (summary_per_lam[i-1]["pass_frac"] >= 0.5 and
                summary_per_lam[i]["pass_frac"] < 0.5):
            lam_c = (summary_per_lam[i-1]["lam"] + summary_per_lam[i]["lam"]) / 2
            break

    # λ cu cea mai mare pass_rate
    best = max(summary_per_lam, key=lambda s: s["pass_frac"])

    # Running dimension (UV < IR → bun)
    log("\n── Running dimension UV→IR ───────────────────────────────────────────")
    for s in summary_per_lam:
        if math.isnan(s["ds_uv"]) or math.isnan(s["ds_ir"]): continue
        delta = s["ds_ir"] - s["ds_uv"]
        if delta > 0.5:
            tag = "↑↑ UV→IR running (CDT-like)"
        elif delta > 0.1:
            tag = "↑  UV→IR slab"
        elif delta < -0.5:
            tag = "↓↓ IR→UV invers (supradens)"
        else:
            tag = "→  plat"
        log(f"    λ={s['lam']:5.3f}: {s['ds_uv']:.3f} → {s['ds_ir']:.3f}  "
            f"Δ={delta:+.3f}  {tag}")

    # Spectral gap
    log("\n── Spectral gap μ₁ ──────────────────────────────────────────────────")
    for s in summary_per_lam:
        flag = ""
        if 0 < s["mu1_mean"] < 0.015: flag = " ⚠ FRAGILE"
        elif s["mu1_mean"] == 0:      flag = " ✗ DISCONNECTED"
        log(f"    λ={s['lam']:5.3f}: μ₁={s['mu1_mean']:.5f}{flag}")

    # Entropia selecției
    log("\n── Entropia selecției per nod H(λ) ──────────────────────────────────")
    h_max = max(s["H_mean"] for s in summary_per_lam)
    for s in summary_per_lam:
        bar = "█" * int(40 * s["H_mean"] / h_max) if h_max > 0 else ""
        log(f"    λ={s['lam']:5.3f}: H={s['H_mean']:7.4f} nats  {bar}")

    # ── Verdict ───────────────────────────────────────────────────────────────
    log("")
    log("=" * 76)
    log("VERDICT")
    log("=" * 76)

    s0 = summary_per_lam[0]
    log(f"\n  λ=0 (Jaccard clasic):  d_s={s0['ds_mean']:.4f}  "
        f"k={s0['mean_deg']:.1f}  μ₁={s0['mu1_mean']:.5f}  "
        f"PASS={s0['pass_frac']*100:.0f}%")

    log(f"\n  Best λ:  λ={best['lam']:.3f}  d_s={best['ds_mean']:.4f}  "
        f"PASS={best['pass_frac']*100:.0f}%")

    if lam_c:
        log(f"\n  λ_critic (50% pass): λ_c ≈ {lam_c:.4f}")
    else:
        log(f"\n  λ_c: pass_rate rămâne ridicat în tot intervalul testat.")

    # Răspuns la întrebările cheie
    log("\n── Întrebări cheie ──────────────────────────────────────────────────")

    # Q1: d_s=4 e o fază sau un punct?
    n_pass_high = sum(1 for s in summary_per_lam if s["pass_frac"] >= 0.5)
    if n_pass_high >= 3:
        log(f"  Q1: d_s≈4 e o FAZĂ (robust pe {n_pass_high} valori λ) ✓")
    elif n_pass_high >= 1:
        log(f"  Q1: d_s≈4 e un PUNCT ÎNGUST (pass la {n_pass_high} λ) ~")
    else:
        log(f"  Q1: d_s≈4 e fragil — apare rar în ansamblu ✗")

    # Q2: Running dimension CDT-like?
    running_at_0 = s0["ds_ir"] - s0["ds_uv"]
    if running_at_0 > 0.3:
        log(f"  Q2: Running UV→IR la λ=0: Δ={running_at_0:+.3f} ✓ (CDT-like)")
    else:
        log(f"  Q2: Running UV→IR la λ=0: Δ={running_at_0:+.3f} — slab sau absent")

    # Q3: μ₁ mai stabil în ansamblu?
    mu1_at_0   = s0["mu1_mean"]
    mu1_at_001 = next((s["mu1_mean"] for s in summary_per_lam if s["lam"] == 0.001), None)
    if mu1_at_0 < 0.01 and mu1_at_001 and mu1_at_001 > 0.01:
        log(f"  Q3: μ₁ crește de la {mu1_at_0:.5f} (λ=0) la {mu1_at_001:.5f} (λ=0.001)")
        log(f"      Fluctuații cuantice mici STABILIZEAZĂ spectral gap ✓")
    elif mu1_at_0 > 0.01:
        log(f"  Q3: μ₁(λ=0) = {mu1_at_0:.5f} > 0.01 — deja stabil la λ=0 ✓")

    # Q4: La ce λ corespunde graful Jaccard clasic real?
    #     Îl detectăm prin: d_s ≈ 4.082 ± 0.125 (valoarea din G18d)
    TARGET_DS = 4.082
    closest = min(summary_per_lam, key=lambda s: abs(s["ds_mean"] - TARGET_DS)
                  if not math.isnan(s["ds_mean"]) else 999)
    log(f"  Q4: λ_eff (d_s≈{TARGET_DS}) = {closest['lam']:.3f}  "
        f"(d_s={closest['ds_mean']:.4f})")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    csv_path = OUT_DIR / "quantum_jaccard_v2_sweep.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(all_results[0]).keys()))
        w.writeheader()
        for r in all_results: w.writerow(asdict(r))

    summary = {
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "params": {"N": N, "K_INIT": K_INIT, "K_CONN": K_CONN, "SEED": SEED,
                   "N_SAMPLES": N_SAMPLES},
        "per_lambda": summary_per_lam,
        "lambda_critical": lam_c,
        "best_lambda": {"lam": best["lam"], "ds_mean": best["ds_mean"],
                        "pass_frac": best["pass_frac"]},
        "lambda_eff_for_classical_ds": closest["lam"],
        "total_time_s": round(time.time() - t0, 1),
    }

    with open(OUT_DIR / "quantum_jaccard_v2_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    with open(OUT_DIR / "run-log-quantum-jaccard-v2.txt", "w") as f:
        f.write("\n".join(lines))

    log(f"\n  Artefacte: {OUT_DIR}")
    log(f"  Timp total: {time.time()-t0:.1f}s")
    log("=" * 76)


if __name__ == "__main__":
    main()
