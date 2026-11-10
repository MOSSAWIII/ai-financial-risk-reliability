#!/usr/bin/env python3
"""Exécute G2 : décision myope contre contrôle dynamique dans SPY–BIL."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping, Sequence

from exploratory_buy_hold_spy_bil import _load_json_decimal, _yahoo_prices, load_contract, prepare_episode_data
from g2_empirical_readiness import build_readiness_report, sha256_file
from historical_c1_c2_comparison import (
    CONTRACT_PATH,
    ROOT,
    SYMBOLS,
    CellDefinition,
    RunResult,
    _cells,
    _run_policy,
    _validate_locked_inputs,
    canonical_json,
    decimal_text,
    float_text,
)
from sequentiality_test import default_model, solve_dynamic_program, solve_myopic_policy


DEFAULT_OUTPUT_DIR = ROOT / "RL" / "results" / "g2_empirical_sequentiality"
PROTOCOL_PATH = ROOT / "RL" / "docs" / "PROTOCOLE_G2_MATERIALITE_EMPIRIQUE.md"
READINESS_PATH = DEFAULT_OUTPUT_DIR / "readiness_report.json"
OUTPUT_NAMES = {
    "decisions": "policy_decisions.csv",
    "trajectories": "daily_trajectories.csv",
    "summaries": "financial_summary.csv",
    "comparisons": "paired_comparison.csv",
}
REPORT_NAME = "g2_report.json"
HALF = Decimal("0.5")
MATERIALITY_USD = Decimal("250")


class G2Error(RuntimeError):
    """Violation du protocole G2 gelé."""


@dataclass(frozen=True)
class SignalObservation:
    cycle: int
    price_date: str
    regime: str
    signal_x: float | None


@dataclass(frozen=True)
class G2Result:
    runs: tuple[RunResult, ...]
    decisions: tuple[Mapping[str, Any], ...]
    comparisons: tuple[Mapping[str, Any], ...]
    report: Mapping[str, Any]


def build_signals(
    grid_rows: Sequence[Mapping[str, str]],
    prices: Mapping[str, Mapping[Any, Mapping[str, Decimal]]],
) -> dict[int, SignalObservation]:
    ordered = sorted(grid_rows, key=lambda row: int(row["cycle"]))
    observations: dict[int, SignalObservation] = {}
    for index, row in enumerate(ordered):
        cycle = int(row["cycle"])
        current_date = date.fromisoformat(row["close_reference"])
        if index < 4:
            observations[cycle] = SignalObservation(
                cycle, row["close_reference"], "WARMUP", None
            )
            continue
        prior_row = ordered[index - 4]
        prior_date = date.fromisoformat(prior_row["close_reference"])
        signal = math.log(
            float(prices["SPY"][current_date]["close"] / prices["SPY"][prior_date]["close"])
        ) - math.log(
            float(prices["BIL"][current_date]["close"] / prices["BIL"][prior_date]["close"])
        )
        observations[cycle] = SignalObservation(
            cycle,
            row["close_reference"],
            "RISK_ON" if signal >= 0 else "RISK_OFF",
            signal,
        )
    if len(observations) != 52:
        raise G2Error("signal incomplet")
    return observations


class TargetController:
    def __init__(
        self,
        *,
        policy_id: str,
        cost_bps: Decimal,
        signals: Mapping[int, SignalObservation],
    ) -> None:
        self.policy_id = policy_id
        self.signals = signals
        self.inherited = 0.5
        self.contexts: dict[int, dict[str, Any]] = {}
        model = default_model(horizon=12)
        cost_rate = float(cost_bps / Decimal("10000"))
        if policy_id == "D_G2":
            self.policy = solve_dynamic_program(model, cost_rate)
            self.controller = "DYNAMIC_RECEDING_HORIZON_12"
        elif policy_id == "M_G2":
            self.policy = solve_myopic_policy(model, cost_rate)
            self.controller = "MYOPIC_ONE_STEP"
        else:
            raise G2Error(f"politique inconnue: {policy_id}")

    def resolve(self, cell: CellDefinition, row: Mapping[str, str], _: Any) -> Decimal:
        cycle = int(row["cycle"])
        observation = self.signals[cycle]
        inherited = self.inherited
        if observation.regime == "WARMUP":
            action = 0.5
        else:
            action = self.policy.actions[(0, observation.regime, inherited)]
        self.contexts[cycle] = {
            "policy_id": self.policy_id,
            "controller": self.controller,
            "regime": observation.regime,
            "signal_x": "" if observation.signal_x is None else float_text(observation.signal_x),
            "inherited_target_weight_spy": decimal_text(Decimal(str(inherited))),
            "target_weight_spy": decimal_text(Decimal(str(action))),
        }
        self.inherited = action
        return Decimal(str(action))


def _source_identity(contract: Any, data: Any, strict_hash: str, conditional_hash: str) -> tuple[str, str]:
    manifest = canonical_json(
        {
            "contract_config": contract.config_sha256,
            "strict_grid": strict_hash,
            "conditional_grid": conditional_hash,
            "g2_protocol": sha256_file(PROTOCOL_PATH),
            "data_sources": {
                label: {
                    "id": data.sources[label].record["id"],
                    "sha256": data.sources[label].sha256,
                }
                for label in sorted(data.sources)
            },
        }
    )
    return manifest, hashlib.sha256(manifest.encode("utf-8")).hexdigest()


def _financially_equal(left: RunResult, right: RunResult) -> bool:
    excluded_summary = {"policy_id"}
    if {k: v for k, v in left.summary.items() if k not in excluded_summary} != {
        k: v for k, v in right.summary.items() if k not in excluded_summary
    }:
        return False
    for left_row, right_row in zip(left.trajectories, right.trajectories, strict=True):
        if {k: v for k, v in left_row.items() if k != "policy_id"} != {
            k: v for k, v in right_row.items() if k != "policy_id"
        }:
            return False
    return True


def _verdict(comparisons: Sequence[Mapping[str, Any]]) -> str:
    s3 = {row["cash_convention"]: Decimal(str(row["terminal_wealth_difference_usd"])) for row in comparisons if row["cost_scenario"] == "S3"}
    d1 = s3["D_PLUS_1"]
    d2 = s3["D_PLUS_2"]
    if d1 >= MATERIALITY_USD and d2 > 0:
        return "G2_MATERIAL_POSITIVE"
    if abs(d1) >= MATERIALITY_USD or abs(d2) >= MATERIALITY_USD:
        return "G2_MATERIAL_OTHER"
    return "G2_NOT_MATERIAL"


def run_experiment(repo_root: Path = ROOT) -> G2Result:
    readiness = build_readiness_report(repo_root)
    if readiness["documentary_verdict"] != "READY_FOR_G2_EXECUTION":
        raise G2Error("DOCUMENTARY_BLOCK")
    contract = load_contract(repo_root / CONTRACT_PATH.relative_to(ROOT))
    data = prepare_episode_data(contract, repo_root=repo_root)
    grid_rows, strict_hash, conditional_hash = _validate_locked_inputs(contract, data)
    documents = {symbol: _load_json_decimal(data.sources[symbol].path) for symbol in SYMBOLS}
    prices = {symbol: _yahoo_prices(documents[symbol], symbol) for symbol in SYMBOLS}
    signals = build_signals(grid_rows, prices)
    source_manifest, source_fingerprint = _source_identity(
        contract, data, strict_hash, conditional_hash
    )

    runs: list[RunResult] = []
    enriched_decisions: list[Mapping[str, Any]] = []
    contexts: dict[tuple[str, str], Mapping[int, Mapping[str, Any]]] = {}
    for cell in _cells(contract):
        for policy_id in ("M_G2", "D_G2"):
            controller = TargetController(
                policy_id=policy_id,
                cost_bps=cell.scenario.basis_points,
                signals=signals,
            )
            run = _run_policy(
                contract=contract,
                data=data,
                prices=prices,
                grid_rows=grid_rows,
                cell=cell,
                policy_id=policy_id,
                source_fingerprint=source_fingerprint,
                source_manifest=source_manifest,
                target_weight_resolver=controller.resolve,
            )
            runs.append(run)
            contexts[(cell.cell_id, policy_id)] = controller.contexts
            for row in run.decisions:
                context = controller.contexts[int(row["cycle"])]
                enriched_decisions.append({**row, **context})

    by_key = {(run.cell.cell_id, run.policy_id): run for run in runs}
    comparisons = []
    for cell in _cells(contract):
        myopic = by_key[(cell.cell_id, "M_G2")]
        dynamic = by_key[(cell.cell_id, "D_G2")]
        m = myopic.summary
        d = dynamic.summary
        m_terminal = Decimal(str(m["terminal_wealth_usd"]))
        d_terminal = Decimal(str(d["terminal_wealth_usd"]))
        m_context = contexts[(cell.cell_id, "M_G2")]
        d_context = contexts[(cell.cell_id, "D_G2")]
        comparisons.append(
            {
                "cell_id": cell.cell_id,
                "cost_scenario": cell.scenario.scenario_id,
                "cost_bps": decimal_text(cell.scenario.basis_points),
                "cash_convention": cell.cash_convention.value,
                "myopic_terminal_wealth_usd": decimal_text(m_terminal),
                "dynamic_terminal_wealth_usd": decimal_text(d_terminal),
                "terminal_wealth_difference_usd": decimal_text(d_terminal - m_terminal),
                "terminal_wealth_difference_initial_capital": float_text(float((d_terminal - m_terminal) / contract.initial_cash)),
                "log_terminal_wealth_difference": float_text(math.log(float(d_terminal / m_terminal))),
                "annualized_volatility_difference": float_text(float(d["annualized_volatility"]) - float(m["annualized_volatility"])),
                "maximum_drawdown_difference": float_text(float(d["maximum_drawdown"]) - float(m["maximum_drawdown"])),
                "incremental_fees_usd": decimal_text(Decimal(str(d["cumulative_fees_usd"])) - Decimal(str(m["cumulative_fees_usd"]))),
                "incremental_gross_notional_usd": decimal_text(Decimal(str(d["gross_traded_notional_usd"])) - Decimal(str(m["gross_traded_notional_usd"]))),
                "myopic_target_changes": sum(item["target_weight_spy"] != item["inherited_target_weight_spy"] for item in m_context.values()),
                "dynamic_target_changes": sum(item["target_weight_spy"] != item["inherited_target_weight_spy"] for item in d_context.values()),
                "action_sequences_identical": all(m_context[cycle]["target_weight_spy"] == d_context[cycle]["target_weight_spy"] for cycle in m_context),
                "financial_paths_identical": _financially_equal(myopic, dynamic),
                "source_fingerprint": source_fingerprint,
            }
        )

    controls = {
        "all_runs_complete": len(runs) == 16 and all(run.summary["run_status"] == "COMPLETE" for run in runs),
        "all_decision_journals_complete": all(len(run.decisions) == 52 for run in runs),
        "warmup_equal_50_50": all(
            context[cycle]["target_weight_spy"] == "0.5"
            for context in contexts.values()
            for cycle in range(1, 5)
        ),
        "s0_s1_s2_action_sequences_identical": all(row["action_sequences_identical"] for row in comparisons if row["cost_scenario"] in {"S0", "S1", "S2"}),
        "s0_s1_s2_financial_paths_identical": all(row["financial_paths_identical"] for row in comparisons if row["cost_scenario"] in {"S0", "S1", "S2"}),
        "s3_reachable_disagreement_observed": any(not row["action_sequences_identical"] for row in comparisons if row["cost_scenario"] == "S3"),
        "no_documentary_block": True,
    }
    if not all(controls.values()):
        raise G2Error("un contrôle négatif G2 a échoué")
    verdict = _verdict(comparisons)
    report = {
        "schema_version": "g2-empirical-sequentiality-1.0",
        "status": "COMPLETE",
        "study_status": "FROZEN_RETROSPECTIVE_DIAGNOSTIC",
        "verdict": verdict,
        "g3_authorized": verdict == "G2_MATERIAL_POSITIVE",
        "materiality_threshold_usd": decimal_text(MATERIALITY_USD),
        "primary_cells": [row for row in comparisons if row["cost_scenario"] == "S3"],
        "controls": controls,
        "runs": len(runs),
        "decisions": len(enriched_decisions),
        "source_fingerprint": source_fingerprint,
        "protocol_sha256": sha256_file(PROTOCOL_PATH),
        "readiness_sha256": sha256_file(READINESS_PATH),
        "interpretation_boundary": "Diagnostic rétrospectif sur un épisode consulté; aucune preuve hors échantillon et aucun RL.",
    }
    return G2Result(tuple(runs), tuple(enriched_decisions), tuple(comparisons), report)


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    import csv

    if not rows:
        raise G2Error(f"sortie vide: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(result: G2Result, output_dir: Path) -> Mapping[str, str]:
    rows = {
        "decisions": list(result.decisions),
        "trajectories": [row for run in result.runs for row in run.trajectories],
        "summaries": [run.summary for run in result.runs],
        "comparisons": list(result.comparisons),
    }
    hashes: dict[str, str] = {}
    for key, values in rows.items():
        path = output_dir / OUTPUT_NAMES[key]
        _write_csv(path, values)
        hashes[path.name] = sha256_file(path)
    report = {**result.report, "output_sha256": hashes}
    report_path = output_dir / REPORT_NAME
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    hashes[REPORT_NAME] = sha256_file(report_path)
    return hashes


def check_outputs(result: G2Result, output_dir: Path) -> None:
    with TemporaryDirectory() as temporary:
        candidate = Path(temporary)
        write_outputs(result, candidate)
        for name in (*OUTPUT_NAMES.values(), REPORT_NAME):
            expected = output_dir / name
            rebuilt = candidate / name
            if not expected.is_file() or expected.read_bytes() != rebuilt.read_bytes():
                raise G2Error(f"sortie non reproductible: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run_experiment(ROOT)
    if args.check:
        check_outputs(result, args.output_dir)
        hashes = {name: sha256_file(args.output_dir / name) for name in (*OUTPUT_NAMES.values(), REPORT_NAME)}
    else:
        hashes = write_outputs(result, args.output_dir)
    print(json.dumps({"verdict": result.report["verdict"], "g3_authorized": result.report["g3_authorized"], "output_sha256": hashes}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
