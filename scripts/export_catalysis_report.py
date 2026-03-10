#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_adsorption_energy import analyze as analyze_adsorption
from analyze_dband_center import analyze as analyze_dband
from analyze_reaction_barrier import analyze as analyze_barrier


def render_markdown(adsorption: dict[str, object], dband: dict[str, object] | None, barrier: dict[str, object] | None) -> str:
    lines = [
        "# Catalysis Analysis Report",
        "",
        "## Adsorption Energy",
        f"- Adsorption energy (eV): `{adsorption['adsorption_energy_eV']:.4f}`",
        f"- Slab energy (eV): `{adsorption['slab_energy_eV']:.6f}`",
        f"- Adsorbate energy (eV): `{adsorption['adsorbate_energy_eV']:.6f}`",
        f"- Adsorbed energy (eV): `{adsorption['adsorbed_energy_eV']:.6f}`",
    ]
    if dband is not None:
        lines.extend(
            [
                "",
                "## d-band Center",
                f"- d-band center (eV): `{dband['d_band_center_eV']:.4f}`",
                f"- Integrated projected weight: `{dband['integrated_weight']:.4f}`",
            ]
        )
    if barrier is not None:
        lines.extend(
            [
                "",
                "## Reaction Barrier",
                f"- Forward barrier (eV): `{barrier['forward_barrier_eV']:.4f}`",
                f"- Reverse barrier (eV): `{barrier['reverse_barrier_eV']:.4f}`",
                f"- Reaction energy (eV): `{barrier['reaction_energy_eV']:.4f}`",
                f"- Highest image: `{barrier['highest_image']}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def default_output(source: Path) -> Path:
    return source / "CATALYSIS_REPORT.md" if source.is_dir() else source.parent / "CATALYSIS_REPORT.md"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a markdown catalysis-analysis report.")
    parser.add_argument("slab")
    parser.add_argument("adsorbate")
    parser.add_argument("adsorbed")
    parser.add_argument("--projdos-path")
    parser.add_argument("--neb-path")
    parser.add_argument("--output")
    args = parser.parse_args()

    slab = Path(args.slab).expanduser().resolve()
    adsorbate = Path(args.adsorbate).expanduser().resolve()
    adsorbed = Path(args.adsorbed).expanduser().resolve()
    adsorption = analyze_adsorption(slab, adsorbate, adsorbed)
    dband = analyze_dband(Path(args.projdos_path).expanduser().resolve()) if args.projdos_path else None
    barrier = analyze_barrier(Path(args.neb_path).expanduser().resolve()) if args.neb_path else None
    output = Path(args.output).expanduser().resolve() if args.output else default_output(adsorbed.parent)
    output.write_text(render_markdown(adsorption, dband, barrier))
    print(output)


if __name__ == "__main__":
    main()
