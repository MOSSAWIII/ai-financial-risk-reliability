#!/usr/bin/env python3
"""Valide la clôture G3A et la seule autorisation documentaire G4.1."""

from __future__ import annotations

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "RL" / "configs" / "g4_problem_redesign.json"
CANONICAL_VALIDATION_PATH = (
    ROOT / "RL" / "results" / "g3_learning_value" / "canonical_validation.json"
)
OUTPUT_PATH = ROOT / "RL" / "results" / "g4_problem_redesign" / "readiness_report.json"


class G4ProtocolError(RuntimeError):
    """Le protocole G4 est incohérent ou prématuré."""


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
        raise G4ProtocolError(f"document invalide: {path}") from exc
    if not isinstance(value, dict):
        raise G4ProtocolError(f"objet JSON requis: {path}")
    return value


def build_report(root: Path = ROOT) -> dict[str, Any]:
    config_path = root / CONFIG_PATH.relative_to(ROOT)
    validation_path = root / CANONICAL_VALIDATION_PATH.relative_to(ROOT)
    config = _load(config_path)
    validation = _load(validation_path)
    instruments = config.get("candidate_instruments", [])
    step = config.get("action_step")
    denominator = round(1 / float(step)) if step is not None else 0
    expected_actions = comb(denominator + len(instruments) - 1, len(instruments) - 1)
    checks = {
        "g3a_is_canonically_validated": validation.get("status")
        == "G3A_CANONICAL_VALIDATED",
        "spy_bil_is_closed_for_rl_necessity": config.get("closed_candidate")
        == "SPY_BIL_RL_NECESSITY",
        "candidate_instruments_are_not_yet_adopted": config.get(
            "instruments_adopted"
        )
        is False,
        "simplex_action_count_is_exact": config.get("expected_action_count")
        == expected_actions
        == 35,
        "turnover_budget_is_endogenous_state": config.get("constraints", {}).get(
            "cumulative_turnover_budget_is_state"
        )
        is True,
        "benchmark_ladder_is_complete": len(config.get("mandatory_benchmarks", []))
        >= 10,
        "only_data_audit_is_authorized": config.get("currently_authorized_gate")
        == "G4_1_DATA_READINESS",
        "no_rl_algorithm_is_authorized": config.get("rl_algorithms_authorized")
        == [],
        "no_performance_is_authorized": config.get(
            "performance_computation_authorized"
        )
        is False,
    }
    if not all(checks.values()):
        raise G4ProtocolError("au moins un invariant G4 a échoué")
    return {
        "schema_version": "g4-protocol-readiness-1.0",
        "verdict": "READY_FOR_G4_DATA_AUDIT",
        "authorized_work": "DOCUMENTARY_AND_STATISTICAL_DATA_AUDIT_ONLY",
        "performance_computation_authorized": False,
        "rl_algorithms_authorized": [],
        "candidate_instruments": instruments,
        "action_count": expected_actions,
        "checks": checks,
        "config_sha256": sha256_file(config_path),
        "g3a_canonical_validation_sha256": sha256_file(validation_path),
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    report = build_report(ROOT)
    rendered = render_report(report)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise G4ProtocolError("rapport G4 non reproductible")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(json.dumps({"verdict": report["verdict"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
