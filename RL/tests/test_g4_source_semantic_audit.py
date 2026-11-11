from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from g4_source_semantic_audit import (  # noqa: E402
    EXPECTED,
    G4SourceAuditError,
    canonical_document,
    sha256_bytes,
)


def payload(symbol: str, rows: int, dividends: int = 0, splits: int = 0) -> bytes:
    timestamps = [1180099800 + 86400 * index for index in range(rows)]
    values = [100.0 + index for index in range(rows)]
    events = {
        "dividends": {str(timestamps[index]): {"date": timestamps[index], "amount": 0.1} for index in range(dividends)},
        "splits": {str(timestamps[index]): {"date": timestamps[index], "numerator": 2.0, "denominator": 1.0, "splitRatio": "2:1"} for index in range(splits)},
    }
    document = {
        "chart": {"result": [{
            "meta": {
                "symbol": symbol,
                "currency": "USD",
                "exchangeName": "PCX",
                "fullExchangeName": "NYSEArca",
                "exchangeTimezoneName": "America/New_York",
                "dataGranularity": "1d",
                "regularMarketPrice": 999.0,
            },
            "timestamp": timestamps,
            "events": events,
            "indicators": {
                "quote": [{name: values for name in ("open", "high", "low", "close", "volume")}],
                "adjclose": [{"adjclose": values}],
            },
        }], "error": None}
    }
    return json.dumps(document, separators=(",", ":")).encode()


class SemanticAuditTests(unittest.TestCase):
    def setUp(self):
        self.original = dict(EXPECTED)

    def tearDown(self):
        EXPECTED.clear()
        EXPECTED.update(self.original)

    def test_live_metadata_does_not_change_canonical_hash(self):
        EXPECTED["SPY"] = {"rows": 3, "start": "2007-05-25", "end": "2007-05-27", "dividends": 1, "splits": 0}
        first = payload("SPY", 3, dividends=1)
        document = json.loads(first)
        document["chart"]["result"][0]["meta"]["regularMarketPrice"] = 1234.0
        second = json.dumps(document, separators=(",", ":")).encode()
        canonical_first, _ = canonical_document(first, "SPY")
        canonical_second, _ = canonical_document(second, "SPY")
        self.assertNotEqual(sha256_bytes(first), sha256_bytes(second))
        self.assertEqual(sha256_bytes(canonical_first), sha256_bytes(canonical_second))

    def test_historical_value_change_changes_canonical_hash(self):
        EXPECTED["SPY"] = {"rows": 3, "start": "2007-05-25", "end": "2007-05-27", "dividends": 0, "splits": 0}
        first = payload("SPY", 3)
        document = json.loads(first)
        document["chart"]["result"][0]["indicators"]["quote"][0]["close"][1] = 999.0
        second = json.dumps(document, separators=(",", ":")).encode()
        canonical_first, _ = canonical_document(first, "SPY")
        canonical_second, _ = canonical_document(second, "SPY")
        self.assertNotEqual(sha256_bytes(canonical_first), sha256_bytes(canonical_second))

    def test_structural_divergence_is_a_hard_failure(self):
        EXPECTED["SPY"] = {"rows": 4, "start": "2007-05-25", "end": "2007-05-28", "dividends": 0, "splits": 0}
        with self.assertRaisesRegex(G4SourceAuditError, "structure historique divergente"):
            canonical_document(payload("SPY", 3), "SPY")


if __name__ == "__main__":
    unittest.main()
