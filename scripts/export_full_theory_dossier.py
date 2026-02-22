#!/usr/bin/env python3
"""
Export a full QNG dossier that aggregates:
- validation test results
- symbols/definitions
- claims register
- derivations
- evidence files
- claim files

Outputs:
- 07_exports/qng-full-theory-dossier.md
- 07_exports/qng-full-theory-dossier.odt
- 07_exports/qng-full-theory-dossier.pdf
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape
import argparse
import re
import zipfile

import workspace_ui as wui


ROOT = Path(__file__).resolve().parent.parent
EXPORT_DIR = ROOT / "07_exports"
CLAIMS_DIR = ROOT / "02_claims" / "claims"
DERIVATIONS_DIR = ROOT / "03_math" / "derivations"
EVIDENCE_DIR = ROOT / "05_validation" / "evidence"

SYMBOLS_MD = ROOT / "03_math" / "symbols.md"
CLAIMS_REGISTER_MD = ROOT / "02_claims" / "claims-register.md"
TEST_PLAN_MD = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG_MD = ROOT / "05_validation" / "results-log.md"
DATASET_MANIFEST_MD = ROOT / "05_validation" / "dataset-manifest.md"

OUT_MD = EXPORT_DIR / "qng-full-theory-dossier.md"
OUT_ODT = EXPORT_DIR / "qng-full-theory-dossier.odt"
OUT_PDF = EXPORT_DIR / "qng-full-theory-dossier.pdf"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def clean_cell(value: str) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip()


def iter_sorted(paths: list[Path], qng_numeric: bool = False) -> list[Path]:
    if not qng_numeric:
        return sorted(paths, key=lambda p: p.name.lower())

    def key(path: Path) -> tuple[int, str]:
        m = re.search(r"(\d{3})", path.stem.lower())
        if not m:
            return (999_999, path.name.lower())
        return (int(m.group(1)), path.name.lower())

    return sorted(paths, key=key)


def summarize_validation() -> tuple[str, str, list[str]]:
    claims = wui.parse_claims_register()
    tests = wui.parse_test_plan()
    results = wui.parse_results_per_test()
    rows = wui.combine_test_rows(tests, results)

    by_exec = Counter(row["exec_status"] for row in rows if row["exec_status"])
    by_prio = Counter(row["priority"] for row in rows if row["priority"])
    by_auth = Counter(
        row["authenticity"]
        for row in rows
        if row["exec_status"] == "pass" and row["authenticity"]
    )

    summary_lines = [
        f"- Claims total: {len(claims)}",
        f"- Tests total: {len(rows)}",
        f"- Status counts: {dict(by_exec)}",
        f"- Priority counts: {dict(by_prio)}",
        f"- Pass authenticity: {dict(by_auth)}",
    ]

    table_lines = [
        "| Test ID | Priority | Claim ID | Exec status | Last run | Authenticity | Leakage risk | Negative control | Metric value |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda r: (r["priority"], r["test_id"])):
        table_lines.append(
            "| "
            + " | ".join(
                [
                    clean_cell(row["test_id"]),
                    clean_cell(row["priority"]),
                    clean_cell(row["claim_id"]),
                    clean_cell(row["exec_status"]),
                    clean_cell(row["last_run"]),
                    clean_cell(row["authenticity"]),
                    clean_cell(row["leakage_risk"]),
                    clean_cell(row["negative_control"]),
                    clean_cell(row["metric_value"]),
                ]
            )
            + " |"
        )

    return ("\n".join(summary_lines), "\n".join(table_lines), [row["test_id"] for row in rows])


def build_markdown() -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    summary_text, test_table, _ = summarize_validation()

    lines: list[str] = []
    lines.append("# QNG Full Theory Dossier")
    lines.append("")
    lines.append(f"- Generated (UTC): {generated}")
    lines.append("- Scope: tests, results, symbols/definitions, claims, derivations, evidence, manifests")
    lines.append("")

    lines.append("## Validation Summary")
    lines.append("")
    lines.extend(summary_text.splitlines())
    lines.append("")

    lines.append("## Validation Results (All Tests)")
    lines.append("")
    lines.extend(test_table.splitlines())
    lines.append("")

    lines.append("## Symbols and Definitions")
    lines.append("")
    lines.append(f"Source: `{rel(SYMBOLS_MD)}`")
    lines.append("")
    lines.append("```markdown")
    lines.append(read_text(SYMBOLS_MD).rstrip())
    lines.append("```")
    lines.append("")

    lines.append("## Claims Register")
    lines.append("")
    lines.append(f"Source: `{rel(CLAIMS_REGISTER_MD)}`")
    lines.append("")
    lines.append("```markdown")
    lines.append(read_text(CLAIMS_REGISTER_MD).rstrip())
    lines.append("```")
    lines.append("")

    lines.append("## Derivations (All)")
    lines.append("")
    derivations = iter_sorted(list(DERIVATIONS_DIR.glob("qng-c-*.md")), qng_numeric=True)
    for path in derivations:
        lines.append(f"### {path.name}")
        lines.append("")
        lines.append(f"Path: `{rel(path)}`")
        lines.append("")
        lines.append("```markdown")
        lines.append(read_text(path).rstrip())
        lines.append("```")
        lines.append("")

    lines.append("## Validation Evidence (All)")
    lines.append("")
    evidence_paths = iter_sorted(
        [p for p in EVIDENCE_DIR.glob("qng-t-*.md") if p.is_file()],
        qng_numeric=True,
    )
    for path in evidence_paths:
        lines.append(f"### {path.name}")
        lines.append("")
        lines.append(f"Path: `{rel(path)}`")
        lines.append("")
        lines.append("```markdown")
        lines.append(read_text(path).rstrip())
        lines.append("```")
        lines.append("")

    lines.append("## Claim Files (All)")
    lines.append("")
    claim_paths = iter_sorted(list(CLAIMS_DIR.glob("QNG-C-*.md")), qng_numeric=True)
    for path in claim_paths:
        lines.append(f"### {path.name}")
        lines.append("")
        lines.append(f"Path: `{rel(path)}`")
        lines.append("")
        lines.append("```markdown")
        lines.append(read_text(path).rstrip())
        lines.append("```")
        lines.append("")

    lines.append("## Validation Plan Snapshot")
    lines.append("")
    lines.append(f"Source: `{rel(TEST_PLAN_MD)}`")
    lines.append("")
    lines.append("```markdown")
    lines.append(read_text(TEST_PLAN_MD).rstrip())
    lines.append("```")
    lines.append("")

    lines.append("## Validation Log Snapshot")
    lines.append("")
    lines.append(f"Source: `{rel(RESULTS_LOG_MD)}`")
    lines.append("")
    lines.append("```markdown")
    lines.append(read_text(RESULTS_LOG_MD).rstrip())
    lines.append("```")
    lines.append("")

    lines.append("## Dataset Manifest Snapshot")
    lines.append("")
    lines.append(f"Source: `{rel(DATASET_MANIFEST_MD)}`")
    lines.append("")
    lines.append("```markdown")
    lines.append(read_text(DATASET_MANIFEST_MD).rstrip())
    lines.append("```")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_md_blocks(md_text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_code = False
    for raw_line in md_text.splitlines():
        line = raw_line.rstrip("\n")

        if line.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            blocks.append(("code", line))
            continue

        if line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
            continue
        if line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            continue
        if line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            continue
        if line.startswith("- "):
            blocks.append(("li", line[2:].strip()))
            continue
        if line.startswith("|"):
            blocks.append(("code", line))
            continue
        if not line.strip():
            blocks.append(("blank", ""))
            continue
        blocks.append(("p", line))
    return blocks


def content_xml_from_blocks(blocks: list[tuple[str, str]]) -> str:
    body: list[str] = []
    for kind, text in blocks:
        esc = escape(text)
        if kind == "h1":
            body.append(f'<text:h text:style-name="H1" text:outline-level="1">{esc}</text:h>')
        elif kind == "h2":
            body.append(f'<text:h text:style-name="H2" text:outline-level="2">{esc}</text:h>')
        elif kind == "h3":
            body.append(f'<text:h text:style-name="H3" text:outline-level="3">{esc}</text:h>')
        elif kind == "li":
            body.append(f'<text:p text:style-name="List">- {esc}</text:p>')
        elif kind == "code":
            body.append(f'<text:p text:style-name="Code">{esc}</text:p>')
        elif kind == "blank":
            body.append('<text:p text:style-name="P"/>')
        else:
            body.append(f'<text:p text:style-name="P">{esc}</text:p>')

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-content
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:version="1.2">
  <office:scripts/>
  <office:font-face-decls>
    <style:font-face style:name="LiberationSerif" svg:font-family="Liberation Serif"/>
    <style:font-face style:name="LiberationMono" svg:font-family="Liberation Mono"/>
  </office:font-face-decls>
  <office:automatic-styles>
    <style:style style:name="P" style:family="paragraph">
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="10.5pt"/>
    </style:style>
    <style:style style:name="List" style:family="paragraph">
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="10.5pt"/>
    </style:style>
    <style:style style:name="Code" style:family="paragraph">
      <style:text-properties style:font-name="LiberationMono" fo:font-size="9pt"/>
    </style:style>
    <style:style style:name="H1" style:family="paragraph">
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="18pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="H2" style:family="paragraph">
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="14pt" fo:font-weight="bold"/>
    </style:style>
    <style:style style:name="H3" style:family="paragraph">
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="12pt" fo:font-weight="bold"/>
    </style:style>
  </office:automatic-styles>
  <office:body>
    <office:text>
      {"".join(body)}
    </office:text>
  </office:body>
</office:document-content>
"""


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<office:document-styles
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  office:version="1.2">
  <office:font-face-decls>
    <style:font-face style:name="LiberationSerif" svg:font-family="Liberation Serif"/>
    <style:font-face style:name="LiberationMono" svg:font-family="Liberation Mono"/>
  </office:font-face-decls>
  <office:styles>
    <style:default-style style:family="paragraph">
      <style:paragraph-properties fo:margin-top="0.0cm" fo:margin-bottom="0.12cm"/>
      <style:text-properties style:font-name="LiberationSerif" fo:font-size="10.5pt"/>
    </style:default-style>
  </office:styles>
  <office:automatic-styles>
    <style:page-layout style:name="pm1">
      <style:page-layout-properties
        fo:page-width="21.0cm"
        fo:page-height="29.7cm"
        style:print-orientation="portrait"
        fo:margin-top="1.8cm"
        fo:margin-bottom="1.8cm"
        fo:margin-left="1.8cm"
        fo:margin-right="1.8cm"/>
    </style:page-layout>
  </office:automatic-styles>
  <office:master-styles>
    <style:master-page style:name="Standard" style:page-layout-name="pm1"/>
  </office:master-styles>
