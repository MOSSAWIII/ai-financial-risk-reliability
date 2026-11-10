from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g2_empirical_sequentiality import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    TargetController,
    check_outputs,
    run_experiment,
)


def test_g2_completes_all_paired_runs_and_decisions() -> None:
    result = run_experiment(ROOT)
    assert len(result.runs) == 16
    assert len(result.decisions) == 16 * 52
    assert len(result.comparisons) == 8
    assert result.report["status"] == "COMPLETE"


def test_negative_controls_hold_through_five_basis_points() -> None:
    result = run_experiment(ROOT)
    for row in result.comparisons:
        if row["cost_scenario"] in {"S0", "S1", "S2"}:
            assert row["action_sequences_identical"] is True
            assert row["financial_paths_identical"] is True


def test_s3_contains_realized_policy_disagreement() -> None:
    result = run_experiment(ROOT)
    assert any(
        row["action_sequences_identical"] is False
        for row in result.comparisons
        if row["cost_scenario"] == "S3"
    )


def test_materiality_verdict_and_g3_gate_are_consistent() -> None:
    result = run_experiment(ROOT)
    assert result.report["verdict"] in {
        "G2_MATERIAL_POSITIVE",
        "G2_MATERIAL_OTHER",
        "G2_NOT_MATERIAL",
    }
    assert result.report["g3_authorized"] is (
        result.report["verdict"] == "G2_MATERIAL_POSITIVE"
    )
    assert result.report["materiality_threshold_usd"] == "250"


def test_versioned_outputs_are_reproducible() -> None:
    result = run_experiment(ROOT)
    check_outputs(result, DEFAULT_OUTPUT_DIR)
