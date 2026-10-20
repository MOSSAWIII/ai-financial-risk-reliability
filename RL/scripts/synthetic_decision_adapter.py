#!/usr/bin/env python3
"""Adaptateur minimal d'une décision SPY/BIL vers le registre synthétique.

Le module ne choisit aucun poids, ne lit aucune donnée de marché et ne déroule
aucune période. Il transforme une décision explicitement fournie en intention
figée, puis traite cette intention une seule fois sur des entrées datées.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol

from synthetic_portfolio_ledger import (
    AccountingSnapshot,
    ExecutionRequest,
    FixedOrder,
    FundingConvention,
    LedgerError,
    SyntheticPortfolioLedger,
    money,
    positive_money,
    whole_share_quantity,
)


SYMBOLS = ("SPY", "BIL")
ZERO = Decimal("0")


class AdapterError(ValueError):
    """Entrée incompatible avec le contrat de préparation de l'adaptateur."""


class ExecutionStatus(str, Enum):
    EXECUTED_HYPOTHETICAL = "EXECUTED_HYPOTHETICAL"
    VOLUNTARY_HOLD = "VOLUNTARY_HOLD"
    ECONOMIC_ORDER_REJECTED = "ECONOMIC_ORDER_REJECTED"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    INVALID_INPUT = "INVALID_INPUT"


class PriceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    DISPUTED = "DISPUTED"


class FundingSource(str, Enum):
    NONE = "NONE"
    SETTLED_CASH = "SETTLED_CASH"
    UNSETTLED_SALE_PROCEEDS = "UNSETTLED_SALE_PROCEEDS"


@dataclass(frozen=True)
class DatedPrice:
    price_date: date
    value: Decimal | None
    status: PriceStatus = PriceStatus.AVAILABLE


@dataclass(frozen=True)
class DecisionIntent:
    intent_id: str
    content_sha256: str
    decision_date: date
    known_market_wealth: Decimal
    target_weight_spy: Decimal
    inherited_positions: Mapping[str, int]
    target_quantities: Mapping[str, int]
    decision_prices: Mapping[str, Decimal]
    orders: tuple[FixedOrder, ...]


@dataclass(frozen=True)
class ExecutionOutcome:
    intent: DecisionIntent
    status: ExecutionStatus
    reason: str
    execution_date: date
    settlement_date: date | None
    execution_prices: Mapping[str, Decimal]
    fees: Mapping[str, Decimal]
    funding_source: FundingSource
    accounting_before: AccountingSnapshot
    accounting_after: AccountingSnapshot
    wealth_before_trade: Decimal | None = None
    wealth_after_trade: Decimal | None = None
    settlement_ids: tuple[int, ...] = ()


class IntentPersistence(Protocol):
    """Interface minimale d'un journal persistant, sans restaurer le registre."""

    def register_intent(self, intent: DecisionIntent) -> None: ...

    def intent_sha256(self, intent_id: str) -> str | None: ...

    def terminal_status(self, intent_id: str) -> str | None: ...

    def record_terminal(self, outcome: ExecutionOutcome) -> None: ...


def _frozen_mapping(values: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(values))


