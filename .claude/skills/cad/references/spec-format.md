# spec.json format

The spec is written **before** the model and is the contract the independent
verifiers check against. Tolerances live here so nobody can loosen them after
the fact; `cad attest` computes PASS/FAIL from these numbers.

```json
{
  "name": "pi5_wall_mount",
  "description": "Wall mount plate for a Raspberry Pi 5, screwed to a wall with 2 x 4 mm wood screws.",
  "model": "pi5_wall_mount.py",
  "printer": "bambu_p1s",              // `cad printers`
  "material": "PETG",
  "nozzle": 0.4,

  "objects": {                          // researched real objects (from research/*.json)
    "rpi5": {
      "name": "Raspberry Pi 5",
      "dimensions": {"length": 85.0, "width": 56.0, "hole_d": 2.7,
                     "hole_pattern": [58.0, 49.0]},
      "sources": ["https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf"],
      "confidence": "high",
      "research_file": "research/rpi5.json"
    }
  },

  "requirements": [
    "Pi sits on 4 standoffs with M2.5 heat-set inserts, 5 mm clearance under the PCB",
    "Two countersunk wood-screw holes outside the board footprint"
  ],

  "features": [                         // each must be checkable on the renders
    "4 standoffs on the 58 x 49 mm pattern",
    "2 countersunk holes outside the board outline",
    "0.8 mm chamfer on the bed edges"
  ],

  "critical_dimensions": [              // verifier must measure EVERY one
    {"id": "standoff_pitch_x", "part": "plate",
     "description": "Centre distance between standoffs along X",
     "nominal": 58.0, "tol_minus": 0.1, "tol_plus": 0.1,
     "basis": "rpi5 hole pattern 58.0 (official drawing)"},
    {"id": "insert_pocket_depth", "part": "plate",
     "description": "Heat-set pocket depth from standoff top",
     "nominal": 6.7, "tol_minus": 0.0, "tol_plus": 1.5,
     "basis": "ruthex M2.5 L 5.7 + 1.0 (vendor rule)"}
  ],

  "checks": [                           // machine checks run by `cad verify`
    {"type": "solids", "part": "plate", "count": 1},
    {"type": "max_size", "part": "plate", "value": [110, 80, 20]},
    {"type": "hole", "part": "plate", "diameter": 4.0, "tol": 0.05, "count": 4, "axis": "z", "min_length": 6.7},
    {"type": "bbox_size", "part": "plate", "axis": "z", "nominal": 12.0, "tol": 0.05},
    {"type": "ray", "part": "plate", "origin": [0, -100, 2], "direction": [0, 1, 0],
     "measure": "material", "index": 0, "nominal": 70.0, "tol_minus": 0.2, "tol_plus": 0.2},
    {"type": "clearance", "part": "plate", "mate": "rpi5", "min": 0.3, "max": 6.0},
    {"type": "min_wall", "part": "plate", "value": 1.2}
  ]
}
```

(JSON has no comments; the `//` above are explanations only.)

## Check types

| type | fields | passes when |
|---|---|---|
| `solids` | count | exported STEP has exactly `count` solids |
| `max_size` | value [x,y,z] | bbox size <= value on every axis |
| `bbox_size` | axis, nominal, tol / tol_minus, tol_plus | bbox along axis within tolerance |
| `hole` | diameter, tol, count?, axis?, kind? (hole/boss), min_length? | number of full cylinders matching == count (or >= 1) |
| `ray` | origin, direction, measure (gaps/material), index, nominal, tol_minus, tol_plus | segment length within tolerance |
| `clearance` | mate, min, max | no interference and min gap in [min, max] |
| `min_wall` | value | sampled minimum wall thickness >= value |

Tolerance tips: fit-critical gaps get asymmetric tolerances (more room is
usually safer than less: `tol_minus 0.05, tol_plus 0.2`); hole pitch +-0.1;
overall envelopes +-0.2; heat-set depth `tol_minus 0`.
