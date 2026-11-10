#!/usr/bin/env python3
"""G3A — valeur incrémentale de l'apprentissage, close-à-close seulement."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sequentiality_test import (
    MarkovAllocationModel, default_model, solve_dynamic_program, solve_myopic_policy
)

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "RL/results/g3_learning_value"
SOURCE_IDS = {
    "SPY": "yahoo_spy_chart_ohlcv_20261019",
    "BIL": "yahoo_bil_chart_ohlcv_20261019",
}
START = date(2007, 5, 30)
INITIAL_END = date(2024, 5, 28)
EVAL_START = date(2025, 6, 2)
EVAL_END = date(2026, 4, 13)
TERMINAL = date(2026, 4, 17)
COST, CAPITAL, WARMUP, THRESHOLD = .001, 100_000., 4, 250.
POLICIES = ("D_G2_FROZEN", "D_G3_LEARNED", "M_G3_LEARNED")
FIELDS = {
    "model_estimates.csv": ("date", "n_risk_on", "n_risk_off",
        "mu_spy_on", "mu_bil_on", "mu_spy_off", "mu_bil_off",
        "p_on_on", "p_off_on", "latest_training_outcome"),
    "policy_decisions.csv": ("date", "next_close", "policy", "regime",
        "signal_x", "inherited_weight", "target_weight", "turnover",
        "cost_fraction", "log_return_spy", "log_return_bil"),
    "wealth_paths.csv": ("date", "policy", "wealth", "drawdown"),
    "paired_comparison.csv": ("challenger", "baseline", "terminal_challenger",
        "terminal_baseline", "difference_usd", "log_wealth_difference",
        "volatility_annualized_challenger", "volatility_annualized_baseline",
        "max_drawdown_challenger", "max_drawdown_baseline",
        "turnover_challenger", "turnover_baseline",
        "target_changes_challenger", "target_changes_baseline",
        "disagreement_frequency"),
}

class G3Error(ValueError):
    """Une frontière du protocole G3 n'est pas satisfaite."""

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_inputs(root: Path) -> dict:
    """Empreintes des sources originales : aucune sortie de performance ici."""
    root = root.resolve()
    manifest = root / "RL/data_manifest.json"
    protocol = root / "RL/docs/PROTOCOLE_G3_VALEUR_APPRENTISSAGE.md"
    checks = []
    for label, path in (("manifest", manifest), ("protocol", protocol)):
        checks.append({"source": label,
                       "status": "VERIFIED" if path.is_file() else "FILE_MISSING",
                       "sha256": sha256(path) if path.is_file() else None})
    index = {}
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        for item in data["datasets"]:
            if item["id"] in index:
                raise G3Error("duplicate dataset id: " + item["id"])
            index[item["id"]] = item
    paths = {}
    for symbol, identifier in SOURCE_IDS.items():
        item = index.get(identifier)
        if not item:
            checks.append({"source": symbol, "id": identifier,
                           "status": "MANIFEST_ENTRY_MISSING"})
            continue
        relative = Path(item["local_file"])
        if relative.is_absolute() or ".." in relative.parts:
            raise G3Error("unsafe raw source path")
        path = root / relative
        observed = sha256(path) if path.is_file() else None
        status = ("FILE_MISSING" if observed is None else
                  "HASH_MISMATCH" if observed != item["sha256"] else
                  "SIZE_MISMATCH" if path.stat().st_size != item["bytes"]
                  else "VERIFIED")
        checks.append({"source": symbol, "id": identifier, "status": status,
                       "expected_sha256": item["sha256"], "observed_sha256": observed})
        if status == "VERIFIED":
            paths[symbol] = path
    ready = len(checks) == 4 and all(x["status"] == "VERIFIED" for x in checks)
    return {"verdict": "READY_FOR_G3_EXECUTION" if ready else "DOCUMENTARY_BLOCK",
            "checks": checks, "paths": paths}

