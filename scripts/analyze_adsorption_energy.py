#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_energy(path: Path) -> float:
    outcar = path / "OUTCAR" if path.is_dir() else path
    text = outcar.read_text(errors="ignore")
    matches = re.findall(r"TOTEN\s*=\s*([\-0-9.Ee+]+)", text)
    if not matches:
        raise SystemExit(f"No TOTEN found in {outcar}")
    return float(matches[-1])


def analyze(slab: Path, adsorbate: Path, adsorbed: Path) -> dict[str, object]:
    e_slab = read_energy(slab)
    e_adsorbate = read_energy(adsorbate)
    e_adsorbed = read_energy(adsorbed)
    e_ads = e_adsorbed - e_slab - e_adsorbate
    return {
        "slab": str(slab),
        "adsorbate": str(adsorbate),
        "adsorbed": str(adsorbed),
        "slab_energy_eV": e_slab,
        "adsorbate_energy_eV": e_adsorbate,
        "adsorbed_energy_eV": e_adsorbed,
        "adsorption_energy_eV": e_ads,
        "observations": ["Adsorption energy estimated from slab, adsorbate, and adsorbed total energies."],
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
