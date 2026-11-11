from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g4_protocol_gate import (  # noqa: E402
    OUTPUT_PATH,
    build_report,
    render_report,
)


class G4ProtocolGateTests(unittest.TestCase):
    def test_g4_opens_only_the_data_audit(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(report["verdict"], "READY_FOR_G4_DATA_AUDIT")
        self.assertIs(report["performance_computation_authorized"], False)
        self.assertEqual(report["rl_algorithms_authorized"], [])

    def test_four_asset_quarter_grid_has_35_actions(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(len(report["candidate_instruments"]), 4)
        self.assertEqual(report["action_count"], 35)

    def test_all_protocol_invariants_pass(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(len(report["checks"]), 9)
        self.assertTrue(all(report["checks"].values()))

    def test_versioned_report_is_reproducible(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(
            OUTPUT_PATH.read_text(encoding="utf-8"), render_report(report)
        )

    def test_canonical_validation_remains_negative_for_rl_authorization(self) -> None:
        validation = json.loads(
            (
                ROOT
                / "RL"
                / "results"
                / "g3_learning_value"
                / "canonical_validation.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(validation["status"], "G3A_CANONICAL_VALIDATED")
        self.assertIs(validation["ppo_cql_iql_authorized"], False)


if __name__ == "__main__":
    unittest.main()
