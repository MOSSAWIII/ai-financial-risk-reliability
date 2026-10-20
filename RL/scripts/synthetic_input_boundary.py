#!/usr/bin/env python3
"""Frontière JSON minimale pour scénarios SPY/BIL entièrement artificiels."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from synthetic_decision_adapter import (
    DatedPrice,
    DecisionIntent,
    ExecutionOutcome,
    ExecutionStatus,
    PriceStatus,
    SyntheticDecisionAdapter,
    canonical_json_bytes,
    intent_content_sha256,
    intent_payload,
)
from synthetic_portfolio_ledger import (
    AccountingSnapshot,
    LedgerError,
    SyntheticPortfolioLedger,
    SyntheticSettlementCalendar,
    SyntheticTradingCalendar,
)


SCHEMA_VERSION = "synthetic_spy_bil_input/v1"
JOURNAL_VERSION = "synthetic_intent_journal/v1"
SYMBOLS = ("SPY", "BIL")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DECIMAL_PATTERN = re.compile(r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class BoundaryError(ValueError):
    """Fixture ou journal incompatible avec le schéma synthétique v1."""


@dataclass(frozen=True)
class SyntheticDecisionSpec:
    decision_key: str
    decision_date: date
    known_market_wealth: Decimal
    decision_closes: Mapping[str, DatedPrice]
    target_weight_spy: Decimal
    execution_date: date
    execution_opens: Mapping[str, DatedPrice]
    fees: Mapping[str, Decimal]
    documentary_status: str
    anomalies: tuple[str, ...]
    settle_after: tuple[date, ...]
    expected_status: ExecutionStatus


@dataclass(frozen=True)
class SyntheticScenario:
    schema_version: str
    scenario_id: str
    provenance: str
    fixture_sha256: str
    trading_dates: tuple[date, ...]
    settlement_dates: tuple[date, ...]
    initial_cash: Decimal
    initial_positions: Mapping[str, int]
    decisions: tuple[SyntheticDecisionSpec, ...]


@dataclass(frozen=True)
class ScenarioRun:
    scenario_id: str
    fixture_sha256: str
    outcomes: tuple[ExecutionOutcome, ...]
    settlement_groups: tuple[tuple[date, tuple[int, ...]], ...]
    final_snapshot: AccountingSnapshot
    final_wealth: Decimal

    def signature(self) -> Mapping[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "fixture_sha256": self.fixture_sha256,
            "outcomes": [_outcome_record(item) for item in self.outcomes],
            "settlement_groups": [
                {"date": item_date.isoformat(), "ids": list(ids)}
                for item_date, ids in self.settlement_groups
            ],
            "final_snapshot": _snapshot_record(self.final_snapshot),
            "final_wealth": _decimal_text(self.final_wealth),
        }


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def _strict_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise BoundaryError(f"{label}: champs absents={missing}, inattendus={extra}")


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise BoundaryError(f"{label} doit être un objet JSON")
    return value


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise BoundaryError(f"{label} doit être une liste JSON")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise BoundaryError(f"{label} doit être une chaîne non vide")
    return value


def _date(value: Any, label: str) -> date:
    text = _text(value, label)
    if not DATE_PATTERN.fullmatch(text):
        raise BoundaryError(f"{label} doit être une date ISO YYYY-MM-DD")
    try:
        result = date.fromisoformat(text)
    except ValueError as exc:
        raise BoundaryError(f"{label} est une date impossible") from exc
    if result.isoformat() != text:
        raise BoundaryError(f"{label} n'est pas une date ISO canonique")
    return result


def _decimal(value: Any, label: str, *, nonnegative: bool = True) -> Decimal:
    text = _text(value, label)
    if not DECIMAL_PATTERN.fullmatch(text):
        raise BoundaryError(f"{label} doit être un décimal textuel sans exposant")
    try:
        result = Decimal(text)
    except InvalidOperation as exc:
        raise BoundaryError(f"{label} est un décimal invalide") from exc
    if not result.is_finite() or (nonnegative and result < 0):
        raise BoundaryError(f"{label} doit être fini et non négatif")
    return result


def _integer(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise BoundaryError(f"{label} doit être un entier non négatif")
    return value


def _symbol_mapping(value: Any, label: str) -> Mapping[str, Any]:
    result = _mapping(value, label)
    if set(result) != set(SYMBOLS):
        raise BoundaryError(f"{label} doit contenir exactement SPY et BIL")
    return result


def _price(value: Any, label: str) -> DatedPrice:
    raw = _mapping(value, label)
    _strict_keys(raw, {"date", "value", "status"}, label)
    try:
        status = PriceStatus(_text(raw["status"], f"{label}.status"))
    except ValueError as exc:
        raise BoundaryError(f"{label}.status est inconnu") from exc
    price_date = _date(raw["date"], f"{label}.date")
    if status is PriceStatus.AVAILABLE:
        amount = _decimal(raw["value"], f"{label}.value")
        if amount <= 0:
            raise BoundaryError(f"{label}.value doit être strictement positif")
    else:
        if raw["value"] is not None:
            raise BoundaryError(f"{label}.value doit être null si le prix est indisponible")
        amount = None
    return DatedPrice(price_date, amount, status)


def _read_verified_bytes(path: Path) -> tuple[bytes, str]:
    if path.suffix.lower() != ".json":
        raise BoundaryError("le fixture doit être un fichier JSON")
    try:
        raw = path.read_bytes()
        sidecar = path.with_suffix(path.suffix + ".sha256").read_text(encoding="ascii")
    except OSError as exc:
        raise BoundaryError("fixture ou fichier SHA-256 inaccessible") from exc
    parts = sidecar.strip().split()
    if len(parts) != 2 or parts[1] != path.name or not SHA256_PATTERN.fullmatch(parts[0]):
        raise BoundaryError("fichier SHA-256 mal formé")
    actual = hashlib.sha256(raw).hexdigest()
    if actual != parts[0]:
        raise BoundaryError("empreinte SHA-256 du fixture incorrecte")
    return raw, actual


def load_synthetic_fixture(path: str | Path) -> SyntheticScenario:
    fixture_path = Path(path)
    raw_bytes, fixture_hash = _read_verified_bytes(fixture_path)
    try:
        document = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("fixture JSON UTF-8 invalide") from exc
    root = _mapping(document, "racine")
    _strict_keys(
        root,
        {
            "schema_version",
            "scenario_id",
            "provenance",
            "calendars",
            "initial_state",
            "decisions",
        },
        "racine",
    )
    schema = _text(root["schema_version"], "schema_version")
    if schema != SCHEMA_VERSION:
        raise BoundaryError("version de schéma non reconnue")
    scenario_id = _text(root["scenario_id"], "scenario_id")
    provenance = _text(root["provenance"], "provenance")
    if provenance != "SYNTHETIC":
        raise BoundaryError("la provenance doit être exactement SYNTHETIC")

    calendars = _mapping(root["calendars"], "calendars")
    _strict_keys(calendars, {"trading", "settlement"}, "calendars")
    trading_dates = tuple(
        _date(item, f"calendars.trading[{index}]")
        for index, item in enumerate(_list(calendars["trading"], "calendars.trading"))
    )
    settlement_dates = tuple(
        _date(item, f"calendars.settlement[{index}]")
        for index, item in enumerate(
            _list(calendars["settlement"], "calendars.settlement")
        )
    )
    if tuple(sorted(set(trading_dates))) != trading_dates:
        raise BoundaryError("calendrier de négociation non trié ou dupliqué")
    if tuple(sorted(set(settlement_dates))) != settlement_dates:
        raise BoundaryError("calendrier de règlement non trié ou dupliqué")
    try:
        SyntheticTradingCalendar(trading_dates)
        SyntheticSettlementCalendar(settlement_dates)
    except LedgerError as exc:
        raise BoundaryError(str(exc)) from exc

    initial = _mapping(root["initial_state"], "initial_state")
    _strict_keys(initial, {"cash", "positions"}, "initial_state")
    initial_cash = _decimal(initial["cash"], "initial_state.cash")
    positions_raw = _symbol_mapping(initial["positions"], "initial_state.positions")
    initial_positions = {
        symbol: _integer(positions_raw[symbol], f"initial_state.positions.{symbol}")
        for symbol in SYMBOLS
    }
    if any(initial_positions.values()):
        raise BoundaryError("le schéma v1 exige des positions initiales nulles")

    decisions = tuple(
        _decision(item, index)
        for index, item in enumerate(_list(root["decisions"], "decisions"))
    )
    if not decisions:
        raise BoundaryError("le fixture doit contenir au moins une décision")
    keys = [item.decision_key for item in decisions]
    if len(keys) != len(set(keys)):
        raise BoundaryError("decision_key dupliqué")
    return SyntheticScenario(
        schema,
        scenario_id,
        provenance,
        fixture_hash,
        trading_dates,
        settlement_dates,
        initial_cash,
        initial_positions,
        decisions,
    )


def _decision(value: Any, index: int) -> SyntheticDecisionSpec:
    label = f"decisions[{index}]"
    raw = _mapping(value, label)
    _strict_keys(
        raw,
        {
            "decision_key",
            "decision_date",
            "known_market_wealth",
            "decision_closes",
            "target_weight_spy",
            "execution_date",
            "execution_opens",
            "fees",
            "documentary_status",
            "anomalies",
            "settle_after",
            "expected_status",
        },
        label,
    )
    decision_date = _date(raw["decision_date"], f"{label}.decision_date")
    execution_date = _date(raw["execution_date"], f"{label}.execution_date")
    closes_raw = _symbol_mapping(raw["decision_closes"], f"{label}.decision_closes")
    opens_raw = _symbol_mapping(raw["execution_opens"], f"{label}.execution_opens")
    closes = {symbol: _price(closes_raw[symbol], f"{label}.closes.{symbol}") for symbol in SYMBOLS}
    opens = {symbol: _price(opens_raw[symbol], f"{label}.opens.{symbol}") for symbol in SYMBOLS}
    if any(item.price_date != decision_date for item in closes.values()):
        raise BoundaryError(f"{label}: une clôture n'est pas datée de la décision")
    if any(item.price_date != execution_date for item in opens.values()):
        raise BoundaryError(f"{label}: un open n'est pas daté de l'exécution")
    fees_raw = _symbol_mapping(raw["fees"], f"{label}.fees")
    fees = {symbol: _decimal(fees_raw[symbol], f"{label}.fees.{symbol}") for symbol in SYMBOLS}
    weight = _decimal(raw["target_weight_spy"], f"{label}.target_weight_spy")
    if weight > 1:
        raise BoundaryError(f"{label}.target_weight_spy doit appartenir à [0, 1]")
    documentary_status = _text(raw["documentary_status"], f"{label}.documentary_status")
    if documentary_status not in {"CLEAR", "BLOCKED"}:
        raise BoundaryError(f"{label}.documentary_status inconnu")
    anomalies = tuple(
        _text(item, f"{label}.anomalies[{item_index}]")
        for item_index, item in enumerate(_list(raw["anomalies"], f"{label}.anomalies"))
    )
    if (documentary_status == "CLEAR") != (not anomalies):
        raise BoundaryError(f"{label}: statut documentaire contradictoire")
    try:
        expected = ExecutionStatus(_text(raw["expected_status"], f"{label}.expected_status"))
    except ValueError as exc:
        raise BoundaryError(f"{label}.expected_status inconnu") from exc
    return SyntheticDecisionSpec(
        decision_key=_text(raw["decision_key"], f"{label}.decision_key"),
        decision_date=decision_date,
        known_market_wealth=_decimal(
            raw["known_market_wealth"], f"{label}.known_market_wealth"
        ),
        decision_closes=closes,
        target_weight_spy=weight,
        execution_date=execution_date,
        execution_opens=opens,
        fees=fees,
        documentary_status=documentary_status,
        anomalies=anomalies,
        settle_after=tuple(
            _date(item, f"{label}.settle_after[{item_index}]")
            for item_index, item in enumerate(
                _list(raw["settle_after"], f"{label}.settle_after")
            )
        ),
        expected_status=expected,
    )


class SyntheticIntentJournal:
    """Journal terminal intègre ; il ne restaure pas l'état du registre."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.entries: dict[str, dict[str, Any]] = {}
        if self.path.exists():
            self._load()

    def _envelope(self) -> dict[str, Any]:
        return {"schema_version": JOURNAL_VERSION, "entries": self.entries}

    def _save(self) -> None:
        envelope = self._envelope()
        digest = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
        document = {
            **envelope,
            "integrity": {"algorithm": "SHA-256", "content_sha256": digest},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def _load(self) -> None:
        try:
            document = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BoundaryError("journal persistant illisible") from exc
        root = _mapping(document, "journal")
        _strict_keys(root, {"schema_version", "entries", "integrity"}, "journal")
        if root["schema_version"] != JOURNAL_VERSION:
            raise BoundaryError("version du journal persisté inconnue")
        integrity = _mapping(root["integrity"], "journal.integrity")
        _strict_keys(integrity, {"algorithm", "content_sha256"}, "journal.integrity")
        if integrity["algorithm"] != "SHA-256":
            raise BoundaryError("algorithme d'intégrité du journal inconnu")
        envelope = {"schema_version": root["schema_version"], "entries": root["entries"]}
        actual = hashlib.sha256(canonical_json_bytes(envelope)).hexdigest()
        if integrity["content_sha256"] != actual:
            raise BoundaryError("intégrité du journal persistant invalide")
        entries = _mapping(root["entries"], "journal.entries")
        for intent_id, entry_value in entries.items():
            entry = _mapping(entry_value, f"journal.entries.{intent_id}")
            _strict_keys(
                entry,
                {"intent_sha256", "intent_payload", "terminal"},
                f"journal.entries.{intent_id}",
            )
            digest = entry["intent_sha256"]
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                raise BoundaryError("empreinte d'intention persistée invalide")
            payload = _mapping(entry["intent_payload"], "intent_payload")
            if hashlib.sha256(canonical_json_bytes(payload)).hexdigest() != digest:
                raise BoundaryError("contenu d'intention persisté altéré")
            if intent_id != f"INTENT-{digest}":
                raise BoundaryError("identifiant d'intention persisté incohérent")
            if entry["terminal"] is None:
                raise BoundaryError("journal persistant incomplet : résultat terminal absent")
            terminal = _mapping(entry["terminal"], "terminal")
            if terminal.get("intent_sha256") != digest or "status" not in terminal:
                raise BoundaryError("résultat terminal persisté incohérent")
            try:
                ExecutionStatus(terminal["status"])
            except (TypeError, ValueError) as exc:
                raise BoundaryError("statut terminal persisté inconnu") from exc
        self.entries = {key: dict(value) for key, value in entries.items()}

    def register_intent(self, intent: DecisionIntent) -> None:
        digest = intent_content_sha256(intent)
        payload = intent_payload(intent)
        if intent.content_sha256 != digest or intent.intent_id != f"INTENT-{digest}":
            raise BoundaryError("intention non canonique refusée par le journal")
        existing = self.entries.get(intent.intent_id)
        if existing is not None:
            if existing["intent_sha256"] != digest or existing["intent_payload"] != payload:
                raise BoundaryError("identifiant persistant réutilisé avec un contenu différent")
            return
        self.entries[intent.intent_id] = {
            "intent_sha256": digest,
            "intent_payload": payload,
            "terminal": None,
        }
        self._save()

    def intent_sha256(self, intent_id: str) -> str | None:
        entry = self.entries.get(intent_id)
        return None if entry is None else str(entry["intent_sha256"])

    def terminal_status(self, intent_id: str) -> str | None:
        entry = self.entries.get(intent_id)
        if entry is None or entry["terminal"] is None:
            return None
        return str(entry["terminal"]["status"])

    def record_terminal(self, outcome: ExecutionOutcome) -> None:
        entry = self.entries.get(outcome.intent.intent_id)
        if entry is None:
            raise BoundaryError("résultat terminal sans intention persistée")
        if entry["intent_sha256"] != outcome.intent.content_sha256:
            raise BoundaryError("résultat terminal associé à une autre intention")
        if entry["terminal"] is not None:
            raise BoundaryError("résultat terminal déjà persisté")
        entry["terminal"] = _outcome_record(outcome)
        self._save()


def _snapshot_record(snapshot: AccountingSnapshot) -> dict[str, Any]:
    return {
        "settled_cash": _decimal_text(snapshot.settled_cash),
        "economic_positions": dict(sorted(snapshot.economic_positions.items())),
        "settled_positions": dict(sorted(snapshot.settled_positions.items())),
        "sale_receivables": _decimal_text(snapshot.sale_receivables),
        "purchase_payables": _decimal_text(snapshot.purchase_payables),
        "distribution_receivables": _decimal_text(snapshot.distribution_receivables),
        "fees_recognized": _decimal_text(snapshot.fees_recognized),
        "pending_settlement_count": snapshot.pending_settlement_count,
        "unpaid_distribution_count": snapshot.unpaid_distribution_count,
    }


def _outcome_record(outcome: ExecutionOutcome) -> dict[str, Any]:
    return {
        "intent_id": outcome.intent.intent_id,
        "intent_sha256": outcome.intent.content_sha256,
        "status": outcome.status.value,
        "reason": outcome.reason,
        "execution_date": outcome.execution_date.isoformat(),
        "settlement_date": (
            None if outcome.settlement_date is None else outcome.settlement_date.isoformat()
        ),
        "execution_prices": {
            key: _decimal_text(value) for key, value in sorted(outcome.execution_prices.items())
        },
        "fees": {key: _decimal_text(value) for key, value in sorted(outcome.fees.items())},
        "funding_source": outcome.funding_source.value,
        "accounting_before": _snapshot_record(outcome.accounting_before),
        "accounting_after": _snapshot_record(outcome.accounting_after),
        "wealth_before_trade": (
            None
            if outcome.wealth_before_trade is None
            else _decimal_text(outcome.wealth_before_trade)
        ),
        "wealth_after_trade": (
            None
            if outcome.wealth_after_trade is None
            else _decimal_text(outcome.wealth_after_trade)
        ),
        "settlement_ids": list(outcome.settlement_ids),
    }


def build_synthetic_components(
    scenario: SyntheticScenario,
    *,
    journal_path: str | Path | None = None,
) -> tuple[SyntheticPortfolioLedger, SyntheticDecisionAdapter]:
    if any(scenario.initial_positions.values()):
        raise BoundaryError("positions initiales non nulles non prises en charge en v1")
    ledger = SyntheticPortfolioLedger(
        scenario.initial_cash,
        strict_temporal=True,
        trading_calendar=SyntheticTradingCalendar(scenario.trading_dates),
        settlement_calendar=SyntheticSettlementCalendar(scenario.settlement_dates),
    )
    journal = None if journal_path is None else SyntheticIntentJournal(journal_path)
    return ledger, SyntheticDecisionAdapter(ledger, persistence=journal)


def run_synthetic_scenario(
    scenario: SyntheticScenario,
    *,
    journal_path: str | Path | None = None,
    enforce_expected: bool = True,
) -> ScenarioRun:
    ledger, adapter = build_synthetic_components(scenario, journal_path=journal_path)
    outcomes: list[ExecutionOutcome] = []
    settlement_groups: list[tuple[date, tuple[int, ...]]] = []
    for spec in scenario.decisions:
        intent = adapter.prepare_intent(
            decision_date=spec.decision_date,
            known_market_wealth=spec.known_market_wealth,
            inherited_positions={
                symbol: ledger.economic_positions.get(symbol, 0) for symbol in SYMBOLS
            },
            decision_closes=spec.decision_closes,
            target_weight_spy=spec.target_weight_spy,
        )
        documentary_issue = (
            None
            if spec.documentary_status == "CLEAR"
            else "; ".join(spec.anomalies)
        )
        outcome = adapter.process_intent(
            intent,
            execution_date=spec.execution_date,
            execution_opens=spec.execution_opens,
            fees=spec.fees,
            documentary_issue=documentary_issue,
        )
        if enforce_expected and outcome.status is not spec.expected_status:
            raise BoundaryError(
                f"{spec.decision_key}: statut {outcome.status.value}, "
                f"attendu {spec.expected_status.value}"
            )
        outcomes.append(outcome)
        for settlement_date in spec.settle_after:
            try:
                settled_ids = tuple(ledger.settle_through(settlement_date))
            except LedgerError as exc:
                raise BoundaryError(
                    f"{spec.decision_key}: règlement artificiel invalide"
                ) from exc
            settlement_groups.append((settlement_date, settled_ids))
    ledger.assert_invariants()
    return ScenarioRun(
        scenario.scenario_id,
        scenario.fixture_sha256,
        tuple(outcomes),
        tuple(settlement_groups),
        ledger.accounting_snapshot(),
        ledger.wealth_market(),
    )


__all__ = [
    "BoundaryError",
    "JOURNAL_VERSION",
    "SCHEMA_VERSION",
    "ScenarioRun",
    "SyntheticDecisionSpec",
    "SyntheticIntentJournal",
    "SyntheticScenario",
    "build_synthetic_components",
    "load_synthetic_fixture",
    "run_synthetic_scenario",
]
