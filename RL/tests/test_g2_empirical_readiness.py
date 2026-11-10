from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RL" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from g2_empirical_readiness import (  # noqa: E402
    PERFORMANCE_OUTPUT_NAMES,
    ReadinessError,
    build_readiness_report,
    write_readiness_only,
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _fixture(tmp_path: Path, *, missing: bool = False, wrong_hash: bool = False) -> tuple[Path, Path, tuple[str, ...]]:
    source_id = "source_a"
    relative = "data/raw/source.bin"
    payload = b"original frozen source"
    expected_hash = _sha256(b"different") if wrong_hash else _sha256(payload)
    if not missing:
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_bytes(payload)
    protocol = tmp_path / "RL/docs/PROTOCOLE_G2_MATERIALITE_EMPIRIQUE.md"
    protocol.parent.mkdir(parents=True)
    protocol.write_text("frozen\n", encoding="utf-8")
    manifest = tmp_path / "RL/data_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "id": source_id,
                        "local_file": relative,
                        "sha256": expected_hash,
                        "bytes": len(payload),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return manifest, protocol, (source_id,)


def test_exact_original_source_opens_the_documentary_gate(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path)
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    assert report["documentary_verdict"] == "READY_FOR_G2_EXECUTION"
    assert report["performance_outputs_authorized"] is True
    assert report["source_checks"][0]["status"] == "VERIFIED"


def test_missing_original_source_blocks_g2(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path, missing=True)
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    assert report["documentary_verdict"] == "DOCUMENTARY_BLOCK"
    assert report["source_checks"][0]["status"] == "FILE_MISSING"
    assert report["performance_computed"] is False


def test_hash_mismatch_is_not_accepted_as_the_original(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path, wrong_hash=True)
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    assert report["documentary_verdict"] == "DOCUMENTARY_BLOCK"
    assert report["source_checks"][0]["status"] == "HASH_MISMATCH"


def test_published_results_do_not_replace_missing_raw_source(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path, missing=True)
    control = tmp_path / "RL/results/historical_c1_c2_2024_2025/journal_decisions_c2.csv"
    control.parent.mkdir(parents=True)
    control.write_text("cycle,target\n1,0.5\n", encoding="utf-8")
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    assert report["documentary_verdict"] == "DOCUMENTARY_BLOCK"
    assert report["published_controls"][0]["present"] is True
    assert report["published_controls_can_replace_raw_sources"] is False


def test_blocked_run_writes_readiness_only(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path, missing=True)
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    output_dir = tmp_path / "out"
    path = write_readiness_only(report, output_dir)
    assert path.is_file()
    assert sorted(item.name for item in output_dir.iterdir()) == ["readiness_report.json"]
    assert all(not (output_dir / name).exists() for name in PERFORMANCE_OUTPUT_NAMES)


def test_blocked_run_refuses_preexisting_performance_output(tmp_path: Path) -> None:
    manifest, protocol, required = _fixture(tmp_path, missing=True)
    report = build_readiness_report(tmp_path, manifest, required, protocol)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "g2_report.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ReadinessError, match="malgré le blocage"):
        write_readiness_only(report, output_dir)
