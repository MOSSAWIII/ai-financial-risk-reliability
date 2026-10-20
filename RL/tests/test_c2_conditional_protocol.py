from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import analyze_c2_conditional_protocol as protocol  # noqa: E402
from synthetic_decision_adapter import DecisionSnapshot  # noqa: E402


D = Decimal
ET = ZoneInfo("America/New_York")


def at(day: date, hour: int, minute: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=ET)


def test_ex_date_identity_conserves_wealth_without_double_counting() -> None:
    result = protocol.ex_date_identity(
        shares=100, cum_price=D("100"), distribution_per_share=D("2")
    )
    assert result.ex_price == D("98")
    assert result.distribution_claim == D("200")
    assert result.pre_detachment_wealth == result.post_detachment_wealth == D("10000")
    assert result.incorrect_double_counted_wealth == D("10200")


def test_conditional_budget_separates_wealth_budget_and_funding() -> None:
    result = protocol.conditional_budget(
        marked_assets=D("9800"),
        admissible_cash=D("50"),
        known_receivables=D("25"),
        unknown_receivables=D("200"),
        paid_cash_not_yet_available=D("75"),
    )
    assert result.economic_wealth == D("10150")
    assert result.decision_budget == D("9875")
    assert result.excluded_from_budget == D("275")
    assert result.financing_cash == D("50")


def test_unknown_claim_is_not_revealed_to_policy_budget() -> None:
    small = protocol.conditional_budget(
        marked_assets=D("9800"), admissible_cash=D("0"), unknown_receivables=D("1")
    )
    large = protocol.conditional_budget(
        marked_assets=D("9800"), admissible_cash=D("0"), unknown_receivables=D("999")
    )
    assert small.decision_budget == large.decision_budget == D("9800")
    assert small.economic_wealth != large.economic_wealth


def test_paid_cash_remains_outside_funding_until_available() -> None:
    pending = protocol.conditional_budget(
        marked_assets=D("10000"),
        admissible_cash=D("0"),
        paid_cash_not_yet_available=D("200"),
    )
    available = protocol.conditional_budget(
        marked_assets=D("10000"), admissible_cash=D("200")
    )
    assert pending.economic_wealth == available.economic_wealth == D("10200")
    assert pending.financing_cash == 0
    assert available.financing_cash == D("200")


def test_one_and_two_business_day_cash_delays_are_distinct() -> None:
    friday = date(2024, 7, 5)
    assert protocol.business_day_after(friday, 1) == date(2024, 7, 8)
    assert protocol.business_day_after(friday, 2) == date(2024, 7, 9)
    assert protocol.business_day_after(date(2024, 6, 6), 2) == date(2024, 6, 10)


def test_information_cutoff_excludes_future_open() -> None:
    day = date(2025, 1, 6)
    observations = (
        protocol.TimedObservation("prior_close", D("100"), at(date(2025, 1, 3), 16)),
        protocol.TimedObservation("future_open", D("98"), at(day, 9, 30)),
    )
    visible = protocol.available_observations(at(day, 8), observations)
    assert visible == {"prior_close": D("100")}


def test_ex_date_event_order_is_enforced() -> None:
    day = date(2025, 1, 6)
    protocol.validate_ex_date_timeline(
        previous_close_at=at(date(2025, 1, 3), 16),
        entitlement_at=at(day, 0),
        decision_at=at(day, 8),
        execution_open_at=at(day, 9, 30),
    )
    with pytest.raises(ValueError, match="event order"):
        protocol.validate_ex_date_timeline(
            previous_close_at=at(date(2025, 1, 3), 16),
            entitlement_at=at(day, 0),
            decision_at=at(day, 10),
            execution_open_at=at(day, 9, 30),
        )


def test_decision_snapshot_protection_remains_frozen() -> None:
    assert DecisionSnapshot.__dataclass_params__.frozen is True


def test_conditional_grid_preserves_strict_results_and_counts_options() -> None:
    rows, summary = protocol.build_conditional_rows(ROOT)
    assert len(rows) == 52
    assert summary["option_counts"]["option_a"] == {
        "CONDITIONALLY_DOCUMENTED": 20,
        "CONDITIONAL_WITH_OPEN_ASSUMPTIONS": 0,
        "BLOCKED_EVEN_CONDITIONALLY": 32,
    }
    assert summary["option_counts"]["option_b"] == {
        "CONDITIONALLY_DOCUMENTED": 52,
        "CONDITIONAL_WITH_OPEN_ASSUMPTIONS": 0,
        "BLOCKED_EVEN_CONDITIONALLY": 0,
    }
    assert summary["option_counts"]["option_c"] == {
        "CONDITIONALLY_DOCUMENTED": 20,
        "CONDITIONAL_WITH_OPEN_ASSUMPTIONS": 32,
        "BLOCKED_EVEN_CONDITIONALLY": 0,
    }
    assert summary["cash_d_plus_2_affected_decisions"] == 5
    assert rows[0]["strict_documentary_status"] == "NOT_EVALUABLE_DOCUMENTARY"
