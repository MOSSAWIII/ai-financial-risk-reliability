from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g4_data_audit import build_report  # noqa: E402


class G4DataAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report(ROOT)

    def test_audit_passes_without_performance_computation(self) -> None:
        self.assertEqual(self.report["verdict"], "G4_1_DATA_AUDIT_PASSED")
        self.assertIs(self.report["performance_computation_performed"], False)
        self.assertIs(self.report["training_authorized"], False)

    def test_four_asset_common_calendar_is_exact(self) -> None:
        calendar = self.report["common_calendar"]
        self.assertEqual(calendar["common_rows"], 4878)
        self.assertEqual(calendar["common_start"], "2007-05-30")
        self.assertEqual(calendar["common_end"], "2026-10-16")

    def test_each_market_source_passes_structural_assertions(self) -> None:
        for source in self.report["market_sources"].values():
            self.assertTrue(all(source["assertions"].values()))

    def test_issuer_sources_have_required_structure(self) -> None:
        for source in self.report["issuer_sources"].values():
            self.assertTrue(all(source["assertions"].values()))


if __name__ == "__main__":
    unittest.main()
