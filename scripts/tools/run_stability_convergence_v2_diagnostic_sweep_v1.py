#!/usr/bin/env python3
"""
Diagnostic-only sweep for convergence-v2 bulk mask sensitivity.

Important:
- This script is not a promotion evaluator.
- Results must not be used for post-hoc threshold selection.
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
DEFAULT_RAW = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v2" / "raw" / "summary.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v2-diagnostic-sweep-v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run convergence-v2 diagnostic bulk sweep.")
    p.add_argument("--raw-summary-csv", default=str(DEFAULT_RAW))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--seed-field", default="grid_seed")
    p.add_argument("--n-nodes-field", default="n_nodes")
    p.add_argument("--metric-field", default="delta_energy_rel")
    p.add_argument("--mask-quantiles", default="0.00,0.25,0.50,0.75")
    p.add_argument("--bulk-levels", default="30,36,42")
    p.add_argument("--min-profiles-per-level", type=int, default=5)
    return p.parse_args()


def parse_float_list(raw: str) -> list[float]:
    out: list[float] = []
    for x in raw.split(","):
        t = x.strip()
        if t:
            out.append(float(t))
    if not out:
        raise ValueError("empty float list")
    return out


def parse_int_list(raw: str) -> list[int]:
    out: list[int] = []
    for x in raw.split(","):
        t = x.strip()
        if t:
            out.append(int(t))
    if not out:
        raise ValueError("empty int list")
    return out


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


def avg(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def rankdata(vals: list[float]) -> list[float]:
    idx = sorted(range(len(vals)), key=lambda i: vals[i])
    out = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[idx[j + 1]] == vals[idx[i]]:
            j += 1
        r = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[idx[k]] = r
        i = j + 1
    return out


def pearson(xs: list[float], ys: list[float]) -> float:
    mx = avg(xs)
    my = avg(ys)
    sxx = sum((x - mx) * (x - mx) for x in xs)
    syy = sum((y - my) * (y - my) for y in ys)
    if sxx <= 1e-18 or syy <= 1e-18:
        return 0.0
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs)))
    return sxy / math.sqrt(sxx * syy)


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def main() -> int:
    args = parse_args()
    raw_csv = Path(args.raw_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not raw_csv.exists():
        raise FileNotFoundError(f"raw summary missing: {raw_csv}")

    mask_qs = parse_float_list(args.mask_quantiles)
    bulk_levels = parse_int_list(args.bulk_levels)
    raw_rows = read_csv(raw_csv)
    if not raw_rows:
        raise RuntimeError("raw summary has zero rows")

    by_seed: dict[str, list[dict[str, str]]] = {}
    for r in raw_rows:
        seed = str(r.get(args.seed_field, "")).strip()
        by_seed.setdefault(seed, []).append(r)

    detail_rows: list[dict[str, Any]] = []
    for q in mask_qs:
        for seed, srows in by_seed.items():
            active_vals = [to_float(r.get("active_ratio", "0.0")) for r in srows]
            thr = percentile(active_vals, q)
            filtered = [r for r in srows if to_float(r.get("active_ratio", "0.0")) >= thr]

            med_map: dict[int, float] = {}
            nsel_map: dict[int, int] = {}
            for n in bulk_levels:
                lvl = [r for r in filtered if int(str(r.get(args.n_nodes_field, "0"))) == n]
                vals = [to_float(r.get(args.metric_field, "0.0")) for r in lvl]
                nsel_map[n] = len(vals)
                if len(vals) >= args.min_profiles_per_level:
                    med_map[n] = median(vals)

            enough = all(n in med_map for n in bulk_levels)
            rho = ""
            step_frac = ""
            if enough:
                xs = [float(n) for n in bulk_levels]
                ys = [med_map[n] for n in bulk_levels]
                rho_val = spearman(xs, ys)
                rho = f"{rho_val:.6f}"
                pass_count = 0
                for i in range(len(bulk_levels) - 1):
                    n0 = bulk_levels[i]
                    n1 = bulk_levels[i + 1]
                    if med_map[n1] <= med_map[n0]:
                        pass_count += 1
                step_frac = f"{(pass_count / max(1, len(bulk_levels)-1)):.6f}"

            detail_rows.append(
                {
                    "mask_strategy": "active_ratio_quantile",
                    "bulk_mask_param": f"{q:.2f}",
                    "seed": seed,
                    "active_ratio_threshold": f"{thr:.6f}",
                    "n_selected_total": len(filtered),
                    "n_selected_30": nsel_map.get(30, 0),
                    "n_selected_36": nsel_map.get(36, 0),
                    "n_selected_42": nsel_map.get(42, 0),
                    "bulk_rho": rho,
                    "bulk_step_fraction": step_frac,
                    "enough_samples": "true" if enough else "false",
                }
            )

    write_csv(
        out_dir / "bulk_rho_sweep.csv",
        detail_rows,
        [
            "mask_strategy",
            "bulk_mask_param",
            "seed",
            "active_ratio_threshold",
            "n_selected_total",
            "n_selected_30",
            "n_selected_36",
            "n_selected_42",
            "bulk_rho",
            "bulk_step_fraction",
            "enough_samples",
        ],
    )

    agg_rows: list[dict[str, Any]] = []
    for q in mask_qs:
        sub = [r for r in detail_rows if r["bulk_mask_param"] == f"{q:.2f}"]
        ok = [r for r in sub if r["enough_samples"] == "true" and str(r["bulk_rho"]).strip() != ""]
        rho_vals = [to_float(r["bulk_rho"]) for r in ok]
        step_vals = [to_float(r["bulk_step_fraction"]) for r in ok]
        agg_rows.append(
            {
                "mask_strategy": "active_ratio_quantile",
                "bulk_mask_param": f"{q:.2f}",
                "seed_count_total": len(sub),
                "seed_count_valid": len(ok),
                "bulk_rho_mean": f"{avg(rho_vals):.6f}" if rho_vals else "",
                "bulk_rho_median": f"{median(rho_vals):.6f}" if rho_vals else "",
                "bulk_step_fraction_mean": f"{avg(step_vals):.6f}" if step_vals else "",
                "bulk_step_fraction_median": f"{median(step_vals):.6f}" if step_vals else "",
            }
        )
    write_csv(
        out_dir / "bulk_rho_heatmap.csv",
        agg_rows,
        [
            "mask_strategy",
            "bulk_mask_param",
            "seed_count_total",
            "seed_count_valid",
            "bulk_rho_mean",
            "bulk_rho_median",
            "bulk_step_fraction_mean",
            "bulk_step_fraction_median",
        ],
    )

    lines = [
        "# Stability Convergence V2 Diagnostic Sweep (v1)",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- raw_summary_csv: `{raw_csv.as_posix()}`",
        "- mode: `diagnostic-only`",
        "- note: `not for promotion / not for threshold selection`",
        "",
        "## Sweep Axis",
        "",
        f"- mask_strategy: `active_ratio_quantile`",
        f"- bulk_mask_param values: `{','.join(f'{q:.2f}' for q in mask_qs)}`",
        "",
        "## Outputs",
        "",
        f"- detail: `{(out_dir / 'bulk_rho_sweep.csv').as_posix()}`",
        f"- aggregate heatmap: `{(out_dir / 'bulk_rho_heatmap.csv').as_posix()}`",
    ]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "report.json").write_text(
        json.dumps(
            {
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "raw_summary_csv": raw_csv.as_posix(),
                "mode": "diagnostic-only",
                "mask_strategy": "active_ratio_quantile",
                "bulk_mask_params": [round(q, 2) for q in mask_qs],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"bulk_rho_sweep_csv: {out_dir / 'bulk_rho_sweep.csv'}")
    print(f"bulk_rho_heatmap_csv: {out_dir / 'bulk_rho_heatmap.csv'}")
    print(f"report_md: {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
