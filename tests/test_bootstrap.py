"""fatpitch.stats.bootstrap (port of CBP tests/test_planning_figures bootstrap test)."""

import numpy as np

from fatpitch.stats.bootstrap import bootstrap_stat, stationary_bootstrap


def test_bootstrap_shape_values_and_reproducibility():
    x = np.arange(100, dtype=float)
    a = stationary_bootstrap(x, 50, 24, 12, np.random.default_rng(1))
    b = stationary_bootstrap(x, 50, 24, 12, np.random.default_rng(1))
    assert a.shape == (50, 24) and np.array_equal(a, b)
    assert set(np.unique(a)).issubset(set(x))
    steps = np.diff(a, axis=1) % 100
    assert (steps == 1).mean() > 0.8


def test_joint_rows_resampled_together():
    x = np.column_stack([np.arange(30), np.arange(30) * 10])
    p = stationary_bootstrap(x, 5, 20, 4, np.random.default_rng(2))
    assert p.shape == (5, 20, 2) and np.array_equal(p[..., 1], p[..., 0] * 10)


def test_bootstrap_stat_mean_centred():
    rng = np.random.default_rng(3)
    x = rng.normal(0.01, 0.05, 400)
    dist = bootstrap_stat(x, np.mean, n_paths=500, mean_block=6)
    assert dist.shape == (500,) and abs(dist.mean() - x.mean()) < 0.003
