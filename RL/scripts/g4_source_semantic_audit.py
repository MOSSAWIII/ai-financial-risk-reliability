#!/usr/bin/env python3
"""Audite l'immuabilit� s�mantique des quatre r�ponses Yahoo G4.

Yahoo inclut dans ``meta`` des champs de march� en direct qui font varier le
SHA-256 brut sans modifier la tranche historique demand�e. Ce module conserve
donc les deux preuves : empreinte des octets re�us et empreinte canonique des
seuls champs historiques utilis�s par G4. Il ne calcule aucun rendement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ASSETS = ("SPY", "IEF", "GLD", "BIL")
PERIOD1 = 1180051200
PERIOD2 = 1792195200
EXPECTED = {
    "SPY": {"rows": 4880, "start": "2007-05-25", "end": "2026-10-16", "dividends": 78, "splits": 0},
    "IEF": {"rows": 4880, "start": "2007-05-25", "end": "2026-10-16", "dividends": 233, "splits": 0},
    "GLD": {"rows": 4880, "start": "2007-05-25", "end": "2026-10-16", "dividends": 0, "splits": 0},
    "BIL": {"rows": 4878, "start": "2007-05-30", "end": "2026-10-16", "dividends": 128, "splits": 1},
}
FROZEN_RAW_SHA256 = {
    "SPY": "b77099e8c46a954f045e95432d2b6220a526f15322c87b877aafae628da14f52",
    "IEF": "9daa83ee383e208e1b4c09e0148b19f92d82049056e71a967323cd54dc744108",
    "GLD": "39b8398c597fb20f03330319904ae9f9549b84e8e6b66d32e509a80daeae4172",
    "BIL": "2eaa0529ae97b0e8e078285e8daa5247176c42b6df114019d6e0e2c4b3f838d2",
}


class G4SourceAuditError(RuntimeError):
    """La tranche historique Yahoo n'est pas conforme au gel G4.1."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_event_map(events: dict[str, Any], name: str) -> dict[str, Any]:
    values = events.get(name) or {}
    return {str(key): values[key] for key in sorted(values, key=lambda item: int(item))}


def canonical_document(payload: bytes, expected_symbol: str) -> tuple[bytes, dict[str, Any]]:
    document = json.loads(payload.decode("utf-8"))
    try:
        result = document["chart"]["result"][0]
        metadata = result["meta"]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise G4SourceAuditError(f"r�ponse Yahoo invalide pour {expected_symbol}") from exc
    required_meta = {
        "symbol": metadata.get("symbol"),
        "currency": metadata.get("currency"),
        "exchangeName": metadata.get("exchangeName"),
        "fullExchangeName": metadata.get("fullExchangeName"),
        "exchangeTimezoneName": metadata.get("exchangeTimezoneName"),
        "dataGranularity": metadata.get("dataGranularity"),
    }
    if required_meta["symbol"] != expected_symbol or required_meta["currency"] != "USD":
        raise G4SourceAuditError(f"symbole ou devise inattendu pour {expected_symbol}")
    if required_meta["exchangeTimezoneName"] != "America/New_York" or required_meta["dataGranularity"] != "1d":
        raise G4SourceAuditError(f"horloge ou granularit� inattendue pour {expected_symbol}")
    fields = {name: quote.get(name) for name in ("open", "high", "low", "close", "volume")}
    lengths = {"timestamp": len(timestamps), **{name: len(values or []) for name, values in fields.items()}}
    if len(set(lengths.values())) != 1 or any(value is None for values in fields.values() for value in values):
        raise G4SourceAuditError(f"tableaux d�salign�s ou incomplets pour {expected_symbol}")
    events = result.get("events") or {}
    canonical = {
        "schema_version": "g4-yahoo-causal-slice-1.2",
        "meta": required_meta,
        "timestamp": timestamps,
        "events": {
            "dividends": _canonical_event_map(events, "dividends"),
            "splits": _canonical_event_map(events, "splits"),
        },
        "indicators": {"quote": [{"close": fields["close"]}]},
    }
    rendered = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    timezone = ZoneInfo("America/New_York")
    dates = [datetime.fromtimestamp(int(value), timezone).date().isoformat() for value in timestamps]
    observed = {
        "rows": len(timestamps),
        "start": min(dates),
        "end": max(dates),
        "dividends": len(canonical["events"]["dividends"]),
        "splits": len(canonical["events"]["splits"]),
    }
    if observed != EXPECTED[expected_symbol]:
        raise G4SourceAuditError(
            f"structure historique divergente pour {expected_symbol}: {observed} != {EXPECTED[expected_symbol]}"
        )
    return rendered, observed


def yahoo_url(symbol: str) -> str:
    query = urlencode({
        "period1": PERIOD1,
        "period2": PERIOD2,
        "interval": "1d",
        "events": "div,splits",
        "includeAdjustedClose": "true",
    })
    return f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{query}"


def download(symbol: str) -> bytes:
    request = Request(
        yahoo_url(symbol),
        headers={"User-Agent": "Mozilla/5.0 (compatible; g4-semantic-audit/1.0)", "Accept": "application/json"},
    )
    with urlopen(request, timeout=90) as response:
        return response.read()


def audit_sources(output_dir: Path, local_inputs: dict[str, Path] | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sources: dict[str, Any] = {}
    for symbol in ASSETS:
        payload = local_inputs[symbol].read_bytes() if local_inputs else download(symbol)
        canonical, observed = canonical_document(payload, symbol)
        raw_sha = sha256_bytes(payload)
        canonical_sha = sha256_bytes(canonical)
        canonical_path = output_dir / f"{symbol.lower()}_historical_slice_sha256-{canonical_sha}.json"
        canonical_path.write_bytes(canonical)
        sources[symbol] = {
            **observed,
            "url": yahoo_url(symbol),
            "raw_bytes": len(payload),
            "raw_sha256": raw_sha,
            "frozen_raw_sha256": FROZEN_RAW_SHA256[symbol],
            "raw_sha_matches_g4_1": raw_sha == FROZEN_RAW_SHA256[symbol],
            "canonical_bytes": len(canonical),
            "canonical_sha256": canonical_sha,
            "canonical_file": canonical_path.name,
        }
    report = {
        "schema_version": "g4-source-semantic-audit-1.0",
        "verdict": "G4_HISTORICAL_SLICES_STRUCTURALLY_CONFORMANT",
        "scope": "SOURCE_BYTES_AND_HISTORICAL_FIELDS_ONLY_NO_RETURNS",
        "canonical_exclusions": [
            "live_meta_fields",
            "adjclose_revised_by_distributions_after_the_requested_period",
            "open_high_low_volume_not_consumed_by_the_g4_transition_builder"
        ],
        "performance_computation_performed": False,
        "sources": sources,
    }
    (output_dir / "source_audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--input", action="append", default=[], metavar="SYMBOL=PATH")
    args = parser.parse_args()
    local: dict[str, Path] = {}
    for item in args.input:
        symbol, value = item.split("=", 1)
        local[symbol.upper()] = Path(value)
    if local and set(local) != set(ASSETS):
        raise G4SourceAuditError("quatre entr�es locales SPY/IEF/GLD/BIL sont requises")
    report = audit_sources(args.output_dir, local or None)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
