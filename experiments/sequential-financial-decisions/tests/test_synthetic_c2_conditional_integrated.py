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
    CashAvailabilityConvention,
    DatedPrice,
    ExecutionStatus,
    PriceStatus,
    ProtocolMode,
    SnapshotStatus,
    SyntheticDecisionAdapter,
    cost_scenario_fees,
    decision_snapshot_content_sha256,
    decision_snapshot_payload,
    economic_audit_content_sha256,
    economic_audit_payload,
    intent_content_sha256,
    intent_payload,
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
    date(2025, 2, 7),
    date(2025, 2, 10),
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


def at(day: date, hour: int = 8, minute: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=ET)


def conditional_ledger() -> SyntheticPortfolioLedger:
    start = date(2025, 1, 2)
    business_dates = tuple(
        start + timedelta(days=index) for index in range(50)
    )
    business_dates = tuple(
        item
        for item in business_dates
        if item.weekday() < 5 and item != date(2025, 1, 20)
    )
    return SyntheticPortfolioLedger(
        D("100000"),
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(SESSIONS),
        settlement_calendar=SyntheticSettlementCalendar(business_dates),
    )


def conditional_snapshot(
    adapter: SyntheticDecisionAdapter,
    decision_day: date,
    spy_close: str,
    bil_close: str,
    *,
    convention: CashAvailabilityConvention = CashAvailabilityConvention.D_PLUS_1,
):
    previous = max(item for item in SESSIONS if item < decision_day)
    return adapter.build_conditional_decision_snapshot(
        decision_at=at(decision_day),
        decision_closes={
            "SPY": DatedPrice(previous, D(spy_close), PriceStatus.AVAILABLE),
            "BIL": DatedPrice(previous, D(bil_close), PriceStatus.AVAILABLE),
        },
        close_available_at={"SPY": at(previous, 16), "BIL": at(previous, 16)},
        provenance=PROVENANCE,
        protocol_mode=ProtocolMode.EXPLORATORY_CONDITIONAL,
        cash_availability_convention=convention,
    )


def conditional_cycle(
    adapter: SyntheticDecisionAdapter,
    decision_day: date,
    spy_close: str,
    bil_close: str,
    spy_open: str,
    bil_open: str,
    *,
    basis_points: str = "0",
    convention: CashAvailabilityConvention = CashAvailabilityConvention.D_PLUS_1,
):
    snapshot = conditional_snapshot(
        adapter,
        decision_day,
        spy_close,
        bil_close,
        convention=convention,
    )
    audit = adapter.build_economic_audit_state(snapshot)
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
    return snapshot, audit, intent, outcome


