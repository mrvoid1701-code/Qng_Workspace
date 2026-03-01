#!/usr/bin/env python3
"""
Sensitivity sweep for G15b multi-peak proxy thresholds.

Purpose:
- Test robustness of the "multi-peakness -> v1 fragility" statement.
- Sweep threshold choices and report v1/v2 fail-rate lift.

Inputs:
- diagnosis CSV produced by run_qng_ppn_multipeak_diagnosis_v1.py

Default sweep:
- peak_2/peak_1 in {0.95, 0.97, 0.98, 0.99}
- distance_norm in {0.05, 0.10, 0.15}

Outputs:
- multipeak_sensitivity.csv
- multipeak_sensitivity_report.md
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIAG_CSV = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g15b-multipeak-diagnosis-v1"
    / "multipeak_diagnosis.csv"
)
DEFAULT_OUT_DIR = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "g15b-multipeak-diagnosis-v1"
)


def parse_grid(text: str) -> list[float]:
    out: list[float] = []
    for token in (x.strip() for x in text.split(",")):
        if token:
            out.append(float(token))
    return out


def parse_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fail_rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return 1.0 - (sum(int(r[key]) for r in rows) / len(rows))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No rows to write.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="G15b multi-peak sensitivity sweep.")
    parser.add_argument("--diagnosis-csv", default=str(DEFAULT_DIAG_CSV))
    parser.add_argument("--ratio-grid", default="0.95,0.97,0.98,0.99")
    parser.add_argument("--distance-grid", default="0.05,0.10,0.15")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args()


def summarize(
    rows: list[dict[str, Any]],
    ratio_thr: float,
    dist_thr: float,
    scope: str,
) -> dict[str, Any]:
    mp = [
        r
        for r in rows
        if float(r["peak_2_over_peak_1"]) >= ratio_thr
        and float(r["peak_1_2_distance_norm"]) >= dist_thr
    ]
    non = [r for r in rows if r not in mp]

    v1_fail_mp = fail_rate(mp, "g15b_v1_pass")
    v1_fail_non = fail_rate(non, "g15b_v1_pass")
    v2_fail_mp = fail_rate(mp, "g15b_v2_pass")
    v2_fail_non = fail_rate(non, "g15b_v2_pass")

    return {
        "scope": scope,
        "ratio_threshold": f"{ratio_thr:.2f}",
        "distance_threshold": f"{dist_thr:.2f}",
        "n_runs": len(rows),
        "n_multi_peak": len(mp),
        "n_non_multi_peak": len(non),
        "v1_fail_multi_peak": f"{v1_fail_mp:.6f}",
        "v1_fail_non_multi_peak": f"{v1_fail_non:.6f}",
        "v1_fail_lift_multi_minus_non": f"{(v1_fail_mp - v1_fail_non):.6f}",
        "v2_fail_multi_peak": f"{v2_fail_mp:.6f}",
        "v2_fail_non_multi_peak": f"{v2_fail_non:.6f}",
        "v2_fail_lift_multi_minus_non": f"{(v2_fail_mp - v2_fail_non):.6f}",
    }


def main() -> int:
    args = parse_args()
    in_csv = Path(args.diagnosis_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = parse_csv(in_csv)
    ratio_grid = parse_grid(args.ratio_grid)
    dist_grid = parse_grid(args.distance_grid)
    datasets = sorted({r["dataset_id"] for r in rows})

    out_rows: list[dict[str, Any]] = []
    for ratio_thr in ratio_grid:
        for dist_thr in dist_grid:
            out_rows.append(
                summarize(rows, ratio_thr, dist_thr, scope="ALL")
            )
            for ds in datasets:
                ds_rows = [r for r in rows if r["dataset_id"] == ds]
                out_rows.append(
                    summarize(ds_rows, ratio_thr, dist_thr, scope=ds)
                )

    out_csv = out_dir / "multipeak_sensitivity.csv"
    write_csv(out_csv, out_rows)

    all_rows = [r for r in out_rows if r["scope"] == "ALL"]
    positive_lift = sum(
        1 for r in all_rows if float(r["v1_fail_lift_multi_minus_non"]) > 0.0
    )
    zero_v2_fail = sum(
        1
        for r in all_rows
        if float(r["v2_fail_multi_peak"]) == 0.0
        and float(r["v2_fail_non_multi_peak"]) == 0.0
    )

    report = out_dir / "multipeak_sensitivity_report.md"
    lines = [
        "# G15b Multi-Peak Sensitivity Sweep",
        "",
        "## Sweep Grid",
        "",
        f"- ratio thresholds: `{', '.join(f'{x:.2f}' for x in ratio_grid)}`",
        f"- distance thresholds: `{', '.join(f'{x:.2f}' for x in dist_grid)}`",
        f"- combinations tested: `{len(ratio_grid) * len(dist_grid)}`",
        "",
        "## Robustness Summary (ALL datasets combined)",
        "",
        f"- Cases with positive v1 fail-rate lift (multi - non): "
        f"`{positive_lift}/{len(all_rows)}`",
        f"- Cases with zero v2 fail in both groups: "
        f"`{zero_v2_fail}/{len(all_rows)}`",
        "",
        "Interpretation:",
        "",
        "- If `v1_fail_lift_multi_minus_non` stays positive across the grid, the fragility trend is not tied to one arbitrary threshold pair.",
        "- If `v2` stays at zero fail in both groups, stability claim for `v2` is threshold-robust under this diagnostic family.",
        "",
        "## Artifacts",
        "",
        f"- `{out_csv}`",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote: {out_csv}")
    print(f"wrote: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
