import os
import sys
import importlib.util
from pathlib import Path
from build123d import (
    Compound,
    Solid,
    Pos,
    ExportSVG,
    LineType,
    export_step,
    export_stl,
)

PLA_DENSITY_G_CM3 = 1.24
PETG_DENSITY_G_CM3 = 1.27

def generate_multiview_svg(shape, output_path):
    bbox = shape.bounding_box()
    span_x = max(bbox.size.X, 10.0)
    span_y = max(bbox.size.Y, 10.0)
    span_z = max(bbox.size.Z, 10.0)
    max_dim = max(span_x, span_y, span_z)

    spacing = max_dim * 1.5
    cam_dist = max_dim * 10.0

    projections = [
        ("top", (0.0, 0.0, cam_dist), (0.0, 1.0, 0.0), -spacing, spacing),
        ("iso", (cam_dist, -cam_dist, cam_dist), (0.0, 0.0, 1.0), spacing, spacing),
        ("front", (0.0, -cam_dist, 0.0), (0.0, 0.0, 1.0), -spacing, -spacing),
        ("right", (cam_dist, 0.0, 0.0), (0.0, 0.0, 1.0), spacing, -spacing),
    ]

    exporter = ExportSVG()
    exporter.add_layer("visible", line_color="#111111", line_weight=0.35)
    exporter.add_layer("hidden", line_color="#999999", line_weight=0.15, line_type=LineType.DASHED)

    for _, origin, up, off_x, off_y in projections:
        vis, hid = shape.project_to_viewport(origin, viewport_up=up)
        exporter.add_shape([e.moved(Pos(off_x, off_y, 0)) for e in vis], layer="visible")
        exporter.add_shape([e.moved(Pos(off_x, off_y, 0)) for e in hid], layer="hidden")

    exporter.write(output_path)
    return str(output_path)

def inspect_solid(shape, name="model", out_dir=".", export_files=True):
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    bbox = shape.bounding_box()
    size_x = round(bbox.size.X, 2)
    size_y = round(bbox.size.Y, 2)
    size_z = round(bbox.size.Z, 2)

    vol_mm3 = shape.volume
    vol_cm3 = round(vol_mm3 / 1000.0, 2)
    area_mm2 = shape.area
    area_cm2 = round(area_mm2 / 100.0, 2)

    weight_pla = round(vol_cm3 * PLA_DENSITY_G_CM3, 2)
    weight_petg = round(vol_cm3 * PETG_DENSITY_G_CM3, 2)

    is_valid = shape.is_valid
    is_closed = shape.is_closed if hasattr(shape, "is_closed") else True

    files_generated = {}
    if export_files:
        step_file = out_path / f"{name}.step"
        stl_file = out_path / f"{name}.stl"
        svg_file = out_path / f"{name}_views.svg"

        export_step(shape, str(step_file))
        export_stl(shape, str(stl_file))
        generate_multiview_svg(shape, str(svg_file))

        files_generated["step"] = str(step_file)
        files_generated["stl"] = str(stl_file)
        files_generated["svg"] = str(svg_file)

    report_lines = [
        f"### Model Inspection: {name}",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Bounding Box (X x Y x Z) | {size_x} x {size_y} x {size_z} mm |",
        f"| Solid Volume | {vol_cm3} cm3 ({round(vol_mm3, 1)} mm3) |",
        f"| Surface Area | {area_cm2} cm2 |",
        f"| Estimated Weight (PLA 100%) | {weight_pla} g |",
        f"| Estimated Weight (PETG 100%) | {weight_petg} g |",
        f"| Valid BREP Topology | {'Yes' if is_valid else 'NO (Topology Error)'} |",
        f"| Closed Manifold Shell | {'Yes' if is_closed else 'NO (Open Edges Detected)'} |",
        "",
    ]

    if files_generated:
        report_lines.append("#### Exported Files")
        report_lines.append(f"- STEP: `{files_generated['step']}`")
        report_lines.append(f"- STL: `{files_generated['stl']}`")
        report_lines.append(f"- Multi-view SVG: `{files_generated['svg']}`")
        report_lines.append("")

    return "\n".join(report_lines)

def run_script_inspection(script_path, out_dir="."):
    script = Path(script_path).resolve()
    if not script.exists():
        sys.exit(f"File not found: {script}")

    spec = importlib.util.spec_from_file_location("cad_target_module", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    targets = {}
    if hasattr(mod, "EXPORT_SOLIDS") and isinstance(mod.EXPORT_SOLIDS, dict):
        targets = mod.EXPORT_SOLIDS
    elif hasattr(mod, "RESULT"):
        targets["result"] = mod.RESULT
    else:
        for attr_name in dir(mod):
            if attr_name.startswith("_"):
                continue
            val = getattr(mod, attr_name)
            if isinstance(val, (Solid, Compound)):
                targets[attr_name.lower()] = val

    if not targets:
        sys.exit("No Solid or Compound instances found to inspect.")

    full_report = []
    for name, solid in targets.items():
        rep = inspect_solid(solid, name=name, out_dir=out_dir, export_files=True)
        full_report.append(rep)

    summary = "\n---\n\n".join(full_report)
    print(summary)
    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m cad_tools.inspect <path_to_cad_script.py> [out_dir]")
        sys.exit(1)

    target_script = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    run_script_inspection(target_script, out_dir)

if __name__ == "__main__":
    main()
