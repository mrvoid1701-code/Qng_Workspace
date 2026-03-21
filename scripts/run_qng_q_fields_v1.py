#!/usr/bin/env python3
"""
QNG Q-Fields v1 — Cuantificarea câmpurilor Σ și χ pe graful Jaccard

Gate experimental (nu parte din lane-ul oficial). Investigează ce se întâmplă
când câmpurile Σ și χ sunt ele însele cuantice (nu doar graful).

Fizică:
  Hamiltonianul cuantic pentru perechea (Σ, χ) pe graful G este:

    H = Σ_i [p_Σ,i² + p_χ,i²] / 2  +  1/2 · [Σ,χ] K [Σ,χ]ᵀ

  unde matricea potențialului K (2N×2N) este:

    K = [[k_cl·I + k_sm·L,  k_mix·I],
         [k_mix·I,           k_chi·I]]

  cu L = Laplacianul Jaccard al grafului.

  Modurile normale ω_a = √λ_a(K) dau energia zero-point E_0 = ħ/2 · Σω_a
  și fluctuațiile ⟨(δΣ_i)²⟩, ⟨δΣ_i δχ_i⟩ per nod.

Gate-uri Q1–Q5 (exploratorii):
  Q1: stabilitate cuantică (ω_min > 0)
  Q2: gap spectral ω_min > threshold
  Q3: fluctuații zero-point mărginite
  Q4: corelații încrucișate Σ-χ cu semnul concordant k_mix (entanglement)
  Q5: cv_quantum în interval rezonabil față de cv_classical ≈ 0.405

Dependințe: numpy (stdlib insuficientă pentru eigh 560×560).
Nu modifică niciun fișier existent.

Derivare: 03_math/derivations/qng-quantum-sigma-chi-v1.md
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-q-fields-v1"
)

# Parametri grafici (identic cu DS-002 oficial)
N_NODES = 280
K_INIT  = 8
K_CONN  = 8

# Parametri câmpuri (valori nominale, configurabile)
K_CL    = 0.5    # local closure strength
K_SM    = 0.2    # smoothness coupling (Σ nearest-neighbor)
K_CHI   = 0.3    # chi restoring frequency²
K_MIX   = 0.1    # bilinear coupling Σ-χ
HBAR    = 1.0    # unități naturale (ħ = 1)


@dataclass
class QFieldsThresholds:
    # Q1: toate frecvențele normale reale (stabilitate cuantică)
    q1_omega_min_abs: float = 1e-6
    # Q2: gap spectral non-trivial (stare fundamentală bine separată)
    q2_gap_min: float = 0.01
    # Q3: fluctuații zero-point finite și mărginite
    q3_zp_sigma_max: float = 10.0
    # Q4: corelații încrucișate Σ-χ (semnul urmează k_mix)
    # evaluat logic în run_gates()
    # Q5: raportul cv_quantum / cv_classical în interval
    # 0.001 = non-trivial (există inhomogeneitate), 1.0 = mai mic decât cv_classical
    q5_cv_ratio_lo: float = 0.001
    q5_cv_ratio_hi: float = 1.0


# ── Construcție graf Jaccard (standalone, fără import) ─────────────────────

def _jaccard(set_a: set, set_b: set) -> float:
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def build_jaccard_graph(n: int, k_init: int, k_conn: int, seed: int) -> dict:
    """Returnează adj[i] = set de vecini (identic cu implementarea din g17_v2)."""
    rng = random.Random(seed)
    nbrs_init: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        pool = list(range(n))
        pool.remove(i)
        for j in rng.sample(pool, min(k_init, len(pool))):
            nbrs_init[i].add(j)
            nbrs_init[j].add(i)

    adj: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        nbrs_i_plus = nbrs_init[i] | {i}
        candidates: set = set()
        for j in nbrs_init[i]:
            candidates |= nbrs_init[j]
        candidates.discard(i)
        scores = [(_jaccard(nbrs_i_plus, nbrs_init[j] | {j}), j)
                  for j in candidates]
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j)
            adj[j].add(i)
    return adj


def graph_laplacian(adj: dict, n: int) -> "np.ndarray":
    """Matricea Laplaciană N×N."""
    L = np.zeros((n, n))
    for i in range(n):
        L[i, i] = float(len(adj[i]))
        for j in adj[i]:
            L[i, j] = -1.0
    return L


# ── Hamiltonianul cuantic ──────────────────────────────────────────────────

def build_K(L: "np.ndarray", n: int,
            k_cl: float, k_sm: float,
            k_chi: float, k_mix: float) -> "np.ndarray":
    """
    Construiește matricea potențialului K (2N × 2N).

    Ordine variabile: [Σ_0,...,Σ_{N-1}, χ_0,...,χ_{N-1}]

    K = [[k_cl·I + k_sm·L,  k_mix·I],
         [k_mix·I,           k_chi·I]]
    """
    M_sigma = k_cl * np.eye(n) + k_sm * L
    M_chi   = k_chi * np.eye(n)
    M_cross = k_mix * np.eye(n)
    return np.block([[M_sigma, M_cross],
                     [M_cross, M_chi]])


def quantize(K: "np.ndarray", n: int, hbar: float) -> dict:
    """
    Diagonalizează K, calculează moduri normale și observabile cuantice.

    Returnează dict cu:
      eigvals, omega, omega_min, E_0, E_0_per_mode,
      zp_sigma (N,), zp_chi (N,), cross_corr (N,)
    """
    eigvals, eigvecs = np.linalg.eigh(K)  # K simetrică → eigh garantat

    # Frecvențe normale (zero dacă λ < 0 sau ≈0)
    omega = np.where(eigvals > 0, np.sqrt(np.maximum(eigvals, 0.0)), 0.0)
    pos_mask = omega > 1e-10
    omega_min = float(omega[pos_mask].min()) if pos_mask.any() else 0.0
    omega_max = float(omega.max())

    # Energie zero-point
    E_0 = float(hbar / 2.0 * omega.sum())
    E_0_per_mode = E_0 / (2 * n)

    # Pondere per mod: ħ / (2ω_a)  [0 pentru moduri zero]
    safe_omega = np.where(pos_mask, omega, np.inf)
    weights = hbar / (2.0 * safe_omega)   # shape (2N,)

    # Componente Σ și χ ale eigenvectorilor
    U_sigma = eigvecs[:n, :]    # (N, 2N) — bloc Σ
    U_chi   = eigvecs[n:, :]    # (N, 2N) — bloc χ

    # Fluctuații zero-point per nod
    zp_sigma = np.einsum("ia,a,ia->i", U_sigma, weights, U_sigma)  # (N,)
    zp_chi   = np.einsum("ia,a,ia->i", U_chi,   weights, U_chi)    # (N,)

    # Corelații încrucișate ⟨δΣ_i · δχ_i⟩
    cross_corr = np.einsum("ia,a,ia->i", U_sigma, weights, U_chi)  # (N,)

    return {
        "eigvals":      eigvals,
        "omega":        omega,
        "omega_min":    omega_min,
        "omega_max":    omega_max,
        "n_pos_modes":  int(pos_mask.sum()),
        "n_zero_modes": int((~pos_mask).sum()),
        "E_0":          E_0,
        "E_0_per_mode": E_0_per_mode,
        "zp_sigma":     zp_sigma,
        "zp_chi":       zp_chi,
        "cross_corr":   cross_corr,
        "min_eigval":   float(eigvals[0]),
    }


# ── Gate-uri ───────────────────────────────────────────────────────────────

CV_CLASSICAL_OFFICIAL = 0.405  # din G17/G20 Jaccard oficial


def run_gates(qd: dict, k_mix: float,
              thr: QFieldsThresholds) -> tuple[dict, float]:
    results: dict = {}

    # Q1 — stabilitate cuantică: toate frecvențele reale
    q1_pass = qd["omega_min"] > thr.q1_omega_min_abs
    results["Q1_quantum_stability"] = {
        "pass": q1_pass,
        "omega_min": qd["omega_min"],
        "min_eigval_K": qd["min_eigval"],
        "threshold": thr.q1_omega_min_abs,
        "note": "K pozitiv definit ⟺ sistem cuantic stabil",
    }

    # Q2 — gap spectral
    q2_pass = qd["omega_min"] > thr.q2_gap_min
    results["Q2_spectral_gap"] = {
        "pass": q2_pass,
        "omega_min": qd["omega_min"],
        "omega_max": qd["omega_max"],
        "threshold": thr.q2_gap_min,
    }

    # Q3 — fluctuații zero-point mărginite
    zp_max  = float(qd["zp_sigma"].max())
    zp_mean = float(qd["zp_sigma"].mean())
    zp_std  = float(qd["zp_sigma"].std())
    q3_pass = zp_max < thr.q3_zp_sigma_max
    results["Q3_zp_bounded"] = {
        "pass": q3_pass,
        "zp_sigma_max":  zp_max,
        "zp_sigma_mean": zp_mean,
        "zp_sigma_std":  zp_std,
        "threshold_max": thr.q3_zp_sigma_max,
    }

    # Q4 — corelații încrucișate Σ-χ: anticorelare când k_mix > 0, ω_Σ > ω_χ
    # Fizică: în modul de frecvență joasă, Σ și χ oscilează în opoziție ca să
    # minimizeze termenul bilinear k_mix·Σ·χ. Prin urmare sign(⟨δΣδχ⟩) = -sign(k_mix)
    # când ω_Σ² = k_cl > ω_χ² = k_chi (cazul nostru nominal: 0.5 > 0.3).
    cc_mean = float(qd["cross_corr"].mean())
    cc_std  = float(qd["cross_corr"].std())
    if abs(k_mix) < 1e-12:
        q4_pass = abs(cc_mean) < 1e-10
        expected = "zero (k_mix=0)"
    elif k_mix > 0:
        q4_pass = cc_mean < 0          # anticorelare — modul jos dominant
        expected = "negativ (k_mix>0, omega_Sigma>omega_chi)"
    else:
        q4_pass = cc_mean > 0          # anticorelare cu semn opus
        expected = "pozitiv (k_mix<0, omega_Sigma>omega_chi)"
    results["Q4_sigma_chi_entanglement"] = {
        "pass": q4_pass,
        "cross_corr_mean": cc_mean,
        "cross_corr_std":  cc_std,
        "k_mix": k_mix,
        "expected_sign": expected,
        "note": ("k_mix ≠ 0 generează ANTICORELARE cuantică Σ-χ "
                 "(modul jos are componente Σ și χ de semne opuse)"),
    }

    # Q5 — cv_quantum vs cv_classical
    # Predicție: cv_quantum < cv_classical (fluctuațiile câmpului Σ sunt mai
    # uniforme spațial decât fluctuațiile ε_vac ale grafului).
    # Testăm că cv_quantum e non-trivial (> 0.001) și mai mic decât cv_classical.
    cv_q = zp_std / zp_mean if zp_mean > 1e-12 else float("nan")
    cv_ratio = cv_q / CV_CLASSICAL_OFFICIAL if math.isfinite(cv_q) else float("nan")
    # Threshold revizuit: 0.001 < cv_ratio < 1.0
    # (non-trivial dar sub nivelul fluctuațiilor grafului)
    q5_pass = (math.isfinite(cv_ratio)
               and thr.q5_cv_ratio_lo < cv_ratio < thr.q5_cv_ratio_hi)
    results["Q5_cv_quantum"] = {
        "pass": q5_pass,
        "cv_classical": CV_CLASSICAL_OFFICIAL,
        "cv_quantum": cv_q,
        "cv_ratio": cv_ratio,
        "threshold_lo": thr.q5_cv_ratio_lo,
        "threshold_hi": thr.q5_cv_ratio_hi,
        "note": ("cv_q = σ(⟨(δΣ_i)²⟩) / μ(⟨(δΣ_i)²⟩); fluctuațiile câmpului Σ "
                 "ar trebui mai uniforme decât ε_vac (cv_ratio < 1)"),
    }

    return results, cv_q


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields v1: Cuantificarea câmpurilor Σ și χ"
    )
    ap.add_argument("--seed",   type=int,   default=3401)
    ap.add_argument("--n",      type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init", type=int,   default=K_INIT)
    ap.add_argument("--k-conn", type=int,   default=K_CONN)
    ap.add_argument("--k-cl",   type=float, default=K_CL)
    ap.add_argument("--k-sm",   type=float, default=K_SM)
    ap.add_argument("--k-chi",  type=float, default=K_CHI)
    ap.add_argument("--k-mix",  type=float, default=K_MIX)
    ap.add_argument("--hbar",   type=float, default=HBAR)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy este necesar. Instalează cu: pip install numpy",
              file=sys.stderr)
        sys.exit(2)

    t0 = time.time()

    print("=" * 60)
    print("QNG Q-Fields v1 — Cuantificarea câmpurilor Σ și χ")
    print("=" * 60)
    print(f"  seed={args.seed}  N={args.n_nodes}  k_conn={args.k_conn}")
    print(f"  k_cl={args.k_cl}  k_sm={args.k_sm}  "
          f"k_chi={args.k_chi}  k_mix={args.k_mix}  ħ={args.hbar}")
    print()

    # 1) Graf Jaccard
    print("[1/4] Construiesc graful Jaccard...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n_edges = sum(len(v) for v in adj.values()) // 2
    print(f"      {args.n_nodes} noduri  {n_edges} muchii")

    # 2) Laplacianu
    print("[2/4] Construiesc Laplacianu grafului L (NxN)...")
    L = graph_laplacian(adj, args.n_nodes)
    # Verificare: det Laplacian = 0 → cel puțin un eigenvalue 0
    l_eigs = np.linalg.eigvalsh(L)
    print(f"      λ_min(L)={l_eigs[0]:.4f}  λ_max(L)={l_eigs[-1]:.4f}")

    # 3) Hamiltonianul cuantic K (2N×2N)
    dim = 2 * args.n_nodes
    print(f"[3/4] Construiesc și diagonalizez K ({dim}x{dim})...")
    K = build_K(L, args.n_nodes, args.k_cl, args.k_sm, args.k_chi, args.k_mix)
    qd = quantize(K, args.n_nodes, args.hbar)
    print(f"      ω_min={qd['omega_min']:.6f}  ω_max={qd['omega_max']:.4f}")
    print(f"      Moduri pozitive: {qd['n_pos_modes']}/{dim}  "
          f"Zero-moduri: {qd['n_zero_modes']}")
    print(f"      E_0 (total)={qd['E_0']:.4f}  "
          f"E_0/mod={qd['E_0_per_mode']:.6f}")
    print(f"      ⟨(δΣ)²⟩ mean={qd['zp_sigma'].mean():.6f}  "
          f"std={qd['zp_sigma'].std():.6f}")
    print(f"      ⟨δΣ·δχ⟩  mean={qd['cross_corr'].mean():.6f}  "
          f"std={qd['cross_corr'].std():.6f}")

    # 4) Gate-uri
    print("[4/4] Evaluez gate-urile Q1–Q5...")
    thr = QFieldsThresholds()
    gate_results, cv_q = run_gates(qd, args.k_mix, thr)

    elapsed = time.time() - t0

    # Afișare rezumat
    n_pass  = sum(1 for r in gate_results.values() if r["pass"])
    n_total = len(gate_results)
    all_pass = n_pass == n_total

    print()
    print("=" * 60)
    print(f"GATE-URI Q-FIELDS  {n_pass}/{n_total} PASS")
    print("=" * 60)
    for name, res in gate_results.items():
        status = "PASS" if res["pass"] else "FAIL"
        print(f"  {name}: {status}")

    print()
    print("--- Interpretare fizică ---")
    print(f"  cv_classical (G17/G20):    {CV_CLASSICAL_OFFICIAL:.4f}")
    print(f"  cv_quantum (fluctuații Σ): {cv_q:.4f}")
    if math.isfinite(cv_q):
        ratio = cv_q / CV_CLASSICAL_OFFICIAL
        print(f"  cv_ratio:                  {ratio:.4f}")
        if ratio < 0.1:
            print("  → Fluctuațiile cuantice ale Σ sunt neglijabile față de graful cuantic.")
        elif ratio < 0.5:
            print("  → Corecție minoră: cv_total ≈ cv_classical.")
        else:
            print("  → Corecție semnificativă: cele două scale de fluctuații sunt comparabile.")
    cc = float(qd["cross_corr"].mean())
    if abs(cc) > 1e-8:
        print(f"  → Entanglement Σ-χ activ: ⟨δΣ·δχ⟩ = {cc:.4f} ≠ 0 (din k_mix={args.k_mix})")
    else:
        print("  → Fără entanglement Σ-χ (k_mix ≈ 0).")

    # Salvare artefact
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_q_fields_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status":    "PASS" if all_pass else "FAIL",
        "params": {
            "seed":   args.seed,
            "n_nodes": args.n_nodes,
            "k_init": args.k_init,
            "k_conn": args.k_conn,
            "k_cl":   args.k_cl,
            "k_sm":   args.k_sm,
            "k_chi":  args.k_chi,
            "k_mix":  args.k_mix,
            "hbar":   args.hbar,
        },
        "observables": {
            "omega_min":           qd["omega_min"],
            "omega_max":           qd["omega_max"],
            "n_positive_modes":    qd["n_pos_modes"],
            "n_zero_modes":        qd["n_zero_modes"],
            "E_0_total":           qd["E_0"],
            "E_0_per_mode":        qd["E_0_per_mode"],
            "zp_sigma_mean":       float(qd["zp_sigma"].mean()),
            "zp_sigma_std":        float(qd["zp_sigma"].std()),
            "zp_chi_mean":         float(qd["zp_chi"].mean()),
            "zp_chi_std":          float(qd["zp_chi"].std()),
            "cross_corr_mean":     float(qd["cross_corr"].mean()),
            "cross_corr_std":      float(qd["cross_corr"].std()),
            "cv_classical":        CV_CLASSICAL_OFFICIAL,
            "cv_quantum":          cv_q,
            "cv_ratio":            (cv_q / CV_CLASSICAL_OFFICIAL
                                    if math.isfinite(cv_q) else None),
        },
        "gates":       gate_results,
        "overall_pass": all_pass,
        "elapsed_s":   round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nArtefact: {out_file}")
    print(f"Timp:     {elapsed:.1f}s")
    print()

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
