"""Run a spec version (git tag) or the working tree on the research split and score it with the current code.

Flow of ``run_version(ref)``:

1. Load the research split from the CURRENT checkout's ``cases\\`` (same cases for every version; holdout
   never unsealed) and record its sha256.
2. Make sure the four nulls are scored for that corpus sha (``run_nulls``, cached).
3. Materialise the version: a tag/ref is checked out into a temporary detached git worktree (removed after);
   ``WORKTREE`` uses the current working tree as an uncommitted candidate (label ``wip``).
4. Evaluate the version's OWN engine, spec and registry in a child interpreter (``driver.py``) with the
   version's ``src`` first on ``sys.path``, over amber's lake (``AmberSource``, ``AMBER_DATA``), on every
   window date of the research cases.
5. Map each Decision to a Prediction (``adapter``) and score with the CURRENT scoring code (``score``).
6. Write ``results\\versions\\<label>\\<run_id>\\`` (``predictions.parquet``, ``scores.json``, ``meta.json``,
   ``decisions.jsonl.gz``, ``driver_info.json``), append the trial log, rewrite the leaderboard.

Never touches ``fatpitch.prereg`` (no registration, no ``record_run``).
"""

from __future__ import annotations

import datetime as _dt
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import fatpitch
from fatpitch.cases import Corpus, load_corpus
from fatpitch.versions import gitops, score, trials
from fatpitch.versions.adapter import ADAPTER_VERSION, decision_to_prediction
from fatpitch.versions.nullsource import (
    BEST_NULL,
    NULL_NAMES,
    input_files,
    lake_stamp,
    null_engines,
    null_source,
)

DEFAULT_AMBER_DATA = r"C:\Users\<user>\Documents\amber\data"
SPEC_FILES = ("spec/process.md", "spec/registry.yaml", "spec/transition_table.yaml", "spec/scoring.md")


@dataclass
class Paths:
    repo: Path                 # current checkout (git ops, WORKTREE candidate)
    cases_root: Path           # corpus loaded with split="research"
    results: Path              # results\versions
    amber_data: Path

    @property
    def trials(self) -> Path:
        return self.results / "trials.jsonl"

    @property
    def leaderboard(self) -> Path:
        return self.results / "LEADERBOARD.md"


def default_paths(root: str | Path | None = None, amber_data: str | Path | None = None) -> Paths:
    root = Path(root) if root else Path(fatpitch.__file__).resolve().parents[2]
    amber = Path(amber_data or os.environ.get("AMBER_DATA") or DEFAULT_AMBER_DATA)
    return Paths(root, root / "cases", root / "results" / "versions", amber)


def safe_label(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", label)


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0)


def _run_id(now: _dt.datetime, commit: str) -> str:
    return f"{now.strftime('%Y%m%dT%H%M%SZ')}-{commit[:8]}"


def _sha(b: bytes | None) -> str | None:
    return None if b is None else hashlib.sha256(b).hexdigest()


def _write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def load_research(paths: Paths) -> Corpus:
    return load_corpus(paths.cases_root, split="research")


def corpus_meta(paths: Paths, corpus: Corpus) -> dict:
    return {"split": corpus.split, "sha256": corpus.sha256, "n_cases": len(corpus),
            "n_episodes": len(corpus.episodes), "root": str(paths.cases_root),
            "holdout_opened": (paths.cases_root / "UNSEAL_LOG.txt").exists(),
            "gate_ids": score.gate_ids(corpus)}


# -------------------------------------------------------------------- nulls


def nulls_dir(paths: Paths, corpus_sha: str) -> Path:
    return paths.results / "nulls" / corpus_sha[:16]


def fed_key(paths: Paths):
    from fatpitch.cases.fedcycles import load_fed_key
    return load_fed_key(paths.repo / "spec" / "fed_cycles.yaml")


