# 05 - Raspberry Pi 5 wall mount (full verified pipeline)

This example went through the whole skill pipeline and is the reference for
what a release looks like:

- `spec.json` - sourced dimensions (official Pi 5 drawing, ruthex table),
  critical dimensions with tolerances, machine checks
- `pi5_wall_mount.py` - the model (Pi 5 as an orange `MATE`)
- `verification/` - automatic checks plus attestations from the independent
  `cad-dimension-verifier` and `cad-print-reviewer` agents, bound to the
  build's file hashes
- `release/` - the files that passed, with `RELEASE.md`

Round 1 of verification sent it back: both agents independently flagged the
countersinks 1.8 mm from the plate ends; they also flagged a zero-margin
insert pocket, a loose screw hole, a 4.5-line standoff wall and unfilleted
standoff roots. Round 2 passed after the fixes.

```bash
./bin/cad status examples/05_raspberry_pi5_wall_mount   # all gates PASS
```
