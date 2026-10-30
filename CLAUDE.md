# Code-CAD: verified parametric CAD for 3D printing

This repo designs 3D-printable parts with Python + build123d. For any modelling
request, use the `cad` skill (`.claude/skills/cad/SKILL.md`): it defines the
pipeline, the agents and the release gate. Tools: `./bin/cad <cmd>`.

## Non-negotiables

1. **No guessed dimensions.** Every real object the part touches gets sourced
   dimensions: `./bin/cad lookup`, then the `cad-dimension-researcher` agent
   (web research against official drawings/datasheets). If confidence is low,
   ask the user for specific caliper measurements.
2. **Spec before model.** `projects/<name>/spec.json` holds sourced object
   dimensions, critical dimensions with tolerances and machine checks.
3. **Independent verification.** `cad-dimension-verifier` and
   `cad-print-reviewer` run as separate agents (in parallel) on the exported
   files. Never pass them your own numbers.
4. **Release gate.** STL/STEP/3MF go to the user only from
   `projects/<name>/release/`, produced by `./bin/cad release`, which refuses
   unless every gate passed on the current file hashes. Never hand over files
   from `build/`.
5. **Look at the renders.** `build/<part>_views.png` and `_sections.png` are
   images; read them after every build.

## Modelling conventions

- Millimetres; export parts in print orientation with the bed face at Z = 0;
  exactly one connected solid per part.
- Named parameters at the top of the script, derived from the spec;
  `EXPORT_SOLIDS = {...}`, reference objects in `MATES = {...}`.
- Patterns and pitfalls: `.claude/skills/cad/references/build123d-cheatsheet.md`.
- DFAM defaults: `SKILL.md` "DFAM rules" and `DFAM_GUIDE.md`.

## Deliverables per model

`<model>.py`, `.step`, `.stl`, `.3mf`, `<part>_views.svg` / `.png`,
`<part>_sections.png`, and `RELEASE.md` (measured critical dimensions, print
orientation, settings, hashes).

## Repo maintenance

`.venv/bin/python -m pytest -q` must pass after changing `cad_tools/` or the
cheat sheet. Reference data changes need source URLs.
