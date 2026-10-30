# build123d cheat sheet (tested on build123d 0.13 / OCP 8.0)

Every block below is executed by `tests/test_cheatsheet.py`. Prefer these
patterns; they avoid the pitfalls listed at the end.

## Conventions for this repo

- Units mm. Export every part **in print orientation, bed face at Z = 0**
  (`align=(Align.CENTER, Align.CENTER, Align.MIN)` puts a box on the bed).
- One connected solid per exported part (`len(part.solids()) == 1`).
- Name every number at the top of the script; derive from spec.json values.
- `EXPORT_SOLIDS = {"name": part}`; mating/reference objects in `MATES = {...}`.

## Algebra mode (shapes as values) - best for composing parts

```python
from build123d import *

base = Box(60, 40, 5, align=(Align.CENTER, Align.CENTER, Align.MIN))   # z 0..5
post = Pos(20, 10, 5) * Cylinder(4, 15, align=(Align.CENTER, Align.CENTER, Align.MIN))
part = base + post                       # union
part -= Pos(-20, 0, 0) * Cylinder(1.7, 50)   # subtract a through hole (centred cylinder spans +-25)
part = part & Box(55, 40, 100)           # intersect
rotated = Rot(0, 0, 45) * part           # rotate about origin (X, Y, Z degrees)
moved = Pos(0, 0, 10) * rotated          # translate
assert len(part.solids()) == 1 and part.is_valid
```

## Builder mode - best for sketch -> extrude workflows

```python
from build123d import *

with BuildPart() as bp:
    with BuildSketch(Plane.XY):                       # sketch on the bed
        RectangleRounded(80, 50, radius=5)
    extrude(amount=3)                                 # z 0..3
    with BuildSketch(Plane.XY.offset(3)):             # sketch on top of the plate
        with Locations((-25, 0), (25, 0)):
            Circle(6)
    extrude(amount=10)                                # two posts z 3..13
    with Locations((-25, 0, 13), (25, 0, 13)):        # holes from the post tops down
        Hole(radius=1.7, depth=10)                    # Hole() cuts DOWN from the location
    fillet(bp.edges().group_by(Axis.Z)[-1], radius=0.5)  # round the post tops (hole rims too)
part = bp.part
assert len(part.solids()) == 1
```

## Selecting edges/faces

```python
from build123d import *

p = Box(30, 20, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
top_face = p.faces().sort_by(Axis.Z)[-1]                 # highest face
bottom_edges = p.edges().group_by(Axis.Z)[0]             # all edges at lowest Z
vertical_edges = p.edges().filter_by(Axis.Z)             # edges parallel to Z
p = p.fillet(2, vertical_edges)                          # method form: radius, edge list
p = p.chamfer(0.8, None, p.edges().group_by(Axis.Z)[0])  # elephant's-foot chamfer
assert abs(p.bounding_box().size.Z - 10) < 1e-6
```

## Shell / hollow box with an open top

```python
from build123d import *

outer = Box(60, 40, 25, align=(Align.CENTER, Align.CENTER, Align.MIN))
outer = outer.fillet(3, outer.edges().filter_by(Axis.Z))
box = offset(outer, amount=-2.0, openings=outer.faces().sort_by(Axis.Z)[-1])   # 2 mm walls, open top
assert len(box.solids()) == 1
```

## Profiles: revolve, loft, sweep

```python
from build123d import *

# revolve a 2D profile drawn in XZ around Z (x = radius, y = height on Plane.XZ)
with BuildPart() as cup:
    with BuildSketch(Plane.XZ):
        Polygon((0, 0), (20, 0), (22, 30), (20, 30), (18, 2), (0, 2), align=None)
    revolve(axis=Axis.Z)
# loft between two sections
with BuildPart() as reducer:
    with BuildSketch(Plane.XY):
        Circle(18)
    with BuildSketch(Plane.XY.offset(25)):
        Circle(12)
    loft()
# sweep a circle along a path
path = Spline((0, 0, 0), (20, 0, 10), (40, 10, 20))
with BuildPart() as tube:
    with BuildSketch(Plane(origin=path @ 0, z_dir=path % 0)):
        Circle(3)
    sweep(path=path)
assert cup.part.is_valid and reducer.part.is_valid and tube.part.is_valid
```

