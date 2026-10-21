from __future__ import annotations

import sys
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from synthetic_decision_adapter import (  # noqa: E402
    AdapterError,
    DatedPrice,
    ExecutionStatus,
    PriceStatus,
    SnapshotStatus,
    SyntheticDecisionAdapter,
    cost_scenario_fees,
)
from synthetic_portfolio_ledger import (  # noqa: E402
    SyntheticPortfolioLedger,
    SyntheticSettlementCalendar,
    SyntheticTradingCalendar,
)


D = Decimal
ET = ZoneInfo("America/New_York")
SESSIONS = (
    date(2025, 1, 3),
    date(2025, 1, 6),
    date(2025, 1, 10),
    date(2025, 1, 13),
    date(2025, 1, 17),
    date(2025, 1, 21),
    date(2025, 1, 24),
    date(2025, 1, 27),
    date(2025, 1, 31),
    date(2025, 2, 3),
)
PROVENANCE = {
    "SPY_close": "ARTIFICIAL_CLOSE_SPY",
    "BIL_close": "ARTIFICIAL_CLOSE_BIL",
    "trading_calendar": "ARTIFICIAL_TRADING_CALENDAR",
    "settlement_calendar": "ARTIFICIAL_SETTLEMENT_CALENDAR",
    "economic_positions": "SYNTHETIC_STRICT_LEDGER",
    "settled_positions": "SYNTHETIC_STRICT_LEDGER",
    "settled_cash": "SYNTHETIC_STRICT_LEDGER",
    "pending_settlements": "SYNTHETIC_STRICT_LEDGER",
    "distribution_claims": "ARTIFICIAL_INFORMATION_TIMELINE",
}


def artificial_ledger() -> SyntheticPortfolioLedger:
    start = date(2025, 1, 2)
    settlement_dates = tuple(start + timedelta(days=index) for index in range(35))
    settlement_dates = tuple(item for item in settlement_dates if item.weekday() < 5)
    return SyntheticPortfolioLedger(
        D("100000"),
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(SESSIONS),
        settlement_calendar=SyntheticSettlementCalendar(settlement_dates),
    )


def at(day: date, hour: int = 8) -> datetime:
    return datetime(day.year, day.month, day.day, hour, tzinfo=ET)


def build_snapshot(
    adapter: SyntheticDecisionAdapter,
    decision_day: date,
    spy_close: str,
    bil_close: str,
    *,
    available_at: datetime | None = None,
):
    previous = max(item for item in SESSIONS if item < decision_day)
    availability = available_at or at(previous, 16)
    return adapter.build_decision_snapshot(
        decision_at=at(decision_day),
        decision_closes={
            "SPY": DatedPrice(previous, D(spy_close), PriceStatus.AVAILABLE),
            "BIL": DatedPrice(previous, D(bil_close), PriceStatus.AVAILABLE),
        },
        close_available_at={"SPY": availability, "BIL": availability},
        provenance=PROVENANCE,
    )


def execute_cycle(
    adapter: SyntheticDecisionAdapter,
    decision_day: date,
    spy_close: str,
    bil_close: str,
    spy_open: str,
    bil_open: str,
    *,
    basis_points: str = "0",
):
    snapshot = build_snapshot(adapter, decision_day, spy_close, bil_close)
    intent = adapter.prepare_intent_from_snapshot(
        snapshot, target_weight_spy=D("0.5")
    )
    opens = {"SPY": D(spy_open), "BIL": D(bil_open)}
    fees = cost_scenario_fees(intent, opens, D(basis_points))
    outcome = adapter.process_intent(
        intent,
        execution_date=decision_day,
        execution_opens={
            symbol: DatedPrice(decision_day, value, PriceStatus.AVAILABLE)
            for symbol, value in opens.items()
        },
        fees=fees,
    )
    return snapshot, intent, outcome


