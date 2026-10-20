from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_c2_documentary_grid as grid  # noqa: E402


def test_weekly_candidates_exclude_initialization_week_and_stop_at_terminal() -> None:
    sessions = {
        date(2024, 5, 28),
        date(2024, 5, 29),
        date(2024, 5, 30),
        date(2024, 5, 31),
        date(2024, 6, 3),
        date(2024, 6, 4),
        date(2025, 5, 23),
        date(2025, 5, 27),
        date(2025, 5, 28),
        date(2025, 5, 29),
        date(2025, 5, 30),
    }
    candidates = grid.weekly_candidates(sessions)
    assert (candidates[0].close_reference, candidates[0].decision_date) == (
        date(2024, 5, 31),
        date(2024, 6, 3),
    )
    assert (candidates[-1].close_reference, candidates[-1].decision_date) == (
        date(2025, 5, 23),
        date(2025, 5, 27),
    )
    assert date(2024, 5, 29) not in {item.decision_date for item in candidates}
    assert all(item.decision_date <= grid.TERMINAL for item in candidates)


def test_next_settlement_day_skips_dtc_non_settlement_day() -> None:
    assert grid.next_settlement_day(date(2024, 10, 11)) == date(2024, 10, 15)
    assert grid.next_settlement_day(date(2025, 5, 23)) == date(2025, 5, 27)


def test_historical_grid_has_prespecified_scope_and_dst_offsets() -> None:
    rows, summary = grid.build_rows(ROOT)
    assert summary["candidate_count"] == 52
    assert summary["distribution_count"] == 16
    assert rows[0]["close_reference"] == "2024-05-31"
    assert rows[0]["decision_at"] == "2024-06-03T08:00:00-04:00"
    assert rows[-1]["open_candidate"] == "2025-05-27"
    winter = next(row for row in rows if row["open_candidate"] == "2024-11-04")
    assert winter["decision_at"].endswith("-05:00")


def test_all_candidate_prices_are_present_but_remain_proxies() -> None:
    rows, _ = grid.build_rows(ROOT)
    assert {row["close_presence"] for row in rows} == {"PRESENT_BOTH"}
    assert {row["open_presence"] for row in rows} == {"PRESENT_BOTH"}
    assert {row["close_point_in_time_status"] for row in rows} == {
        "MARKET_OBSERVABLE_PROXY_NOT_ARCHIVED_PIT"
    }


def test_documentary_blocks_are_retained_without_financial_outputs() -> None:
    rows, summary = grid.build_rows(ROOT)
    assert summary["settlement_status_counts"] == {
        "VERIFIED": 52,
        "RULE_BASED_UNVERIFIED": 0,
        "CONFLICTING": 0,
        "MISSING": 0,
    }
    assert summary["documentary_status_counts"] == {
        "READY_DOCUMENTARY": 0,
        "PARTIALLY_DOCUMENTED": 20,
        "NOT_EVALUABLE_DOCUMENTARY": 32,
    }
    assert "BLOCKED_BY_UNKNOWN_ENTITLEMENT" in rows[0]["decision_statuses"]
    forbidden = {"quantity", "wealth", "order", "performance", "return"}
    assert not any(
        token in column.lower() for column in rows[0] for token in forbidden
    )


def test_versioned_csv_is_reproducible(tmp_path: Path) -> None:
    rows, _ = grid.build_rows(ROOT)
    rebuilt = tmp_path / "grid.csv"
    grid.write_csv(rows, rebuilt)
    assert rebuilt.read_bytes() == grid.DEFAULT_OUTPUT.read_bytes()
