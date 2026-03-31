#!/usr/bin/env python3
"""
Run G17a candidate-v4 (multi-window local-gap recovery) on frozen QM summaries.

Policy (candidate-only; no core threshold/formula edits):
- preserve source official decisions by default
- apply recovery only when all conditions hold:
  1) source G17 fails
  2) source G17a fails, while G17b/G17c/G17d pass
  3) multi-peak mixing flag is true
- compute local basin gap across fixed quantile windows and use max gap
- compare against the same G17a threshold parsed from metric_checks_qm.csv
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
    / "qm-g17a-candidate-v4"
    / "primary_ds002_003_006_s3401_3600"
)

THRESH_RE = re.compile(r"^\s*([<>])\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G17a candidate-v4 multi-window local-gap evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--basin-quantiles", default="0.10,0.15,0.22")
    p.add_argument("--mix-ratio-threshold", type=float, default=0.90)
    p.add_argument("--mix-distance-threshold", type=float, default=0.25)
    p.add_argument("--local-gap-max-modes", type=int, default=12)
    p.add_argument("--local-gap-iters", type=int, default=300)
    p.add_argument("--fallback-gap-threshold", type=float, default=0.01)
    return p.parse_args()


def parse_quantiles(text: str) -> list[float]:
    out: list[float] = []
    for tok in str(text).split(","):
        token = tok.strip()
        if not token:
            continue
        q = float(token)
        if q <= 0.0 or q > 1.0:
            continue
        out.append(q)
    if not out:
        out = [0.10, 0.15, 0.22]
    return sorted(set(out))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_threshold(expr: str, fallback: float) -> tuple[str, float]:
    m = THRESH_RE.match(str(expr or ""))
    if not m:
        return ">", float(fallback)
    return m.group(1), float(m.group(2))


def pass_threshold(value: float, cmp: str, thr: float) -> bool:
    if cmp == ">":
        return value > thr
    if cmp == "<":
        return value < thr
    return False


def get_g17a_threshold(mc_csv: Path, fallback: float) -> tuple[str, float, str]:
    rows = v2.read_csv(mc_csv)
    expr = ""
    for r in rows:
        if str(r.get("gate_id", "")).strip() == "G17a":
            expr = str(r.get("threshold", "")).strip()
            break
    cmp, thr = parse_threshold(expr, fallback)
    expr_norm = expr if expr else f"{cmp}{thr}"
    return cmp, thr, expr_norm


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
                "g17_v2_pass": sum(1 for r in sub if r["g17_status_v2"] == "pass"),
                "improved_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass"
                ),
                "degraded_g17": sum(
                    1 for r in sub if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail"
                ),
                "qm_lane_v1_pass": sum(1 for r in sub if r["all_pass_qm_lane_v1"] == "pass"),
                "qm_lane_v2_pass": sum(1 for r in sub if r["all_pass_qm_lane_v2"] == "pass"),
                "improved_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
                ),
                "degraded_qm_lane": sum(
                    1
                    for r in sub
                    if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
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

    source_rows = v2.read_csv(source_summary)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    quantiles = parse_quantiles(args.basin_quantiles)
    out_rows: list[dict[str, Any]] = []

    for srow in source_rows:
        dataset_id = str(srow.get("dataset_id", "")).strip()
        seed = int(str(srow.get("seed", "0")))
        run_root = v2.resolve_run_root(str(srow.get("run_root", "")))
        rel_run_root = run_root.resolve().relative_to(ROOT.resolve()).as_posix()

        g17_v1 = v2.norm_status(str(srow.get("g17_status", "")))
        g17a_v1 = v2.norm_status(str(srow.get("g17a_status_v2", srow.get("g17a_status_v1", ""))))
        g17b = v2.norm_status(str(srow.get("g17b_status", "")))
        g17c = v2.norm_status(str(srow.get("g17c_status", "")))
        g17d = v2.norm_status(str(srow.get("g17d_status", "")))
        g18 = v2.norm_status(str(srow.get("g18_status", "")))
        g19 = v2.norm_status(str(srow.get("g19_status", "")))
        g20 = v2.norm_status(str(srow.get("g20_status", "")))
        lane_v1 = v2.norm_status(str(srow.get("all_pass_qm_lane", "")))
        mixing = str(srow.get("multi_peak_mixing", "")).strip().lower() == "true"

        gap_max = 0.0
        gap_by_q: dict[str, float] = {}
        g17a_rule = "accept_source"

        g17a_v2 = g17a_v1
        if g17_v1 == "fail" and g17a_v1 == "fail" and g17b == "pass" and g17c == "pass" and g17d == "pass" and mixing:
            mc_csv = run_root / "g17" / "metric_checks_qm.csv"
            if not mc_csv.exists():
                raise FileNotFoundError(f"missing g17 metric file: {mc_csv}")
            cmp, thr, thr_expr = get_g17a_threshold(mc_csv, args.fallback_gap_threshold)
            for q in quantiles:
                feats = v2.compute_multi_peak_and_local_gap(
                    dataset_id=dataset_id,
                    seed=seed,
                    basin_quantile=q,
                    mix_ratio_threshold=args.mix_ratio_threshold,
                    mix_distance_threshold=args.mix_distance_threshold,
                    local_gap_max_modes=args.local_gap_max_modes,
                    local_gap_iters=args.local_gap_iters,
                )
                g = float(feats["g17a_gap_local"])
                gap_by_q[f"g17a_gap_local_q{int(round(100 * q)):02d}"] = g
                if g > gap_max:
                    gap_max = g
            if pass_threshold(gap_max, cmp, thr):
                g17a_v2 = "pass"
                g17a_rule = "multi_window_local_gap_recovery"
            else:
                g17a_v2 = "fail"
                g17a_rule = "retain_source_fail"
        else:
            thr_expr = str(args.fallback_gap_threshold)

        g17_v2 = "pass" if (g17a_v2 == "pass" and g17b == "pass" and g17c == "pass" and g17d == "pass") else "fail"
        lane_v2 = "pass" if (g17_v2 == "pass" and g18 == "pass" and g19 == "pass" and g20 == "pass") else "fail"

        rec: dict[str, Any] = {
            "dataset_id": dataset_id,
            "seed": seed,
            "run_root": rel_run_root,
            "g17_status_v1": g17_v1,
            "g17_status_v2": g17_v2,
            "g17a_status_v1": g17a_v1,
            "g17a_status_v2": g17a_v2,
            "g17a_v2_rule": g17a_rule,
            "g17a_gap_local_max": f"{gap_max:.12f}",
            "g17a_threshold_expr": thr_expr,
            "g17b_status": g17b,
            "g17c_status": g17c,
            "g17d_status": g17d,
            "g18_status": g18,
            "g19_status": g19,
            "g20_status": g20,
            "multi_peak_mixing": "true" if mixing else "false",
            "all_pass_qm_lane_v1": lane_v1,
            "all_pass_qm_lane_v2": lane_v2,
        }
        for q in quantiles:
            key = f"g17a_gap_local_q{int(round(100 * q)):02d}"
            rec[key] = f"{gap_by_q.get(key, 0.0):.12f}"
        out_rows.append(rec)

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g17_v1_pass = sum(1 for r in out_rows if r["g17_status_v1"] == "pass")
    g17_v2_pass = sum(1 for r in out_rows if r["g17_status_v2"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v2_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v2"] == "pass")
    improved_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "fail" and r["g17_status_v2"] == "pass")
    degraded_g17 = sum(1 for r in out_rows if r["g17_status_v1"] == "pass" and r["g17_status_v2"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
    )

    lines = [
        "# QM G17a Candidate-v4 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G17 v1 -> v2: `{g17_v1_pass}/{n} -> {g17_v2_pass}/{n}`",
        f"- QM lane v1 -> v2: `{lane_v1_pass}/{n} -> {lane_v2_pass}/{n}`",
        f"- improved_g17: `{improved_g17}`",
        f"- degraded_g17: `{degraded_g17}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- Candidate applies only to source fail profiles where only G17a blocks G17.",
        "- Uses fixed quantile windows and the same parsed G17a threshold from metric checks.",
        "- No threshold/formula edits in core runners.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g17a-candidate-v4-multiwindow",
        "basin_quantiles": quantiles,
        "mix_ratio_threshold": args.mix_ratio_threshold,
        "mix_distance_threshold": args.mix_distance_threshold,
        "local_gap_max_modes": args.local_gap_max_modes,
        "local_gap_iters": args.local_gap_iters,
        "notes": [
            "Candidate-only G17a multi-window local-gap recovery on g17a-only fail profiles.",
            "No threshold/formula edits in core gate scripts.",
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
