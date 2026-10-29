from build123d import (
    BuildSketch,
    BuildPart,
    Circle,
    Polygon,
    Box,
    Locations,
    Plane,
    extrude,
)

def teardrop_hole(radius=2.5, length=20.0, axis="X"):
    plane = Plane.YZ if axis == "X" else Plane.XZ
    apex_z = radius * 1.41421356
    tangent = radius * 0.70710678

    with BuildSketch(plane) as s:
        Circle(radius=radius)
        Polygon([(0, apex_z), (-tangent, tangent), (tangent, tangent)])

    with BuildPart() as p:
        extrude(s.sketch, amount=length, both=True)

    return p.part

def ventilation_slots(
    slot_width=2.0,
    slot_length=15.0,
    pitch=4.0,
    count=5,
    thickness=4.0,
):
    with BuildPart() as vents:
        total_span = (count - 1) * pitch
        for i in range(count):
            offset_y = -total_span / 2.0 + i * pitch
            with Locations((0, offset_y, 0)):
                Box(slot_length, slot_width, thickness + 2.0)

    return vents.part
