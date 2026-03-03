#!/usr/bin/env python3
"""
Analyze QM Stage-1 post-switch failures and build a taxonomy package.

Scope:
- uses existing official-v2 summary artifacts (primary/attack/holdout)
- emits fail/pass case tables, pattern summaries, optional feature correlations
- no gate threshold/formula changes
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_OUT = ART / "qm-stage1-failure-taxonomy-v1"

DEFAULT_SUMMARY_CSVS = [
    ART / "qm-stage1-official-v2" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-stage1-official-v2" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-stage1-official-v2" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]
DEFAULT_METRICS_SUMMARY_CSVS = [
    ART / "qm-g17-candidate-v2" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-g17-candidate-v2" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-g17-candidate-v2" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]
DEFAULT_PROMOTION_REPORT_JSONS = [
    ART / "qm-g17-promotion-eval-v1" / "primary_ds002_003_006_s3401_3600" / "report.json",
    ART / "qm-g17-promotion-eval-v1" / "attack_seed500_ds002_003_006_s3601_4100" / "report.json",
    ART / "qm-g17-promotion-eval-v1" / "attack_holdout_ds004_008_s3401_3600" / "report.json",
]

GATE_FIELDS = ["g17_status", "g18_status", "g19_status", "g20_status"]
SUBGATE_FIELDS = ["g17a_status_v2", "g17b_status", "g17c_status", "g17d_status"]


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze QM Stage-1 failures and build taxonomy outputs.")
    p.add_argument("--summary-csvs", default=",".join(str(p) for p in DEFAULT_SUMMARY_CSVS))
    p.add_argument("--metrics-summary-csvs", default=",".join(str(p) for p in DEFAULT_METRICS_SUMMARY_CSVS))
    p.add_argument("--promotion-report-jsons", default=",".join(str(p) for p in DEFAULT_PROMOTION_REPORT_JSONS))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=10)
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


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


def to_float(v: Any) -> float | None:
    txt = str(v or "").strip().lower()
    if txt == "":
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


def detect_numeric_fields(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    excluded = {"dataset_id", "seed", "run_root"}
    out: list[str] = []
    cols = list(rows[0].keys())
    for col in cols:
        if col in excluded:
            continue
        if "_status" in col:
            continue
        if col.startswith("all_pass_qm_lane"):
            continue
        has_num = False
        for r in rows:
            if to_float(r.get(col, "")) is not None:
                has_num = True
                break
        if has_num:
            out.append(col)
    return out


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


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


def load_promotion_reports(paths: list[Path]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in paths:
        if not p.exists():
            continue
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        out.append(
            {
                "path": p.as_posix(),
                "eval_id": payload.get("eval_id", ""),
                "overall_decision": payload.get("overall_decision", ""),
                "datasets": payload.get("datasets", []),
            }
        )
    return out


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_paths = [Path(x).resolve() for x in parse_csv_list(args.summary_csvs)]
    if not summary_paths:
        raise RuntimeError("no summary csv paths provided")
    for p in summary_paths:
        if not p.exists():
            raise FileNotFoundError(f"summary missing: {p}")

    metric_paths = [Path(x).resolve() for x in parse_csv_list(args.metrics_summary_csvs)]
    promo_paths = [Path(x).resolve() for x in parse_csv_list(args.promotion_report_jsons)]
    promotion_snapshots = load_promotion_reports(promo_paths)

    combined: list[dict[str, Any]] = []
    for p in summary_paths:
        block_id = p.parent.name
        rows = read_csv(p)
        for r in rows:
            ds = str(r.get("dataset_id", "")).strip()
            seed = int(str(r.get("seed", "0")))
            fail_gates = [g for g in GATE_FIELDS if norm_status(str(r.get(g, ""))) == "fail"]
            fail_subgates = [g for g in SUBGATE_FIELDS if norm_status(str(r.get(g, ""))) == "fail"]
            rec: dict[str, Any] = {
                "block_id": block_id,
                "dataset_id": ds,
                "seed": seed,
                "run_root": str(r.get("run_root", "")),
                "all_pass_qm_lane": norm_status(str(r.get("all_pass_qm_lane", ""))),
                "g17_status": norm_status(str(r.get("g17_status", ""))),
                "g18_status": norm_status(str(r.get("g18_status", ""))),
                "g19_status": norm_status(str(r.get("g19_status", ""))),
                "g20_status": norm_status(str(r.get("g20_status", ""))),
                "g17a_status_v2": norm_status(str(r.get("g17a_status_v2", ""))),
                "g17b_status": norm_status(str(r.get("g17b_status", ""))),
                "g17c_status": norm_status(str(r.get("g17c_status", ""))),
                "g17d_status": norm_status(str(r.get("g17d_status", ""))),
                "multi_peak_mixing": str(r.get("multi_peak_mixing", "")),
                "fail_gate_list": ",".join(fail_gates) if fail_gates else "none",
                "fail_subgate_list": ",".join(fail_subgates) if fail_subgates else "none",
                "fail_gate_signature": "+".join(fail_gates) if fail_gates else "none",
                "fail_subgate_signature": "+".join(fail_subgates) if fail_subgates else "none",
            }
            combined.append(rec)

    combined.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"]), str(r["block_id"])))
    if not combined:
        raise RuntimeError("combined summary rows are empty")

    fail_cases = [r for r in combined if r["all_pass_qm_lane"] == "fail"]
    pass_cases = [r for r in combined if r["all_pass_qm_lane"] == "pass"]

    case_fields = [
        "block_id",
        "dataset_id",
        "seed",
        "all_pass_qm_lane",
        "g17_status",
        "g18_status",
        "g19_status",
        "g20_status",
        "g17a_status_v2",
        "g17b_status",
        "g17c_status",
        "g17d_status",
        "multi_peak_mixing",
        "fail_gate_list",
        "fail_subgate_list",
        "fail_gate_signature",
        "fail_subgate_signature",
        "run_root",
    ]
    write_csv(out_dir / "qm_fail_cases.csv", fail_cases, case_fields)
    write_csv(out_dir / "qm_pass_cases.csv", pass_cases, case_fields)

    pattern_rows: list[dict[str, Any]] = []
    datasets = sorted({str(r["dataset_id"]) for r in combined})
    datasets_all = datasets + ["ALL"]
    for ds in datasets_all:
        sub = fail_cases if ds == "ALL" else [r for r in fail_cases if str(r["dataset_id"]) == ds]
        total_ds = len(combined) if ds == "ALL" else sum(1 for r in combined if str(r["dataset_id"]) == ds)
        fail_ds = len(sub)
        for field in GATE_FIELDS:
            count = sum(1 for r in sub if r[field] == "fail")
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "level": "gate",
                    "pattern": field,
                    "count": count,
                    "profiles_total": total_ds,
                    "profiles_fail": fail_ds,
                    "rate_within_fail": (count / fail_ds) if fail_ds else 0.0,
                    "rate_within_total": (count / total_ds) if total_ds else 0.0,
                }
            )
        for field in SUBGATE_FIELDS:
            count = sum(1 for r in sub if r[field] == "fail")
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "level": "subgate",
                    "pattern": field,
                    "count": count,
                    "profiles_total": total_ds,
                    "profiles_fail": fail_ds,
                    "rate_within_fail": (count / fail_ds) if fail_ds else 0.0,
                    "rate_within_total": (count / total_ds) if total_ds else 0.0,
                }
            )
        gate_sig = Counter(str(r["fail_gate_signature"]) for r in sub)
        for sig, count in gate_sig.items():
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "level": "gate_signature",
                    "pattern": sig,
                    "count": count,
                    "profiles_total": total_ds,
                    "profiles_fail": fail_ds,
                    "rate_within_fail": (count / fail_ds) if fail_ds else 0.0,
                    "rate_within_total": (count / total_ds) if total_ds else 0.0,
                }
            )
        sub_sig = Counter(str(r["fail_subgate_signature"]) for r in sub)
        for sig, count in sub_sig.items():
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "level": "subgate_signature",
                    "pattern": sig,
                    "count": count,
                    "profiles_total": total_ds,
                    "profiles_fail": fail_ds,
                    "rate_within_fail": (count / fail_ds) if fail_ds else 0.0,
                    "rate_within_total": (count / total_ds) if total_ds else 0.0,
                }
            )

    pattern_rows.sort(key=lambda r: (str(r["dataset_id"]), str(r["level"]), -int(r["count"]), str(r["pattern"])))
    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        [
            "dataset_id",
            "level",
            "pattern",
            "count",
            "profiles_total",
            "profiles_fail",
            "rate_within_fail",
            "rate_within_total",
        ],
    )

    metrics_rows: list[dict[str, str]] = []
    for p in metric_paths:
        if p.exists():
            metrics_rows.extend(read_csv(p))

    feature_rows: list[dict[str, Any]] = []
    if metrics_rows:
        m_fields = detect_numeric_fields(metrics_rows)
        m_map: dict[str, dict[str, str]] = {}
        for r in metrics_rows:
            try:
                k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
            except Exception:
                continue
            m_map[k] = r

        for ds in ["ALL"] + datasets:
            rows_ds = combined if ds == "ALL" else [r for r in combined if str(r["dataset_id"]) == ds]
            for field in m_fields:
                vals: list[float] = []
                ys: list[float] = []
                fail_vals: list[float] = []
                pass_vals: list[float] = []
                for r in rows_ds:
                    k = key_of(str(r["dataset_id"]), int(r["seed"]))
                    mr = m_map.get(k)
                    if mr is None:
                        continue
                    x = to_float(mr.get(field, ""))
                    if x is None:
                        continue
                    y = 1.0 if r["all_pass_qm_lane"] == "fail" else 0.0
                    vals.append(x)
                    ys.append(y)
                    if y > 0.5:
                        fail_vals.append(x)
                    else:
                        pass_vals.append(x)
                if not vals:
                    continue
                m_fail = mean(fail_vals)
                m_pass = mean(pass_vals)
                feature_rows.append(
                    {
                        "dataset_id": ds,
                        "feature": field,
                        "n": len(vals),
                        "n_fail": len(fail_vals),
                        "n_pass": len(pass_vals),
                        "mean_fail": f6(m_fail),
                        "mean_pass": f6(m_pass),
                        "delta_fail_minus_pass": f6((m_fail - m_pass) if m_fail is not None and m_pass is not None else None),
                        "pearson_fail_corr": f6(pearson(vals, ys)),
                    }
                )

    feature_rows.sort(
        key=lambda r: (
            str(r["dataset_id"]),
            -abs(float(r["pearson_fail_corr"])) if str(r.get("pearson_fail_corr", "")).strip() else 0.0,
            str(r["feature"]),
        )
    )
    write_csv(
        out_dir / "feature_correlations.csv",
        feature_rows,
        [
            "dataset_id",
            "feature",
            "n",
            "n_fail",
            "n_pass",
            "mean_fail",
            "mean_pass",
            "delta_fail_minus_pass",
            "pearson_fail_corr",
        ],
    )

    total = len(combined)
    total_fail = len(fail_cases)
    total_pass = len(pass_cases)

    per_dataset_rows: list[dict[str, Any]] = []
    for ds in datasets:
        all_ds = [r for r in combined if str(r["dataset_id"]) == ds]
        fail_ds = [r for r in all_ds if r["all_pass_qm_lane"] == "fail"]
        per_dataset_rows.append(
            {
                "dataset_id": ds,
                "n_total": len(all_ds),
                "n_fail": len(fail_ds),
                "fail_rate": (len(fail_ds) / len(all_ds)) if all_ds else 0.0,
            }
        )
    per_dataset_rows.sort(key=lambda r: float(r["fail_rate"]), reverse=True)
    most_sensitive_ds = per_dataset_rows[0]["dataset_id"] if per_dataset_rows else "n/a"

    gate_counter = Counter()
    subgate_counter = Counter()
    for r in fail_cases:
        for g in GATE_FIELDS:
            if r[g] == "fail":
                gate_counter[g] += 1
        for g in SUBGATE_FIELDS:
            if r[g] == "fail":
                subgate_counter[g] += 1

    dominant_gates = gate_counter.most_common(max(1, args.top_k))
    dominant_subgates = subgate_counter.most_common(max(1, args.top_k))
    top_gate = dominant_gates[0][0] if dominant_gates else "none"
    top_subgate = dominant_subgates[0][0] if dominant_subgates else "none"

    g20_fail = gate_counter.get("g20_status", 0)
    top_corr_row = next((r for r in feature_rows if r["dataset_id"] == "ALL" and str(r["pearson_fail_corr"]).strip()), None)
    top_corr_feature = str(top_corr_row["feature"]) if top_corr_row else "n/a"
    top_corr_value = str(top_corr_row["pearson_fail_corr"]) if top_corr_row else ""

    hypotheses = [
        (
            f"Gate-dominant mechanism: `{top_gate}` is the dominant failing gate, suggesting "
            "lane failures are currently driven by that diagnostic family rather than a balanced multi-gate collapse."
        ),
        (
            f"Dataset sensitivity mechanism: `{most_sensitive_ds}` shows the highest fail-rate, "
            "indicating topology/regime-specific sensitivity in the QM lane under the frozen Stage-1 policy."
        ),
        (
            "Coupling stability mechanism: `G20` remains stable (no G20 fails in lane-fail profiles), "
            "so post-switch failures are concentrated upstream (mostly G17/G18/G19 diagnostics) instead of semiclassical closure."
            if g20_fail == 0
            else "Coupling sensitivity mechanism: non-zero G20 fails indicate part of lane failures are tied to semiclassical backreaction stability."
        ),
    ]
    if top_corr_feature != "n/a":
        hypotheses[1] = (
            f"Feature-linked mechanism: `{top_corr_feature}` shows the strongest fail-correlation (`r={top_corr_value}`), "
            "suggesting residual Stage-1 failures cluster around specific geometric/spectral regimes."
        )

    lines = [
        "# QM Stage-1 Failure Taxonomy (v1)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- profiles_total: `{total}`",
        f"- profiles_fail: `{total_fail}`",
        f"- profiles_pass: `{total_pass}`",
        f"- fail_rate: `{(total_fail / total):.6f}`" if total else "- fail_rate: `0.000000`",
        "",
        "## Dominant Failing Gates",
        "",
    ]
    for gate, c in dominant_gates[: args.top_k]:
        lines.append(f"- `{gate}`: `{c}` fail occurrences across fail-cases")
    lines.extend(["", "## Dominant Failing Subgates", ""])
    for gate, c in dominant_subgates[: args.top_k]:
        lines.append(f"- `{gate}`: `{c}` fail occurrences across fail-cases")

    lines.extend(["", "## Dataset Sensitivity", ""])
    for row in per_dataset_rows:
        lines.append(
            f"- `{row['dataset_id']}`: `{row['n_fail']}/{row['n_total']}` fail (`{float(row['fail_rate']):.6f}`)"
        )

    lines.extend(["", "## Top 3 Hypothesized Mechanisms (No Changes Applied)", ""])
    for h in hypotheses[:3]:
        lines.append(f"- {h}")

    lines.extend(
        [
            "",
            "## Inputs",
            "",
            "- official summaries:",
        ]
    )
    for p in summary_paths:
        lines.append(f"  - `{p.as_posix()}`")
    lines.append("- promotion reports:")
    for p in promo_paths:
        lines.append(f"  - `{p.as_posix()}`")

    lines.extend(["", "## Promotion Eval Snapshots", ""])
    if promotion_snapshots:
        for snap in promotion_snapshots:
            lines.append(
                f"- `{snap['eval_id']}`: decision=`{snap['overall_decision']}` datasets=`{','.join(str(x) for x in snap['datasets'])}`"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `qm_fail_cases.csv`",
            "- `qm_pass_cases.csv`",
            "- `pattern_summary.csv`",
            "- `feature_correlations.csv`",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"qm_fail_cases:        {out_dir / 'qm_fail_cases.csv'}")
    print(f"qm_pass_cases:        {out_dir / 'qm_pass_cases.csv'}")
    print(f"pattern_summary:      {out_dir / 'pattern_summary.csv'}")
    print(f"feature_correlations: {out_dir / 'feature_correlations.csv'}")
    print(f"report_md:            {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
