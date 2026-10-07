r"""Seal the research/holdout split of cases\ (writes cases\HOLDOUT.yaml; spec\HOLDOUT.md).

First seal: refuses when cases\HOLDOUT.yaml exists. Re-seal (``--reseal --reason "..."``): same method and seed,
writes version n+1 with the previous version's hashes kept; refuses when cases\UNSEAL_LOG.txt exists (the
holdout has been opened). Prints per-split counts (turning points derived on the full corpus).

    .\.venv\Scripts\python.exe tools\make_holdout.py
    .\.venv\Scripts\python.exe tools\make_holdout.py --reseal --reason "owner decision 2026-10-06: ..."
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fatpitch.cases.holdout import SEED, create, reseal

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--reseal", action="store_true", help="redraw an existing, never-opened seal (version n+1)")
    ap.add_argument("--reason", default="", help="required with --reseal")
    a = ap.parse_args(argv)
    spec = reseal(ROOT / "cases", a.reason, SEED) if a.reseal else create(ROOT / "cases", SEED)
    c = spec["counts_full_corpus_turning"]
    print(f"version {spec['version']}; holdout episodes {spec['holdout_episodes']}")
    print(f"holdout_sha256 {spec['holdout_sha256']}\nresearch_sha256 {spec['research_sha256']}")
    print(f"full_sha256 {spec['full_sha256']}")
    print(f"{'count':28s} {'research':>9s} {'holdout':>9s}")
    for k in c["research"]:
        print(f"{k:28s} {c['research'][k]:9d} {c['holdout'][k]:9d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
