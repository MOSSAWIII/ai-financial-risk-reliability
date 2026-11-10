#!/usr/bin/env python3
"""Contrôle la frontière documentaire de G2 sans calculer de performance.

Les sources originales sont vérifiées par identifiant, chemin, taille et SHA-256.
Un artefact historique versionné est seulement une preuve auxiliaire : il ne
peut jamais compenser l'absence d'une source brute.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "RL" / "data_manifest.json"
DEFAULT_OUTPUT_DIR = ROOT / "RL" / "results" / "g2_empirical_sequentiality"
PROTOCOL_PATH = ROOT / "RL" / "docs" / "PROTOCOLE_G2_MATERIALITE_EMPIRIQUE.md"

REQUIRED_SOURCE_IDS = (
    "yahoo_spy_chart_ohlcv_20261019",
    "yahoo_bil_chart_ohlcv_20261019",
    "yahoo_spy_bil_market_audit_v1_20261019",
    "ssga_spdr_distributions_20261019",
    "nyse_trading_calendars_2022_2025_20261019",
    "sec_settlement_cycle_t1_2023_20261019",
    "dtcc_t1_conversion_guide_may2024_20261020",
)

PUBLISHED_CONTROL_PATHS = (
    "RL/results/historical_c1_c2_2024_2025/journal_decisions_c2.csv",
    "RL/results/historical_c1_c2_2024_2025/trajectoires_quotidiennes.csv",
    "RL/results/historical_c1_c2_2024_2025/synthese_financiere.csv",
    "RL/results/historical_c1_c2_2024_2025/comparaison_appariee.csv",
)

PERFORMANCE_OUTPUT_NAMES = (
    "policy_decisions.csv",
    "daily_trajectories.csv",
    "financial_summary.csv",
    "paired_comparison.csv",
    "g2_report.json",
)


class ReadinessError(ValueError):
    """Le manifeste ou la configuration G2 est incohérent."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReadinessError(f"manifeste illisible: {path}") from exc
    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        raise ReadinessError("datasets doit être une liste")
    return payload


def _dataset_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for dataset in manifest["datasets"]:
        dataset_id = dataset.get("id")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ReadinessError("identifiant de source absent")
        if dataset_id in index:
            raise ReadinessError(f"identifiant dupliqué: {dataset_id}")
        index[dataset_id] = dataset
    return index


def _check_source(repo_root: Path, dataset_id: str, entry: dict[str, Any] | None) -> dict[str, Any]:
    if entry is None:
        return {
            "id": dataset_id,
            "status": "MANIFEST_ENTRY_MISSING",
            "ready": False,
        }
    relative_path = entry.get("local_file")
    expected_hash = entry.get("sha256")
    expected_bytes = entry.get("bytes")
    if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
        return {
            "id": dataset_id,
            "status": "MANIFEST_FIELDS_INVALID",
            "ready": False,
            "local_file": relative_path,
            "expected_sha256": expected_hash,
        }
    path = repo_root / relative_path
    result: dict[str, Any] = {
        "id": dataset_id,
        "local_file": relative_path,
        "expected_sha256": expected_hash,
        "expected_bytes": expected_bytes,
        "ready": False,
    }
    if not path.is_file():
        result["status"] = "FILE_MISSING"
        return result
    observed_hash = sha256_file(path)
    observed_bytes = path.stat().st_size
    result.update(observed_sha256=observed_hash, observed_bytes=observed_bytes)
    if observed_hash != expected_hash:
        result["status"] = "HASH_MISMATCH"
        return result
    if isinstance(expected_bytes, int) and observed_bytes != expected_bytes:
        result["status"] = "SIZE_MISMATCH"
        return result
    additional_checks = []
    for additional in entry.get("additional_files", []):
        additional_path = repo_root / str(additional.get("local_file", ""))
        additional_check: dict[str, Any] = {
            "local_file": additional.get("local_file"),
            "expected_sha256": additional.get("sha256"),
            "expected_bytes": additional.get("bytes"),
            "ready": False,
        }
        if not additional_path.is_file():
            additional_check["status"] = "FILE_MISSING"
        else:
            additional_check["observed_sha256"] = sha256_file(additional_path)
            additional_check["observed_bytes"] = additional_path.stat().st_size
            if additional_check["observed_sha256"] != additional.get("sha256"):
                additional_check["status"] = "HASH_MISMATCH"
            elif isinstance(additional.get("bytes"), int) and additional_check[
                "observed_bytes"
            ] != additional["bytes"]:
                additional_check["status"] = "SIZE_MISMATCH"
            else:
                additional_check.update(status="VERIFIED", ready=True)
        additional_checks.append(additional_check)
    if additional_checks:
        result["additional_file_checks"] = additional_checks
    if any(not item["ready"] for item in additional_checks):
        result["status"] = "ADDITIONAL_FILE_INVALID"
        return result
    result.update(status="VERIFIED", ready=True)
    return result


