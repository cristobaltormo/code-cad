"""Independent STL mesh validation (numpy only).

Checks the exported STL itself, not the BREP it came from, so export problems
(holes, flipped normals, degenerate triangles, extra shells) are caught before
the file reaches a slicer.
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np


def read_stl(path) -> np.ndarray:
    """Return triangles as an (N, 3, 3) float64 array. Handles binary and ASCII STL."""
    data = Path(path).read_bytes()
    if len(data) >= 84:
        (count,) = struct.unpack("<I", data[80:84])
        if 84 + count * 50 == len(data):
            rec = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
            arr = np.frombuffer(data, dtype=rec, count=count, offset=84)
            return arr["v"].astype(np.float64)
    text = data.decode("ascii", errors="ignore")
    verts = [
        [float(x) for x in line.split()[1:4]]
        for line in text.splitlines()
        if line.strip().startswith("vertex")
    ]
    return np.asarray(verts, dtype=np.float64).reshape(-1, 3, 3)


def _components(n_vertices: int, faces: np.ndarray) -> int:
    parent = np.arange(n_vertices)

    def find(i):
        root = i
        while parent[root] != root:
            root = parent[root]
        while parent[i] != root:
            parent[i], i = root, parent[i]
        return root

    for a, b, c in faces:
        ra, rb, rc = find(a), find(b), find(c)
        parent[rb] = ra
        parent[find(rc)] = ra
    used = np.unique(faces)
    return len({find(int(v)) for v in used})


def check_mesh(path, weld_tol: float = 1e-4) -> dict:
    """Watertightness / orientation / volume report for an STL file."""
    tris = read_stl(path)
    if len(tris) == 0:
        return {"triangles": 0, "watertight": False, "error": "empty mesh"}

    flat = tris.reshape(-1, 3)
    keys = np.round(flat / weld_tol).astype(np.int64)
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    faces = inverse.reshape(-1, 3)

    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cross = np.cross(b - a, c - a)
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    degenerate = int(np.sum(areas < 1e-12))

    # Directed edges: in a closed, consistently oriented mesh every directed
    # edge appears once and its reverse appears once.
    directed = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    directed = directed[directed[:, 0] != directed[:, 1]]
    undirected = np.sort(directed, axis=1)
    _, ucounts = np.unique(undirected, axis=0, return_counts=True)
    boundary_edges = int(np.sum(ucounts == 1))
    nonmanifold_edges = int(np.sum(ucounts > 2))
    _, dcounts = np.unique(directed, axis=0, return_counts=True)
    misoriented = int(np.sum(dcounts > 1))

    signed_volume = float(np.sum(np.einsum("ij,ij->i", a, np.cross(b, c))) / 6.0)
    lo, hi = flat.min(axis=0), flat.max(axis=0)
    return {
        "triangles": int(len(tris)),
        "vertices": int(faces.max() + 1),
        "shells": _components(int(faces.max() + 1), faces),
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "misoriented_edges": misoriented,
        "degenerate_triangles": degenerate,
        "watertight": boundary_edges == 0 and nonmanifold_edges == 0,
        "outward_normals": signed_volume > 0,
        "volume_mm3": abs(signed_volume),
        "area_mm2": float(areas.sum()),
        "bbox_min": lo.round(4).tolist(),
        "bbox_max": hi.round(4).tolist(),
        "size": (hi - lo).round(4).tolist(),
    }
