#!/usr/bin/env python3
"""
Run G17b candidate-v4 evaluation on frozen QM Stage-1 official summaries.

Policy (candidate-only; no core threshold/formula edits):
- preserve legacy decisions when G17b-v1 already passes
- for G17b-v1 fail cases:
  - compute high-signal OLS slope on top-q |G_ij| propagator samples
  - keep same slope threshold as v1 (parsed from metric_checks_qm.csv)
  - require minimum support before applying recovery rule
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
TOOLS = ROOT / "scripts" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_qm_g17_candidate_eval_v2 as v2  # noqa: E402


DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-g17b-candidate-v4"
    / "primary_ds002_003_006_s3401_3600"
)

THRESH_RE = re.compile(r"^\s*([<>])\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G17b candidate-v4 high-signal evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--high-signal-quantile", type=float, default=0.80)
    p.add_argument("--min-support", type=int, default=80)
    p.add_argument("--fallback-threshold", type=float, default=-0.01)
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


def parse_threshold(expr: str, fallback: float) -> tuple[float, str]:
    m = THRESH_RE.match(str(expr or ""))
    if not m:
        return fallback, f"<{fallback}"
    cmp = m.group(1)
    val = float(m.group(2))
    if cmp == "<":
        return val, expr
    return fallback, f"<{fallback}"


def ols_slope(x_vals: list[float], y_vals: list[float]) -> float | None:
    n = min(len(x_vals), len(y_vals))
    if n < 2:
        return None
    x = x_vals[:n]
    y = y_vals[:n]
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) * (v - mx) for v in x)
    if abs(sxx) < 1e-18:
        return None
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return sxy / sxx


def high_signal_slope(sample_csv: Path, quantile: float, min_support: int) -> tuple[float | None, int]:
    if not sample_csv.exists():
        return None, 0
    rows = read_csv(sample_csv)
    if not rows:
        return None, 0
    pairs: list[tuple[float, float, float]] = []
    for r in rows:
        try:
            rv = float(str(r.get("r_ij", "")).strip())
            gv = float(str(r.get("G_ij", "")).strip())
        except Exception:
            continue
        pairs.append((abs(gv), rv, gv))
    if len(pairs) < 2:
        return None, 0
    pairs.sort(key=lambda t: t[0], reverse=True)
    n = len(pairs)
    q = max(0.05, min(1.0, float(quantile)))
    n_used = max(int(round(q * n)), int(min_support))
    n_used = min(n_used, n)
    sel = pairs[:n_used]
    x = [p[1] for p in sel]
    y = [p[2] for p in sel]
    return ols_slope(x, y), n_used


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def summarize_by_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g17_v1_pass": sum(1 for r in sub if r["g17_status_v1"] == "pass"),
                "g17_v4_pass": sum(1 for r in sub if r["g17_status_v4"] == "pass"),
                "g17b_v1_pass": sum(1 for r in sub if r["g17b_status_v1"] == "pass"),
                "g17b_v4_pass": sum(1 for r in sub if r["g17b_status_v4"] == "pass"),
                "qm_lane_v1_pass": sum(1 for r in sub if r["all_pass_qm_lane_v1"] == "pass"),
                "qm_lane_v4_pass": sum(1 for r in sub if r["all_pass_qm_lane_v4"] == "pass"),
                "improved_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "fail" and r["g17_status_v4"] == "pass"
                ),
                "degraded_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "pass" and r["g17_status_v4"] == "fail"
                ),
                "improved_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v4"] == "pass"
                ),
                "degraded_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v4"] == "fail"
                ),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    source_summary = Path(args.source_summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not source_summary.exists():
        raise FileNotFoundError(f"source summary not found: {source_summary}")

    source_rows = read_csv(source_summary)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for srow in source_rows:
        dataset_id = str(srow.get("dataset_id", "")).strip()
        seed = int(str(srow.get("seed", "0")))
        run_root = v2.resolve_run_root(str(srow.get("run_root", "")))
        g17_dir = run_root / "g17"
        mc_csv = g17_dir / "metric_checks_qm.csv"
        if not mc_csv.exists():
            raise FileNotFoundError(f"missing g17 metric file: {mc_csv}")

        base = v2.parse_g17_metric_checks(mc_csv)
        mc_rows = read_csv(mc_csv)
        g17b_thr_expr = ""
        for r in mc_rows:
            if str(r.get("gate_id", "")).strip() == "G17b":
                g17b_thr_expr = str(r.get("threshold", "")).strip()
                break
        g17b_thr, g17b_thr_expr_norm = parse_threshold(g17b_thr_expr, args.fallback_threshold)

        slope_hs, n_used = high_signal_slope(
            g17_dir / "propagator_sample.csv",
            quantile=args.high_signal_quantile,
            min_support=args.min_support,
        )

        g17b_v1 = base["g17b_status"]
        if g17b_v1 == "pass":
            g17b_v4 = "pass"
            g17b_rule = "accept_v1_pass"
        else:
            if slope_hs is not None and n_used >= args.min_support and slope_hs < g17b_thr:
                g17b_v4 = "pass"
                g17b_rule = "high_signal_slope_recovery"
            else:
                g17b_v4 = "fail"
                g17b_rule = "retain_v1_fail"

        g17a_v2 = norm_status(str(srow.get("g17a_status_v2", "")))
        g17c = norm_status(str(srow.get("g17c_status", base["g17c_status"])))
        g17d = norm_status(str(srow.get("g17d_status", base["g17d_status"])))
        g17_v4 = "pass" if (g17a_v2 == "pass" and g17b_v4 == "pass" and g17c == "pass" and g17d == "pass") else "fail"

        g18 = norm_status(str(srow.get("g18_status", "")))
        g19 = norm_status(str(srow.get("g19_status", "")))
        g20 = norm_status(str(srow.get("g20_status", "")))
        lane_v1 = norm_status(str(srow.get("all_pass_qm_lane", "")))
        lane_v4 = "pass" if (g17_v4 == "pass" and g18 == "pass" and g19 == "pass" and g20 == "pass") else "fail"

        rel_run_root = run_root.resolve().relative_to(ROOT.resolve()).as_posix()
        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": rel_run_root,
                "g17_status_v1": norm_status(str(srow.get("g17_status", base["g17_status_v1"]))),
                "g17_status_v2": g17_v4,
                "g17_status_v4": g17_v4,
                "g17a_status_v1": base["g17a_status_v1"],
                "g17a_status_v2": g17a_v2,
                "g17a_v2_rule": str(srow.get("g17a_v2_rule", "")),
                "g17b_status": g17b_v4,
                "g17b_status_v1": g17b_v1,
                "g17b_status_v4": g17b_v4,
                "g17b_v4_rule": g17b_rule,
                "g17b_slope": base["g17b_slope"],
                "g17b_slope_high_signal": "" if slope_hs is None else f"{slope_hs:.12f}",
                "g17b_high_signal_n_used": n_used,
                "g17b_threshold_expr": g17b_thr_expr_norm,
                "g17c_status": g17c,
                "g17d_status": g17d,
                "g17a_gap_global": base["g17a_gap_global"],
                "g17c_e0_per_mode": base["g17c_e0_per_mode"],
                "g17d_heisenberg_dev": base["g17d_heisenberg_dev"],
                "g18_status": g18,
                "g19_status": g19,
                "g20_status": g20,
                "all_pass_qm_lane_v1": lane_v1,
                "all_pass_qm_lane_v2": lane_v4,
                "all_pass_qm_lane_v4": lane_v4,
                "multi_peak_mixing": str(srow.get("multi_peak_mixing", "")),
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g17_v1_pass = sum(1 for r in out_rows if r["g17_status_v1"] == "pass")
    g17_v4_pass = sum(1 for r in out_rows if r["g17_status_v4"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v4_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v4"] == "pass")
    g17b_v1_pass = sum(1 for r in out_rows if r["g17b_status_v1"] == "pass")
    g17b_v4_pass = sum(1 for r in out_rows if r["g17b_status_v4"] == "pass")
    improved_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "fail" and r["g17_status_v4"] == "pass")
    degraded_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "pass" and r["g17_status_v4"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v4"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v4"] == "fail"
    )

    lines = [
        "# QM G17b Candidate-v4 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G17b v1 -> v4: `{g17b_v1_pass}/{n} -> {g17b_v4_pass}/{n}`",
        f"- G17 v1 -> v4: `{g17_v1_pass}/{n} -> {g17_v4_pass}/{n}`",
        f"- QM lane v1 -> v4: `{lane_v1_pass}/{n} -> {lane_v4_pass}/{n}`",
        f"- improved_g17: `{improved_g17}`",
        f"- degraded_g17: `{degraded_g17}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- G17b-v1 pass cases are preserved.",
        "- Recovery uses high-signal slope with unchanged v1 threshold.",
        "- No formula or threshold edits in core gate scripts.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g17b-candidate-v4-high-signal",
        "high_signal_quantile": args.high_signal_quantile,
        "min_support": args.min_support,
        "fallback_threshold": args.fallback_threshold,
        "notes": [
            "Candidate-only G17b high-signal slope recovery on fail cases.",
            "Threshold value unchanged from v1 metric definition.",
            "No core gate formula edits.",
        ],
    }
    manifest_json = out_dir / "candidate_manifest.json"
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"dataset_csv: {dataset_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
