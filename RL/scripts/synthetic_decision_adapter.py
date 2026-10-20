#!/usr/bin/env python3
"""Adaptateur minimal d'une décision SPY/BIL vers le registre synthétique.

Le module ne choisit aucun poids, ne lit aucune donnée de marché et ne déroule
aucune période. Il transforme une décision explicitement fournie en intention
figée, puis traite cette intention une seule fois sur des entrées datées.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Protocol
from zoneinfo import ZoneInfo

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


class SnapshotStatus(str, Enum):
    READY = "READY"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class DatedPrice:
    price_date: date
    value: Decimal | None
    status: PriceStatus = PriceStatus.AVAILABLE


@dataclass(frozen=True)
class DecisionSnapshot:
    snapshot_id: str
    decision_at: datetime
    price_date: date
    decision_closes: Mapping[str, Decimal]
    economic_positions: Mapping[str, int]
    settled_positions: Mapping[str, int]
    settled_cash: Decimal
    sale_receivables: Decimal
    purchase_payables: Decimal
    known_distribution_receivables: Decimal
    economic_distribution_receivables: Decimal | None
    unknown_distribution_claim_ids: tuple[int, ...]
    cash_availability_unproven_claim_ids: tuple[int, ...]
    economic_wealth: Decimal | None
    admissible_wealth: Decimal | None
    funding_resources: Decimal
    ledger_sequence: int
    status: SnapshotStatus
    reason: str
    provenance: Mapping[str, str]


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
    decision_at: datetime | None = None
    decision_snapshot_id: str | None = None
    snapshot_ledger_sequence: int | None = None


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
    payload = {
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
    if intent.decision_snapshot_id is not None:
        payload["decision_at"] = (
            None if intent.decision_at is None else intent.decision_at.isoformat()
        )
        payload["decision_snapshot_id"] = intent.decision_snapshot_id
        payload["snapshot_ledger_sequence"] = intent.snapshot_ledger_sequence
    return payload


def canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def decision_snapshot_payload(snapshot: DecisionSnapshot) -> dict[str, Any]:
    """Retourne tout le contenu scellé d'un instantané, hors identifiant."""
    return {
        "decision_at": snapshot.decision_at.isoformat(),
        "price_date": snapshot.price_date.isoformat(),
        "decision_closes": {
            key: _decimal_text(value) for key, value in snapshot.decision_closes.items()
        },
        "economic_positions": dict(snapshot.economic_positions),
        "settled_positions": dict(snapshot.settled_positions),
        "settled_cash": _decimal_text(snapshot.settled_cash),
        "sale_receivables": _decimal_text(snapshot.sale_receivables),
        "purchase_payables": _decimal_text(snapshot.purchase_payables),
        "known_distribution_receivables": _decimal_text(
            snapshot.known_distribution_receivables
        ),
        "economic_distribution_receivables": (
            None
            if snapshot.economic_distribution_receivables is None
            else _decimal_text(snapshot.economic_distribution_receivables)
        ),
        "unknown_distribution_claim_ids": list(
            snapshot.unknown_distribution_claim_ids
        ),
        "cash_availability_unproven_claim_ids": list(
            snapshot.cash_availability_unproven_claim_ids
        ),
        "economic_wealth": (
            None
            if snapshot.economic_wealth is None
            else _decimal_text(snapshot.economic_wealth)
        ),
        "admissible_wealth": (
            None
            if snapshot.admissible_wealth is None
            else _decimal_text(snapshot.admissible_wealth)
        ),
        "funding_resources": _decimal_text(snapshot.funding_resources),
        "ledger_sequence": snapshot.ledger_sequence,
        "status": snapshot.status.value,
        "reason": snapshot.reason,
        "provenance": dict(snapshot.provenance),
    }


def decision_snapshot_content_sha256(snapshot: DecisionSnapshot) -> str:
    return hashlib.sha256(
        canonical_json_bytes(decision_snapshot_payload(snapshot))
    ).hexdigest()


def intent_content_sha256(intent: DecisionIntent) -> str:
    return hashlib.sha256(canonical_json_bytes(intent_payload(intent))).hexdigest()


