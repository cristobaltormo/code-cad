"""Legacy single-shape inspection (kept for old scripts).

New work should use the project pipeline: `cad build / verify / printability /
attest / release` (see cad_tools/pipeline.py). This module now reuses the same
real checks (watertight STL, single solid, STL-vs-STEP volume) instead of the
old "is_valid and volume > 0" test, which passed broken models.
"""

from __future__ import annotations

import sys
from pathlib import Path

from build123d import export_step, export_stl

from cad_tools import measure
from cad_tools.meshcheck import check_mesh
from cad_tools.printers import estimate_mass


def generate_multiview_svg(shape, output_path, name="model"):
    """Write the views sheet; also writes a .png next to it for visual review."""
    from cad_tools.render import render_views

    out = Path(output_path)
    render_views(shape, out.with_suffix(".png"), out, name=name)
    return str(out)


def inspect_solid(shape, name="model", out_dir=".", export_files=True, material="PLA"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bb = measure.bbox(shape)
    mass, solid_mass = estimate_mass(bb["volume_mm3"], shape.area, material)
    lines = [f"### Model Inspection: {name}", "", "| Metric | Value |", "|---|---|",
             f"| Bounding Box (X x Y x Z) | {bb['size'][0]} x {bb['size'][1]} x {bb['size'][2]} mm |",
             f"| Volume | {bb['volume_mm3'] / 1000:.2f} cm3 |",
             f"| Mass ({material}) | ~{mass} g @15% infill, {solid_mass} g solid |",
             f"| Valid BREP | {'Yes' if shape.is_valid else 'NO'} |",
             f"| Connected solids | {bb['solids']} {'' if bb['solids'] == 1 else '(MUST be 1)'} |"]
    if export_files:
        step, stl, svg = out / f"{name}.step", out / f"{name}.stl", out / f"{name}_views.svg"
        export_step(shape, str(step))
        export_stl(shape, str(stl), tolerance=0.005)
        generate_multiview_svg(shape, svg, name)
        m = check_mesh(stl)
        lines += [f"| STL watertight | {'Yes' if m['watertight'] else 'NO'} ({m['boundary_edges']} open edges) |",
                  f"| STL shells | {m['shells']} |", "", "#### Exported Files",
                  f"- STEP: `{step}`", f"- STL: `{stl}`", f"- Views: `{svg}` / `{svg.with_suffix('.png')}`"]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m cad_tools.inspect <model.py> [out_dir]   (prefer: cad build <project>)")
        sys.exit(1)
    from cad_tools.pipeline import _load_module, _shapes

    mod = _load_module(Path(sys.argv[1]).resolve())
    parts, _ = _shapes(mod)
    out = sys.argv[2] if len(sys.argv) > 2 else "."
    for n, s in parts.items():
        print(inspect_solid(s, n, out))


if __name__ == "__main__":
    main()
