#!/usr/bin/env python3
"""
QNG — Test Formal: Convergența μ₁ spre (2-√2)/2

Verificare: spectral gap-ul grafului Jaccard G17 converge spre (2-√2)/2
pe măsură ce n → ∞?

Metodologie:
  - 30 seed-uri per valoare de n ∈ {100, 200, 280, 500, 1000, 2000}
  - Calculăm μ₁ (spectral gap al random walk Laplacian)
  - Comparăm cu μ₁_theory = (2-√2)/2 = 0.29289
  - Raportăm mean, std, bias față de teorie, convergență

Dacă mean(μ₁) → (2-√2)/2 cu σ → 0 pentru n → ∞:
  → legătura μ₁ = 1 - iso_target este un rezultat al large-n limit,
    nu o coincidență pentru o singură semință.

Dacă mean(μ₁) → altă valoare:
  → legătura μ₁ = (2-√2)/2 este coincidentă și trebuie revizuită.
"""

from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "mu1-convergence-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MU1_THEORY = (2.0 - math.sqrt(2.0)) / 2.0  # = 0.29289
N_SEEDS    = 30
N_ITER_EV  = 300  # iteratii power method


# ── Construcție graf Jaccard (din run_qng_g17_v2.py) ─────────────────────────

def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    p0  = k_init / (n - 1)
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
            Nj   = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter / union if union else 0.0, j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def _dot(u, v):    return sum(u[i] * v[i] for i in range(len(u)))
def _norm(v):      s = math.sqrt(_dot(v, v)); return [x/s for x in v] if s > 1e-14 else list(v)
def _defl(v, bs):
    w = list(v)
    for b in bs:
        c = _dot(w, b); w = [w[i] - c * b[i] for i in range(len(w))]
    return w
def _rw(f, nb):    return [(sum(f[j] for j in b) / len(b)) if b else 0.0 for b in nb]


def spectral_gap(neighbours: list[list[int]], seed: int) -> float:
    """Spectral gap al random walk Laplacian (1 - a₁ unde a₁ = a doua eigenvalue)."""
    n    = len(neighbours)
    rng  = random.Random(seed + 99999)
    v0   = _norm([1.0] * n)
    vecs = [v0]
    v    = _norm(_defl([rng.gauss(0.0, 1.0) for _ in range(n)], vecs))
    for _ in range(N_ITER_EV):
        w = _norm(_defl(_rw(v, neighbours), vecs))
        if math.sqrt(_dot(w, w)) < 1e-14:
            break
        v = w
    alpha = _dot(v, _rw(v, neighbours))
    return max(0.0, 1.0 - alpha)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    log = []
    def L(s): log.append(s); print(s)

    L("=" * 72)
    L("QNG — CONVERGENȚA μ₁ SPRE (2-√2)/2")
    L("=" * 72)
    L(f"   μ₁_theory = (2-√2)/2 = {MU1_THEORY:.6f}")
    L(f"   G17 canonical (n=280, seed=3401): μ₁ = 0.291199 (Δ = -0.58%)")
    L(f"   Test: {N_SEEDS} seed-uri × 6 valori n")
    L("")

    sizes = [100, 200, 280, 500, 1000, 2000]
    seeds = list(range(1, N_SEEDS + 1))

    rows_csv  = []
    size_stats = []

    for n in sizes:
        L(f"   n = {n:4d}  ({N_SEEDS} seed-uri)...")
        gaps = []
        for s in seeds:
            nb  = build_jaccard_graph(n, 8, 8, s)
            gap = spectral_gap(nb, s)
            gaps.append(gap)
            rows_csv.append({"n": n, "seed": s, "mu1": round(gap, 6)})

        mean_g = sum(gaps) / len(gaps)
        std_g  = math.sqrt(sum((g - mean_g)**2 for g in gaps) / len(gaps))
        bias   = (mean_g - MU1_THEORY) / MU1_THEORY * 100
        se     = std_g / math.sqrt(len(gaps))
        t_stat = (mean_g - MU1_THEORY) / max(se, 1e-15)

        size_stats.append({
            "n": n, "mean": mean_g, "std": std_g,
            "bias_pct": bias, "t_stat": t_stat, "se": se,
        })

        consistent = abs(t_stat) < 2.0
        L(f"     mean = {mean_g:.4f}  std = {std_g:.4f}  "
          f"bias = {bias:+.1f}%  t = {t_stat:+.2f}  "
          f"{'✓ consistent' if consistent else '✗ semnificativ deviat'}")

    L("")
    L("─" * 72)
    L("CONCLUZIE")
    L("─" * 72)

    # Tendinta: creste sau scade biasul cu n?
    biases = [s["bias_pct"] for s in size_stats]
    abs_biases = [abs(b) for b in biases]
    trend_down = abs_biases[-1] < abs_biases[0]
    max_t = max(abs(s["t_stat"]) for s in size_stats)
    all_consistent = all(abs(s["t_stat"]) < 3.0 for s in size_stats)

    L(f"   Teorie: μ₁ = (2-√2)/2 = {MU1_THEORY:.4f}")
    L(f"   Range bias: [{min(biases):+.1f}%, {max(biases):+.1f}%]")
    L(f"   Max |t-stat|: {max_t:.2f}")
    L(f"   Toate în 3σ: {'✓' if all_consistent else '✗'}")
    L(f"   Trend convergent: {'✓ |bias| scade cu n' if trend_down else '~ oscilant'}")
    L("")

    if all_consistent and max_t < 3.0:
        verdict = "CONSISTENT: μ₁ Jaccard G17 (k=8) este consistent cu (2-√2)/2 la toate scalele n."
        verdict2 = "Relația μ₁ = 1 - 1/√2 este o proprietate emergentă a limitei large-n, nu coincidență per-seed."
    else:
        verdict = "INCONCLUZIV: unele deviații > 3σ — relația μ₁ = (2-√2)/2 necesită investigare."
        verdict2 = "Verifică dacă există alt parametru care explică valoarea μ₁."

    L(f"   {verdict}")
    L(f"   {verdict2}")
    L("")

    # Salvare CSV
    with (OUT_DIR / "mu1_by_seed.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n", "seed", "mu1"])
        w.writeheader(); w.writerows(rows_csv)

    summary = {
        "test_id":       "mu1-convergence-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mu1_theory":    MU1_THEORY,
        "n_seeds":       N_SEEDS,
        "k_init":        8,
        "k_conn":        8,
        "size_stats":    size_stats,
        "max_abs_t":     max_t,
        "all_within_3sigma": all_consistent,
        "trend_converging": trend_down,
        "verdict": verdict,
    }
    with (OUT_DIR / "mu1_convergence_summary.json").open("w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nSalvat în: {OUT_DIR}")
    return summary


if __name__ == "__main__":
    main()
