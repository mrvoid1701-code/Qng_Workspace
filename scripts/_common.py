#!/usr/bin/env python3
"""
Shared housekeeping helpers for QNG scripts.

Policy:
- stdlib only
- no scientific logic
- deterministic defaults
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
import random
import sys
from typing import Any


def configure_stdio_utf8() -> None:
    """Best-effort UTF-8 stdout/stderr on Windows terminals."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except Exception:
                pass


def add_standard_cli_args(
    parser: argparse.ArgumentParser,
    *,
    default_dataset_id: str = "DS-002",
    default_seed: int = 3401,
    default_out_dir: str,
    include_dataset: bool = True,
    include_seed: bool = True,
    include_plots: bool = True,
) -> argparse.ArgumentParser:
    """Attach standard housekeeping CLI flags used across gate scripts."""
    if include_dataset:
        parser.add_argument("--dataset-id", default=default_dataset_id)
    if include_seed:
        parser.add_argument("--seed", type=int, default=default_seed)
    parser.add_argument("--out-dir", "--outdir", dest="out_dir", default=default_out_dir)
    parser.add_argument(
        "--write-artifacts",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write CSV/JSON/PNG artifacts (default: true).",
    )
    if include_plots:
        parser.add_argument(
            "--plots",
            action=argparse.BooleanOptionalAction,
            default=True,
            help="Write plot artifacts (default: true). Supports --no-plots.",
        )
    return parser


def ensure_outdir(out_dir: str | Path) -> Path:
    path = Path(out_dir)
    if not path.is_absolute():
        path = path.resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def rng(seed: int) -> random.Random:
    return random.Random(seed)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_run_manifest(
    *,
    out_dir: Path,
    script_name: str,
    args_dict: dict[str, Any],
    gate_id: str,
    decision: str,
    elapsed_s: float,
    extras: dict[str, Any] | None = None,
) -> Path:
    """Write a small run-manifest JSON for reproducibility bookkeeping."""
    payload: dict[str, Any] = {
        "script": script_name,
        "gate_id": gate_id,
        "decision": decision,
        "elapsed_s": round(elapsed_s, 6),
        "run_utc": datetime.utcnow().isoformat() + "Z",
        "args": args_dict,
    }
    if extras:
        payload["extras"] = extras
    path = out_dir / "run-manifest.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

