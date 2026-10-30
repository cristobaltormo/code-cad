"""Design pipeline: build -> verify (auto + independent agents) -> release gate.

Project layout (created by `cad new <name>`):

    projects/<name>/
      spec.json          requirements, researched object dims, critical dimensions
      research/          dimension research notes from the researcher agent
      <name>.py          parametric build123d model; defines EXPORT_SOLIDS (+ MATES)
      build/             STEP/STL/3MF + PNG/SVG renders + report.json   (staging)
      verification/      auto.json, printability_auto.json,
                         dimensions.json, printability.json             (attestations)
      release/           files copied here ONLY after every gate passes

The release gate binds every attestation to the SHA-256 of the exact build
artifacts, so any rebuild after verification invalidates it.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

from build123d import Compound, Solid, export_step, export_stl

from cad_tools import measure
from cad_tools.meshcheck import check_mesh
from cad_tools.printers import estimate_mass, get_printer

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


# ----------------------------------------------------------------- utilities

def _now():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))


def resolve(project) -> Path:
    """Accept a project dir, a name under projects/, or a path to the model script."""
    p = Path(project)
    if p.is_file() and p.suffix == ".py":
        return p.resolve().parent
    if p.is_dir():
        return p.resolve()
    if (PROJECTS / project).is_dir():
        return (PROJECTS / project).resolve()
    raise FileNotFoundError(f"project not found: {project}")


def load_spec(pdir: Path) -> dict:
    f = pdir / "spec.json"
    return json.loads(f.read_text()) if f.exists() else {}


def model_script(pdir: Path) -> Path:
    spec = load_spec(pdir)
    if spec.get("model"):
        return pdir / spec["model"]
    cand = pdir / f"{pdir.name}.py"
    if cand.exists():
        return cand
    scripts = [p for p in pdir.glob("*.py") if not p.name.startswith("_")]
    if len(scripts) == 1:
        return scripts[0]
    raise FileNotFoundError(f"cannot find the model script in {pdir} (set \"model\" in spec.json)")


def artifacts(pdir: Path) -> dict:
    """Files whose hashes the attestations are bound to."""
    b = pdir / "build"
    files = sorted([*b.glob("*.step"), *b.glob("*.stl"), *b.glob("*.3mf"), *(b / "mates").glob("*.step")])
    return {str(f.relative_to(pdir)): _sha(f) for f in files}


# ----------------------------------------------------------------- new project

SPEC_TEMPLATE = {
    "name": "",
    "description": "What it is, what it holds/attaches to, where it lives.",
    "model": "",
    "printer": "generic_220",
    "material": "PETG",
    "nozzle": 0.4,
    "objects": {
        "_example_phone": {
            "name": "Researched real-world object this part must fit (delete if none)",
            "dimensions": {"width": 0.0, "height": 0.0, "depth": 0.0},
            "sources": ["https://..."],
            "confidence": "high | medium | low | user-measured",
            "research_file": "research/<object>.json",
        }
    },
    "requirements": ["Functional requirement 1", "Load / environment / fit requirement 2"],
    "features": ["Visually verifiable feature, e.g. 'USB-C opening on the -X short wall'"],
    "critical_dimensions": [
        {
            "id": "pocket_width",
            "part": "body",
            "description": "Inner pocket width along X (object width + 2 x clearance)",
            "nominal": 0.0,
            "tol_minus": 0.1,
            "tol_plus": 0.1,
            "basis": "object.width 71.5 + 2 x 0.3 sliding clearance",
        }
    ],
    "checks": [
        {"type": "max_size", "part": "body", "value": [200, 200, 200]},
        {"type": "solids", "part": "body", "count": 1},
    ],
}

MODEL_TEMPLATE = '''"""{name}: parametric model. Run via `cad build {name}`.

