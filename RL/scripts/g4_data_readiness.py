#!/usr/bin/env python3
"""Audit documentaire G4.1 sans calculer de rendement ni de performance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_PATH = ROOT / "RL" / "configs" / "g4_data_requirements.json"
MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
DEFAULT_OUTPUT_PATH = (
    ROOT / "RL" / "results" / "g4_problem_redesign" / "data_readiness_report.json"
)


class G4DataReadinessError(RuntimeError):
    """Une exigence documentaire G4.1 est invalide."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise G4DataReadinessError(f"JSON invalide: {path}") from exc
    if not isinstance(value, dict):
        raise G4DataReadinessError(f"objet JSON requis: {path}")
    return value


def build_report(root: Path = ROOT) -> dict[str, Any]:
    requirements_path = root / REQUIREMENTS_PATH.relative_to(ROOT)
    manifest_path = root / MANIFEST_PATH.relative_to(ROOT)
    requirements = _load(requirements_path)
    manifest = _load(manifest_path)
    index = {
        item["id"]: item
        for item in manifest.get("datasets", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    rows: list[dict[str, Any]] = []
    for requirement in requirements.get("requirements", []):
        dataset_id = requirement["dataset_id"]
        expected_hash = requirement.get("expected_sha256")
        row = {
            "asset": requirement["asset"],
            "role": requirement["role"],
            "dataset_id": dataset_id,
            "expected_sha256": expected_hash,
        }
        record = index.get(dataset_id)
        if record is None:
            row["status"] = "MISSING_MANIFEST_ENTRY"
        elif not isinstance(expected_hash, str) or record.get("sha256") != expected_hash:
            row["manifest_sha256"] = record.get("sha256")
            row["status"] = "HASH_NOT_FROZEN_OR_MANIFEST_MISMATCH"
        else:
            local_file = record.get("local_file")
            path = root / local_file if isinstance(local_file, str) else None
            if path is None or not path.is_file():
                row["status"] = "LOCAL_BYTES_MISSING"
            else:
                observed = sha256_file(path)
                row["local_file"] = local_file
                row["observed_sha256"] = observed
                row["status"] = (
                    "VERIFIED" if observed == expected_hash else "LOCAL_HASH_MISMATCH"
                )
        rows.append(row)
    blockers = [row for row in rows if row["status"] != "VERIFIED"]
    verdict = "READY_FOR_G4_STATISTICAL_AUDIT" if not blockers else "G4_1_DOCUMENTARY_BLOCK"
    return {
        "schema_version": "g4-data-readiness-1.0",
        "verdict": verdict,
        "performance_computation_authorized": False,
        "statistical_audit_authorized": not blockers,
        "requirements": rows,
        "verified_requirements": len(rows) - len(blockers),
        "total_requirements": len(rows),
        "blockers": blockers,
        "requirements_sha256": sha256_file(requirements_path),
        "manifest_sha256": sha256_file(manifest_path),
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report(ROOT)
    rendered = render_report(report)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise G4DataReadinessError("rapport G4.1 non reproductible")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": report["verdict"]}, ensure_ascii=False))
    return 0 if report["verdict"] == "READY_FOR_G4_STATISTICAL_AUDIT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
