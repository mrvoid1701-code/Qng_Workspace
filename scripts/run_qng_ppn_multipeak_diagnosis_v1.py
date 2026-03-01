#!/usr/bin/env python3
"""
QNG G15b multi-peak diagnosis (v1).

Purpose:
- Explain why G15b-v1 can fail on multi-peak geometry while G15b-v2 remains stable.
- Reuse an existing v1/v2 sweep summary and add peak-geometry diagnostics.

Multi-peak proxy used here:
- strong secondary peak: U2/U1 >= --ratio-threshold
- separated peaks: distance(top1, top2) / bbox_diagonal >= --distance-threshold
- multi_peak_flag = both conditions true

Outputs:
- per-run table: multipeak_diagnosis.csv
- aggregate stats: multipeak_summary.json
- short report: multipeak_report.md
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from run_qng_ppn_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SUMMARY_CSV = (
    ROOT
    / "07_exports"
    / "tmp_ppn_v1v2_large_sweep"
    / "summary_v1_vs_v2_200seeds_per_dataset.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g15b-multipeak-diagnosis-v1"
)


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No rows to write")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QNG G15b multi-peak diagnosis v1.")
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV))
    parser.add_argument("--datasets", default="DS-002,DS-003,DS-006")
    parser.add_argument("--phi-scale", type=float, default=0.08)
    parser.add_argument("--ratio-threshold", type=float, default=0.98)
    parser.add_argument("--distance-threshold", type=float, default=0.10)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def fail_rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return 1.0 - (sum(int(r[key]) for r in rows) / len(rows))


def ratio_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
    }


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    datasets = set(ds.upper() for ds in parse_csv_list(args.datasets))
    rows = read_rows(summary_csv)
    rows = [r for r in rows if r.get("dataset_id", "").upper() in datasets]
    if not rows:
        raise RuntimeError("No rows matched requested datasets.")

    diag_rows: list[dict[str, Any]] = []
    for r in rows:
        ds = r["dataset_id"].upper()
        seed = int(r["seed"])

        coords, sigma, _ = build_dataset_graph(ds, seed)
        top = sorted(range(len(sigma)), key=lambda i: (-sigma[i], i))
        i1, i2 = top[0], top[1]
        s1, s2 = sigma[i1], sigma[i2]
        peak_ratio = (s2 / s1) if s1 > 0 else 0.0

        d12 = math.hypot(
            coords[i1][0] - coords[i2][0],
            coords[i1][1] - coords[i2][1],
        )
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        bbox_diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys))
        dnorm = (d12 / bbox_diag) if bbox_diag > 0 else 0.0

        multi_peak_flag = int(
            peak_ratio >= args.ratio_threshold
            and dnorm >= args.distance_threshold
        )

        diag_rows.append(
            {
                "dataset_id": ds,
                "seed": seed,
                "phi_scale": f"{args.phi_scale:.2f}",
                "g15b_v1_ratio": r["g15b_v1_ratio"],
                "g15b_v1_pass": int(r["g15b_v1_pass"]),
                "g15b_v2_ratio": r["g15b_v2_ratio"],
                "g15b_v2_pass": int(r["g15b_v2_pass"]),
                "peak_1_index": i1,
                "peak_2_index": i2,
                "peak_2_over_peak_1": f"{peak_ratio:.6f}",
                "peak_1_2_distance": f"{d12:.6f}",
                "peak_1_2_distance_norm": f"{dnorm:.6f}",
                "multi_peak_flag": multi_peak_flag,
            }
        )

    diag_csv = out_dir / "multipeak_diagnosis.csv"
    write_csv(diag_csv, diag_rows)

    summary: dict[str, Any] = {
        "config": {
            "summary_csv": str(summary_csv),
            "datasets": sorted(datasets),
            "phi_scale": args.phi_scale,
            "ratio_threshold": args.ratio_threshold,
            "distance_threshold": args.distance_threshold,
            "multi_peak_definition": (
                "multi_peak = (peak_2_over_peak_1 >= ratio_threshold) "
                "AND (peak_1_2_distance_norm >= distance_threshold)"
            ),
        },
        "datasets": {},
        "overall": {},
    }

    def aggregate(sub_rows: list[dict[str, Any]]) -> dict[str, Any]:
        mp = [x for x in sub_rows if int(x["multi_peak_flag"]) == 1]
        non = [x for x in sub_rows if int(x["multi_peak_flag"]) == 0]
        v1_vals = [float(x["g15b_v1_ratio"]) for x in sub_rows]
        v2_vals = [float(x["g15b_v2_ratio"]) for x in sub_rows]
        return {
            "n_runs": len(sub_rows),
            "n_multi_peak": len(mp),
            "n_non_multi_peak": len(non),
            "v1_fail_rate_multi_peak": fail_rate(mp, "g15b_v1_pass"),
            "v1_fail_rate_non_multi_peak": fail_rate(non, "g15b_v1_pass"),
            "v2_fail_rate_multi_peak": fail_rate(mp, "g15b_v2_pass"),
            "v2_fail_rate_non_multi_peak": fail_rate(non, "g15b_v2_pass"),
            "v1_fail_rate_lift_multi_minus_non": (
                fail_rate(mp, "g15b_v1_pass") - fail_rate(non, "g15b_v1_pass")
            ),
            "peak_ratio_stats": ratio_stats(
                [float(x["peak_2_over_peak_1"]) for x in sub_rows]
            ),
            "distance_norm_stats": ratio_stats(
                [float(x["peak_1_2_distance_norm"]) for x in sub_rows]
            ),
            "g15b_v1_ratio_stats": ratio_stats(v1_vals),
            "g15b_v2_ratio_stats": ratio_stats(v2_vals),
        }

    for ds in sorted(datasets):
        ds_rows = [x for x in diag_rows if x["dataset_id"] == ds]
        summary["datasets"][ds] = aggregate(ds_rows)

    summary["overall"] = aggregate(diag_rows)
    summary_json = out_dir / "multipeak_summary.json"
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report_md = out_dir / "multipeak_report.md"
    overall = summary["overall"]
    lines = [
        "# G15b Multi-Peak Diagnosis (v1)",
        "",
        "## Definition",
        "",
        f"- `multi_peak = (peak_2/peak_1 >= {args.ratio_threshold:.2f}) "
        f"AND (distance_norm >= {args.distance_threshold:.2f})`",
        "",
        "## Overall",
        "",
        f"- Runs: `{overall['n_runs']}`",
        f"- Multi-peak runs: `{overall['n_multi_peak']}`",
        f"- Non-multi-peak runs: `{overall['n_non_multi_peak']}`",
        f"- `v1` fail rate (multi-peak): `{overall['v1_fail_rate_multi_peak']:.3f}`",
        f"- `v1` fail rate (non-multi-peak): `{overall['v1_fail_rate_non_multi_peak']:.3f}`",
        f"- `v1` fail-rate lift (multi - non): "
        f"`{overall['v1_fail_rate_lift_multi_minus_non']:.3f}`",
        f"- `v2` fail rate (multi-peak): `{overall['v2_fail_rate_multi_peak']:.3f}`",
        f"- `v2` fail rate (non-multi-peak): `{overall['v2_fail_rate_non_multi_peak']:.3f}`",
        "",
        "## Per Dataset",
        "",
    ]

    for ds in sorted(datasets):
        ds_sum = summary["datasets"][ds]
        lines.extend(
            [
                f"### {ds}",
                f"- Runs: `{ds_sum['n_runs']}` (multi-peak: `{ds_sum['n_multi_peak']}`)",
                f"- `v1` fail multi/non: "
                f"`{ds_sum['v1_fail_rate_multi_peak']:.3f}` / "
                f"`{ds_sum['v1_fail_rate_non_multi_peak']:.3f}`",
                f"- `v2` fail multi/non: "
                f"`{ds_sum['v2_fail_rate_multi_peak']:.3f}` / "
                f"`{ds_sum['v2_fail_rate_non_multi_peak']:.3f}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Artifacts",
            "",
            f"- `{diag_csv}`",
            f"- `{summary_json}`",
        ]
    )
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote: {diag_csv}")
    print(f"wrote: {summary_json}")
    print(f"wrote: {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
