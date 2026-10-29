import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from build123d import (
    BuildPart,
    BuildSketch,
    Plane,
    Circle,
    extrude,
    loft,
    chamfer,
    Axis,
    Mode,
)

from cad_tools.inspect import inspect_solid

WALL = 2.4
OUTER_DIAMETER_HOSE = 36.0
OUTER_DIAMETER_TOOL = 31.0
SLEEVE_LENGTH_HOSE = 28.0
TRANSITION_LENGTH = 20.0
SLEEVE_LENGTH_TOOL = 28.0

R_HOSE_OUTER = OUTER_DIAMETER_HOSE / 2.0
R_TOOL_OUTER = OUTER_DIAMETER_TOOL / 2.0
R_HOSE_INNER = R_HOSE_OUTER - WALL
R_TOOL_INNER = R_TOOL_OUTER - WALL

def build_adapter():
    h1 = SLEEVE_LENGTH_HOSE
    h_trans = TRANSITION_LENGTH
    h2 = SLEEVE_LENGTH_TOOL

    with BuildPart() as adapter:
        with BuildSketch(Plane.XY):
            Circle(radius=R_HOSE_OUTER)
        extrude(amount=h1)

        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=R_HOSE_OUTER)
        with BuildSketch(Plane.XY.offset(h1 + h_trans)):
            Circle(radius=R_TOOL_OUTER)
        loft()

        with BuildSketch(Plane.XY.offset(h1 + h_trans)):
            Circle(radius=R_TOOL_OUTER)
        extrude(amount=h2)

        with BuildSketch(Plane.XY.offset(-1.0)):
            Circle(radius=R_HOSE_INNER)
        extrude(amount=h1 + 1.0, mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=R_HOSE_INNER)
        with BuildSketch(Plane.XY.offset(h1 + h_trans)):
            Circle(radius=R_TOOL_INNER)
        loft(mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XY.offset(h1 + h_trans)):
            Circle(radius=R_TOOL_INNER)
        extrude(amount=h2 + 2.0, mode=Mode.SUBTRACT)

        chamfer(adapter.faces().sort_by(Axis.Z)[0].edges(), length=0.8)
        chamfer(adapter.faces().sort_by(Axis.Z)[-1].edges(), length=0.8)

    return adapter.part

EXPORT_SOLIDS = {"shop_vac_adapter": build_adapter()}

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "exports"
    for name, solid in EXPORT_SOLIDS.items():
        print(inspect_solid(solid, name=name, out_dir=str(out_dir)))
