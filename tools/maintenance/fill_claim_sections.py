#!/usr/bin/env python3
"""
Fill TODO sections in claim files using structured data from workspace artifacts.

Sections filled:
- Assumptions
- Mathematical Form
- Potential Falsifier
- Evidence / Notes
- Next Action

Default mode only updates claim files that still contain TODO markers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import re


ROOT = Path(__file__).resolve().parent.parent
CLAIM_FILES_DIR = ROOT / "02_claims" / "claims"
CLAIMS_REGISTER = ROOT / "02_claims" / "claims-register.md"
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"

CLAIM_ID_RE = re.compile(r"^QNG-C-\d{3}$")
TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-{3,}:?$")


@dataclass
class ClaimMeta:
    claim_id: str
    statement: str
    status: str
    confidence: str
    source_pages: str
    derivation: str


@dataclass
class TestMeta:
    test_id: str
    claim_id: str
    claim_statement: str
    derivation: str
    formula_anchor: str
    dataset_environment: str
    method: str
    pass_condition: str
    fail_condition: str
    priority: str
    plan_status: str
    exec_status: str
    evidence_path: str
    next_action: str


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


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(TABLE_SEPARATOR_RE.match(c.strip()) for c in cells)


def parse_claim_cell(value: str) -> tuple[str, str]:
    text = value.strip()
    m = CLAIM_HEAD_RE.match(text)
    if m:
        return m.group(1), m.group(2)
    if CLAIM_ID_RE.match(text):
        return text, ""
    return "", text


def parse_claims_register() -> dict[str, ClaimMeta]:
    out: dict[str, ClaimMeta] = {}
    for line in CLAIMS_REGISTER.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 6:
            continue
        claim_id = cells[0]
        if not CLAIM_ID_RE.match(claim_id):
            continue
        out[claim_id] = ClaimMeta(
            claim_id=claim_id,
            statement=cells[1],
            status=cells[2],
            confidence=cells[3],
            source_pages=cells[4],
            derivation=cells[5],
        )
    return out


def parse_results_table() -> dict[str, dict]:
    out: dict[str, dict] = {}
    lines = RESULTS_LOG.read_text(encoding="utf-8").splitlines()
    in_table = False
    for line in lines:
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
            out[cells[0]] = {
                "exec_status": cells[3],
                "evidence_path": cells[5],
                "next_action": cells[8],
            }
    return out


def parse_test_plan() -> dict[str, TestMeta]:
    result_rows = parse_results_table()
    out: dict[str, TestMeta] = {}
    for line in TEST_PLAN.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        test_id = cells[0]
        if not TEST_ID_RE.match(test_id):
            continue
        claim_id, claim_statement = parse_claim_cell(cells[1])
        if not claim_id:
            continue
        result = result_rows.get(test_id, {})
        out[claim_id] = TestMeta(
            test_id=test_id,
            claim_id=claim_id,
            claim_statement=claim_statement,
            derivation=cells[2],
            formula_anchor=cells[3],
            dataset_environment=cells[4],
            method=cells[5],
            pass_condition=cells[6],
            fail_condition=cells[7],
            priority=cells[8],
            plan_status=cells[9],
            exec_status=result.get("exec_status", ""),
            evidence_path=result.get("evidence_path", ""),
            next_action=result.get("next_action", ""),
        )
    return out


def sanitize(text: str) -> str:
    return " ".join(text.replace("|", "/").split())


def contains_any(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return any(term in low for term in terms)


def generate_assumptions(claim: ClaimMeta, test: TestMeta | None) -> list[str]:
    bullets = [
        "The claim is interpreted inside the discrete QNG graph ontology with local update dynamics.",
        "Symbol definitions follow `03_math/symbols.md`; units are SI-like unless explicitly normalized.",
    ]

    if claim.status == "formalized":
        bullets.append("A mathematically consistent formal closure is assumed for the core variables used by this claim.")
    elif claim.status == "derived":
        bullets.append("The statement is assumed to be a consequence of upstream formalized claims and update rules.")
    elif claim.status in {"predicted", "testable"}:
        bullets.append("The claim assumes measurable signatures can rise above noise and systematics in real data.")
    elif claim.status == "speculative":
        bullets.append("The statement is an extrapolation outside currently validated parameter regimes.")
    else:
        bullets.append("The statement is treated as a working hypothesis pending structured validation.")

    statement_low = claim.statement.lower()
    if contains_any(statement_low, ["lag", "tau", "flyby", "pioneer", "delay"]):
        bullets.append("A finite relaxation scale `tau` is assumed to produce delayed-response effects in dynamics.")
    elif contains_any(statement_low, ["lensing", "halo", "dark", "sigma"]):
        bullets.append("Historical-memory contributions to `Sigma` are assumed to be relevant for the modeled observable.")
    elif contains_any(statement_low, ["phase", "quantum", "decoherence", "superposition"]):
        bullets.append("Phase coherence and threshold dynamics are assumed to control the claimed emergent behavior.")
    elif contains_any(statement_low, ["gr", "einstein", "limit", "coarse"]):
        bullets.append("A well-defined coarse-grained limit is assumed to connect the discrete model to continuum behavior.")
    else:
        bullets.append("A finite-resolution discrete representation is assumed to be sufficient for this domain.")

    if test:
        bullets.append(
            f"The operational validation target is `{test.test_id}` ({test.priority}) with fixed method assumptions."
        )

    return bullets


def generate_math_form(claim: ClaimMeta, test: TestMeta | None) -> list[str]:
    bullets: list[str] = []

    if claim.derivation and claim.derivation != "n/a":
        bullets.append(f"Primary formalization is documented in `{claim.derivation}`.")
    else:
        bullets.append("No dedicated derivation file is linked yet; this claim currently has conceptual formal status.")

    if test and test.formula_anchor:
        bullets.append(f"Operational formula anchor: `{sanitize(test.formula_anchor)}`.")
    else:
        bullets.append(
            "Operational form should be expressed explicitly with measurable terms over `N_i`, `Sigma`, `chi`, `phi`, and `tau` as relevant."
        )

    bullets.append(
        "State space is modeled on graph variables with discrete updates `N_i(t+1)=U(N_i, neighbors, eta_i)` where applicable."
    )

    if test and test.dataset_environment:
        bullets.append(f"Quantitative interpretation is constrained by `{sanitize(test.dataset_environment)}`.")
    else:
        bullets.append("A dataset-linked quantitative closure is still required for full validation traceability.")

    return bullets


def generate_falsifier(claim: ClaimMeta, test: TestMeta | None) -> list[str]:
    if test:
        return [
            f"Direct falsifier from `{test.test_id}`: {sanitize(test.fail_condition)}",
            "Parameter consistency failure across datasets, trajectories, or runs under the same claimed mechanism.",
            "Loss of dimensional/sign consistency in the linked formalization when tested against boundary limits.",
        ]

    return [
        "A reproducible contradiction with core QNG axioms or mandatory consistency constraints.",
        "Failure to produce any measurable or simulation-level discriminator versus baseline alternatives.",
        "Internal unit/sign/limit inconsistency once explicit equations are written for this claim.",
    ]


def generate_evidence_notes(claim: ClaimMeta, test: TestMeta | None) -> list[str]:
    bullets = [
        f"Source grounding: `{claim.source_pages}` from `02_claims/claims-register.md`.",
        f"Register state: status `{claim.status}`, confidence `{claim.confidence}`.",
    ]

    if claim.derivation and claim.derivation != "n/a":
        bullets.append(f"Linked derivation: `{claim.derivation}`.")
    else:
        bullets.append("No direct derivation file is currently linked.")

    if test:
        detail = f"Mapped validation: `{test.test_id}` ({test.priority})"
        if test.exec_status:
            detail += f", exec status `{test.exec_status}`"
        detail += "."
        bullets.append(detail)
        if test.evidence_path:
            bullets.append(f"Evidence target: `{test.evidence_path}`.")
    else:
        bullets.append("No direct test-plan row is currently mapped to this claim.")

    return bullets


def generate_next_action(claim: ClaimMeta, test: TestMeta | None) -> list[str]:
    if test:
        actions = [
            f"Execute `{test.test_id}` ({test.priority}) using the defined method: {sanitize(test.method)}",
            "Record reproducible command, parameters, and outputs in the linked evidence file.",
            "Update `05_validation/results-log.md` with metric value, decision note, and next action after each run.",
        ]
        if test.evidence_path:
            actions[1] = f"Record reproducible command, parameters, and outputs in `{test.evidence_path}`."
        if test.next_action and test.next_action != "TODO":
            actions.append(f"Current queued step: {sanitize(test.next_action)}")
        return actions

    actions = [
        "Convert the claim into a testable form by defining at least one measurable observable and threshold.",
        "If mathematical, create or extend a derivation file in `03_math/derivations/` and link it in the claims register.",
        "Add a corresponding validation row in `05_validation/test-plan.md` with pass/fail criteria.",
    ]
    if claim.status in {"predicted", "testable"}:
        actions[0] = "Prioritize a concrete empirical discriminator and map it to a dataset-backed test protocol."
    return actions


def replace_section(text: str, section: str, bullets: list[str]) -> str:
    block = "\n".join(f"- {sanitize(item)}" for item in bullets).strip()
    pattern = re.compile(rf"(## {re.escape(section)}\n)(.*?)(?=\n## |\Z)", re.DOTALL)
    replacement = rf"\1\n{block}\n\n"
    return pattern.sub(replacement, text, count=1)


def should_update(text: str, force_all: bool) -> bool:
    if force_all:
        return True
    return "- TODO" in text


def process_claim_file(path: Path, claim: ClaimMeta, test: TestMeta | None, force_all: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    if not should_update(text, force_all):
        return False

    text = text.replace("\r\n", "\n")
    text = replace_section(text, "Assumptions", generate_assumptions(claim, test))
    text = replace_section(text, "Mathematical Form", generate_math_form(claim, test))
    text = replace_section(text, "Potential Falsifier", generate_falsifier(claim, test))
    text = replace_section(text, "Evidence / Notes", generate_evidence_notes(claim, test))
    text = replace_section(text, "Next Action", generate_next_action(claim, test))

    path.write_text(text.rstrip("\n") + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Fill claim sections from workspace metadata.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Rewrite sections for all claim files, not only files containing TODO.",
    )
    args = parser.parse_args()

    claims = parse_claims_register()
    tests = parse_test_plan()

    updated = 0
    missing_meta = 0

    for path in sorted(CLAIM_FILES_DIR.glob("QNG-C-*.md")):
        claim_id = path.stem.upper()
        claim = claims.get(claim_id)
        if not claim:
            missing_meta += 1
            continue
        test = tests.get(claim_id)
        if process_claim_file(path, claim, test, force_all=args.all):
            updated += 1

    print(f"Claim files updated: {updated}")
    if missing_meta:
        print(f"Claim files skipped (missing register row): {missing_meta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
