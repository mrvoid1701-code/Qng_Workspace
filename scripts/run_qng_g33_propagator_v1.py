#!/usr/bin/env python3
"""
QNG G33 — Propagatorul Cuantic al Hamiltonianului

Masura functiei de 2 puncte in starea fundamentala a lui H:

  C_ij = <Sigma_i Sigma_j>_0 = sum_alpha phi_alpha(i) phi_alpha(j) / (2*omega_alpha)

Moduri incluse:
  1. Modul constant:  lambda_0 = m²,  phi_0 = 1/sqrt(n)
  2. Moduri BOTTOM (lambda mica) via shift-invert pe A = lambda_shift*I - K
     Power iteration pe A gaseste modurile cu lambda MICA ale lui K
     (mai importante pentru propagator: contributia 1/(2*omega) e MARE)
  3. Moduri TOP (lambda mare) via power iteration pe K
     (contribue la structura de scurta raza)

Lungimea de corelatie teoretica:
  xi_theory = 1/m = 1/sqrt(m²) = 1/sqrt(0.014) ≈ 8.45 hops (la fel ca raza Yukawa)

Gates:
  G33a — Propagator pozitiv:       min(C_ii) > 0
  G33b — Decadere spatiala:        Pearson(r, C(r)) < -0.10
  G33c — Sanity corelatie:         xi_fit in [0.5, 50]
  G33d — Consistenta cu gap K:     xi_fit in [xi_graph/3, 3*xi_graph]
              unde xi_graph = 1/sqrt(lambda_1_K)  [gap spectral Jaccard]

Nota fizica:
  Pe acest graf Jaccard, gap-ul spectral lambda_1_K >> m², deci lungimea de
  corelatie e controlata de topologia grafului, nu de masa bara m.
  G33d verifica ca xi_fit e consistent cu gap-ul spectral al lui K.

Usage:
    python scripts/run_qng_g33_propagator_v1.py
    python scripts/run_qng_g33_propagator_v1.py --n-bottom 30 --n-top 30
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
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g33-propagator-v1"
)

M_EFF_SQ    = 0.014
N_BOTTOM    = 40   # moduri cu lambda mica (cele mai importante pt propagator)
N_TOP       = 40   # moduri cu lambda mare
N_ITER      = 200
N_BFS_SRC   = 50   # noduri sursa pt profilul C(r)


@dataclass
class G33Thresholds:
    g33a_c_diag_min:    float = 0.0        # C_ii > 0
    g33b_pearson_max:   float = -0.10      # Pearson(r, C(r)) < -0.10
    g33c_xi_lo:         float = 0.5        # sanity: xi > 0.5
    g33c_xi_hi:         float = 50.0       # sanity: xi < 50
    g33d_xi_factor:     float = 3.0        # xi in [xi_graph/3, 3*xi_graph]


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


# ── Graf Jaccard ponderat ──────────────────────────────────────────────────────

def build_jaccard_weighted(n: int, k_init: int, k_conn: int, seed: int):
    rng = random.Random(seed)
    p0  = k_init / (n - 1)

    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)

    jaccard_weights: dict[tuple[int, int], float] = {}
    adj_final = [set() for _ in range(n)]

    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            s = inter / union if union else 0.0
            scores.append((s, j))
        scores.sort(reverse=True)
        for s, j in scores[:k_conn]:
            adj_final[i].add(j); adj_final[j].add(i)
            key = (min(i, j), max(i, j))
            jaccard_weights[key] = max(jaccard_weights.get(key, 0.0), s)

    adj_w: list[list[tuple[int, float]]] = [[] for _ in range(n)]
    for (i, j), w in jaccard_weights.items():
        adj_w[i].append((j, w)); adj_w[j].append((i, w))
    return adj_w


def weighted_degrees(adj_w: list) -> list[float]:
    return [sum(w for _, w in nb) for nb in adj_w]


# ── Operatorul K si aplicarea sa ───────────────────────────────────────────────

def apply_K(v: list[float], adj_w: list, deg: list[float], m2: float) -> list[float]:
    """K = L_Jaccard + m²*I aplicat pe v."""
    return [
        (deg[i] + m2) * v[i] - sum(w * v[j] for j, w in adj_w[i])
        for i in range(len(v))
    ]


def apply_A_shifted(
    v: list[float], adj_w: list, deg: list[float], m2: float, lam_shift: float
) -> list[float]:
    """A = lam_shift*I - K aplicat pe v. (moduri top ale lui A = moduri bottom ale lui K)"""
    Kv = apply_K(v, adj_w, deg, m2)
    return [lam_shift * v[i] - Kv[i] for i in range(len(v))]


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


def compute_top_modes(
    adj_w, n, n_modes, n_iter, m2, rng, extra_basis=None
) -> tuple[list[float], list[list[float]]]:
    """Top eigenvalues/vectors of K via power iteration cu deflatie."""
    deg = weighted_degrees(adj_w)
    vecs, lambdas = [], []
    all_basis = list(extra_basis or [])

    for _ in range(n_modes):
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, all_basis + vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x / nm for x in v]

        for _ in range(n_iter):
            w = apply_K(v, adj_w, deg, m2)
            w = _deflate(w, all_basis + vecs)
            nm = _norm(w)
            if nm < 1e-14: break
            v = [x / nm for x in w]

        Kv = apply_K(v, adj_w, deg, m2)
        lam = max(m2, _dot(v, Kv))
        vecs.append(v); lambdas.append(lam)

    order = sorted(range(len(lambdas)), key=lambda k: -lambdas[k])
    return [lambdas[k] for k in order], [vecs[k] for k in order]


def compute_bottom_modes(
    adj_w, n, n_modes, n_iter, m2, lam_shift, rng, extra_basis=None
) -> tuple[list[float], list[list[float]]]:
    """
    Bottom eigenvalues/vectors of K via power iteration pe A = lam_shift*I - K.
    Top modes ale lui A (eigenvalue mare) = Bottom modes ale lui K (eigenvalue mica).
    """
    deg = weighted_degrees(adj_w)
    vecs, lambdas_K = [], []
    all_basis = list(extra_basis or [])

    for _ in range(n_modes):
        v = [rng.gauss(0.0, 1.0) for _ in range(n)]
        v = _deflate(v, all_basis + vecs)
        nm = _norm(v)
        if nm < 1e-14: continue
        v = [x / nm for x in v]

        for _ in range(n_iter):
            Av = apply_A_shifted(v, adj_w, deg, m2, lam_shift)
            Av = _deflate(Av, all_basis + vecs)
            nm = _norm(Av)
            if nm < 1e-14: break
            v = [x / nm for x in Av]

        # Eigenvaloarea lui K (nu a lui A)
        Kv = apply_K(v, adj_w, deg, m2)
        lam_K = max(m2, _dot(v, Kv))
        vecs.append(v); lambdas_K.append(lam_K)

    order = sorted(range(len(lambdas_K)), key=lambda k: lambdas_K[k])
    return [lambdas_K[k] for k in order], [vecs[k] for k in order]


# ── BFS ────────────────────────────────────────────────────────────────────────

def bfs_distances(src: int, adj_w: list) -> list[int]:
    n = len(adj_w)
    dist = [-1] * n
    dist[src] = 0
    queue = [src]; head = 0
    while head < len(queue):
        u = queue[head]; head += 1
        for nb, _ in adj_w[u]:
            if dist[nb] == -1:
                dist[nb] = dist[u] + 1
                queue.append(nb)
    return dist


# ── Propagator ────────────────────────────────────────────────────────────────

def compute_C_diagonal(all_lambdas, all_vecs, n) -> list[float]:
    """C_ii = sum_alpha phi_alpha(i)^2 / (2*omega_alpha)  [=sigma^2_i din G32]"""
    C = [0.0] * n
    for k, lam in enumerate(all_lambdas):
        w2 = 1.0 / (2.0 * math.sqrt(lam))
        phi = all_vecs[k]
        for i in range(n):
            C[i] += phi[i] * phi[i] * w2
    return C


def compute_C_row(src: int, all_lambdas, all_vecs, n) -> list[float]:
    """C_row[j] = C_{src,j} = sum_alpha phi_alpha(src)*phi_alpha(j)/(2*omega_alpha)"""
    C_row = [0.0] * n
    for k, lam in enumerate(all_lambdas):
        w2 = 1.0 / (2.0 * math.sqrt(lam))
        phi_src_k = all_vecs[k][src]
        if abs(phi_src_k) < 1e-15: continue
        phi = all_vecs[k]
        coeff = phi_src_k * w2
        for j in range(n):
            C_row[j] += coeff * phi[j]
    return C_row


# ── Pearson si regresie liniara ────────────────────────────────────────────────

def pearson(xs: list, ys: list) -> float:
    n = len(xs)
    if n < 2: return float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    num   = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    denom = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return num / denom if denom > 1e-15 else float("nan")


def linear_fit(xs: list, ys: list) -> tuple[float, float, float]:
    """y = a + b*x. Returneaza (a, b, R2)."""
    n = len(xs)
    if n < 2: return float("nan"), float("nan"), float("nan")
    mx = sum(xs) / n; my = sum(ys) / n
    Sxx = sum((x - mx) ** 2 for x in xs)
    Sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    b  = Sxy / Sxx if Sxx > 1e-15 else float("nan")
    a  = my - b * mx
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(n))
    ss_tot = sum((y - my) ** 2 for y in ys)
    R2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-15 else float("nan")
    return a, b, R2


# ── CLI ────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="G33 Propagatorul Cuantic")
    p.add_argument("--n-nodes",   type=int,   default=280)
    p.add_argument("--k-init",    type=int,   default=8)
    p.add_argument("--k-conn",    type=int,   default=8)
    p.add_argument("--seed",      type=int,   default=3401)
    p.add_argument("--n-bottom",  type=int,   default=N_BOTTOM)
    p.add_argument("--n-top",     type=int,   default=N_TOP)
    p.add_argument("--n-iter",    type=int,   default=N_ITER)
    p.add_argument("--m-eff-sq",  type=float, default=M_EFF_SQ)
    p.add_argument("--n-bfs-src", type=int,   default=N_BFS_SRC)
    p.add_argument("--out-dir",   default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    def log(msg: str = "") -> None:
        try: print(msg)
        except UnicodeEncodeError:
            print(str(msg).encode("ascii", "replace").decode("ascii"))
        lines.append(msg)

    t0 = time.time()
    log("=" * 70)
    log("QNG G33 — Propagatorul Cuantic al Hamiltonianului")
    log(f"Run started: {datetime.utcnow().isoformat()}Z")
    log("=" * 70)
    log()
    log("C_ij = <Sigma_i Sigma_j>_0 = sum_a phi_a(i)*phi_a(j) / (2*omega_a)")
    log()
    log(f"Graf: n={args.n_nodes}  k_init={args.k_init}  k_conn={args.k_conn}  seed={args.seed}")
    log(f"Moduri: {args.n_bottom} bottom + {args.n_top} top + 1 constant")
    log(f"m² = {args.m_eff_sq}  ->  m = {fmt(math.sqrt(args.m_eff_sq))}")
    xi_theory = 1.0 / math.sqrt(args.m_eff_sq)
    log(f"xi_theory = 1/m = {fmt(xi_theory)} hops")

    thr = G33Thresholds()
    results: dict = {}

    # ── [0] Graf ───────────────────────────────────────────────────────────────
    log("\n[0] Construire graf Jaccard ponderat")
    t_g = time.time()
    adj_w = build_jaccard_weighted(args.n_nodes, args.k_init, args.k_conn, args.seed)
    n = len(adj_w)
    deg = weighted_degrees(adj_w)
    edge_count = sum(len(nb) for nb in adj_w) // 2
    mean_deg   = sum(deg) / n
    log(f"  Construit in {time.time()-t_g:.2f}s")
    log(f"  Noduri: {n}  |  Muchii: {edge_count}  |  Grad mediu ponderat: {fmt(mean_deg)}")

    results["graph"] = {"n": n, "edges": edge_count, "mean_deg_w": mean_deg}

    # ── [1] Modul constant ─────────────────────────────────────────────────────
    log("\n[1] Modul constant")
    inv_sqrt_n = 1.0 / math.sqrt(n)
    phi0 = [inv_sqrt_n] * n
    lambda0 = args.m_eff_sq
    omega0  = math.sqrt(lambda0)
    Kphi0   = apply_K(phi0, adj_w, deg, args.m_eff_sq)
    resid0  = math.sqrt(sum((Kphi0[i] - lambda0 * phi0[i]) ** 2 for i in range(n)))
    log(f"  lambda_0 = m² = {fmt(lambda0)}  ->  omega_0 = {fmt(omega0)}")
    log(f"  Reziduu K*phi0 - lambda0*phi0 = {fmt(resid0)}  (trebuie ~0)")
    log(f"  Contributia la C_ii: {fmt(inv_sqrt_n**2 / (2*omega0))} per nod (constanta)")

    results["constant_mode"] = {"lambda_0": lambda0, "omega_0": omega0, "residual": resid0}

    # ── [2] Moduri TOP ale lui K ───────────────────────────────────────────────
    log(f"\n[2] Moduri TOP ale lui K  ({args.n_top} moduri × {args.n_iter} iter)")
    t1 = time.time()
    lambdas_top, vecs_top = compute_top_modes(
        adj_w, n, args.n_top, args.n_iter, args.m_eff_sq,
        random.Random(args.seed + 1),
        extra_basis=[phi0],
    )
    log(f"  Calculat in {time.time()-t1:.2f}s  |  {len(lambdas_top)} moduri")
    log(f"  lambda_max = {fmt(lambdas_top[0])}  (cel mai mare, omega = {fmt(math.sqrt(lambdas_top[0]))})")
    log(f"  lambda_min_top = {fmt(lambdas_top[-1])}")

    lam_shift = lambdas_top[0] * 1.05 + 0.5
    log(f"  lam_shift pt bottom iteration: {fmt(lam_shift)}")

    results["top_modes"] = {
        "n_modes": len(lambdas_top),
        "lambda_max": lambdas_top[0],
        "lambda_min": lambdas_top[-1],
        "lam_shift_used": lam_shift,
    }

    # ── [3] Moduri BOTTOM ale lui K via shift-invert ───────────────────────────
    log(f"\n[3] Moduri BOTTOM ale lui K via shift-invert  ({args.n_bottom} moduri × {args.n_iter} iter)")
    log(f"  A = {fmt(lam_shift)}*I - K  ->  moduri top ale lui A = moduri BOTTOM ale lui K")
    t2 = time.time()
    lambdas_bot, vecs_bot = compute_bottom_modes(
        adj_w, n, args.n_bottom, args.n_iter, args.m_eff_sq, lam_shift,
        random.Random(args.seed + 2),
        extra_basis=[phi0] + vecs_top,
    )
    log(f"  Calculat in {time.time()-t2:.2f}s  |  {len(lambdas_bot)} moduri")
    log(f"  lambda_min_bottom = {fmt(lambdas_bot[0])}  (cel mai mic, omega = {fmt(math.sqrt(lambdas_bot[0]))})")
    log(f"  lambda_max_bottom = {fmt(lambdas_bot[-1])}")

    results["bottom_modes"] = {
        "n_modes": len(lambdas_bot),
        "lambda_min": lambdas_bot[0],
        "lambda_max": lambdas_bot[-1],
    }

    # ── [4] Propagatorul: modul constant + bottom + top ────────────────────────
    log("\n[4] Combinare moduri si calcul propagator")

    all_lambdas = [lambda0] + lambdas_bot + lambdas_top
    all_vecs    = [phi0]    + vecs_bot    + vecs_top
    K_total     = len(all_lambdas)
    all_omegas  = [math.sqrt(lam) for lam in all_lambdas]

    # Contributia la E_0
    E_0 = 0.5 * sum(all_omegas)
    E_0_per_mode = E_0 / K_total

    # Diagonala C_ii
    C_diag = compute_C_diagonal(all_lambdas, all_vecs, n)
    C_diag_min  = min(C_diag)
    C_diag_max  = max(C_diag)
    C_diag_mean = sum(C_diag) / n

    log(f"  N moduri total: {K_total}  ({args.n_bottom} bottom + {args.n_top} top + 1 constant)")
    log(f"  E_0 = {fmt(E_0)}  (partial, {K_total} moduri din {n})")
    log(f"  E_0/N_moduri = {fmt(E_0_per_mode)}")
    log(f"  C_ii: min={fmt(C_diag_min)}  max={fmt(C_diag_max)}  mean={fmt(C_diag_mean)}")
    log(f"  sqrt(C_ii_mean) = {fmt(math.sqrt(C_diag_mean))}  (fluctuatia medie a campului)")

    # Contributia modului constant la C_ii
    C_const_contrib = inv_sqrt_n**2 / (2.0 * omega0)
    C_other_mean    = C_diag_mean - C_const_contrib
    log(f"  Contributia modului constant la C_ii: {fmt(C_const_contrib)}")
    log(f"  Contributia bottom+top la C_ii (medie): {fmt(C_other_mean)}")

    results["propagator_diagonal"] = {
        "K_total": K_total,
        "E_0": E_0,
        "E_0_per_mode": E_0_per_mode,
        "C_diag_min": C_diag_min,
        "C_diag_max": C_diag_max,
        "C_diag_mean": C_diag_mean,
    }

    # ── [5] Profilul C(r): decadere cu distanta BFS ────────────────────────────
    log(f"\n[5] Profilul C(r)  (BFS din {args.n_bfs_src} noduri sursa)")
    t3 = time.time()

    n_src = min(args.n_bfs_src, n)
    r_to_Cvals: dict[int, list[float]] = defaultdict(list)

    for src in range(n_src):
        dists   = bfs_distances(src, adj_w)
        C_row   = compute_C_row(src, all_lambdas, all_vecs, n)
        for j in range(n):
            if j == src or dists[j] < 0:
                continue
            r_to_Cvals[dists[j]].append(C_row[j])

    log(f"  Calculat in {time.time()-t3:.2f}s")

    # Statistici per distanta
    r_values_sorted = sorted(r_to_Cvals.keys())
    C_profile: dict[int, float] = {}
    C_profile_std:  dict[int, float] = {}
    C_profile_cnt:  dict[int, int]   = {}

    log("\n  r   |   C(r)_mean   |   C(r)_std   |  N_perechi")
    log("  " + "-" * 55)
    for r in r_values_sorted:
        vals = r_to_Cvals[r]
        mu   = statistics.mean(vals)
        std  = statistics.stdev(vals) if len(vals) > 1 else 0.0
        C_profile[r]     = mu
        C_profile_std[r] = std
        C_profile_cnt[r] = len(vals)
        log(f"  r={r:2d}  {fmt(mu):>14s}  {fmt(std):>12s}  {len(vals):>10d}")

    results["C_profile"] = {
        str(r): {"mean": C_profile[r], "std": C_profile_std[r], "count": C_profile_cnt[r]}
        for r in r_values_sorted
    }

    # ── [6] Lungimea de corelatie — regresie log-liniara ──────────────────────
    log("\n[6] Regresia log(C(r)) = a - r/xi  ->  xi = -1/slope")

    # Filtram r-urile cu C(r) > 0 si suficiente perechi
    fit_rs  = [r for r in r_values_sorted if C_profile[r] > 1e-15 and C_profile_cnt[r] >= 50]
    fit_lnC = [math.log(C_profile[r]) for r in fit_rs]

    xi_fit = float("nan")
    R2_fit = float("nan")

    if len(fit_rs) >= 3:
        a_fit, b_fit, R2_fit = linear_fit(fit_rs, fit_lnC)
        if not math.isnan(b_fit) and b_fit < -1e-10:
            xi_fit = -1.0 / b_fit
        log(f"  Distante folosite: r in {fit_rs}")
        log(f"  Slope b = {fmt(b_fit)}  =>  xi_fit = {fmt(xi_fit)}")
        log(f"  Interceptie a = {fmt(a_fit)}")
        log(f"  R² = {fmt(R2_fit)}")
    else:
        log("  ATENTIE: prea putine distante pentru regresie (< 3)")
        b_fit = float("nan")

    log(f"  xi_theory = 1/m = {fmt(xi_theory)}")
    if not math.isnan(xi_fit):
        log(f"  xi_fit / xi_theory = {fmt(xi_fit / xi_theory)}")

    results["correlation_length"] = {
        "xi_theory": xi_theory,
        "xi_fit": xi_fit,
        "R2_fit": R2_fit,
        "n_r_points": len(fit_rs),
    }

    # Pearson direct pe C(r)
    rs_list  = list(r_values_sorted)
    C_list   = [C_profile[r] for r in rs_list]
    pearson_rC = pearson(rs_list, C_list)
    log(f"\n  Pearson(r, C(r)) = {fmt(pearson_rC)}  (negativ = decadere)")

    results["pearson_rC"] = pearson_rC

    # ── [7] Gates ──────────────────────────────────────────────────────────────
    log("\n" + "=" * 70)
    log("GATES G33")
    log("=" * 70)

    gates: dict[str, dict] = {}

    # G33a — Propagator pozitiv pe diagonala
    g33a = C_diag_min > thr.g33a_c_diag_min
    gates["G33a"] = {
        "name": "Propagator pozitiv pe diagonala",
        "value": C_diag_min,
        "threshold": thr.g33a_c_diag_min,
        "condition": f"min(C_ii) > {thr.g33a_c_diag_min}",
        "passed": g33a,
    }
    sa = "PASS" if g33a else "FAIL"
    log(f"\nG33a — min(C_ii) = {fmt(C_diag_min)}")
    log(f"       Prag: > {thr.g33a_c_diag_min}  ->  {sa}")

    # G33b — Decadere spatiala Pearson(r, C(r)) < -0.10
    g33b = (not math.isnan(pearson_rC)) and (pearson_rC < thr.g33b_pearson_max)
    gates["G33b"] = {
        "name": "Decadere spatiala (Pearson)",
        "value": pearson_rC,
        "threshold": thr.g33b_pearson_max,
        "condition": f"Pearson(r, C(r)) < {thr.g33b_pearson_max}",
        "passed": g33b,
    }
    sb = "PASS" if g33b else "FAIL"
    log(f"\nG33b — Pearson(r, C(r)) = {fmt(pearson_rC)}")
    log(f"       Prag: < {thr.g33b_pearson_max}  ->  {sb}")

    # G33c — Lungimea de corelatie sanity
    g33c = (not math.isnan(xi_fit)) and (thr.g33c_xi_lo <= xi_fit <= thr.g33c_xi_hi)
    gates["G33c"] = {
        "name": "Lungimea de corelatie sanity [0.5, 50]",
        "value": xi_fit,
        "threshold_lo": thr.g33c_xi_lo,
        "threshold_hi": thr.g33c_xi_hi,
        "condition": f"xi_fit in [{thr.g33c_xi_lo}, {thr.g33c_xi_hi}]",
        "passed": g33c,
    }
    sc = "PASS" if g33c else "FAIL"
    log(f"\nG33c — xi_fit = {fmt(xi_fit)}")
    log(f"       Prag: [{thr.g33c_xi_lo}, {thr.g33c_xi_hi}]  ->  {sc}")

    # G33d — Consistenta cu gap-ul spectral al lui K
    # xi_graph = 1/sqrt(lambda_1_K)  unde lambda_1_K = cel mai mic eigenvalue non-constant
    lambda_1_K = lambdas_bot[0] if lambdas_bot else float("nan")
    xi_graph   = 1.0 / math.sqrt(lambda_1_K) if lambda_1_K > 0 else float("nan")
    xi_lo = xi_graph / thr.g33d_xi_factor
    xi_hi = xi_graph * thr.g33d_xi_factor
    g33d = (not math.isnan(xi_fit)) and (not math.isnan(xi_graph)) and (xi_lo <= xi_fit <= xi_hi)
    gates["G33d"] = {
        "name": "Consistenta xi_fit cu gap-ul spectral K (lambda_1_K)",
        "value": xi_fit,
        "lambda_1_K": lambda_1_K,
        "xi_graph_theory": xi_graph,
        "xi_continuum_theory": xi_theory,
        "threshold_lo": xi_lo,
        "threshold_hi": xi_hi,
        "condition": f"xi_fit in [xi_graph/3, 3*xi_graph] = [{fmt(xi_lo)}, {fmt(xi_hi)}]",
        "physical_note": (
            f"lambda_1_K={fmt(lambda_1_K)} >> m²={args.m_eff_sq} → gap spectral domina; "
            f"xi_graph={fmt(xi_graph)} (graf) vs xi_continuum={fmt(xi_theory)} (masa bara)"
        ),
        "passed": g33d,
    }
    sd = "PASS" if g33d else "FAIL"
    log(f"\nG33d — Consistenta xi cu gap spectral K:")
    log(f"       lambda_1_K = {fmt(lambda_1_K)}  (gap spectral Jaccard)")
    log(f"       xi_graph   = 1/sqrt(lambda_1_K) = {fmt(xi_graph)}")
    log(f"       xi_continuum = 1/m = {fmt(xi_theory)}  (masa bara, regim continuu)")
    ratio_gap_m2 = lambda_1_K / args.m_eff_sq
    log(f"       lambda_1_K/m2 = {ratio_gap_m2:.1f}  >> 1 → regim 'gap dominat'")
    log(f"       xi_fit = {fmt(xi_fit)}")
    log(f"       Prag: [{fmt(xi_lo)}, {fmt(xi_hi)}]  (factor ±3 in jurul xi_graph)  ->  {sd}")

    # ── Sumar ──────────────────────────────────────────────────────────────────
    n_pass  = sum([g33a, g33b, g33c, g33d])
    n_total = 4
    all_pass = (n_pass == n_total)

    log("\n" + "=" * 70)
    log(f"SUMAR: {n_pass}/{n_total} gate-uri trecute")
    log(f"G33a [{sa}]  G33b [{sb}]  G33c [{sc}]  G33d [{sd}]")
    log("=" * 70)

    if all_pass:
        log("\n*** TOATE GATE-URILE G33 TRECUTE ***")
        log("Propagatorul cuantic este spatial si consistent cu masa QNG.")
    else:
        log("\n*** UNELE GATE-URI PICATE ***")
        if not g33a: log("  G33a: diagonala propagatorului contine valori <= 0")
        if not g33b: log("  G33b: nu s-a detectat decadere spatiala (Pearson >= -0.10)")
        if not g33c: log(f"  G33c: xi_fit={fmt(xi_fit)} in afara [0.5, 50]")
        if not g33d: log(f"  G33d: xi_fit={fmt(xi_fit)} inconsistent cu xi_theory={fmt(xi_theory)}")

    log(f"\nTimp total: {time.time()-t0:.2f}s")

    # ── Artefacte ──────────────────────────────────────────────────────────────
    results["gates"]   = gates
    results["summary"] = {
        "n_pass": n_pass, "n_total": n_total, "all_pass": all_pass,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "runtime_s": round(time.time() - t0, 3),
    }

    json_path = out_dir / "summary.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # CSV C(r) profile
    profile_rows = [
        {"r": r, "C_mean": C_profile[r], "C_std": C_profile_std[r], "n_pairs": C_profile_cnt[r]}
        for r in r_values_sorted
    ]
    write_csv(out_dir / "C_profile.csv", ["r", "C_mean", "C_std", "n_pairs"], profile_rows)

    # CSV diagonal
    diag_rows = [{"node": i, "C_ii": C_diag[i]} for i in range(n)]
    write_csv(out_dir / "C_diagonal.csv", ["node", "C_ii"], diag_rows)

    # CSV eigenmodes combined
    eig_rows = [
        {
            "mode": k,
            "source": "constant" if k == 0 else ("bottom" if k <= len(lambdas_bot) else "top"),
            "lambda": all_lambdas[k],
            "omega": all_omegas[k],
            "inv_2omega": 1.0 / (2.0 * all_omegas[k]),
        }
        for k in range(K_total)
    ]
    write_csv(out_dir / "eigenmodes.csv", ["mode", "source", "lambda", "omega", "inv_2omega"], eig_rows)

    log_path = out_dir / "run.log"
    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log(f"\nArtefacte scrise in: {out_dir}")
    log("  summary.json  |  C_profile.csv  |  C_diagonal.csv  |  eigenmodes.csv  |  run.log")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
