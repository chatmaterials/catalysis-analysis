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
    dband = run_json("scripts/analyze_dband_center.py", "fixtures/projdos", "--json")
    ensure(dband["d_band_center_eV"] < 0, "catalysis-analysis should place the d-band center below the Fermi level for the fixture")
    barrier = run_json("scripts/analyze_reaction_barrier.py", "fixtures/neb", "--json")
    ensure(abs(barrier["forward_barrier_eV"] - 0.7) < 1e-6, "catalysis-analysis should parse the forward barrier")
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
    finally:
        shutil.rmtree(temp_dir)
    print("catalysis-analysis regression passed")


if __name__ == "__main__":
    main()
