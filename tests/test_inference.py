"""fatpitch.stats.inference (port of CBP tests/test_inference.py; window_row test uses numpy)."""

import itertools
import math

import numpy as np
import pytest
from scipy.stats import norm

from fatpitch.stats import inference as inf


def test_dsr_expected_max_matches_bailey_lopez_de_prado_formula():
    n, v = 100, 1.0
    exp = (1 - inf.EULER_GAMMA) * norm.ppf(0.99) + inf.EULER_GAMMA * norm.ppf(1 - 1 / (100 * math.e))
    assert abs(inf.expected_max_sharpe(n, v) - exp) < 1e-12
    assert 2.4 < inf.expected_max_sharpe(n, v) < 2.6


def test_psr_monotone_in_sharpe():
    vals = [inf.psr(s, 0.05, 0.1) for s in (0.05, 0.1, 0.15, 0.2)]
    assert all(a < b for a, b in itertools.pairwise(vals))
    assert abs(inf.psr(0.1, 0.05, 0.1) - 0.5) < 1e-12


def test_dsr_below_psr_when_many_trials():
    assert inf.dsr(0.2, 0.05, 50, 0.002) < inf.psr(0.2, 0.05)


def test_nw_ratio_floor_and_positive_autocorrelation():
    rng = np.random.default_rng(0)
    e = rng.standard_normal(5000)
    neg = e[1:] - 0.5 * e[:-1]
    assert inf.nw_variance_ratio(neg) == 1.0
    pos = np.zeros(5000)
    for i in range(1, 5000):
        pos[i] = 0.5 * pos[i - 1] + e[i]
    assert inf.nw_variance_ratio(pos) > 1.5


@pytest.mark.parametrize("phi,df,t", [(0.0, None, 434), (0.1, 5, 434), (-0.1, 5, 434), (0.0, None, 92)])
def test_interval_coverage_monte_carlo(phi, df, t):
    """95% interval covers the true Sharpe in 93-97% of 2,000 series (92-period design: 90-98%)."""
    rng = np.random.default_rng(20260923)
    n = 2000
    innov = rng.standard_t(df, size=(n, t + 50)) if df else rng.standard_normal((n, t + 50))
    x = np.zeros_like(innov)
    for i in range(1, t + 50):
        x[:, i] = phi * x[:, i - 1] + innov[:, i]
    x = x[:, 50:]
    sd_innov = math.sqrt(df / (df - 2)) if df else 1.0
    sd = sd_innov / math.sqrt(1 - phi**2)
    true_sr = 1.0 / math.sqrt(12)
    x = x / sd * 0.01 + true_sr * 0.01
    z = 1.959963984540054
    cover = 0
    for row in x:
        st = inf.sharpe_stats(row)
        cover += st["sr"] - z * st["se"] <= true_sr <= st["sr"] + z * st["se"]
    rate = cover / n
    lo, hi = (0.93, 0.97) if t >= 400 else (0.90, 0.98)
    assert lo <= rate <= hi, f"coverage {rate:.3f} for phi={phi}, df={df}, T={t}"


def test_window_row_trigger():
    rng = np.random.default_rng(1)
    cash = np.full(219, 0.001)
    ret = cash + rng.normal(0.003, 0.017, 219)
    row = inf.window_row(ret, cash, 16, 0.0005, "test")
    assert {"psr_0", "psr_target", "dsr", "ci95_low", "ci95_high"} <= set(row)
    assert row["target_not_supported"] == (row["psr_target"] < 0.5)
    assert row["ci95_low"] < row["sr_annual"] < row["ci95_high"]
