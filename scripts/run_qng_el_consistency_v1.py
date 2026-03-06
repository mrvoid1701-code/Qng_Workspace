#!/usr/bin/env python3
"""
QNG Foundation Stability EL-consistency checker (v2-capable).

Purpose:
- Validate that the implemented stability update is consistent with the
  discrete Euler-Lagrange proxy update in the frozen foundation lane.
- Report residual statistics (median, p90, max) for Sigma/chi/phi.

Inputs:
- Frozen stability update/action constants (same defaults as stability-v1).
- Fixed block specs (dataset label + seeds + n_nodes + steps).
- Fixed stress case grid (edge_prob, chi_scale, noise, phi_shock).

Outputs:
- profile_residuals.csv
- summary.csv
- report.md
- manifest.json
- run-log.txt

Default artifacts are written under:
  05_validation/evidence/artifacts/qng-foundation-stability-v2/
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.tools.run_stability_stress_v1 import (
    CaseConfig,
    StressConfig,
    build_graph_erdos,
    init_state,
    one_step,
)


ROOT = REPO_ROOT
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-foundation-stability-v2"
DEFAULT_PREREG_DOC_V1 = ROOT / "05_validation" / "pre-registrations" / "qng-foundation-stability-tests-v1.md"
DEFAULT_PREREG_DOC_V2 = ROOT / "05_validation" / "pre-registrations" / "qng-foundation-stability-tests-v2.md"
DEFAULT_FOUNDATION_DOC = ROOT / "03_math" / "derivations" / "qng-foundation-stability-v1.md"
DEFAULT_ACTION_DOC = ROOT / "03_math" / "derivations" / "qng-stability-action-v1.md"
DEFAULT_UPDATE_DOC = ROOT / "03_math" / "derivations" / "qng-stability-update-v1.md"


def parse_float_grid(text: str) -> list[float]:
    out: list[float] = []
    for item in str(text).split(","):
        t = item.strip()
        if not t:
            continue
        out.append(float(t))
    if not out:
        raise ValueError("empty float grid")
    return out


def parse_seed_spec(seed_spec: str) -> list[int]:
    seed_spec = seed_spec.strip()
    if not seed_spec:
        raise ValueError("empty seed spec")
    values: list[int] = []
    for token in seed_spec.split(","):
        t = token.strip()
        if not t:
            continue
        if "-" in t:
            parts = t.split("-", 1)
            lo = int(parts[0].strip())
            hi = int(parts[1].strip())
            if hi < lo:
                lo, hi = hi, lo
            values.extend(range(lo, hi + 1))
        else:
            values.append(int(t))
    if not values:
        raise ValueError(f"invalid seed spec: {seed_spec}")
    # de-duplicate preserving order
    seen: set[int] = set()
    ordered: list[int] = []
    for s in values:
        if s in seen:
            continue
        seen.add(s)
        ordered.append(s)
    return ordered


def parse_block_specs(text: str) -> list[dict[str, Any]]:
    """
    Format:
      DATASET_ID:SEEDS:N_NODES:STEPS;DATASET_ID:SEEDS:N_NODES:STEPS;...
    Example:
      STABILITY-PRIMARY:3401-3403:36:60;STABILITY-ATTACK:4401-4403:36:60
    """
    blocks: list[dict[str, Any]] = []
    for chunk in str(text).split(";"):
        raw = chunk.strip()
        if not raw:
            continue
        parts = raw.split(":")
        if len(parts) != 4:
            raise ValueError(f"invalid block spec: {raw}")
        dataset_id = parts[0].strip()
        seeds = parse_seed_spec(parts[1].strip())
        n_nodes = int(parts[2].strip())
        steps = int(parts[3].strip())
        blocks.append(
            {
                "dataset_id": dataset_id,
                "seeds": seeds,
                "n_nodes": n_nodes,
                "steps": steps,
            }
        )
    if not blocks:
        raise ValueError("no block specs parsed")
    return blocks


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
    x = sorted(vals)
    idx = int(math.floor(q * (len(x) - 1)))
    return x[idx]


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def f6(x: float) -> str:
    return f"{x:.6f}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def as_repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.resolve().as_posix()


def clip01_local(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def wrap_angle_local(x: float) -> float:
    y = (x + math.pi) % (2.0 * math.pi) - math.pi
    if y <= -math.pi:
        return y + 2.0 * math.pi
    return y


def angle_diff_local(a: float, b: float) -> float:
    return wrap_angle_local(a - b)


def neighbors_mean_local(vals: list[float], neighbors: list[int], fallback: float) -> float:
    if not neighbors:
        return fallback
    return sum(vals[j] for j in neighbors) / len(neighbors)


def circular_mean_local(phi_vals: list[float], neighbors: list[int], fallback: float) -> float:
    if not neighbors:
        return fallback
    s = 0.0
    c = 0.0
    for j in neighbors:
        s += math.sin(phi_vals[j])
        c += math.cos(phi_vals[j])
    if abs(s) < 1e-16 and abs(c) < 1e-16:
        return fallback
    return math.atan2(s, c)


def sigma_components_local(
    i: int,
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    cfg: StressConfig,
    k_eq: float,
) -> dict[str, float]:
    deg_i = float(len(adj[i]))
    chi_i = chi[i]
    chi_neigh = neighbors_mean_local(chi, adj[i], chi_i)
    phi_neigh = circular_mean_local(phi, adj[i], phi[i])

    tau_i = max(cfg.tau_floor, cfg.alpha_tau * max(abs(chi_i), cfg.tau_floor))
    delta_t_local = 1.0 + cfg.dt_local_beta * abs(chi_i - chi_neigh)

    sigma_chi = math.exp(-abs(chi_i - cfg.chi_ref) / max(cfg.chi_ref, 1e-12))
    sigma_struct = math.exp(-abs(deg_i - k_eq) / max(k_eq, 1e-12))
    sigma_temp = math.exp(-abs(delta_t_local - tau_i) / max(tau_i, 1e-12))
    sigma_phi = 0.5 * (1.0 + math.cos(angle_diff_local(phi[i], phi_neigh)))
    sigma_hat = clip01_local(sigma_chi * sigma_struct * sigma_temp * sigma_phi)
    sigma_neigh = neighbors_mean_local(sigma, adj[i], sigma[i])

    return {
        "sigma_hat": sigma_hat,
        "sigma_neigh": sigma_neigh,
    }


def make_cases(
    edge_prob_grid: list[float],
    chi_scale_grid: list[float],
    noise_grid: list[float],
    phi_shock_grid: list[float],
    base_seed: int,
    prefix: str,
) -> list[CaseConfig]:
    out: list[CaseConfig] = []
    idx = 0
    for ep in edge_prob_grid:
        for cs in chi_scale_grid:
            for nz in noise_grid:
                for ph in phi_shock_grid:
                    idx += 1
                    out.append(
                        CaseConfig(
                            case_id=f"{prefix}C{idx:03d}",
                            edge_prob=ep,
                            chi_scale=cs,
                            noise_level=nz,
                            phi_shock=ph,
                            case_seed=base_seed + 1009 * idx,
                        )
                    )
    return out


def one_step_el_pred(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    cfg: StressConfig,
    rng: random.Random,
    noise_level: float,
) -> tuple[list[float], list[float], list[float]]:
    n = len(sigma)
    k_eq = mean([float(len(nbrs)) for nbrs in adj]) if adj else 1.0

    sig_new = [0.0] * n
    chi_new = [0.0] * n
    phi_new = [0.0] * n

    for i in range(n):
        comp = sigma_components_local(i, sigma, chi, phi, adj, cfg, k_eq)
        sigma_i = sigma[i]
        sigma_neigh = comp["sigma_neigh"]
        sigma_hat = comp["sigma_hat"]
        phi_neigh = circular_mean_local(phi, adj[i], phi[i])

        grad_sigma = cfg.k_closure * (sigma_i - sigma_hat)
        grad_sigma += cfg.k_smooth * (sigma_i - sigma_neigh)
        grad_sigma += cfg.k_mix * chi[i]

        grad_chi = cfg.k_chi * chi[i] + cfg.k_mix * (sigma_i - sigma_neigh)
        grad_phi = cfg.k_phi * math.sin(angle_diff_local(phi[i], phi_neigh))

        eta_chi = rng.gauss(0.0, noise_level)
        eta_phi = rng.gauss(0.0, 0.5 * noise_level)

        sigma_prop = sigma_i - cfg.alpha_sigma * grad_sigma
        chi_prop = chi[i] - cfg.alpha_chi * grad_chi + eta_chi
        phi_prop = phi[i] - cfg.alpha_phi * grad_phi + eta_phi

        sigma_next = clip01_local(sigma_prop)
        chi_next = chi_prop
        phi_next = wrap_angle_local(phi_prop)

        sig_new[i] = sigma_next
        chi_new[i] = chi_next
        phi_new[i] = phi_next

    return sig_new, chi_new, phi_new


def one_step_self_residual_v1(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    cfg: StressConfig,
    rng: random.Random,
    noise_level: float,
) -> tuple[list[float], list[float], list[float], list[float], list[float], list[float]]:
    """
    Legacy v1 checker behavior: self-referential residual.
    """
    n = len(sigma)
    k_eq = mean([float(len(nbrs)) for nbrs in adj]) if adj else 1.0

    sig_new = [0.0] * n
    chi_new = [0.0] * n
    phi_new = [0.0] * n
    rs_all: list[float] = []
    rc_all: list[float] = []
    rp_all: list[float] = []

    for i in range(n):
        comp = sigma_components_local(i, sigma, chi, phi, adj, cfg, k_eq)
        sigma_i = sigma[i]
        sigma_neigh = comp["sigma_neigh"]
        sigma_hat = comp["sigma_hat"]
        phi_neigh = circular_mean_local(phi, adj[i], phi[i])

        grad_sigma = cfg.k_closure * (sigma_i - sigma_hat)
        grad_sigma += cfg.k_smooth * (sigma_i - sigma_neigh)
        grad_sigma += cfg.k_mix * chi[i]
        grad_chi = cfg.k_chi * chi[i] + cfg.k_mix * (sigma_i - sigma_neigh)
        grad_phi = cfg.k_phi * math.sin(angle_diff_local(phi[i], phi_neigh))

        eta_chi = rng.gauss(0.0, noise_level)
        eta_phi = rng.gauss(0.0, 0.5 * noise_level)

        sigma_prop = sigma_i - cfg.alpha_sigma * grad_sigma
        chi_prop = chi[i] - cfg.alpha_chi * grad_chi + eta_chi
        phi_prop = phi[i] - cfg.alpha_phi * grad_phi + eta_phi

        sigma_next = clip01_local(sigma_prop)
        chi_next = chi_prop
        phi_next = wrap_angle_local(phi_prop)

        sig_new[i] = sigma_next
        chi_new[i] = chi_next
        phi_new[i] = phi_next

        rs_all.append(abs(sigma_next - sigma_prop))
        rc_all.append(abs(chi_next - chi_prop))
        rp_all.append(abs(angle_diff_local(phi_next, phi_prop)))

    return sig_new, chi_new, phi_new, rs_all, rc_all, rp_all


def run_profile(
    cfg: StressConfig,
    dataset_id: str,
    seed: int,
    case: CaseConfig,
    comparator_mode: str,
    sigma_median_max: float,
    sigma_p90_max: float,
    sigma_max_max: float,
    global_p90_max: float,
    global_max_max: float,
    chi_max_max: float,
    phi_max_max: float,
) -> dict[str, Any]:
    rng = random.Random(case.case_seed)
    adj = build_graph_erdos(cfg.n_nodes, case.edge_prob, rng)
    sigma, chi, phi = init_state(cfg.n_nodes, case.chi_scale, case.phi_shock, rng)

    all_sigma: list[float] = []
    all_chi: list[float] = []
    all_phi: list[float] = []
    all_joint: list[float] = []
    for _ in range(cfg.steps):
        if comparator_mode == "v1":
            sigma, chi, phi, rs, rc, rp = one_step_self_residual_v1(
                sigma=sigma,
                chi=chi,
                phi=phi,
                adj=adj,
                cfg=cfg,
                rng=rng,
                noise_level=case.noise_level,
            )
            all_sigma.extend(rs)
            all_chi.extend(rc)
            all_phi.extend(rp)
            all_joint.extend(rs + rc + rp)
        else:
            rng_state = rng.getstate()
            sigma_cur, chi_cur, phi_cur, _, _, _, _, _ = one_step(
                sigma=sigma,
                chi=chi,
                phi=phi,
                adj=adj,
                cfg=cfg,
                rng=rng,
                noise_level=case.noise_level,
            )
            rng.setstate(rng_state)
            sigma_el, chi_el, phi_el = one_step_el_pred(
                sigma=sigma,
                chi=chi,
                phi=phi,
                adj=adj,
                cfg=cfg,
                rng=rng,
                noise_level=case.noise_level,
            )

            rs = [abs(a - b) for a, b in zip(sigma_cur, sigma_el)]
            rc = [abs(a - b) for a, b in zip(chi_cur, chi_el)]
            rp = [abs(angle_diff_local(a, b)) for a, b in zip(phi_cur, phi_el)]
            rj = [max(rs[i], rc[i], rp[i]) for i in range(len(rs))]

            all_sigma.extend(rs)
            all_chi.extend(rc)
            all_phi.extend(rp)
            all_joint.extend(rj)

            # Advance reference state with current implementation.
            sigma, chi, phi = sigma_cur, chi_cur, phi_cur

    sigma_med = percentile(all_sigma, 0.50)
    sigma_p90 = percentile(all_sigma, 0.90)
    sigma_max = max(all_sigma) if all_sigma else 0.0
    chi_p90 = percentile(all_chi, 0.90)
    chi_max = max(all_chi) if all_chi else 0.0
    phi_p90 = percentile(all_phi, 0.90)
    phi_max = max(all_phi) if all_phi else 0.0
    global_med = percentile(all_joint, 0.50)
    global_p90 = percentile(all_joint, 0.90)
    global_max = max(all_joint) if all_joint else 0.0

    gate_sigma_median = sigma_med <= sigma_median_max
    gate_sigma_p90 = sigma_p90 <= sigma_p90_max
    gate_sigma_max = sigma_max <= sigma_max_max
    gate_global_p90 = global_p90 <= global_p90_max
    gate_global_max = global_max <= global_max_max
    gate_chi_max = chi_max <= chi_max_max
    gate_phi_max = phi_max <= phi_max_max
    all_pass = all(
        [
            gate_sigma_median,
            gate_sigma_p90,
            gate_sigma_max,
            gate_global_p90,
            gate_global_max,
            gate_chi_max,
            gate_phi_max,
        ]
    )

    return {
        "dataset_id": dataset_id,
        "comparator_mode": comparator_mode,
        "seed": seed,
        "n_nodes": cfg.n_nodes,
        "steps": cfg.steps,
        "case_id": case.case_id,
        "case_seed": case.case_seed,
        "edge_prob": f6(case.edge_prob),
        "chi_scale": f6(case.chi_scale),
        "noise_level": f6(case.noise_level),
        "phi_shock": f6(case.phi_shock),
        "samples_per_var": str(len(all_sigma)),
        "sigma_abs_median": f6(sigma_med),
        "sigma_abs_p90": f6(sigma_p90),
        "sigma_abs_max": f6(sigma_max),
        "chi_abs_p90": f6(chi_p90),
        "chi_abs_max": f6(chi_max),
        "phi_abs_p90": f6(phi_p90),
        "phi_abs_max": f6(phi_max),
        "global_abs_median": f6(global_med),
        "global_abs_p90": f6(global_p90),
        "global_abs_max": f6(global_max),
        "gate_sigma_median": "pass" if gate_sigma_median else "fail",
        "gate_sigma_p90": "pass" if gate_sigma_p90 else "fail",
        "gate_sigma_max": "pass" if gate_sigma_max else "fail",
        "gate_global_p90": "pass" if gate_global_p90 else "fail",
        "gate_global_max": "pass" if gate_global_max else "fail",
        "gate_chi_max": "pass" if gate_chi_max else "fail",
        "gate_phi_max": "pass" if gate_phi_max else "fail",
        "all_pass": "pass" if all_pass else "fail",
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG EL consistency checker (v2).")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--comparator-mode", choices=["v1", "v2"], default="v2")
    p.add_argument("--prereg-doc", default="")
    p.add_argument(
        "--block-specs",
        default=(
            "STABILITY-PRIMARY:3401-3403:36:60;"
            "STABILITY-ATTACK:4401-4403:36:60;"
            "STABILITY-HOLDOUT:3501-3502:42:80"
        ),
        help="Semicolon-separated DATASET:SEEDS:N_NODES:STEPS blocks.",
    )

    p.add_argument("--edge-prob-grid", default="0.08,0.18,0.32")
    p.add_argument("--chi-scale-grid", default="0.50,1.00,1.50")
    p.add_argument("--noise-grid", default="0.00,0.01,0.03")
    p.add_argument("--phi-shock-grid", default="0.00,0.40")

    p.add_argument("--alpha-sigma", type=float, default=0.12)
    p.add_argument("--alpha-chi", type=float, default=0.06)
    p.add_argument("--alpha-phi", type=float, default=0.05)
    p.add_argument("--alpha-tau", type=float, default=0.08)
    p.add_argument("--chi-ref", type=float, default=1.0)
    p.add_argument("--k-closure", type=float, default=2.20)
    p.add_argument("--k-smooth", type=float, default=0.90)
    p.add_argument("--k-chi", type=float, default=0.45)
    p.add_argument("--k-mix", type=float, default=0.12)
    p.add_argument("--k-phi", type=float, default=0.25)
    p.add_argument("--metric-beta", type=float, default=0.50)
    p.add_argument("--tau-floor", type=float, default=1e-3)
    p.add_argument("--chi-active-min", type=float, default=0.05)
    p.add_argument("--dt-local-beta", type=float, default=0.40)

    # Kept to match frozen StressConfig signature; not used as decision gates here.
    p.add_argument("--chi-runaway-max", type=float, default=6.0)
    p.add_argument("--metric-cond-max", type=float, default=3.0)
    p.add_argument("--energy-rel-max", type=float, default=0.90)
    p.add_argument("--residual-max", type=float, default=0.60)
    p.add_argument("--alpha-rel-drift-max", type=float, default=0.05)
    p.add_argument("--nonlocal-delta-max", type=float, default=1e-9)

    # EL consistency thresholds (locked in prereg v2)
    p.add_argument("--sigma-median-max", type=float, default=0.020)
    p.add_argument("--sigma-p90-max", type=float, default=0.030)
    p.add_argument("--sigma-max-max", type=float, default=0.060)
    p.add_argument("--global-p90-max", type=float, default=0.030)
    p.add_argument("--global-max-max", type=float, default=0.060)
    p.add_argument("--chi-max-max", type=float, default=1e-10)
    p.add_argument("--phi-max-max", type=float, default=1e-10)

    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def build_cfg(args: argparse.Namespace, n_nodes: int, steps: int, seed: int) -> StressConfig:
    return StressConfig(
        n_nodes=n_nodes,
        steps=steps,
        seed=seed,
        alpha_sigma=args.alpha_sigma,
        alpha_chi=args.alpha_chi,
        alpha_phi=args.alpha_phi,
        alpha_tau=args.alpha_tau,
        chi_ref=args.chi_ref,
        k_closure=args.k_closure,
        k_smooth=args.k_smooth,
        k_chi=args.k_chi,
        k_mix=args.k_mix,
        k_phi=args.k_phi,
        metric_beta=args.metric_beta,
        tau_floor=args.tau_floor,
        chi_active_min=args.chi_active_min,
        dt_local_beta=args.dt_local_beta,
        chi_runaway_max=args.chi_runaway_max,
        metric_cond_max=args.metric_cond_max,
        energy_rel_max=args.energy_rel_max,
        residual_max=args.residual_max,
        alpha_rel_drift_max=args.alpha_rel_drift_max,
        nonlocal_delta_max=args.nonlocal_delta_max,
    )


def summarize_dataset(rows: list[dict[str, Any]], dataset_id: str) -> dict[str, Any]:
    n = len(rows)
    pass_count = sum(1 for r in rows if r["all_pass"] == "pass")
    sigma_meds = sorted(float(r["sigma_abs_median"]) for r in rows) if rows else [0.0]
    sigma_p90s = sorted(float(r["sigma_abs_p90"]) for r in rows) if rows else [0.0]
    global_p90s = sorted(float(r["global_abs_p90"]) for r in rows) if rows else [0.0]
    sigma_max = max(float(r["sigma_abs_max"]) for r in rows) if rows else 0.0
    global_max = max(float(r["global_abs_max"]) for r in rows) if rows else 0.0
    chi_max = max(float(r["chi_abs_max"]) for r in rows) if rows else 0.0
    phi_max = max(float(r["phi_abs_max"]) for r in rows) if rows else 0.0
    return {
        "dataset_id": dataset_id,
        "profiles_total": str(n),
        "profiles_pass": str(pass_count),
        "profiles_fail": str(n - pass_count),
        "pass_rate": f6(pass_count / max(n, 1)),
        "profile_sigma_abs_median_median": f6(percentile(sigma_meds, 0.50)),
        "profile_sigma_abs_p90_median": f6(percentile(sigma_p90s, 0.50)),
        "profile_global_abs_p90_median": f6(percentile(global_p90s, 0.50)),
        "profile_sigma_abs_max_max": f6(sigma_max),
        "profile_global_abs_max_max": f6(global_max),
        "profile_chi_abs_max_max": f6(chi_max),
        "profile_phi_abs_max_max": f6(phi_max),
        "all_pass": "pass" if pass_count == n else "fail",
    }


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    ensure_dir(out_dir)
    mode_tag = args.comparator_mode
    if args.prereg_doc.strip():
        prereg_doc = Path(args.prereg_doc).resolve()
    else:
        prereg_doc = DEFAULT_PREREG_DOC_V1 if mode_tag == "v1" else DEFAULT_PREREG_DOC_V2

    blocks = parse_block_specs(args.block_specs)
    edge_prob_grid = parse_float_grid(args.edge_prob_grid)
    chi_scale_grid = parse_float_grid(args.chi_scale_grid)
    noise_grid = parse_float_grid(args.noise_grid)
    phi_shock_grid = parse_float_grid(args.phi_shock_grid)

    profile_rows: list[dict[str, Any]] = []
    for block_idx, block in enumerate(blocks, start=1):
        dataset_id = str(block["dataset_id"])
        n_nodes = int(block["n_nodes"])
        steps = int(block["steps"])
        for seed in block["seeds"]:
            cfg = build_cfg(args, n_nodes=n_nodes, steps=steps, seed=seed)
            cases = make_cases(
                edge_prob_grid=edge_prob_grid,
                chi_scale_grid=chi_scale_grid,
                noise_grid=noise_grid,
                phi_shock_grid=phi_shock_grid,
                base_seed=seed,
                prefix=f"B{block_idx:02d}_S{seed}_",
            )
            for case in cases:
                profile_rows.append(
                    run_profile(
                        cfg=cfg,
                        dataset_id=dataset_id,
                        seed=seed,
                        case=case,
                        comparator_mode=args.comparator_mode,
                        sigma_median_max=args.sigma_median_max,
                        sigma_p90_max=args.sigma_p90_max,
                        sigma_max_max=args.sigma_max_max,
                        global_p90_max=args.global_p90_max,
                        global_max_max=args.global_max_max,
                        chi_max_max=args.chi_max_max,
                        phi_max_max=args.phi_max_max,
                    )
                )

    profile_fields = [
        "dataset_id",
        "comparator_mode",
        "seed",
        "n_nodes",
        "steps",
        "case_id",
        "case_seed",
        "edge_prob",
        "chi_scale",
        "noise_level",
        "phi_shock",
        "samples_per_var",
        "sigma_abs_median",
        "sigma_abs_p90",
        "sigma_abs_max",
        "chi_abs_p90",
        "chi_abs_max",
        "phi_abs_p90",
        "phi_abs_max",
        "global_abs_median",
        "global_abs_p90",
        "global_abs_max",
        "gate_sigma_median",
        "gate_sigma_p90",
        "gate_sigma_max",
        "gate_global_p90",
        "gate_global_max",
        "gate_chi_max",
        "gate_phi_max",
        "all_pass",
    ]
    profile_csv = out_dir / "profile_residuals.csv"
    write_csv(profile_csv, profile_rows, profile_fields)

    summary_rows: list[dict[str, Any]] = []
    dataset_ids = sorted({r["dataset_id"] for r in profile_rows})
    for ds in dataset_ids:
        rows = [r for r in profile_rows if r["dataset_id"] == ds]
        summary_rows.append(summarize_dataset(rows, ds))
    summary_rows.append(summarize_dataset(profile_rows, "ALL"))

    summary_fields = [
        "dataset_id",
        "profiles_total",
        "profiles_pass",
        "profiles_fail",
        "pass_rate",
        "profile_sigma_abs_median_median",
        "profile_sigma_abs_p90_median",
        "profile_global_abs_p90_median",
        "profile_sigma_abs_max_max",
        "profile_global_abs_max_max",
        "profile_chi_abs_max_max",
        "profile_phi_abs_max_max",
        "all_pass",
    ]
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, summary_rows, summary_fields)

    all_total = len(profile_rows)
    all_pass = sum(1 for r in profile_rows if r["all_pass"] == "pass")
    all_fail = all_total - all_pass
    report_lines = [
        f"# QNG EL Consistency Report ({mode_tag})",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- comparator_mode: `{mode_tag}`",
        f"- profiles_total: `{all_total}`",
        f"- profiles_pass: `{all_pass}`",
        f"- profiles_fail: `{all_fail}`",
        "",
        "## Locked Thresholds",
        "",
        f"- `sigma_abs_median <= {args.sigma_median_max}`",
        f"- `sigma_abs_p90 <= {args.sigma_p90_max}`",
        f"- `sigma_abs_max <= {args.sigma_max_max}`",
        f"- `global_abs_p90 <= {args.global_p90_max}`",
        f"- `global_abs_max <= {args.global_max_max}`",
        f"- `chi_abs_max <= {args.chi_max_max}`",
        f"- `phi_abs_max <= {args.phi_max_max}`",
        "",
        "## Dataset Summary",
        "",
    ]
    for row in summary_rows:
        report_lines.append(
            f"- `{row['dataset_id']}`: pass `{row['profiles_pass']}/{row['profiles_total']}` "
            f"(rate={row['pass_rate']}), sigma_p90_med={row['profile_sigma_abs_p90_median']}, "
            f"global_max_max={row['profile_global_abs_max_max']}, all_pass={row['all_pass']}"
        )
    report_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `v2` mode: residual `R = U_current - U_EL` using two one-step implementations.",
            "- `v1` mode: legacy self-check behavior (kept for historical reproducibility).",
            "- `v2` global metric uses joint residual `max(|R_sigma|, |R_chi|, |R_phi|)`.",
            "- `v1` global metric preserves legacy concatenation behavior.",
        ]
    )
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    now_utc = datetime.now(timezone.utc).isoformat()
    manifest = {
        "generated_utc": now_utc,
        "test_id": f"qng-foundation-stability-tests-{mode_tag}",
        "policy_id": f"qng-foundation-stability-tests-{mode_tag}",
        "comparator_mode": mode_tag,
        "blocks": blocks,
        "grids": {
            "edge_prob_grid": edge_prob_grid,
            "chi_scale_grid": chi_scale_grid,
            "noise_grid": noise_grid,
            "phi_shock_grid": phi_shock_grid,
        },
        "thresholds": {
            "sigma_median_max": args.sigma_median_max,
            "sigma_p90_max": args.sigma_p90_max,
            "sigma_max_max": args.sigma_max_max,
            "global_p90_max": args.global_p90_max,
            "global_max_max": args.global_max_max,
            "chi_max_max": args.chi_max_max,
            "phi_max_max": args.phi_max_max,
        },
        "artifacts": {
            "profile_residuals_csv": as_repo_rel(profile_csv),
            "summary_csv": as_repo_rel(summary_csv),
            "report_md": as_repo_rel(report_md),
        },
        "references": {
            "prereg_doc": as_repo_rel(prereg_doc) if prereg_doc.exists() else "",
            "foundation_doc": as_repo_rel(DEFAULT_FOUNDATION_DOC) if DEFAULT_FOUNDATION_DOC.exists() else "",
            "action_doc": as_repo_rel(DEFAULT_ACTION_DOC) if DEFAULT_ACTION_DOC.exists() else "",
            "update_doc": as_repo_rel(DEFAULT_UPDATE_DOC) if DEFAULT_UPDATE_DOC.exists() else "",
        },
    }
    ref_hashes: dict[str, str] = {}
    for key, value in manifest["references"].items():
        if not value:
            continue
        p = Path(value)
        if not p.is_absolute():
            p = ROOT / p
        if p.exists():
            ref_hashes[key] = sha256_file(p)
    if ref_hashes:
        manifest["reference_hashes"] = ref_hashes

    manifest_json = out_dir / "manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run_log = [
        f"qng-el-consistency-{mode_tag}",
        f"generated_utc={now_utc}",
        f"comparator_mode={mode_tag}",
        f"out_dir={out_dir.as_posix()}",
        f"profiles_total={all_total}",
        f"profiles_pass={all_pass}",
        f"profiles_fail={all_fail}",
        f"block_specs={args.block_specs}",
        f"edge_prob_grid={args.edge_prob_grid}",
        f"chi_scale_grid={args.chi_scale_grid}",
        f"noise_grid={args.noise_grid}",
        f"phi_shock_grid={args.phi_shock_grid}",
    ]
    (out_dir / "run-log.txt").write_text("\n".join(run_log) + "\n", encoding="utf-8")

    print(f"profile_csv: {profile_csv.as_posix()}")
    print(f"summary_csv: {summary_csv.as_posix()}")
    print(f"report_md: {report_md.as_posix()}")
    print(f"manifest_json: {manifest_json.as_posix()}")

    if args.strict_exit and all_fail > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
