#!/usr/bin/env python3
"""Evaluate D4 Stage-2 candidate formulas v5 on strict multi-split criteria."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_PER_SEED = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v5-candidates"
    / "per_seed_candidate_summary.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-dual-kernel-v5-candidates"
    / "evaluation-v1"
)


def parse_list(raw: str) -> list[float]:
    out: list[float] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(float(t))
    return out


def parse_int_list(raw: str) -> list[int]:
    out: list[int] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(int(t))
    return out


def parse_str_list(raw: str) -> list[str]:
    out: list[str] = []
    for token in str(raw).split(","):
        t = token.strip()
        if not t:
            continue
        out.append(t)
    return out


def list_almost_equal(a: list[float], b: list[float], tol: float = 1e-12) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if abs(float(x) - float(y)) > tol:
            return False
    return True


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate D4 Stage-2 candidates v5 strict multi-split criteria.")
    p.add_argument("--per-seed-csv", default=str(DEFAULT_PER_SEED))
    p.add_argument("--manifest-json", default="")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))

    # Lock checks (anti post-hoc governance).
    p.add_argument("--expected-test-id", default="d4-stage2-dual-kernel-v5-candidates")
    p.add_argument("--expected-dataset-id", default="DS-006")
    p.add_argument("--expected-dataset-csv-rel", default="data/rotation/rotation_ds006_rotmod.csv")
    p.add_argument("--expected-dataset-sha256", default="1067802fb376629095ab4a0f8d8358eadd0dda488f046305659ac966d1ab556c")
    p.add_argument("--expected-split-seeds", default="3401,3402,3403,3404,3405")
    p.add_argument("--expected-train-frac", type=float, default=0.70)
    p.add_argument("--expected-s1-lambda", type=float, default=0.28)
    p.add_argument("--expected-s2-const", type=float, default=0.355)
    p.add_argument("--expected-r0-kpc", type=float, default=1.0)
    p.add_argument("--expected-r-tail-kpc", type=float, default=4.0)
    p.add_argument("--expected-focus-gamma", type=float, default=2.0)
    p.add_argument("--expected-tau-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,1,2,3,5,8,12,20,30,50")
    p.add_argument("--expected-alpha-grid", default="0.02,0.05,0.1,0.2,0.3,0.5,0.7,1.0,1.3")
    p.add_argument("--expected-candidates", default="outer_lowaccel_single,outer_lowaccel_focus")

    p.add_argument("--min-holdout-improve-vs-null-pct", type=float, default=10.0)
    p.add_argument("--max-holdout-mond-worse-pct", type=float, default=0.0)
    p.add_argument("--max-generalization-gap-pp", type=float, default=20.0)
    p.add_argument("--max-holdout-delta-aic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--max-holdout-delta-bic-dual-minus-mond", type=float, default=0.0)
    p.add_argument("--strict-exit", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def f6(x: float) -> str:
    return f"{x:.6f}"


def main() -> int:
    args = parse_args()
    per_seed_path = Path(args.per_seed_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = (
        Path(args.manifest_json).resolve() if str(args.manifest_json).strip() else per_seed_path.parent / "manifest.json"
    )
    if not per_seed_path.exists():
        raise FileNotFoundError(f"per-seed csv not found: {per_seed_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest json not found: {manifest_path}")

    rows = read_csv(per_seed_path)
    if not rows:
        raise RuntimeError("no rows in per-seed candidate summary")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_seed_list = parse_int_list(args.expected_split_seeds)
    expected_seed_set = set(expected_seed_list)
    expected_tau = parse_list(args.expected_tau_grid)
    expected_alpha = parse_list(args.expected_alpha_grid)
    expected_candidates = parse_str_list(args.expected_candidates)
    expected_candidate_set = set(expected_candidates)

    obs_seed_list = [int(x) for x in manifest.get("split_seeds", [])]
    obs_seed_set = set(obs_seed_list)
    obs_consts = manifest.get("fixed_theory_constants", {})
    obs_search = manifest.get("search_space", {})
    obs_fit = manifest.get("fit_objective", {})
    obs_candidates = [str(x) for x in manifest.get("candidates", [])]
    obs_candidate_set = set(obs_candidates)

    csv_seed_set = {int(r["split_seed"]) for r in rows}
    csv_candidates = {str(r["candidate"]) for r in rows}

    # One row per (candidate, seed) expected tuple.
    unique_pairs = {(str(r["candidate"]), int(r["split_seed"])) for r in rows}
    expected_pair_count = len(expected_seed_set) * len(expected_candidate_set)
    no_duplicate_pairs = len(unique_pairs) == len(rows)
    full_pair_coverage = len(unique_pairs) == expected_pair_count
    for c in expected_candidate_set:
        seen = {int(r["split_seed"]) for r in rows if str(r["candidate"]) == c}
        if seen != expected_seed_set:
            full_pair_coverage = False
            break

    # Per-row checks against locked metadata.
    row_lock_ok = True
    for r in rows:
        if (
            str(r.get("test_id", "")) != str(args.expected_test_id)
            or str(r.get("dataset_id", "")) != str(args.expected_dataset_id)
            or str(r.get("dataset_csv_rel", "")).replace("\\", "/") != str(args.expected_dataset_csv_rel)
            or str(r.get("dataset_sha256", "")).lower() != str(args.expected_dataset_sha256).lower()
        ):
            row_lock_ok = False
            break

    lock_checks = {
        "lock_test_id": str(manifest.get("test_id", "")) == str(args.expected_test_id),
        "lock_dataset_id": str(manifest.get("dataset_id", "")) == str(args.expected_dataset_id),
        "lock_dataset_csv_rel": str(manifest.get("dataset_csv_rel", "")).replace("\\", "/")
        == str(args.expected_dataset_csv_rel),
        "lock_dataset_sha256": str(manifest.get("dataset_sha256", "")).lower()
        == str(args.expected_dataset_sha256).lower(),
        "lock_split_seeds_manifest": obs_seed_list == expected_seed_list,
        "lock_split_seeds_csv": csv_seed_set == expected_seed_set,
        "lock_train_frac": abs(float(manifest.get("train_frac", -1.0)) - float(args.expected_train_frac)) <= 1e-12,
        "lock_s1_lambda": abs(float(obs_consts.get("s1_lambda", float("nan"))) - float(args.expected_s1_lambda))
        <= 1e-12,
        "lock_s2_const": abs(float(obs_consts.get("s2_const", float("nan"))) - float(args.expected_s2_const))
        <= 1e-12,
        "lock_r0_kpc": abs(float(obs_consts.get("r0_kpc", float("nan"))) - float(args.expected_r0_kpc)) <= 1e-12,
        "lock_r_tail_kpc": abs(float(obs_consts.get("r_tail_kpc", float("nan"))) - float(args.expected_r_tail_kpc))
        <= 1e-12,
        "lock_focus_gamma": abs(float(obs_fit.get("focus_gamma", float("nan"))) - float(args.expected_focus_gamma))
        <= 1e-12,
        "lock_grid_selection_objective": str(obs_fit.get("grid_selection_objective", "")) == "train_focus_chi2",
        "lock_tau_grid": list_almost_equal([float(x) for x in obs_search.get("tau_grid", [])], expected_tau),
        "lock_alpha_grid": list_almost_equal([float(x) for x in obs_search.get("alpha_grid", [])], expected_alpha),
        "lock_candidates_manifest": obs_candidate_set == expected_candidate_set,
        "lock_candidates_csv": csv_candidates == expected_candidate_set,
        "lock_pairs_unique": no_duplicate_pairs,
        "lock_pairs_full_coverage": full_pair_coverage,
        "lock_row_metadata": row_lock_ok,
    }
    governance_lock_pass = all(lock_checks.values())

    evaluated_rows: list[dict[str, Any]] = []
    for r in rows:
        holdout_improve = float(r["holdout_improve_vs_null_pct"])
        holdout_mond_worse = float(r["holdout_mond_worse_pct"])
        gen_gap = float(r["generalization_gap_pp"])
        daic = float(r["holdout_delta_aic_dual_minus_mond"])
        dbic = float(r["holdout_delta_bic_dual_minus_mond"])
        checks = {
            "holdout_improve_vs_null": holdout_improve >= float(args.min_holdout_improve_vs_null_pct),
            "holdout_not_worse_than_mond": holdout_mond_worse <= float(args.max_holdout_mond_worse_pct),
            "generalization_gap_ok": gen_gap <= float(args.max_generalization_gap_pp),
            "holdout_aic_not_worse_than_mond": daic <= float(args.max_holdout_delta_aic_dual_minus_mond),
            "holdout_bic_not_worse_than_mond": dbic <= float(args.max_holdout_delta_bic_dual_minus_mond),
        }
        decision = "PASS" if all(checks.values()) else "HOLD"
        out = dict(r)
        out.update(
            {
                "check_holdout_improve_vs_null": "pass" if checks["holdout_improve_vs_null"] else "fail",
                "check_holdout_not_worse_than_mond": "pass" if checks["holdout_not_worse_than_mond"] else "fail",
                "check_generalization_gap_ok": "pass" if checks["generalization_gap_ok"] else "fail",
                "check_holdout_aic_not_worse_than_mond": "pass"
                if checks["holdout_aic_not_worse_than_mond"]
                else "fail",
                "check_holdout_bic_not_worse_than_mond": "pass"
                if checks["holdout_bic_not_worse_than_mond"]
                else "fail",
                "seed_decision": decision,
            }
        )
        evaluated_rows.append(out)

    eval_fields = list(evaluated_rows[0].keys())
    with (out_dir / "per_seed_evaluation.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=eval_fields)
        w.writeheader()
        w.writerows(evaluated_rows)

    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for r in evaluated_rows:
        by_candidate.setdefault(str(r["candidate"]), []).append(r)

    candidate_rows: list[dict[str, Any]] = []
    for candidate in sorted(by_candidate.keys()):
        rr = by_candidate[candidate]
        n = len(rr)
        n_pass = sum(1 for x in rr if x["seed_decision"] == "PASS")
        complete_coverage = n == len(expected_seed_set)
        decision = "PASS" if complete_coverage and n_pass == n else "HOLD"
        candidate_rows.append(
            {
                "candidate": candidate,
                "n_splits": str(n),
                "n_pass": str(n_pass),
                "n_hold": str(n - n_pass),
                "pass_fraction": f6(n_pass / max(n, 1)),
                "complete_seed_coverage": str(complete_coverage).lower(),
                "decision": decision,
            }
        )

    with (out_dir / "candidate_decisions.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "candidate",
                "n_splits",
                "n_pass",
                "n_hold",
                "pass_fraction",
                "complete_seed_coverage",
                "decision",
            ],
        )
        w.writeheader()
        w.writerows(candidate_rows)

    global_decision = (
        "PASS"
        if governance_lock_pass and any(r["decision"] == "PASS" for r in candidate_rows)
        else "HOLD"
    )
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "per_seed_csv": per_seed_path.as_posix(),
        "manifest_json": manifest_path.as_posix(),
        "criteria": {
            "expected_test_id": str(args.expected_test_id),
            "expected_dataset_id": str(args.expected_dataset_id),
            "expected_dataset_csv_rel": str(args.expected_dataset_csv_rel),
            "expected_dataset_sha256": str(args.expected_dataset_sha256).lower(),
            "expected_split_seeds": expected_seed_list,
            "expected_train_frac": float(args.expected_train_frac),
            "expected_s1_lambda": float(args.expected_s1_lambda),
            "expected_s2_const": float(args.expected_s2_const),
            "expected_r0_kpc": float(args.expected_r0_kpc),
            "expected_r_tail_kpc": float(args.expected_r_tail_kpc),
            "expected_focus_gamma": float(args.expected_focus_gamma),
            "expected_tau_grid": expected_tau,
            "expected_alpha_grid": expected_alpha,
            "expected_candidates": expected_candidates,
            "min_holdout_improve_vs_null_pct": float(args.min_holdout_improve_vs_null_pct),
            "max_holdout_mond_worse_pct": float(args.max_holdout_mond_worse_pct),
            "max_generalization_gap_pp": float(args.max_generalization_gap_pp),
            "max_holdout_delta_aic_dual_minus_mond": float(args.max_holdout_delta_aic_dual_minus_mond),
            "max_holdout_delta_bic_dual_minus_mond": float(args.max_holdout_delta_bic_dual_minus_mond),
            "candidate_pass_rule": "all split seeds must PASS with full seed coverage",
        },
        "lock_checks": lock_checks,
        "governance_lock_pass": governance_lock_pass,
        "candidate_decisions": candidate_rows,
        "global_decision": global_decision,
    }
    (out_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# D4 Stage-2 Candidate Evaluation v5",
        "",
        f"- generated_utc: `{report['generated_utc']}`",
        f"- governance_lock_pass: `{governance_lock_pass}`",
        f"- global_decision: `{global_decision}`",
        "",
        "## Lock Checks",
        "",
    ]
    for k in sorted(lock_checks.keys()):
        lines.append(f"- `{k}`: `{lock_checks[k]}`")
    lines += ["", "## Candidate Decisions", ""]
    for r in candidate_rows:
        lines.append(
            f"- `{r['candidate']}`: {r['n_pass']}/{r['n_splits']} pass "
            f"(coverage={r['complete_seed_coverage']}), decision={r['decision']}"
        )
    (out_dir / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"per_seed_eval_csv: {(out_dir / 'per_seed_evaluation.csv').as_posix()}")
    print(f"candidate_decisions_csv: {(out_dir / 'candidate_decisions.csv').as_posix()}")
    print(f"evaluation_json: {(out_dir / 'evaluation_report.json').as_posix()}")
    print(f"governance_lock_pass: {governance_lock_pass}")
    print(f"global_decision: {global_decision}")
    if args.strict_exit and global_decision != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
