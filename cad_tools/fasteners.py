"""Fastener features for 3D-printed parts.

All dimensions verified 2026-10 against ISO tables (fasteners.eu, fasten.it) and
the ruthex / CNC Kitchen insert size tables. Every cutter returned here is a
solid to SUBTRACT; bosses are solids to ADD. Cutters are built along +Z with
the mouth at Z = 0 going down into the part (−Z) unless noted, so place them
with `Pos(x, y, top_z) * cutter`.
"""

from __future__ import annotations

import math

from build123d import Align, BuildPart, BuildSketch, Cone, Cylinder, Plane, Pos, RegularPolygon, extrude

# ISO 4762 socket head cap screw: dk head dia max, k head height max, s hex key
SHCS = {
    "M2": {"dk": 3.8, "k": 2.0, "s": 1.5}, "M2.5": {"dk": 4.5, "k": 2.5, "s": 2.0},
    "M3": {"dk": 5.5, "k": 3.0, "s": 2.5}, "M4": {"dk": 7.0, "k": 4.0, "s": 3.0},
    "M5": {"dk": 8.5, "k": 5.0, "s": 4.0}, "M6": {"dk": 10.0, "k": 6.0, "s": 5.0},
    "M8": {"dk": 13.0, "k": 8.0, "s": 6.0},
}
# ISO 7380-1 button head
BUTTON = {"M3": {"dk": 5.7, "k": 1.65}, "M4": {"dk": 7.6, "k": 2.2}, "M5": {"dk": 9.5, "k": 2.75},
          "M6": {"dk": 10.5, "k": 3.3}, "M8": {"dk": 14.0, "k": 4.4}}
# ISO 10642 countersunk 90 deg (dk = theoretical max)
COUNTERSUNK = {"M3": {"dk": 6.72, "k": 1.86}, "M4": {"dk": 8.96, "k": 2.48}, "M5": {"dk": 11.2, "k": 3.1},
               "M6": {"dk": 13.44, "k": 3.72}, "M8": {"dk": 17.92, "k": 4.96}}
# ISO 4032 hex nut: s across flats, m height max; DIN 934 heights differ for M5 (4.0) / M8 (6.5)
HEX_NUT = {"M2": {"s": 4.0, "m": 1.6}, "M2.5": {"s": 5.0, "m": 2.0}, "M3": {"s": 5.5, "m": 2.4},
           "M4": {"s": 7.0, "m": 3.2}, "M5": {"s": 8.0, "m": 4.7}, "M6": {"s": 10.0, "m": 5.2},
           "M8": {"s": 13.0, "m": 6.8}}
NYLOC_HEIGHT = {"M3": 4.0, "M4": 5.0, "M5": 5.0, "M6": 6.0, "M8": 8.0}  # DIN 985
# ISO 7089 washer d1/d2/h
WASHER = {"M2": (2.2, 5.0, 0.3), "M2.5": (2.7, 6.0, 0.5), "M3": (3.2, 7.0, 0.5), "M4": (4.3, 9.0, 0.8),
          "M5": (5.3, 10.0, 1.0), "M6": (6.4, 12.0, 1.6), "M8": (8.4, 16.0, 1.6)}
# ISO 273 clearance holes (fine, medium, coarse) - metal values; see clearance_dia()
ISO273 = {"M2": (2.2, 2.4, 2.6), "M2.5": (2.7, 2.9, 3.1), "M3": (3.2, 3.4, 3.6), "M4": (4.3, 4.5, 4.8),
          "M5": (5.3, 5.5, 5.8), "M6": (6.4, 6.6, 7.0), "M8": (8.4, 9.0, 10.0)}
TAP_DRILL = {"M2": 1.6, "M2.5": 2.05, "M3": 2.5, "M4": 3.3, "M5": 4.2, "M6": 5.0, "M8": 6.8}

