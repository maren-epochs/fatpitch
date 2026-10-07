"""Registry <-> process.md cross-reference: ids never referenced in process.md
(orphans) and backticked dotted ids in process.md missing from the registry."""
import re, pathlib
from fatpitch.registry import load_default
root = pathlib.Path(__file__).resolve().parents[2]
reg = load_default()
text = (root / "spec" / "process.md").read_text(encoding="utf-8")
ids = [p.id for p in reg.parameters]
globs = [re.compile("^" + re.escape(g).replace(r"\*", "[a-z0-9_]+") + "$")
         for g in re.findall(r"`([a-z_]+\.[a-z0-9_.]*\*[a-z0-9_.]*)`", text)]
orphans = [i for i in ids if i not in text and not any(g.match(i) for g in globs)]
cited = set(re.findall(r"`([a-z_]+\.[a-z0-9_.]+)`", text))
missing = sorted(c for c in cited if c not in set(ids) and not c.endswith((".md", ".yaml", ".py")))
print(f"sha={reg.sha256} params={len(reg)} tunable={len(reg.tunable)}")
print("orphans:", orphans)
print("unknown ids in process.md:", missing)
