#!/usr/bin/env python3
"""
Extract text from a PDF into:
- one combined markdown file
- optional per-page markdown files
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "untitled"


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\x00", "")
    lines = [line.rstrip() for line in value.split("\n")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def write_combined(output_path: Path, source_pdf: Path, pages: list[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    chunks: list[str] = []
    chunks.append("# Source Text\n")
    chunks.append(f"- Source: `{source_pdf}`")
    chunks.append(f"- Generated: `{generated}`\n")

    for index, page_text in enumerate(pages, start=1):
        chunks.append(f"## Page {index}\n")
        chunks.append(page_text if page_text else "_NO_TEXT_EXTRACTED_")
        chunks.append("")

    output_path.write_text("\n".join(chunks), encoding="utf-8")


def write_per_page(pages_dir: Path, pages: list[str]) -> None:
    pages_dir.mkdir(parents=True, exist_ok=True)
    for index, page_text in enumerate(pages, start=1):
        target = pages_dir / f"page-{index:03d}.md"
        content = "\n".join(
            [
                f"# Page {index}",
                "",
                page_text if page_text else "_NO_TEXT_EXTRACTED_",
                "",
            ]
        )
        target.write_text(content, encoding="utf-8")


def extract(pdf_path: Path) -> list[str]:
    try:
        from pypdf import PdfReader
    except Exception:
        print("Missing dependency: pypdf", file=sys.stderr)
        print("Run: python -m pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(1)

    reader = PdfReader(str(pdf_path))
    pages: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(normalize_text(text))
    return pages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract text from PDF into markdown.")
    parser.add_argument("--input", required=True, help="Input PDF path")
    parser.add_argument(
        "--output",
        default="01_notes/source_text.md",
        help="Combined markdown output path",
    )
    parser.add_argument(
        "--pages-dir",
        default="01_notes/page_text",
        help="Directory for per-page markdown files",
    )
    parser.add_argument(
        "--no-pages-dir",
        action="store_true",
        help="Skip per-page file generation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Input PDF not found: {input_path}", file=sys.stderr)
        return 1

    pages = extract(input_path)
    output_path = Path(args.output)
    write_combined(output_path, input_path, pages)

    if not args.no_pages_dir:
        pages_dir = Path(args.pages_dir)
        write_per_page(pages_dir, pages)

    print(f"Extracted {len(pages)} pages from: {input_path}")
    print(f"Combined output: {output_path}")
    if not args.no_pages_dir:
        print(f"Per-page output dir: {args.pages_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
