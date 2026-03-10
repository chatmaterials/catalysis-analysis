#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_adsorption_energy import analyze as analyze_adsorption


def analyze(
    slab: Path,
    adsorbate_a: Path,
    adsorbed_a: Path,
    adsorbate_b: Path,
    adsorbed_b: Path,
    label_a: str,
    label_b: str,
) -> dict[str, object]:
    result_a = analyze_adsorption(slab, adsorbate_a, adsorbed_a)
    result_b = analyze_adsorption(slab, adsorbate_b, adsorbed_b)
    delta = float(result_b["adsorption_energy_eV"]) - float(result_a["adsorption_energy_eV"])
    preferred = label_b if delta < 0 else label_a
    return {
        "slab": str(slab),
        "label_a": label_a,
        "label_b": label_b,
        "adsorption_energy_a_eV": result_a["adsorption_energy_eV"],
        "adsorption_energy_b_eV": result_b["adsorption_energy_eV"],
        "delta_adsorption_eV": delta,
        "preferred_adsorbate": preferred,
        "preference_strength": abs(delta),
        "observations": [
            "Selectivity was estimated from the difference between two adsorption energies on the same slab."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare adsorption selectivity between two adsorbates on the same slab.")
    parser.add_argument("--slab", required=True)
    parser.add_argument("--adsorbate-a", required=True)
    parser.add_argument("--adsorbed-a", required=True)
    parser.add_argument("--adsorbate-b", required=True)
    parser.add_argument("--adsorbed-b", required=True)
    parser.add_argument("--label-a", default="A")
    parser.add_argument("--label-b", default="B")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.slab).expanduser().resolve(),
        Path(args.adsorbate_a).expanduser().resolve(),
        Path(args.adsorbed_a).expanduser().resolve(),
        Path(args.adsorbate_b).expanduser().resolve(),
        Path(args.adsorbed_b).expanduser().resolve(),
        args.label_a,
        args.label_b,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
