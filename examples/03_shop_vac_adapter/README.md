# Example 03: Parametric Dust Extraction / Shop Vac Adapter

A lofted circular duct adapter designed for vacuum hoses, dust collection ports, and power tools.

## Engineering Principles
- Smooth lofted internal transition between differing diameters (`36.0 mm` to `31.0 mm`) to minimize airflow resistance, turbulence, and static pressure drop.
- Uniform wall thickness (`2.4 mm`) throughout the transition.
- 0.8 mm entry chamfers on both sleeve openings to facilitate smooth insertion over hoses and tool dust ports.
- 100% printable without support structures when oriented vertically on the build plate.

## Execution
```bash
python3 adapter.py
```

Generated outputs will be saved to the `exports/` directory:
- `shop_vac_adapter.step` and `shop_vac_adapter.stl`
- `shop_vac_adapter_views.svg`
