import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from build123d import (
    BuildPart,
    BuildSketch,
    Plane,
    Box,
    Cylinder,
    Locations,
    Polygon,
    extrude,
    fillet,
    chamfer,
    Axis,
    Mode,
)

from cad_tools.inspect import inspect_solid

LEG_LENGTH_X = 50.0
LEG_LENGTH_Z = 50.0
BRACKET_WIDTH = 25.0
THICKNESS = 6.0
GUSSET_THICKNESS = 4.0
HOLE_DIAMETER = 5.2
COUNTERBORE_DIAMETER = 10.0
COUNTERBORE_DEPTH = 3.5

def build_bracket():
    with BuildPart() as bracket:
        with Locations((LEG_LENGTH_X / 2.0, 0, THICKNESS / 2.0)):
            Box(LEG_LENGTH_X, BRACKET_WIDTH, THICKNESS)

        with Locations((THICKNESS / 2.0, 0, LEG_LENGTH_Z / 2.0)):
            Box(THICKNESS, BRACKET_WIDTH, LEG_LENGTH_Z)

        inside_edges = bracket.edges().filter_by(Axis.Y).filter_by_position(Axis.X, THICKNESS - 0.2, THICKNESS + 0.2)
        if inside_edges:
            fillet(inside_edges, radius=3.0)

        gusset_hyp = 38.0
        with BuildSketch(Plane.XZ):
            Polygon([(THICKNESS, THICKNESS), (gusset_hyp, THICKNESS), (THICKNESS, gusset_hyp)])
        extrude(amount=GUSSET_THICKNESS / 2.0, both=True)

        chamfer(bracket.faces().sort_by(Axis.Z)[0].edges().filter_by(Axis.Y), length=0.8)

        hole_x = LEG_LENGTH_X - 12.0
        with Locations((hole_x, 0, THICKNESS / 2.0)):
            Cylinder(radius=HOLE_DIAMETER / 2.0, height=THICKNESS + 2.0, mode=Mode.SUBTRACT)
            with Locations((0, 0, (THICKNESS - COUNTERBORE_DEPTH) / 2.0 + 0.5)):
                Cylinder(radius=COUNTERBORE_DIAMETER / 2.0, height=COUNTERBORE_DEPTH + 1.0, mode=Mode.SUBTRACT)

        hole_z = LEG_LENGTH_Z - 12.0
        with Locations((THICKNESS / 2.0, 0, hole_z)):
            with Locations((0, 0, 0)):
                Cylinder(radius=HOLE_DIAMETER / 2.0, height=THICKNESS + 2.0, mode=Mode.SUBTRACT)

    return bracket.part

EXPORT_SOLIDS = {"l_bracket": build_bracket()}

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "exports"
    for name, solid in EXPORT_SOLIDS.items():
        print(inspect_solid(solid, name=name, out_dir=str(out_dir)))
