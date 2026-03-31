#!/usr/bin/env python3
"""
Analyze local seed-neighborhood behavior around remaining GR Stage-3 G11 fails.

Purpose:
- inspect +/- window seeds around each fail seed (same dataset)
- report whether fail is isolated or locally clustered
- summarize G11a/G11b status behavior near each fail

No thresholds/formulas are changed (diagnostic-only).
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "gr-stage3-official-v3-rerun-v1" / "summary.csv"
)
DEFAULT_OUT_DIR = (
    ROOT / "05_validation" / "evidence" / "artifacts" / "gr-stage3-g11-neighborhood-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze GR Stage-3 G11 fail neighborhood (v1).")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--window", type=int, default=5)
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


def norm_status(value: str) -> str:
    return "pass" if (value or "").strip().lower() == "pass" else "fail"


def pick(row: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in row and (row.get(k) or "").strip():
            return str(row.get(k, ""))
    return ""


def to_float(text: str) -> float | None:
    try:
        return float(text)
    except Exception:
        return None


def parse_threshold(text: str) -> tuple[str, float | None]:
    s = (text or "").strip()
    if not s:
        return "", None
    op = ""
    if s.startswith(">="):
        op = ">="
    elif s.startswith("<="):
        op = "<="
    elif s.startswith(">"):
        op = ">"
    elif s.startswith("<"):
        op = "<"
    token = ""
    for ch in s:
        if ch.isdigit() or ch in ".-+eE":
            token += ch
    try:
        return op, float(token) if token else None
    except Exception:
        return op, None


def margin(value: float | None, op: str, thr: float | None) -> float | None:
    if value is None or thr is None:
        return None
    if op in (">", ">="):
        return value - thr
    if op in ("<", "<="):
        return thr - value
    return None


def metric_map(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    for row in read_csv(path):
        gid = (row.get("gate_id") or "").strip()
        if gid:
            out[gid] = row
    return out


def f6(v: float | None) -> str:
    if v is None:
        return ""
    if math.isnan(v) or math.isinf(v):
        return ""
    return f"{v:.6f}"


def main() -> int:
    args = parse_args()
    summary_csv = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_csv.exists():
        raise FileNotFoundError(f"summary not found: {summary_csv}")

    rows = read_csv(summary_csv)
    if not rows:
        raise RuntimeError("summary has zero rows")

    normalized: list[dict[str, Any]] = []
    for r in rows:
        seed = int(str(r.get("seed", "0") or "0"))
        run_root = str(r.get("run_root", "")).strip()
        g11a_status = norm_status(pick(r, "g11a_v3_status", "g11a_status", "g11a_v2_status"))
        g11b_status = norm_status(pick(r, "g11b_status"))
        g11_status = norm_status(pick(r, "g11_status"))
        stage3_status = norm_status(pick(r, "stage3_status"))
        normalized.append(
            {
                "dataset_id": str(r.get("dataset_id", "")),
                "seed": seed,
                "run_root": run_root,
                "g11a_status": g11a_status,
                "g11b_status": g11b_status,
                "g11_status": g11_status,
                "stage3_status": stage3_status,
            }
        )

    fail_rows = [r for r in normalized if r["stage3_status"] == "fail" and r["g11_status"] == "fail"]
    if not fail_rows:
        raise RuntimeError("no stage3 g11 fail rows found")

    by_ds: dict[str, dict[int, dict[str, Any]]] = {}
    for r in normalized:
        ds = str(r["dataset_id"])
        by_ds.setdefault(ds, {})[int(r["seed"])] = r

    neighborhood_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for fr in sorted(fail_rows, key=lambda x: (x["dataset_id"], x["seed"])):
        ds = str(fr["dataset_id"])
        fs = int(fr["seed"])
        ds_map = by_ds.get(ds, {})
        seeds = sorted(s for s in ds_map.keys() if abs(s - fs) <= args.window)

        fail_count = 0
        g11a_fail_count = 0
        g11b_fail_count = 0

        for s in seeds:
            r = ds_map[s]
            rr = ROOT / str(r["run_root"])
            g11_metrics = metric_map(rr / "g11" / "metric_checks_einstein_eq.csv")

            g11a_val = to_float(g11_metrics.get("G11a", {}).get("value", ""))
            g11a_op, g11a_thr = parse_threshold(g11_metrics.get("G11a", {}).get("threshold", ""))
            g11a_margin = margin(g11a_val, g11a_op, g11a_thr)

            g11b_val = to_float(g11_metrics.get("G11b", {}).get("value", ""))
            g11b_op, g11b_thr = parse_threshold(g11_metrics.get("G11b", {}).get("threshold", ""))
            g11b_margin = margin(g11b_val, g11b_op, g11b_thr)

            stage3_fail = r["stage3_status"] == "fail"
            g11a_fail = r["g11a_status"] == "fail"
            g11b_fail = r["g11b_status"] == "fail"
            if stage3_fail:
                fail_count += 1
            if g11a_fail:
                g11a_fail_count += 1
            if g11b_fail:
                g11b_fail_count += 1

            neighborhood_rows.append(
                {
                    "dataset_id": ds,
                    "fail_seed_anchor": fs,
                    "neighbor_seed": s,
                    "delta_seed": abs(s - fs),
                    "stage3_status": r["stage3_status"],
                    "g11_status": r["g11_status"],
                    "g11a_status": r["g11a_status"],
                    "g11b_status": r["g11b_status"],
                    "is_anchor_fail_seed": "true" if s == fs else "false",
                    "g11a_value": f6(g11a_val),
                    "g11a_margin": f6(g11a_margin),
                    "g11b_value": f6(g11b_val),
                    "g11b_margin": f6(g11b_margin),
                    "run_root": r["run_root"],
                }
            )

        n = len(seeds)
        summary_rows.append(
            {
                "dataset_id": ds,
                "fail_seed_anchor": fs,
                "window": args.window,
                "neighbors_n": n,
                "stage3_fail_in_window": fail_count,
                "stage3_fail_rate": f"{(fail_count / n):.6f}" if n else "0.000000",
                "g11a_fail_in_window": g11a_fail_count,
                "g11b_fail_in_window": g11b_fail_count,
                "isolated_fail_flag": "true" if fail_count == 1 else "false",
            }
        )

    write_csv(
        out_dir / "fail_seed_neighborhood.csv",
        neighborhood_rows,
        list(neighborhood_rows[0].keys()),
    )
    write_csv(
        out_dir / "neighborhood_summary.csv",
        summary_rows,
        list(summary_rows[0].keys()),
    )

    lines: list[str] = []
    lines.append("# GR Stage-3 G11 Fail Neighborhood (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- source_summary: `{summary_csv.as_posix()}`")
    lines.append(f"- fail_seed_count: `{len(summary_rows)}`")
    lines.append(f"- neighborhood_window: `+/-{args.window}` seeds")
    lines.append("")
    lines.append("## Anchor Summary")
    lines.append("")
    for r in summary_rows:
        lines.append(
            f"- `{r['dataset_id']} seed {r['fail_seed_anchor']}`: "
            f"stage3_fail_in_window=`{r['stage3_fail_in_window']}/{r['neighbors_n']}`, "
            f"isolated=`{r['isolated_fail_flag']}`, "
            f"g11a_fail_in_window=`{r['g11a_fail_in_window']}`, "
            f"g11b_fail_in_window=`{r['g11b_fail_in_window']}`"
        )
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Diagnostic only, no formula/threshold edits.")
    lines.append("- Use this output to justify candidate-v5 prereg targeting.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"neighborhood_csv: {out_dir / 'fail_seed_neighborhood.csv'}")
    print(f"summary_csv:      {out_dir / 'neighborhood_summary.csv'}")
    print(f"report_md:        {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

