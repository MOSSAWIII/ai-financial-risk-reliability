from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sequentiality_test import (  # noqa: E402
    SequentialityError,
    default_model,
    evaluate_cost,
    run_experiment,
)


class SequentialityV2Tests(unittest.TestCase):
    def test_zero_cost_is_a_negative_control(self) -> None:
        result = evaluate_cost(default_model(), 0)
        self.assertAlmostEqual(result.sequential_value_log, 0.0, places=14)
        self.assertAlmostEqual(
            result.dynamic_expected_log_growth,
            result.myopic_expected_log_growth,
            places=14,
        )

    def test_one_step_horizon_is_a_negative_control(self) -> None:
        for cost_bps in (0, 5, 10, 25, 50, 100):
            result = evaluate_cost(default_model(horizon=1), cost_bps)
            self.assertAlmostEqual(result.sequential_value_log, 0.0, places=14)

    def test_costs_and_inherited_position_create_sequential_value(self) -> None:
        result = evaluate_cost(default_model(), 10)
        self.assertGreater(result.sequential_value_log, 0.0)
        self.assertGreater(result.wealth_uplift, 0.0)
        self.assertTrue(result.reachable_disagreement)
        self.assertEqual(result.dynamic_initial_actions["RISK_ON"], 1.0)
        self.assertEqual(result.myopic_initial_actions["RISK_ON"], 0.5)
        self.assertEqual(result.dynamic_initial_actions["RISK_OFF"], 0.0)
        self.assertEqual(result.myopic_initial_actions["RISK_OFF"], 0.5)

    def test_dynamic_program_weakly_dominates_myopic_policy(self) -> None:
        for cost_bps in (0, 5, 10, 25, 50, 100):
            result = evaluate_cost(default_model(), cost_bps)
            self.assertGreaterEqual(result.sequential_value_log, -1e-12)

    def test_invalid_probability_row_is_rejected(self) -> None:
        model = default_model()
        invalid_transition = {
            **model.transition,
            "RISK_ON": {"RISK_ON": 0.8, "RISK_OFF": 0.3},
        }
        invalid = replace(model, transition=invalid_transition)
        with self.assertRaises(SequentialityError):
            invalid.validate()

    def test_full_protocol_passes_gate_g1(self) -> None:
        report = run_experiment()
        self.assertEqual(report["gate_g1"], "PASS")
        self.assertTrue(all(report["controls"].values()))


if __name__ == "__main__":
    unittest.main()
