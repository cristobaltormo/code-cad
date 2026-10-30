"""Gridfinity bins (Zack Freedman spec; cross-checked against gridfinity-rebuilt).

Bin height convention: total height = 7 mm x U, measured from the bottom of the
feet to the top of the walls, excluding any stacking lip. Origin: XY centred,
bed at Z = 0 (print orientation).
"""

from __future__ import annotations

from build123d import (Align, BuildPart, BuildSketch, Cylinder, Locations, Mode, Plane,
                       RectangleRounded, extrude, loft)

GRIDFINITY_PITCH = 42.0
GRIDFINITY_TOLERANCE = 0.5          # bin outer = pitch*n - 0.5
GRIDFINITY_CORNER_RADIUS = 3.75     # bin outer corner radius
UNIT_HEIGHT = 7.0
BASE_HEIGHT = 4.75                  # 0.8 @45 + 1.8 vertical + 2.15 @45
MAGNET_HOLE_DIA = 6.5
MAGNET_HOLE_DEPTH = 2.4
MAGNET_OFFSET = 13.0                # from cell centre (26 mm apart)


def _foot(magnet_holes=True):
    """One 42 mm cell foot, Z 0..4.75."""
    with BuildPart() as cell:
        with BuildSketch(Plane.XY):
            RectangleRounded(35.6, 35.6, radius=0.8)
        with BuildSketch(Plane.XY.offset(0.8)):
            RectangleRounded(37.2, 37.2, radius=1.6)
        loft()
        with BuildSketch(Plane.XY.offset(0.8)):
            RectangleRounded(37.2, 37.2, radius=1.6)
        extrude(amount=1.8)
        with BuildSketch(Plane.XY.offset(2.6)):
            RectangleRounded(37.2, 37.2, radius=1.6)
        with BuildSketch(Plane.XY.offset(BASE_HEIGHT)):
            RectangleRounded(41.5, 41.5, radius=GRIDFINITY_CORNER_RADIUS)
        loft()
        if magnet_holes:
            pts = [(x, y) for x in (-MAGNET_OFFSET, MAGNET_OFFSET) for y in (-MAGNET_OFFSET, MAGNET_OFFSET)]
            with Locations(*pts):
                Cylinder(MAGNET_HOLE_DIA / 2, MAGNET_HOLE_DEPTH, align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
    return cell.part


def gridfinity_bin(grid_x=1, grid_y=1, height_u=3, wall=1.2, floor_z=UNIT_HEIGHT,
                   magnet_holes=True, hollow=True):
    """A printable bin: feet + body as ONE solid, optional open cavity.

    floor_z: height of the inner floor (default 7 mm = top of the first unit).
    """
    total = height_u * UNIT_HEIGHT
    if total <= floor_z:
        raise ValueError("height_u too small for the floor")
    bx = grid_x * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE
    by = grid_y * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE
    foot = _foot(magnet_holes)
    x0 = -(grid_x - 1) * GRIDFINITY_PITCH / 2
    y0 = -(grid_y - 1) * GRIDFINITY_PITCH / 2
    part = None
    for ix in range(grid_x):
        for iy in range(grid_y):
            f = foot.moved(_pos(x0 + ix * GRIDFINITY_PITCH, y0 + iy * GRIDFINITY_PITCH, 0))
            part = f if part is None else part + f
    with BuildPart() as body:
        with BuildSketch(Plane.XY.offset(BASE_HEIGHT - 0.01)):  # slight overlap fuses feet + body
            RectangleRounded(bx, by, radius=GRIDFINITY_CORNER_RADIUS)
        extrude(amount=total - BASE_HEIGHT + 0.01)
        if hollow:
            with BuildSketch(Plane.XY.offset(floor_z)):
                RectangleRounded(bx - 2 * wall, by - 2 * wall, radius=max(GRIDFINITY_CORNER_RADIUS - wall, 0.5))
            extrude(amount=total, mode=Mode.SUBTRACT)
    return (part + body.part).clean()


def gridfinity_base(grid_x=1, grid_y=1, height_u=2, magnet_holes=True):
    """Back-compat: solid (not hollow) bin block."""
    return gridfinity_bin(grid_x, grid_y, height_u, magnet_holes=magnet_holes, hollow=False)


def _pos(x, y, z):
    from build123d import Location

    return Location((x, y, z))


__all__ = ["GRIDFINITY_PITCH", "gridfinity_bin", "gridfinity_base"]
