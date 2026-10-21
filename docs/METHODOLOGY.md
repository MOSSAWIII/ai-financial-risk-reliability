# Methodological Reference

This document summarizes the mathematical definitions, chronological protocols, evaluation metrics, and accounting invariants used across the two research tracks of the repository.

---

## 1. Primary Track — Financial Risk Forecast Reliability (`notebooks/00`–`07`)

### 1.1 Data and Return Reconstruction

The primary empirical study uses the official daily US market factor archive (`F-F_Research_Data_Factors_daily_CSV.zip`, vintage `202608`, CRSP value-weighted market portfolio) published by the Kenneth R. French Data Library.

- **Coverage:** `26,317` trading sessions from `1926-07-01` to `2026-08-31` (including `1,158` historical Saturday trading sessions prior to 1953, preserved to maintain authentic 5-session trading horizons; `0` missing values and `0` duplicate dates).
- **Simple Daily Market Return:** Let $\text{Mkt-RF}_t$ denote the daily market excess return (in percent) and $\text{RF}_t$ the daily one-month T-bill rate (in percent). The decimal market return on session $t$ is:
  $$r_t = \frac{\text{Mkt-RF}_t + \text{RF}_t}{100}$$

### 1.2 Target Construction ($RV_{5,t}$)

At the market close of trading session $t$, the forecasting target is the annualized realized volatility over the next 5 trading sessions $t+1, \dots, t+5$, expressed in annualized volatility percentage points:

$$RV_{5,t} = \sqrt{\frac{252}{5} \sum_{k=1}^{5} r_{t+k}^2} \times 100$$

- **Zero-mean convention:** Following standard high-frequency and daily volatility forecasting conventions, daily returns are not demeaned over the 5-day window to avoid noisy sample-mean estimation on 5 observations.
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
- **Ex-Ante Fixed Volatility Quintiles (`Q1`–`Q5`):** Cutoffs are fixed once on the `1990–2015` refit sample (`7.742%`, `10.492%`, `14.126%`, `19.815%`) and applied without recalibration to `2016–2019` (`Q1` $\le 7.742\%$; `Q5` $\ge 19.815\%$, $N = 131$ dates in `21` contiguous episodes).
- **Large and Common Underestimation (`notebooks/05`–`07`):**
  - The large-error threshold $s = 10.931$ volatility points is fixed as the 90th percentile of $|e_t|$ for `Constante` on the `2010–2015` validation split.
  - A date $t \in \text{2016–2019}$ is a **common large underestimation date** if at least 4 of the 5 models satisfy $RV_{5,t} - \widehat{RV}_{5,t} > s$ (`44` dates across `13` contiguous episodes; `33` dates across `11` episodes when requiring all 5 models).
- **Ex-Ante Alert Protocol (`notebook 07`):** Two alert rules using only $\mathcal{F}_t$ are calibrated at the 90th percentile of `1990–2015` ($N = 6,553$ dates with valid `HV20`) without post-hoc threshold tuning:
  - **Rule A (High Trailing Volatility):** $HV_{20,t} > 26.3204\%$
  - **Rule B (Short-Term Volatility Acceleration):** $HV_{5,t} / HV_{20,t} > 1.3561$

---

## 2. Complementary Track — Sequential Financial Decisions (`experiments/sequential-financial-decisions/`)

### 2.1 Decision Problem and Operational Timeline

The complementary study evaluates long-only, whole-share portfolio allocation between `SPY` (SPDR S&P 500 ETF Trust) and `BIL` (SPDR Bloomberg 1–3 Month T-Bill ETF) starting from `100,000.00 USD` cash:

- **Decision Timestamp:** `08:00 America/New_York` on the first NYSE trading session of each calendar week (`52` weekly decision cycles per one-year episode).
- **Two-Stage Pre-Open Sealing:**
  1. At `08:00 ET`, the policy observes settled cash, settled integer share holdings, and historical closing prices up to the prior NYSE session $t-1$ (`Close_{t-1}`). Same-day opening prices (`Open_t`) are strictly unobservable when sizing orders.
  2. Target whole-share orders are computed from `Close_{t-1}` and cryptographically sealed into an immutable `OrderIntent` (with a SHA-256 pre-open digest) before `Open_t` is read to simulate execution at the `09:30 ET` market open.

### 2.2 Accounting, Settlement, and Financing Invariants

- **Integer Shares & No Leverage:** Holdings $N^{\text{SPY}}_t, N^{\text{BIL}}_t \in \mathbb{N}_0$; available cash $C_t \ge 0$; no margin, short selling, or fractional shares.
- **`T+1` Settlement and Net Sales Financing (`H_FIN_NET`):** Under the post-May 28, 2024 US equities/ETF `T+1` settlement regime, same-day sale proceeds and purchase obligations settle simultaneously on `T+1`. Under `H_FIN_NET`, gross sale proceeds (net of proportional selling fees) can finance same-session purchases at `Open_t`. If actual `Open_t` gap movement causes total purchase cost plus fees to exceed available cash plus net sale proceeds, the unaffordable buy lot is rejected atomically without ex-post resizing.
- **Conditional Point-in-Time Dividend Boundary (`E-B`):**
  - **Economic Wealth ($W_t$):** On an ETF ex-dividend date, the distribution per share is accrued as a dividend receivable $R_t$ so that mark-to-market economic wealth $W_t = C_t + N^{\text{SPY}}_t P^{\text{SPY}}_t + N^{\text{BIL}}_t P^{\text{BIL}}_t + R_t$ does not record an artificial ex-date wealth drop.
  - **Decision Budget:** Because standard public files lack pre-ex-date timestamped declaration proofs, accrued receivables $R_t$ are excluded from the pre-open trading budget until `D+1` or `D+2` NYSE sessions after the official payable date (`Pay_ Date`).
- **Sensitivity Grid (`8` cells):** Four proportional one-way transaction cost levels (`S0 = 0`, `S1 = 1`, `S2 = 5`, `S3 = 10` bps) crossed with two post-payable cash availability conventions (`D+1` and `D+2`).

### 2.3 Policies Compared and Documentary Gate

- **`A` (100% `SPY` Buy-and-Hold)** and **`B` (100% `BIL` Buy-and-Hold):** Initial whole-share allocation on the first decision date, held without subsequent trading.
- **`C1` (50/50 Buy-and-Hold):** Initial 50/50 whole-share split (`94 SPY` and `544 BIL` in Episode 1); paid distributions accumulate in cash without subsequent trading.
- **`C2` (Weekly 50/50 Rebalancing):** At each weekly decision timestamp, rebalances toward a 50/50 target across investable wealth using `Close_{t-1}` sizing and sealed `Open_t` execution.
- **`C3` (Post Hoc Passive Distribution Reinvestment Diagnostic):** Holds the exact initial `C1` share lots (`94 SPY`, `544 BIL`), never sells either asset, and passively reinvests each ETF's settled distribution cash into whole shares of the paying ETF via segregated cash pools (`cash_pool_spy`, `cash_pool_bil`). `C3` isolates the mechanical effect of reinvesting cash distributions from cross-asset drift rebalancing (`C2 - C3`).
- **Documentary Stopping Rule (`DOCUMENTARY_BLOCK`):** Before computing performance on any historical episode, all 52 weekly execution prices must pass cross-source reconciliation (`Yahoo Finance` vs `Nasdaq` vs official `State Street` NAV). If an execution price exhibits an irreconcilable cross-source discrepancy on an active decision date without primary consolidated tape (`NYSE Daily TAQ`) verification, simulation halts prior to performance aggregation (`performance_computed: false`).