def initialize(
    *, basis_points: str = "0", close: str = "100"
) -> tuple[SyntheticPortfolioLedger, SyntheticDecisionAdapter]:
    ledger = conditional_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, _, _, outcome = conditional_cycle(
        adapter,
        date(2025, 1, 6),
        close,
        close,
        "100",
        "100",
        basis_points=basis_points,
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    ledger.settle_through(date(2025, 1, 7))
    return ledger, adapter


def accrue_unknown_spy_distribution(
    ledger: SyntheticPortfolioLedger, amount: str = "2"
) -> int:
    return ledger.accrue_realized_distribution(
        "SPY",
        event_id=f"ART-SPY-{amount}",
        ex_date=date(2025, 1, 13),
        payment_date=date(2025, 1, 24),
        amount_per_share=D(amount),
    )


def set_marks(
    ledger: SyntheticPortfolioLedger, day: date, spy: str, bil: str
) -> None:
    ledger.set_prices("SPY", market_price=D(spy), price_date=day)
    ledger.set_prices("BIL", market_price=D(bil), price_date=day)


def test_strict_mode_still_blocks_unknown_claim_while_eb_is_explicit() -> None:
    ledger, adapter = initialize()
    accrue_unknown_spy_distribution(ledger)
    previous = date(2025, 1, 10)
    strict = adapter.build_decision_snapshot(
        decision_at=at(date(2025, 1, 13)),
        decision_closes={
            "SPY": DatedPrice(previous, D("100")),
            "BIL": DatedPrice(previous, D("100")),
        },
        close_available_at={"SPY": at(previous, 16), "BIL": at(previous, 16)},
        provenance=PROVENANCE,
    )
    assert strict.status is SnapshotStatus.NOT_EVALUABLE
    assert strict.protocol_mode is ProtocolMode.STRICT_POINT_IN_TIME
    with pytest.raises(AdapterError, match="activé explicitement"):
        adapter.build_conditional_decision_snapshot(
            decision_at=at(date(2025, 1, 13)),
            decision_closes={
                "SPY": DatedPrice(previous, D("100")),
                "BIL": DatedPrice(previous, D("100")),
            },
            close_available_at={
                "SPY": at(previous, 16),
                "BIL": at(previous, 16),
            },
            provenance=PROVENANCE,
            protocol_mode=ProtocolMode.STRICT_POINT_IN_TIME,
            cash_availability_convention=CashAvailabilityConvention.D_PLUS_1,
        )


def test_ex_date_budget_does_not_double_count_embedded_unknown_claim() -> None:
    ledger, adapter = initialize()
    claim_id = accrue_unknown_spy_distribution(ledger)
    snapshot = conditional_snapshot(
        adapter, date(2025, 1, 13), "100", "100"
    )
    audit = adapter.build_economic_audit_state(snapshot)
    assert ledger.distribution_receivables == D("1000")
    assert snapshot.embedded_ex_date_claim_ids == (claim_id,)
    assert snapshot.excluded_distribution_claim_ids == (claim_id,)
    assert audit.economic_wealth == D("100000")
    assert snapshot.decision_budget == D("100000")
    assert snapshot.admissible_wealth == D("100000")
    assert snapshot.financing_cash == 0
    assert snapshot.valuation_reference_at == at(date(2025, 1, 10), 16)
    assert snapshot.information_cutoff == at(date(2025, 1, 13), 8)
    assert snapshot.protocol_mode is ProtocolMode.EXPLORATORY_CONDITIONAL
    assert (
        snapshot.cash_availability_convention
        is CashAvailabilityConvention.D_PLUS_1
    )
    intent = adapter.prepare_intent_from_snapshot(snapshot, target_weight_spy=D("0.5"))
    assert intent.target_quantities == {"SPY": 500, "BIL": 500}
    assert intent.orders == ()
    assert "economic_wealth" not in intent_payload(intent)
    hold = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 13),
        execution_opens={},
    )
    assert hold.status is ExecutionStatus.VOLUNTARY_HOLD
    set_marks(ledger, date(2025, 1, 13), "98", "100")
    assert ledger.wealth_market() == D("100000")


def test_ex_date_open_gap_rejects_frozen_lot_without_resizing() -> None:
    ledger, adapter = initialize()
    claim_id = accrue_unknown_spy_distribution(ledger)
    snapshot, audit, intent, outcome = conditional_cycle(
        adapter, date(2025, 1, 13), "120", "100", "118", "100"
    )
    assert audit.economic_wealth == snapshot.decision_budget == D("110000")
    assert snapshot.embedded_ex_date_claim_ids == (claim_id,)
    assert intent.target_quantities == {"SPY": 458, "BIL": 550}
    assert {(order.symbol, order.quantity) for order in intent.orders} == {
        ("SPY", -42),
        ("BIL", 50),
    }
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert outcome.reason == "financement E-B insuffisant pour le lot figé"
    assert ledger.economic_positions == {"SPY": 500, "BIL": 500}
    assert ledger.distribution_receivables == D("1000")
    assert ledger.pending_settlements == []


