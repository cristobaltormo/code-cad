"""FDM printability analysis of a part *in its print orientation* (Z up, bed at min Z).

Produces numbers and findings for the print-review agent:
  overhangs beyond the limit angle, bridges and their spans, bed contact,
  bottom (elephant's-foot) chamfer, thin walls, tiny holes, round horizontal
  holes that should be teardrops, bed fit and tip-over risk.
Severity: "fail" blocks release, "warn" must be shown to the user, "info" is FYI.
"""

from __future__ import annotations

import math

import numpy as np

from cad_tools import measure
from cad_tools.meshcheck import read_stl


def _weld(tris, tol=1e-4):
    flat = tris.reshape(-1, 3)
    _, inv = np.unique(np.round(flat / tol).astype(np.int64), axis=0, return_inverse=True)
    return inv.reshape(-1, 3)


def _regions(faces_idx, mask):
    """Connected components (sharing a vertex) of the masked triangles."""
    sel = np.nonzero(mask)[0]
    if len(sel) == 0:
        return []
    parent = {int(i): int(i) for i in sel}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    by_vertex: dict[int, int] = {}
    for t in sel:
        for v in faces_idx[t]:
            v = int(v)
            if v in by_vertex:
                ra, rb = find(int(t)), find(by_vertex[v])
                if ra != rb:
                    parent[ra] = rb
            else:
                by_vertex[v] = int(t)
    groups: dict[int, list[int]] = {}
    for t in sel:
        groups.setdefault(find(int(t)), []).append(int(t))
    return list(groups.values())


