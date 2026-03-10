#!/usr/bin/env python3
"""Forensics for D4 winner v12 strict lane (seed/regime diagnostics, no tuning)."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_d4_stage2_dual_kernel_candidates_v5 import train_holdout_split
from scripts.run_d9_cross_validation_v1 import A0_INT, fit_mond, flatten, load_galaxies, v_m8c


DEFAULT_DATA = ROOT / "data" / "rotation" / "rotation_ds006_rotmod.csv"
DEFAULT_PER_SEED = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v12-strict"
    / "per_seed_candidate_summary.csv"
)
DEFAULT_EVAL = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v12-strict"
    / "evaluation-v1"
    / "per_seed_evaluation.csv"
)
DEFAULT_OUT = (
    ROOT
    / "05_validation"
    / "evidence"
    / "artifacts"
    / "d4-stage2-winner-v12-forensics-v1"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze D4 winner v12 failure signatures (forensics-only).")
    p.add_argument("--dataset-id", default="DS-006")
    p.add_argument("--dataset-csv", default=str(DEFAULT_DATA))
    p.add_argument("--per-seed-csv", default=str(DEFAULT_PER_SEED))
    p.add_argument("--eval-csv", default=str(DEFAULT_EVAL))
    p.add_argument("--train-frac", type=float, default=0.70)
    p.add_argument("--split-seeds", default="")
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def f6(x: float) -> str:
    return f"{x:.6f}"


def mond_v(point: dict[str, float], g_dag: float) -> float:
    g_bar = point["g_bar"]
    if g_bar <= 0:
        return 0.0
    x = math.sqrt(g_bar / max(g_dag, 1e-30))
    denom = 1.0 - math.exp(-x)
    g_obs = g_bar / denom if denom > 1e-15 else math.sqrt(g_bar * g_dag)
    return math.sqrt(max(g_obs * point["r"], 0.0))


def null_v(point: dict[str, float]) -> float:
    return math.sqrt(max(point["bt"], 0.0))


def accel_bin(point: dict[str, float]) -> str:
    chi = point["g_bar"] / max(A0_INT, 1e-30)
    if chi < 1.0:
        return "low_accel"
    if chi < 10.0:
        return "mid_accel"
    return "high_accel"


@dataclass
class SeedParams:
    seed: int
    k_fit: float
    g_dag_fit: float


def parse_seed_list(text: str) -> list[int]:
    out: list[int] = []
    for tok in text.split(","):
        t = tok.strip()
        if not t:
            continue
        out.append(int(t))
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    n = max(1, len(rows))
    c2_w = sum(float(r["chi2_winner"]) for r in rows)
    c2_m = sum(float(r["chi2_mond"]) for r in rows)
    c2_n = sum(float(r["chi2_null"]) for r in rows)
    w = c2_w / n
    m = c2_m / n
    nn = c2_n / n
    return {
        "n_points": float(n),
        "chi2_per_n_winner": w,
        "chi2_per_n_mond": m,
        "chi2_per_n_null": nn,
        "winner_over_mond": w / max(m, 1e-12),
        "winner_minus_mond": w - m,
        "improve_vs_null_pct": 100.0 * (nn - w) / max(nn, 1e-12),
    }


def radial_bin_for_index(i: int, n: int) -> str:
    q = (i + 0.5) / max(1, n)
    if q <= 1.0 / 3.0:
        return "inner"
    if q <= 2.0 / 3.0:
        return "mid"
    return "outer"


def main() -> int:
    args = parse_args()

    dataset_path = Path(args.dataset_csv).resolve()
    per_seed_csv = Path(args.per_seed_csv).resolve()
    eval_csv = Path(args.eval_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for p in (dataset_path, per_seed_csv, eval_csv):
        if not p.exists():
            raise FileNotFoundError(f"missing input: {p}")

    per_seed_rows = read_csv(per_seed_csv)
    eval_rows = read_csv(eval_csv)

    params_by_seed: dict[int, SeedParams] = {}
    for r in per_seed_rows:
        seed = int(str(r.get("split_seed", "0")))
        params_by_seed[seed] = SeedParams(
            seed=seed,
            k_fit=float(str(r.get("best_k1", "0"))),
            g_dag_fit=float(str(r.get("best_k2", "0"))),
        )

    eval_by_seed: dict[int, dict[str, str]] = {}
    for r in eval_rows:
        seed = int(str(r.get("split_seed", "0")))
        eval_by_seed[seed] = r

    if args.split_seeds.strip():
        seeds = parse_seed_list(args.split_seeds)
    else:
        fail_seeds = [
            int(str(r.get("split_seed", "0")))
            for r in eval_rows
            if str(r.get("seed_decision", "")).strip().upper() != "PASS"
        ]
        seeds = sorted(set(fail_seeds))

    if not seeds:
        raise RuntimeError("no target seeds selected for forensics")

    galaxies = load_galaxies(dataset_path)
    galaxy_ids = sorted(galaxies.keys())

    seed_summary_rows: list[dict[str, Any]] = []
    regime_rows: list[dict[str, Any]] = []
    worst_rows: list[dict[str, Any]] = []

    for seed in seeds:
        par = params_by_seed.get(seed)
        if par is None:
            raise RuntimeError(f"missing parameters for seed {seed} in {per_seed_csv}")
        ev = eval_by_seed.get(seed, {})

        train_ids, holdout_ids = train_holdout_split(galaxy_ids, seed, float(args.train_frac))
        train_points = flatten(galaxies, sorted(train_ids))
        holdout_points = flatten(galaxies, sorted(holdout_ids))

        gd_mond_fit, train_mond_per_n = fit_mond(train_points)
        holdout_mond_per_n = sum(
            ((p["v"] - mond_v(p, gd_mond_fit)) / p["ve"]) ** 2 for p in holdout_points
        ) / max(1, len(holdout_points))

        point_rows: list[dict[str, Any]] = []
        for gid in sorted(holdout_ids):
            pts = galaxies[gid]
            n = max(1, len(pts))
            for i, p in enumerate(pts):
                v_w = v_m8c(p, par.k_fit, par.g_dag_fit)
                v_m = mond_v(p, gd_mond_fit)
                v_n = null_v(p)
                point_rows.append(
                    {
                        "seed": seed,
                        "galaxy": gid,
                        "accel_bin": accel_bin(p),
                        "radial_bin": radial_bin_for_index(i, n),
                        "chi2_winner": ((p["v"] - v_w) / p["ve"]) ** 2,
                        "chi2_mond": ((p["v"] - v_m) / p["ve"]) ** 2,
                        "chi2_null": ((p["v"] - v_n) / p["ve"]) ** 2,
                    }
                )

        holdout_sum = summarize(point_rows)
        seed_summary_rows.append(
            {
                "seed": str(seed),
                "seed_decision": str(ev.get("seed_decision", "UNKNOWN")),
                "check_holdout_not_worse_than_mond": str(ev.get("check_holdout_not_worse_than_mond", "")),
                "check_generalization_gap_ok": str(ev.get("check_generalization_gap_ok", "")),
                "holdout_mond_worse_pct": str(ev.get("holdout_mond_worse_pct", "")),
                "generalization_gap_pp": str(ev.get("generalization_gap_pp", "")),
                "holdout_chi2_per_n_winner": f6(holdout_sum["chi2_per_n_winner"]),
                "holdout_chi2_per_n_mond": f6(holdout_sum["chi2_per_n_mond"]),
                "holdout_winner_over_mond": f6(holdout_sum["winner_over_mond"]),
                "k_fit": f6(par.k_fit),
                "g_dag_fit": f6(par.g_dag_fit),
                "g_dag_mond_fit": f6(gd_mond_fit),
            }
        )

        for group_name, col, bins in (
            ("accel", "accel_bin", ("low_accel", "mid_accel", "high_accel")),
            ("radial", "radial_bin", ("inner", "mid", "outer")),
        ):
            for b in bins:
                rr = [r for r in point_rows if str(r[col]) == b]
                if not rr:
                    continue
                s = summarize(rr)
                regime_rows.append(
                    {
                        "seed": str(seed),
                        "group": group_name,
                        "bin": b,
                        "n_points": str(int(s["n_points"])),
                        "chi2_per_n_winner": f6(s["chi2_per_n_winner"]),
                        "chi2_per_n_mond": f6(s["chi2_per_n_mond"]),
                        "winner_over_mond": f6(s["winner_over_mond"]),
                        "winner_minus_mond": f6(s["winner_minus_mond"]),
                        "improve_vs_null_pct": f6(s["improve_vs_null_pct"]),
                    }
                )

        by_gal: dict[str, list[dict[str, Any]]] = {}
        for r in point_rows:
            by_gal.setdefault(str(r["galaxy"]), []).append(r)
        gal_rows: list[dict[str, Any]] = []
        for gid, rr in by_gal.items():
            s = summarize(rr)
            gal_rows.append(
                {
                    "seed": str(seed),
                    "galaxy": gid,
                    "n_points": str(int(s["n_points"])),
                    "chi2_per_n_winner": f6(s["chi2_per_n_winner"]),
                    "chi2_per_n_mond": f6(s["chi2_per_n_mond"]),
                    "winner_over_mond": f6(s["winner_over_mond"]),
                    "winner_minus_mond": f6(s["winner_minus_mond"]),
                    "improve_vs_null_pct": f6(s["improve_vs_null_pct"]),
                }
            )
        gal_rows.sort(key=lambda x: float(str(x["winner_over_mond"])), reverse=True)
        worst_rows.extend(gal_rows[:10])

    # Aggregate pattern summary over selected seeds.
    pattern_rows: list[dict[str, Any]] = []
    for group_name, bins in (
        ("accel", ("low_accel", "mid_accel", "high_accel")),
        ("radial", ("inner", "mid", "outer")),
    ):
        for b in bins:
            rr = [r for r in regime_rows if str(r["group"]) == group_name and str(r["bin"]) == b]
            if not rr:
                continue
            vals = [float(str(r["winner_over_mond"])) for r in rr]
            worse_count = sum(1 for v in vals if v > 1.0)
            pattern_rows.append(
                {
                    "group": group_name,
                    "bin": b,
                    "n_seed_bins": str(len(vals)),
                    "mean_winner_over_mond": f6(sum(vals) / max(1, len(vals))),
                    "max_winner_over_mond": f6(max(vals)),
                    "worse_than_mond_count": str(worse_count),
                }
            )

    write_csv(
        out_dir / "failure_seed_summary.csv",
        seed_summary_rows,
        [
            "seed",
            "seed_decision",
            "check_holdout_not_worse_than_mond",
            "check_generalization_gap_ok",
            "holdout_mond_worse_pct",
            "generalization_gap_pp",
            "holdout_chi2_per_n_winner",
            "holdout_chi2_per_n_mond",
            "holdout_winner_over_mond",
            "k_fit",
            "g_dag_fit",
            "g_dag_mond_fit",
        ],
    )
    write_csv(
        out_dir / "regime_summary.csv",
        regime_rows,
        [
            "seed",
            "group",
            "bin",
            "n_points",
            "chi2_per_n_winner",
            "chi2_per_n_mond",
            "winner_over_mond",
            "winner_minus_mond",
            "improve_vs_null_pct",
        ],
    )
    write_csv(
        out_dir / "holdout_top_worst_galaxies.csv",
        worst_rows,
        [
            "seed",
            "galaxy",
            "n_points",
            "chi2_per_n_winner",
            "chi2_per_n_mond",
            "winner_over_mond",
            "winner_minus_mond",
            "improve_vs_null_pct",
        ],
    )
    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        [
            "group",
            "bin",
            "n_seed_bins",
            "mean_winner_over_mond",
            "max_winner_over_mond",
            "worse_than_mond_count",
        ],
    )

    # human summary
    sorted_patterns = sorted(pattern_rows, key=lambda r: float(str(r["mean_winner_over_mond"])), reverse=True)
    pressure_patterns = [r for r in sorted_patterns if float(str(r["mean_winner_over_mond"])) > 1.0]
    top_patterns = pressure_patterns[:3] if pressure_patterns else sorted_patterns[:3]

    report_lines = [
        "# D4 Winner V12 Forensics v1",
        "",
        "Forensics-only analysis (no formula/threshold changes).",
        "",
        f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`",
        f"- dataset_id: `{args.dataset_id}`",
        f"- seeds analyzed: `{','.join(str(s) for s in seeds)}`",
        f"- source per-seed csv: `{per_seed_csv}`",
        f"- source eval csv: `{eval_csv}`",
        "",
        "## Seed Status",
        "",
    ]
    for r in seed_summary_rows:
        report_lines.append(
            f"- seed {r['seed']}: decision={r['seed_decision']}, "
            f"holdout_mond_worse_pct={r['holdout_mond_worse_pct']}, "
            f"generalization_gap_pp={r['generalization_gap_pp']}"
        )
    report_lines += ["", "## Top Regime Pressure (winner_over_mond > 1)", ""]
    for r in top_patterns:
        report_lines.append(
            f"- {r['group']}:{r['bin']} -> mean={r['mean_winner_over_mond']}, max={r['max_winner_over_mond']}, "
            f"worse_count={r['worse_than_mond_count']}/{r['n_seed_bins']}"
        )
    report_lines += [
        "",
        "## Interpretation",
        "",
        "- If pressure concentrates in `outer` and/or `low_accel`, next candidate should target only that regime.",
        "- Keep strict thresholds unchanged; evaluate candidate on all 5 seeds.",
        "",
        "Artifacts:",
        f"- `{(out_dir / 'failure_seed_summary.csv').as_posix()}`",
        f"- `{(out_dir / 'regime_summary.csv').as_posix()}`",
        f"- `{(out_dir / 'holdout_top_worst_galaxies.csv').as_posix()}`",
        f"- `{(out_dir / 'pattern_summary.csv').as_posix()}`",
    ]
    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    summary = {
        "analysis_id": "d4-stage2-winner-v12-forensics-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_id": str(args.dataset_id),
        "seeds": seeds,
        "top_patterns": top_patterns,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"[ok] wrote forensics to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
