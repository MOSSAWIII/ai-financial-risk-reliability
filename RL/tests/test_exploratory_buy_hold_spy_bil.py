from __future__ import annotations

import sys
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
CONFIG = (
    ROOT / "RL" / "tests" / "fixtures" / "exploratory_buy_hold_spy_bil_v1.json"
)
sys.path.insert(0, str(SCRIPTS))

import exploratory_buy_hold_spy_bil as evaluation  # noqa: E402
from exploratory_buy_hold_spy_bil import (  # noqa: E402
    DocumentaryBlock,
    CostScenario,
    EpisodeContract,
    EpisodeData,
    EvaluationVerdict,
    PolicyDefinition,
    ValuationRow,
    calculate_path_metrics,
    audit_session_coverage,
    evaluate_cost_sensitivity,
    evaluate_policy,
    run_evaluation,
    validate_distribution_events,
)


D = Decimal


def artificial_contract() -> EpisodeContract:
    return EpisodeContract(
        "artificial-a-b-c1",
        "0" * 64,
        date(2024, 5, 28),
        datetime(2024, 5, 29, 8, tzinfo=ZoneInfo("America/New_York")),
        date(2024, 5, 29),
        date(2024, 5, 30),
        date(2024, 6, 5),
        D("100000"),
        (
            PolicyDefinition("A", "BUY_AND_HOLD_SPY", D("1")),
            PolicyDefinition("B", "BUY_AND_HOLD_BIL", D("0")),
            PolicyDefinition("C1", "BUY_AND_HOLD_50_50", D("0.5")),
        ),
        (
            CostScenario("S0", D("0")),
            CostScenario("S1", D("1")),
            CostScenario("S2", D("5")),
            CostScenario("S3", D("10")),
        ),
        {},
        252,
        365,
    )


def artificial_data() -> EpisodeData:
    sessions = (
        date(2024, 5, 29),
        date(2024, 5, 30),
        date(2024, 5, 31),
        date(2024, 6, 3),
        date(2024, 6, 4),
        date(2024, 6, 5),
    )
    spy = [D("100"), D("90"), D("80"), D("100"), D("110"), D("105")]
    return EpisodeData(
        sessions[-1],
        sessions,
        {"SPY": D("100"), "BIL": D("100")},
        {"SPY": D("100"), "BIL": D("100")},
        {
            current: {"SPY": spy[index], "BIL": D("100")}
            for index, current in enumerate(sessions)
        },
        (
            evaluation.DistributionEvent(
                "ART-SPY-20240531",
                "SPY",
                date(2024, 5, 31),
                date(2024, 5, 31),
                date(2024, 6, 2),
                D("2"),
            ),
        ),
        {},
    )


def test_artificial_hold_keeps_quantities_and_has_no_extra_orders() -> None:
    result = evaluate_policy(
        artificial_contract(), artificial_data(), artificial_contract().policies[0]
    )
    assert result.quantities == {"SPY": 1000, "BIL": 0}
    assert result.initial_orders == 1
    assert result.initial_lots == 1
    assert result.settled_ids == (1,)
    assert result.economic_rejections == 0
    assert result.terminal_wealth == D("107000")


def test_artificial_distribution_becomes_cash_without_reinvestment() -> None:
    result = evaluate_policy(
        artificial_contract(), artificial_data(), artificial_contract().policies[0]
    )
    assert result.quantities["SPY"] == 1000
    assert result.distribution_contributions["SPY"] == D("2000")
    assert result.terminal_cash == D("2000")
    assert result.trajectory[-1].distribution_receivable == 0
    assert result.distribution_accounting[0]["payment_date"] == "2024-06-02"
    assert result.distribution_accounting[0]["paid_amount"] == "2000"


def test_expected_session_missing_for_one_instrument_is_blocking() -> None:
    expected = (date(2024, 5, 29), date(2024, 5, 30))
    with pytest.raises(DocumentaryBlock, match="SPY=2024-05-30"):
        audit_session_coverage(expected, {expected[0]}, set(expected))


def test_expected_session_missing_for_both_instruments_is_blocking() -> None:
    expected = (date(2024, 5, 29), date(2024, 5, 30))
    with pytest.raises(DocumentaryBlock) as exc_info:
        audit_session_coverage(expected, {expected[0]}, {expected[0]})
    assert "SPY=2024-05-30" in str(exc_info.value)
    assert "BIL=2024-05-30" in str(exc_info.value)


def test_distribution_inventory_rejects_missing_and_duplicate_events() -> None:
    event = artificial_data().distributions[0]
    with pytest.raises(DocumentaryBlock, match="incomplet"):
        validate_distribution_events((event,), expected_ids={event.event_id, "MISSING"})
    with pytest.raises(DocumentaryBlock, match="dupliquée"):
        validate_distribution_events((event, event))


def test_independent_wealth_reconciliation_uses_direct_components() -> None:
    result = evaluate_policy(
        artificial_contract(), artificial_data(), artificial_contract().policies[0]
    )
    reconciliation = result.independent_reconciliation
    assert reconciliation["terminal_position_value"] == D("105000")
    assert reconciliation["initial_residual_cash_before_cost"] == 0
    assert reconciliation["distributions_acquired"] == D("2000")
    assert reconciliation["reconstructed_terminal_wealth"] == D("107000")
    assert reconciliation["difference"] == 0


