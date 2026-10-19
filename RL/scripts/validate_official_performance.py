"""Compare les rendements reconstruits aux performances NAV officielles archivées.

Le script est strictement hors ligne. Il vérifie d'abord les empreintes inscrites
au manifeste, extrait les valeurs non arrondies des pages State Street archivées,
puis reproduit les fenêtres calendaires exactes dans les indices locaux.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
OUTPUT_PATH = ROOT / "data" / "processed" / "rl" / "official_performance_validation.json"

# Seuil fixé avant le calcul comparatif : un point de base, soit le dernier
# chiffre publié dans les factsheets (performances affichées à 0,01 point).
TOLERANCE_PERCENTAGE_POINTS = 0.01

CASES = {
    "SPY": {
        "page_id": "ssga_spy_fund_page_20261019",
        "factsheet_id": "ssga_spy_factsheet_20260930",
        "series_id": "spy_nav_total_returns_v1_20261019",
        "as_of": "2026-09-30",
        "horizons": {1: 15.5984, 5: 13.6521},
    },
    "BIL": {
        "page_id": "ssga_bil_fund_page_20261019",
        "factsheet_id": "ssga_bil_factsheet_20260930",
        "series_id": "bil_nav_total_returns_v1_20261019",
        "as_of": "2026-09-30",
        "horizons": {1: 3.6619, 10: 2.2932},
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_records() -> dict[str, dict[str, Any]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {record["id"]: record for record in manifest["datasets"]}


def verified_path(record: dict[str, Any]) -> Path:
    path = ROOT / record["local_file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size != record["bytes"]:
        raise ValueError(f"Taille modifiée: {record['id']}")
    digest = sha256_file(path)
    if digest != record["sha256"]:
        raise ValueError(f"SHA-256 modifié: {record['id']}")
    return path


def official_nav_performance(page_path: Path) -> tuple[str, dict[int, dict[str, Any]]]:
    source = page_path.read_text(encoding="utf-8")
    match = re.search(
        r'<input type="hidden" id="data-point-ann-qtr" value="(.*?)"\s*/>',
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Bloc de performance absent: {page_path}")
    payload = json.loads(html.unescape(match.group(1)))
    key = next(key for key in payload if key.startswith("fund-perf-ann-net-total-qtr-before-tax"))
    nav = payload[key]
    values: dict[int, dict[str, Any]] = {}
    for years, field in ((1, "yr1"), (5, "yr5"), (10, "yr10")):
        item = nav["attrs"][field]
        values[years] = {
            "displayed_percent": float(item["value"].removesuffix("%")),
            "official_percent": float(item["originalValue"]),
        }
    return nav["asOfDateSimple"], values


def calculate_window(series_path: Path, as_of: str, years: int) -> dict[str, Any]:
    frame = pd.read_csv(series_path, parse_dates=["date"])
    frame = frame.set_index("date", verify_integrity=True).sort_index()
    end = pd.Timestamp(as_of)
    start = end - pd.DateOffset(years=years)
    if end not in frame.index or start not in frame.index:
        raise ValueError(f"Dates exactes absentes pour {series_path.name}: {start.date()}–{end.date()}")
    ratio = float(
        frame.loc[end, "total_return_index_base_100"]
        / frame.loc[start, "total_return_index_base_100"]
    )
    reconstructed = (ratio ** (1 / years) - 1) * 100
    return {
        "start_date": start.date().isoformat(),
        "end_date": end.date().isoformat(),
        "years": years,
        "aggregation": "cumulative total return" if years == 1 else "geometric annualized total return",
        "growth_ratio": ratio,
        "reconstructed_percent": reconstructed,
    }


def build() -> dict[str, Any]:
    records = load_records()
    comparisons = []
    sources = {}
    instrument_status = {}

    for ticker, case in CASES.items():
        page_record = records[case["page_id"]]
        factsheet_record = records[case["factsheet_id"]]
        series_record = records[case["series_id"]]
        page_path = verified_path(page_record)
        verified_path(factsheet_record)
        series_path = verified_path(series_record)
        sources[ticker] = {
            "page_id": page_record["id"],
            "page_sha256": page_record["sha256"],
            "factsheet_id": factsheet_record["id"],
            "factsheet_sha256": factsheet_record["sha256"],
            "series_id": series_record["id"],
            "series_sha256": series_record["sha256"],
        }

        as_of_text, official = official_nav_performance(page_path)
        parsed_as_of = pd.Timestamp(as_of_text).date().isoformat()
        if parsed_as_of != case["as_of"]:
            raise AssertionError(f"Date officielle inattendue pour {ticker}: {parsed_as_of}")

        ticker_passes = []
        for years, preregistered_value in case["horizons"].items():
            observed = official[years]["official_percent"]
            if observed != preregistered_value:
                raise AssertionError(
                    f"Valeur officielle inattendue pour {ticker} {years} an(s): {observed}"
                )
            result = calculate_window(series_path, case["as_of"], years)
            gap = result["reconstructed_percent"] - observed
            passed = abs(gap) <= TOLERANCE_PERCENTAGE_POINTS
            ticker_passes.append(passed)
            comparisons.append(
                {
                    "ticker": ticker,
                    **result,
                    **official[years],
                    "signed_gap_percentage_points": gap,
                    "absolute_gap_percentage_points": abs(gap),
                    "tolerance_percentage_points": TOLERANCE_PERCENTAGE_POINTS,
                    "within_preregistered_tolerance": passed,
                }
            )
        instrument_status[ticker] = {
            "all_official_windows_pass": all(ticker_passes),
            "status_for_nav_total_return_use": "VALIDATED_FOR_USE" if all(ticker_passes) else "AUDITED",
        }

    all_pass = all(row["within_preregistered_tolerance"] for row in comparisons)
    return {
        "schema_version": "1.0",
        "produced_at": "2026-10-19",
        "comparison_scope": "official State Street NAV total-return windows versus existing ex-date reconstruction",
        "preregistered_tolerance_percentage_points": TOLERANCE_PERCENTAGE_POINTS,
        "official_methodology": {
            "return_type": "NAV total return, net of fees",
            "reinvestment": "dividends and capital gains reinvested",
            "annualization": "periods shorter than one year are not annualized; multi-year table values are annualized",
            "unresolved_detail": "the factsheets do not state the precise reinvestment date or price",
        },
        "sources": sources,
        "comparisons": comparisons,
        "instrument_status": instrument_status,
        "validation_levels": {
            "1_source_integrity_and_provenance": "PASS",
            "2_internal_accounting_temporal_and_binary_reproducibility": "PASS",
            "3_bil_corporate_action_documentary_confirmation": "PASS",
            "4_agreement_with_official_performance_windows": "PASS" if all_pass else "PARTIAL",
            "5_fitness_for_the_exact_pair_use": "NOT_VALIDATED" if not all_pass else "VALIDATED_FOR_USE",
        },
        "all_comparisons_passed": all_pass,
        "series_status": "VALIDATED_FOR_USE" if all_pass else "AUDITED",
        "limitations": [
            "The official benchmarks and source data share the same issuer and are not independent-provider validation.",
            "NAV total returns are not executable market-price returns and exclude external trading costs.",
            "The BIL 2008-03-03 distribution chronology and the 2014-10-07 shares fields remain unresolved and unchanged.",
        ],
    }


def main() -> int:
    payload = build()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"\nÉcrit: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
