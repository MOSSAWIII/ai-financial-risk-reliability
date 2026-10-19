#!/usr/bin/env python3
"""Reconstruit SPY avec créances de distribution et réinvestissement au paiement.

Cette variante ne remplace pas la série historique à l'ex-date. Elle suit la
richesse d'un détenteur selon l'identité parts × NAV + cash + créances, vérifie
les frontières des fenêtres officielles et produit deux artefacts déterministes.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from RL.scripts.reconstruct_total_returns import read_distributions, read_nav
from RL.scripts.validate_official_performance import official_nav_performance


MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
OUTPUT_DIR = ROOT / "data" / "processed" / "rl"
SERIES_PATH = OUTPUT_DIR / "spy_nav_total_returns_payment_date_v1.csv"
REPORT_PATH = OUTPUT_DIR / "spy_payment_date_validation_v1.json"
TOLERANCE_PERCENTAGE_POINTS = 0.01
CODE_VERSION = "1.0.0"
CONVENTION_VERSION = "spy_nav_holding_receivable_payment_reinvestment_v1"

SOURCE_IDS = {
    "SPY_NAV": "ssga_spy_nav_20261019",
    "DISTRIBUTIONS": "ssga_spdr_distributions_20261019",
    "LEGACY_EX_DATE": "spy_nav_total_returns_v1_20261019",
    "OFFICIAL_PAGE": "ssga_spy_fund_page_20261019",
    "OFFICIAL_FACTSHEET": "ssga_spy_factsheet_20260930",
    "SEC_2026": "sec_spy_485bpos_20260126",
    "SEC_2025_497": "sec_spy_497_20250128",
    "SEC_2025_485": "sec_spy_485bpos_20250127",
}

OFFICIAL_CASES = {
    1: {"start": "2025-09-30", "end": "2026-09-30", "official_percent": 15.5984},
    5: {"start": "2021-09-30", "end": "2026-09-30", "official_percent": 13.6521},
}

SEC_REQUIRED_PASSAGES = {
    "SEC_2026": [
        "purchase of Units at net asset value per Unit on the first day and a sale at net asset value per Unit on the last day",
        "reinvested at the net asset value per Unit on the respective payment dates of the Trust",
        "including accrued expenses and dividends payable",
        "on the Ex-Dividend Date (also, the “Record Date”) are entitled to receive",
    ],
    "SEC_2025_497": [
        "reinvested at the net asset value per Unit on the respective payment dates of the Trust",
        "rather than the actual reinvestment price for such distribution",
    ],
    "SEC_2025_485": [
        "on the Ex-Dividend Date (also, the “Record Date”) are entitled to receive",
        "payment of dividends is made on the last Business Day in the calendar month following each Ex-Dividend Date",
        "including accrued expenses and dividends payable",
    ],
}


@dataclass(frozen=True)
class SourceFile:
    record: dict[str, Any]
    path: Path


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


def load_sources() -> dict[str, SourceFile]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {record["id"]: record for record in manifest["datasets"]}
    sources: dict[str, SourceFile] = {}
    for label, identifier in SOURCE_IDS.items():
        record = records[identifier]
        path = ROOT / record["local_file"]
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != record["bytes"]:
            raise ValueError(f"Taille modifiée: {identifier}")
        if sha256_file(path) != record["sha256"]:
            raise ValueError(f"SHA-256 modifié: {identifier}")
        sources[label] = SourceFile(record=record, path=path)
    return sources


def normalized_sec_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(raw))
    return re.sub(r"\s+", " ", without_tags).strip()


def verify_documentary_passages(sources: dict[str, SourceFile]) -> dict[str, Any]:
    results = {}
    for label, passages in SEC_REQUIRED_PASSAGES.items():
        text = normalized_sec_text(sources[label].path)
        found = {passage: passage in text for passage in passages}
        if not all(found.values()):
            missing = [passage for passage, present in found.items() if not present]
            raise AssertionError(f"Passages SEC absents dans {label}: {missing}")
        results[label] = {
            "source_id": sources[label].record["id"],
            "published_at": sources[label].record["published_at"],
            "sha256": sources[label].record["sha256"],
            "verified_passages": passages,
        }
    return results


def prepare_events(distributions: pd.DataFrame) -> pd.DataFrame:
    events = distributions.loc[distributions["TICKER"].eq("SPY")].copy()
    events = events.rename(
        columns={
            "EX-DATE": "ex_date",
            "RECORD DATE": "record_date",
            "PAYABLE DATE": "payment_date",
            "total_distribution_usd": "amount_per_share_usd",
        }
    )
    events = events.sort_values(["ex_date", "payment_date"]).reset_index(drop=True)
    events.insert(0, "event_id", [f"SPY-{date:%Y%m%d}" for date in events["ex_date"]])
    if events["event_id"].duplicated().any():
        raise ValueError("Plusieurs distributions SPY partagent la même ex-date")
    if (events["payment_date"] < events["ex_date"]).any():
        raise ValueError("Paiement SPY antérieur à l'ex-date")
    return events[["event_id", "ex_date", "record_date", "payment_date", "amount_per_share_usd"]]


def simulate_holding(
    nav: pd.DataFrame,
    events: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    mode: Literal["payment", "ex_date", "hybrid"] = "payment",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Suit un nouvel investisseur qui achète une part à la NAV de ``start``.

    Les événements à l'ex-date égale ou antérieure au départ sont exclus : le
    nouvel investisseur n'en détient pas le droit économique. En mode payment,
    le droit devient une créance à l'ex-date puis des parts au paiement. En mode
    ex_date, il est immédiatement réinvesti. Le mode hybrid réinvestit à
    l'ex-date seulement les paiements réalisés avant la fin et conserve en
    créance les distributions encore impayées à la fin.
    """

    nav = nav.set_index("date", verify_integrity=True).sort_index()
    if "split_factor_current_per_previous" not in nav.columns:
        nav["split_factor_current_per_previous"] = 1.0
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start not in nav.index or end not in nav.index:
        raise ValueError(f"Dates NAV exactes absentes: {start.date()}–{end.date()}")
    if start >= end:
        raise ValueError("La date de début doit précéder la date de fin")

    window_events = events.loc[(events["ex_date"] > start) & (events["ex_date"] <= end)].copy()
    for date in window_events["ex_date"]:
        if date not in nav.index:
            raise ValueError(f"Ex-date sans NAV: {date.date()}")
    for date in window_events.loc[window_events["payment_date"] <= end, "payment_date"]:
        if date not in nav.index:
            raise ValueError(f"Date de paiement sans NAV: {date.date()}")

    shares = 1.0
    cash = 0.0
    claims: dict[str, float] = {}
    ledger: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    initial_nav = float(nav.loc[start, "nav_usd"])
    previous_wealth: float | None = None

    for date, nav_row in nav.loc[start:end].iterrows():
        nav_usd = float(nav_row["nav_usd"])
        claim_created = 0.0
        payment_received = 0.0
        shares_reinvested = 0.0
        max_transfer_error = 0.0

        if date > start:
            split_factor = float(nav_row["split_factor_current_per_previous"])
            if not math.isfinite(split_factor) or split_factor <= 0:
                raise ValueError(f"Facteur de fractionnement invalide le {date.date()}")
            shares *= split_factor
            todays_ex = window_events.loc[window_events["ex_date"].eq(date)]
            for event in todays_ex.itertuples(index=False):
                entitlement_shares = shares
                claim = entitlement_shares * float(event.amount_per_share_usd)
                reinvest_now = mode == "ex_date" or (mode == "hybrid" and event.payment_date <= end)
                ledger[event.event_id] = {
                    "event_id": event.event_id,
                    "ex_date": event.ex_date.date().isoformat(),
                    "record_date": event.record_date.date().isoformat(),
                    "payment_date": event.payment_date.date().isoformat(),
                    "amount_per_share_usd": float(event.amount_per_share_usd),
                    "entitlement_shares": entitlement_shares,
                    "claim_created_usd": claim,
                    "reinvestment_date": None,
                    "reinvestment_nav_usd": None,
                    "shares_reinvested": 0.0,
                }
                claim_created += claim
                if reinvest_now:
                    bought = claim / nav_usd
                    shares += bought
                    shares_reinvested += bought
                    ledger[event.event_id].update(
                        {
                            "reinvestment_date": date.date().isoformat(),
                            "reinvestment_nav_usd": nav_usd,
                            "shares_reinvested": bought,
                        }
                    )
                else:
                    claims[event.event_id] = claim

            if mode == "payment":
                todays_payments = window_events.loc[window_events["payment_date"].eq(date)]
                for event in todays_payments.itertuples(index=False):
                    if event.event_id not in claims:
                        continue
                    receivable_before = sum(claims.values())
                    wealth_before_transfer = shares * nav_usd + cash + receivable_before
                    amount = claims.pop(event.event_id)
                    cash += amount
                    payment_received += amount
                    bought = cash / nav_usd
                    shares += bought
                    shares_reinvested += bought
                    cash = 0.0
                    wealth_after_transfer = shares * nav_usd + cash + sum(claims.values())
                    max_transfer_error = max(max_transfer_error, abs(wealth_after_transfer - wealth_before_transfer))
                    ledger[event.event_id].update(
                        {
                            "reinvestment_date": date.date().isoformat(),
                            "reinvestment_nav_usd": nav_usd,
                            "shares_reinvested": bought,
                        }
                    )

        receivable = sum(claims.values())
        wealth = shares * nav_usd + cash + receivable
        daily_return = None if previous_wealth is None else wealth / previous_wealth - 1
        rows.append(
            {
                "date": date,
                "ticker": "SPY",
                "nav_usd": nav_usd,
                "split_factor_current_per_previous": float(
                    nav_row["split_factor_current_per_previous"]
                ),
                "shares_held": shares,
                "cash_usd": cash,
                "distribution_receivable_usd": receivable,
                "pending_claim_count": len(claims),
                "claim_created_usd": claim_created,
                "payment_received_usd": payment_received,
                "shares_reinvested_on_date": shares_reinvested,
                "wealth_usd": wealth,
                "total_return_payment_date": daily_return,
                "wealth_index_base_100": 100 * wealth / initial_nav,
                "transfer_identity_error": max_transfer_error,
            }
        )
        previous_wealth = wealth

    frame = pd.DataFrame(rows)
    event_ledger = pd.DataFrame(ledger.values())
    if len(event_ledger):
        event_ledger["status_at_end"] = np.where(
            event_ledger["reinvestment_date"].notna(), "REINVESTED", "RECEIVABLE"
        )
    return frame, event_ledger


