"""Regression tests: the verification tools must catch the bugs the old repo shipped."""

import json
import shutil
import sys
from pathlib import Path

import pytest
from build123d import Align, Box, Cylinder, Pos, export_step, export_stl

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cad_tools import measure, pipeline  # noqa: E402
from cad_tools.fasteners import counterbore, heat_set_boss, heat_set_hole  # noqa: E402
from cad_tools.gridfinity import gridfinity_bin  # noqa: E402
from cad_tools.meshcheck import check_mesh  # noqa: E402
from cad_tools.printability import analyze  # noqa: E402

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)


def _export(shape, tmp_path, name="p"):
    step, stl = tmp_path / f"{name}.step", tmp_path / f"{name}.stl"
    export_step(shape, str(step))
    export_stl(shape, str(stl), tolerance=0.005)
    return step, stl


def test_ray_measures_walls_and_gaps():
    box = Box(20, 10, 10, align=ON_BED) - Pos(0, 0, 2) * Box(16, 6, 30, align=ON_BED)
    r = measure.ray(box, (-50, 0, 5), (1, 0, 0))
    assert [round(m["length"], 3) for m in r["material"]] == [2.0, 2.0]
    assert round(r["gaps"][0]["length"], 3) == 16.0


def test_holes_finds_insert_pocket_depth():
    plate = Box(20, 20, 10, align=ON_BED) - Pos(0, 0, 10) * heat_set_hole("M3")
    bores = [h for h in measure.holes(plate) if h["kind"] == "hole" and abs(h["diameter"] - 4.0) < 1e-6]
    assert len(bores) == 1 and abs(bores[0]["length"] - 6.4) < 1e-6   # 6.7 total incl. 0.3 lead-in


def test_heat_set_boss_refuses_too_short():
    with pytest.raises(ValueError):
        heat_set_boss("M3", total_height=4.0)   # old enclosure bug: 3.25 mm pocket for a 5.7 mm insert


def test_blind_vent_is_detected():
    lid = Box(30, 30, 4, align=ON_BED)
    blind = lid - Pos(0, 0, 0.6) * Box(2, 20, 3.4, align=ON_BED)   # stops 0.6 short
    assert measure.ray(blind, (0, 0, 50), (0, 0, -1))["material"], "skin must be found"
    w = measure.min_wall(blind, 0.8)
    assert w["min_thickness"] < 0.8


def test_disconnected_part_fails_build_gate(tmp_path):
    proj = tmp_path / "floaty"
    proj.mkdir()
    (proj / "floaty.py").write_text(
        "from build123d import *\n"
        "a = Box(10,10,5, align=(Align.CENTER,Align.CENTER,Align.MIN))\n"
        "b = Pos(0,0,10) * Box(10,10,5, align=(Align.CENTER,Align.CENTER,Align.MIN))\n"
        "EXPORT_SOLIDS = {'p': a + b}\n")
    rep = pipeline.build(proj, render=False, export_3mf=False)
    assert rep["status"] == "FAIL"
    failed = {c["id"] for c in rep["parts"]["p"]["checks"] if not c["pass"]}
    assert "single_solid" in failed


def test_gridfinity_is_one_solid():
    g = gridfinity_bin(2, 2, 3)
    assert len(g.solids()) == 1 and abs(g.bounding_box().size.Z - 21.0) < 1e-6


def test_meshcheck_watertight(tmp_path):
    _, stl = _export(Box(10, 10, 10), tmp_path)
    m = check_mesh(stl)
    assert m["watertight"] and m["outward_normals"] and m["shells"] == 1
    assert abs(m["volume_mm3"] - 1000) < 1e-3


def test_printability_flags_round_horizontal_hole(tmp_path):
    part = Box(20, 10, 20, align=ON_BED) - Pos(0, 0, 10) * Cylinder(3, 40).rotate(
        __import__("build123d").Axis.X, 90)
    step, stl = _export(part, tmp_path)
    checks = {f["check"] for f in analyze(step, stl)["findings"]}
    assert "teardrop" in checks


def _mini_project(tmp_path):
    proj = tmp_path / "mini"
    proj.mkdir()
    (proj / "mini.py").write_text(
        "from build123d import *\nfrom cad_tools.fasteners import counterbore\n"
        "from cad_tools.features import chamfer_bottom\n"
        "p = Box(30,20,6, align=(Align.CENTER,Align.CENTER,Align.MIN))\n"
        "p -= Pos(0,0,6) * counterbore('M3')\n"
        "EXPORT_SOLIDS = {'plate': chamfer_bottom(p, 0.6)}\n")
    (proj / "spec.json").write_text(json.dumps({
        "name": "mini", "model": "mini.py", "printer": "bambu_p1s", "material": "PETG",
        "features": ["counterbored hole in the centre"],
        "critical_dimensions": [{"id": "thickness", "nominal": 6.0, "tol_minus": 0.05, "tol_plus": 0.05}],
        "checks": [{"type": "solids", "part": "plate", "count": 1},
                   {"type": "hole", "part": "plate", "diameter": 3.6, "tol": 0.01, "count": 1}]}))
    return proj


def _attest(proj, kind, data):
    f = proj / f"{kind}_in.json"
    f.write_text(json.dumps(data))
    return pipeline.attest(proj, kind, f)


def test_release_gate_end_to_end(tmp_path):
    proj = _mini_project(tmp_path)
    assert pipeline.build(proj, render=False)["status"] == "PASS"
    assert pipeline.run_spec_checks(proj)["status"] == "PASS"
    pipeline.run_printability(proj)
    assert not pipeline.release(proj)["released"]                  # no independent verification yet

    bad = _attest(proj, "dimensions", {"verifier": "t", "measurements": [{"id": "thickness", "measured": 6.3}],
                                       "visual": [{"feature": "counterbored hole in the centre", "ok": True}]})
    assert bad["status"] == "FAIL"                                  # computed from spec tolerance, not claimed
    ok = _attest(proj, "dimensions", {"verifier": "t", "measurements": [{"id": "thickness", "measured": 6.0}],
                                      "visual": [{"feature": "counterbored hole in the centre", "ok": True}]})
    assert ok["status"] == "PASS"
    _attest(proj, "printability", {"verifier": "t", "issues": []})
    rel = pipeline.release(proj)
    assert rel["released"], rel.get("blockers")
    assert (proj / "release" / "plate.stl").exists()

    # any rebuild invalidates every attestation
    pipeline.build(proj, render=False)
    assert not pipeline.release(proj)["released"]


def test_tampered_artifact_is_stale(tmp_path):
    proj = _mini_project(tmp_path)
    pipeline.build(proj, render=False)
    pipeline.run_spec_checks(proj)
    stl = proj / "build" / "plate.stl"
    stl.write_bytes(stl.read_bytes()[:-50] + b"\0" * 50)
    assert pipeline.status(proj)["gates"]["auto"] == "STALE"


EXAMPLES = sorted(p for p in (ROOT / "examples").iterdir() if p.is_dir())


@pytest.mark.parametrize("ex", EXAMPLES, ids=[p.name for p in EXAMPLES])
def test_examples_build(ex, tmp_path):
    work = tmp_path / ex.name
    shutil.copytree(ex, work, ignore=shutil.ignore_patterns("build", "release", "verification"))
    rep = pipeline.build(work, render=False, export_3mf=False)
    assert rep["status"] == "PASS", pipeline.format_build(rep)
