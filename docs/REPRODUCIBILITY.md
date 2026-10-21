# Reproducibility and Data Provenance Guide

This document specifies what can be inspected, tested, and reproduced directly from a clone of `research-overview`, what requires local acquisition of public third-party datasets (`data/raw/`), and how data integrity is verified via SHA-256 digests.

---

## 1. Four Levels of Evidence

The levels below are ordered by how much a reader must have in hand. A result at one level is not thereby established at the next.

### Level 1 — Visible (read on GitHub, nothing to run)
- **Notebooks `00`–`07`** are saved with their execution outputs, tables and figures. Reading them shows what was computed in the author's environment; it does not by itself show that a clean re-execution gives the same output.
- **Locked outputs** of the sequential study (CSV, JSON, SVG) under [`experiments/sequential-financial-decisions/results/`](../experiments/sequential-financial-decisions/results/) and the documentary grids under [`docs/`](../experiments/sequential-financial-decisions/docs/).

### Level 2 — Auditable without raw data (fresh clone)
Tracked fixtures, SHA-256 files and result tables allow deterministic checks of the sequential simulator's accounting logic (ledger invariants, order sealing, `T+1` settlement, `H_FIN_NET`, dividend receivables, the Episode 2 documentary block) against committed artifacts:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

Result of this command in a clean clone without `data/raw/`: `164 passed, 33 skipped`. The 33 skipped tests rebuild outputs from the raw market files and are skipped with the reason `sources historiques locales exclues de GitHub`. These tests concern Study II only; **no automated test covers the notebooks of Study I.**

```bash
python -m ruff check experiments/sequential-financial-decisions/scripts experiments/sequential-financial-decisions/tests
```

### Level 3 — Reproducible locally by the author (archived inputs present)
With the manifest-listed files under both `data/raw/` and `data/processed/` populated, the skipped tests run and the locked outputs are rebuilt byte for byte. The presence of `data/raw/rl_market/` activates these tests; the derived audit files under `data/processed/rl/` are also required:

```bash
python -m pytest -q                      # 197 passed on the author's machine
python experiments/sequential-financial-decisions/scripts/historical_c1_c2_comparison.py --check
python experiments/sequential-financial-decisions/scripts/diagnose_distribution_reinvestment.py --check
python experiments/sequential-financial-decisions/scripts/lock_second_historical_episode.py --check --check-block
```

Locked JSON artifacts such as `statut_validation_documentaire.json` and `historical_c1_c2_2025_2026_lock_v1.json` keep their original `"RL/..."` path strings so that their SHA-256 digests match the archived commits on `main`; the scripts resolve these paths to `experiments/sequential-financial-decisions/...`. Locked CSV files keep their original line endings (see the study's `.gitattributes`).

The forecasting notebooks `00`–`07` load the Fama–French archive `data/raw/fama_french/F-F_Research_Data_Factors_daily_202608_sha256-2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db.zip`. According to their code, notebooks `00`–`06` can fall back to downloading the archive in memory if it is absent, while notebook `07` requires the local archive. Their re-execution from a clean clone has **not** been tested.

### Level 4 — Reproducible by a third party who obtains the data
A third party must download the public sources listed in Section 2, place them under the paths shown, and check the digests. This depends on the continued availability of those sources and on their terms of use. The second sequential episode (`2025-05-29` to `2026-05-29`) cannot be completed even with these data: Cycle 47 (`2026-04-20`) is `DOCUMENTARY_BLOCK` because the Yahoo (`Open 708.78`, `High 709.91`, `Low 706.14`) and Nasdaq (`Open = High = Low = Close = 710.14`, no volume) `SPY` records are incompatible. Resolving it would require a primary source (NYSE Daily TAQ), which has not been acquired; this repository does not decide which public source is correct.

---

## 2. Public Data Sources and SHA-256 Provenance

Raw market and institutional files under `data/raw/` are excluded from Git pending verification of third-party redistribution rights. The tracked [`data_manifest.json`](../experiments/sequential-financial-decisions/data_manifest.json) records their SHA-256 digests and `scripts/verify_local_data.py` checks local files against it; the Fama–French archive filename embeds its own digest. No claim is made that every script or notebook independently re-verifies digests.

### 2.1 Research Study I — Kenneth R. French Data Library (`data/raw/fama_french/`)

| Local Relative Path | Public Source | Vintage / Coverage | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `data/raw/fama_french/F-F_Research_Data_Factors_daily_202608_sha256-2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db.zip` | [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_factors.html) (`F-F_Research_Data_Factors_daily_CSV.zip`) | Vintage `202608` (`1926-07-01` to `2026-08-31`; `26,317` daily sessions) | `2f29e22546069914890a712680a6f81f3680ebc3543b52864484d209ca13a7db` |

### 2.2 Research Study II — ETF & Regulatory Sources (`data/raw/`)

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

## 3. Software Environment, Verification Record and Licensing

- **Environment used for the local archive checks reported here:** Windows, Python `3.11.5`, `numpy 2.2.1`, `pandas 2.2.3`, `matplotlib 3.10.0`, `scikit-learn 1.6.1`, `openpyxl 3.1.5`, `pytest 8.3.5`, `ruff 0.11.2`. [`requirements.txt`](../requirements.txt) declares compatible *version ranges*; it is not a lockfile. Installation into a fresh Windows/Python `3.11.5` virtual environment was also verified, followed by the Level 2 tests and Ruff check.
- **What was actually run (clean local clone of the branch, no `data/raw/`):** `python -m pytest -q` → `164 passed, 33 skipped`; `ruff check` on the scripts and tests → no findings. All 33 skips carry the same reason (`sources historiques locales exclues de GitHub`) and are guarded by `skipif` on the absence of `data/raw/rl_market/`.
- **What was actually run (local machine with the manifest-listed `data/raw/` and `data/processed/` files present):** `python -m pytest -q` → `197 passed`; the three `--check` commands of Level 3 completed successfully; and `python experiments/sequential-financial-decisions/scripts/verify_local_data.py` checked `51` manifest entries with no failure.
- **Not verified:** execution on Linux/macOS; full top-to-bottom re-execution of the notebooks in a clean clone; availability of the third-party URLs at a later date.
- **Language:** notebook prose and many identifiers (file and column names) are in French; each notebook starts with an English overview.
- **Redistribution & Reuse Licensing:** Raw third-party datasets remain excluded from the repository until redistribution rights are verified. No license file is attached to the code and documentation; reuse conditions remain to be defined by the author.
