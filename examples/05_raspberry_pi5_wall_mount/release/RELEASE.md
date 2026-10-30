# Release: pi5_wall_mount

Released 2026-10-30T12:07:50+00:00. Every file below passed:

- automatic geometry checks (valid BREP, single solid, watertight STL, STL=STEP volume, bed fit, spec checks)
- independent dimension verification by `cad-dimension-verifier`
- independent printability review by `cad-print-reviewer` (PASS)

## Critical dimensions

| id | nominal | allowed | measured | ok |
|---|---|---|---|---|
| standoff_pitch_x | 58.0 | [57.9, 58.1] | 58.0 | yes |
| standoff_pitch_y | 49.0 | [48.9, 49.1] | 49.0 | yes |
| insert_hole_d | 4.0 | [3.95, 4.05] | 4.0 | yes |
| insert_pocket_depth | 7.1 | [6.7, 8.2] | 7.1 | yes |
| standoff_wall | 2.0 | [1.6, 2.4] | 2.0 | yes |
| standoff_height | 5.0 | [4.9, 5.1] | 5.0 | yes |
| plate_thickness | 4.0 | [3.95, 4.05] | 4.0 | yes |
| screw_edge_distance | 10.5 | [8.8, 12.5] | 10.5 | yes |
| screw_hole_d | 4.4 | [4.35, 4.45] | 4.4 | yes |
| mate_outline_length | 85.0 | [84.9, 85.1] | 85.0 | yes |
| mate_outline_width | 56.0 | [55.9, 56.1] | 56.0 | yes |
| mate_hole_offset_x | 3.5 | [3.45, 3.55] | 3.5 | yes |
| insert_hole_min_depth | 6.7 | [6.7, 7.7] | 6.8 | yes |
| countersink_top_d | 8.96 | [8.96, 9.96] | 9.36 | yes |

## Print orientation

Print as exported: 4 mm plate flat on the bed (Z=0), standoffs and countersink cones open upward. In service the plate hangs vertically on the wall; the only loads are wood-screw clamping (compression through Z, fine) and the ~46 g Pi cantilevered 5 mm off the standoffs (negligible bending across standoff layers). No load puts layers in Z tension except insert pull-out, which the melted insert bond spans across layers.

## Suggested print settings

- material: PETG
- layer_height: 0.2 mm
- walls: 5 (makes the 2.0 mm standoff walls fully solid perimeters around the inserts)
- top_bottom_layers: 5 top / 4 bottom
- infill: 25% gyroid
- supports: none
- brim: no
- bed: textured PEI (or glue stick on smooth PEI), 70-80 C
- notes: Install ruthex M2.5x5.7 inserts with an iron at ~230-245 C for PETG, pressing straight down; the 0.3 mm lead-in centres them. Use M2.5 screws <= 6 mm thread engagement past a 1.6 mm PCB. Do not over-tighten the 4 mm countersunk wood screws.

## Parts

- **plate**: 119.0 x 64.0 x 9.0 mm, ~24.4 g (PETG)

## SHA-256

- `build/mates/rpi5.step` bd85bd1e39b00930
- `build/plate.3mf` c87a9adeb87968f4
- `build/plate.step` c998a149e424e081
- `build/plate.stl` 19f372a7918f05a4
