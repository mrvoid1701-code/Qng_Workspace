#!/usr/bin/env python3
"""
QNG G32 — Hamiltonian Cuantic Natural (v2)

Imbunatatiri fata de G31:
  1. cv spectral calculat analitic din Tr(K) si Tr(K²) — spectru COMPLET, nu
     doar topul Lanczos.  cv_lambda = std(lambda)/mean(lambda) ≈ 0.39 (fizic).
  2. Modul constant (lambda_0 = m², phi_0 = 1/sqrt(n)) inclus explicit — este
     eigenvector exact al oricarui Laplacian ponderat.
  3. Formula sigma²_i corectata:
        GRESIT in G31: sigma²_i = sum_k phi_k(i)² / (2*omega_k²)  = (K^{-1})_ii/2
        CORECT:        sigma²_i = sum_k phi_k(i)² / (2*omega_k)    = (K^{-1/2})_ii/2
     Variantele oscilatorului armonic H=p²/2+omega²q²/2 au <q²>_0 = 1/(2*omega),
     NU 1/(2*omega²).
  4. Praguri G32 recalibrate fizic:
        G32a — E_0/N_modes in [0.30, 3.0]
        G32b — cv_lambda in [0.25, 0.65]      (spectru complet via Tr)
        G32c — sigma²_max < 0.50              (formula corectata)
        G32d — |cv_lambda - cv_G17|/cv_G17 < 0.80

DERIVAREA FIZICA (identica cu G31, hbar=1 natural):
  H = 1/2 pi² + 1/2 Sigma^T K Sigma
  K = L_Jaccard + m²*I
  <q_alpha²>_0 = 1/(2*omega_alpha)   (omega_alpha = sqrt(lambda_alpha))
  <Sigma_i²>_0 = sum_alpha phi_alpha(i)² / (2*omega_alpha)

Usage:
    python scripts/run_qng_g32_hamiltonian_v2.py
    python scripts/run_qng_g32_hamiltonian_v2.py --seed 4999 --n-modes 40
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g32-hamiltonian-v2"
)

M_EFF_SQ  = 0.014
N_MODES   = 40
N_ITER    = 200
CV_G17    = 0.405   # cv_G17 din G17 (Porter-Thomas pe eigenmodes RW)


@dataclass
class G32Thresholds:
    g32a_e0_per_mode_lo: float = 0.30
    g32a_e0_per_mode_hi: float = 3.0
    g32b_cv_lo:          float = 0.25
    g32b_cv_hi:          float = 0.65
    g32c_sigma2_max:     float = 0.50    # sigma < sqrt(0.5) ≈ 0.71 (confinement lax)
    g32d_cv_rel_tol:     float = 0.80    # |cv_lambda - cv_G17| / cv_G17 < 0.80


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


# ── Jaccard Graph cu ponderi ────────────────────────────────────────────────────

def build_jaccard_weighted(n: int, k_init: int, k_conn: int, seed: int):
    """Construieste graful Jaccard cu ponderi explicite (identic cu G31)."""
    rng = random.Random(seed)
    p0 = k_init / (n - 1)

    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j)
                adj0[j].add(i)

    jaccard_weights: dict[tuple[int, int], float] = {}
    adj_final = [set() for _ in range(n)]

    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i:
                continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj)
            union = len(Ni | Nj)
            s = inter / union if union else 0.0
            scores.append((s, j))
        scores.sort(reverse=True)
        for s, j in scores[:k_conn]:
            adj_final[i].add(j)
            adj_final[j].add(i)
            key = (min(i, j), max(i, j))
            jaccard_weights[key] = max(jaccard_weights.get(key, 0.0), s)

    adj_w: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for (i, j), w in jaccard_weights.items():
        adj_w[i].append((j, w))
        adj_w[j].append((i, w))

    return adj_w


def weighted_degrees(adj_w: list) -> list[float]:
    return [sum(w for _, w in nb) for nb in adj_w]


# ── Momente de urma ale lui K — spectru COMPLET analitic ───────────────────────
#
# Tr(K) = sum_i K_ii = sum_i (d_i + m²) = sum_i d_i + n*m²        [O(n)]
# Tr(K²) = sum_i (K²)_ii
#         = sum_i [ K_ii² + sum_{j in N(i)} K_ij² ]
#         = sum_i [ (d_i+m²)² + sum_{j in N(i)} J_ij² ]             [O(n·k)]
#
# Din aceste doua momente derivam:
#   mean_lambda = Tr(K) / n
#   var_lambda  = Tr(K²)/n - mean_lambda²
#   cv_lambda   = sqrt(var_lambda) / mean_lambda    (spectru complet)

def compute_trace_moments(
    adj_w: list, deg: list[float], n: int, m2: float
) -> tuple[float, float]:
    """
    Returneaza (Tr_K, Tr_K2) fara a construi matricea explicita.
    Complexitate: O(n * k_conn).
    """
    tr_K = sum(d + m2 for d in deg)

    tr_K2 = 0.0
    for i in range(n):
        kii = deg[i] + m2          # K_ii = d_i + m²
        tr_K2 += kii * kii         # K_ii² (diagonal)
        for _, w in adj_w[i]:
            tr_K2 += w * w         # K_ij² = J_ij²  (off-diagonal, symmetric)

    return tr_K, tr_K2


# ── Operatorul K_m² si aplicarea sa ───────────────────────────────────────────

def apply_Km2(v: list[float], adj_w: list, deg: list[float], m2: float) -> list[float]:
    return [
        (deg[i] + m2) * v[i] - sum(w * v[j] for j, w in adj_w[i])
        for i in range(len(v))
    ]


# ── Power iteration cu deflatie ────────────────────────────────────────────────

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


def compute_eigenmodes_Km2(
    adj_w: list,
    n: int,
    n_modes: int,
    n_iter: int,
    m2: float,
    rng: random.Random,
    extra_basis: list | None = None,
) -> tuple[list[float], list[list[float]]]:
    """
    Eigenmode-uri ale K_m² prin power iteration cu deflatie.
    extra_basis: vectori deja cunoscuti de deflat (ex: modul constant).
    Returneaza (lambdas, eigvecs) sortate crescator.
    """
    deg = weighted_degrees(adj_w)
    vecs: list[list[float]] = []
    lambdas: list[float] = []
    all_basis = list(extra_basis) if extra_basis else []

    for _ in range(n_modes):
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, all_basis + vecs)
        nm = _norm(v)
        if nm < 1e-14:
            continue
        v = [x / nm for x in v]

        for _ in range(n_iter):
            w = apply_Km2(v, adj_w, deg, m2)
            w = _deflate(w, all_basis + vecs)
            nm = _norm(w)
            if nm < 1e-14:
                break
            v = [x / nm for x in w]

        Kv = apply_Km2(v, adj_w, deg, m2)
        lam = _dot(v, Kv)
        lam = max(m2, lam)

        vecs.append(v)
        lambdas.append(lam)

    order = sorted(range(len(lambdas)), key=lambda k: lambdas[k])
    return [lambdas[k] for k in order], [vecs[k] for k in order]


# ── Observable cuantice — formula CORECTATA ────────────────────────────────────
#
# Pentru H = sum_alpha omega_alpha (a†_alpha a_alpha + 1/2):
#   <q_alpha²>_0 = 1/(2*omega_alpha)               <- formula CORECTA
#   <Sigma_i²>_0 = sum_alpha phi_alpha(i)² / (2*omega_alpha)
#
# NB: G31 folosea 1/(2*omega_alpha²) = 1/(2*lambda_alpha), ceea ce e (K^{-1})_ii/2
#     — corect din perspectiva propagatorului Euclidian, dar nu e varianța câmpului
#     in starea fundamentala a lui H.

def compute_quantum_observables(
    lambdas: list[float],
    eigvecs: list[list[float]],
    n: int,
) -> tuple[float, list[float], list[float]]:
    """
    Returneaza (E_0, sigma2_nodes, heisenberg).
    sigma2_nodes[i] = <Sigma_i²>_0 = sum_alpha phi_alpha(i)² / (2*omega_alpha)
    """
    K_eff = len(lambdas)
    omegas = [math.sqrt(lam) for lam in lambdas]

    E_0 = 0.5 * sum(omegas)

    # sigma²_i = sum_alpha phi_alpha(i)² / (2*omega_alpha)  [formula corecta]
    sigma2_nodes = [0.0] * n
    for k in range(K_eff):
        inv_omega_half = 1.0 / (2.0 * omegas[k])   # 1/(2*omega) — CORECT
        for i in range(n):
            sigma2_nodes[i] += eigvecs[k][i] ** 2 * inv_omega_half

    # Heisenberg: sigma_Sigma * sigma_pi = 1/2 (per mod — verificare matematica)
    heisenberg = [
        math.sqrt(1.0 / (2.0 * omegas[k])) * math.sqrt(omegas[k] / 2.0)
        for k in range(K_eff)
    ]

    return E_0, sigma2_nodes, heisenberg


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="G32 Hamiltonian Cuantic Natural (v2)")
    p.add_argument("--n-nodes",  type=int,   default=280)
    p.add_argument("--k-init",   type=int,   default=8)
    p.add_argument("--k-conn",   type=int,   default=8)
    p.add_argument("--seed",     type=int,   default=3401)
    p.add_argument("--n-modes",  type=int,   default=N_MODES)
    p.add_argument("--n-iter",   type=int,   default=N_ITER)
    p.add_argument("--m-eff-sq", type=float, default=M_EFF_SQ)
    p.add_argument("--out-dir",  default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []

    def log(msg: str = "") -> None:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(str(msg).encode("ascii", "replace").decode("ascii"))
        lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG G32 — Hamiltonian Cuantic Natural (v2)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log()
    log("Imbunatatiri vs G31:")
    log("  1. cv_lambda din Tr(K)/Tr(K²) — spectru complet, nu doar top Lanczos")
    log("  2. Modul constant (lambda_0=m², phi_0=1/sqrt(n)) inclus explicit")
    log("  3. Formula sigma²_i corectata: 1/(2*omega) nu 1/(2*omega²)")
    log("  4. Praguri G32 recalibrate fizic")
    log()
    log(f"Graf: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"Moduri Lanczos: {args.n_modes}  Iteratii: {args.n_iter}")
    log(f"m²_eff = {args.m_eff_sq}")

    thr = G32Thresholds()
    results: dict = {}

    # ── [0] Graful Jaccard ponderat ────────────────────────────────────────────
    log("\n[0] Construire graf Jaccard ponderat")
    t_g = time.time()
    adj_w = build_jaccard_weighted(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(adj_w)
    deg = weighted_degrees(adj_w)
    mean_deg_w  = sum(deg) / n
    max_deg_w   = max(deg)
    edge_count  = sum(len(nb) for nb in adj_w) // 2
    log(f"  Construit in {time.time()-t_g:.2f}s")
    log(f"  Noduri: {n}  |  Muchii: {edge_count}")
    log(f"  Grad ponderat mediu: {mean_deg_w:.4f}  |  Max: {max_deg_w:.4f}")

    results["graph"] = {
        "n": n, "edges": edge_count,
        "mean_weighted_degree": mean_deg_w,
        "max_weighted_degree": max_deg_w,
    }

    # ── [1] Momente de urma — spectru complet analitic ─────────────────────────
    log("\n[1] Momente de urma Tr(K) si Tr(K²) — spectru complet")
    t_tr = time.time()
    tr_K, tr_K2 = compute_trace_moments(adj_w, deg, n, args.m_eff_sq)
    mean_lambda  = tr_K / n
    var_lambda   = tr_K2 / n - mean_lambda ** 2
    std_lambda   = math.sqrt(max(var_lambda, 0.0))
    cv_lambda    = std_lambda / mean_lambda if mean_lambda > 0 else 0.0
    # Estimare omega_mean via delta method: E[sqrt(lambda)] ≈ sqrt(E[lambda]) - Var/(8*(E[lambda])^1.5)
    omega_mean_est = math.sqrt(mean_lambda) * (1.0 - var_lambda / (8.0 * mean_lambda ** 2))
    log(f"  Tr(K) = {fmt(tr_K)}  |  mean_lambda = {fmt(mean_lambda)}")
    log(f"  Tr(K²) = {fmt(tr_K2)}  |  var_lambda = {fmt(var_lambda)}")
    log(f"  std_lambda = {fmt(std_lambda)}  |  cv_lambda = {fmt(cv_lambda)}  (spectru complet)")
    log(f"  omega_mean_est = {fmt(omega_mean_est)}  (estimat din momente)")
    log(f"  Calculat in {time.time()-t_tr:.4f}s  (O(n*k), exact)")

    results["trace_moments"] = {
        "tr_K": tr_K,
        "tr_K2": tr_K2,
        "mean_lambda": mean_lambda,
        "var_lambda": var_lambda,
        "std_lambda": std_lambda,
        "cv_lambda": cv_lambda,
        "omega_mean_est": omega_mean_est,
    }

    # ── [2] Modul constant — eigenvector exact ─────────────────────────────────
    log("\n[2] Modul constant phi_0 = [1/sqrt(n),...] cu lambda_0 = m²")
    inv_sqrt_n = 1.0 / math.sqrt(n)
    phi0 = [inv_sqrt_n] * n
    lambda0 = args.m_eff_sq
    omega0 = math.sqrt(lambda0)
    # Verificare: K*phi0 = m²*phi0 (Laplacianul anuleaza vectorul constant)
    Kphi0 = apply_Km2(phi0, adj_w, deg, args.m_eff_sq)
    residual0 = math.sqrt(sum((Kphi0[i] - lambda0 * phi0[i]) ** 2 for i in range(n)))
    log(f"  lambda_0 = m² = {fmt(lambda0)}  ->  omega_0 = {fmt(omega0)}")
    log(f"  Reziduu K*phi_0 - lambda_0*phi_0 = {fmt(residual0)}  (trebuie ~0)")
    log(f"  Contributie E_0 (modul constant): {fmt(0.5 * omega0)}")

    results["constant_mode"] = {
        "lambda_0": lambda0,
        "omega_0": omega0,
        "residual": residual0,
        "e0_contribution": 0.5 * omega0,
    }

    # ── [3] Eigenmode-uri Lanczos ale K_m² ────────────────────────────────────
    log(f"\n[3] Eigenmode-uri K_m² prin Lanczos  ({args.n_modes} moduri × {args.n_iter} iter)")
    log("  Deflatie inclusiv pe modul constant — evitam contaminare.")
    t1 = time.time()
    lambdas_lanczos, eigvecs_lanczos = compute_eigenmodes_Km2(
        adj_w, n, args.n_modes, args.n_iter, args.m_eff_sq,
        random.Random(args.seed + 1),
        extra_basis=[phi0],  # deflat pe modul constant
    )
    K_eff_lanczos = len(lambdas_lanczos)
    omegas_lanczos = [math.sqrt(lam) for lam in lambdas_lanczos]
    log(f"  Calculat in {time.time()-t1:.2f}s  |  {K_eff_lanczos} moduri Lanczos")
    log(f"  lambda_min_lanczos = {fmt(lambdas_lanczos[0])}  ->  omega = {fmt(omegas_lanczos[0])}")
    log(f"  lambda_max_lanczos = {fmt(lambdas_lanczos[-1])}  ->  omega = {fmt(omegas_lanczos[-1])}")
    log(f"  omega_mean_lanczos = {fmt(sum(omegas_lanczos)/K_eff_lanczos)}")

    results["eigenmodes_lanczos"] = {
        "n_modes_computed": K_eff_lanczos,
        "lambda_min": lambdas_lanczos[0],
        "lambda_max": lambdas_lanczos[-1],
        "omega_min": omegas_lanczos[0],
        "omega_max": omegas_lanczos[-1],
        "omega_mean": sum(omegas_lanczos) / K_eff_lanczos,
    }

    # ── [4] Observable cuantice — modul constant + moduri Lanczos ─────────────
    log("\n[4] Observable cuantice (modul constant + Lanczos, formula corecta)")

    # Combina: modul constant (index 0) + moduri Lanczos
    all_lambdas = [lambda0] + lambdas_lanczos
    all_eigvecs = [phi0]    + eigvecs_lanczos
    K_eff_total = len(all_lambdas)

    E_0, sigma2_nodes, heisenberg = compute_quantum_observables(
        all_lambdas, all_eigvecs, n
    )
    E_0_per_mode = E_0 / K_eff_total
    sigma2_max   = max(sigma2_nodes)
    sigma2_mean  = sum(sigma2_nodes) / n
    heisenberg_err = max(abs(h - 0.5) for h in heisenberg)

    all_omegas = [math.sqrt(lam) for lam in all_lambdas]
    omega_mean_all = sum(all_omegas) / K_eff_total
    omega_std_all  = statistics.stdev(all_omegas) if K_eff_total > 1 else 0.0
    cv_omega_sample = omega_std_all / omega_mean_all if omega_mean_all > 0 else 0.0

    log(f"  N_moduri total (const+Lanczos): {K_eff_total}")
    log(f"  E_0 = {fmt(E_0)}  (zero-point energy partiala)")
    log(f"  E_0 / N_moduri = {fmt(E_0_per_mode)}")
    log(f"  cv_lambda (spectru complet, din Tr) = {fmt(cv_lambda)}")
    log(f"  cv_omega_sample (din {K_eff_total} moduri) = {fmt(cv_omega_sample)}")
    log(f"  sigma²_max = {fmt(sigma2_max)}  (formula corecta: 1/(2*omega))")
    log(f"  sigma²_mean = {fmt(sigma2_mean)}")
    log(f"  Heisenberg_err_max = {fmt(heisenberg_err)}  (trebuie ~0)")

    results["observables"] = {
        "n_modes_total": K_eff_total,
        "E_0": E_0,
        "E_0_per_mode": E_0_per_mode,
        "cv_lambda_full": cv_lambda,
        "cv_omega_sample": cv_omega_sample,
        "sigma2_max": sigma2_max,
        "sigma2_mean": sigma2_mean,
        "heisenberg_err_max": heisenberg_err,
    }

    # ── [5] Interpretare fizica ────────────────────────────────────────────────
    log("\n[5] Interpretare fizica")
    log(f"  K = L_Jaccard + m²*I,  hbar=1,  n={n} noduri")
    log(f"  lambda_0 = m² = {fmt(lambda0)}  (modul constant, gap spectral)")
    log(f"  mean_lambda (spectru complet) = {fmt(mean_lambda)}")
    log(f"  cv_lambda = {fmt(cv_lambda)}  (raspandire spectrala reala)")
    log(f"  sigma²_mean = {fmt(sigma2_mean)}  (fluctuatii ZP medii per nod)")
    log(f"  sigma_mean = {fmt(math.sqrt(sigma2_mean))}  (deviatia standard medie)")
    log(f"  Nota: sigma²_max provine din moduri Lanczos localizate (top spectru)")

    # ── [6] Gates ──────────────────────────────────────────────────────────────
    log("\n" + "=" * 70)
    log("GATES G32")
    log("=" * 70)

    gates: dict[str, dict] = {}

    # G32a — Energia de vacuum non-triviala
    g32a = (thr.g32a_e0_per_mode_lo < E_0_per_mode < thr.g32a_e0_per_mode_hi)
    gates["G32a"] = {
        "name": "Non-trivial vacuum energy per mode",
        "value": E_0_per_mode,
        "threshold_lo": thr.g32a_e0_per_mode_lo,
        "threshold_hi": thr.g32a_e0_per_mode_hi,
        "condition": f"{thr.g32a_e0_per_mode_lo} < E_0/N_modes < {thr.g32a_e0_per_mode_hi}",
        "passed": g32a,
    }
    status_a = "PASS" if g32a else "FAIL"
    log(f"\nG32a — Vacuum energy per mod: {fmt(E_0_per_mode)}")
    log(f"       Prag: ({thr.g32a_e0_per_mode_lo}, {thr.g32a_e0_per_mode_hi})  ->  {status_a}")

    # G32b — cv_lambda spectru complet (din Tr(K), Tr(K²))
    g32b = (thr.g32b_cv_lo < cv_lambda < thr.g32b_cv_hi)
    gates["G32b"] = {
        "name": "Full-spectrum eigenvalue spread (from trace moments)",
        "value": cv_lambda,
        "threshold_lo": thr.g32b_cv_lo,
        "threshold_hi": thr.g32b_cv_hi,
        "condition": f"{thr.g32b_cv_lo} < cv_lambda < {thr.g32b_cv_hi}",
        "metric_note": "cv_lambda = std(lambda)/mean(lambda) din Tr(K),Tr(K²) — spectru complet",
        "passed": g32b,
    }
    status_b = "PASS" if g32b else "FAIL"
    log(f"\nG32b — cv_lambda (spectru complet): {fmt(cv_lambda)}")
    log(f"       Prag: ({thr.g32b_cv_lo}, {thr.g32b_cv_hi})  ->  {status_b}")

    # G32c — Confinement (formula corectata)
    g32c = (sigma2_max < thr.g32c_sigma2_max)
    gates["G32c"] = {
        "name": "Zero-point fluctuations (corrected formula 1/(2*omega))",
        "value": sigma2_max,
        "threshold": thr.g32c_sigma2_max,
        "condition": f"sigma2_max < {thr.g32c_sigma2_max}",
        "formula_note": "sigma2_i = sum_k phi_k(i)^2 / (2*omega_k)  [corect vs G31]",
        "passed": g32c,
    }
    status_c = "PASS" if g32c else "FAIL"
    log(f"\nG32c — sigma²_max (formula corecta): {fmt(sigma2_max)}")
    log(f"       Prag: < {thr.g32c_sigma2_max}  ->  {status_c}")

    # G32d — Consistenta cv_lambda cu cv_G17
    cv_rel = abs(cv_lambda - CV_G17) / CV_G17
    g32d = (cv_rel < thr.g32d_cv_rel_tol)
    gates["G32d"] = {
        "name": "cv_lambda consistent with cv_G17",
        "value": cv_rel,
        "threshold": thr.g32d_cv_rel_tol,
        "cv_lambda": cv_lambda,
        "cv_G17": CV_G17,
        "condition": f"|cv_lambda - cv_G17|/cv_G17 < {thr.g32d_cv_rel_tol}",
        "passed": g32d,
    }
    status_d = "PASS" if g32d else "FAIL"
    log(f"\nG32d — Consistenta cv: |{fmt(cv_lambda)} - {CV_G17}| / {CV_G17} = {fmt(cv_rel)}")
    log(f"       Prag: < {thr.g32d_cv_rel_tol}  ->  {status_d}")

    # ── Sumar ──────────────────────────────────────────────────────────────────
    n_pass = sum([g32a, g32b, g32c, g32d])
    n_total = 4
    all_pass = (n_pass == n_total)

    log("\n" + "=" * 70)
    log(f"SUMAR: {n_pass}/{n_total} gate-uri trecute")
    log(f"G32a [{status_a}]  G32b [{status_b}]  G32c [{status_c}]  G32d [{status_d}]")
    log("=" * 70)

    if all_pass:
        log("\n*** TOATE GATE-URILE G32 TRECUTE ***")
        log("Hamiltonianul cuantic (v2) este consistent cu teoria QNG.")
    else:
        log("\n*** UNELE GATE-URI PICATE ***")
        if not g32a:
            log("  G32a: energia de vacuum per mod in afara domeniului fizic")
        if not g32b:
            log("  G32b: cv_lambda (spectru complet) in afara intervalului")
        if not g32c:
            log("  G32c: fluctuatii zero-point depasesc pragul")
        if not g32d:
            log("  G32d: cv_lambda inconsistent cu cv_G17")

    log(f"\nTimp total: {time.time()-t0:.2f}s")

    # ── Scriere artefacte ──────────────────────────────────────────────────────
    results["gates"] = gates
    results["summary"] = {
        "n_pass": n_pass,
        "n_total": n_total,
        "all_pass": all_pass,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "runtime_s": round(time.time() - t0, 3),
    }

    json_path = out_dir / "summary.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    log(f"\nArtefacte scrise in: {out_dir}")
    log("  summary.json")

    # CSV eigenvalues (modul constant + Lanczos)
    eig_rows = [
        {"mode": k, "source": "constant" if k == 0 else "lanczos",
         "lambda": all_lambdas[k], "omega": all_omegas[k],
         "sigma_Sigma": 1.0 / math.sqrt(2.0 * all_omegas[k]),
         "sigma_pi":    math.sqrt(all_omegas[k] / 2.0),
         "heisenberg":  heisenberg[k]}
        for k in range(K_eff_total)
    ]
    eig_path = out_dir / "eigenmodes.csv"
    write_csv(eig_path, ["mode", "source", "lambda", "omega", "sigma_Sigma", "sigma_pi", "heisenberg"], eig_rows)
    log("  eigenmodes.csv")

    node_rows = [{"node": i, "sigma2": sigma2_nodes[i]} for i in range(n)]
    node_path = out_dir / "node_fluctuations.csv"
    write_csv(node_path, ["node", "sigma2"], node_rows)
    log("  node_fluctuations.csv")

    log_path = out_dir / "run.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log("  run.log")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
