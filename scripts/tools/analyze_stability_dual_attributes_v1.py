#!/usr/bin/env python3
"""
Dual-attribute stability diagnostic (S1 energetic vs S2 structural).

This is diagnostic-only and does not change gate thresholds/formulas.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_RUN_DIRS = ",".join(
    [
        str(ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v4"),
        str(ROOT / "05_validation" / "evidence" / "artifacts" / "stability-convergence-v5"),
    ]
)
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-dual-attributes-v1"


STRUCTURAL_GATES = [
    "gate_sigma_bounds",
    "gate_metric_positive",
    "gate_metric_cond",
    "gate_runaway",
    "gate_variational_residual",
    "gate_alpha_drift",
    "gate_no_signalling",
]
ENERGY_GATE = "gate_energy_drift"


@dataclass
class RunPaths:
    run_dir: Path
    raw_summary: Path
    seed_checks: Path | None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze dual attributes in stability runs.")
    p.add_argument("--run-dirs", default=DEFAULT_RUN_DIRS)
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def avg(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def median(vals: list[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def std(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = avg(vals)
    return math.sqrt(sum((x - m) * (x - m) for x in vals) / len(vals))


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        x = float(str(v).strip())
    except Exception:
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return x


def is_pass(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in {"pass", "true", "1", "yes"}


def resolve_runs(raw: str) -> list[RunPaths]:
    out: list[RunPaths] = []
    for p in [x.strip() for x in raw.split(",") if x.strip()]:
        run_dir = Path(p).resolve()
        raw_summary = run_dir / "raw" / "summary.csv"
        seed_checks = run_dir / "seed_checks.csv"
        if not raw_summary.exists():
            continue
        out.append(RunPaths(run_dir=run_dir, raw_summary=raw_summary, seed_checks=seed_checks if seed_checks.exists() else None))
    return out


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = resolve_runs(args.run_dirs)
    if not runs:
        raise RuntimeError("no valid run directories")

    lane_rows: list[dict[str, Any]] = []
    seed_rows: list[dict[str, Any]] = []

    for run in runs:
        raw = read_csv(run.raw_summary)
        if not raw:
            continue
        run_id = run.run_dir.name

        profile_total = len(raw)
        structural_profile_pass = 0
        energetic_profile_pass = 0
        by_seed: dict[str, list[dict[str, str]]] = {}
        for r in raw:
            s = str(r.get("grid_seed", "")).strip()
            by_seed.setdefault(s, []).append(r)
            if all(is_pass(r.get(g, "")) for g in STRUCTURAL_GATES):
                structural_profile_pass += 1
            if is_pass(r.get(ENERGY_GATE, "")):
                energetic_profile_pass += 1

        seed_checks_map: dict[str, dict[str, str]] = {}
        if run.seed_checks is not None:
            for r in read_csv(run.seed_checks):
                seed_checks_map[str(r.get("seed", "")).strip()] = r

        s1_seed_scores: list[float] = []
        s2_seed_scores: list[float] = []
        structural_seed_pass_count = 0
        energetic_seed_pass_count = 0
        full_seed_pass_count = 0
        bulk_seed_pass_count = 0

        for seed in sorted(by_seed.keys(), key=lambda x: int(x) if x.isdigit() else x):
            rs = by_seed[seed]
            s1_energy_mean = avg([to_float(r.get("delta_energy_rel", "0.0")) for r in rs])
            s1_energy_gate_pass_rate = avg([1.0 if is_pass(r.get(ENERGY_GATE, "")) else 0.0 for r in rs])

            s2_struct_gate_pass_rate = avg(
                [1.0 if all(is_pass(r.get(g, "")) for g in STRUCTURAL_GATES) else 0.0 for r in rs]
            )
            core_ratio_vals = [to_float(r.get("core_stable_ratio", "0.0")) for r in rs if "core_stable_ratio" in r]
            s2_core_ratio_mean = avg(core_ratio_vals)
            s2_core_ratio_std = std(core_ratio_vals)

            structural_seed_pass = s2_struct_gate_pass_rate >= 0.999999
            energetic_seed_pass = s1_energy_gate_pass_rate >= 0.999999
            if structural_seed_pass:
                structural_seed_pass_count += 1
            if energetic_seed_pass:
                energetic_seed_pass_count += 1

            sc = seed_checks_map.get(seed, {})
            full_pass = is_pass(sc.get("full_pass", "")) if sc else False
            bulk_pass = is_pass(sc.get("bulk_pass", "")) if sc else False
            if full_pass:
                full_seed_pass_count += 1
            if bulk_pass:
                bulk_seed_pass_count += 1

            seed_rows.append(
                {
                    "run_id": run_id,
                    "seed": seed,
                    "s1_energy_mean": f"{s1_energy_mean:.6f}",
                    "s1_energy_gate_pass_rate": f"{s1_energy_gate_pass_rate:.6f}",
                    "s2_struct_gate_pass_rate": f"{s2_struct_gate_pass_rate:.6f}",
                    "s2_core_ratio_mean": f"{s2_core_ratio_mean:.6f}",
                    "s2_core_ratio_std": f"{s2_core_ratio_std:.6f}",
                    "structural_seed_pass": "true" if structural_seed_pass else "false",
                    "energetic_seed_pass": "true" if energetic_seed_pass else "false",
                    "full_pass": "true" if full_pass else "false",
                    "bulk_pass": "true" if bulk_pass else "false",
                }
            )
            s1_seed_scores.append(s1_energy_gate_pass_rate)
            s2_seed_scores.append(s2_struct_gate_pass_rate)

        lane_rows.append(
            {
                "run_id": run_id,
                "profile_total": profile_total,
                "structural_profile_pass_fraction": f"{(structural_profile_pass / profile_total):.6f}",
                "energetic_profile_pass_fraction": f"{(energetic_profile_pass / profile_total):.6f}",
                "seed_total": len(by_seed),
                "structural_seed_pass_fraction": f"{(structural_seed_pass_count / max(len(by_seed),1)):.6f}",
                "energetic_seed_pass_fraction": f"{(energetic_seed_pass_count / max(len(by_seed),1)):.6f}",
                "full_seed_pass_fraction": f"{(full_seed_pass_count / max(len(by_seed),1)):.6f}" if seed_checks_map else "",
                "bulk_seed_pass_fraction": f"{(bulk_seed_pass_count / max(len(by_seed),1)):.6f}" if seed_checks_map else "",
                "s1_seed_pass_rate_median": f"{median(s1_seed_scores):.6f}",
                "s2_seed_pass_rate_median": f"{median(s2_seed_scores):.6f}",
                "s2_seed_pass_rate_std": f"{std(s2_seed_scores):.6f}",
            }
        )

    write_csv(
        out_dir / "lane_summary.csv",
        lane_rows,
        [
            "run_id",
            "profile_total",
            "structural_profile_pass_fraction",
            "energetic_profile_pass_fraction",
            "seed_total",
            "structural_seed_pass_fraction",
            "energetic_seed_pass_fraction",
            "full_seed_pass_fraction",
            "bulk_seed_pass_fraction",
            "s1_seed_pass_rate_median",
            "s2_seed_pass_rate_median",
            "s2_seed_pass_rate_std",
        ],
    )
    write_csv(
        out_dir / "seed_dual_attributes.csv",
        seed_rows,
        [
            "run_id",
            "seed",
            "s1_energy_mean",
            "s1_energy_gate_pass_rate",
            "s2_struct_gate_pass_rate",
            "s2_core_ratio_mean",
            "s2_core_ratio_std",
            "structural_seed_pass",
            "energetic_seed_pass",
            "full_pass",
            "bulk_pass",
        ],
    )

    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Stability Dual-Attributes Diagnostic (v1)",
        "",
        f"- generated_utc: `{generated}`",
        "- S1 definition: energetic channel (`gate_energy_drift` behavior).",
        "- S2 definition: structural channel (all non-energy stability gates + core-support stability descriptors).",
        "",
        "## Lane Summary",
        "",
    ]
    for r in lane_rows:
        lines.extend(
            [
                f"### {r['run_id']}",
                f"- structural_profile_pass_fraction: `{r['structural_profile_pass_fraction']}`",
                f"- energetic_profile_pass_fraction: `{r['energetic_profile_pass_fraction']}`",
                f"- structural_seed_pass_fraction: `{r['structural_seed_pass_fraction']}`",
                f"- energetic_seed_pass_fraction: `{r['energetic_seed_pass_fraction']}`",
                f"- full_seed_pass_fraction: `{r['full_seed_pass_fraction']}`",
                f"- bulk_seed_pass_fraction: `{r['bulk_seed_pass_fraction']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "- If S2 stays near 1.0 while S1 degrades, stability behaves as at least two separable attributes (energetic vs structural).",
            "- This diagnostic is evidence-only and does not redefine official gates.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"lane_summary_csv: {out_dir / 'lane_summary.csv'}")
    print(f"seed_dual_attributes_csv: {out_dir / 'seed_dual_attributes.csv'}")
    print(f"report_md: {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