def test_post_ex_unknown_amount_is_non_interfering_for_every_policy_surface() -> None:
    results = []
    for amount in ("2", "7"):
        ledger, adapter = initialize()
        accrue_unknown_spy_distribution(ledger, amount)
        snapshot = conditional_snapshot(
            adapter, date(2025, 1, 21), "98", "100"
        )
        audit = adapter.build_economic_audit_state(snapshot)
        intent = adapter.prepare_intent_from_snapshot(
            snapshot, target_weight_spy=D("0.5")
        )
        results.append((snapshot, audit, intent))
    small, large = results
    assert small[0].decision_budget == large[0].decision_budget == D("99000")
    assert small[0] == large[0]
    assert decision_snapshot_payload(small[0]) == decision_snapshot_payload(large[0])
    assert small[0].snapshot_id == large[0].snapshot_id
    assert decision_snapshot_content_sha256(small[0]) == (
        decision_snapshot_content_sha256(large[0])
    )
    assert small[1].economic_wealth == D("100000")
    assert large[1].economic_wealth == D("102500")
    assert economic_audit_payload(small[1]) != economic_audit_payload(large[1])
    assert economic_audit_content_sha256(small[1]) != (
        economic_audit_content_sha256(large[1])
    )
    assert small[2] == large[2]
    assert intent_payload(small[2]) == intent_payload(large[2])
    assert small[2].intent_id == large[2].intent_id
    assert intent_content_sha256(small[2]) == intent_content_sha256(large[2])


def test_policy_snapshot_schema_excludes_all_reconstructible_audit_amounts() -> None:
    ledger, adapter = initialize()
    accrue_unknown_spy_distribution(ledger, "9")
    snapshot = conditional_snapshot(adapter, date(2025, 1, 21), "98", "100")
    payload = decision_snapshot_payload(snapshot)
    forbidden = {
        "economic_distribution_receivables",
        "economic_wealth",
        "excluded_distribution_claims",
        "unavailable_paid_cash",
    }
    assert forbidden.isdisjoint(snapshot.__dataclass_fields__)
    assert forbidden.isdisjoint(payload)


def test_known_claim_enters_budget_only_after_cum_close_is_past() -> None:
    ledger, adapter = initialize()
    announcement = ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2025, 1, 8),
        knowledge_at=at(date(2025, 1, 8), 10),
        ex_date=date(2025, 1, 13),
        payment_date=date(2025, 1, 24),
        amount_per_share=D("2"),
    )
    ledger.accrue_announced_distribution(
        announcement, event_date=date(2025, 1, 13)
    )
    current_ex = conditional_snapshot(
        adapter, date(2025, 1, 13), "100", "100"
    )
    post_ex = conditional_snapshot(
        adapter, date(2025, 1, 21), "98", "100"
    )
    assert current_ex.decision_budget == D("100000")
    assert current_ex.embedded_ex_date_claim_ids == (1,)
    assert post_ex.decision_budget == D("100000")
    assert post_ex.known_distribution_receivables == D("1000")
    assert post_ex.embedded_ex_date_claim_ids == ()


def test_paid_cash_is_economic_but_d1_and_d2_control_budget_and_funding() -> None:
    ledger, adapter = initialize()
    accrue_unknown_spy_distribution(ledger)
    ledger.pay_distributions_through(date(2025, 1, 24))
    d1 = conditional_snapshot(
        adapter,
        date(2025, 1, 27),
        "100",
        "100",
        convention=CashAvailabilityConvention.D_PLUS_1,
    )
    d2 = conditional_snapshot(
        adapter,
        date(2025, 1, 27),
        "100",
        "100",
        convention=CashAvailabilityConvention.D_PLUS_2,
    )
    d1_audit = adapter.build_economic_audit_state(d1)
    d2_audit = adapter.build_economic_audit_state(d2)
    assert ledger.settled_cash == D("1000")
    assert d1_audit.economic_wealth == d2_audit.economic_wealth == D("101000")
    assert d1.decision_budget == D("101000")
    assert d1.financing_cash == D("1000")
    assert d1_audit.unavailable_paid_cash == 0
    assert d2.decision_budget == D("100000")
    assert d2.financing_cash == 0
    assert d2_audit.unavailable_paid_cash == D("1000")


