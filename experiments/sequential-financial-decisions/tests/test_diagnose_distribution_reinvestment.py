from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from diagnose_distribution_reinvestment import (  # noqa: E402
    LOCKED_ARTIFACT_HASHES,
    LOCKED_OUTPUT_DIR,
    _intent_hash,
    check_outputs,
    run_diagnostic,
    sha256_file,
    write_outputs,
)
from exploratory_buy_hold_spy_bil import load_contract, prepare_episode_data  # noqa: E402
from historical_c1_c2_comparison import CONTRACT_PATH  # noqa: E402


D = Decimal


@pytest.fixture(scope="module")
def result():
    if not (ROOT / "data" / "raw" / "rl_market").is_dir():
        pytest.skip("sources historiques locales exclues de GitHub")
    return run_diagnostic(ROOT)


def test_locked_c1_c2_artifacts_and_terminals_are_exact(result) -> None:
    for name, expected in LOCKED_ARTIFACT_HASHES.items():
        assert sha256_file(LOCKED_OUTPUT_DIR / name) == expected
    expected_c2 = {
        "S0-D1": D("109616.08057714649936"),
        "S1-D1": D("109601.159897454421731556"),
        "S2-D1": D("109541.694854398025091605"),
        "S3-D1": D("109466.29451610554462057"),
        "S0-D2": D("109605.49060369679237"),
        "S1-D2": D("109592.212926426284514524"),
        "S2-D2": D("109530.6004362172695201"),
        "S3-D2": D("109445.69084644306908208"),
    }
    actual = {
        run.cell.cell_id: D(run.summary["terminal_wealth_usd"])
        for run in result.locked_result.runs
        if run.policy_id == "C2"
    }
    assert actual == expected_c2


def test_eight_c3_cells_are_complete_and_locked(result) -> None:
    expected = {
        "S0-D1": D("109109.97125800733923"),
        "S1-D1": D("109099.743654257491818703"),
        "S2-D1": D("109058.833239258102173515"),
        "S3-D1": D("109007.69522050886511703"),
        "S0-D2": D("109105.20129951124549"),
        "S1-D2": D("109094.973218765548469329"),
        "S2-D2": D("109054.060895782760386645"),
        "S3-D2": D("109002.92049205427528329"),
    }
    assert len(result.c3_runs) == 8
    assert {
        run.cell.cell_id: D(run.summary["terminal_wealth_usd"])
        for run in result.c3_runs
    } == expected
    assert all(run.summary["run_status"] == "COMPLETE" for run in result.c3_runs)


def test_c3_shares_initial_purchase_and_never_sells(result) -> None:
    for run in result.c3_runs:
        assert run.summary["initial_quantities"] == '{"BIL":544,"SPY":94}'
        assert all(int(row["quantity"]) >= 0 for row in run.decisions)
        assert all(row["symbol"] in row["event_id"] for row in run.decisions)


def test_distribution_pools_are_segregated_and_initial_cash_is_untouched(result) -> None:
    for run in result.c3_runs:
        summary = run.summary
        assert D(summary["terminal_cash_usd"]) == (
            D(summary["initial_residual_cash_usd"])
            + D(summary["terminal_spy_distribution_pool_usd"])
            + D(summary["terminal_bil_distribution_pool_usd"])
        )
        assert all(D(row["pool_transfer_usd"]) == 0 for row in run.decisions)
        assert all(D(row["pool_transfer_usd"]) == 0 for row in run.pools)
        for row in run.decisions:
            if row["execution_status"] == "EXECUTED_HYPOTHETICAL":
                assert D(row["actual_cost_usd"]) <= D(row["pool_before_usd"])


def test_intents_are_sealed_before_open_and_use_whole_shares(result) -> None:
    for run in result.c3_runs:
        for row in run.decisions:
            payload = {
                key: row[key]
                for key in (
                    "cell_id",
                    "event_id",
                    "symbol",
                    "decision_at",
                    "close_reference",
                    "decision_close_usd",
                    "pool_before_usd",
                    "quantity",
                    "cost_bps",
                    "snapshot_id",
                )
            }
            assert row["intent_sha256"] == _intent_hash(payload)
            assert row["sealed_before_open"] == "true"
            assert type(row["quantity"]) is int
            assert date.fromisoformat(row["close_reference"]) < date.fromisoformat(row["execution_date"])


def test_d1_d2_schedule_matches_dtc_and_first_nyse_session(result) -> None:
    contract = load_contract(CONTRACT_PATH)
    data = prepare_episode_data(contract, repo_root=ROOT)
    from historical_c1_c2_comparison import _new_ledger

    ledger, _ = _new_ledger(contract, data)
    assert ledger.settlement_calendar is not None
    events = {event.event_id: event for event in data.distributions}
    sessions = tuple(data.common_sessions)
    for run in result.c3_runs:
        delay = 1 if run.cell.cell_id.endswith("D1") else 2
        for row in run.decisions:
            available = ledger.settlement_calendar.business_date_after(
                events[row["event_id"]].payment_date, delay
            )
            expected = next(session for session in sessions if session >= available)
            assert date.fromisoformat(row["execution_date"]) == expected


def test_new_shares_generate_additional_distributions(result) -> None:
    for run in result.c3_runs:
        assert run.summary["distribution_triggers"] == 16
        assert run.summary["triggers_with_purchase"] == 13
        assert run.summary["rejected_orders"] == 0
        assert run.summary["additional_spy_shares"] == 1
        assert run.summary["additional_bil_shares"] == 26
        assert D(run.summary["extra_distributions_from_reinvested_shares_usd"]) == D(
            "48.742068"
        )


def test_daily_and_terminal_identities_are_exact(result) -> None:
    for run in result.c3_runs:
        assert len(run.trajectories) == 251
        assert all(D(row["wealth_identity_difference_usd"]) == 0 for row in run.trajectories)
        assert D(run.summary["terminal_reconciliation_difference_usd"]) == 0
    assert all(D(row["identity_difference_usd"]) == 0 for row in result.differences)


def test_costs_and_cash_delay_have_expected_direction(result) -> None:
    by_cell = {run.cell.cell_id: run.summary for run in result.c3_runs}
    for scenario in ("S0", "S1", "S2", "S3"):
        assert D(by_cell[f"{scenario}-D2"]["terminal_wealth_usd"]) < D(
            by_cell[f"{scenario}-D1"]["terminal_wealth_usd"]
        )
    assert D(by_cell["S0-D1"]["reinvestment_fees_usd"]) == 0
    assert D(by_cell["S3-D1"]["reinvestment_fees_usd"]) > D(
        by_cell["S2-D1"]["reinvestment_fees_usd"]
    )


def test_outputs_rebuild_byte_for_byte(result, tmp_path: Path) -> None:
    write_outputs(result, tmp_path)
    check_outputs(result, tmp_path)
