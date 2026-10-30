"""Headless drawings an agent can actually *look at* (PNG via the Read tool).

    views sheet   : front / top / right hidden-line projections with overall
                    dimensions + two shaded isometric views (mates overlaid)
    sections sheet: cuts through the part centre on XY, XZ and YZ with a mm grid

Both are written as PNG (for visual verification) and the views sheet also as
SVG (the `<model>_views.svg` deliverable).
"""

from __future__ import annotations

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import LineCollection, PolyCollection  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MplPath  # noqa: E402

from build123d import GeomType, Plane, section  # noqa: E402

PART_RGB = np.array([0.30, 0.55, 0.85])
MATE_RGB = np.array([0.95, 0.55, 0.20])


# ----------------------------------------------------------------- helpers

def _edge_points(edge, n=24):
    if edge.geom_type == GeomType.LINE:
        ts = (0.0, 1.0)
    else:
        ts = np.linspace(0.0, 1.0, n)
    return [(p.X, p.Y) for p in (edge.position_at(t) for t in ts)]


def _hlr(shape, view, bb):
    c = bb.center()
    d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10 + 100
    cfg = {
        "front": ((c.X, c.Y - d, c.Z), (0, 0, 1)),
        "top": ((c.X, c.Y, c.Z + d), (0, 1, 0)),
        "right": ((c.X + d, c.Y, c.Z), (0, 0, 1)),
    }[view]
    vis, hid = shape.project_to_viewport(cfg[0], viewport_up=cfg[1], look_at=(c.X, c.Y, c.Z))
    return [_edge_points(e) for e in vis], [_edge_points(e) for e in hid]


def _dim(ax, p0, p1, offset, text, vertical=False):
    """Simple dimension line with arrows and label."""
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
    if vertical:
        x = offset
        ax.annotate("", xy=(x, p0), xytext=(x, p1), **kw)
        ax.text(x, (p0 + p1) / 2, text, rotation=90, ha="right", va="center",
                fontsize=7, color="#c0392b")
    else:
        y = offset
        ax.annotate("", xy=(p0, y), xytext=(p1, y), **kw)
        ax.text((p0 + p1) / 2, y, text, ha="center", va="top", fontsize=7, color="#c0392b")


def _ortho_panel(ax, shape, view, bb, title):
    vis, hid = _hlr(shape, view, bb)
    ax.add_collection(LineCollection(hid, colors="#9a9a9a", linewidths=0.4, linestyles=(0, (3, 2))))
    ax.add_collection(LineCollection(vis, colors="#111111", linewidths=0.8))
    pts = np.array([p for line in vis + hid for p in line]) if (vis or hid) else np.zeros((1, 2))
    x0, y0 = pts.min(axis=0)
    x1, y1 = pts.max(axis=0)
    w, h = x1 - x0, y1 - y0
    m = max(w, h) * 0.18 + 2
    ax.set_xlim(x0 - m, x1 + m)
    ax.set_ylim(y0 - m, y1 + m)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    labels = {"front": ("X", "Z"), "top": ("X", "Y"), "right": ("Y", "Z")}[view]
    _dim(ax, x0, x1, y0 - m * 0.45, f"{w:.2f} ({labels[0]})")
    _dim(ax, y0, y1, x0 - m * 0.45, f"{h:.2f} ({labels[1]})", vertical=True)
    ax.set_title(title, fontsize=9)


