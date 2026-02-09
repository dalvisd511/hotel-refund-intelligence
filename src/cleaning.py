from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


@dataclass(frozen=True)
class CleaningConfig:
    max_refund_amount: float = 1000.0  # outlier filter
    refund_keyword: str = "refund"      # case-insensitive match
    high_value_threshold: float = 100.0 # for later metrics if needed


def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop export padding columns like 'Unnamed: 0', 'Unnamed: 1', etc."""
    cols_to_drop = [c for c in df.columns if str(c).startswith("Unnamed:")]
    return df.drop(columns=cols_to_drop, errors="ignore")


def parse_site_and_month_from_filename(filename: str) -> Tuple[str, str]:
    """
    Expected pattern examples:
      Brighton_November_refund.csv
      Newheaven_January_refund.csv

    Returns:
      site: 'Brighton' / 'Newhaven' (normalized)
      file_month: 'Nov-2025' / 'Dec-2025' / 'Jan-2026' (based on your project months)
    """
    name = Path(filename).name
    parts = name.replace(".csv", "").split("_")
    if len(parts) < 2:
        raise ValueError(f"Unexpected filename format: {filename}")

    raw_site = parts[0].strip()
    raw_month = parts[1].strip().lower()

    # Normalize site spellings
    site_map = {
        "brighton": "Brighton",
        "newheaven": "Newhaven",
        "newhaven": "Newhaven",
    }
    site = site_map.get(raw_site.lower(), raw_site)

    # Your project: November + December = 2025, January = 2026
    month_map = {
        "november": "Nov-2025",
        "nov": "Nov-2025",
        "december": "Dec-2025",
        "dec": "Dec-2025",
        "january": "Jan-2026",
        "jan": "Jan-2026",
    }
    if raw_month not in month_map:
        raise ValueError(f"Unexpected month in filename: {filename}")

    return site, month_map[raw_month]


def add_file_metadata(df: pd.DataFrame, filename: str) -> pd.DataFrame:
    site, file_month = parse_site_and_month_from_filename(filename)
    out = df.copy()
    out["site"] = site
    out["file_month"] = file_month
    return out


def is_refund_row(df: pd.DataFrame, config: CleaningConfig) -> pd.Series:
    """
    Refund indicator: BUSINESS_FORMAT_DATE contains 'Refund' (case-insensitive).
    If BUSINESS_FORMAT_DATE missing, returns all False.
    """
    col = "BUSINESS_FORMAT_DATE"
    if col not in df.columns:
        return pd.Series([False] * len(df), index=df.index)
    return df[col].astype(str).str.contains(config.refund_keyword, case=False, na=False)


def build_transaction_date(df: pd.DataFrame) -> pd.Series:
    """
    Reliable transaction date:
      - parse BUSINESS_DATE first
      - if missing, fallback to BUSINESS_TIME
      - if still missing, fallback to BUSINESS_FORMAT_DATE
    Output: pandas datetime64[ns] (NaT if cannot parse)
    """
    # Helper: parse a series to datetime with coercion
    def _to_dt(s: pd.Series) -> pd.Series:
        return pd.to_datetime(s, errors="coerce", dayfirst=True)

    dt = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")

    if "BUSINESS_DATE" in df.columns:
        dt1 = _to_dt(df["BUSINESS_DATE"])
        dt = dt.fillna(dt1)

    if "BUSINESS_TIME" in df.columns:
        dt2 = _to_dt(df["BUSINESS_TIME"])
        dt = dt.fillna(dt2)

    if "BUSINESS_FORMAT_DATE" in df.columns:
        dt3 = _to_dt(df["BUSINESS_FORMAT_DATE"])
        dt = dt.fillna(dt3)

    return dt


def build_refund_amount(df: pd.DataFrame, config: CleaningConfig) -> pd.Series:
    """
    Refund amount:
      - start from ROOM
      - convert to numeric (coerce errors to NaN)
      - absolute value
      - outlier filter: remove > max_refund_amount => NaN
    """
    if "ROOM" not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index, dtype="Float64")

    amt = pd.to_numeric(df["ROOM"], errors="coerce")
    amt = amt.abs()

    amt = amt.where(amt <= config.max_refund_amount)  # outliers -> NaN
    return amt.astype("Float64")


def clean_single_file(path: Path, config: Optional[CleaningConfig] = None) -> pd.DataFrame:
    """
    Load and clean one CSV file into analysis-ready refund rows.
    """
    config = config or CleaningConfig()

    df = pd.read_csv(path, low_memory=False)
    df = drop_unnamed_columns(df)
    df = add_file_metadata(df, path.name)

    # Refund filter
    refund_mask = is_refund_row(df, config)
    df = df.loc[refund_mask].copy()

    # Create key fields
    df["transaction_date"] = build_transaction_date(df)
    df["refund_amount"] = build_refund_amount(df, config)

    # Keep only rows with usable refund_amount
    df = df[df["refund_amount"].notna()].copy()

    # Normalize category (Accommodation vs F&B) from BUSINESS_FORMAT_DATE
    if "BUSINESS_FORMAT_DATE" in df.columns:
        s = df["BUSINESS_FORMAT_DATE"].astype(str).str.lower()
        df["refund_category"] = pd.Series(pd.NA, index=df.index, dtype="string")
        df.loc[s.str.contains("accomm", na=False), "refund_category"] = "Accommodation"
        df.loc[s.str.contains("f&b", na=False) | s.str.contains("food", na=False) | s.str.contains("bar", na=False), "refund_category"] = "F&B"
        # Everything else
        df["refund_category"] = df["refund_category"].fillna("Other").astype("string")
    else:
        df["refund_category"] = "Other"

    return df


def clean_all_files(raw_dir: Path, config: Optional[CleaningConfig] = None) -> pd.DataFrame:
    """
    Clean all CSVs in data/raw and return a single consolidated dataframe.
    """
    config = config or CleaningConfig()

    paths = sorted(raw_dir.glob("*.csv"))
    if not paths:
        raise FileNotFoundError(f"No CSVs found in: {raw_dir}")

    frames = [clean_single_file(p, config=config) for p in paths]
    out = pd.concat(frames, ignore_index=True)

    return out


def export_processed(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
