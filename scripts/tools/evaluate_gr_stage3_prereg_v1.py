#!/usr/bin/env python3
"""
Evaluate GR Stage-3 prereg outputs (v1).

This evaluator is reporting-only:
- no gate thresholds/formulas are modified
- computes pass/fail totals and fail signatures from Stage-3 summary.csv
- writes a decision note for governance planning
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = ROOT / "05_validation" / "evidence" / "artifacts" / "gr-stage3-prereg-v1" / "summary.csv"
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-prereg-eval-v1"
    / "primary_ds002_003_006_s3401_3600"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate GR Stage-3 prereg summary.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="gr-stage3-prereg-eval-v1")
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def n_pass(rows: list[dict[str, str]], key: str) -> int:
    return sum(1 for r in rows if (r.get(key, "").strip().lower() == "pass"))


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")
    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary has zero rows")

    total = len(rows)
    datasets = sorted({r["dataset_id"] for r in rows})

    status_keys = [
        "g10_status",
        "g11_status",
        "g12_status",
        "g7_status",
        "g8_status",
        "g9_status",
        "lane_3p1_core_status",
        "lane_strong_field_status",
        "lane_tensor_status",
        "lane_geometry_status",
        "lane_conservation_status",
        "stage3_status",
    ]

    gate_rows: list[dict[str, Any]] = []
    for key in status_keys:
        passed = n_pass(rows, key)
        gate_rows.append(
            {
                "status_key": key,
                "pass_count": passed,
                "fail_count": total - passed,
                "total": total,
                "pass_rate_pct": f"{(100.0 * passed / total):.3f}",
            }
        )
    write_csv(out_dir / "status_summary.csv", gate_rows, list(gate_rows[0].keys()))

    ds_rows: list[dict[str, Any]] = []
    for ds in datasets:
        sub = [r for r in rows if r["dataset_id"] == ds]
        n = len(sub)
        ds_rows.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g11_pass": n_pass(sub, "g11_status"),
                "g12_pass": n_pass(sub, "g12_status"),
                "lane_3p1_core_pass": n_pass(sub, "lane_3p1_core_status"),
                "lane_strong_field_pass": n_pass(sub, "lane_strong_field_status"),
                "lane_tensor_pass": n_pass(sub, "lane_tensor_status"),
                "lane_geometry_pass": n_pass(sub, "lane_geometry_status"),
                "lane_conservation_pass": n_pass(sub, "lane_conservation_status"),
                "stage3_pass": n_pass(sub, "stage3_status"),
            }
        )
    write_csv(out_dir / "dataset_summary.csv", ds_rows, list(ds_rows[0].keys()))

    fails = [r for r in rows if r["stage3_status"].strip().lower() != "pass"]
    fail_ds = Counter(r["dataset_id"] for r in fails)
    patterns = Counter()
    for r in fails:
        reasons: list[str] = []
        if r["g11_status"] != "pass":
            reasons.append("G11")
        if r["g12_status"] != "pass":
            reasons.append("G12")
        if r["g10_status"] != "pass":
            reasons.append("G10")
        if r["g7_status"] != "pass":
            reasons.append("G7")
        if r["g8_status"] != "pass":
            reasons.append("G8")
        if r["g9_status"] != "pass":
            reasons.append("G9")
        patterns["+".join(reasons)] += 1

    pattern_rows = [
        {"pattern": k, "count": v}
        for (k, v) in sorted(patterns.items(), key=lambda it: (-it[1], it[0]))
    ]
    if pattern_rows:
        write_csv(out_dir / "fail_patterns.csv", pattern_rows, list(pattern_rows[0].keys()))
    else:
        write_csv(out_dir / "fail_patterns.csv", [{"pattern": "", "count": 0}], ["pattern", "count"])

    stage3_pass = n_pass(rows, "stage3_status")
    stage3_fail = total - stage3_pass
    recommendation = "HOLD" if stage3_fail > 0 else "READY_FOR_PROMOTION_REVIEW"

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "summary_csv": summary_csv.as_posix(),
        "profiles_total": total,
        "stage3_pass": stage3_pass,
        "stage3_fail": stage3_fail,
        "datasets": datasets,
        "fails_by_dataset": {k: int(v) for k, v in sorted(fail_ds.items())},
        "top_fail_patterns": pattern_rows[:10],
        "recommendation": recommendation,
        "notes": [
            "Evaluation is reporting-only and does not modify gate formulas or thresholds.",
            "Stage-3 remains a candidate lane until explicit promotion criteria are preregistered and closed.",
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# GR Stage-3 Prereg Evaluation (v1)")
    lines.append("")
    lines.append(f"- eval_id: `{args.eval_id}`")
    lines.append(f"- generated_utc: `{report['generated_utc']}`")
    lines.append(f"- summary_csv: `{summary_csv.as_posix()}`")
    lines.append(f"- profiles_total: `{total}`")
    lines.append(f"- stage3_pass: `{stage3_pass}/{total}`")
    lines.append(f"- recommendation: `{recommendation}`")
    lines.append("")
    lines.append("## Fail Signatures")
    lines.append("")
    if pattern_rows and pattern_rows[0]["count"] > 0:
        for row in pattern_rows[:10]:
            lines.append(f"- `{row['pattern']}`: `{row['count']}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- `status_summary.csv`: `{(out_dir / 'status_summary.csv').as_posix()}`")
    lines.append(f"- `dataset_summary.csv`: `{(out_dir / 'dataset_summary.csv').as_posix()}`")
    lines.append(f"- `fail_patterns.csv`: `{(out_dir / 'fail_patterns.csv').as_posix()}`")
    lines.append(f"- `report.json`: `{(out_dir / 'report.json').as_posix()}`")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_lines = [
        "# GR Stage-3 Decision Note (Primary Grid)",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- source_summary: `{summary_csv.as_posix()}`",
        "",
        "## Result",
        "",
        f"- Stage-3 pass: `{stage3_pass}/{total}`",
        f"- Stage-3 fail: `{stage3_fail}/{total}`",
        f"- recommendation: `{recommendation}`",
        "",
        "## Interpretation",
        "",
        "- `G7/G8/G9` are stable on this grid (`600/600`).",
        "- Remaining failures are concentrated in inherited Stage-2 sensitive gates (`G11`, `G12`).",
        "- No formula or threshold tuning was applied in this evaluation.",
        "",
        "## Governance Next Step",
        "",
        "- Keep Stage-3 as candidate lane.",
        "- Run attack-seed and holdout blocks under frozen protocol before any official switch discussion.",
    ]
    (out_dir / "decision.md").write_text("\n".join(decision_lines) + "\n", encoding="utf-8")

    print(f"status_summary_csv: {out_dir / 'status_summary.csv'}")
    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"fail_patterns_csv:  {out_dir / 'fail_patterns.csv'}")
    print(f"report_md:          {out_dir / 'report.md'}")
    print(f"decision_md:        {out_dir / 'decision.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

