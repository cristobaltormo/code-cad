# Electronics & PCB Enclosure Prompt

Use this prompt to design parametric enclosures for development boards, sensors, custom PCBs, or battery packs.

---

```markdown
Design a two-part parametric enclosure (base and lid) for the following electronic board using Python and `build123d`.

### Target Electronics:
- Board Name: [e.g., ESP32-S3-DevKitC-1 / Raspberry Pi Zero 2W / Custom PCB]
- PCB Dimensions (Length x Width x Height): [e.g., 55.0 mm x 28.0 mm x 1.6 mm]
- Mounting Hole Locations & Diameter: [e.g., 4x M2.5 holes at 2.5 mm offsets from corners]
- Connectors & Port Locations: [e.g., USB-C connector centered on the short edge, antenna cutout, power switch]

### Mandatory Enclosure Constraints:
1. Tolerances & Clearances:
   - Internal board clearance: 0.4 mm to 0.5 mm on all sides.
   - Connector port clearance: +1.0 mm width and height around plugs to accommodate cable molded hoods.
   - Enclosure joint: Interlocking friction lip (0.4 mm offset) or cantilever snap-fits.
2. Fasteners & Mounting:
   - Standoff bosses with pilot holes for Ruthex M2.5/M3 brass heat-set inserts or M2.5 self-tapping screws.
   - Minimum 3.0 mm standoff height to clear through-hole solder pins underneath the PCB.
3. Manufacturing:
   - Sized for FDM printing: 2.4 mm nominal wall thickness (6 perimeters at 0.4 mm).
   - Bottom chamfer: 0.8 mm at 45 degrees to counteract elephant's foot.
   - Ventilation: Linear slot array on lid or base for convective thermal management.
   - Zero support printing: Base and lid must both print completely flat on the build plate without support structures.

Execute the script, inspect the model topology and bounding box metrics, and provide the `.step`, `.stl`, and `_views.svg` files.
```
