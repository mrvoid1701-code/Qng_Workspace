#!/usr/bin/env python3
"""
QNG G31 — Hamiltonian Cuantic Natural (v1)

Derivare din primul principiu — nimic ad-hoc.

PROBLEMA CU G17/G20
-------------------
G17 si G20 folosesc operatorul random-walk (neponderat):
    (A_rw v)_i = (1/deg_i) * sum_{j in N(i)} v_j

Ponderile Jaccard J_ij sunt calculate in build_jaccard_graph dar ARUNCATE.
Nu exista Lagrangian explicit, nu exista cuantificare canonica — omega_k
sunt "puse" ca sqrt(mu_rw + m²), nu derivate din principiu variational.

DERIVAREA NATURALA
------------------
Pe un graf ponderat G cu ponderi J_ij, singura actiune naturala pentru
campul scalar Sigma_i este energia Dirichlet ponderata:

    S[Sigma] = sum_t [ 1/2 * sum_i Sigma_i_dot²
                     - 1/2 * sum_{(i,j)} J_ij (Sigma_i - Sigma_j)²
                     - 1/2 * m² * sum_i Sigma_i² ]

Transform Legendre -> Hamiltonian:
    H = 1/2 * sum_i pi_i² + 1/2 * Sigma^T K Sigma

unde K = Laplacian Jaccard ponderat + m²*I:
    K_ii = d_i + m²     (grad ponderat + masa)
    K_ij = -J_ij        (cuplaj direct din ponderi Jaccard)
    d_i  = sum_j J_ij   (gradul ponderat al nodului i)

Cuantificare canonica: [Sigma_hat_i, pi_hat_j] = i * delta_ij   (hbar=1)
    - hbar=1 e singurul ales consistent: Sigma in [0,1] si K dimensionless
      => actiunea S e dimensionless => quantum de actiune = 1 (natural)

Starea fundamentala |Psi_0> (exacta pentru H cuadratic — Gaussiana):
    Psi_0[Sigma] ~ exp(-1/2 * sum_alpha omega_alpha * q_alpha²)
    unde q_alpha = coordonate in baza modurilor normale

Observable (toate derivate din K — fara parametri externi):
    E_0          = 1/2 * Tr(sqrt(K)) = 1/2 * sum_alpha omega_alpha
    cv_natural   = std(omega_alpha) / mean(omega_alpha)
    sigma²_i     = 1/2 * sum_alpha |psi_alpha(i)|² / omega_alpha²
                 = (K^-1)_ii / 2  (fluctuatii zero-point per nod)

Singurul parametru mostenit: m² = 0.014 (deja in G17/G20 — nu e nou).

GATES (G31):
    G31a — E_0/N_modes in [0.02, 5.0]  (vacuum energy nontrivial per mod)
    G31b — cv_natural in [0.20, 0.70]  (spectru frecvente fizic rezonabil)
    G31c — max(sigma²_i) < 0.0625      (confinement: sigma < 0.25, Sigma in [0,1])
    G31d — |cv_natural - cv_G17| / cv_G17 < 0.50  (consistenta cu G17)

Obs. prag G31c: vine din domeniu [0,1] cu echilibru la 0.5.
    Fluctuatia maxima admisa: sigma_max = 0.25 => sigma²_max = 0.0625.

Usage:
    python scripts/run_qng_g31_hamiltonian_v1.py
    python scripts/run_qng_g31_hamiltonian_v1.py --seed 4999 --n-modes 50
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
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g31-hamiltonian-v1"
)

# Parametri default — identici cu G17/G20 pentru comparabilitate
M_EFF_SQ  = 0.014   # masa efectiva la patrat (din G17)
N_MODES   = 40      # moduri dominante pentru power iteration
N_ITER    = 200     # iteratii power method per mod
CV_G17    = 0.405   # cv stabilit de G17 (Porter-Thomas pe eigenmodes RW)


@dataclass
class G31Thresholds:
    g31a_e0_per_mode_lo: float = 0.02
    g31a_e0_per_mode_hi: float = 5.0
    g31b_cv_lo:          float = 0.20
    g31b_cv_hi:          float = 0.70
    g31c_sigma2_max:     float = 0.0625   # sigma < 0.25
    g31d_cv_rel_tol:     float = 0.50     # |cv_nat - cv_G17| / cv_G17 < 0.50


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
# Diferenta fata de G17/G20: stocam J_ij explicit in adj_w.
# In G17: adj = list[list[int]] (topologie pura, ponderi aruncate)
# Aici:   adj_w = list[list[(j, J_ij)]] (topologie + ponderi Jaccard)

def build_jaccard_weighted(n: int, k_init: int, k_conn: int, seed: int):
    """
    Construieste graful Jaccard cu ponderi explicite.

    Returneaza adj_w: list[list[(j, w)]] unde w = J(i,j) = Jaccard similarity.

    Aceeasi procedura ca G17/G20 (adj0 Erdos-Renyi, rewire dupa Jaccard top-k)
    dar stocam ponderile J_ij in loc sa le aruncam.
    """
    rng = random.Random(seed)
    p0 = k_init / (n - 1)

    # Pasul 1: graf initial Erdos-Renyi
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j)
                adj0[j].add(i)

    # Pasul 2: rewire dupa Jaccard similarity — stocam scoruri
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
            # J(i,j) e simetric (inter/union nu depinde de directie)
            # pastram max in caz de calcule numerice marginale
            jaccard_weights[key] = max(jaccard_weights.get(key, 0.0), s)

    # Pasul 3: construim adj_w ponderat
    adj_w: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for (i, j), w in jaccard_weights.items():
        adj_w[i].append((j, w))
        adj_w[j].append((i, w))

    return adj_w


def weighted_degrees(adj_w: list) -> list[float]:
    """d_i = sum_j J_ij  (gradul ponderat al nodului i)."""
    return [sum(w for _, w in nb) for nb in adj_w]


# ── Operatorul K_m² = Laplacian ponderat + m²·I ────────────────────────────────
#
# Derivat direct din Hamiltonianul H = 1/2 pi² + 1/2 Sigma^T K Sigma.
# K este Hessian-ul potentialului V[Sigma] = energia Dirichlet + masa.
#
# (K v)_i = (d_i + m²) * v_i - sum_{j in N(i)} J_ij * v_j
#          = sum_{j in N(i)} J_ij * (v_i - v_j)  +  m² * v_i
#
# Toate eigenvalorile >= m² > 0 (K pozitiv definit).

def apply_Km2(v: list[float], adj_w: list, deg: list[float], m2: float) -> list[float]:
    """Aplica K_m² = L_Jaccard + m²*I la vectorul v."""
    return [
        (deg[i] + m2) * v[i] - sum(w * v[j] for j, w in adj_w[i])
        for i in range(len(v))
    ]


# ── Power iteration cu deflatie pentru eigenmodes K_m² ─────────────────────────
# Standard: deflated power method, converge la eigenvalori in ordine descrescatoare.
# Rayleigh quotient lambda_k = v_k^T K v_k (||v_k|| = 1) da eigenvaloarea exacta.

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
) -> tuple[list[float], list[list[float]]]:
    """
    Eigenmode-uri ale K_m² prin power iteration cu deflatie.

    Returneaza (lambdas, eigvecs) sortate crescator dupa eigenvaloare.
    lambda_alpha = omega_alpha² >= m²  (toate pozitive, K pozitiv definit)
    """
    deg = weighted_degrees(adj_w)
    vecs: list[list[float]] = []
    lambdas: list[float] = []

    for _ in range(n_modes):
        # Initializare aleatoare, deflata
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, vecs)
        nm = _norm(v)
        if nm < 1e-14:
            continue
        v = [x / nm for x in v]

        # Iteratii power method
        for _ in range(n_iter):
            w = apply_Km2(v, adj_w, deg, m2)
            w = _deflate(w, vecs)
            nm = _norm(w)
            if nm < 1e-14:
                break
            v = [x / nm for x in w]

        # Eigenvaloarea prin Rayleigh quotient: lambda = v^T K v
        Kv = apply_Km2(v, adj_w, deg, m2)
        lam = _dot(v, Kv)                     # = v^T K v, ||v||=1
        lam = max(m2, lam)                    # K pozitiv definit, lambda >= m²

        vecs.append(v)
        lambdas.append(lam)

    # Sortare crescatoare dupa eigenvaloare
    order = sorted(range(len(lambdas)), key=lambda k: lambdas[k])
    return [lambdas[k] for k in order], [vecs[k] for k in order]


# ── Observable cuantice din starea fundamentala |Psi_0> ────────────────────────
#
# Pentru H = sum_alpha omega_alpha (a†_alpha a_alpha + 1/2):
#   - E_0          = 1/2 * sum_alpha omega_alpha
#   - sigma²_Sigma_alpha = 1/(2*omega_alpha)   (per mod normal)
#   - sigma²_pi_alpha    = omega_alpha/2
#   - sigma_Sigma_alpha * sigma_pi_alpha = 1/2  (Heisenberg exact pentru |0>)
#
# La nivel de nod:
#   - sigma²_i = 1/2 * sum_alpha |psi_alpha(i)|² / omega_alpha²  (approx K^{-1}_ii / 2)

def compute_quantum_observables(
    lambdas: list[float],
    eigvecs: list[list[float]],
    n: int,
) -> tuple[float, float, list[float], list[float]]:
    """
    Calculeaza observable cuantice din starea fundamentala.

    Returneaza:
        E_0         : energia de vacuum (zero-point energy)
        cv_natural  : std(omega) / mean(omega)
        sigma2_nodes: fluctuatii zero-point per nod
        heisenberg  : sigma_Sigma_alpha * sigma_pi_alpha per mod (trebuie = 0.5)
    """
    K_eff = len(lambdas)
    omegas = [math.sqrt(lam) for lam in lambdas]

    E_0 = 0.5 * sum(omegas)

    omega_mean = sum(omegas) / K_eff
    omega_std  = statistics.stdev(omegas) if K_eff > 1 else 0.0
    cv_natural = omega_std / omega_mean if omega_mean > 0 else 0.0

    # Fluctuatii zero-point per nod: sigma²_i = 1/2 * sum_alpha |psi_alpha(i)|² / omega_alpha²
    sigma2_nodes = [0.0] * n
    for k in range(K_eff):
        inv_omega2 = 1.0 / (2.0 * omegas[k] ** 2)
        for i in range(n):
            sigma2_nodes[i] += eigvecs[k][i] ** 2 * inv_omega2

    # Heisenberg per mod: sigma_Sigma_alpha * sigma_pi_alpha
    # sigma_Sigma = 1/sqrt(2*omega), sigma_pi = sqrt(omega/2)
    # produs = 1/2 intotdeauna (verificare matematica, nu gate)
    heisenberg = [
        math.sqrt(1.0 / (2.0 * omegas[k])) * math.sqrt(omegas[k] / 2.0)
        for k in range(K_eff)
    ]

    return E_0, cv_natural, sigma2_nodes, heisenberg


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="G31 Hamiltonian Cuantic Natural (v1)")
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
    log("QNG G31 — Hamiltonian Cuantic Natural (v1)")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log()
    log("Derivare din principii prime — nimic ad-hoc:")
    log("  Actiune -> Lagrangian -> Hamiltonian -> cuantificare canonica")
    log("  K = Laplacian Jaccard ponderat + m²*I  (hbar=1 in unitati naturale)")
    log(f"  m²_eff = {args.m_eff_sq}  (mostenit din G17, singurul parametru extern)")
    log()
    log(f"Graf: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"Moduri: {args.n_modes}  Iteratii: {args.n_iter}")

    thr = G31Thresholds()
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
    log()
    log("  Diferenta cheie fata de G17/G20:")
    log("    G17/G20: adj = list[list[int]] — ponderi Jaccard aruncate")
    log("    G31:     adj_w = list[list[(j, J_ij)]] — ponderi pastrate explicit")

    results["graph"] = {
        "n": n, "edges": edge_count,
        "mean_weighted_degree": mean_deg_w,
        "max_weighted_degree": max_deg_w,
    }

    # ── [1] Eigenmode-uri ale K_m² ─────────────────────────────────────────────
    log(f"\n[1] Eigenmode-uri K_m²  ({args.n_modes} moduri × {args.n_iter} iter)")
    log("  K_m² = Laplacian_Jaccard_ponderat + m²*I")
    log("  Toate eigenvalori >= m² (K pozitiv definit)")
    t1 = time.time()
    lambdas, eigvecs = compute_eigenmodes_Km2(
        adj_w, n, args.n_modes, args.n_iter, args.m_eff_sq,
        random.Random(args.seed + 1),
    )
    K_eff = len(lambdas)
    omegas = [math.sqrt(lam) for lam in lambdas]
    log(f"  Calculat in {time.time()-t1:.2f}s  |  {K_eff} moduri")
    log(f"  lambda_min = {fmt(lambdas[0])}  ->  omega_min = {fmt(omegas[0])}")
    log(f"  lambda_max = {fmt(lambdas[-1])}  ->  omega_max = {fmt(omegas[-1])}")
    log(f"  omega_mean = {fmt(sum(omegas)/K_eff)}")

    results["eigenmodes"] = {
        "n_modes_computed": K_eff,
        "lambda_min": lambdas[0],
        "lambda_max": lambdas[-1],
        "omega_min":  omegas[0],
        "omega_max":  omegas[-1],
        "omega_mean": sum(omegas) / K_eff,
    }

    # ── [2] Observable cuantice din |Psi_0> ────────────────────────────────────
    log("\n[2] Observable cuantice (starea fundamentala |Psi_0>)")
    E_0, cv_natural, sigma2_nodes, heisenberg = compute_quantum_observables(
        lambdas, eigvecs, n
    )
    E_0_per_mode = E_0 / K_eff
    sigma2_max   = max(sigma2_nodes)
    sigma2_mean  = sum(sigma2_nodes) / n
    heisenberg_mean = sum(heisenberg) / K_eff
    heisenberg_err  = max(abs(h - 0.5) for h in heisenberg)

    log(f"  E_0          = {fmt(E_0)}  (zero-point energy totala, {K_eff} moduri)")
    log(f"  E_0 / N_modes= {fmt(E_0_per_mode)}  (energie per mod)")
    log(f"  cv_natural   = {fmt(cv_natural)}  (std(omega)/mean(omega) din spectrul K)")
    log(f"  cv_G17       = {CV_G17}  (Porter-Thomas din eigenmodes RW)")
    log(f"  |cv_nat - cv_G17|/cv_G17 = {fmt(abs(cv_natural - CV_G17)/CV_G17)}")
    log(f"  sigma²_max   = {fmt(sigma2_max)}  (fluctuatii max per nod)")
    log(f"  sigma²_mean  = {fmt(sigma2_mean)}  (fluctuatii medii per nod)")
    log(f"  Heisenberg   = {fmt(heisenberg_mean)}  (trebuie 0.5 exact)")
    log(f"  Heisenberg_err = {fmt(heisenberg_err)}  (eroare maxima per mod)")

    results["observables"] = {
        "E_0": E_0,
        "E_0_per_mode": E_0_per_mode,
        "cv_natural": cv_natural,
        "cv_G17": CV_G17,
        "cv_relative_diff": abs(cv_natural - CV_G17) / CV_G17,
        "sigma2_max": sigma2_max,
        "sigma2_mean": sigma2_mean,
        "heisenberg_mean": heisenberg_mean,
        "heisenberg_err_max": heisenberg_err,
    }

    # ── [3] Interpretare fizica ────────────────────────────────────────────────
    log("\n[3] Interpretare fizica")
    log(f"  hbar = 1 (natural: Sigma in [0,1], K dimensionless, actiune dimensionless)")
    log(f"  omega_min = sqrt(m²) = {fmt(math.sqrt(args.m_eff_sq))}  (masa de repaus — gap spectral)")
    log(f"  Laplacian ponderat vs RW neponderat:")
    log(f"    G17 omega_k ~ sqrt(mu_RW + m²)  cu mu_RW in [0, 2] (neponderat)")
    log(f"    G31 omega_a ~ sqrt(lambda_L + m²) cu lambda_L in [m², lambda_max(K)]")
    log(f"    Diferenta: G31 foloseste ponderile J_ij explicit — mai mult fizic")

    # ── [4] Gates ──────────────────────────────────────────────────────────────
    log("\n" + "=" * 70)
    log("GATES G31")
    log("=" * 70)

    gates: dict[str, dict] = {}

    # G31a — Energia de vacuum nontriviala
    g31a = (thr.g31a_e0_per_mode_lo < E_0_per_mode < thr.g31a_e0_per_mode_hi)
    gates["G31a"] = {
        "name": "Non-trivial vacuum energy",
        "value": E_0_per_mode,
        "threshold_lo": thr.g31a_e0_per_mode_lo,
        "threshold_hi": thr.g31a_e0_per_mode_hi,
        "condition": f"{thr.g31a_e0_per_mode_lo} < E_0/N_modes < {thr.g31a_e0_per_mode_hi}",
        "passed": g31a,
    }
    status_a = "PASS" if g31a else "FAIL"
    log(f"\nG31a — Vacuum energy per mod: {fmt(E_0_per_mode)}")
    log(f"       Prag: ({thr.g31a_e0_per_mode_lo}, {thr.g31a_e0_per_mode_hi})  ->  {status_a}")

    # G31b — cv_natural fizic rezonabil
    g31b = (thr.g31b_cv_lo < cv_natural < thr.g31b_cv_hi)
    gates["G31b"] = {
        "name": "Physically reasonable frequency spread",
        "value": cv_natural,
        "threshold_lo": thr.g31b_cv_lo,
        "threshold_hi": thr.g31b_cv_hi,
        "condition": f"{thr.g31b_cv_lo} < cv_natural < {thr.g31b_cv_hi}",
        "passed": g31b,
    }
    status_b = "PASS" if g31b else "FAIL"
    log(f"\nG31b — cv_natural: {fmt(cv_natural)}")
    log(f"       Prag: ({thr.g31b_cv_lo}, {thr.g31b_cv_hi})  ->  {status_b}")

    # G31c — Confinement (fluctuatii zero-point in [0,1])
    g31c = (sigma2_max < thr.g31c_sigma2_max)
    gates["G31c"] = {
        "name": "Zero-point fluctuations confined within [0,1]",
        "value": sigma2_max,
        "threshold": thr.g31c_sigma2_max,
        "condition": f"sigma²_max < {thr.g31c_sigma2_max} (sigma < 0.25)",
        "passed": g31c,
    }
    status_c = "PASS" if g31c else "FAIL"
    log(f"\nG31c — Confinement sigma²_max: {fmt(sigma2_max)}")
    log(f"       Prag: < {thr.g31c_sigma2_max}  ->  {status_c}")

    # G31d — Consistenta cv_natural cu cv_G17
    cv_rel = abs(cv_natural - CV_G17) / CV_G17
    g31d = (cv_rel < thr.g31d_cv_rel_tol)
    gates["G31d"] = {
        "name": "cv_natural consistent with cv_G17",
        "value": cv_rel,
        "threshold": thr.g31d_cv_rel_tol,
        "cv_natural": cv_natural,
        "cv_G17": CV_G17,
        "condition": f"|cv_natural - cv_G17|/cv_G17 < {thr.g31d_cv_rel_tol}",
        "passed": g31d,
    }
    status_d = "PASS" if g31d else "FAIL"
    log(f"\nG31d — Consistenta cv: |{fmt(cv_natural)} - {CV_G17}| / {CV_G17} = {fmt(cv_rel)}")
    log(f"       Prag: < {thr.g31d_cv_rel_tol}  ->  {status_d}")

    # ── Sumar ──────────────────────────────────────────────────────────────────
    n_pass = sum([g31a, g31b, g31c, g31d])
    n_total = 4
    all_pass = (n_pass == n_total)

    log("\n" + "=" * 70)
    log(f"SUMAR: {n_pass}/{n_total} gate-uri trecute")
    log(f"G31a [{status_a}]  G31b [{status_b}]  G31c [{status_c}]  G31d [{status_d}]")
    log("=" * 70)

    if all_pass:
        log("\n*** TOATE GATE-URILE G31 TRECUTE ***")
        log("Hamiltonianul cuantic natural este consistent cu teoria QNG existenta.")
    else:
        log("\n*** UNELE GATE-URI PICATE ***")
        if not g31a:
            log("  G31a: energia de vacuum per mod in afara domeniului asteptat")
        if not g31b:
            log("  G31b: cv_natural in afara intervalului fizic [0.20, 0.70]")
        if not g31c:
            log("  G31c: fluctuatii zero-point depasesc confinementul in [0,1]")
        if not g31d:
            log("  G31d: cv_natural inconsistent cu cv_G17 (diferenta > 50%)")

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

    # JSON summary
    json_path = out_dir / "summary.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    log(f"\nArtefacte scrise in: {out_dir}")
    log(f"  summary.json")

    # CSV eigenvalues
    eig_rows = [
        {"mode": k, "lambda": lambdas[k], "omega": omegas[k],
         "sigma_Sigma": 1.0 / math.sqrt(2.0 * omegas[k]),
         "sigma_pi":    math.sqrt(omegas[k] / 2.0),
         "heisenberg":  heisenberg[k]}
        for k in range(K_eff)
    ]
    eig_path = out_dir / "eigenmodes.csv"
    write_csv(eig_path, ["mode", "lambda", "omega", "sigma_Sigma", "sigma_pi", "heisenberg"], eig_rows)
    log("  eigenmodes.csv")

    # CSV node fluctuations
    node_rows = [{"node": i, "sigma2": sigma2_nodes[i]} for i in range(n)]
    node_path = out_dir / "node_fluctuations.csv"
    write_csv(node_path, ["node", "sigma2"], node_rows)
    log("  node_fluctuations.csv")

    # Log
    log_path = out_dir / "run.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    log("  run.log")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