def parse_closes(path: Path, ticker: str) -> dict[date, float]:
    doc = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    try:
        result = doc["chart"]["result"][0]
        meta = result["meta"]
        stamps = result["timestamp"]
        prices = result["indicators"]["quote"][0]["close"]
    except (KeyError, IndexError, TypeError) as exc:
        raise G3Error("invalid Yahoo chart: " + ticker) from exc
    if (meta.get("symbol") != ticker or meta.get("currency") != "USD"
            or meta.get("exchangeTimezoneName") != "America/New_York"
            or meta.get("dataGranularity") != "1d"
            or len(stamps) != len(prices)):
        raise G3Error("incompatible Yahoo metadata: " + ticker)
    closes = {}
    for timestamp, raw in zip(stamps, prices):
        day = datetime.fromtimestamp(int(timestamp),
            ZoneInfo("America/New_York")).date()
        value = float(raw)
        if day in closes or not math.isfinite(value) or value <= 0:
            raise G3Error("duplicate or invalid close: " + ticker)
        closes[day] = value
    return closes

def common_weekly(spy: dict, bil: dict) -> list:
    """Sélection de la première clôture commune par semaine ISO."""
    selected, used = [], set()
    for day in sorted(spy.keys() & bil.keys()):
        if not START <= day <= TERMINAL:
            continue
        key = day.isocalendar()[:2]
        if key not in used:
            selected.append((day, spy[day], bil[day]))
            used.add(key)
    return selected

def samples(weekly: list) -> list[dict]:
    observations = []
    for i in range(4, len(weekly)):
        day, spy, bil = weekly[i]
        earlier = weekly[i-4]
        signal = math.log(spy/earlier[1]) - math.log(bil/earlier[2])
        observations.append({"idx": i, "date": day, "signal": signal,
                             "state": "RISK_ON" if signal >= 0 else "RISK_OFF"})
    return observations

def estimate(weekly: list, observations: list, decision: date) -> tuple:
    """Rendements d'entraînement dont la date de fin est < décision."""
    n = {"RISK_ON": 0, "RISK_OFF": 0}
    sums = {s: [0., 0.] for s in n}
    n_trans = {s: {"RISK_ON": 0, "RISK_OFF": 0} for s in n}
    obs_by_i = {o["idx"]: o for o in observations}
    latest = None
    for item in observations:
        i, state = item["idx"], item["state"]
        if i + 1 >= len(weekly):
            continue
        start_day, outcome_day = weekly[i][0], weekly[i+1][0]
        # L'épisode G2 2024–2025 reste une zone interdite pour
        # l'estimation primaire. La fenêtre croissante reprend seulement
        # avec les rendements G3 déjà réalisés avant la décision courante.
        initial_training = START <= start_day and outcome_day <= INITIAL_END
        online_g3_training = start_day >= EVAL_START and outcome_day < decision
        if outcome_day >= decision or not (initial_training or online_g3_training):
            continue
        n[state] += 1
        sums[state][0] += math.log(weekly[i+1][1]/weekly[i][1])
        sums[state][1] += math.log(weekly[i+1][2]/weekly[i][2])
        next_state = obs_by_i.get(i+1)
        if next_state is not None:
            n_trans[state][next_state["state"]] += 1
        latest = weekly[i+1][0]
    if latest is None or min(n.values()) == 0:
        raise G3Error("insufficient pre-decision observations")
    mu = {s: (sums[s][0]/n[s], sums[s][1]/n[s]) for s in n}
    transitions = {}
    for s in n:
        count = sum(n_trans[s].values())
        transitions[s] = {s2: (n_trans[s][s2] + .5)/(count + 1.)
                          for s2 in n}
    frozen = default_model(horizon=12)
    model = MarkovAllocationModel(
        states=frozen.states, actions=frozen.actions, returns=mu,
        transition=transitions,
        initial_probabilities=frozen.initial_probabilities,
        initial_weight_spy=frozen.initial_weight_spy, horizon=frozen.horizon)
    model.validate()
    row = {"date": decision.isoformat(), "n_risk_on": n["RISK_ON"],
           "n_risk_off": n["RISK_OFF"], "mu_spy_on": mu["RISK_ON"][0],
           "mu_bil_on": mu["RISK_ON"][1], "mu_spy_off": mu["RISK_OFF"][0],
           "mu_bil_off": mu["RISK_OFF"][1],
           "p_on_on": transitions["RISK_ON"]["RISK_ON"],
           "p_off_on": transitions["RISK_OFF"]["RISK_ON"],
           "latest_training_outcome": latest.isoformat()}
    return model, row

