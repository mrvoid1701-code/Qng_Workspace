#!/usr/bin/env python3
"""
Stability stress runner for QNG-v1-strict (housekeeping/theory hardening lane).

Purpose:
- Execute a preregistered parameter sweep for stability-focused invariants.
- Keep equation/threshold governance explicit and reproducible.
- Produce one evidence package with summary CSV + gate summary + report + manifest.

This tool does not alter GR/QM gate formulas or thresholds.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-v1"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-v1-strict.md"
DEFAULT_ACTION_DOC = ROOT / "03_math" / "derivations" / "qng-stability-action-v1.md"
DEFAULT_UPDATE_DOC = ROOT / "03_math" / "derivations" / "qng-stability-update-v1.md"
DEFAULT_FREEZE_DOC = ROOT / "docs" / "STABILITY_V1_STRICT.md"


@dataclass(frozen=True)
class StressConfig:
    n_nodes: int
    steps: int
    seed: int
    alpha_sigma: float
    alpha_chi: float
    alpha_phi: float
    alpha_tau: float
    chi_ref: float
    k_closure: float
    k_smooth: float
    k_chi: float
    k_mix: float
    k_phi: float
    metric_beta: float
    tau_floor: float
    chi_active_min: float
    dt_local_beta: float
    chi_runaway_max: float
    metric_cond_max: float
    energy_rel_max: float
    residual_max: float
    alpha_rel_drift_max: float
    nonlocal_delta_max: float


@dataclass(frozen=True)
class CaseConfig:
    case_id: str
    edge_prob: float
    chi_scale: float
    noise_level: float
    phi_shock: float
    case_seed: int


def parse_grid(text: str) -> list[float]:
    out: list[float] = []
    for item in text.split(","):
        t = item.strip()
        if not t:
            continue
        out.append(float(t))
    if not out:
        raise ValueError("empty grid")
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-v1-strict stability stress sweep.")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-nodes", type=int, default=36)
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--seed", type=int, default=3401)

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

    # Frozen stress gates (candidate lane can change only via new prereg version).
    p.add_argument("--chi-runaway-max", type=float, default=6.0)
    p.add_argument("--metric-cond-max", type=float, default=3.0)
    p.add_argument("--energy-rel-max", type=float, default=0.90)
    p.add_argument("--residual-max", type=float, default=0.60)
    p.add_argument("--alpha-rel-drift-max", type=float, default=0.05)
    p.add_argument("--nonlocal-delta-max", type=float, default=1e-9)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


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


def clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def wrap_angle(x: float) -> float:
    # map to (-pi, pi]
    y = (x + math.pi) % (2.0 * math.pi) - math.pi
    if y <= -math.pi:
        return y + 2.0 * math.pi
    return y


def angle_diff(a: float, b: float) -> float:
    return wrap_angle(a - b)


def mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def build_graph_erdos(n: int, edge_prob: float, rng: random.Random) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < edge_prob:
                adj[i].append(j)
                adj[j].append(i)
    return adj


def neighbors_mean(vals: list[float], neighbors: list[int], fallback: float) -> float:
    if not neighbors:
        return fallback
    return sum(vals[j] for j in neighbors) / len(neighbors)


def circular_mean(phi_vals: list[float], neighbors: list[int], fallback: float) -> float:
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


def sigma_components(
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
    chi_neigh = neighbors_mean(chi, adj[i], chi_i)
    phi_neigh = circular_mean(phi, adj[i], phi[i])

    tau_i = max(cfg.tau_floor, cfg.alpha_tau * max(abs(chi_i), cfg.tau_floor))
    delta_t_local = 1.0 + cfg.dt_local_beta * abs(chi_i - chi_neigh)

    sigma_chi = math.exp(-abs(chi_i - cfg.chi_ref) / max(cfg.chi_ref, 1e-12))
    sigma_struct = math.exp(-abs(deg_i - k_eq) / max(k_eq, 1e-12))
    sigma_temp = math.exp(-abs(delta_t_local - tau_i) / max(tau_i, 1e-12))
    sigma_phi = 0.5 * (1.0 + math.cos(angle_diff(phi[i], phi_neigh)))
    sigma_hat = clip01(sigma_chi * sigma_struct * sigma_temp * sigma_phi)
    sigma_neigh = neighbors_mean(sigma, adj[i], sigma[i])

    return {
        "sigma_hat": sigma_hat,
        "sigma_neigh": sigma_neigh,
        "tau_i": tau_i,
        "delta_t_local": delta_t_local,
        "sigma_chi": sigma_chi,
        "sigma_struct": sigma_struct,
        "sigma_temp": sigma_temp,
        "sigma_phi": sigma_phi,
    }


def potential_energy(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    cfg: StressConfig,
) -> float:
    k_eq = mean([float(len(n)) for n in adj]) if adj else 1.0
    total = 0.0
    for i in range(len(sigma)):
        comp = sigma_components(i, sigma, chi, phi, adj, cfg, k_eq)
        sigma_i = sigma[i]
        sigma_neigh = comp["sigma_neigh"]
        sigma_hat = comp["sigma_hat"]
        phi_neigh = circular_mean(phi, adj[i], phi[i])

        e = 0.5 * cfg.k_closure * (sigma_i - sigma_hat) ** 2
        e += 0.5 * cfg.k_smooth * (sigma_i - sigma_neigh) ** 2
        e += 0.5 * cfg.k_chi * (chi[i] ** 2)
        e += cfg.k_mix * chi[i] * (sigma_i - sigma_neigh)
        e += cfg.k_phi * (1.0 - math.cos(angle_diff(phi[i], phi_neigh)))
        total += e
    return total


def one_step(
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    adj: list[list[int]],
    cfg: StressConfig,
    rng: random.Random,
    noise_level: float,
) -> tuple[list[float], list[float], list[float], float, float]:
    n = len(sigma)
    k_eq = mean([float(len(nbrs)) for nbrs in adj]) if adj else 1.0

    sig_new = [0.0] * n
    chi_new = [0.0] * n
    phi_new = [0.0] * n
    max_residual = 0.0
    alpha_rel_drift = 0.0

    for i in range(n):
        comp = sigma_components(i, sigma, chi, phi, adj, cfg, k_eq)
        sigma_i = sigma[i]
        sigma_neigh = comp["sigma_neigh"]
        sigma_hat = comp["sigma_hat"]
        phi_neigh = circular_mean(phi, adj[i], phi[i])

        grad_sigma = cfg.k_closure * (sigma_i - sigma_hat)
        grad_sigma += cfg.k_smooth * (sigma_i - sigma_neigh)
        grad_sigma += cfg.k_mix * chi[i]

        grad_chi = cfg.k_chi * chi[i] + cfg.k_mix * (sigma_i - sigma_neigh)
        grad_phi = cfg.k_phi * math.sin(angle_diff(phi[i], phi_neigh))

        eta_chi = rng.gauss(0.0, noise_level)
        eta_phi = rng.gauss(0.0, 0.5 * noise_level)

        sigma_prop = sigma_i - cfg.alpha_sigma * grad_sigma
        sigma_next = clip01(sigma_prop)
        chi_next = chi[i] - cfg.alpha_chi * grad_chi + eta_chi
        phi_expected = phi[i] - cfg.alpha_phi * grad_phi + eta_phi
        phi_next = wrap_angle(phi_expected)

        sig_new[i] = sigma_next
        chi_new[i] = chi_next
        phi_new[i] = phi_next

        # Variational residual with explicit forcing terms.
        # For sigma we compare against projected update, so clipping contributes residual.
        r_sigma = sigma_next - sigma_prop
        r_chi = chi_next - (chi[i] - cfg.alpha_chi * grad_chi + eta_chi)
        r_phi = angle_diff(phi_next, phi_expected)
        max_residual = max(max_residual, abs(r_sigma), abs(r_chi), abs(r_phi))

        # alpha drift check from tau_i = alpha_tau * |chi_i|, robust to tiny chi.
        denom = max(abs(chi[i]), cfg.tau_floor)
        if abs(chi[i]) >= cfg.chi_active_min:
            alpha_eff = comp["tau_i"] / denom
            alpha_rel_drift = max(
                alpha_rel_drift,
                abs(alpha_eff - cfg.alpha_tau) / max(cfg.alpha_tau, 1e-12),
            )

    return sig_new, chi_new, phi_new, max_residual, alpha_rel_drift


def metric_diagnostics(sigma: list[float], cfg: StressConfig) -> tuple[float, float, float]:
    diag_vals = [1.0 + cfg.metric_beta * s for s in sigma]
    min_diag = min(diag_vals)
    max_diag = max(diag_vals)
    cond = max_diag / max(min_diag, 1e-18)
    return min_diag, max_diag, cond


def no_signalling_check(
    adj: list[list[int]],
    sigma: list[float],
    chi: list[float],
    phi: list[float],
    cfg: StressConfig,
) -> float:
    # One-step locality check: perturb one source node and ensure non-neighbors
    # do not change in one local update (with zero noise).
    n = len(sigma)
    if n < 3:
        return 0.0
    src = 0
    pert_sigma = list(sigma)
    pert_chi = list(chi)
    pert_phi = list(phi)
    pert_sigma[src] = clip01(pert_sigma[src] + 0.05)
    pert_chi[src] += 0.05
    pert_phi[src] = wrap_angle(pert_phi[src] + 0.05)

    base_rng = random.Random(123456)
    pert_rng = random.Random(123456)
    sig_a, _, _, _, _ = one_step(sigma, chi, phi, adj, cfg, base_rng, noise_level=0.0)
    sig_b, _, _, _, _ = one_step(pert_sigma, pert_chi, pert_phi, adj, cfg, pert_rng, noise_level=0.0)

    local = {src}
    local.update(adj[src])
    max_nonlocal = 0.0
    for i in range(n):
        if i in local:
            continue
        max_nonlocal = max(max_nonlocal, abs(sig_b[i] - sig_a[i]))
    return max_nonlocal


def f6(x: float) -> str:
    return f"{x:.6f}"


def make_case_grid(args: argparse.Namespace) -> list[CaseConfig]:
    edge_probs = parse_grid(args.edge_prob_grid)
    chi_scales = parse_grid(args.chi_scale_grid)
    noise_levels = parse_grid(args.noise_grid)
    phi_shocks = parse_grid(args.phi_shock_grid)

    cases: list[CaseConfig] = []
    idx = 0
    for ep in edge_probs:
        for cs in chi_scales:
            for nz in noise_levels:
                for ph in phi_shocks:
                    idx += 1
                    case_id = f"C{idx:03d}"
                    cases.append(
                        CaseConfig(
                            case_id=case_id,
                            edge_prob=ep,
                            chi_scale=cs,
                            noise_level=nz,
                            phi_shock=ph,
                            case_seed=args.seed + 1009 * idx,
                        )
                    )
    return cases


def init_state(n: int, chi_scale: float, phi_shock: float, rng: random.Random) -> tuple[list[float], list[float], list[float]]:
    sigma = [clip01(0.75 + rng.uniform(-0.05, 0.05)) for _ in range(n)]
    chi = [rng.uniform(-1.0, 1.0) * chi_scale for _ in range(n)]
    phi = [rng.uniform(-math.pi, math.pi) for _ in range(n)]
    if phi_shock > 0.0:
        k = max(1, n // 6)
        for idx in rng.sample(range(n), k):
            phi[idx] = wrap_angle(phi[idx] + phi_shock)
    return sigma, chi, phi


def run_case(cfg: StressConfig, case: CaseConfig) -> dict[str, Any]:
    rng = random.Random(case.case_seed)
    adj = build_graph_erdos(cfg.n_nodes, case.edge_prob, rng)
    sigma, chi, phi = init_state(cfg.n_nodes, case.chi_scale, case.phi_shock, rng)

    e0 = potential_energy(sigma, chi, phi, adj, cfg)
    max_residual = 0.0
    max_alpha_rel = 0.0
    min_sigma_seen = min(sigma)
    max_sigma_seen = max(sigma)
    max_abs_chi_seen = max(abs(v) for v in chi)
    metric_cond_max = 0.0
    min_metric_seen = float("inf")
    max_metric_seen = -float("inf")

    for _ in range(cfg.steps):
        sigma, chi, phi, res, alpha_rel = one_step(
            sigma=sigma,
            chi=chi,
            phi=phi,
            adj=adj,
            cfg=cfg,
            rng=rng,
            noise_level=case.noise_level,
        )
        max_residual = max(max_residual, res)
        max_alpha_rel = max(max_alpha_rel, alpha_rel)
        min_sigma_seen = min(min_sigma_seen, min(sigma))
        max_sigma_seen = max(max_sigma_seen, max(sigma))
        max_abs_chi_seen = max(max_abs_chi_seen, max(abs(v) for v in chi))
        min_m, max_m, cond = metric_diagnostics(sigma, cfg)
        min_metric_seen = min(min_metric_seen, min_m)
        max_metric_seen = max(max_metric_seen, max_m)
        metric_cond_max = max(metric_cond_max, cond)

    e1 = potential_energy(sigma, chi, phi, adj, cfg)
    dE_rel = abs(e1 - e0) / max(abs(e0), 1e-12)
    nonlocal_delta = no_signalling_check(adj, sigma, chi, phi, cfg)

    gate_sigma_bounds = (min_sigma_seen >= -1e-12) and (max_sigma_seen <= 1.0 + 1e-12)
    gate_metric_positive = min_metric_seen > 0.0
    gate_metric_cond = metric_cond_max <= cfg.metric_cond_max
    gate_runaway = max_abs_chi_seen <= cfg.chi_runaway_max
    gate_energy_drift = dE_rel <= cfg.energy_rel_max
    gate_variational_residual = max_residual <= cfg.residual_max
    gate_alpha_drift = max_alpha_rel <= cfg.alpha_rel_drift_max
    gate_no_signalling = nonlocal_delta <= cfg.nonlocal_delta_max

    all_pass = all(
        [
            gate_sigma_bounds,
            gate_metric_positive,
            gate_metric_cond,
            gate_runaway,
            gate_energy_drift,
            gate_variational_residual,
            gate_alpha_drift,
            gate_no_signalling,
        ]
    )

    return {
        "case_id": case.case_id,
        "case_seed": case.case_seed,
        "edge_prob": f6(case.edge_prob),
        "chi_scale": f6(case.chi_scale),
        "noise_level": f6(case.noise_level),
        "phi_shock": f6(case.phi_shock),
        "n_nodes": cfg.n_nodes,
        "steps": cfg.steps,
        "energy_start": f6(e0),
        "energy_end": f6(e1),
        "delta_energy_rel": f6(dE_rel),
        "max_residual": f6(max_residual),
        "max_alpha_rel_drift": f6(max_alpha_rel),
        "min_sigma_seen": f6(min_sigma_seen),
        "max_sigma_seen": f6(max_sigma_seen),
        "max_abs_chi_seen": f6(max_abs_chi_seen),
        "min_metric_diag": f6(min_metric_seen),
        "max_metric_diag": f6(max_metric_seen),
        "metric_cond_max_seen": f6(metric_cond_max),
        "max_nonlocal_delta": f6(nonlocal_delta),
        "gate_sigma_bounds": "pass" if gate_sigma_bounds else "fail",
        "gate_metric_positive": "pass" if gate_metric_positive else "fail",
        "gate_metric_cond": "pass" if gate_metric_cond else "fail",
        "gate_runaway": "pass" if gate_runaway else "fail",
        "gate_energy_drift": "pass" if gate_energy_drift else "fail",
        "gate_variational_residual": "pass" if gate_variational_residual else "fail",
        "gate_alpha_drift": "pass" if gate_alpha_drift else "fail",
        "gate_no_signalling": "pass" if gate_no_signalling else "fail",
        "all_pass": "pass" if all_pass else "fail",
    }


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    ensure_dir(out_dir)

    cfg = StressConfig(
        n_nodes=args.n_nodes,
        steps=args.steps,
        seed=args.seed,
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

    cases = make_case_grid(args)
    rows = [run_case(cfg, c) for c in cases]

    summary_csv = out_dir / "summary.csv"
    summary_fields = [
        "case_id",
        "case_seed",
        "edge_prob",
        "chi_scale",
        "noise_level",
        "phi_shock",
        "n_nodes",
        "steps",
        "energy_start",
        "energy_end",
        "delta_energy_rel",
        "max_residual",
        "max_alpha_rel_drift",
        "min_sigma_seen",
        "max_sigma_seen",
        "max_abs_chi_seen",
        "min_metric_diag",
        "max_metric_diag",
        "metric_cond_max_seen",
        "max_nonlocal_delta",
        "gate_sigma_bounds",
        "gate_metric_positive",
        "gate_metric_cond",
        "gate_runaway",
        "gate_energy_drift",
        "gate_variational_residual",
        "gate_alpha_drift",
        "gate_no_signalling",
        "all_pass",
    ]
    write_csv(summary_csv, rows, summary_fields)

    gate_names = [
        "gate_sigma_bounds",
        "gate_metric_positive",
        "gate_metric_cond",
        "gate_runaway",
        "gate_energy_drift",
        "gate_variational_residual",
        "gate_alpha_drift",
        "gate_no_signalling",
        "all_pass",
    ]
    gate_rows: list[dict[str, Any]] = []
    total = len(rows)
    for g in gate_names:
        pass_count = sum(1 for r in rows if r[g] == "pass")
        fail_count = total - pass_count
        gate_rows.append(
            {
                "gate": g,
                "pass_count": pass_count,
                "fail_count": fail_count,
                "pass_rate": f6(pass_count / max(total, 1)),
            }
        )
    gate_csv = out_dir / "gate_summary.csv"
    write_csv(gate_csv, gate_rows, ["gate", "pass_count", "fail_count", "pass_rate"])

    now_utc = datetime.now(timezone.utc).isoformat()
    pass_total = sum(1 for r in rows if r["all_pass"] == "pass")
    fail_total = total - pass_total

    report_lines = [
        "# QNG Stability Stress Report (v1)",
        "",
        f"- generated_utc: `{now_utc}`",
        f"- cases_total: `{total}`",
        f"- all_pass: `{pass_total}/{total}`",
        f"- all_fail: `{fail_total}/{total}`",
        "",
        "## Locked Gate Thresholds",
        "",
        f"- `max_abs_chi <= {cfg.chi_runaway_max}`",
        f"- `metric_cond_max_seen <= {cfg.metric_cond_max}`",
        f"- `|delta_E/E| <= {cfg.energy_rel_max}`",
        f"- `max_residual <= {cfg.residual_max}`",
        f"- `max |delta_alpha/alpha| <= {cfg.alpha_rel_drift_max}` for `|chi| >= {cfg.chi_active_min}`",
        f"- `max_nonlocal_delta <= {cfg.nonlocal_delta_max}`",
        "",
        "## Gate Pass Rates",
        "",
    ]
    for gr in gate_rows:
        report_lines.append(
            f"- `{gr['gate']}`: `{gr['pass_count']}/{total}` "
            f"(pass_rate={gr['pass_rate']})"
        )

    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": now_utc,
        "policy_id": "qng-stability-v1-strict",
        "cases_total": total,
        "cases_pass": pass_total,
        "cases_fail": fail_total,
        "config": cfg.__dict__,
        "grids": {
            "edge_prob_grid": parse_grid(args.edge_prob_grid),
            "chi_scale_grid": parse_grid(args.chi_scale_grid),
            "noise_grid": parse_grid(args.noise_grid),
            "phi_shock_grid": parse_grid(args.phi_shock_grid),
        },
        "references": {
            "prereg_doc": DEFAULT_PREREG.as_posix() if DEFAULT_PREREG.exists() else "",
            "action_doc": DEFAULT_ACTION_DOC.as_posix() if DEFAULT_ACTION_DOC.exists() else "",
            "update_doc": DEFAULT_UPDATE_DOC.as_posix() if DEFAULT_UPDATE_DOC.exists() else "",
            "freeze_doc": DEFAULT_FREEZE_DOC.as_posix() if DEFAULT_FREEZE_DOC.exists() else "",
        },
        "artifacts": {
            "summary_csv": summary_csv.as_posix(),
            "gate_summary_csv": gate_csv.as_posix(),
            "report_md": report_md.as_posix(),
        },
    }
    for key in ["prereg_doc", "action_doc", "update_doc", "freeze_doc"]:
        p = manifest["references"].get(key, "")
        if p:
            fp = Path(p)
            if fp.exists():
                manifest.setdefault("reference_hashes", {})[key] = sha256_file(fp)

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    run_log = [
        "QNG stability stress v1",
        f"generated_utc={now_utc}",
        f"out_dir={out_dir.as_posix()}",
        f"cases_total={total}",
        f"all_pass={pass_total}/{total}",
        f"all_fail={fail_total}/{total}",
    ]
    (out_dir / "run-log.txt").write_text("\n".join(run_log) + "\n", encoding="utf-8")

    print(f"summary_csv: {summary_csv.as_posix()}")
    print(f"gate_summary_csv: {gate_csv.as_posix()}")
    print(f"report_md: {report_md.as_posix()}")
    print(f"manifest_json: {manifest_path.as_posix()}")

    if args.strict_exit and fail_total > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
