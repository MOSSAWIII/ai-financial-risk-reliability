from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "synthetic_spy_bil_v1.json"
sys.path.insert(0, str(SCRIPTS))

from synthetic_decision_adapter import (  # noqa: E402
    ExecutionStatus,
    FundingSource,
)
from synthetic_input_boundary import (  # noqa: E402
    BoundaryError,
    SyntheticIntentJournal,
    build_synthetic_components,
    load_synthetic_fixture,
    run_synthetic_scenario,
)


def fixture_document() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def write_verified_fixture(directory: Path, document: dict, *, name: str = "case.json") -> Path:
    path = directory / name
    raw = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{digest}  {path.name}\n", encoding="ascii"
    )
    return path


def test_fixture_exact_bytes_match_published_sha256() -> None:
    raw = FIXTURE.read_bytes()
    expected, filename = FIXTURE.with_suffix(".json.sha256").read_text(
        encoding="ascii"
    ).split()
    assert expected == "24b752be3b700dc2c4a5d1d17a74164f8c8e5708b3dfb049569d0c64c7386440"
    assert filename == FIXTURE.name
    assert hashlib.sha256(raw).hexdigest() == expected
    scenario = load_synthetic_fixture(FIXTURE)
    assert scenario.fixture_sha256 == expected
    assert scenario.provenance == "SYNTHETIC"


def test_complete_synthetic_sequence_preserves_financial_contract(tmp_path: Path) -> None:
    scenario = load_synthetic_fixture(FIXTURE)
    journal_path = tmp_path / "intent-journal.json"
    run = run_synthetic_scenario(scenario, journal_path=journal_path)

    assert [item.status for item in run.outcomes] == [
        ExecutionStatus.EXECUTED_HYPOTHETICAL,
        ExecutionStatus.EXECUTED_HYPOTHETICAL,
        ExecutionStatus.ECONOMIC_ORDER_REJECTED,
    ]
    assert run.outcomes[0].intent.target_quantities == {"SPY": 0, "BIL": 100}
    assert run.outcomes[1].intent.target_quantities == {"SPY": 50, "BIL": 50}
    assert run.outcomes[1].funding_source is FundingSource.UNSETTLED_SALE_PROCEEDS
    assert run.outcomes[1].settlement_date.isoformat() == "2023-01-11"
    assert "SPY" in run.outcomes[2].reason
    assert run.outcomes[2].accounting_before == run.outcomes[2].accounting_after
    assert run.final_snapshot.settled_cash == 50
    assert run.final_snapshot.economic_positions == {"SPY": 50, "BIL": 50}
    assert run.final_snapshot.settled_positions == {"SPY": 50, "BIL": 50}
    assert run.final_snapshot.sale_receivables == 0
    assert run.final_snapshot.purchase_payables == 0
    assert run.final_snapshot.pending_settlement_count == 0
    assert run.final_wealth == 10000
    assert journal_path.exists()


def test_two_full_replays_from_known_initial_state_are_identical(tmp_path: Path) -> None:
    scenario_a = load_synthetic_fixture(FIXTURE)
    scenario_b = load_synthetic_fixture(FIXTURE)
    run_a = run_synthetic_scenario(scenario_a, journal_path=tmp_path / "a.json")
    run_b = run_synthetic_scenario(scenario_b, journal_path=tmp_path / "b.json")
    assert run_a.signature() == run_b.signature()
    assert [item.intent.intent_id for item in run_a.outcomes] == [
        item.intent.intent_id for item in run_b.outcomes
    ]


def test_fixture_byte_change_after_validation_is_detected(tmp_path: Path) -> None:
    path = tmp_path / "changed.json"
    original = FIXTURE.read_bytes()
    path.write_bytes(original)
    path.with_suffix(".json.sha256").write_text(
        f"{hashlib.sha256(original).hexdigest()}  changed.json\n", encoding="ascii"
    )
    load_synthetic_fixture(path)
    path.write_bytes(original + b" ")
    with pytest.raises(BoundaryError, match="empreinte SHA-256"):
        load_synthetic_fixture(path)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda doc: doc.update(schema_version="unknown/v9"), "schéma"),
        (lambda doc: doc.update(provenance="MARKET"), "provenance"),
        (
            lambda doc: doc["decisions"][0].update(decision_date="03/01/2023"),
            "date ISO",
        ),
        (
            lambda doc: doc["initial_state"].update(cash=10000),
            "chaîne non vide",
        ),
        (
            lambda doc: doc["initial_state"]["positions"].update(UNKNOWN=0),
            "exactement SPY et BIL",
        ),
        (
            lambda doc: doc["decisions"][0].update(
                documentary_status="CLEAR", anomalies=["PRICE_DISPUTED"]
            ),
            "contradictoire",
        ),
        (
            lambda doc: doc["decisions"][0]["execution_opens"]["SPY"].update(
                value="0"
            ),
            "strictement positif",
        ),
        (
            lambda doc: doc["calendars"].update(settlement=[]),
            "calendrier artificiel est vide",
        ),
    ],
)
def test_invalid_fixture_contract_is_rejected(
    tmp_path: Path, mutator, message: str
) -> None:
    document = fixture_document()
    mutator(document)
    path = write_verified_fixture(tmp_path, document)
    with pytest.raises(BoundaryError, match=message):
        load_synthetic_fixture(path)


