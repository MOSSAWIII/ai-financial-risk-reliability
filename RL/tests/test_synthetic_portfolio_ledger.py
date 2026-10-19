from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from synthetic_portfolio_ledger import (  # noqa: E402
    ExecutionRequest,
    FixedOrder,
    FundingConvention,
    LedgerError,
    SyntheticPortfolioLedger,
    SyntheticSettlementCalendar,
    SyntheticTradingCalendar,
    whole_share_quantity,
)


D = Decimal
DECISION = date(2024, 1, 2)
TRADE = date(2024, 1, 3)
SETTLEMENT = date(2024, 1, 5)


def request(
    symbol: str,
    quantity: int,
    execution_price: str,
    *,
    decision_price: str | None = None,
    decision_date: date = DECISION,
    fee: str = "0",
) -> ExecutionRequest:
    price = decision_price if decision_price is not None else execution_price
    return ExecutionRequest(
        FixedOrder(symbol, quantity, decision_date, D(price)),
        D(execution_price),
        D(fee),
    )


def buy_and_settle(
    ledger: SyntheticPortfolioLedger,
    symbol: str,
    quantity: int,
    price: str,
) -> None:
    ledger.set_prices(symbol, market_price=price, nav_price=price)
    ledger.execute_batch(
        [request(symbol, quantity, price)],
        trade_date=TRADE,
        settlement_date=SETTLEMENT,
    )
    ledger.settle_through(SETTLEMENT)


def test_initialization_market_and_nav_wealth() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100", nav_price="99")
    assert ledger.wealth_market() == D("1000")
    assert ledger.wealth_nav() == D("1000")
    assert ledger.accounting_snapshot().settled_cash == D("1000")


def test_simple_purchase_preserves_wealth_and_separates_settlement() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100", nav_price="99")
    before = ledger.wealth_market()
    ledger.execute_batch(
        [request("SPY", 5, "100")], trade_date=TRADE, settlement_date=SETTLEMENT
    )
    assert ledger.economic_positions["SPY"] == 5
    assert ledger.settled_positions.get("SPY", 0) == 0
    assert ledger.settled_cash == D("1000")
    assert ledger.purchase_payables == D("500")
    assert ledger.wealth_market() == before

    ledger.settle_through(SETTLEMENT)
    assert ledger.settled_positions["SPY"] == 5
    assert ledger.settled_cash == D("500")
    assert ledger.purchase_payables == 0
    assert ledger.wealth_market() == before


def test_simple_sale_preserves_wealth_before_and_after_settlement() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "SPY", 5, "100")
    before = ledger.wealth_market()
    ledger.execute_batch(
        [request("SPY", -2, "100", decision_date=date(2024, 1, 8))],
        trade_date=date(2024, 1, 9),
        settlement_date=date(2024, 1, 11),
    )
    assert ledger.economic_positions["SPY"] == 3
    assert ledger.settled_positions["SPY"] == 5
    assert ledger.sale_receivables == D("200")
    assert ledger.wealth_market() == before
    ledger.settle_through(date(2024, 1, 11))
    assert ledger.settled_positions["SPY"] == 3
    assert ledger.settled_cash == D("700")
    assert ledger.wealth_market() == before


def test_fee_reduces_wealth_exactly_once() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100")
    before = ledger.wealth_market()
    ledger.execute_batch(
        [request("SPY", 5, "100", fee="3.25")],
        trade_date=TRADE,
        settlement_date=SETTLEMENT,
    )
    assert ledger.purchase_payables == D("503.25")
    assert ledger.fees_recognized == D("3.25")
    assert ledger.wealth_market() == before - D("3.25")
    ledger.settle_through(SETTLEMENT)
    assert ledger.wealth_market() == before - D("3.25")


def test_market_price_change_affects_only_held_quantity() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "SPY", 5, "100")
    ledger.set_prices("SPY", market_price="112")
    assert ledger.wealth_market() == D("1060")


def test_multiple_transactions_same_session_are_atomic() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100")
    ledger.set_prices("BIL", market_price="50")
    ids = ledger.execute_batch(
        [request("SPY", 2, "100"), request("BIL", 3, "50")],
        trade_date=TRADE,
        settlement_date=SETTLEMENT,
    )
    assert len(ids) == 2
    assert ledger.economic_positions == {"SPY": 2, "BIL": 3}
    assert ledger.purchase_payables == D("350")
    assert ledger.wealth_market() == D("1000")


