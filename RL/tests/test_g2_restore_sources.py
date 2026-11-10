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

from g2_empirical_readiness import ReadinessError, sha256_file  # noqa: E402
from g2_restore_sources import apply_restore_plan, build_restore_plan  # noqa: E402


def _fixture(tmp_path: Path, *, backup_payload: bytes | None, destination_payload: bytes | None = None):
    repo = tmp_path / "repo"
    backup = tmp_path / "backup"
    relative = Path("data/raw/source.bin")
    expected = b"frozen original"
    manifest = repo / "RL/data_manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        json.dumps(
            {
                "datasets": [
                    {
                        "id": "source_a",
                        "local_file": str(relative),
                        "sha256": hashlib.sha256(expected).hexdigest(),
                        "bytes": len(expected),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    if backup_payload is not None:
        source = backup / relative
        source.parent.mkdir(parents=True)
        source.write_bytes(backup_payload)
    if destination_payload is not None:
        destination = repo / relative
        destination.parent.mkdir(parents=True)
        destination.write_bytes(destination_payload)
    return repo, backup, manifest, ("source_a",), expected


def test_exact_backup_is_restored(tmp_path: Path) -> None:
    repo, backup, manifest, required, expected = _fixture(
        tmp_path, backup_payload=b"frozen original"
    )
    plan = build_restore_plan(repo, [backup], manifest, required)
    assert plan["preflight_status"] == "PASS"
    applied = apply_restore_plan(plan)
    destination = repo / "data/raw/source.bin"
    assert destination.read_bytes() == expected
    assert applied["sources"][0]["status"] == "RESTORED"
    assert applied["restored_count"] == 1


def test_missing_backup_blocks_without_writing(tmp_path: Path) -> None:
    repo, backup, manifest, required, _ = _fixture(tmp_path, backup_payload=None)
    plan = build_restore_plan(repo, [backup], manifest, required)
    assert plan["preflight_status"] == "BLOCKED"
    with pytest.raises(ReadinessError, match="précontrôle bloqué"):
        apply_restore_plan(plan)
    assert not (repo / "data/raw/source.bin").exists()


def test_wrong_backup_hash_blocks_without_writing(tmp_path: Path) -> None:
    repo, backup, manifest, required, _ = _fixture(tmp_path, backup_payload=b"current response")
    plan = build_restore_plan(repo, [backup], manifest, required)
    assert plan["sources"][0]["status"] == "BACKUP_HASH_MISMATCH"
    assert not (repo / "data/raw/source.bin").exists()


def test_conflicting_destination_is_never_overwritten(tmp_path: Path) -> None:
    repo, backup, manifest, required, _ = _fixture(
        tmp_path,
        backup_payload=b"frozen original",
        destination_payload=b"user data",
    )
    destination = repo / "data/raw/source.bin"
    before = sha256_file(destination)
    plan = build_restore_plan(repo, [backup], manifest, required)
    assert plan["sources"][0]["status"] == "DESTINATION_CONFLICT"
    with pytest.raises(ReadinessError):
        apply_restore_plan(plan)
    assert sha256_file(destination) == before


def test_already_present_exact_file_is_idempotent(tmp_path: Path) -> None:
    repo, backup, manifest, required, expected = _fixture(
        tmp_path,
        backup_payload=None,
        destination_payload=b"frozen original",
    )
    plan = build_restore_plan(repo, [backup], manifest, required)
    assert plan["preflight_status"] == "PASS"
    assert plan["sources"][0]["status"] == "ALREADY_PRESENT"
    applied = apply_restore_plan(plan)
    assert applied["restored_count"] == 0
    assert (repo / "data/raw/source.bin").read_bytes() == expected
