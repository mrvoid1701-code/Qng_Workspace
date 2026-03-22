#!/usr/bin/env python3
"""
QNG ST-4 — Permutare etichete (test negativ)

Permutam etichetele nodurilor din graful QNG. Deoarece graful e izomorf
cu el insusi sub permutare, C(r) si gamma NU trebuie sa se schimbe.

Acesta valideaza ca masuram topologia grafului, nu artefacte de indexare.

Gates:
  ST4a — |gamma_perm_mean - gamma_orig| < 0.15  [invarianta]
  ST4b — std(gamma_perm) < 0.20                 [stabil sub permutare]
  ST4c — R2_perm_mean > 0.85
  ST4d — frac gamma_perm in [gamma_orig+-0.3] > 0.85
"""

from __future__ import annotations
import json, math, random, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _qng_propagator import build_jaccard, permute_graph, compute_c_profile, fit_powerlaw

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-st4-label-permutation-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_NODES = 280; K_INIT = 8; K_CONN = 8; QNG_SEED = 3401; N_PERMS = 25
N_TOP = 20; N_BOTTOM = 20; N_ITER = 200; N_BFS = 35

def main():
    t0 = datetime.utcnow()
    lines = []; pr = lambda s="": (lines.append(s), print(s))

    pr("="*65); pr("QNG ST-4 — Permutare etichete (test negativ)"); pr("="*65)
    pr(f"n={N_NODES}, QNG seed={QNG_SEED}, N_PERMS={N_PERMS}\n")

    adj_orig = build_jaccard(N_NODES, K_INIT, K_CONN, QNG_SEED)
    bh_orig  = compute_c_profile(adj_orig, QNG_SEED, N_TOP, N_BOTTOM, N_ITER, N_BFS)
    g_orig, R2_orig = fit_powerlaw(bh_orig)
    pr(f"[Original] gamma={g_orig:.4f}  R2={R2_orig:.4f}\n")

    rng_perm = random.Random(9999)
    gammas_p = []; R2s_p = []
    pr(f"{'perm':>5}  {'gamma':>8}  {'R2':>8}  {'delta':>8}")
    pr("-"*36)
    for p_idx in range(N_PERMS):
        perm = list(range(N_NODES)); rng_perm.shuffle(perm)
        adj_p = permute_graph(adj_orig, perm)
        bh_p  = compute_c_profile(adj_p, QNG_SEED + p_idx, N_TOP, N_BOTTOM, N_ITER, N_BFS)
        g_p, R2_p = fit_powerlaw(bh_p)
        if not math.isnan(g_p):
            gammas_p.append(g_p); R2s_p.append(R2_p)
        delta = abs(g_p - g_orig) if not math.isnan(g_p) else float('nan')
        pr(f"{p_idx+1:>5}  {g_p:>8.4f}  {R2_p:>8.4f}  {delta:>8.4f}")

    gm_p  = sum(gammas_p)/len(gammas_p) if gammas_p else float('nan')
    gs_p  = math.sqrt(sum((g-gm_p)**2 for g in gammas_p)/max(len(gammas_p)-1,1)) if len(gammas_p)>1 else float('nan')
    rm_p  = sum(R2s_p)/len(R2s_p) if R2s_p else float('nan')
    delta_mean = abs(gm_p - g_orig) if not math.isnan(gm_p) else float('nan')
    frac_ok = sum(1 for g in gammas_p if abs(g-g_orig)<0.3)/max(len(gammas_p),1)

    pr(f"\n[Statistici permutari N={len(gammas_p)}]")
    pr(f"  gamma_mean={gm_p:.4f}  std={gs_p:.4f}  R2_mean={rm_p:.4f}")
    pr(f"  |mean-orig|={delta_mean:.4f}  frac_within_0.3={frac_ok*100:.1f}%")
    pr(f"  Interpretare: daca |mean-orig|~0 => topologie e invarianta la relabeling")

    ST4a = bool(not math.isnan(delta_mean) and delta_mean < 0.15)
    ST4b = bool(not math.isnan(gs_p) and gs_p < 0.20)
    ST4c = bool(not math.isnan(rm_p) and rm_p > 0.85)
    ST4d = bool(frac_ok > 0.85)

    pr(f"\n{'='*65}"); pr("GATE RESULTS"); pr(f"{'='*65}")
    pr(f"ST4a  |gamma_perm - gamma_orig| < 0.15: {'PASS' if ST4a else 'FAIL'}  ({delta_mean:.4f})")
    pr(f"ST4b  std(gamma_perm) < 0.20:           {'PASS' if ST4b else 'FAIL'}  ({gs_p:.4f})")
    pr(f"ST4c  R2_mean > 0.85:                   {'PASS' if ST4c else 'FAIL'}  ({rm_p:.4f})")
    pr(f"ST4d  frac within 0.3 > 85%:            {'PASS' if ST4d else 'FAIL'}  ({frac_ok*100:.1f}%)")
    n_pass = sum([ST4a,ST4b,ST4c,ST4d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    t1 = datetime.utcnow()
    summary = {
        "original": {"gamma": float(g_orig), "R2": float(R2_orig)},
        "permuted": {"gamma_mean": float(gm_p),"gamma_std": float(gs_p),
                     "R2_mean": float(rm_p),"n_valid": len(gammas_p),
                     "delta_vs_original": float(delta_mean),"frac_within_03": float(frac_ok)},
        "gammas_permuted": [float(g) for g in gammas_p],
        "gates": {
            "ST4a": {"passed": ST4a,"value": float(delta_mean)},
            "ST4b": {"passed": ST4b,"value": float(gs_p)},
            "ST4c": {"passed": ST4c,"value": float(rm_p)},
            "ST4d": {"passed": ST4d,"value": float(frac_ok)},
        },
        "summary": {"n_pass": n_pass,"n_total": 4,"all_pass": n_pass==4,
                    "timestamp": t0.isoformat()+"Z","runtime_s": (t1-t0).total_seconds()},
    }
    (OUT_DIR/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT_DIR/"run.log").write_text("\n".join(lines))
    pr(f"\nArtifacte: {OUT_DIR}")
    return 0 if n_pass==4 else 1

if __name__ == "__main__":
    sys.exit(main())
