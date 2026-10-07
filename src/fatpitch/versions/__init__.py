"""Spec-version comparison runner (research mode).

Versions are git tags ``spec-vX.Y``. Each version's own engine, spec and registry run on the CURRENT research
split; scoring is the CURRENT ``fatpitch.cases`` code, so scores differ only through the version. Every engine
run is a research trial (``results\versions\trials.jsonl``); N feeds Holm/Bonferroni and DSR. Nothing here
unseals the holdout or touches ``fatpitch.prereg``.

    python -m fatpitch.versions run spec-v0.1      # or: run WORKTREE (uncommitted candidate, label "wip")
    python -m fatpitch.versions run-nulls
    python -m fatpitch.versions compare spec-v0.1 null_trend_12m
    python -m fatpitch.versions leaderboard
    python -m fatpitch.versions trials count
"""

from fatpitch.versions.adapter import decision_to_prediction
from fatpitch.versions.compare import compare as compare_runs
from fatpitch.versions.compare import gate1_headroom, leaderboard, write_leaderboard
from fatpitch.versions.runner import Paths, default_paths, run_nulls, run_version

__all__ = ["Paths", "compare_runs", "decision_to_prediction", "default_paths", "gate1_headroom", "leaderboard",
           "run_nulls", "run_version", "write_leaderboard"]
