#!/usr/bin/env python3
"""
Export writing artifacts that include only passed claims.

Outputs:
- 06_writing/validated-claims.md
- 06_writing/paper-valid-only.md
- 07_exports/validated-brief.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
CLAIMS_REGISTER = ROOT / "02_claims" / "claims-register.md"
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"
VALIDATED_CLAIMS = ROOT / "06_writing" / "validated-claims.md"
PAPER_VALID_ONLY = ROOT / "06_writing" / "paper-valid-only.md"
EXPORT_BRIEF = ROOT / "07_exports" / "validated-brief.md"

CLAIM_RE = re.compile(
    r"^\|\s*(QNG-C-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)
TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")


@dataclass
class Claim:
    claim_id: str
    statement: str
    status: str
    confidence: str
    pages: str
    derivation: str


@dataclass
class TestLink:
    test_id: str
    claim_id: str
    priority: str
    formula: str


@dataclass
class ResultRow:
    test_id: str
    claim_id: str
    exec_status: str
    authenticity: str


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


def parse_claims() -> dict[str, Claim]:
    out: dict[str, Claim] = {}
    for line in CLAIMS_REGISTER.read_text(encoding="utf-8").splitlines():
        m = CLAIM_RE.match(line.strip())
        if not m:
            continue
        c = Claim(
            claim_id=m.group(1),
            statement=m.group(2),
            status=m.group(3),
            confidence=m.group(4),
            pages=m.group(5),
            derivation=m.group(6),
        )
        out[c.claim_id] = c
    return out


def parse_tests() -> dict[str, TestLink]:
    out: dict[str, TestLink] = {}
    for line in TEST_PLAN.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        if not TEST_ID_RE.match(cells[0]):
            continue
        claim_match = CLAIM_HEAD_RE.match(cells[1])
        if not claim_match:
            continue
        claim_id = claim_match.group(1)
        out[claim_id] = TestLink(
            test_id=cells[0],
            claim_id=claim_id,
            priority=cells[8],
            formula=cells[3],
        )
    return out


def parse_results_rows() -> list[ResultRow]:
    rows: list[ResultRow] = []
    in_table = False
    for line in RESULTS_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| Test ID | Priority | Claim | Exec status |"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = split_md_row(line)
            if len(cells) < 9:
                continue
            if not TEST_ID_RE.match(cells[0]):
                continue
            claim_match = CLAIM_HEAD_RE.match(cells[2])
            if not claim_match:
                continue
            authenticity = "bronze"
            if len(cells) >= 12 and cells[9].strip():
                authenticity = cells[9].strip().lower()
            rows.append(
                ResultRow(
                    test_id=cells[0],
                    claim_id=claim_match.group(1),
                    exec_status=cells[3].strip().lower(),
                    authenticity=authenticity,
                )
            )
    return rows


def render_validated_claims(claims: list[Claim], tests: dict[str, TestLink]) -> str:
    lines: list[str] = []
    lines.append("# Validated Claims")
    lines.append("")
    lines.append(f"- Count: {len(claims)}")
    lines.append("")
    lines.append("| Claim ID | Statement | Confidence | Test ID | Priority | Derivation | Source page(s) |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for c in claims:
        t = tests.get(c.claim_id)
        test_id = t.test_id if t else "n/a"
        pri = t.priority if t else "n/a"
        lines.append(
            f"| {c.claim_id} | {c.statement.replace('|', '/')} | {c.confidence} | {test_id} | {pri} | {c.derivation} | {c.pages} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_paper_valid_only(claims: list[Claim], tests: dict[str, TestLink]) -> str:
    lines: list[str] = []
    lines.append("# QNG - Validated Claims Paper Draft")
    lines.append("")
    lines.append("This draft includes only claims marked as `pass` with `authenticity=gold` in `05_validation/results-log.md`.")
    lines.append("")
    lines.append("## Abstract")
    lines.append("")
    if claims:
        lines.append(
            f"This document summarizes {len(claims)} validated claims from the QNG framework, with linked tests and derivations."
        )
    else:
        lines.append("No claims are currently marked as pass. Run validation and update results-log first.")
    lines.append("")
    lines.append("## Validated Core Claims")
    lines.append("")
    if not claims:
        lines.append("- None yet.")
    else:
        for c in claims:
            t = tests.get(c.claim_id)
            test_label = t.test_id if t else "n/a"
            lines.append(f"### {c.claim_id}")
            lines.append("")
            lines.append(f"- Statement: {c.statement}")
            lines.append(f"- Test: {test_label}")
            lines.append(f"- Derivation: `{c.derivation}`")
            lines.append(f"- Source: {c.pages}")
            lines.append("")
    lines.append("## Methods and Validation Notes")
    lines.append("")
    lines.append("- See `05_validation/test-plan.md` and `05_validation/results-log.md` for full validation matrix.")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- This export is strictly filtered by `pass` status with `authenticity=gold`.")
    lines.append("")
    return "\n".join(lines)


def render_export_brief(claims: list[Claim], tests: dict[str, TestLink]) -> str:
    lines: list[str] = []
    lines.append("# Validated Brief Export")
    lines.append("")
    lines.append(f"- Total exported claims (Gold pass): {len(claims)}")
    lines.append("- Source: 05_validation/results-log.md")
    lines.append("")
    if not claims:
        lines.append("No passed claims available for export.")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Claim ID | Test ID | Formula Anchor | Derivation |")
    lines.append("| --- | --- | --- | --- |")
    for c in claims:
        t = tests.get(c.claim_id)
        if t:
            lines.append(
                f"| {c.claim_id} | {t.test_id} | {t.formula.replace('|', '/')} | {c.derivation} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    claims_map = parse_claims()
    tests_map = parse_tests()
    results = parse_results_rows()

    pass_rows = [row for row in results if row.exec_status == "pass"]
    if not pass_rows:
        print("Export blocked: no tests are currently marked `pass` in results-log.")
        return 2

    gold_rows = [row for row in pass_rows if row.authenticity == "gold"]
    if not gold_rows:
        print("Export blocked: release policy allows export only from Gold pass tests.")
        return 2

    passed_ids = {row.claim_id for row in gold_rows}
    passed_claims = [claims_map[cid] for cid in sorted(passed_ids) if cid in claims_map]

    VALIDATED_CLAIMS.parent.mkdir(parents=True, exist_ok=True)
    PAPER_VALID_ONLY.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_BRIEF.parent.mkdir(parents=True, exist_ok=True)

    VALIDATED_CLAIMS.write_text(render_validated_claims(passed_claims, tests_map), encoding="utf-8")
    PAPER_VALID_ONLY.write_text(render_paper_valid_only(passed_claims, tests_map), encoding="utf-8")
    EXPORT_BRIEF.write_text(render_export_brief(passed_claims, tests_map), encoding="utf-8")

    print(f"Validated claims exported: {len(passed_claims)}")
    print(f"Updated: {VALIDATED_CLAIMS}")
    print(f"Updated: {PAPER_VALID_ONLY}")
    print(f"Updated: {EXPORT_BRIEF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
