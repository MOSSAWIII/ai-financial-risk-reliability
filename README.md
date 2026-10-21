# Financial Risk Forecast Reliability Under Changing Market Conditions

## Research Question

*How reliable are financial risk forecasts when market conditions change, and how can we evaluate their uncertainty, temporal robustness, and limitations?*

Empirical evaluations of financial risk models typically rely on unconditional loss metrics—such as mean absolute error (MAE) or root mean squared error (RMSE)—averaged over multi-year backtests. This repository investigates how such aggregate rankings behave when decomposed across volatility regimes, why distinct forecasting families fail simultaneously during sudden market transitions, and how point-in-time information and settlement constraints govern sequential financial evaluation.

## Motivation

In risk management and portfolio allocation, the primary vulnerability of a volatility forecast is rarely its typical error during calm sessions, but its tendency to underestimate future risk when market conditions deteriorate abruptly. Because calm trading sessions dominate historical samples, a model can achieve a substantial reduction in average forecasting error while remaining unreliable during stress transitions. In parallel, evaluating sequential allocation rules requires strict discipline regarding what market, dividend, and cash-settlement information is verifiably observable before each decision timestamp.

## Research Approach

The project is organized into two distinct, currently uncoupled research tracks:

1. **Primary Track — Financial Risk Forecast Reliability (`notebooks/`):**
   - **Data and Target:** Daily US market excess returns (`Mkt-RF`) and risk-free rates (`RF`) from the Kenneth R. French Data Library / CRSP (`1926-07-01` to `2026-08-31`; `26,317` trading sessions; SHA-256 verified). From simple daily market returns $r_t = (\text{Mkt-RF}_t + \text{RF}_t)/100$, the target at session close $t$ is the 5-session forward annualized realized volatility:
     $$RV_{5,t} = \sqrt{\frac{252}{5} \sum_{k=1}^{5} r_{t+k}^2} \times 100$$
   - **Chronological Protocol:** All models use features strictly observable at close $t$. Sample boundaries are purged by 4 trading sessions so no target window $t+1 \dots t+5$ crosses a split boundary: estimation (`1990-01-02` to `2009-12-23`, $N = 5,038$), validation (`2010-01-04` to `2015-12-23`, $N = 1,505$), refit (`1990-01-02` to `2015-12-23`, $N = 6,548$), and exploratory evaluation (`2016-01-04` to `2019-12-23`, $N = 1,001$, supplemented by 5 non-overlapping 5-day sub-series of $N = 200\text{--}201$ dates). The `2020–2026` period was inspected during initial data-integrity checks and is therefore not treated as an untouched holdout.
   - **Forecast Specifications:** Estimation-mean baseline (`Constante`, `14.775%`), 20-session trailing realized volatility (`HV20`), calibrated Exponentially Weighted Moving Average (`EWMA`, $\lambda = 0.90$, scale factor $c = 0.924348$), linear `Ridge` regression ($\alpha = 100$ on standardized $HV_{5,t}, HV_{20,t}, HV_{60,t}$ in level space with non-negativity clipping), and shallow `Gradient Boosting` (`max_depth = 1`, `min_samples_leaf = 10`, `learning_rate = 0.05`, `n_estimators = 100` on $HV_{5,t}, HV_{20,t}, HV_{60,t}$), plus sensitivity checks across 56 hyperparameter configurations (`8` `EWMA`, `9` `Ridge`, `39` `Gradient Boosting`).

2. **Complementary Track — Sequential Financial Decisions (`experiments/sequential-financial-decisions/`):**
   - An accounting and execution study of weekly portfolio rebalancing between `SPY` (US equities) and `BIL` (1–3 month US Treasury bills) over a one-year horizon (`100,000 USD` initial capital, integer shares, no leverage or short sales, `08:00 America/New_York` weekly decision timestamp on the first NYSE session of each week, sealed pre-open `OrderIntent`, `T+1` settlement, and net sales financing `H_FIN_NET`).

## Empirical Investigations

The primary volatility reliability study progresses through eight executed notebooks in [`notebooks/`](notebooks/):

