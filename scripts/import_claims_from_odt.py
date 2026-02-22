#!/usr/bin/env python3
"""
Import claim section content from an ODT document into 02_claims/claims/QNG-C-*.md.

The script keeps each claim file metadata header (status/confidence/pages/derivation)
as-is and replaces section bodies:
- Claim Statement
- Assumptions
- Mathematical Form
- Potential Falsifier
- Evidence / Notes
- Next Action
"""

from __future__ import annotations

import argparse
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ODT = Path(r"C:\Users\tigan\Desktop\claims.odt")
CLAIMS_DIR = ROOT / "02_claims" / "claims"

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
}

SECTIONS = [
    "Claim Statement",
    "Assumptions",
    "Mathematical Form",
    "Potential Falsifier",
    "Evidence / Notes",
    "Next Action",
]

META_KEYS = [
    "Status",
    "Confidence",
    "Source page(s)",
    "Related derivation",
    "Register source",
]

SKIP_LINES = {
    "If you want, I can continue with the next claim.",
    "Here is the revision only, clean and publication-ready.",
}


def clean_text(value: str) -> str:
    text = value.replace("\u200b", "").replace("\xa0", " ")
    text = " ".join(text.split())
    return text.strip()


def parse_odt_claims(odt_path: Path) -> dict[str, dict[str, list[str]]]:
    claims: dict[str, dict[str, list[str]]] = {}
    with zipfile.ZipFile(odt_path) as archive:
        content_xml = archive.read("content.xml")
    root = ET.fromstring(content_xml)
    doc_text = root.find("office:body", NS).find("office:text", NS)

    current_claim: str | None = None
    current_section: str | None = None

    for element in doc_text.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in {"h", "p"}:
            continue

        text = clean_text("".join(element.itertext()))
        if not text:
            continue
        lower_text = text.lower()
        if text in SKIP_LINES:
            # Stop collecting the current section once this chat marker appears.
            current_section = None
            continue
        if lower_text.startswith("next statement:") or lower_text.startswith("next statement :"):
            current_section = None
            continue
        if lower_text.startswith("next statement #") or lower_text.startswith("next statement #"):
            current_section = None
            continue
        if "## Claim Statement" in text and "Next Statement" in text:
            current_section = None
            continue

        if tag == "h":
            match = re.search(r"(QNG-C-\d{3})", text)
            if match:
                current_claim = match.group(1)
                current_section = None
                claims.setdefault(current_claim, {name: [] for name in SECTIONS})
                continue
            if text in SECTIONS:
                current_section = text
                continue

        if not current_claim or not current_section:
            continue

        claims[current_claim][current_section].append(text)

    return claims


def parse_metadata_from_claim_file(path: Path) -> dict[str, str]:
    meta = {key: "" for key in META_KEYS}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        stripped = line.strip()
        for key in META_KEYS:
            prefix = f"- {key}:"
            if stripped.startswith(prefix):
                meta[key] = stripped[len(prefix) :].strip()
    return meta


def render_claim_markdown(claim_id: str, meta: dict[str, str], sections: dict[str, list[str]]) -> str:
    lines: list[str] = []
    lines.append(f"# {claim_id}")
    lines.append("")
    lines.append(f"- Status: {meta.get('Status', '').strip()}")
    lines.append(f"- Confidence: {meta.get('Confidence', '').strip()}")
    lines.append(f"- Source page(s): {meta.get('Source page(s)', '').strip()}")
    lines.append(f"- Related derivation: {meta.get('Related derivation', '').strip()}")
    register_source = meta.get("Register source", "").strip() or "02_claims/claims-register.md"
    lines.append(f"- Register source: {register_source}")
    lines.append("")

    statement_lines = sections.get("Claim Statement", [])
    lines.append("## Claim Statement")
    lines.append("")
    if statement_lines:
        lines.extend(statement_lines)
    else:
        lines.append("TODO")
    lines.append("")

    for section in SECTIONS[1:]:
        lines.append(f"## {section}")
        lines.append("")
        content = sections.get(section, [])
        if content:
            for item in content:
                lines.append(f"- {item}")
        else:
            lines.append("- TODO")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Import claim sections from ODT into claim markdown files.")
    parser.add_argument("--odt", default=str(DEFAULT_ODT), help="Path to source ODT file.")
    args = parser.parse_args()

    odt_path = Path(args.odt)
    if not odt_path.exists():
        raise FileNotFoundError(f"ODT file not found: {odt_path}")

    odt_claims = parse_odt_claims(odt_path)
    updated = 0
    skipped = 0
    missing_in_odt: list[str] = []

    for claim_file in sorted(CLAIMS_DIR.glob("QNG-C-*.md")):
        claim_id = claim_file.stem
        sections = odt_claims.get(claim_id)
        if not sections:
            missing_in_odt.append(claim_id)
            skipped += 1
            continue

        meta = parse_metadata_from_claim_file(claim_file)
        rendered = render_claim_markdown(claim_id, meta, sections)
        claim_file.write_text(rendered, encoding="utf-8")
        updated += 1

    print(f"Claims parsed from ODT: {len(odt_claims)}")
    print(f"Claim files updated: {updated}")
    print(f"Claim files skipped: {skipped}")
    if missing_in_odt:
        print("Missing in ODT:", ", ".join(missing_in_odt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
