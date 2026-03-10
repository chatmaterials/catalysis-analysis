#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_adsorption_energy import analyze as analyze_adsorption
from analyze_dband_center import analyze as analyze_dband
from analyze_reaction_barrier import analyze as analyze_barrier


def maybe_analyze_dband(root: Path) -> dict[str, object] | None:
    for name in ("projdos", "pdos", "dos"):
        candidate = root / name
        if candidate.exists():
            return analyze_dband(candidate)
    return None


def maybe_analyze_barrier(root: Path) -> dict[str, object] | None:
    candidate = root / "neb"
    return analyze_barrier(candidate) if candidate.exists() else None


def analyze_case(root: Path, target_adsorption: float) -> dict[str, object]:
    adsorption = analyze_adsorption(root / "slab", root / "adsorbate", root / "adsorbed")
    dband = maybe_analyze_dband(root)
    barrier = maybe_analyze_barrier(root)
    adsorption_penalty = abs(float(adsorption["adsorption_energy_eV"]) - target_adsorption)
    barrier_penalty = float(barrier["forward_barrier_eV"]) if barrier is not None else 0.0
    score = adsorption_penalty + barrier_penalty
    return {
        "case": root.name,
        "path": str(root),
        "backends": adsorption["backends"],
        "adsorption_energy_eV": adsorption["adsorption_energy_eV"],
        "binding_regime": adsorption["binding_regime"],
        "forward_barrier_eV": barrier["forward_barrier_eV"] if barrier is not None else None,
        "kinetic_class": barrier["kinetic_class"] if barrier is not None else None,
        "d_band_center_eV": dband["d_band_center_eV"] if dband is not None else None,
        "occupied_d_band_center_eV": dband["occupied_d_band_center_eV"] if dband is not None else None,
        "adsorption_penalty_eV": adsorption_penalty,
        "barrier_penalty_eV": barrier_penalty,
        "screening_score": score,
    }


def analyze_cases(paths: list[Path], target_adsorption: float) -> dict[str, object]:
    cases = [analyze_case(path, target_adsorption) for path in paths]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "target_adsorption_eV": target_adsorption,
        "ranking_basis": "screening_score = |E_ads - target| + forward_barrier",
        "cases": ranked,
        "best_case": ranked[0]["case"] if ranked else None,
        "observations": [
            "This is a compact screening heuristic intended for catalyst prioritization, not a microkinetic model."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank multiple catalyst cases with a simple adsorption-plus-barrier heuristic.")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--target-adsorption", type=float, default=-0.7)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases([Path(path).expanduser().resolve() for path in args.paths], args.target_adsorption)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
