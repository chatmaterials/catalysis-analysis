#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from analyze_adsorption_energy import analyze as analyze_adsorption
from analyze_dband_center import analyze as analyze_dband
from analyze_reaction_barrier import analyze as analyze_barrier


def screening_note(adsorption: dict[str, object], barrier: dict[str, object] | None) -> str:
    regime = str(adsorption["binding_regime"])
    if barrier is None:
        return f"Adsorption falls in the `{regime}` regime; add a reaction-path calculation before ranking catalysts."
    barrier_value = float(barrier["forward_barrier_eV"])
    if regime == "intermediate-binding" and barrier_value <= 0.8:
        return "This case looks balanced in the simple descriptor space: intermediate adsorption and a modest forward barrier."
    if regime == "strong-binding":
        return "The simple descriptor space suggests strong binding; check whether the surface may be poisoned despite the barrier."
    if regime == "weak-binding":
        return "The simple descriptor space suggests weak binding; activity may be limited by reactant capture."
    return "Adsorption is intermediate, but the barrier remains high enough that kinetics may still dominate."


def render_markdown(adsorption: dict[str, object], dband: dict[str, object] | None, barrier: dict[str, object] | None) -> str:
    lines = [
        "# Catalysis Analysis Report",
        "",
        "## Adsorption Energy",
        f"- Parsed backends: `{', '.join(adsorption['backends'])}`",
        f"- Adsorption energy (eV): `{adsorption['adsorption_energy_eV']:.4f}`",
        f"- Binding regime: `{adsorption['binding_regime']}`",
        f"- Slab energy (eV): `{adsorption['slab_energy_eV']:.6f}`",
        f"- Adsorbate energy (eV): `{adsorption['adsorbate_energy_eV']:.6f}`",
        f"- Adsorbed energy (eV): `{adsorption['adsorbed_energy_eV']:.6f}`",
    ]
    if dband is not None:
        lines.extend(
            [
                "",
                "## d-band Center",
                f"- Parsed backend: `{dband['backend']}`",
                f"- d-band center (eV): `{dband['d_band_center_eV']:.4f}`",
                f"- Integrated projected weight: `{dband['integrated_weight']:.4f}`",
                f"- Occupied d-band center (eV): `{dband['occupied_d_band_center_eV']:.4f}`" if dband["occupied_d_band_center_eV"] is not None else "- Occupied d-band center (eV): `n/a`",
            ]
        )
    if barrier is not None:
        lines.extend(
            [
                "",
                "## Reaction Barrier",
                f"- Parsed backends: `{', '.join(barrier['backends'])}`",
                f"- Forward barrier (eV): `{barrier['forward_barrier_eV']:.4f}`",
                f"- Kinetic class: `{barrier['kinetic_class']}`",
                f"- Reverse barrier (eV): `{barrier['reverse_barrier_eV']:.4f}`",
                f"- Reaction energy (eV): `{barrier['reaction_energy_eV']:.4f}`",
                f"- Highest image: `{barrier['highest_image']}`",
            ]
        )
    lines.extend(["", "## Screening Note", f"- {screening_note(adsorption, barrier)}"])
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
