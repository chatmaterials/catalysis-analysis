#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalysis_io import read_energy


def analyze(slab: Path, adsorbate: Path, adsorbed: Path) -> dict[str, object]:
    slab_backend, e_slab = read_energy(slab)
    adsorbate_backend, e_adsorbate = read_energy(adsorbate)
    adsorbed_backend, e_adsorbed = read_energy(adsorbed)
    backends = sorted({slab_backend, adsorbate_backend, adsorbed_backend})
    e_ads = e_adsorbed - e_slab - e_adsorbate
    observations = ["Adsorption energy estimated from slab, adsorbate, and adsorbed total energies."]
    if len(backends) == 1:
        observations.append(f"All three states were parsed as {backends[0]}-style results.")
    else:
        observations.append("Mixed backends were detected across the reference states.")
    return {
        "slab": str(slab),
        "adsorbate": str(adsorbate),
        "adsorbed": str(adsorbed),
        "backends": backends,
        "slab_energy_eV": e_slab,
        "adsorbate_energy_eV": e_adsorbate,
        "adsorbed_energy_eV": e_adsorbed,
        "adsorption_energy_eV": e_ads,
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate an adsorption energy from three states.")
    parser.add_argument("slab")
    parser.add_argument("adsorbate")
    parser.add_argument("adsorbed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.slab).expanduser().resolve(),
        Path(args.adsorbate).expanduser().resolve(),
        Path(args.adsorbed).expanduser().resolve(),
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