def test_oversale_is_rejected_without_accounting_change() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "SPY", 2, "100")
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="vente supérieure"):
        ledger.execute_batch(
            [request("SPY", -3, "100", decision_date=date(2024, 1, 8))],
            trade_date=date(2024, 1, 9),
            settlement_date=date(2024, 1, 11),
        )
    assert ledger.accounting_snapshot() == before
    assert ledger.rejections[-1].operation == "EXECUTE_BATCH"


def test_unfunded_purchase_is_rejected_atomically() -> None:
    ledger = SyntheticPortfolioLedger(D("100"))
    ledger.set_prices("SPY", market_price="60")
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="cash réglé insuffisant"):
        ledger.execute_batch(
            [request("SPY", 2, "60")], trade_date=TRADE, settlement_date=SETTLEMENT
        )
    assert ledger.accounting_snapshot() == before
    assert len(ledger.pending_settlements) == 0


def test_existing_purchase_payable_reserves_conservative_cash() -> None:
    ledger = SyntheticPortfolioLedger(D("100"))
    ledger.set_prices("BIL", market_price="10")
    ledger.execute_batch(
        [request("BIL", 8, "10")], trade_date=TRADE, settlement_date=SETTLEMENT
    )
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="cash réglé insuffisant"):
        ledger.execute_batch(
            [request("BIL", 3, "10", decision_date=date(2024, 1, 3))],
            trade_date=date(2024, 1, 4),
            settlement_date=date(2024, 1, 8),
        )
    assert ledger.accounting_snapshot() == before


def test_sale_cannot_settle_before_the_shares_are_delivered() -> None:
    ledger = SyntheticPortfolioLedger(D("100"))
    ledger.set_prices("SPY", market_price="10")
    ledger.execute_batch(
        [request("SPY", 5, "10")],
        trade_date=date(2024, 1, 3),
        settlement_date=date(2024, 1, 8),
    )
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="titres réglés insuffisants"):
        ledger.execute_batch(
            [request("SPY", -5, "10", decision_date=date(2024, 1, 3))],
            trade_date=date(2024, 1, 4),
            settlement_date=date(2024, 1, 5),
        )
    assert ledger.accounting_snapshot() == before


def test_fixed_quantity_does_not_change_when_open_differs_from_close() -> None:
    quantity = whole_share_quantity("1000", "100")
    assert quantity == 10
    order = FixedOrder("SPY", quantity, DECISION, D("100"))
    ledger = SyntheticPortfolioLedger(D("1200"))
    ledger.set_prices("SPY", market_price="110")
    ledger.execute_batch(
        [ExecutionRequest(order, D("110"))],
        trade_date=TRADE,
        settlement_date=SETTLEMENT,
    )
    assert order.quantity == 10
    assert ledger.economic_positions["SPY"] == 10


def test_open_gap_can_make_fixed_order_unfundable_without_resizing() -> None:
    quantity = whole_share_quantity("1000", "100")
    order = FixedOrder("SPY", quantity, DECISION, D("100"))
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="110")
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="cash réglé insuffisant"):
        ledger.execute_batch(
            [ExecutionRequest(order, D("110"))],
            trade_date=TRADE,
            settlement_date=SETTLEMENT,
        )
    assert order.quantity == 10
    assert ledger.accounting_snapshot() == before


@pytest.mark.parametrize(
    "bad_request, message",
    [
        (request("SPY", 0, "100"), "quantité nulle"),
        (request("SPY", D("1.5"), "100"), "fractionnaires"),
        (request("SPY", 1, "-1"), "strictement positif"),
    ],
)
def test_invalid_order_inputs_are_rejected_atomically(bad_request, message: str) -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100")
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match=message):
        ledger.execute_batch([bad_request], trade_date=TRADE, settlement_date=SETTLEMENT)
    assert ledger.accounting_snapshot() == before


def test_one_invalid_leg_rejects_entire_batch() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100")
    ledger.set_prices("BIL", market_price="50")
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError):
        ledger.execute_batch(
            [request("SPY", 2, "100"), request("BIL", 0, "50")],
            trade_date=TRADE,
            settlement_date=SETTLEMENT,
        )
    assert ledger.accounting_snapshot() == before


