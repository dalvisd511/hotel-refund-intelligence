from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd


@dataclass(frozen=True)
class ValidationReport:
    counts: Dict[str, int]
    amount_summary: Dict[str, float]
    null_rates: Dict[str, float]
    duplicates: Dict[str, int]


def row_count_reconciliation(raw_rows: int, refund_rows: int, analysis_rows: int) -> Dict[str, int]:
    return {
        "raw_rows": int(raw_rows),
        "refund_rows": int(refund_rows),
        "analysis_rows": int(analysis_rows),
    }


def amount_sanity_checks(df: pd.DataFrame, amount_col: str = "refund_amount") -> Dict[str, float]:
    if amount_col not in df.columns or df.empty:
        return {"min": float("nan"), "p50": float("nan"), "p90": float("nan"), "max": float("nan")}

    s = pd.to_numeric(df[amount_col], errors="coerce").dropna()
    if s.empty:
        return {"min": float("nan"), "p50": float("nan"), "p90": float("nan"), "max": float("nan")}

    return {
        "min": float(s.min()),
        "p50": float(s.quantile(0.50)),
        "p90": float(s.quantile(0.90)),
        "max": float(s.max()),
    }


def null_audit(df: pd.DataFrame, cols=("transaction_date", "refund_amount", "site")) -> Dict[str, float]:
    out = {}
    for c in cols:
        if c in df.columns:
            out[c] = float(df[c].isna().mean())
        else:
            out[c] = 1.0
    return out


def duplicate_check(
    df: pd.DataFrame,
    key_cols=("site", "transaction_date", "RECEIPT_NO", "refund_amount"),
) -> Dict[str, int]:
    missing = [c for c in key_cols if c not in df.columns]
    if missing:
        return {"duplicate_rows": 0, "note_missing_key_cols": len(missing)}

    dup_mask = df.duplicated(subset=list(key_cols), keep=False)
    dup_rows = int(dup_mask.sum())
    distinct_keys = int(df.loc[dup_mask, list(key_cols)].drop_duplicates().shape[0]) if dup_rows else 0
    return {"duplicate_rows": dup_rows, "distinct_duplicate_keys": distinct_keys}


def validate_dataset(
    raw_rows: int,
    refund_rows: int,
    df_analysis: pd.DataFrame,
) -> ValidationReport:
    counts = row_count_reconciliation(raw_rows, refund_rows, len(df_analysis))
    amount_summary = amount_sanity_checks(df_analysis, "refund_amount")
    null_rates = null_audit(df_analysis, ("transaction_date", "refund_amount", "site"))
    duplicates = duplicate_check(df_analysis, ("site", "transaction_date", "RECEIPT_NO", "refund_amount"))

    return ValidationReport(
        counts=counts,
        amount_summary=amount_summary,
        null_rates=null_rates,
        duplicates=duplicates,
    )
