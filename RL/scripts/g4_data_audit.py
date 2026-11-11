#!/usr/bin/env python3
"""Audit structurel G4.1 des sources SPY/IEF/GLD/BIL, sans rendement.

Le rapport contrôle les OHLCV quotidiens, le calendrier empirique commun, les
événements fournisseur et la structure minimale des deux fichiers émetteurs.
Il ne construit ni portefeuille, ni récompense, ni métrique de performance.
"""

from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
READINESS_PATH = ROOT / "RL" / "results" / "g4_problem_redesign" / "data_readiness_report.json"
DEFAULT_OUTPUT = ROOT / "RL" / "results" / "g4_problem_redesign" / "data_audit_report.json"
YAHOO_IDS = {
    "SPY": "yahoo_spy_chart_ohlcv_20261019",
    "IEF": "yahoo_ief_chart_ohlcv_g4",
    "GLD": "yahoo_gld_chart_ohlcv_g4",
    "BIL": "yahoo_bil_chart_ohlcv_20261019",
}


class G4DataAuditError(RuntimeError):
    """L'audit G4.1 ne peut pas produire un verdict valide."""


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G4DataAuditError(f"JSON invalide: {path}") from exc
    if not isinstance(value, dict):
        raise G4DataAuditError(f"objet JSON requis: {path}")
    return value


def _manifest_index(root: Path) -> dict[str, dict[str, Any]]:
    manifest = _load_json(root / MANIFEST_PATH.relative_to(ROOT))
    return {item["id"]: item for item in manifest["datasets"]}


def _local_path(root: Path, index: dict[str, dict[str, Any]], dataset_id: str) -> Path:
    return root / index[dataset_id]["local_file"]


def _audit_yahoo(path: Path, expected_symbol: str) -> tuple[dict[str, Any], set[str]]:
    payload = _load_json(path)
    chart = payload.get("chart") or {}
    results = chart.get("result") or []
    if chart.get("error") is not None or len(results) != 1:
        raise G4DataAuditError(f"réponse Yahoo inutilisable: {path}")
    result = results[0]
    meta = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    quote_sets = ((result.get("indicators") or {}).get("quote") or [])
    adjusted_sets = ((result.get("indicators") or {}).get("adjclose") or [])
    if len(quote_sets) != 1 or len(adjusted_sets) != 1:
        raise G4DataAuditError(f"blocs OHLCV/Adj Close invalides: {path}")
    quote = quote_sets[0]
    adjusted = adjusted_sets[0].get("adjclose") or []
    fields = {name: quote.get(name) or [] for name in ("open", "high", "low", "close", "volume")}
    lengths = {"timestamp": len(timestamps), "adjclose": len(adjusted), **{name: len(values) for name, values in fields.items()}}
    aligned = len(set(lengths.values())) == 1 and bool(timestamps)
    timezone = ZoneInfo(meta.get("exchangeTimezoneName", "America/New_York"))
    dates = [datetime.fromtimestamp(value, timezone).date().isoformat() for value in timestamps]
    duplicate_dates = len(dates) - len(set(dates))
    weekend_dates = sum(datetime.fromisoformat(value).weekday() >= 5 for value in dates)
    missing_rows = 0
    invalid_ohlc_rows = 0
    nonpositive_price_values = 0
    negative_volume_rows = 0
    if aligned:
        for position in range(len(dates)):
            values = {name: fields[name][position] for name in fields}
            row = [values[name] for name in fields] + [adjusted[position]]
            if any(value is None for value in row):
                missing_rows += 1
                continue
            low, high = values["low"], values["high"]
            if not (low <= values["open"] <= high and low <= values["close"] <= high and low <= high):
                invalid_ohlc_rows += 1
            nonpositive_price_values += sum(values[name] <= 0 for name in ("open", "high", "low", "close"))
            negative_volume_rows += values["volume"] < 0
    events = result.get("events") or {}
    dividends = events.get("dividends") or {}
    splits = events.get("splits") or {}
    assertions = {
        "symbol_matches": meta.get("symbol") == expected_symbol,
        "currency_usd": meta.get("currency") == "USD",
        "daily_granularity": meta.get("dataGranularity") == "1d",
        "arrays_aligned": aligned,
        "ascending_unique_dates": dates == sorted(dates) and duplicate_dates == 0,
        "no_weekend_dates": weekend_dates == 0,
        "no_missing_rows": missing_rows == 0,
        "valid_ohlc": invalid_ohlc_rows == 0,
        "positive_prices": nonpositive_price_values == 0,
        "nonnegative_volume": negative_volume_rows == 0,
    }
    return (
        {
            "symbol": meta.get("symbol"),
            "exchange_name": meta.get("exchangeName"),
            "full_exchange_name": meta.get("fullExchangeName"),
            "currency": meta.get("currency"),
            "rows": len(dates),
            "start": min(dates),
            "end": max(dates),
            "field_lengths": lengths,
            "duplicate_dates": duplicate_dates,
            "weekend_dates": weekend_dates,
            "missing_rows": missing_rows,
            "invalid_ohlc_rows": invalid_ohlc_rows,
            "nonpositive_price_values": nonpositive_price_values,
            "negative_volume_rows": negative_volume_rows,
            "dividend_event_count": len(dividends),
            "split_event_count": len(splits),
            "assertions": assertions,
        },
        set(dates),
    )


