#!/usr/bin/env python3
"""
Run stability convergence gate v2:
- full vs bulk convergence scores
- scaling-law trend checks
- cross-seed aggregation
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
    / "stability-convergence-v2"
    / "raw"
    / "summary.csv"
)
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v2"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v2.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence gate v2.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--seed-field", default="grid_seed")
    p.add_argument("--n-nodes-field", default="n_nodes")
    p.add_argument("--metric-field", default="delta_energy_rel")
    p.add_argument("--support-field", default="energy_noether_rel")
    p.add_argument("--step-tol", type=float, default=0.002)
    p.add_argument("--full-step-fraction-min", type=float, default=0.75)
    p.add_argument("--bulk-step-fraction-min", type=float, default=0.85)
    p.add_argument("--overall-improvement-min", type=float, default=0.005)
    p.add_argument("--support-worsen-factor-max", type=float, default=1.25)
    p.add_argument("--rho-full-max", type=float, default=-0.60)
    p.add_argument("--rho-bulk-max", type=float, default=-0.80)
    p.add_argument("--full-seed-pass-fraction-min", type=float, default=0.85)
    p.add_argument("--bulk-seed-pass-fraction-min", type=float, default=0.85)
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


def average(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def rankdata(vals: list[float]) -> list[float]:
    idx = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[idx[j + 1]] == vals[idx[i]]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[idx[k]] = r
        i = j + 1
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = average(xs)
    my = average(ys)
    sxx = sum((x - mx) * (x - mx) for x in xs)
    syy = sum((y - my) * (y - my) for y in ys)
    if sxx <= 1e-18 or syy <= 1e-18:
        return 0.0
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def spearman(xs: list[float], ys: list[float]) -> float:
    rx = rankdata(xs)
    ry = rankdata(ys)
    return pearson(rx, ry)


def make_step_fraction(levels: list[int], med_map: dict[int, float], step_tol: float) -> tuple[float, list[dict[str, Any]]]:
    if len(levels) < 2:
        return 0.0, []
    rows: list[dict[str, Any]] = []
    pass_count = 0
    for i in range(len(levels) - 1):
        n0 = levels[i]
        n1 = levels[i + 1]
        d = med_map[n1] - med_map[n0]
        ok = d <= step_tol
        if ok:
            pass_count += 1
        rows.append(
            {
                "n_from": n0,
                "n_to": n1,
                "median_from": f"{med_map[n0]:.6f}",
                "median_to": f"{med_map[n1]:.6f}",
                "delta": f"{d:.6f}",
                "step_tol": f"{step_tol:.6f}",
                "step_pass": "true" if ok else "false",
            }
        )
    return pass_count / max(1, len(levels) - 1), rows


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_csv.exists():
        raise FileNotFoundError(f"summary missing: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary csv has zero rows")

    per_seed_level: dict[tuple[str, int], list[dict[str, str]]] = {}
    all_levels_set: set[int] = set()
    seeds_set: set[str] = set()

    for r in rows:
        seed = str(r.get(args.seed_field, "")).strip()
        if seed == "":
            continue
        try:
            n = int(str(r.get(args.n_nodes_field, "")).strip())
        except Exception:
            continue
        seeds_set.add(seed)
        all_levels_set.add(n)
        per_seed_level.setdefault((seed, n), []).append(r)

    levels = sorted(all_levels_set)
    if len(levels) < 3:
        raise RuntimeError("need at least 3 levels for bulk/full split")
    bulk_levels = levels[1:-1]
    if len(bulk_levels) < 2:
        raise RuntimeError("bulk levels need at least 2 values")

    seeds = sorted(seeds_set, key=lambda s: int(s) if s.isdigit() else s)
    if not seeds:
        raise RuntimeError("no seeds found")

    seed_rows: list[dict[str, Any]] = []
    step_rows: list[dict[str, Any]] = []
    level_rows: list[dict[str, Any]] = []

    full_seed_pass_count = 0
    bulk_seed_pass_count = 0
    rho_full_vals: list[float] = []
    rho_bulk_vals: list[float] = []

    for seed in seeds:
        med_map: dict[int, float] = {}
        support_p95_map: dict[int, float] = {}
        ok_seed = True
        for n in levels:
            sub = per_seed_level.get((seed, n), [])
            mvals = [to_float(r.get(args.metric_field, "")) for r in sub]
            mvals = [v for v in mvals if v is not None]
            svals = [to_float(r.get(args.support_field, "")) for r in sub]
            svals = [v for v in svals if v is not None]
            if not mvals or not svals:
                ok_seed = False
                break
            med_map[n] = median(mvals)
            support_p95_map[n] = percentile(svals, 0.95)
            level_rows.append(
                {
                    "seed": seed,
                    "n_nodes": n,
                    "n_profiles": len(sub),
                    "metric_mean": f"{average(mvals):.6f}",
                    "metric_median": f"{med_map[n]:.6f}",
                    "metric_p95": f"{percentile(mvals, 0.95):.6f}",
                    "support_mean": f"{average(svals):.6f}",
                    "support_median": f"{median(svals):.6f}",
                    "support_p95": f"{support_p95_map[n]:.6f}",
                }
            )
        if not ok_seed:
            continue

        full_step_frac, full_steps = make_step_fraction(levels, med_map, args.step_tol)
        bulk_step_frac, bulk_steps = make_step_fraction(bulk_levels, med_map, args.step_tol)
        for r in full_steps:
            rr = dict(r)
            rr["seed"] = seed
            rr["scope"] = "full"
            step_rows.append(rr)
        for r in bulk_steps:
            rr = dict(r)
            rr["seed"] = seed
            rr["scope"] = "bulk"
            step_rows.append(rr)

        overall_improvement = med_map[levels[0]] - med_map[levels[-1]]
        support_ratio = support_p95_map[levels[-1]] / max(support_p95_map[levels[0]], 1e-12)

        x_full = [float(n) for n in levels]
        y_full = [med_map[n] for n in levels]
        x_bulk = [float(n) for n in bulk_levels]
        y_bulk = [med_map[n] for n in bulk_levels]
        rho_full = spearman(x_full, y_full)
        rho_bulk = spearman(x_bulk, y_bulk)
        rho_full_vals.append(rho_full)
        rho_bulk_vals.append(rho_bulk)

        full_pass = (
            (full_step_frac >= args.full_step_fraction_min)
            and (overall_improvement >= args.overall_improvement_min)
            and (support_ratio <= args.support_worsen_factor_max)
            and (rho_full <= args.rho_full_max)
        )
        bulk_pass = (
            (bulk_step_frac >= args.bulk_step_fraction_min)
            and (rho_bulk <= args.rho_bulk_max)
        )
        if full_pass:
            full_seed_pass_count += 1
        if bulk_pass:
            bulk_seed_pass_count += 1

        seed_rows.append(
            {
                "seed": seed,
                "full_step_fraction": f"{full_step_frac:.6f}",
                "bulk_step_fraction": f"{bulk_step_frac:.6f}",
                "overall_improvement": f"{overall_improvement:.6f}",
                "support_ratio": f"{support_ratio:.6f}",
                "rho_full": f"{rho_full:.6f}",
                "rho_bulk": f"{rho_bulk:.6f}",
                "full_pass": "true" if full_pass else "false",
                "bulk_pass": "true" if bulk_pass else "false",
            }
        )

    n_seeds = len(seed_rows)
    if n_seeds == 0:
        raise RuntimeError("no valid seeds after parsing")
    full_seed_pass_fraction = full_seed_pass_count / n_seeds
    bulk_seed_pass_fraction = bulk_seed_pass_count / n_seeds
    rho_full_median = median(rho_full_vals) if rho_full_vals else 0.0
    rho_bulk_median = median(rho_bulk_vals) if rho_bulk_vals else 0.0

    checks = {
        "full_seed_pass_fraction": full_seed_pass_fraction >= args.full_seed_pass_fraction_min,
        "bulk_seed_pass_fraction": bulk_seed_pass_fraction >= args.bulk_seed_pass_fraction_min,
        "rho_full_median": rho_full_median <= args.rho_full_max,
        "rho_bulk_median": rho_bulk_median <= args.rho_bulk_max,
    }
    decision = "PASS" if all(checks.values()) else "FAIL"

    write_csv(
        out_dir / "seed_checks.csv",
        seed_rows,
        ["seed", "full_step_fraction", "bulk_step_fraction", "overall_improvement", "support_ratio", "rho_full", "rho_bulk", "full_pass", "bulk_pass"],
    )
    write_csv(
        out_dir / "level_stats.csv",
        level_rows,
        ["seed", "n_nodes", "n_profiles", "metric_mean", "metric_median", "metric_p95", "support_mean", "support_median", "support_p95"],
    )
    write_csv(
        out_dir / "step_checks.csv",
        step_rows,
        ["seed", "scope", "n_from", "n_to", "median_from", "median_to", "delta", "step_tol", "step_pass"],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary_csv": summary_csv.as_posix(),
        "prereg_doc": DEFAULT_PREREG.as_posix() if DEFAULT_PREREG.exists() else "",
        "seed_count": n_seeds,
        "levels_full": levels,
        "levels_bulk": bulk_levels,
        "checks": {
            "full_seed_pass_fraction": round(full_seed_pass_fraction, 6),
            "full_seed_pass_fraction_min": args.full_seed_pass_fraction_min,
            "bulk_seed_pass_fraction": round(bulk_seed_pass_fraction, 6),
            "bulk_seed_pass_fraction_min": args.bulk_seed_pass_fraction_min,
            "rho_full_median": round(rho_full_median, 6),
            "rho_full_max": args.rho_full_max,
            "rho_bulk_median": round(rho_bulk_median, 6),
            "rho_bulk_max": args.rho_bulk_max,
            "full_seed_pass_fraction_ok": checks["full_seed_pass_fraction"],
            "bulk_seed_pass_fraction_ok": checks["bulk_seed_pass_fraction"],
            "rho_full_median_ok": checks["rho_full_median"],
            "rho_bulk_median_ok": checks["rho_bulk_median"],
        },
        "decision": decision,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence Gate v2",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_csv: `{summary_csv.as_posix()}`",
        f"- seed_count: `{n_seeds}`",
        f"- decision: `{decision}`",
        "",
        "## Aggregate Checks",
        "",
        f"- full_seed_pass_fraction: `{full_seed_pass_fraction:.6f}` (min `{args.full_seed_pass_fraction_min}`)",
        f"- bulk_seed_pass_fraction: `{bulk_seed_pass_fraction:.6f}` (min `{args.bulk_seed_pass_fraction_min}`)",
        f"- rho_full_median: `{rho_full_median:.6f}` (max `{args.rho_full_max}`)",
        f"- rho_bulk_median: `{rho_bulk_median:.6f}` (max `{args.rho_bulk_max}`)",
        "",
        "## Rule Results",
        "",
        f"- full_seed_pass_fraction_ok: `{'true' if checks['full_seed_pass_fraction'] else 'false'}`",
        f"- bulk_seed_pass_fraction_ok: `{'true' if checks['bulk_seed_pass_fraction'] else 'false'}`",
        f"- rho_full_median_ok: `{'true' if checks['rho_full_median'] else 'false'}`",
        f"- rho_bulk_median_ok: `{'true' if checks['rho_bulk_median'] else 'false'}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"seed_checks_csv: {out_dir / 'seed_checks.csv'}")
    print(f"level_stats_csv: {out_dir / 'level_stats.csv'}")
    print(f"step_checks_csv: {out_dir / 'step_checks.csv'}")
    print(f"report_md:       {out_dir / 'report.md'}")
    print(f"report_json:     {out_dir / 'report.json'}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
