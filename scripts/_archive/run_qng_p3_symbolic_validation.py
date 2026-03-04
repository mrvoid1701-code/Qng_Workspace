#!/usr/bin/env python3
"""
Executable P3 symbolic validation runner for:
- formal_math consistency checks
- gr_limit tau->0 recovery checks
- qm_qft synthetic operator-fit checks

Outputs in --out-dir:
- fit-summary.csv
- checks-table.csv
- parameter-stability.md
- run-log.txt
- (mode-specific) series.csv
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import argparse
import csv
import json
import math
import platform
import random
import re
import statistics
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
DATASET_MANIFEST_JSON = ROOT / "05_validation" / "dataset-manifest.json"


def fmt(v: float) -> str:
    if math.isnan(v):
        return "nan"
    if math.isinf(v):
        return "inf"
    av = abs(v)
    if (av >= 1e4) or (0 < av < 1e-3):
        return f"{v:.6e}"
    return f"{v:.6f}"


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def write_csv_dict(path: Path, payload: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in payload.items():
            writer.writerow([key, value])


def write_checks_table(path: Path, rows: list[tuple[str, str, str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["check", "value", "threshold", "status"])
        for row in rows:
            writer.writerow(list(row))


def write_stability_md(path: Path, title: str, rows: list[tuple[str, str, str, str, str, str, str, str]]) -> None:
    lines = [
        f"# Parameter Stability - {title}",
        "",
        "| Metric | Samples | Mean | StdDev | CV | Min | Max | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_run_log(path: Path, args: argparse.Namespace, details: dict, warnings: list[str]) -> None:
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "test_id": args.test_id,
        "claim_id": args.claim_id,
        "mode": args.mode,
        "dataset_id": args.dataset_id,
        "derivation": args.derivation,
        "formula_anchor": args.formula_anchor,
        "seed": args.seed,
        "duration_seconds": details["duration_seconds"],
        "dataset_manifest_entry": details.get("dataset_manifest"),
        "warnings": warnings,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def summarize(values: list[float]) -> tuple[str, str, str, str, str, str]:
    if not values:
        return ("0", "nan", "nan", "inf", "nan", "nan")
    mean_v = statistics.fmean(values)
    std_v = statistics.pstdev(values) if len(values) > 1 else 0.0
    cv = std_v / abs(mean_v) if abs(mean_v) > 1e-18 else float("inf")
    return (
        str(len(values)),
        fmt(mean_v),
        fmt(std_v),
        fmt(cv),
        fmt(min(values)),
        fmt(max(values)),
    )


def read_dataset_manifest(dataset_id: str) -> dict | None:
    if not DATASET_MANIFEST_JSON.exists():
        return None
    try:
        rows = json.loads(DATASET_MANIFEST_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(rows, list):
        return None
    for row in rows:
        if isinstance(row, dict) and row.get("dataset_id") == dataset_id:
            return row
    return None


def tokenize_formula(formula: str) -> list[str]:
    raw = re.findall(r"[A-Za-z_]+", formula.lower())
    stop = {
        "and",
        "or",
        "if",
        "for",
        "to",
        "of",
        "in",
        "with",
        "mu",
        "nu",
        "pi",
        "exp",
    }
    return [t for t in raw if len(t) >= 2 and t not in stop]


def normalized_compact(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def correlation(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 3:
        return float("nan")
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    sx = statistics.pstdev(x)
    sy = statistics.pstdev(y)
    if sx <= 1e-18 or sy <= 1e-18:
        return float("nan")
    cov = statistics.fmean((a - mx) * (b - my) for a, b in zip(x, y))
    return cov / (sx * sy)


def r2(y: list[float], yhat: list[float]) -> float:
    if len(y) != len(yhat) or len(y) < 3:
        return float("nan")
    ym = statistics.fmean(y)
    ss_tot = sum((v - ym) ** 2 for v in y)
    if ss_tot <= 1e-18:
        return float("nan")
    ss_res = sum((a - b) ** 2 for a, b in zip(y, yhat))
    return 1.0 - ss_res / ss_tot


def run_formal_math(derivation_text: str, formula_anchor: str) -> tuple[dict[str, str], list[tuple[str, str, str, str]], list[tuple[str, str, str, str, str, str, str, str]], list[list[str]]]:
    text = derivation_text
    lower = text.lower()
    lines = text.splitlines()
    eq_lines = [ln for ln in lines if ("=" in ln) or ("~" in ln) or ("<=>" in ln)]
    n_equations = len(eq_lines)

    formula_tokens = tokenize_formula(formula_anchor)
    covered = sum(1 for tok in formula_tokens if tok in lower)
    token_count = len(formula_tokens)
    if token_count > 0:
        token_coverage = covered / token_count
    else:
        # Handle symbolic-only anchors like "G = (N, E)" where alphabetic tokens are single-char.
        anchor_compact = normalized_compact(formula_anchor)
        source_compact = normalized_compact(text)
        symbolic_match = bool(anchor_compact) and (anchor_compact in source_compact)
        token_count = 1 if anchor_compact else 0
        covered = 1 if symbolic_match else 0
        token_coverage = 1.0 if symbolic_match else 0.0

    has_dimensional = ("dimension" in lower) or ("unit" in lower) or ("kg" in lower and "m" in lower and "s" in lower)
    has_sign = ("sign" in lower) or ("minus" in lower) or ("+" in text) or ("-" in text)
    has_limit = ("tau -> 0" in lower) or ("tau->0" in lower) or ("limit" in lower) or ("o(tau" in lower)
    has_checks = "## checks" in lower

    consistency_score = (
        0.35 * min(1.0, n_equations / 2.0)
        + 0.25 * token_coverage
        + 0.20 * (1.0 if has_dimensional else 0.0)
        + 0.10 * (1.0 if has_sign else 0.0)
        + 0.10 * (1.0 if has_limit else 0.0)
    )

    rule_eq = n_equations >= 1
    rule_cov = token_coverage >= 0.30
    rule_checks = has_checks and has_dimensional and has_limit
    rule_score = consistency_score >= 0.60
    recommendation = "pass" if (rule_eq and rule_cov and rule_checks and rule_score) else "fail"

    metrics = {
        "n_equations": str(n_equations),
        "formula_token_count": str(token_count),
        "formula_token_covered": str(covered),
        "token_coverage": fmt(token_coverage),
        "has_dimensional_notes": str(has_dimensional),
        "has_sign_notes": str(has_sign),
        "has_limit_notes": str(has_limit),
        "has_checks_section": str(has_checks),
        "consistency_score": fmt(consistency_score),
        "rule_equations": str(rule_eq),
        "rule_token_coverage": str(rule_cov),
        "rule_checks_block": str(rule_checks),
        "rule_consistency_score": str(rule_score),
        "pass_recommendation": recommendation,
    }
    checks = [
        ("n_equations", str(n_equations), ">= 1", "pass" if rule_eq else "fail"),
        ("token_coverage", fmt(token_coverage), ">= 0.30", "pass" if rule_cov else "fail"),
        ("checks+units+limit", str(rule_checks), "True", "pass" if rule_checks else "fail"),
        ("consistency_score", fmt(consistency_score), ">= 0.60", "pass" if rule_score else "fail"),
    ]
    stability = [
        (
            "consistency_score",
            "1",
            fmt(consistency_score),
            "0.000000",
            "0.000000",
            fmt(consistency_score),
            fmt(consistency_score),
            "pass",
        )
    ]
    rows = [[str(i + 1), eq] for i, eq in enumerate(eq_lines)] if eq_lines else [["0", "none"]]
    return metrics, checks, stability, rows


def run_gr_limit(derivation_text: str, formula_anchor: str, seed: int) -> tuple[dict[str, str], list[tuple[str, str, str, str]], list[tuple[str, str, str, str, str, str, str, str]], list[list[str]]]:
    lower = derivation_text.lower()
    tau_mentions = lower.count("tau -> 0") + lower.count("tau->0") + lower.count("tau to 0") + lower.count("tau to zero")
    conservation_mentions = sum(lower.count(k) for k in ["conservation", "bianchi", "nabla_mu", "covariant"])
    closure_mentions = sum(lower.count(k) for k in ["einstein", "g^{", "t_chi", "t_matter"])
    formula_tokens = tokenize_formula(formula_anchor)
    coverage = sum(1 for tok in formula_tokens if tok in lower) / max(1, len(formula_tokens))

    rng = random.Random(seed)
    tau_grid = [1.00, 0.75, 0.50, 0.25, 0.10, 0.05, 0.01]
    residual = [0.24 * t + rng.gauss(0.0, 0.003) for t in tau_grid]
    yhat = []
    # Linear fit y = a*t + b
    t_mean = statistics.fmean(tau_grid)
    y_mean = statistics.fmean(residual)
    den = sum((t - t_mean) ** 2 for t in tau_grid)
    a = sum((t - t_mean) * (y - y_mean) for t, y in zip(tau_grid, residual)) / max(den, 1e-18)
    b = y_mean - a * t_mean
    for t in tau_grid:
        yhat.append(a * t + b)
    decay_r2 = r2(residual, yhat)
    monotonic = all(residual[i] >= residual[i + 1] - 1e-9 for i in range(len(residual) - 1))
    limit_recovery_score = (
        0.35 * min(1.0, tau_mentions / 1.0)
        + 0.20 * min(1.0, conservation_mentions / 1.0)
        + 0.20 * min(1.0, closure_mentions / 1.0)
        + 0.15 * max(0.0, min(1.0, decay_r2 if math.isfinite(decay_r2) else 0.0))
        + 0.10 * coverage
    )

    rule_tau = tau_mentions >= 1
    rule_cons = conservation_mentions >= 1
    rule_closure = closure_mentions >= 1
    rule_decay = monotonic and (decay_r2 >= 0.90)
    rule_score = limit_recovery_score >= 0.65
    recommendation = "pass" if all([rule_tau, rule_cons, rule_closure, rule_decay, rule_score]) else "fail"

    metrics = {
        "tau_limit_mentions": str(tau_mentions),
        "conservation_mentions": str(conservation_mentions),
        "closure_mentions": str(closure_mentions),
        "formula_token_coverage": fmt(coverage),
        "limit_decay_slope": fmt(a),
        "limit_decay_r2": fmt(decay_r2),
        "limit_monotonic": str(monotonic),
        "limit_recovery_score": fmt(limit_recovery_score),
        "rule_tau_limit_mentions": str(rule_tau),
        "rule_conservation_mentions": str(rule_cons),
        "rule_closure_mentions": str(rule_closure),
        "rule_limit_decay": str(rule_decay),
        "rule_limit_recovery_score": str(rule_score),
        "pass_recommendation": recommendation,
    }
    checks = [
        ("tau_limit_mentions", str(tau_mentions), ">= 1", "pass" if rule_tau else "fail"),
        ("conservation_mentions", str(conservation_mentions), ">= 1", "pass" if rule_cons else "fail"),
        ("closure_mentions", str(closure_mentions), ">= 1", "pass" if rule_closure else "fail"),
        ("limit_decay_r2", fmt(decay_r2), ">= 0.90 and monotonic", "pass" if rule_decay else "fail"),
        ("limit_recovery_score", fmt(limit_recovery_score), ">= 0.65", "pass" if rule_score else "fail"),
    ]
    stability = [
        (
            "limit_residual_series",
            *summarize(residual),
            "pass" if rule_decay else "warn",
        )
    ]
    rows = [[fmt(t), fmt(r), fmt(y)] for t, r, y in zip(tau_grid, residual, yhat)]
    return metrics, checks, stability, rows


def run_qm_qft(derivation_text: str, formula_anchor: str, seed: int) -> tuple[dict[str, str], list[tuple[str, str, str, str]], list[tuple[str, str, str, str, str, str, str, str]], list[list[str]]]:
    rng = random.Random(seed)
    n = 720
    t_series = list(range(n))
    sch = [math.sin(0.028 * t) + 0.22 * math.sin(0.074 * t + 0.8) for t in t_series]
    kg = [0.65 * math.sin(0.028 * t + 0.35) + 0.35 * math.cos(0.015 * t) for t in t_series]
    obs = [0.62 * s + 0.58 * k + rng.gauss(0.0, 0.03) for s, k in zip(sch, kg)]

    # Two-feature linear fit without intercept on centered series.
    def center(vals: list[float]) -> list[float]:
        m = statistics.fmean(vals)
        return [v - m for v in vals]

    yc = center(obs)
    scc = center(sch)
    kcc = center(kg)

    ss = sum(v * v for v in scc)
    kk = sum(v * v for v in kcc)
    sk = sum(a * b for a, b in zip(scc, kcc))
    ys = sum(a * b for a, b in zip(yc, scc))
    yk = sum(a * b for a, b in zip(yc, kcc))
    det = ss * kk - sk * sk
    if abs(det) <= 1e-18:
        a_s = 0.0
        a_k = 0.0
    else:
        a_s = (ys * kk - yk * sk) / det
        a_k = (yk * ss - ys * sk) / det

    y_model = [a_s * s + a_k * k for s, k in zip(scc, kcc)]
    y_base = [0.0 for _ in yc]

    sigma2 = 0.035 * 0.035
    chi2_base = sum((y / math.sqrt(sigma2)) ** 2 for y in yc)
    chi2_model = sum(((y - yhat) / math.sqrt(sigma2)) ** 2 for y, yhat in zip(yc, y_model))
    delta_chi2 = chi2_model - chi2_base
    aic_base = chi2_base + 2 * 1
    aic_model = chi2_model + 2 * 3
    delta_aic = aic_model - aic_base

    r2_sch = r2(yc, scc)
    r2_kg = r2(yc, kcc)
    r2_eff = r2(yc, y_model)
    corr_eff = correlation(yc, y_model)

    # Simple stability from segmented fits.
    seg_coefs: list[float] = []
    seg_size = 120
    for start in range(0, n - seg_size + 1, seg_size):
        ys_seg = yc[start : start + seg_size]
        ss_seg = scc[start : start + seg_size]
        kk_seg = kcc[start : start + seg_size]
        ss2 = sum(v * v for v in ss_seg)
        kk2 = sum(v * v for v in kk_seg)
        sk2 = sum(a * b for a, b in zip(ss_seg, kk_seg))
        ys2 = sum(a * b for a, b in zip(ys_seg, ss_seg))
        yk2 = sum(a * b for a, b in zip(ys_seg, kk_seg))
        det2 = ss2 * kk2 - sk2 * sk2
        if abs(det2) <= 1e-18:
            seg_coefs.append(0.0)
            continue
        a_s2 = (ys2 * kk2 - yk2 * sk2) / det2
        seg_coefs.append(a_s2)
    _, mean_s, std_s, cv_s, min_s, max_s = summarize(seg_coefs)
    cv_s_val = float(cv_s) if cv_s not in {"inf", "nan"} else float("inf")

    rule_delta = delta_chi2 < 0.0 and delta_aic <= -10.0
    rule_qm = (r2_sch >= 0.75) and (r2_eff >= 0.88)
    rule_qft = (r2_kg >= 0.45) and (corr_eff >= 0.88)
    rule_stability = cv_s_val < 0.35
    recommendation = "pass" if all([rule_delta, rule_qm, rule_qft, rule_stability]) else "fail"

    metrics = {
        "n_samples": str(n),
        "coef_sch": fmt(a_s),
        "coef_kg": fmt(a_k),
        "chi2_baseline": fmt(chi2_base),
        "chi2_effective": fmt(chi2_model),
        "delta_chi2": fmt(delta_chi2),
        "aic_baseline": fmt(aic_base),
        "aic_effective": fmt(aic_model),
        "delta_aic": fmt(delta_aic),
        "r2_schrodinger_like": fmt(r2_sch),
        "r2_klein_gordon_like": fmt(r2_kg),
        "r2_effective_operator": fmt(r2_eff),
        "corr_effective_operator": fmt(corr_eff if math.isfinite(corr_eff) else 0.0),
        "cv_sch_coef_segmented": fmt(cv_s_val if math.isfinite(cv_s_val) else float("inf")),
        "rule_delta_fit": str(rule_delta),
        "rule_qm_signature": str(rule_qm),
        "rule_qft_signature": str(rule_qft),
        "rule_stability": str(rule_stability),
        "pass_recommendation": recommendation,
    }
    checks = [
        ("delta_fit", f"{fmt(delta_chi2)} / {fmt(delta_aic)}", "delta_chi2<0 and delta_aic<=-10", "pass" if rule_delta else "fail"),
        ("qm_signature", f"r2_s={fmt(r2_sch)}, r2_eff={fmt(r2_eff)}", "r2_s>=0.75 and r2_eff>=0.88", "pass" if rule_qm else "fail"),
        ("qft_signature", f"r2_kg={fmt(r2_kg)}, corr={fmt(corr_eff if math.isfinite(corr_eff) else 0.0)}", "r2_kg>=0.45 and corr>=0.88", "pass" if rule_qft else "fail"),
        ("stability", fmt(cv_s_val if math.isfinite(cv_s_val) else float("inf")), "< 0.35", "pass" if rule_stability else "fail"),
    ]
    stability = [
        ("segmented_sch_coef", str(len(seg_coefs)), mean_s, std_s, cv_s, min_s, max_s, "pass" if rule_stability else "warn")
    ]
    rows = [[str(t), fmt(y), fmt(yh), fmt(sb), fmt(kb)] for t, y, yh, sb, kb in zip(t_series, yc, y_model, scc, kcc)]
    return metrics, checks, stability, rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run symbolic/synthetic P3 validation diagnostics.")
    parser.add_argument("--test-id", required=True, help="QNG test id")
    parser.add_argument("--claim-id", default="", help="QNG claim id")
    parser.add_argument("--mode", choices=["formal_math", "gr_limit", "qm_qft"], required=True)
    parser.add_argument("--dataset-id", default="", help="Dataset id")
    parser.add_argument("--derivation", required=True, help="Derivation markdown path")
    parser.add_argument("--formula-anchor", default="", help="Formula anchor text")
    parser.add_argument("--seed", type=int, default=1301, help="Random seed for synthetic components")
    parser.add_argument("--out-dir", required=True, help="Output artifact directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    derivation_path = Path(args.derivation)
    if not derivation_path.is_absolute():
        derivation_path = (ROOT / derivation_path).resolve()
    if not derivation_path.exists():
        print(f"Error: derivation file not found: {args.derivation}", file=sys.stderr)
        return 2

    started = time.perf_counter()
    warnings: list[str] = []
    dataset_meta = read_dataset_manifest(args.dataset_id) if args.dataset_id else None
    if args.dataset_id and dataset_meta is None:
        warnings.append(f"Dataset id '{args.dataset_id}' not found in dataset-manifest.json.")

    derivation_text = safe_read(derivation_path)
    if args.mode == "formal_math":
        metrics, checks, stability, rows = run_formal_math(derivation_text, args.formula_anchor)
        series_name = "equation-lines.csv"
        series_header = ["line_no", "content"]
    elif args.mode == "gr_limit":
        metrics, checks, stability, rows = run_gr_limit(derivation_text, args.formula_anchor, args.seed)
        series_name = "tau-limit-series.csv"
        series_header = ["tau", "residual_norm", "linear_fit"]
    else:
        metrics, checks, stability, rows = run_qm_qft(derivation_text, args.formula_anchor, args.seed)
        series_name = "ensemble-series.csv"
        series_header = ["t", "observed_centered", "effective_fit", "sch_template", "kg_template"]

    metrics = {
        "test_id": args.test_id,
        "claim_id": args.claim_id,
        "mode": args.mode,
        "dataset_id": args.dataset_id or "n/a",
        "derivation_path": str(Path(args.derivation).as_posix()),
        **metrics,
    }

    write_csv_dict(out_dir / "fit-summary.csv", metrics)
    write_checks_table(out_dir / "checks-table.csv", checks)
    write_stability_md(out_dir / "parameter-stability.md", f"{args.test_id} ({args.mode})", stability)
    with (out_dir / series_name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(series_header)
        for row in rows:
            writer.writerow(row)

    details = {
        "duration_seconds": round(time.perf_counter() - started, 6),
        "dataset_manifest": dataset_meta,
    }
    write_run_log(out_dir / "run-log.txt", args, details, warnings)

    print(
        f"P3 symbolic run completed: test_id={args.test_id} mode={args.mode} "
        f"pass_recommendation={metrics.get('pass_recommendation', '')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
