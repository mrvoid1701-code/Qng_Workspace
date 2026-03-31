#!/usr/bin/env python3
"""
Workspace consistency checks for QNG workflow artifacts.
"""

from __future__ import annotations

from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ROOT / "02_claims" / "claims-register.md"
CLAIM_FILES_DIR = ROOT / "02_claims" / "claims"
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"
DATASET_JSON = ROOT / "05_validation" / "dataset-manifest.json"
RUN_MANIFEST_DIR = ROOT / "05_validation" / "run-manifests"
PARAM_REG_JSON = ROOT / "04_models" / "parameter-registry.json"
EVIDENCE_DIR = ROOT / "05_validation" / "evidence"

CLAIM_RE = re.compile(
    r"^\|\s*(QNG-C-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)
TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")
AUTHENTICITY_LEVELS = {"gold", "silver", "bronze"}
LEAKAGE_RISK_LEVELS = {"low", "med", "high"}
NEGATIVE_CONTROL_STATES = {"none", "planned", "done"}
REQUIRED_CLAIM_SECTIONS = [
    "## Claim Statement",
    "## Assumptions",
    "## Mathematical Form",
    "## Potential Falsifier",
    "## Evidence / Notes",
    "## Next Action",
]


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


def parse_claims() -> list[dict]:
    rows: list[dict] = []
    for line in CLAIMS.read_text(encoding="utf-8").splitlines():
        m = CLAIM_RE.match(line.strip())
        if not m:
            continue
        rows.append(
            {
                "claim_id": m.group(1),
                "statement": m.group(2),
                "status": m.group(3),
                "confidence": m.group(4),
                "pages": m.group(5),
                "derivation": m.group(6),
            }
        )
    return rows


def read_claim_file_meta(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    head_end = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            head_end = idx
            break
    head_lines = lines[:head_end]
    head_text = "\n".join(head_lines)

    def grab(label: str) -> str:
        prefix = f"- {label}: "
        for line in head_lines:
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
        return ""

    title = ""
    for line in head_lines:
        if line.strip():
            title = line.strip()
            break

    return {
        "title": title,
        "status": grab("Status"),
        "confidence": grab("Confidence"),
        "pages": grab("Source page(s)"),
        "derivation": grab("Related derivation"),
        "register_source": grab("Register source"),
        "content": path.read_text(encoding="utf-8", errors="replace"),
        "head_text": head_text,
    }


def parse_test_plan() -> list[dict]:
    rows: list[dict] = []
    for line in TEST_PLAN.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        if not TEST_ID_RE.match(cells[0]):
            continue
        claim_match = CLAIM_HEAD_RE.match(cells[1])
        if not claim_match:
            continue
        rows.append(
            {
                "test_id": cells[0],
                "claim_id": claim_match.group(1),
                "derivation": cells[2],
                "dataset": cells[4],
                "priority": cells[8],
            }
        )
    return rows


def parse_results_rows() -> list[dict]:
    rows: list[dict] = []
    in_table = False
    malformed_count = 0
    for line in RESULTS_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| Test ID | Priority | Claim | Exec status |"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            cells = split_md_row(line)
            if len(cells) not in {9, 12}:
                malformed_count += 1
                continue
            if not TEST_ID_RE.match(cells[0]):
                continue
            claim_match = CLAIM_HEAD_RE.match(cells[2])
            if not claim_match:
                continue
            authenticity = cells[9].strip().lower() if len(cells) >= 12 else ""
            leakage_risk = cells[10].strip().lower() if len(cells) >= 12 else ""
            negative_control = cells[11].strip().lower() if len(cells) >= 12 else ""
            rows.append(
                {
                    "test_id": cells[0],
                    "priority": cells[1],
                    "claim_id": claim_match.group(1),
                    "status": cells[3],
                    "evidence_path": cells[5],
                    "authenticity": authenticity,
                    "leakage_risk": leakage_risk,
                    "negative_control": negative_control,
                }
            )
    if malformed_count:
        rows.append({"__malformed__": str(malformed_count)})
    return rows


def check() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not CLAIMS.exists():
        errors.append(f"Missing: {CLAIMS}")
        return errors, warnings
    if not TEST_PLAN.exists():
        errors.append(f"Missing: {TEST_PLAN}")
        return errors, warnings
    if not RESULTS_LOG.exists():
        errors.append(f"Missing: {RESULTS_LOG}")
        return errors, warnings

    claims = parse_claims()
    tests = parse_test_plan()
    results = parse_results_rows()
    malformed = [r for r in results if "__malformed__" in r]
    if malformed:
        errors.append(f"Malformed rows in results-log table: {malformed[0]['__malformed__']}")
        results = [r for r in results if "__malformed__" not in r]

    claim_ids = [c["claim_id"] for c in claims]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append("Duplicate claim IDs in claims-register.md")

    claim_by_id = {c["claim_id"]: c for c in claims}
    for claim_id, claim in sorted(claim_by_id.items()):
        claim_file = CLAIM_FILES_DIR / f"{claim_id}.md"
        if not claim_file.exists():
            errors.append(f"Missing claim file: {claim_file.relative_to(ROOT)}")
            continue

        meta = read_claim_file_meta(claim_file)
        if not meta:
            errors.append(f"Unreadable claim file: {claim_file.relative_to(ROOT)}")
            continue

        expected_title = f"# {claim_id}"
        if meta["title"] != expected_title:
            errors.append(
                f"{claim_file.relative_to(ROOT)} title mismatch: '{meta['title']}' (expected '{expected_title}')"
            )

        if meta["status"] != claim["status"]:
            errors.append(
                f"{claim_file.relative_to(ROOT)} status mismatch: '{meta['status']}' (expected '{claim['status']}')"
            )
        if meta["confidence"] != claim["confidence"]:
            errors.append(
                f"{claim_file.relative_to(ROOT)} confidence mismatch: '{meta['confidence']}' (expected '{claim['confidence']}')"
            )
        if meta["pages"] != claim["pages"]:
            errors.append(
                f"{claim_file.relative_to(ROOT)} source pages mismatch: '{meta['pages']}' (expected '{claim['pages']}')"
            )
        if meta["derivation"] != claim["derivation"]:
            errors.append(
                f"{claim_file.relative_to(ROOT)} derivation mismatch: '{meta['derivation']}' (expected '{claim['derivation']}')"
            )
        if meta["register_source"] != "02_claims/claims-register.md":
            errors.append(
                f"{claim_file.relative_to(ROOT)} invalid register source '{meta['register_source']}'"
            )

        content = meta["content"]
        for section in REQUIRED_CLAIM_SECTIONS:
            if section not in content:
                errors.append(f"{claim_file.relative_to(ROOT)} missing section '{section}'")

    for extra_file in sorted(CLAIM_FILES_DIR.glob("QNG-C-*.md")):
        if extra_file.stem.upper() not in claim_by_id:
            warnings.append(f"Claim file without register row: {extra_file.relative_to(ROOT)}")

    deriv_claims = [c for c in claims if c["derivation"].startswith("03_math/derivations/")]
    for c in deriv_claims:
        deriv_path = ROOT / c["derivation"]
        if not deriv_path.exists():
            errors.append(f"Missing derivation file: {c['derivation']}")

    tests_by_claim = {t["claim_id"]: t for t in tests}
    if len(tests_by_claim) != len(tests):
        errors.append("Duplicate claim mapping in test-plan.md")

    deriv_claim_ids = {c["claim_id"] for c in deriv_claims}
    test_claim_ids = {t["claim_id"] for t in tests}
    missing_tests = sorted(deriv_claim_ids - test_claim_ids)
    if missing_tests:
        errors.append(f"Claims with derivations missing in test-plan: {', '.join(missing_tests)}")

    extra_tests = sorted(test_claim_ids - deriv_claim_ids)
    if extra_tests:
        warnings.append(f"Test-plan claims without derivation link: {', '.join(extra_tests)}")

    result_test_ids = {r["test_id"] for r in results}
    plan_test_ids = {t["test_id"] for t in tests}
    missing_result_rows = sorted(plan_test_ids - result_test_ids)
    if missing_result_rows:
        errors.append(f"Tests missing in results-log table: {', '.join(missing_result_rows)}")

    for r in results:
        ev = ROOT / r["evidence_path"]
        if not ev.exists():
            errors.append(f"Missing evidence file: {r['evidence_path']}")
        status = str(r["status"]).strip().lower()
        if status == "pass":
            if r["authenticity"] not in AUTHENTICITY_LEVELS:
                errors.append(
                    f"{r['test_id']} is pass but has invalid authenticity '{r['authenticity']}' (expected gold|silver|bronze)"
                )
            if r["leakage_risk"] not in LEAKAGE_RISK_LEVELS:
                errors.append(
                    f"{r['test_id']} is pass but has invalid leakage_risk '{r['leakage_risk']}' (expected low|med|high)"
                )
            if r["negative_control"] not in NEGATIVE_CONTROL_STATES:
                errors.append(
                    f"{r['test_id']} is pass but has invalid negative_control '{r['negative_control']}' (expected none|planned|done)"
                )

    if not DATASET_JSON.exists():
        errors.append(f"Missing dataset manifest JSON: {DATASET_JSON}")
    else:
        data = json.loads(DATASET_JSON.read_text(encoding="utf-8"))
        dataset_names = {item.get("dataset_name", "") for item in data if isinstance(item, dict)}
        for t in tests:
            if t["dataset"] not in dataset_names:
                errors.append(f"Dataset missing in manifest: {t['dataset']}")

    if not PARAM_REG_JSON.exists():
        errors.append(f"Missing parameter registry JSON: {PARAM_REG_JSON}")
    else:
        params = json.loads(PARAM_REG_JSON.read_text(encoding="utf-8"))
        if "version" not in params:
            errors.append("parameter-registry.json missing 'version'")
        if "parameters" not in params or not isinstance(params["parameters"], list):
            errors.append("parameter-registry.json missing 'parameters' list")

    for t in tests:
        run_manifest = RUN_MANIFEST_DIR / f"{t['test_id'].lower()}.json"
        if not run_manifest.exists():
            errors.append(f"Missing run manifest: {run_manifest.relative_to(ROOT)}")

    evidence_index = EVIDENCE_DIR / "README.md"
    if not evidence_index.exists():
        errors.append("Missing evidence index README.md")

    return errors, warnings


def main() -> int:
    errors, warnings = check()
    if warnings:
        print("[lint] warnings:")
        for w in warnings:
            print(f"  - {w}")
    if errors:
        print("[lint] errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[lint] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