def test_cash_delay_skips_weekend_and_non_settlement_day() -> None:
    ledger = conditional_ledger()
    calendar = ledger.settlement_calendar
    assert calendar is not None
    assert calendar.business_date_after(date(2025, 1, 17), 1) == date(2025, 1, 21)
    assert calendar.business_date_after(date(2025, 1, 17), 2) == date(2025, 1, 22)


def test_same_day_payment_is_not_available_at_0800_under_eb() -> None:
    ledger, adapter = initialize()
    ledger.accrue_realized_distribution(
        "SPY",
        event_id="ART-SAME-DAY",
        ex_date=date(2025, 1, 13),
        payment_date=date(2025, 1, 13),
        amount_per_share=D("2"),
    )
    ledger.pay_distributions_through(date(2025, 1, 13))
    snapshot = conditional_snapshot(
        adapter, date(2025, 1, 13), "100", "100"
    )
    audit = adapter.build_economic_audit_state(snapshot)
    assert audit.unavailable_paid_cash == D("1000")
    assert snapshot.financing_cash == 0
    assert snapshot.decision_budget == D("100000")


def run_integrated_sequence() -> dict[str, object]:
    ledger, adapter = initialize()
    claim_id = accrue_unknown_spy_distribution(ledger)
    ex_snapshot, ex_audit, ex_intent, ex_hold = conditional_cycle(
        adapter, date(2025, 1, 13), "100", "100", "98", "100"
    )
    set_marks(ledger, date(2025, 1, 13), "98", "100")
    drift_snapshot, drift_audit, drift_intent, drift = conditional_cycle(
        adapter, date(2025, 1, 21), "120", "100", "120", "100"
    )
    ledger.settle_through(date(2025, 1, 22))
    positions_before_payment = dict(ledger.economic_positions)
    ledger.pay_distributions_through(date(2025, 1, 24))
    d1_snapshot, d1_audit, paid_intent, paid = conditional_cycle(
        adapter, date(2025, 1, 27), "100", "100", "100", "100"
    )
    ledger.settle_through(date(2025, 1, 28))
    inherited = dict(ledger.economic_positions)
    inherited_cash = ledger.settled_cash
    _, rejected_audit, rejected_intent, rejected = conditional_cycle(
        adapter, date(2025, 2, 3), "120", "100", "120", "200"
    )
    hold_snapshot, hold_audit, hold_intent, hold = conditional_cycle(
        adapter, date(2025, 2, 10), "100", "100", "100", "100"
    )
    return {
        "ledger": ledger,
        "claim_id": claim_id,
        "ex_snapshot": ex_snapshot,
        "ex_audit": ex_audit,
        "ex_intent": ex_intent,
        "ex_hold": ex_hold,
        "drift_snapshot": drift_snapshot,
        "drift_audit": drift_audit,
        "drift_intent": drift_intent,
        "drift": drift,
        "positions_before_payment": positions_before_payment,
        "d1_snapshot": d1_snapshot,
        "d1_audit": d1_audit,
        "paid_intent": paid_intent,
        "paid": paid,
        "inherited": inherited,
        "inherited_cash": inherited_cash,
        "rejected_intent": rejected_intent,
        "rejected_audit": rejected_audit,
        "rejected": rejected,
        "hold_snapshot": hold_snapshot,
        "hold_audit": hold_audit,
        "hold_intent": hold_intent,
        "hold": hold,
    }


