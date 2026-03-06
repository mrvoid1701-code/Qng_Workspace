#!/usr/bin/env python3
"""
Evaluate D4 Stage-2 dual-kernel run against fixed prereg criteria.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v1"
    / "d4_stage2_dual_kernel_summary.json"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v1"
    / "evaluation-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate D4 Stage-2 dual-kernel prereg criteria.")
    p.add_argument("--summary-json", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--min-holdout-improve-vs-null-pct", type=float, default=10.0)
    p.add_argument("--max-holdout-mond-worse-pct", type=float, default=20.0)
    p.add_argument("--max-generalization-gap-pp", type=float, default=25.0)
    return p.parse_args()


def get_metric(d: dict[str, Any], *keys: str) -> float:
    cur: Any = d
    for k in keys:
        cur = cur[k]
    return float(cur)


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_json).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_path.exists():
        raise FileNotFoundError(f"summary json not found: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    holdout_dual = get_metric(summary, "metrics", "holdout", "chi2_per_n_dual")
    holdout_null = get_metric(summary, "metrics", "holdout", "chi2_per_n_null")
    holdout_mond = get_metric(summary, "metrics", "holdout", "chi2_per_n_mond")
    holdout_improve = get_metric(summary, "metrics", "holdout", "improve_vs_null_pct")
    train_improve = get_metric(summary, "metrics", "train", "improve_vs_null_pct")
    generalization_gap = abs(train_improve - holdout_improve)

    mond_worse_pct = 100.0 * (holdout_dual - holdout_mond) / max(holdout_mond, 1e-12)

    checks = {
        "holdout_improve_vs_null": holdout_improve >= float(args.min_holdout_improve_vs_null_pct),
        "holdout_not_far_worse_than_mond": mond_worse_pct <= float(args.max_holdout_mond_worse_pct),
        "generalization_gap_ok": generalization_gap <= float(args.max_generalization_gap_pp),
    }
    decision = "PASS" if all(checks.values()) else "HOLD"

    report = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "summary_json": summary_path.as_posix(),
        "criteria": {
            "min_holdout_improve_vs_null_pct": float(args.min_holdout_improve_vs_null_pct),
            "max_holdout_mond_worse_pct": float(args.max_holdout_mond_worse_pct),
            "max_generalization_gap_pp": float(args.max_generalization_gap_pp),
        },
        "observed": {
            "holdout_chi2_per_n_dual": holdout_dual,
            "holdout_chi2_per_n_null": holdout_null,
            "holdout_chi2_per_n_mond": holdout_mond,
            "holdout_improve_vs_null_pct": holdout_improve,
            "holdout_mond_worse_pct": mond_worse_pct,
            "train_improve_vs_null_pct": train_improve,
            "generalization_gap_pp": generalization_gap,
        },
        "checks": checks,
        "decision": decision,
    }
    (out_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# D4 Stage-2 Dual-Kernel Evaluation (v1)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_json: `{summary_path.as_posix()}`",
        f"- decision: `{decision}`",
        "",
        "## Observed",
        "",
        f"- holdout chi2/N dual: `{holdout_dual:.6f}`",
        f"- holdout chi2/N null: `{holdout_null:.6f}`",
        f"- holdout chi2/N mond: `{holdout_mond:.6f}`",
        f"- holdout improve vs null (%): `{holdout_improve:.6f}`",
        f"- holdout mond worse (%): `{mond_worse_pct:.6f}`",
        f"- train-holdout improve gap (pp): `{generalization_gap:.6f}`",
        "",
        "## Checks",
        "",
        f"- holdout_improve_vs_null: `{checks['holdout_improve_vs_null']}`",
        f"- holdout_not_far_worse_than_mond: `{checks['holdout_not_far_worse_than_mond']}`",
        f"- generalization_gap_ok: `{checks['generalization_gap_ok']}`",
    ]
    (out_dir / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"evaluation_json: {out_dir / 'evaluation_report.json'}")
    print(f"decision: {decision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

