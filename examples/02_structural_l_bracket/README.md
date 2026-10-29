# Example 02: Structural Reinforced L-Bracket

A heavy-duty 90-degree mounting bracket engineered for structural stiffness and FDM printing durability.

## Engineering Principles
- Triangular gusset rib along the interior corner to resist bending deflection under load.
- Filleted interior corner (radius 3.0 mm) to eliminate stress concentration and notch fractures.
- Recessed counterbore pocket for DIN 912 M5 socket-head cap screws.
- Bottom chamfer to eliminate elephant's foot.
- Optimized print orientation: Print flat on one of the outer rectangular legs to ensure tensile loads align with continuous extrusion paths along X and Y axes, preventing layer delamination under shear.

## Execution
```bash
python3 bracket.py
```

Generated outputs will be saved to the `exports/` directory:
- `l_bracket.step` and `l_bracket.stl`
- `l_bracket_views.svg`
