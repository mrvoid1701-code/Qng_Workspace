#!/usr/bin/env python3
"""
Modul comun: propagator QNG cu deflatie proprie.

Reproduce gamma din G33 (1.55–1.87) prin:
  - Power iteration cu deflatie secventiala pentru moduri TOP
  - Shift-invert cu deflatie pentru moduri BOTTOM
  - Modul constant separat
"""

from __future__ import annotations
import math, random
from collections import deque

M_SQ_DEFAULT = 0.014
N_ITER_DEFAULT = 300


def build_jaccard(n: int, k_init: int, k_conn: int, seed: int):
    rng = random.Random(seed); p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    jw = {}
    for i in range(n):
        Ni = adj0[i] | {i}; sc = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            sc.append((inter / union if union else 0.0, j))
        sc.sort(reverse=True)
        for s, j in sc[:k_conn]:
            key = (min(i, j), max(i, j))
            jw[key] = max(jw.get(key, 0.0), s)
    adj_w = [[] for _ in range(n)]
    for (i, j), w in jw.items():
        adj_w[i].append((j, w)); adj_w[j].append((i, w))
    return adj_w


def permute_graph(adj_w, perm):
    n = len(adj_w); new_adj = [[] for _ in range(n)]
    for i, nb in enumerate(adj_w):
        for j, w in nb:
            new_adj[perm[i]].append((perm[j], w))
    return new_adj


def mat_vec(adj_w, v):
    r = [0.0] * len(adj_w)
    for i, nb in enumerate(adj_w):
        for j, w in nb: r[i] += w * v[j]
    return r


def _dot(a, b): return sum(a[i] * b[i] for i in range(len(a)))
def _norm(v): return math.sqrt(_dot(v, v))
def _normalize(v): nm = _norm(v); return [x / nm for x in v] if nm > 1e-15 else v

def _deflate(v, found_phis):
    """Proiecteaza v orthogonal pe spatiul deja gasit."""
    for phi in found_phis:
        c = _dot(v, phi)
        v = [v[i] - c * phi[i] for i in range(len(v))]
    return v


def find_top_modes(adj_w, n_modes, n_iter, rng_obj):
    """Gaseste n_modes eigenvectori cu eigenvalue MARE via power iteration + deflatie."""
    modes = []  # (phi, lambda_K)
    for _ in range(n_modes):
        v = _normalize([rng_obj.gauss(0, 1) for _ in range(len(adj_w))])
        v = _normalize(_deflate(v, [m[0] for m in modes]))
        lam = 1.0
        for _ in range(n_iter):
            w = mat_vec(adj_w, v)
            w = _deflate(w, [m[0] for m in modes])
            nm = _norm(w)
            if nm < 1e-14: break
            lam = nm; v = [x / nm for x in w]
        Kv = mat_vec(adj_w, v)
        lam_K = _dot(v, Kv)
        if lam_K > 1e-6:
            modes.append((_normalize(v), lam_K))
    return modes


def find_bottom_modes(adj_w, shift, n_modes, n_iter, rng_obj, top_phis):
    """Gaseste n_modes eigenvectori cu eigenvalue MIC via shift-invert + deflatie."""
    all_found_phis = list(top_phis)
    modes = []  # (phi, lambda_K)
    for _ in range(n_modes):
        v = _normalize([rng_obj.gauss(0, 1) for _ in range(len(adj_w))])
        v = _normalize(_deflate(v, all_found_phis + [m[0] for m in modes]))
        lam = 1.0
        for _ in range(n_iter):
            Kv = mat_vec(adj_w, v)
            # A*v = shift*v - K*v  (A = shift*I - K)
            w = [shift * v[i] - Kv[i] for i in range(len(v))]
            w = _deflate(w, all_found_phis + [m[0] for m in modes])
            nm = _norm(w)
            if nm < 1e-14: break
            lam = nm; v = [x / nm for x in w]
        Kv = mat_vec(adj_w, v)
        lam_K = _dot(v, Kv)
        if 0 < lam_K < shift:
            modes.append((_normalize(v), lam_K))
    return modes


