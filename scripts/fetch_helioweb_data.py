#!/usr/bin/env python3
"""Fetch HELIOWeb data via command-line POST request.

NASA endpoint:
https://omniweb.gsfc.nasa.gov/cgi/models/helios1.cgi
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError


DEFAULT_URL = "https://omniweb.gsfc.nasa.gov/cgi/models/helios1.cgi"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch HELIOWeb table output to a local file."
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"HELIOWeb POST endpoint (default: {DEFAULT_URL})",
    )
    parser.add_argument("--activity", default="retrieve")
    parser.add_argument("--object", default="04")
    parser.add_argument("--coordinate", default="1")
    parser.add_argument("--start-year", default="2000")
    parser.add_argument("--start-day", default="001")
    parser.add_argument("--stop-year", default="2000")
    parser.add_argument("--stop-day", default="366")
    parser.add_argument("--resolution", default="001")
    parser.add_argument("--equinox", default="2")
    parser.add_argument("--object2", default="")
    parser.add_argument(
        "--precn",
        default="",
        help="Optional decimal precision field used by some HELIOWeb forms",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="Additional raw payload param in key=value format (repeatable)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file path for HELIOWeb response text",
    )
    parser.add_argument(
        "--manifest-out",
        default="",
        help="Optional JSON manifest output path (default: <out>.manifest.json)",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds",
    )
    return parser.parse_args()


def build_payload(args: argparse.Namespace) -> Dict[str, str]:
    payload = {
        "activity": str(args.activity),
        "object": str(args.object),
        "coordinate": str(args.coordinate),
        "start_year": str(args.start_year),
        "start_day": str(args.start_day),
        "stop_year": str(args.stop_year),
        "stop_day": str(args.stop_day),
        "resolution": str(args.resolution),
        "equinox": str(args.equinox),
        "object2": str(args.object2),
    }
    if str(args.precn).strip():
        payload["precn"] = str(args.precn).strip()
    for item in args.param:
        if "=" not in item:
            raise ValueError(f"Invalid --param value (expected key=value): {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid --param key in: {item}")
        payload[key] = value
    return payload


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    encoded = urlencode(payload).encode("ascii")

    req = Request(
        args.url,
        data=encoded,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "qng-workspace/helioweb-fetcher",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=args.timeout_sec) as resp:  # nosec B310
            body = resp.read()
            status = getattr(resp, "status", None)
            content_type = resp.headers.get("Content-Type", "")
    except URLError as exc:
        print(f"HELIOWeb request failed: {exc}")
        return 2

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(body)

    manifest_path = (
        Path(args.manifest_out)
        if args.manifest_out
        else Path(str(out_path) + ".manifest.json")
    )
    manifest = {
        "source": "NASA HELIOWeb",
        "url": args.url,
        "http_status": status,
        "content_type": content_type,
        "payload": payload,
        "output_file": str(out_path),
        "output_size_bytes": len(body),
        "output_sha256": sha256_bytes(body),
        "cwd": os.getcwd(),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=True), encoding="utf-8"
    )

    print(f"Wrote HELIOWeb response to: {out_path}")
    print(f"Wrote manifest to: {manifest_path}")
    print(f"HTTP status: {status}; bytes: {len(body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
