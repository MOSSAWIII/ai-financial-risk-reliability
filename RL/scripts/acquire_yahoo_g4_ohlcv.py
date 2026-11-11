#!/usr/bin/env python3
"""Acquiert les réponses Yahoo IEF/GLD sur la fenêtre commune G4 candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import time as time_module
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "data" / "raw" / "rl_market"
DEFAULT_START = date(2007, 5, 25)
DEFAULT_END = date(2026, 10, 16)
ACQUISITION_DATE = date(2026, 11, 11)
TICKERS = ("IEF", "GLD")


def epoch_utc(day: date) -> int:
    return int(datetime.combine(day, time.min, tzinfo=timezone.utc).timestamp())


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
            request = Request(url, headers=headers)
            with urlopen(request, timeout=60) as response:
                payload = response.read()
            break
        except (HTTPError, URLError, TimeoutError) as exc:
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
    digest = hashlib.sha256(payload).hexdigest()
    filename = (
        f"yahoo_{ticker.lower()}_{start.isoformat()}_{end.isoformat()}_"
        f"acquired-{ACQUISITION_DATE.isoformat()}_sha256-{digest}.json"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / filename
    if destination.exists() and destination.read_bytes() != payload:
        raise RuntimeError(f"collision de contenu: {destination}")
    if not destination.exists():
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
    args = parser.parse_args()
    results = [
        acquire(ticker, DEFAULT_START, DEFAULT_END, args.output_dir)
        for ticker in TICKERS
    ]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
