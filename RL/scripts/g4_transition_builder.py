#!/usr/bin/env python3
"""Construit les transitions hebdomadaires G4 sans fuite temporelle.

Le module reste volontairement ind�pendant d'un algorithme de contr�le. Il
transforme quatre historiques Yahoo d�j� audit�s en �tats de march� observables
� la cl�ture de d�cision et en r�alisations de march� ult�rieures. La position
h�rit�e et le budget cumulatif de rotation sont ensuite propag�s par une
transition contr�l�e explicite.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from datetime import date, datetime
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


ASSETS = ("SPY", "IEF", "GLD", "BIL")
ACTION_STEP = 0.25
PER_DECISION_TURNOVER_CAP = 0.25
DEFAULT_INITIAL_BUDGET = 2.0
LOOKBACK_WEEKS = 52
YAHOO_DATASET_IDS = {
    "SPY": "yahoo_spy_chart_ohlcv_20261019",
    "IEF": "yahoo_ief_chart_ohlcv_g4",
    "GLD": "yahoo_gld_chart_ohlcv_g4",
    "BIL": "yahoo_bil_chart_ohlcv_20261019",
}


class G4TransitionError(RuntimeError):
    """Le contrat causal ou comptable G4 n'est pas satisfait."""


@dataclass(frozen=True)
class MarketBar:
    day: date
    close: float
    distribution: float = 0.0


@dataclass(frozen=True)
class ControlledState:
    inherited_weights: tuple[float, ...]
    remaining_turnover_budget: float
    wealth: float = 1.0
    wealth_peak: float = 1.0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def simplex_actions(step: float = ACTION_STEP, dimensions: int = 4) -> tuple[tuple[float, ...], ...]:
    denominator = round(1.0 / step)
    if dimensions <= 0 or not math.isclose(step * denominator, 1.0, abs_tol=1e-12):
        raise G4TransitionError("le pas d'action doit partitionner exactement le simplexe")
    actions = []
    for units in product(range(denominator + 1), repeat=dimensions):
        if sum(units) == denominator:
            actions.append(tuple(value / denominator for value in units))
    return tuple(sorted(actions))


def turnover(previous: Sequence[float], target: Sequence[float]) -> float:
    if len(previous) != len(target):
        raise G4TransitionError("dimensions d'allocation incompatibles")
    return 0.5 * sum(abs(float(a) - float(b)) for a, b in zip(previous, target))


def feasible_actions(
    previous: Sequence[float],
    remaining_budget: float,
    per_decision_cap: float = PER_DECISION_TURNOVER_CAP,
) -> tuple[tuple[float, ...], ...]:
    limit = min(float(remaining_budget), float(per_decision_cap))
    return tuple(
        action for action in simplex_actions(dimensions=len(previous))
        if turnover(previous, action) <= limit + 1e-12
    )


def _validate_weights(weights: Sequence[float], expected: int = 4) -> tuple[float, ...]:
    values = tuple(float(value) for value in weights)
    if len(values) != expected or any(value < -1e-12 for value in values):
        raise G4TransitionError("allocation long-only invalide")
    if not math.isclose(sum(values), 1.0, abs_tol=1e-12):
        raise G4TransitionError("l'allocation doit �tre pleinement investie")
    return values


def apply_controlled_transition(
    state: ControlledState,
    target_weights: Sequence[float],
    market_gross_returns: Sequence[float],
    cost_bps: float = 10.0,
    per_decision_cap: float = PER_DECISION_TURNOVER_CAP,
) -> tuple[ControlledState, dict[str, float]]:
    """Propage une d�cision, le budget et les poids d�riv�s apr�s march�."""

    inherited = _validate_weights(state.inherited_weights)
    target = _validate_weights(target_weights, len(inherited))
    gross = tuple(float(value) for value in market_gross_returns)
    if len(gross) != len(target) or any(not math.isfinite(x) or x <= 0 for x in gross):
        raise G4TransitionError("facteurs de croissance de march� invalides")
    if state.remaining_turnover_budget < -1e-12 or state.wealth <= 0 or state.wealth_peak <= 0:
        raise G4TransitionError("�tat contr�l� invalide")
    used = turnover(inherited, target)
    limit = min(state.remaining_turnover_budget, per_decision_cap)
    if used > limit + 1e-12:
        raise G4TransitionError("action infaisable sous le budget de rotation")
    cost_fraction = (cost_bps / 10_000.0) * used
    pre_cost_growth = sum(weight * factor for weight, factor in zip(target, gross))
    net_growth = (1.0 - cost_fraction) * pre_cost_growth
    if net_growth <= 0:
        raise G4TransitionError("croissance nette non positive")
    post_values = tuple(weight * factor for weight, factor in zip(target, gross))
    post_total = sum(post_values)
    next_weights = tuple(value / post_total for value in post_values)
    next_wealth = state.wealth * net_growth
    next_peak = max(state.wealth_peak, next_wealth)
    next_state = ControlledState(
        inherited_weights=next_weights,
        remaining_turnover_budget=max(0.0, state.remaining_turnover_budget - used),
        wealth=next_wealth,
        wealth_peak=next_peak,
    )
    diagnostics = {
        "turnover": used,
        "cost_fraction": cost_fraction,
        "pre_cost_growth": pre_cost_growth,
        "net_growth": net_growth,
        "drawdown": 1.0 - next_wealth / next_peak,
    }
    return next_state, diagnostics


