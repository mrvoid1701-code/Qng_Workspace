#!/usr/bin/env python3
"""
QNG Q-Fields — Ancorarea ħ_field (v1)

Determină ħ_field (constanta Planck a câmpurilor Σ, χ) din proprietățile
spectrale ale grafului Jaccard, prin patru condiții de ancorare distincte.

Observație cheie (derivată analitic):
  cv_quantum = σ(⟨(δΣ)²⟩) / μ(⟨(δΣ)²⟩) este INVARIANT față de ħ_field,
  deoarece atât σ cât și μ scalează liniar cu ħ_field.
  → Corecția Pioneer (δ cv_total) nu depinde de alegerea ħ_field.

Cele patru condiții de ancorare:

  A) Echipariție energetică (condiție fizică):
     ħ_field/2 · mean(ω_a) = ħ_graf/2 · mean(Ω_k)
     → ħ_field = mean(Ω_k) / mean(ω_a)
     unde Ω_k = √(λ_k(L) + M_EFF_SQ)  (G17, M_EFF_SQ=0.014)

  B) Gap spectral egal (G17 ↔ Q-fields):
     ħ_field · ω_min_K = ħ_graf · Ω_min_G17
     → ħ_field = Ω_min_G17 / ω_min_K

  C) Perturbativitate (⟨(δΣ)²⟩ ≪ Σ_range²):
     ħ_field · ⟨(δΣ)²⟩|_{ħ=1} = ε_pert  (ε_pert = 0.01)
     → ħ_field = ε_pert / ⟨(δΣ)²⟩|_{ħ=1}

  D) Scală unică (ħ_field = ħ_graf = 1):
     → ħ_field = 1.0  (ipoteza cea mai simplă)

Fișier nou, nu modifică nimic existent.
Derivare: 03_math/derivations/qng-quantum-sigma-chi-v1.md
Precedent: run_qng_q_fields_v1.py, run_qng_g17_v2.py
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-qf-hbar-anchor-v1"
)

N_NODES   = 280
K_INIT    = 8
K_CONN    = 8
K_CL      = 0.5
K_SM      = 0.2
K_CHI     = 0.3
K_MIX     = 0.1
HBAR_GRAF = 1.0       # ħ_graf = 1 (unități naturale G17)
M_EFF_SQ  = 0.014     # din G17 (masa efectivă a câmpului de pe graf)
EPS_PERT  = 0.01      # prag perturbativitate: ⟨(δΣ)²⟩ < 1% din [0,1]²
CV_CLASS  = 0.405     # cv clasic oficial (din G17/G20)


# ── Graf Jaccard ────────────────────────────────────────────────────────────

def _jacc(a: set, b: set) -> float:
    i = len(a & b); u = len(a | b)
    return i / u if u else 0.0

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    nb: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        pool = list(range(n)); pool.remove(i)
        for j in rng.sample(pool, min(k_init, len(pool))):
            nb[i].add(j); nb[j].add(i)
    adj: dict[int, set] = {i: set() for i in range(n)}
    for i in range(n):
        ni = nb[i] | {i}
        cands: set = set()
        for j in nb[i]: cands |= nb[j]
        cands.discard(i)
        sc = [(_jacc(ni, nb[j] | {j}), j) for j in cands]
        sc.sort(reverse=True)
        for _, j in sc[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return adj

def graph_laplacian(adj, n):
    L = np.zeros((n, n))
    for i in range(n):
        L[i, i] = float(len(adj[i]))
        for j in adj[i]: L[i, j] = -1.0
    return L


# ── Spectru G17 ─────────────────────────────────────────────────────────────

def g17_frequencies(L_eigvals, m_eff_sq):
    """Ω_k = √(λ_k(L) + m²) — frecvențele oscilatorilor G17."""
    return np.sqrt(np.maximum(L_eigvals + m_eff_sq, 0.0))


# ── Hamiltonianul cuantic K (copiat din run_qng_q_fields_v1.py) ─────────────

def build_K(L, n, k_cl, k_sm, k_chi, k_mix):
    M_sigma = k_cl * np.eye(n) + k_sm * L
    M_chi   = k_chi * np.eye(n)
    M_cross = k_mix * np.eye(n)
    return np.block([[M_sigma, M_cross], [M_cross, M_chi]])

def quantize(K, n):
    """Returnează eigenvalues, ω, și fluctuații la ħ=1."""
    eigvals, eigvecs = np.linalg.eigh(K)
    omega = np.where(eigvals > 0, np.sqrt(np.maximum(eigvals, 0.0)), 0.0)
    pos = omega > 1e-10
    safe_omega = np.where(pos, omega, np.inf)
    weights = 1.0 / (2.0 * safe_omega)      # ħ=1 → ħ/(2ω) = 1/(2ω)
    U_sigma = eigvecs[:n, :]
    U_chi   = eigvecs[n:, :]
    zp_sigma = np.einsum("ia,a,ia->i", U_sigma, weights, U_sigma)
    return {
        "eigvals":      eigvals,
        "omega":        omega,
        "omega_min":    float(omega[pos].min()) if pos.any() else 0.0,
        "omega_max":    float(omega.max()),
        "E0_per_mode":  float(omega.sum() / (2 * n)),  # ħ=1
        "mean_omega":   float(omega[pos].mean()) if pos.any() else 0.0,
        "zp_sigma":     zp_sigma,                       # shape (N,), ħ=1
        "zp_mean_h1":   float(zp_sigma.mean()),
        "zp_std_h1":    float(zp_sigma.std()),
        "cv_quantum":   float(zp_sigma.std() / zp_sigma.mean())
                        if zp_sigma.mean() > 1e-12 else float("nan"),
    }


# ── Condiții de ancorare ────────────────────────────────────────────────────

def anchor_conditions(qd, G17_freqs, eps_pert):
    mean_Omega = float(G17_freqs.mean())
    Omega_min  = float(G17_freqs.min())
    mean_omega = qd["mean_omega"]
    omega_min  = qd["omega_min"]
    zp_h1      = qd["zp_mean_h1"]

    conditions = {
        "A_equipartition": {
            "label":   "Echipariție energetică",
            "formula": "ħ_f = mean(Ω_G17) / mean(ω_K)",
            "hbar_field": mean_Omega / mean_omega if mean_omega > 0 else float("nan"),
            "note":    f"mean(Ω_G17)={mean_Omega:.4f}, mean(ω_K)={mean_omega:.4f}",
        },
        "B_gap_match": {
            "label":   "Gap spectral egal (G17 ↔ K)",
            "formula": "ħ_f = Ω_min_G17 / ω_min_K",
            "hbar_field": Omega_min / omega_min if omega_min > 0 else float("nan"),
            "note":    f"Ω_min_G17={Omega_min:.4f}, ω_min_K={omega_min:.4f}",
        },
        "C_perturbativity": {
            "label":   "Perturbativitate",
            "formula": f"ħ_f = ε_pert / ⟨δΣ²⟩|_{{ħ=1}}, ε={eps_pert}",
            "hbar_field": eps_pert / zp_h1 if zp_h1 > 0 else float("nan"),
            "note":    f"⟨δΣ²⟩|{{ħ=1}}={zp_h1:.6f}",
        },
        "D_single_scale": {
            "label":   "Scală unică",
            "formula": "ħ_f = ħ_graf = 1",
            "hbar_field": 1.0,
            "note":    "ipoteza cea mai simplă; ħ_field = ħ_graf",
        },
    }
    return conditions


def evaluate_condition(cond, qd, cv_class):
    hf = cond["hbar_field"]
    if not math.isfinite(hf) or hf <= 0:
        return {**cond, "valid": False}

    zp_phys   = hf * qd["zp_mean_h1"]          # ⟨(δΣ)²⟩ fizic
    zp_std_ph = hf * qd["zp_std_h1"]
    cv_q      = qd["cv_quantum"]                 # invariant față de ħ_field
    cv_tot    = math.sqrt(cv_class**2 + cv_q**2)
    delta_cv  = cv_tot - cv_class
    delta_pct = 100.0 * delta_cv / cv_class

    # Validitate: fluctuațiile trebuie < 50% din domeniul Σ=[0,1]
    valid_pert = zp_phys < 0.25   # ⟨(δΣ)²⟩ < (0.5)²
    # Energie per mod: sanity check că nu e enormă
    E0_phys    = hf * qd["E0_per_mode"]

    return {
        **cond,
        "hbar_field":    hf,
        "zp_sigma_phys": zp_phys,
        "zp_std_phys":   zp_std_ph,
        "cv_quantum":    cv_q,          # invariant
        "cv_total":      cv_tot,
        "delta_cv":      delta_cv,
        "delta_cv_pct":  delta_pct,
        "E0_per_mode_phys": E0_phys,
        "valid_perturbativity": valid_pert,
        "valid": True,
    }


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="QNG Q-Fields: ancorarea ħ_field"
    )
    ap.add_argument("--seed",     type=int,   default=3401)
    ap.add_argument("--n",        type=int,   default=N_NODES, dest="n_nodes")
    ap.add_argument("--k-init",   type=int,   default=K_INIT)
    ap.add_argument("--k-conn",   type=int,   default=K_CONN)
    ap.add_argument("--k-cl",     type=float, default=K_CL)
    ap.add_argument("--k-sm",     type=float, default=K_SM)
    ap.add_argument("--k-chi",    type=float, default=K_CHI)
    ap.add_argument("--k-mix",    type=float, default=K_MIX)
    ap.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    ap.add_argument("--eps-pert", type=float, default=EPS_PERT)
    ap.add_argument("--out-dir",  type=Path,  default=DEFAULT_OUT_DIR)
    args = ap.parse_args()

    if not HAS_NUMPY:
        print("EROARE: numpy necesar.", file=sys.stderr); sys.exit(2)

    t0 = time.time()
    print("=" * 66)
    print("QNG Q-Fields — Ancorarea ħ_field")
    print("=" * 66)
    print(f"  seed={args.seed}  N={args.n_nodes}  "
          f"k_cl={args.k_cl}  k_chi={args.k_chi}  k_mix={args.k_mix}")
    print(f"  M_EFF_SQ={args.m_eff_sq} (G17)  ε_pert={args.eps_pert}")
    print()

    # 1. Graf + Laplacian
    print("[1/4] Graf Jaccard...")
    adj = build_jaccard_graph(args.n_nodes, args.k_init, args.k_conn, args.seed)
    L   = graph_laplacian(adj, args.n_nodes)
    L_eigs = np.linalg.eigvalsh(L)
    print(f"      λ_min(L)={L_eigs[0]:.6f}  λ₁(Fiedler)={L_eigs[1]:.6f}  "
          f"λ_max={L_eigs[-1]:.4f}")
    print(f"      mean(λ_L) = {L_eigs.mean():.4f}")

    # 2. Frecvențe G17 (toate N moduri, nu doar primele 20)
    print("[2/4] Frecvențe G17  Ω_k = √(λ_k + M_EFF_SQ)...")
    G17_freqs = g17_frequencies(L_eigs, args.m_eff_sq)
    print(f"      Ω_min={G17_freqs.min():.6f}  Ω_max={G17_freqs.max():.4f}  "
          f"mean(Ω)={G17_freqs.mean():.4f}")
    E0_graf_per_mode = float(G17_freqs.sum() / (2 * args.n_nodes))
    print(f"      E₀_graf/mod (ħ=1) = {E0_graf_per_mode:.6f}")

    # 3. Q-fields quantization
    print("[3/4] Cuantificare Q-fields K (2N×2N)...")
    K  = build_K(L, args.n_nodes, args.k_cl, args.k_sm, args.k_chi, args.k_mix)
    qd = quantize(K, args.n_nodes)
    print(f"      ω_min={qd['omega_min']:.6f}  ω_max={qd['omega_max']:.4f}  "
          f"mean(ω)={qd['mean_omega']:.4f}")
    print(f"      E₀_field/mod (ħ=1) = {qd['E0_per_mode']:.6f}")
    print(f"      ⟨(δΣ)²⟩ (ħ=1) = {qd['zp_mean_h1']:.6f}  "
          f"cv_quantum = {qd['cv_quantum']:.6f}")

    # 4. Condiții de ancorare
    print("[4/4] Evaluez cele 4 condiții de ancorare...")

    conds = anchor_conditions(qd, G17_freqs, args.eps_pert)
    results = {}
    for key, cond in conds.items():
        results[key] = evaluate_condition(cond, qd, CV_CLASS)

    elapsed = time.time() - t0

    # ── Afișare tabel ──────────────────────────────────────────────────────
    print()
    print("=" * 66)
    print("REZULTATE ANCORARE ħ_field")
    print("=" * 66)
    print(f"\n  {'Condiție':<28}  {'ħ_field':>9}  {'⟨δΣ²⟩_fiz':>11}  "
          f"{'cv_tot':>8}  {'δcv%':>7}  {'Valid?':>7}")
    print(f"  {'-'*28}  {'-'*9}  {'-'*11}  {'-'*8}  {'-'*7}  {'-'*7}")

    for key, r in results.items():
        if not r["valid"]:
            print(f"  {r['label']:<28}  {'N/A':>9}")
            continue
        valid_str = "DA ✓" if r["valid_perturbativity"] else "NU ✗"
        print(f"  {r['label']:<28}  {r['hbar_field']:9.5f}  "
              f"{r['zp_sigma_phys']:11.6f}  "
              f"{r['cv_total']:8.5f}  "
              f"{r['delta_cv_pct']:7.3f}%  "
              f"{valid_str:>7}")

    # ── Observație cheie ────────────────────────────────────────────────────
    print()
    print("─" * 66)
    print("OBSERVAȚIE CHEIE: cv_quantum este INVARIANT față de ħ_field")
    print("─" * 66)
    print(f"  cv_quantum = {qd['cv_quantum']:.6f}  (pentru ORICE ħ_field)")
    print(f"  cv_classic = {CV_CLASS:.4f}")

    # cv_total pentru orice ħ_field
    cv_tot_fixed = math.sqrt(CV_CLASS**2 + qd["cv_quantum"]**2)
    delta_fixed  = cv_tot_fixed - CV_CLASS
    delta_pct_f  = 100.0 * delta_fixed / CV_CLASS
    print(f"  cv_total   = {cv_tot_fixed:.6f}  (corecție fixă: +{delta_pct_f:.2f}%)")
    print()
    print(f"  → Predicția Pioneer NU depinde de ħ_field.")
    print(f"  → cv_total = {cv_tot_fixed:.4f} față de cv_classic = {CV_CLASS:.4f}")
    print(f"  → Corecție absolutizată: Δcv = {delta_fixed:.5f}  (+{delta_pct_f:.2f}%)")

    # ── Condiția A (cea mai fizică): validitate confinement ─────────────────
    print()
    print("─" * 66)
    print("CONDIȚIA A (Echipariție) — analiză detaliată")
    print("─" * 66)
    rA = results["A_equipartition"]
    print(f"  ħ_field = {rA['hbar_field']:.5f}")
    print(f"  ⟨(δΣ)²⟩_fizic = {rA['zp_sigma_phys']:.6f}  "
          f"(σ_Σ = {math.sqrt(rA['zp_sigma_phys']):.4f})")
    print(f"  Domeniu Σ ∈ [0,1] → σ_max = 0.5")
    rel = math.sqrt(rA["zp_sigma_phys"]) / 0.5
    print(f"  σ_Σ / σ_max = {rel:.4f}  "
          f"({'perturbativ ✓' if rel < 0.5 else 'NON-perturbativ! Confinement important'})")
    if rel >= 0.5:
        print()
        print("  ⚠ La echipariție, fluctuațiile Σ sunt de ordinul domeniului [0,1].")
        print("  ⚠ Confinementul Σ ∈ [0,1] devine esențial — potențialul double-well")
        print("  ⚠ sau tratamentul de spin (pasul următor) e necesar.")

    # ── Condiția C (perturbativitate): ħ_field_max ─────────────────────────
    print()
    print("─" * 66)
    print("LIMITA SUPERIOARĂ ħ_field_max din perturbativitate")
    print("─" * 66)
    hbar_max = 0.25 / qd["zp_mean_h1"]   # ⟨δΣ²⟩ < 0.25 = (0.5)²
    print(f"  Condiție: ⟨(δΣ)²⟩_fiz < 0.25  ⟺  ħ_field < {hbar_max:.4f}")
    cA_valid = rA["hbar_field"] < hbar_max
    print(f"  ħ_A = {rA['hbar_field']:.5f}  "
          f"{'< limită ✓' if cA_valid else '> limită! Echipariția necesită confinement'}")
    print(f"  ħ_D = 1.0000 (single scale)  "
          f"{'< limită ✓' if 1.0 < hbar_max else '> limită'}")

    print()
    print(f"Timp: {elapsed:.1f}s")

    # Salvare
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "script":    "run_qng_qf_hbar_anchor_v1.py",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "params": {
            "seed": args.seed, "n_nodes": args.n_nodes,
            "k_cl": args.k_cl, "k_sm": args.k_sm,
            "k_chi": args.k_chi, "k_mix": args.k_mix,
            "m_eff_sq": args.m_eff_sq, "eps_pert": args.eps_pert,
        },
        "graph_spectral": {
            "lambda_fiedler": float(L_eigs[1]),
            "lambda_max":     float(L_eigs[-1]),
            "lambda_mean":    float(L_eigs.mean()),
            "Omega_min_G17":  float(G17_freqs.min()),
            "Omega_max_G17":  float(G17_freqs.max()),
            "Omega_mean_G17": float(G17_freqs.mean()),
            "E0_graf_per_mode": E0_graf_per_mode,
        },
        "qfields": {
            "omega_min": qd["omega_min"],
            "omega_max": qd["omega_max"],
            "mean_omega": qd["mean_omega"],
            "E0_field_per_mode": qd["E0_per_mode"],
            "zp_mean_h1": qd["zp_mean_h1"],
            "cv_quantum": qd["cv_quantum"],
        },
        "invariant_result": {
            "cv_quantum":  qd["cv_quantum"],
            "cv_classic":  CV_CLASS,
            "cv_total":    cv_tot_fixed,
            "delta_cv":    delta_fixed,
            "delta_cv_pct": delta_pct_f,
            "pioneer_correction_independent_of_hbar": True,
        },
        "anchoring_conditions": {
            k: {kk: vv for kk, vv in v.items()
                if isinstance(vv, (int, float, bool, str))}
            for k, v in results.items()
        },
        "hbar_field_max": hbar_max,
        "elapsed_s": round(elapsed, 3),
    }
    out_file = args.out_dir / "summary.json"
    with out_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Artefact: {out_file}")


if __name__ == "__main__":
    main()
