#!/usr/bin/env python3
"""
Run minimal stability convergence gate (v1) on a stress summary CSV.

Contract source:
- 05_validation/pre-registrations/qng-stability-convergence-v1.md
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "stability-convergence-v1"
    / "raw"
    / "summary.csv"
)
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v1"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v1.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence gate v1.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--n-nodes-field", default="n_nodes")
    p.add_argument("--metric-field", default="delta_energy_rel")
    p.add_argument("--support-field", default="energy_noether_rel")
    p.add_argument("--step-tol", type=float, default=0.002)
    p.add_argument("--min-step-pass-fraction", type=float, default=0.75)
    p.add_argument("--min-overall-improvement", type=float, default=0.005)
    p.add_argument("--support-worsen-factor-max", type=float, default=1.25)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
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


def to_float(v: Any) -> float | None:
    try:
        x = float(str(v).strip())
    except Exception:
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return x


def percentile(vals: list[float], q: float) -> float:
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    w = pos - lo
    return s[lo] + (s[hi] - s[lo]) * w


def median(vals: list[float]) -> float:
    return percentile(vals, 0.5)


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    grouped: dict[int, list[dict[str, str]]] = {}
    for r in rows:
        try:
            n = int(str(r.get(args.n_nodes_field, "")).strip())
        except Exception:
            continue
        grouped.setdefault(n, []).append(r)
    levels = sorted(grouped.keys())
    if len(levels) < 2:
        raise RuntimeError("need at least 2 n_nodes levels for convergence gate")

    level_rows: list[dict[str, Any]] = []
    med_map: dict[int, float] = {}
    support_p95_map: dict[int, float] = {}
    for n in levels:
        sub = grouped[n]
        mvals = [to_float(r.get(args.metric_field, "")) for r in sub]
        mvals = [v for v in mvals if v is not None]
        svals = [to_float(r.get(args.support_field, "")) for r in sub]
        svals = [v for v in svals if v is not None]
        if not mvals or not svals:
            raise RuntimeError(f"missing numeric values for n_nodes={n}")
        med = median(mvals)
        p95 = percentile(svals, 0.95)
        med_map[n] = med
        support_p95_map[n] = p95
        level_rows.append(
            {
                "n_nodes": n,
                "n_profiles": len(sub),
                "metric_mean": f"{sum(mvals)/len(mvals):.6f}",
                "metric_median": f"{med:.6f}",
                "metric_p95": f"{percentile(mvals, 0.95):.6f}",
                "support_mean": f"{sum(svals)/len(svals):.6f}",
                "support_median": f"{median(svals):.6f}",
                "support_p95": f"{p95:.6f}",
            }
        )

    step_rows: list[dict[str, Any]] = []
    step_pass = 0
    for i in range(len(levels) - 1):
        n0 = levels[i]
        n1 = levels[i + 1]
        d = med_map[n1] - med_map[n0]
        ok = d <= args.step_tol
        if ok:
            step_pass += 1
        step_rows.append(
            {
                "n_from": n0,
                "n_to": n1,
                "median_from": f"{med_map[n0]:.6f}",
                "median_to": f"{med_map[n1]:.6f}",
                "delta": f"{d:.6f}",
                "step_tol": f"{args.step_tol:.6f}",
                "step_pass": "true" if ok else "false",
            }
        )

    frac = step_pass / max(1, len(levels) - 1)
    n_min = levels[0]
    n_max = levels[-1]
    overall_improvement = med_map[n_min] - med_map[n_max]
    support_ratio = support_p95_map[n_max] / max(support_p95_map[n_min], 1e-12)

    checks = {
        "step_fraction": frac >= args.min_step_pass_fraction,
        "overall_improvement": overall_improvement >= args.min_overall_improvement,
        "support_sanity": support_ratio <= args.support_worsen_factor_max,
    }
    decision = "PASS" if all(checks.values()) else "FAIL"

    write_csv(
        out_dir / "level_stats.csv",
        level_rows,
        ["n_nodes", "n_profiles", "metric_mean", "metric_median", "metric_p95", "support_mean", "support_median", "support_p95"],
    )
    write_csv(
        out_dir / "step_checks.csv",
        step_rows,
        ["n_from", "n_to", "median_from", "median_to", "delta", "step_tol", "step_pass"],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary_csv": summary_csv.as_posix(),
        "prereg_doc": DEFAULT_PREREG.as_posix() if DEFAULT_PREREG.exists() else "",
        "levels": levels,
        "metric_field": args.metric_field,
        "support_field": args.support_field,
        "checks": {
            "step_pass_fraction": round(frac, 6),
            "step_pass_fraction_min": args.min_step_pass_fraction,
            "overall_improvement": round(overall_improvement, 6),
            "overall_improvement_min": args.min_overall_improvement,
            "support_ratio_finest_over_coarsest": round(support_ratio, 6),
            "support_ratio_max": args.support_worsen_factor_max,
            "step_fraction_pass": checks["step_fraction"],
            "overall_improvement_pass": checks["overall_improvement"],
            "support_sanity_pass": checks["support_sanity"],
        },
        "decision": decision,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence Gate v1",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_csv: `{summary_csv.as_posix()}`",
        f"- decision: `{decision}`",
        "",
        "## Checks",
        "",
        f"- step_pass_fraction: `{frac:.6f}` (min `{args.min_step_pass_fraction}`)",
        f"- overall_improvement (`coarse - fine`): `{overall_improvement:.6f}` (min `{args.min_overall_improvement}`)",
        f"- support_ratio (`p95_fine/p95_coarse`): `{support_ratio:.6f}` (max `{args.support_worsen_factor_max}`)",
        "",
        "## Rule Results",
        "",
        f"- step_fraction_pass: `{'true' if checks['step_fraction'] else 'false'}`",
        f"- overall_improvement_pass: `{'true' if checks['overall_improvement'] else 'false'}`",
        f"- support_sanity_pass: `{'true' if checks['support_sanity'] else 'false'}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"level_stats_csv: {out_dir / 'level_stats.csv'}")
    print(f"step_checks_csv: {out_dir / 'step_checks.csv'}")
    print(f"report_md:       {out_dir / 'report.md'}")
    print(f"report_json:     {out_dir / 'report.json'}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