def analyze(step_path, stl_path, printer=None, nozzle=0.4, overhang_limit_deg=45.0,
            max_bridge=15.0, min_wall=None):
    min_wall = min_wall if min_wall is not None else 2 * nozzle
    tris = read_stl(stl_path)
    faces_idx = _weld(tris)
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cr = np.cross(b - a, c - a)
    area = 0.5 * np.linalg.norm(cr, axis=1)
    n = cr / np.maximum(np.linalg.norm(cr, axis=1)[:, None], 1e-15)
    zmin = float(tris[:, :, 2].min())
    zmax = float(tris[:, :, 2].max())
    tri_zmin = tris[:, :, 2].min(axis=1)
    tri_zmax = tris[:, :, 2].max(axis=1)
    on_bed = (tri_zmax - zmin) < 0.02

    findings, metrics = [], {}

    # bed contact
    contact = on_bed & (n[:, 2] < -0.999)
    contact_area = float(area[contact].sum())
    xy = tris[:, :, :2].reshape(-1, 2)
    fp = (xy.max(0) - xy.min(0))
    metrics["bed_contact_mm2"] = round(contact_area, 1)
    metrics["footprint_xy"] = [round(float(v), 2) for v in fp]
    metrics["height"] = round(zmax - zmin, 2)
    if contact_area < 1e-3:
        findings.append({"severity": "fail", "check": "bed_contact",
                         "message": "No flat face on the bed. Re-orient so a flat face is at min Z."})
    elif contact_area < 50:
        findings.append({"severity": "warn", "check": "bed_contact",
                         "message": f"Small bed contact ({contact_area:.0f} mm²): adhesion risk, consider brim."})
    h, base = zmax - zmin, max(min(fp), 1e-6)
    if h / base > 3 and contact_area < 0.3 * fp[0] * fp[1]:
        findings.append({"severity": "warn", "check": "tip_over",
                         "message": f"Tall/narrow part (height/base = {h/base:.1f}); risk of toppling or wobble. Brim or re-orient."})

    # overhangs (angle measured from vertical; 90 deg = flat ceiling)
    # n_z threshold; +1 deg margin so an exact 45 deg chamfer is not flagged
    lim = math.sin(math.radians(overhang_limit_deg + 1.0))
    over = (n[:, 2] < -lim) & ~on_bed
    over_area = float(area[over].sum())
    metrics["overhang_area_mm2"] = round(over_area, 1)
    regions = []
    for grp in _regions(faces_idx, over):
        g = np.array(grp)
        ga = float(area[g].sum())
        if ga < 1.0:
            continue
        pts = tris[g].reshape(-1, 3)
        lo, hi = pts.min(0), pts.max(0)
        flat = bool(np.mean(n[g, 2]) < -0.98)
        # span estimate: min(short bbox side, 4*A/P) - robust for strips and rings
        e = np.sort(np.concatenate([faces_idx[g][:, [0, 1]], faces_idx[g][:, [1, 2]],
                                    faces_idx[g][:, [2, 0]]]), axis=1)
        uniq, cnt = np.unique(e, axis=0, return_counts=True)
        flatv = tris.reshape(-1, 3)
        vpos = np.zeros((faces_idx.max() + 1, 3))
        vpos[faces_idx.reshape(-1)] = flatv
        bnd = uniq[cnt == 1]
        perim = float(np.linalg.norm(vpos[bnd[:, 0]] - vpos[bnd[:, 1]], axis=1).sum()) if len(bnd) else 0.0
        span = float(min(hi[0] - lo[0], hi[1] - lo[1]))
        if perim > 0:
            span = min(span, 4 * ga / perim)
        regions.append({"area_mm2": round(ga, 1), "z": round(float(lo[2]), 2),
                        "bbox_min": lo.round(2).tolist(), "bbox_max": hi.round(2).tolist(),
                        "flat_bridge": flat, "bridge_span_est": round(span, 2) if flat else None})
    regions.sort(key=lambda r: -r["area_mm2"])
    metrics["overhang_regions"] = regions[:15]
    for r in regions:
        if r["flat_bridge"]:
            if r["bridge_span_est"] > max_bridge:
                findings.append({"severity": "fail", "check": "bridge",
                                 "message": f"Flat ceiling at z={r['z']} spans ~{r['bridge_span_est']} mm (> {max_bridge}); needs support or redesign.",
                                 "where": [r["bbox_min"], r["bbox_max"]]})
            elif r["area_mm2"] > 4:
                findings.append({"severity": "info", "check": "bridge",
                                 "message": f"Bridge at z={r['z']} span ~{r['bridge_span_est']} mm (ok if clean bridging).",
                                 "where": [r["bbox_min"], r["bbox_max"]]})
        elif r["area_mm2"] > 5:
            findings.append({"severity": "warn", "check": "overhang",
                             "message": f"Overhang steeper than {overhang_limit_deg}° at z={r['z']} ({r['area_mm2']} mm²).",
                             "where": [r["bbox_min"], r["bbox_max"]]})

    # elephant's foot chamfer near the bed
    chamfer = (n[:, 2] < -0.6) & (n[:, 2] > -0.8) & (tri_zmin - zmin < 0.05) & (tri_zmax - zmin < 1.6)
    metrics["bottom_chamfer_area_mm2"] = round(float(area[chamfer].sum()), 2)
    if area[chamfer].sum() < 0.5:
        findings.append({"severity": "warn", "check": "elephant_foot",
                         "message": "No 45° chamfer detected on bed edges (0.6-1.0 mm recommended)."})

    # BREP-based checks
    shape = measure.load(step_path)
    walls = measure.min_wall(shape, threshold=min_wall)
    metrics["walls"] = walls
    if walls.get("samples") and walls["min_thickness"] < min_wall:
        sev = "fail" if walls["min_thickness"] < nozzle * 1.2 else "warn"
        findings.append({"severity": sev, "check": "thin_wall",
                         "message": f"Wall/feature {walls['min_thickness']} mm thick (< {min_wall} = 2 lines).",
                         "where": walls["thinnest_points"][:3]})
    hl = measure.holes(shape)
    for hole in hl:
        if hole["kind"] != "hole" or hole["sweep_deg"] < 300:
            continue
        ax = hole["axis"]
        vertical = abs(ax[2]) > 0.99
        horizontal = abs(ax[2]) < 0.02
        if vertical and hole["diameter"] < 1.5:
            findings.append({"severity": "warn", "check": "tiny_hole",
                             "message": f"Vertical hole Ø{hole['diameter']} is below ~1.5 mm; will print closed/undersized.",
                             "where": [hole["axis_start"]]})
        if horizontal and hole["diameter"] > 4.0:
            findings.append({"severity": "warn", "check": "teardrop",
                             "message": f"Round horizontal hole Ø{hole['diameter']}: ceiling will droop; use a teardrop profile.",
                             "where": [hole["axis_start"], hole["axis_end"]]})

    # bed fit
    if printer:
        vol = printer["build_volume"]
        size = sorted([fp[0], fp[1]])
        fits = (fp[0] <= vol[0] and fp[1] <= vol[1]) or (fp[1] <= vol[0] and fp[0] <= vol[1])
        fits = fits and (zmax - zmin) <= vol[2]
        metrics["printer"] = {"name": printer.get("name"), "build_volume": vol, "fits": bool(fits)}
        if not fits:
            findings.append({"severity": "fail", "check": "bed_fit",
                             "message": f"Part {fp[0]:.1f} x {fp[1]:.1f} x {zmax - zmin:.1f} does not fit {printer.get('name')} {vol}. Split the part or rotate."})
        del size

    sev = {f["severity"] for f in findings}
    status = "FAIL" if "fail" in sev else "WARN" if "warn" in sev else "PASS"
    return {"status": status, "metrics": metrics, "findings": findings,
            "settings": {"nozzle": nozzle, "overhang_limit_deg": overhang_limit_deg,
                         "max_bridge": max_bridge, "min_wall": min_wall}}
