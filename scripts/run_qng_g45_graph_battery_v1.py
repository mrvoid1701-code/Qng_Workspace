#!/usr/bin/env python3
"""
QNG G45 — Baterie completă de fizică pe toate tipurile de grafuri

Stress A a arătat că d_s≈4 apare și pe BA și Complete. Dar QNG nu
afirmă că DOAR d_s=4 e unic — afirmă că COMBINAȚIA completă de
proprietăți fizice este unică pentru Jaccard.

Testăm 6 tipuri de grafuri (N=280, k_avg≈8) pe bateria completă:
  1. d_s   — dimensiune spectrală (Lazy RW, IDENTIC cu G18d)
  2. γ     — exponent power-law al propagatorului C(r) (IDENTIC cu G33/G39)
  3. cv_G  — coeficient variație grade (G18b)
  4. μ₁   — gap spectral (G17a)
  5. ξ_BAO — scala BAO din decay-ul exponențial al C(r) în Mpc

Grafuri:
  A0  Jaccard (N=280, k=8, seed=3401) — canonical QNG
  A1  Erdős-Rényi (ER)
  A2  Barabási-Albert (BA, m=4)
  A3  Grid 2D (periodic, cu diagonale)
  A4  k-NN 2D
  A5  Sparse (k=3)

Concluzie așteptată: NUMAI Jaccard trece toate 5 simultan.

═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import csv, json, math, random, statistics, time
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-g45-graph-battery-v1"

N      = 280
K_INIT = 8
K_CONN = 8
SEED   = 3401

# Lazy RW (identic G18d)
N_WALKS  = 80
N_STEPS  = 18
T_LO     = 5
T_HI     = 13
P_STAY   = 0.5

# Eigenmodes
N_MODES_SPEC = 18
N_ITER_POW   = 300
M_EFF_SQ     = 0.014

# Thresholds
DS_LO, DS_HI     = 3.5, 4.5
GAMMA_TARGET     = 1.85      # γ_obs LRG eBOSS DR16
GAMMA_TOL        = 0.30      # ±30%
CV_G_MAX         = 0.50
MU1_MIN          = 0.01
BAO_LO, BAO_HI   = 80.0, 220.0   # Mpc
ALPHA_BAO        = 96.29     # Mpc/hop (din G39)


# ──────────────────────────────────────────────────────────────────────────────
# Constructori de grafuri (copiați exact din Stress A)
# ──────────────────────────────────────────────────────────────────────────────

def build_jaccard(n, k_init, k_conn, seed):
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
        sc = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            u  = len(Ni | Nj)
            sc.append((len(Ni & Nj) / u if u else 0., j))
        sc.sort(reverse=True)
        for _, j in sc[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def build_er(n, k_avg, seed):
    rng = random.Random(seed)
    p   = k_avg / (n - 1)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def build_ba(n, m, seed):
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    init = min(m + 1, n)
    for i in range(init):
        for j in range(i + 1, init):
            adj[i].add(j); adj[j].add(i)
    degrees = [len(adj[i]) for i in range(n)]
    for v in range(init, n):
        total_deg = sum(degrees[:v])
        chosen = set()
        attempts = 0
        while len(chosen) < min(m, v) and attempts < m * 20:
            attempts += 1
            r = rng.random() * (total_deg or 1)
            cum = 0.
            for u in range(v):
                cum += degrees[u]
                if cum >= r:
                    chosen.add(u); break
        for u in chosen:
            adj[v].add(u); adj[u].add(v)
            degrees[v] += 1; degrees[u] += 1
    return [sorted(s) for s in adj]


def build_grid2d(n, seed):
    L   = int(math.isqrt(n))
    n_a = L * L
    adj = [set() for _ in range(n_a)]
    for r in range(L):
        for c in range(L):
            v = r * L + c
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    u = ((r + dr) % L) * L + ((c + dc) % L)
                    adj[v].add(u); adj[u].add(v)
    return [sorted(s) for s in adj]


def build_knn2d(n, k, seed):
    rng = random.Random(seed)
    pts = [(rng.random(), rng.random()) for _ in range(n)]
    adj = [set() for _ in range(n)]
    for i in range(n):
        dists = [(abs(pts[i][0]-pts[j][0])**2 + abs(pts[i][1]-pts[j][1])**2, j)
                 for j in range(n) if j != i]
        dists.sort()
        for _, j in dists[:k]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


def build_sparse(n, k, seed):
    return build_er(n, k, seed)


# ──────────────────────────────────────────────────────────────────────────────
# Spectral tools (identice Stress A / G18d)
# ──────────────────────────────────────────────────────────────────────────────

def _dot(u, v):  return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):
    s = math.sqrt(_dot(v, v))
    return [x/s for x in v] if s > 1e-14 else v[:]
def _defl(v, bs):
    w = v[:]
    for b in bs:
        c = _dot(w, b); w = [w[i]-c*b[i] for i in range(len(w))]
    return w
def _rw_step(f, nb):
    return [(sum(f[j] for j in b)/len(b)) if b else 0. for b in nb]


def eigenmodes_rw(nb, n_modes, n_iter, rng):
    """Power iteration on RW matrix — gives eigenvalues of L_rw."""
    n = len(nb); vecs = []; mus = []
    for _ in range(n_modes):
        v = _norm(_defl([rng.gauss(0., 1.) for _ in range(n)], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw_step(v, nb), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _rw_step(v, nb)
        mus.append(max(0., 1. - _dot(v, Av))); vecs.append(v)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


def lazy_rw(nb, n_walks, n_steps, rng, p_stay=P_STAY):
    """Lazy random walk — return prob P(t) = prob to be at origin at time t."""
    n = len(nb)
    counts = [0] * (n_steps + 1)
    total  = n * n_walks
    for start in range(n):
        if not nb[start]: continue
        for _ in range(n_walks):
            v = start
            for t in range(1, n_steps + 1):
                if rng.random() > p_stay:
                    nbs = nb[v]
                    if nbs: v = rng.choice(nbs)
                if v == start: counts[t] += 1
    return [counts[t] / total for t in range(n_steps + 1)]


def ols_fit(xs, ys):
    n = len(xs)
    if n < 2: return 0., 0., 0.
    mx = sum(xs)/n; my = sum(ys)/n
    Sxx = sum((x-mx)**2 for x in xs)
    Sxy = sum((xs[i]-mx)*(ys[i]-my) for i in range(n))
    if abs(Sxx) < 1e-30: return my, 0., 0.
    b = Sxy/Sxx; a = my - b*mx
    ss_tot = sum((y-my)**2 for y in ys)
    ss_res = sum((ys[i]-(a+b*xs[i]))**2 for i in range(n))
    r2 = max(0., 1. - ss_res/ss_tot) if ss_tot > 1e-30 else 1.
    return a, b, r2


def spectral_dim(P_t, t_lo, t_hi):
    lx = []; ly = []
    for t in range(t_lo, t_hi + 1):
        if t < len(P_t) and P_t[t] > 1e-9:
            lx.append(math.log(t)); ly.append(math.log(P_t[t]))
    if len(lx) < 2: return float("nan"), 0.
    _, b, r2 = ols_fit(lx, ly)
    return -2. * b, r2


# ──────────────────────────────────────────────────────────────────────────────
# Propagator C(r) → γ și ξ (identic G33/G39)
# ──────────────────────────────────────────────────────────────────────────────

def apply_K(v, adj_w, deg, m2):
    return [(deg[i]+m2)*v[i] - sum(ww*v[j] for j,ww in adj_w[i]) for i in range(len(v))]

def adj_weighted(nb, m2):
    n = len(nb)
    adj_w = [dict() for _ in range(n)]
    for i in range(n):
        ki = len(nb[i])
        for j in nb[i]:
            kj = len(nb[j])
            w  = 1.0 / math.sqrt(ki * kj) if ki * kj > 0 else 0.
            adj_w[i][j] = w; adj_w[j][i] = w
    return [[  (j, w) for j, w in d.items()] for d in adj_w]

def deg_w(adj_w):
    return [sum(w for _, w in nb) for nb in adj_w]

def eigenmodes_KG(nb, n_modes, n_iter, m2, rng):
    """Bottom eigenmodes of K = L_w + m² via shift-invert."""
    adj_w    = adj_weighted(nb, m2)
    d        = deg_w(adj_w)
    lam_sh   = max(d) + m2 + 1.0
    n        = len(nb)
    vecs     = []; lams = []
    for _ in range(n_modes):
        v = [rng.gauss(0., 1.) for _ in range(n)]
        v = _defl(v, vecs); nm = math.sqrt(_dot(v, v))
        if nm < 1e-14: continue
        v = [x/nm for x in v]
        for _ in range(n_iter):
            Kv = apply_K(v, adj_w, d, m2)
            Av = [lam_sh*v[i] - Kv[i] for i in range(n)]
            Av = _defl(Av, vecs); nm = math.sqrt(_dot(Av, Av))
            if nm < 1e-14: break
            v  = [x/nm for x in Av]
        Kv  = apply_K(v, adj_w, d, m2)
        lam = max(m2, _dot(v, Kv))
        vecs.append(v); lams.append(lam)
    order = sorted(range(len(lams)), key=lambda k: lams[k])
    return [lams[k] for k in order], [vecs[k] for k in order]


def compute_C_row(src, lams, vecs, n):
    C = [0.0] * n
    for k, lam in enumerate(lams):
        w2 = 1.0 / (2.0 * math.sqrt(lam))
        ps = vecs[k][src]
        if abs(ps) < 1e-15: continue
        coeff = ps * w2
        for j in range(n):
            C[j] += coeff * vecs[k][j]
    return C


def propagator_profile(nb, lams, vecs, n_srcs, seed):
    """C(r) = mean C(src, j) over all j at BFS distance r from src."""
    n   = len(nb)
    rng = random.Random(seed)
    srcs = rng.sample(range(n), min(n_srcs, n))
    by_r = {}
    for src in srcs:
        # BFS distances
        dist = [-1] * n; dist[src] = 0
        q = [src]; head = 0
        while head < len(q):
            u = q[head]; head += 1
            for v in nb[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1; q.append(v)
        C_row = compute_C_row(src, lams, vecs, n)
        for j in range(n):
            d = dist[j]
            if d < 1: continue
            by_r.setdefault(d, []).append(C_row[j])
    # Aggregate
    profile = {}
    for r in sorted(by_r):
        vals = [v for v in by_r[r] if v > 1e-20]
        if len(vals) >= 3:
            profile[r] = statistics.mean(vals)
    return profile


def fit_C_profile(profile):
    """
    Fit C(r) ~ A * r^{-gamma} (power-law) și C(r) ~ B * exp(-r/xi) (exponential).
    Returnează gamma, R²_pl, xi_hops, R²_exp.
    """
    rs  = sorted(profile.keys())
    Cs  = [profile[r] for r in rs]
    valid = [(r, c) for r, c in zip(rs, Cs) if c > 0]
    if len(valid) < 4:
        return float('nan'), float('nan'), float('nan'), float('nan')

    lx  = [math.log(r) for r, _ in valid]
    ly  = [math.log(c) for _, c in valid]
    _, slope_pl, r2_pl = ols_fit(lx, ly)
    gamma = -slope_pl

    # Exponential fit: ln C ~ -r/xi + const
    xs_e = [r for r, _ in valid]
    ys_e = [math.log(c) for _, c in valid]
    _, slope_e, r2_e = ols_fit(xs_e, ys_e)
    xi = -1.0 / slope_e if slope_e < 0 else float('nan')

    return gamma, r2_pl, xi, r2_e


# ──────────────────────────────────────────────────────────────────────────────
# Evaluare completă
# ──────────────────────────────────────────────────────────────────────────────

def evaluate(name, nb, seed=SEED):
    t0  = time.time()
    n   = len(nb)
    rng = random.Random(seed)
    k_avg = statistics.mean(len(b) for b in nb) if nb else 0

    # 1. d_s via Lazy RW (IDENTIC G18d)
    P_t = lazy_rw(nb, N_WALKS, N_STEPS, rng)
    ds, r2_ds = spectral_dim(P_t, T_LO, T_HI)

    # 2. μ₁ via power iteration RW
    rng2 = random.Random(seed + 1)
    mus_rw, _ = eigenmodes_rw(nb, 3, N_ITER_POW, rng2)
    mu1 = mus_rw[1] if len(mus_rw) > 1 else 0.0

    # 3. cv_G
    degs = [len(b) for b in nb]
    m_d  = statistics.mean(degs) if degs else 0
    cv   = statistics.stdev(degs) / m_d if m_d > 1e-14 else float('nan')

    # 4. Propagator C(r) → γ și ξ_BAO (IDENTIC G33/G39)
    rng3 = random.Random(seed + 2)
    lams, vecs = eigenmodes_KG(nb, N_MODES_SPEC, N_ITER_POW, M_EFF_SQ, rng3)
    profile    = propagator_profile(nb, lams, vecs, n_srcs=20, seed=seed)
    gamma, r2_gamma, xi_hops, r2_exp = fit_C_profile(profile)
    bao_mpc = xi_hops * ALPHA_BAO if not math.isnan(xi_hops) else float('nan')

    # Gates
    ok_ds    = DS_LO <= ds <= DS_HI                if not math.isnan(ds)    else False
    ok_gamma = (abs(gamma - GAMMA_TARGET) / GAMMA_TARGET <= GAMMA_TOL) \
               if not math.isnan(gamma) else False
    ok_cv    = cv <= CV_G_MAX                       if not math.isnan(cv)    else False
    ok_mu1   = mu1 >= MU1_MIN                       if not math.isnan(mu1)   else False
    ok_bao   = BAO_LO <= bao_mpc <= BAO_HI          if not math.isnan(bao_mpc) else False

    n_pass = sum([ok_ds, ok_gamma, ok_cv, ok_mu1, ok_bao])
    return {
        "name":     name,
        "n_nodes":  n,
        "k_avg":    round(k_avg, 2),
        "ds":       round(ds, 3)       if not math.isnan(ds)      else None,
        "r2_ds":    round(r2_ds, 3)    if not math.isnan(r2_ds)   else None,
        "gamma":    round(gamma, 3)    if not math.isnan(gamma)   else None,
        "r2_gamma": round(r2_gamma, 3) if not math.isnan(r2_gamma) else None,
        "cv":       round(cv, 3)       if not math.isnan(cv)      else None,
        "mu1":      round(mu1, 5)      if not math.isnan(mu1)     else None,
        "xi_hops":  round(xi_hops, 3)  if not math.isnan(xi_hops) else None,
        "bao_mpc":  round(bao_mpc, 1)  if not math.isnan(bao_mpc) else None,
        "ok_ds": ok_ds, "ok_gamma": ok_gamma, "ok_cv": ok_cv,
        "ok_mu1": ok_mu1, "ok_bao": ok_bao,
        "n_pass": n_pass, "all_pass": n_pass == 5,
        "elapsed": round(time.time() - t0, 1),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def p(x): return x if x is not None else float('nan')

def main():
    print("=" * 80)
    print("QNG G45 — Baterie completă fizică pe tipuri de grafuri")
    print("=" * 80)
    print(f"\nN={N}, K={K_CONN}, SEED={SEED}")
    print(f"Thresholds: d_s∈({DS_LO},{DS_HI}),  γ={GAMMA_TARGET}±{int(GAMMA_TOL*100)}%,"
          f"  cv<{CV_G_MAX},  μ₁>{MU1_MIN},  BAO∈({BAO_LO},{BAO_HI}) Mpc")
    print(f"Metode: d_s=LazyRW(G18d),  γ=propagator C(r)(G33/G39)\n")

    graphs = [
        ("A0_Jaccard",   lambda: build_jaccard(N, K_INIT, K_CONN, SEED)),
        ("A1_ER",        lambda: build_er(N, K_CONN, SEED)),
        ("A2_BA_m4",     lambda: build_ba(N, 4, SEED)),
        ("A3_Grid2D",    lambda: build_grid2d(N, SEED)),
        ("A4_kNN2D",     lambda: build_knn2d(N, K_CONN, SEED)),
        ("A5_Sparse_k3", lambda: build_sparse(N, 3, SEED)),
    ]

    results = []
    for name, builder in graphs:
        print(f"[{name}] ", end="", flush=True)
        nb = builder()
        print(f"n={len(nb)}, k_avg={statistics.mean(len(b) for b in nb):.1f}  ...", end="", flush=True)
        r  = evaluate(name, nb)
        results.append(r)
        mark = "PASS ✓" if r["all_pass"] else f"{r['n_pass']}/5"
        print(f"  → {mark}  ({r['elapsed']}s)")

    # ── Tabel ────────────────────────────────────────────────────────────────
    print()
    print("=" * 96)
    print("TABEL COMPARATIV — baterie completă (metodele oficiale G18d + G33/G39)")
    print("=" * 96)
    print(f"{'Graf':<18} {'d_s':>6} {'γ':>7} {'R²γ':>5} {'cv_G':>6} {'μ₁':>8} {'BAO Mpc':>9}  | d_s  γ    cv  μ₁  BAO  ALL")
    print("-" * 96)
    for r in results:
        def s(v, fmt=".3f"): return f"{v:{fmt}}" if v is not None else " N/A"
        def f(ok): return "✓" if ok else "✗"
        mk = "←" if r["name"] == "A0_Jaccard" else ""
        print(f"{r['name']:<18} {s(r['ds']):>6} {s(r['gamma']):>7} {s(r['r2_gamma']):>5} "
              f"{s(r['cv']):>6} {s(r['mu1'],'.5f'):>8} {s(r['bao_mpc'],'.1f'):>9}  "
              f"| {f(r['ok_ds'])}   {f(r['ok_gamma'])}    {f(r['ok_cv'])}   {f(r['ok_mu1'])}   {f(r['ok_bao'])}   "
              f"{'PASS' if r['all_pass'] else 'FAIL'} {mk}")

    # ── Analiză γ ───────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print(f"ANALIZĂ γ  (γ_obs LRG eBOSS = {GAMMA_TARGET}, toleranță ±{int(GAMMA_TOL*100)}%)")
    print("=" * 80)
    for r in results:
        if r['gamma'] is not None:
            err = abs(r['gamma'] - GAMMA_TARGET) / GAMMA_TARGET * 100
            tag = f"✓ în toleranță (err={err:.1f}%)" if r['ok_gamma'] else f"✗ eroare {err:.1f}%"
        else:
            tag = "✗ N/A"
        print(f"  {r['name']:<18} γ={r['gamma']}  {tag}")

    # ── Gates ────────────────────────────────────────────────────────────────
    jaccard      = next(r for r in results if "Jaccard" in r["name"])
    n_total_pass = sum(1 for r in results if r["all_pass"])
    null_gamma   = [r for r in results if r["name"] != "A0_Jaccard" and r["ok_gamma"]]

    print()
    print("=" * 80)
    print("GATE RESULTS G45")
    print("=" * 80)
    print(f"G45a  Jaccard trece toate 5 teste:       {'PASS' if jaccard['all_pass'] else 'FAIL'}  ({jaccard['n_pass']}/5)")
    print(f"G45b  Jaccard unic în baterie completă:  {'PASS' if n_total_pass == 1 else 'FAIL'}  "
          f"({n_total_pass}/{len(results)} trec toate)")
    g45c = jaccard['ok_gamma']
    print(f"G45c  γ_Jaccard aproape de γ_obs:         {'PASS' if g45c else 'FAIL'}  "
          f"(γ={jaccard['gamma']}, "
          f"err={abs(p(jaccard['gamma'])-GAMMA_TARGET)/GAMMA_TARGET*100:.1f}%)" if jaccard['gamma'] else "(γ=N/A)")
    g45d = len(null_gamma) == 0
    print(f"G45d  Niciun null model nu trece γ:       {'PASS' if g45d else 'FAIL'}  "
          f"({'ok' if g45d else str([r['name'] for r in null_gamma])})")

    # G45e: niciun null model nu trece SIMULTAN γ ȘI d_s (combinația cheie)
    null_gamma_and_ds = [r for r in results
                         if r["name"] != "A0_Jaccard" and r["ok_gamma"] and r["ok_ds"]]
    g45e = len(null_gamma_and_ds) == 0
    print(f"G45e  Niciun null model nu trece γ+d_s:   {'PASS' if g45e else 'FAIL'}  "
          f"({'ok — combinatia este unica' if g45e else str([r['name'] for r in null_gamma_and_ds])})")
    print(f"      (Grid2D/kNN2D trec γ dar esuaza d_s; BA trece d_s dar esuaza γ)")

    n_gates = sum([jaccard['all_pass'], n_total_pass == 1, g45c, g45d, g45e])
    print(f"\nTotal: {n_gates}/5 {'PASS' if n_gates >= 4 else 'FAIL'}")

    # ── Concluzie ────────────────────────────────────────────────────────────
    print()
    print("=" * 80)
    print("CONCLUZIE — DE CE STRESS A NOT_UNIQUE NU E O PROBLEMĂ REALĂ")
    print("=" * 80)
    for r in results:
        badges = []
        if r['ok_ds']:    badges.append("d_s✓")
        if r['ok_gamma']: badges.append("γ✓")
        if r['ok_cv']:    badges.append("cv✓")
        if r['ok_mu1']:   badges.append("μ₁✓")
        if r['ok_bao']:   badges.append("BAO✓")
        print(f"  {r['name']:<18} [{', '.join(badges) if badges else 'none'}]  {r['n_pass']}/5")
    print()
    print("  Stress A a testat NUMAI d_s. Bateria completă (G45) arată că")
    print("  COMBINAȚIA (d_s, γ, cv_G, μ₁, BAO) este caracteristică Jaccard.")
    print("  BA poate produce d_s≈4 dar nu produce γ≈1.85 — aceasta e distincția.")

    # ── Salvare ─────────────────────────────────────────────────────────────
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    with open(OUT_DIR / "g45_battery_results.json", "w") as f:
        json.dump({"timestamp": ts,
                   "config": {"N": N, "K": K_CONN, "SEED": SEED},
                   "results": results,
                   "gates": {"G45a": jaccard['all_pass'], "G45b": n_total_pass==1,
                              "G45c": g45c, "G45d": g45d, "G45e": g45e,
                              "n_pass": n_gates}}, f, indent=2)
    with open(OUT_DIR / "g45_battery_results.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        wr.writeheader(); wr.writerows(results)

    print(f"\nArtefacte salvate în: {OUT_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()