def csv_write(path: Path, columns: tuple, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, columns, lineterminator="\n")
        writer.writeheader()
        for item in rows:
            writer.writerow({k: format(v, ".12f") if isinstance(v, float) else v
                             for k, v in item.items()})

def simulate(weekly: list) -> dict:
    days = {x[0] for x in weekly}
    if not {START, INITIAL_END, EVAL_START, EVAL_END, TERMINAL} <= days:
        raise G3Error("frozen dates missing")
    if weekly[-1][0] != TERMINAL:
        raise G3Error("terminal not at end")
    observations = samples(weekly)
    signals = {o["date"]: o for o in observations}
    evaluation = [(i, r) for i, r in enumerate(weekly)
                  if EVAL_START <= r[0] <= EVAL_END]
    if len(evaluation) < 5 or evaluation[0][1][0] != EVAL_START or evaluation[-1][1][0] != EVAL_END:
        raise G3Error("incomplete primary interval")
    frozen = solve_dynamic_program(default_model(horizon=12), COST)
    previous = {p: .5 for p in POLICIES}
    wealth = {p: CAPITAL for p in POLICIES}
    peaks = {p: CAPITAL for p in POLICIES}
    turns = {p: 0. for p in POLICIES}
    changes = {p: 0 for p in POLICIES}
    logs = {p: [] for p in POLICIES}
    paths = [{"date": EVAL_START.isoformat(), "policy": p,
              "wealth": CAPITAL, "drawdown": 0.} for p in POLICIES]
    estimates, decisions = [], []
    for step, (i, row) in enumerate(evaluation):
        day = row[0]
        obs = signals[day]
        model, params = estimate(weekly, observations, day)
        estimates.append(params)
        dynamic = solve_dynamic_program(model, COST)
        myopic = solve_myopic_policy(model, COST)
        if i+1 >= len(weekly):
            raise G3Error("missing next close")
        following = weekly[i+1]
        expected_end = TERMINAL if step == len(evaluation)-1 else following[0]
        if following[0] != expected_end:
            raise G3Error("next weekly close/terminal mismatch")
        rs = math.log(following[1]/row[1])
        rb = math.log(following[2]/row[2])
        for policy in POLICIES:
            old = previous[policy]
            if step < WARMUP:
                action = .5
            elif policy == "D_G2_FROZEN":
                action = frozen.actions[(0, obs["state"], old)]
            elif policy == "D_G3_LEARNED":
                action = dynamic.actions[(0, obs["state"], old)]
            else:
                action = myopic.actions[(0, obs["state"], old)]
            changed = abs(action-old)
            fee = COST*changed
            netlog = action*rs + (1-action)*rb + math.log1p(-fee)
            wealth[policy] *= math.exp(netlog)
            turns[policy] += changed
            changes[policy] += int(old != action)
            previous[policy] = action
            peaks[policy] = max(peaks[policy], wealth[policy])
            logs[policy].append(netlog)
            decisions.append({"date": day.isoformat(),
                "next_close": following[0].isoformat(), "policy": policy,
                "regime": obs["state"], "signal_x": obs["signal"],
                "inherited_weight": old, "target_weight": action,
                "turnover": changed, "cost_fraction": fee,
                "log_return_spy": rs, "log_return_bil": rb})
            paths.append({"date": following[0].isoformat(),
                "policy": policy, "wealth": wealth[policy],
                "drawdown": 1-wealth[policy]/peaks[policy]})
    metric = {}
    for p in POLICIES:
        metric[p] = {
            "wealth": wealth[p],
            "vol": statistics.stdev(logs[p])*math.sqrt(52),
            "mdd": max(row["drawdown"] for row in paths if row["policy"] == p),
            "turnover": turns[p], "changes": changes[p],
        }
    comparison = []
    for challenger in POLICIES[1:]:
        a, b = metric[challenger], metric[POLICIES[0]]
        aa = [x for x in decisions if x["policy"] == challenger]
        bb = [x for x in decisions if x["policy"] == POLICIES[0]]
        disagreements = sum(x["target_weight"] != y["target_weight"]
                            for x, y in zip(aa, bb))
        comparison.append({"challenger": challenger, "baseline": POLICIES[0],
            "terminal_challenger": a["wealth"],
            "terminal_baseline": b["wealth"],
            "difference_usd": a["wealth"]-b["wealth"],
            "log_wealth_difference": math.log(a["wealth"]/b["wealth"]),
            "volatility_annualized_challenger": a["vol"],
            "volatility_annualized_baseline": b["vol"],
            "max_drawdown_challenger": a["mdd"],
            "max_drawdown_baseline": b["mdd"],
            "turnover_challenger": a["turnover"],
            "turnover_baseline": b["turnover"],
            "target_changes_challenger": a["changes"],
            "target_changes_baseline": b["changes"],
            "disagreement_frequency": disagreements/len(aa)})
    delta = comparison[0]["difference_usd"]
    verdict = ("G3_LEARNING_VALUE_POSITIVE" if delta >= THRESHOLD
        else "G3_LEARNING_VALUE_NEGATIVE" if delta <= -THRESHOLD
        else "G3_LEARNING_VALUE_NOT_MATERIAL")
    return {"model_estimates.csv": estimates, "policy_decisions.csv": decisions,
            "wealth_paths.csv": paths, "paired_comparison.csv": comparison,
            "verdict": verdict, "delta": delta}

