#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(path: Path) -> dict[str, object]:
    proj = path / "projdos.dat" if path.is_dir() else path
    rows = []
    for line in proj.read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        rows.append((float(parts[0]), float(parts[1])))
    if not rows:
        raise SystemExit("No projected DOS rows found")
    numerator = sum(energy * weight for energy, weight in rows)
    denominator = sum(weight for _, weight in rows)
    center = numerator / denominator
    return {
        "path": str(path),
        "d_band_center_eV": center,
        "integrated_weight": denominator,
        "observations": ["Simple d-band center estimated from projected DOS weights."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a simple d-band center from projected DOS data.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = analyze(Path(args.path).expanduser().resolve())
    if args.json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
