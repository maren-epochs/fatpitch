"""Selection-adjusted Sharpe inference.

Ported from multi-strategy ``cbp/engine/inference.py``. Changes: pandas removed (``window_row``
takes numpy arrays); ``periods_per_year`` replaces the hard-coded monthly sqrt(12) in
annualisation; the CBP mandate disclosure field is generalised to ``target_annual``.

  se_sharpe   Mertens (2002) non-normal SE of the per-period Sharpe ratio, multiplied by
              sqrt(Newey-West long-run variance / iid variance) of the excess returns (Bartlett
              kernel, lag = floor(4 (T/100)^(2/9))), ratio floored at 1.
  psr         Probabilistic Sharpe Ratio: P(true SR > benchmark) = Phi((SR - SR*) / SE).
  dsr         Deflated Sharpe Ratio (Bailey and Lopez de Prado 2014, JPM 40(5)): PSR against the
              expected maximum Sharpe of N independent trials,
              SR0 = sqrt(V) ((1 - g) Phi^-1(1 - 1/N) + g Phi^-1(1 - 1/(N e))), g = Euler-Mascheroni.

Sharpe inputs to psr/dsr are per-period (not annualised). ``n_trials`` for the DSR comes from the
prereg run log (``fatpitch.prereg.count_runs``).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import kurtosis, norm, skew

EULER_GAMMA = 0.5772156649015329


def nw_lag(t: int) -> int:
    return math.floor(4 * (t / 100) ** (2 / 9))


def nw_variance_ratio(x, lags: int | None = None) -> float:
    """Newey-West long-run variance / iid variance (Bartlett), floored at 1."""
    x = np.asarray(x, dtype=float)
    t = len(x)
    lags = nw_lag(t) if lags is None else lags
    u = x - x.mean()
    g0 = u @ u / t
    lr = g0 + 2 * sum((1 - k / (lags + 1)) * (u[k:] @ u[:-k]) / t for k in range(1, lags + 1))
    return max(1.0, lr / g0)


def sharpe(excess) -> float:
    """Per-period Sharpe ratio (mean / sample sd)."""
    x = np.asarray(excess, dtype=float)
    return float(x.mean() / x.std(ddof=1))


sharpe_monthly = sharpe  # CBP name


def se_mertens(sr: float, t: int, g3: float, g4: float) -> float:
    """Mertens (2002): Var(SR) = (1 - g3 SR + (g4 - 1)/4 SR^2) / T, g4 = raw (Pearson) kurtosis."""
    return math.sqrt(max(1e-18, (1 - g3 * sr + (g4 - 1) / 4 * sr**2) / t))


def sharpe_stats(excess, periods_per_year: int = 12) -> dict:
    """Per-period Sharpe with Mertens SE and the NW-adjusted SE."""
    x = np.asarray(excess, dtype=float)
    x = x[~np.isnan(x)]
    t = len(x)
    sr = sharpe(x)
    g3, g4 = float(skew(x)), float(kurtosis(x, fisher=False))
    se_m = se_mertens(sr, t, g3, g4)
    ratio = nw_variance_ratio(x)
    return {"periods": t, "sr": sr, "sr_annual": sr * math.sqrt(periods_per_year), "skew": g3,
            "kurtosis_raw": g4, "se_mertens": se_m, "nw_ratio": ratio, "se": se_m * math.sqrt(ratio)}


def psr(sr: float, se: float, benchmark: float = 0.0) -> float:
    return float(norm.cdf((sr - benchmark) / se))


def expected_max_sharpe(n_trials: float, var_trials: float) -> float:
    """SR0 of the DSR: expected maximum of n independent trial Sharpes (per-period units)."""
    n = max(float(n_trials), 1.0 + 1e-12)
    return math.sqrt(var_trials) * ((1 - EULER_GAMMA) * norm.ppf(1 - 1 / n)
                                    + EULER_GAMMA * norm.ppf(1 - 1 / (n * math.e)))


def dsr(sr: float, se: float, n_trials: float, var_trials: float) -> float:
    return psr(sr, se, expected_max_sharpe(n_trials, var_trials))


def ci_annual(st: dict, level: float = 0.95, periods_per_year: int = 12) -> tuple[float, float]:
    z = norm.ppf(0.5 + level / 2)
    a = math.sqrt(periods_per_year)
    return (st["sr"] - z * st["se"]) * a, (st["sr"] + z * st["se"]) * a


def window_row(ret, cash, n_trials: float, var_trials: float, label: str, target_annual: float = 0.8,
               periods_per_year: int = 12) -> dict:
    """Sharpe, interval, PSR(0), PSR(target), DSR and a flag when PSR(target) < 0.5."""
    x = np.asarray(ret, dtype=float) - np.asarray(cash, dtype=float)
    x = x[~np.isnan(x)]
    st = sharpe_stats(x, periods_per_year)
    lo, hi = ci_annual(st, periods_per_year=periods_per_year)
    p_t = psr(st["sr"], st["se"], target_annual / math.sqrt(periods_per_year))
    return {"window": label, **st, "ci95_low": lo, "ci95_high": hi,
            "psr_0": psr(st["sr"], st["se"], 0.0), "psr_target": p_t, "target_annual": target_annual,
            "dsr": dsr(st["sr"], st["se"], n_trials, var_trials), "dsr_n": n_trials,
            "dsr_var_trials": var_trials, "target_not_supported": bool(p_t < 0.5)}
