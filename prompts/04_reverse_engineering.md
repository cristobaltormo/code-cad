# Reverse Engineering & Replacement Parts Prompt

Use this prompt when replicating a broken plastic component from physical measurements, photos, or caliper readings.

---

```markdown
Reverse-engineer and design a 3D-printable replacement for a physical component using Python and `build123d`.

### Physical Measurements (Caliper Readings):
- Critical Outer Dimensions: [e.g., Outer diameter, total height, width, depth]
- Critical Interfaces / Mating Features: [e.g., Shaft diameter, D-shaft flat dimension, pin hole spacing]
- Fastener Details: [e.g., M3 countersunk screw hole, snap hook]
- Tolerances Needed: [e.g., Press-fit onto 6.0 mm motor shaft, sliding fit in 20.0 mm track]

### Reverse Engineering Methodology:
1. Deconstruct the part into primitive geometric features (base extrusion, central bore, keyway, mounting flange, chamfers).
2. Apply FDM additive manufacturing adjustments:
   - Shaft hole expansion: Holes print slightly undersized due to thermal plastic shrinkage and nozzle path curvature. Compensate by adding +0.2 mm to internal bore diameters.
   - Chamfer bottom edges by 0.6 mm to prevent elephant's foot.
   - Replace brittle thin walls with reinforced 2.4 mm+ sections.
3. Validate that the replacement part can be printed flat without unnecessary support material.

Follow the /cad pipeline: research the real dimensions, write spec.json, build, run the independent verifier agents, and deliver only the files from `cad release`.
```
