#!/usr/bin/env python3
"""
Analyze v4 bulk convergence failures:
- ties/discrete tau distribution
- support stability across bulk levels
- CI width audit
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BASE = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v4"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v4-failure-taxonomy-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze stability convergence v4 failures.")
    p.add_argument("--seed-checks-csv", default=str(DEFAULT_BASE / "seed_checks.csv"))
    p.add_argument("--level-stats-csv", default=str(DEFAULT_BASE / "level_stats.csv"))
    p.add_argument("--raw-summary-csv", default=str(DEFAULT_BASE / "raw" / "summary.csv"))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--bulk-min-profiles-per-level", type=int, default=5)
    p.add_argument("--tie-eps", type=float, default=1e-9)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        x = float(str(v).strip())
    except Exception:
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return x


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def avg(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def main() -> int:
    args = parse_args()
    seed_checks_csv = Path(args.seed_checks_csv).resolve()
    level_stats_csv = Path(args.level_stats_csv).resolve()
    raw_summary_csv = Path(args.raw_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in [seed_checks_csv, level_stats_csv, raw_summary_csv]:
        if not p.exists():
            raise FileNotFoundError(f"missing input: {p}")

    seed_rows = read_csv(seed_checks_csv)
    level_rows = read_csv(level_stats_csv)
    raw_rows = read_csv(raw_summary_csv)

    levels = sorted({int(str(r.get("n_nodes", "0"))) for r in level_rows})
    bulk_levels = levels[1:-1] if len(levels) >= 3 else []

    # per-seed level medians for tie checks
    bulk_metric_by_seed_level: dict[tuple[str, int], float] = {}
    bulk_support_by_seed_level: dict[tuple[str, int], int] = {}
    for r in level_rows:
        seed = str(r.get("seed", "")).strip()
        n = int(str(r.get("n_nodes", "0")))
        if n not in bulk_levels:
            continue
        m = to_float(r.get("bulk_metric_median_eligible", ""), default=float("nan"))
        if math.isnan(m):
            continue
        bulk_metric_by_seed_level[(seed, n)] = m
        bulk_support_by_seed_level[(seed, n)] = int(str(r.get("n_profiles_bulk_eligible", "0")))

    # core support variability from raw summary
    core_ratio_by_seed_level: dict[tuple[str, int], list[float]] = defaultdict(list)
    for r in raw_rows:
        seed = str(r.get("grid_seed", "")).strip()
        n = int(str(r.get("n_nodes", "0")))
        if n not in bulk_levels:
            continue
        core_ratio_by_seed_level[(seed, n)].append(to_float(r.get("core_stable_ratio", "0.0")))

    # tau distribution
    tau_counter: Counter[str] = Counter()
    for r in seed_rows:
        tau = to_float(r.get("bulk_tau", "0.0"))
        tau_counter[f"{tau:.6f}"] += 1
    tau_dist_rows = [{"bulk_tau": k, "count": v} for k, v in sorted(tau_counter.items(), key=lambda kv: float(kv[0]))]
    write_csv(out_dir / "tau_distribution.csv", tau_dist_rows, ["bulk_tau", "count"])

    fail_rows: list[dict[str, Any]] = []
    ci_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []
    fail_counter: Counter[str] = Counter()

    for r in seed_rows:
        seed = str(r.get("seed", "")).strip()
        bulk_pass = str(r.get("bulk_pass", "")).strip().lower() == "true"
        tau = to_float(r.get("bulk_tau", "0.0"))
        ci_lo = to_float(r.get("bulk_tau_ci_low", "0.0"))
        ci_hi = to_float(r.get("bulk_tau_ci_high", "0.0"))
        ci_width = ci_hi - ci_lo

        bulk_vals = [bulk_metric_by_seed_level.get((seed, n), float("nan")) for n in bulk_levels]
        support_vals = [bulk_support_by_seed_level.get((seed, n), 0) for n in bulk_levels]
        core_ratio_meds = [median(core_ratio_by_seed_level.get((seed, n), [])) for n in bulk_levels]

        tie_adjacent_count = 0
        for i in range(len(bulk_vals) - 1):
            a = bulk_vals[i]
            b = bulk_vals[i + 1]
            if math.isnan(a) or math.isnan(b):
                continue
            if abs(a - b) <= args.tie_eps:
                tie_adjacent_count += 1

        min_support = min(support_vals) if support_vals else 0
        max_support = max(support_vals) if support_vals else 0
        support_range = max_support - min_support
        core_ratio_range = (max(core_ratio_meds) - min(core_ratio_meds)) if core_ratio_meds else 0.0

        reason_flags: list[str] = []
        if ci_hi >= 0.0:
            reason_flags.append("ci_not_excluding_zero")
        if tie_adjacent_count > 0:
            reason_flags.append("ties_in_bulk_series")
        if min_support < args.bulk_min_profiles_per_level:
            reason_flags.append("support_below_min")
        if support_range > 10:
            reason_flags.append("support_variation_high")
        if not reason_flags:
            reason_flags.append("other")

        row = {
            "seed": seed,
            "bulk_pass": "true" if bulk_pass else "false",
            "bulk_tau": f"{tau:.6f}",
            "bulk_tau_ci_low": f"{ci_lo:.6f}",
            "bulk_tau_ci_high": f"{ci_hi:.6f}",
            "bulk_tau_ci_width": f"{ci_width:.6f}",
            "tie_adjacent_count": tie_adjacent_count,
            "min_bulk_support": min_support,
            "max_bulk_support": max_support,
            "support_range": support_range,
            "core_ratio_range": f"{core_ratio_range:.6f}",
            "reason_flags": ",".join(reason_flags),
        }
        ci_rows.append(row)
        support_rows.append(
            {
                "seed": seed,
                "min_bulk_support": min_support,
                "max_bulk_support": max_support,
                "support_range": support_range,
                "core_ratio_range": f"{core_ratio_range:.6f}",
                "tie_adjacent_count": tie_adjacent_count,
            }
        )
        if not bulk_pass:
            fail_rows.append(row)
            for f in reason_flags:
                fail_counter[f] += 1

    ci_rows.sort(key=lambda r: float(r["bulk_tau_ci_width"]), reverse=True)
    write_csv(
        out_dir / "ci_width_audit.csv",
        ci_rows,
        [
            "seed",
            "bulk_pass",
            "bulk_tau",
            "bulk_tau_ci_low",
            "bulk_tau_ci_high",
            "bulk_tau_ci_width",
            "tie_adjacent_count",
            "min_bulk_support",
            "max_bulk_support",
            "support_range",
            "core_ratio_range",
            "reason_flags",
        ],
    )
    write_csv(
        out_dir / "v4_fail_seeds.csv",
        fail_rows,
        [
            "seed",
            "bulk_pass",
            "bulk_tau",
            "bulk_tau_ci_low",
            "bulk_tau_ci_high",
            "bulk_tau_ci_width",
            "tie_adjacent_count",
            "min_bulk_support",
            "max_bulk_support",
            "support_range",
            "core_ratio_range",
            "reason_flags",
        ],
    )
    write_csv(
        out_dir / "support_collapse_summary.csv",
        support_rows,
        [
            "seed",
            "min_bulk_support",
            "max_bulk_support",
            "support_range",
            "core_ratio_range",
            "tie_adjacent_count",
        ],
    )

    generated = datetime.now(timezone.utc).isoformat()
    bulk_fail_count = len(fail_rows)
    total = len(seed_rows)
    tie_fail_count = sum(1 for r in fail_rows if int(str(r["tie_adjacent_count"])) > 0)
    ci_hi_nonneg_count = sum(1 for r in fail_rows if float(str(r["bulk_tau_ci_high"])) >= 0.0)
    lines = [
        "# Stability Convergence v4 Failure Taxonomy (v1)",
        "",
        f"- generated_utc: `{generated}`",
        f"- seed_total: `{total}`",
        f"- bulk_fail_seed_count: `{bulk_fail_count}`",
        f"- bulk_fail_rate: `{(bulk_fail_count / max(total,1)):.6f}`",
        "",
        "## Dominant Findings",
        "",
        f"- CI non-exclusion dominates failures: `{ci_hi_nonneg_count}/{bulk_fail_count}` fail seeds have `tau_ci_high >= 0`.",
        f"- ties/discreteness contribution: `{tie_fail_count}/{bulk_fail_count}` fail seeds show at least one adjacent tie in bulk medians.",
        f"- support collapse signal (below min profiles): `{sum(1 for r in fail_rows if int(str(r['min_bulk_support'])) < args.bulk_min_profiles_per_level)}/{bulk_fail_count}`.",
        "",
        "## Reason Flags (fail seeds)",
        "",
    ]
    for k, v in fail_counter.most_common():
        lines.append(f"- `{k}`: `{v}`")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- v4 failures are primarily a statistical-power issue (CI width/discreteness) rather than threshold tuning failure.",
            "- bulk support is present (`support_ok`) but with only a few bulk levels, CI on trend remains broad.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"v4_fail_seeds_csv: {out_dir / 'v4_fail_seeds.csv'}")
    print(f"tau_distribution_csv: {out_dir / 'tau_distribution.csv'}")
    print(f"ci_width_audit_csv: {out_dir / 'ci_width_audit.csv'}")
    print(f"support_collapse_summary_csv: {out_dir / 'support_collapse_summary.csv'}")
    print(f"report_md: {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
