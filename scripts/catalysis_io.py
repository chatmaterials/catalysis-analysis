#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


RY_TO_EV = 13.605693009
HARTREE_TO_EV = 27.211386018


def read_text(path: Path) -> str:
    return path.read_text(errors="ignore") if path.exists() else ""


def detect_backend(path: Path) -> str:
    root = path if path.is_dir() else path.parent
    names = {item.name for item in root.iterdir()} if root.exists() and root.is_dir() else set()
    if "OUTCAR" in names or path.name == "OUTCAR":
        return "vasp"
    if any(root.glob("*.in")) or any(root.glob("*.out")):
        return "qe"
    if any(root.glob("*.abi")) or any(root.glob("*.abo")):
        return "abinit"
    if path.is_dir() and any((path / candidate).exists() for candidate in ("projdos.dat", "pdos.dat", "dos.dat", "DOSCAR")):
        return "generic"
    if path.is_file():
        return "generic"
    raise SystemExit(f"Could not detect backend from {path}")


def read_energy(path: Path) -> tuple[str, float]:
    backend = detect_backend(path)
    root = path if path.is_dir() else path.parent
    if backend == "vasp":
        text = read_text(root / "OUTCAR" if root.is_dir() else path)
        matches = re.findall(r"TOTEN\s*=\s*([\-0-9.Ee+]+)", text)
        if not matches:
            raise SystemExit(f"No TOTEN found for VASP path {path}")
        return backend, float(matches[-1])
    if backend == "qe":
        out_files = sorted(root.glob("*.out"))
        if not out_files:
            raise SystemExit(f"No QE output file found in {root}")
        text = read_text(out_files[0])
        matches = re.findall(r"!\s+total energy\s+=\s+([\-0-9.DdEe+]+)\s+Ry", text)
        if not matches:
            raise SystemExit(f"No total energy found for QE path {path}")
        return backend, float(matches[-1].replace("D", "e").replace("d", "e")) * RY_TO_EV
    if backend == "abinit":
        abo_files = sorted(root.glob("*.abo"))
        out_file = abo_files[0] if abo_files else root / "run.abo"
        text = read_text(out_file)
        matches = re.findall(r"\betotal\s+([\-0-9.DdEe+]+)", text)
        if not matches:
            raise SystemExit(f"No etotal found for ABINIT path {path}")
        return backend, float(matches[-1].replace("D", "e").replace("d", "e")) * HARTREE_TO_EV
    raise SystemExit(f"Energy parsing is not supported for backend {backend}")


def _parse_doscar(path: Path) -> tuple[list[tuple[float, float]], float | None]:
    lines = read_text(path).splitlines()
    if len(lines) < 7:
        raise SystemExit(f"DOSCAR is too short to analyze in {path}")
    header = lines[5].split()
    nedos = int(float(header[2]))
    efermi = float(header[3])
    rows: list[tuple[float, float]] = []
    for line in lines[6 : 6 + nedos]:
        parts = line.split()
        if len(parts) < 2:
            continue
        rows.append((float(parts[0]), float(parts[1])))
    if not rows:
        raise SystemExit(f"No DOS rows found in {path}")
    return rows, efermi


def _parse_generic_spectrum(path: Path) -> tuple[list[tuple[float, float]], float | None]:
    rows: list[tuple[float, float]] = []
    fermi = None
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("#", "!")):
            fermi_match = re.search(r"fermi\s*[:=]\s*([\-0-9.DdEe+]+)", stripped, re.IGNORECASE)
            if fermi_match:
                fermi = float(fermi_match.group(1).replace("D", "e").replace("d", "e"))
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        try:
            rows.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    if not rows:
        raise SystemExit(f"No projected DOS rows found in {path}")
    return rows, fermi


def read_projected_dos(path: Path) -> tuple[str, list[tuple[float, float]], float | None]:
    backend = detect_backend(path)
    if path.is_file():
        rows, fermi = _parse_doscar(path) if path.name == "DOSCAR" else _parse_generic_spectrum(path)
        return backend, rows, fermi

    if backend == "vasp" and (path / "DOSCAR").exists():
        rows, fermi = _parse_doscar(path / "DOSCAR")
        return backend, rows, fermi

    candidates = [path / "projdos.dat", path / "pdos.dat", path / "dos.dat"]
    if backend == "qe":
        candidates.extend(sorted(path.glob("*pdos*.dat")))
        candidates.extend(sorted(path.glob("*.pdos*")))
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            rows, fermi = _parse_generic_spectrum(candidate)
            return backend, rows, fermi
    raise SystemExit(f"No projected DOS-like file found in {path}")