def test_conservative_and_h_fin_net_differ_for_same_day_rebalance() -> None:
    def funded_position() -> SyntheticPortfolioLedger:
        account = SyntheticPortfolioLedger(D("100"))
        buy_and_settle(account, "BIL", 10, "10")
        account.set_prices("SPY", market_price="20")
        return account

    batch = [
        request("BIL", -10, "10", decision_date=date(2024, 1, 8)),
        request("SPY", 5, "20", decision_date=date(2024, 1, 8)),
    ]
    conservative = funded_position()
    with pytest.raises(LedgerError, match="cash réglé insuffisant"):
        conservative.execute_batch(
            batch,
            trade_date=date(2024, 1, 9),
            settlement_date=date(2024, 1, 11),
            funding=FundingConvention.CONSERVATIVE,
        )
    assert conservative.economic_positions == {"BIL": 10}

    netted = funded_position()
    before = netted.wealth_market()
    netted.execute_batch(
        batch,
        trade_date=date(2024, 1, 9),
        settlement_date=date(2024, 1, 11),
        funding=FundingConvention.H_FIN_NET,
    )
    assert netted.economic_positions == {"BIL": 0, "SPY": 5}
    assert netted.settled_cash == 0
    assert netted.sale_receivables == netted.purchase_payables == D("100")
    assert netted.wealth_market() == before
    netted.settle_through(date(2024, 1, 11))
    assert netted.settled_positions == {"BIL": 0, "SPY": 5}
    assert netted.wealth_market() == before


def test_h_fin_net_does_not_use_a_sale_that_settles_too_late() -> None:
    ledger = SyntheticPortfolioLedger(D("100"))
    buy_and_settle(ledger, "BIL", 10, "10")
    ledger.set_prices("SPY", market_price="20")
    # A vente settling later cannot finance an earlier purchase obligation.
    ledger.execute_batch(
        [request("BIL", -10, "10", decision_date=date(2024, 1, 8))],
        trade_date=date(2024, 1, 9),
        settlement_date=date(2024, 1, 12),
        funding=FundingConvention.H_FIN_NET,
    )
    before_buy = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="financement net impossible"):
        ledger.execute_batch(
            [request("SPY", 5, "20", decision_date=date(2024, 1, 9))],
            trade_date=date(2024, 1, 10),
            settlement_date=date(2024, 1, 11),
            funding=FundingConvention.H_FIN_NET,
        )
    assert ledger.accounting_snapshot() == before_buy


def test_artificial_calendar_t_plus_two_before_transition() -> None:
    calendar = SyntheticSettlementCalendar(
        [date(2024, 5, 24), date(2024, 5, 28), date(2024, 5, 29)]
    )
    assert calendar.cycle_for(date(2024, 5, 24)) == 2
    assert calendar.settlement_date(date(2024, 5, 24)) == date(2024, 5, 29)


def test_artificial_calendar_t_plus_one_from_transition() -> None:
    calendar = SyntheticSettlementCalendar(
        [date(2024, 5, 28), date(2024, 5, 29), date(2024, 5, 30)]
    )
    assert calendar.cycle_for(date(2024, 5, 28)) == 1
    assert calendar.settlement_date(date(2024, 5, 28)) == date(2024, 5, 29)


def test_artificial_calendar_skips_weekend_and_explicit_holiday() -> None:
    calendar = SyntheticSettlementCalendar(
        [date(2024, 1, 5), date(2024, 1, 9), date(2024, 1, 10)]
    )
    assert calendar.settlement_date(date(2024, 1, 5)) == date(2024, 1, 10)


def test_distribution_creates_claim_then_payment_is_wealth_neutral() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "SPY", 10, "50")
    claim_id = ledger.accrue_distribution(
        "SPY", ex_date=date(2024, 1, 8), payment_date=date(2024, 1, 12), amount_per_share="1.25"
    )
    assert ledger.distribution_claims[0].claim_id == claim_id
    assert ledger.distribution_receivables == D("12.50")
    assert ledger.settled_cash == D("500")
    before_payment = ledger.wealth_market()
    ledger.pay_distributions_through(date(2024, 1, 12))
    assert ledger.distribution_receivables == 0
    assert ledger.settled_cash == D("512.50")
    assert ledger.wealth_market() == before_payment


