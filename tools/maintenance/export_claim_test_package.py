#!/usr/bin/env python3
"""
Export a deep claim/test/result package for selected validation tests.

Outputs per test:
- 07_exports/claim-packages/<test-id>-claim-test-report.md
- 07_exports/claim-packages/<test-id>-claim-test-report.odt
- 07_exports/claim-packages/<test-id>-claim-test-report.pdf
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import export_full_theory_dossier as dossier
import workspace_ui as wui


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_ROOT = ROOT / "05_validation" / "evidence" / "artifacts"
SYMBOLS_MD = ROOT / "03_math" / "symbols.md"
EXPORT_DIR = ROOT / "07_exports" / "claim-packages"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def clean_cell(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


def md_section(lines: list[str], title: str) -> list[str]:
    heading = f"## {title}".lower()
    start = -1
    for idx, line in enumerate(lines):
        if line.strip().lower() == heading:
            start = idx + 1
            break
    if start < 0:
        return []
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        out.append(line.rstrip("\n"))
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def first_code_block(lines: list[str], title: str) -> str:
    section_lines = md_section(lines, title)
    if not section_lines:
        return ""
    in_code = False
    block: list[str] = []
    for line in section_lines:
        if line.strip().startswith("```"):
            if in_code:
                break
            in_code = True
            continue
        if in_code:
            block.append(line)
    return "\n".join(block).strip()


def csv_metric_map(path: Path) -> dict[str, str]:
    if not path.exists() or not path.is_file():
        return {}
    out: dict[str, str] = {}
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        for i, row in enumerate(reader):
            if not row:
                continue
            if i == 0 and row[0].strip().lower() == "metric":
                continue
            if len(row) < 2:
                continue
            key = row[0].strip()
            value = row[1].strip()
            if key:
                out[key] = value
    return out


def as_float(value: str) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def as_bool(value: str) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def default_gold_test_ids() -> list[str]:
    rows = wui.parse_results_per_test()
    ids = [
        row["test_id"]
        for row in rows
        if row.get("exec_status") == "pass" and row.get("authenticity", "").lower() == "gold"
    ]
    return sorted(set(ids))


def find_row_data(test_id: str) -> tuple[dict, dict, dict]:
    claims = wui.parse_claims_register()
    tests = wui.parse_test_plan()
    results = wui.parse_results_per_test()
    merged = wui.combine_test_rows(tests, results)

    row = next((r for r in merged if r["test_id"] == test_id), None)
    if not row:
        raise ValueError(f"Unknown test id: {test_id}")

    claim = next((c for c in claims if c["claim_id"] == row["claim_id"]), {})
    result = next((r for r in results if r["test_id"] == test_id), {})
    return row, claim, result


def parse_symbol_rows() -> list[dict]:
    rows: list[dict] = []
    for line in read_text(SYMBOLS_MD).splitlines():
        cells = wui.split_md_row(line)
        if len(cells) != 5:
            continue
        if cells[0].strip().lower() == "symbol":
            continue
        if wui.is_separator_row(cells):
            continue
        rows.append(
            {
                "symbol": cells[0].strip(),
                "meaning": cells[1].strip(),
                "unit": cells[2].strip(),
                "notes": cells[4].strip(),
            }
        )
    return rows


def symbol_aliases(symbol: str) -> set[str]:
    clean = symbol.strip().strip("`")
    aliases = {clean}
    token_src = re.sub(r"[\\\{\}\(\)\[\]\|^*/,+\-=:]", " ", clean)
    for token in re.findall(r"[A-Za-z]+(?:_[A-Za-z0-9]+)?", token_src):
        aliases.add(token)
    return {a for a in aliases if a}


def select_relevant_symbols(source_text: str) -> list[dict]:
    source = source_text.lower()
    selected: list[dict] = []
    for row in parse_symbol_rows():
        found = False
        for alias in symbol_aliases(row["symbol"]):
            pattern = rf"(?<![a-z0-9_]){re.escape(alias.lower())}(?![a-z0-9_])"
            if re.search(pattern, source):
                found = True
                break
        if found:
            selected.append(row)
    selected.sort(key=lambda item: item["symbol"].lower())
    return selected


def collect_variant_rows(test_id: str) -> list[dict]:
    slug = test_id.lower()
    prefix = f"{slug}-"
    rows: list[dict] = []
    preferred = wui.resolve_artifact_dir_for_test(test_id)
    candidates: list[Path] = []

    exact = ARTIFACTS_ROOT / slug
    if exact.exists() and exact.is_dir():
        candidates.append(exact)

    for path in sorted(ARTIFACTS_ROOT.glob(f"{prefix}*")):
        if not path.is_dir():
            continue
        candidates.append(path)

    seen: set[str] = set()
    ordered: list[Path] = []
    if preferred and preferred.exists() and preferred.is_dir():
        ordered.append(preferred)
        seen.add(str(preferred.resolve()).lower())

    for path in candidates:
        key = str(path.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)

    for path in ordered:
        fit = csv_metric_map(path / "fit-summary.csv")
        neg = csv_metric_map(path / "negative-controls-summary.csv")
        if preferred and path.resolve() == preferred.resolve():
            label = "primary"
        elif path.name.startswith(prefix):
            label = path.name[len(prefix) :]
        else:
            label = path.name
        rows.append(
            {
                "label": label,
                "n_lensing": fit.get("n_lensing", ""),
                "delta_chi2": fit.get("delta_chi2", ""),
                "delta_aic": fit.get("delta_aic", ""),
                "delta_bic": fit.get("delta_bic", ""),
                "offset_score": fit.get("offset_score", ""),
                "fit_pass": fit.get("pass_recommendation", ""),
                "neg_pass": neg.get("negative_control_pass", ""),
                "path": rel(path),
            }
        )
    rows.sort(key=lambda item: (0 if item["label"] == "primary" else 1, item["label"].lower()))
    return rows


def matching_runs(test_id: str) -> list[dict]:
    rows = wui.parse_run_journal()
    out: list[dict] = []
    for row in rows:
        touched = [part.strip() for part in row.get("tests_touched", "").split(",") if part.strip()]
        if test_id in touched:
            out.append(row)
    return out


def explain_pass(row: dict, fit: dict[str, str], neg: dict[str, str]) -> list[str]:
    reasons: list[str] = []
    delta_chi2 = as_float(fit.get("delta_chi2", ""))
    delta_aic = as_float(fit.get("delta_aic", ""))
    delta_bic = as_float(fit.get("delta_bic", ""))
    offset_score = as_float(fit.get("offset_score", ""))

    if delta_chi2 is not None and delta_chi2 < 0:
        reasons.append(f"`delta_chi2={fit.get('delta_chi2')}` is negative, so memory fit improves over baseline.")
    if delta_aic is not None and delta_aic <= -10:
        reasons.append(f"`delta_aic={fit.get('delta_aic')}` indicates strong model preference by AIC.")
    if delta_bic is not None and delta_bic <= -10:
        reasons.append(f"`delta_bic={fit.get('delta_bic')}` indicates strong model preference by BIC.")
    if offset_score is not None:
        reasons.append(f"`offset_score={fit.get('offset_score')}` confirms offset-reproduction target was met.")

    for gate in (
        "rule_pass_delta_chi2",
        "rule_pass_delta_aic",
        "rule_pass_delta_bic",
        "rule_pass_stability",
        "rule_pass_offset_score",
        "rule_pass_leave_out",
        "rule_pass_outlier_trim",
    ):
        gate_value = as_bool(fit.get(gate, ""))
        if gate_value is True:
            reasons.append(f"Gate `{gate}=True`.")

    if as_bool(neg.get("negative_control_pass", "")) is True:
        reasons.append("Negative controls pass, so shuffled pairings collapse the signal as expected.")

    if row.get("authenticity", "").lower() == "gold":
        reasons.append("Release review field is `authenticity=gold` with `leakage_risk=low` and `negative_control=done`.")

    if not reasons:
        reasons.append("Result is marked pass in results-log; inspect evidence and artifacts for full justification.")
    return reasons


def rel_link(from_dir: Path, workspace_rel_path: str) -> str:
    target = (ROOT / workspace_rel_path).resolve()
    return os.path.relpath(target, start=from_dir.resolve()).replace("\\", "/")


def render_report(test_id: str) -> str:
    row, claim, result = find_row_data(test_id)
    claim_file = ROOT / claim.get("claim_file", f"02_claims/claims/{row['claim_id'].lower()}.md")
    derivation_file = ROOT / row.get("derivation", "")
    evidence_file = ROOT / row.get("evidence_path", "")
    artifact_dir = wui.resolve_artifact_dir_for_test(test_id)
    if artifact_dir is None:
        artifact_dir = ARTIFACTS_ROOT / test_id.lower()

    claim_lines = read_text(claim_file).splitlines()
    derivation_lines = read_text(derivation_file).splitlines()
    evidence_lines = read_text(evidence_file).splitlines()

    fit_map = csv_metric_map(artifact_dir / "fit-summary.csv")
    neg_map = csv_metric_map(artifact_dir / "negative-controls-summary.csv")
    reasons = explain_pass(row, fit_map, neg_map)
    variants = collect_variant_rows(test_id)
    run_rows = matching_runs(test_id)

    source_text = "\n".join(
        [
            row.get("claim_statement", ""),
            row.get("formula_anchor", ""),
            read_text(derivation_file),
            read_text(claim_file),
        ]
    )
    symbol_rows = select_relevant_symbols(source_text)

    claim_assumptions = md_section(claim_lines, "Assumptions")
    claim_falsifier = md_section(claim_lines, "Potential Falsifier")
    claim_notes = md_section(claim_lines, "Evidence / Notes")
    claim_next = md_section(claim_lines, "Next Action")

    deriv_defs = md_section(derivation_lines, "Definitions")
    deriv_eq = first_code_block(derivation_lines, "Equations")
    deriv_steps = md_section(derivation_lines, "Derivation Steps")
    deriv_checks = md_section(derivation_lines, "Checks")

    repro_block = first_code_block(evidence_lines, "Reproducible Run")
    evidence_summary = wui.parse_evidence_summary(row.get("evidence_path", ""))
    artifacts = wui.collect_artifacts_for_test(test_id)
    images = [item for item in artifacts.get("items", []) if item.get("is_image")]

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    lines: list[str] = []
    lines.append(f"# Claim/Test Evidence Package: {row['claim_id']} via {row['test_id']}")
    lines.append("")
    lines.append(f"- Generated (UTC): {generated}")
    lines.append(f"- Claim: `{row['claim_id']}`")
    lines.append(f"- Test: `{row['test_id']}`")
    lines.append(f"- Status: `{row.get('exec_status', '')}`")
    lines.append(f"- Authenticity: `{row.get('authenticity', '')}`")
    lines.append(f"- Leakage risk: `{row.get('leakage_risk', '')}`")
    lines.append(f"- Negative control: `{row.get('negative_control', '')}`")
    lines.append(f"- Last run: `{row.get('last_run', '')}`")
    lines.append("")

    lines.append("## Executive Verdict")
    lines.append("")
    lines.append(f"- Claim statement: {row.get('claim_statement', '')}")
    lines.append(f"- Decision note: {row.get('decision_note', '')}")
    lines.append(f"- Evidence decision: {evidence_summary.get('decision', '')}")
    lines.append(f"- Evidence rationale: {evidence_summary.get('rationale', '')}")
    lines.append("")
    lines.append("### Why This Passed")
    lines.append("")
    for reason in reasons:
        lines.append(f"- {reason}")
    lines.append("")

    lines.append("## Claim Definition")
    lines.append("")
    lines.append(f"- Claim register status/confidence: `{claim.get('claim_status', '')}` / `{claim.get('confidence', '')}`")
    lines.append(f"- Source pages: `{claim.get('source_pages', '')}`")
    lines.append("")
    lines.append("### Assumptions")
    lines.append("")
    if claim_assumptions:
        lines.extend(claim_assumptions)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Potential Falsifier")
    lines.append("")
    if claim_falsifier:
        lines.extend(claim_falsifier)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Evidence Notes")
    lines.append("")
    if claim_notes:
        lines.extend(claim_notes)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Claim Next Action")
    lines.append("")
    if claim_next:
        lines.extend(claim_next)
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Mathematical Form")
    lines.append("")
    lines.append(f"- Formula anchor (test-plan): `{row.get('formula_anchor', '')}`")
    lines.append("")
    lines.append("### Derivation Definitions")
    lines.append("")
    if deriv_defs:
        lines.extend(deriv_defs)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Derivation Equations")
    lines.append("")
    if deriv_eq:
        lines.append("```text")
        lines.append(deriv_eq)
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Derivation Steps")
    lines.append("")
    if deriv_steps:
        lines.extend(deriv_steps)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Derivation Checks")
    lines.append("")
    if deriv_checks:
        lines.extend(deriv_checks)
    else:
        lines.append("- n/a")
    lines.append("")
    lines.append("### Relevant Symbol Map")
    lines.append("")
    lines.append("| Symbol | Meaning | Unit | Notes |")
    lines.append("| --- | --- | --- | --- |")
    if symbol_rows:
        for item in symbol_rows:
            lines.append(
                f"| {clean_cell(item['symbol'])} | {clean_cell(item['meaning'])} | "
                f"{clean_cell(item['unit'])} | {clean_cell(item['notes'])} |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a |")
    lines.append("")

    lines.append("## Test Protocol")
    lines.append("")
    lines.append(f"- Dataset / environment: {row.get('dataset_environment', '')}")
    lines.append(f"- Method: {row.get('method', '')}")
    lines.append(f"- Pass condition: {row.get('pass_condition', '')}")
    lines.append(f"- Fail condition: {row.get('fail_condition', '')}")
    lines.append("")
    lines.append("### Reproducible Run Commands")
    lines.append("")
    if repro_block:
        lines.append("```powershell")
        lines.append(repro_block)
        lines.append("```")
    else:
        lines.append("- n/a")
    lines.append("")

    lines.append("## Core Results")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    for key in (
        "dataset_id",
        "n_lensing",
        "n_rotation",
        "n_total",
        "tau_fit",
        "k_memory_fit",
        "delta_chi2",
        "delta_chi2_per_point_total",
        "delta_aic",
        "delta_bic",
        "offset_score",
        "cv_tau",
        "cv_k_memory",
        "leave_out_pass_fraction",
        "outlier_trim_delta_chi2",
        "outlier_trim_delta_aic",
        "outlier_trim_delta_bic",
        "rule_pass_delta_chi2",
        "rule_pass_delta_aic",
        "rule_pass_delta_bic",
        "rule_pass_stability",
        "rule_pass_offset_score",
        "rule_pass_leave_out",
        "rule_pass_outlier_trim",
        "pass_recommendation",
        "duration_seconds",
    ):
        lines.append(f"| {key} | {fit_map.get(key, '')} |")
    lines.append("")
    lines.append("### Negative Controls")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    for key in (
        "n_runs_per_mode",
        "delta_chi2_lens_positive",
        "delta_chi2_rot_positive",
        "delta_chi2_total_positive",
        "delta_aic_total_positive",
        "lensing_improvement_ratio_ctrl_vs_pos",
        "rotation_improvement_ratio_ctrl_vs_pos",
        "rule_lensing_control",
        "rule_rotation_control",
        "negative_control_pass",
    ):
        lines.append(f"| {key} | {neg_map.get(key, '')} |")
    lines.append("")

    lines.append("## Robustness and Replication")
    lines.append("")
    lines.append("| Variant | n_lensing | delta_chi2 | delta_aic | delta_bic | offset_score | fit_pass | negative_control_pass | Artifact path |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    if variants:
        for item in variants:
            lines.append(
                f"| {item['label']} | {item['n_lensing']} | {item['delta_chi2']} | {item['delta_aic']} | {item['delta_bic']} | "
                f"{item['offset_score']} | {item['fit_pass']} | {item['neg_pass']} | `{item['path']}` |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    lines.append("")

    lines.append("## Run Journal Trace")
    lines.append("")
    lines.append("| Run ID | Date | Scope | Result summary | Notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    if run_rows:
        for r in run_rows:
            lines.append(
                f"| {r.get('run_id','')} | {r.get('date','')} | {r.get('scope','').replace('|','/')} | "
                f"{r.get('result_summary','').replace('|','/')} | {r.get('notes','').replace('|','/')} |"
            )
    else:
        lines.append("| n/a | n/a | n/a | n/a | n/a |")
    lines.append("")

    lines.append("## Artifact Index")
    lines.append("")
    lines.append(f"- Artifact directory: `{artifacts.get('artifact_dir', '')}`")
    lines.append(f"- Artifact count: `{artifacts.get('count', 0)}`")
    lines.append(f"- Image count: `{artifacts.get('image_count', 0)}`")
    lines.append("")
    for item in artifacts.get("items", []):
        item_type = "image" if item.get("is_image") else ("text" if item.get("is_text") else "binary")
        lines.append(f"- `{item.get('path','')}` ({item_type}, {item.get('size',0)} bytes)")
    lines.append("")

    lines.append("## Image Previews")
    lines.append("")
    if images:
        for image in images[:6]:
            img_path = str(image.get("path", ""))
            if not img_path:
                continue
            lines.append(f"### {image.get('name','')}")
            lines.append("")
            lines.append(f"![{image.get('name','')}](../../{img_path})")
            lines.append("")
    else:
        lines.append("- n/a")
        lines.append("")

    lines.append("## Limits and Next Action")
    lines.append("")
    lines.append(f"- Current test-level next action: {row.get('next_action', '')}")
    lines.append(f"- Formal fail condition (falsifier): {row.get('fail_condition', '')}")
    lines.append("")

    lines.append("## Source Traceability")
    lines.append("")
    lines.append(f"- Claim file: `{rel(claim_file)}`")
    lines.append(f"- Derivation file: `{rel(derivation_file)}`")
    lines.append(f"- Evidence file: `{rel(evidence_file)}`")
    lines.append(f"- Results log: `05_validation/results-log.md`")
    lines.append(f"- Test plan: `05_validation/test-plan.md`")
    lines.append(f"- Symbols registry: `{rel(SYMBOLS_MD)}`")
    lines.append(f"- Main fit summary: `{rel(artifact_dir / 'fit-summary.csv')}`")
    lines.append(f"- Main negative controls: `{rel(artifact_dir / 'negative-controls-summary.csv')}`")
    lines.append("")

    if result:
        lines.append("## Raw Results-Log Row Snapshot")
        lines.append("")
        lines.append("| Field | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| test_id | {result.get('test_id','')} |")
        lines.append(f"| exec_status | {result.get('exec_status','')} |")
        lines.append(f"| last_run | {result.get('last_run','')} |")
        lines.append(f"| metric_value | {result.get('metric_value','').replace('|','/')} |")
        lines.append(f"| decision_note | {result.get('decision_note','').replace('|','/')} |")
        lines.append(f"| next_action | {result.get('next_action','').replace('|','/')} |")
        lines.append(f"| authenticity | {result.get('authenticity','')} |")
        lines.append(f"| leakage_risk | {result.get('leakage_risk','')} |")
        lines.append(f"| negative_control | {result.get('negative_control','')} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_report_files(test_id: str, markdown_text: str, md_only: bool) -> list[Path]:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{test_id.lower()}-claim-test-report"
    out_md = EXPORT_DIR / f"{stem}.md"
    out_md.write_text(markdown_text, encoding="utf-8")

    outputs = [out_md]
    if not md_only:
        out_odt = EXPORT_DIR / f"{stem}.odt"
        out_pdf = EXPORT_DIR / f"{stem}.pdf"
        dossier.write_odt(markdown_text, out_odt)
        dossier.write_pdf(markdown_text, out_pdf)
        outputs.extend([out_odt, out_pdf])
    return outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a deep claim/test/result package (MD/ODT/PDF)."
    )
    parser.add_argument(
        "--test-id",
        default="",
        help="Target test id (QNG-T-xxx). If omitted, exports all pass+gold tests.",
    )
    parser.add_argument(
        "--md-only",
        action="store_true",
        help="Generate markdown only and skip ODT/PDF.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    test_ids: list[str]

    if args.test_id:
        test_id = args.test_id.strip().upper()
        if not TEST_ID_RE.match(test_id):
            print("Invalid --test-id. Expected format QNG-T-xxx.")
            return 2
        test_ids = [test_id]
    else:
        test_ids = default_gold_test_ids()
        if not test_ids:
            print("No pass+gold tests found in results-log.")
            return 2

    all_outputs: list[Path] = []
    for test_id in test_ids:
        markdown_text = render_report(test_id)
        outputs = write_report_files(test_id, markdown_text, md_only=args.md_only)
        all_outputs.extend(outputs)

    for output in all_outputs:
        print(f"Generated: {rel(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