def run(root: Path, output: Path) -> str:
    readiness = verify_inputs(root)
    if readiness["verdict"] != "READY_FOR_G3_EXECUTION":
        raise G3Error("DOCUMENTARY_BLOCK: original source verification failed")
    prices = {symbol: parse_closes(path, symbol)
              for symbol, path in readiness["paths"].items()}
    if TERMINAL not in prices["SPY"] or TERMINAL not in prices["BIL"]:
        raise G3Error("terminal common close missing")
    weekly = [row for row in common_weekly(prices["SPY"], prices["BIL"])
              if row[0] < TERMINAL]
    if weekly[-1][0] != EVAL_END:
        raise G3Error("last weekly decision missing")
    weekly.append((TERMINAL, prices["SPY"][TERMINAL], prices["BIL"][TERMINAL]))
    result = simulate(weekly)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, columns in FIELDS.items():
        csv_write(output/name, columns, result[name])
        hashes[name] = sha256(output/name)
    report = {
        "schema_version": "g3-learning-value-1.0",
        "study": "G3A_CLOSE_TO_CLOSE", "verdict": result["verdict"],
        "terminal_difference_usd": format(result["delta"], ".12f"),
        "threshold_usd": "250", "initial_capital_usd": "100000",
        "cost_bps": 10,
        "training_policy": {
            "initial_sample_end": INITIAL_END.isoformat(),
            "excluded_g2_episode": "2024-05-29/2025-06-01",
            "online_update_from": EVAL_START.isoformat(),
            "future_returns_strictly_excluded": True
        },
        "period": {"first_decision": EVAL_START.isoformat(),
                   "last_decision": EVAL_END.isoformat(),
                   "terminal": TERMINAL.isoformat()},
        "source_sha256": {symbol: sha256(path)
                          for symbol, path in readiness["paths"].items()},
        "protocol_sha256": sha256(root/"RL/docs/PROTOCOLE_G3_VALEUR_APPRENTISSAGE.md"),
        "output_sha256": hashes,
        "interpretation_boundary": (
            "Exploratory unadjusted close-to-close proxy, not executable returns; "
            "no distribution credits, execution, shares or settlement; not PPO."),
    }
    (output/"g3_report.json").write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2)+"\n",
        encoding="utf-8")
    return result["verdict"]

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = p.parse_args()
    print(json.dumps({"verdict": run(args.repo_root, args.output_dir)}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
