"""`cad` command line. Run as `./bin/cad <cmd>` or `python -m cad_tools <cmd>`.

Pipeline:  new -> (research) -> build -> verify + printability -> attest x2 -> release
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import warnings

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # `cad ... | head` exits quietly

warnings.filterwarnings("ignore")


def _vec(s):
    return tuple(float(x) for x in s.split(","))


def _print(obj, as_json):
    if as_json or not isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=2, default=str) if not isinstance(obj, str) else obj)
    else:
        print(json.dumps(obj, indent=2, default=str))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cad", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="scaffold projects/<name>/ with spec.json + model template")
    p.add_argument("name")

    p = sub.add_parser("lookup", help="search the built-in reference dimension database")
    p.add_argument("query", nargs="*")
    p.add_argument("--json", action="store_true")

    sub.add_parser("printers", help="list printer profiles")

    p = sub.add_parser("build", help="run the model, export STEP/STL/3MF, renders, automatic checks")
    p.add_argument("project")
    p.add_argument("--no-render", action="store_true")

    p = sub.add_parser("verify", help="automatic + spec.json checks on the exported STEP")
    p.add_argument("project")

    p = sub.add_parser("printability", help="FDM printability analysis (overhangs, bridges, walls, bed)")
    p.add_argument("project")

    p = sub.add_parser("attest", help="record an independent verifier's result (status is computed)")
    p.add_argument("project")
    p.add_argument("--kind", required=True, choices=["dimensions", "printability"])
    p.add_argument("--input", required=True, help="JSON file written by the verifier agent")

    p = sub.add_parser("status", help="show gate status (MISSING/STALE/PASS/FAIL)")
    p.add_argument("project")

    p = sub.add_parser("release", help="copy files to release/ only if every gate passed")
    p.add_argument("project")

    m = sub.add_parser("measure", help="virtual caliper on a STEP file")
    msub = m.add_subparsers(dest="what", required=True)
    q = msub.add_parser("bbox"); q.add_argument("file")
    q = msub.add_parser("holes"); q.add_argument("file")
    q.add_argument("--min-d", type=float, default=0.0); q.add_argument("--max-d", type=float, default=1e9)
    q.add_argument("--kind", choices=["hole", "boss"])
    q = msub.add_parser("ray"); q.add_argument("file")
    q.add_argument("--from", dest="origin", type=_vec, required=True, help="x,y,z")
    q.add_argument("--dir", dest="direction", type=_vec, required=True, help="dx,dy,dz")
    q = msub.add_parser("section"); q.add_argument("file")
    q.add_argument("--plane", default="XY", choices=["XY", "XZ", "YZ", "xy", "xz", "yz"])
    q.add_argument("--at", type=float, default=0.0)
    q.add_argument("--png", help="also render the cut to this PNG")
    q = msub.add_parser("clearance"); q.add_argument("file"); q.add_argument("other")
    q = msub.add_parser("walls"); q.add_argument("file")
    q.add_argument("--threshold", type=float, default=0.8)

    a = ap.parse_args(argv)
    from cad_tools import pipeline as P

    if a.cmd == "new":
        d = P.new_project(a.name)
        print(f"created {d}\n  edit {d/'spec.json'} then {d/(a.name + '.py')}")
    elif a.cmd == "lookup":
        from cad_tools import reference
        res = reference.search(" ".join(a.query))
        if a.json:
            _print(res, True)
        else:
            print(reference.format_results(res))
    elif a.cmd == "printers":
        from cad_tools.printers import PRINTERS
        for k, (n, v) in PRINTERS.items():
            print(f"{k:16s} {n:32s} {v[0]} x {v[1]} x {v[2]}")
    elif a.cmd == "build":
        rep = P.build(a.project, render=not a.no_render)
        print(P.format_build(rep))
        return 0 if rep["status"] == "PASS" else 1
    elif a.cmd == "verify":
        r = P.run_spec_checks(a.project)
        for c in r["build_checks"] + r["spec_checks"]:
            mark = "PASS" if c["pass"] else ("WARN" if c["severity"] == "warn" else "FAIL")
            print(f"[{mark}] {c.get('part', '')} {c['id']}: {c['message']}")
        print(f"\nauto verification: {r['status']}  -> verification/auto.json")
        return 0 if r["status"] == "PASS" else 1
    elif a.cmd == "printability":
        r = P.run_printability(a.project)
        for name, p in r["parts"].items():
            print(f"== {name}: {p['status']}")
            m = p["metrics"]
            print(f"   bed contact {m['bed_contact_mm2']} mm2, overhang {m['overhang_area_mm2']} mm2, "
                  f"min wall {m['walls'].get('min_thickness')} mm, height {m['height']}")
            for f in p["findings"]:
                print(f"   [{f['severity'].upper()}] {f['check']}: {f['message']}")
        print(f"\nprintability analysis: {r['status']}  -> verification/printability_auto.json")
    elif a.cmd == "attest":
        r = P.attest(a.project, a.kind, a.input)
        print(f"{a.kind} attestation: {r['status']}")
        for pr in r["problems"]:
            print(f"  - {pr}")
        return 0 if r["status"] in ("PASS", "WARN") else 1
    elif a.cmd == "status":
        st = P.status(a.project)
        for k, v in st["gates"].items():
            print(f"{k:20s} {v}")
    elif a.cmd == "release":
        r = P.release(a.project)
        if not r["released"]:
            print("RELEASE BLOCKED:")
            for b in r["blockers"]:
                print(f"  - {b}")
            return 2
        print(f"released to {r['dir']}")
        for f in r["files"]:
            print(f"  {f}")
    elif a.cmd == "measure":
        from cad_tools import measure as M
        s = M.load(a.file)
        if a.what == "bbox":
            _print(M.bbox(s), True)
        elif a.what == "holes":
            hs = M.holes(s, a.min_d, a.max_d)
            if a.kind:
                hs = [h for h in hs if h["kind"] == a.kind]
            for h in hs:
                print(f"{h['kind']:4s} Ø{h['diameter']:<8} axis {h['axis']} from {h['axis_start']} "
                      f"to {h['axis_end']} len {h['length']} sweep {h['sweep_deg']}°")
            print(f"({len(hs)} cylindrical features; sweep<360 = partial: fillet/slot/cut)")
        elif a.what == "ray":
            _print(M.ray(s, a.origin, a.direction), True)
        elif a.what == "section":
            r = M.section_loops(s, a.plane, a.at)
            r.pop("_sketch", None)
            _print(r, True)
            if a.png:
                from cad_tools.render import render_sections
                render_sections(s, a.png, cuts=[(a.plane.upper(), a.at)])
                print(f"png: {a.png}")
        elif a.what == "clearance":
            _print(M.clearance(s, M.load(a.other)), True)
        elif a.what == "walls":
            _print(M.min_wall(s, a.threshold), True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
