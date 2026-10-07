"""CLI: ``python -m fatpitch.versions {run,run-nulls,compare,leaderboard,trials} ...``"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

from fatpitch.versions import compare as cmp
from fatpitch.versions import trials
from fatpitch.versions.runner import default_paths, load_research, run_nulls, run_version


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m fatpitch.versions", description=__doc__)
    ap.add_argument("--root", default=None, help="project root (default: the checkout holding this package)")
    ap.add_argument("--amber-data", default=None, help=r"amber data dir (default: env AMBER_DATA or amber\data)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run a tag (or WORKTREE) on the research split; logs one trial")
    r.add_argument("ref")
    n = sub.add_parser("run-nulls", help="score the four nulls on the research split (cached per corpus sha)")
    n.add_argument("--force", action="store_true")
    c = sub.add_parser("compare", help="paired comparison of two runs / labels / nulls")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--json", default=None, help="also write the comparison as JSON to this path")
    sub.add_parser("leaderboard", help="rewrite LEADERBOARD.md / .json and print it")
    t = sub.add_parser("trials", help="trial log")
    t.add_argument("what", choices=("count", "list"))
    a = ap.parse_args(argv)
    paths = default_paths(a.root, a.amber_data)
    warnings.simplefilter("ignore")

    if a.cmd == "run":
        run_version(a.ref, paths)
    elif a.cmd == "run-nulls":
        run_nulls(paths, force=a.force)
        cmp.write_leaderboard(paths)
    elif a.cmd == "compare":
        res = cmp.compare(paths, a.a, a.b)
        sys.stdout.write(cmp.compare_markdown(res))
        if a.json:
            Path(a.json).write_text(json.dumps(res, indent=2, default=str), encoding="utf-8", newline="\n")
    elif a.cmd == "leaderboard":
        lb = cmp.write_leaderboard(paths, load_research(paths))
        sys.stdout.write(cmp.leaderboard_markdown(lb))
    elif a.cmd == "trials":
        if a.what == "count":
            print(f"N = {trials.count(paths.trials)} engine trials "
                  f"({trials.distinct(paths.trials)} distinct configurations) in {paths.trials}")
        else:
            for rec in trials.read(paths.trials):
                s = rec.get("summary", {})
                print(f"{rec.get('trial') or '-':>4} {rec['kind']:5s} {rec['label']:22s} {rec['run_id']} "
                      f"g1 rps {s.get('gate1_rps')} p {s.get('gate1_rps_p')} g2 {s.get('gate2_score')} p {s.get('gate2_p')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
