# Sequential Financial Decisions — Exploratory SPY–BIL Study

This directory contains the complementary study of the repository: an accounting-exact, point-in-time evaluation of weekly portfolio rebalancing between **SPY** (SPDR S&P 500 ETF Trust) and **BIL** (SPDR Bloomberg 1–3 Month T-Bill ETF) under realistic US equity market-structure constraints.

> **Relationship to the Primary Research Track:** This study is an exploratory financial decision and accounting benchmark. It does not consume the `RV5` volatility forecasts developed in [`notebooks/`](../../notebooks/), does not claim to validate a machine learning signal, and does not train a reinforcement learning policy.

---

## 1. Decision Problem and Accounting Protocol

We evaluate a sequential portfolio manager allocating `100,000.00 USD` across `SPY` and `BIL` over a one-year horizon (`52` weekly decision cycles):

- **Decision Timestamp:** `08:00 America/New_York` on the first NYSE trading session of each calendar week.
- **Pre-Open Information Set & Order Sealing:** At `08:00 ET`, the policy observes settled cash, settled integer share holdings, and historical closing prices up to the previous NYSE session (`Close_{t-1}`). Target whole-share orders are sized from `Close_{t-1}` and sealed into an immutable `OrderIntent` (with a SHA-256 pre-open digest) before same-day opening prices (`Open_t`) are read to simulate execution at the `09:30 ET` open.
- **Portfolio Constraints:** Long-only integer shares ($N^{\text{SPY}}_t, N^{\text{BIL}}_t \in \mathbb{N}_0$), non-negative cash ($C_t \ge 0$), no short sales, no leverage, and no fractional shares.
- **`T+1` Settlement & Net Sales Financing (`H_FIN_NET`):** Under the post-May 28, 2024 US `T+1` settlement cycle, same-day sale proceeds and purchase obligations settle on `T+1`. Net sale proceeds (after proportional selling fees) can finance same-session purchases at `Open_t`. If an overnight price gap between `Close_{t-1}` and `Open_t` renders a buy order unaffordable, that buy lot is rejected atomically without post-open resizing.
- **Conditional Point-in-Time Dividend Boundary (`E-B`):**
  - On each ETF ex-dividend date, the distribution per share is accrued as a dividend receivable $R_t$ in mark-to-market economic wealth ($W_t = C_t + N^{\text{SPY}}_t P^{\text{SPY}}_t + N^{\text{BIL}}_t P^{\text{BIL}}_t + R_t$) to avoid artificial ex-date wealth drops.
  - Because free public distribution tables do not provide pre-ex-date timestamped declaration proofs, accrued receivables are excluded from the pre-open trading budget until `D+1` or `D+2` NYSE sessions after the official payable date (`Pay_ Date`).
- **Sensitivity Grid (`8` cells):** Four proportional one-way transaction cost levels (`S0 = 0`, `S1 = 1`, `S2 = 5`, `S3 = 10` bps) crossed with two post-payable dividend cash availability lags (`D+1` and `D+2`).

---

## 2. Policies Compared

1. **`A` (`100% SPY` Buy-and-Hold):** Initial whole-share purchase of `SPY` (`188` shares on `2024-05-29`), held passively with distributions accumulating in cash.
2. **`B` (`100% BIL` Buy-and-Hold):** Initial whole-share purchase of `BIL` (`1,089` shares on `2024-05-29`), held passively. (Under `S3 = 10` bps, the `1,089`-share order sized on prior close is atomically rejected at `Open` because the `99.94 USD` transaction fee exceeds the `62.47 USD` residual cash buffer.)
3. **`C1` (`50/50` Buy-and-Hold):** Initial 50/50 whole-share purchase (`94 SPY` and `544 BIL`), held passively without subsequent trading; paid distributions remain in cash.
4. **`C2` (Weekly `50/50` Rebalancing):** Rebalances weekly at `08:00 ET` toward a 50/50 target across investable wealth (`Close_{t-1}` sizing, sealed `Open_t` execution).
5. **`C3` (Post Hoc Passive Distribution Reinvestment Diagnostic):** Holds the exact initial `C1` share lots (`94 SPY`, `544 BIL`), never sells either asset, and passively reinvests each ETF's settled distribution cash into whole shares of the paying ETF via segregated pools (`cash_pool_spy`, `cash_pool_bil`). `C3` decomposes the `C2 - C1` terminal wealth difference into passive cash reinvestment (`C3 - C1`) versus relative-drift rebalancing (`C2 - C3`).

