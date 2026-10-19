#!/usr/bin/env python3
"""Acquisition ciblée des réponses Yahoo Finance chart pour SPY et BIL.

Le script conserve exactement les octets JSON reçus. Il refuse d'écraser un
fichier existant et n'effectue aucune transformation financière.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time as time_module
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

import requests


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "raw" / "rl_market"
DEFAULT_START = date(2007, 5, 25)
DEFAULT_END = date(2026, 10, 16)
ACQUISITION_DATE = date(2026, 10, 19)
TICKERS = ("SPY", "BIL")


def epoch_utc(day: date) -> int:
    return int(datetime.combine(day, time.min, tzinfo=timezone.utc).timestamp())


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def acquire(ticker: str, start: date, end: date, output_dir: Path) -> dict[str, object]:
    params = {
        "period1": epoch_utc(start),
        "period2": epoch_utc(end + timedelta(days=1)),
        "interval": "1d",
        "events": "div,splits",
        "includeAdjustedClose": "true",
    }
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?{urlencode(params)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; academic-data-audit/1.0)",
        "Accept": "application/json",
    }
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=(15, 60))
            response.raise_for_status()
            payload = response.content
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time_module.sleep(2**attempt)
    else:
        raise RuntimeError(f"échec réseau après trois tentatives pour {ticker}") from last_error
    document = json.loads(payload.decode("utf-8"))
    chart = document.get("chart") or {}
    if chart.get("error") is not None or not chart.get("result"):
        raise RuntimeError(f"réponse Yahoo invalide pour {ticker}: {chart.get('error')}")
    result = chart["result"][0]
    if (result.get("meta") or {}).get("symbol") != ticker:
        raise RuntimeError(f"symbole inattendu dans la réponse {ticker}")
    timestamps = result.get("timestamp") or []
    if not timestamps:
        raise RuntimeError(f"aucune observation reçue pour {ticker}")

    digest = sha256_bytes(payload)
    filename = (
        f"yahoo_{ticker.lower()}_{start.isoformat()}_{end.isoformat()}_"
        f"acquired-{ACQUISITION_DATE.isoformat()}_sha256-{digest}.json"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / filename
    if destination.exists():
        if destination.read_bytes() != payload:
            raise RuntimeError(f"collision de nom avec contenu différent: {destination}")
    else:
        destination.write_bytes(payload)
    return {
        "ticker": ticker,
        "url": url,
        "local_file": str(destination.relative_to(ROOT)).replace("\\", "/"),
        "bytes": len(payload),
        "sha256": digest,
        "observations": len(timestamps),
        "first_timestamp": min(timestamps),
        "last_timestamp": max(timestamps),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--start", type=date.fromisoformat, default=DEFAULT_START)
    parser.add_argument("--end", type=date.fromisoformat, default=DEFAULT_END)
    args = parser.parse_args()
    if args.end < args.start:
        parser.error("--end doit être postérieur ou égal à --start")
    results = [acquire(ticker, args.start, args.end, args.output_dir) for ticker in TICKERS]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
