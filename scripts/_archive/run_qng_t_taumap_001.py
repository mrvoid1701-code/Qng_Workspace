#!/usr/bin/env python3
"""
QNG-T-TAUMAP-001

Build a real-data tau map from DS-005 trajectory rows and evaluate:
- intra-mission tau stability (where repeated mission passes exist),
- cross-mission transfer/sign consistency,
- geometry coupling against |(v.grad)gradSigma| proxy,
- negative-control separation.

Dependency policy: stdlib only.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import argparse
import csv
import json
import math
import random
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FLYBY_CSV = ROOT / "data" / "trajectory" / "flyby_ds005_real.csv"
DEFAULT_PIONEER_CSV = ROOT / "data" / "trajectory" / "pioneer_ds005_anchor.csv"
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-taumap-001"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0.0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def median(values: list[float]) -> float:
    if not values:
        return float("nan")
    return statistics.median(values)


def quantile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    xs = sorted(values)
    pos = q * (len(xs) - 1)
    i0 = int(math.floor(pos))
    i1 = int(math.ceil(pos))
    if i0 == i1:
        return xs[i0]
    w = pos - i0
    return (1.0 - w) * xs[i0] + w * xs[i1]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_key_value_csv(path: Path, payload: dict[str, str]) -> None:
    write_csv(path, ["metric", "value"], [{"metric": k, "value": v} for k, v in payload.items()])


def write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        return float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    if den <= 1e-30:
        return float("nan")
    return num / den


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-TAUMAP-001.")
    p.add_argument("--test-id", default="QNG-T-TAUMAP-001")
    p.add_argument("--dataset-id", default="DS-005")
    p.add_argument("--flyby-csv", default=str(DEFAULT_FLYBY_CSV))
    p.add_argument("--use-pioneer-anchor", action="store_true")
    p.add_argument("--pioneer-csv", default=str(DEFAULT_PIONEER_CSV))
    p.add_argument("--exclude-placeholder-holdout", action="store_true")
    p.add_argument("--seed", type=int, default=20260221)
    p.add_argument("--n-permutations", type=int, default=5000)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.append(str((ROOT / "scripts").resolve()))
    import run_qng_t_028_trajectory_real as tr  # type: ignore

    t0 = time.perf_counter()
    warnings: list[str] = []

    flyby_csv = Path(args.flyby_csv)
    if not flyby_csv.is_absolute():
        flyby_csv = (ROOT / flyby_csv).resolve()
    rows, row_warnings = tr.parse_real_csv(flyby_csv)
    warnings.extend(row_warnings)

    if args.exclude_placeholder_holdout:
        keep_rows = []
        for r in rows:
            notes = str(r.get("notes", "")).lower()
            src = str(r.get("source_ref", "")).lower()
            is_placeholder = ("placeholder" in notes) or ("placeholder" in src)
            if is_placeholder:
                continue
            keep_rows.append(r)
        warnings.append(
            f"placeholder filter active: kept {len(keep_rows)} of {len(rows)} flyby rows"
        )
        rows = keep_rows

    perigee, _, _, derived = tr.build_observations(rows)

    if args.use_pioneer_anchor:
        pioneer_csv = Path(args.pioneer_csv)
        if not pioneer_csv.is_absolute():
            pioneer_csv = (ROOT / pioneer_csv).resolve()
        p_rows, p_warnings = tr.parse_pioneer_csv(pioneer_csv)
        warnings.extend(p_warnings)
        p_perigee, _, _, _, p_derived = tr.build_pioneer_observations(p_rows)
        perigee.extend(p_perigee)
        derived.extend(p_derived)

    event_date_by_pass: dict[str, str] = {}
    for row in derived:
        pid = str(row.get("pass_id", "")).strip()
        if pid and pid not in event_date_by_pass:
            event_date_by_pass[pid] = str(row.get("event_date", "")).strip()

    science = [o for o in perigee if not (o.is_control or o.is_symmetric)]
    controls = [o for o in perigee if (o.is_control or o.is_symmetric)]
    if len(science) < 4:
        raise RuntimeError(f"Need at least 4 science rows for tau-map; got {len(science)}.")

    event_rows: list[dict[str, str]] = []
    tau_by_mission: dict[str, list[float]] = defaultdict(list)
    abs_x_science: list[float] = []
    abs_y_science: list[float] = []
    abs_tau_science: list[float] = []

    for o in science:
        if abs(o.x) <= 1e-30:
            warnings.append(f"Skipping near-zero feature row in tau map: {o.pass_id}")
            continue
        tau_hat = o.y / o.x
        abs_x = abs(o.x)
        abs_y = abs(o.y)
        abs_tau = abs(tau_hat)
        tau_by_mission[o.mission_id].append(tau_hat)
        abs_x_science.append(abs_x)
        abs_y_science.append(abs_y)
        abs_tau_science.append(abs_tau)
        event_rows.append(
            {
                "pass_id": o.pass_id,
                "mission_id": o.mission_id,
                "event_date": event_date_by_pass.get(o.pass_id, ""),
                "data_domain": o.data_domain,
                "feature_x_abs": fmt(abs_x),
                "a_obs_abs": fmt(abs_y),
                "sigma": fmt(o.sigma),
                "tau_hat": fmt(tau_hat),
                "tau_hat_abs": fmt(abs_tau),
            }
        )

    if len(event_rows) < 4:
        raise RuntimeError(f"Need at least 4 usable tau-hat rows; got {len(event_rows)}.")

    tau_all = [float(r["tau_hat"]) for r in event_rows]
    abs_tau_all = [float(r["tau_hat_abs"]) for r in event_rows]
    global_tau_median = median(tau_all)

    mission_rows: list[dict[str, str]] = []
    mission_cv_values: list[float] = []
    mission_sign_ok: list[float] = []
    for mission_id in sorted(tau_by_mission.keys()):
        vals = tau_by_mission[mission_id]
        mu = statistics.fmean(vals)
        med = median(vals)
        cv = (
            statistics.pstdev(vals) / abs(mu)
            if len(vals) >= 2 and abs(mu) > 1e-30
            else float("nan")
        )
        if math.isfinite(cv):
            mission_cv_values.append(cv)
        if abs(global_tau_median) > 1e-30 and abs(med) > 1e-30:
            mission_sign_ok.append(1.0 if (med * global_tau_median) >= 0.0 else 0.0)
        mission_rows.append(
            {
                "mission_id": mission_id,
                "n_events": str(len(vals)),
                "tau_mean": fmt(mu),
                "tau_median": fmt(med),
                "tau_p10": fmt(quantile(vals, 0.10)),
                "tau_p90": fmt(quantile(vals, 0.90)),
                "tau_cv": fmt(cv),
            }
        )

    # Geometry coupling: |a_obs| vs |feature_x|.
    geometry_r = pearson(abs_x_science, abs_y_science)
    rng = random.Random(args.seed)
    n_perm = max(500, args.n_permutations)
    ge_count = 0
    for _ in range(n_perm):
        x_perm = abs_x_science[:]
        rng.shuffle(x_perm)
        r_perm = pearson(x_perm, abs_y_science)
        if math.isfinite(r_perm) and math.isfinite(geometry_r) and abs(r_perm) >= abs(geometry_r):
            ge_count += 1
    geometry_p = ge_count / float(n_perm)

    # Negative control separation in tau amplitude.
    control_abs_tau: list[float] = []
    for o in controls:
        if abs(o.x) <= 1e-30:
            continue
        control_abs_tau.append(abs(o.y / o.x))
    control_abs_tau_median = median(control_abs_tau) if control_abs_tau else 0.0
    science_abs_tau_median = median(abs_tau_all)
    control_to_science_ratio = (
        control_abs_tau_median / max(science_abs_tau_median, 1e-30)
        if science_abs_tau_median > 0.0
        else float("inf")
    )

    mission_cv_median = median(mission_cv_values) if mission_cv_values else float("nan")
    mission_sign_consistency = statistics.fmean(mission_sign_ok) if mission_sign_ok else float("nan")

    gates = {
        "G1_mission_stability": bool(
            mission_cv_values and math.isfinite(mission_cv_median) and mission_cv_median <= 4.0
        ),
        "G2_sign_transferability": bool(
            math.isfinite(mission_sign_consistency) and mission_sign_consistency >= (2.0 / 3.0)
        ),
        "G3_geometry_coupling": bool(
            math.isfinite(geometry_r) and geometry_r >= 0.70 and geometry_p <= 0.10
        ),
        "G4_control_separation": bool(control_to_science_ratio <= 0.25),
    }
    decision = "pass" if all(gates.values()) else "fail"

    geometry_rows = [
        {
            "metric": "pearson_abs_aobs_vs_abs_feature",
            "value": fmt(geometry_r),
        },
        {"metric": "perm_p_value", "value": fmt(geometry_p)},
        {"metric": "n_permutations", "value": str(n_perm)},
    ]
    write_csv(out_dir / "tau_event_map.csv", list(event_rows[0].keys()), event_rows)
    write_csv(out_dir / "tau_mission_summary.csv", list(mission_rows[0].keys()), mission_rows)
    write_csv(out_dir / "geometry_coupling.csv", ["metric", "value"], geometry_rows)
    write_key_value_csv(
        out_dir / "negative_controls.csv",
        {
            "n_controls": str(len(control_abs_tau)),
            "control_abs_tau_median": fmt(control_abs_tau_median),
            "science_abs_tau_median": fmt(science_abs_tau_median),
            "control_to_science_ratio": fmt(control_to_science_ratio),
        },
    )

    fit_summary = {
        "test_id": args.test_id,
        "dataset_id": args.dataset_id,
        "decision": decision,
        "n_science_events": str(len(event_rows)),
        "n_science_missions": str(len(tau_by_mission)),
        "n_controls": str(len(control_abs_tau)),
        "global_tau_median": fmt(global_tau_median),
        "global_abs_tau_median": fmt(science_abs_tau_median),
        "mission_cv_median": fmt(mission_cv_median),
        "mission_sign_consistency": fmt(mission_sign_consistency),
        "geometry_pearson_abs": fmt(geometry_r),
        "geometry_perm_p": fmt(geometry_p),
        "control_abs_tau_median": fmt(control_abs_tau_median),
        "control_to_science_ratio": fmt(control_to_science_ratio),
        "rule_pass_G1_mission_stability": str(gates["G1_mission_stability"]),
        "rule_pass_G2_sign_transferability": str(gates["G2_sign_transferability"]),
        "rule_pass_G3_geometry_coupling": str(gates["G3_geometry_coupling"]),
        "rule_pass_G4_control_separation": str(gates["G4_control_separation"]),
    }
    write_key_value_csv(out_dir / "fit-summary.csv", fit_summary)

    write_md(
        out_dir / "tau-map-report.md",
        [
            "# Tau Map Report",
            "",
            f"- decision: `{decision}`",
            f"- n_science_events: `{len(event_rows)}`",
            f"- n_science_missions: `{len(tau_by_mission)}`",
            f"- global_tau_median: `{fmt(global_tau_median)}`",
            f"- mission_cv_median: `{fmt(mission_cv_median)}`",
            f"- mission_sign_consistency: `{fmt(mission_sign_consistency)}`",
            f"- geometry_r(|a_obs|,|x|): `{fmt(geometry_r)}` (perm p=`{fmt(geometry_p)}`)",
            f"- control_to_science_abs_tau_ratio: `{fmt(control_to_science_ratio)}`",
            "",
            "## Gates",
            f"- G1 mission stability: `{'pass' if gates['G1_mission_stability'] else 'fail'}`",
            f"- G2 sign transferability: `{'pass' if gates['G2_sign_transferability'] else 'fail'}`",
            f"- G3 geometry coupling: `{'pass' if gates['G3_geometry_coupling'] else 'fail'}`",
            f"- G4 control separation: `{'pass' if gates['G4_control_separation'] else 'fail'}`",
        ],
    )

    run_log = [
        "QNG-T-TAUMAP-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_id: {args.dataset_id}",
        f"flyby_csv: {flyby_csv}",
        f"use_pioneer_anchor: {args.use_pioneer_anchor}",
        f"pioneer_csv: {args.pioneer_csv}",
        f"exclude_placeholder_holdout: {args.exclude_placeholder_holdout}",
        f"seed: {args.seed}",
        f"n_permutations: {n_perm}",
        f"duration_seconds: {fmt(time.perf_counter() - t0)}",
        f"decision: {decision}",
        "",
    ]
    if warnings:
        run_log.append("warnings:")
        for w in warnings:
            run_log.append(f"- {w}")
    write_md(out_dir / "run-log.txt", run_log)

    print(
        f"QNG tau-map run complete: decision={decision} "
        f"n_events={len(event_rows)} "
        f"tau_median={fmt(global_tau_median)} "
        f"geom_r={fmt(geometry_r)} "
        f"geom_p={fmt(geometry_p)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

