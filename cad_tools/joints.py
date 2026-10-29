from build123d import (
    BuildPart,
    BuildSketch,
    BuildLine,
    Line,
    make_face,
    extrude,
    Box,
    Plane,
)

def snap_fit_tab(
    beam_length=8.0,
    beam_width=6.0,
    beam_thickness=1.5,
    hook_depth=1.0,
    hook_height=2.0,
):
    with BuildPart() as tab:
        with BuildSketch(Plane.YZ):
            with BuildLine():
                l1 = Line((0, 0), (beam_thickness, 0))
                l2 = Line((beam_thickness, 0), (beam_thickness, beam_length - hook_height))
                l3 = Line(
                    (beam_thickness, beam_length - hook_height),
                    (beam_thickness + hook_depth, beam_length - hook_height),
                )
                l4 = Line(
                    (beam_thickness + hook_depth, beam_length - hook_height),
                    (beam_thickness, beam_length),
                )
                l5 = Line((beam_thickness, beam_length), (0, beam_length))
                l6 = Line((0, beam_length), (0, 0))
            make_face()
        extrude(amount=beam_width / 2.0, both=True)

    return tab.part

def snap_fit_catch(
    catch_width=6.6,
    catch_depth=1.4,
    catch_height=2.4,
):
    with BuildPart() as catch:
        Box(catch_width, catch_depth, catch_height)

    return catch.part
