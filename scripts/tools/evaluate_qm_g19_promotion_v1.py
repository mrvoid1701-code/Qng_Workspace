#!/usr/bin/env python3
"""
Evaluate QM G19 candidate-v2 promotion criteria (v1).

Reporting-only evaluator:
- compares v1 vs v2 statuses from candidate summary.csv
- supports prereg-style constraints (degraded=0, per-dataset nondegrade, net uplift)
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "qm-g19-promotion-eval-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate QM G19 candidate-v2 promotion criteria.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="qm-g19-promotion-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-net-uplift", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-per-dataset-nondegrade", action=argparse.BooleanOptionalAction, default=True)
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


def bool_str(v: bool) -> str:
    return "true" if v else "false"


@dataclass(frozen=True)
class Totals:
    n: int
    v1_pass: int
    v2_pass: int
    improved: int
    degraded: int

    @property
    def v1_fail(self) -> int:
        return self.n - self.v1_pass

    @property
    def uplift_pp(self) -> float:
        return 100.0 * (self.v2_pass - self.v1_pass) / max(1, self.n)

    @property
    def failcase_uplift_pp(self) -> float:
        return 100.0 * self.improved / max(1, self.v1_fail)


def summarize(rows: list[dict[str, str]], v1_field: str, v2_field: str) -> Totals:
    n = len(rows)
    v1_pass = sum(1 for r in rows if norm_status(r.get(v1_field, "")) == "pass")
    v2_pass = sum(1 for r in rows if norm_status(r.get(v2_field, "")) == "pass")
    improved = sum(
        1 for r in rows if norm_status(r.get(v1_field, "")) == "fail" and norm_status(r.get(v2_field, "")) == "pass"
    )
    degraded = sum(
        1 for r in rows if norm_status(r.get(v1_field, "")) == "pass" and norm_status(r.get(v2_field, "")) == "fail"
    )
    return Totals(n=n, v1_pass=v1_pass, v2_pass=v2_pass, improved=improved, degraded=degraded)


def per_dataset_summary(rows: list[dict[str, str]], v1_field: str, v2_field: str, label: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in rows}):
        sub = [r for r in rows if str(r.get("dataset_id", "")) == ds]
        t = summarize(sub, v1_field, v2_field)
        out.append(
            {
                "scope": label,
                "dataset_id": ds,
                "n": t.n,
                "v1_pass": t.v1_pass,
                "v2_pass": t.v2_pass,
                "improved": t.improved,
                "degraded": t.degraded,
                "uplift_pp": f"{t.uplift_pp:.6f}",
                "failcase_uplift_pp": f"{t.failcase_uplift_pp:.6f}",
                "nondegrade_pass": bool_str(t.degraded == 0),
            }
        )
    return out


def checks_for(t: Totals, ds_rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, bool]:
    return {
        "zero_degraded": (t.degraded == 0) if args.require_zero_degraded else True,
        "net_uplift_failcases": (t.improved > 0) if args.require_net_uplift else True,
        "per_dataset_nondegrade": (
            all(str(r["nondegrade_pass"]) == "true" for r in ds_rows) if args.require_per_dataset_nondegrade else True
        ),
    }


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary csv not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    ds_filter = set(parse_csv_list(args.strict_datasets))
    eval_rows = [r for r in rows if str(r.get("dataset_id", "")) in ds_filter] if ds_filter else rows
    if not eval_rows:
        raise RuntimeError("no rows after dataset filtering")

    g19_tot = summarize(eval_rows, "g19_status_v1", "g19_status_v2")
    lane_tot = summarize(eval_rows, "all_pass_qm_lane_v1", "all_pass_qm_lane_v2")

    g19_ds = per_dataset_summary(eval_rows, "g19_status_v1", "g19_status_v2", "G19")
    lane_ds = per_dataset_summary(eval_rows, "all_pass_qm_lane_v1", "all_pass_qm_lane_v2", "QM_LANE")
    ds_rows = g19_ds + lane_ds
    write_csv(
        out_dir / "dataset_summary.csv",
        ds_rows,
        [
            "scope",
            "dataset_id",
            "n",
            "v1_pass",
            "v2_pass",
            "improved",
            "degraded",
            "uplift_pp",
            "failcase_uplift_pp",
            "nondegrade_pass",
        ],
    )

    checks_g19 = checks_for(g19_tot, g19_ds, args)
    checks_lane = checks_for(lane_tot, lane_ds, args)
    decision_g19 = all(checks_g19.values())
    decision_lane = all(checks_lane.values())
    overall = decision_g19 and decision_lane

    report_json = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": summary_csv.as_posix(),
        "datasets": sorted({str(r.get("dataset_id", "")) for r in eval_rows}),
        "criteria": {
            "require_zero_degraded": bool(args.require_zero_degraded),
            "require_net_uplift": bool(args.require_net_uplift),
            "require_per_dataset_nondegrade": bool(args.require_per_dataset_nondegrade),
        },
        "g19": {
            "totals": {
                "n": g19_tot.n,
                "v1_pass": g19_tot.v1_pass,
                "v2_pass": g19_tot.v2_pass,
                "improved": g19_tot.improved,
                "degraded": g19_tot.degraded,
                "uplift_pp": round(g19_tot.uplift_pp, 6),
                "failcase_uplift_pp": round(g19_tot.failcase_uplift_pp, 6),
            },
            "checks": checks_g19,
            "decision": decision_g19,
        },
        "qm_lane": {
            "totals": {
                "n": lane_tot.n,
                "v1_pass": lane_tot.v1_pass,
                "v2_pass": lane_tot.v2_pass,
                "improved": lane_tot.improved,
                "degraded": lane_tot.degraded,
                "uplift_pp": round(lane_tot.uplift_pp, 6),
                "failcase_uplift_pp": round(lane_tot.failcase_uplift_pp, 6),
            },
            "checks": checks_lane,
            "decision": decision_lane,
        },
        "overall_decision": "PASS" if overall else "HOLD",
    }
    (out_dir / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    lines = [
        "# QM G19 Candidate-v2 Promotion Eval",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report_json['generated_utc']}`",
        f"- source_summary_csv: `{summary_csv.as_posix()}`",
        f"- overall_decision: `{report_json['overall_decision']}`",
        "",
        "## Scope Decisions",
        "",
        f"- G19: decision={'PASS' if decision_g19 else 'HOLD'}, v1_pass={g19_tot.v1_pass}, v2_pass={g19_tot.v2_pass}, improved={g19_tot.improved}, degraded={g19_tot.degraded}, uplift_pp={g19_tot.uplift_pp:.3f}, failcase_uplift_pp={g19_tot.failcase_uplift_pp:.3f}",
        f"  checks: zero_degraded={bool_str(checks_g19['zero_degraded'])}, net_uplift_failcases={bool_str(checks_g19['net_uplift_failcases'])}, per_dataset_nondegrade={bool_str(checks_g19['per_dataset_nondegrade'])}",
        f"- QM_LANE: decision={'PASS' if decision_lane else 'HOLD'}, v1_pass={lane_tot.v1_pass}, v2_pass={lane_tot.v2_pass}, improved={lane_tot.improved}, degraded={lane_tot.degraded}, uplift_pp={lane_tot.uplift_pp:.3f}, failcase_uplift_pp={lane_tot.failcase_uplift_pp:.3f}",
        f"  checks: zero_degraded={bool_str(checks_lane['zero_degraded'])}, net_uplift_failcases={bool_str(checks_lane['net_uplift_failcases'])}, per_dataset_nondegrade={bool_str(checks_lane['per_dataset_nondegrade'])}",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
