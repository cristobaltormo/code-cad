from build123d import (
    BuildPart,
    Box,
    Pos,
    fillet,
    chamfer,
    Axis,
)

GRIDFINITY_PITCH = 42.0
GRIDFINITY_TOLERANCE = 0.5
GRIDFINITY_CORNER_RADIUS = 4.0

def gridfinity_base(grid_x=1, grid_y=1, height_u=2):
    unit_height = 7.0
    total_height = height_u * unit_height
    size_x = grid_x * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE
    size_y = grid_y * GRIDFINITY_PITCH - GRIDFINITY_TOLERANCE

    with BuildPart() as base:
        Box(size_x, size_y, total_height)
        vertical_edges = base.edges().filter_by(Axis.Z)
        fillet(vertical_edges, radius=GRIDFINITY_CORNER_RADIUS)
        bottom_edges = base.faces().sort_by(Axis.Z)[0].edges()
        chamfer(bottom_edges, length=0.8)

    return base.part