def _nulls_current(d: Path, corpus_sha: str, scoring_sha: str, fed_sha: str | None = None) -> bool:
    for n in NULL_NAMES:
        m = d / n / "meta.json"
        if not (m.exists() and (d / n / "scores.json").exists()):
            return False
        meta = json.loads(m.read_text(encoding="utf-8"))
        if meta["corpus"]["sha256"] != corpus_sha or meta["scoring"]["sha256"] != scoring_sha \
                or meta.get("fed_key_sha256") != fed_sha:
            return False
    return True


def run_nulls(paths: Paths, force: bool = False, source=None, corpus: Corpus | None = None,
              quiet: bool = False) -> Path:
    """Score the four nulls on the research split; cached per corpus sha (re-run when the scoring code changes
    or ``force``). Returns the directory holding one sub-directory per null."""
    corpus = corpus or load_research(paths)
    fp = score.scoring_fingerprint()
    out = nulls_dir(paths, corpus.sha256)
    fed = fed_key(paths)
    fed_sha = None if fed is None else fed.sha256
    if not force and _nulls_current(out, corpus.sha256, fp["sha256"], fed_sha):
        if not quiet:
            print(f"nulls cached for corpus {corpus.sha256[:16]}: {out}")
        return out
    t0, started = time.time(), _utc_now()
    src = source if source is not None else null_source(paths.amber_data)
    dates = score.window_dates(corpus, fed)
    results = {}
    for eng in null_engines(corpus):
        table = score.record(eng, src, dates)
        results[eng.name] = (table, score.score(eng.name, table, corpus))
    best = results[BEST_NULL][1].case_scores
    null_refs = {n: score.rps_rows(corpus, results[n][0]) for n in score.GATE1_REFERENCES if n in results}
    fed_null = {n: score.fed_rows(fed, results[n][0]) for n in fc_refs() if n in results} if fed else None
    stamp = lake_stamp(input_files(paths.amber_data)) if source is None else {"note": "injected source"}
    for name, (table, res) in results.items():
        d = out / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        sj = score.scores_json(res, corpus, table, best, BEST_NULL, null_refs, fed, fed_null)
        score.predictions_frame(corpus, table).write_parquet(d / "predictions.parquet")
        _write_json(d / "scores.json", sj)
        meta = {"label": name, "kind": "null", "run_id": started.strftime("%Y%m%dT%H%M%SZ"),
                "corpus": corpus_meta(paths, corpus), "scoring": fp, "adapter_version": ADAPTER_VERSION,
                "run": {"started_utc": started.isoformat(), "seconds": round(time.time() - t0, 1),
                        "n_dates": len(dates), "fatpitch_version": fatpitch.__version__},
                "data": {"amber_data": str(paths.amber_data), "inputs": stamp,
                         "note": "null inputs per spec/scoring.md section 4 (fatpitch.versions.nullsource)"},
                "best_null": BEST_NULL, "gate1_references": list(score.GATE1_REFERENCES),
                "fed_key_sha256": fed_sha}
        _write_json(d / "meta.json", meta)
        trials.append(paths.trials, {"kind": "null", "label": name, "run_id": meta["run_id"],
                                     "timestamp_utc": started.isoformat(), "commit": fp["git"].get("head"),
                                     "registry_sha": None, "corpus_sha": corpus.sha256,
                                     "scoring_sha": fp["sha256"], "summary": score.summary(sj),
                                     "path": str(d.relative_to(paths.results))})
        if not quiet:
            s = score.summary(sj)
            print(f"{name:22s} gate1 RPS {_f(s['gate1_rps'])} binding {s['gate1_binding']} p {_f(s['gate1_binding_p'])} gate2 {_f(s['gate2_score'])} regime {_f(s['regime'])} "
                  f"thesis {_f(s['thesis'])} expression {_f(s['expression'])} action {_f(s['action'])}")
    return out


def fc_refs() -> tuple[str, ...]:
    """Null references of the Fed cycle check (the climatology reference is computed, not a null run)."""
    from fatpitch.cases.fedcycles import FED_REFERENCES
    return FED_REFERENCES[1:]


