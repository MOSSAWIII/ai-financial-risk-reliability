#!/usr/bin/env python3
"""Exécute l'unique comparaison historique exploratoire C1–C2 préspécifiée."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from analyze_c2_conditional_protocol import build_conditional_rows
from build_c2_documentary_grid import DTC_NO_SETTLEMENT, build_rows
from exploratory_buy_hold_spy_bil import (
    CostScenario,
    DistributionEvent,
    EpisodeContract,
    EpisodeData,
    _economic_wealth,
    _load_json_decimal,
    _yahoo_prices,
    load_contract,
    prepare_episode_data,
)
from synthetic_decision_adapter import (
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
    intent_content_sha256,
    intent_payload,
)
from synthetic_portfolio_ledger import (
    SyntheticPortfolioLedger,
    SyntheticSettlementCalendar,
    SyntheticTradingCalendar,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "RL" / "tests" / "fixtures" / "exploratory_buy_hold_spy_bil_v1.json"
STRICT_GRID_PATH = ROOT / "RL" / "docs" / "grille_documentaire_c2_2024_2025.csv"
CONDITIONAL_GRID_PATH = ROOT / "RL" / "docs" / "grille_conditionnelle_c2_2024_2025.csv"
DEFAULT_OUTPUT_DIR = ROOT / "RL" / "results" / "historical_c1_c2_2024_2025"
CONTRACT_COMMIT = "8e9a0164d95ec19d2eace74f65506cdde6c891df"
PROTOCOL_MODE = ProtocolMode.EXPLORATORY_CONDITIONAL
SYMBOLS = ("SPY", "BIL")
ZERO = Decimal("0")
HALF = Decimal("0.5")
ET = ZoneInfo("America/New_York")
OUTPUT_NAMES = {
    "trajectories": "trajectoires_quotidiennes.csv",
    "decisions": "journal_decisions_c2.csv",
    "summaries": "synthese_financiere.csv",
    "comparisons": "comparaison_appariee.csv",
}
FIGURE_NAME = "trajectoire_et_drawdown_s0_d1.svg"


class ComparisonError(RuntimeError):
    """Violation d'une convention verrouillée ou d'un invariant historique."""


@dataclass(frozen=True)
class CellDefinition:
    cell_id: str
    scenario: CostScenario
    cash_convention: CashAvailabilityConvention


@dataclass(frozen=True)
class RunResult:
    cell: CellDefinition
    policy_id: str
    summary: Mapping[str, Any]
    trajectories: tuple[Mapping[str, Any], ...]
    decisions: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class ExperimentResult:
    runs: tuple[RunResult, ...]
    comparisons: tuple[Mapping[str, Any], ...]
    source_hashes: Mapping[str, str]
    source_fingerprint: str
    strict_grid_sha256: str
    conditional_grid_sha256: str


def decimal_text(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    return format(value.normalize(), "f")


def float_text(value: float) -> str:
    return format(value, ".12f")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _date_range(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _validate_locked_inputs(
    contract: EpisodeContract, data: EpisodeData
) -> tuple[list[dict[str, str]], str, str]:
    if (
        contract.decision_date != date(2024, 5, 28)
        or contract.execution_date != date(2024, 5, 29)
        or contract.anniversary_date != date(2025, 5, 29)
        or contract.initial_cash != Decimal("100000")
    ):
        raise ComparisonError("périmètre historique verrouillé modifié")
    c1 = [item for item in contract.policies if item.policy_id == "C1"]
    if len(c1) != 1 or c1[0].target_weight_spy != HALF:
        raise ComparisonError("définition C1 verrouillée absente")
    if [(item.scenario_id, item.basis_points) for item in contract.cost_scenarios] != [
        ("S0", ZERO),
        ("S1", Decimal("1")),
        ("S2", Decimal("5")),
        ("S3", Decimal("10")),
    ]:
        raise ComparisonError("scénarios de coûts verrouillés modifiés")
    if len(data.common_sessions) != 251 or data.terminal_date != date(2025, 5, 29):
        raise ComparisonError("couverture historique commune modifiée")
    if len(data.distributions) != 16:
        raise ComparisonError("inventaire des 16 distributions modifié")

    strict_rows = _read_csv(STRICT_GRID_PATH)
    conditional_rows = _read_csv(CONDITIONAL_GRID_PATH)
    rebuilt_strict, _ = build_rows(ROOT)
    rebuilt_conditional, _ = build_conditional_rows(ROOT)
    if strict_rows != rebuilt_strict:
        raise ComparisonError("grille documentaire non reproductible")
    if conditional_rows != rebuilt_conditional:
        raise ComparisonError("grille conditionnelle non reproductible")
    if len(strict_rows) != 52 or len(conditional_rows) != 52:
        raise ComparisonError("la grille ne contient pas 52 décisions")
    if any(row["settlement_status"] != "VERIFIED" for row in strict_rows):
        raise ComparisonError("règlement non vérifié dans la grille")
    if any(row["option_b_status"] != "CONDITIONALLY_DOCUMENTED" for row in conditional_rows):
        raise ComparisonError("une décision E-B n'est pas documentée")
    if [row["cycle"] for row in strict_rows] != [row["cycle"] for row in conditional_rows]:
        raise ComparisonError("grilles stricte et E-B désalignées")
    return strict_rows, sha256_file(STRICT_GRID_PATH), sha256_file(CONDITIONAL_GRID_PATH)


def _cells(contract: EpisodeContract) -> tuple[CellDefinition, ...]:
    cells = []
    for suffix, convention in (
        ("D1", CashAvailabilityConvention.D_PLUS_1),
        ("D2", CashAvailabilityConvention.D_PLUS_2),
    ):
        for scenario in contract.cost_scenarios:
            cells.append(CellDefinition(f"{scenario.scenario_id}-{suffix}", scenario, convention))
    return tuple(cells)


def _settlement_business_dates(contract: EpisodeContract) -> tuple[date, ...]:
    end = contract.anniversary_date + timedelta(days=7)
    return tuple(
        current
        for current in _date_range(contract.execution_date, end)
        if current.weekday() < 5 and current not in DTC_NO_SETTLEMENT
    )


def _new_ledger(
    contract: EpisodeContract, data: EpisodeData
) -> tuple[SyntheticPortfolioLedger, SyntheticDecisionAdapter]:
    ledger = SyntheticPortfolioLedger(
        contract.initial_cash,
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(
            (contract.decision_date, *data.common_sessions)
        ),
        settlement_calendar=SyntheticSettlementCalendar(
            _settlement_business_dates(contract)
        ),
    )
    return ledger, SyntheticDecisionAdapter(ledger)


def _initialize_50_50(
    contract: EpisodeContract,
    data: EpisodeData,
    adapter: SyntheticDecisionAdapter,
    scenario: CostScenario,
) -> tuple[Mapping[str, int], Decimal, Decimal, Mapping[str, Decimal]]:
    intent = adapter.prepare_intent(
        decision_date=contract.decision_date,
        known_market_wealth=contract.initial_cash,
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes={
            symbol: DatedPrice(contract.decision_date, data.decision_closes[symbol])
            for symbol in SYMBOLS
        },
        target_weight_spy=HALF,
    )
    opens = dict(data.execution_opens)
    fees = cost_scenario_fees(intent, opens, scenario.basis_points)
    outcome = adapter.process_intent(
        intent,
        execution_date=contract.execution_date,
        execution_opens={
            symbol: DatedPrice(contract.execution_date, opens[symbol])
            for symbol in SYMBOLS
        },
        fees=fees,
    )
    if outcome.status is not ExecutionStatus.EXECUTED_HYPOTHETICAL:
        raise ComparisonError(
            f"{scenario.scenario_id}: achat initial 50/50 non exécuté: {outcome.reason}"
        )
    quantities = dict(intent.target_quantities)
    if quantities != {"SPY": 94, "BIL": 544}:
        raise ComparisonError("quantités initiales C1/C2 différentes de la référence")
    gross = sum(opens[symbol] * quantities[symbol] for symbol in SYMBOLS)
    return quantities, sum(fees.values(), ZERO), gross, fees


def _admissible_cash(
    ledger: SyntheticPortfolioLedger,
    as_of: date,
    convention: CashAvailabilityConvention,
) -> Decimal:
    delay = 1 if convention is CashAvailabilityConvention.D_PLUS_1 else 2
    calendar = ledger.settlement_calendar
    assert calendar is not None
    unavailable = sum(
        (
            claim.amount
            for claim in ledger.distribution_claims
            if claim.paid
            and calendar.business_date_after(claim.payment_date, delay) > as_of
        ),
        ZERO,
    )
    return ledger.settled_cash - unavailable


def _trajectory_record(
    *,
    cell: CellDefinition,
    policy_id: str,
    current: date,
    ledger: SyntheticPortfolioLedger,
    prices: Mapping[str, Decimal],
    initial_wealth: Decimal,
    source_fingerprint: str,
) -> Mapping[str, Any]:
    wealth = _economic_wealth(ledger, prices)
    if wealth <= ZERO:
        raise ComparisonError("richesse économique quotidienne non positive")
    spy_value = prices["SPY"] * ledger.economic_positions.get("SPY", 0)
    bil_value = prices["BIL"] * ledger.economic_positions.get("BIL", 0)
    admissible_cash = _admissible_cash(ledger, current, cell.cash_convention)
    reconstructed = (
        spy_value
        + bil_value
        + ledger.settled_cash
        + ledger.distribution_receivables
        + ledger.sale_receivables
        - ledger.purchase_payables
    )
    if reconstructed != wealth:
        raise ComparisonError("identité comptable quotidienne divergente")
    return {
        "episode_id": "spy-bil-c1-c2-2024-05-29-to-2025-05-29",
        "cell_id": cell.cell_id,
        "policy_id": policy_id,
        "cost_scenario": cell.scenario.scenario_id,
        "cost_bps": decimal_text(cell.scenario.basis_points),
        "cash_convention": cell.cash_convention.value,
        "protocol_mode": PROTOCOL_MODE.value,
        "valuation_date": current.isoformat(),
        "spy_close_usd": decimal_text(prices["SPY"]),
        "bil_close_usd": decimal_text(prices["BIL"]),
        "spy_quantity": ledger.economic_positions.get("SPY", 0),
        "bil_quantity": ledger.economic_positions.get("BIL", 0),
        "settled_spy_quantity": ledger.settled_positions.get("SPY", 0),
        "settled_bil_quantity": ledger.settled_positions.get("BIL", 0),
        "spy_value_usd": decimal_text(spy_value),
        "bil_value_usd": decimal_text(bil_value),
        "economic_wealth_usd": decimal_text(wealth),
        "settled_cash_usd": decimal_text(ledger.settled_cash),
        "admissible_cash_usd": decimal_text(admissible_cash),
        "financing_cash_usd": decimal_text(
            max(ZERO, admissible_cash - ledger.purchase_payables)
        ),
        "distribution_receivables_usd": decimal_text(
            ledger.distribution_receivables
        ),
        "sale_receivables_usd": decimal_text(ledger.sale_receivables),
        "purchase_payables_usd": decimal_text(ledger.purchase_payables),
        "cumulative_fees_usd": decimal_text(ledger.fees_recognized),
        "spy_exposure": decimal_text(spy_value / wealth),
        "bil_exposure": decimal_text(bil_value / wealth),
        "cash_exposure": decimal_text(ledger.settled_cash / wealth),
        "wealth_identity_difference_usd": decimal_text(reconstructed - wealth),
        "initial_wealth_usd": decimal_text(initial_wealth),
        "contract_commit": CONTRACT_COMMIT,
        "source_fingerprint": source_fingerprint,
    }


def _path_metrics(
    base_wealth: Decimal,
    trajectory: Sequence[Mapping[str, Any]],
    *,
    initial_wealth: Decimal,
    elapsed_days: int,
) -> Mapping[str, Any]:
    wealth = [float(base_wealth)] + [
        float(Decimal(str(row["economic_wealth_usd"]))) for row in trajectory
    ]
    returns = [wealth[index] / wealth[index - 1] - 1 for index in range(1, len(wealth))]
    peak = wealth[0]
    maximum_drawdown = 0.0
    current_duration = 0
    maximum_duration = 0
    for value in wealth[1:]:
        if value >= peak:
            peak = value
            current_duration = 0
        else:
            current_duration += 1
            maximum_duration = max(maximum_duration, current_duration)
            maximum_drawdown = min(maximum_drawdown, value / peak - 1)
    terminal = Decimal(str(trajectory[-1]["economic_wealth_usd"]))
    total_return = float(terminal / initial_wealth - 1)
    annualized_return = float(
        (terminal / initial_wealth)
        ** (Decimal("365.2425") / Decimal(elapsed_days))
        - 1
    )
    return {
        "terminal_wealth": terminal,
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": statistics.stdev(returns) * math.sqrt(252),
        "maximum_drawdown": maximum_drawdown,
        "maximum_drawdown_duration_sessions": maximum_duration,
        "worst_daily_return": min(returns),
    }


def _provenance(data: EpisodeData) -> Mapping[str, str]:
    return {
        "SPY_close": f"{data.sources['SPY'].record['id']}:{data.sources['SPY'].sha256}",
        "BIL_close": f"{data.sources['BIL'].record['id']}:{data.sources['BIL'].sha256}",
        "trading_calendar": f"{data.sources['trading_calendar'].record['id']}:{data.sources['trading_calendar'].sha256}",
        "settlement_calendar": "DTC-19404-23|DTC-20972-24",
        "economic_positions": "SYNTHETIC_PORTFOLIO_LEDGER",
        "settled_positions": "SYNTHETIC_PORTFOLIO_LEDGER",
        "settled_cash": "SYNTHETIC_PORTFOLIO_LEDGER",
        "pending_settlements": "SYNTHETIC_PORTFOLIO_LEDGER",
        "distribution_claims": f"{data.sources['distributions'].record['id']}:{data.sources['distributions'].sha256}",
    }


def _decision_record(
    *,
    cell: CellDefinition,
    grid_row: Mapping[str, str],
    snapshot: Any,
    intent: Any,
    outcome: Any,
    opens: Mapping[str, Decimal],
    fees: Mapping[str, Decimal],
    transmitted_positions: Mapping[str, int],
    source_fingerprint: str,
) -> Mapping[str, Any]:
    forbidden = {
        "economic_distribution_receivables",
        "economic_wealth",
        "excluded_distribution_claims",
        "unavailable_paid_cash",
    }
    snapshot_data = decision_snapshot_payload(snapshot)
    intention_data = intent_payload(intent)
    if forbidden.intersection(snapshot_data) or forbidden.intersection(intention_data):
        raise ComparisonError("montant rétrospectif présent dans une trace décisionnelle")
    orders = [
        {
            "symbol": order.symbol,
            "quantity": order.quantity,
            "decision_date": order.decision_date.isoformat(),
            "decision_price": decimal_text(order.decision_price),
        }
        for order in intent.orders
    ]
    return {
        "episode_id": "spy-bil-c1-c2-2024-05-29-to-2025-05-29",
        "cell_id": cell.cell_id,
        "cost_scenario": cell.scenario.scenario_id,
        "cost_bps": decimal_text(cell.scenario.basis_points),
        "cash_convention": cell.cash_convention.value,
        "protocol_mode": PROTOCOL_MODE.value,
        "cycle": grid_row["cycle"],
        "decision_at": snapshot.decision_at.isoformat(),
        "close_reference": snapshot.price_date.isoformat(),
        "decision_closes": canonical_json(
            {key: decimal_text(value) for key, value in snapshot.decision_closes.items()}
        ),
        "decision_budget_usd": decimal_text(snapshot.decision_budget),
        "admissible_cash_usd": decimal_text(snapshot.settled_cash),
        "financing_cash_usd": decimal_text(snapshot.financing_cash),
        "known_distribution_receivables_usd": decimal_text(
            snapshot.known_distribution_receivables
        ),
        "excluded_claim_ids": canonical_json(snapshot.excluded_distribution_claim_ids),
        "embedded_ex_date_claim_ids": canonical_json(
            snapshot.embedded_ex_date_claim_ids
        ),
        "inherited_positions": canonical_json(dict(intent.inherited_positions)),
        "target_quantities": canonical_json(dict(intent.target_quantities)),
        "sealed_orders": canonical_json(orders),
        "snapshot_id": snapshot.snapshot_id,
        "snapshot_content_sha256": decision_snapshot_content_sha256(snapshot),
        "intent_id": intent.intent_id,
        "intent_content_sha256": intent_content_sha256(intent),
        "snapshot_status": snapshot.status.value,
        "execution_status": outcome.status.value,
        "execution_opens": canonical_json(
            {key: decimal_text(value) for key, value in opens.items()}
        ),
        "fees_usd": canonical_json(
            {key: decimal_text(value) for key, value in fees.items()}
        ),
        "execution_reason": outcome.reason,
        "settlement_date": (
            "" if outcome.settlement_date is None else outcome.settlement_date.isoformat()
        ),
        "funding_source": outcome.funding_source.value,
        "transmitted_positions": canonical_json(dict(transmitted_positions)),
        "contract_commit": CONTRACT_COMMIT,
        "source_fingerprint": source_fingerprint,
    }


def _run_policy(
    *,
    contract: EpisodeContract,
    data: EpisodeData,
    prices: Mapping[str, Mapping[date, Mapping[str, Decimal]]],
    grid_rows: Sequence[Mapping[str, str]],
    cell: CellDefinition,
    policy_id: str,
    source_fingerprint: str,
    source_manifest: str,
) -> RunResult:
    ledger, adapter = _new_ledger(contract, data)
    initial_quantities, initial_cost, initial_notional, _ = _initialize_50_50(
        contract, data, adapter, cell.scenario
    )
    base_wealth = _economic_wealth(ledger, data.execution_opens)
    if base_wealth != contract.initial_cash - initial_cost:
        raise ComparisonError("richesse d'entrée incohérente avec les frais initiaux")

    ex_events: dict[date, list[DistributionEvent]] = {}
    payment_dates: set[date] = set()
    for event in data.distributions:
        ex_events.setdefault(event.ex_date, []).append(event)
        payment_dates.add(event.payment_date)
    grid_by_date = {date.fromisoformat(row["open_candidate"]): row for row in grid_rows}
    decision_rows: list[Mapping[str, Any]] = []
    trajectory_rows: list[Mapping[str, Any]] = []
    target_gaps: list[Decimal] = []
    executed_rebalance_notional = ZERO
    rebalancing_fees = ZERO
    executed_buy_orders = 0
    executed_sell_orders = 0
    rejected_order_count = 0

    for current in _date_range(contract.execution_date, data.terminal_date):
        if current != contract.execution_date:
            for event in ex_events.get(current, []):
                ledger.accrue_realized_distribution(
                    event.symbol,
                    event_id=event.event_id,
                    ex_date=event.ex_date,
                    payment_date=event.payment_date,
                    amount_per_share=event.amount_per_share,
                )
            if any(item.settlement_date == current for item in ledger.pending_settlements):
                ledger.settle_through(current)
            if current in payment_dates:
                ledger.pay_distributions_through(current)

            if policy_id == "C2" and current in grid_by_date:
                grid_row = grid_by_date[current]
                decision_at = datetime.fromisoformat(grid_row["decision_at"])
                price_date = date.fromisoformat(grid_row["close_reference"])
                snapshot = adapter.build_conditional_decision_snapshot(
                    decision_at=decision_at,
                    decision_closes={
                        symbol: DatedPrice(
                            price_date,
                            prices[symbol][price_date]["close"],
                            PriceStatus.AVAILABLE,
                        )
                        for symbol in SYMBOLS
                    },
                    close_available_at={
                        symbol: datetime.combine(price_date, time(16), ET)
                        for symbol in SYMBOLS
                    },
                    provenance=_provenance(data),
                    protocol_mode=PROTOCOL_MODE,
                    cash_availability_convention=cell.cash_convention,
                )
                if snapshot.status is not SnapshotStatus.READY:
                    raise ComparisonError(
                        f"{cell.cell_id}/{current}: NOT_EVALUABLE: {snapshot.reason}"
                    )
                audit = adapter.build_economic_audit_state(snapshot)
                if audit.ledger_sequence != snapshot.ledger_sequence:
                    raise ComparisonError("versions audit et décision désalignées")
                intent = adapter.prepare_intent_from_snapshot(
                    snapshot, target_weight_spy=HALF
                )
                sealed_quantities = dict(intent.target_quantities)
                opens = {
                    symbol: prices[symbol][current]["open"] for symbol in SYMBOLS
                }
                fees = cost_scenario_fees(intent, opens, cell.scenario.basis_points)
                outcome = adapter.process_intent(
                    intent,
                    execution_date=current,
                    execution_opens={
                        symbol: DatedPrice(current, opens[symbol]) for symbol in SYMBOLS
                    },
                    fees=fees,
                )
                if dict(intent.target_quantities) != sealed_quantities:
                    raise ComparisonError("quantités modifiées après lecture des opens")
                if outcome.status not in {
                    ExecutionStatus.EXECUTED_HYPOTHETICAL,
                    ExecutionStatus.VOLUNTARY_HOLD,
                    ExecutionStatus.ECONOMIC_ORDER_REJECTED,
                }:
                    raise ComparisonError(
                        f"{cell.cell_id}/{current}: {outcome.status.value}: {outcome.reason}"
                    )
                if outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL:
                    executed_rebalance_notional += sum(
                        abs(order.quantity) * opens[order.symbol]
                        for order in intent.orders
                    )
                    rebalancing_fees += sum(fees.values(), ZERO)
                    executed_buy_orders += sum(order.quantity > 0 for order in intent.orders)
                    executed_sell_orders += sum(order.quantity < 0 for order in intent.orders)
                elif outcome.status is ExecutionStatus.ECONOMIC_ORDER_REJECTED:
                    rejected_order_count += len(intent.orders)
                    if outcome.accounting_before != outcome.accounting_after:
                        raise ComparisonError("un rejet a modifié l'état comptable")
                target_gaps.append(
                    abs(
                        snapshot.economic_positions["SPY"]
                        * snapshot.decision_closes["SPY"]
                        / snapshot.decision_budget
                        - HALF
                    )
                )
                decision_rows.append(
                    _decision_record(
                        cell=cell,
                        grid_row=grid_row,
                        snapshot=snapshot,
                        intent=intent,
                        outcome=outcome,
                        opens=opens,
                        fees=fees,
                        transmitted_positions={
                            symbol: ledger.economic_positions.get(symbol, 0)
                            for symbol in SYMBOLS
                        },
                        source_fingerprint=source_fingerprint,
                    )
                )

        if current in data.closing_prices:
            ledger.assert_invariants()
            trajectory_rows.append(
                _trajectory_record(
                    cell=cell,
                    policy_id=policy_id,
                    current=current,
                    ledger=ledger,
                    prices=data.closing_prices[current],
                    initial_wealth=contract.initial_cash,
                    source_fingerprint=source_fingerprint,
                )
            )

    if len(trajectory_rows) != 251:
        raise ComparisonError("trajectoire quotidienne incomplète")
    if policy_id == "C2" and len(decision_rows) != 52:
        raise ComparisonError("journal C2 incomplet")
    if ledger.pending_settlements or ledger.distribution_receivables != ZERO:
        raise ComparisonError("flux non dénoué au terminal")
    ledger.assert_invariants()

    metrics = _path_metrics(
        base_wealth,
        trajectory_rows,
        initial_wealth=contract.initial_cash,
        elapsed_days=(data.terminal_date - contract.execution_date).days,
    )
    terminal_prices = data.closing_prices[data.terminal_date]
    terminal_share_value = sum(
        terminal_prices[symbol] * ledger.economic_positions.get(symbol, 0)
        for symbol in SYMBOLS
    )
    distributions_acquired = sum(
        (claim.amount for claim in ledger.distribution_claims), ZERO
    )
    distributions_paid = sum(
        (claim.amount for claim in ledger.distribution_claims if claim.paid), ZERO
    )
    terminal_reconstruction = (
        terminal_share_value
        + ledger.settled_cash
        + ledger.distribution_receivables
        + ledger.sale_receivables
        - ledger.purchase_payables
    )
    if terminal_reconstruction != metrics["terminal_wealth"]:
        raise ComparisonError("réconciliation terminale indépendante divergente")
    statuses = Counter(row["execution_status"] for row in decision_rows)
    rejection_reasons = Counter(
        row["execution_reason"]
        for row in decision_rows
        if row["execution_status"] == ExecutionStatus.ECONOMIC_ORDER_REJECTED.value
    )
    mean_spy = sum(
        (Decimal(str(row["spy_exposure"])) for row in trajectory_rows), ZERO
    ) / Decimal(len(trajectory_rows))
    mean_bil = sum(
        (Decimal(str(row["bil_exposure"])) for row in trajectory_rows), ZERO
    ) / Decimal(len(trajectory_rows))
    terminal_wealth = metrics["terminal_wealth"]
    summary = {
        "episode_id": "spy-bil-c1-c2-2024-05-29-to-2025-05-29",
        "cell_id": cell.cell_id,
        "policy_id": policy_id,
        "cost_scenario": cell.scenario.scenario_id,
        "cost_bps": decimal_text(cell.scenario.basis_points),
        "cash_convention": cell.cash_convention.value,
        "protocol_mode": PROTOCOL_MODE.value,
        "run_status": "COMPLETE",
        "initial_wealth_usd": decimal_text(contract.initial_cash),
        "terminal_wealth_usd": decimal_text(terminal_wealth),
        "total_return": float_text(metrics["total_return"]),
        "annualized_return": float_text(metrics["annualized_return"]),
        "annualized_volatility": float_text(metrics["annualized_volatility"]),
        "maximum_drawdown": float_text(metrics["maximum_drawdown"]),
        "maximum_drawdown_duration_sessions": metrics[
            "maximum_drawdown_duration_sessions"
        ],
        "worst_daily_return": float_text(metrics["worst_daily_return"]),
        "terminal_cash_usd": decimal_text(ledger.settled_cash),
        "distributions_accrued_usd": decimal_text(distributions_acquired),
        "distributions_paid_usd": decimal_text(distributions_paid),
        "cumulative_fees_usd": decimal_text(ledger.fees_recognized),
        "initial_fees_usd": decimal_text(initial_cost),
        "rebalancing_fees_usd": decimal_text(rebalancing_fees),
        "terminal_share_value_usd": decimal_text(terminal_share_value),
        "terminal_spy_quantity": ledger.economic_positions.get("SPY", 0),
        "terminal_bil_quantity": ledger.economic_positions.get("BIL", 0),
        "terminal_spy_exposure": decimal_text(
            terminal_prices["SPY"]
            * ledger.economic_positions.get("SPY", 0)
            / terminal_wealth
        ),
        "terminal_bil_exposure": decimal_text(
            terminal_prices["BIL"]
            * ledger.economic_positions.get("BIL", 0)
            / terminal_wealth
        ),
        "terminal_cash_exposure": decimal_text(ledger.settled_cash / terminal_wealth),
        "mean_spy_exposure": decimal_text(mean_spy),
        "mean_bil_exposure": decimal_text(mean_bil),
        "candidate_decisions": len(decision_rows),
        "evaluable_intents": len(decision_rows),
        "executed_rebalances": statuses[ExecutionStatus.EXECUTED_HYPOTHETICAL.value],
        "voluntary_holds": statuses[ExecutionStatus.VOLUNTARY_HOLD.value],
        "rejected_batches": statuses[ExecutionStatus.ECONOMIC_ORDER_REJECTED.value],
        "rejected_order_count": rejected_order_count,
        "rejection_reasons": canonical_json(dict(sorted(rejection_reasons.items()))),
        "executed_buy_orders": executed_buy_orders,
        "executed_sell_orders": executed_sell_orders,
        "initial_gross_notional_usd": decimal_text(initial_notional),
        "rebalancing_gross_notional_usd": decimal_text(
            executed_rebalance_notional
        ),
        "gross_traded_notional_usd": decimal_text(
            initial_notional + executed_rebalance_notional
        ),
        "mean_predecision_target_gap": (
            ""
            if not target_gaps
            else decimal_text(sum(target_gaps, ZERO) / Decimal(len(target_gaps)))
        ),
        "distribution_event_count": len(ledger.distribution_claims),
        "terminal_reconciliation_usd": decimal_text(terminal_reconstruction),
        "terminal_reconciliation_difference_usd": decimal_text(
            terminal_reconstruction - terminal_wealth
        ),
        "initial_quantities": canonical_json(initial_quantities),
        "contract_commit": CONTRACT_COMMIT,
        "config_sha256": contract.config_sha256,
        "source_fingerprint": source_fingerprint,
        "source_manifest": source_manifest,
    }
    return RunResult(
        cell,
        policy_id,
        summary,
        tuple(trajectory_rows),
        tuple(decision_rows),
    )


def run_experiment(repo_root: Path = ROOT) -> ExperimentResult:
    contract = load_contract(repo_root / CONTRACT_PATH.relative_to(ROOT))
    data = prepare_episode_data(contract, repo_root=repo_root)
    grid_rows, strict_hash, conditional_hash = _validate_locked_inputs(contract, data)
    source_hashes = {label: source.sha256 for label, source in data.sources.items()}
    source_manifest = canonical_json(
        {
            "contract_config": contract.config_sha256,
            "contract_commit": CONTRACT_COMMIT,
            "strict_grid": strict_hash,
            "conditional_grid": conditional_hash,
            "data_sources": {
                label: {
                    "id": data.sources[label].record["id"],
                    "sha256": data.sources[label].sha256,
                }
                for label in sorted(data.sources)
            },
        }
    )
    source_fingerprint = hashlib.sha256(
        source_manifest.encode("utf-8")
    ).hexdigest()
    price_documents = {
        symbol: _load_json_decimal(data.sources[symbol].path) for symbol in SYMBOLS
    }
    prices = {
        symbol: _yahoo_prices(price_documents[symbol], symbol) for symbol in SYMBOLS
    }
    runs = []
    for cell in _cells(contract):
        for policy_id in ("C1", "C2"):
            runs.append(
                _run_policy(
                    contract=contract,
                    data=data,
                    prices=prices,
                    grid_rows=grid_rows,
                    cell=cell,
                    policy_id=policy_id,
                    source_fingerprint=source_fingerprint,
                    source_manifest=source_manifest,
                )
            )
    comparisons = []
    by_key = {(run.cell.cell_id, run.policy_id): run for run in runs}
    for cell in _cells(contract):
        if (
            by_key[(cell.cell_id, "C1")].summary["initial_quantities"]
            != by_key[(cell.cell_id, "C2")].summary["initial_quantities"]
        ):
            raise ComparisonError(f"{cell.cell_id}: achats initiaux non appariés")
    for scenario in contract.cost_scenarios:
        d1 = by_key[(f"{scenario.scenario_id}-D1", "C1")].summary
        d2 = by_key[(f"{scenario.scenario_id}-D2", "C1")].summary
        for field in (
            "terminal_wealth_usd",
            "total_return",
            "annualized_volatility",
            "maximum_drawdown",
            "cumulative_fees_usd",
            "distributions_accrued_usd",
            "terminal_spy_quantity",
            "terminal_bil_quantity",
        ):
            if d1[field] != d2[field]:
                raise ComparisonError(
                    f"{scenario.scenario_id}: C1 dépend indûment de D+1/D+2 ({field})"
                )
    for cell in _cells(contract):
        c1 = by_key[(cell.cell_id, "C1")].summary
        c2 = by_key[(cell.cell_id, "C2")].summary
        c1_d1 = by_key[(f"{cell.scenario.scenario_id}-D1", "C1")].summary
        c1_d2 = by_key[(f"{cell.scenario.scenario_id}-D2", "C1")].summary
        c2_d1 = by_key[(f"{cell.scenario.scenario_id}-D1", "C2")].summary
        c2_d2 = by_key[(f"{cell.scenario.scenario_id}-D2", "C2")].summary
        comparisons.append(
            {
                "episode_id": c1["episode_id"],
                "cell_id": cell.cell_id,
                "cost_scenario": cell.scenario.scenario_id,
                "cost_bps": decimal_text(cell.scenario.basis_points),
                "cash_convention": cell.cash_convention.value,
                "protocol_mode": PROTOCOL_MODE.value,
                "run_status": "COMPLETE",
                "terminal_wealth_difference_usd": decimal_text(
                    Decimal(str(c2["terminal_wealth_usd"]))
                    - Decimal(str(c1["terminal_wealth_usd"]))
                ),
                "total_return_difference": float_text(
                    float(c2["total_return"]) - float(c1["total_return"])
                ),
                "annualized_volatility_difference": float_text(
                    float(c2["annualized_volatility"])
                    - float(c1["annualized_volatility"])
                ),
                "maximum_drawdown_difference": float_text(
                    float(c2["maximum_drawdown"])
                    - float(c1["maximum_drawdown"])
                ),
                "incremental_fees_usd": decimal_text(
                    Decimal(str(c2["cumulative_fees_usd"]))
                    - Decimal(str(c1["cumulative_fees_usd"]))
                ),
                "executed_rebalances": c2["executed_rebalances"],
                "mean_spy_exposure_difference": decimal_text(
                    Decimal(str(c2["mean_spy_exposure"]))
                    - Decimal(str(c1["mean_spy_exposure"]))
                ),
                "mean_bil_exposure_difference": decimal_text(
                    Decimal(str(c2["mean_bil_exposure"]))
                    - Decimal(str(c1["mean_bil_exposure"]))
                ),
                "c1_terminal_wealth_d2_minus_d1_usd": decimal_text(
                    Decimal(str(c1_d2["terminal_wealth_usd"]))
                    - Decimal(str(c1_d1["terminal_wealth_usd"]))
                ),
                "c2_terminal_wealth_d2_minus_d1_usd": decimal_text(
                    Decimal(str(c2_d2["terminal_wealth_usd"]))
                    - Decimal(str(c2_d1["terminal_wealth_usd"]))
                ),
                "c2_total_return_d2_minus_d1": float_text(
                    float(c2_d2["total_return"]) - float(c2_d1["total_return"])
                ),
                "contract_commit": CONTRACT_COMMIT,
                "source_fingerprint": source_fingerprint,
                "source_manifest": source_manifest,
            }
        )
    return ExperimentResult(
        tuple(runs),
        tuple(comparisons),
        source_hashes,
        source_fingerprint,
        strict_hash,
        conditional_hash,
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ComparisonError(f"sortie vide: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _drawdowns(values: Sequence[float]) -> list[float]:
    peak = values[0]
    result = []
    for value in values:
        peak = max(peak, value)
        result.append(value / peak - 1)
    return result


def _polyline(values: Sequence[float], *, top: float, height: float) -> str:
    low = min(values)
    high = max(values)
    span = high - low or 1.0
    points = []
    for index, value in enumerate(values):
        x = 80 + 880 * index / (len(values) - 1)
        y = top + height * (high - value) / span
        points.append(f"{x:.2f},{y:.2f}")
    return " ".join(points)


def write_figure(result: ExperimentResult, path: Path) -> None:
    selected = {
        run.policy_id: run
        for run in result.runs
        if run.cell.cell_id == "S0-D1"
    }
    c1 = [float(row["economic_wealth_usd"]) for row in selected["C1"].trajectories]
    c2 = [float(row["economic_wealth_usd"]) for row in selected["C2"].trajectories]
    normalized = {
        "C1": [100 * value / 100000 for value in c1],
        "C2": [100 * value / 100000 for value in c2],
    }
    drawdowns = {"C1": _drawdowns(c1), "C2": _drawdowns(c2)}
    wealth_low = min(*normalized["C1"], *normalized["C2"])
    wealth_high = max(*normalized["C1"], *normalized["C2"])
    wealth_span = wealth_high - wealth_low

    def wealth_points(values: Sequence[float]) -> str:
        adjusted = [(value - wealth_low) / wealth_span for value in values]
        return _polyline(adjusted, top=70, height=250)

    drawdown_low = min(*drawdowns["C1"], *drawdowns["C2"])

    def drawdown_points(values: Sequence[float]) -> str:
        adjusted = [(value - drawdown_low) / -drawdown_low for value in values]
        return _polyline(adjusted, top=400, height=220)

    first_date = selected["C1"].trajectories[0]["valuation_date"]
    middle_date = selected["C1"].trajectories[len(c1) // 2]["valuation_date"]
    last_date = selected["C1"].trajectories[-1]["valuation_date"]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="700" viewBox="0 0 1040 700">
<rect width="1040" height="700" fill="white"/>
<style>text{{font-family:Arial,sans-serif;fill:#222}} .axis{{stroke:#888;stroke-width:1}} .grid{{stroke:#ddd;stroke-width:1}} .c1{{fill:none;stroke:#1f77b4;stroke-width:2}} .c2{{fill:none;stroke:#d62728;stroke-width:2}}</style>
<text x="80" y="30" font-size="20" font-weight="bold">C1–C2 S0-D1 — richesse normalisée et drawdown</text>
<text x="80" y="53" font-size="12">Exploratoire conditionnel; base 100 = capital initial; closes Yahoo</text>
<line class="axis" x1="80" y1="320" x2="960" y2="320"/><line class="axis" x1="80" y1="70" x2="80" y2="320"/>
<line class="grid" x1="80" y1="195" x2="960" y2="195"/>
<text x="10" y="75" font-size="11">{wealth_high:.2f}</text><text x="10" y="200" font-size="11">{(wealth_high + wealth_low) / 2:.2f}</text><text x="10" y="320" font-size="11">{wealth_low:.2f}</text>
<polyline class="c1" points="{wealth_points(normalized['C1'])}"/><polyline class="c2" points="{wealth_points(normalized['C2'])}"/>
<text x="790" y="88" font-size="12" fill="#1f77b4">C1</text><line class="c1" x1="815" y1="84" x2="855" y2="84"/>
<text x="870" y="88" font-size="12" fill="#d62728">C2</text><line class="c2" x1="895" y1="84" x2="935" y2="84"/>
<text x="80" y="375" font-size="16" font-weight="bold">Drawdown depuis le sommet courant</text>
<line class="axis" x1="80" y1="620" x2="960" y2="620"/><line class="axis" x1="80" y1="400" x2="80" y2="620"/>
<line class="grid" x1="80" y1="400" x2="960" y2="400"/>
<text x="35" y="405" font-size="11">0 %</text><text x="12" y="620" font-size="11">{100 * drawdown_low:.2f} %</text>
<polyline class="c1" points="{drawdown_points(drawdowns['C1'])}"/><polyline class="c2" points="{drawdown_points(drawdowns['C2'])}"/>
<text x="80" y="650" font-size="11">{first_date}</text><text x="480" y="650" font-size="11">{middle_date}</text><text x="885" y="650" font-size="11">{last_date}</text>
<text x="80" y="680" font-size="11">Source: sorties reproductibles de historical_c1_c2_comparison.py; cellule S0-D1.</text>
</svg>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8", newline="\n")


def write_outputs(result: ExperimentResult, output_dir: Path) -> Mapping[str, str]:
    trajectories = [row for run in result.runs for row in run.trajectories]
    decisions = [row for run in result.runs for row in run.decisions]
    summaries = [run.summary for run in result.runs]
    output_rows = {
        "trajectories": trajectories,
        "decisions": decisions,
        "summaries": summaries,
        "comparisons": list(result.comparisons),
    }
    hashes = {}
    for key, rows in output_rows.items():
        path = output_dir / OUTPUT_NAMES[key]
        _write_csv(path, rows)
        hashes[path.name] = sha256_file(path)
    figure_path = output_dir / FIGURE_NAME
    write_figure(result, figure_path)
    hashes[figure_path.name] = sha256_file(figure_path)
    return hashes


def check_outputs(result: ExperimentResult, output_dir: Path) -> None:
    with TemporaryDirectory() as temporary:
        candidate = Path(temporary)
        write_outputs(result, candidate)
        for name in OUTPUT_NAMES.values():
            expected = output_dir / name
            rebuilt = candidate / name
            if not expected.is_file() or expected.read_bytes() != rebuilt.read_bytes():
                raise ComparisonError(f"sortie non reproductible: {name}")
        expected_figure = output_dir / FIGURE_NAME
        rebuilt_figure = candidate / FIGURE_NAME
        if (
            not expected_figure.is_file()
            or expected_figure.read_bytes() != rebuilt_figure.read_bytes()
        ):
            raise ComparisonError(f"sortie non reproductible: {FIGURE_NAME}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run_experiment(ROOT)
    if args.check:
        check_outputs(result, args.output_dir)
        hashes = {
            name: sha256_file(args.output_dir / name)
            for name in (*OUTPUT_NAMES.values(), FIGURE_NAME)
        }
    else:
        hashes = write_outputs(result, args.output_dir)
    payload = {
        "complete_cells": len(result.comparisons),
        "runs": len(result.runs),
        "c2_decisions": sum(len(run.decisions) for run in result.runs),
        "source_fingerprint": result.source_fingerprint,
        "strict_grid_sha256": result.strict_grid_sha256,
        "conditional_grid_sha256": result.conditional_grid_sha256,
        "output_sha256": hashes,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
