#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_adsorption_energy import analyze as analyze_adsorption


def classify_preference(delta_e: float) -> str:
    if delta_e >= 0.3:
        return "strong-site-preference"
    if delta_e >= 0.1:
        return "moderate-site-preference"
    return "weak-site-preference"


def parse_site_specs(raw_specs: list[str]) -> list[tuple[str, Path]]:
    specs = []
    for raw in raw_specs:
        if "=" not in raw:
            raise SystemExit(f"Invalid --site specification `{raw}`; expected LABEL=PATH")
        label, path = raw.split("=", 1)
        specs.append((label.strip(), Path(path).expanduser().resolve()))
    return specs


def analyze(slab: Path, adsorbate: Path, site_specs: list[tuple[str, Path]]) -> dict[str, object]:
    if len(site_specs) < 2:
        raise SystemExit("Provide at least two --site LABEL=PATH specifications")
    records = []
    for label, adsorbed in site_specs:
        payload = analyze_adsorption(slab, adsorbate, adsorbed)
        records.append(
            {
                "site": label,
                "path": str(adsorbed),
                "adsorption_energy_eV": payload["adsorption_energy_eV"],
                "binding_regime": payload["binding_regime"],
            }
        )
    ranked = sorted(records, key=lambda item: float(item["adsorption_energy_eV"]))
    best = ranked[0]
    second = ranked[1]
    delta = float(second["adsorption_energy_eV"]) - float(best["adsorption_energy_eV"])
    return {
        "slab": str(slab),
        "adsorbate": str(adsorbate),
        "sites": ranked,
        "preferred_site": best["site"],
        "preference_gap_eV": delta,
        "site_preference_class": classify_preference(delta),
        "observations": [
            "Site preference was estimated by comparing adsorption energies across multiple adsorption geometries on the same slab."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare adsorption preference across multiple surface sites.")
    parser.add_argument("--slab", required=True)
    parser.add_argument("--adsorbate", required=True)
    parser.add_argument("--site", action="append", required=True, help="LABEL=PATH for an adsorbed-site result")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.slab).expanduser().resolve(),
        Path(args.adsorbate).expanduser().resolve(),
        parse_site_specs(args.site),
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
