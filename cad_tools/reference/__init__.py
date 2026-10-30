"""Built-in reference dimensions + researched-object cache.

Curated files (data/*.json) were verified against primary sources; every entry
carries `source_urls` and `confidence`. Objects researched online by the
cad-dimension-researcher agent are cached in data/researched/<id>.json so the
next lookup is instant (marked "researched", not curated).

    cad lookup raspberry pi 5
    cad lookup ruthex m3
    cad lookup 608 bearing
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DATA = Path(__file__).parent / "data"


def _tokens(s):
    return set(re.findall(r"[a-z0-9.]+", s.lower().replace("_", " ").replace("-", " ")))


def entries():
    """Yield (id, title, payload, file, kind) for every searchable record."""
    for f in sorted(DATA.glob("*.json")):
        d = json.loads(f.read_text())
        if "boards" in d:
            for k, v in d["boards"].items():
                yield k, v.get("name", k), v, f.name, "curated"
        for gk, g in d.get("groups", {}).items():
            yield gk, gk, g, f.name, "curated"
            data = g.get("data", {}) if isinstance(g, dict) else {}
            if isinstance(data, dict):
                for ik, iv in data.items():
                    payload = {"group": gk, "item": ik, "value": iv,
                               "source_urls": g.get("source_urls"), "confidence": g.get("confidence"),
                               "notes": g.get("notes")}
                    title = iv.get("name", f"{gk} {ik}") if isinstance(iv, dict) else f"{gk} {ik}"
                    yield f"{gk}/{ik}", title, payload, f.name, "curated"
        for k, v in d.get("items", {}).items():
            yield k, v.get("name", k), v, f.name, "curated"
    for f in sorted((DATA / "researched").glob("*.json")):
        v = json.loads(f.read_text())
        yield v.get("id", f.stem), v.get("name", f.stem), v, f"researched/{f.name}", "researched"


def search(query: str, limit: int = 8):
    q = _tokens(query)
    if not q:
        return [{"id": i, "title": t, "file": f, "kind": k} for i, t, _, f, k in entries()]
    scored = []
    for i, t, payload, f, kind in entries():
        aliases = " ".join(payload.get("aliases", [])) if isinstance(payload, dict) else ""
        hay = _tokens(f"{i} {t} {aliases}")
        hit = len(q & hay)
        # partial token match ("pi5" vs "pi 5", "m3" inside "m3_short")
        hit += 0.5 * sum(1 for a in q for b in hay if a != b and (a in b or b in a) and len(a) > 1)
        if hit:
            exact = 1 if hay == q else 0
            scored.append((hit + exact - 0.01 * len(hay), i, t, payload, f, kind))
    scored.sort(key=lambda r: -r[0])
    return [{"id": i, "title": t, "file": f, "kind": k, "data": p} for _, i, t, p, f, k in scored[:limit]]


def get(entry_id: str):
    for i, _, payload, _, _ in entries():
        if i == entry_id:
            return payload
    raise KeyError(entry_id)


def save_researched(entry: dict) -> Path:
    """Cache an object researched online. Required: id, name, dimensions, sources, confidence."""
    for key in ("id", "name", "dimensions", "sources", "confidence"):
        if key not in entry:
            raise ValueError(f"researched entry missing '{key}'")
    f = DATA / "researched" / f"{re.sub(r'[^a-z0-9_]+', '_', entry['id'].lower())}.json"
    f.write_text(json.dumps(entry, indent=1))
    return f


def format_results(results) -> str:
    if not results:
        return "no match in the reference database -> research it online (cad-dimension-researcher)"
    out = []
    for r in results:
        out.append(f"== {r['id']}  [{r['kind']}, {r['file']}]  {r['title']}")
        d = r.get("data")
        if isinstance(d, dict):
            for k, v in d.items():
                line = json.dumps(v) if not isinstance(v, str) else v
                out.append(f"   {k}: {line if len(line) < 600 else line[:600] + ' ...(use --json)'}")
    return "\n".join(out)
