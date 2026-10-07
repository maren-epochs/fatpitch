"""OLS with Newey-West (Bartlett) HAC standard errors.

Ported from multi-strategy ``cbp/research/controls.py`` (``hac_regression`` only). Changes: pandas
removed (numpy arrays; rows with NaN in y or x dropped); ``periods_per_year`` replaces the
hard-coded monthly x12; optional fixed ``lags``. Not ported: the CBP ex-ante control books
(ABSMOM 10-asset universe, 60/40, equal-weight strategies) — fund-specific.

Outputs: per-year alpha = periods_per_year x intercept, its HAC SE and t, beta, tracking error,
information ratio, minimum detectable per-year alpha (80% power, 5% two-sided) = 2.8 x SE.
"""

from __future__ import annotations

import math

import numpy as np

from fatpitch.stats.inference import nw_lag


def hac_regression(y, x, lags: int | None = None, periods_per_year: int = 12) -> dict:
    """OLS y = a + b x + e with Newey-West (Bartlett) HAC standard errors."""
    yv, xv = np.asarray(y, dtype=float), np.asarray(x, dtype=float)
    ok = ~(np.isnan(yv) | np.isnan(xv))
    yv, xv = yv[ok], xv[ok]
    t = len(yv)
    X = np.column_stack([np.ones(t), xv])
    beta = np.linalg.solve(X.T @ X, X.T @ yv)
    e = yv - X @ beta
    L = nw_lag(t) if lags is None else lags
    Xe = X * e[:, None]
    S = Xe.T @ Xe / t
    for k in range(1, L + 1):
        w = 1 - k / (L + 1)
        G = Xe[k:].T @ Xe[:-k] / t
        S += w * (G + G.T)
    XtX_inv = np.linalg.inv(X.T @ X / t)
    V = XtX_inv @ S @ XtX_inv / t
    se_a = math.sqrt(V[0, 0])
    se_b = math.sqrt(V[1, 1])
    p = periods_per_year
    te = float(np.std(yv - xv, ddof=1) * math.sqrt(p))
    return {"periods": t, "lags": L, "alpha_annual": beta[0] * p, "alpha_se_annual": se_a * p,
            "alpha_t": beta[0] / se_a, "beta": beta[1], "beta_se": se_b, "tracking_error": te,
            "information_ratio": float(np.mean(yv - xv) * p / te) if te > 0 else float("nan"),
            "min_detectable_alpha_annual": 2.8 * se_a * p}
