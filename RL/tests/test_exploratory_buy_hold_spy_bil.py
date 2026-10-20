from __future__ import annotations

import sys
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
    EpisodeContract,
    EpisodeData,
    EvaluationVerdict,
    PolicyDefinition,
    ValuationRow,
    calculate_path_metrics,
    evaluate_policy,
    run_evaluation,
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
                date(2024, 6, 3),
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
