from __future__ import annotations

import sys
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from synthetic_decision_adapter import (  # noqa: E402
    AdapterError,
    DatedPrice,
    ExecutionStatus,
    FundingSource,
    PriceStatus,
    SyntheticDecisionAdapter,
)
from synthetic_portfolio_ledger import (  # noqa: E402
    ExecutionRequest,
    FixedOrder,
    FundingConvention,
    SyntheticPortfolioLedger,
    SyntheticSettlementCalendar,
    SyntheticTradingCalendar,
)


D = Decimal


def observation(
    value: str | None,
    price_date: date,
    status: PriceStatus = PriceStatus.AVAILABLE,
) -> DatedPrice:
    return DatedPrice(price_date, None if value is None else D(value), status)


def strict_ledger(
    cash: str = "10000",
    *,
    sessions: list[date] | None = None,
    settlement_calendar: SyntheticSettlementCalendar | None = None,
) -> SyntheticPortfolioLedger:
    sessions = sessions or [
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 6),
        date(2025, 1, 7),
        date(2025, 1, 8),
        date(2025, 1, 9),
        date(2025, 1, 10),
        date(2025, 1, 13),
        date(2025, 1, 14),
    ]
    return SyntheticPortfolioLedger(
        D(cash),
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(sessions),
        settlement_calendar=settlement_calendar or SyntheticSettlementCalendar(sessions),
    )


def prepare_from_cash(
    adapter: SyntheticDecisionAdapter,
    *,
    capital: str = "10000",
    decision_date: date = date(2025, 1, 2),
    target_weight: str = "1",
    spy_close: str = "100",
    bil_close: str = "100",
):
    return adapter.prepare_intent(
        decision_date=decision_date,
        known_market_wealth=D(capital),
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes={
            "SPY": observation(spy_close, decision_date),
            "BIL": observation(bil_close, decision_date),
        },
        target_weight_spy=D(target_weight),
    )


def test_ex_post_distribution_accounting_blocks_later_decision() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    ledger.accrue_realized_distribution(
        "SPY",
        event_id="SPY-20250102",
        ex_date=date(2025, 1, 2),
        payment_date=date(2025, 1, 3),
        amount_per_share="1",
    )
    with pytest.raises(AdapterError, match="ex post"):
        prepare_from_cash(adapter, decision_date=date(2025, 1, 3))


def funded_bil_account() -> tuple[SyntheticPortfolioLedger, SyntheticDecisionAdapter]:
    ledger = strict_ledger()
    ledger.set_prices("BIL", market_price="100", price_date=date(2025, 1, 6))
    ledger.execute_batch(
        [
            ExecutionRequest(
                FixedOrder("BIL", 100, date(2025, 1, 3), D("100")),
                D("100"),
            )
        ],
        trade_date=date(2025, 1, 6),
    )
    ledger.settle_through(date(2025, 1, 7))
    return ledger, SyntheticDecisionAdapter(ledger)


def rebalance_from_bil(
    ledger: SyntheticPortfolioLedger,
    adapter: SyntheticDecisionAdapter,
    *,
    decision_date: date = date(2025, 1, 10),
    target_weight: str = "0.2",
):
    intent = adapter.prepare_intent(
        decision_date=decision_date,
        known_market_wealth="10000",
        inherited_positions={"SPY": 0, "BIL": 100},
        decision_closes={
            "SPY": observation("100", decision_date),
            "BIL": observation("100", decision_date),
        },
        target_weight_spy=target_weight,
    )
    return adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 13),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 13)),
            "BIL": observation("100", date(2025, 1, 13)),
        },
    )


def test_adapter_requires_strict_temporal_ledger() -> None:
    with pytest.raises(AdapterError, match="strict_temporal=True"):
        SyntheticDecisionAdapter(SyntheticPortfolioLedger(D("100")))


