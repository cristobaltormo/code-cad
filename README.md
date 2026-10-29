# Code-CAD

English | [Español](README.es.md)

Parametric Code-CAD engineering framework and agent skills for functional 3D printing with Claude Code, Antigravity, and `build123d`.

Traditional text-to-3D AI generators produce irregular, unconstrained polygon meshes that cannot be manufactured to tight mechanical tolerances. Code-CAD replaces mesh approximation with programmatic boundary representation (B-Rep) modeling. By writing mathematical Python scripts using `build123d` (powered by the OpenCASCADE CAD kernel), an AI agent designs dimensionally exact parts with true analytical curves, standardized fastener interfaces, and verified manufacturing tolerances.

```
+-----------------------------------------------------------------------+
|                           USER PROMPT / TASK                          |
|         (Physical specs, datasheets, caliper measurements)            |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         AI AGENT (Claude Code)                        |
|   1. Enforces DFAM constraints (wall multiples, chamfers, tolerances) |
|   2. Writes parametric Python script using build123d                  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         EXECUTION & TOPOLOGY                          |
|   1. Terminal execution: verifies valid BREP manifold solid           |
|   2. Computes bounding box, volume, and material weight (PLA/PETG)    |
|   3. Exports STEP (lossless curves) and STL (polygon mesh)           |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                   HEADLESS 4-VIEW SVG VERIFICATION                    |
|   1. Hidden-line removal (HLR) orthographic + isometric projection    |
|   2. AI agent inspects SVG visually to verify ports and clearances    |
|   3. Self-corrects errors before output reaches the slicer            |
+-----------------------------------------------------------------------+
```

---

## Why Code-CAD: Moving from 7/10 to 10/10

| Aspect | Basic AI 3D Approach (7/10) | Code-CAD Engineering Framework (10/10) |
|---|---|---|
| **Scope** | Limited to basic PCB / chip enclosures | Universal: Enclosures, structural brackets, ducting, compliant clips, replacement parts, Gridfinity |
| **Geometry Kernel** | Approximate polygonal meshes (OBJ/STL) | Precise OpenCASCADE B-Rep solids exported to STEP (NURBS) and STL |
| **Visual Feedback** | Blind generation (agent guesses coordinates) | Headless 4-view SVG orthographic projection with hidden lines for agent inspection |
| **Manufacturing Rules** | Generic hardcoded wall thickness | Complete DFAM engine: nozzle multiples, elephant's foot chamfers, teardrop horizontal bores |
| **Fastener Standards** | Simple clearance holes | Parameterized bosses for Ruthex brass heat-set inserts (M2-M5), counterbores, captive hex nuts |
| **Verification** | User tests file in slicer manually | Automated CLI validation: watertightness, volume, mass, and dimension bounding box report |

---

## Repository Structure

```
code-cad/
├── .claude/
│   └── commands/
│       └── cad.md                  # Slash command /cad for Claude Code
├── CLAUDE.md                       # Drop-in rules for Claude Code in any CAD workspace
├── SKILL.md                        # Portable skill definition for Antigravity & AI agents
├── DFAM_GUIDE.md                   # Engineering guide: tolerances, nozzle math, shrinkages
├── INSTALL.md                      # Environment setup and dependency installation
├── pyproject.toml                  # Python package configuration
├── requirements.txt                # Dependency specifications (build123d, numpy, scipy)
├── cad_tools/                      # Reusable parametric engineering library
│   ├── __init__.py
│   ├── inspect.py                  # CLI validator, mass calculator, and 4-view SVG projector
│   ├── fasteners.py                # Heat-set insert bosses (M2-M5), counterbores, hex pockets
│   ├── joints.py                   # Cantilever snap-fit tabs, catches, and lip-groove joints
│   ├── features.py                 # Teardrop horizontal holes, ventilation slot arrays
│   └── gridfinity.py               # Standard 42 mm Gridfinity baseplate and bin profiles
├── prompts/                        # Turnkey prompt library for agents
│   ├── 01_kickoff_master.md        # Master kickoff prompt for any 3D model
│   ├── 02_electronics_enclosure.md # Microcontroller and PCB case prompt
│   ├── 03_structural_part.md       # Heavy-load structural bracket prompt
│   ├── 04_reverse_engineering.md   # Physical replacement part from caliper measurements
│   └── 05_adapters_and_ducting.md  # Vacuum adapters, reducers, and pipe fittings
└── examples/                       # Compilable reference implementations
    ├── 01_electronics_enclosure/   # Parametric case with standoffs, USB-C cut, and vent slots
    ├── 02_structural_l_bracket/    # Heavy-duty 90-degree bracket with gusset and counterbores
    ├── 03_shop_vac_adapter/        # Lofted vacuum hose reducer with press-fit taper
    └── 04_compliant_cable_clip/    # Print-in-place compliant snap mechanism
```

---

## Quickstart

### 1. Set Up Environment
```bash
git clone git@gitea-lan:cristobal/code-cad.git
cd code-cad

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Example Validation
Execute any of the reference models to inspect geometry and generate exports:
```bash
python3 examples/01_electronics_enclosure/case.py
```

The script outputs a comprehensive inspection report:
```markdown
### Model Inspection: enclosure_base

| Metric | Value |
|---|---|
| Bounding Box (X x Y x Z) | 60.8 x 33.8 x 16.0 mm |
| Solid Volume | 10.76 cm3 (10760.0 mm3) |
| Surface Area | 94.16 cm2 |
| Estimated Weight (PLA 100%) | 13.34 g |
| Estimated Weight (PETG 100%) | 13.67 g |
| Valid BREP Topology | Yes |
| Closed Manifold Shell | Yes |

#### Exported Files
- STEP: `exports/enclosure_base.step`
- STL: `exports/enclosure_base.stl`
- Multi-view SVG: `exports/enclosure_base_views.svg`
```

---

## Using with Claude Code & AI Agents

### In Claude Code
Start Claude Code in this directory:
```bash
claude
```
Then invoke the `/cad` command:
```
/cad Heavy-duty 90-degree bracket to mount a 500g power supply to a wall with M4 screws
```

### In Other Agent Environments
Copy `SKILL.md` to your agent skills directory (e.g., `~/.agents/skills/code-cad/SKILL.md`) or paste the contents of `prompts/01_kickoff_master.md` as your system or kickoff prompt.

---

## Engineering Standards Summary

For complete engineering rules, consult [DFAM_GUIDE.md](DFAM_GUIDE.md).

- **Wall Multiples:** Design walls as integer multiples of nozzle extrusion lines (e.g. 0.84 mm, 1.26 mm, 1.68 mm, 2.10 mm, 2.50 mm for a 0.4 mm nozzle).
- **Elephant's Foot:** Apply a 0.8 mm 45-degree chamfer to all edges touching the build plate.
- **Horizontal Holes:** Use 45-degree teardrop ceilings for horizontal holes larger than 4 mm to avoid bridge droop without support structures.
- **Stress Relief:** Fillet interior 90-degree corners with radius >= 2.0 mm to prevent crack propagation.
- **Hole Compensation:** Add +0.20 mm to +0.35 mm to vertical hole diameters in CAD to account for thermal polymer contraction and chorded polygon paths.

---

## License

MIT License. Designed and maintained by Cristóbal Tormo.
