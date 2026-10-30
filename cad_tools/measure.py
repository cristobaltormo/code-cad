"""Virtual caliper: measurements taken from exported geometry (STEP/BREP).

Everything here works on a finished shape, never on the design script, so an
independent verifier can measure a part without trusting the designer's numbers.

CLI (via `python -m cad_tools measure ...`):
    bbox      <file>
    holes     <file> [--min-d D] [--max-d D]
    ray       <file> --from X,Y,Z --dir DX,DY,DZ
    section   <file> --plane XY|XZ|YZ --at OFFSET [--png out.png]
    clearance <file> <other.step>
    walls     <file> [--samples N]
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from build123d import Axis, GeomType, Plane, Vector, import_step, section
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepTools import BRepTools
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector

def _t(v):
    return (v.X, v.Y, v.Z)


_PLANES = {"XY": Plane.XY, "XZ": Plane.XZ, "YZ": Plane.YZ}


def load(path):
    """Load a STEP file as a build123d shape."""
    path = Path(path)
    if path.suffix.lower() not in (".step", ".stp"):
        raise ValueError(f"measure needs a STEP file, got {path.name}")
    return import_step(str(path))


def bbox(shape) -> dict:
    bb = shape.bounding_box()
    return {
        "min": [round(bb.min.X, 4), round(bb.min.Y, 4), round(bb.min.Z, 4)],
        "max": [round(bb.max.X, 4), round(bb.max.Y, 4), round(bb.max.Z, 4)],
        "size": [round(bb.size.X, 4), round(bb.size.Y, 4), round(bb.size.Z, 4)],
        "solids": len(shape.solids()),
        "volume_mm3": round(shape.volume, 3),
    }


# ---------------------------------------------------------------- ray caliper

def ray(shape, origin, direction) -> dict:
    """Cast an infinite line and report where it crosses the surface.

    Returns hit points (as distances along `direction` from `origin`) plus the
    derived `material` segments (wall thicknesses) and `gaps` between them
    (cavities, slots, hole diameters). This is the general-purpose caliper.
    """
    d = Vector(*direction).normalized()
    it = IntCurvesFace_ShapeIntersector()
    it.Load(shape.wrapped, 1e-7)
    it.Perform(gp_Lin(gp_Pnt(*origin), gp_Dir(d.X, d.Y, d.Z)), -1e7, 1e7)
    ts = sorted(it.WParameter(i) for i in range(1, it.NbPnt() + 1))
    # merge hits that coincide (ray grazing an edge shared by two faces)
    merged = []
    for t in ts:
        if not merged or abs(t - merged[-1]) > 1e-5:
            merged.append(t)
    o = Vector(*origin)
    material, gaps = [], []
    # classify each interval by testing its midpoint
    for t0, t1 in zip(merged, merged[1:]):
        mid = o + d * ((t0 + t1) / 2)
        inside = shape.is_inside(mid)
        seg = {"from": round(t0, 4), "to": round(t1, 4), "length": round(t1 - t0, 4)}
        (material if inside else gaps).append(seg)
    return {
        "origin": list(origin),
        "direction": [round(d.X, 6), round(d.Y, 6), round(d.Z, 6)],
        "hits": [round(t, 4) for t in merged],
        "hit_points": [[round(c, 4) for c in _t(o + d * t)] for t in merged],
        "material": material,
        "gaps": gaps,
    }


# ---------------------------------------------------------------- holes / bosses

def holes(shape, min_d: float = 0.0, max_d: float = 1e9) -> list[dict]:
    """Find cylindrical features. Each entry is one coaxial cylinder of one radius.

    kind = "hole" (concave, material outside) or "boss" (convex, e.g. a pin or
    standoff outside). `sweep_deg` < 360 means a partial cylinder (fillet, slot
    end, cut-away hole). `axis_start`/`axis_end` are the feature's extent along
    its axis, given as the 3D points where it starts and ends.
    """
    groups: dict[tuple, dict] = {}
    for face in shape.faces():
        if face.geom_type != GeomType.CYLINDER:
            continue
        cyl = BRepAdaptor_Surface(face.wrapped).Cylinder()
        r = cyl.Radius()
        if not (min_d <= 2 * r <= max_d):
            continue
        a1 = cyl.Axis()
        loc, dr = a1.Location(), a1.Direction()
        ax_pos = Vector(loc.X(), loc.Y(), loc.Z())
        dvec = Vector(dr.X(), dr.Y(), dr.Z()).normalized()
        # canonical direction sign so +Z and -Z cylinders group together
        comps = (dvec.X, dvec.Y, dvec.Z)
        first = next(c for c in comps if abs(c) > 1e-9)
        if first < 0:
            dvec = -dvec
        p0 = ax_pos
        foot = p0 - dvec * p0.dot(dvec)  # axis point closest to origin
        umin, umax, _, _ = BRepTools.UVBounds_s(face.wrapped)
        sweep = math.degrees(umax - umin)
        center = face.center()
        radial = center - (p0 + dvec * (center - p0).dot(dvec))
        kind = "hole" if face.normal_at(center).dot(radial) < 0 else "boss"
        ts = [(Vector(v) - foot).dot(dvec) for v in face.vertices()]
        for e in face.edges():
            ts += [(e.position_at(u) - foot).dot(dvec) for u in (0, 0.5, 1)]
        key = (
            round(dvec.X, 3), round(dvec.Y, 3), round(dvec.Z, 3),
            round(foot.X, 2), round(foot.Y, 2), round(foot.Z, 2),
            round(r, 3), kind,
        )
        g = groups.setdefault(key, {"r": r, "dir": dvec, "foot": foot, "kind": kind,
                                    "sweep": 0.0, "tmin": 1e18, "tmax": -1e18})
        g["sweep"] += sweep
        g["tmin"] = min(g["tmin"], min(ts))
        g["tmax"] = max(g["tmax"], max(ts))

    out = []
    for g in groups.values():
        d, f = g["dir"], g["foot"]
        start, end = f + d * g["tmin"], f + d * g["tmax"]
        out.append({
            "kind": g["kind"],
            "diameter": round(2 * g["r"], 4),
            "axis": [round(d.X, 4), round(d.Y, 4), round(d.Z, 4)],
            "axis_start": [round(c, 4) for c in _t(start)],
            "axis_end": [round(c, 4) for c in _t(end)],
            "length": round(g["tmax"] - g["tmin"], 4),
            "sweep_deg": round(min(g["sweep"], 360.0), 1),
        })
    out.sort(key=lambda h: (h["kind"], h["diameter"], h["axis_start"]))
    return out


# ---------------------------------------------------------------- sections

def section_loops(shape, plane: str = "XY", at: float = 0.0) -> dict:
    """Cut the shape with a plane and describe the resulting profile.

    Each face of the section is reported with its area, outer loop bounding box
    and the bounding boxes of its inner loops (holes / cavities in the cut).
    Coordinates are global.
    """
    pl = _PLANES[plane.upper()].offset(at)
    sk = section(shape, section_by=pl)
    faces = []
    for f in sk.faces():
        outer = f.outer_wire()
        inner = f.inner_wires()

        def wb(w):
            b = w.bounding_box()
            return {"min": [round(b.min.X, 3), round(b.min.Y, 3), round(b.min.Z, 3)],
                    "max": [round(b.max.X, 3), round(b.max.Y, 3), round(b.max.Z, 3)],
                    "size": [round(b.size.X, 3), round(b.size.Y, 3), round(b.size.Z, 3)]}

        faces.append({"area_mm2": round(f.area, 3), "outer": wb(outer),
                      "inner_loops": [wb(w) for w in inner]})
    return {"plane": plane.upper(), "offset": at, "faces": faces, "_sketch": sk}


# ---------------------------------------------------------------- clearance

def clearance(part, other) -> dict:
    """Minimum gap and interference volume between two shapes (e.g. part vs mate)."""
    inter = part.intersect(other)
    vol = 0.0
    if inter is not None:
        try:
            vol = sum(s.volume for s in inter.solids())
        except Exception:
            vol = getattr(inter, "volume", 0.0) or 0.0
    dist = 0.0 if vol > 1e-6 else part.distance_to(other)
    return {"min_distance": round(dist, 4), "interference_mm3": round(vol, 4),
            "touching_or_overlapping": vol > 1e-6 or dist < 1e-6}


# ---------------------------------------------------------------- wall thickness

def wall_samples(shape, samples_per_face: int = 6, max_faces: int = 4000) -> np.ndarray:
    """Sample local material thickness: from points on each face, cast a ray
    inward along -normal and measure to the next surface hit.

    Returns an (N, 4) array of [x, y, z, thickness]. Thin regions show up as
    small thickness values. Cheap, approximate, BREP-exact per sample.
    """
    it = IntCurvesFace_ShapeIntersector()
    it.Load(shape.wrapped, 1e-7)
    rows = []
    rng = np.random.default_rng(0)
    for face in list(shape.faces())[:max_faces]:
        if face.area < 1e-3:
            continue
        uv = [(0.5, 0.5)] + [tuple(rng.uniform(0.1, 0.9, 2)) for _ in range(samples_per_face - 1)]
        for u, v in uv:
            try:
                p = face.position_at(u, v)
                n = face.normal_at(p)
            except Exception:
                continue
            if not face.is_inside(p):
                continue
            start = p - n * 1e-4
            it.Perform(gp_Lin(gp_Pnt(*_t(start)), gp_Dir(-n.X, -n.Y, -n.Z)), 0.0, 1e6)
            ts = [it.WParameter(i) for i in range(1, it.NbPnt() + 1)]
            ts = [t for t in ts if t > 1e-3]
            if ts:
                rows.append([p.X, p.Y, p.Z, min(ts) + 1e-4])
    return np.asarray(rows) if rows else np.zeros((0, 4))


def min_wall(shape, threshold: float | None = None) -> dict:
    s = wall_samples(shape)
    if len(s) == 0:
        return {"samples": 0}
    order = np.argsort(s[:, 3])
    res = {"samples": int(len(s)), "min_thickness": round(float(s[order[0], 3]), 4),
           "p05_thickness": round(float(np.percentile(s[:, 3], 5)), 4),
           "thinnest_points": [[round(float(c), 3) for c in s[i]] for i in order[:5]]}
    if threshold is not None:
        res["below_threshold"] = int(np.sum(s[:, 3] < threshold))
    return res
