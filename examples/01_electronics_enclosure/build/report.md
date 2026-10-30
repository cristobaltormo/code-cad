## Build: 01_electronics_enclosure  ->  PASS

### enclosure_base

- bbox: 56.0 x 26.0 x 16.0 mm (min [-28.0, -13.0, -0.0], max [28.0, 13.0, 16.0])
- volume 7.24 cm3, mass ~9.0 g @15% infill (9.0 g solid, PLA)
- holes/bosses found: 16

  - [PASS] brep_valid: BREP topology valid (BRepCheck)
  - [PASS] single_solid: 1 solid(s); a printable part should be exactly 1 connected solid
  - [PASS] positive_volume: volume 7244.203 mm3
  - [PASS] on_bed: min Z = -0.0 (export in print orientation with the bed face at Z=0)
  - [PASS] stl_watertight: STL boundary edges 0, non-manifold 0
  - [PASS] stl_oriented: normals outward=True, misoriented edges 0
  - [PASS] stl_single_shell: STL shells: 1
  - [PASS] stl_matches_step: STL volume 7243.9 vs STEP 7244.2 (0.00%)
  - [PASS] fits_printer: [56.0, 26.0, 16.0] vs Generic 220 mm bed [220, 220, 250]
  - [PASS] no_interference_pico: part vs pico: interference 0.0 mm3, min gap 0.0 mm

  files: step=build/enclosure_base.step, stl=build/enclosure_base.stl, 3mf=build/enclosure_base.3mf, views_png=build/enclosure_base_views.png, views_svg=build/enclosure_base_views.svg, sections_png=build/enclosure_base_sections.png

### enclosure_lid

- bbox: 56.0 x 26.0 x 5.0 mm (min [-28.0, -13.0, 0.0], max [28.0, 13.0, 5.0])
- volume 3.08 cm3, mass ~3.8 g @15% infill (3.8 g solid, PLA)
- holes/bosses found: 20

  - [PASS] brep_valid: BREP topology valid (BRepCheck)
  - [PASS] single_solid: 1 solid(s); a printable part should be exactly 1 connected solid
  - [PASS] positive_volume: volume 3079.532 mm3
  - [PASS] on_bed: min Z = 0.0 (export in print orientation with the bed face at Z=0)
  - [PASS] stl_watertight: STL boundary edges 0, non-manifold 0
  - [PASS] stl_oriented: normals outward=True, misoriented edges 0
  - [PASS] stl_single_shell: STL shells: 1
  - [PASS] stl_matches_step: STL volume 3079.5 vs STEP 3079.5 (0.00%)
  - [PASS] fits_printer: [56.0, 26.0, 5.0] vs Generic 220 mm bed [220, 220, 250]
  - [PASS] no_interference_pico: part vs pico: interference 0.0 mm3, min gap 1.0 mm

  files: step=build/enclosure_lid.step, stl=build/enclosure_lid.stl, 3mf=build/enclosure_lid.3mf, views_png=build/enclosure_lid_views.png, views_svg=build/enclosure_lid_views.svg, sections_png=build/enclosure_lid_sections.png
