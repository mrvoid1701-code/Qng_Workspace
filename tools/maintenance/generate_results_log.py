#!/usr/bin/env python3
"""
Generate results log from 05_validation/test-plan.md.

Output:
- 05_validation/results-log.md
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
TEST_PLAN = ROOT / "05_validation" / "test-plan.md"
RESULTS_LOG = ROOT / "05_validation" / "results-log.md"

TEST_ID_RE = re.compile(r"^QNG-T-\d{3}$")
CLAIM_HEAD_RE = re.compile(r"^(QNG-C-\d{3}):\s+(.*)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_EXEC_STATUS = {
    "queued-p1",
    "queued-p2",
    "queued-p3",
    "in-progress",
    "pass",
    "fail",
    "blocked",
}
AUTHENTICITY_LEVELS = {"gold", "silver", "bronze"}
LEAKAGE_RISK_LEVELS = {"low", "med", "high"}
NEGATIVE_CONTROL_STATES = {"none", "planned", "done"}


@dataclass
class TestRow:
    test_id: str
    claim_id: str
    claim_statement: str
    derivation: str
    formula: str
    dataset: str
    method: str
    pass_condition: str
    fail_condition: str
    priority: str
    plan_status: str


@dataclass
class ExistingResultRow:
    exec_status: str
    last_run: str
    metric_value: str
    decision_note: str
    next_action: str
    authenticity: str
    leakage_risk: str
    negative_control: str


@dataclass
class RunJournalRow:
    run_id: str
    date: str
    scope: str
    tests_touched: str
    result_summary: str
    notes: str


def split_md_row(line: str) -> list[str]:
    raw = line.strip()
    if not raw.startswith("|") or not raw.endswith("|"):
        return []
    buf = raw[1:-1]
    cells: list[str] = []
    cur: list[str] = []
    i = 0
    while i < len(buf):
        ch = buf[i]
        if ch == "\\" and i + 1 < len(buf):
            # Preserve escaped sequences inside cell content.
            cur.append(ch)
            cur.append(buf[i + 1])
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


def locate_table(lines: list[str], header: str) -> tuple[int, int]:
    start = -1
    for idx, line in enumerate(lines):
        if line.strip() == header:
            start = idx + 2
            break
    if start < 0:
        return -1, -1
    end = start
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    return start, end


def parse_test_plan() -> list[TestRow]:
    if not TEST_PLAN.exists():
        raise FileNotFoundError(f"Missing test plan: {TEST_PLAN}")

    tests: list[TestRow] = []
    for line in TEST_PLAN.read_text(encoding="utf-8").splitlines():
        cells = split_md_row(line)
        if len(cells) != 10:
            continue
        if not TEST_ID_RE.match(cells[0]):
            continue
        claim_match = CLAIM_HEAD_RE.match(cells[1])
        if not claim_match:
            continue
        claim_id = claim_match.group(1)
        claim_statement = claim_match.group(2)
        priority = cells[8]
        if priority not in {"P1", "P2", "P3"}:
            continue
        tests.append(
            TestRow(
                test_id=cells[0],
                claim_id=claim_id,
                claim_statement=claim_statement,
                derivation=cells[2],
                formula=cells[3],
                dataset=cells[4],
                method=cells[5],
                pass_condition=cells[6],
                fail_condition=cells[7],
                priority=priority,
                plan_status=cells[9],
            )
        )
    return tests


def normalize_exec_status(value: str, priority: str) -> str:
    raw = value.strip().lower()
    alias = {
        "inprogress": "in-progress",
        "passed": "pass",
        "failed": "fail",
    }
    raw = alias.get(raw, raw)
    if raw in ALLOWED_EXEC_STATUS:
        return raw
    if raw in {"queued", "queue", "pending", "not-started"}:
        return initial_exec_status(priority)
    return initial_exec_status(priority)


def normalize_authenticity(value: str) -> str:
    raw = value.strip().lower()
    alias = {"g": "gold", "s": "silver", "b": "bronze"}
    raw = alias.get(raw, raw)
    return raw if raw in AUTHENTICITY_LEVELS else ""


def normalize_leakage_risk(value: str) -> str:
    raw = value.strip().lower()
    alias = {"medium": "med", "mid": "med", "m": "med", "l": "low", "h": "high"}
    raw = alias.get(raw, raw)
    return raw if raw in LEAKAGE_RISK_LEVELS else ""


def normalize_negative_control(value: str) -> str:
    raw = value.strip().lower()
    alias = {"na": "none", "n/a": "none", "nc": "none"}
    raw = alias.get(raw, raw)
    return raw if raw in NEGATIVE_CONTROL_STATES else ""


def default_review_meta(exec_status: str) -> tuple[str, str, str]:
    if exec_status == "pass":
        return ("bronze", "med", "planned")
    if exec_status == "in-progress":
        return ("bronze", "high", "planned")
    if exec_status.startswith("queued"):
        return ("bronze", "high", "none")
    if exec_status in {"fail", "blocked"}:
        return ("bronze", "high", "done")
    return ("bronze", "high", "none")


def parse_existing_run_journal(lines: list[str]) -> list[RunJournalRow]:
    start, end = locate_table(lines, "| Run ID | Date | Scope | Tests touched | Result summary | Notes |")
    if start < 0:
        return []

    rows: list[RunJournalRow] = []
    for idx in range(start, end):
        cells = split_md_row(lines[idx])
        if len(cells) != 6:
            continue
        if not cells[0].startswith("RUN-"):
            continue
        rows.append(
            RunJournalRow(
                run_id=cells[0],
                date=cells[1],
                scope=cells[2],
                tests_touched=cells[3],
                result_summary=cells[4],
                notes=cells[5],
            )
        )
    return rows


def parse_existing_results(lines: list[str]) -> dict[str, ExistingResultRow]:
    start, end = locate_table(
        lines,
        "| Test ID | Priority | Claim | Exec status | Last run | Evidence path | Metric / value | Decision note | Next action | authenticity | leakage_risk | negative_control |",
    )
    if start < 0:
        return {}

    out: dict[str, ExistingResultRow] = {}
    for idx in range(start, end):
        cells = split_md_row(lines[idx])
        if len(cells) not in {9, 12}:
            continue
        test_id = cells[0]
        if not TEST_ID_RE.match(test_id):
            continue
        priority = cells[1].strip()
        exec_status = normalize_exec_status(cells[3], priority)
        last_run = cells[4].strip() if DATE_RE.match(cells[4].strip()) else "YYYY-MM-DD"
        metric_value = cells[6].strip() or "TODO"
        decision_note = cells[7].strip() or "TODO"
        next_action = cells[8].strip()

        auth = normalize_authenticity(cells[9]) if len(cells) >= 12 else ""
        leak = normalize_leakage_risk(cells[10]) if len(cells) >= 12 else ""
        neg = normalize_negative_control(cells[11]) if len(cells) >= 12 else ""
        d_auth, d_leak, d_neg = default_review_meta(exec_status)

        out[test_id] = ExistingResultRow(
            exec_status=exec_status,
            last_run=last_run,
            metric_value=metric_value,
            decision_note=decision_note,
            next_action=next_action,
            authenticity=auth or d_auth,
            leakage_risk=leak or d_leak,
            negative_control=neg or d_neg,
        )
    return out


def esc(value: str) -> str:
    return value.replace("|", "\\|")


def test_num(test_id: str) -> int:
    return int(test_id.split("-")[-1])


def category_for(row: TestRow) -> str:
    dataset = row.dataset.lower()
    if "flyby/deep-space telemetry" in dataset:
        return "trajectory"
    if "lensing + rotation datasets" in dataset:
        return "lensing_dark"
    if "timing/waveforms" in dataset:
        return "timing_wave"
    if "discrete/n-body simulation environment" in dataset:
        return "simulation_nbody"
    if "analytical + symbolic limit analysis" in dataset:
        return "gr_limit"
    if "ensemble update simulation + operator fitting" in dataset:
        return "qm_qft"
    if "cosmological toy simulation / synthetic catalogs" in dataset:
        return "cosmo_sim"
    return "formal_math"


def category_label(category: str) -> str:
    labels = {
        "trajectory": "Trajectory",
        "lensing_dark": "Lensing/Dark",
        "timing_wave": "Timing/Wave",
        "simulation_nbody": "NBody",
        "gr_limit": "GR-Limit",
        "qm_qft": "QM/QFT",
        "cosmo_sim": "Cosmo-Sim",
        "formal_math": "Formal-Math",
    }
    return labels.get(category, category)


def base_action_for(category: str) -> str:
    actions = {
        "trajectory": "Collect trajectory residual dataset, run GR baseline, then fit tau lag term.",
        "lensing_dark": "Build lensing+rotation sample and fit Sigma-memory kernel vs GR+DM baseline.",
        "timing_wave": "Prepare cleaned timing/waveform residuals and fit tau/chi correction terms.",
        "simulation_nbody": "Run baseline vs memory-kernel N-body A/B with fixed seeds and metrics.",
        "gr_limit": "Run symbolic tau->0 and coarse-grain checks with conservation constraints.",
        "qm_qft": "Run ensemble update simulation and fit emergent effective operators.",
        "cosmo_sim": "Run node-growth simulation and test scaling/signature predictions.",
        "formal_math": "Complete algebra/unit/sign/limit checks in linked derivation.",
    }
    return actions.get(category, "Execute linked validation method.")


def next_action_for(row: TestRow) -> str:
    base = base_action_for(category_for(row))
    if row.priority == "P1":
        return f"Start now: {base}"
    if row.priority == "P2":
        return f"Queue after P1: {base}"
    return f"Run after P1/P2 freeze: {base}"


def evidence_path_for(row: TestRow) -> str:
    category = category_for(row)
    return f"05_validation/evidence/{row.test_id.lower()}-{category}.md"


def initial_exec_status(priority: str) -> str:
    return {"P1": "queued-p1", "P2": "queued-p2", "P3": "queued-p3"}.get(priority, "not-started")


def render_priority_batch(lines: list[str], priority: str, tests: list[TestRow]) -> None:
    lines.append(f"### {priority} Batch")
    lines.append("")
    lines.append("| Test ID | Claim | Category | First action | Evidence target | Batch status |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for t in tests:
        category = category_for(t)
        lines.append(
            f"| {t.test_id} | {t.claim_id} | {category_label(category)} | {esc(base_action_for(category))} | {evidence_path_for(t)} | queued |"
        )
    lines.append("")


def render(
    tests: list[TestRow],
    existing_results: dict[str, ExistingResultRow] | None = None,
    existing_runs: list[RunJournalRow] | None = None,
) -> str:
    existing_results = existing_results or {}
    existing_runs = existing_runs or []
    tests_sorted = sorted(tests, key=lambda t: test_num(t.test_id))
    p1_rows = [t for t in tests_sorted if t.priority == "P1"]
    p2_rows = [t for t in tests_sorted if t.priority == "P2"]
    p3_rows = [t for t in tests_sorted if t.priority == "P3"]
    p1 = len(p1_rows)
    p2 = len(p2_rows)
    p3 = len(p3_rows)
    total = len(tests)

    lines: list[str] = []
    lines.append("# Validation Results Log")
    lines.append("")
    lines.append("Execution log linked 1:1 with `05_validation/test-plan.md`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total tests: {total}")
    lines.append(f"- P1: {p1}")
    lines.append(f"- P2: {p2}")
    lines.append(f"- P3: {p3}")
    lines.append("- Status scale: `queued-p1` / `queued-p2` / `queued-p3` / `in-progress` / `pass` / `fail` / `blocked`")
    lines.append("- Release meta fields: `authenticity` (`gold|silver|bronze`), `leakage_risk` (`low|med|high`), `negative_control` (`none|planned|done`).")
    lines.append("")
    lines.append("## Run Journal")
    lines.append("")
    lines.append("| Run ID | Date | Scope | Tests touched | Result summary | Notes |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    if existing_runs:
        for run in existing_runs:
            lines.append(
                "| "
                + " | ".join(
                    [
                        esc(run.run_id),
                        esc(run.date),
                        esc(run.scope),
                        esc(run.tests_touched),
                        esc(run.result_summary),
                        esc(run.notes),
                    ]
                )
                + " |"
            )
    else:
        lines.append(
            "| RUN-P1-001 | YYYY-MM-DD | P1 batch execution | All P1 tests | pending | Execute highest-priority empirical checks first |"
        )
        lines.append("| RUN-P2-001 | YYYY-MM-DD | P2 batch execution | All P2 tests | pending | Start after P1 review/sign-off |")
        lines.append("| RUN-P3-001 | YYYY-MM-DD | P3 batch execution | All P3 tests | pending | Run formal checks after model freeze |")
    lines.append("")
    lines.append("## Priority Batches")
    lines.append("")
    lines.append("Checklist policy:")
    lines.append("- P1: run first and publish evidence files before touching P2.")
    lines.append("- P2: run after P1 review; keep parameter choices fixed unless justified.")
    lines.append("- P3: run last as consistency/regression gate.")
    lines.append("")
    render_priority_batch(lines, "P1", p1_rows)
    render_priority_batch(lines, "P2", p2_rows)
    render_priority_batch(lines, "P3", p3_rows)
    lines.append("## Per-Test Status")
    lines.append("")
    lines.append(
        "| Test ID | Priority | Claim | Exec status | Last run | Evidence path | Metric / value | Decision note | Next action | authenticity | leakage_risk | negative_control |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for t in tests_sorted:
        existing = existing_results.get(t.test_id)
        if existing:
            exec_status = existing.exec_status
            last_run = existing.last_run
            metric_value = existing.metric_value
            decision_note = existing.decision_note
            next_action = existing.next_action or next_action_for(t)
            authenticity = existing.authenticity
            leakage_risk = existing.leakage_risk
            negative_control = existing.negative_control
        else:
            exec_status = initial_exec_status(t.priority)
            last_run = "YYYY-MM-DD"
            metric_value = "TODO"
            decision_note = "TODO"
            next_action = next_action_for(t)
            authenticity = "bronze"
            leakage_risk = "high"
            negative_control = "none"
        lines.append(
            f"| {t.test_id} | {t.priority} | {t.claim_id}: {esc(t.claim_statement)} | {exec_status} | {last_run} | {evidence_path_for(t)} | {esc(metric_value)} | {esc(decision_note)} | {esc(next_action)} | {authenticity} | {leakage_risk} | {negative_control} |"
        )

    lines.append("")
    lines.append("## Execution Checklist")
    lines.append("")
    lines.append("### P1")
    lines.append("- Lock baseline assumptions.")
    lines.append("- Execute all P1 tests.")
    lines.append("- Attach evidence for each P1 test.")
    lines.append("- Review pass/fail decisions before moving to P2.")
    lines.append("")
    lines.append("### P2")
    lines.append("- Reuse P1-calibrated parameter set unless justified.")
    lines.append("- Execute all P2 tests grouped by data family.")
    lines.append("- Record any parameter drift with rationale.")
    lines.append("")
    lines.append("### P3")
    lines.append("- Run formal consistency checks after data tests stabilize.")
    lines.append("- Confirm unit/sign/limit checks for all linked derivations.")
    lines.append("- Mark blocking issues before next theory revision.")
    lines.append("")
    lines.append("## Evidence Checklist")
    lines.append("")
    lines.append("- Store plots/tables in `05_validation/evidence/`.")
    lines.append("- Keep raw outputs reproducible (script + command + parameters).")
    lines.append("- Link each decision note to at least one saved artifact.")
    lines.append("")
    lines.append("## Decision Rules")
    lines.append("")
    lines.append("1. Mark `pass` only when pass-condition is met with reproducible evidence.")
    lines.append("2. Mark `fail` when fail-condition is met and robustness checks are complete.")
    lines.append("3. Mark `blocked` only for external blockers (missing data, tooling, compute).")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    tests = parse_test_plan()
    existing_results: dict[str, ExistingResultRow] = {}
    existing_runs: list[RunJournalRow] = []
    if RESULTS_LOG.exists():
        existing_lines = RESULTS_LOG.read_text(encoding="utf-8").splitlines()
        existing_results = parse_existing_results(existing_lines)
        existing_runs = parse_existing_run_journal(existing_lines)
    RESULTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_LOG.write_text(render(tests, existing_results=existing_results, existing_runs=existing_runs), encoding="utf-8")
    print(f"Generated results log rows: {len(tests)}")
    print(f"Updated: {RESULTS_LOG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
