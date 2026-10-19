#!/usr/bin/env python3
"""Reconstruit BIL sous une comptabilité de détention et de paiement.

La série BIL-B est distincte de BIL-A. Elle commence le premier jour de NAV
strictement postérieur à l'événement ambigu du 3 mars 2008, qui reste intact
dans la source et explicitement exclu de la couverture validable.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from RL.scripts.reconstruct_spy_payment_date_returns import (
    annualized_performance,
    legacy_performance,
    simulate_holding,
)
from RL.scripts.reconstruct_total_returns import read_distributions, read_nav
from RL.scripts.validate_official_performance import official_nav_performance


MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
OUTPUT_DIR = ROOT / "data" / "processed" / "rl"
SERIES_PATH = OUTPUT_DIR / "bil_nav_total_returns_payment_date_v1.csv"
REPORT_PATH = OUTPUT_DIR / "bil_payment_date_validation_v1.json"
CODE_VERSION = "1.0.0"
CONVENTION_VERSION = "bil_nav_holding_receivable_payment_reinvestment_v1"
COVERAGE_START = pd.Timestamp("2008-03-04")
AMBIGUOUS_EX_DATE = pd.Timestamp("2008-03-03")
TOLERANCE_PERCENTAGE_POINTS = 0.01

SOURCE_IDS = {
    "BIL_NAV": "ssga_bil_nav_20261019",
    "DISTRIBUTIONS": "ssga_spdr_distributions_20261019",
    "LEGACY_EX_DATE": "bil_nav_total_returns_v1_20261019",
    "OFFICIAL_PAGE": "ssga_bil_fund_page_20261019",
    "SEC_2008": "sec_spdr_series_trust_485bpos_20081028",
    "SSGA_2026_SCHEDULE": "ssga_spdr_distribution_schedule_2026",
}

OFFICIAL_CASES = {
    1: {"start": "2025-09-30", "end": "2026-09-30", "official_percent": 3.6619},
    10: {"start": "2016-09-30", "end": "2026-09-30", "official_percent": 2.2932},
}

SEC_REQUIRED_PASSAGES = [
    "SPDR LEHMAN 1-3 MONTH T-BILL ETF",
    "reinvested at net asset value per share on the respective payment dates of each Fund",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return None if not math.isfinite(float(value)) else float(value)
    return value


def load_sources() -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {record["id"]: record for record in manifest["datasets"]}
    selected: dict[str, dict[str, Any]] = {}
    paths: dict[str, Path] = {}
    for label, identifier in SOURCE_IDS.items():
        record = records[identifier]
        path = ROOT / record["local_file"]
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != record["bytes"] or sha256_file(path) != record["sha256"]:
            raise ValueError(f"Intégrité modifiée pour {identifier}")
        selected[label] = record
        paths[label] = path
    return selected, paths


def normalized_sec_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(raw))).strip()


def verify_documentary_evidence(records: dict[str, dict[str, Any]], paths: dict[str, Path]) -> dict[str, Any]:
    text = normalized_sec_text(paths["SEC_2008"])
    passages = {passage: passage.lower() in text.lower() for passage in SEC_REQUIRED_PASSAGES}
    if not all(passages.values()):
        raise AssertionError(f"Passages SEC absents: {[p for p, found in passages.items() if not found]}")
    return {
        "sec_2008": {
            "source_id": records["SEC_2008"]["id"],
            "sha256": records["SEC_2008"]["sha256"],
            "verified_passages": SEC_REQUIRED_PASSAGES,
            "scope": "Méthode de rendement du SPDR Series Trust incluant BIL; pas preuve des dates exactes de l'événement de mars 2008.",
        },
        "state_street_2026_schedule": {
            "source_id": records["SSGA_2026_SCHEDULE"]["id"],
            "sha256": records["SSGA_2026_SCHEDULE"]["sha256"],
            "scope": "Définitions officielles ex-date/record/payable et calendrier BIL actuel; pas preuve historique de mars 2008.",
        },
    }


def audit_and_prepare_events(distributions: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw = distributions.loc[distributions["TICKER"].eq("BIL")].copy()
    raw = raw.sort_values(["EX-DATE", "PAYABLE DATE"]).reset_index(drop=True)
    chronology_invalid = raw.loc[
        (raw["RECORD DATE"] < raw["EX-DATE"]) | (raw["PAYABLE DATE"] < raw["EX-DATE"])
    ].copy()
    if len(chronology_invalid) != 1 or chronology_invalid.iloc[0]["EX-DATE"] != AMBIGUOUS_EX_DATE:
        raise AssertionError("Ensemble inattendu d'anomalies chronologiques BIL")

    positive = raw.loc[raw["total_distribution_usd"] > 0].copy()
    usable = positive.loc[
        (positive["EX-DATE"] >= COVERAGE_START)
        & (positive["RECORD DATE"] >= positive["EX-DATE"])
        & (positive["PAYABLE DATE"] >= positive["EX-DATE"])
    ].copy()
    usable = usable.rename(
        columns={
            "EX-DATE": "ex_date",
            "RECORD DATE": "record_date",
            "PAYABLE DATE": "payment_date",
            "total_distribution_usd": "amount_per_share_usd",
        }
    )
    usable.insert(0, "event_id", [f"BIL-{date:%Y%m%d}" for date in usable["ex_date"]])
    if usable["event_id"].duplicated().any():
        raise AssertionError("Plusieurs distributions BIL positives partagent une ex-date")

    anomaly_rows = []
    for _, row in chronology_invalid.iterrows():
        anomaly_rows.append(
            {
                "ex_date": row["EX-DATE"].date().isoformat(),
                "record_date": row["RECORD DATE"].date().isoformat(),
                "payment_date": row["PAYABLE DATE"].date().isoformat(),
                "amount_per_share_usd": float(row["total_distribution_usd"]),
            }
        )
    audit = {
        "raw_schedule_rows": len(raw),
        "raw_start": raw["EX-DATE"].min().date().isoformat(),
        "raw_end": raw["EX-DATE"].max().date().isoformat(),
        "missing_ex_dates": int(raw["EX-DATE"].isna().sum()),
        "missing_record_dates": int(raw["RECORD DATE"].isna().sum()),
        "missing_payment_dates": int(raw["PAYABLE DATE"].isna().sum()),
        "zero_amount_rows": int(raw["total_distribution_usd"].eq(0).sum()),
        "positive_amount_rows": int(raw["total_distribution_usd"].gt(0).sum()),
        "chronology_invalid_rows": len(chronology_invalid),
        "chronology_anomalies": anomaly_rows,
        "usable_positive_events": len(usable),
        "excluded_before_coverage_or_ambiguous": int(len(positive) - len(usable)),
    }
    columns = ["event_id", "ex_date", "record_date", "payment_date", "amount_per_share_usd"]
    return usable[columns].reset_index(drop=True), audit


def bil_simulation(
    nav: pd.DataFrame, events: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, mode: str = "payment"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame, ledger = simulate_holding(nav, events, start, end, mode=mode)  # type: ignore[arg-type]
    frame["ticker"] = "BIL"
    return frame, ledger


def event_frame(rows: list[tuple[str, str, str, str, float]]) -> pd.DataFrame:
    frame = pd.DataFrame(
        rows,
        columns=["event_id", "ex_date", "record_date", "payment_date", "amount_per_share_usd"],
    )
    for column in ["ex_date", "record_date", "payment_date"]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def validate_event_dates(events: pd.DataFrame) -> None:
    required = ["ex_date", "record_date", "payment_date"]
    if events[required].isna().any().any():
        raise ValueError("Date de distribution absente ou illisible")
    if ((events["record_date"] < events["ex_date"]) | (events["payment_date"] < events["ex_date"])).any():
        raise ValueError("Chronologie de distribution invalide")


def run_synthetic_tests() -> dict[str, bool]:
    dates = pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-05", "2026-01-06"])
    nav = pd.DataFrame({"date": dates, "nav_usd": [100.0, 98.0, 98.0, 98.0]})
    one = event_frame([("A", "2026-01-02", "2026-01-02", "2026-01-05", 2.0)])
    frame, ledger = bil_simulation(nav, one, dates[0], dates[-1])
    assert math.isclose(frame.loc[1, "distribution_receivable_usd"], 2.0, abs_tol=1e-12)
    assert math.isclose(frame.loc[2, "wealth_usd"], 100.0, abs_tol=1e-12)
    assert ledger.iloc[0]["status_at_end"] == "REINVESTED"

    pending, pending_ledger = bil_simulation(nav.iloc[:3], one.assign(payment_date=dates[-1]), dates[0], dates[2])
    assert pending.iloc[-1]["distribution_receivable_usd"] == 2.0
    assert pending_ledger.iloc[0]["status_at_end"] == "RECEIVABLE"

    pre_entry = one.assign(ex_date=dates[0], record_date=dates[0])
    pre_frame, pre_ledger = bil_simulation(nav, pre_entry, dates[1], dates[-1])
    assert pre_ledger.empty and pre_frame["payment_received_usd"].sum() == 0

    simultaneous = event_frame(
        [
            ("B", "2026-01-02", "2026-01-02", "2026-01-06", 1.0),
            ("C", "2026-01-05", "2026-01-05", "2026-01-06", 3.0),
        ]
    )
    multi, multi_ledger = bil_simulation(nav, simultaneous, dates[0], dates[-1])
    assert multi["pending_claim_count"].max() == 2 and len(multi_ledger) == 2

    zero = event_frame([("ZERO", "2026-01-02", "2026-01-02", "2026-01-05", 0.0)])
    economic_zero = zero.loc[zero["amount_per_share_usd"] > 0]
    zero_frame, zero_ledger = bil_simulation(nav, economic_zero, dates[0], dates[-1])
    assert zero_ledger.empty and zero_frame["claim_created_usd"].sum() == 0

    split_nav = nav.copy()
    split_nav["split_factor_current_per_previous"] = [1.0, 1.0, 0.5, 1.0]
    split_nav["nav_usd"] = [100.0, 98.0, 196.0, 196.0]
    split_only, _ = bil_simulation(split_nav, economic_zero, dates[0], dates[-1])
    assert split_only.loc[2, "shares_held"] == 0.5
    assert math.isclose(split_only.loc[1, "wealth_usd"], split_only.loc[2, "wealth_usd"], abs_tol=1e-12)

    split_pending, _ = bil_simulation(split_nav, one.assign(payment_date=dates[-1]), dates[0], dates[-1])
    assert split_pending.loc[1, "distribution_receivable_usd"] == 2.0
    assert split_pending.loc[2, "distribution_receivable_usd"] == 2.0

    same_day = event_frame([("SAME", "2026-01-02", "2026-01-02", "2026-01-02", 2.0)])
    same_frame, same_ledger = bil_simulation(nav, same_day, dates[0], dates[-1])
    assert same_frame.loc[1, "payment_received_usd"] == 2.0
    assert same_frame.loc[1, "distribution_receivable_usd"] == 0.0
    assert same_ledger.iloc[0]["status_at_end"] == "REINVESTED"

    invalid_rejected = False
    missing_rejected = False
    try:
        validate_event_dates(event_frame([("BAD", "2026-01-05", "2026-01-05", "2026-01-02", 1.0)]))
    except ValueError:
        invalid_rejected = True
    try:
        validate_event_dates(event_frame([("MISS", "2026-01-02", "2026-01-02", "", 1.0)]))
    except ValueError:
        missing_rejected = True
    assert invalid_rejected and missing_rejected

    created = float(multi["claim_created_usd"].sum())
    paid = float(multi["payment_received_usd"].sum())
    ending = float(multi["distribution_receivable_usd"].iloc[-1])
    assert math.isclose(created, paid + ending, abs_tol=1e-12)
    assert multi["transfer_identity_error"].max() <= 1e-12

    return {
        "claim_acquired_then_paid": True,
        "pending_claim_at_end": True,
        "pre_entry_ex_date_excluded": True,
        "simultaneous_claims_supported": True,
        "zero_distribution_has_no_economic_effect": True,
        "reverse_split_two_old_for_one_new_conserves_wealth": True,
        "split_does_not_rescale_monetary_claim": True,
        "same_day_ex_date_and_payment_supported": True,
        "invalid_payment_date_rejected": True,
        "missing_payment_date_rejected": True,
        "claim_balance_and_transfer_no_double_counting": True,
    }


def build(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    records, paths = load_sources()
    documentary = verify_documentary_evidence(records, paths)
    synthetic = run_synthetic_tests()

    nav = read_nav(paths["BIL_NAV"], "BIL")
    legacy = pd.read_csv(paths["LEGACY_EX_DATE"], parse_dates=["date"])
    split_factors = legacy[["date", "split_factor_current_per_previous"]]
    nav = nav.merge(split_factors, on="date", how="left", validate="one_to_one")
    if nav["split_factor_current_per_previous"].isna().any():
        raise AssertionError("Facteur de split BIL absent")
    split_rows = nav.loc[nav["split_factor_current_per_previous"].ne(1.0)]
    if len(split_rows) != 1 or split_rows.iloc[0]["date"] != pd.Timestamp("2017-11-30"):
        raise AssertionError("Événement de split BIL inattendu")
    if not math.isclose(float(split_rows.iloc[0]["split_factor_current_per_previous"]), 0.5):
        raise AssertionError("Ratio de regroupement BIL inattendu")

    distributions = read_distributions(paths["DISTRIBUTIONS"])
    events, distribution_audit = audit_and_prepare_events(distributions)
    validate_event_dates(events)
    nav = nav.loc[nav["date"] >= COVERAGE_START].reset_index(drop=True)
    if nav.iloc[0]["date"] != COVERAGE_START:
        raise AssertionError("La première NAV post-anomalie attendue est absente")

    full_series, full_ledger = bil_simulation(nav, events, nav["date"].min(), nav["date"].max())
    if not full_series["date"].equals(nav["date"]):
        raise AssertionError("Calendrier BIL-B modifié")
    created = float(full_series["claim_created_usd"].sum())
    paid = float(full_series["payment_received_usd"].sum())
    ending_receivable = float(full_series["distribution_receivable_usd"].iloc[-1])
    if not math.isclose(created, paid + ending_receivable, abs_tol=1e-10):
        raise AssertionError("Identité du registre de créances non respectée")
    wealth_error = (
        full_series["wealth_usd"]
        - full_series["shares_held"] * full_series["nav_usd"]
        - full_series["cash_usd"]
        - full_series["distribution_receivable_usd"]
    ).abs()
    if wealth_error.max() > 1e-10 or full_series["transfer_identity_error"].max() > 1e-10:
        raise AssertionError("Identité de richesse ou transfert non conservatif")

    official_date, official_values = official_nav_performance(paths["OFFICIAL_PAGE"])
    if pd.Timestamp(official_date).date().isoformat() != "2026-09-30":
        raise AssertionError(f"Date officielle inattendue: {official_date}")
    comparisons = []
    for years, case in OFFICIAL_CASES.items():
        official = float(official_values[years]["official_percent"])
        if official != case["official_percent"]:
            raise AssertionError(f"Performance officielle inattendue à {years} an(s): {official}")
        start, end = pd.Timestamp(case["start"]), pd.Timestamp(case["end"])
        payment, ledger = bil_simulation(nav, events, start, end)
        value_a = legacy_performance(legacy, case["start"], case["end"], years)
        value_b = annualized_performance(payment, years)
        comparisons.append(
            {
                "years": years,
                "start_date": case["start"],
                "end_date": case["end"],
                "aggregation": "cumulative" if years == 1 else "geometric annualized",
                "official_percent": official,
                "convention_a_ex_date_percent": value_a,
                "convention_b_payment_holding_percent": value_b,
                "signed_gap_a_percentage_points": value_a - official,
                "signed_gap_b_percentage_points": value_b - official,
                "absolute_gap_a_percentage_points": abs(value_a - official),
                "absolute_gap_b_percentage_points": abs(value_b - official),
                "effect_b_minus_a_percentage_points": value_b - value_a,
                "tolerance_percentage_points": TOLERANCE_PERCENTAGE_POINTS,
                "convention_a_pass": abs(value_a - official) <= TOLERANCE_PERCENTAGE_POINTS,
                "convention_b_pass": abs(value_b - official) <= TOLERANCE_PERCENTAGE_POINTS,
                "distribution_count": len(ledger),
                "pending_distribution_count_at_end": int(ledger["status_at_end"].eq("RECEIVABLE").sum()),
            }
        )

    all_pass = all(row["convention_b_pass"] for row in comparisons)
    report = {
        "schema_version": "1.0",
        "code_version": CODE_VERSION,
        "convention_version": CONVENTION_VERSION,
        "produced_at": "2026-10-19",
        "status": "VALIDATED_FOR_USE" if all_pass else "AUDITED",
        "allowed_use": "BIL NAV total-return analysis from 2008-03-04 under payment-date holding convention; no execution or external trading costs",
        "coverage_decision": {
            "start": COVERAGE_START.date().isoformat(),
            "reason": "Premier jour de NAV strictement postérieur à l'ex-date ambiguë du 2008-03-03; un nouvel investisseur n'acquiert pas la créance antérieure.",
            "anomaly_resolved": False,
            "raw_event_corrected": False,
            "blocked_use": "Toute comptabilité BIL-B couvrant ou acquérant le droit du 2008-03-03.",
        },
        "accounting_identity": "wealth = shares_held * NAV + cash + distributions_receivable",
        "operation_order": [
            "apply any split to shares while leaving monetary receivables unchanged",
            "create a receivable from shares held on the ex-date",
            "transfer the matching receivable to cash on payment without changing wealth",
            "reinvest same-day cash at NAV into fractional shares",
            "value closing wealth including unpaid receivables",
        ],
        "documentary_validation": documentary,
        "distribution_audit": distribution_audit,
        "synthetic_accounting_tests": synthetic,
        "full_series_controls": {
            "rows": len(full_series),
            "start": full_series["date"].min().date().isoformat(),
            "end": full_series["date"].max().date().isoformat(),
            "duplicate_dates": int(full_series["date"].duplicated().sum()),
            "artificial_dates_added": 0,
            "positive_distribution_events": len(full_ledger),
            "split_events": int(full_series["split_factor_current_per_previous"].ne(1.0).sum()),
            "split_date": "2017-11-30",
            "split_factor_current_per_previous": 0.5,
            "total_claims_created_usd": created,
            "total_payments_reinvested_usd": paid,
            "ending_receivable_usd": ending_receivable,
            "ending_cash_usd": float(full_series["cash_usd"].iloc[-1]),
            "maximum_wealth_identity_error": float(wealth_error.max()),
            "maximum_transfer_identity_error": float(full_series["transfer_identity_error"].max()),
            "claim_balance_identity_error": abs(created - paid - ending_receivable),
        },
        "comparisons": comparisons,
        "all_official_windows_within_preregistered_tolerance": all_pass,
        "all_required_assertions_passed": all_pass and all(synthetic.values()),
        "compatibility_assessment": {
            "spy_bil_common_nav_accounting": True,
            "common_rules": ["shares", "NAV", "cash", "monetary receivables", "payment-date reinvestment", "end-period receivables"],
            "common_coverage_start": COVERAGE_START.date().isoformat(),
            "portfolio_or_execution_validated": False,
            "reason": "Les droits dépendent des positions effectivement détenues; des indices préconstruits ne remplacent pas un futur registre conjoint de parts, cash et créances.",
        },
        "limitations": [
            "L'anomalie du 2008-03-03 n'est pas résolue par une source primaire et demeure dans le brut.",
            "Les comparaisons officielles 2016-2026 ne valident pas les dates de paiement de 2008.",
            "La référence officielle et les NAV/distributions proviennent du même émetteur, donc ne constituent pas une validation indépendante.",
            "La série représente une comptabilité à la NAV, pas des prix exécutables ni un backtest net.",
            "Les distributions nulles sont conservées comme lignes de calendrier mais ne créent ni créance ni performance.",
        ],
        "source_sha256": {
            label: {"id": record["id"], "sha256": record["sha256"]}
            for label, record in records.items()
        },
        "legacy_ex_date_series_unchanged": {
            "path": records["LEGACY_EX_DATE"]["local_file"],
            "sha256": records["LEGACY_EX_DATE"]["sha256"],
            "status": records["LEGACY_EX_DATE"]["status"],
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    series_path = output_dir / SERIES_PATH.name
    report_path = output_dir / REPORT_PATH.name
    full_series.to_csv(series_path, index=False, date_format="%Y-%m-%d", float_format="%.12g", lineterminator="\n")
    report_path.write_text(
        json.dumps(json_value(report), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return {
        "report": report,
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in [series_path, report_path]
        },
    }


def main() -> int:
    result = build()
    print(json.dumps(json_value(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