- [`00_nature_donnees_fama_french.ipynb`](notebooks/00_nature_donnees_fama_french.ipynb) — Descriptive analysis of the 1926–2026 daily market return series: heavy tails (excess kurtosis `16.125`), near-zero linear return autocorrelation, persistent clustering in $|r_t|$ and $r_t^2$, and single-day shock concentration inside 5-session windows (a single session accounts for $>50\%$ of $\sum_{k=1}^5 r_{t+k}^2$ in `63.90%` of windows, and $>75\%$ in `17.00%`).
- [`01_audit_cible_fama_french.ipynb`](notebooks/01_audit_cible_fama_french.ipynb) — Provenance verification and construction of `26,312` valid $RV_{5,t}$ targets without look-ahead leakage.
- [`02_comprendre_volatilite_realisee.ipynb`](notebooks/02_comprendre_volatilite_realisee.ipynb) — Unconditional properties of $RV_{5,t}$ (median `10.61%`, mean `13.44%`, 99th percentile `55.74%` across 48 contiguous episodes) and mechanical overlap autocorrelation ($ACF(1) = 0.938$, $ACF(5) = 0.668$).
- [`03_previsibilite_simple.ipynb`](notebooks/03_previsibilite_simple.ipynb) — Comparison of `HV20` against `Constante` on 2016–2019 ($N = 1,001$): average MAE drops by `31.40%` (`4.839` vs `7.054`) and RMSE by `16.41%` (`6.796` vs `8.129`), but the underestimation frequency increases from `21.1%` to `36.7%`.
- [`04_fiabilite_conditionnelle_simple.ipynb`](notebooks/04_fiabilite_conditionnelle_simple.ipynb) — Decomposition across five realized-volatility quintiles (`Q1`–`Q5`) fixed on 1990–2015.
- [`05_benchmark_cinq_modeles.ipynb`](notebooks/05_benchmark_cinq_modeles.ipynb) — Joint evaluation of `Constante`, `HV20`, `EWMA`, `Ridge`, and `Gradient Boosting` across global, regime-conditional, and tail-underestimation criteria.
- [`06_anatomie_sous_estimations_communes.ipynb`](notebooks/06_anatomie_sous_estimations_communes.ipynb) — Diagnostic anatomy of dates where at least four of the five models simultaneously underestimate $RV_{5,t}$ by more than `10.931` volatility points.
- [`07_reconnaissance_risque_sous_estimation.ipynb`](notebooks/07_reconnaissance_risque_sous_estimation.ipynb) — Out-of-sample test of two non-refitted ex-ante alert rules calibrated at the 90th percentile of 1990–2015 (`HV20 > 26.32%` and `HV5 / HV20 > 1.3561`).

## Selected Findings

1. **Average error reduction is dominated by calm markets:** Between `Constante` and `HV20` on 2016–2019, `98.4%` (`2.180` of `2.215` volatility points) of the global MAE reduction originates in the calmest quintile `Q1` ($RV_5 \le 7.742\%$). In the highest-volatility quintile `Q5` ($RV_5 \ge 19.815\%$, $N = 131$ dates across 21 episodes), `HV20` still underestimates realized volatility on `84.0%` of dates.
2. **No single model dominates across evaluation criteria:** On 2016–2019, `EWMA` achieves the lowest global MAE (`4.295`), `Ridge` the lowest global RMSE (`6.089`), `Gradient Boosting` the lowest unconditional mean underestimation (`1.530`), and `HV20` the lowest `Q5` MAE (`9.243`) and lowest `Q5` underestimation rate (`83.97%` vs `91.6%` for `EWMA`, `92.4%` for `Ridge`, and `96.2%` for `Gradient Boosting`).
3. **Large underestimations cluster in common multi-model episodes:** At least 4 of the 5 models simultaneously underestimate $RV_{5,t}$ beyond the validation 90th-percentile threshold ($s = 10.931$ volatility points) on `44` dates (`4.40%` of the sample) grouped into `13` contiguous episodes (`33` dates in `11` episodes for all 5 models). Across 56 alternative hyperparameter configurations, common failures occur on `45` dates in the same `13` episodes (`97.8%` Jaccard overlap).
4. **Common failures reflect sudden future shocks rather than elevated pre-existing volatility:** Each of the 13 episodes is driven by a single dominant shock session in $t+1 \dots t+5$ accounting for a median `60.7%` of the 5-day sum of squared returns. At the 13 episode-start dates $t$, `0/13` exhibit an extreme same-day return ($|r_t| > q_{95}$).
5. **Negative result on simple ex-ante early warning:** Neither high trailing volatility (`HV20 > 26.32%`, detecting `0/13` episode starts and `0/44` failure dates) nor short-term acceleration (`HV5 / HV20 > 1.3561`, detecting `1/13` episode starts with `4.20%` daily precision vs the `4.40%` base rate and `114` false alerts) anticipates common underestimation episodes at close $t$.