def test_sale_after_ex_date_does_not_remove_distribution_right() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "SPY", 10, "50")
    ledger.accrue_distribution(
        "SPY", ex_date=date(2024, 1, 8), payment_date=date(2024, 1, 15), amount_per_share="1"
    )
    ledger.execute_batch(
        [request("SPY", -10, "50", decision_date=date(2024, 1, 8))],
        trade_date=date(2024, 1, 9),
        settlement_date=date(2024, 1, 11),
    )
    assert ledger.economic_positions["SPY"] == 0
    assert ledger.distribution_receivables == D("10")


def test_purchase_on_ex_date_gets_no_retroactive_right() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="50")
    ledger.execute_batch(
        [request("SPY", 10, "50", decision_date=date(2024, 1, 7))],
        trade_date=date(2024, 1, 8),
        settlement_date=date(2024, 1, 10),
    )
    ledger.accrue_distribution(
        "SPY", ex_date=date(2024, 1, 8), payment_date=date(2024, 1, 12), amount_per_share="1"
    )
    assert ledger.distribution_claims[-1].entitled_shares == 0
    assert ledger.distribution_receivables == 0


def test_multiple_zero_and_unpaid_distributions_remain_separate() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "BIL", 20, "10")
    ledger.accrue_distribution(
        "BIL", ex_date=date(2024, 1, 8), payment_date=date(2024, 1, 12), amount_per_share="0.25"
    )
    ledger.accrue_distribution(
        "BIL", ex_date=date(2024, 1, 9), payment_date=date(2024, 1, 19), amount_per_share="0.10"
    )
    ledger.accrue_distribution(
        "BIL", ex_date=date(2024, 1, 10), payment_date=date(2024, 1, 19), amount_per_share="0"
    )
    assert ledger.distribution_receivables == D("7.00")
    ledger.pay_distributions_through(date(2024, 1, 12))
    assert ledger.distribution_receivables == D("2.00")
    assert sum(not claim.paid for claim in ledger.distribution_claims) == 2


def test_reverse_split_preserves_value_and_existing_claim() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "BIL", 20, "10")
    ledger.accrue_distribution(
        "BIL", ex_date=date(2024, 1, 8), payment_date=date(2024, 1, 20), amount_per_share="0.50"
    )
    before = ledger.wealth_market()
    claim_before = ledger.distribution_receivables
    ledger.apply_reverse_split(
        "BIL", effective_date=date(2024, 1, 9), old_shares=2, new_shares=1
    )
    assert ledger.economic_positions["BIL"] == 10
    assert ledger.settled_positions["BIL"] == 10
    assert ledger.market_prices["BIL"] == D("20")
    assert ledger.nav_prices["BIL"] == D("20")
    assert ledger.distribution_receivables == claim_before
    assert ledger.wealth_market() == before


def test_reverse_split_cannot_be_applied_twice_and_rejection_is_atomic() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    buy_and_settle(ledger, "BIL", 20, "10")
    kwargs = dict(effective_date=date(2024, 1, 9), old_shares=2, new_shares=1)
    ledger.apply_reverse_split("BIL", **kwargs)
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="déjà été appliqué"):
        ledger.apply_reverse_split("BIL", **kwargs)
    assert ledger.accounting_snapshot() == before


def test_nav_and_market_wealth_are_distinct_but_share_same_accounts() -> None:
    ledger = SyntheticPortfolioLedger(D("1000"))
    ledger.set_prices("SPY", market_price="100", nav_price="98")
    ledger.execute_batch(
        [request("SPY", 5, "100")], trade_date=TRADE, settlement_date=SETTLEMENT
    )
    assert ledger.wealth_market() == D("1000")
    assert ledger.wealth_nav() == D("990")


