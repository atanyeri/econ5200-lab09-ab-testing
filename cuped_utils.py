"""CUPED variance reduction for A/B tests (ECON 5200, Lab 9).

After Deng et al. (2013), "Improving the Sensitivity of Online Controlled
Experiments by Utilizing Pre-Experiment Data."
"""

import numpy as np
from numpy.linalg import lstsq


def diff_in_means(y, treat_mask):
    """Treated mean minus control mean, and its standard error."""
    y_t, y_c = y[treat_mask], y[~treat_mask]        # ~ flips True and False
    ate = np.mean(y_t) - np.mean(y_c)
    se = np.sqrt(np.var(y_t, ddof=1) / len(y_t) + np.var(y_c, ddof=1) / len(y_c))
    return ate, se


def cuped_adjust(y, x_pre, treatment):
    """CUPED with one covariate (x_pre 1-D) or several (2-D). Returns a dict."""
    assert y.shape[0] == x_pre.shape[0] == treatment.shape[0]
    treat_mask = treatment == 1

    if x_pre.ndim == 1:
        # One covariate: theta = Cov(y, x) / Var(x), pooled across both arms
        cov_matrix = np.cov(y, x_pre)
        theta = cov_matrix[0, 1] / cov_matrix[1, 1]
        y_adj = y - theta * (x_pre - np.mean(x_pre))
    else:
        # Several covariates: regress y on them, keep the residual, add back y's mean
        X = np.column_stack([np.ones(len(y)), x_pre])
        # lstsq returns four things; _ names the three not used here
        betas, _, _, _ = lstsq(X, y, rcond=None)
        y_adj = y - X @ betas + np.mean(y)          # @ multiplies matrices: X @ betas is the fitted values

    ate_naive, se_naive = diff_in_means(y, treat_mask)
    ate_cuped, se_cuped = diff_in_means(y_adj, treat_mask)
    return {
        "y_adj": y_adj,
        "ate_naive": ate_naive,
        "se_naive": se_naive,
        "ate_cuped": ate_cuped,
        "se_cuped": se_cuped,
        "variance_reduction_pct": round((1 - (se_cuped / se_naive) ** 2) * 100, 2),
    }


def cuped_summary(y, x_pre_dict, treatment):
    """Print the naive estimate and one CUPED row per {label: covariate(s)}."""
    ate_naive, se_naive = diff_in_means(y, treatment == 1)
    # :<25 left-aligns in 25 characters; :>12,.2f right-aligns in 12, with commas and 2 decimals
    print(f"{'Method':<25} {'ATE':>12} {'SE':>12} {'Var Red':>10}")
    print("=" * 60)
    print(f"{'Naive':<25} {ate_naive:>12,.2f} {se_naive:>12,.2f} {'---':>10}")
    for label, x_pre in x_pre_dict.items():
        result = cuped_adjust(y, x_pre, treatment)
        print(f"{'CUPED (' + label + ')':<25} {result['ate_cuped']:>12,.2f} "
              f"{result['se_cuped']:>12,.2f} {result['variance_reduction_pct']:>9.1f}%")