## Complementary Financial Decision Study

The subdirectory [`experiments/sequential-financial-decisions/`](experiments/sequential-financial-decisions/) examines whether a weekly 50/50 rebalancing rule (`C2`) outperforms a 50/50 buy-and-hold baseline (`C1`) and single-asset benchmarks (`A`: 100% `SPY`; `B`: 100% `BIL`) under realistic execution and cash-settlement constraints:

- **2024–2025 Episode (`2024-05-29` to `2025-05-29`, conditional point-in-time convention `E-B`):** Across all 8 cells combining proportional transaction costs (`S0 = 0`, `S1 = 1`, `S2 = 5`, `S3 = 10` bps) and dividend cash availability delays (`D+1`, `D+2` NYSE sessions after payable date), `C2` finishes ahead of `C1` by **`+519.07 USD` (`S3-D2`) to `+590.12 USD` (`S0-D1`)** on `100,000 USD` initial capital, with slightly shallower maximum drawdown (`-9.32%` to `-9.34%` vs `-9.51%` to `-9.52%`) and slightly higher annualized volatility (`10.09%–10.10%` vs `10.02%–10.03%`).
- **Post Hoc Dividend Reinvestment Diagnostic (`C3`):** Passively reinvesting each ETF's paid distributions into whole shares of the paying ETF without cross-asset rebalancing raises terminal wealth over `C1` by **`+76.30 USD` (`S3-D2`) to `+84.01 USD` (`S0-D1`)**, accounting arithmetically for **`13.67%` to `15.02%`** of the `C2 - C1` terminal wealth gap; the remaining `+442.77 USD` to `+506.11 USD` stems from relative-drift rebalancing between `SPY` and `BIL`.
- **2025–2026 Replication Halted by Documentary Block:** The pre-registered replication (`2025-05-29` to `2026-05-29`) is halted at Cycle 47 (`2026-04-20`, status `DOCUMENTARY_BLOCK`, `performance_computed: false`) due to an irreconcilable `SPY` opening price discrepancy between Yahoo Finance (`708.78`, intraday range `706.14–709.91`) and Nasdaq (`710.14`, flat unadjusted OHLC without volume) in the absence of primary NYSE Daily TAQ data.

## Limitations and Ongoing Questions

- **No coupling between tracks yet:** The `RV5` volatility forecasts in Axis A do not yet feed into the `SPY–BIL` allocation rules in Axis B, and no trained reinforcement learning policy is claimed.
- **Single-index and single-episode scope:** Axis A is restricted to univariate daily US aggregate market returns on an exploratory `2016–2019` window; Axis B's completed numerical comparison covers a single one-year historical episode (`2024–2025`) under conditional convention `E-B`.
- **Open research directions:** Conditioning multi-horizon risk intervals on exogenous state variables, accounting for serial overlap in multi-step evaluation, and coupling calibrated uncertainty estimates with sequential allocation rules.

## Reproducibility

- **Directly inspectable in Git:** All 8 executed notebooks (with embedded tables and figures) and all locked CSV/JSON/SVG outputs for the sequential decision study.
- **Automated test verification:** Running `pytest` executes `164` deterministic unit and accounting tests out of the box (`197` tests when local raw market files are present).
- **Data provenance and licensing:** Raw third-party datasets (`data/raw/`) are excluded from Git pending redistribution verification; their exact public sources and SHA-256 digests are documented in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md). Reuse licensing conditions for this repository remain to be defined.

## Repository Guide

- [`notebooks/`](notebooks/) — Executed Jupyter notebooks (`00` through `07`) for the primary `RV5` forecast reliability study.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — Mathematical definitions, chronological split protocol, and sequential accounting rules.
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — Verification tiers, test commands, and SHA-256 data provenance manifest.
- [`experiments/sequential-financial-decisions/`](experiments/sequential-financial-decisions/) — Scripts, test suite, documentary grids, and locked results for the exploratory `SPY–BIL` study ([study README](experiments/sequential-financial-decisions/README.md)).
- [`requirements.txt`](requirements.txt) — Minimal Python dependencies.

## Research Archive

This `research-overview` branch is a curated academic presentation. The complete chronological development log, intermediate validation gates, and full exploratory archive remain preserved on [`main`](https://github.com/MOSSAWIII/ai-financial-risk-reliability/tree/main).