def test_all_test_inputs_are_synthetic_and_module_needs_no_data_files(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("aucune lecture de fichier ou réseau n'est autorisée")

    monkeypatch.setattr(Path, "read_text", forbidden)
    ledger = SyntheticPortfolioLedger(D("100"))
    ledger.set_prices("SPY", market_price="10")
    ledger.execute_batch(
        [request("SPY", 1, "10")], trade_date=TRADE, settlement_date=SETTLEMENT
    )
    assert ledger.wealth_market() == D("100")


def strict_ledger(
    cash: str = "1000",
    *,
    sessions: list[date] | None = None,
    settlement_days: list[date] | None = None,
    shortened: list[date] | None = None,
) -> SyntheticPortfolioLedger:
    sessions = sessions or [
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
        date(2024, 1, 5),
        date(2024, 1, 8),
        date(2024, 1, 9),
        date(2024, 1, 10),
        date(2024, 1, 11),
        date(2024, 1, 12),
        date(2024, 1, 15),
    ]
    settlement_days = settlement_days or sessions
    return SyntheticPortfolioLedger(
        D(cash),
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(
            sessions, shortened_sessions=shortened or []
        ),
        settlement_calendar=SyntheticSettlementCalendar(settlement_days),
    )


def strict_buy_and_settle(
    ledger: SyntheticPortfolioLedger,
    *,
    symbol: str = "SPY",
    quantity: int = 5,
    price: str = "100",
) -> None:
    ledger.set_prices(
        symbol, market_price=price, nav_price=price, price_date=date(2024, 1, 3)
    )
    ledger.execute_batch(
        [request(symbol, quantity, price)],
        trade_date=date(2024, 1, 3),
    )
    ledger.settle_through(date(2024, 1, 5))


def test_strict_mode_requires_both_distinct_calendars() -> None:
    with pytest.raises(LedgerError, match="de négociation et de règlement"):
        SyntheticPortfolioLedger(D("100"), strict_temporal=True)


def test_strict_settlement_is_derived_and_explicit_mismatch_is_atomic() -> None:
    ledger = strict_ledger()
    ledger.set_prices("SPY", market_price="100", price_date=date(2024, 1, 3))
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="ne correspond pas"):
        ledger.execute_batch(
            [request("SPY", 1, "100")],
            trade_date=date(2024, 1, 3),
            settlement_date=date(2024, 1, 4),
        )
    assert ledger.accounting_snapshot() == before
    ids = ledger.execute_batch(
        [request("SPY", 1, "100")], trade_date=date(2024, 1, 3)
    )
    assert ids == [1]
    assert ledger.pending_settlements[0].settlement_date == date(2024, 1, 5)
    assert ledger.wealth_market() == D("1000")


def test_strict_calendar_transition_t2_and_t1_is_mandatory() -> None:
    sessions = [date(2024, 5, 24), date(2024, 5, 28), date(2024, 5, 29)]
    trading = SyntheticTradingCalendar(sessions)
    settlement = SyntheticSettlementCalendar(sessions)
    before = SyntheticPortfolioLedger(
        D("100"), True, trading, settlement
    )
    before.set_prices("SPY", market_price="10", price_date=date(2024, 5, 24))
    before.execute_batch(
        [request("SPY", 1, "10", decision_date=date(2024, 5, 23))],
        trade_date=date(2024, 5, 24),
    )
    assert before.pending_settlements[0].settlement_date == date(2024, 5, 29)

    after = SyntheticPortfolioLedger(D("100"), True, trading, settlement)
    after.set_prices("SPY", market_price="10", price_date=date(2024, 5, 28))
    after.execute_batch(
        [request("SPY", 1, "10", decision_date=date(2024, 5, 24))],
        trade_date=date(2024, 5, 28),
    )
    assert after.pending_settlements[0].settlement_date == date(2024, 5, 29)


def test_trading_day_may_be_absent_from_settlement_calendar() -> None:
    trade_day = date(2024, 11, 11)
    ledger = strict_ledger(
        sessions=[trade_day, date(2024, 11, 12), date(2024, 11, 13)],
        settlement_days=[date(2024, 11, 12), date(2024, 11, 13)],
    )
    ledger.set_prices("SPY", market_price="10", price_date=trade_day)
    ledger.execute_batch(
        [request("SPY", 1, "10", decision_date=date(2024, 11, 8))],
        trade_date=trade_day,
    )
    assert ledger.pending_settlements[0].settlement_date == date(2024, 11, 12)


def test_shortened_session_remains_a_valid_trade_date() -> None:
    shortened = date(2024, 11, 29)
    ledger = strict_ledger(
        sessions=[shortened, date(2024, 12, 2)],
        settlement_days=[shortened, date(2024, 12, 2)],
        shortened=[shortened],
    )
    ledger.set_prices("SPY", market_price="10", price_date=shortened)
    ledger.execute_batch(
        [request("SPY", 1, "10", decision_date=date(2024, 11, 28))],
        trade_date=shortened,
    )
    assert ledger.trading_calendar is not None
    assert ledger.trading_calendar.is_shortened(shortened)


