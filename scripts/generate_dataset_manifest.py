#!/usr/bin/env python3
"""
Generate dataset manifest from 05_validation/test-plan.md.

Outputs:
- 05_validation/dataset-manifest.md
- 05_validation/dataset-manifest.json
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parent.parent
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
OUT_MD = ROOT / "05_validation" / "dataset-manifest.md"
OUT_JSON = ROOT / "05_validation" / "dataset-manifest.json"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")


@dataclass
class TestRow:
    test_id: str
    claim_id: str
    dataset: str
    method: str
    priority: str


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
                dataset=cells[4],
                method=cells[5],
                priority=cells[8],
            )
        )
    return rows


def dataset_type(dataset: str) -> str:
    d = dataset.lower()
    if "telemetry" in d:
        return "spacecraft"
    if "lensing" in d or "rotation" in d:
        return "astronomy"
    if "timing/waveforms" in d:
        return "timing-waveform"
    if "simulation environment" in d:
        return "simulation"
    if "analytical + symbolic" in d:
        return "analytical"
    if "ensemble update simulation" in d:
        return "simulation"
    if "cosmological toy simulation" in d:
        return "simulation"
    return "other"


def priority_rank(priority: str) -> int:
    return {"P1": 1, "P2": 2, "P3": 3}.get(priority, 9)


def build_manifest(rows: list[TestRow]) -> list[dict]:
    groups: dict[str, dict] = {}
    for row in rows:
        key = row.dataset
        if key not in groups:
            groups[key] = {
                "dataset_name": row.dataset,
                "dataset_type": dataset_type(row.dataset),
                "tests": [],
                "claims": [],
                "highest_priority": row.priority,
                "source_url": "TODO",
                "license": "TODO",
                "local_path": "TODO",
                "version_or_release": "TODO",
                "last_verified": "YYYY-MM-DD",
                "notes": "TODO",
            }
        g = groups[key]
        if row.test_id not in g["tests"]:
            g["tests"].append(row.test_id)
        if row.claim_id not in g["claims"]:
            g["claims"].append(row.claim_id)
        if priority_rank(row.priority) < priority_rank(g["highest_priority"]):
            g["highest_priority"] = row.priority

    out: list[dict] = []
    for idx, key in enumerate(sorted(groups.keys()), start=1):
        g = groups[key]
        g["dataset_id"] = f"DS-{idx:03d}"
        g["tests"].sort()
        g["claims"].sort()
        out.append(g)
    return out


def render_md(items: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Dataset Manifest")
    lines.append("")
    lines.append("Generated from `05_validation/test-plan.md`.")
    lines.append("")
    lines.append("| Dataset ID | Name | Type | Highest Priority | Tests | Claims | Source URL | License | Local Path | Version | Last Verified |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in items:
        tests = ", ".join(item["tests"])
        claims = ", ".join(item["claims"])
        lines.append(
            f"| {item['dataset_id']} | {item['dataset_name']} | {item['dataset_type']} | {item['highest_priority']} | {tests} | {claims} | {item['source_url']} | {item['license']} | {item['local_path']} | {item['version_or_release']} | {item['last_verified']} |"
        )
    lines.append("")
    lines.append("## Dataset Notes")
    lines.append("")
    for item in items:
        lines.append(f"### {item['dataset_id']} - {item['dataset_name']}")
        lines.append(f"- Type: {item['dataset_type']}")
        lines.append(f"- Highest priority linked: {item['highest_priority']}")
        lines.append(f"- Tests: {', '.join(item['tests'])}")
        lines.append(f"- Claims: {', '.join(item['claims'])}")
        lines.append("- Notes: TODO")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    rows = parse_test_plan(TEST_PLAN)
    items = build_manifest(rows)
    OUT_MD.write_text(render_md(items), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Datasets indexed: {len(items)}")
    print(f"Updated: {OUT_MD}")
    print(f"Updated: {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

