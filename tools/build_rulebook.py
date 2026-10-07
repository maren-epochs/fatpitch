"""Build the Fat Pitch rulebook page from spec\\ and library\\.

Reads spec\\process.md, spec\\registry.yaml, spec\\transition_table.yaml, spec\\decisions.yaml and library front matter,
writes one self-contained HTML page (data embedded as JSON).

Usage: python tools\\build_rulebook.py <out.html>
"""

from __future__ import annotations

import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
LIB = {"DS": ROOT / "library" / "discovered_sources", "RS": ROOT / "library" / "reference_sources"}

ALIASES = {
    "Feig 2009": "DS/2009-XX-XX",
    "Sohn 2022": "DS/2022-06-XX",
    "NBIM 2024": "RS/2024-11-06",
    "NBIM 2023": "DS/2023-04-24",
    "Lost Tree": "RS/2015-01-18",
    "Real Vision": "RS/2018-09-06",
    "NMW": "RS/1992-XX-XX",
}


def inline_md(text: str) -> str:
    s = html.escape(text, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def library_index() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for d, path in LIB.items():
        for f in sorted(path.glob("*.md")):
            if f.name.startswith("_"):
                continue
            meta: dict = {}
            text = f.read_text(encoding="utf-8", errors="replace")
            m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
            if m:
                try:
                    meta = yaml.safe_load(m.group(1)) or {}
                except yaml.YAMLError:
                    meta = {}
            key = f"{d}/{f.name}"
            out[key] = {
                "key": key,
                "file": f.name,
                "dir": d,
                "date": f.name[:10],
                "title": str(meta.get("title") or f.stem[11:].replace("-", " ")),
                "type": str(meta.get("type") or ""),
                "venue": str(meta.get("venue/outlet") or meta.get("venue") or ""),
                "reliability": str(meta.get("reliability") or ""),
                "access": str(meta.get("access_status") or ""),
                "url": str(meta.get("primary_source_url") or meta.get("transcript_url") or ""),
            }
    return out


def resolve_refs(text: str, lib: dict[str, dict]) -> list[tuple[str, str]]:
    """Return [(library key, reliability marker)] for refs in a citation line."""
    found: list[tuple[str, str]] = []
    for alias, prefix in ALIASES.items():
        text = text.replace(alias, f"{prefix} ")
    for m in re.finditer(r"\b(DS|RS)/(\d{4}-[\dX]{2}-[\dX]{2})([\w\-\.]*?\.md)?(?:[^(]{0,40}?\((NP|P|S)\b)?", text):
        d, date, rest, rel = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        key = None
        if rest:
            cand = f"{d}/{date}{rest}"
            if cand in lib:
                key = cand
        if not key:
            matches = [k for k in lib if k.startswith(f"{d}/{date}")]
            key = matches[0] if matches else None
        if key and all(key != k for k, _ in found):
            found.append((key, rel))
    return found


def parse_md_table(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            continue
        rows.append([inline_md(c) for c in cells])
    return rows


def parse_process(lib: dict[str, dict]) -> dict:
    text = (SPEC / "process.md").read_text(encoding="utf-8")
    steps, rules, conflicts, gaps = [], [], [], []
    cur_step = None
    cur_rule = None
    section = None
    gap_sub = None
    for ln in text.splitlines():
        h2 = re.match(r"^## (\d+)\. (.+)$", ln)
        if h2:
            num, name = int(h2.group(1)), h2.group(2)
            cur_rule = None
            if name.startswith("Step"):
                sm = re.match(r"Step (\w+) — (.+)", name)
                cur_step = {"n": num, "code": sm.group(1), "name": sm.group(2), "intro": []}
                steps.append(cur_step)
                section = "step"
            elif "conflict" in name.lower():
                section, cur_step = "conflicts", None
            elif name.lower().startswith("gaps"):
                section, cur_step = "gaps", None
            else:
                section, cur_step = "other", None
            continue
        if section == "conflicts":
            conflicts.append(ln)
            continue
        if section == "gaps":
            h3g = re.match(r"^### [\d\.]+ (.+)$", ln)
            if h3g:
                gap_sub = {"title": h3g.group(1), "lines": []}
                gaps.append(gap_sub)
            elif gap_sub is not None:
                gap_sub["lines"].append(ln)
            continue
        if section != "step":
            continue
        h3 = re.match(r"^### (R-\d+) (.+?) — (.+)$", ln)
        if h3:
            tagtxt = h3.group(3)
            tags = re.findall(r"`([a-z\-]+)`", tagtxt)
            cur_rule = {
                "id": h3.group(1),
                "title": inline_md(h3.group(2)),
                "tag": tags[0] if tags else "interpreted",
                "tagNote": inline_md(re.sub(r"`[a-z\-]+`", "", tagtxt).strip(" /()")) if len(tagtxt) > 14 else "",
                "step": cur_step["code"],
                "fields": [],
                "sources": [],
            }
            rules.append(cur_rule)
            continue
        bm = re.match(r"^- ([A-Z][A-Za-z ]*(?:\([^)]*\))?): (.*)$", ln)
        if bm and cur_rule is not None:
            label, body = bm.group(1), bm.group(2)
            cur_rule["fields"].append({"label": html.escape(label), "html": inline_md(body)})
            if label.startswith("Cite"):
                for key, rel in resolve_refs(body, lib):
                    cur_rule["sources"].append({"key": key, "rel": rel})
            continue
        if ln.strip() and cur_step is not None and not ln.startswith("#"):
            target = cur_rule["fields"] if cur_rule is not None and not ln.startswith("`size_band`") else None
            if target is not None and ln.startswith("- "):
                target.append({"label": "", "html": inline_md(ln[2:])})
            else:
                cur_step["intro"].append(inline_md(ln))
    return {
        "steps": steps,
        "rules": rules,
        "conflicts": parse_md_table(conflicts),
        "gaps": [{"title": inline_md(g["title"]), "rows": parse_md_table(g["lines"])} for g in gaps],
    }


def main() -> None:
    out = Path(sys.argv[1])
    lib = library_index()
    proc = parse_process(lib)
    registry = yaml.safe_load((SPEC / "registry.yaml").read_text(encoding="utf-8"))
    transitions = yaml.safe_load((SPEC / "transition_table.yaml").read_text(encoding="utf-8"))
    used = {s["key"] for r in proc["rules"] for s in r["sources"]}
    dec_path = SPEC / "decisions.yaml"
    decisions = (yaml.safe_load(dec_path.read_text(encoding="utf-8")) or {}).get("decisions", []) if dec_path.exists() else []
    data = {
        "steps": proc["steps"],
        "rules": proc["rules"],
        "conflicts": proc["conflicts"],
        "gaps": proc["gaps"],
        "registry": [
            {k: (inline_md(str(v)) if isinstance(v, str) else v) for k, v in p.items()} for p in registry
        ],
        "transitions": transitions,
        "sources": {k: v for k, v in lib.items() if k in used},
        "decisions": decisions,
    }
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    template = (Path(__file__).parent / "rulebook_template.html").read_text(encoding="utf-8")
    built = _dt.date.today().isoformat()
    out.write_text(template.replace("__BUILT__", built).replace("__DATA__", payload), encoding="utf-8")
    print(f"rules {len(proc['rules'])}, params {len(registry)}, transitions {len(transitions)}, "
          f"sources cited {len(used)}, decisions {len(decisions)} -> {out}")


if __name__ == "__main__":
    main()
