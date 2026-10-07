"""Pre-registration registry and run log (PLAN E.2, E.6).

Ported from multi-strategy ``cbp/research/prereg.py``. Changes: storage moved to
``<project>\\prereg\\preregistrations.csv`` and ``<project>\\prereg\\run_log.csv`` (project root
from env ``FATPITCH_ROOT``, else the source checkout); pandas removed (csv module); CBP reviewer and
provider strings generalised; ``count_runs`` added (DSR ``n_trials`` from the run log); ``register``
accepts several files via ``register_many`` (spec + transition table + corpus hash file).

Registry fields: id, design_file, sha256, design_commit, registered_utc, type (design | mechanical),
cited_text (mechanical only), tsa_token, ots_receipt, reviewer.

Mechanical-fix rule: a change is mechanical only if it makes code match already-written text and
cites that text (file and line). A fix to an error in the spec itself is a design change and
requires re-registration.

Run log: every ``record_run`` call appends UTC time, module, args, git SHA, dirty flag, prereg id and
sha256 (16 hex) of each output. Analyses run outside logged entry points are not detected; rule:
every scoring run goes through a logged entry point.

    python -m fatpitch.prereg register spec\\process.md --type design
    python -m fatpitch.prereg verify PR-0001
    python -m fatpitch.prereg list
    python -m fatpitch.prereg manifest        # rewrite spec/corpus_manifest.txt from cases/
    python -m fatpitch.prereg pending         # print the E2 registration set and current hashes
    python -m fatpitch.prereg register-all    # register the E2 set in one step (after owner review)

E2 registration set (``PREREG_SET``): spec/process.md, spec/registry.yaml, spec/transition_table.yaml,
spec/corpus_manifest.txt (sha256 of every case file plus the corpus sha256 over sorted case files) and
spec/scoring.md (scoring rule, nulls, permutation test, gates) and cases/HOLDOUT.yaml (sealed research/holdout
split, spec/HOLDOUT.md). ``register_all`` refuses to run when the manifest is stale or the parameter registry
fails validation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def project_root() -> Path:
    env = os.environ.get("FATPITCH_ROOT")
    return Path(env) if env else Path(__file__).resolve().parents[2]


ROOT = project_root()
REGISTRY = ROOT / "prereg" / "preregistrations.csv"
RUN_LOG = ROOT / "prereg" / "run_log.csv"
FIELDS = ["id", "design_file", "sha256", "design_commit", "registered_utc", "type", "cited_text",
          "tsa_token", "ots_receipt", "reviewer"]
RUN_FIELDS = ["utc", "module", "args", "git_sha", "dirty", "prereg_id", "outputs"]


class PreregError(RuntimeError):
    pass


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git(*args, root: Path = ROOT) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _ts(s: str) -> datetime:
    t = datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=UTC)


def read_registry(registry: Path = REGISTRY) -> list[dict]:
    if not Path(registry).exists():
        return []
    with open(registry, newline="", encoding="utf-8") as f:
        return [{k: (v or "") for k, v in row.items()} for row in csv.DictReader(f)]


def _append(path: Path, fields: list[str], row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerow(row)


def register(design_file: str, kind: str = "design", cited_text: str = "", commit: str | None = None,
             registry: Path = REGISTRY, when: str | None = None, root: Path = ROOT) -> str:
    if kind not in ("design", "mechanical"):
        raise PreregError(f"type must be design | mechanical, got {kind!r}")
    if kind == "mechanical" and not cited_text.strip():
        raise PreregError("a mechanical fix must cite the spec text it implements (file and line)")
    path = Path(design_file) if Path(design_file).is_absolute() else Path(root) / design_file
    if not path.is_file():
        raise PreregError(f"design file not found: {path}")
    rid = f"PR-{len(read_registry(registry)) + 1:04d}"
    row = {"id": rid, "design_file": design_file, "sha256": sha256_file(path),
           "design_commit": commit or _git("log", "-1", "--format=%h", "--", design_file, root=root),
           "registered_utc": when or datetime.now(UTC).isoformat(timespec="seconds"),
           "type": kind, "cited_text": cited_text, "tsa_token": "PENDING (provider not chosen)",
           "ots_receipt": "PENDING (provider not chosen)", "reviewer": "automated check - not independent review"}
    _append(Path(registry), FIELDS, row)
    return rid


def register_many(files: list[str], **kw) -> list[str]:
    return [register(f, **kw) for f in files]


def verify(rid: str, run_start_utc: str | None = None, registry: Path = REGISTRY, root: Path = ROOT) -> dict:
    """Design file unchanged since registration, and registration earlier than the run start."""
    rows = [r for r in read_registry(registry) if r["id"] == rid]
    if not rows:
        raise PreregError(f"{rid} is not registered")
    row = rows[0]
    f = Path(row["design_file"])
    f = f if f.is_absolute() else Path(root) / f
    if not f.is_file() or sha256_file(f) != row["sha256"]:
        raise PreregError(f"{rid}: {row['design_file']} changed after registration (hash mismatch)")
    if run_start_utc and _ts(row["registered_utc"]) >= _ts(run_start_utc):
        raise PreregError(f"{rid}: registered at {row['registered_utc']}, not before the run start {run_start_utc}")
    return row


def record_run(module: str, args: str, outputs: list, log: Path = RUN_LOG, prereg_id: str = "",
               root: Path = ROOT) -> dict:
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no", root=root).replace("unknown", ""))
    row = {"utc": datetime.now(UTC).isoformat(timespec="seconds"), "module": module, "args": args,
           "git_sha": _git("rev-parse", "--short", "HEAD", root=root), "dirty": dirty, "prereg_id": prereg_id,
           "outputs": ";".join(f"{Path(o).name}={sha256_file(o)[:16]}" for o in outputs if Path(o).exists())}
    _append(Path(log), RUN_FIELDS, row)
    return row


def read_run_log(log: Path = RUN_LOG) -> list[dict]:
    if not Path(log).exists():
        return []
    with open(log, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_runs(module: str | None = None, log: Path = RUN_LOG) -> int:
    """Logged runs (of ``module``, or all): the DSR ``n_trials`` input."""
    return sum(1 for r in read_run_log(log) if module is None or r["module"] == module)


def posthoc_flags(rid: str, module: str, registry: Path = REGISTRY, log: Path = RUN_LOG) -> list[str]:
    """Runs of ``module`` logged before the registration time (flag 'post-hoc risk')."""
    rows = [r for r in read_registry(registry) if r["id"] == rid]
    if not rows:
        raise PreregError(f"{rid} is not registered")
    reg_time = _ts(rows[0]["registered_utc"])
    return [f"post-hoc risk: {module} ran at {r['utc']} before {rid} was registered"
            for r in read_run_log(log) if r["module"] == module and _ts(r["utc"]) < reg_time]


PREREG_SET = ["spec/process.md", "spec/registry.yaml", "spec/transition_table.yaml", "spec/corpus_manifest.txt",
              "spec/scoring.md", "cases/HOLDOUT.yaml"]
MANIFEST = "spec/corpus_manifest.txt"


def corpus_manifest_text(root: Path = ROOT) -> str:
    """Manifest of ``cases/``: one ``<sha256>  cases/<file>`` line per case file (sorted), then
    ``corpus_sha256 <hex>`` over every case file (``fatpitch.cases.schema.corpus_sha256``; ``HOLDOUT.yaml`` is not
    a case file). The research split is validated by ``load_corpus`` (which also runs the holdout tamper check);
    sealed holdout files are hashed but not parsed beyond ``episode_id`` (spec/HOLDOUT.md)."""
    from fatpitch.cases import load_corpus
    from fatpitch.cases.holdout import case_files, full_digest

    cases = Path(root) / "cases"
    load_corpus(cases)
    n_cases, n_episodes, sha = full_digest(cases)
    lines = [f"{sha256_file(f)}  cases/{f.relative_to(cases).as_posix()}" for f in case_files(cases)]
    return "\n".join(["# fatpitch case corpus manifest (generated by `python -m fatpitch.prereg manifest`)",
                      f"# cases {n_cases} episodes {n_episodes}", *lines, f"corpus_sha256 {sha}", ""])


def write_corpus_manifest(root: Path = ROOT) -> Path:
    out = Path(root) / MANIFEST
    out.write_bytes(corpus_manifest_text(root).encode("utf-8"))
    return out


def pending(root: Path = ROOT) -> list[tuple[str, str]]:
    """``(file, sha256)`` for every file in ``PREREG_SET`` (current contents)."""
    return [(f, sha256_file(Path(root) / f)) for f in PREREG_SET]


def register_all(root: Path = ROOT, registry: Path = REGISTRY, commit: str | None = None) -> list[str]:
    """Register the E2 set in one step. Checks first: the manifest matches ``cases/`` and the
    parameter registry validates with citations resolved. Returns the new registration ids."""
    from fatpitch import registry as _reg

    man = Path(root) / MANIFEST
    if not man.is_file() or man.read_text(encoding="utf-8") != corpus_manifest_text(root):
        raise PreregError(f"{MANIFEST} is missing or stale; run `python -m fatpitch.prereg manifest` and review")
    _reg.load(Path(root) / "spec" / "registry.yaml", root=root)
    for f in PREREG_SET:
        if not (Path(root) / f).is_file():
            raise PreregError(f"missing registration file {f}")
    return register_many(PREREG_SET, registry=registry, root=root, commit=commit)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="fatpitch pre-registration registry")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register")
    r.add_argument("file")
    r.add_argument("--type", default="design")
    r.add_argument("--cite", default="")
    r.add_argument("--commit")
    v = sub.add_parser("verify")
    v.add_argument("id")
    sub.add_parser("list")
    sub.add_parser("manifest")
    sub.add_parser("pending")
    sub.add_parser("register-all")
    a = ap.parse_args(argv)
    if a.cmd == "register":
        print(register(a.file, a.type, a.cite, a.commit))
    elif a.cmd == "verify":
        print(verify(a.id))
    elif a.cmd == "manifest":
        print(write_corpus_manifest())
    elif a.cmd == "pending":
        for f, h in pending():
            print(f"{f}  {h}")
    elif a.cmd == "register-all":
        for rid, f in zip(register_all(), PREREG_SET, strict=True):
            print(f"{rid}  {f}")
    else:
        for row in read_registry():
            print(" | ".join(row[k] for k in ("id", "design_file", "sha256", "registered_utc", "type")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