Conventions: millimetres; export each part in its PRINT orientation with the
bed face at Z = 0; parameters at the top derive from spec.json values.
"""

from build123d import *  # noqa: F401,F403

from cad_tools.features import chamfer_bottom  # noqa: F401

# ---- parameters (keep every number named; derive from the spec) -----------
WALL = 2.4

# ---- geometry ---------------------------------------------------------------
with BuildPart() as body:
    Box(40, 30, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))

part = chamfer_bottom(body.part, 0.8)

EXPORT_SOLIDS = {{"body": part}}

# Reference objects (the thing being held / mated), placed where they sit.
# Rendered in orange and used for clearance/interference checks. Not exported
# for printing.
MATES = {{}}
'''


def new_project(name: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_]*", name):
        raise ValueError("project name must be snake_case: [a-z0-9_]")
    pdir = PROJECTS / name
    if pdir.exists():
        raise FileExistsError(f"{pdir} already exists")
    (pdir / "research").mkdir(parents=True)
    spec = json.loads(json.dumps(SPEC_TEMPLATE))
    spec["name"], spec["model"] = name, f"{name}.py"
    _write_json(pdir / "spec.json", spec)
    (pdir / f"{name}.py").write_text(MODEL_TEMPLATE.format(name=name))
    return pdir


# ----------------------------------------------------------------- build

def _load_module(script: Path):
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(script.parent))
    spec = importlib.util.spec_from_file_location(f"cad_model_{script.stem}", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _shapes(mod):
    if isinstance(getattr(mod, "EXPORT_SOLIDS", None), dict):
        parts = dict(mod.EXPORT_SOLIDS)
    elif hasattr(mod, "RESULT"):
        parts = {"result": mod.RESULT}
    else:
        parts = {k.lower(): v for k, v in vars(mod).items()
                 if not k.startswith("_") and isinstance(v, (Solid, Compound))}
    mates = dict(getattr(mod, "MATES", {}) or {})
    for k, v in list(parts.items()) + list(mates.items()):
        if hasattr(v, "part") and not isinstance(v, (Solid, Compound)):  # BuildPart passed
            (parts if k in parts else mates)[k] = v.part
    return parts, mates


def _check(cid, ok, message, severity="fail", **extra):
    return {"id": cid, "pass": bool(ok), "severity": severity if not ok else "ok", "message": message, **extra}


def build(project, render=True, export_3mf=True) -> dict:
    from cad_tools import render as R

    pdir = resolve(project)
    spec = load_spec(pdir)
    script = model_script(pdir)
    out = pdir / "build"
    if out.exists():
        shutil.rmtree(out)
    (out / "mates").mkdir(parents=True)
    verif = pdir / "verification"
    if verif.exists():  # every rebuild invalidates previous verification
        shutil.rmtree(verif)

    mod = _load_module(script)
    parts, mates = _shapes(mod)
    if not parts:
        raise RuntimeError("model defines no EXPORT_SOLIDS")
    printer = get_printer(spec.get("printer"))
    material = spec.get("material", "PLA")

    report = {"project": pdir.name, "script": script.name, "built_at": _now(),
              "printer": printer, "material": material, "parts": {}, "mates": {}}
    for mname, m in mates.items():
        f = out / "mates" / f"{mname}.step"
        export_step(m, str(f))
        report["mates"][mname] = {"step": str(f.relative_to(pdir)), **measure.bbox(m)}

    for name, shape in parts.items():
        checks = []
        bb = measure.bbox(shape)
        checks.append(_check("brep_valid", shape.is_valid, "BREP topology valid (BRepCheck)"))
        checks.append(_check("single_solid", bb["solids"] == 1,
                             f"{bb['solids']} solid(s); a printable part should be exactly 1 connected solid"))
        checks.append(_check("positive_volume", bb["volume_mm3"] > 1e-3, f"volume {bb['volume_mm3']} mm3"))
        checks.append(_check("on_bed", abs(bb["min"][2]) < 1e-3,
                             f"min Z = {bb['min'][2]} (export in print orientation with the bed face at Z=0)",
                             severity="warn"))

        step_f, stl_f = out / f"{name}.step", out / f"{name}.stl"
        export_step(shape, str(step_f))
        export_stl(shape, str(stl_f), tolerance=0.005, angular_tolerance=0.1)
        files = {"step": str(step_f.relative_to(pdir)), "stl": str(stl_f.relative_to(pdir))}
        if export_3mf:
            try:
                from build123d import Mesher
                mesher = Mesher()
                mesher.add_shape(shape, linear_deflection=0.005, angular_deflection=0.1)
                mesher.write(str(out / f"{name}.3mf"))
                files["3mf"] = f"build/{name}.3mf"
            except Exception as exc:  # 3MF is a convenience, never block on it
                files["3mf_error"] = str(exc)

        mesh = check_mesh(stl_f)
        checks.append(_check("stl_watertight", mesh["watertight"],
                             f"STL boundary edges {mesh['boundary_edges']}, non-manifold {mesh['nonmanifold_edges']}"))
        checks.append(_check("stl_oriented", mesh["outward_normals"] and mesh["misoriented_edges"] == 0,
                             f"normals outward={mesh['outward_normals']}, misoriented edges {mesh['misoriented_edges']}"))
        checks.append(_check("stl_single_shell", mesh["shells"] == 1, f"STL shells: {mesh['shells']}"))
        dv = abs(mesh["volume_mm3"] - bb["volume_mm3"]) / max(bb["volume_mm3"], 1e-9)
        checks.append(_check("stl_matches_step", dv < 0.01,
                             f"STL volume {mesh['volume_mm3']:.1f} vs STEP {bb['volume_mm3']:.1f} ({dv*100:.2f}%)"))
        size = bb["size"]
        vol = printer["build_volume"]
        fits = ((size[0] <= vol[0] and size[1] <= vol[1]) or (size[1] <= vol[0] and size[0] <= vol[1])) and size[2] <= vol[2]
        checks.append(_check("fits_printer", fits, f"{size} vs {printer['name']} {vol}"))

        mass, mass_solid = estimate_mass(bb["volume_mm3"], shape.area, material)
        if render:
            info = {"printer": f"{printer['name']} {vol}", "material": material,
                    "mass": f"~{mass} g (15% infill) / {mass_solid} g solid"}
            R.render_views(shape, out / f"{name}_views.png", out / f"{name}_views.svg",
                           name=name, mates=mates, info=info)
            R.render_sections(shape, out / f"{name}_sections.png")
            files.update(views_png=f"build/{name}_views.png", views_svg=f"build/{name}_views.svg",
                         sections_png=f"build/{name}_sections.png")
        clear = {}
        for mname, m in mates.items():
            c = measure.clearance(shape, m)
            clear[mname] = c
            checks.append(_check(f"no_interference_{mname}", c["interference_mm3"] < 1e-3,
                                 f"part vs {mname}: interference {c['interference_mm3']} mm3, min gap {c['min_distance']} mm"))
        report["parts"][name] = {"files": files, "bbox": bb, "mesh": mesh, "checks": checks,
                                 "mass_g": mass, "mass_solid_g": mass_solid, "area_mm2": round(shape.area, 1),
                                 "holes": measure.holes(shape), "clearance": clear}

    hard = [c for p in report["parts"].values() for c in p["checks"] if not c["pass"] and c["severity"] == "fail"]
    report["status"] = "FAIL" if hard else "PASS"
    report["artifacts"] = artifacts(pdir)
    _write_json(out / "report.json", report)
    (out / "report.md").write_text(format_build(report))
    return report


def format_build(report) -> str:
    lines = [f"## Build: {report['project']}  ->  {report['status']}", ""]
    for name, p in report["parts"].items():
        bb = p["bbox"]
        lines += [f"### {name}", "",
                  f"- bbox: {bb['size'][0]} x {bb['size'][1]} x {bb['size'][2]} mm "
                  f"(min {bb['min']}, max {bb['max']})",
                  f"- volume {bb['volume_mm3']/1000:.2f} cm3, mass ~{p['mass_g']} g @15% infill "
                  f"({p['mass_solid_g']} g solid, {report['material']})",
                  f"- holes/bosses found: {len(p['holes'])}", ""]
        for c in p["checks"]:
            mark = "PASS" if c["pass"] else ("WARN" if c["severity"] == "warn" else "FAIL")
            lines.append(f"  - [{mark}] {c['id']}: {c['message']}")
        lines += ["", "  files: " + ", ".join(f"{k}={v}" for k, v in p["files"].items()), ""]
    return "\n".join(lines)


# ----------------------------------------------------------------- verify (auto)

def _part_step(pdir, part):
    return measure.load(pdir / "build" / f"{part}.step")


def run_spec_checks(project) -> dict:
    """Machine-checkable assertions from spec.json, evaluated on the exported STEP."""
    pdir = resolve(project)
    spec = load_spec(pdir)
    rep_f = pdir / "build" / "report.json"
    if not rep_f.exists():
        raise RuntimeError("no build found; run `cad build` first")
    report = json.loads(rep_f.read_text())
    results = []
    cache = {}

    def shape(part):
        if part not in cache:
            cache[part] = _part_step(pdir, part)
        return cache[part]

    for i, chk in enumerate(spec.get("checks", [])):
        t, part = chk.get("type"), chk.get("part") or next(iter(report["parts"]))
        cid = chk.get("id", f"{t}_{i}")
        try:
            if part not in report["parts"]:
                results.append(_check(cid, False, f"part '{part}' not in build ({list(report['parts'])})"))
                continue
            s = shape(part)
            if t == "max_size":
                size = measure.bbox(s)["size"]
                ok = all(a <= b + 1e-6 for a, b in zip(size, chk["value"]))
                results.append(_check(cid, ok, f"size {size} <= {chk['value']}"))
            elif t == "bbox_size":
                ax = "xyz".index(chk["axis"].lower())
                v = measure.bbox(s)["size"][ax]
                lo, hi = chk["nominal"] - chk.get("tol_minus", chk.get("tol", 0.1)), chk["nominal"] + chk.get("tol_plus", chk.get("tol", 0.1))
                results.append(_check(cid, lo <= v <= hi, f"bbox {chk['axis']} = {v} in [{lo:.3f}, {hi:.3f}]", measured=v))
            elif t == "solids":
                n = measure.bbox(s)["solids"]
                results.append(_check(cid, n == chk.get("count", 1), f"{n} solids (want {chk.get('count', 1)})"))
            elif t == "hole":
                tol = chk.get("tol", 0.05)
                hs = [h for h in measure.holes(s) if h["kind"] == chk.get("kind", "hole")
                      and abs(h["diameter"] - chk["diameter"]) <= tol and h["sweep_deg"] >= 300]
                if "axis" in chk:
                    want = chk["axis"].lower()
                    hs = [h for h in hs if abs(h["axis"]["xyz".index(want)]) > 0.99]
                if chk.get("min_length"):
                    hs = [h for h in hs if h["length"] >= chk["min_length"] - 1e-3]
                want_n = chk.get("count")
                ok = len(hs) == want_n if want_n is not None else len(hs) > 0
                results.append(_check(cid, ok, f"{len(hs)} x Ø{chk['diameter']}±{tol} {chk.get('kind', 'hole')}(s)"
                                      + (f" min length {chk['min_length']}" if chk.get("min_length") else "")
                                      + f" (want {want_n if want_n is not None else '>=1'})",
                                      found=[h["axis_start"] for h in hs]))
            elif t == "ray":
                r = measure.ray(s, chk["origin"], chk["direction"])
                key = chk.get("measure", "gaps")
                idx = chk.get("index", 0)
                segs = r[key]
                if idx >= len(segs) or -idx > len(segs):
                    results.append(_check(cid, False, f"ray found only {len(segs)} {key} segment(s)", ray=r))
                    continue
                v = segs[idx]["length"]
                lo, hi = chk["nominal"] - chk.get("tol_minus", 0.1), chk["nominal"] + chk.get("tol_plus", 0.1)
                results.append(_check(cid, lo <= v <= hi, f"ray {key}[{idx}] = {v} in [{lo:.3f}, {hi:.3f}]", measured=v))
            elif t == "clearance":
                mate = measure.load(pdir / "build" / "mates" / f"{chk['mate']}.step")
                c = measure.clearance(s, mate)
                ok = c["interference_mm3"] < 1e-3 and chk.get("min", 0) - 1e-6 <= c["min_distance"] <= chk.get("max", 1e9) + 1e-6
                results.append(_check(cid, ok, f"gap to {chk['mate']} = {c['min_distance']} (want {chk.get('min', 0)}..{chk.get('max', 'inf')}), interference {c['interference_mm3']} mm3"))
            elif t == "min_wall":
                w = measure.min_wall(s)
                results.append(_check(cid, w.get("min_thickness", 0) >= chk["value"] - 1e-3,
                                      f"min sampled wall {w.get('min_thickness')} >= {chk['value']}", where=w.get("thinnest_points")))
            else:
                results.append(_check(cid, False, f"unknown check type '{t}'"))
        except Exception as exc:
            results.append(_check(cid, False, f"check errored: {exc!r}"))

    build_checks = [dict(c, part=n) for n, p in report["parts"].items() for c in p["checks"]]
    failed = [c for c in build_checks + results if not c["pass"] and c["severity"] == "fail"]
    out = {"kind": "auto", "created": _now(), "status": "FAIL" if failed else "PASS",
           "build_checks": build_checks, "spec_checks": results, "artifacts": artifacts(pdir)}
    _write_json(pdir / "verification" / "auto.json", out)
    return out


def run_printability(project) -> dict:
    from cad_tools.printability import analyze

    pdir = resolve(project)
    spec = load_spec(pdir)
    report = json.loads((pdir / "build" / "report.json").read_text())
    res = {"kind": "printability_auto", "created": _now(), "parts": {}, "artifacts": artifacts(pdir)}
    for name in report["parts"]:
        res["parts"][name] = analyze(pdir / "build" / f"{name}.step", pdir / "build" / f"{name}.stl",
                                     printer=report["printer"], nozzle=spec.get("nozzle", 0.4))
    sts = {p["status"] for p in res["parts"].values()}
    res["status"] = "FAIL" if "FAIL" in sts else "WARN" if "WARN" in sts else "PASS"
    _write_json(pdir / "verification" / "printability_auto.json", res)
    return res


# ----------------------------------------------------------------- attest

def attest(project, kind, input_file) -> dict:
    """Record an independent verifier's result. Pass/fail is COMPUTED here from
    spec tolerances; the verifier only supplies measurements and evidence."""
    pdir = resolve(project)
    spec = load_spec(pdir)
    data = json.loads(Path(input_file).read_text())
    rec = {"kind": kind, "created": _now(), "verifier": data.get("verifier", "unknown"),
           "notes": data.get("notes", ""), "artifacts": artifacts(pdir)}
    problems = []

    if kind == "dimensions":
        crit = {c["id"]: c for c in spec.get("critical_dimensions", []) if not c["id"].startswith("_")}
        meas = {m["id"]: m for m in data.get("measurements", [])}
        rows = []
        for cid, c in crit.items():
            m = meas.get(cid)
            if m is None or m.get("measured") is None:
                rows.append({"id": cid, "pass": False, "message": "not measured"})
                problems.append(f"{cid}: not measured")
                continue
            lo, hi = c["nominal"] - c.get("tol_minus", 0.1), c["nominal"] + c.get("tol_plus", 0.1)
            ok = lo - 1e-6 <= float(m["measured"]) <= hi + 1e-6
            rows.append({"id": cid, "description": c.get("description"), "nominal": c["nominal"],
                         "range": [round(lo, 4), round(hi, 4)], "measured": m["measured"],
                         "method": m.get("method", ""), "evidence": m.get("evidence", ""), "pass": ok})
            if not ok:
                problems.append(f"{cid}: measured {m['measured']} outside [{lo:.3f}, {hi:.3f}]")
        for e in data.get("extra_checks", []):
            lo, hi = e["nominal"] - e.get("tol_minus", 0.1), e["nominal"] + e.get("tol_plus", 0.1)
            ok = lo - 1e-6 <= float(e["measured"]) <= hi + 1e-6
            rows.append({**e, "range": [lo, hi], "pass": ok, "extra": True})
            if not ok:
                problems.append(f"extra {e.get('id')}: {e['measured']} outside [{lo:.3f}, {hi:.3f}]")
        vis = data.get("visual", [])
        feats = [f for f in spec.get("features", []) if not f.startswith("Visually verifiable")]
        if feats and len(vis) < len(feats):
            problems.append(f"visual check covers {len(vis)} of {len(feats)} spec features")
        for v in vis:
            if not v.get("ok"):
                problems.append(f"visual: {v.get('feature')}: {v.get('evidence', '')}")
        rec.update(measurements=rows, visual=vis)
    elif kind == "printability":
        issues = data.get("issues", [])
        auto_f = pdir / "verification" / "printability_auto.json"
        if not auto_f.exists():
            problems.append("printability_auto.json missing: run `cad printability` first")
        else:
            auto = json.loads(auto_f.read_text())
            waived = {w["check"]: w.get("reason", "") for w in data.get("waive", [])}
            for pname, p in auto["parts"].items():
                for f in p["findings"]:
                    if f["severity"] == "fail" and f["check"] not in waived:
                        problems.append(f"{pname}: auto {f['check']}: {f['message']}")
            rec["waived"] = waived
        for i in issues:
            if i.get("severity") == "fail":
                problems.append(f"reviewer: {i.get('message')}")
        rec.update(issues=issues, orientation=data.get("orientation", ""),
                   print_settings=data.get("print_settings", {}))
        warns = [i for i in issues if i.get("severity") == "warn"]
        rec["status"] = "FAIL" if problems else ("WARN" if warns else "PASS")
    else:
        raise ValueError("kind must be 'dimensions' or 'printability'")

    rec.setdefault("status", "FAIL" if problems else "PASS")
    rec["problems"] = problems
    _write_json(pdir / "verification" / f"{kind}.json", rec)
    return rec


# ----------------------------------------------------------------- status / release

def status(project) -> dict:
    pdir = resolve(project)
    cur = artifacts(pdir) if (pdir / "build").exists() else {}
    st = {"project": pdir.name, "built": bool(cur), "gates": {}}
    rep = pdir / "build" / "report.json"
    if rep.exists():
        st["gates"]["build"] = json.loads(rep.read_text())["status"]
    for kind in ("auto", "printability_auto", "dimensions", "printability"):
        f = pdir / "verification" / f"{kind}.json"
        if not f.exists():
            st["gates"][kind] = "MISSING"
            continue
        rec = json.loads(f.read_text())
        stale = rec.get("artifacts") != cur
        st["gates"][kind] = "STALE" if stale else rec["status"]
    return st


def release(project) -> dict:
    pdir = resolve(project)
    st = status(project)
    g = st["gates"]
    blockers = []
    if g.get("build") != "PASS":
        blockers.append(f"build: {g.get('build', 'MISSING')}")
    if g.get("auto") != "PASS":
        blockers.append(f"auto checks: {g.get('auto')} (run `cad verify`)")
    if g.get("printability_auto") in ("MISSING", "STALE"):
        blockers.append(f"printability analysis: {g.get('printability_auto')} (run `cad printability`)")
    if g.get("dimensions") != "PASS":
        blockers.append(f"independent dimension verification: {g.get('dimensions')}")
    if g.get("printability") not in ("PASS", "WARN"):
        blockers.append(f"independent printability review: {g.get('printability')}")
    if blockers:
        return {"released": False, "blockers": blockers, "status": st}

    rel = pdir / "release"
    if rel.exists():
        shutil.rmtree(rel)
    rel.mkdir()
    report = json.loads((pdir / "build" / "report.json").read_text())
    copied = []
    for name, p in report["parts"].items():
        for key in ("step", "stl", "3mf", "views_svg", "views_png", "sections_png"):
            if key in p["files"]:
                src = pdir / p["files"][key]
                shutil.copy2(src, rel / src.name)
                copied.append(str((rel / src.name).relative_to(ROOT if rel.is_relative_to(ROOT) else pdir)))
    shutil.copy2(model_script(pdir), rel / model_script(pdir).name)
    pr = json.loads((pdir / "verification" / "printability.json").read_text())
    dims = json.loads((pdir / "verification" / "dimensions.json").read_text())
    md = [f"# Release: {pdir.name}", "", f"Released {_now()}. Every file below passed:", "",
          "- automatic geometry checks (valid BREP, single solid, watertight STL, STL=STEP volume, bed fit, spec checks)",
          f"- independent dimension verification by `{dims.get('verifier')}`",
          f"- independent printability review by `{pr.get('verifier')}` ({pr['status']})", "",
          "## Critical dimensions", "", "| id | nominal | allowed | measured | ok |", "|---|---|---|---|---|"]
    for m in dims.get("measurements", []):
        md.append(f"| {m['id']} | {m.get('nominal', '')} | {m.get('range', '')} | {m.get('measured', '')} | {'yes' if m['pass'] else 'NO'} |")
    warns = [i for i in pr.get("issues", []) if i.get("severity") == "warn"]
    if warns:
        md += ["", "## Print warnings", ""] + [f"- {w['message']}" for w in warns]
    if pr.get("orientation"):
        md += ["", "## Print orientation", "", pr["orientation"]]
    if pr.get("print_settings"):
        md += ["", "## Suggested print settings", ""] + [f"- {k}: {v}" for k, v in pr["print_settings"].items()]
    md += ["", "## Parts", ""]
    for name, p in report["parts"].items():
        bb = p["bbox"]["size"]
        md.append(f"- **{name}**: {bb[0]} x {bb[1]} x {bb[2]} mm, ~{p['mass_g']} g ({report['material']})")
    md += ["", "## SHA-256", ""] + [f"- `{k}` {v[:16]}" for k, v in artifacts(pdir).items()]
    (rel / "RELEASE.md").write_text("\n".join(md) + "\n")
    return {"released": True, "dir": str(rel), "files": copied, "status": st}
