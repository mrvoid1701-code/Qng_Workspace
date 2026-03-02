#!/usr/bin/env python3
"""
Evaluate promotion criteria for Stage-3 G11/G12 candidate-v3 package.

Reporting-only evaluator:
- no gate math edits
- compares official-v2 vs candidate-v3 statuses from candidate summary.csv
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
    / "gr-stage3-g11-g12-promotion-eval-v2"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-3 G11/G12 candidate-v3 promotion criteria.")
    p.add_argument("--summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--eval-id", default="gr-stage3-g11-g12-promotion-v2")
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
    v2_pass: int
    v3_pass: int
    improved: int
    degraded: int

    @property
    def v2_fail(self) -> int:
        return self.n - self.v2_pass

    @property
    def v3_fail(self) -> int:
        return self.n - self.v3_pass

    @property
    def uplift_pp(self) -> float:
        return 100.0 * (self.v3_pass - self.v2_pass) / max(1, self.n)

    @property
    def failcase_uplift_pp(self) -> float:
        return 100.0 * self.improved / max(1, self.v2_fail)


def summarize_pairs(rows: list[dict[str, str]], base_field: str, cand_field: str) -> Totals:
    n = len(rows)
    v2_pass = sum(1 for r in rows if norm_status(r.get(base_field, "")) == "pass")
    v3_pass = sum(1 for r in rows if norm_status(r.get(cand_field, "")) == "pass")
    improved = sum(
        1
        for r in rows
        if norm_status(r.get(base_field, "")) == "fail"
        and norm_status(r.get(cand_field, "")) == "pass"
    )
    degraded = sum(
        1
        for r in rows
        if norm_status(r.get(base_field, "")) == "pass"
        and norm_status(r.get(cand_field, "")) == "fail"
    )
    return Totals(n=n, v2_pass=v2_pass, v3_pass=v3_pass, improved=improved, degraded=degraded)


def per_dataset_summary(
    rows: list[dict[str, str]],
    base_field: str,
    cand_field: str,
    gate_label: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r.get("dataset_id", "")) for r in rows}):
        sub = [r for r in rows if str(r.get("dataset_id", "")) == ds]
        t = summarize_pairs(sub, base_field=base_field, cand_field=cand_field)
        out.append(
            {
                "gate": gate_label,
                "dataset_id": ds,
                "n": t.n,
                "v2_pass": t.v2_pass,
                "v3_pass": t.v3_pass,
                "improved": t.improved,
                "degraded": t.degraded,
                "uplift_pp": f"{t.uplift_pp:.6f}",
                "failcase_uplift_pp": f"{t.failcase_uplift_pp:.6f}",
                "nondegrade_pass": bool_str(t.degraded == 0),
            }
        )
    return out


def checks_for(t: Totals, ds_rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, bool]:
    zero_degraded = (t.degraded == 0) if args.require_zero_degraded else True
    net_uplift = (t.improved > 0) if args.require_net_uplift else True
    per_ds_nondegrade = all(str(r["nondegrade_pass"]) == "true" for r in ds_rows) if args.require_per_dataset_nondegrade else True
    return {
        "zero_degraded": zero_degraded,
        "net_uplift_failcases": net_uplift,
        "per_dataset_nondegrade": per_ds_nondegrade,
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

    strict_datasets = set(parse_csv_list(args.strict_datasets))
    if strict_datasets:
        rows_eval = [r for r in rows if str(r.get("dataset_id", "")) in strict_datasets]
    else:
        rows_eval = rows
    if not rows_eval:
        raise RuntimeError("no rows after strict dataset filtering")

    g11_tot = summarize_pairs(rows_eval, base_field="g11_v2_status", cand_field="g11_v3_status")
    g12_tot = summarize_pairs(rows_eval, base_field="g12_v2_status", cand_field="g12_v3_status")
    s3_tot = summarize_pairs(rows_eval, base_field="stage3_v2_status", cand_field="stage3_v3_status")

    g11_ds = per_dataset_summary(rows_eval, "g11_v2_status", "g11_v3_status", "G11")
    g12_ds = per_dataset_summary(rows_eval, "g12_v2_status", "g12_v3_status", "G12")
    s3_ds = per_dataset_summary(rows_eval, "stage3_v2_status", "stage3_v3_status", "STAGE3")
    dataset_rows = g11_ds + g12_ds + s3_ds

    checks_g11 = checks_for(g11_tot, g11_ds, args)
    checks_g12 = checks_for(g12_tot, g12_ds, args)
    checks_s3 = checks_for(s3_tot, s3_ds, args)

    decision_g11 = all(checks_g11.values())
    decision_g12 = all(checks_g12.values())
    decision_s3 = all(checks_s3.values())
    overall = decision_g11 and decision_g12 and decision_s3

    write_csv(
        out_dir / "dataset_summary.csv",
        dataset_rows,
        [
            "gate",
            "dataset_id",
            "n",
            "v2_pass",
            "v3_pass",
            "improved",
            "degraded",
            "uplift_pp",
            "failcase_uplift_pp",
            "nondegrade_pass",
        ],
    )

    report_json = {
        "eval_id": args.eval_id,
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": summary_csv.as_posix(),
        "datasets": sorted({str(r.get("dataset_id", "")) for r in rows_eval}),
        "criteria": {
            "require_zero_degraded": bool(args.require_zero_degraded),
            "require_net_uplift": bool(args.require_net_uplift),
            "require_per_dataset_nondegrade": bool(args.require_per_dataset_nondegrade),
        },
        "g11": {
            "totals": {
                "n": g11_tot.n,
                "v2_pass": g11_tot.v2_pass,
                "v3_pass": g11_tot.v3_pass,
                "v2_fail": g11_tot.v2_fail,
                "v3_fail": g11_tot.v3_fail,
                "improved": g11_tot.improved,
                "degraded": g11_tot.degraded,
                "uplift_pp": round(g11_tot.uplift_pp, 6),
                "failcase_uplift_pp": round(g11_tot.failcase_uplift_pp, 6),
            },
            "checks": checks_g11,
            "decision": decision_g11,
        },
        "g12": {
            "totals": {
                "n": g12_tot.n,
                "v2_pass": g12_tot.v2_pass,
                "v3_pass": g12_tot.v3_pass,
                "v2_fail": g12_tot.v2_fail,
                "v3_fail": g12_tot.v3_fail,
                "improved": g12_tot.improved,
                "degraded": g12_tot.degraded,
                "uplift_pp": round(g12_tot.uplift_pp, 6),
                "failcase_uplift_pp": round(g12_tot.failcase_uplift_pp, 6),
            },
            "checks": checks_g12,
            "decision": decision_g12,
        },
        "stage3": {
            "totals": {
                "n": s3_tot.n,
                "v2_pass": s3_tot.v2_pass,
                "v3_pass": s3_tot.v3_pass,
                "v2_fail": s3_tot.v2_fail,
                "v3_fail": s3_tot.v3_fail,
                "improved": s3_tot.improved,
                "degraded": s3_tot.degraded,
                "uplift_pp": round(s3_tot.uplift_pp, 6),
                "failcase_uplift_pp": round(s3_tot.failcase_uplift_pp, 6),
            },
            "checks": checks_s3,
            "decision": decision_s3,
        },
        "overall_decision": "PASS" if overall else "HOLD",
    }
    (out_dir / "report.json").write_text(json.dumps(report_json, indent=2), encoding="utf-8")

    lines = [
        "# GR Stage-3 G11/G12 Candidate-v3 Promotion Eval",
        "",
        f"- eval_id: `{args.eval_id}`",
        f"- generated_utc: `{report_json['generated_utc']}`",
        f"- source_summary_csv: `{summary_csv.as_posix()}`",
        f"- overall_decision: `{report_json['overall_decision']}`",
        "",
        "## Gate Decisions (official-v2 -> candidate-v3)",
        "",
        f"- G11: decision={'PASS' if decision_g11 else 'HOLD'}, v2_pass={g11_tot.v2_pass}, v3_pass={g11_tot.v3_pass}, improved={g11_tot.improved}, degraded={g11_tot.degraded}, uplift_pp={g11_tot.uplift_pp:.3f}, failcase_uplift_pp={g11_tot.failcase_uplift_pp:.3f}",
        f"  checks: zero_degraded={bool_str(checks_g11['zero_degraded'])}, net_uplift_failcases={bool_str(checks_g11['net_uplift_failcases'])}, per_dataset_nondegrade={bool_str(checks_g11['per_dataset_nondegrade'])}",
        f"- G12: decision={'PASS' if decision_g12 else 'HOLD'}, v2_pass={g12_tot.v2_pass}, v3_pass={g12_tot.v3_pass}, improved={g12_tot.improved}, degraded={g12_tot.degraded}, uplift_pp={g12_tot.uplift_pp:.3f}, failcase_uplift_pp={g12_tot.failcase_uplift_pp:.3f}",
        f"  checks: zero_degraded={bool_str(checks_g12['zero_degraded'])}, net_uplift_failcases={bool_str(checks_g12['net_uplift_failcases'])}, per_dataset_nondegrade={bool_str(checks_g12['per_dataset_nondegrade'])}",
        f"- STAGE3: decision={'PASS' if decision_s3 else 'HOLD'}, v2_pass={s3_tot.v2_pass}, v3_pass={s3_tot.v3_pass}, improved={s3_tot.improved}, degraded={s3_tot.degraded}, uplift_pp={s3_tot.uplift_pp:.3f}, failcase_uplift_pp={s3_tot.failcase_uplift_pp:.3f}",
        f"  checks: zero_degraded={bool_str(checks_s3['zero_degraded'])}, net_uplift_failcases={bool_str(checks_s3['net_uplift_failcases'])}, per_dataset_nondegrade={bool_str(checks_s3['per_dataset_nondegrade'])}",
        "",
        "## Dataset Summary",
        "",
        "| gate | dataset | n | v2_pass | v3_pass | improved | degraded | uplift_pp | failcase_uplift_pp | nondegrade_pass |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in dataset_rows:
        lines.append(
            f"| {r['gate']} | {r['dataset_id']} | {r['n']} | {r['v2_pass']} | {r['v3_pass']} | {r['improved']} | {r['degraded']} | {r['uplift_pp']} | {r['failcase_uplift_pp']} | {r['nondegrade_pass']} |"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"dataset_summary_csv: {out_dir / 'dataset_summary.csv'}")
    print(f"report_md:           {out_dir / 'report.md'}")
    print(f"report_json:         {out_dir / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