def parse_yahoo_chart(path: Path, expected_symbol: str) -> dict[date, MarketBar]:
    document = json.loads(path.read_text(encoding="utf-8"))
    try:
        if str(document.get("schema_version", "")).startswith("g4-yahoo-causal-slice-"):
            result = document
        else:
            result = document["chart"]["result"][0]
        metadata = result["meta"]
        timestamps = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]
    except (KeyError, IndexError, TypeError) as exc:
        raise G4TransitionError(f"r�ponse Yahoo invalide pour {expected_symbol}") from exc
    if metadata.get("symbol") != expected_symbol or metadata.get("currency") != "USD":
        raise G4TransitionError(f"m�tadonn�es incompatibles pour {expected_symbol}")
    if metadata.get("dataGranularity") != "1d" or len(timestamps) != len(closes):
        raise G4TransitionError(f"granularit� ou tableaux invalides pour {expected_symbol}")
    timezone = ZoneInfo(metadata.get("exchangeTimezoneName", "America/New_York"))
    distributions: dict[date, float] = {}
    for event in ((result.get("events") or {}).get("dividends") or {}).values():
        event_day = datetime.fromtimestamp(int(event["date"]), timezone).date()
        amount = float(event["amount"])
        if not math.isfinite(amount) or amount < 0:
            raise G4TransitionError(f"distribution invalide pour {expected_symbol}")
        distributions[event_day] = distributions.get(event_day, 0.0) + amount
    bars: dict[date, MarketBar] = {}
    for timestamp, raw_close in zip(timestamps, closes):
        day = datetime.fromtimestamp(int(timestamp), timezone).date()
        if raw_close is None:
            raise G4TransitionError(f"cl�ture manquante pour {expected_symbol} au {day}")
        close = float(raw_close)
        if day in bars or not math.isfinite(close) or close <= 0:
            raise G4TransitionError(f"cl�ture dupliqu�e ou invalide pour {expected_symbol}")
        bars[day] = MarketBar(day, close, distributions.get(day, 0.0))
    unmatched = sorted(set(distributions) - set(bars))
    if unmatched:
        raise G4TransitionError(f"distributions hors calendrier pour {expected_symbol}: {unmatched[:3]}")
    return bars


def _sample_covariance(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise G4TransitionError("fen�tre de covariance insuffisante")
    mean_left = statistics.fmean(left)
    mean_right = statistics.fmean(right)
    return sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right)) / (len(left) - 1)


def _last_common_session_by_iso_week(days: Iterable[date]) -> list[date]:
    selected: dict[tuple[int, int], date] = {}
    for day in sorted(days):
        key = day.isocalendar()[:2]
        selected[key] = day
    return list(selected.values())


