#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=True)


def run_json(*args: str):
    return json.loads(run(*args).stdout)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    ads = run_json("scripts/analyze_adsorption_energy.py", "fixtures/slab", "fixtures/adsorbate", "fixtures/adsorbed", "--json")
    ensure(abs(ads["adsorption_energy_eV"] + 1.2) < 1e-6, "catalysis-analysis should parse adsorption energy")
    ensure(ads["backends"] == ["vasp"], "catalysis-analysis should identify the VASP backend for the default fixture")
    dband = run_json("scripts/analyze_dband_center.py", "fixtures/projdos", "--json")
    ensure(dband["d_band_center_eV"] < 0, "catalysis-analysis should place the d-band center below the Fermi level for the fixture")
    ensure(dband["occupied_d_band_center_eV"] is not None, "catalysis-analysis should compute an occupied d-band center")
    barrier = run_json("scripts/analyze_reaction_barrier.py", "fixtures/neb", "--json")
    ensure(abs(barrier["forward_barrier_eV"] - 0.7) < 1e-6, "catalysis-analysis should parse the forward barrier")
    ensure(barrier["backends"] == ["vasp"], "catalysis-analysis should identify the VASP backend for the default NEB fixture")
    qe_ads = run_json("scripts/analyze_adsorption_energy.py", "fixtures/qe/slab", "fixtures/qe/adsorbate", "fixtures/qe/adsorbed", "--json")
    ensure(abs(qe_ads["adsorption_energy_eV"] + 1.2) < 1e-3, "catalysis-analysis should support QE adsorption-energy inputs")
    abinit_ads = run_json("scripts/analyze_adsorption_energy.py", "fixtures/abinit/slab", "fixtures/abinit/adsorbate", "fixtures/abinit/adsorbed", "--json")
    ensure(abs(abinit_ads["adsorption_energy_eV"] + 1.2) < 1e-3, "catalysis-analysis should support ABINIT adsorption-energy inputs")
    qe_dband = run_json("scripts/analyze_dband_center.py", "fixtures/qe/projdos", "--json")
    ensure(qe_dband["backend"] == "qe", "catalysis-analysis should identify the QE backend for projected DOS fixtures")
    abinit_dband = run_json("scripts/analyze_dband_center.py", "fixtures/abinit/projdos", "--json")
    ensure(abinit_dband["backend"] == "abinit", "catalysis-analysis should identify the ABINIT backend for projected DOS fixtures")
    qe_barrier = run_json("scripts/analyze_reaction_barrier.py", "fixtures/qe/neb", "--json")
    ensure(abs(qe_barrier["forward_barrier_eV"] - 0.7) < 1e-3, "catalysis-analysis should support QE NEB-like image sets")
    abinit_barrier = run_json("scripts/analyze_reaction_barrier.py", "fixtures/abinit/neb", "--json")
    ensure(abs(abinit_barrier["forward_barrier_eV"] - 0.7) < 1e-3, "catalysis-analysis should support ABINIT NEB-like image sets")
    ranked = run_json("scripts/compare_catalyst_set.py", "fixtures", "fixtures/candidates/strong-bind", "--json")
    ensure(ranked["best_case"] == "fixtures", "catalysis-analysis should rank the balanced fixture ahead of the strong-binding case")
    temp_dir = Path(tempfile.mkdtemp(prefix="catalysis-analysis-report-"))
    try:
        report_path = Path(
            run(
                "scripts/export_catalysis_report.py",
                "fixtures/slab",
                "fixtures/adsorbate",
                "fixtures/adsorbed",
                "--projdos-path",
                "fixtures/projdos",
                "--neb-path",
                "fixtures/neb",
                "--output",
                str(temp_dir / "CATALYSIS_REPORT.md"),
            ).stdout.strip()
        )
        report_text = report_path.read_text()
        ensure("# Catalysis Analysis Report" in report_text, "catalysis report should have a heading")
        ensure("## Adsorption Energy" in report_text and "## d-band Center" in report_text and "## Reaction Barrier" in report_text, "catalysis report should include adsorption, d-band, and barrier sections")
        ensure("## Screening Note" in report_text, "catalysis report should include a screening note")
    finally:
        shutil.rmtree(temp_dir)
    print("catalysis-analysis regression passed")


if __name__ == "__main__":
    main()
