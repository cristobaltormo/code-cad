"""Printer build volumes and material properties.

Build volumes are manufacturer-published X x Y x Z in mm (verified 2026-10,
see reference/data/standards.json). Use `cad printers`
to list them; pick one in spec.json ("printer": "<key>").
"""

def _load_printers():
    """Printer volumes come from the verified reference data (single source of truth)."""
    import json
    from pathlib import Path

    f = Path(__file__).parent / "reference" / "data" / "standards.json"
    out = {}
    try:
        for k, v in json.loads(f.read_text())["groups"]["printers"]["data"].items():
            if v.get("build_volume"):
                out[k] = (v["name"], list(v["build_volume"]))
    except (OSError, KeyError, ValueError):
        pass
    out["generic_220"] = ("Generic 220 mm bed", [220, 220, 250])
    return out


PRINTERS = _load_printers()

DEFAULT_PRINTER = "generic_220"

# density g/cm3, typical allowable strain for snap-fits (one-time / repeated)
MATERIALS = {
    "PLA": {"density": 1.24, "strain_once": 0.025, "strain_repeat": 0.015, "notes": "stiff, brittle; creeps above ~50 C"},
    "PETG": {"density": 1.27, "strain_once": 0.04, "strain_repeat": 0.025, "notes": "tough, good default for functional parts"},
    "ABS": {"density": 1.04, "strain_once": 0.05, "strain_repeat": 0.03, "notes": "needs enclosure; ~0.5-0.7% shrink"},
    "ASA": {"density": 1.07, "strain_once": 0.05, "strain_repeat": 0.03, "notes": "UV-stable ABS; outdoor parts"},
    "TPU": {"density": 1.21, "strain_once": 0.5, "strain_repeat": 0.3, "notes": "flexible 95A; no fine tolerances"},
    "PA": {"density": 1.14, "strain_once": 0.06, "strain_repeat": 0.04, "notes": "nylon; must be dried; hygroscopic"},
    "PC": {"density": 1.20, "strain_once": 0.06, "strain_repeat": 0.04, "notes": "high temp; enclosure required"},
}


def get_printer(key):
    key = key or DEFAULT_PRINTER
    if key not in PRINTERS:
        raise KeyError(f"unknown printer '{key}'. Known: {', '.join(PRINTERS)}")
    name, vol = PRINTERS[key]
    return {"key": key, "name": name, "build_volume": vol}


def wall_thickness(perimeters, line_width=0.45, layer_height=0.2):
    """Slicer-exact wall width for N perimeters (PrusaSlicer/Orca spacing model).

    Classic engine: spacing = w - h*(1 - pi/4). With Arachne (default in modern
    slicers) other widths also print cleanly, but integer-perimeter walls stay
    the strongest and most predictable.
    """
    import math

    spacing = line_width - layer_height * (1 - math.pi / 4)
    return round(line_width + (perimeters - 1) * spacing, 3)


def estimate_mass(volume_mm3, area_mm2, material="PLA", infill=0.15, shell=1.0):
    """Mass in grams for a typical print: solid shell `shell` mm thick + infill."""
    d = MATERIALS.get(material.upper(), MATERIALS["PLA"])["density"]
    shell_vol = min(volume_mm3, area_mm2 * shell)
    printed = shell_vol + infill * max(0.0, volume_mm3 - shell_vol)
    return round(printed / 1000 * d, 1), round(volume_mm3 / 1000 * d, 1)
