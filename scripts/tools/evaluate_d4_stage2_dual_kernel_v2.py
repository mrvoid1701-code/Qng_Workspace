#!/usr/bin/env python3
"""
Evaluate D4 Stage-2 dual-kernel run against strict prereg criteria (v2).

This is tooling-only governance hardening. No model formulas are changed.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v2-strict-vs-mond"
    / "d4_stage2_dual_kernel_summary.json"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v2-strict-vs-mond"
    / "evaluation-v2"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate D4 Stage-2 strict vs MOND criteria (v2).")
    p.add_argument("--summary-json", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    # Locked prereg metadata (governance lock checks).
    p.add_argument("--expected-test-id", default="d4-stage2-dual-kernel-v2-strict-vs-mond")
    p.add_argument("--expected-dataset-id", default="DS-006")
    p.add_argument("--expected-dataset-csv-name", default="rotation_ds006_rotmod.csv")
    p.add_argument("--expected-split-seed", type=int, default=3401)
    p.add_argument("--expected-train-frac", type=float, default=0.70)
    p.add_argument("--expected-s1-lambda", type=float, default=0.28)
    p.add_argument("--expected-s2-const", type=float, default=0.355)
    p.add_argument("--expected-r0-kpc", type=float, default=1.0)
    p.add_argument("--expected-tau-grid", default="0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--expected-alpha-grid", default="0.3,0.5,0.7,1.0,1.3")
    p.add_argument("--min-holdout-improve-vs-null-pct", type=float, default=10.0)
    p.add_argument("--max-holdout-mond-worse-pct", type=float, default=0.0)
    p.add_argument("--max-train-mond-worse-pct", type=float, default=5.0)
    p.add_argument("--max-generalization-gap-pp", type=float, default=20.0)
    p.add_argument("--max-holdout-delta-aic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--max-holdout-delta-bic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def get_metric(d: dict[str, Any], *keys: str) -> float:
    cur: Any = d
    for k in keys:
        cur = cur[k]
    return float(cur)


def parse_float_grid(raw: str) -> list[float]:
    out: list[float] = []
    for tok in str(raw).split(","):
        t = tok.strip()
        if not t:
            continue
        out.append(float(t))
    return out


def list_almost_equal(a: list[float], b: list[float], tol: float = 1e-12) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if abs(float(x) - float(y)) > tol:
            return False
    return True


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_json).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not summary_path.exists():
        raise FileNotFoundError(f"summary json not found: {summary_path}")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    holdout_dual = get_metric(summary, "metrics", "holdout", "chi2_per_n_dual")
    holdout_null = get_metric(summary, "metrics", "holdout", "chi2_per_n_null")
    holdout_mond = get_metric(summary, "metrics", "holdout", "chi2_per_n_mond")
    holdout_improve = get_metric(summary, "metrics", "holdout", "improve_vs_null_pct")
    holdout_delta_aic = get_metric(summary, "metrics", "holdout", "delta_aic_dual_minus_mond")
    holdout_delta_bic = get_metric(summary, "metrics", "holdout", "delta_bic_dual_minus_mond")

    train_dual = get_metric(summary, "metrics", "train", "chi2_per_n_dual")
    train_mond = get_metric(summary, "metrics", "train", "chi2_per_n_mond")
    train_improve = get_metric(summary, "metrics", "train", "improve_vs_null_pct")

    generalization_gap = abs(train_improve - holdout_improve)
    holdout_mond_worse_pct = 100.0 * (holdout_dual - holdout_mond) / max(holdout_mond, 1e-12)
    train_mond_worse_pct = 100.0 * (train_dual - train_mond) / max(train_mond, 1e-12)

    expected_tau_grid = parse_float_grid(args.expected_tau_grid)
    expected_alpha_grid = parse_float_grid(args.expected_alpha_grid)

    observed_test_id = str(summary.get("test_id", ""))
    observed_dataset_id = str(summary.get("dataset_id", ""))
    observed_dataset_csv = str(summary.get("dataset_csv", ""))
    observed_split_seed = int(summary.get("split_seed", -1))
    observed_train_frac = float(summary.get("train_frac", -1.0))
    fixed_consts = summary.get("fixed_theory_constants", {})
    observed_s1_lambda = float(fixed_consts.get("s1_lambda", float("nan")))
    observed_s2_const = float(fixed_consts.get("s2_const", float("nan")))
    observed_r0_kpc = float(fixed_consts.get("r0_kpc", float("nan")))
    search_space = summary.get("search_space", {})
    observed_tau_grid = [float(x) for x in search_space.get("tau_grid", [])]
    observed_alpha_grid = [float(x) for x in search_space.get("alpha_grid", [])]

    lock_checks = {
        "lock_test_id": observed_test_id == str(args.expected_test_id),
        "lock_dataset_id": observed_dataset_id == str(args.expected_dataset_id),
        "lock_dataset_csv_name": Path(observed_dataset_csv).name == str(args.expected_dataset_csv_name),
        "lock_split_seed": observed_split_seed == int(args.expected_split_seed),
        "lock_train_frac": abs(observed_train_frac - float(args.expected_train_frac)) <= 1e-12,
        "lock_s1_lambda": abs(observed_s1_lambda - float(args.expected_s1_lambda)) <= 1e-12,
        "lock_s2_const": abs(observed_s2_const - float(args.expected_s2_const)) <= 1e-12,
        "lock_r0_kpc": abs(observed_r0_kpc - float(args.expected_r0_kpc)) <= 1e-12,
        "lock_tau_grid": list_almost_equal(observed_tau_grid, expected_tau_grid),
        "lock_alpha_grid": list_almost_equal(observed_alpha_grid, expected_alpha_grid),
    }

    metric_checks = {
        "holdout_improve_vs_null": holdout_improve >= float(args.min_holdout_improve_vs_null_pct),
        "holdout_not_worse_than_mond": holdout_mond_worse_pct <= float(args.max_holdout_mond_worse_pct),
        "train_not_far_worse_than_mond": train_mond_worse_pct <= float(args.max_train_mond_worse_pct),
        "generalization_gap_ok": generalization_gap <= float(args.max_generalization_gap_pp),
        "holdout_aic_not_worse_than_mond": holdout_delta_aic <= float(args.max_holdout_delta_aic_dual_minus_mond),
        "holdout_bic_not_worse_than_mond": holdout_delta_bic <= float(args.max_holdout_delta_bic_dual_minus_mond),
    }
    checks = {**lock_checks, **metric_checks}
    decision = "PASS" if all(checks.values()) else "HOLD"

    report = {
        "generated_utc": datetime.utcnow().isoformat() + "Z",
        "summary_json": summary_path.as_posix(),
        "criteria": {
            "expected_test_id": str(args.expected_test_id),
            "expected_dataset_id": str(args.expected_dataset_id),
            "expected_dataset_csv_name": str(args.expected_dataset_csv_name),
            "expected_split_seed": int(args.expected_split_seed),
            "expected_train_frac": float(args.expected_train_frac),
            "expected_s1_lambda": float(args.expected_s1_lambda),
            "expected_s2_const": float(args.expected_s2_const),
            "expected_r0_kpc": float(args.expected_r0_kpc),
            "expected_tau_grid": expected_tau_grid,
            "expected_alpha_grid": expected_alpha_grid,
            "min_holdout_improve_vs_null_pct": float(args.min_holdout_improve_vs_null_pct),
            "max_holdout_mond_worse_pct": float(args.max_holdout_mond_worse_pct),
            "max_train_mond_worse_pct": float(args.max_train_mond_worse_pct),
            "max_generalization_gap_pp": float(args.max_generalization_gap_pp),
            "max_holdout_delta_aic_dual_minus_mond": float(args.max_holdout_delta_aic_dual_minus_mond),
            "max_holdout_delta_bic_dual_minus_mond": float(args.max_holdout_delta_bic_dual_minus_mond),
        },
        "observed": {
            "test_id": observed_test_id,
            "dataset_id": observed_dataset_id,
            "dataset_csv_name": Path(observed_dataset_csv).name,
            "split_seed": observed_split_seed,
            "train_frac": observed_train_frac,
            "s1_lambda": observed_s1_lambda,
            "s2_const": observed_s2_const,
            "r0_kpc": observed_r0_kpc,
            "tau_grid": observed_tau_grid,
            "alpha_grid": observed_alpha_grid,
            "holdout_chi2_per_n_dual": holdout_dual,
            "holdout_chi2_per_n_null": holdout_null,
            "holdout_chi2_per_n_mond": holdout_mond,
            "holdout_improve_vs_null_pct": holdout_improve,
            "holdout_mond_worse_pct": holdout_mond_worse_pct,
            "holdout_delta_aic_dual_minus_mond": holdout_delta_aic,
            "holdout_delta_bic_dual_minus_mond": holdout_delta_bic,
            "train_chi2_per_n_dual": train_dual,
            "train_chi2_per_n_mond": train_mond,
            "train_improve_vs_null_pct": train_improve,
            "train_mond_worse_pct": train_mond_worse_pct,
            "generalization_gap_pp": generalization_gap,
        },
        "checks": checks,
        "decision": decision,
    }

    (out_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# D4 Stage-2 Dual-Kernel Evaluation (v2 strict vs MOND)",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- summary_json: `{summary_path.as_posix()}`",
        f"- decision: `{decision}`",
        "",
        "## Observed",
        "",
        f"- holdout chi2/N dual: `{holdout_dual:.6f}`",
        f"- holdout chi2/N mond: `{holdout_mond:.6f}`",
        f"- holdout improve vs null (%): `{holdout_improve:.6f}`",
        f"- holdout mond worse (%): `{holdout_mond_worse_pct:.6f}`",
        f"- holdout delta AIC (dual-mond): `{holdout_delta_aic:.6f}`",
        f"- holdout delta BIC (dual-mond): `{holdout_delta_bic:.6f}`",
        f"- train mond worse (%): `{train_mond_worse_pct:.6f}`",
        f"- train-holdout improve gap (pp): `{generalization_gap:.6f}`",
        "",
        "## Checks",
        "",
        f"- lock_test_id: `{checks['lock_test_id']}`",
        f"- lock_dataset_id: `{checks['lock_dataset_id']}`",
        f"- lock_dataset_csv_name: `{checks['lock_dataset_csv_name']}`",
        f"- lock_split_seed: `{checks['lock_split_seed']}`",
        f"- lock_train_frac: `{checks['lock_train_frac']}`",
        f"- lock_s1_lambda: `{checks['lock_s1_lambda']}`",
        f"- lock_s2_const: `{checks['lock_s2_const']}`",
        f"- lock_r0_kpc: `{checks['lock_r0_kpc']}`",
        f"- lock_tau_grid: `{checks['lock_tau_grid']}`",
        f"- lock_alpha_grid: `{checks['lock_alpha_grid']}`",
        f"- holdout_improve_vs_null: `{checks['holdout_improve_vs_null']}`",
        f"- holdout_not_worse_than_mond: `{checks['holdout_not_worse_than_mond']}`",
        f"- train_not_far_worse_than_mond: `{checks['train_not_far_worse_than_mond']}`",
        f"- generalization_gap_ok: `{checks['generalization_gap_ok']}`",
        f"- holdout_aic_not_worse_than_mond: `{checks['holdout_aic_not_worse_than_mond']}`",
        f"- holdout_bic_not_worse_than_mond: `{checks['holdout_bic_not_worse_than_mond']}`",
    ]
    (out_dir / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"evaluation_json: {out_dir / 'evaluation_report.json'}")
    print(f"decision: {decision}")
    if args.strict_exit and decision != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