</office:document-styles>
"""


def meta_xml() -> str:
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  office:version="1.2">
  <office:meta>
    <meta:generator>QNG Workspace Exporter</meta:generator>
    <meta:creation-date>{generated}</meta:creation-date>
  </office:meta>
</office:document-meta>
"""


def settings_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<office:document-settings
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  office:version="1.2">
  <office:settings/>
</office:document-settings>
"""


def manifest_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
  xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
  manifest:version="1.2">
  <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
  <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="styles.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="meta.xml" manifest:media-type="text/xml"/>
  <manifest:file-entry manifest:full-path="settings.xml" manifest:media-type="text/xml"/>
</manifest:manifest>
"""


def write_odt(markdown_text: str, out_path: Path) -> None:
    blocks = parse_md_blocks(markdown_text)
    content_xml = content_xml_from_blocks(blocks)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, "application/vnd.oasis.opendocument.text")

        zf.writestr("content.xml", content_xml.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("styles.xml", styles_xml().encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("meta.xml", meta_xml().encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("settings.xml", settings_xml().encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("META-INF/manifest.xml", manifest_xml().encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)


class PdfBuilder:
    def __init__(self) -> None:
        self.objects: list[bytes] = []

    def add_object(self, payload: bytes | str) -> int:
        data = payload if isinstance(payload, bytes) else payload.encode("latin-1", errors="replace")
        self.objects.append(data)
        return len(self.objects)

    def set_object(self, object_id: int, payload: bytes | str) -> None:
        data = payload if isinstance(payload, bytes) else payload.encode("latin-1", errors="replace")
        self.objects[object_id - 1] = data

    def write(self, path: Path, root_id: int) -> None:
        out = bytearray()
        out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets = [0]
        for idx, obj in enumerate(self.objects, start=1):
            offsets.append(len(out))
            out.extend(f"{idx} 0 obj\n".encode("ascii"))
            out.extend(obj)
            if not obj.endswith(b"\n"):
                out.extend(b"\n")
            out.extend(b"endobj\n")

        xref_start = len(out)
        out.extend(f"xref\n0 {len(self.objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("ascii"))
        out.extend(
            (
                f"trailer\n<< /Size {len(self.objects) + 1} /Root {root_id} 0 R >>\n"
                f"startxref\n{xref_start}\n%%EOF\n"
            ).encode("ascii")
        )
        path.write_bytes(bytes(out))


def pdf_escape(text: str) -> bytes:
    raw = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return raw.encode("latin-1", errors="replace")


def wrap_for_pdf(lines: list[str], max_chars: int = 96) -> list[str]:
    out: list[str] = []
    for line in lines:
        if not line:
            out.append("")
            continue
        wrapped = wrap(
            line,
            width=max_chars,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=False,
            drop_whitespace=False,
        )
        if not wrapped:
            out.append("")
        else:
            out.extend(wrapped)
    return out


def write_pdf(markdown_text: str, out_path: Path) -> None:
    lines = markdown_text.splitlines()
    lines = wrap_for_pdf(lines, max_chars=96)

    width = 595
    height = 842
    margin_left = 44
    margin_top = 48
    font_size = 10
    line_height = 13
    max_lines = int((height - (margin_top * 2)) / line_height)

    pages: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= max_lines:
            pages.append(current)
            current = []
    if current:
        pages.append(current)
    if not pages:
        pages = [[""]]

    pdf = PdfBuilder()
    pages_id = pdf.add_object("<< /Type /Pages /Count 0 /Kids [] >>")
    font_id = pdf.add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    page_ids: list[int] = []
    for page_lines in pages:
        ops: list[bytes] = []
        ops.append(b"BT")
        ops.append(f"/F1 {font_size} Tf".encode("ascii"))
        ops.append(f"{line_height} TL".encode("ascii"))
        ops.append(f"{margin_left} {height - margin_top} Td".encode("ascii"))
        first = True
        for line in page_lines:
            if not first:
                ops.append(b"T*")
            first = False
            ops.append(b"(" + pdf_escape(line) + b") Tj")
        ops.append(b"ET")
        stream = b"\n".join(ops) + b"\n"

        content_obj = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"endstream"
        )
        content_id = pdf.add_object(content_obj)
        page_id = pdf.add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {width} {height}] "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
        )
        page_ids.append(page_id)

    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    pdf.set_object(
        pages_id,
        f"<< /Type /Pages /Count {len(page_ids)} /Kids [ {kids} ] >>",
    )
    root_id = pdf.add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>")
    pdf.write(out_path, root_id=root_id)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a full QNG dossier to MD/ODT/PDF.")
    parser.add_argument(
        "--md-only",
        action="store_true",
        help="Only generate markdown and skip ODT/PDF conversion.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    markdown_text = build_markdown()
    OUT_MD.write_text(markdown_text, encoding="utf-8")

    if not args.md_only:
        write_odt(markdown_text, OUT_ODT)
        write_pdf(markdown_text, OUT_PDF)

    print(f"Generated: {rel(OUT_MD)}")
    if not args.md_only:
        print(f"Generated: {rel(OUT_ODT)}")
        print(f"Generated: {rel(OUT_PDF)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