def _mesh(shape, tol, max_edge=None):
    """Tessellate, then split long sliver triangles so depth sorting behaves."""
    verts, tris = shape.tessellate(tol, 0.2)
    v = np.array([(p.X, p.Y, p.Z) for p in verts])
    tri = v[np.array(tris, dtype=int).reshape(-1, 3)]
    if max_edge is None:
        bb = shape.bounding_box()
        max_edge = max(bb.size.X, bb.size.Y, bb.size.Z) / 25
    for _ in range(10):
        e = np.stack([np.linalg.norm(tri[:, (i + 1) % 3] - tri[:, i], axis=1) for i in range(3)], 1)
        longest = e.argmax(axis=1)
        split = e.max(axis=1) > max_edge
        if not split.any() or len(tri) > 400_000:
            break
        keep, s = tri[~split], tri[split]
        k = longest[split]
        a = s[np.arange(len(s)), k]
        b = s[np.arange(len(s)), (k + 1) % 3]
        c = s[np.arange(len(s)), (k + 2) % 3]
        m = (a + b) / 2
        tri = np.concatenate([keep, np.stack([a, m, c], 1), np.stack([m, b, c], 1)])
    flat = tri.reshape(-1, 3)
    return flat, np.arange(len(flat)).reshape(-1, 3)


def _shaded_panel(ax, items, azim_deg, elev_deg, title):
    """Painter's-algorithm shaded orthographic render with back-face culling."""
    az, el = math.radians(azim_deg), math.radians(elev_deg)
    view = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])
    right = np.cross([0, 0, 1], view)
    right /= np.linalg.norm(right)
    up = np.cross(view, right)
    light = view * 0.6 + up * 0.5 + right * 0.3
    light /= np.linalg.norm(light)

    polys, colors, depths = [], [], []
    for v, t, rgb, alpha in items:
        tri = v[t]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1)
        ok = ln > 1e-12
        tri, n = tri[ok], n[ok] / ln[ok, None]
        front = n @ view > 0
        tri, n = tri[front], n[front]
        shade = 0.35 + 0.65 * np.clip(n @ light, 0, 1)
        p2 = np.stack([tri @ right, tri @ up], axis=-1)
        polys.extend(p2)
        colors.extend(np.c_[np.clip(shade[:, None] * rgb, 0, 1), np.full(len(shade), alpha)])
        depths.extend((tri @ view).mean(axis=1))
    if polys:
        order = np.argsort(depths)
        pc = PolyCollection([polys[i] for i in order], facecolors=[colors[i] for i in order],
                            edgecolors="none", antialiased=False, rasterized=True)
        ax.add_collection(pc)
        allp = np.concatenate(polys)
        lo, hi = allp.min(axis=0), allp.max(axis=0)
        m = (hi - lo).max() * 0.08 + 1
        ax.set_xlim(lo[0] - m, hi[0] + m)
        ax.set_ylim(lo[1] - m, hi[1] + m)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    # axis triad
    for vec, lab, col in (((1, 0, 0), "X", "r"), ((0, 1, 0), "Y", "g"), ((0, 0, 1), "Z", "b")):
        vv = np.array(vec, float)
        ax.annotate("", xy=(0.08 + 0.06 * vv @ right, 0.1 + 0.06 * vv @ up), xytext=(0.08, 0.1),
                    xycoords="axes fraction", arrowprops=dict(arrowstyle="->", color=col, lw=1))
        ax.text(0.08 + 0.075 * vv @ right, 0.1 + 0.075 * vv @ up, lab, color=col, fontsize=7,
                transform=ax.transAxes, ha="center", va="center")


