#!/usr/bin/env python3
"""
QNG Master Runner — run_all.py

Orchestrează toți runnerii QNG cu filtre pe grupuri.

Usage:
    python scripts/run_all.py                          # rulează grupul 'gates' (default)
    python scripts/run_all.py --group all              # rulează tot
    python scripts/run_all.py --group trajectory       # doar trajectory tests
    python scripts/run_all.py --group metric           # metric hardening + bridges
    python scripts/run_all.py --group curl             # curl validation suite
    python scripts/run_all.py --group cosmo            # cosmology / CMB
    python scripts/run_all.py --group symbolic         # symbolic validation
    python scripts/run_all.py --group gr-guard         # GR regression guard (G10-G16)
    python scripts/run_all.py --group gates,metric     # mai multe grupuri

    python scripts/run_all.py --list                   # listează ce script intră în fiecare grup
    python scripts/run_all.py --dry-run                # arată comenzile fără să le execute

Extra flags passthrough (transmise fiecărui runner):
    --dataset-id DS-003
    --seed 42
    --no-plots
    --no-write-artifacts
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# GRUPURI
# ──────────────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).parent

GROUPS: dict[str, list[str]] = {
    # G-gates: derivații simbolice + validare matematică (G10-G20)
    "gates": [
        "run_qng_action_v1.py",
        "run_qng_conservation_v1.py",
        "run_qng_covariant_cons_v1.py",
        "run_qng_covariant_metric_v1.py",
        "run_qng_covariant_wave_v1.py",
        "run_qng_dynamics_wave_v1.py",
        "run_qng_einstein_v1.py",
        "run_qng_einstein_eq_v1.py",
        "run_qng_gr_solutions_v1.py",
        "run_qng_ppn_v1.py",
        "run_qng_qm_bridge_v1.py",
        "run_qng_qm_info_v1.py",
        "run_qng_semiclassical_v1.py",
        "run_qng_spectrum_v1.py",
        "run_qng_unruh_thermal_v1.py",
    ],
    # Metric hardening + bridge tests
    "metric": [
        "run_qng_metric_hardening_v1.py",
        "run_qng_metric_hardening_v2.py",
        "run_qng_metric_hardening_v3.py",
        "run_qng_metric_hardening_v4.py",
        "run_qng_metric_hardening_v5.py",
        "run_qng_metric_hardening_v6.py",
        "run_qng_metric_anti_leak_v1.py",
        "run_qng_metric_dynamics_v1.py",
        "run_qng_metric_gr_bridge_v1.py",
        "run_qng_metric_gr_bridge_v2.py",
    ],
    # Trajectory tests (flyby, Pioneer, nbody, timing)
    "trajectory": [
        "run_qng_t_028_trajectory.py",
        "run_qng_t_028_trajectory_real.py",
        "run_qng_t_028_sensitivity_v4.py",
        "run_qng_t_029_simulation_nbody.py",
        "run_qng_t_041_c086b3_scaling.py",
        "run_qng_t_042_timing_wave.py",
        "run_qng_t_pioneer_v1.py",
        "run_qng_t_trj_ctrl_001.py",
        "run_qng_t_geodesic_001.py",
        "run_qng_t_grsweep_001.py",
    ],
    # Curl validation suite
    "curl": [
        "run_qng_t_curl_001.py",
        "run_qng_t_curl_002.py",
        "run_qng_t_curl_003.py",
        "run_qng_t_curl_003_v2.py",
        "run_qng_t_curl_004.py",
        "run_qng_t_curl_005.py",
        "run_qng_t_curl_006.py",
    ],
    # Cosmologie / CMB / lensing / rotație / straton
    "cosmo": [
        "run_qng_p2_cosmo_suite.py",
        "run_qng_t_052_cmb_coherence.py",
        "run_qng_t_027_lensing_dark.py",
        "run_qng_t_027_negative_controls.py",
        "run_qng_t_sig_001.py",
        "run_qng_t_straton_001.py",
        "run_qng_t_straton_002.py",
        "run_qng_t_taumap_001.py",
        "run_qng_t_unify_hysteresis_001.py",
        "run_qng_t_v_volume_rules.py",
        "run_qng_t_039_rotation_baseline_upgrade.py",
    ],
    # Validare simbolică
    "symbolic": [
        "run_qng_p3_symbolic_validation.py",
    ],
    # Regression guard: baseline freeze check for GR gates G10..G16
    "gr-guard": [
        "run_qng_gr_regression_guard_v1.py",
    ],
    # Jaccard Informational Graph — toate gate-urile G10-G21 pe graf coord-free
    "jaccard": [
        "run_gr_gates_jaccard_v1.py",   # G10-G16
        "run_qng_g17_v2.py",            # G17 (QM bridge, geodesic distance)
        "run_qng_g18d_v2.py",           # G18a-G18d (d_s=4.0, threshold 3.5-4.5)
        "run_qng_g19_jaccard_v1.py",    # G19 Unruh thermal (BFS hop distance)
        "run_qng_g20_jaccard_v1.py",    # G20 Semiclassical back-reaction
        "run_qng_g21_thermo_v1.py",     # G21 Thermodynamic consistency (S≥0, C_V>0, F=U-TS)
    ],
}

# Ordinea recomandată pentru --group all
ALL_ORDER = [
    "gates",
    "jaccard",
    "gr-guard",
    "metric",
    "curl",
    "trajectory",
    "cosmo",
    "symbolic",
]

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

GREEN = "\033[32m"
RED   = "\033[31m"
YELLOW = "\033[33m"
BOLD  = "\033[1m"
RESET = "\033[0m"


def _configure_stdio_utf8() -> None:
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


def _color(text: str, code: str) -> str:
    if sys.stdout.isatty():
        return f"{code}{text}{RESET}"
    return text


def resolve_groups(group_arg: str) -> list[str]:
    """Transformă 'gates,metric' în lista de scripturi (fără duplicate)."""
    names = [g.strip() for g in group_arg.split(",")]
    if "all" in names:
        names = ALL_ORDER

    seen: set[str] = set()
    scripts: list[str] = []
    for name in names:
        if name not in GROUPS:
            print(f"[ERROR] Grup necunoscut: '{name}'. Disponibile: {', '.join(GROUPS)}, all")
            sys.exit(1)
        for s in GROUPS[name]:
            if s not in seen:
                seen.add(s)
                scripts.append(s)
    return scripts


def build_base_args(args: argparse.Namespace) -> list[str]:
    """Construiește lista de argumente passthrough de bază (fără flags condiționale)."""
    extra: list[str] = []
    if args.dataset_id:
        extra += ["--dataset-id", args.dataset_id]
    if args.seed is not None:
        extra += ["--seed", str(args.seed)]
    return extra


_flag_support_cache: dict[tuple[str, str], bool] = {}


def _supports_flag(script_path: Path, flag: str) -> bool:
    """Verifică dacă scriptul acceptă un flag (via --help). Rezultat cached."""
    key = (str(script_path), flag)
    if key not in _flag_support_cache:
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True, text=True, timeout=10,
            )
            _flag_support_cache[key] = flag in (result.stdout + result.stderr)
        except Exception:
            _flag_support_cache[key] = False
    return _flag_support_cache[key]


def get_cmd(script_path: Path, base_args: list[str], args: argparse.Namespace) -> list[str]:
    """Construiește comanda completă pentru un script, cu probe pentru flags opționale."""
    cmd = [sys.executable, str(script_path)]
    # Fiecare flag e trimis doar dacă scriptul îl acceptă
    if args.dataset_id and _supports_flag(script_path, "--dataset-id"):
        cmd += ["--dataset-id", args.dataset_id]
    if args.seed is not None and _supports_flag(script_path, "--seed"):
        cmd += ["--seed", str(args.seed)]
    if args.no_plots and _supports_flag(script_path, "--plots"):
        cmd.append("--no-plots")
    if args.no_artifacts and _supports_flag(script_path, "--write-artifacts"):
        cmd.append("--no-write-artifacts")
    return cmd


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    _configure_stdio_utf8()

    parser = argparse.ArgumentParser(
        description="QNG Master Runner — rulează runnerii selectați și raportează PASS/FAIL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--group", "-g",
        default="gates",
        help="Grup(uri) de rulat: gates, gr-guard, metric, trajectory, curl, cosmo, symbolic, all. "
             "Separate prin virgulă pentru mai multe. (default: gates)",
    )
    parser.add_argument("--list", "-l", action="store_true", help="Listează scripturi per grup și iese.")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Arată comenzile fără să le execute.")

    # Passthrough flags
    parser.add_argument("--dataset-id", default=None, help="Transmis fiecărui runner (ex: DS-003).")
    parser.add_argument("--seed", type=int, default=None, help="Seed transmis fiecărui runner.")
    parser.add_argument("--no-plots", action="store_true", help="Dezactivează generarea de plot-uri.")
    parser.add_argument("--no-write-artifacts", dest="no_artifacts", action="store_true",
                        help="Dezactivează scrierea artefactelor.")

    args = parser.parse_args()

    # ── --list ──
    if args.list:
        print(f"\n{'Grup':<14} {'Scripturi':>5}  Lista")
        print("─" * 70)
        for grp in ALL_ORDER:
            scripts = GROUPS[grp]
            print(f"\n{_color(grp, BOLD)} ({len(scripts)} scripturi):")
            for s in scripts:
                exists = "✓" if (SCRIPTS_DIR / s).exists() else _color("✗ LIPSEȘTE", RED)
                print(f"    {exists}  {s}")
        print()
        return

    # ── Rezolvă scripturi ──
    scripts = resolve_groups(args.group)
    base_args = build_base_args(args)

    print(f"\n{_color('QNG Master Runner', BOLD)}")
    print(f"Grup(uri): {_color(args.group, YELLOW)} → {len(scripts)} scripturi")
    if base_args:
        print(f"Base args: {' '.join(base_args)}")
    if args.no_plots:
        print("Plots: dezactivate (acolo unde scriptul suportă)")
    if args.dry_run:
        print(_color("[DRY RUN — nicio comandă nu va fi executată]", YELLOW))
    print("─" * 70)

    results: list[tuple[str, str, float]] = []  # (script, status, elapsed)

    for i, script in enumerate(scripts, 1):
        script_path = SCRIPTS_DIR / script
        label = script.removesuffix(".py")
        prefix = f"[{i:>2}/{len(scripts)}]"

        if not script_path.exists():
            print(f"{prefix} {_color('SKIP', YELLOW)} {label}  (fișier lipsă)")
            results.append((label, "SKIP", 0.0))
            continue

        cmd = get_cmd(script_path, base_args, args)
        print(f"{prefix} {label} ...", end="", flush=True)

        if args.dry_run:
            print(f"  {_color('DRY', YELLOW)}  {' '.join(cmd)}")
            results.append((label, "DRY", 0.0))
            continue

        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=False,   # lasă output-ul să curgă în terminal
                text=True,
                cwd=SCRIPTS_DIR.parent,
            )
            elapsed = time.monotonic() - t0
            ok = proc.returncode == 0
        except Exception as exc:
            elapsed = time.monotonic() - t0
            print(f"\n  {_color('ERROR', RED)}: {exc}")
            results.append((label, "ERROR", elapsed))
            continue

        status = _color("PASS", GREEN) if ok else _color("FAIL", RED)
        print(f"\r{prefix} {label:<55} {status}  ({elapsed:.1f}s)")
        results.append((label, "PASS" if ok else "FAIL", elapsed))

    # ── Raport final ──
    if args.dry_run:
        return

    print("\n" + "═" * 70)
    print(f"{_color('RAPORT FINAL', BOLD)}")
    print("═" * 70)

    passed  = [r for r in results if r[1] == "PASS"]
    failed  = [r for r in results if r[1] == "FAIL"]
    skipped = [r for r in results if r[1] in ("SKIP", "ERROR")]
    total_time = sum(r[2] for r in results)

    for label, status, elapsed in results:
        if status == "PASS":
            icon = _color("✓ PASS", GREEN)
        elif status == "FAIL":
            icon = _color("✗ FAIL", RED)
        else:
            icon = _color(f"~ {status}", YELLOW)
        print(f"  {icon}  {label}")

    print("─" * 70)
    summary_parts = [
        _color(f"{len(passed)} PASS", GREEN),
        _color(f"{len(failed)} FAIL", RED) if failed else f"{len(failed)} FAIL",
    ]
    if skipped:
        summary_parts.append(_color(f"{len(skipped)} SKIP/ERR", YELLOW))
    print(f"  {' · '.join(summary_parts)}  din {len(results)} scripturi  ({total_time:.1f}s total)")
    print("═" * 70 + "\n")

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
