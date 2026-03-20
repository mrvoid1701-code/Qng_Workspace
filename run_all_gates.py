#!/usr/bin/env python3
"""
QNG Master Gate Runner - runs all G10-G20 gates in sequence and
produces a single consolidated health report.

Usage:
    python run_all_gates.py                        # DS-002, seed 3401
    python run_all_gates.py --dataset-id DS-003    # alternate dataset
    python run_all_gates.py --fast                 # skip slow gates (G17-G20)
    python run_all_gates.py --gate G17             # run single gate

Output:
    gates_summary.csv      - per-gate: status, key metric, value, threshold, margin%
    gates_summary.txt      - human-readable table
    gates_all_pass.flag    - created iff ALL gates pass (CI sentinel)
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT    = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
ARTS    = ROOT / "05_validation" / "evidence" / "artifacts"

# Gate registry
GATES = [
    dict(id="G10", script="run_qng_covariant_metric_v1.py",
         art_dir="qng-covariant-metric-v1",
         metric_csv="metric_checks_covariant.csv",
         label="Covariant ADM metric"),
    dict(id="G11", script="run_qng_einstein_eq_v1.py",
         art_dir="qng-einstein-eq-v1",
         metric_csv="metric_checks_einstein_eq.csv",
         label="Einstein equations"),
    dict(id="G12", script="run_qng_gr_solutions_v1.py",
         art_dir="qng-gr-solutions-v1",
         metric_csv="metric_checks_gr_solutions.csv",
         label="GR solutions (Schwarzschild)"),
    dict(id="G13", script="run_qng_covariant_wave_v1.py",
         art_dir="qng-covariant-wave-v1",
         metric_csv="metric_checks_covariant_wave.csv",
         label="Covariant wave equation"),
    dict(id="G14", script="run_qng_covariant_cons_v1.py",
         art_dir="qng-covariant-cons-v1",
         metric_csv="metric_checks_cov_cons.csv",
         label="Covariant conservation nabla(T)=0"),
    dict(id="G15", script="run_qng_ppn_v1.py",
         art_dir="qng-ppn-v1",
         metric_csv="metric_checks_ppn.csv",
         label="PPN parameters (gamma, beta, Shapiro)"),
    dict(id="G16", script="run_qng_action_v1.py",
         art_dir="qng-action-v1",
         metric_csv="metric_checks_action.csv",
         label="Action functional S[g,sigma]"),
    dict(id="G17", script="run_qng_g17_v2.py",
         art_dir="qng-g17-v2",
         metric_csv="metric_checks_g17_v2.csv",
         label="QM bridge: canonical quantisation (Jaccard)"),
    dict(id="G18", script="run_qng_qm_info_v1.py",
         art_dir="qng-qm-info-v1",
         metric_csv="metric_checks_qm_info.csv",
         label="Quantum information & emergent geometry"),
    dict(id="G19", script="run_qng_unruh_thermal_v1.py",
         art_dir="qng-unruh-thermal-v1",
         metric_csv="metric_checks_unruh.csv",
         label="Unruh thermal vacuum"),
    dict(id="G20", script="run_qng_semiclassical_v1.py",
         art_dir="qng-semiclassical-v1",
         metric_csv="metric_checks_semi.csv",
         label="Semiclassical back-reaction (GR<->QM)"),
]

SLOW_GATES = {"G17", "G18", "G19", "G20"}   # eigenmodes: ~3-5s each


# Helpers
def read_metric_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def margin_pct(value: str, threshold: str) -> float | None:
    """
    Compute how far the value is from the threshold as a fraction of the threshold.
    Returns None if not computable.
    """
    try:
        v = float(value)
        th = threshold.strip()
        if th.startswith(">"):
            t = float(th[1:])
            return (v - t) / abs(t) * 100 if t != 0 else None
        elif th.startswith("<"):
            t = float(th[1:])
            return (t - v) / abs(t) * 100 if t != 0 else None
        elif th.startswith("(") and "," in th:
            lo, hi = th.strip("()").split(",")
            t_lo, t_hi = float(lo), float(hi)
            dist_lo, dist_hi = v - t_lo, t_hi - v
            # normalise by the nearer bound's magnitude (not interval width)
            if dist_lo <= dist_hi:
                denom = abs(t_lo) if t_lo != 0 else abs(t_hi)
                return dist_lo / denom * 100 if denom else None
            else:
                denom = abs(t_hi) if t_hi != 0 else abs(t_lo)
                return dist_hi / denom * 100 if denom else None
    except Exception:
        pass
    return None


def run_gate(gate: dict, dataset_id: str, seed: int) -> dict:
    """Run a single gate script and return result dict."""
    script = SCRIPTS / gate["script"]
    cmd = [sys.executable, str(script),
           "--dataset-id", dataset_id, "--seed", str(seed)]
    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        elapsed = time.time() - t0
        exit_ok = result.returncode == 0
    except subprocess.TimeoutExpired:
        return dict(gate_id=gate["id"], label=gate["label"],
                    ran=False, exit_ok=False, elapsed=300.0,
                    decision="timeout", rows=[], error="timeout")
    except Exception as e:
        return dict(gate_id=gate["id"], label=gate["label"],
                    ran=False, exit_ok=False, elapsed=0.0,
                    decision="error", rows=[], error=str(e))

    # Read metric CSV from artifact dir (re-run may have updated it)
    art = ARTS / gate["art_dir"] / gate["metric_csv"]
    rows = read_metric_csv(art)

    decision = "pass" if exit_ok else "fail"
    # Cross-check with FINAL row in CSV
    for row in rows:
        if row.get("gate_id", "").upper() == "FINAL":
            decision = row.get("status", decision)
            break

    return dict(gate_id=gate["id"], label=gate["label"],
                ran=True, exit_ok=exit_ok, elapsed=elapsed,
                decision=decision, rows=rows, error="")


def gate_health(rows: list[dict]) -> list[dict]:
    """Return per-metric health with margin%."""
    out = []
    for row in rows:
        if row.get("gate_id", "").upper() == "FINAL":
            continue
        m = margin_pct(row.get("value", ""), row.get("threshold", ""))
        out.append(dict(
            sub_gate=row.get("gate_id", "?"),
            metric=row.get("metric", "?"),
            value=row.get("value", "?"),
            threshold=row.get("threshold", "?"),
            status=row.get("status", "?"),
            margin_pct=f"{m:.1f}" if m is not None else "n/a",
            alert="WARN" if (m is not None and m < 15.0) else "",
        ))
    return out


def print_summary(results: list[dict], elapsed_total: float) -> None:
    print()
    all_pass = all(r["decision"] == "pass" for r in results)
    print("+" + "-"*68 + "+")
    print("|  QNG GATE SUITE - SUMMARY                                        |")
    print("+" + "-"*68 + "+")

    for r in results:
        icon = "OK" if r["decision"] == "pass" else "FAIL"
        t = f"{r['elapsed']:.1f}s" if r["ran"] else "---"
        label = r["label"][:38].ljust(38)
        print(f"|  {icon:<4} {r['gate_id']}  {label}  {t:>6}  |")
    print("+" + "-"*68 + "+")

    status = "ALL PASS" if all_pass else "SOME FAIL"
    n_pass = sum(1 for r in results if r["decision"] == "pass")
    line = f"  {status}   {n_pass}/{len(results)} gates   total {elapsed_total:.1f}s".ljust(69)
    print(f"|{line}|")
    print("+" + "-"*68 + "+")

    fragile = []
    for r in results:
        for h in gate_health(r["rows"]):
            try:
                m = float(h["margin_pct"])
                if m < 20.0:
                    fragile.append((r["gate_id"], h["sub_gate"], h["metric"], h["value"], h["threshold"], h["margin_pct"]))
            except ValueError:
                pass
    if fragile:
        print("\n  WARN  FRAGILE METRICS (margin < 20%):")
        for gid, sg, metric, val, thr, mp in fragile:
            print(f"     {gid}/{sg}  {metric:<30} val={val}  thr={thr}  margin={mp}%")


# Main
def main() -> int:
    p = argparse.ArgumentParser(description="QNG master gate runner G10-G20.")
    p.add_argument("--dataset-id", default="DS-002")
    p.add_argument("--seed",       type=int, default=3401)
    p.add_argument("--fast",       action="store_true",
                   help="Skip slow gates (G17-G20, ~3-5s each)")
    p.add_argument("--gate",       help="Run only this gate (e.g. G17)")
    p.add_argument("--no-run",     action="store_true",
                   help="Read existing artifacts without re-running scripts")
    args = p.parse_args()

    gates_to_run = GATES
    if args.gate:
        gates_to_run = [g for g in GATES if g["id"].upper() == args.gate.upper()]
        if not gates_to_run:
            print(f"Unknown gate: {args.gate}")
            return 1
    elif args.fast:
        gates_to_run = [g for g in GATES if g["id"] not in SLOW_GATES]

    print(f"\nQNG Gate Suite  |  dataset={args.dataset_id}  seed={args.seed}")
    print(f"Running {len(gates_to_run)} gate(s)  "
          f"({'read-only' if args.no_run else 'execute'} mode)")
    print(f"Started: {datetime.utcnow().isoformat()}Z\n")

    results = []
    t_total_0 = time.time()

    for gate in gates_to_run:
        print(f"  [{gate['id']}] {gate['label']} ...", end="", flush=True)
        if args.no_run:
            art = ARTS / gate["art_dir"] / gate["metric_csv"]
            rows = read_metric_csv(art)
            decision = "unknown"
            for row in rows:
                if row.get("gate_id", "").upper() == "FINAL":
                    decision = row.get("status", "unknown")
            r = dict(gate_id=gate["id"], label=gate["label"],
                     ran=False, exit_ok=(decision == "pass"), elapsed=0.0,
                     decision=decision, rows=rows, error="")
        else:
            r = run_gate(gate, args.dataset_id, args.seed)

        icon = "OK" if r["decision"] == "pass" else "FAIL"
        print(f" {icon} ({r['elapsed']:.1f}s)")
        results.append(r)

    elapsed_total = time.time() - t_total_0

    # Print summary
    print_summary(results, elapsed_total)

    # Write gates_summary.csv
    out_rows = []
    for r in results:
        for h in gate_health(r["rows"]):
            out_rows.append(dict(
                gate_id=r["gate_id"],
                label=r["label"],
                gate_decision=r["decision"],
                sub_gate=h["sub_gate"],
                metric=h["metric"],
                value=h["value"],
                threshold=h["threshold"],
                status=h["status"],
                margin_pct=h["margin_pct"],
                alert=h["alert"],
            ))

    csv_path = ROOT / "gates_summary.csv"
    if out_rows:
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0]))
            w.writeheader()
            w.writerows(out_rows)
        print(f"\n  Gates summary written to: {csv_path}")

    # Write human-readable text
    txt_lines = [
        "QNG Gate Suite - Full Health Report",
        f"Generated: {datetime.utcnow().isoformat()}Z",
        f"Dataset: {args.dataset_id}  Seed: {args.seed}",
        "",
        f"{'Gate':<6} {'Label':<40} {'Decision':<8} {'Time':>6}",
        "-" * 68,
    ]
    for r in results:
        txt_lines.append(
            f"{r['gate_id']:<6} {r['label']:<40} {r['decision']:<8} "
            f"{r['elapsed']:>5.1f}s"
        )
    txt_lines += ["", "Sub-gate metrics:", "-" * 68]
    for r in results:
        for h in gate_health(r["rows"]):
            alert = h["alert"]
            txt_lines.append(
                f"  {r['gate_id']}/{h['sub_gate']:<8} {h['metric']:<30} "
                f"val={h['value']:<14} thr={h['threshold']:<20} "
                f"margin={h['margin_pct']:>6}%  {alert}"
            )

    (ROOT / "gates_summary.txt").write_text("\n".join(txt_lines), encoding="utf-8")

    # CI sentinel
    flag = ROOT / "gates_all_pass.flag"
    all_pass = all(r["decision"] == "pass" for r in results)
    if all_pass:
        flag.write_text(f"ALL_PASS  {datetime.utcnow().isoformat()}Z\n", encoding="utf-8")
    elif flag.exists():
        flag.unlink()

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())

