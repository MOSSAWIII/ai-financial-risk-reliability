# Methodological Reference

This document summarizes the mathematical definitions, chronological protocols, evaluation metrics, and accounting invariants used across the two research tracks of the repository.

---

## 1. Primary Track — Financial Risk Forecast Reliability (`notebooks/00`–`07`)

### 1.1 Data and Return Reconstruction

The primary empirical study uses the official daily US market factor archive (`F-F_Research_Data_Factors_daily_CSV.zip`, vintage `202608`, CRSP value-weighted market portfolio) published by the Kenneth R. French Data Library.

- **Coverage:** `26,317` trading sessions from `1926-07-01` to `2026-08-31` (including `1,158` historical Saturday sessions, preserved as published; `0` missing values and `0` duplicate dates).
- **Simple Daily Market Return:** Let $\text{Mkt-RF}_t$ denote the daily market excess return (in percent) and $\text{RF}_t$ the daily one-month T-bill rate (in percent). The decimal market return on session $t$ is:
  $$r_t = \frac{\text{Mkt-RF}_t + \text{RF}_t}{100}$$

### 1.2 Target Construction ($RV_{5,t}$)

At the market close of trading session $t$, the forecasting target is the annualized realized volatility over the next 5 trading sessions $t+1, \dots, t+5$, expressed in annualized volatility percentage points:

$$RV_{5,t} = \sqrt{\frac{252}{5} \sum_{k=1}^{5} r_{t+k}^2} \times 100$$

- **Zero-mean convention:** daily returns are not demeaned inside the 5-day window (squared returns are summed directly).
- **Valid targets:** `26,312` observations (`1926-07-01` to `2026-08-24`; the final 5 sessions of the sample lack a complete 5-day forward window).
- **Structural overlap:** Consecutive targets $RV_{5,t}$ and $RV_{5,t+1}$ share 4 out of 5 future return sessions. Consequently, errors and target levels exhibit strong mechanical serial dependence up to lag 4 ($ACF(1) = 0.938$, $ACF(5) = 0.668$). To prevent this overlap from distorting inference, evaluations report both full daily series and **5 non-overlapping sub-series** (offsets $0, 1, 2, 3, 4$, stepping every 5 sessions).

### 1.3 Chronological Split and Boundary Purging

Every forecast $\widehat{RV}_{5,t}$ issued at close $t$ uses exclusively information measurable in $\mathcal{F}_t = \{r_s : s \le t\}$. Whenever a sample boundary occurs at date $B$, the last 4 trading sessions preceding $B$ are purged from the preceding split so that every target window satisfies $t+5 \le B$:

| Split | Start Date | End Date (`t`) | Last Target Session (`t+5`) | Valid Dates ($N$) | Role |
| :--- | :--- | :--- | :--- | ---: | :--- |
| **Estimation** | `1990-01-02` | `2009-12-23` | `2009-12-31` | `5,038` | Initial parameter estimation |
| **Validation** | `2010-01-04` | `2015-12-23` | `2015-12-31` | `1,505` | Hyperparameter selection (`EWMA`, `Ridge`, `Boosting`) |
| **Refit (`1990–2015`)** | `1990-01-02` | `2015-12-23` | `2015-12-31` | `6,548` | Pre-evaluation refit & fixed regime/alert quantile calibration |
| **Exploratory Evaluation** | `2016-01-04` | `2019-12-23` | `2019-12-31` | `1,001` | Out-of-sample comparison (`5` non-overlapping offsets: $N = 201, 200, 200, 200, 200$) |

> **Status of `2020–2026`:** Because the full `1926–2026` series was inspected during initial data-integrity checks (`notebooks/00`–`02`), `2020–2026` is not claimed as a virgin holdout. All modeling comparisons in `notebooks/03`–`07` are strictly restricted to `1990–2019`.

### 1.4 Forecast Specifications Compared

All models are refitted on the `1990–2015` sample ($N = 6,548$) before evaluating on `2016–2019` ($N = 1,001$):

1. **`Constante`:** Unconditional mean of $RV_{5,t}$ on `1990–2015` (`14.775%`).
2. **`HV20`:** Trailing 20-session annualized realized volatility at close $t$:
   $$HV_{20,t} = \sqrt{\frac{252}{20}\sum_{j=0}^{19} r_{t-j}^2} \times 100$$
