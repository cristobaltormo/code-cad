# Mechanical & Structural Component Prompt

Use this prompt to design load-bearing brackets, motor mounts, robotic arms, hinges, or tooling fixtures.

---

```markdown
Design a structural, load-bearing mechanical component using Python and `build123d`.

### Component Specifications:
- Function: [e.g., NEMA 17 Stepper Motor Mount / Heavy-duty 90-degree Shelf Bracket / Camera Gimbal Arm]
- Expected Load & Direction: [e.g., 5 kg cantilever load in negative Z axis]
- Mating Geometry: [e.g., 2x M5 DIN 912 screws into 2020 aluminum extrusion, 31 mm square bolt pattern]
- Space Envelope / Maximum Dimensions: [e.g., 60 mm x 40 mm x 50 mm max]

### Structural Engineering Constraints:
1. Load Path & Layer Orientation:
   - State the primary stress direction. Orient the print so tensile stresses are carried along continuous extruded filament paths in the XY plane, never across Z layer boundaries.
2. Geometry Reinforcement:
   - Add triangular gussets or stiffening ribs along cantilevered corners.
   - Blend interior 90-degree corners with fillets (radius >= 3.0 mm) to reduce notch stress concentrations.
   - Wall and flange thicknesses must be at least 4.0 mm to 6.0 mm.
3. Fastener Interfaces:
   - Recessed counterbore pockets for socket head cap screws to keep heads flush.
   - Edge distance: center of bolt holes must be at least 2.5 times the bolt diameter from any edge.

Execute the script, inspect the model topology and metrics, and provide the `.step`, `.stl`, and `_views.svg` files.
```