def _audit_ief(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    required = ["Holdings", "Historical", "Performance", "Distributions", "Record Date", "Ex-Date", "Payable Date", "Total Distribution"]
    present = {value: value in text for value in required}
    return {
        "format": "SpreadsheetML XML",
        "bytes": path.stat().st_size,
        "required_labels": present,
        "assertions": {"all_required_labels_present": all(present.values()), "substantial_document": path.stat().st_size > 1_000_000},
    }


def _audit_gld(path: Path) -> dict[str, Any]:
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as archive:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        sheets = [item.attrib["name"] for item in workbook.findall(".//m:sheets/m:sheet", namespace)]
        shared = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(node.text or "" for node in item.findall(".//m:t", namespace)) for item in shared.findall("m:si", namespace)]
        history = ElementTree.fromstring(archive.read("xl/worksheets/sheet2.xml"))
        row_count = len(history.findall(".//m:sheetData/m:row", namespace))
    required = ["Date", "Ounces of Gold per Share", "NAV/Share at 10:30am NYT", "Daily Share Volume", "Total Net Asset Value in the Trust"]
    present = {value: value in strings for value in required}
    return {
        "format": "XLSX",
        "bytes": path.stat().st_size,
        "sheets": sheets,
        "historical_sheet_rows_including_headers": row_count,
        "required_labels": present,
        "assertions": {
            "historical_sheet_present": "US GLD Historical Archive" in sheets,
            "all_required_labels_present": all(present.values()),
            "substantial_history": row_count > 5_000,
        },
    }


def build_report(root: Path = ROOT) -> dict[str, Any]:
    readiness = _load_json(root / READINESS_PATH.relative_to(ROOT))
    if readiness.get("verdict") != "READY_FOR_G4_STATISTICAL_AUDIT":
        raise G4DataAuditError("le verrou documentaire G4.1 n'est pas levé")
    index = _manifest_index(root)
    market: dict[str, Any] = {}
    date_sets: dict[str, set[str]] = {}
    for symbol, dataset_id in YAHOO_IDS.items():
        market[symbol], date_sets[symbol] = _audit_yahoo(_local_path(root, index, dataset_id), symbol)
    common = set.intersection(*date_sets.values())
    union = set.union(*date_sets.values())
    calendar = {
        "common_rows": len(common),
        "common_start": min(common),
        "common_end": max(common),
        "union_rows": len(union),
        "asset_only_vs_common": {symbol: len(dates - common) for symbol, dates in date_sets.items()},
        "asset_missing_vs_union": {symbol: len(union - dates) for symbol, dates in date_sets.items()},
        "assertions": {"common_window_nonempty": bool(common), "candidate_common_start_observed": min(common) == "2007-05-30", "common_end_aligned": max(common) == "2026-10-16"},
    }
    issuer = {
        "IEF": _audit_ief(_local_path(root, index, "ishares_ief_distribution_history_g4")),
        "GLD": _audit_gld(_local_path(root, index, "spdr_gld_historical_archive_g4")),
    }
    assertion_groups = [item["assertions"] for item in market.values()] + [calendar["assertions"]] + [item["assertions"] for item in issuer.values()]
    failed = [name for group in assertion_groups for name, passed in group.items() if not passed]
    return {
        "schema_version": "g4-data-audit-1.0",
        "verdict": "G4_1_DATA_AUDIT_PASSED" if not failed else "G4_1_DATA_AUDIT_FAILED",
        "scope": "STRUCTURE_CALENDAR_EVENTS_AND_ISSUER_FILES_ONLY",
        "performance_computation_performed": False,
        "training_authorized": False,
        "market_sources": market,
        "common_calendar": calendar,
        "issuer_sources": issuer,
        "failed_assertions": failed,
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report(ROOT)
    rendered = render_report(report)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise G4DataAuditError("rapport d'audit G4.1 non reproductible")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "G4_1_DATA_AUDIT_PASSED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
