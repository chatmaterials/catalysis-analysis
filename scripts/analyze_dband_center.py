#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalysis_io import read_projected_dos


def weighted_center(rows: list[tuple[float, float]]) -> tuple[float, float]:
    filtered = [(energy, weight) for energy, weight in rows if weight > 0.0]
    if not filtered:
        raise SystemExit("Projected DOS window contains no positive weights")
    denominator = sum(weight for _, weight in filtered)
    numerator = sum(energy * weight for energy, weight in filtered)
    return numerator / denominator, denominator


def analyze(path: Path, emin: float | None = None, emax: float | None = None, fermi: float | None = None) -> dict[str, object]:
    backend, rows, parsed_fermi = read_projected_dos(path)
    fermi_used = fermi if fermi is not None else (parsed_fermi if parsed_fermi is not None else 0.0)
    window_rows = [
        (energy, weight)
        for energy, weight in rows
        if (emin is None or energy >= emin) and (emax is None or energy <= emax)
    ]
    if not window_rows:
        raise SystemExit("No projected DOS rows fall inside the requested energy window")
    center, denominator = weighted_center(window_rows)
    occupied_rows = [(energy, weight) for energy, weight in window_rows if energy <= fermi_used]
    occupied_center = None
    occupied_weight = 0.0
    if occupied_rows:
        occupied_center, occupied_weight = weighted_center(occupied_rows)
    observations = ["Simple d-band center estimated from projected DOS weights."]
    if parsed_fermi is None and fermi is None:
        observations.append("No Fermi level was embedded in the input, so 0 eV was used as the occupied-state reference.")
    return {
        "path": str(path),
        "backend": backend,
        "fermi_eV": fermi_used,
        "energy_window_eV": [emin, emax],
        "d_band_center_eV": center,
        "integrated_weight": denominator,
        "occupied_d_band_center_eV": occupied_center,
        "occupied_integrated_weight": occupied_weight,
        "points_in_window": len(window_rows),
        "observations": observations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a simple d-band center from projected DOS data.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--emin", type=float)
    parser.add_argument("--emax", type=float)
    parser.add_argument("--fermi", type=float)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve(), args.emin, args.emax, args.fermi)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
