"""code-cad: build123d helpers + verification pipeline for 3D-printable parts."""

from cad_tools.fasteners import (BUTTON, COUNTERSUNK, HEAT_SET, HEAT_SET_SPECS, HEX_NUT, SCREW_SPECS,
                                 SHCS, captive_hex_pocket, clearance_dia, counterbore, countersink,
                                 heat_set_boss, heat_set_hole, hex_nut_pocket, screw_counterbore)
from cad_tools.features import chamfer_bottom, slot_array, teardrop_hole, ventilation_slots
from cad_tools.gridfinity import GRIDFINITY_PITCH, gridfinity_base, gridfinity_bin
from cad_tools.inspect import generate_multiview_svg, inspect_solid
from cad_tools.joints import snap_fit_catch, snap_fit_tab

__all__ = [
    "BUTTON", "COUNTERSUNK", "HEAT_SET", "HEAT_SET_SPECS", "HEX_NUT", "SCREW_SPECS", "SHCS",
    "captive_hex_pocket", "clearance_dia", "counterbore", "countersink", "heat_set_boss",
    "heat_set_hole", "hex_nut_pocket", "screw_counterbore", "chamfer_bottom", "slot_array",
    "teardrop_hole", "ventilation_slots", "GRIDFINITY_PITCH", "gridfinity_base", "gridfinity_bin",
    "generate_multiview_svg", "inspect_solid", "snap_fit_catch", "snap_fit_tab",
]
