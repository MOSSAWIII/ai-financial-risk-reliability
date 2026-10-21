#!/usr/bin/env python3
"""Registre comptable minimal pour opérations SPY/BIL entièrement artificielles.

Le module ne recherche aucune donnée, ne choisit aucune allocation et ne simule
aucun marché. Les dates, prix, quantités et calendriers lui sont tous fournis.
"""

from __future__ import annotations

from bisect import bisect_right
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


ZERO = Decimal("0")
TRANSITION_T1 = date(2024, 5, 28)


class LedgerError(ValueError):
    """Opération incompatible avec les conventions du registre."""


class FundingConvention(str, Enum):
    CONSERVATIVE = "CONSERVATIVE_SETTLED_CASH"
    H_FIN_NET = "H_FIN_NET"


class EventPhase(int, Enum):
    """Ordre comptable conventionnel lorsqu'une date seule est disponible."""

    CORPORATE_ACTION = 10
    DISTRIBUTION_ENTITLEMENT = 20
    SETTLEMENT = 30
    DISTRIBUTION_PAYMENT = 40
    PRICE_MARK = 50
    TRADE = 60


def money(value: Any, *, label: str = "montant") -> Decimal:
    """Convertit une valeur explicite en Decimal fini."""
    if isinstance(value, bool):
        raise LedgerError(f"{label} invalide")
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise LedgerError(f"{label} invalide") from exc
    if not result.is_finite():
        raise LedgerError(f"{label} doit être fini")
    return result


def positive_money(value: Any, *, label: str) -> Decimal:
    result = money(value, label=label)
    if result <= ZERO:
        raise LedgerError(f"{label} doit être strictement positif")
    return result


def whole_share_quantity(target_notional: Any, decision_price: Any) -> int:
    """Dimensionne un ordre entier avec une information connue à la décision."""
    notional = money(target_notional, label="notionnel cible")
    price = positive_money(decision_price, label="prix de décision")
    if notional < ZERO:
        raise LedgerError("le notionnel cible ne peut pas être négatif")
    return int((notional / price).to_integral_value(rounding=ROUND_FLOOR))


@dataclass(frozen=True)
class FixedOrder:
    symbol: str
    quantity: int
    decision_date: date
    decision_price: Decimal


@dataclass(frozen=True)
class ExecutionRequest:
    order: FixedOrder
    execution_price: Decimal
    fee: Decimal = ZERO


@dataclass(frozen=True)
class PendingSettlement:
    settlement_id: int
    symbol: str
    quantity: int
    trade_date: date
    settlement_date: date
    gross_amount: Decimal
    cash_receivable: Decimal
    cash_payable: Decimal
    fee: Decimal


@dataclass
class DistributionClaim:
    claim_id: int
    symbol: str
    ex_date: date
    payment_date: date
    entitled_shares: int
    amount_per_share: Decimal
    amount: Decimal
    paid: bool = False
    information_mode: str = "LEGACY"
    cash_available_at: datetime | None = None


@dataclass
class DistributionAnnouncement:
    announcement_id: int
    symbol: str
    knowledge_date: date
    ex_date: date
    payment_date: date
    amount_per_share: Decimal
    claim_id: int | None = None
    knowledge_at: datetime | None = None


@dataclass(frozen=True)
class JournalEntry:
    sequence: int
    event_date: date
    kind: str
    details: Mapping[str, Any]


@dataclass(frozen=True)
class RejectionRecord:
    sequence: int
    event_date: date | None
    operation: str
    reason: str


@dataclass(frozen=True)
class AccountingSnapshot:
    settled_cash: Decimal
    economic_positions: Mapping[str, int]
    settled_positions: Mapping[str, int]
    sale_receivables: Decimal
    purchase_payables: Decimal
    distribution_receivables: Decimal
    fees_recognized: Decimal
    pending_settlement_count: int
    unpaid_distribution_count: int


class SyntheticSettlementCalendar:
    """Calendrier de règlement explicitement fourni, sans portée historique."""

    def __init__(self, business_dates: Iterable[date]) -> None:
        dates = tuple(sorted(set(business_dates)))
        if not dates:
            raise LedgerError("le calendrier artificiel est vide")
        if any(item.weekday() >= 5 for item in dates):
            raise LedgerError("le calendrier de règlement contient un week-end")
        self.business_dates = dates

    @staticmethod
    def cycle_for(trade_date: date) -> int:
        return 1 if trade_date >= TRANSITION_T1 else 2

    def settlement_date(self, trade_date: date) -> date:
        lag = self.cycle_for(trade_date)
        index = bisect_right(self.business_dates, trade_date)
        target = index + lag - 1
        if target >= len(self.business_dates):
            raise LedgerError("calendrier artificiel insuffisant pour calculer le règlement")
        return self.business_dates[target]

    def business_date_after(self, reference_date: date, delay: int) -> date:
        """Return the Nth supplied settlement business date after a date."""
        if type(delay) is not int or delay < 1:
            raise LedgerError("le délai doit être un nombre positif de jours ouvrés")
        index = bisect_right(self.business_dates, reference_date)
        target = index + delay - 1
        if target >= len(self.business_dates):
            raise LedgerError("calendrier artificiel insuffisant pour le délai de cash")
        return self.business_dates[target]


