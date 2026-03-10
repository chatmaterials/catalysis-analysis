# catalysis-analysis

[![CI](https://img.shields.io/github/actions/workflow/status/chatmaterials/catalysis-analysis/ci.yml?branch=main&label=CI)](https://github.com/chatmaterials/catalysis-analysis/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/chatmaterials/catalysis-analysis?display_name=tag)](https://github.com/chatmaterials/catalysis-analysis/releases)

Standalone skill for catalysis-relevant DFT result analysis.

## Install

```bash
npx skills add chatmaterials/catalysis-analysis -g -y
```

## Local Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add . --list
python3 scripts/analyze_adsorption_energy.py fixtures/slab fixtures/adsorbate fixtures/adsorbed --json
python3 scripts/analyze_dband_center.py fixtures/projdos --json
python3 scripts/analyze_reaction_barrier.py fixtures/neb --json
python3 scripts/export_catalysis_report.py fixtures/slab fixtures/adsorbate fixtures/adsorbed --projdos-path fixtures/projdos --neb-path fixtures/neb
python3 scripts/run_regression.py
```
