# Power BI Dashboard Outline — Premier Inn Refund Intelligence

## Audience & decisions
Stakeholders: GM (Brighton/Newhaven), Ops Manager, Finance/Revenue Assurance, Guest Relations, Regional Manager  
Decisions supported:
- Where refunds concentrate (site/month/day)
- Whether refunds are accommodation-driven (guest experience proxy)
- Which days require investigation (anomaly detection)
- Whether risk is increasing (trend + SQRI)

## Data model (star schema proposal)
**FactRefunds** (from `data/processed/refunds_processed.*`)
- txn_date, txn_datetime
- site
- file_month
- refund_amount
- category (derived in model or precomputed)
- receipt_no (optional)

**DimDate**
- Date, Year, Month, WeekStart, DayName, IsWeekend

**DimSite**
- SiteName (Brighton/Newhaven)

## Page 1 — Executive Overview
**KPI Cards**
- Total Refunds (£)
- Refund Count
- Avg Refund (£)
- Accommodation Share (£)
- High-Value Share (% ≥ £100)
- SQRI

**Visuals**
- Clustered bar: Refund £ by Site by Month
- Line: Monthly trend by site
- Stacked bar: Accommodation vs F&B by site (value £)
- Table: Top 10 Refund Days (site-filtered)

**Slicers**
- Site
- Month
- Category
- High-value flag (≥£100)

## Page 2 — Operations Drill-down
**Visuals**
- Calendar/heatmap style: daily refunds (site filtered)
- Distribution: refund amount histogram (binning)
- Table: anomaly dates with totals/counts and drill-through

## Measures (DAX list)
- Total Refunds (£) = SUM(FactRefunds[refund_amount])
- Refund Count = COUNT(FactRefunds[refund_amount])
- Avg Refund (£) = DIVIDE([Total Refunds (£)], [Refund Count])
- Accommodation Refunds (£) = CALCULATE([Total Refunds (£)], FactRefunds[category] = "Accommodation")
- Accommodation Share (£) = DIVIDE([Accommodation Refunds (£)], [Total Refunds (£)])
- High Value Refund Count = CALCULATE([Refund Count], FactRefunds[refund_amount] >= 100)
- High Value Share = DIVIDE([High Value Refund Count], [Refund Count])

### SQRI (measure approach)
SQRI requires normalisation across sites (min-max). In Power BI:
- Option A: compute SQRI in Python (preferred for transparency) and store as a table
- Option B: DAX with site-level min/max using ALL(DimSite) and then weighted sum:
  - SQRI = 0.45*Norm(AccShare) + 0.35*Norm(AccAvg) + 0.20*Norm(HighValueShare)

## Refresh cadence & governance
- Weekly refresh (or daily if feed is automated)
- Add approval threshold workflow for refunds ≥ £100
- Weekly exception review pack for Ops + Finance