def _decimal_text(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    return format(value.normalize(), "f")


def intent_payload(intent: DecisionIntent) -> dict[str, Any]:
    """Retourne le contenu économique canonique, hors identifiant et empreinte."""
    return {
        "decision_date": intent.decision_date.isoformat(),
        "known_market_wealth": _decimal_text(intent.known_market_wealth),
        "target_weight_spy": _decimal_text(intent.target_weight_spy),
        "inherited_positions": {
            symbol: intent.inherited_positions[symbol] for symbol in SYMBOLS
        },
        "target_quantities": {
            symbol: intent.target_quantities[symbol] for symbol in SYMBOLS
        },
        "decision_prices": {
            symbol: _decimal_text(intent.decision_prices[symbol]) for symbol in SYMBOLS
        },
        "orders": [
            {
                "symbol": order.symbol,
                "quantity": order.quantity,
                "decision_date": order.decision_date.isoformat(),
                "decision_price": _decimal_text(order.decision_price),
            }
            for order in sorted(intent.orders, key=lambda item: item.symbol)
        ],
    }


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def intent_content_sha256(intent: DecisionIntent) -> str:
    return hashlib.sha256(canonical_json_bytes(intent_payload(intent))).hexdigest()


@dataclass
class SyntheticDecisionAdapter:
    """Traite des intentions explicites avec un registre strict déjà fourni."""

    ledger: SyntheticPortfolioLedger
    persistence: IntentPersistence | None = None
    outcomes: list[ExecutionOutcome] = field(default_factory=list, init=False)
    _prepared_intents: dict[str, str] = field(default_factory=dict, init=False)
    _processed_intents: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        if not self.ledger.strict_temporal:
            raise AdapterError("l'adaptateur exige strict_temporal=True")
        if self.ledger.trading_calendar is None or self.ledger.settlement_calendar is None:
            raise AdapterError("l'adaptateur exige deux calendriers explicites")

    def prepare_intent(
        self,
        *,
        decision_date: date,
        known_market_wealth: Any,
        inherited_positions: Mapping[str, int],
        decision_closes: Mapping[str, DatedPrice],
        target_weight_spy: Any,
    ) -> DecisionIntent:
        """Fige les quantités cibles à partir des seules clôtures datées."""
        if not isinstance(decision_date, date):
            raise AdapterError("date de décision invalide")
        try:
            self.ledger.trading_calendar.require_session(decision_date)
        except LedgerError as exc:
            raise AdapterError("la date de décision n'est pas une séance négociable") from exc
        if any(entry.event_date > decision_date for entry in self.ledger.journal):
            raise AdapterError("la décision est antidatée par rapport à l'état du registre")
        if any(
            entry.kind == "REALIZED_DISTRIBUTION_ACCRUAL"
            for entry in self.ledger.journal
        ):
            raise AdapterError(
                "une comptabilité de distribution ex post interdit toute nouvelle décision"
            )
        positions = self._normalize_positions(inherited_positions)
        ledger_positions = {symbol: self.ledger.economic_positions.get(symbol, 0) for symbol in SYMBOLS}
        outside = {
            symbol: quantity
            for symbol, quantity in self.ledger.economic_positions.items()
            if symbol not in SYMBOLS and quantity != 0
        }
        if outside or positions != ledger_positions:
            raise AdapterError("les positions héritées ne correspondent pas au registre")

        closes: dict[str, Decimal] = {}
        for symbol in SYMBOLS:
            observation = decision_closes.get(symbol)
            if not isinstance(observation, DatedPrice):
                raise AdapterError(f"clôture datée absente pour {symbol}")
            if observation.status is not PriceStatus.AVAILABLE or observation.value is None:
                raise AdapterError(f"clôture non disponible pour {symbol}")
            if observation.price_date != decision_date:
                raise AdapterError(f"la clôture de {symbol} n'est pas datée de la décision")
            try:
                closes[symbol] = positive_money(
                    observation.value, label=f"clôture de décision {symbol}"
                )
            except LedgerError as exc:
                raise AdapterError(str(exc)) from exc

        try:
            wealth = money(known_market_wealth, label="richesse connue")
            weight = money(target_weight_spy, label="poids cible SPY")
        except LedgerError as exc:
            raise AdapterError(str(exc)) from exc
        if wealth < ZERO:
            raise AdapterError("la richesse connue ne peut pas être négative")
        if not ZERO <= weight <= Decimal("1"):
            raise AdapterError("le poids cible SPY doit appartenir à [0, 1]")

        expected_wealth = (
            sum(closes[symbol] * positions[symbol] for symbol in SYMBOLS)
            + self.ledger.settled_cash
            + self.ledger.distribution_receivables
            + self.ledger.sale_receivables
            - self.ledger.purchase_payables
        )
        if wealth != expected_wealth:
            raise AdapterError("la richesse connue ne correspond pas à l'état et aux clôtures fournis")

        target_weights = {"SPY": weight, "BIL": Decimal("1") - weight}
        targets = {
            symbol: whole_share_quantity(target_weights[symbol] * wealth, closes[symbol])
            for symbol in SYMBOLS
        }
        orders = tuple(
            FixedOrder(
                symbol=symbol,
                quantity=targets[symbol] - positions[symbol],
                decision_date=decision_date,
                decision_price=closes[symbol],
            )
            for symbol in SYMBOLS
            if targets[symbol] != positions[symbol]
        )
        provisional = DecisionIntent(
            intent_id="",
            content_sha256="",
            decision_date=decision_date,
            known_market_wealth=wealth,
            target_weight_spy=weight,
            inherited_positions=_frozen_mapping(positions),
            target_quantities=_frozen_mapping(targets),
            decision_prices=_frozen_mapping(closes),
            orders=orders,
        )
        digest = intent_content_sha256(provisional)
        intent = DecisionIntent(
            intent_id=f"INTENT-{digest}",
            content_sha256=digest,
            decision_date=provisional.decision_date,
            known_market_wealth=provisional.known_market_wealth,
            target_weight_spy=provisional.target_weight_spy,
            inherited_positions=provisional.inherited_positions,
            target_quantities=provisional.target_quantities,
            decision_prices=provisional.decision_prices,
            orders=provisional.orders,
        )
        known = self._prepared_intents.get(intent.intent_id)
        if known is not None and known != digest:
            raise AdapterError("identifiant d'intention réutilisé avec un contenu différent")
        self._prepared_intents[intent.intent_id] = digest
        if self.persistence is not None:
            self.persistence.register_intent(intent)
        return intent

    def process_intent(
        self,
        intent: DecisionIntent,
        *,
        execution_date: date,
        execution_opens: Mapping[str, DatedPrice],
        fees: Mapping[str, Any] | None = None,
        documentary_issue: str | None = None,
    ) -> ExecutionOutcome:
        """Traite une fois l'intention, sans choisir ni redimensionner son poids."""
        before = self.ledger.accounting_snapshot()
        if not isinstance(intent, DecisionIntent):
            raise AdapterError("intention invalide")
        if not isinstance(execution_date, date):
            raise AdapterError("date d'exécution invalide")
        integrity_reason = self._intent_integrity_reason(intent)
        if integrity_reason is not None:
            return self._finish(
                intent,
                ExecutionStatus.INVALID_INPUT,
                integrity_reason,
                execution_date,
                before,
            )
        if intent.intent_id in self._processed_intents:
            return self._finish(
                intent,
                ExecutionStatus.INVALID_INPUT,
                "cette intention a déjà été traitée",
                execution_date,
                before,
            )
        if self.persistence is not None and self.persistence.terminal_status(intent.intent_id):
            return self._finish(
                intent,
                ExecutionStatus.INVALID_INPUT,
                "cette intention possède déjà un résultat terminal persistant",
                execution_date,
                before,
            )

        if intent.decision_date >= execution_date:
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                "la date de décision doit précéder la date d'exécution",
                execution_date,
                before,
            )
        next_session = next(
            (
                session
                for session in self.ledger.trading_calendar.sessions
                if session > intent.decision_date
            ),
            None,
        )
        if next_session is None:
            return self._terminal(
                intent,
                ExecutionStatus.NOT_EVALUABLE,
                "le calendrier ne contient aucune séance postérieure à la décision",
                execution_date,
                before,
            )
        if execution_date != next_session:
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                "la date d'exécution n'est pas la séance admissible suivante",
                execution_date,
                before,
            )
        current_positions = {
            symbol: self.ledger.economic_positions.get(symbol, 0) for symbol in SYMBOLS
        }
        if current_positions != dict(intent.inherited_positions):
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                "l'intention est périmée : les positions ont changé",
                execution_date,
                before,
            )
        if not intent.orders:
            return self._terminal(
                intent,
                ExecutionStatus.VOLUNTARY_HOLD,
                "la décision ne demande aucune transaction",
                execution_date,
                before,
            )
        if documentary_issue:
            return self._terminal(
                intent,
                ExecutionStatus.NOT_EVALUABLE,
                documentary_issue,
                execution_date,
                before,
            )

        price_values, price_error, price_status = self._execution_prices(
            execution_opens, execution_date
        )
        if price_error is not None:
            return self._terminal(
                intent,
                price_status,
                price_error,
                execution_date,
                before,
            )
        fee_values, fee_error = self._fees(fees)
        if fee_error is not None:
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                fee_error,
                execution_date,
                before,
                execution_prices=price_values,
            )

        try:
            settlement_date = self.ledger.settlement_calendar.settlement_date(execution_date)
        except LedgerError as exc:
            return self._terminal(
                intent,
                ExecutionStatus.NOT_EVALUABLE,
                str(exc),
                execution_date,
                before,
                execution_prices=price_values,
                fees=fee_values,
            )

        due_reason = self._due_event_reason(execution_date)
        if due_reason is not None:
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                due_reason,
                execution_date,
                before,
                settlement_date=settlement_date,
                execution_prices=price_values,
                fees=fee_values,
            )

        for order in intent.orders:
            if order.quantity < 0:
                available = self.ledger.settled_positions.get(order.symbol, 0)
                if -order.quantity > available:
                    return self._terminal(
                        intent,
                        ExecutionStatus.ECONOMIC_ORDER_REJECTED,
                        f"titres réglés et intégralement payés insuffisants pour {order.symbol}",
                        execution_date,
                        before,
                        settlement_date=settlement_date,
                        execution_prices=price_values,
                        fees=fee_values,
                    )

        requests = tuple(
            ExecutionRequest(
                order=order,
                execution_price=price_values[order.symbol],
                fee=fee_values[order.symbol],
            )
            for order in intent.orders
        )
        purchase_need = sum(
            price_values[order.symbol] * order.quantity + fee_values[order.symbol]
            for order in intent.orders
            if order.quantity > 0
        )
        settled_capacity = self.ledger.settled_cash - self.ledger.purchase_payables
        funding_source = (
            FundingSource.NONE
            if purchase_need == ZERO
            else FundingSource.SETTLED_CASH
            if purchase_need <= settled_capacity
            else FundingSource.UNSETTLED_SALE_PROCEEDS
        )

        try:
            for symbol in SYMBOLS:
                self.ledger.set_prices(
                    symbol,
                    market_price=price_values[symbol],
                    price_date=execution_date,
                )
        except LedgerError as exc:
            return self._terminal(
                intent,
                ExecutionStatus.INVALID_INPUT,
                str(exc),
                execution_date,
                before,
                settlement_date=settlement_date,
                execution_prices=price_values,
                fees=fee_values,
            )

        wealth_before = self.ledger.wealth_market()
        trade_before = self.ledger.accounting_snapshot()
        try:
            settlement_ids = self.ledger.execute_batch(
                requests,
                trade_date=execution_date,
                funding=FundingConvention.H_FIN_NET,
            )
        except LedgerError as exc:
            return self._terminal(
                intent,
                ExecutionStatus.ECONOMIC_ORDER_REJECTED,
                str(exc),
                execution_date,
                before,
                settlement_date=settlement_date,
                execution_prices=price_values,
                fees=fee_values,
                wealth_before_trade=wealth_before,
            )

        after = self.ledger.accounting_snapshot()
        wealth_after = self.ledger.wealth_market()
        if trade_before == after:
            raise AssertionError("une exécution acceptée doit modifier l'état comptable")
        return self._terminal(
            intent,
            ExecutionStatus.EXECUTED_HYPOTHETICAL,
            "lot hypothétique comptabilisé",
            execution_date,
            before,
            settlement_date=settlement_date,
            execution_prices=price_values,
            fees=fee_values,
            funding_source=funding_source,
            wealth_before_trade=wealth_before,
            wealth_after_trade=wealth_after,
            settlement_ids=tuple(settlement_ids),
        )

    @staticmethod
    def _normalize_positions(positions: Mapping[str, int]) -> dict[str, int]:
        if not isinstance(positions, Mapping):
            raise AdapterError("positions héritées invalides")
        if set(positions) - set(SYMBOLS):
            raise AdapterError("l'univers de l'adaptateur est limité à SPY et BIL")
        result = {symbol: positions.get(symbol, 0) for symbol in SYMBOLS}
        if any(type(quantity) is not int or quantity < 0 for quantity in result.values()):
            raise AdapterError("les positions héritées doivent être des entiers non négatifs")
        return result

    def _intent_integrity_reason(self, intent: DecisionIntent) -> str | None:
        try:
            digest = intent_content_sha256(intent)
        except (KeyError, AttributeError, TypeError, ValueError):
            return "contenu d'intention invalide"
        if intent.content_sha256 != digest:
            return "l'empreinte de l'intention ne correspond pas à son contenu"
        if intent.intent_id != f"INTENT-{digest}":
            return "l'identifiant de l'intention ne correspond pas à son contenu"
        expected = self._prepared_intents.get(intent.intent_id)
        if expected is None and self.persistence is not None:
            expected = self.persistence.intent_sha256(intent.intent_id)
        if expected is None:
            return "l'intention n'a pas été préparée par cette frontière"
        if expected != digest:
            return "identifiant d'intention réutilisé avec un contenu différent"

        try:
            positions = self._normalize_positions(intent.inherited_positions)
            targets = self._normalize_positions(intent.target_quantities)
        except AdapterError as exc:
            return str(exc)
        if set(intent.decision_prices) != set(SYMBOLS):
            return "prix de décision incomplets"
        try:
            prices = {
                symbol: positive_money(
                    intent.decision_prices[symbol], label=f"prix de décision {symbol}"
                )
                for symbol in SYMBOLS
            }
            wealth = money(intent.known_market_wealth, label="richesse connue")
            weight = money(intent.target_weight_spy, label="poids cible SPY")
        except (LedgerError, AdapterError) as exc:
            return str(exc)
        if wealth < ZERO or not ZERO <= weight <= Decimal("1"):
            return "paramètres économiques de l'intention invalides"
        expected_targets = {
            "SPY": whole_share_quantity(weight * wealth, prices["SPY"]),
            "BIL": whole_share_quantity(
                (Decimal("1") - weight) * wealth, prices["BIL"]
            ),
        }
        if targets != expected_targets:
            return "quantités cibles incohérentes avec le poids et les prix de décision"
        expected_orders = tuple(
            FixedOrder(
                symbol=symbol,
                quantity=targets[symbol] - positions[symbol],
                decision_date=intent.decision_date,
                decision_price=prices[symbol],
            )
            for symbol in SYMBOLS
            if targets[symbol] != positions[symbol]
        )
        if tuple(sorted(intent.orders, key=lambda item: item.symbol)) != tuple(
            sorted(expected_orders, key=lambda item: item.symbol)
        ):
            return "ordres incohérents avec les positions et quantités cibles"
        return None

    @staticmethod
    def _execution_prices(
        observations: Mapping[str, DatedPrice], execution_date: date
    ) -> tuple[dict[str, Decimal], str | None, ExecutionStatus]:
        values: dict[str, Decimal] = {}
        for symbol in SYMBOLS:
            observation = observations.get(symbol)
            if not isinstance(observation, DatedPrice):
                return values, f"open indispensable absent pour {symbol}", ExecutionStatus.NOT_EVALUABLE
            if observation.status is not PriceStatus.AVAILABLE or observation.value is None:
                return (
                    values,
                    f"open {observation.status.value.lower()} pour {symbol}",
                    ExecutionStatus.NOT_EVALUABLE,
                )
            if observation.price_date != execution_date:
                return (
                    values,
                    f"l'open de {symbol} n'est pas daté de l'exécution",
                    ExecutionStatus.INVALID_INPUT,
                )
            try:
                values[symbol] = positive_money(
                    observation.value, label=f"open d'exécution {symbol}"
                )
            except LedgerError as exc:
                return values, str(exc), ExecutionStatus.INVALID_INPUT
        return values, None, ExecutionStatus.EXECUTED_HYPOTHETICAL

    @staticmethod
    def _fees(fees: Mapping[str, Any] | None) -> tuple[dict[str, Decimal], str | None]:
        raw = {} if fees is None else fees
        if not isinstance(raw, Mapping) or set(raw) - set(SYMBOLS):
            return {}, "table de frais invalide"
        values: dict[str, Decimal] = {}
        for symbol in SYMBOLS:
            try:
                value = money(raw.get(symbol, ZERO), label=f"frais {symbol}")
            except LedgerError as exc:
                return values, str(exc)
            if value < ZERO:
                return values, f"les frais {symbol} ne peuvent pas être négatifs"
            values[symbol] = value
        return values, None

    def _due_event_reason(self, execution_date: date) -> str | None:
        if any(
            item.settlement_date <= execution_date for item in self.ledger.pending_settlements
        ):
            return "un règlement échu doit être traité avant l'exécution"
        if any(
            not claim.paid and claim.payment_date <= execution_date
            for claim in self.ledger.distribution_claims
        ):
            return "un paiement de distribution échu doit être traité avant l'exécution"
        if any(
            item.claim_id is None and item.ex_date <= execution_date
            for item in self.ledger.distribution_announcements
        ):
            return "une ex-date annoncée doit être traitée avant l'exécution"
        return None

    def _terminal(
        self,
        intent: DecisionIntent,
        status: ExecutionStatus,
        reason: str,
        execution_date: date,
        before: AccountingSnapshot,
        **kwargs: Any,
    ) -> ExecutionOutcome:
        outcome = self._finish(intent, status, reason, execution_date, before, **kwargs)
        self._processed_intents.add(intent.intent_id)
        if self.persistence is not None:
            self.persistence.record_terminal(outcome)
        return outcome

    def _finish(
        self,
        intent: DecisionIntent,
        status: ExecutionStatus,
        reason: str,
        execution_date: date,
        before: AccountingSnapshot,
        *,
        settlement_date: date | None = None,
        execution_prices: Mapping[str, Decimal] | None = None,
        fees: Mapping[str, Decimal] | None = None,
        funding_source: FundingSource = FundingSource.NONE,
        wealth_before_trade: Decimal | None = None,
        wealth_after_trade: Decimal | None = None,
        settlement_ids: tuple[int, ...] = (),
    ) -> ExecutionOutcome:
        outcome = ExecutionOutcome(
            intent=intent,
            status=status,
            reason=reason,
            execution_date=execution_date,
            settlement_date=settlement_date,
            execution_prices=_frozen_mapping(execution_prices or {}),
            fees=_frozen_mapping(fees or {}),
            funding_source=funding_source,
            accounting_before=before,
            accounting_after=self.ledger.accounting_snapshot(),
            wealth_before_trade=wealth_before_trade,
            wealth_after_trade=wealth_after_trade,
            settlement_ids=settlement_ids,
        )
        self.outcomes.append(outcome)
        return outcome


__all__ = [
    "AdapterError",
    "DatedPrice",
    "DecisionIntent",
    "ExecutionOutcome",
    "ExecutionStatus",
    "FundingSource",
    "IntentPersistence",
    "PriceStatus",
    "SyntheticDecisionAdapter",
    "canonical_json_bytes",
    "intent_content_sha256",
    "intent_payload",
]
