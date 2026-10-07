"""Research trial log ``results\\versions\\trials.jsonl`` (append-only) and multiple-testing adjustment.

Separate from ``fatpitch.prereg`` (pre-registration deferred; nothing here registers or calls
``record_run``). One JSON object per line, written once, never rewritten.

| kind | Counted in N | Written by |
|---|---|---|
| ``tag`` | yes | ``run <tag>`` (any committed version) |
| ``wip`` | yes | ``run WORKTREE`` (uncommitted candidate) |
| ``null`` | no | ``run-nulls`` (baselines, recomputed once per corpus sha / scoring sha) |

N (``count``) is every engine scoring run on the research split, re-runs of an unchanged version
included: the conservative count for DSR ``n_trials`` and for the Holm/Bonferroni family. ``distinct``
reports the number of distinct (commit, wip fingerprint, registry sha, corpus sha) configurations as a
lower bound.
"""

from __future__ import annotations

import json
from pathlib import Path

ENGINE_KINDS = ("tag", "wip")


def read(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def engine_trials(path: str | Path) -> list[dict]:
    return [t for t in read(path) if t.get("kind") in ENGINE_KINDS]


def count(path: str | Path) -> int:
    return len(engine_trials(path))


def distinct(path: str | Path) -> int:
    keys = {(t.get("commit"), t.get("wip_fingerprint"), t.get("registry_sha"), t.get("corpus_sha"))
            for t in engine_trials(path)}
    return len(keys)


def append(path: str | Path, record: dict) -> dict:
    """Append one record. Engine records get ``trial`` = previous engine count + 1."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = dict(record)
    if rec.get("kind") in ENGINE_KINDS:
        rec["trial"] = count(p) + 1
    else:
        rec["trial"] = None
    line = json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str)
    if "\n" in line:
        raise ValueError("trial record must serialise to one line")
    with p.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    return rec


# -------------------------------------------------------------------- adjustment


def bonferroni(p: float | None, n: int) -> float | None:
    return None if p is None else min(1.0, p * max(n, 1))


def holm(pvalues: list[float | None]) -> list[float | None]:
    """Holm step-down adjusted p-values over the whole family (m = len(pvalues)). A missing p (no informative
    pair) is a member of the family with p = 1 and is returned as None."""
    m = len(pvalues)
    filled = [1.0 if p is None else float(p) for p in pvalues]
    order = sorted(range(m), key=lambda i: filled[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * filled[i]))
        adj[i] = running
    return [None if pvalues[i] is None else adj[i] for i in range(m)]


def adjusted(path: str | Path, key: str) -> dict[int, dict]:
    """For every engine trial: raw p at ``key`` (e.g. ``gate1_p``), Holm and Bonferroni over all N trials."""
    tr = engine_trials(path)
    raw = [t.get("summary", {}).get(key) for t in tr]
    h = holm(raw)
    n = len(tr)
    return {t["trial"]: {"raw": r, "holm": hh, "bonferroni": bonferroni(r, n), "n": n}
            for t, r, hh in zip(tr, raw, h, strict=True)}
