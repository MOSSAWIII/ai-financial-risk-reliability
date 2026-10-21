# Reproducibility and Data Provenance Guide

This document specifies what can be inspected, tested, and reproduced directly from a clone of `research-overview`, what requires local acquisition of public third-party datasets (`data/raw/`), and how data integrity is verified via SHA-256 digests.

---

## 1. Four Verification Tiers

### Tier 1 — Directly Inspectable Without Running Code
All empirical outputs, summary tables, and figures are committed and rendered directly in the repository:
- **Axis A (`notebooks/00_*.ipynb` to `07_*.ipynb`):** All 8 Jupyter notebooks are saved with their complete execution outputs, numerical tables, and embedded matplotlib figures.
- **Axis B (`experiments/sequential-financial-decisions/`):**
  - Documentary and conditional grids in [`experiments/sequential-financial-decisions/docs/`](../experiments/sequential-financial-decisions/docs/).
  - Locked CSV, JSON, and SVG artifacts for the `2024–2025` `C1–C2` comparison, the `C3` passive distribution reinvestment diagnostic, and the `2025–2026` documentary audit in [`experiments/sequential-financial-decisions/results/`](../experiments/sequential-financial-decisions/results/).

### Tier 2 — Automated Offline Verification (Fresh Clone, No `data/raw/` Required)
A fresh clone of `research-overview` can immediately execute `164` deterministic unit, accounting, and fixture-backed tests covering the sequential portfolio simulator, order sealing, `T+1` settlement, net sales financing (`H_FIN_NET`), dividend receivable accounting, and the April 20, 2026 documentary block:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Expected output without `data/raw/`:
```text
164 passed, 33 skipped
```
The 33 skipped tests are guarded by `@pytest.mark.skipif` because they cross-check the full historical rebuild against the untracked `data/raw/rl_market/` files.

Static analysis on all retained scripts and test suites can also be run offline:
```bash
python -m ruff check experiments/sequential-financial-decisions/scripts experiments/sequential-financial-decisions/tests
```

### Tier 3 — Full Historical Rebuild (With Local `data/raw/` Populated)
When `data/raw/fama_french/` and `data/raw/rl_market/` are present locally with the SHA-256 digests listed in Section 2:

1. **Full 197-test suite:**
   ```bash
   python -m pytest -q
   ```
   Expected output: `197 passed`.
2. **Byte-for-byte verification of locked Axis B results:**
   ```bash
   python experiments/sequential-financial-decisions/scripts/historical_c1_c2_comparison.py --check
   python experiments/sequential-financial-decisions/scripts/diagnose_distribution_reinvestment.py --check
   python experiments/sequential-financial-decisions/scripts/lock_second_historical_episode.py --check --check-block
   ```
   *(Note: To preserve cryptographic SHA-256 identity with the historical commits on `main`, locked JSON artifacts such as `statut_validation_documentaire.json` and `historical_c1_c2_2025_2026_lock_v1.json` retain their original `"RL/..."` path string keys inside JSON payloads, which the verification scripts automatically resolve to `experiments/sequential-financial-decisions/...`.)*
3. **Full re-execution of Axis A notebooks (`notebooks/00`–`07`):**
   Each notebook checks the SHA-256 digest of `data/raw/fama_french/F-F_Research_Data_Factors_daily_202608_sha256-2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db.zip` before executing deterministically from top to bottom (Notebooks `00`–`06` also include an in-memory download fallback from the Kenneth French Data Library if the local archive is absent, whereas Notebook `07` strictly requires the local archive).

### Tier 4 — Primary-Source Limitation (`2025–2026` Replication)
The second sequential episode (`2025-05-29` to `2026-05-29`) is intentionally halted at Cycle 47 (`2026-04-20`, status `DOCUMENTARY_BLOCK`) because public free sources disagree on the `SPY` opening price (`Yahoo Finance`: `708.78`, intraday range `706.14–709.91`; `Nasdaq`: `710.14`, flat unadjusted OHLC without volume). Resolving this block would require institutional consolidated tape data (`NYSE Daily TAQ` primary opening auction print), which is not included.

---

## 2. Public Data Sources and SHA-256 Provenance

