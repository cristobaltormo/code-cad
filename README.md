# Code-CAD

English | [Español](README.es.md)

A Claude Code skill that designs **verified** 3D-printable parts. Ask for an
object ("a wall mount for my Raspberry Pi 5", "a stand for an iPhone 16 Pro",
"a holder for 4 x 18650 cells") and it:

1. **looks up the real dimensions** of every object involved, from a built-in
   database of verified parts plus web research against official drawings,
   with sources and confidence;
2. **scouts existing designs** on Printables / MakerWorld / Thingiverse for
   proven patterns and known failure points;
3. writes a **spec** with sourced dimensions and tolerances *before* modelling;
4. models the part in Python with [build123d](https://github.com/gumyr/build123d)
   (exact B-Rep, exported to STEP, STL and 3MF);
5. has **two independent agents** - a dimension verifier and a print reviewer -
   measure and review the exported files in their own contexts;
6. **releases** the STL/STEP only through a gate that requires every check to
   pass on the exact file hashes being released.

```
 request ─▶ cad-dimension-researcher ─┐ (parallel, one per real object)
            cad-design-scout ─────────┤
                                      ▼
                     spec.json  (sourced dims, critical dimensions + tolerances)
                                      ▼
                     model.py ─▶ cad build ─▶ cad verify / cad printability
                                      ▼            (self-check loop)
            cad-dimension-verifier ───┤ (parallel, independent, measure the
            cad-print-reviewer ───────┘  exported STEP/STL, never the script)
                                      ▼
                     cad release  ── refuses unless build + auto + dimensions +
                                     printability gates pass on current hashes
```

## Quickstart

```bash
./install.sh              # venv + deps (handles Ubuntu without python3-venv)
claude                    # in this repo
```

```
/cad wall mount for a Raspberry Pi 5, PETG, Bambu P1S
```

Or just describe what you want; the skill triggers on 3D-printing requests.
Results land in `projects/<name>/release/` together with `RELEASE.md`
(measured critical dimensions, print orientation and settings, file hashes).

`./install.sh --global` also links the skill and agents into `~/.claude` so
`/cad` works from any directory.

## What is in the box

| Path | What |
|---|---|
| `.claude/skills/cad/SKILL.md` | The skill: pipeline, gates, DFAM rules |
| `.claude/skills/cad/references/` | Tested build123d cheat sheet, spec format |
| `.claude/agents/cad-dimension-researcher.md` | Finds sourced dimensions of real objects |
| `.claude/agents/cad-design-scout.md` | Distils proven design patterns from model sites |
| `.claude/agents/cad-dimension-verifier.md` | Independent metrology on exported files |
| `.claude/agents/cad-print-reviewer.md` | Independent printability / strength review |
| `bin/cad` | CLI (uses the repo venv from any directory) |
| `cad_tools/` | build123d helpers + pipeline, caliper, renderer, analysis |
| `cad_tools/reference/data/` | Verified reference dimensions (with source URLs) |
| `examples/` | Six reference parts; `05_raspberry_pi5_wall_mount` shows a full verified release |
| `tests/` | Regression tests, including every bug the old version shipped |

## The `cad` CLI

```
cad new <name>                 scaffold projects/<name>/ (spec.json + model template)
cad lookup <words>             search verified reference dimensions (boards, inserts, bearings, ...)
cad printers                   build volumes of 36 current printers
cad build <project>            export STEP/STL/3MF, renders (PNG+SVG), sections, automatic gates
cad verify <project>           build gates + spec.json machine checks on the exported STEP
cad printability <project>     overhangs, bridges, walls, bed contact, chamfer, teardrops, bed fit
cad measure <what> <file.step> virtual caliper: bbox | holes | ray | section | clearance | walls
cad attest <project> --kind dimensions|printability --input <json>
cad status <project>           gate status: PASS / FAIL / MISSING / STALE
cad release <project>          copy to release/ only if every gate passed on current hashes
```

**Visual verification that agents can actually see.** Every build renders
`<part>_views.png` (top/front/right hidden-line views with dimensions, shaded
isometrics with mating objects in orange, bed-side view) and
`<part>_sections.png` (cuts through the centre on three planes with a mm grid).
The agents read these PNGs as images.

**Fit checks against the real object.** Put the researched object in the model
as `MATES = {"phone": solid}`. The build renders it, checks interference, and
the verifier checks the mate against the research.

## Reference database

`cad lookup` covers, with source URLs and confidence per entry:
Raspberry Pi 5 / 4B / 3B+ / Zero 2 W / Pico (incl. connector positions),
Arduino Uno R3/R4 / Nano / Mega, ESP32 DevKits, Pi cameras, ISO screws/nuts/
washers/clearance holes, ruthex / CNC Kitchen / Voron heat-set inserts,
batteries (AA ... 21700), ball and linear bearings, fans, NEMA steppers,
aluminium extrusions, T8/GT2 motion parts, Gridfinity, GoPro mounts, camera
threads, Arca-Swiss, connector cut-outs, LEGO, pipes/hoses and printer build
volumes. Everything else is researched online per project and cached in
`cad_tools/reference/data/researched/`.

## Engineering rules

Defaults in `SKILL.md` and [DFAM_GUIDE.md](DFAM_GUIDE.md): walls in multiples
of the line width; clearances (press 0.05-0.10, sliding 0.15-0.20, loose
0.30-0.40 per side); vertical screw holes ISO 273 + 0.2; heat-set pockets at
the vendor diameter and >= insert length + 1; teardrops for horizontal holes
over 4 mm; 45 deg bed chamfers; loads along XY filaments; parts exported in
print orientation.

## What changed in v0.2

The old checks reported "valid / closed manifold: Yes" for parts that could not
work. The new tools caught all of these in the v0.1 examples:
the enclosure's insert pockets were 3.25 mm deep for a 5.7 mm insert, its lid
vents were blind (0.6 mm skin), the L-bracket's gusset hung over the
counterbore, the cable clip's screw hole left a 0.4 mm skin into the cable
channel, and Gridfinity bins came out as 5 disconnected solids with the body
floating 4.75 mm above the feet. All examples were rebuilt and every one of
these cases is now a regression test.

## License

MIT. Original framework by Cristóbal Tormo.
