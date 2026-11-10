#!/usr/bin/env python3
"""Restaure les six originaux G2 depuis une ou plusieurs sauvegardes locales.

La restauration est précédée d'un contrôle complet des empreintes. Aucun fichier
n'est copié si une source manque, diffère du manifeste ou si une destination
existante contient d'autres octets. Le mode par défaut est une simulation ;
``--apply`` autorise la copie après succès du précontrôle global.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

from g2_empirical_readiness import (
    REQUIRED_SOURCE_IDS,
    ROOT,
    ReadinessError,
    sha256_file,
)


def _manifest_index(manifest_path: Path) -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReadinessError(f"manifeste illisible: {manifest_path}") from exc
    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        raise ReadinessError("datasets doit être une liste")
    return {entry["id"]: entry for entry in datasets if isinstance(entry.get("id"), str)}


def _candidate_paths(backup_roots: Iterable[Path], relative_path: str) -> list[Path]:
    candidates: list[Path] = []
    for root in backup_roots:
        for candidate in (root / relative_path, root / "RL" / relative_path):
            if candidate.is_file() and candidate not in candidates:
                candidates.append(candidate)
    return candidates


def build_restore_plan(
    repo_root: Path,
    backup_roots: Iterable[Path],
    manifest_path: Path | None = None,
    required_source_ids: Iterable[str] = REQUIRED_SOURCE_IDS,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    roots = tuple(Path(root).resolve() for root in backup_roots)
    if not roots:
        raise ReadinessError("au moins une racine de sauvegarde est requise")
    manifest_path = manifest_path or repo_root / "RL" / "data_manifest.json"
    index = _manifest_index(manifest_path)
    rows: list[dict[str, Any]] = []
    blockers: list[dict[str, str]] = []

    for dataset_id in required_source_ids:
        entry = index.get(dataset_id)
        if entry is None:
            row = {"id": dataset_id, "status": "MANIFEST_ENTRY_MISSING"}
            rows.append(row)
            blockers.append({"id": dataset_id, "status": row["status"]})
            continue
        components = [("primary", entry), *[
            (f"additional_{index}", item)
            for index, item in enumerate(entry.get("additional_files", []), start=1)
        ]]
        for component, file_entry in components:
            component_id = dataset_id if component == "primary" else f"{dataset_id}#{component}"
            relative_path = file_entry.get("local_file")
            expected_hash = file_entry.get("sha256")
            expected_bytes = file_entry.get("bytes")
            if not isinstance(relative_path, str) or not isinstance(expected_hash, str):
                row = {"id": component_id, "dataset_id": dataset_id, "status": "MANIFEST_FIELDS_INVALID"}
                rows.append(row)
                blockers.append({"id": component_id, "status": row["status"]})
                continue

            destination = repo_root / relative_path
            row = {
                "id": component_id,
                "dataset_id": dataset_id,
                "component": component,
                "relative_path": relative_path,
                "expected_sha256": expected_hash,
                "expected_bytes": expected_bytes,
                "destination": str(destination),
            }
            if destination.is_file():
                destination_hash = sha256_file(destination)
                row["destination_sha256"] = destination_hash
                if destination_hash == expected_hash and (
                    not isinstance(expected_bytes, int)
                    or destination.stat().st_size == expected_bytes
                ):
                    row["status"] = "ALREADY_PRESENT"
                    rows.append(row)
                    continue
                row["status"] = "DESTINATION_CONFLICT"
                rows.append(row)
                blockers.append({"id": component_id, "status": row["status"]})
                continue

            candidates = _candidate_paths(roots, relative_path)
            checked = [
                {
                    "path": str(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
                for path in candidates
            ]
            row["backup_candidates"] = checked
            valid = [
                item
                for item in checked
                if item["sha256"] == expected_hash
                and (
                    not isinstance(expected_bytes, int)
                    or item["bytes"] == expected_bytes
                )
            ]
            if valid:
                row.update(status="READY_TO_COPY", source=valid[0]["path"])
            elif checked:
                row["status"] = "BACKUP_HASH_MISMATCH"
                blockers.append({"id": component_id, "status": row["status"]})
            else:
                row["status"] = "BACKUP_FILE_MISSING"
                blockers.append({"id": component_id, "status": row["status"]})
            rows.append(row)

    return {
        "schema_version": "1.0",
        "operation": "G2_SOURCE_RESTORE",
        "repo_root": str(repo_root),
        "backup_roots": [str(root) for root in roots],
        "preflight_status": "PASS" if not blockers else "BLOCKED",
        "blockers": blockers,
        "sources": rows,
    }


def apply_restore_plan(plan: dict[str, Any]) -> dict[str, Any]:
    if plan["preflight_status"] != "PASS":
        raise ReadinessError("restauration interdite: précontrôle bloqué")
    repo_root = Path(plan["repo_root"])
    to_copy = [row for row in plan["sources"] if row["status"] == "READY_TO_COPY"]
    with tempfile.TemporaryDirectory(prefix=".g2-restore-", dir=repo_root) as temporary:
        staging_root = Path(temporary)
        staged: list[tuple[Path, Path, dict[str, Any]]] = []
        for row in to_copy:
            source = Path(row["source"])
            relative = Path(row["relative_path"])
            stage = staging_root / relative
            stage.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, stage)
            if sha256_file(stage) != row["expected_sha256"]:
                raise ReadinessError(f"copie intermédiaire invalide: {row['id']}")
            staged.append((stage, repo_root / relative, row))
        for stage, destination, row in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage, destination)
            row["status"] = "RESTORED"
            row["restored_sha256"] = sha256_file(destination)
    plan["apply_status"] = "APPLIED"
    plan["restored_count"] = len(to_copy)
    return plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-root", action="append", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_restore_plan(args.repo_root, args.backup_root, args.manifest)
    if args.apply and plan["preflight_status"] == "PASS":
        apply_restore_plan(plan)
    else:
        plan["apply_status"] = "DRY_RUN" if not args.apply else "NOT_APPLIED"
    print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if plan["preflight_status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
