# Example 01: Parametric Electronics Enclosure

A two-part parametric snap-lid enclosure designed for microcontroller boards (such as ESP32 or Raspberry Pi Pico).

## Features
- Parametric clearances for PCB expansion (`CLEARANCE = 0.5 mm`).
- Walls sized as multiples of standard 0.4 mm extrusion nozzles (`WALL = 2.4 mm`).
- Four integrated corner standoffs with pilot holes for mounting screws.
- Cutout for USB-C cable connector.
- Ventilation slot array on lid for passive heat dissipation.
- Bottom chamfer (0.8 mm at 45 degrees) to eliminate first-layer elephant's foot.
- Interlocking friction lip on lid.

## Execution
Run the script directly to validate geometry and export files:
```bash
python3 case.py
```

Generated outputs will be saved to the `exports/` directory:
- `enclosure_base.step` and `enclosure_base.stl`
- `enclosure_lid.step` and `enclosure_lid.stl`
- `enclosure_base_views.svg` and `enclosure_lid_views.svg`