def annualized_performance(frame: pd.DataFrame, years: int) -> float:
    growth = float(frame["wealth_usd"].iloc[-1] / frame["wealth_usd"].iloc[0])
    return (growth ** (1 / years) - 1) * 100


def legacy_performance(legacy: pd.DataFrame, start: str, end: str, years: int) -> float:
    frame = legacy.set_index("date", verify_integrity=True)
    growth = float(
        frame.loc[pd.Timestamp(end), "total_return_index_base_100"]
        / frame.loc[pd.Timestamp(start), "total_return_index_base_100"]
    )
    return (growth ** (1 / years) - 1) * 100


def run_synthetic_tests() -> dict[str, Any]:
    nav = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-05"]),
            "nav_usd": [100.0, 98.0, 98.0],
        }
    )
    event = pd.DataFrame(
        {
            "event_id": ["TEST-1"],
            "ex_date": pd.to_datetime(["2026-01-02"]),
            "record_date": pd.to_datetime(["2026-01-02"]),
            "payment_date": pd.to_datetime(["2026-01-05"]),
            "amount_per_share_usd": [2.0],
        }
    )
    frame, ledger = simulate_holding(nav, event, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-05"))
    ex_row = frame.loc[frame["date"].eq(pd.Timestamp("2026-01-02"))].iloc[0]
    pay_row = frame.loc[frame["date"].eq(pd.Timestamp("2026-01-05"))].iloc[0]
    assert math.isclose(ex_row["wealth_usd"], 100.0, abs_tol=1e-12)
    assert math.isclose(ex_row["distribution_receivable_usd"], 2.0, abs_tol=1e-12)
    assert math.isclose(ex_row["cash_usd"], 0.0, abs_tol=1e-12)
    assert math.isclose(pay_row["wealth_usd"], 100.0, abs_tol=1e-12)
    assert math.isclose(pay_row["distribution_receivable_usd"], 0.0, abs_tol=1e-12)
    assert math.isclose(pay_row["shares_held"], 1 + 2 / 98, abs_tol=1e-12)
    assert pay_row["transfer_identity_error"] <= 1e-12
    assert ledger.iloc[0]["status_at_end"] == "REINVESTED"

    multiple = pd.concat(
        [
            event.assign(
                event_id="TEST-A",
                payment_date=pd.Timestamp("2026-01-06"),
                amount_per_share_usd=1.0,
            ),
            event.assign(
                event_id="TEST-B",
                ex_date=pd.Timestamp("2026-01-05"),
                record_date=pd.Timestamp("2026-01-05"),
                payment_date=pd.Timestamp("2026-01-06"),
                amount_per_share_usd=3.0,
            ),
        ],
        ignore_index=True,
    )
    nav_multiple = pd.concat(
        [nav, pd.DataFrame({"date": [pd.Timestamp("2026-01-06")], "nav_usd": [98.0]})],
        ignore_index=True,
    )
    multi_frame, multi_ledger = simulate_holding(
        nav_multiple, multiple, pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-06")
    )
    assert multi_frame["pending_claim_count"].max() == 2
    assert multi_frame["pending_claim_count"].iloc[-1] == 0
    assert len(multi_ledger) == 2
    assert math.isclose(
        multi_ledger["claim_created_usd"].sum(),
        multi_frame["payment_received_usd"].sum(),
        abs_tol=1e-12,
    )

    pre_start = event.assign(ex_date=pd.Timestamp("2026-01-01"), record_date=pd.Timestamp("2026-01-01"))
    boundary_frame, boundary_ledger = simulate_holding(
        nav, pre_start, pd.Timestamp("2026-01-02"), pd.Timestamp("2026-01-05")
    )
    assert boundary_ledger.empty
    assert boundary_frame["payment_received_usd"].sum() == 0

    return {
        "ex_date_wealth_conservation": True,
        "no_cash_before_payment": True,
        "payment_transfer_wealth_conservation": True,
        "claim_extinguished_after_payment": True,
        "fractional_shares_reinvested_correctly": True,
        "multiple_pending_claims_supported": True,
        "pre_start_claim_excluded": True,
    }


def build(output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    sources = load_sources()
    documentary = verify_documentary_passages(sources)
    synthetic_tests = run_synthetic_tests()

    nav = read_nav(sources["SPY_NAV"].path, "SPY")
    distributions = read_distributions(sources["DISTRIBUTIONS"].path)
    events = prepare_events(distributions)
    legacy = pd.read_csv(sources["LEGACY_EX_DATE"].path, parse_dates=["date"])
    split_factors = legacy[["date", "split_factor_current_per_previous"]].copy()
    nav = nav.merge(split_factors, on="date", how="left", validate="one_to_one")
    if nav["split_factor_current_per_previous"].isna().any():
        raise AssertionError("Facteur de fractionnement SPY absent")
    if not nav["split_factor_current_per_previous"].eq(1.0).all():
        raise AssertionError("Événement SPY inattendu: revue documentaire requise avant reconstruction")
    official_date, official_values = official_nav_performance(sources["OFFICIAL_PAGE"].path)
    if pd.Timestamp(official_date).date().isoformat() != "2026-09-30":
        raise AssertionError(f"Date officielle inattendue: {official_date}")

    full_series, full_ledger = simulate_holding(
        nav,
        events,
        pd.Timestamp(nav["date"].min()),
        pd.Timestamp(nav["date"].max()),
        mode="payment",
    )
    if full_series["date"].duplicated().any() or len(full_series) != len(nav):
        raise AssertionError("Calendrier de sortie différent du calendrier NAV")
    if not full_series["date"].equals(nav["date"].reset_index(drop=True)):
        raise AssertionError("Dates artificielles ou réordonnées")
    if full_series["transfer_identity_error"].max() > 1e-10:
        raise AssertionError("Transfert créance-cash-parts non conservatif")
    created = float(full_series["claim_created_usd"].sum())
    paid = float(full_series["payment_received_usd"].sum())
    pending = float(full_series["distribution_receivable_usd"].iloc[-1])
    if not math.isclose(created, paid + pending, rel_tol=0, abs_tol=1e-10):
        raise AssertionError("Double comptage ou extinction incorrecte des créances")

    comparisons = []
    for years, case in OFFICIAL_CASES.items():
        start, end = pd.Timestamp(case["start"]), pd.Timestamp(case["end"])
        official = float(official_values[years]["official_percent"])
        if official != case["official_percent"]:
            raise AssertionError(f"Performance officielle inattendue à {years} an(s): {official}")

        payment, ledger = simulate_holding(nav, events, start, end, mode="payment")
        ex_date, _ = simulate_holding(nav, events, start, end, mode="ex_date")
        hybrid, _ = simulate_holding(nav, events, start, end, mode="hybrid")
        convention_a = legacy_performance(legacy, case["start"], case["end"], years)
        direct_ex_date = annualized_performance(ex_date, years)
        if not math.isclose(convention_a, direct_ex_date, rel_tol=0, abs_tol=1e-9):
            raise AssertionError("La simulation A ne reproduit pas la série historique")
        convention_b = annualized_performance(payment, years)
        hybrid_performance = annualized_performance(hybrid, years)
        end_wealth_without_receivable = (
            float(payment["wealth_usd"].iloc[-1])
            - float(payment["distribution_receivable_usd"].iloc[-1])
        )
        growth_without_end_receivable = end_wealth_without_receivable / float(payment["wealth_usd"].iloc[0])
        performance_without_end_receivable = (growth_without_end_receivable ** (1 / years) - 1) * 100
        full_indexed = full_series.set_index("date", verify_integrity=True)
        global_holding_growth = float(
            full_indexed.loc[end, "wealth_usd"] / full_indexed.loc[start, "wealth_usd"]
        )
        global_holding_performance = (global_holding_growth ** (1 / years) - 1) * 100

        pre_start_pending = events.loc[
            (events["ex_date"] <= start) & (events["payment_date"] > start),
            ["event_id", "ex_date", "payment_date", "amount_per_share_usd"],
        ]
        end_pending = ledger.loc[ledger["status_at_end"].eq("RECEIVABLE")]
        gap_a = convention_a - official
        gap_b = convention_b - official
        explained = 1 - abs(gap_b) / abs(gap_a)
        comparisons.append(
            {
                "years": years,
                "start_date": case["start"],
                "end_date": case["end"],
                "aggregation": "cumulative" if years == 1 else "geometric annualized",
                "official_percent": official,
                "convention_a_ex_date_percent": convention_a,
                "convention_b_payment_holding_percent": convention_b,
                "signed_gap_a_percentage_points": gap_a,
                "absolute_gap_a_percentage_points": abs(gap_a),
                "signed_gap_b_percentage_points": gap_b,
                "absolute_gap_b_percentage_points": abs(gap_b),
                "tolerance_percentage_points": TOLERANCE_PERCENTAGE_POINTS,
                "convention_a_pass": abs(gap_a) <= TOLERANCE_PERCENTAGE_POINTS,
                "convention_b_pass": abs(gap_b) <= TOLERANCE_PERCENTAGE_POINTS,
                "initial_absolute_gap_explained_fraction": explained,
                "initial_absolute_gap_explained_percent": 100 * explained,
                "total_effect_b_minus_a_percentage_points": convention_b - convention_a,
                "payment_timing_effect_percentage_points": convention_b - hybrid_performance,
                "end_pending_claim_effect_percentage_points": hybrid_performance - convention_a,
                "end_receivable_inclusion_effect_percentage_points": convention_b
                - performance_without_end_receivable,
                "performance_if_end_receivable_omitted_percent": performance_without_end_receivable,
                "global_continuing_holder_ratio_percent": global_holding_performance,
                "new_investor_minus_global_ratio_percentage_points": convention_b
                - global_holding_performance,
                "distribution_count": len(ledger),
                "paid_distribution_count": int(ledger["status_at_end"].eq("REINVESTED").sum()),
                "pending_distribution_count_at_end": int(ledger["status_at_end"].eq("RECEIVABLE").sum()),
                "pre_start_pending_distribution_count_excluded": len(pre_start_pending),
                "pre_start_pending_distributions_excluded": [
                    {
                        "event_id": row.event_id,
                        "ex_date": row.ex_date.date().isoformat(),
                        "payment_date": row.payment_date.date().isoformat(),
                        "amount_per_share_usd": float(row.amount_per_share_usd),
                    }
                    for row in pre_start_pending.itertuples(index=False)
                ],
                "end_pending_distributions": json_value(end_pending.to_dict(orient="records")),
                "maximum_transfer_identity_error": float(payment["transfer_identity_error"].max()),
                "ending_shares": float(payment["shares_held"].iloc[-1]),
                "ending_cash_usd": float(payment["cash_usd"].iloc[-1]),
                "ending_receivable_usd": float(payment["distribution_receivable_usd"].iloc[-1]),
            }
        )

    all_b_pass = all(row["convention_b_pass"] for row in comparisons)
    report = {
        "schema_version": "1.0",
        "code_version": CODE_VERSION,
        "convention_version": CONVENTION_VERSION,
        "produced_at": "2026-10-19",
        "status": "VALIDATED_FOR_USE" if all_b_pass else "AUDITED",
        "allowed_use": "SPY NAV total-return analysis under payment-date holding convention; no execution or external trading costs",
        "legacy_ex_date_series_unchanged": {
            "path": sources["LEGACY_EX_DATE"].record["local_file"],
            "sha256": sources["LEGACY_EX_DATE"].record["sha256"],
            "status": sources["LEGACY_EX_DATE"].record["status"],
        },
        "accounting_identity": "wealth = shares_held * NAV + cash + distributions_receivable",
        "operation_order": [
            "establish distribution right from shares already held on ex/record date",
            "keep the right as a non-cash receivable until payment",
            "on payment, transfer the matching receivable to cash without changing wealth",
            "reinvest that cash at same-day NAV into fractional shares",
            "mark closing wealth including any still-unpaid receivable",
        ],
        "documentary_validation": documentary,
        "methodological_link_limit": "SEC filings document the Trust method; the September 2026 factsheet does not explicitly cross-reference the precise payment-date implementation.",
        "synthetic_accounting_tests": synthetic_tests,
        "full_series_controls": {
            "rows": len(full_series),
            "start": full_series["date"].min().date().isoformat(),
            "end": full_series["date"].max().date().isoformat(),
            "duplicate_dates": int(full_series["date"].duplicated().sum()),
            "artificial_dates_added": 0,
            "distribution_events": len(full_ledger),
            "split_events": int(
                full_series["split_factor_current_per_previous"].ne(1.0).sum()
            ),
            "total_claims_created_usd": created,
            "total_payments_reinvested_usd": paid,
            "ending_receivable_usd": pending,
            "ending_cash_usd": float(full_series["cash_usd"].iloc[-1]),
            "maximum_transfer_identity_error": float(full_series["transfer_identity_error"].max()),
            "claim_balance_identity_error": abs(created - paid - pending),
        },
        "comparisons": comparisons,
        "all_official_windows_within_preregistered_tolerance": all_b_pass,
        "all_required_assertions_passed": all_b_pass and all(synthetic_tests.values()),
        "limitations": [
            "The factsheet does not explicitly state that its September 2026 figures use the SEC payment-date convention.",
            "The official comparison and source NAV/distributions come from the same issuer, not an independent provider.",
            "The series represents NAV accounting, not an executable market-price return or a net trading backtest.",
            "A ratio of a long-lived holding index across arbitrary dates need not equal a new-investor window return when a pre-start receivable exists.",
        ],
        "source_sha256": {
            label: {"id": source.record["id"], "sha256": source.record["sha256"]}
            for label, source in sources.items()
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    series_path = output_dir / SERIES_PATH.name
    report_path = output_dir / REPORT_PATH.name
    full_series.to_csv(series_path, index=False, date_format="%Y-%m-%d", float_format="%.12g", lineterminator="\n")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return {
        "report": report,
        "files": {
            series_path.name: {
                "bytes": series_path.stat().st_size,
                "sha256": sha256_file(series_path),
            },
            report_path.name: {
                "bytes": report_path.stat().st_size,
                "sha256": sha256_file(report_path),
            },
        },
    }


def main() -> int:
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
