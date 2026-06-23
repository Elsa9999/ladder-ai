# -*- coding: utf-8 -*-
"""
run_acceptance.py  (v2)
=======================
Automated Offline QA Acceptance Test Runner.

Exit codes:
  0 = all mandatory steps passed (optional failures do NOT block)
  1 = at least one mandatory step failed

Status values per step:
  PASS          - step succeeded (exit code 0)
  SKIP          - optional step exited with code 2 (readback not yet available)
  OPTIONAL_FAIL - optional step failed (exit code != 0 and != 2)
  FAIL          - mandatory step failed

Usage:
  python harness/run_acceptance.py
      Steps 1-5 mandatory, Step 6 optional (shows SKIP or OPTIONAL_FAIL)

  python harness/run_acceptance.py --require-readback
      Steps 1-6 all mandatory. Step 6 MUST pass.
"""

import os
import sys
import subprocess
import argparse

# ── Encoding ──────────────────────────────────────────────────────────────────
sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Core step runner (returns success, returncode) ────────────────────────────
def run_step(name, command):
    """Run a step command. Returns (success: bool, returncode: int)."""
    print(f"\n=========================================================")
    print(f" STEP: {name}")
    print(f" COMMAND: {' '.join(command)}")
    print(f"=========================================================")

    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            print("\n[ERRORS/WARNINGS]:")
            print(proc.stderr.strip())

        return proc.returncode == 0, proc.returncode

    except Exception as e:
        print(f"\n---> ERROR executing step '{name}': {e}")
        return False, -1


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Offline QA Acceptance Test Runner for Mixing_Nuoc_Tuong_Maggi_2026"
    )
    parser.add_argument(
        '--require-readback',
        action='store_true',
        help='Make Step 6 (post-import readback verification) mandatory. '
             'Use this AFTER running update_tia_project.exe successfully.'
    )
    args = parser.parse_args()
    require_readback = args.require_readback

    if require_readback:
        print("\n[MODE] --require-readback: Step 6 is MANDATORY.")
    else:
        print("\n[MODE] Normal mode: Step 6 is OPTIONAL (SKIP if readback not yet available).")

    print("=========================================================")
    print(" STARTING OFFLINE ACCEPTANCE RUNNER")
    print("=========================================================")

    # ── Step definitions ───────────────────────────────────────────────────
    steps = [
        {
            "name"    : "1. Generate PLC XML Project Files",
            "command" : [sys.executable, "projects/Mixing_Nuoc_Tuong_Maggi_2026/generate_mixing_project.py"],
            "optional": False,
        },
        {
            "name"    : "1.5. Validate PLC Tag Overlaps (Quality Gate)",
            "command" : [sys.executable, "scratch/validate_plc_overlaps.py"],
            "optional": False,
        },
        {
            "name"    : "2. Prepare & Distribute TIA Import Sets",
            "command" : [sys.executable, "projects/Mixing_Nuoc_Tuong_Maggi_2026/prepare_tia_import_sets.py"],
            "optional": False,
        },
        {
            "name"    : "2.5. Verify Mixing Runtime Fixes (P0/P1 Criteria)",
            "command" : [sys.executable, "scratch/verify_mixing_runtime_fixes.py"],
            "optional": False,
        },
        {
            "name"    : "3. Validate TIA XML Imports (Ladder-Only & QA Rules)",
            "command" : [sys.executable, "scratch/validate_tia_imports.py"],
            "optional": False,
        },
        {
            "name"    : "4. Verify Clean Folder (No Stale MB TCP DBs)",
            "command" : [sys.executable, "scratch/verify_clean.py"],
            "optional": False,
        },
        {
            "name"    : "5. Run Offline PLC Scan-Cycle Simulation Tests",
            "command" : [sys.executable, "scratch/test_plc_logic.py"],
            "optional": False,
        },
        {
            "name"    : "6. Verify Post-Import Export XML (post_import_export_manual)",
            "command" : [sys.executable, "scratch/verify_post_import_export_manual.py"],
            # optional = True unless --require-readback is set
            "optional": not require_readback,
            "readback": True,
        },
    ]

    results      = {}   # step_name → status string
    overall_pass = True

    for step in steps:
        name     = step["name"]
        optional = step.get("optional", False)

        success, returncode = run_step(name, step["command"])

        if success:
            status = "PASS"
            print(f"\n---> SUCCESS: {name} PASSED.")
        elif optional:
            # exit code 2 = explicit SKIP (readback not yet produced)
            if returncode == 2:
                status = "SKIP"
                print(f"\n---> SKIP: {name} – readback not yet available (run update_tia_project.exe first).")
            else:
                status = "OPTIONAL_FAIL"
                print(f"\n---> OPTIONAL_FAIL: {name} failed (exit code {returncode}) – optional, not blocking.")
        else:
            status = "FAIL"
            overall_pass = False
            print(f"\n---> FAILURE: {name} FAILED (exit code {returncode}).")

        results[name] = status

        # Stop on mandatory failure
        if not success and not optional:
            break

    # ── Summary dashboard ─────────────────────────────────────────────────
    print("\n=========================================================")
    print(" ACCEPTANCE SUMMARY DASHBOARD")
    print("=========================================================")
    for name, status in results.items():
        print(f" {name:<60} : [{status}]")
    print("=========================================================")

    # Count optional failures for informational note
    opt_fails = [n for n, s in results.items() if s == "OPTIONAL_FAIL"]
    skipped   = [n for n, s in results.items() if s == "SKIP"]

    if overall_pass:
        if opt_fails:
            print(f" OVERALL STATUS: MANDATORY CHECKS PASSED (QA OK)")
            print(f"   NOTE: {len(opt_fails)} optional step(s) failed – run after TIA import.")
        elif skipped:
            print(f" OVERALL STATUS: MANDATORY CHECKS PASSED (QA OK)")
            print(f"   NOTE: {len(skipped)} step(s) skipped – run update_tia_project.exe then re-run with --require-readback.")
        else:
            print(" OVERALL STATUS: ALL CHECKS PASSED (QA OK)")
        print("=========================================================")
        sys.exit(0)
    else:
        print(" OVERALL STATUS: QA ACCEPTANCE FAILED! PLEASE RE-CHECK LOGS")
        print("=========================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
