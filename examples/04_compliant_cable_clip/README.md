# Example 04: Compliant Snap-Fit Cable Clip

A monolithic print-in-place compliant snap clip for wire management and cable routing.

## Engineering Principles
- Flexible cantilever arms with filleted entry tips to permit insertion while resisting unintentional pullout.
- Integrated flat mounting tab with a 4.2 mm hole for M4 screw fastening or zip-ties.
- Wall thickness of 2.4 mm (6 perimeters with a 0.4 mm nozzle) providing optimal spring deflection without plastic fatigue when printed in PETG or PLA.
- Zero support material required when printed flat on its side face.

## Execution
```bash
python3 clip.py
```

Generated outputs will be saved to the `exports/` directory:
- `cable_clip.step` and `cable_clip.stl`
- `cable_clip_views.svg`
