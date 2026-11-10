#!/usr/bin/env python3
"""Teste exactement la valeur de la séquentialité dans le laboratoire V2.

Le marché est une chaîne de Markov exogène. L'action devient le poids SPY
hérité de la période suivante, de sorte que les coûts de rotation peuvent
coupler les décisions. Aucun prix historique ni algorithme RL n'est utilisé.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "RL" / "docs" / "PROTOCOLE_SCIENTIFIQUE_V2.md"
DEFAULT_OUTPUT_DIR = ROOT / "RL" / "results" / "sequentiality_v2"
TOLERANCE = 1e-12


class SequentialityError(ValueError):
    """Paramètre ou état incompatible avec le laboratoire préspecifié."""


@dataclass(frozen=True)
class MarkovAllocationModel:
    states: tuple[str, ...]
    actions: tuple[float, ...]
    returns: Mapping[str, tuple[float, float]]
    transition: Mapping[str, Mapping[str, float]]
    initial_probabilities: Mapping[str, float]
    initial_weight_spy: float
    horizon: int

    def validate(self) -> None:
        if not self.states or not self.actions:
            raise SequentialityError("états et actions non vides requis")
        if self.horizon <= 0:
            raise SequentialityError("horizon strictement positif requis")
        if tuple(sorted(self.actions)) != self.actions:
            raise SequentialityError("actions triées requises")
        if len(set(self.actions)) != len(self.actions):
            raise SequentialityError("actions distinctes requises")
        if any(action < 0 or action > 1 for action in self.actions):
            raise SequentialityError("les poids doivent appartenir à [0,1]")
        if self.initial_weight_spy not in self.actions:
            raise SequentialityError("poids initial absent de l'espace d'actions")
        if set(self.returns) != set(self.states):
            raise SequentialityError("rendements incomplets")
        if set(self.transition) != set(self.states):
            raise SequentialityError("matrice de transition incomplète")
        if set(self.initial_probabilities) != set(self.states):
            raise SequentialityError("distribution initiale incomplète")
        if abs(sum(self.initial_probabilities.values()) - 1.0) > TOLERANCE:
            raise SequentialityError("la distribution initiale ne somme pas à un")
        for state in self.states:
            row = self.transition[state]
            if set(row) != set(self.states):
                raise SequentialityError(f"ligne de transition incomplète: {state}")
            if abs(sum(row.values()) - 1.0) > TOLERANCE:
                raise SequentialityError(f"ligne de transition invalide: {state}")
            if any(probability < 0 for probability in row.values()):
                raise SequentialityError("probabilité négative")
        if any(probability < 0 for probability in self.initial_probabilities.values()):
            raise SequentialityError("probabilité initiale négative")


@dataclass(frozen=True)
class SolvedPolicy:
    actions: Mapping[tuple[int, str, float], float]
    values: Mapping[tuple[int, str, float], float]


@dataclass(frozen=True)
class CostResult:
    cost_bps: int
    dynamic_expected_log_growth: float
    myopic_expected_log_growth: float
    sequential_value_log: float
    wealth_uplift: float
    dynamic_initial_actions: Mapping[str, float]
    myopic_initial_actions: Mapping[str, float]
    reachable_disagreement: bool


def default_model(*, horizon: int = 12) -> MarkovAllocationModel:
    model = MarkovAllocationModel(
        states=("RISK_ON", "RISK_OFF"),
        actions=(0.0, 0.25, 0.5, 0.75, 1.0),
        returns={
            "RISK_ON": (0.002, 0.001),
            "RISK_OFF": (0.0, 0.001),
        },
        transition={
            "RISK_ON": {"RISK_ON": 0.80, "RISK_OFF": 0.20},
            "RISK_OFF": {"RISK_ON": 0.35, "RISK_OFF": 0.65},
        },
        initial_probabilities={"RISK_ON": 0.50, "RISK_OFF": 0.50},
        initial_weight_spy=0.50,
        horizon=horizon,
    )
    model.validate()
    return model


def immediate_log_reward(
    model: MarkovAllocationModel,
    state: str,
    inherited_weight: float,
    action: float,
    cost_rate: float,
) -> float:
    if state not in model.states:
        raise SequentialityError(f"état inconnu: {state}")
    if inherited_weight not in model.actions or action not in model.actions:
        raise SequentialityError("poids hors espace d'actions")
    if cost_rate < 0:
        raise SequentialityError("coût négatif")
    spy_return, bil_return = model.returns[state]
    cost_factor = 1.0 - cost_rate * abs(action - inherited_weight)
    market_factor = 1.0 + action * spy_return + (1.0 - action) * bil_return
    gross_factor = cost_factor * market_factor
    if gross_factor <= 0:
        raise SequentialityError("facteur de richesse non positif")
    return math.log(gross_factor)


def _argmax_action(
    candidates: list[tuple[float, float]], inherited_weight: float
) -> tuple[float, float]:
    best_value = max(value for _, value in candidates)
    tied = [
        (action, value)
        for action, value in candidates
        if abs(value - best_value) <= 1e-15
    ]
    action, value = min(tied, key=lambda item: (abs(item[0] - inherited_weight), item[0]))
    return action, value


def solve_dynamic_program(
    model: MarkovAllocationModel, cost_rate: float
) -> SolvedPolicy:
    model.validate()
    next_values = {
        (state, inherited): 0.0
        for state in model.states
        for inherited in model.actions
    }
    actions: dict[tuple[int, str, float], float] = {}
    values: dict[tuple[int, str, float], float] = {}
    for step in range(model.horizon - 1, -1, -1):
        current_values: dict[tuple[str, float], float] = {}
        for state in model.states:
            for inherited in model.actions:
                candidates = []
                for action in model.actions:
                    continuation = sum(
                        model.transition[state][next_state]
                        * next_values[(next_state, action)]
                        for next_state in model.states
                    )
                    value = immediate_log_reward(
                        model, state, inherited, action, cost_rate
                    ) + continuation
                    candidates.append((action, value))
                action, value = _argmax_action(candidates, inherited)
                actions[(step, state, inherited)] = action
                values[(step, state, inherited)] = value
                current_values[(state, inherited)] = value
        next_values = current_values
    return SolvedPolicy(actions=actions, values=values)


def solve_myopic_policy(
    model: MarkovAllocationModel, cost_rate: float
) -> SolvedPolicy:
    model.validate()
    actions: dict[tuple[int, str, float], float] = {}
    values: dict[tuple[int, str, float], float] = {}
    for step in range(model.horizon):
        for state in model.states:
            for inherited in model.actions:
                candidates = [
                    (
                        action,
                        immediate_log_reward(
                            model, state, inherited, action, cost_rate
                        ),
                    )
                    for action in model.actions
                ]
                action, value = _argmax_action(candidates, inherited)
                actions[(step, state, inherited)] = action
                values[(step, state, inherited)] = value
    return SolvedPolicy(actions=actions, values=values)


def evaluate_policy_exact(
    model: MarkovAllocationModel,
    policy: SolvedPolicy,
    cost_rate: float,
) -> float:
    distribution = {
        (state, model.initial_weight_spy): probability
        for state, probability in model.initial_probabilities.items()
    }
    expected_log_growth = 0.0
    for step in range(model.horizon):
        next_distribution: dict[tuple[str, float], float] = {}
        for (state, inherited), probability in distribution.items():
            action = policy.actions[(step, state, inherited)]
            expected_log_growth += probability * immediate_log_reward(
                model, state, inherited, action, cost_rate
            )
            for next_state, transition_probability in model.transition[state].items():
                key = (next_state, action)
                next_distribution[key] = next_distribution.get(key, 0.0) + (
                    probability * transition_probability
                )
        distribution = next_distribution
    if abs(sum(distribution.values()) - 1.0) > TOLERANCE:
        raise SequentialityError("perte de masse de probabilité")
    return expected_log_growth


def _reachable_disagreement(
    model: MarkovAllocationModel,
    dynamic: SolvedPolicy,
    myopic: SolvedPolicy,
) -> bool:
    reachable = {
        (state, model.initial_weight_spy)
        for state, probability in model.initial_probabilities.items()
        if probability > 0
    }
    for step in range(model.horizon):
        next_reachable: set[tuple[str, float]] = set()
        for state, inherited in reachable:
            dynamic_action = dynamic.actions[(step, state, inherited)]
            myopic_action = myopic.actions[(step, state, inherited)]
            if dynamic_action != myopic_action:
                return True
            for next_state, probability in model.transition[state].items():
                if probability > 0:
                    next_reachable.add((next_state, dynamic_action))
        reachable = next_reachable
    return False


def evaluate_cost(model: MarkovAllocationModel, cost_bps: int) -> CostResult:
    if cost_bps < 0:
        raise SequentialityError("coût négatif")
    cost_rate = cost_bps / 10_000.0
    dynamic = solve_dynamic_program(model, cost_rate)
    myopic = solve_myopic_policy(model, cost_rate)
    dynamic_value = evaluate_policy_exact(model, dynamic, cost_rate)
    myopic_value = evaluate_policy_exact(model, myopic, cost_rate)
    difference = dynamic_value - myopic_value
    return CostResult(
        cost_bps=cost_bps,
        dynamic_expected_log_growth=dynamic_value,
        myopic_expected_log_growth=myopic_value,
        sequential_value_log=difference,
        wealth_uplift=math.expm1(difference),
        dynamic_initial_actions={
            state: dynamic.actions[(0, state, model.initial_weight_spy)]
            for state in model.states
        },
        myopic_initial_actions={
            state: myopic.actions[(0, state, model.initial_weight_spy)]
            for state in model.states
        },
        reachable_disagreement=_reachable_disagreement(model, dynamic, myopic),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _model_payload(model: MarkovAllocationModel) -> dict[str, Any]:
    return {
        "states": list(model.states),
        "actions": list(model.actions),
        "returns": {
            state: {"SPY": model.returns[state][0], "BIL": model.returns[state][1]}
            for state in model.states
        },
        "transition": {
            state: dict(model.transition[state]) for state in model.states
        },
        "initial_probabilities": dict(model.initial_probabilities),
        "initial_weight_spy": model.initial_weight_spy,
        "horizon": model.horizon,
    }


def _result_payload(result: CostResult) -> dict[str, Any]:
    return {
        "cost_bps": result.cost_bps,
        "dynamic_expected_log_growth": result.dynamic_expected_log_growth,
        "myopic_expected_log_growth": result.myopic_expected_log_growth,
        "sequential_value_log": result.sequential_value_log,
        "wealth_uplift": result.wealth_uplift,
        "dynamic_initial_actions": dict(result.dynamic_initial_actions),
        "myopic_initial_actions": dict(result.myopic_initial_actions),
        "reachable_disagreement": result.reachable_disagreement,
    }


def run_experiment(costs_bps: tuple[int, ...] = (0, 5, 10, 25, 50, 100)) -> dict[str, Any]:
    model = default_model()
    results = tuple(evaluate_cost(model, cost) for cost in costs_bps)
    one_step = default_model(horizon=1)
    one_step_equal = all(
        abs(
            evaluate_cost(one_step, cost).dynamic_expected_log_growth
            - evaluate_cost(one_step, cost).myopic_expected_log_growth
        )
        <= TOLERANCE
        for cost in costs_bps
    )
    zero_cost = next(result for result in results if result.cost_bps == 0)
    positive_improvements = [
        result
        for result in results
        if result.cost_bps > 0 and result.sequential_value_log > TOLERANCE
    ]
    controls = {
        "zero_cost_equivalence": abs(zero_cost.sequential_value_log) <= TOLERANCE,
        "one_step_equivalence": one_step_equal,
        "dynamic_weakly_dominates": all(
            result.sequential_value_log >= -TOLERANCE for result in results
        ),
        "probabilities_valid": True,
        "positive_cost_improvement_exists": bool(positive_improvements),
        "reachable_policy_disagreement_exists": any(
            result.reachable_disagreement for result in positive_improvements
        ),
    }
    gate_g1_passed = all(controls.values())
    return {
        "schema_version": "sequentiality-v2.0",
        "status": "STRUCTURAL_TEST_ONLY",
        "model": _model_payload(model),
        "costs_bps": list(costs_bps),
        "tolerance": TOLERANCE,
        "results": [_result_payload(result) for result in results],
        "controls": controls,
        "gate_g1": "PASS" if gate_g1_passed else "FAIL",
        "interpretation_boundary": (
            "G1 démontre seulement une interdépendance synthétique créée par les "
            "coûts et la position héritée; aucune performance historique ou RL."
        ),
        "source_hashes": {
            "script_sha256": _sha256(Path(__file__).resolve()),
            "protocol_sha256": _sha256(PROTOCOL_PATH),
        },
    }


def write_results(report: Mapping[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "sequentiality_results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        fieldnames = (
            "cost_bps",
            "dynamic_expected_log_growth",
            "myopic_expected_log_growth",
            "sequential_value_log",
            "wealth_uplift",
            "dynamic_initial_action_risk_on",
            "dynamic_initial_action_risk_off",
            "myopic_initial_action_risk_on",
            "myopic_initial_action_risk_off",
            "reachable_disagreement",
        )
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for result in report["results"]:
            writer.writerow(
                {
                    "cost_bps": result["cost_bps"],
                    "dynamic_expected_log_growth": format(
                        result["dynamic_expected_log_growth"], ".15f"
                    ),
                    "myopic_expected_log_growth": format(
                        result["myopic_expected_log_growth"], ".15f"
                    ),
                    "sequential_value_log": format(
                        result["sequential_value_log"], ".15f"
                    ),
                    "wealth_uplift": format(result["wealth_uplift"], ".15f"),
                    "dynamic_initial_action_risk_on": result[
                        "dynamic_initial_actions"
                    ]["RISK_ON"],
                    "dynamic_initial_action_risk_off": result[
                        "dynamic_initial_actions"
                    ]["RISK_OFF"],
                    "myopic_initial_action_risk_on": result[
                        "myopic_initial_actions"
                    ]["RISK_ON"],
                    "myopic_initial_action_risk_off": result[
                        "myopic_initial_actions"
                    ]["RISK_OFF"],
                    "reachable_disagreement": result["reachable_disagreement"],
                }
            )
    report_path = output_dir / "sequentiality_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = run_experiment()
    write_results(report, args.output_dir)
    print(json.dumps({"gate_g1": report["gate_g1"], "output_dir": str(args.output_dir)}))
    return 0 if report["gate_g1"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
