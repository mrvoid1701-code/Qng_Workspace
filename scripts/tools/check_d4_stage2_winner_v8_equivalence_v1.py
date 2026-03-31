#!/usr/bin/env python3
"""A/B equivalence check for D4 winner v8 vs direct D9 WINNER_V1 (M8c)."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import train_holdout_split
from scripts.run_d9_cross_validation_v1 import chi2_pts, fit_m8c, flatten, load_galaxies, v_m8c


DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_PER_SEED = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v8-strict"
    / "per_seed_candidate_summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v8-strict"
    / "equivalence-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check D4 winner v8 A/B equivalence to D9 WINNER_V1 implementation.")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--per-seed-csv", default=str(DEFAULT_PER_SEED))
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--candidate", default="winner_v1_m8c")
    p.add_argument("--tol", type=float, default=1e-9)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def f9(x: float) -> str:
    return f"{x:.9f}"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset_csv).resolve()
    per_seed_path = Path(args.per_seed_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_path.exists():
        raise FileNotFoundError(f"dataset csv not found: {dataset_path}")
    if not per_seed_path.exists():
        raise FileNotFoundError(f"per-seed csv not found: {per_seed_path}")

    rows = [r for r in read_rows(per_seed_path) if str(r.get("candidate", "")) == str(args.candidate)]
    if not rows:
        raise RuntimeError(f"no rows for candidate={args.candidate} in {per_seed_path}")

    galaxies = load_galaxies(dataset_path)
    galaxy_ids = sorted(galaxies.keys())
    out_rows: list[dict[str, str]] = []

    max_abs_delta_train = 0.0
    max_abs_delta_holdout = 0.0
    max_abs_delta_k = 0.0
    max_abs_delta_g = 0.0

    for r in rows:
        seed = int(r["split_seed"])
        train_ids, holdout_ids = train_holdout_split(galaxy_ids, seed, float(args.train_frac))
        train_points = flatten(galaxies, sorted(train_ids))
        holdout_points = flatten(galaxies, sorted(holdout_ids))
        n_train = max(1, len(train_points))
        n_holdout = max(1, len(holdout_points))

        k_csv = float(r["best_k1"])
        gd_csv = float(r["best_k2"])
        train_csv = float(r["train_chi2_per_n_dual"])
        holdout_csv = float(r["holdout_chi2_per_n_dual"])

        train_recalc = chi2_pts(train_points, lambda p: v_m8c(p, k_csv, gd_csv)) / n_train
        holdout_recalc = chi2_pts(holdout_points, lambda p: v_m8c(p, k_csv, gd_csv)) / n_holdout

        k_ref, gd_ref, train_ref = fit_m8c(train_points)
        holdout_ref = chi2_pts(holdout_points, lambda p: v_m8c(p, k_ref, gd_ref)) / n_holdout

        delta_train = abs(train_recalc - train_csv)
        delta_holdout = abs(holdout_recalc - holdout_csv)
        delta_k = abs(k_ref - k_csv)
        delta_g = abs(gd_ref - gd_csv)
        delta_holdout_ref = abs(holdout_ref - holdout_csv)

        max_abs_delta_train = max(max_abs_delta_train, delta_train)
        max_abs_delta_holdout = max(max_abs_delta_holdout, delta_holdout)
        max_abs_delta_k = max(max_abs_delta_k, delta_k)
        max_abs_delta_g = max(max_abs_delta_g, delta_g)

        out_rows.append(
            {
                "split_seed": str(seed),
                "k_csv": f9(k_csv),
                "k_refit_d9": f9(k_ref),
                "abs_delta_k": f9(delta_k),
                "gdag_csv": f9(gd_csv),
                "gdag_refit_d9": f9(gd_ref),
                "abs_delta_gdag": f9(delta_g),
                "train_chi2_per_n_csv": f9(train_csv),
                "train_chi2_per_n_recalc": f9(train_recalc),
                "abs_delta_train_chi2_per_n": f9(delta_train),
                "holdout_chi2_per_n_csv": f9(holdout_csv),
                "holdout_chi2_per_n_recalc": f9(holdout_recalc),
                "holdout_chi2_per_n_refit_d9": f9(holdout_ref),
                "abs_delta_holdout_chi2_per_n": f9(delta_holdout),
                "abs_delta_holdout_vs_refit_d9": f9(delta_holdout_ref),
                "ab_pass": str(
                    delta_train <= float(args.tol)
                    and delta_holdout <= float(args.tol)
                    and delta_k <= float(args.tol)
                    and delta_g <= float(args.tol)
                ).lower(),
            }
        )

    fields = list(out_rows[0].keys()) if out_rows else []
    write_csv(out_dir / "equivalence_rows.csv", out_rows, fields)

    pass_all = (
        max_abs_delta_train <= float(args.tol)
        and max_abs_delta_holdout <= float(args.tol)
        and max_abs_delta_k <= float(args.tol)
        and max_abs_delta_g <= float(args.tol)
    )
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_csv": dataset_path.as_posix(),
        "per_seed_csv": per_seed_path.as_posix(),
        "candidate": str(args.candidate),
        "tol": float(args.tol),
        "max_abs_delta_train_chi2_per_n": max_abs_delta_train,
        "max_abs_delta_holdout_chi2_per_n": max_abs_delta_holdout,
        "max_abs_delta_k": max_abs_delta_k,
        "max_abs_delta_gdag": max_abs_delta_g,
        "equivalence_pass": pass_all,
    }
    (out_dir / "equivalence_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "# D4 Winner V8 Equivalence Report",
        "",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- candidate: `{summary['candidate']}`",
        f"- tolerance: `{summary['tol']}`",
        f"- max_abs_delta_train_chi2_per_n: `{f9(summary['max_abs_delta_train_chi2_per_n'])}`",
        f"- max_abs_delta_holdout_chi2_per_n: `{f9(summary['max_abs_delta_holdout_chi2_per_n'])}`",
        f"- max_abs_delta_k: `{f9(summary['max_abs_delta_k'])}`",
        f"- max_abs_delta_gdag: `{f9(summary['max_abs_delta_gdag'])}`",
        f"- equivalence_pass: `{summary['equivalence_pass']}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"equivalence_csv: {(out_dir / 'equivalence_rows.csv').as_posix()}")
    print(f"equivalence_summary_json: {(out_dir / 'equivalence_summary.json').as_posix()}")
    print(f"equivalence_pass: {pass_all}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
