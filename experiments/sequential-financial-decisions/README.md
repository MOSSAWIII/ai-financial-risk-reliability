# Research Study II — Sequential Financial Decision-Making

*Exploratory SPY–BIL study*

This directory contains a standalone, **exploratory historical simulation**: weekly allocation between **SPY** (SPDR S&P 500 ETF Trust) and **BIL** (SPDR Bloomberg 1–3 Month T-Bill ETF), with explicit accounting for integer shares, `T+1` settlement, proportional costs and dividend cash availability.

> **Scope.** Study II is empirically separate from Study I in [`notebooks/`](../../notebooks/): no `RV5` forecast feeds any policy here, no machine-learning signal is evaluated, and no reinforcement-learning agent has been trained. Prices are retrospective public data; the Yahoo `Open` field is a *proxy* for a hypothetical opening execution, not a price obtained from a broker. The results are conditional on the stated assumptions and are not evidence of an implementable or profitable strategy.

---

## 1. Simulator Protocol

A hypothetical manager allocates `100,000.00 USD` between `SPY` and `BIL` over one year (`52` weekly decision cycles).

- **Decision timestamp:** `08:00 America/New_York` on the first NYSE session of each calendar week.
- **Information at decision time (simulator convention):** settled cash, settled integer share holdings, and closing prices up to the previous NYSE session (`Close_{t-1}`). Whole-share target orders are sized on `Close_{t-1}` and sealed into an immutable `OrderIntent` (SHA-256 digest) *before* the historical `Open_t` proxy is read to simulate execution at the opening.
- **Portfolio constraints:** long-only, integer shares, non-negative cash, no leverage, no short sales.
- **Settlement and financing:** `T+1` settlement has applied to US equities and ETFs since 2024-05-28 (institutional rule). `H_FIN_NET` is a *simulator hypothesis*: net sale proceeds may finance purchases in the same hypothetical session. An unaffordable buy lot is rejected atomically. Real broker behaviour is not modeled.
- **Conditional information boundary (`E-B`):** an ex-dividend distribution is accrued as a receivable in economic wealth, but excluded from the decision budget until `D+1` or `D+2` NYSE sessions after the payable date, because the public tables do not prove when each distribution was announced. This is a conservative, explicitly conditional assumption.
- **Sensitivity grid (`8` cells):** proportional one-way costs `S0 = 0`, `S1 = 1`, `S2 = 5`, `S3 = 10` bps (stylised scenarios, not observed spreads) × cash availability `D+1` / `D+2`.

---

## 2. Policies

1. **`A`** — 100% `SPY` buy-and-hold (`188` shares).
2. **`B`** — 100% `BIL` buy-and-hold (`1,089` shares). Under `S3` (10 bps) the initial order is rejected because the `99.94 USD` fee exceeds the `62.47 USD` residual cash.
3. **`C1`** — 50/50 initial split (`94 SPY`, `544 BIL`), then buy-and-hold; distributions stay in cash.
4. **`C2`** — weekly rebalancing toward 50/50, sized on `Close_{t-1}` and executed hypothetically at the `Open_t` proxy.
5. **`C3`** — *post hoc diagnostic*: the `C1` lots are never sold, and each ETF's settled distributions are passively reinvested in whole shares of the paying ETF through segregated cash pools.

---

## 3. Episode 1 (`2024-05-29` to `2025-05-29`)

