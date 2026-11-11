from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g4_data_readiness import build_report  # noqa: E402


class G4DataReadinessTests(unittest.TestCase):
    def test_audit_is_documentary_only(self) -> None:
        report = build_report(ROOT)
        self.assertIs(report["performance_computation_authorized"], False)

    def test_spy_and_bil_sources_are_reused_exactly(self) -> None:
        report = build_report(ROOT)
        for row in report["requirements"]:
            if row["asset"] in {"SPY", "BIL"}:
                self.assertEqual(row["status"], "VERIFIED")

    def test_missing_ief_and_gld_sources_block_g4_1(self) -> None:
        report = build_report(ROOT)
        blockers = {(row["asset"], row["role"]) for row in report["blockers"]}
        self.assertEqual(
            blockers,
            {
                ("IEF", "MARKET_OHLCV"),
                ("IEF", "DISTRIBUTIONS"),
                ("GLD", "MARKET_OHLCV"),
                ("GLD", "ISSUER_HISTORY_AND_DISTRIBUTION_POLICY"),
            },
        )
        self.assertEqual(report["verdict"], "G4_1_DOCUMENTARY_BLOCK")

    def test_no_statistical_audit_is_authorized_while_blocked(self) -> None:
        report = build_report(ROOT)
        self.assertIs(report["statistical_audit_authorized"], False)


if __name__ == "__main__":
    unittest.main()
