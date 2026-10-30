"""Heavy 90 deg shelf bracket, modelled IN PRINT ORIENTATION (lying on its side).

Build: ./bin/cad build examples/02_structural_l_bracket

The L profile (with a full-width triangular web) lies in XY and is extruded
along Z, so legs and web are continuous perimeters in the XY plane: the
bending load of a shelf runs along the filaments, never across layers. The
screw holes are horizontal in this orientation, so they are 45 deg teardrops
(apex +Z) and print without support. Holes sit clear of the web so the screw
heads and the driver have room.
"""

from build123d import *

from cad_tools.fasteners import clearance_dia
from cad_tools.features import chamfer_bottom, teardrop_hole

LEG = 60.0            # leg length, both legs
T = 6.0               # leg thickness
WIDTH = 30.0          # bracket width = print height (Z)
WEB = 28.0            # web size from the inner corner along each leg
WEB_FILLET = 3.0      # fillet where the web meets each leg
SCREW = "M5"
HOLE_FROM_END = 14.0  # hole centre from the leg end (>= 2.5 x d)

HOLE_D = clearance_dia(SCREW)   # ISO 273 medium + 0.2 printed compensation

with BuildSketch() as profile:
    Polygon((0, 0), (LEG, 0), (LEG, T), (T + WEB, T), (T, T + WEB), (T, LEG), (0, LEG), align=None)
    corners = profile.vertices().filter_by(
        lambda v: (abs(v.X - (T + WEB)) < 1e-6 and abs(v.Y - T) < 1e-6)
        or (abs(v.X - T) < 1e-6 and abs(v.Y - (T + WEB)) < 1e-6))
    fillet(corners, WEB_FILLET)

bracket = extrude(profile.sketch, amount=WIDTH)
hole_at = LEG - HOLE_FROM_END
bracket -= teardrop_hole(HOLE_D / 2, length=T * 4, axis="Y", center=(hole_at, T / 2, WIDTH / 2))
bracket -= teardrop_hole(HOLE_D / 2, length=T * 4, axis="X", center=(T / 2, hole_at, WIDTH / 2))
bracket = chamfer_bottom(bracket, 0.8)

EXPORT_SOLIDS = {"l_bracket": bracket}
