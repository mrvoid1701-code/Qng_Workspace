#!/usr/bin/env python3
"""
Generate evidence stub files for all tests in 05_validation/test-plan.md.

Outputs:
- 05_validation/evidence/qng-t-xxx-<category>.md
- 05_validation/evidence/README.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re


ROOT = Path(__file__).resolve().parent.parent
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
EVIDENCE_DIR = ROOT / "05_validation" / "evidence"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")


@dataclass
class TestPlanRow:
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


def parse_test_plan(path: Path) -> list[TestPlanRow]:
    if not path.exists():
        raise FileNotFoundError(f"Missing test plan: {path}")

    rows: list[TestPlanRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        if not TEST_ID_RE.match(cells[0]):
            continue
        claim_match = CLAIM_HEAD_RE.match(cells[1])
        if not claim_match:
            continue
        priority = cells[8]
        if priority not in {"P1", "P2", "P3"}:
            continue
        rows.append(
            TestPlanRow(
                test_id=cells[0],
                claim_id=claim_match.group(1),
                claim_statement=claim_match.group(2),
                derivation=cells[2],
                formula=cells[3],
                dataset=cells[4],
                method=cells[5],
                pass_condition=cells[6],
                fail_condition=cells[7],
                priority=priority,
                status=cells[9],
            )
        )
    return rows


def category_for(dataset: str) -> str:
    d = dataset.lower()
    if "flyby/deep-space telemetry" in d:
        return "trajectory"
    if "lensing + rotation datasets" in d:
        return "lensing_dark"
    if "timing/waveforms" in d:
        return "timing_wave"
    if "discrete/n-body simulation environment" in d:
        return "simulation_nbody"
    if "analytical + symbolic limit analysis" in d:
        return "gr_limit"
    if "ensemble update simulation + operator fitting" in d:
        return "qm_qft"
    if "cosmological toy simulation / synthetic catalogs" in d:
        return "cosmo_sim"
    return "formal_math"


def evidence_file_for(row: TestPlanRow) -> Path:
    category = category_for(row.dataset)
    name = f"{row.test_id.lower()}-{category}.md"
    return EVIDENCE_DIR / name


def render_stub(row: TestPlanRow, evidence_rel: str) -> str:
    lines: list[str] = []
    lines.append(f"# Evidence - {row.test_id}")
    lines.append("")
    lines.append(f"- Priority: {row.priority}")
    lines.append(f"- Claim: {row.claim_id}")
    lines.append(f"- Claim statement: {row.claim_statement}")
    lines.append(f"- Derivation: `{row.derivation}`")
    lines.append(f"- Test plan source: `05_validation/test-plan.md`")
    lines.append(f"- Evidence file: `{evidence_rel}`")
    lines.append(f"- Current status: not-started")
    lines.append("")
    lines.append("## Objective")
    lines.append("")
    lines.append(row.claim_statement)
    lines.append("")
    lines.append("## Formula Anchor")
    lines.append("")
    lines.append("```text")
    lines.append(row.formula)
    lines.append("```")
    lines.append("")
    lines.append("## Dataset / Environment")
    lines.append("")
    lines.append(f"- {row.dataset}")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(f"- {row.method}")
    lines.append("")
    lines.append("## Reproducible Run")
    lines.append("")
    lines.append("```powershell")
    lines.append("# Command(s) used")
    lines.append("# Parameters")
    lines.append("# Seed/version/date")
    lines.append("```")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append("| Input | Version / Date | Notes |")
    lines.append("| --- | --- | --- |")
    lines.append("| TODO | TODO | TODO |")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append("| Artifact | Path | Notes |")
    lines.append("| --- | --- | --- |")
    lines.append("| Plot/table/log | TODO | TODO |")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value | Threshold | Status |")
    lines.append("| --- | --- | --- | --- |")
    lines.append("| TODO | TODO | TODO | pending |")
    lines.append("")
    lines.append("## Pass / Fail Criteria")
    lines.append("")
    lines.append(f"- Pass: {row.pass_condition}")
    lines.append(f"- Fail: {row.fail_condition}")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("- Decision: pending")
    lines.append("- Rationale: TODO")
    lines.append("- Last updated: YYYY-MM-DD")
    lines.append("")
    return "\n".join(lines)


def render_index(rows: list[TestPlanRow]) -> str:
    p1 = sum(1 for r in rows if r.priority == "P1")
    p2 = sum(1 for r in rows if r.priority == "P2")
    p3 = sum(1 for r in rows if r.priority == "P3")
    lines: list[str] = []
    lines.append("# Evidence Index")
    lines.append("")
    lines.append("- Generated from `05_validation/test-plan.md`.")
    lines.append(f"- Total stubs: {len(rows)}")
    lines.append(f"- P1: {p1}")
    lines.append(f"- P2: {p2}")
    lines.append(f"- P3: {p3}")
    lines.append("")
    lines.append("| Test ID | Priority | Claim | Category | Evidence File |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in sorted(rows, key=lambda r: int(r.test_id.split("-")[-1])):
        category = category_for(row.dataset)
        rel = f"05_validation/evidence/{evidence_file_for(row).name}"
        lines.append(f"| {row.test_id} | {row.priority} | {row.claim_id} | {category} | `{rel}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate evidence stub files for validation tests.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing evidence files.")
    args = parser.parse_args()

    rows = parse_test_plan(TEST_PLAN)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    skipped = 0
    for row in rows:
        out = evidence_file_for(row)
        rel = f"05_validation/evidence/{out.name}"
        if out.exists() and not args.force:
            skipped += 1
            continue
        out.write_text(render_stub(row, rel), encoding="utf-8")
        created += 1

    (EVIDENCE_DIR / "README.md").write_text(render_index(rows), encoding="utf-8")
    print(f"Evidence stubs created: {created}")
    print(f"Evidence stubs skipped: {skipped}")
    print(f"Index: {EVIDENCE_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