## Text (labels, embossed or debossed)

```python
from build123d import *

plate = Box(50, 20, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
label = extrude(Pos(0, 0, 3) * Text("M3", font_size=8), amount=-0.6)   # 0.6 mm deep
plate -= label
assert plate.is_valid
```

## Repo helpers (cad_tools)

```python
from build123d import *
from cad_tools.fasteners import heat_set_hole, heat_set_boss, counterbore, countersink, hex_nut_pocket, clearance_dia
from cad_tools.features import chamfer_bottom, teardrop_hole, slot_array

plate = Box(40, 30, 8, align=(Align.CENTER, Align.CENTER, Align.MIN))
plate -= Pos(-12, 0, 8) * counterbore("M3")            # cutters: mouth at Z=0, go DOWN -> place at the top face
plate -= Pos(12, 0, 8) * heat_set_hole("M3")           # pocket depth = insert length + 1 (vendor rule)
plate -= Pos(0, 8, 8) * hex_nut_pocket("M3", depth=3)
plate -= teardrop_hole(radius=2.6, length=50, axis="X", center=(0, -8, 4))   # horizontal, apex +Z
plate = chamfer_bottom(plate, 0.6)
boss = heat_set_boss("M3", total_height=8)             # raises if too short for the insert
assert len(plate.solids()) == 1 and clearance_dia("M3") == 3.6
```

## Mates (reference objects for fit checks)

```python
from build123d import *

PHONE = (71.5, 149.6, 8.25)
CLEAR = 0.4
cradle = Box(PHONE[0] + 2 * CLEAR + 6, 40, PHONE[2] + 2 * CLEAR + 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
pocket = Pos(0, 0, 3) * Box(PHONE[0] + 2 * CLEAR, 40, 50, align=(Align.CENTER, Align.CENTER, Align.MIN))
cradle -= pocket
phone = Pos(0, 0, 3 + CLEAR) * Box(*PHONE, align=(Align.CENTER, Align.CENTER, Align.MIN))
EXPORT_SOLIDS = {"cradle": cradle}
MATES = {"phone": phone}          # rendered orange, checked for interference by `cad build`
assert (cradle & phone).volume < 1e-6
```

## Pitfalls (each one has bitten this repo)

1. `Box/Cylinder` default `align` is CENTER: a `Cylinder(r, 10)` spans z -5..5.
   Use `align=(..., Align.MIN)` or remember the half-height.
2. `extrude(amount=a, both=True)` gives total length **2a**.
3. `chamfer()` / `fillet()` free functions in algebra mode take only edges -
   use the methods `part.chamfer(length, None, edges)` / `part.fillet(r, edges)`
   when you have a shape value. They raise if the edge is shorter than the size.
4. Nested `Locations` / `Plane.offset` stack: `with Locations((0,0,5)):` +
   `BuildSketch(Plane.XY.offset(5))` puts the sketch at z = 10 (the old
   gridfinity helper floated the body 4.75 mm above its feet this way).
5. `group_by(Axis.Z)[0]` = edges at the lowest Z, `sort_by(Axis.Z)[0]` = the
   single lowest object. `filter_by(Axis.Z)` = edges parallel to Z.
6. Unioning parts that only touch at a face/edge can produce 2 solids; overlap
   by 0.01 mm or check `len(part.solids())`.
7. `Plane.XZ` normal is **-Y**; `Plane.XZ.offset(5)` is at y = -5.
8. A cutter that is exactly as thick as the wall leaves coincident faces and
   may leave a zero-thickness skin; make cutters longer than the wall
   (the old lid vents stopped 0.6 mm short and were blind).
9. Holes for printed parts: vertical screw holes +0.2 mm (`clearance_dia`),
   heat-set holes at the vendor diameter (no extra), horizontal holes > 4 mm
   as teardrops.
