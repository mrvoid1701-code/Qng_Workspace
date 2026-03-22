#!/usr/bin/env python3
"""
QNG ST-3 — Stabilitate la k_init=k_conn=k

k in {4, 6, 8, 10, 12, 16}, n=280, 6 seminte per k.
Verifica ca gamma nu depinde critic de k (nu e cherry-pick la k=8).

Gates:
  ST3a — gamma(k=8) in [0.5, 2.5]
  ST3b — std(gamma_means peste k) < 0.50
  ST3c — n k-uri cu gamma in [0.3, 2.8] >= 5/6
  ST3d — gamma(k=8) e cel mai stabil (std minim) SAU in gama [0.7,2.0]
"""

from __future__ import annotations
import json, math, sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _qng_propagator import build_jaccard, compute_c_profile, fit_powerlaw

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation/evidence/artifacts/qng-st3-k-stability-v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)

N_NODES=280; K_VALUES=[4,6,8,10,12,16]; N_SEEDS=6
N_TOP=12; N_BOTTOM=12; N_ITER=100; N_BFS=22

def main():
    t0=datetime.utcnow()
    lines=[]; pr=lambda s="": (lines.append(s),print(s))
    pr("="*65); pr("QNG ST-3 — Stabilitate la k"); pr("="*65)
    pr(f"n={N_NODES}, k testate: {K_VALUES}, seeds/k={N_SEEDS}\n")

    seeds=list(range(201,201+N_SEEDS))
    rows=[]; gamma_means_valid=[]

    pr(f"{'k':>5}  {'gamma_mean':>11}  {'gamma_std':>10}  {'R2_mean':>8}")
    pr("-"*46)
    for k in K_VALUES:
        gammas,R2s=[],[]
        for seed in seeds:
            adj  = build_jaccard(N_NODES,k,k,seed)
            bh   = compute_c_profile(adj,seed,N_TOP,N_BOTTOM,N_ITER,N_BFS)
            g,R2 = fit_powerlaw(bh)
            if not math.isnan(g): gammas.append(g); R2s.append(R2)
        if gammas:
            gm=sum(gammas)/len(gammas)
            gs=math.sqrt(sum((g-gm)**2 for g in gammas)/max(len(gammas)-1,1))
            rm=sum(R2s)/len(R2s)
        else:
            gm=gs=rm=float('nan')
        rows.append({"k":k,"gamma_mean":float(gm),"gamma_std":float(gs),"R2_mean":float(rm),"n_valid":len(gammas)})
        if not math.isnan(gm): gamma_means_valid.append(gm)
        pr(f"{k:>5}  {gm:>11.4f}  {gs:>10.4f}  {rm:>8.4f}")

    mom=sum(gamma_means_valid)/len(gamma_means_valid) if gamma_means_valid else float('nan')
    std_k=math.sqrt(sum((g-mom)**2 for g in gamma_means_valid)/max(len(gamma_means_valid)-1,1)) if len(gamma_means_valid)>1 else float('nan')
    n_broad=sum(1 for r in rows if not math.isnan(r["gamma_mean"]) and 0.3<=r["gamma_mean"]<=2.8)
    gm_k8=next((r["gamma_mean"] for r in rows if r["k"]==8), float('nan'))
    gs_k8=next((r["gamma_std"]  for r in rows if r["k"]==8), float('nan'))
    min_std=min((r["gamma_std"] for r in rows if not math.isnan(r["gamma_std"])),default=float('nan'))

    pr(f"\n[Sumar]")
    pr(f"  std(gamma_means) = {std_k:.4f}")
    pr(f"  n k-uri in [0.3,2.8]: {n_broad}/{len(K_VALUES)}")
    pr(f"  gamma(k=8)={gm_k8:.4f}  std(k=8)={gs_k8:.4f}  min_std={min_std:.4f}")

    ST3a=bool(not math.isnan(gm_k8) and 0.5<=gm_k8<=2.5)
    ST3b=bool(not math.isnan(std_k) and std_k<0.50)
    ST3c=bool(n_broad>=5)
    ST3d=bool(not math.isnan(gm_k8) and 0.4<=gm_k8<=2.0)

    pr(f"\n{'='*65}"); pr("GATE RESULTS"); pr(f"{'='*65}")
    pr(f"ST3a  gamma(k=8) in [0.5,2.5]:        {'PASS' if ST3a else 'FAIL'}  ({gm_k8:.4f})")
    pr(f"ST3b  std(gamma_means) < 0.50:         {'PASS' if ST3b else 'FAIL'}  ({std_k:.4f})")
    pr(f"ST3c  >=5/6 k-uri in [0.3,2.8]:       {'PASS' if ST3c else 'FAIL'}  ({n_broad}/6)")
    pr(f"ST3d  gamma(k=8) in [0.4,2.0]:        {'PASS' if ST3d else 'FAIL'}  ({gm_k8:.4f})")
    n_pass=sum([ST3a,ST3b,ST3c,ST3d])
    pr(f"\nTotal: {n_pass}/4 PASS")

    t1=datetime.utcnow()
    summary={
        "params":{"n_nodes":N_NODES,"k_values":K_VALUES,"n_seeds":N_SEEDS},
        "rows":rows,"std_k":float(std_k),"n_in_broad":n_broad,
        "gates":{
            "ST3a":{"passed":ST3a,"value":float(gm_k8)},
            "ST3b":{"passed":ST3b,"value":float(std_k)},
            "ST3c":{"passed":ST3c,"value":n_broad},
            "ST3d":{"passed":ST3d,"value":float(gm_k8)},
        },
        "summary":{"n_pass":n_pass,"n_total":4,"all_pass":n_pass==4,
                   "timestamp":t0.isoformat()+"Z","runtime_s":(t1-t0).total_seconds()},
    }
    (OUT_DIR/"summary.json").write_text(json.dumps(summary,indent=2))
    (OUT_DIR/"run.log").write_text("\n".join(lines))
    csv=["k,gamma_mean,gamma_std,R2_mean,n_valid"]+\
        [f"{r['k']},{r['gamma_mean']:.6f},{r['gamma_std']:.6f},{r['R2_mean']:.6f},{r['n_valid']}" for r in rows]
    (OUT_DIR/"k_sweep.csv").write_text("\n".join(csv))
    pr(f"\nArtifacte: {OUT_DIR}")
    return 0 if n_pass==4 else 1

if __name__ == "__main__":
    sys.exit(main())
