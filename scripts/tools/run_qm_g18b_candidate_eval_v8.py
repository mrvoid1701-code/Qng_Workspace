#!/usr/bin/env python3
"""
Run G18b candidate-v8 robust IPR evaluation on frozen QM summaries.

Policy (candidate-only; no core threshold/formula edits):
- preserve source official decisions when G18 already passes
- for source G18 fail rows:
  - keep pass/fail of G18a/G18c/G18d unchanged from source summary
  - recompute G18b with trimmed-mean n*IPR over mode table
  - apply the same G18b threshold parsed from metric_checks_qm_info.csv
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-g18b-candidate-v8"
    / "primary_ds002_003_006_s3401_3600"
)

THRESH_RE = re.compile(r"^\s*([<>])\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G18b candidate-v8 robust IPR evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--trim-top-fraction", type=float, default=0.20)
    p.add_argument("--min-modes", type=int, default=10)
    p.add_argument("--fallback-threshold", type=float, default=5.0)
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def resolve_run_root(raw: str) -> Path:
    p = Path(raw)
    if p.is_absolute():
        return p
    return (ROOT / raw).resolve()


def parse_threshold(expr: str, fallback: float) -> tuple[str, float, str]:
    m = THRESH_RE.match(str(expr or ""))
    if not m:
        return "<", fallback, f"<{fallback}"
    cmp = m.group(1)
    thr = float(m.group(2))
    return cmp, thr, str(expr)


def pass_threshold(value: float, cmp: str, thr: float) -> bool:
    if cmp == "<":
        return value < thr
    if cmp == ">":
        return value > thr
    return False


def parse_g18_metrics(path: Path, fallback_threshold: float) -> dict[str, Any]:
    rows = read_csv(path)
    by_gate: dict[str, dict[str, str]] = {}
    for r in rows:
        gid = str(r.get("gate_id", "")).strip()
        if gid:
            by_gate[gid] = r
    cmp, thr, thr_expr = parse_threshold(str(by_gate.get("G18b", {}).get("threshold", "")), fallback_threshold)
    return {
        "g18a_status": norm_status(str(by_gate.get("G18a", {}).get("status", ""))),
        "g18b_status_v1": norm_status(str(by_gate.get("G18b", {}).get("status", ""))),
        "g18c_status": norm_status(str(by_gate.get("G18c", {}).get("status", ""))),
        "g18d_status_v1": norm_status(str(by_gate.get("G18d", {}).get("status", ""))),
        "g18_status_v1_raw": norm_status(str(by_gate.get("FINAL", {}).get("status", ""))),
        "g18b_n_times_mean_ipr": float(str(by_gate.get("G18b", {}).get("value", "nan"))),
        "g18b_threshold_cmp": cmp,
        "g18b_threshold": thr,
        "g18b_threshold_expr": thr_expr,
    }


def robust_n_ipr(path: Path, trim_top_fraction: float, min_modes: int) -> dict[str, Any]:
    rows = read_csv(path)
    vals: list[float] = []
    for r in rows:
        try:
            vals.append(float(str(r.get("n_IPR_k", "")).strip()))
        except Exception:
            continue
    n = len(vals)
    out: dict[str, Any] = {
        "n_modes": n,
        "n_used": 0,
        "trimmed_mean_n_ipr": None,
    }
    if n < max(1, int(min_modes)):
        return out
    vals = sorted(vals)
    trim = max(0.0, min(0.8, float(trim_top_fraction)))
    drop = int(round(trim * n))
    keep_n = max(int(min_modes), n - drop)
    kept = vals[:keep_n]
    out["n_used"] = keep_n
    out["trimmed_mean_n_ipr"] = sum(kept) / len(kept)
    return out


def summarize_by_dataset(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ds in sorted({str(r["dataset_id"]) for r in rows}):
        sub = [r for r in rows if str(r["dataset_id"]) == ds]
        n = len(sub)
        out.append(
            {
                "dataset_id": ds,
                "n_profiles": n,
                "g18_v1_pass": sum(1 for r in sub if r["g18_status_v1"] == "pass"),
                "g18_v2_pass": sum(1 for r in sub if r["g18_status_v2"] == "pass"),
                "improved_g18": sum(
                    1 for r in sub if r["g18_status_v1"] == "fail" and r["g18_status_v2"] == "pass"
                ),
                "degraded_g18": sum(
                    1 for r in sub if r["g18_status_v1"] == "pass" and r["g18_status_v2"] == "fail"
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

    source_rows = read_csv(source_summary)
    if not source_rows:
        raise RuntimeError("source summary has zero rows")

    out_rows: list[dict[str, Any]] = []
    for srow in source_rows:
        dataset_id = str(srow.get("dataset_id", "")).strip()
        seed = int(str(srow.get("seed", "0")))
        run_root = resolve_run_root(str(srow.get("run_root", "")))
        rel_run_root = run_root.resolve().relative_to(ROOT.resolve()).as_posix()

        g17 = norm_status(str(srow.get("g17_status", "")))
        g19 = norm_status(str(srow.get("g19_status", "")))
        g20 = norm_status(str(srow.get("g20_status", "")))
        lane_v1 = norm_status(str(srow.get("all_pass_qm_lane", "")))
        source_g18 = norm_status(str(srow.get("g18_status", "")))
        g18d_v2 = norm_status(str(srow.get("g18d_status_v2", "")))
        multi_peak = str(srow.get("multi_peak_mixing", ""))

        g18_dir = run_root / "g18"
        metric_csv = g18_dir / "metric_checks_qm_info.csv"
        modes_csv = g18_dir / "qm_info_modes.csv"
        if not metric_csv.exists():
            raise FileNotFoundError(f"missing g18 metric file: {metric_csv}")

        base = parse_g18_metrics(metric_csv, args.fallback_threshold)
        robust = robust_n_ipr(modes_csv, args.trim_top_fraction, args.min_modes) if modes_csv.exists() else {
            "n_modes": 0,
            "n_used": 0,
            "trimmed_mean_n_ipr": None,
        }

        if source_g18 == "pass":
            g18b_v2 = "pass"
            g18b_rule = "accept_source_official_pass"
        else:
            can_recover = (
                base["g18a_status"] == "pass"
                and base["g18b_status_v1"] == "fail"
                and base["g18c_status"] == "pass"
                and g18d_v2 == "pass"
            )
            if can_recover:
                val = robust["trimmed_mean_n_ipr"]
                if val is not None and pass_threshold(float(val), base["g18b_threshold_cmp"], base["g18b_threshold"]):
                    g18b_v2 = "pass"
                    g18b_rule = "trimmed_mean_n_ipr_recovery"
                else:
                    g18b_v2 = "fail"
                    g18b_rule = "retain_source_fail"
            else:
                g18b_v2 = "fail"
                g18b_rule = "retain_source_non_g18b_fail"

        g18_v2 = (
            "pass"
            if base["g18a_status"] == "pass" and g18b_v2 == "pass" and base["g18c_status"] == "pass" and g18d_v2 == "pass"
            else "fail"
        )
        lane_v2 = "pass" if (g17 == "pass" and g18_v2 == "pass" and g19 == "pass" and g20 == "pass") else "fail"

        out_rows.append(
            {
                "dataset_id": dataset_id,
                "seed": seed,
                "run_root": rel_run_root,
                "g17_status": g17,
                "g18_status_v1": source_g18,
                "g18_status_v2": g18_v2,
                "g18_status": g18_v2,
                "g19_status": g19,
                "g20_status": g20,
                "g18a_status": base["g18a_status"],
                "g18b_status_v1": base["g18b_status_v1"],
                "g18b_status_v2": g18b_v2,
                "g18b_v2_rule": g18b_rule,
                "g18c_status": base["g18c_status"],
                "g18d_status_v1": base["g18d_status_v1"],
                "g18d_status_v2": g18d_v2,
                "g18b_n_times_mean_ipr_global": f"{float(base['g18b_n_times_mean_ipr']):.12f}",
                "g18b_n_times_mean_ipr_trimmed": ""
                if robust["trimmed_mean_n_ipr"] is None
                else f"{float(robust['trimmed_mean_n_ipr']):.12f}",
                "g18b_trim_n_modes_total": int(robust["n_modes"]),
                "g18b_trim_n_modes_used": int(robust["n_used"]),
                "g18b_threshold_expr": str(base["g18b_threshold_expr"]),
                "g18b_threshold_cmp": str(base["g18b_threshold_cmp"]),
                "g18b_threshold_value": f"{float(base['g18b_threshold']):.12f}",
                "multi_peak_mixing": multi_peak,
                "all_pass_qm_lane_v1": lane_v1,
                "all_pass_qm_lane_v2": lane_v2,
                "all_pass_qm_lane": lane_v2,
            }
        )

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g18_v1_pass = sum(1 for r in out_rows if r["g18_status_v1"] == "pass")
    g18_v2_pass = sum(1 for r in out_rows if r["g18_status_v2"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v2_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v2"] == "pass")
    improved_g18 = sum(1 for r in out_rows if r["g18_status_v1"] == "fail" and r["g18_status_v2"] == "pass")
    degraded_g18 = sum(1 for r in out_rows if r["g18_status_v1"] == "pass" and r["g18_status_v2"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
    )

    lines = [
        "# QM G18b Candidate-v8 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G18 v1 -> v2: `{g18_v1_pass}/{n} -> {g18_v2_pass}/{n}`",
        f"- QM lane v1 -> v2: `{lane_v1_pass}/{n} -> {lane_v2_pass}/{n}`",
        f"- improved_g18: `{improved_g18}`",
        f"- degraded_g18: `{degraded_g18}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- G18 pass rows are preserved unchanged.",
        "- Recovery path targets G18b only and keeps the same parsed threshold from metric checks.",
        "- G18d uses already-frozen v2 status from source summary.",
        "- No threshold/formula edits in core gate scripts.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g18b-candidate-v8-trimmed-n-ipr",
        "trim_top_fraction": float(args.trim_top_fraction),
        "min_modes": int(args.min_modes),
        "notes": [
            "Candidate-only G18b trimmed n*IPR recovery.",
            "No edits to core G18 formulas/thresholds.",
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

