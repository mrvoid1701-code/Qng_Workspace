#!/usr/bin/env python3
"""
QNG Stress Test — Categoria B: Atac termodinamic

Bomba eleganta: legile termodinamicii ca arme.

Atacuri:
  B1  T → 0   : legea a 3-a — S → 0, C_V → 0 (teorema lui Nernst)
  B2  T → ∞   : limita clasica — C_V → K_eff (Dulong-Petit), E_MB/E_BE → 1
  B3  S(T) monoton?  : dS/dT > 0 pentru orice T? (a doua lege)
  B4  C_V(T) > 0?    : stabilitate termodinamica globala
  B5  Tranzitie de faza? : e C_V(T) continua? (gaz Bose liber → fara BEC)
  B6  Ecuatie de stare : E vs T (liniar clasic sau cuantic?)
  B7  Entropie per mod : distribuita uniform sau localizata?

Intrebari de fond:
  - Exista un T* critic unde teoria se rupe?
  - Sistemul respecta toate legile termodinamicii la nivel de cod?
  - Limita clasica (T → ∞) reproduce ecuipartitia?

Dependinte: stdlib only.
"""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stress-B-thermodynamics-v1"

N = 280; K = 8; SEED = 3401
N_MODES = 20; N_ITER_POW = 350; M_EFF_SQ = 0.014


# ── Graf Jaccard ──────────────────────────────────────────────────────────────

def build_jaccard_graph(n, k_init, k_conn, seed):
    rng = random.Random(seed)
    p0 = k_init / (n - 1)
    adj0 = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p0:
                adj0[i].add(j); adj0[j].add(i)
    adj = [set() for _ in range(n)]
    for i in range(n):
        Ni = adj0[i] | {i}
        scores = []
        for j in range(n):
            if j == i: continue
            Nj = adj0[j] | {j}
            inter = len(Ni & Nj); union = len(Ni | Nj)
            scores.append((inter / union if union else 0., j))
        scores.sort(reverse=True)
        for _, j in scores[:k_conn]:
            adj[i].add(j); adj[j].add(i)
    return [sorted(s) for s in adj]


# ── Spectral ──────────────────────────────────────────────────────────────────

def _dot(u, v):    return sum(u[i]*v[i] for i in range(len(u)))
def _norm(v):
    n = math.sqrt(_dot(v, v))
    return [x/n for x in v] if n > 1e-14 else v[:]
def _defl(v, basis):
    w = v[:]
    for b in basis:
        c = _dot(w, b); w = [w[i] - c*b[i] for i in range(len(w))]
    return w
def _rw(f, nb):
    return [(sum(f[j] for j in b) / len(b)) if b else 0. for b in nb]

def compute_eigenmodes(neighbours, n_modes, n_iter, rng):
    n = len(neighbours); vecs = []; mus = []
    for _ in range(n_modes):
        v = _norm(_defl([rng.gauss(0., 1.) for _ in range(n)], vecs))
        for _ in range(n_iter):
            w = _norm(_defl(_rw(v, neighbours), vecs))
            if math.sqrt(_dot(w, w)) < 1e-14: break
            v = w
        Av = _rw(v, neighbours)
        mu = max(0., 1. - _dot(v, Av))
        vecs.append(v); mus.append(mu)
    order = sorted(range(len(mus)), key=lambda k: mus[k])
    return [mus[k] for k in order], [vecs[k] for k in order]


# ── Termodinamica bosonica ────────────────────────────────────────────────────

