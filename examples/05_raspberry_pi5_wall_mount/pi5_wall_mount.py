"""Raspberry Pi 5 wall mount plate. Build: ./bin/cad build pi5_wall_mount

Print flat as exported (plate on the bed). Pi hole pattern and insert data come
from the reference database (official Pi 5 drawing, ruthex size table).
"""

from build123d import *

from cad_tools.fasteners import countersink, heat_set_hole, insert_spec
from cad_tools.features import chamfer_bottom

# ---- researched / spec values ----------------------------------------------
PI_L, PI_W, PCB_T = 85.0, 56.0, 1.6
HOLE_PITCH_X, HOLE_PITCH_Y = 58.0, 49.0
HOLE_OFFSET = 3.5                      # hole centre from left/bottom board edge
INSERT = insert_spec("M2.5")           # ruthex: hole 4.0, L 5.7, min wall 1.6

# ---- design parameters --------------------------------------------------------
PLATE_T = 4.0
STANDOFF_H = 5.0                       # above the plate top
STANDOFF_WALL = 2.0                    # 5 lines @0.4, >= vendor 1.6
STANDOFF_D = INSERT["hole"] + 2 * STANDOFF_WALL
MARGIN = 4.0                           # plate border around the board
SCREW_END = 13.0                       # extra plate length per end for wall screws
SCREW_X = 49.0                         # >= 2 x d from the plate end, countersink clear of the board
SCREW_HOLE_D = 4.4                     # 4 mm wood screw + 0.4 loose fit
POCKET_EXTRA = 1.4                     # insert L + 1.4 = 7.1 mm (vendor min L + 1)
ROOT_FILLET = 1.0
PLATE_L = PI_L + 2 * MARGIN + 2 * SCREW_END
PLATE_W = PI_W + 2 * MARGIN
CORNER_R = 4.0
BED_CHAMFER = 0.8

# board centred on the plate; hole pattern centre relative to board centre
board_x0, board_y0 = -PI_L / 2, -PI_W / 2
holes = [(board_x0 + HOLE_OFFSET + dx, board_y0 + HOLE_OFFSET + dy)
         for dx in (0, HOLE_PITCH_X) for dy in (0, HOLE_PITCH_Y)]

with BuildPart() as bp:
    with BuildSketch():
        RectangleRounded(PLATE_L, PLATE_W, CORNER_R)
    extrude(amount=PLATE_T)
    with BuildSketch(Plane.XY.offset(PLATE_T)):
        with Locations(*holes):
            Circle(STANDOFF_D / 2)
    extrude(amount=STANDOFF_H)
    roots = bp.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[1]   # standoff bases at z = PLATE_T
    fillet(roots, ROOT_FILLET)

plate = chamfer_bottom(bp.part, BED_CHAMFER)
top = PLATE_T + STANDOFF_H
for x, y in holes:
    plate -= Pos(x, y, top) * heat_set_hole("M2.5", extra_depth=POCKET_EXTRA)
for sx in (-SCREW_X, SCREW_X):
    plate -= Pos(sx, 0, PLATE_T) * countersink("M4", through=PLATE_T + 2, hole_d=SCREW_HOLE_D)

pi5 = Pos(0, 0, top) * Box(PI_L, PI_W, PCB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
for x, y in holes:
    pi5 -= Pos(x, y, top) * Cylinder(2.7 / 2, 10)

EXPORT_SOLIDS = {"plate": plate}
MATES = {"rpi5": pi5}
