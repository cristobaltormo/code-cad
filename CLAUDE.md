# Code-CAD: Parametric 3D CAD Engineering

This workspace is configured for programmatic 3D CAD modeling and Design for Additive Manufacturing (DFAM) using Python and the `build123d` library.

## Core Rules & Engineering Standards

### 1. Verification First (No Blind Geometry)
- Do not guess physical dimensions, mounting hole patterns, or port locations. Ask or extract from datasheets and caliper measurements.
- Write a clean parametric script using `build123d`.
- Execute the script using Python in the terminal to verify zero topology errors.
- Run `cad_tools.inspect.inspect_solid` to calculate bounding box dimensions, volume, mass, and generate a 4-view orthographic and isometric SVG drawing (`_views.svg`).
- Check the generated SVG using file inspection tools to visually confirm port locations, alignment, and clearances.

### 2. Design for Additive Manufacturing (DFAM)
- Wall Thickness: Sized as exact multiples of nozzle extrusion line width (e.g., 0.4 mm nozzle -> 0.8 mm, 1.2 mm, 1.6 mm, 2.0 mm, 2.4 mm).
- Elephant's Foot Mitigation: Apply a 0.6 mm to 1.0 mm 45-degree chamfer on bottom edges contacting the print bed.
- Overhangs & Bridges: Keep unsupported overhangs under 45 degrees. Use 45-degree teardrop profiles for horizontal holes larger than 4 mm to prevent bridge droop.
- Stress Concentration: Apply fillets (radius >= 2.0 mm) on interior 90-degree corners to avoid notch fractures.
- Layer Anisotropy: Orient models so structural tensile loads run along continuous filament extrusions in the XY plane, never across Z layer boundaries.
- Tolerances:
  - Press / interference fit: +0.05 mm to +0.10 mm.
  - Close sliding fit: +0.15 mm to +0.20 mm.
  - Free / loose fit: +0.30 mm to +0.40 mm.
  - Internal hole compensation: +0.20 mm over nominal diameter to counteract thermal shrinkage and extrusion curvature.

### 3. Deliverables
Every model task must produce:
1. Parametric Python script (`<model>.py`).
2. STEP file (`<model>.step`) for lossless analytical curves in modern slicers (OrcaSlicer, Bambu Studio, PrusaSlicer).
3. STL file (`<model>.stl`) for standard mesh workflows.
4. Multi-view technical drawing (`<model>_views.svg`).