def test_integrated_c2_sequence_inherits_state_settles_rejects_and_holds() -> None:
    result = run_integrated_sequence()
    ledger = result["ledger"]
    ex_snapshot = result["ex_snapshot"]
    ex_intent = result["ex_intent"]
    ex_hold = result["ex_hold"]
    assert ex_snapshot.embedded_ex_date_claim_ids == (result["claim_id"],)
    assert ex_intent.orders == ()
    assert ex_hold.status is ExecutionStatus.VOLUNTARY_HOLD

    drift_snapshot = result["drift_snapshot"]
    drift_intent = result["drift_intent"]
    drift = result["drift"]
    assert drift_snapshot.economic_positions == {"SPY": 500, "BIL": 500}
    assert drift_snapshot.settled_positions == {"SPY": 500, "BIL": 500}
    assert drift_snapshot.decision_budget == D("110000")
    drift_audit = result["drift_audit"]
    assert drift_audit.economic_wealth == D("111000")
    assert drift_intent.target_quantities == {"SPY": 458, "BIL": 550}
    assert drift.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert drift.funding_source.value == "UNSETTLED_SALE_PROCEEDS"
    assert drift.wealth_before_trade == drift.wealth_after_trade == D("111000")

    assert result["positions_before_payment"] == {"SPY": 458, "BIL": 550}
    d1_snapshot = result["d1_snapshot"]
    paid_intent = result["paid_intent"]
    paid = result["paid"]
    assert d1_snapshot.financing_cash == D("1040")
    assert paid_intent.inherited_positions == {"SPY": 458, "BIL": 550}
    assert paid.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert all(claim.paid for claim in ledger.distribution_claims)
    assert ledger.distribution_receivables == 0
    assert len(
        [entry for entry in ledger.journal if entry.kind == "DISTRIBUTION_PAYMENT"]
    ) == 1

    rejected_intent = result["rejected_intent"]
    rejected = result["rejected"]
    assert rejected.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert rejected.reason == "financement E-B insuffisant pour le lot figé"
    assert rejected_intent.target_quantities == {"SPY": 466, "BIL": 560}
    assert rejected.accounting_before == rejected.accounting_after
    assert ledger.economic_positions == result["inherited"] == {"SPY": 509, "BIL": 509}
    assert ledger.settled_cash == result["inherited_cash"] == D("40")
    assert ledger.pending_settlements == []

    hold_snapshot = result["hold_snapshot"]
    hold_intent = result["hold_intent"]
    hold = result["hold"]
    assert hold_snapshot.economic_positions == result["inherited"]
    assert hold_intent.inherited_positions == result["inherited"]
    assert hold_intent.orders == ()
    assert hold.status is ExecutionStatus.VOLUNTARY_HOLD
    ledger.assert_invariants()


def test_integrated_sequence_is_reproducible() -> None:
    first = run_integrated_sequence()
    second = run_integrated_sequence()
    keys = (
        "ex_snapshot",
        "ex_intent",
        "drift_snapshot",
        "drift_intent",
        "d1_snapshot",
        "paid_intent",
        "rejected_intent",
        "hold_snapshot",
        "hold_intent",
    )
    assert {key: first[key] for key in keys} == {
        key: second[key] for key in keys
    }
    assert first["ledger"].accounting_snapshot() == second["ledger"].accounting_snapshot()


