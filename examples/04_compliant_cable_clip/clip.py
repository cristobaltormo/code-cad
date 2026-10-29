import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from build123d import (
    BuildPart,
    BuildSketch,
    Circle,
    Rectangle,
    Box,
    Cylinder,
    Locations,
    Rotation,
    extrude,
    fillet,
    Axis,
    Mode,
)

from cad_tools.inspect import inspect_solid

CABLE_DIAMETER = 8.0
CLIP_WIDTH = 12.0
WALL = 2.4
MOUNT_HOLE_DIA = 4.2
ENTRY_GAP = 4.5

R_INNER = CABLE_DIAMETER / 2.0
R_OUTER = R_INNER + WALL

def build_clip():
    with BuildPart() as clip:
        with BuildSketch():
            Circle(radius=R_OUTER)
            Circle(radius=R_INNER, mode=Mode.SUBTRACT)
            with Locations((0, R_OUTER)):
                Rectangle(ENTRY_GAP, WALL * 2.0 + 2.0, mode=Mode.SUBTRACT)

        extrude(amount=CLIP_WIDTH)

        base_height = WALL
        base_width = R_OUTER * 2.0 + 4.0
        with Locations((0, -R_OUTER - base_height / 2.0 + 0.1, CLIP_WIDTH / 2.0)):
            Box(base_width, base_height, CLIP_WIDTH)

        with Locations((0, -R_OUTER - base_height / 2.0, CLIP_WIDTH / 2.0)):
            with Locations(Rotation(90, 0, 0)):
                Cylinder(radius=MOUNT_HOLE_DIA / 2.0, height=base_height + 4.0, mode=Mode.SUBTRACT)

        top_edges = clip.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-4:]
        fillet(top_edges, radius=0.6)

    return clip.part

EXPORT_SOLIDS = {"cable_clip": build_clip()}

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "exports"
    for name, solid in EXPORT_SOLIDS.items():
        print(inspect_solid(solid, name=name, out_dir=str(out_dir)))
