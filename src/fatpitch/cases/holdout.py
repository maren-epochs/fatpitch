"""Research/holdout split of the case corpus (sealed holdout; ``spec/HOLDOUT.md``, ``spec/scoring.md`` section 9).

About one third of the episodes are sealed in ``cases/HOLDOUT.yaml`` by a seeded, stratified draw
(``draw``). Episodes are never split. ``fatpitch.cases.load_corpus`` returns the research split by default;
the holdout (``split="holdout"``) or the full corpus (``split="all"``) loads only with ``unseal=True``, the
environment variable ``FATPITCH_UNSEAL=1`` and a non-empty ``reason``; every unseal appends one line to
``cases/UNSEAL_LOG.txt``. Every load recomputes the holdout hash and raises ``HoldoutError`` when it differs
from ``HOLDOUT.yaml`` (tamper check). A research load reads only the ``episode_id`` of holdout files (to
partition) and their bytes (to hash); it never parses or returns their targets.

Hashes use ``fatpitch.cases.schema.corpus_sha256``: sha256 over sorted ``relative_path NUL sha256(file bytes)
LF`` lines, so a changed byte, an added, removed or renamed file, or a case moved into or out of a holdout
episode changes the hash.
"""

from __future__ import annotations

import datetime as _dt
import getpass
import math
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

from fatpitch.cases.schema import Case, CaseError, corpus_sha256, turning_point_ids

HOLDOUT_FILE = "HOLDOUT.yaml"
UNSEAL_LOG = "UNSEAL_LOG.txt"
UNSEAL_ENV = "FATPITCH_UNSEAL"
SEED = 20261006
FRACTION = 1 / 3
SPLITS = ("research", "holdout", "all")
REPO_CASES = Path(__file__).resolve().parents[3] / "cases"
METHOD = (
    "Episode-level draw, numpy.random.default_rng(seed); every list sorted before each draw. "
    "n_target = round(n_episodes / 3). "
    "(1) Gate 1 episodes (episodes with an era-A turning-point case with a regime target; turning points by "
    "turning_point_ids on the full corpus): ceil(n / 2) drawn by rng.permutation. "
    "(2) If exactly two episodes contain 13F cases (targets.tilt): exactly one is held out; if step 1 took "
    "none, one is drawn by rng.permutation; if it took both, the one drawn second by rng.permutation is "
    "returned to research and replaced by an undrawn non-13F Gate 1 episode drawn by rng.permutation. "
    "(3) If no held-out episode is era B (all cases era B), one era-B episode is drawn by rng.permutation. "
    "(4) The remaining episodes (13F episodes excluded when step 2 applied) are permuted and added in that "
    "order until n_target is reached. Hash: fatpitch.cases.schema.corpus_sha256."
)


class HoldoutError(CaseError):
    pass


# -------------------------------------------------------------------- files


def case_files(root: str | Path) -> list[Path]:
    """Case YAML files under ``root`` (``HOLDOUT.yaml`` excluded), sorted by relative path."""
    root = Path(root)
    files = [f for f in list(root.rglob("*.yaml")) + list(root.rglob("*.yml")) if f.name != HOLDOUT_FILE]
    return sorted(files, key=lambda f: f.relative_to(root).as_posix())


def episode_of(path: Path) -> str:
    """``episode_id`` of a case file without parsing or validating anything else."""
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or d.get("episode_id") is None:
        raise CaseError(f"{path.name}: missing episode_id")
    return str(d["episode_id"])


def full_digest(root: str | Path) -> tuple[int, int, str]:
    """``(n_cases, n_episodes, sha256)`` over every case file; reads episode ids and bytes only."""
    files = case_files(root)
    return len(files), len({episode_of(f) for f in files}), corpus_sha256(files, Path(root))


def read_spec(root: str | Path) -> dict | None:
    p = Path(root) / HOLDOUT_FILE
    if not p.is_file():
        return None
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(d, dict) or not d.get("holdout_episodes") or not d.get("holdout_sha256"):
        raise HoldoutError(f"{p}: malformed (holdout_episodes and holdout_sha256 required)")
    return d


def partition(root: str | Path, episodes) -> tuple[list[Path], list[Path]]:
    """``(research_files, holdout_files)``: a file is held out when its ``episode_id`` is in ``episodes``."""
    keep = set(episodes)
    research, hold = [], []
    for f in case_files(root):
        (hold if episode_of(f) in keep else research).append(f)
    return research, hold


def verify(root: str | Path, spec: dict | None = None) -> tuple[list[Path], list[Path], str]:
    """Tamper check. Returns ``(research_files, holdout_files, holdout_sha256)``; raises ``HoldoutError`` when
    the holdout files' hash differs from ``HOLDOUT.yaml``."""
    root = Path(root)
    spec = spec or read_spec(root)
    if spec is None:
        raise HoldoutError(f"{root / HOLDOUT_FILE} not found")
    research, hold = partition(root, spec["holdout_episodes"])
    sha = corpus_sha256(hold, root)
    if sha != spec["holdout_sha256"]:
        raise HoldoutError(f"holdout hash mismatch: files {sha} != {HOLDOUT_FILE} {spec['holdout_sha256']}; "
                           "the sealed holdout was modified (tamper check). Restore the files; do not re-seal "
                           "after the holdout has been seen")
    return research, hold, sha


