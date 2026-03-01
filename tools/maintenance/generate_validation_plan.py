#!/usr/bin/env python3
"""
Generate 1:1 validation plan from claims and derivations.

Output:
- 05_validation/test-plan.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
CLAIMS_REGISTER = ROOT / "02_claims" / "claims-register.md"
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"


ROW_RE = re.compile(
    r"^\|\s*(QNG-C-\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)


@dataclass
class ClaimRow:
    claim_id: str
    statement: str
    status: str
    confidence: str
    pages: str
    derivation: str


TOP_PRIORITY_IDS = {
    "QNG-C-060",
    "QNG-C-086",
    "QNG-C-058",
    "QNG-C-082",
    "QNG-C-090",
    "QNG-C-091",
    "QNG-C-062",
}


def parse_claims() -> list[ClaimRow]:
    claims: list[ClaimRow] = []
    for line in CLAIMS_REGISTER.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        claims.append(
            ClaimRow(
                claim_id=m.group(1),
                statement=m.group(2),
                status=m.group(3),
                confidence=m.group(4),
                pages=m.group(5),
                derivation=m.group(6),
            )
        )
    return claims


def claim_num(claim_id: str) -> int:
    return int(claim_id.split("-")[-1])


def extract_formula(derivation_path: str) -> str:
    path = ROOT / derivation_path
    if not path.exists():
        return "formula_missing"
    lines = path.read_text(encoding="utf-8").splitlines()
    in_block = False
    eq_lines: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("```text") and not in_block:
            in_block = True
            continue
        if in_block and s.startswith("```"):
            break
        if in_block and s:
            eq_lines.append(s)
    if not eq_lines:
        return "formula_not_found"
    formula = eq_lines[0]
    formula = formula.replace("`", "")
    if len(formula) > 110:
        formula = formula[:107] + "..."
    return formula


def safe_cell(value: str) -> str:
    value = value.replace("|", "\\|")
    return value


def category_for(claim_id: str) -> str:
    cid = claim_id[-3:]
    if cid in {"025", "026", "055", "060", "086"}:
        return "trajectory"
    if cid in {"027", "037", "038", "040", "058", "082"}:
        return "lensing_dark"
    if cid in {"069", "090", "091", "078", "066"}:
        return "timing_wave"
    if cid in {"062"}:
        return "simulation_nbody"
    if cid in {"081", "093", "094"}:
        return "gr_limit"
    if cid in {"095", "096"}:
        return "qm_qft"
    if cid in {"103", "104", "107", "111"}:
        return "cosmo_sim"
    return "formal_math"


def method_for(category: str) -> tuple[str, str, str, str]:
    if category == "trajectory":
        return (
            "Flyby/deep-space telemetry (Galileo, NEAR, Rosetta, Cassini, Juno, Pioneer)",
            "Fit lag term a_res=-tau(v.nabla)nablaSigma on trajectory residuals vs GR-only baseline.",
            "Single tau-band improves fit metrics and residual direction matches prediction across missions.",
            "No significant fit improvement or inconsistent/random tau and sign across missions.",
        )
    if category == "lensing_dark":
        return (
            "Lensing + rotation datasets (Hubble, JWST, Euclid, Bullet-like clusters, RC catalogs)",
            "Fit Sigma-memory kernel model and compare against GR+particle-DM baseline.",
            "Offsets/profiles reproduced with stable memory parameters and consistent cross-dataset behavior.",
            "Model cannot reproduce offsets/profiles or needs unstable/nonphysical parameter tuning.",
        )
    if category == "timing_wave":
        return (
            "Timing/waveforms (GPS residuals, binary pulsars, LIGO/Virgo/KAGRA)",
            "Search tau/chi-linked corrections in TOA, clock and ringdown residuals after systematics control.",
            "Residual pattern remains significant and parameter-consistent after robustness checks.",
            "No robust tau/chi-linked residual remains once systematics and noise models are applied.",
        )
    if category == "simulation_nbody":
        return (
            "Discrete/N-body simulation environment",
            "Run memory-kernel N-body and compare morphology/kinematics against instantaneous-gravity baseline.",
            "Kernel model improves target metrics (offsets, halo evolution, structure coherence) reproducibly.",
            "No metric improvement or unstable dynamics under realistic parameter ranges.",
        )
    if category == "gr_limit":
        return (
            "Analytical + symbolic limit analysis",
            "Take tau->0 and coarse-grain graph dynamics; verify GR-form recovery and conservation constraints.",
            "Recovered equations match intended GR-form closure within defined approximation tolerance.",
            "GR limit cannot be recovered or violates core consistency/conservation requirements.",
        )
    if category == "qm_qft":
        return (
            "Ensemble update simulation + operator fitting",
            "Estimate effective operators from stochastic update ensembles and compare with claimed emergent forms.",
            "Controlled regime reproduces claimed Schrodinger-like / Klein-Gordon-like effective behavior.",
            "No stable emergent operator class consistent with the stated claim.",
        )
    if category == "cosmo_sim":
        return (
            "Cosmological toy simulation / synthetic catalogs",
            "Simulate node-growth + memory dynamics and test scaling/signature predictions.",
            "Predicted scaling/signatures appear across reasonable parameter bands without ad-hoc tuning.",
            "Signatures absent or only appear under nonphysical/extreme parameter tuning.",
        )
    return (
        "Symbolic math + dimensional analysis",
        "Check algebraic consistency, unit consistency and limit behavior against linked derivation.",
        "Equation is internally consistent, dimensionally valid and compatible with stated limit cases.",
        "Any dimensional contradiction, algebraic inconsistency or failed limit-case reproduction.",
    )


def priority_for(claim_id: str, category: str) -> str:
    if claim_id in TOP_PRIORITY_IDS:
        return "P1"
    if category in {"trajectory", "lensing_dark", "timing_wave", "simulation_nbody", "cosmo_sim"}:
        return "P2"
    return "P3"


def render_plan(claims: list[ClaimRow]) -> str:
    lines: list[str] = []
    lines.append("# Test Plan")
    lines.append("")
    lines.append("Validation matrix generated 1:1 from claims that have derivations.")
    lines.append("")
    lines.append("| Test ID | Claim | Derivation | Formula anchor | Dataset / Environment | Method | Pass condition | Fail condition | Priority | Status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")

    rows = sorted(claims, key=lambda c: claim_num(c.claim_id))
    for idx, claim in enumerate(rows, start=1):
        test_id = f"QNG-T-{idx:03d}"
        category = category_for(claim.claim_id)
        dataset, method, pass_cond, fail_cond = method_for(category)
        priority = priority_for(claim.claim_id, category)
        formula = extract_formula(claim.derivation)

        safe_statement = safe_cell(claim.statement)
        safe_formula = safe_cell(formula)
        safe_dataset = safe_cell(dataset)
        safe_method = safe_cell(method)
        safe_pass = safe_cell(pass_cond)
        safe_fail = safe_cell(fail_cond)

        lines.append(
            f"| {test_id} | {claim.claim_id}: {safe_statement} | {claim.derivation} | {safe_formula} | {safe_dataset} | {safe_method} | {safe_pass} | {safe_fail} | {priority} | draft |"
        )

    lines.append("")
    lines.append("## Execution Order")
    lines.append("")
    lines.append("1. Run all P1 tests first.")
    lines.append("2. Run P2 tests grouped by data family (trajectory, lensing, timing, simulations).")
    lines.append("3. Run P3 formal consistency tests after each major model revision.")
    lines.append("")
    lines.append("## Regeneration")
    lines.append("")
    lines.append("- `./.venv/Scripts/python.exe scripts/generate_validation_plan.py`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    claims = parse_claims()
    linked = [c for c in claims if c.derivation.startswith("03_math/derivations/")]
    TEST_PLAN.parent.mkdir(parents=True, exist_ok=True)
    TEST_PLAN.write_text(render_plan(linked), encoding="utf-8")
    print(f"Generated validation rows: {len(linked)}")
    print(f"Updated: {TEST_PLAN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
