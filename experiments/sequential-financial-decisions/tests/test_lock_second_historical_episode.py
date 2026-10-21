from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lock_second_historical_episode import (  # noqa: E402
    CONFIG_PATH,
    GRID_PATH,
    PRICE_BLOCK_DATE,
    build_lock,
    check_block_artifacts,
    check_lock,
    sha256_file,
    verify_locked_artifacts,
)

RAW_DATA_ABSENT = not (ROOT / "data" / "raw" / "rl_market").is_dir()


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_lock_is_reproducible_and_precedes_performance() -> None:
    config, rows = build_lock(ROOT)
    check_lock(config, rows)
    assert config["locked_before_performance"] is True
    assert config["performance_computed"] is False


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_episode_scope_and_calendar_are_exact() -> None:
    config, rows = build_lock(ROOT)
    assert config["dates"]["execution_date"] == "2025-05-29"
    assert config["dates"]["terminal_date"] == "2026-05-29"
    assert config["coverage"]["common_sessions"] == 252
    assert config["coverage"]["weekly_decisions"] == 52
    assert len(rows) == 52


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_policies_and_eight_cells_are_not_recalibrated() -> None:
    config, _ = build_lock(ROOT)
    assert config["policies"] == {
        "C1": "INITIAL_50_50_THEN_HOLD_DISTRIBUTIONS_IN_CASH",
        "C2": "INITIAL_50_50_THEN_WEEKLY_50_50_OF_E_B_DECISION_BUDGET",
    }
    assert config["cost_scenarios_bps"] == {"S0": "0", "S1": "1", "S2": "5", "S3": "10"}
    assert config["decision_protocol"]["cash_conventions"] == ["D_PLUS_1", "D_PLUS_2"]
    assert "C3" not in config["policies"]


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_distributions_are_fully_enumerated() -> None:
    config, _ = build_lock(ROOT)
    assert config["coverage"]["distribution_events"] == 16
    assert config["coverage"]["spy_distributions"] == 4
    assert config["coverage"]["bil_distributions"] == 12
    assert len({row["event_id"] for row in config["distribution_events"]}) == 16


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_unresolved_spy_open_blocks_all_c2_cells() -> None:
    config, rows = build_lock(ROOT)
    blocked = [row for row in rows if row["documentary_status"] == "DOCUMENTARY_BLOCK"]
    assert len(blocked) == 1
    assert blocked[0]["open_candidate"] == PRICE_BLOCK_DATE.isoformat()
    assert blocked[0]["cycle"] == "47"
    assert blocked[0]["affected_cells"] == "ALL_EIGHT_C2_CELLS"
    assert config["documentary_gate"]["status"] == "DOCUMENTARY_BLOCK"


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_sources_are_hashed_and_new_nyse_calendar_is_present() -> None:
    config, _ = build_lock(ROOT)
    for source in config["sources"].values():
        assert len(source["sha256"]) == 64
        assert source["verified_bytes"] > 0
    calendar = config["sources"]["trading_calendar_2026"]
    assert calendar["id"] == "nyse_trading_calendar_2026_20261021"
    assert sha256_file(ROOT / calendar["local_file"]) == calendar["sha256"]


def test_config_hash_is_self_consistent() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    expected = config.pop("config_sha256")
    from lock_second_historical_episode import canonical_json
    import hashlib

    assert hashlib.sha256(canonical_json(config).encode("utf-8")).hexdigest() == expected
    assert GRID_PATH.is_file()
    verify_locked_artifacts(ROOT)


@pytest.mark.skipif(RAW_DATA_ABSENT, reason="sources historiques locales exclues de GitHub")
def test_prior_results_and_block_artifacts_are_reproducible() -> None:
    config, _ = build_lock(ROOT)
    verify_locked_artifacts(ROOT)
    check_block_artifacts(config)