---

## 3. Episode 1 Results (`2024-05-29` to `2025-05-29`)

Across the 251 NYSE trading sessions (`52` weekly decision dates and `16` distribution events: `4 SPY`, `12 BIL`), single-asset reference policies under `S0` (0 bps) end at **`113,448.70 USD`** for `A` (`100% SPY`, annualized volatility `19.98%`, max drawdown `-18.37%`) and **`104,607.45 USD`** for `B` (`100% BIL`, annualized volatility `0.22%`, max drawdown `-0.01%`).

### 3.1 Paired Comparison and Reinvestment Decomposition (`C1`, `C2`, `C3`)

All figures below are exact values from [`results/historical_c1_c2_2024_2025/comparaison_appariee.csv`](results/historical_c1_c2_2024_2025/comparaison_appariee.csv), [`results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/synthese_comparative_c1_c2_c3.csv`](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/synthese_comparative_c1_c2_c3.csv), and [`results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/differences_richesse_c3_c1_c2_c3.csv`](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/differences_richesse_c3_c1_c2_c3.csv):

| Cell | Cost (bps) | Cash Lag | `C1` Terminal Wealth (USD) | `C2` Terminal Wealth (USD) | `C3` Terminal Wealth (USD) | `C2 - C1` (USD) | `C3 - C1` (USD) | `C2 - C3` (USD) | `C3` Share of `C2 - C1` | `C2` Executed Rebalances | `C2` Max Drawdown | `C1` Max Drawdown |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`S0-D1`** | `0` | `D+1` | `109,025.96` | `109,616.08` | `109,109.97` | `+590.12` | `+84.01` | `+506.11` | `14.24%` | `47` | `-9.32%` | `-9.51%` |
| **`S1-D1`** | `1` | `D+1` | `109,016.03` | `109,601.16` | `109,099.74` | `+585.13` | `+83.72` | `+501.42` | `14.31%` | `48` | `-9.32%` | `-9.51%` |
| **`S2-D1`** | `5` | `D+1` | `108,976.29` | `109,541.69` | `109,058.83` | `+565.40` | `+82.54` | `+482.86` | `14.60%` | `49` | `-9.33%` | `-9.52%` |
| **`S3-D1`** | `10` | `D+1` | `108,926.62` | `109,466.29` | `109,007.70` | `+539.67` | `+81.07` | `+458.60` | `15.02%` | `51` | `-9.34%` | `-9.52%` |
| **`S0-D2`** | `0` | `D+2` | `109,025.96` | `109,605.49` | `109,105.20` | `+579.53` | `+79.24` | `+500.29` | `13.67%` | `48` | `-9.32%` | `-9.51%` |
| **`S1-D2`** | `1` | `D+2` | `109,016.03` | `109,592.21` | `109,094.97` | `+576.19` | `+78.95` | `+497.24` | `13.70%` | `48` | `-9.32%` | `-9.51%` |
| **`S2-D2`** | `5` | `D+2` | `108,976.29` | `109,530.60` | `109,054.06` | `+554.31` | `+77.77` | `+476.54` | `14.03%` | `49` | `-9.33%` | `-9.52%` |
| **`S3-D2`** | `10` | `D+2` | `108,926.62` | `109,445.69` | `109,002.92` | `+519.07` | `+76.30` | `+442.77` | `14.70%` | `51` | `-9.34%` | `-9.52%` |

*(Under `C3`, segregated distribution pools purchase `+1 SPY` share and `+26 BIL` shares across `13` passive reinvestment orders without ever selling either asset, accounting arithmetically for `13.67%` (`S0-D2`) to `15.02%` (`S3-D1`) of the `C2 - C1` terminal wealth difference.)*