def initially_funded(
    *, decision_close: str = "100", basis_points: str = "0"
) -> tuple[SyntheticPortfolioLedger, SyntheticDecisionAdapter]:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, _, outcome = execute_cycle(
        adapter,
        date(2025, 1, 6),
        decision_close,
        decision_close,
        "100",
        "100",
        basis_points=basis_points,
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    ledger.settle_through(date(2025, 1, 7))
    return ledger, adapter


def test_successive_c2_decisions_inherit_state_and_cover_both_drifts_and_hold() -> None:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)

    _, first, initial = execute_cycle(
        adapter, date(2025, 1, 6), "100", "100", "100", "100"
    )
    assert initial.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert first.target_quantities == {"SPY": 500, "BIL": 500}
    ledger.settle_through(date(2025, 1, 7))

    _, second, drift_up = execute_cycle(
        adapter, date(2025, 1, 13), "120", "100", "120", "100"
    )
    assert second.inherited_positions == {"SPY": 500, "BIL": 500}
    assert second.target_quantities == {"SPY": 458, "BIL": 550}
    assert {(item.symbol, item.quantity) for item in second.orders} == {
        ("SPY", -42),
        ("BIL", 50),
    }
    assert drift_up.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    ledger.settle_through(date(2025, 1, 14))

    _, third, drift_down = execute_cycle(
        adapter, date(2025, 1, 21), "80", "100", "80", "100"
    )
    assert third.inherited_positions == {"SPY": 458, "BIL": 550}
    assert third.target_quantities == {"SPY": 573, "BIL": 458}
    assert {(item.symbol, item.quantity) for item in third.orders} == {
        ("SPY", 115),
        ("BIL", -92),
    }
    assert drift_down.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    ledger.settle_through(date(2025, 1, 22))

    snapshot, hold_intent, hold = execute_cycle(
        adapter, date(2025, 1, 27), "458", "573", "458", "573"
    )
    assert snapshot.settled_cash == D("40")
    assert hold_intent.inherited_positions == {"SPY": 573, "BIL": 458}
    assert hold_intent.orders == ()
    assert hold.status is ExecutionStatus.VOLUNTARY_HOLD
    assert ledger.fees_recognized == 0


def test_snapshot_separates_economic_settled_and_funding_states() -> None:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    execute_cycle(adapter, date(2025, 1, 6), "100", "100", "100", "100")

    snapshot = build_snapshot(adapter, date(2025, 1, 10), "100", "100")
    assert snapshot.economic_positions == {"SPY": 500, "BIL": 500}
    assert snapshot.settled_positions == {"SPY": 0, "BIL": 0}
    assert snapshot.status is SnapshotStatus.NOT_EVALUABLE
    assert "règlement échu" in snapshot.reason
    assert snapshot.funding_resources == 0


def test_future_close_availability_is_not_admissible() -> None:
    adapter = SyntheticDecisionAdapter(artificial_ledger())
    snapshot = build_snapshot(
        adapter,
        date(2025, 1, 6),
        "100",
        "100",
        available_at=at(date(2025, 1, 6), 9),
    )
    assert snapshot.status is SnapshotStatus.NOT_EVALUABLE
    assert snapshot.admissible_wealth is None
    assert "disponibilité point-in-time" in snapshot.reason


def test_announced_distribution_is_known_wealth_but_not_funding_cash() -> None:
    ledger, adapter = initially_funded()
    announcement = ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2025, 1, 8),
        knowledge_at=at(date(2025, 1, 8), 10),
        ex_date=date(2025, 1, 9),
        payment_date=date(2025, 1, 15),
        amount_per_share=D("2"),
    )
    ledger.accrue_announced_distribution(announcement, event_date=date(2025, 1, 9))

    snapshot = build_snapshot(adapter, date(2025, 1, 13), "100", "100")
    audit = adapter.build_economic_audit_state(snapshot)
    assert snapshot.status is SnapshotStatus.READY
    assert snapshot.known_distribution_receivables == D("1000")
    assert ledger.distribution_receivables == D("1000")
    assert audit.accounting.distribution_receivables == D("1000")
    assert audit.economic_wealth == D("101000")
    assert snapshot.admissible_wealth == D("101000")
    assert snapshot.funding_resources == 0


