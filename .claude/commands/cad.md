---
description: Design a parametric 3D CAD model ready for 3D printing using build123d
---

Execute a complete Code-CAD workflow to design a 3D-printable model:

1. Requirements Clarification:
   - Identify mating components, dimensions, tolerances, and structural requirements from $ARGUMENTS.
   - If critical dimensions or datasheets are missing, request them before generating code.

2. Parametric Script Generation:
   - Create a clean Python script using `build123d`.
   - Apply DFAM rules: nozzle wall multiples (e.g., 2.4 mm), bed chamfers (0.8 mm), stress-relief fillets, and proper tolerances.

3. Execution & Verification:
   - Execute the script using Python.
   - Run `cad_tools.inspect.inspect_solid` to verify topology, calculate volume/weight, export `.step` and `.stl`, and generate a 4-view SVG sheet (`_views.svg`).
   - Read and visually verify the exported SVG.

4. Report:
   - Provide bounding box dimensions (X x Y x Z mm), estimated weight, print orientation recommendations, and file export paths.
