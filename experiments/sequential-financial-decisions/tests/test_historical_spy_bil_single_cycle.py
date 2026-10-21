from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
REAL_CONFIG = (
    Path(__file__).resolve().parents[0]
    / "fixtures"
    / "historical_spy_bil_single_cycle_v1.json"
)
sys.path.insert(0, str(SCRIPTS))

from historical_spy_bil_single_cycle import (  # noqa: E402
    HistoricalCycleVerdict,
    prepare_historical_cycle,
    run_single_cycle,
)
from synthetic_decision_adapter import (  # noqa: E402
    DatedPrice,
    ExecutionStatus,
    PriceStatus,
)
from synthetic_portfolio_ledger import FixedOrder  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def write_config(path: Path, value: dict) -> None:
    write_json(path, value)
    path.with_suffix(path.suffix + ".sha256").write_text(
        f"{sha256(path)}  {path.name}\n", encoding="ascii"
    )


def yahoo_document(symbol: str) -> dict:
    if symbol == "SPY":
        closes = ["100", "98"]
        opens = ["101", "99"]
        highs = ["102", "100"]
        lows = ["99", "97"]
    else:
        closes = ["50", "49"]
        opens = ["50.5", "49"]
        highs = ["51", "50"]
        lows = ["49.5", "48"]
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "symbol": symbol,
                        "currency": "USD",
                        "exchangeTimezoneName": "America/New_York",
                        "dataGranularity": "1d",
                    },
                    "timestamp": [1716903000, 1716989400],
                    "indicators": {
                        "quote": [
                            {
                                "open": opens,
                                "high": highs,
                                "low": lows,
                                "close": closes,
                                "volume": [1000, 1100],
                            }
                        ]
                    },
                    "events": {},
                }
            ],
            "error": None,
        }
    }


def source_record(identifier: str, path: Path, root: Path, **extra) -> dict:
    return {
        "id": identifier,
        "local_file": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "status": extra.pop("status", "AUDITED"),
        **extra,
    }


def artificial_repository(tmp_path: Path) -> tuple[Path, Path, dict]:
    root = tmp_path / "repo"
    data = root / "data"
    spy_path = data / "spy.json"
    bil_path = data / "bil.json"
    audit_path = data / "audit.json"
    distribution_path = data / "distributions.xlsx"
    rule_path = data / "sec-rule.pdf"
    calendar_path = data / "dtcc-guide.pdf"
    write_json(spy_path, yahoo_document("SPY"))
    write_json(bil_path, yahoo_document("BIL"))
    write_json(
        audit_path,
        {
            "cross_checks": {
                "spy_yahoo_vs_nasdaq_priority_window": {
                    "diagnostic_alerts": {"dates": []}
                }
            }
        },
    )
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "dividend"
    sheet.append(["TICKER", "EX-DATE", "RECORD DATE", "PAYABLE DATE"])
    sheet.append(["SPY", "06/21/2024", "06/21/2024", "07/31/2024"])
    distribution_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(distribution_path)
    rule_path.write_bytes(b"artificial SEC T+1 rule")
    calendar_path.write_bytes(b"artificial DTCC May 29 to May 30 calendar")

    records = [
        source_record("yahoo_spy_chart_ohlcv_20261019", spy_path, root),
        source_record("yahoo_bil_chart_ohlcv_20261019", bil_path, root),
        source_record("yahoo_spy_bil_market_audit_v1_20261019", audit_path, root),
        source_record("ssga_spdr_distributions_20261019", distribution_path, root),
        source_record(
            "sec_settlement_cycle_t1_2023_20261019",
            rule_path,
            root,
            status="VALIDATED_FOR_USE",
        ),
        source_record(
            "dtcc_t1_conversion_guide_may2024_20261020",
            calendar_path,
            root,
            status="VALIDATED_FOR_USE",
            coverage="29 mai 2024 au 30 mai 2024",
            economic_meaning="trade du 29 mai 2024 réglé le 30 mai 2024",
            allowed_uses=["cycle ciblé du 29 mai 2024 au 30 mai 2024"],
        ),
    ]
    manifest = root / "RL" / "data_manifest.json"
    write_json(manifest, {"datasets": records})
    config = json.loads(REAL_CONFIG.read_text(encoding="utf-8"))
    config_path = tmp_path / "cycle.json"
    write_config(config_path, config)
    return root, config_path, config


