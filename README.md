# Diagnosing Experimental Failures in A/B Testing

## Objective
I found and fixed common failures in A/B test analysis: broken variance reduction, sample ratio mismatch, interference between units, misleading significance tests, and peeking at results.

## Methodology
- Debugged an analyst's CUPED code by checking each line against the CUPED formulas. I fixed three bugs: theta was computed as a correlation instead of Cov(Y, X) / Var(X), the covariate was not centered, and the standard error was computed from the raw outcome instead of the adjusted one.
- Ran chi-squared sample ratio mismatch tests on two experiments with different sizes and compared the statistical signal with the practical size of each imbalance.
- Simulated a two-sided marketplace in three worlds (no interference, individual randomization with interference, and a full rollout) and measured the bias in the naive estimate against both the individual effect and the global rollout effect.
- Ran a Beta-Binomial Bayesian A/B test with Beta(1, 1) priors, computing P(B > A) and the expected loss by Monte Carlo, and compared it with a permutation test.
- Wrote my own function for the Bayesian test and used it on a test with four times the users.
- Simulated 1,000 experiments with no true effect, peeking at 50 points in each, and compared uncorrected peeking, a Bonferroni correction, and a single test at the end.
- For the challenge, applied single-covariate and multi-covariate CUPED (OLS residualization) to the LaLonde job training data.

## Key Findings
- **CUPED:** The analyst reported a 0.0% variance reduction. After my fixes it was 82.7%, with the SE falling from 0.1539 to 0.0641 and the CUPED ATE at 2.0185 against a true effect of 2.0.
- **Sample ratio mismatch:** A 0.6 pp imbalance among 100,000 users gave a chi-squared of 14.40, and a 0.05 pp imbalance among 20 million users gave 20.00. Both trip the p < 0.001 alarm, but the larger statistic came from the smaller imbalance because the statistic grows with sample size. The 0.6 pp imbalance is the more likely engineering problem and the bigger threat to validity. A platform should check the size of the imbalance as well as the p-value.
- **Marketplace interference:** The naive ATE was 0.1861, against 0.1428 for rolling the discount out to everyone, an overstatement of 23.3% of the naive estimate. The global rollout effect is the benchmark that matters for a ship decision.
- **Bayesian vs. frequentist:** P(B > A) = 0.8866 and the expected loss of shipping B was 0.000473, so the ship rule said False because the probability was below 0.95. A permutation test gave p = 0.2302, so both approaches said not to ship.
- **Longer test:** With four times the users, P(B > A) = 0.9951 and the ship rule said to ship B.
- **Peeking:** With no true effect, 32.4% of experiments crossed p < 0.05 at least once across 50 peeks, against 5.3% with a single test at the end.
- **Challenge (LaLonde):** re74 and re75 together cut the variance by only 0.8%. Pre-program earnings predict 1978 earnings weakly, so CUPED helps only as much as its covariate does.
