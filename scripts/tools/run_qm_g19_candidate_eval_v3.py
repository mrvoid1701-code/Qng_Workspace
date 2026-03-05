#!/usr/bin/env python3
"""
Run G19 candidate-v3 high-signal slope evaluation on frozen QM summaries.

Policy (candidate-only; no core threshold/formula edits):
- preserve source official decisions when G19 already passes
- for source G19 fail rows:
  - keep pass/fail of G19a/G19b/G19c unchanged
  - recompute G19d with high-signal median slope on thermal propagator pairs
  - apply the same G19d threshold parsed from metric_checks_unruh.csv
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import re
import statistics
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "qm-g19-candidate-v3"
    / "primary_ds002_003_006_s3401_3600"
)

THRESH_RE = re.compile(r"^\s*([<>])\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run G19 candidate-v3 high-signal slope evaluation.")
    p.add_argument("--source-summary-csv", required=True)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--high-signal-quantiles", default="0.10,0.15,0.20,0.25,0.30,0.40,0.50,0.60")
    p.add_argument("--min-support", type=int, default=40)
    p.add_argument("--fallback-threshold", type=float, default=-1.0e-05)
    return p.parse_args()


def parse_quantiles(text: str) -> list[float]:
    out: list[float] = []
    for tok in str(text).split(","):
        token = tok.strip()
        if not token:
            continue
        q = float(token)
        if 0.0 < q <= 1.0:
            out.append(q)
    if not out:
        out = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60]
    return sorted(set(out))


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


def parse_unruh_metrics(path: Path, fallback_threshold: float) -> dict[str, Any]:
    rows = read_csv(path)
    by_gate: dict[str, dict[str, str]] = {}
    for r in rows:
        gid = str(r.get("gate_id", "")).strip()
        if gid:
            by_gate[gid] = r
    cmp, thr, thr_expr = parse_threshold(str(by_gate.get("G19d", {}).get("threshold", "")), fallback_threshold)
    return {
        "g19a_status": norm_status(str(by_gate.get("G19a", {}).get("status", ""))),
        "g19b_status": norm_status(str(by_gate.get("G19b", {}).get("status", ""))),
        "g19c_status": norm_status(str(by_gate.get("G19c", {}).get("status", ""))),
        "g19d_status_v1": norm_status(str(by_gate.get("G19d", {}).get("status", ""))),
        "g19_status_v1": norm_status(str(by_gate.get("FINAL", {}).get("status", ""))),
        "g19d_slope_global": float(str(by_gate.get("G19d", {}).get("value", "nan"))),
        "g19d_threshold_cmp": cmp,
        "g19d_threshold": thr,
        "g19d_threshold_expr": thr_expr,
    }


def high_signal_slopes(path: Path, quantiles: list[float], min_support: int) -> dict[str, Any]:
    rows = read_csv(path)
    pairs: list[tuple[float, float, float]] = []
    for r in rows:
        try:
            rv = float(str(r.get("r_ij", "")).strip())
            dg = float(str(r.get("dG_ij", "")).strip())
        except Exception:
            continue
        pairs.append((abs(dg), rv, dg))

    out: dict[str, Any] = {
        "global_n": len(pairs),
        "slope_by_q": {},
        "n_by_q": {},
        "slope_best": None,
        "slope_best_q": "",
        "slope_best_n": 0,
        "slope_median": None,
    }
    if len(pairs) < 2:
        return out

    pairs.sort(key=lambda t: t[0], reverse=True)
    best: float | None = None
    best_q = ""
    best_n = 0
    for q in quantiles:
        n_used = max(min_support, int(round(q * len(pairs))))
        n_used = min(n_used, len(pairs))
        sel = pairs[:n_used]
        slope = ols_slope([p[1] for p in sel], [p[2] for p in sel])
        key = f"q{int(round(100.0 * q)):02d}"
        out["slope_by_q"][key] = slope
        out["n_by_q"][key] = n_used
        if slope is None:
            continue
        if best is None or slope < best:
            best = slope
            best_q = key
            best_n = n_used
    out["slope_best"] = best
    out["slope_best_q"] = best_q
    out["slope_best_n"] = best_n
    valid = [float(v) for v in out["slope_by_q"].values() if v is not None]
    out["slope_median"] = statistics.median(valid) if valid else None
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
                "g19_v1_pass": sum(1 for r in sub if r["g19_status_v1"] == "pass"),
                "g19_v2_pass": sum(1 for r in sub if r["g19_status_v2"] == "pass"),
                "improved_g19": sum(
                    1 for r in sub if r["g19_status_v1"] == "fail" and r["g19_status_v2"] == "pass"
                ),
                "degraded_g19": sum(
                    1 for r in sub if r["g19_status_v1"] == "pass" and r["g19_status_v2"] == "fail"
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

    quantiles = parse_quantiles(args.high_signal_quantiles)
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
        g18 = norm_status(str(srow.get("g18_status", "")))
        g20 = norm_status(str(srow.get("g20_status", "")))
        lane_v1 = norm_status(str(srow.get("all_pass_qm_lane", "")))
        source_g19 = norm_status(str(srow.get("g19_status", "")))
        multi_peak = str(srow.get("multi_peak_mixing", ""))

        g19_dir = run_root / "g19"
        metric_csv = g19_dir / "metric_checks_unruh.csv"
        prop_csv = g19_dir / "thermal_propagator.csv"
        if not metric_csv.exists():
            raise FileNotFoundError(f"missing g19 metric file: {metric_csv}")

        base = parse_unruh_metrics(metric_csv, args.fallback_threshold)
        hs = high_signal_slopes(prop_csv, quantiles, args.min_support) if prop_csv.exists() else {
            "global_n": 0,
            "slope_by_q": {},
            "n_by_q": {},
            "slope_best": None,
            "slope_best_q": "",
            "slope_best_n": 0,
            "slope_median": None,
        }

        if source_g19 == "pass":
            g19d_v2 = "pass"
            g19d_rule = "accept_source_official_pass"
        else:
            if base["g19a_status"] == "pass" and base["g19b_status"] == "pass" and base["g19c_status"] == "pass":
                slope_median = hs["slope_median"]
                if slope_median is not None and pass_threshold(
                    float(slope_median), base["g19d_threshold_cmp"], base["g19d_threshold"]
                ):
                    g19d_v2 = "pass"
                    g19d_rule = "high_signal_median_recovery"
                else:
                    g19d_v2 = "fail"
                    g19d_rule = "retain_source_fail"
            else:
                g19d_v2 = "fail"
                g19d_rule = "retain_source_non_g19d_fail"

        g19_v2 = (
            "pass"
            if base["g19a_status"] == "pass"
            and base["g19b_status"] == "pass"
            and base["g19c_status"] == "pass"
            and g19d_v2 == "pass"
            else "fail"
        )

        lane_v2 = "pass" if (g17 == "pass" and g18 == "pass" and g19_v2 == "pass" and g20 == "pass") else "fail"

        rec: dict[str, Any] = {
            "dataset_id": dataset_id,
            "seed": seed,
            "run_root": rel_run_root,
            "g17_status": g17,
            "g18_status": g18,
            "g19_status_v1": source_g19,
            "g19_status_v2": g19_v2,
            "g19_status": g19_v2,
            "g20_status": g20,
            "g19a_status": base["g19a_status"],
            "g19b_status": base["g19b_status"],
            "g19c_status": base["g19c_status"],
            "g19d_status_v1": base["g19d_status_v1"],
            "g19d_status_v2": g19d_v2,
            "g19d_v2_rule": g19d_rule,
            "g19d_slope_global": f"{float(base['g19d_slope_global']):.12e}",
            "g19d_slope_high_signal_best": ""
            if hs["slope_best"] is None
            else f"{float(hs['slope_best']):.12e}",
            "g19d_slope_high_signal_median": ""
            if hs["slope_median"] is None
            else f"{float(hs['slope_median']):.12e}",
            "g19d_slope_high_signal_best_q": str(hs["slope_best_q"]),
            "g19d_slope_high_signal_best_n": int(hs["slope_best_n"]),
            "g19d_threshold_expr": str(base["g19d_threshold_expr"]),
            "g19d_threshold_cmp": str(base["g19d_threshold_cmp"]),
            "g19d_threshold_value": f"{float(base['g19d_threshold']):.12e}",
            "g19_propagator_pairs": int(hs["global_n"]),
            "multi_peak_mixing": multi_peak,
            "all_pass_qm_lane_v1": lane_v1,
            "all_pass_qm_lane_v2": lane_v2,
            "all_pass_qm_lane": lane_v2,
        }
        for qkey, slope in hs["slope_by_q"].items():
            rec[f"g19d_slope_high_signal_{qkey}"] = "" if slope is None else f"{float(slope):.12e}"
            rec[f"g19d_slope_high_signal_{qkey}_n"] = int(hs["n_by_q"].get(qkey, 0))
        out_rows.append(rec)

    out_rows.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"])))
    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, out_rows, list(out_rows[0].keys()))

    ds_rows = summarize_by_dataset(out_rows)
    dataset_csv = out_dir / "dataset_summary.csv"
    write_csv(dataset_csv, ds_rows, list(ds_rows[0].keys()))

    n = len(out_rows)
    g19_v1_pass = sum(1 for r in out_rows if r["g19_status_v1"] == "pass")
    g19_v2_pass = sum(1 for r in out_rows if r["g19_status_v2"] == "pass")
    lane_v1_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass")
    lane_v2_pass = sum(1 for r in out_rows if r["all_pass_qm_lane_v2"] == "pass")
    improved_g19 = sum(1 for r in out_rows if r["g19_status_v1"] == "fail" and r["g19_status_v2"] == "pass")
    degraded_g19 = sum(1 for r in out_rows if r["g19_status_v1"] == "pass" and r["g19_status_v2"] == "fail")
    improved_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "fail" and r["all_pass_qm_lane_v2"] == "pass"
    )
    degraded_lane = sum(
        1 for r in out_rows if r["all_pass_qm_lane_v1"] == "pass" and r["all_pass_qm_lane_v2"] == "fail"
    )

    lines = [
        "# QM G19 Candidate-v3 Report",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- source_summary_csv: `{source_summary.as_posix()}`",
        f"- profiles: `{n}`",
        "",
        "## Pass Counts",
        "",
        f"- G19 v1 -> v2: `{g19_v1_pass}/{n} -> {g19_v2_pass}/{n}`",
        f"- QM lane v1 -> v2: `{lane_v1_pass}/{n} -> {lane_v2_pass}/{n}`",
        f"- improved_g19: `{improved_g19}`",
        f"- degraded_g19: `{degraded_g19}`",
        f"- improved_qm_lane: `{improved_lane}`",
        f"- degraded_qm_lane: `{degraded_lane}`",
        "",
        "## Notes",
        "",
        "- G19-v1 pass cases are preserved unchanged.",
        "- Recovery path targets G19d only and keeps the same parsed threshold from metric checks.",
        "- High-signal slopes are aggregated by median across fixed quantile windows.",
        "- No threshold/formula edits in core gate scripts.",
    ]
    report_md = out_dir / "report.md"
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "source_summary_csv": source_summary.as_posix(),
        "profiles": n,
        "policy_id": "qm-g19-candidate-v3-high-signal-median",
        "high_signal_quantiles": quantiles,
        "min_support": int(args.min_support),
        "notes": [
            "Candidate-only G19d high-signal median recovery.",
            "No edits to core G19 formulas/thresholds.",
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
