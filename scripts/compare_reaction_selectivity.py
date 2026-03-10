#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_reaction_barrier import analyze as analyze_barrier


def classify_selectivity(delta_barrier: float) -> str:
    if delta_barrier >= 0.3:
        return "strongly-selective"
    if delta_barrier >= 0.1:
        return "moderately-selective"
    if delta_barrier > 0.0:
        return "weakly-selective"
    return "non-selective-or-inverted"


def analyze(desired_path: Path, undesired_path: Path, desired_label: str, undesired_label: str) -> dict[str, object]:
    desired = analyze_barrier(desired_path)
    undesired = analyze_barrier(undesired_path)
    delta_barrier = float(undesired["forward_barrier_eV"]) - float(desired["forward_barrier_eV"])
    preferred = desired_label if delta_barrier > 0 else undesired_label
    return {
        "desired_label": desired_label,
        "undesired_label": undesired_label,
        "desired_forward_barrier_eV": desired["forward_barrier_eV"],
        "undesired_forward_barrier_eV": undesired["forward_barrier_eV"],
        "desired_kinetic_class": desired["kinetic_class"],
        "undesired_kinetic_class": undesired["kinetic_class"],
        "delta_barrier_eV": delta_barrier,
        "preferred_path": preferred,
        "selectivity_class": classify_selectivity(delta_barrier),
        "observations": [
            "Reaction selectivity was estimated from the forward-barrier difference between two competing pathways."
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare selectivity between two reaction pathways from NEB image sets.")
    parser.add_argument("--desired-path", required=True)
    parser.add_argument("--undesired-path", required=True)
    parser.add_argument("--desired-label", default="desired")
    parser.add_argument("--undesired-label", default="undesired")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(
        Path(args.desired_path).expanduser().resolve(),
        Path(args.undesired_path).expanduser().resolve(),
        args.desired_label,
        args.undesired_label,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
