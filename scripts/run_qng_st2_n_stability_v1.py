#!/usr/bin/env python3
"""
QNG ST-2 — Stabilitate la n (marimea grafului)

n = 80, 120, 160, 200, 280, 400, 560 — 6 seminte per n.
Verifica convergenta gamma cu n mare.

Gates:
  ST2a — gamma(n=280) in [0.5, 2.5]
  ST2b — std(gamma_means peste n) < 0.40
  ST2c — |gamma(n=560) - gamma(n=280)| < 0.40  [convergenta]
  ST2d — trend: gamma(n=560) in [0.3, 2.8]
"""

from __future__ import annotations
import json, math, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _qng_propagator import build_jaccard, compute_c_profile, fit_powerlaw

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-st2-n-stability-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

K_INIT=8; K_CONN=8; N_SIZES=[80,120,160,200,280,400,560]; N_SEEDS=6
N_TOP=12; N_BOTTOM=12; N_ITER=100; N_BFS=20

def main():
    t0=datetime.utcnow()
    lines=[]; pr=lambda s="": (lines.append(s),print(s))
    pr("="*65); pr("QNG ST-2 — Stabilitate la n"); pr("="*65)
    pr(f"n testate: {N_SIZES}, seeds/n={N_SEEDS}\n")

    seeds=list(range(101,101+N_SEEDS))
    rows=[]; gamma_means=[]

    pr(f"{'n':>6}  {'gamma_mean':>11}  {'gamma_std':>10}  {'R2_mean':>8}  {'n_valid':>8}")
    pr("-"*52)
    for n in N_SIZES:
        gammas,R2s=[],[]
        for seed in seeds:
            adj   = build_jaccard(n,K_INIT,K_CONN,seed)
            bh    = compute_c_profile(adj,seed,N_TOP,N_BOTTOM,N_ITER,min(N_BFS,n-1))
            g,R2  = fit_powerlaw(bh, min_pairs=max(8, n//20))
            if not math.isnan(g): gammas.append(g); R2s.append(R2)
        if gammas:
            gm=sum(gammas)/len(gammas)
            gs=math.sqrt(sum((g-gm)**2 for g in gammas)/max(len(gammas)-1,1))
            rm=sum(R2s)/len(R2s)
        else:
            gm=gs=rm=float('nan')
        rows.append({"n":n,"gamma_mean":float(gm),"gamma_std":float(gs),"R2_mean":float(rm),"n_valid":len(gammas)})
        gamma_means.append(gm)
        pr(f"{n:>6}  {gm:>11.4f}  {gs:>10.4f}  {rm:>8.4f}  {len(gammas):>8}")

    valid_means=[g for g in gamma_means if not math.isnan(g)]
    mean_of_means=sum(valid_means)/len(valid_means)
    std_k=math.sqrt(sum((g-mean_of_means)**2 for g in valid_means)/max(len(valid_means)-1,1))
    gm_280=next((r["gamma_mean"] for r in rows if r["n"]==280), float('nan'))
    gm_560=next((r["gamma_mean"] for r in rows if r["n"]==560), float('nan'))
    delta_conv=abs(gm_560-gm_280) if not(math.isnan(gm_280) or math.isnan(gm_560)) else float('nan')

    pr(f"\n[Convergenta]")
    pr(f"  std(gamma_means) = {std_k:.4f}")
    pr(f"  gamma(280)={gm_280:.4f}  gamma(560)={gm_560:.4f}  delta={delta_conv:.4f}")

    ST2a=bool(not math.isnan(gm_280) and 0.5<=gm_280<=2.5)
    ST2b=bool(not math.isnan(std_k) and std_k<0.40)
    ST2c=bool(not math.isnan(delta_conv) and delta_conv<0.40)
    ST2d=bool(not math.isnan(gm_560) and 0.3<=gm_560<=2.8)

    pr(f"\n{'='*65}"); pr("GATE RESULTS"); pr(f"{'='*65}")
    pr(f"ST2a  gamma(280) in [0.5,2.5]:       {'PASS' if ST2a else 'FAIL'}  ({gm_280:.4f})")
    pr(f"ST2b  std(means) < 0.40:             {'PASS' if ST2b else 'FAIL'}  ({std_k:.4f})")
    pr(f"ST2c  |gamma(560)-gamma(280)| < 0.40: {'PASS' if ST2c else 'FAIL'}  ({delta_conv:.4f})")
    pr(f"ST2d  gamma(560) in [0.3,2.8]:       {'PASS' if ST2d else 'FAIL'}  ({gm_560:.4f})")
    n_pass=sum([ST2a,ST2b,ST2c,ST2d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    t1=datetime.utcnow()
    summary={
        "params":{"k_init":K_INIT,"k_conn":K_CONN,"n_sizes":N_SIZES,"n_seeds":N_SEEDS},
        "rows":rows,
        "convergence":{"std_means":float(std_k),"delta_560_280":float(delta_conv),
                       "gamma_280":float(gm_280),"gamma_560":float(gm_560)},
        "gates":{
            "ST2a":{"passed":ST2a,"value":float(gm_280)},
            "ST2b":{"passed":ST2b,"value":float(std_k)},
            "ST2c":{"passed":ST2c,"value":float(delta_conv)},
            "ST2d":{"passed":ST2d,"value":float(gm_560)},
        },
        "summary":{"n_pass":n_pass,"n_total":4,"all_pass":n_pass==4,
                   "timestamp":t0.isoformat()+"Z","runtime_s":(t1-t0).total_seconds()},
    }
    (OUT_DIR/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT_DIR/"run.log").write_text("\n".join(lines))
    csv=["n,gamma_mean,gamma_std,R2_mean,n_valid"]+\
        [f"{r['n']},{r['gamma_mean']:.6f},{r['gamma_std']:.6f},{r['R2_mean']:.6f},{r['n_valid']}" for r in rows]
    (OUT_DIR/"n_sweep.csv").write_text("\n".join(csv))
    pr(f"\nArtifacte: {OUT_DIR}")
    return 0 if n_pass==4 else 1

if __name__ == "__main__":
    sys.exit(main())