def test_artificial_single_cycle_freezes_before_open_and_settles(tmp_path: Path) -> None:
    root, config_path, _ = artificial_repository(tmp_path)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.VALIDATED
    assert result.outcome is not None
    assert result.outcome.status is ExecutionStatus.EXECUTED_HYPOTHETICAL
    assert result.intent is not None
    assert result.intent.target_quantities == {"SPY": 500, "BIL": 1000}
    assert result.trace.index("INTENT_PREPARED_AND_QUANTITIES_FROZEN") < result.trace.index(
        "EXECUTION_OPENS_LOADED_AFTER_INTENT"
    )
    assert result.after_settlement is not None
    assert result.after_settlement.settled_positions == {"SPY": 500, "BIL": 1000}
    assert result.wealth_before_settlement == result.wealth_after_settlement


def test_missing_documentary_source_stops_before_financial_mutation(tmp_path: Path) -> None:
    root, config_path, _ = artificial_repository(tmp_path)
    manifest_path = root / "RL" / "data_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["datasets"] = [
        item
        for item in manifest["datasets"]
        if item["id"] != "dtcc_t1_conversion_guide_may2024_20261020"
    ]
    write_json(manifest_path, manifest)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.NOT_EVALUABLE
    assert result.outcome is None
    assert result.before_settlement is None


def test_wrong_source_hash_fails_integrity(tmp_path: Path) -> None:
    root, config_path, _ = artificial_repository(tmp_path)
    (root / "data" / "spy.json").write_bytes(b"tampered")
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.FAILED
    assert "empreinte" in result.reason


def test_incoherent_date_is_rejected(tmp_path: Path) -> None:
    root, config_path, config = artificial_repository(tmp_path)
    config["execution"]["trade_date"] = "2024-05-28"
    write_config(config_path, config)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.FAILED
    assert "chronologie" in result.reason


def test_disputed_price_blocks_before_financial_mutation(tmp_path: Path) -> None:
    root, config_path, config = artificial_repository(tmp_path)
    config["execution"]["anomaly_status"] = "DISPUTED"
    write_config(config_path, config)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.NOT_EVALUABLE
    assert result.outcome is None


def test_future_open_cannot_be_used_as_decision_price(tmp_path: Path) -> None:
    root, config_path, config = artificial_repository(tmp_path)
    config["decision"]["decision_price_field"] = "open"
    write_config(config_path, config)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.FAILED
    assert "uniquement le close" in result.reason


def test_modified_orders_are_rejected_after_boundary_preparation(tmp_path: Path) -> None:
    root, config_path, _ = artificial_repository(tmp_path)
    prepared = prepare_historical_cycle(config_path, repo_root=root)
    forged = replace(
        prepared.intent,
        orders=(FixedOrder("SPY", 1, date(2024, 5, 28), Decimal("100")),),
    )
    before = prepared.ledger.accounting_snapshot()
    outcome = prepared.adapter.process_intent(
        forged,
        execution_date=date(2024, 5, 29),
        execution_opens={
            "SPY": DatedPrice(date(2024, 5, 29), Decimal("99"), PriceStatus.AVAILABLE),
            "BIL": DatedPrice(date(2024, 5, 29), Decimal("49"), PriceStatus.AVAILABLE),
        },
    )
    assert outcome.status is ExecutionStatus.INVALID_INPUT
    assert outcome.accounting_before == outcome.accounting_after == before


def test_unverified_calendar_blocks_cycle(tmp_path: Path) -> None:
    root, config_path, config = artificial_repository(tmp_path)
    config["calendars"]["settlement_status"] = "UNVERIFIED"
    write_config(config_path, config)
    result = run_single_cycle(config_path, repo_root=root)
    assert result.verdict is HistoricalCycleVerdict.NOT_EVALUABLE
    assert result.outcome is None


def test_complete_replay_from_same_initial_state_is_identical(tmp_path: Path) -> None:
    root, config_path, _ = artificial_repository(tmp_path)
    first = run_single_cycle(config_path, repo_root=root)
    second = run_single_cycle(config_path, repo_root=root)
    assert first.to_record() == second.to_record()


@pytest.mark.skipif(
    not (ROOT / "data" / "raw" / "rl_market").is_dir(),
    reason="sources historiques locales exclues de GitHub",
)
def test_real_prespecified_cycle_is_separate_and_reproducible() -> None:
    first = run_single_cycle(REAL_CONFIG, repo_root=ROOT)
    second = run_single_cycle(REAL_CONFIG, repo_root=ROOT)
    assert first.to_record() == second.to_record()
    assert first.verdict is HistoricalCycleVerdict.VALIDATED
    assert first.closes == {
        "SPY": Decimal("529.8099975585938"),
        "BIL": Decimal("91.76000213623047"),
    }
    assert first.opens == {
        "SPY": Decimal("525.6799926757812"),
        "BIL": Decimal("91.7699966430664"),
    }
    assert first.intent is not None
    assert first.intent.target_quantities == {"SPY": 94, "BIL": 544}
    assert first.outcome is not None
    assert first.outcome.settlement_date == date(2024, 5, 30)
