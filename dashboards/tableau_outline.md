# Tableau Dashboard Outline — Premier Inn Refund Intelligence

## Audience & decisions
Same stakeholder set as Power BI. Focus on fast anomaly detection and operational drill-down.

## Data source
Use `data/processed/refunds_processed.csv` for easy Tableau ingestion.

## Calculated fields
- Refund Count: COUNT([refund_amount])
- Total Refunds (£): SUM([refund_amount])
- Avg Refund (£): AVG([refund_amount])
- High Value Flag: IF [refund_amount] >= 100 THEN "High Value" ELSE "Standard" END
- Accommodation Flag (if category not precomputed):
  - IF CONTAINS(LOWER([BUSINESS_FORMAT_DATE]), "breakfast") OR CONTAINS(LOWER([BUSINESS_FORMAT_DATE]), "bar") OR ... THEN "F&B" ELSE "Accommodation" END

## Sheet list
1. KPI row (Total £, Count, Avg, Acc Share, High Value Share)
2. Site x Month clustered bar (refund £)
3. Monthly trend line by site
4. Category split stacked bar by site
5. Heatmap: WeekStart x DayName (refund £)
6. Top 10 dates table (refund £ + count)

## Dashboard layout
- Top: slicers (site, month, category, high value)
- Middle: trend + site/month
- Bottom: heatmap + top dates table

## Notes
- Use fixed month ordering (Nov, Dec, Jan)
- Add tooltip with date, site, count, total £
- Provide drill-through from anomaly date → receipt-level records (if fields available)
