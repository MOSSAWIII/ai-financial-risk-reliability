#!/usr/bin/env python3
"""Diagnostic post hoc C1/C2/C3 du réinvestissement des distributions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from exploratory_buy_hold_spy_bil import (
    DistributionEvent,
    _economic_wealth,
    _load_json_decimal,
    _yahoo_prices,
    load_contract,
    prepare_episode_data,
)
from historical_c1_c2_comparison import (
    CONTRACT_PATH,
    DEFAULT_OUTPUT_DIR as LOCKED_OUTPUT_DIR,
    ET,
    PROTOCOL_MODE,
    ROOT,
    SYMBOLS,
    ZERO,
    CellDefinition,
    ComparisonError,
    _cells,
    _date_range,
    _initialize_50_50,
    _new_ledger,
    _path_metrics,
    _provenance,
    _trajectory_record,
    canonical_json,
    check_outputs as check_locked_outputs,
    decimal_text,
    float_text,
    run_experiment as run_locked_experiment,
    sha256_file,
)
from synthetic_decision_adapter import (
    CashAvailabilityConvention,
    DatedPrice,
    PriceStatus,
    SnapshotStatus,
    decision_snapshot_content_sha256,
)
from synthetic_portfolio_ledger import (
    ExecutionRequest,
    FixedOrder,
    FundingConvention,
    LedgerError,
)


DEFAULT_OUTPUT_DIR = (
    ROOT / "RL" / "results" / "diagnostic_reinvestissement_c1_c2_c3_2024_2025"
)
OUTPUT_NAMES = {
    "summary": "synthese_comparative_c1_c2_c3.csv",
    "trajectories": "trajectoires_economiques_c3.csv",
    "decisions": "journal_reinvestissements_c3.csv",
    "pools": "reserves_distributions_c3.csv",
    "differences": "differences_richesse_c3_c1_c2_c3.csv",
    "gap_trajectories": "chronologie_ecarts_richesse_c1_c2_c3.csv",
}
FIGURE_NAME = "trajectoires_c1_c2_c3_s0_d1.svg"
LOCKED_ARTIFACT_HASHES = {
    "comparaison_appariee.csv": "e0b86234c6f5eb435c1dd6d426d22b3f0af265d2f8a231e3facecc45775ac311",
    "journal_decisions_c2.csv": "41fa6239c2a67ed7725f411d50830a42c785d5543aed395350208668980fcd3f",
    "synthese_financiere.csv": "aa3b6b992a6b29f21fc4a3eef47127fb21f82ed47dc1412b29efb103fd8d53bf",
    "trajectoire_et_drawdown_s0_d1.svg": "7f3b936ae3f0ee23a97ac9cee4a1fa87963b04bb8927e66aa164dd4d540f4b10",
    "trajectoires_quotidiennes.csv": "6407a80efc20ea2a5defb73a95bcffc45d697ae7b8f8b762daceddd382085849",
}


@dataclass(frozen=True)
class C3Run:
    cell: CellDefinition
    summary: Mapping[str, Any]
    trajectories: tuple[Mapping[str, Any], ...]
    decisions: tuple[Mapping[str, Any], ...]
    pools: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class DiagnosticResult:
    locked_result: Any
    c3_runs: tuple[C3Run, ...]
    summaries: tuple[Mapping[str, Any], ...]
    differences: tuple[Mapping[str, Any], ...]
    gap_trajectories: tuple[Mapping[str, Any], ...]
    source_fingerprint: str


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _last_close_before(sessions: Sequence[date], current: date) -> date:
    candidates = [session for session in sessions if session < current]
    if not candidates:
        raise ComparisonError(f"aucun close admissible avant {current.isoformat()}")
    return candidates[-1]


def _first_session_on_or_after(sessions: Sequence[date], current: date) -> date:
    candidate = next((session for session in sessions if session >= current), None)
    if candidate is None:
        raise ComparisonError(f"aucune séance après {current.isoformat()}")
    return candidate


def _intent_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def _verify_locked_artifacts(root: Path, locked_result: Any) -> None:
    output_dir = root / LOCKED_OUTPUT_DIR.relative_to(ROOT)
    for name, expected in LOCKED_ARTIFACT_HASHES.items():
        path = output_dir / name
        if not path.exists() or sha256_file(path) != expected:
            raise ComparisonError(f"livrable C1/C2 verrouillé modifié: {name}")
    check_locked_outputs(locked_result, output_dir)


def _run_c3(
    *,
    contract: Any,
    data: Any,
    prices: Mapping[str, Mapping[date, Mapping[str, Decimal]]],
    cell: CellDefinition,
    source_fingerprint: str,
) -> C3Run:
    ledger, adapter = _new_ledger(contract, data)
    initial_quantities, initial_cost, initial_notional, _ = _initialize_50_50(
        contract, data, adapter, cell.scenario
    )
    initial_residual_cash = ledger.settled_cash - ledger.purchase_payables
    base_wealth = _economic_wealth(ledger, data.execution_opens)
    if base_wealth != contract.initial_cash - initial_cost:
        raise ComparisonError("richesse initiale C3 incohérente")

    ex_events: dict[date, list[DistributionEvent]] = {}
    payment_dates: set[date] = set()
    for event in data.distributions:
        ex_events.setdefault(event.ex_date, []).append(event)
        payment_dates.add(event.payment_date)

    delay = 1 if cell.cash_convention is CashAvailabilityConvention.D_PLUS_1 else 2
    settlement_calendar = ledger.settlement_calendar
    assert settlement_calendar is not None
    sessions = tuple(data.common_sessions)
    trigger_by_date: dict[date, list[str]] = {}
    for event in data.distributions:
        cash_date = settlement_calendar.business_date_after(event.payment_date, delay)
        trigger = _first_session_on_or_after(sessions, cash_date)
        trigger_by_date.setdefault(trigger, []).append(event.event_id)

    pools = {symbol: ZERO for symbol in SYMBOLS}
    allocated_claims: set[str] = set()
    decisions: list[Mapping[str, Any]] = []
    pool_rows: list[Mapping[str, Any]] = []
    trajectories: list[Mapping[str, Any]] = []
    reinvestment_fees = ZERO
    reinvestment_notional = ZERO
    purchased = Counter({symbol: 0 for symbol in SYMBOLS})
    status_counts: Counter[str] = Counter()

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

            event_ids = sorted(
                trigger_by_date.get(current, []),
                key=lambda event_id: (
                    next(e.symbol for e in data.distributions if e.event_id == event_id),
                    event_id,
                ),
            )
            for event_id in event_ids:
                event = next(e for e in data.distributions if e.event_id == event_id)
                claim = next(
                    c
                    for c in ledger.distribution_claims
                    if c.symbol == event.symbol and c.ex_date == event.ex_date
                )
                if not claim.paid or event_id in allocated_claims:
                    raise ComparisonError(f"réserve C3 invalide pour {event_id}")
                pools[event.symbol] += claim.amount
                allocated_claims.add(event_id)

            if event_ids:
                close_date = _last_close_before(sessions, current)
                decision_at = datetime.combine(current, time(8), ET)
                snapshot = adapter.build_conditional_decision_snapshot(
                    decision_at=decision_at,
                    decision_closes={
                        symbol: DatedPrice(
                            close_date,
                            prices[symbol][close_date]["close"],
                            PriceStatus.AVAILABLE,
                        )
                        for symbol in SYMBOLS
                    },
                    close_available_at={
                        symbol: datetime.combine(close_date, time(16), ET)
                        for symbol in SYMBOLS
                    },
                    provenance=_provenance(data),
                    protocol_mode=PROTOCOL_MODE,
                    cash_availability_convention=cell.cash_convention,
                )
                if snapshot.status is not SnapshotStatus.READY:
                    raise ComparisonError(
                        f"{cell.cell_id}/{current}: snapshot C3 non évaluable"
                    )
                snapshot_hash = decision_snapshot_content_sha256(snapshot)
                prepared: list[dict[str, Any]] = []
                for event_id in event_ids:
                    event = next(e for e in data.distributions if e.event_id == event_id)
                    symbol = event.symbol
                    close = prices[symbol][close_date]["close"]
                    fee_rate = cell.scenario.basis_points / Decimal("10000")
                    quantity = int(
                        (pools[symbol] / (close * (Decimal("1") + fee_rate))).to_integral_value(
                            rounding=ROUND_FLOOR
                        )
                    )
                    payload = {
                        "cell_id": cell.cell_id,
                        "event_id": event_id,
                        "symbol": symbol,
                        "decision_at": decision_at.isoformat(),
                        "close_reference": close_date.isoformat(),
                        "decision_close_usd": decimal_text(close),
                        "pool_before_usd": decimal_text(pools[symbol]),
                        "quantity": quantity,
                        "cost_bps": decimal_text(cell.scenario.basis_points),
                        "snapshot_id": snapshot.snapshot_id,
                    }
                    prepared.append({**payload, "intent_sha256": _intent_hash(payload)})

                opens = {symbol: prices[symbol][current]["open"] for symbol in SYMBOLS}
                executable: list[dict[str, Any]] = []
                for item in prepared:
                    symbol = item["symbol"]
                    quantity = item["quantity"]
                    open_price = opens[symbol]
                    fee = open_price * quantity * cell.scenario.basis_points / Decimal("10000")
                    cost = open_price * quantity + fee
                    if quantity == 0:
                        status, reason = "NO_WHOLE_SHARE", "réserve insuffisante pour une part au close"
                    elif cost > pools[symbol]:
                        status, reason = "ECONOMIC_ORDER_REJECTED", "réserve propre insuffisante à l'open"
                    else:
                        status, reason = "EXECUTED_HYPOTHETICAL", "achat passif financé par la réserve propre"
                        executable.append({**item, "open": open_price, "fee": fee, "cost": cost})
                    status_counts[status] += 1
                    decisions.append(
                        {
                            "episode_id": "spy-bil-c1-c2-c3-2024-05-29-to-2025-05-29",
                            **item,
                            "cash_convention": cell.cash_convention.value,
                            "execution_date": current.isoformat(),
                            "execution_open_usd": decimal_text(open_price),
                            "fee_usd": decimal_text(fee),
                            "actual_cost_usd": decimal_text(cost),
                            "execution_status": status,
                            "execution_reason": reason,
                            "snapshot_content_sha256": snapshot_hash,
                            "sealed_before_open": "true",
                            "pool_transfer_usd": "0",
                            "source_fingerprint": source_fingerprint,
                        }
                    )

                if executable:
                    for symbol in SYMBOLS:
                        ledger.set_prices(symbol, market_price=opens[symbol], price_date=current)
                    ledger._authorize_snapshot_execution(
                        snapshot.snapshot_id, ledger_sequence=ledger.event_sequence
                    )
                    requests = tuple(
                        ExecutionRequest(
                            order=FixedOrder(
                                symbol=item["symbol"],
                                quantity=item["quantity"],
                                decision_date=close_date,
                                decision_price=prices[item["symbol"]][close_date]["close"],
                            ),
                            execution_price=item["open"],
                            fee=item["fee"],
                        )
                        for item in executable
                    )
                    try:
                        ledger.execute_batch(
                            requests,
                            trade_date=current,
                            funding=FundingConvention.H_FIN_NET,
                            decision_snapshot_id=snapshot.snapshot_id,
                        )
                    except LedgerError as exc:
                        raise ComparisonError(f"lot C3 rejeté par le registre: {exc}") from exc
                    for item in executable:
                        symbol = item["symbol"]
                        pools[symbol] -= item["cost"]
                        purchased[symbol] += item["quantity"]
                        reinvestment_fees += item["fee"]
                        reinvestment_notional += item["open"] * item["quantity"]

                pool_rows.append(
                    {
                        "episode_id": "spy-bil-c1-c2-c3-2024-05-29-to-2025-05-29",
                        "cell_id": cell.cell_id,
                        "cash_convention": cell.cash_convention.value,
                        "as_of_date": current.isoformat(),
                        "trigger_event_ids": canonical_json(event_ids),
                        "spy_distribution_pool_usd": decimal_text(pools["SPY"]),
                        "bil_distribution_pool_usd": decimal_text(pools["BIL"]),
                        "total_distribution_pool_usd": decimal_text(sum(pools.values(), ZERO)),
                        "initial_residual_cash_usd": decimal_text(initial_residual_cash),
                        "pool_transfer_usd": "0",
                        "source_fingerprint": source_fingerprint,
                    }
                )

        if current in data.closing_prices:
            ledger.assert_invariants()
            row = dict(
                _trajectory_record(
                    cell=cell,
                    policy_id="C3",
                    current=current,
                    ledger=ledger,
                    prices=data.closing_prices[current],
                    initial_wealth=contract.initial_cash,
                    source_fingerprint=source_fingerprint,
                )
            )
            row.update(
                {
                    "spy_distribution_pool_usd": decimal_text(pools["SPY"]),
                    "bil_distribution_pool_usd": decimal_text(pools["BIL"]),
                    "initial_residual_cash_usd": decimal_text(initial_residual_cash),
                }
            )
            trajectories.append(row)

    if len(trajectories) != 251 or len(allocated_claims) != 16:
        raise ComparisonError("couverture C3 incomplète")
    if ledger.pending_settlements or ledger.distribution_receivables != ZERO:
        raise ComparisonError("flux C3 non dénoué au terminal")
    if any(value < ZERO for value in pools.values()):
        raise ComparisonError("réserve C3 négative")
    ledger.assert_invariants()
    metrics = _path_metrics(
        base_wealth,
        trajectories,
        initial_wealth=contract.initial_cash,
        elapsed_days=(data.terminal_date - contract.execution_date).days,
    )
    terminal_prices = data.closing_prices[data.terminal_date]
    terminal_share_value = sum(
        terminal_prices[symbol] * ledger.economic_positions.get(symbol, 0)
        for symbol in SYMBOLS
    )
    acquired = sum((claim.amount for claim in ledger.distribution_claims), ZERO)
    initial_position_distributions = sum(
        event.amount_per_share * initial_quantities[event.symbol]
        for event in data.distributions
    )
    extra_distributions = acquired - initial_position_distributions
    terminal_wealth = metrics["terminal_wealth"]
    reconstructed = terminal_share_value + ledger.settled_cash
    if reconstructed != terminal_wealth:
        raise ComparisonError("réconciliation terminale C3 divergente")
    if ledger.settled_cash != initial_residual_cash + sum(pools.values(), ZERO):
        raise ComparisonError("le cash terminal ne se sépare pas entre résiduel et réserves")
    mean_spy = sum(Decimal(str(row["spy_exposure"])) for row in trajectories) / Decimal(251)
    mean_bil = sum(Decimal(str(row["bil_exposure"])) for row in trajectories) / Decimal(251)
    summary = {
        "episode_id": "spy-bil-c1-c2-c3-2024-05-29-to-2025-05-29",
        "cell_id": cell.cell_id,
        "policy_id": "C3",
        "cost_scenario": cell.scenario.scenario_id,
        "cost_bps": decimal_text(cell.scenario.basis_points),
        "cash_convention": cell.cash_convention.value,
        "run_status": "COMPLETE",
        "terminal_wealth_usd": decimal_text(terminal_wealth),
        "total_return": float_text(metrics["total_return"]),
        "annualized_volatility": float_text(metrics["annualized_volatility"]),
        "maximum_drawdown": float_text(metrics["maximum_drawdown"]),
        "terminal_cash_usd": decimal_text(ledger.settled_cash),
        "distributions_accrued_usd": decimal_text(acquired),
        "extra_distributions_from_reinvested_shares_usd": decimal_text(extra_distributions),
        "cumulative_fees_usd": decimal_text(ledger.fees_recognized),
        "initial_fees_usd": decimal_text(initial_cost),
        "reinvestment_fees_usd": decimal_text(reinvestment_fees),
        "transactions_after_initialization": status_counts[
            "EXECUTED_HYPOTHETICAL"
        ],
        "distribution_triggers": len(decisions),
        "triggers_with_purchase": status_counts["EXECUTED_HYPOTHETICAL"],
        "rejected_orders": status_counts["ECONOMIC_ORDER_REJECTED"],
        "no_whole_share_triggers": status_counts["NO_WHOLE_SHARE"],
        "additional_spy_shares": purchased["SPY"],
        "additional_bil_shares": purchased["BIL"],
        "terminal_spy_quantity": ledger.economic_positions.get("SPY", 0),
        "terminal_bil_quantity": ledger.economic_positions.get("BIL", 0),
        "terminal_spy_exposure": decimal_text(
            terminal_prices["SPY"] * ledger.economic_positions.get("SPY", 0) / terminal_wealth
        ),
        "terminal_bil_exposure": decimal_text(
            terminal_prices["BIL"] * ledger.economic_positions.get("BIL", 0) / terminal_wealth
        ),
        "mean_spy_exposure": decimal_text(mean_spy),
        "mean_bil_exposure": decimal_text(mean_bil),
        "terminal_spy_distribution_pool_usd": decimal_text(pools["SPY"]),
        "terminal_bil_distribution_pool_usd": decimal_text(pools["BIL"]),
        "terminal_total_distribution_pool_usd": decimal_text(sum(pools.values(), ZERO)),
        "initial_residual_cash_usd": decimal_text(initial_residual_cash),
        "reinvestment_gross_notional_usd": decimal_text(reinvestment_notional),
        "terminal_reconciliation_difference_usd": decimal_text(reconstructed - terminal_wealth),
        "initial_quantities": canonical_json(initial_quantities),
        "source_fingerprint": source_fingerprint,
    }
    return C3Run(cell, summary, tuple(trajectories), tuple(decisions), tuple(pool_rows))


def run_diagnostic(repo_root: Path = ROOT) -> DiagnosticResult:
    locked = run_locked_experiment(repo_root)
    _verify_locked_artifacts(repo_root, locked)
    contract = load_contract(repo_root / CONTRACT_PATH.relative_to(ROOT))
    data = prepare_episode_data(contract, repo_root=repo_root)
    price_documents = {
        symbol: _load_json_decimal(data.sources[symbol].path) for symbol in SYMBOLS
    }
    prices = {symbol: _yahoo_prices(price_documents[symbol], symbol) for symbol in SYMBOLS}
    c3_runs = tuple(
        _run_c3(
            contract=contract,
            data=data,
            prices=prices,
            cell=cell,
            source_fingerprint=locked.source_fingerprint,
        )
        for cell in _cells(contract)
    )
    locked_by_key = {(run.cell.cell_id, run.policy_id): run for run in locked.runs}
    summaries: list[Mapping[str, Any]] = []
    differences: list[Mapping[str, Any]] = []
    gap_trajectories: list[Mapping[str, Any]] = []
    for c3_run in c3_runs:
        cell_id = c3_run.cell.cell_id
        c1 = locked_by_key[(cell_id, "C1")].summary
        c2 = locked_by_key[(cell_id, "C2")].summary
        c3 = c3_run.summary
        for policy in (c1, c3, c2):
            summaries.append(
                {
                    "cell_id": cell_id,
                    "policy_id": policy["policy_id"],
                    "terminal_wealth_usd": policy["terminal_wealth_usd"],
                    "total_return": policy["total_return"],
                    "annualized_volatility": policy["annualized_volatility"],
                    "maximum_drawdown": policy["maximum_drawdown"],
                    "terminal_cash_usd": policy["terminal_cash_usd"],
                    "distributions_accrued_usd": policy["distributions_accrued_usd"],
                    "cumulative_fees_usd": policy["cumulative_fees_usd"],
                    "transactions_after_initialization": (
                        0
                        if policy["policy_id"] == "C1"
                        else (
                            policy["transactions_after_initialization"]
                            if policy["policy_id"] == "C3"
                            else policy["executed_rebalances"]
                        )
                    ),
                    "terminal_spy_quantity": policy["terminal_spy_quantity"],
                    "terminal_bil_quantity": policy["terminal_bil_quantity"],
                    "terminal_spy_exposure": policy["terminal_spy_exposure"],
                    "terminal_bil_exposure": policy["terminal_bil_exposure"],
                    "mean_spy_exposure": policy["mean_spy_exposure"],
                    "mean_bil_exposure": policy["mean_bil_exposure"],
                    "additional_spy_shares": policy.get("additional_spy_shares", ""),
                    "additional_bil_shares": policy.get("additional_bil_shares", ""),
                    "extra_distributions_from_reinvested_shares_usd": policy.get(
                        "extra_distributions_from_reinvested_shares_usd", ""
                    ),
                    "reinvestment_fees_usd": policy.get("reinvestment_fees_usd", ""),
                    "terminal_spy_distribution_pool_usd": policy.get(
                        "terminal_spy_distribution_pool_usd", ""
                    ),
                    "terminal_bil_distribution_pool_usd": policy.get(
                        "terminal_bil_distribution_pool_usd", ""
                    ),
                    "source_fingerprint": locked.source_fingerprint,
                }
            )
        w1 = Decimal(str(c1["terminal_wealth_usd"]))
        w2 = Decimal(str(c2["terminal_wealth_usd"]))
        w3 = Decimal(str(c3["terminal_wealth_usd"]))
        d31, d23, d21 = w3 - w1, w2 - w3, w2 - w1
        if d31 + d23 != d21:
            raise ComparisonError(f"identité terminale non vérifiée pour {cell_id}")
        differences.append(
            {
                "cell_id": cell_id,
                "c3_minus_c1_usd": decimal_text(d31),
                "c2_minus_c3_usd": decimal_text(d23),
                "c2_minus_c1_usd": decimal_text(d21),
                "identity_difference_usd": decimal_text(d31 + d23 - d21),
                "arithmetic_share_c3_minus_c1_of_c2_minus_c1": float_text(float(d31 / d21)),
                "source_fingerprint": locked.source_fingerprint,
            }
        )
        c1_path = locked_by_key[(cell_id, "C1")].trajectories
        c2_path = locked_by_key[(cell_id, "C2")].trajectories
        for c1_row, c3_row, c2_row in zip(
            c1_path, c3_run.trajectories, c2_path, strict=True
        ):
            if not (
                c1_row["valuation_date"]
                == c3_row["valuation_date"]
                == c2_row["valuation_date"]
            ):
                raise ComparisonError(f"trajectoires désalignées pour {cell_id}")
            w1 = Decimal(str(c1_row["economic_wealth_usd"]))
            w2 = Decimal(str(c2_row["economic_wealth_usd"]))
            w3 = Decimal(str(c3_row["economic_wealth_usd"]))
            gap_trajectories.append(
                {
                    "cell_id": cell_id,
                    "valuation_date": c1_row["valuation_date"],
                    "c1_wealth_usd": decimal_text(w1),
                    "c3_wealth_usd": decimal_text(w3),
                    "c2_wealth_usd": decimal_text(w2),
                    "c3_minus_c1_usd": decimal_text(w3 - w1),
                    "c2_minus_c3_usd": decimal_text(w2 - w3),
                    "c2_minus_c1_usd": decimal_text(w2 - w1),
                    "identity_difference_usd": decimal_text(
                        (w3 - w1) + (w2 - w3) - (w2 - w1)
                    ),
                    "source_fingerprint": locked.source_fingerprint,
                }
            )
    return DiagnosticResult(
        locked,
        c3_runs,
        tuple(summaries),
        tuple(differences),
        tuple(gap_trajectories),
        locked.source_fingerprint,
    )


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        raise ComparisonError(f"sortie vide: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _polyline(values: Sequence[float], *, top: float, bottom: float) -> str:
    width, height, left = 1120.0, 430.0, 65.0
    lo, hi = bottom, top
    return " ".join(
        f"{left + width * i / (len(values) - 1):.2f},{40 + height * (hi - value) / (hi - lo):.2f}"
        for i, value in enumerate(values)
    )


def write_figure(result: DiagnosticResult, path: Path) -> None:
    locked = {
        run.policy_id: run
        for run in result.locked_result.runs
        if run.cell.cell_id == "S0-D1"
    }
    c3 = next(run for run in result.c3_runs if run.cell.cell_id == "S0-D1")
    series = {
        "C1": [float(row["economic_wealth_usd"]) for row in locked["C1"].trajectories],
        "C3": [float(row["economic_wealth_usd"]) for row in c3.trajectories],
        "C2": [float(row["economic_wealth_usd"]) for row in locked["C2"].trajectories],
    }
    lo = min(min(values) for values in series.values())
    hi = max(max(values) for values in series.values())
    colors = {"C1": "#777777", "C3": "#1b9e77", "C2": "#d95f02"}
    lines = "\n".join(
        f'<polyline fill="none" stroke="{colors[name]}" stroke-width="2.4" points="{_polyline(values, top=hi, bottom=lo)}"/>'
        for name, values in series.items()
    )
    legend = "".join(
        f'<line x1="{720+i*130}" y1="25" x2="{745+i*130}" y2="25" stroke="{colors[name]}" stroke-width="3"/><text x="{752+i*130}" y="30">{name}</text>'
        for i, name in enumerate(("C1", "C3", "C2"))
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="520" viewBox="0 0 1240 520">
<rect width="1240" height="520" fill="white"/><text x="65" y="25" font-size="17">Richesse économique — S0-D1</text>{legend}
<line x1="65" y1="470" x2="1185" y2="470" stroke="#999"/><line x1="65" y1="40" x2="65" y2="470" stroke="#999"/>
{lines}<text x="65" y="500" font-size="12">29 mai 2024</text><text x="1100" y="500" font-size="12">29 mai 2025</text>
<text x="5" y="55" font-size="11">{hi:,.0f}</text><text x="5" y="470" font-size="11">{lo:,.0f}</text></svg>\n'''
    path.write_text(svg, encoding="utf-8", newline="\n")


def write_outputs(result: DiagnosticResult, output_dir: Path) -> Mapping[str, str]:
    rows = {
        "summary": result.summaries,
        "trajectories": tuple(row for run in result.c3_runs for row in run.trajectories),
        "decisions": tuple(row for run in result.c3_runs for row in run.decisions),
        "pools": tuple(row for run in result.c3_runs for row in run.pools),
        "differences": result.differences,
        "gap_trajectories": result.gap_trajectories,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    for key, values in rows.items():
        _write_csv(output_dir / OUTPUT_NAMES[key], values)
    write_figure(result, output_dir / FIGURE_NAME)
    return {
        name: sha256_file(output_dir / name)
        for name in (*OUTPUT_NAMES.values(), FIGURE_NAME)
    }


def check_outputs(result: DiagnosticResult, output_dir: Path) -> None:
    with TemporaryDirectory() as temporary:
        rebuilt = Path(temporary)
        write_outputs(result, rebuilt)
        for name in (*OUTPUT_NAMES.values(), FIGURE_NAME):
            if not (output_dir / name).exists() or (output_dir / name).read_bytes() != (rebuilt / name).read_bytes():
                raise ComparisonError(f"sortie C3 non reproductible: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = run_diagnostic(ROOT)
        if args.check:
            check_outputs(result, args.output_dir)
            hashes = {name: sha256_file(args.output_dir / name) for name in (*OUTPUT_NAMES.values(), FIGURE_NAME)}
        else:
            hashes = write_outputs(result, args.output_dir)
    except (ComparisonError, LedgerError, ValueError) as exc:
        print(f"FAILED_VALIDATION: {exc}", file=sys.stderr)
        return 1
    print("REINVESTMENT_DIAGNOSTIC_VALIDATED")
    print(json.dumps(hashes, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