@pytest.mark.parametrize(
    ("basis_points", "expected_fee"),
    [("0", "0"), ("1", "9.9"), ("5", "49.5"), ("10", "99")],
)
def test_eb_cost_scenarios_apply_once_to_traded_notional(
    basis_points: str, expected_fee: str
) -> None:
    ledger = conditional_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, _, intent, outcome = conditional_cycle(
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
    assert sum(outcome.fees.values(), D("0")) == D(expected_fee)
    assert ledger.fees_recognized == D(expected_fee)
    assert outcome.wealth_after_trade == D("100000") - D(expected_fee)
    ledger.settle_through(date(2025, 1, 7))
    assert ledger.fees_recognized == D(expected_fee)


def test_eb_fee_rejection_preserves_frozen_intent_and_state() -> None:
    ledger = conditional_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    _, _, intent, outcome = conditional_cycle(
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
    assert outcome.reason == "financement E-B insuffisant pour le lot figé"
    assert ledger.economic_positions == {}
    assert ledger.pending_settlements == []
    assert ledger.fees_recognized == 0


def test_eb_costs_accumulate_and_hold_adds_no_fee() -> None:
    ledger, adapter = initialize(basis_points="1", close="101")
    initial_fee = ledger.fees_recognized
    _, _, _, second = conditional_cycle(
        adapter,
        date(2025, 1, 13),
        "120",
        "100",
        "120",
        "100",
        basis_points="1",
    )
    assert second.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    second_fee = sum(second.fees.values(), D("0"))
    assert ledger.fees_recognized == initial_fee + second_fee
    ledger.settle_through(date(2025, 1, 14))
    assert ledger.fees_recognized == initial_fee + second_fee

    fees_before_hold = ledger.fees_recognized
    _, _, intent, hold = conditional_cycle(
        adapter,
        date(2025, 1, 21),
        "549",
        "457",
        "549",
        "457",
        basis_points="10",
    )
    assert intent.orders == ()
    assert hold.status is ExecutionStatus.VOLUNTARY_HOLD
    assert ledger.fees_recognized == fees_before_hold


def test_eb_snapshot_and_intent_hashes_detect_tampering_and_staleness() -> None:
    ledger, adapter = initialize()
    snapshot = conditional_snapshot(
        adapter, date(2025, 1, 13), "100", "100"
    )
    with pytest.raises(AdapterError, match="empreinte"):
        adapter.prepare_intent_from_snapshot(
            replace(snapshot, decision_budget=D("1")), target_weight_spy=D("0.5")
        )
    intent = adapter.prepare_intent_from_snapshot(snapshot, target_weight_spy=D("0.5"))
    set_marks(ledger, date(2025, 1, 13), "100", "100")
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 13),
        execution_opens={
            "SPY": DatedPrice(date(2025, 1, 13), D("100")),
            "BIL": DatedPrice(date(2025, 1, 13), D("100")),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert "périmé" in outcome.reason


def test_synthetic_c1_c2_share_accounting_but_only_c2_rebalances() -> None:
    c1, _ = initialize()
    c2, c2_adapter = initialize()
    accrue_unknown_spy_distribution(c1)
    accrue_unknown_spy_distribution(c2)
    set_marks(c1, date(2025, 1, 13), "98", "100")
    set_marks(c2, date(2025, 1, 13), "98", "100")

    _, _, c2_intent, c2_trade = conditional_cycle(
        c2_adapter, date(2025, 1, 21), "120", "100", "120", "100"
    )
    assert c2_trade.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert c2_intent.orders
    c2.settle_through(date(2025, 1, 22))

    set_marks(c1, date(2025, 1, 21), "120", "100")
    c1.pay_distributions_through(date(2025, 1, 24))
    c2.pay_distributions_through(date(2025, 1, 24))
    set_marks(c1, date(2025, 2, 10), "100", "100")
    set_marks(c2, date(2025, 2, 10), "100", "100")

    assert c1.economic_positions == {"SPY": 500, "BIL": 500}
    assert c2.economic_positions == {"SPY": 458, "BIL": 550}
    assert c1.distribution_receivables == c2.distribution_receivables == 0
    assert c1.wealth_market() == (
        D("100") * 500 + D("100") * 500 + c1.settled_cash
    )
    assert c2.wealth_market() == (
        D("100") * 458 + D("100") * 550 + c2.settled_cash
    )
    assert not [entry for entry in c1.journal if entry.kind == "TRADE" and entry.event_date > date(2025, 1, 6)]
    c1.assert_invariants()
    c2.assert_invariants()
