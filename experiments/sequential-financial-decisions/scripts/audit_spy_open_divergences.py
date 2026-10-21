#!/usr/bin/env python3
"""Audit ciblé des divergences quotidiennes SPY Yahoo/Nasdaq.

Ce contrôle ne reconstruit ni ordre, ni portefeuille, ni performance. Il lit
uniquement les sources locales déjà inscrites au manifeste et produit un
diagnostic descriptif sur les ouvertures et la fenêtre candidate depuis 2018.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

import audit_spy_bil_market_prices as base


OPEN_ALERT_BPS = 10.0
CANDIDATE_START = pd.Timestamp("2018-01-01")
PRIORITY_DATES = [
    "2016-11-07",
    "2017-05-17",
    "2019-08-14",
    "2021-03-09",
    "2026-04-17",
    "2026-04-20",
]
FIELDS = ["open", "high", "low", "close", "volume"]


def scalar(value: Any) -> float | int | bool | None:
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    number = float(value)
    return int(number) if number.is_integer() else number


def merged_sources() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[dict[str, Any]], list[dict[str, Any]]]:
    _, index = base.load_manifest()
    yahoo_spy, _, _, spy_splits = base.parse_yahoo(
        base.source_path(index, "yahoo_spy_chart_ohlcv_20261019")
    )
    yahoo_bil, _, _, bil_splits = base.parse_yahoo(
        base.source_path(index, "yahoo_bil_chart_ohlcv_20261019")
    )
    nasdaq_spy = base.parse_nasdaq(base.source_path(index, "nasdaq_spy_ohlcv_20261019"))
    merged = yahoo_spy[["date", *FIELDS]].merge(
        nasdaq_spy[["date", *FIELDS]], on="date", suffixes=("_yahoo", "_nasdaq")
    )
    return merged, yahoo_spy, yahoo_bil, spy_splits, bil_splits


def open_alerts(merged: pd.DataFrame) -> list[dict[str, Any]]:
    frame = merged.copy()
    frame["open_difference_bps"] = (
        frame["open_yahoo"] / frame["open_nasdaq"] - 1.0
    ) * 10_000.0
    frame = frame.loc[frame["open_difference_bps"].abs() > OPEN_ALERT_BPS]
    rows: list[dict[str, Any]] = []
    for row in frame.itertuples(index=False):
        yahoo_in_nasdaq = row.low_nasdaq <= row.open_yahoo <= row.high_nasdaq
        nasdaq_in_yahoo = row.low_yahoo <= row.open_nasdaq <= row.high_yahoo
        mutually_compatible = yahoo_in_nasdaq and nasdaq_in_yahoo
        rows.append(
            {
                "date": row.date.date().isoformat(),
                "yahoo": {
                    field: scalar(getattr(row, f"{field}_yahoo")) for field in FIELDS
                },
                "nasdaq": {
                    field: scalar(getattr(row, f"{field}_nasdaq")) for field in FIELDS
                },
                "open_difference_bps": float(row.open_difference_bps),
                "yahoo_open_inside_nasdaq_range": bool(yahoo_in_nasdaq),
                "nasdaq_open_inside_yahoo_range": bool(nasdaq_in_yahoo),
                "classification": (
                    "OBSERVATION_ECONOMIQUEMENT_PLAUSIBLE"
                    if mutually_compatible
                    else "CAS_NON_RESOLU"
                ),
                "documented_definition_difference": False,
                "demonstrated_provider_error": False,
                "reason": (
                    "Les deux ouvertures appartiennent aux deux plages quotidiennes; "
                    "la différence reste compatible avec des premiers échanges ou des "
                    "constructions de barre distincts."
                    if mutually_compatible
                    else "Au moins une ouverture est hors de la plage quotidienne de "
                    "l'autre fournisseur; aucune source officielle tierce locale ne "
                    "permet d'attribuer l'écart."
                ),
            }
        )
    return rows


def priority_cases(merged: pd.DataFrame) -> list[dict[str, Any]]:
    selected = merged.loc[merged["date"].isin(pd.to_datetime(PRIORITY_DATES))]
    cases: list[dict[str, Any]] = []
    for row in selected.itertuples(index=False):
        differences = {}
        for field in FIELDS:
            left = getattr(row, f"{field}_yahoo")
            right = getattr(row, f"{field}_nasdaq")
            if pd.isna(left) or pd.isna(right):
                differences[field] = None
            elif field == "volume":
                differences[field] = float(left / right - 1.0)
            else:
                differences[field] = float((left / right - 1.0) * 10_000.0)
        cases.append(
            {
                "date": row.date.date().isoformat(),
                "yahoo": {
                    field: scalar(getattr(row, f"{field}_yahoo")) for field in FIELDS
                },
                "nasdaq": {
                    field: scalar(getattr(row, f"{field}_nasdaq")) for field in FIELDS
                },
                "relative_differences": differences,
                "classification": "CAS_NON_RESOLU",
                "demonstrated_provider_error": False,
            }
        )
    return cases


def candidate_window(
    merged: pd.DataFrame,
    yahoo_spy: pd.DataFrame,
    yahoo_bil: pd.DataFrame,
    spy_splits: list[dict[str, Any]],
    bil_splits: list[dict[str, Any]],
) -> dict[str, Any]:
    spy = yahoo_spy.loc[yahoo_spy["date"] >= CANDIDATE_START].copy()
    bil = yahoo_bil.loc[yahoo_bil["date"] >= CANDIDATE_START].copy()
    common = spy[["date", "open", "close"]].merge(
        bil[["date", "open", "close"]], on="date", suffixes=("_spy", "_bil")
    )
    weeks = common.assign(
        iso_year=common["date"].dt.isocalendar().year.astype(int),
        iso_week=common["date"].dt.isocalendar().week.astype(int),
    ).groupby(["iso_year", "iso_week"], as_index=False)["date"].max()
    alert_dates = {
        item["date"] for item in open_alerts(merged) if item["date"] >= "2018-01-01"
    }
    return {
        "start": common["date"].min().date().isoformat(),
        "end": common["date"].max().date().isoformat(),
        "common_sessions": int(len(common)),
        "spy_sessions": int(len(spy)),
        "bil_sessions": int(len(bil)),
        "identical_spy_bil_date_sets": bool(set(spy["date"]) == set(bil["date"])),
        "missing_open_values": int(common[["open_spy", "open_bil"]].isna().sum().sum()),
        "missing_close_values": int(common[["close_spy", "close_bil"]].isna().sum().sum()),
        "observed_iso_weeks": int(len(weeks)),
        "open_alert_dates": sorted(alert_dates),
        "spy_split_events_since_start": [
            item for item in spy_splits if item["date"] >= "2018-01-01"
        ],
        "bil_split_events_since_start": [
            item for item in bil_splits if item["date"] >= "2018-01-01"
        ],
        "calendar_scope": (
            "Calendrier observé seulement: il prouve les dates présentes dans les "
            "deux fichiers, pas les heures de clôture anticipée, retards d'ouverture "
            "ou interruptions intrajournalières."
        ),
    }


def audit() -> dict[str, Any]:
    merged, yahoo_spy, yahoo_bil, spy_splits, bil_splits = merged_sources()
    alerts = open_alerts(merged)
    counts = pd.Series([item["classification"] for item in alerts]).value_counts()
    return {
        "audit_version": "1.0.0",
        "purpose": "Audit descriptif ciblé; aucune correction, transaction ou performance.",
        "open_alert_threshold_bps": OPEN_ALERT_BPS,
        "open_alert_count": len(alerts),
        "classification_counts": {str(key): int(value) for key, value in counts.items()},
        "open_alerts": alerts,
        "priority_cases": priority_cases(merged),
        "candidate_window": candidate_window(
            merged, yahoo_spy, yahoo_bil, spy_splits, bil_splits
        ),
        "global_conclusion": (
            "Aucune différence de définition ni erreur de fournisseur n'est démontrée. "
            "Les cas incompatibles avec les plages de l'autre source restent non résolus."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Fichier JSON facultatif; stdout sinon")
    args = parser.parse_args()
    payload = json.dumps(audit(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
