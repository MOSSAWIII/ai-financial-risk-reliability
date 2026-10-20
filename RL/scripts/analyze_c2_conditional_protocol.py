#!/usr/bin/env python3
"""Analyze C2 methodological conventions without executing historical C2.

Only artificial arithmetic and documentary classifications are produced.  The
strict grid remains the authoritative point-in-time assessment.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from build_c2_documentary_grid import (
    DEFAULT_OUTPUT as STRICT_GRID,
    DTC_NO_SETTLEMENT,
    ROOT,
    SOURCE_IDS,
    manifest_index,
    verified_path,
)
from exploratory_buy_hold_spy_bil import _load_distributions


DEFAULT_OUTPUT = ROOT / "RL" / "docs" / "grille_conditionnelle_c2_2024_2025.csv"
ZERO = Decimal("0")


@dataclass(frozen=True)
class ExDateIdentity:
    pre_detachment_wealth: Decimal
    ex_price: Decimal
    distribution_claim: Decimal
    post_detachment_wealth: Decimal
    incorrect_double_counted_wealth: Decimal


@dataclass(frozen=True)
class ConditionalBudget:
    economic_wealth: Decimal
    decision_budget: Decimal
    excluded_from_budget: Decimal
    financing_cash: Decimal


@dataclass(frozen=True)
class TimedObservation:
    label: str
    value: Decimal
    available_at: datetime


def ex_date_identity(
    *, shares: int, cum_price: Decimal, distribution_per_share: Decimal,
    other_assets: Decimal = ZERO,
) -> ExDateIdentity:
    """Show conservation of wealth under a pure mechanical ex-date drop."""
    if shares < 0 or cum_price <= 0 or distribution_per_share < 0:
        raise ValueError("artificial ex-date inputs must be non-negative")
    claim = Decimal(shares) * distribution_per_share
    ex_price = cum_price - distribution_per_share
    if ex_price <= 0:
        raise ValueError("artificial ex-price must remain positive")
    pre = Decimal(shares) * cum_price + other_assets
    post = Decimal(shares) * ex_price + claim + other_assets
    incorrect = Decimal(shares) * cum_price + claim + other_assets
    return ExDateIdentity(pre, ex_price, claim, post, incorrect)


def conditional_budget(
    *, marked_assets: Decimal, admissible_cash: Decimal,
    known_receivables: Decimal = ZERO,
    unknown_receivables: Decimal = ZERO,
    paid_cash_not_yet_available: Decimal = ZERO,
) -> ConditionalBudget:
    """Separate economic wealth, policy budget and funding resources."""
    values = (
        marked_assets,
        admissible_cash,
        known_receivables,
        unknown_receivables,
        paid_cash_not_yet_available,
    )
    if any(value < 0 for value in values):
        raise ValueError("artificial accounting values must be non-negative")
    excluded = unknown_receivables + paid_cash_not_yet_available
    return ConditionalBudget(
        economic_wealth=sum(values, ZERO),
        decision_budget=marked_assets + admissible_cash + known_receivables,
        excluded_from_budget=excluded,
        financing_cash=admissible_cash,
    )


def available_observations(
    decision_at: datetime, observations: tuple[TimedObservation, ...]
) -> dict[str, Decimal]:
    """Expose only observations available no later than the decision cutoff."""
    if decision_at.tzinfo is None:
        raise ValueError("decision_at must be timezone-aware")
    return {
        item.label: item.value
        for item in observations
        if item.available_at.tzinfo is not None and item.available_at <= decision_at
    }


def validate_ex_date_timeline(
    *, previous_close_at: datetime, entitlement_at: datetime,
    decision_at: datetime, execution_open_at: datetime,
) -> None:
    """Validate the artificial close/right/decision/open event order."""
    moments = (previous_close_at, entitlement_at, decision_at, execution_open_at)
    if any(moment.tzinfo is None for moment in moments):
        raise ValueError("all event times must be timezone-aware")
    if not previous_close_at < entitlement_at <= decision_at < execution_open_at:
        raise ValueError("invalid ex-date event order")


def business_day_after(day: date, delay: int) -> date:
    """Return the start date of the Nth later DTC settlement business day."""
    if delay < 1:
        raise ValueError("delay must be at least one business day")
    current = day
    counted = 0
    while counted < delay:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in DTC_NO_SETTLEMENT:
            counted += 1
    return current


def _read_strict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def build_conditional_rows(root: Path = ROOT) -> tuple[list[dict[str, str]], dict[str, Any]]:
    strict_rows = _read_strict_rows(root / STRICT_GRID.relative_to(ROOT))
    records = manifest_index(root)
    distribution_path = verified_path(records, SOURCE_IDS["distributions"], root)
    events = _load_distributions(
        distribution_path, date(2024, 5, 29), date(2025, 5, 29)
    )
    payment_dates = {event.event_id: event.payment_date for event in events}
    derived: list[dict[str, str]] = []
    for row in strict_rows:
        decision = date.fromisoformat(row["open_candidate"])
        active_unknown = bool(row["active_unknown_entitlements"])
        prior_ids = tuple(
            item
            for item in row["prior_payments_without_account_evidence"].split("|")
            if item
        )
        pending_under_two_days = tuple(
            event_id
            for event_id in prior_ids
            if business_day_after(payment_dates[event_id], 2) > decision
        )
        derived.append(
            {
                "cycle": row["cycle"],
                "decision_at": row["decision_at"],
                "strict_documentary_status": row["documentary_status"],
                "strict_decision_statuses": row["decision_statuses"],
                "option_a_status": (
                    "BLOCKED_EVEN_CONDITIONALLY"
                    if active_unknown
                    else "CONDITIONALLY_DOCUMENTED"
                ),
                "option_a_assumptions": (
                    "strict claim knowledge; Yahoo close/open proxies; cash D+1 convention"
                ),
                "option_b_status": "CONDITIONALLY_DOCUMENTED",
                "option_b_assumptions": (
                    "unknown claim excluded from decision budget; right preserved in economic "
                    "accounting; prior-close anchor; Yahoo close/open proxies; cash D+1"
                ),
                "option_c_status": (
                    "CONDITIONAL_WITH_OPEN_ASSUMPTIONS"
                    if active_unknown
                    else "CONDITIONALLY_DOCUMENTED"
                ),
                "option_c_assumptions": (
                    "realized claim amount treated as decision-known without announcement archive; "
                    "look-ahead risk; Yahoo close/open proxies; cash D+1"
                ),
                "cash_d_plus_1_status": "AVAILABLE_IF_PREVIOUSLY_PAID",
                "cash_d_plus_2_pending_events": "|".join(pending_under_two_days),
                "portfolio_state_dependency": "IF_RELEVANT_ASSET_HELD",
            }
        )

    statuses = (
        "CONDITIONALLY_DOCUMENTED",
        "CONDITIONAL_WITH_OPEN_ASSUMPTIONS",
        "BLOCKED_EVEN_CONDITIONALLY",
    )
    summary = {
        "candidate_count": len(derived),
        "option_counts": {
            option: {
                status: sum(row[f"{option}_status"] == status for row in derived)
                for status in statuses
            }
            for option in ("option_a", "option_b", "option_c")
        },
        "cash_d_plus_2_affected_decisions": sum(
            bool(row["cash_d_plus_2_pending_events"]) for row in derived
        ),
        "strict_grid_preserved": (root / STRICT_GRID.relative_to(ROOT)).is_file(),
    }
    return derived, summary


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
    rows, summary = build_conditional_rows()
    if args.check:
        temporary = args.output.with_suffix(".check.csv")
        try:
            write_csv(rows, temporary)
            if temporary.read_bytes() != args.output.read_bytes():
                raise SystemExit("conditional grid is not reproducible")
        finally:
            temporary.unlink(missing_ok=True)
    else:
        write_csv(rows, args.output)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
