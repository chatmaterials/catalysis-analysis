# catalysis-analysis

[![CI](https://img.shields.io/github/actions/workflow/status/chatmaterials/catalysis-analysis/ci.yml?branch=main&label=CI)](https://github.com/chatmaterials/catalysis-analysis/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/chatmaterials/catalysis-analysis?display_name=tag)](https://github.com/chatmaterials/catalysis-analysis/releases)

Standalone skill for catalysis-relevant DFT result analysis, now with cross-backend energy support, mode-specific catalyst ranking, and both adsorption/pathway selectivity comparison.

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
python3 scripts/analyze_adsorption_energy.py fixtures/qe/slab fixtures/qe/adsorbate fixtures/qe/adsorbed --json
python3 scripts/analyze_adsorption_energy.py fixtures/abinit/slab fixtures/abinit/adsorbate fixtures/abinit/adsorbed --json
python3 scripts/compare_catalyst_set.py fixtures fixtures/candidates/strong-bind --target-dband -1.5 --mode balanced --json
python3 scripts/compare_catalyst_set.py fixtures fixtures/candidates/strong-bind fixtures/candidates/weak-fast --target-dband -1.5 --mode activity --json
python3 scripts/compare_catalyst_set.py fixtures fixtures/candidates/strong-bind fixtures/candidates/weak-fast --target-dband -1.5 --mode poisoning-resistant --json
python3 scripts/compare_adsorbate_selectivity.py --slab fixtures/selectivity/slab --adsorbate-a fixtures/selectivity/h2 --adsorbed-a fixtures/selectivity/h2_star --adsorbate-b fixtures/selectivity/co --adsorbed-b fixtures/selectivity/co_star --label-a H2 --label-b CO --json
python3 scripts/compare_reaction_selectivity.py --desired-path fixtures/pathways/desired --undesired-path fixtures/pathways/undesired --desired-label desired --undesired-label undesired --json
python3 scripts/compare_surface_sites.py --slab fixtures/sites/slab --adsorbate fixtures/sites/adsorbate --site top=fixtures/sites/top --site bridge=fixtures/sites/bridge --site hollow=fixtures/sites/hollow --json
python3 scripts/export_catalysis_report.py fixtures/slab fixtures/adsorbate fixtures/adsorbed --projdos-path fixtures/projdos --neb-path fixtures/neb
python3 scripts/run_regression.py
```
