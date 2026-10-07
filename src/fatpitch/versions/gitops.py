"""Git helpers for the version runner: resolve a version, materialise it in a temporary worktree.

A version is a git tag ``spec-vX.Y`` (any ref that resolves to a commit is accepted). The tagged commit is
checked out with ``git worktree add --detach`` into a fresh directory under ``%TEMP%`` and removed afterwards
(``git worktree remove --force`` then ``git worktree prune``). The current checkout is never modified.
"""

from __future__ import annotations

import contextlib
import hashlib
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

WIP = "WORKTREE"
WIP_LABEL = "wip"


class GitError(RuntimeError):
    pass


def git(repo: str | Path, *args: str, check: bool = True, binary: bool = False):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if check and p.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed ({p.returncode}): {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace").strip()


def toplevel(path: str | Path) -> Path:
    return Path(git(path, "rev-parse", "--show-toplevel")).resolve()


def resolve_commit(repo: str | Path, ref: str) -> str:
    """Full commit sha of ``ref`` (tag, branch or sha); annotated tags are peeled."""
    return git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}")


def head(repo: str | Path) -> str:
    return git(repo, "rev-parse", "HEAD")


def is_tag(repo: str | Path, ref: str) -> bool:
    return bool(git(repo, "tag", "--list", ref))


def show_file(repo: str | Path, commit: str, relpath: str) -> bytes | None:
    """Bytes of ``relpath`` at ``commit`` (None when absent)."""
    p = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{relpath}"], capture_output=True, check=False)
    return p.stdout if p.returncode == 0 else None


def dirty_paths(repo: str | Path, paths: list[str] | None = None) -> list[str]:
    """Paths with uncommitted changes (tracked or untracked), optionally restricted to ``paths``."""
    out = git(repo, "status", "--porcelain", "--untracked-files=all", "--", *(paths or []))
    return [line[3:] for line in out.splitlines() if line.strip()]


def wip_fingerprint(repo: str | Path, paths: tuple[str, ...] = ("src", "spec")) -> str:
    """sha256 of the uncommitted state under ``paths``: ``git diff HEAD --binary`` plus the bytes of every
    untracked file. Identical working trees give identical fingerprints; a clean tree gives the sha of ''."""
    repo = Path(repo)
    h = hashlib.sha256()
    h.update(git(repo, "diff", "HEAD", "--binary", "--", *paths, binary=True))
    untracked = git(repo, "ls-files", "--others", "--exclude-standard", "--", *paths).splitlines()
    for rel in sorted(untracked):
        f = repo / rel
        if f.is_file():
            h.update(f"\0{rel}\0".encode())
            h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


@contextlib.contextmanager
def worktree(repo: str | Path, commit: str, parent: str | Path | None = None) -> Iterator[Path]:
    """Check ``commit`` out (detached) into a temporary directory; remove it on exit, also on error."""
    repo = Path(repo)
    base = Path(parent) if parent else Path(tempfile.gettempdir()) / "fatpitch-worktrees"
    base.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix=f"wt-{commit[:10]}-", dir=base))
    path.rmdir()  # git worktree add wants to create the directory itself
    git(repo, "worktree", "add", "--detach", str(path), commit)
    try:
        yield path
    finally:
        git(repo, "worktree", "remove", "--force", str(path), check=False)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
        git(repo, "worktree", "prune", check=False)
