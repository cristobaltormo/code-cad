import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from build123d import (
    BuildPart,
    Box,
    Locations,
    Axis,
    fillet,
    chamfer,
    Mode,
)

from cad_tools.fasteners import heat_set_boss
from cad_tools.features import ventilation_slots
from cad_tools.inspect import inspect_solid

WALL = 2.4
CLEARANCE = 0.5
PCB_LENGTH = 55.0
PCB_WIDTH = 28.0
PCB_THICKNESS = 1.6
STANDOFF_HEIGHT = 4.0

INNER_LENGTH = PCB_LENGTH + CLEARANCE * 2
INNER_WIDTH = PCB_WIDTH + CLEARANCE * 2
OUTER_LENGTH = INNER_LENGTH + WALL * 2
OUTER_WIDTH = INNER_WIDTH + WALL * 2
BASE_HEIGHT = 16.0
LID_HEIGHT = 4.0

HOLE_OFFSET_X = 2.5
HOLE_OFFSET_Y = 2.5
BOSS_X = PCB_LENGTH / 2.0 - HOLE_OFFSET_X
BOSS_Y = PCB_WIDTH / 2.0 - HOLE_OFFSET_Y

def build_case():
    with BuildPart() as base:
        Box(OUTER_LENGTH, OUTER_WIDTH, BASE_HEIGHT)
        fillet(base.edges().filter_by(Axis.Z), radius=3.0)
        chamfer(base.faces().sort_by(Axis.Z)[0].edges(), length=0.8)

        cavity_z = WALL / 2.0 + 0.1
        with Locations((0, 0, cavity_z)):
            Box(INNER_LENGTH, INNER_WIDTH, BASE_HEIGHT - WALL + 0.2, mode=Mode.SUBTRACT)

        boss_z = -BASE_HEIGHT / 2.0 + WALL + STANDOFF_HEIGHT / 2.0
        for bx in (-BOSS_X, BOSS_X):
            for by in (-BOSS_Y, BOSS_Y):
                with Locations((bx, by, boss_z)):
                    boss = heat_set_boss("M2.5", total_height=STANDOFF_HEIGHT)
                    base.part = base.part + boss

        usb_cut_y = -OUTER_WIDTH / 2.0
        usb_cut_z = -BASE_HEIGHT / 2.0 + WALL + STANDOFF_HEIGHT + PCB_THICKNESS + 1.7
        with Locations((0, usb_cut_y, usb_cut_z)):
            Box(12.0, WALL * 2.0 + 1.0, 6.5, mode=Mode.SUBTRACT)

    with BuildPart() as lid:
        Box(OUTER_LENGTH, OUTER_WIDTH, LID_HEIGHT)
        fillet(lid.edges().filter_by(Axis.Z), radius=3.0)
        chamfer(lid.faces().sort_by(Axis.Z)[-1].edges(), length=0.8)

        lip_depth = 1.6
        lip_z = -LID_HEIGHT / 2.0 - lip_depth / 2.0
        with Locations((0, 0, lip_z)):
            Box(INNER_LENGTH - 0.4, INNER_WIDTH - 0.4, lip_depth)

        vents = ventilation_slots(slot_width=1.8, slot_length=16.0, pitch=3.6, count=6, thickness=LID_HEIGHT)
        lid.part = lid.part - vents

    return {"enclosure_base": base.part, "enclosure_lid": lid.part}

EXPORT_SOLIDS = build_case()

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "exports"
    for name, solid in EXPORT_SOLIDS.items():
        print(inspect_solid(solid, name=name, out_dir=str(out_dir)))
