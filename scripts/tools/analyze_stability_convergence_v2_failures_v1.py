#!/usr/bin/env python3
"""
Analyze stability convergence-v2 failures (bulk-focused taxonomy).

Outputs:
- bulk_fail_seeds.csv
- bulk_vs_full_delta.csv
- feature_correlations.csv
- pattern_summary.csv
- report.md
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BASE = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v2"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v2-failure-taxonomy-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze stability convergence-v2 failures.")
    p.add_argument("--report-json", default=str(DEFAULT_BASE / "report.json"))
    p.add_argument("--seed-checks-csv", default=str(DEFAULT_BASE / "seed_checks.csv"))
    p.add_argument("--level-stats-csv", default=str(DEFAULT_BASE / "level_stats.csv"))
    p.add_argument("--step-checks-csv", default=str(DEFAULT_BASE / "step_checks.csv"))
    p.add_argument("--raw-summary-csv", default=str(DEFAULT_BASE / "raw" / "summary.csv"))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
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


def bool01(v: Any) -> float:
    s = str(v or "").strip().lower()
    return 1.0 if s in {"true", "pass", "1", "yes"} else 0.0


def avg(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx = avg(xs)
    my = avg(ys)
    sxx = sum((x - mx) * (x - mx) for x in xs)
    syy = sum((y - my) * (y - my) for y in ys)
    if sxx <= 1e-18 or syy <= 1e-18:
        return None
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs)))
    return sxy / math.sqrt(sxx * syy)


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def main() -> int:
    args = parse_args()
    report_json = Path(args.report_json).resolve()
    seed_checks_csv = Path(args.seed_checks_csv).resolve()
    level_stats_csv = Path(args.level_stats_csv).resolve()
    step_checks_csv = Path(args.step_checks_csv).resolve()
    raw_summary_csv = Path(args.raw_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in [report_json, seed_checks_csv, level_stats_csv, step_checks_csv, raw_summary_csv]:
        if not p.exists():
            raise FileNotFoundError(f"missing input: {p}")

    report = json.loads(report_json.read_text(encoding="utf-8"))
    seed_rows = read_csv(seed_checks_csv)
    level_rows = read_csv(level_stats_csv)
    step_rows = read_csv(step_checks_csv)
    raw_rows = read_csv(raw_summary_csv)

    # Seed-level fail table
    bulk_fail_rows: list[dict[str, Any]] = []
    full_vs_bulk_rows: list[dict[str, Any]] = []
    fail_seeds: set[str] = set()
    for r in seed_rows:
        seed = str(r.get("seed", "")).strip()
        full_pass = str(r.get("full_pass", "")).strip().lower() == "true"
        bulk_pass = str(r.get("bulk_pass", "")).strip().lower() == "true"
        full_frac = to_float(r.get("full_step_fraction", "0"))
        bulk_frac = to_float(r.get("bulk_step_fraction", "0"))
        rho_full = to_float(r.get("rho_full", "0"))
        rho_bulk = to_float(r.get("rho_bulk", "0"))
        delta_frac = full_frac - bulk_frac
        delta_rho = rho_bulk - rho_full

        row = {
            "seed": seed,
            "full_pass": "true" if full_pass else "false",
            "bulk_pass": "true" if bulk_pass else "false",
            "full_step_fraction": f"{full_frac:.6f}",
            "bulk_step_fraction": f"{bulk_frac:.6f}",
            "delta_step_fraction_full_minus_bulk": f"{delta_frac:.6f}",
            "rho_full": f"{rho_full:.6f}",
            "rho_bulk": f"{rho_bulk:.6f}",
            "delta_rho_bulk_minus_full": f"{delta_rho:.6f}",
            "fail_mode": (
                "bulk_only_fail" if (full_pass and not bulk_pass) else
                "full_and_bulk_fail" if (not full_pass and not bulk_pass) else
                "full_only_fail" if (not full_pass and bulk_pass) else
                "pass"
            ),
        }
        full_vs_bulk_rows.append(row)
        if not bulk_pass:
            fail_seeds.add(seed)
            bulk_fail_rows.append(row)

    # Add worst bulk step deltas per fail seed
    step_by_seed: dict[str, list[dict[str, str]]] = {}
    for r in step_rows:
        if str(r.get("scope", "")).strip().lower() != "bulk":
            continue
        seed = str(r.get("seed", "")).strip()
        step_by_seed.setdefault(seed, []).append(r)

    for r in bulk_fail_rows:
        seed = str(r["seed"])
        srows = step_by_seed.get(seed, [])
        deltas = [to_float(x.get("delta", "0.0")) for x in srows]
        failed = [x for x in srows if str(x.get("step_pass", "")).strip().lower() != "true"]
        r["bulk_step_fail_count"] = len(failed)
        r["bulk_step_delta_max"] = f"{(max(deltas) if deltas else 0.0):.6f}"
        r["bulk_step_delta_min"] = f"{(min(deltas) if deltas else 0.0):.6f}"

    write_csv(
        out_dir / "bulk_fail_seeds.csv",
        bulk_fail_rows,
        [
            "seed",
            "fail_mode",
            "full_pass",
            "bulk_pass",
            "full_step_fraction",
            "bulk_step_fraction",
            "delta_step_fraction_full_minus_bulk",
            "rho_full",
            "rho_bulk",
            "delta_rho_bulk_minus_full",
            "bulk_step_fail_count",
            "bulk_step_delta_max",
            "bulk_step_delta_min",
        ],
    )
    write_csv(
        out_dir / "bulk_vs_full_delta.csv",
        full_vs_bulk_rows,
        [
            "seed",
            "fail_mode",
            "full_pass",
            "bulk_pass",
            "full_step_fraction",
            "bulk_step_fraction",
            "delta_step_fraction_full_minus_bulk",
            "rho_full",
            "rho_bulk",
            "delta_rho_bulk_minus_full",
        ],
    )

    # Per-seed regime feature table from raw summary
    raw_by_seed: dict[str, list[dict[str, str]]] = {}
    for r in raw_rows:
        seed = str(r.get("grid_seed", "")).strip()
        raw_by_seed.setdefault(seed, []).append(r)

    feature_rows: list[dict[str, Any]] = []
    for seed in sorted(raw_by_seed.keys(), key=lambda s: int(s) if s.isdigit() else s):
        rows = raw_by_seed[seed]
        n = len(rows)
        mean_active_ratio = avg([to_float(r.get("active_ratio", "0.0")) for r in rows])
        mean_cond = avg([to_float(r.get("metric_cond_max_seen", "0.0")) for r in rows])
        mean_residual = avg([to_float(r.get("max_residual", "0.0")) for r in rows])
        mean_energy = avg([to_float(r.get("delta_energy_rel", "0.0")) for r in rows])
        mean_noether = avg([to_float(r.get("energy_noether_rel", "0.0")) for r in rows])
        sparse_rate = avg([1.0 if to_float(r.get("edge_prob", "0.0")) <= 0.10 else 0.0 for r in rows])
        low_signal_rate = avg([1.0 if to_float(r.get("active_ratio", "0.0")) <= 0.05 else 0.0 for r in rows])
        noisy_rate = avg([1.0 if to_float(r.get("noise_level", "0.0")) >= 0.01 else 0.0 for r in rows])
        phi_shock_rate = avg([1.0 if to_float(r.get("phi_shock", "0.0")) > 0.0 else 0.0 for r in rows])
        near_cond_cap_rate = avg([1.0 if to_float(r.get("metric_cond_max_seen", "0.0")) >= 2.5 else 0.0 for r in rows])
        near_residual_cap_rate = avg([1.0 if to_float(r.get("max_residual", "0.0")) >= 0.5 else 0.0 for r in rows])
        drift_fail_rate = avg([1.0 if str(r.get("gate_energy_drift", "")).strip().lower() != "pass" else 0.0 for r in rows])
        fail_flag = 1.0 if seed in fail_seeds else 0.0

        feature_rows.append(
            {
                "seed": seed,
                "n_profiles": n,
                "bulk_fail_label": int(fail_flag),
                "mean_active_ratio": mean_active_ratio,
                "mean_metric_cond": mean_cond,
                "mean_residual": mean_residual,
                "mean_delta_energy_rel": mean_energy,
                "mean_energy_noether_rel": mean_noether,
                "sparse_rate": sparse_rate,
                "low_signal_rate": low_signal_rate,
                "noisy_rate": noisy_rate,
                "phi_shock_rate": phi_shock_rate,
                "near_cond_cap_rate": near_cond_cap_rate,
                "near_residual_cap_rate": near_residual_cap_rate,
                "drift_fail_rate": drift_fail_rate,
                "multi_peak_proxy_available": 0,
            }
        )

    features = [k for k in feature_rows[0].keys() if k not in {"seed", "n_profiles", "bulk_fail_label"}] if feature_rows else []
    labels = [float(r["bulk_fail_label"]) for r in feature_rows]
    corr_rows: list[dict[str, Any]] = []
    for f in features:
        vals = [float(r[f]) for r in feature_rows]
        corr = pearson(vals, labels)
        if corr is None:
            continue
        fail_vals = [vals[i] for i in range(len(vals)) if labels[i] > 0.5]
        pass_vals = [vals[i] for i in range(len(vals)) if labels[i] < 0.5]
        corr_rows.append(
            {
                "feature": f,
                "corr_with_bulk_fail": f"{corr:.6f}",
                "abs_corr": f"{abs(corr):.6f}",
                "fail_mean": f"{avg(fail_vals):.6f}" if fail_vals else "",
                "pass_mean": f"{avg(pass_vals):.6f}" if pass_vals else "",
                "delta_fail_minus_pass": f"{(avg(fail_vals) - avg(pass_vals)):.6f}" if fail_vals and pass_vals else "",
            }
        )
    corr_rows.sort(key=lambda r: float(r["abs_corr"]), reverse=True)
    write_csv(
        out_dir / "feature_correlations.csv",
        corr_rows,
        ["feature", "corr_with_bulk_fail", "abs_corr", "fail_mean", "pass_mean", "delta_fail_minus_pass"],
    )

    # Pattern summary from step failure shapes
    pattern_counter: Counter[str] = Counter()
    for r in bulk_fail_rows:
        seed = str(r["seed"])
        srows = step_by_seed.get(seed, [])
        fail_steps = [x for x in srows if str(x.get("step_pass", "")).strip().lower() != "true"]
        if not fail_steps:
            pattern_counter["bulk_fail_no_step_violation"] += 1
            continue
        deltas = [to_float(x.get("delta", "0.0")) for x in fail_steps]
        if deltas and max(deltas) > 0.01:
            pattern_counter["bulk_fail_large_positive_step_delta"] += 1
        else:
            pattern_counter["bulk_fail_small_positive_step_delta"] += 1
    pattern_rows = [{"pattern": k, "count": v} for k, v in pattern_counter.most_common()]
    write_csv(out_dir / "pattern_summary.csv", pattern_rows, ["pattern", "count"])

    # Top 3 cause hypotheses from strongest correlations
    top = corr_rows[:6]
    cause_lines: list[str] = []
    used = 0
    for r in top:
        feat = str(r["feature"])
        d = to_float(r.get("delta_fail_minus_pass", "0.0"), 0.0)
        if feat == "low_signal_rate":
            cause_lines.append(
                f"- low-signal concentration in failing seeds (delta fail-pass `{d:.3f}`) suggests bulk trend fragility in weak-support regime."
            )
            used += 1
        elif feat == "sparse_rate":
            cause_lines.append(
                f"- sparse graph share is higher in failing seeds (delta fail-pass `{d:.3f}`), consistent with noisier bulk ordering."
            )
            used += 1
        elif feat == "phi_shock_rate":
            cause_lines.append(
                f"- phase-shock proxy is elevated in failing seeds (delta fail-pass `{d:.3f}`), indicating mixing-like instability in bulk trend."
            )
            used += 1
        elif feat in {"mean_residual", "near_residual_cap_rate"}:
            cause_lines.append(
                f"- residual-related metrics rise in failing seeds (delta fail-pass `{d:.3f}`), implying numerical/stochastic contamination of bulk slope."
            )
            used += 1
        elif feat in {"mean_metric_cond", "near_cond_cap_rate"}:
            cause_lines.append(
                f"- conditioning-related metrics rise in failing seeds (delta fail-pass `{d:.3f}`), suggesting operator sensitivity in bulk subset."
            )
            used += 1
        if used >= 3:
            break
    while len(cause_lines) < 3:
        cause_lines.append("- additional cause requires richer per-node observables (multi-peak and topology-local diagnostics not present in v2 summary).")

    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Stability Convergence V2 Failure Taxonomy (v1)",
        "",
        f"- generated_utc: `{generated}`",
        f"- source_report: `{report_json.as_posix()}`",
        f"- source_seed_checks: `{seed_checks_csv.as_posix()}`",
        f"- source_raw_summary: `{raw_summary_csv.as_posix()}`",
        f"- convergence_decision: `{report.get('decision', '')}`",
        f"- seed_count: `{len(seed_rows)}`",
        f"- bulk_fail_seed_count: `{len(fail_seeds)}`",
        "",
        "## Dominant Fail Mode",
        "",
        f"- bulk_vs_full median delta step fraction (`full-bulk`): `{median([to_float(r.get('delta_step_fraction_full_minus_bulk','0.0')) for r in full_vs_bulk_rows]):.6f}`",
        f"- fail-mode distribution: `{dict(Counter([str(r['fail_mode']) for r in full_vs_bulk_rows]))}`",
        "",
        "## Top 3 Hypothesized Causes",
        "",
    ]
    lines.extend(cause_lines[:3])
    lines.extend(
        [
            "",
            "## Data Availability Notes",
            "",
            "- multi-peak flag is not directly available in stability convergence summaries.",
            "- `phi_shock_rate` is used as a mixing proxy for diagnostics only.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"bulk_fail_seeds_csv: {out_dir / 'bulk_fail_seeds.csv'}")
    print(f"bulk_vs_full_delta_csv: {out_dir / 'bulk_vs_full_delta.csv'}")
    print(f"feature_correlations_csv: {out_dir / 'feature_correlations.csv'}")
    print(f"pattern_summary_csv: {out_dir / 'pattern_summary.csv'}")
    print(f"report_md: {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
