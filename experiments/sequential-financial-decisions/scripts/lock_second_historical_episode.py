#!/usr/bin/env python3
"""Verrouille l'épisode C1-C2 2025-2026 sans calculer de performance."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

from audit_historical_calendars import expected_sessions
from audit_spy_open_divergences import audit as audit_open_divergences
from build_c2_documentary_grid import manifest_index, verified_path
from exploratory_buy_hold_spy_bil import (
    _load_distributions,
    _load_json_decimal,
    _yahoo_prices,
)


EXP_DIR = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = EXP_DIR / "tests" / "fixtures" / "historical_c1_c2_2025_2026_lock_v1.json"
GRID_PATH = EXP_DIR / "docs" / "grille_documentaire_c2_2025_2026.csv"
RESULTS_DIR = EXP_DIR / "results" / "historical_c1_c2_2025_2026"
BLOCK_STATUS_PATH = RESULTS_DIR / "statut_validation_documentaire.json"
SOURCES_PATH = RESULTS_DIR / "sources_configuration.csv"
REFERENCE_COMMIT = "893afda71ed930b5eec8a95058ebcfca962f49b1"
CONFIG_COMMIT = "7372cf3db90dfcd7d8eafb06cfe9151c98bf3490"
START = date(2025, 5, 29)
TERMINAL = date(2026, 5, 29)
DECISION_PRICE_DATE = date(2025, 5, 28)
FIRST_RECURRING_WEEK = date(2025, 6, 2)
NY = ZoneInfo("America/New_York")
SOURCE_IDS = {
    "SPY": "yahoo_spy_chart_ohlcv_20261019",
    "BIL": "yahoo_bil_chart_ohlcv_20261019",
    "market_audit": "yahoo_spy_bil_market_audit_v1_20261019",
    "distributions": "ssga_spdr_distributions_20261019",
    "trading_calendar_2025": "nyse_trading_calendars_2022_2025_20261019",
    "trading_calendar_2026": "nyse_trading_calendar_2026_20261021",
    "settlement_rule": "sec_settlement_cycle_t1_2023_20261019",
    "settlement_calendar": "dtcc_settlement_documentary_bundle_20261020",
}
PRICE_BLOCK_DATE = date(2026, 4, 20)
DTC_NO_SETTLEMENT = {
    date(2025, 6, 19),
    date(2025, 7, 4),
    date(2025, 9, 1),
    date(2025, 10, 13),
    date(2025, 11, 11),
    date(2025, 11, 27),
    date(2025, 12, 25),
    date(2026, 1, 1),
    date(2026, 1, 19),
    date(2026, 2, 16),
    date(2026, 4, 3),
    date(2026, 5, 25),
}
LOCKED_ARTIFACT_HASHES = {
    "RL/results/historical_c1_c2_2024_2025/comparaison_appariee.csv": "e0b86234c6f5eb435c1dd6d426d22b3f0af265d2f8a231e3facecc45775ac311",
    "RL/results/historical_c1_c2_2024_2025/journal_decisions_c2.csv": "41fa6239c2a67ed7725f411d50830a42c785d5543aed395350208668980fcd3f",
    "RL/results/historical_c1_c2_2024_2025/synthese_financiere.csv": "aa3b6b992a6b29f21fc4a3eef47127fb21f82ed47dc1412b29efb103fd8d53bf",
    "RL/results/historical_c1_c2_2024_2025/trajectoire_et_drawdown_s0_d1.svg": "7f3b936ae3f0ee23a97ac9cee4a1fa87963b04bb8927e66aa164dd4d540f4b10",
    "RL/results/historical_c1_c2_2024_2025/trajectoires_quotidiennes.csv": "6407a80efc20ea2a5defb73a95bcffc45d697ae7b8f8b762daceddd382085849",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/chronologie_ecarts_richesse_c1_c2_c3.csv": "e3f41f3047f7d28db3c16ef7c8a1e3206f49de085ca6fcb532d851846fe0486b",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/differences_richesse_c3_c1_c2_c3.csv": "1a4c7fa0135df328d4d9d51bee7ca6d23330fdbc5e1dad2b068bddcaa5d7bb4c",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/journal_reinvestissements_c3.csv": "8db63c790c85e8f745aaba4156384984e49718fc9ef661c2e60502c9998aae01",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/reserves_distributions_c3.csv": "b166a0a285771691b490386a80b9ff62e4855a916c4a067c7228272391fbc18d",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/synthese_comparative_c1_c2_c3.csv": "c73e582dd2aaa8e8f24bfb3fa65285747ecc0f2a7868edaa8bb592e8c441ce29",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/trajectoires_c1_c2_c3_s0_d1.svg": "31fc530f3b17cb93cd5fc80e93fb0a86c184e6b0de89c8189a9f149eb04df596",
    "RL/results/diagnostic_reinvestissement_c1_c2_c3_2024_2025/trajectoires_economiques_c3.csv": "e38e9cf21d8e3dcc301e2648e57085d34602c8dadf612c353cd1a881b1d3dff0",
}


class LockError(RuntimeError):
    """La configuration ne peut pas être verrouillée fidèlement."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def verify_locked_artifacts(root: Path = ROOT) -> None:
    exp_dir = root / "experiments" / "sequential-financial-decisions"
    for relative, expected in LOCKED_ARTIFACT_HASHES.items():
        path = root / relative
        if not path.is_file() and relative.startswith("RL/"):
            path = exp_dir / relative.removeprefix("RL/")
        if not path.is_file() or sha256_file(path) != expected:
            raise LockError(f"livrable historique antérieur modifié: {relative}")


