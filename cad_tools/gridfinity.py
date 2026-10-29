from build123d import (
    BuildPart,
    BuildSketch,
    Plane,
    RectangleRounded,
    Cylinder,
    Locations,
    loft,
    extrude,
    Mode,
)

GRIDFINITY_PITCH = 42.0
GRIDFINITY_TOLERANCE = 0.5
GRIDFINITY_CORNER_RADIUS = 3.75
MAGNET_HOLE_DIA = 6.5
MAGNET_HOLE_DEPTH = 2.4
MAGNET_OFFSET = 13.0

def gridfinity_cell_profile(magnet_holes=True):
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
        with BuildSketch(Plane.XY.offset(4.75)):
            RectangleRounded(41.5, 41.5, radius=GRIDFINITY_CORNER_RADIUS)
        loft()

        if magnet_holes:
            mag_radius = MAGNET_HOLE_DIA / 2.0
            mag_z = MAGNET_HOLE_DEPTH / 2.0
            for mx in (-MAGNET_OFFSET, MAGNET_OFFSET):
                for my in (-MAGNET_OFFSET, MAGNET_OFFSET):
                    with Locations((mx, my, mag_z)):
                        Cylinder(radius=mag_radius, height=MAGNET_HOLE_DEPTH + 0.1, mode=Mode.SUBTRACT)

    return cell.part

def gridfinity_base(grid_x=1, grid_y=1, height_u=2, magnet_holes=True):
    unit_height = 7.0
    total_height = height_u * unit_height
    upper_height = total_height - 4.75

    cells = []
    start_x = -(grid_x - 1) * GRIDFINITY_PITCH / 2.0
    start_y = -(grid_y - 1) * GRIDFINITY_PITCH / 2.0

    with BuildPart() as bin_solid:
        for ix in range(grid_x):
            for iy in range(grid_y):
                cx = start_x + ix * GRIDFINITY_PITCH
                cy = start_y + iy * GRIDFINITY_PITCH
                with Locations((cx, cy, 0)):
                    c = gridfinity_cell_profile(magnet_holes=magnet_holes)
                    bin_solid.part = bin_solid.part + c if bin_solid.part else c

        body_x = grid_x * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE
        body_y = grid_y * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE
        with Locations((0, 0, 4.75)):
            with BuildSketch(Plane.XY.offset(4.75)):
                RectangleRounded(body_x, body_y, radius=GRIDFINITY_CORNER_RADIUS)
            extrude(amount=upper_height)

    return bin_solid.part
