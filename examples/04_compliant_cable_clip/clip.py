"""Snap-in cable clip with a side screw tab, modelled in print orientation.

Build: ./bin/cad build examples/04_compliant_cable_clip

The C-ring profile lies in XY and is extruded along Z, so the flexing arms are
continuous concentric perimeters (they bend in XY, never across layers). The
mounting tab extends sideways so the screw head has its own seat and the
screw never enters the cable channel (the old design drilled up into the
channel and left a 0.4 mm skin). The screw hole is horizontal in print
orientation, so it is a teardrop.
"""

from build123d import *

from cad_tools.features import chamfer_bottom, teardrop_hole

CABLE_D = 8.0
CLEAR = 0.3                    # loose fit around the cable
WALL = 2.0                     # ring wall (5 lines) - flexible in PETG
WIDTH = 10.0                   # clip width = print height
ENTRY = 0.75 * CABLE_D         # snap-in opening; arms deflect ~1 mm each
TAB_L = 14.0                   # tab length beyond the ring
TAB_T = 3.0                    # tab thickness
SCREW_HOLE_D = 4.4             # 4 mm wood screw / M4, loose
ROOT_FILLET = 1.5

R_IN = CABLE_D / 2 + CLEAR
R_OUT = R_IN + WALL

with BuildSketch() as prof:
    Circle(R_OUT)
    # tab along the mounting surface (y = -R_OUT), extending to +X
    with Locations((0, -R_OUT + TAB_T / 2)):
        Rectangle(R_OUT + TAB_L, TAB_T, align=(Align.MIN, Align.CENTER))
    root = prof.vertices().filter_by(lambda v: abs(v.Y - (-R_OUT + TAB_T)) < 1e-6 and 0 < v.X < R_OUT)
    fillet(root, ROOT_FILLET)
    # cut the cable channel and the snap-in gap AFTER adding the tab
    Circle(R_IN, mode=Mode.SUBTRACT)
    with Locations((0, R_OUT)):                       # entry gap at +Y
        Rectangle(ENTRY, 2 * R_OUT, mode=Mode.SUBTRACT)    # reaches the centre: no cusps

clip = extrude(prof.sketch, amount=WIDTH)
# round the outer snap-in lips so the cable slides in (inner acute corners cannot be filleted)
lips = clip.edges().filter_by(Axis.Z).filter_by(lambda e: abs(abs(e.center().X) - ENTRY / 2) < 1e-3 and e.center().Y > R_IN)
clip = clip.fillet(0.6, lips)
hole_x = R_OUT + TAB_L / 2 + 1.0
clip -= teardrop_hole(SCREW_HOLE_D / 2, length=TAB_T * 4, axis="Y", center=(hole_x, -R_OUT + TAB_T / 2, WIDTH / 2))
clip = chamfer_bottom(clip, 0.4)

cable = Pos(0, 0, -5) * Cylinder(CABLE_D / 2, WIDTH + 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

EXPORT_SOLIDS = {"cable_clip": clip}
MATES = {"cable": cable}
