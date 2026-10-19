#!/usr/bin/env python3
"""Reconstruit hors ligne les rendements totaux quotidiens à la NAV de SPY et BIL.

Le module ne télécharge rien et ne modifie jamais les fichiers bruts. Il vérifie les
empreintes du manifeste, applique une convention ex-dividende explicite, traite les
fractionnements seulement lorsqu'ils sont corroborés par NAV, parts et actif net,
puis écrit des CSV et rapports JSON déterministes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "RL" / "data_manifest.json"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "rl"
CODE_VERSION = "1.0.0"
CONVENTION_VERSION = "nav_total_return_ex_date_v1"
SOURCE_IDS = {
    "SPY_NAV": "ssga_spy_nav_20261019",
    "BIL_NAV": "ssga_bil_nav_20261019",
    "DISTRIBUTIONS": "ssga_spdr_distributions_20261019",
    "SPY_MARKET": "nasdaq_spy_ohlcv_20261019",
    "SPY_PREMIUM_DISCOUNT": "ssga_spy_premium_discount_20261019",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def python_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not math.isfinite(float(value)) else float(value)
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    return value


def load_manifest() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {record["id"]: record for record in manifest["datasets"]}
    missing = sorted(set(SOURCE_IDS.values()) - set(records))
    if missing:
        raise KeyError(f"Sources absentes du manifeste: {missing}")
    return manifest, records


def verify_source(record: dict[str, Any]) -> Path:
    path = ROOT / record["local_file"]
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size != record["bytes"]:
        raise ValueError(f"Taille modifiée pour {record['id']}")
    actual = sha256_file(path)
    if actual != record["sha256"]:
        raise ValueError(f"SHA-256 modifié pour {record['id']}: {actual}")
    return path


def parse_numeric(values: pd.Series) -> pd.Series:
    return pd.to_numeric(
        values.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace({"-": None, "nan": None, "": None}),
        errors="coerce",
    )


def read_nav(path: Path, ticker: str) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name="navhist", header=3)
    frame["date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.loc[frame["date"].notna(), ["date", "NAV", "Shares Outstanding", "Total Net Assets"]].copy()
    frame = frame.rename(
        columns={"NAV": "nav_usd", "Shares Outstanding": "shares_outstanding", "Total Net Assets": "total_net_assets_usd"}
    )
    for column in ["nav_usd", "shares_outstanding", "total_net_assets_usd"]:
        frame[column] = parse_numeric(frame[column])
    frame = frame.sort_values("date").reset_index(drop=True)
    if frame["date"].duplicated().any():
        raise ValueError(f"Dates NAV dupliquées pour {ticker}")
    if frame["nav_usd"].isna().any() or (frame["nav_usd"] <= 0).any():
        raise ValueError(f"NAV absente ou non positive pour {ticker}")
    return frame


def read_distributions(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name="dividend")
    frame = frame.loc[frame["TICKER"].isin(["SPY", "BIL"])].copy()
    for column in ["EX-DATE", "RECORD DATE", "PAYABLE DATE"]:
        frame[column] = pd.to_datetime(frame[column], format="%m/%d/%Y", errors="coerce")
    if frame[["EX-DATE", "RECORD DATE", "PAYABLE DATE"]].isna().any().any():
        raise ValueError("Date SPY/BIL illisible dans le fichier de distributions")
    money_columns = ["DIVIDEND ($)", "SHORT TERM CAPITAL GAIN ($)", "LONG TERM CAPITAL GAIN ($)"]
    for column in money_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    if (frame[money_columns] < 0).any().any():
        raise ValueError("Distribution négative détectée")
    frame["total_distribution_usd"] = frame[money_columns].sum(axis=1)
    return frame.sort_values(["TICKER", "EX-DATE"]).reset_index(drop=True)


def infer_split_factors(nav: pd.DataFrame) -> tuple[pd.Series, list[dict[str, Any]]]:
    nav_ratio = nav["nav_usd"] / nav["nav_usd"].shift(1)
    share_ratio = nav["shares_outstanding"] / nav["shares_outstanding"].shift(1)
    asset_ratio = nav["total_net_assets_usd"] / nav["total_net_assets_usd"].shift(1)
    large_nav_jump = (nav_ratio > 1.5) | (nav_ratio < (1 / 1.5))
    reciprocal = (nav_ratio * share_ratio - 1).abs() <= 0.02
    asset_continuity = (asset_ratio - 1).abs() <= 0.10
    candidate = large_nav_jump & reciprocal & asset_continuity
    factors = pd.Series(1.0, index=nav.index, name="split_factor_current_per_previous")
    factors.loc[candidate] = share_ratio.loc[candidate]
    events: list[dict[str, Any]] = []
    for i in nav.index[candidate]:
        events.append(
            {
                "date": nav.loc[i, "date"].date().isoformat(),
                "split_factor_current_per_previous": float(factors.loc[i]),
                "nav_ratio": float(nav_ratio.loc[i]),
                "shares_ratio": float(share_ratio.loc[i]),
                "assets_ratio": float(asset_ratio.loc[i]),
                "evidence": "Inférence interne: saut réciproque NAV/parts avec continuité de l'actif net; aucune source indépendante locale du fractionnement.",
            }
        )
    return factors, events


def reconstruct_one(ticker: str, nav: pd.DataFrame, distributions: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    events = distributions.loc[distributions["TICKER"].eq(ticker)].copy()
    in_window = events["EX-DATE"].between(nav["date"].min(), nav["date"].max())
    used = events.loc[in_window].copy()
    before = int((events["EX-DATE"] < nav["date"].min()).sum())
    after = int((events["EX-DATE"] > nav["date"].max()).sum())
    duplicate_ex_dates = int(used["EX-DATE"].duplicated().sum())
    if duplicate_ex_dates:
        raise ValueError(f"Plusieurs distributions le même jour pour {ticker}; convention d'agrégation non validée")
    unmatched = sorted(set(used["EX-DATE"]) - set(nav["date"]))
    if unmatched:
        raise ValueError(f"Dates ex-dividende sans NAV pour {ticker}: {unmatched}")

    distribution_columns = {
        "EX-DATE": "date",
        "RECORD DATE": "distribution_record_date",
        "PAYABLE DATE": "distribution_payable_date",
        "DIVIDEND ($)": "dividend_usd_per_current_share",
        "SHORT TERM CAPITAL GAIN ($)": "short_term_capital_gain_usd_per_current_share",
        "LONG TERM CAPITAL GAIN ($)": "long_term_capital_gain_usd_per_current_share",
        "total_distribution_usd": "total_distribution_usd_per_current_share",
    }
    used = used[list(distribution_columns)].rename(columns=distribution_columns)
    used["distribution_event"] = True
    output = nav.merge(used, on="date", how="left", validate="one_to_one")
    money = [
        "dividend_usd_per_current_share",
        "short_term_capital_gain_usd_per_current_share",
        "long_term_capital_gain_usd_per_current_share",
        "total_distribution_usd_per_current_share",
    ]
    output[money] = output[money].fillna(0.0)
    output["distribution_event"] = output["distribution_event"].eq(True)
    output["distribution_payment_lag_calendar_days"] = (
        output["distribution_payable_date"] - output["date"]
    ).dt.days.astype("Int64")

    split_factors, split_events = infer_split_factors(output)
    output["split_factor_current_per_previous"] = split_factors
    previous_nav = output["nav_usd"].shift(1)
    output["nav_return_unadjusted"] = output["nav_usd"] / previous_nav - 1
    output["nav_price_return_split_adjusted"] = (
        output["split_factor_current_per_previous"] * output["nav_usd"] / previous_nav - 1
    )
    output["total_return_nav"] = (
        output["split_factor_current_per_previous"]
        * (output["nav_usd"] + output["total_distribution_usd_per_current_share"])
        / previous_nav
        - 1
    )
    output["growth_factor"] = 1 + output["total_return_nav"]
    output["total_return_index_base_100"] = output["growth_factor"].fillna(1.0).cumprod() * 100.0
    output.insert(1, "ticker", ticker)

    identity_error = (output["growth_factor"] - (1 + output["total_return_nav"])).abs().dropna()
    index_ratio = output["total_return_index_base_100"] / output["total_return_index_base_100"].shift(1)
    cumulative_error = (index_ratio - output["growth_factor"]).abs().dropna()
    source_distribution_sum = float(events.loc[in_window, "total_distribution_usd"].sum())
    mapped_distribution_sum = float(output["total_distribution_usd_per_current_share"].sum())
    chronology_issues = events.loc[
        events["PAYABLE DATE"] < events["EX-DATE"],
        ["EX-DATE", "RECORD DATE", "PAYABLE DATE", "total_distribution_usd"],
    ]

    summary = {
        "ticker": ticker,
        "rows": len(output),
        "returns": int(output["total_return_nav"].notna().sum()),
        "start": output["date"].min().date().isoformat(),
        "end": output["date"].max().date().isoformat(),
        "first_return_date": output.loc[output["total_return_nav"].notna(), "date"].min().date().isoformat(),
        "duplicate_nav_dates": int(output["date"].duplicated().sum()),
        "missing_nav": int(output["nav_usd"].isna().sum()),
        "nonpositive_nav": int((output["nav_usd"] <= 0).sum()),
        "missing_shares": int(output["shares_outstanding"].isna().sum()),
        "missing_total_net_assets": int(output["total_net_assets_usd"].isna().sum()),
        "distribution_events_source": len(events),
        "distribution_events_used": len(used),
        "distribution_cusip_values": sorted(events["CUSIP"].dropna().astype(str).unique().tolist()),
        "distribution_frequency_values": sorted(events["FREQUENCY"].dropna().astype(str).unique().tolist()),
        "distribution_events_before_nav": before,
        "distribution_events_after_nav": after,
        "distribution_dates_unmatched": len(unmatched),
        "duplicate_distribution_ex_dates": duplicate_ex_dates,
        "distribution_sum_source_in_window": source_distribution_sum,
        "distribution_sum_mapped": mapped_distribution_sum,
        "payment_before_ex_date_count": len(chronology_issues),
        "payment_before_ex_date_rows": [
            {column: python_value(value) for column, value in row.items()}
            for row in chronology_issues.to_dict(orient="records")
        ],
        "split_events_inferred": split_events,
        "max_growth_identity_error": float(identity_error.max()) if len(identity_error) else 0.0,
        "max_cumulative_identity_error": float(cumulative_error.max()) if len(cumulative_error) else 0.0,
        "minimum_total_return": float(output["total_return_nav"].min()),
        "maximum_total_return": float(output["total_return_nav"].max()),
        "ending_total_return_index": float(output["total_return_index_base_100"].iloc[-1]),
    }
    return output, summary


def read_nasdaq_close(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["data"]["tradesTable"]["rows"])
    frame["date"] = pd.to_datetime(frame["date"], format="%m/%d/%Y")
    frame["market_close_usd"] = parse_numeric(frame["close"])
    frame = frame.sort_values("date")
    frame["market_price_return"] = frame["market_close_usd"].pct_change(fill_method=None)
    return frame[["date", "market_close_usd", "market_price_return"]]


def read_premium_discount(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name="pdhist", header=3)
    frame["date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.loc[frame["date"].notna(), ["date", "Premium/Discount"]].copy()
    frame["official_premium_discount"] = parse_numeric(frame["Premium/Discount"])
    return frame[["date", "official_premium_discount"]].sort_values("date")


def independent_checks(spy: pd.DataFrame, market_path: Path, premium_path: Path) -> dict[str, Any]:
    market = read_nasdaq_close(market_path)
    joined = spy[["date", "nav_usd", "nav_price_return_split_adjusted"]].merge(market, on="date", how="inner")
    return_rows = joined.dropna(subset=["nav_price_return_split_adjusted", "market_price_return"]).copy()
    difference = return_rows["nav_price_return_split_adjusted"] - return_rows["market_price_return"]

    premium = read_premium_discount(premium_path)
    pd_join = joined[["date", "nav_usd", "market_close_usd"]].merge(premium, on="date", how="inner")
    pd_join["calculated_close_to_nav_pct"] = (pd_join["market_close_usd"] / pd_join["nav_usd"] - 1) * 100
    pd_difference = pd_join["calculated_close_to_nav_pct"] - pd_join["official_premium_discount"]
    max_pd_row = pd_join.loc[pd_difference.abs().idxmax()]

    return {
        "nature": "Contrôle indépendant partiel: Nasdaq fournit un prix de marché SPY, pas un indice officiel de rendement total à la NAV. Les distributions restent celles de State Street.",
        "common_level_rows": len(joined),
        "common_start": joined["date"].min().date().isoformat(),
        "common_end": joined["date"].max().date().isoformat(),
        "comparable_return_rows": len(return_rows),
        "nav_market_return_correlation": float(return_rows["nav_price_return_split_adjusted"].corr(return_rows["market_price_return"])),
        "nav_market_return_mean_difference_bp": float(difference.mean() * 10_000),
        "nav_market_return_mae_bp": float(difference.abs().mean() * 10_000),
        "nav_market_return_rmse_bp": float(np.sqrt(np.mean(np.square(difference))) * 10_000),
        "nav_market_return_max_abs_difference_bp": float(difference.abs().max() * 10_000),
        "premium_discount_common_rows": len(pd_join),
        "premium_discount_median_abs_gap_percentage_points": float(pd_difference.abs().median()),
        "premium_discount_max_abs_gap_percentage_points": float(pd_difference.abs().max()),
        "premium_discount_max_gap_date": max_pd_row["date"].date().isoformat(),
        "premium_discount_max_gap_note": "Le prix de clôture Nasdaq et le champ officiel premium/discount ne sont pas nécessairement définis au même instant ni selon le même prix de marché.",
        "external_total_return_reference_available": False,
    }


def anomaly_2014(nav_by_ticker: dict[str, pd.DataFrame]) -> dict[str, Any]:
    result = {"date": "2014-10-07", "interpretation": "La NAV et l'actif net impliquent un nombre de parts différent du champ publié. Les NAV restent continues; aucune NAV n'est corrigée ou exclue."}
    for ticker, frame in nav_by_ticker.items():
        row = frame.loc[frame["date"].eq(pd.Timestamp("2014-10-07"))].iloc[0]
        implied = row["total_net_assets_usd"] / row["nav_usd"]
        result[ticker] = {
            "nav_usd": float(row["nav_usd"]),
            "reported_shares": float(row["shares_outstanding"]),
            "total_net_assets_usd": float(row["total_net_assets_usd"]),
            "shares_implied_by_nav_and_assets": float(implied),
            "reported_minus_implied_shares": float(row["shares_outstanding"] - implied),
        }
    return result


def common_calendar(spy: pd.DataFrame, bil: pd.DataFrame) -> dict[str, Any]:
    spy_dates, bil_dates = set(spy["date"]), set(bil["date"])
    overlap_start = max(spy["date"].min(), bil["date"].min())
    overlap_end = min(spy["date"].max(), bil["date"].max())
    spy_window = {d for d in spy_dates if overlap_start <= d <= overlap_end}
    bil_window = {d for d in bil_dates if overlap_start <= d <= overlap_end}
    common = sorted(spy_window & bil_window)
    return {
        "start": overlap_start.date().isoformat(),
        "end": overlap_end.date().isoformat(),
        "common_nav_dates": len(common),
        "common_return_dates": max(len(common) - 1, 0),
        "spy_only_dates_within_overlap": len(spy_window - bil_window),
        "bil_only_dates_within_overlap": len(bil_window - spy_window),
        "no_calendar_dates_added": True,
    }


def assert_validation(report: dict[str, Any]) -> None:
    for ticker in ["SPY", "BIL"]:
        item = report["series"][ticker]
        assert item["duplicate_nav_dates"] == 0
        assert item["missing_nav"] == 0
        assert item["nonpositive_nav"] == 0
        assert item["distribution_dates_unmatched"] == 0
        assert item["duplicate_distribution_ex_dates"] == 0
        assert abs(item["distribution_sum_source_in_window"] - item["distribution_sum_mapped"]) <= 1e-12
        assert item["max_growth_identity_error"] <= 1e-15
        assert item["max_cumulative_identity_error"] <= 1e-12
    assert report["series"]["SPY"]["split_events_inferred"] == []
    bil_splits = report["series"]["BIL"]["split_events_inferred"]
    assert len(bil_splits) == 1 and bil_splits[0]["date"] == "2017-11-30"
    assert report["common_calendar"]["no_calendar_dates_added"] is True


def build(output_dir: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest, records = load_manifest()
    source_paths = {name: verify_source(records[identifier]) for name, identifier in SOURCE_IDS.items()}
    distributions = read_distributions(source_paths["DISTRIBUTIONS"])
    nav_by_ticker = {
        "SPY": read_nav(source_paths["SPY_NAV"], "SPY"),
        "BIL": read_nav(source_paths["BIL_NAV"], "BIL"),
    }
    reconstructed: dict[str, pd.DataFrame] = {}
    summaries: dict[str, dict[str, Any]] = {}
    for ticker in ["SPY", "BIL"]:
        reconstructed[ticker], summaries[ticker] = reconstruct_one(ticker, nav_by_ticker[ticker], distributions)

    validation = {
        "convention_version": CONVENTION_VERSION,
        "series_status": "AUDITED",
        "status_reason": "Cohérence interne établie, mais absence de référence locale indépendante de rendement total à la NAV et fractionnement BIL seulement inféré des champs officiels.",
        "series": summaries,
        "common_calendar": common_calendar(reconstructed["SPY"], reconstructed["BIL"]),
        "anomaly_2014_10_07": anomaly_2014(nav_by_ticker),
        "independent_checks_spy": independent_checks(
            reconstructed["SPY"], source_paths["SPY_MARKET"], source_paths["SPY_PREMIUM_DISCOUNT"]
        ),
        "all_required_assertions_passed": True,
    }
    assert_validation(validation)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_paths: dict[str, Path] = {}
    for ticker, frame in reconstructed.items():
        path = output_dir / f"{ticker.lower()}_nav_total_returns.csv"
        serial = frame.copy()
        for column in ["date", "distribution_record_date", "distribution_payable_date"]:
            serial[column] = serial[column].dt.strftime("%Y-%m-%d")
        serial.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")
        csv_paths[ticker] = path

    validation_path = output_dir / "validation_report.json"
    write_json(validation_path, validation)
    output_hashes = {path.name: sha256_file(path) for path in [*csv_paths.values(), validation_path]}
    metadata = {
        "produced_on": manifest["created_at"],
        "code_file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
        "code_version": CODE_VERSION,
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "convention_version": CONVENTION_VERSION,
        "sources": {
            name: {
                "id": SOURCE_IDS[name],
                "local_file": records[SOURCE_IDS[name]]["local_file"],
                "sha256": records[SOURCE_IDS[name]]["sha256"],
            }
            for name in SOURCE_IDS
        },
        "economic_convention": {
            "price_return": "q_t * NAV_t / NAV_{t-1} - 1",
            "total_return": "q_t * (NAV_t + D_t) / NAV_{t-1} - 1, où q_t est le nombre de parts courantes par part précédente et D_t la somme des distributions par part courante à la date ex-dividende.",
            "reinvestment": "L'indice suppose le réinvestissement conventionnel de D_t à la NAV_t. Il ne prétend pas rendre le cash disponible avant la date de paiement.",
            "fees": "Les frais internes déjà reflétés dans la NAV ne sont pas retranchés une seconde fois; aucun coût externe de transaction n'est inclus.",
            "first_observation": "Indice fixé à 100 à la première NAV; premier rendement à la deuxième date de NAV.",
        },
        "units": {
            "nav_and_distributions": "USD par part",
            "returns": "décimal",
            "growth_factor": "1 + rendement",
            "total_return_index_base_100": "indice, première NAV = 100",
        },
        "coverage": {ticker: {key: summaries[ticker][key] for key in ["start", "end", "rows", "returns"]} for ticker in summaries},
        "status": "AUDITED",
        "allowed_uses": ["Analyses financières hors exécution et hors coûts externes, sous la convention documentée, après acceptation des réserves"],
        "prohibited_or_unvalidated_uses": ["Prix exécutable", "Backtest net", "Simulation de portefeuille", "Rendement total officiellement validé par une seconde source"],
        "output_sha256": output_hashes,
    }
    metadata_path = output_dir / "reconstruction_metadata.json"
    write_json(metadata_path, metadata)
    return {
        "output_dir": str(output_dir),
        "files": {path.name: {"bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in [*csv_paths.values(), validation_path, metadata_path]},
        "validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true", help="Imprime le résumé complet en JSON")
    args = parser.parse_args()
    result = build(args.output_dir.resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Reconstruction terminée dans {result['output_dir']}")
        for name, details in result["files"].items():
            print(f"- {name}: {details['bytes']} octets, sha256={details['sha256']}")
        print("- assertions comptables et temporelles: OK")
        print(f"- statut: {result['validation']['series_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