def test_cost_is_deducted_once_without_changing_quantities_or_dates() -> None:
    data = replace(
        artificial_data(), decision_closes={"SPY": D("101"), "BIL": D("101")}
    )
    contract = artificial_contract()
    baseline = evaluate_policy(contract, data, contract.policies[0])
    costly = evaluate_policy(
        contract,
        data,
        contract.policies[0],
        cost_scenario=CostScenario("S3", D("10")),
        expected_quantities=baseline.quantities,
    )
    assert baseline.quantities == costly.quantities == {"SPY": 990, "BIL": 0}
    assert costly.initial_cost == D("99")
    assert costly.terminal_wealth == baseline.terminal_wealth - D("99")
    assert costly.independent_reconciliation["applicable_costs"] == D("99")
    assert [row.valuation_date for row in costly.trajectory] == [
        row.valuation_date for row in baseline.trajectory
    ]


def test_unfunded_cost_rejects_whole_lot_without_resizing() -> None:
    contract = artificial_contract()
    data = artificial_data()
    baseline = tuple(
        evaluate_policy(contract, data, policy) for policy in contract.policies
    )
    scenarios = evaluate_cost_sensitivity(contract, data, baseline)
    s1_a = scenarios[1]["policies"][0]
    assert s1_a["status"] == "ECONOMIC_ORDER_REJECTED"
    assert s1_a["quantities"] == {"SPY": 1000, "BIL": 0}
    assert s1_a["partial_execution"] is False
    assert s1_a["performance_comparable"] is False


def test_artificial_policies_are_paired_on_identical_dates() -> None:
    contract = artificial_contract()
    data = artificial_data()
    results = [evaluate_policy(contract, data, policy) for policy in contract.policies]
    assert [item.quantities for item in results] == [
        {"SPY": 1000, "BIL": 0},
        {"SPY": 0, "BIL": 1000},
        {"SPY": 500, "BIL": 500},
    ]
    assert len({tuple(row.valuation_date for row in item.trajectory) for item in results}) == 1
    assert [item.terminal_wealth for item in results] == [
        D("107000"),
        D("100000"),
        D("103500"),
    ]


def test_path_metrics_include_entry_base_drawdown_and_exact_return() -> None:
    rows = tuple(
        ValuationRow("X", date(2024, 1, index + 1), D(value), D("0"), D("0"), D("0"), D("0"))
        for index, value in enumerate(("100", "90", "80", "100"))
    )
    metrics = calculate_path_metrics(
        rows,
        volatility_factor=252,
        elapsed_days=3,
        annualized_return_day_count=3,
    )
    assert metrics["total_return"] == pytest.approx(0)
    assert metrics["annualized_return"] == pytest.approx(0)
    assert metrics["maximum_drawdown"] == pytest.approx(-0.2)
    assert metrics["maximum_drawdown_duration_sessions"] == 2
    assert metrics["terminal_drawdown_open"] is False


def test_documentary_block_stops_before_any_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*args, **kwargs):  # noqa: ANN002, ANN003
        raise DocumentaryBlock("source commune manquante")

    monkeypatch.setattr(evaluation, "prepare_episode_data", blocked)
    result = run_evaluation(CONFIG, repo_root=ROOT)
    assert result.verdict is EvaluationVerdict.NOT_EVALUABLE
    assert result.policies == ()
    assert result.trace == ("CONFIG_VERIFIED",)


@pytest.mark.skipif(
    not (ROOT / "data" / "raw" / "rl_market").is_dir(),
    reason="sources historiques locales exclues de GitHub",
)
def test_real_prespecified_episode_is_reproducible() -> None:
    first = run_evaluation(CONFIG, repo_root=ROOT)
    second = run_evaluation(CONFIG, repo_root=ROOT)
    assert first.to_record() == second.to_record()
    assert first.verdict is EvaluationVerdict.VALIDATED
    assert first.terminal_date == date(2025, 5, 29)
    assert [item.quantities for item in first.policies] == [
        {"SPY": 188, "BIL": 0},
        {"SPY": 0, "BIL": 1089},
        {"SPY": 94, "BIL": 544},
    ]
    assert [item.terminal_wealth for item in first.policies] == [
        D("113448.69771003126880"),
        D("104607.45166969141714"),
        D("109025.95923914063984"),
    ]
    coverage = first.market_summary["session_coverage"]
    assert len(coverage["expected_sessions"]) == 251
    assert len(coverage["common_sessions"]) == 251
    assert coverage["missing_spy"] == coverage["missing_bil"] == []
    assert coverage["spy_only"] == coverage["bil_only"] == []
    assert coverage["early_closes"] == [
        "2024-07-03",
        "2024-11-29",
        "2024-12-24",
    ]
    assert coverage["exceptional_closures"] == ["2025-01-09"]
    assert all(
        item["claim_amount"] == item["paid_amount"]
        for policy in first.policies
        for item in policy.distribution_accounting
    )
    by_scenario = {item["scenario_id"]: item for item in first.cost_sensitivity}
    assert all(
        item["status"] == "EXECUTED_HYPOTHETICAL"
        for scenario_id in ("S0", "S1", "S2")
        for item in by_scenario[scenario_id]["policies"]
    )
    s3 = {item["policy_id"]: item for item in by_scenario["S3"]["policies"]}
    assert s3["B"]["status"] == "ECONOMIC_ORDER_REJECTED"
    assert s3["B"]["quantities"] == {"SPY": 0, "BIL": 1089}
    assert s3["B"]["initial_cost"] == "99.9375263442993096"
    assert s3["B"]["partial_execution"] is False
    assert s3["A"]["terminal_wealth"] == "113349.8698714082219344"
    assert s3["C1"]["terminal_wealth"] == "108926.6224416552882856"