def test_unknown_field_is_not_silently_ignored(tmp_path: Path) -> None:
    document = fixture_document()
    document["decisions"][0]["future_open_for_sizing"] = "999"
    path = write_verified_fixture(tmp_path, document)
    with pytest.raises(BoundaryError, match="inattendus"):
        load_synthetic_fixture(path)


def test_terminal_journal_reloads_and_blocks_second_execution(tmp_path: Path) -> None:
    scenario = load_synthetic_fixture(FIXTURE)
    journal_path = tmp_path / "journal.json"
    first_run = run_synthetic_scenario(scenario, journal_path=journal_path)
    journal = SyntheticIntentJournal(journal_path)
    first_id = first_run.outcomes[0].intent.intent_id
    assert journal.terminal_status(first_id) == "EXECUTED_HYPOTHETICAL"

    ledger, adapter = build_synthetic_components(scenario, journal_path=journal_path)
    spec = scenario.decisions[0]
    intent = adapter.prepare_intent(
        decision_date=spec.decision_date,
        known_market_wealth=spec.known_market_wealth,
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes=spec.decision_closes,
        target_weight_spy=spec.target_weight_spy,
    )
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        intent,
        execution_date=spec.execution_date,
        execution_opens=spec.execution_opens,
        fees=spec.fees,
    )
    assert intent.intent_id == first_id
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert "terminal persistant" in outcome.reason
    assert outcome.accounting_before == outcome.accounting_after == before


def test_reused_persisted_identifier_with_changed_content_is_rejected(
    tmp_path: Path,
) -> None:
    scenario = load_synthetic_fixture(FIXTURE)
    journal_path = tmp_path / "journal.json"
    first_run = run_synthetic_scenario(scenario, journal_path=journal_path)
    ledger, adapter = build_synthetic_components(scenario, journal_path=journal_path)
    original = first_run.outcomes[0].intent
    forged = replace(original, target_weight_spy=original.target_weight_spy + 1)
    before = ledger.accounting_snapshot()
    outcome = adapter.process_intent(
        forged,
        execution_date=scenario.decisions[0].execution_date,
        execution_opens=scenario.decisions[0].execution_opens,
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert outcome.accounting_before == outcome.accounting_after == before


def test_incomplete_persistent_entry_is_detected(tmp_path: Path) -> None:
    scenario = load_synthetic_fixture(FIXTURE)
    journal_path = tmp_path / "incomplete.json"
    _, adapter = build_synthetic_components(scenario, journal_path=journal_path)
    spec = scenario.decisions[0]
    adapter.prepare_intent(
        decision_date=spec.decision_date,
        known_market_wealth=spec.known_market_wealth,
        inherited_positions={"SPY": 0, "BIL": 0},
        decision_closes=spec.decision_closes,
        target_weight_spy=spec.target_weight_spy,
    )
    with pytest.raises(BoundaryError, match="résultat terminal absent"):
        SyntheticIntentJournal(journal_path)


def test_altered_persistent_result_is_detected(tmp_path: Path) -> None:
    scenario = load_synthetic_fixture(FIXTURE)
    journal_path = tmp_path / "journal.json"
    run_synthetic_scenario(scenario, journal_path=journal_path)
    document = json.loads(journal_path.read_text(encoding="utf-8"))
    first = next(iter(document["entries"].values()))
    first["terminal"]["status"] = "VOLUNTARY_HOLD"
    journal_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(BoundaryError, match="intégrité"):
        SyntheticIntentJournal(journal_path)


def test_fixture_contains_no_external_market_provenance_or_known_anomaly() -> None:
    document = fixture_document()
    serialized = json.dumps(document).lower()
    assert document["provenance"] == "SYNTHETIC"
    assert "yahoo" not in serialized
    assert "nasdaq" not in serialized
    assert "state street" not in serialized
    assert "2026-04-20" not in serialized