def _f(x) -> str:
    return "n/a" if x is None else f"{x:.3f}"


# -------------------------------------------------------------------- versions


def _run_driver(version_root: Path, dates: list[_dt.date], out_dir: Path, amber_data: Path) -> dict:
    version_src = version_root / "src"
    if not (version_src / "fatpitch" / "__init__.py").exists():
        raise FileNotFoundError(f"no fatpitch package under {version_src}")
    reg = version_root / "spec" / "registry.yaml"
    req = {"version_src": str(version_src), "version_root": str(version_root),
           "registry": str(reg) if reg.exists() else None, "amber_data": str(amber_data),
           "dates": [d.isoformat() for d in dates], "out_dir": str(out_dir)}
    req_path = out_dir / "driver_request.json"
    _write_json(req_path, req)
    env = dict(os.environ)
    env.update({"PYTHONPATH": str(version_src), "FATPITCH_ROOT": str(version_root), "AMBER_DATA": str(amber_data),
                "PYTHONIOENCODING": "utf-8"})
    driver = Path(__file__).resolve().parent / "driver.py"
    p = subprocess.run([sys.executable, "-X", "utf8", "-u", str(driver), str(req_path)], env=env,
                       cwd=str(version_root), stdout=subprocess.PIPE, stderr=None, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"version driver failed (exit {p.returncode}); see stderr above. "
                           f"stdout: {p.stdout.decode(errors='replace')[-2000:]}")
    return json.loads((out_dir / "driver_info.json").read_text(encoding="utf-8"))


