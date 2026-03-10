---
name: "catalysis-analysis"
description: "Use when the task is to analyze catalysis-relevant quantities from DFT results, including adsorption energies, d-band center estimates, reaction barriers from NEB images, and compact markdown reports from finished calculations."
---

# Catalysis Analysis

Use this skill for catalysis-oriented post-processing rather than generic workflow setup.

## When to use

- estimate adsorption energies from slab, adsorbate, and adsorbed calculations
- summarize a simple d-band center from projected DOS data
- estimate reaction barriers from NEB image sets
- write a compact catalysis-analysis report from existing calculations

## Use the bundled helpers

- `scripts/analyze_adsorption_energy.py`
  Estimate an adsorption energy from slab, adsorbate, and adsorbed states.
- `scripts/analyze_dband_center.py`
  Estimate a simple d-band center from projected DOS data.
- `scripts/analyze_reaction_barrier.py`
  Estimate forward and reverse reaction barriers from a numbered image set.
- `scripts/export_catalysis_report.py`
  Export a markdown catalysis-analysis report.

## Guardrails

- Do not overinterpret adsorption energies without stating the reference states.
- Treat a simple d-band center as a descriptor, not a proof of catalytic activity.
- Distinguish reaction barriers from adsorption thermodynamics.