def build_market_transitions(
    series: Mapping[str, Mapping[date, MarketBar]],
    lookback_weeks: int = LOOKBACK_WEEKS,
) -> list[dict[str, Any]]:
    if tuple(series.keys()) != ASSETS and set(series) != set(ASSETS):
        raise G4TransitionError(f"univers requis: {ASSETS}")
    common_days = set.intersection(*(set(series[symbol]) for symbol in ASSETS))
    if len(common_days) < 260:
        raise G4TransitionError("calendrier commun insuffisant")
    days = sorted(common_days)
    endpoints = _last_common_session_by_iso_week(days)
    day_position = {day: index for index, day in enumerate(days)}
    daily_gross: dict[str, dict[date, float]] = {symbol: {} for symbol in ASSETS}
    for symbol in ASSETS:
        for previous_day, current_day in zip(days, days[1:]):
            previous = series[symbol][previous_day]
            current = series[symbol][current_day]
            factor = (current.close + current.distribution) / previous.close
            if not math.isfinite(factor) or factor <= 0:
                raise G4TransitionError(f"rendement total invalide pour {symbol} au {current_day}")
            daily_gross[symbol][current_day] = factor
    weekly_logs: dict[str, list[float]] = {symbol: [math.nan] for symbol in ASSETS}
    weekly_gross: dict[str, list[float]] = {symbol: [math.nan] for symbol in ASSETS}
    for previous_endpoint, endpoint in zip(endpoints, endpoints[1:]):
        interval = days[day_position[previous_endpoint] + 1:day_position[endpoint] + 1]
        for symbol in ASSETS:
            factor = math.prod(daily_gross[symbol][day] for day in interval)
            weekly_gross[symbol].append(factor)
            weekly_logs[symbol].append(math.log(factor))
    if len(endpoints) <= lookback_weeks + 1:
        raise G4TransitionError("moins d'un an de d�cisions hebdomadaires")
    rows: list[dict[str, Any]] = []
    for index in range(lookback_weeks, len(endpoints) - 1):
        decision_day = endpoints[index]
        next_day = endpoints[index + 1]
        features: dict[str, Any] = {}
        window_start = index - lookback_weeks + 1
        for symbol in ASSETS:
            values = weekly_logs[symbol]
            trailing_52 = values[window_start:index + 1]
            features[symbol] = {
                "log_return_1w": values[index],
                "log_return_4w": sum(values[index - 3:index + 1]),
                "log_return_13w": sum(values[index - 12:index + 1]),
                "volatility_13w_annualized": statistics.stdev(values[index - 12:index + 1]) * math.sqrt(52.0),
                "volatility_52w_annualized": statistics.stdev(trailing_52) * math.sqrt(52.0),
            }
        covariance = {
            left: {
                right: _sample_covariance(
                    weekly_logs[left][window_start:index + 1],
                    weekly_logs[right][window_start:index + 1],
                ) * 52.0
                for right in ASSETS
            }
            for left in ASSETS
        }
        rows.append({
            "decision_date": decision_day.isoformat(),
            "outcome_end_date": next_day.isoformat(),
            "information_cutoff": decision_day.isoformat(),
            "history_start_52w": endpoints[window_start - 1].isoformat(),
            "features": features,
            "covariance_52w_annualized": covariance,
            "outcome_gross_returns": {
                symbol: weekly_gross[symbol][index + 1] for symbol in ASSETS
            },
        })
    return rows


def _manifest_paths(root: Path) -> dict[str, Path]:
    manifest_path = root / "RL" / "data_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index = {item["id"]: item for item in manifest["datasets"]}
    paths: dict[str, Path] = {}
    for symbol, dataset_id in YAHOO_DATASET_IDS.items():
        if dataset_id not in index:
            raise G4TransitionError(f"source absente du manifeste: {dataset_id}")
        item = index[dataset_id]
        path = root / item["local_file"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise G4TransitionError(f"source absente ou alt�r�e: {dataset_id}")
        paths[symbol] = path
    return paths


def render_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


def run_paths(paths: Mapping[str, Path], output: Path, source_contract: str) -> dict[str, Any]:
    if set(paths) != set(ASSETS):
        raise G4TransitionError("quatre sources SPY/IEF/GLD/BIL sont requises")
    series = {symbol: parse_yahoo_chart(path, symbol) for symbol, path in paths.items()}
    rows = build_market_transitions(series)
    rendered = render_jsonl(rows)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n")
    return {
        "schema_version": "g4-point-in-time-transitions-1.0",
        "verdict": "G4_2_TRANSITIONS_BUILT",
        "rows": len(rows),
        "first_decision": rows[0]["decision_date"],
        "last_decision": rows[-1]["decision_date"],
        "assets": list(ASSETS),
        "action_count": len(simplex_actions()),
        "state_lookback_weeks": LOOKBACK_WEEKS,
        "performance_comparison_performed": False,
        "rl_training_authorized": False,
        "source_contract": source_contract,
        "source_sha256": {symbol: sha256_file(path) for symbol, path in paths.items()},
        "transitions_sha256": sha256_file(output),
    }


def run(root: Path, output: Path) -> dict[str, Any]:
    return run_paths(_manifest_paths(root), output, "G4_1_FROZEN_RAW_SHA256")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--input", action="append", default=[], metavar="SYMBOL=PATH")
    args = parser.parse_args()
    output = args.output or args.repo_root / "data" / "processed" / "rl" / "g4_weekly_market_transitions.jsonl"
    explicit: dict[str, Path] = {}
    for item in args.input:
        symbol, value = item.split("=", 1)
        explicit[symbol.upper()] = Path(value)
    report = (
        run_paths(explicit, output, "G4_CAUSAL_SLICE_SHA256")
        if explicit else run(args.repo_root, output)
    )
    report_path = output.with_suffix(".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
