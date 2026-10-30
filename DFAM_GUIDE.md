# Design for Additive Manufacturing (DFAM) Engineering Guide

A practical reference handbook for designing functional, dimensionally accurate 3D printed parts for FDM (Fused Deposition Modeling) and SLA (Stereolithography).

---

## 1. Wall Thickness & Nozzle Geometry

FDM printers deposit continuous beads of molten polymer with a specific width and height.

### Nominal Nozzle Multiples (0.4 mm Standard Nozzle)
Slicers typically calculate an extrusion line width of 0.42 mm to 0.45 mm for a 0.40 mm nozzle. Walls must be designed to contain an integer number of solid perimeters without leaving internal micro-gaps:

| Target Wall Strength | Perimeter Count | Recommended CAD Thickness |
|---|---|---|
| Light / cosmetic covers | 2 perimeters | 0.84 mm - 0.90 mm |
| Standard enclosures / boxes | 3-4 perimeters | 1.26 mm - 1.68 mm |
| Heavy-duty / structural parts | 5-6 perimeters | 2.10 mm - 2.50 mm |
| Threaded insert bosses | 6+ perimeters | 2.50 mm - 3.50 mm solid |

Rule: Avoid wall thicknesses between integer multiples (e.g., a 1.0 mm wall with 0.42 mm perimeters forces the slicer into erratic gap-fill motion). Modern slicers (Arachne wall generator in PrusaSlicer/Orca/Bambu Studio) handle odd widths better, but integer-perimeter walls remain the strongest. `cad_tools.printers.wall_thickness(n)` gives the slicer-exact width for n perimeters.

---

## 2. Fit Tolerances & Clearances

Tolerances depend on printer calibration, filament material shrinkage (PLA ~0.3%, PETG ~0.6%, ABS/ASA ~1.5%), and layer height.

| Fit Class | Radial Offset (Per Side) | Diametrical Clearance | Typical Application |
|---|---|---|---|
| Interference / Press Fit | 0.05 mm | 0.10 mm | Bearings into pockets, metal pins, dowels |
| Snug / Sliding Fit | 0.10 mm | 0.20 mm | Enclosure lid lips, battery trays, sliding covers |
| Free / Moving Fit | 0.15 mm - 0.20 mm | 0.30 mm - 0.40 mm | Hinges, latches, guide rails, linkages |
| Cable / Port Clearance | 0.50 mm | 1.00 mm | USB ports, power plugs, Ethernet cutouts |

---

## 3. Hole Sizing & Horizontal Expansion

In FDM printing, vertical cylindrical holes consistently print smaller than CAD dimensions due to:
1. Centripetal tension: The extruded polymer noodle is stretched along an inner curve, pulling toward the circle's center.
2. Polygon approximation: Slicers triangulate circles into chorded line segments.
3. Thermal contraction during cooling.

### Hole Sizing Matrix

CAD diameters for vertical holes = ISO 273 medium clearance + 0.2 mm printed
compensation (`cad_tools.fasteners.clearance_dia`). Tune after a test print.

| Fastener / Pin | Nominal | ISO 273 medium | CAD diameter (vertical hole) |
|---|---|---|---|
| M2 | 2.0 | 2.4 | 2.6 |
| M2.5 | 2.5 | 2.9 | 3.1 |
| M3 | 3.0 | 3.4 | 3.6 |
| M4 | 4.0 | 4.5 | 4.7 |
| M5 | 5.0 | 5.5 | 5.7 |
| M6 | 6.0 | 6.6 | 6.8 |
| 608 bearing OD (press) | 22.0 | - | 22.10-22.15 |

---

## 4. Horizontal Holes & Bridges (Teardrop Rule)

When a circular hole is oriented horizontally (parallel to the print bed), the top arc creates an unsupported overhang bridge that can droop.

- Holes <= 4.0 mm: Can print as standard cylinders with minor bridge bridging.
- Holes > 4.0 mm: Replace the circular top half with a 45-degree pointed apex (teardrop profile). The angled ceiling prints self-supporting without sagging or requiring internal support structures.

---

## 5. Chamfers vs. Fillets

### Bottom Edges (Build Plate Contact)
- Never use a fillet on an edge resting on the build plate. The tangent curve begins at 0 degrees against the bed, creating extreme overhang angles that curl and degrade.
- Always use a 45-degree chamfer (0.6 mm to 1.0 mm). A 45-degree chamfer eliminates the "elephant's foot" bulge caused by first-layer bed squish.

### Vertical & Interior Edges
- Use fillets (radius >= 2.0 mm) on all interior 90-degree corners. Fillets distribute mechanical stress evenly, preventing the notch effect and crack propagation under load.

---

## 6. Fasteners: Heat-Set Inserts vs. Screws

### Brass Heat-Set Inserts

Values from the ruthex and CNC Kitchen size tables (verified 2026-10; `cad lookup ruthex`).
Model the hole at the vendor diameter (no extra compensation); pocket depth
>= insert length + 1 mm; boss wall >= vendor minimum.

| Insert (ruthex) | Length | Insert OD | Hole Ø | Min pocket depth | Min wall | Min boss OD |
|---|---|---|---|---|---|---|
| M2 x 4 | 4.0 | 3.6 | 3.2 | 5.0 | 1.3 | 5.8 |
| M2.5 x 5.7 | 5.7 | 4.6 | 4.0 | 6.7 | 1.6 | 7.2 |
| M3 x 5.7 | 5.7 | 4.6 | 4.0 | 6.7 | 1.6 | 7.2 |
| M3 x 4 (short) | 4.0 | 4.6 | 4.0 | 5.0 | 1.6 | 7.2 |
| M4 x 8.1 | 8.1 | 6.3 | 5.6 | 9.1 | 2.1 | 9.8 |
| M5 x 9.5 | 9.5 | 7.0 | 6.4 | 10.5 | 2.6 | 11.6 |
| M6 x 12.7 | 12.7 | 8.7 | 8.0 | 13.7 | 3.3 | 14.6 |

CNC Kitchen differs: M2 is 3.0 long, M2.5 is 4.0 long, M3 short is 3.0 long;
holes M4 5.7 / M5 6.5 / M6 8.1. Voron-style M3 x 5 x 4: hole 4.4.

`heat_set_boss()` refuses bosses too short for the pocket; let the pocket run
into the floor instead (`heat_set_hole()` on the combined part).

---

## 7. Anisotropic Mechanical Strength & Print Orientation

FDM parts exhibit anisotropic tensile strength:
- Strength along the filament path (XY axes): 100% (bulk polymer tensile strength).
- Strength across layer bonds (Z axis): 40% to 65% depending on temperature and layer adhesion.

Rule: Never orient structural parts such that primary tensile or bending stresses pull layers apart along the Z axis. Rotate the model in CAD so the principal stress vectors align with continuous extruded strands on the build plate.