def test_incomplete_and_incoherent_calendars_are_rejected() -> None:
    with pytest.raises(LedgerError, match="week-end"):
        SyntheticSettlementCalendar([date(2024, 1, 6)])
    calendar = SyntheticSettlementCalendar([date(2024, 1, 3)])
    with pytest.raises(LedgerError, match="insuffisant"):
        calendar.settlement_date(date(2024, 1, 3))
    with pytest.raises(LedgerError, match="écourtée"):
        SyntheticTradingCalendar(
            [date(2024, 1, 3)], shortened_sessions=[date(2024, 1, 4)]
        )


def test_strict_backdated_transaction_and_price_are_rejected_atomically() -> None:
    ledger = strict_ledger()
    strict_buy_and_settle(ledger)
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="antidaté"):
        ledger.set_prices("SPY", market_price="101", price_date=date(2024, 1, 4))
    assert ledger.accounting_snapshot() == before
    assert ledger.market_prices["SPY"] == D("100")


def test_future_announcement_has_no_accounting_effect_until_ex_date() -> None:
    ledger = strict_ledger()
    strict_buy_and_settle(ledger)
    before = ledger.accounting_snapshot()
    announcement_id = ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2024, 1, 5),
        ex_date=date(2024, 1, 8),
        payment_date=date(2024, 1, 12),
        amount_per_share="1",
    )
    assert ledger.accounting_snapshot() == before
    claim_id = ledger.accrue_announced_distribution(
        announcement_id, event_date=date(2024, 1, 8)
    )
    assert claim_id == 1
    assert ledger.distribution_receivables == D("5")
    assert ledger.wealth_market() == D("1005")


def test_future_knowledge_date_advances_chronology_without_financial_effect() -> None:
    ledger = strict_ledger()
    strict_buy_and_settle(ledger)
    before = ledger.accounting_snapshot()
    ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2024, 1, 8),
        ex_date=date(2024, 1, 12),
        payment_date=date(2024, 1, 15),
        amount_per_share="1",
    )
    assert ledger.accounting_snapshot() == before
    with pytest.raises(LedgerError, match="antidaté"):
        ledger.set_prices("SPY", market_price="101", price_date=date(2024, 1, 5))
    assert ledger.market_prices["SPY"] == D("100")


def test_distribution_declared_after_ex_date_is_rejected() -> None:
    ledger = strict_ledger()
    strict_buy_and_settle(ledger)
    ledger.set_prices("SPY", market_price="100", price_date=date(2024, 1, 8))
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="après son ex-date"):
        ledger.announce_distribution(
            "SPY",
            knowledge_date=date(2024, 1, 8),
            ex_date=date(2024, 1, 5),
            payment_date=date(2024, 1, 12),
            amount_per_share="1",
        )
    assert ledger.accounting_snapshot() == before


def test_payment_before_entitlement_and_double_payment_are_rejected() -> None:
    ledger = strict_ledger()
    strict_buy_and_settle(ledger)
    announcement_id = ledger.announce_distribution(
        "SPY",
        knowledge_date=date(2024, 1, 5),
        ex_date=date(2024, 1, 8),
        payment_date=date(2024, 1, 12),
        amount_per_share="1",
    )
    with pytest.raises(LedgerError, match="aucune distribution exigible"):
        ledger.pay_distributions_through(date(2024, 1, 5))
    ledger.accrue_announced_distribution(announcement_id, event_date=date(2024, 1, 8))
    before_payment = ledger.wealth_market()
    ledger.pay_distributions_through(date(2024, 1, 12))
    assert ledger.wealth_market() == before_payment
    settled_cash = ledger.settled_cash
    with pytest.raises(LedgerError, match="aucune distribution exigible"):
        ledger.pay_distributions_through(date(2024, 1, 12))
    assert ledger.settled_cash == settled_cash


def test_premature_and_double_settlement_are_rejected() -> None:
    ledger = strict_ledger()
    ledger.set_prices("SPY", market_price="100", price_date=date(2024, 1, 3))
    ledger.execute_batch([request("SPY", 1, "100")], trade_date=date(2024, 1, 3))
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="prématuré"):
        ledger.settle_through(date(2024, 1, 4))
    assert ledger.accounting_snapshot() == before
    ledger.settle_through(date(2024, 1, 5))
    after = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="aucun règlement exigible"):
        ledger.settle_through(date(2024, 1, 5))
    assert ledger.accounting_snapshot() == after


