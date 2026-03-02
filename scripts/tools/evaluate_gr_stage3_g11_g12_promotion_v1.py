#!/usr/bin/env python3
"""
Evaluate promotion criteria for Stage-3 G11/G12 candidate-v2 package.

Reporting-only evaluator:
- no gate math edits
- compares v1 vs v2 statuses from candidate summary.csv
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
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage3-g11-g12-promotion-eval-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-3 G11/G12 candidate-v2 promotion criteria.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="gr-stage3-g11-g12-promotion-v1")
    p.add_argument("--strict-datasets", default="")
    p.add_argument("--require-zero-degraded", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-net-uplift", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--require-per-dataset-nondegrade", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def parse_csv_list(text: str) -> list[str]:
    return [x.strip() for x in text.split(",") if x.strip()]


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
    def v2_fail(self) -> int:
        return self.n - self.v2_pass

    @property
    def uplift_pp(self) -> float:
        if self.n == 0:
            return 0.0
        return 100.0 * (self.v2_pass - self.v1_pass) / self.n

    @property
    def failcase_uplift_pp(self) -> float:
        if self.v1_fail == 0:
            return 0.0
        return 100.0 * self.improved / self.v1_fail


def compute_totals(rows: list[dict[str, str]], v1_key: str, v2_key: str) -> Totals:
    n = len(rows)
    v1_pass = sum(1 for r in rows if norm_status(r.get(v1_key, "")) == "pass")
    v2_pass = sum(1 for r in rows if norm_status(r.get(v2_key, "")) == "pass")
    improved = sum(
        1
        for r in rows
        if norm_status(r.get(v1_key, "")) == "fail"
        and norm_status(r.get(v2_key, "")) == "pass"
    )
    degraded = sum(
        1
        for r in rows
        if norm_status(r.get(v1_key, "")) == "pass"
        and norm_status(r.get(v2_key, "")) == "fail"
    )
    return Totals(n=n, v1_pass=v1_pass, v2_pass=v2_pass, improved=improved, degraded=degraded)


def evaluate_gate(
    rows: list[dict[str, str]],
    gate_name: str,
    v1_key: str,
    v2_key: str,
    require_zero_degraded: bool,
    require_net_uplift: bool,
    require_per_dataset_nondegrade: bool,
) -> dict[str, Any]:
    totals = compute_totals(rows, v1_key, v2_key)
    datasets = sorted({r.get("dataset_id", "").strip().upper() for r in rows if r.get("dataset_id", "").strip()})

    ds_rows: list[dict[str, Any]] = []
    per_dataset_ok = True
    for ds in datasets:
        sub = [r for r in rows if r.get("dataset_id", "").strip().upper() == ds]
        t = compute_totals(sub, v1_key, v2_key)
        ok = t.v2_pass >= t.v1_pass
        per_dataset_ok = per_dataset_ok and ok
        ds_rows.append(
            {
                "gate": gate_name,
                "dataset_id": ds,
                "n": t.n,
                "v1_pass": t.v1_pass,
                "v2_pass": t.v2_pass,
                "improved": t.improved,
                "degraded": t.degraded,
                "uplift_pp": f"{t.uplift_pp:.3f}",
                "failcase_uplift_pp": f"{t.failcase_uplift_pp:.3f}",
                "nondegrade_pass": bool_str(ok),
            }
        )

    checks = {
        "zero_degraded": (not require_zero_degraded) or (totals.degraded == 0),
        "net_uplift_failcases": (not require_net_uplift) or (totals.improved > totals.degraded),
        "per_dataset_nondegrade": (not require_per_dataset_nondegrade) or per_dataset_ok,
    }
    decision = all(checks.values())
    return {
        "gate": gate_name,
        "totals": totals,
        "checks": checks,
        "decision": decision,
        "dataset_rows": ds_rows,
    }


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

    strict_datasets = sorted([d.upper() for d in parse_csv_list(args.strict_datasets)])
    datasets = sorted({r.get("dataset_id", "").strip().upper() for r in rows if r.get("dataset_id", "").strip()})
    if strict_datasets and datasets != strict_datasets:
        raise ValueError(f"strict dataset mismatch: expected {strict_datasets}, got {datasets}")

    g11_eval = evaluate_gate(
        rows=rows,
        gate_name="G11",
        v1_key="g11_v1_status",
        v2_key="g11_v2_status",
        require_zero_degraded=args.require_zero_degraded,
        require_net_uplift=args.require_net_uplift,
        require_per_dataset_nondegrade=args.require_per_dataset_nondegrade,
    )
    g12_eval = evaluate_gate(
        rows=rows,
        gate_name="G12",
        v1_key="g12_v1_status",
        v2_key="g12_v2_status",
        require_zero_degraded=args.require_zero_degraded,
        require_net_uplift=args.require_net_uplift,
        require_per_dataset_nondegrade=args.require_per_dataset_nondegrade,
    )
    stage3_eval = evaluate_gate(
        rows=rows,
        gate_name="STAGE3",
        v1_key="stage3_v1_status",
        v2_key="stage3_v2_status",
        require_zero_degraded=args.require_zero_degraded,
        require_net_uplift=args.require_net_uplift,
        require_per_dataset_nondegrade=args.require_per_dataset_nondegrade,
    )

    overall_pass = bool(g11_eval["decision"] and g12_eval["decision"] and stage3_eval["decision"])

    ds_rows = g11_eval["dataset_rows"] + g12_eval["dataset_rows"] + stage3_eval["dataset_rows"]
    write_csv(
        out_dir / "dataset_summary.csv",
        ds_rows,
        list(ds_rows[0].keys()) if ds_rows else ["gate", "dataset_id"],
    )

    def totals_json(ev: dict[str, Any]) -> dict[str, Any]:
        t: Totals = ev["totals"]
        return {
            "n": t.n,
            "v1_pass": t.v1_pass,
            "v2_pass": t.v2_pass,
            "v1_fail": t.v1_fail,
            "v2_fail": t.v2_fail,
            "improved": t.improved,
            "degraded": t.degraded,
            "uplift_pp": round(t.uplift_pp, 6),
            "failcase_uplift_pp": round(t.failcase_uplift_pp, 6),
        }

    report = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": summary_csv.as_posix(),
        "datasets": datasets,
        "criteria": {
            "require_zero_degraded": args.require_zero_degraded,
            "require_net_uplift": args.require_net_uplift,
            "require_per_dataset_nondegrade": args.require_per_dataset_nondegrade,
        },
        "g11": {
            "totals": totals_json(g11_eval),
            "checks": g11_eval["checks"],
            "decision": bool(g11_eval["decision"]),
        },
        "g12": {
            "totals": totals_json(g12_eval),
            "checks": g12_eval["checks"],
            "decision": bool(g12_eval["decision"]),
        },
        "stage3": {
            "totals": totals_json(stage3_eval),
            "checks": stage3_eval["checks"],
            "decision": bool(stage3_eval["decision"]),
        },
        "overall_decision": "PASS" if overall_pass else "FAIL",
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# GR Stage-3 G11/G12 Candidate-v2 Promotion Eval")
    lines.append("")
    lines.append(f"- eval_id: `{args.eval_id}`")
    lines.append(f"- generated_utc: `{report['generated_utc']}`")
    lines.append(f"- source_summary_csv: `{summary_csv.as_posix()}`")
    lines.append(f"- overall_decision: `{report['overall_decision']}`")
    lines.append("")
    lines.append("## Gate Decisions")
    lines.append("")
    for name, ev in [("G11", g11_eval), ("G12", g12_eval), ("STAGE3", stage3_eval)]:
        t: Totals = ev["totals"]
        decision_text = "PASS" if ev["decision"] else "FAIL"
        lines.append(
            f"- {name}: decision={decision_text}, "
            f"v1_pass={t.v1_pass}, v2_pass={t.v2_pass}, improved={t.improved}, degraded={t.degraded}, "
            f"uplift_pp={t.uplift_pp:.3f}, failcase_uplift_pp={t.failcase_uplift_pp:.3f}"
        )
        lines.append(
            f"  checks: zero_degraded={bool_str(ev['checks']['zero_degraded'])}, "
            f"net_uplift_failcases={bool_str(ev['checks']['net_uplift_failcases'])}, "
            f"per_dataset_nondegrade={bool_str(ev['checks']['per_dataset_nondegrade'])}"
        )
    lines.append("")
    lines.append("## Dataset Summary")
    lines.append("")
    lines.append("| gate | dataset | n | v1_pass | v2_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in ds_rows:
        lines.append(
            f"| {r['gate']} | {r['dataset_id']} | {r['n']} | {r['v1_pass']} | {r['v2_pass']} | "
            f"{r['improved']} | {r['degraded']} | {r['uplift_pp']} | {r['failcase_uplift_pp']} | {r['nondegrade_pass']} |"
        )
    lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

