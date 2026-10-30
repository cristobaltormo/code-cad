---
name: cad
description: Design parametric, verified 3D-printable parts (STEP/STL/3MF) with build123d. Use whenever the user wants something 3D printed or modelled - holders, mounts, stands, cases, enclosures, brackets, adapters, clips, replacement parts, organisers, Gridfinity - especially when it must fit a real object (a phone, board, tool, battery, appliance). Looks up the object's real dimensions online, designs to a written spec, and runs independent verifier agents before any STL is handed over.
argument-hint: "[what to make, what it must fit, constraints]"
---

# CAD: research -> spec -> design -> independent verification -> release

You are the lead design engineer. Sub-agents do research and verification in
their own contexts so their judgement stays independent of yours. **The user
gets STL/STEP files only from `release/`, and `cad release` refuses unless every
gate passed on the exact files being released.**

Request: $ARGUMENTS

All commands run from the repo root (`${CLAUDE_PROJECT_DIR}`): `./bin/cad <cmd>`.
If this is not the code-cad repo (skill installed with `install.sh --global`),
use `cad <cmd>` from PATH instead; projects are then created in the code-cad
repo's `projects/` folder (paths are printed by `cad new`). If `.venv` is
missing, run `./install.sh`.

## 1. Intake (you)

Extract: function, loads, environment (heat, UV, outdoors), material if given,
printer if given, and **every real-world object the part touches** (the phone,
the board, the screw, the shelf, the hose). Ask the user only about things
research cannot answer (their preference, their printer, measurements of their
specific unit). Defaults: PETG, 0.4 nozzle, `generic_220` printer, sliding fit.

Then `./bin/cad new <snake_name>` -> `projects/<name>/`.

## 2. Research (parallel agents - one message, several Agent calls)

For EACH real-world object, spawn **cad-dimension-researcher**
(subagent_type `cad-dimension-researcher`) with: object name and variant,
which features matter, project dir. Standard parts (screws, inserts, nuts,
bearings, boards, batteries) are often already in the database: still let the
researcher confirm and cite them (`./bin/cad lookup <words>` shows them).

At the same time spawn **cad-design-scout** with the object type and
constraints for proven design patterns from Printables/MakerWorld/Thingiverse.

Wait for all of them. If any critical dimension comes back `low` confidence or
in `needs_caliper_check`, ask the user to measure exactly those (say what and
where) before designing. Never substitute a guess for a fit-critical number.

## 3. Spec (you) - the contract written BEFORE the model

Fill `projects/<name>/spec.json` (format: `references/spec-format.md`):
objects with sourced dimensions, requirements, `features` (each one visually
checkable), and `critical_dimensions` = every number that decides fit or
function, with nominal and tolerance derived from the research + DFAM rules
(e.g. pocket = phone width 71.5 + 2 x 0.4 clearance = 72.3 +0.2/-0.1). Add
machine `checks` (max_size, solids, hole counts/diameters, clearance to
mates, min_wall). Delete the template's `_example` entries.

Show the user a short summary of the key numbers and assumptions, then continue
without waiting unless something is genuinely their call.

## 4. Design (you)

Write `projects/<name>/<name>.py` following `references/build123d-cheatsheet.md`
(tested patterns + pitfalls) and the DFAM rules below. Parameters at the top,
derived from the spec. Export parts **in print orientation, bed face at Z = 0**.
Model each researched object as a simple solid in `MATES` where it sits (a box
or rounded box of its envelope plus critical features such as a camera bump or
connector) - the build renders it orange and checks interference.

Use `cad_tools` helpers: `fasteners.counterbore / countersink / heat_set_hole /
heat_set_boss / hex_nut_pocket / clearance_dia`, `features.chamfer_bottom /
teardrop_hole / slot_array`, `gridfinity.gridfinity_bin`. Threads, gears and
other advanced parts: `pip install bd_warehouse` (thread, gear, fastener,
bearing modules) when needed.

## 5. Build + self-check loop (you)

```
./bin/cad build <name>          # STEP/STL/3MF, renders, report.json, basic gates
./bin/cad verify <name>         # build gates + spec.json machine checks
./bin/cad printability <name>   # overhangs, bridges, walls, chamfer, bed fit
```

Look at `build/<part>_views.png` and `build/<part>_sections.png` yourself (Read
tool shows images). Fix and rebuild until build + verify PASS and printability
has no FAIL. A rebuild deletes previous verification - that is intended.

## 6. Independent verification (parallel agents - one message, two Agent calls)

Spawn both at once, giving each only the project dir and the user's request:

- **cad-dimension-verifier** - measures the exported STEP/STL against every
  critical dimension and feature, checks mates, attests.
- **cad-print-reviewer** - printability/strength review, attests, print settings.

Do not tell them what you think the numbers are. If either FAILs: fix the
model, rebuild, re-run `verify`/`printability`, and re-spawn BOTH verifiers
(the old attestations are stale). Max 4 rounds, then report to the user.

## 7. Release (you)

`./bin/cad release <name>` - copies STEP/STL/3MF/SVG/PNG + script +
RELEASE.md to `projects/<name>/release/` only if build, auto, dimensions and
printability gates are PASS (printability WARN allowed) and every attestation
matches the current file hashes. `./bin/cad status <name>` shows the gates.

Report to the user: release paths, bbox + mass, the critical-dimension table
from RELEASE.md, print orientation and settings, warnings, and sources used for
the object dimensions. Never hand over files from `build/`.

## DFAM rules (defaults; spec may override with reasons)

- Walls: multiples of line width - 0.4 nozzle: 0.8 / 1.2 / 1.6 / 2.0 / 2.4 mm;
  structural >= 2.4; nothing below 0.8 (`printers.wall_thickness(n)` gives
  slicer-exact widths).
- Clearance per side: press 0.05-0.10, sliding 0.15-0.20, loose 0.30-0.40;
  around real objects (phones, boards) 0.3-0.5; connector openings +0.5/side.
- Holes: vertical screw clearance = ISO 273 medium + 0.2 (`clearance_dia`);
  heat-set pockets at the vendor diameter, depth >= insert length + 1,
  boss wall >= vendor minimum (`heat_set_boss` enforces it); horizontal holes
  > 4 mm as 45 deg teardrops; nothing vertical under 1.5 mm.
- Overhangs <= 45 deg; bridges <= 15 mm; turn ceilings into 45 deg chamfers.
- Bed edges: 0.6-1.0 mm 45 deg chamfer (never a fillet on the bed).
- Interior corners on loaded features: fillet >= 2 mm; hook/snap roots
  fillet >= 0.5 x beam thickness.
- Orientation: tensile/bending loads along XY filaments, never across layers;
  snap beams and clips flex in XY.
- Edge distance for bolts >= 2 x hole diameter; washers or counterbores under
  heads on plastic.
- Materials: PLA stiff/brittle, creeps > 50 C (no cars, no dishwashers);
  PETG default functional; ASA outdoors; TPU for grips/feet.
