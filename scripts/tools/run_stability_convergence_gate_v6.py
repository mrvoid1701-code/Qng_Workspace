#!/usr/bin/env python3
"""
Run stability convergence gate v6 (dual-channel):
- S2 structural lane: hard deterministic pass/fail
- S1 energetic lane: block-level statistical trend (Theil-Sen slope + CI)
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
    / "stability-convergence-v6"
    / "raw"
    / "summary.csv"
)
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v6"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "qng-stability-convergence-v6.md"

STRUCTURAL_GATES = [
    "gate_sigma_bounds",
    "gate_metric_positive",
    "gate_metric_cond",
    "gate_runaway",
    "gate_variational_residual",
    "gate_alpha_drift",
    "gate_no_signalling",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run stability convergence gate v6.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--prereg-doc", default=str(DEFAULT_PREREG))
    p.add_argument("--seed-field", default="grid_seed")
    p.add_argument("--n-nodes-field", default="n_nodes")
    p.add_argument("--full-metric-field", default="delta_energy_rel")
    p.add_argument("--bulk-metric-field", default="delta_energy_rel")
    p.add_argument("--bulk-flag-active", default="active_regime_flag")
    p.add_argument("--bulk-flag-sigma", default="gate_sigma_bounds")
    p.add_argument("--bulk-flag-metric", default="gate_metric_positive")
    p.add_argument("--bulk-core-size-field", default="core_stable_size")
    p.add_argument("--bulk-core-ratio-field", default="core_stable_ratio")
    p.add_argument("--bulk-core-size-min", type=int, default=6)
    p.add_argument("--bulk-core-ratio-min", type=float, default=0.10)
    p.add_argument("--bulk-min-profiles-per-level", type=int, default=5)
    p.add_argument("--bootstrap-reps", type=int, default=2000)
    p.add_argument("--ci-alpha", type=float, default=0.05)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
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


def to_int(v: Any, default: int = 0) -> int:
    try:
        return int(str(v).strip())
    except Exception:
        return default


def is_pass(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in {"pass", "true", "1", "yes"}


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def percentile(vals: list[float], q: float) -> float:
    if not vals:
        return 0.0
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


def theil_sen_slope(xs: list[float], ys: list[float]) -> float:
    slopes: list[float] = []
    for i in range(len(xs) - 1):
        for j in range(i + 1, len(xs)):
            dx = xs[j] - xs[i]
            if abs(dx) <= 1e-18:
                continue
            slopes.append((ys[j] - ys[i]) / dx)
    return median(slopes) if slopes else 0.0


def bootstrap_median_ci(vals: list[float], reps: int, alpha: float, seed: int) -> tuple[float, float, float]:
    if not vals:
        return 0.0, 0.0, 0.0
    rng = random.Random(seed)
    boots: list[float] = []
    n = len(vals)
    for _ in range(max(100, reps)):
        sample = [vals[rng.randrange(n)] for _ in range(n)]
        boots.append(median(sample))
    lo = percentile(boots, alpha / 2.0)
    hi = percentile(boots, 1.0 - alpha / 2.0)
    return median(vals), lo, hi


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
    per_seed_profiles: dict[str, list[dict[str, str]]] = {}
    levels = sorted({int(str(r.get(args.n_nodes_field, "0"))) for r in rows})
    bulk_levels = levels[1:-1]
    for r in rows:
        s = str(r.get(args.seed_field, "")).strip()
        n = int(str(r.get(args.n_nodes_field, "0")))
        per_seed_profiles.setdefault(s, []).append(r)
        per_seed_level.setdefault((s, n), []).append(r)

    seed_rows: list[dict[str, Any]] = []
    level_rows: list[dict[str, Any]] = []
    s2_seed_pass_count = 0
    bulk_valid_seed_count = 0
    full_seed_slopes: list[float] = []
    bulk_seed_slopes: list[float] = []

    for seed in sorted(per_seed_profiles.keys(), key=lambda x: int(x) if x.isdigit() else x):
        profiles = per_seed_profiles[seed]
        structural_seed_pass = all(all(is_pass(r.get(g, "")) for g in STRUCTURAL_GATES) for r in profiles)
        if structural_seed_pass:
            s2_seed_pass_count += 1

        full_medians: dict[int, float] = {}
        bulk_medians: dict[int, float] = {}
        bulk_valid = True

        for n in levels:
            sub = per_seed_level.get((seed, n), [])
            full_vals = [to_float(r.get(args.full_metric_field, "")) for r in sub]
            full_medians[n] = median(full_vals)

            eligible = []
            for r in sub:
                if not is_pass(r.get(args.bulk_flag_active, "")):
                    continue
                if not is_pass(r.get(args.bulk_flag_sigma, "")):
                    continue
                if not is_pass(r.get(args.bulk_flag_metric, "")):
                    continue
                if to_int(r.get(args.bulk_core_size_field, "0")) < args.bulk_core_size_min:
                    continue
                if to_float(r.get(args.bulk_core_ratio_field, "0.0")) < args.bulk_core_ratio_min:
                    continue
                eligible.append(r)

            eligible_vals = [to_float(r.get(args.bulk_metric_field, "")) for r in eligible]
            if n in bulk_levels:
                if len(eligible_vals) < args.bulk_min_profiles_per_level:
                    bulk_valid = False
                else:
                    bulk_medians[n] = median(eligible_vals)

            level_rows.append(
                {
                    "seed": seed,
                    "n_nodes": n,
                    "n_profiles": len(sub),
                    "n_profiles_bulk_eligible": len(eligible_vals),
                    "full_metric_median": f"{full_medians[n]:.6f}",
                    "bulk_metric_median": f"{bulk_medians[n]:.6f}" if n in bulk_medians else "",
                }
            )

        full_x = [float(n) for n in levels]
        full_y = [full_medians[n] for n in levels]
        full_slope = theil_sen_slope(full_x, full_y)
        full_seed_slopes.append(full_slope)

        bulk_slope = 0.0
        if bulk_valid and all(n in bulk_medians for n in bulk_levels):
            bulk_x = [float(n) for n in bulk_levels]
            bulk_y = [bulk_medians[n] for n in bulk_levels]
            bulk_slope = theil_sen_slope(bulk_x, bulk_y)
            bulk_seed_slopes.append(bulk_slope)
            bulk_valid_seed_count += 1

        seed_rows.append(
            {
                "seed": seed,
                "structural_seed_pass": "true" if structural_seed_pass else "false",
                "bulk_valid": "true" if bulk_valid else "false",
                "full_slope_theilsen": f"{full_slope:.9f}",
                "bulk_slope_theilsen": f"{bulk_slope:.9f}" if bulk_valid else "",
            }
        )

    seed_total = len(seed_rows)
    s2_seed_pass_fraction = s2_seed_pass_count / max(seed_total, 1)
    bulk_valid_seed_fraction = bulk_valid_seed_count / max(seed_total, 1)

    full_med, full_ci_lo, full_ci_hi = bootstrap_median_ci(
        full_seed_slopes, reps=args.bootstrap_reps, alpha=args.ci_alpha, seed=1701
    )
    bulk_med, bulk_ci_lo, bulk_ci_hi = bootstrap_median_ci(
        bulk_seed_slopes, reps=args.bootstrap_reps, alpha=args.ci_alpha, seed=1702
    )

    checks = {
        "s2_all_seeds_pass": abs(s2_seed_pass_fraction - 1.0) <= 1e-12,
        "bulk_valid_all_seeds": abs(bulk_valid_seed_fraction - 1.0) <= 1e-12,
        "s1_full_slope_ci_excludes_zero_neg": full_ci_hi < 0.0,
        "s1_bulk_slope_ci_excludes_zero_neg": bulk_ci_hi < 0.0,
    }
    decision = "PASS" if all(checks.values()) else "FAIL"

    write_csv(
        out_dir / "seed_checks.csv",
        seed_rows,
        ["seed", "structural_seed_pass", "bulk_valid", "full_slope_theilsen", "bulk_slope_theilsen"],
    )
    write_csv(
        out_dir / "level_stats.csv",
        level_rows,
        ["seed", "n_nodes", "n_profiles", "n_profiles_bulk_eligible", "full_metric_median", "bulk_metric_median"],
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "summary_csv": summary_csv.as_posix(),
        "prereg_doc": prereg_doc.as_posix() if prereg_doc.exists() else "",
        "seed_count": seed_total,
        "levels_full": levels,
        "levels_bulk": bulk_levels,
        "bootstrap_reps": args.bootstrap_reps,
        "ci_alpha": args.ci_alpha,
        "checks": {
            "s2_seed_pass_fraction": round(s2_seed_pass_fraction, 6),
            "bulk_valid_seed_fraction": round(bulk_valid_seed_fraction, 6),
            "full_slope_median": full_med,
            "full_slope_ci_low": full_ci_lo,
            "full_slope_ci_high": full_ci_hi,
            "bulk_slope_median": bulk_med,
            "bulk_slope_ci_low": bulk_ci_lo,
            "bulk_slope_ci_high": bulk_ci_hi,
            "s2_all_seeds_pass_ok": checks["s2_all_seeds_pass"],
            "bulk_valid_all_seeds_ok": checks["bulk_valid_all_seeds"],
            "s1_full_slope_ci_excludes_zero_neg_ok": checks["s1_full_slope_ci_excludes_zero_neg"],
            "s1_bulk_slope_ci_excludes_zero_neg_ok": checks["s1_bulk_slope_ci_excludes_zero_neg"],
        },
        "decision": decision,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Stability Convergence Gate v6",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_csv: `{summary_csv.as_posix()}`",
        f"- prereg_doc: `{report['prereg_doc']}`",
        f"- seed_count: `{seed_total}`",
        f"- decision: `{decision}`",
        "",
        "## S2 Structural Lane",
        "",
        f"- s2_seed_pass_fraction: `{s2_seed_pass_fraction:.6f}` (must be `1.0`)",
        f"- bulk_valid_seed_fraction: `{bulk_valid_seed_fraction:.6f}` (must be `1.0`)",
        "",
        "## S1 Energetic Lane (Theil-Sen + CI)",
        "",
        f"- full_slope_median: `{full_med:.9f}`",
        f"- full_slope_ci: `[{full_ci_lo:.9f}, {full_ci_hi:.9f}]` (require upper `< 0`)",
        f"- bulk_slope_median: `{bulk_med:.9f}`",
        f"- bulk_slope_ci: `[{bulk_ci_lo:.9f}, {bulk_ci_hi:.9f}]` (require upper `< 0`)",
        "",
        "## Rule Results",
        "",
        f"- s2_all_seeds_pass_ok: `{'true' if checks['s2_all_seeds_pass'] else 'false'}`",
        f"- bulk_valid_all_seeds_ok: `{'true' if checks['bulk_valid_all_seeds'] else 'false'}`",
        f"- s1_full_slope_ci_excludes_zero_neg_ok: `{'true' if checks['s1_full_slope_ci_excludes_zero_neg'] else 'false'}`",
        f"- s1_bulk_slope_ci_excludes_zero_neg_ok: `{'true' if checks['s1_bulk_slope_ci_excludes_zero_neg'] else 'false'}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"seed_checks_csv: {out_dir / 'seed_checks.csv'}")
    print(f"level_stats_csv: {out_dir / 'level_stats.csv'}")
    print(f"report_md:       {out_dir / 'report.md'}")
    print(f"report_json:     {out_dir / 'report.json'}")

    if args.strict_exit and decision != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
