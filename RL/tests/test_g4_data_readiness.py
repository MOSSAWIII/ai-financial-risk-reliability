from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g4_data_readiness import build_report  # noqa: E402


class G4DataReadinessTests(unittest.TestCase):
    def test_all_frozen_requirements_are_verified(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(report["verified_requirements"], 10)
        self.assertEqual(report["blockers"], [])

    def test_readiness_authorizes_only_the_statistical_audit(self) -> None:
        report = build_report(ROOT)
        self.assertEqual(report["verdict"], "READY_FOR_G4_STATISTICAL_AUDIT")
        self.assertIs(report["statistical_audit_authorized"], True)
        self.assertIs(report["performance_computation_authorized"], False)

    def test_missing_source_remains_a_hard_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_dir = root / "RL" / "configs"
            config_dir.mkdir(parents=True)
            requirements = {
                "requirements": [
                    {
                        "asset": "IEF",
                        "role": "MARKET_OHLCV",
                        "dataset_id": "absent",
                        "expected_sha256": "0" * 64,
                    }
                ]
            }
            (config_dir / "g4_data_requirements.json").write_text(
                json.dumps(requirements), encoding="utf-8"
            )
            (root / "RL" / "data_manifest.json").write_text(
                json.dumps({"datasets": []}), encoding="utf-8"
            )
            report = build_report(root)
        self.assertEqual(report["verdict"], "G4_1_DOCUMENTARY_BLOCK")
        self.assertIs(report["statistical_audit_authorized"], False)
        self.assertEqual(report["blockers"][0]["status"], "MISSING_MANIFEST_ENTRY")


if __name__ == "__main__":
    unittest.main()
