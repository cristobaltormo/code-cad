---
name: code-cad
description: Verified parametric 3D CAD for 3D printing with build123d. Researches real object dimensions, writes a spec, models the part, runs independent dimension + printability verification and releases STEP/STL/3MF only through a hash-bound gate.
---

# Code-CAD (portable summary)

The full Claude Code version lives in `.claude/skills/cad/SKILL.md` with its
agents in `.claude/agents/`. This file is for agent environments that load a
single skill file.

1. **Research**: for every real object the part touches, find sourced
   dimensions (`./bin/cad lookup <words>`, then official drawings/datasheets
   online; follow `.claude/agents/cad-dimension-researcher.md`).
2. **Spec**: `./bin/cad new <name>`, then fill `projects/<name>/spec.json` with
   sourced dimensions, `critical_dimensions` (nominal + tolerances) and `checks`
   (`.claude/skills/cad/references/spec-format.md`).
3. **Design**: `projects/<name>/<name>.py` with build123d
   (`.claude/skills/cad/references/build123d-cheatsheet.md`), print
   orientation, bed at Z = 0, `EXPORT_SOLIDS` + `MATES`.
4. **Build & self-check**: `./bin/cad build|verify|printability <name>`; read
   the PNG renders in `build/`.
5. **Independent verification**: run the procedures in
   `.claude/agents/cad-dimension-verifier.md` and
   `.claude/agents/cad-print-reviewer.md` in *separate* sessions/sub-agents
   that never see the designer's reasoning; they record results with
   `./bin/cad attest`.
6. **Release**: `./bin/cad release <name>`; deliver only `release/` files.

DFAM defaults: walls in line-width multiples (0.8/1.2/1.6/2.0/2.4); clearances
press 0.05-0.10, sliding 0.15-0.20, loose 0.30-0.40 per side; screw holes ISO
273 + 0.2; heat-set pockets at vendor diameter and >= length + 1; teardrops for
horizontal holes > 4 mm; 45 deg bed chamfers; overhangs <= 45 deg; loads along
XY.
