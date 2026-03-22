#!/usr/bin/env python3
"""
QNG ST-1 — Stabilitate la seed (N=50 seminte)

Verifica ca gamma(C(r)) e stabil indiferent de seed-ul ales.
Daca gamma variaza mult => cherry-picking. Daca e stabil => robustete.

Gates:
  ST1a — std(gamma) < 0.25         [stable]
  ST1b — fractie gamma in [0.5,2.5] > 0.90
  ST1c — |media - gamma(seed_ref)| < 0.30
  ST1d — R2_mean > 0.85
"""

from __future__ import annotations
import json, math, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _qng_propagator import build_jaccard, compute_c_profile, fit_powerlaw

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-st1-seed-stability-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_NODES = 280; K_INIT = 8; K_CONN = 8; REF_SEED = 3401; N_SEEDS = 50
N_TOP = 20; N_BOTTOM = 20; N_ITER = 200; N_BFS = 35

def main():
    t0 = datetime.utcnow()
    lines = []; pr = lambda s="": (lines.append(s), print(s))

    pr("="*65); pr("QNG ST-1 — Stabilitate la seed (N=50)"); pr("="*65)
    pr(f"n={N_NODES}, k={K_INIT}/{K_CONN}, n_top={N_TOP}, n_bottom={N_BOTTOM}\n")

    # Gamma de referinta (seed=3401)
    adj_ref  = build_jaccard(N_NODES, K_INIT, K_CONN, REF_SEED)
    bh_ref   = compute_c_profile(adj_ref, REF_SEED, N_TOP, N_BOTTOM, N_ITER, N_BFS)
    g_ref, _ = fit_powerlaw(bh_ref)
    pr(f"Gamma referinta (seed={REF_SEED}): {g_ref:.4f}\n")

    seeds = list(range(1, N_SEEDS+1))
    results = []
    pr(f"{'seed':>6}  {'gamma':>8}  {'R2':>8}")
    pr("-"*28)
    for seed in seeds:
        adj   = build_jaccard(N_NODES, K_INIT, K_CONN, seed)
        bh    = compute_c_profile(adj, seed, N_TOP, N_BOTTOM, N_ITER, N_BFS)
        g, R2 = fit_powerlaw(bh)
        results.append({"seed": seed, "gamma": g, "R2": R2})
        g_s = f"{g:.4f}" if not math.isnan(g) else "  nan  "
        pr(f"{seed:>6}  {g_s:>8}  {R2:>8.4f}")

    valid  = [r for r in results if not math.isnan(r["gamma"])]
    gammas = [r["gamma"] for r in valid]
    R2s    = [r["R2"] for r in valid]
    gm  = sum(gammas)/len(gammas)
    gs  = math.sqrt(sum((g-gm)**2 for g in gammas)/max(len(gammas)-1,1))
    rm  = sum(R2s)/len(R2s)
    frac= sum(1 for g in gammas if 0.5<=g<=2.5)/max(len(gammas),1)
    dref= abs(gm - g_ref)

    pr(f"\n[Statistici N={len(valid)}]")
    pr(f"  media={gm:.4f}  std={gs:.4f}  min={min(gammas):.4f}  max={max(gammas):.4f}")
    pr(f"  R2_mean={rm:.4f}  frac_ok={frac*100:.1f}%  |media-ref|={dref:.4f}")

    ST1a = bool(gs < 0.25)
    ST1b = bool(frac > 0.90)
    ST1c = bool(dref < 0.30)
    ST1d = bool(rm > 0.85)

    pr(f"\n{'='*65}"); pr("GATE RESULTS"); pr(f"{'='*65}")
    pr(f"ST1a  std(gamma) < 0.25:          {'PASS' if ST1a else 'FAIL'}  ({gs:.4f})")
    pr(f"ST1b  frac in [0.5,2.5] > 90%:   {'PASS' if ST1b else 'FAIL'}  ({frac*100:.1f}%)")
    pr(f"ST1c  |media-ref| < 0.30:         {'PASS' if ST1c else 'FAIL'}  ({dref:.4f})")
    pr(f"ST1d  R2_mean > 0.85:             {'PASS' if ST1d else 'FAIL'}  ({rm:.4f})")
    n_pass = sum([ST1a,ST1b,ST1c,ST1d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    t1 = datetime.utcnow()
    summary = {
        "params": {"n_nodes": N_NODES,"k_init": K_INIT,"k_conn": K_CONN,"n_seeds": N_SEEDS},
        "ref": {"seed": REF_SEED, "gamma": float(g_ref)},
        "stats": {"gamma_mean": float(gm),"gamma_std": float(gs),"R2_mean": float(rm),
                  "frac_in_range": float(frac),"delta_vs_ref": float(dref)},
        "gammas": [float(r["gamma"]) for r in results],
        "gates": {
            "ST1a": {"passed": ST1a,"value": float(gs)},
            "ST1b": {"passed": ST1b,"value": float(frac)},
            "ST1c": {"passed": ST1c,"value": float(dref)},
            "ST1d": {"passed": ST1d,"value": float(rm)},
        },
        "summary": {"n_pass": n_pass,"n_total": 4,"all_pass": n_pass==4,
                    "timestamp": t0.isoformat()+"Z","runtime_s": (t1-t0).total_seconds()},
    }
    (OUT_DIR/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT_DIR/"run.log").write_text("\n".join(lines))
    csv = ["seed,gamma,R2"] + [f"{r['seed']},{r['gamma']:.6f},{r['R2']:.6f}" for r in results]
    (OUT_DIR/"seed_sweep.csv").write_text("\n".join(csv))
    pr(f"\nArtifacte: {OUT_DIR}")
    return 0 if n_pass==4 else 1

if __name__ == "__main__":
    sys.exit(main())