@pytest.mark.parametrize(
    ("capital", "expected_spy", "expected_bil"),
    [("10000", 12, 40), ("100000", 120, 400), ("1000000", 1200, 4000)],
)
def test_prepare_intent_uses_whole_shares_at_three_fixed_wealth_levels(
    capital: str, expected_spy: int, expected_bil: int
) -> None:
    ledger = strict_ledger(capital)
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(
        adapter,
        capital=capital,
        target_weight="0.6",
        spy_close="500",
        bil_close="100",
    )
    assert intent.target_quantities == {"SPY": expected_spy, "BIL": expected_bil}
    assert {order.symbol: order.quantity for order in intent.orders} == {
        "SPY": expected_spy,
        "BIL": expected_bil,
    }


def test_prepare_rejects_future_dated_close_and_inconsistent_wealth() -> None:
    adapter = SyntheticDecisionAdapter(strict_ledger())
    with pytest.raises(AdapterError, match="datée de la décision"):
        adapter.prepare_intent(
            decision_date=date(2025, 1, 2),
            known_market_wealth="10000",
            inherited_positions={"SPY": 0, "BIL": 0},
            decision_closes={
                "SPY": observation("100", date(2025, 1, 3)),
                "BIL": observation("100", date(2025, 1, 2)),
            },
            target_weight_spy="1",
        )
    with pytest.raises(AdapterError, match="richesse connue"):
        prepare_from_cash(adapter, capital="9999")


def test_prepare_rejects_non_session_and_retroactive_decision() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    with pytest.raises(AdapterError, match="séance négociable"):
        prepare_from_cash(adapter, decision_date=date(2025, 1, 4))
    ledger.set_prices("SPY", market_price="100", price_date=date(2025, 1, 3))
    with pytest.raises(AdapterError, match="antidatée"):
        prepare_from_cash(adapter, decision_date=date(2025, 1, 2))


