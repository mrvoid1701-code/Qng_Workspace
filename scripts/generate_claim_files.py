#!/usr/bin/env python3
"""
Generate claim files and claim index from 02_claims/claims-register.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re


ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "02_claims" / "claims-register.md"
OUT_DIR = ROOT / "02_claims" / "claims"
INDEX = ROOT / "02_claims" / "claim-files-index.md"

ROW_RE = re.compile(
    r"^\|\s*(QNG-C-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)


@dataclass
class ClaimRow:
    claim_id: str
    statement: str
    status: str
    confidence: str
    source_pages: str
    related_derivation: str


def parse_register(path: Path) -> list[ClaimRow]:
    rows: list[ClaimRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        rows.append(
            ClaimRow(
                claim_id=m.group(1),
                statement=m.group(2),
                status=m.group(3),
                confidence=m.group(4),
                source_pages=m.group(5),
                related_derivation=m.group(6),
            )
        )
    return rows


def render_claim_file(row: ClaimRow) -> str:
    lines: list[str] = []
    lines.append(f"# {row.claim_id}")
    lines.append("")
    lines.append(f"- Status: {row.status}")
    lines.append(f"- Confidence: {row.confidence}")
    lines.append(f"- Source page(s): {row.source_pages}")
    lines.append(f"- Related derivation: {row.related_derivation}")
    lines.append("- Register source: 02_claims/claims-register.md")
    lines.append("")
    lines.append("## Claim Statement")
    lines.append("")
    lines.append(row.statement)
    lines.append("")
    lines.append("## Assumptions")
    lines.append("")
    lines.append("- TODO")
    lines.append("")
    lines.append("## Mathematical Form")
    lines.append("")
    lines.append("- TODO")
    lines.append("")
    lines.append("## Potential Falsifier")
    lines.append("")
    lines.append("- TODO")
    lines.append("")
    lines.append("## Evidence / Notes")
    lines.append("")
    lines.append("- TODO")
    lines.append("")
    lines.append("## Next Action")
    lines.append("")
    lines.append("- TODO")
    lines.append("")
    return "\n".join(lines)


def render_index(rows: list[ClaimRow]) -> str:
    lines: list[str] = []
    lines.append("# Claim Files Index")
    lines.append("")
    lines.append("| Claim ID | File | Status | Confidence | Source page(s) |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(
            f"| {row.claim_id} | 02_claims/claims/{row.claim_id}.md | {row.status} | {row.confidence} | {row.source_pages} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate claim files from claims register.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing claim files.")
    args = parser.parse_args()

    rows = parse_register(REGISTER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for row in rows:
        target = OUT_DIR / f"{row.claim_id}.md"
        if target.exists() and not args.force:
            skipped += 1
            continue
        target.write_text(render_claim_file(row), encoding="utf-8")
        written += 1

    INDEX.write_text(render_index(rows), encoding="utf-8")
    print(f"Claim files generated: {written}")
    print(f"Claim files skipped: {skipped}")
    print(f"Index updated: {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