def _inventory_controls(repo_root: Path, paths: Iterable[str]) -> list[dict[str, Any]]:
    inventory = []
    for relative_path in paths:
        path = repo_root / relative_path
        row: dict[str, Any] = {"path": relative_path, "present": path.is_file()}
        if path.is_file():
            row.update(bytes=path.stat().st_size, sha256=sha256_file(path))
        inventory.append(row)
    return inventory


def build_readiness_report(
    repo_root: Path = ROOT,
    manifest_path: Path | None = None,
    required_source_ids: Iterable[str] = REQUIRED_SOURCE_IDS,
    protocol_path: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path or repo_root / "RL" / "data_manifest.json"
    protocol_path = protocol_path or repo_root / "RL" / "docs" / "PROTOCOLE_G2_MATERIALITE_EMPIRIQUE.md"
    manifest = _load_manifest(manifest_path)
    index = _dataset_index(manifest)
    source_checks = [
        _check_source(repo_root, dataset_id, index.get(dataset_id))
        for dataset_id in required_source_ids
    ]
    ready = all(check["ready"] for check in source_checks)
    blockers = [
        {"id": check["id"], "status": check["status"]}
        for check in source_checks
        if not check["ready"]
    ]
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "study": "G2_EMPIRICAL_SEQUENTIALITY",
        "protocol_status": "FROZEN_RETROSPECTIVE_DIAGNOSTIC",
        "documentary_verdict": "READY_FOR_G2_EXECUTION" if ready else "DOCUMENTARY_BLOCK",
        "performance_computed": False,
        "source_checks": source_checks,
        "blockers": blockers,
        "published_controls": _inventory_controls(repo_root, PUBLISHED_CONTROL_PATHS),
        "published_controls_can_replace_raw_sources": False,
        "performance_outputs_authorized": ready,
    }
    if protocol_path.is_file():
        try:
            protocol_relative = str(protocol_path.resolve().relative_to(repo_root))
        except ValueError:
            protocol_relative = str(protocol_path.resolve())
        report["protocol"] = {
            "path": protocol_relative,
            "sha256": sha256_file(protocol_path),
        }
    else:
        report["protocol"] = {"path": str(protocol_path), "status": "FILE_MISSING"}
        report["documentary_verdict"] = "DOCUMENTARY_BLOCK"
        report["performance_outputs_authorized"] = False
        report["blockers"].append({"id": "g2_protocol", "status": "FILE_MISSING"})
    return report


def write_readiness_only(report: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    if report["documentary_verdict"] == "DOCUMENTARY_BLOCK":
        forbidden = [name for name in PERFORMANCE_OUTPUT_NAMES if (output_dir / name).exists()]
        if forbidden:
            raise ReadinessError(
                "sorties de performance présentes malgré le blocage: " + ", ".join(forbidden)
            )
    path = output_dir / "readiness_report.json"
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_readiness_report(args.repo_root, args.manifest)
    path = write_readiness_only(report, args.output_dir)
    print(json.dumps({"verdict": report["documentary_verdict"], "report": str(path)}))
    return 0 if report["documentary_verdict"] == "READY_FOR_G2_EXECUTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
