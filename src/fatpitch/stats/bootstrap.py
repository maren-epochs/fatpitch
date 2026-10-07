"""Politis-Romano stationary bootstrap.

Ported from multi-strategy ``cbp/research/planning_figures.stationary_bootstrap`` (called by
``cbp/engine/ladder.breach_probability``). Unchanged algorithm. Added: ``stationary_indices`` and
``bootstrap_stat`` (statistic distribution over resampled paths). Not ported: the drawdown ladder
itself (fund-specific risk rule).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def stationary_indices(n: int, n_paths: int, horizon: int, mean_block: float,
                       rng: np.random.Generator) -> np.ndarray:
    """Index paths: blocks of geometric length (mean ``mean_block``), wrapping the sample."""
    p = 1.0 / mean_block
    idx = np.empty((n_paths, horizon), dtype=int)
    idx[:, 0] = rng.integers(0, n, n_paths)
    new_block = rng.random((n_paths, horizon)) < p
    starts = rng.integers(0, n, (n_paths, horizon))
    for t in range(1, horizon):
        idx[:, t] = np.where(new_block[:, t], starts[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def stationary_bootstrap(x: np.ndarray, n_paths: int, horizon: int, mean_block: float,
                         rng: np.random.Generator) -> np.ndarray:
    """Resampled paths of ``x`` (rows of a 2-D array are resampled jointly)."""
    x = np.asarray(x)
    return x[stationary_indices(len(x), n_paths, horizon, mean_block, rng)]


def bootstrap_stat(x: np.ndarray, stat: Callable[[np.ndarray], float], n_paths: int = 2000,
                   mean_block: float = 12, horizon: int | None = None, seed: int = 20261006) -> np.ndarray:
    """Distribution of ``stat`` over stationary-bootstrap paths of length ``horizon`` (default len(x))."""
    x = np.asarray(x)
    rng = np.random.default_rng(seed)
    paths = stationary_bootstrap(x, n_paths, horizon or len(x), mean_block, rng)
    return np.array([stat(p) for p in paths])
