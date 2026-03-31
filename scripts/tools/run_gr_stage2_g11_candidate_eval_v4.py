#!/usr/bin/env python3
"""
Evaluate G11a-v4 candidate-only decision layer over Stage-2 summary packages.

Policy:
- no edits to official gate scripts
- candidate is computed in post-processing from existing run artifacts
- v3 remains official baseline for this evaluation

G11a-v4 candidate core:
- keeps v3 Poisson-source high-signal construction (same quantile/smoothing)
- adds robust rank fallback for v3-fail rows:
  - Spearman on high-signal subset
  - Spearman on trimmed high-signal subset (drop 10% low/high |R_smooth|)
  - pass if either rank metric satisfies |rho| >= 0.20
- no threshold tuning (0.20 kept)
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS_DIR = ROOT / "scripts" / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from run_gr_stage2_g11_candidate_eval_v3 import (  # noqa: E402
    f6,
    g11_v3_poisson_rule,
    get_first,
    laplacian_rw,
    norm_status,
    percentile,
    read_csv,
    smooth_values,
    to_float,
    write_csv,
)
from run_qng_gr_solutions_v1 import build_dataset_graph  # noqa: E402


DEFAULT_SOURCE_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-official-v3"
    / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "gr-stage2-g11-candidate-v4"
)

HIGH_SIGNAL_QUANTILE = 0.80
CORR_MIN = 0.20
R_SMOOTH_ALPHA = 0.50
R_SMOOTH_ITERS = 1
TRIM_FRACTION = 0.10


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate Stage-2 G11a-v4 candidate-only layer.")
    p.add_argument("--source-summary-csv", default=str(DEFAULT_SOURCE_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--high-signal-quantile", type=float, default=HIGH_SIGNAL_QUANTILE)
    p.add_argument("--corr-min", type=float, default=CORR_MIN)
    p.add_argument("--r-smooth-alpha", type=float, default=R_SMOOTH_ALPHA)
    p.add_argument("--r-smooth-iters", type=int, default=R_SMOOTH_ITERS)
    p.add_argument("--trim-fraction", type=float, default=TRIM_FRACTION)
    return p.parse_args()


def trimmed_order_indices(values: list[float], trim_fraction: float, min_keep: int = 6) -> list[int]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    k = int(len(order) * max(0.0, min(0.45, trim_fraction)))
    kept = order[k : len(order) - k]
    if len(kept) < min_keep:
        return order
    return kept


def rank_corr_trimmed(
    source_vals: list[float],
    target_vals: list[float],
    high_signal_quantile: float,
    corr_min: float,
    trim_fraction: float,
) -> dict[str, Any]:
    n = min(len(source_vals), len(target_vals))
    if n < 6:
        return {
            "hs_count": 0,
            "hs_count_trimmed": 0,
            "s_threshold": float("nan"),
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "spearman_hs_trimmed": float("nan"),
            "rank_or_pass": False,
            "pearson_collapse_flag": False,
            "weak_rank_flag": True,
        }

    s = source_vals[:n]
    t = target_vals[:n]
    s_thr = percentile(s, high_signal_quantile)
    idx = [i for i, v in enumerate(s) if v >= s_thr]
    if len(idx) < 6:
        return {
            "hs_count": len(idx),
            "hs_count_trimmed": len(idx),
            "s_threshold": s_thr,
            "spearman_hs": float("nan"),
            "pearson_hs": float("nan"),
            "spearman_hs_trimmed": float("nan"),
            "rank_or_pass": False,
            "pearson_collapse_flag": False,
            "weak_rank_flag": True,
        }

    hs_s = [s[i] for i in idx]
    hs_t = [t[i] for i in idx]

    from run_gr_stage2_g11_candidate_eval_v3 import pearson_corr, spearman_corr  # local import to avoid lint noise

    sp_hs = spearman_corr(hs_s, hs_t)
    pe_hs = pearson_corr(hs_s, hs_t)

    keep = trimmed_order_indices(hs_t, trim_fraction=trim_fraction, min_keep=6)
    hs_s_t = [hs_s[i] for i in keep]
    hs_t_t = [hs_t[i] for i in keep]
    sp_hs_t = spearman_corr(hs_s_t, hs_t_t)

    sp_ok = (not math.isnan(sp_hs)) and (abs(sp_hs) >= corr_min)
    sp_t_ok = (not math.isnan(sp_hs_t)) and (abs(sp_hs_t) >= corr_min)
    pe_ok = (not math.isnan(pe_hs)) and (abs(pe_hs) >= corr_min)

    rank_or = sp_ok or sp_t_ok
    return {
        "hs_count": len(idx),
        "hs_count_trimmed": len(keep),
        "s_threshold": s_thr,
        "spearman_hs": sp_hs,
        "pearson_hs": pe_hs,
        "spearman_hs_trimmed": sp_hs_t,
        "rank_or_pass": rank_or,
        "pearson_collapse_flag": rank_or and (not pe_ok),
        "weak_rank_flag": (not rank_or),
    }


def gate_from_statuses(*statuses: str) -> str:
    return "pass" if all(norm_status(s) == "pass" for s in statuses) else "fail"


def main() -> int:
    args = parse_args()
    source_csv = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")

    src_rows = read_csv(source_csv)
    if not src_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []

    for row in src_rows:
        dataset_id = str(row["dataset_id"])
        seed = int(str(row["seed"]))
        run_root = (ROOT / row["run_root"]).resolve()

        g10_status = norm_status(get_first(row, ["g10_status", "g10_v1_status"]))
        g12_status = norm_status(get_first(row, ["g12_status", "g12_v2_status", "g12_v1_status"]))
        g7_status = norm_status(get_first(row, ["g7_status", "g7_v1_status"]))
        g11_v3_status = norm_status(get_first(row, ["g11_status", "g11_v3_status"]))

        g11b_status = norm_status(get_first(row, ["g11b", "g11b_status", "g11b_v1_status"]))
        g11c_status = norm_status(get_first(row, ["g11c", "g11c_status", "g11c_v1_status"]))
        g11d_status = norm_status(get_first(row, ["g11d", "g11d_status", "g11d_v1_status"]))

        eq_csv = run_root / "g11" / "einstein_eq.csv"
        eq_rows = read_csv(eq_csv) if eq_csv.exists() else []
        r_vals: list[float] = []
        sigma_norm: list[float] = []
        for r in eq_rows:
            rv = to_float(r.get("R", ""))
            sv = to_float(r.get("sigma_norm", ""))
            if rv is None or sv is None:
                continue
            r_vals.append(rv)
            sigma_norm.append(sv)

        _, _, adj_w = build_dataset_graph(dataset_id, seed)
        neighbours = [[j for j, _ in nb] for nb in adj_w]
        n = min(len(r_vals), len(sigma_norm), len(neighbours))
        r_vals = r_vals[:n]
        sigma_norm = sigma_norm[:n]
        neighbours = neighbours[:n]

        v3_diag = g11_v3_poisson_rule(
            r_vals=r_vals,
            sigma_norm=sigma_norm,
            neighbours=neighbours,
            high_signal_quantile=args.high_signal_quantile,
            corr_min=args.corr_min,
            smooth_alpha=args.r_smooth_alpha,
            smooth_iters=args.r_smooth_iters,
        )

        r_smooth = smooth_values(r_vals, neighbours, alpha=args.r_smooth_alpha, iters=args.r_smooth_iters)
        target_vals = [abs(v) for v in r_smooth]
        source_vals = [abs(v) for v in laplacian_rw(sigma_norm, neighbours)]
        v4_rank = rank_corr_trimmed(
            source_vals=source_vals,
            target_vals=target_vals,
            high_signal_quantile=args.high_signal_quantile,
            corr_min=args.corr_min,
            trim_fraction=args.trim_fraction,
        )

        g11a_v4_fallback = (
            g11b_status == "pass"
            and g11c_status == "pass"
            and g11d_status == "pass"
            and bool(v4_rank["rank_or_pass"])
        )
        g11_v4_status = "pass" if (g11_v3_status == "pass" or g11a_v4_fallback) else "fail"

        stage2_v3 = gate_from_statuses(g10_status, g11_v3_status, g12_status, g7_status)
        stage2_v4 = gate_from_statuses(g10_status, g11_v4_status, g12_status, g7_status)

        fail_signature = "none"
        if g11_v4_status != "pass":
            if g11b_status != "pass":
                fail_signature = "g11b_slope_fail"
            elif bool(v4_rank["weak_rank_flag"]):
                fail_signature = "weak_rank_corr"
            elif bool(v4_rank["pearson_collapse_flag"]):
                fail_signature = "rank_monotonic_pearson_collapse"
            else:
                fail_signature = "mixed_other"

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": row["run_root"],
                "g10_status": g10_status,
                "g12_status": g12_status,
                "g7_status": g7_status,
                "g11b_status": g11b_status,
                "g11c_status": g11c_status,
                "g11d_status": g11d_status,
                "g11_v3_status": g11_v3_status,
                "g11_v4_status": g11_v4_status,
                "g11a_v4_fallback_pass": "true" if g11a_v4_fallback else "false",
                "g11_poisson_spearman_hs": f6(v3_diag["spearman_hs"]),
                "g11_poisson_pearson_hs": f6(v3_diag["pearson_hs"]),
                "g11_poisson_rule_pass": "true" if bool(v3_diag["rule_pass"]) else "false",
                "g11_v4_s_threshold": f6(v4_rank["s_threshold"]),
                "g11_v4_hs_count": int(v4_rank["hs_count"]),
                "g11_v4_hs_trimmed_count": int(v4_rank["hs_count_trimmed"]),
                "g11_v4_spearman_hs": f6(v4_rank["spearman_hs"]),
                "g11_v4_pearson_hs": f6(v4_rank["pearson_hs"]),
                "g11_v4_spearman_hs_trimmed": f6(v4_rank["spearman_hs_trimmed"]),
                "g11_v4_rank_or_pass": "true" if bool(v4_rank["rank_or_pass"]) else "false",
                "g11_v4_pearson_collapse_flag": "true" if bool(v4_rank["pearson_collapse_flag"]) else "false",
                "g11_v4_weak_rank_flag": "true" if bool(v4_rank["weak_rank_flag"]) else "false",
                "g11_v4_fail_signature": fail_signature,
                "stage2_v3_status": stage2_v3,
                "stage2_v4_status": stage2_v4,
            }
        )

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    n = len(out_rows)
    g11_v3_pass = sum(1 for r in out_rows if r["g11_v3_status"] == "pass")
    g11_v4_pass = sum(1 for r in out_rows if r["g11_v4_status"] == "pass")
    improved = sum(1 for r in out_rows if r["g11_v3_status"] == "fail" and r["g11_v4_status"] == "pass")
    degraded = sum(1 for r in out_rows if r["g11_v3_status"] == "pass" and r["g11_v4_status"] == "fail")
    stage2_v3_pass = sum(1 for r in out_rows if r["stage2_v3_status"] == "pass")
    stage2_v4_pass = sum(1 for r in out_rows if r["stage2_v4_status"] == "pass")

    report_lines = [
        "# GR Stage-2 G11 Candidate Evaluation (v4)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary: `{source_csv.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## G11 Counts (v3 -> v4)",
        "",
        f"- g11_v3_pass: `{g11_v3_pass}/{n}`",
        f"- g11_v4_pass: `{g11_v4_pass}/{n}`",
        f"- improved_vs_v3: `{improved}`",
        f"- degraded_vs_v3: `{degraded}`",
        "",
        "## Stage-2 Counts (v3 -> v4)",
        "",
        f"- stage2_v3_pass: `{stage2_v3_pass}/{n}`",
        f"- stage2_v4_pass: `{stage2_v4_pass}/{n}`",
        "",
        "## Notes",
        "",
        "- v4 is candidate-only in this script (no official switch).",
        "- thresholds are unchanged (`corr_min=0.20`), with robust rank estimator added.",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_csv.as_posix(),
        "constants": {
            "high_signal_quantile": args.high_signal_quantile,
            "corr_min": args.corr_min,
            "r_smooth_alpha": args.r_smooth_alpha,
            "r_smooth_iters": args.r_smooth_iters,
            "trim_fraction": args.trim_fraction,
        },
        "notes": [
            "No edits to official gate scripts.",
            "Candidate v4 computed from frozen run artifacts.",
            "No threshold tuning; robust rank fallback reuses corr_min=0.20.",
        ],
    }
    (out_dir / "prereg_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {out_dir / 'report.md'}")
    print(f"manifest:    {out_dir / 'prereg_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
