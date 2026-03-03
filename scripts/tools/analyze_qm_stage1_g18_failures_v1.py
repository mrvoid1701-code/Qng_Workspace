#!/usr/bin/env python3
"""
Analyze QM Stage-1 G18 failures (post G17-v2 official) and build taxonomy outputs.

Housekeeping scope:
- reads frozen official summaries + existing run artifacts
- emits diagnostic CSV/report only
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
DEFAULT_OUT = ART / "qm-stage1-g18-failure-taxonomy-v1"

DEFAULT_OFFICIAL_SUMMARIES = [
    ART / "qm-stage1-official-v2" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-stage1-official-v2" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-stage1-official-v2" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]
DEFAULT_CANDIDATE_SUMMARIES = [
    ART / "qm-g17-candidate-v2" / "primary_ds002_003_006_s3401_3600" / "summary.csv",
    ART / "qm-g17-candidate-v2" / "attack_seed500_ds002_003_006_s3601_4100" / "summary.csv",
    ART / "qm-g17-candidate-v2" / "attack_holdout_ds004_008_s3401_3600" / "summary.csv",
]

G18_SUBGATES = ["g18a_status", "g18b_status", "g18c_status", "g18d_status"]


def parse_csv_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze QM Stage-1 G18 failures.")
    p.add_argument("--official-summary-csvs", default=",".join(str(p) for p in DEFAULT_OFFICIAL_SUMMARIES))
    p.add_argument("--candidate-summary-csvs", default=",".join(str(p) for p in DEFAULT_CANDIDATE_SUMMARIES))
    p.add_argument("--out-dir", default=str(DEFAULT_OUT))
    p.add_argument("--top-k", type=int, default=10)
    p.add_argument("--degenerate-peak-ratio-thr", type=float, default=0.995)
    p.add_argument("--degenerate-peak-dist-thr", type=float, default=0.060)
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


def to_float(v: Any) -> float | None:
    txt = str(v or "").strip().lower()
    if txt == "":
        return None
    if txt in {"true", "false"}:
        return 1.0 if txt == "true" else 0.0
    try:
        x = float(txt)
    except Exception:
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return x


def f6(v: float | None) -> str:
    if v is None:
        return ""
    return f"{v:.6f}"


def key_of(dataset_id: str, seed: int) -> str:
    return f"{dataset_id.upper()}::{seed}"


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    xs = sorted(values)
    pos = max(0.0, min(1.0, q)) * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    w = pos - lo
    return xs[lo] * (1.0 - w) + xs[hi] * w


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


def parse_metric_checks(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "g18a_status": "fail",
        "g18b_status": "fail",
        "g18c_status": "fail",
        "g18d_status": "fail",
        "g18a_value": None,
        "g18b_value": None,
        "g18c_value": None,
        "g18d_value": None,
        "g18a_threshold": "",
        "g18b_threshold": "",
        "g18c_threshold": "",
        "g18d_threshold": "",
        "g18_final_status_metric": "fail",
    }
    if not path.exists():
        return out
    rows = read_csv(path)
    by_id: dict[str, dict[str, str]] = {}
    for r in rows:
        gid = str(r.get("gate_id", "")).strip().upper()
        if gid:
            by_id[gid] = r
    for k in ["G18A", "G18B", "G18C", "G18D"]:
        row = by_id.get(k, {})
        kk = k.lower()
        out[f"{kk}_status"] = norm_status(str(row.get("status", "")))
        out[f"{kk}_value"] = to_float(row.get("value", ""))
        out[f"{kk}_threshold"] = str(row.get("threshold", ""))
    out["g18_final_status_metric"] = norm_status(str(by_id.get("FINAL", {}).get("status", "")))
    return out


def parse_config(path: Path) -> dict[str, float | None]:
    keys = [
        "mean_degree",
        "n_nodes",
        "spectral_gap_mu1",
        "binary_entropy_SA",
        "n_times_mean_IPR",
        "mean_G_diag",
        "cv_G_diag",
        "spectral_dim_ds",
        "rw_r2",
    ]
    out: dict[str, float | None] = {k: None for k in keys}
    if not path.exists():
        return out
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return out
    for k in keys:
        out[k] = to_float(payload.get(k, ""))
    return out


def detect_numeric_fields(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    excluded = {
        "seed",
    }
    out: list[str] = []
    for k in rows[0].keys():
        if k in excluded:
            continue
        if k.endswith("_status"):
            continue
        if "signature" in k:
            continue
        if k.endswith("_threshold"):
            continue
        if k in {"dataset_id", "block_id", "run_root", "signal_regime", "density_regime", "peak_regime", "geometry_regime"}:
            continue
        has_num = False
        for r in rows:
            if to_float(r.get(k, "")) is not None:
                has_num = True
                break
        if has_num:
            out.append(k)
    return out


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    official_paths = [Path(x).resolve() for x in parse_csv_list(args.official_summary_csvs)]
    cand_paths = [Path(x).resolve() for x in parse_csv_list(args.candidate_summary_csvs)]
    for p in official_paths:
        if not p.exists():
            raise FileNotFoundError(f"official summary missing: {p}")

    cand_map: dict[str, dict[str, str]] = {}
    for p in cand_paths:
        if not p.exists():
            continue
        for r in read_csv(p):
            try:
                k = key_of(str(r.get("dataset_id", "")), int(str(r.get("seed", "0"))))
            except Exception:
                continue
            cand_map[k] = r

    rows: list[dict[str, Any]] = []
    for p in official_paths:
        block_id = p.parent.name
        for r in read_csv(p):
            ds = str(r.get("dataset_id", "")).strip()
            seed = int(str(r.get("seed", "0")))
            run_root = str(r.get("run_root", "")).strip()
            key = key_of(ds, seed)

            run_abs = (ROOT / run_root).resolve()
            g18_dir = run_abs / "g18"
            g18_metrics = parse_metric_checks(g18_dir / "metric_checks_qm_info.csv")
            g18_cfg = parse_config(g18_dir / "config_qm_info.json")
            cand = cand_map.get(key, {})

            fail_sub = [g.upper().replace("_STATUS", "") for g in G18_SUBGATES if g18_metrics[g] == "fail"]
            fail_sig = "+".join(fail_sub) if fail_sub else "none"

            row: dict[str, Any] = {
                "block_id": block_id,
                "dataset_id": ds,
                "seed": seed,
                "run_root": run_root,
                "all_pass_qm_lane": norm_status(str(r.get("all_pass_qm_lane", ""))),
                "g17_status": norm_status(str(r.get("g17_status", ""))),
                "g18_status": norm_status(str(r.get("g18_status", ""))),
                "g19_status": norm_status(str(r.get("g19_status", ""))),
                "g20_status": norm_status(str(r.get("g20_status", ""))),
                "g18a_status": g18_metrics["g18a_status"],
                "g18b_status": g18_metrics["g18b_status"],
                "g18c_status": g18_metrics["g18c_status"],
                "g18d_status": g18_metrics["g18d_status"],
                "g18_subgate_signature": fail_sig,
                "g18_fail_subgates": ",".join(fail_sub) if fail_sub else "none",
                "g18a_value": g18_metrics["g18a_value"],
                "g18b_value": g18_metrics["g18b_value"],
                "g18c_value": g18_metrics["g18c_value"],
                "g18d_value": g18_metrics["g18d_value"],
                "g18a_threshold": g18_metrics["g18a_threshold"],
                "g18b_threshold": g18_metrics["g18b_threshold"],
                "g18c_threshold": g18_metrics["g18c_threshold"],
                "g18d_threshold": g18_metrics["g18d_threshold"],
                "g18_final_status_metric": g18_metrics["g18_final_status_metric"],
                "mean_degree": g18_cfg["mean_degree"],
                "n_nodes": g18_cfg["n_nodes"],
                "spectral_gap_mu1": g18_cfg["spectral_gap_mu1"],
                "binary_entropy_sa": g18_cfg["binary_entropy_SA"],
                "n_times_mean_ipr": g18_cfg["n_times_mean_IPR"],
                "mean_g_diag": g18_cfg["mean_G_diag"],
                "cv_g_diag": g18_cfg["cv_G_diag"],
                "spectral_dim_ds": g18_cfg["spectral_dim_ds"],
                "rw_r2": g18_cfg["rw_r2"],
                "multi_peak_mixing": str(cand.get("multi_peak_mixing", "")),
                "sigma_peak2_to_peak1": to_float(cand.get("sigma_peak2_to_peak1", "")),
                "peak12_distance_norm": to_float(cand.get("peak12_distance_norm", "")),
                "g17c_e0_per_mode": to_float(cand.get("g17c_e0_per_mode", "")),
                "g17b_slope": to_float(cand.get("g17b_slope", "")),
            }
            rows.append(row)

    if not rows:
        raise RuntimeError("no rows loaded for G18 taxonomy")

    rows.sort(key=lambda x: (str(x["dataset_id"]), int(x["seed"]), str(x["block_id"])))

    # Regime labels
    signal_vals = [float(r["g17c_e0_per_mode"]) for r in rows if r["g17c_e0_per_mode"] is not None]
    signal_q33 = percentile(signal_vals, 0.33) if signal_vals else float("nan")
    signal_q66 = percentile(signal_vals, 0.66) if signal_vals else float("nan")
    degree_vals = [float(r["mean_degree"]) for r in rows if r["mean_degree"] is not None]
    degree_q33 = percentile(degree_vals, 0.33) if degree_vals else float("nan")
    degree_q66 = percentile(degree_vals, 0.66) if degree_vals else float("nan")

    for r in rows:
        sv = r["g17c_e0_per_mode"]
        if sv is None or math.isnan(signal_q33):
            r["signal_regime"] = "unknown"
        elif sv <= signal_q33:
            r["signal_regime"] = "low_signal"
        elif sv >= signal_q66:
            r["signal_regime"] = "high_signal"
        else:
            r["signal_regime"] = "mid_signal"

        dv = r["mean_degree"]
        if dv is None or math.isnan(degree_q33):
            r["density_regime"] = "unknown"
        elif dv <= degree_q33:
            r["density_regime"] = "sparse"
        elif dv >= degree_q66:
            r["density_regime"] = "dense"
        else:
            r["density_regime"] = "mid_density"

        r["peak_regime"] = "multi_peak" if str(r.get("multi_peak_mixing", "")).strip().lower() == "true" else "single_peak"

        ratio = r.get("sigma_peak2_to_peak1")
        dist = r.get("peak12_distance_norm")
        if ratio is None or dist is None:
            r["geometry_regime"] = "unknown"
        elif ratio >= args.degenerate_peak_ratio_thr and dist <= args.degenerate_peak_dist_thr:
            r["geometry_regime"] = "degenerate_geometry"
        else:
            r["geometry_regime"] = "normal_geometry"

    g18_fail = [r for r in rows if r["g18_status"] == "fail"]
    g18_pass = [r for r in rows if r["g18_status"] == "pass"]

    case_fields = [
        "block_id",
        "dataset_id",
        "seed",
        "g18_status",
        "all_pass_qm_lane",
        "g17_status",
        "g19_status",
        "g20_status",
        "g18a_status",
        "g18b_status",
        "g18c_status",
        "g18d_status",
        "g18_final_status_metric",
        "g18_subgate_signature",
        "g18_fail_subgates",
        "g18a_value",
        "g18b_value",
        "g18c_value",
        "g18d_value",
        "g18a_threshold",
        "g18b_threshold",
        "g18c_threshold",
        "g18d_threshold",
        "signal_regime",
        "density_regime",
        "peak_regime",
        "geometry_regime",
        "multi_peak_mixing",
        "mean_degree",
        "n_nodes",
        "spectral_gap_mu1",
        "binary_entropy_sa",
        "n_times_mean_ipr",
        "mean_g_diag",
        "cv_g_diag",
        "spectral_dim_ds",
        "rw_r2",
        "g17c_e0_per_mode",
        "g17b_slope",
        "sigma_peak2_to_peak1",
        "peak12_distance_norm",
        "run_root",
    ]
    write_csv(out_dir / "g18_fail_cases.csv", g18_fail, case_fields)
    write_csv(out_dir / "g18_pass_cases.csv", g18_pass, case_fields)

    # pattern summary: counts by dataset and failing subgate/signature
    pattern_rows: list[dict[str, Any]] = []
    datasets = sorted({str(r["dataset_id"]) for r in rows})
    for ds in ["ALL"] + datasets:
        sub_all = rows if ds == "ALL" else [r for r in rows if str(r["dataset_id"]) == ds]
        sub_fail = g18_fail if ds == "ALL" else [r for r in g18_fail if str(r["dataset_id"]) == ds]
        n_all = len(sub_all)
        n_fail = len(sub_fail)

        for g in G18_SUBGATES:
            count = sum(1 for r in sub_fail if r[g] == "fail")
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "pattern_type": "g18_subgate",
                    "pattern": g,
                    "count": count,
                    "n_total": n_all,
                    "n_g18_fail": n_fail,
                    "rate_within_g18_fail": (count / n_fail) if n_fail else 0.0,
                    "rate_within_total": (count / n_all) if n_all else 0.0,
                }
            )

        sig_counter = Counter(str(r["g18_subgate_signature"]) for r in sub_fail)
        for sig, count in sig_counter.items():
            pattern_rows.append(
                {
                    "dataset_id": ds,
                    "pattern_type": "g18_subgate_signature",
                    "pattern": sig,
                    "count": count,
                    "n_total": n_all,
                    "n_g18_fail": n_fail,
                    "rate_within_g18_fail": (count / n_fail) if n_fail else 0.0,
                    "rate_within_total": (count / n_all) if n_all else 0.0,
                }
            )

    pattern_rows.sort(
        key=lambda r: (str(r["dataset_id"]), str(r["pattern_type"]), -int(r["count"]), str(r["pattern"]))
    )
    write_csv(
        out_dir / "pattern_summary_g18_subgates.csv",
        pattern_rows,
        ["dataset_id", "pattern_type", "pattern", "count", "n_total", "n_g18_fail", "rate_within_g18_fail", "rate_within_total"],
    )

    regime_rows: list[dict[str, Any]] = []
    for field in ["signal_regime", "density_regime", "peak_regime", "geometry_regime"]:
        cnt_fail = Counter(str(r.get(field, "")) for r in g18_fail)
        cnt_all = Counter(str(r.get(field, "")) for r in rows)
        keys = sorted(set(cnt_all.keys()) | set(cnt_fail.keys()))
        for k in keys:
            regime_rows.append(
                {
                    "regime_field": field,
                    "regime_value": k,
                    "count_fail": cnt_fail.get(k, 0),
                    "count_total": cnt_all.get(k, 0),
                    "rate_within_g18_fail": (cnt_fail.get(k, 0) / len(g18_fail)) if g18_fail else 0.0,
                    "rate_within_total": (cnt_fail.get(k, 0) / cnt_all.get(k, 1)) if cnt_all.get(k, 0) else 0.0,
                }
            )
    regime_rows.sort(key=lambda r: (str(r["regime_field"]), -int(r["count_fail"]), str(r["regime_value"])))
    write_csv(
        out_dir / "regime_summary.csv",
        regime_rows,
        ["regime_field", "regime_value", "count_fail", "count_total", "rate_within_g18_fail", "rate_within_total"],
    )

    # optional feature correlations
    feature_rows: list[dict[str, Any]] = []
    numeric_fields = detect_numeric_fields(rows)
    for ds in ["ALL"] + datasets:
        sub = rows if ds == "ALL" else [r for r in rows if str(r["dataset_id"]) == ds]
        for f in numeric_fields:
            xs: list[float] = []
            ys: list[float] = []
            x_fail: list[float] = []
            x_pass: list[float] = []
            for r in sub:
                x = to_float(r.get(f, ""))
                if x is None:
                    continue
                y = 1.0 if r["g18_status"] == "fail" else 0.0
                xs.append(x)
                ys.append(y)
                if y > 0.5:
                    x_fail.append(x)
                else:
                    x_pass.append(x)
            if not xs:
                continue
            mf = mean(x_fail)
            mp = mean(x_pass)
            feature_rows.append(
                {
                    "dataset_id": ds,
                    "feature": f,
                    "n": len(xs),
                    "n_fail": len(x_fail),
                    "n_pass": len(x_pass),
                    "mean_fail": f6(mf),
                    "mean_pass": f6(mp),
                    "delta_fail_minus_pass": f6((mf - mp) if mf is not None and mp is not None else None),
                    "pearson_fail_corr": f6(pearson(xs, ys)),
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
        ["dataset_id", "feature", "n", "n_fail", "n_pass", "mean_fail", "mean_pass", "delta_fail_minus_pass", "pearson_fail_corr"],
    )

    # report
    total = len(rows)
    total_fail = len(g18_fail)
    total_pass = len(g18_pass)
    fail_rate = (total_fail / total) if total else 0.0

    subgate_counts = Counter()
    signature_counts = Counter(str(r["g18_subgate_signature"]) for r in g18_fail)
    for r in g18_fail:
        for g in G18_SUBGATES:
            if r[g] == "fail":
                subgate_counts[g] += 1

    dataset_rows = []
    for ds in datasets:
        all_ds = [r for r in rows if str(r["dataset_id"]) == ds]
        fail_ds = [r for r in all_ds if r["g18_status"] == "fail"]
        dataset_rows.append(
            {
                "dataset_id": ds,
                "n_total": len(all_ds),
                "n_fail": len(fail_ds),
                "fail_rate": (len(fail_ds) / len(all_ds)) if all_ds else 0.0,
            }
        )
    dataset_rows.sort(key=lambda r: float(r["fail_rate"]), reverse=True)

    top_signatures = signature_counts.most_common(3)
    top_corr = next((r for r in feature_rows if r["dataset_id"] == "ALL" and str(r["pearson_fail_corr"]).strip()), None)
    top_corr_feature = str(top_corr["feature"]) if top_corr else "n/a"
    top_corr_val = str(top_corr["pearson_fail_corr"]) if top_corr else ""

    top_ds = dataset_rows[0]["dataset_id"] if dataset_rows else "n/a"
    top_subgate = subgate_counts.most_common(1)[0][0] if subgate_counts else "none"
    hypotheses = [
        f"Subgate-dominant mechanism: `{top_subgate}` dominates G18 failures, indicating concentration around one information-geometry observable.",
        f"Dataset sensitivity mechanism: `{top_ds}` has the highest G18 fail-rate, suggesting topology/regime dependence in the QM info lane.",
        (
            f"Feature-linked mechanism: `{top_corr_feature}` has strongest correlation with G18 fail (`r={top_corr_val}`), indicating failures cluster in specific signal/geometry regimes."
            if top_corr_feature != "n/a"
            else "Feature-linked mechanism: no stable numeric correlation could be extracted from available metrics."
        ),
    ]

    lines = [
        "# G18 Failure Taxonomy (v1)",
        "",
        f"- generated_utc: `{datetime.utcnow().isoformat()}Z`",
        f"- profiles_total: `{total}`",
        f"- g18_fail_profiles: `{total_fail}`",
        f"- g18_pass_profiles: `{total_pass}`",
        f"- g18_fail_rate: `{fail_rate:.6f}`",
        "",
        "## Dominant G18 Failing Subgates",
        "",
    ]
    for gate, c in subgate_counts.most_common(args.top_k):
        lines.append(f"- `{gate}`: `{c}` fail occurrences")

    lines.extend(["", "## Dataset Sensitivity", ""])
    for r in dataset_rows:
        lines.append(
            f"- `{r['dataset_id']}`: `{r['n_fail']}/{r['n_total']}` fail (`{float(r['fail_rate']):.6f}`)"
        )

    lines.extend(["", "## Regime Patterns (Fail Cases)", ""])
    for field in ["signal_regime", "density_regime", "peak_regime", "geometry_regime"]:
        lines.append(f"- `{field}`:")
        field_rows = [rr for rr in regime_rows if rr["regime_field"] == field]
        for rr in field_rows[:5]:
            lines.append(
                f"  - `{rr['regime_value']}`: `{rr['count_fail']}` fails "
                f"(within-fail `{float(rr['rate_within_g18_fail']):.6f}`)"
            )

    lines.extend(["", "## Top 3 Fail Signatures", ""])
    for sig, c in top_signatures:
        lines.append(f"- `{sig}`: `{c}`")
    if not top_signatures:
        lines.append("- `none`")

    lines.extend(["", "## Top 3 Hypothesized Mechanisms (No Changes Applied)", ""])
    for h in hypotheses:
        lines.append(f"- {h}")

    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `g18_fail_cases.csv`",
            "- `g18_pass_cases.csv`",
            "- `pattern_summary_g18_subgates.csv`",
            "- `regime_summary.csv`",
            "- `feature_correlations.csv`",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"g18_fail_cases:            {out_dir / 'g18_fail_cases.csv'}")
    print(f"g18_pass_cases:            {out_dir / 'g18_pass_cases.csv'}")
    print(f"pattern_summary_subgates:  {out_dir / 'pattern_summary_g18_subgates.csv'}")
    print(f"regime_summary:            {out_dir / 'regime_summary.csv'}")
    print(f"feature_correlations:      {out_dir / 'feature_correlations.csv'}")
    print(f"report_md:                 {out_dir / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