def next_settlement_day(trade_date: date) -> date:
    candidate = trade_date + timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in DTC_NO_SETTLEMENT:
        candidate += timedelta(days=1)
    return candidate


def weekly_candidates(common_sessions: Sequence[date]) -> tuple[dict[str, Any], ...]:
    by_week: dict[tuple[int, int], list[date]] = {}
    for session in common_sessions:
        iso = session.isocalendar()
        by_week.setdefault((iso.year, iso.week), []).append(session)
    candidates: list[dict[str, Any]] = []
    for week_sessions in by_week.values():
        decision = week_sessions[0]
        if decision < FIRST_RECURRING_WEEK:
            continue
        week_monday = decision - timedelta(days=decision.weekday())
        prior = [session for session in common_sessions if session < week_monday]
        if not prior:
            raise LockError(f"close antérieur absent pour {decision.isoformat()}")
        candidates.append(
            {
                "cycle": len(candidates) + 1,
                "close_reference": prior[-1],
                "decision_date": decision,
                "settlement_date": next_settlement_day(decision),
            }
        )
    return tuple(candidates)


def _source_record(
    records: Mapping[str, Mapping[str, Any]], source_id: str, root: Path
) -> dict[str, Any]:
    path = verified_path(records, source_id, root)
    record = records[source_id]
    for additional in record.get("additional_files", []):
        additional_path = root / additional["local_file"]
        if not additional_path.is_file() or sha256_file(additional_path) != additional["sha256"]:
            raise LockError(f"source additionnelle invalide: {additional_path}")
    return {
        "id": source_id,
        "sha256": record["sha256"],
        "local_file": record["local_file"],
        "acquired_at": record.get("acquired_at"),
        "coverage": record.get("coverage"),
        "units": record.get("units"),
        "status": record.get("status"),
        "verified_bytes": path.stat().st_size,
        "additional_files": [
            {
                "local_file": item["local_file"],
                "bytes": item["bytes"],
                "sha256": item["sha256"],
            }
            for item in record.get("additional_files", [])
        ],
    }


