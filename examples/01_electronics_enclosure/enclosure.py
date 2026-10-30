"""Two-part enclosure for a Raspberry Pi Pico (board data: `cad lookup pico`).

Build: ./bin/cad build examples/01_electronics_enclosure
Both parts are exported in print orientation: base open side up, lid upside
down (outer face on the bed, lip pointing up). No supports needed.
"""

from build123d import *

from cad_tools.fasteners import heat_set_hole, insert_spec
from cad_tools.features import chamfer_bottom, slot_array

# ---- board (official Pico datasheet) -------------------------------------------
PCB_L, PCB_W, PCB_T = 51.0, 21.0, 1.0
HOLES = [(2.0, 4.8), (2.0, 16.2), (49.0, 4.8), (49.0, 16.2)]   # from PCB corner, USB end at x=0
USB_CENTER_Y = 10.5                                            # micro-USB centred on the short edge
INSERT = insert_spec("M2")                                     # ruthex M2x4: hole 3.2, L 4.0, wall 1.3

# ---- design ------------------------------------------------------------------
WALL = 2.0               # 5 perimeters
FLOOR = 2.0
CLEAR = 0.5              # board to wall, per side
STANDOFF_H = 4.0         # clears solder joints; pocket (5.0) leaves 1.0 mm floor below
BOSS_D = INSERT["hole"] + 2 * INSERT["wall"] + 0.4
INNER_H = STANDOFF_H + PCB_T + 9.0      # room for headers / components above the PCB
IN_L, IN_W = PCB_L + 2 * CLEAR, PCB_W + 2 * CLEAR
OUT_L, OUT_W = IN_L + 2 * WALL, IN_W + 2 * WALL
BASE_H = FLOOR + INNER_H
R_OUT = 3.0
USB_OPENING = (11.0, 7.0)               # width x height: cable overmold + 0.5/side
LID_T = 2.0
LIP_H, LIP_WALL, LIP_CLEAR = 3.0, 1.2, 0.2

# board placed with its USB end towards -X, centred in the cavity
bx0, by0 = -PCB_L / 2, -PCB_W / 2
pcb_z = FLOOR + STANDOFF_H

with BuildPart() as base:
    Box(OUT_L, OUT_W, BASE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(base.edges().filter_by(Axis.Z), R_OUT)
    with Locations((0, 0, FLOOR)):
        Box(IN_L, IN_W, BASE_H, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    with Locations(*[(bx0 + x, by0 + y, FLOOR) for x, y in HOLES]):
        Cylinder(BOSS_D / 2, STANDOFF_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
base_part = chamfer_bottom(base.part, 0.8)
for x, y in HOLES:      # pocket = L + 1 = 5.0 mm, continues into the floor (standoff is only 3)
    base_part -= Pos(bx0 + x, by0 + y, pcb_z) * heat_set_hole("M2")
usb_z = pcb_z + PCB_T + 1.0               # micro-USB centre ~1 mm above PCB top
base_part -= Pos(-OUT_L / 2, by0 + USB_CENTER_Y, usb_z) * Box(2 * WALL + 1.0, *USB_OPENING)  # wall only

with BuildPart() as lid:
    Box(OUT_L, OUT_W, LID_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(lid.edges().filter_by(Axis.Z), R_OUT)
    with Locations((0, 0, LID_T)):      # hollow rim lip that slides into the base opening
        Box(IN_L - 2 * LIP_CLEAR, IN_W - 2 * LIP_CLEAR, LIP_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Box(IN_L - 2 * LIP_CLEAR - 2 * LIP_WALL, IN_W - 2 * LIP_CLEAR - 2 * LIP_WALL, LIP_H,
            align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
lid_part = chamfer_bottom(lid.part, 0.6)
lid_part -= Rot(0, 0, 90) * slot_array(slot_width=1.6, slot_length=12, pitch=4.0, count=8, depth=20)  # through

pico = Pos(0, 0, pcb_z) * Box(PCB_L, PCB_W, PCB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))

EXPORT_SOLIDS = {"enclosure_base": base_part, "enclosure_lid": lid_part}
MATES = {"pico": pico}