# Heat-set inserts: L length, od knurl, hole = vendor hole dia (use AS IS, no extra
# compensation), wall = vendor minimum wall around the hole. Min hole depth = L + 1.
HEAT_SET = {
    "ruthex": {
        "M2": {"L": 4.0, "od": 3.6, "hole": 3.2, "wall": 1.3},
        "M2.5": {"L": 5.7, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M3": {"L": 5.7, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M3_short": {"L": 4.0, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M4": {"L": 8.1, "od": 6.3, "hole": 5.6, "wall": 2.1},
        "M5": {"L": 9.5, "od": 7.0, "hole": 6.4, "wall": 2.6},
        "M6": {"L": 12.7, "od": 8.7, "hole": 8.0, "wall": 3.3},
    },
    "cnc_kitchen": {
        "M2": {"L": 3.0, "od": 3.6, "hole": 3.2, "wall": 1.3},
        "M2.5": {"L": 4.0, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M3": {"L": 5.7, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M3_short": {"L": 3.0, "od": 4.6, "hole": 4.0, "wall": 1.6},
        "M4": {"L": 8.1, "od": 6.3, "hole": 5.7, "wall": 2.1},
        "M5": {"L": 9.5, "od": 7.0, "hole": 6.5, "wall": 2.6},
        "M6": {"L": 12.7, "od": 8.7, "hole": 8.1, "wall": 3.3},
    },
    "voron": {"M3": {"L": 4.0, "od": 5.0, "hole": 4.4, "wall": 1.6}},  # M3x5x4, hole per ruthex/CNCK
}

# Back-compat aliases used by older scripts
HEAT_SET_SPECS = {k: {"hole_dia": v["hole"], "hole_depth": v["L"] + 1.0, "boss_od": v["hole"] + 2 * v["wall"],
                      "insert_od": v["od"]} for k, v in HEAT_SET["ruthex"].items() if "_" not in k}
SCREW_SPECS = {k: {"clearance_dia": ISO273[k][1], "socket_head_dia": SHCS[k]["dk"] + 0.6,
                   "socket_head_depth": SHCS[k]["k"] + 0.3} for k in SHCS}


def clearance_dia(size="M3", fit="medium", printed=True):
    """Through-hole diameter. FDM vertical holes print ~0.2 mm small, so +0.2 when printed."""
    d = ISO273[size][{"fine": 0, "medium": 1, "coarse": 2}[fit]]
    return round(d + (0.2 if printed else 0.0), 3)


def insert_spec(size="M3", brand="ruthex"):
    return dict(HEAT_SET[brand][size])


def _cyl_down(r, depth, z_top=0.0):
    return Pos(0, 0, z_top) * Cylinder(r, depth, align=(Align.CENTER, Align.CENTER, Align.MAX))


def heat_set_hole(size="M3", brand="ruthex", extra_depth=1.0, through=False, part_depth=None):
    """Cutter for a heat-set insert pocket, mouth at Z=0, going down.

    Depth = insert length + extra_depth (vendors: >= L + 1 mm to catch melt).
    Includes a 0.3 mm lead-in counterbore at insert OD to start it square.
    """
    s = HEAT_SET[brand][size]
    depth = part_depth + 1 if through else s["L"] + extra_depth
    c = _cyl_down(s["hole"] / 2, depth)
    c += _cyl_down(s["od"] / 2 + 0.05, 0.3)
    return c


def heat_set_boss(size="M3", total_height=8.0, brand="ruthex", od=None, wall_override=None):
    """Standoff boss sitting on Z=0 with an insert pocket from its top.

    Raises if the boss is too short for the insert: the old helper silently
    produced pockets shorter than the insert.
    """
    s = HEAT_SET[brand][size]
    need = s["L"] + 1.0
    if total_height < need:
        raise ValueError(f"{size} {brand} insert needs a pocket {need} mm deep; boss is only "
                         f"{total_height} mm. Make the boss taller or let the pocket continue into the floor "
                         f"(use heat_set_hole() on the combined part).")
    od = od or wall_override or (s["hole"] + 2 * s["wall"] + 0.4)
    boss = Cylinder(od / 2, total_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return boss - Pos(0, 0, total_height) * heat_set_hole(size, brand)


def counterbore(size="M3", depth=None, head="socket", through=20.0, clearance=0.4):
    """Cutter: clearance hole + head pocket, mouth at Z=0 going down.

    depth defaults to head height + 0.3 so the head sits just below flush.
    """
    hd = (SHCS if head == "socket" else BUTTON)[size]
    depth = hd["k"] + 0.3 if depth is None else depth
    c = _cyl_down(clearance_dia(size) / 2, through)
    c += _cyl_down(hd["dk"] / 2 + clearance, depth)
    return c


def countersink(size="M3", through=20.0, recess=0.2, hole_d=None):
    """Cutter for an ISO 10642 90 deg countersunk screw, mouth at Z=0 going down.

    hole_d overrides the shank hole (e.g. 4.4 for a 4 mm wood screw).
    """
    hd = COUNTERSUNK[size]
    r_top = hd["dk"] / 2 + 0.2
    r_bot = (hole_d or clearance_dia(size)) / 2
    cone_h = r_top - r_bot  # 90 deg included angle
    c = _cyl_down(r_bot, through)
    c += Pos(0, 0, -recess) * Cone(r_bot, r_top, cone_h, align=(Align.CENTER, Align.CENTER, Align.MAX))
    c += _cyl_down(r_top, recess + 0.01)
    return c


def hex_nut_pocket(size="M3", tolerance=0.3, depth=None, nyloc=False):
    """Hexagonal nut trap, mouth at Z=0 going down. Flats along X."""
    s = HEX_NUT[size]
    depth = depth or ((NYLOC_HEIGHT[size] if nyloc else s["m"]) + tolerance)
    r = (s["s"] + tolerance) / math.sqrt(3)
    with BuildPart() as p:
        with BuildSketch(Plane.XY):
            RegularPolygon(r, 6)
        extrude(amount=-depth)
    return p.part


captive_hex_pocket = hex_nut_pocket  # back-compat name


def screw_counterbore(size="M3", part_thickness=5.0):
    """Back-compat: centred counterbore cutter for a plate centred on Z=0."""
    return Pos(0, 0, part_thickness / 2) * counterbore(size, through=part_thickness + 2)
