from build123d import (
    Cylinder,
    Box,
    RegularPolygon,
    BuildSketch,
    extrude,
    Locations,
    BuildPart,
    Mode,
)

HEAT_SET_SPECS = {
    "M2": {
        "hole_dia": 3.2,
        "hole_depth": 4.0,
        "boss_od": 5.4,
        "insert_od": 3.6,
    },
    "M2.5": {
        "hole_dia": 4.0,
        "hole_depth": 5.7,
        "boss_od": 6.5,
        "insert_od": 4.6,
    },
    "M3": {
        "hole_dia": 4.0,
        "hole_depth": 5.7,
        "boss_od": 7.0,
        "insert_od": 4.6,
    },
    "M4": {
        "hole_dia": 5.6,
        "hole_depth": 8.0,
        "boss_od": 9.0,
        "insert_od": 6.3,
    },
    "M5": {
        "hole_dia": 6.8,
        "hole_depth": 9.5,
        "boss_od": 11.0,
        "insert_od": 7.6,
    },
}

SCREW_SPECS = {
    "M2": {
        "clearance_dia": 2.4,
        "socket_head_dia": 4.2,
        "socket_head_depth": 2.2,
        "countersink_dia": 4.4,
    },
    "M2.5": {
        "clearance_dia": 2.9,
        "socket_head_dia": 5.0,
        "socket_head_depth": 2.7,
        "countersink_dia": 5.5,
    },
    "M3": {
        "clearance_dia": 3.4,
        "socket_head_dia": 6.0,
        "socket_head_depth": 3.3,
        "countersink_dia": 6.6,
    },
    "M4": {
        "clearance_dia": 4.5,
        "socket_head_dia": 7.6,
        "socket_head_depth": 4.3,
        "countersink_dia": 8.8,
    },
    "M5": {
        "clearance_dia": 5.5,
        "socket_head_dia": 9.2,
        "socket_head_depth": 5.3,
        "countersink_dia": 10.8,
    },
}

HEX_NUT_SPECS = {
    "M2": {"width_across_flats": 4.0, "thickness": 1.6},
    "M2.5": {"width_across_flats": 5.0, "thickness": 2.0},
    "M3": {"width_across_flats": 5.5, "thickness": 2.4},
    "M4": {"width_across_flats": 7.0, "thickness": 3.2},
    "M5": {"width_across_flats": 8.0, "thickness": 4.0},
}

def heat_set_boss(size="M3", total_height=8.0, wall_override=None):
    spec = HEAT_SET_SPECS.get(size, HEAT_SET_SPECS["M3"])
    hole_radius = spec["hole_dia"] / 2.0
    hole_depth = min(spec["hole_depth"] + 1.0, total_height - 0.8)
    boss_radius = (wall_override if wall_override else spec["boss_od"]) / 2.0
    hole_z = (total_height - hole_depth) / 2.0
    lead_in_radius = spec["insert_od"] / 2.0
    lead_in_depth = 0.6
    lead_in_z = total_height / 2.0 - lead_in_depth / 2.0

    with BuildPart() as boss:
        Cylinder(radius=boss_radius, height=total_height)
        with Locations((0, 0, hole_z)):
            Cylinder(radius=hole_radius, height=hole_depth + 0.1, mode=Mode.SUBTRACT)
        with Locations((0, 0, lead_in_z)):
            Cylinder(radius=lead_in_radius, height=lead_in_depth + 0.1, mode=Mode.SUBTRACT)

    return boss.part

def screw_counterbore(size="M3", part_thickness=5.0):
    spec = SCREW_SPECS.get(size, SCREW_SPECS["M3"])
    clearance_radius = spec["clearance_dia"] / 2.0
    head_radius = spec["socket_head_dia"] / 2.0
    head_depth = spec["socket_head_depth"]
    head_z = (part_thickness - head_depth) / 2.0 + 0.5

    with BuildPart() as cut:
        Cylinder(radius=clearance_radius, height=part_thickness + 2.0)
        with Locations((0, 0, head_z)):
            Cylinder(radius=head_radius, height=head_depth + 1.0)

    return cut.part

def captive_hex_pocket(size="M3", tolerance=0.25):
    spec = HEX_NUT_SPECS.get(size, HEX_NUT_SPECS["M3"])
    nut_radius = (spec["width_across_flats"] + tolerance) / 1.73205
    pocket_depth = spec["thickness"] + tolerance

    with BuildPart() as nut_cut:
        with BuildSketch():
            RegularPolygon(radius=nut_radius, side_count=6)
        extrude(amount=pocket_depth)

    return nut_cut.part
