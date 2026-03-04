#!/usr/bin/env python3
"""
Analyze QM Stage-2 prereg failures and build a strict taxonomy package.

Scope:
- reads existing per-profile qm_lane summary.csv files
- emits fail/pass tables and pattern summaries
- no threshold/formula changes
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_OUT_DIR = ART / "qm-stage2-failure-taxonomy-v1"
DEFAULT_SUMMARY_CSVS = [
    ART / "qm-stage2-prereg-v1" / "primary_ds002_003_006_s3401_3600" / "qm_lane" / "summary.csv",
    ART / "qm-stage2-prereg-v1" / "attack_ds002_003_006_s3601_4100" / "qm_lane" / "summary.csv",
    ART / "qm-stage2-prereg-v1" / "holdout_ds004_008_s3401_3600" / "qm_lane" / "summary.csv",
]

GATE_FIELDS = ["g17_status", "g18_status", "g19_status", "g20_status"]
RC_FIELDS = ["g17_rc", "g18_rc", "g19_rc", "g20_rc", "rc_fail_count"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze QM Stage-2 failures from qm_lane summaries.")
    p.add_argument("--summary-csvs", default=",".join(str(p) for p in DEFAULT_SUMMARY_CSVS))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    p.add_argument("--top-k", type=int, default=10)
    return p.parse_args()


def parse_csv_list(text: str) -> list[Path]:
    out: list[Path] = []
    for tok in text.split(","):
        token = tok.strip()
        if token:
            out.append(Path(token).resolve())
    return out


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def to_int(v: Any) -> int:
    try:
        return int(str(v))
    except Exception:
        return 0


def to_float(v: Any) -> float | None:
    text = str(v or "").strip()
    if not text:
        return None
    try:
        out = float(text)
    except Exception:
        return None
    if math.isnan(out) or math.isinf(out):
        return None
    return out


def pearson(xs: list[float], ys: list[float]) -> float | None:
    n = min(len(xs), len(ys))
    if n < 3:
        return None
    x = xs[:n]
    y = ys[:n]
    mx = sum(x) / n
    my = sum(y) / n
    sxx = sum((v - mx) * (v - mx) for v in x)
    syy = sum((v - my) * (v - my) for v in y)
    if sxx <= 1e-18 or syy <= 1e-18:
        return None
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    return sxy / math.sqrt(sxx * syy)


def f6(v: float | None) -> str:
    if v is None:
        return ""
    return f"{v:.6f}"


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_paths = parse_csv_list(args.summary_csvs)
    if not summary_paths:
        raise RuntimeError("no summary paths provided")
    for p in summary_paths:
        if not p.exists():
            raise FileNotFoundError(f"missing summary: {p}")

    combined: list[dict[str, Any]] = []
    for p in summary_paths:
        block_id = p.parent.parent.name
        rows = read_csv(p)
        for r in rows:
            ds = str(r.get("dataset_id", "")).strip()
            seed = to_int(r.get("seed", 0))
            fail_gates = [g for g in GATE_FIELDS if norm_status(str(r.get(g, ""))) == "fail"]
            rec: dict[str, Any] = {
                "block_id": block_id,
                "dataset_id": ds,
                "seed": seed,
                "mode": str(r.get("mode", "")),
                "all_pass_qm_lane": norm_status(str(r.get("all_pass_qm_lane", ""))),
                "g17_status": norm_status(str(r.get("g17_status", ""))),
                "g18_status": norm_status(str(r.get("g18_status", ""))),
                "g19_status": norm_status(str(r.get("g19_status", ""))),
                "g20_status": norm_status(str(r.get("g20_status", ""))),
                "g17_rc": to_int(r.get("g17_rc", 0)),
                "g18_rc": to_int(r.get("g18_rc", 0)),
                "g19_rc": to_int(r.get("g19_rc", 0)),
                "g20_rc": to_int(r.get("g20_rc", 0)),
                "rc_fail_count": to_int(r.get("rc_fail_count", 0)),
                "runner_rc": to_int(r.get("runner_rc", 0)),
                "fail_gate_list": ",".join(fail_gates) if fail_gates else "none",
                "fail_gate_signature": "+".join(fail_gates) if fail_gates else "none",
                "run_root": str(r.get("run_root", "")),
            }
            combined.append(rec)

    if not combined:
        raise RuntimeError("combined rows are empty")
    combined.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"]), str(r["block_id"])))

    fail_cases = [r for r in combined if r["all_pass_qm_lane"] == "fail"]
    pass_cases = [r for r in combined if r["all_pass_qm_lane"] == "pass"]

    case_fields = [
        "block_id",
        "dataset_id",
        "seed",
        "mode",
        "all_pass_qm_lane",
        "g17_status",
        "g18_status",
        "g19_status",
        "g20_status",
        "g17_rc",
        "g18_rc",
        "g19_rc",
        "g20_rc",
        "rc_fail_count",
        "runner_rc",
        "fail_gate_list",
        "fail_gate_signature",
        "run_root",
    ]
    write_csv(out_dir / "qm_fail_cases.csv", fail_cases, case_fields)
    write_csv(out_dir / "qm_pass_cases.csv", pass_cases, case_fields)

    # Pattern summary by block/dataset/gate/signature.
    pattern_rows: list[dict[str, Any]] = []
    blocks = sorted({str(r["block_id"]) for r in combined})
    datasets = sorted({str(r["dataset_id"]) for r in combined})

    for block in blocks + ["ALL"]:
        for ds in datasets + ["ALL"]:
            subset = fail_cases
            total_subset = combined
            if block != "ALL":
                subset = [r for r in subset if str(r["block_id"]) == block]
                total_subset = [r for r in total_subset if str(r["block_id"]) == block]
            if ds != "ALL":
                subset = [r for r in subset if str(r["dataset_id"]) == ds]
                total_subset = [r for r in total_subset if str(r["dataset_id"]) == ds]

            total_n = len(total_subset)
            fail_n = len(subset)
            if total_n == 0:
                continue

            pattern_rows.append(
                {
                    "block_id": block,
                    "dataset_id": ds,
                    "level": "overall",
                    "pattern": "all_pass_qm_lane_fail",
                    "count": fail_n,
                    "profiles_total": total_n,
                    "rate": f"{(fail_n / total_n):.6f}",
                }
            )
            for gate in GATE_FIELDS:
                c = sum(1 for r in subset if r[gate] == "fail")
                pattern_rows.append(
                    {
                        "block_id": block,
                        "dataset_id": ds,
                        "level": "gate",
                        "pattern": gate,
                        "count": c,
                        "profiles_total": total_n,
                        "rate": f"{(c / total_n):.6f}",
                    }
                )

            sig_counter: Counter[str] = Counter(str(r["fail_gate_signature"]) for r in subset)
            for sig, c in sig_counter.most_common(args.top_k):
                pattern_rows.append(
                    {
                        "block_id": block,
                        "dataset_id": ds,
                        "level": "signature",
                        "pattern": sig,
                        "count": c,
                        "profiles_total": total_n,
                        "rate": f"{(c / total_n):.6f}",
                    }
                )

    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        ["block_id", "dataset_id", "level", "pattern", "count", "profiles_total", "rate"],
    )

    # Optional feature correlations with fail label.
    y = [1.0 if r["all_pass_qm_lane"] == "fail" else 0.0 for r in combined]
    corr_rows: list[dict[str, Any]] = []
    for col in RC_FIELDS:
        xs: list[float] = []
        ys: list[float] = []
        for i, r in enumerate(combined):
            fv = to_float(r.get(col, ""))
            if fv is None:
                continue
            xs.append(fv)
            ys.append(y[i])
        corr_rows.append(
            {
                "field": col,
                "n": len(xs),
                "pearson_with_fail_label": f6(pearson(xs, ys)),
            }
        )
    write_csv(out_dir / "feature_correlations.csv", corr_rows, ["field", "n", "pearson_with_fail_label"])

    # Report
    total = len(combined)
    fail_total = len(fail_cases)
    pass_total = len(pass_cases)
    gate_counter: Counter[str] = Counter()
    for r in fail_cases:
        for g in GATE_FIELDS:
            if r[g] == "fail":
                gate_counter[g] += 1
    top_gate = gate_counter.most_common(1)[0][0] if gate_counter else "none"

    ds_rows: list[str] = []
    for ds in datasets:
        ds_total = sum(1 for r in combined if str(r["dataset_id"]) == ds)
        ds_fail = sum(1 for r in fail_cases if str(r["dataset_id"]) == ds)
        ds_rows.append(f"- `{ds}`: fail `{ds_fail}/{ds_total}`")

    block_rows: list[str] = []
    for b in blocks:
        b_total = sum(1 for r in combined if str(r["block_id"]) == b)
        b_fail = sum(1 for r in fail_cases if str(r["block_id"]) == b)
        block_rows.append(f"- `{b}`: fail `{b_fail}/{b_total}`")

    sig_counter_all: Counter[str] = Counter(str(r["fail_gate_signature"]) for r in fail_cases)
    top_sigs = sig_counter_all.most_common(3)

    lines: list[str] = []
    lines.append("# QM Stage-2 Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- profiles_total: `{total}`")
    lines.append(f"- fail_profiles: `{fail_total}`")
    lines.append(f"- pass_profiles: `{pass_total}`")
    lines.append(f"- fail_rate: `{(fail_total / total):.6f}`")
    lines.append(f"- dominant_failing_gate: `{top_gate}`")
    lines.append("")
    lines.append("## Fail Rate by Block")
    lines.append("")
    lines.extend(block_rows if block_rows else ["- none"])
    lines.append("")
    lines.append("## Dataset Sensitivity")
    lines.append("")
    lines.extend(ds_rows if ds_rows else ["- none"])
    lines.append("")
    lines.append("## Top Fail Signatures")
    lines.append("")
    for sig, c in top_sigs:
        lines.append(f"- `{sig}`: `{c}`")
    if not top_sigs:
        lines.append("- none")
    lines.append("")
    lines.append("## Top 3 Hypothesized Mechanisms (diagnostic only)")
    lines.append("")
    lines.append(f"- Dominant gate `{top_gate}` drives most lane fails in current Stage-2 prereg range.")
    lines.append("- Joint signatures (e.g. `g17_status+g18_status`) suggest coupled fragility in hard regimes.")
    lines.append("- RC concentration indicates estimator sensitivity rather than coupling (G20) instability.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Tooling only; no gate threshold or formula changes.")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"qm_fail_cases:        {out_dir / 'qm_fail_cases.csv'}")
    print(f"qm_pass_cases:        {out_dir / 'qm_pass_cases.csv'}")
    print(f"pattern_summary:      {out_dir / 'pattern_summary.csv'}")
    print(f"feature_correlations: {out_dir / 'feature_correlations.csv'}")
    print(f"report_md:            {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

