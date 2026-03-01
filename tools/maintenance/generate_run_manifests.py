#!/usr/bin/env python3
"""
Generate per-test run manifests from 05_validation/test-plan.md.

Outputs:
- 05_validation/run-manifests/qng-t-xxx.json
- 05_validation/run-manifests/README.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import re


ROOT = Path(__file__).resolve().parent.parent
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"
OUT_DIR = ROOT / "05_validation" / "run-manifests"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")


@dataclass
class TestRow:
    test_id: str
    claim_id: str
    claim_statement: str
    derivation: str
    formula: str
    dataset: str
    method: str
    pass_condition: str
    fail_condition: str
    priority: str
    status: str


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


def parse_test_plan(path: Path) -> list[TestRow]:
    rows: list[TestRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        if not TEST_ID_RE.match(cells[0]):
            continue
        claim_match = CLAIM_HEAD_RE.match(cells[1])
        if not claim_match:
            continue
        rows.append(
            TestRow(
                test_id=cells[0],
                claim_id=claim_match.group(1),
                claim_statement=claim_match.group(2),
                derivation=cells[2],
                formula=cells[3],
                dataset=cells[4],
                method=cells[5],
                pass_condition=cells[6],
                fail_condition=cells[7],
                priority=cells[8],
                status=cells[9],
            )
        )
    return rows


def parse_results_status(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    statuses: dict[str, str] = {}
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| Test ID | Priority | Claim | Exec status |"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = split_md_row(line)
            if len(cells) < 4:
                continue
            if TEST_ID_RE.match(cells[0]):
                statuses[cells[0]] = cells[3]
    return statuses


def render_index(rows: list[TestRow]) -> str:
    lines: list[str] = []
    lines.append("# Run Manifest Index")
    lines.append("")
    lines.append(f"- Total manifests: {len(rows)}")
    lines.append("")
    lines.append("| Test ID | Claim | Priority | Manifest |")
    lines.append("| --- | --- | --- | --- |")
    for row in sorted(rows, key=lambda r: int(r.test_id.split("-")[-1])):
        lines.append(
            f"| {row.test_id} | {row.claim_id} | {row.priority} | `05_validation/run-manifests/{row.test_id.lower()}.json` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate per-test run manifests.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing manifests.")
    args = parser.parse_args()

    rows = parse_test_plan(TEST_PLAN)
    status_map = parse_results_status(RESULTS_LOG)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    for row in rows:
        target = OUT_DIR / f"{row.test_id.lower()}.json"
        if target.exists() and not args.force:
            skipped += 1
            continue
        payload = {
            "schema_version": "1.0",
            "test_id": row.test_id,
            "claim_id": row.claim_id,
            "claim_statement": row.claim_statement,
            "priority": row.priority,
            "status": status_map.get(row.test_id, "queued"),
            "derivation_path": row.derivation,
            "formula_anchor": row.formula,
            "dataset": row.dataset,
            "method": row.method,
            "pass_condition": row.pass_condition,
            "fail_condition": row.fail_condition,
            "parameters": {
                "tau": None,
                "chi": None,
                "sigma_min": None,
                "kernel_type": None,
            },
            "inputs": [],
            "commands": [],
            "outputs": [],
            "decision": {
                "result": "pending",
                "note": "",
                "reviewer": "",
                "date": "YYYY-MM-DD",
            },
            "reproducibility": {
                "seed": None,
                "code_version": "TODO",
                "environment": "TODO",
            },
        }
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        created += 1

    (OUT_DIR / "README.md").write_text(render_index(rows), encoding="utf-8")
    print(f"Run manifests created: {created}")
    print(f"Run manifests skipped: {skipped}")
    print(f"Index: {OUT_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
