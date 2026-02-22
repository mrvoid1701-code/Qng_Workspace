#!/usr/bin/env python3
"""
QNG-T-GEODESIC-001

Metric-v3 trajectory/geodesic sanity checks:
- numerical stability of metric-driven local trajectories,
- Newtonian-direction compatibility,
- acceleration magnitude sanity in the weak-field bridge regime.

Dependency policy: stdlib only (+ existing local script module).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import math
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "qng-t-geodesic-001"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0.0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run QNG-T-GEODESIC-001.")
    p.add_argument("--test-id", default="QNG-T-GEODESIC-001")
    p.add_argument("--dataset-ids", default="DS-002,DS-003,DS-006")
    p.add_argument("--samples", type=int, default=72)
    p.add_argument("--seed", type=int, default=3401)
    p.add_argument("--steps", type=int, default=40)
    p.add_argument("--dt", type=float, default=0.05)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.append(str((ROOT / "scripts").resolve()))
    import run_qng_metric_hardening_v3 as mv3  # type: ignore

    t0 = time.perf_counter()
    warnings: list[str] = []

    ds_list = [d.strip() for d in args.dataset_ids.split(",") if d.strip()]
    if not ds_list:
        raise RuntimeError("No dataset ids provided.")

    sample_rows: list[dict[str, str]] = []
    summary_rows: list[dict[str, str]] = []

    for ds in ds_list:
        coords, sigma, adj, median_edge = mv3.build_dataset_graph(ds, args.seed)
        anchors = mv3.choose_anchors(sigma, args.samples, args.seed)
        s0 = median_edge

        cos_vals: list[float] = []
        mag_ratio_vals: list[float] = []
        stable_flags: list[int] = []
        used = 0

        for anchor in anchors:
            dist_anchor = mv3.dijkstra(adj, anchor)
            local_nodes = mv3.local_nodes_from_anchor(dist_anchor, anchor, 18)
            dmat = mv3.local_pairwise_distances(adj, local_nodes)
            chart = mv3.geodesic_tangent_chart(dmat)
            if chart is None:
                warnings.append(f"{ds}: anchor {anchor} skipped (chart failed)")
                continue

            sigma_local = [sigma[i] for i in local_nodes]
            sigma_s = mv3.smooth_sigma_local(dmat, sigma_local, s0)
            est = mv3.estimate_sigma_grad_hessian(chart, sigma_s)
            if est is None:
                warnings.append(f"{ds}: anchor {anchor} skipped (hessian fit failed)")
                continue

            grad, hess = est
            g11, g12, g22 = mv3.metric_from_sigma_hessian(
                hess[0], hess[1], hess[2], floor=1e-6, anisotropy_keep=0.4
            )
            inv = mv3.inv2x2(g11, g12, g22)
            if inv is None:
                warnings.append(f"{ds}: anchor {anchor} skipped (metric inverse failed)")
                continue

            inv11, inv12, inv22 = inv
            a_metric = (
                -(inv11 * grad[0] + inv12 * grad[1]),
                -(inv12 * grad[0] + inv22 * grad[1]),
            )
            a_newton = (-grad[0], -grad[1])
            cos_val = mv3.cosine(a_metric, a_newton)
            if math.isfinite(cos_val):
                cos_vals.append(cos_val)

            n_metric = math.hypot(a_metric[0], a_metric[1])
            n_newton = math.hypot(a_newton[0], a_newton[1])
            mag_ratio = n_metric / max(n_newton, 1e-30)
            if math.isfinite(mag_ratio):
                mag_ratio_vals.append(mag_ratio)

            # Local trajectory integration under metric-driven acceleration.
            x = 0.0
            y = 0.0
            vx = 0.0
            vy = 0.0
            path_len = 0.0
            stable = True
            for _ in range(max(1, args.steps)):
                vx_next = vx + args.dt * a_metric[0]
                vy_next = vy + args.dt * a_metric[1]
                x_next = x + args.dt * vx_next
                y_next = y + args.dt * vy_next
                step_len = math.hypot(x_next - x, y_next - y)
                path_len += step_len
                if not (
                    math.isfinite(x_next)
                    and math.isfinite(y_next)
                    and math.isfinite(vx_next)
                    and math.isfinite(vy_next)
                    and abs(x_next) < 1e6
                    and abs(y_next) < 1e6
                ):
                    stable = False
                    break
                x, y, vx, vy = x_next, y_next, vx_next, vy_next
            stable_flags.append(1 if stable else 0)
            used += 1

            sample_rows.append(
                {
                    "dataset_id": ds,
                    "anchor_id": str(anchor),
                    "cos_metric_vs_newton": fmt(cos_val),
                    "mag_ratio_metric_vs_newton": fmt(mag_ratio),
                    "stable": str(stable),
                    "final_x": fmt(x),
                    "final_y": fmt(y),
                    "path_length": fmt(path_len),
                }
            )

        if used == 0:
            raise RuntimeError(f"{ds}: no usable anchors for geodesic sanity.")

        cos_med = statistics.median(cos_vals)
        cos_p10 = quantile(cos_vals, 0.10)
        ratio_med = statistics.median(mag_ratio_vals)
        ratio_p90 = quantile(mag_ratio_vals, 0.90)
        stable_fraction = statistics.fmean(stable_flags)

        pass_g1 = stable_fraction >= 0.99
        pass_g2 = (cos_med >= 0.95) and (cos_p10 >= 0.90)
        pass_g3 = (0.50 <= ratio_med <= 3.00) and (ratio_p90 <= 3.50)
        pass_dataset = pass_g1 and pass_g2 and pass_g3

        summary_rows.append(
            {
                "dataset_id": ds,
                "n_anchors_used": str(used),
                "stable_fraction": fmt(stable_fraction),
                "cos_median": fmt(cos_med),
                "cos_p10": fmt(cos_p10),
                "mag_ratio_median": fmt(ratio_med),
                "mag_ratio_p90": fmt(ratio_p90),
                "pass_G1_stability": str(pass_g1),
                "pass_G2_newton_direction": str(pass_g2),
                "pass_G3_mag_sanity": str(pass_g3),
                "pass_dataset": str(pass_dataset),
            }
        )

    final_pass = all(r["pass_dataset"] == "True" for r in summary_rows)
    write_csv(out_dir / "trajectory_samples.csv", list(sample_rows[0].keys()), sample_rows)
    write_csv(out_dir / "dataset_summary.csv", list(summary_rows[0].keys()), summary_rows)

    checks = [
        {
            "gate_id": "G1",
            "metric": "stable_fraction_per_dataset",
            "value": "all>=0.99" if final_pass else "see dataset_summary.csv",
            "threshold": ">=0.99 each dataset",
            "status": "pass" if all(r["pass_G1_stability"] == "True" for r in summary_rows) else "fail",
        },
        {
            "gate_id": "G2",
            "metric": "cos_metric_vs_newton (median/p10)",
            "value": "see dataset_summary.csv",
            "threshold": "median>=0.95 and p10>=0.90 each dataset",
            "status": "pass" if all(r["pass_G2_newton_direction"] == "True" for r in summary_rows) else "fail",
        },
        {
            "gate_id": "G3",
            "metric": "mag_ratio_metric_vs_newton (median/p90)",
            "value": "see dataset_summary.csv",
            "threshold": "0.50<=median<=3.00 and p90<=3.50 each dataset",
            "status": "pass" if all(r["pass_G3_mag_sanity"] == "True" for r in summary_rows) else "fail",
        },
        {
            "gate_id": "FINAL",
            "metric": "decision",
            "value": "pass" if final_pass else "fail",
            "threshold": "G1&G2&G3 all pass on all datasets",
            "status": "pass" if final_pass else "fail",
        },
    ]
    write_csv(out_dir / "checks.csv", ["gate_id", "metric", "value", "threshold", "status"], checks)

    write_key_value_csv(
        out_dir / "fit-summary.csv",
        {
            "test_id": args.test_id,
            "decision": "pass" if final_pass else "fail",
            "dataset_ids": ",".join(ds_list),
            "samples": str(args.samples),
            "seed": str(args.seed),
            "steps": str(args.steps),
            "dt": fmt(args.dt),
            "rule_pass_G1_stability": str(all(r["pass_G1_stability"] == "True" for r in summary_rows)),
            "rule_pass_G2_newton_direction": str(
                all(r["pass_G2_newton_direction"] == "True" for r in summary_rows)
            ),
            "rule_pass_G3_mag_sanity": str(all(r["pass_G3_mag_sanity"] == "True" for r in summary_rows)),
        },
    )

    write_md(
        out_dir / "geodesic-report.md",
        [
            "# Geodesic / Metric Trajectory Sanity",
            "",
            f"- decision: `{'pass' if final_pass else 'fail'}`",
            f"- datasets: `{', '.join(ds_list)}`",
            f"- samples per dataset: `{args.samples}`",
            f"- integration: steps=`{args.steps}`, dt=`{fmt(args.dt)}`",
            "",
            "See `dataset_summary.csv` and `checks.csv` for gate-level values.",
        ],
    )

    run_log = [
        "QNG-T-GEODESIC-001 run log",
        f"timestamp_utc: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        f"test_id: {args.test_id}",
        f"dataset_ids: {','.join(ds_list)}",
        f"samples: {args.samples}",
        f"seed: {args.seed}",
        f"steps: {args.steps}",
        f"dt: {fmt(args.dt)}",
        f"duration_seconds: {fmt(time.perf_counter() - t0)}",
        f"decision: {'pass' if final_pass else 'fail'}",
        "",
    ]
    if warnings:
        run_log.append("warnings:")
        for w in warnings:
            run_log.append(f"- {w}")
    write_md(out_dir / "run-log.txt", run_log)

    print(
        f"QNG geodesic sanity run complete: decision={'pass' if final_pass else 'fail'} "
        f"datasets={len(summary_rows)} anchors={len(sample_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

