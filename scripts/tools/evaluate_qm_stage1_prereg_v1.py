#!/usr/bin/env python3
"""
Evaluate QM-Stage-1 prereg summary outputs (v1).

Reporting-only by default:
- no gate formula or threshold edits
- aggregates pass/fail and runtime stability for G17..G20
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "qm-stage1-eval-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate QM-Stage-1 prereg summary (v1).")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="qm-stage1-eval-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--require-zero-rc", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--min-all-pass-rate", type=float, default=0.0)
    return p.parse_args()


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_path.exists():
        raise FileNotFoundError(f"summary not found: {summary_path}")

    rows = read_csv(summary_path)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    strict_datasets = set(parse_csv_list(args.strict_datasets))
    if strict_datasets:
        eval_rows = [r for r in rows if str(r.get("dataset_id", "")) in strict_datasets]
    else:
        eval_rows = rows
    if not eval_rows:
        raise RuntimeError("no rows after dataset filter")

    n = len(eval_rows)
    g17_pass = sum(1 for r in eval_rows if norm_status(r.get("g17_status", "")) == "pass")
    g18_pass = sum(1 for r in eval_rows if norm_status(r.get("g18_status", "")) == "pass")
    g19_pass = sum(1 for r in eval_rows if norm_status(r.get("g19_status", "")) == "pass")
    g20_pass = sum(1 for r in eval_rows if norm_status(r.get("g20_status", "")) == "pass")
    lane_pass = sum(1 for r in eval_rows if norm_status(r.get("all_pass_qm_lane", "")) == "pass")
    rc_fail_profiles = sum(
        1
        for r in eval_rows
        if any(int(str(r.get(k, "1"))) != 0 for k in ("g17_rc", "g18_rc", "g19_rc", "g20_rc"))
    )

    all_pass_rate = lane_pass / max(1, n)
    checks = {
        "zero_rc_failures": (rc_fail_profiles == 0) if args.require_zero_rc else True,
        "min_all_pass_rate": all_pass_rate >= args.min_all_pass_rate,
    }
    decision = "PASS" if all(checks.values()) else "HOLD"

    ds_rows: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in eval_rows}):
        sub = [r for r in eval_rows if str(r.get("dataset_id", "")) == ds]
        m = len(sub)
        ds_rows.append(
            {
                "dataset_id": ds,
                "n_profiles": m,
                "g17_pass": sum(1 for r in sub if norm_status(r.get("g17_status", "")) == "pass"),
                "g18_pass": sum(1 for r in sub if norm_status(r.get("g18_status", "")) == "pass"),
                "g19_pass": sum(1 for r in sub if norm_status(r.get("g19_status", "")) == "pass"),
                "g20_pass": sum(1 for r in sub if norm_status(r.get("g20_status", "")) == "pass"),
                "qm_lane_pass": sum(1 for r in sub if norm_status(r.get("all_pass_qm_lane", "")) == "pass"),
                "rc_fail_profiles": sum(
                    1
                    for r in sub
                    if any(int(str(r.get(k, "1"))) != 0 for k in ("g17_rc", "g18_rc", "g19_rc", "g20_rc"))
                ),
            }
        )

    write_csv(out_dir / "dataset_summary.csv", ds_rows, list(ds_rows[0].keys()))

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": summary_path.as_posix(),
        "datasets": sorted({str(r.get("dataset_id", "")) for r in eval_rows}),
        "profiles": n,
        "totals": {
            "g17_pass": g17_pass,
            "g18_pass": g18_pass,
            "g19_pass": g19_pass,
            "g20_pass": g20_pass,
            "qm_lane_pass": lane_pass,
            "rc_fail_profiles": rc_fail_profiles,
            "all_pass_rate": round(all_pass_rate, 6),
        },
        "criteria": {
            "require_zero_rc": bool(args.require_zero_rc),
            "min_all_pass_rate": args.min_all_pass_rate,
        },
        "checks": checks,
        "decision": decision,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# QM-Stage-1 Evaluation Report (v1)",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- source_summary_csv: `{summary_path.as_posix()}`",
        f"- decision: `{decision}`",
        "",
        "## Totals",
        "",
        f"- profiles: `{n}`",
        f"- g17_pass: `{g17_pass}/{n}`",
        f"- g18_pass: `{g18_pass}/{n}`",
        f"- g19_pass: `{g19_pass}/{n}`",
        f"- g20_pass: `{g20_pass}/{n}`",
        f"- qm_lane_pass: `{lane_pass}/{n}`",
        f"- all_pass_rate: `{all_pass_rate:.6f}`",
        f"- rc_fail_profiles: `{rc_fail_profiles}`",
        "",
        "## Criteria Checks",
        "",
        f"- zero_rc_failures: `{'true' if checks['zero_rc_failures'] else 'false'}`",
        f"- min_all_pass_rate({args.min_all_pass_rate}): `{'true' if checks['min_all_pass_rate'] else 'false'}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
