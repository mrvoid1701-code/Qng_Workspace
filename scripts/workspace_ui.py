#!/usr/bin/env python3
"""
Local workspace UI server for QNG.

Features:
- Serves static frontend from ./ui
- JSON API for browsing, reading, and saving text files
- Mission/workbench/graph endpoints for workflow control
- Controlled status update endpoint for validation tests
- System action endpoints (lint/sync/export)
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import csv
import json
import mimetypes
import os
import re
import socket
import subprocess
import sys
import time


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
UI_ROOT = WORKSPACE_ROOT / "ui"
IGNORED_DIRS = {".venv", ".git", "__pycache__"}
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".ps1",
    ".json",
    ".yaml",
    ".yml",
    ".csv",
    ".toml",
    ".tex",
    ".html",
    ".css",
    ".js",
    ".svg",
    ".xml",
}

CLAIMS_REGISTER = WORKSPACE_ROOT / "02_claims" / "claims-register.md"
TEST_PLAN = WORKSPACE_ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = WORKSPACE_ROOT / "05_validation" / "results-log.md"
PARAMETER_REGISTRY = WORKSPACE_ROOT / "04_models" / "parameter-registry.json"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_ID_RE = re.compile(r"^QNG-C-\d{3}$")
CLAIM_CELL_RE = re.compile(r"^(QNG-C-\d{3})\s*:\s*(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_EXEC_STATUS = {
    "queued-p1",
    "queued-p2",
    "queued-p3",
    "in-progress",
    "pass",
    "fail",
    "blocked",
}
AUTHENTICITY_LEVELS = {"gold", "silver", "bronze"}
LEAKAGE_RISK_LEVELS = {"low", "med", "high"}
NEGATIVE_CONTROL_STATES = {"none", "planned", "done"}
DEFAULT_EXEC_BY_PRIORITY = {
    "P1": "queued-p1",
    "P2": "queued-p2",
    "P3": "queued-p3",
}
SYSTEM_ACTIONS = {
    "lint": "scripts/lint_workspace.py",
    "sync": "scripts/sync_workspace.py",
    "export": "scripts/export_validated_writing.py",
}
ARTIFACTS_ROOT = WORKSPACE_ROOT / "05_validation" / "evidence" / "artifacts"
EXPORT_ROOT = WORKSPACE_ROOT / "07_exports"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def ensure_inside(path: Path, root: Path) -> bool:
    base = root.resolve()
    try:
        path.resolve().relative_to(base)
        return True
    except ValueError:
        return False


def resolve_relative_path(relative_path: str) -> Path:
    normalized = relative_path.replace("\\", "/").strip()
    normalized = normalized.lstrip("/")
    target = (WORKSPACE_ROOT / normalized).resolve()
    if not ensure_inside(target, WORKSPACE_ROOT):
        raise ValueError("Path escapes workspace")
    return target


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.suffix == ""


def build_tree(path: Path, relative_prefix: str = "") -> list[dict]:
    entries: list[dict] = []
    for child in path.iterdir():
        if child.name in IGNORED_DIRS:
            continue
        rel_path = f"{relative_prefix}/{child.name}".lstrip("/")
        info = {
            "name": child.name,
            "path": rel_path,
            "mtime": int(child.stat().st_mtime),
        }
        if child.is_dir():
            info["type"] = "dir"
            info["children"] = build_tree(child, rel_path)
        else:
            info["type"] = "file"
            info["size"] = child.stat().st_size
            info["editable"] = is_text_file(child)
        entries.append(info)

    def sort_key(item: dict) -> tuple[int, str]:
        return (0 if item["type"] == "dir" else 1, item["name"].lower())

    return sorted(entries, key=sort_key)


def parse_json_body(handler: BaseHTTPRequestHandler) -> dict:
    raw_length = handler.headers.get("Content-Length", "0")
    try:
        length = int(raw_length)
    except ValueError:
        length = 0
    raw = handler.rfile.read(length) if length > 0 else b""
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def split_md_row(line: str) -> list[str]:
    raw = line.strip()
    if not raw.startswith("|") or not raw.endswith("|"):
        return []
    body = raw[1:-1]
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            cur.append(body[i + 1])
            i += 2
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def sanitize_inline(value: object) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "/").strip()


def join_md_row(cells: list[str]) -> str:
    return "| " + " | ".join(sanitize_inline(c) for c in cells) + " |"


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(TABLE_SEPARATOR_RE.match(c.strip()) for c in cells)


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def write_lines(path: Path, lines: list[str]) -> None:
    content = "\n".join(lines).rstrip("\n") + "\n"
    path.write_text(content, encoding="utf-8")


def to_workspace_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(WORKSPACE_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def parse_markdown_section(lines: list[str], title: str) -> str:
    heading = f"## {title}"
    start = -1
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start < 0:
        return ""

    chunks: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped:
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        chunks.append(stripped)
    return " ".join(chunks).strip()


def parse_evidence_summary(evidence_rel_path: str) -> dict:
    if not evidence_rel_path:
        return {
            "objective": "",
            "method": "",
            "decision": "",
            "rationale": "",
            "last_updated": "",
        }
    try:
        evidence_path = resolve_relative_path(evidence_rel_path)
    except ValueError:
        return {
            "objective": "",
            "method": "",
            "decision": "",
            "rationale": "",
            "last_updated": "",
        }
    if not evidence_path.exists():
        return {
            "objective": "",
            "method": "",
            "decision": "",
            "rationale": "",
            "last_updated": "",
        }

    lines = evidence_path.read_text(encoding="utf-8", errors="replace").splitlines()
    decision = ""
    rationale = ""
    last_updated = ""
    for line in lines:
        if line.startswith("- Decision: "):
            decision = line[len("- Decision: ") :].strip()
        elif line.startswith("- Rationale: "):
            rationale = line[len("- Rationale: ") :].strip()
        elif line.startswith("- Last updated: "):
            last_updated = line[len("- Last updated: ") :].strip()

    return {
        "objective": parse_markdown_section(lines, "Objective"),
        "method": parse_markdown_section(lines, "Method"),
        "decision": decision,
        "rationale": rationale,
        "last_updated": last_updated,
    }


def parse_metric_rows_from_csv(csv_path: Path) -> list[dict]:
    if not csv_path.exists() or not csv_path.is_file():
        return []
    rows: list[dict] = []
    with csv_path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        for i, row in enumerate(reader):
            if i == 0 and row and row[0].strip().lower() == "metric":
                continue
            if len(row) < 2:
                continue
            metric = row[0].strip()
            value = row[1].strip()
            if not metric:
                continue
            rows.append({"metric": metric, "value": value})
    return rows


def metric_map_from_csv(csv_path: Path) -> dict[str, str]:
    return {row["metric"]: row["value"] for row in parse_metric_rows_from_csv(csv_path)}


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _artifact_quality_score(path: Path, test_slug: str) -> tuple[int, int, str]:
    fit_map = metric_map_from_csv(path / "fit-summary.csv")
    neg_map = metric_map_from_csv(path / "negative-controls-summary.csv")
    score = 0

    if fit_map:
        score += 100
        if fit_map.get("pass_recommendation", "").strip().lower() == "pass":
            score += 40
        for gate in (
            "rule_pass_delta_chi2",
            "rule_pass_delta_aic",
            "rule_pass_delta_bic",
            "rule_pass_stability",
            "rule_pass_offset_score",
            "rule_pass_leave_out",
            "rule_pass_outlier_trim",
        ):
            if _is_true(fit_map.get(gate, "")):
                score += 5

    if neg_map:
        score += 30
        if _is_true(neg_map.get("negative_control_pass", "")):
            score += 20

    if path.name == f"{test_slug}-direct":
        score += 15
    elif path.name == test_slug:
        score += 5

    return (score, int(path.stat().st_mtime), path.name.lower())


def resolve_artifact_dir_for_test(test_id: str) -> Path | None:
    test_slug = test_id.lower().strip()
    candidates: list[Path] = []

    exact = ARTIFACTS_ROOT / test_slug
    if exact.exists() and exact.is_dir():
        candidates.append(exact)

    for path in ARTIFACTS_ROOT.glob(f"{test_slug}-*"):
        if path.is_dir():
            candidates.append(path)

    if not candidates:
        return None

    return max(candidates, key=lambda path: _artifact_quality_score(path, test_slug))


def collect_artifacts_for_test(test_id: str) -> dict:
    artifact_dir = resolve_artifact_dir_for_test(test_id)
    items: list[dict] = []
    if artifact_dir and artifact_dir.exists() and artifact_dir.is_dir():
        for path in sorted(artifact_dir.iterdir(), key=lambda p: p.name.lower()):
            if not path.is_file():
                continue
            content_type, _ = mimetypes.guess_type(path.name)
            suffix = path.suffix.lower()
            is_image = suffix in IMAGE_SUFFIXES
            item = {
                "name": path.name,
                "path": to_workspace_relative(path),
                "size": path.stat().st_size,
                "mtime": int(path.stat().st_mtime),
                "content_type": content_type or "application/octet-stream",
                "is_image": is_image,
                "is_text": is_text_file(path),
            }
            items.append(item)

    hero_image = next((item["path"] for item in items if item["is_image"]), "")
    fit_summary_path = artifact_dir / "fit-summary.csv" if artifact_dir else None
    metrics = parse_metric_rows_from_csv(fit_summary_path) if fit_summary_path else []
    metric_map = {row["metric"]: row["value"] for row in metrics}

    return {
        "artifact_dir": to_workspace_relative(artifact_dir) if artifact_dir else "",
        "items": items,
        "count": len(items),
        "image_count": sum(1 for item in items if item["is_image"]),
        "hero_image_path": hero_image,
        "fit_summary_path": to_workspace_relative(fit_summary_path) if fit_summary_path and fit_summary_path.exists() else "",
        "metrics": metrics,
        "pass_recommendation": metric_map.get("pass_recommendation", ""),
    }


def build_results_data(priority_filter: str, status_filter: str, query_text: str) -> dict:
    claims = parse_claims_register()
    tests = parse_test_plan()
    results = parse_results_per_test()
    test_rows = combine_test_rows(tests, results)
    claims_by_id = {c["claim_id"]: c for c in claims}

    query = query_text.strip().lower()
    filtered_rows: list[dict] = []
    for row in test_rows:
        if priority_filter and row["priority"] != priority_filter:
            continue
        if status_filter and row["exec_status"] != status_filter:
            continue
        if query:
            haystack = " ".join(
                [
                    row["test_id"],
                    row["claim_id"],
                    row["claim_statement"],
                    row["formula_anchor"],
                    row["dataset_environment"],
                    row["metric_value"],
                    row["decision_note"],
                    row["exec_status"],
                    row["authenticity"],
                    row["leakage_risk"],
                    row["negative_control"],
                ]
            ).lower()
            if query not in haystack:
                continue
        filtered_rows.append(row)

    priority_rank = {"P1": 0, "P2": 1, "P3": 2}
    filtered_rows.sort(key=lambda row: (priority_rank.get(row["priority"], 9), row["test_id"]))

    out_rows: list[dict] = []
    for row in filtered_rows:
        claim = claims_by_id.get(row["claim_id"], {})
        claim_statement = row["claim_statement"] or claim.get("statement", "")
        artifacts = collect_artifacts_for_test(row["test_id"])
        run_manifest_rel = f"05_validation/run-manifests/{row['test_id'].lower()}.json"
        run_manifest_path = resolve_relative_path(run_manifest_rel)

        out_rows.append(
            {
                "test_id": row["test_id"],
                "claim_id": row["claim_id"],
                "claim_statement": claim_statement,
                "priority": row["priority"],
                "exec_status": row["exec_status"],
                "last_run": row["last_run"],
                "metric_value": row["metric_value"],
                "decision_note": row["decision_note"],
                "next_action": row["next_action"],
                "authenticity": row["authenticity"],
                "leakage_risk": row["leakage_risk"],
                "negative_control": row["negative_control"],
                "evidence_path": row["evidence_path"],
                "derivation": row["derivation"],
                "artifact_dir": artifacts["artifact_dir"],
                "artifact_count": artifacts["count"],
                "image_count": artifacts["image_count"],
                "hero_image_path": artifacts["hero_image_path"],
                "fit_summary_path": artifacts["fit_summary_path"],
                "pass_recommendation": artifacts["pass_recommendation"],
                "run_manifest_path": run_manifest_rel,
                "run_manifest_exists": run_manifest_path.exists(),
            }
        )

    status_counts = Counter(row["exec_status"] for row in out_rows if row["exec_status"])
    all_status_counts = Counter(row["exec_status"] for row in test_rows if row["exec_status"])
    return {
        "generated_on": date.today().isoformat(),
        "filters": {
            "priority": priority_filter,
            "status": status_filter,
            "q": query_text,
        },
        "stats": {
            "tests_returned": len(out_rows),
            "tests_total": len(test_rows),
            "status_counts_filtered": dict(status_counts),
            "status_counts_total": dict(all_status_counts),
        },
        "tests": out_rows,
    }


def build_result_detail(test_id: str) -> dict:
    if not TEST_ID_RE.match(test_id):
        raise ValueError("Invalid test_id")

    claims = parse_claims_register()
    tests = parse_test_plan()
    results = parse_results_per_test()
    test_rows = combine_test_rows(tests, results)

    row = next((item for item in test_rows if item["test_id"] == test_id), None)
    if not row:
        raise ValueError(f"Unknown test_id: {test_id}")

    claims_by_id = {c["claim_id"]: c for c in claims}
    claim = claims_by_id.get(row["claim_id"], {})
    claim_statement = row["claim_statement"] or claim.get("statement", "")

    evidence_summary = parse_evidence_summary(row["evidence_path"])
    artifacts = collect_artifacts_for_test(row["test_id"])
    metric_map = {entry["metric"]: entry["value"] for entry in artifacts["metrics"]}

    run_manifest_rel = f"05_validation/run-manifests/{row['test_id'].lower()}.json"
    run_manifest_path = resolve_relative_path(run_manifest_rel)

    return {
        "generated_on": date.today().isoformat(),
        "test": {
            "test_id": row["test_id"],
            "claim_id": row["claim_id"],
            "claim_statement": claim_statement,
            "claim_file": claim.get("claim_file", ""),
            "priority": row["priority"],
            "exec_status": row["exec_status"],
            "last_run": row["last_run"],
            "metric_value": row["metric_value"],
            "decision_note": row["decision_note"],
            "next_action": row["next_action"],
            "authenticity": row["authenticity"],
            "leakage_risk": row["leakage_risk"],
            "negative_control": row["negative_control"],
            "formula_anchor": row["formula_anchor"],
            "dataset_environment": row["dataset_environment"],
            "method": row["method"],
            "pass_condition": row["pass_condition"],
            "fail_condition": row["fail_condition"],
            "evidence_path": row["evidence_path"],
            "derivation": row["derivation"],
        },
        "evidence": {
            "objective": evidence_summary["objective"],
            "method": evidence_summary["method"],
            "decision": evidence_summary["decision"],
            "rationale": evidence_summary["rationale"],
            "last_updated": evidence_summary["last_updated"],
        },
        "artifacts": artifacts["items"],
        "artifact_dir": artifacts["artifact_dir"],
        "metrics": artifacts["metrics"],
        "metric_map": metric_map,
        "run_manifest": {
            "path": run_manifest_rel,
            "exists": run_manifest_path.exists(),
        },
    }


def parse_claim_cell(cell: str) -> tuple[str, str]:
    value = cell.strip()
    m = CLAIM_CELL_RE.match(value)
    if m:
        return m.group(1), m.group(2)
    if CLAIM_ID_RE.match(value):
        return value, ""
    return "", value


def locate_table(lines: list[str], header_prefix: str) -> tuple[int, int]:
    for i, line in enumerate(lines):
        if line.strip().startswith(header_prefix):
            row_start = i + 1
            while row_start < len(lines):
                cells = split_md_row(lines[row_start])
                if not cells:
                    break
                if is_separator_row(cells):
                    row_start += 1
                    continue
                break
            row_end = row_start
            while row_end < len(lines) and lines[row_end].strip().startswith("|"):
                row_end += 1
            return row_start, row_end
    return -1, -1


def parse_claims_register() -> list[dict]:
    rows: list[dict] = []
    for line in read_lines(CLAIMS_REGISTER):
        cells = split_md_row(line)
        if len(cells) != 6:
            continue
        claim_id = cells[0]
        if not CLAIM_ID_RE.match(claim_id):
            continue
        rows.append(
            {
                "claim_id": claim_id,
                "statement": cells[1],
                "claim_status": cells[2],
                "confidence": cells[3],
                "source_pages": cells[4],
                "derivation": cells[5],
                "claim_file": f"02_claims/claims/{claim_id.lower()}.md",
            }
        )
    return rows


def parse_test_plan() -> list[dict]:
    rows: list[dict] = []
    for line in read_lines(TEST_PLAN):
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        test_id = cells[0]
        if not TEST_ID_RE.match(test_id):
            continue
        claim_id, claim_statement = parse_claim_cell(cells[1])
        rows.append(
            {
                "test_id": test_id,
                "claim_id": claim_id,
                "claim_statement": claim_statement,
                "derivation": cells[2],
                "formula_anchor": cells[3],
                "dataset_environment": cells[4],
                "method": cells[5],
                "pass_condition": cells[6],
                "fail_condition": cells[7],
                "priority": cells[8],
                "plan_status": cells[9],
            }
        )
    return rows


def parse_results_per_test(lines: list[str] | None = None) -> list[dict]:
    source = lines if lines is not None else read_lines(RESULTS_LOG)
    start, end = locate_table(source, "| Test ID | Priority | Claim | Exec status |")
    if start < 0:
        return []

    rows: list[dict] = []
    for idx in range(start, end):
        cells = split_md_row(source[idx])
        if len(cells) not in {9, 12}:
            continue
        test_id = cells[0]
        if not TEST_ID_RE.match(test_id):
            continue
        claim_id, claim_statement = parse_claim_cell(cells[2])
        authenticity = cells[9].strip().lower() if len(cells) >= 12 else ""
        leakage_risk = cells[10].strip().lower() if len(cells) >= 12 else ""
        negative_control = cells[11].strip().lower() if len(cells) >= 12 else ""
        rows.append(
            {
                "test_id": test_id,
                "priority": cells[1],
                "claim_id": claim_id,
                "claim_statement": claim_statement,
                "exec_status": cells[3],
                "last_run": cells[4],
                "evidence_path": cells[5],
                "metric_value": cells[6],
                "decision_note": cells[7],
                "next_action": cells[8],
                "authenticity": authenticity,
                "leakage_risk": leakage_risk,
                "negative_control": negative_control,
                "line_index": idx,
            }
        )
    return rows


def parse_run_journal() -> list[dict]:
    lines = read_lines(RESULTS_LOG)
    start, end = locate_table(lines, "| Run ID | Date | Scope | Tests touched | Result summary | Notes |")
    if start < 0:
        return []

    rows: list[dict] = []
    for idx in range(start, end):
        cells = split_md_row(lines[idx])
        if len(cells) != 6:
            continue
        if not cells[0].startswith("RUN-"):
            continue
        rows.append(
            {
                "run_id": cells[0],
                "date": cells[1],
                "scope": cells[2],
                "tests_touched": cells[3],
                "result_summary": cells[4],
                "notes": cells[5],
            }
        )
    return rows


def parse_parameter_registry() -> list[dict]:
    if not PARAMETER_REGISTRY.exists():
        return []
    try:
        payload = json.loads(PARAMETER_REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    params = payload.get("parameters")
    if not isinstance(params, list):
        return []
    out: list[dict] = []
    for entry in params:
        if not isinstance(entry, dict):
            continue
        out.append(
            {
                "parameter_id": str(entry.get("parameter_id", "")).strip(),
                "symbol": str(entry.get("symbol", "")).strip(),
                "name": str(entry.get("name", "")).strip(),
                "status": str(entry.get("status", "")).strip(),
                "related_claims": [str(v) for v in entry.get("related_claims", []) if isinstance(v, str)],
            }
        )
    return out


def combine_test_rows(tests: list[dict], results: list[dict]) -> list[dict]:
    result_by_test = {r["test_id"]: r for r in results}
    merged: list[dict] = []
    for test in tests:
        result = result_by_test.get(test["test_id"])
        exec_status = (
            result["exec_status"]
            if result
            else DEFAULT_EXEC_BY_PRIORITY.get(test["priority"], "queued-p3")
        )
        merged.append(
            {
                "test_id": test["test_id"],
                "claim_id": test["claim_id"],
                "claim_statement": test["claim_statement"],
                "priority": test["priority"],
                "formula_anchor": test["formula_anchor"],
                "derivation": test["derivation"],
                "dataset_environment": test["dataset_environment"],
                "method": test["method"],
                "pass_condition": test["pass_condition"],
                "fail_condition": test["fail_condition"],
                "plan_status": test["plan_status"],
                "exec_status": exec_status,
                "last_run": result["last_run"] if result else "YYYY-MM-DD",
                "evidence_path": result["evidence_path"] if result else "",
                "metric_value": result["metric_value"] if result else "TODO",
                "decision_note": result["decision_note"] if result else "TODO",
                "next_action": result["next_action"] if result else "",
                "authenticity": (result["authenticity"] or "bronze") if result else "bronze",
                "leakage_risk": (result["leakage_risk"] or "high") if result else "high",
                "negative_control": (result["negative_control"] or "none") if result else "none",
            }
        )
    return merged


def evaluate_export_release_gate(test_rows: list[dict]) -> dict:
    pass_rows = [row for row in test_rows if row.get("exec_status") == "pass"]
    non_gold = [row["test_id"] for row in pass_rows if row.get("authenticity") != "gold"]
    return {
        "ready": len(pass_rows) > 0 and not non_gold,
        "pass_total": len(pass_rows),
        "gold_total": sum(1 for row in pass_rows if row.get("authenticity") == "gold"),
        "blocked_tests": non_gold,
    }

def build_mission_data() -> dict:
    claims = parse_claims_register()
    tests = parse_test_plan()
    results = parse_results_per_test()
    runs = parse_run_journal()

    claims_by_id = {c["claim_id"]: c for c in claims}
    test_rows = combine_test_rows(tests, results)
    for row in test_rows:
        if not row["claim_statement"]:
            row["claim_statement"] = claims_by_id.get(row["claim_id"], {}).get("statement", "")

    claims_by_status = Counter(c["claim_status"] for c in claims if c["claim_status"])
    claims_by_conf = Counter(c["confidence"] for c in claims if c["confidence"])
    tests_by_priority = Counter(t["priority"] for t in test_rows if t["priority"])
    tests_by_exec = Counter(t["exec_status"] for t in test_rows if t["exec_status"])
    pass_auth = Counter(t["authenticity"] for t in test_rows if t["exec_status"] == "pass" and t["authenticity"])

    release_gate = evaluate_export_release_gate(test_rows)

    priority_rank = {"P1": 0, "P2": 1, "P3": 2}
    queue_status = {"queued-p1", "queued-p2", "queued-p3", "in-progress"}
    queue = [t for t in test_rows if t["exec_status"] in queue_status]
    queue.sort(key=lambda row: (priority_rank.get(row["priority"], 9), row["test_id"]))

    p1_focus = [t for t in test_rows if t["priority"] == "P1"]
    p1_focus.sort(key=lambda row: row["test_id"])

    return {
        "generated_on": date.today().isoformat(),
        "summary": {
            "claims_total": len(claims),
            "tests_total": len(test_rows),
            "runs_total": len(runs),
            "claims_by_status": dict(claims_by_status),
            "claims_by_confidence": dict(claims_by_conf),
            "tests_by_priority": dict(tests_by_priority),
            "tests_by_exec_status": dict(tests_by_exec),
            "pass_by_authenticity": dict(pass_auth),
            "export_release": release_gate,
        },
        "p1_focus": p1_focus,
        "queue": queue[:24],
        "runs": runs[:12],
    }


def build_exports_data() -> dict:
    tests = parse_test_plan()
    results = parse_results_per_test()
    rows = combine_test_rows(tests, results)
    release_gate = evaluate_export_release_gate(rows)

    gold_rows = [row for row in rows if row["exec_status"] == "pass" and row["authenticity"] == "gold"]
    gold_rows.sort(key=lambda row: row["test_id"])

    gold_tests = [
        {
            "test_id": row["test_id"],
            "claim_id": row["claim_id"],
            "claim_statement": row["claim_statement"],
            "priority": row["priority"],
            "last_run": row["last_run"],
            "authenticity": row["authenticity"],
            "leakage_risk": row["leakage_risk"],
            "negative_control": row["negative_control"],
            "metric_value": row["metric_value"],
            "evidence_path": row["evidence_path"],
        }
        for row in gold_rows
    ]

    return {
        "generated_on": date.today().isoformat(),
        "release_gate": release_gate,
        "release_note": export_release_block_reason() if not release_gate["ready"] else "",
        "gold_tests": gold_tests,
        "recent_exports": list_recent_export_files(),
    }


def build_workbench_data(
    priority_filter: str,
    status_filter: str,
    query_text: str,
    claim_id_filter: str,
    test_id_filter: str,
) -> dict:
    claims = parse_claims_register()
    tests = parse_test_plan()
    results = parse_results_per_test()
    test_rows = combine_test_rows(tests, results)

    query = query_text.strip().lower()
    tests_by_claim: dict[str, list[dict]] = {}
    for test in test_rows:
        tests_by_claim.setdefault(test["claim_id"], []).append(test)

    filtered_tests: list[dict] = []
    for test in test_rows:
        if priority_filter and test["priority"] != priority_filter:
            continue
        if status_filter and test["exec_status"] != status_filter:
            continue
        if claim_id_filter and test["claim_id"] != claim_id_filter:
            continue
        if test_id_filter and test["test_id"] != test_id_filter:
            continue
        if query:
            haystack = " ".join(
                [
                    test["test_id"],
                    test["claim_id"],
                    test["claim_statement"],
                    test["formula_anchor"],
                    test["dataset_environment"],
                    test["derivation"],
                    test["exec_status"],
                    test["authenticity"],
                    test["leakage_risk"],
                    test["negative_control"],
                ]
            ).lower()
            if query not in haystack:
                continue
        filtered_tests.append(test)

    filtered_tests.sort(key=lambda row: (row["priority"], row["test_id"]))

    filtered_claims: list[dict] = []
    for claim in claims:
        linked_tests = tests_by_claim.get(claim["claim_id"], [])
        if claim_id_filter and claim["claim_id"] != claim_id_filter:
            continue
        if test_id_filter and test_id_filter not in {t["test_id"] for t in linked_tests}:
            continue
        if priority_filter and not any(t["priority"] == priority_filter for t in linked_tests):
            continue
        if status_filter and not any(t["exec_status"] == status_filter for t in linked_tests):
            continue
        if query:
            claim_text = " ".join(
                [
                    claim["claim_id"],
                    claim["statement"],
                    claim["claim_status"],
                    claim["confidence"],
                    claim["source_pages"],
                    claim["derivation"],
                ]
            ).lower()
            if query not in claim_text and not any(
                query in " ".join(
                    [
                        t["test_id"],
                        t["formula_anchor"],
                        t["dataset_environment"],
                        t["exec_status"],
                        t["authenticity"],
                        t["leakage_risk"],
                        t["negative_control"],
                    ]
                ).lower()
                for t in linked_tests
            ):
                continue

        primary = linked_tests[0] if linked_tests else None
        filtered_claims.append(
            {
                "claim_id": claim["claim_id"],
                "statement": claim["statement"],
                "claim_status": claim["claim_status"],
                "confidence": claim["confidence"],
                "source_pages": claim["source_pages"],
                "derivation": claim["derivation"],
                "claim_file": claim["claim_file"],
                "linked_test_count": len(linked_tests),
                "linked_tests": [t["test_id"] for t in linked_tests],
                "primary_test_id": primary["test_id"] if primary else "",
                "primary_priority": primary["priority"] if primary else "",
                "primary_exec_status": primary["exec_status"] if primary else "",
                "primary_evidence_path": primary["evidence_path"] if primary else "",
            }
        )

    filtered_claims.sort(key=lambda row: row["claim_id"])

    return {
        "generated_on": date.today().isoformat(),
        "filters": {
            "priority": priority_filter,
            "status": status_filter,
            "q": query_text,
            "claim_id": claim_id_filter,
            "test_id": test_id_filter,
        },
        "stats": {
            "claims_returned": len(filtered_claims),
            "tests_returned": len(filtered_tests),
            "claims_total": len(claims),
            "tests_total": len(test_rows),
        },
        "claims": filtered_claims,
        "tests": filtered_tests,
    }


def build_graph_data(priority_filter: str) -> dict:
    claims = parse_claims_register()
    tests = parse_test_plan()
    results = parse_results_per_test()
    params = parse_parameter_registry()
    test_rows = combine_test_rows(tests, results)

    if priority_filter:
        selected_tests = [row for row in test_rows if row["priority"] == priority_filter]
        selected_claim_ids = {row["claim_id"] for row in selected_tests}
    else:
        selected_tests = test_rows
        selected_claim_ids = {row["claim_id"] for row in claims}

    claims_by_id = {row["claim_id"]: row for row in claims}
    nodes: dict[str, dict] = {}
    edges: dict[str, dict] = {}

    def add_node(node_id: str, node_type: str, label: str, **meta: object) -> None:
        existing = nodes.get(node_id)
        if existing:
            existing.update(meta)
            return
        payload = {"id": node_id, "type": node_type, "label": label}
        payload.update(meta)
        nodes[node_id] = payload

    def add_edge(source: str, target: str, kind: str) -> None:
        key = f"{source}|{target}|{kind}"
        if key in edges:
            return
        edges[key] = {"source": source, "target": target, "kind": kind}

    for claim_id in sorted(selected_claim_ids):
        claim = claims_by_id.get(claim_id)
        if not claim:
            continue
        add_node(
            claim_id,
            "claim",
            claim_id,
            claim_status=claim["claim_status"],
            confidence=claim["confidence"],
            statement=claim["statement"],
            path=claim["claim_file"],
        )
        derivation = claim["derivation"]
        if derivation and derivation != "n/a":
            deriv_label = Path(derivation).name
            add_node(derivation, "derivation", deriv_label, path=derivation)
            add_edge(claim_id, derivation, "has-derivation")

    for test in selected_tests:
        add_node(
            test["test_id"],
            "test",
            test["test_id"],
            priority=test["priority"],
            exec_status=test["exec_status"],
            formula_anchor=test["formula_anchor"],
            claim_id=test["claim_id"],
        )
        if test["claim_id"]:
            add_edge(test["claim_id"], test["test_id"], "validated-by")

        evidence_path = test["evidence_path"]
        if evidence_path:
            ev_label = Path(evidence_path).name
            add_node(evidence_path, "evidence", ev_label, path=evidence_path)
            add_edge(test["test_id"], evidence_path, "collects-evidence")

    for param in params:
        related = [cid for cid in param["related_claims"] if cid in selected_claim_ids]
        if not related:
            continue
        param_id = param["parameter_id"] or f"param:{param['symbol']}"
        label = param["symbol"] or param_id
        add_node(
            param_id,
            "parameter",
            label,
            name=param["name"],
            param_status=param["status"],
        )
        for claim_id in related:
            add_edge(param_id, claim_id, "constrains")

    node_list = list(nodes.values())
    node_list.sort(key=lambda row: (row["type"], row["id"]))
    edge_list = list(edges.values())
    edge_list.sort(key=lambda row: (row["source"], row["target"], row["kind"]))

    node_counts = Counter(row["type"] for row in node_list)
    return {
        "generated_on": date.today().isoformat(),
        "scope": priority_filter or "ALL",
        "nodes": node_list,
        "edges": edge_list,
        "counts": dict(node_counts),
    }


def python_bin() -> str:
    venv_py = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def run_system_command(cmd: list[str]) -> dict:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            cmd,
            cwd=WORKSPACE_ROOT,
            text=True,
            capture_output=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "ok": False,
            "exit_code": -1,
            "duration_seconds": round(duration, 3),
            "command": cmd,
            "stdout": stdout,
            "stderr": (stderr + "\nProcess timed out after 1800 seconds.").strip(),
        }

    duration = time.perf_counter() - started
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "duration_seconds": round(duration, 3),
        "command": cmd,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_system_script(script_path: str) -> dict:
    return run_system_command([python_bin(), script_path])


def parse_generated_paths(stdout_text: str) -> list[str]:
    out: list[str] = []
    for line in stdout_text.splitlines():
        prefix = "Generated: "
        if not line.startswith(prefix):
            continue
        raw_path = line[len(prefix) :].strip()
        if not raw_path:
            continue
        try:
            resolved = resolve_relative_path(raw_path)
        except ValueError:
            continue
        out.append(to_workspace_relative(resolved))
    # Preserve order but remove duplicates.
    return list(dict.fromkeys(out))


def list_recent_export_files(limit: int = 36) -> list[dict]:
    if not EXPORT_ROOT.exists() or not EXPORT_ROOT.is_dir():
        return []

    files = [path for path in EXPORT_ROOT.rglob("*") if path.is_file()]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)

    out: list[dict] = []
    for path in files[:limit]:
        content_type, _ = mimetypes.guess_type(path.name)
        out.append(
            {
                "name": path.name,
                "path": to_workspace_relative(path),
                "size": path.stat().st_size,
                "mtime": int(path.stat().st_mtime),
                "content_type": content_type or "application/octet-stream",
            }
        )
    return out


def export_release_block_reason() -> str:
    tests = parse_test_plan()
    results = parse_results_per_test()
    merged = combine_test_rows(tests, results)
    gate = evaluate_export_release_gate(merged)
    if gate["ready"]:
        return ""
    blocked = gate["blocked_tests"]
    if blocked:
        sample = ", ".join(blocked[:12])
        extra = "" if len(blocked) <= 12 else f" (+{len(blocked) - 12} more)"
        return (
            "Export blocked: only Gold authenticity is allowed for released pass tests. "
            f"Non-gold pass tests: {sample}{extra}. "
            "Set `authenticity=gold`, and keep leakage/negative-control fields completed in Workbench."
        )
    return "Export blocked: no passed tests are currently eligible for Gold-only release."


def normalize_exec_status(value: str) -> str:
    status = value.strip().lower().replace("_", "-")
    alias = {
        "inprogress": "in-progress",
        "passed": "pass",
        "failed": "fail",
        "queue": "queued-p3",
        "queued": "queued-p3",
    }
    status = alias.get(status, status)
    if status in ALLOWED_EXEC_STATUS:
        return status
    return ""


def normalize_authenticity(value: str) -> str:
    raw = value.strip().lower()
    alias = {"g": "gold", "s": "silver", "b": "bronze"}
    raw = alias.get(raw, raw)
    return raw if raw in AUTHENTICITY_LEVELS else ""


def normalize_leakage_risk(value: str) -> str:
    raw = value.strip().lower()
    alias = {"medium": "med", "mid": "med", "m": "med", "l": "low", "h": "high"}
    raw = alias.get(raw, raw)
    return raw if raw in LEAKAGE_RISK_LEVELS else ""


def normalize_negative_control(value: str) -> str:
    raw = value.strip().lower()
    alias = {"na": "none", "n/a": "none", "nc": "none"}
    raw = alias.get(raw, raw)
    return raw if raw in NEGATIVE_CONTROL_STATES else ""


def default_review_meta(exec_status: str) -> tuple[str, str, str]:
    if exec_status == "pass":
        return ("bronze", "med", "planned")
    if exec_status == "in-progress":
        return ("bronze", "high", "planned")
    if exec_status.startswith("queued"):
        return ("bronze", "high", "none")
    if exec_status in {"fail", "blocked"}:
        return ("bronze", "high", "done")
    return ("bronze", "high", "none")


def ensure_results_row_shape(cells: list[str], exec_status: str) -> list[str]:
    if len(cells) >= 12:
        return cells
    out = list(cells[:9])
    while len(out) < 9:
        out.append("")
    auth, leak, control = default_review_meta(exec_status)
    out.extend([auth, leak, control])
    return out


def batch_status_from_exec(exec_status: str) -> str:
    if exec_status.startswith("queued"):
        return "queued"
    return exec_status


def decision_from_exec(exec_status: str) -> str:
    if exec_status in {"pass", "fail", "blocked"}:
        return exec_status
    return "pending"


def update_evidence_file(
    evidence_rel_path: str,
    exec_status: str,
    decision: str,
    rationale: str,
    last_updated: str,
    authenticity: str,
    leakage_risk: str,
    negative_control: str,
) -> dict:
    if not evidence_rel_path:
        return {"ok": False, "updated": False, "error": "No evidence path in results-log row"}
    try:
        evidence_path = resolve_relative_path(evidence_rel_path)
    except ValueError:
        return {"ok": False, "updated": False, "error": "Invalid evidence path"}

    if not evidence_path.exists():
        return {"ok": False, "updated": False, "error": "Evidence file does not exist", "path": evidence_rel_path}

    lines = evidence_path.read_text(encoding="utf-8").splitlines()
    changed = False

    def upsert(prefix: str, value: str) -> None:
        nonlocal changed
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                replacement = f"{prefix}{sanitize_inline(value)}"
                if lines[i] != replacement:
                    lines[i] = replacement
                    changed = True
                return
        lines.append(f"{prefix}{sanitize_inline(value)}")
        changed = True

    upsert("- Current status: ", exec_status)
    upsert("- Decision: ", decision)
    upsert("- Rationale: ", rationale)
    upsert("- Last updated: ", last_updated)
    upsert("- Authenticity: ", authenticity)
    upsert("- Leakage risk: ", leakage_risk)
    upsert("- Negative control: ", negative_control)

    if changed:
        evidence_path.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")

    return {"ok": True, "updated": changed, "path": evidence_rel_path}


def update_test_result(payload: dict) -> dict:
    test_id = sanitize_inline(payload.get("test_id", "")).upper()
    if not TEST_ID_RE.match(test_id):
        raise ValueError("Invalid or missing 'test_id'")

    exec_status = normalize_exec_status(str(payload.get("exec_status", "")))
    if not exec_status:
        raise ValueError("Invalid or missing 'exec_status'")

    last_run = sanitize_inline(payload.get("last_run", "")) or date.today().isoformat()
    if not DATE_RE.match(last_run):
        raise ValueError("'last_run' must use YYYY-MM-DD")

    lines = read_lines(RESULTS_LOG)
    if not lines:
        raise RuntimeError("results-log.md not found or empty")

    parsed_rows = parse_results_per_test(lines)
    target = next((row for row in parsed_rows if row["test_id"] == test_id), None)
    if not target:
        raise ValueError(f"Test not found in results-log: {test_id}")
    transitioned_to_pass = target.get("exec_status", "") != "pass" and exec_status == "pass"

    row_index = target["line_index"]
    cells = split_md_row(lines[row_index])
    if len(cells) not in {9, 12}:
        raise RuntimeError("Malformed per-test row in results-log")
    cells = ensure_results_row_shape(cells, exec_status=exec_status)

    cells[3] = exec_status
    cells[4] = last_run

    if "metric_value" in payload:
        cells[6] = sanitize_inline(payload.get("metric_value", ""))
    if "decision_note" in payload:
        cells[7] = sanitize_inline(payload.get("decision_note", ""))
    if "next_action" in payload:
        cells[8] = sanitize_inline(payload.get("next_action", ""))

    current_auth = cells[9]
    current_leak = cells[10]
    current_neg = cells[11]

    auth_raw = sanitize_inline(payload.get("authenticity", current_auth))
    leak_raw = sanitize_inline(payload.get("leakage_risk", current_leak))
    neg_raw = sanitize_inline(payload.get("negative_control", current_neg))

    authenticity = normalize_authenticity(auth_raw)
    leakage_risk = normalize_leakage_risk(leak_raw)
    negative_control = normalize_negative_control(neg_raw)

    if exec_status == "pass":
        if transitioned_to_pass:
            required_keys = {"authenticity", "leakage_risk", "negative_control"}
            missing = [key for key in sorted(required_keys) if key not in payload]
            if missing:
                raise ValueError(
                    "Promoting to `pass` requires explicit review fields: "
                    "`authenticity`, `leakage_risk`, `negative_control`."
                )
        if not authenticity:
            raise ValueError("Missing or invalid 'authenticity'. Allowed: gold|silver|bronze")
        if not leakage_risk:
            raise ValueError("Missing or invalid 'leakage_risk'. Allowed: low|med|high")
        if not negative_control:
            raise ValueError("Missing or invalid 'negative_control'. Allowed: none|planned|done")
    else:
        if not authenticity:
            authenticity = normalize_authenticity(current_auth) or default_review_meta(exec_status)[0]
        if not leakage_risk:
            leakage_risk = normalize_leakage_risk(current_leak) or default_review_meta(exec_status)[1]
        if not negative_control:
            negative_control = normalize_negative_control(current_neg) or default_review_meta(exec_status)[2]

    cells[9] = authenticity
    cells[10] = leakage_risk
    cells[11] = negative_control

    lines[row_index] = join_md_row(cells)

    batch_status = batch_status_from_exec(exec_status)
    for i, line in enumerate(lines):
        batch_cells = split_md_row(line)
        if len(batch_cells) == 6 and batch_cells[0] == test_id:
            batch_cells[5] = batch_status
            lines[i] = join_md_row(batch_cells)

    write_lines(RESULTS_LOG, lines)

    decision = sanitize_inline(payload.get("decision", "")) or decision_from_exec(exec_status)
    rationale = sanitize_inline(payload.get("rationale", "")) or sanitize_inline(payload.get("decision_note", ""))
    if not rationale:
        rationale = "Updated from workspace UI."

    evidence_update = update_evidence_file(
        evidence_rel_path=cells[5],
        exec_status=exec_status,
        decision=decision,
        rationale=rationale,
        last_updated=last_run,
        authenticity=authenticity,
        leakage_risk=leakage_risk,
        negative_control=negative_control,
    )

    claim_id, claim_statement = parse_claim_cell(cells[2])
    return {
        "test_id": cells[0],
        "priority": cells[1],
        "claim_id": claim_id,
        "claim_statement": claim_statement,
        "exec_status": cells[3],
        "last_run": cells[4],
        "evidence_path": cells[5],
        "metric_value": cells[6],
        "decision_note": cells[7],
        "next_action": cells[8],
        "authenticity": cells[9],
        "leakage_risk": cells[10],
        "negative_control": cells[11],
        "evidence_update": evidence_update,
    }

class Handler(BaseHTTPRequestHandler):
    server_version = "QNGWorkspaceUI/2.0"

    def _set_json_headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _send_json(self, payload: dict, status: int = 200) -> None:
        self._set_json_headers(status=status)
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _send_text(self, content: str, status: int = 200, content_type: str = "text/plain; charset=utf-8") -> None:
        data = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            bind_host, bind_port = self.server.server_address[:2]
            self._send_json(
                {
                    "ok": True,
                    "workspace": str(WORKSPACE_ROOT),
                    "host": str(bind_host),
                    "port": int(bind_port),
                }
            )
            return

        if path == "/api/tree":
            tree = build_tree(WORKSPACE_ROOT)
            self._send_json({"workspace": str(WORKSPACE_ROOT), "items": tree})
            return

        if path == "/api/file":
            self.handle_read_file(parsed)
            return

        if path == "/api/mission":
            try:
                self._send_json(build_mission_data())
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": f"Mission read failed: {exc}"}, status=500)
            return

        if path == "/api/workbench":
            query = parse_qs(parsed.query)
            priority = sanitize_inline(query.get("priority", [""])[0]).upper()
            status_filter = normalize_exec_status(sanitize_inline(query.get("status", [""])[0]))
            q = sanitize_inline(query.get("q", [""])[0])
            claim_id = sanitize_inline(query.get("claim_id", [""])[0]).upper()
            test_id = sanitize_inline(query.get("test_id", [""])[0]).upper()

            if priority and priority not in {"P1", "P2", "P3"}:
                self._send_json({"error": "Invalid priority filter"}, status=400)
                return
            if claim_id and not CLAIM_ID_RE.match(claim_id):
                self._send_json({"error": "Invalid claim_id filter"}, status=400)
                return
            if test_id and not TEST_ID_RE.match(test_id):
                self._send_json({"error": "Invalid test_id filter"}, status=400)
                return
            try:
                payload = build_workbench_data(priority, status_filter, q, claim_id, test_id)
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": f"Workbench read failed: {exc}"}, status=500)
                return
            self._send_json(payload)
            return

        if path == "/api/results":
            self.handle_results(parsed)
            return

        if path == "/api/results/detail":
            self.handle_result_detail(parsed)
            return

        if path == "/api/artifact":
            self.handle_artifact(parsed)
            return

        if path == "/api/export-file":
            self.handle_export_file(parsed)
            return

        if path == "/api/graph":
            query = parse_qs(parsed.query)
            priority = sanitize_inline(query.get("priority", [""])[0]).upper()
            if priority and priority not in {"P1", "P2", "P3"}:
                self._send_json({"error": "Invalid graph priority filter"}, status=400)
                return
            try:
                self._send_json(build_graph_data(priority))
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": f"Graph build failed: {exc}"}, status=500)
            return

        if path == "/api/exports":
            try:
                self._send_json(build_exports_data())
            except Exception as exc:  # noqa: BLE001
                self._send_json({"error": f"Exports read failed: {exc}"}, status=500)
            return

        self.serve_static(path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/file":
            self.handle_save_file()
            return
        if path == "/api/new":
            self.handle_new_file()
            return
        if path == "/api/test/update":
            self.handle_test_update()
            return
        if path == "/api/system/lint":
            self.handle_system_action("lint")
            return
        if path == "/api/system/sync":
            self.handle_system_action("sync")
            return
        if path == "/api/system/export":
            self.handle_system_action("export")
            return
        if path == "/api/system/export/package":
            self.handle_export_package()
            return
        if path == "/api/system/export/dossier":
            self.handle_export_dossier()
            return

        self._send_json({"error": "Unknown endpoint"}, status=404)

    def handle_read_file(self, parsed) -> None:
        query = parse_qs(parsed.query)
        requested = unquote(query.get("path", [""])[0])
        if not requested:
            self._send_json({"error": "Missing 'path' query parameter"}, status=400)
            return
        try:
            target = resolve_relative_path(requested)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if not target.exists() or not target.is_file():
            self._send_json({"error": "File not found"}, status=404)
            return
        if not is_text_file(target):
            self._send_json({"error": "File is not editable text"}, status=415)
            return

        try:
            content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = target.read_text(encoding="utf-8", errors="replace")

        self._send_json(
            {
                "path": requested.replace("\\", "/"),
                "content": content,
                "size": target.stat().st_size,
                "mtime": int(target.stat().st_mtime),
            }
        )

    def handle_results(self, parsed) -> None:
        query = parse_qs(parsed.query)
        priority = sanitize_inline(query.get("priority", [""])[0]).upper()
        status_filter = normalize_exec_status(sanitize_inline(query.get("status", [""])[0]))
        q = sanitize_inline(query.get("q", [""])[0])

        if priority and priority not in {"P1", "P2", "P3"}:
            self._send_json({"error": "Invalid priority filter"}, status=400)
            return
        try:
            payload = build_results_data(priority, status_filter, q)
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"Results read failed: {exc}"}, status=500)
            return
        self._send_json(payload)

    def handle_result_detail(self, parsed) -> None:
        query = parse_qs(parsed.query)
        test_id = sanitize_inline(query.get("test_id", [""])[0]).upper()
        if not TEST_ID_RE.match(test_id):
            self._send_json({"error": "Missing or invalid test_id"}, status=400)
            return
        try:
            payload = build_result_detail(test_id)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"Result detail failed: {exc}"}, status=500)
            return
        self._send_json(payload)

    def handle_artifact(self, parsed) -> None:
        query = parse_qs(parsed.query)
        requested = unquote(query.get("path", [""])[0])
        if not requested:
            self._send_json({"error": "Missing 'path' query parameter"}, status=400)
            return
        try:
            target = resolve_relative_path(requested)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if not ensure_inside(target, ARTIFACTS_ROOT):
            self._send_json({"error": "Artifact path must be under 05_validation/evidence/artifacts"}, status=403)
            return
        if not target.exists() or not target.is_file():
            self._send_json({"error": "Artifact file not found"}, status=404)
            return

        content_type, _ = mimetypes.guess_type(target.name)
        content_type = content_type or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def handle_export_file(self, parsed) -> None:
        query = parse_qs(parsed.query)
        requested = unquote(query.get("path", [""])[0])
        if not requested:
            self._send_json({"error": "Missing 'path' query parameter"}, status=400)
            return
        try:
            target = resolve_relative_path(requested)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if not ensure_inside(target, EXPORT_ROOT):
            self._send_json({"error": "Export path must be under 07_exports"}, status=403)
            return
        if not target.exists() or not target.is_file():
            self._send_json({"error": "Export file not found"}, status=404)
            return

        content_type, _ = mimetypes.guess_type(target.name)
        content_type = content_type or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def handle_save_file(self) -> None:
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        relative_path = str(payload.get("path", "")).strip()
        content = payload.get("content", "")

        if not relative_path:
            self._send_json({"error": "Missing 'path'"}, status=400)
            return
        if not isinstance(content, str):
            self._send_json({"error": "'content' must be a string"}, status=400)
            return

        try:
            target = resolve_relative_path(relative_path)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if target.exists() and target.is_dir():
            self._send_json({"error": "Cannot save content into a directory"}, status=400)
            return
        if not is_text_file(target):
            self._send_json({"error": "Extension is not allowed for editing"}, status=415)
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self._send_json({"ok": True, "path": relative_path.replace("\\", "/")})

    def handle_new_file(self) -> None:
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        dir_path = str(payload.get("dir", "")).strip()
        name = str(payload.get("name", "")).strip()

        if not name:
            self._send_json({"error": "Missing 'name'"}, status=400)
            return

        safe_name = name.replace("\\", "/").split("/")[-1]
        if safe_name in {".", ".."}:
            self._send_json({"error": "Invalid file name"}, status=400)
            return

        relative_path = f"{dir_path}/{safe_name}".strip("/")
        try:
            target = resolve_relative_path(relative_path)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if target.exists():
            self._send_json({"error": "File already exists"}, status=409)
            return
        if not is_text_file(target):
            self._send_json({"error": "Extension is not allowed for editing"}, status=415)
            return

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
        self._send_json({"ok": True, "path": relative_path})

    def handle_test_update(self) -> None:
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        try:
            updated = update_test_result(payload)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, status=500)
            return

        self._send_json({"ok": True, "updated": updated})

    def handle_export_package(self) -> None:
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        test_id = sanitize_inline(payload.get("test_id", "")).upper()
        all_gold = bool(payload.get("all_gold", False))
        md_only = bool(payload.get("md_only", False))

        if test_id and not TEST_ID_RE.match(test_id):
            self._send_json({"error": "Invalid test_id for claim package export."}, status=400)
            return
        if not test_id and not all_gold:
            self._send_json({"error": "Provide test_id or set all_gold=true."}, status=400)
            return

        if test_id:
            exists = any(row["test_id"] == test_id for row in parse_test_plan())
            if not exists:
                self._send_json({"error": f"Unknown test_id: {test_id}"}, status=400)
                return

        cmd = [python_bin(), "scripts/export_claim_test_package.py"]
        if test_id:
            cmd.extend(["--test-id", test_id])
        if md_only:
            cmd.append("--md-only")

        result = run_system_command(cmd)
        result["action"] = "export-package"
        result["scope"] = test_id if test_id else "all-gold"
        result["generated"] = parse_generated_paths(result.get("stdout", ""))
        result["recent_exports"] = list_recent_export_files()
        self._send_json(result, status=200)

    def handle_export_dossier(self) -> None:
        try:
            payload = parse_json_body(self)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON body"}, status=400)
            return

        md_only = bool(payload.get("md_only", False))
        cmd = [python_bin(), "scripts/export_full_theory_dossier.py"]
        if md_only:
            cmd.append("--md-only")

        result = run_system_command(cmd)
        result["action"] = "export-dossier"
        result["generated"] = parse_generated_paths(result.get("stdout", ""))
        result["recent_exports"] = list_recent_export_files()
        self._send_json(result, status=200)

    def handle_system_action(self, action: str) -> None:
        if action == "export":
            reason = export_release_block_reason()
            if reason:
                self._send_json(
                    {
                        "ok": False,
                        "action": action,
                        "error": reason,
                    },
                    status=400,
                )
                return
        script_path = SYSTEM_ACTIONS[action]
        result = run_system_script(script_path)
        result["action"] = action
        result["generated"] = parse_generated_paths(result.get("stdout", ""))
        if action == "export":
            result["recent_exports"] = list_recent_export_files()
        self._send_json(result, status=200)

    def serve_static(self, path: str) -> None:
        if path in {"/", ""}:
            static_path = UI_ROOT / "index.html"
        else:
            static_path = UI_ROOT / path.lstrip("/")

        static_path = static_path.resolve()
        if not ensure_inside(static_path, UI_ROOT):
            self._send_text("Forbidden", status=403)
            return

        if not static_path.exists() or not static_path.is_file():
            self._send_text("Not found", status=404)
            return

        content_type, _ = mimetypes.guess_type(static_path.name)
        content_type = content_type or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {
            "application/javascript",
            "application/json",
            "image/svg+xml",
        }:
            content_type = f"{content_type}; charset=utf-8"

        data = static_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stdout.write(f"[ui] {self.address_string()} - {fmt % args}\n")


def main() -> int:
    if not UI_ROOT.exists():
        print(f"Missing UI directory: {UI_ROOT}")
        return 1

    host = (os.environ.get("QNG_UI_HOST", DEFAULT_HOST) or DEFAULT_HOST).strip()
    if not host:
        host = DEFAULT_HOST

    raw_port = (os.environ.get("QNG_UI_PORT", str(DEFAULT_PORT)) or str(DEFAULT_PORT)).strip()
    try:
        port = int(raw_port)
    except ValueError:
        port = DEFAULT_PORT
    if port <= 0 or port > 65535:
        port = DEFAULT_PORT

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"QNG workspace UI running at http://{host}:{port}")
    if host == "0.0.0.0":
        lan_ip = ""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            lan_ip = sock.getsockname()[0]
            sock.close()
        except OSError:
            lan_ip = ""
        if lan_ip:
            print(f"LAN URL (phone): http://{lan_ip}:{port}")
        else:
            print("LAN URL (phone): use your PC local IP with the same port.")
    print(f"Workspace root: {WORKSPACE_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