def authorize_unseal(root: str | Path, split: str, unseal: bool, reason: str | None, sha: str) -> Path:
    """Checks the three unseal conditions and appends one line to ``UNSEAL_LOG.txt``."""
    if not unseal:
        raise HoldoutError(f"split={split!r} is sealed; pass unseal=True (with {UNSEAL_ENV}=1 and a reason)")
    if os.environ.get(UNSEAL_ENV) != "1":
        raise HoldoutError(f"split={split!r} is sealed; environment variable {UNSEAL_ENV}=1 is not set")
    if not reason or not str(reason).strip():
        raise HoldoutError("unseal requires a non-empty reason")
    try:
        user = getpass.getuser()
    except Exception:  # noqa: BLE001 - no login name available
        user = "unknown"
    ts = _dt.datetime.now(_dt.UTC).isoformat(timespec="seconds")
    line = (f"{ts}\tuser={user}\tsplit={split}\tholdout_sha256={sha}\tsha_verified=yes\t"
            f"reason={' '.join(str(reason).split())}\n")
    log = Path(root) / UNSEAL_LOG
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
    return log


def select(root: str | Path, split: str = "research", unseal: bool = False,
           reason: str | None = None) -> tuple[list[Path], list[Path] | None, str]:
    """Files to load for ``split``: ``(files, turning_files, label)``. ``turning_files`` is the file set the
    turning points are derived on (None = ``files``): the research split derives them on research cases only
    (no holdout target can reach a research label); holdout and all derive them on the full corpus."""
    if split not in SPLITS:
        raise ValueError(f"split {split!r} not in {SPLITS}")
    root = Path(root)
    spec = read_spec(root)
    if spec is None:
        if root.resolve() == REPO_CASES.resolve():
            raise HoldoutError(f"{root / HOLDOUT_FILE} is missing: the project corpus must carry its sealed split")
        if split == "holdout":
            raise HoldoutError(f"no {HOLDOUT_FILE} in {root}: no holdout defined")
        return case_files(root), None, "unsplit"
    research, hold, sha = verify(root, spec)
    if split == "research":
        return research, None, "research"
    authorize_unseal(root, split, unseal, reason, sha)
    allf = sorted(research + hold, key=lambda f: f.relative_to(root).as_posix())
    return (hold if split == "holdout" else allf), allf, split


# -------------------------------------------------------------------- draw and counts


def gate1_ids(cases, turning: frozenset[str]) -> set[str]:
    """Era-A turning-point cases with a regime target (Gate 1 subset, spec/scoring.md section 7)."""
    return {c.id for c in cases if c.era == "A" and c.id in turning and c.targets.regime_direction is not None}


def _perm(rng: np.random.Generator, items) -> list[str]:
    items = sorted(items)
    return [items[i] for i in rng.permutation(len(items))]


def draw(cases: list[Case], seed: int = SEED, fraction: float = FRACTION) -> list[str]:
    """Held-out episode ids (sorted). Deterministic for given cases and seed; method in ``METHOD``."""
    turning = turning_point_ids(cases)
    by_ep: dict[str, list[Case]] = defaultdict(list)
    for c in cases:
        by_ep[c.episode_id].append(c)
    episodes = sorted(by_ep)
    g1_cases = gate1_ids(cases, turning)
    g1 = [e for e in episodes if any(c.id in g1_cases for c in by_ep[e])]
    f13 = [e for e in episodes if any(c.targets.tilt for c in by_ep[e])]
    era_b = [e for e in episodes if all(c.era == "B" for c in by_ep[e])]
    n_target = round(len(episodes) * fraction)
    rng = np.random.default_rng(seed)

    hold = _perm(rng, g1)[: math.ceil(len(g1) / 2)]
    if len(f13) == 2:
        inside = [e for e in f13 if e in hold]
        if not inside:
            hold.append(_perm(rng, f13)[0])
        elif len(inside) == 2:
            drop = _perm(rng, inside)[1]
            hold.remove(drop)
            spare = [e for e in g1 if e not in hold and e not in f13 and e != drop]
            if spare:
                hold.append(_perm(rng, spare)[0])
    if era_b and not any(e in era_b for e in hold):
        hold.append(_perm(rng, era_b)[0])
    pool = [e for e in episodes if e not in hold and not (len(f13) == 2 and e in f13)]
    for e in _perm(rng, pool):
        if len(hold) >= n_target:
            break
        hold.append(e)
    return sorted(hold)