def build_lock(root: Path = ROOT) -> tuple[dict[str, Any], list[dict[str, str]]]:
    verify_locked_artifacts(root)
    records = manifest_index(root)
    source_records = {
        label: _source_record(records, source_id, root)
        for label, source_id in SOURCE_IDS.items()
    }
    spy = _yahoo_prices(
        _load_json_decimal(verified_path(records, SOURCE_IDS["SPY"], root)), "SPY"
    )
    bil = _yahoo_prices(
        _load_json_decimal(verified_path(records, SOURCE_IDS["BIL"], root)), "BIL"
    )
    required_price_dates = {DECISION_PRICE_DATE, *(
        current
        for current in set(spy) & set(bil)
        if START <= current <= TERMINAL
    )}
    if any(current not in spy or current not in bil for current in required_price_dates):
        raise LockError("prix SPY/BIL requis absent")
    common_sessions = tuple(sorted(current for current in set(spy) & set(bil) if START <= current <= TERMINAL))
    expected = {
        current for current in expected_sessions() if START <= current <= TERMINAL
    }
    if set(common_sessions) != expected:
        raise LockError("séances Yahoo incompatibles avec le calendrier NYSE")
    candidates = weekly_candidates(common_sessions)
    if PRICE_BLOCK_DATE not in {item["decision_date"] for item in candidates}:
        raise LockError("le cas SPY contesté n'est pas représenté dans le calendrier")
    open_audit = audit_open_divergences()
    unresolved = {
        date.fromisoformat(item["date"])
        for item in open_audit["open_alerts"]
        if item["classification"] == "CAS_NON_RESOLU"
    }
    if PRICE_BLOCK_DATE not in unresolved:
        raise LockError("le cas SPY du 20 avril 2026 n'est plus classé non résolu")

    distributions = _load_distributions(
        verified_path(records, SOURCE_IDS["distributions"], root), START, TERMINAL
    )
    rows: list[dict[str, str]] = []
    for item in candidates:
        decision = item["decision_date"]
        blocked = decision == PRICE_BLOCK_DATE
        rows.append(
            {
                "cycle": str(item["cycle"]),
                "close_reference": item["close_reference"].isoformat(),
                "decision_at": datetime.combine(decision, time(8), NY).isoformat(),
                "open_candidate": decision.isoformat(),
                "settlement_candidate": item["settlement_date"].isoformat(),
                "close_presence": "PRESENT_BOTH",
                "open_presence": "PRESENT_BOTH",
                "open_validation_status": (
                    "PRICE_MISSING_OR_DISPUTED" if blocked else "MARKET_OBSERVABLE_PROXY"
                ),
                "documentary_status": (
                    "DOCUMENTARY_BLOCK" if blocked else "CONDITIONALLY_DOCUMENTED"
                ),
                "affected_cells": "ALL_EIGHT_C2_CELLS" if blocked else "NONE",
                "reason": (
                    "Yahoo/Nasdaq SPY OHLC incompatibles; source primaire TAQ non acquise"
                    if blocked
                    else "sources et calendriers présents sous conventions verrouillées"
                ),
                "price_sources": f'{SOURCE_IDS["SPY"]}|{SOURCE_IDS["BIL"]}',
                "calendar_sources": (
                    f'{SOURCE_IDS["trading_calendar_2025"]}|'
                    f'{SOURCE_IDS["trading_calendar_2026"]}|'
                    f'{SOURCE_IDS["settlement_calendar"]}'
                ),
            }
        )

    source_manifest = canonical_json(source_records)
    provisional: dict[str, Any] = {
        "schema_version": "historical_c1_c2_episode_lock/v1",
        "episode_id": "spy-bil-c1-c2-2025-05-29-to-2026-05-29",
        "reference_commit": REFERENCE_COMMIT,
        "scientific_status": "EXPLORATORY_TEMPORAL_REPLICATION_POST_HOC",
        "locked_before_performance": True,
        "performance_computed": False,
        "dates": {
            "decision_price_date": DECISION_PRICE_DATE.isoformat(),
            "decision_at": datetime.combine(START, time(8), NY).isoformat(),
            "execution_date": START.isoformat(),
            "initial_settlement_date": next_settlement_day(START).isoformat(),
            "first_recurring_week": FIRST_RECURRING_WEEK.isoformat(),
            "terminal_date": TERMINAL.isoformat(),
            "terminal_rule": "COMMON_CLOSE_NO_FICTITIOUS_LIQUIDATION",
        },
        "account": {
            "currency": "USD",
            "initial_cash": "100000",
            "whole_shares": True,
            "funding": "H_FIN_NET",
            "borrowing": False,
            "shorting": False,
            "batch_resizing_after_rejection": False,
        },
        "policies": {
            "C1": "INITIAL_50_50_THEN_HOLD_DISTRIBUTIONS_IN_CASH",
            "C2": "INITIAL_50_50_THEN_WEEKLY_50_50_OF_E_B_DECISION_BUDGET",
        },
        "decision_protocol": {
            "mode": "EXPLORATORY_CONDITIONAL",
            "decision_time": "08:00 America/New_York",
            "frequency": "FIRST_NYSE_SESSION_OF_EACH_WEEK",
            "decision_price": "LAST_ADMISSIBLE_CLOSE",
            "execution_price": "SAME_DAY_YAHOO_OPEN_READ_AFTER_SEALING",
            "cash_conventions": ["D_PLUS_1", "D_PLUS_2"],
            "unknown_distribution_receivables_excluded": True,
        },
        "cost_scenarios_bps": {"S0": "0", "S1": "1", "S2": "5", "S3": "10"},
        "coverage": {
            "common_sessions": len(common_sessions),
            "weekly_decisions": len(candidates),
            "distribution_events": len(distributions),
            "spy_distributions": sum(event.symbol == "SPY" for event in distributions),
            "bil_distributions": sum(event.symbol == "BIL" for event in distributions),
        },
        "distribution_events": [
            {
                "event_id": event.event_id,
                "symbol": event.symbol,
                "ex_date": event.ex_date.isoformat(),
                "payment_date": event.payment_date.isoformat(),
                "amount_per_share_usd": str(event.amount_per_share),
            }
            for event in distributions
        ],
        "dtc_no_settlement_dates": sorted(item.isoformat() for item in DTC_NO_SETTLEMENT),
        "documentary_gate": {
            "status": "DOCUMENTARY_BLOCK",
            "blocking_cycle": next(
                item["cycle"] for item in candidates if item["decision_date"] == PRICE_BLOCK_DATE
            ),
            "blocking_date": PRICE_BLOCK_DATE.isoformat(),
            "affected_scope": "ALL_EIGHT_C2_CELLS",
            "reason": "SPY Yahoo/Nasdaq OHLC incompatibles et aucun TAQ primaire acquis",
            "required_resolution": "archive primaire NYSE Daily TAQ ou source équivalente préautorisée",
        },
        "sources": source_records,
        "source_fingerprint": hashlib.sha256(source_manifest.encode("utf-8")).hexdigest(),
    }
    config_hash = hashlib.sha256(canonical_json(provisional).encode("utf-8")).hexdigest()
    return {**provisional, "config_sha256": config_hash}, rows


