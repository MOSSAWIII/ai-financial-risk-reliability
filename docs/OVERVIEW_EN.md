# Research overview (English)

**Financial risk forecasting under changing conditions** — [principal documentation en français](../README.md).

This is an **ongoing research project**, not a finished scientific result or an investment strategy.

## Research question

How reliable are forecasts of future market risk when the economic environment changes? The work examines predictive errors, conditional underestimation, temporal stability, uncertainty, and whether a forecasting method recognizes the limits of its own predictions.

## Current empirical approach

- Define and audit five-session forward realized volatility from US market-return data.
- Compare simple baselines with a small number of machine-learning methods.
- Keep chronological splits explicit and inspect overlapping-window dependence.
- Diagnose errors by risk regime rather than relying solely on average accuracy.
- Record methodological decisions, data provenance and negative or inconclusive results.

The [main README](../README.md) records the precise stage of this research; it takes precedence over this high-level introduction.

## Related exploratory track

The [RL subproject](../RL/README.md) investigates sequential financial decisions and synthetic accounting for an SPY–BIL mandate. It is **pre-experimental**: documentation and data/accounting validation do not establish a trained RL agent, executed strategy, profitable backtest, or investment performance.

## Boundaries

A technically correct realized-volatility calculation is not proof that it captures all economically relevant risk. In-sample fit and exploratory benchmarks are not investment evidence. Raw datasets are deliberately excluded from this repository; their provenance and checks are documented.

**Navigation:** [Main project](../README.md) · [Phase 0](PHASE_0_CADRAGE_SCIENTIFIQUE.md) · [Decision log](JOURNAL_DECISIONS.md) · [RL workstream](../RL/README.md).
