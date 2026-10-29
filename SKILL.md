---
name: code-cad
description: Parametric 3D CAD engineering and Design for Additive Manufacturing (DFAM) using build123d and Python. Generates exact STEP, STL, and multi-view technical drawings for enclosures, brackets, adapters, and mechanisms.
---

# Code-CAD Skill

Use this skill to design functional, production-ready 3D models for FDM and resin 3D printers using programmatic CAD (Code-CAD).

## Core Principles

1. Programmatic CAD over Mesh Generators:
   - Use Python and `build123d` (OpenCASCADE BREP kernel).
   - Generates exact NURBS geometry exported to `.step` (lossless curves in OrcaSlicer, Bambu Studio, PrusaSlicer) and `.stl`.

2. Automated Verification Loop:
   - Every script must be executed in the terminal.
   - Run `cad_tools.inspect.inspect_solid` to verify:
     - BREP validity (`is_valid == True`).
     - Closed watertight manifold shell (`is_closed == True`).
     - 4-view orthographic and isometric technical drawing in SVG format with hidden lines (`_views.svg`).
   - Read the SVG file using text or visual inspection tools to confirm feature placement.

3. Standard Tolerances & DFAM Rules:
   - Nominal walls: 1.6 mm to 2.4 mm (multiples of 0.4 mm extrusion lines).
   - Elephant's foot mitigation: 0.6 mm to 1.0 mm 45-degree chamfer on bottom edges.
   - Bore hole expansion: add +0.2 mm to hole diameters for vertical printed cylinders.
   - Teardrop horizontal holes: use 45-degree pointed apex for horizontal bores larger than 4 mm.
   - Press fit: +0.05 mm to +0.10 mm.
   - Sliding fit: +0.15 mm to +0.20 mm.
   - Loose fit: +0.30 mm to +0.40 mm.
   - Fasteners: use `cad_tools.fasteners.heat_set_boss` for Ruthex/standard brass inserts (M2, M2.5, M3, M4, M5).

## Directory Structure
- `cad_tools/`: Fastener, joint, feature, and inspection helper library.
- `prompts/`: Ready-to-use prompt templates for enclosures, brackets, reverse engineering, and adapters.
- `examples/`: Compilable reference implementations with exported `.step`, `.stl`, and `.svg` files.