3. **`EWMA`:** Exponentially weighted moving variance $v_t = \lambda v_{t-1} + (1-\lambda)(252 \, r_t^2)$ with decay $\lambda = 0.90$ (selected on `2010–2015` validation from `{0.90, 0.94, 0.97, 0.99}`) and closed-form multiplicative scale factor $c = 0.924348$ refitted on `1990–2015`.
4. **`Ridge`:** Linear Ridge regression fitted directly on the annualized volatility level $RV_{5,t}$ using 3 backward-looking historical volatility features at close $t$ ($HV_{5,t}$, $HV_{20,t}$, $HV_{60,t}$), standardized via `StandardScaler`, regularized with $\alpha = 100$ (selected on `2010–2015` validation from `{0.01, 0.1, 1, 10, 100}`), and clipped at zero (`np.maximum(raw, 0.0)`).
5. **`Gradient Boosting`:** Shallow tree ensemble (`GradientBoostingRegressor(loss='squared_error', max_depth=1, min_samples_leaf=10, learning_rate=0.05, n_estimators=100, random_state=42)`) trained directly on $RV_{5,t}$ using the same 3 trailing volatility features ($HV_{5,t}$, $HV_{20,t}$, $HV_{60,t}$).
6. **Hyperparameter Sensitivity Grid (`56` configurations):** To verify that common underestimation episodes are not an artifact of hyperparameter selection, Notebooks 05 and 06 evaluate `56` total configurations across the three tunable families (`8` $\lambda$ values for `EWMA`, `9` $\alpha$ values for `Ridge`, and `39` `(max_depth, min_samples_leaf, learning_rate, n_estimators)` combinations for `Gradient Boosting`).

### 1.5 Loss Metrics, Regime Conditioning, and Common Underestimation

Let $e_t = RV_{5,t} - \widehat{RV}_{5,t}$ denote the forecast error at date $t$ (positive $e_t > 0$ indicates **underestimation of future risk**).

- **Global and Asymmetric Metrics:**
  - $\text{MAE} = \frac{1}{N}\sum_{t} |e_t|$ and $\text{RMSE} = \sqrt{\frac{1}{N}\sum_{t} e_t^2}$
  - Underestimation frequency: $\frac{1}{N}\sum_{t} \mathbb{I}(e_t > 0)$
  - Mean unconditional underestimation: $\frac{1}{N}\sum_{t} \max(e_t, 0)$

#### Ex post diagnostics versus ex ante information

Three kinds of quantities appear in the notebooks and must not be conflated:

1. **Ex post conditional diagnostics (notebooks `04`–`06`).** The quintile cutoffs `Q1`–`Q5` of $RV_5$ (`7.742%`, `10.492%`, `14.126%`, `19.815%`) are fixed once on the `1990–2015` sample and applied without recalibration to `2016–2019` (`Q1` $\le 7.742\%$; `Q5` $\ge 19.815\%$, $N = 131$ dates in `21` contiguous episodes). The **thresholds** are fixed ex ante, but the **regime assigned to a date $t$ depends on the realized future $RV_{5,t}$**, which is unknown at $t$. Conditioning on `Q5` therefore shows *where* the forecasts fail once the outcome is known; it does not show that a forecaster could identify `Q5` dates at $t$. Likewise, the *common underestimation dates* (at least 4 of 5 models with $RV_{5,t} - \widehat{RV}_{5,t} > s$, where $s = 10.931$ volatility points is the 90th percentile of $|e_t|$ for `Constante` on `2010–2015`; `44` dates in `13` contiguous episodes, `33` dates in `11` episodes when all 5 models are required) are defined from realized outcomes.
2. **Variables available at the forecast date.** Forecasts and alert rules may use only $\mathcal{F}_t = \{r_s : s \le t\}$: trailing volatilities $HV_{5,t}$, $HV_{20,t}$, $HV_{60,t}$, the current return $r_t$, and quantities derived from them.
3. **Genuinely ex ante alert rules (notebook `07`).** Two rules using only $\mathcal{F}_t$ are calibrated at the 90th percentile of `1990–2015` ($N = 6,553$ dates with valid `HV20`), without post hoc threshold tuning: **Rule A** $HV_{20,t} > 26.3204\%$ and **Rule B** $HV_{5,t} / HV_{20,t} > 1.3561$. Their results on `2016–2019` are negative: they detect `0/13` and `1/13` episode starts, and Rule B's daily precision (`4.20%`) is not above the `4.40%` base rate. The `Q5` diagnostics above must not be read as the performance of a real-time detection system.

---

## 2. Complementary Track — Sequential Financial Decisions (`experiments/sequential-financial-decisions/`)

### 2.1 Decision Problem and Simulator Timeline

The complementary study is an exploratory historical simulation of long-only, whole-share allocation between `SPY` (SPDR S&P 500 ETF Trust) and `BIL` (SPDR Bloomberg 1–3 Month T-Bill ETF) starting from `100,000.00 USD` cash. Prices are retrospective public data; the Yahoo `Open` field is used as a proxy for a hypothetical opening execution, not as a price actually obtained from a broker.

