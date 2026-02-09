from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pandas as pd


@dataclass(frozen=True)
class SQRIWeights:
    # You can tune these; keep simple and explainable
    accommodation_share_weight: float = 0.5
    accommodation_avg_weight: float = 0.3
    high_value_share_weight: float = 0.2


def kpis(df: pd.DataFrame) -> Dict[str, float]:
    if df.empty:
        return {"refund_count": 0, "total_refund_value": 0.0, "avg_refund_value": 0.0}
    s = pd.to_numeric(df["refund_amount"], errors="coerce").dropna()
    total = float(s.sum()) if not s.empty else 0.0
    count = int(s.shape[0])
    avg = float(s.mean()) if count else 0.0
    return {"refund_count": count, "total_refund_value": total, "avg_refund_value": avg}


def by_site_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Output: site, file_month, refund_count, total_refund_value, avg_refund_value
    """
    g = (
        df.groupby(["site", "file_month"], dropna=False)["refund_amount"]
        .agg(refund_count="count", total_refund_value="sum", avg_refund_value="mean")
        .reset_index()
    )
    return g


def category_split(df: pd.DataFrame) -> pd.DataFrame:
    """
    Output: site, refund_category, refund_count, total_refund_value, avg_refund_value
    """
    g = (
        df.groupby(["site", "refund_category"], dropna=False)["refund_amount"]
        .agg(refund_count="count", total_refund_value="sum", avg_refund_value="mean")
        .reset_index()
    )
    return g


def peak_days(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Output: site, transaction_date (date), daily_refund_value, daily_refund_count
    """
    if "transaction_date" not in df.columns:
        return pd.DataFrame(columns=["site", "transaction_date", "daily_refund_value", "daily_refund_count"])

    d = df.copy()
    d["date_only"] = pd.to_datetime(d["transaction_date"], errors="coerce").dt.date

    g = (
        d.groupby(["site", "date_only"])["refund_amount"]
        .agg(daily_refund_value="sum", daily_refund_count="count")
        .reset_index()
        .rename(columns={"date_only": "transaction_date"})
        .sort_values(["daily_refund_value"], ascending=False)
        .head(top_n)
    )
    return g


def sqri(
    df: pd.DataFrame,
    weights: Optional[SQRIWeights] = None,
    high_value_threshold: float = 100.0,
) -> pd.DataFrame:
    """
    Sleep Quality Risk Index (proxy).
    Components:
      - accommodation share (£) = accommodation_value / total_value
      - accommodation avg (£)
      - high value share = % refunds >= threshold
    Weighted sum (normalized accommodation avg by dividing by 100 for readability).
    Output per site.
    """
    weights = weights or SQRIWeights()

    if df.empty:
        return pd.DataFrame(columns=[
            "site",
            "total_value",
            "accommodation_value",
            "accommodation_share_value",
            "accommodation_avg",
            "high_value_share",
            "sqri_score",
        ])

    d = df.copy()
    d["refund_amount"] = pd.to_numeric(d["refund_amount"], errors="coerce")
    d = d.dropna(subset=["refund_amount", "site"])

    total_by_site = d.groupby("site")["refund_amount"].sum().rename("total_value")

    acc_mask = d["refund_category"].astype(str).str.lower().eq("accommodation")
    acc_by_site = d.loc[acc_mask].groupby("site")["refund_amount"].sum().rename("accommodation_value")
    acc_avg_by_site = d.loc[acc_mask].groupby("site")["refund_amount"].mean().rename("accommodation_avg")

    high_value_by_site = (
        (d["refund_amount"] >= float(high_value_threshold))
        .groupby(d["site"])
        .mean()
        .rename("high_value_share")
    )

    out = pd.concat([total_by_site, acc_by_site, acc_avg_by_site, high_value_by_site], axis=1).fillna(0.0).reset_index()

    out["accommodation_share_value"] = out.apply(
        lambda r: (r["accommodation_value"] / r["total_value"]) if r["total_value"] else 0.0, axis=1
    )

    # Normalize accommodation avg (divide by 100) so scale is comparable to shares.
    out["accommodation_avg_norm"] = out["accommodation_avg"] / 100.0

    out["sqri_score"] = (
        out["accommodation_share_value"] * weights.accommodation_share_weight
        + out["accommodation_avg_norm"] * weights.accommodation_avg_weight
        + out["high_value_share"] * weights.high_value_share_weight
    )

    return out.drop(columns=["accommodation_avg_norm"]).sort_values("sqri_score", ascending=False)
