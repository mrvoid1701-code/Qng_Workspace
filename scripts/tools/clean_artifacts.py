#!/usr/bin/env python3
"""
Artifact hygiene helper for QNG workspace.

Scans git-modified/untracked files under:
- 05_validation/evidence/artifacts/
- 07_exports/

Categories:
- (A) generated outputs safe to delete/regenerate
- (B) important notes/docs to keep
- (C) source-code changes (should be committed)

Default mode is dry-run (report only).
"""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
TARGETS = (
    Path("05_validation/evidence/artifacts"),
    Path("07_exports"),
)

DEFAULT_KEEP_PATTERNS = (
    "*.md",
    "*.json",
    "*manifest*",
    "*hashes*",
    "run-log-*.txt",
)

SOURCE_EXTENSIONS = {
    ".py",
    ".pyi",
    ".ipynb",
    ".sh",
    ".ps1",
    ".bat",
    ".cmd",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".rs",
    ".go",
    ".js",
    ".ts",
}


def parse_keep_patterns(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_KEEP_PATTERNS
    out: list[str] = []
    for token in (x.strip() for x in raw.split(",")):
        if not token:
            continue
        if token.startswith(".") and "*" not in token and "?" not in token:
            out.append(f"*{token}")
        else:
            out.append(token)
    return tuple(out or DEFAULT_KEEP_PATTERNS)


def run_git_status() -> list[tuple[str, str]]:
    cmd = [
        "git",
        "-c",
        "core.quotepath=false",
        "status",
        "--porcelain=1",
        "--untracked-files=all",
        "--",
        *(str(t).replace("\\", "/") for t in TARGETS),
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "git status failed").strip()
        raise RuntimeError(msg)

    entries: list[tuple[str, str]] = []
    for raw_line in (proc.stdout or "").splitlines():
        if len(raw_line) < 4:
            continue
        status = raw_line[:2]
        path_part = raw_line[3:]
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]
        path_part = path_part.strip().strip('"')
        if path_part:
            entries.append((status, path_part.replace("\\", "/")))
    return entries


def matches_any(path_text: str, patterns: Iterable[str]) -> bool:
    lowered = path_text.lower()
    for pattern in patterns:
        p = pattern.strip()
        if not p:
            continue
        if fnmatch.fnmatch(lowered, p.lower()):
            return True
        if fnmatch.fnmatch(Path(lowered).name, p.lower()):
            return True
    return False


def is_source_path(path_text: str) -> bool:
    suffix = Path(path_text).suffix.lower()
    return suffix in SOURCE_EXTENSIONS


def categorize(
    entries: list[tuple[str, str]],
    keep_patterns: tuple[str, ...],
) -> tuple[list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    category_a: list[tuple[str, str]] = []
    category_b: list[tuple[str, str]] = []
    category_c: list[tuple[str, str]] = []

    for status, rel_path in entries:
        if is_source_path(rel_path):
            category_c.append((status, rel_path))
        elif matches_any(rel_path, keep_patterns):
            category_b.append((status, rel_path))
        else:
            category_a.append((status, rel_path))

    return category_a, category_b, category_c


def print_category(title: str, rows: list[tuple[str, str]]) -> None:
    print(f"\n{title} ({len(rows)})")
    if not rows:
        print("  - none")
        return
    for status, rel_path in rows:
        print(f"  - [{status}] {rel_path}")


def delete_files(rows: list[tuple[str, str]], dry_run: bool) -> tuple[int, int]:
    deleted = 0
    missing = 0
    for _, rel_path in rows:
        full_path = ROOT / rel_path
        if dry_run:
            print(f"  would delete: {rel_path}")
            continue
        if not full_path.exists():
            missing += 1
            continue
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        deleted += 1
        print(f"  deleted: {rel_path}")
    return deleted, missing


def remove_empty_dirs(root: Path) -> int:
    removed = 0
    if not root.exists():
        return removed
    for path in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            try:
                next(path.iterdir())
            except StopIteration:
                path.rmdir()
                removed += 1
            except OSError:
                pass
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report and optionally delete generated artifact/export files.",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Report only (default: true). Use --no-dry-run to apply deletion.",
    )
    parser.add_argument(
        "--delete-generated",
        action="store_true",
        help="Delete category (A) files only.",
    )
    parser.add_argument(
        "--keep-patterns",
        default=None,
        help="Comma-separated glob patterns for category (B) keep set.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    keep_patterns = parse_keep_patterns(args.keep_patterns)

    print("QNG artifact hygiene report")
    print(f"Repo root: {ROOT}")
    print(
        "Targets: "
        + ", ".join(str(t).replace("\\", "/") for t in TARGETS)
    )
    print(f"Keep patterns: {', '.join(keep_patterns)}")
    print(f"Mode: {'dry-run' if args.dry_run else 'apply'}")

    try:
        entries = run_git_status()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    cat_a, cat_b, cat_c = categorize(entries, keep_patterns)

    print(f"\nDetected git changes under targets: {len(entries)}")
    print_category("(A) generated outputs safe to delete/regenerate", cat_a)
    print_category("(B) important notes/docs to keep", cat_b)
    print_category("(C) source-code changes (should be committed)", cat_c)

    if args.delete_generated:
        print("\nDelete category (A):")
        deleted, missing = delete_files(cat_a, dry_run=args.dry_run)
        if args.dry_run:
            print(f"  planned deletions: {len(cat_a)}")
        else:
            empty_removed = 0
            for target in TARGETS:
                empty_removed += remove_empty_dirs(ROOT / target)
            print(f"  deleted files: {deleted}")
            print(f"  missing/already-gone: {missing}")
            print(f"  empty directories removed: {empty_removed}")
    else:
        print("\nDeletion skipped (use --delete-generated).")

    return 0


if __name__ == "__main__":
    sys.exit(main())
