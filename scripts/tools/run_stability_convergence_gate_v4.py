#!/usr/bin/env python3
"""
Run stability convergence gate v4:
- full trend unchanged vs v2/v3 (Spearman on full levels)
- bulk trend uses robust Kendall tau + bootstrap CI (exclude 0)
- bulk eligibility keeps Sigma-mask core-stable policy
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "stability-convergence-v4"
    / "raw"
    / "summary.csv"
)
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v4"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v4.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence gate v4.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--prereg-doc", default=str(DEFAULT_PREREG))
    p.add_argument("--seed-field", default="grid_seed")
    p.add_argument("--n-nodes-field", default="n_nodes")
    p.add_argument("--full-metric-field", default="delta_energy_rel")
    p.add_argument("--bulk-metric-field", default="delta_energy_rel")
    p.add_argument("--support-field", default="energy_noether_rel")
    p.add_argument("--step-tol", type=float, default=0.002)
    p.add_argument("--full-step-fraction-min", type=float, default=0.75)
    p.add_argument("--bulk-step-fraction-min", type=float, default=0.85)
    p.add_argument("--overall-improvement-min", type=float, default=0.005)
    p.add_argument("--support-worsen-factor-max", type=float, default=1.25)
    p.add_argument("--rho-full-max", type=float, default=-0.60)
    p.add_argument("--full-seed-pass-fraction-min", type=float, default=0.85)
    p.add_argument("--bulk-seed-pass-fraction-min", type=float, default=0.85)
    p.add_argument("--bulk-min-profiles-per-level", type=int, default=5)
    p.add_argument("--bulk-flag-active", default="active_regime_flag")
    p.add_argument("--bulk-flag-sigma", default="gate_sigma_bounds")
    p.add_argument("--bulk-flag-metric", default="gate_metric_positive")
    p.add_argument("--bulk-core-size-field", default="core_stable_size")
    p.add_argument("--bulk-core-ratio-field", default="core_stable_ratio")
    p.add_argument("--bulk-core-size-min", type=int, default=6)
    p.add_argument("--bulk-core-ratio-min", type=float, default=0.10)
    p.add_argument("--bulk-bootstrap-reps", type=int, default=400)
    p.add_argument("--bulk-ci-alpha", type=float, default=0.05)
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


def to_int(v: Any, default: int = 0) -> int:
    try:
        return int(str(v).strip())
    except Exception:
        return default


def is_pass_flag(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in {"pass", "true", "1", "yes"}


def percentile(vals: list[float], q: float) -> float:
    s = sorted(vals)
    if not s:
        return 0.0
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


def kendall_tau(yvals: list[float]) -> float:
    n = len(yvals)
    if n < 2:
        return 0.0
    pairs = n * (n - 1) // 2
    if pairs <= 0:
        return 0.0
    score = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = yvals[j] - yvals[i]
            if d > 0:
                score += 1
            elif d < 0:
                score -= 1
    return score / pairs


def theil_sen_slope(xs: list[float], ys: list[float]) -> float:
    slopes: list[float] = []
    for i in range(len(xs) - 1):
        for j in range(i + 1, len(xs)):
            dx = xs[j] - xs[i]
            if abs(dx) <= 1e-18:
                continue
            slopes.append((ys[j] - ys[i]) / dx)
    return median(slopes) if slopes else 0.0


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


def bootstrap_kendall_ci(
    levels: list[int],
    level_samples: dict[int, list[float]],
    reps: int,
    alpha: float,
    seed_token: int,
) -> tuple[float, float, float, float]:
    rng = random.Random(seed_token)
    x = [float(n) for n in levels]
    taus: list[float] = []
    slopes: list[float] = []
    for _ in range(max(10, reps)):
        meds: list[float] = []
        ok = True
        for n in levels:
            vals = level_samples.get(n, [])
            if not vals:
                ok = False
                break
            samp = [vals[rng.randrange(len(vals))] for _ in range(len(vals))]
            meds.append(median(samp))
        if not ok:
            continue
        taus.append(kendall_tau(meds))
        slopes.append(theil_sen_slope(x, meds))
    if not taus:
        return 1.0, 1.0, 1.0, 0.0
    lo = percentile(taus, alpha / 2.0)
    hi = percentile(taus, 1.0 - alpha / 2.0)
    tau_med = median(taus)
    slope_med = median(slopes) if slopes else 0.0
    return tau_med, lo, hi, slope_med


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    prereg_doc = Path(args.prereg_doc).resolve()
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
    bulk_ci_pass_count = 0
    rho_full_vals: list[float] = []
    tau_bulk_vals: list[float] = []
    tau_bulk_ci_hi_vals: list[float] = []
    insufficient_bulk_count = 0

    for seed in seeds:
        med_map_full: dict[int, float] = {}
        med_map_bulk: dict[int, float] = {}
        bulk_samples: dict[int, list[float]] = {}
        support_p95_map: dict[int, float] = {}
        ok_seed = True
        bulk_support_ok = True

        for n in levels:
            sub = per_seed_level.get((seed, n), [])
            full_vals = [to_float(r.get(args.full_metric_field, "")) for r in sub]
            full_vals = [v for v in full_vals if v is not None]
            svals = [to_float(r.get(args.support_field, "")) for r in sub]
            svals = [v for v in svals if v is not None]
            if not full_vals or not svals:
                ok_seed = False
                break
            med_map_full[n] = median(full_vals)
            support_p95_map[n] = percentile(svals, 0.95)

            eligible = []
            for r in sub:
                if not is_pass_flag(r.get(args.bulk_flag_active, "")):
                    continue
                if not is_pass_flag(r.get(args.bulk_flag_sigma, "")):
                    continue
                if not is_pass_flag(r.get(args.bulk_flag_metric, "")):
                    continue
                core_size = to_int(r.get(args.bulk_core_size_field, "0"), 0)
                core_ratio = to_float(r.get(args.bulk_core_ratio_field, "0.0"))
                core_ratio = 0.0 if core_ratio is None else core_ratio
                if core_size < args.bulk_core_size_min:
                    continue
                if core_ratio < args.bulk_core_ratio_min:
                    continue
                eligible.append(r)

            eligible_bulk_vals = [to_float(r.get(args.bulk_metric_field, "")) for r in eligible]
            eligible_bulk_vals = [v for v in eligible_bulk_vals if v is not None]
            if n in bulk_levels:
                if len(eligible_bulk_vals) < args.bulk_min_profiles_per_level:
                    bulk_support_ok = False
                else:
                    med_map_bulk[n] = median(eligible_bulk_vals)
                    bulk_samples[n] = eligible_bulk_vals

            level_rows.append(
                {
                    "seed": seed,
                    "n_nodes": n,
                    "n_profiles": len(sub),
                    "n_profiles_bulk_eligible": len(eligible_bulk_vals),
                    "metric_mean": f"{average(full_vals):.6f}",
                    "metric_median": f"{med_map_full[n]:.6f}",
                    "metric_p95": f"{percentile(full_vals, 0.95):.6f}",
                    "bulk_metric_median_eligible": f"{med_map_bulk[n]:.6f}" if n in med_map_bulk else "",
                    "support_mean": f"{average(svals):.6f}",
                    "support_median": f"{median(svals):.6f}",
                    "support_p95": f"{support_p95_map[n]:.6f}",
                }
            )

        if not ok_seed:
            continue

        full_step_frac, full_steps = make_step_fraction(levels, med_map_full, args.step_tol)
        for r in full_steps:
            rr = dict(r)
            rr["seed"] = seed
            rr["scope"] = "full"
            step_rows.append(rr)

        bulk_step_frac = 0.0
        tau_bulk = 1.0
        tau_ci_low = 1.0
        tau_ci_high = 1.0
        ts_slope = 0.0
        ci_excludes_zero_neg = False
        bulk_steps: list[dict[str, Any]] = []
        if bulk_support_ok and all(n in med_map_bulk for n in bulk_levels):
            bulk_step_frac, bulk_steps = make_step_fraction(bulk_levels, med_map_bulk, args.step_tol)
            y_bulk = [med_map_bulk[n] for n in bulk_levels]
            tau_bulk = kendall_tau(y_bulk)
            seed_token = (int(seed) if seed.isdigit() else abs(hash(seed))) + 1701
            _, tau_ci_low, tau_ci_high, ts_slope = bootstrap_kendall_ci(
                levels=bulk_levels,
                level_samples=bulk_samples,
                reps=args.bulk_bootstrap_reps,
                alpha=args.bulk_ci_alpha,
                seed_token=seed_token,
            )
            ci_excludes_zero_neg = tau_ci_high < 0.0
            if ci_excludes_zero_neg:
                bulk_ci_pass_count += 1
        else:
            insufficient_bulk_count += 1
            bulk_support_ok = False

        for r in bulk_steps:
            rr = dict(r)
            rr["seed"] = seed
            rr["scope"] = "bulk"
            step_rows.append(rr)

        overall_improvement = med_map_full[levels[0]] - med_map_full[levels[-1]]
        support_ratio = support_p95_map[levels[-1]] / max(support_p95_map[levels[0]], 1e-12)
        x_full = [float(n) for n in levels]
        y_full = [med_map_full[n] for n in levels]
        rho_full = spearman(x_full, y_full)
        rho_full_vals.append(rho_full)
        tau_bulk_vals.append(tau_bulk)
        tau_bulk_ci_hi_vals.append(tau_ci_high)

        full_pass = (
            (full_step_frac >= args.full_step_fraction_min)
            and (overall_improvement >= args.overall_improvement_min)
            and (support_ratio <= args.support_worsen_factor_max)
            and (rho_full <= args.rho_full_max)
        )
        bulk_pass = (
            bulk_support_ok
            and (bulk_step_frac >= args.bulk_step_fraction_min)
            and ci_excludes_zero_neg
        )
        if full_pass:
            full_seed_pass_count += 1
        if bulk_pass:
            bulk_seed_pass_count += 1

        seed_rows.append(
            {
                "seed": seed,
                "full_step_fraction": f"{full_step_frac:.6f}",
                "bulk_step_fraction": f"{bulk_step_frac:.6f}" if bulk_support_ok else "",
                "overall_improvement": f"{overall_improvement:.6f}",
                "support_ratio": f"{support_ratio:.6f}",
                "rho_full": f"{rho_full:.6f}",
                "bulk_tau": f"{tau_bulk:.6f}" if bulk_support_ok else "",
                "bulk_tau_ci_low": f"{tau_ci_low:.6f}" if bulk_support_ok else "",
                "bulk_tau_ci_high": f"{tau_ci_high:.6f}" if bulk_support_ok else "",
                "bulk_theil_sen_slope": f"{ts_slope:.6f}" if bulk_support_ok else "",
                "bulk_ci_excludes_zero_neg": "true" if ci_excludes_zero_neg else "false",
                "bulk_support_ok": "true" if bulk_support_ok else "false",
                "full_pass": "true" if full_pass else "false",
                "bulk_pass": "true" if bulk_pass else "false",
            }
        )

    n_seeds = len(seed_rows)
    if n_seeds == 0:
        raise RuntimeError("no valid seeds after parsing")
    full_seed_pass_fraction = full_seed_pass_count / n_seeds
    bulk_seed_pass_fraction = bulk_seed_pass_count / n_seeds
    bulk_ci_pass_fraction = bulk_ci_pass_count / n_seeds
    rho_full_median = median(rho_full_vals) if rho_full_vals else 0.0
    tau_bulk_median = median(tau_bulk_vals) if tau_bulk_vals else 1.0
    tau_bulk_ci_high_median = median(tau_bulk_ci_hi_vals) if tau_bulk_ci_hi_vals else 1.0

    checks = {
        "full_seed_pass_fraction": full_seed_pass_fraction >= args.full_seed_pass_fraction_min,
        "bulk_seed_pass_fraction": bulk_seed_pass_fraction >= args.bulk_seed_pass_fraction_min,
        "rho_full_median": rho_full_median <= args.rho_full_max,
        "tau_bulk_ci_high_median": tau_bulk_ci_high_median < 0.0,
    }
    decision = "PASS" if all(checks.values()) else "FAIL"

    write_csv(
        out_dir / "seed_checks.csv",
        seed_rows,
        [
            "seed",
            "full_step_fraction",
            "bulk_step_fraction",
            "overall_improvement",
            "support_ratio",
            "rho_full",
            "bulk_tau",
            "bulk_tau_ci_low",
            "bulk_tau_ci_high",
            "bulk_theil_sen_slope",
            "bulk_ci_excludes_zero_neg",
            "bulk_support_ok",
            "full_pass",
            "bulk_pass",
        ],
    )
    write_csv(
        out_dir / "level_stats.csv",
        level_rows,
        [
            "seed",
            "n_nodes",
            "n_profiles",
            "n_profiles_bulk_eligible",
            "metric_mean",
            "metric_median",
            "metric_p95",
            "bulk_metric_median_eligible",
            "support_mean",
            "support_median",
            "support_p95",
        ],
    )
    write_csv(
        out_dir / "step_checks.csv",
        step_rows,
        ["seed", "scope", "n_from", "n_to", "median_from", "median_to", "delta", "step_tol", "step_pass"],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary_csv": summary_csv.as_posix(),
        "prereg_doc": prereg_doc.as_posix() if prereg_doc.exists() else "",
        "seed_count": n_seeds,
        "levels_full": levels,
        "levels_bulk": bulk_levels,
        "full_metric_field": args.full_metric_field,
        "bulk_metric_field": args.bulk_metric_field,
        "bulk_core_size_min": args.bulk_core_size_min,
        "bulk_core_ratio_min": args.bulk_core_ratio_min,
        "bulk_bootstrap_reps": args.bulk_bootstrap_reps,
        "bulk_ci_alpha": args.bulk_ci_alpha,
        "insufficient_bulk_support_seed_count": insufficient_bulk_count,
        "checks": {
            "full_seed_pass_fraction": round(full_seed_pass_fraction, 6),
            "full_seed_pass_fraction_min": args.full_seed_pass_fraction_min,
            "bulk_seed_pass_fraction": round(bulk_seed_pass_fraction, 6),
            "bulk_seed_pass_fraction_min": args.bulk_seed_pass_fraction_min,
            "bulk_ci_pass_fraction": round(bulk_ci_pass_fraction, 6),
            "rho_full_median": round(rho_full_median, 6),
            "rho_full_max": args.rho_full_max,
            "tau_bulk_median": round(tau_bulk_median, 6),
            "tau_bulk_ci_high_median": round(tau_bulk_ci_high_median, 6),
            "full_seed_pass_fraction_ok": checks["full_seed_pass_fraction"],
            "bulk_seed_pass_fraction_ok": checks["bulk_seed_pass_fraction"],
            "rho_full_median_ok": checks["rho_full_median"],
            "tau_bulk_ci_high_median_ok": checks["tau_bulk_ci_high_median"],
        },
        "decision": decision,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence Gate v4",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_csv: `{summary_csv.as_posix()}`",
        f"- prereg_doc: `{report['prereg_doc']}`",
        f"- seed_count: `{n_seeds}`",
        f"- decision: `{decision}`",
        "",
        "## Bulk Trend Estimator",
        "",
        "- estimator: `Kendall tau` over bulk-level medians",
        "- uncertainty: bootstrap CI on tau; pass requires `tau_ci_high < 0`",
        f"- bootstrap_reps: `{args.bulk_bootstrap_reps}`",
        f"- ci_alpha: `{args.bulk_ci_alpha}`",
        "",
        "## Bulk Support Policy",
        "",
        f"- min profiles per bulk level: `{args.bulk_min_profiles_per_level}`",
        f"- core stable size min: `{args.bulk_core_size_min}`",
        f"- core stable ratio min: `{args.bulk_core_ratio_min}`",
        f"- insufficient bulk support seed count: `{insufficient_bulk_count}`",
        "",
        "## Aggregate Checks",
        "",
        f"- full_seed_pass_fraction: `{full_seed_pass_fraction:.6f}` (min `{args.full_seed_pass_fraction_min}`)",
        f"- bulk_seed_pass_fraction: `{bulk_seed_pass_fraction:.6f}` (min `{args.bulk_seed_pass_fraction_min}`)",
        f"- bulk_ci_pass_fraction: `{bulk_ci_pass_fraction:.6f}`",
        f"- rho_full_median: `{rho_full_median:.6f}` (max `{args.rho_full_max}`)",
        f"- tau_bulk_median: `{tau_bulk_median:.6f}`",
        f"- tau_bulk_ci_high_median: `{tau_bulk_ci_high_median:.6f}` (must be `< 0`)",
        "",
        "## Rule Results",
        "",
        f"- full_seed_pass_fraction_ok: `{'true' if checks['full_seed_pass_fraction'] else 'false'}`",
        f"- bulk_seed_pass_fraction_ok: `{'true' if checks['bulk_seed_pass_fraction'] else 'false'}`",
        f"- rho_full_median_ok: `{'true' if checks['rho_full_median'] else 'false'}`",
        f"- tau_bulk_ci_high_median_ok: `{'true' if checks['tau_bulk_ci_high_median'] else 'false'}`",
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
