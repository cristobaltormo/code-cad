"""2 x 1 Gridfinity bin, 3 units tall, with 6x2 magnet pockets.

Build: ./bin/cad build examples/06_gridfinity_bin
Spec values (42 mm pitch, 4.75 mm base profile, 7 mm units, magnets 6.5 x 2.4
at +-13 mm) are verified against gridfinity-rebuilt: `cad lookup gridfinity`.
Prints upright as exported; the magnet pockets face the bed (no bridging).
"""

from cad_tools.gridfinity import gridfinity_bin

bin_2x1 = gridfinity_bin(grid_x=2, grid_y=1, height_u=3, wall=1.2, magnet_holes=True)

EXPORT_SOLIDS = {"gridfinity_bin_2x1x3": bin_2x1}
