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


def poisoning_penalty(binding_regime: str) -> float:
    if binding_regime == "strong-binding":
        return 1.5
    if binding_regime == "intermediate-binding":
        return 0.25
    return 0.0


def analyze_case(root: Path, target_adsorption: float, target_dband: float | None, mode: str) -> dict[str, object]:
    adsorption = analyze_adsorption(root / "slab", root / "adsorbate", root / "adsorbed")
    dband = maybe_analyze_dband(root)
    barrier = maybe_analyze_barrier(root)
    adsorption_penalty = abs(float(adsorption["adsorption_energy_eV"]) - target_adsorption)
    barrier_penalty = float(barrier["forward_barrier_eV"]) if barrier is not None else 0.0
    dband_penalty = 0.0
    if target_dband is not None and dband is not None:
        dband_penalty = 0.25 * abs(float(dband["d_band_center_eV"]) - target_dband)
    poison_penalty = poisoning_penalty(str(adsorption["binding_regime"]))
    if mode == "activity":
        score = 0.75 * adsorption_penalty + 1.5 * barrier_penalty + 0.5 * dband_penalty
    elif mode == "poisoning-resistant":
        score = 0.75 * adsorption_penalty + 0.5 * barrier_penalty + dband_penalty + 1.5 * poison_penalty
    elif mode == "descriptor":
        score = 0.5 * adsorption_penalty + 0.5 * barrier_penalty + 2.0 * dband_penalty
    else:
        score = adsorption_penalty + barrier_penalty + dband_penalty
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
        "dband_penalty_eV": dband_penalty,
        "poisoning_penalty": poison_penalty,
        "mode": mode,
        "screening_score": score,
    }


def analyze_cases(paths: list[Path], target_adsorption: float, target_dband: float | None, mode: str) -> dict[str, object]:
    cases = [analyze_case(path, target_adsorption, target_dband, mode) for path in paths]
    ranked = sorted(cases, key=lambda item: item["screening_score"])
    return {
        "target_adsorption_eV": target_adsorption,
        "target_dband_eV": target_dband,
        "mode": mode,
        "ranking_basis": "screening_score = weighted(adsorption_penalty, barrier_penalty, dband_penalty, poisoning_penalty)",
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
    parser.add_argument("--target-dband", type=float)
    parser.add_argument("--mode", choices=["balanced", "activity", "poisoning-resistant", "descriptor"], default="balanced")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze_cases([Path(path).expanduser().resolve() for path in args.paths], args.target_adsorption, args.target_dband, args.mode)
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
