#!/usr/bin/env python3
"""
Strict fail-closure taxonomy for Stage-2 official-v3 G11 failures.

Scope:
- analyze only rows with `g11_status=fail` from official-v3 summary
- attach nearest pass neighbors (same dataset, nearest seeds)
- produce compact class map for v4 candidate design
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = ROOT / "scripts" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from run_gr_stage2_g11_candidate_eval_v4 import (  # noqa: E402
    rank_corr_trimmed,
    read_csv,
    smooth_values,
    laplacian_rw,
    norm_status,
    to_float,
    f6,
    write_csv,
)
from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v3-rerun-v3-600-v1"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-g11-fail-closure-v3-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze strict Stage-2 official-v3 G11 fail-closure.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--neighbor-k", type=int, default=2)
    p.add_argument("--high-signal-quantile", type=float, default=0.80)
    p.add_argument("--corr-min", type=float, default=0.20)
    p.add_argument("--r-smooth-alpha", type=float, default=0.50)
    p.add_argument("--r-smooth-iters", type=int, default=1)
    p.add_argument("--trim-fraction", type=float, default=0.10)
    return p.parse_args()


def multi_peak_flag(coords: list[tuple[float, float]], sigma: list[float], ratio_thr: float = 0.98, dist_thr: float = 0.10) -> tuple[bool, float, float]:
    if len(sigma) < 2:
        return (False, 0.0, 0.0)
    top = sorted(range(len(sigma)), key=lambda i: sigma[i], reverse=True)[:2]
    i1, i2 = top[0], top[1]
    ratio = sigma[i2] / max(sigma[i1], 1e-12)
    x_min = min(c[0] for c in coords)
    x_max = max(c[0] for c in coords)
    y_min = min(c[1] for c in coords)
    y_max = max(c[1] for c in coords)
    diag = math.hypot(x_max - x_min, y_max - y_min)
    dist = math.hypot(coords[i1][0] - coords[i2][0], coords[i1][1] - coords[i2][1])
    dist_norm = dist / max(diag, 1e-12)
    return ((ratio >= ratio_thr) and (dist_norm <= dist_thr), ratio, dist_norm)


def classify_fail(row: dict[str, Any], corr_min: float) -> str:
    g11b_status = norm_status(str(row.get("g11b_status", "")))
    sp = abs(to_float(str(row.get("spearman_hs", ""))) or float("nan"))
    pe = abs(to_float(str(row.get("pearson_hs", ""))) or float("nan"))
    sp_t = abs(to_float(str(row.get("spearman_hs_trimmed", ""))) or float("nan"))
    rank_or = str(row.get("rank_or_pass", "")).strip().lower() == "true"
    mp = str(row.get("multi_peak_flag", "")).strip().lower() == "true"

    if g11b_status != "pass":
        return "g11b_slope_fail"
    if rank_or and (not math.isnan(pe)) and pe < corr_min:
        return "rank_monotonic_pearson_collapse"
    if (not rank_or) and mp:
        return "multi_peak_weak_rank"
    if (not rank_or) and (not math.isnan(sp)) and (not math.isnan(sp_t)):
        return "weak_rank_corr"
    return "mixed_other"


def nearest_passes(fail_row: dict[str, Any], pass_rows: list[dict[str, Any]], k: int) -> list[dict[str, Any]]:
    ds = str(fail_row["dataset_id"])
    seed = int(fail_row["seed"])
    cand = [r for r in pass_rows if str(r["dataset_id"]) == ds]
    cand.sort(key=lambda r: (abs(int(r["seed"]) - seed), int(r["seed"])))
    return cand[: max(0, k)]


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    src_rows = read_csv(summary_csv)
    if not src_rows:
        raise RuntimeError("summary has zero rows")

    rows: list[dict[str, Any]] = []
    for src in src_rows:
        dataset_id = str(src["dataset_id"])
        seed = int(str(src["seed"]))
        run_root = str(src["run_root"])
        g11_status = norm_status(str(src.get("g11_status", "")))
        g11b_status = norm_status(str(src.get("g11b", "")))
        g11c_status = norm_status(str(src.get("g11c", "")))
        g11d_status = norm_status(str(src.get("g11d", "")))

        eq_csv = (ROOT / run_root / "g11" / "einstein_eq.csv").resolve()
        eq_rows = read_csv(eq_csv) if eq_csv.exists() else []
        r_vals: list[float] = []
        sigma_norm: list[float] = []
        for eq in eq_rows:
            rv = to_float(eq.get("R", ""))
            sv = to_float(eq.get("sigma_norm", ""))
            if rv is None or sv is None:
                continue
            r_vals.append(rv)
            sigma_norm.append(sv)

        coords, sigma, adj = build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj]
        n = min(len(r_vals), len(sigma_norm), len(neighbours), len(coords), len(sigma))
        r_vals = r_vals[:n]
        sigma_norm = sigma_norm[:n]
        neighbours = neighbours[:n]
        coords = coords[:n]
        sigma = sigma[:n]

        r_smooth = smooth_values(r_vals, neighbours, alpha=args.r_smooth_alpha, iters=args.r_smooth_iters)
        target_vals = [abs(v) for v in r_smooth]
        source_vals = [abs(v) for v in laplacian_rw(sigma_norm, neighbours)]
        diag = rank_corr_trimmed(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.high_signal_quantile,
            corr_min=args.corr_min,
            trim_fraction=args.trim_fraction,
        )
        mp_flag, peak_ratio, peak_dist_norm = multi_peak_flag(coords, sigma)

        rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": run_root,
                "g11_status": g11_status,
                "g11b_status": g11b_status,
                "g11c_status": g11c_status,
                "g11d_status": g11d_status,
                "hs_count": int(diag["hs_count"]),
                "hs_trimmed_count": int(diag["hs_count_trimmed"]),
                "spearman_hs": f6(diag["spearman_hs"]),
                "pearson_hs": f6(diag["pearson_hs"]),
                "spearman_hs_trimmed": f6(diag["spearman_hs_trimmed"]),
                "rank_or_pass": "true" if bool(diag["rank_or_pass"]) else "false",
                "pearson_collapse_flag": "true" if bool(diag["pearson_collapse_flag"]) else "false",
                "weak_rank_flag": "true" if bool(diag["weak_rank_flag"]) else "false",
                "multi_peak_flag": "true" if mp_flag else "false",
                "sigma_peak2_to_peak1": f6(peak_ratio),
                "peak12_distance_norm": f6(peak_dist_norm),
            }
        )

    pass_rows = [r for r in rows if r["g11_status"] == "pass"]
    fail_rows = [r for r in rows if r["g11_status"] != "pass"]
    if not fail_rows:
        raise RuntimeError("no g11 fail rows found in summary")

    summary_rows: list[dict[str, Any]] = []
    for fr in fail_rows:
        out = dict(fr)
        out["fail_class"] = classify_fail(fr, corr_min=args.corr_min)
        near = nearest_passes(fr, pass_rows, args.neighbor_k)
        for i in range(max(0, args.neighbor_k)):
            pref = f"neighbor{i+1}"
            if i < len(near):
                nr = near[i]
                out[f"{pref}_seed"] = nr["seed"]
                out[f"{pref}_seed_delta"] = abs(int(nr["seed"]) - int(fr["seed"]))
                out[f"{pref}_spearman_hs"] = nr["spearman_hs"]
                out[f"{pref}_pearson_hs"] = nr["pearson_hs"]
                out[f"{pref}_spearman_hs_trimmed"] = nr["spearman_hs_trimmed"]
                out[f"{pref}_rank_or_pass"] = nr["rank_or_pass"]
            else:
                out[f"{pref}_seed"] = ""
                out[f"{pref}_seed_delta"] = ""
                out[f"{pref}_spearman_hs"] = ""
                out[f"{pref}_pearson_hs"] = ""
                out[f"{pref}_spearman_hs_trimmed"] = ""
                out[f"{pref}_rank_or_pass"] = ""
        summary_rows.append(out)

    class_counts: dict[str, int] = {}
    for r in summary_rows:
        k = str(r["fail_class"])
        class_counts[k] = class_counts.get(k, 0) + 1
    class_rows = [
        {
            "fail_class": k,
            "count": v,
            "rate_pct": f"{100.0 * v / len(summary_rows):.3f}",
        }
        for k, v in sorted(class_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]

    write_csv(out_dir / "summary.csv", summary_rows, list(summary_rows[0].keys()))
    write_csv(out_dir / "class_summary.csv", class_rows, ["fail_class", "count", "rate_pct"])

    lines: list[str] = []
    lines.append("# GR Stage-2 G11 Fail-Closure Taxonomy (official-v3, strict)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    lines.append(f"- total_profiles: `{len(rows)}`")
    lines.append(f"- g11_fails_strict: `{len(summary_rows)}`")
    lines.append(f"- neighbor_k: `{args.neighbor_k}`")
    lines.append("")
    lines.append("## Dominant Classes")
    lines.append("")
    for r in class_rows:
        lines.append(f"- `{r['fail_class']}`: `{r['count']}`")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Classes are assigned only on fail rows.")
    lines.append("- Nearest-pass neighbors are selected within the same dataset by seed distance.")
    lines.append("- Corr threshold remains frozen at `0.20`.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("- `summary.csv`")
    lines.append("- `class_summary.csv`")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"summary_csv:       {out_dir / 'summary.csv'}")
    print(f"class_summary_csv: {out_dir / 'class_summary.csv'}")
    print(f"report_md:         {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