- **Decision Timestamp:** `08:00 America/New_York` on the first NYSE trading session of each calendar week (`52` weekly decision cycles per one-year episode).
- **Two-Stage Pre-Open Sealing (simulator convention):**
  1. At `08:00 ET`, the policy observes settled cash, settled integer share holdings, and closing prices up to the prior NYSE session $t-1$ (`Close_{t-1}`). `Open_t` is not available to the policy when sizing orders.
  2. Target whole-share orders are computed from `Close_{t-1}` and sealed into an immutable `OrderIntent` (SHA-256 digest) before `Open_t` is read to simulate execution at the `09:30 ET` market open.

### 2.2 Accounting, Settlement, and Financing Invariants

- **Integer Shares & No Leverage:** Holdings $N^{\text{SPY}}_t, N^{\text{BIL}}_t \in \mathbb{N}_0$; available cash $C_t \ge 0$; no margin, short selling, or fractional shares.
- **`T+1` Settlement (institutional rule) and Net Sales Financing (`H_FIN_NET`, simulator hypothesis):** US equities and ETFs have settled on `T+1` since 2024-05-28; this is an institutional rule. `H_FIN_NET` is a modeling hypothesis of the simulator: net sale proceeds (after proportional selling fees) may finance purchases in the same hypothetical session at `Open_t`. If the realized `Open_t` gap makes total purchase cost plus fees exceed available cash plus net sale proceeds, the unaffordable buy lot is rejected atomically without resizing. Real broker behaviour is not modeled.
- **Conditional Information Boundary (`E-B`):**
  - **Economic Wealth ($W_t$):** On an ETF ex-dividend date, the distribution per share is accrued as a dividend receivable $R_t$, so that mark-to-market economic wealth $W_t = C_t + N^{\text{SPY}}_t P^{\text{SPY}}_t + N^{\text{BIL}}_t P^{\text{BIL}}_t + R_t$ does not record an artificial ex-date wealth drop.
  - **Decision Budget:** Because the public distribution tables do not prove when each distribution was announced, accrued receivables $R_t$ are excluded from the pre-open trading budget until `D+1` or `D+2` NYSE sessions after the payable date. This is a conservative, explicitly conditional assumption, not a verified reconstruction of broker cash availability.
- **Sensitivity Grid (`8` cells):** Four proportional one-way transaction cost levels (`S0 = 0`, `S1 = 1`, `S2 = 5`, `S3 = 10` bps) crossed with two post-payable cash availability conventions (`D+1` and `D+2`). These costs are stylised scenarios, not observed spreads, slippage or commissions.

### 2.3 Policies Compared and Documentary Gate

- **`A` (100% `SPY` Buy-and-Hold)** and **`B` (100% `BIL` Buy-and-Hold):** Initial whole-share allocation on the first decision date, held without subsequent trading.
- **`C1` (50/50 Buy-and-Hold):** Initial 50/50 whole-share split (`94 SPY` and `544 BIL` in Episode 1); paid distributions accumulate in cash without subsequent trading.
- **`C2` (Weekly 50/50 Rebalancing):** At each weekly decision timestamp, rebalances toward a 50/50 target across investable wealth, sizing orders on `Close_{t-1}` and executing hypothetically at the historical `Open_t` proxy.
- **`C3` (Post Hoc Passive Distribution Reinvestment Diagnostic):** Holds the exact initial `C1` share lots (`94 SPY`, `544 BIL`), never sells either asset, and passively reinvests each ETF's settled distribution cash into whole shares of the paying ETF via segregated cash pools (`cash_pool_spy`, `cash_pool_bil`).
- **Interpretation of `C1`, `C2`, `C3`:** `C3 - C1` is the observed terminal-wealth difference under the specified passive reinvestment policy; arithmetically it accounts for `13.67%`–`15.02%` of `C2 - C1`. `C2 - C3` is the remaining difference between two complete trading policies. It mixes different allocation paths, exposures, accumulated cash, future distributions, fees, whole-share constraints and their interactions. It is **not** an isolated causal rebalancing premium, and `C3` is not a complete causal decomposition of `C2 - C1`.
- **Documentary Stopping Rule (`DOCUMENTARY_BLOCK`):** Before any performance is computed for an episode, the `Open` price required at each weekly cycle is classified from the available public sources (`MARKET_OBSERVABLE_PROXY` or `PRICE_MISSING_OR_DISPUTED`). For Episode 2 (`2025-05-29` to `2026-05-29`), `51` of the `52` cycles are classified `CONDITIONALLY_DOCUMENTED`. Cycle 47 (`2026-04-20`) is disputed: the Yahoo and Nasdaq `SPY` OHLC records are incompatible and no primary NYSE Daily TAQ source has been acquired. The episode is therefore halted with `performance_computed: false`. "Conditionally documented" means that a retrospective public-data proxy exists; it does not mean that the price was verified as an executable price.