def cost_scenario_fees(
    intent: DecisionIntent,
    execution_prices: Mapping[str, Any],
    basis_points: Any,
) -> Mapping[str, Decimal]:
    """Calcule une friction unique sur chaque notionnel réellement négocié."""
    try:
        bps = money(basis_points, label="coût en points de base")
    except LedgerError as exc:
        raise AdapterError(str(exc)) from exc
    if bps not in {ZERO, Decimal("1"), Decimal("5"), Decimal("10")}:
        raise AdapterError("le scénario de coûts doit être S0, S1, S2 ou S3")
    quantities = {order.symbol: abs(order.quantity) for order in intent.orders}
    fees: dict[str, Decimal] = {}
    for symbol in SYMBOLS:
        if quantities.get(symbol, 0) == 0:
            fees[symbol] = ZERO
            continue
        try:
            price = positive_money(
                execution_prices[symbol], label=f"open d'exécution {symbol}"
            )
        except (KeyError, LedgerError) as exc:
            raise AdapterError(f"open indispensable absent ou invalide pour {symbol}") from exc
        fees[symbol] = price * quantities[symbol] * bps / Decimal("10000")
    return _frozen_mapping(fees)


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

    def build_decision_snapshot(
        self,
        *,
        decision_at: datetime,
        decision_closes: Mapping[str, DatedPrice],
        close_available_at: Mapping[str, datetime],
        provenance: Mapping[str, str],
    ) -> DecisionSnapshot:
        """Construit une vue point-in-time distincte du registre économique."""
        if not isinstance(decision_at, datetime) or decision_at.tzinfo is None:
            raise AdapterError("instant de décision invalide")
        local_decision = decision_at.astimezone(ZoneInfo("America/New_York"))
        if local_decision.timetz().replace(tzinfo=None) != time(8, 0):
            raise AdapterError("la décision synthétique doit intervenir à 08:00 ET")
        decision_session = local_decision.date()
        try:
            self.ledger.trading_calendar.require_session(decision_session)
        except LedgerError as exc:
            raise AdapterError("la date de décision n'est pas une séance négociable") from exc
        previous_sessions = [
            item
            for item in self.ledger.trading_calendar.sessions
            if item < decision_session
        ]
        if not previous_sessions:
            raise AdapterError("aucune clôture antérieure admissible")
        price_date = previous_sessions[-1]
        required_provenance = {
            "SPY_close",
            "BIL_close",
            "trading_calendar",
            "settlement_calendar",
            "economic_positions",
            "settled_positions",
            "settled_cash",
            "pending_settlements",
            "distribution_claims",
        }
        if set(provenance) != required_provenance or any(
            not isinstance(value, str) or not value.strip()
            for value in provenance.values()
        ):
            raise AdapterError("provenance de l'instantané incomplète")

        closes: dict[str, Decimal] = {}
        reasons: list[str] = []
        for symbol in SYMBOLS:
            observation = decision_closes.get(symbol)
            available_at = close_available_at.get(symbol)
            if (
                not isinstance(observation, DatedPrice)
                or observation.status is not PriceStatus.AVAILABLE
                or observation.value is None
            ):
                reasons.append(f"clôture non disponible pour {symbol}")
                continue
            if observation.price_date != price_date:
                reasons.append(f"clôture {symbol} non datée de la dernière séance")
                continue
            if (
                not isinstance(available_at, datetime)
                or available_at.tzinfo is None
                or available_at.date() < observation.price_date
                or available_at > decision_at
            ):
                reasons.append(f"disponibilité point-in-time non prouvée pour {symbol}")
                continue
            try:
                closes[symbol] = positive_money(
                    observation.value, label=f"clôture de décision {symbol}"
                )
            except LedgerError as exc:
                reasons.append(str(exc))

        if any(entry.event_date > decision_session for entry in self.ledger.journal):
            reasons.append("le registre contient un événement économique futur")
        if any(
            item.settlement_date <= decision_session
            for item in self.ledger.pending_settlements
        ):
            reasons.append("un règlement échu doit précéder l'instantané")
        if any(
            not claim.paid and claim.payment_date <= decision_session
            for claim in self.ledger.distribution_claims
        ):
            reasons.append("un paiement échu doit précéder l'instantané")
        if any(
            item.claim_id is None and item.ex_date <= decision_session
            for item in self.ledger.distribution_announcements
        ):
            reasons.append("une ex-date annoncée doit précéder l'instantané")

        announcements = {
            item.claim_id: item
            for item in self.ledger.distribution_announcements
            if item.claim_id is not None
        }
        known_receivables = ZERO
        unknown_claim_ids: list[int] = []
        unproven_cash_ids: list[int] = []
        for claim in self.ledger.distribution_claims:
            if claim.paid:
                if (
                    claim.cash_available_at is None
                    or claim.cash_available_at > decision_at
                ):
                    unproven_cash_ids.append(claim.claim_id)
                continue
            announcement = announcements.get(claim.claim_id)
            known = False
            if announcement is not None:
                if announcement.knowledge_at is not None:
                    known = announcement.knowledge_at <= decision_at
                else:
                    known = announcement.knowledge_date < decision_session
            if known:
                known_receivables += claim.amount
            else:
                unknown_claim_ids.append(claim.claim_id)

        if unknown_claim_ids:
            reasons.append("montant de créance non démontré comme connu")
        if unproven_cash_ids:
            reasons.append("disponibilité du cash de distribution non démontrée")

        unproven_cash_amount = sum(
            (
                claim.amount
                for claim in self.ledger.distribution_claims
                if claim.claim_id in unproven_cash_ids
            ),
            ZERO,
        )
        known_settled_cash = self.ledger.settled_cash - unproven_cash_amount

        positions = {
            symbol: self.ledger.economic_positions.get(symbol, 0)
            for symbol in SYMBOLS
        }
        settled_positions = {
            symbol: self.ledger.settled_positions.get(symbol, 0)
            for symbol in SYMBOLS
        }
        holdings = (
            sum(closes[symbol] * positions[symbol] for symbol in SYMBOLS)
            if set(closes) == set(SYMBOLS)
            else None
        )
        economic_wealth = (
            None
            if holdings is None or unknown_claim_ids or unproven_cash_ids
            else holdings
            + self.ledger.settled_cash
            + self.ledger.distribution_receivables
            + self.ledger.sale_receivables
            - self.ledger.purchase_payables
        )
        admissible_wealth = (
            economic_wealth
            if not reasons
            and economic_wealth is not None
            and known_receivables == self.ledger.distribution_receivables
            else None
        )
        status = (
            SnapshotStatus.READY
            if admissible_wealth is not None
            else SnapshotStatus.NOT_EVALUABLE
        )
        reason = "instantané décisionnel complet" if not reasons else "; ".join(reasons)
        provisional = DecisionSnapshot(
            "",
            decision_at,
            price_date,
            _frozen_mapping(closes),
            _frozen_mapping(positions),
            _frozen_mapping(settled_positions),
            known_settled_cash,
            self.ledger.sale_receivables,
            self.ledger.purchase_payables,
            known_receivables,
            (
                None
                if unknown_claim_ids
                else self.ledger.distribution_receivables
            ),
            tuple(unknown_claim_ids),
            tuple(unproven_cash_ids),
            economic_wealth,
            admissible_wealth,
            max(
                ZERO,
                known_settled_cash - self.ledger.purchase_payables,
            ),
            self.ledger.event_sequence,
            status,
            reason,
            _frozen_mapping(provenance),
        )
        return replace(
            provisional,
            snapshot_id="SNAPSHOT-" + decision_snapshot_content_sha256(provisional),
        )

    def prepare_intent_from_snapshot(
        self,
        snapshot: DecisionSnapshot,
        *,
        target_weight_spy: Any,
    ) -> DecisionIntent:
        """Scelle une intention uniquement depuis un instantané admissible."""
        if not isinstance(snapshot, DecisionSnapshot):
            raise AdapterError("instantané décisionnel invalide")
        if snapshot.snapshot_id != (
            "SNAPSHOT-" + decision_snapshot_content_sha256(snapshot)
        ):
            raise AdapterError("l'empreinte de l'instantané est invalide")
        if snapshot.status is not SnapshotStatus.READY or snapshot.admissible_wealth is None:
            raise AdapterError("instantané NOT_EVALUABLE: " + snapshot.reason)
        if snapshot.ledger_sequence != self.ledger.event_sequence:
            raise AdapterError("instantané périmé avant préparation")
        if dict(snapshot.economic_positions) != {
            symbol: self.ledger.economic_positions.get(symbol, 0)
            for symbol in SYMBOLS
        }:
            raise AdapterError("positions de l'instantané périmées")
        return self._seal_intent(
            decision_date=snapshot.price_date,
            known_market_wealth=snapshot.admissible_wealth,
            inherited_positions=snapshot.economic_positions,
            closes=snapshot.decision_closes,
            target_weight_spy=target_weight_spy,
            decision_at=snapshot.decision_at,
            decision_snapshot_id=snapshot.snapshot_id,
            snapshot_ledger_sequence=snapshot.ledger_sequence,
        )

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

        return self._seal_intent(
            decision_date=decision_date,
            known_market_wealth=wealth,
            inherited_positions=positions,
            closes=closes,
            target_weight_spy=weight,
        )

    def _seal_intent(
        self,
        *,
        decision_date: date,
        known_market_wealth: Any,
        inherited_positions: Mapping[str, int],
        closes: Mapping[str, Decimal],
        target_weight_spy: Any,
        decision_at: datetime | None = None,
        decision_snapshot_id: str | None = None,
        snapshot_ledger_sequence: int | None = None,
    ) -> DecisionIntent:
        try:
            wealth = money(known_market_wealth, label="richesse connue")
            weight = money(target_weight_spy, label="poids cible SPY")
        except LedgerError as exc:
            raise AdapterError(str(exc)) from exc
        positions = self._normalize_positions(inherited_positions)
        if wealth < ZERO or not ZERO <= weight <= Decimal("1"):
            raise AdapterError("paramètres économiques de l'intention invalides")
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
            decision_at=decision_at,
            decision_snapshot_id=decision_snapshot_id,
            snapshot_ledger_sequence=snapshot_ledger_sequence,
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
            decision_at=provisional.decision_at,
            decision_snapshot_id=provisional.decision_snapshot_id,
            snapshot_ledger_sequence=provisional.snapshot_ledger_sequence,
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

        if intent.decision_snapshot_id is not None:
            if (
                intent.decision_at is None
                or intent.snapshot_ledger_sequence is None
                or intent.decision_at.date() != execution_date
            ):
                return self._terminal(
                    intent,
                    ExecutionStatus.INVALID_INPUT,
                    "l'instantané ne correspond pas à la séance d'exécution",
                    execution_date,
                    before,
                )
            if intent.snapshot_ledger_sequence != self.ledger.event_sequence:
                return self._terminal(
                    intent,
                    ExecutionStatus.INVALID_INPUT,
                    "l'instantané est périmé : l'état a changé avant l'open",
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
            if intent.decision_snapshot_id is not None:
                self.ledger._authorize_snapshot_execution(
                    intent.decision_snapshot_id,
                    ledger_sequence=self.ledger.event_sequence,
                )
            settlement_ids = self.ledger.execute_batch(
                requests,
                trade_date=execution_date,
                funding=FundingConvention.H_FIN_NET,
                decision_snapshot_id=intent.decision_snapshot_id,
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
    "DecisionSnapshot",
    "DecisionIntent",
    "ExecutionOutcome",
    "ExecutionStatus",
    "FundingSource",
    "IntentPersistence",
    "PriceStatus",
    "SnapshotStatus",
    "SyntheticDecisionAdapter",
    "canonical_json_bytes",
    "cost_scenario_fees",
    "decision_snapshot_content_sha256",
    "decision_snapshot_payload",
    "intent_content_sha256",
    "intent_payload",
]
