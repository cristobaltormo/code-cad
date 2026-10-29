from build123d import (
    BuildPart,
    Box,
    Locations,
)

def snap_fit_tab(
    beam_length=8.0,
    beam_width=6.0,
    beam_thickness=1.5,
    hook_depth=0.8,
):
    with BuildPart() as tab:
        Box(beam_width, beam_thickness, beam_length)
        hook_height = hook_depth * 1.5
        hook_y = (beam_thickness + hook_depth) / 2.0
        hook_z = (beam_length - hook_height) / 2.0
        with Locations((0, hook_y, hook_z)):
            Box(beam_width, hook_depth, hook_height)

    return tab.part

def snap_fit_catch(
    catch_width=6.6,
    catch_depth=1.2,
    catch_height=2.0,
):
    with BuildPart() as catch:
        Box(catch_width, catch_depth, catch_height)

    return catch.part