def test_adverse_open_gap_keeps_quantity_fixed_and_rejects_atomically() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("105", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert intent.target_quantities["SPY"] == 100
    assert intent.orders[0].quantity == 100
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert outcome.accounting_before == outcome.accounting_after == before
    assert ledger.pending_settlements == []


def test_favorable_open_does_not_increase_frozen_quantity() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("95", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert outcome.funding_source is FundingSource.SETTLED_CASH
    assert ledger.economic_positions["SPY"] == 100
    assert outcome.settlement_ids == (1,)
    assert outcome.wealth_before_trade == outcome.wealth_after_trade


@pytest.mark.parametrize("execution_date", [date(2025, 1, 2), date(2025, 1, 6)])
def test_decision_must_precede_and_cannot_skip_next_execution_session(
    execution_date: date,
) -> None:
    adapter = SyntheticDecisionAdapter(strict_ledger())
    intent = prepare_from_cash(adapter)
    outcome = adapter.process_intent(
        intent,
        execution_date=execution_date,
        execution_opens={},
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert outcome.accounting_before == outcome.accounting_after


def test_misdated_open_is_invalid_before_financial_mutation() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 2)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert outcome.accounting_before == outcome.accounting_after == before


def test_insufficient_settlement_calendar_is_not_evaluable() -> None:
    sessions = [date(2025, 1, 2), date(2025, 1, 3)]
    ledger = strict_ledger(sessions=sessions)
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.NOT_EVALUABLE
    assert "calendrier artificiel insuffisant" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after == before


def test_normal_bil_to_spy_rebalance_uses_unsettled_sale_proceeds() -> None:
    ledger, adapter = funded_bil_account()
    outcome = rebalance_from_bil(ledger, adapter)
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert outcome.funding_source is FundingSource.UNSETTLED_SALE_PROCEEDS
    assert ledger.economic_positions == {"BIL": 80, "SPY": 20}
    assert ledger.settled_positions == {"BIL": 100}
    assert ledger.sale_receivables == ledger.purchase_payables == D("2000")
    assert outcome.wealth_before_trade == outcome.wealth_after_trade == D("10000")
    ledger.settle_through(date(2025, 1, 14))
    assert ledger.settled_positions == {"BIL": 80, "SPY": 20}
    assert ledger.settled_cash == 0
    assert ledger.wealth_market() == D("10000")


def test_sale_of_unsettled_purchase_is_rejected_even_if_economically_held() -> None:
    sessions = [
        date(2022, 12, 30),
        date(2023, 1, 2),
        date(2023, 1, 3),
        date(2023, 1, 4),
        date(2023, 1, 5),
        date(2023, 1, 6),
    ]
    ledger = strict_ledger(sessions=sessions)
    ledger.set_prices("BIL", market_price="100", price_date=date(2023, 1, 2))
    ledger.execute_batch(
        [
            ExecutionRequest(
                FixedOrder("BIL", 100, date(2022, 12, 30), D("100")), D("100")
            )
        ],
        trade_date=date(2023, 1, 2),
    )
    assert ledger.economic_positions["BIL"] == 100
    assert ledger.settled_positions.get("BIL", 0) == 0
    adapter = SyntheticDecisionAdapter(ledger)
    intent = adapter.prepare_intent(
        decision_date=date(2023, 1, 2),
        known_market_wealth="10000",
        inherited_positions={"SPY": 0, "BIL": 100},
        decision_closes={
            "SPY": observation("100", date(2023, 1, 2)),
            "BIL": observation("100", date(2023, 1, 2)),
        },
        target_weight_spy="1",
    )
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2023, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2023, 1, 3)),
            "BIL": observation("100", date(2023, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert "intégralement payés" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after


def test_purchase_funded_by_unsettled_sale_cannot_be_resold_before_payment() -> None:
    sessions = [
        date(2022, 12, 23),
        date(2022, 12, 27),
        date(2022, 12, 28),
        date(2022, 12, 29),
        date(2022, 12, 30),
        date(2023, 1, 2),
        date(2023, 1, 3),
        date(2023, 1, 4),
        date(2023, 1, 5),
        date(2023, 1, 6),
    ]
    ledger = strict_ledger(sessions=sessions)
    ledger.set_prices("BIL", market_price="100", price_date=date(2022, 12, 27))
    ledger.execute_batch(
        [
            ExecutionRequest(
                FixedOrder("BIL", 100, date(2022, 12, 23), D("100")), D("100")
            )
        ],
        trade_date=date(2022, 12, 27),
    )
    ledger.settle_through(date(2022, 12, 29))
    first = SyntheticDecisionAdapter(ledger)
    first_intent = first.prepare_intent(
        decision_date=date(2023, 1, 2),
        known_market_wealth="10000",
        inherited_positions={"SPY": 0, "BIL": 100},
        decision_closes={
            "SPY": observation("100", date(2023, 1, 2)),
            "BIL": observation("100", date(2023, 1, 2)),
        },
        target_weight_spy="0.5",
    )
    first_outcome = first.process_intent(
        first_intent,
        execution_date=date(2023, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2023, 1, 3)),
            "BIL": observation("100", date(2023, 1, 3)),
        },
    )
    assert first_outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert first_outcome.funding_source is FundingSource.UNSETTLED_SALE_PROCEEDS
    assert ledger.economic_positions == {"BIL": 50, "SPY": 50}
    assert ledger.settled_positions.get("SPY", 0) == 0

    second_intent = first.prepare_intent(
        decision_date=date(2023, 1, 3),
        known_market_wealth="10000",
        inherited_positions={"SPY": 50, "BIL": 50},
        decision_closes={
            "SPY": observation("100", date(2023, 1, 3)),
            "BIL": observation("100", date(2023, 1, 3)),
        },
        target_weight_spy="0",
    )
    before = ledger.accounting_snapshot()
    second_outcome = first.process_intent(
        second_intent,
        execution_date=date(2023, 1, 4),
        execution_opens={
            "SPY": observation("100", date(2023, 1, 4)),
            "BIL": observation("100", date(2023, 1, 4)),
        },
    )
    assert second_outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert "SPY" in second_outcome.reason
    assert second_outcome.accounting_before == second_outcome.accounting_after == before