def test_same_day_order_protects_entitlement_and_cash_availability() -> None:
    ledger = strict_ledger("100")
    strict_buy_and_settle(ledger, symbol="BIL", quantity=10, price="10")
    announcement_id = ledger.announce_distribution(
        "BIL",
        knowledge_date=date(2024, 1, 5),
        ex_date=date(2024, 1, 8),
        payment_date=date(2024, 1, 8),
        amount_per_share="1",
    )
    ledger.accrue_announced_distribution(announcement_id, event_date=date(2024, 1, 8))
    ledger.pay_distributions_through(date(2024, 1, 8))
    ledger.set_prices("SPY", market_price="10", price_date=date(2024, 1, 8))
    ledger.execute_batch(
        [request("SPY", 1, "10", decision_date=date(2024, 1, 5))],
        trade_date=date(2024, 1, 8),
    )
    assert ledger.economic_positions == {"BIL": 10, "SPY": 1}
    assert ledger.settled_cash == D("10")
    assert ledger.purchase_payables == D("10")
    assert ledger.distribution_receivables == 0
    assert ledger.wealth_market() == D("110")
    with pytest.raises(LedgerError, match="ordre intrajournalier"):
        ledger.announce_distribution(
            "BIL",
            knowledge_date=date(2024, 1, 8),
            ex_date=date(2024, 1, 8),
            payment_date=date(2024, 1, 12),
            amount_per_share="1",
        )


def test_same_day_split_precedes_distribution_entitlement() -> None:
    ledger = strict_ledger("100")
    strict_buy_and_settle(ledger, symbol="BIL", quantity=10, price="10")
    announcement_id = ledger.announce_distribution(
        "BIL",
        knowledge_date=date(2024, 1, 5),
        ex_date=date(2024, 1, 8),
        payment_date=date(2024, 1, 12),
        amount_per_share="1",
    )
    before = ledger.wealth_market()
    ledger.apply_reverse_split(
        "BIL", effective_date=date(2024, 1, 8), old_shares=2, new_shares=1
    )
    assert ledger.wealth_market() == before
    ledger.accrue_announced_distribution(announcement_id, event_date=date(2024, 1, 8))
    assert ledger.distribution_claims[-1].entitled_shares == 5
    assert ledger.distribution_receivables == D("5")


def test_multiple_settlements_and_h_fin_net_preserve_wealth() -> None:
    ledger = strict_ledger("200")
    ledger.set_prices("BIL", market_price="10", price_date=date(2024, 1, 3))
    ledger.execute_batch([request("BIL", 10, "10")], trade_date=date(2024, 1, 3))
    ledger.settle_through(date(2024, 1, 5))
    ledger.set_prices("BIL", market_price="10", price_date=date(2024, 1, 8))
    ledger.set_prices("SPY", market_price="20", price_date=date(2024, 1, 8))
    before = ledger.wealth_market()
    ledger.execute_batch(
        [
            request("BIL", -10, "10", decision_date=date(2024, 1, 5)),
            request("SPY", 5, "20", decision_date=date(2024, 1, 5)),
        ],
        trade_date=date(2024, 1, 8),
        funding=FundingConvention.H_FIN_NET,
    )
    assert ledger.sale_receivables == ledger.purchase_payables == D("100")
    assert ledger.wealth_market() == before
    ledger.settle_through(date(2024, 1, 10))
    assert ledger.settled_cash == D("100")
    assert ledger.wealth_market() == before


def test_strict_rejection_of_oversale_is_atomic() -> None:
    ledger = strict_ledger("100")
    ledger.set_prices("SPY", market_price="10", price_date=date(2024, 1, 3))
    ledger.execute_batch([request("SPY", 5, "10")], trade_date=date(2024, 1, 3))
    ledger.set_prices("SPY", market_price="10", price_date=date(2024, 1, 4))
    before = ledger.accounting_snapshot()
    with pytest.raises(LedgerError, match="vente supérieure"):
        ledger.execute_batch(
            [request("SPY", -6, "10", decision_date=date(2024, 1, 3))],
            trade_date=date(2024, 1, 4),
        )
    assert ledger.accounting_snapshot() == before
    assert ledger.economic_positions == {"SPY": 5}
    assert len(ledger.pending_settlements) == 1