def counts(cases, turning: frozenset[str]) -> dict:
    """Descriptive counts of a case set (turning points as given)."""
    cases = list(cases)
    g1 = gate1_ids(cases, turning)
    out = {
        "cases": len(cases),
        "episodes": len({c.episode_id for c in cases}),
        "era_A_cases": sum(c.era == "A" for c in cases),
        "era_B_cases": sum(c.era == "B" for c in cases),
        "era_A_episodes": len({c.episode_id for c in cases if c.era == "A"}),
        "era_B_episodes": len({c.episode_id for c in cases if c.era == "B"}),
        "turning_points": sum(c.id in turning for c in cases),
        "turning_with_regime_target": sum(c.id in turning and c.targets.regime_direction is not None
                                          for c in cases),
        "gate1_cases": len(g1),
        "gate1_episodes": len({c.episode_id for c in cases if c.id in g1}),
        "thesis_target_cases": sum(bool(c.targets.theses) for c in cases),
        "gate2_cases": sum(bool(c.targets.theses) and c.era == "A" for c in cases),
        "gate2_episodes": len({c.episode_id for c in cases if c.targets.theses and c.era == "A"}),
        "thirteen_f_cases": sum(bool(c.targets.tilt) for c in cases),
    }
    for k in ("process", "action"):
        out[f"truth_{k}"] = sum(c.truth_type == k for c in cases)
    for k in ("yes", "partial", "no"):
        out[f"mechanizable_{k}"] = sum(c.mechanizable == k for c in cases)
    for k in ("primary", "near-primary", "secondary"):
        out[f"reliability_{k}"] = sum(c.source_reliability == k for c in cases)
    return out


def create(root: str | Path, seed: int = SEED, now: _dt.datetime | None = None) -> dict:
    """Draw the split and write ``HOLDOUT.yaml``. Refuses when one exists (the seal is made once)."""
    root = Path(root)
    out = root / HOLDOUT_FILE
    if out.exists():
        raise HoldoutError(f"{out} exists; the holdout is sealed once and never redrawn (see reseal)")
    spec = _seal(root, seed, now)
    out.write_text(yaml.safe_dump(spec, sort_keys=False, width=110), encoding="utf-8")
    return spec


def reseal(root: str | Path, reason: str, seed: int = SEED, now: _dt.datetime | None = None) -> dict:
    """Redraw the split with the same method and seed and write ``HOLDOUT.yaml`` version n+1 (spec/HOLDOUT.md
    "Re-seal log"). Allowed only while the holdout has never been opened: refuses when ``UNSEAL_LOG.txt``
    exists. The previous version's episodes, hashes, creation time and file sha256 are kept under
    ``previous`` (all earlier versions, oldest first). Does not verify the old holdout hash: a re-seal exists
    precisely because cases were added to holdout episodes."""
    import hashlib

    root = Path(root)
    out = root / HOLDOUT_FILE
    if (root / UNSEAL_LOG).exists():
        raise HoldoutError(f"{root / UNSEAL_LOG} exists: the holdout has been opened and cannot be re-sealed")
    if not reason or not str(reason).strip():
        raise HoldoutError("reseal requires a non-empty reason")
    old = read_spec(root)
    if old is None:
        raise HoldoutError(f"{out} not found; use create for the first seal")
    prev = {k: old.get(k) for k in ("version", "seed", "created_utc", "holdout_episodes", "holdout_n_cases",
                                    "holdout_sha256", "research_n_cases", "research_sha256", "full_sha256")}
    prev["holdout_yaml_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    spec = _seal(root, seed, now)
    spec["version"] = int(old.get("version", 1)) + 1
    spec["reseal_reason"] = " ".join(str(reason).split())
    spec["unseal_log_absent_at_reseal"] = True
    spec["previous"] = list(old.get("previous") or []) + [prev]
    out.write_text(yaml.safe_dump(spec, sort_keys=False, width=110), encoding="utf-8")
    return spec


def _seal(root: Path, seed: int, now: _dt.datetime | None) -> dict:
    """Draw and describe a split of the case files under ``root`` (no file written)."""
    from fatpitch.cases.schema import _load_files

    files = case_files(root)
    cases = _load_files(files, root)
    episodes = draw(cases, seed)
    research, hold = partition(root, episodes)
    full_turning = turning_point_ids(cases)
    hold_ids = {c.id for c in cases if c.episode_id in set(episodes)}
    hold_cases = [c for c in cases if c.id in hold_ids]
    res_cases = [c for c in cases if c.id not in hold_ids]
    spec = {
        "version": 1,
        "purpose": "Sealed holdout for the final Gate 1 / Gate 2 test (spec/HOLDOUT.md). Do not edit.",
        "seed": seed,
        "method": METHOD,
        "created_utc": (now or _dt.datetime.now(_dt.UTC)).isoformat(timespec="seconds"),
        "hash_method": "sha256 over sorted 'relative_path NUL sha256(file bytes) LF' lines "
                       "(fatpitch.cases.schema.corpus_sha256), paths relative to cases/",
        "holdout_episodes": episodes,
        "holdout_n_cases": len(hold),
        "holdout_sha256": corpus_sha256(hold, root),
        "research_n_cases": len(research),
        "research_sha256": corpus_sha256(research, root),
        "full_sha256": corpus_sha256(files, root),
        "counts_full_corpus_turning": {
            "research": counts(res_cases, full_turning),
            "holdout": counts(hold_cases, full_turning),
        },
    }
    return spec
