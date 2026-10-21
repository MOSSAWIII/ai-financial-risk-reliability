from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import historical_c1_c2_comparison as comparison  # noqa: E402


D = Decimal


@pytest.fixture(scope="module")
def result() -> comparison.ExperimentResult:
    if not (ROOT / "data" / "raw" / "rl_market").is_dir():
        pytest.skip("sources historiques locales exclues de GitHub")
    return comparison.run_experiment(ROOT)


def summaries_by_key(result: comparison.ExperimentResult):
    return {
        (run.cell.cell_id, run.policy_id): run.summary for run in result.runs
    }


def test_eight_independent_cells_and_all_runs_complete(result) -> None:
    assert len(result.comparisons) == 8
    assert len(result.runs) == 16
    assert {run.cell.cell_id for run in result.runs} == {
        "S0-D1",
        "S1-D1",
        "S2-D1",
        "S3-D1",
        "S0-D2",
        "S1-D2",
        "S2-D2",
        "S3-D2",
    }
    assert all(run.summary["run_status"] == "COMPLETE" for run in result.runs)


def test_c1_reproduces_published_terminal_wealth_exactly(result) -> None:
    summaries = summaries_by_key(result)
    expected = {
        "S0": D("109025.95923914063984"),
        "S1": D("109016.02555939210468456"),
        "S2": D("108976.2908403979640628"),
        "S3": D("108926.6224416552882856"),
    }
    for scenario, wealth in expected.items():
        assert D(summaries[(f"{scenario}-D1", "C1")]["terminal_wealth_usd"]) == wealth
        assert D(summaries[(f"{scenario}-D2", "C1")]["terminal_wealth_usd"]) == wealth


def test_c2_terminal_wealth_is_locked_for_all_cells(result) -> None:
    summaries = summaries_by_key(result)
    expected = {
        "S0-D1": D("109616.08057714649936"),
        "S1-D1": D("109601.159897454421731556"),
        "S2-D1": D("109541.694854398025091605"),
        "S3-D1": D("109466.29451610554462057"),
        "S0-D2": D("109605.49060369679237"),
        "S1-D2": D("109592.212926426284514524"),
        "S2-D2": D("109530.6004362172695201"),
        "S3-D2": D("109445.69084644306908208"),
    }
    assert {
        cell: D(summaries[(cell, "C2")]["terminal_wealth_usd"])
        for cell in expected
    } == expected


def test_all_52_decisions_are_evaluable_sealed_and_non_interfering(result) -> None:
    allowed = {
        "EXECUTED_HYPOTHETICAL",
        "VOLUNTARY_HOLD",
        "ECONOMIC_ORDER_REJECTED",
    }
    forbidden = {
        "economic_distribution_receivables",
        "economic_wealth",
        "excluded_distribution_claims",
        "unavailable_paid_cash",
    }
    c2_runs = [run for run in result.runs if run.policy_id == "C2"]
    assert sum(len(run.decisions) for run in c2_runs) == 416
    for run in c2_runs:
        assert len(run.decisions) == 52
        assert {row["cycle"] for row in run.decisions} == {
            str(index) for index in range(1, 53)
        }
        assert all(row["snapshot_status"] == "READY" for row in run.decisions)
        assert all(row["execution_status"] in allowed for row in run.decisions)
        assert all(row["snapshot_id"].startswith("SNAPSHOT-") for row in run.decisions)
        assert all(row["intent_id"].startswith("INTENT-") for row in run.decisions)
        assert all(forbidden.isdisjoint(row) for row in run.decisions)


def test_daily_and_terminal_accounting_reconcile_exactly(result) -> None:
    for run in result.runs:
        assert len(run.trajectories) == 251
        assert all(
            D(row["wealth_identity_difference_usd"]) == 0
            for row in run.trajectories
        )
        assert D(run.summary["terminal_reconciliation_difference_usd"]) == 0
        assert D(run.summary["terminal_reconciliation_usd"]) == D(
            run.summary["terminal_wealth_usd"]
        )


def test_all_sixteen_distributions_are_accrued_and_paid_once(result) -> None:
    for run in result.runs:
        assert run.summary["distribution_event_count"] == 16
        assert D(run.summary["distributions_accrued_usd"]) == D(
            run.summary["distributions_paid_usd"]
        )
        assert D(run.trajectories[-1]["distribution_receivables_usd"]) == 0


def test_initial_trades_are_paired_and_rejections_are_never_hidden(result) -> None:
    summaries = summaries_by_key(result)
    for cell in {item["cell_id"] for item in result.comparisons}:
        c1 = summaries[(cell, "C1")]
        c2 = summaries[(cell, "C2")]
        assert c1["initial_quantities"] == c2["initial_quantities"]
        assert c1["initial_fees_usd"] == c2["initial_fees_usd"]
        assert c2["candidate_decisions"] == 52
        assert (
            c2["executed_rebalances"]
            + c2["voluntary_holds"]
            + c2["rejected_batches"]
            == 52
        )
        assert c2["rejected_batches"] == 0
        assert c2["rejected_order_count"] == 0


def test_d2_effect_is_descriptive_and_c1_is_invariant(result) -> None:
    comparisons = {row["cell_id"]: row for row in result.comparisons}
    for row in comparisons.values():
        assert D(row["c1_terminal_wealth_d2_minus_d1_usd"]) == 0
        assert D(row["c2_terminal_wealth_d2_minus_d1_usd"]) < 0


def test_outputs_rebuild_byte_for_byte(result, tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_hashes = comparison.write_outputs(result, first)
    second_hashes = comparison.write_outputs(result, second)
    assert first_hashes == second_hashes
    for name in comparison.OUTPUT_NAMES.values():
        assert (first / name).read_bytes() == (second / name).read_bytes()
        assert (first / name).read_bytes() == (
            comparison.DEFAULT_OUTPUT_DIR / name
        ).read_bytes()
    assert (first / comparison.FIGURE_NAME).read_bytes() == (
        second / comparison.FIGURE_NAME
    ).read_bytes()
    assert (first / comparison.FIGURE_NAME).read_bytes() == (
        comparison.DEFAULT_OUTPUT_DIR / comparison.FIGURE_NAME
    ).read_bytes()
