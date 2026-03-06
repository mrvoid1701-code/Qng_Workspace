#!/usr/bin/env python3
"""
Evaluate D4 Stage-2 candidate formulas v3 on multi-split strict criteria.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PER_SEED = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v3-candidates"
    / "per_seed_candidate_summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v3-candidates"
    / "evaluation-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate D4 Stage-2 candidates v3 strict multi-split criteria.")
    p.add_argument("--per-seed-csv", default=str(DEFAULT_PER_SEED))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--min-holdout-improve-vs-null-pct", type=float, default=10.0)
    p.add_argument("--max-holdout-mond-worse-pct", type=float, default=0.0)
    p.add_argument("--max-generalization-gap-pp", type=float, default=20.0)
    p.add_argument("--max-holdout-delta-aic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--max-holdout-delta-bic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def f6(x: float) -> str:
    return f"{x:.6f}"


def main() -> int:
    args = parse_args()
    per_seed_path = Path(args.per_seed_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not per_seed_path.exists():
        raise FileNotFoundError(f"per-seed csv not found: {per_seed_path}")

    rows = read_csv(per_seed_path)
    if not rows:
        raise RuntimeError("no rows in per-seed candidate summary")

    evaluated_rows: list[dict[str, Any]] = []
    for r in rows:
        holdout_improve = float(r["holdout_improve_vs_null_pct"])
        holdout_mond_worse = float(r["holdout_mond_worse_pct"])
        gen_gap = float(r["generalization_gap_pp"])
        daic = float(r["holdout_delta_aic_dual_minus_mond"])
        dbic = float(r["holdout_delta_bic_dual_minus_mond"])
        checks = {
            "holdout_improve_vs_null": holdout_improve >= float(args.min_holdout_improve_vs_null_pct),
            "holdout_not_worse_than_mond": holdout_mond_worse <= float(args.max_holdout_mond_worse_pct),
            "generalization_gap_ok": gen_gap <= float(args.max_generalization_gap_pp),
            "holdout_aic_not_worse_than_mond": daic <= float(args.max_holdout_delta_aic_dual_minus_mond),
            "holdout_bic_not_worse_than_mond": dbic <= float(args.max_holdout_delta_bic_dual_minus_mond),
        }
        decision = "PASS" if all(checks.values()) else "HOLD"
        out = dict(r)
        out.update(
            {
                "check_holdout_improve_vs_null": "pass" if checks["holdout_improve_vs_null"] else "fail",
                "check_holdout_not_worse_than_mond": "pass" if checks["holdout_not_worse_than_mond"] else "fail",
                "check_generalization_gap_ok": "pass" if checks["generalization_gap_ok"] else "fail",
                "check_holdout_aic_not_worse_than_mond": "pass"
                if checks["holdout_aic_not_worse_than_mond"]
                else "fail",
                "check_holdout_bic_not_worse_than_mond": "pass"
                if checks["holdout_bic_not_worse_than_mond"]
                else "fail",
                "seed_decision": decision,
            }
        )
        evaluated_rows.append(out)

    eval_fields = list(evaluated_rows[0].keys())
    with (out_dir / "per_seed_evaluation.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=eval_fields)
        w.writeheader()
        w.writerows(evaluated_rows)

    # Aggregate candidate decision: pass only if all seeds pass.
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for r in evaluated_rows:
        by_candidate.setdefault(str(r["candidate"]), []).append(r)

    candidate_rows: list[dict[str, Any]] = []
    for candidate in sorted(by_candidate.keys()):
        rr = by_candidate[candidate]
        n = len(rr)
        n_pass = sum(1 for x in rr if x["seed_decision"] == "PASS")
        candidate_rows.append(
            {
                "candidate": candidate,
                "n_splits": str(n),
                "n_pass": str(n_pass),
                "n_hold": str(n - n_pass),
                "pass_fraction": f6(n_pass / max(n, 1)),
                "decision": "PASS" if n_pass == n else "HOLD",
            }
        )

    with (out_dir / "candidate_decisions.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["candidate", "n_splits", "n_pass", "n_hold", "pass_fraction", "decision"]
        )
        w.writeheader()
        w.writerows(candidate_rows)

    global_decision = "PASS" if any(r["decision"] == "PASS" for r in candidate_rows) else "HOLD"
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "per_seed_csv": per_seed_path.as_posix(),
        "criteria": {
            "min_holdout_improve_vs_null_pct": float(args.min_holdout_improve_vs_null_pct),
            "max_holdout_mond_worse_pct": float(args.max_holdout_mond_worse_pct),
            "max_generalization_gap_pp": float(args.max_generalization_gap_pp),
            "max_holdout_delta_aic_dual_minus_mond": float(args.max_holdout_delta_aic_dual_minus_mond),
            "max_holdout_delta_bic_dual_minus_mond": float(args.max_holdout_delta_bic_dual_minus_mond),
            "candidate_pass_rule": "all split seeds must PASS",
        },
        "candidate_decisions": candidate_rows,
        "global_decision": global_decision,
    }
    (out_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# D4 Stage-2 Candidate Evaluation v3",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- global_decision: `{global_decision}`",
        "",
        "## Candidate Decisions",
        "",
    ]
    for r in candidate_rows:
        lines.append(
            f"- `{r['candidate']}`: {r['n_pass']}/{r['n_splits']} pass "
            f"(fraction={r['pass_fraction']}), decision={r['decision']}"
        )
    (out_dir / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"per_seed_eval_csv: {(out_dir / 'per_seed_evaluation.csv').as_posix()}")
    print(f"candidate_decisions_csv: {(out_dir / 'candidate_decisions.csv').as_posix()}")
    print(f"evaluation_json: {(out_dir / 'evaluation_report.json').as_posix()}")
    print(f"global_decision: {global_decision}")
    if args.strict_exit and global_decision != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