def _render_config(config: Mapping[str, Any]) -> str:
    return json.dumps(config, ensure_ascii=False, indent=2) + "\n"


def _render_grid(rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        raise LockError("grille vide")
    from io import StringIO

    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def write_lock(config: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(_render_config(config), encoding="utf-8", newline="\n")
    GRID_PATH.write_text(_render_grid(rows), encoding="utf-8", newline="\n")


def check_lock(config: Mapping[str, Any], rows: Sequence[Mapping[str, Any]]) -> None:
    if CONFIG_PATH.read_text(encoding="utf-8") != _render_config(config):
        raise LockError("configuration verrouillée non reproductible")
    if GRID_PATH.read_text(encoding="utf-8") != _render_grid(rows):
        raise LockError("grille verrouillée non reproductible")


def _block_status(config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "episode_id": config["episode_id"],
        "validation_status": "DOCUMENTARY_BLOCK",
        "performance_computed": False,
        "complete_cells": 0,
        "affected_cells": [
            f"S{scenario}-{cash}"
            for cash in ("D1", "D2")
            for scenario in range(4)
        ],
        "blocking_cycle": config["documentary_gate"]["blocking_cycle"],
        "blocking_date": config["documentary_gate"]["blocking_date"],
        "reason": config["documentary_gate"]["reason"],
        "required_resolution": config["documentary_gate"]["required_resolution"],
        "configuration_commit": CONFIG_COMMIT,
        "configuration_path": "RL/tests/fixtures/historical_c1_c2_2025_2026_lock_v1.json",
        "configuration_sha256": config["config_sha256"],
        "configuration_file_sha256": sha256_file(CONFIG_PATH),
        "documentary_grid_path": "RL/docs/grille_documentaire_c2_2025_2026.csv",
        "documentary_grid_sha256": sha256_file(GRID_PATH),
        "locked_artifacts_verified": LOCKED_ARTIFACT_HASHES,
    }


def _render_sources(config: Mapping[str, Any]) -> str:
    rows = [
        {
            "usage": usage,
            "source_id": source["id"],
            "sha256": source["sha256"],
            "acquired_at": source["acquired_at"],
            "coverage": source["coverage"],
            "units": source["units"],
            "status": source["status"],
        }
        for usage, source in config["sources"].items()
    ]
    return _render_grid(rows)


def write_block_artifacts(config: Mapping[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    BLOCK_STATUS_PATH.write_text(
        json.dumps(_block_status(config), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    SOURCES_PATH.write_text(_render_sources(config), encoding="utf-8", newline="\n")


def check_block_artifacts(config: Mapping[str, Any]) -> None:
    expected_status = json.dumps(_block_status(config), ensure_ascii=False, indent=2) + "\n"
    if BLOCK_STATUS_PATH.read_text(encoding="utf-8") != expected_status:
        raise LockError("statut documentaire publié non reproductible")
    if SOURCES_PATH.read_text(encoding="utf-8") != _render_sources(config):
        raise LockError("inventaire des sources publié non reproductible")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--publish-block", action="store_true")
    parser.add_argument("--check-block", action="store_true")
    args = parser.parse_args()
    try:
        config, rows = build_lock(ROOT)
        if args.check:
            check_lock(config, rows)
        elif not args.publish_block and not args.check_block:
            write_lock(config, rows)
        if args.publish_block:
            check_lock(config, rows)
            write_block_artifacts(config)
        if args.check_block:
            check_lock(config, rows)
            check_block_artifacts(config)
    except (LockError, KeyError, ValueError) as exc:
        print(f"LOCK_FAILED: {exc}", file=sys.stderr)
        return 1
    print(f"LOCKED_CONFIG_SHA256={config['config_sha256']}")
    print(f"SESSIONS={config['coverage']['common_sessions']}")
    print(f"WEEKLY_DECISIONS={config['coverage']['weekly_decisions']}")
    print(f"DOCUMENTARY_GATE={config['documentary_gate']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