### 3.2 Visual Trajectories (`S0-D1`)

![Economic Wealth and Drawdown Trajectories (S0-D1)](results/historical_c1_c2_2024_2025/trajectoire_et_drawdown_s0_d1.svg)

![Cumulative Wealth Gap Decomposition C1, C2, C3 (S0-D1)](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/trajectoires_c1_c2_c3_s0_d1.svg)

---

## 4. Episode 2 Replication (`2025-05-29` to `2026-05-29`) — Documentary Block

To test whether the Episode 1 finding persists out of sample, a second contiguous one-year episode (`2025-05-29` to `2026-05-29`, `252` NYSE sessions, `52` weekly decision dates, `16` distributions) was pre-registered and locked ([`tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json`](tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json) and [`results/historical_c1_c2_2025_2026/sources_configuration.csv`](results/historical_c1_c2_2025_2026/sources_configuration.csv), configuration SHA-256 `39c05d75a8ef83eef4601cdd9343e0c0fc0ac93c84009c389da90a250795e1b9`).

During pre-execution documentary verification ([`docs/grille_documentaire_c2_2025_2026.csv`](docs/grille_documentaire_c2_2025_2026.csv)), **51 of the 52 weekly decision cycles** passed cross-source reconciliation, but **Cycle 47 (sizing close `2026-04-17`, execution open `2026-04-20`)** triggered the documentary stopping rule (`DOCUMENTARY_BLOCK`):

- **Yahoo Finance (`SPY` on `2026-04-20`):** `Open = 708.78`, `High = 709.91`, `Low = 706.14`, `Close = 708.72`, `Volume = 60,096,000`.
- **Nasdaq (`SPY` on `2026-04-20`):** `Open = High = Low = Close = 710.14`, `Volume = N/A` (outside Yahoo's entire intraday `[Low, High]` range by `+1.36 USD`, or `19.19` bps).
- **State Street (`SPY` on `2026-04-20`):** Official daily `NAV = 708.47` (closing valuation only; does not establish the primary `09:30 ET` opening print).

Because primary consolidated tape data (`NYSE Daily TAQ`) is not available in the repository to arbitrate between the conflicting secondary providers on `2026-04-20`, simulation of Episode 2 is halted prior to portfolio trajectory aggregation (`performance_computed: false` in [`results/historical_c1_c2_2025_2026/statut_validation_documentaire.json`](results/historical_c1_c2_2025_2026/statut_validation_documentaire.json)).

---

## 5. Directory Contents and Verification Commands

- [`scripts/`](scripts/) — 14 pure-Python standard-library modules implementing the point-in-time portfolio accounting engine (`synthetic_portfolio_ledger.py`, `exploratory_buy_hold_spy_bil.py`), `C1–C2` historical runner (`historical_c1_c2_comparison.py`), `C3` reinvestment diagnostic (`diagnose_distribution_reinvestment.py`), Episode 2 documentary lock (`lock_second_historical_episode.py`), and data/calendar audits.
- [`tests/`](tests/) — 12 `pytest` suites (`164` offline unit/fixture tests + `33` raw-data rebuild tests = `197` tests total).
- [`docs/`](docs/) — Versioned CSV documentary grids for Episode 1 (`grille_documentaire_c2_2024_2025.csv`, `grille_conditionnelle_c2_2024_2025.csv`) and Episode 2 (`grille_documentaire_c2_2025_2026.csv`).
- [`results/`](results/) — Locked CSV, JSON, and SVG outputs for Episode 1 (`historical_c1_c2_2024_2025/`), the `C3` diagnostic (`diagnostic_reinvestissement_c1_c2_c3_2024_2025/`), and the Episode 2 documentary block (`historical_c1_c2_2025_2026/`).
- [`data_manifest.json`](data_manifest.json) — Provenance, coverage, and SHA-256 hashes of all raw market and regulatory files.

Run the test suite from the repository root:
```bash
python -m pytest -q
```