def test_fee_is_included_in_funding_and_rejection_is_atomic() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
        fees={"SPY": "1"},
    )
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert outcome.accounting_before == outcome.accounting_after == before
    assert ledger.fees_recognized == 0


def test_successful_fee_decreases_wealth_exactly_once_and_settlement_is_neutral() -> None:
    ledger = strict_ledger("10001")
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter, capital="10001")
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
        fees={"SPY": "1"},
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert outcome.wealth_before_trade - outcome.wealth_after_trade == D("1")
    before_settlement = ledger.wealth_market()
    ledger.settle_through(date(2025, 1, 6))
    assert ledger.wealth_market() == before_settlement


class NonMonotoneSettlementCalendar(SyntheticSettlementCalendar):
    def settlement_date(self, trade_date: date) -> date:
        overrides = {
            date(2025, 1, 3): date(2025, 1, 6),
            date(2025, 1, 8): date(2025, 1, 13),
            date(2025, 1, 9): date(2025, 1, 10),
        }
        if trade_date in overrides:
            return overrides[trade_date]
        return super().settlement_date(trade_date)


def test_later_sale_settlement_cannot_fund_earlier_purchase_settlement() -> None:
    sessions = [
        date(2025, 1, 2),
        date(2025, 1, 3),
        date(2025, 1, 6),
        date(2025, 1, 7),
        date(2025, 1, 8),
        date(2025, 1, 9),
        date(2025, 1, 10),
        date(2025, 1, 13),
    ]
    calendar = NonMonotoneSettlementCalendar(sessions)
    ledger = strict_ledger("100", sessions=sessions, settlement_calendar=calendar)
    ledger.set_prices("BIL", market_price="10", price_date=date(2025, 1, 3))
    ledger.execute_batch(
        [ExecutionRequest(FixedOrder("BIL", 10, date(2025, 1, 2), D("10")), D("10"))],
        trade_date=date(2025, 1, 3),
    )
    ledger.settle_through(date(2025, 1, 6))
    ledger.set_prices("BIL", market_price="10", price_date=date(2025, 1, 8))
    ledger.execute_batch(
        [ExecutionRequest(FixedOrder("BIL", -10, date(2025, 1, 7), D("10")), D("10"))],
        trade_date=date(2025, 1, 8),
        funding=FundingConvention.H_FIN_NET,
    )
    adapter = SyntheticDecisionAdapter(ledger)
    intent = adapter.prepare_intent(
        decision_date=date(2025, 1, 8),
        known_market_wealth="100",
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes={
            "SPY": observation("20", date(2025, 1, 8)),
            "BIL": observation("10", date(2025, 1, 8)),
        },
        target_weight_spy="1",
    )
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 9),
        execution_opens={
            "SPY": observation("20", date(2025, 1, 9)),
            "BIL": observation("10", date(2025, 1, 9)),
        },
    )
    assert outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert "financement net impossible" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after == before


class CommitmentSettlementCalendar(SyntheticSettlementCalendar):
    def settlement_date(self, trade_date: date) -> date:
        overrides = {
            date(2022, 12, 27): date(2022, 12, 29),
            date(2023, 1, 3): date(2023, 1, 10),
            date(2023, 1, 4): date(2023, 1, 13),
            date(2023, 1, 5): date(2023, 1, 13),
        }
        if trade_date in overrides:
            return overrides[trade_date]
        return super().settlement_date(trade_date)


