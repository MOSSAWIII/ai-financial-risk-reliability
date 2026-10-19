#!/usr/bin/env python3
"""Compare un calendrier NYSE dérivé de règles officielles aux dates Yahoo.

Le script ne lit que les horodatages des deux réponses Yahoo déjà auditées. Il
ne modifie aucun prix et ne construit ni portefeuille, ni rendement, ni ordre.
"""

from __future__ import annotations

import argparse
import json
from calendar import monthrange
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "RL" / "data_manifest.json"
START = date(2018, 1, 2)
END = date(2026, 10, 16)
EXCEPTIONAL_CLOSURES = {date(2018, 12, 5), date(2025, 1, 9)}
# L'exception de fin d'exercice à la règle du vendredi observé a maintenu
# l'ouverture du 31 décembre 2021 lorsque le 1er janvier 2022 tombait samedi.
YEAR_END_OPEN_EXCEPTIONS = {date(2021, 12, 31)}
VERIFIED_EARLY_CLOSES = {
    date(2022, 11, 25),
    date(2023, 7, 3),
    date(2023, 11, 24),
    date(2024, 7, 3),
    date(2024, 11, 29),
    date(2024, 12, 24),
    date(2025, 7, 3),
    date(2025, 11, 28),
    date(2025, 12, 24),
    date(2026, 11, 27),
    date(2026, 12, 24),
}


def nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> date:
    first = date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    return first + timedelta(days=offset + 7 * (occurrence - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    last = date(year, month, monthrange(year, month)[1])
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def observed_fixed(day: date) -> date:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def easter_sunday(year: int) -> date:
    """Algorithme grégorien de Meeus/Jones/Butcher."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ell = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ell) // 451
    month = (h + ell - 7 * m + 114) // 31
    day = (h + ell - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def exchange_holidays(year: int) -> set[date]:
    holidays = {
        observed_fixed(date(year, 1, 1)),
        nth_weekday(year, 1, 0, 3),
        nth_weekday(year, 2, 0, 3),
        easter_sunday(year) - timedelta(days=2),
        last_weekday(year, 5, 0),
        observed_fixed(date(year, 7, 4)),
        nth_weekday(year, 9, 0, 1),
        nth_weekday(year, 11, 3, 4),
        observed_fixed(date(year, 12, 25)),
    }
    if year >= 2022:
        holidays.add(observed_fixed(date(year, 6, 19)))
    return holidays


def expected_sessions() -> set[date]:
    closed = set(EXCEPTIONAL_CLOSURES)
    for year in range(START.year, END.year + 1):
        closed.update(exchange_holidays(year))
    closed.difference_update(YEAR_END_OPEN_EXCEPTIONS)
    current = START
    sessions: set[date] = set()
    while current <= END:
        if current.weekday() < 5 and current not in closed:
            sessions.add(current)
        current += timedelta(days=1)
    return sessions


def manifest_index() -> dict[str, dict[str, Any]]:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload["datasets"]}


def yahoo_dates(path: Path) -> set[date]:
    result = json.loads(path.read_text(encoding="utf-8"))["chart"]["result"][0]
    timezone = ZoneInfo(result["meta"].get("exchangeTimezoneName", "America/New_York"))
    return {
        datetime.fromtimestamp(timestamp, tz=timezone).date()
        for timestamp in result["timestamp"]
        if START <= datetime.fromtimestamp(timestamp, tz=timezone).date() <= END
    }


def audit() -> dict[str, Any]:
    index = manifest_index()
    spy = yahoo_dates(ROOT / index["yahoo_spy_chart_ohlcv_20261019"]["local_file"])
    bil = yahoo_dates(ROOT / index["yahoo_bil_chart_ohlcv_20261019"]["local_file"])
    common = spy & bil
    expected = expected_sessions()
    early_in_range = {item for item in VERIFIED_EARLY_CLOSES if START <= item <= END}
    return {
        "scope": {"start": START.isoformat(), "end": END.isoformat()},
        "observed_common_yahoo_sessions": len(common),
        "rule_derived_nyse_sessions": len(expected),
        "missing_from_yahoo_common": sorted(item.isoformat() for item in expected - common),
        "unexpected_in_yahoo_common": sorted(item.isoformat() for item in common - expected),
        "verified_early_closes_in_scope": sorted(item.isoformat() for item in early_in_range),
        "verified_early_closes_absent_from_yahoo_common": sorted(
            item.isoformat() for item in early_in_range - common
        ),
        "exceptional_closures": sorted(item.isoformat() for item in EXCEPTIONAL_CLOSURES),
        "interpretation": (
            "Comparaison de dates uniquement; les règles annuelles 2018-2021 et le "
            "calendrier de règlement exhaustif ne sont pas déclarés intégralement prouvés."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
