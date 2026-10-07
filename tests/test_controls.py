"""fatpitch.stats.controls.hac_regression.

The CBP test compared against statsmodels; statsmodels is not a dependency here, so the reference
is an independent loop implementation of the same sandwich estimator (Bartlett weights, no small-
sample correction), plus closed-form checks.
"""

import math

import numpy as np

from fatpitch.stats.controls import hac_regression
from fatpitch.stats.inference import nw_lag


def _reference(y, x, lags):
    t = len(y)
    X = [[1.0, xi] for xi in x]
    XtX = np.zeros((2, 2))
    Xty = np.zeros(2)
    for i in range(t):
        for a in range(2):
            Xty[a] += X[i][a] * y[i]
            for b in range(2):
                XtX[a, b] += X[i][a] * X[i][b]
    beta = np.linalg.solve(XtX, Xty)
    e = [y[i] - beta[0] - beta[1] * x[i] for i in range(t)]
    S = np.zeros((2, 2))
    for k in range(lags + 1):
        w = 1.0 if k == 0 else 1 - k / (lags + 1)
        G = np.zeros((2, 2))
        for i in range(k, t):
            for a in range(2):
                for b in range(2):
                    G[a, b] += X[i][a] * e[i] * X[i - k][b] * e[i - k]
        S += w * (G if k == 0 else G + G.T)
    Binv = np.linalg.inv(XtX)
    V = Binv @ S @ Binv
    return beta, np.sqrt(np.diag(V))


def _data(t=200, seed=3):
    rng = np.random.default_rng(seed)
    x = rng.normal(0.004, 0.03, t)
    e = np.zeros(t)
    for i in range(1, t):
        e[i] = 0.3 * e[i - 1] + rng.normal(0, 0.01)
    return 0.002 + 0.5 * x + e, x


def test_matches_independent_sandwich():
    y, x = _data()
    ours = hac_regression(y, x)
    beta, se = _reference(list(y), list(x), nw_lag(200))
    assert abs(ours["alpha_annual"] - beta[0] * 12) < 1e-12
    assert abs(ours["beta"] - beta[1]) < 1e-12
    assert abs(ours["alpha_se_annual"] - se[0] * 12) < 1e-10
    assert abs(ours["beta_se"] - se[1]) < 1e-10


def test_lag_zero_is_white_hc0_and_ols_coefficients():
    y, x = _data(150, 9)
    ours = hac_regression(y, x, lags=0)
    X = np.column_stack([np.ones(150), x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    B = np.linalg.inv(X.T @ X)
    hc0 = B @ (X.T * e**2) @ X @ B
    assert np.allclose([ours["alpha_annual"] / 12, ours["beta"]], b)
    assert abs(ours["alpha_se_annual"] / 12 - math.sqrt(hc0[0, 0])) < 1e-12


def test_nan_rows_dropped_and_periods_per_year():
    y, x = _data(120, 4)
    y2 = y.copy()
    y2[5] = np.nan
    r = hac_regression(y2, x, periods_per_year=252)
    assert r["periods"] == 119
    assert abs(r["min_detectable_alpha_annual"] - 2.8 * r["alpha_se_annual"]) < 1e-12