def test_same_sale_proceeds_cannot_cover_incompatible_total_obligations() -> None:
    sessions = [
        date(2022, 12, 23),
        date(2022, 12, 27),
        date(2022, 12, 28),
        date(2022, 12, 29),
        date(2022, 12, 30),
        date(2023, 1, 2),
        date(2023, 1, 3),
        date(2023, 1, 4),
        date(2023, 1, 5),
        date(2023, 1, 6),
        date(2023, 1, 9),
        date(2023, 1, 10),
        date(2023, 1, 11),
        date(2023, 1, 12),
        date(2023, 1, 13),
    ]
    ledger = strict_ledger(
        "100",
        sessions=sessions,
        settlement_calendar=CommitmentSettlementCalendar(sessions),
    )
    ledger.set_prices("BIL", market_price="10", price_date=date(2022, 12, 27))
    ledger.execute_batch(
        [ExecutionRequest(FixedOrder("BIL", 10, date(2022, 12, 23), D("10")), D("10"))],
        trade_date=date(2022, 12, 27),
    )
    ledger.settle_through(date(2022, 12, 29))
    ledger.set_prices("BIL", market_price="10", price_date=date(2023, 1, 3))
    ledger.execute_batch(
        [ExecutionRequest(FixedOrder("BIL", -10, date(2023, 1, 2), D("10")), D("10"))],
        trade_date=date(2023, 1, 3),
        funding=FundingConvention.H_FIN_NET,
    )

    adapter = SyntheticDecisionAdapter(ledger)
    first_intent = adapter.prepare_intent(
        decision_date=date(2023, 1, 3),
        known_market_wealth="100",
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes={
            "SPY": observation("30", date(2023, 1, 3)),
            "BIL": observation("70", date(2023, 1, 3)),
        },
        target_weight_spy="0.5",
    )
    first_outcome = adapter.process_intent(
        first_intent,
        execution_date=date(2023, 1, 4),
        execution_opens={
            "SPY": observation("30", date(2023, 1, 4)),
            "BIL": observation("70", date(2023, 1, 4)),
        },
    )
    assert first_outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert first_outcome.funding_source is FundingSource.UNSETTLED_SALE_PROCEEDS
    assert ledger.purchase_payables == D("30")

    second_intent = adapter.prepare_intent(
        decision_date=date(2023, 1, 4),
        known_market_wealth="90",
        inherited_positions={"SPY": 1, "BIL": 0},
        decision_closes={
            "SPY": observation("20", date(2023, 1, 4)),
            "BIL": observation("70", date(2023, 1, 4)),
        },
        target_weight_spy="1",
    )
    before = ledger.accounting_snapshot()
    second_outcome = adapter.process_intent(
        second_intent,
        execution_date=date(2023, 1, 5),
        execution_opens={
            "SPY": observation("25", date(2023, 1, 5)),
            "BIL": observation("70", date(2023, 1, 5)),
        },
    )
    assert second_intent.orders[0].quantity == 3
    assert second_outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED
    assert "financement net impossible" in second_outcome.reason
    assert second_outcome.accounting_before == second_outcome.accounting_after == before
    assert ledger.purchase_payables == D("30")


@pytest.mark.parametrize("status", [PriceStatus.MISSING, PriceStatus.DISPUTED])
def test_missing_or_disputed_open_is_not_evaluable_before_mutation(
    status: PriceStatus,
) -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    journal_length = len(ledger.journal)
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation(None, date(2025, 1, 3), status),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.NOT_EVALUABLE
    assert outcome.accounting_before == outcome.accounting_after == before
    assert len(ledger.journal) == journal_length


def test_voluntary_hold_is_distinct_from_rejection() -> None:
    ledger, adapter = funded_bil_account()
    intent = adapter.prepare_intent(
        decision_date=date(2025, 1, 10),
        known_market_wealth="10000",
        inherited_positions={"SPY": 0, "BIL": 100},
        decision_closes={
            "SPY": observation("100", date(2025, 1, 10)),
            "BIL": observation("100", date(2025, 1, 10)),
        },
        target_weight_spy="0",
    )
    assert intent.orders == ()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 13),
        execution_opens={},
        documentary_issue="un open inutile au hold est contesté",
    )
    assert outcome.status is ExecutionStatus.VOLUNTARY_HOLD
    assert outcome.accounting_before == outcome.accounting_after