Raw market and institutional files under `data/raw/` are excluded from Git via `.gitignore` pending verification of third-party redistribution rights. Every script and notebook verifies the exact SHA-256 digest of its inputs prior to execution.

### 2.1 Primary Track — Kenneth R. French Data Library (`data/raw/fama_french/`)

| Local Relative Path | Public Source | Vintage / Coverage | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `data/raw/fama_french/F-F_Research_Data_Factors_daily_202608_sha256-2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db.zip` | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html) (`F-F_Research_Data_Factors_daily_CSV.zip`) | Vintage `202608` (`1926-07-01` to `2026-08-31`; `26,317` daily sessions) | `2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db` |

### 2.2 Complementary Track — ETF & Regulatory Sources (`data/raw/`)

The machine-readable provenance manifest is tracked at [`experiments/sequential-financial-decisions/data_manifest.json`](../experiments/sequential-financial-decisions/data_manifest.json) (manifest SHA-256: `8cb901a45313764956abf9fd94c8baf0877a6f9b45e00a51685d70ae4fff56fc`). Key market data inputs used by the `SPY–BIL` sequential decision scripts:

| Dataset ID in `data_manifest.json` | Provider / Instrument | Local Relative Path | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `yahoo_spy_chart_ohlcv_20261019` | Yahoo Finance (`SPY` daily OHLCV + events) | `data/raw/rl_market/yahoo_spy_2007-05-25_2026-10-16_acquired-2026-10-19_sha256-b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52.json` | `b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52` |
| `yahoo_bil_chart_ohlcv_20261019` | Yahoo Finance (`BIL` daily OHLCV + events) | `data/raw/rl_market/yahoo_bil_2007-05-25_2026-10-16_acquired-2026-10-19_sha256-2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2.json` | `2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2` |
| `nasdaq_spy_ohlcv_20261019` | Nasdaq (`SPY` historical OHLCV cross-check) | `data/raw/rl_universe/nasdaq_spy_2026-10-19_sha256-79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5.json` | `79e03e22a87b3be3eb5f38ee7e47f6ef39cb268a1996ff94b115b2a846316ad5` |
| `ssga_spy_nav_20261019` | State Street Global Advisors (`SPY` daily NAV) | `data/raw/rl_research/state_street/navhist-us-en-spy_2026-10-19_sha256-80deb8db0ca46881dbec2b521487389d7c2290233ffe40b45c46b9c33699565f.xlsx` | `80deb8db0ca46881dbec2b521487389d7c2290233ffe40b45c46b9c33699565f` |
| `ssga_bil_nav_20261019` | State Street Global Advisors (`BIL` daily NAV) | `data/raw/rl_research/state_street/navhist-us-en-bil_2026-10-19_sha256-13ac00ae7dd64308bd1e548386a5fe8ae51c0f3983b51d2f2dd3789bbc3ae68a.xlsx` | `13ac00ae7dd64308bd1e548386a5fe8ae51c0f3983b51d2f2dd3789bbc3ae68a` |
| `ssga_spdr_distributions_20261019` | State Street Global Advisors (`SPY` & `BIL` distributions) | `data/raw/rl_research/state_street/spdr-etf-historical-distributions_2026-10-19_sha256-6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320.xlsx` | `6b65cbf956b5d25705d08470006a0e97e6a7d2a0d5cfd08b63f6f79783b06320` |

All additional regulatory and market-structure references (SEC `T+1` rule release `34-96930`, NYSE holiday calendar, DTCC corporate actions service description, and State Street statutory prospectuses) are listed with their exact URLs and SHA-256 digests in [`experiments/sequential-financial-decisions/data_manifest.json`](../experiments/sequential-financial-decisions/data_manifest.json).

---

## 3. Software Environment and Licensing Note

- **Tested Environment:** Python `3.11+` (`3.11.9` used for verification), `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `pytest`, and `ruff` as pinned in [`requirements.txt`](../requirements.txt).
- **Redistribution & Reuse Licensing:** Raw third-party datasets remain excluded from the repository until redistribution rights are verified. No open-source license file is currently attached to the code and documentation; reuse conditions remain to be defined by the author.
