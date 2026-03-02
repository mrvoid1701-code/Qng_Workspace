#!/usr/bin/env python3
"""
Evaluate G16b hybrid split candidate (v1):

- low-signal regime: use pre-registered G16b-v2 decision
- high-signal regime: keep legacy G16b-v1 decision

No formulas or thresholds are changed. This is a post-processing evaluation
over frozen summary outputs from run_g16b_v2_candidate_eval_v1.py.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_SOURCE_SANITY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-v2-candidate-sanity-v1"
    / "summary.csv"
)
DEFAULT_SOURCE_PREREG = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-v2-candidate-prereg-v1"
    / "summary.csv"
)
DEFAULT_OUT_SANITY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-split-hybrid-sanity-v1"
)
DEFAULT_OUT_PREREG = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g16b-split-hybrid-prereg-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate G16b hybrid split candidate (v1).")
    p.add_argument("--mode", choices=["sanity", "prereg"], default="prereg")
    p.add_argument("--source-summary-csv", default="")
    p.add_argument("--out-dir", default="")
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


def normalize_status(value: str) -> str:
    v = (value or "").strip().lower()
    return "pass" if v == "pass" else "fail"


def choose_source(args: argparse.Namespace) -> Path:
    if args.source_summary_csv.strip():
        return Path(args.source_summary_csv).resolve()
    return (DEFAULT_SOURCE_SANITY if args.mode == "sanity" else DEFAULT_SOURCE_PREREG).resolve()


def choose_out_dir(args: argparse.Namespace) -> Path:
    if args.out_dir.strip():
        return Path(args.out_dir).resolve()
    return (DEFAULT_OUT_SANITY if args.mode == "sanity" else DEFAULT_OUT_PREREG).resolve()


def build_rows(src_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in src_rows:
        v1 = normalize_status(row.get("g16b_v1_status", ""))
        v2 = normalize_status(row.get("g16b_v2_status", ""))
        low = (row.get("is_low_signal", "").strip().lower() == "true")

        hybrid = v2 if low else v1

        g16a = normalize_status(row.get("g16a_status", ""))
        g16c = normalize_status(row.get("g16c_status", ""))
        g16d = normalize_status(row.get("g16d_status", ""))
        g16_v1 = "pass" if all(x == "pass" for x in [g16a, v1, g16c, g16d]) else "fail"
        g16_v2 = "pass" if all(x == "pass" for x in [g16a, v2, g16c, g16d]) else "fail"
        g16_hybrid = "pass" if all(x == "pass" for x in [g16a, hybrid, g16c, g16d]) else "fail"

        out.append(
            {
                "dataset_id": row.get("dataset_id", ""),
                "seed": row.get("seed", ""),
                "phi_scale": row.get("phi_scale", ""),
                "is_low_signal": "true" if low else "false",
                "signal_regime": "low" if low else "high",
                "g16a_status": g16a,
                "g16b_v1_status": v1,
                "g16b_v2_status": v2,
                "g16b_hybrid_status": hybrid,
                "g16c_status": g16c,
                "g16d_status": g16d,
                "g16_v1_status": g16_v1,
                "g16_v2_status": g16_v2,
                "g16_hybrid_status": g16_hybrid,
                "g16b_v2_branch": row.get("g16b_v2_branch", ""),
                "t11_std_to_abs_mean": row.get("t11_std_to_abs_mean", ""),
                "r2_full_recomputed": row.get("r2_full_recomputed", ""),
                "r2_high_signal": row.get("r2_high_signal", ""),
                "abs_pearson_high_signal": row.get("abs_pearson_high_signal", ""),
                "abs_spearman_high_signal": row.get("abs_spearman_high_signal", ""),
            }
        )
    return out


def count_fail(rows: list[dict[str, Any]], key: str) -> int:
    return sum(1 for r in rows if r[key] != "pass")


def write_report(path: Path, rows: list[dict[str, Any]], mode: str) -> None:
    total = len(rows)
    v1_fail = count_fail(rows, "g16b_v1_status")
    v2_fail = count_fail(rows, "g16b_v2_status")
    hybrid_fail = count_fail(rows, "g16b_hybrid_status")

    improved = sum(1 for r in rows if r["g16b_v1_status"] == "fail" and r["g16b_hybrid_status"] == "pass")
    degraded = sum(1 for r in rows if r["g16b_v1_status"] == "pass" and r["g16b_hybrid_status"] == "fail")

    low_rows = [r for r in rows if r["signal_regime"] == "low"]
    high_rows = [r for r in rows if r["signal_regime"] == "high"]
    low_v1_fail = count_fail(low_rows, "g16b_v1_status")
    low_hybrid_fail = count_fail(low_rows, "g16b_hybrid_status")
    high_v1_fail = count_fail(high_rows, "g16b_v1_status")
    high_hybrid_fail = count_fail(high_rows, "g16b_hybrid_status")

    lines: list[str] = []
    lines.append("# G16b Hybrid Split Candidate (v1)")
    lines.append("")
    lines.append(f"- mode: `{mode}`")
    lines.append(f"- generated_utc: `{datetime.utcnow().isoformat()}Z`")
    lines.append(f"- profiles: `{total}`")
    lines.append(f"- g16b_v1_pass: `{total - v1_fail}`")
    lines.append(f"- g16b_v2_pass: `{total - v2_fail}`")
    lines.append(f"- g16b_hybrid_pass: `{total - hybrid_fail}`")
    lines.append(f"- improved_vs_v1: `{improved}`")
    lines.append(f"- degraded_vs_v1: `{degraded}`")
    lines.append("")

    if mode == "prereg":
        low_improve = low_hybrid_fail < low_v1_fail
        high_non_degrade = high_hybrid_fail <= high_v1_fail
        overall_non_degrade = hybrid_fail <= v1_fail
        verdict = "candidate acceptable for next promotion grid" if (low_improve and high_non_degrade and overall_non_degrade) else "candidate NOT acceptable yet"

        lines.append("## Pre-Registered Checks")
        lines.append("")
        lines.append("- criteria:")
        lines.append("  - low-signal fail count improves vs v1")
        lines.append("  - high-signal fail count does not degrade vs v1")
        lines.append("  - overall fail count does not degrade vs v1")
        lines.append(f"- low-signal: v1_fail={low_v1_fail}, hybrid_fail={low_hybrid_fail}, pass={str(low_improve).lower()}")
        lines.append(f"- high-signal: v1_fail={high_v1_fail}, hybrid_fail={high_hybrid_fail}, pass={str(high_non_degrade).lower()}")
        lines.append(f"- overall: v1_fail={v1_fail}, hybrid_fail={hybrid_fail}, pass={str(overall_non_degrade).lower()}")
        lines.append(f"- verdict: `{verdict}`")
        lines.append("")

    lines.append("## Dataset Summary")
    lines.append("")
    lines.append("| dataset | n | v1_fail | v2_fail | hybrid_fail |")
    lines.append("| --- | --- | --- | --- | --- |")
    for ds in sorted({r["dataset_id"] for r in rows}):
        sub = [r for r in rows if r["dataset_id"] == ds]
        lines.append(
            f"| {ds} | {len(sub)} | "
            f"{count_fail(sub, 'g16b_v1_status')} | "
            f"{count_fail(sub, 'g16b_v2_status')} | "
            f"{count_fail(sub, 'g16b_hybrid_status')} |"
        )
    lines.append("")

    lines.append("## Regime Summary")
    lines.append("")
    lines.append("| regime | n | v1_fail | v2_fail | hybrid_fail |")
    lines.append("| --- | --- | --- | --- | --- |")
    for reg in ["low", "high"]:
        sub = [r for r in rows if r["signal_regime"] == reg]
        lines.append(
            f"| {reg} | {len(sub)} | "
            f"{count_fail(sub, 'g16b_v1_status')} | "
            f"{count_fail(sub, 'g16b_v2_status')} | "
            f"{count_fail(sub, 'g16b_hybrid_status')} |"
        )
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    source_csv = choose_source(args)
    if not source_csv.exists():
        raise FileNotFoundError(f"source summary not found: {source_csv}")
    out_dir = choose_out_dir(args)
    out_dir.mkdir(parents=True, exist_ok=True)

    src_rows = read_csv(source_csv)
    rows = build_rows(src_rows)
    if not rows:
        raise RuntimeError("source summary had zero rows")

    summary_csv = out_dir / "summary.csv"
    write_csv(summary_csv, rows, list(rows[0].keys()))
    report_md = out_dir / "report.md"
    write_report(report_md, rows, args.mode)

    manifest = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "mode": args.mode,
        "source_summary_csv": source_csv.as_posix(),
        "policy": {
            "low_signal_rule": "is_low_signal == true (from prereg G16b-v2 evaluator; std(T11)/|mean(T11)| > 10)",
            "low_signal_gate": "use g16b_v2_status",
            "high_signal_gate": "use g16b_v1_status",
        },
        "notes": [
            "No new thresholds or formulas introduced.",
            "Hybrid policy is now the official G16b decision gate; script retained for reproducible evaluation outputs.",
        ],
    }
    manifest_path = out_dir / "prereg_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"summary_csv: {summary_csv}")
    print(f"report_md:   {report_md}")
    print(f"manifest:    {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