def thermo(omegas: list[float], T: float) -> dict:
    """
    Calculeaza (F, U, S, C_V) pentru gaz bosonic la temperatura T.

    ln Z = -Σ ln(1 - exp(-βω))
    F    = -T ln Z
    U    = Σ ω n_k        [n_k = Bose-Einstein]
    S    = (U - F) / T    [equivalenta cu ln Z + βU]
    C_V  = Σ ω² n_k(n_k+1) / T²
    """
    if T < 1e-20:
        return {"ln_Z": 0., "F": 0., "U": 0., "S": 0., "C_V": 0., "n_modes": 0}
    beta = 1. / T
    ln_Z = 0.; U = 0.; C_V = 0.; n_active = 0
    for omega in omegas:
        if omega < 1e-14: continue
        x = beta * omega
        if x > 700.: continue       # exp(-x) ≈ 0, contributie neglijabila
        expm = math.exp(-x)
        denom = 1. - expm
        if denom < 1e-30: continue  # overflow
        ln_Z += -math.log(denom)
        n_k   = expm / denom
        U    += omega * n_k
        C_V  += omega**2 * n_k * (n_k + 1.) / T**2
        n_active += 1
    F = -T * ln_Z
    S = (U - F) / T if T > 1e-20 else 0.
    return {"ln_Z": ln_Z, "F": F, "U": U, "S": S, "C_V": C_V, "n_modes": n_active}


def thermo_per_mode(omegas: list[float], T: float) -> list[dict]:
    """Contributia fiecarui mod la termodinamica."""
    if T < 1e-20: return []
    beta = 1. / T
    result = []
    for k, omega in enumerate(omegas):
        if omega < 1e-14:
            result.append({"k": k, "omega": omega, "S_k": 0., "n_k": 0.})
            continue
        x = beta * omega
        if x > 700.:
            result.append({"k": k, "omega": omega, "S_k": 0., "n_k": 0.})
            continue
        expm = math.exp(-x)
        denom = 1. - expm
        if denom < 1e-30:
            result.append({"k": k, "omega": omega, "S_k": 0., "n_k": 0.})
            continue
        n_k  = expm / denom
        ln_Z_k = -math.log(denom)
        S_k  = ln_Z_k + x * n_k   # S_k = ln Z_k + β ω n_k
        result.append({"k": k, "omega": omega, "S_k": S_k, "n_k": n_k})
    return result


# ── T_global din Unruh ────────────────────────────────────────────────────────