def test_realized_unannounced_distribution_is_hidden_and_blocks_exact_target() -> None:
    ledger, adapter = initially_funded()
    ledger.accrue_realized_distribution(
        "SPY",
        event_id="ART-UNKNOWN",
        ex_date=date(2025, 1, 9),
        payment_date=date(2025, 1, 15),
        amount_per_share=D("2"),
    )

    snapshot = build_snapshot(adapter, date(2025, 1, 13), "100", "100")
    audit = adapter.build_economic_audit_state(snapshot)
    assert ledger.distribution_receivables == D("1000")
    assert audit.accounting.distribution_receivables == D("1000")
    assert audit.economic_wealth == D("101000")
    assert snapshot.known_distribution_receivables == 0
    assert snapshot.unknown_distribution_claim_ids == (1,)
    assert snapshot.status is SnapshotStatus.NOT_EVALUABLE
    assert snapshot.admissible_wealth is None
    with pytest.raises(AdapterError, match="NOT_EVALUABLE"):
        adapter.prepare_intent_from_snapshot(snapshot, target_weight_spy=D("0.5"))
    with pytest.raises(AdapterError, match="ex post"):
        adapter.prepare_intent(
            decision_date=date(2025, 1, 10),
            known_market_wealth=D("101000"),
            inherited_positions={"SPY": 500, "BIL": 500},
            decision_closes={
                "SPY": DatedPrice(date(2025, 1, 10), D("100")),
                "BIL": DatedPrice(date(2025, 1, 10), D("100")),
            },
            target_weight_spy=D("0.5"),
        )


def test_paid_realized_distribution_can_fund_later_decision_with_proof() -> None:
    ledger, adapter = initially_funded()
    ledger.accrue_realized_distribution(
        "SPY",
        event_id="ART-PAID",
        ex_date=date(2025, 1, 9),
        payment_date=date(2025, 1, 11),
        amount_per_share=D("2"),
    )
    ledger.pay_distributions_through(
        date(2025, 1, 11), cash_available_at=at(date(2025, 1, 11), 12)
    )

    snapshot = build_snapshot(adapter, date(2025, 1, 13), "120", "100")
    assert date(2025, 1, 11) not in ledger.trading_calendar.sessions
    assert snapshot.status is SnapshotStatus.READY
    assert snapshot.settled_cash == D("1000")
    assert snapshot.funding_resources == D("1000")
    intent = adapter.prepare_intent_from_snapshot(
        snapshot, target_weight_spy=D("0.5")
    )
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 13),
        execution_opens={
            "SPY": DatedPrice(date(2025, 1, 13), D("120")),
            "BIL": DatedPrice(date(2025, 1, 13), D("100")),
        },
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL


def test_same_day_payment_is_not_known_at_0800_without_prior_credit_proof() -> None:
    ledger, adapter = initially_funded()
    ledger.accrue_realized_distribution(
        "SPY",
        event_id="ART-SAME-DAY",
        ex_date=date(2025, 1, 9),
        payment_date=date(2025, 1, 13),
        amount_per_share=D("2"),
    )
    ledger.pay_distributions_through(
        date(2025, 1, 13), cash_available_at=at(date(2025, 1, 13), 9)
    )

    snapshot = build_snapshot(adapter, date(2025, 1, 13), "100", "100")
    audit = adapter.build_economic_audit_state(snapshot)
    assert snapshot.status is SnapshotStatus.NOT_EVALUABLE
    assert snapshot.cash_availability_unproven_claim_ids == (1,)
    assert snapshot.settled_cash == 0
    assert audit.economic_wealth == D("101000")
    assert "disponibilité du cash" in snapshot.reason


def test_h_fin_net_rebalance_is_atomic_and_uses_only_settled_sales() -> None:
    ledger, adapter = initially_funded()
    _, intent, outcome = execute_cycle(
        adapter, date(2025, 1, 13), "120", "100", "120", "100"
    )
    assert {(item.symbol, item.quantity) for item in intent.orders} == {
        ("SPY", -42),
        ("BIL", 50),
    }
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert outcome.funding_source.value == "UNSETTLED_SALE_PROCEEDS"
    assert ledger.economic_positions == {"SPY": 458, "BIL": 550}
    assert ledger.settled_positions == {"SPY": 500, "BIL": 500}
    assert ledger.settled_cash == 0
    ledger.assert_invariants()


def test_open_gap_rejection_preserves_state_and_next_decision_inherits_it() -> None:
    ledger, adapter = initially_funded(decision_close="101")
    inherited = dict(ledger.economic_positions)
    _, rejected_intent, rejected = execute_cycle(
        adapter, date(2025, 1, 13), "120", "100", "120", "200"
    )
    assert rejected_intent.target_quantities == {"SPY": 457, "BIL": 549}
    assert rejected.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert ledger.economic_positions == inherited == {"SPY": 495, "BIL": 495}
    assert ledger.pending_settlements == []
    assert ledger.fees_recognized == 0

    _, next_intent, accepted = execute_cycle(
        adapter, date(2025, 1, 21), "80", "100", "80", "100"
    )
    assert next_intent.inherited_positions == inherited
    assert accepted.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert ledger.economic_positions == {"SPY": 563, "BIL": 450}