def _read_decisions(out_dir: Path, dates: list[_dt.date]) -> dict:
    """Stream the driver output: each Decision line is mapped to a Prediction and released (low memory)."""
    out = {}
    it = iter(dates)
    with gzip.open(out_dir / "decisions.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            d = next(it, None)
            if d is None:
                raise RuntimeError(f"driver wrote more decisions than the {len(dates)} dates")
            out[d] = decision_to_prediction(json.loads(line))
    if len(out) != len(dates):
        raise RuntimeError(f"driver wrote {len(out)} decisions for {len(dates)} dates")
    return out


def _version_files(version_root: Path) -> dict:
    return {rel: _sha((version_root / rel).read_bytes()) if (version_root / rel).exists() else None
            for rel in SPEC_FILES}


def run_version(ref: str, paths: Paths | None = None, null_source_override=None, write_leaderboard: bool = True,
                quiet: bool = False) -> Path:
    """Run one version; returns its run directory. ``ref``: a git tag (or any commit-ish) or ``WORKTREE``."""
    paths = paths or default_paths()
    corpus = load_research(paths)
    ndir = run_nulls(paths, source=null_source_override, corpus=corpus, quiet=quiet)
    best = score.case_scores_from(json.loads((ndir / BEST_NULL / "scores.json").read_text(encoding="utf-8"))
                                  ["case_scores"])
    null_refs = {n: score.rps_from_json(json.loads((ndir / n / "scores.json").read_text(encoding="utf-8"))
                                        ["regime_rps"]) for n in score.GATE1_REFERENCES if (ndir / n).is_dir()}
    fed = fed_key(paths)
    fed_null = {n: score.fed_rows_from_json(json.loads((ndir / n / "scores.json").read_text(encoding="utf-8"))
                                            .get("fed_rows") or []) for n in fc_refs() if (ndir / n).is_dir()} \
        if fed else None
    fp = score.scoring_fingerprint()
    dates = score.window_dates(corpus, fed)
    started, t0 = _utc_now(), time.time()
    repo = gitops.toplevel(paths.repo)

    wip = ref == gitops.WIP
    if wip:
        commit, label, kind = gitops.head(repo), gitops.WIP_LABEL, "wip"
        ver = {"ref": ref, "commit": commit, "is_tag": False, "wip_fingerprint": gitops.wip_fingerprint(repo),
               "dirty_paths": gitops.dirty_paths(repo, ["src", "spec"])}
    else:
        commit, label, kind = gitops.resolve_commit(repo, ref), ref, "tag"
        ver = {"ref": ref, "commit": commit, "is_tag": gitops.is_tag(repo, ref), "wip_fingerprint": None,
               "dirty_paths": []}
    run_id = _run_id(started, commit)
    run_dir = paths.results / safe_label(label) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    try:
        if wip:
            version_root = repo
            info = _run_driver(version_root, dates, run_dir, paths.amber_data)
            ver["spec_files"] = _version_files(version_root)
        else:
            with gitops.worktree(repo, commit) as wt:
                ver["worktree"] = str(wt)
                info = _run_driver(wt, dates, run_dir, paths.amber_data)
                ver["spec_files"] = _version_files(wt)
        table = _read_decisions(run_dir, dates)
        res = score.score(label, table, corpus)
        sj = score.scores_json(res, corpus, table, best, BEST_NULL, null_refs, fed, fed_null)
        score.predictions_frame(corpus, table).write_parquet(run_dir / "predictions.parquet")
        _write_json(run_dir / "scores.json", sj)
        fred = sorted((paths.amber_data / "lake" / "fred" / "series").glob("*.parquet"))
        meta = {"label": label, "kind": kind, "run_id": run_id, "version": ver,
                "registry_sha": info.get("registry_sha"),
                "registry_file_sha256": ver["spec_files"].get("spec/registry.yaml"),
                "engine": info, "corpus": corpus_meta(paths, corpus), "scoring": fp,
                "adapter_version": ADAPTER_VERSION, "best_null": BEST_NULL,
                "gate1_references": list(score.GATE1_REFERENCES),
                "fed_key_sha256": None if fed is None else fed.sha256, "nulls_dir": str(ndir.relative_to(paths.results)),
                "run": {"started_utc": started.isoformat(), "finished_utc": _utc_now().isoformat(),
                        "seconds": round(time.time() - t0, 1), "n_dates": len(dates),
                        "runner_fatpitch_version": fatpitch.__version__, "python": sys.version.split()[0]},
                "data": {"amber_data": str(paths.amber_data),
                         "fred_series": {"n_files": len(fred), **lake_stamp(fred)},
                         "note": "engine reads through the version's own AmberSource; the stamp covers amber "
                                 "lake\\fred\\series (what AmberSource v0.1 reads); file names, sizes and mtimes, "
                                 "not contents"}}
        rec = trials.append(paths.trials, {
            "kind": kind, "label": label, "run_id": run_id, "timestamp_utc": started.isoformat(), "commit": commit,
            "wip_fingerprint": ver["wip_fingerprint"], "registry_sha": meta["registry_sha"],
            "corpus_sha": corpus.sha256, "scoring_sha": fp["sha256"], "summary": score.summary(sj),
            "path": str(run_dir.relative_to(paths.results))})
        meta["trial"] = rec["trial"]
        _write_json(run_dir / "meta.json", meta)
    except BaseException:
        shutil.rmtree(run_dir, ignore_errors=True)
        raise
    if write_leaderboard:
        from fatpitch.versions.compare import write_leaderboard as _wl
        _wl(paths, corpus)
    if not quiet:
        s = score.summary(sj)
        print(f"{label} {run_id} trial {rec['trial']}: gate1 RPS {_f(s['gate1_rps'])} pass {s['gate1_pass']} "
              f"binding {s['gate1_binding']} p {_f(s['gate1_binding_p'])} (k {s['gate1_k']}) "
              f"gate2 {_f(s['gate2_score'])} (p {_f(s['gate2_p'])}) regime {_f(s['regime'])} thesis {_f(s['thesis'])} "
              f"expression {_f(s['expression'])} action {_f(s['action'])}\n  -> {run_dir}")
    return run_dir