def test_same_intent_cannot_execute_twice() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    opens = {
        "SPY": observation("95", date(2025, 1, 3)),
        "BIL": observation("100", date(2025, 1, 3)),
    }
    first = adapter.process_intent(
        intent, execution_date=date(2025, 1, 3), execution_opens=opens
    )
    after_first = ledger.accounting_snapshot()
    second = adapter.process_intent(
        intent, execution_date=date(2025, 1, 3), execution_opens=opens
    )
    assert first.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert second.status is ExecutionStatus.INVALID_INPUT
    assert ledger.accounting_snapshot() == after_first
    assert len(ledger.pending_settlements) == 1


def test_documentary_issue_stops_before_price_or_financial_mutation() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2025, 1, 3),
        execution_opens={},
        documentary_issue="CALENDAR_UNVERIFIED",
    )
    assert outcome.status is ExecutionStatus.NOT_EVALUABLE
    assert outcome.reason == "CALENDAR_UNVERIFIED"
    assert outcome.accounting_before == outcome.accounting_after == before


@pytest.mark.parametrize(
    "mutation",
    [
        lambda intent: replace(
            intent,
            target_quantities={"SPY": 1, "BIL": 0},
        ),
        lambda intent: replace(
            intent,
            orders=(
                FixedOrder("SPY", 1, intent.decision_date, D("100")),
            ),
        ),
        lambda intent: replace(
            intent,
            decision_prices={"SPY": D("99"), "BIL": D("100")},
        ),
        lambda intent: replace(intent, target_weight_spy=D("0.5")),
    ],
)
def test_modified_intention_is_rejected_before_any_mutation(mutation) -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    intent = prepare_from_cash(adapter)
    forged = mutation(intent)
    before = ledger.accounting_snapshot()
    journal_length = len(ledger.journal)
    outcome = adapter.process_intent(
        forged,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert "empreinte" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after == before
    assert len(ledger.journal) == journal_length


def test_identifier_reused_for_different_intention_is_rejected() -> None:
    ledger = strict_ledger()
    adapter = SyntheticDecisionAdapter(ledger)
    first = prepare_from_cash(adapter, target_weight="1")
    second = prepare_from_cash(adapter, target_weight="0")
    forged = replace(second, intent_id=first.intent_id)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        forged,
        execution_date=date(2025, 1, 3),
        execution_opens={
            "SPY": observation("100", date(2025, 1, 3)),
            "BIL": observation("100", date(2025, 1, 3)),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert "identifiant" in outcome.reason or "empreinte" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after == before


def test_normal_settlement_between_decision_and_execution_is_allowed() -> None:
    sessions = [
        date(2023, 1, 2),
        date(2023, 1, 3),
        date(2023, 1, 4),
        date(2023, 1, 5),
        date(2023, 1, 6),
        date(2023, 1, 9),
    ]
    ledger = strict_ledger("100", sessions=sessions)
    ledger.set_prices("BIL", market_price="10", price_date=date(2023, 1, 2))
    ledger.execute_batch(
        [ExecutionRequest(FixedOrder("BIL", 10, date(2022, 12, 30), D("10")), D("10"))],
        trade_date=date(2023, 1, 2),
    )
    adapter = SyntheticDecisionAdapter(ledger)
    intent = adapter.prepare_intent(
        decision_date=date(2023, 1, 3),
        known_market_wealth="100",
        inherited_positions={"SPY": 0, "BIL": 10},
        decision_closes={
            "SPY": observation("10", date(2023, 1, 3)),
            "BIL": observation("10", date(2023, 1, 3)),
        },
        target_weight_spy="1",
    )
    ledger.settle_through(date(2023, 1, 4))
    outcome = adapter.process_intent(
        intent,
        execution_date=date(2023, 1, 4),
        execution_opens={
            "SPY": observation("10", date(2023, 1, 4)),
            "BIL": observation("10", date(2023, 1, 4)),
        },
    )
    assert outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert ledger.economic_positions == {"BIL": 0, "SPY": 10}