class SyntheticTradingCalendar:
    """Séances négociables, distinctes des jours admissibles au règlement."""

    def __init__(
        self,
        sessions: Iterable[date],
        *,
        shortened_sessions: Iterable[date] = (),
    ) -> None:
        dates = tuple(sorted(set(sessions)))
        shortened = frozenset(shortened_sessions)
        if not dates:
            raise LedgerError("le calendrier de négociation est vide")
        if any(item.weekday() >= 5 for item in dates):
            raise LedgerError("le calendrier de négociation contient un week-end")
        if not shortened.issubset(dates):
            raise LedgerError("une séance écourtée est absente des séances négociables")
        self.sessions = dates
        self.shortened_sessions = shortened
        self._date_set = set(dates)

    def require_session(self, trading_date: date) -> None:
        if trading_date not in self._date_set:
            raise LedgerError("la trade date est absente du calendrier de négociation")

    def is_shortened(self, trading_date: date) -> bool:
        self.require_session(trading_date)
        return trading_date in self.shortened_sessions


@dataclass
class SyntheticPortfolioLedger:
    initial_cash: Decimal
    strict_temporal: bool = False
    trading_calendar: SyntheticTradingCalendar | None = None
    settlement_calendar: SyntheticSettlementCalendar | None = None
    settled_cash: Decimal = field(init=False)
    economic_positions: dict[str, int] = field(default_factory=dict, init=False)
    settled_positions: dict[str, int] = field(default_factory=dict, init=False)
    market_prices: dict[str, Decimal] = field(default_factory=dict, init=False)
    nav_prices: dict[str, Decimal] = field(default_factory=dict, init=False)
    pending_settlements: list[PendingSettlement] = field(default_factory=list, init=False)
    distribution_claims: list[DistributionClaim] = field(default_factory=list, init=False)
    distribution_announcements: list[DistributionAnnouncement] = field(
        default_factory=list, init=False
    )
    fees_recognized: Decimal = field(default=ZERO, init=False)
    journal: list[JournalEntry] = field(default_factory=list, init=False)
    rejections: list[RejectionRecord] = field(default_factory=list, init=False)
    _position_events: dict[str, list[tuple[date, int, str, Any]]] = field(default_factory=dict, init=False)
    _applied_splits: set[tuple[str, date, int, int]] = field(default_factory=set, init=False)
    _realized_distribution_event_ids: set[str] = field(default_factory=set, init=False)
    _decision_authorizations: dict[str, int] = field(default_factory=dict, init=False)
    _sequence: int = field(default=0, init=False)
    _next_settlement_id: int = field(default=1, init=False)
    _next_claim_id: int = field(default=1, init=False)
    _next_announcement_id: int = field(default=1, init=False)
    _last_effective_date: date | None = field(default=None, init=False)
    _last_phase: EventPhase | None = field(default=None, init=False)
    _price_dates: dict[str, date] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.initial_cash = money(self.initial_cash, label="cash initial")
        if self.initial_cash < ZERO:
            raise LedgerError("le cash initial ne peut pas être négatif")
        if self.strict_temporal and (
            self.trading_calendar is None or self.settlement_calendar is None
        ):
            raise LedgerError(
                "le mode temporel strict exige des calendriers de négociation et de règlement"
            )
        self.settled_cash = self.initial_cash

    def _validate_effect_time(
        self,
        event_date: date,
        phase: EventPhase,
        *,
        operation: str,
    ) -> None:
        if not self.strict_temporal:
            return
        if self._last_effective_date is not None:
            if event_date < self._last_effective_date:
                raise LedgerError(
                    f"{operation}: événement antidaté après clôture comptable du "
                    f"{self._last_effective_date.isoformat()}"
                )
            if (
                event_date == self._last_effective_date
                and self._last_phase is not None
                and phase.value < self._last_phase.value
            ):
                raise LedgerError(
                    f"{operation}: ordre intrajournalier incompatible avec "
                    f"{self._last_phase.name}"
                )

        if phase.value > EventPhase.DISTRIBUTION_ENTITLEMENT.value:
            missed = [
                item
                for item in self.distribution_announcements
                if item.claim_id is None and item.ex_date <= event_date
            ]
            if missed:
                raise LedgerError("une ex-date annoncée doit être comptabilisée avant cet événement")
        if phase.value > EventPhase.SETTLEMENT.value and any(
            item.settlement_date <= event_date for item in self.pending_settlements
        ):
            raise LedgerError("un règlement échu doit être traité avant cet événement")
        if phase.value > EventPhase.DISTRIBUTION_PAYMENT.value and any(
            not claim.paid and claim.payment_date <= event_date
            for claim in self.distribution_claims
        ):
            raise LedgerError("un paiement de distribution échu doit précéder cet événement")

    def _commit_effect_time(self, event_date: date, phase: EventPhase) -> None:
        if self.strict_temporal:
            self._last_effective_date = event_date
            self._last_phase = phase

    def _commit_knowledge_time(self, knowledge_date: date) -> None:
        """Avance la chronologie sans produire d'effet financier."""
        if self.strict_temporal and (
            self._last_effective_date is None or knowledge_date > self._last_effective_date
        ):
            self._last_effective_date = knowledge_date
            self._last_phase = None

    def _next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def _record(self, event_date: date, kind: str, **details: Any) -> None:
        self.journal.append(JournalEntry(self._next_sequence(), event_date, kind, details))

    def _reject(self, operation: str, reason: str, event_date: date | None = None) -> None:
        self.rejections.append(
            RejectionRecord(self._next_sequence(), event_date, operation, reason)
        )
        raise LedgerError(reason)

    def set_prices(
        self,
        symbol: str,
        *,
        market_price: Any,
        nav_price: Any | None = None,
        price_date: date | None = None,
    ) -> None:
        symbol = self._valid_symbol(symbol)
        try:
            market = positive_money(market_price, label="prix de marché")
            nav = None if nav_price is None else positive_money(nav_price, label="NAV")
            if self.strict_temporal:
                if price_date is None:
                    raise LedgerError("le mode temporel strict exige la date du prix")
                assert self.trading_calendar is not None
                self.trading_calendar.require_session(price_date)
                self._validate_effect_time(
                    price_date, EventPhase.PRICE_MARK, operation="PRICE_MARK"
                )
        except LedgerError as exc:
            self._reject("PRICE_MARK", str(exc), price_date)
        self.market_prices[symbol] = market
        if nav is not None:
            self.nav_prices[symbol] = nav
        if price_date is not None:
            self._price_dates[symbol] = price_date
            self._record(price_date, "PRICE_MARK", symbol=symbol, market_price=market, nav_price=nav)
            self._commit_effect_time(price_date, EventPhase.PRICE_MARK)

    @staticmethod
    def _valid_symbol(symbol: str) -> str:
        if not isinstance(symbol, str) or not symbol.strip():
            raise LedgerError("symbole invalide")
        return symbol.strip().upper()

    def accounting_snapshot(self) -> AccountingSnapshot:
        return AccountingSnapshot(
            settled_cash=self.settled_cash,
            economic_positions=deepcopy(self.economic_positions),
            settled_positions=deepcopy(self.settled_positions),
            sale_receivables=self.sale_receivables,
            purchase_payables=self.purchase_payables,
            distribution_receivables=self.distribution_receivables,
            fees_recognized=self.fees_recognized,
            pending_settlement_count=len(self.pending_settlements),
            unpaid_distribution_count=sum(not claim.paid for claim in self.distribution_claims),
        )

    @property
    def event_sequence(self) -> int:
        """Version monotone de l'état, utilisable pour sceller un instantané."""
        return self._sequence

    def _authorize_snapshot_execution(
        self, snapshot_id: str, *, ledger_sequence: int
    ) -> None:
        """Autorise une seule exécution interne issue d'un instantané à jour."""
        if (
            not isinstance(snapshot_id, str)
            or not snapshot_id.startswith("SNAPSHOT-")
            or ledger_sequence != self._sequence
        ):
            raise LedgerError("autorisation d'instantané invalide ou périmée")
        self._decision_authorizations[snapshot_id] = ledger_sequence

    @property
    def sale_receivables(self) -> Decimal:
        return sum((item.cash_receivable for item in self.pending_settlements), ZERO)

    @property
    def purchase_payables(self) -> Decimal:
        return sum((item.cash_payable for item in self.pending_settlements), ZERO)

    @property
    def distribution_receivables(self) -> Decimal:
        return sum((claim.amount for claim in self.distribution_claims if not claim.paid), ZERO)

    def wealth_market(self) -> Decimal:
        missing = [symbol for symbol in self.economic_positions if symbol not in self.market_prices]
        if missing:
            raise LedgerError(f"prix de marché manquant pour {', '.join(sorted(missing))}")
        holdings = sum(
            (self.market_prices[symbol] * quantity for symbol, quantity in self.economic_positions.items()),
            ZERO,
        )
        return (
            holdings
            + self.settled_cash
            + self.distribution_receivables
            + self.sale_receivables
            - self.purchase_payables
        )

    def wealth_nav(self) -> Decimal:
        missing = [symbol for symbol in self.economic_positions if symbol not in self.nav_prices]
        if missing:
            raise LedgerError(f"NAV manquante pour {', '.join(sorted(missing))}")
        holdings = sum(
            (self.nav_prices[symbol] * quantity for symbol, quantity in self.economic_positions.items()),
            ZERO,
        )
        return (
            holdings
            + self.settled_cash
            + self.distribution_receivables
            + self.sale_receivables
            - self.purchase_payables
        )

    def execute_batch(
        self,
        requests: Sequence[ExecutionRequest],
        *,
        trade_date: date,
        settlement_date: date | None = None,
        funding: FundingConvention = FundingConvention.CONSERVATIVE,
        decision_snapshot_id: str | None = None,
    ) -> list[int]:
        """Comptabilise atomiquement des transactions au trade date."""
        try:
            authorized_sequence = (
                None
                if decision_snapshot_id is None
                else self._decision_authorizations.pop(decision_snapshot_id, None)
            )
            if (
                self._realized_distribution_event_ids
                and authorized_sequence != self._sequence
            ):
                raise LedgerError(
                    "une comptabilité de distribution ex post interdit toute nouvelle transaction"
                )
            if self.strict_temporal:
                assert self.trading_calendar is not None
                assert self.settlement_calendar is not None
                self.trading_calendar.require_session(trade_date)
                expected = self.settlement_calendar.settlement_date(trade_date)
                if settlement_date is not None and settlement_date != expected:
                    raise LedgerError(
                        "la settlement date explicite ne correspond pas au calendrier de règlement"
                    )
                settlement_date = expected
                self._validate_effect_time(trade_date, EventPhase.TRADE, operation="TRADE")
                symbols = {self._valid_symbol(item.order.symbol) for item in requests}
                if any(self._price_dates.get(symbol) != trade_date for symbol in symbols):
                    raise LedgerError("chaque prix d'exécution strict doit être daté de la trade date")
            elif settlement_date is None:
                raise LedgerError("la settlement date explicite est requise en mode historique")
            assert settlement_date is not None
            normalized = self._validate_batch(requests, trade_date, settlement_date)
            candidate_positions = dict(self.economic_positions)
            net_quantities: dict[str, int] = {}
            for symbol, quantity, _, _, _ in normalized:
                net_quantities[symbol] = net_quantities.get(symbol, 0) + quantity
            for symbol, quantity in net_quantities.items():
                candidate_positions[symbol] = candidate_positions.get(symbol, 0) + quantity
                if candidate_positions[symbol] < 0:
                    raise LedgerError(f"vente supérieure à la position économique disponible pour {symbol}")

            new_settlements: list[PendingSettlement] = []
            next_id = self._next_settlement_id
            total_fees = ZERO

            for symbol, quantity, execution_price, fee, order in normalized:
                gross = execution_price * abs(quantity)
                if quantity < 0 and fee > gross:
                    raise LedgerError("les frais de vente dépassent le produit brut")
                new_settlements.append(
                    PendingSettlement(
                        settlement_id=next_id,
                        symbol=symbol,
                        quantity=quantity,
                        trade_date=trade_date,
                        settlement_date=settlement_date,
                        gross_amount=gross,
                        cash_receivable=gross - fee if quantity < 0 else ZERO,
                        cash_payable=gross + fee if quantity > 0 else ZERO,
                        fee=fee,
                    )
                )
                next_id += 1
                total_fees += fee

            self._validate_position_settlement(new_settlements)
            self._validate_funding(new_settlements, funding)
        except LedgerError as exc:
            self._reject("EXECUTE_BATCH", str(exc), trade_date)

        self.economic_positions = candidate_positions
        self.pending_settlements.extend(new_settlements)
        self.fees_recognized += total_fees
        self._next_settlement_id = next_id
        for settlement, (_, _, _, _, order) in zip(new_settlements, normalized):
            seq = self._next_sequence()
            self._position_events.setdefault(settlement.symbol, []).append(
                (trade_date, seq, "TRADE", settlement.quantity)
            )
            self.journal.append(
                JournalEntry(
                    seq,
                    trade_date,
                    "TRADE",
                    {
                        "settlement_id": settlement.settlement_id,
                        "symbol": settlement.symbol,
                        "quantity": settlement.quantity,
                        "decision_date": order.decision_date,
                        "decision_price": order.decision_price,
                        "execution_price": settlement.gross_amount / abs(settlement.quantity),
                        "fee": settlement.fee,
                        "settlement_date": settlement.settlement_date,
                        "funding": funding.value,
                    },
                )
            )
        self.assert_invariants()
        self._commit_effect_time(trade_date, EventPhase.TRADE)
        return [item.settlement_id for item in new_settlements]

    def _validate_batch(
        self,
        requests: Sequence[ExecutionRequest],
        trade_date: date,
        settlement_date: date,
    ) -> list[tuple[str, int, Decimal, Decimal, FixedOrder]]:
        if not requests:
            raise LedgerError("lot de transactions vide")
        if settlement_date <= trade_date:
            raise LedgerError("la settlement date doit être postérieure à la trade date")
        normalized = []
        for request in requests:
            if not isinstance(request, ExecutionRequest):
                raise LedgerError("instruction d'exécution invalide")
            order = request.order
            symbol = self._valid_symbol(order.symbol)
            if type(order.quantity) is not int:
                raise LedgerError("les quantités fractionnaires sont interdites")
            if order.quantity == 0:
                raise LedgerError("une quantité nulle est interdite")
            if order.decision_date >= trade_date:
                raise LedgerError("la quantité doit être fixée avant la trade date")
            decision_price = positive_money(order.decision_price, label="prix de décision")
            execution_price = positive_money(request.execution_price, label="prix d'exécution")
            fee = money(request.fee, label="frais")
            if fee < ZERO:
                raise LedgerError("les frais ne peuvent pas être négatifs")
            if symbol not in self.market_prices:
                raise LedgerError(f"prix de marché absent pour {symbol}")
            if execution_price != self.market_prices[symbol]:
                raise LedgerError(
                    f"le prix d'exécution de {symbol} doit égaler le prix de marché du même instant"
                )
            normalized.append(
                (symbol, order.quantity, execution_price, fee, FixedOrder(symbol, order.quantity, order.decision_date, decision_price))
            )
        return normalized

    def _validate_funding(
        self,
        new_settlements: Sequence[PendingSettlement],
        funding: FundingConvention,
    ) -> None:
        if not isinstance(funding, FundingConvention):
            raise LedgerError("convention de financement inconnue")
        all_pending = [*self.pending_settlements, *new_settlements]
        if funding is FundingConvention.CONSERVATIVE:
            reserved = sum((item.cash_payable for item in all_pending), ZERO)
            if reserved > self.settled_cash:
                raise LedgerError("cash réglé insuffisant selon la convention conservatrice")
            return

        cash = self.settled_cash
        dates = sorted({item.settlement_date for item in all_pending})
        for settlement_date in dates:
            due = [item for item in all_pending if item.settlement_date == settlement_date]
            cash += sum((item.cash_receivable - item.cash_payable for item in due), ZERO)
            if cash < ZERO:
                raise LedgerError(
                    f"financement net impossible à la date {settlement_date.isoformat()}"
                )

    def _validate_position_settlement(
        self, new_settlements: Sequence[PendingSettlement]
    ) -> None:
        """Vérifie que les titres pourront être livrés à chaque échéance."""
        candidate = dict(self.settled_positions)
        all_pending = [*self.pending_settlements, *new_settlements]
        for settlement_date in sorted({item.settlement_date for item in all_pending}):
            for item in (row for row in all_pending if row.settlement_date == settlement_date):
                candidate[item.symbol] = candidate.get(item.symbol, 0) + item.quantity
            negative = [symbol for symbol, quantity in candidate.items() if quantity < 0]
            if negative:
                raise LedgerError(
                    "titres réglés insuffisants à la date "
                    f"{settlement_date.isoformat()} pour {', '.join(sorted(negative))}"
                )

    def settle_through(self, as_of_date: date) -> list[int]:
        """Règle atomiquement chaque groupe de flux arrivé à échéance."""
        if self.strict_temporal:
            try:
                self._validate_effect_time(
                    as_of_date, EventPhase.SETTLEMENT, operation="SETTLEMENT"
                )
                due_exact = [
                    item
                    for item in self.pending_settlements
                    if item.settlement_date == as_of_date
                ]
                if not due_exact:
                    if any(
                        item.settlement_date > as_of_date
                        for item in self.pending_settlements
                    ):
                        raise LedgerError("tentative de règlement prématuré")
                    raise LedgerError("aucun règlement exigible à cette date")
                if any(
                    item.settlement_date < as_of_date
                    for item in self.pending_settlements
                ):
                    raise LedgerError("un règlement antérieur est resté impayé")
            except LedgerError as exc:
                self._reject("SETTLEMENT", str(exc), as_of_date)
        due_dates = sorted(
            {item.settlement_date for item in self.pending_settlements if item.settlement_date <= as_of_date}
        )
        if not due_dates:
            return []

        candidate_cash = self.settled_cash
        candidate_settled = dict(self.settled_positions)
        groups: list[tuple[date, list[PendingSettlement], Decimal]] = []
        for due_date in due_dates:
            due = [item for item in self.pending_settlements if item.settlement_date == due_date]
            cash_change = sum((item.cash_receivable - item.cash_payable for item in due), ZERO)
            candidate_cash += cash_change
            if candidate_cash < ZERO:
                self._reject("SETTLEMENT", "le règlement créerait un cash négatif", due_date)
            for item in due:
                candidate_settled[item.symbol] = candidate_settled.get(item.symbol, 0) + item.quantity
            if any(quantity < 0 for quantity in candidate_settled.values()):
                self._reject("SETTLEMENT", "le règlement créerait une position réglée négative", due_date)
            groups.append((due_date, due, cash_change))

        settled_ids = sorted(item.settlement_id for _, due, _ in groups for item in due)
        settled_id_set = set(settled_ids)
        self.settled_cash = candidate_cash
        self.settled_positions = candidate_settled
        self.pending_settlements = [
            item for item in self.pending_settlements if item.settlement_id not in settled_id_set
        ]
        for due_date, due, cash_change in groups:
            self._record(
                due_date,
                "SETTLEMENT",
                settlement_ids=tuple(sorted(item.settlement_id for item in due)),
                cash_change=cash_change,
            )
        self.assert_invariants()
        self._commit_effect_time(as_of_date, EventPhase.SETTLEMENT)
        return settled_ids

    def announce_distribution(
        self,
        symbol: str,
        *,
        knowledge_date: date,
        ex_date: date,
        payment_date: date,
        amount_per_share: Any,
        knowledge_at: datetime | None = None,
    ) -> int:
        """Enregistre une information future sans créer de créance."""
        symbol = self._valid_symbol(symbol)
        try:
            amount = money(amount_per_share, label="distribution par part")
            if not self.strict_temporal:
                raise LedgerError("les annonces séparées exigent le mode temporel strict")
            if amount < ZERO:
                raise LedgerError("la distribution ne peut pas être négative")
            if self._last_effective_date is not None and knowledge_date < self._last_effective_date:
                raise LedgerError("la date de connaissance est antidatée")
            if ex_date < knowledge_date:
                raise LedgerError("une distribution ne peut pas être annoncée après son ex-date")
            if knowledge_at is not None and (
                knowledge_at.tzinfo is None
                or knowledge_at.astimezone(ZoneInfo("America/New_York")).date()
                != knowledge_date
            ):
                raise LedgerError("instant de connaissance de distribution invalide")
            if self._last_effective_date is not None and (
                ex_date < self._last_effective_date
                or (
                    ex_date == self._last_effective_date
                    and self._last_phase is not None
                    and self._last_phase.value >= EventPhase.DISTRIBUTION_ENTITLEMENT.value
                )
            ):
                raise LedgerError("l'ex-date est déjà clôturée dans l'ordre intrajournalier")
            if payment_date < ex_date:
                raise LedgerError("la payment date précède l'ex-date")
        except LedgerError as exc:
            self._reject("DISTRIBUTION_ANNOUNCEMENT", str(exc), knowledge_date)
        announcement = DistributionAnnouncement(
            self._next_announcement_id,
            symbol,
            knowledge_date,
            ex_date,
            payment_date,
            amount,
            knowledge_at=knowledge_at,
        )
        self._next_announcement_id += 1
        self.distribution_announcements.append(announcement)
        self._record(
            knowledge_date,
            "DISTRIBUTION_ANNOUNCEMENT",
            announcement_id=announcement.announcement_id,
            symbol=symbol,
            ex_date=ex_date,
            payment_date=payment_date,
            amount_per_share=amount,
            knowledge_at=knowledge_at,
        )
        self._commit_knowledge_time(knowledge_date)
        return announcement.announcement_id

    def accrue_announced_distribution(
        self, announcement_id: int, *, event_date: date
    ) -> int:
        """Crée la créance uniquement à l'ex-date annoncée."""
        try:
            announcement = next(
                item
                for item in self.distribution_announcements
                if item.announcement_id == announcement_id
            )
            if announcement.claim_id is not None:
                raise LedgerError("cette distribution a déjà acquis son droit")
            if event_date != announcement.ex_date:
                raise LedgerError("le droit doit être acquis exactement à l'ex-date")
            self._validate_effect_time(
                event_date,
                EventPhase.DISTRIBUTION_ENTITLEMENT,
                operation="DISTRIBUTION_ENTITLEMENT",
            )
        except (LedgerError, StopIteration) as exc:
            reason = str(exc) if isinstance(exc, LedgerError) else "annonce de distribution inconnue"
            self._reject("DISTRIBUTION_ACCRUAL", reason, event_date)

        shares = self.shares_for_entitlement(announcement.symbol, event_date)
        claim = DistributionClaim(
            claim_id=self._next_claim_id,
            symbol=announcement.symbol,
            ex_date=announcement.ex_date,
            payment_date=announcement.payment_date,
            entitled_shares=shares,
            amount_per_share=announcement.amount_per_share,
            amount=announcement.amount_per_share * shares,
            information_mode="ANNOUNCED",
        )
        self._next_claim_id += 1
        self.distribution_claims.append(claim)
        announcement.claim_id = claim.claim_id
        self._record(
            event_date,
            "DISTRIBUTION_ACCRUAL",
            announcement_id=announcement_id,
            claim_id=claim.claim_id,
            symbol=claim.symbol,
            entitled_shares=shares,
            amount_per_share=claim.amount_per_share,
            amount=claim.amount,
            payment_date=claim.payment_date,
        )
        self._commit_effect_time(event_date, EventPhase.DISTRIBUTION_ENTITLEMENT)
        self.assert_invariants()
        return claim.claim_id

    def accrue_realized_distribution(
        self,
        symbol: str,
        *,
        event_id: str,
        ex_date: date,
        payment_date: date,
        amount_per_share: Any,
    ) -> int:
        """Comptabilise ex post un droit réalisé sans inventer une annonce.

        L'événement n'est jamais enregistré comme information historiquement connue.
        Par défaut il bloque toute transaction ultérieure. La seule exception est une
        autorisation interne à usage unique issue d'un instantané décisionnel strict
        qui n'expose pas prématurément ce montant.
        """
        symbol = self._valid_symbol(symbol)
        try:
            if not self.strict_temporal:
                raise LedgerError("la comptabilité ex post exige le mode temporel strict")
            if not isinstance(event_id, str) or not event_id.strip():
                raise LedgerError("identifiant de distribution réalisée invalide")
            event_id = event_id.strip()
            if event_id in self._realized_distribution_event_ids:
                raise LedgerError("cette distribution réalisée est déjà comptabilisée")
            amount = money(amount_per_share, label="distribution par part")
            if amount < ZERO:
                raise LedgerError("la distribution ne peut pas être négative")
            if payment_date < ex_date:
                raise LedgerError("la payment date précède l'ex-date")
            self._validate_effect_time(
                ex_date,
                EventPhase.DISTRIBUTION_ENTITLEMENT,
                operation="REALIZED_DISTRIBUTION_ACCRUAL",
            )
        except LedgerError as exc:
            self._reject("REALIZED_DISTRIBUTION_ACCRUAL", str(exc), ex_date)

        shares = self.shares_for_entitlement(symbol, ex_date)
        claim = DistributionClaim(
            claim_id=self._next_claim_id,
            symbol=symbol,
            ex_date=ex_date,
            payment_date=payment_date,
            entitled_shares=shares,
            amount_per_share=amount,
            amount=amount * shares,
            information_mode="REALIZED_EX_POST",
        )
        self._next_claim_id += 1
        self.distribution_claims.append(claim)
        self._realized_distribution_event_ids.add(event_id)
        self._record(
            ex_date,
            "REALIZED_DISTRIBUTION_ACCRUAL",
            event_id=event_id,
            claim_id=claim.claim_id,
            symbol=symbol,
            entitled_shares=shares,
            amount_per_share=amount,
            amount=claim.amount,
            payment_date=payment_date,
            information_use="EX_POST_ACCOUNTING_ONLY",
        )
        self._commit_effect_time(ex_date, EventPhase.DISTRIBUTION_ENTITLEMENT)
        self.assert_invariants()
        return claim.claim_id

    def accrue_distribution(
        self,
        symbol: str,
        *,
        ex_date: date,
        payment_date: date,
        amount_per_share: Any,
    ) -> int:
        if self.strict_temporal:
            self._reject(
                "DISTRIBUTION_ACCRUAL",
                "le mode temporel strict exige une annonce puis une acquisition à l'ex-date",
                ex_date,
            )
        symbol = self._valid_symbol(symbol)
        amount = money(amount_per_share, label="distribution par part")
        if amount < ZERO:
            self._reject("DISTRIBUTION_ACCRUAL", "la distribution ne peut pas être négative", ex_date)
        if payment_date < ex_date:
            self._reject("DISTRIBUTION_ACCRUAL", "la payment date précède l'ex-date", ex_date)
        shares = self.shares_before(symbol, ex_date)
        claim = DistributionClaim(
            claim_id=self._next_claim_id,
            symbol=symbol,
            ex_date=ex_date,
            payment_date=payment_date,
            entitled_shares=shares,
            amount_per_share=amount,
            amount=amount * shares,
        )
        self._next_claim_id += 1
        self.distribution_claims.append(claim)
        self._record(
            ex_date,
            "DISTRIBUTION_ACCRUAL",
            claim_id=claim.claim_id,
            symbol=symbol,
            entitled_shares=shares,
            amount_per_share=amount,
            amount=claim.amount,
            payment_date=payment_date,
        )
        self.assert_invariants()
        return claim.claim_id

    def pay_distributions_through(
        self,
        as_of_date: date,
        *,
        cash_available_at: datetime | None = None,
    ) -> list[int]:
        if cash_available_at is not None and (
            cash_available_at.tzinfo is None
            or cash_available_at.astimezone(ZoneInfo("America/New_York")).date()
            != as_of_date
        ):
            self._reject(
                "DISTRIBUTION_PAYMENT",
                "instant de disponibilité du cash invalide",
                as_of_date,
            )
        if self.strict_temporal:
            try:
                self._validate_effect_time(
                    as_of_date,
                    EventPhase.DISTRIBUTION_PAYMENT,
                    operation="DISTRIBUTION_PAYMENT",
                )
                due_exact = [
                    claim
                    for claim in self.distribution_claims
                    if not claim.paid and claim.payment_date == as_of_date
                ]
                if not due_exact:
                    if any(
                        not claim.paid and claim.payment_date > as_of_date
                        for claim in self.distribution_claims
                    ):
                        raise LedgerError("tentative de paiement prématuré")
                    raise LedgerError("aucune distribution exigible à cette date")
                if any(
                    not claim.paid and claim.payment_date < as_of_date
                    for claim in self.distribution_claims
                ):
                    raise LedgerError("un paiement de distribution antérieur est resté impayé")
            except LedgerError as exc:
                self._reject("DISTRIBUTION_PAYMENT", str(exc), as_of_date)
        claims = [
            claim for claim in self.distribution_claims
            if not claim.paid and claim.payment_date <= as_of_date
        ]
        if not claims:
            return []
        amount = sum((claim.amount for claim in claims), ZERO)
        self.settled_cash += amount
        for claim in claims:
            claim.paid = True
            claim.cash_available_at = cash_available_at
        ids = [claim.claim_id for claim in claims]
        for payment_date in sorted({claim.payment_date for claim in claims}):
            group = [claim for claim in claims if claim.payment_date == payment_date]
            self._record(
                payment_date,
                "DISTRIBUTION_PAYMENT",
                claim_ids=tuple(claim.claim_id for claim in group),
                amount=sum((claim.amount for claim in group), ZERO),
                cash_available_at=cash_available_at,
            )
        self.assert_invariants()
        self._commit_effect_time(as_of_date, EventPhase.DISTRIBUTION_PAYMENT)
        return ids

    def shares_before(self, symbol: str, cutoff_date: date) -> int:
        """Position économique au début du jour, avant tout événement daté du jour."""
        return self._replay_shares(symbol, cutoff_date, include_same_day_splits=False)

    def shares_for_entitlement(self, symbol: str, ex_date: date) -> int:
        """Position après corporate actions, mais avant les trades de l'ex-date."""
        return self._replay_shares(symbol, ex_date, include_same_day_splits=True)

    def _replay_shares(
        self,
        symbol: str,
        cutoff_date: date,
        *,
        include_same_day_splits: bool,
    ) -> int:
        symbol = self._valid_symbol(symbol)
        shares = 0
        for event_date, sequence, kind, value in sorted(
            self._position_events.get(symbol, []), key=lambda item: (item[0], item[1])
        ):
            if event_date > cutoff_date or (
                event_date == cutoff_date
                and not (include_same_day_splits and kind == "SPLIT")
            ):
                break
            if kind == "TRADE":
                shares += int(value)
            elif kind == "SPLIT":
                numerator, denominator = value
                transformed = shares * numerator
                if transformed % denominator:
                    raise LedgerError("historique de parts incompatible avec le regroupement")
                shares = transformed // denominator
        return shares

    def apply_reverse_split(
        self,
        symbol: str,
        *,
        effective_date: date,
        old_shares: int,
        new_shares: int,
    ) -> None:
        symbol = self._valid_symbol(symbol)
        key = (symbol, effective_date, new_shares, old_shares)
        try:
            self._validate_effect_time(
                effective_date, EventPhase.CORPORATE_ACTION, operation="REVERSE_SPLIT"
            )
            if type(old_shares) is not int or type(new_shares) is not int:
                raise LedgerError("le ratio de regroupement doit être entier")
            if old_shares <= 0 or new_shares <= 0 or new_shares >= old_shares:
                raise LedgerError("ratio de regroupement invalide")
            if key in self._applied_splits:
                raise LedgerError("ce regroupement a déjà été appliqué")
            prior_events = self._position_events.get(symbol, [])
            if prior_events and effective_date < max(event[0] for event in prior_events):
                raise LedgerError("un regroupement ne peut pas être antidaté")
            if any(item.symbol == symbol for item in self.pending_settlements):
                raise LedgerError("regroupement refusé avec titres en cours de règlement")
            economic = self.economic_positions.get(symbol, 0)
            settled = self.settled_positions.get(symbol, 0)
            if economic * new_shares % old_shares or settled * new_shares % old_shares:
                raise LedgerError("le regroupement créerait une part fractionnaire")
            if symbol not in self.market_prices:
                raise LedgerError("prix de marché absent pour le regroupement")
        except LedgerError as exc:
            self._reject("REVERSE_SPLIT", str(exc), effective_date)

        self.economic_positions[symbol] = economic * new_shares // old_shares
        self.settled_positions[symbol] = settled * new_shares // old_shares
        price_factor = Decimal(old_shares) / Decimal(new_shares)
        self.market_prices[symbol] *= price_factor
        if symbol in self.nav_prices:
            self.nav_prices[symbol] *= price_factor
        self._applied_splits.add(key)
        seq = self._next_sequence()
        self._position_events.setdefault(symbol, []).append(
            (effective_date, seq, "SPLIT", (new_shares, old_shares))
        )
        self.journal.append(
            JournalEntry(
                seq,
                effective_date,
                "REVERSE_SPLIT",
                {"symbol": symbol, "old_shares": old_shares, "new_shares": new_shares},
            )
        )
        self.assert_invariants()
        self._commit_effect_time(effective_date, EventPhase.CORPORATE_ACTION)

    def assert_invariants(self) -> None:
        if self.settled_cash < ZERO:
            raise AssertionError("cash réglé négatif")
        if any(type(quantity) is not int or quantity < 0 for quantity in self.economic_positions.values()):
            raise AssertionError("position économique invalide")
        if any(type(quantity) is not int or quantity < 0 for quantity in self.settled_positions.values()):
            raise AssertionError("position réglée invalide")
        symbols = set(self.economic_positions) | set(self.settled_positions)
        for symbol in symbols:
            pending_quantity = sum(
                item.quantity for item in self.pending_settlements if item.symbol == symbol
            )
            if self.settled_positions.get(symbol, 0) + pending_quantity != self.economic_positions.get(symbol, 0):
                raise AssertionError(f"identité titres/règlement violée pour {symbol}")
        if self.purchase_payables < ZERO or self.sale_receivables < ZERO:
            raise AssertionError("compte de règlement négatif")
        if self.distribution_receivables < ZERO:
            raise AssertionError("créance de distribution négative")


__all__ = [
    "AccountingSnapshot",
    "DistributionClaim",
    "DistributionAnnouncement",
    "EventPhase",
    "ExecutionRequest",
    "FixedOrder",
    "FundingConvention",
    "JournalEntry",
    "LedgerError",
    "PendingSettlement",
    "SyntheticPortfolioLedger",
    "SyntheticSettlementCalendar",
    "SyntheticTradingCalendar",
    "TRANSITION_T1",
    "whole_share_quantity",
]
