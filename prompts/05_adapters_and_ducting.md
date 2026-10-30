# Ducting, Adapters & Fluid Handling Prompt

Use this prompt to design shop vac hose reducers, dust collection fittings, fan shrouds, funnels, or pipe adapters.

---

```markdown
Design a parametric adapter or ducting component using Python and `build123d`.

### Ducting Interface Requirements:
- Input Port Geometry: [e.g., Round outer diameter 35.0 mm, insertion depth 25.0 mm]
- Output Port Geometry: [e.g., Round outer diameter 31.8 mm, insertion depth 25.0 mm]
- Coupling Type: [e.g., Friction taper fit (1.5-degree draft angle) / Direct hose barb / Clamp sleeve]
- Transition Length: [e.g., 30.0 mm smooth conical loft between ports]

### Manufacturing & Fluid Flow Constraints:
1. Aerodynamics & Flow Efficiency:
   - Use smooth lofted transitions between differing cross-sections to minimize air turbulence, backpressure, and material clogs.
   - Maintain uniform internal wall thickness (2.4 mm to 3.0 mm) throughout the entire length.
2. Printing Constraints:
   - Ensure the part prints oriented vertically along its longitudinal axis without internal or external supports.
   - Wall thickness must equal 4 to 6 continuous perimeters with a 0.4 mm nozzle for airtight/watertight integrity.
   - 0.8 mm entry chamfers on both sleeve ends to guide hose insertion.

Follow the /cad pipeline: research the real dimensions, write spec.json, build, run the independent verifier agents, and deliver only the files from `cad release`.
```
