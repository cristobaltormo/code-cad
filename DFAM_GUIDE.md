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

Rule: Avoid wall thicknesses between integer multiples (e.g., a 1.0 mm wall with 0.42 mm perimeters forces the slicer into erratic gap-fill motion).

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

| Fastener / Pin | Nominal Diameter | CAD Diameter (Vertical Hole) | Notes |
|---|---|---|---|
| M2 Screw (Clearance) | 2.0 mm | 2.3 mm - 2.4 mm | Smooth pass-through |
| M2.5 Screw (Clearance) | 2.5 mm | 2.8 mm - 2.9 mm | Smooth pass-through |
| M3 Screw (Clearance) | 3.0 mm | 3.3 mm - 3.4 mm | Smooth pass-through |
| M4 Screw (Clearance) | 4.0 mm | 4.4 mm - 4.5 mm | Smooth pass-through |
| M5 Screw (Clearance) | 5.0 mm | 5.4 mm - 5.5 mm | Smooth pass-through |
| 608 Ball Bearing | 22.0 mm | 22.15 mm - 22.20 mm | Press fit into pocket |

Rule of Thumb: For vertical screw clearance holes under 10 mm, add +0.3 mm to +0.4 mm to the nominal diameter in CAD.

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

### Brass Heat-Set Inserts (Ruthex / Standard)
Brass threaded inserts pressed in with a soldering iron offer high pull-out and torque strength in thermoplastics:

| Thread Size | Hole Diameter (CAD) | Hole Depth (CAD) | Minimum Boss Outer Diameter |
|---|---|---|---|
| M2 | 3.2 mm | 4.0 mm | 5.4 mm |
| M2.5 | 4.0 mm | 5.7 mm | 6.5 mm |
| M3 | 4.0 mm | 5.7 mm | 7.0 mm |
| M4 | 5.6 mm | 8.0 mm | 9.0 mm |
| M5 | 6.8 mm | 9.5 mm | 11.0 mm |

Boss Design Rules:
- Add a 0.5 mm lead-in counterbore at the top of the hole with insert outer diameter to guide insertion square.
- Ensure the hole depth is at least 1.0 mm deeper than the insert length to trap melted plastic overflow.

---

## 7. Anisotropic Mechanical Strength & Print Orientation

FDM parts exhibit anisotropic tensile strength:
- Strength along the filament path (XY axes): 100% (bulk polymer tensile strength).
- Strength across layer bonds (Z axis): 40% to 65% depending on temperature and layer adhesion.

Rule: Never orient structural parts such that primary tensile or bending stresses pull layers apart along the Z axis. Rotate the model in CAD so the principal stress vectors align with continuous extruded strands on the build plate.
