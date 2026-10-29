import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from build123d import (
    BuildPart,
    BuildSketch,
    Plane,
    Circle,
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
TAPER_ANGLE_DEG = 1.5

R_HOSE_OUTER = OUTER_DIAMETER_HOSE / 2.0
R_TOOL_OUTER = OUTER_DIAMETER_TOOL / 2.0
TAPER_OFFSET = SLEEVE_LENGTH_HOSE * math.tan(math.radians(TAPER_ANGLE_DEG))

def build_adapter():
    h1 = SLEEVE_LENGTH_HOSE
    ht = TRANSITION_LENGTH
    h2 = SLEEVE_LENGTH_TOOL

    r_hose_base = R_HOSE_OUTER - TAPER_OFFSET
    r_hose_top = R_HOSE_OUTER
    r_tool_base = R_TOOL_OUTER
    r_tool_tip = R_TOOL_OUTER - TAPER_OFFSET

    with BuildPart() as adapter:
        with BuildSketch(Plane.XY):
            Circle(radius=r_hose_base)
        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=r_hose_top)
        loft()

        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=r_hose_top)
        with BuildSketch(Plane.XY.offset(h1 + ht)):
            Circle(radius=r_tool_base)
        loft()

        with BuildSketch(Plane.XY.offset(h1 + ht)):
            Circle(radius=r_tool_base)
        with BuildSketch(Plane.XY.offset(h1 + ht + h2)):
            Circle(radius=r_tool_tip)
        loft()

        with BuildSketch(Plane.XY.offset(-1.0)):
            Circle(radius=r_hose_base - WALL)
        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=r_hose_top - WALL)
        loft(mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XY.offset(h1)):
            Circle(radius=r_hose_top - WALL)
        with BuildSketch(Plane.XY.offset(h1 + ht)):
            Circle(radius=r_tool_base - WALL)
        loft(mode=Mode.SUBTRACT)

        with BuildSketch(Plane.XY.offset(h1 + ht)):
            Circle(radius=r_tool_base - WALL)
        with BuildSketch(Plane.XY.offset(h1 + ht + h2 + 1.0)):
            Circle(radius=r_tool_tip - WALL)
        loft(mode=Mode.SUBTRACT)

        chamfer(adapter.faces().sort_by(Axis.Z)[0].edges(), length=0.6)
        chamfer(adapter.faces().sort_by(Axis.Z)[-1].edges(), length=0.6)

    return adapter.part

EXPORT_SOLIDS = {"shop_vac_adapter": build_adapter()}

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "exports"
    for name, solid in EXPORT_SOLIDS.items():
        print(inspect_solid(solid, name=name, out_dir=str(out_dir)))
