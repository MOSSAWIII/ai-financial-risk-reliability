from __future__ import annotations

import math
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from g4_transition_builder import (  # noqa: E402
    ASSETS,
    ControlledState,
    G4TransitionError,
    MarketBar,
    apply_controlled_transition,
    build_market_transitions,
    feasible_actions,
    render_jsonl,
    simplex_actions,
    turnover,
)


def synthetic_series(weeks: int = 80):
    start = date(2020, 1, 6)
    output = {symbol: {} for symbol in ASSETS}
    levels = {symbol: 100.0 + 5.0 * i for i, symbol in enumerate(ASSETS)}
    loadings = {"SPY": 0.0010, "IEF": 0.0003, "GLD": 0.0006, "BIL": 0.00005}
    for offset in range(weeks * 7):
        day = start + timedelta(days=offset)
        if day.weekday() >= 5:
            continue
        for symbol in ASSETS:
            levels[symbol] *= math.exp(loadings[symbol] * (1 if (offset // 14) % 2 == 0 else -0.4))
            distribution = 0.0
            if symbol in {"SPY", "IEF", "BIL"} and offset in {140, 280, 420}:
                distribution = {"SPY": 0.5, "IEF": 0.2, "BIL": 0.1}[symbol]
            output[symbol][day] = MarketBar(day, levels[symbol], distribution)
    return output


class G4TransitionBuilderTests(unittest.TestCase):
    def test_simplex_is_exact_and_has_35_actions(self):
        actions = simplex_actions()
        self.assertEqual(35, len(actions))
        self.assertEqual(len(actions), len(set(actions)))
        for action in actions:
            self.assertTrue(all(value in {0.0, 0.25, 0.5, 0.75, 1.0} for value in action))
            self.assertAlmostEqual(1.0, sum(action))

    def test_turnover_budget_is_endogenous_and_irreversible(self):
        state = ControlledState((0.25, 0.25, 0.25, 0.25), 0.50)
        target = (0.50, 0.25, 0.25, 0.0)
        self.assertAlmostEqual(0.25, turnover(state.inherited_weights, target))
        following, diagnostics = apply_controlled_transition(state, target, (1.02, 1.0, 0.99, 1.0))
        self.assertAlmostEqual(0.25, following.remaining_turnover_budget)
        self.assertAlmostEqual(0.25, diagnostics["turnover"])
        self.assertNotEqual(target, following.inherited_weights)

    def test_action_over_budget_is_rejected(self):
        state = ControlledState((1.0, 0.0, 0.0, 0.0), 0.10)
        with self.assertRaisesRegex(G4TransitionError, "infaisable"):
            apply_controlled_transition(state, (0.75, 0.25, 0.0, 0.0), (1.0, 1.0, 1.0, 1.0))
        self.assertEqual(((1.0, 0.0, 0.0, 0.0),), feasible_actions(state.inherited_weights, 0.10))

    def test_distribution_is_credited_only_in_subsequent_outcome(self):
        series = synthetic_series()
        rows = build_market_transitions(series)
        event_day = date(2021, 3, 1)
        prior = [row for row in rows if date.fromisoformat(row["decision_date"]) < event_day]
        self.assertTrue(prior)
        row = prior[-1]
        self.assertLess(date.fromisoformat(row["decision_date"]), event_day)
        # Les caract�ristiques s'arr�tent � la d�cision; la distribution future
        # n'entre que dans le facteur r�alis� vers la d�cision suivante.
        without_distribution = synthetic_series()
        without_distribution["SPY"][event_day] = MarketBar(
            event_day, without_distribution["SPY"][event_day].close, 0.0
        )
        comparison = build_market_transitions(without_distribution)
        other = next(item for item in comparison if item["decision_date"] == row["decision_date"])
        self.assertEqual(row["features"], other["features"])
        self.assertGreater(row["outcome_gross_returns"]["SPY"], other["outcome_gross_returns"]["SPY"])

    def test_future_shock_cannot_rewrite_past_states(self):
        original = synthetic_series()
        before = build_market_transitions(original)
        shock_day = date(2021, 3, 1)
        shocked = synthetic_series()
        for symbol in ASSETS:
            bar = shocked[symbol][shock_day]
            shocked[symbol][shock_day] = MarketBar(shock_day, bar.close * (1.8 if symbol == "SPY" else 1.0), bar.distribution)
        after = build_market_transitions(shocked)
        left = [row for row in before if date.fromisoformat(row["decision_date"]) < shock_day]
        right = [row for row in after if date.fromisoformat(row["decision_date"]) < shock_day]
        for first, second in zip(left, right):
            self.assertEqual(first["decision_date"], second["decision_date"])
            self.assertEqual(first["features"], second["features"])
            self.assertEqual(first["covariance_52w_annualized"], second["covariance_52w_annualized"])

    def test_decision_is_last_common_session_of_week(self):
        rows = build_market_transitions(synthetic_series())
        self.assertTrue(rows)
        self.assertTrue(all(date.fromisoformat(row["decision_date"]).weekday() == 4 for row in rows))

    def test_serialization_is_byte_deterministic(self):
        rows = build_market_transitions(synthetic_series())
        self.assertEqual(render_jsonl(rows), render_jsonl(build_market_transitions(synthetic_series())))


if __name__ == "__main__":
    unittest.main()
