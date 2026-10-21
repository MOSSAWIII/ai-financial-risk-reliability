#!/usr/bin/env python3
"""Audit hors ligne des prix de marché quotidiens Yahoo SPY/BIL.

Le script ne construit ni rendement de portefeuille ni simulation. Il vérifie
les champs OHLCV, les calendriers observés, le split BIL et les concordances
avec les références locales Nasdaq et State Street.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = (
    ROOT / "experiments" / "sequential-financial-decisions" / "data_manifest.json"
)
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "rl" / "yahoo_spy_bil_market_audit_v1.json"
AUDIT_DATE = "2026-10-19"
PRIORITY_START = pd.Timestamp("2016-10-17")
PRIORITY_END = pd.Timestamp("2026-10-16")
SPLIT_DATE = pd.Timestamp("2017-11-30")


def load_manifest() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return manifest, {item["id"]: item for item in manifest["datasets"]}


def source_path(index: dict[str, dict[str, Any]], dataset_id: str) -> Path:
    return ROOT / index[dataset_id]["local_file"]


def finite_or_none(value: Any) -> float | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return float(value)


def stats(values: pd.Series) -> dict[str, float | int | None]:
    clean = pd.to_numeric(values, errors="coerce").dropna().astype(float)
    if clean.empty:
        return {"n": 0, "mean": None, "median": None, "max_abs": None, "rmse": None}
    return {
        "n": int(len(clean)),
        "mean": finite_or_none(clean.mean()),
        "median": finite_or_none(clean.median()),
        "max_abs": finite_or_none(clean.abs().max()),
        "rmse": finite_or_none(float(np.sqrt(np.mean(np.square(clean))))),
    }


def longest_equal_run(values: pd.Series) -> int:
    if values.empty:
        return 0
    groups = values.ne(values.shift()).cumsum()
    return int(values.groupby(groups).size().max())


def parse_yahoo(path: Path) -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    result = json.loads(path.read_text(encoding="utf-8"))["chart"]["result"][0]
    meta = result["meta"]
    timezone_name = meta.get("exchangeTimezoneName", "America/New_York")
    timezone = ZoneInfo(timezone_name)
    timestamps = pd.to_datetime(result["timestamp"], unit="s", utc=True)
    local = timestamps.tz_convert(timezone)
    frame = pd.DataFrame(result["indicators"]["quote"][0])
    frame["adjclose"] = result["indicators"]["adjclose"][0]["adjclose"]
    frame["timestamp_utc"] = timestamps
    frame["timestamp_local"] = local
    frame["date"] = pd.to_datetime(local.date)
    frame = frame.sort_values("date").reset_index(drop=True)

    events = result.get("events") or {}
    dividends = []
    for event in (events.get("dividends") or {}).values():
        event_local = pd.Timestamp(event["date"], unit="s", tz="UTC").tz_convert(timezone)
        dividends.append({"date": event_local.date().isoformat(), "amount": float(event["amount"])})
    splits = []
    for event in (events.get("splits") or {}).values():
        event_local = pd.Timestamp(event["date"], unit="s", tz="UTC").tz_convert(timezone)
        splits.append(
            {
                "date": event_local.date().isoformat(),
                "numerator": float(event["numerator"]),
                "denominator": float(event["denominator"]),
                "split_ratio": event["splitRatio"],
            }
        )
    return frame, meta, sorted(dividends, key=lambda row: row["date"]), sorted(splits, key=lambda row: row["date"])


def yahoo_summary(frame: pd.DataFrame, meta: dict[str, Any], dividends: list[dict[str, Any]], splits: list[dict[str, Any]]) -> dict[str, Any]:
    numeric = frame[["open", "high", "low", "close", "adjclose", "volume"]].apply(pd.to_numeric, errors="coerce")
    valid = (
        numeric[["open", "close"]].min(axis=1).ge(numeric["low"])
        & numeric[["open", "close"]].max(axis=1).le(numeric["high"])
        & numeric["low"].le(numeric["high"])
    )
    close_change = numeric["close"].pct_change()
    extremes = (
        pd.DataFrame({"date": frame["date"], "change": close_change})
        .dropna()
        .assign(abs_change=lambda item: item["change"].abs())
        .nlargest(10, "abs_change")
    )
    local_times = frame["timestamp_local"].dt.strftime("%H:%M:%S%z").value_counts().sort_index()
    return {
        "symbol": meta.get("symbol"),
        "currency": meta.get("currency"),
        "exchange_name": meta.get("exchangeName"),
        "full_exchange_name": meta.get("fullExchangeName"),
        "exchange_timezone_name": meta.get("exchangeTimezoneName"),
        "instrument_type": meta.get("instrumentType"),
        "data_granularity": meta.get("dataGranularity"),
        "columns": ["date", "open", "high", "low", "close", "adjclose", "volume"],
        "rows": int(len(frame)),
        "start": frame["date"].min().date().isoformat(),
        "end": frame["date"].max().date().isoformat(),
        "ascending_dates": bool(frame["date"].is_monotonic_increasing),
        "duplicate_dates": int(frame["date"].duplicated().sum()),
        "weekend_dates": int((frame["date"].dt.dayofweek >= 5).sum()),
        "missing_by_field": {column: int(numeric[column].isna().sum()) for column in numeric},
        "nonpositive_price_values": int((numeric[["open", "high", "low", "close"]] <= 0).sum().sum()),
        "negative_volume_rows": int((numeric["volume"] < 0).sum()),
        "zero_volume_rows": int((numeric["volume"] == 0).sum()),
        "invalid_ohlc_rows": int((~valid).sum()),
        "zero_intraday_range_rows": int(numeric["high"].eq(numeric["low"]).sum()),
        "longest_constant_close_run": longest_equal_run(numeric["close"]),
        "longest_constant_volume_run": longest_equal_run(numeric["volume"]),
        "timestamp_local_time_counts": {str(key): int(value) for key, value in local_times.items()},
        "largest_absolute_close_changes": [
            {"date": row.date.date().isoformat(), "change": float(row.change)}
            for row in extremes.itertuples()
        ],
        "dividend_event_count": len(dividends),
        "split_events": splits,
    }


def parse_nasdaq(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["data"]["tradesTable"]["rows"])
    frame["date"] = pd.to_datetime(frame["date"], format="%m/%d/%Y")
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(
            frame[column].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False),
            errors="coerce",
        )
    return frame.sort_values("date").reset_index(drop=True)


def parse_ssga_sheet(path: Path) -> pd.DataFrame:
    frame = pd.read_excel(path, header=3).dropna(how="all")
    frame["date"] = pd.to_datetime(frame["Date"], errors="coerce")
    return frame.loc[frame["date"].notna()].copy()


def parse_ssga_nav(path: Path) -> pd.DataFrame:
    frame = parse_ssga_sheet(path)
    frame["nav"] = pd.to_numeric(
        frame["NAV"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False),
        errors="coerce",
    )
    return frame[["date", "nav"]]


def parse_ssga_premium(path: Path) -> pd.DataFrame:
    frame = parse_ssga_sheet(path)
    frame["premium_discount_pct"] = pd.to_numeric(frame["Premium/Discount"], errors="coerce")
    return frame[["date", "premium_discount_pct"]]


def compare_frames(left: pd.DataFrame, right: pd.DataFrame, fields: list[str]) -> dict[str, Any]:
    merged = left[["date", *fields]].merge(right[["date", *fields]], on="date", suffixes=("_left", "_right"))
    comparisons = {}
    for field in fields:
        difference = merged[f"{field}_left"] - merged[f"{field}_right"]
        paired = merged[[f"{field}_left", f"{field}_right"]].dropna()
        largest = difference.abs().nlargest(5).index
        comparisons[field] = {
            "difference": stats(difference),
            "correlation": finite_or_none(paired.corr().iloc[0, 1]) if len(paired) > 1 else None,
            "exact_equal": int(merged[f"{field}_left"].eq(merged[f"{field}_right"]).sum()),
            "largest_absolute_differences": [
                {
                    "date": merged.loc[index_value, "date"].date().isoformat(),
                    "left": finite_or_none(merged.loc[index_value, f"{field}_left"]),
                    "right": finite_or_none(merged.loc[index_value, f"{field}_right"]),
                    "difference": finite_or_none(difference.loc[index_value]),
                }
                for index_value in largest
            ],
        }
    alert_masks: dict[str, pd.Series] = {}
    for field in [item for item in fields if item in {"open", "high", "low", "close"}]:
        alert_masks[field] = (merged[f"{field}_left"] / merged[f"{field}_right"] - 1).abs() > 0.001
    if "volume" in fields:
        alert_masks["volume"] = (
            (merged["volume_left"] / merged["volume_right"] - 1).abs() > 0.05
        ) | merged[["volume_left", "volume_right"]].isna().any(axis=1)
    any_alert = pd.DataFrame(alert_masks).any(axis=1) if alert_masks else pd.Series(False, index=merged.index)
    return {
        "common_dates": int(len(merged)),
        "start": merged["date"].min().date().isoformat(),
        "end": merged["date"].max().date().isoformat(),
        "fields": comparisons,
        "diagnostic_alerts": {
            "rule": "écart relatif absolu > 10 points de base pour un OHLC, ou > 5 % / valeur manquante pour le volume; drapeaux descriptifs sans exclusion automatique",
            "field_counts": {field: int(mask.sum()) for field, mask in alert_masks.items()},
            "unique_date_count": int(any_alert.sum()),
            "dates": merged.loc[any_alert, "date"].dt.date.astype(str).tolist(),
        },
    }


def nav_comparison(price: pd.DataFrame, nav: pd.DataFrame, divisor: float = 1.0) -> dict[str, Any]:
    merged = price[["date", "close"]].merge(nav, on="date").dropna()
    gap_bps = ((merged["close"] / divisor) / merged["nav"] - 1) * 10_000
    return {
        "common_dates": int(len(merged)),
        "start": merged["date"].min().date().isoformat(),
        "end": merged["date"].max().date().isoformat(),
        "close_over_nav_minus_one_bps": stats(gap_bps),
    }


def premium_comparison(price: pd.DataFrame, nav: pd.DataFrame, premium: pd.DataFrame) -> dict[str, Any]:
    merged = price[["date", "close"]].merge(nav, on="date").merge(premium, on="date").dropna()
    merged["close_nav_pct"] = (merged["close"] / merged["nav"] - 1) * 100
    difference = merged["close_nav_pct"] - merged["premium_discount_pct"]
    return {
        "common_dates": int(len(merged)),
        "start": merged["date"].min().date().isoformat(),
        "end": merged["date"].max().date().isoformat(),
        "yahoo_close_over_nav_minus_official_premium_pct_points": stats(difference),
        "interpretation": "La prime officielle emploie le midpoint bid/ask et l'INAV à 16 h; elle n'est pas tenue d'égaler clôture Yahoo / NAV.",
    }


def distribution_comparison(
    ticker: str,
    yahoo_events: list[dict[str, Any]],
    distributions_path: Path,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> dict[str, Any]:
    source = pd.read_excel(distributions_path, sheet_name="dividend")
    source = source[source["TICKER"].eq(ticker)].copy()
    source["date"] = pd.to_datetime(source["EX-DATE"])
    for column in ["DIVIDEND ($)", "SHORT TERM CAPITAL GAIN ($)", "LONG TERM CAPITAL GAIN ($)"]:
        source[column] = pd.to_numeric(source[column], errors="coerce").fillna(0.0)
    source["amount"] = source[["DIVIDEND ($)", "SHORT TERM CAPITAL GAIN ($)", "LONG TERM CAPITAL GAIN ($)"]].sum(axis=1)
    source = source[source["date"].between(start, end) & source["amount"].ne(0)]
    yahoo = pd.DataFrame(yahoo_events)
    yahoo["date"] = pd.to_datetime(yahoo["date"])
    merged = yahoo.merge(source[["date", "amount"]], on="date", how="outer", suffixes=("_yahoo", "_ssga"), indicator=True)
    common = merged[merged["_merge"].eq("both")].copy()
    differences = common["amount_yahoo"] - common["amount_ssga"]
    output = {
        "yahoo_positive_events": int(len(yahoo)),
        "state_street_positive_events_in_window": int(len(source)),
        "common_dates": int(len(common)),
        "only_yahoo_events": [
            {"date": row.date.date().isoformat(), "amount": float(row.amount_yahoo)}
            for row in merged[merged["_merge"].eq("left_only")].sort_values("date").itertuples()
        ],
        "only_state_street_events": [
            {"date": row.date.date().isoformat(), "amount": float(row.amount_ssga)}
            for row in merged[merged["_merge"].eq("right_only")].sort_values("date").itertuples()
        ],
        "amount_difference_usd_on_common_dates": stats(differences),
    }
    if ticker == "BIL":
        for name, mask in {
            "pre_split": common["date"] < SPLIT_DATE,
            "post_split": common["date"] >= SPLIT_DATE,
        }.items():
            period = common.loc[mask]
            output[name] = {
                "events": int(len(period)),
                "amount_difference_usd": stats(period["amount_yahoo"] - period["amount_ssga"]),
                "yahoo_over_state_street_amount_ratio": stats(period["amount_yahoo"] / period["amount_ssga"]),
            }
    return output


def audit() -> dict[str, Any]:
    manifest, index = load_manifest()
    yahoo_spy, meta_spy, div_spy, split_spy = parse_yahoo(source_path(index, "yahoo_spy_chart_ohlcv_20261019"))
    yahoo_bil, meta_bil, div_bil, split_bil = parse_yahoo(source_path(index, "yahoo_bil_chart_ohlcv_20261019"))
    nasdaq_spy = parse_nasdaq(source_path(index, "nasdaq_spy_ohlcv_20261019"))
    nasdaq_ivv = parse_nasdaq(source_path(index, "nasdaq_ivv_ohlcv_20261019"))
    nasdaq_vti = parse_nasdaq(source_path(index, "nasdaq_vti_ohlcv_20261019"))

    spy_nav = parse_ssga_nav(source_path(index, "ssga_spy_nav_20261019"))
    bil_nav = parse_ssga_nav(source_path(index, "ssga_bil_nav_20261019"))
    spy_premium = parse_ssga_premium(source_path(index, "ssga_spy_premium_discount_20261019"))
    bil_premium = parse_ssga_premium(source_path(index, "ssga_bil_premium_discount_20261019"))
    distributions_path = source_path(index, "ssga_spdr_distributions_20261019")

    priority_spy = yahoo_spy[yahoo_spy["date"].between(PRIORITY_START, PRIORITY_END)].copy()
    priority_bil = yahoo_bil[yahoo_bil["date"].between(PRIORITY_START, PRIORITY_END)].copy()
    y_spy_dates = set(priority_spy["date"])
    y_bil_dates = set(priority_bil["date"])
    n_sets = [set(frame["date"]) for frame in [nasdaq_spy, nasdaq_ivv, nasdaq_vti]]
    nasdaq_reference = set.intersection(*n_sets)
    all_weekdays = set(pd.date_range(PRIORITY_START, PRIORITY_END, freq="B"))
    observed_union = y_spy_dates | y_bil_dates | set.union(*n_sets)

    common_all = sorted(set(yahoo_spy["date"]) & set(yahoo_bil["date"]))
    common_priority = sorted(y_spy_dates & y_bil_dates)
    calendar = {
        "method": "Calendrier empirique; les séances de référence sont les dates communes aux trois fichiers Nasdaq SPY/IVV/VTI. Les fermetures candidates sont les jours de semaine absents de toutes les séries. Ce procédé ne détecte pas les séances écourtées.",
        "full_yahoo_common": {
            "rows": len(common_all),
            "start": common_all[0].date().isoformat(),
            "end": common_all[-1].date().isoformat(),
            "spy_only_dates": sorted(day.date().isoformat() for day in set(yahoo_spy["date"]) - set(yahoo_bil["date"])),
            "bil_only_dates": sorted(day.date().isoformat() for day in set(yahoo_bil["date"]) - set(yahoo_spy["date"])),
        },
        "priority_window": {
            "start": PRIORITY_START.date().isoformat(),
            "end": PRIORITY_END.date().isoformat(),
            "yahoo_spy_rows": len(priority_spy),
            "yahoo_bil_rows": len(priority_bil),
            "yahoo_common_rows": len(common_priority),
            "yahoo_spy_only_dates": sorted(day.date().isoformat() for day in y_spy_dates - y_bil_dates),
            "yahoo_bil_only_dates": sorted(day.date().isoformat() for day in y_bil_dates - y_spy_dates),
            "nasdaq_three_instrument_reference_rows": len(nasdaq_reference),
            "yahoo_both_missing_on_nasdaq_reference": sorted(day.date().isoformat() for day in nasdaq_reference - (y_spy_dates & y_bil_dates)),
            "yahoo_common_not_in_nasdaq_reference": sorted(day.date().isoformat() for day in (y_spy_dates & y_bil_dates) - nasdaq_reference),
            "weekday_market_closed_candidates": sorted(day.date().isoformat() for day in all_weekdays - observed_union),
            "early_closes": "non identifiables à partir d'un OHLCV quotidien; calendrier officiel historique dédié non acquis",
        },
    }

    spy_nasdaq = compare_frames(priority_spy, nasdaq_spy, ["open", "high", "low", "close", "volume"])
    spy_nasdaq["interpretation"] = "Contrôle indépendant partiel de fournisseur; les deux sources peuvent réutiliser des flux de marché communs."

    pre_split_bil = yahoo_bil[yahoo_bil["date"] < SPLIT_DATE]
    post_split_bil = yahoo_bil[yahoo_bil["date"] >= SPLIT_DATE]
    split_window = yahoo_bil[yahoo_bil["date"].between("2017-11-27", "2017-12-04")][
        ["date", "open", "high", "low", "close", "volume"]
    ].merge(bil_nav, on="date", how="left")
    split_control = {
        "provider_events": split_bil,
        "expected_official_event": {"date": "2017-11-30", "old_shares_per_new_share": 2, "current_per_previous": 0.5},
        "event_match": split_bil == [{"date": "2017-11-30", "numerator": 1.0, "denominator": 2.0, "split_ratio": "1:2"}],
        "window": [
            {
                "date": row.date.date().isoformat(),
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "volume": int(row.volume),
                "state_street_nav": finite_or_none(row.nav),
            }
            for row in split_window.itertuples()
        ],
        "pre_split_yahoo_close_vs_raw_nav": nav_comparison(pre_split_bil, bil_nav),
        "pre_split_yahoo_close_divided_by_two_vs_raw_nav": nav_comparison(pre_split_bil, bil_nav, divisor=2.0),
        "post_split_yahoo_close_vs_raw_nav": nav_comparison(post_split_bil, bil_nav),
        "conclusion": "L'OHLC Yahoo antérieur au split est rétrospectivement multiplié par deux: il est continu autour de 91 USD alors que la NAV brute passe d'environ 45,7 à 91,5 USD. Ne pas appliquer une seconde correction à la série Yahoo; diviser par deux serait nécessaire pour retrouver une échelle historique par ancienne part, mais cette dérivation n'est pas publiée comme série exécutable. Le traitement historique du volume n'est pas documenté.",
    }

    source_hashes = {
        dataset_id: {"sha256": index[dataset_id]["sha256"], "bytes": index[dataset_id]["bytes"]}
        for dataset_id in [
            "yahoo_spy_chart_ohlcv_20261019",
            "yahoo_bil_chart_ohlcv_20261019",
            "nasdaq_spy_ohlcv_20261019",
            "nasdaq_ivv_ohlcv_20261019",
            "nasdaq_vti_ohlcv_20261019",
            "ssga_spy_nav_20261019",
            "ssga_bil_nav_20261019",
            "ssga_spy_premium_discount_20261019",
            "ssga_bil_premium_discount_20261019",
            "ssga_spdr_distributions_20261019",
        ]
    }

    required_assertions = {
        "both_yahoo_files_present": True,
        "no_missing_yahoo_ohlcv": not yahoo_spy[["open", "high", "low", "close", "volume"]].isna().any().any()
        and not yahoo_bil[["open", "high", "low", "close", "volume"]].isna().any().any(),
        "no_invalid_yahoo_ohlc": yahoo_summary(yahoo_spy, meta_spy, div_spy, split_spy)["invalid_ohlc_rows"] == 0
        and yahoo_summary(yahoo_bil, meta_bil, div_bil, split_bil)["invalid_ohlc_rows"] == 0,
        "priority_calendars_identical": y_spy_dates == y_bil_dates == nasdaq_reference,
        "bil_split_event_matches_official": split_control["event_match"],
        "common_priority_rows_positive": len(common_priority) > 0,
    }

    return {
        "audit_version": "1.0.0",
        "audit_date": AUDIT_DATE,
        "scope": "Qualité, provenance et adéquation des OHLCV quotidiens SPY/BIL; aucun portefeuille, backtest ou rendement de stratégie.",
        "source_hashes": source_hashes,
        "provider_documentation": {
            "yahoo_history_page": "Close est annoncé ajusté des splits; Adj Close est annoncé ajusté des splits et distributions.",
            "unresolved": [
                "définition exacte de l'ouverture (enchère, première transaction ou construction fournisseur)",
                "origine consolidée ou place précise des OHLC",
                "inclusion ou exclusion exacte des transactions hors séance",
                "traitement historique du volume lors des splits",
                "stabilité binaire d'Adj Close, dont de petites valeurs ont varié entre deux réponses",
            ],
        },
        "structural_audit": {
            "SPY": yahoo_summary(yahoo_spy, meta_spy, div_spy, split_spy),
            "BIL": yahoo_summary(yahoo_bil, meta_bil, div_bil, split_bil),
        },
        "calendar_audit": calendar,
        "split_bil_audit": split_control,
        "cross_checks": {
            "spy_yahoo_vs_nasdaq_priority_window": spy_nasdaq,
            "spy_yahoo_close_vs_state_street_nav": nav_comparison(yahoo_spy, spy_nav),
            "bil_yahoo_close_vs_state_street_nav_post_split": nav_comparison(post_split_bil, bil_nav),
            "spy_premium_discount": premium_comparison(yahoo_spy, spy_nav, spy_premium),
            "bil_premium_discount": premium_comparison(yahoo_bil, bil_nav, bil_premium),
            "spy_distributions": distribution_comparison("SPY", div_spy, distributions_path, yahoo_spy["date"].min(), yahoo_spy["date"].max()),
            "bil_distributions": distribution_comparison("BIL", div_bil, distributions_path, yahoo_bil["date"].min(), yahoo_bil["date"].max()),
        },
        "coverage_decision": {
            "raw_common": {"start": common_all[0].date().isoformat(), "end": common_all[-1].date().isoformat(), "rows": len(common_all)},
            "quality_audited_split_adjusted": {"start": common_all[0].date().isoformat(), "end": common_all[-1].date().isoformat(), "rows": len(common_all)},
            "priority_common": {"start": common_priority[0].date().isoformat(), "end": common_priority[-1].date().isoformat(), "rows": len(common_priority)},
            "post_bil_split_historical_price_scale": {
                "start": SPLIT_DATE.date().isoformat(),
                "end": yahoo_bil["date"].max().date().isoformat(),
                "rows": int(len(post_split_bil)),
            },
            "market_price_reference_status": "AUDITED",
            "opening_execution_reference": "CONDITIONALLY_USABLE_ONLY_AS_A_FUTURE_MODELING_REFERENCE",
            "execution_guarantee": False,
        },
        "scientific_status": "AUDITED",
        "allowed_use": "Analyse descriptive locale des OHLCV quotidiens SPY/BIL sous conventions Yahoo et contrôles documentés.",
        "not_validated_for": [
            "définition officielle de l'enchère d'ouverture",
            "prix brut BIL antérieur au split sans dérivation",
            "exécution garantie ou disponible pour une quantité donnée",
            "bid, ask, spread, profondeur, slippage ou impact",
            "backtest ou performance nette négociable",
            "redistribution publique des fichiers bruts",
        ],
        "required_assertions": required_assertions,
        "all_required_assertions_passed": all(required_assertions.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()
    result = audit()
    encoded = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    if args.stdout:
        print(encoded.decode("utf-8"), end="")
    else:
        print(
            json.dumps(
                {
                    "output": str(args.output.relative_to(ROOT)).replace("\\", "/"),
                    "bytes": len(encoded),
                    "scientific_status": result["scientific_status"],
                    "all_required_assertions_passed": result["all_required_assertions_passed"],
                    "coverage": result["coverage_decision"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0 if result["all_required_assertions_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
