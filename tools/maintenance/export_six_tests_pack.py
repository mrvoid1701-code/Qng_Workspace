#!/usr/bin/env python3
"""
Export one consolidated package for six completed tests.

Outputs:
- 07_exports/claim-packages/qng-six-tests-pack-YYYY-MM-DD.md
- 07_exports/claim-packages/qng-six-tests-pack-YYYY-MM-DD.odt
- 07_exports/claim-packages/qng-six-tests-pack-YYYY-MM-DD.pdf
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import export_full_theory_dossier as dossier
import workspace_ui as wui


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "07_exports" / "claim-packages"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"

DEFAULT_TEST_IDS = [
    "QNG-T-TAUMAP-001",
    "QNG-T-UNIFY-001",
    "QNG-T-HYST-001",
    "QNG-T-GEODESIC-001",
    "QNG-T-GRSWEEP-001",
    "QNG-T-TRJ-CTRL-001",
]

KEY_METRICS_ORDER = [
    "delta_chi2",
    "delta_chi2_one_vs_base",
    "delta_aic",
    "delta_aic_one_vs_base",
    "delta_bic",
    "delta_bic_one_vs_base",
    "global_tau_median",
    "tau_hat",
    "lambda_global",
    "n_science_events",
    "geometry_pearson_abs",
    "geometry_perm_p",
    "orientation_p",
    "segment_p",
    "directionality_randomized_median",
    "control_mean_abs_over_sigma",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def normalize_ids(values: list[str]) -> list[str]:
    ids = [v.strip().upper() for v in values if v.strip()]
    dedup: list[str] = []
    seen: set[str] = set()
    for test_id in ids:
        if test_id in seen:
            continue
        dedup.append(test_id)
        seen.add(test_id)
    return dedup


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def read_csv_map(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists() or not path.is_file():
        return out
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        for i, row in enumerate(reader):
            if not row or len(row) < 2:
                continue
            if i == 0 and row[0].strip().lower() == "metric":
                continue
            key = row[0].strip()
            value = row[1].strip()
            if key:
                out[key] = value
    return out


def parse_per_test_rows() -> dict[str, dict[str, str]]:
    lines = RESULTS_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
    in_section = False
    headers: list[str] = []
    rows: dict[str, dict[str, str]] = {}

    for line in lines:
        stripped = line.strip()
        if stripped == "## Per-Test Status":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        cells = wui.split_md_row(line)
        if not cells:
            continue
        if wui.is_separator_row(cells):
            continue
        if not headers:
            headers = [c.strip() for c in cells]
            continue
        if len(cells) != len(headers):
            continue
        row = {headers[i]: cells[i].strip() for i in range(len(headers))}
        test_id = row.get("Test ID", "").strip()
        if test_id:
            rows[test_id] = row
    return rows


def latest_task_report(test_id: str) -> Path | None:
    reports_dir = ROOT / "07_exports" / "reports"
    slug = test_id.lower()
    candidates = sorted(reports_dir.glob(f"{slug}-*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def pick_key_metrics(fit_map: dict[str, str], limit: int = 10) -> list[tuple[str, str]]:
    selected: list[tuple[str, str]] = []
    seen: set[str] = set()

    for key in KEY_METRICS_ORDER:
        value = fit_map.get(key, "")
        if value == "":
            continue
        selected.append((key, value))
        seen.add(key)
        if len(selected) >= limit:
            return selected

    for key in sorted(fit_map.keys()):
        if key in seen:
            continue
        if key.startswith("rule_pass_"):
            continue
        selected.append((key, fit_map[key]))
        if len(selected) >= limit:
            break
    return selected


def build_markdown(test_ids: list[str]) -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    per_test_rows = parse_per_test_rows()

    lines: list[str] = []
    lines.append("# QNG Six-Tests Consolidated Package")
    lines.append("")
    lines.append(f"- Generated (UTC): {generated}")
    lines.append("- Scope: one clean export for the six completed tests requested.")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Test ID | Status | Authenticity | Leakage | Negative control | Last run |")
    lines.append("| --- | --- | --- | --- | --- | --- |")

    test_data: list[dict[str, Any]] = []
    for test_id in test_ids:
        slug = test_id.lower()
        manifest_path = ROOT / "05_validation" / "run-manifests" / f"{slug}.json"
        evidence_path = ROOT / "05_validation" / "evidence" / f"{slug}.md"
        artifact_dir = ROOT / "05_validation" / "evidence" / "artifacts" / slug
        fit_path = artifact_dir / "fit-summary.csv"
        prereg_path = ROOT / "05_validation" / "pre-registrations" / f"{slug}.md"
        report_path = latest_task_report(test_id)

        manifest = read_json(manifest_path)
        fit_map = read_csv_map(fit_path)
        row = per_test_rows.get(test_id, {})

        status = row.get("Exec status", manifest.get("status", ""))
        auth = row.get("authenticity", "")
        leak = row.get("leakage_risk", "")
        neg = row.get("negative_control", "")
        last_run = row.get("Last run", manifest.get("decision", {}).get("date", ""))

        lines.append(f"| {test_id} | {status} | {auth} | {leak} | {neg} | {last_run} |")

        test_data.append(
            {
                "test_id": test_id,
                "manifest_path": manifest_path,
                "manifest": manifest,
                "evidence_path": evidence_path,
                "artifact_dir": artifact_dir,
                "fit_path": fit_path,
                "fit_map": fit_map,
                "prereg_path": prereg_path,
                "report_path": report_path,
                "results_row": row,
            }
        )

    lines.append("")
    lines.append("## Detailed Test Records")
    lines.append("")

    for item in test_data:
        test_id = item["test_id"]
        manifest = item["manifest"]
        fit_map = item["fit_map"]
        row = item["results_row"]

        lines.append(f"## {test_id}")
        lines.append("")
        lines.append("### Core Identity")
        lines.append("")
        lines.append(f"- Claim ID: `{manifest.get('claim_id', '')}`")
        lines.append(f"- Claim statement: {manifest.get('claim_statement', '')}")
        lines.append(f"- Priority: `{manifest.get('priority', '')}`")
        lines.append(f"- Decision: `{manifest.get('decision', {}).get('result', row.get('Exec status', ''))}`")
        lines.append(f"- Decision note: {manifest.get('decision', {}).get('note', row.get('Decision note', ''))}")
        lines.append("")

        lines.append("### Mathematical Form")
        lines.append("")
        lines.append(f"- Derivation path: `{manifest.get('derivation_path', '')}`")
        lines.append(f"- Formula anchor: `{manifest.get('formula_anchor', '')}`")
        lines.append(f"- Physical dataset: {manifest.get('dataset', '')}")
        lines.append(f"- Method: {manifest.get('method', '')}")
        lines.append("")

        lines.append("### Falsifier / Gate Logic")
        lines.append("")
        lines.append(f"- Pass condition: {manifest.get('pass_condition', '')}")
        lines.append(f"- Fail condition: {manifest.get('fail_condition', '')}")
        lines.append("")

        lines.append("### Key Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | --- |")
        selected = pick_key_metrics(fit_map, limit=12)
        if selected:
            for key, value in selected:
                lines.append(f"| {key} | {value} |")
        else:
            lines.append("| n/a | n/a |")
        lines.append("")

        rule_keys = sorted(k for k in fit_map.keys() if k.startswith("rule_pass_"))
        if rule_keys:
            lines.append("### Registered Gates")
            lines.append("")
            lines.append("| Gate | Value |")
            lines.append("| --- | --- |")
            for key in rule_keys:
                lines.append(f"| {key} | {fit_map.get(key, '')} |")
            lines.append("")

        lines.append("### Repro / Traceability")
        lines.append("")
        lines.append(f"- Run manifest: `{rel(item['manifest_path'])}`")
        lines.append(f"- Evidence page: `{rel(item['evidence_path'])}`")
        lines.append(f"- Preregistration: `{rel(item['prereg_path'])}`")
        lines.append(f"- Fit summary: `{rel(item['fit_path'])}`")
        lines.append(f"- Artifact directory: `{rel(item['artifact_dir'])}`")
        if item["report_path"] is not None:
            lines.append(f"- Task report: `{rel(item['report_path'])}`")
        lines.append("")

        lines.append("### Next Action")
        lines.append("")
        next_action = row.get("Next action", "")
        if not next_action:
            next_action = "Keep lock/gates unchanged and re-run only on new out-of-sample data."
        lines.append(f"- {next_action}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(
        description="Export one consolidated MD/ODT/PDF package for six completed tests."
    )
    parser.add_argument(
        "--tests",
        default=",".join(DEFAULT_TEST_IDS),
        help="Comma-separated test ids. Default is the six completed tests.",
    )
    parser.add_argument(
        "--stem",
        default=f"qng-six-tests-pack-{today}",
        help="Output filename stem (without extension).",
    )
    parser.add_argument(
        "--md-only",
        action="store_true",
        help="Generate markdown only and skip ODT/PDF.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    test_ids = normalize_ids(args.tests.split(","))
    if not test_ids:
        raise ValueError("No test ids provided.")

    markdown_text = build_markdown(test_ids)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    out_md = OUT_DIR / f"{args.stem}.md"
    out_md.write_text(markdown_text, encoding="utf-8")
    outputs = [out_md]

    if not args.md_only:
        out_odt = OUT_DIR / f"{args.stem}.odt"
        out_pdf = OUT_DIR / f"{args.stem}.pdf"
        dossier.write_odt(markdown_text, out_odt)
        dossier.write_pdf(markdown_text, out_pdf)
        outputs.extend([out_odt, out_pdf])

    for path in outputs:
        print(f"Generated: {rel(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

