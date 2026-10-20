#!/usr/bin/env python3
"""Build the weekly C2 documentary grid without simulating C2.

The output records dates, source presence and documentary dependencies only.
It never constructs a portfolio, an order or a financial result.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from audit_historical_calendars import expected_sessions
from exploratory_buy_hold_spy_bil import _load_distributions, _yahoo_prices


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "RL" / "data_manifest.json"
DEFAULT_OUTPUT = ROOT / "RL" / "docs" / "grille_documentaire_c2_2024_2025.csv"
START = date(2024, 5, 29)
TERMINAL = date(2025, 5, 29)
FIRST_RECURRING_WEEK = date(2024, 6, 3)
NY = ZoneInfo("America/New_York")

SOURCE_IDS = {
    "SPY": "yahoo_spy_chart_ohlcv_20261019",
    "BIL": "yahoo_bil_chart_ohlcv_20261019",
    "market_audit": "yahoo_spy_bil_market_audit_v1_20261019",
    "distributions": "ssga_spdr_distributions_20261019",
    "trading_calendar": "nyse_trading_calendars_2022_2025_20261019",
    "settlement_rule": "sec_settlement_cycle_t1_2023_20261019",
}

# DTC dates on which ordinary settlement was unavailable in the episode.
# Sources: Important Notices 19404-23 (2024) and 20972-24 (2025).
DTC_NO_SETTLEMENT = {
    date(2024, 6, 19),
    date(2024, 7, 4),
    date(2024, 9, 2),
    date(2024, 10, 14),
    date(2024, 11, 11),
    date(2024, 11, 28),
    date(2024, 12, 25),
    date(2025, 1, 1),
    date(2025, 1, 20),
    date(2025, 2, 17),
    date(2025, 5, 26),
}

SETTLEMENT_SOURCES = (
    "SEC-34-96930",
    "DTC-19404-23",
    "DTC-20972-24",
)


@dataclass(frozen=True)
class Candidate:
    cycle: int
    close_reference: date
    decision_date: date
    settlement_date: date


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def manifest_index(root: Path = ROOT) -> dict[str, Mapping[str, Any]]:
    payload = json.loads((root / "RL" / "data_manifest.json").read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload["datasets"]}


def verified_path(
    records: Mapping[str, Mapping[str, Any]], source_id: str, root: Path = ROOT
) -> Path:
    record = records[source_id]
    path = root / str(record["local_file"])
    if not path.is_file():
        raise FileNotFoundError(f"source absente: {source_id}")
    if _sha256(path) != record["sha256"]:
        raise ValueError(f"empreinte incompatible: {source_id}")
    return path


def verify_additional_files(record: Mapping[str, Any], root: Path = ROOT) -> None:
    for item in record.get("additional_files", []):
        path = root / str(item["local_file"])
        if not path.is_file() or _sha256(path) != item["sha256"]:
            raise ValueError(f"fichier additionnel incompatible: {path}")


def next_settlement_day(trade_date: date) -> date:
    candidate = trade_date + timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in DTC_NO_SETTLEMENT:
        candidate += timedelta(days=1)
    return candidate


def weekly_candidates(common_sessions: Iterable[date]) -> tuple[Candidate, ...]:
    sessions = sorted(item for item in set(common_sessions) if item <= TERMINAL)
    by_week: dict[tuple[int, int], list[date]] = {}
    for session in sessions:
        iso = session.isocalendar()
        by_week.setdefault((iso.year, iso.week), []).append(session)

    candidates: list[Candidate] = []
    for week_sessions in by_week.values():
        decision = week_sessions[0]
        week_monday = decision - timedelta(days=decision.weekday())
        if week_monday < FIRST_RECURRING_WEEK or decision > TERMINAL:
            continue
        prior = [item for item in sessions if item < week_monday]
        if not prior:
            raise ValueError(f"close de reference absente avant {decision}")
        candidates.append(
            Candidate(
                cycle=len(candidates) + 1,
                close_reference=prior[-1],
                decision_date=decision,
                settlement_date=next_settlement_day(decision),
            )
        )
    return tuple(candidates)


def _joined(values: Iterable[str]) -> str:
    return "|".join(sorted(set(values)))


def build_rows(root: Path = ROOT) -> tuple[list[dict[str, str]], dict[str, Any]]:
    records = manifest_index(root)
    paths = {
        label: verified_path(records, source_id, root)
        for label, source_id in SOURCE_IDS.items()
    }
    verify_additional_files(records[SOURCE_IDS["trading_calendar"]], root)
    spy_path = paths["SPY"]
    bil_path = paths["BIL"]
    distribution_path = paths["distributions"]
    spy = _yahoo_prices(json.loads(spy_path.read_text(encoding="utf-8")), "SPY")
    bil = _yahoo_prices(json.loads(bil_path.read_text(encoding="utf-8")), "BIL")
    common = set(spy) & set(bil)
    expected = {item for item in expected_sessions() if START <= item <= TERMINAL}
    observed = {item for item in common if START <= item <= TERMINAL}
    if observed != expected:
        raise ValueError("couverture commune incompatible avec le calendrier NYSE")
    audit = json.loads(paths["market_audit"].read_text(encoding="utf-8"))
    alert_dates = {
        date.fromisoformat(value)
        for value in audit["cross_checks"]["spy_yahoo_vs_nasdaq_priority_window"][
            "diagnostic_alerts"
        ]["dates"]
    }
    events = _load_distributions(distribution_path, START, TERMINAL)
    candidates = weekly_candidates(common)
    rows: list[dict[str, str]] = []

    for candidate in candidates:
        relevant = [event for event in events if event.ex_date <= candidate.decision_date]
        entitlement_unknown = [
            event
            for event in relevant
            if candidate.decision_date <= event.payment_date
        ]
        paid_before_decision = [
            event
            for event in relevant
            if event.payment_date < candidate.decision_date
        ]
        dependencies = ["CONDITIONAL_ON_PORTFOLIO_STATE"]
        reasons = [
            "historical Yahoo version at 08:00 ET not archived",
            "distribution announcement timestamps unavailable",
        ]
        if entitlement_unknown:
            dependencies.append("BLOCKED_BY_UNKNOWN_ENTITLEMENT")
            reasons.append("potential entitlement cannot be known point-in-time")
        if paid_before_decision:
            dependencies.append("CONDITIONAL_ON_CASH_AVAILABILITY")
            reasons.append("custodian credit time/account evidence unavailable")

        documentary_status = (
            "NOT_EVALUABLE_DOCUMENTARY"
            if entitlement_unknown
            else "PARTIALLY_DOCUMENTED"
        )
        decision_at = datetime.combine(candidate.decision_date, time(8), NY)
        price_dates_ok = all(
            item in prices
            for prices in (spy, bil)
            for item in (candidate.close_reference, candidate.decision_date)
        )
        rows.append(
            {
                "cycle": str(candidate.cycle),
                "close_reference": candidate.close_reference.isoformat(),
                "decision_at": decision_at.isoformat(),
                "open_candidate": candidate.decision_date.isoformat(),
                "settlement_candidate": candidate.settlement_date.isoformat(),
                "settlement_status": "VERIFIED",
                "close_presence": "PRESENT_BOTH" if price_dates_ok else "MISSING",
                "close_point_in_time_status": "MARKET_OBSERVABLE_PROXY_NOT_ARCHIVED_PIT",
                "open_presence": "PRESENT_BOTH" if price_dates_ok else "MISSING",
                "open_status": "RETROSPECTIVE_HYPOTHETICAL_PROXY",
                "price_anomaly": (
                    "AUDIT_ALERT"
                    if {candidate.close_reference, candidate.decision_date} & alert_dates
                    else "NONE_IDENTIFIED_IN_EPISODE_AUDIT"
                ),
                "active_unknown_entitlements": _joined(
                    event.event_id for event in entitlement_unknown
                ),
                "prior_payments_without_account_evidence": _joined(
                    event.event_id for event in paid_before_decision
                ),
                "announcement_knowledge": "UNVERIFIED_FOR_ALL_RELEVANT_EVENTS",
                "cash_availability": (
                    "CONDITIONAL_UNVERIFIED" if paid_before_decision else "NOT_YET_APPLICABLE"
                ),
                "trading_calendar_status": "AUDITED",
                "documentary_status": documentary_status,
                "decision_statuses": _joined(dependencies),
                "reasons": _joined(reasons),
                "price_source_ids": f"{SOURCE_IDS['SPY']}|{SOURCE_IDS['BIL']}",
                "distribution_source_id": SOURCE_IDS["distributions"],
                "settlement_source_refs": "|".join(SETTLEMENT_SOURCES),
            }
        )

    summary = {
        "candidate_count": len(rows),
        "first_candidate": rows[0]["open_candidate"],
        "last_candidate": rows[-1]["open_candidate"],
        "distribution_count": len(events),
        "settlement_status_counts": {
            status: sum(row["settlement_status"] == status for row in rows)
            for status in ("VERIFIED", "RULE_BASED_UNVERIFIED", "CONFLICTING", "MISSING")
        },
        "documentary_status_counts": {
            status: sum(row["documentary_status"] == status for row in rows)
            for status in (
                "READY_DOCUMENTARY",
                "PARTIALLY_DOCUMENTED",
                "NOT_EVALUABLE_DOCUMENTARY",
            )
        },
        "unknown_entitlement_count": sum(
            bool(row["active_unknown_entitlements"]) for row in rows
        ),
        "decision_status_counts": {
            status: sum(status in row["decision_statuses"].split("|") for row in rows)
            for status in (
                "CONDITIONAL_ON_PORTFOLIO_STATE",
                "BLOCKED_BY_UNKNOWN_ENTITLEMENT",
                "CONDITIONAL_ON_CASH_AVAILABILITY",
                "CONDITIONAL_ON_SETTLEMENT",
                "NO_DOCUMENTARY_BLOCK_IDENTIFIED",
            )
        },
        "fully_ready_count": sum(
            row["documentary_status"] == "READY_DOCUMENTARY" for row in rows
        ),
        "source_hashes": {
            source_id: records[source_id]["sha256"] for source_id in SOURCE_IDS.values()
        },
    }
    return rows, summary


def write_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, summary = build_rows()
    if args.check:
        expected = args.output.read_text(encoding="utf-8")
        temporary = args.output.with_suffix(".check.csv")
        try:
            write_csv(rows, temporary)
            if temporary.read_text(encoding="utf-8") != expected:
                raise SystemExit("grille versionnee non reproductible")
        finally:
            temporary.unlink(missing_ok=True)
    else:
        write_csv(rows, args.output)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