def compute_c_profile(adj_w, seed,
                      n_top=25, n_bottom=25,
                      n_iter=N_ITER_DEFAULT,
                      n_bfs_src=40,
                      m_sq=M_SQ_DEFAULT,
                      n_min=50):
    """Calculeaza C(r) cu propagator complet (constant + top + bottom cu deflatie).

    n_min: numarul minim de perechi pentru un bin r sa fie inclus in profil.
           Default=50 previne artefacte la r-uri rare (σ≈0 → weight→∞ in fit-uri ponderate).
    """
    n = len(adj_w)
    rng_obj = random.Random(seed + 88888)

    # Modul constant
    phi0 = [1.0 / math.sqrt(n)] * n
    modes = [(phi0, math.sqrt(m_sq))]

    # Estimeaza lambda_max pentru shift
    tmp_rng = random.Random(seed + 1)
    v_tmp = _normalize([tmp_rng.gauss(0, 1) for _ in range(n)])
    for _ in range(150):
        w = mat_vec(adj_w, v_tmp)
        nm = _norm(w)
        if nm < 1e-14: break
        v_tmp = [x / nm for x in w]
    Kv_tmp = mat_vec(adj_w, v_tmp)
    lam_max = abs(_dot(v_tmp, Kv_tmp))
    shift = lam_max * 1.1 + 0.5

    # Moduri TOP cu deflatie
    top_modes = find_top_modes(adj_w, n_top, n_iter, rng_obj)
    for phi, lam_K in top_modes:
        modes.append((phi, math.sqrt(max(lam_K, 0.0) + m_sq)))

    # Moduri BOTTOM cu deflatie
    top_phis = [m[0] for m in top_modes] + [phi0]
    bot_modes = find_bottom_modes(adj_w, shift, n_bottom, n_iter, rng_obj, top_phis)
    for phi, lam_K in bot_modes:
        modes.append((phi, math.sqrt(max(lam_K, 0.0) + m_sq)))

    # Profil C(r) via BFS
    srcs = rng_obj.sample(range(n), min(n_bfs_src, n))
    by_hop: dict[int, list[float]] = {}
    for src in srcs:
        dist = {src: 0}; q = deque([src])
        while q:
            u = q.popleft()
            for v_node, _ in adj_w[u]:
                if v_node not in dist:
                    dist[v_node] = dist[u] + 1; q.append(v_node)
        for node, d in dist.items():
            if d == 0: continue
            c_val = sum(phi[src] * phi[node] / (2.0 * om) for phi, om in modes)
            by_hop.setdefault(d, []).append(c_val)
    # Filtru robustete: exclude bin-uri cu prea putine perechi
    if n_min > 1:
        by_hop = {r: v for r, v in by_hop.items() if len(v) >= n_min}
    return by_hop


def fit_powerlaw(by_hop, min_pairs=50):
    rs, Cs = [], []
    for r in sorted(by_hop):
        vals = by_hop[r]
        if len(vals) >= min_pairs:
            m = sum(vals) / len(vals)
            if m > 0: rs.append(r); Cs.append(m)
    if len(rs) < 2: return float('nan'), 0.0
    lx = [math.log(r) for r in rs]; ly = [math.log(c) for c in Cs]
    n  = len(lx); mlx = sum(lx)/n; mly = sum(ly)/n
    sxy = sum((lx[i]-mlx)*(ly[i]-mly) for i in range(n))
    sxx = sum((lx[i]-mlx)**2 for i in range(n))
    if sxx == 0: return float('nan'), 0.0
    sl = sxy/sxx; ic = mly - sl*mlx
    lp = [ic + sl*lx[i] for i in range(n)]
    ss_res = sum((ly[i]-lp[i])**2 for i in range(n))
    ss_tot = sum((ly[i]-mly)**2 for i in range(n))
    return -sl, 1.0 - ss_res/max(ss_tot, 1e-30)