def render_views(shape, png_path, svg_path=None, name="model", mates=None, info=None):
    """Write the 4+ view sheet. `mates` = {name: shape} drawn in orange in the iso views."""
    bb = shape.bounding_box()
    tol = max(min(max(bb.size.X, bb.size.Y, bb.size.Z) / 400, 0.2), 0.01)
    part_mesh = _mesh(shape, tol)
    items = [(*part_mesh, PART_RGB, 1.0)]
    for m in (mates or {}).values():
        items.append((*_mesh(m, tol), MATE_RGB, 1.0))

    fig = plt.figure(figsize=(14, 9.5), dpi=110)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])
    _ortho_panel(fig.add_subplot(gs[0, 0]), shape, "top", bb, "TOP (looking -Z, X right, Y up)")
    _shaded_panel(fig.add_subplot(gs[0, 1]), items, -60, 30, "ISO front-right (shaded)")
    _shaded_panel(fig.add_subplot(gs[0, 2]), items, 120, 30, "ISO back-left (shaded)")
    _ortho_panel(fig.add_subplot(gs[1, 0]), shape, "front", bb, "FRONT (looking +Y, X right, Z up)")
    _ortho_panel(fig.add_subplot(gs[1, 1]), shape, "right", bb, "RIGHT (looking -X, Y right, Z up)")
    _shaded_panel(fig.add_subplot(gs[1, 2]), [(*part_mesh, PART_RGB, 1.0)], -60, -30,
                  "BOTTOM ISO (bed side)")
    lines = [f"{name}",
             f"bbox X {bb.size.X:.2f}  Y {bb.size.Y:.2f}  Z {bb.size.Z:.2f} mm",
             f"min ({bb.min.X:.2f}, {bb.min.Y:.2f}, {bb.min.Z:.2f})  max ({bb.max.X:.2f}, {bb.max.Y:.2f}, {bb.max.Z:.2f})"]
    if mates:
        lines.append("orange = mating/reference objects: " + ", ".join(mates))
    for k, v in (info or {}).items():
        lines.append(f"{k}: {v}")
    fig.suptitle("\n".join(lines), fontsize=9, family="monospace", x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(png_path)
    if svg_path:
        fig.savefig(svg_path)
    plt.close(fig)
    return str(png_path)


# ----------------------------------------------------------------- sections

def _face_path(face, plane):
    def ring(w):
        pts = []
        for e in w.order_edges() if hasattr(w, "order_edges") else w.edges():
            n = 2 if e.geom_type == GeomType.LINE else 32
            pts += [plane.to_local_coords(e.position_at(t)) for t in np.linspace(0, 1, n)]
        return [(p.X, p.Y) for p in pts]

    verts, codes = [], []
    for w in [face.outer_wire(), *face.inner_wires()]:
        r = ring(w)
        if len(r) < 3:
            continue
        verts += r + [r[0]]
        codes += [MplPath.MOVETO] + [MplPath.LINETO] * (len(r) - 1) + [MplPath.CLOSEPOLY]
    return MplPath(verts, codes) if verts else None


def render_sections(shape, png_path, cuts=None):
    """Cuts through the bbox centre (or `cuts` = [(plane_name, offset), ...])."""
    bb = shape.bounding_box()
    c = bb.center()
    cuts = cuts or [("XY", c.Z), ("XZ", c.Y), ("YZ", c.X)]
    planes = {"XY": Plane.XY, "XZ": Plane.XZ, "YZ": Plane.YZ}
    axes_lbl = {"XY": ("X", "Y"), "XZ": ("X", "Z"), "YZ": ("Y", "Z")}
    normal_lbl = {"XY": "Z", "XZ": "Y", "YZ": "X"}
    fig, axs = plt.subplots(1, len(cuts), figsize=(6 * len(cuts), 6), dpi=110)
    axs = np.atleast_1d(axs)
    for ax, (pn, off) in zip(axs, cuts):
        pl = planes[pn].offset(off if pn != "XZ" else -off)  # Plane.XZ normal is -Y
        try:
            sk = section(shape, section_by=pl)
            faces = sk.faces()
        except Exception:
            faces = []
        for f in faces:
            p = _face_path(f, pl)
            if p is not None:
                ax.add_patch(PathPatch(p, facecolor="#5b8fd6", edgecolor="#111", lw=0.7))
        ax.autoscale_view()
        ax.set_aspect("equal")
        ax.grid(True, which="both", lw=0.3, color="#bbb")
        ax.minorticks_on()
        h, v = axes_lbl[pn]
        ax.set_xlabel(f"{h} [mm]", fontsize=8)
        ax.set_ylabel(f"{v} [mm]", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.set_title(f"SECTION {pn} at {normal_lbl[pn]} = {off:.2f}"
                     + ("" if faces else "  (no material)"), fontsize=9)
    fig.tight_layout()
    fig.savefig(png_path)
    plt.close(fig)
    return str(png_path)
