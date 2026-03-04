#!/usr/bin/env python3
"""
Analyze QM Stage-1 official-v5 G17b failures and build a targeted taxonomy package.

Scope:
- uses frozen official-v5 summaries (primary/attack/holdout)
- inspects existing per-profile metric CSVs under run_root/g17,g18,g19
- outputs fail/pass tables, pattern summary, feature correlations, report
- no gate threshold/formula changes
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import datetime, timezone
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent.parent
ART = ROOT / "05_validation" / "evidence" / "artifacts"
DEFAULT_OUT_DIR = ART / "qm-stage1-g17b-failure-taxonomy-v1"
DEFAULT_SUMMARY_CSVS = [
    ART / "qm-stage1-official-v5" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-stage1-official-v5" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-stage1-official-v5" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze QM Stage-1 G17b failures from official-v5 summaries.")
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


def read_metrics(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    out: dict[str, dict[str, str]] = {}
    for r in rows:
        metric = str(r.get("metric", "")).strip()
        if metric:
            out[metric] = r
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def norm_status(v: str) -> str:
    return "pass" if (v or "").strip().lower() == "pass" else "fail"


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


def f6(v: float | None) -> str:
    if v is None:
        return ""
    return f"{v:.6f}"


def mean(xs: list[float]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


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


THRESH_RE = re.compile(r"^\s*([<>])\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$")


def parse_simple_threshold(expr: str) -> tuple[str, float] | None:
    m = THRESH_RE.match(str(expr or ""))
    if not m:
        return None
    cmp = m.group(1)
    thr = float(m.group(2))
    return cmp, thr


def threshold_margin(value: float | None, thr_expr: str) -> float | None:
    """
    Positive margin means fail-side distance (how far over the threshold boundary).
    Negative margin means pass-side slack.
    """
    if value is None:
        return None
    parsed = parse_simple_threshold(thr_expr)
    if parsed is None:
        return None
    cmp, thr = parsed
    if cmp == "<":
        return value - thr
    if cmp == ">":
        return thr - value
    return None


def bool_flag(v: str) -> int:
    return 1 if str(v or "").strip().lower() == "true" else 0


def classify_g17b_fail(r: dict[str, Any]) -> str:
    margin = to_float(r.get("g17b_margin_to_threshold", ""))
    coupled_g18 = r.get("g18_status") == "fail"
    coupled_g19 = r.get("g19_status") == "fail"
    coupled_g20 = r.get("g20_status") == "fail"
    coupled_sub = any(
        r.get(k) == "fail"
        for k in ("g17a_status_v2", "g17c_status", "g17d_status")
    )
    multi_peak = bool_flag(str(r.get("multi_peak_mixing", ""))) == 1

    if coupled_g18 and multi_peak:
        return "coupled_g18_multipeak"
    if coupled_g18:
        return "coupled_g18_non_multipeak"
    if coupled_g19:
        return "coupled_g19"
    if coupled_g20:
        return "coupled_g20"
    if coupled_sub:
        return "coupled_other_g17_subgate"
    if margin is None:
        return "isolated_margin_unknown"
    if margin <= 0.002:
        return "isolated_near_threshold"
    if margin <= 0.010:
        return "isolated_moderate_margin"
    return "isolated_high_margin"


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

    rows_all: list[dict[str, Any]] = []
    for p in summary_paths:
        block_id = p.parent.name
        rows = read_csv(p)
        for row in rows:
            ds = str(row.get("dataset_id", "")).strip()
            seed = int(str(row.get("seed", "0")))
            run_root = Path(str(row.get("run_root", "")).strip())
            if not run_root.is_absolute():
                run_root = (ROOT / run_root).resolve()

            g17_metrics = read_metrics(run_root / "g17" / "metric_checks_qm.csv")
            g18_metrics = read_metrics(run_root / "g18" / "metric_checks_qm_info.csv")
            g19_metrics = read_metrics(run_root / "g19" / "metric_checks_unruh.csv")

            g17b_row = g17_metrics.get("propagator_slope", {})
            g17a_row = g17_metrics.get("spectral_gap", {})
            g17c_row = g17_metrics.get("E0_per_mode", {})
            g17d_row = g17_metrics.get("heisenberg_dev", {})
            g18d_row = g18_metrics.get("spectral_dimension_ds", {})
            g19d_row = g19_metrics.get("dG_thermal_slope", {})

            g17b_val = to_float(g17b_row.get("value", ""))
            g17b_thr = str(g17b_row.get("threshold", ""))
            g17b_margin = threshold_margin(g17b_val, g17b_thr)

            rec: dict[str, Any] = {
                "block_id": block_id,
                "dataset_id": ds,
                "seed": seed,
                "run_root": run_root.as_posix(),
                "all_pass_qm_lane": norm_status(str(row.get("all_pass_qm_lane", ""))),
                "g17_status": norm_status(str(row.get("g17_status", ""))),
                "g18_status": norm_status(str(row.get("g18_status", ""))),
                "g19_status": norm_status(str(row.get("g19_status", ""))),
                "g20_status": norm_status(str(row.get("g20_status", ""))),
                "g17a_status_v2": norm_status(str(row.get("g17a_status_v2", ""))),
                "g17b_status": norm_status(str(row.get("g17b_status", ""))),
                "g17c_status": norm_status(str(row.get("g17c_status", ""))),
                "g17d_status": norm_status(str(row.get("g17d_status", ""))),
                "g18d_status_v2": norm_status(str(row.get("g18d_status_v2", ""))),
                "multi_peak_mixing": str(row.get("multi_peak_mixing", "")).strip().lower(),
                "g17a_spectral_gap": f6(to_float(g17a_row.get("value", ""))),
                "g17b_propagator_slope": f6(g17b_val),
                "g17b_threshold_expr": g17b_thr,
                "g17b_margin_to_threshold": f6(g17b_margin),
                "g17c_e0_per_mode": f6(to_float(g17c_row.get("value", ""))),
                "g17d_heisenberg_dev": f6(to_float(g17d_row.get("value", ""))),
                "g18d_spectral_dimension_ds": f6(to_float(g18d_row.get("value", ""))),
                "g19d_thermal_slope": f6(to_float(g19d_row.get("value", ""))),
            }
            if rec["g17b_status"] == "fail":
                rec["g17b_fail_class"] = classify_g17b_fail(rec)
            else:
                rec["g17b_fail_class"] = "none"
            rows_all.append(rec)

    rows_all.sort(key=lambda r: (str(r["dataset_id"]), int(r["seed"]), str(r["block_id"])))
    fail_cases = [r for r in rows_all if r["g17b_status"] == "fail"]
    pass_cases = [r for r in rows_all if r["g17b_status"] == "pass"]

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
        "g18d_status_v2",
        "multi_peak_mixing",
        "g17a_spectral_gap",
        "g17b_propagator_slope",
        "g17b_threshold_expr",
        "g17b_margin_to_threshold",
        "g17c_e0_per_mode",
        "g17d_heisenberg_dev",
        "g18d_spectral_dimension_ds",
        "g19d_thermal_slope",
        "g17b_fail_class",
        "run_root",
    ]
    write_csv(out_dir / "g17b_fail_cases.csv", fail_cases, case_fields)
    write_csv(out_dir / "g17b_pass_cases.csv", pass_cases, case_fields)

    pattern_rows: list[dict[str, Any]] = []
    blocks = sorted({str(r["block_id"]) for r in rows_all})
    datasets = sorted({str(r["dataset_id"]) for r in rows_all})

    for block in blocks + ["ALL"]:
        for ds in datasets + ["ALL"]:
            sub_all = rows_all
            sub_fail = fail_cases
            if block != "ALL":
                sub_all = [r for r in sub_all if str(r["block_id"]) == block]
                sub_fail = [r for r in sub_fail if str(r["block_id"]) == block]
            if ds != "ALL":
                sub_all = [r for r in sub_all if str(r["dataset_id"]) == ds]
                sub_fail = [r for r in sub_fail if str(r["dataset_id"]) == ds]
            total = len(sub_all)
            if total == 0:
                continue
            fail_n = len(sub_fail)
            pattern_rows.append(
                {
                    "block_id": block,
                    "dataset_id": ds,
                    "level": "overall",
                    "pattern": "g17b_fail_rate",
                    "count": fail_n,
                    "profiles_total": total,
                    "rate": f"{(fail_n / total):.6f}",
                }
            )

            class_counter = Counter(str(r["g17b_fail_class"]) for r in sub_fail)
            for klass, c in class_counter.most_common(args.top_k):
                pattern_rows.append(
                    {
                        "block_id": block,
                        "dataset_id": ds,
                        "level": "g17b_fail_class",
                        "pattern": klass,
                        "count": c,
                        "profiles_total": total,
                        "rate": f"{(c / total):.6f}",
                    }
                )

            coupled_sig_counter: Counter[str] = Counter()
            for r in sub_fail:
                sig_parts: list[str] = []
                for field in ("g17a_status_v2", "g17c_status", "g17d_status", "g18_status", "g19_status", "g20_status"):
                    if r.get(field) == "fail":
                        sig_parts.append(field)
                coupled_sig_counter["+".join(sig_parts) if sig_parts else "isolated_g17b"] += 1

            for sig, c in coupled_sig_counter.most_common(args.top_k):
                pattern_rows.append(
                    {
                        "block_id": block,
                        "dataset_id": ds,
                        "level": "coupled_signature",
                        "pattern": sig,
                        "count": c,
                        "profiles_total": total,
                        "rate": f"{(c / total):.6f}",
                    }
                )

    write_csv(
        out_dir / "pattern_summary.csv",
        pattern_rows,
        ["block_id", "dataset_id", "level", "pattern", "count", "profiles_total", "rate"],
    )

    feature_specs = [
        ("multi_peak_mixing_flag", lambda r: float(bool_flag(str(r.get("multi_peak_mixing", ""))))),
        ("g18_fail_flag", lambda r: 1.0 if r.get("g18_status") == "fail" else 0.0),
        ("g19_fail_flag", lambda r: 1.0 if r.get("g19_status") == "fail" else 0.0),
        ("g17a_fail_flag", lambda r: 1.0 if r.get("g17a_status_v2") == "fail" else 0.0),
        ("g17b_propagator_slope", lambda r: to_float(r.get("g17b_propagator_slope", ""))),
        ("g17b_margin_to_threshold", lambda r: to_float(r.get("g17b_margin_to_threshold", ""))),
        ("g17a_spectral_gap", lambda r: to_float(r.get("g17a_spectral_gap", ""))),
        ("g18d_spectral_dimension_ds", lambda r: to_float(r.get("g18d_spectral_dimension_ds", ""))),
        ("g19d_thermal_slope", lambda r: to_float(r.get("g19d_thermal_slope", ""))),
    ]
    corr_rows: list[dict[str, Any]] = []
    y = [1.0 if r["g17b_status"] == "fail" else 0.0 for r in rows_all]
    for name, getter in feature_specs:
        xs: list[float] = []
        ys: list[float] = []
        fail_vals: list[float] = []
        pass_vals: list[float] = []
        for i, r in enumerate(rows_all):
            xv = getter(r)
            if xv is None:
                continue
            x = float(xv)
            yi = y[i]
            xs.append(x)
            ys.append(yi)
            if yi > 0.5:
                fail_vals.append(x)
            else:
                pass_vals.append(x)
        corr_rows.append(
            {
                "feature": name,
                "n": len(xs),
                "n_fail": len(fail_vals),
                "n_pass": len(pass_vals),
                "mean_fail": f6(mean(fail_vals)),
                "mean_pass": f6(mean(pass_vals)),
                "delta_fail_minus_pass": f6(
                    (mean(fail_vals) - mean(pass_vals))
                    if mean(fail_vals) is not None and mean(pass_vals) is not None
                    else None
                ),
                "pearson_with_g17b_fail": f6(pearson(xs, ys)),
            }
        )
    corr_rows.sort(
        key=lambda r: abs(float(r["pearson_with_g17b_fail"])) if str(r["pearson_with_g17b_fail"]).strip() else 0.0,
        reverse=True,
    )
    write_csv(
        out_dir / "feature_correlations.csv",
        corr_rows,
        [
            "feature",
            "n",
            "n_fail",
            "n_pass",
            "mean_fail",
            "mean_pass",
            "delta_fail_minus_pass",
            "pearson_with_g17b_fail",
        ],
    )

    total = len(rows_all)
    fail_total = len(fail_cases)
    pass_total = len(pass_cases)
    class_counter_all = Counter(str(r["g17b_fail_class"]) for r in fail_cases)
    top_classes = class_counter_all.most_common(3)

    ds_lines: list[str] = []
    for ds in datasets:
        all_ds = [r for r in rows_all if str(r["dataset_id"]) == ds]
        fail_ds = [r for r in fail_cases if str(r["dataset_id"]) == ds]
        ds_lines.append(f"- `{ds}`: `{len(fail_ds)}/{len(all_ds)}` fail (`{(len(fail_ds) / len(all_ds)):.6f}`)")

    top_corr = corr_rows[0] if corr_rows else None
    top_corr_line = (
        f"- strongest feature correlation: `{top_corr['feature']}` (`r={top_corr['pearson_with_g17b_fail']}`)"
        if top_corr
        else "- strongest feature correlation: `n/a`"
    )

    lines: list[str] = []
    lines.append("# QM Stage-1 G17b Failure Taxonomy (v1)")
    lines.append("")
    lines.append(f"- generated_utc: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append(f"- profiles_total: `{total}`")
    lines.append(f"- g17b_fail_profiles: `{fail_total}`")
    lines.append(f"- g17b_pass_profiles: `{pass_total}`")
    lines.append(f"- g17b_fail_rate: `{(fail_total / total):.6f}`")
    lines.append("")
    lines.append("## Dataset Sensitivity")
    lines.append("")
    lines.extend(ds_lines if ds_lines else ["- none"])
    lines.append("")
    lines.append("## Dominant G17b Fail Classes")
    lines.append("")
    for klass, c in top_classes:
        lines.append(f"- `{klass}`: `{c}`")
    if not top_classes:
        lines.append("- none")
    lines.append("")
    coupled_n = sum(
        1
        for r in fail_cases
        if (
            r.get("g18_status") == "fail"
            or r.get("g19_status") == "fail"
            or r.get("g20_status") == "fail"
            or r.get("g17a_status_v2") == "fail"
            or r.get("g17c_status") == "fail"
            or r.get("g17d_status") == "fail"
        )
    )
    near_n = class_counter_all.get("isolated_near_threshold", 0)

    lines.append("## Top 3 Hypothesized Mechanisms (No Gate Changes Applied)")
    lines.append("")
    if coupled_n == 0:
        lines.append("- Coupled regime mechanism: no coupled gate co-fail was observed for G17b fail profiles in this snapshot.")
    elif coupled_n <= max(1, int(0.10 * fail_total)):
        lines.append(
            f"- Coupled regime mechanism: coupled co-fails are a minority (`{coupled_n}/{fail_total}`), indicating G17b fragility is mostly isolated."
        )
    else:
        lines.append(
            f"- Coupled regime mechanism: coupled co-fails are substantial (`{coupled_n}/{fail_total}`), indicating cross-gate stress contributes materially."
        )
    lines.append(
        f"- Near-threshold mechanism: isolated near-threshold cases dominate (`{near_n}/{fail_total}`), indicating slope-estimator sensitivity near the fixed boundary."
    )
    lines.append(top_corr_line)
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("- official summary csvs:")
    for p in summary_paths:
        lines.append(f"  - `{p.as_posix()}`")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("- `g17b_fail_cases.csv`")
    lines.append("- `g17b_pass_cases.csv`")
    lines.append("- `pattern_summary.csv`")
    lines.append("- `feature_correlations.csv`")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"g17b_fail_cases:      {out_dir / 'g17b_fail_cases.csv'}")
    print(f"g17b_pass_cases:      {out_dir / 'g17b_pass_cases.csv'}")
    print(f"pattern_summary:      {out_dir / 'pattern_summary.csv'}")
    print(f"feature_correlations: {out_dir / 'feature_correlations.csv'}")
    print(f"report_md:            {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
