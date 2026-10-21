# Financial Risk Forecast Reliability Under Changing Market Conditions

## Research Question

*How reliable are financial risk forecasts when market conditions change, and how can we evaluate their uncertainty, temporal robustness, and limitations?*

The project asks whether a forecasting method that looks better *on average* is also more reliable when risk rises, and what a forecaster could actually know at the time of the forecast.

## Why It Matters

Risk forecasts are used to size positions and set limits. The costly failure is not a typical error in a calm market but a forecast that is too low just before volatility jumps. Average error metrics are dominated by calm periods and can hide this failure. The project therefore evaluates forecasts *conditionally*, and separates what is learned after the fact from what could be known in advance.

## Research Approach

- **Data and target.** Daily US market returns from the Kenneth R. French Data Library (1926–2026, SHA-256 verified). The target is the realized volatility over the next five trading sessions, `RV5`.
- **Protocol.** Strictly chronological, with boundary purging so that no target window crosses a split. Models are estimated on 1990–2009, hyperparameters are chosen on 2010–2015, models are refitted on 1990–2015, and they are compared on 2016–2019 (1,001 forecast dates). The 2020–2026 period was inspected earlier and is not treated as an untouched holdout.
- **Methods.** A constant benchmark, trailing volatility (`HV20`), `EWMA`, `Ridge` regression and `Gradient Boosting`, with sensitivity checks over 56 hyperparameter configurations.
- **Evaluation.** Average errors (MAE, RMSE), underestimation frequency and size, results by volatility regime, and tests of simple ex ante alert rules.

Full definitions, splits and hyperparameters are in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

> **Ex post diagnostics vs. ex ante information.** Regimes `Q1`–`Q5` are quintiles of the *realized future* `RV5`. Their cutoffs are fixed in advance on 1990–2015, but the regime of a given date is known only after its outcome. Regime-conditional results show *where* forecasts fail; they do not show that a forecaster could recognise those regimes at date `t`. Only the alert rules of notebook `07` use information available at `t`.

## Main Empirical Findings

All figures refer to 2016–2019 (`N = 1,001`).

1. **Better average error, but frequent underestimation when risk is high.** `HV20` lowers MAE from `7.05` to `4.84` (−31.4%) and RMSE from `8.13` to `6.80` relative to the constant benchmark, yet underestimates on `36.7%` of dates instead of `21.1%`. `98.4%` of its MAE gain comes from the calmest regime (`Q1`). In the highest regime (`Q5`, defined ex post), `HV20` still underestimates on `84.0%` of dates.
2. **No model family dominates.** `EWMA` has the lowest MAE (`4.295`), `Ridge` the lowest RMSE (`6.089`), `Gradient Boosting` the lowest mean underestimation, and `HV20` the lowest MAE within `Q5` (`9.243`). Rankings depend on the criterion.
3. **Large underestimations are shared across models.** At least four of five models underestimate `RV5` by more than a fixed threshold on `44` dates grouped in `13` episodes (`4.4%` of dates); the same episodes recur across 56 hyperparameter configurations (Jaccard overlap `97.8%`). Each episode is driven by one dominant future session (median `60.7%` of the five-day sum of squared returns), and at none of the 13 episode starts was the same-day return extreme (`0/13` above its 95th percentile).
4. **Simple ex ante alert rules do not anticipate these episodes (negative result).** A high-trailing-volatility rule detects `0/13` episode starts; a volatility-acceleration rule detects `1/13`, with daily precision (`4.20%`) no better than the `4.4%` base rate. Their thresholds were fixed from 1990–2015 and not retuned on 2016–2019.

![Mean absolute error and mean underestimation by future-RV5 quintile, five models, 2016–2019](docs/figures/rv5_quintile_reliability_notebook05.png)

*Figure: error by quintile of the realized future `RV5` (ex post regimes), extracted unchanged from [notebook 05, section 8](notebooks/05_benchmark_cinq_modeles.ipynb); labels are in French (`Constante`, `modèle`, `Points de volatilité`). Every model's error and underestimation are largest in `Q5`.*

## Complementary Study: Sequential Financial Decisions

[`experiments/sequential-financial-decisions/`](experiments/sequential-financial-decisions/) is an exploratory historical simulation of weekly `SPY`/`BIL` allocation with integer shares, `T+1` settlement and dividend cash availability. It is **not connected** to the forecasting track: no `RV5` forecast is used, and no reinforcement-learning agent has been trained.

- In one episode (2024-05-29 to 2025-05-29) and under the stated conditional assumptions, weekly 50/50 rebalancing (`C2`) ends `519`–`590 USD` above 50/50 buy-and-hold (`C1`) on `100,000 USD`, across eight cost and cash-timing cells. Passively reinvesting distributions (`C3`) accounts arithmetically for `13.7%`–`15.0%` of that gap; the remainder reflects differences between complete trading policies and is not an isolated causal effect.
- A second episode (2025–2026), chosen after seeing the first, was locked before computing performance but is not an independent confirmation. It is **halted**: Yahoo and Nasdaq disagree on the `SPY` open of 2026-04-20 and no primary source was acquired. No 2025–2026 performance is reported.

## Limitations and Reproducibility

- Evidence comes from one asset class (US aggregate market), one exploratory evaluation window, and one financial episode. Nothing here is a claim of a new method, a coverage guarantee, or a profitable strategy.
- **Visible:** the eight executed notebooks and the locked CSV/JSON/SVG outputs can be read on GitHub without running anything.
- **Auditable:** documentary grids, SHA-256 manifests and fixtures are tracked. `pytest` without raw data: `164 passed, 33 skipped`.
- **Reproducible locally:** with the archived inputs in `data/raw/` and `data/processed/` (both excluded from Git), `197 passed` and the byte-for-byte `--check` scripts succeed. Full notebook re-execution in a clean clone has **not** been verified.
- **Third parties** need the public sources listed in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md). Notebook text and identifiers are mostly in French; each notebook opens with an English overview. No license has been attached yet.

## Explore the Repository

- [`notebooks/`](notebooks/): eight executed notebooks, `00` (data) to `07` (ex ante alert rules).
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md): definitions, splits, models, accounting rules.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md): what can be checked, how, and with what limits.
- [`experiments/sequential-financial-decisions/`](experiments/sequential-financial-decisions/): scripts, tests, locked results ([study README](experiments/sequential-financial-decisions/README.md)).

## Research Archive

This branch is a curated presentation. The full development history, intermediate reports and complete test history remain on [`main`](https://github.com/MOSSAWIII/ai-financial-risk-reliability/tree/main).
