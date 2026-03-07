#!/usr/bin/env python3
"""Select one v7 config from exploratory summary and write strict prereg lock files."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_AGG = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-v7-exp-v1"
    / "aggregate_lambda_summary.csv"
)
DEFAULT_OUT_DIR = ROOT / "05_validation" / "evidence" / "artifacts" / "d4-stage2-v7-exp-v1"
DEFAULT_PREREG = ROOT / "05_validation" / "pre-registrations" / "d4-stage2-dual-kernel-v7-strict.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Select v7 strict config from exploratory aggregate summary.")
    p.add_argument("--aggregate-csv", default=str(DEFAULT_AGG))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--selected-json-name", default="selected_config.json")
    p.add_argument("--prereg-md", default=str(DEFAULT_PREREG))
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--dataset-csv-rel", default="data/rotation/rotation_ds006_rotmod.csv")
    p.add_argument("--split-seeds", default="3401,3402,3403,3404,3405")
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--s1-lambda", type=float, default=0.28)
    p.add_argument("--s2-const", type=float, default=0.355)
    p.add_argument("--r0-kpc", type=float, default=1.0)
    p.add_argument("--r-tail-kpc", type=float, default=4.0)
    p.add_argument("--focus-gamma", type=float, default=2.0)
    p.add_argument("--tau-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--alpha-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3")
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    agg_path = Path(args.aggregate_csv).resolve()
    if not agg_path.exists():
        raise FileNotFoundError(f"aggregate csv not found: {agg_path}")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv(agg_path)
    if not rows:
        raise RuntimeError("no rows in aggregate summary")

    # Selection criterion:
    # 1) smallest avg_holdout_mond_worse_pct
    # 2) then smaller avg_boundary_hit_rate
    # 3) then smaller avg_single_component_only_rate
    # 4) then smaller avg_holdout_chi2_per_n_dual
    def key_fn(r: dict[str, str]) -> tuple[float, float, float, float]:
        return (
            float(r["avg_holdout_mond_worse_pct"]),
            float(r["avg_boundary_hit_rate"]),
            float(r["avg_single_component_only_rate"]),
            float(r["avg_holdout_chi2_per_n_dual"]),
        )

    best = min(rows, key=key_fn)
    selected = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "selection_source_csv": agg_path.as_posix(),
        "criterion": [
            "min avg_holdout_mond_worse_pct",
            "min avg_boundary_hit_rate",
            "min avg_single_component_only_rate",
            "min avg_holdout_chi2_per_n_dual",
        ],
        "selected_lambda_s": float(best["lambda_s"]),
        "selected_lambda_e": float(best["lambda_e"]),
        "selected_row": best,
    }
    selected_path = out_dir / str(args.selected_json_name)
    selected_path.write_text(json.dumps(selected, indent=2), encoding="utf-8")

    # Write strict prereg with locked selected lambdas.
    prereg_path = Path(args.prereg_md).resolve()
    prereg_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Pre-Registration - D4 Stage-2 v7 Strict",
        "",
        f"- Date: {datetime.now(timezone.utc).date().isoformat()}",
        "- Test ID: `d4-stage2-dual-kernel-v7-strict`",
        "- Purpose: strict evaluation of one fixed v7 setup chosen from v7-exp",
        "- Policy: anti post-hoc (`prereg -> run -> evaluate`)",
        "",
        "## Fixed Selection Input",
        "",
        f"- source aggregate csv: `{agg_path.as_posix()}`",
        f"- selected lambda_s: `{best['lambda_s']}`",
        f"- selected lambda_e: `{best['lambda_e']}`",
        "",
        "## Locked Data / Splits / Constants",
        "",
        f"- dataset_id: `{args.dataset_id}`",
        f"- dataset_csv: `{args.dataset_csv_rel}`",
        f"- split_seeds: `{args.split_seeds}`",
        f"- train_frac: `{args.train_frac}`",
        f"- s1_lambda: `{args.s1_lambda}`",
        f"- s2_const: `{args.s2_const}`",
        f"- r0_kpc: `{args.r0_kpc}`",
        f"- r_tail_kpc: `{args.r_tail_kpc}`",
        f"- focus_gamma: `{args.focus_gamma}`",
        "",
        "## Locked Grids",
        "",
        f"- tau_grid: `{args.tau_grid}`",
        f"- alpha_grid: `{args.alpha_grid}`",
        "",
        "## Locked Formula",
        "",
        "```text",
        "v_pred^2 = bt + k1*H1 + k2*Outer",
        "Outer = H2*(r/(r+r_tail))/sqrt(1 + g_bar/a0), g_bar=bt/r, k1,k2>=0",
        "selection objective = argmin_{tau,alpha} [chi2_focus + lambda_s*R_smooth + lambda_e*R_edge]",
        "```",
        "",
        "## Strict Criteria",
        "",
        "- same evaluator thresholds as current strict MOND lane (unchanged)",
        "",
        "## Lock Rule",
        "",
        "No edits after seeing strict results to:",
        "1. selected lambdas",
        "2. dataset/splits/constants",
        "3. tau/alpha grids",
        "4. evaluator thresholds",
    ]
    prereg_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report_lines = [
        "# D4 v7 Selection Report",
        "",
        f"- generated_utc: `{selected['generated_utc']}`",
        f"- selected lambda_s: `{best['lambda_s']}`",
        f"- selected lambda_e: `{best['lambda_e']}`",
        f"- selected by criteria: `{', '.join(selected['criterion'])}`",
        "",
        "## Selected Row",
        "",
    ]
    for k in sorted(best.keys()):
        report_lines.append(f"- `{k}`: `{best[k]}`")
    (out_dir / "selection_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"selected_json: {selected_path.as_posix()}")
    print(f"prereg_md: {prereg_path.as_posix()}")
    print(f"selection_report_md: {(out_dir / 'selection_report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

