"""Printable geometry features (cutters to subtract unless noted)."""

from __future__ import annotations

import math
import sys

from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Circle, Locations, Plane, Polygon,
                       SlotOverall, extrude)


def chamfer_bottom(part, size=0.8, z=None):
    """45 deg elephant's-foot chamfer on every edge lying in the bed plane.

    Raises with a clear message if OCCT cannot chamfer (typically a bed edge
    meets a feature narrower than `size`): reduce `size` or chamfer selectively.
    """
    bb = part.bounding_box()
    z = bb.min.Z if z is None else z
    edges = part.edges().filter_by(lambda e: abs(e.center().Z - z) < 1e-4
                                   and e.bounding_box().size.Z < 1e-4)
    if not edges:
        return part
    try:
        return part.chamfer(size, None, list(edges))
    except Exception:
        pass
    # Fall back edge by edge (acute corners / tiny edges cannot take the chamfer).
    done, skipped = part, 0
    for e in sorted(edges, key=lambda e: -e.length):
        match = [c for c in done.edges() if (c.center() - e.center()).length < 1e-4
                 and abs(c.length - e.length) < 1e-4]
        try:
            done = done.chamfer(size, None, match[:1]) if match else done
            skipped += 0 if match else 1
        except Exception:
            skipped += 1
    if skipped == len(edges):
        raise ValueError(f"chamfer_bottom({size}) failed on all {len(edges)} bed edges; use a smaller size")
    if skipped:
        print(f"chamfer_bottom: {skipped}/{len(edges)} bed edges could not take a {size} mm chamfer "
              "(acute corners / short edges) and were left sharp", file=sys.stderr)
    return done


def teardrop_hole(radius=2.5, length=20.0, axis="X", center=(0, 0, 0), truncate=None):
    """Horizontal hole with a 45 deg roof so it prints without support.

    Total length = `length` (centred on `center`). Apex points to +Z (print up).
    `truncate` (e.g. 1.05*radius) flattens the apex tip for a cleaner look.
    """
    plane = Plane.YZ if axis.upper() == "X" else Plane.XZ
    apex = radius * math.sqrt(2)
    t = radius / math.sqrt(2)
    with BuildPart() as p:
        with BuildSketch(plane):
            Circle(radius)
            Polygon((0, apex), (-t, t), (t, t), align=None)
        extrude(amount=length / 2, both=True)
    part = p.part
    if truncate:
        part = part - Box(length * 4, length * 4, apex * 2,
                          align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(_loc((0, 0, truncate)))
    return part.moved(_loc(center))


def _loc(xyz):
    from build123d import Location

    return Location(tuple(xyz))


def slot_array(slot_width=2.0, slot_length=15.0, pitch=4.0, count=5, depth=10.0):
    """Rounded slot cutters along Y, centred, spanning Z in [-depth/2, depth/2].

    Make `depth` larger than the wall you cut through so the slots go THROUGH.
    """
    with BuildPart() as p:
        with BuildSketch(Plane.XY.offset(-depth / 2)):
            span = (count - 1) * pitch
            with Locations(*[(0, -span / 2 + i * pitch) for i in range(count)]):
                SlotOverall(slot_length, slot_width)
        extrude(amount=depth)
    return p.part


def ventilation_slots(slot_width=2.0, slot_length=15.0, pitch=4.0, count=5, thickness=4.0):
    """Back-compat wrapper: through-slots for a plate of `thickness` centred on Z=0."""
    return slot_array(slot_width, slot_length, pitch, count, depth=thickness * 3)


def edge_select_vertical(part):
    return part.edges().filter_by(Axis.Z)