`251` sessions, `52` weekly decisions, `16` distribution events. Under `S0`, `A` ends at `113,448.70 USD` (annualized volatility `19.98%`, maximum drawdown `-18.37%`) and `B` at `104,607.45 USD` (`0.22%`, `-0.01%`). These `A`/`B` figures come from the first exploratory evaluation archived on `main` ([`PREMIERE_EVALUATION_EXPLORATOIRE_SPY_BIL_A_B_C1.md`](https://github.com/MOSSAWIII/ai-financial-risk-reliability/blob/main/RL/docs/PREMIERE_EVALUATION_EXPLORATOIRE_SPY_BIL_A_B_C1.md)) and are not recomputed in this directory.

### 3.1 `C1`, `C2`, `C3` across the 8 cells

Values are read from [`comparaison_appariee.csv`](results/historical_c1_c2_2024_2025/comparaison_appariee.csv), [`synthese_comparative_c1_c2_c3.csv`](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/synthese_comparative_c1_c2_c3.csv) and [`differences_richesse_c3_c1_c2_c3.csv`](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/differences_richesse_c3_c1_c2_c3.csv).

| Cell | Cost (bps) | Cash lag | `C1` terminal (USD) | `C2` terminal (USD) | `C3` terminal (USD) | `C2 − C1` | `C3 − C1` | `C2 − C3` | `(C3 − C1)/(C2 − C1)` | `C2` rebalances | `C2` max DD | `C1` max DD |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `S0-D1` | 0 | `D+1` | 109,025.96 | 109,616.08 | 109,109.97 | +590.12 | +84.01 | +506.11 | 14.24% | 47 | −9.32% | −9.51% |
| `S1-D1` | 1 | `D+1` | 109,016.03 | 109,601.16 | 109,099.74 | +585.13 | +83.72 | +501.42 | 14.31% | 48 | −9.32% | −9.51% |
| `S2-D1` | 5 | `D+1` | 108,976.29 | 109,541.69 | 109,058.83 | +565.40 | +82.54 | +482.86 | 14.60% | 49 | −9.33% | −9.52% |
| `S3-D1` | 10 | `D+1` | 108,926.62 | 109,466.29 | 109,007.70 | +539.67 | +81.07 | +458.60 | 15.02% | 51 | −9.34% | −9.52% |
| `S0-D2` | 0 | `D+2` | 109,025.96 | 109,605.49 | 109,105.20 | +579.53 | +79.24 | +500.29 | 13.67% | 48 | −9.32% | −9.51% |
| `S1-D2` | 1 | `D+2` | 109,016.03 | 109,592.21 | 109,094.97 | +576.19 | +78.95 | +497.24 | 13.70% | 48 | −9.32% | −9.51% |
| `S2-D2` | 5 | `D+2` | 108,976.29 | 109,530.60 | 109,054.06 | +554.31 | +77.77 | +476.54 | 14.03% | 49 | −9.33% | −9.52% |
| `S3-D2` | 10 | `D+2` | 108,926.62 | 109,445.69 | 109,002.92 | +519.07 | +76.30 | +442.77 | 14.70% | 51 | −9.34% | −9.52% |

Across the 8 cells, `C2` finishes `519.07`–`590.12 USD` above `C1`, with a slightly shallower maximum drawdown and slightly higher annualized volatility (`10.09%–10.10%` vs `10.02%–10.03%`).

### 3.2 How to read `C3`

Under the specified `C3` policy, passive dividend reinvestment (`+1` `SPY` share and `+26` `BIL` shares over `13` purchases) accounts *arithmetically* for `13.67%`–`15.02%` of the observed `C2 − C1` terminal-wealth difference. The remaining `C2 − C3` gap (`+442.77` to `+506.11 USD`) reflects differences between two complete trading policies: different allocation paths and exposures over time, different cash balances, different future distributions, fees, whole-share constraints, and interactions among these. **It cannot be interpreted as a pure causal rebalancing premium, and `C3` is not a complete causal decomposition of `C2 − C1`.** The result comes from a single one-year episode, with no statistical inference and no out-of-sample confirmation.

![Wealth trajectories of C1, C2 and C3 (S0-D1)](results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/trajectoires_c1_c2_c3_s0_d1.svg)

![Economic wealth and drawdown (S0-D1)](results/historical_c1_c2_2024_2025/trajectoire_et_drawdown_s0_d1.svg)

---

## 4. Episode 2 (`2025-05-29` to `2026-05-29`): post hoc replication attempt, halted

A second contiguous one-year episode (`252` sessions, `52` weekly decisions, `16` distribution events) was chosen **after** the Episode 1 results were known. Its configuration was locked before any performance computation ([`historical_c1_c2_2025_2026_lock_v1.json`](tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json), configuration SHA-256 `39c05d75a8ef83eef4601cdd9343e0c0fc0ac93c84009c389da90a250795e1b9`), but it is therefore **not** an independent, pre-registered confirmatory test.

The documentary grid ([`grille_documentaire_c2_2025_2026.csv`](docs/grille_documentaire_c2_2025_2026.csv)) classifies `51` of the `52` cycles as `CONDITIONALLY_DOCUMENTED` (a retrospective public `Open` proxy exists; this does not verify an executable price). **Cycle 47** (sizing close `2026-04-17`, hypothetical execution at the `2026-04-20` open) is `DOCUMENTARY_BLOCK`:

| Source (`SPY`, `2026-04-20`) | Open | High | Low | Close | Volume |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Yahoo Finance chart JSON | 708.78 | 709.91 | 706.14 | 708.72 | 43,546,800 |
| Nasdaq historical JSON | 710.14 | 710.14 | 710.14 | 710.14 | `N/A` |

The Nasdaq record has four identical prices and no volume, and its value lies `0.23 USD` above Yahoo's High. It also equals the `2026-04-17` close in both sources; no inference is drawn from this. The State Street NAV for the day (`708.53`) is a closing valuation, not an opening price. Without a primary source (NYSE Daily TAQ, not acquired), the true opening price is **not established**, no source is preferred, and the episode is halted with `performance_computed: false` ([`statut_validation_documentaire.json`](results/historical_c1_c2_2025_2026/statut_validation_documentaire.json)). No 2025–2026 performance is claimed.

*Provenance of the Yahoo figures:* `data/raw/rl_market/yahoo_spy_2007-05-25_2026-10-16_acquired-2026-10-19_sha256-b77099e8…f14f52.json` (SHA-256 `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52`). Nasdaq: SHA-256 `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5`. Both raw files are excluded from Git; see [`data_manifest.json`](data_manifest.json).

---

## 5. Contents and Verification

- [`scripts/`](scripts/) — 14 Python modules: accounting ledger (`synthetic_portfolio_ledger.py`), `C1`–`C2` runner (`historical_c1_c2_comparison.py`), `C3` diagnostic (`diagnose_distribution_reinvestment.py`), Episode 2 lock (`lock_second_historical_episode.py`) and data audits. Some audit scripts require `numpy`, `pandas` and `openpyxl` (see [`requirements.txt`](../../requirements.txt)).
- [`tests/`](tests/) — 12 `pytest` modules. Without `data/raw/`: `164 passed, 33 skipped`; with the manifest-listed local `data/raw/` and `data/processed/` files: `197 passed` (see [`docs/REPRODUCIBILITY.md`](../../docs/REPRODUCIBILITY.md) for what was run, and its limits).
- [`docs/`](docs/) — documentary grids; [`results/`](results/) — locked CSV/JSON/SVG outputs (not edited); [`data_manifest.json`](data_manifest.json) — sources and SHA-256 digests.

```bash
python -m pytest -q
```