def compute_T_global(neighbours):
    n = len(neighbours)
    degrees = [len(nb) for nb in neighbours]
    mean_k = sum(degrees) / n
    alpha = [d / mean_k for d in degrees]
    T_list = []
    for i in range(n):
        nb = neighbours[i]
        if not nb: T_list.append(0.); continue
        a_eff = sum(abs(alpha[j] - alpha[i]) for j in nb) / len(nb)
        T_list.append(a_eff / (2. * math.pi))
    return statistics.mean(T_list)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print("=" * 70)
    print("QNG STRESS TEST — Categoria B: Atac termodinamic")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print("Bomba: legile termodinamicii ca arme contra QNG.")
    print("=" * 70)

    # Construieste graful si calculează eigenmodes
    print(f"\n[0] Graf Jaccard N={N}, k={K}, seed={SEED}")
    nb = build_jaccard_graph(N, K, K, SEED)
    rng = random.Random(SEED + 1)
    mus, vecs = compute_eigenmodes(nb, N_MODES, N_ITER_POW, rng)
    active = [i for i in range(1, len(mus))]  # skip zero mode
    omegas = [math.sqrt(mus[i] + M_EFF_SQ) for i in active]
    K_eff  = len(omegas)
    T_base = compute_T_global(nb)
    omega_min = min(omegas); omega_max = max(omegas); omega_mean = statistics.mean(omegas)
    print(f"  K_eff={K_eff}  ω ∈ [{omega_min:.4f}, {omega_max:.4f}]  ω_mean={omega_mean:.4f}")
    print(f"  T_global (Unruh) = {T_base:.6e}")
    print(f"  β·ω_min = {omega_min/T_base:.3f}  (>1: quantum regime)")
    print(f"  β·ω_max = {omega_max/T_base:.3f}")

    # ── B1: T → 0 (legea a 3-a) ───────────────────────────────────────────────
    print("\n── B1: T → 0 (Legea a 3-a: S→0, C_V→0) ──────────────────────────")
    T_cold = [T_base * f for f in [1.0, 0.1, 0.01, 1e-3, 1e-4, 1e-6, 1e-9, 1e-12]]
    b1_rows = []
    for T in T_cold:
        th = thermo(omegas, T)
        b1_rows.append({"T": T, **th})
        print(f"  T={T:.3e}  S={th['S']:.4e}  C_V={th['C_V']:.4e}  "
              f"U={th['U']:.4e}  F={th['F']:.4e}")
    # Verificare legea a 3-a
    S_at_Tmin = b1_rows[-1]["S"]
    CV_at_Tmin = b1_rows[-1]["C_V"]
    law3_S  = abs(S_at_Tmin)  < 1e-10
    law3_CV = abs(CV_at_Tmin) < 1e-10
    print(f"  Legea a 3-a: S→0? {law3_S} (S={S_at_Tmin:.2e})  "
          f"C_V→0? {law3_CV} (C_V={CV_at_Tmin:.2e})")

    # ── B2: T → ∞ (limita clasica, Dulong-Petit) ──────────────────────────────
    print("\n── B2: T → ∞ (Dulong-Petit: C_V → K_eff) ─────────────────────────")
    T_hot = [T_base * f for f in [1.0, 10., 100., 1e3, 1e4, 1e6, 1e9, 1e12]]
    b2_rows = []
    for T in T_hot:
        th = thermo(omegas, T)
        # Raport E_MB/E_BE: la T mare, n_k ≈ T/ω → U ≈ K_eff * T (clasic)
        # E_MB = K_eff * T (equipartition clasic)
        E_MB   = K_eff * T
        E_BE   = th["U"]
        ratio  = E_MB / E_BE if E_BE > 1e-30 else float("inf")
        CV_frac = th["C_V"] / K_eff   # trebuie → 1 la T → ∞
        b2_rows.append({"T": T, **th, "E_MB": E_MB, "ratio_MB_BE": ratio,
                         "CV_frac_Keff": CV_frac})
        print(f"  T={T:.3e}  C_V/K_eff={CV_frac:.4f}  "
              f"E_MB/E_BE={ratio:.3f}  S={th['S']:.4e}")
    # Limita clasica
    CV_classical = b2_rows[-1]["CV_frac_Keff"]
    ratio_classical = b2_rows[-1]["ratio_MB_BE"]
    dulong_petit = abs(CV_classical - 1.0) < 0.01
    equipartition = abs(ratio_classical - 1.0) < 0.01
    print(f"  Dulong-Petit (C_V/K→1): {dulong_petit} (C_V/K={CV_classical:.6f})")
    print(f"  Echipajul clasic (E_MB/E_BE→1): {equipartition} ({ratio_classical:.6f})")

    # ── B3: S(T) monoton crescatoare? ────────────────────────────────────────
    print("\n── B3: S(T) monoton? (dS/dT > 0 intotdeauna?) ────────────────────")
    T_sweep = [T_base * 10**i for i in range(-8, 9)]  # 17 puncte
    S_vals  = []
    b3_rows = []
    for T in T_sweep:
        th = thermo(omegas, T)
        S_vals.append(th["S"])
        b3_rows.append({"T": T, "S": th["S"], "C_V": th["C_V"]})
    violations = []
    for i in range(1, len(S_vals)):
        if S_vals[i] < S_vals[i-1] - 1e-15:
            violations.append((T_sweep[i-1], T_sweep[i], S_vals[i-1], S_vals[i]))
    monoton = len(violations) == 0
    print(f"  S monotona? {monoton}  "
          f"(S_min={min(S_vals):.4e}  S_max={max(S_vals):.4e})")
    if violations:
        print(f"  VIOLARI:")
        for v in violations[:5]:
            print(f"    T={v[0]:.2e}→{v[1]:.2e}: S={v[2]:.4e}→{v[3]:.4e}")

    # ── B4: C_V(T) > 0 intotdeauna? ────────────────────────────────────────────
    print("\n── B4: C_V(T) > 0? (stabilitate termodinamica) ────────────────────")
    CV_vals = [r["C_V"] for r in b3_rows]
    CV_negative = [(T_sweep[i], cv) for i, cv in enumerate(CV_vals) if cv < -1e-20]
    CV_positive = all(cv >= -1e-20 for cv in CV_vals)
    print(f"  C_V >= 0 intotdeauna? {CV_positive}")
    if CV_negative:
        print(f"  VALORI NEGATIVE: {CV_negative[:5]}")
    print(f"  C_V_min = {min(CV_vals):.4e}  la T={T_sweep[CV_vals.index(min(CV_vals))]:.2e}")
    print(f"  C_V_max = {max(CV_vals):.4e}  la T={T_sweep[CV_vals.index(max(CV_vals))]:.2e}")

    # ── B5: Tranzitie de faza? C_V continua? ─────────────────────────────────
    print("\n── B5: Tranzitie de faza? (discontinuitate C_V?) ──────────────────")
    # Sweep fin pe 100 puncte in intervalul [T_base/10, 100*T_base]
    T_fine = [T_base * 10**(-1 + 3*i/99) for i in range(100)]
    CV_fine = [thermo(omegas, T)["C_V"] for T in T_fine]
    # Cauta discontinuitati: variatii mai mari de 10x intre puncte adiacente
    jumps = []
    for i in range(1, len(CV_fine)):
        if CV_fine[i-1] > 1e-30:
            ratio = CV_fine[i] / CV_fine[i-1]
            if ratio > 10 or ratio < 0.1:
                jumps.append((T_fine[i-1], T_fine[i], CV_fine[i-1], CV_fine[i]))
    has_transition = len(jumps) > 0
    print(f"  Tranzitie detectata? {has_transition}")
    if jumps:
        for j in jumps[:3]:
            print(f"  JUMP: T={j[0]:.2e}→{j[1]:.2e}: C_V={j[2]:.4e}→{j[3]:.4e}")
    else:
        # Varful lui C_V
        peak_idx = CV_fine.index(max(CV_fine))
        print(f"  C_V continua, max la T*={T_fine[peak_idx]:.4e}  "
              f"(C_V_peak={CV_fine[peak_idx]:.4e})")
        print(f"  (Pentru gaz Bose liber pe graf finit, nu exista BEC — corect)")

    # ── B6: Ecuatie de stare U(T) ─────────────────────────────────────────────
    print("\n── B6: Ecuatie de stare U(T) — quantum vs clasic ──────────────────")
    # La T mic: U ≈ Σ ω_k exp(-ω_k/T)  (quantum, exponential)
    # La T mare: U ≈ K_eff * T           (clasic, liniar)
    T_state = [T_base * 10**i for i in range(-4, 7)]
    b6_rows = []
    print(f"  {'T':>12} {'U':>12} {'U/(K_eff*T)':>13} {'regim'}")
    for T in T_state:
        th = thermo(omegas, T)
        U = th["U"]
        classical_frac = U / (K_eff * T) if T > 0 else 0.
        regime = "clasic" if classical_frac > 0.9 else "quantum"
        b6_rows.append({"T": T, "U": U, "classical_frac": classical_frac})
        print(f"  T={T:.4e}  U={U:.4e}  U/(K*T)={classical_frac:.4f}  [{regime}]")

    T_crossover = next((b6_rows[i]["T"] for i in range(len(b6_rows))
                        if b6_rows[i]["classical_frac"] > 0.5), None)
    print(f"  T_crossover (quantum→clasic) ≈ {T_crossover:.4e}")
    print(f"  T_base/T_crossover = {T_base/T_crossover:.3f}  (sistem in regim quantum)")

    # ── B7: Entropie per mod — uniform sau localizata? ───────────────────────
    print("\n── B7: Entropie per mod (la T_base) ──────────────────────────────")
    modes_at_T = thermo_per_mode(omegas, T_base)
    S_per_mode = [m["S_k"] for m in modes_at_T]
    if S_per_mode:
        S_mean = statistics.mean(S_per_mode)
        S_std  = statistics.stdev(S_per_mode) if len(S_per_mode) > 1 else 0.
        cv_S   = S_std / S_mean if S_mean > 1e-30 else float("inf")
        S_min  = min(S_per_mode); S_max = max(S_per_mode)
        print(f"  S_k: mean={S_mean:.4e}  std={S_std:.4e}  "
              f"cv={cv_S:.3f}  min={S_min:.4e}  max={S_max:.4e}")
        # Modurile cu cea mai mare/mica entropie
        sorted_modes = sorted(modes_at_T, key=lambda m: m["S_k"], reverse=True)
        print(f"  Top 3 moduri (S maxim): "
              f"{[(round(m['omega'],4), round(m['S_k'],6)) for m in sorted_modes[:3]]}")
        print(f"  Bot 3 moduri (S minim): "
              f"{[(round(m['omega'],4), round(m['S_k'],6)) for m in sorted_modes[-3:]]}")
        entropy_uniform = cv_S < 0.5
        print(f"  Entropie uniform distribuita? {entropy_uniform} (cv_S={cv_S:.3f})")

    # ── Verdict global ────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SUMAR FINAL — Consistenta termodinamica")
    print("=" * 70)

    checks = {
        "B1_third_law_S":    law3_S,
        "B1_third_law_CV":   law3_CV,
        "B2_dulong_petit":   dulong_petit,
        "B2_equipartition":  equipartition,
        "B3_S_monoton":      monoton,
        "B4_CV_positive":    CV_positive,
        "B5_no_transition":  not has_transition,
    }
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  {check:<25} {status}")

    all_pass = all(checks.values())
    verdict  = "THERMODYNAMICALLY_CONSISTENT" if all_pass else "INCONSISTENT"
    print(f"\n  verdict={verdict}")
    print(f"  Timp total: {time.time()-t0:.1f}s")

    if all_pass:
        print()
        print("TOATE legile termodinamicii respectate la nivel de cod.")
        print(f"T_crossover quantum→clasic: {T_crossover:.4e}")
        print(f"T_Unruh / T_crossover = {T_base/T_crossover:.3f}  (sistem profund quantum)")
    else:
        fails = [k for k,v in checks.items() if not v]
        print(f"\nVIOLATII: {fails}")

    # ── Salvare ───────────────────────────────────────────────────────────────
    # CSV S vs T (sweep complet)
    csv_T = OUT_DIR / "stress_B_S_vs_T.csv"
    with csv_T.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["T", "S", "C_V", "U", "F", "ln_Z"])
        for row in b3_rows:
            th = thermo(omegas, row["T"])
            w.writerow([row["T"], row["S"], row["C_V"],
                        th["U"], th["F"], th["ln_Z"]])

    # CSV C_V fine sweep
    csv_CV = OUT_DIR / "stress_B5_CV_fine.csv"
    with csv_CV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["T", "C_V"])
        for T, CV in zip(T_fine, CV_fine):
            w.writerow([T, CV])

    json_path = OUT_DIR / "stress_B_results.json"
    json_path.write_text(json.dumps({
        "run_date": datetime.utcnow().isoformat() + "Z",
        "params": {"N": N, "K": K, "SEED": SEED, "K_eff": K_eff,
                   "T_base": T_base, "omega_min": omega_min,
                   "omega_max": omega_max, "T_crossover": T_crossover},
        "checks": checks,
        "verdict": verdict,
        "B1_cold_sweep": [
            {"T": r["T"], "S": r["S"], "C_V": r["C_V"]} for r in b1_rows
        ],
        "B2_hot_sweep": [
            {"T": r["T"], "C_V": r["C_V"], "CV_frac": r["CV_frac_Keff"],
             "ratio_MB_BE": r["ratio_MB_BE"]} for r in b2_rows
        ],
        "B3_S_violations": violations,
        "B4_CV_negative": CV_negative,
        "B5_phase_transitions": [{"T0": j[0], "T1": j[1]} for j in jumps],
        "B7_entropy_per_mode": {
            "mean": S_mean, "std": S_std, "cv": cv_S,
            "uniform": entropy_uniform
        } if S_per_mode else {},
    }, indent=2, default=str), encoding="utf-8")

    print(f"\nArtefacte: {OUT_DIR}/")
    print(f"  {csv_T.name}  {csv_CV.name}  {json_path.name}")
    print()
    print("=" * 70)
    print(f"STRESS TEST B COMPLET | verdict={verdict}")
    print("=" * 70)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
