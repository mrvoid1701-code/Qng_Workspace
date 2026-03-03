#!/usr/bin/env python3
"""
Analyze QNG stability-v1 stress failures and build a strict taxonomy package.

Outputs:
- fail_cases.csv
- pass_cases.csv
- pattern_summary.csv
- feature_correlations.csv
- report.md
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SUMMARY = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-v1" / "summary.csv"
DEFAULT_OUT = ROOT / "05_validation" / "evidence" / "artifacts" / "stability-v1-failure-taxonomy-v1"

GATE_FIELDS = [
    "gate_sigma_bounds",
    "gate_metric_positive",
    "gate_metric_cond",
    "gate_runaway",
    "gate_energy_drift",
    "gate_variational_residual",
    "gate_alpha_drift",
    "gate_no_signalling",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze stability-v1 failures and build taxonomy outputs.")
    p.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=10)
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


def to_float(v: Any) -> float | None:
    txt = str(v or "").strip().lower()
    if not txt:
        return None
    if txt in {"true", "false"}:
        return 1.0 if txt == "true" else 0.0
    try:
        out = float(txt)
    except Exception:
        return None
    if math.isnan(out) or math.isinf(out):
        return None
    return out


def norm_status(v: Any) -> str:
    return "pass" if str(v or "").strip().lower() == "pass" else "fail"


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) * (x - mx) for x in xs)
    syy = sum((y - my) * (y - my) for y in ys)
    if sxx <= 1e-18 or syy <= 1e-18:
        return None
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def classify_mechanism(row: dict[str, str]) -> str:
    e_gate = to_float(row.get("delta_energy_rel", "")) or 0.0
    e_noether = to_float(row.get("energy_noether_rel", "")) or 0.0
    slope_late = abs(to_float(row.get("energy_gate_slope_late_per100", "")) or 0.0)
    noise = to_float(row.get("noise_level", "")) or 0.0
    active = str(row.get("active_regime_flag", "")).strip().lower() == "true"

    if norm_status(row.get("gate_energy_drift", "")) == "fail":
        if e_noether < 0.25 * max(e_gate, 1e-12):
            return "gate_energy_vs_noether_mismatch"
        if active and noise >= 0.01:
            return "active_regime_energy_drift"
        if slope_late > 0.15:
            return "late_step_energy_runaway"
        return "energy_drift_other"
    return "non_energy_fail"


def main() -> int:
    args = parse_args()
    summary_path = Path(args.summary_csv).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not summary_path.exists():
        raise FileNotFoundError(f"summary csv missing: {summary_path}")

    rows = read_csv(summary_path)
    if not rows:
        raise RuntimeError("summary csv is empty")

    enriched: list[dict[str, Any]] = []
    for r in rows:
        fail_gates = [g for g in GATE_FIELDS if norm_status(r.get(g, "")) == "fail"]
        sig = "+".join(fail_gates) if fail_gates else "none"
        mech = classify_mechanism(r)
        rec = dict(r)
        rec["fail_gate_list"] = ",".join(fail_gates) if fail_gates else "none"
        rec["fail_gate_signature"] = sig
        rec["dominant_mechanism"] = mech
        rec["all_pass"] = norm_status(r.get("all_pass", ""))
        enriched.append(rec)

    fail_rows = [r for r in enriched if r["all_pass"] == "fail"]
    pass_rows = [r for r in enriched if r["all_pass"] == "pass"]

    core_fields = [
        "case_id",
        "dataset_id",
        "dt",
        "steps",
        "case_seed",
        "edge_prob",
        "chi_scale",
        "noise_level",
        "phi_shock",
        "energy_gate_slope_per100",
        "energy_gate_slope_early_per100",
        "energy_gate_slope_late_per100",
        "energy_noether_slope_per100",
        "energy_noether_slope_early_per100",
        "energy_noether_slope_late_per100",
        "delta_energy_rel",
        "energy_noether_rel",
        "max_abs_sigma_seen",
        "max_abs_chi_seen",
        "max_abs_phi_seen",
        "active_regime_flag",
        "active_ratio",
        "edge_changes",
        "neighbor_changes",
        "max_residual",
        "max_alpha_rel_drift",
        "metric_cond_max_seen",
        "fail_gate_list",
        "fail_gate_signature",
        "dominant_mechanism",
    ] + GATE_FIELDS + ["all_pass"]

    write_csv(out_dir / "fail_cases.csv", fail_rows, core_fields)
    write_csv(out_dir / "pass_cases.csv", pass_rows, core_fields)

    pattern_counter: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for r in fail_rows:
        key = (
            str(r.get("dataset_id", "")),
            str(r.get("fail_gate_signature", "")),
            str(r.get("dominant_mechanism", "")),
            str(r.get("active_regime_flag", "")),
        )
        pattern_counter[key] += 1

    pattern_rows: list[dict[str, Any]] = []
    for (dataset_id, signature, mechanism, active_flag), count in sorted(
        pattern_counter.items(), key=lambda kv: (-kv[1], kv[0])
    ):
        pattern_rows.append(
            {
                "dataset_id": dataset_id,
                "fail_gate_signature": signature,
                "dominant_mechanism": mechanism,
                "active_regime_flag": active_flag,
                "count": count,
            }
        )
    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        ["dataset_id", "fail_gate_signature", "dominant_mechanism", "active_regime_flag", "count"],
    )

    # Optional feature correlations: fail flag vs numeric fields.
    labels = [1.0 if r["all_pass"] == "fail" else 0.0 for r in enriched]
    numeric_fields: list[str] = []
    for k in enriched[0].keys():
        if k in {"case_id", "dataset_id", "fail_gate_list", "fail_gate_signature", "dominant_mechanism"}:
            continue
        if k.endswith("_status") or k.startswith("gate_"):
            continue
        if all(to_float(r.get(k, "")) is not None for r in enriched):
            numeric_fields.append(k)

    corr_rows: list[dict[str, Any]] = []
    for f in numeric_fields:
        vals = [to_float(r.get(f, "")) or 0.0 for r in enriched]
        corr = pearson(vals, labels)
        if corr is None:
            continue
        corr_rows.append({"feature": f, "corr_with_fail": f"{corr:.6f}", "abs_corr": f"{abs(corr):.6f}"})
    corr_rows.sort(key=lambda r: float(r["abs_corr"]), reverse=True)
    write_csv(out_dir / "feature_correlations.csv", corr_rows, ["feature", "corr_with_fail", "abs_corr"])

    mech_counts = Counter(r["dominant_mechanism"] for r in fail_rows)
    gate_counts = Counter()
    for r in fail_rows:
        for g in GATE_FIELDS:
            if norm_status(r.get(g, "")) == "fail":
                gate_counts[g] += 1

    top_mech = mech_counts.most_common(3)
    top_gates = gate_counts.most_common(3)
    generated = datetime.now(timezone.utc).isoformat()
    report_lines = [
        "# Stability Failure Taxonomy (v1)",
        "",
        f"- generated_utc: `{generated}`",
        f"- source_summary: `{summary_path.as_posix()}`",
        f"- total_profiles: `{len(enriched)}`",
        f"- fail_profiles: `{len(fail_rows)}`",
        f"- pass_profiles: `{len(pass_rows)}`",
        "",
        "## Dominant Failing Gates",
        "",
    ]
    if top_gates:
        for g, c in top_gates:
            report_lines.append(f"- `{g}`: `{c}`")
    else:
        report_lines.append("- none")

    report_lines.extend(
        [
            "",
            "## Dataset Sensitivity",
            "",
        ]
    )
    ds_counter = Counter(str(r.get("dataset_id", "")) for r in fail_rows)
    if ds_counter:
        for ds, c in ds_counter.most_common():
            report_lines.append(f"- `{ds}` fail count: `{c}`")
    else:
        report_lines.append("- no fail profiles")

    report_lines.extend(
        [
            "",
            "## Top 3 Hypothesized Mechanisms",
            "",
        ]
    )
    if top_mech:
        for mech, c in top_mech:
            report_lines.append(f"- `{mech}`: `{c}` fail cases")
    else:
        report_lines.append("- no fail profiles")

    (out_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    (out_dir / "run-log.txt").write_text(
        "\n".join(
            [
                "stability failure taxonomy v1",
                f"generated_utc={generated}",
                f"summary_csv={summary_path.as_posix()}",
                f"fail_profiles={len(fail_rows)}",
                f"pass_profiles={len(pass_rows)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"fail_cases_csv: {(out_dir / 'fail_cases.csv').as_posix()}")
    print(f"pass_cases_csv: {(out_dir / 'pass_cases.csv').as_posix()}")
    print(f"pattern_summary_csv: {(out_dir / 'pattern_summary.csv').as_posix()}")
    print(f"feature_correlations_csv: {(out_dir / 'feature_correlations.csv').as_posix()}")
    print(f"report_md: {(out_dir / 'report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
