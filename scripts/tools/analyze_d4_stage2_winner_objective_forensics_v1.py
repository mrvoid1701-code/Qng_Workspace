#!/usr/bin/env python3
"""
D4 Stage-2 winner objective forensics v1.

Compares strict evaluation outputs across winner lanes (v10/v11/v12 by default)
to classify persistent seed-level failure signatures without changing formulas
or thresholds.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-objective-forensics-v1"
)

DEFAULT_LANES = [
    (
        "v10",
        ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "d4-stage2-winner-v10-strict"
        / "evaluation-v1"
        / "per_seed_evaluation.csv",
    ),
    (
        "v11",
        ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "d4-stage2-winner-v11-strict"
        / "evaluation-v1"
        / "per_seed_evaluation.csv",
    ),
    (
        "v12",
        ROOT
        / "05_validation"
        / "evidence"
        / "artifacts"
        / "d4-stage2-winner-v12-strict"
        / "evaluation-v1"
        / "per_seed_evaluation.csv",
    ),
]


@dataclass
class LaneInput:
    lane_id: str
    csv_path: Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze D4 winner strict lane objective sensitivity (forensics).")
    p.add_argument(
        "--lane",
        action="append",
        default=[],
        help="Lane descriptor: lane_id=path/to/per_seed_evaluation.csv (repeatable).",
    )
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def parse_lanes(raw_lanes: list[str]) -> list[LaneInput]:
    if not raw_lanes:
        return [LaneInput(lane_id=k, csv_path=Path(v)) for k, v in DEFAULT_LANES]
    out: list[LaneInput] = []
    for token in raw_lanes:
        if "=" not in token:
            raise ValueError(f"invalid --lane '{token}' (expected lane_id=path)")
        lane_id, raw_path = token.split("=", 1)
        lane_id = lane_id.strip()
        raw_path = raw_path.strip()
        if not lane_id or not raw_path:
            raise ValueError(f"invalid --lane '{token}' (empty lane_id/path)")
        out.append(LaneInput(lane_id=lane_id, csv_path=Path(raw_path).resolve()))
    return out


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(x: str, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    lanes = parse_lanes(args.lane)
    lane_rows: dict[str, list[dict[str, str]]] = {}
    for lane in lanes:
        csv_path = lane.csv_path.resolve()
        if not csv_path.exists():
            raise FileNotFoundError(f"lane csv not found: {lane.lane_id} -> {csv_path}")
        rows = read_csv(csv_path)
        if not rows:
            raise RuntimeError(f"empty lane csv: {lane.lane_id} -> {csv_path}")
        lane_rows[lane.lane_id] = rows

    # Flatten lane+seed matrix for downstream diagnostics.
    seed_matrix: list[dict[str, Any]] = []
    lane_summary: list[dict[str, Any]] = []
    all_seeds: set[str] = set()
    fail_causes_global: dict[str, int] = {}
    for lane_id, rows in lane_rows.items():
        pass_count = 0
        hold_count = 0
        gap_values: list[float] = []
        mond_worse_values: list[float] = []
        improve_values: list[float] = []
        for r in rows:
            seed = str(r.get("split_seed", ""))
            all_seeds.add(seed)
            decision = str(r.get("seed_decision", ""))
            if decision == "PASS":
                pass_count += 1
            else:
                hold_count += 1
            gap = to_float(r.get("generalization_gap_pp", "0"))
            mond_worse = to_float(r.get("holdout_mond_worse_pct", "0"))
            improve = to_float(r.get("holdout_improve_vs_null_pct", "0"))
            gap_values.append(gap)
            mond_worse_values.append(mond_worse)
            improve_values.append(improve)

            fail_checks = []
            for k, v in r.items():
                if k.startswith("check_") and str(v).strip().lower() == "fail":
                    fail_checks.append(k)
                    fail_causes_global[k] = fail_causes_global.get(k, 0) + 1

            seed_matrix.append(
                {
                    "lane_id": lane_id,
                    "split_seed": seed,
                    "seed_decision": decision,
                    "generalization_gap_pp": f"{gap:.6f}",
                    "holdout_mond_worse_pct": f"{mond_worse:.6f}",
                    "holdout_improve_vs_null_pct": f"{improve:.6f}",
                    "failed_checks": ",".join(fail_checks),
                }
            )

        n = max(1, len(rows))
        lane_summary.append(
            {
                "lane_id": lane_id,
                "n_seeds": str(len(rows)),
                "pass_count": str(pass_count),
                "hold_count": str(hold_count),
                "pass_rate": f"{pass_count / n:.6f}",
                "avg_generalization_gap_pp": f"{sum(gap_values) / n:.6f}",
                "max_generalization_gap_pp": f"{max(gap_values):.6f}",
                "avg_holdout_mond_worse_pct": f"{sum(mond_worse_values) / n:.6f}",
                "max_holdout_mond_worse_pct": f"{max(mond_worse_values):.6f}",
                "avg_holdout_improve_vs_null_pct": f"{sum(improve_values) / n:.6f}",
            }
        )

    # Seed persistence across lanes.
    invariant_rows: list[dict[str, Any]] = []
    ordered_lanes = [x.lane_id for x in lanes]
    ordered_seeds = sorted(all_seeds, key=lambda x: int(x))
    for seed in ordered_seeds:
        decisions = []
        failed_checks = []
        gaps = []
        for lane_id in ordered_lanes:
            rows = lane_rows[lane_id]
            row = next((r for r in rows if str(r.get("split_seed", "")) == seed), None)
            if row is None:
                continue
            d = str(row.get("seed_decision", ""))
            decisions.append(d)
            gaps.append(to_float(row.get("generalization_gap_pp", "0")))
            for k, v in row.items():
                if k.startswith("check_") and str(v).strip().lower() == "fail":
                    failed_checks.append(k)

        pass_count = sum(1 for d in decisions if d == "PASS")
        hold_count = sum(1 for d in decisions if d != "PASS")
        invariant_rows.append(
            {
                "split_seed": seed,
                "lanes_seen": str(len(decisions)),
                "pass_count": str(pass_count),
                "hold_count": str(hold_count),
                "always_pass": "true" if pass_count == len(decisions) and decisions else "false",
                "always_hold": "true" if hold_count == len(decisions) and decisions else "false",
                "mean_generalization_gap_pp": f"{(sum(gaps) / max(1, len(gaps))):.6f}",
                "failed_checks_union": ",".join(sorted(set(failed_checks))),
            }
        )

    # Most frequent fail checks.
    fail_check_rows = [
        {"check_id": k, "count": str(v)}
        for k, v in sorted(fail_causes_global.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    write_csv(
        out_dir / "lane_summary.csv",
        lane_summary,
        [
            "lane_id",
            "n_seeds",
            "pass_count",
            "hold_count",
            "pass_rate",
            "avg_generalization_gap_pp",
            "max_generalization_gap_pp",
            "avg_holdout_mond_worse_pct",
            "max_holdout_mond_worse_pct",
            "avg_holdout_improve_vs_null_pct",
        ],
    )
    write_csv(
        out_dir / "seed_matrix.csv",
        seed_matrix,
        [
            "lane_id",
            "split_seed",
            "seed_decision",
            "generalization_gap_pp",
            "holdout_mond_worse_pct",
            "holdout_improve_vs_null_pct",
            "failed_checks",
        ],
    )
    write_csv(
        out_dir / "invariant_failure_summary.csv",
        invariant_rows,
        [
            "split_seed",
            "lanes_seen",
            "pass_count",
            "hold_count",
            "always_pass",
            "always_hold",
            "mean_generalization_gap_pp",
            "failed_checks_union",
        ],
    )
    write_csv(out_dir / "fail_check_frequency.csv", fail_check_rows, ["check_id", "count"])

    best_lane = max(lane_summary, key=lambda r: (int(r["pass_count"]), -to_float(r["avg_generalization_gap_pp"])))
    persistent_hold = [r for r in invariant_rows if r["always_hold"] == "true"]
    persistent_hold_seeds = ", ".join(r["split_seed"] for r in persistent_hold) if persistent_hold else "none"

    report_lines = [
        "# D4 Winner Objective Forensics v1",
        "",
        "Forensics-only comparison across strict winner lanes (no threshold/formula changes).",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- lanes: `{', '.join(ordered_lanes)}`",
        f"- best lane by pass_count: `{best_lane['lane_id']}` ({best_lane['pass_count']}/{best_lane['n_seeds']})",
        f"- persistent hold seeds across all lanes: `{persistent_hold_seeds}`",
        "",
        "## Dominant Failure Signature",
    ]
    if fail_check_rows:
        report_lines.append(
            f"- top failing check: `{fail_check_rows[0]['check_id']}` (count={fail_check_rows[0]['count']})"
        )
    else:
        report_lines.append("- none")
    report_lines.extend(
        [
            "",
            "## Interpretation",
            "- If the same seed remains HOLD across objective variants, the blocker is likely split-regime sensitivity (distribution shift), not optimizer noise.",
            "- Recommended next step: keep strict lane frozen and add a separate stratified-split methodological lane.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    summary = {
        "analysis_id": "d4-stage2-winner-objective-forensics-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lanes": ordered_lanes,
        "best_lane": best_lane["lane_id"],
        "best_lane_pass_count": int(best_lane["pass_count"]),
        "best_lane_n_seeds": int(best_lane["n_seeds"]),
        "persistent_hold_seeds": [r["split_seed"] for r in persistent_hold],
        "top_fail_check": fail_check_rows[0]["check_id"] if fail_check_rows else "",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[ok] wrote forensics package: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

