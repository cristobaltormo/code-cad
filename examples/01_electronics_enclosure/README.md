# 01 - Raspberry Pi Pico enclosure

Base + lid for a Raspberry Pi Pico, using the board data from the reference
database (`cad lookup pico`: 51 x 21 x 1.0 mm, Ø2.1 holes on 47 x 11.4).

- 4 standoffs with ruthex M2 heat-set pockets (Ø3.2, 5.0 deep, 1.0 mm floor below)
- micro-USB opening on the -X short wall, sized for the cable overmold
- lid with a hollow sliding lip (0.2 mm clearance per side) and through vents
- 2.0 mm walls, 0.8 / 0.6 mm bed chamfers; both parts exported in print orientation

```bash
./bin/cad build examples/01_electronics_enclosure
```