@pytest.mark.parametrize(
    ("basis_points", "expected_fee"),
    [("0", "0"), ("1", "9.9"), ("5", "49.5"), ("10", "99")],
)
def test_s0_s3_costs_apply_once_to_actual_initial_notional(
    basis_points: str, expected_fee: str
) -> None:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, intent, outcome = execute_cycle(
        adapter,
        date(2025, 1, 6),
        "101",
        "101",
        "100",
        "100",
        basis_points=basis_points,
    )
    assert intent.target_quantities == {"SPY": 495, "BIL": 495}
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert ledger.fees_recognized == D(expected_fee)
    assert outcome.wealth_after_trade == D("100000") - D(expected_fee)


def test_costs_accumulate_over_rebalances_and_hold_costs_nothing() -> None:
    ledger, adapter = initially_funded(decision_close="101", basis_points="1")
    assert ledger.fees_recognized == D("9.9")
    _, _, second = execute_cycle(
        adapter,
        date(2025, 1, 13),
        "120",
        "100",
        "120",
        "100",
        basis_points="1",
    )
    assert second.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert sum(second.fees.values(), D("0")) == D("0.996")
    assert ledger.fees_recognized == D("10.896")
    ledger.settle_through(date(2025, 1, 14))
    assert ledger.fees_recognized == D("10.896")

    fees_before = ledger.fees_recognized
    snapshot = build_snapshot(adapter, date(2025, 1, 21), "549", "457")
    intent = adapter.prepare_intent_from_snapshot(snapshot, target_weight_spy=D("0.5"))
    assert intent.orders == ()
    assert cost_scenario_fees(intent, {}, D("10")) == {"SPY": 0, "BIL": 0}
    hold = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 21),
        execution_opens={},
        fees={"SPY": 0, "BIL": 0},
    )
    assert hold.status is ExecutionStatus.VOLUNTARY_HOLD
    assert ledger.fees_recognized == fees_before


def test_fee_can_reject_frozen_lot_without_resizing() -> None:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, intent, outcome = execute_cycle(
        adapter,
        date(2025, 1, 6),
        "100",
        "100",
        "100",
        "100",
        basis_points="10",
    )
    assert intent.target_quantities == {"SPY": 500, "BIL": 500}
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert ledger.economic_positions == {}
    assert ledger.pending_settlements == []
    assert ledger.fees_recognized == 0


def test_accumulated_s3_costs_reject_rebalance_and_preserve_inherited_state() -> None:
    ledger, adapter = initially_funded(decision_close="101", basis_points="10")
    inherited = dict(ledger.economic_positions)
    fees_before = ledger.fees_recognized
    _, intent, outcome = execute_cycle(
        adapter,
        date(2025, 1, 13),
        "120",
        "100",
        "120",
        "101.1",
        basis_points="10",
    )
    assert intent.target_quantities == {"SPY": 457, "BIL": 549}
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert ledger.economic_positions == inherited == {"SPY": 495, "BIL": 495}
    assert ledger.pending_settlements == []
    assert ledger.fees_recognized == fees_before == D("99")


def test_snapshot_is_reproducible_and_stale_state_cannot_execute() -> None:
    ledger = artificial_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    first = build_snapshot(adapter, date(2025, 1, 6), "101", "101")
    second = build_snapshot(adapter, date(2025, 1, 6), "101", "101")
    assert first == second
    with pytest.raises(AdapterError, match="empreinte"):
        adapter.prepare_intent_from_snapshot(
            replace(first, admissible_wealth=D("1")),
            target_weight_spy=D("0.5"),
        )
    intent = adapter.prepare_intent_from_snapshot(first, target_weight_spy=D("0.5"))

    ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2025, 1, 6),
        knowledge_at=at(date(2025, 1, 6), 8),
        ex_date=date(2025, 1, 9),
        payment_date=date(2025, 1, 15),
        amount_per_share=D("1"),
    )
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 6),
        execution_opens={
            "SPY": DatedPrice(date(2025, 1, 6), D("100")),
            "BIL": DatedPrice(date(2025, 1, 6), D("100")),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert "périmé" in outcome.reason
    assert ledger.economic_positions == {}
